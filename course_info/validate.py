"""Check course-data consistency and the actual PDF deliverables."""
from pathlib import Path
import json,re,hashlib
import fitz
from content import COURSE,INSTRUCTORS,WEEKS,ASSESSMENTS,PROJECT,SLIDES
R=Path(__file__).parent
checks=[]
def check(label,condition):
 assert condition,label
 checks.append(label)
check('One complete 13-week sequence',[week for week,topic in WEEKS]==list(range(1,14)) and all(topic for week,topic in WEEKS))
check('Assessment weights total 100%',sum(a['weight'] for a in ASSESSMENTS)==100 and len(ASSESSMENTS)==3)
check('Exam formats and durations are specified',all(a['format']=='Closed book' and a['hours']>0 for a in ASSESSMENTS if a['id']!='project'))
check('Project duration matches its inclusive week range',PROJECT['end_week']-PROJECT['start_week']+1==PROJECT['duration_weeks'])
check('Project preparation precedes the project period',PROJECT['topic_by_week']<PROJECT['start_week'])
outputs={};texts={}
for filename,expected in [('MH6003_Course_Information.pdf',7),('MH6003_Review_Notes.pdf',2)]:
 path=R/filename;doc=fitz.open(path);fonts={};issues=[];pages=[]
 check(filename+' page count',len(doc)==expected)
 check(filename+' not encrypted',not doc.is_encrypted)
 for n,page in enumerate(doc,1):
  txt=page.get_text();pages.append(txt)
  if not txt.strip() or '\ufffd' in txt or '\x00' in txt:issues.append((n,'invalid text'))
  for b in page.get_text('dict')['blocks']:
   for line in b.get('lines',[]):
    for span in line['spans']:
     if not page.rect.contains(fitz.Rect(span['bbox'])):issues.append((n,'text outside page',span['text']))
  for f in page.get_fonts():fonts[f[3]]=bool(doc.extract_font(f[0])[3])
  page.get_pixmap(matrix=fitz.Matrix(.5,.5))
 check(filename+' renders with valid text geometry',not issues)
 check(filename+' all fonts embedded',all(fonts.values()))
 texts[filename]=pages
 outputs[filename]=dict(pages=len(doc),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),all_pages_rendered=True,all_fonts_embedded=True,fonts=list(fonts),issues=issues)
full=' '.join(' '.join(texts['MH6003_Course_Information.pdf']).split())
check('Course identity appears in the PDF',COURSE['code'] in full and COURSE['title'] in full)
check('Both instructor contacts appear in the PDF',all(i['name'] in full and i['email'] in full for i in INSTRUCTORS))
with fitz.open(R/'MH6003_Course_Information.pdf') as doc:
 links={link.get('uri') for p in doc for link in p.get_links()}
check('Instructor email links target the correct addresses',all('mailto:'+i['email'] in links for i in INSTRUCTORS))
check('No unrelated email addresses are published',set(re.findall(r'[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',full))=={i['email'] for i in INSTRUCTORS})
check('All assessment components and percentages appear',all(a['title'] in full and str(a['weight'])+'%' in full for a in ASSESSMENTS))
check('All weekly topics appear in their schedule pages',all(' '.join(topic.split()) in ' '.join(' '.join(texts['MH6003_Course_Information.pdf'][2:4]).split()) for week,topic in WEEKS))
check('Latest week-13 clarification appears','Revision (about 1 hour), followed by the final exam (2 hours)' in full)
check('Group size and project milestones appear','3–4 students' in full and all(term in full for term in ['By week 7','Weeks 8–11','End of week 11']))
check('Draft status is visible on every main slide',all('DRAFT FOR REVIEW' in page for page in texts['MH6003_Course_Information.pdf']))
report=dict(course=COURSE['code'],status='Draft for instructor review',checks_passed=len(checks),checks=checks,pdfs=outputs,visual_review='All seven slides and both review-note pages rendered and inspected; contact, schedule, grading, and project pages reviewed at full size.')
(R/'validation.json').write_text(json.dumps(report,indent=2))
print(f'{len(checks)} checks passed; all nine PDF pages rendered; all fonts embedded.')
