"""Reusable exact word/tuple search over group rings F2[G] and matrix rings
M_r(F2[G]) for the formal rank-one-idempotent register model.

Model (the coordinate-CNOT line of PR1333/1414/1491/1541/1722 and the S_n
line of PR1989): G finite, R = F2[G]; a paid call is D_N(g) = I + ([g]+1) N
with g a paid label and N = u v^T a binary rank-one idempotent (v^T u = 1)
in M_r(F2); free scalar GL_r(F2) mixing at zero cost; acceptance is equality
of all formal group-algebra coefficients in M_r(F2[G]).

Contents:
  * Group / GroupAlgebra: F2[G] from a multiplication table (gl2f2, q8).
  * M_r(F2) and M_r(F2[G]) exact arithmetic; rank-one idempotent alphabets.
  * Quotient projections: sign quotient (F2[epsilon]/(epsilon^2)) and the
    natural 2-dimensional quotient for GL_2(F2); the pair is an algebra
    isomorphism, so sign + natural equations are equivalent to the full
    endpoint (checked, not assumed).
  * The C-matrix invariant C_ij = v_i^T u_j: C^2 = C plus four projected
    block equations is equivalent to the full endpoint at full rank.
  * Search engine: layer-ball digests, meet-in-the-middle joins, prefix
    closure bounds, GL_r conjugation reduction, SHA256-receipted parallel-safe
    batch splitting, and a signature-DP enumeration for frame-plus-extra
    tuples (the six-distinct-value KB2 family).

Python stdlib only.  Exact F2 arithmetic throughout.  Apache-2.0.
Aaron Wang, with help from opencode.
"""

import hashlib

# --------------------------------------------------------------------------
# Groups from multiplication tables.
# --------------------------------------------------------------------------


class Group:
    def __init__(self, name, table, identity, names):
        self.name = name
        self.n = len(table)
        self.table = tuple(tuple(row) for row in table)
        self.identity = identity
        self.names = tuple(names)

    def mul(self, i, j):
        return self.table[i][j]

    def parity(self, g):
        """Image of g under G -> G/[G,G] = C_2 (0 = even)."""
        return self._parity[g]

    def _set_parity(self, parities):
        self._parity = tuple(parities)


def gl2f2():
    """G = GL_2(F2) as packed 2x2 matrices (bits r0c0 r0c1 r1c0 r1c1)."""
    def mmul(x, y):
        a = [(x >> 3) & 1, (x >> 2) & 1, (x >> 1) & 1, x & 1]
        b = [(y >> 3) & 1, (y >> 2) & 1, (y >> 1) & 1, y & 1]
        c00 = (a[0] & b[0]) ^ (a[1] & b[2])
        c01 = (a[0] & b[1]) ^ (a[1] & b[3])
        c10 = (a[2] & b[0]) ^ (a[3] & b[2])
        c11 = (a[2] & b[1]) ^ (a[3] & b[3])
        return (c00 << 3) | (c01 << 2) | (c10 << 1) | c11

    mats = [m for m in range(16)
            if (((m >> 3) & 1) * (m & 1)) ^ (((m >> 2) & 1) * ((m >> 1) & 1))]
    mats.sort()
    idx = {m: i for i, m in enumerate(mats)}
    mul = [[idx[mmul(mats[i], mats[j])] for j in range(6)] for i in range(6)]
    names = []
    for m in mats:
        names.append({0b1001: "e", 0b1101: "a", 0b1011: "b",
                      0b0110: "s"}.get(m, "g%d" % m))
    g = Group("GL_2(F2)", mul, idx[0b1001], names)
    g.A = idx[0b1101]
    g.B = idx[0b1011]
    g.S = idx[0b0110]
    # parity = permutation parity of the action on the three nonzero vectors
    vecs = (0b01, 0b10, 0b11)

    def act(m, v):
        r0 = ((m >> 3) & 1) * ((v >> 1) & 1) ^ ((m >> 2) & 1) * (v & 1)
        r1 = ((m >> 1) & 1) * ((v >> 1) & 1) ^ (m & 1) * (v & 1)
        return (r0 << 1) | r1

    par = []
    for m in mats:
        perm = [vecs.index(act(m, v)) for v in vecs]
        inv = sum(1 for i in range(3) for j in range(i + 1, 3)
                  if perm[i] > perm[j])
        par.append(inv & 1)
    g._set_parity(par)
    return g


