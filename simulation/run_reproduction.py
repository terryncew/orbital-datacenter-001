#!/usr/bin/env python3
"""
Module: run_reproduction.py

One-command reproduction for the orbital thermal study. From the repository
root, run:

    python3 simulation/run_reproduction.py

It executes:
  1. The implemented coupon defect repairs (F1-F5, F8) and true B-Rep STEP
     generation. F6/F7 concern analyses outside this study and have no implementation in this package; they are not claimed here (see repair_coupon.py).
  2. The three-round tournament across 12 architectures, 3 scales (1 kW,
     150 kW, 1 MW), and 2 workload regimes (C3 general AI vs C1/C2
     space-native edge triage).
  3. The sensitivity analysis for the two headline claims.
  4. The standalone unfamiliar stress-case replay (250 kW, beta=75 deg,
     7 yr, q_env 210 W/m2) — no external engine.
  5. Figure and CAD generation (figures 1-3, STL/DXF/SVG coupon drawings).
  6. Byte-determinism verification across two consecutive regenerations.
  7. The 8-test verification suite in standard and -O modes.
  8. SHA256SUMS.txt manifest generation and verification over the whole repo.

STATUS: computational, AI-assisted research. No physical thermal-vacuum
validation is performed by this script; the TVAC coupon test is the
falsification gate for the central thermal claim.
"""

from __future__ import annotations
import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict

SIM_DIR = Path(__file__).resolve().parent
ROOT = SIM_DIR.parent
if str(SIM_DIR) not in sys.path:
    sys.path.insert(0, str(SIM_DIR))

from repair_coupon import run_all_004_repairs
from orbital_thermal_study import (
    CANDIDATE_ARCHITECTURES,
    evaluate_architecture_at_scale,
    evaluate_unfamiliar_spacecraft_stress_case,
    run_complete_multi_round_tournament,
    run_sensitivity_analysis,
)
from generate_figures import (
    generate_tvac_coupon_stl_dxf_svg,
    generate_orbital_tournament_figures,
    generate_sensitivity_figure,
)


