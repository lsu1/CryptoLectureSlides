from pathlib import Path
from collections import Counter, defaultdict
from math import factorial, log2
import string, json, re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape

ROOT=Path(__file__).parent
for n,f in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf'),('Italic','DejaVuSans-Oblique.ttf')]:
 pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Italic',boldItalic='Bold')
from slide_content import *
from math_typesetting import compile_equations
import fitz

NAVY=colors.HexColor('#132B3C'); TEAL=colors.HexColor('#087E83'); ORANGE=colors.HexColor('#D85C36'); PAPER=colors.HexColor('#F6F4EE'); INK=colors.HexColor('#183342'); MUTED=colors.HexColor('#536875'); LIGHT=colors.HexColor('#E5EEED'); WHITE=colors.white
W,H=960,540
issues=[]
placements=[]
styles={}
for size in [12,13,14,15,16,17,18,19,20,22,26]:
 styles[size]=ParagraphStyle(str(size),fontName='Sans',fontSize=size,leading=size*1.4,textColor=INK,spaceAfter=0)
def para(c,s,x,y,w,size=18,color=None):
 st=ParagraphStyle('p',parent=styles[size],textColor=color or INK)
 p=Paragraph(s,st); _,h=p.wrap(w,800)
 p.drawOn(c,x,y-h)
 return y-h

def drawblocks(c,blocks,x,y,w,slide):
 for block in blocks:
  typ=block[0]
  if typ in ('p','b'):
   s=block[1]
   if typ=='b':
    c.setFillColor(TEAL); c.circle(x+4,y-12,3,fill=1,stroke=0)
    y=para(c,s,x+22,y,w-22,18)-17
   else:y=para(c,s,x,y,w,18)-17
  elif typ=='code':
   _,label,s,*opts=block
   lines=s.split('\n'); fs=opts[0] if opts else 19
   while max(pdfmetrics.stringWidth(v,'Mono',fs) for v in lines)>w-30: fs-=.5
   hh=29+len(lines)*(fs*1.35)+12
   c.setFillColor(LIGHT); c.roundRect(x,y-hh,w,hh,8,fill=1,stroke=0)
   c.setFillColor(TEAL); c.setFont('Bold',9); c.drawString(x+16,y-17,label)
   c.setFillColor(INK); c.setFont('Mono',fs)
   for j,line in enumerate(lines): c.drawString(x+16,y-39-j*fs*1.35,line)
   y-=hh+14
  elif typ=='table':
   _,headers,rows,widths=block
   widths=widths or [w/len(headers)]*len(headers)
   if sum(widths)!=w:widths=[v*w/sum(widths) for v in widths]
   data=[[Paragraph(escape(str(cell)),ParagraphStyle('t',parent=styles[14],textColor=WHITE if i==0 else INK,fontName='Bold' if i==0 else 'Sans')) for cell in row] for i,row in enumerate([headers]+rows)]
   table=Table(data,colWidths=widths)
   table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Sans'),('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[LIGHT,colors.HexColor('#EFF2EF')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),1,TEAL)]))
   _,hh=table.wrap(w,800); table.drawOn(c,x,y-hh); y-=hh+17
  elif typ=='two':
   gap=32; ww=(w-gap)/2
   y1=drawblocks(c,block[1],x,y,ww,slide);y2=drawblocks(c,block[2],x+ww+gap,y,ww,slide);y=min(y1,y2)
  elif typ=='math':
   expr=block[1]; pageidx,clip=assets[expr]
   scale=min(1.0,(w-32)/clip.width); hh=clip.height*scale+24
   if scale<0.8: issues.append((slide,'math too small',round(scale,2)))
   c.setFillColor(LIGHT);c.roundRect(x,y-hh,w,hh,7,fill=1,stroke=0)
   rect=fitz.Rect(x+16,H-y+12,x+16+clip.width*scale,H-y+12+clip.height*scale)
   placements.append((slide-1,rect,pageidx,clip))
   y-=hh+14
  elif typ=='grid':
   cell=48; gx=x+(w-5*cell)/2; gy=y-5*cell
   highlight=set(block[1]);limit=block[2]
   for i,ch in enumerate(SQUARE):
    r,col=divmod(i,5); xx=gx+col*cell; yy=gy+(4-r)*cell
    if i>=limit:ch=''
    c.setFillColor(TEAL if ch in highlight else LIGHT);c.setStrokeColor(PAPER);c.rect(xx,yy,cell,cell,fill=1,stroke=1)
    c.setFillColor(WHITE if ch in highlight else INK);c.setFont('Mono',22);c.drawCentredString(xx+cell/2,yy+16,ch)
   y=gy-18
  elif typ=='pipeline':
   ww=(w-96)/5
   labels=[('PLAINTEXT','message p'),('ENCRYPTION','Eₖ'),('CIPHERTEXT','c = Eₖ(p)'),('DECRYPTION','Dₖ'),('PLAINTEXT','message p')]
   for j,(a,b) in enumerate(labels):
    xx=x+j*(ww+24);c.setFillColor(LIGHT);c.roundRect(xx,y-104,ww,94,7,fill=1,stroke=0)
    c.setFillColor(TEAL);c.setFont('Bold',9);c.drawCentredString(xx+ww/2,y-37,a)
    c.setFillColor(INK);c.setFont('Sans',17);c.drawCentredString(xx+ww/2,y-77,b)
    if j in (1,3):
     c.setFillColor(TEAL);c.setFont('Sans',10);c.drawCentredString(xx+ww/2,y+3,'shared key k')
    if j<4:
     c.setStrokeColor(ORANGE);c.setLineWidth(1.5);c.line(xx+ww+3,y-57,xx+ww+20,y-57);c.line(xx+ww+15,y-52,xx+ww+20,y-57);c.line(xx+ww+15,y-62,xx+ww+20,y-57)
   y-=132
  if y+14<89: issues.append((slide,typ,round(y,1)))
 return y

