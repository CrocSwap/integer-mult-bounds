"""Punctured quad-skeleton bit word (J3-A W1).  gen.py of PR #493 with a removed-line set P (neither source nor target).
V1 = verbatim restriction of the R489/R480 skeleton (every helper register kept as a junk wire where its line is gone)
     + totals as PSEUDO-TARGETS: for each y_j in P a fresh helper reads exactly what the (removed) target y_j would read
       (qout x2 + qdeliv at D6[Hy], then its two needers at y_j-perp): x-part = J_{y_j}|L' = z_{y_j}|L', frame rank 7.
usage: python gen_punct.py OUT.json.gz P=0,11,38,... [PLAN=...]"""
import itertools, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pword import PWord, V, e8, solve_transform_lu, save  # noqa
from geom import Geom  # noqa

GI = e8.GI
PKG = os.path.join(HERE, "..", "..", "..", "e8-bit-carrier-skeleton")   # PR #493's package (plan, skeleton modules)


def load_plan(path):
    d = json.load(open(path))
    return dict(match={tuple(f): k for f, k in d["match"]},
                ext={(q, tuple(H)): e for q, H, e in d["ext"]},
                plus={tuple(H): (l, r) for H, l, r in d["plus"]})


def span_add(basis, v):
    for pb, bv in basis:
        if v >> pb & 1:
            v ^= bv
    if v:
        basis.append((v.bit_length() - 1, v)); basis.sort(reverse=True)
        return True
    return False


def decoder_rows(cent, live):
    rows = {}
    for t in e8.bits(live):
        want = (((1 << V) - 1) ^ sum((int(GI[t, b]) & 1) << b for b in range(V))) & live
        found = None
        for k in range(len(cent) + 1):
            for C in itertools.combinations(range(len(cent)), k):
                m = 0
                for c in C:
                    m ^= cent[c]
                if m == want:
                    found = list(C); break
            if found is not None:
                break
        assert found is not None, ("row not in span of totals", t)
        rows[t] = found
    return rows


def qnode_transform(inputs_x, outs, nlive_extra=0):
    """register-level invertible transform on n = len(inputs) + junk wires: returns (nj, M rows, assign-ready outputs)."""
    n0 = len(inputs_x)
    # coordinates of each out in terms of the (independent) input x-parts
    basis = []
    for i, v in enumerate(inputs_x):
        combo = 1 << i
        for pb, bv, bc in basis:
            if v >> pb & 1:
                v ^= bv; combo ^= bc
        assert v, "live inputs dependent"
        basis.append((v.bit_length() - 1, v, combo)); basis.sort(key=lambda z: -z[0])

    def coords(w):
        c = 0
        for pb, bv, bc in basis:
            if w >> pb & 1:
                w ^= bv; c ^= bc
        assert w == 0, "output not in span of live inputs"
        return c
    A = [coords(o) for o in outs]
    # independence of the A rows; add junk coordinates for dependent ones
    bs = []
    rows = []
    nj = 0
    for a in A:
        r = a
        if not span_add(bs, r):
            nj += 1
            r = a | (1 << (n0 + nj - 1))
            assert span_add(bs, r)
        rows.append(r)
    n = n0 + nj
    # complete to a basis of F2^n with the remaining wires' unit vectors (live units first, then junk)
    left = []
    for i in range(n):
        if len(rows) + len(left) == n:
            break
        if span_add(bs, 1 << i):
            left.append(1 << i)
    assert len(rows) + len(left) == n
    return nj, rows, left


