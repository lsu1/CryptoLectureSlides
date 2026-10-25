"""Build a short instructor review sheet for the course-information draft."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from content import COURSE, INSTRUCTORS, ASSESSMENTS, PROJECT, SOURCES, SLIDES

ROOT=Path(__file__).parent
for name,file in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Italic','DejaVuSans-Oblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Italic',boldItalic='Bold')
NAVY=colors.HexColor('#132B3C');TEAL=colors.HexColor('#087E83');LIGHT=colors.HexColor('#E5EEED')
STYLES={
    'title':ParagraphStyle('title',fontName='Bold',fontSize=22,leading=28,textColor=NAVY,spaceAfter=12),
    'h':ParagraphStyle('h',fontName='Bold',fontSize=12,leading=17,textColor=TEAL,spaceBefore=10,spaceAfter=6),
    'body':ParagraphStyle('body',fontName='Sans',fontSize=10.2,leading=14.5,textColor=NAVY,spaceAfter=9),
    'small':ParagraphStyle('small',fontName='Sans',fontSize=9,leading=13,textColor=NAVY,spaceAfter=6),
}
story=[]
def p(text,style='body'):story.append(Paragraph(text,STYLES[style]))
def h(text):p(text,'h')
def page(title):
    if story:story.append(PageBreak())
    p(title,'title')
def table(headers,rows,widths):
    data=[]
    for i,row in enumerate([headers]+rows):
        st=ParagraphStyle('cell',parent=STYLES['small'],fontName='Bold' if i==0 else 'Sans',textColor=colors.white if i==0 else NAVY)
        data.append([Paragraph(escape(str(v)),st) for v in row])
    tab=Table(data,colWidths=widths,hAlign='LEFT')
    tab.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),'Sans'),('BACKGROUND',(0,0),(-1,0),NAVY),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[LIGHT,colors.HexColor('#F4F5F1')]),
        ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),
        ('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
    ]))
    story.append(tab);story.append(Spacer(1,8))

mid=next(a for a in ASSESSMENTS if a['id']=='midterm')
final=next(a for a in ASSESSMENTS if a['id']=='final')
project=next(a for a in ASSESSMENTS if a['id']=='project')
page(f'{COURSE["code"]} / instructor review notes')
p(f'{COURSE["title"]} • Course-information draft • {len(SLIDES)} student-facing slides')
p('This sheet records the inputs used to prepare the draft and the few details that remain open. The slide deck is ready for the instructors to review and revise.')
h('Information carried into the slides')
table(['Item','Draft content and basis'],[
    ['Course',f'{COURSE["code"]}: {COURSE["title"]}; {COURSE["academic_units"]} academic units, from the course outline.'],
    ['Instructors','; '.join(i['name']+' — '+i['email'] for i in INSTRUCTORS)+'. Both were confirmed as instructors by the user.'],
    ['Weekly topics','The 13-week outline is retained. Week 12 is regular teaching. Week 13 has about one hour of revision followed by the two-hour final exam, as explicitly clarified by the user.'],
    ['Assessment weights',f'Mid-term {mid["weight"]}%; group project {project["weight"]}%; final examination {final["weight"]}%. These sum to 100% and come from the assessment table.'],
    ['Exams',f'Mid-term: week {mid["week"]}, {mid["hours"]} hour, closed book. Final: week {final["week"]}, {final["hours"]} hours, closed book. Duration and format come from the discussion screenshot; week 13 is confirmed by the user.'],
    ['Project',f'Teams of {PROJECT["group_size"]}; form the group and choose a topic by week {PROJECT["topic_by_week"]}; work in weeks {PROJECT["start_week"]}–{PROJECT["end_week"]}; submit by the end of week {PROJECT["end_week"]}. State individual contributions.'],
    ['Session window',f'{COURSE["session"]}, from the earlier user instruction. No exact mid-term or final-exam clock time is inferred from this window.'],
],[110,389])
h('How the timing clarification was applied')
p('The screenshot suggested leaving weeks 12–13 for final-exam review. The later user clarification takes precedence: week 12 still contains the planned regular topics; week 13 combines a short revision with the final examination. No earlier topics were shifted to make a second revision week.')

page('Source record and remaining details')
h('Source record')
for source in SOURCES:
    p('<b>'+escape(source['name'])+'</b><br/>'+escape(source['role'])+' '+escape(source['status']),'small')
h('Details not specified by the inputs')
p('Calendar dates, weekday, venue, and exact examination start times are not supplied. The deck therefore uses week numbers and durations. Permission for calculators or other materials is not inferred from “closed book.”')
p('The detailed project brief, deliverables, submission platform or format, and precise contribution-moderation procedure remain for the instructors to specify. The draft does not invent these requirements.')
h('Template points kept out of the student-facing grading summary')
p('The project appendix mixes instructor-rated contributions with references to teammate scores. The deck keeps the clear requirement to state contributions and does not reproduce the inconsistent numerical moderation formula.')
p('The generic absenteeism paragraph mentions a participation grade, while the assessment table assigns all 100% to the mid-term, project, and final. The deck follows that explicit three-component assessment structure.')
p('The outline lists 39 planned contact hours. The draft does not convert the user’s evening clock window into a new contact-hour total; the two quantities are not treated as interchangeable.')
h('Review and revision')
p('The student-facing deck is a draft for instructor review. It contains the requested contact details, week-by-week schedule, assessment weights, exam arrangements, and project timeline. It does not redistribute the original course document, screenshot, email headers, or unrelated correspondence.')

def footer(c,doc):
    c.setFillColor(TEAL);c.setFont('Sans',8);c.drawString(48,27,'MH6003 / INSTRUCTOR REVIEW NOTES');c.drawRightString(547,27,str(doc.page))
class ReviewCanvas(Canvas):
    def __init__(self,*args,**kwargs):
        kwargs['initialFontName']='Sans';super().__init__(*args,**kwargs)
doc=SimpleDocTemplate(str(ROOT/'MH6003_Review_Notes.pdf'),pagesize=(595,842),leftMargin=48,rightMargin=48,topMargin=43,bottomMargin=47,title='MH6003 — Instructor Review Notes',author='MH6003 course instructors')
doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=ReviewCanvas)
print('Instructor review notes built.')
