# full checks of a built word against its base (own code)
import sys, collections
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import fastx, pricekit as pk  # vendored in this directory
def traces(W, R):
    """per owned lifetime: tuple of (op, other-reg-if-public, coef, chart, src proj, dst proj) incl. CLEAR content"""
    n=W['public']; NO=W['owned_fields']; K=4; P=fastx.P
    M=[list(R[r]) for r in range(n)]+[[0]*K for _ in range(NO)]
    cur={}; out=[]; live=0; peak=0
    for e in W['program']:
        op=e[0]
        if op=='MOVE': continue
        if op=='INIT': cur[e[1]]=[('INIT',e[2])]; M[e[1]]=[0]*K; live+=1; peak=max(peak,live); continue
        if op=='CLEAR': cur[e[1]].append(('CLEAR',e[2],tuple(M[e[1]]))); out.append(tuple(cur.pop(e[1]))); M[e[1]]=[0]*K; live-=1; continue
        if op=='SCALE':
            if e[1]>=n: cur[e[1]].append(('S',e[2],e[3],tuple(M[e[1]])))
            q=Q(e[2]); qq=q.numerator%P*pow(q.denominator%P,-1,P)%P; M[e[1]]=[x*qq%P for x in M[e[1]]]; continue
        d,s=e[1],e[2]
        if d>=n or s>=n:
            rec=('A', d if d<n else 'o', s if s<n else 'o', e[3], e[4], tuple(M[s]), tuple(M[d]))
            for x in (d,s):
                if x>=n: cur[x].append(rec)
        q=Q(e[3]); qq=q.numerator%P*pow(q.denominator%P,-1,P)%P
        if op=='COPY': M[d]=[0]*K
        M[d]=[(x+qq*y)%P for x,y in zip(M[d],M[s])]
    return out, peak
from fractions import Fraction as Q
def full(B, W2, label=''):
    n=B['public']; R=fastx.proj_matrix(n,4,1)
    fB=fastx.FastReplay(B,R,4); fW=fastx.FastReplay(W2,R,4)
    ok=fW.ok and all(fB.proj[q]==fW.proj[q] for q in range(n+B['owned_fields']))
    tb,pb=traces(B,R); tw,pw=traces(W2,R)
    cb=collections.Counter(tb); cw=collections.Counter(tw)
    miss=cb-cw; extra=cw-cb
    labels=len({e[1] for e in W2['program'] if e[0]=='INIT'})
    nd=sum(1 for e in W2['program'] if e[0] in('ADD','COPY','SCALE') and (Q(e[3] if e[0]!='SCALE' else e[2]).denominator & (Q(e[3] if e[0]!='SCALE' else e[2]).denominator-1)))
    return dict(rows_ok=ok, problems=fW.bad[:3], base_lifetimes_kept=not miss, missing=sum(miss.values()), new_lifetimes=sum(extra.values()), peak=pw, labels=labels, nondyadic=nd, events=len(W2['program']))
