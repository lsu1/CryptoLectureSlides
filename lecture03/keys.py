"""AES key expansion, decryption and implementation for the final teaching hour."""
from deck_schema import C, M, P, T, slide
from aes_trace import ROUND_TRACE


def located_slide(title, blocks, *, focus, detail, **options):
    item = slide(title, blocks, **options)
    item.update(aes_focus=focus, aes_detail=detail)
    return item


def key_page(title, blocks, **options):
    return located_slide(title, blocks, section='KEY EXPANSION', focus='keys', **options)


def inverse_page(title, blocks, **options):
    return located_slide(title, blocks, section='ENCRYPTION AND DECRYPTION', **options)


def closing_page(title, blocks, *, focus='verify', **options):
    return located_slide(title, blocks, section='AES IN PRACTICE', focus=focus, **options)


# The same column-ordered FIPS example used in the first-round walkthrough.
round1 = ROUND_TRACE[1]['end']
round9 = ROUND_TRACE[9]['end']
sub10 = ROUND_TRACE[10]['sub_bytes']
shift10 = ROUND_TRACE[10]['shift_rows']
ciphertext = ROUND_TRACE[10]['end']

slides = [
    key_page('Where did the first round key come from?', [
        P('Round 1 used the key D6AA74FD D2AF72FA DAA678F1 D6AB76FE. Both ends derive it from the same 16-byte secret key.'),
        C('SPLIT THE ORIGINAL KEY INTO FOUR WORDS OF FOUR BYTES EACH',
          'word       w[0]      w[1]      w[2]      w[3]\n'
          'bytes     00010203  04050607  08090A0B  0C0D0E0F'),
        M(r'K_j=\big(w[4j]\;\|\; w[4j+1]\;\|\;w[4j+2]\;\|\;w[4j+3]\big).'),
        P('The double bar joins words in order. In round j, column c uses w[4j + c], top byte first. For round 1, columns 0 through 3 use words 4 through 7.')
    ], detail='Read the original key', notes='Keep the four original words visible. Ask which word will be XORed into the second column at the initial key addition. Answer w[1].', minutes=3),

    key_page('Rotate one word and substitute its four bytes', [
        C('BEGIN WITH THE LAST WORD OF THE ORIGINAL KEY',
          'w[3]      0C 0D 0E 0F\nRotWord   0D 0E 0F 0C'),
        T(['Rotated input', 'S-box row', 'S-box column', 'SubWord output'], [
            ['0D', '0', 'D', 'D7'], ['0E', '0', 'E', 'AB'],
            ['0F', '0', 'F', '76'], ['0C', '0', 'C', 'FE']
        ], [220, 204, 214, 218]),
        P('The substituted word is D7 AB 76 FE. SubWord uses the same S-box as SubBytes.')
    ], detail='K₁ · RotWord and SubWord', notes='Point to 0C moving from the first position to the last. Look up the first output byte with the class. Ask them to read the other three.', minutes=4),

    key_page('Add the round constant to the first byte', [
        C('THE FIRST KEY-EXPANSION CONSTANT',
          '   D7 AB 76 FE    substituted word\n'
          '⊕  01 00 00 00    Rcon[1]\n'
          '=  D6 AB 76 FE    transformed word'),
        P('Successive constants have first bytes 01, 02, 04, 08, 10, 20, 40, 80, 1B, 36. The other three bytes are zero.'),
        P('Multiply by 02 in the AES byte field to advance one step. For 80, the shift gives 100 in hex and reduction by 11B leaves 1B.')
    ], detail='K₁ · apply Rcon[1]', take='The round constant changes the input to each special key-expansion step.',
       notes='Every value in the sequence is hexadecimal. Have someone compute the next value after 1B. The answer is 36.', minutes=3),

    key_page('Why does the key schedule use a round constant?', [
        P('The constant marks the position of a key-expansion step. Its first byte is a power of x in the AES byte field.'),
        M(r'\mathrm{Rcon}[j]=\big(x^{j-1}\bmod m(x),\;00,\;00,\;00\big),\qquad j\ge 1.'),
        T(['Suppose the substituted word is D7 AB 76 FE both times', 'Output after XOR'], [
            ['Use Rcon[1] = 01 00 00 00', 'D6 AB 76 FE'],
            ['Use Rcon[2] = 02 00 00 00', 'D5 AB 76 FE']
        ], [535, 321]),
        P('Even if a substituted word repeats at two positions, the two constants give different results. This breaks a symmetry in the expansion rule.')
    ], detail='Compare Rcon[1] and Rcon[2]',
       notes='Use the same hypothetical substituted word to isolate the effect of position. Each constant is public. The secrecy comes from the original key. This example illustrates the design rationale and does not establish that every possible key schedule state is distinct.', minutes=2),

    key_page('Generate the first two words of K₁', [
        T(['New word', 'Earlier word', 'XOR with', 'Result'], [
            ['w[4]', 'w[0] = 00010203', 'D6AB76FE', 'D6AA74FD'],
            ['w[5]', 'w[1] = 04050607', 'w[4] = D6AA74FD', 'D2AF72FA']
        ], [117, 245, 276, 218]),
        C('READ THE FIRST XOR BY BYTE',
          '00 ⊕ D6 = D6    01 ⊕ AB = AA\n02 ⊕ 76 = 74    03 ⊕ FE = FD'),
        P('Only w[4] used the transformed word. For w[5], the input on the right is the word just generated.')
    ], detail='K₁ · words 4 and 5', notes='Read across row one and then down to row two. The result of the first line becomes an input to the next.', minutes=4),

    key_page('Your turn · finish the first round key', [
        P('Compute w[6] first. Carry its result to the next line to compute w[7]. Work byte by byte in hexadecimal.'),
        C('WORD 6',
          'w[6] = w[2] ⊕ w[5] = 08 09 0A 0B ⊕ D2 AF 72 FA'),
        C('WORD 7',
          'w[7] = w[3] ⊕ w[6] = 0C 0D 0E 0F ⊕ __ __ __ __'),
        P('Which four bytes of K₁ meet the fourth column of the state?')
    ], detail='K₁ · words 6 and 7', notes='Give pairs about two minutes. Leave the previous result w[5] on the board. An incorrect w[6] should consistently propagate to w[7].', minutes=3),

    key_page('Read the four completed key columns', [
        C('SOLUTIONS TO THE TWO XORS',
          'w[6] = 08090A0B ⊕ D2AF72FA = DAA678F1\n'
          'w[7] = 0C0D0E0F ⊕ DAA678F1 = D6AB76FE'),
        T(['State column', '0', '1', '2', '3'], [
            ['Word in K₁', 'w[4]', 'w[5]', 'w[6]', 'w[7]'],
            ['Bytes, top to bottom', 'D6 AA 74 FD', 'D2 AF 72 FA', 'DA A6 78 F1', 'D6 AB 76 FE']
        ], [236, 155, 155, 155, 155]),
        P('The fourth column uses w[7]. These are the four key columns used at the end of round 1.')
    ], detail='K₁ · assemble four words', notes='Have students compare with the first-round AddRoundKey on the previous section. Point out that D6AB76FE happens to recur here for this input.', minutes=3),

    key_page('How many words does each AES version need?', [
        P('Write Nₖ for the number of 32-bit words in the original key and Nᵣ for the number of rounds. Every round key occupies four words.'),
        T(['Version', 'Nₖ', 'Nᵣ', 'Round keys (with K₀)', 'Total words'], [
            ['AES-128', '4', '10', '11', '44'],
            ['AES-192', '6', '12', '13', '52'],
            ['AES-256', '8', '14', '15', '60']
        ], [154, 87, 87, 306, 222]),
        P('For AES-192 the six original words fill K₀ and half of K₁. The key schedule generates w[6] and w[7] to complete K₁.')
    ], detail='Count expanded words', notes='Draw a ruler with breaks every four words for the round keys, then mark six words for AES-192. Distinguish a 128-bit block and a 192-bit key.', minutes=3),

    key_page('One expansion rule covers all three key sizes', [
        P('Copy the original key into the first Nₖ words. For each following word w[i], start with t = w[i − 1] and choose the matching row.'),
        T(['When generating word i', 'Value of t to use'], [
            ['i is a multiple of Nₖ', 'SubWord(RotWord(t)) XOR Rcon[i / Nₖ]'],
            ['Nₖ = 8 and i mod 8 = 4', 'SubWord(t)'],
            ['All other positions', 't, as copied from w[i − 1]']
        ], [383, 473]),
        M(r'w[i] = w[i-N_k]\oplus t.'),
        P('In AES-256, i = 8 uses the first row and i = 12 uses the second.')
    ], detail='Generate the next word', notes='Ask which row AES-192 uses at i = 12 and get the Rcon index of 2. For AES-128 at i = 6 the earlier word is w[2].', minutes=4),

    inverse_page('Follow the block to the last round', [
        P('Each full round feeds its result into the next. Here are two checkpoints for the running AES-128 example.'),
        ('states', [('After round 1', round1, []), ('After round 9', round9, [0])]),
        P('The highlighted BD enters the last SubBytes lookup. In the S-box, row B and column D give 7A.')
    ], focus='final', detail='Round 10 · A SubBytes', take='Rounds 1 through 9 each apply SubBytes, ShiftRows, MixColumns and AddRoundKey.',
       notes='The two pictures are eight rounds apart. The appendix records the intermediate rounds if students wish to trace the chain.', minutes=2),

    inverse_page('Finish round 10 with the last key', [
        ('states', [('After SubBytes', sub10, [0]), ('After ShiftRows', shift10, [0]),
                    ('Ciphertext', ciphertext, [0])]),
        C('FINAL XOR IN COLUMN ORDER',
          '   7AD5FDA7 89EF4E27 2BCA100B 3D9FF59F\n'
          '⊕  13111D7F E3944A17 F307A78B 4D2B30C5   K10\n'
          '=  69C4E0D8 6A7B0430 D8CDB780 70B4C55A', 17)
    ], focus='final', detail='Round 10 · A SubBytes → B ShiftRows → D AddRoundKey', take='In the last round, ShiftRows feeds AddRoundKey directly. The first ciphertext byte is 7A XOR 13 = 69.',
       notes='Point to 7A in the top row, which ShiftRows leaves in place. For the next byte D5 XOR 11 gives C4. The output is read down each column.', minutes=4),

    inverse_page('Decrypt the last round we just encrypted', [
        T(['Starting from ciphertext', 'First column after this operation'], [
            ['XOR with the four words of K₁₀', '7A D5 FD A7'],
            ['Rotate each row right by its row index', '7A 9F 10 27'],
            ['Apply the inverse S-box to each byte', 'BD 6E 7C 3D']
        ], [505, 351]),
        P('For the top byte, 69 XOR 13 gives 7A. The top row stays in place. Since S(BD) = 7A, the inverse S-box maps 7A back to BD.'),
        P('BD 6E 7C 3D is the first column at the end of round 9.')
    ], focus='inv_final', detail='Undo round 10 · D Key XOR → B InvShiftRows → A InvSubBytes', notes='The first-row byte stays in place during row shifts. The other three bytes in this column come from different columns during the inverse row rotations. Read their original positions on the previous slide.', minutes=3),

    inverse_page('Reverse the operations in each round', [
        T(['Encryption operation being undone', 'Decryption, starting at the ciphertext'], [
            ['Last round uses SubBytes, ShiftRows, XOR K₁₀.', 'XOR K₁₀ → InvShiftRows → InvSubBytes'],
            ['Each full round uses SubBytes, ShiftRows, MixColumns, then XOR with its key.', 'For j = 9 down to 1, apply XOR Kⱼ → InvMixColumns → InvShiftRows → InvSubBytes.'],
            ['Encryption began with XOR K₀.', 'Finish with XOR K₀ to recover the plaintext.']
        ], [422, 434]),
        P('These rows group inverse operations by the encryption round they undo. XOR with the same key cancels the original key addition.')
    ], focus='inverse_overview', detail='Decrypt · undo the encryption stages in reverse order', notes='Trace the right column from top to bottom. This grouping gives the same order as FIPS 197 INVCIPHER. There is no inverse column mixing for the last encryption round. The j subscript names whichever full round is being undone.', minutes=3),

    inverse_page('Undo the mixing of the first column', [
        C('ROUND 1, AFTER REMOVING ITS KEY',
          'mixed column    5F  72  64  15\ninverse row     0E  0B  0D  09'),
        C('MULTIPLY CORRESPONDING BYTES IN THE AES FIELD',
          '0E · 5F = 17    0B · 72 = 2B\n0D · 64 = E2    09 · 15 = BD'),
        P('XOR the four products. 17 XOR 2B = 3C, then 3C XOR E2 = DE and DE XOR BD = <b>63</b>. This recovers the top byte before MixColumns.')
    ], focus='inv_mix', detail='Undo round 1 · C InvMixColumns · column 0', take='The inverse matrix restores the full column 63 53 E0 8C. The appendix works through its field products.',
       notes='The first mixed column appears in the round 1 trace. On the board, 09 times 15 is (08 times 15) XOR 15, giving A8 XOR 15 = BD.', minutes=4),

    inverse_page('Your turn · recover four plaintext bytes', [
        P('Decryption has reached the state just before round 1 mixed its columns. Undo ShiftRows and SubBytes, then undo the first key addition.'),
        ('states', [('After undoing MixColumns', ROUND_TRACE[1]['shift_rows'], [0, 13, 10, 7])]),
        P('Which four highlighted bytes return to column 0? For the next step use S(00) = 63, S(10) = CA, S(20) = B7 and S(30) = 04. The first key column is 00 01 02 03.')
    ], focus='inv_initial', detail='Step 3 · undo B then A → step 2 · initial XOR', notes='Allow a minute for students to mark which direction undoes a left rotation. Row 3 can be rotated right three places or left one. Then apply the four lookups backwards and XOR.', minutes=4),

    inverse_page('Check the return to plaintext', [
        T(['Operation', 'Column 0, top to bottom', 'What happened?'], [
            ['InvShiftRows', '63 CA B7 04', 'The highlighted bytes returned from columns 0, 3, 2 and 1.'],
            ['InvSubBytes', '00 10 20 30', 'Each output byte was looked up in the inverse S-box.'],
            ['XOR with K₀', '00 11 22 33', '00 ⊕ 00, 10 ⊕ 01, 20 ⊕ 02, 30 ⊕ 03.']
        ], [173, 250, 433]),
        C('READ THE RECOVERED BLOCK IN COLUMN ORDER',
          '00112233 44556677 8899AABB CCDDEEFF')
    ], focus='inv_initial', detail='Undo B → A → initial XOR · check column 0', notes='Point out that an inverse row rotation moves a byte within its own row. Concatenating the displayed column first matches the original plaintext format.', minutes=3),

    closing_page('How can we check an AES implementation?', [
        C('AES-128 KNOWN-ANSWER TEST · ONE BLOCK IN HEX',
          'Key          00010203 04050607 08090A0B 0C0D0E0F\n'
          'Plaintext    00112233 44556677 8899AABB CCDDEEFF\n'
          'Ciphertext   69C4E0D8 6A7B0430 D8CDB780 70B4C55A', 17),
        P('Encrypt the specified plaintext and compare all 16 bytes with the expected ciphertext. Separately decrypt the published ciphertext and compare with the original plaintext.'),
        P('A round-trip test can pass when matching mistakes cancel. If a known-answer test fails, find the first intermediate state that differs from the reference.')
    ], detail='Known-answer test', notes='For example, encryptors and decryptors can both agree on a transposed internal mapping while disagreeing with standard AES at the interface. A single vector is useful evidence and only covers one input/key pair.', minutes=3),

    closing_page('How does a processor perform the round?', [
        T(['Implementation choice', 'How it carries out AES'], [
            ['Lookup tables', 'Tables can combine substitution and mixing. A secret-dependent index can make memory access patterns depend on secret data.'],
            ['Dedicated processor instructions', 'Intel introduced AES-NI in 2010. AESENC performs a full encryption round. AESENCLAST performs the shortened final round.'],
            ['Library implementation', 'A maintained cryptographic library can select a supported hardware path or a constant-time software implementation.']
        ], [299, 557]),
        P('For a speed measurement, report the CPU, library version, message size and whether the run includes key expansion.')
    ], detail='Implement the round', notes='A hardware AES round still needs the appropriate round key. Separate the educational hand implementation from the selection of a production library. Intel AESKEYGENASSIST assists key expansion. A hardware round instruction avoids software S-box table lookups for that round. Actual performance also depends on data size, CPU support and how the library uses the instructions.', minutes=3),

    closing_page('What makes this keyed permutation work?', [
        T(['Question from Lecture 2', 'The answer in AES'], [
            ['Where does the nonlinearity enter?', 'SubBytes maps each byte through inversion in the byte field and an affine map.'],
            ['How does one byte influence other positions?', 'MixColumns spreads a difference through a column. ShiftRows routes the resulting bytes into separate columns in the next round.'],
            ['How can the recipient undo every round?', 'The key schedule recreates the round keys. Each state transformation has an inverse, and the recipient applies them in reverse order.']
        ], [330, 526]),
        P('AES now gives us a permutation of one 16-byte block. How should we use it when a message contains many blocks?')
    ], focus='synthesis', detail='Review one-block encryption', notes='Return to the toy SPN and the same confusion/diffusion questions. Let the closing question lead into modes of operation in the following lecture.', minutes=2),
]

