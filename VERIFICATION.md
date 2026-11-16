# Verification — per-claim results

Independent verification of the science in this repository. All values below
are from executed code (`python3 simulation/run_reproduction.py`), not from any earlier version's text. Where an earlier version disagreed with the executed code, the code wins and the version's text is listed as a correction.

## Reproduction

- The tournament, the F1–F5/F8 repairs, the sensitivity analysis, and the
  unfamiliar stress-case replay all reproduce deterministically: two
  consecutive regenerations produce byte-identical evidence.
- The 8-test suite passes in standard and `-O` modes with zero warnings.
- The tournament outputs match an earlier version's outputs exactly
  (all `by_scale` values identical; the only differences are two corrected
  architecture display names and the round-progression strings, which are now
  computed from the results instead of hardcoded).
- The stress-case replay (250 kW, β=75°, 7 yr, q_env 210 W/m²) reproduces the
  earlier replay exactly: A10 3.346 kg/kW coupled, A04 8.73, A06 13.164.

## Headline claims (150 kW, $1,500/kg launch, 5 yr)

| Claim | Executed value | Verdict |
|---|---|---|
| A09 coupled thermal mass vs A04 | 2.725 vs 6.817 kg/kW = 60.03% lower | REPRODUCES |
| A09 screen (80 °C) vs A04 | 3.594 vs 5.423 = 33.73% lower | REPRODUCES |
| A10 scenes/$ vs A11 (C1) | 0.4861 vs 0.1589 = 3.059× | REPRODUCES |
| A10 vs A04 scenes/$ | 0.4861 vs 0.0328 = 14.82× | Corrected (earlier version said 14.7×) |
| A10 vs A02 scenes/$ | 0.4861 vs 0.0240 = 20.25× | Corrected (earlier version said 20.2×) |
| A11 vs A10 general AI (C3) | $1,384.33 vs $10,495.60/kW-yr; TFLOPS-yr/$ 9.72× | REPRODUCES |
| A11 vs best orbital at $100/kg | $1,384.33 vs $2,622.31 = 1.89× | Corrected (earlier version said 1.97× / $2,732) |
| Al₂O₃ reduction, A10 vs A04 | 84.05% | Corrected (earlier version said 83.9%) |
| A06 rejected | 9.345 kg/kW screen (+72.31%), coupled 10.500, MMOD 76.08%, $40,343.10/kW-yr | Corrected (earlier version said MMOD 78.57%; the rejection is stronger than stated) |
| A08 rejected | coupled 4.173, total 32.948, MMOD 68.28%, $224,585.57/kW-yr | REPRODUCES as executed; earlier version's table stale |
| Terrestrial cheaper for C3 at all launch prices | True at $1,500 / $500 / $250 / $100 per kg | REPRODUCES |

## Corrections to the earlier version

An earlier version's report text disagreed with its own code in twelve places.
All are corrected here; the paper and the code use the executed values.

1. **F1 electrical network.** The earlier version described an "8-series/2-parallel"
   network (4.80 Ω, 21.908902 V, R_eq 9.60 Ω). The implemented circuit is
   **4 parallel strings × 4 series × 11.52 Ω SMD 2512 at 24.0 V SELV,
   R_eq 11.52 Ω, 2.0833 A, 3.125 W/resistor, 50.000 W**. The earlier version's numbers
   are internally inconsistent (8S2P of 4.80 Ω gives R_eq 19.2 Ω and 25.0 W;
   its 9.60 Ω / 21.9089 V numbers imply 8S4P, whose per-resistor power is
   1.5625 W). The 8S2P description is withdrawn.
2. **F1 "50.000 W exact".** True for the matrix alone at its bus terminals.
   The netlist includes 0.020 Ω fuse + 0.010 Ω bimetal series protection:
   total draw **49.87 W**, matrix dissipation **49.74 W** (3.109 W/resistor).
   Both figures are now stated.
3. **F2 envelope.** Earlier version: 40.35 mm; code 40.10 mm. Y 36.95 mm and the
   clearances match.
4. **A09 mass decomposition.** Earlier version: 5.10 kg/m² raw panel, 1.80 kg/m² bus
   credit, 0.24 kg/m² cabling credit. Code: 3.85 kg/m² panel, 0.85 kg/m²
   credit, net 3.458 kg/m². The earlier version's decomposition contradicts its own
   net figure (5.10×1.08+0.15−1.80−0.24 = 3.618, not 3.458).
5. **Leaderboard table.** The earlier version's table had stale Al₂O₃ values for nine
   arms, wrong MMOD cells for A01 (52.97% vs 69.65%), A06 (78.57% vs
   76.08%), A08 (99.90% vs 68.28%), and wrong A08 coupled/total/scenes/$.
   The executed CSV in `evidence/` is authoritative.
6. **Multi-scale table (1 kW, 1,000 kW).** All six earlier-version values differ from
   the code. Executed: 1 kW A04 (35.049 kg/kW, $15,218.84), A09 (27.192,
   $11,148.63), A10 (26.808, $11,017.48); 1,000 kW A04 (32.669, $14,356.59),
   A09 (25.186, $10,477.62), A10 (24.904, $10,383.77).
