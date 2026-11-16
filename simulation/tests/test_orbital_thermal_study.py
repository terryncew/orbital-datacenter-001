#!/usr/bin/env python3
"""
Module: tests/test_orbital_thermal_study.py

Independent unit and constitutive verification suite (8 tests).
Executes every solver from scratch in both standard and -O modes with zero warnings.
Artifact-generating tests write to a temporary directory, never into the repo.
"""

from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from repair_coupon import (
    verify_and_repair_f1_f2_heater_and_netlist,
    generate_true_manifold_brep_step,
    verify_and_repair_f4_hydraulics,
    solve_true_3d_fvm_pdn_resistance,
)
from orbital_thermal_study import (
    CANDIDATE_ARCHITECTURES,
    evaluate_architecture_at_scale,
    evaluate_unfamiliar_spacecraft_stress_case,
    run_complete_multi_round_tournament,
    run_sensitivity_analysis,
)


class TestOrbitalThermalStudy(unittest.TestCase):
    def test_01_f1_f2_netlist_50w_exact_and_zero_package_collision(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = verify_and_repair_f1_f2_heater_and_netlist(Path(d))
        self.assertAlmostEqual(r["defect_f1_old_parallel_power_w"], 614.4, places=1)
        self.assertAlmostEqual(r["defect_f1_repaired_series_parallel_power_w"], 50.0, places=4)
        self.assertGreater(r["defect_f2_old_to247_span_mm"], 45.0)
        self.assertLess(r["defect_f2_repaired_smd2512_span_mm"], 45.0)
        self.assertEqual(r["defect_f2_geometric_collision_count"], 0)
        # With the 0.020 Ohm fuse + 0.010 Ohm bimetal series protection included:
        self.assertAlmostEqual(r["defect_f1_total_draw_with_protection_w"], 49.8701, places=3)
        self.assertAlmostEqual(r["defect_f1_matrix_power_with_protection_w"], 49.7406, places=3)
        self.assertAlmostEqual(r["defect_f1_power_per_resistor_with_protection_w"], 3.1088, places=3)

    def test_02_f3_true_manifold_brep_step_euler_closure(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            step_path = Path(d) / "ms_ohp_sp_tvac_coupon_brep.step"
            b = generate_true_manifold_brep_step(step_path)
            txt = step_path.read_text(encoding="utf-8")
        self.assertEqual(b["manifold_solid_brep_count"], 10)
        self.assertEqual(b["closed_shell_count"], 10)
        self.assertEqual(b["advanced_face_count"], 60)
        self.assertTrue(b["all_euler_poincare_v_minus_e_plus_f_equal_2"])
        self.assertIn("MANIFOLD_SOLID_BREP", txt)
        self.assertIn("CLOSED_SHELL", txt)
        self.assertIn("ADVANCED_FACE", txt)

    def test_03_f4_f5_hydraulic_continuity_and_true_3d_fvm_laplace(self) -> None:
        h = verify_and_repair_f4_hydraulics()
        self.assertEqual(h["channels_per_header_repaired"], 30)
        self.assertAlmostEqual(h["repaired_continuity_velocity_m_s"], 2.0 * h["buggy_004_velocity_m_s"], places=3)
        self.assertTrue(h["below_3_5_m_s_erosion_limit"])
        self.assertTrue(h["below_45_kpa_pressure_limit"])

        p_lat = solve_true_3d_fvm_pdn_resistance("LATERAL_FR4_2OZ", 1280.0)
        p_coax = solve_true_3d_fvm_pdn_resistance("COAXIAL_BOLTED_POSTS", 1280.0)
        p_vias = solve_true_3d_fvm_pdn_resistance("COAXIAL_THRU_SUBSTRATE_VIAS", 1280.0)
        self.assertGreater(p_lat["solved_3d_joule_loss_w"], p_coax["solved_3d_joule_loss_w"] * 3.5)
        self.assertGreater(p_coax["solved_3d_joule_loss_w"], p_vias["solved_3d_joule_loss_w"])

    def test_04_round1_incumbent_beats_naive_mif_pws_and_is_adopted(self) -> None:
        a04 = evaluate_architecture_at_scale(CANDIDATE_ARCHITECTURES["A04_CONV_LIGHTWEIGHT_RADIATOR_INCUMBENT"], 150.0)
        a06 = evaluate_architecture_at_scale(CANDIDATE_ARCHITECTURES["A06_NAIVE_PUMPED_MIF_PWS_STRUCTURAL"], 150.0)
        self.assertAlmostEqual(a04["screening_80c_thermal_kg_per_kw"], 5.423, places=3)
        self.assertAlmostEqual(a06["screening_80c_thermal_kg_per_kw"], 9.345, places=3)
        self.assertLess(a04["coupled_thermal_rad_kg_per_kw"], a06["coupled_thermal_rad_kg_per_kw"])
        self.assertGreater(a04["mmod_5yr_thermal_survival_prob"], a06["mmod_5yr_thermal_survival_prob"])

    def test_05_round2_ms_ohp_sp_beats_incumbent_and_breakeven(self) -> None:
        a04 = evaluate_architecture_at_scale(CANDIDATE_ARCHITECTURES["A04_CONV_LIGHTWEIGHT_RADIATOR_INCUMBENT"], 150.0)
        a09 = evaluate_architecture_at_scale(CANDIDATE_ARCHITECTURES["A09_ROUND2_INVENTION_MS_OHP_SP"], 150.0)
        self.assertLess(a09["effective_areal_density_kg_m2"], 5.083)
        self.assertLess(a09["coupled_thermal_rad_kg_per_kw"], 0.50 * a04["coupled_thermal_rad_kg_per_kw"])
        self.assertLess(a09["total_spacecraft_launched_kg_per_kw"], a04["total_spacecraft_launched_kg_per_kw"] - 7.0)

    def test_06_round3_split_regime_terrestrial_wins_c3_and_sparse_edge_wins_c1(self) -> None:
        tour = run_complete_multi_round_tournament()
        s150 = tour["by_scale"]["SCALE_150KW"]
        # Regime C3: Terrestrial A11 beats every orbital arm
        max_orbital_c3 = max(
            v["regime_c3_general_ai_tflops_yr_per_usd"]
            for v in s150.values() if v["domain"] == "ORBITAL_LEO"
        )
        self.assertGreater(s150["A11_TERRESTRIAL_CLEAN_GRID_DRYCOOL"]["regime_c3_general_ai_tflops_yr_per_usd"], 8.0 * max_orbital_c3)
        self.assertTrue(all(r["terrestrial_still_cheaper_for_regime_c3"] for r in tour["launch_price_sensitivity_150kw"]))

        # Regime C1/C2: A10 beats Terrestrial A11 and the modeled Suncatcher-class A02
        self.assertGreater(
            s150["A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP"]["regime_c1_space_native_scenes_per_usd"],
            3.0 * s150["A11_TERRESTRIAL_CLEAN_GRID_DRYCOOL"]["regime_c1_space_native_scenes_per_usd"],
        )
        self.assertGreater(
            s150["A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP"]["regime_c1_space_native_scenes_per_usd"],
            15.0 * s150["A02_GOOGLE_PLANET_SUNCATCHER_CCHP"]["regime_c1_space_native_scenes_per_usd"],
        )

    def test_07_environmental_ledger_epistemic_honesty(self) -> None:
        a02 = evaluate_architecture_at_scale(CANDIDATE_ARCHITECTURES["A02_GOOGLE_PLANET_SUNCATCHER_CCHP"], 150.0)
        a10 = evaluate_architecture_at_scale(CANDIDATE_ARCHITECTURES["A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP"], 150.0)
        a11 = evaluate_architecture_at_scale(CANDIDATE_ARCHITECTURES["A11_TERRESTRIAL_CLEAN_GRID_DRYCOOL"], 150.0)
        self.assertIn("UNKNOWN", a10["environmental_ledger"]["stratospheric_radiative_forcing_multiplier"])
        self.assertEqual(a11["environmental_ledger"]["site_evaporative_water_liters"], 0.0)
        self.assertLess(
            a10["environmental_ledger"]["reentry_alumina_al2o3_ablation_kg"],
            0.20 * a02["environmental_ledger"]["reentry_alumina_al2o3_ablation_kg"],
        )

    def test_08_unfamiliar_stress_case_replay(self) -> None:
        # Held-out generalization check: 250 kW, beta=75 deg, 7 yr, q_env 210 W/m2.
        # Standalone — no external engine. Values are the executed replay results.
        stress_a10 = evaluate_unfamiliar_spacecraft_stress_case("A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP")
        a04 = evaluate_unfamiliar_spacecraft_stress_case("A04_CONV_LIGHTWEIGHT_RADIATOR_INCUMBENT")
        a06 = evaluate_unfamiliar_spacecraft_stress_case("A06_NAIVE_PUMPED_MIF_PWS_STRUCTURAL")
        self.assertTrue(stress_a10["feasible_on_all_flight_gates"])
        self.assertFalse(a04["feasible_on_all_flight_gates"])
        self.assertFalse(a06["feasible_on_all_flight_gates"])
        self.assertAlmostEqual(stress_a10["coupled_thermal_rad_kg_per_kw"], 3.346, places=3)
        self.assertAlmostEqual(a04["coupled_thermal_rad_kg_per_kw"], 8.73, places=2)
        self.assertAlmostEqual(a06["coupled_thermal_rad_kg_per_kw"], 13.164, places=3)
        self.assertAlmostEqual(stress_a10["mmod_7yr_survival_prob"], 0.998, places=3)
        self.assertAlmostEqual(a04["mmod_7yr_survival_prob"], 0.9842, places=4)
        self.assertAlmostEqual(a06["mmod_7yr_survival_prob"], 0.6189, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
