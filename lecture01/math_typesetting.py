"""Typeset equations with LaTeX once, then place their cropped vector PDF pages."""
from pathlib import Path
import tempfile,subprocess
import fitz

def compile_equations(expressions):
    expressions=list(dict.fromkeys(expressions))
    cache=tempfile.TemporaryDirectory(prefix='classical-cipher-math-')
    root=Path(cache.name)
    pre=r'''\documentclass{article}
\usepackage[paperwidth=16in,paperheight=4in,margin=12pt]{geometry}
\usepackage{amsmath,amssymb,lmodern,xcolor}
\pagestyle{empty}
\begin{document}
\color[HTML]{183342}\fontsize{22}{28}\selectfont
'''
    tex=pre+'\n\\newpage\n'.join('\\noindent\\(\\displaystyle '+expr+'\\)\n' for expr in expressions)+'\n\\end{document}\n'
    (root/'equations.tex').write_text(tex)
    r=subprocess.run(['pdflatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','equations.tex'],cwd=root,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    if r.returncode:raise RuntimeError('LaTeX failed:\n'+r.stdout[-5000:])
    doc=fitz.open(root/'equations.pdf')
    assert len(doc)==len(expressions),(len(doc),len(expressions))
    assets={}
    for i,expr in enumerate(expressions):
        p=doc[i];rects=[]
        for block in p.get_text('dict')['blocks']:
            for line in block.get('lines',[]):
                for span in line['spans']:rects.append(fitz.Rect(span['bbox']))
        rects += [fitz.Rect(d['rect']) for d in p.get_drawings()]
        assert rects,expr
        clip=rects[0]
        for rr in rects[1:]:clip|=rr
        clip+=(-2,-2,2,2)
        assert clip.x0>=0 and clip.y0>=0 and clip.x1<=p.rect.width and clip.y1<=p.rect.height,(expr,clip)
        assets[expr]=(i,clip)
    return cache,doc,assets
