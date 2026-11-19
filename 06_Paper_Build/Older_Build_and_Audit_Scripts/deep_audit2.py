"""
deep_audit2.py — Full formatting audit of draft_2.docx, ASCII-safe output.
"""
import sys
import docx
from docx.shared import Pt
from docx.oxml.ns import qn

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

doc = docx.Document(r'D:\MBSE\Paper\draft_2.docx')

def pt(v):
    try:
        return round(v.pt, 2)
    except:
        return None

def emu_to_in(v):
    try:
        return round(v / 914400, 3)
    except:
        return None

issues = []

# -----------------------------------------------------------------------
# 1. Paragraph spacing & alignment
# -----------------------------------------------------------------------
print("1. PARAGRAPH SPACING & ALIGNMENT")
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt:
        continue
    pf = p.paragraph_format
    sa  = pt(pf.space_after)
    sb  = pt(pf.space_before)
    al  = p.alignment

    run_fonts = set()
    run_sizes = set()
    for r in p.runs:
        if r.font.name: run_fonts.add(r.font.name)
        if r.font.size: run_sizes.add(pt(r.font.size))

    flags = []
    if sa is not None and sa > 25:
        flags.append(f'LARGE_SPACE_AFTER:{sa}pt')
    if len(run_fonts) > 1:
        flags.append(f'MIXED_FONTS:{sorted(run_fonts)}')
    if len(run_sizes) > 2:
        flags.append(f'MANY_SIZES:{sorted(run_sizes)}')

    if flags:
        issues.append(('P', i, flags, txt[:60]))
        print(f"  P{i:03d} | {flags} | '{txt[:60]}'")

print(f"  Paragraph issues: {sum(1 for x in issues if x[0]=='P')}")

# -----------------------------------------------------------------------
# 2. Heading consistency (Calibri bold >= 10pt)
# -----------------------------------------------------------------------
print("\n2. HEADING STYLE CONSISTENCY")
heading_data = []
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt:
        continue
    pPr = p._p.find(qn('w:pPr'))
    has_border = False
    if pPr is not None:
        pBdr = pPr.find(qn('w:pBdr'))
        has_border = pBdr is not None

    for r in p.runs:
        if r.font.name == 'Calibri' and r.bold and r.font.size and pt(r.font.size) >= 10.0:
            color_str = 'None'
            try:
                if r.font.color and r.font.color.type:
                    color_str = str(r.font.color.rgb)
            except:
                pass
            heading_data.append({
                'idx': i, 'text': txt[:55],
                'size': pt(r.font.size),
                'border': has_border,
                'color': color_str,
                'sa': pt(p.paragraph_format.space_after),
                'sb': pt(p.paragraph_format.space_before),
                'align': p.alignment,
            })
            break

section_headings = [h for h in heading_data if h['size'] in {12.0}]
sub_headings     = [h for h in heading_data if h['size'] in {10.5, 11.0}]
other_headings   = [h for h in heading_data if h not in section_headings and h not in sub_headings]

print(f"  Section headings (12pt, Calibri bold): {len(section_headings)}")
no_border = [h for h in section_headings if not h['border']]
wrong_sb  = [h for h in section_headings if h['sb'] is not None and h['sb'] < 14]
wrong_sa  = [h for h in section_headings if h['sa'] is not None and h['sa'] > 8]
print(f"    Missing bottom border : {len(no_border)}")
print(f"    Too-small space_before: {len(wrong_sb)}")
print(f"    Too-large space_after : {len(wrong_sa)}")

print(f"  Sub-headings (10.5-11pt, Calibri bold): {len(sub_headings)}")
print(f"  Other bold Calibri (cover/captions): {len(other_headings)}")

# Check all section headings have same color
sh_colors = set(h['color'] for h in section_headings)
print(f"  Section heading colors: {sh_colors}")

# Check sub-headings colors
sh2_colors = set(h['color'] for h in sub_headings)
print(f"  Sub-heading colors    : {sh2_colors}")

