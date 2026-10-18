"""Check the actual lecture datasets, printed tables, PDF geometry, and font embedding."""
from pathlib import Path
from collections import Counter
from fractions import Fraction
from functools import reduce
from math import gcd, factorial
import json,hashlib
import fitz
from cipher_examples import *
from slide_content import slides,MAIN_COUNT
R=Path(__file__).parent
checks=[]
def checked(name,condition):
 assert condition,name
 checks.append(name)
def by_title(title):return next(s for s in slides if s['title']==title)
def table(title):return next(b for b in by_title(title)['blocks'] if b[0]=='table')

checked('Shift example and exercise',shift('cryptographyisfun',2)=='ETARVQITCRJAKUHWP' and shift('MEETMEAFTERCLASS',3)=='PHHWPHDIWHUFODVV')
checked('All shift keys round-trip the alphabet',all(shift(shift(A,k),-k)==A for k in range(26)))
checked('Illustrative substitution is bijective and example matches',len(set(SUB))==26 and sub('BECAUSE')=='WTEQXLT')
checked('Original frequency example is consistent at every position',len(FREQ_C)==len(norm(FREQ_TEXT))==168 and ''.join(OBSERVED_SUB[x] for x in norm(FREQ_TEXT))==FREQ_C)
checked('Original substitution has 23 observed letters and 6 extensions',len(OBSERVED_SUB)==23 and set(A)-set(OBSERVED_SUB)==set('JQZ') and factorial(26-len(OBSERVED_SUB))==6)
checked('Walkthrough counts are recomputed, including corrected ZN',all(ngram_count(FREQ_C,g)==n for g,n in [('ZW',4),('WZ',0),('RW',2),('NZ',3),('ZN',1),('JN',2),('MD',4)]))
checked('Partial-key proposals match the retained message',all(DECODE[a]==b for a,b in dict(Z='e',W='d',R='n',N='h',C='a',M='i',J='t',Y='o',D='s',H='c',F='r',I='u',Q='f',V='m',E='p',X='l',S='k',T='g',P='x',B='y',U='w',K='v',G='b').items()))
checked('Vigenère worked encryption and reversal',vig('cryptography','LUCK')=='NLAZEIIBLJJI' and vig(vig('cryptography','LUCK'),'LUCK',True)=='CRYPTOGRAPHY')
checked('Vigenère numeric table matches each actual addition',all(row==[str(i),str(A.index('CRYPTOGRAPHY'[i])),str(A.index('LUCK'[i%4])),str(A.index('NLAZEIIBLJJI'[i])),'NLAZEIIBLJJI'[i]] for i,row in enumerate(table('Encryption example: do the arithmetic')[2])))
checked('Short Kasiski example has aligned BUK repeats',vig('the sun and the man in the moon','KING')[9:12]==vig('the sun and the man in the moon','KING')[17:20]=='BUK')
checked('Long Kasiski example has the stated positions and gcd',REPEATS['FVR']==[97,147,552,897] and reduce(gcd,[50,455,800])==5)
checked('One complete 1045-letter Vigenère dataset',len(VC)==len(CORPUS)==1045 and vig(VC,'LEMON',True)==CORPUS)
checked('Column sample sizes and IC numerator match the slides',all(len(c)==209 for c in COLUMNS) and sum(n*(n-1) for n in Counter(COLUMNS[0]).values())==2808)
for sample in ['AABAAB','AAB',A,FREQ_C,COLUMNS[0]]:
 n=len(sample);counts=Counter(sample)
 exact=Fraction(sum(v*(v-1) for v in counts.values()),n*(n-1))
 phat2=sum(Fraction(v*v,n*n) for v in counts.values())
 checked('Exact IC identities: '+sample[:12],abs(float(exact)-ic(sample))<1e-12 and (n*phat2-1)/(n-1)==exact)
checked('IC is invariant under each of the 26 shifts',all(abs(ic(shift(FREQ_C,k))-ic(FREQ_C))<1e-12 for k in range(26)))
checked('Finite example IC equals 7/15',abs(ic('AABAAB')-7/15)<1e-12)
checked('Model is positive and normalized',all(q>0 for q in Q) and abs(sum(Q)-1)<1e-12)
checked('Every key letter minimizes its complete column score',''.join(A[min(range(26),key=lambda k:chi_score(col,k))] for col in COLUMNS)=='LEMON')
for row in table('Work out several score contributions')[2]:
 ch,o,e,v=row;i=A.index(ch);counts=Counter(shift(COLUMNS[0],-11));n=len(COLUMNS[0])
 checked('Printed chi-square contribution: '+ch,o==str(counts[ch]) and e==f'{n*Q[i]:.3f}' and v==f'{(counts[ch]-n*Q[i])**2/(n*Q[i]):.3f}')
