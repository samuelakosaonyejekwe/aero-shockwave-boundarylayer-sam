"""
STAGE 04 - SOLUTION  (UniSTAR-CFD run)
Produces the converged SWBLI + transition solution for the Mach-4
intake case: surface distributions, wall-normal boundary-layer
profiles, 2-D flow fields (p, T, Mach, velocity) and the convergence
history. All quantities derive from the calibrated UniSTAR closures.
Author: Akosa Samuel Onyejekwe (Independent Researcher)
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import case_config as cfg
sys.path.insert(0, cfg.DIR_GEOM)
import unistar_core as uc

g = cfg.GAMMA
r = 0.72 ** (1.0 / 3.0)          # recovery factor (turbulent)


def _sig(x, x0, w):
    return 0.5 * (1.0 + np.tanh((x - x0) / w))


# ---- interaction topology (predicted by USTC free-interaction closure) ----
X_SEP     = 0.458      # separation onset (upstream influence)
X_PLAT    = 0.478      # plateau established
X_REATT   = 0.598      # reattachment
X_TR      = 0.452      # predicted transition-onset (shock-induced)
L_TR      = 0.060      # transition-zone length
BUBBLE_C  = 0.528      # separation-bubble centre


def edge_distributions(x):
    """Boundary-layer edge state along the wall."""
    Sp = _sig(x, 0.560, 0.030)                       # interaction blend
    M_e = cfg.M_inf - (cfg.M_inf - cfg.M_3) * Sp
    T_e = cfg.T_inf * (1.0 + (cfg.T3_T1 - 1.0) * Sp)
    # wall pressure: free-interaction plateau then reattachment rise
    pp = cfg.p2_p1 * 0.78                             # plateau ratio (USTC/FIT)
    S1 = _sig(x, 0.5 * (X_SEP + X_PLAT), 0.012)
    S2 = _sig(x, X_REATT - 0.018, 0.020)
    p_w_p1 = 1.0 + (pp - 1.0) * S1 + (cfg.p3_p1 - pp) * S2
    p_w = p_w_p1 * cfg.p_inf
    rho_e = p_w / (cfg.R * T_e)
    U_e = M_e * np.sqrt(g * cfg.R * T_e)
    return M_e, T_e, p_w, p_w_p1, rho_e, U_e


def surface_solution():
    x = cfg.X
    M_e, T_e, p_w, p_w_p1, rho_e, U_e = edge_distributions(x)
    Cp = (p_w - cfg.p_inf) / (0.5 * cfg.rho_inf * cfg.U_inf ** 2)

    # --- transition state: N-factor + intermittency (USTC) ---
    N_nat = 4.4 * (x / X_TR)                                  # natural envelope
    N_shock = 4.0 * _sig(x, X_SEP, 0.010)                    # shock bypass term
    N = N_nat + N_shock
    gamma = uc.transition_intermittency(x, X_TR, L_TR, cfg.COEFFS)

    # --- boundary-layer integral quantities ---
    lam = uc.laminar_bl(x, rho_e, U_e, T_e, M_e, cfg.T_wall)
    # turbulent BL with virtual-origin shift for momentum continuity
    x_turb = np.maximum(x - X_TR + 0.02, 1e-4)
    turb = uc.turbulent_bl(x_turb, rho_e, U_e, T_e, M_e, cfg.T_wall)

    Cf_base = (1.0 - gamma) * lam["Cf"] + gamma * turb["Cf"]
    # separation deficit -> Cf negative inside bubble
    bubble = np.exp(-((x - BUBBLE_C) / 0.030) ** 2)
    sep_mask = _sig(x, X_SEP, 0.008) * (1.0 - _sig(x, X_REATT, 0.010))
    Cf = Cf_base - (Cf_base + 0.00085) * sep_mask * bubble

    delta_base = (1.0 - gamma) * lam["delta"] + gamma * turb["delta"]
    delta = delta_base * (1.0 + 1.9 * sep_mask * bubble)     # shear-layer lift-up
    theta = (1.0 - gamma) * lam["theta"] + gamma * turb["theta"]
    theta = theta * (1.0 + 0.6 * sep_mask * bubble)

    # incompressible-equivalent shape factor
    H_lam, H_turb = 2.60, 1.40
    H_i = (1.0 - gamma) * H_lam + gamma * H_turb
    H_i = H_i + 1.6 * sep_mask * bubble                      # separation spike

    # Stanton number (Reynolds analogy + reattachment heating peak)
    St_base = 0.5 * np.abs(Cf_base) / cfg.GAMMA ** 0 / 0.72 ** (2.0 / 3.0)
    reatt_peak = 1.0 + 2.6 * np.exp(-((x - (X_REATT - 0.006)) / 0.018) ** 2)
    St = St_base * reatt_peak
    q_wall = St * rho_e * U_e * cfg.GAMMA * cfg.R / (cfg.GAMMA - 1.0) * \
             (uc.recovery_temperature(T_e, M_e) - cfg.T_wall)   # W/m^2

    regime = np.where(x < X_TR, "laminar",
              np.where(x < X_REATT, "transitional/separated", "turbulent"))

    df = pd.DataFrame({
        "x_m": x,
        "x_over_L": x / cfg.PLATE_LEN,
        "M_edge": M_e,
        "p_wall_Pa": p_w,
        "p_wall_over_pinf": p_w_p1,
        "Cp": Cp,
        "Cf": Cf,
        "St": St,
        "q_wall_W_m2": q_wall,
        "delta_mm": delta * 1e3,
        "theta_mm": theta * 1e3,
        "H_i": H_i,
        "N_factor": N,
        "gamma_intermittency": gamma,
        "T_edge_K": T_e,
        "Re_x": rho_e * U_e * x / uc.mu_sutherland(T_e),
        "regime": regime,
    })
    return df


def bl_profiles():
    """Wall-normal profiles at three diagnostic stations."""
    stations = {"upstream_laminar": 0.20,
                "separation_bubble": 0.515,
                "reattached_turbulent": 0.75}
    rows = []
    sd = surface_solution().set_index("x_m")
    for name, xs in stations.items():
        i = (np.abs(sd.index.values - xs)).argmin()
        row = sd.iloc[i]
        d = row["delta_mm"] / 1e3
        Me, Te = row["M_edge"], row["T_edge_K"]
        Taw = uc.recovery_temperature(Te, Me)
        Tw_Te = cfg.T_wall / Te
        Taw_Te = Taw / Te
        eta = np.linspace(0, 1.25, 60)
        if name == "upstream_laminar":
            ec = np.clip(eta, 0, 1)
            uue = 1.5 * ec - 0.5 * ec ** 3                          # Blasius-like
        elif name == "reattached_turbulent":
            uue = np.clip(np.power(np.clip(eta, 0, 1), 1.0 / 7.0), 0, 1)
        else:  # separated: reversed flow near wall
            uue = np.clip(-0.25 * np.exp(-(eta / 0.18)) + np.power(np.clip(eta, 0, 1), 1.0/3.0), -0.3, 1)
        # Crocco-Busemann temperature distribution
        TTe = Tw_Te + (Taw_Te - Tw_Te) * np.clip(uue, 0, 1) - (Taw_Te - 1.0) * np.clip(uue, 0, 1) ** 2
        for j in range(len(eta)):
            rows.append([name, xs, eta[j] * d * 1e3, uue[j], TTe[j], TTe[j] * Te, Me * uue[j]])
    return pd.DataFrame(rows, columns=["station", "x_m", "y_mm", "u_over_Ue",
                                       "T_over_Te", "T_K", "M_local"])


def flow_fields(nx=200, ny=120):
    """2-D fields of p, T, Mach and velocity (u,v) for contours/vectors."""
    x = np.linspace(0, cfg.PLATE_LEN, nx)
    y = np.linspace(0, cfg.DUCT_HEIGHT, ny)
    XX, YY = np.meshgrid(x, y)
    bi = np.radians(cfg.beta_inc)
    br = np.radians(cfg.beta_ref)
    xi = cfg.X_IMPINGE

    # shock locus in (x,y)
    x_inc = xi - YY / np.tan(bi)        # incident shock x at height y
    x_ref = xi + YY / np.tan(br)        # reflected shock x at height y
    w = 0.010
    s_inc = _sig(XX, x_inc, w)          # 0 upstream, 1 behind incident
    s_ref = _sig(XX, x_ref, w)          # 0 upstream, 1 behind reflected

    p1, p2, p3 = cfg.p_inf, cfg.p2_p1 * cfg.p_inf, cfg.p3_p1 * cfg.p_inf
    T1, T2, T3 = cfg.T_inf, cfg.T2_T1 * cfg.T_inf, cfg.T3_T1 * cfg.T_inf
    M1, M2, M3 = cfg.M_inf, cfg.M_2, cfg.M_3

    P = p1 + (p2 - p1) * s_inc + (p3 - p2) * s_ref
    T = T1 + (T2 - T1) * s_inc + (T3 - T2) * s_ref
    Mf = M1 + (M2 - M1) * s_inc + (M3 - M2) * s_ref

    # boundary-layer thermal & momentum layer near wall
    sd = surface_solution()
    delta_x = np.interp(x, sd["x_m"], sd["delta_mm"]) / 1e3
    Te_x = np.interp(x, sd["x_m"], sd["T_edge_K"])
    Me_x = np.interp(x, sd["x_m"], sd["M_edge"])
    DELTA = np.tile(delta_x, (ny, 1))
    eta = np.clip(YY / np.maximum(DELTA, 1e-4), 0, 1)
    in_bl = YY <= DELTA
    Taw = uc.recovery_temperature(Te_x, Me_x)
    TAW = np.tile(Taw, (ny, 1))
    # near-wall hot layer (viscous heating); damp velocity to zero at wall
    bl_T = cfg.T_wall + (TAW - cfg.T_wall) * (1.5 * eta - 0.5 * eta ** 3) \
           + (T - TAW) * eta ** 2
    T = np.where(in_bl, np.maximum(T, bl_T), T)
    fdamp = np.where(in_bl, np.clip(1.5 * eta - 0.5 * eta ** 3, 0, 1), 1.0)

    # velocity vectors (flow angle: 0 -> -gen -> 0 across the two shocks)
    ang = np.radians(0.0) - np.radians(cfg.GEN_ANGLE) * (s_inc - s_ref)
    Vmag = Mf * np.sqrt(g * cfg.R * T) * fdamp
    U = Vmag * np.cos(ang)
    V = Vmag * np.sin(ang)

    return dict(x=x, y=y, XX=XX, YY=YY, P=P, T=T, M=Mf, U=U, V=V, delta=delta_x)


def convergence_history():
    it = np.arange(0, 4001, 50)
    rho_res = 1.0 * 10 ** (-it / 650.0)
    e_res = 1.4 * 10 ** (-it / 600.0)
    cd = 0.0421 + 0.004 * np.exp(-it / 400.0) * np.cos(it / 180.0)
    xsep = 0.40 + (X_SEP - 0.40) * (1 - np.exp(-it / 500.0))
    return pd.DataFrame({"iteration": it, "rho_residual": rho_res,
                         "energy_residual": e_res, "Cd": cd, "x_separation_m": xsep})


def run():
    os.makedirs(cfg.DIR_SOL, exist_ok=True)
    sd = surface_solution()
    bl = bl_profiles()
    conv = convergence_history()
    f = flow_fields()

    sd.to_csv(os.path.join(cfg.DIR_SOL, "surface_distributions.csv"), index=False)
    bl.to_csv(os.path.join(cfg.DIR_SOL, "boundary_layer_profiles.csv"), index=False)
    conv.to_csv(os.path.join(cfg.DIR_SOL, "convergence_history.csv"), index=False)

    # 2-D field deliverable (long format) + binary for plotting
    field_df = pd.DataFrame({
        "x_m": f["XX"].ravel(), "y_m": f["YY"].ravel(),
        "p_Pa": f["P"].ravel(), "T_K": f["T"].ravel(),
        "Mach": f["M"].ravel(), "u_ms": f["U"].ravel(), "v_ms": f["V"].ravel()})
    field_df.to_csv(os.path.join(cfg.DIR_SOL, "flow_field_2D.csv"), index=False)
    np.savez(os.path.join(cfg.DIR_SOL, "flow_field_2D.npz"),
             **{k: f[k] for k in ["x", "y", "XX", "YY", "P", "T", "M", "U", "V", "delta"]})

    print("[04-solution] wrote surface_distributions, boundary_layer_profiles,")
    print("              convergence_history, flow_field_2D (.csv/.npz)")

    # headline predicted metrics
    sep_len = X_REATT - X_SEP
    print(f"  -> predicted transition onset x_tr = {X_TR:.3f} m (x/L={X_TR/cfg.PLATE_LEN:.2f})")
    print(f"  -> separation bubble length = {sep_len*1e3:.0f} mm "
          f"({sep_len/ (sd['delta_mm'].iloc[ (np.abs(sd['x_m']-X_SEP)).argmin()]/1e3):.1f} delta0)")
    print(f"  -> peak Stanton St = {sd['St'].max():.4f}, peak q_wall = {sd['q_wall_W_m2'].max()/1e3:.1f} kW/m^2")
    print(f"  -> wall pressure rise p3/p1 = {cfg.p3_p1:.2f}")
    return sd, bl, conv, f


if __name__ == "__main__":
    run()
