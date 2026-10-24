"""Exact checks for free per-register address twists in the formal bit model.

Model: R binary roles holding elements of F2[M_3(Q)].  A paid call is
D_N([A]) = I + ([A]-1) x y^T with A rank one and y^T x = 1 over F2.  Free
operations are binary XOR mixing and a per-register twist [B] -> [P B Q^T]
for axis permutations P, Q.  Operators are matrices over the skew group ring
F2[M_3(Q)] x| G, represented exactly as finite sets of (frame, twist) pairs.

The verifier checks the finite statements recorded in README.md and PROOF.md:
the one-sided flattening lemma on seeded random words, the exact direct
nine-call word, and the two-sided seven-call relaxation witness (all 5040
orders agree with the target in the square-zero quotient, none exactly).
Python 3.12 standard library only.  Apache-2.0.  JoyboyBrian, with
substantial assistance from Anthropic Claude (Claude Code, Opus 5.5).
"""

import itertools
import random
import sys

M = 3
P_ID = (0, 1, 2)
TW_ID = (P_ID, P_ID)
Z9 = (0,) * 9

EXPECTED = {
    "direct_word_calls": 9,
    "floor_three_targets": 9,
    "witness_calls": 7,
    "witness_orders": 5040,
    "witness_exact_orders": 0,
    "random_words_per_side": 120,
}


def fail(msg):
    print("FAIL:", msg)
    sys.exit(1)


def check(cond, msg):
    if not cond:
        fail(msg)


def unit(i, j):
    a = [0] * 9
    a[M * i + j] = 1
    return tuple(a)


def mat_add(*frames):
    return tuple(sum(col) for col in zip(*frames))


def act(tw, a):
    """Twist (pl, pr): (P_l A P_r^T)[pl[i], pr[j]] = A[i, j]."""
    pl, pr = tw
    out = [0] * 9
    for i in range(M):
        for j in range(M):
            out[M * pl[i] + pr[j]] = a[M * i + j]
    return tuple(out)


def tw_comp(s, t):
    return (tuple(s[0][t[0][i]] for i in range(M)), tuple(s[1][t[1][i]] for i in range(M)))


def tw_inv(t):
    def inv(p):
        q = [0] * M
        for i, v in enumerate(p):
            q[v] = i
        return tuple(q)
    return (inv(t[0]), inv(t[1]))


ONE = frozenset({(Z9, TW_ID)})
ZERO = frozenset()


def mul(x, y):
    out = set()
    for a, g in x:
        for b, h in y:
            out ^= {(tuple(u + v for u, v in zip(a, act(g, b))), tw_comp(g, h))}
    return frozenset(out)


def xsum(items):
    out = set()
    for v in items:
        out ^= v
    return frozenset(out)


def mat_mul(x, y):
    n = len(x)
    return [[xsum(mul(x[i][k], y[k][j]) for k in range(n)) for j in range(n)] for i in range(n)]


def ident(n):
    return [[ONE if i == j else ZERO for j in range(n)] for i in range(n)]


def paid(n, x, y, a):
    check(sum(u & v for u, v in zip(x, y)) % 2 == 1, "paid projector is not idempotent")
    check(rank_q_one(a), "paid frame is not rank one")
    d = frozenset({(a, TW_ID), (Z9, TW_ID)})
    return [[xsum([ONE if i == j else ZERO, d if x[i] and y[j] else ZERO]) for j in range(n)] for i in range(n)]


def twist(n, tws):
    return [[frozenset({(Z9, tws[i])}) if i == j else ZERO for j in range(n)] for i in range(n)]


def xor_into(n, dst, src):
    m = ident(n)
    m[dst][src] = ONE
    return m


def product(n, ops):
    t = ident(n)
    for op in ops:
        t = mat_mul(op, t)
    return t


def rank_q_one(a):
    rows = [a[M * i:M * i + M] for i in range(M)]
    nz = [r for r in rows if any(r)]
    if not nz:
        return False
    r0 = nz[0]
    return all(r0[i] * r[j] == r0[j] * r[i] for r in nz for i in range(M) for j in range(M))


