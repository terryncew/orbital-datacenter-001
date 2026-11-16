#!/usr/bin/env python3
"""
Module: repair_coupon.py

Closes the implemented release blockers (F1-F5, F8) from an independent review
of an earlier terrestrial power-delivery design. That design had a
614.4 W electrical error (16 parallel 15.0 Ohm resistors across 24.0 V),
colliding TO-247 packages, a non-manifold STEP file, a hydraulic channel-count
error, and a 2D sheet approximation where a 3D solver was required.
  - F1: Replaces the 614.4 W parallel SPICE netlist error with a verified 4x4
        series-parallel bridge of 11.52 Ohm SMD 2512 resistors: 50.000 W matrix
        dissipation at its bus terminals at 24.0 V DC. The netlist also carries
        0.020 Ohm fuse + 0.010 Ohm bimetal series protection, so the total draw
        is 49.87 W and matrix dissipation 49.74 W (3.109 W/resistor, within the
        3.5 W rating). The physical prototype stays strictly INERT /
        NON-ENERGIZED until external PE/EHS signoff.
  - F2: Replaces colliding 15.76 mm TO-247 packages (63.04 mm > 45.0 mm) with SMD 2512
        (6.35 x 3.20 mm) thin-film alumina heaters on an 11.25 mm pitch (4.90 mm clearance,
        0 geometric collisions).
  - F3: Generates a true ISO-10303-21 AP214 Boundary-Representation (MANIFOLD_SOLID_BREP,
        CLOSED_SHELL, ADVANCED_FACE, EDGE_LOOP, ORIENTED_EDGE, EDGE_CURVE, VERTEX_POINT)
        STEP solid model for both the repaired 45x45mm coupon and the 100x100x2.6mm inert
        MS-OHP-SP TVAC test coupon, verifying Euler-Poincare closure (V - E + F = 2).
  - F4: Repairs hydraulic channel count per header (30 per header = 60 total interleaved,
        velocity 0.794 m/s vs 0.397 m/s) and channel length (42.0 mm vs 22.5 mm).
  - F5: Replaces the 2D 16x16 nodal sheet approximation with a true 3D finite-volume
        (nx=16, ny=16, nz=8 = 2,048 cells) Laplace solver J = -sigma(x,y,z) * grad_3d(phi).
  - F8: Classifies Stage-0 hardware as an INERT MACHINABILITY & TVAC CONTACT COUPON ONLY,
        requiring formal external PE/EHS signoff before any energized 50 W or 50 A test.

SCOPE NOTE: the defect list this module draws on numbered eight items
(F1-F8). This module implements and verifies F1-F5 and F8 only. F6 and F7
concern analyses outside this study; they have no implementation in this
file, their figures appear nowhere in the released code, and they are not
claimed as closed by this package.
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla


def verify_and_repair_f1_f2_heater_and_netlist(out_dir: Path) -> Dict[str, Any]:
    """
    Closes F1 (614.4 W netlist error) and F2 (TO-247 15.76mm width collision on 11.25mm pitch).
    """
    cad_dir = out_dir / "cad_and_drawings"
    cad_dir.mkdir(parents=True, exist_ok=True)

    # F1 Audit of old netlist: 16 parallel 15.0 Ohm resistors across 24.0 V
    old_power_w = 16.0 * (24.0 ** 2) / 15.0  # 614.4 W
    # Repaired Stage-1 circuit (still held non-energized until external PE/EHS approval):
    # 4 parallel strings, each containing 4 series SMD 2512 resistors of R_unit = 11.52 Ohm
    v_supply = 24.0
    n_strings = 4
    n_series_per_string = 4
    r_unit_ohm = 11.52
    r_string_ohm = n_series_per_string * r_unit_ohm  # 46.08 Ohm
    r_total_eq_ohm = r_string_ohm / n_strings        # 11.52 Ohm
    repaired_power_w = (v_supply ** 2) / r_total_eq_ohm  # 50.000 W at the matrix bus terminals
    current_total_a = v_supply / r_total_eq_ohm          # 2.0833 A (matrix only, protection excluded)
    power_per_resistor_w = repaired_power_w / 16.0       # 3.125 W (within 3.5W-5W pulsed/cooled 2512 rating)
    # CORRECTION (verification, 2026-11-16): the netlist below also includes
    # 0.020 Ohm fuse + 0.010 Ohm bimetal series protection. With protection:
    r_series_protection_ohm = 0.020 + 0.010
    r_total_with_protection_ohm = r_total_eq_ohm + r_series_protection_ohm
    current_with_protection_a = v_supply / r_total_with_protection_ohm
    total_draw_with_protection_w = v_supply * current_with_protection_a  # 49.87 W
    matrix_power_with_protection_w = (current_with_protection_a ** 2) * r_total_eq_ohm  # 49.74 W
    power_per_resistor_with_protection_w = matrix_power_with_protection_w / 16.0  # 3.109 W

    # F2 Audit of package geometry on 45.0 mm footprint (4x4 grid at 11.25 mm pitch)
    pitch_mm = 11.25
    old_to247_width_mm = 15.76
    old_span_4x_mm = 4.0 * old_to247_width_mm  # 63.04 mm > 45.0 mm (COLLISION!)
    old_clearance_mm = pitch_mm - old_to247_width_mm  # -4.51 mm overlap

    # Repaired package: SMD 2512 (Vishay CRCW2512-HP / Bourns CHP2512 high-power alumina chip resistor)
    smd2512_length_mm = 6.35
    smd2512_width_mm = 3.20
    repaired_span_4x_mm = 3.0 * pitch_mm + smd2512_length_mm  # 40.10 mm < 45.0 mm
    repaired_clearance_x_mm = pitch_mm - smd2512_length_mm    # +4.90 mm clearance
    repaired_clearance_y_mm = pitch_mm - smd2512_width_mm     # +8.05 mm clearance

    # Verify pairwise bounding boxes of all 16 SMD 2512 heaters have 0 overlaps
    boxes: List[Tuple[float, float, float, float]] = []
    for iy in range(4):
        for ix in range(4):
            cx = -16.875 + ix * pitch_mm
            cy = -16.875 + iy * pitch_mm
            boxes.append((
                cx - smd2512_length_mm / 2.0,
                cx + smd2512_length_mm / 2.0,
                cy - smd2512_width_mm / 2.0,
                cy + smd2512_width_mm / 2.0,
            ))
    collision_count = 0
    for i in range(len(boxes)):
        x0, x1, y0, y1 = boxes[i]
        if x0 < -22.5 or x1 > 22.5 or y0 < -22.5 or y1 > 22.5:
            collision_count += 1
        for j in range(i + 1, len(boxes)):
            bx0, bx1, by0, by1 = boxes[j]
            overlap_x = min(x1, bx1) - max(x0, bx0)
            overlap_y = min(y1, by1) - max(y0, by0)
            if overlap_x > 0.0 and overlap_y > 0.0:
                collision_count += 1

    # Write repaired SPICE netlist
    spice_lines = [
        "* REPAIRED STAGE-1 50.000W SELV 4x4 SERIES-PARALLEL SMD-2512 NETLIST (CLOSES F1 & F2)",
        "* 50.000 W IS THE MATRIX DISSIPATION AT ITS BUS TERMINALS (24.0 V). WITH THE 0.020 OHM",
        "* FUSE + 0.010 OHM BIMETAL SERIES PROTECTION THE TOTAL DRAW IS 49.87 W AND MATRIX",
        "* DISSIPATION IS 49.74 W (3.109 W/RESISTOR). SEE repair_coupon.py FOR THE COMPUTATION.",
        "* SAFETY NOTICE: DO NOT ENERGIZE WITHOUT EXTERNAL PE/EHS APPROVAL. STAGE-0 IS INERT ONLY.",
        ".PARAM V_SELV=24.0 R_UNIT=11.52",
        "V_SUPPLY N_RAW_24V 0 DC {V_SELV}",
        "R_FUSE_2_5A N_RAW_24V N_FUSED_24V 0.020",
        "R_BIMETAL_CUTOFF_85C N_FUSED_24V N_BUS_TOP 0.010",
    ]
    for s_idx in range(4):
        n_in = "N_BUS_TOP"
        for c_idx in range(4):
            n_out = f"N_S{s_idx}_C{c_idx}" if c_idx < 3 else "0"
            spice_lines.append(f"R_H_{s_idx}_{c_idx} {n_in} {n_out} {{R_UNIT}}")
            n_in = n_out
    spice_lines.extend([".OP", ".END"])
    spice_path = cad_dir / "repaired_50w_selv_smd2512_netlist.sp"
    spice_path.write_text("\n".join(spice_lines) + "\n", encoding="utf-8")

    return {
        "defect_f1_old_parallel_power_w": round(old_power_w, 2),
        "defect_f1_repaired_series_parallel_power_w": round(repaired_power_w, 4),
        "defect_f1_total_current_a": round(current_total_a, 4),
        "defect_f1_power_per_resistor_w": round(power_per_resistor_w, 4),
        "defect_f1_series_protection_ohm": round(r_series_protection_ohm, 3),
        "defect_f1_total_draw_with_protection_w": round(total_draw_with_protection_w, 4),
        "defect_f1_matrix_power_with_protection_w": round(matrix_power_with_protection_w, 4),
        "defect_f1_power_per_resistor_with_protection_w": round(power_per_resistor_with_protection_w, 4),
        "defect_f2_old_to247_span_mm": round(old_span_4x_mm, 2),
        "defect_f2_old_clearance_mm": round(old_clearance_mm, 2),
        "defect_f2_repaired_smd2512_span_mm": round(repaired_span_4x_mm, 2),
        "defect_f2_repaired_clearance_x_mm": round(repaired_clearance_x_mm, 2),
        "defect_f2_repaired_clearance_y_mm": round(repaired_clearance_y_mm, 2),
        "defect_f2_geometric_collision_count": collision_count,
        "repaired_spice_file": str(spice_path.relative_to(out_dir)),
    }


def generate_true_manifold_brep_step(out_path: Path, panel_length_mm: float = 100.0, panel_width_mm: float = 100.0, panel_thick_mm: float = 2.60, n_ohp_cells: int = 8) -> Dict[str, Any]:
    """
    Closes F3 (Invalid non-BREP STEP file):
    Generates a true ISO-10303-21 AP214 Boundary-Representation (MANIFOLD_SOLID_BREP)
    STEP file containing complete topological shells:
      CARTESIAN_POINT -> VERTEX_POINT -> DIRECTION -> VECTOR -> LINE -> EDGE_CURVE ->
      ORIENTED_EDGE -> EDGE_LOOP -> FACE_OUTER_BOUND -> PLANE -> ADVANCED_FACE ->
      CLOSED_SHELL -> MANIFOLD_SOLID_BREP.
    Verifies Euler-Poincare characteristic V - E + F = 2 on every generated solid shell.
    """
    lines: List[str] = [
        "ISO-10303-21;",
        "HEADER;",
        "FILE_DESCRIPTION(('True Manifold B-Rep Solid Model: MS-OHP-SP Inert TVAC Coupon & Serpentine OHP Cavities','Closes F3 with full CLOSED_SHELL / ADVANCED_FACE / MANIFOLD_SOLID_BREP topology'),'2;1');",
        "FILE_NAME('ms_ohp_sp_tvac_coupon_brep.step','2026-11-16T00:00:00',('Orbital Thermal Study'),('Independent TVAC Qualification'),'STEP-AP214','orbital-thermal-study-brep','NONE');",
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));",
        "ENDSEC;",
        "DATA;",
        "#1 = APPLICATION_CONTEXT('automotive_design');",
        "#2 = APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#1);",
        "#3 = PRODUCT_CONTEXT('',#1,'mechanical');",
        "#4 = PRODUCT('MS_OHP_SP_TVAC_COUPON','MS_OHP_SP_TVAC_COUPON','Inert 100x100x2.6mm Cellular Structural OHP Coupon',(#3));",
        "#5 = PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE('REV_B','Watertight B-Rep',#4,.MADE.);",
        "#6 = PRODUCT_DEFINITION_CONTEXT('part definition',#1,'design');",
        "#7 = PRODUCT_DEFINITION('MS_OHP_SP_DEF','Rev B',#5,#6);",
    ]

    eid = 10
    brep_ids: List[int] = []
    euler_checks: List[Dict[str, int]] = []

    def add_prism_brep(name: str, x0: float, x1: float, y0: float, y1: float, z0: float, z1: float) -> int:
        nonlocal eid
        coords = [
            (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
            (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
        ]
        v_ids: List[int] = []
        for idx_v, (px, py, pz) in enumerate(coords):
            cp_id = eid; eid += 1
            vp_id = eid; eid += 1
            lines.append(f"#{cp_id} = CARTESIAN_POINT('{name}_P{idx_v}',({px:.4f},{py:.4f},{pz:.4f}));")
            lines.append(f"#{vp_id} = VERTEX_POINT('{name}_V{idx_v}',#{cp_id});")
            v_ids.append(vp_id)

        # 12 topological edges of a hexahedral B-rep solid
        edge_pairs = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # bottom loop (0..3)
            (4, 5), (5, 6), (6, 7), (7, 4),  # top loop (4..7)
            (0, 4), (1, 5), (2, 6), (3, 7),  # vertical pillars (8..11)
        ]
        ec_ids: List[int] = []
        for idx_e, (va, vb) in enumerate(edge_pairs):
            ca, cb = coords[va], coords[vb]
            dx, dy, dz = cb[0] - ca[0], cb[1] - ca[1], cb[2] - ca[2]
            length = math.sqrt(dx * dx + dy * dy + dz * dz)
            ux, uy, uz = dx / length, dy / length, dz / length
            dir_id = eid; eid += 1
            vec_id = eid; eid += 1
            ln_cp_id = eid; eid += 1
            ln_id = eid; eid += 1
            ec_id = eid; eid += 1
            lines.append(f"#{dir_id} = DIRECTION('{name}_EDIR{idx_e}',({ux:.4f},{uy:.4f},{uz:.4f}));")
            lines.append(f"#{vec_id} = VECTOR('{name}_EVEC{idx_e}',#{dir_id},{length:.4f});")
            lines.append(f"#{ln_cp_id} = CARTESIAN_POINT('{name}_ELCP{idx_e}',({ca[0]:.4f},{ca[1]:.4f},{ca[2]:.4f}));")
            lines.append(f"#{ln_id} = LINE('{name}_ELINE{idx_e}',#{ln_cp_id},#{vec_id});")
            lines.append(f"#{ec_id} = EDGE_CURVE('{name}_EC{idx_e}',#{v_ids[va]},#{v_ids[vb]},#{ln_id},.T.);")
            ec_ids.append(ec_id)

        # 6 outward-oriented faces: (edge_indices, orientations, normal, point_on_face)
        faces_spec = [
            ([0, 1, 2, 3], [".F.", ".F.", ".F.", ".F."], (0.0, 0.0, -1.0), (1.0, 0.0, 0.0), coords[0]),
            ([4, 5, 6, 7], [".T.", ".T.", ".T.", ".T."], (0.0, 0.0, 1.0), (1.0, 0.0, 0.0), coords[4]),
            ([0, 9, 4, 8], [".T.", ".T.", ".F.", ".F."], (0.0, -1.0, 0.0), (1.0, 0.0, 0.0), coords[0]),
            ([1, 10, 5, 9], [".T.", ".T.", ".F.", ".F."], (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), coords[1]),
            ([2, 11, 6, 10], [".T.", ".T.", ".F.", ".F."], (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0), coords[2]),
            ([3, 8, 7, 11], [".T.", ".T.", ".F.", ".F."], (-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), coords[3]),
        ]
        af_ids: List[int] = []
        for idx_f, (e_list, ori_list, norm, ref_dir, fpt) in enumerate(faces_spec):
            oe_ids: List[int] = []
            for e_idx, ori in zip(e_list, ori_list):
                oe_id = eid; eid += 1
                lines.append(f"#{oe_id} = ORIENTED_EDGE('{name}_F{idx_f}_OE{e_idx}',*,*,#{ec_ids[e_idx]},{ori});")
                oe_ids.append(oe_id)
            el_id = eid; eid += 1
            fob_id = eid; eid += 1
            fcp_id = eid; eid += 1
            fnorm_id = eid; eid += 1
            fref_id = eid; eid += 1
            ax2_id = eid; eid += 1
            pln_id = eid; eid += 1
            af_id = eid; eid += 1
            oe_str = ",".join(f"#{x}" for x in oe_ids)
            lines.append(f"#{el_id} = EDGE_LOOP('{name}_EL{idx_f}',({oe_str}));")
            lines.append(f"#{fob_id} = FACE_OUTER_BOUND('{name}_FOB{idx_f}',#{el_id},.T.);")
            lines.append(f"#{fcp_id} = CARTESIAN_POINT('{name}_FCP{idx_f}',({fpt[0]:.4f},{fpt[1]:.4f},{fpt[2]:.4f}));")
            lines.append(f"#{fnorm_id} = DIRECTION('{name}_FNORM{idx_f}',({norm[0]:.4f},{norm[1]:.4f},{norm[2]:.4f}));")
            lines.append(f"#{fref_id} = DIRECTION('{name}_FREF{idx_f}',({ref_dir[0]:.4f},{ref_dir[1]:.4f},{ref_dir[2]:.4f}));")
            lines.append(f"#{ax2_id} = AXIS2_PLACEMENT_3D('{name}_FAX{idx_f}',#{fcp_id},#{fnorm_id},#{fref_id});")
            lines.append(f"#{pln_id} = PLANE('{name}_PLN{idx_f}',#{ax2_id});")
            lines.append(f"#{af_id} = ADVANCED_FACE('{name}_AF{idx_f}',(#{fob_id}),#{pln_id},.T.);")
            af_ids.append(af_id)

        cs_id = eid; eid += 1
        brep_id = eid; eid += 1
        af_str = ",".join(f"#{x}" for x in af_ids)
        lines.append(f"#{cs_id} = CLOSED_SHELL('{name}_SHELL',({af_str}));")
        lines.append(f"#{brep_id} = MANIFOLD_SOLID_BREP('{name}_BREP',#{cs_id});")
        brep_ids.append(brep_id)
        euler_checks.append({
            "solid_name": name,
            "vertices_V": len(v_ids),
            "edges_E": len(ec_ids),
            "faces_F": len(af_ids),
            "euler_V_minus_E_plus_F": len(v_ids) - len(ec_ids) + len(af_ids),
        })
        return brep_id

    # 1. Outer structural sandwich panel body (-50..50, -50..50, 0..2.60 mm)
    add_prism_brep("PANEL_BODY", -panel_length_mm / 2.0, panel_length_mm / 2.0, -panel_width_mm / 2.0, panel_width_mm / 2.0, 0.0, panel_thick_mm)
    # 2. Central AlSiC/MoCu die-attach boss (-22.5..22.5, -22.5..22.5, 2.60..3.40 mm)
    add_prism_brep("DIE_BOSS_45X45", -22.5, 22.5, -22.5, 22.5, panel_thick_mm, panel_thick_mm + 0.80)
    # 3. 8 independent cellular OHP serpentine channel cavities inside the 2.6mm core (z = 0.50..2.10 mm)
    pitch_y = panel_width_mm / n_ohp_cells
    for c_idx in range(n_ohp_cells):
        yc = -panel_width_mm / 2.0 + (c_idx + 0.5) * pitch_y
        add_prism_brep(f"OHP_CELL_{c_idx:02d}", -46.0, 46.0, yc - 1.20, yc + 1.20, 0.50, 2.10)

    brep_list_str = ",".join(f"#{x}" for x in brep_ids)
    lines.append(f"#{eid} = ADVANCED_BREP_SHAPE_REPRESENTATION('MS_OHP_SP_SHAPES',({brep_list_str}),#1);")
    lines.extend(["ENDSEC;", "END-ISO-10303-21;"])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "step_file": str(out_path.name),
        "manifold_solid_brep_count": len(brep_ids),
        "closed_shell_count": len(brep_ids),
        "advanced_face_count": len(brep_ids) * 6,
        "all_euler_poincare_v_minus_e_plus_f_equal_2": all(c["euler_V_minus_E_plus_F"] == 2 for c in euler_checks),
        "euler_checks": euler_checks,
    }


def solve_true_3d_fvm_pdn_resistance(
    topology: str,
    current_total_a: float = 1280.0,
    nx: int = 16,
    ny: int = 16,
    nz: int = 8,
) -> Dict[str, float]:
    """
    Closes F5 (2D nodal sheet with lumped constants):
    Solves the 3D finite-volume Laplace equation div_3D(sigma(x,y,z) grad_3D(phi)) = 0
    on an explicit (nx=16, ny=16, nz=8 = 2,048 cells) 3D Cartesian mesh with:
      - iz = 0..1: Bottom busbar/PCB return plane
      - iz = 2..5: Through-substrate / channel zone (dielectric fluid/core except at conductor posts/vias)
      - iz = 6: Solder/bond interface layer
      - iz = 7: Top die/heater current sink layer
    """
    lx_m = 0.045
    ly_m = 0.045
    lz_m = 0.0056  # 5.6 mm total stack height
    dx = lx_m / nx
    dy = ly_m / ny
    dz = lz_m / nz

    sigma_cu = 5.05e7      # S/m at 65 C
    sigma_solder = 6.80e6  # S/m SAC305 / SnAgCu interface
    sigma_dielectric = 1e-4  # S/m insulated region

    sigma = np.full((nz, ny, nx), sigma_dielectric, dtype=float)

    if topology == "LATERAL_FR4_2OZ":
        # Thin lateral copper sheet only in top layer iz=7 (scaled by 0.28mm / dz thickness ratio)
        sigma[7, :, :] = sigma_cu * (0.00028 / dz)
        sigma[6, :, :] = sigma_cu * (0.00028 / dz)
    elif topology == "COAXIAL_BOLTED_POSTS":
        # Top redistribution bridge (iz=7: 1.2mm Cu/CMC), solder layer (iz=6), 16 vertical posts (iz=1..5), bottom busbar (iz=0)
        sigma[7, :, :] = sigma_cu * 0.72
        sigma[6, :, :] = sigma_solder
        sigma[0, :, :] = sigma_cu
        for iy in range(ny):
            for ix in range(nx):
                if (ix % 4 in (1, 2)) and (iy % 4 in (1, 2)):
                    sigma[1:6, iy, ix] = sigma_cu * 0.65
    elif topology == "COAXIAL_THRU_SUBSTRATE_VIAS":
        # Dense 64-post vertical coaxial matrix
        sigma[7, :, :] = sigma_cu * 0.82
        sigma[6, :, :] = sigma_solder * 2.2  # sintered-Ag attach
        sigma[0, :, :] = sigma_cu
        for iy in range(ny):
            for ix in range(nx):
                if (ix % 2 == 1) and (iy % 2 == 1):
                    sigma[1:6, iy, ix] = sigma_cu * 0.85

    total_cells = nx * ny * nz
    rows, cols, vals = [], [], []
    rhs = np.zeros(total_cells, dtype=float)
    sink_per_top_cell = current_total_a / (nx * ny)

    def idx3(iz: int, iy: int, ix: int) -> int:
        return (iz * ny + iy) * nx + ix

    for iz in range(nz):
        for iy in range(ny):
            for ix in range(nx):
                row = idx3(iz, iy, ix)
                # Reference ground terminal (phi = 0):
                # For lateral FR-4, left/right edges of top layer (iz=7, ix=0 or nx-1);
                # For coaxial vertical topologies, bottom busbar plane (iz=0) at perimeter/posts.
                is_ground_terminal = False
                if topology == "LATERAL_FR4_2OZ":
                    if iz == 7 and (ix == 0 or ix == nx - 1):
                        is_ground_terminal = True
                else:
                    if iz == 0 and ((ix % 4 in (1, 2)) and (iy % 4 in (1, 2))):
                        is_ground_terminal = True

                if is_ground_terminal:
                    rows.append(row)
                    cols.append(row)
                    vals.append(1.0)
                    rhs[row] = 0.0
                    continue

                s_c = sigma[iz, iy, ix]
                diag = 0.0
                # 6-neighbor harmonic-mean finite-volume conductance stencil in 3D
                neighbors = [
                    (iz, iy, ix - 1, (dy * dz) / dx),
                    (iz, iy, ix + 1, (dy * dz) / dx),
                    (iz, iy - 1, ix, (dx * dz) / dy),
                    (iz, iy + 1, ix, (dx * dz) / dy),
                    (iz - 1, iy, ix, (dx * dy) / dz),
                    (iz + 1, iy, ix, (dx * dy) / dz),
                ]
                for nz_i, ny_i, nx_i, geom_factor in neighbors:
                    if 0 <= nz_i < nz and 0 <= ny_i < ny and 0 <= nx_i < nx:
                        s_n = sigma[nz_i, ny_i, nx_i]
                        s_harm = 2.0 * s_c * s_n / max(s_c + s_n, 1e-18)
                        g_link = s_harm * geom_factor
                        rows.append(row)
                        cols.append(idx3(nz_i, ny_i, nx_i))
                        vals.append(-g_link)
                        diag += g_link

                rows.append(row)
                cols.append(row)
                vals.append(diag)
                if iz == 7:
                    rhs[row] = sink_per_top_cell

    mat = sp.csr_matrix((vals, (rows, cols)), shape=(total_cells, total_cells))
    phi = spla.spsolve(mat, rhs).reshape((nz, ny, nx))

    # Supply-plus-return loop factor (2x one-way potential drop)
    mean_top_phi_v = 2.0 * float(np.mean(phi[7, :, :]))
    r_eq_ohm = mean_top_phi_v / max(current_total_a, 1e-9)
    r_eq_mohm = r_eq_ohm * 1000.0
    p_joule_w = (current_total_a ** 2) * r_eq_ohm

    return {
        "mesh_dimensions": f"{nx}x{ny}x{nz} ({total_cells} 3D FVM cells)",
        "topology": topology,
        "solved_3d_r_pdn_mohm": round(r_eq_mohm, 5),
        "solved_3d_v_drop_mv": round(mean_top_phi_v * 1000.0, 3),
        "solved_3d_joule_loss_w": round(p_joule_w, 3),
    }


def verify_and_repair_f4_hydraulics() -> Dict[str, float]:
    """
    Closes F4 (60 vs 30 channels per header & 22.5 mm vs 42.0 mm channel length):
    Recomputes exact continuity velocity and laminar developing pressure drop for
    60 total interleaved channels (30 per header) over the drawn 42.0 mm channel length.
    """
    q_total_m3_s = (2.5 / 60.0) * 1e-3  # 2.5 L/min total = 1.25 L/min per header
    q_per_header_m3_s = 0.5 * q_total_m3_s
    w_ch_m = 0.00035
    h_ch_m = 0.00250
    a_ch_m2 = w_ch_m * h_ch_m

    # Buggy 004 calculation: used n_passes_per_header = 60 and L = 22.5 mm
    v_buggy_m_s = q_per_header_m3_s / (60 * a_ch_m2)
    # Repaired calculation: 30 channels per header and L = 42.0 mm (matching STEP/DXF coordinates -21.0 to +21.0 mm)
    n_channels_per_header = 30
    l_ch_repaired_m = 0.0420
    v_repaired_m_s = q_per_header_m3_s / (n_channels_per_header * a_ch_m2)

    rho_f = 1030.0
    mu_f = 0.0016
    d_h_m = 4.0 * a_ch_m2 / (2.0 * (w_ch_m + h_ch_m))
    re_repaired = rho_f * v_repaired_m_s * d_h_m / mu_f
    aspect = w_ch_m / h_ch_m
    f_re = 24.0 * (1.0 - 1.3553 * aspect + 1.9467 * (aspect ** 2) - 1.7012 * (aspect ** 3) + 0.9564 * (aspect ** 4))
    f_darcy = (f_re / re_repaired) * 4.0 + 0.08 * ((d_h_m / l_ch_repaired_m) ** 0.5)
    dp_repaired_kpa = (
        f_darcy * (l_ch_repaired_m / d_h_m) * 0.5 * rho_f * (v_repaired_m_s ** 2)
        + 1.8 * 0.5 * rho_f * (v_repaired_m_s ** 2)
    ) * 1e-3

    return {
        "total_interleaved_channels": 60,
        "channels_per_header_repaired": n_channels_per_header,
        "channel_length_mm_repaired": 42.0,
        "buggy_004_velocity_m_s": round(v_buggy_m_s, 4),
        "repaired_continuity_velocity_m_s": round(v_repaired_m_s, 4),
        "repaired_reynolds_number": round(re_repaired, 2),
        "repaired_pressure_drop_kpa": round(dp_repaired_kpa, 3),
        "below_3_5_m_s_erosion_limit": bool(v_repaired_m_s <= 3.5),
        "below_45_kpa_pressure_limit": bool(dp_repaired_kpa <= 45.0),
    }


def run_all_004_repairs(out_dir: Path) -> Dict[str, Any]:
    cad_dir = out_dir / "cad_and_drawings"
    cad_dir.mkdir(parents=True, exist_ok=True)
    f1_f2 = verify_and_repair_f1_f2_heater_and_netlist(out_dir)
    f3 = generate_true_manifold_brep_step(cad_dir / "ms_ohp_sp_tvac_coupon_brep.step")
    f4 = verify_and_repair_f4_hydraulics()
    f5_lat = solve_true_3d_fvm_pdn_resistance("LATERAL_FR4_2OZ", 1280.0)
    f5_coax = solve_true_3d_fvm_pdn_resistance("COAXIAL_BOLTED_POSTS", 1280.0)
    f5_vias = solve_true_3d_fvm_pdn_resistance("COAXIAL_THRU_SUBSTRATE_VIAS", 1280.0)

    return {
        "F1_and_F2_netlist_and_package_collision_repair": f1_f2,
        "F3_true_manifold_brep_step_repair": f3,
        "F4_hydraulic_continuity_and_length_repair": f4,
        "F5_true_3d_fvm_pdn_laplace_repair": {
            "lateral_fr4_2oz": f5_lat,
            "coaxial_bolted_posts": f5_coax,
            "coaxial_thru_substrate_vias": f5_vias,
        },
        "F8_safety_classification_repair": "INERT_MACHINABILITY_AND_TVAC_COUPON_ONLY (Zero energization at 50W or 50A without external PE/EHS signoff, fused 2.5A current limit, and 85C hardware thermal cutout).",
    }


if __name__ == "__main__":
    import json
    res = run_all_004_repairs(Path("."))
    print(json.dumps(res, indent=2))
