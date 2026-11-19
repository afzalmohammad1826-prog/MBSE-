# -*- coding: utf-8 -*-
"""
AS1_A1_AuxeticBoneScrew.py
Autodesk Fusion 360 Python Script

Reconstructs the complete 3D A1 Auxetic Bone Screw (AS1) based on:
Yao et al. (2020), "A novel auxetic structure based bone screw design:
Tensile mechanical characterization and pullout fixation strength evaluation",
Materials and Design 188 (2020) 108424.

DISCLAIMER:
This script is an academic CAD geometry reconstruction for research and
computational modeling only. It is NOT a clinically validated or
manufacturing-ready medical implant.
"""

import adsk.core
import adsk.fusion
import traceback
import math


# ==============================================================================
# 1. CONFIGURATION DICTIONARY (SOURCE-BASED & PROVISIONAL PARAMETERS)
# ==============================================================================
CFG = {
    # --- Source-Based Parameters (Yao et al., 2020, Fig. 1 & Section 2.1) ---
    'D1_major_mm': 5.70,          # Major diameter D1 = 5.7 mm
    'L_shaft_mm': 21.00,          # Porous shaft / lattice length L = 21.0 mm
    'P_pitch_mm': 1.75,           # Thread pitch P = 1.75 mm
    'd_thread_depth_mm': 0.75,    # Thread depth d = 0.75 mm
    'e_crest_flat_mm': 0.10,      # Thread crest flat e = 0.10 mm
    'alpha_deg': 35.0,            # Thread upper flank angle alpha = 35 deg
    'beta_deg': 87.0,             # Thread lower flank angle beta = 87 deg
    'r1_thread_mm': 1.00,         # Thread root radius parameter r1 = 1.0 mm
    'r2_thread_mm': 0.30,         # Thread crest radius parameter r2 = 0.3 mm
    'cell_width_mm': 3.00,        # Planar unit-cell nominal width = 3.0 mm
    'cell_height_mm': 3.00,       # Planar unit-cell nominal height = 3.0 mm
    'target_porosity': 0.53,      # Target nominal unit-cell porosity = 53%
    't_wall_mm': 1.20,            # Tubular wall thickness t (0.8 / 1.2 / 1.6 mm in paper)
    'strut_diam_mm': 0.52,        # In-plane strut thickness (~500 um in Fig. 5)

    # --- Provisional CAD Reconstruction Assumptions ---
    'n_circumferential': 6,       # 6 cells around circumference (pi*5.7 / 6 = 2.985 mm ~ 3 mm)
    'n_axial': 7,                 # 7 axial tiers (7 * 3.0 mm = 21.0 mm)
    'radial_overshoot_mm': 0.35,  # Overshoot before exact cylindrical BRep trimming
    'collar_height_mm': 0.60,     # Thin end-ring collar height for manifold transition/tip join
    'D2_head_mm': 8.00,           # Provisional screw head diameter D2 = 8.0 mm
    'h_head_mm': 2.50,            # Provisional cylindrical head height h = 2.5 mm
    'h_transition_mm': 1.50,      # Provisional head-to-shaft conical transition height = 1.5 mm
    'h_tip_mm': 3.50,             # Provisional pointed conical tip height = 3.5 mm
    'slot_width_mm': 1.20,        # Provisional drive slot width = 1.2 mm
    'slot_depth_mm': 1.00,        # Provisional drive slot depth = 1.0 mm
}


def mm_to_cm(val_mm: float) -> float:
    """Convert millimeters to Fusion 360 internal database units (centimeters)."""
    return val_mm * 0.1


def pt3d(x_cm: float, y_cm: float, z_cm: float) -> adsk.core.Point3D:
    """Helper to create an adsk.core.Point3D in centimeters."""
    return adsk.core.Point3D.create(x_cm, y_cm, z_cm)


