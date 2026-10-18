"""Group G2 (lift route): exact checks of the g1/PROOF.md data (sections 6, 9, 10, 11) and of Theorem 9.3 on small cases.
Every instance is enumerated over ALL admissible B (enumall.c, exhaustive), so 'minimisers' means the full list.
Prints one line per fact; verify.sh matches them with checks/expect.py."""
import sys, os, json, itertools, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from kit import *

def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])

def projeq(a, b):
    return all(x == 0 for x in cross(a, b))

def analyse(name, py_cross=True):
    P, Q = load_cfg(name); v = len(P)
    best, ms, R, A, free = enum(P, Q)
    Bs = [tomat(g, free, v) for _, g in ms]
    rk = sorted(set(tuple(blockranks(B, R, A)) for B in Bs))
    fl = jsign_batch(Bs, R, A, True)
    whole = [tus(B, range(v), range(v)) for B in Bs]
    blk = [[tus(B, R[j], A[j]) for j in range(3)] for B in Bs]
    assert all(f[0][1:] == tuple(b) for f, b in zip(fl, blk)), 'jsign block flags disagree with tusign'
    info = dict(P=P, Q=Q, v=v, best=best, ms=ms, R=R, A=A, free=free, Bs=Bs, ranks=rk, fl=fl, whole=whole, blk=blk)
    if py_cross:
        info['py'] = [py_flags(B, R, A) for B in Bs]
        assert all(p == f[0] for p, (f) in zip(info['py'], fl)), 'python Camion disagrees with jsign'
    return info

def lifts_ok(I, idx):
    """Exact Fraction block ranks of the joint signing found by the Camion system equal the F2 ranks?"""
    out = []
    for i in idx:
        (f, sgn) = I['fl'][i]
        if not f[0]:
            out.append(None); continue
        S = signed_matrix(I['Bs'][i], sgn)
        out.append(block_q(S, I['R'], I['A']) == blockranks(I['Bs'][i], I['R'], I['A']))
    return out

# ---------------------------------------------------------------- 6. whole-matrix TU fails: v = 9
I = analyse('cex_wholeTS_v9.json')
v = I['v']; ones = sorted(bin(g).count('1') for _, g in I['ms'])
print("W9 v=%d f=%d mincost=%d minimisers=%d block ranks %s offdiag-ones %d..%d" % (v, len(I['free']), I['best'], len(I['ms']), I['ranks'], ones[0], ones[-1]))
print("W9 whole-matrix TU-signable: %d of %d; all three blocks TU-signable: %d of %d; jointly block-TU signable: %d of %d; python Camion agrees: %s" % (
    sum(I['whole']), len(I['ms']), sum(all(b) for b in I['blk']), len(I['ms']), sum(f[0][0] for f in I['fl']), len(I['ms']), all(p == f[0] for p, f in zip(I['py'], I['fl']))))
lo = lifts_ok(I, range(len(I['ms'])))
print("W9 joint signing has exact Q block ranks equal to the F2 ranks for %d of %d minimisers; (A) %d >= v = %d: %s" % (sum(1 for x in lo if x), len(I['ms']), I['best'], v, I['best'] >= v))
# fewest-ones minimiser = the matrix printed in g1/PROOF.md section 6
want = ["100100001", "010000001", "001000100", "011100000", "000010000", "000001000", "100000100", "000000010", "001000001"]
mins8 = [B for (c, g), B in zip(I['ms'], I['Bs']) if bin(g).count('1') == 8]
print("W9 the 8-ones minimiser of PROOF section 6 occurs: %s (number of 8-ones minimisers %d)" % (any(["".join(map(str, r)) for r in B] == want for B in mins8), len(mins8)))
P, Q = I['P'], I['Q']
print("W9 degeneracy: lines 1,2 equal %s; lines 4,6 equal %s; lines 7,8 same projective line %s; points 4,5 coincide %s" % (
    projeq(Q[1], Q[2]), projeq(Q[4], Q[6]), projeq(Q[7], Q[8]), projeq(P[4], P[5])))

# ---------------------------------------------------------------- 11. joint block-TU fails: v = 7 (X1 evidence)
I7 = analyse('cex_joint_v7.json')
v = I7['v']
print("J7 v=%d f=%d mincost=%d minimisers=%d off-diagonal ones %s block ranks %s" % (v, len(I7['free']), I7['best'], len(I7['ms']), sorted(bin(g).count('1') for _, g in I7['ms']), I7['ranks']))
print("J7 jointly block-TU signable: %d of %d; whole-matrix TU-signable: %d; block 2 TU-signable: %d; blocks 0,1 TU-signable: %d,%d; python Camion agrees: %s; (A) %d >= v = %d: %s" % (
    sum(f[0][0] for f in I7['fl']), len(I7['ms']), sum(I7['whole']), sum(b[2] for b in I7['blk']), sum(b[0] for b in I7['blk']), sum(b[1] for b in I7['blk']),
    all(p == f[0] for p, f in zip(I7['py'], I7['fl'])), I7['best'], v, I7['best'] >= v))
