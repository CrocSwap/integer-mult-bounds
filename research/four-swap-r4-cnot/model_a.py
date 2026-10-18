"""Exact four-coordinate-SWAP search in the formal F2[GL2(F2)] register model.

Model (self-contained; see TASK.md and README):
  G = GL2(F2) = S3 = <a,b | a^2 = b^2 = (ab)^3 = 1>, S = aba = bab.
  r registers; a paid call is C(g,N) = I + ([g]+1)N in M_r(F2[G]),
  g in {a,b}, N a binary rank-one idempotent over F2^r.
  Target T = diag([S],...,[S],1,...,1) with t SWAP entries.
  Exact matrix equality in M_r(F2[G]) is the acceptance test (arbitrary
  dirty inputs, full restoration).

Two exact homomorphic images are used for a complete finite search:
  * the natural representation (entrywise 2-dim rep of S3): states are 2r x 2r
    binary matrices packed in one int;
  * the sign quotient F2[G] -> F2[eps]/(eps^2): the eps-part of a q-call word
    is the XOR sum of the call idempotents (a written invariant, README L1-L3).

Written invariants proved in README:
  L1 (det parity): q = t (mod 2).
  L2 (mixing is useless here): with free scalar GL_r mixing anywhere,
     any word hitting T = [S]*I_r has mixing factor U = I and sum N_i = I_r
     when t = r (and sum N_i = D_t in general).
  L3: each call is an involution, and products of q calls are closed under
     inversion within the q-call ball.

This file is implementation A (bit-row matrices).  Implementation B
(search_b.py) is written independently for cross-checking.
Standard library only.
"""

import itertools
import sys
import time

# ---------------- group G = GL2(F2) = S3 as 2x2 binary matrices -------------
# elements: 0 = e, then the others by enumeration; multiplication as matrices.

def mm2(p, q):
    # 2x2 binary matrices packed as (a00 a01 a10 a11) bits 0..3: row major
    a00, a01, a10, a11 = p & 1, (p >> 1) & 1, (p >> 2) & 1, (p >> 3) & 1
    b00, b01, b10, b11 = q & 1, (q >> 1) & 1, (q >> 2) & 1, (q >> 3) & 1
    r00 = (a00 & b00) ^ (a01 & b10)
    r01 = (a00 & b01) ^ (a01 & b11)
    r10 = (a10 & b00) ^ (a11 & b10)
    r11 = (a10 & b01) ^ (a11 & b11)
    return r00 | (r01 << 1) | (r10 << 2) | (r11 << 3)

IDENT2 = 0b1001  # [[1,0],[0,1]]
A_MAT = 0b1011   # [[1,1],[0,1]]  (order 2)
B_MAT = 0b1101   # [[1,0],[1,1]]  (order 2)
assert mm2(A_MAT, A_MAT) == IDENT2
assert mm2(B_MAT, B_MAT) == IDENT2
S_MAT = mm2(mm2(A_MAT, B_MAT), A_MAT)   # aba
assert S_MAT == mm2(B_MAT, mm2(A_MAT, B_MAT))  # bab
assert mm2(S_MAT, S_MAT) == IDENT2

# enumerate all six elements, index them, with a = A_MAT, b = B_MAT first
_ELTS = []
for bits in range(16):
    m = bits
    # invertible iff det = a00*a11 + a01*a10 = 1 over F2
    d = ((m & 1) & ((m >> 3) & 1)) ^ (((m >> 1) & 1) & ((m >> 2) & 1))
    if d == 1:
        _ELTS.append(m)
assert len(_ELTS) == 6
ELTS = _ELTS                      # list of 6 matrices
E_IDX = ELTS.index(IDENT2)
A_IDX = ELTS.index(A_MAT)
B_IDX = ELTS.index(B_MAT)
S_IDX = ELTS.index(S_MAT)

# multiplication table over indices; F2[G] element = 6-bit mask
MUL = [[ELTS.index(mm2(ELTS[i], ELTS[j])) for j in range(6)] for i in range(6)]
INV = [ELTS.index(mm2(ELTS[i], ELTS[i])) for i in range(6)]  # placeholder
INV = [0] * 6
for i in range(6):
    for j in range(6):
        if MUL[i][j] == E_IDX:
            INV[i] = j