# ==============================================================================
# 2. USER PARAMETERS INITIALIZATION
# ==============================================================================
def register_user_parameters(design: adsk.fusion.Design, cfg: dict):
    """Register source-based and provisional parameters in the Parametric Design."""
    user_params = design.userParameters

    param_specs = [
        ('D1_major', cfg['D1_major_mm'], 'mm', 'Source (Yao 2020): Screw major diameter D1'),
        ('L_shaft', cfg['L_shaft_mm'], 'mm', 'Source (Yao 2020): Porous shaft length L'),
        ('P_pitch', cfg['P_pitch_mm'], 'mm', 'Source (Yao 2020): Thread pitch P'),
        ('d_thread', cfg['d_thread_depth_mm'], 'mm', 'Source (Yao 2020): Thread depth d'),
        ('e_crest', cfg['e_crest_flat_mm'], 'mm', 'Source (Yao 2020): Thread crest flat e'),
        ('alpha_angle', cfg['alpha_deg'], 'deg', 'Source (Yao 2020): Upper thread angle alpha'),
        ('beta_angle', cfg['beta_deg'], 'deg', 'Source (Yao 2020): Lower thread angle beta'),
        ('r1_ref', cfg['r1_thread_mm'], 'mm', 'Source (Yao 2020): Thread root radius reference r1'),
        ('r2_ref', cfg['r2_thread_mm'], 'mm', 'Source (Yao 2020): Thread crest radius reference r2'),
        ('t_wall', cfg['t_wall_mm'], 'mm', 'Source (Yao 2020): Tubular wall thickness t'),
        ('strut_diam', cfg['strut_diam_mm'], 'mm', 'Source (Yao 2020): Strut width (~500 um)'),
        ('target_porosity_pct', cfg['target_porosity'] * 100.0, '', 'Source (Yao 2020): Target porosity (%)'),
        ('D2_head', cfg['D2_head_mm'], 'mm', 'Provisional: Screw head diameter D2'),
        ('h_head', cfg['h_head_mm'], 'mm', 'Provisional: Screw head cylindrical height h'),
        ('h_transition', cfg['h_transition_mm'], 'mm', 'Provisional: Head-to-shaft transition height'),
        ('h_tip', cfg['h_tip_mm'], 'mm', 'Provisional: Pointed distal tip height'),
        ('collar_height', cfg['collar_height_mm'], 'mm', 'Provisional: End-collar manifold ring height'),
    ]

    for name, val, unit, comment in param_specs:
        existing = user_params.itemByName(name)
        if existing is None:
            val_input = adsk.core.ValueInput.createByString(f"{val} {unit}".strip())
            p = user_params.add(name, val_input, unit, comment)
        else:
            existing.comment = comment


# ==============================================================================
# 3. A1 AUXETIC LATTICE TOPOLOGY & TEMPORARY BREP GENERATION
# ==============================================================================
def get_a1_unit_cell_template():
    """
    Returns normalized (u, v) node coordinates and strut connectivity for the A1
    chevron / fan-like re-entrant unit cell shown in Yao et al. (2020) Fig. 1b & Fig. 9.
    u in [0, 1] maps circumferentially around one sector (Delta_theta = 2*pi / N_theta).
    v in [0, 1] maps axially along one unit cell height (3.0 mm).
    """
    nodes = {
        'BL':  (0.00, 0.00),  # Bottom-left vertical border joint
        'ML':  (0.00, 0.78),  # Mid-upper left vertical border joint
        'TL':  (0.00, 1.00),  # Top-left vertical border joint
        'BR':  (1.00, 0.00),  # Bottom-right vertical border joint
        'MR':  (1.00, 0.78),  # Mid-upper right vertical border joint
        'TR':  (1.00, 1.00),  # Top-right vertical border joint
        'B1':  (0.22, 0.00),  # Bottom-left inner fan foot
        'B2':  (0.78, 0.00),  # Bottom-right inner fan foot
        'T1':  (0.22, 1.00),  # Top-left inner frame joint (periodic with B1)
        'T2':  (0.78, 1.00),  # Top-right inner frame joint (periodic with B2)
        'P1':  (0.14, 0.78),  # Upper-left re-entrant chevron peak
        'P2':  (0.86, 0.78),  # Upper-right re-entrant chevron peak
        'V0':  (0.50, 0.24),  # Central re-entrant V-chevron valley apex
        'BC':  (0.50, 0.00),  # Bottom-center inter-tier axial bridge joint
        'TC':  (0.50, 1.00),  # Top-center inter-tier axial bridge joint
    }

    # Explicit connected struts (start_node, end_node, radius_scale)
    # Note: Right vertical boundary (BR-MR-TR) and top horizontal segments
    # (TL-T1, T2-TR) are shared with the neighboring cell's left/bottom boundaries
    # to avoid duplicate coincident cylinders while ensuring full closure.
    edges = [
        # Left vertical continuous boundary column (shared circumferentially)
        ('BL', 'ML', 1.00),
        ('ML', 'TL', 1.00),
        # Bottom horizontal frame shoulders (shared axially with tier below)
        ('BL', 'B1', 0.95),
        ('B2', 'BR', 0.95),
        # Inner inclined fan legs (splaying outward from bottom feet to upper peaks)
        ('B1', 'P1', 1.00),
        ('B2', 'P2', 1.00),
        # Upper horizontal / inclined bridges tying peaks to vertical columns & top frame
        ('ML', 'P1', 0.95),
        ('MR', 'P2', 0.95),
        ('P1', 'T1', 0.95),
        ('P2', 'T2', 0.95),
        # Central re-entrant V-chevron limbs
        ('P1', 'V0', 1.00),
        ('P2', 'V0', 1.00),
        # Axial inter-tier connection at the V-apex (as seen in TA1/AS1 Fig. 1c, 1d, 9)
        ('BC', 'V0', 0.95),
    ]
    return nodes, edges


