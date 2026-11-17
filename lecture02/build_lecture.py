"""Render Lecture 02 as vector PDF with embedded text and LaTeX mathematics."""
from pathlib import Path
from math import sin,cos,pi
from xml.sax.saxutils import escape
import json
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from math_typesetting import compile_equations
from diagrams import draw as draw_diagram

ROOT=Path(__file__).parent
for n,f in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf'),('Italic','DejaVuSans-Oblique.ttf')]:
 pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Italic',boldItalic='Bold')
NAVY=colors.HexColor('#132B3C');TEAL=colors.HexColor('#087E83');CORAL=colors.HexColor('#D85C36');PAPER=colors.HexColor('#F6F4EE');INK=colors.HexColor('#183342');MUTED=colors.HexColor('#536875');LIGHT=colors.HexColor('#E5EEED');WHITE=colors.white
W,H=960,540
styles={}
for size in [9,10,11,12,13,14,15,16,17,18,19,20,22,24]:
 styles[size]=ParagraphStyle(str(size),fontName='Sans',fontSize=size,leading=size*1.34,textColor=INK)
issues=[];placements=[];layout=[]

def para(c,s,x,y,w,size=18,color=None):
 p=Paragraph(s,ParagraphStyle('p',parent=styles[size],textColor=color or INK));_,h=p.wrap(w,900)
 p.drawOn(c,x,y-h);return y-h

def drawblocks(c,blocks,x,y,w,number):
 for b in blocks:
  typ=b[0];start=y
  if typ in ('p','b'):
   if typ=='b':c.setFillColor(TEAL);c.circle(x+4,y-11,3,stroke=0,fill=1)
   xx=x+22 if typ=='b' else x;ww=w-22 if typ=='b' else w
   y=para(c,b[1],xx,y,ww)-14
  elif typ=='code':
   _,label,s,*opts=b;fs=opts[0] if opts else 19;lines=s.split('\n')
   while max(pdfmetrics.stringWidth(line,'Mono',fs) for line in lines)>w-32:fs-=.5
   if fs<12:issues.append((number,'code too small',fs))
   hh=41+len(lines)*fs*1.34
   c.setFillColor(LIGHT);c.roundRect(x,y-hh,w,hh,7,stroke=0,fill=1)
   c.setFillColor(TEAL);c.setFont('Bold',9);c.drawString(x+16,y-17,label)
   c.setFillColor(INK);c.setFont('Mono',fs)
   for j,s in enumerate(lines):c.drawString(x+16,y-40-j*fs*1.34,s)
   y-=hh+13
  elif typ=='math':
   expr=b[1];page,clip=assets[expr];scale=min(1.0,(w-30)/clip.width);hh=clip.height*scale+22
   if scale<.66:issues.append((number,'equation too small',round(scale,2)))
   c.setFillColor(LIGHT);c.roundRect(x,y-hh,w,hh,7,stroke=0,fill=1)
   rect=fitz.Rect(x+15,H-y+11,x+15+clip.width*scale,H-y+11+clip.height*scale)
   placements.append((number-1,rect,page,clip));y-=hh+13
  elif typ=='table':
   _,headers,rows,widths=b;nc=len(headers);nr=len(rows)+1
   widths=widths or [1]*nc;widths=[v*w/sum(widths) for v in widths]
   fs=14 if nc<=8 and nr<=11 else 11 if nc<=9 else 10
   pad=7 if nr<=11 else 2.4
   if w<500:fs=min(fs,13);pad=min(pad,5)
   data=[]
   for i,row in enumerate([headers]+rows):
    st=ParagraphStyle('cell',fontName='Bold' if i==0 else 'Sans',fontSize=fs,leading=fs*1.22,textColor=WHITE if i==0 else INK)
    data.append([Paragraph(escape(str(cell)),st) for cell in row])
   t=Table(data,colWidths=widths)
   t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Sans'),('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[LIGHT,colors.HexColor('#EFF2EF')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),10 if nc<10 else 3),('RIGHTPADDING',(0,0),(-1,-1),10 if nc<10 else 3),('TOPPADDING',(0,0),(-1,-1),pad),('BOTTOMPADDING',(0,0),(-1,-1),pad),('LINEBELOW',(0,0),(-1,0),1,TEAL)]))
   _,hh=t.wrap(w,1000);t.drawOn(c,x,y-hh);y-=hh+13
  elif typ=='two':
   gap=28;ww=(w-gap)/2
   y=min(drawblocks(c,b[1],x,y,ww,number),drawblocks(c,b[2],x+ww+gap,y,ww,number))
  elif typ=='diagram':
   y-=draw_diagram(c,b[1],b[2],x,y,w)+12
  else:raise ValueError(typ)
  layout.append(dict(slide=number,type=typ,top=start,bottom=y+13))
 return y

