# -*- coding: utf-8 -*-
"""
AS1_A1_AuxeticBoneScrew.py
Geometry RECONSTRUCTION of an A1 re-entrant auxetic bone screw (AS1), inspired by
Fig. 1 of  Yao et al. (2020), Materials & Design 188, 108424.

This is NOT the authors' CAD model and is NOT an exact reproduction. The A1 vertex layout
below is read from the low-resolution Fig. 1(b) glyph; every assumption is listed here.

Run in Fusion: Utilities > Scripts and Add-Ins > Scripts > "+" > Run.
Axis of the screw = +Y. Units: millimetres in this file; Fusion API = centimetres (mm()).

------------------------------------------------------------------------------------
VALUES TAKEN FROM THE PAPER (Fig. 1 caption / text)
  D1 = 5.7 mm, L = 21 mm, P = 1.75 mm, d = 0.75 mm, e = 0.1 mm,
  alpha = 35 deg, beta = 87 deg, r1 = 1 mm, r2 = 0.3 mm,
  planar unit cell 3 mm x 3 mm, porosity 0.53, pore sizes 358-1260 um (literature range),
  wall thickness t: 0.8 mm (tubular structures, Fig.1 caption / fabricated tubes),
                    1.2 mm (fabricated screws), 1.6 mm (FEA screws / FEA tubes also 0.8, 1.2).
PROVISIONAL MODELLING ASSUMPTIONS (NOT reported by Yao et al.)
  head_diameter 8.0, head_height 3.0, tip_height 3.5, transition_height 1.0,
  end_collar_height 0.5, cell_strut_thickness 0.5 (Fig. 5 suggests ~0.5 mm design strut for
  A1, read approximately from a bar chart), A1 vertex layout, thread-angle interpretation,
  the choice of 6 circumferential cells, and all strut-joint details.

A1 CELL ASSUMPTION (unrolled cell, u = circumferential, v = axial, cell = W x H = 3 x 3 mm)
  * "wall" struts  : vertical lines at u = 0 (shared with the neighbouring cell)
  * "stem" strut   : vertical line at u = W/2 (central rib)
  * two "arm" struts: from the wall nodes (0, H) and (W, H) down-inwards to the stem node
                      (W/2, a1_apex_ratio*H)  -> an "M"/chevron on top of a stem, with
                      inward pointing V regions.  Apex ratio 0.5 gives 45 deg in the plane.
  Rows repeat along the screw axis, cells repeat around the circumference
  (6 cells x 3 mm ~ pi*5.7 mm, so the cell width closes the circumference almost exactly).

THREAD INTERPRETATION (assumption)
  Fig. 1(a) shows a sharp-crested thread. Here the tube outer diameter is D1 and a helical
  GROOVE is cut into the lattice (the paper says threads were cut into the structure).
  alpha = angle of the leading flank from the radial direction, beta is measured from the
  screw axis so the trailing flank is (90 - beta) deg from the radial direction,
  e = crest flat width, r1 / r2 = root fillets at the leading / trailing flank,
  d = thread depth (crest radius - root radius).

HOW THE MODEL IS BUILT / EDITABILITY (read this)
  * All user parameters are created in the Fusion parameter table.
  * The A1 strut network is generated numerically in Python as temporary BRep solids (oriented
    boxes), unioned and trimmed to the cylindrical shell in memory, then inserted as ONE BASE
    FEATURE. It is real solid BRep geometry but NOT driven by timeline sketches: to change
    the lattice, edit CFG and re-run. This avoids hundreds of fragile Boolean features.
  * Head, tip, thread-groove sketch/sweep and the final joins ARE timeline features; a few of
    their dimensions are linked to user parameters, but changing parameters afterwards does
    not regenerate the lattice.
------------------------------------------------------------------------------------
"""

import adsk.core
import adsk.fusion
import traceback
import math

# =====================================================================================
# CONFIGURATION  (mm, degrees)
# =====================================================================================
CFG = {
    # --- from the paper ---
    'major_diameter': 5.7,          # D1
    'shaft_length': 21.0,           # L  (interpreted as the lattice node-to-node length, see notes)
    'thread_pitch': 1.75,           # P
    'thread_depth': 0.75,           # d
    'thread_parameter_e': 0.1,      # e  (crest flat)
    'thread_angle_alpha': 35.0,     # alpha
    'thread_angle_beta': 87.0,      # beta
    'thread_radius_r1': 1.0,        # r1
    'thread_radius_r2': 0.3,        # r2
    'cell_width': 3.0,
    'cell_height': 3.0,
    'target_porosity': 0.53,
    # --- provisional ---
    'head_diameter': 8.0,           # D2  PROVISIONAL
    'head_height': 3.0,             # h   PROVISIONAL
    'tip_height': 3.5,              #     PROVISIONAL
    'transition_height': 1.0,       #     PROVISIONAL (head-to-shaft cone)
    'end_collar_height': 0.5,       #     PROVISIONAL (solid collars at both ends of the lattice)
    'cell_strut_thickness': 0.5,    # in-plane strut width  PROVISIONAL (initial value)
    'lattice_wall_thickness': 1.2,  # radial tube wall t: 0.8 tubular / 1.2 fabricated screw / 1.6 FEA screw
    'circumferential_cell_count': 6,
    'axial_cell_count': 7,
    'a1_apex_ratio': 0.5,           # stem/arm node height inside the cell (0..1), 0.5 -> 45 deg planar arms
}