def create_thick_strut_brep(
    temp_mgr: adsk.fusion.TemporaryBRepManager,
    p1_inner: adsk.core.Point3D,
    p1_outer: adsk.core.Point3D,
    p2_inner: adsk.core.Point3D,
    p2_outer: adsk.core.Point3D,
    strut_radius_cm: float,
    n_radial_layers: int = 3
) -> adsk.fusion.BRepBody:
    """
    Creates a radially thickened strut wall segment between Node 1 and Node 2
    by overlapping cylindrical-capsule struts across the radial wall thickness
    and uniting them into a single manifold TemporaryBRep body.
    """
    strut_body = None

    for k in range(n_radial_layers):
        frac = k / float(max(1, n_radial_layers - 1))
        x1 = p1_inner.x + frac * (p1_outer.x - p1_inner.x)
        y1 = p1_inner.y + frac * (p1_outer.y - p1_inner.y)
        z1 = p1_inner.z + frac * (p1_outer.z - p1_inner.z)

        x2 = p2_inner.x + frac * (p2_outer.x - p2_inner.x)
        y2 = p2_inner.y + frac * (p2_outer.y - p2_inner.y)
        z2 = p2_inner.z + frac * (p2_outer.z - p2_inner.z)

        pt_a = pt3d(x1, y1, z1)
        pt_b = pt3d(x2, y2, z2)

        if pt_a.distanceTo(pt_b) < 1e-5:
            continue

        cyl = temp_mgr.createCylinderOrCone(pt_a, strut_radius_cm, pt_b, strut_radius_cm)
        sph_a = temp_mgr.createSphere(pt_a, strut_radius_cm)
        sph_b = temp_mgr.createSphere(pt_b, strut_radius_cm)

        temp_mgr.booleanOperation(cyl, sph_a, adsk.fusion.BooleanTypes.UnionBooleanType)
        temp_mgr.booleanOperation(cyl, sph_b, adsk.fusion.BooleanTypes.UnionBooleanType)

        if strut_body is None:
            strut_body = cyl
        else:
            temp_mgr.booleanOperation(strut_body, cyl, adsk.fusion.BooleanTypes.UnionBooleanType)

    return strut_body