def walk_math(blocks):
 for b in blocks:
  if b[0]=='math':yield b[1]
  elif b[0]=='two':
   yield from walk_math(b[1]);yield from walk_math(b[2])
math_cache,math_doc,assets=compile_equations([expr for s in slides for expr in walk_math(s['blocks'])])
out=ROOT/'Lecture01_Classical_Ciphers.pdf'
c=canvas.Canvas(str(out),pagesize=(W,H),initialFontName='Sans')
c.setTitle('Lecture 01 — Classical Ciphers');c.setAuthor('Cryptography lecture series');c.setSubject('Three-hour introductory lecture for master’s students')
for i,s in enumerate(slides,1):
 dark=s['kind'] in ('cover','divider')
 c.setFillColor(NAVY if dark else PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(ORANGE);c.rect(52,492,34,4,fill=1,stroke=0)
 c.setFillColor(WHITE if dark else TEAL);c.setFont('Bold',10);c.drawString(98,490,s['section'])
 # title is one line where possible, smaller as needed
 fs=34
 while pdfmetrics.stringWidth(s['title'],'Bold',fs)>856: fs-=.5
 c.setFont('Bold',fs);c.setFillColor(WHITE if dark else NAVY);c.drawString(52,445,s['title'])
 top=410
 if s['sub']:
  top=para(c,s['sub'],52,411,856,16,WHITE if dark else MUTED)-21
 if dark:
  # Invert paragraph palette only; code cards retain their readable light palette.
  for block in s['blocks']:
   if block[0]=='p':top=para(c,block[1],52,top,820,22,WHITE)-24
   else:top=drawblocks(c,[block],52,top,856,i)
 else:drawblocks(c,s['blocks'],52,top,856,i)
 if s['take']:
  c.setFillColor(TEAL if dark else LIGHT);c.roundRect(52,43,856,35,5,fill=1,stroke=0)
  p=Paragraph(escape(s['take']),ParagraphStyle('take',parent=styles[12],textColor=WHITE if dark else INK))
  _,hh=p.wrap(830,40)
  if hh>29:issues.append((i,'takeaway',hh))
  p.drawOn(c,65,60-hh/2)
 c.setFont('Sans',8);c.setFillColor(colors.HexColor('#BDD0D7') if dark else MUTED)
 c.drawString(52,22,s['source'] if s['source'] else 'CRYPTOGRAPHY / LECTURE 01 / CLASSICAL CIPHERS')
 c.drawRightString(908,22,f'{i:02d} / {len(slides):02d}')
 c.showPage()
c.save()
doc=fitz.open(out)
for page,rect,mathpage,clip in placements:
 doc[page].show_pdf_page(rect,math_doc,mathpage,clip=clip)
final=out.with_name(out.stem+'.tmp.pdf')
doc.save(final,garbage=4,deflate=True)
doc.close();final.replace(out)
math_doc.close();math_cache.cleanup()
(ROOT/'slide_manifest.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2))
(ROOT/'worked_examples.json').write_text(json.dumps(dict(substitution_alphabet=SUB,frequency_plaintext=FREQ_TEXT,frequency_ciphertext=FREQ_C,frequency_counts=dict(Counter(FREQ_C)),vigenere_plaintext=CORPUS,vigenere_ciphertext=VC,vigenere_key='LEMON',recovered_key=REC,english_model=Q,vigenere_columns=COLUMNS,column0_counts=dict(Counter(COLUMNS[0])),column0_scores={str(k):chi_score(COLUMNS[0],k) for k in range(26)},kasiski_trigram='FVR',kasiski_positions=REPEATS['FVR'],observed_substitution=OBSERVED_SUB,column_IC={str(m):[ic(VC[j::m]) for j in range(m)] for m in [1,2,3,4,5,10]},playfair_square=SQUARE,permutation=PERM,inverse_permutation=INV),indent=2))
print('Slides:',len(slides),'Scheduled:',MAIN_COUNT,'Appendix:',len(slides)-MAIN_COUNT,'Equations:',len(placements),'Layout issues:',issues)
assert not issues,issues
