"""Practical security and the block-cipher design bridge."""
from deck_schema import *
from crypto_examples import TOY_SBOX, TOY_PERM, TOY_KEYS, TOY_PLAINTEXT, TOY_CIPHERTEXT, TOY_TRACE, TOY_FLIP_MASK, toy_encrypt

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
 S('A 16-bit toy SPN: see the data path',[
  D('toy_spn'),
  P('Three rounds; four 4-bit S-box positions per round. The first two rounds include a bit permutation; a final key XOR follows round 3.')],
  take='A teaching construction with explicit example choices, not a cipher recommended for use.',
  notes='Matches the reference’s 16-bit/three-round structure. Its S-box, permutation, and numerical keys were unspecified; the next slides make illustrative choices explicit.',minutes=3),
 S('Specify the toy substitution and wiring',[
  C('S-BOX: HEX INPUT DIGIT → HEX OUTPUT DIGIT','Input   0 1 2 3 4 5 6 7 8 9 A B C D E F\nOutput  '+' '.join(f'{x:X}' for x in TOY_SBOX),15),
  C('PERMUTATION: OUTPUT POSITION j TAKES INPUT POSITION P[j]','P = 1,5,9,13, 2,6,10,14, 3,7,11,15, 4,8,12,16',15),
  P('Positions start at 1 at the leftmost bit. The same bijective S-box is used at all four positions; it is separate from DES’s S-boxes.')],
  take='One hexadecimal digit represents four bits: A = 1010, F = 1111.',notes='The 16 S-box outputs are distinct, so each nibble can be inverted. The displayed bit permutation is a 4×4 transpose.',minutes=3),
 S('Toy example: work through the first round',[
  C('PLAINTEXT AND ILLUSTRATIVE ROUND KEYS',f'Plaintext  {TOY_PLAINTEXT:04X}\nKeys       '+', '.join(f'{k:04X}' for k in TOY_KEYS),19),
  T(['Operation','Result (hex)','How to obtain it'],[
   ['Key XOR',f'{TOY_TRACE["rounds"][0]["mixed"]:04X}','XOR the plaintext with key K₀.'],
   ['Substitution',f'{TOY_TRACE["rounds"][0]["substituted"]:04X}','Look up each of the four hexadecimal digits.'],
   ['Permutation',f'{TOY_TRACE["rounds"][0]["state"]:04X}','Reorder the 16 bits using P.']],[190,180,486])],
  notes='Pause for a nibble lookup and one output-bit lookup. These round keys are explicit illustrative inputs, not a claim about a secure master-key schedule.',minutes=4),
 S('Finish the three-round toy example',[
  T(['Stage','XOR key','After key XOR','After S-boxes','After P / output'],[
   *[[f'Round {i+1}',f'{TOY_KEYS[i]:04X}',f'{r["mixed"]:04X}',f'{r["substituted"]:04X}',f'{r["state"]:04X}' if i<2 else 'P omitted'] for i,r in enumerate(TOY_TRACE['rounds'])],
   ['Final whitening',f'{TOY_KEYS[3]:04X}','—','—',f'{TOY_CIPHERTEXT:04X}']],[165,140,180,180,191]),
  P('To decrypt, undo the final key XOR, use the inverse S-box, and reverse the first two permutations and earlier key XORs.')],
  take='Every reversible layer has a defined inverse; the layer order reverses during decryption.',notes='Whitening here simply means the final key XOR. It is not an additional substitution round.',minutes=3),
 S('Observe a one-bit change through the toy rounds',[
  T(['Input / stage','Original','One-bit-changed','Differing bits'],[
   ['Plaintext',f'{TOY_PLAINTEXT:04X}',f'{TOY_PLAINTEXT^TOY_FLIP_MASK:04X}','1'],
   *[[f'After round {i+1}',f'{a["state"]:04X}',f'{b["state"]:04X}',str((a['state']^b['state']).bit_count())] for i,(a,b) in enumerate(zip(TOY_TRACE['rounds'],toy_encrypt(TOY_PLAINTEXT^TOY_FLIP_MASK,trace=True)[1]['rounds']))],
   ['Ciphertext',f'{TOY_CIPHERTEXT:04X}',f'{toy_encrypt(TOY_PLAINTEXT^TOY_FLIP_MASK):04X}',str((TOY_CIPHERTEXT^toy_encrypt(TOY_PLAINTEXT^TOY_FLIP_MASK)).bit_count())]],[200,200,200,256]),
  P('This trace illustrates spreading influence. One example is not evidence that the toy construction is secure.')],
  notes='A secure design aims for strong avalanche behavior across many inputs and keys. Do not claim every change flips exactly half the output bits.',minutes=3),
 S('What should a key schedule accomplish?',[
  P('Derive all round keys reproducibly from a single secret key, so the receiver can generate the same sequence.'),
  P('Aim to spread key-bit influence and avoid exploitable patterns, weak-key classes, and simple relations between round keys.'),
  P('There is no universally optimal schedule. Its interaction with the round function must be analysed.')],
  take='A complicated-looking schedule is not a substitute for cryptanalysis.',notes='DES will provide a concrete schedule using selection, rotation, and permutation. The toy round-key list was supplied directly.',minutes=2),
]
