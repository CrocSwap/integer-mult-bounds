# Lemma F level-set count for the all-root A_{p-1} pattern: line t (not in E_S) lies in >= p - maxlevel(nu_t) seven-flats,
# nu_t(a) = <r_t, u_a>, h_ab = u_a - u_b. Standard A_{p-1} = {e_a - e_b : a,b < p} inside D8 subset E8 (p<=8).
import itertools
from collections import Counter
R=[]
for i,j in itertools.combinations(range(8),2):
    for s in (2,-2):
        for u in (2,-2):
            v=[0]*8; v[i]=s; v[j]=u; R.append(tuple(v))
for m in range(256):
    v=tuple(1 if m>>k&1 else -1 for k in range(8))
    if sum(1 for x in v if x<0)%2==0: R.append(v)
L=sorted({max(r,tuple(-x for x in r)) for r in R})
for p,cS,name in [(7,20,'113 [7^7,6]'),(8,20,'159 [7^8,6]'),(8,21,'262 [7^8,6,1]')]:
    need=[]
    for l in L:
        nu=[l[a] for a in range(p)]          # <r_t, e_a> (doubled coords; constant shift irrelevant)
        need.append(p-max(Counter(nu).values()))
    need.sort(reverse=True)
    tot=sum(need); excused=sum(need[:cS])
    print(name,'p',p,'Sum need',tot,'minus top',cS,'=',tot-excused,'cap 36p =',36*p, 'KILL' if tot-excused>36*p else 'no', Counter(need))
