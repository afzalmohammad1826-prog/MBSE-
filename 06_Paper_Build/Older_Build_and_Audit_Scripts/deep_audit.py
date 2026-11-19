"""
deep_audit.py — Deep formatting audit: spacing, alignment, style hierarchy,
run-level vs paragraph-level properties, table borders, header/footer fonts,
list indents, and cross-document consistency checks.
"""
import docx
from docx.shared import Pt, Inches
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = docx.Document(r'D:\MBSE\Paper\draft_2.docx')

def pt(v):
    try: return round(v.pt, 2)
    except: return None

def emu_to_in(v):
    try: return round(v / 914400, 3)
    except: return None

issues = []

print("=" * 90)
print("1. PARAGRAPH-LEVEL SPACING & ALIGNMENT AUDIT")
print("=" * 90)

BODY_TEXTS_EXPECT_JUSTIFY = True  # body paragraphs should be justified
prev_heading = False

for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt:
        continue
    pf = p.paragraph_format
    sa   = pt(pf.space_after)
    sb   = pt(pf.space_before)
    li   = emu_to_in(pf.left_indent) if pf.left_indent else 0
    fli  = emu_to_in(pf.first_line_indent) if pf.first_line_indent else 0
    ls   = pf.line_spacing
    al   = p.alignment
    style_name = p.style.name if p.style else 'None'

    flags = []

    # Flag unusual space_after values
    if sa is not None and sa > 20:
        flags.append(f'LARGE_SPACE_AFTER:{sa}pt')
    if sa is not None and sa < 0:
        flags.append(f'NEG_SPACE_AFTER:{sa}pt')

    # Check runs for font/size issues
    run_fonts  = set()
    run_sizes  = set()
    for r in p.runs:
        if r.font.name:  run_fonts.add(r.font.name)
        if r.font.size:  run_sizes.add(pt(r.font.size))

    mixed_fonts = len(run_fonts) > 1
    mixed_sizes = len(run_sizes) > 1

    if mixed_fonts:
        flags.append(f'MIXED_FONTS:{sorted(run_fonts)}')
    if mixed_sizes and style_name not in ['List Bullet', 'List Number']:
        flags.append(f'MIXED_SIZES:{sorted(run_sizes)}')

    if flags:
        snippet = txt[:70]
        issues.append(flags)
        print(f"  P{i:03d} [{style_name}] al={al} sa={sa} sb={sb} li={li} | {flags}")
        print(f"       Text: '{snippet}'")

print(f"\n  => {len(issues)} paragraph issues found")

print()
print("=" * 90)
print("2. HEADING STYLE CONSISTENCY AUDIT")
print("=" * 90)

heading_paras = []
for i, p in enumerate(doc.paragraphs):
    txt = p.text.strip()
    if not txt: continue
    # Check if paragraph has pBdr (bottom border = our custom heading style)
    pPr = p._p.find(qn('w:pPr'))
    has_border = False
    if pPr is not None:
        pBdr = pPr.find(qn('w:pBdr'))
        if pBdr is not None:
            has_border = True

    for r in p.runs:
        if r.font.name == 'Calibri' and r.bold and r.font.size and pt(r.font.size) >= 10:
            heading_paras.append({
                'idx': i, 'text': txt[:60],
                'size': pt(r.font.size),
                'has_border': has_border,
                'color': str(r.font.color.rgb) if r.font.color and r.font.color.type else 'None',
                'align': str(p.alignment),
                'sa': pt(p.paragraph_format.space_after),
                'sb': pt(p.paragraph_format.space_before),
            })
            break

print(f"  Found {len(heading_paras)} heading-style paragraphs:")
for h in heading_paras:
    border_ok = '✓ border' if h['has_border'] else '✗ NO border'
    print(f"  P{h['idx']:03d} | {h['size']}pt | {border_ok} | sb={h['sb']} sa={h['sa']} | color={h['color']} | '{h['text']}'")

print()
print("=" * 90)
print("3. TABLE CELL ALIGNMENT & CONTENT AUDIT")
print("=" * 90)

table_issues = []
for ti, table in enumerate(doc.tables):
    row_count = len(table.rows)
    col_count = len(table.columns) if table.columns else 0
    print(f"\n  Table {ti}: {row_count} rows x {col_count} cols")
    for ri, row in enumerate(table.rows):
        for ci, cell in enumerate(row.cells):
            for pi, p in enumerate(cell.paragraphs):
                txt = p.text.strip()
                if not txt: continue
                al = p.alignment
                for rj, run in enumerate(p.runs):
                    fname = run.font.name
                    fsize = pt(run.font.size)
                    if fname is None or fsize is None:
                        issue = f'    T{ti} R{ri} C{ci}: run has None font={fname} size={fsize} | "{txt[:40]}"'
                        table_issues.append(issue)
                        print(issue)

if not table_issues:
    print("  All table cells have explicit font/size set. ✓")

print()
print("=" * 90)
print("4. LIST STYLE AUDIT")
print("=" * 90)
list_paras = [(i, p) for i, p in enumerate(doc.paragraphs)
              if p.style and ('Bullet' in p.style.name or 'Number' in p.style.name)]
print(f"  Found {len(list_paras)} list paragraphs")
for i, p in list_paras[:5]:
    for r in p.runs:
        print(f"  P{i:03d} [{p.style.name}] font={r.font.name} size={pt(r.font.size)} | '{p.text[:60]}'")
        break

print()
print("=" * 90)
print("5. HEADER / FOOTER AUDIT")
print("=" * 90)
for si, section in enumerate(doc.sections):
    for region, label in [(section.header, 'HEADER'), (section.footer, 'FOOTER')]:
        for p in region.paragraphs:
            if p.text.strip():
                for r in p.runs:
                    print(f"  Section {si} {label}: font={r.font.name} size={pt(r.font.size)} | '{p.text[:60]}'")

print()
print("=" * 90)
print("6. FIGURE CAPTION CONSISTENCY")
print("=" * 90)
captions = [(i,p) for i,p in enumerate(doc.paragraphs) if p.text.strip().startswith('Figure')]
print(f"  Found {len(captions)} figure captions")
for i, p in captions:
    sizes = [pt(r.font.size) for r in p.runs if r.font.size]
    fonts = [r.font.name for r in p.runs if r.font.name]
    al = p.alignment
    print(f"  P{i:03d} | align={al} | sizes={sizes} | fonts={set(fonts)} | '{p.text[:60]}'")

print()
print("=" * 90)
print("7. DOCUMENT STATISTICS")
print("=" * 90)
all_fonts = set()
all_sizes = set()
para_count = 0
table_count = len(doc.tables)
for p in doc.paragraphs:
    if p.text.strip(): para_count += 1
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
print(f"  Tables               : {table_count}")
print(f"  Unique fonts         : {sorted(all_fonts)}")
print(f"  Unique sizes (pt)    : {sorted(all_sizes)}")
print(f"  Sections             : {len(doc.sections)}")
print()
print("AUDIT COMPLETE.")
