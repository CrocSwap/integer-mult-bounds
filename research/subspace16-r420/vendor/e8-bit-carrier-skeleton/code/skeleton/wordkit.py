# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Word builder for bit words with mutable sources ('bitE8/1+mut'): registers x 0..v-1, y v..2v-1, helpers 2v...
Tracks frames (closed line masks) and F2 contents (int bitsets over columns x | y0 | dirt), checks nesting on the fly,
and emits the bitE8/1 JSON (D, A, scatter, B, C, final) with D (dirt compensation at frame 0) and C (reverse of every
z-destination gate of A and B at FULL) rebuilt as in #370's fullword.py."""
import gzip
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e8  # noqa: E402

V = e8.V
FULL = e8.FULL


class Word:
    def __init__(self):
        self.nh = 0
        self.cur = {}                 # register -> current frame mask
        self.content = {}             # register -> int (columns: x 0..119, y0 120..239, dirt 240+h)
        self.dims = {}                # register -> list of frame dims visited
        for s in range(V):
            self.cur[s] = 1 << s
            self.content[s] = 1 << s
        for t in range(V):
            self.cur[V + t] = 0
            self.content[V + t] = 1 << (V + t)
        self.A, self.B = [], []
        self.ret = []
        self.phase = "A"
        self.role = {}
        self.cleanup = "literal"

    def helper(self, role=""):
        r = 2 * V + self.nh
        self.nh += 1
        self.cur[r] = 0
        self.content[r] = 1 << r
        self.role[r] = role
        return r

    def climb(self, r, F):
        F = e8.closure(F)[0] if F else 0
        a = self.cur[r]
        if a == F:
            return
        assert (a & ~F) == 0 and a != F, ("frame not nested", r, e8.bits(a), e8.bits(F))
        self.cur[r] = F

    def gate(self, F, dst, srcs):
        F = e8.closure(F)[0]
        regs = [dst] + list(srcs)
        assert len(set(regs)) == len(regs)
        assert not (V <= dst < 2 * V and self.phase == "A"), "y written before the scatter"
        for r in regs:
            if V <= r < 2 * V:
                assert self.phase == "B", "y used before the scatter"
            self.climb(r, F)
        for s in srcs:
            self.content[dst] ^= self.content[s]
        (self.A if self.phase == "A" else self.B).append((F, dst, list(srcs)))

    def xpart(self, r):
        return self.content[r] & ((1 << V) - 1)

    def build(self, scatter_rows):
        """scatter_rows[t] = list of indices into self.ret.  Returns the JSON dict."""
        nreg = 2 * V + self.nh
        frames = {}

        def fid(mask):
            if mask not in frames:
                frames[mask] = len(frames)
            return frames[mask]
        fid(0)
        fid(FULL)
        A = [[fid(F), d, list(s)] for F, d, s in self.A]
        B = [[fid(F), d, list(s)] for F, d, s in self.B]
        # dirt reaching y (columns of helpers)
        dv = [0] * nreg
        for r in range(2 * V, nreg):
            dv[r] = 1 << (r - 2 * V)
        for f, d, srcs in A:
            for s in srcs:
                dv[d] ^= dv[s]
        cdirt = [dv[q] for q in self.ret]
        for t in range(V):
            for k in scatter_rows[t]:
                dv[V + t] ^= cdirt[k]
        for f, d, srcs in B:
            for s in srcs:
                dv[d] ^= dv[s]
        D = []
        for t in range(V):
            m = dv[V + t]
            srcs = []
            while m:
                b = m & -m
                srcs.append(2 * V + b.bit_length() - 1)
                m ^= b
            if srcs:
                D.append([fid(0), V + t, srcs])
        Cl = []
        if self.cleanup == "literal":
            for f, d, srcs in reversed(A + B):
                if d < V or d >= 2 * V:
                    Cl.append([fid(FULL), d, srcs])
        else:
            # segment-wise inverse: maximal runs of z-destination gates at one frame are undone, in reverse order,
            # by a cascade-free (U then L) realisation of the run's inverse, which keeps the prefix bill small.
            zg = [(f, d, srcs) for f, d, srcs in (A + B) if d < V or d >= 2 * V]
            segs = []
            for g in zg:
                if segs and segs[-1][0][0] == g[0]:
                    segs[-1].append(g)
                else:
                    segs.append([g])
            for seg in reversed(segs):
                regs = sorted({r for f, d, srcs in seg for r in [d] + list(srcs)})
                idx = {r: i for i, r in enumerate(regs)}
                n = len(regs)
                cur = [1 << i for i in range(n)]          # contents in the segment-start basis
                for f, d, srcs in seg:
                    for s in srcs:
                        cur[idx[d]] ^= cur[idx[s]]
                ops = inverse_ops_nopivot(cur)
                if ops is None:
                    import random as _r
                    rr = _r.Random(len(Cl) * 7919 + n)
                    for _ in range(400):
                        perm = list(range(n))
                        rr.shuffle(perm)            # new label k <- old wire perm[k]
                        inv = {perm[k]: k for k in range(n)}
                        cur2 = []
                        for k in range(n):
                            row = cur[perm[k]]
                            nr = 0
                            for j in range(n):
                                if row >> j & 1:
                                    nr |= 1 << inv[j]
                            cur2.append(nr)
                        ops2 = inverse_ops_nopivot(cur2)
                        if ops2 is not None:
                            ops = [(perm[a], perm[b]) for a, b in ops2]
                            break
                if ops is None:
                    for f, d, srcs in reversed(seg):
                        Cl.append([fid(FULL), d, srcs])
                    continue
                for a, b in ops:
                    Cl.append([fid(FULL), regs[a], [regs[b]]])
        fr = [None] * len(frames)
        for mk, i in frames.items():
            fr[i] = e8.bits(mk)
        start = [fid(1 << s) for s in range(V)] + [fid(0)] * (V + self.nh)
        final = [fid(FULL)] * V + [fid(e8.HYP[t]) for t in range(V)] + [fid(FULL)] * self.nh
        return dict(format="bitE8/1+mut", coords="ham", h=8, v=V, R=self.nh, lines=[list(r) for r in e8.LINES],
                    form="<x,y>/2", frames=fr, start=start, final=final, ret=list(self.ret),
                    scatter=[list(r) for r in scatter_rows], D=D, A=A, B=B, C=Cl)


