# Integrated Structural Thermal Management for Orbital Computing: A Comparative Engineering and Economic Study

**Status: computational, AI-assisted research.** All results in this paper
are modeled outputs of the accompanying simulation code. No physical
thermal-vacuum validation has been performed. The TVAC coupon test described
in Section 4.7 is the falsification gate for the central thermal claim.
Nothing in this paper is demonstrated hardware performance.

*Reproduction: `python3 simulation/run_reproduction.py` regenerates every
number, figure, and table in this paper from the code. Evidence, leaderboard,
and manifest: `evidence/`, `SHA256SUMS.txt`.*

## Abstract

We compare twelve orbital and terrestrial computing architectures at 1, 150,
and 1,000 kW across two workload regimes — general AI for terrestrial users
(Regime C3) and space-native edge triage of Earth-observation, SAR, and
hyperspectral data (Regime C1/C2) — using a Stefan–Boltzmann radiative model
with a coupled junction-to-radiator thermal chain, a Grün-flux micrometeoroid
survival model, and a five-year lifecycle cost model including launch and
replenishment. A monolithic structural oscillating-heat-pipe panel (MS-OHP-SP,
A09) that combines radiator, heat pipe, and power bus in one load-bearing
sandwich cuts coupled thermal mass by 60.0% against the conventional
lightweight radiator incumbent (2.725 vs 6.817 kg/kW at 150 kW), and its
sparse-triage variant (A10) delivers 3.06× more actionable space-native
scenes per dollar than terrestrial downlink. But terrestrial clean-grid
compute still wins general AI by 9.72× on delivered TFLOPS-yr/$, and remains
cheaper (1.89×) even at $100/kg launch. The split verdict is the finding:
orbital computing is not a general data-center strategy; it is a niche
strategy for work whose data is already in orbit. The 60% thermal claim is
robust to any single assumed benefit failing; the 3.06× claim is fragile,
depending on two assigned inputs with no cited measurement, and we publish
its breakevens. The decisive physical test — a thermal-vacuum coupon
measurement of the microgravity oscillation startup threshold — is
outstanding and could reject the central claim.

## 1. Introduction

The orbital data-center proposition is simple to state and hard to settle:
space offers continuous sunlight and a cold sink, but everything launched
must be paid for by mass, and the hardware still needs power, storage, and
shielding. Two recent analyses frame the bounds. Turyshev (JPL/Caltech)
finds a 1 MW orbital anchor needs 5,640 m² of photovoltaics and 2,500 m² of
radiator, at 29.4 kg/kW for power, storage, and radiator and 34–59 kg/kW
total, and concludes space-native processing (C1) and communications-integrated
edge compute (C2) are credible early while general terrestrial compute (C3)
closes only for low communication intensity, high utilization, long life, and
very low cost [1]. The ICEF roadmap finds that supplying 10% of projected
2030 AI data-center demand from orbit would require at least 700
Starship-sized launches per year in perpetuity [6]. The U.S. GAO notes that
space does not cool hardware efficiently and that cooling at data-center
scale is unproven [7]. Google's Project Suncatcher has flown a 4-TPU
prototype (1 Oct 2026, Transporter-18) but publishes no thermal design [2];
SpaceX's AI1 is described in SEC filings as a 150 kW peak design with a
pumped liquid radiator [3].

This study asks a narrower, answerable question: given a fixed thermal
model, which architectures win on mass, cost, and survival, at which scales,
and for which workload — and how sensitive are the answers to the inputs?
We do not build hardware. We model twelve architectures, reject two, invent
one, and report the split verdict with its sensitivities and its falsifier.

## 2. Methods

### 2.1 Model

The model is `simulation/orbital_thermal_study.py` (standard library only).
All equations below are implemented there; the paper states them so a reader
can check the code against the claims.

**Radiative flux.** Two-sided Stefan–Boltzmann emission with view factor,
emissivity, background temperature, and absorbed environmental flux:

$$q = 2 \cdot v_f \cdot \varepsilon \cdot \sigma \cdot (T_{rad}^4 - T_{bg}^4) - q_{abs}$$

with σ = 5.670374419×10⁻⁸ W/m²K⁴, T_bg = 220 K, q_abs = 75 W/m². The
**screening convention** fixes T_rad = 80 °C, ε = 0.85, v_f = 1.0
(flux 1,198.6 W/m²). The **coupled calculation** sets T_rad = T_junction −
ΔT_chain with end-of-life emissivity (BOL minus five-year loss, floored at
0.50) and v_f = 0.96, and uses total waste heat (IT power plus PDN and pump
losses). Radiator area is waste heat divided by flux; thermal mass is area
times net effective areal density, floored at 2.5 kg/m²:

$$\rho_{net} = \max(2.5,\ \rho_{panel}(1+f_{anc}) + \rho_{support} - \rho_{credit})$$

**Spacecraft mass.** Total launched mass per kW is coupled thermal mass plus
PV/PMAD, eclipse storage, and bus/ADCS/propulsion/shielding/communications,
with a scale overhead of 1.28× at ≤2 kW, 1.0× at ≤200 kW, and 0.94× above
200 kW. Power overhead multiplies PV and storage masses.

**Micrometeoroid survival.** Grün flux of ≥0.6 mm perforating particles,
0.018 impacts/m²/yr. Pumped loops (fewer than 0.2 compartments/m²) survive
as exp(−flux × 0.12 × 0.18 × reference area); compartmentalized designs
survive as 1 − flux/compartments per m². The liquid droplet radiator (A08)
additionally loses fluid at an assigned 18.5%/yr (droplet retention floored
at 0.15). Delivered compute years are mission years × MMOD survival ×
droplet retention × exp(−hazard × years / 2) × 0.955 (SEU checkpoint duty).

**Economics.** Five-year cost per kW is (hardware + launch × total mass)
times a replenishment multiplier 1/max(MMOD × droplet × hardware survival,
0.35), plus five-year operations and energy. Cost per delivered compute-year
divides by delivered years. Launch is $1,500/kg baseline, swept to $100/kg.

**Workload metrics.** Regime C3 (general AI) is delivered TFLOPS-yr per
dollar at a nominal 20,000 TFLOPS/kW (20 TFLOPS/W). Regime C1/C2
(space-native triage) is actionable scenes per dollar:
1000 × useful-scene multiplier × downlink gate × delivered years / total
cost, with the downlink gate min(1, 0.12 × log₂(1 + compression)).

**Two asymmetries, disclosed.** (i) The orbital C3 branch applies a 0.78
space-to-ground gateway duty factor; the terrestrial branch does not. Without
it, orbital C3 values would be 1.28× higher and the A11/A10 ratio 7.58×
rather than 9.72×. (ii) The terrestrial C1 branch applies no downlink gate;
A11's 0.22 multiplier is described as already encoding the downlink penalty.
If A11 were gated like orbital (compression 1.0 → gate 0.12), A11 scenes/$
would be 0.019 and the A10/A11 ratio 25.5× rather than 3.06×. Both ratios in
this paper are the as-modeled values; the symmetric values are stated here
so the reader can see what the asymmetries buy.

**Environmental ledger.** Launch black carbon at 0.042 kg per kg launched
payload; re-entry alumina at 1.889 kg per kg aluminum (complete ablation and
oxidation — an upper bound; Ferreira et al. model ~0.12 kg per kg of
satellite [12]); lifecycle CO₂ at 0.012 t/MWh (clean grid) or 0.018 t/MWh.
The stratospheric radiative-forcing multiplier is recorded as UNKNOWN, not
estimated.

### 2.2 Architectures

Twelve arms. A01–A08 and A11–A12 are baselines, references, and controls;
A09 is the Round 2 invention; A10 is the Round 3 invention. Reference arms
A02 and A03 are **modeled references informed by public parameters, not
measured performance of any company's hardware**: A02 uses the Suncatcher
paper's orbital parameters (81 satellites, 650 km) with an assumed Al–NH₃
CCHP thermal stack the paper does not publish; A03 uses the AI1 power
figures from the June 2026 SEC filing with a pumped liquid radiator. The
full parameter set is in the code; the decisive assigned inputs are:

| Arm | Cooling | Panel (kg/m²) | ΔT (K) | Cells/m² | Scene mult. | Compr. | HW ($/kW) |
|---|---|---|---|---|---|---|---|
| A01 Heritage ISS pumped loop | pumped fluid | 14.00 | 22.0 | 0 | 1.00 | 1 | 18,500 |
| A02 Modeled Suncatcher-class | CCHP heat pipe | 8.00 | 20.5 | 4 | 1.25 | 8 | 11,200 |
| A03 Modeled SpaceX AI1 | CCHP/LHP hybrid | 6.00 | 16.5 | 6 | 1.20 | 6 | 8,400 |
| A04 Conventional lightweight CCHP | lightweight CCHP | 5.00 | 18.0 | 8 | 1.25 | 8 | 8,900 |
| A05 Isogrid + CCHP prior art | isogrid CCHP | 6.80 | 17.5 | 6 | 1.25 | 8 | 9,200 |
| A06 Naive pumped structural panel | pumped MIF-PWS | 9.00 | 11.0 | 0 | 1.25 | 8 | 12,800 |
| A07 Modular passive LHP | modular LHP | 6.20 | 15.0 | 12 | 1.25 | 8 | 9,800 |
| A08 Liquid droplet radiator | droplet stream | 1.80 | 19.0 | 0 | 1.00 | 4 | 15,400 |
| A09 MS-OHP-SP (invention) | structural OHP | 3.85 | 8.2 | 64 | 1.25 | 8 | 7,800 |
| A10 Sparse edge + MS-OHP-SP | structural OHP | 3.85 | 8.2 | 64 | 5.80 | 160 | 8,100 |
| A11 Terrestrial clean-grid dry cool | dry cooler | — | — | — | 0.22 | 1 | 3,600 |
| A12 Terrestrial solar + LiFePO₄ | dry cooler | — | — | — | 0.22 | 1 | 6,400 |

A09's 3.85 kg/m² panel, 0.85 kg/m² structural bus credit, 8.2 K
junction-to-radiator drop, and 64 independent cells/m² are the invention's
four benefits; Section 3.6 tests each one. A09's $7,800/kW hardware cost is
modeled *cheaper* than the A04 incumbent's $8,900/kW despite being novel; the
sensitivity section prices that assumption. A10 adds event-gated sparse
triage (5.80× useful-scene multiplier, 160:1 compression) and a demisable
low-aluminum bus (12% Al vs 22% for A09, 55% for A04).

### 2.3 Procedure

Three rounds. Round 1 screened six arms and adopted the conventional
lightweight radiator (A04) as baseline, rejecting the naive pumped
structural panel (A06) and the liquid droplet radiator (A08). Round 2
invented the MS-OHP-SP panel (A09) on the A04 baseline. Round 3 split the
regimes: terrestrial for C3, sparse orbital edge for C1/C2. A held-out stress
case (250 kW, β=75°, 7-year mission, absorbed flux 210 W/m², junction limit
92 °C) tested generalization to an untuned configuration. Sensitivity analysis
re-evaluated the model with one assigned input changed at a time
(`run_sensitivity_analysis()` in the code).

### 2.4 Coupon defect repairs (F1–F5, F8)

An earlier terrestrial power-delivery package carried eight defects; the
implemented repairs in `simulation/repair_coupon.py` are: **F1**, a 614.4 W
electrical error (16 parallel 15.0 Ω resistors across 24.0 V) replaced by a
4-parallel × 4-series bridge of 11.52 Ω SMD 2512 resistors — 50.000 W matrix
dissipation at its bus terminals at 24.0 V SELV (49.87 W total draw and
49.74 W matrix dissipation including the 0.020 Ω fuse + 0.010 Ω bimetal
series protection, 3.109 W/resistor); **F2**, colliding 15.76 mm TO-247
packages (63.04 mm span on a 45.0 mm envelope) replaced by SMD 2512 heaters
on an 11.25 mm pitch (40.10 mm span, 0 collisions); **F3**, a non-manifold
STEP file replaced by a true AP214 MANIFOLD_SOLID_BREP model (10 solids, 60
faces, Euler–Poincaré V−E+F=2 on every shell) for the 45×45 mm coupon and the
100×100×2.6 mm inert MS-OHP-SP TVAC coupon; **F4**, hydraulic channel count
corrected to 30 per header (60 total, 42.0 mm length; velocity 0.794 m/s vs
0.397 m/s, Re 314, Δp 6.53 kPa, within the 3.5 m/s erosion and 45 kPa
limits); **F5**, a 2D sheet approximation replaced by a true 3D finite-volume
Laplace solver (16×16×8 = 2,048 cells; Joule loss 8.016 W lateral FR4,
1.891 W coaxial bolted posts, 1.638 W through-substrate vias at 1,280 A);
**F8**, Stage-0 hardware classified INERT MACHINABILITY & TVAC CONTACT
COUPON ONLY — zero energization at 50 W or 50 A without external PE/EHS
signoff, fused 2.5 A limit, 85 °C hardware cutout. Two items from the earlier list (F6 and F7) concern analyses outside this study and have no implementation in the released code; they are not claimed as closed by this package.

## 3. Results

### 3.1 Twelve-architecture leaderboard (150 kW)