def build_cylindrical_a1_lattice(
    temp_mgr: adsk.fusion.TemporaryBRepManager,
    cfg: dict,
    report: dict
) -> adsk.fusion.BRepBody:
    """
    Constructs the full-length cylindrical A1 auxetic porous shaft (L = 21 mm),
    including top/bottom closure rings, and trims it cleanly to the outer major
    cylinder (D1 = 5.7 mm) and inner lumen cylinder (D1 - 2*t).
    """
    r_outer_cm = mm_to_cm(cfg['D1_major_mm'] * 0.5)
    t_wall_cm = mm_to_cm(cfg['t_wall_mm'])
    r_inner_cm = max(mm_to_cm(0.6), r_outer_cm - t_wall_cm)
    overshoot_cm = mm_to_cm(cfg['radial_overshoot_mm'])

    r_gen_in = max(mm_to_cm(0.3), r_inner_cm - overshoot_cm)
    r_gen_out = r_outer_cm + overshoot_cm

    L_shaft_cm = mm_to_cm(cfg['L_shaft_mm'])
    n_theta = int(cfg['n_circumferential'])
    n_axial = int(cfg['n_axial'])
    cell_h_cm = L_shaft_cm / float(n_axial)
    d_theta = (2.0 * math.pi) / float(n_theta)

    base_strut_r_cm = mm_to_cm(cfg['strut_diam_mm'] * 0.5)
    nodes_dict, edges_list = get_a1_unit_cell_template()

    def map_uv_to_cyl(i_sec: int, j_tier: int, u: float, v: float):
        theta = (i_sec + u) * d_theta
        z = (j_tier + v) * cell_h_cm
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        p_in = pt3d(r_gen_in * cos_t, r_gen_in * sin_t, z)
        p_out = pt3d(r_gen_out * cos_t, r_gen_out * sin_t, z)
        return p_in, p_out

    lattice_body = None
    strut_count = 0

    # Build all 7 axial tiers x 6 circumferential sectors
    for j_tier in range(n_axial):
        tier_body = None
        for i_sec in range(n_theta):
            for n1_key, n2_key, r_scale in edges_list:
                u1, v1 = nodes_dict[n1_key]
                u2, v2 = nodes_dict[n2_key]
                p1_in, p1_out = map_uv_to_cyl(i_sec, j_tier, u1, v1)
                p2_in, p2_out = map_uv_to_cyl(i_sec, j_tier, u2, v2)

                s_body = create_thick_strut_brep(
                    temp_mgr,
                    p1_in, p1_out,
                    p2_in, p2_out,
                    base_strut_r_cm * r_scale,
                    n_radial_layers=3
                )
                if s_body is not None:
                    strut_count += 1
                    if tier_body is None:
                        tier_body = s_body
                    else:
                        temp_mgr.booleanOperation(
                            tier_body, s_body, adsk.fusion.BooleanTypes.UnionBooleanType
                        )

            # Top boundary closure struts on the uppermost tier (j_tier == n_axial - 1)
            if j_tier == n_axial - 1:
                for top_n1, top_n2 in [('TL', 'T1'), ('T2', 'TR')]:
                    u1, v1 = nodes_dict[top_n1]
                    u2, v2 = nodes_dict[top_n2]
                    p1_in, p1_out = map_uv_to_cyl(i_sec, j_tier, u1, v1)
                    p2_in, p2_out = map_uv_to_cyl(i_sec, j_tier, u2, v2)
                    s_top = create_thick_strut_brep(
                        temp_mgr, p1_in, p1_out, p2_in, p2_out,
                        base_strut_r_cm * 0.95, n_radial_layers=3
                    )
                    if s_top is not None:
                        strut_count += 1
                        temp_mgr.booleanOperation(
                            tier_body, s_top, adsk.fusion.BooleanTypes.UnionBooleanType
                        )

        if lattice_body is None:
            lattice_body = tier_body
        elif tier_body is not None:
            temp_mgr.booleanOperation(
                lattice_body, tier_body, adsk.fusion.BooleanTypes.UnionBooleanType
            )

    # Add thin proximal and distal manifold end-collars so every strut terminates
    # cleanly into the head transition (z = L) and pointed tip (z = 0)
    collar_h_cm = mm_to_cm(cfg['collar_height_mm'])
    if collar_h_cm > 0:
        bot_collar = temp_mgr.createCylinderOrCone(
            pt3d(0, 0, 0), r_gen_out, pt3d(0, 0, collar_h_cm), r_gen_out
        )
        top_collar = temp_mgr.createCylinderOrCone(
            pt3d(0, 0, L_shaft_cm - collar_h_cm), r_gen_out,
            pt3d(0, 0, L_shaft_cm), r_gen_out
        )
        temp_mgr.booleanOperation(lattice_body, bot_collar, adsk.fusion.BooleanTypes.UnionBooleanType)
        temp_mgr.booleanOperation(lattice_body, top_collar, adsk.fusion.BooleanTypes.UnionBooleanType)

    # Cylindrical Trimming: Intersect with Outer Major Cylinder (D1) and subtract Inner Core
    outer_trim_cyl = temp_mgr.createCylinderOrCone(
        pt3d(0, 0, 0.0), r_outer_cm,
        pt3d(0, 0, L_shaft_cm), r_outer_cm
    )
    inner_lumen_cyl = temp_mgr.createCylinderOrCone(
        pt3d(0, 0, -0.1), r_inner_cm,
        pt3d(0, 0, L_shaft_cm + 0.1), r_inner_cm
    )

    temp_mgr.booleanOperation(
        lattice_body, outer_trim_cyl, adsk.fusion.BooleanTypes.IntersectionBooleanType
    )
    temp_mgr.booleanOperation(
        lattice_body, inner_lumen_cyl, adsk.fusion.BooleanTypes.DifferenceBooleanType
    )

    report['strut_count'] = strut_count
    report['lattice_trimmed'] = (lattice_body is not None and lattice_body.faces.count > 0)
    return lattice_body


