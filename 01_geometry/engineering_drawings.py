"""
STAGE 01b - ENGINEERING DRAWINGS
Formal multi-view engineering drawings of the Mach-4 intake SWBLI test
section: orthographic (front / plan / side), isometric, and a sectional
view, each with dimension lines and a title block. No black is used.
Author: Akosa Samuel Onyejekwe (Independent Researcher)
"""
import os, sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import case_config as cfg
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "05_postprocessing"))
import plot_style as ps
ps.apply()
INK = ps.INK
P = ps.PALETTE

L = cfg.PLATE_LEN * 1000.0      # mm
H = cfg.DUCT_HEIGHT * 1000.0    # mm
W = cfg.PLATE_SPAN * 1000.0     # mm
XI = cfg.X_IMPINGE * 1000.0     # mm
T_WALL_TH = 12.0                # wall plate thickness mm
MAN = []


def _dim(ax, p1, p2, text, off=0.0, vert=False, color=None):
    color = color or P[5]
    x1, y1 = p1; x2, y2 = p2
    if vert:
        ax.annotate("", (x2, y2), (x1, y1),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.2))
        ax.text(x1 + off, (y1 + y2) / 2, text, color=color, fontsize=9,
                rotation=90, va="center", ha="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    else:
        ax.annotate("", (x2, y2), (x1, y1),
                    arrowprops=dict(arrowstyle="<->", color=color, lw=1.2))
        ax.text((x1 + x2) / 2, y1 + off, text, color=color, fontsize=9,
                ha="center", va="center",
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))


def _title_block(fig, view):
    fig.text(0.99, 0.012,
             f"HSRA Mach-4 Intake — SWBLI Test Section  |  {view}  |  "
             f"Units: mm  |  Scale: NTS  |  A. S. Onyejekwe",
             ha="right", va="bottom", fontsize=8, color=INK,
             bbox=dict(boxstyle="round,pad=0.3", fc="#eef2f7", ec=ps.GRIDC))


def drawing_side():
    """Side elevation (x-y plane) with shock geometry."""
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    xg = (cfg.X_IMPINGE - cfg.DUCT_HEIGHT / np.tan(np.radians(cfg.beta_inc))) * 1000
    xgt = cfg.PLATE_LEN * 0.65 * 1000
    # wall plate
    ax.add_patch(Rectangle((0, -T_WALL_TH), L, T_WALL_TH, fc=P[7], ec=INK, alpha=0.5, lw=1.4))
    # generator
    ax.add_patch(Rectangle((xg, H), xgt - xg, 14, fc=P[6], ec=INK, alpha=0.5, lw=1.4))
    # shocks
    ax.plot([xg, XI], [H, 0], color=P[1], lw=2.2)
    xr = (cfg.X_IMPINGE + cfg.DUCT_HEIGHT / np.tan(np.radians(cfg.beta_ref))) * 1000
    ax.plot([XI, xr], [0, H], color=P[3], lw=2.2, ls="--")
    ax.text(xg + 40, H * 0.55, f"incident\nβ={cfg.beta_inc:.1f}°", color=P[1], fontsize=9)
    ax.text(xr - 150, H * 0.6, f"reflected\nβ={cfg.beta_ref:.1f}°", color=P[3], fontsize=9)
    ax.plot(XI, 0, "o", color=P[0], ms=9)
    # dims
    _dim(ax, (0, -34), (L, -34), f"L = {L:.0f}")
    _dim(ax, (-26, 0), (-26, H), f"H = {H:.0f}", vert=True)
    _dim(ax, (0, H + 40), (XI, H + 40), f"x_imp = {XI:.0f}")
    ax.set_xlim(-70, L + 40); ax.set_ylim(-60, H + 70)
    ax.set_aspect("equal"); ax.set_xlabel("x [mm]"); ax.set_ylabel("y [mm]")
    ax.set_title("SIDE ELEVATION (looking −z)")
    ax.grid(True, alpha=0.3)
    _title_block(fig, "Side elevation")
    return _save(fig, "DWG1_side_elevation.png", "Side elevation",
                 "Orthographic side view with shock geometry and principal dimensions.")