| Arm | Screen 80 °C (kg/kW) | Coupled (kg/kW) | Total (kg/kW) | MMOD 5-yr | Delivered (yr/5) | Cost ($/kW-yr) | C3 (TFLOPS-yr/$) | C1 (scenes/$) | Al₂O₃ (kg) |
|---|---|---|---|---|---|---|---|---|---|
| A01 Heritage pumped loop | 17.655 | 26.248 | 59.21 | 69.65% | 2.689 | 71,760.45 | 0.2174 | 0.0017 | 20,258.54 |
| A02 Suncatcher-class (modeled) | 10.446 | 13.869 | 42.85 | 97.75% | 4.309 | 19,843.36 | 0.7862 | 0.0240 | 8,343.14 |
| A03 AI1 (modeled) | 6.758 | 8.106 | 34.00 | 98.50% | 4.385 | 15,112.40 | 1.0323 | 0.0268 | 6,083.72 |
| **A04 Incumbent CCHP** | **5.423** | **6.817** | **33.09** | **98.88%** | **4.446** | **14,508.75** | **1.0752** | **0.0328** | **5,537.90** |
| A05 Isogrid + CCHP | 6.975 | 7.560 | 33.23 | 98.50% | 4.418 | 14,815.89 | 1.0529 | 0.0321 | 6,614.45 |
| A06 Naive pumped structural | 9.345 | 10.500 | 37.55 | 76.08% | 2.886 | 40,343.10 | 0.3867 | 0.0118 | 7,919.99 |
| A07 Modular LHP | 6.687 | 7.946 | 34.32 | 99.25% | 4.497 | 14,836.64 | 1.0515 | 0.0320 | 5,988.78 |
| A08 Liquid droplet radiator | 2.662 | 4.173 | 32.95 | 68.28% | 0.837 | 224,585.57 | 0.0695 | 0.0012 | 13,337.02 |
| **A09 MS-OHP-SP** | **3.594** | **2.725** | **25.54** | **99.86%** | **4.627** | **10,596.04** | **1.4722** | **0.0449** | **1,642.91** |
| **A10 Sparse edge + MS-OHP-SP** | **3.594** | **2.725** | **25.24** | **99.86%** | **4.639** | **10,495.60** | **1.4863** | **0.4861** | **883.39** |
| **A11 Terrestrial clean-grid** | — | — | — | 100% | 4.876 | **1,384.33** | **14.4474** | 0.1589 | 0.0 |
| A12 Terrestrial solar + battery | — | — | — | 100% | 4.864 | 1,511.16 | 13.2349 | 0.1456 | 0.0 |

A08 is the cautionary row: the lightest coupled thermal mass of any orbital
arm (4.173 kg/kW) with the worst survival (68.28%) and a cost 15× the
incumbent, because droplet escape and replenishment dominate. A06 loses on
every axis that matters: +72.31% screen mass vs A04, 76.08% MMOD survival,
2.78× the cost.

### 3.2 The rounds

**Round 1** rejected A06 (9.345 kg/kW screen, 10.500 coupled, 76.08% MMOD
survival, $40,343.10/kW-yr) and A08, and adopted A04 (5.423 screen, 6.817
coupled, 98.88% survival, $14,508.75/kW-yr). **Round 2** invented A09:
3.458 kg/m² net areal density (below the 5.083 kg/m² break-even), 3.594
kg/kW screen (−33.7% vs A04), 2.725 kg/kW coupled (−60.0%), 25.54 kg/kW
total spacecraft, 99.86% MMOD survival at 64 cells/m². **Round 3** split the
regimes: for C3, A11 at $1,384.33/kW-yr (14.447 TFLOPS-yr/$) beats the best
orbital arm A10 ($10,495.60/kW-yr, 1.486 TFLOPS-yr/$) by 9.72×; for C1/C2,
A10 delivers 0.486 actionable scenes/$, 3.06× terrestrial A11 (0.159),
14.82× conventional orbital A04 (0.033), and 20.25× the modeled
Suncatcher-class A02 (0.024), while cutting re-entry Al₂O₃ by 84.05% vs A04.

### 3.3 Multi-scale summary

| Scale | A04 total (kg/kW) / cost | A09 total / cost | A10 total / cost | A11 cost |
|---|---|---|---|---|
| 1 kW | 35.049 / $15,218.84 | 27.192 / $11,148.63 | 26.808 / $11,017.48 | $1,384.33 |
| 150 kW | 33.089 / $14,508.75 | 25.540 / $10,596.04 | 25.240 / $10,495.60 | $1,384.33 |
| 1,000 kW | 32.669 / $14,356.59 | 25.186 / $10,477.62 | 24.904 / $10,383.77 | $1,384.33 |

