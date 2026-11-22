"""A complete AES-128 first round, with the same block at every stage."""

from deck_schema import slide, P, C, T, M


from aes_trace import KEY as KEY0, PLAINTEXT, ROUND_TRACE

INITIAL = ROUND_TRACE[0]['end']
SUB = ROUND_TRACE[1]['sub_bytes']
SHIFT = ROUND_TRACE[1]['shift_rows']
MIX = ROUND_TRACE[1]['mix_columns']
KEY1 = ROUND_TRACE[1]['round_key']
ROUND1 = ROUND_TRACE[1]['end']
FIRST_COLUMN = [0, 1, 2, 3]


def round_slide(title, blocks, **kwargs):
    return slide(title, blocks, section='AES ENCRYPTION', **kwargs)


slides = [
    round_slide('First, XOR the plaintext with the key', [
        ('states', [
            ('Plaintext', PLAINTEXT, FIRST_COLUMN),
            ('Round key 0', KEY0, FIRST_COLUMN),
            ('Round 1 input', INITIAL, FIRST_COLUMN),
        ]),
        C('DOWN THE FIRST COLUMN',
          '00 XOR 00 = 00     11 XOR 01 = 10\n22 XOR 02 = 20     33 XOR 03 = 30', 18),
    ], take='AddRoundKey pairs bytes at the same row and column. Apply it once before round 1.',
        notes='The first AES-128 round key is the original 16-byte key. Trace two corresponding cells with a finger, then ask students to check the bottom-right cell, FF XOR 0F = F0.',
        minutes=3),

    round_slide('SubBytes replaces one byte at a time', [
        P('For a byte written with two hex digits, the first digit selects the table row. The second selects the column. Input 05 goes to row 0, column 5 and gives 6B.'),
        T(['First digit', 'Column 0', 'Column 1', 'Column 2', 'Column 5'], [
            ['0', '63', '7C', '77', '6B'],
            ['1', 'CA', '82', 'C9', '59'],
            ['2', 'B7', 'FD', '93', '3F'],
            ['3', '04', 'C7', '23', '96'],
        ], [1.35, 1, 1, 1, 1]),
        P('Try input 30. Row 3, column 0 gives 04.'),
    ], take='This is a fragment of the fixed AES substitution table. The complete S-box is in appendix A1.',
        notes='Start with 05 because its field inverse was derived earlier. Point to the row and column headers, then let students find 30. S-box coordinates index a byte value, regardless of its position in the state.',
        minutes=3),

    round_slide('How does AES construct the S-box?', [
        P('First take the multiplicative inverse of the input byte in the AES field. For input 00, assign the intermediate byte 00. Call the resulting byte b.'),
        P('Next combine b with four rotated copies and the fixed byte 63, all by XOR. This second step is called an affine transformation.'),
        M(r'S(a)= b \oplus R(b)\oplus R^2(b)\oplus R^3(b)\oplus R^4(b)\oplus\mathtt{63}'),
        C('R ROTATES AN EIGHT-BIT BYTE LEFT BY ONE POSITION',
          'b7 b6 b5 b4 b3 b2 b1 b0  →  b6 b5 b4 b3 b2 b1 b0 b7', 17),
    ], take='R² means applying the rotation twice. The leftmost bit wraps around to the rightmost position.',
        notes='Number the bits from b0 at the right to b7 at the left. Field inversion gives the S-box its nonlinearity. Each rotation acts on a single byte. Rotations here and row shifts later act on different units.',
        minutes=3),

    round_slide('Build the entry for input 05', [
        P('The field inverse of 05 is 52. Start with its eight bits and rotate one position at a time.'),
        C('THE FIVE COPIES IN THE AFFINE TRANSFORMATION',
          'Left rotations       0         1         2         3         4\n'
          'Binary        01010010  10100100  01001001  10010010  00100101\n'
          'Hex                 52        A4        49        92        25', 16),
        C('XOR THE FIVE COPIES AND THE CONSTANT 63',
          '52 ⊕ A4 = F6      F6 ⊕ 49 = BF      BF ⊕ 92 = 2D\n'
          '2D ⊕ 25 = 08      08 ⊕ 63 = 6B', 17),
        P('For input 00, every rotated copy is 00, so the same rule gives S(00) = 63.'),
    ], notes='Verify the wrap when A4 becomes 49: the 1 on the far left moves to the right. Compare the two calculated values 6B and 63 with the first row of the S-box.',
        minutes=4),

    round_slide('Apply the lookup to all 16 bytes', [
        ('states', [
            ('Round 1 input', INITIAL, FIRST_COLUMN),
            ('After SubBytes', SUB, FIRST_COLUMN),
        ]),
        C('FIRST COLUMN FROM TOP TO BOTTOM',
          'S(00) = 63      S(10) = CA      S(20) = B7      S(30) = 04', 17),
        P('Each output occupies the same cell as its input.'),
    ], take='A change in one input byte changes one output byte at this stage.',
        notes='Ask students to read the four outputs vertically and locate each answer in the earlier table fragment, all in table column 0.',
        minutes=2),

    round_slide('ShiftRows rotates each row by its index', [
        ('states', [
            ('Before ShiftRows', SUB, [1, 5, 9, 13]),
            ('After ShiftRows', SHIFT, [1, 5, 9, 13]),
        ]),
        P('Count rows from 0. Row 0 stays in place. Rows 1, 2 and 3 move left by 1, 2 and 3 cells, wrapping around at the left edge.'),
        C('FOLLOW ROW 1 FROM LEFT TO RIGHT', 'CA  53  60  70   →   53  60  70  CA', 18),
    ], notes='Invite a student to point to the original and new position of CA. For row 3, three places left gives the same arrangement as one place right. ShiftRows changes positions and preserves the byte values.',
        minutes=3),

    round_slide('Which four bytes now meet in column 0?', [
        ('states', [
            ('Before ShiftRows', SUB, [0, 5, 10, 15]),
            ('After ShiftRows', SHIFT, FIRST_COLUMN),
        ]),
        P('Read the highlighted cells in row order. Byte 63 stays in column 0. Bytes 53, E0 and 8C arrive there from columns 1, 2 and 3.'),
        C('INPUT TO THE FIRST MIXCOLUMNS CALCULATION', '63   53   E0   8C    (top to bottom)', 19),
    ], take='MixColumns will combine four bytes that came from four different SubBytes columns.',
        notes='Hide the right grid briefly. Have students predict where E0 arrives and trace its two-cell movement. This is the link between moving bytes across columns and mixing inside each column.',
        minutes=3),

    round_slide('A column is a polynomial with four byte coefficients', [
        P('Read a column from top to bottom as a₀, a₁, a₂, a₃. Its row index is the exponent of a new variable y.'),
        M(r'A(y)=a_0+a_1y+a_2y^2+a_3y^3'),
        C('FOR THE FIRST COLUMN', 'A(y) = 63 + 53y + E0y² + 8Cy³', 20),
        T(['Where the arithmetic takes place', 'What the modulus does'], [
            ['Inside a byte, using x', 'Reduce bit-polynomial products modulo x⁸ + x⁴ + x³ + x + 1.'],
            ['Across a column, using y', 'Reduce powers of y modulo y⁴ + 1 to return four bytes.'],
        ], [0.39, 0.61]),
    ], notes='Hex pairs are coefficients in the AES byte field. The two indeterminates serve different purposes. Row zero is the constant coefficient even though we read it at the top of the state.',
        minutes=4),

    round_slide('Where do the MixColumns weights come from?', [
        P('AES multiplies each column polynomial by the same fixed polynomial in the quotient ring shown below. Its coefficients are hex bytes.'),
        M(r'B(y)=\mathtt{02}+\mathtt{01}y+\mathtt{01}y^2+\mathtt{03}y^3'
          r'\quad\text{in}\quad \mathrm{GF}(2^8)[y]/(y^4+1)'),
        P('Here y⁴ = 1 because addition and subtraction coincide. Both degree-0 and degree-4 terms therefore contribute to the new top byte.'),
        M(r'd_0=\underbrace{\mathtt{02}\,a_0}_{\text{degree 0}}'
          r'\oplus\underbrace{\mathtt{03}\,a_1\oplus\mathtt{01}\,a_2\oplus\mathtt{01}\,a_3}_{\text{degree 4}}'),
    ], take='For example, (03y³)(a₁y) contributes 03·a₁ to the constant coefficient because y⁴ wraps to 1.',
        notes='Write B(y)A(y) and circle each pair of exponents that sums to four. Ask which pair of exponents contributes 03 times a1. All coefficient products are field products, and coefficients at a given power combine with XOR.',
        minutes=5),

    round_slide('Read the MixColumns matrix one row at a time', [
        M(r'\begin{pmatrix}d_0\\d_1\\d_2\\d_3\end{pmatrix}='
          r'\begin{pmatrix}\mathtt{02}&\mathtt{03}&\mathtt{01}&\mathtt{01}\\'
          r'\mathtt{01}&\mathtt{02}&\mathtt{03}&\mathtt{01}\\'
          r'\mathtt{01}&\mathtt{01}&\mathtt{02}&\mathtt{03}\\'
          r'\mathtt{03}&\mathtt{01}&\mathtt{01}&\mathtt{02}\end{pmatrix}'
          r'\begin{pmatrix}a_0\\a_1\\a_2\\a_3\end{pmatrix}'),
        P('Each row gives four field products for one output byte. XOR those four products. Moving down one row rotates the weights one place to the right.'),
        C('SHORTCUTS FOR THE THREE WEIGHTS',
          '01 · a = a       02 · a = xtime(a)       03 · a = xtime(a) ⊕ a', 17),
    ], notes='Point out that 03 is 02 XOR 01 as a field element. Ask students for the weights that produce d2 and identify the byte that will be multiplied by 02.',
        minutes=3),

    round_slide('Work the first output byte by hand', [
        P('For input 63, 53, E0, 8C, take the weights 02, 03, 01, 01 from the first matrix row.'),
        T(['Product', 'Byte calculation', 'Result'], [
            ['02 · 63', 'Left shift 01100011 by one bit.', 'C6'],
            ['03 · 53', 'Double 53 to A6. Then A6 XOR 53 = F5.', 'F5'],
            ['01 · E0 and 01 · 8C', 'Multiplication by 01 preserves each byte.', 'E0 and 8C'],
        ], [0.24, 0.57, 0.19]),
        C('COMBINE THE FOUR RESULTS',
          'C6 ⊕ F5 = 33        33 ⊕ E0 = D3        D3 ⊕ 8C = 5F', 18),
    ], take='5F goes into row 0 of the first output column.',
        notes='Check the first XOR nibble by nibble, C XOR F = 3 and 6 XOR 5 = 3. Both 63 and 53 have top bit 0, so their doublings use the simple shift.',
        minutes=4),

    round_slide('Finish the first output column', [
        P('Two remaining doublings need reduction. E0 shifts to C0 in the low eight bits, then C0 ⊕ 1B = DB. For 8C, the same steps give 18 ⊕ 1B = 03.'),
        T(['Output row', 'Weights', 'XOR of products', 'Byte'], [
            ['0', '02  03  01  01', 'C6 ⊕ F5 ⊕ E0 ⊕ 8C', '5F'],
            ['1', '01  02  03  01', '63 ⊕ A6 ⊕ 3B ⊕ 8C', '72'],
            ['2', '01  01  02  03', '63 ⊕ 53 ⊕ DB ⊕ 8F', '64'],
            ['3', '03  01  01  02', 'A5 ⊕ 53 ⊕ E0 ⊕ 03', '15'],
        ], [0.18, 0.25, 0.42, 0.15]),
        P('For row 1, the third product is 03 · E0 = DB ⊕ E0 = 3B.'),
    ], notes='Encourage students to verify 8F in row 2 as 03 XOR 8C. The four output bytes are read in row order down the resulting column.',
        minutes=4),

    round_slide('Your turn with the second column', [
        ('states', [('After ShiftRows', SHIFT, [4, 5, 6, 7])]),
        P('Write down the four highlighted bytes in order. Compute the top output byte using the weights 02, 03, 01, 01. Keep the four products visible before you XOR them.'),
        C('USE THESE TWO RULES',
          '02 · a = xtime(a)                 03 · a = xtime(a) ⊕ a', 18),
    ], take='Allow three minutes for calculation, then compare your intermediate products with a neighbour.',
        notes='Give students three minutes individually and a minute in pairs. Have them say the four input bytes aloud before starting. Revisit the effect of the top input bit during xtime if needed.',
        minutes=5),

    round_slide('Check your byte in the full mixed state', [
        C('SECOND COLUMN, TOP OUTPUT BYTE',
          '02 · 09 = 12       03 · 60 = C0 ⊕ 60 = A0\n'
          '12 ⊕ A0 = B2       B2 ⊕ E1 = 53       53 ⊕ 04 = 57', 18),
        ('states', [
            ('Before MixColumns', SHIFT, [4, 5, 6, 7]),
            ('After MixColumns', MIX, [4]),
        ]),
        P('The top byte of column 1 is 57. The first column still reads 5F, 72, 64, 15.'),
    ], notes='Ask a student to explain why 60 is doubled before it is XORed with itself. Compare 57 to its location in the right grid and read the four bytes in the preceding column.',
        minutes=3),

    round_slide('How much difference does one changed byte make?', [
        P('Compare two input columns by XORing them. If only the third byte differs by 01, their input difference has the form below. MixColumns is linear, so it acts directly on this difference.'),
        C('USE THE THIRD MATRIX COLUMN',
          'Input difference       00  00  01  00\n'
          'Output difference      01  03  02  01', 19),
        M(r'\operatorname{wt}(\Delta)+\operatorname{wt}(\mathrm{MixColumns}(\Delta))\geq 5'
          r'\qquad (\Delta\ne 0)'),
        P('Here wt counts nonzero bytes. Our example attains 1 + 4 = 5. This minimum is the branch number.'),
    ], notes='Invite the class to predict how many output bytes must change if two input bytes change (at least three). If time permits, trace how the next SubBytes and ShiftRows distribute four active bytes from one column into four columns.',
        minutes=5),

    round_slide('Finish round 1 with its round key', [
        ('states', [
            ('After MixColumns', MIX, FIRST_COLUMN),
            ('Round key 1', KEY1, FIRST_COLUMN),
            ('After round 1', ROUND1, FIRST_COLUMN),
        ]),
        C('XOR THE CORRESPONDING BYTES OF COLUMN 0',
          '5F ⊕ D6 = 89     72 ⊕ AA = D8     64 ⊕ 74 = 10     15 ⊕ FD = E8', 16),
        P('The key schedule derives this 16-byte round key from the original key.'),
    ], notes='The action is the same bytewise XOR as the initial addition, with a different round key. Check an unhighlighted position together, for instance 57 XOR D2 = 85.',
        minutes=3),

    round_slide('Trace column 0 from the plaintext to round 2', [
        T(['Stage', 'Column 0, top to bottom', 'How these bytes arose'], [
            ['Plaintext', '00  11  22  33', 'Load four consecutive input bytes.'],
            ['After the initial key XOR', '00  10  20  30', 'XOR with round key 0.'],
            ['After SubBytes', '63  CA  B7  04', 'Substitute each byte separately.'],
            ['After ShiftRows', '63  53  E0  8C', 'Gather bytes from four input columns.'],
            ['After MixColumns', '5F  72  64  15', 'Mix those four bytes together.'],
            ['After round key 1', '89  D8  10  E8', 'XOR with D6, AA, 74, FD.'],
        ], [0.28, 0.29, 0.43]),
        C('FULL INPUT TO ROUND 2, READ DOWN SUCCESSIVE COLUMNS',
          '89D810E8  855ACE68  2D1843D8  CB128FE4', 20),
    ], notes='Read the checkpoint table vertically. Ask at which step our column first depended on other columns; it was ShiftRows. Use the last key column to motivate the expansion of the original key in the next part.',
        minutes=3),
]


