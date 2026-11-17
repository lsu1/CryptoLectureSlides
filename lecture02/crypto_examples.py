"""Reproducible teaching data for OTP, information theory, and block ciphers.

DES uses the published FIPS 46-3 tables, with table positions numbered from 1
at the most significant input bit. The tiny SPN is an explicitly specified
teaching model, not a cipher recommended for protecting data. DES is historical
and insecure for contemporary encryption. No third-party crypto package is
required to reproduce the printed examples.
"""
from fractions import Fraction
from math import factorial, log2

# FIPS 46-3 permutations: each output bit selects the numbered input bit.
IP = [58,50,42,34,26,18,10,2,60,52,44,36,28,20,12,4,
      62,54,46,38,30,22,14,6,64,56,48,40,32,24,16,8,
      57,49,41,33,25,17,9,1,59,51,43,35,27,19,11,3,
      61,53,45,37,29,21,13,5,63,55,47,39,31,23,15,7]
FP = [40,8,48,16,56,24,64,32,39,7,47,15,55,23,63,31,
      38,6,46,14,54,22,62,30,37,5,45,13,53,21,61,29,
      36,4,44,12,52,20,60,28,35,3,43,11,51,19,59,27,
      34,2,42,10,50,18,58,26,33,1,41,9,49,17,57,25]
E = [32,1,2,3,4,5,4,5,6,7,8,9,8,9,10,11,12,13,
     12,13,14,15,16,17,16,17,18,19,20,21,20,21,22,23,24,25,
     24,25,26,27,28,29,28,29,30,31,32,1]
P = [16,7,20,21,29,12,28,17,1,15,23,26,5,18,31,10,
     2,8,24,14,32,27,3,9,19,13,30,6,22,11,4,25]
PC1 = [57,49,41,33,25,17,9,1,58,50,42,34,26,18,
       10,2,59,51,43,35,27,19,11,3,60,52,44,36,
       63,55,47,39,31,23,15,7,62,54,46,38,30,22,
       14,6,61,53,45,37,29,21,13,5,28,20,12,4]
PC2 = [14,17,11,24,1,5,3,28,15,6,21,10,
       23,19,12,4,26,8,16,7,27,20,13,2,
       41,52,31,37,47,55,30,40,51,45,33,48,
       44,49,39,56,34,53,46,42,50,36,29,32]
SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]
SBOXES = [
    [[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7],
     [0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8],
     [4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0],
     [15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13]],
    [[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10],
     [3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5],
     [0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15],
     [13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9]],
    [[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8],
     [13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1],
     [13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7],
     [1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12]],
    [[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15],
     [13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9],
     [10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4],
     [3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14]],
    [[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9],
     [14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6],
     [4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14],
     [11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3]],
    [[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11],
     [10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8],
     [9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6],
     [4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13]],
    [[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1],
     [13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6],
     [1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2],
     [6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12]],
    [[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7],
     [1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2],
     [7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8],
     [2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]]
]
DES_IP, DES_FP, DES_E, DES_P = IP, FP, E, P
DES_PC1, DES_PC2 = PC1, PC2
MASK28, MASK32 = (1 << 28)-1, (1 << 32)-1


def permute(value, table, input_bits):
    """Select MSB-first input positions listed in table, yielding an integer."""
    if not 0 <= value < (1 << input_bits):
        raise ValueError('Input does not fit its stated bit width')
    out = 0
    for position in table:
        if not 1 <= position <= input_bits:
            raise ValueError('Table position outside input width')
        out = (out << 1) | ((value >> (input_bits-position)) & 1)
    return out


def rotate28(value, count):
    return ((value << count) | (value >> (28-count))) & MASK28


def key_schedule_trace(key64):
    """Return PC1 and every rotated 28-bit half / 48-bit round key."""
    chosen = permute(key64, PC1, 64)
    c, d = chosen >> 28, chosen & MASK28
    result = dict(pc1=chosen, c0=c, d0=d, rounds=[])
    for number, count in enumerate(SHIFTS, 1):
        c, d = rotate28(c, count), rotate28(d, count)
        result['rounds'].append(dict(round=number, shift=count, c=c, d=d,
                                     key=permute((c << 28) | d, PC2, 56)))
    return result


def des_subkeys(key64):
    """Return the sixteen 48-bit DES round keys in encryption order."""
    return [row['key'] for row in key_schedule_trace(key64)['rounds']]


