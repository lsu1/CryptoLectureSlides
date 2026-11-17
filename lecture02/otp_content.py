"""One-time pad and information theory: examples, probability, and complete secrecy proof.

All numerical examples are computed here so the lecture builder can verify them.
"""
from math import factorial, log2
from deck_schema import slide, P, B, C, M, T, Two, D


def bitxor(a, b):
    """XOR equal-length binary strings without dropping leading zeroes."""
    assert len(a) == len(b) and set(a + b) <= {'0', '1'}
    return ''.join(str(int(x) ^ int(y)) for x, y in zip(a, b))


OTP_LETTER_PLAINTEXT = 'NANYANG'
OTP_LETTER_KEY = 'XRTRPLK'
OTP_LETTER_VALUES = [(ord(p) - 65, ord(k) - 65) for p, k in zip(OTP_LETTER_PLAINTEXT, OTP_LETTER_KEY)]
OTP_LETTER_CIPHERTEXT = ''.join(chr((p + k) % 26 + 65) for p, k in OTP_LETTER_VALUES)
OTP_BIT_PLAINTEXT = '1010011000'
OTP_BIT_KEY = '0110101110'
OTP_BIT_CIPHERTEXT = bitxor(OTP_BIT_PLAINTEXT, OTP_BIT_KEY)
OTP_REUSE_SECOND_PLAINTEXT = '1100001101'
OTP_REUSE_SECOND_CIPHERTEXT = bitxor(OTP_REUSE_SECOND_PLAINTEXT, OTP_BIT_KEY)
OTP_REUSE_RELATION = bitxor(OTP_BIT_CIPHERTEXT, OTP_REUSE_SECOND_CIPHERTEXT)
OTP_COMPATIBILITY_ROWS = [(format(p, '02b'), bitxor(format(p, '02b'), '10')) for p in range(4)]
OTP_BIASED_PRIOR = [('00', 0.5), ('01', 0.25), ('10', 0.125), ('11', 0.125)]
OTP_COIN_ENTROPIES = [1.0, -0.7 * log2(0.7) - 0.3 * log2(0.3), 0.0]
OTP_HMAX = log2(26)
OTP_HL = 1.25
OTP_REDUNDANCY_BITS = OTP_HMAX - OTP_HL
OTP_REDUNDANCY_FRACTION = OTP_REDUNDANCY_BITS / OTP_HMAX
OTP_SUBSTITUTION_KEY_ENTROPY = log2(factorial(26))
OTP_UNICITY_ESTIMATE = OTP_SUBSTITUTION_KEY_ENTROPY / OTP_REDUNDANCY_BITS

assert OTP_LETTER_CIPHERTEXT == 'KRGPPYQ'
assert OTP_BIT_CIPHERTEXT == '1100110110'
assert bitxor(OTP_BIT_CIPHERTEXT, OTP_BIT_KEY) == OTP_BIT_PLAINTEXT
assert OTP_REUSE_RELATION == bitxor(OTP_BIT_PLAINTEXT, OTP_REUSE_SECOND_PLAINTEXT) == '0110010101'


def S(title, blocks, *, section='ONE-TIME PAD', notes='', minutes=2, source='', **kwargs):
    result = slide(title, blocks, section=section, notes=notes, minutes=minutes, **kwargs)
    result['source'] = source
    return result


