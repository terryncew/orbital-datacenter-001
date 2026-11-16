# Integrated Structural Thermal Management for Orbital Computing

## A Comparative Engineering and Economic Study

**Status: computational, AI-assisted research.** Every result in this
repository is a modeled output of the simulation code in `simulation/`. No
physical thermal-vacuum validation has been performed. The TVAC coupon test
described in the paper is the falsification gate for the central thermal
claim. Nothing here is demonstrated hardware performance.

## What we found

We compared 12 orbital and terrestrial computing architectures at 1, 150,
and 1,000 kW, across two workload regimes: general AI for terrestrial users
(Regime C3) and space-native edge triage of Earth-observation, SAR, and
hyperspectral data (Regime C1/C2).

| Finding | Value (150 kW, $1,500/kg launch, 5 yr) |
|---|---|
| Structural oscillating-heat-pipe panel (A09) coupled thermal mass vs the conventional lightweight radiator incumbent (A04) | **2.725 vs 6.817 kg/kW — 60.0% lower** |
| Sparse orbital edge + A09 (A10) actionable scenes per dollar vs terrestrial clean-grid (A11) | **0.486 vs 0.159 — 3.06×** |
| Terrestrial clean-grid (A11) vs the best orbital arm, general AI (TFLOPS-yr/$) | **14.447 vs 1.486 — 9.72×** |
| Terrestrial still cheaper for general AI, even at $100/kg launch | **$1,384 vs $2,622/kW-yr — 1.89×** |
| Naive pumped structural panel (A06) vs incumbent | Rejected: +72.3% mass, 76.08% MMOD survival |
| Liquid droplet radiator (A08) vs incumbent | Rejected: 68.28% MMOD survival, $224,586/kW-yr |

The split verdict: **orbital computing loses for general-purpose AI and wins
only for space-native edge triage** — where the data is already in orbit and
the alternative is downlinking it all. That negative result for Regime C3 is
a finding of the study, not a footnote: it holds at every launch price from
$1,500/kg down to $100/kg.

## What is fragile

The 60% thermal-mass claim survives any single benefit failing (worst single
case: 44.4%) but falls to 19.3% if all four modeled benefits fail together.
The 3.06× scenes-per-dollar claim is fragile: it depends on two assigned
inputs — a 5.80× useful-scene multiplier and 160:1 downlink compression —
with no cited measurement behind them. At a 2.0× multiplier the advantage is
1.05× (parity); at 8:1 compression it is 1.32×; with both degraded,
terrestrial wins (0.46×). Breakevens: multiplier ≈ 1.90, compression ≈ 4.3×.
See Figure 3 and `evidence/` for the full sensitivity tables.

## Reproduce it

```sh
python3 -m venv .venv
.venv/bin/pip install -r simulation/requirements.txt
python3 simulation/run_reproduction.py
```

One command regenerates the tournament, the sensitivity analysis, the
stress-case replay, figures 1–3, the CAD drawings, the evidence JSON and
leaderboard CSV, runs the 8-test suite in standard and `-O` modes, verifies
byte-determinism, and writes `SHA256SUMS.txt`. See `simulation/README.md`.

## Contents

| Path | What it is |
|---|---|
| `PAPER.md` / `PAPER.pdf` | The full paper: methodology, equations, assumptions, results, limitations, prior art, references. |
| `SUMMARY.md` | Short accessible summary. |
| `CITATIONS.md` | Every cited source, verified to exist, with what it supports — and what was removed for failing verification. |
| `VERIFICATION.md` | Per-claim verification table and the full corrections log (what reproduced, what was corrected, what was withdrawn). |
| `simulation/` | The model, the coupon repairs, the figure generator, the one-command runner, and the 8-test suite. |
| `evidence/` | Regenerated evidence JSON, 150 kW leaderboard CSV. |
| `figures/` | Figures 1–3, regenerated from the reproduced data. |
| `cad_and_drawings/` | Inert TVAC coupon: STEP B-Rep, SPICE netlist, STL, DXF, SVG blueprint. Stage 0 is inert only — energized testing is on hold pending external PE/EHS signoff. |

## The falsification test

The single most important remaining test is a thermal-vacuum (TVAC) coupon
measurement of the **microgravity oscillation startup threshold** of the
structural oscillating-heat-pipe panel, with brazed-joint contact
conductance as the measurable proxy (effective conductivity ≥ 1,200 W/m·K;
reject the architecture if < 600 W/m·K or dryout below 50 W). The modeled
thermal advantage rests on an assumed 8.2 K junction-to-radiator temperature
drop, which assumes the heat pipe actually oscillates and transports heat at
panel scale in microgravity. If the coupon shows no sustained oscillation,
the 60% claim collapses regardless of the conductivity number. Geometry and
mass gate: dry mass ≤ 62% of a solid aluminum control at equal bending
stiffness (±5%); helium leak < 1×10⁻⁸ atm·cc/s at 1.5× maximum working
pressure.

## License

Apache License 2.0. See `LICENSE`.
