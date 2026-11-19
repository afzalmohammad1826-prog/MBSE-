# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import rec
from paths import OUT
import render_word

elems = rec.record()
os.makedirs(OUT, exist_ok=True)
render_word.render(elems, os.path.join(OUT, 'final_draft_1.docx'))
print('word ok')
if len(sys.argv) > 1 and sys.argv[1] == 'tex':
    import render_tex
    render_tex.render(elems, os.path.join(OUT, 'final_draft_1_latex'))
    print('tex ok')
