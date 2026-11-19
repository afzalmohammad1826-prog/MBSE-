# -*- coding: utf-8 -*-
"""Render recorded content as a two-column journal-style Word document (layout follows Wiley NJD)."""
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

import part_a

FONT = 'Cambria'
BODY = 9.5
PAGE_W, MARG, GAP = 8.5, 0.8, 0.28
COL_W = (PAGE_W - 2 * MARG - GAP) / 2.0
FULL_W = PAGE_W - 2 * MARG
INK = RGBColor(0x1A, 0x1A, 0x1A)
GREY = RGBColor(0x55, 0x55, 0x55)
ACCENT = RGBColor(0x1B, 0x36, 0x5D)


def set_cols(section, n):
    sectPr = section._sectPr
    for c in sectPr.findall(qn('w:cols')):
        sectPr.remove(c)
    cols = OxmlElement('w:cols')
    cols.set(qn('w:num'), str(n))
    cols.set(qn('w:space'), str(int(GAP * 1440)))
    sectPr.append(cols)


def font(run, size=BODY, bold=False, italic=False, color=INK, name=FONT):
    run.font.name = name
    run._element.rPr.rFonts.set(qn('w:eastAsia'), name)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def shade(par_or_cell, fill):
    if hasattr(par_or_cell, '_tc'):
        pr = par_or_cell._tc.get_or_add_tcPr()
    else:
        pr = par_or_cell._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    pr.append(shd)


def border(par, side, sz=8, color='1A1A1A', space=1):
    pPr = par._p.get_or_add_pPr()
    b = pPr.find(qn('w:pBdr'))
    if b is None:
        b = OxmlElement('w:pBdr')
        pPr.append(b)
    e = OxmlElement('w:' + side)
    e.set(qn('w:val'), 'single')
    e.set(qn('w:sz'), str(sz))
    e.set(qn('w:space'), str(space))
    e.set(qn('w:color'), color)
    b.append(e)


def fmt(par, before=0, after=4, line=1.08, align=WD_ALIGN_PARAGRAPH.JUSTIFY, keep_next=False):
    pf = par.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    par.alignment = align
    pf.keep_with_next = keep_next


def add_field(par, instr, size=8):
    r = par.add_run()
    font(r, size, color=GREY)
    for kind in ('begin', None, 'end'):
        if kind:
            el = OxmlElement('w:fldChar')
            el.set(qn('w:fldCharType'), kind)
        else:
            el = OxmlElement('w:instrText')
            el.set(qn('xml:space'), 'preserve')
            el.text = instr
        r._r.append(el)



SUB = re.compile(r'(?<![A-Za-z0-9_])([A-Za-zνστφθπΣℓεαβ])_([A-Za-z0-9]+)')


def rich(par, text, size=BODY, bold=False, italic=False, color=INK, name=FONT):
    pos = 0
    for m in SUB.finditer(text):
        if m.start() > pos:
            r = par.add_run(text[pos:m.start()])
            font(r, size, bold, italic, color, name)
        r = par.add_run(m.group(1))
        font(r, size, bold, italic, color, name)
        r = par.add_run(m.group(2))
        font(r, size, bold, italic, color, name)
        r.font.subscript = True
        pos = m.end()
    if pos < len(text):
        r = par.add_run(text[pos:])
        font(r, size, bold, italic, color, name)


