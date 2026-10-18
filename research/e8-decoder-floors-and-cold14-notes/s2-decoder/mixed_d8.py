import numpy as np, itertools
from e8units import standard_e8, e8_labels
from mixed import *
L, G = standard_e8()
U = e8_labels(G); u = [int(''.join(map(str, r)), 2) for r in U]
Lq = L.astype(np.int64)
ok, why = check_pattern(Lq, u); print('E8 std ok', ok, star_cost(Lq, u)[0])
half = list(range(56, 120))
# punctured set: D8 roots involving e_0 .. ; add unit vectors
def try_unit(add_axes):
    P = set(i for i in range(56) if any(L[i][a] != 0 for a in add_axes))
    live = [i for i in range(120) if i not in P]
    lam = [Lq[i] for i in live]; lab = [u[i] for i in live]
    for a in add_axes:
        e = np.zeros(8, dtype=np.int64); e[a] = 2
        N = [k for k, i in enumerate(live) if e @ Lq[i] != 0]
        # odd z orthogonal to labels of N
        zs = [z for z in range(1, 512) if bin(z).count('1') % 2 and all(not dot(z, lab[k]) for k in N)]
        if not zs: return None
        lam.append(e); lab.append(zs[0])
    lam = np.array(lam); okp, why = check_pattern(lam, lab)
    if not okp: return ('pattern fail', why)
    c, ch, sd = star_cost(lam, lab)
    return dict(v=len(lab), punct=len(P), cst=c, x=c / len(lab), labdim=sd)
for k in range(1, 9):
    print(k, try_unit(list(range(k))), flush=True)
