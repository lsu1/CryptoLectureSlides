from pathlib import Path
from collections import Counter, defaultdict
from math import factorial, log2
import string, json, re
from math import sin,cos,pi
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
  elif typ=='alignment':
   text=norm('the sun and the man in the moon'); key='KING'*6; crypt=vig(text,'KING')
   left=142; cell=(w-left)/24; sx=x+left; selected=set(range(9,12))|set(range(17,20))
   c.setFont('Sans',9);c.setFillColor(MUTED)
   for j in range(24):c.drawCentredString(sx+(j+.5)*cell,y-15,str(j))
   for r,(label,row) in enumerate([('PLAINTEXT',text),('KEY STREAM',key),('CIPHERTEXT',crypt)]):
    yy=y-52-r*43
    c.setFillColor(TEAL);c.setFont('Bold',10);c.drawString(x,yy+2,label)
    for j,ch in enumerate(row):
     xx=sx+j*cell
     c.setFillColor((TEAL if r==1 else ORANGE) if j in selected else LIGHT)
     c.roundRect(xx+1,yy-8,cell-2,31,3,fill=1,stroke=0)
     c.setFillColor(WHITE if j in selected else INK);c.setFont('Mono',17);c.drawCentredString(xx+cell/2,yy+1,ch)
   yy=y-185;aa=sx+9.5*cell;bb=sx+17.5*cell
   c.setStrokeColor(ORANGE);c.setLineWidth(1.8);c.line(aa,yy,bb,yy)
   for end,direction in [(aa,1),(bb,-1)]:
    c.line(end,yy,end+direction*6,yy+4);c.line(end,yy,end+direction*6,yy-4)
   c.setFillColor(INK);c.setFont('Sans',13);c.drawCentredString((aa+bb)/2,yy-25,'8 positions = two 4-letter key cycles')
   y-=232
  elif typ=='ic_pairs':
   cw=58;gap=35;sx=x+w/2-(3*cw+2*gap)/2
   for i,ch in enumerate('AAB'):
    xx=sx+i*(cw+gap);c.setFillColor(MUTED);c.setFont('Sans',10);c.drawCentredString(xx+cw/2,y-7,'position '+str(i))
    c.setFillColor(LIGHT);c.roundRect(xx,y-76,cw,56,6,fill=1,stroke=0)
    c.setFillColor(INK);c.setFont('Mono',29);c.drawCentredString(xx+cw/2,y-59,ch)
   width=(w-32)/3
   for j,(a,b) in enumerate([(0,1),(0,2),(1,2)]):
    xx=x+j*(width+16);match='AAB'[a]=='AAB'[b]
    c.setFillColor(LIGHT);c.roundRect(xx,y-178,width,77,6,fill=1,stroke=0)
    c.setFillColor(MUTED);c.setFont('Sans',11);c.drawCentredString(xx+width/2,y-123,f'Pair of positions ({a}, {b})')
    c.setFillColor(TEAL if match else INK);c.setFont('Bold',18);c.drawCentredString(xx+width/2,y-155,'A–A: match' if match else 'A–B: different')
   c.setFillColor(TEAL);c.setFont('Bold',19);c.drawCentredString(x+w/2,y-211,'1 matching pair out of 3 → IC = 1/3')
   y-=232
  elif typ=='ic_reference':
   c.setFont('Bold',10);c.setFillColor(TEAL);c.drawString(x,y-10,'REFERENCE MATCH RATES FOR LONGER TEXTS')
   for j,(label,rate,display) in enumerate([('Uniform independent letters',1/26,'≈ 0.0385'),('Typical English prose',.065,'≈ 0.065')]):
    yy=y-57-j*58;c.setFillColor(INK);c.setFont('Sans',15);c.drawString(x,yy,label)
    c.setFillColor(LIGHT);c.roundRect(x+340,yy-6,330,24,3,fill=1,stroke=0)
    c.setFillColor(TEAL if j else MUTED);c.roundRect(x+340,yy-6,330*rate/.1,24,3,fill=1,stroke=0)
    c.setFillColor(INK);c.setFont('Sans',14);c.drawString(x+690,yy,display)
   y-=151
  elif typ=='columns':
   lw=152;cell=(w-lw)/5;palette=['#D8ECEB','#F4DFD5','#DFE5F3','#ECE3F1','#E8ECCC']
   for j in range(5):
    c.setFillColor(INK);c.setFont('Bold',12);c.drawCentredString(x+lw+(j+.5)*cell,y-16,'Key slot '+str(j+1))
   for r in range(5):
    yy=y-66-r*39;c.setFont('Sans',11);c.setFillColor(MUTED);c.drawString(x,yy+2,f'Positions {r*5}–{r*5+4}')
    for j in range(5):
     xx=x+lw+j*cell+5;c.setFillColor(colors.HexColor(palette[j]));c.roundRect(xx,yy-9,cell-10,33,4,fill=1,stroke=0)
     c.setFillColor(INK);c.setFont('Mono',21);c.drawCentredString(xx+(cell-10)/2,yy,VC[r*5+j])
   y-=248
  elif typ=='frequency_compare':
   gap=32;cw=(w-gap)/2;ph=130
   for j,k in enumerate([0,11]):
    xx=x+j*(cw+gap);px=xx+24;pw=cw-30;base=y-165
    c.setFont('Bold',13);c.setFillColor(INK);c.drawString(xx,y-18,'Subtract '+str(k)+(' (candidate L)' if k else ' (no shift)'))
    for tick in [0,.05,.10,.15]:
     yy=base+ph*tick/.15;c.setStrokeColor(LIGHT);c.setLineWidth(.5);c.line(px,yy,px+pw,yy)
     c.setFillColor(MUTED);c.setFont('Sans',8);c.drawRightString(px-3,yy-2,f'{100*tick:.0f}%')
    counts=Counter(shift(COLUMNS[0],-k));step=pw/26
    for i,ch in enumerate(A):
     bx=px+i*step;c.setFillColor(colors.HexColor('#BAC5CA'));c.rect(bx+1,base,step*.38,ph*Q[i]/.15,fill=1,stroke=0)
     c.setFillColor(TEAL);c.rect(bx+step*.44,base,step*.38,ph*(counts[ch]/209)/.15,fill=1,stroke=0)
     c.setFillColor(INK);c.setFont('Mono',8);c.drawCentredString(bx+step/2,base-13,ch)
   c.setFillColor(colors.HexColor('#BAC5CA'));c.rect(x,y-210,12,10,fill=1,stroke=0)
   c.setFillColor(INK);c.setFont('Sans',11);c.drawString(x+19,y-210,'English model')
   c.setFillColor(TEAL);c.rect(x+160,y-210,12,10,fill=1,stroke=0)
   c.setFillColor(INK);c.drawString(x+179,y-210,'Trial-decrypted column 1 • compare all 26 letters')
   y-=228
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
 if s['kind']=='cover':
  c.setFillColor(NAVY);c.rect(0,0,W,H,fill=1,stroke=0)
  c.setFillColor(WHITE);c.setFont('Sans',14);c.drawString(52,463,s['sub'])
  c.setFillColor(ORANGE);c.rect(52,436,56,4,fill=1,stroke=0)
  c.setFillColor(WHITE);c.setFont('Bold',66);c.drawString(52,326,'Classical');c.drawString(52,246,'ciphers')
  c.setFont('Sans',22);c.drawString(55,180,s['blocks'][0][1])
  cx,cy=730,276
  for radius,col in [(143,colors.HexColor('#365260')),(109,colors.HexColor('#365260'))]:
   c.setStrokeColor(col);c.setLineWidth(.6);c.circle(cx,cy,radius,fill=0,stroke=1)
  for letter_index,ch in enumerate(A):
   angle=pi/2-letter_index*2*pi/26
   for radius,char in [(143,ch),(109,A[(letter_index+2)%26])]:
    xx=cx+radius*cos(angle);yy=cy+radius*sin(angle)
    if letter_index==0:
     c.setFillColor(ORANGE if radius==143 else TEAL);c.circle(xx,yy,13,fill=1,stroke=0)
    c.setFillColor(WHITE if letter_index==0 else colors.HexColor('#B8CED6'));c.setFont('Mono',12);c.drawCentredString(xx,yy-4,char)
  c.setFillColor(WHITE);c.setFont('Sans',24);c.drawCentredString(cx,cy-8,'A → C')
  c.setFont('Sans',8);c.setFillColor(colors.HexColor('#BDD0D7'));c.drawRightString(908,22,f'{i:02d} / {len(slides):02d}')
  c.showPage();continue
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