assert all(MUL[i][INV[i]] == E_IDX for i in range(6))

def elmul_mask(x, y):
    """product of two F2[G] elements given as 6-bit masks"""
    out = 0
    xs = x
    i = 0
    while xs:
        if xs & 1:
            ys = y
            j = 0
            while ys:
                if ys & 1:
                    out ^= 1 << MUL[i][j]
                ys >>= 1
                j += 1
        xs >>= 1
        i += 1
    return out

# sign of each element (parity of the permutation; abelianization G -> C2)
def _sign(m):
    # det of (m + I) tells transvection (odd) vs order 3 (even): use parity
    # via commutator: m is even iff m is in A3 = {e, ab, ba}
    return 0 if m in (IDENT2, mm2(A_MAT, B_MAT), mm2(B_MAT, A_MAT)) else 1

SIGN = [_sign(m) for m in ELTS]
# sanity: sign is a homomorphism
assert all(SIGN[MUL[i][j]] == (SIGN[i] ^ SIGN[j]) for i in range(6) for j in range(6))
assert SIGN[A_IDX] == 1 and SIGN[B_IDX] == 1 and SIGN[S_IDX] == 1

# ---------------- rank-one idempotents over F2^r ---------------------------

def rank_one_idempotents(r):
    """N = v phi with phi(v) = 1, as r x r binary row-tuple"""
    out = []
    for v in range(1, 1 << r):
        for phi in range(1 << r):
            # phi as bitmask of coefficients; phi(v) = dot = 1
            dot = bin(phi & v).count('1') & 1
            if dot != 1:
                continue
            rows = []
            for i in range(r):
                vi = (v >> i) & 1
                rows.append(tuple(((phi >> j) & 1) if vi else 0 for j in range(r)))   # row i = v_i * phi
            out.append(tuple(rows))
    # dedup and verify idempotence + rank one
    out = sorted(set(out))
    for N in out:
        # N^2 == N
        assert all(
            sum((N[i][k] & N[k][j]) for k in range(r)) & 1 == N[i][j]
            for i in range(r) for j in range(r)
        ), N
    return out

# ---------------- natural image: (2r x 2r binary matrix) as one int --------

def nat_identity(r):
    n = 2 * r
    out = 0
    for i in range(n):
        out |= 1 << (8 * i + i) if n <= 8 else 0
    if n > 8:
        raise ValueError("packed rows assume 2r <= 8")
    return out

def pack_rows(rows, n):
    out = 0
    for i in range(n):
        out |= (rows[i] & ((1 << n) - 1)) << (8 * i)
    return out

def unpack_rows(x, n):
    return tuple((x >> (8 * i)) & ((1 << n) - 1) for i in range(n))

def mul_packed(x, y, n):
    """x,y packed n x n binary matrices (n <= 8), row i in bits 8i..8i+n-1"""
    yr = unpack_rows(y, n)
    out = 0
    for i in range(n):
        row = (x >> (8 * i)) & ((1 << n) - 1)
        acc = 0
        j = 0
        while row:
            if row & 1:
                acc ^= yr[j]
            row >>= 1
            j += 1
        out |= acc << (8 * i)
    return out

def nat_of_call(gmask_idx, N, r):
    """I + (rho(g)+I2) kron N, as 2r x 2r packed matrix"""
    A = mm2(ELTS[gmask_idx], IDENT2)  # rho(g)
    A = A ^ IDENT2                    # rho(g) + I2
    n = 2 * r
    rows = [0] * n
    for i in range(r):
        for j in range(r):
            if N[i][j]:
                a00, a01, a10, a11 = A & 1, (A >> 1) & 1, (A >> 2) & 1, (A >> 3) & 1
                rows[2 * i + 0] |= (a00 << (2 * j + 0)) | (a01 << (2 * j + 1))
                rows[2 * i + 1] |= (a10 << (2 * j + 0)) | (a11 << (2 * j + 1))
    # add identity
    for k in range(n):
        rows[k] ^= 1 << k
    return pack_rows(rows, n)

