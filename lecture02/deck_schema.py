"""Shared, editable slide-content primitives for Lecture 02."""
def slide(title, blocks=None, *, section='', sub='', take='', kind='normal', notes='', minutes=2, source=''):
    return dict(title=title, blocks=blocks or [], section=section, sub=sub, take=take,
                kind=kind, notes=notes, minutes=minutes, source=source)
def P(text): return ('p',text)
def B(text): return ('b',text)
def C(label,text,size=19): return ('code',label,text,size)
def M(tex): return ('math',tex)
def T(headers,rows,widths=None): return ('table',headers,rows,widths)
def Two(left,right): return ('two',left,right)
def D(name,**options): return ('diagram',name,options)
