# Research summary — in plain language

## The question

Should we put AI data centers in orbit? Two ideas compete. One: space is
cold and sunny, so orbital computers could run cooler and cheaper than
Earth-bound ones. Two: launching anything is expensive, and the hardware
still needs power, batteries, and shielding — so Earth wins anyway. We tested
both, with numbers, across 12 different designs.

## What we did

We built a physics-and-economics model (not hardware) of 12 ways to run
compute in orbit or on the ground, at three sizes (1 kW, 150 kW, 1 MW), and
scored them on mass, cost, survival against micrometeoroids, and two jobs:
general AI for people on Earth, and triage of satellite imagery already in
orbit. We also designed a small test coupon — a 10 cm metal plate — that
would be the first physical check of the most important assumption.

## What we found

- **A new radiator design helps a lot, on paper.** A panel that is also the
  structure, the heat pipe, and the power bus cuts the thermal mass by 60%
  compared with the conventional space radiator. That part of the claim is
  sturdy: it survives losing any single assumed benefit.
- **But it does not make orbital data centers cheap.** Even with the new
  radiator, a terrestrial clean-grid data center delivers general AI compute
  about 10× more cheaply. The reason is everything else: solar panels,
  batteries, shielding, launch, and replacing dead satellites. That result
  holds even if launch fell to $100/kg.
- **Orbital computing wins exactly one job: triage in orbit.** When a
  satellite looks at Earth, most of what it sees is clouds or empty ocean.
  Sorting that in orbit and downlinking only the useful scenes is about 3×
  more cost-effective than downlinking everything. But that 3× depends on two
  assumed numbers with no measurement behind them — if they are lower, the
  advantage vanishes. We publish the breakevens so anyone can check.
- **Two designs failed outright.** A naive pumped-liquid structural panel
  and a liquid droplet radiator both lost badly on mass and reliability.

## What is still unknown

Everything here is computation. The key physical question — does an
oscillating heat pipe actually start up and keep working in microgravity at
panel scale? — has not been tested. That test, in a thermal-vacuum chamber,
is the next step, and it could kill the central claim. Until then, treat the
60% figure as a modeled result, not a measured one.

## Bottom line

Put the computer where the data is, not where the marketing is. For general
AI, that is Earth. For deciding which satellite images are worth sending
down, that is orbit — if the triage assumptions hold.