def square_zero(entry):
    """Image in Lambda x| G with Lambda = F2 + M_3(F2) eps, eps^2 = 0."""
    c = 0
    lin = [0] * 9
    tw = set()
    for a, g in entry:
        c ^= 1
        lin = [(u + v) % 2 for u, v in zip(lin, a)]
        tw ^= {g}
    return c, tuple(lin), frozenset(tw)


def sz_matrix(t):
    return [[square_zero(e) for e in row] for row in t]


def target(cs, n):
    return [[frozenset({(cs[i], TW_ID)}) if i == j and i < len(cs) else (ONE if i == j else ZERO)
             for j in range(n)] for i in range(n)]


def rank_f2(rows):
    rank = 0
    rows = [r for r in rows if r]
    while rows:
        pivot = rows.pop()
        if not pivot:
            continue
        rank += 1
        low = pivot & -pivot
        rows = [r ^ pivot if r & low else r for r in rows]
        rows = [r for r in rows if r]
    return rank


def flattened_rank(sz, side):
    """Rank of L: c -> w.  'left' rows (r,i) cols (s,l); 'right' rows (r,l) cols (s,i)."""
    n = len(sz)
    rows = []
    for r in range(n):
        for p in range(M):
            bits = 0
            for s in range(n):
                lin = sz[r][s][1]
                for q in range(M):
                    val = lin[M * p + q] if side == "left" else lin[M * q + p]
                    if val:
                        bits |= 1 << (M * s + q)
            rows.append(bits)
    return rank_f2(rows)


# Targets: invertible lower-triangular integer frames, invertible mod 2.
C1 = mat_add(unit(0, 0), unit(1, 1), unit(2, 2))
C2 = mat_add(C1, unit(1, 0))
C3 = mat_add(C1, unit(2, 1))
TARGETS = [C1, C2, C3]


def columns(c):
    out = []
    for j in range(M):
        col = [0] * 9
        for i in range(M):
            col[M * i + j] = c[M * i + j]
        out.append(tuple(col))
    return out


def direct_word(n):
    ops = []
    for r, c in enumerate(TARGETS):
        e = tuple(int(k == r) for k in range(n))
        ops += [paid(n, e, e, col) for col in columns(c)]
    return ops


def check_direct():
    for n in (3, 4):
        ops = direct_word(n)
        check(len(ops) == EXPECTED["direct_word_calls"], "direct word length")
        check(product(n, ops) == target(TARGETS, n), "direct word is not exact")
        check(product(n, ops[1:]) != target(TARGETS, n), "deleted-call control passed")
    bad = direct_word(3)
    bad[4] = paid(3, (0, 1, 0), (0, 1, 0), mat_add(unit(1, 1), unit(2, 1)))
    check(product(3, bad) != target(TARGETS, 3), "mutated-frame control passed")
    floor = flattened_rank(sz_matrix(target(TARGETS, 3)), "left")
    check(floor == EXPECTED["floor_three_targets"], "target flattened rank")
    check(flattened_rank(sz_matrix(target(TARGETS, 3)), "right") == floor, "right flattening of target")
    print("direct word: exact with 0/1 dirty helper; deletion and frame mutation rejected; floor", floor)


def random_frame(rng):
    while True:
        a = [rng.choice((-2, -1, 0, 1, 1, 2, 3)) for _ in range(M)]
        b = [rng.choice((-1, 0, 1, 1, 2)) for _ in range(M)]
        f = tuple(a[i] * b[j] for i in range(M) for j in range(M))
        if any(f):
            return f


def random_projector(rng, n):
    while True:
        x = tuple(rng.randint(0, 1) for _ in range(n))
        y = tuple(rng.randint(0, 1) for _ in range(n))
        if sum(u & v for u, v in zip(x, y)) % 2 == 1:
            return x, y


def random_perm(rng):
    p = list(P_ID)
    rng.shuffle(p)
    return tuple(p)


