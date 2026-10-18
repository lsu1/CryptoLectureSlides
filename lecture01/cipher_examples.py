from collections import Counter, defaultdict
from math import factorial, log2
import string

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
FREQ_TEXT="Our friend from Paris examined his empty glass with surprise, as if evaporation had taken place while he wasn’t looking. I poured some more wine and he settled back in his chair, face tilted up towards the sun."
FREQ_C='YIFQFMZRWQFYVECFMDZPCVMRZWNMDZVEJBTXCDDUMJNDIFEFMDZCDMQZKCEYFCJMYRNCWJCSZREXCHZUNMXZNZUCDRJXYYSMRTMEYIFZWDYVZVYFZUMRZCRWNZDZJJXZWGCHSMRNMDHNCMFQCHZJMXJZWIEJYUCFWDJNZDIR'
OBSERVED_SUB=dict(zip(norm(FREQ_TEXT),FREQ_C))
assert len(FREQ_C)==len(norm(FREQ_TEXT))==168
assert ''.join(OBSERVED_SUB[ch] for ch in norm(FREQ_TEXT))==FREQ_C
assert len(set(OBSERVED_SUB.values()))==len(OBSERVED_SUB)
DECODE={v:k.lower() for k,v in OBSERVED_SUB.items()}
def partial(mapping):
    return ''.join(mapping.get(ch,'·') for ch in FREQ_C)
def ngram_count(s,gram):
    return sum(s[i:i+len(gram)]==gram for i in range(len(s)-len(gram)+1))

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


Q=[x/sum(ENG) for x in ENG]
def chi_score(col,k):
    obs=Counter(shift(col,-k)); n=len(col)
    return sum((obs[A[i]]-n*Q[i])**2/(n*Q[i]) for i in range(26))
COLUMNS=[VC[j::5] for j in range(5)]
REPEATS=defaultdict(list)
for i in range(len(VC)-2): REPEATS[VC[i:i+3]].append(i)
