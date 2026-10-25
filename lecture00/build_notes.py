"""Build the short instructor companion for Lecture 00."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from content import SLIDES, SOURCES

ROOT=Path(__file__).parent
for name,file in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Italic','DejaVuSans-Oblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Italic',boldItalic='Bold')
NAVY=colors.HexColor('#132B3C');TEAL=colors.HexColor('#087E83');LIGHT=colors.HexColor('#E5EEED')
STYLES={
 'title':ParagraphStyle('title',fontName='Bold',fontSize=23,leading=29,textColor=NAVY,spaceAfter=13),
 'h':ParagraphStyle('h',fontName='Bold',fontSize=11.5,leading=16,textColor=TEAL,spaceBefore=9,spaceAfter=5),
 'body':ParagraphStyle('body',fontName='Sans',fontSize=10,leading=14,textColor=NAVY,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='Sans',fontSize=8.7,leading=12,textColor=NAVY,spaceAfter=5),
}
story=[]
def p(text,style='body'):story.append(Paragraph(text,STYLES[style]))
def h(text):p(text,'h')
def page(title):
    if story:story.append(PageBreak())
    p(title,'title')
def fmt(seconds):return f'{seconds//60}:{seconds%60:02d}'
def table(headers,rows,widths):
    data=[]
    for i,row in enumerate([headers]+rows):
        st=ParagraphStyle('table',parent=STYLES['small'],fontName='Bold' if i==0 else 'Sans',textColor=colors.white if i==0 else NAVY)
        data.append([Paragraph(escape(str(cell)),st) for cell in row])
    t=Table(data,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Sans'),('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[LIGHT,colors.HexColor('#F4F5F1')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.append(t);story.append(Spacer(1,8))

TOTAL=sum(s['seconds'] for s in SLIDES)
page('Lecture 00 / teaching notes')
p(f'Introduction to cryptography • {len(SLIDES)} slides • Suggested delivery: {TOTAL//60} minutes {TOTAL%60} seconds, with room to adapt within a 10–15-minute opening.')
h('Purpose and tone')
p('Give students a reason to care before introducing notation. Retain the reference’s broad, inviting survey: what cryptography protects, how its uses evolved, where it appears in daily life, and why secure systems require more than cryptography. No formulas or algorithm descriptions are needed here.')
rows=[];elapsed=0
for i,s in enumerate(SLIDES,1):
    rows.append([str(i),s['title'],fmt(s['seconds']),f'{fmt(elapsed)}–{fmt(elapsed+s["seconds"])}'])
    elapsed+=s['seconds']
table(['Slide','Main idea','Time','Elapsed'],rows,[45,277,55,122])
h('Delivery')
p('Keep the opening cover brief. On slide 2, invite one or two examples students used that morning. Spend more time on the three protection goals and the final system-level limitation. Avoid turning the application slides into protocol tutorials. The final slide leads directly into Lecture 01 on classical ciphers.')

page('Explanations and accuracy notes')
h('The three protection goals')
p('Confidentiality asks who can read the content. Integrity asks whether it has been altered. Authentication asks who or what is on the other side, or where a message came from. Cryptanalysis studies how protections can fail. These are different questions; secrecy alone does not answer all of them.')
h('History and changing technology')
p('Connect hand writing, machine-assisted military communication, and digital networks. Enigma cryptanalysis drew on Polish work and multinational Allied teams. Avoid attributing the history to a single person. The historical thread should motivate the subject, without adding a new cipher lesson.')
h('Messaging and the web')
p('The messaging illustration describes an end-to-end encrypted conversation, not all chat or ordinary email. The forwarding service is not intended to have the keys needed to read the content. Metadata, backups, and compromised devices are separate concerns. HTTPS authenticates the named domain and protects a connection; it does not certify the operator’s honesty. The domain bank.example is fictional.')
h('Payments and passkeys')
p('Cryptographic payment checks help authenticate transaction data and detect changes. Payment methods do not all use identical mechanisms, and these checks do not prevent every fraud. With passkeys, a local face, fingerprint, or PIN check can authorize use of a credential; the website receives cryptographic proof, not the biometric as its login credential. Some passkeys sync between devices.')
h('Passports and signed updates')
p('A signature can support checks of data origin and integrity. An electronic passport’s chip-data signature does not by itself identify the person holding the document or prove that a chip was not cloned. A software signature is not a guarantee that the program contains no bugs. These qualifications belong in spoken explanation when relevant.')
h('One clear limitations discussion')
p('The transfer scam is illustrative, not a news report: a person can be manipulated into authorizing a genuine transaction whose cryptographic checks succeed. Secure devices, software, key handling, people, and processes also matter. Keep this point in one slide rather than repeating warnings after every application.')
h('Bridge to the first technical lecture')
p('The final glimpse MEET → PHHW uses a shift of three, but do not derive it here. Invite curiosity about how a message can be hidden and how another person might recover it. Lecture 01 supplies the construction and analysis.')

page('Sources and updates from the reference')
p('The source records distinguish material inspected in the uploaded reference, documentation retrieved from official repositories, and background standards cited bibliographically. The deck does not depend on live news or rapidly changing statistics.','small')
for source in SOURCES:
    h(f'[{source["id"]}] {escape(source["label"])}')
    p(escape(source['citation']),'small')
    if source['url']:
        url=escape(source['url']);p(f'<link href="{url}" color="#087E83">{url}</link>','small')
    p(escape(source['status']),'small')
h('What was refreshed')
p('Retained the three security goals, the connection to computing and communication, military history, finance, daily-life applications, and the system-level limitation. Replaced the Swift-volume and regional ATM discussion with timeless payment concepts; refreshed account authentication with passkeys; added signed software updates; and used a clearly illustrative scam instead of relying on the 2016 Bangladesh Bank incident. The original uploaded PDF is not redistributed.','small')

def footer(c,doc):
    c.setFont('Sans',8);c.setFillColor(TEAL);c.drawString(48,27,'LECTURE 00 / TEACHING NOTES');c.drawRightString(547,27,str(doc.page))
class NotesCanvas(Canvas):
    def __init__(self,*args,**kwargs):
        kwargs['initialFontName']='Sans';super().__init__(*args,**kwargs)
doc=SimpleDocTemplate(str(ROOT/'Lecture00_Teaching_Notes.pdf'),pagesize=(595,842),leftMargin=48,rightMargin=48,topMargin=43,bottomMargin=47,title='Lecture 00 — Teaching Notes',author='Cryptography lecture series')
doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=NotesCanvas)
print(f'Teaching notes built; delivery allocation {fmt(TOTAL)}.')
