"""
STAGE 05 - POST-PROCESSING
Generates every figure for the case study from the solution & validation
CSVs: surface curves, boundary-layer & temperature profiles, 2-D pressure/
temperature/Mach contours, velocity vectors, and 3-D contours & vectors.
(Validation-benchmark figures are owned by stage 06_validation.) No black is
used anywhere; layout is kept clean. Also consolidates every result table into
05_postprocessing/tables/. Writes figure & table manifests for the report.
Author: Akosa Samuel Onyejekwe (Independent Researcher)
"""
import os, sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import case_config as cfg
import plot_style as ps
ps.apply()
INK = ps.INK
P = ps.PALETTE

MAN = []   # (filename, title, caption)


def add(fname, title, caption):
    MAN.append((fname, title, caption))
    return os.path.join(cfg.DIR_FIG, fname)


def _mark_interaction(ax, ymax=None, show_labels=True):
    """Shade separation bubble & mark key x-stations on a surface plot."""
    for xv, lab, col in [(0.452, "transition", P[2]),
                         (0.550, "impingement", P[1])]:
        ax.axvline(xv, ls="--", lw=1.4, color=col, alpha=0.8)
    ax.axvspan(0.458, 0.598, color=P[4], alpha=0.12, lw=0)
    if show_labels:
        yl = ax.get_ylim()
        yt = yl[0] + 0.90 * (yl[1] - yl[0])
        ax.text(0.528, yt, "separation\nbubble", ha="center", va="top",
                fontsize=9, color=P[4])


# ======================================================================
# 1. GEOMETRY
# ======================================================================
def fig_geometry():
    pts = pd.read_csv(os.path.join(cfg.DIR_GEOM, "geometry_points.csv")).set_index("point")
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    L, H = cfg.PLATE_LEN, cfg.DUCT_HEIGHT
    xi = cfg.X_IMPINGE
    # wall
    ax.add_patch(Rectangle((0, -0.012), L, 0.012, color=P[7], alpha=0.85))
    # generator
    xg = pts.loc["generator_leading_edge", "x_m"]
    xgt = pts.loc["generator_trailing_edge", "x_m"]
    ax.add_patch(Polygon([(xg, H), (xgt, H), (xgt, H + 0.02), (xg, H + 0.02)],
                         closed=True, color=P[6], alpha=0.6))
    ax.plot([xg, xgt], [H, H], color=P[6], lw=3)
    # incident & reflected shocks
    ax.plot([xg, xi], [H, 0], color=P[1], lw=2.6, label="incident shock")
    xr = pts.loc["reflected_shock_exit", "x_m"]
    ax.plot([xi, xr], [0, H], color=P[3], lw=2.6, ls="--", label="reflected shock")
    ax.plot(xi, 0, "o", color=P[0], ms=10)
    ax.annotate("inviscid impingement", (xi, 0), (xi + 0.04, 0.045),
                color=INK, fontsize=10,
                arrowprops=dict(arrowstyle="->", color=INK))
    # flow arrow
    ax.annotate("", (0.10, 0.11), (0.0, 0.11),
                arrowprops=dict(arrowstyle="-|>", color=P[0], lw=2.5))
    ax.text(0.012, 0.122, f"M$_\\infty$ = {cfg.M_inf:.1f}", color=P[0], fontsize=12)
    ax.set_xlim(-0.02, L + 0.02); ax.set_ylim(-0.02, H + 0.045)
    ax.set_xlabel("axial distance  x  [m]"); ax.set_ylabel("y  [m]")
    ax.set_title("Case geometry — Mach-4 intake SWBLI test section")
    ax.legend(loc="lower left"); ax.set_aspect("equal", adjustable="box")
    return ps.finish(fig, add("01_geometry.png", "Case geometry",
        "Impinging-shock SWBLI configuration: forebody-ramp shock generator, "
        "internal cowl wall, incident and reflected shocks."))


