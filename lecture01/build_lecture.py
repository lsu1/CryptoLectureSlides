from pathlib import Path
from collections import Counter, defaultdict
from math import factorial, log2
import string, json, re
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from xml.sax.saxutils import escape

ROOT=Path(__file__).parent
for n,f in [('Sans','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf'),('Mono','DejaVuSansMono.ttf'),('Italic','DejaVuSans-Oblique.ttf')]:
 pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Sans',normal='Sans',bold='Bold',italic='Italic',boldItalic='Bold')
A=string.ascii_uppercase
norm=lambda s: ''.join(x for x in s.upper() if x in A)
def shift(s,k): return ''.join(A[(A.index(x)+k)%26] for x in norm(s))
def vig(s,key,decrypt=False):
 s,key=norm(s),norm(key)
 return ''.join(A[(A.index(x)+(-1 if decrypt else 1)*A.index(key[i%len(key)]))%26] for i,x in enumerate(s))
SUB='QWERTYUIOPASDFGHJKLZXCVBNM'
def sub(s): return norm(s).translate(str.maketrans(A,SUB))
def ic(s):
 n=len(s); return sum(f*(f-1) for f in Counter(s).values())/(n*(n-1)) if n>1 else 0
SQUARE='PLAYFIREXMBCDGHKNOQSTUVWZ'
def prepare(s):
 s=norm(s).replace('J','I'); out=[]; i=0
 while i<len(s):
  a=s[i]; filler='Q' if a=='X' else 'X'
  if i+1==len(s) or s[i+1]==a: out.append(a+filler); i+=1
  else: out.append(s[i:i+2]); i+=2
 return out
def play(s,dec=False):
 pairs=[s[i:i+2] for i in range(0,len(s),2)] if dec else prepare(s)
 out=[]; d=-1 if dec else 1
 for a,b in pairs:
  r,c=divmod(SQUARE.index(a),5); u,v=divmod(SQUARE.index(b),5)
  if r==u: out.append(SQUARE[5*r+(c+d)%5]+SQUARE[5*u+(v+d)%5])
  elif c==v: out.append(SQUARE[5*((r+d)%5)+c]+SQUARE[5*((u+d)%5)+v])
  else: out.append(SQUARE[5*r+v]+SQUARE[5*u+c])
 return ''.join(out)
PERM=[3,1,4,6,2,5]
def perm(s):
 s=norm(s); assert len(s)%6==0
 return ''.join(s[j+i-1] for j in range(0,len(s),6) for i in PERM)
FREQ_TEXT='the secret meeting is in the east tower. the messenger needs the secret letter. send the letter to the east tower and then meet the messenger at the gate.'
FREQ_C=sub(FREQ_TEXT)
CORPUS=norm('''The history of secret writing is also a history of people finding patterns. A sender may replace every letter with another symbol and hope that the message will remain hidden. Yet the habits of a language survive in surprising ways. Common letters still occur often, repeated words leave repeated shapes, and familiar phrases provide clues. A careful reader does not treat any single clue as proof. Instead the reader makes a guess, checks its consequences, and changes the guess when the evidence disagrees. Computers make this process faster but do not remove the need for a clear model of the problem. When a short key is repeated across a long message, the same positions in the key return again and again. Splitting the message into columns can reveal a simple pattern inside each column. Enough text gives the analyst a better chance of distinguishing a useful pattern from a coincidence. The lesson is that a large number of possible keys is only one part of security. We must also ask what information remains visible and what an observer can learn from it. Good engineering starts by stating the assumptions, checking examples, and looking for ways that a system can fail. A secure design must survive careful public study rather than depend on keeping the method unknown.''')
VC=vig(CORPUS,'LEMON')
ENG=[8.167,1.492,2.782,4.253,12.702,2.228,2.015,6.094,6.966,.153,.772,4.025,2.406,6.749,7.507,1.929,.095,5.987,6.327,9.056,2.758,.978,2.360,.150,1.974,.074]
def recover(col):
 def score(k):
  counts=Counter(shift(col,-k)); n=len(col)
  return sum((counts[A[i]]-n*ENG[i]/100)**2/(n*ENG[i]/100) for i in range(26))
 return min(range(26),key=score)
REC=''.join(A[recover(VC[j::5])] for j in range(5))
assert shift('cryptographyisfun',2)=='ETARVQITCRJAKUHWP'
assert vig('attack at dawn','LEMON')=='LXFOPVEFRNHR'
assert vig(VC,'LEMON',True)==CORPUS
assert play('hide the gold in the tree stump')=='BMODZBXDNABEKUDMUIXMMOUVIF'
assert play(play('BALLOON'),True)==''.join(prepare('BALLOON'))
assert REC=='LEMON',REC
assert sorted(PERM)==list(range(1,7))
INV=[PERM.index(i)+1 for i in range(1,7)]
assert ''.join(perm('ATTACK')[i-1] for i in INV)=='ATTACK'

NAVY=colors.HexColor('#132B3C'); TEAL=colors.HexColor('#087E83'); ORANGE=colors.HexColor('#D85C36'); PAPER=colors.HexColor('#F6F4EE'); INK=colors.HexColor('#183342'); MUTED=colors.HexColor('#536875'); LIGHT=colors.HexColor('#E5EEED'); WHITE=colors.white
W,H=960,540
slides=[]; issues=[]
def S(title,blocks=None,sub='',take='',section='FOUNDATIONS',source='',kind='normal'):
 slides.append(dict(title=title,blocks=blocks or [],sub=sub,take=take,section=section,source=source,kind=kind))
def P(s): return ('p',s)
def B(s): return ('b',s)
def C(label,s): return ('code',label,s)
def T(headers,rows,widths=None): return ('table',headers,rows,widths)
def Grid(pairs=None): return ('grid',pairs or [])
def Two(left,right):return ('two',left,right)

