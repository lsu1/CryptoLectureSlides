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
        timing = 'break' if slide['section'].startswith('BREAK') else 'estimated'
        heading += f'   <font color="#536875">· {minutes:g} min {timing}</font>'
    text = slide.get('notes') or slide.get('take') or ''
    entry = [para(heading, 'head')]
    if text:
        entry.append(para(escape(text), 'note' if with_duration else 'appendix_note'))
    return entry


def get_story(slides, main_count, plan):
    rows = []
    teaching_minutes = 0
    teaching_estimate = 0
    break_minutes = 0
    for row in plan:
        first, last = row['first'], row['last']
        pages = str(first) if first == last else f'{first}–{last}'
        if slides[first - 1]['section'].startswith('BREAK'):
            break_minutes += row['minutes']
            estimate_label = 'Break'
        else:
            teaching_minutes += row['minutes']
            teaching_estimate += row['estimate']
            estimate_label = f"{row['estimate']:g} min"
        rows.append([f"{row['start']}–{row['end']}", pages, row['label'], estimate_label])
    excess = teaching_estimate - teaching_minutes
    if excess > 0:
        difference = f'{excess:g} minutes beyond the classroom allocation'
    elif excess < 0:
        difference = f'leaving {-excess:g} minutes for additional discussion'
    else:
        difference = 'exactly the classroom allocation'
    story = [
        para('Teaching AES', 'title'),
        para(f'This review edition has {len(slides)} slides. Pages 1–{main_count} include the '
             f'lecture and break markers. The final {len(slides) - main_count} pages hold '
             'reference tables and additional working.'),
        para('Class timetable and full teaching estimates', 'section'),
        table(['Class time', 'Slides', 'Material', 'Full teaching'], rows,
              [90, 58, BODY_WIDTH - 233, 85]),
        Spacer(1, 6),
        para(f'The booked session runs from {plan[0]["start"]} to {plan[-1]["end"]}, with '
             f'{teaching_minutes} teaching minutes and {break_minutes} minutes of breaks. '
             f'Allowing time to explain every main slide and work the examples gives an '
             f'estimated <b>{teaching_estimate:g} teaching minutes</b>, '
             f'{difference}. '
             'This estimate excludes the appendix.'),
        para('How to read the AES overview', 'section'),
        para('<b>1 Prepare.</b> Load the plaintext into a four-by-four state and expand the key. '
             '<b>2 Initial XOR.</b> Combine the state with the first key. '
             '<b>3 Full rounds.</b> Apply A SubBytes, B ShiftRows, C MixColumns and D AddRoundKey '
             'in order. <b>4 Final round.</b> Apply A, B and D, then read the ciphertext down '
             'the columns.'),
        para('Use the marker to point back to the operation under discussion. For instance, '
             'the byte-inverse example supports A, while the polynomial fold explains C. '
             'For a decryption slide, “Undo” identifies the corresponding encryption step. '
             'Ask which state the class should recover before showing the result.'),
        para('Sources for the lecture', 'section'),
        para('Wu Hongjun, <i>MH4311 Cryptography, Lecture 6, Block Cipher AES</i>. The '
             'supplied deck develops the mathematics from Euclid’s algorithm through column '
             'polynomials and includes the 57 × 83 field product and the inverse of 05.'),
        para('NIST, <i>Advanced Encryption Standard (AES)</i>, FIPS 197, updated 2023. '
             'Sections 3–5 specify the state layout, field operations, key expansion and inverse '
             'cipher. <link color="#087E83" href="https://doi.org/10.6028/NIST.FIPS.197-upd1">'
             'Read the standard.</link>'),
        para('The ascending-byte key and 001122…EEFF plaintext are the AES-128 example in '
             'Appendix C.1 of the original 2001 edition. '
             '<link color="#087E83" href="https://doi.org/10.6028/NIST.FIPS.197">'
             'See the 2001 example.</link> '
             '<link color="#087E83" href="https://csrc.nist.gov/projects/cryptographic-standards-and-guidelines/example-values">'
             'See NIST’s further worked examples.</link>'),
        PageBreak(),
        para('Mathematics to check at the board', 'title'),
        para('Choose the coefficient system first. In the integer examples below the numbers '
             'are decimal. In the field and column examples, pairs of digits are hex bytes.'),
        table(['Checkpoint', 'Working or expected value'], [
            ['Integer inverses', 'For 12 and 5, the last nonzero remainder is 1. '
             'The identity 1 = 5 × 5 − 2 × 12 gives the inverse of 12 modulo 5 as 3. '
             'For 45 and 19 the remainders are 7, 5, 2, 1, 0. Back-substitution gives '
             '1 = 19 × 19 − 8 × 45. The inverse of 45 modulo 19 is −8 ≡ 11.'],
            ['Field with two elements', 'In GF(2), 1 + 1 = 0. Like powers of x therefore '
             'cancel when their coefficients are added. Check addition one bit at a time '
             'using 57 XOR 83 = D4.'],
            ['Field product', '83 has set bits at positions 7, 1 and 0. The corresponding '
             'field multiples of 57 are 38, AE and 57. Their XOR is C1. Equivalently, the '
             'unreduced bit-polynomial product is 2B79. XOR with 2360, then 08D8 '
             '(shifted copies of 11B), leaves C1.'],
            ['Inverse of 05', 'The division identity is m(x) = (x⁶ + x⁴ + x)(x² + 1) + 1, '
             'where m(x) is the AES byte modulus. The factor x⁶ + x⁴ + x encodes 52. '
             'Check 05 × 52. The unreduced product 11A XOR the modulus 11B is 01.'],
            ['Cubic column polynomial', 'Write a column top to bottom as the coefficients of '
             '1, y, y², y³. Multiplication of two cubic polynomials gives coefficients '
             'c₀ through c₆. Because y⁴ = 1 modulo y⁴ + 1, the reduced coefficients are '
             '(c₀ + c₄, c₁ + c₅, c₂ + c₆, c₃). Each plus sign is bytewise XOR.'],
            ['Two different moduli', 'Bit-polynomial products within a single byte reduce '
             'modulo x⁸ + x⁴ + x³ + x + 1. Column-polynomial products across four bytes '
             'reduce modulo y⁴ + 1. For instance, y³ × y = 1 in the column ring.'],
        ], [127, BODY_WIDTH - 127]),
        PageBreak(),
        para('The AES-128 trace at the board', 'title'),
        para('One input block, 00112233445566778899AABBCCDDEEFF, and the ascending key '
             '000102030405060708090A0B0C0D0E0F identify the example. In a state column, '
             'read the four bytes from top to bottom.'),
        table(['Checkpoint', 'Working or expected value'], [
            ['Input and initial key', 'The first plaintext column is 00 11 22 33. XOR with the '
             'first key column 00 01 02 03 gives 00 10 20 30.'],
            ['First substituted byte', 'Input 00 maps to 63. The S-box table row is the high '
             'hex digit and the column is the low hex digit. The separate algebra example '
             'on input 05 starts from the inverse 52. Its four one- through four-bit left '
             'rotations are A4, 49, 92 and 25. XOR these with 52 and 63 to obtain 6B.'],
            ['First mixed output', 'ShiftRows assembles 63 53 E0 8C in the first column. The '
             'four terms of the first MixColumns row are C6, F5, E0 and 8C. Their XOR is 5F.'],
            ['First round key', 'RotWord changes 0C 0D 0E 0F to 0D 0E 0F 0C. SubWord gives '
             'D7 AB 76 FE. After the first round constant and XOR with the first master-key '
             'word, the new word is D6 AA 74 FD.'],
            ['AES-256 key expansion', 'The master key has eight 32-bit words. When the word index '
             'i leaves remainder 4 on division by 8, apply SubWord to the preceding word '
             'and XOR with word i − 8. The RotWord and round-constant branch applies at '
             'multiples of 8.'],
            ['End of round 1', 'The first mixed column 5F 72 64 15 XOR the first round-key '
             'column D6 AA 74 FD gives 89 D8 10 E8.'],
            ['End of round 10', 'The ciphertext is 69C4E0D8 6A7B0430 D8CDB780 70B4C55A. '
             'Each group is one column. Decrypting it with the original key returns the input.'],
            ['Undo the final XOR', 'The first ciphertext column 69 C4 E0 D8 XOR the first '
             'column of the last round key, 13 11 1D 7F, recovers 7A D5 FD A7. Next, undo '
             'the row shifts, then the byte substitutions, to recover the end of round 9.'],
        ], [134, BODY_WIDTH - 134]),
        PageBreak(), para('Slide-by-slide notes', 'title'),
        para('Each slide number matches the review PDF. Teaching estimates include the '
             'calculation or discussion described in the note. Break durations follow the class timetable.'),
    ]
    last_section = None
    for number, slide in enumerate(slides[:main_count], 1):
        section = slide['section']
        entry = notes_entry(number, slide, True)
        if section != last_section:
            entry.insert(0, para(escape(section.title()), 'section'))
        story.append(KeepTogether(entry))
        last_section = section
    story.extend([PageBreak(), para('Appendix slide notes', 'title')])
    for number, slide in enumerate(slides[main_count:], main_count + 1):
        story.append(KeepTogether(notes_entry(number, slide, False)))
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