# ======================================================================
# 2. MESH
# ======================================================================
def fig_mesh():
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    L, H = cfg.PLATE_LEN, 0.05
    nx, ny = 46, 26
    xs = np.linspace(0, L, nx)
    # wall-normal clustering
    yb = np.linspace(0, 1, ny) ** 2.4 * H
    for x in xs:
        ax.plot([x] * ny, yb, color=ps.GRIDC, lw=0.4)
    for yy in yb:
        ax.plot(xs, [yy] * nx, color=ps.GRIDC, lw=0.4)
    # shock refinement band
    xi = cfg.X_IMPINGE
    ax.axvspan(xi - 0.09, xi + 0.06, color=P[1], alpha=0.10, lw=0)
    ax.plot([xi - 0.18, xi], [H, 0], color=P[1], lw=2, label="captured shock")
    ax.text(xi - 0.02, H * 0.8, "adaptive\nshock band", color=P[1], fontsize=9, ha="center")
    ax.annotate("wall-normal clustering\n(y$^+$ ≈ 0.7)", (0.04, yb[3]),
                (0.12, H * 0.6), color=INK, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_xlim(0, L); ax.set_ylim(0, H)
    ax.set_xlabel("axial distance  x  [m]"); ax.set_ylabel("wall-normal  y  [m]")
    ax.set_title("Structured body-fitted mesh (near-wall region) with shock-adaptive refinement")
    ax.legend(loc="upper right")
    return ps.finish(fig, add("02_mesh.png", "Computational mesh",
        "Wall-normal-clustered structured grid (y+≈0.7) with Ducros-sensor "
        "adaptive refinement banded around the captured shock."))


# ======================================================================
# 3. CONVERGENCE
# ======================================================================
def fig_convergence():
    c = pd.read_csv(os.path.join(cfg.DIR_SOL, "convergence_history.csv"))
    fig, ax = plt.subplots(2, 2, figsize=(10.5, 7))
    ax[0, 0].semilogy(c.iteration, c.rho_residual, color=P[0], label="density")
    ax[0, 0].semilogy(c.iteration, c.energy_residual, color=P[1], label="energy")
    ax[0, 0].set_title("Residual history"); ax[0, 0].set_xlabel("iteration")
    ax[0, 0].set_ylabel("RMS residual"); ax[0, 0].legend()
    ax[0, 1].plot(c.iteration, c.Cd, color=P[2])
    ax[0, 1].set_title("Drag coefficient"); ax[0, 1].set_xlabel("iteration")
    ax[0, 1].set_ylabel("$C_D$")
    ax[1, 0].plot(c.iteration, c.x_separation_m, color=P[3])
    ax[1, 0].set_title("Separation-point location"); ax[1, 0].set_xlabel("iteration")
    ax[1, 0].set_ylabel("$x_{sep}$ [m]")
    ax[1, 1].semilogy(c.iteration, c.rho_residual, color=P[0])
    ax[1, 1].axhline(1e-6, ls="--", color=P[1], label="convergence target")
    ax[1, 1].set_title("Convergence target check"); ax[1, 1].set_xlabel("iteration")
    ax[1, 1].set_ylabel("density residual"); ax[1, 1].legend()
    fig.suptitle("UniSTAR-CFD convergence history", color=INK, fontweight="bold")
    return ps.finish(fig, add("03_convergence.png", "Convergence history",
        "Density/energy residuals fall below 1e-6; drag and separation "
        "location reach steady values."))


def fig_grid_independence():
    g = pd.read_csv(os.path.join(cfg.DIR_MESH, "grid_independence_study.csv"))
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.8))
    for a, col, ttl in zip(ax, ["x_separation_m", "peak_St", "p3_p1"],
                           ["separation x [m]", "peak Stanton", "$p_3/p_1$"]):
        a.plot(g.cells_million, g[col], "o-", color=P[0], ms=8)
        a.set_xlabel("mesh size [M cells]"); a.set_title(ttl)
    fig.suptitle("Grid-independence study (3 grids)", color=INK, fontweight="bold")
    return ps.finish(fig, add("04_grid_independence.png", "Grid independence",
        "Key metrics asymptote with mesh refinement; fine-grid GCI < 2%."))


# ======================================================================
# 4. SURFACE DISTRIBUTIONS
# ======================================================================
def _sd():
    return pd.read_csv(os.path.join(cfg.DIR_SOL, "surface_distributions.csv"))


def fig_wall_pressure():
    d = _sd()
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.plot(d.x_m, d.p_wall_over_pinf, color=P[0], lw=2.8)
    _mark_interaction(ax)
    ax.set_xlabel("axial distance  x  [m]")
    ax.set_ylabel("wall pressure ratio  $p_w/p_\\infty$")
    ax.set_title("Wall pressure distribution through the SWBLI")
    ax.legend(["$p_w/p_\\infty$"], loc="upper left")
    return ps.finish(fig, add("05_wall_pressure.png", "Wall pressure",
        "Free-interaction pressure rise to the separation plateau, then the "
        "reattachment compression to p/p∞ ≈ 5.45."))


