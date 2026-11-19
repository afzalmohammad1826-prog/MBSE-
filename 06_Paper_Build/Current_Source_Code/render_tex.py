# -*- coding: utf-8 -*-
"""Render the recorded manuscript as a two-column journal-style LaTeX document (XeLaTeX/LuaLaTeX)."""
import os
import re
import shutil

import part_a

GREEK = {'ν': r'\nu', 'σ': r'\sigma', 'τ': r'\tau', 'φ': r'\varphi', 'θ': r'\theta', 'π': r'\pi',
         'Σ': r'\Sigma', 'ℓ': r'\ell', 'ε': r'\varepsilon', 'α': r'\alpha', 'β': r'\beta', 'µ': r'\mu'}
SUPER = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
SYM = {'≥': r'$\geq$', '≤': r'$\leq$', '×': r'$\times$', '±': r'$\pm$', '−': r'$-$', '·': r'$\cdot$',
       '≈': r'$\approx$', '°': r'\textdegree{}', '–': '--', '—': '---', '’': "'", '‘': '`', '“': '``', '”': "''",
       'ᵢ': r'$_{i}$', ' ': r'\enspace{}', ' ': '~', '→': r'$\rightarrow$'}
ESC = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{',
       '}': r'\}', '~': r'\textasciitilde{}', '^': r'\textasciicircum{}'}
SUBRE = re.compile(r'(?<![A-Za-z0-9_])([A-Za-zνστφθπΣℓεαβ])_([A-Za-z0-9]+)')
UNMAPPED = set()


def _g(ch):
    return GREEK.get(ch, ch)


def tex(text):
    text = re.sub(r'"([^"]*)"', lambda m: '``' + m.group(1) + "''", text)
    out = []
    pos = 0
    for m in SUBRE.finditer(text):
        out.append(_plain(text[pos:m.start()]))
        sub = m.group(2)
        subtex = sub if len(sub) == 1 and sub.isalpha() else r'\mathrm{' + sub + '}'
        if len(sub) == 1 and sub.isalpha():
            subtex = sub
        out.append('$' + _g(m.group(1)) + '_{' + subtex + '}$')
        pos = m.end()
    out.append(_plain(text[pos:]))
    return ''.join(out)


def _plain(s):
    s = re.sub(r'⁻([⁰¹²³⁴⁵⁶⁷⁸⁹])', lambda m: r'\textsuperscript{$-$' + SUPER[m.group(1)] + '}', s)
    res = []
    for ch in s:
        if ch in SUPER:
            res.append(r'\textsuperscript{' + SUPER[ch] + '}')
        elif ch in GREEK:
            res.append('$' + GREEK[ch] + '$')
        elif ch in SYM:
            res.append(SYM[ch])
        elif ch in ESC:
            res.append(ESC[ch])
        elif ord(ch) > 127:
            UNMAPPED.add(ch)
            res.append(ch)
        else:
            res.append(ch)
    return ''.join(res)


EQ = {
    1: r'\varphi(t) = 1 - \frac{A_s(t)}{W\,H}',
    2: r't(y) = t_c + (t_d - t_c)\,s(y)',
    3: r'\nu_{\mathrm{eff}} = -\,\frac{\varepsilon_{\mathrm{transverse}}}{\varepsilon_{\mathrm{axial}}}',
    4: r'K = \frac{F_y}{U_y}',
}