def nat_of_target(t, r):
    """kron(I_r, rho(S)) block diagonal"""
    n = 2 * r
    rows = [0] * n
    s00, s01, s10, s11 = S_MAT & 1, (S_MAT >> 1) & 1, (S_MAT >> 2) & 1, (S_MAT >> 3) & 1
    for i in range(t):
        rows[2 * i + 0] |= (s00 << (2 * i + 0)) | (s01 << (2 * i + 1))
        rows[2 * i + 1] |= (s10 << (2 * i + 0)) | (s11 << (2 * i + 1))
    for i in range(t, r):
        rows[2 * i + 0] |= 1 << (2 * i + 0)
        rows[2 * i + 1] |= 1 << (2 * i + 1)
    return pack_rows(rows, n)

# ---------------- sign-quotient sum of idempotents ------------------------

def sum_mask_of_N(N, r):
    """XOR-sum matrix N as 16-bit int (r <= 4)"""
    out = 0
    for i in range(r):
        for j in range(r):
            if N[i][j]:
                out ^= 1 << (i * r + j)
    return out

# ---------------- formal algebra core (implementation A) ------------------
# element of M_r(F2[G]): tuple of r*r 6-bit masks, row major.

def formal_identity(r):
    return tuple((1 << E_IDX) if i == j else 0 for i in range(r) for j in range(r))

def formal_mul(X, Y, r):
    out = [0] * (r * r)
    for i in range(r):
        for j in range(r):
            acc = 0
            for k in range(r):
                a = X[i * r + k]
                b = Y[k * r + j]
                if a and b:
                    acc ^= elmul_mask(a, b)
            out[i * r + j] = acc
    return tuple(out)

def formal_of_call(gi, N, r):
    gmask = 1 << gi
    gp1 = gmask ^ (1 << E_IDX)   # [g] + 1
    out = []
    for i in range(r):
        for j in range(r):
            v = gp1 if N[i][j] else 0
            if i == j:
                v ^= 1 << E_IDX
            out.append(v)
    return tuple(out)

def formal_of_target(t, r):
    out = []
    for i in range(r):
        for j in range(r):
            if i == j:
                out.append((1 << S_IDX) if i < t else (1 << E_IDX))
            else:
                out.append(0)
    return tuple(out)

# ---------------- BFS core -------------------------------------------------

def build_ball(depth, moves, r, n):
    """set of packed nat states of words of exactly `depth` calls.
    returns dict state -> eps-sum mask (or AMBIG)."""
    AMBIG = -1
    ident = nat_identity(r)
    cur = {ident: 0}
    for _ in range(depth):
        nxt = {}
        for st, sm in cur.items():
            for (mv, mv_sum, _) in moves:
                ns = mul_packed(st, mv, n)
                nsum = sm ^ mv_sum
                old = nxt.get(ns, None)
                if old is None:
                    nxt[ns] = nsum
                elif old != nsum:
                    nxt[ns] = AMBIG
        cur = nxt
    return cur

def meet_length_k(ball, k, nat_T, sum_T, r, n, need_formal=True):
    """Examine pairs F', B in ball (k calls each) with F'^{-1} B = T.
    Using moves-involution and ball inversion closure: hit iff
    (nat_F' * nat_T, sum) is in ball with sum = sum_T ^ sum_F'.
    Returns (n_hits, formal_hits, first_candidate) where candidate is
    (nat_state_F', nat_state_B) for witness reconstruction."""
    AMBIG = -1
    hits = 0
    formal_hits = []
    first = None
    for st, sm in ball.items():
        g = mul_packed(st, nat_T, n)
        want = None if sm == AMBIG else (sum_T ^ sm)
        val = ball.get(g, None)
        if val is None:
            continue
        if val != AMBIG and want is not None and val != want:
            continue
        hits += 1
        if first is None:
            first = (st, g)
    return hits, formal_hits, first
