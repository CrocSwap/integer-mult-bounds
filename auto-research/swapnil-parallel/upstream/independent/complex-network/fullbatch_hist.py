"""Residual histogram of the PR #7 complex network (h+1 centre wires, PR #7 schedule), from our
own producer (side.Side), labels (labels.Checker) and role compilation (roles.compile_roles).
Every nonzero residual edge is counted; full batching treats each as one whole-residual call."""
import sys, json, pickle
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import Counter
from math import comb
from side import Side
from labels import Checker
from roles import compile_roles

class Trace:
    def __init__(s,d): s.dim=list(d); s.hist=Counter(); s.desc=[]
    def gate(s,roles,dim):
        for r in set(roles):
            o=s.dim[r]; k=abs(dim-o)
            if k: s.hist[k]+=1
            if o>dim: s.desc.append(o-dim)
            s.dim[r]=dim

def invocation(c,k,dims,stage,inverse,sf=False):
    h=c.h; m=h**3; v=len(c.triples); R=k['size']
    x={t:i for i,t in enumerate(c.triples)}; y={t:v+i for i,t in enumerate(c.triples)}
    side=lambda sl:2*v+sl
    ncent=h+1
    cent=tuple(range(2*v+R,2*v+R+ncent))
    a=h**(stage-1); low,high=(a-1)*h,a*h
    tr=Trace([a]*v+[a-1]*v+[h if stage==3 else 0]*(R+ncent))
    # Source frames (stage two only, notes/complex-source-frames.tex): an auxiliary role starts in D0, of dim
    # low, and its exit child to the sink wt+q_D0 has rank (m+low) - last dim. Input-pivot slots are left
    # at source 0: their first stage-two gate is the copy in the data frame, not a frame above D0, so
    # starting them at D0 would charge a descent and break the rank sum.
    keep=set(k['src'].values())|set(k['rout'].values())
    sfr={2*v+sl for sl in range(R) if sf and stage==2 and sl not in keep}
    for r in sfr: tr.dim[r]=low
    pieces={t:[] for t in c.triples}
    for i,sl in k['pout'].items(): pieces[c.pieces[i][0]].append(side(sl))
    def mix(md,rev=False):
        for n,ins,outs in (reversed(k['gates']) if rev else k['gates']):
            f={'low':low,'high':high,'label':low+dims[n],'complement':high-dims[n]}[md]
            tr.gate([side(q) for q in ins+outs],f)
    def inject(b,f):
        for t in c.triples: tr.gate([b[t]]+pieces[t],f)
    def copy(b,f):
        for t,sl in k['src'].items(): tr.gate((b[t],side(sl)),f)
    def central(b,f): tr.gate(tuple(b.values())+cent,f)
    if True:
        if not inverse:
            mix('low'); inject(y,low); mix('low',True); central(y,low)
            copy(x,low+1); central(x,high); central(y,low)
            mix('label'); inject(y,high-1); mix('high',True)
            central(x,high); copy(x,high)
        else:
            copy(y,a-1); central(y,low); mix('low'); inject(x,low+1)
            mix('complement',True); central(x,high); central(y,low)
            copy(y,high-1); central(x,high); mix('high'); inject(x,high)
            mix('high',True)
    for r in x.values(): tr.gate((r,),high)
    for r in y.values(): tr.gate((r,),high-1)
    for r in range(2*v,len(tr.dim)): tr.gate((r,),(m+low) if r in sfr else (h if stage==1 else m))
    return tr.hist, tr.desc

def run(h,sf=False):
    c=Side(h)
    k=compile_roles(c); ch=Checker(c); chk=ch.run()
    dims={n:len(ch.label(n)) for n in c.active}
    H=Counter(); D=[]
    for st,inv in ((1,False),(2,True),(3,False)):
        hh,dd=invocation(c,k,dims,st,inv,sf); H.update(hh); D.append(sorted(Counter(dd).items()))
    v=len(c.triples); m=h**3; N=v**3; Rb=k['size']+h+1
    loss=h*(h+1)
    W=2*N+2*v*v*Rb; L=3*v*v*loss; s=W*m-2*N+2*L
    hist={r:n*v*v for r,n in sorted(H.items())}
    tot=sum(r*n for r,n in hist.items())
    return dict(h=h,checker=chk,R=Rb,W=W,s=s,m=m,sum_ok=(tot==s),tot=tot,desc=D,hist=hist)

if __name__=='__main__':
    h=int(sys.argv[1]); out=sys.argv[2] if len(sys.argv)>2 else f'/tmp/fullbatch_hist_{h}.json'
    r=run(h,sf=len(sys.argv)>3 and sys.argv[3]=='sf')
    json.dump({**r,'hist':{str(a):b for a,b in r['hist'].items()}},open(out,'w'))
    print({k:v for k,v in r.items() if k!='hist'}); print(r['hist'])
