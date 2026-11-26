"""Three worked representations of the AES affine transformation."""

from aes_trace import SBOX, gf_inverse, rotl_byte, xtime
from slide_style import CORAL, INK, LIGHT, MUTED, TEAL, WHITE, box, write

# Relative bit positions selected by one row of the AES affine map, modulo 8.
AFFINE_OFFSETS = (0, 4, 5, 6, 7)


def binary_byte(byte):
    bits = f'{byte:08b}'
    return bits[:4] + ' ' + bits[4:]


def draw_rotation(c, x, top, width):
    a = 0x05
    b = gf_inverse(a)
    constant = 0x63
    terms = [rotl_byte(b, turns) for turns in range(5)] + [constant]
    left_width = 357
    right = x + left_width + 24
    right_width = width - left_width - 24
    write(c, 'For input a = 05, we found the inverse b = 52 (hex) = 0101 0010. Apply the affine transformation to b.',
          x, top - 10, 15.5)

    write(c, 'How does a circular left rotation work?', x, top - 43, 15.5, TEAL, 'Bold')
    box(c, x, top - 130, left_width, 74, LIGHT)
    bit_labels = ('b₀', 'b₁', 'b₂', 'b₃', 'b₄', 'b₅', 'b₆', 'b₇')
    first = x + 109
    spacing = 31
    last = first + 7 * spacing
    for depth, label, indices in ((78, 'Original', (7, 6, 5, 4, 3, 2, 1, 0)),
                                  (120, 'Rotate left', (6, 5, 4, 3, 2, 1, 0, 7))):
        write(c, label, x + 10, top - depth, 13, INK, 'Bold')
        for position, bit in enumerate(indices):
            center = first + position * spacing
            if bit == 7:
                box(c, center - 13, top - depth - 4, 26, 20, TEAL, 3)
            write(c, bit_labels[bit], center, top - depth, 14,
                  WHITE if bit == 7 else INK, 'Sans', 'center')
    # Connect just the wrapped bit, leaving the two rows of bit labels legible.
    mid = top - 94
    c.setLineWidth(1.4)
    c.setStrokeColor(TEAL)
    c.lines(((first, top - 82, first, mid), (first, mid, last, mid),
             (last, mid, last, top - 102), (last - 3, top - 99, last, top - 102),
             (last + 3, top - 99, last, top - 102)))
    write(c, 'Rotation keeps all eight bits by wrapping bit 7 to bit 0.',
          x, top - 149, 12.3)

    compare = terms[1]
    write(c, f'Try the same input {compare:02X} = {binary_byte(compare)}',
          x, top - 180, 14.7, TEAL, 'Bold')
    box(c, x, top - 208, left_width, 21, INK, 2)
    for label, offset in (('Operation', 9), ('Result in binary', 189), ('Hex', 310)):
        write(c, label, x + offset, top - 202, 12, WHITE, 'Bold')
    comparison = (('8-bit left shift', (compare << 1) & 0xFF),
                  ('Circular left rotation', rotl_byte(compare, 1)),
                  ('AES xtime', xtime(compare)))
    for row, (operation, result) in enumerate(comparison):
        depth = 226 + row * 22
        if row == 1:
            box(c, x, top - depth - 5, left_width, 21, LIGHT, 2)
        write(c, operation, x + 9, top - depth, 13)
        write(c, binary_byte(result), x + 189, top - depth, 14, INK, 'Mono')
        write(c, f'{result:02X}', x + 310, top - depth, 14, INK, 'Mono')
    write(c, 'Only xtime reduces the shifted polynomial modulo 11B.',
          x, top - 294, 12.3)

    write(c, 'Rotate 52, then XOR the six bytes', right, top - 43, 15.5, TEAL, 'Bold')
    box(c, right, top - 78, right_width, 24, INK, 3)
    for label, offset in (('Term', 10), ('Turns', 88), ('Hex', 142),
                          ('Binary', 195), ('Running XOR (hex)', 309)):
        write(c, label, right + offset, top - 71, 12, WHITE, 'Bold')
    labels = ('b', 'R(b)', 'R²(b)', 'R³(b)', 'R⁴(b)', 'Constant')
    running = 0
    for row, (label, term) in enumerate(zip(labels, terms, strict=True)):
        depth = 99 + row * 24
        if row % 2 == 0:
            box(c, right, top - depth - 6, right_width, 23, LIGHT, 2)
        write(c, label, right + 10, top - depth, 14, INK)
        write(c, str(row) if row < 5 else '—', right + 104, top - depth, 13,
              MUTED, 'Sans', 'center')
        write(c, f'{term:02X}', right + 142, top - depth, 15, INK, 'Mono')
        write(c, binary_byte(term), right + 195, top - depth, 15, INK, 'Mono')
        if 1 <= row <= 4:
            char_width = c.stringWidth('0', 'Mono', 15)
            wrapped_bit = right + 195 + 8 * char_width
            c.setStrokeColor(TEAL)
            c.setLineWidth(1.8)
            c.line(wrapped_bit, top - depth - 3, wrapped_bit + char_width, top - depth - 3)
        previous = running
        running ^= term
        operation = f'Start at {term:02X}' if row == 0 else f'{previous:02X} ⊕ {term:02X} = {running:02X}'
        write(c, operation, right + 309, top - depth, 13.5, INK, 'Mono')
    c.setStrokeColor(TEAL)
    c.line(right + 140, top - 231, right + 287, top - 231)
    write(c, 'XOR result', right + 10, top - 252, 14, INK, 'Bold')
    write(c, f'{running:02X}', right + 142, top - 252, 15.5, TEAL, 'Mono')
    write(c, binary_byte(running), right + 195, top - 252, 15, TEAL, 'Mono')
    write(c, 'Each underline marks the bit that wrapped to the right.',
          right, top - 274, 12.8)
    write(c, 'XOR down each binary column. An odd count of 1s gives 1.',
          right, top - 292, 12.8)

    # A small S-box excerpt ties the computed output to the actual lookup.
    bottom = top - 365
    box(c, x, bottom, width, 55, LIGHT)
    write(c, f'S(05) = {running:02X}', x + 13, bottom + 20, 19, TEAL, 'Bold')
    write(c, 'Column', x + 161, bottom + 34, 11.5, MUTED, 'Bold')
    write(c, 'Row 0', x + 161, bottom + 11, 12, INK, 'Bold')
    for index in (4, 5, 6):
        center = x + 240 + 36 * (index - 4)
        write(c, str(index), center, bottom + 34, 12.5, TEAL if index == a else MUTED,
              'Bold', 'center')
        if index == a:
            box(c, center - 16, bottom + 5, 32, 21, TEAL, 3)
        write(c, f'{SBOX[index]:02X}', center, bottom + 10, 14,
              WHITE if index == a else INK, 'Mono', 'center')
    write(c, 'For input 00, every rotated byte is 00.', right + 8, bottom + 33, 13.5)
    write(c, 'S(00) = 00 ⊕ 00 ⊕ 00 ⊕ 00 ⊕ 00 ⊕ 63 = 63',
          right + 8, bottom + 10, 14, INK, 'Mono')
    return bottom - 6


