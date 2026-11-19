# -*- coding: utf-8 -*-
"""Records the manuscript content as a neutral list so Word and LaTeX can both be rendered from it."""
import os
import sys

import part_a, part_b, part_c, part_d

ELEMS = []


def _heading(doc, num, title):
    ELEMS.append(('h', num, title))


def _subheading(doc, title, level=2):
    num, _, rest = title.partition('  ')
    ELEMS.append(('sh', num.strip(), rest.strip()))


def _body(doc, text, space_after=6):
    ELEMS.append(('p', text))


def _bullet(doc, prefix, text):
    ELEMS.append(('b', prefix, text))


def _figure(doc, filename, n, caption, width_in=5.8):
    if filename == 'FIG2_COMPOSITE':
        filename = 'sysml_composite.png'
    for d in ('D:/MBSE/Paper/figs2', 'D:/MBSE/Paper/figures'):
        p = os.path.join(d, filename)
        if os.path.exists(p):
            ELEMS.append(('fig', p, n, caption, width_in))
            return
    raise FileNotFoundError(filename)


def _table(doc, num, caption, header, rows, widths=None, note=None, font=9.0, align_first_left=True):
    ELEMS.append(('tbl', num, caption, header, rows, widths, note))


def _equation(doc, text, num):
    ELEMS.append(('eq', text, num))


def _refs(doc):
    ELEMS.append(('refs', part_c.all_refs()))


def record():
    ELEMS.clear()
    for m in (part_a, part_b, part_c, part_d):
        m.add_wiley_heading = _heading
        m.add_wiley_subheading = _subheading
        m.add_body_p = _body
        m.add_bullet_p = _bullet
        m.add_wiley_figure = _figure
        m.table = _table
        m.equation = _equation
    part_c.build_refs = _refs
    part_a.build_intro(None)
    part_a.build_background(None)
    part_a.build_framework(None)
    part_a.build_requirements(None)
    part_b.build_methods(None)
    part_d.build_graded(None)
    part_c.build_trace(None)
    part_d.build_discussion(None)
    part_d.build_conclusions(None)
    _refs(None)
    return list(ELEMS)


if __name__ == '__main__':
    e = record()
    from collections import Counter
    print(Counter(x[0] for x in e))
