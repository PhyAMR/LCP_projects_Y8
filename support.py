import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

# Configuración de estilo científico con Seaborn
sns.set_context("paper", font_scale=1.2) # Escala para artículos
sns.set_style("whitegrid", {'grid.linestyle': '--'}) # Fondo limpio con rejilla sutil

def plot_3d_scientific(df, x, y, z, hue_col):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Elegir una paleta científica (ej: 'viridis', 'magma' o 'rocket')
    palette = sns.color_palette("viridis", as_cmap=True)
    
    # El scatter plot
    # s=20 define el tamaño del punto, edgecolor='w' da claridad si hay solapamiento
    scatter = ax.scatter(df[x], df[y], df[z], 
                        c=df[hue_col], 
                        cmap=palette, 
                        s=30, 
                        alpha=0.7, 
                        edgecolors='w', 
                        linewidth=0.5)
    
    # Configuración de etiquetas (Labels)
    ax.set_xlabel(f'\n{x}', linespacing=2.5, fontweight='bold')
    ax.set_ylabel(f'\n{y}', linespacing=2.5, fontweight='bold')
    ax.set_zlabel(f'\n{z}', linespacing=2.5, fontweight='bold')
    
    # Limpiar el fondo de los ejes (opcional, para un look más moderno)
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    
    # Añadir barra de color
    cbar = plt.colorbar(scatter, ax=ax, shrink=0.5, aspect=10, pad=0.1)
    cbar.set_label(hue_col, fontweight='bold')
    
    plt.tight_layout()
    return fig, ax