M7 = [[-1, 0, 0, -2, 0, 0, 0], [0, 3, 0, 0, 0, 0, 0], [0, 0, 1, -2, 1, 0, 0], [0, 0, 0, -2, 0, 0, -1], [-2, 0, 0, 0, -2, 0, 2], [0, 0, 0, 0, 0, 2, 0], [0, 0, 2, 0, 0, 0, 2]]
supp7 = [[int(x != 0) for x in r] for r in M7]
hit = [i for i, B in enumerate(I7['Bs']) if B == supp7]
print("J7 lift: the printed rational 7x7 matrix has the support of a minimiser: %s; exact Q block ranks %s, F2 block ranks %s" % (
    bool(hit), block_q(M7, I7['R'], I7['A']), blockranks(supp7, I7['R'], I7['A'])))
print("J7 block 2 has %d nonzero rows of %d (full row rank 4 for every odd lift: F2 rank 4 = number of nonzero rows)" % (
    sum(1 for t in I7['R'][2] if any(I7['Bs'][hit[0]][t][s] for s in I7['A'][2])), len(I7['R'][2])) if hit else "J7 no hit")

print("J7 submatrix rows 0,2,3,4 x cols 0,3,4,6 (induced odd theta once the leaf column 2 is dropped) TU-signable, per minimiser (by ones): %s" % sorted(
    (bin(g).count('1'), tus(B, [0, 2, 3, 4], [0, 3, 4, 6])) for (_, g), B in zip(I7['ms'], I7['Bs'])))
# second refutation instance of the same kind (jclimb2): v = 10
I10 = analyse('nojoint_21_1.json', py_cross=False)
print("J10 v=%d f=%d mincost=%d minimisers=%d block ranks %s jointly block-TU signable %d; block-wise TU-signable (b0 b1 b2) %s; (A) %s" % (
    I10['v'], len(I10['free']), I10['best'], len(I10['ms']), I10['ranks'], sum(f[0][0] for f in I10['fl']), [tuple(int(x) for x in b) for b in I10['blk']], I10['best'] >= I10['v']))

# ---------------------------------------------------------------- 9/10. the two failure modes F1 and F2 (Cech)
IC = analyse('cech_v8.json', py_cross=False)
cech = [i for i, f in enumerate(IC['fl']) if (not f[0][0]) and all(f[0][1:])]
print("C8 v=%d f=%d mincost=%d minimisers=%d; minimisers with all blocks TU-signable but NO joint signing (Cech, F2): %d; jointly signable: %d" % (
    IC['v'], len(IC['free']), IC['best'], len(IC['ms']), len(cech), sum(f[0][0] for f in IC['fl'])))
pc = [py_flags(IC['Bs'][i], IC['R'], IC['A']) for i in cech[:3]]
print("C8 python Camion agrees on the Cech minimisers: %s" % all(p == IC['fl'][i][0] for p, i in zip(pc, cech[:3])))
IS = analyse('supmin_fail_v8.json')
v = IS['v']
print("S8 v=%d f=%d mincost=%d minimisers=%d ones %s block ranks %s; whole-TU %s; block TU flags %s; jointly signable %d" % (
    v, len(IS['free']), IS['best'], len(IS['ms']), sorted(bin(g).count('1') for _, g in IS['ms']), IS['ranks'], [int(x) for x in IS['whole']],
    [tuple(int(x) for x in b) for b in IS['blk']], sum(f[0][0] for f in IS['fl'])))
print("S8 the two minimisers differ by one swap of ones: %s" % (bin(IS['ms'][0][1] ^ IS['ms'][1][1]).count('1') == 2))

# ---------------------------------------------------------------- Lemma 9.1 / F7 / odd theta
F7 = [[1, 1, 0], [0, 1, 1], [1, 0, 1], [1, 1, 1]]
J2 = [[1, 1], [1, 1]]; C3 = [[1, 1, 0], [0, 1, 1], [1, 0, 1]]
print("L91 TU-signable: J2 %s, odd 3-cycle %s, F7 submatrix [110,011,101,111] %s" % (tus(J2, range(2), range(2)), tus(C3, range(3), range(3)), tus(F7, range(4), range(3))))
theta = [[1, 1, 1, 0], [0, 0, 1, 1], [0, 1, 0, 1], [1, 0, 0, 1]]
print("L91 odd theta of supmin_fail_v8 (rows 0,1,2,6 x cols 0,3,4,6): TU-signable %s" % tus(theta, range(4), range(4)))

