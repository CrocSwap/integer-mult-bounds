# BSTAR pcompat.py / hset3.py, E8 only (CHECKED): a frame F is P-compatible if every eps-class (4 lines) at every pair of every F-tetrad has a line in L and every sign pattern (eps_ab,eps_bc) (2 lines) of every triple does (L = E8: always).
# Used by Theorem P / A (BSTAR): every orthogonal pair lies in a P-compatible frame.
import itertools
from e8lib import *
FR=frames(); print('frames',len(FR)); assert len(FR)==2025
sg=lambda u,a,b: 1 if G[u][a]*G[u][b]>0 else -1
PC=0; cov=set()
for f in FR:
    ok=True
    for k,ls in tetrads(f).items():
        kk=sorted(k)
        for a,b in itertools.combinations(kk,2):
            for e in (1,-1):
                if not any(sg(u,a,b)==e for u in ls): ok=False
        for a,b,c in itertools.combinations(kk,3):
            for e1 in (1,-1):
                for e2 in (1,-1):
                    if not any(sg(u,a,b)==e1 and sg(u,b,c)==e2 for u in ls): ok=False
    PC+=ok
    if ok: cov.update(itertools.combinations(sorted(f),2))
allp=[p for p in itertools.combinations(range(N),2) if G[p[0]][p[1]]==0]
print('P-compatible frames',PC,'/',len(FR),'| orthogonal pairs covered',sum(p in cov for p in allp),'/',len(allp))
assert PC==2025 and len(allp)==3780 and all(p in cov for p in allp)
print('PASS pframes: all 2025 E8 frames are P-compatible; all 3780 orthogonal pairs lie in a frame')
