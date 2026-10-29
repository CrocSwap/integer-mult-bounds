# AUD-2: independent re-check of SIXHEAVY's 12 GRRC-2 (j=2) kills from certs.txt, using own scenario generation
# and ONLY the cover facts AUD-2 reproduced in cov.c (root/D7 NONE lists) + the G1 cap thresholds (57 / 78).
import csv, json, re, itertools
from collections import Counter
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}
ROOT_NONE={(6,6,5,4),(6,6,4,4,2),(6,6,4,4,1,1),(6,6,4,4,1),(6,6,5,3,1)}
D7_NONE={(6,6,6,5,4),(6,6,6,4,4,3),(6,6,6,4,4,2),(6,6,6,4,4,1,1)}
def cap(M): return sum(g[w] for w in M)
def noroot(M): M=tuple(sorted(M,reverse=True)); return cap(M)<57 or M in ROOT_NONE
def nononroot(M): M=tuple(sorted(M,reverse=True)); return cap(M)<78 or (cap(M)<=82 and M in D7_NONE)
L='../../data/ledger2_consolidated.csv'
rows={int(r['row']):(int(r['d']),json.loads(r['weights']),int(r['slack'])) for r in csv.DictReader(open(L))}
def scen(ws,d,s):
    if s==7: return {'ClassI':(ws,d,0)}
    S={'beta1':(ws,d,0),'alpha':(ws,d,1)}
    for x in set(ws):
        w=list(ws); w.remove(x); w.append(x+1); S['bump%d'%x]=(sorted(w,reverse=True),d,0)
    if 7 in ws: w=list(ws); w.remove(7); S['b3B']=(w,d-1,0)
    return S
certs={}
for line in open('../SIXHEAVY/certs.txt'):
    m=re.match(r'- (\d+): (.*)',line.strip())
    if not m: continue
    for part in m.group(2).split(' | '):
        t,K0,comp,nodes=re.match(r'(\w+): K0=\(([\d, ]*)\) comp=\(([\d, ]*)\) nodes\(removed\)=\[([\d, ]*)\]',part).groups()
        P=lambda s:[int(x) for x in s.split(',') if x.strip()]
        certs.setdefault(int(m.group(1)),{})[t]=(P(K0),P(comp),P(nodes))
allok=True
for r in [169,312,316,332,333,418,420,426,427,430,435,464]:
    d,ws,s=rows[r]; S=scen(sorted(ws,reverse=True),d,s)
    for t,(w2,dd,ex) in S.items():
        if t not in certs.get(r,{}): print(r,t,'MISSING CERT'); allok=False; continue
        K0,comp,nodes=certs[r][t]
        ok = Counter(K0)+Counter(comp)==Counter(w2) and len(K0)==dd-2
        cc=Counter(comp); ok &= not (Counter(nodes)-cc)   # nodes are distinct pieces of comp
        unit=(1,)*ex
        for p in nodes: ok&=nononroot(tuple(x for x in (comp[:comp.index(p)]+comp[comp.index(p)+1:]))+unit)
        for i,j in itertools.combinations(range(len(nodes)),2):
            rest=list(comp); rest.remove(nodes[i]); rest.remove(nodes[j]); ok&=noroot(tuple(rest)+unit)
        ok&=len(nodes)>3
        allok&=ok; print(r,t,'ok' if ok else 'FAIL')
print('ALL OK' if allok else 'SOME FAIL')
