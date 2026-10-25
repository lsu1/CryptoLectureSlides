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
page('Instructor guide / joint session')
appendix_count=len(slides)-MAIN_COUNT
p(f'Lecture 00 followed by Lecture 01 • 6:30–10:00 pm • {MAIN_COUNT} classical-cipher teaching slides + {appendix_count} optional appendix pages • 210 minutes including two 10-minute breaks')
h('Shared session plan — instructor use only')
table(['Time (pm)','Deck / slides','Focus'],[
['6:30–6:45','Lecture 00: 1–11','Nontechnical orientation; allow responses and handoff'],
['6:45–7:40',f"Lecture 01: {min(sections['FOUNDATIONS'])}–{max(sections['FREQUENCY ANALYSIS'])}",'Foundations, shift, substitution, and frequency analysis'],
['7:40–7:50',f"Lecture 01: {min(sections['BREAK 01'])}",'Break'],
['7:50–8:45',f"Lecture 01: {slide_range('VIGENÈRE')}",'Worked Vigenère encryption, Kasiski, IC, and key recovery'],
['8:45–8:55',f"Lecture 01: {min(sections['BREAK 02'])}",'Break'],
['8:55–9:30',f"Lecture 01: {slide_range('PLAYFAIR')}",'Playfair square, preparation, geometric rules, and exercise'],
['9:30–9:50',f"Lecture 01: {slide_range('TRANSPOSITION')}",'Forward and inverse permutations, calculation, and exercise'],
['9:50–10:00',f"Lecture 01: {slide_range('SYNTHESIS')}",'Compare the constructions, connect to digital messages, and take questions']],[90,110,299])
h('One session, two complementary decks')
p('The 210-minute session contains 190 minutes of teaching. Reserve 15 minutes for Lecture 00, including its suggested 11-minute-45-second delivery and about three minutes for student responses and the handoff. The remaining 175 teaching minutes cover Lecture 01 and questions. Both decks remain separate.')
p('The classical-cipher deck now assumes students have seen the application survey. It removes the repeated Alice-and-Bob motivation, makes cryptanalysis and confidentiality the opening focus, and uses the encryption diagram to introduce notation. Preserve the formal model, vocabulary, examples, and optional appendix.')
h('Use the available time for worked understanding')
p('The allocations include calculation pauses, board annotations, and questions; they are not equal time per page. Keep the five grouped frequency stages and the visual Kasiski/IC explanation. Optional derivations and detailed scoring remain supporting appendix material, rather than extra required lecture content.')
page('Foundations, shift, and substitution')
h('A clear opening')
p('Use the cover subtitle “Historical ciphers and cryptanalysis” to mark the move from Lecture 00’s application survey to construction and analysis. The repeated Alice-and-Bob motivation is removed. Focus the opening on confidentiality and introduce cryptanalysis as the study of how a proposed protection can be defeated under stated assumptions.')
p('Retain plaintext, ciphertext, algorithm, and key as precise vocabulary. The shortened communication diagram introduces p, c, Eₖ, and Dₖ. Explain that today’s five hand ciphers assume a shared secret; Lecture 00’s browser example allowed a protected connection without a previously shared secret. Key distribution is assumed solved here.')
p('Then introduce plaintext, ciphertext, and key spaces as sets. Eₖ maps plaintext to ciphertext; Dₖ reverses the chosen transformation. Dₖ(Eₖ(p)) = p is a correctness condition, not a security claim.')
h('Alphabet and indexing conventions')
p('Use A = 0 through Z = 25 and representatives 0–25 for residues modulo 26. Message positions start at 0 in the shift and Vigenère sections. Permutation tables later use positions 1 through m explicitly. Removing spaces and punctuation is preprocessing and can discard information.')
h('Shift: calculate, then recognize the answer')
p('With key 2, C (2) → E (4), R (17) → T (19), Y (24) → A (0), and P (15) → R (17). The complete CRYPTOGRAPHYISFUN result is ETARVQITCRJAKUHWP. Reverse A → Y by subtracting 2 modulo 26.')
p('For intercepted KHOORZRUOG, show trials 1, 2, and 3 only. Key 3 produces HELLOWORLD, so stop the worked search there. The mathematical key space still contains 26 candidates; there is no need to display a subsequent key after this plausible solution.')
p('The exercise PHHWPHDIWHUFODVV decrypts to MEETMEAFTERCLASS at key 3. Known plaintext M → P gives (15 − 12) mod 26 = 3. Very short strings can have several plausible readings; this example is intentionally recognizable.')
h('Explain σ before using it')
p('S₂₆ is the set of all alphabet permutations. The chosen secret key σ is one particular member of that set: it assigns each plaintext symbol exactly one distinct ciphertext symbol. Its inverse σ⁻¹ follows the same table in reverse for decryption. The inverse identity explains why the original symbol is recovered.')
p('The illustrative QWERTY alphabet maps BECAUSE to WTEQXLT. To reverse W, locate it in the output row and read B above it. The later 168-letter attack uses a different unknown key. There are 26! keys, but equality patterns and counts survive; key-space size alone does not establish security.')
page('Frequency analysis / five representative stages')
p(f"Slides {slide_range('FREQUENCY ANALYSIS')} retain the original 168-letter message while combining repetitive guesses. Ciphertext is uppercase; partial plaintext is lowercase; a middle dot marks an unknown letter. Work one or two representative hypotheses carefully, then group the similar continuations.")
table(['Stage','Main reasoning'],[
['1. Count','Z occurs 20/168 times. Test Z → e while leaving other common symbols open.'],
['2. Pair clues','ZW occurs 4 times, WZ zero times, RW twice, NZ three times, and ZN once. Together with injectivity and language clues, test W → d, R → n, and N → h.'],
['3. Partial text','RZCRWNZ gives ne·ndhe, suggesting C → a. RNM gives nh· and CM gives a·; test M → i. Apply the resulting key to the whole text.'],
['4. Word patterns','JN suggests th, the emerging context suggests o, and MD suggests is. HNCMF then suggests chair. Group these similar tests rather than repeating the complete procedure for every letter.'],
['5. Complete','Use familiar fragments such as our friend, from Paris, looking, examined, and evaporation to summarize the remaining recovery. Check all proposed mappings globally.']],[86,413])
h('Keep evidence and logical constraints distinct')
p('Choosing Z → e is a statistical guess. Excluding R → e after retaining Z → e uses the bijection constraint. Other word completions remain hypotheses until they are consistent with the whole ciphertext. Do not treat a missing pair in a short text as proof of impossibility.')
p('The verified ciphertext has one ZN occurrence. The original reference says zero; the deck uses the recomputed count. This correction does not require spending lecture time reconstructing the old error.')
h('Reveal the full message after a visible partial solution')
p('Our friend from Paris examined his empty glass with surprise, as if evaporation had taken place while he wasn’t looking. I poured some more wine and he settled back in his chair, face tilted up towards the sun.')
p('Exactly 23 plaintext letters occur. J, Q, and Z are absent; 3! = 6 full substitution keys can extend the recovered partial key. The message can be readable even when the complete key is not uniquely determined.')
page('Vigenère / explain the attack through examples')
h('First work the encryption')
p('Repeat LUCK below CRYPTOGRAPHY. The first six sums produce NLAZEI; the full result is NLAZEIIBLJJI. R at positions 1 and 7 encrypts to L and B because its aligned key letters differ. Decryption subtracts the same aligned residue.')
h('See the repetition before calculating a period')
p('In THESUNANDTHEMANINTHEMOON with KING, highlight THE at positions 9 and 17, the aligned key letters, and the two BUK outputs. The marked distance is 8, divisible by period 4. THE at position 0 has a different alignment.')
p('The longer attack uses one 1,045-letter ciphertext, printed in Appendix A1–A2. FVR starts at positions 97, 147, 552, and 897; distances from the first occurrence are 50, 455, 800. Their gcd is 5. These are candidate-period clues, not a guarantee.')
h('Define index of coincidence before abbreviating it')
p('<b>Index of coincidence (IC)</b> is the probability that two randomly chosen, distinct positions contain the same letter. In AAB, the three unordered pairs are AA, AB, and AB: one matches, giving IC = 1/3. Ordered counting gives the same rate; the longer derivation belongs to the appendix.')
p('For longer texts, uniform independent letters have expected IC about 0.0385; ordinary English prose often has a value near 0.065. Uneven letter frequencies cause more matching pairs. IC measures this match rate, not general cryptographic security. Show the exact count formula only after this intuition.')
h('Use the coloured columns to explain the check')
p('Lay out the ciphertext in rows of five and colour each column consistently. If the period is 5, each column shares one shift. The first five rows are ELQVV / DXAFL / ZJESP / CIFKE / TXUBT. Read down a column, not across it.')
vals=', '.join(f'{ic(col):.4f}' for col in COLUMNS)
p('Period 1 gives IC 0.0429. At period 5, the five column values are '+vals+'. Each column has 209 letters. A period of 10 can also look plausible because it divides the same aligned shifts into smaller samples; avoid claiming a unique answer from IC alone.')
h('Recover one shift visually, then summarize')
p('The first column contains P 27 times. If P represents shifted E, the candidate shift is (15 − 4) mod 26 = 11, or L. Compare the whole trial-decrypted histogram against the English model under shifts 0 and 11. The column itself is every fifth plaintext letter and will not form continuous words.')
p('Summarize the remaining shifts as 11, 4, 12, 14, 13 → LEMON. Decrypting the complete interleaved message gives THEHISTORYOFSECRETWRITING… . Appendix A5–A6 contains the complete prose. Detailed numerical scoring remains optional appendix material.')
page('Playfair and transposition')
h('Playfair: build and prepare before transforming')
p('Construct PLAYF / IREXM / BCDGH / KNOQS / TUVWZ from PLAYFAIR EXAMPLE. The two-stage diagram separates keyword placement from completion. I and J share a cell. BALLOON scans as BA, LX, LO, ON; reconsider the second L after inserting the filler.')
p('Use X as the default filler and Q when the current letter is X. Thus X becomes XQ and XX becomes XQ XQ. This explicit convention handles the repeated-X edge case; other implementations may choose a different alternate.')
h('Work the three geometric rules')
p('Same row: PL → LA; wrapping FP → PL. Same column: PI → IB; wrapping TP → PI. Rectangle: H at (3,5) becomes B at (3,1), and I at (2,1) becomes M at (2,5), so HI → BM. Grid shading identifies the input pair.')
p('The first gold-example pairs are HI→BM by rectangle, DE→OD by column, TH→ZB by rectangle, and EG→XD by rectangle. Work these before revealing the complete prepared and encrypted rows.')
h('Playfair exercise and interpretation')
p('RO→EN by rectangle; NC→CR by column-up; FL→YP by row-left; WI→TX by rectangle. The prepared result is ENCRYPTX; ENCRYPT is the intended reading after interpreting padding. AXA and AA both prepare to AXAX, so preparation can be many-to-one. Do not automatically remove every X or assume exact I/J spelling is recoverable.')
h('Transposition: direction before calculation')
p('Encryption reads input positions [3, 1, 4, 6, 2, 5]; decryption reads the inverse [2, 5, 1, 3, 6, 4]. ATTACK→TAAKTC; ATDAWN→DAANTW. The exercise gives DEFEND→FDEDEN→DEFEND. There are 6! = 720 keys at this block size, and labeled letter counts are unchanged.')
p('Construct the inverse by asking where each original input position went. Composing the permutation and its inverse proves correctness. For incomplete blocks, retain the true message length separately from X padding.')
page('Optional depth, reading, and reproducibility')
h('Use the appendix selectively')
p('The complete Vigenère ciphertext, count table, frequency model, and recovered prose support independent study. The longer IC derivation, sample/probability identities, chi-squared score formula, contribution calculations, and candidate-score tables provide optional mathematical depth. The main lecture supplies the intuition and the essential IC formula first.')
p('Language scores rank hypotheses and can fail on short or unusual text. Re-encryption checks consistency with a candidate transformation; it cannot by itself establish that the key is correct. Coherent full-message plaintext supplies further evidence.')
h('Reading and provenance — retained here rather than on a lecture slide')
p('Stinson &amp; Paterson, <i>Cryptography: Theory and Practice</i>, 4th edition, Chapter 1, provides core reading. Section numbering differs across editions. The supplied <i>Lecture02_Classical_Ciphers.pdf</i>, Wu Hongjun, supplies the classical-cipher scope, 168-letter substitution example, and standard Playfair illustration.')
p('Historical reading: Kahn, <i>The Codebreakers</i> (revised edition, 1996); Kerckhoffs, <i>La Cryptographie Militaire</i> (1883); Kasiski (1863). The original uploaded PDF is cited but not redistributed in the source bundle.')
h('This revision and the previous feedback')
p('Retains the approved cover layout and earlier slide removals, stops the worked shift search at key 3, defines σ explicitly, groups substitution reasoning into five stages, and keeps Kasiski/IC visual. The latest cleanup removes overlap with Lecture 00, changes the cover subtitle, and updates the guides and break timings for the 3.5-hour joint session. The same five ciphers and worked examples are retained.')
h('Edit, build, and inspect')
p('Requirements: Python 3 with ReportLab and PyMuPDF; DejaVu Sans and Sans Mono font files; pdflatex with amsmath, amssymb, Latin Modern, xcolor, and geometry. Equations are placed as vector PDF content; LaTeX shell escape is disabled.')
p('Run python build_lecture.py, python build_guide.py, then python validate.py from lecture01. Edit slide_content.py for content, cipher_examples.py for examples, and build_lecture.py for layout. The manifest, numerical data, PDFs, and validation report are generated outputs. Inspect rendered pages after edits as well as running the checks.')
p('The source bundle includes editable files and supporting data. Previous published versions remain accessible through Git history.')

def footer(c,d):
 c.setFillColor(teal);c.setFont('Sans',8);c.drawString(48,28,'LECTURE 01 / INSTRUCTOR GUIDE');c.drawRightString(547,28,str(d.page))
class GuideCanvas(Canvas):
 def __init__(self,*a,**kw):kw['initialFontName']='Sans';super().__init__(*a,**kw)
doc=SimpleDocTemplate(str(R/'Lecture01_Instructor_Guide.pdf'),pagesize=(595,842),leftMargin=48,rightMargin=48,topMargin=44,bottomMargin=48,title='Lecture 01 — Instructor Guide',author='Cryptography lecture series')
doc.build(story,onFirstPage=footer,onLaterPages=footer,canvasmaker=GuideCanvas)
print('Consolidated guide built')
