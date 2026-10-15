# SPDX-License-Identifier: Apache-2.0
"""Toy soundness control (standalone, standard library): random small words over F2^3, exhaustive minimum over every
linear extension of the commutation order and every nested frame assignment, against (a) the lo2/hi2 intervals,
(b) the order-free stabbing DP and (c) the dimension-coupled Lagrangian DP with random multipliers.

run(seed, count, mutated=False) returns the number of trials (and of trials with more than one linear extension);
it raises AssertionError on any violation. mutated=True charges negative multipliers at the entry point instead of
the exit point (an invalid rule) and must be caught.
"""
import itertools
import random

H = 3
FULL = (1 << (1 << H)) - 1


def extend(f, v):
    return f if f >> v & 1 else f | sum(1 << (x ^ v) for x in range(1 << H) if f >> x & 1)


def span(vs):
    f = 1
    for v in vs:
        f = extend(f, v)
    return f


def dim(f):
    return f.bit_count().bit_length() - 1


SUBS = sorted({span(c) for k in range(H + 1) for c in itertools.combinations(range(1, 1 << H), k)}, key=lambda f: f.bit_count())


def join(a, b):
    r = a
    for v in range(1 << H):
        if b >> v & 1:
            r = extend(r, v)
    return r


def cost(d):
    return 0.0 if d == 0 else d ** 0.8


def commute(g, h):
    if g[0] == 'add' and h[0] == 'add':
        return g[1] != h[2] and h[1] != g[2]
    if g[0] == 'scale' and h[0] == 'scale':
        return True
    return not (set(g[1:]) & set(h[1:]))


def trial(rng, mutated):
    nreg, ng = rng.randint(2, 4), rng.randint(2, 4)
    ops = []
    for _ in range(ng):
        if rng.random() < 0.8:
            t, s = rng.sample(range(nreg), 2)
            ops.append(('add', t, s))
        else:
            ops.append(('scale', rng.randrange(nreg)))
    S = {q: rng.choice([s for s in SUBS if dim(s) <= 1]) for q in range(nreg)}
    E = {q: rng.choice([e for e in SUBS if e & S[q] == S[q] and dim(e) >= 2]) for q in range(nreg)}
    on = {q: [i for i, g in enumerate(ops) if q in g[1:]] for q in range(nreg)}
    pred = {i: {j for j in range(i) if set(ops[i][1:]) & set(ops[j][1:]) and not commute(ops[i], ops[j])} for i in range(ng)}
    lo, hi = {}, {}
    for i in range(ng):
        f = 1
        for q in ops[i][1:]:
            f = join(f, S[q])
        for j in pred[i]:
            f = join(f, lo[j])
        lo[i] = f
    for i in reversed(range(ng)):
        f = FULL
        for q in ops[i][1:]:
            f &= E[q]
        for j in range(i + 1, ng):
            if i in pred[j]:
                f &= hi[j]
        hi[i] = f
    if any(lo[i] & ~hi[i] for i in range(ng)):
        return None
    exts = [p for p in itertools.permutations(range(ng)) if all(p.index(j) < p.index(i) for i in range(ng) for j in pred[i])]
    best = None
    for p in exts:
        for F in itertools.product(SUBS, repeat=ng):
            total, ok = 0.0, True
            for q in range(nreg):
                seq = [S[q]] + [F[i] for i in p if q in ops[i][1:]] + [E[q]]
                for a, b in zip(seq, seq[1:]):
                    if a & ~b:
                        ok = False
                        break
                    total += cost(dim(b) - dim(a))
                if not ok:
                    break
            if not ok:
                continue
            for i in range(ng):
                assert F[i] & lo[i] == lo[i] and F[i] & ~hi[i] == 0, 'lo2/hi2 unsound'
            if best is None or total < best:
                best = total
    if best is None:
        return None
    for t in range(6):
        lam = {i: (0.0 if t == 0 else rng.uniform(-1, 1)) for i, g in enumerate(ops) if g[0] == 'add'}
        L = 0.0
        for q in range(nreg):
            items = [(lo[i], hi[i], lam.get(i, 0.0) * (1 if ops[i][1] == q else -1) if ops[i][0] == 'add' else 0.0) for i in on[q]]
            cand = sorted({S[q], E[q]} | {F for l, h, _ in items for F in SUBS if F & l == l and F & ~h == 0}, key=lambda f: f.bit_count())
            inl = [[it[0] & ~V == 0 for it in items] for V in cand]
            inh = [[V & ~it[1] == 0 for it in items] for V in cand]
            s0, e0 = cand.index(S[q]), cand.index(E[q])
            f = [None] * len(cand)
            f[s0] = 0.0 if mutated else sum(it[2] * dim(S[q]) for k, it in enumerate(items) if inl[s0][k] and it[2] > 0)
            for j in range(len(cand)):
                if j == s0:
                    continue
                bj = None
                for i2 in range(len(cand)):
                    if f[i2] is None or cand[i2] == cand[j] or cand[i2] & ~cand[j]:
                        continue
                    if any(inl[j][k] and not inl[i2][k] and not inh[j][k] for k in range(len(items))):
                        continue
                    v = f[i2] + cost(dim(cand[j]) - dim(cand[i2]))
                    for k, it in enumerate(items):
                        if mutated:
                            if it[2] > 0 and inh[i2][k] and not inh[j][k]:
                                v += it[2] * dim(cand[i2])
                        elif it[2] > 0 and inl[j][k] and not inl[i2][k]:
                            v += it[2] * dim(cand[j])
                        if it[2] < 0 and inh[i2][k] and not inh[j][k]:
                            v += it[2] * dim(cand[i2])
                    if bj is None or v < bj:
                        bj = v
                f[j] = bj
            tail = (lambda it: it[2] != 0) if mutated else (lambda it: it[2] < 0)
            L += f[e0] + sum(it[2] * dim(E[q]) for k, it in enumerate(items) if inh[e0][k] and tail(it))
        assert L <= best + 1e-9, 'Lagrangian bound above the exact minimum'
    return best, len(exts)


def run(seed, count, mutated=False):
    rng = random.Random(seed)
    done = multi = 0
    while done < count:
        r = trial(rng, mutated)
        if r is None:
            continue
        done += 1
        multi += r[1] > 1
    return done, multi
