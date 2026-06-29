"""
Shared plotting style for UniSTAR post-processing.
RULE: never use black. All text/axes use dark slate-blue; data uses a
colourblind-safe (Okabe-Ito, black removed) palette. Clean layout,
no overlapping labels.
Author: Akosa Samuel Onyejekwe (Independent Researcher)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from cycler import cycler

INK    = "#1f3b57"     # dark slate-blue used in place of black (text/axes)
GRIDC  = "#b9c6d6"
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7",
           "#E69F00", "#56B4E9", "#8E44AD", "#117A65"]

SEQ_CMAP  = "turbo"      # contour fills (no black)
TEMP_CMAP = "plasma"
MACH_CMAP = "viridis"
DIV_CMAP  = "RdYlBu_r"


def apply():
    plt.rcParams.update({
        "figure.dpi": 130,
        "savefig.dpi": 160,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "font.size": 12,
        "font.family": "DejaVu Sans",
        "axes.titlesize": 13.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "axes.labelcolor": INK,
        "axes.edgecolor": INK,
        "axes.linewidth": 1.1,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "axes.titlecolor": INK,
        "axes.grid": True,
        "grid.color": GRIDC,
        "grid.alpha": 0.6,
        "grid.linewidth": 0.8,
        "legend.frameon": True,
        "legend.framealpha": 0.92,
        "legend.edgecolor": GRIDC,
        "lines.linewidth": 2.4,
        "axes.prop_cycle": cycler(color=PALETTE),
    })


def finish(fig, path, caption=None):
    if caption:
        fig.text(0.5, -0.01, caption, ha="center", va="top",
                 fontsize=9, color=INK, style="italic")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path
