import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_header_footer(doc):
    for s in doc.sections:
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("IEEE Systems Journal / Systems Engineering - Research Article Draft")
        hrun.font.name = "Times New Roman"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
        
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Model-Based Systems Engineering Framework for Auxetic Metamaterial Implants")
        frun.font.name = "Times New Roman"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

def format_inlines(paragraph, text):
    parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**') and len(part) >= 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
        elif part.startswith('*') and part.endswith('*') and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
        elif part.startswith('`') and part.endswith('`') and len(part) >= 2:
            run = paragraph.add_run(part[1:-1])
            run.font.name = 'Consolas'
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0x99, 0x00, 0x00)
        else:
            paragraph.add_run(part)

def build_paper():
    md_path = r'D:\MBSE\Paper\Paper.md'
    docx_path = r'D:\MBSE\Paper\Paper.docx'
    
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = [l.rstrip() for l in f]
        
    doc = docx.Document()
    
    # Page setup
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)
    
    add_header_footer(doc)
    
    i = 0
    in_table = False
    table_lines = []
    
    while i < len(lines):
        line = lines[i]
        
        # Check for start of table
        if '|' in line and i + 1 < len(lines) and '|---' in lines[i+1]:
            table_lines = [line]
            i += 1
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i])
                i += 1
            
            # Process table
            headers = [c.strip() for c in table_lines[0].split('|')[1:-1]]
            rows_data = []
            for r_line in table_lines[2:]:
                if '|' in r_line:
                    row_cells = [c.strip() for c in r_line.split('|')[1:-1]]
                    if any(row_cells):
                        rows_data.append(row_cells)
            
            table = doc.add_table(rows=len(rows_data) + 1, cols=len(headers))
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            table.autofit = True
            
            # Format header
            hdr_cells = table.rows[0].cells
            for idx, h_text in enumerate(headers):
                hdr_cells[idx].text = ""
                p = hdr_cells[idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(h_text.replace('**', ''))
                run.bold = True
                run.font.name = 'Times New Roman'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                set_cell_background(hdr_cells[idx], '1B365D') # Deep Navy
                set_cell_margins(hdr_cells[idx], top=120, bottom=120, left=120, right=120)
                hdr_cells[idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            # Format body rows
            for r_idx, r_vals in enumerate(rows_data):
                row_cells = table.rows[r_idx + 1].cells
                bg_col = 'F9FAFB' if r_idx % 2 == 1 else 'FFFFFF'
                for c_idx, val in enumerate(r_vals):
                    if c_idx < len(row_cells):
                        cell = row_cells[c_idx]
                        cell.text = ""
                        p = cell.paragraphs[0]
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
                        val_clean = val.replace('<br>', '\n').replace('$', '')
                        for sub_idx, sub_val in enumerate(val_clean.split('\n')):
                            if sub_idx > 0:
                                p = cell.add_paragraph()
                                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
                            format_inlines(p, sub_val)
                            for r in p.runs:
                                r.font.name = 'Times New Roman'
                                r.font.size = Pt(9.0)
                        set_cell_background(cell, bg_col)
                        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
                        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            
            # Add small spacer after table
            sp = doc.add_paragraph()
            sp.paragraph_format.space_after = Pt(6)
            continue
            
        # Title
        if line.startswith('# '):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(12)
            run = p.add_run(line[2:])
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(18)
            run.font.color.rgb = RGBColor(0x11, 0x11, 0x11)
            
            # Add Authors and Affiliations
            ap = doc.add_paragraph()
            ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ap.paragraph_format.space_after = Pt(2)
            arun = ap.add_run("Systems Engineering & Biomechanical Design Research Group")
            arun.bold = True
            arun.font.size = Pt(11)
            
            affp = doc.add_paragraph()
            affp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            affp.paragraph_format.space_after = Pt(18)
            affrun = affp.add_run("Department of Mechanical and Biomedical Engineering\nTarget Publication: IEEE Systems Journal / INCOSE Systems Engineering\nModel-Based Systems Engineering (MBSE) Digital Thread Project")
            affrun.italic = True
            affrun.font.size = Pt(9.5)
            affrun.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
            
            i += 1
            continue

        # Target Journal line
        if line.startswith('**Target Journal:**'):
            i += 1
            continue
            
        # Horizontal rule
        if line.strip() in ['---', '***']:
            i += 1
            continue
            
        # Heading 1
        if line.startswith('## '):
            h_text = line[3:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(13)
            run.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D) # Navy
            i += 1
            continue
            
        # Heading 2
        if line.startswith('### '):
            h_text = line[4:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(h_text)
            run.bold = True
            run.font.name = 'Times New Roman'
            run.font.size = Pt(11.5)
            run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
            i += 1
            continue

        # Images: ![alt](path)
        img_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
        if img_match:
            alt_text, img_rel_path = img_match.groups()
            full_img_path = os.path.join(r'D:\MBSE\Paper', img_rel_path.replace('/', '\\'))
            if os.path.exists(full_img_path):
                ip = doc.add_paragraph()
                ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
                ip.paragraph_format.space_before = Pt(10)
                ip.paragraph_format.space_after = Pt(4)
                ip.paragraph_format.keep_with_next = True
                run = ip.add_run()
                run.add_picture(full_img_path, width=Inches(5.8))
            i += 1
            continue
            
        # Captions: *Figure X: ...*
        if line.startswith('*Figure ') or line.startswith('*Fig. '):
            cp = doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_after = Pt(12)
            caption_text = line.strip('*')
            format_inlines(cp, caption_text)
            for r in cp.runs:
                r.italic = True
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            i += 1
            continue
            
        # Table label: $$\text{Table ...}$$
        if line.startswith('$$\\text{Table') or line.startswith('$$\\text{Table'):
            tbl_title = re.search(r'\\text\{(.*?)\}', line)
            title_text = tbl_title.group(1) if tbl_title else line.replace('$$', '')
            tp = doc.add_paragraph()
            tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            tp.paragraph_format.space_before = Pt(14)
            tp.paragraph_format.space_after = Pt(4)
            tp.paragraph_format.keep_with_next = True
            trun = tp.add_run(title_text)
            trun.bold = True
            trun.font.name = 'Times New Roman'
            trun.font.size = Pt(10.5)
            trun.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
            i += 1
            continue
            
        # Bullet list items
        if line.startswith('* ') or line.startswith('- '):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            format_inlines(p, line[2:].strip())
            i += 1
            continue
            
        # Numbered list items
        num_match = re.match(r'^(\d+)\.\s+(.*)', line)
        if num_match:
            num, rest = num_match.groups()
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.15
            format_inlines(p, rest.strip())
            i += 1
            continue
            
        # Display Math: $$ ... $$
        if line.startswith('$$') and line.endswith('$$') and len(line) > 4:
            mp = doc.add_paragraph()
            mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            mp.paragraph_format.space_before = Pt(6)
            mp.paragraph_format.space_after = Pt(6)
            eq_text = line[2:-2].strip().replace('\\text', '').replace('{', '').replace('}', '').replace('\\quad', '  ').replace('\\rightarrow', ' -> ')
            mrun = mp.add_run(eq_text)
            mrun.font.name = 'Cambria Math'
            mrun.font.size = Pt(10.5)
            mrun.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)
            i += 1
            continue

        # Standard Paragraph
        if line.strip():
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            if line.startswith('**Keywords:**'):
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(14)
            format_inlines(p, line)
            
        i += 1
        
    doc.save(docx_path)
    print(f"Successfully compiled {docx_path} ({os.path.getsize(docx_path)} bytes)")

if __name__ == '__main__':
    build_paper()