def generate_all_artifacts(root: Path) -> Dict[str, object]:
    repairs = run_all_004_repairs(root)
    tournament = run_complete_multi_round_tournament()
    sensitivity = run_sensitivity_analysis()
    stress = {
        "selected_a10": evaluate_unfamiliar_spacecraft_stress_case(
            "A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP"),
        "conventional_a04": evaluate_unfamiliar_spacecraft_stress_case(
            "A04_CONV_LIGHTWEIGHT_RADIATOR_INCUMBENT"),
        "naive_mif_pws_a06": evaluate_unfamiliar_spacecraft_stress_case(
            "A06_NAIVE_PUMPED_MIF_PWS_STRUCTURAL"),
    }
    cad_extra = generate_tvac_coupon_stl_dxf_svg(root)
    figures = generate_orbital_tournament_figures(tournament, root)
    fig3 = generate_sensitivity_figure(sensitivity, root)

    # Export CSV leaderboard for the 150 kW scale
    ev_dir = root / "evidence"
    ev_dir.mkdir(parents=True, exist_ok=True)
    csv_path = ev_dir / "orbital_thermal_study_150kw_leaderboard.csv"
    s150 = tournament["by_scale"]["SCALE_150KW"]
    rows = []
    for k, v in s150.items():
        rows.append({
            "arm_id": k,
            "round_introduced": v["round_introduced"],
            "domain": v["domain"],
            "screening_80c_thermal_kg_per_kw": v["screening_80c_thermal_kg_per_kw"],
            "coupled_thermal_rad_kg_per_kw": v["coupled_thermal_rad_kg_per_kw"],
            "total_spacecraft_launched_kg_per_kw": v["total_spacecraft_launched_kg_per_kw"],
            "mmod_5yr_thermal_survival_prob": v["mmod_5yr_thermal_survival_prob"],
            "delivered_compute_years_out_of_5": v["delivered_compute_years_out_of_5"],
            "cost_per_delivered_compute_kw_yr_usd": v["cost_per_delivered_compute_kw_yr_usd"],
            "regime_c3_general_ai_tflops_yr_per_usd": v["regime_c3_general_ai_tflops_yr_per_usd"],
            "regime_c1_space_native_scenes_per_usd": v["regime_c1_space_native_scenes_per_usd"],
            "launch_black_carbon_soot_kg": v["environmental_ledger"]["launch_black_carbon_soot_kg"],
            "reentry_alumina_al2o3_ablation_kg": v["environmental_ledger"]["reentry_alumina_al2o3_ablation_kg"],
        })
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    # Final disposition, computed from the results (never hardcoded: an
    # earlier version's hardcoded strings contradicted the executed outputs).
    a04 = s150["A04_CONV_LIGHTWEIGHT_RADIATOR_INCUMBENT"]
    a06 = s150["A06_NAIVE_PUMPED_MIF_PWS_STRUCTURAL"]
    a09 = s150["A09_ROUND2_INVENTION_MS_OHP_SP"]
    a10 = s150["A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP"]
    a11 = s150["A11_TERRESTRIAL_CLEAN_GRID_DRYCOOL"]
    a02 = s150["A02_GOOGLE_PLANET_SUNCATCHER_CCHP"]
    a09_100 = evaluate_architecture_at_scale(
        CANDIDATE_ARCHITECTURES["A09_ROUND2_INVENTION_MS_OHP_SP"], 150.0,
        launch_cost_override_usd_kg=100.0)
    c3_ratio = a11["regime_c3_general_ai_tflops_yr_per_usd"] / a10["regime_c3_general_ai_tflops_yr_per_usd"]
    c1_ratio = a10["regime_c1_space_native_scenes_per_usd"] / a11["regime_c1_space_native_scenes_per_usd"]
    c1_vs_a02 = a10["regime_c1_space_native_scenes_per_usd"] / a02["regime_c1_space_native_scenes_per_usd"]
    al2o3_cut = (1.0 - a10["environmental_ledger"]["reentry_alumina_al2o3_ablation_kg"]
                 / a04["environmental_ledger"]["reentry_alumina_al2o3_ablation_kg"]) * 100.0
    cost_ratio_100 = a09_100["cost_per_delivered_compute_kw_yr_usd"] / a11["cost_per_delivered_compute_kw_yr_usd"]
    mmode_risk_a06 = (1.0 - a06["mmod_5yr_thermal_survival_prob"]) * 100.0

    evidence = {
        "schema": "orbital-thermal-study.evidence.v1",
        "title": "Integrated Structural Thermal Management for Orbital Computing: A Comparative Engineering and Economic Study",
        "status": "COMPUTATIONAL — AI-assisted research. No physical thermal-vacuum validation has been performed. The TVAC coupon test is the falsification gate for the central thermal claim.",
        "final_disposition": {
            "overall_verdict": "LIMITED GO (Split-Regime Adoption + Inert TVAC Coupon Qualification)",
            "naive_pumped_a06": (
                f"REJECT ({a06['screening_80c_thermal_kg_per_kw']:.3f} kg/kW vs "
                f"{a04['screening_80c_thermal_kg_per_kw']:.3f} kg/kW conventional incumbent A04 at 80C; "
                f"{mmode_risk_a06:.1f}% 5-yr MMOD loop-drain hazard)"
            ),
            "liquid_droplet_radiator_a08": "REJECT (18.5%/yr attitude-slew droplet escape & optical/PV oil contamination; 18.5% is an assigned model input, not a measurement)",
            "regime_c3_general_terrestrial_user_ai": (
                f"REJECT ORBIT / ADOPT TERRESTRIAL CLEAN-GRID + DRY COOLING (A11 wins by {c3_ratio:.1f}x at "
                f"$1,500/kg launch and {cost_ratio_100:.2f}x even at $100/kg Starship launch, with 0 kg "
                f"stratospheric soot or Al2O3)"
            ),
            "regime_c1_c2_space_native_sensor_triage": (
                f"LIMITED GO — ADOPT A10 (Event-Gated Sparse Spectral/SAR Triage + MS-OHP-SP 64-Cell/m^2 "
                f"Structural Oscillating-Heat-Pipe Bus + Demisable C-SiC Low-Alumina Chassis: {c1_ratio:.2f}x vs "
                f"terrestrial raw downlink, {c1_vs_a02:.2f}x vs the modeled Suncatcher-class baseline A02, "
                f"-{al2o3_cut:.1f}% re-entry Al2O3)"
            ),
            "physical_prototype_status": "HOLD FOR EXTERNAL TVAC & PE/EHS REVIEW (Stage-0 is an INERT 100x100x2.6mm machinability & passive thermal-vacuum contact coupon; zero energization authorized)",
        },
        "stopping_boundary_explanation": (
            "Additional purely computational iterations cannot credibly improve the result because: (1) in Regime C3, "
            "the non-thermal spacecraft subsystem floor (PV + eclipse storage + ADCS/shielding = 22.5 kg/kW) and "
            "launch/replenishment overhead make even a zero-mass radiator more expensive per compute-year than "
            "terrestrial clean-grid power ($1,384/kW-yr); and (2) in Regime C1/C2, MS-OHP-SP's remaining uncertainty "
            "is the physical microgravity oscillation startup threshold and contact conductance across the brazed "
            "AlSiC/MoCu boss, which requires an external Thermal-Vacuum (TVAC) chamber measurement rather than "
            "further simulation."
        ),
        "coupon_defect_repairs_f1_f5_f8": repairs,
        "tournament": tournament,
        "sensitivity": sensitivity,
        "unfamiliar_stress_case_replay": stress,
        "cad_and_visual_deliverables": {
            **cad_extra,
            "step_brep_file": "cad_and_drawings/ms_ohp_sp_tvac_coupon_brep.step",
            "repaired_spice_file": "cad_and_drawings/repaired_50w_selv_smd2512_netlist.sp",
            "figures": figures + [fig3],
            "leaderboard_csv": "evidence/orbital_thermal_study_150kw_leaderboard.csv",
        },
    }
    ev_bytes = json.dumps(evidence, indent=2, sort_keys=True).encode("utf-8")
    content_sha256 = hashlib.sha256(ev_bytes).hexdigest()
    evidence["deterministic_content_sha256"] = content_sha256

    out_json = ev_dir / "orbital_thermal_study_evidence.json"
    out_json.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return evidence