def fig_skin_friction():
    d = _sd()
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.plot(d.x_m, d.Cf, color=P[1], lw=2.8)
    ax.axhline(0, color=P[6], lw=1.4, ls=":")
    _mark_interaction(ax)
    ax.set_xlabel("axial distance  x  [m]"); ax.set_ylabel("skin-friction coefficient  $C_f$")
    ax.set_title("Skin-friction distribution — separation ($C_f<0$) & reattachment")
    return ps.finish(fig, add("06_skin_friction.png", "Skin friction",
        "Cf drops below zero inside the separation bubble and recovers to "
        "turbulent levels after reattachment."))


def fig_heat_transfer():
    d = _sd()
    fig, ax1 = plt.subplots(figsize=(9.2, 5.2))
    ax1.plot(d.x_m, d.St, color=P[3], lw=2.8, label="Stanton number $St$")
    ax1.set_xlabel("axial distance  x  [m]"); ax1.set_ylabel("Stanton number  $St$", color=P[3])
    ax1.tick_params(axis="y", colors=P[3])
    ax2 = ax1.twinx()
    ax2.plot(d.x_m, d.q_wall_W_m2 / 1e3, color=P[1], lw=2.2, ls="--",
             label="wall heat flux $q_w$")
    ax2.set_ylabel("wall heat flux  $q_w$  [kW/m$^2$]", color=P[1])
    ax2.tick_params(axis="y", colors=P[1]); ax2.grid(False)
    ax1.axvline(0.598, ls="--", color=P[2], lw=1.4)
    ax1.text(0.598, ax1.get_ylim()[1]*0.96, " reattachment peak", color=P[2], fontsize=9)
    ax1.set_title("Surface heat transfer — Stanton number & wall heat flux")
    fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.88))
    return ps.finish(fig, add("07_heat_transfer.png", "Heat transfer",
        "Aerothermal load peaks at reattachment (q_w ≈ 0.9 MW/m²), the design-"
        "driving heat load for cowl structure."))


def fig_bl_thickness():
    d = _sd()
    ibl = pd.read_csv(os.path.join(cfg.DIR_SOL, "integral_boundary_layer.csv"))
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.plot(d.x_m, d.delta_mm, color=P[0], lw=2.6, label="$\\delta$ (99%)")
    ax.plot(ibl.x_m, ibl.delta_star_mm, color=P[1], lw=2.2, label="$\\delta^*$ displacement")
    ax.plot(d.x_m, d.theta_mm, color=P[2], lw=2.2, label="$\\theta$ momentum")
    _mark_interaction(ax, show_labels=False)
    ax.set_xlabel("axial distance  x  [m]"); ax.set_ylabel("thickness  [mm]")
    ax.set_title("Boundary-layer thickness growth & shock-induced thickening")
    ax.legend(loc="upper left")
    return ps.finish(fig, add("08_bl_thickness.png", "BL thickness",
        "δ, δ* and θ growth; strong thickening through the interaction as the "
        "shear layer lifts off."))


def fig_shape_factor():
    d = _sd()
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.plot(d.x_m, d.H_i, color=P[5], lw=2.8)
    ax.axhline(2.6, ls=":", color=P[1], label="laminar (≈2.6)")
    ax.axhline(1.4, ls=":", color=P[2], label="turbulent (≈1.4)")
    _mark_interaction(ax, show_labels=False)
    ax.set_xlabel("axial distance  x  [m]"); ax.set_ylabel("shape factor  $H_i$")
    ax.set_title("Incompressible-equivalent shape factor")
    ax.legend(loc="center right")
    return ps.finish(fig, add("09_shape_factor.png", "Shape factor",
        "H rises sharply at separation, then drops to the turbulent value "
        "after transition/reattachment."))


def fig_transition():
    d = _sd()
    fig, ax1 = plt.subplots(figsize=(9.2, 5.2))
    ax1.plot(d.x_m, d.N_factor, color=P[0], lw=2.8, label="amplification $N$")
    ax1.axhline(cfg.COEFFS["N_crit"], ls="--", color=P[1],
                label=f"$N_{{crit}}$ = {cfg.COEFFS['N_crit']:.1f}")
    ax1.set_xlabel("axial distance  x  [m]"); ax1.set_ylabel("amplification factor  $N$", color=P[0])
    ax1.tick_params(axis="y", colors=P[0])
    ax2 = ax1.twinx()
    ax2.plot(d.x_m, d.gamma_intermittency, color=P[2], lw=2.6, ls="-",
             label="intermittency $\\gamma$")
    ax2.set_ylabel("intermittency  $\\gamma$", color=P[2]); ax2.tick_params(axis="y", colors=P[2])
    ax2.grid(False)
    ax1.axvline(0.452, ls="--", color=P[3], lw=1.6)
    ax1.text(0.452, cfg.COEFFS["N_crit"] + 1.2, " transition onset", color=P[3], fontsize=9)
    ax1.set_title("USTC transition prediction — N-factor & intermittency")
    fig.legend(loc="upper left", bbox_to_anchor=(0.12, 0.88))
    return ps.finish(fig, add("10_transition.png", "Transition prediction",
        "The shock-bypass source drives N across N_crit at the interaction, "
        "setting the intermittency ramp 0→1 (shock-induced transition)."))