def des_sbox(box_number, six_bits):
    """Apply S1..S8 (box_number is 1-based) to a six-bit integer."""
    if not (1 <= box_number <= 8 and 0 <= six_bits < 64):
        raise ValueError('Expected S-box number 1..8 and six-bit input')
    row = ((six_bits >> 4) & 2) | (six_bits & 1)
    column = (six_bits >> 1) & 15
    return SBOXES[box_number-1][row][column]


def des_f(right, round_key, trace=False):
    expanded = permute(right, E, 32)
    xored = expanded ^ round_key
    substituted = 0
    boxes = []
    for index in range(8):
        chunk = (xored >> (42-6*index)) & 63
        value = des_sbox(index+1, chunk)
        substituted = (substituted << 4) | value
        boxes.append(dict(box=index+1, input=chunk,
                          row=((chunk >> 4) & 2) | (chunk & 1),
                          column=(chunk >> 1) & 15, output=value))
    output = permute(substituted, P, 32)
    if trace:
        return output, dict(expanded=expanded, xored=xored,
                            sbox_output=substituted, boxes=boxes, f=output)
    return output


def des_encrypt(block, key64, decrypt=False, trace=False):
    """Encrypt/decrypt a 64-bit DES block; optionally return (result, trace).

    Trace stores input/post_ip/l0/r0, sixteen rounds, preoutput (R16||L16),
    and output. Round keys are reversed for decryption. Parity bits are ignored
    by PC1, as the standard specifies; has_odd_parity checks their representation.
    """
    initial = permute(block, IP, 64)
    left, right = initial >> 32, initial & MASK32
    subkeys = des_subkeys(key64)
    if decrypt:
        subkeys = subkeys[::-1]
    result = dict(input=block, key=key64, decrypt=decrypt, post_ip=initial,
                  l0=left, r0=right, rounds=[])
    for number, subkey in enumerate(subkeys, 1):
        fvalue, detail = des_f(right, subkey, trace=True)
        row = dict(round=number, key=subkey, l_in=left, r_in=right, **detail)
        left, right = right, left ^ fvalue
        row.update(l=left, r=right)
        result['rounds'].append(row)
    preoutput = (right << 32) | left
    output = permute(preoutput, FP, 64)
    result.update(preoutput=preoutput, output=output)
    return (output, result) if trace else output


def double_des_encrypt(block, key1, key2):
    return des_encrypt(des_encrypt(block,key1),key2)


def triple_des_encrypt(block, key1, key2, key3, decrypt=False):
    """Historical EDE composition; permits key3=key1 for two-key TDEA."""
    if decrypt:
        return des_encrypt(des_encrypt(des_encrypt(block,key3,True),key2),key1,True)
    return des_encrypt(des_encrypt(des_encrypt(block,key1),key2,True),key3)


def has_odd_parity(key64):
    return all(((key64 >> shift) & 255).bit_count() % 2 == 1
               for shift in range(0, 64, 8))


DES_PLAINTEXT = 0x0123456789ABCDEF
DES_KEY = 0x133457799BBCDFF1
DES_CIPHERTEXT, DES_TRACE = des_encrypt(DES_PLAINTEXT, DES_KEY, trace=True)
DES_KEY_TRACE = key_schedule_trace(DES_KEY)
DES_TRACE.update(pc1=DES_KEY_TRACE['pc1'], c0=DES_KEY_TRACE['c0'], d0=DES_KEY_TRACE['d0'])
DES_FLIPPED_PLAINTEXT = DES_PLAINTEXT ^ 1
DES_FLIPPED_CIPHERTEXT, DES_FLIPPED_TRACE = des_encrypt(DES_FLIPPED_PLAINTEXT, DES_KEY, trace=True)
DES_AVALANCHE = (DES_CIPHERTEXT ^ DES_FLIPPED_CIPHERTEXT).bit_count()
DES_ROUND_DIFFERENCES = [(a['l'] ^ b['l']).bit_count() + (a['r'] ^ b['r']).bit_count()
                         for a,b in zip(DES_TRACE['rounds'],DES_FLIPPED_TRACE['rounds'])]

# Explicit toy SPN: three substitution rounds, two permutations, final whitening.
# All four positions use this SAME bijection; hexadecimal entries give S(0)..S(F).
TOY_SBOX = [0xE,0x4,0xD,0x1,0x2,0xF,0xB,0x8,
            0x3,0xA,0x6,0xC,0x5,0x9,0x0,0x7]