PREAMBLE = r'''% Compile with XeLaTeX or LuaLaTeX (Overleaf: Menu > Compiler > XeLaTeX).
\documentclass[10pt,twocolumn,letterpaper]{article}
\usepackage[top=0.95in,bottom=0.9in,left=0.8in,right=0.8in,columnsep=0.28in,headheight=14pt,footskip=24pt]{geometry}
\usepackage{fontspec}
\setmainfont{TeX Gyre Pagella}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs,array}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{lastpage}
\renewcommand{\topfraction}{0.92}
\renewcommand{\dbltopfraction}{0.92}
\renewcommand{\textfraction}{0.08}
\renewcommand{\floatpagefraction}{0.7}
\renewcommand{\dblfloatpagefraction}{0.7}
\setcounter{topnumber}{3}
\setcounter{dbltopnumber}{3}
\setcounter{totalnumber}{5}
\usepackage{caption}
\usepackage{enumitem}
\usepackage{url}
\usepackage{microtype}
\usepackage[hidelinks]{hyperref}
\urlstyle{same}
\sloppy
\setlength{\parindent}{0pt}
\setlength{\parskip}{3.5pt}
\renewcommand{\baselinestretch}{1.05}

% headings: "1 | Introduction" as in the Wiley journal layout
\titleformat{\section}{\bfseries\fontsize{11}{13}\selectfont}{\thesection\hspace{0.45em}|\hspace{0.45em}}{0pt}{}
\titleformat{\subsection}{\bfseries\fontsize{9.5}{11.5}\selectfont}{\thesubsection\hspace{0.45em}|\hspace{0.45em}}{0pt}{}
\titlespacing*{\section}{0pt}{10pt}{4pt}
\titlespacing*{\subsection}{0pt}{6pt}{3pt}

% captions: "FIGURE 1 | text"
\renewcommand{\figurename}{FIGURE}
\renewcommand{\tablename}{TABLE}
\DeclareCaptionLabelSeparator{bar}{\hspace{0.4em}|\hspace{0.4em}}
\captionsetup{font=footnotesize,labelfont=bf,labelsep=bar,justification=raggedright,singlelinecheck=false,skip=4pt}

% header and footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\colorbox{black!12}{\textit{\textbf{\small\ Systems Engineering\ }}}}
\fancyfoot[L]{\footnotesize\itshape MBSE framework for auxetic bone screws}
\fancyfoot[R]{\footnotesize\thepage\ of \pageref{LastPage}}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancypagestyle{plain}{\fancyhf{}\fancyfoot[L]{\footnotesize\itshape MBSE framework for auxetic bone screws}\fancyfoot[R]{\footnotesize\thepage\ of \pageref{LastPage}}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0.4pt}}

\setlist[itemize]{leftmargin=1.1em,itemsep=1.5pt,topsep=2pt,parsep=0pt}
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.12}

\begin{document}
'''


def front(title, authors, abstract, keywords):
    parts = [
        r'\twocolumn[{%',
        r'\vspace*{-4pt}',
        r'{\noindent\rule[-2pt]{2.5pt}{11pt}\hspace{5pt}{\small\bfseries RESEARCH ARTICLE}\par}',
        r'\vspace{8pt}',
        r'{\raggedright\fontsize{21}{25}\selectfont\bfseries ' + tex(title) + r'\par}',
        r'\vspace{8pt}',
        r'{\raggedright\textbf{' + tex(authors[0]) + r'}\\{\small\color{black!65} ' + tex(authors[1]) + r'}\par}',
        r'\vspace{8pt}',
        r'\noindent\colorbox{black!8}{\parbox{\dimexpr\textwidth-2\fboxsep}{\small\textbf{ABSTRACT}\\[2pt]' + tex(abstract) + r'}}\par',
        r'\vspace{6pt}',
        r'{\small\textbf{Keywords:} ' + tex(keywords) + r'\par}',
        r'\vspace{6pt}',
        r'}]',
    ]
    return '\n'.join(parts) + '\n'


def colspec(header, rows, widths, full):
    n = len(header)
    ws = widths if widths else [1.0] * n
    s = float(sum(ws))
    spec = []
    for ci in range(n):
        frac = ws[ci] / s
        wexpr = r'\dimexpr(\linewidth-%d\tabcolsep)*%d/1000\relax' % (2 * n, round(frac * 1000))
        longest = max(len(str(r[ci])) for r in rows)
        al = r'\raggedright\arraybackslash' if (ci == 0 or longest > 26) else r'\centering\arraybackslash'
        spec.append(r'>{' + al + r'}p{' + wexpr + '}')
    return ''.join(spec)


