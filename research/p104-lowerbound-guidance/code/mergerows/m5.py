"""MERGEROWS m5: NF pipeline on a decoder: (1) constructive normal form on the saturated class and on each equal-support class;
(2) gauge climb of alpha+beta; (3) if below thr, cost-safe transvection search from the NF.  All steps keep C <= C0 (asserted)."""
import sys,pickle,numpy as np
from nf import *
from m2 import *
def classes(rows,Q):
    n=len(Q); rq=rk2(Q); pr=prices(rows,Q)
    sat=[k for k in range(len(rows)) if pr[k]==rq]
    sup={}
    for k in range(len(rows)):
        if pr[k]==rq: continue
        key=(tuple(t for t in range(n) if rows[k][0][t]!=0),tuple(t for t in range(n) if rows[k][1][t]!=0)); sup.setdefault(key,[]).append(k)
    return [c for c in [sat]+list(sup.values()) if len(c)>=2]
def nf_all(rows,Q):
    ds=[]
    for c in classes(rows,Q):
        rows,c=drop_kernel(rows,c)
        if len(c)>=2: rows,d=normal_form(rows,c); ds.append((c,d))
    return clean(rows),ds
if __name__=='__main__':
    f,setn,thr=sys.argv[1],sys.argv[2],int(sys.argv[3])
    rows=pickle.load(open(f,'rb')); L=std_set(setn); Q=Q_std(L); C0=sum(prices(rows,Q))
    g0=gauge_max(rows,Q,600,0)['gmax_sum']
    nfr,ds=nf_all(rows,Q); assert check_decoder(nfr,Q)==0; C1=sum(prices(nfr,Q)); assert C1<=C0
    g1=max(gauge_max(nfr,Q,800,sd)['gmax_sum'] for sd in range(2))
    out='%s C0 %d S1 %d | classes %s | NF C %d S1 %d'%(f.split('/')[-1],C0,g0,[(len(c),d) for c,d in ds],C1,g1)
    if g1<thr:
        _,g2,br,h=search(nfr,Q,40,1); C2=sum(prices(br,Q)); assert C2<=C0 and check_decoder(br,Q)==0
        out+=' | +safe-T C %d S1 %d'%(C2,g2); g1=max(g1,g2)
    print(out,'| PASS' if g1>=thr else '| FAIL',flush=True)
