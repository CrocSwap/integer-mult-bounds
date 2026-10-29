# impl B (independent of lf/lab/tight): Bourbaki E8, A8 = roots with alpha2-coeff in {0,+-3}, labels <r,alpha_i> mod 2,
# need via orthogonality to A8 roots on the complement, 6-flats via numpy over dual 3-subspaces (dedupe by kernel), sigma0 relief bound.
import numpy as np, itertools
h=0.5
S=np.array([[h,-h,-h,-h,-h,-h,-h,h],[1,1,0,0,0,0,0,0],[-1,1,0,0,0,0,0,0],[0,-1,1,0,0,0,0,0],[0,0,-1,1,0,0,0,0],[0,0,0,-1,1,0,0,0],[0,0,0,0,-1,1,0,0],[0,0,0,0,0,-1,1,0]])
roots={tuple(r) for r in S}; frontier=list(roots)
while frontier:
  new=[]
  for r in frontier:
    r=np.array(r)
    for a in S:
      q=tuple(r-np.dot(r,a)*a)
      if q not in roots: roots.add(q); new.append(q)
  frontier=new
R=np.array(sorted(roots)); assert len(R)==240
C=np.linalg.solve(S.T,R.T).T.round().astype(int)       # simple-root coefficients
pos=R[(C>=0).all(1)]; Cp=C[(C>=0).all(1)]; assert len(pos)==120
A8=pos[np.isin(Cp[:,1],[0,3])]; assert len(A8)==36
Gl=(np.rint(pos@S.T).astype(int)%2)
lab=[int(''.join(map(str,g)),2)|(1<<8) for g in Gl]; assert len(set(lab))==120
# A8 simple system: positive A8 roots (w.r.t. a generic functional) not sum of two
gen=np.arange(1,9)*1.0+np.sqrt(2)*np.arange(8)**2
sg=np.sign(A8@gen); P8=A8*sg[:,None]
Pset={tuple(np.round(x,6)) for x in P8}
simp=[x for x in P8 if not any(tuple(np.round(x-y,6)) in Pset for y in P8 if not np.allclose(x,y))]
assert len(simp)==8
# chain order
adj=lambda a,b: abs(np.dot(a,b)+1)<1e-9
ends=[i for i in range(8) if sum(adj(simp[i],simp[j]) for j in range(8))==1]
ch=[ends[0]]
while len(ch)<8: ch.append(next(j for j in range(8) if j not in ch and adj(simp[ch[-1]],simp[j])))
sm=[simp[i] for i in ch]
pair={}
for a in range(9):
  for b in range(a+1,9): pair[(a,b)]=sum(sm[a:b])
need=[]
for t in pos:
  best=0
  for k in range(9,0,-1):
    if any(all(abs(np.dot(t,pair[(a,b)]))<1e-9 for a,b in itertools.combinations(K,2)) for K in itertools.combinations(range(9),k)):
      best=k; break
  need.append(9-best)
need=np.array(need); print("need hist",np.unique(need,return_counts=True),"total",need.sum())
# minimal patterns: J = complement of the unique max K
pat=[]
for i,t in enumerate(pos):
  Ks=[K for K in itertools.combinations(range(9),9-need[i]) if all(abs(np.dot(t,pair[(a,b)]))<1e-9 for a,b in itertools.combinations(K,2))]
  assert len(Ks)==1; pat.append(set(range(9))-set(Ks[0]))
Am=np.array([[a in pat[i] for i in range(120)] for a in range(9)])
D=np.array([[bin(u&l).count('1')%2==0 for l in lab] for u in range(512)])
m7=max(int((Am[:,None,:]&(D[u]&D[v]&D[u^v])[None,None,:]).sum(2).max()) for u in range(1,512) for v in range(u+1,512))
print("m (max |A_a cap 7-flat|)",m7)
ks=set(); K6=[]
for u,v,w in itertools.combinations(range(1,512),3):
  if w==u^v or (w^u^v)==0: continue
  if u>v^u or u>w^u: continue
  key=(D[u]&D[v]&D[w]).tobytes()
  if key in ks: continue
  ks.add(key); K6.append(D[u]&D[v]&D[w])
K6=np.array(K6); print("distinct 6-flat line sets",len(K6),"max lines",K6.sum(1).max())
Hk=np.maximum(0,(Am[None,:,:]&~K6[:,None,:]).sum(2)-m7).sum(1)
for s0 in range(1,9):
  rel=np.maximum(0,np.minimum(np.minimum(need,s0),2*need-s0))
  print(s0,int((Hk-(K6*rel[None,:]).sum(1)).min()))