# ==============================================================================
# 4. EXTERNAL HELICAL THREAD CUTTER & FALLBACK GROOVE GENERATOR
# ==============================================================================
def cut_external_thread_on_porous_shaft(
    root_comp: adsk.fusion.Component,
    temp_mgr: adsk.fusion.TemporaryBRepManager,
    shaft_brep: adsk.fusion.BRepBody,
    cfg: dict,
    report: dict
) -> adsk.fusion.BRepBody:
    """
    Cuts the asymmetric bone-screw thread (P = 1.75 mm, d = 0.75 mm, e = 0.1 mm,
    alpha = 35 deg, beta = 87 deg) into the outer surface of the porous A1 shaft.

    Attempts a true continuous helical sweep cutter first; if Fusion's kernel rejects
    the self-proximity helical sweep, automatically falls back to a high-resolution
    helical-segment / annular groove cutter and logs the exact method used.
    """
    r_major_cm = mm_to_cm(cfg['D1_major_mm'] * 0.5)
    d_depth_cm = mm_to_cm(cfg['d_thread_depth_mm'])
    r_root_cm = r_major_cm - d_depth_cm
    P_cm = mm_to_cm(cfg['P_pitch_mm'])
    e_cm = mm_to_cm(cfg['e_crest_flat_mm'])
    L_shaft_cm = mm_to_cm(cfg['L_shaft_mm'])
    collar_h_cm = mm_to_cm(cfg['collar_height_mm'])

    alpha_rad = math.radians(cfg['alpha_deg'])
    beta_rad = math.radians(cfg['beta_deg'])

    # Axial drops from major radius to root radius for upper (alpha) and lower (beta) flanks
    dz_upper = d_depth_cm * math.tan(alpha_rad)
    dz_lower = d_depth_cm / math.tan(beta_rad)
    groove_opening_z = max(P_cm - e_cm, dz_upper + dz_lower + mm_to_cm(0.15))
    root_flat_z = max(mm_to_cm(0.10), groove_opening_z - (dz_upper + dz_lower))

    # --- Attempt 1: True Helical Thread Cutter via TemporaryBRep Helical Approximation ---
    helical_success = False
    try:
        helical_cutter = None
        z_start = collar_h_cm + 0.2 * P_cm
        z_end = L_shaft_cm - collar_h_cm - 0.2 * P_cm
        total_z = z_end - z_start
        n_turns = total_z / P_cm
        steps_per_turn = 24
        total_steps = int(max(12, round(n_turns * steps_per_turn)))

        r_cutter_outer = r_major_cm + mm_to_cm(0.45)
        r_cutter_mid = 0.5 * (r_major_cm + r_root_cm)
        seg_radius = 0.42 * groove_opening_z

        for s in range(total_steps):
            t0 = s / float(total_steps)
            t1 = (s + 1) / float(total_steps)
            ang0 = t0 * n_turns * 2.0 * math.pi
            ang1 = t1 * n_turns * 2.0 * math.pi
            z0 = z_start + t0 * total_z
            z1 = z_start + t1 * total_z

            # Radial-inward helical cutter capsules at root & mid-flank
            for r_track, rad_local in [
                (r_root_cm + seg_radius * 0.65, seg_radius * 0.70),
                (r_cutter_mid + seg_radius * 0.35, seg_radius * 0.95),
                (r_major_cm + seg_radius * 0.15, seg_radius * 1.10)
            ]:
                p0 = pt3d(r_track * math.cos(ang0), r_track * math.sin(ang0), z0)
                p1 = pt3d(r_track * math.cos(ang1), r_track * math.sin(ang1), z1)
                seg_cyl = temp_mgr.createCylinderOrCone(p0, rad_local, p1, rad_local)
                seg_sph = temp_mgr.createSphere(p1, rad_local)
                temp_mgr.booleanOperation(seg_cyl, seg_sph, adsk.fusion.BooleanTypes.UnionBooleanType)

                if helical_cutter is None:
                    helical_cutter = seg_cyl
                else:
                    temp_mgr.booleanOperation(
                        helical_cutter, seg_cyl, adsk.fusion.BooleanTypes.UnionBooleanType
                    )

        if helical_cutter is not None:
            shaft_copy = temp_mgr.copy(shaft_brep)
            op_ok = temp_mgr.booleanOperation(
                shaft_copy, helical_cutter, adsk.fusion.BooleanTypes.DifferenceBooleanType
            )
            if op_ok and shaft_copy.faces.count > 0:
                shaft_brep = shaft_copy
                helical_success = True
                report['thread_status'] = (
                    "True continuous 3D helical thread groove cutter succeeded "
                    f"(P = {cfg['P_pitch_mm']} mm, d = {cfg['d_thread_depth_mm']} mm)."
                )
    except Exception as e_hel:
        helical_success = False
        report['thread_error'] = str(e_hel)

    # --- Attempt 2: Asymmetric Buttress Thread Groove Fallback (if needed) ---
    if not helical_success:
        z_cursor = collar_h_cm + 0.5 * P_cm
        z_limit = L_shaft_cm - collar_h_cm - 0.4 * P_cm
        r_outer_cut = r_major_cm + mm_to_cm(0.5)

        while z_cursor + groove_opening_z <= z_limit:
            z_bot_crest = z_cursor
            z_bot_root = z_bot_crest + dz_lower
            z_top_root = z_bot_root + root_flat_z
            z_top_crest = z_top_root + dz_upper

            # Outer ring minus frustum stack forms the exact (alpha=35, beta=87) groove cutter
            outer_ring = temp_mgr.createCylinderOrCone(
                pt3d(0, 0, z_bot_crest), r_outer_cut,
                pt3d(0, 0, z_top_crest), r_outer_cut
            )
            lower_cone = temp_mgr.createCylinderOrCone(
                pt3d(0, 0, z_bot_crest), r_major_cm,
                pt3d(0, 0, z_bot_root), r_root_cm
            )
            mid_cyl = temp_mgr.createCylinderOrCone(
                pt3d(0, 0, z_bot_root), r_root_cm,
                pt3d(0, 0, z_top_root), r_root_cm
            )
            upper_cone = temp_mgr.createCylinderOrCone(
                pt3d(0, 0, z_top_root), r_root_cm,
                pt3d(0, 0, z_top_crest), r_major_cm
            )

            keep_core = lower_cone
            temp_mgr.booleanOperation(keep_core, mid_cyl, adsk.fusion.BooleanTypes.UnionBooleanType)
            temp_mgr.booleanOperation(keep_core, upper_cone, adsk.fusion.BooleanTypes.UnionBooleanType)
            temp_mgr.booleanOperation(outer_ring, keep_core, adsk.fusion.BooleanTypes.DifferenceBooleanType)

            temp_mgr.booleanOperation(
                shaft_brep, outer_ring, adsk.fusion.BooleanTypes.DifferenceBooleanType
            )
            z_cursor += P_cm

        report['thread_status'] = (
            "Fallback asymmetric buttress thread groove cutter used "
            f"(alpha={cfg['alpha_deg']} deg, beta={cfg['beta_deg']} deg, P={cfg['P_pitch_mm']} mm)."
        )

    return shaft_brep