CREATE_THREAD = True               # helical groove (falls back to annular grooves with a warning)
ALLOW_ANNULAR_THREAD_FALLBACK = True
AUTO_TUNE_STRUT_TO_TARGET_POROSITY = False   # True: choose strut thickness to hit target planar porosity
JOIN_END_SOLIDS = True             # Boolean-join head/tip with the lattice body
JOINT_EXTENSION_FACTOR = 0.25      # strut ends are extended by factor*thickness to fill joint notches
END_RADIUS_UNDERCUT = 0.03         # mm; end collars are slightly smaller than D1 to avoid coincident faces

# =====================================================================================
# REPORT + SMALL HELPERS
# =====================================================================================


class Report(object):
    def __init__(self):
        self.created, self.failed, self.warnings, self.notes = [], [], [], []

    def ok(self, m):
        self.created.append(m)

    def fail(self, m):
        self.failed.append(m)

    def warn(self, m):
        self.warnings.append(m)

    def note(self, m):
        self.notes.append(m)


REP = Report()
BODY_NAME = 'AS1_A1_Auxetic_Bone_Screw_Body'
COMP_NAME = 'AS1_A1_Auxetic_Bone_Screw'


def mm(v):
    return v / 10.0


def pt(x, y, z=0.0):
    return adsk.core.Point3D.create(mm(x), mm(y), mm(z))


def vec(v):
    return adsk.core.Vector3D.create(v[0], v[1], v[2])


def vi(expr):
    return adsk.core.ValueInput.createByString(expr)


def fmt(v):
    return '{:.6g}'.format(v)


def stage(label, fn):
    try:
        return fn()
    except Exception:
        tb = traceback.format_exc().strip().splitlines()
        REP.fail('{} -> {}'.format(label, ' | '.join(tb[-2:])))
        return None


# --- tiny tuple vector maths (mm) ---
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
    return (a[0] / n, a[1] / n, a[2] / n)


def pos(R, phi, y):
    """Point on the cylinder of radius R, angle phi (rad, right-handed about +Y), height y."""
    return (R * math.cos(phi), y, -R * math.sin(phi))


# =====================================================================================
# DERIVED GEOMETRY + VALIDATION
# =====================================================================================
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
    G['vy'] = c['a1_apex_ratio']
    G['Rmap'] = 0.5 * (G['Ri'] + G['Ro'])
    G['Re'] = G['Ro'] - END_RADIUS_UNDERCUT
    G['Rh'] = c['head_diameter'] / 2.0
    G['collar'] = c['end_collar_height']
    G['emb'] = min(0.25, 0.5 * G['collar'])
    G['Y_lo'] = c['tip_height'] + G['collar']
    G['Y_hi'] = G['Y_lo'] + G['L']
    G['y_top'] = G['Y_hi'] + G['collar'] + c['transition_height'] + c['head_height']
    G['R_root'] = G['Ro'] - c['thread_depth']

    if G['n'] < 3 or G['N'] < 1:
        raise ValueError('circumferential_cell_count must be >= 3 and axial_cell_count >= 1.')
    if G['Ri'] < 0.6:
        raise ValueError('lattice_wall_thickness leaves an inner radius < 0.6 mm.')
    if c['head_diameter'] <= c['major_diameter']:
        raise ValueError('head_diameter must exceed major_diameter.')
    if not (0.15 <= G['vy'] <= 0.85):
        raise ValueError('a1_apex_ratio must be within 0.15..0.85.')
    if G['collar'] < 0.2:
        raise ValueError('end_collar_height must be >= 0.2 mm.')
    if abs(G['L'] - c['cell_height'] * G['N']) > 1e-6:
        REP.warn('shaft_length ({}) != axial_cell_count*cell_height ({}); the effective axial cell height is {:.4f} mm.'.format(
            fmt(G['L']), fmt(c['cell_height'] * G['N']), G['H']))
    arc = 2.0 * math.pi * G['Ro'] / G['n']
    G['arc_w'] = arc
    if abs(arc - c['cell_width']) / c['cell_width'] > 0.10:
        REP.warn('Circumferential cell width at the outer surface is {:.3f} mm vs cell_width {:.3f} mm '
                 '(>10% apart). Change circumferential_cell_count.'.format(arc, c['cell_width']))
    if G['wall'] - c['thread_depth'] < 0.2:
        REP.warn('Thread depth {} leaves only {:.2f} mm of lattice wall under the thread root; '
                 'the groove may cut through the wall.'.format(fmt(c['thread_depth']), G['wall'] - c['thread_depth']))
    if G['t'] >= 0.8 * min(arc / 2.0, G['H'] / 2.0):
        REP.warn('Strut thickness is large relative to the cell; pores may close.')
    return G


# =====================================================================================
# POROSITY ESTIMATE (idealised unrolled planar cell, pure Python)
# =====================================================================================
def planar_solid_fraction(W, H, t, vy, grid=100):
    segs = []
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            x0, y0 = i * W, j * H
            segs.append(((x0, y0), (x0, y0 + H)))
            segs.append(((x0 + W / 2.0, y0), (x0 + W / 2.0, y0 + H)))
            segs.append(((x0, y0 + H), (x0 + W / 2.0, y0 + vy * H)))
            segs.append(((x0 + W, y0 + H), (x0 + W / 2.0, y0 + vy * H)))
    pre = []
    for (p, q) in segs:
        dx, dy = q[0] - p[0], q[1] - p[1]
        ln = math.hypot(dx, dy)
        pre.append((p[0], p[1], dx / ln, dy / ln, ln))
    hit = 0
    for ix in range(grid):
        x = (ix + 0.5) * W / grid
        for iy in range(grid):
            y = (iy + 0.5) * H / grid
            for (px, py, ux, uy, ln) in pre:
                s = (x - px) * ux + (y - py) * uy
                if -0.0 <= s <= ln:
                    d = abs(-(x - px) * uy + (y - py) * ux)
                    if d <= t / 2.0:
                        hit += 1
                        break
    return hit / float(grid * grid)


