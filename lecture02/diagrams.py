"""Vector-only lecture illustrations; coordinates are local, measured from the top."""
from math import log2
from reportlab.lib import colors

NAVY=colors.HexColor('#132B3C');TEAL=colors.HexColor('#087E83');CORAL=colors.HexColor('#D85C36')
LIGHT=colors.HexColor('#E5EEED');INK=colors.HexColor('#183342');MUTED=colors.HexColor('#536875');WHITE=colors.white

def text(c,x,y,s,size=15,bold=False,color=INK,center=False,mono=False):
 c.setFont('Mono' if mono else 'Bold' if bold else 'Sans',size);c.setFillColor(color)
 (c.drawCentredString if center else c.drawString)(x,-y,s)
def box(c,x,y,w,h,title,subtitle='',accent=False):
 c.setFillColor(TEAL if accent else LIGHT);c.roundRect(x,-y-h,w,h,7,fill=1,stroke=0)
 text(c,x+w/2,y+(h/2+5 if not subtitle else h/2-5),title,16,True,WHITE if accent else INK,True)
 if subtitle:text(c,x+w/2,y+h/2+18,subtitle,12,color=WHITE if accent else MUTED,center=True)
def line(c,x1,y1,x2,y2,color=CORAL,width=1.6):
 c.setStrokeColor(color);c.setLineWidth(width);c.line(x1,-y1,x2,-y2)
def arrow(c,x1,y1,x2,y2,color=CORAL,width=1.6):
 from math import atan2,cos,sin,pi
 line(c,x1,y1,x2,y2,color,width);a=atan2(y2-y1,x2-x1)
 for side in [-1,1]:line(c,x2,y2,x2-7*cos(a+side*pi/6),y2-7*sin(a+side*pi/6),color,width)
def xor(c,x,y,r=12):
 c.setStrokeColor(TEAL);c.setLineWidth(1.7);c.circle(x,-y,r,stroke=1,fill=0)
 line(c,x-r+4,y,x+r-4,y,TEAL);line(c,x,y-r+4,x,y+r-4,TEAL)

