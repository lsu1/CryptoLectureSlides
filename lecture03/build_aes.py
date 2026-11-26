"""Render the AES lecture using Lecture 2's fonts, tables, vector math and palette."""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape

import fitz
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from content import slides, MAIN_COUNT
from algorithm import MAP_TITLE, ROUND_TITLE, STAGES, OPERATIONS, STAGE_EXAMPLES, OPERATION_EXAMPLES, location
import build_lecture as style
from aes_trace import SBOX, INV_SBOX, verify_examples
from math_typesetting import compile_equations

ROOT = Path(__file__).resolve().parent
DEST = ROOT / 'Lecture03_AES.pdf'
W, H = style.W, style.H
NAVY, TEAL, PAPER, CORAL = style.NAVY, style.TEAL, style.PAPER, style.CORAL
INK, MUTED, LIGHT, WHITE = style.INK, style.MUTED, style.LIGHT, colors.white
PALE = colors.HexColor('#CFDFDE')
SOFT = colors.HexColor('#EFF2EF')
COOL = colors.HexColor('#C2DBDC')


def write(c, text, x, y, size, color=INK, face='Sans', align='left'):
    c.setFont(face, size)
    c.setFillColor(color)
    {'left': c.drawString, 'center': c.drawCentredString, 'right': c.drawRightString}[align](x, y, text)


def box(c, x, y, w, h, color, radius=6):
    c.setFillColor(color)
    c.roundRect(x, y, w, h, radius, stroke=0, fill=1)


def draw_states(c, states, x, top, w):
    """Matrix labels give row/column coordinates; indices stay column-major."""
    n = len(states)
    gap, height = 16, 145
    card = min((w - gap * (n - 1)) / n, 360)
    x += (w - (n * card + (n - 1) * gap)) / 2
    for i, (name, hex_state, active) in enumerate(states):
        values = bytes.fromhex(hex_state)
        assert len(values) == 16 and all(0 <= v <= 15 for v in active)
        left = x + i * (card + gap)
        box(c, left, top - height, card, height, LIGHT)
        write(c, name, left + card / 2, top - 18, 14, NAVY, 'Bold', 'center')
        cellw, cellh = 42, 22
        gx = left + (card - 4 * cellw) / 2 + 7
        for col in range(4):
            write(c, f'c{col}', gx + (col + .5) * cellw, top - 38, 10, MUTED, 'Sans', 'center')
            for row in range(4):
                index = 4 * col + row
                cy = top - 44 - (row + 1) * cellh
                cx = gx + col * cellw
                hot = index in active
                box(c, cx + 1, cy + 1, cellw - 2, cellh - 2, TEAL if hot else WHITE, 2)
                write(c, f'{values[index]:02X}', cx + cellw / 2, cy + 4.5, 17,
                      WHITE if hot else INK, 'Mono', 'center')
                if col == 0:
                    write(c, f'r{row}', gx - 7, cy + 6.5, 10, MUTED, 'Sans', 'right')
    return top - height - 13


def draw_timeline(c, events, x, top, w):
    step = w / len(events)
    axis = top - 45
    c.setStrokeColor(TEAL)
    c.setLineWidth(2)
    c.line(x + 8, axis, x + 3 * step + 9, axis)
    for i, (year, caption) in enumerate(events):
        xx = x + i * step
        write(c, year, xx, top - 25, 24, NAVY, 'Bold')
        c.setFillColor(CORAL)
        c.circle(xx + 9, axis, 5, fill=1, stroke=0)
        style.para(c, escape(caption), xx, axis - 16, step - 18, 16)
    return top - 168


def link_to_slide(c, title, bounds):
    number = next(n for n, item in enumerate(slides, 1) if item['title'] == title)
    c.linkRect(title, f'slide-{number}', bounds, relative=0, thickness=0)


