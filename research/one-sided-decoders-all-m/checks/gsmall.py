# exact g(d) for d<=6 via codim-3 flats then extra hyperplanes; P112 labels
from base import *
par=lambda x: bin(x).count('1')&1
mask={z:sum(1<<t for t in range(v) if not par(z&LAB[t])) for z in range(1,512)}
pc=lambda m: bin(m).count('1')
# dim-6 flats with >=8 lines
seen=set(); F6=[]
for a in range(1,512):
  for b in range(a+1,512):
    mab=mask[a]&mask[b]
    if pc(mab)<8: continue
    for c in range(b+1,512):
      if c==a^b: continue
      m=mab&mask[c]
      if pc(m)>=8: F6.append(m)
F6=list(set(F6)); print('6-flats >=8 lines (distinct line sets)',len(F6),'max',max(map(pc,F6)))
g5=0;g4=0
for m in F6:
  for z in range(1,512):
    k=pc(m&mask[z])
    if k>g5 and (m&mask[z])!=m: g5=k
print('g(5) >=',g5)
def rk(m): return f2rank([LAB[t] for t in range(v) if m>>t&1])
best={}
for m in F6:
  r=rk(m); best[r]=max(best.get(r,0),pc(m))
print('F6 sets by label rank: max lines',best)
g=dict(best)
for m in F6:
  if pc(m)<=g.get(5,0): continue
  for z in range(1,512):
    mm=m&mask[z]
    if pc(mm)>g.get(5,0) and rk(mm)<=5: g[5]=pc(mm)
print('g(5)=',g.get(5))
