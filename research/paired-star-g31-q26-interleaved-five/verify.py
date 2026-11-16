#!/usr/bin/env python3
"""Check one interleaved g=31, q=26 paired-star word.

The argument is PROOF.md. These checks fail closed. They are not a search
over call orders and they are not a census of projector frames.
"""

from __future__ import annotations

G = 31
Q = 26
MAPS = 5


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


def zeros(n):
    return [[0] * n for _ in range(n)]


def eye(n):
    m = zeros(n)
    for i in range(n):
        m[i][i] = 1
    return m


def add(a, b):
    return [[a[i][j] ^ b[i][j] for j in range(len(a))] for i in range(len(a))]


def scale(a, s):
    row = MUL[s]
    return [[row[a[i][j]] for j in range(len(a))] for i in range(len(a))]


def mm(a, b):
    n = len(a)
    c = [[0] * n for _ in range(n)]
    for i in range(n):
        ai = a[i]
        ci = c[i]
        for k in range(n):
            aik = ai[k]
            if not aik:
                continue
            mk = MUL[aik]
            bk = b[k]
            for j in range(n):
                bjk = bk[j]
                if bjk:
                    ci[j] ^= mk[bjk]
    return c


def prod(values):
    p = 1
    for v in values:
        p = MUL[p][v]
    return p


def standard_frame(q, c_entry=1):
    """A = diag(I_q, 0), B with a single top-from-bottom 1 at (0, 0)."""
    d = 2 * q
    a = zeros(d)
    b = zeros(d)
    for i in range(q):
        a[i][i] = 1
    if c_entry:
        b[0][q] = c_entry
    return a, b


def local_projector(a_mat, b_mat):
    d = len(a_mat)
    q_block = add(a_mat, b_mat)
    p = zeros(2 * d)
    for i in range(d):
        for j in range(d):
            p[i][j] = q_block[i][j]
            p[i][d + j] = b_mat[i][j]
            p[d + i][j] = b_mat[i][j]
            p[d + i][d + j] = q_block[i][j]
    return p


def embed(local, leaf, leaves, d):
    n = d * (leaves + 1)
    m = zeros(n)
    idx = list(range(d)) + [d * (leaf + 1) + i for i in range(d)]
    for a, ia in enumerate(idx):
        for b, ib in enumerate(idx):
            m[ia][ib] = local[a][b]
    return m


def plane_projectors():
    """The invariant 6-plane for C = 1, D = 0.

    Basis order: core top, core bottom, leaf0 top, leaf0 bottom,
    leaf1 top, leaf1 bottom.
    """
    p = zeros(6)
    pp = zeros(6)
    # First half. Column cb = e_ct + e_lt.
    p[0][0] = 1
    p[0][1] = 1
    p[0][3] = 1
    p[2][1] = 1
    p[2][2] = 1
    p[2][3] = 1
    # Complement.
    pp[0][1] = 1
    pp[0][3] = 1
    pp[1][1] = 1
    pp[2][1] = 1
    pp[2][3] = 1
    pp[3][3] = 1
    q = zeros(6)
    qp = zeros(6)
    q[0][0] = 1
    q[0][1] = 1
    q[0][5] = 1
    q[4][1] = 1
    q[4][4] = 1
    q[4][5] = 1
    qp[0][1] = 1
    qp[0][5] = 1
    qp[1][1] = 1
    qp[4][1] = 1
    qp[4][5] = 1
    qp[5][5] = 1
    return p, pp, q, qp


def factor(projector, scalar_x):
    return add(eye(len(projector)), scale(projector, scalar_x))


def support(indices, n):
    m = zeros(n)
    for i in indices:
        m[i][i] = 1
    return m


def walk_basis(v0, v1):
    """Apply the crossed factors to the core-bottom basis vector."""
    p, pp, q, qp = plane_projectors()
    x = v0 ^ 1
    z = v1 ^ 1
    n = 6
    vec = [0] * n
    vec[1] = 1

    def apply(mat, src):
        out = [0] * n
        for j in range(n):
            if not src[j]:
                continue
            col = MUL[src[j]]
            for i in range(n):
                if mat[i][j]:
                    out[i] ^= col[mat[i][j]]
        return out

    def step(mat, scalar, src):
        return add_vec(src, scale_vec(apply(mat, src), scalar))

    vec = step(p, x, vec)
    vec = step(q, z, vec)
    vec = step(pp, x, vec)
    vec = step(qp, z, vec)
    return vec, x, z