def tune_strut_thickness(W, H, vy, target_porosity):
    lo, hi = 0.1, 0.9
    for _ in range(14):
        mid = 0.5 * (lo + hi)
        por = 1.0 - planar_solid_fraction(W, H, mid, vy, grid=60)
        if por > target_porosity:
            lo = mid
        else:
            hi = mid
    return round(0.5 * (lo + hi), 3)


# =====================================================================================
# USER PARAMETERS
# =====================================================================================
def upsert_param(design, name, expr, unit, comment):
    up = design.userParameters
    existing = up.itemByName(name)
    if existing:
        existing.expression = expr
        return existing
    return up.add(name, adsk.core.ValueInput.createByString(expr), unit, comment)


def create_user_parameters(design):
    c = CFG
    mmv = lambda k: fmt(c[k]) + ' mm'
    specs = [
        # screw dimensions
        ('major_diameter', mmv('major_diameter'), 'mm', 'D1 major (thread crest) diameter - Yao et al. Fig.1'),
        ('shaft_length', mmv('shaft_length'), 'mm', 'L lattice node-to-node length - Yao et al. Fig.1 (interpretation, see script notes)'),
        ('head_diameter', mmv('head_diameter'), 'mm', 'D2 head diameter - PROVISIONAL modelling assumption'),
        ('head_height', mmv('head_height'), 'mm', 'h head height - PROVISIONAL modelling assumption'),
        ('tip_height', mmv('tip_height'), 'mm', 'Pointed tip height - PROVISIONAL modelling assumption'),
        ('transition_height', mmv('transition_height'), 'mm', 'Head-to-shaft cone height - PROVISIONAL'),
        ('end_collar_height', mmv('end_collar_height'), 'mm', 'Solid collar at each end of the lattice - PROVISIONAL'),
        # thread (paper)
        ('thread_pitch', mmv('thread_pitch'), 'mm', 'P thread pitch - Yao et al. Fig.1'),
        ('thread_depth', mmv('thread_depth'), 'mm', 'd thread depth - Yao et al. Fig.1'),
        ('thread_parameter_e', mmv('thread_parameter_e'), 'mm', 'e thread parameter (modelled as crest flat) - Yao et al. Fig.1'),
        ('thread_angle_alpha', fmt(c['thread_angle_alpha']) + ' deg', 'deg', 'alpha (modelled: leading flank angle from radial) - Yao et al. Fig.1'),
        ('thread_angle_beta', fmt(c['thread_angle_beta']) + ' deg', 'deg', 'beta (modelled: trailing flank measured from axis) - Yao et al. Fig.1'),
        ('thread_radius_r1', mmv('thread_radius_r1'), 'mm', 'r1 root fillet, leading flank - Yao et al. Fig.1'),
        ('thread_radius_r2', mmv('thread_radius_r2'), 'mm', 'r2 root fillet, trailing flank - Yao et al. Fig.1'),
        ('thread_root_diameter', 'major_diameter - 2 * thread_depth', 'mm', 'Derived thread root diameter'),
        # lattice
        ('cell_width', mmv('cell_width'), 'mm', 'Planar unit-cell width 3 mm - Yao et al. Sect. 2.1'),
        ('cell_height', mmv('cell_height'), 'mm', 'Planar unit-cell height 3 mm - Yao et al. Sect. 2.1'),
        ('cell_strut_thickness', mmv('cell_strut_thickness'), 'mm',
         'In-plane STRUT thickness (not the wall thickness) - PROVISIONAL initial value'),
        ('lattice_wall_thickness', mmv('lattice_wall_thickness'), 'mm',
         'Radial tube WALL thickness t: paper uses 0.8 (tubular), 1.2 (fabricated screws), 1.6 (FEA screws)'),
        ('lattice_outer_diameter', 'major_diameter', 'mm', 'Lattice tube outer diameter (= D1)'),
        ('lattice_inner_diameter', 'major_diameter - 2 * lattice_wall_thickness', 'mm', 'Derived inner (bore) diameter'),
        ('target_porosity', fmt(c['target_porosity']), '', 'Target nominal porosity 0.53 - Yao et al. Sect. 2.1 (target, NOT achieved value)'),
        ('circumferential_cell_count', fmt(c['circumferential_cell_count']), '', 'Cells around the circumference (assumption: 6)'),
        ('axial_cell_count', fmt(c['axial_cell_count']), '', 'Cell rows along the screw axis'),
        ('a1_apex_ratio', fmt(c['a1_apex_ratio']), '', 'A1 stem/arm node height ratio inside the cell - ASSUMPTION'),
    ]
    for name, expr, unit, comment in specs:
        upsert_param(design, name, expr, unit, comment)
    REP.ok('User parameters created ({}): {}'.format(len(specs), ', '.join(s[0] for s in specs)))


# =====================================================================================
# SKETCH HELPERS
# =====================================================================================
HORIZ = adsk.fusion.DimensionOrientations.HorizontalDimensionOrientation
VERT = adsk.fusion.DimensionOrientations.VerticalDimensionOrientation