def draw_stage_map(c, descriptions, x, top, w):
    rowh = 49
    for i, (label, description) in enumerate(zip(STAGES, descriptions, strict=True)):
        y = top - (i + 1) * rowh
        box(c, x, y + 3, w, rowh - 5, LIGHT if i % 2 == 0 else SOFT, 4)
        box(c, x + 10, y + 10, 31, 30, TEAL, 5)
        write(c, str(i+1), x + 25, y + 18, 15, WHITE, 'Bold', 'center')
        write(c, label, x + 55, y + 18, 17, NAVY, 'Bold')
        paragraph = Paragraph(description, style.styles[14])
        _, paragraph_height = paragraph.wrap(w - 210, rowh - 5)
        assert paragraph_height <= rowh - 9, label
        paragraph_bottom = y + 3 + (rowh - 5 - paragraph_height) / 2
        paragraph.drawOn(c, x + 200, paragraph_bottom)
        link_to_slide(c, STAGE_EXAMPLES[i], (x, y + 2, x + w, y + rowh - 2))
    return top - len(descriptions) * rowh - 14


def draw_operation_map(c, descriptions, x, top, w):
    gap, height = 9, 125
    cardw = (w - 3 * gap) / 4
    for i, (label, description) in enumerate(zip(OPERATIONS, descriptions, strict=True)):
        left = x + i * (cardw + gap)
        box(c, left, top - height, cardw, height, LIGHT)
        box(c, left + 11, top - 37, 27, 26, TEAL, 4)
        write(c, chr(65 + i), left + 24.5, top - 29.5, 15, WHITE, 'Bold', 'center')
        write(c, label, left + 46, top - 30, 17, NAVY, 'Bold')
        end = style.para(c, description, left + 13, top - 52, cardw - 26, 15)
        assert end >= top - height + 7
        link_to_slide(c, OPERATION_EXAMPLES[i], (left, top - height, left + cardw, top))
    return top - height - 16


def draw_round_paths(c, x, top, w):
    entries = [
        ('Step 3 · Full rounds', 'A  →  B  →  C  →  D', 'Run rounds 1 through r − 1.'),
        ('Step 4 · Final round', 'A  →  B  →  D', 'ShiftRows feeds directly into AddRoundKey.'),
    ]
    for i, (label, sequence, note) in enumerate(entries):
        y = top - i * 35
        write(c, label, x + 12, y - 17, 15, NAVY, 'Bold')
        write(c, sequence, x + 215, y - 17, 16, TEAL, 'Bold')
        write(c, note, x + 410, y - 17, 15)
    return top - 81


def draw_location(c, item):
    focus = item.get('aes_focus')
    if not focus:
        return
    phase, operation = location(focus)
    caption = item.get('aes_detail') or operation
    left, right, gap = 347, 908, 4
    cardw = (right - left - 3 * gap) / 4
    for i, label in enumerate(STAGES, 1):
        x = left + (i - 1) * (cardw + gap)
        selected = phase == i
        box(c, x, 501, cardw, 22, TEAL if selected else LIGHT, 3)
        write(c, f'{i}  {label}', x + cardw / 2, 507, 12,
              WHITE if selected else MUTED, 'Bold' if selected else 'Sans', 'center')
    assert pdfmetrics.stringWidth(caption, 'Bold', 12.5) <= right - left, caption
    write(c, caption, right, 482, 12.5, TEAL, 'Bold', 'right')
    page = ROUND_TITLE if phase in (3, 4) or focus.startswith(('math_', 'inv_', 'sbox')) else MAP_TITLE
    link_to_slide(c, page, (left, 478, right, 525))


def draw_boxmap(c, inverse, x, top, w):
    mapping = INV_SBOX if inverse else SBOX
    highlight = 0x6B if inverse else 0x05
    rowh, cellw = 18.4, w / 17
    for row in range(17):
        for col in range(17):
            xx = x + col * cellw
            yy = top - (row + 1) * rowh
            header = col == 0 or row == 0
            index = ((row - 1) * 16 + col - 1)
            if row == col == 0:
                val = 'hex'
            elif header:
                val = f'{max(row, col) - 1:X}'
            else:
                val = f'{mapping[index]:02X}'
            hot = not header and index == highlight
            fill = NAVY if header else TEAL if hot else LIGHT if row % 2 else SOFT
            c.setFillColor(fill)
            c.rect(xx, yy, cellw, rowh, fill=1, stroke=0)
            write(c, val, xx + cellw / 2, yy + 4.6, 12.4, WHITE if hot or header else INK, 'Mono', 'center')
    return top - 17 * rowh - 13


