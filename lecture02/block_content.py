"""Practical security and the block-cipher design bridge."""
from deck_schema import *
from crypto_examples import TOY_SBOX, TOY_PERM, TOY_KEYS, TOY_PLAINTEXT, TOY_CIPHERTEXT, TOY_TRACE, TOY_FLIP_MASK, toy_encrypt



def bit_groups(value):
    return ' '.join(f'{int(digit, 16):04b}' for digit in f'{value:04X}')


def routing_rows(value, permutation):
    bits = f'{value:016b}'
    rows = []
    for offset in range(0, 16, 4):
        positions = permutation[offset:offset + 4]
        copied = ''.join(bits[pos - 1] for pos in positions)
        rows.append([f'{offset + 1}–{offset + 4}',
                     ', '.join(map(str, positions)), copied, f'{int(copied, 2):X}'])
    return rows


first_round = TOY_TRACE['rounds'][0]

def S(title,blocks=None,**kw):return slide(title,blocks,section='BLOCK CIPHERS',**kw)
BLOCK_SLIDES=[
 S('From perfect secrecy to practical security',[
  T(['Information-theoretic confidentiality','Computational confidentiality'],[
   ['OTP: ciphertext is independent of the message.','Attacks must exceed a specified resource budget.'],
   ['No bound on the attacker’s computing power.','Assess time, memory, data, and attack model.'],
   ['A fresh secret pad as long as the message.','A short reusable key, under usage limits.']],[428,428]),
  P('A large key space is necessary for resisting exhaustive search. It does not establish security against other attacks.')],
  take='Perfect secrecy is a statistical statement; practical security depends on a construction and an attack model.',
  notes='Do not call all information-theoretic security perfect secrecy: here perfect secrecy is the exact confidentiality property being contrasted.',minutes=3),
 S('Count keys before counting computers',[
  M(r'|\mathcal K|=2^k,\qquad \mathbb E[T]\approx\frac{2^{k-1}}{R}'),
  P('Here k is the number of uniformly random key bits; R is the number of complete candidate-key tests per second.'),
  T(['Key bits k','Mean time if R = 10¹² tests/second'],[
   ['56','About 10 hours'],['80','About 19,000 years'],['128','About 5.4 × 10¹⁸ years']],[230,626])],
  take='These are hypothetical classical exhaustive-search costs, not measured hardware benchmarks.',
  notes='Assume enough known plaintext to reject incorrect keys. Mean cost is about half the key space; worst case is the full space.',minutes=3),
 S('Why FLOPS are not a cipher benchmark',[
  P('A floating-point operation, a CPU clock cycle, and a complete DES or AES key test are different units of work.'),
  P('An attack estimate must name the algorithm, implementation, hardware, memory, and data requirements.'),
  P('Parallel hardware can accelerate search. Future improvements are uncertain; fixed doubling forecasts do not prove long-term security.')],
  take='Measure the operation an attack actually performs.',notes='Replaces the original processor-price list and supercomputer league table. No live hardware ranking is needed.',minutes=2),
 S('The attacker’s information matters',[
  T(['Attack model','Available information','Example'],[
   ['Ciphertext-only','Ciphertexts and a plaintext-language model.','Last lecture’s substitution attack.'],
   ['Known-plaintext','Some matching plaintext/ciphertext pairs.','A file has a predictable header.']],[195,345,316]),
  P('The objective may be to recover the key or to decrypt additional messages. A useful cipher must resist known-plaintext attacks.')],
  notes='A known message does not itself need to stay secret. The attack concerns the remaining protection.',minutes=2),
 S('Known plaintext: a useful contrast',[
  C('ONE-TIME PAD AT KNOWN POSITIONS','ciphertext c XOR known plaintext p = pad k'),
  P('This reveals the pad bits at those positions. Other fresh, independent pad bits remain unrevealed; known plaintext may still give contextual clues about the message.'),
  P('For a block cipher, known plaintext and ciphertext give a test for a candidate key. They should not provide an efficient way to recover it.')],
  take='Known plaintext defeats pad reuse; it does not defeat a correctly used OTP.',notes='Tie back to the reuse example, then distinguish fresh OTP positions from a block cipher’s deliberately reused key.',minutes=2),
 S('Kerckhoffs’ principle: put the secret in the key',[
  P('Assume the attacker knows the cipher’s complete specification. Security should depend on the secrecy of the key.'),
  P('Publishing a design enables independent analysis. It does not require attackers to share their discoveries.'),
  P('Hidden designs can be recovered from software or hardware. Reverse engineering of MIFARE Classic’s Crypto1 is a historical example.')],
  source='Kerckhoffs (1883); MIFARE Classic / Crypto1 research published in 2008.',
  take='A public algorithm is compatible with a secret key.',notes='The original publication/cooperative-attacker claim is removed. Public scrutiny is useful but is not a proof of security.',minutes=2),
 S('A block cipher selects a permutation',[
  M(r'E_k:\{0,1\}^{n}\longrightarrow\{0,1\}^{n},\qquad D_k=E_k^{-1}'),
  D('block_box'),
  P('For each fixed key k, every n-bit input has a different n-bit output. This bijection makes decryption well defined.')],
  take='n is the block size. The key size is a separate parameter.',notes='There are 2^n possible blocks, not n possible blocks. E is a family indexed by k.',minutes=3),
 S('Block size and key size answer different questions',[
  T(['Construction','Block size','Key material','Status / role here'],[
   ['DES','64 bits','56 effective bits','Historical; insecure.'],
   ['Triple DES','64 bits','112 or 168 effective key bits','Historical; retired for new protection.'],
   ['AES','128 bits','128, 192, or 256 bits','Modern comparison; details later.']],[160,135,245,316]),
  P('Key length is not automatically security strength: three-key Triple DES does not provide 168-bit generic attack resistance.')],
  notes='Only compare parameters. Do not introduce AES internals or modes in this lecture.',minutes=2),
 S('Build a complex permutation from simple rounds',[
  D('rounds'),
  P('An iterated cipher updates a state repeatedly. A key schedule derives a sequence of round keys from the master key.'),
  M(r'K\longmapsto(K_1,\ldots,K_r),\qquad X_i=R_i(X_{i-1},K_i)')],
  take='Round keys are related outputs of one schedule, not independent fresh OTP pads.',notes='Define state as the current n-bit intermediate block. R_i denotes a round transformation, not the right half used in Feistel notation later.',minutes=3),
 S('Confusion and diffusion work together',[
  T(['Design idea','Purpose','Typical mechanism'],[
   ['Confusion','Make relations among key, message, and ciphertext complex.','Nonlinear substitution boxes (S-boxes).'],
   ['Diffusion','Spread local input influence across many state bits.','Routing followed by substitution; linear mixing.']],[155,390,311]),
  P('A bit permutation only moves bits. Across rounds, it routes the output of one S-box into several later S-boxes.')],
  take='Neither an S-box nor a wiring diagram alone guarantees a secure cipher.',notes='Avoid equating XOR by itself with nonlinear confusion. A deterministic bit permutation preserves the number of flipped bits.',minutes=3),
 S('Two useful round structures',[
  T(['Substitution–permutation network (SPN)','Feistel network'],[
   ['Substitute small groups; mix or permute the state.','Split the state; transform one half and XOR into the other.'],
   ['Invertible layers give an invertible cipher.','The full round is invertible even if its inner F is not.'],
   ['Our next toy example illustrates the structure.','DES uses 16 Feistel rounds.']],[428,428])],
  notes='This is the first definition of SPN. AES uses a substitution-permutation design but is not the toy network shown here.',minutes=2),
 S('Follow one 16-bit block through three rounds',[
  P('Our plaintext is 1234 in hexadecimal. Each digit stands for four bits, so the four digits together form one 16-bit block.'),
  D('toy_spn')],
  take='For this example the four keys, in order, are K₀ = 3A94, K₁ = A94D, K₂ = 94D6, and K₃ = 4D63.',
  notes='Trace the arrows once. Each intermediate value replaces the preceding block. The S-box and four key values are teaching choices. Keep the first key and the plaintext on the board.',minutes=1),
 S('Round 1 · XOR the plaintext with the first key',[
  P('Write the plaintext and K₀ as four groups of four bits. Compare matching bits. XOR gives 1 when the two bits differ and 0 when they match.'),
  T(['','Hex','Bits in groups of four'],[
   [label, f'{value:04X}', bit_groups(value)] for label,value in
   [('Plaintext',TOY_PLAINTEXT),('Round key K₀',TOY_KEYS[0]),('After XOR',first_round['mixed'])]
  ],[195,135,526]),
  P('In the second group, 2 XOR A gives 0010 XOR 1010 = 1000. That is hex 8.')],
  take='Read the four result groups from left to right to get 28A0.',
  notes='Align the first pair 0001 and 0011, then ask students to read their XOR, 0010. For the second pair, A is ten in decimal and 1010 in binary. Each XOR acts on corresponding bits independently.',minutes=2.5),
 S('Round 1 · Substitute each digit of 28A0',[
  P('Use the same substitution table for each of the four digits. Find the input digit in the top row and copy the entry directly below it.'),
  D('toy_sbox_lookup',value=first_round['mixed'],sbox=TOY_SBOX)],
  take='Join the four outputs in the order of the input digits. The new block is D36E.',
  notes='Begin with the digit 2. Find its column and read D below it. Ask the class to repeat that lookup for 8, A, and 0. Reading those four answers in message order gives D36E.',minutes=2),
 S('Round 1 · Where does the first output digit come from?',[
  P('Expand D36E into bits and number them from 1 to 16, starting on the left. The permutation tells us to copy input positions 1, 5, 9, and 13 into the first four output slots.'),
  D('toy_bit_positions',value=first_round['substituted'],positions=TOY_PERM[:4])],
  take='The copied bits are 1001. In binary place values that is 1 × 8 + 0 × 4 + 0 × 2 + 1 × 1 = 9.',
  notes='Point separately at position 5 and at the 0 underneath it. Ask which of the two is copied. Students should answer 0. Then point to positions 9 and 13 and have them read their bits before forming 1001.',minutes=3),
 S('Round 1 · Copy the remaining bits in order',[
  C('INPUT BITS GROUPED BY HEX DIGIT','D = 1101      3 = 0011      6 = 0110      E = 1110',18),
  T(['Output bits','Copy input positions','Bits copied','Hex digit'],
     routing_rows(first_round['substituted'],TOY_PERM),[155,315,195,191]),
  P('Each row takes one bit from each input group. For the second row, take the second bit of D, then of 3, then of 6, then of E. This gives 1011, or hex B.')],
  take='Reading the output digits in order gives 9B7C. This is the block that enters round 2.',
  notes='Before moving past row two, ask a student to find the bits at positions 2, 6, 10, and 14 on the preceding slide. Repeat for the third and fourth rows as needed. Every input position is used once.',minutes=3),
 S('Finish rounds 2 and 3, then apply the last key',[
  T(['Stage','XOR key','After key XOR','After S-boxes','After P / output'],[
   *[[f'Round {i+1}',f'{TOY_KEYS[i]:04X}',f'{r["mixed"]:04X}',f'{r["substituted"]:04X}',f'{r["state"]:04X}' if i<2 else 'P omitted'] for i,r in enumerate(TOY_TRACE['rounds'])],
   ['Final whitening',f'{TOY_KEYS[3]:04X}','—','—',f'{TOY_CIPHERTEXT:04X}']],[165,140,180,180,191]),
  P('Round 2 starts with 9B7C XOR A94D = 3231. Round 3 starts with 450E and ends after substitution at 9493.'),
  C('FINAL KEY XOR   •   WHITENING','9 XOR 4 = D    4 XOR D = 9    9 XOR 6 = F    3 XOR 3 = 0\n9493 XOR 4D63 = D9F0',17)],
  notes='For round 2 the S-box converts 3, 2, 3, 1 into 1, D, 1, 4. Use the same permutation to obtain 450E. In round 3 the permutation is omitted. To decrypt, first undo whitening with K₃, then undo the substitutions and earlier operations in reverse order.',minutes=2.5),
 S('Change one input bit and follow the difference',[
  P('Change 1234 to 123C and keep the keys fixed. Only the last digit changes, from 4 (0100) to C (1100). That flips input bit 13.'),
  T(['Input / stage','Original','One-bit-changed','Differing bits'],[
   ['Plaintext',f'{TOY_PLAINTEXT:04X}',f'{TOY_PLAINTEXT^TOY_FLIP_MASK:04X}','1'],
   *[[f'After round {i+1}',f'{a["state"]:04X}',f'{b["state"]:04X}',str((a['state']^b['state']).bit_count())] for i,(a,b) in enumerate(zip(TOY_TRACE['rounds'],toy_encrypt(TOY_PLAINTEXT^TOY_FLIP_MASK,trace=True)[1]['rounds']))],
   ['Ciphertext',f'{TOY_CIPHERTEXT:04X}',f'{toy_encrypt(TOY_PLAINTEXT^TOY_FLIP_MASK):04X}',str((TOY_CIPHERTEXT^toy_encrypt(TOY_PLAINTEXT^TOY_FLIP_MASK)).bit_count())]],[200,200,225,231])],
  take='In this example one input bit changes eight ciphertext bits. This illustrates diffusion across rounds.',
  notes='The permutation sends the changed bits to different S-boxes in the next round. The number of differences can then grow under substitution. The final XOR with the same key preserves the eight-bit difference.',minutes=2),
 S('What should a key schedule accomplish?',[
  P('Derive all round keys reproducibly from a single secret key, so the receiver can generate the same sequence.'),
  P('Aim to spread key-bit influence and avoid exploitable patterns, weak-key classes, and simple relations between round keys.'),
  P('There is no universally optimal schedule. Its interaction with the round function must be analysed.')],
  take='A complicated-looking schedule is not a substitute for cryptanalysis.',notes='DES will provide a concrete schedule using selection, rotation, and permutation. The toy round-key list was supplied directly.',minutes=2),
]
