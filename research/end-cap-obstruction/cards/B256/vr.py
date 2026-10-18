"""B256 version reconstruction engine. ops are lists [op,t,(s),a,b,frame]."""
from lib import *
import copy
def relax(w, record=None):
    """lazy-widen every explicit frame to contain current register frames (frames only grow). returns (word, nwid)"""
    w=copy.deepcopy(w); R=w['report']['R']; n=2*V+R; P=w['ports']
    cur={}
    for r in range(n): cur[r]=(P[r],) if r<V else ((G.basis(w['start_extra'][str(r)]) if str(r) in w.get('start_extra',{}) else ()) if r>=2*V else ())
    nw=0
    for part in 'AB':
        for e in w[part]:
            rr=[e[1]]+([e[2]] if e[0]=='add' else [])
            F=G.basis(list(e[-1])+[x for r in rr for x in cur[r]])
            if tuple(F)!=tuple(G.basis(e[-1])): nw+=1
            e[-1]=list(F)
            for r in rr: cur[r]=F
    return w,nw
def rowsfinal(w): return rows_final(w)
def same_value(w1,w2):
    r1=rows_final(w1);r2=rows_final(w2)
    return r1==r2
def rows_at(w,part,idx):
    """rows just before op (part,idx)"""
    n=2*V+w['report']['R'];rows=[{r:Q(1)} for r in range(n)]
    for e in w['A']:
        if part=='A' and e is w['A'][idx]: return rows
        G.apply_op(e,rows)
    for e in w['cut']: G.apply_op(e,rows)
    for i,e in enumerate(w['B']):
        if part=='B' and i==idx: return rows
        G.apply_op(e,rows)
    return rows
def caps(w):
    P=w['ports'];R=w['report']['R'];n=2*V+R
    cur={r:((P[r],) if r<V else ((G.basis(w['start_extra'][str(r)]) if str(r) in w.get('start_extra',{}) else ()) if r>=2*V else ())) for r in range(n)}
    first={}
    for part in 'AB':
        for i,e in enumerate(w[part]):
            F=G.basis(e[-1]);rr=[e[1]]+([e[2]] if e[0]=='add' else [])
            for r in rr:
                nf=G.basis(list(cur[r])+list(F))
                if V<=r<2*V and r not in first and not inperp(nf,r-V,P): first[r]=(part,i,e[:3])
                cur[r]=nf
    bad=[r for r in range(V,2*V) if not inperp(cur[r],r-V,P)]
    return bad,first
def prof(w):
    try: return dict(sorted(G.profile(w).items()))
    except AssertionError as ex: return 'FAIL '+str(ex)[:150]

def lazy(w, seeds, startg=0, maxcone=None):
    """re-derive lazy-join frames for ops touching the cone (cone grows through shared ops), widening elsewhere.
    returns word, #ops changed, cone"""
    w=copy.deepcopy(w); R=w['report']['R']; n=2*V+R; P=w['ports']
    cone=set(seeds)
    cur={r:((P[r],) if r<V else ((G.basis(w['start_extra'][str(r)]) if str(r) in w.get('start_extra',{}) else ()) if r>=2*V else ())) for r in range(n)}
    ch=0
    for part in 'AB':
        for e in w[part]:
            rr=[e[1]]+([e[2]] if e[0]=='add' else [])
            need=G.basis([x for r in rr for x in cur[r]])
            if e[-1] is None or any(r in cone for r in rr):
                F=need; 
                cone.update(rr)
            else:
                F=G.basis(list(e[-1])+list(need))
            if e[-1] is None or tuple(F)!=tuple(G.basis(e[-1])): ch+=1
            e[-1]=list(F)
            for r in rr: cur[r]=F
    return w,ch,cone