def write_and_verify_manifest(root: Path) -> int:
    files = sorted(
        p for p in root.rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.name != "SHA256SUMS.txt"
        and not p.name.endswith(".pyc")
        and ".git" not in p.parts
        # Never manifest a virtualenv or any other hidden directory a user
        # (or a clean-room gate) may create inside the repo tree; dot-files
        # at the root such as .gitignore are still included.
        and not any(part.startswith(".") for part in p.relative_to(root).parts[:-1])
    )
    lines = []
    for f in files:
        rel = f.relative_to(root).as_posix()
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        lines.append(f"{h}  {rel}")
    manifest_path = root / "SHA256SUMS.txt"
    manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        eh, rel = line.split("  ", 1)
        ah = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        if ah != eh:
            raise RuntimeError(f"Manifest mismatch on {rel}: {ah} != {eh}")
    return len(lines)


def main() -> None:
    print("[1/5] Running F1-F5/F8 repairs, 12-arm tournament, sensitivity, stress replay, figures and CAD...")
    m1 = generate_all_artifacts(ROOT)
    h1 = m1["deterministic_content_sha256"]

    print("[2/5] Verifying byte-determinism across a second consecutive regeneration...")
    m2 = generate_all_artifacts(ROOT)
    h2 = m2["deterministic_content_sha256"]
    if h1 != h2:
        raise RuntimeError(f"Non-deterministic output detected: {h1} != {h2}")
    print(f"      Byte-deterministic evidence SHA-256: {h2}")

    print("[3/5] Running 8-test verification suite in standard and -O modes (with -W error::DeprecationWarning)...")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    subprocess.run([sys.executable, "-W", "error::DeprecationWarning", "-m", "unittest", "discover",
                    "-s", str(SIM_DIR / "tests"), "-v"], check=True, cwd=str(SIM_DIR), env=env)
    subprocess.run([sys.executable, "-O", "-W", "error::DeprecationWarning", "-m", "unittest", "discover",
                    "-s", str(SIM_DIR / "tests"), "-v"], check=True, cwd=str(SIM_DIR), env=env)

    print("[4/5] Writing and verifying SHA256SUMS.txt manifest...")
    n_files = write_and_verify_manifest(ROOT)
    print(f"      Manifest covers {n_files} files.")

    print("[5/5] Done.")
    print(f"ALL {n_files} FILES VERIFIED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