def draw_bits(c, x, top, width):
    inverse = gf_inverse(0x05)
    constant = 0x63
    subscripts = '₀₁₂₃₄₅₆₇₈'
    indices = range(7, -1, -1)

    def operands(i):
        positions = [(i + offset) % 8 for offset in AFFINE_OFFSETS]
        bits = [(inverse >> position) & 1 for position in positions]
        return bits + [(constant >> i) & 1]

    write(c, 'Rotations and XOR gave S(05) = 6B. Read one bit position across the same XOR to calculate one output bit.',
          x, top - 4, 14)
    write(c, 'bᵢ is bit i of the inverse (hex 52), cᵢ is bit i of the constant (hex 63), and sᵢ is bit i of the output.',
          x, top - 25, 14)

    box(c, x, top - 71, width, 34, LIGHT)
    write(c, 'sᵢ = bᵢ ⊕ b₍ᵢ₊₄₎ ⊕ b₍ᵢ₊₅₎ ⊕ b₍ᵢ₊₆₎ ⊕ b₍ᵢ₊₇₎ ⊕ cᵢ',
          x + 12, top - 59, 18, INK, 'Sans')
    write(c, 'Read every index of b modulo 8.', x + width - 12, top - 59, 14, TEAL, 'Bold', 'right')
    write(c, 'Bit 7 is leftmost (most significant). Bit 0 is rightmost (least significant). The shaded cells supply each XOR.',
          x, top - 89, 14)

    panel_top = top - 100
    panel_width = (width - 14) / 2
    cell_width = (panel_width - 117) / 8
    for i in (0, 1):
        left = x + i * (panel_width + 14)
        box(c, left, panel_top - 158, panel_width, 158, LIGHT)
        write(c, f'Output bit {i}', left + 12, panel_top - 19, 16, TEAL, 'Bold')

        grid = left + 104
        for j, bit in enumerate(indices):
            cx = grid + (j + .5) * cell_width
            write(c, str(bit), cx, panel_top - 39, 13, MUTED, 'Sans', 'center')
        write(c, 'Bit index', left + 12, panel_top - 39, 13, MUTED)
        selected = {(i + offset) % 8 for offset in AFFINE_OFFSETS}
        for row, (label, byte, selected_bits) in enumerate((('b = 52', inverse, selected), ('c = 63', constant, {i}))):
            baseline = panel_top - 59 - 20 * row
            write(c, label, left + 12, baseline, 14, INK, 'Mono')
            for j, bit in enumerate(indices):
                cx = grid + (j + .5) * cell_width
                active = bit in selected_bits
                box(c, cx - 12, baseline - 3, 24, 17, TEAL if active else WHITE, 2)
                write(c, str((byte >> bit) & 1), cx, baseline, 14, WHITE if active else INK, 'Mono', 'center')

        symbol = 's' + subscripts[i]
        raw_indices = [i + offset for offset in AFFINE_OFFSETS]
        raw_terms = ['b' + subscripts[index] for index in raw_indices] + ['c' + subscripts[i]]
        write(c, f'{symbol} = ' + ' ⊕ '.join(raw_terms), left + 12, panel_top - 100, 15)
        if i == 1:
            write(c, '8 mod 8 = 0, so b₈ = b₀.', left + 12, panel_top - 117, 13.5, TEAL, 'Bold')
            write(c, 's₁ = b₁ ⊕ b₅ ⊕ b₆ ⊕ b₇ ⊕ b₀ ⊕ c₁', left + 12, panel_top - 134, 15)
        values = ' ⊕ '.join(map(str, operands(i)))
        write(c, f'{symbol} = {values} = 1', left + 12, panel_top - (152 if i else 122), 15, INK, 'Bold')
        if i == 0:
            write(c, 'In rotation order, the copies supply bits 0, 7, 6, 5, 4 of 52.',
                  left + 12, panel_top - 149, 13.5)

    # Repeat the same six-term calculation for every index, in displayed byte order.
    grid_top = panel_top - 167
    grid = x + 114
    step = (width - 114) / 8
    box(c, x, grid_top - 19, width, 19, LIGHT, 3)
    for row, label in enumerate(('Bit index i', 'Six inputs to ⊕', 'Output bit sᵢ')):
        write(c, label, x + 6, grid_top - 14 - row * 19, 13, INK, 'Bold')
    for col, i in enumerate(indices):
        cx = grid + (col + .5) * step
        bits = operands(i)
        write(c, str(i), cx, grid_top - 14, 13, MUTED, 'Mono', 'center')
        write(c, ' '.join(map(str, bits)), cx, grid_top - 33, 12, INK, 'Mono', 'center')
        if col:
            c.setStrokeColor(LIGHT)
            c.setLineWidth(1)
            c.line(grid + col * step, grid_top - 53, grid + col * step, grid_top - 19)
        write(c, str(sum(bits) % 2), cx, grid_top - 52, 15, TEAL, 'Bold', 'center')

    write(c, 'Index wrapping reproduces circular rotation. Both methods give S(05) = 0110 1011₂ = 6B in hex.',
          x, grid_top - 78, 15, TEAL, 'Bold')
    return grid_top - 91