S('Classical ciphers', [P('An introduction to cryptography'),P('Five hand ciphers. Five ways to see what secrecy leaves behind.'),C('LECTURE 01','Master’s level • Computer science & engineering')],sub='From secret writing to systematic cryptanalysis',kind='cover',take='Three hours • Worked examples • Two breaks')
S('The question for today',[P('You intercept a message. You know the encryption method, but not the key.'),C('INTERCEPTED',shift('meet me at noon',3)),P('What information would let you recover the message?')],take='Think about the attacker’s information before choosing an attack.')
S('What you will be able to do',[B('Encrypt and decrypt with the five ciphers in this lecture.'),B('Use frequency, repetition, and position as evidence in an attack.'),B('Explain why a large key space alone does not establish security.'),B('Separate a historical teaching cipher from a tool suitable for real data.')])
S('Our three-hour route',[T(['Elapsed time','Focus'],[['00–50 min','Foundations, shift, substitution'],['50–60 min','Break'],['60–110 min','Frequency analysis and Vigenère'],['110–120 min','Break'],['120–170 min','Playfair and transposition'],['170–180 min','Synthesis and exit questions']],[180,676])],take='Exercises and discussion are included in these timings.')
S('Five ciphers, three design ideas',[T(['Design idea','Ciphers in this lecture','What changes?'],[['One symbol at a time','Shift; monoalphabetic substitution','Letter identity'],['Change by position / by pair','Vigenère; Playfair','Mapping with context'],['Rearrange a block','Transposition (permutation)','Letter positions']],[220,360,276])],take='For each cipher: define a key, work an example, and identify what remains visible.')
S('Why study ciphers we should not deploy?',[B('Small examples make the key, algorithm, and attacker visible.'),B('Failures expose recurring problems: predictable data and repeated structure.'),B('Manual attacks introduce the logic behind automated cryptanalysis.')],take='Historical relevance does not imply present-day security.')
S('A short historical thread',[T(['Period','Milestone'],[['Antiquity','Caesar uses a fixed alphabet shift in correspondence.'],['9th century','Al-Kindi describes frequency-based cryptanalysis.'],['1553','Bellaso describes a repeating-key polyalphabetic scheme.'],['1854','Wheatstone invents the cipher promoted by Playfair.'],['19th century','Kasiski publishes a method attacking periodic substitution.']],[170,686])],source='Historical overview: original deck; Kahn, The Codebreakers; Kasiski (1863).')
S('The basic communication model',[('pipeline',),P('Plaintext is the original message; ciphertext is the encrypted message.'),P('A cipher is the algorithm. A key selects one transformation from the family.')],take='Correctness: decrypting an encrypted message with the right key recovers it.')
S('Algorithm ≠ key',[Two([C('PUBLIC METHOD','shift each letter by K'),P('Assume the attacker knows the algorithm.')],[C('SECRET KEY','K = 3'),P('The key is the information the sender and receiver must protect.')])],take='Kerckhoffs’s principle: security should not depend on hiding the method.',source='Kerckhoffs, La Cryptographie Militaire (1883), principle 2.')
S('Shared keys / the setup behind every example',[P('The sender and receiver share a secret key before exchanging messages.'),P('All five ciphers here use symmetric-key encryption: the decryption operation is determined by the same shared key.'),P('An interceptor who learns that key can also decrypt. Getting the key to the receiver securely is a separate problem.')],take='Encryption aims to protect confidentiality; it does not by itself guarantee authenticity.')
S('A minimal threat model',[T(['Attacker’s information','What can be attempted?'],[['Ciphertext only','Infer patterns using a language model.'],['Known plaintext + matching ciphertext','Recover key constraints directly.'],['Chosen plaintext','Observe encryption of selected messages.']],[330,526]),P('We mainly use ciphertext-only attacks today; known plaintext gives useful contrasts.')],take='Always say what the attacker can see or request.')
S('Our notation and conventions',[B('Use the 26-letter English alphabet: A = 0, B = 1, …, Z = 25.'),B('Examples are normalized to uppercase; spaces and punctuation are removed.'),B('Indices start at 0 unless a table explicitly uses positions 1, 2, … .'),B('For each cipher, define any padding or filler rule before using it.')],take='Normalization loses information before encryption; it is not encryption.')
S('Arithmetic on a circular alphabet',[C('WRAP AROUND','Y + 2 → A        A − 2 → Y'),P('Modulo 26 keeps the result in {0, 1, …, 25}.'),C('NUMERIC CHECK','(24 + 2) mod 26 = 0\n(0 − 2) mod 26 = 24')],take='In code, ensure negative remainders are normalized to 0–25.')
S('01 / Shift cipher',[P('One secret offset for every letter.'),C('KEY','K ∈ {0, …, 25}'),P('We include K = 0 mathematically; it leaves the message unchanged.')],kind='divider',section='SHIFT',take='The Caesar cipher conventionally uses K = 3.')
S('Encrypt and decrypt a shift',[C('ENCRYPT','C[i] = (P[i] + K) mod 26'),C('DECRYPT','P[i] = (C[i] − K) mod 26'),P('The same shared key K controls both operations.')],section='SHIFT')
S('Worked example / K = 2',[C('PLAINTEXT','CRYPTOGRAPHYISFUN'),C('CIPHERTEXT',shift('cryptographyisfun',2)),P('Wrap-around checks: Y (24) → A (0); Z (25) → B (1).')],section='SHIFT',take='Check both ordinary letters and wrap-around cases.')
S('Attack the shift cipher',[P('Try each key and inspect the candidate plaintext.'),T(['Candidate K','Decrypt KHOORZRUOG'],[[str(k),shift('KHOORZRUOG',-k)] for k in [1,2,3,4]],[230,626]),P('Only 26 keys exist, including the identity key. Exhaustive search is tiny.')],section='SHIFT',take='The successful candidate is HELLOWORLD at K = 3.')
S('Try it / a shift challenge',[C('CIPHERTEXT','PHHWPHDIWHUFODVV'),P('1. Recover the plaintext without being given K.'),P('2. Explain how you know your answer is plausible.'),P('3. If you know plaintext M corresponds to ciphertext P, what is K?')],sub='Pair exercise • 3 minutes',section='SHIFT',take='Work first; the next slide reveals the answer.')
S('Debrief / little search, useful structure',[C('SOLUTION','K = 3 → MEETMEAFTERCLASS'),C('KNOWN-PLAINTEXT CHECK','K = (15 − 12) mod 26 = 3'),P('Readable language helps select a key. Very short strings may admit several plausible readings.')],section='SHIFT',take='An attacker need not recover the key by brute force if a matching letter is known.')
S('02 / Monoalphabetic substitution',[P('Replace the fixed shift with an arbitrary alphabet permutation.'),P('Each plaintext letter still always becomes the same ciphertext letter.')],kind='divider',section='SUBSTITUTION',take='More keys—but the language still leaves fingerprints.')
S('The key is a bijection',[C('PLAINTEXT ALPHABET',A),C('SUBSTITUTION ALPHABET',SUB),C('WORKED EXAMPLE','BECAUSE → '+sub('because')),P('Decryption uses the inverse table. Distinct input letters must have distinct outputs.')],section='SUBSTITUTION',take='A repeated output letter would make unique decryption impossible.')
S('A huge key space is not enough',[C('NUMBER OF TABLES','26! ≈ 4.03 × 10²⁶ ≈ 2^88.4'),P('At one billion keys per second, trying every table would take about 12.8 billion years.'),P('Yet a substitution preserves letter counts and repeated-letter patterns.')],section='SUBSTITUTION',take='An attack can exploit structure rather than enumerate every key.')
S('What survives substitution?',[Two([C('PATTERN','MEET → DTTZ'),P('The two middle letters remain equal.')],[C('ANOTHER PATTERN','LETTER → STZZTK'),P('Equalities survive; letter identities change.')]),P('Word boundaries, if retained, reveal even more. We remove them in our main example.')],section='SUBSTITUTION',take='A bijective substitution relabels the frequency histogram.')
S('Break / return in 10 minutes',[P('Before you go: why does 26! fail to guarantee security?'),P('After the break, we will use the surviving patterns to attack a complete message.')],kind='divider',section='BREAK 01',take='Elapsed time: 50–60 minutes')
S('Frequency analysis / evidence, not certainty',[B('Count letters in the ciphertext and compare with a plausible language model.'),B('Use pairs, triples, repeated patterns, and context to test candidate mappings.'),B('Revise guesses when they contradict other evidence.')],section='FREQUENCY ANALYSIS',take='The most frequent ciphertext letter is not guaranteed to represent E.')
S('A histogram with the labels scrambled',[('freqchart',),P('This is the actual distribution of our example—not a universal English frequency table.')],section='FREQUENCY ANALYSIS',take='The substitution changes the labels, while the counts stay exactly the same.')
S('The intercepted message',[C(f'{len(FREQ_C)} LETTERS • SPACES REMOVED','\n'.join(FREQ_C[i:i+48] for i in range(0,len(FREQ_C),48))),P('Assume a single substitution table was used throughout.'),P('This deliberately repetitive example is not representative English prose.')],section='FREQUENCY ANALYSIS')
S('Count first; guess second',[T(['Ciphertext symbol','Count','Relative frequency'],[[x,str(n),f'{100*n/len(FREQ_C):.1f}%'] for x,n in Counter(FREQ_C).most_common(6)],[300,200,356]),P('T is a reasonable E candidate. Other mappings need additional evidence.')],section='FREQUENCY ANALYSIS',take='Message topic, length, and style can shift the expected ranking.')
S('Use repeated triples to test a guess',[C('REPEATED CIPHERTEXT PATTERN','ZIT'),P('Hypothesis: ZIT represents THE. Then Z → T, I → H, and T → E.'),C('A CONSEQUENCE TO CHECK','ZITLTEKTZ → THESECRET'),P('A plausible completion is THESECRET. This adds L → S, E → C, and K → R.')],section='FREQUENCY ANALYSIS',take='A word-shaped guess must agree with every occurrence of its letters.')
S('Reveal only the letters supported so far',[C('MAPPINGS USED','Z→T  I→H  T→E  L→S  E→C  K→R'),('partial',),P('Repeated fragments suggest further word hypotheses.'),P('Try a new mapping everywhere before accepting it.')],section='FREQUENCY ANALYSIS',take='Here we show plaintext letters in uppercase and unknown letters as dots.')
S('Exercise / grow the partial key',[C('LOOK FOR THESE FRAGMENTS','DTTZOFU     DTLLTFUTK     STZZTK'),P('Use the current partial key to decode what you can.'),P('Propose two additional letter mappings and justify them with context.'),P('Which of your conclusions are evidence-based guesses rather than certainties?')],sub='Small-group exercise • 4 minutes',section='FREQUENCY ANALYSIS',take='The next slide shows the full teaching plaintext.')
S('Debrief / reconstruct the message',[P('THE SECRET MEETING IS IN THE EAST TOWER. THE MESSENGER NEEDS THE SECRET LETTER. SEND THE LETTER TO THE EAST TOWER AND THEN MEET THE MESSENGER AT THE GATE.'),C('EXAMPLE NEW MAPPINGS','D→M   O→I   U→G   S→L   F→N'),P('The recovered letters must also produce a consistent one-to-one substitution.')],section='FREQUENCY ANALYSIS',take='Letters absent from the message may remain undetermined even after reading it.')
S('When simple frequency analysis struggles',[B('Short messages: counts are noisy, and many readings can fit.'),B('Unusual vocabulary or a different language: the assumed model may be wrong.'),B('Missing spaces: word boundaries must be inferred.'),B('Longer language patterns help: pairs, triples, and four-letter sequences.')],section='FREQUENCY ANALYSIS',take='More ciphertext often helps—but there is no universal length that guarantees success.')
S('03 / Vigenère cipher',[P('Use several shifts, selected by a repeating keyword.'),C('KEY IDEA','Position in the key changes the mapping.')],kind='divider',section='VIGENÈRE',take='The weakness moves from one fixed mapping to a repeating schedule.')
S('A repeating key selects the shifts',[C('RULE','C[i] = (P[i] + K[i mod m]) mod 26'),C('WORKED EXAMPLE','Plaintext   ATTACKATDAWN\nKey         LEMONLEMONLE\nCiphertext  LXFOPVEFRNHR'),P('The key length is m = 5. Decryption subtracts the corresponding key value.')],section='VIGENÈRE',take='The two A letters at positions 0 and 3 encrypt differently.')
S('Exercise / encrypt, then reverse',[C('PLAINTEXT','CRYPTOGRAPHY'),C('KEY','LUCK'),P('Repeat the key, encrypt the first six letters, and check the wrap-around.'),P('Then decrypt your result by subtracting the same repeated key.')],sub='Pair exercise • 3 minutes',section='VIGENÈRE',take='A = 0; the first key shift L is 11, not 12.')
S('Debrief / check every column',[C('ALIGNED ROWS','Plaintext   CRYPTOGRAPHY\nKey         LUCKLUCKLUCK\nCiphertext  '+vig('cryptography','LUCK')),C('FIRST TWO LETTERS','C + L: (2 + 11) mod 26 = 13 → N\nR + U: (17 + 20) mod 26 = 11 → L'),P('One plaintext letter can have different ciphertext letters.')],section='VIGENÈRE')
S('The attack has two stages',[T(['Stage','Question','Tool'],[['1. Find a plausible period','When does the shift schedule repeat?','Kasiski; index of coincidence'],['2. Recover each shift','Which Caesar shift fits each column?','Language scoring; trial decryption']],[220,330,306]),P('The effective period can be shorter than the written keyword: ABCABC repeats every three letters.')],section='VIGENÈRE',take='Finding a candidate key length is a hypothesis, not the end of the attack.')
S('Kasiski / repetitions reveal distances',[C('PLAINTEXT','THESUNANDTHEMANINTHEMOON'),C('KEY','KINGKINGKINGKINGKINGKING'),C('CIPHERTEXT',vig('the sun and the man in the moon','KING')),P('The plaintext THE at positions 9 and 17 has the same key alignment: distance 8.'),P('Both occurrences encrypt to BUK. The period 4 divides their distance.')],section='VIGENÈRE',take='Positions are zero-based. Repeated segments can also occur by coincidence.')
S('Kasiski / turn distances into candidates',[P('Find repeated ciphertext segments, usually at least three letters long.'),P('Measure distances between their starting positions and look for common factors.'),C('ILLUSTRATIVE DISTANCE SET','Distances: 30, 45, 75\ngcd(30, 45, 75) = 15\nCandidate periods: 1, 3, 5, 15'),P('Coincidences can spoil a gcd; true repeats may reveal a multiple of the period.')],section='VIGENÈRE',take='Use several repeats and cross-check the candidate periods statistically.')
S('Index of coincidence / count collisions',[P('Pick two distinct positions at random. What is the chance their letters match?'),C('DEFINITION','IC = Σ f[a](f[a] − 1) / (N(N − 1))'),P('f[a] is the count of letter a; N is the number of letters. Require N ≥ 2.'),C('SMALL CHECK','AAB: IC = 2 / 6 = 1/3')],section='VIGENÈRE',take='The sum is over all 26 letters; ordered pairs are counted consistently.')
S('What IC does—and does not—measure',[T(['Text model','Expected / typical IC'],[['Independent uniform letters','1/26 ≈ 0.0385'],['Ordinary English prose','Often about 0.065; varies by text'],['One fixed substitution of that prose','Exactly the same IC as the original text']],[550,306]),P('IC is a statistical clue, not a general test of security.')],section='VIGENÈRE',take='A Caesar shift preserves counts up to relabeling, so it preserves IC.')
S('Guess a period; split into columns',[C('FOR CANDIDATE PERIOD m = 5','Column 0: C[0], C[5], C[10], …\nColumn 1: C[1], C[6], C[11], …\n…\nColumn 4: C[4], C[9], C[14], …'),P('At the correct period, each column is encrypted by a single fixed shift.'),P('Wrong periods usually mix shifts. Multiples of the true period may also look good.')],section='VIGENÈRE',take='Short columns make IC estimates unreliable; prefer enough data and corroborating evidence.')
S('A reproducible IC experiment',[T(['Candidate period','Mean column IC','Interpretation'],[[str(m),f'{sum(ic(VC[j::m]) for j in range(m))/m:.4f}', 'Strong candidate / multiple' if m in (5,10) else 'Mixed key positions'] for m in [1,2,3,4,5,10]],[240,250,366]),P(f'Computed from {len(VC)} letters of original English prose, encrypted with key LEMON.')],section='VIGENÈRE',take='The full plaintext, ciphertext, and calculations accompany this deck.')
S('Recover a column by scoring all 26 shifts',[P('For each candidate shift, decrypt the column and compare its letter counts with an English model.'),C('ONE STANDARD SCORE','χ² = Σ (observed − expected)² / expected'),P('Lower scores indicate a closer fit to that model; try promising candidates in the complete message.'),P('Use every letter count—not only the most frequent letter.')],section='VIGENÈRE',take='Enumerating 26 candidates per column is practical; language scoring makes it useful.')
S('Recover the key / confirm the message',[T(['Column','Best-scoring shift','Key letter'],[[str(j),str(recover(VC[j::5])),A[recover(VC[j::5])]] for j in range(5)],[240,330,286]),P('Recovered key: LEMON. Decryption begins THEHISTORYOFSECRETWRITING…')],section='VIGENÈRE',take='We do not need to enumerate all 26ᵐ complete keys: columns can be scored independently.')
S('Checkpoint / what broke Vigenère?',[P('Explain why repeating the key creates several interleaved shift ciphers.'),P('Why can a candidate period of 10 look convincing when the true period is 5?'),P('What extra uncertainty would you expect from a 25-letter message?')],sub='Discussion • 3 minutes',section='VIGENÈRE',take='Answers: periodic alignment; multiples preserve alignment; too little data per column.')
S('Break / return in 10 minutes',[P('So far: a huge table leaks frequencies; a repeating key leaks periodicity.'),P('Next: encrypt pairs of letters, then try moving the letters instead.')],kind='divider',section='BREAK 02',take='Elapsed time: 110–120 minutes')
S('04 / Playfair cipher',[P('Encrypt pairs of letters using a small key square.'),P('Invented by Charles Wheatstone in 1854 and promoted by Lyon Playfair.')],kind='divider',section='PLAYFAIR',take='A practical historical hand cipher—not a present-day security mechanism.')
S('From codebooks to letter pairs',[P('A codebook can assign a code group to an entire word or instruction.'),C('CODEBOOK ILLUSTRATION','“Attack at dawn” → 48271'),P('Playfair instead uses a compact rule to substitute letter pairs. It avoids distributing a huge phrase table.'),P('Historical attraction: manual operation with more complexity than a single-letter substitution.')],section='PLAYFAIR',take='Codebooks operate on meaningful units; Playfair operates on prepared letter pairs.')
S('Build the Playfair square',[Two([P('Keyword: PLAYFAIR EXAMPLE'),P('1. Merge J into I.'),P('2. Remove spaces and repeated letters, keeping first occurrences.'),P('3. Append unused letters in alphabetical order.')],[Grid()])],section='PLAYFAIR',take='Distinct keyword letters: P L A Y F I R E X M. The square has 25 cells.')
S('Prepare pairs carefully',[C('RULE','Scan left to right; form pairs of distinct letters.'),P('If the next two letters match, insert X after the first and reconsider the second letter.'),P('Pad a final single letter with X. For a repeated or final X, use Q instead.'),C('EXAMPLE','BALLOON → BA LX LO ON\nX → XQ      XX → XQ XQ')],section='PLAYFAIR',take='This lecture specifies Q as the alternate filler; implementations can use different conventions.')
S('Three geometric rules',[Two([P('<b>Same row:</b> move each letter one cell right, wrapping at the edge.'),P('<b>Same column:</b> move each letter one cell down, wrapping at the bottom.'),P('<b>Rectangle:</b> keep each letter’s row and use the other letter’s column.')],[Grid()])],section='PLAYFAIR',take='Apply exactly one rule to each prepared pair.')
S('Worked pairs / see each rule',[Two([C('SAME ROW','PL → LA'),C('SAME COLUMN','PI → IB'),C('RECTANGLE','HI → BM')],[Grid(['PL','PI','HI'])])],section='PLAYFAIR',take='For a rectangle, preserve the order of the two input rows.')
S('A complete Playfair example',[C('NORMALIZED PLAINTEXT','HIDETHEGOLDINTHETREESTUMP'),C('PREPARED PAIRS','HI DE TH EG OL DI NT HE TR EX ES TU MP'),C('ENCRYPTED PAIRS','BM OD ZB XD NA BE KU DM UI XM MO UV IF'),P('Notice the inserted X in TREE: preparation changes the representation before encryption.')],section='PLAYFAIR',source='Standard PLAYFAIR EXAMPLE illustration, also used in the supplied deck.')
S('Decrypt by reversing the movement',[Two([P('<b>Same row:</b> move left.'),P('<b>Same column:</b> move up.'),P('<b>Rectangle:</b> use the same opposite-corner rule.'),C('CHECK','BM → HI\nLA → PL\nIB → PI')],[Grid()])],section='PLAYFAIR',take='Decryption recovers the prepared text, including any inserted fillers.')
S('Exercise / decrypt a Playfair message',[C('KEYWORD','PLAYFAIR EXAMPLE'),C('CIPHERTEXT','RO NC FL WI'),P('Use the same square and write down the rule used for each pair.'),P('After decryption, decide whether any filler should be removed.')],sub='Pair exercise • 4 minutes',section='PLAYFAIR',take='The answer follows on the next slide.')
S('Debrief / fillers require interpretation',[C('PAIR-BY-PAIR SOLUTION','RO → EN    NC → CR\nFL → YP    WI → TX'),C('PREPARED PLAINTEXT',play('RONCFLWI',True)),P('The prepared plaintext is ENCRYPTX. The final X pads the last single letter.'),P('The intended reading is ENCRYPT. We remove the final X using context, not a cipher rule.')],section='PLAYFAIR',take='Keep the padding in the mechanical decryption; interpret it in a separate step.')
S('One more challenge / repeated letters',[Two([C('CIPHERTEXT',''+ ' '.join(play('balloon')[i:i+2] for i in range(0,len(play('balloon')),2))),P('Decrypt with the same square. Then infer a likely original word.')],[Grid()])],sub='Pair exercise • 2 minutes',section='PLAYFAIR',take='Solution: BA LX LO ON → BALLOON. The inserted X splits the original repeated L.')
S('Why filler removal is ambiguous',[C('EXAMPLE','AXA → AX AX\nAA  → AX AX'),P('Both messages prepare to AXAX under our rules, so they encrypt identically.'),P('Removing every X would corrupt genuine X letters. Merging I/J also loses information.')],section='PLAYFAIR',take='The cipher is reversible on prepared pairs; preparation is not reversible in general.')
S('How Playfair can still be attacked',[B('Single-letter frequencies are less direct, but pair and longer patterns survive.'),B('Try a candidate square; decrypt and score the result using language statistics.'),B('Change the square and retain better candidates. Use restarts to escape poor local choices.')],section='PLAYFAIR',take='Search quality depends on text length, language, scoring, and computation—not a fixed guarantee.')
S('Hill climbing / the attack as an algorithm',[C('SEARCH LOOP','candidate square → decrypt → language score\n          ↑                         ↓\n          └──── change square ← keep if better'),P('For example, swap two square entries and compare four-letter sequence scores.'),P('A local optimum may not be the correct square. Multiple random starts help.')],section='PLAYFAIR',take='A readable result must be checked by re-encryption and contextual consistency.')
S('05 / Transposition cipher',[P('Keep the letters. Change only their positions.'),C('FOCUS','Fixed-size block permutation')],kind='divider',section='TRANSPOSITION',take='A permutation is a one-to-one rearrangement of positions.')
S('Define the direction of the permutation',[T(['Ciphertext position i','1','2','3','4','5','6'],[['Plaintext position π(i)']+[str(x) for x in PERM]],[310,91,91,91,91,91,91]),C('RULE','C[i] = P[π(i)]'),P('This table tells us which plaintext position supplies each output position.'),P('The block size is 6. Pad the last block with X; retain the original length separately.')],section='TRANSPOSITION',take='Some sources define the reverse direction; a worked example prevents ambiguity.')
S('Worked example / rearrange two blocks',[C('PLAINTEXT','ATTACK ATDAWN'),C('PERMUTATION','Read positions 3, 1, 4, 6, 2, 5'),C('CIPHERTEXT',perm('ATTACK')+' '+perm('ATDAWN')),P('First block: input positions 3, 1, 4, 6, 2, 5 give T, A, A, K, T, C.')],section='TRANSPOSITION',take='No letter changes identity; every block retains exactly its original letter counts.')
S('Decryption uses the inverse permutation',[C('ENCRYPTION ORDER','π = [3, 1, 4, 6, 2, 5]'),C('DECRYPTION ORDER','π⁻¹ = ['+', '.join(map(str,INV))+']'),C('CHECK',perm('ATTACK')+' → ATTACK'),P('Equivalently, place each ciphertext letter back into the plaintext position named by the encryption table.')],section='TRANSPOSITION',take='Verify the direction by checking one full round trip.')
S('Exercise / the letters are all still there',[C('PLAINTEXT','DEFEND'),P('Encrypt with π = [3, 1, 4, 6, 2, 5]. Then decrypt your result.'),P('How many possible permutations are there for this block size?'),P('Would ordinary single-letter frequency counts change?')],sub='Pair exercise • 3 minutes',section='TRANSPOSITION',take='Check repeated letters as well as the table direction.')
S('Debrief / preserved counts expose structure',[C('SOLUTION','DEFEND → '+perm('DEFEND')),P('There are 6! = 720 possible keys for this particular block size.'),P('The histogram is unchanged. Candidate rearrangements can be ranked by language patterns.'),P('With longer blocks, exhaustive search grows, but preserved statistics remain a weakness.')],section='TRANSPOSITION',take='Permutation is a useful design ingredient; this simple cipher alone is weak.')
S('Compare the five ciphers',[T(['Cipher','Key / structure','Useful attack clue'],[['Shift','One offset','26 candidates; readable text'],['Substitution','One alphabet permutation','Counts and repeated patterns'],['Vigenère','Periodic shifts','Repetitions; column statistics'],['Playfair','5 × 5 square; letter pairs','Language-scored square search'],['Transposition','A fixed position permutation','Unchanged counts; word patterns']],[180,310,366])],section='SYNTHESIS',take='For each design, ask: what does the transformation fail to hide?')
S('A contemporary reason to care',[P('A team stores an API credential in a configuration file, shifted by 13 letters, and calls it “encrypted”.'),P('An attacker who reads the file can try every shift immediately. Hiding the transformation offers little help.'),P('The engineering question is who can obtain the secret—and what assumptions protect it.')],section='SYNTHESIS',take='Illustrative present-day scenario, not a reported incident. Never protect real secrets with these ciphers.')
S('From letters to exact digital data',[C('BYTES • HEXADECIMAL','A → 41     0 → 30     ? → 3F     space → 20'),P('These are ASCII code values represented as bytes; ASCII itself is a 7-bit code.'),P('Modern encryption accepts bytes or bits, so spaces, files, and images can be recovered exactly.'),P('Security needs more than obscuring letter frequencies: key handling and protection against tampering also matter.')],section='SYNTHESIS',take='We motivate later lectures here without introducing additional cipher algorithms.')
S('Exit questions / explain your reasoning',[P('1. Why can a cipher with 26! keys still be breakable?'),P('2. Which observation makes a repeating-key cipher vulnerable?'),P('3. Why can Playfair decryption fail to recover the exact original spelling?'),P('4. Which cipher leaves the complete letter histogram unchanged?')],sub='Individual reflection • 4 minutes',section='SYNTHESIS',take='A useful answer identifies a surviving property, not just an attack name.')
S('Exit discussion / the four ideas',[B('Substitution preserves frequency structure even when exhaustive search is infeasible.'),B('Vigenère repeats the shift schedule; aligned columns reduce to shift ciphers.'),B('Playfair preparation inserts fillers and merges I/J, losing information.'),B('Transposition leaves letter identities—and therefore their counts—unchanged.')],section='SYNTHESIS',take='All five ciphers are learning tools, not recommendations for real-world encryption.')
S('Reading and sources',[P('<b>Primary teaching reference:</b> supplied <i>Lecture02_Classical_Ciphers.pdf</i>, Wu Hongjun, 79 pages. Scope and example-based approach retained; examples and explanations revised.'),P('<b>Technical reading:</b> Stinson &amp; Paterson, <i>Cryptography: Theory and Practice</i>, 4th ed., Chapter 1. Section numbering differs across editions.'),P('<b>History:</b> Kahn, <i>The Codebreakers</i> (rev. ed., 1996); Kerckhoffs (1883); Kasiski (1863).'),P('<b>Companion materials:</b> teaching guide, reproducible examples, and build source accompany this PDF. No external images or copied news articles are used.')],section='REFERENCES',take='The lecture ends here. All numerical examples in this deck are generated and checked in the build source.')

