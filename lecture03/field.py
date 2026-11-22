"""AES byte arithmetic, with examples carried forward into the round."""
from deck_schema import C, M, P, T, slide


def lesson(title, blocks, minutes, notes, take=''):
    return slide(title, blocks, section='BYTE ARITHMETIC', minutes=minutes,
                 notes=notes, take=take)


slides = [
    lesson('What does a field let us do?', [
        P('In SubBytes we will need the multiplicative inverse of a byte. Which algebraic rules guarantee that we can find one?'),
        T(['Structure', 'Rules we will use', 'Familiar example'], [
            ['Group', 'A closed, associative operation has an identity and an inverse for each element.', 'Integers under addition. The inverse of 3 is −3.'],
            ['Ring with identity', 'Addition is a commutative group. Multiplication is closed and associative, has an identity, and distributes over addition.', 'Integers with addition and multiplication.'],
            ['Field', 'A commutative ring with 0 ≠ 1. Every nonzero element has a multiplicative inverse.', 'Rational numbers. The inverse of 3 is 1/3.'],
        ], [1.05, 3.8, 2.1]),
    ], 3, 'Start with the distinction between an additive inverse and a multiplicative inverse. In a ring the latter may exist for some elements. In a field it exists for every nonzero element.'),

    lesson('Start with arithmetic on one bit', [
        P('GF means Galois field, a field with finitely many elements. Its size is a prime power. In GF(2) the elements are 0 and 1, and both operations use the remainder modulo 2.'),
        T(['Operation', '0 with 0', '0 with 1', '1 with 0', '1 with 1'], [
            ['Add (XOR)', '0', '1', '1', '0'],
            ['Multiply (AND)', '0', '0', '0', '1'],
        ]),
        P('For a larger example, 3 has inverse 5 modulo 7 because 3 × 5 = 15 leaves remainder 1. Modulo 6, every multiple of 2 is even, so 2 has no inverse.'),
    ], 2, 'Ask which entry in the first row changes ordinary polynomial addition. The answer is 1 + 1 = 0. In GF(7) every nonzero element is invertible since 7 is prime.'),

    lesson('Find an inverse by tracing remainders', [
        P('Which integer multiplied by 12 leaves remainder 1 modulo 5? Euclid’s algorithm finds the greatest common divisor. Its extended form expresses that divisor in terms of the two inputs.'),
        C('DIVIDE, THEN SUBSTITUTE BACK', '12 = 2 × 5 + 2      5 = 2 × 2 + 1      2 = 2 × 1 + 0\n 1 = 5 − 2 × 2 = 5 − 2(12 − 2 × 5) = 5 × 5 − 2 × 12', 18),
        P('Reduce the last equality modulo 5. The term 5 × 5 vanishes, leaving 1 ≡ (−2) × 12. Since −2 ≡ 3 modulo 5, the inverse is 3. Indeed, 12 × 3 = 36 = 7 × 5 + 1.'),
    ], 4, 'Underline the last nonzero remainder, then label the coefficient of 12. This Bézout identity is the template for finding an inverse of a polynomial later.'),

    lesson('Read a byte as a polynomial', [
        P('One hexadecimal digit encodes four bits. The byte 57 in hexadecimal is 0101 0111 in binary. The rightmost bit is the coefficient of the constant term.'),
        C('THE SAME BYTE IN THREE REPRESENTATIONS', 'Hex digits       5       7\nPower of x       7 6 5 4   3 2 1 0\nCoefficient      0 1 0 1   0 1 1 1'),
        M(r'\mathtt{57}\quad\longleftrightarrow\quad x^6+x^4+x^2+x+1'),
    ], 3, 'Read the coefficient row from left to right. Point to each 1, and write its term. On subsequent slides two-character byte values are hexadecimal.', 'Eight binary coefficients give 256 possible bytes.'),

    lesson('Add bytes one coefficient at a time', [
        P('Add 57 and 83 in the AES byte field. Their binary polynomials have coefficients in GF(2), so two copies of a term cancel.'),
        C('ALIGN CORRESPONDING POWERS', '57       0101 0111\n83   XOR 1000 0011\n         ---------\nD4       1101 0100'),
        P('Both inputs contain x and 1. These terms cancel. The remaining powers are 7, 6, 4 and 2, giving D4.'),
    ], 2, 'Ask for the low two bits before revealing why they are both zero. The additive inverse of any byte equals that same byte.'),

    lesson('Keep a product inside one byte', [
        P('Two byte polynomials can multiply to a degree above seven. AES divides the product by a fixed polynomial and keeps the remainder.'),
        M(r'm(x)=x^8+x^4+x^3+x+1\quad(\text{binary }100011011=\text{hex }\mathtt{11B})'),
        M(r'\mathrm{GF}(2^8)=\mathrm{GF}(2)[x]/(m(x))'),
        P('The quotient identifies binary polynomials with the same remainder. The modulus is irreducible, meaning it has no factorisation into lower-degree nonconstant binary polynomials. This guarantees a multiplicative inverse for each nonzero byte.'),
    ], 3, 'Define irreducible as having no factorisation into two lower-degree nonconstant binary polynomials. Give the prime integer analogy if needed. AES fixes this particular irreducible polynomial.'),

    lesson('Multiply by 02 with one shift', [
        P('The byte 02 represents x. Multiplying by x shifts each coefficient up one power. If an x⁸ term appears, cancel it by adding the modulus 11B.'),
        T(['Input', 'Shift left, keeping the extra bit', 'Remainder in one byte'], [
            ['57 = 0101 0111', '0 1010 1110 = 0AE', 'AE (degree below 8)'],
            ['AE = 1010 1110', '1 0101 1100 = 15C', '15C XOR 11B = 047, giving 47'],
        ], [1.25, 2.05, 2.4]),
        P('In an eight-bit register the extra bit falls away. If the original high bit was 1, XOR the low eight bits with 1B. AES calls this calculation xtime.'),
    ], 3, 'In the second row trace the outgoing high bit. Cancel the degree-eight term by XORing 11B. Discarding the extra bit and XORing 1B has the same effect.'),

    lesson('Try two products with the same byte', [
        P('Work with a partner for three minutes. Write each byte in hexadecimal and keep the intermediate shift.'),
        C('INPUT BYTE', '83 = 1000 0011'),
        P('<b>1.</b> Find 02 · 83. Does the shift create a ninth bit? Show the reduction if it does.'),
        P('<b>2.</b> Find 03 · 83 using your first answer. The byte 03 represents x + 1.'),
    ], 4, 'Give three minutes of calculation time and one minute to compare methods. Ask pairs to predict which operation undoes addition of the modulus.'),

    lesson('Use the first product to get the second', [
        C('02 TIMES 83', 'Shift left         1 0000 0110   = 106\nReduce             106 XOR 11B   = 01D'),
        M(r'\mathtt{03}\cdot\mathtt{83}=(x+1)\cdot\mathtt{83}=(\mathtt{02}\cdot\mathtt{83})\oplus\mathtt{83}'),
        C('03 TIMES 83', '1D XOR 83 = 0001 1101 XOR 1000 0011 = 1001 1110 = 9E', 18),
    ], 2, 'Ask a student to explain why the second line distributes. This shortcut for multiplication by 03 will appear in the MixColumns matrix.'),

    lesson('Which partial products do we need?', [
        P('To multiply 57 by 83, look for the 1s in the multiplier. The byte 83 has a 1 in positions 7, 1 and 0, counting from the right starting at 0.'),
        C('DECODE THE MULTIPLIER', '83 = 1000 0011   →   x⁷ + x + 1'),
        M(r'\mathtt{57}\cdot\mathtt{83}=x^7\cdot\mathtt{57}\;\oplus\;x\cdot\mathtt{57}\;\oplus\;\mathtt{57}\pmod{m(x)}'),
        P('Start at 57 and apply xtime repeatedly. Save the starting byte and the values after one and seven shifts.'),
    ], 3, 'Pause for the class to choose three powers of x. Distinguish polynomial bit positions from the bit numbering used in DES permutations. Here position j is the exponent of x.'),

    lesson('Follow seven shifts from 57', [
        P('Each arrow multiplies the current byte by x and reduces the result. A high input bit of 1 triggers the XOR with 1B.'),
        C('POWER OF x MULTIPLYING 57', 'Power     0     1     2     3     4     5     6     7\nByte     57 →  AE →  47 →  8E →  07 →  0E →  1C →  38', 18),
        P('For the step from power 3 to 4, shift 8E to 11C. Cancel the high bit by computing 11C XOR 11B = 07. The next three shifts all fit in one byte.'),
    ], 3, 'Have students fill in 07 before following the last three arrows. The three values selected by the multiplier are 38, AE and 57.'),

    lesson('Combine the three selected bytes', [
        C('SELECT POWERS 7, 1 AND 0', 'x⁷ · 57   38      0011 1000\nx  · 57   AE      1010 1110\n1  · 57   57      0101 0111'),
        C('ADD THE PARTIAL PRODUCTS USING XOR', '38 XOR AE = 96       96 XOR 57 = C1'),
        P('The AES byte product of 57 and 83 is C1. The same method works for any two bytes.'),
    ], 2, 'Carry out one XOR nibble by nibble. All partial products have already been reduced. Their XOR fits in eight bits.'),

    lesson('What would it mean to invert 05?', [
        P('To construct the S-box entry for 05, the first step is to find a byte that gives 01 when multiplied by 05. Write b(x) = x² + 1 for the byte 05.'),
        M(r'b(x)d(x)+m(x)c(x)=1\quad\Longrightarrow\quad b(x)d(x)\equiv 1\pmod{m(x)}'),
        P('This is the polynomial version of the integer inverse calculation. Irreducibility of m guarantees that its greatest common divisor with a nonzero byte polynomial is 1.'),
    ], 3, 'Point to d(x), the coefficient of the byte polynomial. It plays the same role as the coefficient −2 of 12 in the integer example. A zero input requires the special S-box convention.'),

    lesson('Divide the AES modulus by x² + 1', [
        P('At each step, cancel the leading term using a shifted copy of b(x). Hexadecimal values below encode the coefficients, including the ninth bit when present.'),
        T(['Current polynomial', 'Choose quotient term', 'XOR its multiple of 05', 'Remainder'], [
            ['11B, degree 8', 'x⁶ (8 − 2 = 6)', '11B XOR 140', '05B, degree 6'],
            ['05B, degree 6', 'x⁴ (6 − 2 = 4)', '05B XOR 050', '00B, degree 3'],
            ['00B, degree 3', 'x (3 − 2 = 1)', '00B XOR 00A', '001, degree 0'],
        ], [1.25, 1.45, 1.4, 1.35]),
        M(r'm(x)=(x^6+x^4+x)b(x)+1'),
    ], 4, 'Explain 140 by shifting binary 101 left six positions. Read the chosen terms down the middle column. The remainder 1 has degree below the divisor and is the last nonzero remainder.'),

    lesson('Read the inverse and check it', [
        P('Modulo m(x), the division identity gives (x⁶ + x⁴ + x)b(x) = 1. Since 1 + 1 = 0 in GF(2), each polynomial is its own additive inverse.'),
        C('ENCODE THE QUOTIENT', 'x⁶ + x⁴ + x   →   0101 0010   →   52'),
        C('CHECK 05 TIMES 52 USING 05 = x² + 1', 'xtime(52) = A4       xtime(A4) = 48 XOR 1B = 53\n05 · 52   = 53 XOR 52 = 01', 18),
        P('Thus 52 is the inverse of 05. The S-box will apply one further transformation to 52.'),
    ], 3, 'Show the difference between an inverse and an S-box output. The reference example is completed when 52 is put through the affine transformation.'),

    lesson('Where do these operations appear in AES?', [
        T(['Arithmetic we can now do', 'Where it enters a round'], [
            ['Add two byte polynomials by XOR.', 'AddRoundKey combines each state byte with one key byte.'],
            ['Find a nonzero byte’s multiplicative inverse.', 'SubBytes uses that inverse to construct a substitution.'],
            ['Multiply by 02 or 03 and add the products.', 'MixColumns combines all four bytes of a state column.'],
        ], [1.95, 2.65]),
        P('Keep 05 → 52 and the xtime rule in your notes. We will use both when we read an AES round.'),
    ], 2, 'Ask the class to match each operation to the part of the cipher that uses it. Remind them that ordinary integer multiplication modulo 256 would fail to supply an inverse for an even byte such as 52.'),
]