# -----------------------------------------------------------------------
# 3. Table cell font coverage
# -----------------------------------------------------------------------
print("\n3. TABLE CELL FONT AUDIT")
table_issues = []
for ti, table in enumerate(doc.tables):
    nr = len(table.rows)
    nc = len(table.rows[0].cells) if table.rows else 0
    empty_runs = 0
    for ri, row in enumerate(table.rows):
        for ci, cell in enumerate(row.cells):
            for p in cell.paragraphs:
                for r in p.runs:
                    if not r.font.name or not r.font.size:
                        empty_runs += 1
    if empty_runs:
        print(f"  Table {ti} ({nr}x{nc}): {empty_runs} runs missing font/size")
        table_issues.append(ti)
    else:
        print(f"  Table {ti} ({nr}x{nc}): OK - all runs have font+size")

# -----------------------------------------------------------------------
# 4. List paragraph audit
# -----------------------------------------------------------------------
print("\n4. LIST PARAGRAPHS")
list_paras = [(i,p) for i,p in enumerate(doc.paragraphs)
              if p.style and ('Bullet' in p.style.name or 'Number' in p.style.name)]
print(f"  Total list paragraphs: {len(list_paras)}")
list_font_issues = 0
for i, p in list_paras:
    for r in p.runs:
        if not r.font.name or not r.font.size:
            list_font_issues += 1
print(f"  List runs missing font/size: {list_font_issues}")
# Sample list fonts/sizes
sample_sizes = set()
sample_fonts = set()
for i, p in list_paras:
    for r in p.runs:
        if r.font.name: sample_fonts.add(r.font.name)
        if r.font.size: sample_sizes.add(pt(r.font.size))
print(f"  List fonts : {sorted(sample_fonts)}")
print(f"  List sizes : {sorted(sample_sizes)}")

# -----------------------------------------------------------------------
# 5. Figure caption audit
# -----------------------------------------------------------------------
print("\n5. FIGURE CAPTIONS")
captions = [(i,p) for i,p in enumerate(doc.paragraphs)
            if p.text.strip().startswith('Figure') or p.text.strip().startswith('Table')]
for i, p in captions:
    sizes = sorted(set(pt(r.font.size) for r in p.runs if r.font.size))
    fonts = sorted(set(r.font.name for r in p.runs if r.font.name))
    al    = p.alignment
    sa    = pt(p.paragraph_format.space_after)
    print(f"  P{i:03d} align={al} sa={sa} fonts={fonts} sizes={sizes} | '{p.text[:55]}'")

# -----------------------------------------------------------------------
# 6. Header / Footer
# -----------------------------------------------------------------------
print("\n6. HEADER / FOOTER")
for si, sec in enumerate(doc.sections):
    for region, label in [(sec.header, 'HDR'), (sec.footer, 'FTR')]:
        for p in region.paragraphs:
            if p.text.strip():
                for r in p.runs:
                    print(f"  Sec{si} {label}: font={r.font.name} size={pt(r.font.size)} bold={r.bold} | '{p.text[:50]}'")

# -----------------------------------------------------------------------
# 7. Summary statistics
# -----------------------------------------------------------------------
print("\n7. DOCUMENT STATISTICS")
all_fonts = set()
all_sizes = set()
para_count = sum(1 for p in doc.paragraphs if p.text.strip())
for p in doc.paragraphs:
    for r in p.runs:
        if r.font.name: all_fonts.add(r.font.name)
        if r.font.size: all_sizes.add(pt(r.font.size))
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                for r in p.runs:
                    if r.font.name: all_fonts.add(r.font.name)
                    if r.font.size: all_sizes.add(pt(r.font.size))

print(f"  Non-empty paragraphs : {para_count}")
print(f"  Tables               : {len(doc.tables)}")
print(f"  Sections             : {len(doc.sections)}")
print(f"  Unique fonts         : {sorted(all_fonts)}")
print(f"  Unique sizes (pt)    : {sorted(all_sizes)}")

total_issues = len(issues) + len(table_issues)
print(f"\n  TOTAL ISSUES FOUND   : {total_issues}")
print("AUDIT COMPLETE.")
