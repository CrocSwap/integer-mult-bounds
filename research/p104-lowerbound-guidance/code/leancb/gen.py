import re,sys,json,itertools
src=open('<research-tree>/lean/decoder-duality/Nov15/LinP104Base.lean').read()
def lst(name):
    m=re.search(r'def '+name+r' : List Nat := \[([^\]]*)\]',src); return [int(x) for x in m.group(1).split(',')]
X=lst('xMasks'); BM=lst('bmMasks')
bit=lambda m,i:(m>>i)&1
def Bf(x,y): # sum_j sum_i B_ji x_i y_j
    return sum(bit(BM[j],i)*bit(x,i)*bit(y,j) for j in range(8) for i in range(8))%2
cells=[(t,s) for t in range(104) for s in range(104) if Bf(X[t],X[s])==0]
print(len(cells))
def vec(t,s):
    v=0
    for a in range(8):
        for b in range(8):
            if bit(X[t],a) and bit(X[s],b): v|=1<<(a*8+b)
    return v
# greedy elimination with combination tracking
basis={}  # pivot -> (vec, combo mask over selected list idx)
sel=[]
import random
random.seed(1)
cl=cells[:]; random.shuffle(cl)
for (t,s) in cl:
    v=vec(t,s); idx=len(sel); comb=1<<idx
    while v:
        p=v.bit_length()-1
        if p in basis:
            bv,bc=basis[p]; v^=bv; comb^=bc
        else:
            basis[p]=(v,comb); sel.append((t,s)); break
    if len(sel)==64: break
print('rank',len(sel))
# find (i0,j0) with B=1
i0,j0=next((i,j) for i in range(8) for j in range(8) if bit(BM[i],j))
print('i0j0',i0,j0)
def solve(target):
    v=target; comb=0
    while v:
        p=v.bit_length()-1
        if p not in basis: return None
        bv,bc=basis[p]; v^=bv; comb^=bc
    return comb
lam=[]
for i in range(8):
    for j in range(8):
        tg=(1<<(i*8+j)) ^ ((1<<(i0*8+j0)) if bit(BM[i],j) else 0)
        c=solve(tg)
        assert c is not None,(i,j)
        lam.append(c)
print('nsel',len(sel))
json.dump({'sel':sel,'lam':lam,'i0':i0,'j0':j0},open('kern.json','w'))
# dependent pairwise-orthogonal set
labs=range(104)
orth=lambda a,b:Bf(X[a],X[b])==0
found=None
for a in range(104):
  for b in range(a+1,104):
    if not orth(a,b): continue
    for c in range(b+1,104):
      if not (orth(a,c) and orth(b,c)): continue
      d=X[a]^X[b]^X[c]
      if d in X:
        dd=X.index(d)
        if dd>c and orth(a,dd) and orth(b,dd) and orth(c,dd):
          found=(a,b,c,dd);break
    if found:break
  if found:break
print('dep4',found)
json.dump(found,open('dep.json','w'))