def draw_xtime_chain(c, start, selected_powers, x, top, w):
    """Expose the shift and polynomial reduction before retaining each byte."""
    widths = [54, 196, 220, 216, 70, 100]
    assert sum(widths) == w
    headings = [
        ('Power', 'of x'), ('Before shift', 'hex · eight bits'),
        ('Shift left', 'nine bits · hex'), ('Reduce to one byte', 'XOR if the ninth bit is 1'),
        ('Result', 'hex'), ('Use for 83', ''),
    ]
    header_height, row_height = 37, 27
    c.setFillColor(NAVY)
    c.rect(x, top - header_height, w, header_height, fill=1, stroke=0)
    left = x
    for width, (heading, detail) in zip(widths, headings, strict=True):
        write(c, heading, left + 8, top - 14, 11, WHITE, 'Bold')
        write(c, detail, left + 8, top - 29, 10, WHITE)
        left += width

    current = start
    for power in range(8):
        bits = f'{current:08b}'
        before = f'{current:02X} · {bits[:4]} {bits[4:]}'
        shifted_text, reduction = '—', 'Starting value'
        result = current
        if power:
            shifted = current << 1
            nine_bits = f'{shifted:09b}'
            shifted_text = f'{nine_bits[0]} {nine_bits[1:5]} {nine_bits[5:]} · {shifted:03X}'
            reduction = 'Fits in eight bits'
            if shifted & 0x100:
                result = shifted ^ 0x11B
                reduction = f'{shifted:03X} XOR 11B = {result:03X}'
            else:
                result = shifted
        values = [str(power), before, shifted_text, reduction, f'{result:02X}',
                  'Keep' if power in selected_powers else '']
        bottom = top - header_height - (power + 1) * row_height
        c.setFillColor(LIGHT if power % 2 == 0 else SOFT)
        c.rect(x, bottom, w, row_height, fill=1, stroke=0)
        left = x
        for column, (width, value) in enumerate(zip(widths, values, strict=True)):
            selected = power in selected_powers and column >= 4
            write(c, value, left + 8, bottom + 8, 14,
                  TEAL if selected else INK, 'Bold' if column == 5 else 'Mono')
            left += width
        current = result
    return top - header_height - 8 * row_height - 13