def save(cert, path):
    data = json.dumps(cert, separators=(",", ":"), sort_keys=True).encode()
    if path.endswith(".gz"):
        with open(path, "wb") as fh:
            with gzip.GzipFile(filename="", mode="wb", fileobj=fh, mtime=0) as gz:
                gz.write(data)
    else:
        open(path, "wb").write(data)


def inverse_ops_nopivot(rows):
    """rows[i] (int bitset over n columns) = current content of wire i in a basis where the goal is wire i = e_i.
    Find wire operations (a, b) [wire a ^= wire b], applied in order, that bring every wire to e_i, realised as
    N = M^-1 = L U without pivoting (apply U: increasing a with b > a; then L: decreasing a with b < a): no wire
    reads a wire already modified in the same factor.  Returns None if a zero pivot appears."""
    n = len(rows)
    # invert M over F2 (Gauss-Jordan on [M | I])
    A = [rows[i] | (1 << (n + i)) for i in range(n)]
    for col in range(n):
        p = next((r for r in range(col, n) if A[r] >> col & 1), None)
        if p is None:
            raise ValueError("singular segment")
        A[col], A[p] = A[p], A[col]
        for r in range(n):
            if r != col and A[r] >> col & 1:
                A[r] ^= A[col]
    Ninv = [[(A[i] >> (n + j)) & 1 for j in range(n)] for i in range(n)]   # rows of M^-1
    # LU without pivoting of Ninv: Ninv = L U
    Uu = [row[:] for row in Ninv]
    Lm = [[0] * n for _ in range(n)]
    for col in range(n):
        if not Uu[col][col]:
            return None
        for r in range(col + 1, n):
            if Uu[r][col]:
                Lm[r][col] = 1
                Uu[r] = [a ^ b for a, b in zip(Uu[r], Uu[col])]
    ops = []
    for i in range(n):
        for j in range(i + 1, n):
            if Uu[i][j]:
                ops.append((i, j))
    for i in range(n - 1, -1, -1):
        for j in range(i):
            if Lm[i][j]:
                ops.append((i, j))
    cur = list(rows)
    for a, b in ops:
        cur[a] ^= cur[b]
    assert all(cur[i] == 1 << i for i in range(n))
    return ops


