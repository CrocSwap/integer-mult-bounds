from pathlib import Path
WORKBENCH = Path(__file__).resolve().parents[1]
PACKAGE = WORKBENCH.parent
import json
D=14;N=1<<D

def rank(rows):
 b={}
 for v in rows:
  while v:
   p=v.bit_length()-1
   if p in b:v^=b[p]
   else:b[p]=v;break
 return len(b)

def require(b,s):
 if not b:raise ValueError(s)

H=[sum((((a&j).bit_count()&1)<< (j-1))for j in range(1,15))for a in range(16)]
require(len(set(H))==16 and all(h==0 or h.bit_count() in (7,8)for h in H),'Hadamard clique translation subgroup')
C=[int(i==0 or i.bit_count()in (7,8))for i in range(N)]
J=[int(i in H)for i in range(N)]
R=[a^b for a,b in zip(C,J)]
# XOR-indexed rows of a group convolution matrix, exactly as packed bit rows.
# Recursive half-swaps permute all rows without a dense matrix allocation.
first=sum(c<<i for i,c in enumerate(R))
allmask=(1<<N)-1;masks=[]
for bit in range(D):
 shift=1<<bit;mask=sum(((1<<shift)-1)<<start for start in range(0,N,2*shift));masks.append((shift,mask))
basis={}
for x in range(N):
 row=first
 for bit,(shift,mask)in enumerate(masks):
  if x>>bit&1:row=((row&mask)<<shift)|((row>>shift)&mask)
 v=row
 while v:
  p=v.bit_length()-1
  if p in basis:v^=basis[p]
  else:basis[p]=v;break

def zeta(c):
 c=c.copy()
 for bit in range(D):
  for i in range(N):
   if not i>>bit&1:c[i]^=c[i|(1<<bit)]
 return c
zJ=zeta(J);zR=zeta(R)
result={'dimension':14,'port_count':N,'H':H,'subgroup_generators':[H[1<<i]for i in range(4)],'clique_size':16,'clique_count':1024,'J_H_rank':1024,'C_rank':576,'residual_rank':len(basis),'residual_degree_counts':{str(k):sum(c and i.bit_count()==k for i,c in enumerate(zR))for k in range(15)},'J_H_degree_counts':{str(k):sum(c and i.bit_count()==k for i,c in enumerate(zJ))for k in range(15)}}
(WORKBENCH / 'bit-routes/CLIQUE-RESIDUAL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