TOY_INV_SBOX = [TOY_SBOX.index(value) for value in range(16)]
TOY_PERM = [1,5,9,13,2,6,10,14,3,7,11,15,4,8,12,16]
TOY_INV_PERM = [TOY_PERM.index(position)+1 for position in range(1,17)]
TOY_KEYS = [0x3A94,0xA94D,0x94D6,0x4D63]
TOY_PLAINTEXT = 0x1234


def toy_substitute(value, inverse=False):
    box = TOY_INV_SBOX if inverse else TOY_SBOX
    return sum(box[(value >> shift) & 15] << shift for shift in [12,8,4,0])


def toy_encrypt(block, round_keys=None, trace=False):
    """Toy: XOR K0,S,P; XOR K1,S,P; XOR K2,S; XOR K3.

    A deliberately chosen list of four 16-bit round keys is supplied directly.
    They are illustrative values, not a proposed secure key schedule.
    """
    keys = TOY_KEYS if round_keys is None else list(round_keys)
    if len(keys) != 4 or not all(0 <= x < 65536 for x in [block]+keys):
        raise ValueError('Toy needs one 16-bit block and four 16-bit round keys')
    state = block
    result = dict(input=block, keys=keys, rounds=[])
    for index in range(3):
        mixed = state ^ keys[index]
        substituted = toy_substitute(mixed)
        permuted = permute(substituted, TOY_PERM, 16) if index < 2 else None
        state = permuted if permuted is not None else substituted
        result['rounds'].append(dict(round=index+1, key=keys[index], mixed=mixed,
                                     substituted=substituted, permuted=permuted, state=state))
    output = state ^ keys[3]
    result.update(whitening_key=keys[3],output=output)
    return (output,result) if trace else output


def toy_decrypt(block, round_keys=None):
    keys = TOY_KEYS if round_keys is None else list(round_keys)
    if len(keys) != 4 or not all(0 <= x < 65536 for x in [block]+keys):
        raise ValueError('Toy needs one 16-bit block and four 16-bit round keys')
    state = block ^ keys[3]
    for index in [2,1,0]:
        if index < 2:
            state = permute(state, TOY_INV_PERM, 16)
        state = toy_substitute(state,inverse=True) ^ keys[index]
    return state


TOY_CIPHERTEXT, TOY_TRACE = toy_encrypt(TOY_PLAINTEXT,trace=True)
TOY_FLIP_MASK = 0x0008  # one explicitly selected input bit; an example, not a security test
TOY_FLIPPED_PLAINTEXT = TOY_PLAINTEXT ^ TOY_FLIP_MASK
TOY_FLIPPED_CIPHERTEXT, TOY_FLIPPED_TRACE = toy_encrypt(TOY_FLIPPED_PLAINTEXT,trace=True)
TOY_AVALANCHE = (TOY_CIPHERTEXT ^ TOY_FLIPPED_CIPHERTEXT).bit_count()
TOY_ROUND_DIFFERENCES = [(a['state'] ^ b['state']).bit_count()
                         for a,b in zip(TOY_TRACE['rounds'],TOY_FLIPPED_TRACE['rounds'])]

# One-time-pad examples retained from the supplied reference.
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
OTP_PLAINTEXT = 'NANYANG'
OTP_KEY = 'XRTRPLK'

def otp_letters(message,key,decrypt=False):
    if len(message) != len(key):
        raise ValueError('OTP message and key lengths must match')
    direction = -1 if decrypt else 1
    return ''.join(ALPHABET[(ALPHABET.index(p.upper()) + direction*ALPHABET.index(k.upper())) % 26]
                   for p,k in zip(message,key))


def xor_bits(a,b):
    if len(a) != len(b) or set(a+b) - {'0','1'}:
        raise ValueError('Expected equally long binary strings')
    return ''.join(str(int(x)^int(y)) for x,y in zip(a,b))


OTP_CIPHERTEXT = otp_letters(OTP_PLAINTEXT,OTP_KEY)
OTP_LETTER_ROWS = [[p,ALPHABET.index(p),k,ALPHABET.index(k),
                    (ALPHABET.index(p)+ALPHABET.index(k))%26,c]
                   for p,k,c in zip(OTP_PLAINTEXT,OTP_KEY,OTP_CIPHERTEXT)]
