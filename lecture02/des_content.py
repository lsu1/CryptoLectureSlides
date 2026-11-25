"""Feistel and DES teaching content, with complete reproducible reference data.

All bit-table positions are 1-based from the most significant input bit.
Hexadecimal examples are fixed-width representations, including leading zeros.
"""
from deck_schema import slide, P, B, C, M, T, Two, D
from crypto_examples import (
    IP, FP, E, P as DES_P_PERM, PC1, PC2, SHIFTS, SBOXES,
    DES_PLAINTEXT, DES_KEY, DES_CIPHERTEXT, DES_TRACE, DES_KEY_TRACE,
)


def hx(value, bits):
    return f'{value:0{bits//4}X}'


def fs(title, blocks=None, **options):
    return slide(title, blocks, section='FEISTEL NETWORKS', **options)


def ds(title, blocks=None, **options):
    return slide(title, blocks, section='DES', **options)


# This deliberately non-invertible function is a teaching model, not DES F.
def toy_round(left, right, key):
    return right, left ^ (right & key)


_toy = [(0b1010, 0b1100)]
for _k in [0b0110, 0b0101]:
    _toy.append(toy_round(*_toy[-1], _k))
_toy_back = [(_toy[-1][1], _toy[-1][0])]
for _k in [0b0101, 0b0110]:
    _toy_back.append(toy_round(*_toy_back[-1], _k))
assert _toy[-1] == (0b1110, 0b1000)
assert (_toy_back[-1][1], _toy_back[-1][0]) == _toy[0]

FEISTEL_SLIDES = [
    fs('Feistel: build an invertible round', [D('feistel_round')],
       take='Split into equal halves; transform the right half, XOR into the left half, then exchange their roles.',
       notes='Introduce Horst Feistel and the structural idea used by DES. The unchanged branch retains the information needed to undo the other branch. The drawn exchange is already part of the round equations; do not add an extra swap inside each round.', minutes=2),
    fs('Write one round precisely', [
        M(r'L_i=R_{i-1},\qquad R_i=L_{i-1}\oplus F(R_{i-1},K_i).'),
        P('L and R are equal-length bit strings. Kᵢ is the subkey for round i; F produces a string the same length as a half-block.'),
        P('The right half becomes the next left half. Its transformed value is mixed into the old left half using XOR.'),
    ], take='The round is a transformation of the whole pair (L, R), not an inversion of F.',
       notes='Connect every symbol to the diagram. Distinguish the master key from a derived round key. F may have a different-size key input; the XOR requires its output to match the half-block length.', minutes=2),
    fs('A four-bit-half example', [
        T(['Quantity', 'Value'], [
            ['Input left half L₀', '1010'], ['Input right half R₀', '1100'],
            ['Round key K₁', '0110'], ['F(R₀,K₁) = R₀ AND K₁', '0100'],
            ['L₁ = R₀', '1100'], ['R₁ = L₀ XOR 0100', '1110'],
        ], [530, 326]),
    ], take='Bitwise AND is non-invertible: with this key, both 0000 and 0001 map to 0000.',
       notes='Use F(R,K)=R AND K only for this tiny teaching model. Compute the four XOR positions aloud: 1010 XOR 0100 = 1110. This explicit non-invertible F demonstrates the structural property more clearly than an invertible addition example.', minutes=2),
    fs('Undo a round without inverting F', [
        M(r'R_{i-1}=L_i,\qquad L_{i-1}=R_i\oplus F(L_i,K_i).'),
        M(r'R_i\oplus F(L_i,K_i)=L_{i-1}\oplus F(R_{i-1},K_i)\oplus F(R_{i-1},K_i)=L_{i-1}.'),
        C('CHECK THE TOY ROUND', 'R₀ = L₁ = 1100\nL₀ = 1110 XOR (1100 AND 0110) = 1010', 17),
    ], take='The same F is evaluated again; XOR cancels the repeated value.',
       notes='The first inverse identity comes directly from the unchanged branch. Substitute that identity into the second, then cancel X XOR X. This proves invertibility for every F with the required input/output widths.', minutes=3),
    fs('Two rounds: follow encryption and decryption', [
        Two([
            T(['Forward step', 'L', 'R'], [
                ['Input', '1010', '1100'], ['K₁ = 0110', '1100', '1110'], ['K₂ = 0101', '1110', '1000'],
            ], [190, 111, 111]),
        ], [
            T(['Reverse step', 'L', 'R'], [
                ['Input ciphertext', '1000', '1110'], ['K₂ = 0101', '1110', '1100'], ['K₁ = 0110', '1100', '1010'],
            ], [190, 111, 111]),
        ]),
        C('FINISH EACH DIRECTION BY SWAPPING HALVES', 'Encryption output: 1000 || 1110\nDecryption output: 1010 || 1100', 18),
    ], take='The same two-round construction reverses the transformation when the key order is reversed.',
       notes='Keep the toy function R AND K fixed in both directions. Distinguish the round state (L₂,R₂) from the externally serialized ciphertext (R₂,L₂). Give students three minutes to calculate the reverse steps using K₂ and then K₁ before discussing the result.', minutes=6),
]

