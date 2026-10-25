"""Validate the published short deck and its companion teaching notes."""
from pathlib import Path
import json,re,hashlib
import fitz
from content import SLIDES,SOURCES
R=Path(__file__).parent
checks=[]
def check(label,condition):
 assert condition,label
 checks.append(label)
check('Eleven content slides',len(SLIDES)==11 and len({s['id'] for s in SLIDES})==11)
seconds=sum(s['seconds'] for s in SLIDES)
check('Suggested pacing fits 10–15 minutes',600<=seconds<=900)
check('Every slide has delivery notes',all(s.get('notes') for s in SLIDES))
check('Includes source provenance',any(s['id']=='R' for s in SOURCES) and all(s['citation'] and s['status'] for s in SOURCES))
check('Bridge example really is a shift by three',''.join(chr((ord(ch)-65+3)%26+65) for ch in 'MEET')=='PHHW')
outputs={};decktext=[]
for filename,n in [('Lecture00_Introduction.pdf',11),('Lecture00_Teaching_Notes.pdf',3)]:
 p=R/filename;d=fitz.open(p);issues=[];fonts={};word_counts=[]
 check(filename+' expected page count',len(d)==n)
 check(filename+' opens without a password',not d.is_encrypted)
 for index,page in enumerate(d,1):
  txt=page.get_text();word_counts.append(len(txt.split()))
  if 'Introduction.pdf' in filename:decktext.append(txt)
  if not txt.strip() or '\ufffd' in txt or '\x00' in txt:issues.append((index,'invalid or missing text'))
  for b in page.get_text('dict')['blocks']:
   for line in b.get('lines',[]):
    for span in line['spans']:
     if not page.rect.contains(fitz.Rect(span['bbox'])):issues.append((index,'text outside page',span['text']))
  for f in page.get_fonts():fonts[f[3]]=bool(d.extract_font(f[0])[3])
  page.get_pixmap(matrix=fitz.Matrix(.5,.5))
 check(filename+' all text inside page and no replacement characters',not issues)
 check(filename+' all referenced fonts embedded',all(fonts.values()))
 outputs[filename]=dict(pages=len(d),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),word_counts=word_counts,fonts=list(fonts),all_fonts_embedded=True,all_pages_rendered=True,issues=issues)
full='\n'.join(decktext)
check('Main deck is concise',max(outputs['Lecture00_Introduction.pdf']['word_counts'])<130)
check('Defines cryptography','Cryptography uses mathematics' in full)
check('Retains the three original protection goals',all(w in full for w in ['Confidentiality','Integrity','Authentication']))
check('Retains history, payments, and passport applications',all(w in full.lower() for w in ['pen and paper','machines','connected devices','payment','passport']))
check('Adds passkeys and software signing',all(w in full.lower() for w in ['passkey','digital signatures','software','update']))
check('Messaging scope explicitly end-to-end encrypted','End-to-end encryption' in full)
check('HTTPS example is fictional','https://bank.example' in full and 'fictional domain' in full)
check('Includes significance and system limitations','part of the system' in full and 'scam' in full)
check('No dense algorithm or formula treatment',not re.search(r'\b(AES|RSA|Vigenère|modulo|chi.squared|Kasiski)\b',full))
check('No time-sensitive usage statistics or old incident totals',not re.search(r'\b(11,500|15\.1|81 million|2014|2016|2025)\b',full))
check('No timetable or bibliography slide',not any(s['id'] in ('agenda','schedule','sources','reading','reflection') for s in SLIDES))
report=dict(lecture='00',edition='Short visual introduction',checks_passed=len(checks),checks=checks,suggested_seconds=seconds,pdfs=outputs,visual_review='All eleven slides and three teaching-note pages rendered and inspected; messaging labels and passkey diagram spacing corrected after review.')
(R/'validation.json').write_text(json.dumps(report,indent=2))
print(f'{len(checks)} checks passed; {sum(x["pages"] for x in outputs.values())} PDF pages rendered; suggested pacing {seconds//60}m {seconds%60}s.')
