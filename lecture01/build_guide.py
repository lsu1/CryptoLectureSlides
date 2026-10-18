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
page('Instructor guide / Lecture 01')
p('Classical ciphers • Master’s students in computer science and engineering • 180 minutes including two 10-minute breaks')
h('Pacing plan')
table(['Elapsed time','Slides','Delivery focus'],[
['00–05','1–4','Opening puzzle, goals, route'],['05–20','5–13','History, model, keys, modular arithmetic'],['20–35','14–19','Shift example; 3-minute challenge'],['35–50','20–23','Substitution and preserved patterns'],['50–60','24','Break'],['60–78','25–33','Frequency attack; 4-minute group task'],['78–110','34–47','Vigenère; 3-minute exercise; 3-minute discussion'],['110–120','48','Break'],['120–152','49–62','Playfair; 4-minute and 2-minute tasks'],['152–170','63–68','Transposition; 3-minute task'],['170–180','69–74','Comparison; 4-minute exit questions; wrap-up']],[90,54,355])
h('Delivery')
p('The 74 pages include section dividers, break screens, exercise prompts, and answer slides. These are presentation cues, not 74 equal-length mini-lectures. Keep answer slides hidden until students have attempted each task.')
p('Use a board or shared document for the shift enumeration, partial substitution key, one index-of-coincidence calculation, and one Playfair pair. No live software or Internet access is needed to teach the deck.')
page('Foundations and frequency analysis')
h('Slides 5–13 / establish the model')
p('Ask what the interceptor knows. Separate the public algorithm from the secret key. All examples use a shared secret; key distribution is assumed, not solved. Explain that confidentiality and authenticity are different goals without developing additional algorithms.')
p('Make students compute (0 − 2) mod 26 = 24. Normalization removes spaces and punctuation before encryption. The cipher cannot restore information already discarded by this step.')
h('Slides 14–23 / shift and substitution')
p('The opening intercept PHHWDWQRRQ reads MEETATNOON with K = 3. The shift challenge PHHWPHDIWHUFODVV reads MEETMEAFTERCLASS. Known plaintext M (12) → P (15) gives K = 3 immediately.')
p('For an arbitrary substitution, 26! is about 4.03 × 10²⁶. The 12.8-billion-year estimate assumes one billion full-key trials per second and exhaustive enumeration of the entire key space. It is not an estimate of the cost of the best attack.')
h('Slides 25–33 / recover a partial substitution key')
p('The 123-letter example is deliberately repetitive: T appears 35 times and Z appears 24 times. Do not present its histogram as a typical English distribution. The chart uses plaintext labels to demonstrate the invariant; the following slides switch to ciphertext counts.')
p('Treat ZIT → THE as a hypothesis. ZITLTEKTZ → THESECRET adds L→S, E→C, K→R. Apply each mapping everywhere and reject contradictions. In an actual attack, keep alternative hypotheses rather than declaring guesses proven.')
p('Exercise fragments: DTTZOFU → MEETING, DTLLTFUTK → MESSENGER, STZZTK → LETTER. Example additional mappings: D→M, O→I, U→G, S→L, F→N. All guesses must preserve a one-to-one mapping.')
h('Discussion prompt')
p('Could the full message be readable while some entries of the substitution table remain unknown? Yes: plaintext letters absent from this message impose no direct constraints on their images. Context and one-to-one constraints can help, but the message need not determine every key entry.')
page('Vigenère / make the attack reproducible')
h('Slides 34–40 / the key alignment matters')
p('ATTACKATDAWN with LEMON gives LXFOPVEFRNHR. CRYPTOGRAPHY with LUCK gives NLAZEIIBLJJI; the first six ciphertext letters are NLAZEI. Keep all three rows aligned on the board.')
p('In THESUNANDTHEMANINTHEMOON with KING, THE starts at positions 9 and 17 with the same key alignment, producing BUK twice. The distance is 8, divisible by the period 4. The THE at position 0 has a different alignment.')
p('The Kasiski distance set 30, 45, 75 is explicitly illustrative, not measured from the short KING example. Its gcd is 15. Candidate periods are divisors of 15; accidental repeats and multiples make corroboration necessary.')
h('Slides 41–46 / IC and key recovery')
p('IC counts matching ordered pairs of positions. In AAB, the two A positions generate two matches out of six ordered pairs: IC = 1/3. Independent uniform letters have expected IC 1/26. Typical English IC is only an approximate reference.')
data=json.loads((R/'worked_examples.json').read_text())
table(['Candidate period','Mean column IC'],[[m,f"{sum(vals)/len(vals):.4f}"] for m,vals in data['column_IC'].items()],[180,319])
p('The example contains 1,045 normalized letters of original prose and uses LEMON. For m = 5, recover shifts 11, 4, 12, 14, 13 by scoring all 26 candidates in each column. The result decrypts to THEHISTORYOFSECRETWRITING… .')
p('A period of 10 also gives elevated IC because each column still has one fixed shift. Prefer the shorter supported period, then validate the full decryption. Short or atypical text can mislead both IC and frequency scoring.')
h('Avoid a common misconception')
p('Brute force is not “impossible” merely because the keyword has m letters. With a candidate period, trying 26 shifts per column and using a language score is practical. The full 26ᵐ product is unnecessary for this attack. Independently chosen best columns are still candidates; verify the resulting message.')
page('Playfair / examples and ambiguity')
h('Slides 49–54 / model the preparation separately')
p('Build the square from PLAYFAIR EXAMPLE. Keep the first occurrence of each keyword letter, merge J into I, then append unused letters. Rows: PLAYF / IREXM / BCDGH / KNOQS / TUVWZ.')
p('Preparation is a left-to-right scan, not a global replacement of repeated letters. BALLOON becomes BA LX LO ON, not BA LX LX OO NX. Reconsider the second repeated letter after inserting a filler.')
p('The lecture uses X as the default filler and Q when the current letter is X. Thus X → XQ, and XX → XQ XQ. This is an explicit teaching convention; different implementations can choose different alternates.')
table(['Rule','Worked encryption','Worked decryption'],[['Same row','PL → LA','LA → PL'],['Same column','PI → IB','IB → PI'],['Rectangle','HI → BM','BM → HI']],[140,180,179])
h('Slides 55–59 / worked message and challenges')
p('HIDE THE GOLD IN THE TREE STUMP prepares to:<br/>HI DE TH EG OL DI NT HE TR EX ES TU MP','mono')
p('Ciphertext:<br/>BM OD ZB XD NA BE KU DM UI XM MO UV IF','mono')
p('The retained original challenge RONCFLWI decrypts as RO→EN, NC→CR, FL→YP, WI→TX, giving ENCRYPTX. Removing the final X produces the intended ENCRYPT. Ask which geometric rule applies to each pair.')
p('The second challenge DP YR AN QO decrypts to BA LX LO ON, giving the plausible original word BALLOON. Its answer is printed in the takeaway strip; cover the strip while students work, or use the exercise verbally.')
h('Slides 60–62 / what is and is not reversible')
p('AXA and AA both prepare to AXAX and therefore encrypt identically. Decryption recovers prepared pairs, not necessarily the original spelling. Do not delete all X letters automatically. Merging I/J is another source of lost information.')
p('Hill climbing is a search strategy, not an extra cipher. Describe decrypt → score → modify → accept improvement. Local optima motivate restarts. Re-encryption is a consistency check; for an invertible candidate cipher it is not proof that the recovered key is correct.')
page('Transposition, wrap-up, and reuse')
h('Slides 63–68 / direction before calculation')
p('Use the original deck’s block-permutation convention: the i-th ciphertext letter is the π(i)-th plaintext letter. Positions here are numbered 1 through 6, unlike the zero-based indices used earlier.')
p('π = [3, 1, 4, 6, 2, 5]<br/>π⁻¹ = [2, 5, 1, 3, 6, 4]','mono')
p('ATTACK → TAAKTC; ATDAWN → DAANTW. The exercise DEFEND → FDEDEN. Decrypt by placing each output letter back in its original position, or by reading the inverse order. Every letter count is unchanged. There are 6! = 720 keys for this block size.')
p('Pad incomplete blocks with X and retain the original length separately. Without a length or an unambiguous encoding convention, genuine trailing X letters cannot always be distinguished from padding. Padding is not a source of secrecy.')
h('Slides 69–74 / exit discussion')
p('Exit answers: (1) substitution preserves language statistics; (2) a repeated key creates aligned shift-cipher columns; (3) Playfair preparation adds fillers and merges I/J; (4) transposition preserves the exact labeled letter histogram. A general substitution also preserves the multiset of counts, but relabels them.')
p('The API-credential scenario is fictional and contemporary, not a news report. No unverifiable “latest incident” is presented. Keep the distinction between hiding a representation and protecting access to the underlying secret.')
h('What changed from the supplied lecture')
p('Retained all five ciphers, the attack methods, codebook context, the standard Playfair square and gold example, and the RONCFLWI exercise. Replaced the long frequency-analysis walkthrough with a shorter, reproducible message and group task. Added explicit assumptions, timed activities, answer slides, and preparation/padding caveats.')
p('Refined the Vigenère brute-force discussion, treated IC and frequency clues as statistical evidence, specified permutation direction, and corrected the explanation of ASCII as a 7-bit code commonly stored in bytes. Introductory modern context stays conceptual; no additional cipher algorithm is taught.')
h('Rebuild and adapt')
p('The companion source bundle contains build_lecture.py, build_guide.py, slide_manifest.json, and worked_examples.json. Requirements: Python 3, ReportLab, and DejaVu Sans / Sans Mono font files. Run the lecture builder first, then the guide builder. The JSON file contains the full Vigenère corpus and ciphertext.')
p('The build checks cipher examples, key recovery, inverse permutations, selected statistical values, and layout limits. Final PDFs were also rendered for visual inspection. After editing, rerun the checks and inspect the affected slides again. No external imagery or current-news content requires refreshing.')

def footer(c,d):
 c.setFillColor(teal);c.setFont('Sans',8);c.drawString(48,28,'LECTURE 01 / INSTRUCTOR GUIDE');c.drawRightString(547,28,str(d.page))
class GuideCanvas(Canvas):
 def __init__(self,*a,**kw):kw['initialFontName']='Sans';super().__init__(*a,**kw)
doc=SimpleDocTemplate(str(R/'Lecture01_Instructor_Guide.pdf'),pagesize=(595,842),leftMargin=48,rightMargin=48,topMargin=44,bottomMargin=48,title='Lecture 01 — Instructor Guide',author='Cryptography lecture series')
doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=GuideCanvas)
print('Guide built')