def q8():
    """Q8 = {+-1, +-i, +-j, +-k}; element (sign, axis): axis 0 = 1, 1 = i,
    2 = j, 3 = k; sign 0 = +, 1 = -."""
    axis_mul = [
        [0, 1, 2, 3],
        [1, 0, 3, 2],
        [2, 3, 0, 1],
        [3, 2, 1, 0],
    ]
    sign_flip = [
        [0, 0, 0, 0],
        [0, 1, 0, 1],
        [0, 1, 1, 0],
        [0, 0, 1, 1],
    ]

    def enc(s, ax):
        return (s << 2) | ax

    mul = [[0] * 8 for _ in range(8)]
    for el in range(8):
        for fr in range(8):
            s1, ax1 = el >> 2, el & 3
            s2, ax2 = fr >> 2, fr & 3
            mul[el][fr] = enc(s1 ^ s2 ^ sign_flip[ax1][ax2],
                              axis_mul[ax1][ax2])
    names = ["1", "i", "j", "k", "-1", "-i", "-j", "-k"]
    g = Group("Q8", mul, enc(0, 0), names)
    g.X = enc(0, 1)   # i
    g.Y = enc(0, 2)   # j
    g.Z = enc(1, 0)   # -1 = x^2 = y^2 = xyxy
    g._set_parity([0] * 8)   # Q8 is not used with a sign quotient here
    return g


class GroupAlgebra:
    """F2[G]: elements are bit masks over Group elements."""

    def __init__(self, group):
        self.group = group
        n = group.n
        size = 1 << n
        mul = [bytearray(size) for _ in range(size)]
        for x in range(size):
            xs = [i for i in range(n) if (x >> i) & 1]
            if not xs:
                continue
            row = mul[x]
            for y in range(size):
                out = 0
                for i in xs:
                    for j in range(n):
                        if (y >> j) & 1:
                            out ^= 1 << group.mul(i, j)
                row[y] = out
        self._mul = tuple(bytes(row) for row in mul)
        self.one = 1 << group.identity

    def add(self, x, y):
        return x ^ y

    def mul(self, x, y):
        if x == 0 or y == 0:
            return 0
        return self._mul[x][y]

    def basis(self, i):
        return 1 << i


# --------------------------------------------------------------------------
# M_r(F2) and rank-one idempotents.
# --------------------------------------------------------------------------


def mat_add(x, y):
    return tuple(a ^ b for a, b in zip(x, y))


def mat_mul(n, x, y):
    out = [0] * n
    for i in range(n):
        xi = x[i]
        acc = 0
        while xi:
            low = xi & -xi
            k = low.bit_length() - 1
            acc ^= y[k]
            xi ^= low
        out[i] = acc
    return tuple(out)


def proj_rows(t, u, v):
    return tuple(v if (u >> i) & 1 else 0 for i in range(t))


def dot(u, v):
    return bin(u & v).count("1") & 1


def rank_f2(n, x):
    rows = list(x)
    rank = 0
    for col in range(n):
        piv = None
        for r in range(rank, n):
            if (rows[r] >> col) & 1:
                piv = r
                break
        if piv is None:
            continue
        rows[rank], rows[piv] = rows[piv], rows[rank]
        for r in range(n):
            if r != rank and (rows[r] >> col) & 1:
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def rank_one_idempotents(t):
    out = []
    for u in range(1, 1 << t):
        for v in range(1, 1 << t):
            if dot(u, v):
                out.append((u, v))
    return out


def coord_proj(t, c):
    return (1 << c, 1 << c)


def proj_sum(t, rows_list):
    acc = [0] * t
    for rows in rows_list:
        for i in range(t):
            acc[i] ^= rows[i]
    return tuple(acc)


def eye_f2(t):
    return tuple(1 << i for i in range(t))


# --------------------------------------------------------------------------
# M_r(F2[G]) and word products.
# --------------------------------------------------------------------------


def ring_eye(ga, r):
    one = ga.one
    return tuple(one if i == j else 0
                 for i in range(r) for j in range(r))


def ring_add(x, y):
    return tuple(a ^ b for a, b in zip(x, y))


