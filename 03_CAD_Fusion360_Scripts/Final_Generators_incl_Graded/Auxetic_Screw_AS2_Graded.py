# -*- coding: utf-8 -*-
"""
Auxetic_Screw_AS2.py
AS2 with optional axial strut-thickness grading (graded-transition study).
Set GRADE_ON=False for the uniform control, True for the graded screw.
Reference: Yao et al., Materials & Design 188 (2020) 108424.

Run in Fusion 360:
  Utilities > Scripts and Add-Ins > Scripts > Create/Edit > Paste & Run.
"""

import os
import adsk.core
import adsk.fusion
import traceback
import math

# =====================================================================================
# CONFIGURATION & PARAMETERS (mm, degrees)
# =====================================================================================
GRADE_ON = True        # True: graded strut thickness; False: uniform control
T_CORE = 0.472         # strut thickness in the active core (mm), Case B value for AS2
T_DENSE = 0.65         # strut thickness at the head end of the lattice (mm)
RAMP_LENGTH = 6.0      # length of the ramp measured from the head end (mm)
SCREW_TYPE = 'AS2G' if GRADE_ON else 'AS2U'

CFG = {
    # --- Paper Specifications (Yao et al. 2020) ---
    'major_diameter': 5.7,          # D1: Major / crest diameter (mm)
    'shaft_length': 21.0,           # L: Active porous shaft length (mm)
    'thread_pitch': 1.75,           # P: Thread pitch (mm)
    'thread_depth': 0.75,           # d: Thread height (mm)
    'thread_parameter_e': 0.1,      # e: Crest flat width (mm)
    'thread_angle_alpha': 35.0,     # alpha: Leading flank angle (deg)
    'thread_angle_beta': 87.0,      # beta: Trailing flank angle (deg)
    'thread_radius_r1': 1.0,        # r1: Leading root fillet (mm)
    'thread_radius_r2': 0.3,        # r2: Trailing root fillet (mm)
    'cell_width': 3.0,              # Planar unit cell width (mm)
    'cell_height': 3.0,             # Planar unit cell height (mm)

    # --- Wall & Strut Sizing ---
    'lattice_wall_thickness': 1.2,  # t: Radial wall (0.8 tubular, 1.2 printed screw, 1.6 FEA)
    'cell_strut_thickness': 0.50,   # In-plane strut thickness (mm)
    'circumferential_cell_count': 6,# 6 cells around cylinder (6 * 3 mm ~ pi * 5.7 mm)
    'axial_cell_count': 7,          # 7 cell rows (7 * 3 mm = 21 mm)

    # --- Solid Head & Tip Ends ---
    'head_diameter': 8.0,           # D2 head diameter (mm)
    'head_height': 3.0,             # h head height (mm)
    'tip_height': 3.5,              # Pointed self-tapping cone tip height (mm)
    'transition_height': 1.0,       # Conical neck transition (mm)
    'end_collar_height': 0.5,       # Solid collar bridging lattice to solid ends (mm)
}

CREATE_THREAD = True
ALLOW_ANNULAR_THREAD_FALLBACK = True
JOIN_END_SOLIDS = True
JOINT_EXTENSION_FACTOR = 0.25
END_RADIUS_UNDERCUT = 0.03


# =====================================================================================
# GEOMETRIC VECTOR HELPERS (Units in mm, Fusion internal in cm)
# =====================================================================================
def mm(v):
    return v / 10.0

def pt(x, y, z=0.0):
    return adsk.core.Point3D.create(mm(x), mm(y), mm(z))

def vec(v):
    return adsk.core.Vector3D.create(v[0], v[1], v[2])

def vi(expr):
    return adsk.core.ValueInput.createByString(expr)

def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def v_mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)

def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def v_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def v_len(a):
    return math.sqrt(v_dot(a, a))

def v_unit(a):
    n = v_len(a)
    return (a[0] / n, a[1] / n, a[2] / n) if n > 1e-9 else (0.0, 1.0, 0.0)

