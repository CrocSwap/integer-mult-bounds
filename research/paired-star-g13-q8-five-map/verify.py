#!/usr/bin/env python3
"""Check the consecutive-halves paired-star map-count.

The written argument is PROOF.md. These checks fail closed if the state
machine, the Laurent block factors, or the five-map pigeonhole disagree
with that argument. They do not search for an interleaved word.
"""

from itertools import product
import random


def require(ok, message):
    if not ok:
        raise SystemExit(message)


MUL = [[0] * 16 for _ in range(16)]
INV = [0] * 16


def _mul_raw(a, b):
    p = 0
    for _ in range(4):
        if b & 1:
            p ^= a
        b >>= 1
        hi = a & 8
        a = (a << 1) & 15
        if hi:
            a ^= 3
    return p


for a in range(16):
    for b in range(16):
        MUL[a][b] = _mul_raw(a, b)
for a in range(1, 16):
    for b in range(1, 16):
        if MUL[a][b] == 1:
            INV[a] = b


def mm(A, B):
    n = len(A)
    C = [[0] * n for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        Ci = C[i]
        for k in range(n):
            aik = Ai[k]
            if not aik:
                continue
            mk = MUL[aik]
            Bk = B[k]
            for j in range(n):
                bjk = Bk[j]
                if bjk:
                    Ci[j] ^= mk[bjk]
    return C


def add(A, B):
    n = len(A)
    return [[A[i][j] ^ B[i][j] for j in range(n)] for i in range(n)]


def zeros(n):
    return [[0] * n for _ in range(n)]


def eye(n):
    M = zeros(n)
    for i in range(n):
        M[i][i] = 1
    return M


def scale(A, s):
    row = MUL[s]
    return [[row[A[i][j]] for j in range(len(A))] for i in range(len(A))]


def invert(A):
    n = len(A)
    M = [A[i][:] + [1 if i == j else 0 for j in range(n)] for i in range(n)]
    for col in range(n):
        piv = next((i for i in range(col, n) if M[i][col]), None)
        require(piv is not None, "singular matrix in a check that uses an inverse")
        M[col], M[piv] = M[piv], M[col]
        invp = INV[M[col][col]]
        M[col] = [MUL[invp][x] for x in M[col]]
        for i in range(n):
            if i != col and M[i][col]:
                f = M[i][col]
                M[i] = [M[i][j] ^ MUL[f][M[col][j]] for j in range(2 * n)]
    return [row[n:] for row in M]


def prod(values):
    p = 1
    for v in values:
        p = MUL[p][v]
    return p


def local_pair(A, B):
    """Return (P, R, P2, R2) for halves with the same B and A' = I + A."""
    d = len(A)
    Ap = [row[:] for row in A]
    for i in range(d):
        Ap[i][i] ^= 1

    def pack(X, Y):
        P = zeros(2 * d)
        R = zeros(2 * d)
        XY = add(X, Y)
        for i in range(d):
            for j in range(d):
                P[i][j] = XY[i][j]
                P[i][d + j] = Y[i][j]
                P[d + i][j] = Y[i][j]
                P[d + i][d + j] = XY[i][j]
                R[i][j] = R[i][d + j] = R[d + i][j] = R[d + i][d + j] = X[i][j]
        return P, R

    P, R = pack(A, B)
    P2, R2 = pack(Ap, B)
    return P, R, P2, R2


def embed(local, leaf, g, d):
    n = d * (g + 1)
    M = zeros(n)
    idx = list(range(d)) + [d * (leaf + 1) + i for i in range(d)]
    for a, ia in enumerate(idx):
        row = local[a]
        for b, ib in enumerate(idx):
            M[ia][ib] = row[b]
    return M


def standard_AB(q, C, D):
    d = 2 * q
    A = zeros(d)
    B = zeros(d)
    for i in range(q):
        A[i][i] = 1
    for i in range(q):
        for j in range(q):
            B[i][q + j] = C[i][j]
            B[q + i][j] = D[i][j]
    return A, B


def q1_legal_pairs():
    idem = []
    for bits in range(16):
        A = [[bits & 1, (bits >> 1) & 1], [(bits >> 2) & 1, (bits >> 3) & 1]]
        if mm(A, A) == A and sum(sum(row) for row in A) != 0:
            # rank 1 over F2: not zero and not full rank I-like with det.
            rows = A
            rank = 0
            if rows[0] != [0, 0]:
                rank += 1
            if rows[1] != [0, 0] and rows[1] != rows[0]:
                rank += 1
            if rank == 1:
                idem.append(A)
    pairs = []
    for A in idem:
        for bits in range(16):
            B = [[bits & 1, (bits >> 1) & 1], [(bits >> 2) & 1, (bits >> 3) & 1]]
            AB, BA = mm(A, B), mm(B, A)
            if add(AB, BA) != B:
                continue
            pairs.append((A, B, bits != 0))
    return pairs


def thin_map(g, d, leaves, core=False):
    n = d * (g + 1)
    Z = zeros(n)
    for leaf in leaves:
        for i in range(d):
            a = d * (leaf + 1) + i
            Z[i][a] ^= 1
            Z[a][i] ^= 1
    if core:
        for i in range(d):
            Z[i][i] ^= 1
    return Z


def sharp_calls(g, q, A, B, keep=None):
    """Consecutive halves in stage order, one thin map after each odd stage.

    keep is an optional set of 0-based stage indices after which a thin map
    is inserted. The default keeps every even index, which is the sharp word.
    """
    d = 2 * q
    P, R, P2, R2 = local_pair(A, B)
    calls = []
    if keep is None:
        keep = set(range(0, g, 2))
    for s in range(g):
        calls.append(("full", embed(P, s, g, d), embed(R, s, g, d), s))
        calls.append(("full", embed(P2, s, g, d), embed(R2, s, g, d), s))
        if s in keep:
            leaves = [s] if s + 1 >= g else [s, s + 1]
            calls.append(("thin", thin_map(g, d, leaves, core=(g % 2 == 0 and s == 0))))
    return calls


def target(v, g, d):
    n = d * (g + 1)
    T = zeros(n)
    allp = prod(v)
    for i in range(d):
        T[i][i] = allp
        for j in range(g):
            T[d * (j + 1) + i][d * (j + 1) + i] = v[j]
    return T


def run_state(calls, v):
    n = len(calls[0][1]) if calls[0][0] == "full" else len(calls[0][1])
    # n from the first matrix
    n = len(calls[0][1])
    pure, deriv = eye(n), zeros(n)
    for call in calls:
        if call[0] == "full":
            _, P, R, s = call
            vv = v[s]
            x = vv ^ 1
            Pp, Pd, Rp = mm(P, pure), mm(P, deriv), mm(R, pure)
            pure = [[pure[i][j] ^ MUL[x][Pp[i][j]] for j in range(n)] for i in range(n)]
            deriv = [[deriv[i][j] ^ MUL[x][Pd[i][j]] ^ MUL[vv][Rp[i][j]] for j in range(n)] for i in range(n)]
        else:
            Z = call[1]
            deriv = add(deriv, mm(Z, pure))
    return pure, deriv


def ad_projector(S, P, v):
    """Conjugate S by I + (v+1) P. Requires P^2 = P and v != 0."""
    x = v ^ 1
    xv = MUL[x][INV[v]]
    PS, SP = mm(P, S), mm(S, P)
    PSP = mm(P, SP)
    xx = MUL[x][xv]
    out = [row[:] for row in S]
    for i in range(len(S)):
        for j in range(len(S)):
            out[i][j] ^= MUL[x][PS[i][j]] ^ MUL[xv][SP[i][j]] ^ MUL[xx][PSP[i][j]]
    return out


def run_normalized(calls, v):
    """Track the normalized coefficient S. Each full call stores its own R."""
    n = len(calls[0][1])
    S = zeros(n)
    for call in calls:
        if call[0] == "full":
            _, P, R, s = call
            S = add(ad_projector(S, P, v[s]), R)
        else:
            S = add(S, call[1])
    return S


def block(M, r, c, d):
    return [row[c:c + d] for row in M[r:r + d]]


def scalar_block(s, d):
    M = zeros(d)
    for i in range(d):
        M[i][i] = s
    return M


def covered_leaves(order, gap):
    out = []
    if gap > 0:
        out.append(order[gap - 1])
    if gap < len(order):
        out.append(order[gap])
    return out


def covered_by_exponents(order, gap):
    remaining = order[gap:]
    found = []
    for s, leaf in enumerate(order):
        needed = order[s + 1:]
        if leaf in remaining:
            got = [x for x in remaining if x != leaf]
        else:
            got = list(remaining)
        if list(got) == list(needed):
            found.append(leaf)
    return found


def factor_indices(order, gap, leaf):
    remaining = order[gap:]
    if leaf in remaining:
        return [x for x in remaining if x != leaf]
    return list(remaining)


def needed_indices(order, leaf):
    return order[order.index(leaf) + 1:]


def check_emission():
    pairs = q1_legal_pairs()
    require(len(pairs) == 24, "expected 24 legal q=1 pairs, found %d" % len(pairs))
    nonzero = sum(1 for _, _, nz in pairs if nz)
    require(nonzero == 18, "expected 18 legal q=1 pairs with B != 0, found %d" % nonzero)
    for A, B, _nz in pairs:
        P, R, P2, R2 = local_pair(A, B)
        require(mm(P, P) == P and mm(P2, P2) == P2, "half is not a projector")
        require(add(P, P2) == eye(4), "halves do not resolve E")
        require(mm(P, P2) == zeros(4) and mm(P2, P) == zeros(4), "halves are not orthogonal")
        for v in (2, 4, 8, 3):
            calls = [("full", P, R, 0), ("full", P2, R2, 0)]
            pure, deriv = run_state(calls, [v])
            x = v ^ 1
            expect_pure = add(eye(4), scale(eye(4), x))
            # I + x I = (1+x) I = v I on the whole 4-space, since E = I there.
            require(pure == scale(eye(4), v), "consecutive halves missed I+xE")
            require(deriv == scale(add(R, R2), v), "consecutive emission is not T")
            require(add(R, R2) == ones_blocks(2), "R+R' is not the paired query T")
            S = run_normalized(calls, [v])
            require(S == add(R, R2), "normalized emission drifted from T")
            require(mm(deriv, invert(pure)) == S, "state machine and normalized S disagree")
    # q=8 standard frame, nonzero legal B, two stages do not commute.
    q = 8
    C = zeros(q)
    D = zeros(q)
    C[0][0] = 1
    D[1][2] = 1
    A, B = standard_AB(q, C, D)
    P, R, P2, R2 = local_pair(A, B)
    d = 2 * q
    require(mm(P, P) == P and add(P, P2) == eye(2 * d), "q=8 local pair is illegal")
    require(mm(P, P2) == zeros(2 * d), "q=8 halves do not annihilate")
    g = 2
    e0 = embed(P, 0, g, d)
    e1 = embed(P, 1, g, d)
    require(mm(e0, e1) != mm(e1, e0), "chosen q=8 projectors unexpectedly commute")
    calls = sharp_calls(1, q, A, B)
    for v in (2, 5, 11):
        pure, deriv = run_state(calls, [v])
        require(pure == target([v], 1, d) and deriv == target([v], 1, d),
                "q=8 g=1 sharp word missed the endpoint")
    bare = [("full", embed(P, 0, 1, d), embed(R, 0, 1, d), 0),
            ("full", embed(P2, 0, 1, d), embed(R2, 0, 1, d), 0)]
    pure, deriv = run_state(bare, [2])
    require(deriv != target([2], 1, d), "q=8 g=1 word without its thin map unexpectedly succeeded")


def ones_blocks(d):
    """T on one stage: I on all four d by d blocks."""
    T = zeros(2 * d)
    for i in range(d):
        for a in (0, d):
            for b in (0, d):
                T[a + i][b + i] = 1
    return T


def endpoint_equal(calls, v, g, d):
    pure, deriv = run_state(calls, v)
    T = target(v, g, d)
    return pure == T and deriv == T


def check_sharp_words():
    A = [[1, 0], [0, 0]]
    B = [[0, 1], [0, 0]]
    # This B is legal and the two stage projectors do not commute.
    P, R, P2, R2 = local_pair(A, B)
    require(add(mm(A, B), mm(B, A)) == B, "control B is illegal")
    e0, e1 = embed(P, 0, 3, 2), embed(P, 1, 3, 2)
    require(mm(e0, e1) != mm(e1, e0), "control projectors commute; the example is not the noncommuting case")
    for g in (1, 2, 4, 5):
        calls = sharp_calls(g, 1, A, B)
        for v in product((2, 4, 8), repeat=g):
            require(endpoint_equal(calls, v, g, 2), "sharp consecutive word failed at g=%d" % g)
        # One fewer map: delete the last thin map.
        short = [c for c in calls]
        if g % 2 == 1:
            require(short[-1][0] == "thin", "odd-g sharp word should end on its singleton thin map")
        idx = max(i for i, c in enumerate(short) if c[0] == "thin")
        del short[idx]
        missed = False
        for v in product((2, 4, 8), repeat=g):
            if not endpoint_equal(short, v, g, 2):
                missed = True
                break
        require(missed, "deleting one sharp-word map still met the endpoint at g=%d" % g)
    # q=8, g=2, nonzero B, full 3-by-3 grid.
    q = 8
    C, D = zeros(q), zeros(q)
    C[0][1] = 1
    D[3][0] = 1
    A8, B8 = standard_AB(q, C, D)
    calls = sharp_calls(2, q, A8, B8)
    d = 16
    P, _, _, _ = local_pair(A8, B8)
    require(mm(embed(P, 0, 2, d), embed(P, 1, 2, d)) != mm(embed(P, 1, 2, d), embed(P, 0, 2, d)),
            "q=8 g=2 projectors commute")
    for v in product((2, 4, 8), repeat=2):
        require(endpoint_equal(calls, v, 2, d), "q=8 g=2 sharp word failed")
    short = [c for c in calls if c[0] != "thin"]
    require(not endpoint_equal(short, (2, 4), 2, d), "q=8 g=2 word with no thin map unexpectedly succeeded")


def check_exponents_and_g13():
    for g in (1, 2, 3, 7, 13):
        orders = [tuple(range(g))]
        if g <= 7:
            # Every order at small g, plus the identity already included.
            from itertools import permutations
            orders = list(permutations(range(g)))
        else:
            rng = random.Random(13)
            for _ in range(40):
                row = list(range(g))
                rng.shuffle(row)
                orders.append(tuple(row))
        for order in orders:
            for gap in range(g + 1):
                require(covered_by_exponents(order, gap) == covered_leaves(order, gap),
                        "exponent match set disagrees with the adjacent-stage rule")
                require(len(covered_leaves(order, gap)) <= 2, "a gap covers more than two leaves")
    # Standard order, five maps: no placement covers 13 leaves.
    sets = [set(covered_leaves(list(range(13)), gap)) for gap in range(14)]
    require(all(len(s) <= 2 for s in sets), "standard-order gap exceeds two leaves")
    covered_all = False
    worst = 0
    for choice in product(range(14), repeat=5):
        union = set()
        for gap in choice:
            union |= sets[gap]
        if len(union) > worst:
            worst = len(union)
        if len(union) >= 13:
            covered_all = True
            break
    require(not covered_all and worst <= 10, "five standard-order gaps covered %d leaves" % worst)

    A = [[1, 0], [0, 0]]
    B = [[0, 1], [0, 0]]
    d = 2
    g = 13
    full = sharp_calls(g, 1, A, B)
    # Five maps: keep the first five odd-stage gaps (stages 0,2,4,6,8).
    short = sharp_calls(g, 1, A, B, keep={0, 2, 4, 6, 8})
    points = (
        (2, 4, 8, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14),
        (3, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 2, 4),
    )
    order = list(range(g))
    for v in points:
        require(endpoint_equal(full, v, g, d), "g=13 sharp seven-map word missed a test point")
        require(not endpoint_equal(short, v, g, d), "g=13 five-map consecutive word met a test point")
        pure, deriv = run_state(short, v)
        require(pure == target(v, g, d), "thin maps changed the pure product")
        S = mm(deriv, invert(pure))
        S_direct = run_normalized(short, v)
        require(S == S_direct, "normalized tracker disagrees with deriv * pure^{-1}")
        # Maps sit after stages 1,3,5,7,9 (1-based), i.e. gaps 1,3,5,7,9 in the 0-based count
        # of completed stages. Stage s (0-based) completes at gap s+1.
        maps = [(s + 1, [s] if s + 1 >= g else [s, s + 1]) for s in (0, 2, 4, 6, 8)]
        for leaf in range(g):
            coeff = prod(v[i] for i in needed_indices(order, leaf))
            for gap, leaves in maps:
                if leaf in leaves:
                    coeff ^= prod(v[i] for i in factor_indices(order, gap, leaf))
            got = block(S, 0, d * (leaf + 1), d)
            require(got == scalar_block(coeff, d), "core->leaf residual mismatch at leaf %d" % (leaf + 1))
            inv_coeff = prod(INV[v[i]] for i in needed_indices(order, leaf))
            for gap, leaves in maps:
                if leaf in leaves:
                    inv_coeff ^= prod(INV[v[i]] for i in factor_indices(order, gap, leaf))
            back = block(S, d * (leaf + 1), 0, d)
            require(back == scalar_block(inv_coeff, d), "leaf->core residual mismatch at leaf %d" % (leaf + 1))
        uncovered = [leaf for leaf in range(g) if all(leaf not in leaves for _, leaves in maps)]
        require(uncovered == [10, 11, 12], "unexpected uncovered leaves %s" % uncovered)
        for leaf in uncovered:
            require(block(S, 0, d * (leaf + 1), d) != zeros(d),
                    "uncovered leaf %d cancelled" % (leaf + 1))


def main():
    check_emission()
    check_sharp_words()
    check_exponents_and_g13()
    print("PASS_PAIRED_STAR_G13_Q8_CONSECUTIVE")


if __name__ == "__main__":
    main()