def draw(c,name,options,x,y,w):
 c.saveState();c.translate(x,y)
 if name=='otp_compatibility':
  cc=int(options.get('ciphertext','10'),2);cw=w/4
  for j,p in enumerate(range(4)):
   xx=j*cw+5
   box(c,xx,9,cw-10,156,f'p = {p:02b}',f'k = {p^cc:02b}')
   text(c,xx+(cw-10)/2,130,f'p XOR k = {cc:02b}',15,color=TEAL,center=True,mono=True)
  text(c,w/2,199,'Every candidate message has exactly one compatible 2-bit key.',16,center=True)
  h=220
 elif name=='dice_grid':
  cell=29;gx=102;gy=33
  text(c,190,11,'Die 2',11,True,TEAL,True);text(c,0,125,'Die 1',11,True,TEAL)
  for j in range(6):text(c,gx+(j+.5)*cell,29,str(j+1),11,center=True)
  for i in range(6):
   text(c,gx-15,gy+(i+.65)*cell,str(i+1),11,center=True)
   for j in range(6):
    match=i+j+2==4;double=i==j
    c.setFillColor(CORAL if match else LIGHT);c.roundRect(gx+j*cell+1,-gy-(i+1)*cell+1,cell-2,cell-2,3,fill=1,stroke=0)
    if double:c.setStrokeColor(TEAL);c.setLineWidth(2);c.roundRect(gx+j*cell+3,-gy-(i+1)*cell+3,cell-6,cell-6,2,fill=0,stroke=1)
    text(c,gx+(j+.5)*cell,gy+(i+.65)*cell,str(i+j+2),11,color=WHITE if match else INK,center=True)
  box(c,362,36,w-367,52,'36 equally likely outcomes')
  text(c,380,123,'Coral: sum is 4 → three outcomes',15,color=CORAL)
  text(c,380,157,'Teal border: a double → six outcomes',15,color=TEAL)
  text(c,380,191,'Both events: (2, 2) → one outcome',15)
  h=224
 elif name=='entropy_bars':
  ps=options.get('probabilities',[.5,.7,1.0]);gap=44;cw=(w-gap*2)/3
  for j,p in enumerate(ps):
   ent=-sum(q*log2(q) for q in (p,1-p) if q);xx=j*(cw+gap)
   text(c,xx+cw/2,20,f'Pr[heads] = {p:g}',16,True,center=True)
   c.setFillColor(LIGHT);c.roundRect(xx+30,-171,cw-60,125,4,fill=1,stroke=0)
   if ent:c.setFillColor(TEAL if j==0 else CORAL);c.roundRect(xx+30,-171,cw-60,125*ent,4,fill=1,stroke=0)
   text(c,xx+cw/2,199,f'H = {ent:.3f} bits',17,True,center=True)
  h=222
 elif name=='block_box':
  cw=150;gap=(w-5*cw)/4
  for i,(a,b) in enumerate([('Plaintext','n bits'),('Eₖ','encrypt'),('Ciphertext','n bits'),('Dₖ','decrypt'),('Plaintext','n bits')]):
   xx=i*(cw+gap);box(c,xx,18,cw,72,a,b,i in (1,3))
   if i<4:arrow(c,xx+cw+2,54,xx+cw+gap-2,54)
  h=116
 elif name=='rounds':
  gap=26;cw=(w-3*gap)/4
  for i in range(4):
   xx=i*(cw+gap);label=['Round 1','Round 2','…','Round r'][i]
   box(c,xx,65,cw,70,label,'state → state',True)
   if i<3:arrow(c,xx+cw+3,100,xx+cw+gap-3,100)
   if i!=2:text(c,xx+cw/2,38,['K₁','K₂','','Kᵣ'][i],16,center=True);arrow(c,xx+cw/2,43,xx+cw/2,61)
  text(c,w/2,10,'Master key K → key schedule → round keys',14,True,TEAL,True)
  h=157
 elif name=='toy_spn':
  gap=30;cw=(w-2*gap)/3
  for i in range(3):
   xx=i*(cw+gap);box(c,xx,20,cw,145,'');text(c,xx+cw/2,58,f'Round {i+1}',18,True,center=True)
   text(c,xx+cw/2,103,f'XOR K{i} → four S-boxes',14,center=True)
   text(c,xx+cw/2,136,'Bit permutation P' if i<2 else 'Then XOR K3',14,color=TEAL,center=True)
   if i<2:arrow(c,xx+cw+4,85,xx+cw+gap-4,85)
  text(c,0,198,'16-bit plaintext',13,True);text(c,w,198,'16-bit ciphertext',13,True,center=False) if False else None
  text(c,w-70,198,'16-bit ciphertext',13,True,center=True)
  h=220
 elif name=='toy_sbox_lookup':
  value=int(options.get('value',0x28A0));sbox=list(options['sbox'])
  if not 0<=value<1<<16 or len(sbox)!=16 or any(not isinstance(v,int) or not 0<=v<16 for v in sbox):
   raise ValueError('A toy lookup needs a 16-bit input and sixteen 4-bit S-box outputs')
  digits=[(value>>shift)&15 for shift in (12,8,4,0)];selected=set(digits)
  gutter=116;cw=(w-gutter)/16
  text(c,0,36,'Input digit',12,True,TEAL)
  text(c,0,73,'S-box output',12,True,TEAL)
  for digit in range(16):
   xx=gutter+digit*cw
   for row,val in enumerate((digit,sbox[digit])):
    yy=13+row*37;chosen=digit in selected
    c.setFillColor((TEAL if row==0 else CORAL) if chosen else LIGHT)
    c.roundRect(xx+1,-yy-33,cw-2,33,3,fill=1,stroke=0)
    text(c,xx+cw/2,yy+23,f'{val:X}',16,True,WHITE if chosen else INK,True,True)
  text(c,0,110,'Read the four lookups in the order of the input digits',13,True,TEAL)
  gap=20;cardw=(w-3*gap)/4
  for i,digit in enumerate(digits):
   xx=i*(cardw+gap)
   c.setFillColor(LIGHT);c.roundRect(xx,-126-64,cardw,64,6,fill=1,stroke=0)
   text(c,xx+cardw/2,146,f'Input digit {i+1}',11,color=MUTED,center=True)
   text(c,xx+cardw/2,177,f'{digit:X} → {sbox[digit]:X}',23,True,INK,True,True)
  h=202
 elif name=='toy_bit_positions':
  value=int(options.get('value',0xD36E));positions=list(options.get('positions',[1,5,9,13]))
  if not 0<=value<1<<16 or len(positions)!=4 or any(not isinstance(v,int) or not 1<=v<=16 for v in positions):
   raise ValueError('A toy bit-copy diagram needs a 16-bit input and four positions numbered 1–16')
  bits=[(value>>(15-i))&1 for i in range(16)];selected=set(positions)
  gutter=132;gap=12;cw=(w-gutter-3*gap)/16;groupw=4*cw
  def input_center(position):
   i=position-1
   return gutter+(i//4)*(groupw+gap)+(i%4+.5)*cw
  text(c,0,31,'Hex digit',13,True,TEAL)
  text(c,0,73,'Input position',12,True,TEAL)
  text(c,0,111,'Input bit',13,True,TEAL)
  for group,digit in enumerate(f'{value:04X}'):
   xx=gutter+group*(groupw+gap)
   c.setFillColor(NAVY);c.roundRect(xx+1,-8-33,groupw-2,33,4,fill=1,stroke=0)
   text(c,xx+groupw/2,32,digit,21,True,WHITE,True,True)
  for i,bit in enumerate(bits):
   position=i+1;xx=input_center(position)-cw/2;chosen=position in selected
   c.setFillColor(TEAL if chosen else LIGHT);c.roundRect(xx+1,-52-28,cw-2,28,3,fill=1,stroke=0)
   text(c,xx+cw/2,72,str(position),12,True if chosen else False,WHITE if chosen else INK,True,True)
   c.setFillColor(CORAL if chosen else LIGHT);c.roundRect(xx+1,-87-35,cw-2,35,3,fill=1,stroke=0)
   text(c,xx+cw/2,112,str(bit),21,True,WHITE if chosen else INK,True,True)
  text(c,0,195,'Output bit',13,True,TEAL)
  copied=[]
  for j,position in enumerate(positions):
   cx=gutter+j*(groupw+gap)+groupw/2;bit=bits[position-1];copied.append(str(bit))
   arrow(c,input_center(position),125,cx,146,CORAL,1.6)
   text(c,cx,164,f'position {j+1}',11,True,TEAL,True)
   c.setFillColor(LIGHT);c.roundRect(cx-29,-174-34,58,34,4,fill=1,stroke=0)
   text(c,cx,199,str(bit),22,True,INK,True,True)
  text(c,w/2,231,'Output bits 1–4 = '+''.join(copied),15,True,TEAL,True)
  h=235
 elif name=='feistel_round':
  lx=w*.22;rx=w*.78;fx=w*.51
  box(c,lx-88,0,176,38,'Lᵢ₋₁');box(c,rx-88,0,176,38,'Rᵢ₋₁')
  line(c,lx,38,lx,138,TEAL);line(c,rx,38,rx,153,TEAL)
  box(c,fx-65,65,130,49,'F',accent=True)
  arrow(c,rx,88,fx+68,88,TEAL);arrow(c,fx,44,fx,61)
  text(c,fx,35,'Kᵢ',15,center=True)
  line(c,fx,114,fx,150,TEAL);arrow(c,fx,150,lx+16,150,TEAL)
  xor(c,lx,150);c.setFillColor(TEAL);c.circle(rx,-88,3,fill=1,stroke=0)
  arrow(c,lx,164,rx,213,TEAL);arrow(c,rx,153,lx,213,TEAL)
  box(c,lx-88,218,176,38,'Lᵢ = Rᵢ₋₁');box(c,rx-116,218,232,38,'Rᵢ = Lᵢ₋₁ XOR F')
  h=269
 elif name=='des_lookup':
  table=options['table'];value=int(options.get('value',24))
  if not 0<=value<64 or len(table)!=4 or any(len(row)!=16 for row in table):
   raise ValueError('A DES lookup needs a six-bit input and a 4 × 16 S-box table')
  bits=f'{value:06b}';outer=bits[0]+bits[-1];inner=bits[1:5]
  row=int(outer,2);col=int(inner,2);result=table[row][col]
  text(c,0,22,'6-bit input',12,True,TEAL)
  text(c,102,24,bits[0],22,True,CORAL,True,True)
  text(c,129,24,'|',20,color=MUTED,center=True,mono=True)
  text(c,177,24,inner,22,True,TEAL,True,True)
  text(c,226,24,'|',20,color=MUTED,center=True,mono=True)
  text(c,253,24,bits[-1],22,True,CORAL,True,True)
  text(c,302,22,f'Outer {outer} → row {row}',13,True,CORAL)
  text(c,541,22,f'Inner {inner} → column {col}',13,True,TEAL)
  gutter=44;cw=(w-gutter)/16;headh=25;top=54;body=82;ch=26
  text(c,gutter,47,'Column index (decimal)',10,True,TEAL)
  text(c,0,77,'Row',10,True,TEAL)
  for j in range(16):
   xx=gutter+j*cw;c.setFillColor(TEAL if j==col else NAVY)
   c.roundRect(xx+1,-top-headh,cw-2,headh,2,fill=1,stroke=0)
   text(c,xx+cw/2,top+18,str(j),12,True,WHITE,True,True)
  for i,entries in enumerate(table):
   yy=body+i*ch;c.setFillColor(CORAL if i==row else NAVY)
   c.roundRect(1,-yy-ch+1,gutter-4,ch-2,2,fill=1,stroke=0)
   text(c,(gutter-2)/2,yy+18,str(i),13,True,WHITE,True,True)
   for j,val in enumerate(entries):
    xx=gutter+j*cw;chosen=i==row and j==col
    c.setFillColor(CORAL if chosen else LIGHT if i%2==0 else colors.HexColor('#EFF2EF'))
    c.roundRect(xx+1,-yy-ch+1,cw-2,ch-2,2,fill=1,stroke=0)
    text(c,xx+cw/2,yy+18,str(val),14,chosen,WHITE if chosen else INK,True,True)
  text(c,w/2,216,f'Table entry = {result} (decimal) → output {result:04b}',16,True,TEAL,True)
  h=225
 elif name=='des_stage':
  active=int(options.get('active',0))
  if active not in range(4):raise ValueError('DES stage index must be 0, 1, 2, or 3')
  labels=['1. Expand','2. XOR with key','3. S-box lookups','4. Permute bits'];gap=20;cw=(w-3*gap)/4
  for i,label in enumerate(labels):
   xx=i*(cw+gap);chosen=i==active
   c.setFillColor(TEAL if chosen else LIGHT);c.roundRect(xx,-3-34,cw,34,5,fill=1,stroke=0)
   text(c,xx+cw/2,25,label,14,True,WHITE if chosen else MUTED,True)
   if i<3:arrow(c,xx+cw+2,20,xx+cw+gap-2,20,MUTED,1.2)
  h=43
 elif name=='des_overview':
  gap=20;cw=(w-4*gap)/5
  labels=[('IP','64 → 64'),('16 Feistel rounds','Round keys K₁ … K₁₆'),('Swap halves','R₁₆ || L₁₆'),('IP⁻¹','64 → 64'),('Ciphertext','64 bits')]
  for i,(a,b) in enumerate(labels):
   xx=i*(cw+gap);chosen=i==1
   c.setFillColor(TEAL if chosen else LIGHT);c.roundRect(xx,-42-85,cw,85,7,fill=1,stroke=0)
   text(c,xx+cw/2,79,a,14 if chosen else 16,True,WHITE if chosen else INK,True)
   text(c,xx+cw/2,103,b,11 if chosen else 12,color=WHITE if chosen else MUTED,center=True)
   if i<4:arrow(c,xx+cw+2,84,xx+cw+gap-2,84)
  text(c,0,18,'64-bit plaintext enters IP',13,True,TEAL)
  text(c,w/2,163,'IP and IP⁻¹ are public, fixed bit permutations.',15,center=True)
  h=186
 elif name=='des_f':
  gap=24;cw=(w-3*gap)/4
  labels=[('Expand E','32 → 48 bits'),('XOR Kᵢ','48 → 48 bits'),('S₁ … S₈','48 → 32 bits'),('Permute P','32 → 32 bits')]
  for i,(a,b) in enumerate(labels):
   xx=i*(cw+gap);box(c,xx,57,cw,91,a,b,i==2)
   if i<3:arrow(c,xx+cw+3,102,xx+cw+gap-3,102)
  xx=cw+gap+cw/2;text(c,xx,20,'48-bit round key Kᵢ',13,True,TEAL,True);arrow(c,xx,27,xx,52)
  text(c,w/2,187,'Each S-box receives 6 bits and outputs 4 bits.',15,center=True)
  h=210
 elif name=='key_schedule':
  gap=24;cw=(w-3*gap)/4
  for i,(a,b) in enumerate([('PC1','64 → 56 bits'),('Split','C₀, D₀: 28 bits each'),('Rotate','1 or 2 positions'),('PC2','56 → 48 bits')]):
   xx=i*(cw+gap);box(c,xx,46,cw,87,a,b,i==2)
   if i<3:arrow(c,xx+cw+3,89,xx+cw+gap-3,89)
  text(c,0,20,'64-bit key representation (includes 8 parity bits)',13,True,TEAL)
  text(c,w/2,178,'Rotate C and D separately each round; PC2 selects the round key.',15,center=True)
  h=202
 elif name=='ede':
  decrypt=options.get('decrypt',False);cw=190;gap=(w-3*cw)/2
  for i,(a,b) in enumerate(([('D K₃','DES decrypt'),('E K₂','DES encrypt'),('D K₁','DES decrypt')] if decrypt else [('E K₁','DES encrypt'),('D K₂','DES decrypt'),('E K₃','DES encrypt')])):
   xx=i*(cw+gap);box(c,xx,34,cw,90,a,b,i!=1)
   if i<2:arrow(c,xx+cw+3,80,xx+cw+gap-3,80)
  text(c,w/2,163,'Three DES operations on the same 64-bit block.',15,center=True)
  h=184
 elif name=='bit_table':
  values=options['table'];label=options.get('label','');desired=options.get('height',None)
  nested=bool(values and isinstance(values[0],(list,tuple)))
  if nested:
   rows=values;cols=len(rows[0]);headers=options.get('column_headers',False);rowheads=options.get('row_headers',False)
   hh=desired or 137;labelh=22 if label else 0;headh=18 if headers else 0;bodyh=hh-labelh-headh-10;ch=bodyh/len(rows)
   gutter=28 if rowheads else 0;cw=(w-gutter)/cols
   if label:text(c,0,14,label,12,True,TEAL)
   if headers:
    for j in range(cols):text(c,gutter+(j+.5)*cw,labelh+13,str(j),9,True,TEAL,True,True)
   for i,row in enumerate(rows):
    yy=labelh+headh+i*ch
    if rowheads:text(c,10,yy+ch/2+3,str(i),10,True,TEAL,True)
    for j,val in enumerate(row):
     xx=gutter+j*cw;c.setFillColor(LIGHT if i%2==0 else colors.HexColor('#EFF2EF'));c.rect(xx+1,-yy-ch+1,cw-2,ch-2,stroke=0,fill=1)
     text(c,xx+cw/2,yy+ch/2+3,str(val),10,center=True,mono=True)
   h=hh
  else:
   cols=options.get('cols',8);nr=(len(values)+cols-1)//cols;hh=desired or nr*29+34
   labeled_ranges=options.get('output_ranges',False)
   gutter=84 if labeled_ranges else 0
   labelh=25 if label else 0
   if label:text(c,0,14,label,15 if labeled_ranges else 12,True,TEAL)
   if labeled_ranges:
    text(c,gutter/2,labelh+12,'Output bits',12,True,NAVY,True)
    text(c,(w+gutter)/2,labelh+12,'Input positions to copy',12,True,NAVY,True)
    labelh+=21
   ch=(hh-labelh-10)/nr;cw=(w-gutter)/cols
   for j,val in enumerate(values):
    r,col=divmod(j,cols);xx=gutter+col*cw;yy=labelh+r*ch
    highlighted=r==options.get('highlight_row')
    if labeled_ranges and col==0:
     text(c,gutter/2,yy+ch/2+4,f'{j+1}–{min(j+cols,len(values))}',13,True,TEAL if highlighted else INK,True)
    c.setFillColor(TEAL if highlighted else LIGHT);c.rect(xx+1,-yy-ch+1,cw-2,ch-2,stroke=0,fill=1)
    text(c,xx+cw/2,yy+ch/2+(5 if labeled_ranges else 4),str(val),17 if labeled_ranges else 12,
         highlighted,WHITE if highlighted else INK,True)
   h=hh
 else:raise ValueError(f'Unknown diagram {name}')
 c.restoreState();return h