# Example invariants: fail the build if a displayed result ceases to match its definition.
assert shift('MEETMEAFTERCLASS',3)=='PHHWPHDIWHUFODVV'
assert sub('MEET')=='DTTZ' and sub('LETTER')=='STZZTK'
assert sub('THESECRET')=='ZITLTEKTZ'
assert sub('MEETING')=='DTTZOFU' and sub('MESSENGER')=='DTLLTFUTK'
assert play('PL')=='LA' and play('PI')=='IB' and play('HI')=='BM'
assert play('RONCFLWI',True)=='ENCRYPTX'
assert play('AXA')==play('AA') and prepare('AXA')==prepare('AA')
assert perm('ATTACK')=='TAAKTC' and perm('ATDAWN')=='DAANTW'
assert perm('DEFEND')=='FDEDEN'
assert vig('cryptography','LUCK')=='NLAZEIIBLJJI'
assert len(set(SQUARE))==25 and 'J' not in SQUARE
assert SQUARE==''.join(dict.fromkeys(norm('Playfair Example').replace('J','I')+A.replace('J','')))
assert abs(ic('AAB')-1/3)<1e-12
assert round(factorial(26)/1e9/(365.25*86400)/1e9,1)==12.8
assert round(log2(factorial(26)),1)==88.4
assert vig('the sun and the man in the moon','KING')[9:12]=='BUK'
assert vig('the sun and the man in the moon','KING')[17:20]=='BUK'
for text in ['BALLOON','HIDE THE GOLD IN THE TREE STUMP','X','XX','AXA','AA','MEET ME AT NOON']:
    assert play(play(text),True)==''.join(prepare(text))