def fig_edge_conditions():
    d = _sd()
    fig, ax1 = plt.subplots(figsize=(9.2, 5.2))
    ax1.plot(d.x_m, d.M_edge, color=P[0], lw=2.8, label="edge Mach $M_e$")
    ax1.set_xlabel("axial distance  x  [m]"); ax1.set_ylabel("edge Mach  $M_e$", color=P[0])
    ax1.tick_params(axis="y", colors=P[0])
    ax2 = ax1.twinx()
    ax2.plot(d.x_m, d.T_edge_K, color=P[1], lw=2.6, ls="--", label="edge temp $T_e$")
    ax2.set_ylabel("edge temperature  $T_e$  [K]", color=P[1]); ax2.tick_params(axis="y", colors=P[1])
    ax2.grid(False)
    ax1.set_title("Boundary-layer edge conditions across the interaction")
    lines = ax1.get_lines() + ax2.get_lines()
    ax1.legend(lines, [l.get_label() for l in lines], loc="center left")
    return ps.finish(fig, add("11_edge_conditions.png", "Edge conditions",
        "Edge Mach drops 4.0→2.74 and edge temperature rises across the "
        "two-shock compression."))


def fig_cp():
    d = _sd()
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    ax.plot(d.x_m, d.Cp, color=P[7], lw=2.8)
    _mark_interaction(ax)
    ax.set_xlabel("axial distance  x  [m]"); ax.set_ylabel("pressure coefficient  $C_p$")
    ax.set_title("Wall pressure coefficient")
    return ps.finish(fig, add("12_cp.png", "Pressure coefficient",
        "Surface Cp signature of the SWBLI."))


def fig_dashboard():
    d = _sd()
    fig, ax = plt.subplots(2, 3, figsize=(13.5, 7.4))
    series = [("p_wall_over_pinf", "$p_w/p_\\infty$", P[0]),
              ("Cf", "$C_f$", P[1]),
              ("St", "Stanton $St$", P[3]),
              ("delta_mm", "$\\delta$ [mm]", P[2]),
              ("H_i", "shape factor $H_i$", P[5]),
              ("N_factor", "amplification $N$", P[6])]
    for a, (col, lab, c) in zip(ax.ravel(), series):
        a.plot(d.x_m, d[col], color=c, lw=2.3)
        a.axvspan(0.458, 0.598, color=P[4], alpha=0.10, lw=0)
        a.axvline(0.452, ls="--", color=P[2], lw=1.0)
        a.set_xlabel("x [m]"); a.set_ylabel(lab)
        if col == "Cf":
            a.axhline(0, color=P[6], lw=1.0, ls=":")
    fig.suptitle("Surface-solution dashboard — Mach-4 intake SWBLI",
                 color=INK, fontweight="bold")
    return ps.finish(fig, add("13_dashboard.png", "Surface dashboard",
        "Overview of all surface predictions used for the design decision."))


def fig_re_theta():
    ibl = pd.read_csv(os.path.join(cfg.DIR_SOL, "integral_boundary_layer.csv"))
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    ax.plot(ibl.x_m, ibl.Re_theta, color=P[0], lw=2.8)
    _mark_interaction(ax, show_labels=False)
    ax.set_xlabel("axial distance  x  [m]"); ax.set_ylabel("momentum-thickness Reynolds  $Re_\\theta$")
    ax.set_title("Momentum-thickness Reynolds number")
    return ps.finish(fig, add("14_re_theta.png", "Re_theta",
        "Re_θ used by the transition correlation; jumps through the interaction."))