def pos(R, phi, y):
    """Cylindrical coordinate mapping: phi about +Y axis, height y."""
    return (R * math.cos(phi), y, -R * math.sin(phi))


def derive_geometry():
    c = CFG
    G = {}
    G['Ro'] = c['major_diameter'] / 2.0
    G['wall'] = c['lattice_wall_thickness']
    G['Ri'] = G['Ro'] - G['wall']
    G['n'] = int(round(c['circumferential_cell_count']))
    G['N'] = int(round(c['axial_cell_count']))
    G['L'] = c['shaft_length']
    G['H'] = G['L'] / float(G['N'])
    G['dphi'] = 2.0 * math.pi / G['n']
    G['t'] = c['cell_strut_thickness']
    G['Rmap'] = 0.5 * (G['Ri'] + G['Ro'])
    G['Re'] = G['Ro'] - END_RADIUS_UNDERCUT
    G['Rh'] = c['head_diameter'] / 2.0
    G['collar'] = c['end_collar_height']
    G['emb'] = min(0.25, 0.5 * G['collar'])
    G['Y_lo'] = c['tip_height'] + G['collar']
    G['Y_hi'] = G['Y_lo'] + G['L']
    G['R_root'] = G['Ro'] - c['thread_depth']
    return G


# =====================================================================================
# TEMPORARY B-REP SOLID STRUT GENERATION
# =====================================================================================
def strut_t(G, y):
    """Strut thickness at axial position y (mm); linear ramp T_CORE -> T_DENSE over RAMP_LENGTH at the head end."""
    if not GRADE_ON:
        return T_CORE
    s = (y - (G['Y_hi'] - RAMP_LENGTH)) / RAMP_LENGTH
    s = min(max(s, 0.0), 1.0)
    return T_CORE + s * (T_DENSE - T_CORE)


def make_strut_box(tbm, G, P, Q, phi_mid, half_span):
    """Generates an oriented solid B-Rep box along P->Q spanning through the shell wall."""
    t = strut_t(G, 0.5 * (P[1] + Q[1]))
    ext = JOINT_EXTENSION_FACTOR * t
    d = v_sub(Q, P)
    Lc = v_len(d)
    if Lc < 1e-6:
        return None
    dh = v_unit(d)
    rh = (math.cos(phi_mid), 0.0, -math.sin(phi_mid))
    w = v_cross(dh, rh)
    if v_len(w) < 1e-9:
        w = v_cross(dh, (0.0, 0.0, 1.0))
    wh = v_unit(w)

    s_max = G['Rmap'] * math.sin(half_span) + t / 2.0 + ext
    rho_out = G['Ro'] + 0.10
    rho_in = max(math.sqrt(max(G['Ri']**2 - s_max**2, 0.0)) - 0.10, 0.05)
    height = rho_out - rho_in
    rho_mid = 0.5 * (rho_out + rho_in)

    M = v_mul(v_add(P, Q), 0.5)
    rho_c = v_dot(M, rh)
    center = v_add(M, v_mul(rh, rho_mid - rho_c))

    obb = adsk.core.OrientedBoundingBox3D.create(
        pt(*center), vec(dh), vec(wh),
        mm(Lc + 2.0 * ext), mm(t), mm(height)
    )
    return tbm.createBox(obb)


def union_into(tbm, acc, tool):
    if tool is None:
        return acc
    if acc is None:
        return tool
    tbm.booleanOperation(acc, tool, adsk.fusion.BooleanTypes.UnionBooleanType)
    return acc


