"""AES byte arithmetic, with examples carried forward into the round."""
from deck_schema import C, M, P, T, slide


def lesson(title, blocks, minutes, notes, take='', *, focus='math_byte'):
    item = slide(title, blocks, section='BYTE ARITHMETIC', minutes=minutes,
                 notes=notes, take=take)
    item['aes_focus'] = focus
    return item


slides = [
    lesson('What does a field let us do?', [
        P('In SubBytes we will need the multiplicative inverse of a byte. Which algebraic rules guarantee that we can find one?'),
        ('algebra_table', ['Structure', 'Formal definition', 'Rules we will use', 'Familiar example'], [
            ['Group',
             '(G, ∗) with an operation ∗: G × G → G.\n'
             '∀a, b, c ∈ G, (a ∗ b) ∗ c = a ∗ (b ∗ c).\n'
             '∃e ∈ G, ∀a ∈ G, e ∗ a = a ∗ e = a.\n'
             '∀a ∈ G, ∃a⁻¹ ∈ G, a ∗ a⁻¹ = a⁻¹ ∗ a = e.',
             'A closed, associative operation has an identity and an inverse for each element.',
             'Integers under addition. The inverse of 3 is −3.'],
            ['Ring with identity',
             '(R, +) is a group, and ∀a, b ∈ R, a + b = b + a.\n'
             '·: R × R → R, with (ab)c = a(bc) ∀a, b, c ∈ R.\n'
             '∃1 ∈ R, ∀a ∈ R, 1a = a1 = a.\n'
             '∀a, b, c ∈ R, a(b + c) = ab + ac\n'
             'and (a + b)c = ac + bc.',
             'Addition is a commutative group. Multiplication is closed and associative, has an identity, and distributes over addition.',
             'Integers with addition and multiplication.'],
            ['Field',
             '(F, +, ·) is a ring with identity.\n'
             '0 ≠ 1 and ab = ba for all a, b ∈ F.\n'
             '∀a ∈ F with a ≠ 0, ∃a⁻¹ ∈ F\n'
             'such that aa⁻¹ = a⁻¹a = 1.',
             'A commutative ring with 0 ≠ 1. Every nonzero element has a multiplicative inverse.',
             'Rational numbers. The inverse of 3 is 1/3.'],
        ]),
        P('The symbol ∀ means “for all”. The symbol ∃ means “there exists”.'),
    ], 3, 'Introduce each formal definition before reading its rules and example across the row. A binary operation maps a pair of elements back into the same set, which states closure. Read the universal and existential quantifiers aloud. A group has one operation, with a two-sided identity and two-sided inverses. For the ring, addition forms an abelian group and multiplication has its own identity. Both distributive laws hold. For a field, multiplication also commutes, 0 and 1 are distinct, and every nonzero element has a multiplicative inverse. Relate the additive inverse −3 in the integers to the multiplicative inverse 1/3 in the rationals.'),

    lesson('Why do repeated divisions find the gcd?', [
        P('For positive integers a and b, divide a by b. The quotient q counts whole copies of b and the remainder r is smaller than b.'),
        M(r'a=qb+r,\quad 0\leq r<b,\qquad \gcd(a,b)=\gcd(b,r).'),
        P('Any divisor of a and b also divides r = a − qb. Conversely, any divisor of b and r divides a = qb + r. The two pairs have exactly the same common divisors.'),
        P('Replace (a, b) by (b, r). The positive remainders strictly decrease, so eventually a remainder is zero. The last nonzero remainder is the gcd.'),
    ], 3, 'Work through the divisor argument in both directions. With the final pair (d, 0), the greatest common divisor is d. The same reasoning will apply to polynomial remainders.', focus='math_inverse'),

    lesson('Find an inverse by tracing remainders', [
        P('Which integer multiplied by 12 leaves remainder 1 modulo 5? Apply Euclid’s algorithm to 12 and 5. Then express the last nonzero remainder using the original two numbers.'),
        C('DIVIDE, THEN SUBSTITUTE BACK', '12 = 2 × 5 + 2      5 = 2 × 2 + 1      2 = 2 × 1 + 0\n 1 = 5 − 2 × 2 = 5 − 2(12 − 2 × 5) = 5 × 5 − 2 × 12', 18),
        P('The last nonzero remainder is 1, so gcd(12, 5) = 1. The equation 1 = (−2) × 12 + 5 × 5 expresses the gcd as a combination of the inputs. This is a Bézout identity.'),
    ], 4, 'Underline the last nonzero remainder, then label the coefficient of 12. This Bézout identity is the template for finding an inverse of a polynomial later.', focus='math_inverse'),

    lesson('One Bézout identity gives two inverses', [
        M(r'1=ax+by\quad\Longrightarrow\quad ax\equiv1\pmod b,\qquad by\equiv1\pmod a.'),
        P('The coefficient of a is its inverse modulo b. Swap the roles of a and b to read the other inverse. This works when their gcd is 1.'),
        T(['Read 1 = (−2) × 12 + 5 × 5', 'Coefficient', 'Check the remainder'], [
            ['Inverse of 12 modulo 5', '−2 ≡ 3 modulo 5', '12 × 3 = 36 = 7 × 5 + 1'],
            ['Inverse of 5 modulo 12', '5', '5 × 5 = 25 = 2 × 12 + 1'],
        ], [1.9, 1.35, 2.1]),
    ], 2, 'Cover the middle column and ask for the second inverse. Distinguish the coefficient of an input from the modulus used when reading that coefficient.', focus='math_inverse'),

    lesson('Track the coefficients at each division', [
        P('Instead of substituting backwards, write each remainder as rᵢ = sᵢa + tᵢb. Start with a and b themselves.'),
        M(r'(r_0,s_0,t_0)=(a,1,0),\qquad(r_1,s_1,t_1)=(b,0,1).'),
        P('For each nonzero current remainder, take q = ⌊rᵢ₋₁ / rᵢ⌋. Subtract q copies of the current row from the preceding row, including its two coefficients.'),
        M(r'\begin{aligned}r_{i+1}&=r_{i-1}-qr_i,\\(s_{i+1},t_{i+1})&=(s_{i-1},t_{i-1})-q(s_i,t_i).\end{aligned}'),
    ], 3, 'After the first two rows, each update preserves r = sa + tb. The coefficients in the last nonzero row form a Bézout identity. Floor brackets mean round the nonnegative quotient down.', focus='math_inverse'),

    lesson('Run the coefficient table for 45 and 19', [
        P('Read each new coefficient pair from the two rows above it. The quotient shown on a row is the one used to produce that row.'),
        T(['Remainder r', 'Division step', 's', 't', 'Check r = 45s + 19t'], [
            ['45', 'Initial a', '1', '0', '45'],
            ['19', 'Initial b', '0', '1', '19'],
            ['7',  '45 − 2 × 19', '1', '−2', '45 − 38 = 7'],
            ['5',  '19 − 2 × 7', '−2', '5', '−90 + 95 = 5'],
            ['2',  '7 − 1 × 5', '3', '−7', '135 − 133 = 2'],
            ['1',  '5 − 2 × 2', '−8', '19', '−360 + 361 = 1'],
        ], [1.1, 1.55, .65, .65, 1.9]),
    ], 3, 'For the row with remainder 5, use (0,1) − 2(1,−2) = (−2,5). Have the class compute the final coefficient pair. The next division, 2 = 2 × 1 + 0, stops the algorithm.', focus='math_inverse'),

    lesson('Recover both inverses for 45 and 19', [
        M(r'1=(-8)\cdot45+19\cdot19.'),
        P('Modulo 19, the second term disappears. The coefficient −8 is equivalent to 11, so 45 has inverse 11 modulo 19.'),
        P('Modulo 45, the first term disappears. The coefficient 19 gives the inverse of 19 modulo 45.'),
        C('CHECK BOTH PRODUCTS', '45 × 11 = 495 = 26 × 19 + 1\n19 × 19 = 361 =  8 × 45 + 1', 19),
    ], 2, 'The appendix repeats this example using back-substitution so students can compare the two ways of finding the coefficients.', focus='math_inverse'),

    lesson('What makes an operation a group?', [
        P('Let G be a set with a binary operation, written here as a · b. A group satisfies all four rules.'),
        T(['Rule', 'What must hold for elements of G'], [
            ['Closure', 'For every a and b in G, the result a · b belongs to G.'],
            ['Associativity', '(a · b) · c = a · (b · c) for every a, b and c.'],
            ['Identity', 'There is an e in G with a · e = e · a = a for every a.'],
            ['Inverse', 'Every a has a b in G such that a · b = b · a = e.'],
        ], [1, 4.2]),
        P('When a · b = b · a for all elements, the group is also called abelian.'),
    ], 2, 'Under addition replace the dot by plus and e by 0. Under multiplication the identity is 1. The examples on the next slide test whether inverses stay in the chosen set.'),

    lesson('Test the inverse in three familiar sets', [
        T(['Set and operation', 'Test', 'Conclusion'], [
            ['All integers, addition', 'The identity is 0. For any integer a, its inverse −a is another integer.', 'Abelian group'],
            ['Nonnegative integers, addition', 'An inverse of 3 would be −3, outside the set.', 'Fails the inverse rule'],
            ['All integers, multiplication', 'An inverse of 2 would satisfy 2b = 1. No integer b does.', 'Fails the inverse rule'],
        ], [1.45, 2.9, 1.35]),
        P('The same set can behave differently when the operation changes. Keep the operation in view when asking for an inverse.'),
    ], 2, 'For the additive integer group, check closure and associativity as well. Ask which rational number would invert 2 under multiplication.'),

    lesson('A ring has two operations', [
        P('We use rings with a multiplicative identity. Addition makes the set an abelian group, with additive identity 0.'),
        P('Multiplication is closed and associative and has an identity 1. It distributes over addition in both directions.'),
        M(r'a(b+c)=ab+ac,\qquad (a+b)c=ac+bc.'),
        P('Integers, real numbers and complex numbers are rings under their usual operations. Square matrices of a fixed size over the real numbers also form a ring.'),
    ], 2, 'Integers supply the simplest example. Matrices motivate having both distributive laws because general matrix multiplication may change when factors are exchanged.'),

    lesson('Which rings are fields?', [
        P('A field is a commutative ring with distinct elements 0 and 1. Its nonzero elements form an abelian group under multiplication.'),
        T(['Set', 'Can every nonzero element a be inverted?', 'Structure'], [
            ['Rational numbers ℚ', 'Yes. If a = m/n with m and n nonzero, n/m is its inverse.', 'Field'],
            ['Real numbers ℝ', 'Yes. For every nonzero real a, its reciprocal 1/a is real.', 'Field'],
            ['Integers ℤ', 'The reciprocal of 2 is 1/2, outside ℤ.', 'Ring'],
        ], [1.4, 3.1, .85]),
        P('These examples have infinitely many elements. AES uses a field that fits into one byte.'),
    ], 2, 'Ask why zero is excluded. Its product with any element is zero, while the required multiplicative identity is one.'),

    lesson('How many elements can a finite field have?', [
        P('A finite field is a field with finitely many elements. GF stands for Galois field.'),
        M(r'\text{For each prime }p\text{ and integer }n\ge1,\quad\mathrm{GF}(p^n)\text{ exists and has }p^n\text{ elements.}'),
        P('Every finite field has a prime-power size. With p = 7 and n = 1 we can use integer arithmetic modulo 7. With p = 2 and n = 8 we will represent elements by eight binary coefficients.'),
        P('Integer arithmetic modulo 256 has 256 residues, but 2 has no multiplicative inverse there. AES therefore needs a different rule for multiplication.'),
    ], 2, 'A field of a given prime-power order is unique up to isomorphism. Different encodings can give different bit patterns for products. AES selects a particular polynomial encoding.'),

    lesson('Start with arithmetic on one bit', [
        P('In GF(2) the elements are 0 and 1. Addition and multiplication use the remainder modulo 2. Each table entry gives the result on the two inputs named at the top.'),
        T(['Operation', '0 with 0', '0 with 1', '1 with 0', '1 with 1'], [
            ['Add (XOR)', '0', '1', '1', '0'],
            ['Multiply (AND)', '0', '0', '0', '1'],
        ]),
        P('Each bit added to itself gives zero. The only nonzero element is 1, and 1 × 1 = 1. We will use these two rules for the coefficients of AES byte polynomials.'),
    ], 2, 'Ask which entry in the first row changes ordinary polynomial addition. The answer is 1 + 1 = 0. In GF(7) every nonzero element is invertible since 7 is prime.'),

    lesson('Compare the arithmetic modulo 7 and modulo 6', [
        T(['Modulus', 'Elements', 'Example calculation'], [
            ['7', '0, 1, 2, 3, 4, 5, 6', '4 + 5 ≡ 2 and 3 × 5 ≡ 1 modulo 7.'],
            ['6', '0, 1, 2, 3, 4, 5', '2 × 0, 2 × 1, …, 2 × 5 give residues 0, 2, 4, 0, 2, 4.'],
        ], [1.05, 1.55, 3.3]),
        P('Modulo 7 every nonzero residue is coprime to 7. The extended Euclidean algorithm therefore supplies each inverse. These residues form GF(7).'),
        P('Modulo 6, no product with 2 gives 1. The six residues form a ring in which 2 has no multiplicative inverse.'),
    ], 2, 'Ask for the inverse of 3 modulo 7. Then ask where a 1 would have to appear in the second row to make 2 invertible.'),

    lesson('Encode an element of the AES byte field', [
        P('The AES field extends GF(2). Each element has a unique polynomial representative of degree at most seven, or the zero polynomial. Its coefficients are bits.'),
        M(r'b(x)=b_7 x^7+b_6x^6+\cdots+b_1x+b_0,\qquad b_i\in\{0,1\}.'),
        C('READ THE COEFFICIENTS FROM HIGH POWER TO LOW POWER', '00 = 0000 0000   zero polynomial\n01 = 0000 0001   constant polynomial 1\nFF = 1111 1111   all eight coefficients equal 1', 18),
        P('Eight independent binary choices give 2⁸ = 256 encodings. Each group of four bits becomes one hexadecimal digit.'),
    ], 2, 'The one-byte representation includes all-zero coefficients. Count the number of choices without assigning the product rule of the integers modulo 256 to these encodings.'),

    lesson('Read a byte as a polynomial', [
        P('One hexadecimal digit encodes four bits. The byte 57 in hexadecimal is 0101 0111 in binary. The rightmost bit is the coefficient of the constant term.'),
        C('THE SAME BYTE IN THREE REPRESENTATIONS', 'Hex digits       5       7\nPower of x       7 6 5 4   3 2 1 0\nCoefficient      0 1 0 1   0 1 1 1'),
        M(r'\mathtt{57}\quad\longleftrightarrow\quad x^6+x^4+x^2+x+1'),
    ], 3, 'Read the coefficient row from left to right. Point to each 1, and write its term. On subsequent slides two-character byte values are hexadecimal.', 'Eight binary coefficients give 256 possible bytes.'),

    lesson('Match hexadecimal digits to four bits', [
        P('Hexadecimal is base 16. Digits A through F stand for the values ten through fifteen. The prefix 0x is one way to mark a hexadecimal value.'),
        C('ONE DIGIT ENCODES FOUR BITS', '0  0000     4  0100     8  1000     C  1100\n1  0001     5  0101     9  1001     D  1101\n2  0010     6  0110     A  1010     E  1110\n3  0011     7  0111     B  1011     F  1111', 19),
        P('For example, 0x83 gives 1000 0011. Its 1s occur at powers 7, 1 and 0, so its polynomial is x⁷ + x + 1.'),
    ], 2, 'Use the table to have the class translate D4 as two four-bit groups. The notation {57} in the supplied reference is also a hexadecimal byte.'),

    lesson('Add bytes one coefficient at a time', [
        P('Add 57 and 83 in the AES byte field. Their binary polynomials have coefficients in GF(2), so two copies of a term cancel.'),
        C('ALIGN CORRESPONDING POWERS', '57       0101 0111\n83   XOR 1000 0011\n         ---------\nD4       1101 0100'),
        M(r'(x^6+x^4+x^2+x+1)+(x^7+x+1)=x^7+x^6+x^4+x^2.'),
        P('The repeated x terms and constants cancel. In general a ⊕ 00 = a and a ⊕ a = 00. Each byte is its own additive inverse.'),
    ], 2, 'Ask for the low two bits before revealing why they are both zero. The additive inverse of any byte equals that same byte.'),

    lesson('Keep a product inside one byte', [
        P('Two byte polynomials can multiply to a degree above seven. AES divides the product by a fixed polynomial and keeps the remainder.'),
        M(r'm(x)=x^8+x^4+x^3+x+1\quad(\text{binary }100011011=\text{hex }\mathtt{11B})'),
        M(r'\mathrm{GF}(2^8)=\mathrm{GF}(2)[x]/(m(x))'),
        P('The quotient identifies binary polynomials with the same remainder. There are 30 irreducible degree-eight polynomials over GF(2). AES uses the one shown here. With this modulus every nonzero byte has an inverse.'),
    ], 3, 'Define irreducible as having no factorisation into two lower-degree nonconstant binary polynomials. Give the prime integer analogy if needed. AES fixes this particular irreducible polynomial.'),

    lesson('Try factoring four binary polynomials', [
        P('Over GF(2), an irreducible polynomial has no factorisation into two nonconstant polynomials of smaller degree. Which of these four are irreducible?'),
        M(r'x^2+1,\qquad x^3+1,\qquad x^4+1,\qquad x^2+x+1.'),
        P('For each polynomial, first evaluate it at 0 and 1. A root at 0 gives a factor x. A root at 1 gives a factor x + 1, because 1 = −1 in GF(2).'),
        P('If a quadratic factors, it must have a linear factor. Use this fact to decide the last case.'),
    ], 3, 'Give students two minutes in pairs. Ask them to exhibit a factor when they claim reducibility, and to justify the irreducible case.'),

    lesson('Read the factors and the irreducible case', [
        T(['Polynomial', 'Evidence in GF(2)', 'Conclusion'], [
            ['x² + 1', '(x + 1)² = x² + 2x + 1 = x² + 1.', 'Reducible'],
            ['x³ + 1', '(x + 1)(x² + x + 1) = x³ + 1.', 'Reducible'],
            ['x⁴ + 1', '(x + 1)⁴ = (x² + 1)² = x⁴ + 1.', 'Reducible'],
            ['x² + x + 1', 'The value is 1 at both 0 and 1. A factorisation of this quadratic would have a linear factor.', 'Irreducible'],
        ], [1.05, 3.25, 1.05]),
        P('The third example will return in MixColumns, where a different variable describes the position of a byte in a column.'),
    ], 2, 'The calculation (x + 1)² uses the cancellation of 2x. A root test suffices for a quadratic or cubic since a proper factorisation must then have a linear factor.'),

    lesson('Multiply by 02 with one shift', [
        P('The byte 02 represents x. Multiplying by x shifts each coefficient up one power. If an x⁸ term appears, cancel it by adding the modulus 11B.'),
        T(['Input', 'Shift left, keeping the extra bit', 'Remainder in one byte'], [
            ['57 = 0101 0111', '0 1010 1110 = 0AE', 'AE (degree below 8)'],
            ['AE = 1010 1110', '1 0101 1100 = 15C', '15C XOR 11B = 047, giving 47'],
        ], [1.25, 2.05, 2.4]),
    ], 3, 'In the second row trace the outgoing high bit. Cancel the degree-eight term by XORing 11B. Discarding the extra bit and XORing 1B has the same effect.', focus='math_product'),

    lesson('Try two products with the same byte', [
        P('Work with a partner for three minutes. Write each byte in hexadecimal and keep the intermediate shift.'),
        C('INPUT BYTE', '83 = 1000 0011'),
        P('<b>1.</b> Find 02 · 83. Does the shift create a ninth bit? Show the reduction if it does.'),
        P('<b>2.</b> Find 03 · 83 using your first answer. The byte 03 represents x + 1.'),
    ], 4, 'Give three minutes of calculation time and one minute to compare methods. Ask pairs to predict which operation undoes addition of the modulus.', focus='math_product'),

    lesson('Use the first product to get the second', [
        C('02 TIMES 83', 'Shift left         1 0000 0110   = 106\nReduce             106 XOR 11B   = 01D'),
        M(r'\mathtt{03}\cdot\mathtt{83}=(x+1)\cdot\mathtt{83}=(\mathtt{02}\cdot\mathtt{83})\oplus\mathtt{83}'),
        C('03 TIMES 83', '1D XOR 83 = 0001 1101 XOR 1000 0011 = 1001 1110 = 9E', 18),
    ], 2, 'Ask a student to explain why the second line distributes. This shortcut for multiplication by 03 will appear in the MixColumns matrix.', focus='math_product'),

    lesson('Which partial products do we need?', [
        P('To multiply 57 by 83, look for the 1s in the multiplier. The byte 83 has a 1 in positions 7, 1 and 0, counting from the right starting at 0.'),
        C('DECODE THE MULTIPLIER', '83 = 1000 0011   →   x⁷ + x + 1'),
        M(r'\mathtt{57}\cdot\mathtt{83}=x^7\cdot\mathtt{57}\;\oplus\;x\cdot\mathtt{57}\;\oplus\;\mathtt{57}\pmod{m(x)}'),
        P('Start at 57 and apply xtime repeatedly. Save the starting byte and the values after one and seven shifts.'),
    ], 3, 'Pause for the class to choose three powers of x. Distinguish polynomial bit positions from the bit numbering used in DES permutations. Here position j is the exponent of x.', focus='math_product'),

    lesson('Follow seven shifts from 57', [
        P('Each step multiplies by x. Keep the ninth bit until reduction. A leading 1 requires XOR with 11B. For 83 = x⁷ + x + 1, save powers 0, 1 and 7.'),
        ('xtime_chain', 0x57, (0, 1, 7)),
    ], 3, 'Read each row from left to right. Begin with 57 = 01010111 and shift left to get 0 10101110. The result AE already fits in eight bits. Next, AE shifts to 1 01011100 = 15C. XOR 11B to cancel the ninth bit and obtain 047, stored as 47. The same reduction turns 11C into 007 after shifting 8E. Preserve the leading zeros in 07 and 0E. The highlighted results at powers 0, 1 and 7 are 57, AE and 38. XOR them on the next slide.', focus='math_product'),

    lesson('Combine the three selected bytes', [
        C('SELECT POWERS 7, 1 AND 0', 'x⁷ · 57   38      0011 1000\nx  · 57   AE      1010 1110\n1  · 57   57      0101 0111'),
        C('ADD THE PARTIAL PRODUCTS USING XOR', '38 XOR AE = 96       96 XOR 57 = C1'),
        P('The AES byte product of 57 and 83 is C1. The same method works for any two bytes.'),
    ], 2, 'Carry out one XOR nibble by nibble. All partial products have already been reduced. Their XOR fits in eight bits.', focus='math_product'),

    lesson('Multiply 57 by 83 directly as polynomials', [
        P('We can check C1 by leaving reduction until the end. Write A = x⁶ + x⁴ + x² + x + 1 for 57. The three terms of 83 give three shifted copies of A.'),
        M(r'\begin{aligned} x^7 A&=x^{13}+x^{11}+x^9+x^8+x^7,\\ x A&=x^7+x^5+x^3+x^2+x,\\ A&=x^6+x^4+x^2+x+1.\end{aligned}'),
        P('Add the rows. Powers 7, 2 and 1 each occur twice and cancel. The sum is the unreduced product, with degree 13.'),
        M(r'P(x)=x^{13}+x^{11}+x^9+x^8+x^6+x^5+x^4+x^3+1.'),
    ], 3, 'Trace the duplicated terms in the three rows before collecting coefficients. The expanded product is encoded by hex 2B79.', focus='math_product'),

    lesson('Reduce the degree-13 product by long division', [
        P('Hex 2B79 encodes the unreduced product P(x) from slide 36. Each row adds a shifted copy of the AES modulus m(x), using XOR on the coefficients.'),
        T(['Current polynomial', 'Add this shifted modulus', 'Remainder after XOR'], [
            ['2B79 ↔ P(x) = x¹³ + x¹¹ + x⁹ + x⁸ + x⁶ + x⁵ + x⁴ + x³ + 1',
             '2360 ↔ x⁵m(x) = x¹³ + x⁹ + x⁸ + x⁶ + x⁵',
             '0819 ↔ r₁(x) = x¹¹ + x⁴ + x³ + 1'],
            ['0819 ↔ r₁(x) = x¹¹ + x⁴ + x³ + 1',
             '08D8 ↔ x³m(x) = x¹¹ + x⁷ + x⁶ + x⁴ + x³',
             '00C1 ↔ r₂(x) = x⁷ + x⁶ + 1'],
        ], [2.0, 1.8, 1.65]),
        M(r'\begin{aligned}r_1(x)&=P(x)+x^5m(x)=x^{11}+x^4+x^3+1,\\'
          r'r_2(x)&=r_1(x)+x^3m(x)=x^7+x^6+1.\end{aligned}'),
        P('The final remainder has degree 7. It encodes 1100 0001 = C1, the byte product found by repeated shifts.'),
    ], 3, 'Point back to the unreduced product on slide 36. The table shows each hexadecimal encoding with all its polynomial terms. XOR cancels each term that occurs in both polynomials. The first step cancels x¹³ and leaves degree 11. The second cancels x¹¹ and leaves degree 7, so division stops. The two steps give P(x) = (x⁵ + x³)m(x) + (x⁷ + x⁶ + 1).', focus='math_product'),

    lesson('What would it mean to invert 05?', [
        P('Recall SubBytes replaces each byte using a fixed S-box. We will construct its entry for 05.'),
        ('sbox_inverse', 0x05),
        M(r'\begin{aligned}\mathtt{05}&\leftrightarrow b(x)=x^2+1,\\'
          r'b(x)d(x)+m(x)c(x)&=1\quad\Longrightarrow\quad b(x)d(x)\equiv 1\pmod{m(x)}.'
          r'\end{aligned}'),
        P('This is polynomial inversion, following the integer example. Since m(x) is irreducible, its gcd with any nonzero byte polynomial is 1.'),
    ], 3, 'Recall the S-box from the algorithm overview. Input 05 selects row 0 and column 5 in the fixed table, so SubBytes outputs 6B. Point to both highlighted labels and the table cell. Explain how AES constructs this entry in two steps: find the multiplicative inverse in the AES byte field, then apply a fixed affine bit transformation. Our immediate goal is the first step, finding d with 05 times d equal to 01 modulo m. The next two slides derive d = 52. The later S-box section shows that the affine transformation takes 52 to 6B. Point to d(x) in the Bézout identity. It plays the same role as the coefficient −2 of 12 in the integer example. The zero input uses a separate convention, shown when we construct the full S-box.', focus='math_inverse'),

    lesson('Finding the inverse of 05: polynomial long division', [
        ('inverse_division', [
            ['11B', 8, 6, 'x⁶b(x) = 140 = x⁸ + x⁶', '11B XOR 140 = 05B'],
            ['05B', 6, 4, 'x⁴b(x) = 050 = x⁶ + x⁴', '05B XOR 050 = 00B = x³ + x + 1'],
            ['00B', 3, 1, 'xb(x) = 00A = x³ + x', '00B XOR 00A = 001 = 1'],
        ]),
    ], 4, 'We seek the multiplicative inverse of 05 in the AES byte field. First divide the modulus m by the fixed polynomial b = x² + 1. The degree-difference rule aligns the leading powers. In the first step, 8 − 2 = 6, so multiply b by x⁶. The matching x⁸ terms cancel in the polynomial sum. Read the same operation in nine-bit binary: 100011011 XOR 101000000 = 001011011. Thus 11B XOR 140 = 05B, whose degree is 6. The value 140 is the unreduced binary-polynomial product of 05 with x⁶, before field reduction. Carry 05B down to the next row. Repeat with differences 6 − 2 = 4 and 3 − 2 = 1. The divisor stays x² + 1 throughout. Collect one quotient term from each shift to obtain Q = x⁶ + x⁴ + x. The remainder 1 has degree 0, below the divisor degree 2, so division stops. The following slide connects this result to ordinary division and derives the inverse.', focus='math_inverse'),

    lesson('Why the quotient is the multiplicative inverse', [
        ('inverse_proof',),
    ], 3, 'Begin with ordinary integer division, 11 = 2 × 5 + 1. Identify the dividend, divisor, quotient and remainder before matching those roles to m, b, Q and 1. The previous slide obtained Q(x) = x⁶ + x⁴ + x with remainder 1. Since addition and subtraction of binary-polynomial coefficients both use XOR, rearrange m = Qb + 1 as Qb = m + 1. Reducing modulo m gives Qb congruent to 1, so d = Q is the required multiplicative inverse. Read the coefficients from power 7 down to power 0: 0, 1, 0, 1, 0, 0, 1, 0. This byte is 52 in hexadecimal. Verify the field product by multiplying 52 by x twice, obtaining A4 and 53, then XOR with the original 52 to get 01. The raw second shift is 148, and 148 XOR 11B = 053. The quotient supplies the inverse directly here because this first polynomial division has remainder 1. Other inputs can require further extended Euclidean steps. The later S-box construction applies the affine map to 52 to produce 6B.', focus='math_inverse'),

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
        P('A root finds a linear factor. What if a higher-degree polynomial has no root in GF(2)? Consider f(x) = x⁴ + x² + 1.'),
        M(r'f(0)=1,\qquad f(1)=1,\qquad f(x)=(x^2+x+1)^2.'),
        P('The polynomial has no linear factor, yet it is reducible. Squaring in GF(2) keeps the squares of each term because the cross terms occur in equal pairs.'),
        P('For degrees two and three, a factorisation must contain a linear factor and testing both roots suffices. For degree four, a complete test must also allow two quadratic factors.'),
    ], section='APPENDIX', minutes=0, notes='Pairs with the four class examples on factoring binary polynomials. The AES degree-eight modulus is a specified irreducible polynomial.'),
    slide('A second integer inverse by back-substitution', [
        C('FIND THE LAST NONZERO REMAINDER', '45 = 2 × 19 + 7      19 = 2 × 7 + 5\n 7 = 1 × 5  + 2       5 = 2 × 2 + 1'),
        C('WRITE 1 IN TERMS OF 45 AND 19', '1 = 5 − 2(7 − 5) = 3 × 5 − 2 × 7\n  = 3(19 − 2 × 7) − 2 × 7 = 3 × 19 − 8 × 7\n  = 3 × 19 − 8(45 − 2 × 19) = 19 × 19 − 8 × 45', 17),
        P('Read the coefficient of 45. Its inverse modulo 19 is −8 ≡ 11. Indeed, 45 × 11 = 495 = 26 × 19 + 1.'),
    ], section='APPENDIX', minutes=0, notes='Optional independent practice with the second pair of integers in the supplied reference.'),
]
