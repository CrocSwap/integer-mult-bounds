from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,gzip,hashlib,copy,sys,math
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
src,out=args.input,args.out;w=json.loads(gzip.decompress(src.read_bytes()));V=w['v'];N=2*V+w['R'];old=copy.deepcopy(w)
assert hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()=='cb9c80a62d75c5dfc8bc8933d4b1d44e6b6b816db47c2444bc2dbba6b3a6e454'
H=[0]*N
for i in range(V):H[V+i]=1<<i
for f,t,S in reversed(w['B']):
 for s in S:H[s]^=H[t]
for t,S in enumerate(w['scatter']):
 for k in S:H[w['ret'][k]]^=H[V+t]
remove=[]
for i in range(len(w['A'])-1,-1,-1):
 f,t,S=w['A'][i]
 if H[t]==0:remove.append(i)
 for s in S:H[s]^=H[t]
w['A']=[e for i,e in enumerate(w['A'])if i not in set(remove)]
w['C']=[[1,t,list(S)]for f,t,S in reversed(w['A'])]
# Independently compute exact rational row bases and subspace nesting.
def basis(vecs):
 B={}
 for rr in vecs:
  row=list(map(Q,rr))
  for c in sorted(B):
   q=row[c];row=[a-q*b for a,b in zip(row,B[c])]
  c=next((i for i,x in enumerate(row)if x),None)
  if c is not None:
   q=row[c];B[c]=[x/q for x in row]
 return B
FB=[basis(w['lines'][i]for i in f)for f in w['frames']];dim=list(map(len,FB));cache={}
def sub(a,b):
 if (a,b)not in cache:cache[a,b]=len(basis(list(FB[a].values())+list(FB[b].values())))==dim[b]
 return cache[a,b]
def replay(z):
 val=[1<<i for i in range(N)];cur=list(z['start']);H=Counter();tops=[]
 def climb(r,f):
  a=cur[r];assert sub(a,f),(r,a,f)
  if dim[f]>dim[a]:H[dim[f]-dim[a]]+=1
  cur[r]=f
 def gates(sec):
  for f,t,ss in z[sec]:
   assert len({t,*ss})==1+len(ss)
   for r in [t,*ss]:climb(r,f)
   for s in ss:val[t]^=val[s]
 gates('D');gates('A');tops.extend(dim[cur[q]]for q in z['ret']);snap=[val[q]for q in z['ret']]
 for t,ks in enumerate(z['scatter']):
  for k in ks:val[V+t]^=snap[k]
 gates('B');gates('C')
 for r,f in enumerate(z['final']):climb(r,f)
 for r in range(N):assert val[r]==((1<<r)^(1<<(r-V))if V<=r<2*V else 1<<r),r
 return H,tops

h0,c0=replay(old);h1,c1=replay(w);assert len(remove)==227 and h0==h1 and c0==c1==[8]*9;print('before',dict(h0),'copies',c0);print('after',dict(h1),'copies',c1);print('mass',sum(k*v for k,v in h1.items()),'deltaMoment',sum((h1[k]-h0[k])*k**.9984 for k in set(h0)|set(h1)))
out.mkdir(parents=True,exist_ok=False);data=json.dumps(w,sort_keys=True,separators=(',',':')).encode();z=gzip.compress(data,compresslevel=9,mtime=0);z=z[:9]+bytes([255])+z[10:];(out/'WORD.json.gz').write_bytes(z)
r={'removed':remove,'before':dict(h0),'after':dict(h1),'retained_copies_before':c0,'retained_copies_after':c1,'word_sha256':hashlib.sha256(z).hexdigest(),'all_dirty_columns':N,'scope':'Exact GF2 scalar endpoint and rational frame chains; native/global/costchecks stillneeded.'};(out/'REVIEW.json').write_text(json.dumps(r,indent=2)+'\n')