def draw_inverse_division(c, rows, x, top, width):
    """Show the degree rule, its first application and the complete division."""
    top = style.para(
        c, 'Find the multiplicative inverse of 05 in the AES finite field. '
        'First divide modulus 11B by the polynomial for 05.',
        x, top, width, 15,
    ) - 5
    write(c, 'Dividend  m(x) = x⁸ + x⁴ + x³ + x + 1  ↔  11B',
          x, top - 14, 14, NAVY)
    write(c, 'Fixed divisor  b(x) = x² + 1  ↔  05',
          x + 495, top - 14, 14, TEAL, 'Bold')
    top -= 24
    box(c, x, top - 29, width, 29, LIGHT, 4)
    write(c, 'Required shift = current polynomial degree − divisor degree',
          x + 12, top - 20, 16, CORAL, 'Bold')
    top -= 37
    top = style.para(
        c, 'Match the highest powers, XOR to cancel them, then carry the remainder forward. '
        'Multiplying by xᵏ shifts the binary bits left k places. In GF(2), addition and subtraction are XOR.',
        x, top, width, 14,
    ) - 5

    write(c, 'First step   x⁸ ÷ x² = x⁶, so 8 − 2 = 6',
          x, top - 14, 15, NAVY, 'Bold')
    polynomial_x = x + 84
    for offset, label, polynomial in [
        (34, 'Current', 'x⁸ + x⁴ + x³ + x + 1'),
        (52, 'Add x⁶b', 'x⁸ + x⁶'),
    ]:
        baseline = top - offset
        write(c, label, x, baseline, 13, MUTED)
        write(c, polynomial, polynomial_x, baseline, 15)
        c.setStrokeColor(CORAL)
        c.setLineWidth(1.2)
        c.roundRect(polynomial_x - 2, baseline - 3,
                    pdfmetrics.stringWidth('x⁸', 'Sans', 15) + 4, 18, 2,
                    fill=0, stroke=1)
    write(c, 'XOR', x, top - 70, 13, TEAL, 'Bold')
    write(c, 'x⁸ + x⁸ = 0', x + 410, top - 52, 13, CORAL, 'Bold')
    write(c, '05B = x⁶ + x⁴ + x³ + x + 1  (degree 6)',
          polynomial_x, top - 70, 14, TEAL)
    binary_x = x + 568
    write(c, 'The same XOR in binary', binary_x, top - 14, 13, TEAL, 'Bold')
    for line, text in enumerate([
        '11B   100011011', '140   101000000',
        '      ---------', 'XOR   001011011 = 05B',
    ]):
        write(c, text, binary_x, top - 31 - 14 * line, 13, INK, 'Mono')
    write(c, '140 is 05 shifted left six places as an unreduced binary-polynomial product.',
          x, top - 91, 13, MUTED)
    top -= 102

    widths = [110, 115, 135, 250, width - 610]
    colors_by_column = [NAVY, NAVY, CORAL, TEAL, NAVY]
    headers = ['Current value', 'Current degree', 'Required shift', 'Shifted divisor', 'XOR result → next current value']
    header_height, row_height = 24, 25
    c.setFillColor(NAVY)
    c.rect(x, top - header_height, width, header_height, fill=1, stroke=0)
    left = x
    for column_width, heading in zip(widths, headers, strict=True):
        assert pdfmetrics.stringWidth(heading, 'Bold', 11) <= column_width - 10
        write(c, heading, left + 5, top - 16, 11, WHITE, 'Bold')
        left += column_width
    for row_number, (current, degree, shift, multiple, remainder) in enumerate(rows):
        bottom = top - header_height - (row_number + 1) * row_height
        c.setFillColor(LIGHT if row_number % 2 == 0 else SOFT)
        c.rect(x, bottom, width, row_height, fill=1, stroke=0)
        values = [current, str(degree), f'{degree} − 2 = {shift}', multiple, remainder]
        left = x
        for column, (column_width, value) in enumerate(zip(widths, values, strict=True)):
            indent = 20 if column == 0 else 5
            if column == 0 and row_number:
                write(c, '↓', left + 4, bottom + 7, 14, CORAL, 'Bold')
            assert pdfmetrics.stringWidth(value, 'Sans', 13) <= column_width - indent - 4
            write(c, value, left + indent, bottom + 7, 13, colors_by_column[column])
            left += column_width
    top -= header_height + len(rows) * row_height
    write(c, 'Collect x⁶, x⁴, x → Q(x) = x⁶ + x⁴ + x.  R(x) = 1. Stop when deg R < deg b, here 0 < 2.',
          x, top - 20, 14, NAVY, 'Bold')
    return top - 32


def draw_sbox_inverse(c, input_byte, x, top, width):
    """Connect a highlighted lookup with the inverse used to construct it."""
    row, selected_column = divmod(input_byte, 16)
    assert selected_column < 8
    table_width, gutter = 430, 46
    cell_width, row_height = (table_width - gutter) / 8, 24
    output = SBOX[input_byte]
    write(c, 'A fragment of the fixed AES S-box', x, top - 14, 13, TEAL, 'Bold')
    for line in range(2):
        bottom = top - 24 - (line + 1) * row_height
        box(c, x, bottom, gutter - 2, row_height - 1, NAVY, 1)
        write(c, 'Col' if line == 0 else f'{row:X}',
              x + gutter / 2, bottom + 7, 12, WHITE, 'Bold', 'center')
        for column in range(8):
            left = x + gutter + column * cell_width
            selected = column == selected_column
            box(c, left, bottom, cell_width - 2, row_height - 1,
                TEAL if selected else LIGHT, 1)
            label = f'{column:X}' if line == 0 else f'{SBOX[16 * row + column]:02X}'
            write(c, label, left + (cell_width - 2) / 2, bottom + 6,
                  14, WHITE if selected else INK, 'Mono', 'center')
    style.para(c,
               f'Input <b>{input_byte:02X}</b> selects row <b>{row:X}</b>, column '
               f'<b>{selected_column:X}</b>.<br/>'
               f'The highlighted entry gives <b>S({input_byte:02X}) = {output:02X}</b>.',
               x + 452, top - 25, width - 452, 15)

    labels = [
        ('Input byte', f'{input_byte:02X}'),
        ('1. Field inverse', f'Find d with {input_byte:02X} · d = 01'),
        ('2. Affine map', 'Fixed bit mixing + XOR 63'),
        ('SubBytes output', f'{output:02X}'),
    ]
    gap, height = 24, 48
    card_width = (width - 3 * gap) / 4
    for index, (heading, detail) in enumerate(labels):
        left = x + index * (card_width + gap)
        selected = index in (0, 3)
        box(c, left, top - 144, card_width, height, TEAL if selected else LIGHT, 4)
        write(c, heading, left + card_width / 2, top - 114, 13,
              WHITE if selected else NAVY, 'Bold', 'center')
        write(c, detail, left + card_width / 2, top - 134, 12,
              WHITE if selected else INK, 'Mono' if selected else 'Sans', 'center')
        if index < 3:
            write(c, '→', left + card_width + gap / 2, top - 125, 18,
                  TEAL, 'Sans', 'center')
    return top - 157