# ======================================================================
# 5. BOUNDARY-LAYER & TEMPERATURE PROFILES
# ======================================================================
def fig_velocity_profiles():
    bl = pd.read_csv(os.path.join(cfg.DIR_SOL, "boundary_layer_profiles.csv"))
    fig, ax = plt.subplots(figsize=(7.6, 6.2))
    colors = {"upstream_laminar": P[0], "separation_bubble": P[1],
              "reattached_turbulent": P[2]}
    labels = {"upstream_laminar": "x=0.20 m (laminar)",
              "separation_bubble": "x=0.515 m (separated)",
              "reattached_turbulent": "x=0.75 m (turbulent)"}
    for st, gdf in bl.groupby("station"):
        ax.plot(gdf.u_over_Ue, gdf.y_mm, "o-", ms=3, color=colors[st], label=labels[st])
    ax.axvline(0, color=P[6], lw=1.2, ls=":")
    ax.set_xlabel("velocity ratio  $u/U_e$"); ax.set_ylabel("wall distance  y  [mm]")
    ax.set_title("Boundary-layer velocity profiles")
    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    return ps.finish(fig, add("15_velocity_profiles.png", "Velocity profiles",
        "Laminar, separated (reversed near-wall flow, u<0) and reattached "
        "turbulent velocity profiles."))


def fig_temperature_profiles():
    bl = pd.read_csv(os.path.join(cfg.DIR_SOL, "boundary_layer_profiles.csv"))
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    colors = {"upstream_laminar": P[0], "separation_bubble": P[1],
              "reattached_turbulent": P[2]}
    labels = {"upstream_laminar": "x=0.20 m (laminar)",
              "separation_bubble": "x=0.515 m (separated)",
              "reattached_turbulent": "x=0.75 m (turbulent)"}
    for st, gdf in bl.groupby("station"):
        ax[0].plot(gdf.T_over_Te, gdf.y_mm, "o-", ms=3, color=colors[st], label=labels[st])
        ax[1].plot(gdf.T_K, gdf.y_mm, "o-", ms=3, color=colors[st], label=labels[st])
    ax[0].set_xlabel("temperature ratio  $T/T_e$"); ax[0].set_ylabel("wall distance  y  [mm]")
    ax[0].set_title("Normalised temperature profile"); ax[0].legend(loc="upper right")
    ax[1].axvline(cfg.T_wall, ls="--", color=P[1], lw=1.4, label=f"$T_w$={cfg.T_wall:.0f} K")
    ax[1].set_xlabel("static temperature  T  [K]"); ax[1].set_ylabel("wall distance  y  [mm]")
    ax[1].set_title("Static temperature profile"); ax[1].legend(loc="upper right")
    fig.suptitle("Boundary-layer temperature profiles (Crocco–Busemann)",
                 color=INK, fontweight="bold")
    return ps.finish(fig, add("16_temperature_profiles.png", "Temperature profiles",
        "Near-wall viscous heating peak (T→T_aw) with the cooled-wall "
        "condition T_w=470 K; the design heat-load driver."))


# ======================================================================
# 6. 2-D CONTOURS & VECTORS
# ======================================================================
def _load_field():
    f = np.load(os.path.join(cfg.DIR_SOL, "flow_field_2D.npz"))
    return f


def _shock_lines(ax):
    H = cfg.DUCT_HEIGHT; xi = cfg.X_IMPINGE
    bi, br = np.radians(cfg.beta_inc), np.radians(cfg.beta_ref)
    ax.plot([xi - H / np.tan(bi), xi], [H, 0], color="white", lw=1.6, ls="--", alpha=0.9)
    ax.plot([xi, xi + H / np.tan(br)], [0, H], color="white", lw=1.6, ls="--", alpha=0.9)


def fig_pressure_contour():
    f = _load_field()
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    cs = ax.contourf(f["XX"], f["YY"], f["P"] / 1e3, levels=40, cmap=ps.SEQ_CMAP)
    _shock_lines(ax)
    cb = fig.colorbar(cs, ax=ax, pad=0.02); cb.set_label("static pressure [kPa]")
    ax.plot(f["x"], f["delta"], color="white", lw=1.4, alpha=0.7)
    ax.set_xlabel("x  [m]"); ax.set_ylabel("y  [m]")
    ax.set_title("Static-pressure contour — incident/reflected shock system")
    return ps.finish(fig, add("17_pressure_contour.png", "Pressure contour",
        "2-D static-pressure field; dashed lines = shocks, solid = BL edge."))


def fig_temperature_contour():
    f = _load_field()
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    cs = ax.contourf(f["XX"], f["YY"], f["T"], levels=40, cmap=ps.TEMP_CMAP)
    _shock_lines(ax)
    cb = fig.colorbar(cs, ax=ax, pad=0.02); cb.set_label("static temperature [K]")
    ax.set_xlabel("x  [m]"); ax.set_ylabel("y  [m]")
    ax.set_title("Static-temperature contour — hot near-wall boundary layer")
    return ps.finish(fig, add("18_temperature_contour.png", "Temperature contour",
        "Temperature field showing the hot viscous boundary layer and the "
        "post-shock temperature rise."))


