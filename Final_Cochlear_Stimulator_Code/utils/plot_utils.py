from matplotlib.figure import Figure
import numpy as np
from matplotlib.figure import Figure
import numpy as np
from matplotlib import rcParams

'''
def plot_time_domain(x, fs):
    fig = Figure(figsize=(4.5, 3.2), dpi=100)
    ax = fig.add_subplot(111)
    time_axis = np.arange(len(x)) / fs
    ax.plot(time_axis, x, color='#9dc183', linewidth=2.0)
    ax.set_facecolor("#fffdf6")
    fig.patch.set_facecolor("#fffdf6")
    ax.grid(True, linestyle="--", color="#e0dacd")
    ax.set_title("Time Domain Plot", fontsize=13, fontweight="bold", color="#3d2f1e")
    ax.set_xlabel("Time (s)", fontsize=10, color="#40342a")
    ax.set_ylabel("Amplitude", fontsize=10, color="#40342a")
    ax.tick_params(colors="#40342a", labelsize=9)
    fig.tight_layout()
    return fig
'''

# Optional: Use a pixel-style font if installed
rcParams['font.family'] = 'VT323'

def plot_time_domain(x, fs):
    line_color = "#3e0b4f"     # deep plum
    label_color = "#000000"
    grid_color = "#e6d6f0"     # pale lilac
    bg_color = "#fffdf6"       # cream dream

    fig = Figure(figsize=(4.5, 3.2), dpi=100)
    ax = fig.add_subplot(111)
    
    time_axis = np.arange(len(x)) / fs
    ax.plot(time_axis, x, color=line_color, linewidth=2.0)

    # Set background colors
    ax.set_facecolor(bg_color)
    fig.patch.set_facecolor(bg_color)

    # Grid
    ax.grid(True, linestyle="--", color=grid_color)

    # Titles and labels in kawaii lavender
    ax.set_title("Time Domain Plot", fontsize=10, color=label_color, pad=10)
    ax.set_xlabel("Time (s)", fontsize=8, color=label_color)
    ax.set_ylabel("Amplitude", fontsize=8, color=label_color)

    # Tick styling
    ax.tick_params(colors=label_color, labelsize=7)

    fig.tight_layout()
    return fig

def plot_electrodogram(ftm, strategy_name, channels=16):
    fig = Figure(figsize=(4.5, 3.2), dpi=100)
    ax = fig.add_subplot(111)
    im = ax.imshow(ftm[::-1], aspect='auto', cmap='viridis', extent=[0, 1000, 1, channels])
    ax.set_facecolor("#fffdf6")
    fig.patch.set_facecolor("#fffdf6")
    ax.set_title(f"Electrodogram – {strategy_name}", fontsize=13, fontweight="bold", color="#3d2f1e")
    ax.set_xlabel("Time (ms)", fontsize=10, color="#40342a")
    ax.set_ylabel("Electrode", fontsize=10, color="#40342a")
    ax.set_yticks(np.arange(1, channels + 1))
    ax.set_yticklabels(np.arange(1, channels + 1))
    ax.tick_params(colors="#40342a", labelsize=9)
    ax.invert_yaxis()
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Amplitude", fontsize=9, color='#3d2f1e')
    cbar.ax.yaxis.set_tick_params(color='#40342a')
    for label in cbar.ax.get_yticklabels():
        label.set_color('#40342a')
        label.set_fontsize(8)
    fig.tight_layout()
    return fig