def build(G, sol, P, verbose=True, totals="pseudo", zzleft=None):
    zzleft = zzleft or {}
    Pset = set(P)
    live = ((1 << V) - 1) & ~sum(1 << s for s in Pset)
    isl = lambda s: s not in Pset
    W = PWord(live)
    match, ext, plus = sol["match"], sol["ext"], sol["plus"]
    mpairs, yy = {}, set()
    for f in G.frames4:
        a, b, c, d = f
        mp = [((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))][match[f]]
        mpairs[f] = mp
        yy.update(mp)
    stats = dict(junk_carriers=0)
    branch = {}
    for f in G.frames4:
        for s in f:
            cs = list(G.cells_of[s])
            mcell = [c for c in cs if c in yy][0]
            for c in cs:
                if c == mcell:
                    branch[(s, c)] = s if isl(s) else None
                else:
                    k = W.helper("carrier")
                    if isl(s):
                        W.gate(1 << s, k, [s])
                    else:
                        stats["junk_carriers"] += 1
                    branch[(s, c)] = k
    delivery, keeper = {}, {}
    cell_quads = {}
    for q in range(len(G.quads)):
        for c in G.qcells[q]:
            cell_quads.setdefault(c, []).append(q)
    owner_of_dcell = {G.dcell[H]: H for H in G.cells}
    for c in G.cells:
        F = G.cmask[c]
        s, d = c
        qa, qb = cell_quads[c]
        if c in yy:
            e1 = W.helper("empty"); e2 = W.helper("empty")
            srcs = [branch[(x, c)] for x in (s, d) if branch[(x, c)] is not None]
            if srcs:
                W.gate(F, e1, srcs)
                W.gate(F, e2, [e1])
            delivery[(c, qa)] = e1; delivery[(c, qb)] = e2
            keeper[(c, s)] = branch[(s, c)]; keeper[(c, d)] = branch[(d, c)]
        else:
            H = owner_of_dcell[c]
            l, _rcv = plus[H]
            l2 = d if l == s else s
            e = W.helper("empty")
            bl, bl2 = branch[(l, c)], branch[(l2, c)]
            if isl(l):
                W.gate(F, bl2, [bl])      # bl2 (junk or real carrier) <- + x_l
            # else: bl junk (x-part 0): the original gate adds nothing to x
            if isl(l) or isl(l2):
                W.gate(F, e, [bl2])
            delivery[(c, qa)] = bl2
            delivery[(c, qb)] = e
            keeper[(c, l)] = bl
    # quads
    qout = {}
    for q in range(len(G.quads)):
        U = G.quads[q]
        cs = G.qcells[q]
        wires = [delivery[(c, q)] for c in cs]
        S = 0
        for c in cs:
            S |= G.cmask[c]
        owners = G.qowners[q]
        outs = []
        for H in owners:
            e = ext[(q, H)]
            D = G.cmask[G.dcell[H]]; Qc = G.cmask[G.qcell[(q, H)]]
            outs.append(S ^ D ^ Qc ^ ({"D": D, "Q": Qc, "0": 0}[e]))
        full_inputs = [G.cmask[c] for c in cs]
        ops, assign = solve_transform_lu(full_inputs, outs)
        for a, b in ops:
            W.gate(U, wires[a], [wires[b]])
        for k, H in enumerate(owners):
            qout[(q, H)] = wires[assign[k]]
            assert W.xpart(wires[assign[k]]) == outs[k] & live, ("quad out", q, H)
    # (z,z) D6
    needer, dead = {}, []
    for H in G.cells:
        if H in yy:
            continue
        q1, q2 = G.d6quads[H]
        o1, o2 = qout[(q1, H)], qout[(q2, H)]
        l, rcv = plus[H]
        p = keeper[(G.dcell[H], l)]
        F = G.D6[H]
        other = H[0] if rcv == H[1] else H[1]
        opt = zzleft.get(H, 0)
        if opt & 1:
            o1, o2 = o2, o1
        W.gate(F, o1, [o2])
        W.gate(F, p, [o1])
        if opt & 2:
            W.gate(F, o2, [p, o1])
        needer[(H, rcv)] = p
        needer[(H, other)] = o1
        dead.append(o2)
    # Q needs
    qneed = {}
    for t in range(V):
        f = G.phi[t]
        m = [p for p in mpairs[f] if t in p][0]
        Hy = tuple(sorted(m))
        acc = e8.HYP[t] & live
        for q in G.d6quads[Hy]:
            acc ^= W.xpart(qout[(q, Hy)])
        for e in f:
            if e == t:
                continue
            H = tuple(sorted((t, e)))
            if H == Hy:
                continue
            acc ^= W.xpart(needer[(H, t)])
        if Hy in qneed:
            assert qneed[Hy] == acc, ("y-partners disagree", t)
        qneed[Hy] = acc
    # Q-nodes
    qdeliv = {}
    stats["qnode_junk"] = 0
    for bi, bmask in enumerate(G.blocks):
        cb = G.comp[bi]
        Hs = sorted(H for H in yy if G.cblk[H] == cb)
        outs = [qneed[H] for H in Hs]
        assert all((o & ~(bmask & live)) == 0 for o in outs)
        wires = []
        for f in G.frames4:
            if G.blk[f[0]] != bi:
                continue
            for c in mpairs[f]:
                for s in c:
                    if isl(s):
                        wires.append(keeper[(c, s)])
        inputs = [W.xpart(w) for w in wires]
        nj, rows, left = qnode_transform(inputs, outs)
        stats["qnode_junk"] += nj
        for j in range(nj):
            wires.append(W.helper("qjunk"))
        n = len(wires)
        allrows = rows + left
        ops, assign = solve_transform_lu([1 << i for i in range(n)], allrows)
        for a, b in ops:
            W.gate(bmask, wires[a], [wires[b]])
        for k, H in enumerate(Hs):
            qdeliv[H] = wires[assign[k]]
            assert W.xpart(wires[assign[k]]) == qneed[H], ("qdeliv", bi, H)
    # totals
    if totals == "pseudo":
        for t in sorted(P):
            f = G.phi[t]
            m = [p for p in mpairs[f] if t in p][0]
            Hy = tuple(sorted(m))
            tot = W.helper("total")
            srcs = [qout[(q, Hy)] for q in G.d6quads[Hy]] + [qdeliv[Hy]]
            W.gate(G.D6[Hy], tot, srcs)
            nd = []
            for e in f:
                if e == t:
                    continue
                H = tuple(sorted((t, e)))
                if H == Hy:
                    continue
                nd.append(needer[(H, t)])
            W.gate(e8.HYP[t], tot, nd)
            assert W.xpart(tot) == e8.HYP[t] & live, ("total", t)
            W.ret.append(tot)
    cvals = [W.xpart(q) for q in W.ret]
    rows = decoder_rows(cvals, live)
    # phase B
    W.phase = "B"
    for t in W.ports:
        f = G.phi[t]
        m = [p for p in mpairs[f] if t in p][0]
        Hy = tuple(sorted(m))
        srcs = [qout[(q, Hy)] for q in G.d6quads[Hy]] + [qdeliv[Hy]]
        W.gate(G.D6[Hy], V + t, srcs)
    for t in W.ports:
        f = G.phi[t]
        srcs = []
        for e in f:
            if e == t:
                continue
            H = tuple(sorted((t, e)))
            if H in yy:
                continue
            srcs.append(needer[(H, t)])
        W.gate(e8.HYP[t], V + t, srcs)
    word = W.build(rows)
    word["stats"] = stats
    return W, word


def main():
    args = dict(a.split("=", 1) for a in sys.argv[2:])
    P = [int(x) for x in args["P"].split(",")]
    G = Geom()
    sol = load_plan(args.get("PLAN", PKG + "/data/skeleton/plan-skB.json"))
    W, word = build(G, sol, P)
    print("R", word["R"], "v", word["v"], "gates D/A/B/C", len(word["D"]), len(word["A"]), len(word["B"]), len(word["C"]), word["stats"])
    save(word, sys.argv[1])


if __name__ == "__main__":
    main()
