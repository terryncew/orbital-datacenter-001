# References — verified

Every source below was checked to exist and to say what the paper claims it
says. URLs are the primary sources consulted. Where a source was found to be
misattributed or fabricated in an earlier version, it is listed under
"Removed" with the reason — the paper does not cite it.

## Cited sources

1. **Turyshev, S. G. (JPL/Caltech), "Orbital Data Centers: Spacecraft
   Constraints and Economic Viability", arXiv:2604.27197 (29 Apr 2026).**
   https://arxiv.org/abs/2604.27197
   Supports: 1 MW anchor — PV 5,640 m², radiator 2,500 m², 29.4 kg/kW for
   PV + storage + radiator; 34–59 kg/kW total; $250–$1,000/kg combined
   launch + build budget; regimes C1/C2/C3. The decomposed sub-masses
   (14.9 t PV, 7.5 t radiator, 7.0 t storage) are derived arithmetically
   from the abstract and are cited as derived, not quoted.

2. **Agüera y Arcas, Beals et al. (Google), "Towards a future space-based,
   highly scalable AI infrastructure system design" (Project Suncatcher),
   2025; arXiv:2511.19468; Joule, 1 Oct 2026.**
   https://services.google.com/fh/files/misc/suncatcher_paper.pdf
   Supports: 81-satellite cluster, 1 km radius, 650 km dawn–dusk
   sun-synchronous orbit; Trillium v6e TPU radiation testing (67 MeV proton
   beam; HBM irregularities after 2 krad(Si); all other tests to 15
   krad(Si)); DWDM free-space optical links (800 Gbps unidirectional /
   1.6 Tbps bidirectional bench demonstrator); 4× Trillium TPU prototype
   launched 1 Oct 2026 on SpaceX Transporter-18.
   Does NOT support: any thermal design. The paper names no bus class, no
   constant-conductance heat pipe, no facesheet material, and no TIM type.
   Architecture A02 is a modeled reference, not the Suncatcher design.

3. **SpaceX, SEC Free Writing Prospectus (filed 9 Jun 2026, Reg. No.
   333-296070), CFO Bret Johnsen interview and Musk/Dahl/Huot conversation.**
   https://www.sec.gov/Archives/edgar/data/1181412/000162828026041761/fwp_cfointerview.htm
   Supports: AI1 first design — 150 kW peak / 120 kW sustained power;
   ~110 m² deployable liquid radiator at 1,400 W/m² (both sides combined);
   pumped liquid radiator with redundant pump loops (ammonia assessed).
   The S-1 itself warns orbital compute "may not achieve commercial
   viability". Later reporting cites a revised 175 kW average / 250 kW peak
   Vera Rubin variant; the paper cites the June 2026 figures as the June
   design, not a stable specification.

4. **Planet Labs, "Planet Successfully Runs AI in Space" (2026).**
   https://investors.planet.com/news/news-details/2026/Planet-Successfully-Runs-AI-in-Space/default.aspx
   Supports: Pelican-4, 25 Mar 2026, NVIDIA Jetson Orin onboard object
   detection at 80% accuracy on raw imagery; Pelican-12 launched 20 Oct
   2026 carrying a Jetson; Tanager hyperspectral, 426 bands at 30 m
   (Tanager-2 launched 1 Oct 2026).

5. **Lupu et al., "Learning in Orbit: Onboard Training and Closed-Loop
   Attitude Control with a Thermal Segmentation Model on a Spacecraft",
   arXiv:2610.19122 (13 Oct 2026).**
   https://arxiv.org/abs/2610.19122
   Supports: onboard training and inference on a 6U CubeSat (NVIDIA Jetson
   TX2 NX), closed-loop attitude control tracking the Moon, 12 experiments
   over ~1 year. A Caltech/Aerospace demonstration — NOT a Planet paper.
   The paper does not group it with Planet.

6. **ICEF, "Space-Based Data Centers Roadmap: The Case for Caution",
   working paper, November 2026 (Sandalow et al.).**
   https://icef.go.jp/wp-content/themes/icef_new/pdf/roadmap/2026/ICEF%20SBDC%20Roadmap%20Findings%20and%20Recommendations%20Nov%202026.pdf
   Supports: maintaining a fleet with 10% of projected 2030 AI data-center
   demand would require at least 700 Starship-sized launches per year (2 per
   day) in perpetuity. Working paper, not peer-reviewed.

7. **U.S. Government Accountability Office, "Science & Tech Spotlight:
   Data Centers in Space", GAO-26-109012 (April 2026).**
   https://www.gao.gov/products/gao-26-109012
   Supports: space does not cool hardware efficiently; cooling at
   data-center scale unproven; solar arrays for large facilities would
   exceed any launched or assembled as of April 2026. A Spotlight, not an
   audit product, subject to revision.

8. **ThermAvant Technologies, oscillating heat pipe (OHP) product
   documentation and catalogue.**
   https://www.thermavant.com/oscillating-heat-pipes
   https://www.thermavant.com/news/ohp-form-factors-heat-spreaders-transporters-and-radiators
   Supports: OHP heat spreaders, transporters, and heat sinks at TRL 9;
   **OHP satellite radiators at TRL 7** (not 9); structural OHP panels at
   1.6 g/cm³ effective density (Al-6061/Ti construction); first flight 2017
   (ASETS-II, X-37B); >10 million on-orbit operating hours (Apr 2026).
   Does NOT support: ">1,000 units on orbit", a 2,000–10,000 W/m-K range
   for the structural radiator, or a Bond-number < 2 qualification
   criterion — none of these were found in ThermAvant material.

