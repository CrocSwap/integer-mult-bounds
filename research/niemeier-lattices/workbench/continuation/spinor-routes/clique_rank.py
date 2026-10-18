from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
D=14;N=1<<D
p=OUT/'CLIQUE-LEADING.json'; data=json.loads(p.read_text());support=data['kernel_support']
v=[int(i in set(support))for i in range(N)]
for bit in range(D):
 for i in range(N):
  if not i>>bit&1:v[i]^=v[i|(1<<bit)]
print('degree census',{k:sum(c and i.bit_count()==k for i,c in enumerate(v))for k in range(15)},flush=True)
first=sum(1<<i for i in support)
masks=[]
for bit in range(D):
 shift=1<<bit;mask=sum(((1<<shift)-1)<<start for start in range(0,N,2*shift));masks.append((shift,mask))
basis={}
for x in range(N):
 row=first
 for bit,(shift,mask)in enumerate(masks):
  if x>>bit&1:row=((row&mask)<<shift)|((row>>shift)&mask)
 while row:
  q=row.bit_length()-1
  if q in basis:row^=basis[q]
  else:basis[q]=row;break
 if x%1024==0:print(x,len(basis),flush=True)
data['binary_rank']=len(basis);data['degree_census']={k:sum(c and i.bit_count()==k for i,c in enumerate(v))for k in range(15)}
p.write_text(json.dumps(data)+'\n');print('FINAL',len(basis))