def random_word(rng, n, side, calls):
    ops = []
    for _ in range(calls):
        tws = []
        for _ in range(n):
            p = random_perm(rng)
            q = random_perm(rng)
            tws.append((p, P_ID) if side == "left" else (P_ID, q))
        pre = []
        for _ in range(rng.randint(0, 2)):
            d, s = rng.sample(range(n), 2)
            pre.append(xor_into(n, d, s))
        x, y = random_projector(rng, n)
        ops += pre + [twist(n, tws), paid(n, x, y, random_frame(rng)),
                      twist(n, [tw_inv(t) for t in tws])] + pre[::-1]
        if rng.random() < 0.5:
            d, s = rng.sample(range(n), 2)
            ops.append(xor_into(n, d, s))
    return ops


def check_one_sided():
    rng = random.Random(20261023)
    worst = {"left": 0, "right": 0}
    violations = {"left": 0, "right": 0, "cross": 0}
    for side in ("left", "right"):
        for _ in range(EXPECTED["random_words_per_side"]):
            n = rng.choice((3, 4))
            k = rng.randint(1, 4)
            sz = sz_matrix(product(n, random_word(rng, n, side, k)))
            rk = flattened_rank(sz, side)
            worst[side] = max(worst[side], rk - k)
            if rk > k:
                violations[side] += 1
            other = "right" if side == "left" else "left"
            if flattened_rank(sz, other) > k:
                violations["cross"] += 1
    check(violations["left"] == 0 and violations["right"] == 0, "one-sided flattening exceeded call count")
    check(violations["cross"] > 0, "wrong-side flattening control never exceeded call count")
    print("one-sided lemma: %d random words per side, flattened rank <= calls; wrong flattening exceeds on %d words"
          % (EXPECTED["random_words_per_side"], violations["cross"]))


SW = ((1, 0, 2), (1, 0, 2))  # simultaneous swap of address axes 0 and 1


def witness_calls(private_twist=SW):
    calls = [("J", None)] + [(kind, s) for s in range(3) for kind in ("P", "D")]

    def ops_for(call):
        kind, s = call
        if kind == "J":
            return [paid(3, (1, 1, 1), (1, 1, 1), unit(0, 0))]
        e = tuple(int(r == s) for r in range(3))
        if kind == "D":
            return [paid(3, e, e, unit(2, 2))]
        tws = [TW_ID if r == s else private_twist for r in range(3)]
        return [twist(3, tws), paid(3, (1, 1, 1), e, unit(1, 1)), twist(3, [tw_inv(t) for t in tws])]
    return calls, ops_for


def check_witness():
    ident_target = target([C1, C1, C1], 3)
    want = sz_matrix(ident_target)
    calls, ops_for = witness_calls()
    check(len(calls) == EXPECTED["witness_calls"], "witness length")
    orders = exact = 0
    for order in itertools.permutations(range(len(calls))):
        ops = [op for idx in order for op in ops_for(calls[idx])]
        t = product(3, ops)
        orders += 1
        check(sz_matrix(t) == want, "witness order disagrees with target in square-zero quotient")
        if t == ident_target:
            exact += 1
    check(orders == EXPECTED["witness_orders"], "witness order count")
    check(exact == EXPECTED["witness_exact_orders"], "witness exact-order count")
    check(flattened_rank(want, "left") == 9 and flattened_rank(want, "right") == 9, "witness flattened ranks")
    # Controls: a different target, or untwisted private calls, break the relaxation match.
    base = [op for c in calls for op in ops_for(c)]
    check(sz_matrix(product(3, base)) != sz_matrix(target(TARGETS, 3)), "altered-target control passed")
    calls0, ops0 = witness_calls(private_twist=TW_ID)
    check(sz_matrix(product(3, [op for c in calls0 for op in ops0(c)])) != want, "untwisted control passed")
    callsL, opsL = witness_calls(private_twist=((1, 0, 2), P_ID))
    check(sz_matrix(product(3, [op for c in callsL for op in opsL(c)])) != want, "left-only twist control passed")
    print("two-sided witness: %d calls, all %d orders match the target mod square-zero, %d exact"
          % (len(calls), orders, exact))


def main():
    check_direct()
    check_one_sided()
    check_witness()
    print("PASS bit-address-twist-register-floor")


if __name__ == "__main__":
    main()
