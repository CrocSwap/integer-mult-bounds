#!/usr/bin/env python3
"""Per-event verifier for the hosted mixed-port native word, dyadic alphabet (the predecessor rule): exact Fractions replay of every event (standard library only).
python3 -I -B verify_host3_dyadic.py WORD.json.gz
Checks: frame law for each event, public moves up and nested, owned moves nested either way (owned ascent counted and printed), ADD at a common frame, dyadic coefficients and dyadic SCALE units,
|q|+1 < 2^16, finals, helper rank > 0, 104 literal ports, main endpoint frames, exact endpoint X = x + a y, Y = x + (1+a) y (hosted ports and two-chain ports), helpers identity, owned zero after CLEAR.
Prints the histogram of paid moves and helpers and PASS_HOST3."""
import gzip,json,sys
from fractions import Fraction as Q
from collections import Counter
W=json.load(gzip.open(sys.argv[1]));fr=W['frames'];n=len(W['initial']);NO=W['owned_fields'];NR=n+NO
alpha=Q(W['hosted']['alpha']);beta=Q(W['hosted']['beta']);H=W['hosted'];assert H['mode']=='mix-t0' and alpha==-1 and beta==Q(1,2)
X2=H['X2'];Y2=H['Y2'];a2=Q(H['alpha2']);DP=H['Dports'];assert a2==-1 and len(set(X2)|set(Y2))==2*len(DP)==2*len(X2)
sp=[]
for b in fr:
    s={0}
    for v in b:
        assert 0<v<512 and v not in s;s|={x^v for x in s}
    sp.append(frozenset(s))
cur=list(W['initial'])+[None]*NO;val=[{r:Q(1)} if r<n else {} for r in range(NR)];own=set();paid=Counter();up=Counter();nev=0
def add(a,b,c):
    for k,v in b.items():
        t=a.get(k,0)+c*v
        if t:a[k]=t
        else:a.pop(k,None)
for i,e in enumerate(W['program']):
    op=e[0];r=e[1]
    if op=='MOVE':
        _,r,a,b,pv=e;assert cur[r]==a and (r>=n)==bool(pv),i
        if pv:
            assert sp[a]<sp[b] or sp[b]<sp[a],i
            if sp[a]<sp[b]:up[len(fr[b])-len(fr[a])]+=1
        else:assert sp[a]<sp[b],i
        paid[abs(len(fr[b])-len(fr[a]))]+=1;cur[r]=b
    elif op=='INIT':assert r>=n and r not in own,i;own.add(r);cur[r]=e[2];val[r]={}
    elif op=='CLEAR':assert r in own and cur[r]==e[2],i;own.discard(r);cur[r]=None;val[r]={}
    elif op=='SCALE':
        q=Q(e[2]);assert cur[r]==e[3] and q!=0 and q.denominator&(q.denominator-1)==0 and abs(q.numerator)&(abs(q.numerator)-1)==0,i
        val[r]={k:v*q for k,v in val[r].items()}
    elif op in('ADD','COPY'):
        s=e[2];q=Q(e[3]);f=e[4];assert cur[r]==f==cur[s] and s!=r and q!=0 and q.denominator&(q.denominator-1)==0 and abs(q)+1<2**16,i
        if op=='COPY':assert r in own and not val[r],i
        add(val[r],val[s],q)
    else:raise SystemExit('bad op')
assert not own and all(cur[r]==W['final'][r] for r in range(n))
live=W['live'];X=set(live);Y={r+112 for r in live};assert len(live)==104
X2s=dict(zip(X2,Y2));Y2s=set(Y2);assert not (X2s.keys()|Y2s)&(X|Y);dX={live[i] for i in DP}
bad=0;hel=Counter()
for r in range(n):
    if r in X:ex={r:Q(1)} if r in dX else {r:Q(1),r+112:alpha}
    elif r in Y:ex={r-112:Q(1),r:Q(1)} if r-112 in dX else {r-112:beta,r:1+alpha*beta}
    elif r in X2s:ex={r:Q(1),X2s[r]:a2}
    elif r in Y2s:ex={r:Q(1)}
    else:
        ex={r:Q(1)};d=len(fr[W['final'][r]])-len(fr[W['initial'][r]]);assert d>0,r;assert sp[W['initial'][r]]<=sp[W['final'][r]];hel[d]+=1
    if val[r]!=ex:bad+=1
for r,q in zip(live,W['ports']):
    assert fr[W['initial'][r]]==[q] and len(fr[W['final'][r]])==9 and len(fr[W['initial'][r+112]])==0
    assert sp[W['final'][r+112]]==frozenset(x for x in range(512) if not (x&q).bit_count()%2)
for x2,y2,r,q in zip(X2,Y2,[live[i] for i in DP],[W['ports'][i] for i in DP]):
    assert W['initial'][x2]==W['initial'][r] and fr[W['initial'][x2]]==[q] and W['final'][x2]==W['final'][r] and len(fr[W['final'][x2]])==9
    assert W['initial'][y2]==W['initial'][r+112] and W['final'][y2]==W['final'][r+112]
print('events',len(W['program']),'public',n,'owned roles',NO,'paid',dict(sorted(paid.items())),'owned UP',dict(sorted(up.items())),'helpers',dict(sorted(hel.items())))
print('endpoint bad rows',bad)
assert bad==0;print('PASS_HOST3 decoupled ports',len(DP),'hosted ports',104-len(DP))