appendix = [
    slide('How polynomial coefficients wrap into four rows', [
        P('Multiply the column polynomial A(y) by the AES multiplier B(y) before reduction. Write the seven product coefficients as c₀ through c₆.'),
        M(r'B(y)A(y)=c_0+c_1y+c_2y^2+c_3y^3+c_4y^4+c_5y^5+c_6y^6'),
        P('Since y⁴ = 1 in this quotient, y⁵ becomes y and y⁶ becomes y². Coefficients that reach the same power combine by XOR.'),
        M(r'(d_0,d_1,d_2,d_3)=(c_0\oplus c_4,\ c_1\oplus c_5,\ c_2\oplus c_6,\ c_3)'),
    ], section='APPENDIX', take='Addition of two column polynomials also combines corresponding bytes by XOR.',
        notes='This is the general coefficient folding behind the cyclic matrix. It extends the top-row derivation shown during class.', minutes=0),
    slide('Why the fixed column multiplier has an inverse', [
        P('In characteristic two, y⁴ + 1 = (y + 1)⁴. A polynomial shares a factor with this modulus exactly when y + 1 divides it, which is equivalent to having value 0 at y = 1.'),
        M(r'B(1)=\mathtt{02}\oplus\mathtt{01}\oplus\mathtt{01}\oplus\mathtt{03}=\mathtt{01}'),
        P('Thus B(y) is relatively prime to y⁴ + 1. The extended Euclidean algorithm gives a polynomial inverse. Its four coefficients define InvMixColumns.'),
        M(r'B^{-1}(y)=\mathtt{0E}+\mathtt{09}y+\mathtt{0D}y^2+\mathtt{0B}y^3'
          r'\pmod{y^4+1}'),
    ], section='APPENDIX', take='The column ring contains noninvertible elements. The multiplier selected for MixColumns is invertible.',
        notes='For a contrasting example, the fourth power of the nonzero element y+1 is zero in this ring. The polynomial Euclidean algorithm used for a byte inverse also applies over the field of byte coefficients.', minutes=0),
]
