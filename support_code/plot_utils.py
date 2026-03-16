import os
import pandas as pd  # pandas for DataFrame manipulation
import seaborn as sns  # seaborn for statistical plotting
import matplotlib.pyplot as plt  # matplotlib for figure handling
import patchworklib as pw  # patchworklib to arrange multiple plots
import fitz  # PyMuPDF
import ipywidgets as widgets


def plot_joint_threshold_split(df, labels, x_col, y_col, row_col, label_dict, threshold_row=None, cat='sys', sample_size=200000, col_col=None, threshold_col=None, quantile=0.9, save=True):
    """Create a grid of joint plots split by a row threshold and optional column bins.

    This helper creates JointGrid scatter+KDE plots for multiple sub-datasets defined
    by a categorical column (`cat`). It splits each dataset into two row-based groups
    (<= threshold_row and > threshold_row) and optionally into column-based bins
    defined by `threshold_col`. The resulting bricks are arranged with patchworklib
    and optionally saved to PDF.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing the data.
    labels : list[str]
        List of labels for each unique value in `df[cat]` (used in legends).
    x_col, y_col : str
        Column names to plot on the x and y axes.
    row_col : str
        Column name used to split rows by `threshold_row`.
    label_dict : dict
        Mapping from column names to LaTeX or human-readable labels for axis titles.
    threshold_row : float
        Value to split the `row_col` into two groups.
    cat : str
        Column name containing the category used to create separate datasets.
    sample_size : int
        Maximum number of points per subset to plot (subsampling applied if larger).
    col_col : str or None
        Optional column to create additional column-based bins.
    threshold_col : list or None
        If col_col is provided, list of thresholds defining bins for col_col.
    quantile : float
        Quantile used to clip axis values to reduce outlier effects.
    save : bool
        If True, the resulting patchwork grid is saved as a PDF; otherwise returned.

    Returns
    -------
    None or patchworklib.Patchwork
        Saves the figure when save=True; otherwise returns the patchwork object.
    """
    # 1. Columns we need to keep clean (non-null) for plotting
    needed_cols = [x_col, y_col, cat]
    if row_col: needed_cols.append(row_col)
    if col_col: needed_cols.append(col_col)
    
    # Clean NaNs only from necessary columns
    df_clean = df.dropna(subset=needed_cols).copy()
    
    # Use GroupBy instead of list comprehension for speed
    # This maps 'GC', 'YSC', 'NSC' to their data chunks efficiently
    
    
    # Ensure we follow the order of the 'labels' list provided
    # unique_cats corresponds to the actual keys in the group dict
    dfs = [df_clean[df_clean[cat] == la].reset_index(drop=True) for la in df_clean[cat].unique()]
    # 3. Compute global axis limits (quantile) across all datasets for consistent comparison
    all_x = pd.concat([d[x_col] for d in dfs])
    all_y = pd.concat([d[y_col] for d in dfs])

    x_lim = all_x.quantile(quantile)  # upper quantile for x-axis
    y_lim = all_y.quantile(quantile)  # upper quantile for y-axis
    x_min, y_min = all_x.min(), all_y.min()  # global minima for bin ranges

    os.makedirs(f"images/{row_col}/threshold_split/{x_col}", exist_ok=True)  # ensure output directory exists
    colors = ["#3498db", "#e74c3c", "#2ecc71"]  # palette for the three categories
    markers = ['o', 's', '^']  # marker styles for scatter points

    # Define row-based conditions and their title fragments using label dict for readable output
    if threshold_row is not None:
        conditions_row = [
            (lambda d, r=row_col, t=threshold_row: d[r] <= t, rf"{label_dict[row_col]} $\leq$ {threshold_row}"),
            (lambda d, r=row_col, t=threshold_row: d[r] > t, rf"{label_dict[row_col]} $>$ {threshold_row}")
        ]
    else:
        # Returns a boolean mask of all True, matching the index of input 'd'
        conditions_row = [(lambda d: pd.Series(True, index=d.index), "All Data")]

    # 4. Corrected Column Conditions Logic
    if col_col is not None and threshold_col is not None:
        conditions_col = [
            (lambda d, r=col_col, i=i: (d[r] >= threshold_col[i]) & (d[r] < threshold_col[i+1]), 
             rf"{threshold_col[i]} $\leq$ {label_dict[col_col]} < {threshold_col[i+1]}") 
            for i in range(len(threshold_col)-1)
        ]
    else:
        conditions_col = [(lambda d: pd.Series(True, index=d.index), "")]
    g_list_row = []  # accumulate row bricks here

    for r_idx, (check_row, cond_name_row) in enumerate(conditions_row):
        g_list_cols = []  # accumulate column bricks for this row condition
        for c_idx, (check_col, cond_name_col) in enumerate(conditions_col):
            plt.clf()
            g = sns.JointGrid(height=15)  # create a new JointGrid for this brick

            for i, dfi in enumerate(dfs):
                # select only relevant columns to reduce memory and avoid accidental modifications
                dfa = dfi[needed_cols].dropna().copy()

                # apply the row condition to filter rows
                subset_row = dfa[check_row(dfa)].fillna(False).copy().reset_index(drop=True)

                # apply the column condition if present
                if check_col is not None:
                    subset = subset_row[check_col(subset_row)].fillna(False).copy().reset_index(drop=True)
                else:
                    subset = subset_row.fillna(False).copy().reset_index(drop=True)

                # subsample if the subset is larger than sample_size to limit plotting time
                subset = subset.sample(frac=sample_size/subset.shape[0], random_state=42) if subset.shape[0] > sample_size else subset
                subset = subset.dropna().reset_index(drop=True)
                # compute per-column quantile cut-off based on subset to trim extreme values
                local_cut_x = subset[x_col].quantile(quantile)
                local_cut_y = subset[y_col].quantile(quantile)
                
                # Apply both local and global limits strictly
                mask = (subset[x_col] <= local_cut_x) & (subset[y_col] <= local_cut_y) & \
                    (subset[x_col] <= x_lim) & (subset[y_col] <= y_lim)
                
                subset_scat = subset[mask].dropna().reset_index(drop=True)
                print(subset.shape)

                if subset.empty:
                    print(f"Warning: No data for {labels[i]} in condition '{cond_name_row}' and '{cond_name_col}'")
                    continue  # skip plotting if no data available for this category and condition

                # Scatter and KDE on the joint axis
                sns.scatterplot(data=subset_scat, x=x_col, y=y_col, ax=g.ax_joint,
                                color=colors[i], marker=markers[i], alpha=0.4, s=15, label=labels[i])
                sns.kdeplot(data=subset_scat, x=x_col, y=y_col, ax=g.ax_joint,
                            color=colors[i], levels=[0.1,0.25,0.5,0.75,0.9], alpha=0.8)

                # Marginal histograms on the joint grid
                sns.histplot(data=subset, x=x_col, ax=g.ax_marg_x, color=colors[i],
                            element="step", fill=False, linewidth=2, binrange=(x_min, x_lim))
                sns.histplot(data=subset, y=y_col, ax=g.ax_marg_y, color=colors[i],
                            element="step", fill=False, linewidth=2, binrange=(y_min, y_lim))

            # Force limits to keep bricks comparable across categories
            xmin, xmax = g.ax_joint.get_xlim()
            ymin, ymax = g.ax_joint.get_ylim()
            g.ax_joint.set_xlim(xmin, xmax)
            g.ax_joint.set_ylim(ymin, ymax)
            g.ax_joint.set_xlabel(label_dict[x_col])  # set x label using provided mapping
            g.ax_joint.set_ylabel(label_dict[y_col])  # set y label using provided mapping
            g.ax_joint.legend(title="Origin Cluster", loc='upper right')  # add legend

            # Convert seaborn JointGrid into a patchworklib brick for layout
            
            curr_brick = pw.load_seaborngrid(g)
            curr_brick.case.set_title(f"{cond_name_row} {cond_name_col}", fontsize=10)
            g_list_cols.append(curr_brick)
            plt.close(g.fig)  # close the matplotlib figure to free memory

        # after iterating column bins, stack them horizontally
        g_list_row.append(pw.stack(g_list_cols, operator="|"))

    # stack the row bricks vertically to produce the full grid
    full_grid = pw.stack(g_list_row, operator="/")

    if save:
        # save to a PDF file in the images directory
        path = f"images/{row_col}/threshold_split/{x_col}/joint_threshold_{x_col}_{y_col}.pdf"
        full_grid.savefig(fname=path, quick=True)
        print(f"Saved to {path}")
    else:
        return full_grid  # return the brick object for interactive display




def pdf_to_image_widget(file_path, width=800):
    """Converts the first page of a PDF to a high-res Image widget."""
    doc = fitz.open(file_path)
    page = doc.load_page(0)
    
    # Increase resolution for sharp text in graphs
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
    image_bytes = pix.tobytes("png")
    
    # Return as a Jupyter Image widget
    return widgets.Image(value=image_bytes, format='png', width=width)


def plot_feature_importance(model, features, title, label_dict):
    importances = model.feature_importances_
    importances_norm = 100 * importances / importances.sum()
    
    importance_df = pd.DataFrame({'feature': features,
                                  'importance': importances_norm}).sort_values('importance', ascending=False)

    print("\nFeature importances (percentage):")
    print(importance_df)
    names = importance_df['feature'].map(label_dict)
    plt.figure(figsize=(10,6))
    plt.title(title)
    sns.set_style("whitegrid")
    sns.set_palette("Set2")
    sns.barplot(x=range(len(features)), y=importance_df['importance'], align='center', edgecolor='black',hue=importance_df['feature'], legend=False)
    plt.xticks(range(len(features)), names, rotation=90)
    plt.ylabel("Importance (%)")
    plt.tight_layout()
    plt.show()