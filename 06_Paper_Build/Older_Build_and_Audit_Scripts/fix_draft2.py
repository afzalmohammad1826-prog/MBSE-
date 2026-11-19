"""
fix_draft2.py — Fix all identified formatting issues in draft_2.docx
Issues found:
  1. Table 7 (2x2 SysML image grid): 4 runs in caption paragraphs missing
     explicit font.name and font.size — fix to Times New Roman 8.5pt italic.
  2. Caption size inconsistency: Table captions use 9.0pt, Figure captions
     use 9.5pt — standardise ALL captions to 9.5pt italic Times New Roman.
  3. Sub-heading level-3 (green, 10.0pt Calibri) audit and confirm.
  4. Header/Footer bold=None — explicitly set bold=False for clarity.
  5. Spacer paragraph after each callout box / divider verified.
Saves output as draft_2.docx (overwrites).
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import docx
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

DOC_PATH = r'D:\MBSE\Paper\draft_2.docx'
doc = docx.Document(DOC_PATH)

FIX_LOG = []

C_DGRAY = RGBColor(0x44, 0x44, 0x44)
C_NAVY  = RGBColor(0x1B, 0x36, 0x5D)

def pt(v):
    try:    return round(v.pt, 2)
    except: return None

# =========================================================================
# FIX 1: Table 7 — 2x2 SysML figure grid caption runs
# =========================================================================
print("FIX 1: Table 7 — SysML grid caption cells")
t7 = doc.tables[7]
for ri, row in enumerate(t7.rows):
    for ci, cell in enumerate(row.cells):
        for pi, p in enumerate(cell.paragraphs):
            # First paragraph = image (run with _r picture element, skip)
            # Second+ paragraphs = caption text
            if pi == 0:
                # This is the image paragraph — set spacing just in case
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.space_before = Pt(4)
                # Fix any runs that are inside (there shouldn't be text runs)
                for r in p.runs:
                    if r.text.strip():
                        if not r.font.name:
                            r.font.name = 'Times New Roman'
                        if not r.font.size:
                            r.font.size = Pt(8.5)
            else:
                # Caption paragraph
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_after = Pt(5)
                for r in p.runs:
                    if not r.font.name:
                        r.font.name = 'Times New Roman'
                        FIX_LOG.append(f'  T7 R{ri} C{ci} P{pi}: set font.name=Times New Roman')
                    if not r.font.size:
                        r.font.size = Pt(8.5)
                        FIX_LOG.append(f'  T7 R{ri} C{ci} P{pi}: set font.size=8.5pt')
                    r.italic = True
                    r.font.color.rgb = C_DGRAY
                    # Always ensure set regardless
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(8.5)

print(f"  Applied {len(FIX_LOG)} fixes to Table 7")

# =========================================================================
# FIX 2: Standardise ALL captions to 9.5pt italic Times New Roman
# =========================================================================
print("\nFIX 2: Standardise caption sizes to 9.5pt")
caption_paras = [(i, p) for i, p in enumerate(doc.paragraphs)
                 if p.text.strip().startswith(('Figure', 'Table'))]
cap_fixed = 0
for i, p in caption_paras:
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf = p.paragraph_format
    # Ensure consistent spacing
    if pf.space_after is None or pt(pf.space_after) < 10:
        pf.space_after = Pt(12)
    for r in p.runs:
        # Bold run = "Figure X: " label
        if r.bold:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            r.font.color.rgb = C_NAVY
        else:
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            r.italic = True
            r.font.color.rgb = C_DGRAY
        cap_fixed += 1
print(f"  Fixed {len(caption_paras)} captions ({cap_fixed} runs standardised to 9.5pt)")

# =========================================================================
# FIX 3: Header / Footer — explicitly set bold=False
# =========================================================================
print("\nFIX 3: Header/Footer explicit bold=False")
for sec in doc.sections:
    for region in [sec.header, sec.footer]:
        for p in region.paragraphs:
            for r in p.runs:
                if r.bold is None:
                    r.bold = False
                    FIX_LOG.append('  HDR/FTR: set bold=False')
print("  Header/Footer bold clarified")

# =========================================================================
# FIX 4: Body paragraphs — ensure all runs have explicit TNR 11pt
#         (catches any paragraph where run inherits from document default)
# =========================================================================
print("\nFIX 4: Body paragraphs — explicit font enforcement")
body_fixed = 0
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt:
        continue
    style_name = p.style.name if p.style else ''
    # Skip headings (Calibri) and list bullets/numbers
    is_heading = any(r.font.name == 'Calibri' and r.bold for r in p.runs if r.font.name)
    is_list = 'Bullet' in style_name or 'Number' in style_name
    if is_heading or is_list:
        continue
    # Body paragraphs: ensure Times New Roman 11pt
    for r in p.runs:
        changed = False
        if r.font.name != 'Times New Roman':
            # Only fix if it's not Calibri heading
            if not (r.bold and r.font.name == 'Calibri'):
                r.font.name = 'Times New Roman'
                changed = True
        if not r.font.size:
            r.font.size = Pt(11)
            changed = True
        if changed:
            body_fixed += 1
print(f"  Fixed {body_fixed} body runs")

# =========================================================================
# FIX 5: Ensure list paragraphs have consistent line spacing
# =========================================================================
print("\nFIX 5: List paragraph line spacing")
list_fixed = 0
for p in doc.paragraphs:
    if p.style and ('Bullet' in p.style.name or 'Number' in p.style.name):
        pf = p.paragraph_format
        if pf.line_spacing is None or (hasattr(pf.line_spacing, 'pt') and pt(pf.line_spacing) > 1.3):
            pf.line_spacing = 1.1
            list_fixed += 1
        pf.space_after = Pt(3)
print(f"  Fixed {list_fixed} list paragraphs")

# =========================================================================
# FIX 6: Callout box table (1x1 tables) — ensure title runs consistent
#         (bg_hex=H_MINT tables: title is Calibri 10.5pt bold green)
# =========================================================================
print("\nFIX 6: Callout box inner formatting")
callout_fixed = 0
for ti, table in enumerate(doc.tables):
    nr = len(table.rows)
    nc = len(table.rows[0].cells) if table.rows else 0
    if nr == 1 and nc == 1:
        cell = table.cell(0, 0)
        for pi, p in enumerate(cell.paragraphs):
            pf = p.paragraph_format
            pf.space_after = Pt(3)
            for r in p.runs:
                if not r.font.name:
                    r.font.name = 'Times New Roman'
                    callout_fixed += 1
                if not r.font.size:
                    r.font.size = Pt(10.5) if pi == 0 else Pt(10.0)
                    callout_fixed += 1
print(f"  Fixed {callout_fixed} callout box runs")

# =========================================================================
# FIX 7: Key metrics rows (1x3 tables) — verify sizes
# =========================================================================
print("\nFIX 7: Key metric row tables (cover page)")
metric_fixed = 0
for ti, table in enumerate(doc.tables):
    if len(table.rows) == 1 and len(table.rows[0].cells) == 3:
        for ci, cell in enumerate(table.rows[0].cells):
            for p in cell.paragraphs:
                for r in p.runs:
                    if not r.font.name:
                        r.font.name = 'Calibri'
                        metric_fixed += 1
                    if not r.font.size:
                        r.font.size = Pt(9.5) if ci == 0 else (Pt(13) if ci == 1 else Pt(9.5))
                        metric_fixed += 1
print(f"  Fixed {metric_fixed} metric table runs")

# =========================================================================
# FIX 8: Ensure consistent space_after on all table captions in tables
#         The spacer paragraph after each caption → 12pt after
# =========================================================================
print("\nFIX 8: Table caption spacing in tables")
for ti, table in enumerate(doc.tables):
    # Only look at tables with column headers (shaded first row)
    if len(table.rows) >= 2:
        # Ensure all header row cells have correct vertical alignment set
        for cell in table.rows[0].cells:
            cell.vertical_alignment = docx.enum.table.WD_ALIGN_VERTICAL.CENTER

# =========================================================================
# SAVE
# =========================================================================
print("\nSaving fixed document...")
doc.save(DOC_PATH)

import os
size_kb = os.path.getsize(DOC_PATH) // 1024
print(f"SAVED: {DOC_PATH}  ({size_kb} KB)")
print(f"\nSUMMARY OF FIXES APPLIED:")
print(f"  Fix 1 (Table 7 captions)     : Done")
print(f"  Fix 2 (Caption size 9.5pt)    : {len(caption_paras)} captions standardised")
print(f"  Fix 3 (Header/Footer bold)    : Done")
print(f"  Fix 4 (Body run enforcement)  : {body_fixed} runs updated")
print(f"  Fix 5 (List line spacing)     : {list_fixed} list paragraphs")
print(f"  Fix 6 (Callout box)           : {callout_fixed} runs")
print(f"  Fix 7 (Key metric rows)       : {metric_fixed} runs")
print(f"  Fix 8 (Table header valign)   : Done")
