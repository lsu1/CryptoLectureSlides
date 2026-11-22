"""Build the printable teaching notes from Lecture 03's slide records."""
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parent
DESTINATION = ROOT / 'Lecture03_Instructor_Guide.pdf'
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
NAVY = colors.HexColor('#132B3C')
TEAL = colors.HexColor('#087E83')
MUTED = colors.HexColor('#536875')
LIGHT = colors.HexColor('#E5EEED')
PAPER = colors.HexColor('#F6F4EE')
BODY_WIDTH = A4[0] - 96


def style(name, font, size, leading, color=NAVY, **kwargs):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                          textColor=color, **kwargs)


STYLES = {
    'title': style('title', 'GuideBold', 23, 29, spaceAfter=12, keepWithNext=True),
    'section': style('section', 'GuideBold', 14, 19, TEAL,
                     spaceBefore=9, spaceAfter=6, keepWithNext=True),
    'head': style('head', 'GuideBold', 11, 15, spaceAfter=3),
    'body': style('body', 'GuideSans', 11, 15.5, spaceAfter=8),
    'note': style('note', 'GuideSans', 11, 15, spaceAfter=10),
    'appendix_note': style('appendix_note', 'GuideSans', 11, 15, spaceAfter=4),
    'cell': style('cell', 'GuideSans', 10.5, 14),
    'cell_head': style('cell_head', 'GuideBold', 10.5, 14, colors.white),
}


def para(value, kind='body'):
    return Paragraph(value, STYLES[kind])


def table(headers, rows, widths):
    cells = []
    for index, row in enumerate([headers, *rows]):
        cells.append([para(escape(str(value)), 'cell_head' if index == 0 else 'cell')
                      for value in row])
    grid = Table(cells, colWidths=widths, hAlign='LEFT', repeatRows=1)
    grid.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'GuideSans'),
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT, PAPER]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return grid


def page_frame(canvas, document):
    canvas.setFillColor(TEAL)
    canvas.setFont('GuideBold', 8.5)
    canvas.drawString(48, A4[1] - 35, 'MH6003  /  CRYPTOGRAPHY')
    canvas.setFillColor(MUTED)
    canvas.setFont('GuideSans', 8.5)
    canvas.drawRightString(A4[0] - 48, A4[1] - 35, 'Lecture 03  /  Advanced Encryption Standard')
    canvas.setStrokeColor(colors.HexColor('#B7CCCA'))
    canvas.line(48, A4[1] - 42, A4[0] - 48, A4[1] - 42)
    canvas.drawString(48, 30, 'LECTURE 03  /  INSTRUCTOR GUIDE')
    canvas.drawRightString(A4[0] - 48, 30, str(document.page))


class GuideCanvas(Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{**kwargs, 'initialFontName': 'GuideSans'})


def notes_entry(number, slide, with_duration):
    heading = f"{number}  /  {escape(slide['title'])}"
    if with_duration:
        minutes = slide['minutes']
        heading += f'   <font color="#536875">· {minutes:g} min</font>'
    text = slide.get('notes') or slide.get('take') or ''
    entry = [para(heading, 'head')]
    if text:
        entry.append(para(escape(text), 'note' if with_duration else 'appendix_note'))
    return entry


