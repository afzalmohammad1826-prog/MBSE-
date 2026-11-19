# -*- coding: utf-8 -*-
import sys, os, shutil
sys.stdout.reconfigure(encoding='utf-8')
import paper_helpers as H
from paper_helpers import *
import part_a, part_b, part_c, part_d

H.FIGURES_DIR = 'D:/MBSE/Paper/figs2'
shutil.copy('D:/MBSE/Paper/figures/v_model_diagram.png', 'D:/MBSE/Paper/figs2/v_model_diagram.png')
shutil.copy('D:/MBSE/Paper/figs2/sysml_composite.png', 'D:/MBSE/Paper/figs2/FIG2_COMPOSITE.png')

_orig = H.add_wiley_figure


def fig(doc, filename, n, cap, width_in=5.8):
    if filename == 'FIG2_COMPOSITE':
        filename = 'FIG2_COMPOSITE.png'
    return _orig(doc, filename, n, cap, width_in)


for m in (part_a, part_b, part_c, part_d):
    m.add_wiley_figure = fig

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Inches(1.0)
    s.left_margin = s.right_margin = Inches(1.0)
    hp = s.header.paragraphs[0]
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r = hp.add_run("Systems Engineering | Research Article")
    r.font.name = 'Calibri'; r.font.size = Pt(8); r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    fp = s.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = fp.add_run("MBSE framework for auxetic bone screws")
    r.font.name = 'Calibri'; r.font.size = Pt(8); r.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

part_a.build_front(doc)
part_a.build_intro(doc)
part_a.build_background(doc)
part_a.build_framework(doc)
part_a.build_requirements(doc)
part_b.build_methods(doc)
part_d.build_graded(doc)
part_c.build_trace(doc)
part_d.build_discussion(doc)
part_d.build_conclusions(doc)
part_c.build_refs(doc)
out = 'D:/MBSE/Paper/draft_5.docx'
doc.save(out)
print('saved', out)