def draw_polygon(sk, pts_mm):
    lines = sk.sketchCurves.sketchLines
    n = len(pts_mm)
    out = [lines.addByTwoPoints(pt(*pts_mm[0]), pt(*pts_mm[1]))]
    prev = out[0]
    for i in range(2, n):
        ln = lines.addByTwoPoints(prev.endSketchPoint, pt(*pts_mm[i]))
        out.append(ln)
        prev = ln
    out.append(lines.addByTwoPoints(prev.endSketchPoint, out[0].startSketchPoint))
    return out


def safe_constraint(fn, label):
    try:
        fn()
        return True
    except Exception:
        REP.note('Sketch constraint skipped ({}).'.format(label))
        return False


def link_dim(sk, p1, p2, orientation, expr, label):
    try:
        g1, g2 = p1.geometry, p2.geometry
        text = adsk.core.Point3D.create((g1.x + g2.x) / 2.0 + 0.4, (g1.y + g2.y) / 2.0 + 0.4, 0)
        dim = sk.sketchDimensions.addDistanceDimension(p1, p2, orientation, text)
        dim.parameter.expression = expr
        return True
    except Exception:
        REP.note('Dimension "{}" not linked to a parameter ({}); numeric value used.'.format(label, expr))
        return False


def find_body(comp, name):
    for i in range(comp.bRepBodies.count):
        b = comp.bRepBodies.item(i)
        if b.name == name:
            return b
    return None


# =====================================================================================
# A1 LATTICE (temporary BRep -> one base feature)
# =====================================================================================
def make_strut_box(tbm, G, P, Q, phi_mid, half_span):
    """Oriented box along P->Q, radial depth covering the shell with overshoot (trimmed later)."""
    t = G['t']
    ext = JOINT_EXTENSION_FACTOR * t
    d = v_sub(Q, P)
    Lc = v_len(d)
    dh = v_unit(d)
    rh = (math.cos(phi_mid), 0.0, -math.sin(phi_mid))
    w = v_cross(dh, rh)
    if v_len(w) < 1e-9:
        raise ValueError('Degenerate strut orientation.')
    wh = v_unit(w)
    s_max = G['Rmap'] * math.sin(half_span) + t / 2.0 + ext
    rho_out = G['Ro'] + 0.05
    rho_in = max(math.sqrt(max(G['Ri'] ** 2 - s_max ** 2, 0.0)) - 0.05, 0.05)
    height = rho_out - rho_in
    rho_mid = 0.5 * (rho_out + rho_in)
    M = v_mul(v_add(P, Q), 0.5)
    rho_c = v_dot(M, rh)
    center = v_add(M, v_mul(rh, rho_mid - rho_c))
    obb = adsk.core.OrientedBoundingBox3D.create(pt(*center), vec(dh), vec(wh),
                                                 mm(Lc + 2.0 * ext), mm(t), mm(height))
    return tbm.createBox(obb)


def union_into(tbm, acc, tool, failed):
    if acc is None:
        return tool
    ok = tbm.booleanOperation(acc, tool, adsk.fusion.BooleanTypes.UnionBooleanType)
    if not ok:
        failed.append(tool)
    return acc