def add_vec(u, v):
    return [u[i] ^ v[i] for i in range(len(u))]


def scale_vec(u, s):
    row = MUL[s]
    return [row[x] for x in u]


def rank_f2(rows):
    m = [row[:] for row in rows]
    n = len(m)
    used = [False] * n
    rank = 0
    width = len(m[0])
    for col in range(width):
        piv = None
        for i in range(n):
            if not used[i] and m[i][col]:
                piv = i
                break
        if piv is None:
            continue
        used[piv] = True
        rank += 1
        for i in range(n):
            if i != piv and m[i][col]:
                m[i] = [a ^ b for a, b in zip(m[i], m[piv])]
    return rank


def slice_matrix(kind):
    """One port coordinate, regions core + 31 leaves."""
    n = G + 1
    m = [[0] * n for _ in range(n)]
    if kind == "J":
        for leaf in range(1, n):
            m[0][leaf] = 1
            m[leaf][0] = 1
    elif kind == "K":
        m[0][1] = 1
        m[1][0] = 1
    elif kind == "JK":
        for leaf in range(2, n):
            m[0][leaf] = 1
            m[leaf][0] = 1
    else:
        raise SystemExit("unknown slice")
    return m


def monomial(x_exp, z_exp):
    return 1 << (x_exp + 5 * z_exp)