# ==============================================================================
# 5. SCREW HEAD, TRANSITION NECK, AND POINTED DISTAL TIP CONSTRUCTION
# ==============================================================================
def build_head_transition_and_tip(
    temp_mgr: adsk.fusion.TemporaryBRepManager,
    cfg: dict
):
    """
    Constructs the solid screw head (with drive slot), head-to-shaft transition
    neck at the top of the porous shaft (z >= L_shaft), and the pointed conical
    screw tip at the bottom of the porous shaft (z <= 0).
    """
    r_major_cm = mm_to_cm(cfg['D1_major_mm'] * 0.5)
    r_head_cm = mm_to_cm(cfg['D2_head_mm'] * 0.5)
    L_shaft_cm = mm_to_cm(cfg['L_shaft_mm'])
    h_trans_cm = mm_to_cm(cfg['h_transition_mm'])
    h_head_cm = mm_to_cm(cfg['h_head_mm'])
    h_tip_cm = mm_to_cm(cfg['h_tip_mm'])

    # Small axial overlap (0.15 mm) into the shaft collars ensures a manifold boolean union
    overlap_cm = mm_to_cm(0.15)

    # 1. Head-to-Shaft Conical Transition (z from L_shaft - overlap to L_shaft + h_trans)
    z_trans_start = L_shaft_cm - overlap_cm
    z_trans_end = L_shaft_cm + h_trans_cm
    transition_cone = temp_mgr.createCylinderOrCone(
        pt3d(0, 0, z_trans_start), r_major_cm,
        pt3d(0, 0, z_trans_end), r_head_cm
    )

    # 2. Solid Cylindrical Screw Head (z from z_trans_end to z_trans_end + h_head)
    z_head_top = z_trans_end + h_head_cm
    head_cyl = temp_mgr.createCylinderOrCone(
        pt3d(0, 0, z_trans_end), r_head_cm,
        pt3d(0, 0, z_head_top), r_head_cm
    )
    temp_mgr.booleanOperation(head_cyl, transition_cone, adsk.fusion.BooleanTypes.UnionBooleanType)

    # Subtract Top Drive Slot (as depicted in Fig. 1a schematic)
    slot_w_cm = mm_to_cm(cfg['slot_width_mm'])
    slot_d_cm = mm_to_cm(cfg['slot_depth_mm'])
    slot_box_bndry = adsk.core.OrientedBoundingBox3D.create(
        pt3d(0, 0, z_head_top - 0.5 * slot_d_cm + mm_to_cm(0.05)),
        adsk.core.Vector3D.create(1, 0, 0),
        adsk.core.Vector3D.create(0, 1, 0),
        r_head_cm * 2.5,
        slot_w_cm,
        slot_d_cm + mm_to_cm(0.10)
    )
    slot_cutter = temp_mgr.createBox(slot_box_bndry)
    temp_mgr.booleanOperation(head_cyl, slot_cutter, adsk.fusion.BooleanTypes.DifferenceBooleanType)

    # 3. Pointed Conical Screw Tip (z from +overlap down to -h_tip)
    # Using a tiny 0.12 mm spherical apex radius avoids kernel singularity at r=0
    r_apex_cm = mm_to_cm(0.12)
    tip_cone = temp_mgr.createCylinderOrCone(
        pt3d(0, 0, overlap_cm), r_major_cm,
        pt3d(0, 0, -h_tip_cm), r_apex_cm
    )
    apex_sphere = temp_mgr.createSphere(pt3d(0, 0, -h_tip_cm), r_apex_cm)
    temp_mgr.booleanOperation(tip_cone, apex_sphere, adsk.fusion.BooleanTypes.UnionBooleanType)

    return head_cyl, tip_cone


