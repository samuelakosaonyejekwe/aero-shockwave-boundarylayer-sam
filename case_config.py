"""
=====================================================================
 CASE CONFIGURATION  --  shared constants for all pipeline stages
 ---------------------------------------------------------------------
 INDUSTRIAL CASE STUDY
   "Shock-wave / boundary-layer transition prediction for the
    variable-geometry supersonic engine intake of a Mach-4
    high-speed research/transport aircraft (HSRA)"

 Physical scenario:
   The forebody compression ramp of a mixed-compression supersonic
   intake generates an oblique shock. That shock impinges on the
   boundary layer growing along the internal cowl / second-ramp wall.
   The interaction (SWBLI) drives boundary-layer separation and
   forces laminar->turbulent transition. Predicting WHERE transition
   occurs and HOW LARGE the separation bubble is governs:
       * intake total-pressure recovery & distortion (engine surge)
       * boundary-layer bleed-system sizing
       * local heat load on the cowl structure
       * unstart margin
 ---------------------------------------------------------------------
 Flight point:  Mach 4.0 cruise, 20 km standard altitude.
=====================================================================
"""
import os
import numpy as np
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "00_solver"))
import unistar_core as uc

# ---- output directories -------------------------------------------------
DIR_GEOM = os.path.join(HERE, "01_geometry")
DIR_MESH = os.path.join(HERE, "02_mesh")
DIR_SET  = os.path.join(HERE, "03_model_setup")
DIR_SOL  = os.path.join(HERE, "04_solution")
DIR_POST = os.path.join(HERE, "05_postprocessing")
DIR_FIG  = os.path.join(DIR_POST, "figures")
DIR_TAB  = os.path.join(DIR_POST, "tables")
DIR_VAL  = os.path.join(HERE, "06_validation")
DIR_VALD = os.path.join(DIR_VAL, "data")
DIR_VALF = os.path.join(DIR_VAL, "figures")

# =====================================================================
# FREESTREAM (Mach 4.0, 20 km ISA)
# =====================================================================
GAMMA = uc.GAMMA
R     = uc.R_AIR

M_inf   = 4.0
T_inf   = 216.65            # K   (ISA 20 km)
p_inf   = 5474.9            # Pa  (ISA 20 km)
rho_inf = p_inf / (R * T_inf)
a_inf   = np.sqrt(GAMMA * R * T_inf)
U_inf   = M_inf * a_inf
mu_inf  = uc.mu_sutherland(T_inf)
Re_unit = rho_inf * U_inf / mu_inf          # per metre
T0      = T_inf * uc.isentropic_T0_T(M_inf)
p0      = p_inf * uc.isentropic_p0_p(M_inf)

# Wall thermal condition (radiation-equilibrium cooled cowl)
T_wall  = 470.0                              # K  (fixed-temperature wall)
Tw_T0   = T_wall / T0

# =====================================================================
# GEOMETRY
# =====================================================================
PLATE_LEN     = 1.000        # m   internal cowl / second-ramp wall length
PLATE_SPAN    = 0.300        # m   modelled spanwise width
GEN_ANGLE     = 10.0         # deg forebody-ramp shock-generator deflection
DUCT_HEIGHT   = 0.150        # m   distance generator-to-wall at leading edge
X_IMPINGE     = 0.550        # m   inviscid shock-impingement location on wall

# =====================================================================
# DERIVED INVISCID SHOCK SYSTEM (incident + reflected)
# =====================================================================
_inc = uc.solve_oblique_shock(M_inf, GEN_ANGLE)          # incident shock
M_2  = _inc["M2"]
_ref = uc.solve_oblique_shock(M_2, GEN_ANGLE)            # reflected shock
INCIDENT  = _inc
REFLECTED = _ref
p2_p1 = _inc["p2p1"]
p3_p2 = _ref["p2p1"]
p3_p1 = p2_p1 * p3_p2
M_3   = _ref["M2"]
T2_T1 = _inc["T2T1"]
T3_T1 = _inc["T2T1"] * _ref["T2T1"]
beta_inc = _inc["beta_deg"]
beta_ref = _ref["beta_deg"]

# =====================================================================
# CALIBRATION (ML regime-adaptive coefficient set)
# =====================================================================
COEFFS = uc.regime_calibrated_coeffs(M_inf, Re_unit, Tw_T0)

# Streamwise sampling grid (surface)
NX = 600
X  = np.linspace(0.010, PLATE_LEN, NX)   # start off the LE singularity


def summary():
    return {
        "M_inf": M_inf, "T_inf_K": T_inf, "p_inf_Pa": p_inf,
        "rho_inf": rho_inf, "U_inf_ms": U_inf, "a_inf_ms": a_inf,
        "mu_inf": mu_inf, "Re_unit_perm": Re_unit, "T0_K": T0, "p0_Pa": p0,
        "T_wall_K": T_wall, "Tw_T0": Tw_T0,
        "beta_inc_deg": beta_inc, "beta_ref_deg": beta_ref,
        "p2_p1": p2_p1, "p3_p1": p3_p1, "M_2": M_2, "M_3": M_3,
        "x_impinge_m": X_IMPINGE,
    }


if __name__ == "__main__":
    import json
    print(json.dumps({k: round(v, 5) if isinstance(v, float) else v
                      for k, v in summary().items()}, indent=2))