def get_story(slides, main_count, plan):
    rows = []
    for row in plan:
        first, last = row['first'], row['last']
        pages = str(first) if first == last else f'{first}–{last}'
        rows.append([f"{row['start']}–{row['end']}", pages, row['label'], f"{row['minutes']} min"])
    story = [
        para('Teaching AES', 'title'),
        para('Start with the question left by the 16-bit substitution–permutation network in '
             'Lecture 2. How can a cipher combine reversible steps so that a local change '
             'spreads across a 128-bit block? Use the same AES-128 plaintext and key throughout '
             'the state trace.'),
        para('Evening plan', 'section'),
        table(['Local time', 'Slides', 'Focus', 'Time'], rows, [92, 54, BODY_WIDTH - 206, 60]),
        Spacer(1, 6),
        para('The 180 teaching minutes include time for students to calculate, compare results '
             'and ask questions. The two 15-minute breaks bring the session to 3½ hours. '
             'Appendix slides are available for reference after the session.'),
        para('Prompts for the board', 'section'),
        para('<b>Before the first field product.</b> Write 80 in hex and 10000000 in binary. '
             'Ask which polynomial it represents. Multiplying by the field element 02 produces '
             'the term of degree eight. The AES modulus reduces that term to 1B.'),
        para('<b>Before the first row shift.</b> Have one student label the rows and another '
             'load the bytes down the columns. Mark a byte in the second row and follow its '
             'destination when the row rotates left.'),
        para('<b>Before decryption.</b> Ask which encryption operation touched the ciphertext '
             'last. XOR with the last round key reverses that step. Let students reason backwards '
             'through the remaining operations.'),
        PageBreak(),
        para('Answers to check at the board', 'title'),
        para('Use these values while students work. Two hexadecimal digits denote one byte. '
             'When four bytes appear together as a state column, read from top to bottom.'),
        table(['Checkpoint', 'Working or expected value'], [
            ['Inverse of 05', '05 × 52 = 01 in the AES field. The unreduced polynomial '
             'product is 11A in hex. XOR with the modulus 11B leaves 01.'],
            ['Reference field product', '83 has set bits at positions 7, 1 and 0. The corresponding '
             'multiples of 57 are 38, AE and 57. Their XOR is C1.'],
            ['Input and initial key', 'The first plaintext column is 00 11 22 33. XOR with the '
             'first key column 00 01 02 03 gives 00 10 20 30.'],
            ['First substituted byte', 'Input 00 maps to 63. The S-box table row is the high '
             'hex digit and the column is the low hex digit. The separate algebra example '
             'on input 05 yields 6B.'],
            ['First mixed output', 'ShiftRows assembles 63 53 E0 8C in the first column. The '
             'four terms of the first MixColumns row are C6, F5, E0 and 8C. Their XOR is 5F.'],
            ['First round key', 'RotWord changes 0C 0D 0E 0F to 0D 0E 0F 0C. SubWord gives '
             'D7 AB 76 FE. After the first round constant and XOR with the first master-key '
             'word, the new word is D6 AA 74 FD.'],
            ['End of round 1', 'The first mixed column 5F 72 64 15 XOR the first round-key '
             'column D6 AA 74 FD gives 89 D8 10 E8.'],
            ['End of round 10', 'The ciphertext is 69C4E0D8 6A7B0430 D8CDB780 70B4C55A. '
             'Each group is one column. Decrypting it with the original key returns the input.'],
        ], [134, BODY_WIDTH - 134]),
        PageBreak(), para('Slide-by-slide notes', 'title'),
    ]
    last_section = None
    for number, slide in enumerate(slides[:main_count], 1):
        section = slide['section']
        entry = notes_entry(number, slide, True)
        if section != last_section:
            entry.insert(0, para(escape(section.title()), 'section'))
        story.append(KeepTogether(entry))
        last_section = section
    story.extend([PageBreak(), para('Appendix and sources', 'title')])
    for number, slide in enumerate(slides[main_count:], main_count + 1):
        story.append(KeepTogether(notes_entry(number, slide, False)))
    story.extend([
        para('Teaching references', 'section'),
        para('Wu Hongjun, <i>MH4311 Cryptography, Lecture 6, Block Cipher AES</i>. '
             'The supplied lecture connects Euclid’s algorithm and finite fields to the AES '
             'S-box, column mixing, key expansion and decryption. The 57 × 83 product and '
             'the inverse of 05 are worked examples from that lecture.'),
        para('NIST, <i>Advanced Encryption Standard (AES)</i>, FIPS 197, updated 2023. '
             'Sections 3–5 specify the state layout, field operations, key expansion and inverse '
             'cipher. <link color="#087E83" href="https://doi.org/10.6028/NIST.FIPS.197-upd1">'
             'Read the standard.</link>'),
        para('The sequential-byte key and 001122…EEFF plaintext are the AES-128 example in '
             'Appendix C.1 of the original 2001 edition. '
             '<link color="#087E83" href="https://doi.org/10.6028/NIST.FIPS.197">'
             'See the 2001 example.</link> '
             '<link color="#087E83" href="https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines/example-values">'
             'See NIST’s further worked examples.</link>'),
    ])
    return story


def build():
    from content import MAIN_COUNT, plan, slides
    for name, file in [('GuideSans', 'DejaVuSans.ttf'), ('GuideBold', 'DejaVuSans-Bold.ttf'),
                       ('GuideItalic', 'DejaVuSans-Oblique.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(FONT_DIR / file)))
    pdfmetrics.registerFontFamily('GuideSans', normal='GuideSans', bold='GuideBold',
                                 italic='GuideItalic', boldItalic='GuideBold')
    document = SimpleDocTemplate(str(DESTINATION), pagesize=A4, leftMargin=42, rightMargin=42,
                                 topMargin=53, bottomMargin=47,
                                 title='MH6003 Cryptography — Lecture 03 Instructor Guide',
                                 author='MH6003 Cryptography')
    document.build(get_story(slides, MAIN_COUNT, plan), onFirstPage=page_frame,
                   onLaterPages=page_frame, canvasmaker=GuideCanvas)


if __name__ == '__main__':
    build()
