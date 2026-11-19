"""Build the Lecture 02 teaching companion from the editable slide records."""
from collections import defaultdict
from math import factorial, log2
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

from slide_content import MAIN_COUNT, SESSION_PLAN, slides
from crypto_examples import (
    DES_CIPHERTEXT, DES_KEY, DES_PLAINTEXT, DES_TRACE, DES_KEY_TRACE,
    TOY_CIPHERTEXT, TOY_KEYS, TOY_PLAINTEXT, TOY_TRACE,
)

ROOT = Path(__file__).resolve().parent
FONT_ROOT = Path('/usr/share/fonts/truetype/dejavu')
for name, filename in [
    ('Sans', 'DejaVuSans.ttf'), ('Bold', 'DejaVuSans-Bold.ttf'),
    ('Italic', 'DejaVuSans-Oblique.ttf'), ('Mono', 'DejaVuSansMono.ttf'),
]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_ROOT / filename)))
pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='Bold', italic='Italic', boldItalic='Bold')

NAVY = colors.HexColor('#132B3C')
TEAL = colors.HexColor('#087E83')
MUTED = colors.HexColor('#536875')
LIGHT = colors.HexColor('#E5EEED')
PAPER = colors.HexColor('#F6F4EE')
WIDTH = 499
styles = {
    'title': ParagraphStyle('title', fontName='Bold', fontSize=22, leading=28,
                            textColor=NAVY, spaceAfter=13),
    'h': ParagraphStyle('h', fontName='Bold', fontSize=12.5, leading=17,
                        textColor=TEAL, spaceBefore=11, spaceAfter=6, keepWithNext=True),
    'p': ParagraphStyle('p', fontName='Sans', fontSize=9.6, leading=13.3,
                        textColor=NAVY, spaceAfter=7),
    'small': ParagraphStyle('small', fontName='Sans', fontSize=8.7, leading=12,
                            textColor=NAVY, spaceAfter=6),
    'notehead': ParagraphStyle('notehead', fontName='Bold', fontSize=10.2, leading=13.5,
                               textColor=NAVY, spaceAfter=3),
    'note': ParagraphStyle('note', fontName='Sans', fontSize=9.15, leading=12.3,
                           textColor=NAVY, spaceAfter=6.5),
    'meta': ParagraphStyle('meta', fontName='Sans', fontSize=8, leading=11,
                           textColor=MUTED, spaceAfter=7),
}
# Reference entries retain the notes' type size and leading, with a smaller
# inter-entry gap so the complete appendix index stays together on one page.
styles['appendixhead'] = ParagraphStyle('appendixhead', parent=styles['notehead'], spaceAfter=2)
styles['appendixnote'] = ParagraphStyle('appendixnote', parent=styles['note'], spaceAfter=3)
story = []


def para(text, style='p'):
    return Paragraph(text, styles[style])


def p(text, style='p'):
    story.append(para(text, style))


def h(text):
    p(text, 'h')


def page(title):
    if story:
        story.append(PageBreak())
    p(title, 'title')


def table(headers, rows, widths):
    data = []
    for i, row in enumerate([headers] + rows):
        style = ParagraphStyle(
            'cell', parent=styles['small'], spaceAfter=0,
            textColor=colors.white if i == 0 else NAVY,
            fontName='Bold' if i == 0 else 'Sans',
        )
        data.append([Paragraph(escape(str(value)), style) for value in row])
    result = Table(data, colWidths=widths, hAlign='LEFT', repeatRows=1)
    result.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Sans'),
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT, PAPER]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.extend([result, Spacer(1, 7)])


sections = defaultdict(list)
for number, slide in enumerate(slides[:MAIN_COUNT], 1):
    sections[slide['section']].append(number)
index = {slide['title']: number for number, slide in enumerate(slides, 1)}
appendix_count = len(slides) - MAIN_COUNT
break_count = sum(row['kind'] == 'break' for row in SESSION_PLAN)
teaching_minutes = sum(row['minutes'] for row in SESSION_PLAN if row['kind'] == 'teaching')
session_minutes = sum(row['minutes'] for row in SESSION_PLAN)


def span(numbers):
    return str(numbers[0]) if numbers[0] == numbers[-1] else f'{numbers[0]}–{numbers[-1]}'


