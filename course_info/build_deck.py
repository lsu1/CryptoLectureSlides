"""Build the review draft of the MH6003 course-information deck."""
from pathlib import Path
from xml.sax.saxutils import escape
import json
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from content import COURSE,INSTRUCTORS,WEEKS,ASSESSMENTS,PROJECT,SLIDES,SOURCES
R=Path(__file__).parent
for n,f in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Sans',boldItalic='Bold')
W,H=960,540
NAVY=colors.HexColor('#132B3C');INK=colors.HexColor('#183342');TEAL=colors.HexColor('#087E83');CORAL=colors.HexColor('#D85C36');PAPER=colors.HexColor('#F6F4EE');LIGHT=colors.HexColor('#E5EEED');WHITE=colors.white;MUTED=colors.HexColor('#536875');MINT=colors.HexColor('#7DDBD4');PANEL=colors.HexColor('#244353')
c=canvas.Canvas(str(R/'MH6003_Course_Information.pdf'),pagesize=(W,H),initialFontName='Sans')
c.setTitle('MH6003 — Cryptography: Course Information');c.setAuthor('MH6003 course team');c.setSubject('Draft course information for instructor review')
PAGE=0;TEXT=[]
def line(s,x,y,size=20,font='Sans',color=INK,align='left',maxwidth=None):
 width=pdfmetrics.stringWidth(s,font,size)
 if maxwidth is not None:assert width<=maxwidth,(PAGE,s,width,maxwidth)
 left=x-width/2 if align=='center' else x-width if align=='right' else x
 assert left>=0 and left+width<=W and 0<=y<=H,(PAGE,s,left,width,y)
 c.setFillColor(color);c.setFont(font,size);c.drawString(left,y,s);TEXT.append(dict(page=PAGE,text=s))
def para(s,x,top,width,size=18,font='Sans',color=INK):
 p=Paragraph(escape(s),ParagraphStyle('p',fontName=font,fontSize=size,leading=size*1.38,textColor=color));_,h=p.wrap(width,600)
 assert top-h>=55,(PAGE,'paragraph too low',s,top,h)
 p.drawOn(c,x,top-h);TEXT.append(dict(page=PAGE,text=s));return top-h

def box(x,y,w,h,fill=LIGHT,r=9):c.setFillColor(fill);c.roundRect(x,y,w,h,r,fill=1,stroke=0)
def arrow(x1,y,x2):
 c.setStrokeColor(CORAL);c.setLineWidth(2);c.line(x1,y,x2,y);c.line(x2,y,x2-7,y+4);c.line(x2,y,x2-7,y-4)
def footer():
 line('MH6003 / COURSE INFORMATION / DRAFT FOR REVIEW',52,22,8,color=MUTED if PAGE!=1 else colors.HexColor('#BAD0D9'))
 line(f'{PAGE:02d} / {len(SLIDES):02d}',908,22,8,color=MUTED if PAGE!=1 else colors.HexColor('#BAD0D9'),align='right')
def header(s):
 c.setFillColor(PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(CORAL);c.rect(52,491,34,4,fill=1,stroke=0)
 line(s['kicker'],98,489,10,'Bold',TEAL)
 size=35
 while pdfmetrics.stringWidth(s['title'],'Bold',size)>856:size-=.5
 line(s['title'],52,439,size,'Bold',NAVY,maxwidth=856)
def table(top,rows,headers=('Week','Topics / milestones'),widths=(102,754),fs=17):
 style=lambda i:ParagraphStyle('t',fontName='Bold' if i==0 else 'Sans',fontSize=15 if i==0 else fs,leading=22.5,textColor=WHITE if i==0 else INK)
 data=[[Paragraph(escape(str(v)),style(i)) for v in row] for i,row in enumerate([list(headers)]+rows)]
 t=Table(data,colWidths=list(widths));t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Sans'),('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[LIGHT,colors.HexColor('#EDF1EE')]),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),15),('RIGHTPADDING',(0,0),(-1,-1),15),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
 _,height=t.wrap(sum(widths),600)
 assert top-height>=63,(PAGE,'table too low',height,top)
 t.drawOn(c,52,top-height)
 for row in [list(headers)]+rows:
  for cell in row:TEXT.append(dict(page=PAGE,text=str(cell)))
 return top-height