def draw_matrix(c, x, top, width):
    input_byte = 0x05
    inverse = gf_inverse(input_byte)
    constant = 0x63
    subscripts = '₀₁₂₃₄₅₆₇'
    # A column participates precisely when it appears in this output bit's XOR.
    matrix = [[int((column - row) % 8 in AFFINE_OFFSETS) for column in range(8)]
              for row in range(8)]
    inverse_bits = [(inverse >> i) & 1 for i in range(8)]
    constant_bits = [(constant >> i) & 1 for i in range(8)]
    output_bits = [
        (sum(a * b for a, b in zip(row, inverse_bits)) % 2) ^ constant_bit
        for row, constant_bit in zip(matrix, constant_bits)
    ]
    assert sum(bit << i for i, bit in enumerate(output_bits)) == SBOX[input_byte]

    write(c, 'The eight XOR equations from the previous slide form one matrix equation over GF(2).',
          x, top - 7, 15)
    write(c, 'Here b is the field inverse, c is the fixed constant and s is the S-box output.',
          x, top - 25, 14)
    box(c, x + width - 172, top - 22, 172, 31, LIGHT)
    write(c, 's = A × b ⊕ c', x + width - 86, top - 13, 17, TEAL, 'Bold', 'center')

    write(c, 'A · fixed 8 × 8 AES matrix', x, top - 45, 15, INK, 'Bold')
    write(c, 'Bit vectors (bytes in hex)', x + 269, top - 45, 15, INK, 'Bold')
    columns = [x + 44 + i * 27 for i in range(8)]
    vector_x = [x + offset for offset in (286, 342, 399, 456)]
    for i, cx in enumerate(columns):
        write(c, 'b' + subscripts[i], cx, top - 67, 14, MUTED, 'Bold', 'center')
    for cx, label in zip(vector_x, ('Bit', 'b (52)', 'c (63)', 's (6B)')):
        write(c, label, cx, top - 67, 13, MUTED, 'Bold', 'center')

    def cell(value, cx, y, selected=False):
        if selected:
            box(c, cx - 11, y - 2.5, 22, 16.2, TEAL, 3)
        write(c, str(value), cx, y, 14.5, WHITE if selected else INK, 'Mono', 'center')

    row_spacing = 17.6
    first_y = top - 90
    for i, row in enumerate(matrix):
        y = first_y - i * row_spacing
        if i == 0:
            box(c, x, y - 3.5, 251, 18.5, LIGHT, 3)
        write(c, 's' + subscripts[i], x + 10, y, 14, TEAL, 'Bold', 'center')
        for cx, entry in zip(columns, row):
            cell(entry, cx, y, selected=(i == 0 and entry == 1))
        write(c, str(i), vector_x[0], y, 13, MUTED, 'Mono', 'center')
        cell(inverse_bits[i], vector_x[1], y, selected=bool(matrix[0][i]))
        cell(constant_bits[i], vector_x[2], y)
        cell(output_bits[i], vector_x[3], y)

    # The arrow runs along the output vector, with its head at bit zero.
    arrow_x, arrow_tip = x + 477, first_y + 4
    c.setStrokeColor(CORAL)
    c.setLineWidth(1.8)
    c.line(arrow_x, first_y - 7 * row_spacing + 4, arrow_x, arrow_tip)
    c.line(arrow_x, arrow_tip, arrow_x - 3, arrow_tip - 6)
    c.line(arrow_x, arrow_tip, arrow_x + 3, arrow_tip - 6)

    right = x + 504
    write(c, 'Read the highlighted row', right, top - 45, 15, INK, 'Bold')
    write(c, 'A 1 selects an inverse bit. A 0 skips it.', right, top - 67, 14)
    write(c, 'In GF(2), multiply by AND and add by XOR.', right, top - 85, 14)
    write(c, 's₀ = b₀ ⊕ b₄ ⊕ b₅ ⊕ b₆ ⊕ b₇ ⊕ c₀', right, top - 108, 15.5, TEAL, 'Bold')
    write(c, '     = 0 ⊕ 1 ⊕ 0 ⊕ 1 ⊕ 0 ⊕ 1 = 1', right, top - 127, 14.5)
    write(c, 'Read the output byte', right, top - 154, 15, INK, 'Bold')
    write(c, '52 = 0101 0010 is written from bit 7 to bit 0.', right, top - 174, 14)
    write(c, 'Here bit 0 is at the top. Read s upwards to', right, top - 192, 14)
    write(c, 'write the same bits in ordinary binary order.', right, top - 210, 14)
    write(c, '0110 1011 = 6B', right, top - 230, 15, TEAL, 'Bold')

    write(c, 'Choose one of the three equivalent affine calculations', x, top - 245, 16, INK, 'Bold')
    y_mid = top - 294
    input_w, inverse_w = 100, 144
    inverse_x, method_x = x + 126, x + 315
    method_w = 250
    result_x = x + 618
    box(c, x, y_mid - 18, input_w, 36, LIGHT, 5)
    write(c, 'Input 05', x + input_w / 2, y_mid - 5, 15, INK, 'Bold', 'center')
    write(c, '→', x + 113, y_mid - 5, 17, TEAL, 'Bold', 'center')
    box(c, inverse_x, y_mid - 18, inverse_w, 36, LIGHT, 5)
    write(c, 'Field inverse 52', inverse_x + inverse_w / 2, y_mid - 5, 15,
          INK, 'Bold', 'center')

    c.setStrokeColor(TEAL)
    c.setLineWidth(1.4)
    fork_x, join_x = method_x - 22, result_x - 26
    c.line(inverse_x + inverse_w, y_mid, fork_x, y_mid)
    c.line(fork_x, y_mid - 24, fork_x, y_mid + 24)
    c.line(join_x, y_mid - 24, join_x, y_mid + 24)
    c.line(join_x, y_mid, result_x, y_mid)
    c.line(result_x, y_mid, result_x - 6, y_mid + 3)
    c.line(result_x, y_mid, result_x - 6, y_mid - 3)
    methods = ('Circular rotation and XOR', 'Bit-by-bit XOR', 'Matrix multiplication over GF(2)')
    for i, method in enumerate(methods):
        y = y_mid + (1 - i) * 24
        c.line(fork_x, y, method_x, y)
        c.line(method_x + method_w, y, join_x, y)
        box(c, method_x, y - 10, method_w, 20, LIGHT, 4)
        write(c, method, method_x + method_w / 2, y - 4.6, 13.5, INK, align='center')
    box(c, result_x, y_mid - 18, width - (result_x - x), 36, TEAL, 5)
    write(c, 'S(05) = 6B', (result_x + x + width) / 2, y_mid - 6, 19,
          WHITE, 'Bold', 'center')

    write(c, 'During encryption, SubBytes can look up 6B directly in its precomputed S-box at row 0, column 5.',
          x, top - 358, 15)
    return top - 365