def fig_mach_contour():
    f = _load_field()
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    cs = ax.contourf(f["XX"], f["YY"], f["M"], levels=40, cmap=ps.MACH_CMAP)
    _shock_lines(ax)
    cb = fig.colorbar(cs, ax=ax, pad=0.02); cb.set_label("Mach number")
    ax.set_xlabel("x  [m]"); ax.set_ylabel("y  [m]")
    ax.set_title("Mach-number contour")
    return ps.finish(fig, add("19_mach_contour.png", "Mach contour",
        "Mach field: deceleration 4.0→2.74 through the two-shock compression; "
        "low-momentum boundary layer at the wall."))


def fig_velocity_vectors():
    f = _load_field()
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    mag = np.sqrt(f["U"] ** 2 + f["V"] ** 2)
    cs = ax.contourf(f["XX"], f["YY"], mag, levels=40, cmap=ps.MACH_CMAP, alpha=0.85)
    s = (slice(None, None, 6), slice(None, None, 9))
    ax.quiver(f["XX"][s], f["YY"][s], f["U"][s], f["V"][s],
              color="white", scale=26000, width=0.0022, alpha=0.9)
    _shock_lines(ax)
    cb = fig.colorbar(cs, ax=ax, pad=0.02); cb.set_label("velocity magnitude [m/s]")
    ax.set_xlabel("x  [m]"); ax.set_ylabel("y  [m]")
    ax.set_title("Velocity vector field — flow turning across the shock system")
    return ps.finish(fig, add("20_velocity_vectors.png", "Velocity vectors",
        "Velocity vectors over the speed field; flow turns toward the wall "
        "behind the incident shock and realigns behind the reflected shock."))


# ======================================================================
# 7. 3-D CONTOURS & VECTORS
# ======================================================================
def fig_3d_wall_pressure():
    d = _sd()
    z = np.linspace(0, cfg.PLATE_SPAN, 40)
    Xg, Zg = np.meshgrid(d.x_m.values, z)
    Pg = np.tile(d.p_wall_over_pinf.values, (z.size, 1))
    fig = plt.figure(figsize=(10, 6.6))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(Xg, Zg, Pg, cmap=ps.SEQ_CMAP, linewidth=0,
                           antialiased=True, rcount=40, ccount=60)
    fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.08, label="$p_w/p_\\infty$")
    ax.set_xlabel("x [m]"); ax.set_ylabel("span z [m]"); ax.set_zlabel("$p_w/p_\\infty$")
    ax.set_title("3-D wall-pressure surface (spanwise ridge at interaction)")
    ax.view_init(elev=28, azim=-122)
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.label.set_color(INK)
    return ps.finish(fig, add("21_3d_wall_pressure.png", "3-D wall pressure",
        "Spanwise-extruded wall-pressure surface; the ridge marks the "
        "reattachment compression."))


def fig_3d_pressure_field():
    f = _load_field()
    fig = plt.figure(figsize=(10, 6.6))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(f["XX"], f["YY"], f["P"] / 1e3, cmap=ps.SEQ_CMAP,
                           linewidth=0, antialiased=True, rcount=60, ccount=80)
    fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.08, label="p [kPa]")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_zlabel("p [kPa]")
    ax.set_title("3-D static-pressure field (shock surfaces)")
    ax.view_init(elev=32, azim=-120)
    return ps.finish(fig, add("22_3d_pressure_field.png", "3-D pressure field",
        "Pressure as a height field reveals the incident & reflected shock "
        "fronts as steep ramps."))


def fig_3d_temperature_field():
    f = _load_field()
    fig = plt.figure(figsize=(10, 6.6))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(f["XX"], f["YY"], f["T"], cmap=ps.TEMP_CMAP,
                           linewidth=0, antialiased=True, rcount=60, ccount=80)
    fig.colorbar(surf, ax=ax, shrink=0.6, pad=0.08, label="T [K]")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]"); ax.set_zlabel("T [K]")
    ax.set_title("3-D static-temperature field (hot boundary layer)")
    ax.view_init(elev=30, azim=-130)
    return ps.finish(fig, add("23_3d_temperature_field.png", "3-D temperature field",
        "Temperature height field: hot near-wall layer ridge plus post-shock "
        "temperature steps."))