def build_lattice_temp(G):
    """Returns (temp_body_or_list, stats)."""
    tbm = adsk.fusion.TemporaryBRepManager.get()
    n, N, H, dphi = G['n'], G['N'], G['H'], G['dphi']
    Rm = G['Rmap']
    y_a, y_b = G['Y_lo'] - G['emb'], G['Y_hi'] + G['emb']
    failed = []
    cols = []
    n_struts = 0
    for i in range(n):
        phi_w = i * dphi
        phi_s = phi_w + dphi / 2.0
        col = None
        # wall
        col = union_into(tbm, col, make_strut_box(tbm, G, pos(Rm, phi_w, y_a), pos(Rm, phi_w, y_b), phi_w, 0.0), failed)
        # stem
        col = union_into(tbm, col, make_strut_box(tbm, G, pos(Rm, phi_s, y_a), pos(Rm, phi_s, y_b), phi_s, 0.0), failed)
        n_struts += 2
        for k in range(N):
            y_t = G['Y_lo'] + (k + 1) * H
            y_ap = y_t - (1.0 - G['vy']) * H
            col = union_into(tbm, col, make_strut_box(
                tbm, G, pos(Rm, phi_w, y_t), pos(Rm, phi_s, y_ap), phi_w + dphi / 4.0, dphi / 4.0), failed)
            col = union_into(tbm, col, make_strut_box(
                tbm, G, pos(Rm, phi_w + dphi, y_t), pos(Rm, phi_s, y_ap), phi_w + 3.0 * dphi / 4.0, dphi / 4.0), failed)
            n_struts += 2
        cols.append(col)
    acc = None
    for col in cols:
        acc = union_into(tbm, acc, col, failed)

    # trim to the cylindrical shell Ri..Ro
    y_lo_c, y_hi_c = y_a - 0.5, y_b + 0.5
    cyl_o = tbm.createCylinderOrCone(pt(0, y_lo_c, 0), mm(G['Ro']), pt(0, y_hi_c, 0), mm(G['Ro']))
    cyl_i = tbm.createCylinderOrCone(pt(0, y_lo_c - 1, 0), mm(G['Ri']), pt(0, y_hi_c + 1, 0), mm(G['Ri']))
    tube = cyl_o
    if not tbm.booleanOperation(tube, cyl_i, adsk.fusion.BooleanTypes.DifferenceBooleanType):
        raise RuntimeError('Could not create the trimming tube.')
    trimmed = tbm.booleanOperation(acc, tube, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    if not trimmed:
        REP.fail('Lattice trim to the cylindrical shell FAILED: struts keep flat faces and slightly exceed the envelope.')

    stats = {'n_struts': n_struts, 'unmerged': len(failed), 'trimmed': bool(trimmed)}
    # window volume (Y_lo..Y_hi) for porosity
    try:
        win_o = tbm.createCylinderOrCone(pt(0, G['Y_lo'], 0), mm(G['Ro']), pt(0, G['Y_hi'], 0), mm(G['Ro']))
        win_i = tbm.createCylinderOrCone(pt(0, G['Y_lo'] - 1, 0), mm(G['Ri']), pt(0, G['Y_hi'] + 1, 0), mm(G['Ri']))
        tbm.booleanOperation(win_o, win_i, adsk.fusion.BooleanTypes.DifferenceBooleanType)
        cp = tbm.copy(acc)
        if tbm.booleanOperation(cp, win_o, adsk.fusion.BooleanTypes.IntersectionBooleanType):
            stats['V_window'] = cp.volume * 1000.0
        stats['V_total_pre'] = acc.volume * 1000.0
    except Exception:
        REP.note('Window volume for porosity could not be evaluated on the temporary body.')
    return acc, failed, stats


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
# THREAD (groove profile, helical sweep cut, annular fallback)
# =====================================================================================
def thread_numbers(G):
    c = CFG
    P, d, e = c['thread_pitch'], c['thread_depth'], c['thread_parameter_e']
    t_lead = math.tan(math.radians(c['thread_angle_alpha']))
    t_trail = math.tan(math.radians(90.0 - c['thread_angle_beta']))
    W_top = P - e
    ext = 0.04
    T = {
        't_lead': t_lead, 't_trail': t_trail,
        'z_a': d * t_trail, 'z_b': W_top - d * t_lead,
        'z_lt': -ext * t_trail, 'z_rt': W_top + ext * t_lead,
        'R_top': G['Ro'] + ext,
    }
    T['floor'] = T['z_b'] - T['z_a']
    T['top_width'] = T['z_rt'] - T['z_lt']
    if T['floor'] <= 0.05:
        raise ValueError('Thread floor width <= 0 for the given alpha/beta/d/e/P.')
    if T['top_width'] >= P - 0.02:
        raise ValueError('Groove top width {:.3f} mm leaves no crest between turns (pitch {}).'.format(T['top_width'], fmt(P)))
    ia = 90.0 + math.degrees(math.atan(t_trail))
    ib = 90.0 + math.degrees(math.atan(t_lead))
    tl_a = c['thread_radius_r2'] / math.tan(math.radians(ia / 2.0))
    tl_b = c['thread_radius_r1'] / math.tan(math.radians(ib / 2.0))
    T['fillets_ok'] = (tl_a + tl_b) < T['floor'] * 0.98 and tl_b < d / math.cos(math.radians(c['thread_angle_alpha'])) * 0.98
    return T


def draw_groove(sk, G, T, y_floor_mid):
    c = CFG
    y0 = y_floor_mid - 0.5 * (T['z_a'] + T['z_b'])
    Rr, Rt = G['R_root'], T['R_top']
    pts = [(Rr, y0 + T['z_a']), (Rr, y0 + T['z_b']), (Rt, y0 + T['z_rt']), (Rt, y0 + T['z_lt'])]
    L = draw_polygon(sk, pts)
    filleted = False
    if T['fillets_ok']:
        def mid(line):
            a, b = line.startSketchPoint.geometry, line.endSketchPoint.geometry
            return adsk.core.Point3D.create((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, 0)
        try:
            arcs = sk.sketchCurves.sketchArcs
            arcs.addFillet(L[0], mid(L[0]), L[1], mid(L[1]), mm(c['thread_radius_r1']))
            arcs.addFillet(L[3], mid(L[3]), L[0], mid(L[0]), mm(c['thread_radius_r2']))
            filleted = True
        except Exception:
            REP.warn('Thread root fillets r1/r2 could not be applied; sharp groove roots are used.')
    else:
        REP.warn('Thread fillets r1/r2 do not fit the groove geometry; sharp groove roots are used.')
    return filleted


def make_helix_wire(tbm, G, y_s, turns):
    P = CFG['thread_pitch']
    try:
        w = tbm.createHelixWire(pt(0, y_s, 0), vec((0, 1, 0)), pt(G['R_root'], y_s, 0), mm(P), turns, 0.0)
        if isinstance(w, tuple):
            w = w[0]
        return w, 'TemporaryBRepManager.createHelixWire'
    except Exception:
        pass
    # fallback: cubic B-spline through compensated control points
    m_per_turn = 24
    npts = int(math.ceil(turns * m_per_turn)) + 1
    th = 2.0 * math.pi / m_per_turn
    comp_f = (4.0 + 2.0 * math.cos(th)) / 6.0
    Rc = G['R_root'] / comp_f
    ctrl = []
    for i in range(npts):
        a = 2.0 * math.pi * i / m_per_turn
        ctrl.append(pt(Rc * math.cos(a), y_s + P * i / float(m_per_turn), -Rc * math.sin(a)))
    knots = [0.0] * 4 + [float(k) for k in range(1, npts - 3)] + [float(npts - 3)] * 4
    curve = adsk.core.NurbsCurve3D.createNonRational(ctrl, 3, knots, False)
    res = adsk.fusion.TemporaryBRepManager.get().createWireFromCurves([curve], True)
    if isinstance(res, tuple):
        res = res[0]
    return res, 'cubic B-spline approximation of a helix'


def cut_thread(comp, G):
    """Returns a short status string."""
    c = CFG
    T = thread_numbers(G)
    P = c['thread_pitch']
    y_s = G['Y_lo'] - P
    turns = (G['Y_hi'] - G['Y_lo']) / P + 2.0
    lattice = find_body(comp, 'A1_Lattice_Shell')
    v_before = lattice.volume * 1000.0

    # ---- try helical sweep ----
    helical_ok, how = False, ''
    try:
        sk = comp.sketches.add(comp.xYConstructionPlane)
        sk.name = 'Thread_Groove_Profile'
        draw_groove(sk, G, T, y_s)
        if sk.profiles.count != 1:
            raise RuntimeError('Groove sketch produced {} profiles.'.format(sk.profiles.count))
        tbm = adsk.fusion.TemporaryBRepManager.get()
        wire, how = make_helix_wire(tbm, G, y_s, turns)
        wbody = add_temp_body(comp, wire, 'Thread_Helix_Path', 'Thread_Helix_Path_BaseFeature')
        path = comp.features.createPath(wbody.edges.item(0))
        sweeps = comp.features.sweepFeatures
        sin = sweeps.createInput(sk.profiles.item(0), path, adsk.fusion.FeatureOperations.CutFeatureOperation)
        try:
            sin.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
        except Exception:
            pass
        try:
            sin.participantBodies = [lattice]
        except Exception:
            pass
        feat = sweeps.add(sin)
        feat.name = 'Thread_Helical_Groove_Sweep_Cut'
        lattice = find_body(comp, 'A1_Lattice_Shell')
        v_after = lattice.volume * 1000.0
        if v_before - v_after > 0.05:
            helical_ok = True
            try:
                wbody.isVisible = False
            except Exception:
                pass
        else:
            REP.warn('Helical sweep-cut ran but removed no measurable material.')
    except Exception:
        tb = traceback.format_exc().strip().splitlines()
        REP.warn('Helical thread FAILED ({}).'.format(' | '.join(tb[-2:])))

    if helical_ok:
        REP.ok('External thread: true HELICAL groove cut (path: {}); pitch {} mm, depth {} mm, {:.1f} turns; '
               'volume removed {:.1f} mm^3.'.format(how, fmt(P), fmt(c['thread_depth']), turns, v_before - v_after))
        return 'helical'

    if not ALLOW_ANNULAR_THREAD_FALLBACK:
        raise RuntimeError('Helical thread failed and the annular fallback is disabled.')

    # ---- fallback: annular (non-helical) grooves ----
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = 'Thread_Groove_Profiles_Annular_Fallback'
    sk.isComputeDeferred = True
    count = int(math.ceil((G['Y_hi'] - G['Y_lo']) / P)) + 2
    for i in range(count):
        draw_groove(sk, G, T, y_s + i * P)
    sk.isComputeDeferred = False
    profs = adsk.core.ObjectCollection.create()
    for i in range(sk.profiles.count):
        profs.add(sk.profiles.item(i))
    revs = comp.features.revolveFeatures
    rin = revs.createInput(profs, comp.yConstructionAxis, adsk.fusion.FeatureOperations.CutFeatureOperation)
    rin.setAngleExtent(False, vi('360 deg'))
    try:
        rin.participantBodies = [find_body(comp, 'A1_Lattice_Shell')]
    except Exception:
        pass
    f = revs.add(rin)
    f.name = 'Thread_Annular_Grooves_Fallback_Cut'
    v_after = find_body(comp, 'A1_Lattice_Shell').volume * 1000.0
    REP.warn('FALLBACK: the thread is a set of ANNULAR (non-helical) grooves at the nominal pitch, NOT a true helical thread.')
    REP.ok('Annular groove fallback cut {} grooves; volume removed {:.1f} mm^3.'.format(count, v_before - v_after))
    return 'annular'


# =====================================================================================
# HEAD, TIP, JOIN
# =====================================================================================
def build_end_solids(comp, G):
    c = CFG
    Re, Rh = G['Re'], G['Rh']
    tip_h, collar = c['tip_height'], G['collar']
    revs = comp.features.revolveFeatures
    cut = adsk.fusion.FeatureOperations.NewBodyFeatureOperation

    # --- tip: cone + solid collar ---
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = 'Tip_Profile'
    L = draw_polygon(sk, [(0, 0), (Re, tip_h), (Re, tip_h + collar), (0, tip_h + collar)])
    gc = sk.geometricConstraints
    safe_constraint(lambda: gc.addCoincident(L[0].startSketchPoint, sk.originPoint), 'tip apex on origin')
    safe_constraint(lambda: gc.addVertical(L[1]), 'tip collar vertical')
    safe_constraint(lambda: gc.addHorizontal(L[2]), 'tip top horizontal')
    safe_constraint(lambda: gc.addVertical(L[3]), 'tip axis vertical')
    P = [ln.startSketchPoint for ln in L]
    link_dim(sk, P[0], P[1], HORIZ, 'major_diameter / 2 - {} mm'.format(fmt(END_RADIUS_UNDERCUT)), 'tip radius')
    link_dim(sk, P[0], P[1], VERT, 'tip_height', 'tip height')
    link_dim(sk, P[1], P[2], VERT, 'end_collar_height', 'tip collar')
    if sk.profiles.count != 1:
        raise RuntimeError('Tip sketch produced {} profiles.'.format(sk.profiles.count))
    rin = revs.createInput(sk.profiles.item(0), L[3], cut)
    rin.setAngleExtent(False, vi('360 deg'))
    f = revs.add(rin)
    f.name = 'Tip_Revolve'
    tip_body = f.bodies.item(0)
    tip_body.name = 'Solid_Pointed_Tip'

    # --- head: collar + transition cone + head cylinder ---
    y_c0 = G['Y_hi']
    y1 = y_c0 + collar
    y2 = y1 + c['transition_height']
    y3 = y2 + c['head_height']
    hs = comp.sketches.add(comp.xYConstructionPlane)
    hs.name = 'Head_Transition_Profile'
    H = draw_polygon(hs, [(0, y_c0), (Re, y_c0), (Re, y1), (Rh, y2), (Rh, y3), (0, y3)])
    hgc = hs.geometricConstraints
    safe_constraint(lambda: hgc.addCoincident(H[0].startSketchPoint, hs.yConstructionAxis), 'head start on axis')
    safe_constraint(lambda: hgc.addHorizontal(H[0]), 'head base horizontal')
    safe_constraint(lambda: hgc.addVertical(H[1]), 'collar wall vertical')
    safe_constraint(lambda: hgc.addVertical(H[3]), 'head wall vertical')
    safe_constraint(lambda: hgc.addHorizontal(H[4]), 'head top horizontal')
    safe_constraint(lambda: hgc.addVertical(H[5]), 'head axis vertical')
    HP = [ln.startSketchPoint for ln in H]
    link_dim(hs, hs.originPoint, HP[0], VERT, 'tip_height + end_collar_height + shaft_length', 'head base height')
    link_dim(hs, HP[0], HP[1], HORIZ, 'major_diameter / 2 - {} mm'.format(fmt(END_RADIUS_UNDERCUT)), 'collar radius')
    link_dim(hs, HP[1], HP[2], VERT, 'end_collar_height', 'top collar')
    link_dim(hs, HP[2], HP[3], VERT, 'transition_height', 'transition height')
    link_dim(hs, HP[3], HP[4], VERT, 'head_height', 'head height')
    link_dim(hs, HP[5], HP[4], HORIZ, 'head_diameter / 2', 'head radius')
    if hs.profiles.count != 1:
        raise RuntimeError('Head sketch produced {} profiles.'.format(hs.profiles.count))
    hin = revs.createInput(hs.profiles.item(0), H[5], cut)
    hin.setAngleExtent(False, vi('360 deg'))
    hf = revs.add(hin)
    hf.name = 'Head_Transition_Revolve'
    head_body = hf.bodies.item(0)
    head_body.name = 'Solid_Head_And_Transition'
    REP.ok('Solid pointed tip and solid head + head-to-shaft transition cone created (revolved, timeline features).')
    return tip_body, head_body


def join_bodies(comp, target, tools):
    cf = comp.features.combineFeatures
    coll = adsk.core.ObjectCollection.create()
    for b in tools:
        coll.add(b)
    inp = cf.createInput(target, coll)
    inp.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
    inp.isKeepToolBodies = False
    f = cf.add(inp)
    f.name = 'Join_Lattice_Head_Tip'
    return f


# =====================================================================================
# MAIN BUILD
# =====================================================================================
def build_screw(design, G):
    c = CFG
    root = design.rootComponent
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = COMP_NAME

    # ---------- lattice ----------
    acc, unmerged, stats = build_lattice_temp(G)
    lattice = add_temp_body(comp, acc, 'A1_Lattice_Shell', 'A1_Lattice_BaseFeature')
    for i, b in enumerate(unmerged):
        add_temp_body(comp, b, 'A1_Unmerged_Strut_{:02d}'.format(i + 1), 'A1_Unmerged_Strut_BaseFeature_{:02d}'.format(i + 1))
    if unmerged:
        REP.fail('{} strut(s) could not be unioned in memory and were kept as separate bodies (A1_Unmerged_Strut_*). '
                 'The lattice is NOT a single connected solid.'.format(len(unmerged)))
    lumps = lattice.lumps.count
    V_env = math.pi * (G['Ro'] ** 2 - G['Ri'] ** 2) * G['L']
    G['V_env'] = V_env
    REP.ok('A1 lattice shell: {} strut boxes unioned and {} to the shell Ri={:.3f}..Ro={:.3f} mm; '
           'lumps in lattice body = {}.'.format(stats['n_struts'], 'trimmed' if stats['trimmed'] else 'NOT trimmed',
                                               G['Ri'], G['Ro'], lumps))
    if lumps != 1:
        REP.fail('Lattice body has {} disconnected lumps: it is NOT one connected solid.'.format(lumps))
    por_pre = None
    if 'V_window' in stats:
        por_pre = 1.0 - stats['V_window'] / V_env
        REP.ok('Lattice porosity BEFORE thread = {:.1f}% (1 - V_lattice[{:.1f} mm^3]/V_shell_envelope[{:.1f} mm^3]; '
               'envelope = annulus Ri..Ro x L = {} mm).'.format(por_pre * 100.0, stats['V_window'], V_env, fmt(G['L'])))
    G['V_embed'] = (stats.get('V_total_pre', 0.0) - stats.get('V_window', 0.0)) if ('V_window' in stats) else 0.0

    # ---------- thread ----------
    thread_status = 'disabled'
    if CREATE_THREAD:
        thread_status = stage('Thread', lambda: cut_thread(comp, G)) or 'FAILED'
        if thread_status == 'FAILED':
            REP.warn('NO thread was created: the shaft lattice has a smooth outer surface. This is a failed step, not a design choice.')
        lat2 = find_body(comp, 'A1_Lattice_Shell')
        if lat2 is not None and thread_status != 'FAILED':
            v_post = lat2.volume * 1000.0 - G['V_embed']
            REP.ok('Estimated lattice porosity AFTER thread = {:.1f}% (same envelope volume; end-embed volume subtracted).'.format(
                (1.0 - v_post / V_env) * 100.0))
    else:
        REP.warn('Thread creation is disabled (CREATE_THREAD = False): the lattice has a smooth outer surface.')
    G['thread_status'] = thread_status

    # ---------- head and tip ----------
    ends = stage('Head / tip', lambda: build_end_solids(comp, G))
    lattice = find_body(comp, 'A1_Lattice_Shell')
    if ends and JOIN_END_SOLIDS and lattice is not None:
        try:
            join_bodies(comp, lattice, list(ends))
        except Exception:
            tb = traceback.format_exc().strip().splitlines()
            REP.fail('Join of head/tip with the lattice FAILED ({}). Bodies are overlapping but separate.'.format(' | '.join(tb[-2:])))
    # ---------- final naming / checks ----------
    solids = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count) if comp.bRepBodies.item(i).isSolid]
    if len(solids) == 1:
        solids[0].name = BODY_NAME
        b = solids[0]
        bb = b.boundingBox
        REP.ok('Final screw: ONE solid body "{}", lumps = {}, volume {:.1f} mm^3, bbox {:.2f} x {:.2f} x {:.2f} mm.'.format(
            BODY_NAME, b.lumps.count, b.volume * 1000.0,
            (bb.maxPoint.x - bb.minPoint.x) * 10, (bb.maxPoint.y - bb.minPoint.y) * 10, (bb.maxPoint.z - bb.minPoint.z) * 10))
        if b.lumps.count != 1:
            REP.fail('Final body has {} lumps (not a single connected solid).'.format(b.lumps.count))
    else:
        REP.fail('Final model has {} separate solid bodies (expected 1): {}'.format(
            len(solids), ', '.join(s.name for s in solids)))
    return comp


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
        if design is None:
            raise RuntimeError('No active Fusion design in the new document.')
        try:
            design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        except Exception:
            REP.note('Could not force Parametric design type (document may already be parametric).')
        try:
            design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
        except Exception:
            pass

        if AUTO_TUNE_STRUT_TO_TARGET_POROSITY:
            CFG['cell_strut_thickness'] = tune_strut_thickness(
                CFG['cell_width'], CFG['cell_height'], CFG['a1_apex_ratio'], CFG['target_porosity'])
            REP.ok('Strut thickness auto-tuned to {} mm for the idealised planar target porosity.'.format(fmt(CFG['cell_strut_thickness'])))

        G = derive_geometry()
        est = stage('Planar porosity estimate', lambda: planar_solid_fraction(
            CFG['cell_width'], CFG['cell_height'], CFG['cell_strut_thickness'], CFG['a1_apex_ratio']))
        if est is not None:
            REP.ok('Idealised planar (unrolled, flat) porosity estimate = {:.1f}% for strut {} mm vs target {:.0f}% '
                   '(estimate only; not the 3D value).'.format((1.0 - est) * 100.0, fmt(CFG['cell_strut_thickness']),
                                                                CFG['target_porosity'] * 100.0))
            if abs((1.0 - est) - CFG['target_porosity']) > 0.03:
                REP.warn('Planar porosity estimate is not within 3 points of the 53% target; the A1 reconstruction with the '
                         'provisional 0.5 mm strut is not porosity-matched (set AUTO_TUNE_STRUT_TO_TARGET_POROSITY = True to tune).')
        stage('User parameters', lambda: create_user_parameters(design))
        stage('AS1_A1_Auxetic_Bone_Screw', lambda: build_screw(design, G))

        try:
            app.activeViewport.fit()
        except Exception:
            pass

        lines = ['AS1_A1 AUXETIC BONE SCREW - RECONSTRUCTION SUMMARY', '',
                 'Geometry reconstruction for research; NOT the original authors\' CAD model.',
                 'Geometry: R_out={:.3f}, R_in={:.3f} mm, {} circumferential x {} axial cells, strut {} mm,'.format(
                     G['Ro'], G['Ri'], G['n'], G['N'], fmt(G['t'])),
                 'cell arc width at outer surface {:.3f} mm, lattice window y = {:.2f}..{:.2f} mm, total length {:.2f} mm.'.format(
                     G['arc_w'], G['Y_lo'], G['Y_hi'], G['y_top']), '', 'CREATED / MEASURED:']
        lines += ['  - ' + m for m in REP.created]
        lines += ['', 'WARNINGS:' if REP.warnings else 'WARNINGS: none']
        lines += ['  - ' + m for m in REP.warnings]
        lines += ['', 'FAILED OPERATIONS:' if REP.failed else 'FAILED OPERATIONS: none']
        lines += ['  - ' + m for m in REP.failed]
        lines += ['', 'NOTES:']
        lines += ['  - ' + m for m in REP.notes]
        ui.messageBox('\n'.join(lines), 'AS1_A1 Auxetic Bone Screw')
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    pass