def draw_inverse_proof(c, x, top, width):
    """Connect the division remainder, field inverse and byte encoding."""
    write(c, 'Find d(x) so that b(x)d(x) ≡ 1 (mod m(x)).', x, top - 16, 16)

    box(c, x, top - 78, width, 50, LIGHT)
    write(c, 'Ordinary integer division', x + 12, top - 44, 12, TEAL, 'Bold')
    write(c, '11 = 2 × 5 + 1', x + 12, top - 67, 17, NAVY, 'Bold')
    write(c, 'Dividend = Quotient × Divisor + Remainder',
          x + 250, top - 47, 15, NAVY, 'Bold')
    write(c, '11 is the dividend, 5 the divisor, 2 the quotient and 1 the remainder.',
          x + 250, top - 68, 13)

    write(c, 'Use the polynomial division identity', x, top - 99, 14, TEAL, 'Bold')
    proof_lines = [
        'm(x) = (x⁶ + x⁴ + x)b(x) + 1',
        '⇒ Q(x)b(x) = m(x) + 1',
        '⇒ Q(x)b(x) ≡ 1 (mod m(x))',
        'Therefore d(x) = Q(x) = x⁶ + x⁴ + x.',
    ]
    for index, text in enumerate(proof_lines):
        write(c, text, x, top - 123 - 23 * index, 16,
              TEAL if index == 3 else INK, 'Bold' if index == 3 else 'Sans')
    write(c, 'In GF(2), addition and subtraction both use XOR.',
          x, top - 212, 13)

    right = x + 480
    card_width = width - 480
    box(c, right, top - 213, card_width, 122, LIGHT)
    write(c, 'Encode d(x) = x⁶ + x⁴ + x', right + 12, top - 111,
          14, TEAL, 'Bold')
    write(c, 'Power', right + 12, top - 140, 13, NAVY, 'Bold')
    write(c, 'Bit', right + 12, top - 167, 13, NAVY, 'Bold')
    cell_width = (card_width - 78) / 8
    for column, power in enumerate(range(7, -1, -1)):
        center = right + 72 + (column + .5) * cell_width
        coefficient = 1 if power in (6, 4, 1) else 0
        write(c, str(power), center, top - 140, 14, INK, 'Mono', 'center')
        box(c, center - cell_width / 2 + 1, top - 174,
            cell_width - 2, 23, TEAL if coefficient else WHITE, 2)
        write(c, str(coefficient), center, top - 167, 14,
              WHITE if coefficient else INK, 'Mono', 'center')
    write(c, '0101 0010 = 52 (hex)', right + card_width / 2, top - 199,
          17, TEAL, 'Bold', 'center')

    box(c, x, top - 283, width, 59, LIGHT)
    write(c, 'Verify in the AES byte field using 05 = x² + 1',
          x + 12, top - 241, 13, TEAL, 'Bold')
    write(c, '52 · 05 = (x² + 1) · 52', x + 12, top - 268, 16)
    write(c, '52 → A4 → 53     53 XOR 52 = 01',
          x + 365, top - 268, 16, INK, 'Mono')
    write(c, 'Multiplicative inverse of 05 = 52', x, top - 306, 19, TEAL, 'Bold')
    bottom = style.para(
        c, 'This quotient gives the inverse directly because the first division leaves '
        'remainder 1. Other bytes can require more extended Euclidean steps.',
        x, top - 319, width, 14,
    )
    return bottom - 13


