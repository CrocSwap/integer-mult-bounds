"""Generalized joint contact-block contraction: k anchors with per-anchor entrance frames.

Written by the main-session Claude (Sonnet 5.5, via Claude Code) with orchestrated
subagent assistance, for the user Erwan L. Apache-2.0. Not authored by any predecessor.
The structure follows research/p104-contact-block-contraction/construct.py (source and
lineage credits are in NOTICE). With spec=None it
reproduces the PR6372 word exactly (regression checked by verify.py); with the
SPEC.json spec it builds three anchors: 224 and 227 enter at frame 245, 234 at
frame 246. The legacy basis helpers are loaded from the pinned PR6353 source.
"""
from copy import deepcopy
from fractions import Fraction as Q
from collections import defaultdict
import sys

# CANDIDATE CHANGE: the legacy basis module is the one already loaded and authenticated by the caller
LB = sys.modules['legacy_basis']
transpose,add,apply,inverse,emit,span=LB.transpose,LB.add,LB.apply,LB.inverse,LB.emit,LB.span
ZERO,FULL=3,127
from support import need


def load_spec(d):
    """JSON spec (Fractions as strings) -> construct spec."""
    return {'anchors': [int(a) for a in d['anchors']], 'entries': {int(k): int(v) for k, v in d['entries'].items()},
            'dirs': {int(a): {int(k): Q(x) for k, x in u.items()} for a, u in d['dirs'].items()},
            'lams': {int(a): {int(k): Q(x) for k, x in u.items()} for a, u in d['lams'].items()}}
def elementary(T,roles):
    """ops (ADD/SCALE/SWAP on `roles`) that map rows e_i -> rows T[i] (as combination of the row of roles[j])."""
    n=len(roles); M=[[Q(x) for x in r] for r in T]; ops=[]   # E_k...E_1 M = I, record E as op on index
    for c in range(n):
        cand=[i for i in range(c,n) if M[i][c]!=0]
        def pw2(x):
            x=abs(Q(x)); return x.numerator&(x.numerator-1)==0 and x.denominator&(x.denominator-1)==0
        k=next((i for i in cand if pw2(M[i][c])),cand[0])
        if k!=c:
            M[c],M[k]=M[k],M[c]; ops.append(('SWAP',c,k))
        if M[c][c]!=1:
            f=M[c][c]; M[c]=[x/f for x in M[c]]; ops.append(('SCALE',c,1/f))
        for i in range(n):
            if i!=c and M[i][c]!=0:
                f=M[i][c]; M[i]=[x-f*y for x,y in zip(M[i],M[c])]; ops.append(('ADD',i,c,-f))
    out=[]
    for op in reversed(ops):      # F_1=E_n^{-1} ... ; SWAP is self-inverse
        if op[0]=='SWAP': out.append(('SWAP',roles[op[1]],roles[op[2]]))
        elif op[0]=='SCALE': out.append(('SCALE',roles[op[1]],1/Q(op[2])))
        else: out.append(('ADD',roles[op[1]],roles[op[2]],-Q(op[3])))
    return out
def ops_from_spec(spec):
    """spec: anchors (list of roles), entries {role:frame}, dirs {role: {k: coeff}} (u_j), lams {role: {row: coeff}}"""
    anchors=spec['anchors']; dirs=spec['dirs']; lams=spec['lams']
    # B0: first the non-anchor rows, then the anchor block
    B0=[]
    nonanch=sorted({k for u in dirs.values() for k in u if k not in anchors})
    for k in nonanch:
        for a in anchors:
            c=dirs[a].get(k,0)
            if c: B0.append(('ADD',k,a,Q(c)))
    T=[[Q(dirs[aj].get(ai,0)) for aj in anchors] for ai in anchors]   # row i = B[a_i] = sum_j u_j[a_i] e_{a_j}
    B0+=elementary(T,anchors)
    Lam=[[Q(lams[ai].get(aj,0)) for aj in anchors] for ai in anchors]
    Cops=elementary(Lam,anchors)
    for ai in anchors:
        for r,c in sorted(lams[ai].items()):
            if r not in anchors and c: Cops.append(('ADD',ai,r,Q(c)))
    return B0,Cops
