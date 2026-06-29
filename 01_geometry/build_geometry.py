"""
STAGE 01 - GEOMETRY
Defines the SWBLI test section (cowl-side wall + shock generator) and
writes the geometry definition table used by meshing & solver stages.
"""
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import case_config as cfg


def build():
    L, H = cfg.PLATE_LEN, cfg.DUCT_HEIGHT
    xi = cfg.X_IMPINGE
    beta = np.radians(cfg.beta_inc)

    # shock generator origin: incident shock reaches the wall at (xi, 0).
    # the generator leading edge sits at height H; shock travels at angle beta.
    x_gen_le = xi - H / np.tan(beta)

    rows = [
        ["wall_leading_edge",        0.0,        0.0,   "internal cowl / 2nd-ramp wall start"],
        ["wall_trailing_edge",       L,          0.0,   "wall end (engine-face station)"],
        ["generator_leading_edge",   x_gen_le,   H,     "forebody-ramp shock generator LE"],
        ["generator_trailing_edge",  L*0.65,     H,     "shock generator TE"],
        ["inviscid_impingement",     xi,         0.0,   "nominal incident-shock foot on wall"],
        ["reflected_shock_exit",     xi + H/np.tan(np.radians(cfg.beta_ref)), H, "reflected shock exits duct"],
    ]
    geom = pd.DataFrame(rows, columns=["point", "x_m", "y_m", "description"])

    params = pd.DataFrame([
        ["plate_length_m",            cfg.PLATE_LEN],
        ["plate_span_m",              cfg.PLATE_SPAN],
        ["duct_height_m",             cfg.DUCT_HEIGHT],
        ["generator_deflection_deg",  cfg.GEN_ANGLE],
        ["incident_shock_angle_deg",  cfg.beta_inc],
        ["reflected_shock_angle_deg", cfg.beta_ref],
        ["inviscid_impingement_x_m",  cfg.X_IMPINGE],
        ["generator_LE_x_m",          x_gen_le],
    ], columns=["parameter", "value"])

    os.makedirs(cfg.DIR_GEOM, exist_ok=True)
    geom.to_csv(os.path.join(cfg.DIR_GEOM, "geometry_points.csv"), index=False)
    params.to_csv(os.path.join(cfg.DIR_GEOM, "geometry_parameters.csv"), index=False)
    print("[01-geometry] wrote geometry_points.csv, geometry_parameters.csv")
    return geom, params, x_gen_le


if __name__ == "__main__":
    build()
