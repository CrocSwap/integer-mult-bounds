#!/usr/bin/env python3
"""Tape-level simulation of Idea A (expose only the fine bits u of one axis).

Every array lives on a Tape: a list of records with ONE head.  Data are read
and written only at the head; each head step (read, write or seek by one cell)
adds one to that tape's move counter.  Seeking by a distance D costs D, which is
what a machine pays when it counts D cells off a counter (upstream counter
lemma).  The kernel's window buffer is a tape too, but its moves are reported
separately as "local": they are the line algorithm's own work, not transport.

Pipeline for one axis, with line coordinate j = J*F + u, F = 2^f:
  natural (X, J, u, Y)  --f digit moves-->  (X, J, Y, u)
  forward pass   (windowed map across <=3 slabs, periodic wrap of period s
                  spliced at u = s mod F, per-line state on its own tape,
                  per-(X,J,Y) auxiliary records, Y-validity bitmap)
  backward pass  (slabs J descending, u descending, state carried right to
                  left, auxiliary records read back)
  (X, J, Y, u)   --f digit moves-->  natural (X, J, u, Y)
and the result is compared with the same maps applied line by line.
"""
import random
import sys

MOD = 1_000_003


class Tape:
    def __init__(self, name, cells=None):
        self.name = name
        self.c = list(cells) if cells else []
        self.h = 0
        self.moves = 0

    def seek(self, pos):
        assert pos >= 0
        self.moves += abs(pos - self.h)
        self.h = pos

    def read(self):
        v = self.c[self.h] if self.h < len(self.c) else 0
        self.h += 1
        self.moves += 1
        return v

    def write(self, v):
        if self.h >= len(self.c):
            self.c.extend([0] * (self.h + 1 - len(self.c)))
        self.c[self.h] = v
        self.h += 1
        self.moves += 1


# ---------------------------------------------------------------- digit moves
def move_bit(src, P, M, S, forward, tapes):
    """Move one binary address digit past a field of size M.
    forward:  (P, b, M, S) -> (P, M, b, S);  backward: the inverse.
    Split on b into two stream tapes, then merge in output order (upstream
    elementary-streams lemma, item 2).  Returns a fresh output tape."""
    s0, s1 = Tape("split0"), Tape("split1")
    out = Tape("moved")
    src.seek(0)
    for p in range(P):
        if forward:
            for b in (0, 1):
                st = s1 if b else s0
                for _ in range(M * S):
                    st.write(src.read())
        else:
            for m in range(M):
                for b in (0, 1):
                    st = s1 if b else s0
                    for _ in range(S):
                        st.write(src.read())
    s0.seek(0)
    s1.seek(0)
    for p in range(P):
        if forward:
            for m in range(M):
                for st in (s0, s1):
                    for _ in range(S):
                        out.write(st.read())
        else:
            for st in (s0, s1):
                for _ in range(M * S):
                    out.write(st.read())
    out.seek(0)
    tapes.extend([src, s0, s1])
    return out


def expose(tape, nX, nJ, f, nY, tapes):
    for i in range(f):
        tape = move_bit(tape, nX * nJ * 2 ** (f - 1 - i), nY, 2 ** i, True, tapes)
    return tape


def restore(tape, nX, nJ, f, nY, tapes):
    for i in reversed(range(f)):
        tape = move_bit(tape, nX * nJ * 2 ** (f - 1 - i), nY, 2 ** i, False, tapes)
    return tape


# ---------------------------------------------------------------- the stand-in
class LineOp:
    """Windowed map with a periodic input (period `period`), a forward
    recurrence with a two-word state (running value, border accumulator),
    sparse "wrap" records kept for the backward sweep, then a backward
    recurrence seeded by the final forward state."""

    def __init__(self, n_in_box, period, n_out_box, n_out, center, W):
        self.n_in_box, self.period = n_in_box, period
        self.n_out_box, self.n_out = n_out_box, n_out
        self.center, self.W = center, W

    def weight(self, k, m):
        return (1 + 3 * m * m + 5 * m + 7 * (k % 13)) % MOD

    def is_wrap(self, k):
        # outputs where the input centre does not advance: density ~ 1 - s/t
        return self.center(k + 1) == self.center(k)

    def ysum(self, k, xt):
        c = self.center(k)
        return sum(self.weight(k, m) * xt(c + m) for m in range(-self.W, self.W + 1)) % MOD


A_COEF, C_COEF = 31, 17