def construct(source,spec=None):
    w=transpose(source); out=deepcopy(w); N=w['public']
    if spec is None:
        a,b=224,227; anchors=[a,b]; entries={a:245,b:245}; g=1091
        B0=[('ADD',a,b,Q(1)),('SCALE',b,Q(-2)),('ADD',b,a,Q(1)),('SCALE',a,Q(2))]
        extra={228:1,229:-1,232:-1,233:1,238:-1,239:1,449:-1}
        B0+=[('ADD',r,b,Q(c)) for r,c in extra.items()]
        Cops=[('ADD',193,742,Q(1,2)),('ADD',169,742,Q(1,2)),('SWAP',a,193),('SWAP',b,169)]
    else:
        anchors=spec['anchors']; entries=spec['entries']; g=1091
        B0,Cops=ops_from_spec(spec)
    shadow={a:N+9+i for i,a in enumerate(anchors)}
    helpers={r for r in range(N) if r not in set(w['live'])|{s+112 for s in w['live']} and w['initial'][r]==ZERO and w['final'][r]==FULL}
    zero=[e for e in w['program'] if e[0] in('ADD','COPY','SCALE','INIT','CLEAR') and e[-1]==ZERO]
    need(not any(e[0]=='MOVE' and e[1]>=N and (e[2]==ZERO or e[3]==ZERO) for e in w['program']),'No owned transport through Z')
    old_zero_owned={e[1] for e in zero if e[0]=='INIT'}
    need(not old_zero_owned.intersection(shadow.values()),'Disjoint zero-register lifetimes')
    first={e[1]:(i,e[3]) for i,e in enumerate(w['program']) if e[0]=='MOVE' and e[1]<N and e[2]==ZERO}
    groups=defaultdict(list)
    for r,(i,gg) in first.items(): groups[gg].append(r)
    def execute(rows,program):
        for e in program:
            op,r=e[:2]
            if op in('INIT','CLEAR'):
                if op=='CLEAR': need(not rows[r],'Every preparation CLEAR is zero')
                rows[r]={}
            elif op=='SCALE': rows[r]={k:Q(e[2])*v for k,v in rows[r].items()}
            elif op=='COPY':
                need(not rows[r],'Preparation COPY is zero'); rows[r]={k:Q(e[3])*v for k,v in rows[e[2]].items()}
            elif op=='ADD': add(rows[r],rows[e[2]],Q(e[3]))
            else: raise ValueError('Preparation opcode')
    A=[{r:Q(1)} for r in range(N+w['owned_fields'])]; execute(A,zero)
    used={e[1] for e in B0}|{e[2] for e in B0 if e[0]=='ADD'}
    need(used<=helpers,'Input basis uses full independent helpers')
    B=[{r:Q(1)} for r in range(N+w['owned_fields'])]; apply(B,B0)
    inv_ok=all(first[r][1]==g for e in Cops for r in ([e[1]]+([e[2]] if e[0] in('ADD','SWAP') else [])))
    need(inv_ok and all(first[r][1]==g for r in anchors),'One native departure block')
    apply(A,Cops)
    def response(r,anchor): return sum(c*B[k].get(anchor,Q(0)) for k,c in A[r].items())
    
    need([[response(r,x) for x in anchors] for r in anchors]==[[Q(int(r==x)) for x in anchors] for r in anchors],'Unit primary responses')
    for r in groups[g]:
        if r in anchors: continue
        ops=[('ADD',r,x,-response(r,x)) for x in anchors if response(r,x)]
        Cops+=ops; apply(A,ops)
    B2=[];off={}
    for r in anchors:
        row={}
        for k,c in A[r].items(): add(row,B[k],c)
        need({x:row.get(x,0) for x in anchors}=={x:Q(x==r) for x in anchors},'Exact anchor input pairing')
        row.pop(r)
        need(set(row)<=helpers-set(anchors),'Helper-only off-anchor correction')
        off[r]=row; B2+=[('ADD',r,s,-c) for s,c in row.items()]
    response_rows={r:{x:response(r,x) for x in anchors if response(r,x)} for r in range(N)}
    response_rows={r:row for r,row in response_rows.items() if row}
    need(set(response_rows)<=set(first),'All responses have native departures')
    for r,row in response_rows.items():
        if r in anchors: continue
        need({entries[x] for x in row}=={first[r][1]},'Response rows depart through the entrance frame of their anchors')
    prep=[['INIT',s,ZERO] for s in shadow.values()]
    prep+=emit(B2,ZERO,shadow); prep+=emit(B0,ZERO,shadow)
    for e in zero:
        e=list(e); e[1]=shadow.get(e[1],e[1])
        if e[0] in('ADD','COPY'): e[2]=shadow.get(e[2],e[2])
        prep.append(e)
    prep+=emit(Cops,ZERO,shadow)
    prepared=[{r:Q(1)} for r in range(N+w['owned_fields'])]; execute(prepared,prep)
    need(all(not prepared[s] for s in shadow.values()),'New preparation rows are exactly zero')
    prep+=[['CLEAR',s,ZERO] for s in reversed(tuple(shadow.values()))]
    for r,f in entries.items(): out['initial'][r]=f
    early=[];moved=set()
    for r,row in response_rows.items():
        if r in anchors: continue
        F=first[r][1]
        early.append(['MOVE',r,ZERO,F,False]); moved.add(r)
        early+=[['ADD',r,x,str(c),F] for x,c in row.items()]
    for r in anchors:
        early.append(['MOVE',r,entries[r],g,False]); moved.add(r)
    for r in groups[g]:
        if r not in moved: early.append(['MOVE',r,ZERO,g,False]); moved.add(r)
    early+=emit(inverse(Cops),g)
    rest=[];omitted=set()
    for i,e in enumerate(w['program']):
        if e[0] in('ADD','COPY','SCALE','INIT','CLEAR') and e[-1]==ZERO: continue
        if e[0]=='MOVE' and e[1] in moved and e[2]==ZERO:
            need(first[e[1]][0]==i and e[1] not in omitted,'Exact eager departure replacement'); omitted.add(e[1]); continue
        rest.append(deepcopy(e))
    need(omitted==moved,'All replaced departures are present')
    out['program']=prep+early+rest+emit(inverse(B0),FULL)
    out['program']+=emit(inverse(B2),FULL)
    forward=transpose(out)
    need(all(span(x)==span(y) for x,y in zip(forward['frames'],source['frames'])),'Double transpose preserves every native subspace')
    forward['frames']=deepcopy(source['frames'])
    return forward,dict(response_rows=response_rows,B0=B0,C=Cops)
