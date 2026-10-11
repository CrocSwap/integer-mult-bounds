"""Generalised exact checker for variants of the #433 complex word (arbitrary dirt, inverse-transpose, frame chain, paid profile).
A variant = dict(A,B,cut,precondition,pre,start,ports,...).  pre = list of ['add',donor,pivot,num,den,E] ops placed first in main.
start = {register: frame(list of masks)} for pivots (default () for helpers, (P[s],) for sources, () for targets).
cleanup is rebuilt: inverse of all non-target ops of pre+A+B at FULL, reversed."""
from cxlab import *
import time
FULL=tuple(1<<i for i in range(8,-1,-1))
def perp(x):return basis([z for z in range(1,512) if not (x&z).bit_count()%2])
def dual(e):
    e=inv(e)
    if e[0]=='add':e[1],e[2]=e[2],e[1]
    return e
def fr(F):return basis(list(F))
def inside_(a,b):  # a subspace of b (both basis tuples)
    return basis(list(a)+list(b))==tuple(b)
def check(word,pre=(),start=None,full=True,verbose=True):
    t0=time.time()
    A,B,cut,prec=word['A'],word['B'],word['cut'],word['precondition']
    R=word['report']['R'] if 'R' not in word else word['R']
    n=240+R;P=word['ports'];start=start or {}
    main=list(pre)+A+cut+B
    M=ident(n)
    for e in main:apply(e,M)
    dirty=[{} for r in range(n)]
    for r in range(v,2*v):dirty[r]={j:x for j,x in M[r].items() if j>=2*v}
    for e in prec:apply(e,dirty)
    comp=[]
    for r in range(v,2*v):
        for j,x in sorted(dirty[r].items()):comp.append(['add',r,j,-x.numerator,x.denominator,[]])
    ncomp_cols=len({e[2] for e in comp})
    cleanup=[]
    for e in reversed(list(pre)+A+B):
        if not v<=e[1]<2*v:
            c=inv(e);c[-1]=list(FULL);cleanup.append(c)
    program=list(prec)+comp+main+cleanup
    rep=dict(R=R,comp_adds=len(comp),comp_cols=ncomp_cols)
    if full:
        actual=ident(n)
        for e in program:apply(e,actual)
        expected=ident(n)
        for t in range(v):expected[v+t][t]=Q(1)
        assert actual==expected,'arbitrary-dirt exactness FAILED'
        back=ident(n)
        for e in program:apply(dual(e),back)
        eb=ident(n)
        for t in range(v):eb[t][v+t]=Q(-1)
        assert back==eb,'inverse-transpose FAILED'
        rep['exact_arbitrary_dirt']=True;rep['exact_inverse_transpose']=True
    # frame chain + paid profile (mirrors complex_audit canonical climb check)
    cur={}
    for r in range(n):
        if r<v:cur[r]=(P[r],)
        elif r<2*v:cur[r]=()
        else:cur[r]=fr(start.get(r,()))
    startrank={r:len(cur[r]) for r in range(n)}
    paid=Counter();edges=set()
    def climb(r,F):
        F=fr(F);o=cur[r]
        assert inside_(o,F),('frame violation',r,o,F)
        if o!=F:paid[len(F)-len(o)]+=1;edges.add((o,F));cur[r]=F
    for part,seq in (('A',list(pre)+A),('B',B)):
        if part=='B':
            ce=word['centers'];cf=word['center_frames']
            assert all(cur[r]==fr(f) for r,f in zip(ce,cf)),'center frames'
            assert all(cur[r]==() for r in range(v,2*v)),'targets start'
            for f in cf:paid[len(f)]+=1
        for e in seq:
            for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):climb(r,e[-1])
    for r in range(n):
        climb(r,FULL if (r<v or r>=2*v) else perp(P[r-v]))
    rep['local_profile']=dict(sorted(paid.items()));rep['edges']=len(edges)
    rep['mass']=sum(r*z for r,z in paid.items())
    rep['widths']=[9-startrank[r] for r in range(2*v,n)]
    rep['seconds']=time.time()-t0
    rep['_program']=program
    return rep,edges
if __name__=='__main__':
    w=load();rep,_=check(w)
    print({k:v for k,v in rep.items() if k not in('_program','widths')},sum(rep['widths']))