def worked_feistel_rounds(states, keys, key_names):
    columns = []
    for (left, right), (next_left, next_right), key in zip(states, states[1:], keys):
        f_value = right & key
        columns.append([
            f'({left:04b}, {right:04b})',
            f'{right:04b} AND {key:04b} = {f_value:04b}',
            f'{next_left:04b}',
            f'{left:04b} XOR {f_value:04b} = {next_right:04b}',
            f'({next_left:04b}, {next_right:04b})',
        ])

    labels = ['Input (L, R)', '1. Compute F = R AND K', '2. Copy R to the new left',
              '3. New right = L XOR F', 'Output (new left, new right)']
    headers = ['Round calculation',
               f'First round ({key_names[0]} = {keys[0]:04b})',
               f'Second round ({key_names[1]} = {keys[1]:04b})']
    return T(headers, list(zip(labels, *columns)), [272, 292, 292])


FEISTEL_APPENDIX = [
    slide('Feistel by hand / encryption', [
        P('Split the plaintext 10101100 into L = 1010 and R = 1100. Read each round down its column. Work one bit at a time. AND gives 1 when both bits are 1. XOR gives 1 when the bits differ.'),
        worked_feistel_rounds(_toy, [0b0110, 0b0101], ['K₁', 'K₂']),
        C('FINAL SWAP  •  WRITE THE RIGHT HALF FIRST, THEN THE LEFT',
          'Ciphertext = 1000 || 1110 = 10001110', 19),
    ], notes='AND gives 1 when both input bits are 1. XOR gives 1 when the bits differ. The symbol || joins the two four-bit halves. In each round calculate F from the input right half and use the input left half for the XOR.', minutes=0),
    slide('Feistel by hand / decryption', [
        P('Split the ciphertext 10001110 into L = 1000 and R = 1110. Apply the same round rule, using K₂ first and K₁ second.'),
        worked_feistel_rounds(_toy_back, [0b0101, 0b0110], ['K₂', 'K₁']),
        C('FINAL SWAP  •  WRITE THE RIGHT HALF FIRST, THEN THE LEFT',
          'Recovered plaintext = 1010 || 1100 = 10101100', 19),
    ], notes='Check the pair after the first reverse round against the first encryption round. Their halves appear in opposite order. The final swap gives the original plaintext, 10101100.', minutes=0),
]

_first = DES_TRACE['rounds'][0]
_ks1 = DES_KEY_TRACE['rounds'][0]
_second = DES_TRACE['rounds'][1]
_last = DES_TRACE['rounds'][-1]
_c0_bits = f'{DES_KEY_TRACE["c0"]:028b}'


def bit_copy_table(value, width, positions):
    bits = f'{value:0{width}b}'
    return T(['Output position'] + [str(i) for i in range(1, len(positions) + 1)], [
        ['Read input bit'] + [str(pos) for pos in positions],
        ['Bit copied'] + [bits[pos - 1] for pos in positions],
    ], [190] + [666 / len(positions)] * len(positions))