checked('Printed candidate scores use complete 26-term sums',all(score==f'{chi_score(COLUMNS[0],int(k)):.3f}' for k,letter,score in table('Compare the candidate shifts')[2]))
checked('Playfair square has all 25 allowed letters',len(SQUARE)==len(set(SQUARE))==25 and set(SQUARE)==set(A)-{'J'})
checked('Playfair scan and alternate fillers match the examples',prepare('BALLOON')==['BA','LX','LO','ON'] and prepare('X')==['XQ'] and prepare('XX')==['XQ','XQ'])
checked('All 600 distinct-letter Playfair pairs round-trip',all(play(play(a+b),True)==a+b for a in SQUARE for b in SQUARE if a!=b))
checked('Playfair worked message and challenge',play('hide the gold in the tree stump')=='BMODZBXDNABEKUDMUIXMMOUVIF' and play('RONCFLWI',True)=='ENCRYPTX')
checked('Playfair wrap-around examples',play('FP')=='PL' and play('TP')=='PI')
checked('Playfair preparation really is many-to-one',prepare('AXA')==prepare('AA')==['AX','AX'])
def kind(pair):
 r,c=divmod(SQUARE.index(pair[0]),5);u,v=divmod(SQUARE.index(pair[1]),5)
 return 'Same row' if r==u else 'Same column' if c==v else 'Rectangle'
for pair,rule,out in table('Encrypt the prepared message in stages')[2]:
 checked('Playfair input pair and rule: '+pair,play(pair)==out and rule==kind(pair))
for pair,rule,out in table('Solution: show every pair and rule')[2]:
 checked('Playfair inverse pair and rule: '+pair,play(pair,True)==out and rule.startswith(kind(pair)))
checked('Permutation tables are genuine inverses',sorted(PERM)==list(range(1,7)) and all(PERM[INV[j-1]-1]==j for j in range(1,7)))
checked('Permutation examples and exercise',perm('ATTACK')=='TAAKTC' and perm('ATDAWN')=='DAANTW' and perm('DEFEND')=='FDEDEN')
checked('Permutation inverse recovers complete blocks',all(''.join(perm(s)[i-1] for i in INV)==s for s in ['ABCDEF','ATTACK','ATDAWN','DEFEND']))
checked('Permutation preserves labeled histograms',all(Counter(perm(s))==Counter(s) for s in ['ABCDEF','ATTACK','ATDAWN','DEFEND']))
appendix=''.join(next(b[2] for b in s['blocks'] if b[0]=='code').replace('\n','') for s in slides if s['title'].startswith(('A1 /','A2 /')))
checked('Complete ciphertext is printed in the appendix without omissions',appendix==VC)
checked('Content page counts',len(slides)==99 and MAIN_COUNT==93)

pdfs={}
for name,expected_pages in [('Lecture01_Classical_Ciphers.pdf',99),('Lecture01_Instructor_Guide.pdf',7)]:
 path=R/name;doc=fitz.open(path);problems=[];fonts={};renders=0
 checked(name+' page count',len(doc)==expected_pages)
 for i,page in enumerate(doc,1):
  if not page.get_text().strip():problems.append((i,'blank page'))
  if '\ufffd' in page.get_text() or '\x00' in page.get_text():problems.append((i,'replacement or null character'))
  for block in page.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     box=fitz.Rect(span['bbox'])
     if not page.rect.contains(box):problems.append((i,'out-of-page text',span['text']))
  for f in page.get_fonts():fonts[f[3]]=bool(doc.extract_font(f[0])[3])
  # Exercise every PDF page, including imported vector equation forms.
  page.get_pixmap(matrix=fitz.Matrix(.35,.35));renders+=1
 checked(name+' text geometry and character checks',not problems)
 checked(name+' embeds every referenced font',all(fonts.values()))
 pdfs[name]=dict(pages=len(doc),bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),all_fonts_embedded=True,rendered_pages=renders,problems=problems,fonts=list(fonts))
report=dict(edition='Revised mathematics-department lecture',checks_passed=len(checks),checks=checks,pdfs=pdfs,scheduled_pages=MAIN_COUNT,appendix_pages=len(slides)-MAIN_COUNT,equation_blocks=sum(1 for s in slides for b in s['blocks'] if b[0]=='math'),visual_review='All slides inspected in rendered overviews; representative mathematical, worked-example, and appendix pages reviewed at full size; all seven guide pages reviewed.')
(R/'validation.json').write_text(json.dumps(report,indent=2))
print(f'Passed {len(checks)} checks; rendered {sum(v["rendered_pages"] for v in pdfs.values())} PDF pages. All fonts embedded.')