appendix = [
    located_slide('Compute a row of InvMixColumns', [
        M(r'\begin{pmatrix}\mathtt{0E}&\mathtt{0B}&\mathtt{0D}&\mathtt{09}\\'
          r'\mathtt{09}&\mathtt{0E}&\mathtt{0B}&\mathtt{0D}\\'
          r'\mathtt{0D}&\mathtt{09}&\mathtt{0E}&\mathtt{0B}\\'
          r'\mathtt{0B}&\mathtt{0D}&\mathtt{09}&\mathtt{0E}\end{pmatrix}'
          r'\begin{pmatrix}\mathtt{5F}\\\mathtt{72}\\\mathtt{64}\\\mathtt{15}\end{pmatrix}'
          r'=\begin{pmatrix}\mathtt{63}\\\mathtt{53}\\\mathtt{E0}\\\mathtt{8C}\end{pmatrix}'),
        T(['Input byte b', '02 · b', '04 · b', '08 · b', 'Product used in row 0'], [
            ['5F', 'BE', '67', 'CE', '0E · 5F = CE ⊕ 67 ⊕ BE = 17'],
            ['72', 'E4', 'D3', 'BD', '0B · 72 = BD ⊕ E4 ⊕ 72 = 2B'],
            ['64', 'C8', '8B', '0D', '0D · 64 = 0D ⊕ 8B ⊕ 64 = E2'],
            ['15', '2A', '54', 'A8', '09 · 15 = A8 ⊕ 15 = BD'],
        ], [134, 98, 98, 98, 428]),
        P('Double with xtime. Since 0E = 08 ⊕ 04 ⊕ 02, combine CE ⊕ 67 ⊕ BE.')
    ], section='APPENDIX', focus='inv_mix', detail='Undo round 1 · C InvMixColumns · field products', notes='The first-row products XOR to 63. Applying the other rows to the same four input bytes gives 53 E0 8C.', minutes=0),

    located_slide('Read the standard decryption loop', [
        P('Use the expanded keys in decreasing order. Here the loop groups operations as in the inverse cipher in FIPS 197.'),
        C('INVCIPHER · THE STATE STARTS AS THE CIPHERTEXT',
          'Apply AddRoundKey using the last key.\n'
          'For j from the penultimate key index down to 1:\n'
          '    InvShiftRows → InvSubBytes → AddRoundKey(K[j]) → InvMixColumns\n'
          'InvShiftRows → InvSubBytes → AddRoundKey(K[0])', 17),
        P('For AES-128, the penultimate key is K₉. Its key addition undoes the end of encryption round 9. The two inverse steps immediately before it finish undoing round 10.')
    ], section='APPENDIX', focus='inverse_overview', detail='FIPS 197 decryption loop',
       notes='FIPS 197 Algorithm 3 uses the same order for all three key sizes. The loop covers indices Nᵣ − 1 to 1 inclusive. The last AddRoundKey returns the plaintext.', minutes=0),

    located_slide('Match an AES implementation to its hardware', [
        T(['Target', 'How it can execute the same transformations'], [
            ['Small microcontroller', 'Bytewise XOR and xtime calculate MixColumns with little temporary storage. The implementation can store the S-box as a table or compute it.'],
            ['General-purpose software', 'Precomputed tables can combine substitution and mixing. Their size and memory access pattern affect both performance and side-channel exposure.'],
            ['CPU with AES support', 'AES round instructions operate on a full state. A key-schedule instruction such as AESKEYGENASSIST helps software derive round keys.'],
            ['Dedicated hardware', 'An AES circuit can reuse one round unit, or use more units to process multiple blocks in a pipeline.']
        ], [260, 596]),
        P('Run a known-answer test on each implementation. Benchmark the workload on its target platform and state whether the timing includes key expansion.')
    ], section='APPENDIX', focus='verify', detail='Compare implementations',
       notes='Older throughput figures in cycles per byte described particular processors, software and workloads. The comparable choices today depend on the target and on whether latency, throughput or memory is the limiting resource.', minutes=0),
]
