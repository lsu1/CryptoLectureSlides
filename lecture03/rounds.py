"""A complete AES-128 first round, with the same block at every stage."""

from deck_schema import slide, P, C, T, M, Two


from aes_trace import KEY as KEY0, PLAINTEXT, ROUND_TRACE

INITIAL = ROUND_TRACE[0]['end']
SUB = ROUND_TRACE[1]['sub_bytes']
SHIFT = ROUND_TRACE[1]['shift_rows']
MIX = ROUND_TRACE[1]['mix_columns']
KEY1 = ROUND_TRACE[1]['round_key']
ROUND1 = ROUND_TRACE[1]['end']
FIRST_COLUMN = [0, 1, 2, 3]


def round_slide(focus, title, blocks, **kwargs):
    item = slide(title, blocks, section='AES ENCRYPTION', **kwargs)
    item['aes_focus'] = focus
    return item


slides = [
    round_slide('initial', 'First, XOR the plaintext with the key', [
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

    round_slide('sub', 'SubBytes replaces one byte at a time', [
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

    round_slide('sub', 'How does AES construct the S-box?', [
        P('First take the multiplicative inverse of the input byte in the AES field. For input 00, assign the intermediate byte 00. Call the resulting byte b.'),
        P('Next combine b with four rotated copies and the fixed byte 63, all by XOR. This second step is called an affine transformation.'),
        M(r'S(a)= b \oplus R(b)\oplus R^2(b)\oplus R^3(b)\oplus R^4(b)\oplus\mathtt{63}'),
        C('R ROTATES AN EIGHT-BIT BYTE LEFT BY ONE POSITION',
          'b7 b6 b5 b4 b3 b2 b1 b0  →  b6 b5 b4 b3 b2 b1 b0 b7', 17),
    ], take='R² means applying the rotation twice. The leftmost bit wraps around to the rightmost position.',
        notes='Number the bits from b0 at the right to b7 at the left. Field inversion gives the S-box its nonlinearity. Each rotation acts on a single byte. Rotations here and row shifts later act on different units.',
        minutes=3),


    round_slide('sub', 'Compute one output bit of the S-box', [
        P('Write b₀ for the least significant bit of the inverse byte. Write cᵢ for bit i of the constant 63 and sᵢ for bit i of the S-box output. Every subscript on b wraps modulo 8.'),
        M(r's_i=b_i\oplus b_{i+4}\oplus b_{i+5}\oplus b_{i+6}\oplus b_{i+7}\oplus c_i'),
        C('EXAMPLE FOR BIT 0 WHEN b = 52 AND c = 63',
          'Bit index        7  6  5  4  3  2  1  0\n'
          '52 in binary     0  1  0  1  0  0  1  0\n'
          's₀ = b₀ ⊕ b₄ ⊕ b₅ ⊕ b₆ ⊕ b₇ ⊕ c₀ = 0 ⊕ 1 ⊕ 0 ⊕ 1 ⊕ 0 ⊕ 1 = 1', 15),
    ], take='Each output bit uses five input bits and one constant bit. Next, arrange those selections into a matrix.',
        notes='The four rotated words contribute bits b(i−1) through b(i−4), with indices modulo 8. Written in increasing offsets these are i+4, i+5, i+6, i+7.', minutes=3),

    round_slide('sub', 'Read the affine matrix with bit 0 at the top', [
        P('Each row selects the bits of b to XOR. Multiply over GF(2), then XOR the constant vector. The example uses the field inverse b = 52 for input 05.'),
        M(r'\begin{pmatrix}1&0&0&0&1&1&1&1\\1&1&0&0&0&1&1&1\\'
          r'1&1&1&0&0&0&1&1\\1&1&1&1&0&0&0&1\\1&1&1&1&1&0&0&0\\'
          r'0&1&1&1&1&1&0&0\\0&0&1&1&1&1&1&0\\0&0&0&1&1&1&1&1\end{pmatrix}'
          r'\begin{pmatrix}0\\1\\0\\0\\1\\0\\1\\0\end{pmatrix}'
          r'\oplus\begin{pmatrix}1\\1\\0\\0\\0\\1\\1\\0\end{pmatrix}'
          r'=\begin{pmatrix}1\\1\\0\\1\\0\\1\\1\\0\end{pmatrix}'),
    ], take='Read the result from bottom to top in conventional binary order. 01101011 gives 6B.',
        notes='The first row is the preceding slide’s calculation. For row 1 select b0, b1, b5, b6 and b7. Their sum is 0 modulo 2, then c1 = 1 gives output bit 1. Ask students to check one additional row.', minutes=3),

    round_slide('sub', 'Build the entry for input 05', [
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

    round_slide('sub', 'Apply the lookup to all 16 bytes', [
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

    round_slide('shift', 'ShiftRows rotates each row by its index', [
        ('states', [
            ('Before ShiftRows', SUB, [1, 5, 9, 13]),
            ('After ShiftRows', SHIFT, [1, 5, 9, 13]),
        ]),
        P('Count rows from 0. Row 0 stays in place. Rows 1, 2 and 3 move left by 1, 2 and 3 cells, wrapping around at the left edge.'),
        C('FOLLOW ROW 1 FROM LEFT TO RIGHT', 'CA  53  60  70   →   53  60  70  CA', 18),
    ], notes='Invite a student to point to the original and new position of CA. For row 3, three places left gives the same arrangement as one place right. ShiftRows changes positions and preserves the byte values.',
        minutes=3),

    round_slide('shift', 'Which four bytes now meet in column 0?', [
        ('states', [
            ('Before ShiftRows', SUB, [0, 5, 10, 15]),
            ('After ShiftRows', SHIFT, FIRST_COLUMN),
        ]),
        P('Read the highlighted cells in row order. Byte 63 stays in column 0. Bytes 53, E0 and 8C arrive there from columns 1, 2 and 3.'),
        C('INPUT TO THE FIRST MIXCOLUMNS CALCULATION', '63   53   E0   8C    (top to bottom)', 19),
    ], take='MixColumns will combine four bytes that came from four different SubBytes columns.',
        notes='Hide the right grid briefly. Have students predict where E0 arrives and trace its two-cell movement. This is the link between moving bytes across columns and mixing inside each column.',
        minutes=3),


    round_slide('mix', 'Which numbers can be polynomial coefficients?', [
        P('For a field K, the polynomial ring K[y] consists of all finite polynomials in the formal variable y with coefficients in K. Add like powers and distribute products, using the arithmetic of K for each coefficient.'),
        M(r'F(y)=a_0+a_1y+\cdots+a_m y^m,\qquad a_j\in K'),
        T(['Coefficient field K', 'Expand the same square'], [
            ['Real numbers', '(1 + y)² = 1 + 2y + y².'],
            ['AES byte field GF(2⁸)', '(01 + y)² = 01 + y² because 01 ⊕ 01 = 00.'],
        ], [0.39, 0.61]),
    ], take='The field tells us how to compute each coefficient. The exponent of y tracks its position.',
        notes='The construction K[y] also makes sense for a commutative ring K. Demonstrate the two mixed terms 1·y and y·1. The 2y term survives over the reals and cancels over the AES byte field.', minutes=3),

    round_slide('mix', 'Keep the remainder after polynomial division', [
        P('Choose a monic polynomial p(y), meaning its leading coefficient is 1. Division writes every F(y) in exactly one way as a multiple of p plus a remainder.'),
        M(r'F(y)=Q(y)p(y)+R(y),\qquad R=0\ \text{or}\ \deg R<\deg p'),
        P('The quotient ring K[y]/(p) represents each element by this remainder. Two polynomials give the same element when their difference is divisible by p. Add or multiply, then take the remainder again.'),
        C('WITH p(y) = y⁴ + 1 OVER THE AES BYTE FIELD',
          'y⁵ + y³ + y = y(y⁴ + 1) + y³      →      remainder y³', 18),
    ], notes='Read K[y]/(p) as polynomials over K modulo p. Perform the illustrated division on the board. Ask why a divisor of degree four leaves at most four coefficient positions.', minutes=3),

    round_slide('mix', 'A column is a polynomial with four byte coefficients', [
        P('Read a column from top to bottom as a₀, a₁, a₂, a₃. Its row index is the exponent of a new variable y.'),
        M(r'A(y)=a_0+a_1y+a_2y^2+a_3y^3'),
        C('FOR THE FIRST COLUMN', 'A(y) = 63 + 53y + E0y² + 8Cy³', 20),
        T(['Where the arithmetic takes place', 'What the modulus does'], [
            ['Inside a byte, using x', 'Reduce bit-polynomial products modulo x⁸ + x⁴ + x³ + x + 1.'],
            ['Across a column, using y', 'Reduce powers of y modulo y⁴ + 1 to return four bytes.'],
        ], [0.39, 0.61]),
    ], notes='Hex pairs are coefficients in the AES byte field. The two indeterminates serve different purposes. Row zero is the constant coefficient even though we read it at the top of the state.',
        minutes=4),


    round_slide('mix', 'Compare the two quotient constructions', [
        T(['Property', 'One byte', 'One four-byte column'], [
            ['Coefficient set', 'Bits in GF(2)', 'Bytes in GF(2⁸)'],
            ['Polynomial variable', 'x counts bit positions.', 'y counts rows in a column.'],
            ['Modulus', 'm(x) = x⁸ + x⁴ + x³ + x + 1', 'p(y) = y⁴ + 1'],
            ['Remainder', 'Degree below 8, giving 2⁸ values.', 'Degree below 4, giving (2⁸)⁴ = 2³² values.'],
            ['Multiplicative inverses', 'm(x) is irreducible. Every nonzero byte is invertible.', 'p(y) = (y + 1)⁴ is reducible. Some nonzero columns have no inverse.'],
        ], [0.23, 0.37, 0.4]),
    ], take='Each coefficient operation in the column ring uses arithmetic in the byte field.',
        notes='Point to the two variables and ask what x² and y² describe. The first selects a bit in one byte. The second selects row 2 in a column. Polynomials of degree below four include the zero polynomial.', minutes=3),

    round_slide('mix', 'Add two column polynomials', [
        P('Take the first two columns after ShiftRows. Addition combines the two coefficients of each power of y. Each pair of coefficients is a pair of bytes, so use XOR.'),
        C('COEFFICIENTS ORDERED FROM THE TOP ROW TO THE BOTTOM ROW',
          'Power of y        0     1     2     3\n'
          'Column 0         63    53    E0    8C\n'
          'Column 1         09    60    E1    04\n'
          'Sum              6A    33    01    88', 18),
        M(r'(\mathtt{63}\oplus\mathtt{09})+(\mathtt{53}\oplus\mathtt{60})y'
          r'+(\mathtt{E0}\oplus\mathtt{E1})y^2+(\mathtt{8C}\oplus\mathtt{04})y^3'),
    ], take='This calculation illustrates addition in the ring. MixColumns applies a product to each column separately.',
        notes='Ask the class to compute the coefficient of y². E0 and E1 differ only in their least significant bit, so their XOR is 01.', minutes=2),

    round_slide('mix', 'Multiply two short polynomials and reduce', [
        P('Take U = 02 + y³ and V = 03 + y. Expand all four pairwise products in the byte field. For the constant term, 02 · 03 = 06.'),
        M(r'UV=\mathtt{06}+\mathtt{02}y+\mathtt{03}y^3+y^4'),
        P('Since y⁴ + 1 = 0 in the column ring, y⁴ and 1 have the same remainder. The coefficient 01 of y⁴ joins the constant term.'),
        M(r'UV\bmod(y^4+1)=(\mathtt{06}\oplus\mathtt{01})+\mathtt{02}y+\mathtt{03}y^3'
          r'=\mathtt{07}+\mathtt{02}y+\mathtt{03}y^3'),
    ], take='The four output coefficients, from top to bottom, are 07, 02, 00, 03.',
        notes='Read the missing power y² as coefficient 00. Check the quotient explicitly by XORing one copy of y⁴ + 1 with the unreduced product.', minutes=3),

    round_slide('mix', 'Collect the seven coefficients of a full product', [
        P('Let A and B have coefficients a₀, …, a₃ and b₀, …, b₃. In their ordinary product, aᵢbⱼ contributes to cₖ exactly when i + j = k. Each juxtaposition below means multiplication in the AES byte field.'),
        Two([M(r'\begin{aligned}c_0&=a_0b_0\\c_1&=a_0b_1\oplus a_1b_0\\'
               r'c_2&=a_0b_2\oplus a_1b_1\oplus a_2b_0\\'
               r'c_3&=a_0b_3\oplus a_1b_2\oplus a_2b_1\oplus a_3b_0\end{aligned}')],
            [M(r'\begin{aligned}c_4&=a_1b_3\oplus a_2b_2\oplus a_3b_1\\'
               r'c_5&=a_2b_3\oplus a_3b_2\\c_6&=a_3b_3\end{aligned}')]),
        M(r'A(y)B(y)=c_0+c_1 y+c_2 y^2+c_3y^3+c_4y^4+c_5y^5+c_6y^6'),
    ], take='A product of two degree-three polynomials can reach degree six. Reduction brings it back to four coefficients.',
        notes='Draw the 4-by-4 grid of pair products. The diagonals contain 1, 2, 3, 4, 3, 2, 1 terms. Invite the class to recover c4 by following its three index pairs.', minutes=4),

    round_slide('mix', 'Fold powers four, five and six into the column', [
        C('READ EACH POWER OF y MODULO y⁴ + 1',
          'Original exponent      0   1   2   3   4   5   6\n'
          'Output exponent        0   1   2   3   0   1   2', 19),
        M(r'd_0=c_0\oplus c_4,\quad d_1=c_1\oplus c_5,\quad'
          r' d_2=c_2\oplus c_6,\quad d_3=c_3'),
        P('For example, the coefficient of y in the reduced product comes from degrees 1 and 5. Substituting their terms gives the weights for the second output byte.'),
        M(r'd_1=a_0b_1\oplus a_1b_0\oplus a_2b_3\oplus a_3b_2'),
    ], notes='Track c1 and c5 back to the preceding page. Explain why c3 has no partner: even the largest exponent in the product is only six.', minutes=3),

    round_slide('mix', 'The folded product is a circulant matrix', [
        P('Fix the multiplier B. Group the terms in each dᵢ by input byte a₀, a₁, a₂, a₃. The coefficient beside each input becomes an entry in that matrix row.'),
        M(r'\begin{pmatrix}d_0\\d_1\\d_2\\d_3\end{pmatrix}='
          r'\begin{pmatrix}b_0&b_3&b_2&b_1\\b_1&b_0&b_3&b_2\\'
          r'b_2&b_1&b_0&b_3\\b_3&b_2&b_1&b_0\end{pmatrix}'
          r'\begin{pmatrix}a_0\\a_1\\a_2\\a_3\end{pmatrix}'),
        P('The second row reproduces the calculation for d₁. Each new row rotates the preceding weights one position to the right. A matrix of this form is called circulant.'),
    ], notes='Circle the second row and read off the weights b1, b0, b3, b2. For the top row ask which terms reach degree zero after reduction. AES now supplies the four fixed values of B.', minutes=3),

    round_slide('mix', 'Where do the MixColumns weights come from?', [
        P('AES multiplies each column polynomial by the same fixed polynomial in the quotient ring shown below. Its coefficients are hex bytes.'),
        M(r'B(y)=\mathtt{02}+\mathtt{01}y+\mathtt{01}y^2+\mathtt{03}y^3'
          r'\quad\text{in}\quad \mathrm{GF}(2^8)[y]/(y^4+1)'),
        P('Here y⁴ = 1 because addition and subtraction coincide. Both degree-0 and degree-4 terms therefore contribute to the new top byte.'),
        M(r'd_0=\underbrace{\mathtt{02}\,a_0}_{\text{degree 0}}'
          r'\oplus\underbrace{\mathtt{03}\,a_1\oplus\mathtt{01}\,a_2\oplus\mathtt{01}\,a_3}_{\text{degree 4}}'),
    ], take='For example, (03y³)(a₁y) contributes 03·a₁ to the constant coefficient because y⁴ wraps to 1.',
        notes='Write B(y)A(y) and circle each pair of exponents that sums to four. Ask which pair of exponents contributes 03 times a1. All coefficient products are field products, and coefficients at a given power combine with XOR.',
        minutes=5),

    round_slide('mix', 'Read the MixColumns matrix one row at a time', [
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

    round_slide('mix', 'Work the first output byte by hand', [
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

    round_slide('mix', 'Finish the first output column', [
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

    round_slide('mix', 'Your turn with the second column', [
        ('states', [('After ShiftRows', SHIFT, [4, 5, 6, 7])]),
        P('Write down the four highlighted bytes in order. Compute the top output byte using the weights 02, 03, 01, 01. Keep the four products visible before you XOR them.'),
        C('USE THESE TWO RULES',
          '02 · a = xtime(a)                 03 · a = xtime(a) ⊕ a', 18),
    ], take='Allow three minutes for calculation, then compare your intermediate products with a neighbour.',
        notes='Give students three minutes individually and a minute in pairs. Have them say the four input bytes aloud before starting. Revisit the effect of the top input bit during xtime if needed.',
        minutes=5),

    round_slide('mix', 'Check your byte in the full mixed state', [
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


    round_slide('mix', 'Which column multipliers can be undone?', [
        P('A unit has a multiplicative inverse. In the column ring, a polynomial is a unit exactly when it is relatively prime to p(y) = y⁴ + 1. The extended Euclidean algorithm then expresses 1 as a polynomial combination of the two.'),
        M(r'p(y)=(y+1)^4,\quad B(1)=\mathtt{02}\oplus\mathtt{01}\oplus\mathtt{01}\oplus\mathtt{03}=\mathtt{01}'),
        P('The only irreducible factor of p is y + 1. Since B(1) is nonzero, this factor does not divide B. Thus the AES column multiplier is a unit.'),
        C('A NONZERO COLUMN WITHOUT AN INVERSE',
          '(y + 1)(y + 1)³ = (y + 1)⁴ = 0   modulo y⁴ + 1', 17),
    ], notes='The last identity produces zero from a product of two nonzero residues, which cannot happen if the first factor has an inverse. Use the factor theorem for polynomials over the byte field at the point y = 1.', minutes=3),

    round_slide('mix', 'Recover the inverse column multiplier', [
        P('Apply extended Euclid to p and B using byte-field division. List polynomial coefficients from constant term upward. Each row in the table divides by the previous remainder.'),
        T(['Division', 'Quotient coefficients', 'Remainder coefficients'], [
            ['p divided by B', '52, F6', 'A5, A5, A4'],
            ['B divided by the first remainder', '4F, 8A', 'C5, 4F'],
            ['First remainder divided by the second', 'CA, F3', '9A'],
        ], [0.45, 0.25, 0.30]),
        P('The last nonzero remainder is a field constant. Back-substitute and scale it to 01. The coefficient of B in the resulting identity is the inverse.'),
        M(r'B^{-1}(y)=\mathtt{0E}+\mathtt{09}y+\mathtt{0D}y^2+\mathtt{0B}y^3'
          r'\pmod{y^4+1}'),
    ], notes='The first quotient 52 + F6 y cancels the degree-four and degree-three terms of p. Each division leaves a lower-degree remainder. Dividing the second remainder by 9A leaves zero. The next slide tracks the coefficient of B through those divisions.', minutes=4),

    round_slide('mix', 'Track the coefficient of B through Euclid', [
        P('Write each remainder as rᵢ = sᵢ p + tᵢ B. Modulo p, this becomes rᵢ ≡ tᵢ B. Start with r₀ = p and r₁ = B, so t₀ = 0 and t₁ = 1.'),
        T(['Remainder (low degree first)', 'How to get tᵢ', 'Coefficients of tᵢ'], [
            ['r₂ = (A5, A5, A4)', 't₀ + q₁ t₁', '52, F6'],
            ['r₃ = (C5, 4F)', 't₁ + q₂ t₂', '45, 40, 8F'],
            ['r₄ = 9A', 't₂ + q₃ t₃', 'CD, 26, 78, 09'],
        ], [0.39, 0.28, 0.33]),
        P('The last row gives t₄ B ≡ 9A. Multiply both sides by the byte 9F, since 9F · 9A = 01 in the AES field.'),
        C('SCALE EACH COEFFICIENT TO OBTAIN THE INVERSE',
          '9F · (CD, 26, 78, 09) = (0E, 09, 0D, 0B)', 17),
    ], notes='Use the three quotients from the preceding slide in order. Each division gives a remainder by adding the quotient times the divisor to the dividend, because addition and subtraction coincide in characteristic two. Apply the same update to the coefficients of B. For example, t₃ = 1 + (4F + 8A y)(52 + F6 y). Its constant term is 01 XOR 44 = 45. The next slide checks the four normalized bytes by multiplying back.', minutes=3),

    round_slide('mix', 'Check the inverse by multiplying back', [
        P('Use the ordinary coefficient product of B and its proposed inverse, then apply the same folding used for a state column.'),
        C('UNREDUCED PRODUCT OF (02, 01, 01, 03) AND (0E, 09, 0D, 0B)',
          'Degree           0    1    2    3    4    5    6\n'
          'Coefficient     1C   1C   1D   00   1D   1C   1D', 17),
        C('REDUCE MODULO y⁴ + 1',
          'd₀ = 1C ⊕ 1D = 01      d₁ = 1C ⊕ 1C = 00\n'
          'd₂ = 1D ⊕ 1D = 00      d₃ = 00', 18),
        P('The remainder is (01, 00, 00, 00), the constant polynomial 1. Multiplying a mixed column by this inverse therefore restores it.'),
    ], notes='Verify the leading and trailing coefficients quickly: 02·0E = 1C and 03·0B = 1D. The normalized Bézout identity has coefficient (1D, 1C, 1D) on p and (0E, 09, 0D, 0B) on B.', minutes=3),

    round_slide('mix', 'How much difference does one changed byte make?', [
        P('Compare two input columns by XORing them. If only the third byte differs by 01, their input difference has the form below. MixColumns is linear, so it acts directly on this difference.'),
        C('USE THE THIRD MATRIX COLUMN',
          'Input difference       00  00  01  00\n'
          'Output difference      01  03  02  01', 19),
        M(r'\operatorname{wt}(\Delta)+\operatorname{wt}(\mathrm{MixColumns}(\Delta))\geq 5'
          r'\qquad (\Delta\ne 0)'),
        P('Here wt counts nonzero bytes. Our example attains 1 + 4 = 5. This minimum is the branch number.'),
    ], notes='Invite the class to predict how many output bytes must change if two input bytes change (at least three). If time permits, trace how the next SubBytes and ShiftRows distribute four active bytes from one column into four columns.',
        minutes=5),


    round_slide('mix', 'Why this mixing is called maximum distance separable', [
        P('Pair each four-byte column X with its four-byte mixed column M(X). Each pair is an eight-byte word. Its byte distance from another word counts the positions where their bytes differ.'),
        M(r'd((X,M(X)),(Y,M(Y)))=\operatorname{wt}(X\oplus Y)'
          r'+\operatorname{wt}(M(X\oplus Y))'),
        P('For any distinct X and Y the distance is at least 5. Changing one input byte gives exactly 5 differences, one at the input and four at the output.'),
        P('A code with eight output symbols that carries four independent symbols has minimum distance at most 8 − 4 + 1 = 5. Meeting this bound makes the code maximum distance separable (MDS).'),
    ], notes='Use the counting proof of the Singleton bound if time permits: deleting d−1 positions must still distinguish all 256⁴ inputs; hence 8−(d−1) must be at least 4. Here the words are the concatenated input and output columns. This diffusion measure counts byte differences.', minutes=3),

    round_slide('xor', 'Finish round 1 with its round key', [
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

    round_slide('round_summary', 'Trace column 0 from the plaintext to round 2', [
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
        P('Multiply the first column (63, 53, E0, 8C) by the fixed multiplier (02, 01, 01, 03). For example, c₁ = 02 · 53 ⊕ 01 · 63 = A6 ⊕ 63 = C5.'),
        C('ALL SEVEN COEFFICIENTS BEFORE REDUCTION',
          'Power of y      0     1     2     3     4     5     6\n'
          'Coefficient    C6    C5    EB    15    99    B7    8F', 18),
        C('FOLD THE LAST THREE COEFFICIENTS BACK INTO THE FIRST THREE',
          'd₀ = C6 ⊕ 99 = 5F       d₁ = C5 ⊕ B7 = 72\n'
          'd₂ = EB ⊕ 8F = 64       d₃ = 15', 19),
    ], section='APPENDIX', take='The polynomial and matrix calculations give the same output column, 5F 72 64 15.',
        notes='Compare the result with the first MixColumns matrix multiplication. For example, the last product coefficient equals 03·8C = 8F.', minutes=0),
    slide('Why the fixed column multiplier has an inverse', [
        P('In characteristic two, y⁴ + 1 = (y + 1)⁴. A polynomial shares a factor with this modulus exactly when y + 1 divides it, which is equivalent to having value 0 at y = 1.'),
        M(r'B(1)=\mathtt{02}\oplus\mathtt{01}\oplus\mathtt{01}\oplus\mathtt{03}=\mathtt{01}'),
        P('Thus B(y) is relatively prime to y⁴ + 1. The extended Euclidean algorithm gives a polynomial inverse. Its four coefficients define InvMixColumns.'),
        M(r'B^{-1}(y)=\mathtt{0E}+\mathtt{09}y+\mathtt{0D}y^2+\mathtt{0B}y^3'
          r'\pmod{y^4+1}'),
    ], section='APPENDIX', take='The column ring contains noninvertible elements. The multiplier selected for MixColumns is invertible.',
        notes='For a contrasting example, the fourth power of the nonzero element y+1 is zero in this ring. The polynomial Euclidean algorithm used for a byte inverse also applies over the field of byte coefficients.', minutes=0),
]