def section_span(*names):
    values = sorted(number for name in names for number in sections.get(name, []))
    return span(values) if values else 'See slide index'


def pace(minutes):
    seconds = max(5, round(minutes * 60 / 5) * 5)
    whole, remainder = divmod(seconds, 60)
    return (f'{whole} min' if whole else '') + (f' {remainder} sec' if remainder else '')


page('Lecture 02 / instructor guide')
p(f'One-time pads &amp; block ciphers • {MAIN_COUNT} main pages, including {break_count} break pages, '
  f'plus {appendix_count} optional appendix pages. '
  f'The 6:30–10:00 pm session contains {teaching_minutes} teaching minutes and '
  f'{session_minutes - teaching_minutes} minutes of breaks.')
h('Session plan')
table(['Time', 'Slides', 'Focus'], [
    [f"{row['start']}–{row['end']}", span(row['slides']), row['label']]
    for row in SESSION_PLAN
], [117, 48, 334])
h('Teach calculations and assumptions together')
p('The audience has already seen classical ciphers. Begin with the repeating-key weakness, then use '
  'the letter pad and XOR exercise to establish the construction before introducing probability. '
  'Keep the complete perfect-secrecy proof in the main lecture: each page supplies one step, '
  'and a biased prior checks what the theorem actually says.')
p('The middle block turns from an exact distributional guarantee to computational security. '
  'Use the specified toy SPN to make substitution, wiring, and reversibility concrete. '
  'Feistel then prepares students to follow one real DES round without treating the inner function '
  'as an invertible cipher.')
p('The final block first follows the same DES test vector through a complete first round: '
  'IP and input halves, expansion, key XOR, the actual S-box groups, permutation P, and the round output. '
  'The next pages derive the supplied round key, then return to the remaining rounds, final swap, and ciphertext. '
  'The lecture then compares exhaustive search and meet-in-the-middle. The allocations include board work, '
  'student calculations, and questions. The optional tables and entropy bound support follow-up; '
  'they are not extra required material to fit before 10:00 pm.')
h('Coverage of the supplied references')
table(['Supplied deck / original pages', 'Coverage in this deck'], [
    ['Lecture03_OneTimePad.pdf: 4–16, 18–27, 29–34',
     f"Slides {section_span('ONE-TIME PAD', 'PROBABILITY', 'PERFECT SECRECY', 'INFORMATION THEORY')}: "
     'pad construction, examples, reuse, probability, proof, entropy, redundancy, and unicity. '
     'The conditional-entropy key bound is in the appendix.'],
    ['Lecture04_Block_Cipher_Introduction.pdf: 6–10, 12–16, 18–25',
     f"Slides {section_span('BLOCK CIPHERS')}: security models, search costs, attack information, "
     'public design, permutations, rounds, SPN, and key scheduling.'],
    ['Lecture05_Block_Cipher_DES.pdf: 5, 7–10, 12–25',
     f"Slides {section_span('FEISTEL', 'FEISTEL NETWORKS', 'DES', 'MULTIPLE ENCRYPTION')}: "
     'history, Feistel, DES data path and keys, key-size limits, Double DES, and Triple DES. '
     'Full lookup tables are optional appendix material.'],
], [222, 277])

