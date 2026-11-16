# KILL-A8 impl C data: own E8 build (doubled coords), labels = (coords mod 2 in a lattice basis, 1) in F2^9,
# maximal 7-flat masks (2 independent F2^9 functionals), A_{P-1} chain pair roots and their Off sets. Writes dat_P.txt
import itertools, sys
from fractions import Fraction as Fr
P=int(sys.argv[1])
R=[]
for i,j in itertools.combinations(range(8),2):
  for s in (2,-2):
    for u in (2,-2):
      v=[0]*8; v[i]=s; v[j]=u; R.append(tuple(v))
for sg in itertools.product((1,-1),repeat=8):
  if sg.count(-1)%2==0: R.append(sg)
assert len(R)==240
ip=lambda a,b: sum(x*y for x,y in zip(a,b))//4
canon=lambda v: v if next(x for x in v if x)>0 else tuple(-x for x in v)
L=sorted({canon(r) for r in R}); idx={l:i for i,l in enumerate(L)}
# lattice basis: e1-e2..e6-e7 (doubled), e6+e7, half vector (-1/2)(1..1)  [Dynkin E8 basis, Bourbaki-free variant]
Bc=[[2 if k==i else -2 if k==i+1 else 0 for k in range(8)] for i in range(6)]+[[0]*5+[2,2,0],[-1]*8]
def coords(v):
  M=[[Fr(Bc[j][i]) for j in range(8)]+[Fr(v[i])] for i in range(8)]
  for c in range(8):
    p=next(r for r in range(c,8) if M[r][c]!=0); M[c],M[p]=M[p],M[c]; M[c]=[x/M[c][c] for x in M[c]]
    for r in range(8):
      if r!=c and M[r][c]!=0: M[r]=[x-M[r][c]*y for x,y in zip(M[r],M[c])]
  return [M[i][8] for i in range(8)]
lab=[]
for l in L:
  ci=coords(l); assert all(x.denominator==1 for x in ci)
  lab.append(sum((int(x)%2)<<k for k,x in enumerate(ci))|(1<<8))
assert len(set(lab))==120
def rk(vs):
  b=[]
  for v in vs:
    for y in b: v=min(v,v^y)
    if v: b.append(v)
  return len(b)
assert rk(lab)==9
par=lambda x: bin(x).count('1')&1
ms=set()
for f in range(1,512):
  for g in range(f+1,512):
    ms.add(sum(1<<t for t in range(120) if not par(f&lab[t]) and not par(g&lab[t])))
ml=sorted(ms,key=lambda v:-bin(v).count('1')); mx=[]
for v in ml:
  if not any(v&w==v for w in mx): mx.append(v)
# chain: greedy A_{P-1}
ch=[R[0]]
while len(ch)<P-1:
  ch.append(next(r for r in R if ip(r,ch[-1])==-1 and all(ip(r,c)==0 for c in ch[:-1])))
pairs=[(a,b) for a in range(P) for b in range(a+1,P)]
off=[]
for a,b in pairs:
  h=tuple(sum(c[k] for c in ch[a:b]) for k in range(8)); assert ip(h,h)==2
  off.append(sum(1<<t for t in range(120) if ip(L[t],h)!=0))
print('masks',len(mx),'sizes',sorted({bin(v).count('1') for v in mx}),'off',[bin(o).count('1') for o in off],file=sys.stderr)
with open('dat_%d.txt'%P,'w') as f:
  f.write('%d %d\n'%(P,len(mx))); f.write(' '.join(map(str,lab))+'\n')
  w=lambda v: f.write('%d %d\n'%(v&((1<<64)-1),v>>64))
  for o in off: w(o)
  for v in mx: w(v)