def render(elems, outdir):
    os.makedirs(os.path.join(outdir, 'figures'), exist_ok=True)
    L = [PREAMBLE]
    L.append(front(part_a.TITLE, ['G Mohammad Afzal', 'Roll No. ME23B2014'], part_a.ABSTRACT, part_a.KEYWORDS))
    i = 0
    while i < len(elems):
        e = elems[i]
        k = e[0]
        if k == 'h':
            L.append('\n' + r'\section{' + tex(e[2]) + '}')
        elif k == 'sh':
            L.append(r'\subsection{' + tex(e[2]) + '}')
        elif k == 'p':
            L.append(tex(e[1]) + '\n')
        elif k == 'b':
            L.append(r'\begin{itemize}')
            while i < len(elems) and elems[i][0] == 'b':
                pre, txt = elems[i][1], elems[i][2]
                if pre.startswith('('):
                    L.append(r'\item[\textbf{' + tex(pre) + r'}] ' + tex(txt))
                else:
                    L.append(r'\item ' + (r'\textbf{' + tex(pre) + r'} ' if pre else '') + tex(txt))
                i += 1
            L.append(r'\end{itemize}')
            i -= 1
        elif k == 'eq':
            L.append(r'\begin{equation}' + EQ[e[2]] + r'\end{equation}')
        elif k == 'fig':
            path, num, cap, w = e[1], e[2], e[3], e[4]
            fn = os.path.basename(path)
            shutil.copy(path, os.path.join(outdir, 'figures', fn))
            full = w > 4.6
            env = 'figure*' if full else 'figure'
            width = r'\textwidth' if full else r'\columnwidth'
            L.append(r'\begin{%s}[!t]' % env)
            L.append(r'\centering\includegraphics[width=%s]{figures/%s}' % (width, fn))
            L.append(r'\caption{' + tex(cap) + '}')
            L.append(r'\end{%s}' % env)
        elif k == 'tbl':
            num, cap, header, rows, widths, note = e[1:7]
            full = len(header) >= 5
            env = 'table*' if full else 'table'
            L.append(r'\begin{%s}[!t]' % env)
            L.append(r'\caption{' + tex(cap) + '}')
            L.append(r'\centering\fontsize{8}{9.6}\selectfont')
            L.append(r'\begin{tabular}{' + colspec(header, rows, widths, full) + '}')
            L.append(r'\toprule')
            L.append(' & '.join(r'\textbf{' + tex(h) + '}' for h in header) + r' \\')
            L.append(r'\midrule')
            for r in rows:
                cells = [(r'\textbf{' + tex(str(r[0])) + '}')] + [tex(str(c)) for c in r[1:]]
                L.append(' & '.join(cells) + r' \\')
            L.append(r'\bottomrule')
            L.append(r'\end{tabular}')
            if note:
                L.append(r'\par\vspace{3pt}{\raggedright\fontsize{7.5}{9}\selectfont\itshape ' + tex(note) + '\\par}')
            L.append(r'\end{%s}' % env)
        elif k == 'refs':
            L.append(r'\begingroup\footnotesize\setlength{\parskip}{1.5pt}')
            L.append(r'\begin{thebibliography}{99}')
            L.append(r'\setlength{\itemsep}{1.5pt}')
            for r in e[1]:
                num, _, txt = r.partition('\t')
                n = num.strip('[]')
                txt = txt.strip()
                parts = re.split(r'(https?://\S+)', txt)
                body = ''
                for pt in parts:
                    if pt.startswith('http'):
                        body += r'\url{' + pt.rstrip('.') + '}' + ('.' if pt.endswith('.') else '')
                    else:
                        body += tex(pt)
                L.append(r'\bibitem{r%s} %s' % (n, body))
            L.append(r'\end{thebibliography}')
            L.append(r'\endgroup')
        i += 1
    L.append('\n' + r'\end{document}' + '\n')
    src = '\n'.join(L)
    with open(os.path.join(outdir, 'final_draft_1.tex'), 'w', encoding='utf-8') as f:
        f.write(src)
    with open(os.path.join(outdir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write('final_draft_1.tex  (two-column, journal-style layout)\n'
                'Compile with XeLaTeX or LuaLaTeX (not pdfLaTeX). Run twice so the "page x of y" footer resolves.\n'
                'Overleaf: upload this whole folder, then Menu > Compiler > XeLaTeX.\n'
                'Font: TeX Gyre Pagella (included in TeX Live and on Overleaf).\n')
    if UNMAPPED:
        print('UNMAPPED unicode:', UNMAPPED)
    return src