7. **Launch-sensitivity table.** Earlier version, $500/kg: A04 $7,417.30, A09
   $5,049.70. Executed: $6,516.72 / $4,900.52. Earlier version, $100/kg: A04
   $4,580.70, A10 $2,732.00. Executed: $3,319.90 / $2,654.83.
8. **Stress-case replay.** Earlier version: A06 15.654 kg/kW, 56.60% MMOD; A09/A10
   3.553 vs A04 9.826 (−63.84%); A10 $8,912.40/kW-yr. Executed: A06 13.164,
   61.89%; A04 8.73, 98.42%; A10 3.346, 99.80%; reduction 61.7%. The replay
   computes no cost, so the $8,912.40 figure is dropped; A09 is not
   evaluated in the replay (A10 is the selected arm).
9. **Round-progression narrative strings.** The code itself contained stale
   hardcoded text (5.149 kg/kW for A04; 2.509 kg/kW / −51.3% / 98.7% for
   A09; $1,419 vs $10,837; 3.79×/6.91×). The strings are now computed from
   the results and cannot go stale again.
10. **Final-disposition strings.** "21.3% MMOD hazard" (executed 23.9%),
    "2.1× even at $100/kg" (executed 1.89× vs best orbital), "20.2×"
    (executed 20.25×), "−83.7% Al₂O₃" (executed −84.05%). All now computed.
11. **C3 asymmetry (disclosure).** The orbital branch applies a 0.78
    space-to-ground gateway duty factor to Regime C3; the terrestrial branch
    does not. Without it, orbital C3 values would be 1.28× higher and the
    A11/A10 ratio 7.58× rather than 9.72×.
12. **C1 asymmetry (disclosure).** The terrestrial branch applies no
    downlink gate factor. If A11 were gated like orbital (compression 1.0 →
    gate 0.12), A11 scenes/$ would be 0.019 and the A10/A11 ratio 25.5×
    rather than 3.06×.

## Sensitivity (recomputed by `run_sensitivity_analysis()`)

- **60% thermal-mass claim:** robust to any single benefit failing (ΔT 18 K
  → 54.1%; credit 0 → 50.2%; density 5.10 → 44.4%; PDN 0.095 → 57.0%).
  Worst case (all benefits removed) → 19.3%. Most sensitive single input:
  panel areal density. With JPL bus masses (PV 14.9 + storage 7.0 kg/kW),
  A09 total rises to 30.94 kg/kW (+21%), cost $12,403 (vs $10,596).
- **3.06× scenes/$ claim:** highly sensitive to assigned inputs. Multiplier
  5.80 → 2.0 gives 1.05× (parity); compression 160 → 8 gives 1.32×; both
  worst → 0.46× (terrestrial wins). A11 multiplier 0.5 → 1.35×; 1.0 → 0.67×.
  Breakevens: useful-scene multiplier ≈ 1.90; compression ratio ≈ 4.3×.

## Model assumptions disclosed in the paper

- Nominal compute density 20,000 TFLOPS/kW (20 TFLOPS/W), ~9–14× current
  H100/B200-class hardware. Absolute TFLOPS-yr/$ scales with it; ratios do not.
- OHP effective conductivity does NOT enter the model. The thermal advantage
  comes only from areal density + junction-to-radiator ΔT (8.2 K vs 18 K).
- LDR 18.5%/yr droplet escape and 0.008 rad/s² slew are narrative, not coded
  physics (18.5% is an assigned input).
- A09 hardware cost $7,800/kW is modeled cheaper than incumbent A04
  $8,900/kW despite being novel. At $8,900/kW the mass claim is unchanged
  but A09 cost rises to $10,841/kW-yr.
- The model's power+thermal floor (19.64 kg/kW) is well below JPL's
  29.4 kg/kW — the model is more optimistic than its cited reference on bus mass.
- Environmental ledger: black carbon 0.042 kg per kg launched payload and
  Al₂O₃ = 1.889 kg per kg aluminum assume complete ablation and oxidation of
  all aluminum (an upper bound). Ferreira et al. 2024 model ~0.12 kg Al₂O₃
  per kg of satellite. Barker et al. 2026 report ~20 t black carbon per
  Falcon 9 launch — on a per-launched-kg basis substantially higher than the
  model's 0.042 kg/kg, so the ledger's black-carbon figures should be read
  as a lower bound. Radiative-forcing multiplier is flagged UNKNOWN.

## What was withdrawn

The 8S/2P electrical description; the earlier version's leaderboard, multi-scale, and
launch-sensitivity tables; the earlier version's stress-case replay numbers and the unsourced
$8,912.40/kW-yr figure; the fabricated or misattributed citations listed in
CITATIONS.md; the "1.97× even at $100/kg" claim (corrected to 1.89×). The F6/F7 defect items concern analyses outside this study and have no implementation in the released code and are not claimed as closed here. Nothing else was withdrawn:
all twelve architecture evaluations, the F1–F5/F8 repairs, the sensitivity
results, and the split-regime conclusion stand on executed code.