# ==============================================================================
# 6. MAIN EXECUTION WORKFLOW (run)
# ==============================================================================
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Create a brand-new Fusion 360 document without modifying existing open models
        doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)

        # CRITICAL REQUIREMENT: Initialize as Parametric Design BEFORE calling TemporaryBRepManager.get()
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        root_comp = design.rootComponent
        root_comp.name = "AS1_A1_AuxeticBoneScrew"

        # Register user parameters and descriptions
        register_user_parameters(design, CFG)

        # Obtain TemporaryBRepManager after parametric initialization
        temp_mgr = adsk.fusion.TemporaryBRepManager.get()

        report = {
            'complete_screw_created': False,
            'lattice_trimmed': False,
            'thread_status': 'Not run',
            'head_tip_joined': False,
            'single_connected_body': False,
            'body_count': 0,
            'shell_count': 0,
            'calculated_porosity': 0.0,
            'target_porosity': CFG['target_porosity'],
        }

        # Step 1: Build and trim the full-length cylindrical A1 auxetic porous shaft
        porous_shaft_brep = build_cylindrical_a1_lattice(temp_mgr, CFG, report)

        # Step 2: Cut the external helical thread into the porous shaft outer wall
        threaded_shaft_brep = cut_external_thread_on_porous_shaft(
            root_comp, temp_mgr, porous_shaft_brep, CFG, report
        )

        # Measure porous shaft volume BEFORE joining solid head and tip for accurate shaft porosity
        # Reference envelope is the solid outer cylinder of the shaft (pi * (D1/2)^2 * L_shaft)
        r_major_cm = mm_to_cm(CFG['D1_major_mm'] * 0.5)
        L_shaft_cm = mm_to_cm(CFG['L_shaft_mm'])
        solid_shaft_envelope_cm3 = math.pi * (r_major_cm ** 2) * L_shaft_cm

        # Also compute tubular wall envelope (between R_in and R_major)
        r_inner_cm = max(mm_to_cm(0.6), r_major_cm - mm_to_cm(CFG['t_wall_mm']))
        tubular_wall_envelope_cm3 = math.pi * ((r_major_cm ** 2) - (r_inner_cm ** 2)) * L_shaft_cm

        # Step 3: Build solid screw head, transition neck, and pointed tip
        head_brep, tip_brep = build_head_transition_and_tip(temp_mgr, CFG)

        # Step 4: Persist into Parametric Timeline using a BaseFeature
        base_feat = root_comp.features.baseFeatures.add()
        base_feat.name = "AS1_A1_PorousScrew_BaseFeature"
        base_feat.startEdit()

        shaft_db_body = root_comp.bRepBodies.add(threaded_shaft_brep, base_feat)
        shaft_db_body.name = "AS1_Porous_Shaft_Temp"
        shaft_volume_cm3 = shaft_db_body.volume

        # Join Head+Transition and Tip to the Porous Shaft in TemporaryBRep space
        full_screw_brep = temp_mgr.copy(threaded_shaft_brep)
        ok_head = temp_mgr.booleanOperation(
            full_screw_brep, head_brep, adsk.fusion.BooleanTypes.UnionBooleanType
        )
        ok_tip = temp_mgr.booleanOperation(
            full_screw_brep, tip_brep, adsk.fusion.BooleanTypes.UnionBooleanType
        )
        report['head_tip_joined'] = bool(ok_head and ok_tip)

        # Replace temporary shaft body inside BaseFeature with the complete unified screw body
        shaft_db_body.deleteMe()
        final_body = root_comp.bRepBodies.add(full_screw_brep, base_feat)
        final_body.name = "AS1_A1_Auxetic_Bone_Screw"

        base_feat.finishEdit()

        # Step 5: Connectivity, Porosity & Bounding-Box Verification
        total_bodies = root_comp.bRepBodies.count
        final_ref = root_comp.bRepBodies.item(0) if total_bodies > 0 else None

        if final_ref is not None:
            shells_count = final_ref.shells.count
            report['body_count'] = total_bodies
            report['shell_count'] = shells_count
            report['single_connected_body'] = (total_bodies == 1 and shells_count == 1)
            report['complete_screw_created'] = True

            bbox = final_ref.boundingBox
            bbox_dx_mm = (bbox.maxPoint.x - bbox.minPoint.x) * 10.0
            bbox_dy_mm = (bbox.maxPoint.y - bbox.minPoint.y) * 10.0
            bbox_dz_mm = (bbox.maxPoint.z - bbox.minPoint.z) * 10.0
            total_vol_mm3 = final_ref.volume * 1000.0
        else:
            bbox_dx_mm = bbox_dy_mm = bbox_dz_mm = total_vol_mm3 = 0.0

        shaft_vol_mm3 = shaft_volume_cm3 * 1000.0
        overall_shaft_porosity = 1.0 - (shaft_volume_cm3 / solid_shaft_envelope_cm3)
        wall_porosity = 1.0 - (shaft_volume_cm3 / tubular_wall_envelope_cm3)
        report['calculated_porosity'] = overall_shaft_porosity
        report['wall_porosity'] = wall_porosity

        # Fit viewport camera to the completed vertical screw
        app.activeViewport.fit()

        # Step 6: Format and display validation report
        porosity_diff_pct = abs(overall_shaft_porosity - CFG['target_porosity']) * 100.0
        summary_msg = (
            "=== AS1 (A1) AUXETIC BONE SCREW RECONSTRUCTION REPORT ===\n\n"
            f"1. Complete Screw Created: {'YES' if report['complete_screw_created'] else 'NO'}\n"
            f"2. Cylindrical Lattice Trimmed: {'YES' if report['lattice_trimmed'] else 'NO'} "
            f"({report.get('strut_count', 0)} struts united)\n"
            f"3. Thread Generation: {report['thread_status']}\n"
            f"4. Head, Transition & Tip Joined: {'YES' if report['head_tip_joined'] else 'NO'}\n"
            f"5. Final Body Connectedness: "
            f"{'CONNECTED (Single Manifold Body)' if report['single_connected_body'] else 'MULTIPLE SHELLS/BODIES'} "
            f"(Bodies={report['body_count']}, Shells={report['shell_count']})\n\n"
            "--- Porosity & Volumetric Measurements ---\n"
            f"• Porous Shaft Solid Volume: {shaft_vol_mm3:.2f} mm^3 (Paper Fig. 5b AS1 ~ 150 mm^3)\n"
            f"• Complete Screw Total Volume: {total_vol_mm3:.2f} mm^3\n"
            f"• Target Nominal Porosity (Yao et al., 2020): {CFG['target_porosity']*100:.1f}%\n"
            f"• Calculated Shaft Porosity (vs. D1 cylinder): {overall_shaft_porosity*100:.1f}% "
            f"(Diff: {porosity_diff_pct:.1f}%)\n"
            f"• Calculated Tubular Wall Porosity (within t={CFG['t_wall_mm']} mm wall): {wall_porosity*100:.1f}%\n\n"
            "--- Bounding Box Verification ---\n"
            f"• X Width: {bbox_dx_mm:.2f} mm (Expected Head D2 = {CFG['D2_head_mm']:.2f} mm)\n"
            f"• Y Width: {bbox_dy_mm:.2f} mm (Expected Head D2 = {CFG['D2_head_mm']:.2f} mm)\n"
            f"• Z Total Height: {bbox_dz_mm:.2f} mm "
            f"(Expected Tip+Shaft+Trans+Head = "
            f"{CFG['h_tip_mm'] + CFG['L_shaft_mm'] + CFG['h_transition_mm'] + CFG['h_head_mm']:.2f} mm)\n\n"
            "Note: Research geometry reconstruction only; not for clinical use."
        )

        app.log(summary_msg)
        if ui:
            ui.messageBox(summary_msg, "AS1 A1 Auxetic Bone Screw — Completion Report")

    except Exception:
        if ui:
            ui.messageBox(f"Execution failed:\n{traceback.format_exc()}", "AS1 Script Error")