def ring_mul(ga, x, y, r):
    out = [0] * (r * r)
    for i in range(r):
        for k in range(r):
            aik = x[i * r + k]
            if aik:
                for j in range(r):
                    bkj = y[k * r + j]
                    if bkj:
                        out[i * r + j] ^= ga.mul(aik, bkj)
    return tuple(out)


def call_matrix(ga, group, r, g, n_rows):
    """D_N(g) = I + ([g]+1) N in M_r(F2[G]) with N = n_rows (M_r(F2))."""
    one = ga.one
    xb = ga.basis(g) ^ one
    out = []
    for i in range(r):
        for j in range(r):
            v = one if i == j else 0
            if (n_rows[i] >> j) & 1:
                v ^= xb
            out.append(v)
    return tuple(out)


def word_product(ga, group, r, labels, projs):
    """Product D_0 D_1 ... with labels[0] leftmost (any consistent direction
    defines the same problem on the palindromic alternating word)."""
    acc = ring_eye(ga, r)
    for g, (u, v) in zip(labels, projs):
        fac = call_matrix(ga, group, r, g, proj_rows(r, u, v))
        acc = ring_mul(ga, acc, fac, r)
    return acc


def ring_target(ga, r, s):
    sb = ga.basis(s)
    return tuple(sb if i == j else 0
                 for i in range(r) for j in range(r))


def endpoint_check(ga, group, r, labels, projs):
    return word_product(ga, group, r, labels, projs) == \
        ring_target(ga, r, group.S if hasattr(group, "S") else group.Z)


def expanded_word_product(ga, group, r, labels, projs):
    """Independent subset expansion: sum_S (prod_{i in S} ([g_i]+1)) N(S).
    Used to cross-check the iterative product engine."""
    n = len(labels)
    xs = [ga.basis(g) ^ ga.one for g in labels]
    xprod = [0] * (1 << n)
    xprod[0] = ga.one
    for mask in range(1, 1 << n):
        low = mask & -mask
        bit = low.bit_length() - 1
        # order: positions increase left to right
        xprod[mask] = ga.mul(xs[bit], xprod[mask ^ low])
    out = [0] * (r * r)
    for mask in range(1 << n):
        picks = [i for i in range(n) if (mask >> i) & 1]
        if not picks:
            one = ga.one
            for i in range(r):
                out[i * r + i] ^= one
            continue
        # N(S) = u_first (prod interior dots) v_last^T (F2 scalars are bits)
        u_first, _ = projs[picks[0]]
        _, v_last = projs[picks[-1]]
        alive = 1
        for p in range(len(picks) - 1):
            _, vp = projs[picks[p]]
            uq, _ = projs[picks[p + 1]]
            alive &= dot(vp, uq)
            if not alive:
                break
        if not alive:
            continue
        scalar = xprod[mask]
        for i in range(r):
            if (u_first >> i) & 1:
                for j in range(r):
                    if (v_last >> j) & 1:
                        out[i * r + j] ^= scalar
    return tuple(out)


# --------------------------------------------------------------------------
# Quotient projections.
# --------------------------------------------------------------------------


def sign_quotient_word(group, r, labels, projs):
    """Product in M_r(F2[epsilon]/(epsilon^2)) = (M0, M1)."""
    eye = eye_f2(r)
    acc = [0] * r
    for g, (u, v) in zip(labels, projs):
        if group.parity(g):
            rows = proj_rows(r, u, v)
            for i in range(r):
                acc[i] ^= rows[i]
    return eye, tuple(acc)


def sign_check(group, r, labels, projs):
    m0, m1 = sign_quotient_word(group, r, labels, projs)
    return m1 == eye_f2(r)


def natural_check(group, r, labels, projs):
    """Natural quotient [g] -> g in M_2(F2): product in M_{2r}(F2)."""
    if group.name != "GL_2(F2)":
        raise ValueError("natural_check needs the GL_2(F2) 2-dim rep")
    n = 2 * r
    acc = tuple(1 << i for i in range(n))
    for g, (u, v) in zip(labels, projs):
        m = gl2_matrix(group, g)
        n_rows = proj_rows(r, u, v)
        fac = [1 << i for i in range(n)]
        for i in range(r):
            for j in range(r):
                if (n_rows[i] >> j) & 1:
                    for p in range(2):
                        for q in range(2):
                            if (m[p] >> q) & 1:
                                fac[2 * i + p] ^= 1 << (2 * j + q)
        acc = mat_mul(n, acc, tuple(fac))
    tgt = [0] * n
    sm = gl2_matrix(group, group.S)
    for i in range(r):
        for p in range(2):
            for q in range(2):
                if (sm[p] >> q) & 1:
                    tgt[2 * i + p] ^= 1 << (2 * i + q)
    return acc == tuple(tgt)


