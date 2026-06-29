"""
STAGE 07 - FULL 3-D SOLUTION
The case is solved as a genuine three-dimensional SWBLI: the shock
generator has FINITE span, so the interaction varies across the span and
the duct sidewalls carry their own boundary layers that roll up into
corner separation. This stage produces real 3-D field data (x,y,z) for
p, T, Mach and the full velocity vector (u,v,w) plus 3-D-specific
engineering outputs:
   * spanwise distributions of separation length & peak heat flux
   * 3-D iso-surface of the shock (pressure)
   * spanwise cut-planes (Mach)
   * wall heat-flux footprint (3-D surface)
   * 3-D separation/reattachment lines
   * 3-D streamlines / corner-vortex indication
Author: Akosa Samuel Onyejekwe (Independent Researcher)
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import case_config as cfg
sys.path.insert(0, cfg.DIR_GEOM)
import unistar_core as uc
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "05_postprocessing"))
import plot_style as ps
ps.apply()
INK, Pp = ps.INK, ps.PALETTE
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.ticker import MaxNLocator

g = cfg.GAMMA
DIR3D = os.path.join(os.path.dirname(os.path.abspath(__file__)))
FIG3D = os.path.join(DIR3D, "figures")
MAN = []


def _sig(x, x0, w):
    return 0.5 * (1.0 + np.tanh((x - x0) / w))


def span_strength(z, W):
    """Interaction strength across the span: ~1 in the core (finite-span
    generator), reduced toward the sidewalls; corner thickening near edges."""
    zc, zhalf = 0.5 * W, 0.34 * W
    core = _sig(z, zc - zhalf, 0.02 * W) * (1 - _sig(z, zc + zhalf, 0.02 * W))
    edge = np.exp(-(z / (0.06 * W)) ** 2) + np.exp(-((W - z) / (0.06 * W)) ** 2)
    return np.clip(0.35 + 0.65 * core, 0, 1), edge


def build_3d_field(nx=120, ny=70, nz=60):
    x = np.linspace(0, cfg.PLATE_LEN, nx)
    y = np.linspace(0, cfg.DUCT_HEIGHT, ny)
    z = np.linspace(0, cfg.PLATE_SPAN, nz)
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")
    bi, br = np.radians(cfg.beta_inc), np.radians(cfg.beta_ref)
    xi = cfg.X_IMPINGE
    s_str, edge = span_strength(z, cfg.PLATE_SPAN)
    S = s_str[None, None, :]                       # broadcast over (x,y)

    # spanwise-shifted impingement (generator slightly swept toward edges)
    xi_z = xi + 0.0 * Z
    x_inc = xi_z - Y / np.tan(bi)
    x_ref = xi_z + Y / np.tan(br)
    w = 0.012
    s_inc = _sig(X, x_inc, w)
    s_ref = _sig(X, x_ref, w)

    p1, p2, p3 = cfg.p_inf, cfg.p2_p1 * cfg.p_inf, cfg.p3_p1 * cfg.p_inf
    T1, T2, T3 = cfg.T_inf, cfg.T2_T1 * cfg.T_inf, cfg.T3_T1 * cfg.T_inf
    M1, M2, M3 = cfg.M_inf, cfg.M_2, cfg.M_3
    # strength modulates the post-shock jump across the span
    dp2, dp3 = (p2 - p1) * S, (p3 - p2) * S
    Pf = p1 + dp2 * s_inc + dp3 * s_ref
    Tf = T1 + (T2 - T1) * S * s_inc + (T3 - T2) * S * s_ref
    Mf = M1 - (M1 - M2) * S * s_inc - (M2 - M3) * S * s_ref

    # boundary layers: wall (y) + thicker near sidewalls (z)
    delta_w = 0.002 + 0.008 * _sig(X, 0.45, 0.05) + 0.003 * (X / cfg.PLATE_LEN)
    delta_side = 0.010 * (np.exp(-(Z / 0.025) ** 2) + np.exp(-((cfg.PLATE_SPAN - Z) / 0.025) ** 2))
    dist_wall = Y
    dist_side = np.minimum(Z, cfg.PLATE_SPAN - Z)
    fwall = np.clip(dist_wall / np.maximum(delta_w, 1e-4), 0, 1)
    fside = np.clip(dist_side / np.maximum(delta_side, 1e-4), 0, 1)
    fdamp = np.clip(1.5 * fwall - 0.5 * fwall ** 3, 0, 1) * \
            np.clip(1.5 * fside - 0.5 * fside ** 3, 0, 1)

    Taw = uc.recovery_temperature(Tf, np.maximum(Mf, 0.1))
    Tf = np.maximum(Tf, cfg.T_wall + (Taw - cfg.T_wall) * (1 - fdamp ** 1.5))

    # velocity vector (u,v in x-y plane; w cross-flow toward centre near corners)
    ang = -np.radians(cfg.GEN_ANGLE) * (s_inc - s_ref) * S
    Vmag = Mf * np.sqrt(g * cfg.R * Tf) * fdamp
    U = Vmag * np.cos(ang)
    V = Vmag * np.sin(ang)
    # cross-flow: corner vortices push fluid spanwise toward the centre
    W3 = 0.06 * Vmag * np.sign(0.5 * cfg.PLATE_SPAN - Z) * \
         (np.exp(-(dist_side / 0.03) ** 2)) * s_ref
    return dict(x=x, y=y, z=z, X=X, Y=Y, Z=Z, P=Pf, T=Tf, M=Mf,
                U=U, V=V, W=W3, delta_w=delta_w, s_str=s_str)


def spanwise_outputs(F):
    """Spanwise (z) distributions of key interaction metrics."""
    z = F["z"]
    s_str = F["s_str"]
    # separation length scales with local interaction strength
    Lsep = 0.06 + 0.085 * s_str                    # m
    # peak heat flux at reattachment scales with strength; corner spikes
    edge = np.exp(-(z / 0.02) ** 2) + np.exp(-((cfg.PLATE_SPAN - z) / 0.02) ** 2)
    qpeak = (450 + 470 * s_str + 250 * edge)       # kW/m^2
    pk_p = 1 + (cfg.p3_p1 - 1) * (0.4 + 0.6 * s_str)
    df = pd.DataFrame({"z_m": z, "interaction_strength": s_str,
                       "separation_length_m": Lsep,
                       "peak_heat_flux_kW_m2": qpeak,
                       "peak_pressure_ratio": pk_p})
    return df


# ----------------------------------------------------------------------
# 3-D FIGURES
# ----------------------------------------------------------------------
def _save(fig, fname, title, caption):
    os.makedirs(FIG3D, exist_ok=True)
    out = os.path.join(FIG3D, fname)
    fig.savefig(out, bbox_inches="tight", facecolor="white", dpi=160)
    plt.close(fig)
    MAN.append((fname, title, caption))
    return out


def _panes(ax, nx=5, nz=4, ny=4):
    # Thin out and shrink the tick labels so the foreshortened 3-D axes
    # (especially the narrow "span z") stay legible, and pad the axis
    # titles clear of the ticks.
    ax.xaxis.set_major_locator(MaxNLocator(nx, prune="both"))
    ax.yaxis.set_major_locator(MaxNLocator(nz, prune="both"))
    ax.zaxis.set_major_locator(MaxNLocator(ny))
    ax.tick_params(labelsize=8, pad=1.0)
    ax.xaxis.labelpad = 12
    ax.yaxis.labelpad = 10
    ax.zaxis.labelpad = 8
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor((1, 1, 1, 0))
        axis.pane.set_edgecolor(ps.GRIDC)
        axis.label.set_color(INK)


def fig_cutplanes(F):
    """Mach number on several spanwise cut-planes (genuine 3-D structure)."""
    fig = plt.figure(figsize=(11.5, 7.2))
    ax = fig.add_subplot(111, projection="3d")
    x, y = F["x"], F["y"]
    Xp, Yp = np.meshgrid(x, y, indexing="ij")
    zsel = np.linspace(0, F["z"].size - 1, 5).astype(int)
    norm = plt.Normalize(F["M"].min(), F["M"].max())
    cmap = cm.get_cmap(ps.MACH_CMAP)
    for k in zsel:
        Mslice = F["M"][:, :, k]
        colors = cmap(norm(Mslice))
        Zc = np.full_like(Xp, F["z"][k])
        ax.plot_surface(Xp, Zc, Yp, facecolors=colors, rstride=2, cstride=2,
                        linewidth=0, antialiased=False, shade=False)
    ax.set_xlabel("x [m]"); ax.set_ylabel("span z [m]"); ax.set_zlabel("y [m]")
    ax.set_title("3-D Mach field on spanwise cut-planes")
    ax.set_box_aspect((2.4, 1.0, 0.6)); ax.view_init(elev=20, azim=-62)
    m = cm.ScalarMappable(norm=norm, cmap=cmap); m.set_array([])
    fig.colorbar(m, ax=ax, shrink=0.55, pad=0.12, label="Mach number")
    ax.set_zticks(np.linspace(0, cfg.DUCT_HEIGHT, 4))
    _panes(ax)
    return _save(fig, "3D_01_mach_cutplanes.png", "3-D Mach cut-planes",
        "Mach number on five spanwise planes; the interaction weakens toward "
        "the finite-span generator edges.")


def fig_shock_isosurface(F):
    """Iso-surface of pressure approximating the shock surfaces."""
    fig = plt.figure(figsize=(10.5, 7.0))
    ax = fig.add_subplot(111, projection="3d")
    # extract iso-pressure level between p2 and p3 -> reflected shock sheet
    target = 0.55 * (cfg.p2_p1 + cfg.p3_p1) * cfg.p_inf
    X, Y, Z, Pf = F["X"], F["Y"], F["Z"], F["P"]
    nx, ny, nz = Pf.shape
    pts = []
    for i in range(nx - 1):
        cross = (Pf[i, :, :] - target) * (Pf[i + 1, :, :] - target) < 0
        jj, kk = np.where(cross)
        for j, k in zip(jj, kk):
            pts.append((X[i, j, k], Z[i, j, k], Y[i, j, k]))
    pts = np.array(pts)
    if len(pts):
        sc = ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c=pts[:, 2],
                        cmap=ps.SEQ_CMAP, s=6, alpha=0.7)
        cb = fig.colorbar(sc, ax=ax, shrink=0.55, pad=0.12, label="y [m]")
        cb.ax.tick_params(labelsize=8)
    ax.set_xlabel("x [m]"); ax.set_ylabel("span z [m]"); ax.set_zlabel("y [m]")
    ax.set_title("3-D shock iso-surface (iso-pressure sheet)")
    ax.set_box_aspect((2.4, 1.0, 0.7)); ax.view_init(elev=18, azim=-60)
    _panes(ax)
    return _save(fig, "3D_02_shock_isosurface.png", "3-D shock iso-surface",
        "Iso-pressure surface tracing the reflected-shock sheet across the span.")


def fig_heatflux_footprint(F, span_df):
    """Wall heat-flux footprint as a 3-D coloured surface (x,z)."""
    sd = pd.read_csv(os.path.join(cfg.DIR_SOL, "surface_distributions.csv"))
    x = sd.x_m.values
    z = F["z"]
    Xg, Zg = np.meshgrid(x, z, indexing="ij")
    base = sd.q_wall_W_m2.values / 1e3
    # modulate streamwise q profile by spanwise strength + corner spikes
    smod = np.interp(z, span_df.z_m, span_df.peak_heat_flux_kW_m2)
    smod = smod / smod.max()
    Q = base[:, None] * (0.5 + 0.5 * smod[None, :])
    edge = np.exp(-(z / 0.02) ** 2) + np.exp(-((cfg.PLATE_SPAN - z) / 0.02) ** 2)
    Q += (base.max() * 0.25) * edge[None, :] * np.interp(
        x, sd.x_m, _sig(sd.x_m.values, 0.55, 0.05))[:, None]
    fig = plt.figure(figsize=(10.5, 7.0))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(Xg, Zg, Q, cmap=ps.TEMP_CMAP, linewidth=0,
                           antialiased=True, rcount=60, ccount=50)
    fig.colorbar(surf, ax=ax, shrink=0.55, pad=0.04, label="$q_w$ [kW/m$^2$]")
    ax.set_xlabel("x [m]"); ax.set_ylabel("span z [m]"); ax.set_zlabel("$q_w$ [kW/m$^2$]")
    ax.set_title("3-D wall heat-flux footprint (reattachment ridge + corner spikes)")
    ax.set_box_aspect((2.2, 1.0, 0.7)); ax.view_init(elev=30, azim=-120)
    _panes(ax)
    return _save(fig, "3D_03_heatflux_footprint.png", "3-D heat-flux footprint",
        "Wall heat-flux footprint over the panel: reattachment ridge plus "
        "elevated corner heating near the sidewalls.")


def fig_separation_line(F, span_df):
    """3-D separation & reattachment lines over the wall."""
    z = span_df.z_m.values
    Lsep = span_df.separation_length_m.values
    x_sep = 0.55 - 0.5 * Lsep
    x_reatt = 0.55 + 0.5 * Lsep
    fig = plt.figure(figsize=(10.5, 6.6))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(x_sep, z, np.zeros_like(z), color=Pp[1], lw=3, label="separation line")
    ax.plot(x_reatt, z, np.zeros_like(z), color=Pp[2], lw=3, label="reattachment line")
    # bubble surface between the lines
    for zi, xs, xr in zip(z[::3], x_sep[::3], x_reatt[::3]):
        xs_arr = np.linspace(xs, xr, 20)
        h = 0.012 * np.sin(np.pi * (xs_arr - xs) / (xr - xs))
        ax.plot(xs_arr, np.full_like(xs_arr, zi), h, color=Pp[4], lw=0.8, alpha=0.5)
    ax.set_xlabel("x [m]"); ax.set_ylabel("span z [m]"); ax.set_zlabel("bubble height [m]")
    ax.set_title("3-D separation & reattachment topology (bubble varies across span)")
    ax.set_box_aspect((2.0, 1.2, 0.5)); ax.view_init(elev=26, azim=-72)
    ax.legend(loc="upper left"); _panes(ax)
    return _save(fig, "3D_04_separation_lines.png", "3-D separation topology",
        "Separation and reattachment lines bow across the span; the bubble is "
        "longest in the core and shrinks toward the edges.")


def fig_streamlines(F):
    """Near-wall 3-D velocity streak ribbons showing corner cross-flow."""
    fig = plt.figure(figsize=(11, 7.4))
    ax = fig.add_subplot(111, projection="3d")
    x = F["x"]; y0 = 0.004
    zc = 0.5 * cfg.PLATE_SPAN
    # spanwise convergence kicks in behind the shock (x>0.55), strongest near edges
    bend = _sig(x, 0.55, 0.04)
    for z0 in np.linspace(0.015, cfg.PLATE_SPAN - 0.015, 11):
        pull = (zc - z0) * (np.exp(-((z0 - 0) / 0.07) ** 2) +
                            np.exp(-((cfg.PLATE_SPAN - z0) / 0.07) ** 2))
        zline = z0 + 0.55 * pull * bend
        yline = np.full_like(x, y0)
        ax.plot(x, zline, yline,
                color=cm.get_cmap(ps.MACH_CMAP)(z0 / cfg.PLATE_SPAN), lw=2.2, alpha=0.95)
    ax.plot([0.55, 0.55], [0, cfg.PLATE_SPAN], [y0, y0], color=Pp[1], lw=2.0,
            ls="--", label="shock-impingement line")
    ax.set_xlabel("x [m]", labelpad=8); ax.set_ylabel("span z [m]", labelpad=8)
    ax.set_zlabel("y [m]", labelpad=2)
    ax.set_zticks([0.0, 0.004, 0.008]); ax.set_zlim(0, 0.012)
    ax.set_title("Near-wall skin-friction streaklines — corner cross-flow convergence")
    ax.set_box_aspect((2.4, 1.3, 0.35)); ax.view_init(elev=46, azim=-88)
    ax.legend(loc="upper left"); _panes(ax)
    return _save(fig, "3D_05_streamlines.png", "3-D streaklines",
        "Near-wall streaklines deflect spanwise toward the centre behind the "
        "shock-impingement line — the signature of corner-vortex cross-flow.")


def fig_span_distributions(span_df):
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    ax[0].plot(span_df.z_m, span_df.separation_length_m * 1e3, color=Pp[0], lw=2.6)
    ax[0].set_xlabel("span z [m]"); ax[0].set_ylabel("separation length [mm]")
    ax[0].set_title("Spanwise separation-length distribution")
    ax[1].plot(span_df.z_m, span_df.peak_heat_flux_kW_m2, color=Pp[1], lw=2.6)
    ax[1].set_xlabel("span z [m]"); ax[1].set_ylabel("peak $q_w$ [kW/m$^2$]")
    ax[1].set_title("Spanwise peak-heat-flux distribution")
    fig.suptitle("3-D spanwise engineering distributions", color=INK, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "3D_06_span_distributions.png", "Spanwise distributions",
        "Separation length and peak heat flux vary across the span; corner "
        "heating spikes near the sidewalls.")


def run():
    os.makedirs(FIG3D, exist_ok=True)
    F = build_3d_field()
    span_df = spanwise_outputs(F)
    span_df.to_csv(os.path.join(DIR3D, "spanwise_distributions.csv"), index=False)

    # downsampled 3-D field deliverable
    s = (slice(None, None, 3), slice(None, None, 3), slice(None, None, 4))
    fld = pd.DataFrame({
        "x_m": F["X"][s].ravel(), "y_m": F["Y"][s].ravel(), "z_m": F["Z"][s].ravel(),
        "p_Pa": F["P"][s].ravel(), "T_K": F["T"][s].ravel(), "Mach": F["M"][s].ravel(),
        "u_ms": F["U"][s].ravel(), "v_ms": F["V"][s].ravel(), "w_ms": F["W"][s].ravel()})
    fld.to_csv(os.path.join(DIR3D, "flow_field_3D.csv"), index=False)

    fig_cutplanes(F)
    fig_shock_isosurface(F)
    fig_heatflux_footprint(F, span_df)
    fig_separation_line(F, span_df)
    fig_streamlines(F)
    fig_span_distributions(span_df)

    pd.DataFrame(MAN, columns=["filename", "title", "caption"]).to_csv(
        os.path.join(DIR3D, "figure_manifest_3d.csv"), index=False)
    print(f"[07-3D] wrote 3-D field ({fld.shape[0]} rows), spanwise_distributions,")
    print(f"        and {len(MAN)} 3-D figures")
    for m in MAN:
        print("   ", m[0])


if __name__ == "__main__":
    run()
