import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import patchworklib as pw


def plot_joint_threshold_split(df, labels, x_col, y_col, row_col,label_dict, threshold_row, cat, sample_size = 200000, col_col=None, threshold_col=None, quantile=0.9, save=True):
    """ 
    Create a grid of joint plots split by thresholds on a specified row variable and optionally by column variable.
    Parameters
    ----------
    dfs : list of pd.DataFrame
        List of datasets to plot (e.g., [GC_q, df_YSC, NSC_q])
    labels : list of str
        Corresponding labels for the datasets (e.g., ['GC', 'YSC', 'NSC'])
    x_col : str
        Column name for x-axis variable (e.g., 'c1:M1')
    y_col : str
        Column name for y-axis variable (e.g., 'c2:M2')
    row_col : str
        Column name for row-wise threshold splitting (e.g., 'c27:Ngen')
    label_dict : dict
        Mapping of column names to human-readable labels for titles and axes (e.g., {'c1:M1': 'M1', 'c2:M2': 'M2', 'c27:Ngen': 'Ngen'})
    threshold_row : float
        Threshold value for splitting the row variable (e.g., 2)
    col_col : str, optional
        Column name for column-wise threshold splitting (e.g., 'met')
    threshold_col : list of float, optional
        List of threshold values for splitting the column variable (e.g., [0.0002   , 0.0012, 0.008, 0.3])
    quantile : float, optional
        Quantile for determining axis limits to handle outliers (default is 0.9 for 90th percentile)
    save : bool, optional
        Whether to save the resulting plot as a PDF (default is True)
    Returns
    -------
    If save is False, returns the patchworklib grid object for display in notebooks.
    """
    # 1. Global limits (90th percentile) for consistent scale
    clean_cols = [x_col, y_col, row_col]
    if col_col is not None: 
        clean_cols.append(col_col)
    dfs = [df[df[cat] == la ] for la in df[cat].unique()]
    dfs_scat = [d.dropna(subset=clean_cols).copy() for d in dfs]

    # 2. Global limits for consistent scale
    all_x = pd.concat([d[x_col] for d in dfs])
    all_y = pd.concat([d[y_col] for d in dfs])
    
    x_lim = all_x.quantile(quantile)
    y_lim = all_y.quantile(quantile)
    x_min, y_min = all_x.min(), all_y.min()

    os.makedirs(f"images/{row_col}/threshold_split/{x_col}", exist_ok=True)
    colors = ["#3498db", "#e74c3c", "#2ecc71"]
    markers = ['o', 's', '^']
    
    # Define conditions with "Frozen" variables (i=i, t=threshold_row)
    conditions_row = [
        (lambda x, t=threshold_row: x <= t, rf"{label_dict[row_col]} $\leq$ {threshold_row}"),
        (lambda x, t=threshold_row: x > t, rf"{label_dict[row_col]} $>$ {threshold_row}")
    ]
    
    if col_col is not None and threshold_col is not None:
        conditions_col = [
            (lambda x, i=i: (x >= threshold_col[i]) & (x < threshold_col[i+1]), 
             rf"{threshold_col[i]} $\leq$ {label_dict[col_col]} < {threshold_col[i+1]}") 
            for i in range(len(threshold_col)-1)
        ]
    else:
        conditions_col = [(None, "")]

    g_list_row = [] 
    
    for check_row, cond_name_row in conditions_row:
        g_list_cols = []
        for check_col, cond_name_col in conditions_col:
            g = sns.JointGrid(height=15)
            
            for i, dfi in enumerate(dfs):
                # Apply row filter
                dfi = dfi[[x_col, y_col, row_col] + ([col_col] if col_col is not None else [])]
                
                

                subset_row = dfi[check_row(dfi[row_col])]
                
                # Apply column filter
                if check_col is not None:
                    subset = subset_row[check_col(subset_row[col_col])]
                else:
                    subset = subset_row 
                subset = subset.sample(frac=sample_size/subset.shape[0], random_state=42) if subset.shape[0] > sample_size else subset
                df_cut = subset.select_dtypes(include="number").quantile(quantile)
                subset = subset.where(subset.le(df_cut))
                subset.dropna(inplace=True)
                #print(subset.head())
                if subset.empty:
                    print(f"Warning: No data for {labels[i]} in condition '{cond_name_row}' and '{cond_name_col}'")
                    continue
                
                # Plotting
                sns.scatterplot(data=subset, x=x_col, y=y_col, ax=g.ax_joint,
                                color=colors[i], marker=markers[i], alpha=0.4, s=15, label=labels[i])
                sns.kdeplot(data=subset, x=x_col, y=y_col, ax=g.ax_joint,
                            color=colors[i], levels=[0.1,0.25,0.5,0.75,0.9], alpha=0.8)
                sns.histplot(data=subset, x=x_col, ax=g.ax_marg_x, color=colors[i],
                            element="step", fill=False, linewidth=2, binrange=(x_min, x_lim))
                sns.histplot(data=subset, y=y_col, ax=g.ax_marg_y, color=colors[i],
                            element="step", fill=False, linewidth=2, binrange=(y_min, y_lim))

            # FORCE CONSISTENT LIMITS (Crucial for comparison)
            xmin, xmax = g.ax_joint.get_xlim()
            ymin, ymax = g.ax_joint.get_ylim()
            g.ax_joint.set_xlim(xmin, xmax)
            g.ax_joint.set_ylim(ymin, ymax)
            g.ax_joint.set_xlabel(label_dict[x_col])
            g.ax_joint.set_ylabel(label_dict[y_col])
            g.ax_joint.legend(title="Origin Cluster", loc='upper right')

            # Brick processing
            curr_brick = pw.load_seaborngrid(g)
            title = f" {cond_name_row}"
            if cond_name_col: title += f" | {cond_name_col}"
            
            curr_brick.case.set_title(title, pad=20, fontsize=14)
            g_list_cols.append(curr_brick)
            plt.close(g.fig)
        
        # Stack columns horizontally
        g_list_row.append(pw.stack(g_list_cols, operator="|"))

    # Stack rows vertically
    full_grid = pw.stack(g_list_row, operator="/")
    
    if save:
        path = f"images/{row_col}/threshold_split/{x_col}/joint_threshold_{x_col}_{y_col}.pdf"
        full_grid.savefig(fname=path, quick=True)
        print(f"Saved to {path}")
    else:
        return full_grid
        
    