def solve_transform_lu(inputs, outputs):
    """Same contract as solve_transform, but realises the transform as P T = L U (U applied first, rows in increasing
    order; then L, rows in decreasing order), so every wire receives at most n terms per factor and the
    cancellation-free row norms stay below n^2 times the input norms."""
    n = len(inputs)
    basis = []
    for i, v in enumerate(inputs):
        combo = 1 << i
        for pb, bv, bc in basis:
            if v >> pb & 1:
                v ^= bv
                combo ^= bc
        assert v, "inputs dependent"
        basis.append((v.bit_length() - 1, v, combo))
        basis.sort(key=lambda z: -z[0])

    def coords(w):
        c = 0
        for pb, bv, bc in basis:
            if w >> pb & 1:
                w ^= bv
                c ^= bc
        assert w == 0, "output not in span of inputs"
        return c
    T = [coords(o) for o in outputs]          # T[k] bit j: output k uses input j
    # LU with row pivoting over F2: find permutation perm (output order) with T[perm] = L U
    A = [[(T[k] >> j) & 1 for j in range(n)] for k in range(n)]
    perm = list(range(n))
    Lm = [[0] * n for _ in range(n)]
    for col in range(n):
        p = next((r for r in range(col, n) if A[r][col]), None)
        assert p is not None, "outputs dependent"
        if p != col:
            A[col], A[p] = A[p], A[col]
            perm[col], perm[p] = perm[p], perm[col]
            for j in range(col):
                Lm[col][j], Lm[p][j] = Lm[p][j], Lm[col][j]
        for r in range(col + 1, n):
            if A[r][col]:
                Lm[r][col] = 1
                A[r] = [a ^ b for a, b in zip(A[r], A[col])]
    U = A                                        # upper unitriangular
    ops = []
    for i in range(n):                           # w <- U w
        for j in range(i + 1, n):
            if U[i][j]:
                ops.append((i, j))
    for i in range(n - 1, -1, -1):               # w <- L w
        for j in range(i):
            if Lm[i][j]:
                ops.append((i, j))
    # wire i ends holding output perm[i]
    assign = [None] * n
    for i in range(n):
        assign[perm[i]] = i
    cur = list(inputs)
    for a, b in ops:
        cur[a] ^= cur[b]
    for k in range(n):
        assert cur[assign[k]] == outputs[k]
    return ops, assign


def solve_transform(inputs, outputs):
    """inputs/outputs: lists of ints (vectors over F2, the x-parts), same length n, outputs in span(inputs) and
    independent.  Returns (ops, assign): ops = list of (i, j) meaning wire i ^= wire j (applied in order), and
    assign[k] = index of the wire that ends holding outputs[k] (as a combination of inputs, ignoring other columns).
    Method: express outputs in the input basis (matrix T, rows), reduce T to a permutation by row operations."""
    n = len(inputs)
    # coordinates of each output in the input basis
    basis = []   # (pivot bit, vector, combo)
    for i, v in enumerate(inputs):
        combo = 1 << i
        for pb, bv, bc in basis:
            if v >> pb & 1:
                v ^= bv
                combo ^= bc
        assert v, "inputs dependent"
        pb = v.bit_length() - 1
        basis.append((pb, v, combo))

    def coords(w):
        c = 0
        for pb, bv, bc in basis:
            if w >> pb & 1:
                w ^= bv
                c ^= bc
        assert w == 0, "output not in span of inputs"
        return c
    T = [coords(o) for o in outputs]          # row k: which inputs make output k
    # reduce T to a permutation matrix with row ops; record ops (row a ^= row b)
    rows = list(T)
    ops_rev = []
    used = set()
    piv_of_row = {}
    for col in range(n):
        p = next((r for r in range(n) if r not in used and rows[r] >> col & 1), None)
        assert p is not None, "outputs dependent"
        used.add(p)
        piv_of_row[p] = col
        for r in range(n):
            if r != p and rows[r] >> col & 1:
                rows[r] ^= rows[p]
                ops_rev.append((r, p))
    # now rows[r] = 1 << piv_of_row[r]; T = E_1 ... E_k P  where ops_rev = [E_1 ... E_k] applied to T gives P
    # Output k = row k of T.  Starting from wires holding inputs, put input piv_of_row[k] on "slot k" (relabel), then
    # apply the inverse sequence: T = E_1^-1 ... E_k^-1 P, so apply E_k first ... E_1 last (each E is self-inverse).
    # slot k is the wire that initially holds input piv_of_row[k]
    wire_of_slot = {k: piv_of_row[k] for k in range(n)}
    ops = []
    for (a, b) in reversed(ops_rev):
        ops.append((wire_of_slot[a], wire_of_slot[b]))
    assign = [wire_of_slot[k] for k in range(n)]
    # verify
    cur = list(inputs)
    for a, b in ops:
        cur[a] ^= cur[b]
    for k in range(n):
        assert cur[assign[k]] == outputs[k]
    return ops, assign