def gl2_matrix(group, g):
    """2x2 matrix (rows as ints, bit j = column j) of a GL_2(F2) element."""
    mats = [m for m in range(16)
            if (((m >> 3) & 1) * (m & 1)) ^ (((m >> 2) & 1) * ((m >> 1) & 1))]
    mats.sort()
    m = mats[g]
    return (((m >> 2) & 1) << 1) | ((m >> 3) & 1), \
        ((m & 1) << 1) | ((m >> 1) & 1)


# --------------------------------------------------------------------------
# C-matrix invariant: C_ij = v_i^T u_j.
# --------------------------------------------------------------------------


def c_matrix(projs):
    n = len(projs)
    rows = []
    for i in range(n):
        _, vi = projs[i]
        row = 0
        for j in range(n):
            uj, _ = projs[j]
            if dot(vi, uj):
                row |= 1 << j
        rows.append(row)
    return tuple(rows)


def c_conditions_ok(r, labels, projs):
    """C^2 = C, rank C = r, and the projected block equations: for every
    ordered label pair (p, q), sum_{i<=j, labels p..q} Z_ij u_i v_j^T = I
    projected is (C D^{p,q} C) = C."""
    n = len(projs)
    c = c_matrix(projs)
    if rank_f2(n, c) != r:
        return False
    if mat_mul(n, c, c) != c:
        return False
    # M_ij = c_ij for j > i with j - i odd; Z = M + M^2 + ... + M^n
    m = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if ((j - i) & 1) and ((c[i] >> j) & 1):
                m[i] |= 1 << j
    z = [0] * n
    power = tuple(m)
    for _ in range(n):
        z = [a ^ b for a, b in zip(z, power)]
        power = mat_mul(n, power, m)
    distinct = sorted(set(labels))
    for p in distinct:
        for q in distinct:
            d = [0] * n
            for i in range(n):
                if labels[i] != p:
                    continue
                for j in range(i, n):
                    if labels[j] != q:
                        continue
                    if (z[i] >> j) & 1:
                        d[i] |= 1 << j
            if mat_mul(n, c, mat_mul(n, tuple(d), c)) != c:
                return False
    return True


# --------------------------------------------------------------------------
# Symmetry: GL_r conjugation.
# --------------------------------------------------------------------------


def random_gl(t, rng):
    while True:
        rows = [rng.randrange(1 << t) for _ in range(t)]
        if rank_f2(t, tuple(rows)) != t:
            continue
        inv = [1 << i for i in range(t)]
        work = list(rows)
        for col in range(t):
            piv = next(r for r in range(col, t) if (work[r] >> col) & 1)
            work[col], work[piv] = work[piv], work[col]
            inv[col], inv[piv] = inv[piv], inv[col]
            for r in range(t):
                if r != col and (work[r] >> col) & 1:
                    work[r] ^= work[col]
                    inv[r] ^= inv[col]
        return tuple(rows), tuple(inv)


def proj_conj(t, u, v, p, pinv):
    u2 = 0
    for i in range(t):
        if dot(p[i], u):
            u2 |= 1 << i
    v2 = 0
    for j in range(t):
        if (v >> j) & 1:
            v2 ^= pinv[j]
    return (u2, v2)


def random_tuple(group, t, length, rng):
    alphabet = rank_one_idempotents(t)
    labels = [group.A if rng.randrange(2) == 0 else group.B
              for _ in range(length)]
    projs = [alphabet[rng.randrange(len(alphabet))]
             for _ in range(length)]
    return labels, projs


# --------------------------------------------------------------------------
# Search engine: layer balls, MITM, prefix bounds, shards.
# --------------------------------------------------------------------------


def layer_ball_sizes(ga, gens, depth):
    """BFS distance-layer sizes in the monoid generated by `gens`: the number
    of new products reachable at each exact length (memoized ball digest)."""
    r = int(round(len(gens[0]) ** 0.5))
    eye = ring_eye(ga, r)
    seen = {eye}
    frontier = {eye}
    out = [1]
    for _ in range(depth):
        nxt = set()
        for st in frontier:
            for gen in gens:
                nxt.add(ring_mul(ga, gen, st, r))
        new = nxt - seen
        seen |= nxt
        frontier = new
        out.append(len(new))
    return out


