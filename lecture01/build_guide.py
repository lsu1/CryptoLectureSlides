from pathlib import Path
from xml.sax.saxutils import escape
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
R=Path(__file__).parent
for n,f in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf'),('Italic','DejaVuSans-Oblique.ttf')]:pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Italic',boldItalic='Bold')
navy=colors.HexColor('#132B3C');teal=colors.HexColor('#087E83')
styles={
 'title':ParagraphStyle('title',fontName='Bold',fontSize=23,leading=30,textColor=navy,spaceAfter=14),
 'h':ParagraphStyle('h',fontName='Bold',fontSize=13,leading=19,textColor=teal,spaceBefore=10,spaceAfter=7),
 'p':ParagraphStyle('p',fontName='Sans',fontSize=10,leading=14,textColor=navy,spaceAfter=8),
 'small':ParagraphStyle('small',fontName='Sans',fontSize=9,leading=13,textColor=navy,spaceAfter=8),
 'mono':ParagraphStyle('mono',fontName='Mono',fontSize=9,leading=14,textColor=navy,spaceAfter=10)}
story=[]
def p(s,style='p'):story.append(Paragraph(s,styles[style]))
def h(s):p(s,'h')
def page(title):
 if story:story.append(PageBreak())
 p(title,'title')
def table(headers,rows,widths):
 data=[[Paragraph(escape(str(v)),ParagraphStyle('t',parent=styles['small'],textColor=colors.white if i==0 else navy,fontName='Bold' if i==0 else 'Sans')) for v in row] for i,row in enumerate([headers]+rows)]
 t=Table(data,colWidths=widths,hAlign='LEFT');t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Sans'),('BACKGROUND',(0,0),(-1,0),navy),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#E5EEED'),colors.HexColor('#F4F5F1')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]));story.append(t);story.append(Spacer(1,8))
