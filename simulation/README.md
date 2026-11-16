# Simulation — reproduction package

## Run it

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/pip install -r simulation/requirements.txt
python3 simulation/run_reproduction.py
```

One command regenerates everything: the coupon defect repairs (F1–F5, F8),
the 12-architecture tournament at 1 / 150 / 1,000 kW, the sensitivity analysis,
the unfamiliar stress-case replay, figures 1–3, the CAD drawings, the evidence
JSON and leaderboard CSV, and the `SHA256SUMS.txt` manifest. It runs the
8-test suite in standard and `-O` modes and verifies byte-determinism across
two consecutive regenerations. Expected runtime is a few minutes on a
single-core machine (the 3D finite-volume PDN solver dominates).

## Files

| File | What it is |
|---|---|
| `orbital_thermal_study.py` | The model. 12 architectures, Stefan–Boltzmann two-sided radiative flux, MMOD survival, economics, environmental ledger, the three-round tournament, the sensitivity analysis, and the unfamiliar stress-case replay. Standard library only. |
| `repair_coupon.py` | The coupon defect repairs F1–F5 and F8: 4×4 series-parallel 50 W SELV netlist, TO-247 collision fix, true manifold B-Rep STEP (Euler closure V−E+F=2), hydraulic channel repair, 3D finite-volume PDN solver. Needs numpy/scipy. |
| `generate_figures.py` | Figures 1–3 and the STL/DXF/SVG coupon drawings, regenerated from the reproduced data. Needs matplotlib/Pillow. |
| `run_reproduction.py` | The one-command driver. Writes `evidence/`, `figures/`, `cad_and_drawings/`, and `SHA256SUMS.txt` at the repository root. |
| `tests/test_orbital_thermal_study.py` | 8 tests. Artifact-generating tests use a temporary directory. |

## What is NOT in this package

The stress-case replay is reproduced here as a standalone function
(`evaluate_unfamiliar_spacecraft_stress_case`); no external engine is required. Two items from the earlier defect list (F6 and F7) concern analyses outside
this study and have no implementation in the released code; they are not
claimed as closed by this package; see `repair_coupon.py`.

## Status

Computational, AI-assisted research. Every number in the paper traces to a
run of this code. No physical thermal-vacuum validation has been performed;
the TVAC coupon test is the falsification gate for the central thermal claim.
