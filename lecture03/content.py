"""Assemble Lecture 3, its wall-clock schedule, and the numerical appendices."""
from copy import deepcopy
from pathlib import Path
import sys

# Share the primitives used by the preceding lecture in this repository.
sys.path.append(str(Path(__file__).resolve().parents[1] / 'lecture02'))
from deck_schema import C, M, P, T, slide
from aes_trace import KEY, PLAINTEXT, ROUND_KEYS, ROUND_STATES
from algorithm import overview
import field
import keys
import rounds


def intro(title, blocks, minutes, notes, **kwargs):
    return slide(title, blocks, section='FROM DES TO AES', minutes=minutes,
                 notes=notes, **kwargs)


opening = [
    slide('The Advanced Encryption Standard', section='LECTURE 03', kind='cover', minutes=1,
          notes='Recall the 16-bit substitution–permutation network from Lecture 2. Ask what students would need to trace a real cipher in the same way. Return to the question during the first round.'),
    intro('From the toy network to AES', [
        P('Last time we encrypted a 16-bit block by substituting small groups, moving bits and XORing round keys. What changes when the block holds 16 bytes?'),
        T(['In the toy network', 'In an AES round'], [
            ['A lookup replaces each four-bit group.', 'SubBytes replaces each eight-bit byte.'],
            ['Wires move bits to new groups.', 'ShiftRows moves bytes. MixColumns combines four bytes at a time.'],
            ['XOR introduces the round key.', 'AddRoundKey XORs a 16-byte key into the state.'],
        ], [1, 1.3]),
        P('We will trace one block and then run the transformations backwards.'),
    ], 2, 'Ask students which operation from the toy SPN they can already invert. XOR undoes itself. A Feistel network can use a many-to-one inner function, whereas each AES state layer has an inverse.'),
    intro('How Rijndael became AES', [
        ('timeline', [
            ('1997', 'NIST calls for a successor to DES.'),
            ('1998', 'Fifteen candidate algorithms enter the evaluation.'),
            ('2000', 'NIST selects Rijndael, designed by Joan Daemen and Vincent Rijmen.'),
            ('2001', 'FIPS 197 specifies the Advanced Encryption Standard.'),
        ]),
        P('DES used a 56-bit key and a 64-bit block. Rijndael offered larger keys and a 128-bit block for the new standard.'),
        P('Today a browser can negotiate AES-GCM to protect a TLS connection. AES supplies the block cipher. The mode specifies how to protect messages that span many blocks.'),
    ], 2, 'Recall the 56-bit effective key and the 64-bit block in DES. In 2023 NIST updated the presentation of FIPS 197 while keeping the algorithm the same. AES-GCM in TLS 1.3 is a point of contact with deployed systems. Modes will be covered later.'),
    intro('What does the number in AES-256 count?', [
        T(['Variant', 'Block size', 'Master key', 'Encryption rounds'], [
            ['AES-128', '128 bits', '128 bits', '10'],
            ['AES-192', '128 bits', '192 bits', '12'],
            ['AES-256', '128 bits', '256 bits', '14'],
        ]),
        P('All three operate on exactly 16 bytes at a time. The suffix gives the key length. A longer key also changes how the round keys are generated.'),
        P('For the worked example we use AES-128, so the master key and the block each occupy 16 bytes.'),
    ], 2, 'Ask how many state columns AES-256 has. The answer is four, as for AES-128. Reserve the key-schedule details for the final hour.'),
    *overview,
    intro('Place 16 input bytes into the state', [
        C('PLAINTEXT BYTES IN INPUT ORDER', '00 11 22 33   44 55 66 77   88 99 AA BB   CC DD EE FF', 19),
        ('states', [('Plaintext state', PLAINTEXT, [0, 1, 2, 3])]),
        P('Fill the highlighted column from top to bottom with the first four bytes. The fifth byte, 44, starts the next column. Labels r and c count rows and columns from zero.'),
    ], 3, 'Write the first four bytes vertically on the board. Ask which byte lies below 44 and wait for 55. When reading the ciphertext later, reverse this loading rule.'),
    intro('Where does byte 99 belong?', [
        P('Try it before looking down. In the input string, 99 has index 9. Which row and column does it occupy?'),
        M(r'\mathrm{state}[r,c]=\mathrm{input}[4c+r],\qquad r,c\in\{0,1,2,3\}'),
        ('states', [('Locate input byte 9', PLAINTEXT, [9]), ('Load the key by the same rule', KEY, [9])]),
        P('Since 9 = 4 × 2 + 1, look in row 1, column 2. The plaintext byte 99 meets key byte 09 at this position.'),
    ], 2, 'Give students thirty seconds to predict both coordinates with the grid covered. Ask for the initial XOR at that cell. The answer is 90 in hex.'),

]


