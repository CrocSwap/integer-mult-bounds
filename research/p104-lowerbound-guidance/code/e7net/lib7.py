# E7NET lib: shard decoder as Net (netlib evaluator, labels overridden to the shard's labels)
import sys, os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1')
sys.path.insert(0,'code/l2test')
sys.path.insert(0,'code/netvswall')
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import e8shard as E
import netlib as NL
from netlib import span, inspan, rankp, P, dot
import numpy as np
from fractions import Fraction as Fr
rows120=[]
for (zp,z) in E.pairs:
    d,dp=E.idx[z],E.idx[zp]; c=int(E.G[d,dp])
    rows120.append(([Fr(int(E.G[p,d])) for p in range(120)],[Fr(int(E.G[s,dp]),2*c) for s in range(120)]))
def shard(kind):
    if kind=='e7': return [t for t in range(120) if E.G[t,117]==0]
    if kind=='p52': return [t for t in range(104) if E.G[t,117]==0]
def setlabels(ports):
    NL.L=[E.U[t] for t in ports]; NL.Qm=np.array([[dot(a,b) for b in NL.L] for a in NL.L])
def modp(fr): return (fr.numerator*pow(fr.denominator,P-2,P))%P
def dec_net(ports):
    setlabels(ports); n=len(ports); N=NL.Net(n); rows=[]
    allU=E.U
    for w,u in rows120:
        D=[i for i,t in enumerate(ports) if w[t]!=0]; S=[i for i,t in enumerate(ports) if u[t]!=0]
        if not D or not S: continue
        a=span([NL.L[s] for s in S]); dl=[NL.L[t] for t in D]
        # b = a ∩ dl^perp  (brute force basis over span elements)
        els=[0]
        for x in a: els+= [e^x for e in els]
        bb=[e for e in els if all(dot(e,d)==0 for d in dl)]
        b=span(bb)
        N.add(a,b,{s:modp(u[ports[s]]) for s in S},{t:modp(w[ports[t]]) for t in D})
    return N
if __name__=='__main__':
    for kind in ('e7','p52'):
        ports=shard(kind); N=dec_net(ports)
        ok,_=N.check(); print(kind,len(ports),'legal',N.legal(),'decoder ok',ok,'D',N.drop(),[ (N.adim(k),N.bdim(k)) for k in range(len(N.nodes))])
        r=N.report(kind,9); print(r)
