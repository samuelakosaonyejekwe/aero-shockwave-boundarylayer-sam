"""
STAGE 03 - MODEL SETUP
Writes the freestream/operating point, boundary conditions, solver
numerics settings, gas/material properties and the ML-calibrated
closure-coefficient table used by UniSTAR for this case.
Author: Akosa Samuel Onyejekwe (Independent Researcher)
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import case_config as cfg


def build():
    freestream = pd.DataFrame([
        ["freestream_Mach",          cfg.M_inf,    "-"],
        ["static_temperature",       cfg.T_inf,    "K"],
        ["static_pressure",          cfg.p_inf,    "Pa"],
        ["density",                  cfg.rho_inf,  "kg/m^3"],
        ["velocity",                 cfg.U_inf,    "m/s"],
        ["speed_of_sound",           cfg.a_inf,    "m/s"],
        ["dynamic_viscosity",        cfg.mu_inf,   "Pa.s"],
        ["unit_Reynolds_number",     cfg.Re_unit,  "1/m"],
        ["total_temperature",        cfg.T0,       "K"],
        ["total_pressure",           cfg.p0,       "Pa"],
        ["altitude_ISA",             20000.0,      "m"],
    ], columns=["quantity", "value", "unit"])

    bcs = pd.DataFrame([
        ["inflow",        "supersonic_inlet",   "M=4.0 fixed total p/T, fixed flow angle"],
        ["outflow",       "supersonic_outlet",  "1st-order extrapolation (M>1)"],
        ["wall",          "no-slip isothermal",  f"Tw = {cfg.T_wall:.1f} K (cooled cowl)"],
        ["shock_generator","inviscid_wedge",     f"{cfg.GEN_ANGLE:.1f} deg deflection"],
        ["farfield_top",  "characteristic",      "Riemann invariants"],
        ["spanwise",      "periodic",            "2.5D mean-flow assumption"],
    ], columns=["boundary", "type", "specification"])

    numerics = pd.DataFrame([
        ["governing_equations",   "compressible RANS (Favre-averaged)"],
        ["turbulence_model",      "k-omega SST (UniSTAR-coupled)"],
        ["transition_model",      "USTC unified shock-transition closure (gamma_tilde transport)"],
        ["convective_scheme",     "AUSM+-up, 3rd-order MUSCL, van Albada limiter"],
        ["shock_capture",         "Ducros-sensor hybrid + adaptive refinement"],
        ["time_integration",      "implicit LU-SGS, dual time-stepping"],
        ["CFL",                   "ramped 1 -> 50"],
        ["convergence_criterion", "density residual < 1e-6, force coeff < 1e-5"],
        ["flux_jacobian",         "exact analytical"],
        ["calibration_layer",     "ML regime response-surface (auto-tuned)"],
    ], columns=["setting", "value"])

    material = pd.DataFrame([
        ["gas",                  "air (calorically perfect)"],
        ["gamma",                str(cfg.GAMMA)],
        ["R_specific_J_kgK",     str(cfg.R)],
        ["Prandtl_number",       "0.72"],
        ["viscosity_law",        "Sutherland (1.716e-5, 110.4 K)"],
        ["thermal_conductivity", "k = mu*cp/Pr"],
    ], columns=["property", "value"])

    calib = pd.DataFrame([
        ["a0",        cfg.COEFFS["a0"],        "natural amplification slope"],
        ["a_M",       cfg.COEFFS["a_M"],       "compressibility amplification factor"],
        ["a_shock",   cfg.COEFFS["a_shock"],   "shock-bypass augmentation gain (USTC novelty)"],
        ["gamma_k",   cfg.COEFFS["gamma_k"],   "intermittency ramp constant"],
        ["gamma_exp", cfg.COEFFS["gamma_exp"], "intermittency exponent"],
        ["N_crit",    cfg.COEFFS["N_crit"],    "amplification threshold at transition onset"],
        ["F_plateau", cfg.COEFFS["F_plateau"], "free-interaction plateau constant"],
    ], columns=["coefficient", "calibrated_value", "role"])

    os.makedirs(cfg.DIR_SET, exist_ok=True)
    freestream.to_csv(os.path.join(cfg.DIR_SET, "freestream_conditions.csv"), index=False)
    bcs.to_csv(os.path.join(cfg.DIR_SET, "boundary_conditions.csv"), index=False)
    numerics.to_csv(os.path.join(cfg.DIR_SET, "solver_numerics.csv"), index=False)
    material.to_csv(os.path.join(cfg.DIR_SET, "material_properties.csv"), index=False)
    calib.to_csv(os.path.join(cfg.DIR_SET, "calibration_coefficients.csv"), index=False)
    print("[03-setup] wrote freestream, boundary, numerics, material, calibration CSVs")
    return freestream, bcs, numerics, material, calib


if __name__ == "__main__":
    build()
