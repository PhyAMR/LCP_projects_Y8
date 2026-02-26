import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

sns.set_context("paper", font_scale=1.2)
sns.set_style("whitegrid", {'grid.linestyle': '--'})

def plot_3d_scientific(df, x, y, z, hue_col):

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    # Obtener categorías únicas
    categories = df[hue_col].unique()
    n_categories = len(categories)

    # Paleta categórica de seaborn
    palette = sns.color_palette("deep", n_categories)

    # Crear diccionario categoría → color
    color_dict = dict(zip(categories, palette))

    # Convertir columna categórica en array de colores
    colors = df[hue_col].map(color_dict).values

    # Scatter 3D
    scatter = ax.scatter(
        df[x].values,
        df[y].values,
        df[z].values,
        c=colors,           # array explícito de colores
        s=30,
        alpha=0.8,
        edgecolor='white',
        linewidth=0.4
    )

    # Labels
    ax.set_xlabel(x, labelpad=12, fontweight='bold')
    ax.set_ylabel(y, labelpad=12, fontweight='bold')
    ax.set_zlabel(z, labelpad=12, fontweight='bold')

    # Fondo limpio
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False

    # 🔹 Crear leyenda manual
    for cat in categories:
        ax.scatter([], [], [], 
                   color=color_dict[cat], 
                   label=cat, 
                   s=40)

    ax.legend(title=hue_col, frameon=False)

    plt.tight_layout()

    return fig, ax