def shard_split(items, n):
    """Deterministic contiguous shards with SHA256 receipts; each shard is an
    independent batch (safe for parallel workers)."""
    items = list(items)
    k, extra = divmod(len(items), n)
    shards = []
    start = 0
    for i in range(n):
        stop = start + k + (1 if i < extra else 0)
        part = items[start:stop]
        shards.append({
            "index": i,
            "items": part,
            "sha256": hashlib.sha256(
                ",".join(map(str, part)).encode()).hexdigest(),
        })
        start = stop
    return shards


def sign_prefix_bound(t, partial_rows, placed, total):
    """Prefix closure bound: the remaining total - placed rank-one idempotents
    must be able to sum to I - partial; hence rank(I - partial) <= left."""
    left = total - placed
    if left < 0:
        return False
    res = list(eye_f2(t))
    for row in partial_rows:
        for i in range(t):
            res[i] ^= row[i]
    return rank_f2(t, tuple(res)) <= left


# --------------------------------------------------------------------------
# Frame-plus-extra (six-distinct-value) enumeration: signature DP.
# --------------------------------------------------------------------------


def alt_labels(group, n):
    return [group.A if i % 2 == 0 else group.B for i in range(n)]


def sig_eval(ga, group, t, wlabels, h, u, v):
    """Word product for a frame-plus-extra tuple: h[c][s] is the class-c
    segment-s label product (single group element), extra projector uv^T at
    the m = len(wlabels) extra positions.  Returns the M_t(F2[G]) product.

    F2[G] is noncommutative, so each extra scalar x = [g]+1 stays at its own
    position in the chain: Term(T)_{ab} = f_lead[a] x_j1 u_a S v_b
    f_trail[b] with S = sigma_1 x_j2 sigma_2 ... x_jk."""
    m = len(wlabels)
    xs = [ga.basis(g) ^ ga.one for g in wlabels]
    out = [0] * (t * t)
    for mask in range(1 << m):
        picks = [j for j in range(m) if (mask >> j) & 1]
        bounds = []
        prev = 0
        for j in picks:
            bounds.append((prev, j))
            prev = j + 1
        bounds.append((prev, m))
        blocks = []
        for lo, hi in bounds:
            diag = []
            for c in range(t):
                acc = group.identity
                for s in range(lo, hi + 1):
                    acc = group.mul(acc, h[c][s])
                diag.append(acc)
            blocks.append(diag)
        if not picks:
            diag = blocks[0]
            for c in range(t):
                out[c * t + c] ^= ga.basis(diag[c])
            continue
        lead = blocks[0]
        trail = blocks[-1]
        # chain scalar S = sigma_1 x_j2 sigma_2 ... x_jk (k = len(picks))
        s_prod = ga.one
        ok = True
        for bi in range(1, len(blocks) - 1):
            diag = blocks[bi]
            sigma = 0
            for c in range(t):
                if ((u >> c) & 1) and ((v >> c) & 1):
                    sigma ^= ga.basis(diag[c])
            if bi > 1:
                s_prod = ga.mul(s_prod, xs[picks[bi - 1]])
            s_prod = ga.mul(s_prod, sigma)
            if s_prod == 0:
                ok = False
                break
        if not ok:
            continue
        if len(picks) > 1:
            s_prod = ga.mul(s_prod, xs[picks[-1]])
        x1 = xs[picks[0]]
        for a in range(t):
            if not ((u >> a) & 1):
                continue
            pref = ga.mul(ga.basis(lead[a]), x1)
            if pref == 0:
                continue
            for b in range(t):
                if not ((v >> b) & 1):
                    continue
                mid = ga.mul(pref, s_prod)
                if mid == 0:
                    continue
                val = ga.mul(mid, ga.basis(trail[b]))
                out[a * t + b] ^= val
    return tuple(out)


