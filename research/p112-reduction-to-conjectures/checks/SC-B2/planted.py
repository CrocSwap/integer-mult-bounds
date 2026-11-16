import random

from cov3 import *
from lib import f2rank
random.seed(5)
# planted covers: random w-dim subspaces of F_2^9 (not inside c=0), T = union of their line sets
def rand_sub(w):
    while True:
        vs=[random.randrange(1,512) for _ in range(w)]
        if f2rank(vs)==w and any(v&1 for v in vs): return vs
def span(vs):
    S={0}
    for v in vs: S|={s^v for s in S}
    return S
ok=0;tot=0
for trial in range(12):
    ws=random.choice([[6,6,5,3,1],[6,5,5,4,1,1],[7,5,4,2],[6,6,6,2,1,1],[5,5,5,4,3]])
    T=set()
    for w in ws:
        S=span(rand_sub(w)); T|={t for t in range(n) if lab[t] in S}
    T=sorted(T)
    if len(T)<8: continue
    tot+=1
    # make weights fit: need flats of dims w exactly; pass
    r=cover_set3(T,ws)
    ok+=bool(r); print(ws,len(T),r,flush=True)
print(ok,tot)