appendix = [
    slide('Which binary polynomials are irreducible?', [
        P('An irreducible polynomial over GF(2) has no factorisation into lower-degree nonconstant polynomials with coefficients in GF(2).'),
        T(['Polynomial', 'What to check', 'Result over GF(2)'], [
            ['x² + 1', 'At x = 1 the value is 0.', '(x + 1)²'],
            ['x³ + 1', 'At x = 1 the value is 0.', '(x + 1)(x² + x + 1)'],
            ['x⁴ + 1', 'Square x² + 1.', '(x + 1)⁴'],
            ['x² + x + 1', 'Its value at both 0 and 1 is 1.', 'Irreducible. A reducible quadratic has a linear factor.'],
        ], [1.1, 1.85, 2.7]),
        P('The degree-eight AES modulus is irreducible. At degree eight, testing for roots alone only rules out linear factors.'),
    ], section='APPENDIX', minutes=0, notes='Extra examples adapted from the supplied AES reference. Contrast the byte modulus with the reducible column modulus used in MixColumns.'),
    slide('A second integer inverse by back-substitution', [
        C('FIND THE LAST NONZERO REMAINDER', '45 = 2 × 19 + 7      19 = 2 × 7 + 5\n 7 = 1 × 5  + 2       5 = 2 × 2 + 1'),
        C('WRITE 1 IN TERMS OF 45 AND 19', '1 = 5 − 2(7 − 5) = 3 × 5 − 2 × 7\n  = 3(19 − 2 × 7) − 2 × 7 = 3 × 19 − 8 × 7\n  = 3 × 19 − 8(45 − 2 × 19) = 19 × 19 − 8 × 45', 17),
        P('Read the coefficient of 45. Its inverse modulo 19 is −8 ≡ 11. Indeed, 45 × 11 = 495 = 26 × 19 + 1.'),
    ], section='APPENDIX', minutes=0, notes='Optional independent practice with the second pair of integers in the supplied reference.'),
]