def drawing_plan():
    """Plan / top view (x-z plane)."""
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    ax.add_patch(Rectangle((0, 0), L, W, fc=P[7], ec=INK, alpha=0.35, lw=1.4))
    # impingement footprint line (spanwise)
    ax.plot([XI, XI], [0, W], color=P[1], lw=2.0, ls="--")
    ax.text(XI + 8, W * 0.5, "shock\nimpingement\nline", color=P[1], fontsize=9)
    # interaction band
    ax.add_patch(Rectangle((458, 0), 140, W, fc=P[4], ec="none", alpha=0.18))
    ax.text(528, W * 0.08, "interaction band", color=P[4], ha="center", fontsize=9)
    _dim(ax, (0, -22), (L, -22), f"L = {L:.0f}")
    _dim(ax, (-26, 0), (-26, W), f"W = {W:.0f}", vert=True)
    ax.set_xlim(-70, L + 30); ax.set_ylim(-45, W + 25)
    ax.set_aspect("equal"); ax.set_xlabel("x [mm]"); ax.set_ylabel("span z [mm]")
    ax.set_title("PLAN VIEW (looking −y, onto wall)")
    ax.grid(True, alpha=0.3)
    _title_block(fig, "Plan view")
    return _save(fig, "DWG2_plan_view.png", "Plan view",
                 "Top view of the cowl wall with spanwise shock-impingement line.")


def drawing_front():
    """Front view (y-z plane) — duct cross-section."""
    fig, ax = plt.subplots(figsize=(6.6, 5.4))
    ax.add_patch(Rectangle((0, -T_WALL_TH), W, T_WALL_TH, fc=P[7], ec=INK, alpha=0.5, lw=1.4))
    ax.add_patch(Rectangle((0, H), W, 14, fc=P[6], ec=INK, alpha=0.5, lw=1.4))
    ax.add_patch(Rectangle((0, 0), W, H, fc=P[0], ec=INK, alpha=0.08, lw=1.0, ls=":"))
    ax.text(W / 2, H / 2, "flow\nchannel", color=P[0], ha="center", va="center", fontsize=10)
    _dim(ax, (0, -34), (W, -34), f"W = {W:.0f}")
    _dim(ax, (-26, 0), (-26, H), f"H = {H:.0f}", vert=True)
    ax.set_xlim(-70, W + 30); ax.set_ylim(-55, H + 60)
    ax.set_aspect("equal"); ax.set_xlabel("span z [mm]"); ax.set_ylabel("y [mm]")
    ax.set_title("FRONT VIEW (looking +x, inflow)")
    ax.grid(True, alpha=0.3)
    _title_block(fig, "Front view")
    return _save(fig, "DWG3_front_view.png", "Front view",
                 "Inflow-facing cross-section: wall plate, shock generator, duct height.")


def drawing_isometric():
    """Isometric assembly view."""
    fig = plt.figure(figsize=(9.6, 7.2))
    ax = fig.add_subplot(111, projection="3d")
    Lx, Hy, Wz = L, H, W
    # wall slab
    _box(ax, 0, Lx, 0, Wz, -T_WALL_TH, 0, P[7], 0.45)
    # generator slab
    xg = (cfg.X_IMPINGE - cfg.DUCT_HEIGHT / np.tan(np.radians(cfg.beta_inc))) * 1000
    xgt = cfg.PLATE_LEN * 0.65 * 1000
    _box(ax, xg, xgt, 0, Wz, Hy, Hy + 14, P[6], 0.45)
    # shock planes (incident, reflected) as translucent surfaces
    zz = np.array([0, Wz])
    xi_line = np.array([xg, XI]); yi_line = np.array([Hy, 0])
    Xs, Zs = np.meshgrid(xi_line, zz); Ys = np.tile(yi_line, (2, 1))
    ax.plot_surface(Xs, Zs, Ys, color=P[1], alpha=0.35, linewidth=0)
    xr = (cfg.X_IMPINGE + cfg.DUCT_HEIGHT / np.tan(np.radians(cfg.beta_ref))) * 1000
    xr_line = np.array([XI, xr]); yr_line = np.array([0, Hy])
    Xr, Zr = np.meshgrid(xr_line, zz); Yr = np.tile(yr_line, (2, 1))
    ax.plot_surface(Xr, Zr, Yr, color=P[3], alpha=0.30, linewidth=0)
    ax.set_xlabel("x [mm]"); ax.set_ylabel("span z [mm]"); ax.set_zlabel("y [mm]")
    ax.set_title("ISOMETRIC ASSEMBLY VIEW")
    ax.set_box_aspect((2.4, 0.9, 0.7)); ax.view_init(elev=22, azim=-58)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((1, 1, 1, 0))
        axis.pane.set_edgecolor(ps.GRIDC)
    _title_block(fig, "Isometric")
    return _save(fig, "DWG4_isometric.png", "Isometric view",
                 "Isometric assembly: cowl wall, shock generator, incident & "
                 "reflected shock planes.")


