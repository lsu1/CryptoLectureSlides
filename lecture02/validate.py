"""Verify the lecture's computed examples, printed data, schedule, and PDFs.

Run ``python lecture02/validate.py --content-only`` while editing the sources,
or omit the flag after both final PDFs have been built. The full run writes a
machine-readable validation.json; it does not substitute for visual review.
"""
from collections import Counter
from datetime import datetime
from fractions import Fraction
from html.parser import HTMLParser
from math import factorial, isclose, log2
from pathlib import Path
import argparse
import hashlib
import json
import re

import fitz
from reportlab.pdfbase.ttfonts import TTFont
import crypto_examples as cx
import otp_content as oc
import block_content as bc


ROOT = Path(__file__).resolve().parent
CHECKS = []
FONT_FILES = {'Sans': 'DejaVuSans.ttf', 'Bold': 'DejaVuSans-Bold.ttf',
              'Mono': 'DejaVuSansMono.ttf', 'Italic': 'DejaVuSans-Oblique.ttf'}
FONT_CMAPS = {name: {codepoint for codepoint, glyph in TTFont('Check' + name,
                     '/usr/share/fonts/truetype/dejavu/' + filename).face.charToGlyph.items() if glyph != 0}
              for name, filename in FONT_FILES.items()}


class PlainText(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.feed(text)

    def handle_data(self, data):
        self.parts.append(data)


def unsupported(text, font):
    return sorted({character for character in text
                   if not character.isspace() and ord(character) not in FONT_CMAPS[font]})


def checked(name, condition):
    if not condition:
        raise AssertionError(name)
    CHECKS.append(name)


def walk_blocks(blocks):
    for block in blocks:
        yield block
        if block[0] == 'two':
            yield from walk_blocks(block[1])
            yield from walk_blocks(block[2])


def tables(items, headers):
    return [block for item in items for block in walk_blocks(item['blocks'])
            if block[0] == 'table' and block[1] == headers]


def one_table(items, headers):
    matches = tables(items, headers)
    if len(matches) != 1:
        raise AssertionError(f'Expected one table with headers {headers!r}; found {len(matches)}')
    return matches[0][2]


def code_text(items):
    return '\n'.join(block[2] for item in items for block in walk_blocks(item['blocks'])
                     if block[0] == 'code')


def numerical_checks():
    checked('Letter OTP known answer and decryption',
            cx.OTP_CIPHERTEXT == oc.OTP_LETTER_CIPHERTEXT == 'KRGPPYQ'
            and cx.otp_letters(cx.OTP_CIPHERTEXT, cx.OTP_KEY, True) == cx.OTP_PLAINTEXT)
    letter_rows = [[p, k, f'({ord(p)-65} + {ord(k)-65}) mod 26 = {(ord(p)+ord(k)-130)%26}', c]
                   for p, k, c in zip(cx.OTP_PLAINTEXT, cx.OTP_KEY, cx.OTP_CIPHERTEXT)]
    checked('Every printed letter-OTP addition matches the original example',
            one_table(oc.OTP_SLIDES, ['Plaintext', 'Key', 'Add modulo 26', 'Output']) == letter_rows)
    checked('Printed XOR truth table contains the four correct cases',
            one_table(oc.OTP_SLIDES, ['Bit a', 'Bit b', 'a ⊕ b']) ==
            [[str(a), str(b), str(a ^ b)] for a in range(2) for b in range(2)])
    checked('Ten-bit exercise and its inverse preserve the specified length',
            cx.OTP_BITS_CIPHERTEXT == oc.OTP_BIT_CIPHERTEXT == '1100110110'
            and cx.xor_bits(oc.OTP_BIT_CIPHERTEXT, oc.OTP_BIT_KEY) == oc.OTP_BIT_PLAINTEXT
            and len(oc.OTP_BIT_CIPHERTEXT) == 10
            and cx.xor_bits('0001', '0001') == '0000')
    checked('Printed binary worked answer uses the actual exercise data',
            all(value in code_text(oc.OTP_SLIDES) for value in
                [oc.OTP_BIT_PLAINTEXT, oc.OTP_BIT_KEY, oc.OTP_BIT_CIPHERTEXT]))
    reuse_relation = cx.xor_bits(oc.OTP_BIT_PLAINTEXT, oc.OTP_REUSE_SECOND_PLAINTEXT)
    checked('Pad-reuse cancellation and known-plaintext recovery',
            cx.xor_bits(oc.OTP_BIT_CIPHERTEXT, oc.OTP_REUSE_SECOND_CIPHERTEXT)
            == oc.OTP_REUSE_RELATION == reuse_relation == '0110010101'
            and cx.xor_bits(oc.OTP_BIT_PLAINTEXT, reuse_relation) == oc.OTP_REUSE_SECOND_PLAINTEXT)
    checked('Printed reused-pad data matches both encryptions and their XOR',
            [row[1] for row in one_table(oc.OTP_SLIDES, ['Quantity', 'Ten-bit value'])] ==
            [oc.OTP_BIT_PLAINTEXT, oc.OTP_REUSE_SECOND_PLAINTEXT, oc.OTP_BIT_CIPHERTEXT,
             cx.xor_bits(oc.OTP_REUSE_SECOND_PLAINTEXT, oc.OTP_BIT_KEY), reuse_relation])
    checked('Every two-bit plaintext has exactly one compatible pad for ciphertext 10',
            oc.OTP_COMPATIBILITY_ROWS ==
            [(f'{p:02b}', f'{p ^ 2:02b}') for p in range(4)]
            and all(cx.xor_bits(p, k) == '10' for p, k in oc.OTP_COMPATIBILITY_ROWS))

    # Exact enumeration supplies an independent check of the arbitrary-prior
    # proof, including plaintexts with zero prior probability.
    prior_examples = [(1, [1, 3]), (2, [4, 2, 1, 1]),
                      (3, [0, 1, 2, 0, 4, 5, 0, 7]), (4, list(range(1, 17)))]
    for bits, weights in prior_examples:
        size = 1 << bits
        prior = [Fraction(weight, sum(weights)) for weight in weights]
        joint = {(p, c): Fraction(0) for p in range(size) for c in range(size)}
        for p in range(size):
            for k in range(size):
                joint[p, p ^ k] += prior[p] / size
        marginals = [sum(joint[p, c] for p in range(size)) for c in range(size)]
        checked(f'Exact OTP perfect secrecy for a nonuniform {bits}-bit plaintext prior',
                all(pc == Fraction(1, size) for pc in marginals)
                and all(joint[p, c] / marginals[c] == prior[p]
                        for p in range(size) for c in range(size)))
    prior_rows = one_table(oc.OTP_SLIDES,
                          ['Candidate p', 'Prior Pr[P = p]', 'Posterior after C = 10'])
    checked('Printed biased prior and posterior equal the exact enumerated distribution',
            [(p, Fraction(a), Fraction(b)) for p, a, b in prior_rows] ==
            [(f'{p:02b}', Fraction(w, 8), Fraction(w, 8)) for p, w in enumerate([4, 2, 1, 1])])

    outcomes = [(a, b) for a in range(1, 7) for b in range(1, 7)]
    sum4 = [pair for pair in outcomes if sum(pair) == 4]
    doubles = [pair for pair in outcomes if pair[0] == pair[1]]
    both = set(sum4) & set(doubles)
    checked('Two-dice event counts and exact marginal probabilities',
            len(outcomes) == 36 and sum4 == [(1, 3), (2, 2), (3, 1)]
            and both == {(2, 2)} and cx.DICE_P_SUM4 == Fraction(1, 12)
            and cx.DICE_P_DOUBLE == Fraction(1, 6))
    checked('Exact conditional probabilities and both Bayes products',
            cx.DICE_P_DOUBLE_GIVEN_SUM4 == Fraction(len(both), len(sum4)) == Fraction(1, 3)
            and cx.DICE_P_SUM4_GIVEN_DOUBLE == Fraction(len(both), len(doubles)) == Fraction(1, 6)
            and cx.DICE_P_DOUBLE_GIVEN_SUM4 * cx.DICE_P_SUM4
            == cx.DICE_P_SUM4_GIVEN_DOUBLE * cx.DICE_P_DOUBLE == Fraction(1, 36))
    dice_rows = one_table(oc.OTP_SLIDES, ['Event', 'Favourable outcomes', 'Probability'])
    checked('Printed dice probabilities match the exact sample-space counts',
            [row[2] for row in dice_rows] == ['3/36 = 1/12', '6/36 = 1/6', '1/36'])
    checked('Coin entropies, including zero-probability terms',
            cx.entropy([Fraction(1, 2), Fraction(1, 2)]) == cx.ENTROPY_FAIR_COIN == 1
            and isclose(cx.entropy([Fraction(7, 10), Fraction(3, 10)]), 0.8812908992306927)
            and cx.entropy([0, 1]) == cx.ENTROPY_CERTAIN_COIN == 0
            and all(isclose(a, b, abs_tol=1e-12) for a, b in
                    zip(oc.OTP_COIN_ENTROPIES, [1, cx.ENTROPY_BIASED_COIN, 0])))
    entropy_diagrams = [b for item in oc.OTP_SLIDES for b in walk_blocks(item['blocks'])
                        if b[:2] == ('diagram', 'entropy_bars')]
    checked('Entropy illustration is driven by the verified coin distributions',
            len(entropy_diagrams) == 1
            and entropy_diagrams[0][2]['probabilities'] == [0.5, 0.7, 1.0]
            and entropy_diagrams[0][2]['entropies'] == oc.OTP_COIN_ENTROPIES)
    hmax, rate = log2(26), 1.25
    redundancy = hmax - rate
    key_entropy = log2(factorial(26))
    checked('One consistent language-rate assumption drives redundancy and unicity',
            oc.OTP_HL == cx.ENGLISH_RATE_ILLUSTRATIVE == rate
            and isclose(oc.OTP_HMAX, hmax)
            and isclose(oc.OTP_REDUNDANCY_BITS, redundancy)
            and isclose(cx.ENGLISH_REDUNDANCY_BITS, redundancy)
            and isclose(oc.OTP_REDUNDANCY_FRACTION, redundancy / hmax)
            and isclose(cx.ENGLISH_REDUNDANCY, redundancy / hmax)
            and isclose(oc.OTP_SUBSTITUTION_KEY_ENTROPY, key_entropy)
            and isclose(cx.SUBSTITUTION_KEY_ENTROPY, key_entropy)
            and isclose(oc.OTP_UNICITY_ESTIMATE, key_entropy / redundancy)
            and isclose(cx.SUBSTITUTION_UNICITY_DISTANCE, 25.61469277710924))
    approximations = [float(value) for item in oc.OTP_SLIDES for block in walk_blocks(item['blocks'])
                      if block[0] == 'math'
                      for value in re.findall(r'\\approx\s*([0-9]+(?:\.[0-9]+)?)', block[1])]
    checked('Printed entropy, redundancy, and unicity approximations use consistent rounding',
            all(value in approximations for value in
                [round(hmax, 4), round(redundancy, 4), round(redundancy / hmax, 4),
                 round(key_entropy, 3), round(key_entropy / redundancy, 1)]))

    checked('DES standard known-answer encryption and decryption',
            cx.DES_PLAINTEXT == 0x0123456789ABCDEF
            and cx.DES_KEY == 0x133457799BBCDFF1
            and cx.DES_CIPHERTEXT == 0x85E813540F0AB405
            and cx.des_encrypt(cx.DES_CIPHERTEXT, cx.DES_KEY, decrypt=True) == cx.DES_PLAINTEXT)
    trace = cx.DES_TRACE
    first, last = trace['rounds'][0], trace['rounds'][-1]
    checked('DES initial permutation and independently known first-round internals',
            trace['post_ip'] == 0xCC00CCFFF0AAF0AA
            and (trace['l0'], trace['r0']) == (0xCC00CCFF, 0xF0AAF0AA)
            and first['key'] == 0x1B02EFFC7072
            and first['expanded'] == 0x7A15557A1555
            and first['xored'] == 0x6117BA866527
            and first['sbox_output'] == 0x5C82B597
            and first['f'] == 0x234AA9BB
            and (first['l'], first['r']) == (0xF0AAF0AA, 0xEF4A6544))
    checked('DES final round, final swap, and inverse permutation',
            len(trace['rounds']) == 16 and last['key'] == 0xCB3D8B0E17F5
            and (last['l'], last['r']) == (0x43423234, 0x0A4CD995)
            and trace['preoutput'] == 0x0A4CD99543423234
            and cx.permute(trace['preoutput'], cx.FP, 64) == cx.DES_CIPHERTEXT)
    checked('DES first-round S1 lookup uses outer-bit row and inner-bit column',
            cx.des_sbox(1, 0b011000) == cx.SBOXES[0][0][12] == 0b0101
            and first['boxes'][0]['input'] == 0b011000
            and (first['boxes'][0]['row'], first['boxes'][0]['column']) == (0, 12))
    checked('DES first-round S-box inputs and outputs match the published trace',
            [row['input'] for row in first['boxes']] ==
            [0b011000, 0b010001, 0b011110, 0b111010, 0b100001, 0b100110, 0b010100, 0b100111]
            and [row['output'] for row in first['boxes']] == [5, 12, 8, 2, 11, 5, 9, 7])
    checked('DES IP and FP are inverse bit permutations on every basis vector',
            sorted(cx.IP) == sorted(cx.FP) == list(range(1, 65))
            and all(cx.permute(cx.permute(1 << bit, cx.IP, 64), cx.FP, 64) == 1 << bit
                    for bit in range(64)))
    checked('DES selection and permutation tables have the specified widths',
            len(cx.E) == 48 and set(cx.E) == set(range(1, 33))
            and sorted(cx.P) == list(range(1, 33))
            and len(cx.PC1) == len(set(cx.PC1)) == 56
            and set(cx.PC1) == set(range(1, 65)) - set(range(8, 65, 8))
            and len(cx.PC2) == len(set(cx.PC2)) == 48
            and set(cx.PC2) <= set(range(1, 57)))
    kt = cx.DES_KEY_TRACE
    checked('DES key schedule known initial halves and first rotated halves',
            kt['pc1'] == 0xF0CCAAF556678F
            and (kt['c0'], kt['d0']) == (0xF0CCAAF, 0x556678F)
            and (kt['rounds'][0]['c'], kt['rounds'][0]['d']) == (0xE19955F, 0xAACCF1E))
    checked('DES sixteen 48-bit subkeys follow rotations totalling 28 positions',
            cx.SHIFTS == [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
            and sum(cx.SHIFTS) == 28 and len(cx.des_subkeys(cx.DES_KEY)) == 16
            and all(0 <= key < 1 << 48 for key in cx.des_subkeys(cx.DES_KEY))
            and (kt['rounds'][-1]['c'], kt['rounds'][-1]['d']) == (kt['c0'], kt['d0'])
            and all(row['key'] == cx.permute((row['c'] << 28) | row['d'], cx.PC2, 56)
                    for row in kt['rounds']))
    parity_mask = 0x0101010101010101
    checked('DES parity bits do not contribute to the effective encryption key',
            cx.has_odd_parity(cx.DES_KEY) and not cx.has_odd_parity(cx.DES_KEY ^ parity_mask)
            and cx.des_subkeys(cx.DES_KEY) == cx.des_subkeys(cx.DES_KEY ^ parity_mask)
            and cx.des_encrypt(cx.DES_PLAINTEXT, cx.DES_KEY ^ parity_mask) == cx.DES_CIPHERTEXT)
    test_keys = [0, 0xFFFFFFFFFFFFFFFF, cx.DES_KEY, 0x0E329232EA6D0D73]
    test_blocks = [0, 1, 0xFFFFFFFFFFFFFFFF, cx.DES_PLAINTEXT, 0x8000000000000000]
    checked('DES round-trips diverse blocks under several keys',
            all(cx.des_encrypt(cx.des_encrypt(block, key), key, decrypt=True) == block
                for key in test_keys for block in test_blocks))
    checked('Every DES trace obeys the Feistel round equations',
            all(row['l'] == row['r_in'] and row['r'] == row['l_in'] ^ row['f']
                for row in trace['rounds']))
    checked('Triple-DES EDE decryption reverses encryption and equal keys recover DES',
            all(cx.triple_des_encrypt(cx.triple_des_encrypt(block, *test_keys[:3]),
                                      *test_keys[:3], decrypt=True) == block
                and cx.triple_des_encrypt(block, cx.DES_KEY, cx.DES_KEY, cx.DES_KEY)
                == cx.des_encrypt(block, cx.DES_KEY) for block in test_blocks))
    checked('DES one-bit-change trace and avalanche count are computed consistently',
            (cx.DES_PLAINTEXT ^ cx.DES_FLIPPED_PLAINTEXT).bit_count() == 1
            and cx.DES_AVALANCHE == (cx.DES_CIPHERTEXT ^ cx.DES_FLIPPED_CIPHERTEXT).bit_count()
            and cx.DES_ROUND_DIFFERENCES ==
            [(a['l'] ^ b['l']).bit_count() + (a['r'] ^ b['r']).bit_count()
             for a, b in zip(trace['rounds'], cx.DES_FLIPPED_TRACE['rounds'])])

    checked('Toy SPN S-box and bit routing are bijections with correct inverses',
            sorted(cx.TOY_SBOX) == list(range(16))
            and all(cx.TOY_INV_SBOX[cx.TOY_SBOX[x]] == x for x in range(16))
            and sorted(cx.TOY_PERM) == list(range(1, 17))
            and all(cx.permute(cx.permute(1 << bit, cx.TOY_PERM, 16), cx.TOY_INV_PERM, 16)
                    == 1 << bit for bit in range(16)))
    checked('Toy SPN known trace has three substitution rounds and final whitening',
            cx.TOY_PLAINTEXT == 0x1234 and cx.TOY_CIPHERTEXT == 0xD9F0
            and len(cx.TOY_TRACE['rounds']) == 3
            and cx.TOY_TRACE['rounds'][-1]['permuted'] is None
            and cx.TOY_CIPHERTEXT == cx.TOY_TRACE['rounds'][-1]['state'] ^ cx.TOY_KEYS[3])
    checked('Toy SPN round-trips representative blocks and an alternate round-key list',
            all(cx.toy_decrypt(cx.toy_encrypt(block, keys), keys) == block
                for keys in [cx.TOY_KEYS, [0, 0, 0, 0], [0xFFFF, 0x0123, 0x8000, 0x4567]]
                for block in [0, 1, 0x1234, 0x8000, 0xFFFF]))
    toy_first = cx.TOY_TRACE['rounds'][0]
    toy_blocks = [block for item in bc.BLOCK_SLIDES for block in walk_blocks(item['blocks'])]
    xor_values = [cx.TOY_PLAINTEXT, cx.TOY_KEYS[0], cx.TOY_PLAINTEXT ^ cx.TOY_KEYS[0]]
    checked('Worked toy XOR table displays the correct hexadecimal and every input/output bit',
            [row[1:] for row in one_table(bc.BLOCK_SLIDES, ['', 'Hex', 'Bits in groups of four'])]
            == [[f'{value:04X}', ' '.join(f'{value:016b}'[start:start+4] for start in range(0, 16, 4))]
                for value in xor_values]
            and xor_values[-1] == toy_first['mixed'])
    toy_lookups = [block[2] for block in toy_blocks if block[:2] == ('diagram', 'toy_sbox_lookup')]
    checked('Worked toy S-box lookup uses the first key-XOR result and the specified bijection',
            len(toy_lookups) == 1 and toy_lookups[0]['value'] == toy_first['mixed'] == 0x28A0
            and toy_lookups[0]['sbox'] == cx.TOY_SBOX
            and sum(toy_lookups[0]['sbox'][(toy_lookups[0]['value'] >> shift) & 15] << shift
                    for shift in [12, 8, 4, 0]) == toy_first['substituted'] == 0xD36E)
    bit_picks = [block[2] for block in toy_blocks if block[:2] == ('diagram', 'toy_bit_positions')]
    first_positions = cx.TOY_PERM[:4]
    checked('Worked bit-position diagram selects the first output nibble from the S-box result',
            len(bit_picks) == 1 and bit_picks[0]['value'] == toy_first['substituted']
            and bit_picks[0]['positions'] == first_positions == [1, 5, 9, 13]
            and cx.permute(bit_picks[0]['value'], bit_picks[0]['positions'], 16) == 9)
    input_bits = f'{toy_first["substituted"]:016b}'
    expected_groups = []
    for start in range(0, 16, 4):
        positions = cx.TOY_PERM[start:start+4]
        copied = ''.join(input_bits[position-1] for position in positions)
        expected_groups.append([f'{start+1}–{start+4}', ', '.join(map(str, positions)),
                                copied, f'{int(copied, 2):X}'])
    checked('All four printed permutation groups copy the specified bits and form 9B7C',
            one_table(bc.BLOCK_SLIDES, ['Output bits', 'Copy input positions', 'Bits copied', 'Hex digit'])
            == expected_groups
            and expected_groups[0][2:] == ['1001', '9']
            and int(''.join(row[3] for row in expected_groups), 16)
            == cx.permute(toy_first['substituted'], cx.TOY_PERM, 16) == toy_first['state'] == 0x9B7C)
    expected_toy = [[f'Round {i+1}', f'{cx.TOY_KEYS[i]:04X}', f'{row["mixed"]:04X}',
                     f'{row["substituted"]:04X}', f'{row["state"]:04X}' if i < 2 else 'P omitted']
                    for i, row in enumerate(cx.TOY_TRACE['rounds'])]
    expected_toy.append(['Final whitening', f'{cx.TOY_KEYS[3]:04X}', '—', '—', f'{cx.TOY_CIPHERTEXT:04X}'])
    checked('Printed complete toy trace matches all computed intermediate states',
            one_table(bc.BLOCK_SLIDES, ['Stage', 'XOR key', 'After key XOR', 'After S-boxes',
                                      'After P / output']) == expected_toy)
    avalanche_rows = one_table(bc.BLOCK_SLIDES,
                               ['Input / stage', 'Original', 'One-bit-changed', 'Differing bits'])
    changed_input = int(avalanche_rows[0][2], 16)
    changed_output, changed_trace = cx.toy_encrypt(changed_input, trace=True)
    expected_avalanche = [['Plaintext', f'{cx.TOY_PLAINTEXT:04X}', f'{changed_input:04X}', '1']]
    expected_avalanche += [[f'After round {i+1}', f'{a["state"]:04X}', f'{b["state"]:04X}',
                            str((a['state'] ^ b['state']).bit_count())]
                           for i, (a, b) in enumerate(zip(cx.TOY_TRACE['rounds'], changed_trace['rounds']))]
    expected_avalanche += [['Ciphertext', f'{cx.TOY_CIPHERTEXT:04X}', f'{changed_output:04X}',
                            str((cx.TOY_CIPHERTEXT ^ changed_output).bit_count())]]
    checked('Printed toy avalanche trace uses one input-bit change and actual state differences',
            (changed_input ^ cx.TOY_PLAINTEXT).bit_count() == 1 and avalanche_rows == expected_avalanche)


def assembled_checks(slides, main_count, plan, des_content):
    nonbreak_titles = [s['title'] for s in slides if not s['section'].startswith('BREAK')]
    checked('Main/appendix boundary is valid and non-break titles are distinct',
            0 < main_count <= len(slides)
            and len(set(nonbreak_titles)) == len(nonbreak_titles)
            and all(s['section'] == 'APPENDIX' and s['minutes'] == 0 for s in slides[main_count:]))
    main_titles = {s['title'] for s in slides[:main_count]}
    core = oc.OTP_SLIDES + bc.BLOCK_SLIDES + des_content.FEISTEL_SLIDES + des_content.DES_SLIDES
    checked('Core material from all three source topics is included in the teaching sequence',
            all(item['title'] in main_titles for item in core))
    appendix_titles = {re.sub(r'^A\d+ / ', '', s['title']) for s in slides[main_count:]}
    checked('Authored optional mathematical and DES tables remain available in the appendix',
            all(item['title'] in appendix_titles for item in oc.OTP_APPENDIX + des_content.DES_APPENDIX))
    checked('All teaching slides have delivery notes and positive allocated time',
            all(s.get('notes', '').strip() and s['minutes'] > 0 for s in slides[:main_count]))
    checked('Session allocates 210 minutes, including 20 break and 190 teaching minutes',
            sum(row['minutes'] for row in plan) == 210
            and sum(row['minutes'] for row in plan if row['kind'] == 'break') == 20
            and sum(row['minutes'] for row in plan if row['kind'] == 'teaching') == 190
            and isclose(sum(s['minutes'] for s in slides[:main_count]), 210, abs_tol=1e-9))
    coverage = []
    previous_end = None
    for row in plan:
        start = datetime.strptime(row['start'], '%I:%M %p')
        end = datetime.strptime(row['end'], '%I:%M %p')
        checked('Wall-clock interval and per-slide allocation: ' + row['start'] + '–' + row['end'],
                (end - start).total_seconds() == row['minutes'] * 60
                and (previous_end is None or start == previous_end)
                and isclose(sum(s['minutes'] for s in slides[row['slides'][0]-1:row['slides'][1]]),
                            row['minutes'], abs_tol=1e-9))
        coverage.extend(range(row['slides'][0], row['slides'][1]+1))
        previous_end = end
    checked('Session spans 6:30–10:00 pm and covers every main slide once',
            plan[0]['start'] == '6:30 pm' and plan[-1]['end'] == '10:00 pm'
            and coverage == list(range(1, main_count+1)))
    breaks = [row for row in plan if row['kind'] == 'break']
    checked('Exactly two ten-minute break slides display the scheduled wall-clock times',
            len(breaks) == 2
            and all(row['minutes'] == 10 and row['slides'][0] == row['slides'][1]
                    and slides[row['slides'][0]-1]['section'].startswith('BREAK')
                    and row['start'] in slides[row['slides'][0]-1]['take']
                    and row['end'] in slides[row['slides'][0]-1]['take'] for row in breaks))


def des_printed_checks(dc):
    forward = [(0b1010, 0b1100)]
    for key in [0b0110, 0b0101]:
        left, right = forward[-1]
        forward.append((right, left ^ (right & key)))
    reverse = [(forward[-1][1], forward[-1][0])]
    for key in [0b0101, 0b0110]:
        left, right = reverse[-1]
        reverse.append((right, left ^ (right & key)))
    checked('Printed forward and reverse Feistel example follows the stated non-invertible F',
            [row[1:] for row in one_table(dc.FEISTEL_SLIDES, ['Forward step', 'L', 'R'])]
            == [[f'{left:04b}', f'{right:04b}'] for left, right in forward]
            and [row[1:] for row in one_table(dc.FEISTEL_SLIDES, ['Reverse step', 'L', 'R'])]
            == [[f'{left:04b}', f'{right:04b}'] for left, right in reverse]
            and (reverse[-1][1], reverse[-1][0]) == forward[0]
            and (0b0000 & 0b0110) == (0b0001 & 0b0110))
    first = cx.DES_TRACE['rounds'][0]
    # Use strings with explicit MSB-first indexing as an independent route
    # through the worked bit selections, rather than reuse cx.permute.
    def select_bits(value, positions, width):
        source = f'{value:0{width}b}'
        return ''.join(source[position-1] for position in positions)

    def normalized_rows(rows):
        return [[str(cell) for cell in row] for row in rows]

    def des_slide(title):
        matches = [item for item in dc.DES_SLIDES if item['title'] == title]
        if len(matches) != 1:
            raise AssertionError(f'Expected one DES slide titled {title!r}')
        return matches

    ip_positions = [58, 50, 42, 34, 26, 18, 10, 2]
    ip_bits = select_bits(cx.DES_PLAINTEXT, ip_positions, 64)
    checked('Worked IP first byte independently copies bits 58,50,42,34,26,18,10,2',
            ip_bits == '11001100' and ip_bits[0] == '1'
            and normalized_rows(one_table(des_slide('How to read the initial permutation'),
                ['Output position'] + [str(i) for i in range(1, 9)])) ==
            [['Read input bit'] + list(map(str, ip_positions)),
             ['Bit copied'] + list(ip_bits)]
            and f'{cx.DES_TRACE["post_ip"]:064b}'[:8] == ip_bits)
    e_positions = [32, 1, 2, 3, 4, 5]
    e_bits = select_bits(cx.DES_TRACE['r0'], e_positions, 32)
    expanded_bits = f'{first["expanded"]:048b}'
    key_bits = f'{first["key"]:048b}'
    xor_bits = ''.join(str(int(a) ^ int(b)) for a, b in zip(expanded_bits, key_bits))
    checked('Worked expansion group independently copies R0 and retains its leading zero',
            e_bits == expanded_bits[:6] == '011110'
            and normalized_rows(one_table(des_slide('Build the first six expansion bits'),
                ['Output position'] + [str(i) for i in range(1, 7)])) ==
            [['Read input bit'] + list(map(str, e_positions)),
             ['Bit copied'] + list(e_bits)])
    checked('Worked first six expanded and subkey bits XOR to the actual S1 input',
            key_bits[:6] == '000110' and xor_bits[:6] == '011000'
            and int(xor_bits, 2) == first['xored'] == 0x6117BA866527
            and all(value in code_text(dc.DES_SLIDES)
                    for value in [e_bits, key_bits[:6], xor_bits[:6]]))

    rotated_halves = cx.DES_KEY_TRACE['rounds'][0]
    combined_key = (rotated_halves['c'] << 28) | rotated_halves['d']
    pc2_positions = [14, 17, 11, 24, 1, 5]
    selected_key_bits = select_bits(combined_key, pc2_positions, 56)
    checked('Worked PC2 first six selections reproduce the round-key bits used at S1',
            selected_key_bits == key_bits[:6] == '000110'
            and normalized_rows(one_table(des_slide('Recover the six key bits we used'),
                ['Output position'] + [str(i) for i in range(1, 7)])) ==
            [['Read input bit'] + list(map(str, pc2_positions)),
             ['Bit copied'] + list(selected_key_bits)]
            and f'{first["key"]:012X}' in code_text(des_slide('Recover the six key bits we used')))

    s1_diagrams = [block[2] for item in dc.DES_SLIDES for block in walk_blocks(item['blocks'])
                   if block[:2] == ('diagram', 'des_lookup')]
    checked('Worked S1 diagram uses the complete S1 table and the actual first-round input',
            len(s1_diagrams) == 1 and s1_diagrams[0]['table'] == cx.SBOXES[0]
            and s1_diagrams[0]['value'] == 0b011000
            and cx.SBOXES[0][int(xor_bits[0] + xor_bits[5], 2)][int(xor_bits[1:5], 2)] == 5)

    expected_lookups = []
    sbox_outputs = []
    for index in range(8):
        expanded_group = expanded_bits[6*index:6*index+6]
        key_group = key_bits[6*index:6*index+6]
        mixed_group = ''.join(str(int(a) ^ int(b)) for a, b in zip(expanded_group, key_group))
        outer = mixed_group[0] + mixed_group[-1]
        inner = mixed_group[1:5]
        row, column = int(outer, 2), int(inner, 2)
        output = cx.SBOXES[index][row][column]
        expected_lookups.append(['S'+str(index+1), expanded_group, key_group, mixed_group,
                                 f'{outer} → {row}', f'{inner} → {column}', f'{output:04b}'])
        sbox_outputs.append(f'{output:04b}')
    checked('Appendix eight S-box calculations independently verify expansion, key XOR, indices, and outputs',
            one_table(dc.DES_SBOX_APPENDIX, ['Box', 'E(R₀)', 'K₁', 'XOR',
                                       'Outer bits → row', 'Inner bits → column', 'Output'])
            == expected_lookups
            and int(''.join(sbox_outputs), 2) == first['sbox_output'] == 0x5C82B597)

    p_positions = [16, 7, 20, 21]
    p_bits = select_bits(first['sbox_output'], p_positions, 32)
    p_first_byte = select_bits(first['sbox_output'], [16, 7, 20, 21, 29, 12, 28, 17], 32)
    checked('Worked P first nibble independently selects S-box output bits 16,7,20,21',
            p_bits == '0010' and p_first_byte == '00100011'
            and normalized_rows(one_table(des_slide('Permute the 32 output bits'),
                ['Output position'] + [str(i) for i in range(1, 5)])) ==
            [['Read input bit'] + list(map(str, p_positions)),
             ['Bit copied'] + list(p_bits)]
            and f'{first["f"]:032b}'[:4] == p_bits
            and (first['f'] >> 24) == int(p_first_byte, 2) == 0x23)
    all_p_bits = select_bits(first['sbox_output'], cx.P, 32)
    r1_bits = ''.join(str(int(a) ^ int(b)) for a, b in
                      zip(f'{cx.DES_TRACE["l0"]:032b}', all_p_bits))
    checked('Worked F result and first-round halves independently agree after XOR',
            int(all_p_bits, 2) == first['f'] == 0x234AA9BB
            and first['l'] == cx.DES_TRACE['r0'] == 0xF0AAF0AA
            and int(r1_bits, 2) == first['r'] == 0xEF4A6544
            and all(f'{value:08X}' in code_text(dc.DES_SLIDES)
                    for value in [first['f'], first['l'], first['r']]))
    printed_keys = [row for table in tables(dc.DES_APPENDIX, ['i', 'sᵢ', 'Kᵢ (hex)'])
                    for row in table[2]]
    checked('All sixteen printed DES subkeys preserve their shifts and 48-bit widths',
            printed_keys == [[str(row['round']), str(row['shift']), f'{row["key"]:012X}']
                             for row in cx.DES_KEY_TRACE['rounds']])
    printed_states = [row for table in tables(dc.DES_APPENDIX, ['i', 'Lᵢ (hex)', 'Rᵢ (hex)'])
                      for row in table[2]]
    checked('All sixteen printed DES round states match the computed encryption',
            printed_states == [[str(row['round']), f'{row["l"]:08X}', f'{row["r"]:08X}']
                               for row in cx.DES_TRACE['rounds']])
    bit_diagrams = [block[2] for item in dc.DES_APPENDIX for block in walk_blocks(item['blocks'])
                    if block[:2] == ('diagram', 'bit_table')]
    expected_tables = [cx.IP, cx.FP, cx.E, cx.P, cx.PC1, cx.PC2] + cx.SBOXES
    checked('Complete printed DES permutation, selection, and eight S-box tables match FIPS data',
            len(bit_diagrams) == len(expected_tables)
            and [item['table'] for item in bit_diagrams] == expected_tables
            and all(len(item['table']) * (len(item['table'][0]) if isinstance(item['table'][0], list) else 1)
                    == item['rows'] * item['cols'] for item in bit_diagrams))
    codes = code_text(dc.DES_SLIDES)
    critical_values = [(cx.DES_PLAINTEXT, 16), (cx.DES_KEY, 16), (cx.DES_CIPHERTEXT, 16),
                       (cx.DES_TRACE['post_ip'], 16), (cx.DES_TRACE['preoutput'], 16),
                       (first['expanded'], 12), (first['key'], 12), (first['xored'], 12),
                       (first['sbox_output'], 8), (first['f'], 8),
                       (cx.DES_KEY_TRACE['c0'], 7), (cx.DES_KEY_TRACE['d0'], 7)]
    checked('Main DES worked examples display the verified values with fixed-width hexadecimal',
            all(f'{value:0{digits}X}' in codes for value, digits in critical_values))


def source_glyph_checks(slides):
    """Check source text before a PDF font's .notdef glyph can hide a problem."""
    from diagrams import draw as draw_diagram
    missing = []
    seen = {font: set() for font in FONT_CMAPS}

    def scan(text, font, location, markup=False):
        if markup:
            text = ''.join(PlainText(str(text)).parts)
        else:
            text = str(text)
        seen[font].update(text)
        absent = unsupported(text, font)
        if absent:
            missing.append(dict(location=location, font=font,
                                characters=[f'{ch} (U+{ord(ch):04X})' for ch in absent]))

    class DiagramCanvas:
        """Record the diagram renderer's actual strings and selected fonts."""
        font = 'Sans'

        def setFont(self, name, size):
            self.font = name

        def drawString(self, x, y, text):
            scan(text, self.font, location + ' / diagram')

        drawCentredString = drawString
        drawRightString = drawString

        def __getattr__(self, name):
            return lambda *args, **kwargs: None

    for number, item in enumerate(slides, 1):
        location = f'Slide {number}'
        scan(item['title'], 'Bold', location + ' / title')
        scan(item['section'], 'Bold', location + ' / section')
        for key in ['sub', 'take', 'source']:
            scan(item.get(key, ''), 'Sans', location + ' / ' + key, markup=key == 'sub')
        for block in walk_blocks(item['blocks']):
            kind = block[0]
            if kind in ['p', 'b']:
                scan(block[1], 'Sans', location + ' / paragraph', markup=True)
            elif kind == 'code':
                scan(block[1], 'Bold', location + ' / code label')
                scan(block[2], 'Mono', location + ' / code body')
            elif kind == 'table':
                for cell in block[1]:
                    scan(cell, 'Bold', location + ' / table header')
                for row in block[2]:
                    for cell in row:
                        scan(cell, 'Sans', location + ' / table body')
            elif kind == 'diagram':
                draw_diagram(DiagramCanvas(), block[1], block[2], 0, 0, 856)
            # math blocks are rendered using their separate TeX fonts.
    if missing:
        raise AssertionError('Missing source-font glyphs: ' + json.dumps(missing, ensure_ascii=False))
    checked('Every visible slide string and vector diagram label has glyphs in its selected font', True)
    return {font: dict(unique_characters=len(characters), missing=[])
            for font, characters in seen.items()}


def validate_pdf(path, expected_pages=None):
    doc = fitz.open(path)
    checked(path.name + ' page count',
            len(doc) == expected_pages if expected_pages is not None else len(doc) > 0)
    problems, fonts, missing_glyphs = [], {}, []
    # Imported TeX glyph boxes can exceed their baseline by subpoint rounding.
    # The tolerance is far below a visible character or meaningful layout margin.
    tolerance = 0.75
    for number, page in enumerate(doc, 1):
        text = page.get_text()
        if not text.strip():
            problems.append([number, 'blank page'])
        if '\ufffd' in text or '\x00' in text:
            problems.append([number, 'replacement or null character'])
        allowed = page.rect + (-tolerance, -tolerance, tolerance, tolerance)
        for block in page.get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    if not allowed.contains(fitz.Rect(span['bbox'])):
                        problems.append([number, 'out-of-page text', span['text'], span['bbox']])
                    family = span['font'].split('+')[-1]
                    role = ('Mono' if family.startswith('DejaVuSansMono') else
                            'Bold' if family.startswith('DejaVuSans-Bold') else
                            'Italic' if family.startswith('DejaVuSans-Oblique') else
                            'Sans' if family.startswith('DejaVuSans') else None)
                    if role and unsupported(span['text'], role):
                        missing_glyphs.append([number, span['font'], unsupported(span['text'], role)])
        for font in page.get_fonts(full=True):
            xref, _, _, name, *_ = font
            fonts[f'{xref}:{name}'] = bool(doc.extract_font(xref)[3])
        # Render every page, including vector equations and nested form objects.
        page.get_pixmap(matrix=fitz.Matrix(0.35, 0.35), alpha=False)
    checked(path.name + ' has no invalid characters or out-of-page text', not problems)
    checked(path.name + ' embeds every referenced font', bool(fonts) and all(fonts.values()))
    checked(path.name + ' text uses glyphs covered by its DejaVu fonts', not missing_glyphs)
    result = dict(pages=len(doc), bytes=path.stat().st_size,
                  sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  rendered_pages=len(doc), all_fonts_embedded=all(fonts.values()),
                  fonts=fonts, text_bounds_tolerance_pt=tolerance, problems=problems,
                  missing_glyphs=missing_glyphs)
    doc.close()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content-only', action='store_true', help='Skip PDFs and do not write a report.')
    args = parser.parse_args()
    import des_content
    from slide_content import slides, MAIN_COUNT, SESSION_PLAN

    numerical_checks()
    des_printed_checks(des_content)
    assembled_checks(slides, MAIN_COUNT, SESSION_PLAN, des_content)
    glyph_coverage = source_glyph_checks(slides)
    if args.content_only:
        print(f'Passed {len(CHECKS)} numerical, printed-data, and schedule checks; PDFs not checked.')
        return
    layout_path = ROOT / 'layout_checks.json'
    if layout_path.exists():
        checked('Lecture renderer reports no content, font-size, or footer overflows',
                not json.loads(layout_path.read_text())['issues'])
    pdfs = {name: validate_pdf(ROOT / name, pages) for name, pages in
            [('Lecture02_OTP_and_Block_Ciphers.pdf', len(slides)),
             ('Lecture02_Instructor_Guide.pdf', None)]}
    report = dict(edition='Lecture 02: one-time pads and block ciphers',
                  checks_passed=len(CHECKS), checks=CHECKS,
                  teaching_pages=MAIN_COUNT, appendix_pages=len(slides)-MAIN_COUNT,
                  session_minutes=sum(row['minutes'] for row in SESSION_PLAN),
                  teaching_minutes=sum(row['minutes'] for row in SESSION_PLAN if row['kind'] == 'teaching'),
                  break_minutes=sum(row['minutes'] for row in SESSION_PLAN if row['kind'] == 'break'),
                  source_glyph_coverage=glyph_coverage,
                  pdfs=pdfs,
                  visual_review='Automated rendering of every page; manual visual review is separate.')
    (ROOT / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'Passed {len(CHECKS)} checks; rendered {sum(p["rendered_pages"] for p in pdfs.values())} PDF pages. All fonts embedded.')


if __name__ == '__main__':
    main()
