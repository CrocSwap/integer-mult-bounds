import json,gzip,sys,copy
from fractions import Fraction as Q
from collections import Counter,defaultdict
PKG='/Users/joelpulikkan/imb-r1/research/complex-571-cold14-e1'
sys.path.insert(0,PKG+'/code')
import build_cold_end as BCE
import hpe_audit_and_transport as ATC
span=BCE.span
def rd(p):
    b=open(p,'rb').read()
    return json.loads(gzip.decompress(b) if str(p).endswith('.gz') else b)
def regs(e): return [e[1]]+([e[2]] if e[0]=='add' else [])
def inside(a,b): return span(list(a)+list(b))==span(b)
def frames_endB(w):
    """raw-coordinate frame of every register after A, B (before tail)"""
    v,R=w['report']['v'],w['report']['R'];n=2*v+R
    cur=[() for _ in range(n)]
    for i,p in enumerate(w['ports']):cur[i]=span([p])
    for r,f in w.get('start_extra',{}).items():cur[int(r)]=span(f)
    start=list(cur)
    for part in ('A','B'):
        for e in w[part]:
            for r in regs(e):cur[r]=span(e[-1])
    return start,cur
def main_maps(w):
    v,R=w['report']['v'],w['report']['R'];n=2*v+R
    main=w['A']+w['cut']+w['B']
    m=[{r:Q(1)} for r in range(n)]
    for e in main:ATC.apply(e,m)
    dirty=[{} for _ in range(n)]
    for r in range(v,2*v):dirty[r]={j:x for j,x in m[r].items() if j>=2*v}
    for e in w['precondition']:ATC.apply(e,dirty)
    comp=[['add',r,j,-q.numerator,q.denominator,[]] for r in range(v,2*v) for j,q in sorted(dirty[r].items())]
    P,Pinv=ATC.state_maps(w['precondition']+comp+main,n)
    return P,Pinv,comp
PR=2**61-1
def modrank(rows):
    """rank mod a large prime of a list of dict rows {col: Fraction}"""
    piv={}
    r=0
    for row in rows:
        x={c:(q.numerator*pow(q.denominator,-1,PR))%PR for c,q in row.items() if q}
        x={c:a for c,a in x.items() if a}
        while x:
            c=min(x)
            if c in piv:
                p=piv[c];f=x[c]
                for cc,a in p.items():
                    x[cc]=(x.get(cc,0)-f*a)%PR
                    if not x[cc]:del x[cc]
            else:
                inv=pow(x[c],-1,PR);piv[c]={cc:a*inv%PR for cc,a in x.items()};r+=1;break
    return r
def nullspace_rows(rows, keep):
    """left null space of the matrix whose rows are rows[i] (dict col->Q), restricted to columns in keep.
    returns RREF basis vectors as dicts i->Q (indices into rows)."""
    # augment: row i -> (restricted row, identity tag)
    aug=[({c:x for c,x in r.items() if c in keep and x},{i:Q(1)}) for i,r in enumerate(rows)]
    piv={}
    null=[]
    for a,t in aug:
        a=dict(a);t=dict(t)
        while a:
            c=min(a)
            if c in piv:
                pa,pt=piv[c];f=a[c]
                for cc,x in pa.items():
                    y=a.get(cc,0)-f*x
                    if y:a[cc]=y
                    else:a.pop(cc,None)
                for cc,x in pt.items():
                    y=t.get(cc,0)-f*x
                    if y:t[cc]=y
                    else:t.pop(cc,None)
            else:
                f=a[c];piv[c]=({cc:x/f for cc,x in a.items()},{cc:x/f for cc,x in t.items()});break
        if not a:null.append(t)
    # RREF the null basis on tag coordinates (prefer high index pivots? use min)
    basis={}
    for t in null:
        t=dict(t)
        for c in sorted(basis):
            if c in t:
                f=t[c];
                for cc,x in basis[c].items():
                    y=t.get(cc,0)-f*x
                    if y:t[cc]=y
                    else:t.pop(cc,None)
        if not t:continue
        c=max(t);f=t[c];t={cc:x/f for cc,x in t.items()}
        for c2 in basis:
            if c in basis[c2]:
                g=basis[c2][c]
                for cc,x in t.items():
                    y=basis[c2].get(cc,0)-g*x
                    if y:basis[c2][cc]=y
                    else:basis[c2].pop(cc,None)
        basis[c]=t
    return basis   # pivot index -> vector