def draw_algebra_table(c, headers, rows, x, top, width):
    """Keep formal axioms, existing rules and examples together on one slide."""
    data = []
    for row_number, row in enumerate([headers, *rows]):
        paragraph_style = ParagraphStyle(
            'algebra-cell', fontName='Bold' if row_number == 0 else 'Sans',
            fontSize=12.5, leading=15.5, textColor=WHITE if row_number == 0 else INK,
        )
        data.append([
            Paragraph(escape(cell).replace('\n', '<br/>'), paragraph_style)
            for cell in row
        ])
    table = Table(data, colWidths=[85, 355, 260, width - 700])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Sans'),
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT, SOFT]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 1, TEAL),
    ]))
    _, height = table.wrap(width, H)
    table.drawOn(c, x, top - height)
    return top - height - 13


def draw_blocks(c, blocks, x, top, width, number):
    for block in blocks:
        kind = block[0]
        if kind == 'states':
            top = draw_states(c, block[1], x, top, width)
        elif kind == 'stage_map':
            top = draw_stage_map(c, block[1], x, top, width)
        elif kind == 'operation_map':
            top = draw_operation_map(c, block[1], x, top, width)
        elif kind == 'round_paths':
            top = draw_round_paths(c, x, top, width)
        elif kind == 'timeline':
            top = draw_timeline(c, block[1], x, top, width)
        elif kind == 'boxmap':
            top = draw_boxmap(c, block[1], x, top, width)
        elif kind == 'xtime_chain':
            top = draw_xtime_chain(c, block[1], block[2], x, top, width)
        elif kind == 'algebra_table':
            top = draw_algebra_table(c, block[1], block[2], x, top, width)
        elif kind == 'sbox_inverse':
            top = draw_sbox_inverse(c, block[1], x, top, width)
        elif kind == 'inverse_division':
            top = draw_inverse_division(c, block[1], x, top, width)
        elif kind == 'inverse_proof':
            top = draw_inverse_proof(c, x, top, width)
        else:
            top = style.drawblocks(c, [block], x, top, width, number)
    return top


def cover(c):
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    write(c, 'MH6003  /  Cryptography lecture series', 52, 468, 16, WHITE)
    c.setFillColor(CORAL)
    c.rect(52, 441, 56, 4, fill=1, stroke=0)
    write(c, 'Lecture 03', 52, 383, 22, COOL)
    write(c, 'The Advanced', 52, 303, 50, WHITE, 'Bold')
    write(c, 'Encryption Standard', 52, 239, 50, WHITE, 'Bold')
    write(c, 'Following one block through AES', 54, 162, 22, WHITE)
    data = bytes.fromhex('00112233445566778899AABBCCDDEEFF')
    for row in range(4):
        for col in range(4):
            xx, yy = 662 + col * 59, 323 - row * 53
            box(c, xx, yy, 54, 47, TEAL if col == 0 else colors.HexColor('#244657'), 4)
            write(c, f'{data[4*col+row]:02X}', xx + 27, yy + 15, 20, WHITE, 'Mono', 'center')


def reference_links():
    """Give worked slides a direct link to the table or derivation they use."""
    references = {
        'Find an inverse by tracing remainders': 'A second integer inverse by back-substitution',
        'Keep a product inside one byte': 'Which binary polynomials are irreducible?',
        'What would it mean to invert 05?': 'Forward S-box',
        'SubBytes replaces one byte at a time': 'Forward S-box',
        'Apply the lookup to all 16 bytes': 'Forward S-box',
        'Where do the MixColumns weights come from?': 'How polynomial coefficients wrap into four rows',
        'Read the MixColumns matrix one row at a time': 'Why the fixed column multiplier has an inverse',
        'Rotate one word and substitute its four bytes': 'Forward S-box',
        'Read the four completed key columns': 'AES-128 checkpoints, rounds 0–5',
        'Follow the block to the last round': 'AES-128 checkpoints, rounds 6–10',
        'Decrypt the last round we just encrypted': 'Inverse S-box',
        'Undo the mixing of the first column': 'Compute a row of InvMixColumns',
    }
    appendix_pages = {s['title'].split(' / ', 1)[1]: (n, s['title'])
                      for n, s in enumerate(slides[MAIN_COUNT:], MAIN_COUNT + 1)}
    pages = {n: appendix_pages[references[s['title']]]
             for n, s in enumerate(slides[:MAIN_COUNT], 1) if s['title'] in references}
    assert len(pages) == len(references)
    return pages


