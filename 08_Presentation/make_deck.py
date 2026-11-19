# -*- coding: utf-8 -*-
"""CK chain presentation, styled after the SDMI reference (rust / orange / beige chain with E-R-F pills)."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

RUST = RGBColor(0x8E, 0x3B, 0x25)
BANNER = RGBColor(0x95, 0x3F, 0x25)
DARK = RGBColor(0x6B, 0x2A, 0x22)
ORANGE = RGBColor(0xF4, 0x93, 0x4F)
BEIGE = RGBColor(0xDD, 0xD5, 0xBE)
GREEN = RGBColor(0x66, 0x82, 0x3F)
PEACH = RGBColor(0xFB, 0xE3, 0xD3)
RED = RGBColor(0xE5, 0x39, 0x35)
INK = RGBColor(0x3B, 0x1F, 0x16)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT = 'Calibri'

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


def _fill(shape, color, line=None, lw=1.5):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(lw)
    shape.shadow.inherit = False


def text_in(shape, lines, size=14, color=INK, bold=True, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.MIDDLE,
            ml=0.15, italic_first=False):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(ml)
    tf.margin_top = tf.margin_bottom = Inches(0.05)
    lines = lines if isinstance(lines, list) else [lines]
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(3)
        r = p.add_run()
        r.text = ln
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.color.rgb = color
        r.font.name = FONT
        if italic_first and i == 1:
            r.font.italic = True


def rrect(slide, x, y, w, h, fill, radius=0.12):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = radius
    _fill(s, fill)
    return s


def badge(slide, x, y, letter, sub, kind, d=0.62):
    """Circle badge: C = rust, K = peach with rust ring."""
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    if kind == 'C':
        _fill(c, RUST)
        col = WHITE
    else:
        _fill(c, PEACH, RUST, 1.5)
        col = RUST
    tf = c.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = letter
    r.font.size = Pt(15); r.font.bold = True; r.font.color.rgb = col; r.font.name = FONT
    if sub:
        r2 = p.add_run(); r2.text = sub
        r2.font.size = Pt(9); r2.font.bold = True; r2.font.color.rgb = col; r2.font.name = FONT
        r2.font._element.set('baseline', '-25000')
    return c


def pill(slide, cx, cy, text, w=None):
    w = w or (0.35 + 0.115 * len(text))
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(cx - w / 2), Inches(cy - 0.15), Inches(w), Inches(0.3))
    s.adjustments[0] = 0.5
    _fill(s, DARK)
    text_in(s, text, size=12, color=WHITE, align=PP_ALIGN.CENTER, ml=0.05)
    return s


def line(slide, x1, y1, x2, y2, arrow=False, w=2.0):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = RGBColor(0, 0, 0)
    c.line.width = Pt(w)
    if arrow:
        ln = c.line._get_or_add_ln()
        t = etree.SubElement(ln, qn('a:tailEnd'))
        t.set('type', 'triangle')
    return c


def side_arrow(slide, y, x1=0.97, x2=1.35):
    line(slide, x1, y, x2, y, arrow=True)


def chain(slide, y_from, y_to, label, x_from=12.2, x_to=1.0):
    """Elbow arrow from the bottom-right of one block to the top-left of the next, with a pill."""
    ym = (y_from + y_to) / 2
    line(slide, x_from, y_from, x_from, ym)
    line(slide, x_from, ym, x_to, ym)
    line(slide, x_to, ym, x_to, y_to, arrow=True)
    pill(slide, (x_from + x_to) / 2, ym, label)


def k_block(slide, y, h, left, corner, bullets, tag=None, size=14):
    rrect(slide, 1.35, y, 11.85, h, ORANGE)
    s = slide.shapes.add_textbox(Inches(1.85), Inches(y + 0.05), Inches(9.0 if tag else 11.0), Inches(h - 0.1))
    text_in(s, ['•  ' + b for b in bullets], size=size, color=INK, ml=0.05)
    badge(slide, 0.3, y + h / 2 - 0.31, left[0], left[1], 'C' if left[0] == 'C' else 'K')
    side_arrow(slide, y + h / 2)
    badge(slide, 1.05, y - 0.2, corner[0], corner[1], 'K')
    if tag:
        t = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(11.0), Inches(y + 0.1), Inches(1.95), Inches(0.9))
        _fill(t, RED)
        text_in(t, tag, size=11, color=WHITE, align=PP_ALIGN.CENTER, ml=0.05)


def c_block(slide, y, h, left, corner, text, pill_text=None, size=14, w=11.85):
    rrect(slide, 1.35, y, w, h, BEIGE)
    s = slide.shapes.add_textbox(Inches(1.85), Inches(y + 0.03), Inches(w - 1.0), Inches(h - 0.06))
    text_in(s, text, size=size, color=INK, ml=0.05)
    badge(slide, 0.3, y + h / 2 - 0.31, left[0], left[1], 'C' if left[0] == 'C' else 'K')
    side_arrow(slide, y + h / 2)
    badge(slide, 1.05, y - 0.2, corner[0], corner[1], 'C')
    if pill_text:
        pill(slide, 6.7, y - 0.02, pill_text)


def footer(slide, n):
    t = slide.shapes.add_textbox(Inches(0.4), Inches(7.12), Inches(9), Inches(0.3))
    text_in(t, 'G Mohammad Afzal  |  ME23B2014  |  Strategic Management of Design and Innovation', size=10, color=RUST, bold=False, ml=0)
    t = slide.shapes.add_textbox(Inches(12.1), Inches(7.12), Inches(0.9), Inches(0.3))
    text_in(t, str(n), size=10, color=RUST, bold=False, align=PP_ALIGN.RIGHT, ml=0)


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# =============== SLIDE 1: problem, K0 / C0, K1, C1
s = prs.slides.add_slide(BLANK)
b = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(0.9)); _fill(b, BANNER)
e = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1.2), Inches(0.25), Inches(15.7), Inches(1.15)); _fill(e, BANNER)
t = s.shapes.add_textbox(Inches(0.4), Inches(0.12), Inches(12.4), Inches(1.1))
text_in(t, ['PROBLEM STATEMENT:',
            'Screws loosen in weak bone. Auxetic screws promise better grip, but their soft core creates a stiffness step '
            'at the head, and design work is not linked to requirements.'],
        size=15, color=WHITE, anchor=MSO_ANCHOR.TOP, ml=0.05, italic_first=True)
g = rrect(s, 0, 1.65, 12.7, 1.55, GREEN, 0.15)
badge(s, 0.3, 1.78, 'K', '0', 'K')
badge(s, 0.3, 2.45, 'C', '0', 'C')
t = s.shapes.add_textbox(Inches(1.1), Inches(1.72), Inches(11.4), Inches(0.7))
text_in(t, 'Screws loosen in weak bone. Auxetic structures widen when pulled. Requirements can be traced in a systems model. CAD and simulation tools exist.',
        size=14, color=WHITE, ml=0.05)
t = s.shapes.add_textbox(Inches(1.1), Inches(2.42), Inches(11.4), Inches(0.7))
text_in(t, '"A bone screw that grips by widening when it is pulled out, designed through a requirements-linked model."',
        size=14, color=WHITE, ml=0.05)
chain(s, 3.2, 3.75, 'E (Expansion)', x_from=12.3, x_to=0.6)
k_block(s, 3.95, 1.75, ('C', '0'), ('K', '1'),
        ['Auxetic cells have been studied as unit cells and sandwich panels, not as a full screw design.',
         'A wider core meets the solid head: a stiffness step where fatigue is expected to start.',
         'No source says what "grips better" means in numbers.',
         'SysML and the V-model exist, but are not linked to the screw CAD and simulation.'],
        tag=['GAP:', 'THE TRANSITION', 'PARADOX'], size=13)
c_block(s, 6.05, 0.85, ('K', '1'), ('C', '1'),
        '"A screw whose porous core is generated from requirements, with the stiffness step managed."',
        pill_text='F (Reframing)')
footer(s, 1)
notes(s, "Question one: the problem and the idea. The problem is that screws loosen in weak bone, and auxetic screws have their own weakness, a stiffness step at the head. "
         "K0 is what I knew: screws loosen, auxetic structures widen when pulled, and requirements can be traced in a model. C0 is the concept I launched from that: "
         "a screw that grips by widening when pulled out. It is undecidable because I cannot call it true or false without bone tests. "
         "E means expansion: I looked for new knowledge, K1. The gap was the transition paradox, and that nobody had defined what better grip means. "
         "That reframed the concept, F, into C1: generate the core from requirements, and manage the stiffness step.")

# =============== SLIDE 2: K2, C1.1, C1.2, C2
s = prs.slides.add_slide(BLANK)
k_block(s, 0.45, 1.65, ('C', '1'), ('K', '2'),
        ['Three unit cells to compare: re-entrant chevron (AS1), hourglass (AS2) and a hexagonal control (NS).',
         'Generative design: split the design space into preserve, keep-out and design regions.',
         'Strut thickness can change along the screw axis, so the stiffness can be graded.',
         'Performance must be checked by simulation, not by looks.'], size=13)
chain(s, 2.1, 2.85, 'R - Refinement.', x_from=12.3, x_to=1.15)
c_block(s, 3.0, 0.8, ('K', '2'), ('C', '1.1'),
        '"A screw family (AS1, AS2, NS) built from one requirements-linked parameter set."')
c_block(s, 4.2, 0.8, ('C', '1.1'), ('C', '1.2'),
        '"An AS2 screw whose strut thickness rises smoothly toward the head, to soften the stiffness step."',
        pill_text='R - Refinement.')
c_block(s, 5.4, 0.8, ('C', '1.2'), ('C', '2'),
        '"A screw whose stiffness step is moved and tracked, not assumed removed, with every claim tied to its evidence."',
        pill_text='F - Reframing')
for i, (lbl, txt) in enumerate([('E', 'Expansion: new K is added'), ('R', 'Refinement: the concept is narrowed'),
                                ('F', 'Reframing: the concept changes direction'), ('?', 'Unclear: not yet decidable')]):
    x = 0.6 + i * 3.1
    pill(s, x + 0.2, 6.6, lbl, w=0.5)
    t = s.shapes.add_textbox(Inches(x + 0.5), Inches(6.43), Inches(2.6), Inches(0.35))
    text_in(t, txt, size=11, color=RUST, bold=False, ml=0.02)
footer(s, 2)
notes(s, "K2 is the knowledge I needed to explore C1: three unit-cell types, generative design that splits the design space into regions, and graded strut thickness. "
         "R, refinement, narrows the concept: first to a screw family built from one parameter set, C1.1, then to a graded AS2, C1.2. "
         "Then a reframing, F: after testing, the question changed from making the step disappear to moving it and tracking the evidence. That is C2.")

# =============== SLIDE 3: K3, C3, C3.1, K3.1
s = prs.slides.add_slide(BLANK)
k_block(s, 0.45, 1.9, ('C', '2'), ('K', '3'),
        ['Simulation ranking is stable: AS1 > AS2 > NS on every mesh.',
         'Peak stress does not converge, so it can only be used to rank screws, not as a value.',
         'Grading cut stress next to the head by about 19%, but raised it in the ramp by about 27%.',
         'The stiffness step was moved, not removed.'], size=13)
chain(s, 2.35, 3.05, 'E - Expansion.', x_from=12.3, x_to=1.15)
c_block(s, 3.2, 0.85, ('K', '3'), ('C', '3'),
        'A requirements-traced screw whose claims are labelled by evidence level: simulated, bench-tested or clinical.')
c_block(s, 4.55, 0.8, ('C', '3'), ('C', '3.1'),
        'A screw that is shown to grip better in bone.', pill_text='? - Unclear')
k_block(s, 5.7, 1.25, ('C', '3.1'), ('K', '3.1'),
        ['Bone contact and fatigue are not modelled.',
         'Pullout (ASTM F543) has not been tested.',
         'Material data are typical wrought values, not measured as-built values.'], size=13)
footer(s, 3)
notes(s, "Question three: why C stays undecidable, and how I explored it. K3 is what the simulations told me. The ranking of the three screws was stable, but peak stress never converged, so I used it only to rank. "
         "Grading lowered stress next to the head and raised it in the ramp. The step was moved, not removed. "
         "That expansion, E, gave C3: a screw whose claims are labelled by evidence level. "
         "The original idea, a screw that grips better in bone, is marked unclear. K3.1 shows why: no bone contact, no fatigue, no pullout test. "
         "So C is still undecidable, and the simulation work made that visible.")

# =============== SLIDE 4: C3.1.1, tables, scope drift
s = prs.slides.add_slide(BLANK)
c_block(s, 0.55, 0.8, ('K', '3.1'), ('C', '3.1.1'),
        'A test plan: pullout (ASTM F543) and fatigue tests in a bone analogue, for the graded, uniform and control screws.',
        pill_text='R - Refinement.')
# stage table
rows = [('C0 \u2192 K1', 'E', 'Expansion'), ('K1 \u2192 C1', 'F', 'Reframing'), ('C1 \u2192 C1.1', 'R', 'Refinement'),
        ('C1.1 \u2192 C1.2', 'R', 'Refinement'), ('C1.2 \u2192 C2', 'F', 'Reframing'), ('C2 \u2192 K3 \u2192 C3', 'E', 'Expansion'),
        ('C3 \u2192 C3.1', '?', 'Unclear'), ('C3.1 \u2192 K3.1', 'E', 'Expansion'), ('K3.1 \u2192 C3.1.1', 'R', 'Refinement')]
tbl = s.shapes.add_table(len(rows) + 1, 3, Inches(0.45), Inches(1.85), Inches(5.3), Inches(3.9)).table
for j, (w, hd, fc) in enumerate([(2.2, 'Stage', GREEN), (1.3, 'Transition', DARK), (1.8, 'Meaning', WHITE)]):
    tbl.columns[j].width = Inches(w)
    c = tbl.cell(0, j); c.fill.solid(); c.fill.fore_color.rgb = fc
    c.text_frame.text = hd
    r = c.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(13); r.font.bold = True; r.font.name = FONT
    r.font.color.rgb = WHITE if fc != WHITE else INK
for i, row in enumerate(rows, start=1):
    for j, v in enumerate(row):
        c = tbl.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = WHITE
        c.text_frame.text = v
        r = c.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(12); r.font.name = FONT; r.font.color.rgb = INK
# why undefined
t = s.shapes.add_textbox(Inches(6.2), Inches(1.7), Inches(6.7), Inches(0.4))
text_in(t, 'Why is it undecided?', size=15, color=RUST, align=PP_ALIGN.CENTER)
why = [('C0', 'Grip in bone and fatigue at the head are unknown.'),
       ('C1', 'Whether a generated core can meet all requirements is unverified.'),
       ('C1.1', 'Which unit cell is best in bone is unknown; only stiffness is known.'),
       ('C1.2', 'The effect of grading on fatigue is unverified; stress did not converge.'),
       ('C2', 'Whether moving the step helps real fixation is unknown.'),
       ('C3', 'Evidence beyond simulation does not exist yet.'),
       ('C3.1', 'Pullout and fatigue in bone are untested.'),
       ('C3.1.1', 'Test results will decide it; none exist yet.')]
tb2 = s.shapes.add_table(len(why), 2, Inches(6.2), Inches(2.15), Inches(6.7), Inches(3.6)).table
tb2.columns[0].width = Inches(1.0); tb2.columns[1].width = Inches(5.7)
for i, (a, bb) in enumerate(why):
    for j, v in enumerate((a, bb)):
        c = tb2.cell(i, j); c.fill.solid(); c.fill.fore_color.rgb = WHITE
        c.text_frame.text = v
        r = c.text_frame.paragraphs[0].runs[0]; r.font.size = Pt(12); r.font.name = FONT; r.font.color.rgb = INK
t = s.shapes.add_textbox(Inches(0.45), Inches(6.0), Inches(12.4), Inches(1.0))
text_in(t, ['SCOPE DRIFT IN THE LOGIC:',
            'The project began as a screw that grips better. By C2 it had become a study of how to manage a stiffness step and prove it with evidence.'],
        size=13, color=RUST, anchor=MSO_ANCHOR.TOP, ml=0)
footer(s, 4)
notes(s, "Question four: the final C and what I learned. The final C is the test plan, C3.1.1: pullout and fatigue tests in a bone analogue for the graded, uniform and control screws. "
         "The left table lists each transition. E is expansion, R is refinement, F is reframing. The right table says why each concept is still undecided. "
         "What I learned from C to K is the scope drift at the bottom. The project began as a screw that grips better, and became a study of how to manage a stiffness step and prove it with evidence. "
         "New knowledge to chase: bone contact, fatigue and pullout. Thank you.")

prs.save('D:/MBSE/Paper/presentation/CK_Presentation_v2.pptx')
print('saved')