def six_distinct_search(ga, group, t, labels, m_values, w_all, probe=None,
                        target=None):
    """Exhaustive search of the frame-plus-one-extra family: t frame classes
    (odd multiplicities) plus one extra projector W (even multiplicity m) at
    any word positions.  Returns per-m receipts with survivors.

    One signature DP runs over all extra-position patterns at once: a state is
    the S_t-canonical tuple of (class segment products, parity) rows plus the
    extra-position label word.  Canonicalization is complete because every W
    candidate is tested and GL_t conjugation preserves the endpoint."""
    n = len(labels)
    if target is None:
        target = ring_target(ga, t, group.S)
    receipts = {}
    for m in m_values:
        init_row = (tuple(group.identity for _ in range(m + 1)), 0)
        states = {(tuple(sorted([init_row] * t)), ()): 1}
        for i in range(n):
            nxt = {}
            for (rows, wl), cnt in states.items():
                if len(wl) < m:
                    key = (rows, wl + (labels[i],))
                    nxt[key] = nxt.get(key, 0) + cnt
                seg = len(wl)
                for ci in range(t):
                    row, par = rows[ci]
                    r2 = list(row)
                    r2[seg] = group.mul(r2[seg], labels[i])
                    unit = (tuple(r2), par ^ 1)
                    merged = tuple(sorted(rows[:ci] + (unit,) + rows[ci + 1:]))
                    key = (merged, wl)
                    nxt[key] = nxt.get(key, 0) + cnt
            states = nxt
        sigs = {}
        assignments = 0
        peak = len(states)
        for (rows, wl), cnt in states.items():
            if len(wl) != m:
                continue
            if any(par == 0 for _, par in rows):
                continue
            flat = tuple(row[s] for row, _ in rows for s in range(m + 1))
            key = (m, wl, flat)
            sigs[key] = sigs.get(key, 0) + cnt
            assignments += cnt
        survivors = []
        evals = 0
        full = (1 << len(w_all)) - 1
        uvmask = [0] * t
        for idx, (u, v) in enumerate(w_all):
            for c in range(t):
                if ((u >> c) & 1) and ((v >> c) & 1):
                    uvmask[c] |= 1 << idx
        for key, cnt in sigs.items():
            m_, wlabels, flat = key
            h = [[flat[c * (m_ + 1) + s] for s in range(m_ + 1)]
                 for c in range(t)]
            # sound diagonal pre-filter: the empty-subset term contributes
            # prod_s h[c][s] to entry (c,c) and every other term carries the
            # factor u_c v_c, so a class whose segment product differs from
            # the target diagonal forces u_c v_c = 1.
            need = full
            for c in range(t):
                prod = group.identity
                for s in range(m_ + 1):
                    prod = group.mul(prod, h[c][s])
                if ga.basis(prod) != target[c * t + c]:
                    need &= uvmask[c]
                    if need == 0:
                        break
            wm = need
            while wm:
                low = wm & -wm
                idx = low.bit_length() - 1
                wm ^= low
                u, v = w_all[idx]
                evals += 1
                got = sig_eval(ga, group, t, wlabels, h, u, v)
                if got == target:
                    survivors.append((key, u, v, cnt))
        digest = hashlib.sha256()
        for key in sorted(sigs):
            digest.update(repr(key).encode())
        receipts["m%d" % m] = {
            "w_subsets": None,
            "assignments": assignments,
            "signatures": len(sigs),
            "w_candidates": len(w_all),
            "evaluations": evals,
            "survivors": len(survivors),
            "signature_sha256": digest.hexdigest(),
            "peak_dp_states": peak,
            "witnesses": survivors[:5],
            "all_witnesses": survivors,
        }
        if probe:
            probe(receipts["m%d" % m])
    return receipts


# --------------------------------------------------------------------------
# Self-test (see tests/test_research_exact_word_search.py for the full suite).
# --------------------------------------------------------------------------


def selftest():
    g = gl2f2()
    ga = GroupAlgebra(g)
    assert g.mul(g.A, g.A) == g.identity
    assert g.mul(g.mul(g.A, g.B), g.A) == g.S
    assert len(rank_one_idempotents(5)) == 496
    t = 5
    labels = alt_labels(g, 15)
    projs = [coord_proj(t, i // 3) for i in range(15)]
    assert word_product(ga, g, t, labels, projs) == ring_target(ga, t, g.S)
    projs2 = list(projs)
    projs2[0] = coord_proj(t, 1)
    assert word_product(ga, g, t, labels, projs2) != ring_target(ga, t, g.S)
    return "SELFTEST_OK"


if __name__ == "__main__":
    print(selftest())