The ranking is scale-invariant: A09/A10 beat A04 at every scale, and A11
beats every orbital arm at every scale. The 1 kW penalty (35.049 vs 33.089
for A04) is the 1.28× small-bus overhead; the 1 MW benefit (32.669) is the
0.94× large-scale factor.

### 3.4 Launch-cost sensitivity (150 kW)

| Launch ($/kg) | A04 ($/kW-yr) | A09 ($/kW-yr) | A10 ($/kW-yr) | A11 ($/kW-yr) | A10 C1 advantage |
|---|---|---|---|---|---|
| 1,500 | 14,508.75 | 10,596.04 | 10,495.60 | 1,384.33 | 3.06× |
| 500 | 6,516.72 | 4,900.52 | 4,895.05 | 1,384.33 | 6.56× |
| 250 | 4,518.71 | 3,476.64 | 3,494.92 | 1,384.33 | 9.19× |
| 100 | 3,319.90 | 2,622.31 | 2,654.83 | 1,384.33 | 12.10× |

Terrestrial remains cheaper for general AI at every launch price: even at
$100/kg, the best orbital arm (A09, $2,622.31) costs 1.89× the terrestrial
arm. The C1 advantage grows as launch falls, because cheaper launch raises
the value of the scenes delivered per dollar.

### 3.5 Held-out stress case (250 kW, β=75°, 7 yr)

| Arm | Coupled (kg/kW) | Total (kg/kW) | MMOD 7-yr | Delivered (yr/7) | C1 (scenes/$) | Feasible |
|---|---|---|---|---|---|---|
| A10 Sparse edge + MS-OHP-SP | 3.346 | 25.525 | 99.80% | 6.42 | 0.6593 | Yes |
| A04 Incumbent | 8.730 | 34.582 | 98.42% | 6.05 | 0.0418 | No (mass) |
| A06 Naive pumped structural | 13.164 | 39.779 | 61.89% | 3.00 | 0.0087 | No |

The ranking generalizes to the untuned configuration: A10 remains feasible
on all flight gates (mass ≤ 28.0 kg/kW, MMOD ≥ 0.980, delivered ≥ 6.00 yr)
with a 61.7% coupled thermal-mass reduction vs A04 in the stress case.

### 3.6 Sensitivity of the headline claims

