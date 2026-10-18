# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Generate a quad-skeleton bit word with mutable sources (skeleton B) from a CP-SAT plan.

usage: PLAN=data/skeleton/plan-skB.json python -I gen.py OUT.json.gz 0 fresh   (the R = 489 word)
Register roles per 4-frame Phi = {t,m,c,d} (matching {t,m},{c,d}):
  sources (4) sit in their matching cell; carriers (8, born at frame 0, copy x_s at line(s)) in the cross cells and
  the other matching-cell slot; empties (8): one per cross cell, two per matching cell.
Phase A: carriers copy; cells form deliveries (two per cell) and keep single lines; quads apply the butterfly
S + u_H; Q-nodes (block D4 frames) turn their 12 kept lines into 6 deliveries for the (y,y) D6s of the complementary
block plus 6 leftovers; (z,z) D6s form two needers + leftover; totals are formed at FULL on dead registers.
Phase B: y climbs 0 -> its (y,y) D6 (reads 3 registers) -> t^perp (reads its two needers)."""
import itertools
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e8  # noqa: E402
from geom import Geom  # noqa: E402
from wordkit import Word, save, solve_transform_lu as solve_transform  # noqa: E402

V = e8.V
GI = e8.GI


CLEANUP = ["literal"]
QHOST = [False]


def decoder_basis():
    """the 9 decoder totals: T0 = all lines, T_i = {s : <a_i,s> odd} for 8 lines a_i independent mod 2 (as #370)."""
    B = [[int(GI[a, b]) & 1 for b in range(V)] for a in range(V)]
    piv = {}
    basis = []
    for a in range(V):
        m = sum(B[a][b] << b for b in range(V))
        while m:
            p = m.bit_length() - 1
            if p in piv:
                m ^= piv[p]
            else:
                piv[p] = m
                basis.append(a)
                break
        if len(basis) == 8:
            break
    return [(1 << V) - 1] + [sum(B[a][b] << b for b in range(V)) for a in basis]


def decoder_rows(cent):
    """scatter rows: subsets of centres whose XOR = 1 + B(t,.) (x_t plus the 63 lines of t^perp)."""
    full = (1 << V) - 1
    rows = []
    for t in range(V):
        want = full ^ sum((int(GI[t, b]) & 1) << b for b in range(V))
        found = None
        for k in range(len(cent) + 1):
            for C in itertools.combinations(range(len(cent)), k):
                m = 0
                for c in C:
                    m ^= cent[c]
                if m == want:
                    found = list(C)
                    break
            if found is not None:
                break
        assert found is not None
        rows.append(found)
    return rows


def span_reduce(basis, v):
    for pb, bv in basis:
        if v >> pb & 1:
            v ^= bv
    return v


def span_add(basis, v):
    v = span_reduce(basis, v)
    if v:
        basis.append((v.bit_length() - 1, v))
        basis.sort(reverse=True)
        return True
    return False


def build(G, sol, verbose=True, patch_lines=(), zzleft=None, fresh_totals=False):
    zzleft = zzleft or {}
    W = Word()
    W.cleanup = CLEANUP[0]
    patches = []
    for s in patch_lines:
        k = W.helper("totalpatch")
        W.gate(1 << s, k, [s])        # copy x_s at its line before the source leaves it
        patches.append(k)
    match = sol["match"]
    ext = sol["ext"]
    plus = sol["plus"]
    mpairs = {}
    yy = set()
    for f in G.frames4:
        a, b, c, d = f
        mp = [((a, b), (c, d)), ((a, c), (b, d)), ((a, d), (b, c))][match[f]]
        mpairs[f] = mp
        yy.update(mp)
    # ---- branches: source sits in its matching cell, carriers elsewhere
    branch = {}       # (line, cell) -> register
    for f in G.frames4:
        for s in f:
            cs = [c for c in G.cells_of[s]]
            mcell = [c for c in cs if c in yy][0]
            for c in cs:
                if c == mcell:
                    branch[(s, c)] = s
                else:
                    k = W.helper("carrier")
                    W.gate(1 << s, k, [s])
                    branch[(s, c)] = k
    # ---- cells
    delivery = {}     # (cell, quad) -> register carrying the cell sum
    keeper = {}       # (cell, line) -> register holding x_line
    cell_quads = defaultdict(list)
    for q in range(len(G.quads)):
        for c in G.qcells[q]:
            cell_quads[c].append(q)
    owner_of_dcell = {}
    for H in G.cells:
        owner_of_dcell[G.dcell[H]] = H
    for c in G.cells:
        F = G.cmask[c]
        s, d = c
        qa, qb = cell_quads[c]
        if c in yy:          # matching cell: keep both lines
            e1 = W.helper("empty")
            e2 = W.helper("empty")
            W.gate(F, e1, [branch[(s, c)], branch[(d, c)]])
            W.gate(F, e2, [e1])
            delivery[(c, qa)] = e1
            delivery[(c, qb)] = e2
            keeper[(c, s)] = branch[(s, c)]
            keeper[(c, d)] = branch[(d, c)]
        else:                # cross cell: keep the plus line of the (z,z) D6 whose d-cell it is
            H = owner_of_dcell[c]
            l, _rcv = plus[H]
            l2 = d if l == s else s
            e = W.helper("empty")
            W.gate(F, branch[(l2, c)], [branch[(l, c)]])
            W.gate(F, e, [branch[(l2, c)]])
            delivery[(c, qa)] = branch[(l2, c)]
            delivery[(c, qb)] = e
            keeper[(c, l)] = branch[(l, c)]
    # ---- quads: butterfly
    qout = {}         # (quad, owner D6) -> register
    for q in range(len(G.quads)):
        U = G.quads[q]
        cs = G.qcells[q]
        wires = [delivery[(c, q)] for c in cs]
        inputs = [W.xpart(w) for w in wires]
        S = 0
        for c in cs:
            S |= G.cmask[c]
        owners = G.qowners[q]
        outs = []
        for H in owners:
            e = ext[(q, H)]
            D = G.cmask[G.dcell[H]]
            Qc = G.cmask[G.qcell[(q, H)]]
            o = S ^ (Qc if e == "D" else (D if e == "Q" else (D ^ Qc)))
            # o = E-cells + extra: e == 'D' -> extra D ; 'Q' -> extra Q-cell ; '0' -> none
            o = S ^ D ^ Qc ^ ({"D": D, "Q": Qc, "0": 0}[e])
            outs.append(o)
        # inputs as x-parts must equal cell sums
        assert sorted(inputs) == sorted(G.cmask[c] for c in cs)
        ops, assign = solve_transform(inputs, outs)
        for a, b in ops:
            W.gate(U, wires[a], [wires[b]])
        for k, H in enumerate(owners):
            qout[(q, H)] = wires[assign[k]]
            assert W.xpart(wires[assign[k]]) == outs[k]
    # ---- (z,z) D6s: two needers + leftover
    needer = {}       # (D6 owner, target) -> register
    dead = []
    for H in G.cells:
        if H in yy:
            continue
        q1, q2 = G.d6quads[H]
        o1, o2 = qout[(q1, H)], qout[(q2, H)]
        l, rcv = plus[H]
        p = keeper[(G.dcell[H], l)]
        F = G.D6[H]
        opt = zzleft.get(H, 0)
        other = H[0] if rcv == H[1] else H[1]
        if opt & 1:
            o1, o2 = o2, o1          # leftover keeps d1 instead of d2
        W.gate(F, o1, [o2])          # o1 = d1 + d2
        W.gate(F, p, [o1])           # p = x_l + d1 + d2
        if opt & 2:
            W.gate(F, o2, [p, o1])   # o2 = d2 + (x_l + d1 + d2) + (d1 + d2) = x_l + d2; needers unchanged
        needer[(H, rcv)] = p
        needer[(H, other)] = o1
        dead.append(o2)
    qleft = set()
    # ---- Q-deliveries needed per (y,y) D6: content for its targets
    def target_needs_Q(t):
        """the Q-delivery content t needs at its (y,y) D6: J_t minus everything else it reads"""
        f = G.phi[t]
        m = [p for p in mpairs[f] if t in p][0]
        Hy = tuple(sorted(m))
        acc = e8.HYP[t]
        for q in G.d6quads[Hy]:
            acc ^= W.xpart(qout[(q, Hy)])
        for e in f:
            if e == t:
                continue
            H = tuple(sorted((t, e)))
            if H == Hy:
                continue
            acc ^= W.xpart(needer[(H, t)])
        return Hy, acc
    qneed = {}
    for t in range(V):
        Hy, acc = target_needs_Q(t)
        if Hy in qneed:
            assert qneed[Hy] == acc, ("y-partners disagree", t, e8.bits(qneed[Hy] ^ acc))
        qneed[Hy] = acc
    # ---- Q-nodes
    cent = decoder_basis()
    qdeliv = {}
    for bi, bmask in enumerate(G.blocks):
        # targets served: (y,y) D6s of the complementary block's 4-frames
        cb = G.comp[bi]
        Hs = sorted(H for H in yy if G.cblk[H] == cb)
        assert len(Hs) == 6
        outs = [qneed[H] for H in Hs]
        for o in outs:
            assert (o & ~bmask) == 0, "Q-need outside the block"
        lines = e8.bits(bmask)
        wires = []
        for f in G.frames4:
            if G.blk[f[0]] != bi:
                continue
            for c in mpairs[f]:
                for s in c:
                    wires.append(keeper[(c, s)])
        assert sorted(W.xpart(w) for w in wires) == sorted(1 << s for s in lines)
        inputs = [W.xpart(w) for w in wires]
        # leftovers: complete outs to a basis, preferring the restricted decoder space
        basis = []
        for o in outs:
            assert span_add(basis, o), "Q-deliveries dependent"
        lefts = []
        nd = 0
        for T in cent:
            v = T & bmask
            if v and span_add(basis, v):
                lefts.append(v)
            elif v:
                nd += 1
        if verbose and nd:
            print("block", bi, ": restricted totals dependent on deliveries:", nd)
        for s in lines:
            if len(lefts) == 6:
                break
            if span_add(basis, 1 << s):
                lefts.append(1 << s)
        assert len(lefts) == 6, len(lefts)
        ops, assign = solve_transform(inputs, outs + lefts)
        for a, b in ops:
            W.gate(bmask, wires[a], [wires[b]])
        for k, H in enumerate(Hs):
            qdeliv[H] = wires[assign[k]]
        for k in range(6):
            dead.append(wires[assign[6 + k]])
            qleft.add(wires[assign[6 + k]])
    # ---- totals on dead registers at FULL
    dead += patches
    dbasis = []        # (pivot, vector, combo of dead registers)
    for r in dead:
        v = W.xpart(r)
        combo = {r}
        for pb, bv, bc in dbasis:
            if v >> pb & 1:
                v ^= bv
                combo ^= bc
        if v:
            dbasis.append((v.bit_length() - 1, v, combo))
            dbasis.sort(key=lambda z: -z[0])
    # deficiency of the dead span w.r.t. the decoder space; patch with single-line copies at FULL if needed
    def reduce_dead(v):
        combo = set()
        for pb, bv, bc in dbasis:
            if v >> pb & 1:
                v ^= bv
                combo ^= bc
        return v, combo
    miss = []
    for T in cent:
        v, _ = reduce_dead(T)
        if v and span_add(miss, v):
            pass
    if verbose:
        print("dead registers", len(dead), "dead span", len(dbasis), "decoder deficiency", len(miss))
    if miss:
        need = []
        for pb, v in miss:
            need.append(pb)          # one pivot line per missing dimension (copied early by a patch register)
        return ("patch", need)
    used = set()
    for T in cent:
        # reduce over current contents of the unused dead registers
        # unused dead helpers first (a total must live on a helper), then sources, then used hosts (content T_j)
        pool = ([r for r in dead if r not in used and r >= 2 * V and r in qleft]
                + [r for r in dead if r not in used and r >= 2 * V and r not in qleft]
                + [r for r in dead if r not in used and r < 2 * V] + sorted(used))
        dbasis = []
        for r in pool:
            vv = W.xpart(r)
            combo = {r}
            for pb, bv, bc in dbasis:
                if vv >> pb & 1:
                    vv ^= bv
                    combo ^= bc
            if vv:
                dbasis.append((vv.bit_length() - 1, vv, combo))
                dbasis.sort(key=lambda z: -z[0])
        v = T
        combo = set()
        for pb, bv, bc in dbasis:
            if v >> pb & 1:
                v ^= bv
                combo ^= bc
        if v:
            if verbose:
                print("total not in span of dead registers: missing", e8.popcount(v), "lines")
            return None
        if fresh_totals is True or (isinstance(fresh_totals, int) and fresh_totals is not False and cent.index(T) < fresh_totals):
            # a fresh register (frame 0 -> FULL) collects the combination: keeps the payload bill small because the
            # total's large row norm never flows back through the cleanup of other registers
            host = W.helper("total")
            others = sorted(r for r in combo if r not in used)
            assert not (combo & used)
            W.gate(e8.FULL, host, others)
            W.ret.append(host)
            assert W.xpart(host) == T
            continue
        # pick a dead register in combo not yet used as a total, make it the total
        host = next((r for r in sorted(combo) if r not in used and r >= 2 * V and (r in qleft or not QHOST[0])), None)
        assert host is not None, "no unused helper in the total's combination"
        others = [r for r in sorted(combo) if r != host]
        # host must end holding T (x-part): host ^= others
        W.gate(e8.FULL, host, others) if others else W.climb(host, e8.FULL)
        used.add(host)
        W.ret.append(host)
        assert W.xpart(host) == T
        # other dead registers keep their content (they were only read)
    cvals = [W.xpart(q) for q in W.ret]
    rows = decoder_rows(cvals)
    # ---- phase B
    W.phase = "B"
    for t in range(V):
        f = G.phi[t]
        m = [p for p in mpairs[f] if t in p][0]
        Hy = tuple(sorted(m))
        srcs = [qout[(q, Hy)] for q in G.d6quads[Hy]] + [qdeliv[Hy]]
        W.gate(G.D6[Hy], V + t, srcs)
    for t in range(V):
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
    return W, word


def save_plan(sol, path):
    out = dict(match=[[list(f), k] for f, k in sol["match"].items()],
               ext=[[q, list(H), e] for (q, H), e in sorted(sol["ext"].items())],
               plus=[[list(H), l, r] for H, (l, r) in sorted(sol["plus"].items())])
    json.dump(out, open(path, "w"), sort_keys=True)


def load_plan(path):
    d = json.load(open(path))
    return dict(match={tuple(f): k for f, k in d["match"]},
                ext={(q, tuple(H)): e for q, H, e in d["ext"]},
                plus={tuple(H): (l, r) for H, l, r in d["plus"]})


if __name__ == "__main__":
    G = Geom()
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    fm = {f: 0 for f in G.frames4}
    planfile = os.environ.get("PLAN")
    if planfile and os.path.exists(planfile):
        sol = load_plan(planfile)
        print("plan loaded from", planfile)
    else:
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "discovery"))
        from plan import solve  # CP-SAT (ortools); not needed when a plan file is given
        st, sol = solve(G, fixed_match=fm, seed=seed)
        print("plan", st)
        if planfile:
            save_plan(sol, planfile)
            print("plan saved to", planfile)
    import random
    rng = random.Random(seed)
    zzleft = {}
    FT = len(sys.argv) > 3 and sys.argv[3] == 'fresh'
    if len(sys.argv) > 3 and sys.argv[3].startswith('fresh') and sys.argv[3] != 'fresh':
        FT = int(sys.argv[3][5:])
    if len(sys.argv) > 4:
        CLEANUP[0] = sys.argv[4]
    if len(sys.argv) > 5:
        QHOST[0] = sys.argv[5] == 'qhost'

    res = build(G, sol, zzleft=zzleft, verbose=False, fresh_totals=FT)
    tries = 0
    while res and res[0] == "patch" and tries < 400:
        # random restarts of the (z,z) leftover choices until the dead span holds the decoder space
        tries += 1
        zzleft = {H: rng.randrange(4) for H in G.cells}
        res = build(G, sol, zzleft=zzleft, verbose=False, fresh_totals=FT)
    print("leftover search tries", tries)
    if res and res[0] == "patch":
        print("patching totals with single-line copies of", res[1])
        res = build(G, sol, patch_lines=res[1], zzleft=zzleft, fresh_totals=FT)
    if res:
        W, word = res
        print("R", word["R"], "gates D/A/B/C", len(word["D"]), len(word["A"]), len(word["B"]), len(word["C"]))
        save(word, sys.argv[1])