class Writer:
    def __init__(self, title, authors, abstract, keywords):
        self.doc = Document()
        st = self.doc.styles['Normal']
        st.font.name = FONT
        st.font.size = Pt(BODY)
        sec = self.doc.sections[0]
        sec.page_width, sec.page_height = Inches(8.5), Inches(11)
        sec.left_margin = sec.right_margin = Inches(MARG)
        sec.top_margin, sec.bottom_margin = Inches(0.95), Inches(0.9)
        sec.header_distance, sec.footer_distance = Inches(0.45), Inches(0.4)
        self.header_footer(sec)
        self.front(title, authors, abstract, keywords)
        s2 = self.doc.add_section(WD_SECTION.CONTINUOUS)
        set_cols(s2, 2)
        self.cols = 2

    def header_footer(self, sec):
        hp = sec.header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = hp.add_run(' Systems Engineering ')
        font(r, 9, bold=True, italic=True, color=GREY)
        shade(hp, 'E6E6E6')
        fp = sec.footer.paragraphs[0]
        fp.style = self.doc.styles['Normal']
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        border(fp, 'top', 4, '7A7A7A', 4)
        pf = fp.paragraph_format
        pf.tab_stops.add_tab_stop(Inches(FULL_W), WD_TAB_ALIGNMENT.RIGHT)
        r = fp.add_run('MBSE framework for auxetic bone screws')
        font(r, 8, italic=True, color=GREY)
        r = fp.add_run('\t')
        font(r, 8)
        add_field(fp, 'PAGE')
        r = fp.add_run(' of ')
        font(r, 8, color=GREY)
        add_field(fp, 'NUMPAGES')

    def front(self, title, authors, abstract, keywords):
        d = self.doc
        p = d.add_paragraph()
        fmt(p, 6, 8, align=WD_ALIGN_PARAGRAPH.LEFT)
        border(p, 'left', 24, '1A1A1A', 6)
        r = p.add_run('RESEARCH ARTICLE')
        font(r, 9, bold=True)
        p = d.add_paragraph()
        fmt(p, 6, 8, 1.0, WD_ALIGN_PARAGRAPH.LEFT)
        r = p.add_run(title)
        font(r, 20, bold=True)
        p = d.add_paragraph()
        fmt(p, 0, 10, 1.1, WD_ALIGN_PARAGRAPH.LEFT)
        for i, line in enumerate(authors):
            r = p.add_run(line + ('\n' if i < len(authors) - 1 else ''))
            font(r, 10.5 if i == 0 else 9.5, bold=(i == 0), color=INK if i == 0 else GREY)
        p = d.add_paragraph()
        fmt(p, 4, 0, 1.12, WD_ALIGN_PARAGRAPH.JUSTIFY)
        shade(p, 'E9E9E9')
        p.paragraph_format.left_indent = Inches(0.08)
        p.paragraph_format.right_indent = Inches(0.08)
        r = p.add_run('ABSTRACT')
        font(r, 9.5, bold=True)
        p = d.add_paragraph()
        fmt(p, 0, 8, 1.12, WD_ALIGN_PARAGRAPH.JUSTIFY)
        shade(p, 'E9E9E9')
        p.paragraph_format.left_indent = Inches(0.08)
        p.paragraph_format.right_indent = Inches(0.08)
        r = p.add_run(abstract)
        font(r, 9.5)
        p = d.add_paragraph()
        fmt(p, 0, 10, 1.1, WD_ALIGN_PARAGRAPH.LEFT)
        r = p.add_run('Keywords: ')
        font(r, 9, bold=True)
        r = p.add_run(keywords)
        font(r, 9)

    # ---------- flow control ----------
    def fullwidth(self, fn):
        s = self.doc.add_section(WD_SECTION.CONTINUOUS)
        set_cols(s, 1)
        fn()
        s = self.doc.add_section(WD_SECTION.CONTINUOUS)
        set_cols(s, 2)

    # ---------- elements ----------
    def heading(self, num, title):
        p = self.doc.add_paragraph()
        fmt(p, 10, 4, 1.0, WD_ALIGN_PARAGRAPH.LEFT, True)
        text = f'{num}  |  {title}' if num else title
        r = p.add_run(text)
        font(r, 11, bold=True)

    def subheading(self, num, title):
        p = self.doc.add_paragraph()
        fmt(p, 6, 3, 1.0, WD_ALIGN_PARAGRAPH.LEFT, True)
        r = p.add_run(f'{num}  |  {title}')
        font(r, 9.5, bold=True)

    def para(self, text):
        p = self.doc.add_paragraph()
        fmt(p, 0, 4.5)
        rich(p, text)

    def bullet(self, prefix, text):
        p = self.doc.add_paragraph()
        fmt(p, 0, 3)
        p.paragraph_format.left_indent = Inches(0.2)
        p.paragraph_format.first_line_indent = Inches(-0.2)
        if not prefix.startswith('('):
            r = p.add_run('• ')
            font(r)
        else:
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.first_line_indent = Inches(-0.3)
        if prefix:
            r = p.add_run(prefix + ' ')
            font(r, bold=True)
        rich(p, text)

    def equation(self, text, num):
        p = self.doc.add_paragraph()
        fmt(p, 2, 5, 1.0, WD_ALIGN_PARAGRAPH.LEFT)
        w = COL_W if self.cols == 2 else FULL_W
        p.paragraph_format.tab_stops.add_tab_stop(Inches(w / 2.0), WD_TAB_ALIGNMENT.CENTER)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(w), WD_TAB_ALIGNMENT.RIGHT)
        rich(p, '\t' + text + '\t(' + str(num) + ')', 10, name='Cambria Math')

    def caption(self, label, num, text, before=2, after=8, keep_next=False):
        p = self.doc.add_paragraph()
        fmt(p, before, after, 1.05, WD_ALIGN_PARAGRAPH.LEFT, keep_next)
        r = p.add_run(f'{label} {num}  |  ')
        font(r, 8.5, bold=True)
        rich(p, text, 8.5)

    def figure(self, path, num, caption, width_in):
        full = width_in > 4.6

        def put():
            p = self.doc.add_paragraph()
            fmt(p, 6, 3, 1.0, WD_ALIGN_PARAGRAPH.CENTER, True)
            w = FULL_W if full else COL_W
            if full:
                w = min(FULL_W, width_in * 1.08)
            else:
                w = min(COL_W, max(width_in, 2.6))
            p.add_run().add_picture(path, width=Inches(w))
            self.caption('FIGURE', num, caption)
        if full:
            self.fullwidth(put)
        else:
            put()

    def table(self, num, caption, header, rows, widths, note):
        full = len(header) >= 5
        total = FULL_W if full else COL_W

        def put():
            self.caption('TABLE', num, caption, 6, 3, True)
            t = self.doc.add_table(rows=1 + len(rows), cols=len(header))
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.autofit = False
            ws = widths if widths else [1.0] * len(header)
            s = sum(ws)
            ws = [x / s * total for x in ws]
            tblPr = t._tbl.tblPr
            for e in tblPr.findall(qn('w:tblBorders')):
                tblPr.remove(e)
            fs = 8 if full or len(header) <= 4 else 7.5
            for ri in range(len(rows) + 1):
                for ci in range(len(header)):
                    c = t.cell(ri, ci)
                    c.width = Inches(ws[ci])
                    tcPr = c._tc.get_or_add_tcPr()
                    mar = OxmlElement('w:tcMar')
                    for side, v in (('top', 25), ('bottom', 25), ('left', 55), ('right', 55)):
                        e = OxmlElement('w:' + side)
                        e.set(qn('w:w'), str(v))
                        e.set(qn('w:type'), 'dxa')
                        mar.append(e)
                    tcPr.append(mar)
                    bd = OxmlElement('w:tcBorders')
                    edges = []
                    if ri == 0:
                        edges = [('top', 10), ('bottom', 6)]
                    if ri == len(rows):
                        edges = [('bottom', 10)]
                    for side, sz in edges:
                        e = OxmlElement('w:' + side)
                        e.set(qn('w:val'), 'single')
                        e.set(qn('w:sz'), str(sz))
                        e.set(qn('w:color'), '1A1A1A')
                        bd.append(e)
                    tcPr.append(bd)
                    val = header[ci] if ri == 0 else rows[ri - 1][ci]
                    p = c.paragraphs[0]
                    fmt(p, 0, 0, 1.0, WD_ALIGN_PARAGRAPH.LEFT if (ci == 0 or len(str(val)) > 26) else WD_ALIGN_PARAGRAPH.CENTER)
                    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    rich(p, str(val), fs, bold=(ri == 0))
                    if ri < len(rows):
                        p.paragraph_format.keep_with_next = True
            if note:
                p = self.doc.add_paragraph()
                fmt(p, 3, 8, 1.0, WD_ALIGN_PARAGRAPH.JUSTIFY)
                rich(p, note, 7.5, italic=True, color=GREY)
            else:
                p = self.doc.add_paragraph()
                fmt(p, 0, 4, 1.0)
        if full:
            self.fullwidth(put)
        else:
            put()

    def refs(self, items):
        self.heading('', 'References')
        for r_ in items:
            num, _, text = r_.partition('\t')
            p = self.doc.add_paragraph()
            fmt(p, 0, 2, 1.0, WD_ALIGN_PARAGRAPH.LEFT)
            p.paragraph_format.left_indent = Inches(0.28)
            p.paragraph_format.first_line_indent = Inches(-0.28)
            r = p.add_run(num + ' ' + text)
            font(r, 7.5)


def render(elems, out):
    w = Writer(part_a.TITLE, ['G Mohammad Afzal', 'Roll No. ME23B2014'], part_a.ABSTRACT, part_a.KEYWORDS)
    for e in elems:
        k = e[0]
        if k == 'h':
            w.heading(e[1], e[2])
        elif k == 'sh':
            w.subheading(e[1], e[2])
        elif k == 'p':
            w.para(e[1])
        elif k == 'b':
            w.bullet(e[1], e[2])
        elif k == 'eq':
            w.equation(e[1], e[2])
        elif k == 'fig':
            w.figure(e[1], e[2], e[3], e[4])
        elif k == 'tbl':
            w.table(e[1], e[2], e[3], e[4], e[5], e[6])
        elif k == 'refs':
            w.refs(e[1])
    w.doc.save(out)
