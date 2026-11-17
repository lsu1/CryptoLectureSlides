"""Feistel and DES teaching content, with complete reproducible reference data.

All bit-table positions are 1-based from the most significant input bit.
Hexadecimal examples are fixed-width representations, including leading zeros.
"""
from deck_schema import slide, P, B, C, M, T, Two, D
from crypto_examples import (
    IP, FP, E, P as DES_P_PERM, PC1, PC2, SHIFTS, SBOXES,
    DES_PLAINTEXT, DES_KEY, DES_CIPHERTEXT, DES_TRACE, DES_KEY_TRACE,
    des_subkeys, des_sbox, des_encrypt, permute,
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
    fs('Reverse the keys: make the final swap explicit', [
        P('Our network convention is: run r Feistel rounds, then swap the two output halves.'),
        M(r'C=R_r\,\|\,L_r.\qquad\text{Decrypt with }K_r,K_{r-1},\ldots,K_1\text{ and the same final swap.}'),
        M(r'(\widetilde L_1,\widetilde R_1)=(L_r,L_{r-1})=(R_{r-1},L_{r-1}).'),
        P('The reverse run successively recovers the preceding pairs in exchanged order. After all r rounds, its final swap restores L₀ ∥ R₀.'),
    ], take='“Same network, reversed keys” depends on the stated input/output swap convention.',
       notes='Start the reverse network with (Rr,Lr). Its first output is (Lr, Rr XOR F(Lr,Kr)), equal to (Rr−1,Lr−1). Repeat the argument. This is why DES can use the same round machinery for both directions.', minutes=3),
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
       notes='Keep the toy function R AND K fixed in both directions. Distinguish the round state (L₂,R₂) from the externally serialized ciphertext (R₂,L₂). The numeric example is deliberately only eight bits long.', minutes=3),
]