def math_walk(blocks):
 for b in blocks:
  if b[0]=='math':yield b[1]
  elif b[0]=='two':yield from math_walk(b[1]);yield from math_walk(b[2])

def cover(c,total):
 c.setFillColor(NAVY);c.rect(0,0,W,H,stroke=0,fill=1)
 c.setFillColor(WHITE);c.setFont('Sans',14);c.drawString(52,463,'Cryptography lecture series • Lecture 02')
 c.setFillColor(CORAL);c.rect(52,436,56,4,stroke=0,fill=1)
 c.setFillColor(WHITE);c.setFont('Bold',52)
 for yy,t in [(335,'One-time pads'),(270,'& block ciphers')]:c.drawString(52,yy,t)
 c.setFont('Sans',21);c.drawString(54,196,'Perfect secrecy, practical security, and DES')
 # Bit strings enter a stylised three-round network.
 xx=742
 for i,t in enumerate(['1011 0010','0110 1101','1101 1111']):
  yy=370-i*112;c.setFillColor(colors.HexColor('#244657'));c.roundRect(xx-102,yy-29,204,58,8,stroke=0,fill=1)
  c.setFillColor(WHITE);c.setFont('Mono',23);c.drawCentredString(xx,yy-8,t)
  if i<2:
   c.setStrokeColor(CORAL);c.setLineWidth(2);c.line(xx,yy-30,xx,yy-81);c.line(xx,yy-81,xx-5,yy-75);c.line(xx,yy-81,xx+5,yy-75)
 c.setFillColor(colors.HexColor('#BDD0D7'));c.setFont('Sans',8);c.drawString(52,22,'CRYPTOGRAPHY / LECTURE 02');c.drawRightString(908,22,f'01 / {total:02d}')