def byte_table(name, inverse=False):
    return slide(name, [
        P('Look up the first hex digit in the row labels and the second in the column labels.'),
        ('boxmap', inverse),
    ], section='APPENDIX', minutes=0, notes='This table is indexed by the input byte. Both nibble labels use hexadecimal. Highlighted entries trace 05 → 6B and 6B → 05.')


def spaced(hex_string):
    return ' '.join(hex_string[i:i + 8] for i in range(0, 32, 8))


def checkpoints(first, last):
    rows = [[str(i), spaced(ROUND_KEYS[i]), spaced(ROUND_STATES[i])] for i in range(first, last + 1)]
    return slide(f'AES-128 checkpoints, rounds {first}–{last}', [
        P('Read the four groups left to right. Each group holds one state column, top byte first. Round 0 denotes the initial key XOR.'),
        T(['Round', 'Round key (four words)', 'State after AddRoundKey'], rows, [.65, 2.65, 2.65]),
        P('Use a matching round boundary to check your working before moving to the next round.'),
    ], section='APPENDIX', minutes=0, notes='All values use the plaintext 00112233445566778899AABBCCDDEEFF and the ascending key starting at 00. The original FIPS 197 Appendix C.1 lists the same example.')


for item in opening:
    if item['title'] in ('Place 16 input bytes into the state', 'Where does byte 99 belong?'):
        item['aes_focus'] = 'state'

slides = []
plan = []


def add_session(label, start, end, items):
    items = deepcopy(items)
    first = len(slides) + 1
    estimate = sum(s['minutes'] for s in items)
    start_h, start_m = map(int, start.split(':'))
    end_h, end_m = map(int, end.split(':'))
    duration = 60 * (end_h - start_h) + end_m - start_m
    slides.extend(items)
    plan.append(dict(label=label, start=start, end=end, first=first, last=len(slides), minutes=duration, estimate=estimate))


def add_break(number, start, end, prompt, hint):
    br = slide('Break / 15 minutes', [P(prompt), P(hint)], section=f'BREAK {number:02d}',
               kind='divider', minutes=15, take=f'{start}–{end}  •  Return at {end}',
               notes=f'Resume at {end}.')
    add_session(f'Break {number}', start, end, [br])


add_session('From the toy SPN to AES byte arithmetic', '18:30', '19:30', opening + field.slides)
add_break(1, '19:30', '19:45', 'We found the byte that undoes multiplication by 05.',
          'After the break we will see how that inverse becomes an entry in the AES substitution table.')
add_session('A complete first round of AES-128', '19:45', '20:45', rounds.slides)
add_break(2, '20:45', '21:00', 'We have followed all 16 bytes through the first round.',
          'After the break we will derive its round key and work back from the ciphertext.')
add_session('Key expansion, decryption and implementation', '21:00', '22:00', keys.slides)
MAIN_COUNT = len(slides)
assert [b['minutes'] for b in plan] == [60, 15, 60, 15, 60], plan

reference = [
    byte_table('Forward S-box'),
    byte_table('Inverse S-box', True),
    checkpoints(0, 5),
    checkpoints(6, 10),
] + field.appendix + rounds.appendix + keys.appendix

appendix_focus = {
    'Forward S-box': 'sbox_ref',
    'Inverse S-box': 'inverse_lookup',
    'Which binary polynomials are irreducible?': 'math_inverse',
    'A second integer inverse by back-substitution': 'math_inverse',
    'How polynomial coefficients wrap into four rows': 'mix',
    'Why the fixed column multiplier has an inverse': 'inv_mix',
}

for index, item in enumerate(deepcopy(reference), 1):
    if item['title'].startswith('AES-128 checkpoints'):
        item['aes_focus'] = 'checkpoints'
    elif item['title'] in appendix_focus:
        item['aes_focus'] = appendix_focus[item['title']]
    item.update(title=f'A{index} / {item["title"]}', section='APPENDIX', minutes=0)
    slides.append(item)


# The numerical walkthrough begins immediately after the two algorithm overviews.
first_example = slides.index(next(s for s in slides if s['title'] == 'Place 16 input bytes into the state'))
assert all(s.get('aes_focus') for s in slides[first_example:] if s['kind'] != 'divider')