OTP_SLIDES = [
    S('From a repeating key to a one-time pad', [
        P('Vigenère repeats a short key. Positions sharing one key letter form interleaved shift ciphers.'),
        P('What if the key never repeats, is as long as the message, and is chosen uniformly at random?'),
        P('The one-time pad removes the repeated schedule. Its security will follow from a precise probability argument.')
    ], notes='Connect to the previous lecture’s aligned-column attack. No new key schedule should be assumed random merely because it looks complicated. The next slide makes independence and uniformity explicit.', minutes=2),
    S('The requirements all matter', [
        T(['Requirement', 'Meaning for one message'], [
            ['Uniform and independent', 'Every pad of the required length is equally likely; it is independent of the plaintext.'],
            ['Sufficient length', 'One fresh pad symbol for every plaintext symbol.'],
            ['Secret and used once', 'Only the parties know the pad; no pad segment is reused.']
        ], [230, 626]),
        P('A deterministic expansion of a short secret does not supply a uniformly random pad of arbitrary length.')
    ], take='Perfect secrecy requires these assumptions, including an independent key and a single use.', notes='Treat the conditions as a mathematical model. A uniformly selected n-bit pad has 2^n equally likely values; a short seed has fewer possible expanded sequences. Explain that key independence rules out key generation correlated with message content.', minutes=2),
    S('A letter example: NANYANG with XRTRPLK', [
        T(['Plaintext', 'Key', 'Add modulo 26', 'Output'], [
            [p, k, f'({pv} + {kv}) mod 26 = {(pv + kv) % 26}', c]
            for p, k, (pv, kv), c in zip(OTP_LETTER_PLAINTEXT, OTP_LETTER_KEY, OTP_LETTER_VALUES, OTP_LETTER_CIPHERTEXT)
        ], [150, 150, 406, 150])
    ], take='A = 0, …, Z = 25. The complete ciphertext is KRGPPYQ; decryption subtracts the pad modulo 26.', notes='Retains the original NANYANG / XRTRPLK illustration. Work the first row: N=13, X=23, 36 mod 26 = 10 = K. Point out the two different outputs for repeated N. The seven-letter row is illustrative; a real pad must actually satisfy the generation conditions.', minutes=2.5),
    S('For bits, addition modulo 2 is XOR', [
        P('A bit is 0 or 1; a byte contains eight bits. XOR applies separately at each position.'),
        T(['Bit a', 'Bit b', 'a ⊕ b'], [['0', '0', '0'], ['0', '1', '1'], ['1', '0', '1'], ['1', '1', '0']], [270, 270, 316]),
        M(r'a\oplus b=(a+b)\bmod2.')
    ], notes='Define the ⊕ symbol before using it in message equations. Bitwise XOR is x ^ y in Python, C, C++, and Java; MATLAB uses bitxor(x,y), and R uses bitwXor(x,y). Leading zeroes are part of the specified bit-string length.', minutes=2),
    S('The same XOR operation decrypts', [
        P('Each bit is its own additive inverse modulo 2: adding it twice cancels it.'),
        M(r'0\oplus0=1\oplus1=0,\qquad a\oplus0=a.'),
        M(r'c=p\oplus k\quad\Longrightarrow\quad c\oplus k=p\oplus(k\oplus k)=p.'),
        P('The identities apply bit by bit to equal-length strings, not just to a single bit.')
    ], notes='Use associativity of XOR to regroup terms. Over Z2, subtraction equals addition, so decryption can use the same operation. Distinguish a repeated operation from repeated pad use: applying the same key to decrypt its one ciphertext is correct.', minutes=2),
    S('Exercise: encrypt these ten bits', [
        C('PLAINTEXT AND PAD', 'Plaintext   ' + OTP_BIT_PLAINTEXT + '\nPad         ' + OTP_BIT_KEY),
        P('Compute the ciphertext one position at a time. Preserve the ten-bit length.'),
        P('Then apply the same pad to your ciphertext and check that the plaintext returns.')
    ], sub='Short calculation • 2 minutes', notes='This is the original reference exercise. Pause before advancing to the answer. The first three XOR operations are 1⊕0=1, 0⊕1=1, 1⊕1=0.', minutes=2),
    S('Worked answer: encrypt, then reverse', [
        C('BITWISE XOR', 'Plaintext   ' + OTP_BIT_PLAINTEXT + '\nPad         ' + OTP_BIT_KEY + '\nCiphertext  ' + OTP_BIT_CIPHERTEXT),
        C('DECRYPT WITH THE SAME PAD', OTP_BIT_CIPHERTEXT + ' ⊕ ' + OTP_BIT_KEY + ' = ' + OTP_BIT_PLAINTEXT),
        P('Every ciphertext bit is computed from exactly one plaintext bit and one pad bit.')
    ], notes='Answer: 1100110110. Check several equal-bit and unequal-bit positions. Reinforce that XOR has no carries between positions; ordinary integer addition is a different operation.', minutes=1),
    S('Why a pad segment must never be reused', [
        P('Suppose two messages p₁ and p₂ use the same pad k, producing ciphertexts c₁ and c₂.'),
        M(r'c_1=p_1\oplus k,\qquad c_2=p_2\oplus k.'),
        M(r'c_1\oplus c_2=(p_1\oplus k)\oplus(p_2\oplus k)=p_1\oplus p_2.'),
        P('An interceptor learns a relation between the plaintexts. Knowing one plaintext reveals the other.')
    ], take='Fresh key material is required for every message and every pad segment.', notes='A relation between plaintexts is already a confidentiality failure; reuse does not automatically reveal both messages in full. With structure or known plaintext, the relation can be exploited. Use the next ten-bit example to make cancellation visible.', minutes=2.5),
    S('Pad reuse: cancellation in an actual example', [
        T(['Quantity', 'Ten-bit value'], [
            ['First plaintext p₁', OTP_BIT_PLAINTEXT],
            ['Second plaintext p₂', OTP_REUSE_SECOND_PLAINTEXT],
            ['First ciphertext c₁', OTP_BIT_CIPHERTEXT],
            ['Second ciphertext c₂', OTP_REUSE_SECOND_CIPHERTEXT],
            ['c₁ ⊕ c₂ = p₁ ⊕ p₂', OTP_REUSE_RELATION]
        ], [390, 466]),
        P('The attacker computes the last row directly from the two ciphertexts, without learning the pad first.')
    ], notes='Both messages here use pad 0110101110. The second ciphertext is 1010100011. The XOR relation is 0110010101. If p₁ is known, p₂ = p₁ ⊕ (c₁ ⊕ c₂). The example is an arithmetic illustration rather than a language-based reconstruction.', minutes=2.5),
    S('A historical lesson: VENONA', [
        P('Some Soviet intelligence messages used codebooks with additive one-time-pad material.'),
        P('Duplicate pad material caused some additives to be reused. VENONA analysts exploited this reuse together with message structure and other evidence.'),
        P('The lesson is operational: the mathematical guarantee depends on how keys are generated, distributed, and consumed.')
    ], source='Historical case: NSA/CSS, VENONA declassified history.', notes='Keep the claim limited: reused additives helped recover parts of messages; neither all Soviet traffic nor every reused-pad message was automatically solved. Do not portray this as breaking a correctly implemented one-time pad. Predictable additive sequences likewise violate the uniform-pad assumption.', minutes=1),
    S('Simple operations, demanding key management', [
        P('Early pads could be paper sheets destroyed after use; the name combines “one time” with that physical pad.'),
        P('A 1 GB message requires 1 GB of fresh secret pad material, already shared securely. Storage, synchronization, and avoiding reuse dominate the logistics.'),
        P('Historically, pads were useful in specialized diplomatic and intelligence communications. Their confidentiality claim does not by itself provide message authenticity.')
    ], notes='The byte count is a minimum fresh-pad length for the same binary message representation, before administrative overhead. Physical pads motivate deletion after use. The modern practical alternative is not a short “random-looking” pad called an OTP; later sections distinguish computational constructions.', minutes=2),
    S('Random variables and their probabilities', [
        P('A discrete random variable X takes values x in a finite value space. Write Pr[X = x] for the probability of one value.'),
        M(r'\mathcal X=\{\text{possible values of }X\},\quad\sum_{x\in\mathcal X}\Pr[X=x]=1.'),
        T(['Fair coin outcome x', 'Pr[X = x]'], [['Heads', '1/2'], ['Tails', '1/2']], [430, 426])
    ], section='PROBABILITY', notes='Cryptographic plaintext, key, and ciphertext will be random variables. Lowercase letters denote possible values, not additional random variables. The fair coin is a distributional model, not a promise that every random quantity is uniform.', minutes=1),
    S('Joint probability and independence', [
        P('For random variables X and Y, the joint probability Pr[X = x, Y = y] describes both values occurring together.'),
        M(r'\Pr[X=x,Y=y]\quad\text{is a joint probability.}'),
        P('X and Y are independent precisely when the joint distribution factors for every pair of values:'),
        M(r'\Pr[X=x,Y=y]=\Pr[X=x]\Pr[Y=y].')
    ], section='PROBABILITY', notes='Independence is an assumption that must be justified, not a property implied by different variable names. It will be essential that the OTP key K is independent of the message P.', minutes=1),
    S('Two dice: define the observations first', [
        P('Roll two fair, independent dice D₁ and D₂. Let X = D₁ + D₂. Let Y = d for a double and Y = n otherwise.'),
        D('dice_grid')
    ], section='PROBABILITY', take='The 36 ordered die outcomes are equally likely. Sum 4 occurs at (1,3), (2,2), and (3,1).', notes='Use the 6×6 grid of ordered outcomes. Highlight all six diagonal outcomes as doubles and outline the three cells with sum 4; the intersection is (2,2). X ranges from 2 to 12, while Y takes only d or n. The observations X and Y need not be independent even though D₁ and D₂ are.', minutes=1.5),
    S('Conditioning: restrict the possible outcomes', [
        T(['Event', 'Favourable outcomes', 'Probability'], [
            ['X = 4', '(1,3), (2,2), (3,1)', '3/36 = 1/12'],
            ['Y = d', '(1,1), …, (6,6)', '6/36 = 1/6'],
            ['X = 4 and Y = d', '(2,2)', '1/36']
        ], [260, 360, 236]),
        P('The bar means “given”. Among the three outcomes with sum 4, exactly one is a double.'),
        M(r'\Pr[Y=d\mid X=4]=\frac{\Pr[X=4,Y=d]}{\Pr[X=4]}=\frac{1/36}{3/36}=\frac13.')
    ], section='PROBABILITY', notes='State that the conditioning event must have positive probability. Compare 1/3 with the unconditioned double probability 1/6 to show X and Y are dependent. This also illustrates joint = conditional × marginal.', minutes=2),
    S('Bayes’ rule reverses the conditioning', [
        P('For Pr[X = x] > 0 and Pr[Y = y] > 0, factor the same joint probability in either order:'),
        M(r'\Pr[X=x\mid Y=y]=\frac{\Pr[Y=y\mid X=x]\Pr[X=x]}{\Pr[Y=y]}.'),
        P('In the dice example, ask for sum 4 after learning that a double occurred:'),
        M(r'\Pr[X=4\mid Y=d]=\frac{(1/3)(1/12)}{1/6}=\frac16.')
    ], section='PROBABILITY', take='The two conditional probabilities differ, but each gives the same joint probability 1/36.', notes='The six doubles are equally likely and only (2,2) has sum 4, so direct counting also gives 1/6. Reversing the condition does not preserve its value. We will use Bayes to compare a plaintext prior with its ciphertext-conditioned posterior.', minutes=2),
    S('Perfect secrecy: observing c changes no belief', [
        P('Let P denote the plaintext random variable and C the ciphertext random variable; p and c denote particular messages.'),
        M(r'\Pr[P=p\mid C=c]=\Pr[P=p]\quad\text{for every }p,c\text{ with }\Pr[C=c]>0.'),
        P('The right side is the prior probability. The left side is the posterior after observing c. Perfect secrecy makes them equal.')
    ], section='PERFECT SECRECY', source='Shannon, “Communication Theory of Secrecy Systems” (1949).', notes='This is independence of P and C. It does not assert that every plaintext has the same prior probability. The guarantee concerns the stated ciphertext observation and fixed message-length model, not arbitrary side information or authenticity.', minutes=2.5),
    S('Two bits: every plaintext has a compatible pad', [
        P('Suppose the observed ciphertext is c = 10. For each candidate plaintext p, exactly one two-bit pad k = p ⊕ c produces it.'),
        D('otp_compatibility', ciphertext='10')
    ], section='PERFECT SECRECY', take='Equal-likelihood pads do not imply equal-likelihood plaintexts: the attacker retains the original prior.', notes='Rows should be p=00,k=10; p=01,k=11; p=10,k=00; p=11,k=01. Each pad has probability 1/4 and is independent of P. The diagram is intuition for a conditional likelihood argument, not a proof that the plaintext prior is uniform.', minutes=2.5),
    S('State the model for an n-bit proof', [
        P('Let n be the fixed message length. Plaintext P, key K, and ciphertext C take values in the n-bit strings.'),
        M(r'\mathcal P=\mathcal K=\mathcal C=\{0,1\}^{n},\qquad C=P\oplus K.'),
        P('K is uniform and independent of P: every key k has probability 2⁻ⁿ. The distribution of P can be arbitrary.')
    ], section='PERFECT SECRECY', notes='All variables and spaces are now explicit. Fixed length matters: the theorem does not promise to hide message length. Uniform n-bit K is independent of arbitrary P, including biased or partially predictable messages. Used-once and secrecy are the operational conditions for applying this one-message model.', minutes=2.5),
    S('Proof 1: a fixed message gives a uniform ciphertext', [
        P('Fix a plaintext p with positive probability and any ciphertext c. The unique compatible pad is p ⊕ c.'),
        M(r'\Pr[C=c\mid P=p]=\Pr[K=p\oplus c\mid P=p].'),
        M(r'\Pr[K=p\oplus c\mid P=p]=2^{-n}.'),
        P('Independence lets us ignore the condition P = p; uniformity makes this probability the same for every key.')
    ], section='PERFECT SECRECY', notes='Separate the two assumptions: independence removes conditioning; uniformity gives 2^-n. Uniqueness follows from XOR cancellation. We condition only on positive-prior plaintexts, so no undefined conditional probability is used.', minutes=3),
    S('Proof 2: sum over the possible plaintexts', [
        P('The law of total probability averages those identical likelihoods using the actual plaintext probabilities.'),
        M(r'\Pr[C=c]=\sum_{p:\Pr[P=p]>0}\Pr[P=p]\Pr[C=c\mid P=p].'),
        M(r'=2^{-n}\sum_{p:\Pr[P=p]>0}\Pr[P=p]=2^{-n}.'),
        P('The ciphertext is uniform even when the plaintext is biased. The proof has not assumed a uniform message source.')
    ], section='PERFECT SECRECY', notes='The sum is over the support of P, written explicitly to avoid conditioning on zero-probability values. Plaintext probabilities sum to 1, so every c has positive probability 2^-n. This supplies the denominator needed by Bayes.', minutes=3),
    S('Proof 3: the posterior equals the prior', [
        P('For any plaintext p with positive prior probability, apply Bayes’ rule:'),
        M(r'\Pr[P=p\mid C=c]=\frac{\Pr[C=c\mid P=p]\Pr[P=p]}{\Pr[C=c]}.'),
        M(r'=\frac{2^{-n}\Pr[P=p]}{2^{-n}}=\Pr[P=p].'),
        P('If p has prior probability zero, its joint probability with c is zero, so its posterior is also zero. This covers every plaintext.')
    ], section='PERFECT SECRECY', take='The proof holds for every plaintext distribution under the stated independent, uniform-pad model.', notes='All c have positive probability by the previous page. Explicitly close the zero-prior case rather than claiming conditional likelihoods are defined there. Perfect secrecy is a theorem about distributions, not a claim that a computational attack happens to be slow.', minutes=3),
    S('A biased prior remains biased', [
        T(['Candidate p', 'Prior Pr[P = p]', 'Posterior after C = 10'], [
            ['00', '1/2', '1/2'], ['01', '1/4', '1/4'], ['10', '1/8', '1/8'], ['11', '1/8', '1/8']
        ], [250, 300, 306]),
        P('The most likely plaintext remains 00. Perfect secrecy prevents the ciphertext from improving the attacker’s prior information.')
    ], section='PERFECT SECRECY', notes='The ciphertext probability is 1/4 even for this nonuniform prior. For example, joint probability P=00,C=10 equals (1/2)(1/4)=1/8, so posterior is(1/8)/(1/4)=1/2. All plaintexts being compatible does not mean they become equally likely.', minutes=2),
    S('Entropy quantifies uncertainty', [
        P('For a finite random variable X, entropy H(X) measures average uncertainty in bits. The logarithm is base 2.'),
        M(r'H(X)=-\sum_{x\in\mathcal X}\Pr[X=x]\log_2\Pr[X=x].'),
        P('Use the convention 0 log₂ 0 = 0, obtained by taking a limit. A certain outcome has entropy zero.')
    ], section='INFORMATION THEORY', source='Shannon, “A Mathematical Theory of Communication” (1948).', notes='Corrects the reference’s publication year for this information-theory paper: 1948, while the secrecy-systems paper is 1949. Entropy is distributional uncertainty, not a visual randomness score for a single string. The next coin examples fix the units and interpretation.', minutes=2.5),
    S('Coin examples: uncertainty decreases with bias', [
        P('Let X be the coin outcome and let q = Pr[X = Heads]. Compare the same two-outcome space under three distributions.'),
        D('entropy_bars', probabilities=[0.5, 0.7, 1.0], entropies=OTP_COIN_ENTROPIES)
    ], section='INFORMATION THEORY', take='q = 0.5 gives 1 bit; q = 0.7 gives about 0.881 bits; q = 1 gives 0 bits.', notes='Compare the three labeled bars at 1, 0.8812908992, and 0 bits, for fair/biased/certain coin. Explain a representative computation: -.7log2(.7)-.3log2(.3). A probability-one outcome contributes -1log2(1)=0; the impossible outcome contributes the limit 0.', minutes=2.5),
    S('Language: single letters and longer blocks differ', [
        T(['Source / model', 'Entropy per letter'], [
            ['Uniform independent letters from 26 symbols', 'log₂ 26 ≈ 4.70 bits'],
            ['Illustrative English single-letter frequencies', 'About 4.19 bits'],
            ['Illustrative two-letter block model', 'H(two-letter block)/2 ≈ 3.9 bits'],
            ['Long English-text models', 'Entropy rate often estimated around 1–1.5 bits']
        ], [580, 276]),
        P('Words, spelling, and context create dependencies. A single-letter entropy is not the same quantity as the long-text entropy rate.')
    ], section='INFORMATION THEORY', notes='These English values are illustrative estimates, not universal constants or values from one specified fitted corpus. The key distinction is between one marginal H(P_i), a normalized block entropy, and the limiting rate. English text is neither independent nor uniform.', minutes=3),
    S('Define the entropy rate of a language model', [
        P('Let Pᵢ be the random letter at position i in a language model. Joint block entropy includes dependencies between its letters.'),
        M(r'H_L=\lim_{n\to\infty}\frac{H(P_1,\ldots,P_n)}{n}\quad\text{when this limit exists.}'),
        P('H_L is measured in bits per letter. For the coming numerical illustration, assume H_L = 1.25; this is a model choice, not an exact property of English.')
    ], section='INFORMATION THEORY', notes='H(P_1,...,P_n) is the entropy of the whole length-n vector using the same finite-variable definition. A stationary finite-alphabet model has a well-defined entropy rate. Avoid substituting a one-letter marginal estimate such as 4.19 where the calculation needs the rate 1.25.', minutes=2.5),
    S('Redundancy: unused uncertainty per letter', [
        P('Let A be the 26-letter alphabet. Its maximum entropy per letter is hₘₐₓ; define D as redundancy in bits per letter and R_L as its fraction.'),
        M(r'h_{\max}=\log_2|A|=\log_2 26\approx4.7004.'),
        M(r'D=h_{\max}-H_L\approx3.4504,\qquad R_L=\frac{D}{h_{\max}}\approx0.7341.'),
        P('Under H_L = 1.25, this model is about 73% redundant. D and R_L are different quantities with different units.')
    ], section='INFORMATION THEORY', notes='Use the same 1.25-bit rate in both the redundancy fraction and the next unicity calculation. D is in bits per letter; R_L is dimensionless. The reference mixed approximately 73% and 75%; this deck keeps one consistent numerical assumption.', minutes=3),
    S('Unicity distance is a model-based heuristic', [
        P('As ciphertext grows, language structure can rule out candidate keys. Unicity distance estimates the length at which few plausible spurious keys are expected under the model.'),
        M(r'n_0\approx\frac{H(K)}{D}.'),
        P('H(K) is key entropy in bits and D is redundancy in bits per plaintext letter, so n₀ is measured in letters.')
    ], section='INFORMATION THEORY', take='This is an information-theoretic heuristic, not an attack runtime or a guarantee for every message.', notes='Distinguish possible unique identification from efficient recovery. The estimate depends on a plaintext language model and cipher assumptions; it is not a sharp threshold below which all messages are safe or above which every key is recoverable.', minutes=2.5),
    S('Unicity estimate for a substitution cipher', [
        P('For a uniformly selected alphabet permutation, the key space has 26! elements.'),
        M(r'H(K)=\log_2(26!)\approx88.382\ \text{bits}.'),
        M(r'n_0\approx\frac{88.382}{\log_2 26-1.25}=\frac{88.382}{3.4504}\approx25.6\ \text{letters}.'),
        P('The estimate uses the same entropy-rate assumption as the preceding redundancy calculation.')
    ], section='INFORMATION THEORY', notes='No 0.75 × 4.7 denominator is introduced: the actual denominator is log2(26)-1.25=3.450439718. The quotient is 25.614692777. It says nothing about how much computation a practical cryptanalyst needs.', minutes=3),
    S('Why 25.6 letters is not a universal threshold', [
        P('Even known plaintext need not determine an entire substitution table. If only r distinct plaintext letters occur, mappings for the other 26 − r letters remain unconstrained by those pairs.'),
        M(r'\text{Number of full permutation keys extending those pairs}=(26-r)!.'),
        P('A long message made only of A cannot reveal all 26 mappings. Natural-language unicity estimates describe statistical expectations, not every possible string.')
    ], section='INFORMATION THEORY', notes='This is a known-plaintext identifiability example, deliberately distinguished from the ciphertext-only heuristic. If r=1, there are 25! extensions even for a very long repeated-A message. For ciphertext-only language analysis there can be additional uncertainty. This reinforces the earlier lecture’s23observedletters/6extensions example.', minutes=2.5),
]

