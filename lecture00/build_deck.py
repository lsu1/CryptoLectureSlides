"""Build a short visual introduction using only original vector illustrations."""
from pathlib import Path
from math import sin,cos,pi
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from content import SLIDES,SOURCES
R=Path(__file__).parent
for n,f in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf')]:
 pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Sans',boldItalic='Bold')
W,H=960,540
NAVY=colors.HexColor('#132B3C');INK=colors.HexColor('#183342');TEAL=colors.HexColor('#087E83');CORAL=colors.HexColor('#D85C36');PAPER=colors.HexColor('#F6F4EE');LIGHT=colors.HexColor('#E5EEED');WHITE=colors.white;MUTED=colors.HexColor('#536875');MINT=colors.HexColor('#7DDBD4');PANEL=colors.HexColor('#244353')
BOUNDS=[]
c=canvas.Canvas(str(R/'Lecture00_Introduction.pdf'),pagesize=(W,H),initialFontName='Sans')
c.setTitle('Lecture 00 — Introduction to Cryptography');c.setAuthor('Cryptography lecture series');c.setSubject('An 11-slide nontechnical opening for new cryptography students')
PAGE=0

def text(s,x,y,size=20,font='Sans',color=INK,align='left',maxwidth=None):
 width=pdfmetrics.stringWidth(s,font,size)
 if maxwidth is not None:assert width<=maxwidth,(PAGE,s,width,maxwidth)
 c.setFont(font,size);c.setFillColor(color)
 left=x-width/2 if align=='center' else x-width if align=='right' else x
 assert left>=0 and left+width<=W,(PAGE,s,left,width)
 assert 0<=y<=H,(PAGE,s,y)
 c.drawString(left,y,s)
 BOUNDS.append(dict(page=PAGE,text=s,box=[left,y-4,left+width,y+size]))
def para(s,x,top,width,size=20,font='Sans',color=INK,leading=None):
 st=ParagraphStyle('body',fontName=font,fontSize=size,leading=leading or size*1.38,textColor=color)
 p=Paragraph(escape(s),st);_,h=p.wrap(width,600)
 assert top-h>=45,(PAGE,'paragraph crosses footer',s,top,h)
 p.drawOn(c,x,top-h);BOUNDS.append(dict(page=PAGE,text=s,box=[x,top-h,x+width,top]))
 return top-h

def box(x,y,w,h,fill=LIGHT,r=10,stroke=None):
 c.setFillColor(fill);c.setStrokeColor(stroke or fill);c.roundRect(x,y,w,h,r,fill=1,stroke=bool(stroke))
def arrow(x1,y1,x2,y2,color=CORAL,lw=2.3):
 c.setStrokeColor(color);c.setLineWidth(lw);c.line(x1,y1,x2,y2)
 dx,dy=x2-x1,y2-y1;length=(dx*dx+dy*dy)**.5;ux,uy=dx/length,dy/length
 c.line(x2,y2,x2-ux*9-uy*5,y2-uy*9+ux*5);c.line(x2,y2,x2-ux*9+uy*5,y2-uy*9-ux*5)
def path(points,stroke,fill=None,close=False,lw=3):
 p=c.beginPath();p.moveTo(*points[0])
 for pt in points[1:]:p.lineTo(*pt)
 if close:p.close()
 c.setStrokeColor(stroke);c.setLineWidth(lw)
 if fill:c.setFillColor(fill)
 c.drawPath(p,stroke=1,fill=bool(fill))
