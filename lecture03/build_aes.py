"""Render the AES lecture using Lecture 2's fonts, tables, vector math and palette."""
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.sax.saxutils import escape

import fitz
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas

from content import slides, MAIN_COUNT
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


def draw_flow(c, items, x, top, w):
    gap = 12
    card = (w - (len(items) - 1) * gap) / len(items)
    for i, (title, lines) in enumerate(items):
        left = x + i * (card + gap)
        box(c, left, top - 106, card, 106, LIGHT)
        write(c, title, left + 14, top - 31, 18, TEAL, 'Bold')
        for j, line in enumerate(lines.splitlines()):
            write(c, line, left + 14, top - 61 - j * 21, 15, INK)
    return top - 123


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


def draw_blocks(c, blocks, x, top, width, number):
    for block in blocks:
        kind = block[0]
        if kind == 'states':
            top = draw_states(c, block[1], x, top, width)
        elif kind == 'flow':
            top = draw_flow(c, block[1], x, top, width)
        elif kind == 'timeline':
            top = draw_timeline(c, block[1], x, top, width)
        elif kind == 'boxmap':
            top = draw_boxmap(c, block[1], x, top, width)
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
                c.addOutlineEntry(s['section'].title(), key, level=0)
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
