# Shock-Wave / Boundary-Layer Transition in a Mach-4 Supersonic Intake

**Prediction of shock-wave / boundary-layer interaction (SWBLI) and laminar-to-turbulent
transition for the variable-geometry supersonic engine intake of a Mach-4 high-speed
research / transport aircraft, computed with the purpose-built `UniSTAR-CFD` universal solver.**

**Author:** Akosa Samuel Onyejekwe (Independent Researcher)

📄 **Full report:** [`aero_shockwave_boundarylayer_all.pdf`](aero_shockwave_boundarylayer_all.pdf) — the complete 58-page case study (analysis, figures, tables, engineering drawings, and validation).

---

## 1. Overview

The forebody compression ramp of a mixed-compression supersonic intake generates an oblique
shock. That shock impinges on the boundary layer growing along the internal cowl / second-ramp
wall. The interaction (SWBLI) drives boundary-layer separation and forces laminar→turbulent
transition. Predicting **where** transition occurs and **how large** the separation bubble is
governs:

- intake total-pressure recovery & distortion (engine-surge margin),
- boundary-layer bleed-system sizing,
- local aerothermal heat load on the cowl structure,
- unstart margin.

This repository contains a fully reproducible, end-to-end engineering pipeline — geometry, mesh,
model setup, solution, post-processing, validation, and a genuine 3-D solution — that produces the
report and every figure and table in it.

### Flight point & conditions

| Quantity | Value |
|---|---|
| Freestream Mach | 4.0 |
| Altitude (ISA) | 20 km (T∞ = 216.65 K, p∞ = 5475 Pa) |
| Freestream velocity | ≈ 1180 m/s |
| Unit Reynolds number | ≈ 7.3 × 10⁶ /m |
| Stagnation temperature | ≈ 910 K |
| Forebody-ramp shock generator | 10° deflection |
| Wall thermal condition | fixed-temperature cooled cowl, Tᵥᵥ = 470 K |
| Inviscid pressure rise through interaction | p₃/p₁ ≈ 5.45 |

## 2. The `UniSTAR-CFD` solver

`UniSTAR-CFD` (Universal Shock-Transition Adaptive Resolver) couples a compressible RANS core, a
k-ω SST turbulence model, and a novel **Unified Shock-Transition Closure (USTC)** that predicts
shock-induced bypass transition within a single transport framework, using a machine-learning,
regime-adaptive coefficient set calibrated to the local (M, Re, Tᵥᵥ/T₀). The solver core lives in
[`00_solver/unistar_core.py`](00_solver/unistar_core.py).

## 3. Repository structure

The project is organised as a staged pipeline; each stage writes data consumed by the next.

| Stage | Directory | Purpose |
|---|---|---|
| Solver | [`00_solver/`](00_solver) | `UniSTAR-CFD` core (gas dynamics, shock relations, closures) |
| 01 | [`01_geometry/`](01_geometry) | Case geometry + engineering drawings |
| 02 | [`02_mesh/`](02_mesh) | Mesh generation & grid-independence study |
| 03 | [`03_model_setup/`](03_model_setup) | Freestream, boundary conditions, numerics, calibration |
| 04 | [`04_solution/`](04_solution) | Surface & flow-field solution, integral BL, engineering outputs |
| 05 | [`05_postprocessing/`](05_postprocessing) | All report figures + consolidated result tables |
| 06 | [`06_validation/`](06_validation) | Validation against public experimental benchmarks |
| 07 | [`07_3D_solution/`](07_3D_solution) | Genuine 3-D (finite-span) SWBLI solution & figures |

Shared plotting style (colour-blind-safe palette, no pure black) is defined in
[`05_postprocessing/plot_style.py`](05_postprocessing/plot_style.py).

## 4. Validation against real experimental data

`UniSTAR-CFD` is validated against **three credible, widely-cited public benchmarks**. Every
benchmark is assessed against **real measured data digitized from the cited source figures** — the
raw source crops and a full provenance record are preserved in
[`06_validation/data/sources/`](06_validation/data/sources).

| # | Benchmark | Quantity | Source | NRMSE | R² |
|---|---|---|---|---|---|
| V1 | Schülein Mach 5 impinging-shock SWBLI | skin friction Cf(x) | DLR; NASA WIND archive | 3.4 % | 0.99 |
| V2 | Settles Mach 2.95, 20° compression ramp | wall pressure p/p₀ | AGARD-AG-280, Fig. 3.22 | 3.3 % | 0.99 |
| V3 | Horvath/Berry Mach 6 slender cone | transition heating h/h_ref | NASA Langley, AIAA-2002-2743, Fig. 4b | 4.3 % | 0.98 |

Measured transition Reynolds number (V3): **4.33 × 10⁶** vs `UniSTAR-CFD` **4.30 × 10⁶** (−0.7 %).

> **Provenance note:** experimental arrays are digitized from the published source figures; each
> dataset is documented (source, figure, conditions) in
> [`06_validation/data/sources/DATA_PROVENANCE.md`](06_validation/data/sources/DATA_PROVENANCE.md).
> No numerical-reference or mismatched-condition data is presented as measured.

## 5. Contents

Each stage directory contains its analysis code and the data, figures, and tables it produces,
built on the `UniSTAR-CFD` core in [`00_solver/`](00_solver). Stage scripts are written for
Python 3.10+ (`numpy`, `pandas`, `matplotlib`). The authoritative deliverable is the complete
report, `aero_shockwave_boundarylayer_all.pdf`, which collects the full analysis, every figure
and table, the engineering drawings, and the validation results.

## 6. Key outputs

- **Report:** `aero_shockwave_boundarylayer_all.pdf` (complete case study + engineering drawings)
- **Figures:** `05_postprocessing/figures/` (surface curves, contours, 3-D fields, dashboard) and
  `07_3D_solution/figures/` (3-D SWBLI), plus a figure manifest
- **Tables:** `05_postprocessing/tables/` (16 consolidated result tables + manifest)
- **Validation:** `06_validation/` (figures, metrics, transition-Reynolds comparison, source data)

## 7. Plotting conventions

All figures use a colour-blind-safe palette with dark-navy text and axes — **no pure black is used
anywhere** — and labels are kept clear of the data.

## 8. License & attribution

© Akosa Samuel Onyejekwe. Independent research case study. Experimental benchmark data remains the
property of the original authors / institutions cited above and in the provenance record.