def render(out):
    style.issues.clear()
    style.placements.clear()
    style.layout.clear()
    math = [e for s in slides for e in style.math_walk(s['blocks'])]
    cache, equations, style.assets = compile_equations(math)
    links = reference_links()
    with TemporaryDirectory(prefix='aes-lecture-') as tmp:
        base = Path(tmp) / 'base.pdf'
        c = Canvas(str(base), pagesize=(W, H), initialFontName='Sans')
        c.setAuthor('MH6003 Cryptography')
        c.setTitle('MH6003 Cryptography / Lecture 03 / The Advanced Encryption Standard')
        c.setSubject('AES finite-field arithmetic, encryption, key expansion and decryption')
        last_section = None
        for n, s in enumerate(slides, 1):
            key = f'slide-{n}'
            c.bookmarkPage(key)
            if s['section'] != last_section:
                section_key = f'section-{n}'
                c.bookmarkPage(section_key)
                c.addOutlineEntry(s['section'].title(), section_key, level=0)
                last_section = s['section']
            if n > MAIN_COUNT:
                c.addOutlineEntry(s['title'], key, level=1)
            dark = s['kind'] in ('cover', 'divider')
            if s['kind'] == 'cover':
                cover(c)
            else:
                c.setFillColor(NAVY if dark else PAPER)
                c.rect(0, 0, W, H, stroke=0, fill=1)
                c.setFillColor(CORAL)
                c.rect(52, 492, 34, 4, stroke=0, fill=1)
                write(c, s['section'], 98, 490, 10, WHITE if dark else TEAL, 'Bold')
                draw_location(c, s)
                fs = 34
                while pdfmetrics.stringWidth(s['title'], 'Bold', fs) > 856:
                    fs -= .5
                assert fs >= 24, (n, s['title'], fs)
                write(c, s['title'], 52, 445, fs, WHITE if dark else NAVY, 'Bold')
                top = 410
                if s['sub']:
                    top = style.para(c, s['sub'], 52, top, 856, 16, WHITE if dark else MUTED) - 17
                if dark:
                    for b in s['blocks']:
                        top = style.para(c, b[1], 52, top, 830, 22, WHITE) - 19
                else:
                    top = draw_blocks(c, s['blocks'], 52, top, 856, n)
                if top + 13 < (88 if s['take'] else 42):
                    style.issues.append((n, s['title'], round(top + 13, 1), 'footer clearance'))
                if s['take']:
                    box(c, 52, 43, 856, 35, TEAL if dark else LIGHT)
                    end = style.para(c, escape(s['take']), 65, 69, 830, 12, WHITE if dark else INK)
                    if end < 44:
                        style.issues.append((n, 'takeaway wraps', s['take']))
            foot = COOL if dark else MUTED
            footer = 'MH6003 / CRYPTOGRAPHY / LECTURE 03 / AES'
            if s['title'].endswith('S-box') and n > MAIN_COUNT:
                footer = 'NIST FIPS 197-upd1 (2023) / AES substitution tables'
            elif s['title'].startswith(('A3 /', 'A4 /')) or s['title'] == 'How can we check an AES implementation?':
                footer = 'NIST FIPS 197 (2001), Appendix C.1 / AES-128 example'
            write(c, footer, 52, 22, 8, foot)
            if n in links:
                dst, label = links[n]
                write(c, label, 839, 21, 10, TEAL, 'Bold', 'right')
                label_width = pdfmetrics.stringWidth(label, 'Bold', 10)
                c.linkRect(f'Go to {label}', f'slide-{dst}', (836 - label_width, 15, 845, 35), relative=0, thickness=0)
            write(c, f'{n:02d} / {len(slides):02d}', 908, 22, 8, foot, align='right')
            c.showPage()
        c.save()
        with fitz.open(base) as doc:
            for page, rect, mathpage, clip in style.placements:
                doc[page].show_pdf_page(rect, equations, mathpage, clip=clip)
            doc.save(out, garbage=4, deflate=True)
    equations.close()
    cache.cleanup()
    if style.issues:
        raise ValueError(f'Layout checks: {style.issues}')
    print(f'{len(slides)} slides, including {len(slides)-MAIN_COUNT} appendix pages.')


if __name__ == '__main__':
    verify_examples()
    render(DEST)