DES_SLIDES = [
    ds('DES: a historical standard', [
        T(['Year', 'Milestone'], [
            ['1977', 'NBS publishes DES as FIPS 46.'],
            ['2001', 'NIST standardizes AES as the successor.'],
            ['2005', 'NIST withdraws DES, FIPS 46-3.'],
            ['2024', 'NIST withdraws its Triple DES recommendation.'],
        ], [160, 696]),
        P('We study the design and its lessons. DES and Triple DES are historical constructions for new-encryption decisions.'),
    ], take='DES shows how a bit-level construction becomes an efficiently reversible keyed permutation.',
       notes='Frame this as historical technical study, not deployment advice. DES originated in IBM research and was standardized by the US National Bureau of Standards, now NIST. AES details belong to a later lecture. TDEA withdrawal took effect on 1 January 2024.', minutes=2),
    ds('DES parameters', [
        T(['Property', 'DES value'], [
            ['Plaintext / ciphertext block', '64 bits → 64 bits'], ['Effective secret key', '56 bits'],
            ['Conventional key representation', '64 bits, including eight parity bits'],
            ['Round structure', '16 Feistel rounds; 32-bit halves'], ['Round subkey', '48 bits'],
        ], [420, 436]),
    ], take='The block length, effective key length, and subkey length are three different quantities.',
       notes='Prevent the common conflation of 64-bit block size with 64-bit security. For each fixed effective key, DES permutes the set of 64-bit blocks. The key schedule expands neither the independent key entropy nor the block size.', minutes=2),
    ds('Why 64 key bits mean 56 secret bits', [
        D('des_key_parity', key=DES_KEY),
        P('The seven key bits contain two 1s. Set the parity bit to 1 so that the whole byte has three 1s. DES uses this <b>odd parity</b> rule for each of the eight bytes.'),
        P('If a bit flips and 00010011 becomes 00000011, only two 1s remain. A parity check flags that byte.'),
    ], take='Each byte contributes seven independent key bits. Across eight bytes, the secret key has 8 × 7 = 56 bits.',
       notes='Start with the full example key and point to its first byte, 13 in hexadecimal. Read each hex digit as four bits. Then regroup the same eight bits as seven key bits and one check bit. To generate a key, choose the seven key bits per byte freely and set the last bit to make the total number of ones odd. Ask what the check bit would be if the seven key bits already contained an odd number of ones (0). A single flipped bit fails the check. Two flipped bits in the same byte preserve parity.', minutes=2),
    ds('How does DES encrypt one block?', [
        C('ONE BLOCK AND ITS MASTER KEY  •  HEXADECIMAL',
          f'Plaintext   {DES_PLAINTEXT:016X}\nMaster key  {DES_KEY:016X}', 20),
        D('des_overview'),
    ], take='Our first goal is to apply IP and calculate L₁ and R₁, the two halves that enter round 2.',
       notes='Follow the full path from plaintext to ciphertext. IP rearranges the plaintext bits, which we split into L₀ and R₀. Round 1 uses K₁ to produce L₁ and R₁. Point to these halves on the arrow into round 2. The omitted rounds follow the same Feistel rule, each with its own subkey. Only after round 16 do we join R₁₆ before L₁₆ and apply IP⁻¹.', minutes=2),
    ds('How to read the initial permutation', [
        P('Read each row from left to right. Each entry names a plaintext bit to copy, counting from 1.'),
        Two([
            D('bit_table', table=IP, cols=8, label='Complete IP table',
              note='DES specifies this fixed, public table for every block and key.',
              output_ranges=True, highlight_row=0, height=266),
        ], [
            C('PLAINTEXT BYTES IN HEX', DES_PLAINTEXT.to_bytes(8, 'big').hex(' ').upper(), 20),
            D('ip_byte_copies', plaintext=DES_PLAINTEXT, input_positions=IP[:2]),
            C('FIRST ROW  •  TAKE THE SECOND BIT OF EACH BYTE',
              'Byte   EF CD AB 89 67 45 23 01\nBit     1  1  0  0  1  1  0  0', 18),
        ]),
    ], take='Row 1 gives the first output byte, 1100 1100 = CC. For this plaintext the eight rows give CC 00 CC FF F0 AA F0 AA.',
       notes='DES specifies the same public table for every key and block. Point to entry 58 and the boxed 1 in EF. This byte occupies positions 57–64, so 58 is its second bit from the left. The next entry, 50, points to the boxed second bit of CD, which occupies positions 49–56. Read the remaining six entries to finish the first output byte, CC. Row 2 produces the second byte, 00. Use the eight output bytes to identify the two halves on the next slide.', minutes=3),
    ds('What enters the first Feistel round?', [
        C('APPLY IP, THEN SPLIT INTO TWO 32-BIT HALVES',
          f'IP output   {DES_TRACE["post_ip"]:016X}\nLeft  L₀    {DES_TRACE["l0"]:08X}\nRight R₀    {DES_TRACE["r0"]:08X}', 20),
        C('USE THIS 48-BIT ROUND KEY FOR NOW', f'K₁ = {_first["key"]:012X}', 19),
        M(r'L_1=R_0,\qquad R_1=L_0\oplus F(R_0,K_1).'),
    ], take='We can already write L₁ = F0AAF0AA. To calculate R₁, we need the value of F.',
       notes='Point to the first CC byte students have just calculated. The first eight hex digits make up L0 and the last eight make up R0. Treat K1 as given while working on the message. We derive this exact subkey after completing the round.', minutes=2),
    ds('What is inside the DES round function?', [
        P('In the toy example we used R AND K. DES keeps the Feistel rule and defines F with four operations. Follow the right half and the round key through them.'),
        D('des_f'),
    ], take='F returns 32 bits so its output can be XORed with the 32 bits of L₀.',
       notes='Point to the widths and the key entering at the XOR. Eight independent lookup tables shrink the result to 32 bits. The fixed permutation P is the last operation inside F. Leave the unchanged left input on the board until the end of the round.', minutes=2),
    ds('Build the first six expansion bits', [
        D('des_stage', active=0),
        C('READ THE TWO ENDS OF THE RIGHT HALF',
          'R₀ = F0AAF0AA     first byte F0 = 11110000     last digit A = 1010', 17),
        bit_copy_table(DES_TRACE['r0'], 32, E[:6]),
        P('The last bit is 0. The first five are 11110. Joining them in the order shown gives <b>011110</b>, the first six bits of E(R₀).'),
    ], take='Expansion builds eight six-bit groups from 32 bits. Neighbouring groups reuse boundary bits. The full E table is in A4.',
       notes='Read positions 32, 1, 2, 3, 4, 5 aloud. Circle the last bit of A, then take the four bits of F and the leading zero of the next digit. The next group uses positions 4 through 9, so positions 4 and 5 appear again.', minutes=3),
    ds('XOR six bits with six key bits', [
        D('des_stage', active=1),
        P('K₁ starts with hex 1B, or 0001 1011 in binary. Its first six bits are 000110. XOR gives 1 wherever the two input bits differ.'),
        Two([C('FIRST SIX BITS  •  BINARY',
               f'Expanded   {_first["expanded"] >> 42:06b}\nKey        {_first["key"] >> 42:06b}\nXOR        {_first["xored"] >> 42:06b}', 20)],
            [C('ALL 48 BITS  •  HEX',
               f'E(R₀)   {_first["expanded"]:012X}\nK₁      {_first["key"]:012X}\nXOR     {_first["xored"]:012X}', 20)]),
    ], take='Split the 48-bit XOR result into eight groups of six. Send the first group, 011000, to S₁.',
       notes='Compare the six aligned columns on the left. Bit 4 is 1 in both inputs, so the output there is 0. The hex view on the right shows the same operation across all eight groups. Six-bit boundaries can fall in the middle of a hex digit.', minutes=2),
    ds('Look up 011000 in the first S-box', [
        D('des_stage', active=2),
        D('des_lookup', table=SBOXES[0], value=_first['boxes'][0]['input']),
    ], take='S₁ returns decimal 5. Write it as 0101, the first four bits of the 32-bit S-box output.',
       notes='The two outside bits form a two-bit row number. The four middle bits form a four-bit column number. Rows and columns both start at zero. Follow the highlighted row and column to 5. Since this table maps 64 inputs to 16 values, different inputs can produce the same output.', minutes=3),
    ds('Where does that first 5 go?', [
        D('des_stage', active=2),
        P('Each group goes to its own S-box, in order. Try S₂ on 010001. Which row and column would you use? The S₂ table is in A7.'),
        C('JOIN THE EIGHT FOUR-BIT OUTPUTS FROM LEFT TO RIGHT',
          'Box       S1    S2    S3    S4    S5    S6    S7    S8\n'
          + 'Bits      ' + '  '.join(f'{box["output"]:04b}' for box in _first['boxes']) + '\n'
          + 'Hex        ' + '     '.join(f'{box["output"]:X}' for box in _first['boxes']), 18),
        P('The 5 from S₁ becomes the first hex digit. The C from S₂ becomes the second. All eight together give <b>5C82B597</b>.'),
    ], notes='Let students answer before interpreting the output strip. For 010001, outer bits 01 select row 1 and inner bits 1000 select column 8. S2 gives 12 in decimal, written C in hex or 1100 in four bits.', minutes=3),
    ds('Permute the 32 output bits', [
        D('des_stage', active=3),
        P('The P table uses the same copying rule as IP. In 5C82B597, bit 16 is the last bit of the fourth digit, 2 = 0010. Copy its 0 into output position 1.'),
        bit_copy_table(_first['sbox_output'], 32, DES_P_PERM[:4]),
        C('FIRST OUTPUT DIGIT 0010 = 2  •  CONTINUE FOR ALL 32 POSITIONS',
          f'Before P   {_first["sbox_output"]:08X}\nAfter P    {_first["f"]:08X}', 18),
    ], take='After P, the value of F(R₀, K₁) is 234AA9BB. It is ready to mix into the left half.',
       notes='To check another bit, select input position 20, the last bit of the fifth digit B = 1011. It supplies the 1 in output position 3. P just rearranges all 32 bits. The complete table appears in A4.', minutes=2),
    ds('Put F back into the Feistel round', [
        M(r'L_1=R_0,\qquad R_1=L_0\oplus F(R_0,K_1).'),
        Two([C('COPY THE OLD RIGHT HALF',
               f'R₀    {DES_TRACE["r0"]:08X}\nL₁    {_first["l"]:08X}', 21)],
            [C('XOR F INTO THE OLD LEFT HALF',
               f'L₀    {DES_TRACE["l0"]:08X}\nF     {_first["f"]:08X}\nR₁    {_first["r"]:08X}', 21)]),
        P('Check the first digit of R₁ by hand. Hex C XOR 2 gives 1100 XOR 0010 = 1110, or E.'),
    ], take='Round 1 ends with (L₁, R₁) = (F0AAF0AA, EF4A6544). These two halves are the input to round 2.',
       notes='Ask which half was copied and which required the entire F calculation. Point back to the same two operations on slide 57. The output of F alone is not the right-half output of the round.', minutes=3),
    ds('Retrace the calculation of F', [
        T(['Operation', 'What it does', 'Round 1 result in hex'], [
            ['Expand R₀', 'Repeat boundary bits to make eight groups.', hx(_first['expanded'],48)],
            ['XOR with K₁', 'Mix the subkey into those groups.', hx(_first['xored'],48)],
            ['Apply S₁ to S₈', 'Use a nonlinear six-bit to four-bit lookup.', hx(_first['sbox_output'],32)],
            ['Permute with P', 'Move those 32 bits to their next positions.', hx(_first['f'],32)],
        ], [165,448,243]),
        M(r'F(R_0,K_1)=\mathsf{P}\bigl(S(E(R_0)\oplus K_1)\bigr).'),
        P('Read the formula from the inside out. If we kept R₀ and changed K₁, at which row could the result first change?'),
    ], take='The expansion depends only on R₀. The subkey first affects the result at the XOR.',
       notes='Use the question as a pause before the key schedule. Ask a student to point to the 5 from S1 and the 2 that starts the final output of F. The S-boxes supply nonlinearity, while E and P are fixed public bit selections.', minutes=1),
    ds('Where did the round key come from?', [
        P('In round 1 we used K₁ = 1B02EFFC7072. Start with the master key and follow this separate calculation to reproduce those 48 bits.'),
        D('key_schedule'),
    ], take='The same 56 effective master-key bits determine all sixteen round keys.',
       notes='The message halves L and R are set aside here. C and D below are halves of the key. Expand the abbreviations: PC1 is Permuted Choice 1, and PC2 is Permuted Choice 2.', minutes=2),
    ds('Select the 56 key bits with PC1', [
        P('Permuted Choice 1 (PC1) reads the master key in a fixed order and skips the parity bit in each byte. Its first entry is 57. The last key byte is F1, or 11110001, so bit 57 is 1.'),
        C('SPLIT THE PC1 OUTPUT AFTER SEVEN HEX DIGITS',
          f'Master key   {DES_KEY:016X}\nPC1 output   {DES_KEY_TRACE["pc1"]:014X}\nKey halves   C₀ = {DES_KEY_TRACE["c0"]:07X}    D₀ = {DES_KEY_TRACE["d0"]:07X}', 20),
    ], take='Each key half contains 28 bits. The full PC1 and PC2 tables are in A5.',
       notes='Key positions 8, 16, …, 64 carry parity. PC1 selects all the remaining positions once and rearranges them. Ask how seven hex digits correspond to 28 bits. The first digit F of C0 starts with the 1 just identified.', minutes=2),
    ds('Rotate each key half one place', [
        P('In round 1, move the leftmost bit of each 28-bit half to its own right-hand end. Follow the separated bit in C₀.'),
        C('ONE-BIT ROTATION OF THE LEFT KEY HALF',
          f'C₀   {_c0_bits[0]} | {_c0_bits[1:]}\nC₁       {_c0_bits[1:]} | {_c0_bits[0]}', 19),
        C('ROTATE THE RIGHT HALF BY THE SAME AMOUNT',
          f'C₀ {DES_KEY_TRACE["c0"]:07X}  →  C₁ {_ks1["c"]:07X}\nD₀ {DES_KEY_TRACE["d0"]:07X}  →  D₁ {_ks1["d"]:07X}', 19),
    ], take='Round numbers 1, 2, 9 and 16 rotate by one place. The other rounds rotate by two, starting from the previous halves.',
       notes='Have students follow the leading 1 to the right end of C1. D0 rotates within its own 28 positions. Joining the halves before rotating would give a different result. A6 lists the shifts and every computed subkey.', minutes=2),
    ds('Recover the six key bits we used', [
        P('Join C₁ and D₁ to form a 56-bit string. Permuted Choice 2 (PC2) picks 48 positions from it. Read the first six entries exactly as we read the IP and E tables.'),
        C('ROTATED KEY HALVES SIDE BY SIDE', f'C₁ || D₁ = {_ks1["c"]:07X} {_ks1["d"]:07X}', 18),
        bit_copy_table((_ks1['c'] << 28) | _ks1['d'], 56, PC2[:6]),
        C('ALL 48 SELECTED BITS', f'K₁ = {_ks1["key"]:012X}', 19),
    ], take='The first six bits are 000110, exactly the bits we XORed with 011110 to enter S₁.',
       notes='Read the first copied bit from position 14 of the combined 56 bits. Complete the first six selections together. The remaining 42 selections follow the same rule. K1 is one 48-bit subkey derived from the original key.', minutes=3),
    ds('Start round 2 with the output of round 1', [
        C('INPUT TO ROUND 2  •  HEX',
          f'L₁ = {_first["l"]:08X}    R₁ = {_first["r"]:08X}    K₂ = {_second["key"]:012X}', 19),
        P('Before calculating F again, which half of the round 2 output can you already write down?'),
        C('APPLY THE SAME TWO RULES',
          f'L₂ = R₁ = {_second["l"]:08X}\nR₂ = L₁ XOR F(R₁, K₂) = {_first["l"]:08X} XOR {_second["f"]:08X} = {_second["r"]:08X}', 17),
    ], take='Repeat this round rule through round 16, using the next subkey each time. Appendix A11 lists the sixteen output pairs.',
       notes='Ask for L2 before uncovering the last box. The class can now follow later rounds without manually performing another eight lookups. Verify that round 2 starts from the pair at the end of round 1 and consumes K2 from the same key schedule.', minutes=2),
    ds('Finish encryption after round 16', [
        C('LAST ROUND OUTPUT  •  HEX',
          f'L₁₆ = {_last["l"]:08X}    R₁₆ = {_last["r"]:08X}', 21),
        C('SWAP THE HALVES, THEN APPLY THE FINAL PERMUTATION',
          f'R₁₆ || L₁₆     {DES_TRACE["preoutput"]:016X}\nCiphertext     {DES_CIPHERTEXT:016X}', 21),
        P('The final permutation (FP) undoes the opening bit rearrangement. Its first entry is 40, so it copies bit 40 of the swapped block into ciphertext position 1.'),
    ], take='The plaintext 0123456789ABCDEF encrypts to 85E813540F0AB405 with master key 133457799BBCDFF1.',
       notes='Point out the order of the two halves in the concatenation. FP is IP inverse, so it uses the full table in A3. Bits 33 to 40 of the swapped block form hex 43, ending in 1. This matches the leading bit of the ciphertext, which begins with hex 8.', minutes=2),
    ds('Undo the last round first', [
        P('Recall the two-round example on slide 57. There we started decryption with K₂. DES has sixteen rounds, so start with K₁₆.'),
        C('APPLY IP TO THE CIPHERTEXT',
          f'Ciphertext     {DES_CIPHERTEXT:016X}\nFirst pair     ({_last["r"]:08X}, {_last["l"]:08X})', 19),
        C('ONE FEISTEL ROUND WITH K₁₆',
          f'Copy right      {_last["l"]:08X}\nF(right, K₁₆)   {_last["f"]:08X}\nXOR into left   {_last["r"]:08X} XOR {_last["f"]:08X} = {_last["l_in"]:08X}', 18),
    ], take='The first decryption round gives (R₁₅, L₁₅) = (43423234, C28C960D).',
       notes='IP undoes the FP just applied during encryption. The right half entering F is L16, equal to R15, so using K16 reproduces F = C8C04F98 from the last encryption round. XOR cancels it. Use A11 to compare the resulting pair with the round 15 pair in exchanged order.', minutes=2),
    ds('Recover the original plaintext', [
        C('USE THE SAME DES ROUNDS WITH THE SUBKEYS IN REVERSE',
          'Encrypt   K₁,  K₂,  …, K₁₅, K₁₆\nDecrypt   K₁₆, K₁₅, …, K₂,  K₁', 19),
        C('AFTER ALL SIXTEEN DECRYPTION ROUNDS  •  HEX',
          f'Output pair   ({DES_TRACE["r0"]:08X}, {DES_TRACE["l0"]:08X})\nAfter swap    {DES_TRACE["post_ip"]:016X}\nAfter FP      {DES_PLAINTEXT:016X}', 19),
    ], take='The last swap restores the two halves in their original order. FP returns them to their original plaintext bit positions.',
       notes='Compare the value after the swap with the IP output at the start. The same F, S-boxes, initial and final permutations work in both directions. Only the order of subkeys changes, as in the two-round Feistel example.', minutes=1),
    ds('The effective key size became the problem', [
        M(r'|\mathcal K|=2^{56}\qquad\text{effective DES keys.}'),
        P('With a known plaintext/ciphertext pair, an attacker can test a candidate key by computing one block encryption.'),
        P('In 1998, the EFF’s dedicated DES-cracking hardware recovered a challenge key in about 56 hours.'),
        P('The historical response was to apply DES several times with more than one key.'),
    ], take='Hardware and cost estimates age; the structural limitation is the small 56-bit key space.',
       notes='Retain the historical exhaustive-search lesson without presenting the old 2006 hardware budget as a current benchmark. A candidate match should be checked against additional data as needed. Multiple encryption must be analyzed rather than judged by the count of nominal key bits.', minutes=2),
    ds('Double DES and the meet-in-the-middle idea', [
        M(r'C=E_{K_2}(E_{K_1}(P))\quad\Longrightarrow\quad E_{K_1}(P)=D_{K_2}(C).'),
        P('Store each middle value with its K₁, trying all 2⁵⁶ keys. Then try all 2⁵⁶ choices of K₂ from the ciphertext side and look for matches.'),
        M(r'\text{Work}\approx2^{56}+2^{56}=2^{57}\text{ DES operations};\qquad\text{storage}\approx2^{56}\text{ entries}.'),
        P('Use additional known pairs to reject false key-pair matches.'),
    ], take='Two 56-bit keys do not automatically provide 112-bit security.',
       notes='Keep this to the equality and cost intuition; a detailed attack lecture is outside the scope. The memory estimate is enormous. A single 64-bit plaintext/ciphertext pair permits many key-pair candidates, so a table match is not by itself proof of the unique correct keys.', minutes=3),
    ds('Triple DES uses encrypt–decrypt–encrypt', [
        D('ede', height=184),
        M(r'C=E_{K_3}\bigl(D_{K_2}(E_{K_1}(P))\bigr).'),
        P('This historical EDE composition applies three DES transformations to the same 64-bit block.'),
    ], take='If all three keys are equal, EDE collapses to ordinary DES: the middle inverse cancels one encryption.',
       notes='Read the composition from the innermost operation outward, matching the diagram from plaintext to ciphertext. EDE was chosen in part for compatibility with single-DES behavior when all keys coincide. The inverse and historical key options follow on the next page.', minutes=2),
    ds('Triple DES: inverse, key options, and retirement', [
        M(r'P=D_{K_1}\bigl(E_{K_2}(D_{K_3}(C))\bigr).'),
        T(['Historical option', 'Key relation', 'Effective key material'], [
            ['Three-key EDE', 'K₁,K₂,K₃ independent', '168 bits'],
            ['Two-key EDE', 'K₁ = K₃; K₂ independent', '112 bits'],
        ], [230,360,266]),
        P('Three-key EDE has about 112-bit generic security, despite 168 bits of key material. The two-key option has additional historical weaknesses.'),
        P('NIST withdrew its Triple DES (TDEA) recommendation on 1 January 2024. DES and Triple DES are unsuitable choices for new encryption.'),
    ], take='The block size remains 64 bits; extra key material does not remove the data-volume limits of a small block.',
       notes='Separate nominal effective key material from achieved attack resistance. Do not label the two-key option as 112-bit secure just because it contains 112 independent key bits. The 64-bit block creates restrictive data-volume limits in common modes, which are covered later. TDEA stands for Triple Data Encryption Algorithm. NIST withdrawal concerns new cryptographic protection; processing previously protected data has separate transition guidance.', minutes=3),
]