page('Worked checkpoints and important updates')
first_toy_round = TOY_TRACE['rounds'][0]
first_des_round = DES_TRACE['rounds'][0]
first_des_box = first_des_round['boxes'][0]
first_des_key = DES_KEY_TRACE['rounds'][0]
redundancy = log2(26) - 1.25
table(['Checkpoint', 'Verified answer / interpretation'], [
    ['Letter pad', 'NANYANG + XRTRPLK modulo 26 = KRGPPYQ. N + X gives (13 + 23) mod 26 = 10 = K.'],
    ['Bit pad and reuse', '1010011000 XOR 0110101110 = 1100110110. For the second plaintext 1100001101, '
     'the same pad gives 1010100011; the two ciphertexts XOR to 0110010101, equal to the plaintext XOR.'],
    ['Two fair, independent dice', 'Pr(sum = 4) = 1/12; Pr(double) = 1/6; '
     'Pr(double | sum = 4) = 1/3; Pr(sum = 4 | double) = 1/6. The joint probability is 1/36.'],
    ['Entropy and unicity', f'Coin entropy: 1 bit (fair), about 0.881 bits (p = 0.7), 0 bits (certain). '
     f'With language rate 1.25 bits/letter, redundancy is {redundancy:.4f} bits/letter; '
     f'log₂(26!)/redundancy = {log2(factorial(26))/redundancy:.1f} letters.'],
    ['Toy SPN (hexadecimal)', f'Plaintext {TOY_PLAINTEXT:04X}; keys '
     + ', '.join(f'{key:04X}' for key in TOY_KEYS)
     + f'. First round: XOR {first_toy_round["mixed"]:04X}, S-boxes '
     + f'{first_toy_round["substituted"]:04X}, permutation {first_toy_round["state"]:04X}. '
     + f'Final ciphertext {TOY_CIPHERTEXT:04X}.'],
    ['DES input and first-round setup (hexadecimal)',
     f'P = {DES_PLAINTEXT:016X}; K = {DES_KEY:016X} (parity included). '
     f'IP(P) = {DES_TRACE["post_ip"]:016X}; L₀ = {DES_TRACE["l0"]:08X}, '
     f'R₀ = {DES_TRACE["r0"]:08X}. Use K₁ = {first_des_round["key"]:012X} for the worked round; '
     'its derivation follows the data-path calculation.'],
    ['DES round 1 / actual S-box input',
     f'S₁({first_des_box["input"]:06b}): outer bits 00 give row {first_des_box["row"]}; '
     f'inner bits 1100 give column {first_des_box["column"]}; output '
     f'{first_des_box["output"]:04b} = {first_des_box["output"]}. '
     f'All eight outputs concatenate to {first_des_round["sbox_output"]:08X}; '
     f'permutation P gives F = {first_des_round["f"]:08X}. '
     f'L₁ = {first_des_round["l"]:08X}, R₁ = {first_des_round["r"]:08X}. '
     'Appendix A14 shows every six-bit XOR, row, column, and output.'],
    ['DES round-key derivation',
     f'PC1(K) = {DES_KEY_TRACE["pc1"]:014X}, split as '
     f'C₀ = {DES_KEY_TRACE["c0"]:07X}, D₀ = {DES_KEY_TRACE["d0"]:07X}. '
     f'Rotate each half left by one bit, then apply PC2 to obtain K₁ = {first_des_key["key"]:012X}. '
     'This is the subkey already used in round 1.'],
    ['DES remaining rounds and final output',
     'Rounds 2–16 use the same data-path rule with their respective subkeys. '
     f'Then serialize R₁₆ || L₁₆ = {DES_TRACE["preoutput"]:016X} and apply FP = IP⁻¹. '
     f'The final ciphertext is {DES_CIPHERTEXT:016X}.'],
], [125, 374])
h('Corrections that affect the explanation')
p('<b>Shannon and language:</b> the information-theory paper is from 1948; the secrecy-systems '
  'paper is from 1949. Distinguish single-letter entropy, normalized block entropy, and entropy '
  'rate. The unicity example consistently uses a 1.25-bit/letter rate, giving about 25.6 letters. '
  'This is a statistical heuristic, not a guaranteed break or a runtime estimate.', 'small')
p('<b>Security and public review:</b> perfect secrecy is the exact independence property proved here. '
  'A public algorithm can retain a secret key; independent scrutiny helps evaluation without requiring '
  'attackers to cooperate. Search-rate examples are explicitly hypothetical. GHz and FLOPS do not '
  'measure complete cipher-key trials.', 'small')
p('<b>Design choices and indexing:</b> the reference toy SPN has no numerical lookup tables or keys. '
  'This deck supplies explicit teaching choices and preserves its three S-layers, two P-layers, '
  'and final key XOR. Toy and DES table positions count from 1 at the leftmost bit; DES S-box '
  'row and column values count from 0. Ordinary Feistel rounds are followed by the stated DES '
  'final swap exactly once.', 'small')
p('<b>Contemporary status:</b> DES and Triple DES are historical examples. NIST withdrew '
  'SP 800-67 Rev. 2 effective 1 January 2024; TDEA is no longer approved for applying new '
  'cryptographic protection under NIST guidance. This is a standards status, not a universal legal '
  'ban. Key length, security strength, and block-size data limits are separate questions.', 'small')

