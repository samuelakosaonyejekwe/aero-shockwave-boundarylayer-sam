# Validation data sources

UniSTAR-CFD is validated against three credible, widely-cited public
benchmarks. V1 now uses REAL measured experimental data; V2 and V3 use
reconstructed reference distributions (see NOTE) pending substitution of the
raw tabulated datasets.

## V1 - Mach 5 impinging oblique-shock / turbulent boundary-layer interaction
  *** REAL EXPERIMENTAL DATA ***
- Quantity validated: skin-friction coefficient Cf(x) through the interaction
  (attached upstream -> reverse flow Cf<0 in the bubble -> reattachment),
  38 measured points, x = 274-454 mm. Measured separation/reattachment at
  S = 334 mm, R = 345 mm (DLR 1996, sections 101/102).
- Raw data digitized from fig. 7 of: Schuelein, E. (2004), "Optical Skin
  Friction Measurements in Short-Duration Facilities", AIAA-2004-2115, and
  distributed in the NASA Glenn WIND validation archive (case m5swbli).
  Files preserved verbatim in `data/sources/`; parsed array in
  `data/V1_schulein_M5_cf_experiment.csv`.
- Original experiment: Schuelein, E., Krogmann, P., Stanewsky, E. (1996),
  "Documentation of Two-Dimensional Impinging Shock / Turbulent Boundary
  Layer Interaction Flow", DLR Report DLR IB 223-96 A 49.
- NASA Glenn WIND validation archive, "Mach 5 Shock Wave Boundary Layer
  Interaction": https://www.grc.nasa.gov/www/wind/valid/m5swbli/m5swbli.html
  Geometry: 10 deg wedge shock generator on a 500 mm flat plate.

## V2 - Mach 2.95, 20 deg compression-ramp SWBLI
  *** REAL EXPERIMENTAL DATA ***
- Quantity validated: wall pressure p/p0 vs X/delta0 through the ramp
  interaction (upstream rise -> separation plateau -> reattachment
  compression), 18 points, X/delta0 = -2 to 4.5.
- Raw data digitized from AGARD-AG-280 (Delery, J. & Marvin, J.G.,
  "Shock-Wave Boundary Layer Interactions", AGARDograph 280, 1986), Fig.
  3.22 -- Settles (1975) ramp data at M0 = 2.95, Re_delta0 = 0.78e6,
  alpha = 20 deg. Source crop in `data/sources/`; parsed array in
  `data/V2_settles_M2p95_20deg_pressure_experiment.csv`.
- Original experiment: Settles, G.S. (1975), PhD thesis, Princeton Univ.;
  Settles, Vas & Bogdonoff, AIAA J. 14(12), 1976.

## V3 - Mach 6 cone boundary-layer transition heating
  *** REAL EXPERIMENTAL DATA ***
- Quantity validated: natural-transition surface-heating ratio h/h_ref vs
  Re_x (laminar floor -> transition rise -> turbulent recovery), 22 points,
  Re_x = 1.4-8.6 x 10^6. Measured transition (intermittency midpoint) at
  Re_x ~ 4.3 x 10^6.
- Raw data digitized from AIAA-2002-2743 (Horvath, T.J., Berry, S.A.,
  Hollis, B.R., Chang, C.-L. & Singer, B.A., "Boundary Layer Transition on
  Slender Cones in Conventional and Low Disturbance Mach 6 Wind Tunnels",
  NASA Langley, 2002), Fig. 4b -- 5-deg straight cone, M_inf = 6,
  Re_x = 4.3e6/ft, "No trip (natural transition)" curve. x[in] -> Re_x via
  Re_x = 4.3 * x/12. Source crop in `data/sources/`; parsed array in
  `data/V3_horvath_M6_cone_heating_experiment.csv`.
- Related sharp-cone transition references: Stetson, AFWAL-TR-86-3089 (1986,
  DTIC AD-A178877); Stetson & Rushton, AIAA J. 5 (1967).

NOTE: All three benchmarks (V1, V2, V3) now use REAL measured data digitized
from the cited source figures; raw files / source crops are preserved in
`data/sources/`. See `data/sources/DATA_PROVENANCE.md` for full provenance.
