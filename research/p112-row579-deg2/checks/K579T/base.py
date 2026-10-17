# K579T impl A base: own E8 build (doubled coords), labels as KILL-A8 gen.py convention, maximal 7-flat masks, A7 chains of both classes.
import itertools, random, numpy as np
R=[]
for i,j in itertools.combinations(range(8),2):
  for s in (2,-2):
    for u in (2,-2):
      v=[0]*8; v[i]=s; v[j]=u; R.append(tuple(v))
for sg in itertools.product((1,-1),repeat=8):
  if sg.count(-1)%2==0: R.append(sg)
ip=lambda a,b: sum(x*y for x,y in zip(a,b))//4
canon=lambda v: v if next(x for x in v if x)>0 else tuple(-x for x in v)
L=sorted({canon(r) for r in R}); idx={l:i for i,l in enumerate(L)}
Bc=np.array([[2 if k==i else -2 if k==i+1 else 0 for k in range(8)] for i in range(6)]+[[0]*5+[2,2,0],[-1]*8],dtype=float)
C=np.linalg.solve(Bc.T,np.array(L,dtype=float).T).T
Ci=np.rint(C).astype(int); assert np.abs(C-Ci).max()<1e-9
lab=[int(sum((int(x)%2)<<k for k,x in enumerate(c)))|256 for c in Ci]
assert len(set(lab))==120
LAB=np.array(lab)
par=np.array([bin(x).count('1')&1 for x in range(512)])
Z=np.array([[par[f&l] for l in lab] for f in range(512)],dtype=bool)  # Z[f,t]= f(label t)=1
def masks():
  ms=set()
  for f in range(1,512):
    for g in range(f+1,512):
      ms.add(np.packbits(~(Z[f]|Z[g])).tobytes())
  ms=[np.unpackbits(np.frombuffer(m,dtype=np.uint8))[:120].astype(bool) for m in ms]
  ms.sort(key=lambda v:-v.sum()); mx=[]
  A=np.array(ms)
  keep=[]
  for i,v in enumerate(ms):
    # maximal: no strictly larger superset
    sup=(A[:i]|v).sum(1)==A[:i].sum(1) if i else np.array([],bool)
    if not sup.any(): keep.append(v)
  return np.array(keep)
def chain(cls,seed=0):
  rnd=random.Random(seed)
  while True:
    ch=[rnd.choice(R)]
    ok=True
    while len(ch)<7:
      c=[r for r in R if ip(r,ch[-1])==-1 and all(ip(r,x)==0 for x in ch[:-1])]
      if not c: ok=False;break
      ch.append(rnd.choice(c))
    if not ok: continue
    perproot=any(all(ip(r,x)==0 for x in ch) for r in R)
    if (cls=='E7')==perproot: return ch
def xvals(ch):
  # x[t,a] = <r_t,u_a> with x[.,0]=0, h_ab=u_a-u_b = c_a+..+c_{b-1}
  X=np.zeros((120,8),int)
  for a in range(1,8):
    h=[sum(c[k] for c in ch[0:a]) for k in range(8)]  # h_0a = u_0-u_a
    for t in range(120): X[t,a]=-ip(L[t],h)
  return X
