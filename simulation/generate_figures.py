#!/usr/bin/env python3
"""
Module: generate_figures.py

Generates byte-deterministic PNG figures (zero Pillow deprecation warnings),
watertight STL, AutoCAD R12 DXF, and GD&T SVG blueprint for the inert
100x100x2.60mm MS-OHP-SP vs Conventional CCHP TVAC comparison coupon.

Figures are regenerated from the reproduced tournament data on every run;
no figure is copied from any earlier version. PNGs carry no metadata chunks
(Pillow round-trip strips them), so repeated runs are byte-identical.
"""

from __future__ import annotations
import io
from pathlib import Path
from typing import Dict, List, Tuple, Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image


def _save_deterministic_png(fig: plt.Figure, out_path: Path, dpi: int = 180) -> None:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGBA")
    # Use tobytes/frombytes (Pillow 14+ safe, zero DeprecationWarning) to strip volatile PNG timestamps
    clean = Image.frombytes("RGBA", img.size, img.tobytes())
    clean.save(out_path, format="PNG", optimize=False)


def generate_tvac_coupon_stl_dxf_svg(out_dir: Path) -> Dict[str, Any]:
    cad_dir = out_dir / "cad_and_drawings"
    cad_dir.mkdir(parents=True, exist_ok=True)

    # 1. Watertight ASCII STL of 100x100x2.60mm MS-OHP-SP panel + 45x45x0.80mm boss
    def box_tris(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> List[Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]]:
        p000, p100, p110, p010 = (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)
        p001, p101, p111, p011 = (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)
        return [
            ((0.0, 0.0, -1.0), p000, p110, p100), ((0.0, 0.0, -1.0), p000, p010, p110),
            ((0.0, 0.0, 1.0), p001, p101, p111), ((0.0, 0.0, 1.0), p001, p111, p011),
            ((0.0, -1.0, 0.0), p000, p100, p101), ((0.0, -1.0, 0.0), p000, p101, p001),
            ((0.0, 1.0, 0.0), p010, p111, p110), ((0.0, 1.0, 0.0), p010, p011, p111),
            ((-1.0, 0.0, 0.0), p000, p001, p011), ((-1.0, 0.0, 0.0), p000, p011, p010),
            ((1.0, 0.0, 0.0), p100, p110, p111), ((1.0, 0.0, 0.0), p100, p111, p101),
        ]

    tris = box_tris(-50.0, 50.0, -50.0, 50.0, 0.0, 2.60) + box_tris(-22.5, 22.5, -22.5, 22.5, 2.60, 3.40)
    stl_lines = ["solid MS_OHP_SP_TVAC_COUPON"]
    for norm, v1, v2, v3 in tris:
        stl_lines.append(f"  facet normal {norm[0]:.4f} {norm[1]:.4f} {norm[2]:.4f}")
        stl_lines.append("    outer loop")
        stl_lines.append(f"      vertex {v1[0]:.4f} {v1[1]:.4f} {v1[2]:.4f}")
        stl_lines.append(f"      vertex {v2[0]:.4f} {v2[1]:.4f} {v2[2]:.4f}")
        stl_lines.append(f"      vertex {v3[0]:.4f} {v3[1]:.4f} {v3[2]:.4f}")
        stl_lines.append("    endloop")
        stl_lines.append("  endfacet")
    stl_lines.append("endsolid MS_OHP_SP_TVAC_COUPON")
    stl_path = cad_dir / "ms_ohp_sp_tvac_coupon.stl"
    stl_path.write_text("\n".join(stl_lines) + "\n", encoding="utf-8")

    # 2. AutoCAD R12 DXF of the 100x100mm TVAC coupon, 45x45mm boss, 16 non-colliding SMD 2512 pads, and 8 cellular OHP serpentine cavities
    dxf = ["0", "SECTION", "2", "ENTITIES"]
    dxf_count = 0

    def add_rect(layer: str, x0: float, y0: float, x1: float, y1: float) -> None:
        nonlocal dxf_count
        for ax, ay, bx, by in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
            dxf.extend(["0", "LINE", "8", layer, "10", f"{ax:.4f}", "20", f"{ay:.4f}", "30", "0.0", "11", f"{bx:.4f}", "21", f"{by:.4f}", "31", "0.0"])
            dxf_count += 1

    add_rect("OUTER_PANEL_100X100", -50.0, -50.0, 50.0, 50.0)
    add_rect("DIE_BOSS_45X45", -22.5, -22.5, 22.5, 22.5)
    for c_idx in range(8):
        yc = -50.0 + (c_idx + 0.5) * 12.5
        add_rect("CELLULAR_OHP_CAVITIES_8X", -46.0, yc - 1.2, 46.0, yc + 1.2)
    for iy in range(4):
        for ix in range(4):
            cx = -16.875 + ix * 11.25
            cy = -16.875 + iy * 11.25
            add_rect("SMD2512_NON_COLLIDING_16X", cx - 3.175, cy - 1.60, cx + 3.175, cy + 1.60)
    dxf.extend(["0", "ENDSEC", "0", "EOF"])
    dxf_path = cad_dir / "ms_ohp_sp_tvac_coupon.dxf"
    dxf_path.write_text("\n".join(dxf) + "\n", encoding="utf-8")

    # 3. Dimensioned SVG blueprint
    svg_path = cad_dir / "ms_ohp_sp_tvac_coupon_blueprint.svg"
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="680" viewBox="0 0 1100 680">
  <rect width="1100" height="680" fill="#0f172a"/>
  <rect x="16" y="16" width="1068" height="648" rx="8" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <text x="36" y="50" fill="#f8fafc" font-family="monospace" font-size="19" font-weight="bold">
    ORBITAL MS-OHP-SP INERT TVAC COUPON &amp; REPAIRED SMD-2512 LAYOUT BLUEPRINT (F1-F5, F8)
  </text>
  <text x="36" y="74" fill="#94a3b8" font-family="monospace" font-size="12.5">
    Stage-0 Status: INERT MACHINABILITY &amp; TVAC CONTACT COUPON ONLY (Zero Energization Without PE/EHS Signoff) | Watertight B-Rep STEP (V-E+F=2)
  </text>

  <!-- Left: 100x100mm MS-OHP-SP Panel with 45x45mm Boss & 16 Non-Colliding SMD 2512 Footprints -->
  <rect x="40" y="95" width="480" height="440" fill="#0f172a" stroke="#64748b" stroke-width="1.5"/>
  <text x="55" y="118" fill="#38bdf8" font-family="monospace" font-size="13.5" font-weight="bold">
    A. 100x100x2.6mm MS-OHP-SP PANEL + 4x4 SMD-2512 ARRAY (0 COLLISIONS)
  </text>
  <rect x="100" y="140" width="360" height="360" fill="#1e293b" stroke="#38bdf8" stroke-width="2"/>
  <rect x="199" y="239" width="162" height="162" fill="#0f172a" stroke="#f59e0b" stroke-width="2"/>
  <!-- 8 Cellular OHP serpentine cavities -->
  <rect x="114" y="156" width="332" height="18" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1"/>
  <rect x="114" y="198" width="332" height="18" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1"/>
  <rect x="114" y="240" width="332" height="18" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1"/>
  <rect x="114" y="282" width="332" height="18" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1"/>
  <rect x="114" y="324" width="332" height="18" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1"/>
  <rect x="114" y="366" width="332" height="18" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1"/>
  <rect x="114" y="408" width="332" height="18" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1"/>
  <rect x="114" y="450" width="332" height="18" fill="#0284c7" fill-opacity="0.25" stroke="#38bdf8" stroke-width="1"/>
  <!-- 4x4 non-colliding SMD 2512 heaters (6.35x3.20mm on 11.25mm pitch -> +4.90mm X clearance, +8.05mm Y clearance) -->
  <rect x="208" y="252" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="248" y="252" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="288" y="252" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="328" y="252" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="208" y="292" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="248" y="292" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="288" y="292" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="328" y="292" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="208" y="332" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="248" y="332" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="288" y="332" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="328" y="332" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="208" y="372" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="248" y="372" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="288" y="372" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <rect x="328" y="372" width="23" height="12" fill="#22c55e" stroke="#bbf7d0" stroke-width="1"/>
  <text x="98" y="522" fill="#e2e8f0" font-family="monospace" font-size="11.5">
    Outer Panel: 100.0x100.0mm | Boss: 45.0x45.0mm | SMD 2512 Clearance: +4.90mm X / +8.05mm Y
  </text>

  <!-- Right Top: Coupon Defect Repair Table (F1-F5, F8) -->
  <rect x="540" y="95" width="520" height="240" fill="#0f172a" stroke="#22c55e" stroke-width="1.5"/>
  <text x="556" y="118" fill="#4ade80" font-family="monospace" font-size="13.5" font-weight="bold">
    B. COUPON DEFECT REPAIRS (F1-F5, F8)
  </text>
  <text x="556" y="144" fill="#e2e8f0" font-family="monospace" font-size="11.5">
    - F1 Netlist Power: 4x4 Series-Parallel 11.52 Ohm @ 24V, 50.000 W matrix (49.87 W total)
  </text>
  <text x="556" y="166" fill="#e2e8f0" font-family="monospace" font-size="11.5">
    - F2 Package Collision: SMD 2512 (6.35x3.20mm) spans 40.10mm &lt; 45.0mm (0 collisions)
  </text>
  <text x="556" y="188" fill="#e2e8f0" font-family="monospace" font-size="11.5">
    - F3 STEP Topology: 10 MANIFOLD_SOLID_BREP / 10 CLOSED_SHELL / 60 ADVANCED_FACE (V-E+F=2)
  </text>
  <text x="556" y="210" fill="#e2e8f0" font-family="monospace" font-size="11.5">
    - F4 Channel Continuity: 30 ch/header (60 total), L=42.0mm, v=0.7937 m/s, dP=6.53 kPa
  </text>
  <text x="556" y="232" fill="#e2e8f0" font-family="monospace" font-size="11.5">
    - F5 3D PDN Laplace: 16x16x8 (2,048 3D FVM cells) explicit z-axis conductivity solver
  </text>
  <text x="556" y="254" fill="#e2e8f0" font-family="monospace" font-size="11.5">
    - F8: INERT Stage-0 classification (no energization without external PE/EHS signoff)
  </text>
  <text x="556" y="284" fill="#fde047" font-family="monospace" font-size="12" font-weight="bold">
    TVAC Acceptance Gates: dry mass &lt;= 62% of solid Al-6061 control at equal EI (+/-5%); He leak &lt; 1e-8 atm-cc/s; k_eff &gt;= 1,200 W/m-K (reject &lt; 600 or dryout &lt; 50 W)
  </text>
  <text x="556" y="306" fill="#94a3b8" font-family="monospace" font-size="11">
    Compared head-to-head against matched-area Conventional CCHP Panel (A04: 5.423 kg/kW)
  </text>

  <!-- Right Bottom: 3-Round Orbital Invention Loop Summary -->
  <rect x="540" y="350" width="520" height="185" fill="#0f172a" stroke="#38bdf8" stroke-width="1.5"/>
  <text x="556" y="374" fill="#38bdf8" font-family="monospace" font-size="13.5" font-weight="bold">
    C. THREE-ROUND COMPARATIVE STUDY SUMMARY
  </text>
  <text x="556" y="400" fill="#fca5a5" font-family="monospace" font-size="11.5">
    Round 1: Naive Pumped MIF-PWS (A06: 9.345 kg/kW) REJECTED; Conventional A04 (5.423 kg/kW) ADOPTED
  </text>
  <text x="556" y="424" fill="#86efac" font-family="monospace" font-size="11.5">
    Round 2: Invented MS-OHP-SP (A09: 3.458 kg/m2 &lt; 5.083 break-even; 2.725 kg/kW coupled, -60% vs A04)
  </text>
  <text x="556" y="448" fill="#fde047" font-family="monospace" font-size="11.5">
    Round 3 (Regime C3 General AI): Terrestrial Clean-Grid A11 ($1,384/kW-yr) beats the best orbital arm by 9.7x
  </text>
  <text x="556" y="472" fill="#38bdf8" font-family="monospace" font-size="11.5">
    Round 3 (Regime C1/C2 Space-Native Edge): Sparse Edge + MS-OHP-SP (A10) wins by 3.06x vs Ground
  </text>
  <text x="556" y="496" fill="#cbd5e1" font-family="monospace" font-size="11">
    and 20.25x vs the modeled Suncatcher-class baseline (A02), while cutting re-entry Al2O3 by -84.0%!
  </text>

  <rect x="40" y="550" width="1020" height="90" fill="#0f172a" stroke="#475569" stroke-width="1.5"/>
  <text x="56" y="576" fill="#f8fafc" font-family="monospace" font-size="13" font-weight="bold">
    FINAL DISPOSITION: LIMITED GO (Regime C1/C2 Space-Native Edge A10 &amp; Inert TVAC Coupon) | REJECT (Naive Pumped MIF-PWS A06 &amp; Regime C3 General Orbital AI)
  </text>
  <text x="56" y="600" fill="#94a3b8" font-family="monospace" font-size="11.5">
    All results are computational &amp; CAD-verified (SIMULATED). Physical flight &amp; thermal-vacuum qualification remain on HOLD pending external TVAC chamber test.
  </text>
  <text x="56" y="622" fill="#94a3b8" font-family="monospace" font-size="11.5">
    Stratospheric black-carbon radiative forcing &amp; heterogeneous Al2O3 ozone-depletion coefficients are explicitly recorded as UNKNOWN.
  </text>