page('Slide-by-slide teaching notes')
p('The following notes are generated from the editable slide records. Per-slide allocations '
  'are rounded to five seconds; the session table controls the wall-clock timings. '
  'Keep the worked answers visible only after allowing the corresponding calculation pause.', 'small')


def clean_note(text):
    """Normalize a few compact source-note spellings for print readability."""
    replacements = {
        'mod26': 'mod 26', 'from2to12': 'from 2 to 12',
        'sum4': 'sum 4', 'probability1/6': 'probability 1/6',
        'gives1/6': 'gives 1/6', 'gives2^-n': 'gives 2⁻ⁿ',
        'at1,.8812908992,0': 'at 1, 0.8812908992, and 0',
        'No0.75×4.7': 'No 0.75 × 4.7', 'same1.25-bit': 'same 1.25-bit',
        'as4.19': 'as 4.19', 'rate1.25': 'rate 1.25',
        'with23observedletters/6extensions': 'with 23 observed letters / 6 extensions',
        'lecture’s23observedletters/6extensions': 'lecture’s 23 observed letters / 6 extensions',
        'there are25!': 'there are 25!', 'if r=1': 'if r = 1',
        'probability1/4': 'probability 1/4', 'probability2^-n': 'probability 2⁻ⁿ',
        'to1,': 'to 1,', 'is1/4': 'is 1/4', 'is1949': 'is 1949',
        'limit0': 'limit 0', 'approximately73%': 'approximately 73%',
        'and75%': 'and 75%', 'is25.614692777': 'is 25.614692777',
        '2^-n': '2⁻ⁿ',
    }
    for before, after in replacements.items():
        text = text.replace(before, after)
    return text


previous_section = None
for number, slide in enumerate(slides[:MAIN_COUNT], 1):
    section = slide['section']
    section_heading = []
    if section != previous_section:
        section_heading = [para(escape(section.title()), 'h')]
        previous_section = section
    duration = pace(slide['minutes']).strip()
    heading = f'{number}. {escape(slide["title"])}'
    if duration:
        heading += f' <font color="#536875">/ about {duration}</font>'
    note = clean_note(slide.get('notes') or slide.get('take') or 'Use the displayed example to consolidate the preceding idea.')
    story.append(KeepTogether(section_heading + [para(heading, 'notehead'), para(escape(note), 'note')]))

if appendix_count:
    page('Optional appendix / reference use')
    p(f'The {appendix_count} appendix pages are outside the {teaching_minutes}-minute teaching plan. '
      'Use them to answer a specific question or support independent calculation. The main lecture '
      'includes the OTP proof and a worked DES round. The appendix covers conditional entropy, '
      'provides the full lookup tables, works through both directions of the two-round Feistel example, '
      'and records all eight first-round DES S-box calculations in A14.', 'small')
    for offset, slide in enumerate(slides[MAIN_COUNT:], 1):
        label = f'A{offset}'
        title = slide['title'].split(' / ', 1)[-1]
        note = clean_note(slide.get('notes') or slide.get('take') or 'Reference table for checking the worked calculation.')
        story.append(KeepTogether([
            para(f'{label} <font color="#536875">(PDF page {MAIN_COUNT + offset})</font> / {escape(title)}', 'appendixhead'),
            para(escape(note), 'appendixnote'),
        ]))

page('Reading, provenance, and rebuilding')
h('Teaching references')
p('The supplied Wu Hongjun decks are the scope reference: <i>Lecture03_OneTimePad.pdf</i> '
  '(35 pages), <i>Lecture04_Block_Cipher_Introduction.pdf</i> (26 pages), and '
  '<i>Lecture05_Block_Cipher_DES.pdf</i> (26 pages). The revised lecture preserves their progression '
  'and core topics while adding completed calculations, explicit notation, and a consistent worked '
  'DES trace. Cover, outline, reading, and summary pages are consolidated. The original PDFs are '
  'cited but are not redistributed.')
p('General reading: Stinson &amp; Paterson, <i>Cryptography: Theory and Practice</i>, '
  'information-theory and block-cipher chapters; Menezes, van Oorschot &amp; Vanstone, '
  '<i>Handbook of Applied Cryptography</i>, Chapters 2 and 7. Section numbering varies by edition. '
  'Claude E. Shannon, “A Mathematical Theory of Communication” (1948), and '
  '“Communication Theory of Secrecy Systems” (1949), establish the historical theory.')
