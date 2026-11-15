"""GAPLEMMA dfloor_count.py [C, stdlib, no pricing]: the purely combinatorial part of the kill chain on the pair/single + slack menu
of the L = 17, nl = 8 two-arm B layout (masks as sets of stages; Z_k = roles alive at stage k).

 (1) refined DYINGPAIR / generalised kill (SLACK PROOF C and H.2):  `killed`
 (2) Delta-Floor lemma (GAPLEMMA PROOF P1): kill if some 0 <= i <= d has |Delta_{i-1}| < 2i+4 - |U_i minus Delta|
     (Delta = left roles of U_d absent from Z_K, K = d+1; U_i = roles entered by stage i).

Expected (the counts quoted in README section 3): 117 layouts survive (1); (2) kills 102 of them; the 15 left are all c = 1, k = 1.
Controls: the plain B layout has no dying set; a pair entering at stage 0 is killed at i = 0 by (2); every pair layout that survives (1)
is killed by (2). Prints PASS_DFLOOR_COUNT."""
L = 17; nl = 8

def two_arm(L=17, nl=8, hubs=2, grow=2):
    masks = [set(range(L)) for _ in range(hubs)]
    for k in range(nl): masks += [set(range(k, nl)) for _ in range(grow)]
    for k in range(L - 1, nl - 1, -1): masks += [set(range(nl, k + 1)) for _ in range(grow)]
    return masks

def dying(specs):
    ms = two_arm()
    for arm, k, d, c, extra in specs:
        assert arm == 'L'
        full = set(range(k, nl)); new = set(range(k, d + 1)); ex = set(range(d + 1, nl))
        for _ in range(c): ms.remove(full); ms.append(set(new))
        for _ in range(extra): ms.append(set(ex))
    return ms

def Z_count(ms, k): return sum(1 for m in ms if k in m)
def U(ms, j): return sum(1 for m in ms if min(m) <= j)
def left(ms): return [m for m in ms if max(m) < nl]

def killed(ms, c, k, d):
    K = d + 1; ZK = Z_count(ms, K); Dl = [m for m in left(ms) if min(m) <= d and K not in m]
    old = ZK + len(Dl) - c <= 2 * K + 3 and all(U(ms, j - 1) <= 2 * j + 2 for j in range(k + 1, d + 1))
    ents = {min(m) for m in Dl}
    new = len(ents) == 1 and 2 * K + 4 - ZK >= 1 and all(U(ms, t - 1) <= 2 * t + 2 for t in range(min(ents) + 1, d + 1))
    return old or new

def dkill(ms, d):
    K = d + 1; Dl = [m for m in left(ms) if min(m) <= d and K not in m]
    for i in range(0, d + 1):
        Uim = sum(1 for m in ms if min(m) <= i)
        Dim1 = sum(1 for m in Dl if min(m) <= i - 1)
        Dn = sum(1 for m in Dl if min(m) <= i)
        if Dim1 < 2 * i + 4 - (Uim - Dn): return i
    return None

menu = []; surv = []; nk = 0; rem = []
for c in (2, 1):
    for k in (0, 1):
        for d in range(max(k, 1), nl - 2):
            for je in range(0, d + 1):
                for eend in (d, nl - 1):
                    if k == 0 and je == 0: continue
                    ms = dying([('L', k, d, c, 0)]); ms.append(set(range(je, eend + 1)))
                    menu.append(1)
                    if killed(ms, c, k, d): continue
                    surv.append((c, k, d, je, eend))
                    if dkill(ms, d) is None: rem.append((c, k, d, je, eend))
print('menu', len(menu), 'survivors of the refined DYINGPAIR / generalised kill', len(surv),
      'killed by Delta-Floor', len(surv) - len(rem), 'remaining', len(rem))
assert len(surv) == 117 and len(rem) == 15
assert all(c == 1 and k == 1 for c, k, d, je, eend in rem)
assert all(c == 1 for c, *_ in rem) and not any(c == 2 for c, *_ in rem)       # every pair layout dies
# controls
assert dying([]) == two_arm()
ms = dying([('L', 0, 3, 1, 0)]); ms.append(set(range(1, 4)))
assert dkill(ms, 3) == 0                                                      # outermost entry, all own roles die: fails at i = 0
ms = dying([('L', 1, 3, 1, 0)]); ms.append(set(range(0, 4)))
assert dkill(ms, 3) is None                                                   # family A: not killed by P1 (open case)
print('PASS_DFLOOR_COUNT')
