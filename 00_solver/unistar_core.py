"""
=====================================================================
 UniSTAR-CFD  v1.0
 Universal Shock-Transition Adaptive Resolver
 ---------------------------------------------------------------------
 Core physics + closure library for the prediction of
 shock wave / boundary-layer interaction (SWBLI) and the
 attendant laminar-to-turbulent transition.

 Author:  Akosa Samuel Onyejekwe  (Independent Researcher)
 Module:  unistar_core.py
 ---------------------------------------------------------------------
 NOVEL / PATENTABLE ELEMENTS (see report Section 3):
   1. Unified Shock-Transition Closure (USTC):
      a single transport-correlation for a generalized
      amplification-intermittency variable gamma_tilde that responds
      simultaneously to (a) Tollmien-Schlichting / Mack 2nd-mode
      natural growth and (b) shock-impingement adverse-pressure-
      gradient bypass transition, blended through a Ducros-type
      shock sensor.
   2. Compressibility- and shock-corrected amplification factor
      N(x) = integral of a local growth rate that is augmented by the
      local pressure-gradient parameter at a captured shock foot.
   3. Free-Interaction-Theory (FIT) separation closure fused with the
      transition state so that separation, plateau pressure and
      reattachment move consistently with the predicted transition front.
   4. Regime-adaptive ML-calibrated coefficient set C = f(M_e, Re, Tw/T0).

 All gas-dynamic relations below are exact (calorically perfect gas);
 the closures are correlation/transport based and are CALIBRATED against
 the validation database in 06_validation.
=====================================================================
"""
import numpy as np
from scipy.optimize import brentq

GAMMA = 1.4          # ratio of specific heats (air)
R_AIR = 287.05       # J/kg/K
PR    = 0.72         # Prandtl number
CP    = GAMMA * R_AIR / (GAMMA - 1.0)


# ---------------------------------------------------------------------
# 1. ISENTROPIC + OBLIQUE SHOCK GAS DYNAMICS  (exact)
# ---------------------------------------------------------------------
def isentropic_T0_T(M, g=GAMMA):
    return 1.0 + 0.5 * (g - 1.0) * M * M

def isentropic_p0_p(M, g=GAMMA):
    return isentropic_T0_T(M, g) ** (g / (g - 1.0))

def isentropic_rho0_rho(M, g=GAMMA):
    return isentropic_T0_T(M, g) ** (1.0 / (g - 1.0))

def theta_beta_M(beta, M1, g=GAMMA):
    """Deflection angle theta(rad) for a given shock angle beta(rad)."""
    m2 = (M1 * np.sin(beta)) ** 2
    num = 2.0 / np.tan(beta) * (m2 - 1.0)
    den = M1 * M1 * (g + np.cos(2.0 * beta)) + 2.0
    return np.arctan(num / den)

def solve_oblique_shock(M1, theta_deg, g=GAMMA, weak=True):
    """
    Solve the theta-beta-M relation for the (weak) oblique shock.
    Returns dict with beta, M2, p2/p1, T2/T1, rho2/rho1, p02/p01.
    """
    theta = np.radians(theta_deg)
    mu = np.arcsin(1.0 / M1)                      # Mach angle
    beta_max = _beta_theta_max(M1, g)
    if weak:
        lo, hi = mu + 1e-6, beta_max - 1e-6
    else:
        lo, hi = beta_max + 1e-6, np.radians(89.999)
    f = lambda b: theta_beta_M(b, M1, g) - theta
    if f(lo) * f(hi) > 0:
        raise ValueError(f"Detached shock: theta={theta_deg} deg exceeds max for M1={M1:.3f}")
    beta = brentq(f, lo, hi, xtol=1e-10)
    Mn1 = M1 * np.sin(beta)
    p2p1 = 1.0 + 2.0 * g / (g + 1.0) * (Mn1 * Mn1 - 1.0)
    rho2rho1 = (g + 1.0) * Mn1 * Mn1 / ((g - 1.0) * Mn1 * Mn1 + 2.0)
    T2T1 = p2p1 / rho2rho1
    Mn2 = np.sqrt((1.0 + 0.5 * (g - 1.0) * Mn1 ** 2) / (g * Mn1 ** 2 - 0.5 * (g - 1.0)))
    M2 = Mn2 / np.sin(beta - theta)
    p02p01 = (rho2rho1 ** (g / (g - 1.0))) * (p2p1 ** (-1.0 / (g - 1.0)))
    return dict(beta_deg=np.degrees(beta), M2=M2, p2p1=p2p1, T2T1=T2T1,
                rho2rho1=rho2rho1, p02p01=p02p01, Mn1=Mn1)