DES_APPENDIX = [
    slide('DES reference / initial and final permutations', [
        Two([D('bit_table', table=IP, rows=8, cols=8, label='Initial permutation IP', height=230)],
            [D('bit_table', table=FP, rows=8, cols=8, label='Final permutation FP = IP⁻¹', height=230)]),
        P('Read each table left to right, top to bottom. Each entry specifies the 1-based input position copied to the next output position.'),
    ], section='DES APPENDIX', take='Positions are numbered from the most significant input bit. FP exactly inverts IP.',
       notes='Complete FIPS 46-3 wiring tables. These are retained for independent calculation and implementation checking, not memorization.', minutes=0),
    slide('DES reference / expansion E and permutation P', [
        Two([D('bit_table', table=E, rows=8, cols=6, label='Expansion E:32 →48', height=230)],
            [D('bit_table', table=DES_P_PERM, rows=8, cols=4, label='P permutation:32 →32', height=230)]),
        P('E repeats selected boundary bits. P is a permutation of the 32 concatenated S-box output bits.'),
    ], section='DES APPENDIX', take='The table values are input bit positions, not S-box outputs or numeric additions.',
       notes='E has 48 entries selected from 32 input positions; P has each position 1 through 32 exactly once.', minutes=0),
    slide('DES reference / PC1 and PC2', [
        Two([D('bit_table', table=PC1, rows=8, cols=7, label='PC1:64 →56', height=230)],
            [D('bit_table', table=PC2, rows=8, cols=6, label='PC2:56 →48', height=230)]),
        P('PC1 omits parity positions 8,16,…,64. PC2 reads the concatenated, already rotated halves Cᵢ ∥ Dᵢ.'),
    ], section='DES APPENDIX', take='These are key-schedule selections. They are different from the data-path IP and P tables.',
       notes='Key representation has 64 bits, schedule halves have 28 bits each, and each selected subkey has 48 bits. Complete tables are taken directly from the shared verified example module.', minutes=0),
]