def icon(name,x,y,size=64,color=TEAL):
 c.saveState();c.translate(x-size/2,y-size/2);c.scale(size/100,size/100);c.setStrokeColor(color);c.setFillColor(color);c.setLineWidth(3);c.setLineCap(1);c.setLineJoin(1)
 if name=='key':
  c.circle(29,62,18,fill=0,stroke=1);c.line(42,49,83,8);c.line(67,24,78,35);c.line(76,15,87,26)
 elif name=='lock':
  c.roundRect(22,12,56,47,7,fill=0,stroke=1);c.arc(32,42,68,88,0,180);c.line(32,65,32,59);c.line(68,65,68,59);c.circle(50,38,4,fill=0,stroke=1);c.line(50,34,50,26)
 elif name=='check':
  path([(18,48),(40,26),(82,76)],color,lw=5)
 elif name=='user':
  c.circle(50,72,15,fill=0,stroke=1);c.arc(18,5,82,59,0,180);c.line(18,31,18,15);c.line(82,31,82,15);c.line(18,15,82,15)
 elif name=='phone':
  c.roundRect(25,5,50,90,8,fill=0,stroke=1);c.line(40,86,60,86);c.line(44,14,56,14)
 elif name=='browser':
  c.roundRect(7,12,86,75,6,fill=0,stroke=1);c.line(7,70,93,70)
  for xx in [16,26,36]:c.circle(xx,78,1.6,fill=1,stroke=0)
  c.circle(50,42,19,fill=0,stroke=1);c.line(31,42,69,42);c.ellipse(42,23,58,61,fill=0,stroke=1)
 elif name=='card':
  c.roundRect(5,20,90,60,7,fill=0,stroke=1);c.roundRect(17,45,20,19,3,fill=0,stroke=1);c.line(17,54,37,54);c.line(27,45,27,64)
  for xx in [18,32,46,60]:c.line(xx,34,xx+6,34)
  for k in [0,1,2]:c.arc(61-k*7,41-k*5,78+k*7,68+k*5,-45,90)
 elif name=='terminal':
  c.roundRect(23,5,54,90,7,fill=0,stroke=1);c.rect(31,57,38,24,fill=0,stroke=1)
  for xx in [35,50,65]:
   for yy in [20,32,44]:c.circle(xx,yy,2,fill=1,stroke=0)
 elif name=='bank':
  path([(9,68),(50,91),(91,68)],color,close=True);c.line(11,60,89,60)
  for xx in [24,50,76]:c.line(xx,22,xx,60)
  c.line(10,19,90,19);c.line(5,10,95,10)
 elif name=='update':
  path([(22,9),(76,9),(76,70),(57,90),(22,90)],color,close=True);path([(57,90),(57,70),(76,70)],color)
  c.line(49,25,49,60);path([(35,46),(49,60),(63,46)],color)
 elif name=='passport':
  c.roundRect(18,5,64,90,5,fill=0,stroke=1);c.circle(50,58,20,fill=0,stroke=1);c.ellipse(41,38,59,78,fill=0,stroke=1);c.line(30,58,70,58);c.line(35,25,65,25);c.line(35,17,65,17)
 elif name=='machine':
  c.roundRect(5,12,90,73,6,fill=0,stroke=1)
  for xx in [25,50,75]:c.circle(xx,66,11,fill=0,stroke=1);c.line(xx,60,xx,72)
  for row in range(2):
   for col in range(5):c.circle(18+col*16,28+row*13,3,fill=0,stroke=1)
 elif name=='paper':
  c.rect(20,7,62,85,fill=0,stroke=1)
  for yy in [69,55,41,27]:c.line(31,yy,69,yy)
 elif name=='globe':
  c.circle(50,50,40,fill=0,stroke=1);c.ellipse(31,10,69,90,fill=0,stroke=1);c.ellipse(13,32,87,68,fill=0,stroke=1);c.line(10,50,90,50);c.line(50,10,50,90)
 elif name=='shield':
  p=c.beginPath();p.moveTo(50,92);p.lineTo(85,78);p.lineTo(82,46);p.curveTo(79,24,61,12,50,6);p.curveTo(39,12,21,24,18,46);p.lineTo(15,78);p.close();c.drawPath(p,stroke=1,fill=0);path([(33,49),(45,36),(69,63)],color,lw=4)
 elif name=='face':
  for xx,yy,dx,dy in [(10,90,1,-1),(90,90,-1,-1),(10,10,1,1),(90,10,-1,1)]:c.line(xx,yy,xx+dx*18,yy);c.line(xx,yy,xx,yy+dy*18)
  c.circle(50,56,21,fill=0,stroke=1);c.arc(35,29,65,49,180,180)
 else:raise ValueError(name)
 c.restoreState()