p('Historical context: the NSA/CSS VENONA declassified history supports the pad-reuse example. '
  'Kerckhoffs, <i>La Cryptographie Militaire</i> (1883), is the source of the public-design principle. '
  'Published 2008 MIFARE Classic / Crypto1 reverse-engineering research supplies an example of '
  'why hiding a commercial cipher specification is fragile. These are bibliographic references, '
  'rather than a claim that a new literature review was performed for this deck.')
h('Standards references and retrieval status')
p('NIST <b>FIPS 46-3, Data Encryption Standard (DES)</b> (1999; withdrawn 2005) '
  'specifies DES and its tables. NIST <b>SP 800-67 Rev. 2</b> (2017; withdrawn effective '
  '1 January 2024) and <b>SP 800-131A Rev. 2</b> (2019) support the TDEA transition context. '
  'The NIST TDEA project page records the withdrawal. Attempts to retrieve these official '
  'pages and PDFs on 17 November 2026 were blocked by the network proxy (HTTP 403). '
  'They are supplied as bibliographic citations; this package does not claim live retrieval or '
  'a comprehensive statement of every organization’s current migration policy.')
for label, url in [
    ('FIPS 46-3 / DES', 'https://csrc.nist.gov/pubs/fips/46-3/final'),
    ('SP 800-67 Rev. 2 / TDEA', 'https://csrc.nist.gov/pubs/sp/800/67/r2/final'),
    ('SP 800-131A Rev. 2 / transitions', 'https://csrc.nist.gov/pubs/sp/800/131/a/r2/final'),
    ('NIST TDEA project and withdrawal', 'https://csrc.nist.gov/projects/block-cipher-techniques/tdea'),
]:
    p(f'<link href="{url}" color="#087E83">{escape(label)}</link>', 'small')
h('Worked-example provenance')
p('The NANYANG letter pad, ten-bit XOR exercise, dice experiment, and coin-entropy cases '
  'are retained and completed from the reference. The toy SPN lookup values, bit permutation, '
  'plaintext, and round keys are explicit teaching choices because the old figure did not specify '
  'them. They do not define a recommended cipher. The DES plaintext/key/ciphertext vector '
  'is a conventional known-answer example. The round walkthrough uses its actual S₁ input, '
  'and appendix A14 expands all eight lookups. '
  'Its trace is recomputed from the standard tables '
  'and was independently checked, including the ciphertext with OpenSSL.')
h('Edit, build, and inspect')
p('Requirements: Python 3, ReportLab, PyMuPDF, DejaVu Sans / Sans Mono fonts, and '
  'pdflatex with amsmath, amssymb, Latin Modern, xcolor, and geometry. Equations are placed '
  'as vector PDF content with LaTeX shell escape disabled. No Internet connection is needed '
  'to build or present the deck.')
p('Run <b>python build_lecture.py</b>, <b>python build_guide.py</b>, '
  '<b>python validate.py</b>, then <b>python package_source.py</b> from lecture02. '
  'Edit the content modules for exposition, crypto_examples.py for numerical demonstrations, '
  'and slide_content.py for assembly and pacing. The source bundle includes the editable '
  'files and generated review outputs. Inspect rendered pages after edits as well as running '
  'the numerical and layout checks.')


def footer(canvas, doc):
    canvas.setFillColor(TEAL)
    canvas.setFont('Sans', 8)
    canvas.drawString(48, 28, 'LECTURE 02 / INSTRUCTOR GUIDE')
    canvas.drawRightString(547, 28, str(doc.page))


class GuideCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        kwargs['initialFontName'] = 'Sans'
        super().__init__(*args, **kwargs)


if __name__ == '__main__':
    document = SimpleDocTemplate(
        str(ROOT / 'Lecture02_Instructor_Guide.pdf'), pagesize=(595, 842),
        # Frame padding is 6 pt on each side: 42 pt margins give the intended
        # 499 pt text width and align body text with the footer at x=48.
        leftMargin=42, rightMargin=42, topMargin=43, bottomMargin=47,
        title='Lecture 02 — Instructor Guide', author='Cryptography lecture series',
    )
    document.build(story, onFirstPage=footer, onLaterPages=footer, canvasmaker=GuideCanvas)
    print('Lecture02_Instructor_Guide.pdf built')
