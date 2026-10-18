"""O1: cross-block 'X4' faces on the 112 lines (port of cards B68/B74 dump.c restricted to quads in 4 distinct blocks),
the face-sum supply tests of B74, and the booked charge arithmetic of B7.  Input: root lines of the #656 word."""
import itertools, random
import numpy as np
from common import *
R = np.array(jgz('pr656-FULL-WORD.json.gz')['root_lines'], int)
ip = R @ R.T
blk = np.arange(112) // 8
S = np.sign(ip).astype(np.int8)
faces = []; hist = {}
for bq in itertools.combinations(range(14), 4):
    tg = np.array([t for t in range(112) if blk[t] not in bq])
    L = [np.arange(8 * b, 8 * b + 8) for b in bq]
    s = [S[np.ix_(tg, l)] for l in L]            # (80, 8)
    ok = [(x != 0) for x in s]
    valid = ok[0][:, :, None, None, None] & ok[1][:, None, :, None, None] & ok[2][:, None, None, :, None] & ok[3][:, None, None, None, :]
    sg0 = s[0][:, :, None, None, None]
    code = ((s[1][:, None, :, None, None] != sg0).astype(np.int8)
            + 2 * (s[2][:, None, None, :, None] != sg0).astype(np.int8)
            + 4 * (s[3][:, None, None, None, :] != sg0).astype(np.int8))
    cnt = np.stack([((code == k) & valid).sum(0) for k in range(8)]).max(0)   # (8,8,8,8)
    for m, nn in zip(*np.unique(cnt, return_counts=True)):
        hist[int(m)] = hist.get(int(m), 0) + int(nn)
    for idx in zip(*np.nonzero(cnt >= 10)):
        faces.append(tuple(int(8 * b + i) for b, i in zip(bq, idx)))
check('o1.4-block-quads-total', sum(hist.values()) == 1001 * 4096)
check('o1.eff-reach-10-faces-2688-none-above', len(faces) == 2688 and max(hist) == 10 and hist[10] == 2688, f'max eff reach {max(hist)}, count at 10: {hist[10]}')
check('o1.every-face-spans-4-blocks', all(len({f_ // 8 for f_ in f}) == 4 for f in faces))
rk = lambda A: int(np.linalg.matrix_rank(A, tol=1e-8))
random.seed(1)
def form(f, sg):
    v = np.zeros(112)
    for i, s in zip(f, sg): v[i] = s
    return v
Tall = np.array([form(f, [random.choice([-1, 1]) for _ in range(4)]) for f in faces])
check('o1.2688-face-forms-span-Q^112', rk(Tall) == 112)
res = set()
for _ in range(20):
    T = Tall[random.sample(range(len(faces)), 56)]
    res.add((rk(T), rk(np.vstack([R.T.astype(float), T])) - 8))
check('o1.random-56-faces-rank-56-and-56-beyond-the-8-centres', res == {(56, 56)}, str(res))
def pairs_needed(sel):
    used = set()
    for f in sel:
        opts = [((f[0], f[1]), (f[2], f[3])), ((f[0], f[2]), (f[1], f[3])), ((f[0], f[3]), (f[1], f[2]))]
        used |= set(min(opts, key=lambda o: sum(p not in used for p in o)))
    return len(used)
r = [pairs_needed([faces[i] for i in random.sample(range(len(faces)), 56)]) for _ in range(50)]
check('o1.random-56-faces-need-at-least-100-pair-registers', 100 <= min(r) and max(r) <= 112, f'{min(r)}..{max(r)} distinct pair registers (seeded 50 trials, greedy pairing; B74 recorded 105..112)')
check('o1.booked-charge-arithmetic-12.21', abs(14 * 0.3 + 56 * 0.143 - 12.208) < 1e-9 and abs(56 * 0.143 - 8.008) < 1e-9, '14 x 0.3 + 56 x 0.143 = 4.2 + 8.008 (booked rates; 0.143/helper is the J16-H class rate, not derived here)')
done()