def cover(s):
 c.setFillColor(NAVY);c.rect(0,0,W,H,fill=1,stroke=0)
 line(COURSE['code'],52,473,20,'Bold',MINT)
 c.setFillColor(CORAL);c.rect(52,441,54,4,fill=1,stroke=0)
 line(COURSE['title'],52,323,60,'Bold',WHITE,maxwidth=550)
 line(s['subtitle'],55,270,27,color=WHITE)
 c.setStrokeColor(colors.HexColor('#365464'));c.setLineWidth(2);c.line(702,180,702,365)
 for week,y,label,col in [(1,365,'Start',TEAL),(7,272,'Mid-term',CORAL),(13,180,'Final exam',TEAL)]:
  c.setFillColor(col);c.circle(702,y,29,fill=1,stroke=0)
  line(str(week),702,y-9,24,'Bold',WHITE,align='center')
  line('WEEK '+str(week),753,y+12,10,'Bold',MINT)
  line(label,753,y-15,19,'Bold',WHITE,maxwidth=155)

def instructors(s):
 header(s)
 for i,person in enumerate(INSTRUCTORS):
  x=52+i*444;box(x,174,412,212)
  line('INSTRUCTOR',x+24,352,10,'Bold',TEAL)
  line(person['name'],x+24,295,27,'Bold',maxwidth=364)
  line(person['email'],x+24,239,21,color=TEAL,maxwidth=364)
  width=pdfmetrics.stringWidth(person['email'],'Sans',21)
  c.linkURL('mailto:'+person['email'],(x+24,234,x+24+width,260),relative=0,thickness=0)
 line('3 academic units',52,115,19,'Bold')
 line('Evening session: '+COURSE['session'],908,115,19,align='right')

def schedule(s,first,last):
 header(s)
 rows=[[str(week),topic] for week,topic in WEEKS if first<=week<=last]
 table(399,rows)

def grading(s):
 header(s)
 palette=[CORAL,TEAL,NAVY]
 for i,(a,col) in enumerate(zip(ASSESSMENTS,palette)):
  x=52+i*293;box(x,157,270,224)
  c.setFillColor(col);c.roundRect(x,363,270,18,7,fill=1,stroke=0)
  line(str(a['weight'])+'%',x+135,276,64,'Bold',col,align='center',maxwidth=250)
  line(a['title'],x+135,220,22,'Bold',align='center',maxwidth=246)
  line(a['mode'],x+135,184,17,color=MUTED,align='center')
 line('Total: 100% of the course grade',52,102,21,'Bold',TEAL)

def exams(s):
 header(s)
 for i,a in enumerate([ASSESSMENTS[0],ASSESSMENTS[2]]):
  x=52+i*444;box(x,154,412,232)
  line(a['title'],x+24,349,25,'Bold',maxwidth=365)
  line('WEEK '+str(a['week']),x+24,317,11,'Bold',TEAL)
  line(str(a['hours'])+(' hour' if a['hours']==1 else ' hours'),x+24,260,42,'Bold')
  box(x+24,195,165,32,TEAL,5);line('CLOSED BOOK',x+106.5,205,12,'Bold',WHITE,align='center')
  line('Individual assessment',x+24,171,16,color=MUTED)
 para('Week 13: approximately one hour of revision, followed by the two-hour final exam.',52,112,856,19)

def project(s):
 header(s)
 para('Teams of 3–4 students. The project contributes 30% of the course grade.',52,399,856,21)
 specs=[('By week 7',['Form your group','Choose your topic']),('Weeks 8–11',['Four-week','project period']),('End of week 11',['Submit','the project'])]
 for i,(title,body) in enumerate(specs):
  x=52+i*299;box(x,139,258,199)
  line(title,x+20,302,23,'Bold',TEAL,maxwidth=220)
  yy=252
  for item in body:line(item,x+20,yy,21,maxwidth=220);yy-=33
  if i==1:
   for j,week in enumerate([8,9,10,11]):
    box(x+20+j*53,157,43,29,WHITE,4);line(str(week),x+41.5+j*53,166,12,'Bold',align='center')
  if i<2:arrow(x+266,233,x+291)
 para(PROJECT['contributions'],52,105,856,20)

for n,s in enumerate(SLIDES,1):
 PAGE=n
 if s['id']=='cover':cover(s)
 elif s['id']=='instructors':instructors(s)
 elif s['id']=='weeks_first':schedule(s,1,6)
 elif s['id']=='weeks_second':schedule(s,7,13)
 elif s['id']=='grading':grading(s)
 elif s['id']=='exams':exams(s)
 elif s['id']=='project':project(s)
 else:raise ValueError(s['id'])
 footer();c.showPage()
c.save()
(R/'course_data.json').write_text(json.dumps(dict(course=COURSE,instructors=INSTRUCTORS,weeks=WEEKS,assessments=ASSESSMENTS,project=PROJECT,sources=SOURCES),ensure_ascii=False,indent=2))
(R/'slide_manifest.json').write_text(json.dumps(SLIDES,ensure_ascii=False,indent=2))
(R/'rendered_text.json').write_text(json.dumps(TEXT,ensure_ascii=False,indent=2))
print('Built seven-slide course-information draft.')
