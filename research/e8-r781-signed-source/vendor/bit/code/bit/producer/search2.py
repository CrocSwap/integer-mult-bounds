# Dylan Crow, with Anthropic Claude assistance; Apache-2.0.
import sys, random, pickle, time, os
import ham2, compile2 as C2, compile as C, e8lib as E
V=E.V
def evalP(Pd):
    ham2.P.clear(); ham2.P.update(Pd)
    h=ham2.build(0,True)
    W=C2.compile2(h)
    bad=C.f2_check(W)
    assert not bad[0] and not bad[1]
    s,deficit,D,steps=C.evaluate(W)
    return s,W.nh,h
keys=[]
import itertools
from ham1 import blocks, cw_lines
for c in blocks:
    ls=cw_lines(c)
    for t in ls: keys.append((('fold',t),2)); keys.append((('l5',t),2))
    for t in ls: keys.append((('pair',c,t),3))
for m in range(8): keys.append((('fc0',m),7)); keys.append((('fn',m),3))
if os.environ.get('LSKEYS'):
    import e8lib as E2
    for c2 in blocks:
        for t in cw_lines(c2): pass
    hh=ham2.build(0,True)
    for k in list(ham2.LSKEYS): keys.append((k,3))
seed=int(sys.argv[1]); rng=random.Random(seed); iters=int(sys.argv[2])
Pd={}
if len(sys.argv)>3 and os.path.exists(sys.argv[3]): Pd=pickle.load(open(sys.argv[3],'rb'))
t0=time.time(); best,R,_=evalP(Pd); print('start',best,R,flush=True)
for it in range(iters):
    k,n=rng.choice(keys)
    old=Pd.get(k,0); new=(old+rng.randrange(1,n))%n
    Pd[k]=new
    try:
        s,R,h=evalP(Pd)
    except AssertionError as e:
        Pd[k]=old; continue
    if s>best-1e-12:
        if s>best+1e-12: print(it,'improved %.6e'%s,'R',R,k,new,'%.0fs'%(time.time()-t0),flush=True)
        best=s; pickle.dump(Pd,open('P_best_%d.pkl'%seed,'wb'))
    else:
        Pd[k]=old
print('final',best)
