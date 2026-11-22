"""The overview and the labels used to locate a calculation within AES."""

from deck_schema import P, slide

STAGES = ('Prepare', 'Initial XOR', 'Full rounds', 'Final round')
OPERATIONS = ('SubBytes', 'ShiftRows', 'MixColumns', 'AddRoundKey')

MAP_TITLE = 'AES encryption in four steps'
ROUND_TITLE = 'What happens inside one AES round?'

# The order of the links matches the stages/operations shown on the overview.
STAGE_EXAMPLES = (
    'Place 16 input bytes into the state',
    'First, XOR the plaintext with the key',
    'SubBytes replaces one byte at a time',
    'Finish round 10 with the last key',
)
OPERATION_EXAMPLES = (
    'SubBytes replaces one byte at a time',
    'ShiftRows rotates each row by its index',
    'Work the first output byte by hand',
    'Finish round 1 with its round key',
)

overview = [
    slide(MAP_TITLE, [
        P('Start with one 16-byte plaintext block and a secret key. The working grid of 16 bytes is called the <b>state</b>. Let <i>r</i> be the number of rounds.'),
        ('stage_map', [
            'Load the plaintext into the state. Expand the secret key into round keys K₀ through Kᵣ.',
            'Before round 1, XOR the state with K₀. This operation is called AddRoundKey.',
            'For rounds 1 through r − 1, run all four operations shown on the next slide. Each round uses its own round key.',
            'In round r, run three operations. Read the resulting state down each column to obtain the 16 ciphertext bytes.',
        ]),
    ], section='AES ALGORITHM', minutes=3,
        notes='Walk down the four numbered steps before showing any hex. Expansion depends only on the key and can be performed in advance. Ask which step repeats nine times in AES-128. Select a numbered row to jump to its example.',
        take='For AES-128, r = 10. The initial XOR, nine full rounds and one final round use eleven round keys.'),
    slide(ROUND_TITLE, [
        ('operation_map', [
            'Replace each byte using the same substitution table.',
            'Rotate each row left by its row number.',
            'Combine the four bytes within each column.',
            'XOR each byte with the matching byte of this round’s key.',
        ]),
        ('round_paths',),
        P('The strip above each worked example shows the numbered step and the operation being calculated. Select the strip to revisit the overview.'),
    ], section='AES ALGORITHM', minutes=3,
        notes='Trace the lettered operations left to right. The output of each operation becomes the next input. Ask which operation is absent in round 10 and what happens immediately after ShiftRows. Select a lettered card to jump to a worked calculation.'),
]

# First coordinate: numbered forward phase to highlight. Second: the activity
# students are seeing. Neutral markers explain mathematics or a whole-cipher check.
def location(focus):
    phase, caption = {
        'state': (1, 'Load the state  ·  Read columns from top to bottom'),
        'keys': (1, 'Key expansion  ·  Derive round keys from the master key'),
        'initial': (2, 'Before round 1  ·  AddRoundKey with K₀'),
        'sub': (3, 'Round 1  ·  A  SubBytes'),
        'shift': (3, 'Round 1  ·  B  ShiftRows'),
        'mix': (3, 'Round 1  ·  C  MixColumns'),
        'xor': (3, 'Round 1  ·  D  AddRoundKey'),
        'round_summary': (3, 'Round 1  ·  A → B → C → D'),
        'final': (4, 'Round 10  ·  A SubBytes → B ShiftRows → D AddRoundKey'),
        'inv_final': (4, 'Undo round 10  ·  D → B → A'),
        'inv_round': (3, 'Undo a full round  ·  D → C → B → A'),
        'inv_mix': (3, 'Undo round 1  ·  C  InvMixColumns'),
        'inv_initial': (0, 'Undo round 1, then the initial XOR with K₀'),
        'inverse_overview': (0, 'Decrypt  ·  Undo the encryption stages in reverse order'),
        'verify': (0, 'Whole cipher  ·  Implementation and verification'),
        'synthesis': (0, 'Whole cipher  ·  From plaintext to ciphertext and back'),
        'math_byte': (0, 'Byte arithmetic for A SubBytes and C MixColumns'),
        'math_inverse': (0, 'Math for A SubBytes  ·  Multiplicative inverses'),
        'math_product': (0, 'Math for C MixColumns  ·  Multiplication in the byte field'),
        'sbox_ref': (0, 'Lookup for A SubBytes  ·  Also used in key expansion'),
        'inverse_lookup': (0, 'Undo A SubBytes  ·  Inverse lookup'),
        'checkpoints': (0, 'Reference  ·  Round keys and states after AddRoundKey'),
    }[focus]
    return phase, caption
