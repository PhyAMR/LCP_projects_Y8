"""
Here are some utility functions that will allow us to easily call them in the main notebook. This includes functions for plotting, data manipulation, and any other helper functions we might need.

This file adds descriptive docstrings and inline comments for each function to improve readability and maintainability.
"""

import pandas as pd  # pandas for DataFrame handling

from pathlib import Path  # Pathlib for file system path operations
import numpy as np  # numpy for numeric utilities (import kept for compatibility)
from beautifultable import BeautifulTable  # BeautifulTable for terminal-friendly tables
import re
import glob

def read_nth_generation(path):
    # read and repair header (merge tokens that start with '(' into previous token)
    with open(path, 'r') as f:
        header = f.readline().strip()
    tokens = header.split()
    names = []
    for tok in tokens:
        if tok.startswith('(') and names:
            names[-1] = names[-1] + ' ' + tok
        else:
            names.append(tok)
    # read remaining rows using whitespace splitting and assign repaired names
    df = pd.read_csv(path, sep='\s+', header=None, names=names, skiprows=1, comment='#')
    return df

def create_df(columns_to_keep=None, path = 'fastcluster_comp_physA', folder_path = '**/*/Dyn/*/nth_generation.txt'):
    base_path = Path(path)
    all_data = []
    for filepath in base_path.glob(folder_path):
        sys_origin = filepath.parts[-4].split('_')[0]
        mettalictty = float(filepath.parts[-2])
        df = read_nth_generation(filepath)
        df['sys'] = sys_origin
        df['met'] = mettalictty
        all_data.append(df)

    df_final = pd.concat(all_data, ignore_index=True, sort=False)
    df_final.columns = [col.split('/')[0] for col in df_final.columns]
    if columns_to_keep is not None:
        df_final = df_final[columns_to_keep + ['sys', 'met']]  # Ensure sys and met are always included
    return df_final

def dataset_drift_report(dfs,quantile_cut=0.9,drift_threshold=10,columns_to_compare=None):
    """
        Compare statistics across datasets and detect drift.

        Parameters
        ----------
        dfs : dict
            {"dataset_name": dataframe}
        num_rows : float
            Number of rows to sample from each dataset (if <1.0, treated as fraction; if >=1.0, treated as absolute number)
        quantile_cut : float
            Upper quantile used to remove outliers
        drift_threshold : float
            % difference used to flag drift
    """

    stats_list = []
    for name in list(dfs.keys())[1:]:
        print("Sample fractions:" + str((dfs[name].shape[0]/dfs[list(dfs.keys())[0]].shape[0])))
        
    for name, df in dfs.items():

        df = df.select_dtypes(include="number")
        if columns_to_compare is not None:
            df = df[columns_to_compare]
        
        # full stats
        stats = df.agg(["mean", "median", "std"]).T
        stats.columns = ["Mean", "Median", "Std"]

        # quantile filtered stats
        q_cut = df.quantile(quantile_cut)
        df_q = df.where(df.le(q_cut))

        stats_q = df_q.agg(["mean", "median"]).T
        stats_q.columns = [
            f"Mean ({int(quantile_cut*100)}%Q)",
            f"Median ({int(quantile_cut*100)}%Q)"
        ]

        stats = pd.concat([stats, stats_q], axis=1)
        stats["Dataset"] = name
        stats["Column"] = stats.index

        stats_list.append(stats.reset_index(drop=True))

    report = pd.concat(stats_list)

    # Pivot for comparison
    pivot = report.pivot(index="Column", columns="Dataset")

    pivot.columns = ["_".join(col) for col in pivot.columns]
    pivot = pivot.reset_index()

    # Drift calculation (relative difference)
    datasets = list(dfs.keys())

    drift_info = []

    if len(datasets) >= 2:
        base = datasets[0]
        for other in datasets[1:]:
            # Calculate drift relative to the first dataset in the dictionary
            mean_diff = ((pivot[f"Mean_{other}"] - pivot[f"Mean_{base}"]) / pivot[f"Mean_{base}"]) * 100
            median_diff = ((pivot[f"Median_{other}"] - pivot[f"Median_{base}"]) / pivot[f"Median_{base}"]) * 100
            std_diff = ((pivot[f"Std_{other}"] - pivot[f"Std_{base}"]) / pivot[f"Std_{base}"]) * 100

            # Drift flag based on max of the three metrics
            drift_flag = pd.concat([mean_diff.abs(), median_diff.abs(), std_diff.abs()], axis=1).max(axis=1) > drift_threshold

            drift_df = pd.DataFrame({
                "Column": pivot["Column"],
                "Dataset_Compared": other,
                "Mean_diff_%": mean_diff,
                "Median_diff_%": median_diff,
                "Std_diff_%": std_diff,
                "Drift": drift_flag
            })
            drift_info.append(drift_df)

    drift_table_df = pd.concat(drift_info)

    # ----------- BEAUTIFULTABLE REPORT -----------
    table = BeautifulTable(maxwidth=120)
    table.set_style(BeautifulTable.STYLE_RST) # Clean, terminal-friendly style
    
    # Header
    table.columns.header = ["Column", "Comp vs Base", "Mean Δ%", "Median Δ%", "Std Δ%", "Status"]
    
    for _, row in drift_table_df.iterrows():
        status = "DRIFT ⚠" if row["Drift"] else "OK"
        table.rows.append([
            row["Column"],
            row["Dataset_Compared"],
            f"{row['Mean_diff_%']:.2f}%",
            f"{row['Median_diff_%']:.2f}%",
            f"{row['Std_diff_%']:.2f}%",
            status
        ])

    # Construct the final text output
    meta_info = (
        f"DATASET DRIFT REPORT\n"
        f"{'='*50}\n"
        f"Base Dataset: {datasets[0]}\n"
        f"Outlier filter: {quantile_cut*100:.0f}% Quantile\n"
        f"Threshold: {drift_threshold}%\n"
        f"{'='*50}\n"
    )
    
    report_text = meta_info + str(table)

    return report_text, report, drift_table_df

    
def extract_combinations_from_filenames(pattern="images/*/threshold_split/*/joint_threshold_*_*.pdf"):
    combo_list = []
    # Define the pattern to search for
    # * is a wildcard that matches any characters
    search_pattern = pattern

    # This regex extracts x_col and y_col from the specific filename format:
    # joint_threshold_{x_col}_{y_col}.pdf
    # [^_]+ matches characters that are not underscores
    path_regex = r"joint_threshold_([^_]+)_([^_]+)\.pdf$"


    # Loop through all files matching the pattern
    for file_path in glob.glob(search_pattern):
        # Extract the filename from the full path
        file_name = file_path.split('/')[-1]
        
        # Use regex to find x_col and y_col
        match = re.search(path_regex, file_name)
        
        if match:
            x_val = match.group(1)
            y_val = match.group(2)
            combo_list.append((x_val, y_val))
        else:
            print(f"Filename {file_name} does not match the expected pattern.")
    return combo_list