_first = DES_TRACE['rounds'][0]
_ks1 = DES_KEY_TRACE['rounds'][0]
_s5 = des_sbox(5, 0b011011)
assert _s5 == 9

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
        P('Each of the eight key bytes contains seven effective key bits and one odd-parity bit.'),
        C('FIRST BYTE OF THE EXAMPLE KEY: HEX 13', '0001001 | 1\n7 key bits | parity bit', 20),
        M(r'64=8(7+1),\qquad\text{effective key bits}=8\cdot7=56.'),
        P('The byte 00010011 has three 1s, so its parity is odd. Parity can detect some representation errors; it adds no secret-key strength.'),
    ], take='PC1 discards the parity positions before generating round keys.',
       notes='Bit numbering in the DES tables is 1-based from the most significant bit. The parity positions are 8,16,…,64. The standard example key has odd parity in every byte. Changing only parity bits does not change DES encryption.', minutes=2),
    ds('One example will connect the whole design', [
        C('STANDARD KNOWN-ANSWER EXAMPLE • HEXADECIMAL',
          'Plaintext  '+hx(DES_PLAINTEXT,64)+'\nKey        '+hx(DES_KEY,64)+'\nCiphertext '+hx(DES_CIPHERTEXT,64), 21),
        P('We will derive the first round and its first subkey, then connect them to this complete encryption.'),
        P('Hexadecimal is a compact display of bits: one hex digit represents four bits.'),
    ], take='Leading zeros matter: each displayed plaintext and ciphertext is exactly 64 bits.',
       notes='Use this single dataset consistently throughout the DES section. This is a known-answer validation example, not an example of secure contemporary encryption. The complete round trace and all subkeys are retained in the appendix.', minutes=2),
    ds('The DES data path', [
        D('des_overview'),
        P('After round 16, serialize R₁₆ ∥ L₁₆ before the final permutation. This is the final swap used in our Feistel convention.'),
    ], take='Initial permutation → 16 rounds → final half swap → final permutation.',
       notes='Keep round transformations separate from IP/FP and from the key-schedule branch. Some drawings omit the exchange in the last round instead of drawing a final undoing exchange. Both describe the same preoutput R16||L16.', minutes=2),
    ds('Initial and final permutations', [
        M(r'L_0\,\|\,R_0=\operatorname{IP}(P),\qquad C=\operatorname{FP}(R_{16}\,\|\,L_{16}).'),
        M(r'\operatorname{FP}=\operatorname{IP}^{-1}.'),
        P('A table entry names the input bit copied to that output position. For example, the first eight IP output bits read input positions:'),
        C('FIRST EIGHT ENTRIES OF IP', ', '.join(map(str,IP[:8])), 20),
    ], take='These fixed, public bit rearrangements do not add meaningful cryptographic strength.',
       notes='Explain the table convention before showing complete tables. Neither IP nor FP depends on the key. Appendix reference tables provide every position; no memorization of the wiring is required.', minutes=2),
    ds('A DES round is a Feistel round', [
        M(r'L_i=R_{i-1},\qquad R_i=L_{i-1}\oplus F(R_{i-1},K_i).'),
        T(['Input / output', 'Width'], [['Lᵢ₋₁ and Rᵢ₋₁', '32 bits each'], ['Kᵢ', '48 bits'], ['F(Rᵢ₋₁,Kᵢ)', '32 bits']], [530, 326]),
        P('The round function mixes a 32-bit half-block with a 48-bit subkey and returns 32 bits for the XOR.'),
    ], take='F does not have to be invertible; the whole Feistel round is.',
       notes='The DES-specific work is inside F and the round-key schedule. The outer Feistel equations and reverse-key decryption argument are unchanged from the preceding section.', minutes=2),
    ds('Inside the DES round function', [
        D('des_f'),
        M(r'F(R,K)=\mathsf P\bigl(S(E(R)\oplus K)\bigr).'),
    ], take='Expand 32→48; mix the key; substitute 48→32; permute the 32 output bits.',
       notes='Use the diagram to introduce all four stages before expanding them. Here the typeface P denotes the fixed 32-bit permutation, not the plaintext variable used elsewhere. The eight S-box outputs are concatenated before that permutation.', minutes=2),
    ds('Expansion: 32 input bits supply 48 positions', [
        T(['Six-bit group', 'Input positions selected by E'], [
            ['1', ', '.join(map(str,E[:6]))], ['2', ', '.join(map(str,E[6:12]))],
            ['8', ', '.join(map(str,E[-6:]))],
        ], [240, 616]),
        P('Some boundary bits appear in two groups. Expansion repeats and rearranges existing bits; it does not create new information.'),
        M(r'B=E(R)\oplus K\qquad(48\text{ bits}).'),
    ], take='The complete E table is in the appendix; each group feeds one S-box.',
       notes='Point to the overlap of positions 4 and 5 between the first two groups and the wrap-around from bit 32 to bit 1. The expanded value and round key must both be 48 bits for the XOR.', minutes=2),
    ds('Mix the expanded half with the round key', [
        C('VALUES FOR THE FIRST ROUND OF OUR EXAMPLE',
          'E(R₀) '+hx(_first['expanded'],48)+'\nK₁    '+hx(_first['key'],48)+'\nXOR   '+hx(_first['xored'],48), 21),
        P('For the first hex digit, 7 XOR 1 = 6. For the next, A XOR B = 1. Continue digit by digit, or work with all 48 bits.'),
        P('The XOR result is divided into eight consecutive six-bit groups.'),
    ], take='These values come from the same known-answer example; the key schedule will derive K₁ shortly.',
       notes='Hex XOR is shorthand for four bitwise XORs per digit. Do not treat hexadecimal values as ordinary addition or subtraction. This is the first round’s key mixing, before the S-boxes.', minutes=2),
    ds('Eight S-boxes reduce 48 bits to 32', [
        M(r'B=B_1\|\cdots\|B_8,\quad |B_j|=6;\qquad S(B)=S_1(B_1)\|\cdots\|S_8(B_8).'),
        T(['One S-box', 'All eight S-boxes'], [['6 input bits → 4 output bits', '48 input bits → 32 output bits'], ['A different fixed table for each j', 'Concatenate the eight four-bit outputs']], [428, 428]),
        P('Each S-box is many-to-one and therefore non-invertible. Feistel decryption does not require an inverse S-box.'),
    ], take='The S-boxes supply the round’s nonlinearity; the full tables are retained in the appendix.',
       notes='There are 64 possible inputs and only 16 output values for each S-box. That pigeonhole argument already proves non-invertibility, independently of the particular entries.', minutes=2),
    ds('S₅(011011): read the row and column', [
        C('SEPARATE OUTER AND INNER BITS', '0 | 1101 | 1', 23),
        P('Outer bits 01 select row 1. Inner bits 1101 select column 13. Both table indices start at 0.'),
        T(['S₅, row 1 / column', '12', '13', '14', '15'], [['Entry']+[str(SBOXES[4][1][j]) for j in range(12,16)]], [360, 124, 124, 124, 124]),
        M(r'S_5(011011)=9_{10}=1001_2.'),
    ], take='This standalone lookup illustrates the rule; the standard first round uses different S-box inputs.',
       notes='Retains the supplied reference’s S5 example, with explicit zero-based row and column selection. The two outer bits are not adjacent in the input. The complete S5 table appears with the other S-boxes in the appendix.', minutes=3),
    ds('Permute the 32 S-box output bits', [
        P('The fixed P permutation redistributes the S-box output positions before the value is XORed into the other half.'),
        C('FIRST EIGHT OUTPUT POSITIONS READ INPUT BITS', ', '.join(map(str,DES_P_PERM[:8])), 19),
        C('FIRST-ROUND EXAMPLE', 'Before P: '+hx(_first['sbox_output'],32)+'\nAfter P:  '+hx(_first['f'],32), 21),
    ], take='P changes positions, not the number of bits or their individual values.',
       notes='The complete P table is available alongside E in the appendix. Students can verify selected output positions rather than perform all 32 selections in class.', minutes=2),
    ds('Different stages serve different roles', [
        T(['Stage', 'Role in F'], [
            ['Expansion E', 'Repeat and rearrange bits into eight six-bit inputs.'],
            ['XOR with Kᵢ', 'Introduce the secret round-key dependence.'],
            ['S₁,…,S₈', 'Apply nonlinear, many-to-one substitutions.'],
            ['Permutation P', 'Redistribute the resulting 32 bits.'],
        ], [250,606]),
        P('The DES S-boxes were designed with resistance to differential cryptanalysis in mind; that attack is outside today’s scope.'),
    ], take='An invertible outer structure can contain deliberately non-invertible nonlinear components.',
       notes='Do not expand this historical comment into a new attack lecture. The point is to distinguish fixed wiring, key mixing, and substitution. The original reference’s observation about S-box design is preserved without claiming that structure alone proves security.', minutes=2),
    ds('The key schedule supplies sixteen subkeys', [
        D('key_schedule'),
        P('Permuted Choice 1 (PC1) removes parity. After rotating each 28-bit half, Permuted Choice 2 (PC2) selects the 48-bit round key.'),
    ], take='Sixteen subkeys are derived from one 56-bit effective master key; they are not independent secrets.',
       notes='The round-key schedule is deterministic. Its output contains 16×48 displayed bits, but the original effective secret still has only 56 independent bits. All bit selections and rotations are public.', minutes=2),
    ds('PC1: remove parity and split the key', [
        C('OUR EXAMPLE KEY AFTER PC1',
          'Key:   '+hx(DES_KEY,64)+'\nPC1:   '+hx(DES_KEY_TRACE['pc1'],56)+'\nC₀:    '+hx(DES_KEY_TRACE['c0'],28)+'\nD₀:    '+hx(DES_KEY_TRACE['d0'],28), 20),
        P('PC1 selects 56 of the 64 representation bits and orders them into C₀ and D₀, each 28 bits long.'),
        P('Positions 8,16,…,64 are the discarded parity bits.'),
    ], take='The PC1 and PC2 tables are provided together in the appendix.',
       notes='C and D here name the key-schedule halves; they are different from the data-path halves L and R. The fixed-width hexadecimal display uses seven hex digits per 28-bit half.', minutes=2),
    ds('Rotate the halves, then select 48 bits', [
        M(r'C_i=\operatorname{rotl}_{28}(C_{i-1},s_i),\qquad D_i=\operatorname{rotl}_{28}(D_{i-1},s_i).'),
        M(r'K_i=\operatorname{PC2}(C_i\|D_i).'),
        T(['Round numbers', 'Left rotation sᵢ'], [['1,2,9,16', '1 bit'], ['All other rounds', '2 bits']], [500,356]),
        P('Rotations wrap within each 28-bit half. PC2 selects and permutes 48 of the combined 56 bits.'),
    ], take='The complete shift sequence and all sixteen computed subkeys appear in the appendix.',
       notes='Clarify that each round rotates the preceding C and D, not the original halves afresh. Across all 16 rounds the scheduled left rotations sum to 28, so the last schedule halves return to their initial positions.', minutes=2),
    ds('Compute the first round key', [
        C('ROUND 1 USES A ONE-BIT LEFT ROTATION',
          'C₀ '+hx(DES_KEY_TRACE['c0'],28)+' → C₁ '+hx(_ks1['c'],28)+'\nD₀ '+hx(DES_KEY_TRACE['d0'],28)+' → D₁ '+hx(_ks1['d'],28), 21),
        C('APPLY PC2 TO C₁ ∥ D₁', 'K₁ = '+hx(_ks1['key'],48), 22),
        P('This is the same 48-bit subkey used in our earlier first-round XOR.'),
    ], take='Use the table as wiring: each PC2 entry selects one input position from the 56-bit concatenation.',
       notes='The displayed computed values are generated by the shared DES implementation. Students can verify the rotations at the bit level, then trace a few PC2 selections to connect the table to the hexadecimal subkey.', minutes=3),
    ds('Enter round 1 after the initial permutation', [
        C('AFTER IP ON THE EXAMPLE PLAINTEXT',
          'IP(P) = '+hx(DES_TRACE['post_ip'],64)+'\nL₀    = '+hx(DES_TRACE['l0'],32)+'\nR₀    = '+hx(DES_TRACE['r0'],32), 21),
        C('ROUND 1 SUBKEY', 'K₁ = '+hx(_first['key'],48), 21),
        P('We now have every input required to evaluate the first DES round.'),
    ], take='All displayed trace values are hexadecimal; input tables still select individual bits.',
       notes='This is the joining point of the data path and key schedule. The known-answer plaintext, master key, IP output, and first round key have each been introduced separately. Work through F next.', minutes=2),
    ds('Round 1: inspect all eight S-box lookups', [
        T(['Box', 'Six-bit input', 'Row / column', 'Output'], [
            ['S'+str(b['box']), f'{b["input"]:06b}', f'{b["row"]} / {b["column"]}', f'{b["output"]:04b}']
            for b in _first['boxes']
        ], [110,260,260,226]),
    ], take='Concatenating these eight four-bit outputs gives 5C82B597; P then gives F(R₀,K₁)=234AA9BB.',
       notes='The input being partitioned is the XOR result 6117BA866527. Unlike the standalone S5 example, the fifth six-bit group here is 100001, which selects row 3, column 0 and returns 1011. The complete eight-box trace is generated rather than transcribed.', minutes=3),
    ds('Complete round 1, then finish the encryption', [
        M(r'L_1=R_0,\qquad R_1=L_0\oplus F(R_0,K_1).'),
        C('FIRST ROUND',
          'F(R₀,K₁) = '+hx(_first['f'],32)+'\nL₁ = '+hx(_first['l'],32)+'\nR₁ = '+hx(DES_TRACE['l0'],32)+' XOR '+hx(_first['f'],32)+' = '+hx(_first['r'],32), 18),
        C('AFTER ROUND 16 AND THE FINAL SWAP',
          'R₁₆ || L₁₆ = '+hx(DES_TRACE['preoutput'],64)+'\nFP gives C = '+hx(DES_CIPHERTEXT,64), 18),
    ], take='Rounds 2–16 repeat the same rule with their subkeys. The appendix retains every (Lᵢ,Rᵢ) pair.',
       notes='Check that the first-round left output equals the previous right input. The final code row is not obtained after one round; it reports the end of all 16 rounds. The preoutput and final permutation result are distinct values.', minutes=3),
    ds('DES decryption follows the same data path', [
        C('KEY ORDER', 'Encryption: K₁, K₂, …, K₁₆\nDecryption: K₁₆, K₁₅, …, K₁', 20),
        P('Keep IP, the round function, the final half swap, and FP in the same positions. Reverse only the order in which the round subkeys are supplied.'),
        C('CHECK THE COMPLETE REVERSE OPERATION', hx(DES_CIPHERTEXT,64)+' → '+hx(DES_PLAINTEXT,64), 20),
    ], take='The same master key generates the subkeys; decryption consumes that list in reverse.',
       notes='Applying IP to the ciphertext undoes the encryption’s FP and exposes R16||L16. The reverse-key Feistel run and its output swap recover the original IP output; FP then recovers the original plaintext. This uses the exact swap convention already established.', minutes=2),
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

# Content-level invariants are useful before the full PDF and layout checks run.
assert len(FEISTEL_SLIDES)==6 and len(DES_SLIDES)==26 and len(DES_APPENDIX)==9
assert DES_CIPHERTEXT==0x85E813540F0AB405
assert DES_TRACE['post_ip']==0xCC00CCFFF0AAF0AA
assert _first['expanded']==0x7A15557A1555 and _first['xored']==0x6117BA866527
assert _first['sbox_output']==0x5C82B597 and _first['f']==0x234AA9BB
assert _first['l']==0xF0AAF0AA and _first['r']==0xEF4A6544
assert _ks1['key']==0x1B02EFFC7072