def drawing_section():
    """Sectional view A-A through the interaction (shows BL & bubble)."""
    sd = __import__("pandas").read_csv(os.path.join(cfg.DIR_SOL, "surface_distributions.csv"))
    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    x = sd.x_m.values * 1000
    delta = sd.delta_mm.values
    # wall
    ax.add_patch(Rectangle((0, -8), L, 8, fc=P[7], ec=INK, alpha=0.5, lw=1.2))
    # boundary layer (hatched fill)
    ax.fill_between(x, 0, delta, color=P[0], alpha=0.18)
    ax.plot(x, delta, color=P[0], lw=2.0, label="boundary-layer edge δ")
    # separation bubble outline
    mask = (x >= 458) & (x <= 598)
    bub = np.where(mask, 0.35 * (delta - np.interp(458, x, delta)), 0)
    ax.fill_between(x, 0, np.clip(bub, 0, None), color=P[1], alpha=0.4,
                    label="separation bubble")
    # shocks
    ax.plot([(XI - H / np.tan(np.radians(cfg.beta_inc))), XI], [H, 0], color=P[1], lw=1.8)
    ax.plot([XI, XI + H / np.tan(np.radians(cfg.beta_ref))], [0, H], color=P[3], lw=1.8, ls="--")
    ax.set_xlim(0, L); ax.set_ylim(-12, H * 0.55)
    ax.set_xlabel("x [mm]"); ax.set_ylabel("y [mm]")
    ax.set_title("SECTION A–A (mid-span) — boundary layer, separation bubble & shocks")
    ax.legend(loc="upper left")
    _title_block(fig, "Section A-A")
    return _save(fig, "DWG5_section_AA.png", "Sectional view A–A",
                 "Mid-span section showing the boundary-layer growth, the "
                 "separation bubble and the impinging/reflected shocks.")


def _box(ax, x0, x1, z0, z1, y0, y1, color, alpha):
    """Draw a 3D rectangular box."""
    import itertools
    verts = list(itertools.product([x0, x1], [z0, z1], [y0, y1]))
    faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4],
             [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    polys = [[verts[i] for i in fc] for fc in faces]
    pc = Poly3DCollection(polys, facecolor=color, edgecolor=INK, alpha=alpha, linewidths=0.8)
    ax.add_collection3d(pc)


def _save(fig, fname, title, caption):
    out = os.path.join(cfg.DIR_GEOM, fname)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor="white", dpi=160)
    plt.close(fig)
    MAN.append((fname, title, caption))
    return out


def run():
    for fn in [drawing_front, drawing_plan, drawing_side,
               drawing_isometric, drawing_section]:
        p = fn()
        print("  drawing:", os.path.basename(p))
    import pandas as pd
    pd.DataFrame(MAN, columns=["filename", "title", "caption"]).to_csv(
        os.path.join(cfg.DIR_GEOM, "drawing_manifest.csv"), index=False)
    print(f"[01b-drawings] wrote {len(MAN)} engineering drawings")


if __name__ == "__main__":
    run()
