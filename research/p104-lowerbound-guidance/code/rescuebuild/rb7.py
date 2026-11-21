"""rb7: no-good enumeration of designs (presolve on) using rb6.build; dihedral canonical dedupe; saves pickle."""
import sys,os,pickle,time;sys.path.insert(0,'.')
from rb6 import *
def enum(k,bar,cr=True,maxn=100000,tl=1800,extra=None):
    m,c,O,val=build(k,bar=bar,cellrank=cr,extra=extra);seen={};t0=time.time();raw=0
    while time.time()-t0<tl and raw<maxn:
        sv=cp_model.CpSolver();sv.parameters.num_workers=1;sv.parameters.max_time_in_seconds=max(5,tl-(time.time()-t0))
        st=sv.Solve(m)
        if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return seen,sv.StatusName(st),raw
        v=[sv.Value(x) for x in c];raw+=1
        des=tuple(O[i] for i,x in enumerate(v) for _ in range(x))
        cd=canon(k,des)
        if cd not in seen:
            seen[cd]=float(sum(val[i]*x for i,x in enumerate(v))*104/k);print('#%d %.3f t=%.0f'%(len(seen),seen[cd],time.time()-t0),cd,flush=True)
        # forbid all dihedral images of this design
        for r in range(k):
            for f in (1,-1):
                mp=lambda t:(f*t+r)%k
                img={}
                for M,P,mn in des:
                    o=(frozenset(map(mp,M)),tuple(sorted((frozenset(map(mp,p)) for p in P),key=sorted)),frozenset(map(mp,mn)))
                    j=O.index(o);img[j]=img.get(j,0)+1
                ds=[]
                for j,cnt in img.items():
                    d=m.NewBoolVar('');m.Add(c[j]==cnt).OnlyEnforceIf(d);m.Add(c[j]!=cnt).OnlyEnforceIf(d.Not());ds.append(d)
                m.Add(sum(ds)<=len(ds)-1)
    return seen,'TIMEOUT',raw
if __name__=='__main__':
    k=int(sys.argv[1]);bar=Dm(sys.argv[2]);cr=sys.argv[3]=='1'
    seen,st,raw=enum(k,bar,cr,tl=float(os.environ.get('TL','1800')))
    print('k',k,'bar',bar,'cellrank',cr,'final',st,'designs',len(seen),flush=True)
    pickle.dump(seen,open('rb7_k%d_b%s_cr%d.pkl'%(k,sys.argv[2],cr),'wb'))
    for d,v in sorted(seen.items(),key=lambda x:-x[1])[:12]:print(round(v,3),d)