9. **Sharma, S. P., "Impact of Spaceflight on Earth's Atmosphere: Climate,
   Ozone, and the Upper Atmosphere", NASA/TM−20240013276 (Oct 2024).**
   https://ntrs.nasa.gov/api/citations/20240013276/downloads/NASA-TM-20240013276-V6.pdf
   Supports: launch black carbon / NOx / H₂O and re-entry alumina as
   stratospheric pollutants; launch tonnage rising 3,500 → >30,000 t/yr by
   2040; re-entry flux 1,000 → >30,000 t/yr.

10. **Revell, L. E. et al., "Near-future rocket launches could slow ozone
    recovery", Communications Earth & Environment (2025).**
    https://pmc.ncbi.nlm.nih.gov/articles/PMC12148926/
    Supports: ambitious scenario (2,040 launches/yr) → −0.29% annual-mean
    near-global total column ozone in 2030, Antarctic spring −3.9%;
    conservative scenario (884/yr) → −0.17%; ozone loss driven by chlorine
    from solid motors and black carbon; alumina alone has little impact on
    ozone in the quantities modeled.

11. **Barker, C., Marais, E. et al., "Radiative Forcing and Ozone Depletion
    of a Decade of Satellite Megaconstellation Missions", Earth's Future
    (2026), DOI 10.1029/2025EF007229.**
    Supports: ~870 tonnes black carbon/yr by 2029; ~20 tonnes black carbon
    per Falcon 9 launch; black carbon 540× more potent per unit mass than
    surface soot; 2.5–3 year residence. Authors are at UCL, not TU Delft.

12. **Ferreira et al., "Re-entry alumina" modelling, Geophysical Research
    Letters (2024).**
    Supports: a 250 kg satellite at 30% aluminum with ~32% of aluminum
    oxidised yields just under 30 kg alumina — ~0.12 kg per kg of satellite.
    Cited as the realistic reference against the model's complete-oxidation
    upper bound (1.889 kg Al₂O₃ per kg aluminum).

13. **Presler, A. F., Coles, C. E., Diem-Kirsop, P., & White, K. A.,
    "Liquid droplet radiator program at the NASA Lewis Research Center"
    (1985).** https://ntrs.nasa.gov/citations/19870035127
    Also: Hertzberg et al., N93-1909 (NTRS 19930007720).
    Supports: the liquid droplet radiator concept (droplets sprayed, radiate,
    collected and recycled; ~100 µm droplets; 10–100× power-to-mass advantage
    claimed over solid radiators). Replaces the fabricated TM-88908 citation.

14. **JAXA SDS-4 / IHTC-17 2023 review, "Toward LEO Applications: The
    Scientific Journey of the Space Pulsating Heat Pipe".**
    https://arxiv.org/pdf/2312.11055
    Supports: flown pulsating heat pipes — JAXA SDS-4 (2012–), ISS Space PHP
    consortium (17 parabolic-flight campaigns, 3 sounding rockets),
    ASETS-II on X-37B (780 days), ACT pulsating heat pipes (ISS 2017).

15. **Advanced Cooling Technologies (ACT), honeycomb radiator panels;
    Beyond Gravity, thermo-structural radiator panels.** (Vendor catalogues.)
    Supports: the nearest prior art for structure + radiator + embedded heat
    pipe in one panel — ACT aluminum honeycomb sandwich panels serving as
    spacecraft structural shells and radiators with embedded CCHPs; Beyond
    Gravity panels up to 6 kW each, up to 18 m², with optional embedded heat
    pipe networks. Neither integrates an electrical power bus as a fourth
    function, and neither uses an oscillating heat pipe as the primary-structure
    load path.

## Removed — do not cite

- **NASA TM-88908 as a liquid-droplet-radiator source: fabricated.**
  TM-88908 is Schmidt, Moore, Wood & Steinke, "Supersonic Through-Flow Fan
  Design" (1987) — a supersonic aircraft fan paper, unrelated to radiators.
  Replaced by references 13 above.
- **Black-carbon factors "~15–25 kg/t payload (CH₄/LOX), ~110–140 kg/t
  (RP-1/LOX)" and alumina "0.45–0.65 kg per kg dry bus/radiator mass":
  not found in any cited source and contradicted** (Ferreira et al. give
  ~0.12 kg/kg). Removed; the paper uses Revell et al. and Barker et al.
  aggregates instead, and states the model's own ledger factors as model
  assumptions.
- **"TU Delft, Earth's Future 2026" attribution: wrong.** The 2026 Earth's
  Future paper on this topic is Barker/Marais, UCL (reference 11). A
  separate TU Delft paper could not be verified from this environment and is
  not cited.
- **Suncatcher thermal stack (Pelican-class buses, Al-NH₃ CCHP,
  carbon-composite facesheet radiators, conformable multi-spring TIM,
  Trillium TDP 250–350 W) and the "10 km benchtop demo": not in the Google
  paper.** The "10 km" figure is a theoretical near-field link distance for
  a 10 cm aperture, not a demo. Architecture A02 is labeled a modeled
  reference throughout.
- **SpaceX AI1 as "passive solid-conductor / heat-pipe" thermal:
  contradicted.** Sources describe a pumped liquid radiator. Architecture
  A03 is modeled as a pumped/hybrid arm.
- **Planet "20×–100× downlink shortfall": unsourced.** No Planet source
  states it. Removed.
- **ThermAvant radiator "TRL 9", ">1,000 units on orbit", "2,000–10,000
  W/m-K", "Bond number < 2": unsupported or contradicted** (see reference 8).