def fig_3d_vectors():
    f = _load_field()
    sx = slice(2, None, 20); sy = slice(2, None, 12)
    Xp = f["XX"][sy, sx]; Yp = f["YY"][sy, sx]
    Up = f["U"][sy, sx]; Vp = f["V"][sy, sx]
    fig = plt.figure(figsize=(11.5, 7.6))
    ax = fig.add_subplot(111, projection="3d")
    planes = np.linspace(0, cfg.PLATE_SPAN, 3)
    pcols = [P[0], P[2], P[1]]
    for zc, c in zip(planes, pcols):
        Z = np.full_like(Xp, zc)
        ax.quiver(Xp, Z, Yp, Up, np.zeros_like(Up), Vp,
                  length=0.055, normalize=True, linewidth=1.3,
                  arrow_length_ratio=0.4, color=c, label=f"span z = {zc:.2f} m")
    # draw the wall planes faintly
    ax.set_xlabel("x  [m]", labelpad=10); ax.set_ylabel("span z  [m]", labelpad=10)
    ax.set_zlabel("y  [m]", labelpad=8)
    ax.set_title("3-D velocity vector field across spanwise planes")
    ax.set_box_aspect((2.2, 1.0, 0.6))
    ax.view_init(elev=18, azim=-66)
    ax.legend(loc="upper left")
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((1, 1, 1, 0.0))
        axis.pane.set_edgecolor(ps.GRIDC)
    return ps.finish(fig, add("24_3d_vectors.png", "3-D velocity vectors",
        "Velocity vectors on three spanwise planes showing the shock-"
        "induced flow deflection and near-wall retardation."))


# ======================================================================
# 8. VALIDATION
# ======================================================================
# Validation figures are owned by the validation stage (06_validation/
# validate.py -> 06_validation/figures/ + figure_manifest.csv) to keep a
# single source of truth. They are embedded in the report from cfg.DIR_VALF.
# ======================================================================
def fig_intake_perf():
    d = pd.read_csv(os.path.join(cfg.DIR_SOL, "intake_performance.csv"))
    sel = d[d["quantity"].isin([
        "total_pressure_recovery_inviscid", "total_pressure_recovery_actual",
        "MIL-E-5008B_reference_recovery", "kinetic_energy_efficiency",
        "mass_capture_ratio"])]
    fig, ax = plt.subplots(figsize=(9.8, 5.0))
    labels = ["recovery\n(inviscid)", "recovery\n(actual)", "MIL-E-5008B\nref",
              "KE\nefficiency", "mass\ncapture"]
    ax.bar(labels, sel.value.values, color=P[:5], alpha=0.9)
    for i, v in enumerate(sel.value.values):
        ax.text(i, v + 0.01, f"{v:.3f}", ha="center", color=INK, fontsize=10)
    ax.set_ylim(0, 1.08); ax.set_ylabel("value")
    ax.set_title("Predicted supersonic-intake performance")
    return ps.finish(fig, add("29_intake_performance.png", "Intake performance",
        "Predicted total-pressure recovery, KE efficiency and mass capture, "
        "with the MIL-E-5008B reference."))


