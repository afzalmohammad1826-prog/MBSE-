# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import rec
import render_word

elems = rec.record()
render_word.render(elems, 'D:/MBSE/Paper/final_draft_1.docx')
print('word ok')
if len(sys.argv) > 1 and sys.argv[1] == 'tex':
    import render_tex
    render_tex.render(elems, 'D:/MBSE/Paper/final_draft_1_latex')
    print('tex ok')