def build_lattice_temp(G):
    """
    Constructs the un-trimmed AS2 strut mesh in Python memory, then trims it to
    the exact cylindrical tube Ri..Ro.
    """
    tbm = adsk.fusion.TemporaryBRepManager.get()
    n, N, H, dphi = G['n'], G['N'], G['H'], G['dphi']
    Rm = G['Rmap']
    y_a = G['Y_lo'] - G['emb']
    y_b = G['Y_hi'] + G['emb']

    acc = None

    for i in range(n):
        phi_w = i * dphi
        phi_s = phi_w + dphi / 2.0
        phi_w_next = phi_w + dphi

        # AS2 - RE-ENTRANT HONEYCOMB / BOWTIE
        # Continuous vertical side columns (provides the paper's highest stiffness)
        for k in range(N):
            ya_k = y_a if k == 0 else G['Y_lo'] + k * H
            yb_k = y_b if k == N - 1 else G['Y_lo'] + (k + 1) * H
            acc = union_into(tbm, acc, make_strut_box(tbm, G, pos(Rm, phi_w, ya_k), pos(Rm, phi_w, yb_k), phi_w, 0.0))

        delta_y = 0.35 * H
        for k in range(N):
            y_base = G['Y_lo'] + k * H
            y_top = y_base + H
            y_top_nook = y_top - delta_y
            y_bot_nook = y_base + delta_y

            # Central vertical stem rib connecting the re-entrant apexes
            acc = union_into(tbm, acc, make_strut_box(tbm, G, pos(Rm, phi_s, y_bot_nook - 0.1*H), pos(Rm, phi_s, y_top_nook + 0.1*H), phi_s, 0.0))

            # Top re-entrant arms (angled downward into the center)
            acc = union_into(tbm, acc, make_strut_box(tbm, G, pos(Rm, phi_w, y_top), pos(Rm, phi_s, y_top_nook), phi_w + dphi/4.0, dphi/4.0))
            acc = union_into(tbm, acc, make_strut_box(tbm, G, pos(Rm, phi_w_next, y_top), pos(Rm, phi_s, y_top_nook), phi_w + 3.0*dphi/4.0, dphi/4.0))

            # Bottom re-entrant arms (angled upward into the center)
            acc = union_into(tbm, acc, make_strut_box(tbm, G, pos(Rm, phi_w, y_base), pos(Rm, phi_s, y_bot_nook), phi_w + dphi/4.0, dphi/4.0))
            acc = union_into(tbm, acc, make_strut_box(tbm, G, pos(Rm, phi_w_next, y_base), pos(Rm, phi_s, y_bot_nook), phi_w + 3.0*dphi/4.0, dphi/4.0))

    # --- Trim the entire lattice body to the cylindrical tube Ri..Ro ---
    y_lo_c, y_hi_c = y_a - 0.5, y_b + 0.5
    cyl_o = tbm.createCylinderOrCone(pt(0, y_lo_c, 0), mm(G['Ro']), pt(0, y_hi_c, 0), mm(G['Ro']))
    cyl_i = tbm.createCylinderOrCone(pt(0, y_lo_c - 1, 0), mm(G['Ri']), pt(0, y_hi_c + 1, 0), mm(G['Ri']))
    tbm.booleanOperation(cyl_o, cyl_i, adsk.fusion.BooleanTypes.DifferenceBooleanType)
    tbm.booleanOperation(acc, cyl_o, adsk.fusion.BooleanTypes.IntersectionBooleanType)

    return acc


def add_temp_body(comp, tmp, name, feat_name):
    bf = comp.features.baseFeatures.add()
    bf.name = feat_name
    bf.startEdit()
    try:
        body = comp.bRepBodies.add(tmp, bf)
    finally:
        bf.finishEdit()
    body.name = name
    return body


# =====================================================================================
# THREAD CUTTING (Buttress Thread with Helical Sweep & Annular Fallback)
# =====================================================================================
def thread_numbers(G):
    c = CFG
    P, d, e = c['thread_pitch'], c['thread_depth'], c['thread_parameter_e']
    t_lead = math.tan(math.radians(c['thread_angle_alpha']))
    t_trail = math.tan(math.radians(90.0 - c['thread_angle_beta']))
    W_top = P - e
    ext = 0.05
    return {
        't_lead': t_lead, 't_trail': t_trail,
        'z_a': d * t_trail, 'z_b': W_top - d * t_lead,
        'z_lt': -ext * t_trail, 'z_rt': W_top + ext * t_lead,
        'R_top': G['Ro'] + ext,
    }


