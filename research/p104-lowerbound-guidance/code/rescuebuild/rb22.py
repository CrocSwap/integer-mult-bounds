"""rb22: CEGAR mask-level sup: maximize chat under CP-SAT laws; lazily cut designs killed by STAR-ZERO (rblaw.star_zero).
usage: rb22.py k maxiter"""
import sys,os,time;sys.path.insert(0,'.')
from rb6 import *
from rblaw import star_zero,violations
from rb10 import roles_of
k=int(sys.argv[1]);mi=int(sys.argv[2])
BAR=Dm(os.environ.get('BAR','0'))
m,c,O,val=build(k,bar=BAR,cellrank=True)
SC=10**6
if BAR==0:m.Maximize(sum(c[i]*int(val[i]*SC) for i in range(len(O))))
import itertools
GK={}
for i,(M,P,mn) in enumerate(O):GK.setdefault((M,frozenset(p for p in P if len(p)>=2)),[]).append(i)
GV={key:None for key in GK}
def gvar(key):
    if GV[key] is None:
        v=m.NewIntVar(0,2*k-2,'');m.Add(v==sum(c[i] for i in GK[key]));GV[key]=v
    return GV[key]
def forbid(des):
    # STAR-ZERO uses only masks + multi pieces and is invariant under ALL stage permutations: forbid every relabelling
    # of the (mask, multi-piece) count vector, whatever the singleton main/idle labels
    seenimg=set()
    for perm in itertools.permutations(range(k)):
        mp=lambda t:perm[t];img={}
        for M,P,mn in des:
            key=(frozenset(map(mp,M)),frozenset(frozenset(map(mp,p)) for p in P if len(p)>=2));img[key]=img.get(key,0)+1
        kk=tuple(sorted(img.items(),key=lambda x:(sorted(x[0][0]),sorted(map(sorted,x[0][1])),x[1])))
        if kk in seenimg:continue
        seenimg.add(kk);ds=[]
        for key,cnt in img.items():
            d=m.NewBoolVar('');g=gvar(key);m.Add(g==cnt).OnlyEnforceIf(d);m.Add(g!=cnt).OnlyEnforceIf(d.Not());ds.append(d)
        m.Add(sum(ds)<=len(ds)-1)
def forbid_dihedral(des):
    for r in range(k):
        for f_ in (1,-1):
            mp=lambda t:(f_*t+r)%k;img={}
            for M,P,mn in des:
                o=(frozenset(map(mp,M)),tuple(sorted((frozenset(map(mp,p)) for p in P),key=sorted)),frozenset(map(mp,mn)))
                j=O.index(o);img[j]=img.get(j,0)+1
            ds=[]
            for j,cnt in img.items():
                d=m.NewBoolVar('');m.Add(c[j]==cnt).OnlyEnforceIf(d);m.Add(c[j]!=cnt).OnlyEnforceIf(d.Not());ds.append(d)
            m.Add(sum(ds)<=len(ds)-1)
t0=time.time()
for it in range(mi):
    sv=cp_model.CpSolver();sv.parameters.num_workers=1;sv.parameters.max_time_in_seconds=1800
    sv.parameters.max_time_in_seconds=float(os.environ.get('TLI','1800'))
    st=sv.Solve(m)
    if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):print('it',it,'STATUS',sv.StatusName(st),'t=%.0f'%(time.time()-t0),flush=True);break
    v=[sv.Value(x) for x in c];des=tuple(O[i] for i,x in enumerate(v) for _ in range(x))
    val_=float(sum(val[i]*x for i,x in enumerate(v))*104/k);R=roles_of(canon(k,des))
    kz=star_zero(k,R)
    print('it',it,sv.StatusName(st),'val %.3f bound %.3f'%(val_,sv.BestObjectiveBound()/SC*104/k),'STARZERO' if kz else 'SURVIVES','t=%.0f'%(time.time()-t0),canon(k,des),flush=True)
    if not kz:
        if os.environ.get('CONT','0')!='1':break
        forbid_dihedral(des);continue
    forbid(des)
