"""Theorem F (flag chains flatten onto N at no higher price). Stdlib only."""
import os, sys, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e8lib as E
n = E.n
fails = []
def ck(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg, flush=True)
    if not cond: fails.append(msg)
def span_set(gens):
    S = {0}
    for g in gens:
        if g not in S: S |= {s ^ g for s in S}
    return S
def dim(S): return len(S).bit_length() - 1
def orth_to(S):   # ports whose label is orthogonal (form) to every element of S
    return [p for p in range(n) if all(E.form(E.LABEL[p], x) == 0 for x in S)]
def inside(S): return [p for p in range(n) if E.LABEL[p] in S]
def flag(m, rng):
    F = [span_set([rng.randrange(1, 512) for _ in range(rng.randint(4, 8))])]
    for i in range(m):
        base = sorted(F[-1])
        F.append(span_set([rng.choice(base) for _ in range(rng.randint(0, max(0, dim(F[-1]) - 1)))]))
    return F
def rand_vec(supp, rng):
    v = [0] * n
    for p in supp:
        if rng.random() < 0.7: v[p] = rng.randint(-3, 3)
    return v
def run_chain(F, rng, nested=True):
    ev = []   # time-ordered events (kind, vector)
    for lvl, Fi in enumerate(F):
        reads = inside(Fi); writes = orth_to(Fi)
        items = []
        for _ in range(rng.randint(0, 2)): items.append(('R', rand_vec(reads, rng)))
        for _ in range(rng.randint(0, 2)): items.append(('W', rand_vec(writes, rng)))
        rng.shuffle(items); ev += items
    X = [[0] * n for _ in range(n)]
    seen_reads = [0] * n
    for kind, v in ev:
        if kind == 'R':
            for p in range(n): seen_reads[p] += v[p]
        else:
            for s in range(n):
                if v[s]:
                    for p in range(n):
                        if seen_reads[p]: X[s][p] += v[s] * seen_reads[p]
    w = [sum(v[s] for k, v in ev if k == 'W') for s in range(n)]
    r = [sum(v[p] for k, v in ev if k == 'R') for p in range(n)]
    return X, w, r
rng = random.Random(12)
okF = okP = True; total = 0; nonzero = 0; mismatch_ctrl = 0; ctrl = 0
for t in range(60):
    m = rng.randint(1, 4)
    F = flag(m, rng)
    X, w, r = run_chain(F, rng)
    S = [s for s in range(n) if w[s]]; T = [p for p in range(n) if r[p]]
    for s in range(n):
        for p in range(n):
            if (E.NR[s] >> p) & 1:
                if X[s][p] != w[s] * r[p]: okF = False
                if w[s] * r[p]: nonzero += 1
    mass = dim(F[0]) - dim(F[-1])
    if E.rho(S, T) > mass: okP = False
    total += 1
ck(okF, f'N o X = N o (w r^T) on all {total} random flag chains (nested frames, interleaved reads and writes, depth 1 to 4)')
ck(nonzero > 0, f'the test is not vacuous: {nonzero} N entries with w(s) r(p) != 0')
ck(okP, 'price: rho(supp w, supp r) <= dim F_0 - dim F_m on every chain (reads in F_0, writes orthogonal to F_m)')
# control: frames that are not nested (an ascent) break the flattening
for t in range(60):
    F = [span_set([rng.randrange(1, 512) for _ in range(rng.randint(3, 7))]) for _ in range(3)]
    X, w, r = run_chain(F, rng)
    ctrl += 1
    if any(((E.NR[s] >> p) & 1) and X[s][p] != w[s] * r[p] for s in range(n) for p in range(n)): mismatch_ctrl += 1
ck(mismatch_ctrl > 0, f'control: with non-nested frames the flattening fails on {mismatch_ctrl} of {ctrl} random programs (hypothesis is used)')
print('PASS_FLATTEN' if not fails else 'FAILED_FLATTEN')
sys.exit(1 if fails else 0)