def polynomial_difference():
    """Exact 6-by-6 product over GF(2)[x, z]. Entries are exponent masks."""
    p6, pp6, q6, qp6 = plane_projectors()
    n = 6

    def blank():
        return [[0] * n for _ in range(n)]

    def poly_eye():
        m = blank()
        for i in range(n):
            m[i][i] = monomial(0, 0)
        return m

    def convolve(left, right):
        acc = 0
        a = left
        while a:
            bit_a = (a & -a).bit_length() - 1
            a ^= 1 << bit_a
            b = right
            while b:
                bit_b = (b & -b).bit_length() - 1
                b ^= 1 << bit_b
                x_exp = (bit_a % 5) + (bit_b % 5)
                z_exp = (bit_a // 5) + (bit_b // 5)
                if x_exp >= 5 or z_exp >= 5:
                    raise SystemExit("polynomial degree left the packed exponent range")
                acc ^= monomial(x_exp, z_exp)
        return acc

    def poly_mul(left, right):
        out = blank()
        for i in range(n):
            for k in range(n):
                if not left[i][k]:
                    continue
                for j in range(n):
                    if right[k][j]:
                        out[i][j] ^= convolve(left[i][k], right[k][j])
        return out

    def poly_add(left, right):
        return [[left[i][j] ^ right[i][j] for j in range(n)] for i in range(n)]

    def affine(projector, x_exp, z_exp):
        m = poly_eye()
        bit = monomial(x_exp, z_exp)
        for i in range(n):
            for j in range(n):
                if projector[i][j]:
                    m[i][j] ^= bit
        return m

    pure = poly_eye()
    for projector, x_exp, z_exp in ((p6, 1, 0), (q6, 0, 1), (pp6, 1, 0), (qp6, 0, 1)):
        pure = poly_mul(affine(projector, x_exp, z_exp), pure)
    target = poly_mul(affine(support([0, 1, 4, 5], 6), 0, 1), affine(support([0, 1, 2, 3], 6), 1, 0))
    return poly_add(pure, target)


def check_frame_and_plane():
    a_mat, b_mat = standard_frame(Q, 1)
    d = 2 * Q
    require(mm(a_mat, a_mat) == a_mat, "A is not idempotent")
    require(add(mm(a_mat, b_mat), mm(b_mat, a_mat)) == b_mat, "AB+BA is not B")
    ap = [row[:] for row in a_mat]
    for i in range(d):
        ap[i][i] ^= 1
    p = local_projector(a_mat, b_mat)
    pp = local_projector(ap, b_mat)
    require(mm(p, p) == p and mm(pp, pp) == pp, "a half is not a projector")
    require(add(p, pp) == eye(2 * d), "halves do not resolve the stage support")
    require(mm(p, pp) == zeros(2 * d), "halves do not annihilate")
    e0 = embed(p, 0, 2, d)
    e1 = embed(p, 1, 2, d)
    require(mm(e0, e1) != mm(e1, e0), "the chosen stage projectors commute")

    p6, pp6, q6, qp6 = plane_projectors()
    require(add(p6, pp6) == support([0, 1, 2, 3], 6), "plane halves do not resolve leaf 0")
    require(add(q6, qp6) == support([0, 1, 4, 5], 6), "plane halves do not resolve leaf 1")
    require(mm(p6, p6) == p6 and mm(pp6, pp6) == pp6, "plane half is not a projector")
    require(mm(p6, pp6) == zeros(6) and mm(q6, qp6) == zeros(6), "plane halves do not annihilate")
    require(mm(p6, q6) != mm(q6, p6), "plane projectors unexpectedly commute")
    diff = polynomial_difference()
    xz = monomial(1, 1)
    require(diff[4][1] == xz and diff[0][3] == xz, "crossed pure-product defect is not the monomial xz")
    for i in range(6):
        for j in range(6):
            if (i, j) not in ((4, 1), (0, 3)):
                require(diff[i][j] == 0, "crossed pure product has an unexpected polynomial entry")

    # Same projectors, adjacent halves: the pure product matches.
    for v0, v1 in ((2, 4), (3, 5)):
        x = v0 ^ 1
        z = v1 ^ 1
        pure = eye(6)
        for mat, scalar in ((p6, x), (pp6, x), (q6, z), (qp6, z)):
            pure = mm(factor(mat, scalar), pure)
        target = eye(6)
        target = mm(factor(support([0, 1, 2, 3], 6), x), target)
        target = mm(factor(support([0, 1, 4, 5], 6), z), target)
        require(pure == target, "adjacent halves of this frame missed the pure target")

    # Crossed order: leaf1-top from core-bottom is xz, not 0.
    for v0, v1 in ((2, 4), (3, 5)):
        vec, x, z = walk_basis(v0, v1)
        require(vec[4] == MUL[x][z] and vec[4] != 0, "crossed core-bottom vector missed the xz leaf entry")
        expect_cb = MUL[v0][v1]  # (1+x)(1+z) = v0*v1
        require(vec[1] == expect_cb, "crossed core-bottom diagonal is not the target scalar")
        for i in (0, 2, 3, 5):
            require(vec[i] == 0, "crossed core-bottom vector has an unexpected component")


def pure_on_profile(v0, v1, c_entry):
    """Pure product of the all-first then all-second order, other x_j = 0."""
    a_mat, b_mat = standard_frame(Q, c_entry)
    d = 2 * Q
    ap = [row[:] for row in a_mat]
    for i in range(d):
        ap[i][i] ^= 1
    p = local_projector(a_mat, b_mat)
    pp = local_projector(ap, b_mat)
    # Three regions: core, leaf 0, leaf 1. Other stages have x = 0.
    e_p = embed(p, 0, 2, d)
    e_pp = embed(pp, 0, 2, d)
    f_p = embed(p, 1, 2, d)
    f_pp = embed(pp, 1, 2, d)
    x = v0 ^ 1
    z = v1 ^ 1
    pure = eye(3 * d)
    # Rightmost factor is applied first: P0, P1, P0', P1'.
    for mat, scalar in ((e_p, x), (f_p, z), (e_pp, x), (f_pp, z)):
        pure = mm(factor(mat, scalar), pure)
    return pure


def target_pure_two(v0, v1):
    d = 2 * Q
    n = 3 * d
    t = eye(n)
    # core scaled by v0*v1, leaf 0 by v0, leaf 1 by v1. Off-blocks stay 0.
    core = prod((v0, v1))
    for i in range(d):
        t[i][i] = core
        t[d + i][d + i] = v0
        t[2 * d + i][2 * d + i] = v1
    return t


def check_profile_pure():
    d = 2 * Q
    for v0, v1 in ((2, 4), (3, 5)):
        got = pure_on_profile(v0, v1, 1)
        exp = target_pure_two(v0, v1)
        require(got != exp, "interleaved pure product unexpectedly matched")
        x = v0 ^ 1
        z = v1 ^ 1
        # leaf1 top (local 0) from core bottom (local q).
        require(got[2 * d][Q] == MUL[x][z] and MUL[x][z] != 0,
                "q=26 leaf1-top entry is not xz")
        # core top from leaf0 bottom.
        require(got[0][d + Q] == MUL[x][z], "q=26 core-top entry is not xz")
        require(exp[2 * d][Q] == 0 and exp[0][d + Q] == 0, "target off-block is not zero")
        p6, pp6, q6, qp6 = plane_projectors()
        small = eye(6)
        for mat, scalar in ((p6, x), (q6, z), (pp6, x), (qp6, z)):
            small = mm(factor(mat, scalar), small)
        plane = (0, Q, d, d + Q, 2 * d, 2 * d + Q)
        for a, ia in enumerate(plane):
            for b, ib in enumerate(plane):
                require(got[ia][ib] == small[a][b],
                        "q=26 pure product does not restrict to the 6-plane")
        commuting = pure_on_profile(v0, v1, 0)
        require(commuting == exp, "B=0 cross of this order should match; the frame control failed")


def check_forced_maps():
    n = G + 1
    j = slice_matrix("J")
    k = slice_matrix("K")
    jk = slice_matrix("JK")
    require(rank_f2(j) == 2 and rank_f2(k) == 2 and rank_f2(jk) == 2, "a coordinate slice is not rank 2")
    summed = [[j[r][c] ^ k[r][c] ^ jk[r][c] for c in range(n)] for r in range(n)]
    require(summed == zeros(n), "J+K does not cancel to J on a coordinate")
    # Direct sum over a block of 13 coordinates: images use distinct port coordinates.
    groups = [list(range(13 * t, 13 * t + 13)) for t in range(4)]
    require(sorted(c for group in groups for c in group) == list(range(2 * Q)),
            "the four coordinate blocks do not partition the port space")
    for group in groups:
        require(len(group) == 13 and len(set(group)) == 13, "a rank block is not 13 coordinates")
    # Map 0 uses JK on group 0, map 4 uses K on group 0, maps 1..3 use J.
    # Each is a direct sum of 13 rank-2 slices, hence rank 26.
    require(13 * 2 == Q, "thirteen rank-2 slices are not rank q")
    # Sum of the five maps is J on every coordinate: JK+K = J on group 0, and J elsewhere.
    for c in range(2 * Q):
        kind = "J"
        if c < 13:
            # contributed by map 0 (JK) and map 4 (K)
            kind = "JK+K"
        require(kind == "J" or kind == "JK+K", "coordinate not covered")
    require(add(jk, k) == j, "the central pair of maps does not sum to J")
    for coord in range(2 * Q):
        group = coord // 13
        for which in range(MAPS):
            for leaf in range(G):
                region = leaf + 1
                expect = 0
                if which == 0 and group == 0:
                    expect = jk[0][region]
                elif which == 4 and group == 0:
                    expect = k[0][region]
                elif which == group:
                    expect = j[0][region]
                require(map_diag(which, coord, region) == expect,
                        "thin-map diagonal does not match its rank slice")


def diagonal(entries):
    m = zeros(len(entries))
    for i, value in enumerate(entries):
        m[i][i] = value
    return m


def block_zero(g, d):
    return [[None for _ in range(g + 1)] for _ in range(g + 1)]


def block_add(blocks, r, c, mat):
    current = blocks[r][c]
    blocks[r][c] = mat if current is None else add(current, mat)


def plocal_blocks(a_mat, b_mat):
    q_block = add(a_mat, b_mat)
    return [[q_block, b_mat], [b_mat, q_block]]


def conj_blocks(blocks, leaf, p_blocks, x, y, g):
    """Replace S by (I+xP) S (I+yP). `leaf` is the stage index, not the region."""
    if x == 0 and y == 0:
        return blocks
    active = [0, leaf + 1]
    size = g + 1
    right = [row[:] for row in blocks]
    if y:
        for r in range(size):
            for li, col in enumerate(active):
                acc = None
                for lj, src in enumerate(active):
                    block = blocks[r][src]
                    if block is None:
                        continue
                    prod = mm(block, p_blocks[lj][li])
                    acc = prod if acc is None else add(acc, prod)
                if acc is None:
                    continue
                acc = scale(acc, y)
                right[r][col] = acc if right[r][col] is None else add(right[r][col], acc)
    out = [row[:] for row in right]
    if x:
        for li, row in enumerate(active):
            for c in range(size):
                acc = None
                for lj, src in enumerate(active):
                    block = right[src][c]
                    if block is None:
                        continue
                    prod = mm(p_blocks[li][lj], block)
                    acc = prod if acc is None else add(acc, prod)
                if acc is None:
                    continue
                acc = scale(acc, x)
                out[row][c] = acc if out[row][c] is None else add(out[row][c], acc)
    return out


def add_half(blocks, leaf, a_mat):
    block_add(blocks, 0, 0, a_mat)
    block_add(blocks, 0, leaf + 1, a_mat)
    block_add(blocks, leaf + 1, 0, a_mat)
    block_add(blocks, leaf + 1, leaf + 1, a_mat)


def map_diag(which, coord, leaf_region):
    """1 if this map puts a 1 on that core/leaf diagonal entry."""
    group = coord // 13
    if which == 0 and group == 0:
        return 1 if leaf_region != 1 else 0  # JK: every leaf except leaf 0
    if which == 4 and group == 0:
        return 1 if leaf_region == 1 else 0  # K: only leaf 0
    if which == group and which in (1, 2, 3):
        return 1
    return 0


def add_thin(blocks, which, d):
    for leaf in range(G):
        region = leaf + 1
        entries_out = [map_diag(which, c, region) for c in range(d)]
        entries_back = entries_out[:]
        if any(entries_out):
            block_add(blocks, 0, region, diagonal(entries_out))
            block_add(blocks, region, 0, diagonal(entries_back))


def is_identity_blocks(blocks, g, d):
    for r in range(g + 1):
        for c in range(g + 1):
            got = blocks[r][c]
            if r == c:
                if got != eye(d):
                    return False
            elif got is not None and got != zeros(d):
                return False
    return True


def run_normalized(values, a_mat, b_mat, ap, include_maps):
    d = len(a_mat)
    g = len(values)
    p_blocks = plocal_blocks(a_mat, b_mat)
    pp_blocks = plocal_blocks(ap, b_mat)
    blocks = block_zero(g, d)
    # First halves, then the five maps, then second halves.
    for leaf, v in enumerate(values):
        x = v ^ 1
        y = 0 if x == 0 else MUL[x][INV[v]]
        blocks = conj_blocks(blocks, leaf, p_blocks, x, y, g)
        add_half(blocks, leaf, a_mat)
    if include_maps:
        for which in range(MAPS):
            add_thin(blocks, which, d)
    for leaf, v in enumerate(values):
        x = v ^ 1
        y = 0 if x == 0 else MUL[x][INV[v]]
        blocks = conj_blocks(blocks, leaf, pp_blocks, x, y, g)
        add_half(blocks, leaf, ap)
    return blocks


def dense_normalized(calls, values):
    """Reference state machine for the q=1 engine check. calls are (P, R, stage) or ('thin', Z)."""
    n = len(calls[0][1]) if calls[0][0] != "thin" else len(calls[0][1])
    n = len(calls[0][1])
    pure = eye(n)
    deriv = zeros(n)
    for call in calls:
        if call[0] == "thin":
            deriv = add(deriv, mm(call[1], pure))
            continue
        _, p, r, stage = call
        v = values[stage]
        x = v ^ 1
        pp = mm(p, pure)
        pd = mm(p, deriv)
        rp = mm(r, pure)
        pure = [[pure[i][j] ^ MUL[x][pp[i][j]] for j in range(n)] for i in range(n)]
        deriv = [[deriv[i][j] ^ MUL[x][pd[i][j]] ^ MUL[v][rp[i][j]] for j in range(n)] for i in range(n)]
    return pure, deriv


def invert(a):
    n = len(a)
    m = [a[i][:] + [1 if i == j else 0 for j in range(n)] for i in range(n)]
    for col in range(n):
        piv = next((i for i in range(col, n) if m[i][col]), None)
        require(piv is not None, "singular pure factor in the engine check")
        m[col], m[piv] = m[piv], m[col]
        invp = INV[m[col][col]]
        m[col] = [MUL[invp][x] for x in m[col]]
        for i in range(n):
            if i != col and m[i][col]:
                f = m[i][col]
                m[i] = [m[i][j] ^ MUL[f][m[col][j]] for j in range(2 * n)]
    return [row[n:] for row in m]


def blocks_to_dense(blocks, d):
    g = len(blocks) - 1
    n = d * (g + 1)
    m = zeros(n)
    for r in range(g + 1):
        for c in range(g + 1):
            block = blocks[r][c]
            if block is None:
                continue
            for i in range(d):
                for j in range(d):
                    m[r * d + i][c * d + j] = block[i][j]
    return m


def check_engine_and_points():
    # q=1, g=2, nonzero B, one thin map equal to the D=1 correction.
    q = 1
    d = 2
    a_mat, b_mat = standard_frame(q, 1)
    ap = [row[:] for row in a_mat]
    for i in range(d):
        ap[i][i] ^= 1
    p = local_projector(a_mat, b_mat)
    pp = local_projector(ap, b_mat)
    def query(half_a):
        out = zeros(2 * d)
        for i in range(d):
            for j in range(d):
                out[i][j] = half_a[i][j]
                out[i][d + j] = half_a[i][j]
                out[d + i][j] = half_a[i][j]
                out[d + i][d + j] = half_a[i][j]
        return out
    r0 = query(a_mat)
    r0p = query(ap)
    g = 2
    calls = []
    for leaf, half_p, half_r in ((0, p, r0), (1, p, r0)):
        calls.append(("full", embed(half_p, leaf, g, d), embed(half_r, leaf, g, d), leaf))
    # A thin map that is the whole M for g=2: I on both core-leaf directions.
    z = zeros(d * (g + 1))
    for leaf in range(g):
        for i in range(d):
            z[i][d * (leaf + 1) + i] = 1
            z[d * (leaf + 1) + i][i] = 1
    calls.append(("thin", z))
    for leaf, half_p, half_r in ((0, pp, r0p), (1, pp, r0p)):
        calls.append(("full", embed(half_p, leaf, g, d), embed(half_r, leaf, g, d), leaf))
    values = (2, 4)
    pure, deriv = dense_normalized(calls, values)
    s_dense = mm(deriv, invert(pure))
    # Block engine for this small word: reuse the g=31 map code only for g=31.
    # Here compare by a direct block run specialized to g=2 with one full M map.
    blocks = block_zero(g, d)
    p_blocks = plocal_blocks(a_mat, b_mat)
    pp_blocks = plocal_blocks(ap, b_mat)
    for leaf, v, halves, query_a in (
        (0, values[0], p_blocks, a_mat),
        (1, values[1], p_blocks, a_mat),
    ):
        x = v ^ 1
        y = MUL[x][INV[v]]
        blocks = conj_blocks(blocks, leaf, halves, x, y, g)
        add_half(blocks, leaf, query_a)
    for leaf in range(g):
        block_add(blocks, 0, leaf + 1, eye(d))
        block_add(blocks, leaf + 1, 0, eye(d))
    for leaf, v, halves, query_a in (
        (0, values[0], pp_blocks, ap),
        (1, values[1], pp_blocks, ap),
    ):
        x = v ^ 1
        y = MUL[x][INV[v]]
        blocks = conj_blocks(blocks, leaf, halves, x, y, g)
        add_half(blocks, leaf, query_a)
    require(blocks_to_dense(blocks, d) == s_dense, "block conjugation disagrees with deriv * pure^{-1}")

    # g=31 forced maps at D_j = 1 meet the endpoint. Other points do not.
    a_big, b_big = standard_frame(Q, 1)
    ap_big = [row[:] for row in a_big]
    for i in range(2 * Q):
        ap_big[i][i] ^= 1
    ones = tuple(1 for _ in range(G))
    s_one = run_normalized(ones, a_big, b_big, ap_big, True)
    require(is_identity_blocks(s_one, G, 2 * Q), "D_j=1 did not force the five maps onto the endpoint")
    short = run_normalized(ones, a_big, b_big, ap_big, False)
    require(not is_identity_blocks(short, G, 2 * Q), "omitting the thin maps still met D_j=1")
    for v0, v1 in ((2, 4), (3, 5)):
        values = tuple([v0, v1] + [1] * (G - 2))
        s = run_normalized(values, a_big, b_big, ap_big, True)
        require(not is_identity_blocks(s, G, 2 * Q),
                "normalized coefficient met I at a point where the pure product fails")


def main():
    check_frame_and_plane()
    check_profile_pure()
    check_forced_maps()
    check_engine_and_points()
    print("PASS_PAIRED_STAR_G31_Q26_INTERLEAVED")


if __name__ == "__main__":
    main()
