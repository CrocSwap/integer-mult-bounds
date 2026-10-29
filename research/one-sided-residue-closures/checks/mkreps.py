# Orbit bookkeeping for the non-E8 direction masks (dirs.pkl) under the frame stabiliser G (G.npy), and the covering targets.
#  * every element of G preserves the frame and acts label-linearly (so covering facts transport along G);
#  * the 17 representative masks of data/targets.txt have pairwise disjoint G-orbits whose union is ALL 21,340 non-E8 masks with |Off|<=89;
#  * the root target is Off(r0) (53 lines).   Writes dirreps.pkl (input of annon.py).   Prints PASS/FAIL lines.
import numpy as np, pickle, os, sys
import p112 as p
from paths import DATA
G = np.load('G.npy'); D = pickle.load(open('dirs.pkl', 'rb'))
ok = True
def rep(name, cond, msg=''):
    global ok; ok &= bool(cond); print(('PASS ' if cond else 'FAIL ') + name + (' ' + msg if msg else ''))
rep('G has 172032 elements', len(G) == 172032, str(len(G)))
fr = np.array(sorted(p.FRAME))
rep('G preserves the frame', all(set(g[fr].tolist()) == set(fr.tolist()) for g in G[:2000]) and (np.sort(G[:, fr], axis=1) == fr).all())
# label-linearity of every element: express each line label in a basis of 9 independent labels (lines bi)
LAB = p.LAB; basis = []; coeff = {}
span = {0: 0}
for i in range(120):
    if int(LAB[i]) not in span:
        k = len(basis); basis.append(i)
        for v, m in list(span.items()): span[v ^ int(LAB[i])] = m | (1 << k)
        if len(basis) == 9: break
assert len(basis) == 9
cm = np.array([span[int(LAB[i])] for i in range(120)])     # coefficient bitmask over basis
Gi = G.astype(np.int64)
imgb = LAB[Gi[:, basis]]                                   # |G| x 9 images of basis labels
pred = np.zeros((len(G), 120), dtype=np.int64)
for k in range(9):
    sel = ((cm >> k) & 1).astype(bool)
    pred[:, sel] ^= imgb[:, [k]]
rep('every element of G is label-linear (label(g(l)) = A label(l))', (pred == LAB[Gi]).all())
pos = {g: i for i, g in enumerate(p.P)}
def hexm_to_global(lo, hi):
    m = int(lo, 16) | (int(hi, 16) << 64)
    return tuple(p.P[i] for i in range(112) if m >> i & 1)
T = [l.split() for l in open(os.path.join(DATA, 'targets.txt')) if l.strip()]
Dnon = set(D['non']); allnon = set(Dnon)
# root target
r0 = p.P[0]; off_r = tuple(i for i in p.P if p.IP[i, r0] != 0)
rt = [t for t in T if t[0] == 'root'][0]
rep('root target = Off(r0), 53 lines', hexm_to_global(rt[1], rt[2]) == off_r and len(off_r) == 53 and int(rt[4]) == pos[r0])
def img_masks(o):
    idx = G[:, list(o)].astype(np.int64)                    # |G| x |o| global indices
    lo = np.zeros(len(G), dtype=np.uint64); hi = np.zeros(len(G), dtype=np.uint64)
    posarr = np.array([pos.get(i, -1) for i in range(120)])
    ps = posarr[idx]
    assert (ps >= 0).all()
    for c in range(ps.shape[1]):
        pc = ps[:, c]
        lo |= np.where(pc < 64, np.uint64(1) << np.minimum(pc, 63).astype(np.uint64), np.uint64(0))
        hi |= np.where(pc >= 64, np.uint64(1) << np.maximum(pc - 64, 0).astype(np.uint64), np.uint64(0))
    return set(zip(lo.tolist(), hi.tolist()))
def to_masks(S):
    out = set()
    for o in S:
        lo = hi = 0
        for i in o:
            q = pos[i]
            if q < 64: lo |= 1 << q
            else: hi |= 1 << (q - 64)
        out.add((lo, hi))
    return out
allmasks = to_masks(Dnon)
seen = set(); reps = []
for t in T:
    if t[0] == 'root': continue
    o = hexm_to_global(t[1], t[2]); sz = len(o)
    assert o in Dnon, t
    orb = img_masks(o)
    rep('orbit of %s: %d masks, all in the direction list, disjoint from earlier orbits' % (t[0], len(orb)), orb <= allmasks and not (orb & seen))
    seen |= orb
    tags = D['tags'][tuple(sorted(o))]
    reps.append((sz, len(orb), o, tags))
rep('the 17 orbits cover all %d non-E8 masks with |Off|<=89' % len(allmasks), seen == allmasks, '%d vs %d' % (len(seen), len(allmasks)))
rep('orbit sizes sum to 21340', sum(r[1] for r in reps) == 21340 == len(allmasks))
big = [r for r in reps if r[0] == 89]
rep('Fact D correction: exactly one orbit with |Off| = 89, of 3584 directions', len(big) == 1 and big[0][1] == 3584)
# root/frame masks: single G-orbits
rm = to_masks(D['rootmasks']); roots = [m for m in D['rootmasks'] if len(m) == 53]; frs = [m for m in D['rootmasks'] if len(m) == 56]
rep('direction list: 112 root masks (|Off|=53) and 8 frame masks (|Off|=56), nothing else with |Off|<=69 but 70+', len(roots) == 112 and len(frs) == 8 and min(len(o) for o in Dnon) == 70)
pickle.dump(reps, open('dirreps.pkl', 'wb'))
print('PASS mkreps' if ok else 'FAIL mkreps'); sys.exit(0 if ok else 1)