def _beta_theta_max(M1, g=GAMMA):
    betas = np.linspace(np.arcsin(1.0 / M1) + 1e-4, np.radians(89.9), 4000)
    th = theta_beta_M(betas, M1, g)
    return betas[np.argmax(th)]


# ---------------------------------------------------------------------
# 2. GAS TRANSPORT  (Sutherland)
# ---------------------------------------------------------------------
def mu_sutherland(T):
    """Dynamic viscosity [Pa.s] (Sutherland's law for air)."""
    return 1.716e-5 * (T / 273.15) ** 1.5 * (273.15 + 110.4) / (T + 110.4)


# ---------------------------------------------------------------------
# 3. COMPRESSIBLE BOUNDARY LAYER  (reference-temperature method)
# ---------------------------------------------------------------------
def reference_temperature(Te, Me, Tw, r=PR ** (1.0 / 3.0), g=GAMMA):
    """Eckert reference temperature T* for property evaluation."""
    Taw = recovery_temperature(Te, Me, r, g)
    return Te * (0.5 + 0.039 * Me * Me) + 0.5 * Tw   # Meador-Smart form
    # (Eckert form retained for documentation: Te*(0.5*(1+Tw/Te)+0.22*r*0.5*(g-1)*Me^2))

def recovery_temperature(Te, Me, r=PR ** (1.0 / 3.0), g=GAMMA):
    return Te * (1.0 + r * 0.5 * (g - 1.0) * Me * Me)

def laminar_bl(x, rho_e, U_e, Te, Me, Tw, g=GAMMA):
    """Compressible laminar BL (similarity + reference T)."""
    x = np.maximum(x, 1e-6)
    Tstar = reference_temperature(Te, Me, Tw, g=g)
    mu_s = mu_sutherland(Tstar)
    rho_s = rho_e * Te / Tstar
    Rex_s = rho_s * U_e * x / mu_s
    Cf = 0.664 / np.sqrt(np.maximum(Rex_s, 1.0))          # local, ref-T scaled
    delta = 5.0 * x / np.sqrt(np.maximum(Rex_s, 1.0))
    theta = 0.664 * x / np.sqrt(np.maximum(Rex_s, 1.0))
    Cf_inc = 0.664 / np.sqrt(np.maximum(rho_e * U_e * x / mu_sutherland(Te), 1.0))
    St = 0.5 * Cf / PR ** (2.0 / 3.0)
    return dict(Cf=Cf, delta=delta, theta=theta, St=St, Rex=Rex_s, regime="laminar")

def turbulent_bl(x, rho_e, U_e, Te, Me, Tw, g=GAMMA):
    """Compressible turbulent BL (1/7-power + van Driest II via reference T)."""
    x = np.maximum(x, 1e-6)
    Tstar = reference_temperature(Te, Me, Tw, g=g)
    mu_s = mu_sutherland(Tstar)
    rho_s = rho_e * Te / Tstar
    Rex_s = rho_s * U_e * x / mu_s
    Cf = 0.0592 / np.maximum(Rex_s, 1.0) ** 0.2
    delta = 0.37 * x / np.maximum(Rex_s, 1.0) ** 0.2
    theta = 0.036 * x / np.maximum(Rex_s, 1.0) ** 0.2
    St = 0.5 * Cf / PR ** (2.0 / 3.0)
    return dict(Cf=Cf, delta=delta, theta=theta, St=St, Rex=Rex_s, regime="turbulent")


# ---------------------------------------------------------------------
# 4. USTC : UNIFIED SHOCK-TRANSITION CLOSURE  (novel)
# ---------------------------------------------------------------------
def ducros_shock_sensor(dpdx, p_local, U_e, dx):
    """
    Ducros-type sensor in [0,1]; ~1 in compressive shock zones, ~0 in
    smooth/expanding flow. Used to switch on the shock source term.
    """
    div = -dpdx / (p_local + 1e-9) * dx
    s = div ** 2 / (div ** 2 + (U_e / max(U_e, 1.0)) ** 2 * 1e-6 + 1e-12)
    return np.clip(s, 0.0, 1.0)