from slide_content import slides,MAIN_COUNT
from cipher_examples import *
from collections import defaultdict
index={s['title']:i+1 for i,s in enumerate(slides)}
sections=defaultdict(list)
for i,s in enumerate(slides,1):sections[s['section']].append(i)
def slide_range(section):return f'{min(sections[section])}–{max(sections[section])}'
def ref(title):return str(index[title])
page('Instructor guide / revised edition')
p(f'Classical ciphers • Mathematics master’s students new to cryptography • {MAIN_COUNT} teaching slides + six appendix pages • 180 minutes including two breaks')
h('Pacing plan')
table(['Elapsed time','Slides','Focus'],[
['00–16',slide_range('FOUNDATIONS'),'Communication problem, vocabulary, symmetric keys, mathematical model'],['16–25',slide_range('SHIFT'),'Definition, inverse calculation, worked shift, 2-minute exercise'],['25–30',slide_range('SUBSTITUTION'),'Alphabet bijections, example, key count'],['30–60',slide_range('FREQUENCY ANALYSIS'),'Original 168-letter example, eleven explicit recovery stages'],['60–70',slide_range('BREAK 01'),'Break'],['70–120',slide_range('VIGENÈRE'),'Worked encryption; Kasiski; IC derivation; complete key recovery'],['120–130',slide_range('BREAK 02'),'Break'],['130–158',slide_range('PLAYFAIR'),'Square construction, preparation, separate pair rules, 3-minute exercise'],['158–172',slide_range('TRANSPOSITION'),'Formal definition, forward and inverse tables, 2-minute exercise'],['172–180',f"{min(sections['SYNTHESIS'])}–{max(sections['REFERENCES'])}",'Comparison, 3-minute reflection, reading']],[78,55,366])
h('How to use the expanded deck')
p('The added slides reveal intermediate states. A partial substitution row or one arithmetic table may take less than a minute; the IC derivation and discussion need longer. Do not allocate equal time to every page. The appendix is supporting data, not additional scheduled lecture content.')
p('For a slower class, shorten the three calculation pauses and give the closing questions as an exit task. Preserve the worked reasoning: do not replace the frequency walkthrough or IC derivation with just their final results.')
page('Foundations, shift, and substitution')
h('A gentle introduction, then mathematical language')
p('Begin with Alice, Bob, and Eve and an ordinary plaintext message. Establish plaintext, ciphertext, algorithm, and key before formal notation. Cryptography has several goals; this lecture focuses on confidentiality. Assume a shared secret and postpone how it is distributed.')
p('Introduce plaintext, ciphertext, and key spaces as sets. Eₖ maps plaintext to ciphertext; Dₖ reverses that choice of transformation. Ask students to explain why Dₖ(Eₖ(p)) = p is a correctness condition, rather than a security claim.')
h('Alphabet and indexing conventions')
p('Use A = 0 through Z = 25 and representatives 0–25 for residues modulo 26. Message positions start at 0 in the shift and Vigenère sections. Permutation tables later use positions 1 through m explicitly. Normalization removes spaces and punctuation; a cipher cannot reconstruct information discarded before encryption.')
h('Shift: work the example before the complete row')
p('With key 2, C (2) → E (4), R (17) → T (19), Y (24) → A (0), and P (15) → R (17). The full CRYPTOGRAPHYISFUN result is ETARVQITCRJAKUHWP. Check A → Y under decryption by subtracting 2 modulo 26.')
p('The exercise PHHWPHDIWHUFODVV decrypts to MEETMEAFTERCLASS at key 3. If M maps to P, the key is (15 − 12) mod 26 = 3. A short readable candidate is evidence; extremely short messages may have several plausible readings.')
h('Substitution: demonstrate the inverse explicitly')
p('The illustrative QWERTY alphabet maps BECAUSE to WTEQXLT. To reverse W, locate it in the output row and read B above it. An alphabet bijection supplies unique inverses. There are 26! keys, but equality patterns and occurrence counts survive under relabeling.')
p('The later 168-letter attack uses a different unknown key. The known illustrative table is not a key for that attack. Trying all 26! keys at one billion trials per second takes about 12.8 billion years; the reference to 88.4 bits concerns key-space size, not demonstrated security.')
page('Frequency attack / the original example')
p(f"Slides {slide_range('FREQUENCY ANALYSIS')} reuse the reference’s 168-letter message. The eleven stages distinguish contextual guesses from consequences of a retained bijection hypothesis. Ciphertext is uppercase; partial plaintext is lowercase; a middle dot is unknown.")
table(['Stage','Reasoning and provisional additions'],[
['1–2','Z occurs 20/168 times; test Z → e. M is also common at 16/168.'],['3','ZW occurs 4 times, WZ zero times, and W has count 8. Test W → d using these combined clues.'],['4','RW occurs twice and becomes ?d. Candidates nd and ed suggest R → n when e is already assigned to Z.'],['5','NZ occurs 3 times and ZN once. Test N → h; HE fits the language model.'],['6','RZCRWNZ reads ne·ndhe. Testing C → a gives neandhe.'],['7','RNM becomes nh· and CM becomes a·. Test the vowel hypothesis M → i.'],['8','JN becomes ·h; test J → t and inspect every occurrence.'],['9','Context suggests Y → o and D → s. HNCMF becomes ·hai·, suggesting H → c and F → r.'],['10','our friend / from Paris / looking add I → u, Q → f, V → m, E → p, X → l, S → k, T → g.'],['11','examined / empty / with / evaporation / back add P → x, B → y, U → w, K → v, G → b.']],[55,444])
h('A verified correction to the reference')
p('The actual ciphertext contains ZN once. The reference’s walkthrough says it is absent. The revised table uses the measured count. More generally, missing pairs in short texts are evidence for ranking guesses, not proof that a mapping is impossible.')
h('A mathematical endpoint')
p('Exactly 23 plaintext letters occur. J, Q, and Z are absent. The recovered partial bijection can therefore extend to 3! = 6 full substitution keys, even though the message itself is readable. This separates recovering a message from uniquely recovering every entry of a key.')
page('Vigenère / encryption, period, and IC')
h('Encryption is position-dependent modular addition')
p('Repeat LUCK below CRYPTOGRAPHY. The first six numeric sums produce NLAZEI; the full result is NLAZEIIBLJJI. R at positions 1 and 7 encrypts to L and B because its aligned key letters differ. Decryption subtracts the same aligned residue.')
h('Kasiski: separate the explanatory example and the attack dataset')
p('In THESUNANDTHEMANINTHEMOON with KING, THE at positions 9 and 17 has the same alignment, so both occurrences encrypt to BUK. The distance 8 is divisible by 4. This short example explains the mechanism.')
p('The subsequent attack consistently uses one 1,045-letter ciphertext, printed in full in Appendix A1–A2. In it, FVR begins at zero-based positions 97, 147, 552, and 897. Distances from the first occurrence are 50, 455, 800; their gcd is 5. Factors 1 and 5 are candidates, subject to chance repeats.')
h('Derive IC before using its reference values')
p('There are N(N − 1) ordered pairs of distinct positions. If a letter occurs f times, it supplies f(f − 1) matching ordered pairs. Summing across letters and dividing gives the exact finite-sample IC. For AABAAB, the numerator is 4·3 + 2·1 = 14 and the denominator is 6·5 = 30, giving 7/15.')
p('For independent letter probabilities q, matching two positions has probability equal to the sum of q². Uniform independent letters give 1/26. English prose often has IC near 0.065, but corpus dependence and position dependence should remain explicit. A fixed alphabet permutation preserves empirical IC exactly.')
h('Inspect individual columns')
vals=', '.join(f'{ic(col):.4f}' for col in COLUMNS)
p('At period 5, the five column IC values are '+vals+'. Each column has 209 letters. The first column has matching-pair numerator 2,808 and denominator 209·208. A period of 10 can also appear plausible because it separates the same aligned shifts into smaller samples.')
p('Ask students why the average alone is insufficient. Some candidate splits could average to a plausible value while individual columns disagree. Use the per-column values in the slide table.')
page('Vigenère / recover and validate the key')
h('Show what happens in one real column')
p('The first ciphertext column’s most frequent symbol is P, appearing 27 times. If it is shifted E, k₀ = (15 − 4) mod 26 = 11. The decrypted column is every fifth plaintext letter; lack of continuous readable words does not reject the key.')
h('Compute and compare a full frequency score')
p('For each candidate shift, count the 26 decrypted symbols. Expected counts are 209 times the corresponding English model probabilities. Sum (observed − expected)² / expected over all letters. The illustrative frequency model is normalized to sum to 1 and printed in Appendix A4.')
col=COLUMNS[0];obs=Counter(shift(col,-11));n=len(col)
table(['Letter','Observed','Expected','Contribution'],[[ch,str(obs[ch]),f'{n*Q[A.index(ch)]:.3f}',f'{(obs[ch]-n*Q[A.index(ch)])**2/(n*Q[A.index(ch)]):.3f}'] for ch in 'ENAZ'],[100,110,140,149])
p(f'The complete 26-term score at shift 11 is {chi_score(col,11):.3f}. Selected terms are shown above; the displayed four contributions are not the whole sum. Shift 11 wins among all 26 candidates for this column.')
table(['Column','Best shift','Letter','Full score'],[[str(j),str(recover(c)),A[recover(c)],f'{chi_score(c,recover(c)):.3f}'] for j,c in enumerate(COLUMNS)],[100,110,140,149])
p('The candidate key is LEMON. Decrypt the complete interleaved ciphertext: it begins THEHISTORYOFSECRETWRITINGISALSOAHISTORY… . Appendix A5–A6 gives the complete prose, with editorially reconstructed spaces and punctuation.')
h('Interpretation, not an overstated guarantee')
p('Language scores rank hypotheses. They do not prove a key correct, and they can fail on short or unusual text. Re-encryption checks consistency with the candidate transformation; by itself it cannot identify a correct key, since any invertible candidate can round-trip its own decryption. Coherent full-message plaintext supplies further evidence.')
page('Playfair and transposition')
h('Playfair: build and prepare before transforming')
p('Construct PLAYF / IREXM / BCDGH / KNOQS / TUVWZ from PLAYFAIR EXAMPLE. The two-stage square slide shows the keyword placement and completion separately. I and J share a cell. BALLOON scans as BA, then LX, then LO, then ON; the second L is reconsidered after the filler is inserted.')
p('Use X as the default filler and Q when the current letter is X. Thus X prepares to XQ and XX to XQ XQ. This explicit convention handles an otherwise ambiguous edge case; implementations may choose another alternate.')
h('Separate the three geometric rules')
p('Same row: PL → LA; wrapping FP → PL. Same column: PI → IB; wrapping TP → PI. Rectangle: H at (3,5) becomes B at (3,1), and I at (2,1) becomes M at (2,5), so HI → BM. Shading identifies the input pair.')
p('For the gold example, the first pairs are HI→BM by rectangle, DE→OD by column, TH→ZB by rectangle, EG→XD by rectangle. Walk through these before revealing the complete prepared and encrypted rows.')
h('Playfair exercise and interpretation')
p('RO→EN by rectangle; NC→CR by column-up; FL→YP by row-left; WI→TX by rectangle. The prepared plaintext is ENCRYPTX; ENCRYPT is the intended reading after interpreting padding. AXA and AA both prepare to AXAX, proving that preparation can be many-to-one. Exact I/J spelling and genuine X letters cannot always be reconstructed.')
h('Transposition: direction and inverse')
p('Encryption reads input positions [3, 1, 4, 6, 2, 5]; decryption reads the inverse [2, 5, 1, 3, 6, 4]. ATTACK→TAAKTC; ATDAWN→DAANTW. The exercise is DEFEND→FDEDEN→DEFEND. There are 6! = 720 keys at this block size. Labeled letter counts are unchanged.')
p('Have students derive the inverse by asking where each original input position went. The correctness argument composes the permutation with its inverse. For incomplete blocks, retain the true message length separately from X padding.')
page('Revision notes, reflection, and reproducibility')
h('Closing reflection: expected reasoning')
p('An inverse is required because distinct plaintexts must not collide under the retained substitution key. In the frequency attack, excluding R→e once Z→e is retained uses injectivity; guessing Z→e initially uses language statistics. The IC denominator counts ordered distinct pairs. A fixed shift preserves the counts under relabeling. Periods 5 and 10 can both isolate fixed shifts, but the latter uses shorter samples.')
h('What this revision changes')
p('Restores a problem-first introduction before attacker terminology, then introduces explicit message/key spaces, encryption and decryption maps, and correctness. Restores the reference’s 168-letter substitution example with eleven visible recovery stages. Replaces the first draft’s highly repetitive teaching text.')
p('Adds the exact finite-sample IC derivation and its relationship to probability models; individual column IC values; actual Kasiski distances from the long dataset; selected score contributions; competing full scores; and all five recovered shifts. Makes the supporting data available within the PDF.')
p('Separates Playfair square construction and geometric rules, explains pair preparation as a scan, and expands the block-permutation inverse argument. Preserves the five-cipher scope, consistent design, selected calculation pauses, and explicit treatment of uncertainty. No new cipher algorithm or unverified current-news story is introduced.')
h('Build and check')
p('Requirements: Python 3 with ReportLab and PyMuPDF; DejaVu Sans and Sans Mono font files; pdflatex with amsmath, amssymb, Latin Modern, xcolor, and geometry. Equations are typeset once into cropped vector PDF pages. LaTeX shell escape is disabled.')
p('Run python build_lecture.py, then python build_guide.py, then python validate.py from the lecture01 directory. slide_content.py is the editable content; cipher_examples.py defines the examples and calculations. The manifest and JSON data are generated outputs. Inspect rendered pages after changes as well as running numerical checks.')
p('The original supplied PDF is cited but is not redistributed. The source bundle contains the editable Python files, generated content/data, and validation report. Previous published versions remain available through Git history.')

def footer(c,d):
 c.setFillColor(teal);c.setFont('Sans',8);c.drawString(48,28,'LECTURE 01 / REVISED INSTRUCTOR GUIDE');c.drawRightString(547,28,str(d.page))
class GuideCanvas(Canvas):
 def __init__(self,*a,**kw):kw['initialFontName']='Sans';super().__init__(*a,**kw)
doc=SimpleDocTemplate(str(R/'Lecture01_Instructor_Guide.pdf'),pagesize=(595,842),leftMargin=48,rightMargin=48,topMargin=44,bottomMargin=48,title='Lecture 01 — Revised Instructor Guide',author='Cryptography lecture series')
doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=GuideCanvas)
print('Revised guide built')
