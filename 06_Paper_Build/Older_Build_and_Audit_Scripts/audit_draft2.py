"""
audit_draft2.py — Inspect every paragraph and table cell in draft_2.docx
and report font names, sizes, colors, alignment, and style inconsistencies.
"""
import docx
from docx.shared import Pt
from docx.oxml.ns import qn

doc = docx.Document(r'D:\MBSE\Paper\draft_2.docx')

issues = []

EXPECTED_BODY_FONTS  = {'Times New Roman'}
EXPECTED_HEAD_FONTS  = {'Calibri', 'Times New Roman'}
ALLOWED_SIZES_PT     = {8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 13.0, 20.0}

def pt(size_obj):
    if size_obj is None:
        return None
    return round(size_obj.pt, 1)

print("=" * 80)
print("PARAGRAPH AUDIT")
print("=" * 80)
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt:
        continue
    align = str(p.alignment)
    pf = p.paragraph_format
    sa = round(pf.space_after.pt, 1) if pf.space_after else None
    sb = round(pf.space_before.pt, 1) if pf.space_before else None

    for j, run in enumerate(p.runs):
        fname = run.font.name
        fsize = pt(run.font.size)
        fbold = run.bold
        fital = run.italic
        fcolor = run.font.color.rgb if run.font.color and run.font.color.type else None
        snippet = run.text[:60].replace('\n', ' ')

        flags = []
        if fname and fname not in EXPECTED_BODY_FONTS and fname not in EXPECTED_HEAD_FONTS:
            flags.append(f'UNKNOWN_FONT:{fname}')
        if fsize and fsize not in ALLOWED_SIZES_PT:
            flags.append(f'ODD_SIZE:{fsize}')
        if fname is None:
            flags.append('NO_FONT_SET')
        if fsize is None:
            flags.append('NO_SIZE_SET')

        if flags:
            issues.append({
                'para': i, 'run': j,
                'text': snippet,
                'font': fname, 'size': fsize, 'bold': fbold, 'italic': fital,
                'flags': flags
            })
            print(f"  P{i:03d} R{j} | font={fname} size={fsize}pt bold={fbold} italic={fital} | {flags} | '{snippet}'")

print()
print("=" * 80)
print("TABLE AUDIT")
print("=" * 80)
for ti, table in enumerate(doc.tables):
    for ri, row in enumerate(table.rows):
        for ci, cell in enumerate(row.cells):
            for pi, p in enumerate(cell.paragraphs):
                for rj, run in enumerate(p.runs):
                    fname = run.font.name
                    fsize = pt(run.font.size)
                    snippet = run.text[:40].replace('\n',' ')
                    flags = []
                    if fname and fname not in EXPECTED_BODY_FONTS and fname not in EXPECTED_HEAD_FONTS:
                        flags.append(f'UNKNOWN_FONT:{fname}')
                    if fsize and fsize not in ALLOWED_SIZES_PT:
                        flags.append(f'ODD_SIZE:{fsize}')
                    if flags:
                        print(f"  T{ti} R{ri} C{ci} | font={fname} size={fsize}pt | {flags} | '{snippet}'")
                        issues.append({'table': ti, 'cell': (ri, ci), 'flags': flags})

print()
print("=" * 80)
print(f"TOTAL ISSUES FOUND: {len(issues)}")
print("=" * 80)

# Check document default style
ns = doc.styles['Normal']
print(f"\nNormal style -> font={ns.font.name}, size={pt(ns.font.size)}")
print(f"Heading 1    -> font={doc.styles['Heading 1'].font.name if 'Heading 1' in doc.styles else 'N/A'}")

# Check all unique font names used across the document
all_fonts = set()
for p in doc.paragraphs:
    for r in p.runs:
        if r.font.name:
            all_fonts.add(r.font.name)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    if r.font.name:
                        all_fonts.add(r.font.name)
print(f"\nAll unique fonts used: {sorted(all_fonts)}")

# Check all unique sizes
all_sizes = set()
for p in doc.paragraphs:
    for r in p.runs:
        if r.font.size:
            all_sizes.add(pt(r.font.size))
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    if r.font.size:
                        all_sizes.add(pt(r.font.size))
print(f"All unique sizes (pt): {sorted(all_sizes)}")
