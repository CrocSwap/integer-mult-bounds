# Root-subsystem facts used by the deficit budget (exhaustive over the standard parabolics; W(E8)-orbit sizes computed by reflections).
#  (a) N_r := max #lines of a rank-r parabolic subsystem of E8, r = 0..7  -> d_b >= 112 - N_{8-b}
#  (b) rank-7 parabolics with >= 40 lines are exactly E7 (63) and D7 (42); their W(E8)-orbits have 120 and 1080 members
#      = the 120 root lines and 1080 norm-4 lines (completeness of the direction list |Off(h)| <= 72)
#  (c) rank-6 parabolics with >= 35 lines: only E6 (36); orbit size 1120
# Classical input (Bourbaki VI.1.7 / Humphreys 1.12): for a subspace V, Phi ∩ V is W-conjugate to a standard parabolic subsystem.
import os, sys, itertools, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get('BX_DATA', os.path.join(HERE, '..', 'data', 'data.json'))
D = json.load(open(DATA)); E8 = np.rint(np.array(D['E8']) * 2).astype(int)   # 120 root lines, coordinates x2
n = len(E8); key = {}
for i, r in enumerate(E8): key[tuple(r)] = i; key[tuple(-r)] = i
v = np.array([1, 2, 3, 5, 8, 13, 21, 34]) * 1.0 + 0.01 * np.arange(8)
pos = [r if r @ v > 0 else -r for r in E8]
posset = {tuple(p) for p in pos}
simple = [i for i, r in enumerate(pos) if not any(tuple(r - p) in posset for p in pos if not np.array_equal(p, r))]
assert len(simple) == 8
S = [pos[i] for i in simple]
refl = [[key[tuple(r - 2 * (r @ a) // (a @ a) * a)] for r in E8] for a in S]
def flat(idx):
    M = np.array([pos[i] for i in idx], float); rk = np.linalg.matrix_rank(M)
    return rk, frozenset(j for j in range(n) if np.linalg.matrix_rank(np.vstack([M, E8[j]])) == rk)
std = {}
for k in range(0, 8):
    for sub in itertools.combinations(simple, k):
        rk, f = flat(sub) if k else (0, frozenset())
        std.setdefault((rk, len(f)), set()).add(f)
N = {}
for (rk, sz) in std: N[rk] = max(N.get(rk, 0), sz)
print('N_r (max lines in a rank-r standard parabolic), r=0..7:', [N[r] for r in range(8)])
assert [N[r] for r in range(8)] == [0, 1, 3, 6, 12, 20, 36, 63]
print('PASS N_r = 0,1,3,6,12,20,36,63 (so d_b >= 112 - N_{8-b} = 112,111,109,106,100,92,76,49 for b=8..1 up to the sharper d_1 = 53, d_2 = 78)')
def orbit(f):
    seen = {f}; st = [f]
    while st:
        x = st.pop()
        for p in refl:
            y = frozenset(p[j] for j in x)
            if y not in seen: seen.add(y); st.append(y)
    return seen
r7 = sorted(sz for (rk, sz) in std if rk == 7); print('rank-7 standard parabolic sizes', r7)
big7 = {sz for (rk, sz) in std if rk == 7 and sz >= 40}
assert big7 == {63, 42}, big7
orbs = {sz: len(orbit(next(iter(std[(7, sz)])))) for sz in big7}
print('orbit sizes of rank-7 parabolics with >= 40 lines', orbs)
assert orbs == {63: 120, 42: 1080}
print('PASS rank-7 flats with >= 40 lines: E7 (orbit 120) and D7 (orbit 1080) = the 120 root and 1080 norm-4 directions')
big6 = {sz for (rk, sz) in std if rk == 6 and sz >= 35}
assert big6 == {36}
o6 = len(orbit(next(iter(std[(6, 36)])))); print('E6 orbit size', o6); assert o6 == 1120
print('PASS rank-6 flats with >= 35 lines: only E6, 1120 of them')
