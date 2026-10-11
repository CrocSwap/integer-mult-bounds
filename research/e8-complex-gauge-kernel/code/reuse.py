"""Elimination reuse / early reset for the complex word: alias a later helper h2 onto a dead helper h1's physical register
after cancelling h1's clean row with available rows at a frame inside h2's first frame."""
from cxlab import *
import copy
def span(F):
    s={0}
    for b in F:s|={x^b for x in s}
    return s
def solve(target,cands,rows_):
    cols=sorted({j for k in cands for j in rows_[k]}|set(target))
    idx={j:i for i,j in enumerate(cols)}
    M=[[Q(0)]*(len(cands)+1) for _ in cols]
    for ci,k in enumerate(cands):
        for j,x in rows_[k].items():M[idx[j]][ci]=x
    for j,x in target.items():M[idx[j]][-1]=x
    piv=[];r=0
    for c in range(len(cands)):
        p=next((i for i in range(r,len(M)) if M[i][c]),None)
        if p is None:continue
        M[r],M[p]=M[p],M[r];q=M[r][c];M[r]=[x/q for x in M[r]]
        for i in range(len(M)):
            if i!=r and M[i][c]:
                f=M[i][c];M[i]=[a-f*b for a,b in zip(M[i],M[r])]
        piv.append(c);r+=1
    for i in range(r,len(M)):
        if M[i][-1]:return None
    return {cands[c]:M[i][-1] for i,c in enumerate(piv) if M[i][-1]}
def timeline(word):
    return [('A',e) for e in word['A']]+[('C',e) for e in word['cut']]+[('B',e) for e in word['B']]
def find_pairs(word,maxk=3):
    R=word['R'] if 'R' in word else word['report']['R'];n=240+R;P=word['ports']
    tl=timeline(word);ops=[e for _,e in tl]
    first={};last={};ffr={};nxt={}
    uses=defaultdict(list)   # reg -> list of (idx, frame)
    for i,e in enumerate(ops):
        F=basis(e[-1]) if e[-1] is not None else None
        for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):
            uses[r].append((i,F))
    for r in range(2*v,n):
        if uses[r]:first[r]=uses[r][0][0];last[r]=uses[r][-1][0];ffr[r]=uses[r][0][1] if uses[r][0][1] is not None else ()
    # centres of A->cut etc: cut ops for center frames use None frame -> treated as ()
    rows=[{r:Q(1)} if r<v else {} for r in range(n)]
    cur=[()]*n
    for r in range(v):cur[r]=(P[r],)
    # center registers carry their center_frames from the B-phase start; cut frames are None; handle: cur set at A end by climbs
    lasts=defaultdict(list)
    for h,l in last.items():lasts[l].append(h)
    out=[]
    for i,e in enumerate(ops):
        if e[-1] is not None:
            F=basis(e[-1])
            for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):cur[r]=F
        apply(e,rows)
        for h1 in lasts.get(i,[]):
            F1=cur[h1]
            for h2 in range(2*v,n):
                if h2==h1 or h2 not in first or first[h2]<=i:continue
                F2=ffr[h2]
                if not span(F1)<=span(F2):continue
                if not rows[h1]:
                    out.append((h1,h2,i,{},F1));continue
                cands=[]
                for k in range(n):
                    if k==h1 or not rows[k] or k in (h2,):continue
                    if k>=2*v and (k not in first or first[k]>i+0 and False):pass
                    if not span(cur[k])<=span(F2):continue
                    # k's future frames must contain the frame we will force
                    cands.append(k)
                sol=solve(rows[h1],cands,rows)
                if sol is None:continue
                # frame of reset ops
                ok=True
                for k in sol:
                    Fr=basis(list(F1)+list(cur[k]))
                    if not span(Fr)<=span(F2):ok=False;break
                    nf=next((fr for (ii,fr) in uses[k] if ii>i and fr is not None),None)
                    if nf is not None and not span(Fr)<=span(nf):ok=False;break
                if ok:out.append((h1,h2,i,sol,F1))
    return out,tl
def rewrite(word,h1,h2,i,sol,tl):
    """alias h2 onto h1; insert reset adds after timeline index i"""
    w=copy.deepcopy(word);P=w['ports']
    # recompute frames of reset ops: need cur frames at time i -> replay frames only
    n=240+(w['R'] if 'R' in w else w['report']['R'])
    cur=[()]*n
    for r in range(v):cur[r]=(P[r],)
    for j,(ph,e) in enumerate(tl):
        if j>i:break
        if e[-1] is not None:
            F=basis(e[-1])
            for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):cur[r]=F
    resets=[]
    for k,c in sol.items():
        Fr=list(basis(list(cur[h1])+list(cur[k])))
        c=-c
        resets.append(['add',h1,k,c.numerator,c.denominator,Fr])
    # split timeline back to lists
    lst={'A':[], 'C':[], 'B':[]}
    for j,(ph,e) in enumerate(tl):
        e=copy.deepcopy(e)
        if j>i:
            if e[1]==h2:e[1]=h1
            if e[0]=='add' and e[2]==h2:e[2]=h1
        lst[ph].append(e)
        if j==i:lst[ph]+=resets
    # for ops before i (h2 unused) fine.  compact ids: remove h2
    mp={}
    R=(w['R'] if 'R' in w else w['report']['R'])
    for r in range(n):
        if r==h2:continue
        mp[r]=r-(1 if r>h2 else 0)
    for ph in lst:
        for e in lst[ph]:
            e[1]=mp[e[1]]
            if e[0]=='add':e[2]=mp[e[2]]
    w['A'],w['cut'],w['B']=lst['A'],lst['C'],lst['B']
    w['centers']=[mp[r] for r in w['centers']] if all(r!=h2 for r in w['centers']) else None
    assert w['centers'] is not None
    w['R']=R-1
    return w