def fig_aerothermal():
    d = pd.read_csv(os.path.join(cfg.DIR_SOL, "surface_distributions.csv"))
    fig, ax = plt.subplots(figsize=(9.6, 5.0))
    ax.fill_between(d.x_m, d.q_wall_W_m2 / 1e3, color=P[1], alpha=0.25)
    ax.plot(d.x_m, d.q_wall_W_m2 / 1e3, color=P[1], lw=2.6)
    ax.axvline(0.598, ls="--", color=P[2], lw=1.4)
    ax.annotate("design heat-load peak", (0.598, (d.q_wall_W_m2/1e3).max()),
                (0.66, (d.q_wall_W_m2/1e3).max()*0.85), color=INK, fontsize=9,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_xlabel("axial distance  x  [m]"); ax.set_ylabel("wall heat flux  $q_w$  [kW/m$^2$]")
    ax.set_title("Aerothermal load distribution (cowl structure design input)")
    return ps.finish(fig, add("30_aerothermal.png", "Aerothermal load",
        "Wall heat-flux distribution; the reattachment peak sizes the thermal-"
        "protection / cooling requirement."))


# ----------------------------------------------------------------------
# Result-table export  ->  05_postprocessing/tables/  (+ table_manifest)
# Mirrors the figure workflow: gathers the canonical result tables from
# every stage into one self-contained deliverable consumed by the report.
# ----------------------------------------------------------------------
TABLES = [
    # (out_name,                stage_dir,   source_csv,                       title)
    ("T01_freestream.csv",          cfg.DIR_SET,  "freestream_conditions.csv",       "Freestream conditions (Mach 4, 20 km ISA)"),
    ("T02_geometry.csv",            cfg.DIR_GEOM, "geometry_parameters.csv",         "Case geometry parameters"),
    ("T03_mesh_quality.csv",        cfg.DIR_MESH, "mesh_quality_metrics.csv",        "Mesh quality metrics"),
    ("T04_grid_independence.csv",   cfg.DIR_MESH, "grid_independence_study.csv",     "Grid-independence study"),
    ("T05_boundary_conditions.csv", cfg.DIR_SET,  "boundary_conditions.csv",         "Boundary conditions"),
    ("T06_solver_numerics.csv",     cfg.DIR_SET,  "solver_numerics.csv",             "Solver numerics"),
    ("T07_material_properties.csv", cfg.DIR_SET,  "material_properties.csv",         "Material properties"),
    ("T08_calibration.csv",         cfg.DIR_SET,  "calibration_coefficients.csv",    "ML regime-calibrated coefficients"),
    ("T09_prediction_summary.csv",  cfg.DIR_SOL,  "prediction_summary.csv",          "Prediction summary"),
    ("T10_interaction_metrics.csv", cfg.DIR_SOL,  "interaction_metrics.csv",         "SWBLI interaction metrics"),
    ("T11_aerothermal_loads.csv",   cfg.DIR_SOL,  "aerothermal_loads.csv",           "Aerothermal loads"),
    ("T12_intake_performance.csv",  cfg.DIR_SOL,  "intake_performance.csv",          "Supersonic-intake performance"),
    ("T13_force_coefficients.csv",  cfg.DIR_SOL,  "forces_coefficients.csv",         "Force coefficients"),
    ("T14_spanwise.csv",            os.path.join(cfg.DIR_POST, "..", "07_3D_solution"),
                                                  "spanwise_distributions.csv",      "3-D spanwise distributions"),
    ("T15_validation_metrics.csv",  cfg.DIR_VAL,  "validation_metrics.csv",          "Validation error metrics"),
    ("T16_transition_reynolds.csv", cfg.DIR_VAL,  "transition_reynolds_comparison.csv", "Transition-Reynolds comparison"),
]


def tables():
    os.makedirs(cfg.DIR_TAB, exist_ok=True)
    rows = []
    for out_name, stage, src, title in TABLES:
        src_path = os.path.join(stage, src)
        if not os.path.exists(src_path):
            print("  [WARN] missing table source:", src_path)
            continue
        df = pd.read_csv(src_path)
        df.to_csv(os.path.join(cfg.DIR_TAB, out_name), index=False)
        rows.append([out_name, title, os.path.basename(os.path.normpath(stage)),
                     src, df.shape[0], df.shape[1]])
        print("  table:", out_name)
    man = pd.DataFrame(rows, columns=["filename", "title", "source_stage",
                                      "source_file", "n_rows", "n_cols"])
    man.to_csv(os.path.join(cfg.DIR_TAB, "table_manifest.csv"), index=False)
    print(f"[05-postprocessing] wrote {len(rows)} tables + table_manifest.csv "
          f"to {cfg.DIR_TAB}")
    return man


def run():
    os.makedirs(cfg.DIR_FIG, exist_ok=True)
    funcs = [fig_geometry, fig_mesh, fig_convergence, fig_grid_independence,
             fig_wall_pressure, fig_skin_friction, fig_heat_transfer,
             fig_bl_thickness, fig_shape_factor, fig_transition,
             fig_edge_conditions, fig_cp, fig_dashboard, fig_re_theta,
             fig_velocity_profiles, fig_temperature_profiles,
             fig_pressure_contour, fig_temperature_contour, fig_mach_contour,
             fig_velocity_vectors, fig_3d_wall_pressure, fig_3d_pressure_field,
             fig_3d_temperature_field, fig_3d_vectors,
             fig_intake_perf, fig_aerothermal]
    for fn in funcs:
        p = fn()
        print("  figure:", os.path.basename(p))
    man = pd.DataFrame(MAN, columns=["filename", "title", "caption"])
    man.to_csv(os.path.join(cfg.DIR_POST, "figure_manifest.csv"), index=False)
    print(f"[05-postprocessing] wrote {len(MAN)} figures + figure_manifest.csv")
    tables()
    return man


if __name__ == "__main__":
    run()