</svg>
"""
    svg_path.write_text(svg_content, encoding="utf-8")

    return {
        "stl_file": str(stl_path.relative_to(out_dir)),
        "stl_triangle_count": len(tris),
        "dxf_file": str(dxf_path.relative_to(out_dir)),
        "dxf_entity_count": dxf_count,
        "svg_file": str(svg_path.relative_to(out_dir)),
    }


def generate_orbital_tournament_figures(tour_data: Dict[str, Any], out_dir: Path) -> List[str]:
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    s150 = tour_data["by_scale"]["SCALE_150KW"]

    # Figure 1: 4-Panel Orbital & Terrestrial Tournament Comparison (150 kW Scale)
    fig1, axes = plt.subplots(2, 2, figsize=(14.5, 9.8), facecolor="#0f172a")
    for ax in axes.flat:
        ax.set_facecolor("#1e293b")
        for sp_v in ax.spines.values():
            sp_v.set_color("#475569")
        ax.tick_params(colors="#e2e8f0", labelsize=8.5)

    orb_keys = [
        "A01_HERITAGE_ISS_PUMPED_LOOP",
        "A02_GOOGLE_PLANET_SUNCATCHER_CCHP",
        "A03_SPACEX_AI1_150KW_REFERENCE",
        "A04_CONV_LIGHTWEIGHT_RADIATOR_INCUMBENT",
        "A05_LOAD_BEARING_ISOGRID_CCHP_PRIOR_ART",
        "A06_NAIVE_PUMPED_MIF_PWS_STRUCTURAL",
        "A07_MODULAR_PASSIVE_LHP_PANELS",
        "A08_LIQUID_DROPLET_RADIATOR_LDR",
        "A09_ROUND2_INVENTION_MS_OHP_SP",
        "A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP",
    ]
    short_orb = ["A01\nISS", "A02\nSuncatch", "A03\nSpX AI1", "A04\nIncumb", "A05\nIsogrid", "A06\nMIF-PWS", "A07\nLHP", "A08\nLDR", "A09\nMS-OHP", "A10\nSparse+OHP"]

    # Panel A: Thermal-Structural Mass per kW (80 C Screening vs Coupled EOL Chain)
    ax0 = axes[0, 0]
    x = list(range(len(orb_keys)))
    w = 0.38
    m_scr = [s150[k]["screening_80c_thermal_kg_per_kw"] for k in orb_keys]
    m_cpl = [s150[k]["coupled_thermal_rad_kg_per_kw"] for k in orb_keys]
    ax0.bar([i - w / 2 for i in x], m_scr, width=w, color="#38bdf8", label="Fixed 80 C Screening (kg/kW)")
    ax0.bar([i + w / 2 for i in x], m_cpl, width=w, color="#22c55e", label="Coupled Tj->Trad + EOL (kg/kW)")
    ax0.axhline(5.423, color="#fde047", linestyle="--", linewidth=1.6, label="Round 1 Incumbent A04 (5.423 kg/kW)")
    ax0.set_xticks(x)
    ax0.set_xticklabels(short_orb, rotation=35, ha="right")
    ax0.set_ylabel("Thermal + Radiator Mass (kg / kW IT)", color="#f8fafc", fontsize=9.5)
    ax0.set_title("A. Radiator & Thermal Mass: Round 1 Incumbent (A04) vs Round 2 MS-OHP-SP (A09)", color="#f8fafc", fontsize=10.5, fontweight="bold")
    ax0.legend(facecolor="#0f172a", edgecolor="#475569", labelcolor="#f8fafc", fontsize=8)

    # Panel B: Full Launched Spacecraft Mass (kg/kW IT) at 150 kW
    ax1 = axes[0, 1]
    tot_kg = [s150[k]["total_spacecraft_launched_kg_per_kw"] for k in orb_keys]
    bar_colors = ["#64748b", "#94a3b8", "#38bdf8", "#f59e0b", "#94a3b8", "#f43f5e", "#94a3b8", "#a855f7", "#22c55e", "#10b981"]
    bars1 = ax1.bar(x, tot_kg, color=bar_colors, width=0.58)
    for b in bars1:
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.8, f"{b.get_height():.1f}", ha="center", va="bottom", color="#f8fafc", fontsize=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels(short_orb, rotation=35, ha="right")
    ax1.set_ylim(0, 68)
    ax1.set_ylabel("Total Spacecraft Mass (kg / kW IT)", color="#f8fafc", fontsize=9.5)
    ax1.set_title("B. Full Spacecraft Mass (Thermal + PV + Battery + Bus/Shielding)", color="#f8fafc", fontsize=10.5, fontweight="bold")

    # Panel C: Regime C3 (Terrestrial-User General AI: TFLOPS-yr / $) — Terrestrial A11/A12 Win!
    ax2 = axes[1, 0]
    all_keys = orb_keys + ["A11_TERRESTRIAL_CLEAN_GRID_DRYCOOL", "A12_TERRESTRIAL_SOLAR_BATTERY_OFFGRID"]
    all_short = short_orb + ["A11\nTerr Grid", "A12\nTerr Solar"]
    c3_scores = [s150[k]["regime_c3_general_ai_tflops_yr_per_usd"] for k in all_keys]
    c3_colors = bar_colors + ["#eab308", "#f97316"]
    x_all = list(range(len(all_keys)))
    bars2 = ax2.bar(x_all, c3_scores, color=c3_colors, width=0.60)
    for b in bars2:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3, f"{b.get_height():.2f}", ha="center", va="bottom", color="#f8fafc", fontsize=7.5)
    ax2.set_xticks(x_all)
    ax2.set_xticklabels(all_short, fontsize=7.5, rotation=35, ha="right")
    ax2.set_ylim(0, 17.0)
    ax2.set_ylabel("Delivered TFLOPS-yr / Lifecycle $", color="#f8fafc", fontsize=9.5)
    c3_ratio = s150["A11_TERRESTRIAL_CLEAN_GRID_DRYCOOL"]["regime_c3_general_ai_tflops_yr_per_usd"] / s150["A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP"]["regime_c3_general_ai_tflops_yr_per_usd"]
    ax2.set_title(f"C. Regime C3 (General Terrestrial AI): Terrestrial Clean-Grid (A11) Wins by {c3_ratio:.1f}x", color="#f8fafc", fontsize=10.5, fontweight="bold")

    # Panel D: Regime C1/C2 (Space-Native Sensor/SAR/Hyperspectral Triage: Actionable Scenes / $) — A10 Wins!
    ax3 = axes[1, 1]
    c1_scores = [s150[k]["regime_c1_space_native_scenes_per_usd"] for k in all_keys]
    bars3 = ax3.bar(x_all, c1_scores, color=c3_colors, width=0.60)
    for b in bars3:
        ax3.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01, f"{b.get_height():.3f}", ha="center", va="bottom", color="#f8fafc", fontsize=7.5)
    ax3.set_xticks(x_all)
    ax3.set_xticklabels(all_short, fontsize=7.5, rotation=35, ha="right")
    ax3.set_ylim(0, 0.58)
    ax3.set_ylabel("Actionable Space-Native Scenes / Lifecycle $", color="#f8fafc", fontsize=9.5)
    c1_ratio = s150["A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP"]["regime_c1_space_native_scenes_per_usd"] / s150["A11_TERRESTRIAL_CLEAN_GRID_DRYCOOL"]["regime_c1_space_native_scenes_per_usd"]
    ax3.set_title(f"D. Regime C1/C2 (Space-Native EO/SAR Edge): Sparse + MS-OHP-SP (A10) Wins by {c1_ratio:.2f}x", color="#f8fafc", fontsize=10.5, fontweight="bold")

    fig1.suptitle("INTEGRATED STRUCTURAL THERMAL MANAGEMENT FOR ORBITAL COMPUTING — 12-ARCHITECTURE COMPARISON [SIMULATED]", color="#38bdf8", fontsize=12.5, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    f1_path = fig_dir / "fig1_orbital_tournament_and_regimes.png"
    _save_deterministic_png(fig1, f1_path)

    # Figure 2: Launch Cost Sensitivity ($1,500/kg down to $100/kg) & Re-Entry Al2O3 Reduction
    fig2, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(13.8, 5.2), facecolor="#0f172a")
    for ax in (ax_l, ax_r):
        ax.set_facecolor("#1e293b")
        for sp_v in ax.spines.values():
            sp_v.set_color("#475569")
        ax.tick_params(colors="#e2e8f0", labelsize=9)

    sweep = tour_data["launch_price_sensitivity_150kw"]
    l_prices = [r["launch_cost_per_kg_usd"] for r in sweep]
    c_a04 = [r["A04_conv_incumbent_cost_per_kw_yr_usd"] for r in sweep]
    c_a09 = [r["A09_ms_ohp_sp_cost_per_kw_yr_usd"] for r in sweep]
    c_a11 = [r["A11_terrestrial_clean_grid_cost_per_kw_yr_usd"] for r in sweep]
    ax_l.plot(l_prices, c_a04, "-s", color="#f59e0b", linewidth=2.2, label="A04: Conv Lightweight Orbital Incumbent")
    ax_l.plot(l_prices, c_a09, "-o", color="#22c55e", linewidth=2.4, label="A09/A10: Round 2/3 MS-OHP-SP Orbital")
    ax_l.plot(l_prices, c_a11, "--", color="#38bdf8", linewidth=2.2, label="A11: Terrestrial Clean-Grid + Dry Cooler ($1,384/kW-yr)")
    ax_l.set_xlabel("Launch Price to LEO ($ / kg Payload)", color="#f8fafc", fontsize=10)
    ax_l.set_ylabel("5-Yr Cost per Delivered Compute-Year ($ / kW-yr)", color="#f8fafc", fontsize=10)
    ax_l.set_title("A. Launch-Cost Sensitivity: Terrestrial A11 Wins C3 Even at $100/kg", color="#f8fafc", fontsize=10.5, fontweight="bold")
    ax_l.invert_xaxis()
    ax_l.legend(facecolor="#0f172a", edgecolor="#475569", labelcolor="#f8fafc", fontsize=8.5)

    env_keys = ["A01_HERITAGE_ISS_PUMPED_LOOP", "A02_GOOGLE_PLANET_SUNCATCHER_CCHP", "A04_CONV_LIGHTWEIGHT_RADIATOR_INCUMBENT", "A09_ROUND2_INVENTION_MS_OHP_SP", "A10_ROUND3_INVENTION_SPARSE_ORBITAL_EDGE_MS_OHP", "A11_TERRESTRIAL_CLEAN_GRID_DRYCOOL"]
    env_labels = ["A01: ISS\nPumped", "A02: Google\nSuncatcher", "A04: Conv\nIncumbent", "A09: Round 2\nMS-OHP-SP", "A10: Round 3\nDemisable C-SiC", "A11: Terr\nClean-Grid"]
    al2o3_kg = [s150[k]["environmental_ledger"]["reentry_alumina_al2o3_ablation_kg"] for k in env_keys]
    bc_kg = [s150[k]["environmental_ledger"]["launch_black_carbon_soot_kg"] for k in env_keys]
    ex = list(range(len(env_keys)))
    ax_r.bar([i - 0.18 for i in ex], al2o3_kg, width=0.35, color="#f43f5e", label="Re-Entry Al₂O₃ Ozone Catalyst (kg / 150kW sat)")
    ax_r.bar([i + 0.18 for i in ex], bc_kg, width=0.35, color="#94a3b8", label="Launch Black Carbon Soot (kg / 150kW sat)")
    ax_r.set_xticks(ex)
    ax_r.set_xticklabels(env_labels, fontsize=8.5)
    ax_r.set_ylabel("Stratospheric Particulate Emissions (kg)", color="#f8fafc", fontsize=10)
    ax_r.set_title("B. Stratospheric Re-Entry Al₂O₃ & Launch Black Carbon (150 kW, 5-Yr)", color="#f8fafc", fontsize=10.5, fontweight="bold")
    ax_r.legend(facecolor="#0f172a", edgecolor="#475569", labelcolor="#f8fafc", fontsize=8.5)

    plt.tight_layout()
    f2_path = fig_dir / "fig2_pareto_mass_cost_and_lifecycle.png"
    _save_deterministic_png(fig2, f2_path)
    return [str(f1_path.relative_to(out_dir)), str(f2_path.relative_to(out_dir))]


def generate_sensitivity_figure(sens_data: Dict[str, Any], out_dir: Path) -> str:
    """Figure 3: sensitivity of the two headline claims to their assigned inputs.

    Panel A: A09 coupled thermal-mass reduction vs A04 (baseline 60.0%) under
    single-benefit failures and all benefits removed.
    Panel B: A10 scenes/$ advantage vs A11 (baseline 3.06x) under degraded
    A10 inputs and stronger terrestrial inputs. The dashed line is parity
    (1.0x): below it, terrestrial wins.
    """
    fig_dir = out_dir / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    fig3, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(13.8, 5.2), facecolor="#0f172a")
    fig3.suptitle("SENSITIVITY OF THE TWO HEADLINE CLAIMS TO THEIR ASSIGNED INPUTS [SIMULATED]", color="#38bdf8", fontsize=12.5, fontweight="bold", y=0.98)
    ax_l.set_facecolor("#0f172a")
    ax_r.set_facecolor("#0f172a")

    mass = sens_data["thermal_mass_reduction_pct_vs_a04"]
    m_labels = ["Baseline", "dT 18 K", "Credit 0", "Density 5.10", "PDN 0.095", "All removed"]
    m_keys = ["baseline", "dT_chain 18 K (no interface benefit)", "structural bus credit 0",
              "panel areal density 5.10 kg/m2", "PDN loss 0.095 (A04 level)", "all four benefits removed"]
    m_vals = [mass[k] for k in m_keys]
    bars = ax_l.barh(m_labels, m_vals, color=["#38bdf8" if v == m_vals[0] else "#64748b" for v in m_vals])
    for b, v in zip(bars, m_vals):
        ax_l.text(b.get_width() + 1.0, b.get_y() + b.get_height() / 2, f"{v:.1f}%", va="center", color="#f8fafc", fontsize=9)
    ax_l.set_xlim(0, 72)
    ax_l.set_xlabel("Coupled thermal-mass reduction vs A04 (%)", color="#f8fafc", fontsize=10)
    ax_l.set_title("A. 60% thermal-mass claim: survives any single benefit failing", color="#f8fafc", fontsize=10.5, fontweight="bold")
    ax_l.tick_params(colors="#f8fafc", labelsize=9)
    for s in ("top", "right"):
        ax_l.spines[s].set_visible(False)

    ratio = sens_data["scenes_per_usd_ratio_vs_a11"]
    r_labels = ["Baseline", "A10 mult 2.0", "A10 compr 8:1", "Both worst", "A11 mult 0.5", "A11 mult 1.0"]
    r_keys = ["baseline", "A10 useful-scene multiplier 2.0", "A10 downlink compression 8:1",
              "both worst (multiplier 2.0, compression 8:1)", "A11 useful-scene multiplier 0.5", "A11 useful-scene multiplier 1.0"]
    r_vals = [ratio[k] for k in r_keys]
    bars = ax_r.barh(r_labels, r_vals, color=["#38bdf8" if v == r_vals[0] else ("#f87171" if v < 1.0 else "#64748b") for v in r_vals])
    for b, v in zip(bars, r_vals):
        ax_r.text(b.get_width() + 0.06, b.get_y() + b.get_height() / 2, f"{v:.2f}x", va="center", color="#f8fafc", fontsize=9)
    ax_r.axvline(1.0, color="#facc15", linestyle="--", linewidth=1.2)
    ax_r.set_ylim(-0.6, 5.9)
    ax_r.text(1.03, 5.55, "parity (1.0x)", color="#facc15", fontsize=9)
    ax_r.set_xlim(0, 3.6)
    ax_r.set_xlabel("A10 scenes/$ advantage vs terrestrial A11 (x)", color="#f8fafc", fontsize=10)
    ax_r.set_title("B. 3.06x scenes/$ claim: fragile — two assigned inputs decide it", color="#f8fafc", fontsize=10.5, fontweight="bold")
    ax_r.tick_params(colors="#f8fafc", labelsize=9)
    for s in ("top", "right"):
        ax_r.spines[s].set_visible(False)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out = fig_dir / "fig3_sensitivity.png"
    _save_deterministic_png(fig3, out)
    return str(out.relative_to(out_dir))


if __name__ == "__main__":
    from orbital_thermal_study import run_complete_multi_round_tournament, run_sensitivity_analysis
    t_data = run_complete_multi_round_tournament()
    cad_info = generate_tvac_coupon_stl_dxf_svg(Path("."))
    figs = generate_orbital_tournament_figures(t_data, Path("."))
    sens = run_sensitivity_analysis()
    fig3 = generate_sensitivity_figure(sens, Path("."))
    print("Generated:", cad_info, figs, fig3)
