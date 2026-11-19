"""
fix_image_runs.py — Fix the 4 image (drawing) runs in Table 7 that have
font=None size=None. These are the picture-container runs — set their rPr
to Times New Roman 8.5pt so the XML is clean and consistent.
Also fix caption size=107950 EMU (8.5pt) to explicit 8.5pt.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DOC_PATH = r'D:\MBSE\Paper\draft_2.docx'
doc = docx.Document(DOC_PATH)

def set_run_font_xml(run, font_name='Times New Roman', size_pt=8.5):
    """Force font and size onto a run via XML rPr."""
    rPr = run._r.get_or_add_rPr()

    # Remove any existing rFonts
    for old in rPr.findall(qn('w:rFonts')):
        rPr.remove(old)

    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'),    font_name)
    rFonts.set(qn('w:hAnsi'),   font_name)
    rFonts.set(qn('w:cs'),      font_name)
    rPr.insert(0, rFonts)

    # Remove any existing sz / szCs
    for old in rPr.findall(qn('w:sz')):
        rPr.remove(old)
    for old in rPr.findall(qn('w:szCs')):
        rPr.remove(old)

    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(int(size_pt * 2)))   # half-points
    rPr.append(sz)

    szCs = OxmlElement('w:szCs')
    szCs.set(qn('w:val'), str(int(size_pt * 2)))
    rPr.append(szCs)

t7 = doc.tables[7]
fixes = 0

for ri, row in enumerate(t7.rows):
    for ci, cell in enumerate(row.cells):
        for pi, p in enumerate(cell.paragraphs):
            for rj, run in enumerate(p.runs):
                has_drawing = run._r.find(qn('w:drawing')) is not None
                if has_drawing:
                    # Image run — set font on the rPr for XML cleanliness
                    set_run_font_xml(run, 'Times New Roman', 8.5)
                    fixes += 1
                    print(f"  Fixed image run T7[{ri},{ci}] para{pi} run{rj}")
                else:
                    # Caption text run — standardise to 8.5pt
                    set_run_font_xml(run, 'Times New Roman', 8.5)
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(8.5)
                    run.italic = True
                    fixes += 1

doc.save(DOC_PATH)
import os
size_kb = os.path.getsize(DOC_PATH) // 1024
print(f"\nApplied {fixes} XML-level fixes to Table 7 image/caption runs")
print(f"Saved: {DOC_PATH}  ({size_kb} KB)")