def build():
 global assets
 from slide_content import slides,MAIN_COUNT,SESSION_PLAN
 cache,mathdoc,assets=compile_equations([e for s in slides for e in math_walk(s['blocks'])])
 out=ROOT/'Lecture02_OTP_and_Block_Ciphers.pdf'
 c=canvas.Canvas(str(out),pagesize=(W,H),initialFontName='Sans')
 c.setTitle('Lecture 02 — One-time Pads and Block Ciphers');c.setAuthor('Cryptography lecture series');c.setSubject('Master’s cryptography: perfect secrecy, information theory, block-cipher design, and historical DES')
 seen_sections=set()
 for n,s in enumerate(slides,1):
  c.bookmarkPage(f'slide-{n}')
  if s['section'] not in seen_sections:
   c.addOutlineEntry(s['section'].title(),f'slide-{n}',level=0,closed=False);seen_sections.add(s['section'])
  elif n>MAIN_COUNT:
   c.addOutlineEntry(s['title'],f'slide-{n}',level=1,closed=False)
  if s['kind']=='cover':cover(c,len(slides));c.showPage();continue
  dark=s['kind']=='divider'
  c.setFillColor(NAVY if dark else PAPER);c.rect(0,0,W,H,stroke=0,fill=1)
  c.setFillColor(CORAL);c.rect(52,492,34,4,stroke=0,fill=1)
  c.setFillColor(WHITE if dark else TEAL);c.setFont('Bold',10);c.drawString(98,490,s['section'])
  fs=34
  while pdfmetrics.stringWidth(s['title'],'Bold',fs)>856:fs-=.5
  if fs<25:issues.append((n,'title small',fs))
  c.setFont('Bold',fs);c.setFillColor(WHITE if dark else NAVY);c.drawString(52,445,s['title'])
  top=410
  if s['sub']:top=para(c,s['sub'],52,top,856,16,WHITE if dark else MUTED)-17
  if dark:
   for b in s['blocks']:
    if b[0]=='p':top=para(c,b[1],52,top,820,22,WHITE)-22
    else:top=drawblocks(c,[b],52,top,856,n)
  else:top=drawblocks(c,s['blocks'],52,top,856,n)
  limit=89 if s['take'] else 55
  if top+13<limit:issues.append((n,'content reaches footer',round(top+13,1),s['title']))
  if s['take']:
   c.setFillColor(TEAL if dark else LIGHT);c.roundRect(52,43,856,35,5,stroke=0,fill=1)
   p=Paragraph(escape(s['take']),ParagraphStyle('take',parent=styles[12],textColor=WHITE if dark else INK));_,hh=p.wrap(830,40)
   if hh>29:issues.append((n,'takeaway overflows',hh))
   p.drawOn(c,65,60-hh/2)
  c.setFont('Sans',8);c.setFillColor(colors.HexColor('#BDD0D7') if dark else MUTED)
  c.drawString(52,22,s['source'] or ('OPTIONAL MATHEMATICAL / TABLE REFERENCE' if n>MAIN_COUNT else 'CRYPTOGRAPHY / LECTURE 02 / ONE-TIME PADS & BLOCK CIPHERS'))
  c.drawRightString(908,22,f'{n:02d} / {len(slides):02d}');c.showPage()
 c.save()
 doc=fitz.open(out)
 for page,rect,mp,clip in placements:doc[page].show_pdf_page(rect,mathdoc,mp,clip=clip)
 tmp=out.with_suffix('.tmp.pdf');doc.save(tmp,garbage=4,deflate=True);doc.close();tmp.replace(out)
 mathdoc.close();cache.cleanup()
 (ROOT/'slide_manifest.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2))
 (ROOT/'layout_checks.json').write_text(json.dumps(dict(issues=issues,blocks=layout),indent=2))
 (ROOT/'session_plan.json').write_text(json.dumps(SESSION_PLAN,ensure_ascii=False,indent=2))
 from crypto_examples import DES_PLAINTEXT,DES_KEY,DES_CIPHERTEXT,DES_TRACE,DES_KEY_TRACE,TOY_PLAINTEXT,TOY_KEYS,TOY_CIPHERTEXT,TOY_TRACE
 from otp_content import OTP_LETTER_CIPHERTEXT,OTP_BIT_CIPHERTEXT,OTP_UNICITY_ESTIMATE
 data=dict(des_plaintext=f'{DES_PLAINTEXT:016X}',des_key=f'{DES_KEY:016X}',des_ciphertext=f'{DES_CIPHERTEXT:016X}',des_trace=DES_TRACE,des_key_trace=DES_KEY_TRACE,toy_plaintext=f'{TOY_PLAINTEXT:04X}',toy_round_keys=[f'{v:04X}' for v in TOY_KEYS],toy_ciphertext=f'{TOY_CIPHERTEXT:04X}',toy_trace=TOY_TRACE,otp_letter_ciphertext=OTP_LETTER_CIPHERTEXT,otp_bit_ciphertext=OTP_BIT_CIPHERTEXT,substitution_unicity_estimate=OTP_UNICITY_ESTIMATE)
 (ROOT/'worked_examples.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
 print('Slides',len(slides),'Teaching',MAIN_COUNT,'Appendix',len(slides)-MAIN_COUNT,'Equation placements',len(placements),'Layout issues',issues)
 if issues:raise SystemExit('Fix layout issues before publishing.')
if __name__=='__main__':build()