OTP_APPENDIX = [
    S('Conditional entropy for the key-size bound', [
        P('For finite random variables X and Y, conditional entropy averages the uncertainty in X after observing Y. Sum only over positive-probability y.'),
        M(r'H(X\mid Y)=\sum_{y:\Pr[Y=y]>0}\Pr[Y=y]\,H(X\mid Y=y).'),
        P('Here H(X | Y = y) is the entropy of the conditional distribution. Joint and further-conditioned entropies use the same definition.'),
        M(r'H(X,Y\mid Z)=H(X\mid Z)+H(Y\mid X,Z).')
    ], section='INFORMATION THEORY', take='Z denotes any further finite observation. Conditioning cannot increase entropy on average.', notes='Preparation for the optional Shannon key-uncertainty bound. State the chain rule, nonnegativity, and H(X|Y)≤H(X); these are average statements, not inequalities for every individual observed value y. This appendix page is not needed to follow the main OTP proof.', minutes=3),
    S('Perfect secrecy requires enough key uncertainty', [
        P('Let P, K, C be finite plaintext, key, and ciphertext variables. Assume exact decryption from K and C, and perfect secrecy.'),
        M(r'H(P\mid K,C)=0,\qquad H(P\mid C)=H(P).'),
        M(r'H(P)=H(P\mid C)\le H(P,K\mid C)=H(K\mid C)\le H(K).'),
        P('Therefore H(K) ≥ H(P). An n-bit uniform OTP key has H(K) = n; equality with message entropy occurs when P is also uniform on all n-bit strings.')
    ], section='PERFECT SECRECY', source='Shannon, “Communication Theory of Secrecy Systems” (1949).', notes='The chain rule and exact decryption make H(P,K|C)=H(K|C). The first inequality adds the nonnegative conditional uncertainty of K after P,C; the last uses conditioning-reduces-entropy. Do not infer that a biased message source always has H(P)=n or that this entropy inequality alone constructs a usable secure cipher.', minutes=3),
]