def header(s,dark=False):
 c.setFillColor(NAVY if dark else PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(CORAL);c.rect(52,491,34,4,fill=1,stroke=0)
 text(s['kicker'],98,489,10,'Bold',MINT if dark else TEAL)
 size=36
 while pdfmetrics.stringWidth(s['title'],'Bold',size)>856:size-=.5
 text(s['title'],52,439,size,'Bold',WHITE if dark else NAVY,maxwidth=856)
def footer(ref='',dark=False):
 col=colors.HexColor('#BAD0D9') if dark else MUTED
 text('CRYPTOGRAPHY / INTRODUCTION'+('  •  '+ref if ref else ''),52,22,8,color=col)
 text(f'{PAGE:02d} / {len(SLIDES):02d}',908,22,8,color=col,align='right')

def cover(s):
 c.setFillColor(NAVY);c.rect(0,0,W,H,fill=1,stroke=0)
 text(s['kicker'],52,473,12,'Bold',MINT)
 c.setFillColor(CORAL);c.rect(52,445,54,4,fill=1,stroke=0)
 text('Cryptography',52,323,60,'Bold',WHITE,maxwidth=550)
 text(s['subtitle'],55,270,25,color=WHITE,maxwidth=510)
 cx,cy=748,277
 for x,y,name in [(638,385,'phone'),(866,381,'browser'),(639,158,'bank'),(866,160,'update')]:
  c.setStrokeColor(colors.HexColor('#365464'));c.setLineWidth(1.5);c.line(cx,cy,x,y)
  c.setFillColor(PANEL);c.circle(x,y,37,fill=1,stroke=0);icon(name,x,y,44,MINT if name in ('phone','update') else WHITE)
 c.setFillColor(PANEL);c.circle(cx,cy,66,fill=1,stroke=0);icon('key',cx,cy,89,CORAL)
 text(f'{PAGE:02d} / {len(SLIDES):02d}',908,22,8,color=colors.HexColor('#BAD0D9'),align='right')

def everyday(s):
 header(s);para('Which of these have you done today?',52,395,856,22,color=TEAL)
 specs=[('browser','Open a website','WEB'),('card','Tap to pay','PAYMENTS'),('user','Sign in','IDENTITY'),('update','Install an update','SOFTWARE')]
 for i,(im,label,tag) in enumerate(specs):
  x=52+i*219;box(x,140,199,218)
  icon(im,x+99.5,290,75)
  text(label,x+99.5,217,18,'Bold',align='center',maxwidth=185)
  text(tag,x+99.5,169,10,'Bold',TEAL,align='center')
 footer()

def goals(s):
 header(s,True);para('Cryptography uses mathematics to protect information.',52,400,856,21,color=WHITE)
 specs=[('Who can\nread it?','Confidentiality','Keep the message private.','lock'),('Has it\nchanged?','Integrity','Detect an altered message.','check'),('Who is on the\nother end?','Authentication','Check the claimed identity.','user')]
 for i,(question,term,desc,im) in enumerate(specs):
  x=52+i*293;box(x,114,270,234,PANEL)
  yy=323
  for line in question.split('\n'):text(line,x+20,yy,27,'Bold',WHITE,maxwidth=230);yy-=34
  text(term,x+20,228,18,'Bold',MINT,maxwidth=230)
  icon(im,x+44,171,43,MINT);para(desc,x+80,195,170,16,color=WHITE,leading=22)
 footer('R',True)

def history(s):
 header(s);para('As communication and computing changed, the methods of protection changed too.',52,400,856,20)
 specs=[('paper','Pen and paper','Letters and couriers'),('machine','Machines','Military radio traffic'),('globe','Connected devices','Global digital communication')]
 for i,(im,title,sub) in enumerate(specs):
  x=52+i*299;box(x,133,258,192)
  icon(im,x+129,265,70)
  text(title,x+129,200,21,'Bold',align='center',maxwidth=240)
  text(sub,x+129,165,14,align='center',maxwidth=240)
  if i<2:arrow(x+268,232,x+288,232)
 footer('R')

def message_phone(x,y,label):
 box(x,y,164,218,WHITE,15,TEAL);c.setStrokeColor(TEAL);c.setLineWidth(2);c.line(x+58,y+204,x+106,y+204);c.line(x+65,y+13,x+99,y+13)
 box(x+14,y+105,136,58,LIGHT,7)
 text('Meet at noon.',x+82,y+128,16,align='center',maxwidth=129)
 text(label,x+82,y-27,17,'Bold',align='center',maxwidth=200)
def messages(s):
 header(s);para('End-to-end encryption protects a conversation’s content as it crosses the network.',52,400,856,20)
 message_phone(72,126,'Alice’s device');message_phone(724,126,'Bob’s device')
 text('ENCRYPT',154,356,11,'Bold',TEAL,align='center');text('DECRYPT',806,356,11,'Bold',TEAL,align='center')
 arrow(250,267,338,267);arrow(622,267,710,267)
 box(350,231,260,72,LIGHT);icon('lock',382,267,37);text('Protected message',493,260,17,'Bold',align='center',maxwidth=205)
 text('Message service',480,192,18,align='center')
 para('Keys let the intended devices unlock the message.',52,90,856,20)
 footer('2')

def web(s):
 header(s);para('Your browser checks the server’s identity for the named domain.',52,400,856,20)
 box(100,176,760,182,WHITE,10);box(100,318,760,40,LIGHT,9)
 icon('browser',125,338,27);text('https://bank.example',153,332,17,'Mono')
 for i,(im,label) in enumerate([('check','Check domain identity'),('key','Agree on keys'),('lock','Protect the data')]):
  cx=235+i*245;icon(im,cx,270,53)
  text(label,cx,206,17,'Bold',align='center',maxwidth=220)
  if i<2:arrow(cx+63,267,cx+180,267)
 para('Two computers can create a protected connection without sharing a secret in advance.',52,132,856,20)
 footer('1 • fictional domain shown')

def payments(s):
 header(s,True);para('Modern payments use cryptographic checks to authenticate transaction data.',52,400,856,20,color=WHITE)
 for i,(im,label) in enumerate([('card','Card or phone'),('terminal','Payment terminal'),('bank','Bank')]):
  cx=178+i*302;c.setFillColor(PANEL);c.circle(cx,268,78,fill=1,stroke=0);icon(im,cx,268,87,MINT if i!=1 else WHITE)
  text(label,cx,163,20,'Bold',WHITE,align='center',maxwidth=260)
  if i<2:arrow(cx+94,268,cx+208,268,MINT)
 for i,label in enumerate(['Protect payment data','Authenticate the transaction','Detect changes']):
  x=52+i*293;box(x,79,270,45,PANEL,6);text(label,x+135,95,15,'Bold',WHITE,align='center',maxwidth=250)
 footer('R • 5',True)

def passkeys(s):
 header(s);para('Your device proves it can use the right key.',52,400,856,23)
 box(105,133,194,223,WHITE,17,TEAL);c.setStrokeColor(TEAL);c.setLineWidth(2);c.line(174,342,230,342);c.line(182,146,222,146)
 icon('face',202,262,85);text('Local check',202,190,18,'Bold',align='center')
 text('Face • fingerprint • PIN',202,104,15,align='center',maxwidth=240)
 arrow(321,265,390,265);icon('key',445,265,70,CORAL);arrow(497,265,548,265)
 text('Use a passkey',445,177,17,'Bold',align='center')
 box(565,164,300,190,WHITE);box(565,315,300,39,LIGHT,8);text('Your account',715,328,17,'Bold',align='center')
 icon('check',715,258,65);text('Proof verified',715,193,20,'Bold',TEAL,align='center')
 para('The website receives cryptographic proof, not your fingerprint or face scan.',52,84,856,18)
 footer('3')

def signed(s):
 header(s);para('Digital signatures help check origin and detect changes.',52,400,856,22)
 for x,im,title,body in [(52,'passport','Electronic\npassport','Check the issuer and integrity of signed chip data.'),(496,'update','Software\nupdate','Check the publisher and integrity of an update.')]:
  box(x,142,412,218)
  icon(im,x+97,251,98)
  yy=323
  for line in title.split('\n'):text(line,x+182,yy,23,'Bold',maxwidth=210);yy-=30
  para(body,x+182,246,208,18)
 para('Authenticity matters even when the information itself is not secret.',52,105,856,20,color=TEAL)
 footer('4 • 5')

def limits(s):
 header(s,True);para('Strong cryptography cannot make every decision safe.',52,400,856,21,color=WHITE)
 box(52,166,466,176,PANEL)
 text('ILLUSTRATIVE SCAM',74,316,10,'Bold',MINT)
 para('“Please approve this transfer to keep your account safe.”',74,291,420,25,color=WHITE,leading=34)
 for i,(im,label) in enumerate([('key','Cryptography'),('phone','Devices & software'),('user','People & processes')]):
  yy=311-i*78;box(581,yy-31,327,61,PANEL,8);icon(im,614,yy,35,MINT);text(label,651,yy-7,18,'Bold',WHITE,maxwidth=240)
 para('A payment can pass the checks and still be part of a scam.',52,126,820,21,color=WHITE)
 footer('Illustrative scenario',True)

def next_slide(s):
 header(s);para('We begin with historical examples that we can work through by hand.',52,400,856,21)
 box(97,207,290,119,LIGHT);box(573,207,290,119,LIGHT)
 text('MEET',242,243,48,'Mono',align='center');text('PHHW',718,243,48,'Mono',TEAL,align='center');arrow(411,266,549,266)
 text('How do we hide a message?',52,156,25,'Bold',maxwidth=856)
 text('How could someone recover it?',52,108,25,'Bold',maxwidth=856)
 footer('Next: Lecture 01 / Classical ciphers')

DRAWERS=dict(cover=cover,everyday=everyday,goals=goals,history=history,messages=messages,web=web,payments=payments,passkeys=passkeys,signed=signed,limits=limits,next=next_slide)
for i,s in enumerate(SLIDES,1):
 PAGE=i;DRAWERS[s['id']](s);c.showPage()
c.save()
(R/'slide_manifest.json').write_text(json.dumps(SLIDES,ensure_ascii=False,indent=2))
(R/'source_notes.json').write_text(json.dumps(SOURCES,ensure_ascii=False,indent=2))
(R/'layout_checks.json').write_text(json.dumps(BOUNDS,ensure_ascii=False,indent=2))
print(f'Built {len(SLIDES)} visual slides; pacing: {sum(s["seconds"] for s in SLIDES)//60}m{sum(s["seconds"] for s in SLIDES)%60:02d}s.')
