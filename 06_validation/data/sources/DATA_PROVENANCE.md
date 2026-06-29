# Validation data provenance & sourcing record

This file records the effort to source RAW experimental data for each
benchmark, so the validation is auditable. Author: Akosa Samuel Onyejekwe.

## V1 — Schülein Mach 5 impinging-shock SWBLI  ✅ REAL DATA
- **Status:** real measured data integrated.
- **Quantity:** skin-friction coefficient Cf(x) through the interaction
  (attached → reverse flow Cf<0 → reattachment), 38 measured points.
- **Source:** digitized optical Cf from Schülein, "Optical Skin Friction
  Measurements in Short-Duration Facilities," AIAA-2004-2115 (fig. 7),
  distributed in the NASA Glenn WIND validation archive (case `m5swbli`,
  file `Schulein2004_fig7_10deg_cfopt.dat`).
- **Original experiment:** Schülein, Krogmann, Stanewsky, DLR IB 223-96 A 49
  (1996). Measured separation S = 334 mm, reattachment R = 345 mm.
- **Files preserved here:** `Schulein2004_fig7_10deg_cfopt.dat`,
  `Schulein1996_10deg_bl.dat`. Parsed array:
  `../V1_schulein_M5_cf_experiment.csv`.
- **Archive:** https://www.grc.nasa.gov/WWW/wind/valid/m5swbli/m5swbli.html

## V2 — Settles Mach 2.95, 20° compression ramp  ✅ REAL DATA
- **Status:** real measured data integrated (wall pressure).
- **Quantity:** wall pressure p/p0 vs X/δ0 through the ramp interaction
  (upstream rise → separation plateau → reattachment compression), 18 points.
- **Source:** digitized from AGARD-AG-280 (Délery & Marvin, "Shock-Wave
  Boundary Layer Interactions," AGARDograph 280, 1986), **Fig. 3.22** —
  Settles (1975) ramp data at M0 = 2.95, Re_δ0 = 0.78×10⁶, α = 20°. (Note:
  the highest angle in that figure is 20°, not 24°; the validated case is
  therefore the real 20° ramp.) Source crop:
  `Settles1975_AGARD-AG-280_fig3.22_M2p95_ramp_pressure.png`. Parsed array:
  `../V2_settles_M2p95_20deg_pressure_experiment.csv`.
- **Original experiment:** Settles, G.S. (1975), PhD thesis, Princeton Univ.;
  Settles, Vas & Bogdonoff, AIAA J. 14(12), 1976.
- **Earlier rejected (kept for the record):** Qin et al. (2024) "ramp"
  figures plot Carter / Hung & MacCormack *numerical laminar* solutions, not
  Settles — rejected. Settles–Dodson NASA-CR database (archive.org
  `nasa_techdoc_19940032012`) keeps its tables on an accompanying diskette;
  the scanned OCR is garbled and its corner cases are Mach 3–4 — rejected.
- **Not yet covered:** skin friction Cf for this ramp (no clean digitizable
  Cf figure found); V2 is wall-pressure-only.

## V3 — Mach 6 cone transition heating  ✅ REAL DATA
- **Status:** real measured data integrated (surface heating ratio).
- **Quantity:** natural-transition heating ratio h/h_ref vs Re_x (laminar
  floor → transition rise → turbulent recovery), 22 points, Re_x = 1.4–8.6×10⁶;
  measured transition (intermittency midpoint) at Re_x ≈ 4.3×10⁶.
- **Source:** digitized from **AIAA-2002-2743** (Horvath, T.J., Berry, S.A.,
  Hollis, B.R., Chang, C.-L. & Singer, B.A., "Boundary Layer Transition on
  Slender Cones in Conventional and Low Disturbance Mach 6 Wind Tunnels," NASA
  Langley, 2002), **Fig. 4b** — 5° straight cone, M∞=6, Re_x=4.3×10⁶/ft, the
  "No trip (natural transition)" curve; x[in]→Re_x via Re_x = 4.3·x/12. Source
  crop: `Horvath2002_AIAA-2002-2743_fig4b_M6cone_heating.png`. Parsed array:
  `../V3_horvath_M6_cone_heating_experiment.csv`. (NASA NTRS doc 20030000846.)
- **Earlier examined for the sharp-cone case:** Stetson, AFWAL-TR-86-3089
  (1986, DTIC AD-A178877) — a transition-location / bluntness study with no
  clean digitizable heating curve; superseded here by the Horvath data.
- **Note:** the validated cone (5°, NASA Langley) differs from the originally
  cited Stetson 8° cone; the benchmark was relabeled to match the real data.

## Principle
Only data traceable to a real, correctly-matched source is labeled "real."
Numerical reference solutions, mismatched flow conditions, and garbled OCR are
explicitly NOT substituted in, to avoid false precision in the error metrics.
