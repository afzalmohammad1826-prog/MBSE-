"""
fix_table7.py — Fix Table 7 (2x2 SysML image grid) missing run fonts.
The 4 runs are picture runs (image objects), not text runs.
We need to find the actual caption text paragraphs and fix them at XML level.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_ALIGN_PARAGRAPH

DOC_PATH = r'D:\MBSE\Paper\draft_2.docx'
doc = docx.Document(DOC_PATH)

C_DGRAY = RGBColor(0x44, 0x44, 0x44)

# Inspect Table 7 in detail
t7 = doc.tables[7]
print(f"Table 7: {len(t7.rows)} rows x {len(t7.rows[0].cells)} cols")

for ri, row in enumerate(t7.rows):
    for ci, cell in enumerate(row.cells):
        print(f"\n  Cell [{ri},{ci}]: {len(cell.paragraphs)} paragraphs")
        for pi, p in enumerate(cell.paragraphs):
            print(f"    Para {pi}: align={p.alignment} runs={len(p.runs)} text='{p.text[:50]}'")
            for rj, run in enumerate(p.runs):
                # Check if this run contains a drawing (image)
                has_drawing = run._r.find(qn('w:drawing')) is not None
                has_pict    = run._r.find(qn('w:pict')) is not None
                print(f"      Run {rj}: font={run.font.name!r} size={run.font.size} "
                      f"bold={run.bold} italic={run.italic} "
                      f"drawing={has_drawing} pict={has_pict} "
                      f"text='{run.text[:30]!r}'")