**60% thermal-mass claim (A09 vs A04).** Recomputed reduction under
single-benefit failures: ΔT 18 K → 54.1%; structural credit 0 → 50.2%;
panel density 5.10 kg/m² → 44.4%; PDN loss 0.095 → 57.0%. All four benefits
removed together → 19.3%. Most sensitive single input: panel areal density.
With JPL bus masses (PV 14.9 + storage 7.0 kg/kW vs the model's 12.1 + 4.5),
A09 total rises to 30.94 kg/kW (+21%) and cost to $12,403 (vs $10,596). At
A04's hardware cost ($8,900/kW) the mass claim is unchanged but A09 cost
rises to $10,841/kW-yr. Verdict: robust to any single failure, not to all
four at once.

**3.06× scenes/$ claim (A10 vs A11).** Useful-scene multiplier 5.80 → 2.0
gives 1.05× (parity); downlink compression 160 → 8 gives 1.32×; both worst
→ 0.46× (terrestrial wins). A11 multiplier 0.5 → 1.35×; 1.0 → 0.67×
(terrestrial wins). Breakevens: multiplier ≈ 1.90, compression ≈ 4.3×.
Verdict: fragile. The claim depends on two assigned inputs with no cited
measurement behind them, and the paper presents it as the modeled value at
assigned inputs, with the breakevens alongside. See Figure 3.

### 3.7 Environmental ledger (150 kW, 5 yr)

A10 launches 163.68 kg of black carbon and ablates 883.39 kg of Al₂O₃ over
five years, against A04's 223.87 kg and 5,537.90 kg and A02's 299.20 kg and
8,343.14 kg. A11/A12 launch nothing and ablate nothing. Two caveats: the
ledger's black-carbon factor (0.042 kg per kg launched payload) is a model
assumption, and Barker et al. report ~20 t of black carbon per Falcon 9
launch [11] — on a per-launched-kg basis substantially higher — so the
ledger's black-carbon figures should be read as a lower bound pending a
propellant-based accounting. The alumina factor (1.889 kg per kg aluminum)
assumes complete ablation and oxidation (an upper bound); Ferreira et al.
model ~0.12 kg per kg of satellite [12]. Revell et al. find alumina alone
has little impact on ozone in the quantities modeled, with chlorine from
solid motors and black carbon driving the loss [10].

## 4. Discussion

### 4.1 What the 60% claim does and does not mean

The 60.03% reduction is a coupled thermal-mass figure inside one model: same
junction limit (95 °C), same background (220 K), same absorbed flux
(75 W/m²), same MMOD environment. It comes from four modeled benefits
stacked together: a hotter radiator (+9.8 K, worth +14.8% flux from
temperature alone, +18.8% including the higher end-of-life emissivity), a
lighter panel (3.85 vs 5.00 kg/m² before credits), a structural credit
(0.85 kg/m² for deleting the separate bus skin), and a near-zero PDN loss
(0.019 vs 0.095). No single benefit carries the claim — the worst
single-failure case still gives 44.4% — but all four failing together leaves
19.3%, which is an ordinary improvement, not a breakthrough. The claim is
therefore a statement about the *combination*, and the combination is
untested in hardware. The panel areal density is the most sensitive input:
it is also the least verified, resting on a vendor catalogue density
(1.6 g/cm³ for structural OHP panels [8]) rather than a measured panel.

### 4.2 What the 3.06× claim does and does not mean

The 3.06× scenes-per-dollar advantage is the ratio of two modeled numbers,
each carrying an assigned multiplier. A10's 5.80× useful-scene multiplier
says most of what a satellite sees is not worth downlinking; A11's 0.22×
says terrestrial downlink is already the bottleneck. Neither is a
measurement. The honest statement is conditional: *if* sparse triage
delivers 5.80× more useful scenes per unit of downlink and *if* 160:1
compression holds, *then* orbital triage is 3.06× more cost-effective than
raw downlink. The breakevens (≈1.90× multiplier, ≈4.3× compression) are the
numbers a skeptic should test first. Note also the asymmetry disclosed in
Section 2.1: the ratio is 3.06× under the model's asymmetric gating and
25.5× under symmetric gating. Either way the direction holds at baseline
inputs; the magnitude does not survive degraded inputs.

### 4.3 Why terrestrial wins general AI

The C3 result is not close and does not depend on the radiator. The
non-thermal spacecraft floor — PV + eclipse storage + ADCS/shielding at
22.5 kg/kW for A09 — plus launch and replenishment overhead makes even a
zero-mass radiator more expensive per compute-year than terrestrial
clean-grid power ($1,384/kW-yr). This is the Turyshev conclusion [1]
reproduced from inside the model: general AI belongs on Earth unless launch
becomes nearly free *and* the bus-mass floor collapses. At $100/kg the best
orbital arm is still 1.89× the terrestrial cost. The negative result is the
paper's most robust finding, because it survives the most optimistic launch
price in the sweep.

### 4.4 The reference architectures are models, not products

A02 and A03 exist in this paper as parameterized references. The Suncatcher
paper publishes no thermal design [2], so A02's CCHP stack is an assumption
that could be wrong in either direction; the AI1 power figures are a June
2026 design snapshot that later reporting revises upward [3]. Treating either
arm as a company's measured performance would be a category error, and the
paper does not do so. The leaderboard's meaningful comparisons are A09/A10
against A04 (the incumbent control) and A11 (the terrestrial control), both
of which are defined inside the model.

### 4.5 The model is optimistic on bus mass

With Turyshev's bus masses (PV 14.9 + storage 7.0 kg/kW [1]) instead of the
model's (12.1 + 4.5), A09's total rises 21% to 30.94 kg/kW and its cost to
$12,403/kW-yr. The model's power-plus-thermal floor (19.64 kg/kW) sits well
below JPL's 29.4 kg/kW. Readers should treat the absolute masses and costs
as optimistic; the *rankings* are the sturdier output, because the same
optimism applies unevenly — A09's advantage narrows under JPL masses but
does not reverse.

### 4.6 Prior art and the novelty claim

Each element of the MS-OHP-SP panel exists separately and in pairs. Flown
oscillating heat pipes include JAXA SDS-4, the ISS Space PHP consortium, and
ASETS-II on X-37B [14]. The closest single prior art is ACT's honeycomb
radiator panel (structure + radiator + embedded CCHP) and ThermAvant's
structural OHP radiator (structure + radiator + OHP, TRL 7) [8, 15], with
Beyond Gravity's thermo-structural panels as a further near neighbor. The
U.S. Air Force multi-functional structure programme put power and data planes
into spacecraft structure as a concept, not as a flown radiator panel. The
novelty claim in this paper is therefore narrow and explicit: **an
oscillating heat pipe (not a CCHP) as the primary-structure load path,
combined with a structural panel and an electrical power bus in one panel**.
No single flown product combines all four functions. That is a combination
claim, not an invention-of-the-elements claim, and it is stated as such
because the elements are all prior art.

### 4.7 The falsification test

The single most important remaining test is a thermal-vacuum (TVAC) coupon
measurement of the **microgravity oscillation startup threshold** of the
structural OHP panel, with brazed-joint contact conductance as the measurable
proxy. Gates: effective in-plane conductivity k_eff ≥ 1,200 W/m·K across
horizontal (0°) and adverse-gravity (+5°) orientations in a 10⁻⁵ Torr vacuum
chamber radiated to an 80 K LN₂ cold shroud; **reject A09 if k_eff <
600 W/m·K or dryout occurs below 50 W**, and revert to A04. Geometry and
mass gate: dry mass ≤ 62% of a solid Al-6061 control coupon at identical
bending stiffness EI (±5%) under three-point bend testing; helium leak <
1×10⁻⁸ atm·cc/s at 1.5× maximum working vapor pressure. The startup
threshold is the sharper gate, because the modeled advantage rests on the
assumed 8.2 K junction-to-radiator drop, which assumes the heat pipe actually
oscillates and transports heat at panel scale in microgravity. If the coupon
shows no sustained oscillation, the 60% claim collapses regardless of the
conductivity number. Stage 0 is an inert coupon only; energized testing is on
hold pending external PE/EHS signoff.

## 5. Limitations

Labeled by category, as the results require.

**Demonstrated software behavior (executed, reproducible).** The tournament
reproduces deterministically; the 8-test suite passes in standard and `-O`
modes; the stress-case replay reproduces exactly; the F1–F5/F8 repairs verify
(netlist power, zero collisions, Euler closure, hydraulic continuity, 3D
Laplace solution). The leaderboard, multi-scale, launch-sensitivity, and
sensitivity numbers in this paper are outputs of that code.

**Modeled engineering performance (computed, not measured).** All twelve
architecture evaluations, the 60% and 3.06× headline figures, the cost
figures, the MMOD survivals, and the environmental ledger. These depend on
assigned inputs listed in Section 2.2 and on the asymmetries disclosed in
Section 2.1. The nominal compute density (20,000 TFLOPS/kW) is ~9–14×
current H100/B200-class hardware; absolute TFLOPS-yr/$ scales with it,
ratios do not. The OHP effective conductivity does not enter the model. The
LDR droplet-escape rate (18.5%/yr) is an assigned input. A09's hardware cost
is modeled below the incumbent's.

**Untested hypotheses.** That an oscillating heat pipe starts up and sustains
oscillation in microgravity at panel scale; that the brazed AlSiC/MoCu joint
achieves the assumed contact conductance; that sparse triage delivers a
5.80× useful-scene multiplier at 160:1 compression; that the 1.6 g/cm³
structural panel density is achievable with flight-qualified manufacturing.
Each is falsifiable by the test in Section 4.7 or by measurement of the
triage inputs.

**What this paper does not claim.** No flight qualification, no measured
thermal performance, no cost certainty, no environmental impact assessment
(the radiative-forcing multiplier is UNKNOWN by design), and no statement
about any company's actual hardware. An earlier version of this work contained fabricated and misattributed citations and stale tables; all are corrected or
removed, and the full corrections log is in `VERIFICATION.md`.

## 6. Conclusion

A structural oscillating-heat-pipe panel can, in the model, cut orbital
thermal mass by 60% — and it still does not make orbital data centers
competitive for general AI. The economics are decided by the bus, not the
radiator. Orbital computing earns its place only where the data is already in
orbit and the work is deciding what is worth sending down. That is a smaller
claim than the orbital data-center pitch, and it is the one the numbers
support. The next step is not more simulation. It is a coupon in a vacuum
chamber.

## References

[1] Turyshev, S. G., "Orbital Data Centers: Spacecraft Constraints and
Economic Viability", arXiv:2604.27197 (29 Apr 2026).
https://arxiv.org/abs/2604.27197

[2] Agüera y Arcas, Beals et al. (Google), "Towards a future space-based,
highly scalable AI infrastructure system design" (Project Suncatcher), 2025;
arXiv:2511.19468; Joule, 1 Oct 2026.
https://services.google.com/fh/files/misc/suncatcher_paper.pdf

[3] SpaceX, SEC Free Writing Prospectus (filed 9 Jun 2026, Reg. No.
333-296070), CFO interview and Musk/Dahl/Huot conversation.
https://www.sec.gov/Archives/edgar/data/1181412/000162828026041761/fwp_cfointerview.htm

[4] Planet Labs, "Planet Successfully Runs AI in Space" (2026).
https://investors.planet.com/news/news-details/2026/Planet-Successfully-Runs-AI-in-Space/default.aspx

[5] Lupu et al., "Learning in Orbit: Onboard Training and Closed-Loop
Attitude Control with a Thermal Segmentation Model on a Spacecraft",
arXiv:2610.19122 (13 Oct 2026). https://arxiv.org/abs/2610.19122

[6] ICEF, "Space-Based Data Centers Roadmap: The Case for Caution", working
paper, November 2026 (Sandalow et al.).
https://icef.go.jp/wp-content/themes/icef_new/pdf/roadmap/2026/ICEF%20SBDC%20Roadmap%20Findings%20and%20Recommendations%20Nov%202026.pdf

[7] U.S. Government Accountability Office, "Science & Tech Spotlight: Data
Centers in Space", GAO-26-109012 (April 2026).
https://www.gao.gov/products/gao-26-109012

[8] ThermAvant Technologies, oscillating heat pipe product documentation and
catalogue. https://www.thermavant.com/oscillating-heat-pipes

[9] Sharma, S. P., "Impact of Spaceflight on Earth's Atmosphere: Climate,
Ozone, and the Upper Atmosphere", NASA/TM−20240013276 (Oct 2024).
https://ntrs.nasa.gov/api/citations/20240013276/downloads/NASA-TM-20240013276-V6.pdf

[10] Revell, L. E. et al., "Near-future rocket launches could slow ozone
recovery", Communications Earth & Environment (2025).
https://pmc.ncbi.nlm.nih.gov/articles/PMC12148926/

[11] Barker, C., Marais, E. et al., "Radiative Forcing and Ozone Depletion
of a Decade of Satellite Megaconstellation Missions", Earth's Future (2026),
DOI 10.1029/2025EF007229.

[12] Ferreira et al., re-entry alumina modelling, Geophysical Research
Letters (2024).

[13] Presler, A. F., Coles, C. E., Diem-Kirsop, P., & White, K. A., "Liquid
droplet radiator program at the NASA Lewis Research Center" (1985).
https://ntrs.nasa.gov/citations/19870035127 ; Hertzberg et al., N93-1909
(NTRS 19930007720).

[14] JAXA SDS-4 / IHTC-17 2023 review, "Toward LEO Applications: The
Scientific Journey of the Space Pulsating Heat Pipe".
https://arxiv.org/pdf/2312.11055

[15] Advanced Cooling Technologies, honeycomb radiator panels; Beyond
Gravity, thermo-structural radiator panels (vendor catalogues).

## Appendix A. Corrections log (summary)

An earlier version's report text disagreed with its own executed code in twelve places; all are corrected in this paper and in the code. The full log
with before/after values is in `VERIFICATION.md`. Headlines: the F1 network
is 4-series/4-parallel, not 8-series/2-parallel; the "50.000 W exact" figure
is the matrix at its bus terminals (49.87 W total draw with protection); the
leaderboard, multi-scale, and launch-sensitivity tables are replaced with
executed values; the stress-case replay numbers are replaced with the executed replay values (A06 13.164, A04 8.73, A10 3.346 kg/kW coupled; 61.7% reduction); the
"1.97× even at $100/kg" claim is corrected to 1.89×; the fabricated
TM-88908 LDR citation, the unsourced emission factors, the wrong "TU Delft"
attribution, the unsupported ThermAvant TRL 9 / ">1,000 units" / k_eff range,
the Suncatcher thermal stack, the "passive" AI1 description, and the
"20×–100× downlink" figure are all removed or replaced. The F6/F7 defect
items have no implementation in the released code and are not claimed.

## Appendix B. Reproduction

```sh
python3 -m venv .venv
.venv/bin/pip install -r simulation/requirements.txt
python3 simulation/run_reproduction.py
```

This regenerates the tournament, sensitivity analysis, stress replay, figures
1–3, CAD drawings, evidence JSON, leaderboard CSV, and `SHA256SUMS.txt`,
runs the 8-test suite in standard and `-O` modes, and verifies
byte-determinism. Verified environment: Python 3.12.3, matplotlib 3.8.4,
Pillow 10.2.0, numpy 1.26.4, scipy 1.11.4 (see
`simulation/requirements.txt`).