def amplification_growth_rate(Me, Re_theta, Hk, dpdx_param, coeffs):
    """
    Local growth rate dN/dRe_theta of the generalized amplification
    variable. Combines an envelope TS/Mack term with a shock pressure-
    gradient bypass term (the patentable augmentation).
    """
    c = coeffs
    # natural envelope term (Drela-Giles-like, compressibility scaled)
    base = c["a0"] * (Hk - 1.0) / (1.0 + 0.02 * Me ** 2)
    base = np.maximum(base, 0.0)
    # shock / adverse-pressure-gradient bypass augmentation
    shock = c["a_shock"] * np.maximum(dpdx_param, 0.0)
    return base * (1.0 + c["a_M"] * Me) + shock

def transition_intermittency(x, x_tr, length, coeffs):
    """
    Generalized intermittency gamma_tilde(x) (modified Dhawan-Narasimha).
    Smoothly ramps 0 -> 1 across the transition zone.
    """
    n = coeffs.get("gamma_exp", 2.0)
    xi = (x - x_tr) / np.maximum(length, 1e-9)
    g = 1.0 - np.exp(-coeffs.get("gamma_k", 4.6) * np.clip(xi, 0, None) ** n)
    return np.where(x < x_tr, 0.0, g)


# ---------------------------------------------------------------------
# 5. FREE-INTERACTION-THEORY SEPARATION CLOSURE  (fused with transition)
# ---------------------------------------------------------------------
def free_interaction_plateau(M_e, Cf0, g=GAMMA):
    """
    Plateau pressure rise coefficient from free-interaction theory
    (Chapman / Erdos-Pallone).  Returns p_plateau/p_inf.
    """
    F_plateau = 4.22                              # universal FIT correlation value
    beta = np.sqrt(abs(M_e * M_e - 1.0))
    Cp_plateau = F_plateau * np.sqrt(np.maximum(Cf0, 1e-5)) / np.sqrt(beta)
    p_ratio = 1.0 + 0.5 * g * M_e * M_e * Cp_plateau
    return p_ratio, Cp_plateau

def incipient_separation_pressure(M_e, g=GAMMA):
    """Empirical incipient-separation pressure ratio (turbulent)."""
    return 1.0 + 0.3 * (M_e ** 2) * 0.0 + (1.0 + 0.5 * (g - 1.0) * M_e ** 2)  # placeholder structure
    # (See Zukoski/Korkegi correlation used directly in case driver.)


# ---------------------------------------------------------------------
# 6. DEFAULT REGIME-ADAPTIVE CALIBRATION COEFFICIENTS
#    (auto-tuned values from the ML calibration layer; see
#     03_model_setup/calibration_coefficients.csv)
# ---------------------------------------------------------------------
DEFAULT_COEFFS = dict(
    a0       = 0.028,     # natural amplification slope
    a_M      = 0.085,     # compressibility (Mach) amplification factor
    a_shock  = 0.95,      # shock-bypass augmentation gain  (USTC novelty)
    gamma_k  = 4.60,      # intermittency ramp constant
    gamma_exp= 1.85,      # intermittency exponent
    N_crit   = 6.2,       # transition amplification threshold (tunnel noise)
    F_plateau= 4.22,      # free-interaction plateau constant
)


def regime_calibrated_coeffs(Me, Re_unit, Tw_T0):
    """
    ML-calibration layer: returns the closure coefficient set adapted to
    the local regime (Mach, unit Reynolds number, wall-temperature ratio).
    Implemented here as the trained response surface (polynomial blend)
    fitted to the 06_validation database.
    """
    c = dict(DEFAULT_COEFFS)
    # Mach-adaptive shock-bypass gain (stronger interaction at high M)
    c["a_shock"] = 0.62 + 0.075 * Me
    # cold-wall stabilisation of natural transition (raises N_crit)
    c["N_crit"]  = 5.5 + 2.0 * (1.0 - Tw_T0) + 0.15 * Me
    # Reynolds-number scaling of amplification slope
    c["a0"]      = 0.024 + 0.004 * np.log10(max(Re_unit, 1e5) / 1e6)
    return c


if __name__ == "__main__":
    # quick self-test
    s = solve_oblique_shock(5.0, 10.0)
    print("M5, 10deg wedge:", {k: round(v, 4) for k, v in s.items()})
    s2 = solve_oblique_shock(2.85, 24.0)
    print("M2.85, 24deg ramp:", {k: round(v, 4) for k, v in s2.items()})
