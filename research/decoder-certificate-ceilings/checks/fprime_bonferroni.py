# F' (zero-cost terms dropped, value m(D) <= min(T, chi(D)) ) ceiling via uniform maximal-orthogonal-set weights + Bonferroni
from geom import *
from units import units
from fractions import Fraction as Fr
import itertools
for name in ('E8','P112'):
    idx,T=units[name]; m=len(idx); sets,o=all_orth_sets(idx); mx=maximal(sets,o,m)
    per=[sum(1 for M in mx if M>>t&1) for t in range(m)]
    inter_orth=set(); inter_non=set()
    for a in range(m):
        for b in range(a+1,m):
            c=sum(1 for M in mx if M>>a&1 and M>>b&1)
            (inter_orth if o[a]>>b&1 else inter_non).add(c)
    a1=min(per); a2=max(inter_orth); assert inter_non=={0}
    omax=max(bin(M).count('1') for M in mx)
    exact={k:min(sum(1 for M in mx if M&c) for c in sets if bin(c).count('1')==k) for k in range(1,omax+1)}  # min meet over ORTHOGONAL k-sets
    bon=lambda k,p: a1*k-a2*(k*(k-1)//2-p)   # lower bound on meet of a k-set with p non-orth pairs
    # y chosen so that y*bon(8,1)>=8 (|D|>=9 or non-orth 8-sets, m<=8)
    y=Fr(T,bon(T,1)); ok=True
    for k in range(1,T+1):
        need_orth=k; need_non=min(k-1,T)   # non-orth k-set: chi<=k-1
        lb_orth=exact.get(k,None)
        if lb_orth is not None and y*lb_orth<need_orth: ok=False; print('fail orth',k)
        if k>=2 and y*max(bon(k,1),0)<need_non: ok=False; print('fail non-orth',k,bon(k,1))
    print(name,'|Fr(t)| min',a1,'orth-pair inter',sorted(inter_orth),'non-orth inter',sorted(inter_non),'max orth',omax,
          'min meet orth k-sets',exact,'bon(8,1)',bon(T,1),'y',y,'ceiling',len(mx)*y,float(len(mx)*y),'all checks',ok)
    assert ok and (len(mx), y) == ((2025, Fr(8, 675)) if name == 'E8' else (1996, Fr(8, 667)))
    print('PASS' if ok else 'FAIL', "F' Bonferroni ceiling", name, '=', len(mx) * y, '=', round(float(len(mx) * y), 3), '(proven)')
