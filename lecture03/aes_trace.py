"""Generate AES teaching examples using the byte order in NIST FIPS 197.

A serialized state stores column 0 from top to bottom, then column 1 and so on.
The FIPS 197 (2001) Appendix C examples supply the independent test values.
"""

from functools import reduce
from operator import xor


def xtime(value):
    """Multiply a field element by x modulo x^8 + x^4 + x^3 + x + 1."""
    shifted = value << 1
    if shifted & 0x100:
        shifted ^= 0x11B
    return shifted


def gf_product(left, right):
    """Multiply two bytes as polynomials by accumulating shifted copies."""
    result = 0
    while right:
        if right & 1:
            result ^= left
        left = xtime(left)
        right >>= 1
    return result


def gf_inverse(value):
    """Return the multiplicative inverse of a nonzero field element."""
    if value == 0:
        raise ValueError('Zero has no multiplicative inverse')
    # The nonzero elements form a group of order 255, so a^(-1) = a^254.
    power = 254
    result = 1
    while power:
        if power & 1:
            result = gf_product(result, value)
        value = gf_product(value, value)
        power >>= 1
    return result


def rotl_byte(value, count):
    return ((value << count) | (value >> (8 - count))) & 0xFF


def make_sbox_byte(value):
    # FIPS 197 assigns 00 to 00 in the inversion step only.
    inverse = gf_inverse(value) if value else 0
    affine = inverse ^ 0x63
    for count in range(1, 5):
        affine ^= rotl_byte(inverse, count)
    return affine


SBOX = bytes(make_sbox_byte(value) for value in range(256))
INV_SBOX = bytes(SBOX.index(value) for value in range(256))


def xor_bytes(left, right):
    return bytes(a ^ b for a, b in zip(left, right, strict=True))


def sub_bytes(state, table=SBOX):
    return bytes(table[value] for value in state)


def shift_rows(state, inverse=False):
    result = bytearray(16)
    for col in range(4):
        for row in range(4):
            source_col = (col - row if inverse else col + row) % 4
            result[4 * col + row] = state[4 * source_col + row]
    return bytes(result)


MIX = ((2, 3, 1, 1), (1, 2, 3, 1), (1, 1, 2, 3), (3, 1, 1, 2))
INV_MIX = ((14, 11, 13, 9), (9, 14, 11, 13), (13, 9, 14, 11), (11, 13, 9, 14))


def mix_columns(state, matrix=MIX):
    result = bytearray()
    for offset in range(0, 16, 4):
        column = state[offset:offset + 4]
        for row in matrix:
            terms = (gf_product(coefficient, value) for coefficient, value in zip(row, column))
            result.append(reduce(xor, terms))
    return bytes(result)


def expand_key(key):
    """Return the full sequence of 16-byte round keys in word order."""
    if len(key) not in (16, 24, 32):
        raise ValueError('An AES key has 16, 24 or 32 bytes')
    words = [key[i:i + 4] for i in range(0, len(key), 4)]
    key_words = len(words)
    rounds = key_words + 6
    round_constant = 1
    for i in range(key_words, 4 * (rounds + 1)):
        temp = words[i - 1]
        if i % key_words == 0:
            temp = sub_bytes(temp[1:] + temp[:1])
            temp = xor_bytes(temp, bytes((round_constant, 0, 0, 0)))
            round_constant = xtime(round_constant)
        elif key_words == 8 and i % key_words == 4:
            temp = sub_bytes(temp)
        words.append(xor_bytes(words[i - key_words], temp))
    return tuple(b''.join(words[i:i + 4]) for i in range(0, len(words), 4))


def encrypt_trace(plaintext, key):
    """Return one dictionary of uppercase hex checkpoints per round."""
    if len(plaintext) != 16:
        raise ValueError('An AES block has 16 bytes')
    round_keys = expand_key(key)
    state = xor_bytes(plaintext, round_keys[0])
    records = [dict(start=plaintext, round_key=round_keys[0], end=state)]
    for index, round_key in enumerate(round_keys[1:], start=1):
        record = dict(start=state, round_key=round_key)
        state = record['sub_bytes'] = sub_bytes(state)
        state = record['shift_rows'] = shift_rows(state)
        if index < len(round_keys) - 1:
            state = record['mix_columns'] = mix_columns(state)
        state = record['end'] = xor_bytes(state, round_key)
        records.append(record)
    return tuple({name: value.hex().upper() for name, value in row.items()} for row in records)


