# AUD-2 independent checker for KILL-6C certs (exact Fractions; own scenario derivation from ledger)
import json, csv, itertools
from fractions import Fraction as F
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}; N={1:1,2:3,3:6}
L='../../data/ledger2_consolidated.csv'
rows={int(r['row']):(int(r['d']),json.loads(r['weights']),int(r['slack'])) for r in csv.DictReader(open(L))}
C=json.load(open('../KILL-6C/certs.json'))
def scen(ws,s,tag):
    ws=sorted(ws,reverse=True)
    if tag in('beta1','alpha','ClassI'): return ws,(119 if tag=='alpha' else 120)
    x=int(tag[4:]); w=list(ws); w.remove(x); w.append(x+1); return sorted(w,reverse=True),120
allok=True
for key,c in C.items():
    r,tag=key.split(':'); d,ws,s=rows[int(r)]
    assert d==8, key
    if s==7: assert tag=='ClassI',key
    else: assert tag!='ClassI',key
    myws,NL=scen(ws,s,tag)
    cw=c['ws']; p=len(cw)
    # cert's piece order may differ: compare multisets, then use cert order for masks
    ok_ws = sorted(cw,reverse=True)==myws and c['NL']==NL
    y={}
    for m,v in c['K']:
        assert 0<m<(1<<p) and bin(m).count('1')<=3 and F(v)>=0
        y[m]=y.get(m,0)+F(v)
    z=[F(v) for v in c['z']]; assert all(v>=0 for v in z)
    rhs=sum(v*N[bin(m).count('1')] for m,v in y.items())+sum(z[j]*g[cw[j]] for j in range(p))
    mn=min(sum(v for m,v in y.items() if m&M==M)+sum(z[j] for j in range(p) if M>>j&1) for M in range(1,1<<p))
    ok= ok_ws and rhs<NL and mn>=1
    allok&=ok
    print(key,'ws',myws,'p',p,'NL',NL,'rhs %.3f'%rhs,'mincover',mn,'OK' if ok else 'FAIL')
# Lemma TC bound recomputed
for p,NL in[(12,120),(12,119),(13,120),(14,120)]:
    print('TC',p,NL,float(F(2*(p-2)*NL-2*p*(p-1),p-3)))
print('ALL OK' if allok else 'SOME FAIL')