_key_rows = [[str(r['round']),str(r['shift']),hx(r['key'],48)] for r in DES_KEY_TRACE['rounds']]
DES_APPENDIX.append(slide('DES reference / rotations and all sixteen subkeys', [
    Two([T(['i', 'sᵢ', 'Kᵢ (hex)'], _key_rows[:8], [48,48,316])],
        [T(['i', 'sᵢ', 'Kᵢ (hex)'], _key_rows[8:], [48,48,316])]),
], section='DES APPENDIX', take='Master key 133457799BBCDFF1. Rotations are cumulative within each 28-bit half.',
   notes='Every key is printed as 12 hexadecimal digits, representing 48 bits. A two-column presentation preserves all 16 rows without shrinking the type excessively.', minutes=0))

for _first_box in [0,2,4,6]:
    DES_APPENDIX.append(slide(f'DES reference / S-boxes S{_first_box+1} and S{_first_box+2}', [
        D('bit_table', table=SBOXES[_first_box], rows=4, cols=16,
          label=f'S{_first_box+1}: rows 0–3, columns 0–15', row_headers=True, column_headers=True, height=135),
        D('bit_table', table=SBOXES[_first_box+1], rows=4, cols=16,
          label=f'S{_first_box+2}: rows 0–3, columns 0–15', row_headers=True, column_headers=True, height=135),
    ], section='DES APPENDIX', take='For six-bit input b₁b₂b₃b₄b₅b₆, use outer bits b₁b₆ for the row and inner bits b₂b₃b₄b₅ for the column.',
       notes='Each entry is a decimal number 0–15; encode it as a four-bit output. All eight distinct DES S-boxes are retained. Row and column indices are zero-based.', minutes=0))