OTP_BITS_PLAINTEXT = '1010011000'
OTP_BITS_KEY = '0110101110'
OTP_BITS_CIPHERTEXT = xor_bits(OTP_BITS_PLAINTEXT,OTP_BITS_KEY)
REUSE_P1, REUSE_P2, REUSE_KEY = '10110010','01101100','11001010'
REUSE_C1, REUSE_C2 = xor_bits(REUSE_P1,REUSE_KEY),xor_bits(REUSE_P2,REUSE_KEY)
REUSE_PLAINTEXT_XOR,REUSE_CIPHERTEXT_XOR = xor_bits(REUSE_P1,REUSE_P2),xor_bits(REUSE_C1,REUSE_C2)

# Probability / information-theory calculations, with exact dice fractions.
DICE_OUTCOMES = [(a,b) for a in range(1,7) for b in range(1,7)]
DICE_SUM4 = [(a,b) for a,b in DICE_OUTCOMES if a+b==4]
DICE_DOUBLES = [(a,b) for a,b in DICE_OUTCOMES if a==b]
DICE_SUM4_AND_DOUBLE = [(a,b) for a,b in DICE_SUM4 if a==b]
DICE_P_SUM4 = Fraction(len(DICE_SUM4),36)
DICE_P_DOUBLE = Fraction(len(DICE_DOUBLES),36)
DICE_P_DOUBLE_GIVEN_SUM4 = Fraction(len(DICE_SUM4_AND_DOUBLE),len(DICE_SUM4))
DICE_P_SUM4_GIVEN_DOUBLE = Fraction(len(DICE_SUM4_AND_DOUBLE),len(DICE_DOUBLES))


def entropy(probabilities):
    values = [float(p) for p in probabilities]
    if any(p < 0 for p in values) or abs(sum(values)-1) > 1e-9:
        raise ValueError('Entropy requires a normalized probability distribution')
    return -sum(p*log2(p) for p in values if p > 0)


ENTROPY_FAIR_COIN = entropy([0.5,0.5])
ENTROPY_BIASED_COIN = entropy([0.7,0.3])
ENTROPY_CERTAIN_COIN = entropy([1,0])
ENGLISH_ALPHABET_BITS = log2(26)
ENGLISH_RATE_ILLUSTRATIVE = 1.25
ENGLISH_REDUNDANCY = 1-ENGLISH_RATE_ILLUSTRATIVE/ENGLISH_ALPHABET_BITS
ENGLISH_REDUNDANCY_BITS = ENGLISH_ALPHABET_BITS-ENGLISH_RATE_ILLUSTRATIVE
SUBSTITUTION_KEY_ENTROPY = log2(factorial(26))
SUBSTITUTION_UNICITY_DISTANCE = SUBSTITUTION_KEY_ENTROPY/ENGLISH_REDUNDANCY_BITS


if __name__ == '__main__':
    assert DES_CIPHERTEXT == 0x85E813540F0AB405
    assert des_encrypt(DES_CIPHERTEXT,DES_KEY,decrypt=True) == DES_PLAINTEXT
    assert DES_TRACE['l0'] == 0xCC00CCFF and DES_TRACE['r0'] == 0xF0AAF0AA
    first = DES_TRACE['rounds'][0]
    assert first['key'] == 0x1B02EFFC7072 and first['f'] == 0x234AA9BB
    assert first['l'] == 0xF0AAF0AA and first['r'] == 0xEF4A6544
    assert has_odd_parity(DES_KEY)
    assert des_sbox(5,0b011011) == 0b1001
    assert toy_decrypt(TOY_CIPHERTEXT) == TOY_PLAINTEXT
    assert all(toy_decrypt(toy_encrypt(p)) == p for p in range(65536))
    assert OTP_CIPHERTEXT == 'KRGPPYQ'
    assert otp_letters(OTP_CIPHERTEXT,OTP_KEY,True) == OTP_PLAINTEXT
    assert xor_bits(OTP_BITS_CIPHERTEXT,OTP_BITS_KEY) == OTP_BITS_PLAINTEXT
    assert REUSE_PLAINTEXT_XOR == REUSE_CIPHERTEXT_XOR
    print(f'DES: {DES_PLAINTEXT:016X} -> {DES_CIPHERTEXT:016X}; first round verified')
    print(f'Toy: {TOY_PLAINTEXT:04X} -> {TOY_CIPHERTEXT:04X}; all 65536 blocks round-trip')
    print('OTP:',OTP_CIPHERTEXT,OTP_BITS_CIPHERTEXT)
    print('Avalanche example: DES',DES_AVALANCHE,'/64; toy',TOY_AVALANCHE,'/16')
