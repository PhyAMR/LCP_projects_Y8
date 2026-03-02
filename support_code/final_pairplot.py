# This file creats the html report for the final dataset since jupyter keeps crushing when I try to make it in the notebook
import pandas as pd
from pathlib import Path
import seaborn as sns
import numpy as np

# 1. Definir la ruta base donde están tus carpetas
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

base_path = Path('fastcluster_comp_physA')
all_data = []
for filepath in base_path.glob('**/*/Dyn/*/nth_generation.txt'):
    sys_origin = filepath.parts[-4].split('_')[0]
    mettalictty = float(filepath.parts[-2])
    df = read_nth_generation(filepath)
    df['sys'] = sys_origin
    df['met'] = mettalictty
    all_data.append(df)

df_final = pd.concat(all_data, ignore_index=True, sort=False)

df_final.drop(columns=['c5:theta1', 'c6:theta2', 'c7:SMA(Rsun)', 'c8:ecc','c10:SMAfin(cm)', 'c11:eccfin',
       'c12:tpeters/Myr', 'c14:vkick/kms', 'c18:flag1', 'c19:flag2', 'c20:flag3', 'c21:flagSN', 'c22:flag_exch',
       'c23:flag_t3bb', 'c24:flag_evap','c26:ecc(10Hz)'], inplace=True)
df_final['c0:identifier'] = df_final['c0:identifier'].astype('category')

df_final_no_id = df_final.drop(columns=['c0:identifier'])
numeric_cols = df_final_no_id.select_dtypes(include=[np.number]).columns.tolist()

g = sns.pairplot(df_final_no_id, 
                 vars=numeric_cols, # Only plot these
                 hue="sys", 
                 diag_kind="hist", 
                 palette="Set2")
g.map_lower(sns.kdeplot, levels=4, color=".2")
g.fig.suptitle("Pairplot of the final dataset", y=1.02)
g.savefig("final_pairplot.png", dpi=300)