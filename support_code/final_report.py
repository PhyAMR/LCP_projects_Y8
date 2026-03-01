# This file creats the html report for the final dataset since jupyter keeps crushing when I try to make it in the notebook
import pandas as pd
from pathlib import Path
from ydata_profiling import ProfileReport

# 1. Definir la ruta base donde están tus carpetas
base_path = Path('fastcluster_comp_physA') # Cambia '.' por la ruta real si es necesario

all_data = []

# 2. Buscamos todos los archivos 'nth_generation.txt' recursivamente
for filepath in base_path.glob('**/*/Dyn/*/nth_generation.txt'):
    
    # Extraemos metadatos de la ruta
    # filepath.parts nos da una lista con los nombres de las carpetas
    sys_origin = filepath.parts[-4].split('_')[0]  # GC, NSC o YSC
    mettalictty = float(filepath.parts[-2])           # 0.0002, 0.0004, etc.
    
    # 3. Leer el archivo
    # Asumo que es un archivo separado por espacios o comas. 
    # Ajusta 'sep' según sea tu caso (si es tabulación usa sep='\t')
    df = pd.read_csv(filepath, sep='\\s+') 
    
    # 4. Añadimos los metadatos como nuevas columnas
    df['sys'] = sys_origin
    df['met'] = mettalictty
    
    all_data.append(df)

# 5. Concatenar todo en un solo DataFrame
df_final = pd.concat(all_data, ignore_index=True)

df_final.drop(columns=['c5:theta1', 'c6:theta2', 'c7:SMA(Rsun)', 'c8:ecc','c10:SMAfin(cm)', 'c11:eccfin',
       'c12:tpeters/Myr', 'c14:vkick/kms', 'c18:flag1', 'c19:flag2', 'c20:flag3', 'c21:flagSN', 'c22:flag_exch',
       'c23:flag_t3bb', 'c24:flag_evap','c26:ecc(10Hz)'], inplace=True)

profile_total = ProfileReport(df_final, title="Profiling Report for total dataset", explorative=True)
profile_total.to_file("total_report.html")