for k in range(26):
    assert shift(shift(A,k),-k)==A
# Correct, then validate the old challenge rather than inherit an unverified answer.
print('old challenge:',play('RONCFLWI',True))
print('shift:',shift('cryptographyisfun',2))
print('frequency length/counts:',len(FREQ_C),Counter(FREQ_C).most_common(6))
print('vig demo:',vig('cryptography','LUCK'))
print('IC:',[(m,round(sum(ic(VC[j::m]) for j in range(m))/m,4)) for m in [1,2,3,4,5,10]])
print('Playfair meeting:',prepare('meet me at noon'),play('meet me at noon'))

styles={}
for size in [12,13,14,15,16,17,18,19,20,22,26]:
 styles[size]=ParagraphStyle(str(size),fontName='Sans',fontSize=size,leading=size*1.4,textColor=INK,spaceAfter=0)
def para(c,s,x,y,w,size=18,color=None):
 st=ParagraphStyle('p',parent=styles[size],textColor=color or INK)
 p=Paragraph(s,st); _,h=p.wrap(w,800)
 p.drawOn(c,x,y-h)
 return y-h

def drawblocks(c,blocks,x,y,w,slide):
 for block in blocks:
  typ=block[0]
  if typ in ('p','b'):
   s=block[1]
   if typ=='b':
    c.setFillColor(TEAL); c.circle(x+4,y-12,3,fill=1,stroke=0)
    y=para(c,s,x+22,y,w-22,18)-17
   else:y=para(c,s,x,y,w,18)-17
  elif typ=='code':
   _,label,s=block
   lines=s.split('\n'); fs=19
   while max(pdfmetrics.stringWidth(v,'Mono',fs) for v in lines)>w-30: fs-=.5
   hh=29+len(lines)*(fs*1.35)+12
   c.setFillColor(LIGHT); c.roundRect(x,y-hh,w,hh,8,fill=1,stroke=0)
   c.setFillColor(TEAL); c.setFont('Bold',9); c.drawString(x+16,y-17,label)
   c.setFillColor(INK); c.setFont('Mono',fs)
   for j,line in enumerate(lines): c.drawString(x+16,y-39-j*fs*1.35,line)
   y-=hh+14
  elif typ=='table':
   _,headers,rows,widths=block
   widths=widths or [w/len(headers)]*len(headers)
   if sum(widths)!=w:widths=[v*w/sum(widths) for v in widths]
   data=[[Paragraph(escape(str(cell)),ParagraphStyle('t',parent=styles[14],textColor=WHITE if i==0 else INK,fontName='Bold' if i==0 else 'Sans')) for cell in row] for i,row in enumerate([headers]+rows)]
   table=Table(data,colWidths=widths)
   table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'Sans'),('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[LIGHT,colors.HexColor('#EFF2EF')]),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12),('TOPPADDING',(0,0),(-1,-1),9),('BOTTOMPADDING',(0,0),(-1,-1),9),('LINEBELOW',(0,0),(-1,0),1,TEAL)]))
   _,hh=table.wrap(w,800); table.drawOn(c,x,y-hh); y-=hh+17
  elif typ=='two':
   gap=32; ww=(w-gap)/2
   y1=drawblocks(c,block[1],x,y,ww,slide);y2=drawblocks(c,block[2],x+ww+gap,y,ww,slide);y=min(y1,y2)
  elif typ=='grid':
   cell=48; gx=x+(w-5*cell)/2; gy=y-5*cell
   highlight=set(''.join(block[1]))
   for i,ch in enumerate(SQUARE):
    r,col=divmod(i,5); xx=gx+col*cell; yy=gy+(4-r)*cell
    c.setFillColor(TEAL if ch in highlight else LIGHT);c.setStrokeColor(PAPER);c.rect(xx,yy,cell,cell,fill=1,stroke=1)
    c.setFillColor(WHITE if ch in highlight else INK);c.setFont('Mono',22);c.drawCentredString(xx+cell/2,yy+16,ch)
   y=gy-18
  elif typ=='pipeline':
   ww=(w-80)/3
   for j,(a,b) in enumerate([('PLAINTEXT','MEET AT NOON'),('ENCRYPT WITH KEY','…ciphertext…'),('DECRYPT WITH KEY','MEET AT NOON')]):
    xx=x+j*(ww+40); c.setFillColor(LIGHT); c.roundRect(xx,y-99,ww,99,8,fill=1,stroke=0)
    c.setFillColor(TEAL);c.setFont('Bold',10);c.drawCentredString(xx+ww/2,y-28,a)
    c.setFillColor(INK);c.setFont('Sans',17);c.drawCentredString(xx+ww/2,y-65,b)
    if j<2:
     c.setStrokeColor(ORANGE);c.setLineWidth(2);c.line(xx+ww+7,y-50,xx+ww+31,y-50);c.line(xx+ww+25,y-44,xx+ww+31,y-50);c.line(xx+ww+25,y-56,xx+ww+31,y-50)
   y-=124
  elif typ=='partial':
   mapping={'Z':'T','I':'H','T':'E','L':'S','E':'C','K':'R'}
   ss=''.join(mapping.get(ch,'.') for ch in FREQ_C)
   y=drawblocks(c,[C('PARTIAL DECRYPTION','\n'.join(ss[i:i+48] for i in range(0,len(ss),48)))],x,y,w,slide)
  elif typ=='freqchart':
   counts=Counter(norm(FREQ_TEXT)); top=max(counts.values()); bw=w/26; base=y-214
   for i,ch in enumerate(A):
    hh=counts[ch]/top*170;xx=x+i*bw+3
    c.setFillColor(TEAL);c.rect(xx,base,bw-7,hh,fill=1,stroke=0)
    c.setFillColor(INK);c.setFont('Mono',10);c.drawCentredString(xx+(bw-7)/2,base-17,ch)
    if counts[ch]:c.setFont('Sans',9);c.drawCentredString(xx+(bw-7)/2,base+hh+6,str(counts[ch]))
   c.setFont('Sans',10);c.drawString(x,base-37,'Plaintext letter labels • bar height = count; substitution preserves every bar height')
   y=base-58
  if y+14<89: issues.append((slide,typ,round(y,1)))
 return y

out=ROOT/'Lecture01_Classical_Ciphers.pdf'
c=canvas.Canvas(str(out),pagesize=(W,H),initialFontName='Sans')
c.setTitle('Lecture 01 — Classical Ciphers');c.setAuthor('Cryptography lecture series');c.setSubject('Three-hour introductory lecture for master’s students')
for i,s in enumerate(slides,1):
 dark=s['kind'] in ('cover','divider')
 c.setFillColor(NAVY if dark else PAPER);c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(ORANGE);c.rect(52,492,34,4,fill=1,stroke=0)
 c.setFillColor(WHITE if dark else TEAL);c.setFont('Bold',10);c.drawString(98,490,s['section'])
 # title is one line where possible, smaller as needed
 fs=34
 while pdfmetrics.stringWidth(s['title'],'Bold',fs)>856: fs-=.5
 c.setFont('Bold',fs);c.setFillColor(WHITE if dark else NAVY);c.drawString(52,445,s['title'])
 top=410
 if s['sub']:
  top=para(c,s['sub'],52,411,856,16,WHITE if dark else MUTED)-21
 if dark:
  # Invert paragraph palette only; code cards retain their readable light palette.
  for block in s['blocks']:
   if block[0]=='p':top=para(c,block[1],52,top,820,22,WHITE)-24
   else:top=drawblocks(c,[block],52,top,856,i)
 else:drawblocks(c,s['blocks'],52,top,856,i)
 if s['take']:
  c.setFillColor(TEAL if dark else LIGHT);c.roundRect(52,43,856,35,5,fill=1,stroke=0)
  p=Paragraph(escape(s['take']),ParagraphStyle('take',parent=styles[12],textColor=WHITE if dark else INK))
  _,hh=p.wrap(830,40)
  if hh>29:issues.append((i,'takeaway',hh))
  p.drawOn(c,65,60-hh/2)
 c.setFont('Sans',8);c.setFillColor(colors.HexColor('#BDD0D7') if dark else MUTED)
 c.drawString(52,22,s['source'] if s['source'] else 'CRYPTOGRAPHY / LECTURE 01 / CLASSICAL CIPHERS')
 c.drawRightString(908,22,f'{i:02d} / {len(slides):02d}')
 c.showPage()
c.save()
(ROOT/'slide_manifest.json').write_text(json.dumps(slides,ensure_ascii=False,indent=2))
(ROOT/'worked_examples.json').write_text(json.dumps(dict(substitution_alphabet=SUB,frequency_plaintext=FREQ_TEXT,frequency_ciphertext=FREQ_C,frequency_counts=dict(Counter(FREQ_C)),vigenere_plaintext=CORPUS,vigenere_ciphertext=VC,vigenere_key='LEMON',recovered_key=REC,column_IC={str(m):[ic(VC[j::m]) for j in range(m)] for m in [1,2,3,4,5,10]},playfair_square=SQUARE,permutation=PERM,inverse_permutation=INV),indent=2))
print('Slides',len(slides),'Layout issues',issues)
assert not issues,issues