def decrypt_block(ciphertext, key):
    """Apply the inverse cipher with the original round keys in reverse order."""
    if len(ciphertext) != 16:
        raise ValueError('An AES block has 16 bytes')
    round_keys = expand_key(key)
    state = xor_bytes(ciphertext, round_keys[-1])
    for round_key in reversed(round_keys[1:-1]):
        state = sub_bytes(shift_rows(state, inverse=True), INV_SBOX)
        state = mix_columns(xor_bytes(state, round_key), INV_MIX)
    state = sub_bytes(shift_rows(state, inverse=True), INV_SBOX)
    return xor_bytes(state, round_keys[0])


PLAINTEXT = '00112233445566778899AABBCCDDEEFF'
KEY = '000102030405060708090A0B0C0D0E0F'
ROUND_TRACE = encrypt_trace(bytes.fromhex(PLAINTEXT), bytes.fromhex(KEY))
ROUND_STATES = tuple(row['end'] for row in ROUND_TRACE)
ROUND_KEYS = tuple(row['round_key'] for row in ROUND_TRACE)
CIPHERTEXT = ROUND_STATES[-1]


def verify_examples():
    assert gf_product(0x57, 0x83) == 0xC1
    assert gf_inverse(0x05) == 0x52
    assert all(gf_product(i, gf_inverse(i)) == 1 for i in range(1, 256))
    assert [SBOX[i] for i in (0x00, 0x05, 0x53)] == [0x63, 0x6B, 0xED]
    assert all(INV_SBOX[SBOX[i]] == i for i in range(256))
    assert ROUND_KEYS[1] == 'D6AA74FDD2AF72FADAA678F1D6AB76FE'
    assert ROUND_KEYS[10] == '13111D7FE3944A17F307A78B4D2B30C5'
    assert ROUND_TRACE[1]['sub_bytes'] == '63CAB7040953D051CD60E0E7BA70E18C'
    assert ROUND_TRACE[1]['shift_rows'] == '6353E08C0960E104CD70B751BACAD0E7'
    assert ROUND_TRACE[1]['mix_columns'] == '5F72641557F5BC92F7BE3B291DB9F91A'
    assert ROUND_STATES == (
        '00102030405060708090A0B0C0D0E0F0', '89D810E8855ACE682D1843D8CB128FE4',
        '4915598F55E5D7A0DACA94FA1F0A63F7', 'FA636A2825B339C940668A3157244D17',
        '247240236966B3FA6ED2753288425B6C', 'C81677BC9B7AC93B25027992B0261996',
        'C62FE109F75EEDC3CC79395D84F9CF5D', 'D1876C0F79C4300AB45594ADD66FF41F',
        'FDE3BAD205E5D0D73547964EF1FE37F1', 'BD6E7C3DF2B5779E0B61216E8B10B689',
        '69C4E0D86A7B0430D8CDB78070B4C55A',
    )
    assert 'mix_columns' not in ROUND_TRACE[-1]
    plaintext = bytes.fromhex(PLAINTEXT)
    for key_length, expected in (
        (16, '69C4E0D86A7B0430D8CDB78070B4C55A'),
        (24, 'DDA97CA4864CDFE06EAF70A0EC0D7191'),
        (32, '8EA2B7CA516745BFEAFC49904B496089'),
    ):
        key = bytes(range(key_length))
        assert encrypt_trace(plaintext, key)[-1]['end'] == expected
        assert decrypt_block(bytes.fromhex(expected), key) == plaintext


if __name__ == '__main__':
    verify_examples()
    print('Verified the field examples, AES-128 round trace, and all three AES known answers.')
