exec(open('lab.py').read())
import numpy as np
P=np.array([[bin(u&l).count('1')%2 for l in lab] for u in range(512)],dtype=np.uint8)  # P[u,t]=<u,l_t>
Z=(P==0)
# max lines in a k-flat (k=6,7): annihilator of (9-k)-dim dual subspace
def maxflat(cod):
  best=0
  if cod==2:
    for u in range(1,512):
      for v in range(u+1,512):
        best=max(best,int((Z[u]&Z[v]&Z[u^v]).sum()))
  else:
    pairs=[(u,v) for u in range(1,512) for v in range(u+1,512)]
    for u in range(1,512):
      for v in range(u+1,512):
        zz=Z[u]&Z[v]
        if zz.sum()<=best: continue
        for w in range(v+1,512):
          if w==(u^v): continue
          c=int((zz&Z[w]).sum())
          if c>best: best=c
  return best
print("max lines in 7-flat",maxflat(2))
print("max lines in 6-flat",maxflat(3))
for p in (8,9):
  for ch in chains(p):
    c=classify(ch)
    nd=[needA(t,ch) for t in L]
    # minimal J patterns: for line t, coordinates k in every minimal J (g-value not the majority value)
    out=[]
    for a in range(p):
      A=[i for i,t in enumerate(L) if nd[i]>0 and (lambda g:(g[a]!=max(set(g),key=g.count) and g.count(max(set(g),key=g.count))>p-nd[i]-1))(gvec(t,ch))]
      out.append((len(A),rk2([lab[i] for i in A])))
    print(p,c,out[:3],"...")
    if p==9 or c==1: pass
  