def draw_groove_polygon(sk, G, T, y_mid):
    y0 = y_mid - 0.5 * (T['z_a'] + T['z_b'])
    Rr, Rt = G['R_root'], T['R_top']
    pts = [(Rr, y0 + T['z_a']), (Rr, y0 + T['z_b']), (Rt, y0 + T['z_rt']), (Rt, y0 + T['z_lt'])]
    lines = sk.sketchCurves.sketchLines
    for i in range(len(pts)):
        p1 = pt(pts[i][0], pts[i][1])
        p2 = pt(pts[(i + 1) % len(pts)][0], pts[(i + 1) % len(pts)][1])
        lines.addByTwoPoints(p1, p2)


def cut_thread(comp, G, lattice_body):
    c = CFG
    T = thread_numbers(G)
    P = c['thread_pitch']
    y_s = G['Y_lo'] - P
    turns = (G['Y_hi'] - G['Y_lo']) / P + 2.0
    tbm = adsk.fusion.TemporaryBRepManager.get()

    helical_ok = False
    try:
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Thread_Groove_Profile'
        draw_groove_polygon(sk, G, T, y_s)

        wire = tbm.createHelixWire(pt(0, y_s, 0), vec((0, 1, 0)), pt(G['R_root'], y_s, 0), mm(P), turns, 0.0)
        if isinstance(wire, tuple):
            wire = wire[0]
        wbody = add_temp_body(comp, wire, 'Thread_Helix_Wire', 'Thread_Helix_BaseFeature')
        path = comp.features.createPath(wbody.edges.item(0))

        sweeps = comp.features.sweepFeatures
        sin = sweeps.createInput(sk.profiles.item(0), path, adsk.fusion.FeatureOperations.CutFeatureOperation)
        sin.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
        sweeps.add(sin)
        wbody.isVisible = False
        helical_ok = True
    except Exception:
        pass

    # Robust fallback: annular grooves (revolved) if sweep-cut experiences kernel tolerances
    if not helical_ok and ALLOW_ANNULAR_THREAD_FALLBACK:
        sk_annular = comp.sketches.add(comp.xYConstructionPlane)
        sk_annular.name = 'Thread_Annular_Grooves'
        sk_annular.isComputeDeferred = True
        count = int(math.ceil((G['Y_hi'] - G['Y_lo']) / P)) + 2
        for i in range(count):
            draw_groove_polygon(sk_annular, G, T, y_s + i * P)
        sk_annular.isComputeDeferred = False

        profs = adsk.core.ObjectCollection.create()
        for i in range(sk_annular.profiles.count):
            profs.add(sk_annular.profiles.item(i))

        revs = comp.features.revolveFeatures
        rin = revs.createInput(profs, comp.yConstructionAxis, adsk.fusion.FeatureOperations.CutFeatureOperation)
        rin.setAngleExtent(False, vi('360 deg'))
        revs.add(rin)


# =====================================================================================
# SOLID HEAD & POINTED TIP (ASTM F543 Standard)
# =====================================================================================
def build_end_solids(comp, G):
    c = CFG
    Re, Rh = G['Re'], G['Rh']
    tip_h, collar = c['tip_height'], G['collar']
    revs = comp.features.revolveFeatures
    op = adsk.fusion.FeatureOperations.NewBodyFeatureOperation

    # --- Tip Revolve ---
    sk_tip = comp.sketches.add(comp.xYConstructionPlane)
    sk_tip.name = 'Tip_Profile'
    pts_tip = [(0, 0), (Re, tip_h), (Re, tip_h + collar), (0, tip_h + collar)]
    for i in range(len(pts_tip)):
        p1 = pt(pts_tip[i][0], pts_tip[i][1])
        p2 = pt(pts_tip[(i + 1) % len(pts_tip)][0], pts_tip[(i + 1) % len(pts_tip)][1])
        sk_tip.sketchCurves.sketchLines.addByTwoPoints(p1, p2)

    rin = revs.createInput(sk_tip.profiles.item(0), comp.yConstructionAxis, op)
    rin.setAngleExtent(False, vi('360 deg'))
    tip_body = revs.add(rin).bodies.item(0)

    # --- Head & Transition Revolve ---
    y_c0 = G['Y_hi']
    y1 = y_c0 + collar
    y2 = y1 + c['transition_height']
    y3 = y2 + c['head_height']
    sk_head = comp.sketches.add(comp.xYConstructionPlane)
    sk_head.name = 'Head_Profile'
    pts_head = [(0, y_c0), (Re, y_c0), (Re, y1), (Rh, y2), (Rh, y3), (0, y3)]
    for i in range(len(pts_head)):
        p1 = pt(pts_head[i][0], pts_head[i][1])
        p2 = pt(pts_head[(i + 1) % len(pts_head)][0], pts_head[(i + 1) % len(pts_head)][1])
        sk_head.sketchCurves.sketchLines.addByTwoPoints(p1, p2)

    hin = revs.createInput(sk_head.profiles.item(0), comp.yConstructionAxis, op)
    hin.setAngleExtent(False, vi('360 deg'))
    head_body = revs.add(hin).bodies.item(0)

    return tip_body, head_body