_trace_rows = [[str(r['round']),hx(r['l'],32),hx(r['r'],32)] for r in DES_TRACE['rounds']]
DES_APPENDIX.append(slide('DES reference / all sixteen round states', [
    Two([T(['i', 'Lᵢ (hex)', 'Rᵢ (hex)'], _trace_rows[:8], [60,176,176])],
        [T(['i', 'Lᵢ (hex)', 'Rᵢ (hex)'], _trace_rows[8:], [60,176,176])]),
], section='DES APPENDIX', take='The state is (Lᵢ,Rᵢ) after each round. Preoutput is R₁₆ ∥ L₁₆ before FP; ciphertext is 85E813540F0AB405.',
   notes='Initial halves are L0=CC00CCFF and R0=F0AAF0AA. The full trace is generated from the same known-answer example; preserve leading zeros in the eight-digit half-block displays.', minutes=0))

_expanded_bits = f"{_first['expanded']:048b}"
_subkey_bits = f"{_first['key']:048b}"
_sbox_rows = []
for _box in _first['boxes']:
    _start = 6 * (_box['box'] - 1)
    _group = slice(_start, _start + 6)
    _input_bits = f"{_box['input']:06b}"
    _sbox_rows.append([
        f"S{_box['box']}", _expanded_bits[_group], _subkey_bits[_group], _input_bits,
        f"{_input_bits[0]}{_input_bits[-1]} → {_box['row']}",
        f"{_input_bits[1:5]} → {_box['column']}", f"{_box['output']:04b}",
    ])