def reference(line, op):
    """Natural-order, one line at a time."""
    xt = lambda j: line[j % op.period]
    z = b = 0
    zs, ys = [], []
    for k in range(op.n_out):
        y = op.ysum(k, xt)
        z = (A_COEF * z + y) % MOD
        b = (b + y) % MOD
        zs.append(z)
        ys.append(y)
    g = z
    out = [0] * op.n_out_box
    for k in reversed(range(op.n_out)):
        g = (C_COEF * g + zs[k] + b + (7 * ys[k] if op.is_wrap(k) else 0)) % MOD
        out[k] = g
    return zs + [0] * (op.n_out_box - op.n_out), out


# ---------------------------------------------------------------- validity
def build_bitmap(boxes, bounds, tapes):
    """Tensor product of per-axis indicator vectors, built by repeated copies.
    Cost <= 2 * prod(boxes) moves per tape."""
    cur = Tape("bm0", [1])
    for box, bnd in reversed(list(zip(boxes, bounds))):
        nxt = Tape("bm")
        n = len(cur.c)
        for d in range(box):
            cur.seek(0)
            for _ in range(n):
                v = cur.read()
                nxt.write(v if d < bnd else 0)
        tapes.append(cur)
        cur = nxt
    cur.seek(0)
    return cur


# ---------------------------------------------------------------- slab passes
def forward_pass(IN, nX, xvalid, nY, VALID, F, op, h, tapes, K, SIG=2):
    """IN holds the input in (X, J, Y, u) order with op.n_in_box per line."""
    nJin, nJout = op.n_in_box // F, op.n_out_box // F
    G = nJin * nY * F                      # input records per X group
    OUT, AUX, FINAL = Tape("out"), Tape("aux"), Tape("final")
    CP, ST, BUF = Tape("copy"), Tape("state"), Tape("buf")
    E = [Tape("E0"), Tape("E1"), Tape("E2")]
    lo = lambda k: op.center(k) - op.W
    hi = lambda k: op.center(k) + op.W
    Jp = [lo(J * F) // F for J in range(nJout)]
    # Setup per J (independent of X and Y): J' is non-decreasing and moves by <= 2.
    for J in range(1, nJout):
        assert 0 <= Jp[J] - Jp[J - 1] <= 2
    vlo = Jp[0]
    vhi = max(Jp[J] for J in range(nJout) if J * F < op.n_out) + 2
    for J in range(nJout):
        if J * F < op.n_out:
            assert hi(min(J * F + F, op.n_out) - 1) < (Jp[J] + 3) * F, "window > 3 slabs"
    assert -vlo <= h and (vhi + 1) * F - op.period <= h * F + F and op.period >= 2 * F
    op.n_e = vhi - vlo + 1
    local = 0
    for X in range(nX):
        base = X * G
        if not xvalid[X]:
            # whole group is zero: skip it, write zeros
            IN.seek(base + G)
            for _ in range(nJout * nY * F):
                OUT.write(0)
            for _ in range(nJout * nY * K):
                AUX.write(0)
            for _ in range(nY * SIG):
                FINAL.write(0)
            continue
        # copy the group so two heads can read two slabs at the same Y
        IN.seek(base)
        CP.seek(0)
        for _ in range(G):
            CP.write(IN.read())
        # build the extended (virtual, periodic) slabs vlo..vhi on E0,E1,E2 at once
        for t in E:
            t.seek(0)
        for v in range(vlo, vhi + 1):
            phys = [((v * F + u) % op.period) for u in range(F)]
            slabs = []
            for p in phys:
                if p // F not in slabs:
                    slabs.append(p // F)
            assert len(slabs) <= 2, "virtual slab draws from >2 physical slabs"
            heads = {slabs[0]: (IN, base)}
            if len(slabs) == 2:
                heads[slabs[1]] = (CP, 0)
            for Y in range(nY):
                for sl, (tp, b0) in heads.items():
                    tp.seek(b0 + (sl * nY + Y) * F)
                for p in phys:
                    tp, b0 = heads[p // F]
                    tp.seek(b0 + ((p // F) * nY + Y) * F + p % F)
                    val = tp.read()
                    assert p < op.period
                    for t in E:
                        t.write(val)
                for sl, (tp, b0) in heads.items():
                    tp.seek(b0 + (sl * nY + Y + 1) * F)   # finish the slab row
        slab_off = lambda v: (v - vlo) * nY * F
        # per-line state on its own tape, in Y order
        ST.seek(0)
        for _ in range(nY * SIG):
            ST.write(0)
        for J in range(nJout):
            kfirst = J * F
            if kfirst >= op.n_out:
                for _ in range(nY * F):
                    OUT.write(0)
                for _ in range(nY * K):
                    AUX.write(0)
                continue
            for i, t in enumerate(E):
                t.seek(slab_off(Jp[J] + i))
            ST.seek(0)
            VALID.seek(0)
            for Y in range(nY):
                ok = VALID.read()
                BUF.seek(0)
                for t in E:                          # gather 3 slab rows
                    for _ in range(F):
                        BUF.write(t.read())
                st = [ST.read() for _ in range(SIG)]
                outs, aux = [0] * F, []
                if ok:
                    z, b = st
                    w0 = Jp[J] * F
                    for u in range(F):
                        k = kfirst + u
                        if k >= op.n_out:
                            break
                        c = op.center(k)
                        acc = 0
                        BUF.seek(c - op.W - w0)
                        for m in range(-op.W, op.W + 1):
                            acc += op.weight(k, m) * BUF.read()
                        y = acc % MOD
                        z = (A_COEF * z + y) % MOD
                        b = (b + y) % MOD
                        outs[u] = z
                        if op.is_wrap(k):
                            aux.append(y)
                    ST.seek(ST.h - SIG)
                    ST.write(z)
                    ST.write(b)
                for v in outs:
                    OUT.write(v)
                assert len(aux) <= K
                for i in range(K):
                    AUX.write(aux[i] if i < len(aux) else 0)
            ST.seek(0)
        ST.seek(0)
        for _ in range(nY * SIG):
            FINAL.write(ST.read())
    local = BUF.moves
    BUF.moves = 0
    tapes.extend([IN, CP, ST, BUF, AUX] + E)
    OUT.seek(0); AUX.seek(0); FINAL.seek(0)
    return OUT, AUX, FINAL, local


def backward_pass(Z, AUX, FINAL, nX, xvalid, nY, VALID, F, op, tapes, K, SIG=2):
    nJ = op.n_out_box // F
    G = nJ * nY * F
    OUT2, ST, BUF = Tape("out2"), Tape("bstate"), Tape("bbuf")
    OUT2.c = [0] * (nX * G)          # blank tape of the output's length
    for X in range(nX):
        ST.seek(0)
        FINAL.seek(X * nY * SIG)
        for _ in range(nY * SIG):
            ST.write(FINAL.read())
        if not xvalid[X]:
            continue                     # output already blank (zero)
        top = (op.n_out - 1) // F
        for J in range(top, -1, -1):
            off = X * G + J * nY * F
            Z.seek(off)
            OUT2.seek(off)
            AUX.seek(((X * nJ + J) * nY) * K)
            ST.seek(0)
            VALID.seek(0)
            for Y in range(nY):
                ok = VALID.read()
                BUF.seek(0)
                for _ in range(F):
                    BUF.write(Z.read())
                ax = [AUX.read() for _ in range(K)]
                g, b = ST.read(), ST.read()
                res = [0] * F
                if ok:
                    ks = [J * F + u for u in range(F) if J * F + u < op.n_out]
                    nw = sum(1 for k in ks if op.is_wrap(k))
                    for u in reversed(range(len(ks))):
                        k = ks[u]
                        BUF.seek(u)
                        zk = BUF.read()
                        extra = 0
                        if op.is_wrap(k):
                            nw -= 1
                            extra = 7 * ax[nw]
                        g = (C_COEF * g + zk + b + extra) % MOD
                        res[u] = g
                    ST.seek(ST.h - SIG)
                    ST.write(g)
                    ST.write(b)
                for v in res:
                    OUT2.write(v)
    local = BUF.moves
    BUF.moves = 0
    tapes.extend([Z, AUX, FINAL, ST, BUF])
    OUT2.seek(0)
    return OUT2, local


# ---------------------------------------------------------------- one case
def run_case(name, nXbox, nXval, ybox, yval, nbox, s, t, kind, f, W, seed):
    rnd = random.Random(seed)
    F = 2 ** f
    nY = 1
    for b in ybox:
        nY *= b
    yvalid = []
    for Y in range(nY):
        r, ok = Y, True
        for b, v in reversed(list(zip(ybox, yval))):
            ok &= (r % b) < v
            r //= b
        yvalid.append(1 if ok else 0)
    xvalid = [1 if X < nXval else 0 for X in range(nXbox)]
    if kind == "expand":      # A: C^s -> C^t, input s-periodic (splice at s mod F)
        op = LineOp(nbox, s, nbox, t, lambda k: (s * k) // t, W)
    elif kind == "compress":  # B0: C^t -> C^s, input t-periodic, writes s then zeros
        op = LineOp(nbox, t, nbox, s, lambda k: (t * k) // s, W)
    else:                     # N: s -> s, s-periodic
        op = LineOp(nbox, s, nbox, s, lambda k: k, W)
    nat = {}
    for X in range(nXbox):
        for Y in range(nY):
            ok = xvalid[X] and yvalid[Y]
            nat[X, Y] = [rnd.randrange(MOD) if ok and j < op.period else 0
                         for j in range(nbox)]
    # natural layout (X, j, Y) == (X, J, u, Y)
    natural = [nat[X, Y][j] for X in range(nXbox) for j in range(nbox) for Y in range(nY)]
    tapes = []
    T0 = Tape("natural", natural)
    nJ = nbox // F
    phys = expose(T0, nXbox, nJ, f, nY, tapes)
    m_expose = sum(tp.moves for tp in tapes) + phys.moves
    for tp in tapes:
        tp.moves = 0
    phys.moves = 0
    # check exposure against the definition of the (X, J, Y, u) order
    for X in range(nXbox):
        for J in range(nJ):
            for Y in range(nY):
                for u in range(F):
                    assert phys.c[((X * nJ + J) * nY + Y) * F + u] == nat[X, Y][J * F + u]
    t2 = []
    VALID = build_bitmap(ybox, yval, t2)
    m_bitmap = sum(tp.moves for tp in t2) + VALID.moves
    VALID.moves = 0
    K = max(sum(1 for k in range(J * F, min(J * F + F, op.n_out)) if op.is_wrap(k))
            for J in range(nbox // F))
    h = 2
    tf = []
    Z, AUX, FINAL, loc_f = forward_pass(phys, nXbox, xvalid, nY, VALID, F, op, h, tf, K)
    m_fwd = sum(tp.moves for tp in tf) + Z.moves + VALID.moves
    for tp in tf:
        tp.moves = 0
    Z.moves = AUX.moves = FINAL.moves = VALID.moves = 0
    tb = []
    OUT2, loc_b = backward_pass(Z, AUX, FINAL, nXbox, xvalid, nY, VALID, F, op, tb, K)
    m_bwd = sum(tp.moves for tp in tb) + OUT2.moves + VALID.moves
    OUT2.moves = 0
    t3 = []
    back = restore(OUT2, nXbox, nJ, f, nY, t3)
    m_restore = sum(tp.moves for tp in t3) + back.moves
    # compare with natural-order reference (forward output and final output)
    okz = okg = True
    for X in range(nXbox):
        for Y in range(nY):
            zs, gs = reference(nat[X, Y], op)
            if not (xvalid[X] and yvalid[Y]):
                zs = gs = [0] * nbox
            for J in range(nJ):
                for u in range(F):
                    k = J * F + u
                    okz &= Z.c[((X * nJ + J) * nY + Y) * F + u] == zs[k]
                    okg &= back.c[(X * nbox + k) * nY + Y] == gs[k]
    V = nXbox * nY * nbox
    # Proven per-pass bounds from the lemma (records moved, all transport tapes).
    B, n_s, SIG = nY * F, nbox // F, 2
    fwd_bound = (28 * V + 11 * nXbox * (op.n_e - n_s) * B
                 + V * (4 * SIG + 2 * K + 2) / F + 4 * nXbox * nY * SIG)
    bwd_bound = 11 * V + V * (3 * K + 6 * SIG + 2) / F + 4 * nXbox * nY * SIG
    assert m_fwd <= fwd_bound, (name, m_fwd, fwd_bound)
    assert m_bwd <= bwd_bound, (name, m_bwd, bwd_bound)
    assert m_expose == 6 * f * V and m_restore == 6 * f * V
    rec = dict(name=name, kind=kind, s=s, t=t, F=F, nY=nY, nX=nXbox, V=V,
               ok=okz and okg, expose=m_expose / V / f, restore=m_restore / V / f,
               bitmap=m_bitmap / nY, fwd=m_fwd / V, bwd=m_bwd / V,
               local=(loc_f + loc_b) / V, K=K, splice=s % F)
    return rec


CASES = [
    # name, X box, X valid, Y boxes, Y valid, line box, s, t, kind, f, W
    ("e13/16 f2", 3, 2, (2, 3), (2, 2), 16, 13, 16, "expand", 2, 1),
    ("e29/32 f3", 2, 2, (4, 2), (3, 2), 32, 29, 32, "expand", 3, 2),
    ("e53/64 f3", 3, 2, (3,), (2,), 64, 53, 64, "expand", 3, 2),
    ("e61/64 f4", 2, 1, (2, 2), (2, 1), 64, 61, 64, "expand", 4, 3),
    ("e107/128 f4 Y1", 4, 3, (1,), (1,), 128, 107, 128, "expand", 4, 3),
    ("c13/16 f2", 3, 2, (2, 3), (2, 2), 16, 13, 16, "compress", 2, 1),
    ("c29/32 f3", 2, 2, (4, 2), (3, 2), 32, 29, 32, "compress", 3, 1),
    ("c53/64 f3", 3, 2, (3,), (2,), 64, 53, 64, "compress", 3, 2),
    ("c103/128 f4", 2, 2, (5,), (3,), 128, 103, 128, "compress", 4, 3),
    ("n29 f3", 2, 2, (4, 2), (3, 2), 32, 29, 32, "N", 3, 2),
    ("n61 f4", 3, 2, (3, 2), (2, 2), 64, 61, 64, "N", 4, 4),
    ("n127 f4 big", 2, 2, (8, 4), (7, 3), 128, 127, 128, "N", 4, 3),
]

def scaling():
    """fwd/V and bwd/V must stay bounded as |Y|, the X count and the line grow."""
    print("\nscaling (expand, all lines valid):")
    print(f"{'nX':>3} {'|Y|':>4} {'line':>5} {'F':>3} {'fwd/V':>6} {'bwd/V':>6}")
    for nX, ny, nbox, s, f, W in [(1, 1, 256, 211, 4, 3), (1, 16, 256, 211, 4, 3),
                                   (1, 64, 256, 211, 4, 3), (4, 16, 256, 211, 4, 3),
                                   (2, 16, 512, 487, 5, 6), (2, 16, 1024, 937, 6, 12)]:
        r = run_case("scale", nX, nX, (ny,), (ny,), nbox, s, nbox, "expand", f, W, seed=7)
        assert r["ok"]
        print(f"{nX:>3} {ny:>4} {nbox:>5} {2**f:>3} {r['fwd']:6.2f} {r['bwd']:6.2f}")



def centred_window_check():
    """The notes' window J'-1, J', J'+1 with J' = floor(J s / t) misses inputs:
    count output slabs whose inputs reach slab J'+2 (expansion map)."""
    print("\nold centred window J'-1..J'+1 (superseded) vs left-anchored J'..J'+2 (lemma); failures below are for the old window:")
    for s, t, F, W in [(211, 256, 16, 3), (937, 1024, 64, 12), (1009, 1024, 64, 8)]:
        bad = 0
        for J in range(t // F):
            jc = (J * F * s // t) // F
            lo, hi = (s * J * F) // t - W, (s * (J * F + F - 1)) // t + W
            bad += hi >= (jc + 2) * F or lo < (jc - 1) * F
        print(f"  s={s} t={t} F={F} W={W}: {bad} of {t // F} slabs fail")


if __name__ == "__main__":
    allok = True
    hdr = f"{'case':16} {'ok':4} {'s%F':>4} {'|Y|':>4} {'K':>2} {'exp/Vf':>7} {'fwd/V':>6} {'bwd/V':>6} {'rst/Vf':>7} {'local/V':>8}"
    print(hdr)
    worst = {"fwd": 0, "bwd": 0, "expose": 0, "restore": 0}
    for i, c in enumerate(CASES):
        r = run_case(*c, seed=i)
        allok &= r["ok"]
        for k in worst:
            worst[k] = max(worst[k], r[k])
        print(f"{r['name']:16} {'PASS' if r['ok'] else 'FAIL':4} {r['splice']:>4} {r['nY']:>4} {r['K']:>2} "
              f"{r['expose']:7.2f} {r['fwd']:6.2f} {r['bwd']:6.2f} {r['restore']:7.2f} {r['local']:8.2f}")
    print("worst:", {k: round(v, 2) for k, v in worst.items()})
    print("ALL PASS" if allok else "SOME FAIL")
    if "--scale" in sys.argv:
        scaling()
    centred_window_check()
    sys.exit(0 if allok else 1)

