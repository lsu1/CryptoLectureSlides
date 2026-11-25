"""Lecture 02 assembly and wall-clock pacing. Edit the three content modules."""
from copy import deepcopy
from deck_schema import *
from otp_content import OTP_SLIDES,OTP_APPENDIX
from block_content import BLOCK_SLIDES
from des_content import FEISTEL_SLIDES,DES_SLIDES,DES_APPENDIX,FEISTEL_APPENDIX,DES_SBOX_APPENDIX

slides=[]
SESSION_PLAN=[]
def add_block(items,start,end,minutes,label):
 first=len(slides)+1;items=deepcopy(items)
 raw=sum(s['minutes'] for s in items)
 for s in items:
  s['minutes']=s['minutes']*minutes/raw
  slides.append(s)
 SESSION_PLAN.append(dict(kind='teaching',start=start,end=end,minutes=minutes,label=label,slides=[first,len(slides)]))
def add_break(start,end,number,next_text):
 n=len(slides)+1
 slides.append(slide('Break / 10 minutes',[P(next_text)],section=f'BREAK {number:02d}',kind='divider',take=f'{start}–{end} • Resume at {end}',notes='Ten-minute break. The following section starts at the stated return time.',minutes=10))
 SESSION_PLAN.append(dict(kind='break',start=start,end=end,minutes=10,label='Break',slides=[n,n]))

cover=slide('One-time pads & block ciphers',[P('Perfect secrecy, practical security, and DES')],section='LECTURE 02',kind='cover',notes='Continue from last lecture’s repeating-key weaknesses. Today we contrast a proof of perfect secrecy with the structure and limitations of practical block ciphers.',minutes=1)
add_block([cover]+OTP_SLIDES,'6:30 pm','7:40 pm',70,'One-time pads, probability, perfect secrecy, and information theory')
add_break('7:40 pm','7:50 pm',1,'Next: practical security, block-cipher rounds, and the Feistel construction.')
add_block(BLOCK_SLIDES+FEISTEL_SLIDES,'7:50 pm','8:50 pm',60,'Practical security, block-cipher design, toy SPN, and Feistel networks')
add_break('8:50 pm','9:00 pm',2,'Next: follow a DES round, derive its round keys, and examine multiple encryption.')
closing=slide('Three ideas to carry forward',[
 T(['Idea','What we established'],[
  ['Perfect secrecy','With a uniform independent fresh pad, observing ciphertext does not change the message distribution.'],
  ['Practical block ciphers','A short key selects a permutation; security depends on the full design and the attacker’s resources.'],
  ['Feistel and DES','Reversibility can survive a non-invertible inner function; a sound structure still needs adequate key and block sizes.']],[210,646]),
 P('DES and Triple DES explain foundational design choices. Modern cipher design and message-encryption modes follow in later lectures.')],section='SYNTHESIS',notes='Use the last minutes for clarification and returning to the difference between a theorem of independence and a computational security assessment. The optional appendix is a reference, not material to rush through.',minutes=2)
add_block(DES_SLIDES+[closing],'9:00 pm','10:00 pm',60,'DES internals, key schedule, Double DES, and Triple DES')
MAIN_COUNT=len(slides)
appendix = OTP_APPENDIX + DES_APPENDIX + FEISTEL_APPENDIX + DES_SBOX_APPENDIX
for i,s in enumerate(deepcopy(appendix),1):
 s['title']=f'A{i} / '+s['title'];s['section']='APPENDIX';s['minutes']=0
 slides.append(s)

# Resolve the key-derivation reference after all teaching slides are assembled.
pages_by_title = {s['title']: number for number, s in enumerate(slides, 1)}
key_start = pages_by_title['Where did the round key come from?']
key_end = pages_by_title['Recover the six key bits we used']
first_round = slides[pages_by_title['What enters the first Feistel round?'] - 1]
first_round['blocks'].insert(2, P(
 f'(We derive this key from the master key on slides {key_start}–{key_end}.)'))

# Make the classroom example's appendix reference navigable in the exported PDF.
first_worked = appendix.index(FEISTEL_APPENDIX[0]) + 1
example = next(s for s in slides if s['title'] == 'Two rounds: follow encryption and decryption')
example['jump_page'] = MAIN_COUNT + first_worked
example['take'] = (f'Decrypt with K₂, then K₁. See appendix A{first_worked}–A{first_worked + 1} '
                   'for every AND, XOR, and final swap.')

sbox_page = appendix.index(DES_SBOX_APPENDIX[0]) + 1
sbox_example = next(s for s in slides if s['title'] == 'Where does that first 5 go?')
sbox_example['jump_page'] = MAIN_COUNT + sbox_page
sbox_example['take'] = (f'See appendix A{sbox_page} for all eight calculations, from the expansion '
                        'and key bits to each S-box output.')

assert len([r for r in SESSION_PLAN if r['kind']=='break'])==2
assert sum(r['minutes'] for r in SESSION_PLAN)==210
assert sum(s['minutes'] for s in slides[:MAIN_COUNT])>209.9999