_sbox_outputs = ' '.join(row[-1] for row in _sbox_rows)

DES_SBOX_APPENDIX = [
    slide('Round 1 / all eight S-box calculations', [
        T(['Box', 'E(R₀)', 'K₁', 'XOR', 'Outer bits → row', 'Inner bits → column', 'Output'],
          _sbox_rows, [58, 99, 99, 99, 161, 190, 150]),
    ], section='DES APPENDIX',
       sub='Read across each row. XOR the two six-bit groups, then look up the result in that row’s S-box.',
       take=f"Join the outputs from S1 to S8 in order. {_sbox_outputs} = {hx(_first['sbox_output'], 32)} (hex).",
       notes='The first and sixth bits of the XOR result give the row. The four bits between them give the column. Both indices start at zero. Use the S-box tables in A7–A10 to check each four-bit output.', minutes=0),
]

# Content-level invariants are useful before the full PDF and layout checks run.
assert len(FEISTEL_SLIDES)==5 and len(DES_SLIDES)==26 and len(DES_APPENDIX)==9
assert DES_CIPHERTEXT==0x85E813540F0AB405
assert DES_TRACE['post_ip']==0xCC00CCFFF0AAF0AA
assert _first['expanded']==0x7A15557A1555 and _first['xored']==0x6117BA866527
assert _first['sbox_output']==0x5C82B597 and _first['f']==0x234AA9BB
assert _first['l']==0xF0AAF0AA and _first['r']==0xEF4A6544
assert _ks1['key']==0x1B02EFFC7072