def join_bodies(comp, target, tools):
    cf = comp.features.combineFeatures
    coll = adsk.core.ObjectCollection.create()
    for b in tools:
        coll.add(b)
    inp = cf.createInput(target, coll)
    inp.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    inp.isKeepToolBodies = False
    return cf.add(inp)


# =====================================================================================
# SCREW BUILD CONTROLLER
# =====================================================================================
def build_screw(root_comp, G):
    # 1. Dedicated Occurrence
    trans = adsk.core.Matrix3D.create()
    occ = root_comp.occurrences.addNewComponent(trans)
    comp = occ.component
    comp.name = "AS2_Auxetic_Bone_Screw"

    # 2. Lattice Shell Generation
    acc = build_lattice_temp(G)
    lattice_body = add_temp_body(comp, acc, "AS2_Lattice_Shell", "AS2_Lattice_BaseFeature")

    # 3. Thread Cutting
    if CREATE_THREAD:
        cut_thread(comp, G, lattice_body)

    # 4. Pointed Tip & Solid Head
    tip_body, head_body = build_end_solids(comp, G)

    # 5. Combine into One Unified Solid Body
    if JOIN_END_SOLIDS:
        try:
            join_bodies(comp, lattice_body, [tip_body, head_body])
            lattice_body.name = "AS2_Screw_Body"
        except Exception:
            pass

    return comp


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            return

        design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        root_comp = design.rootComponent
        G = derive_geometry()

        build_screw(root_comp, G)

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        export_msg = ""
        try:
            export_mgr = design.exportManager
            export_dir = os.path.dirname(os.path.abspath(__file__))
            step_path = os.path.join(export_dir, f"{SCREW_TYPE}_screw.step")
            stl_path = os.path.join(export_dir, f"{SCREW_TYPE}_screw.stl")

            step_options = export_mgr.createSTEPExportOptions(step_path)
            export_mgr.execute(step_options)

            stl_options = export_mgr.createSTLExportOptions(root_comp, stl_path)
            stl_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            export_mgr.execute(stl_options)
            export_msg = f"\n\nFiles exported for FEA:\n• {step_path}\n• {stl_path}"
        except Exception as e_exp:
            export_msg = f"\n\n(Auto-export notice: {e_exp})"

        ui.messageBox(
            "AS2 (Re-entrant Bowtie Honeycomb) screw generated successfully!\n\n"
            f"• Shaft Length: {CFG['shaft_length']} mm\n"
            f"• Major Diameter: {CFG['major_diameter']} mm\n"
            f"• Wall Thickness: {CFG['lattice_wall_thickness']} mm\n"
            f"• Pitch / Thread Depth: {CFG['thread_pitch']} mm / {CFG['thread_depth']} mm"
            f"{export_msg}",
            "Bone Screw Modeling"
        )

    except Exception:
        if ui:
            ui.messageBox(f"Execution Failed:\n{traceback.format_exc()}")