# ---------------------------------------------------------------- Theorem 9.3 against the brute-force oracle
cases = []
def add(I, idx, tag):
    for i in idx:
        cases.append((tag, I['Bs'][i], I['R'], I['A']))
add(I7, range(len(I7['Bs'])), 'J7'); add(IS, range(len(IS['Bs'])), 'S8'); add(IC, cech[:2] + [i for i, f in enumerate(IC['fl']) if f[0][0]][:3], 'C8')
add(I, [0, 1, 2], 'W9')
rng = random.Random(93)
vals = (-2, -1, 0, 1, 2)
pool = [x for x in itertools.product(vals, repeat=3) if any(x)]
n_rand = 0
while n_rand < 40:
    v = rng.randrange(5, 8); P = []; Q = []
    while len(P) < v:
        if P and rng.random() < 0.9:
            s = rng.randrange(len(P)); t = rng.randrange(len(P))
            p = rng.choice([x for x in pool if dot(x, Q[s]) == 0] or pool); q = rng.choice([x for x in pool if dot(P[t], x) == 0] or pool)
        else:
            p = rng.choice(pool); q = rng.choice(pool)
        if dot(p, q):
            P.append(list(p)); Q.append(list(q))
    R, A, free = setup(P, Q)
    if len(free) < 4 or len(free) > 40:
        continue
    B = tomat(rng.getrandbits(len(free)) | rng.getrandbits(len(free)), free, v)
    cases.append(('R%d' % n_rand, B, R, A)); n_rand += 1
agree = 0; tot = 0; stats = {}; skipped = 0
for tag, B, R, A in cases:
    br = brute_batch([B], R, A)[0]
    if br is None:
        skipped += 1; continue
    fl = jsign_batch([B], R, A)[0]
    tot += 1; agree += (br == fl)
    key = pretty_flags(fl); stats[key] = stats.get(key, 0) + 1
print("T93 Camion system (jsign.c) vs exhaustive signings x exhaustive minors (brutetu.c): %d instances, %d agree on (J,b0,b1,b2), %d skipped as out of range" % (tot, agree, skipped))
print("T93 outcome classes seen: %s" % ", ".join("%s x%d" % (k, stats[k]) for k in sorted(stats)))
print("T93 Cech case (every block signable, no joint signing) confirmed by the exhaustive oracle: %s" % any(
    brute_batch([B], R, A)[0] == (False, True, True, True) for tag, B, R, A in cases if tag == 'C8'))

# ---------------------------------------------------------------- S1's F7* gadget (g1/PROOF.md section 1): a minimiser with a non-TU-signable block
Pg, Qg = load_cfg('gad.json'); vg = len(Pg); Rg, Ag, fg = setup(Pg, Qg)
gm = json.load(open(os.path.join(DATA, 'gad_nonTS_minimiser.json')))
Bg = tomat(gm['g'], fg, vg)
print("GAD v=%d f=%d (cost 19 and 23552 minimisers are the recorded exhaustive 2^29 run); stored minimiser: %d off-diagonal ones, block ranks %s sum %d = 19: %s; block TU-signable flags %s; whole B TU-signable %s" % (
    vg, len(fg), bin(gm['g']).count('1'), blockranks(Bg, Rg, Ag), sum(blockranks(Bg, Rg, Ag)), sum(blockranks(Bg, Rg, Ag)) == 19, [tus(Bg, Rg[j], Ag[j]) for j in range(3)], tus(Bg, range(vg), range(vg))))

# ---------------------------------------------------------------- 14 instances of jclimb2 with no jointly signable minimiser
rows = []
for i in range(1, 15):
    Ik = analyse('nojoint_21_%d.json' % i, py_cross=False)
    rows.append((Ik['v'], Ik['best'], len(Ik['ms']), sum(f[0][0] for f in Ik['fl']), Ik['best'] >= Ik['v']))
print("NJ14 instances nojoint_21_1..14 (v 7-10): minimisers without a joint block-TU signing: %d of %d instances (joint signings in total %d); (A) cost >= v in %d; (v, cost): %s" % (
    sum(1 for r in rows if r[3] == 0), len(rows), sum(r[3] for r in rows), sum(1 for r in rows if r[4]), [(r[0], r[1]) for r in rows]))
