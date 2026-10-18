# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Skeleton L3: 3 registers per cell, type-L targets that climb 0 -> d-single cell -> t^perp, every D6 (z,z).

usage: NODEOPT=2000 python -I gen_l3.py data/plan-l3.json OUT.json.gz 0 dead last   (the shipped R = 420 word)
(plan from discovery/planL3.py and planL3b.py; the generator that built the shipped word, with package import paths).
Per 4-frame Phi: each target t reads (phase B) the keeper of its cell C_t = Phi - {t, x(t)} (the source of line l_t,
sitting in C_t and keeping x_l), then climbs straight to t^perp and reads its three needers there (one per D6 of its
triple).  Every D6 forms o1 = o1 + o2 in phase A (leftover o2 dead) and
has a third register: either t's Q-delivery (the D6 is t's Q-host; in phase B qdel = qdel + o1 is t's needer, o1 the
other target's) or a free keeper of the complementary block (phase A: k = k + o1 is the recipient's needer).
The block node (phase B, after the d-single reads) turns its 12 keepers into the 12 Q-deliveries (rank 12)."""
import itertools
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "e8-bit-carrier-skeleton", "code", "skeleton"))   # PR #493 on main
sys.path.insert(0, HERE)
import e8  # noqa: E402
from geom import Geom  # noqa: E402
from gen import decoder_basis, decoder_rows, span_add  # noqa: E402
from planio import load_plan  # noqa: E402
from wordkit import Word, save, solve_transform_lu  # noqa: E402
from nodeopt import realise  # noqa: E402

V = e8.V
NODEOPT = [int(os.environ.get("NODEOPT", "2000"))]


def rank_of(vecs):
    b = []
    for v in vecs:
        span_add(b, v)
    return len(b)


def derive(G, sol, freeline=None):
    freeline = freeline or {}
    part, kline = sol["partner"], sol["kline"]
    dcellof, keepline, home, qhostD6 = {}, {}, {}, {}
    for f in G.frames4:
        for t in f:
            x = part[t]
            C = tuple(sorted(y for y in f if y not in (t, x)))
            dcellof[t] = C
            keepline[C] = kline[t]
            home[kline[t]] = C
            qhostD6[t] = tuple(sorted((t, sol["qhost"][t])))
        assert len({dcellof[t] for t in f}) == 4 and len({qhostD6[t] for t in f}) == 4
        for c in itertools.combinations(f, 2):
            if c not in keepline:
                keepline[c] = c[freeline.get(c, 0)]
    hosted = set(qhostD6.values())
    zz = [H for H in G.cells if H not in hosted]          # D6s whose third is a free keeper
    return dcellof, keepline, home, qhostD6, zz


def ex_part(G, sol, q, H):
    S = 0
    for c in G.qcells[q]:
        S |= G.cmask[c]
    D = G.cmask[G.dcell[H]]
    Qc = G.cmask[G.qcell[(q, H)]]
    return S ^ D ^ Qc ^ ({"D": D, "Q": Qc, "0": 0}[sol["ext"][(q, H)]])


def plan_thirds(G, sol, rng, tries=20000):
    dcellof, keepline, home, qhostD6, zz = derive(G, sol)
    dualcells = set(home.values())
    Ex = {H: ex_part(G, sol, G.d6quads[H][0], H) ^ ex_part(G, sol, G.d6quads[H][1], H) for H in G.cells}
    base = {}
    for t in range(V):
        acc = e8.HYP[t] ^ (1 << keepline[dcellof[t]])
        for x in G.phi[t]:
            if x != t:
                acc ^= Ex[tuple(sorted((t, x)))]
        base[t] = acc
    freeline, assign, failed = {}, {}, []
    for bi in range(len(G.blocks)):
        cb = G.comp[bi]
        us = [t for t in range(V) if G.blk[t] == cb]
        Hs = sorted(H for H in zz if G.cblk[H] == cb)
        cs = [c for c in G.cells if c not in dualcells and G.cblk[c] == bi]
        assert len(Hs) == len(cs) == 6
        ok = False
        for _ in range(tries):
            fl = {c: rng.randrange(2) for c in cs}
            perm = list(cs)
            rng.shuffle(perm)
            extra = {}
            for H, c in zip(Hs, perm):
                r = sol["rcv"][H]
                extra[r] = extra.get(r, 0) ^ (1 << c[fl[c]])
            if rank_of([base[u] ^ extra.get(u, 0) for u in us]) == 12:
                ok = True
                break
        if not ok:
            failed.append(bi)
            continue
        freeline.update(fl)
        assign.update(dict(zip(Hs, perm)))
    return (freeline, assign) if not failed else ("failed", failed)


def build(G, sol, zzleft=None, freeline=None, thirdperm=None, fresh_totals=False, host_order="last", verbose=True,
          node_seed=None):
    zzleft = zzleft or {}
    W = Word()
    ext = sol["ext"]
    dcellof, keepline, home, qhostD6, zz = derive(G, sol, freeline)
    dualcells = set(home.values())
    # ---- phase A: carriers
    branch = {}
    for s in range(V):
        for c in G.cells_of[s]:
            if c == home[s]:
                branch[(s, c)] = s
            else:
                k = W.helper("carrier")
                W.gate(1 << s, k, [s])
                branch[(s, c)] = k
    # ---- cells
    cell_quads = defaultdict(list)
    for q in range(len(G.quads)):
        for c in G.qcells[q]:
            cell_quads[c].append(q)
    delivery, keeper = {}, {}
    for c in G.cells:
        F = G.cmask[c]
        l = keepline[c]
        l2 = c[0] if l == c[1] else c[1]
        qa, qb = cell_quads[c]
        e = W.helper("empty")
        W.gate(F, branch[(l2, c)], [branch[(l, c)]])
        W.gate(F, e, [branch[(l2, c)]])
        delivery[(c, qa)] = branch[(l2, c)]
        delivery[(c, qb)] = e
        keeper[c] = branch[(l, c)]
    # ---- quads
    qout = {}
    for q in range(len(G.quads)):
        U = G.quads[q]
        cs = G.qcells[q]
        wires = [delivery[(c, q)] for c in cs]
        inputs = [W.xpart(w) for w in wires]
        outs = [ex_part(G, sol, q, H) for H in G.qowners[q]]
        ops, assign = solve_transform_lu(inputs, outs)
        for a, b in ops:
            W.gate(U, wires[a], [wires[b]])
        for k, H in enumerate(G.qowners[q]):
            qout[(q, H)] = wires[assign[k]]
    # ---- D6 nodes (phase A)
    E, dead, needer = {}, [], {}
    for H in G.cells:
        q1, q2 = G.d6quads[H]
        o1, o2 = qout[(q1, H)], qout[(q2, H)]
        if zzleft.get(H, 0) & 1:
            o1, o2 = o2, o1
        W.gate(G.D6[H], o1, [o2])
        E[H] = o1
        dead.append(o2)
    # free-keeper thirds (phase A)
    free_by_block = defaultdict(list)
    for c in G.cells:
        if c not in dualcells:
            free_by_block[G.cblk[c]].append(c)
    zz_by_block = defaultdict(list)
    for H in zz:
        zz_by_block[G.cblk[H]].append(H)
    for bi in range(len(G.blocks)):
        cb = G.comp[bi]
        Hs = sorted(zz_by_block[cb])
        cs = [thirdperm[H] for H in Hs] if thirdperm is not None else list(free_by_block[bi])
        for H, c in zip(Hs, cs):
            k = keeper[c]
            r = sol["rcv"][H]
            W.gate(G.D6[H], k, [E[H]])
            needer[(H, r)] = k
            other = H[0] if r == H[1] else H[1]
            needer[(H, other)] = E[H]
    # host D6s: the non-host target's needer is o1 (the host target's needer is formed in phase B)
    for t in range(V):
        H = qhostD6[t]
        x = H[0] if H[1] == t else H[1]
        needer[(H, x)] = E[H]
    # ---- Q needs
    need = {}
    for t in range(V):
        acc = e8.HYP[t] ^ W.xpart(keeper[dcellof[t]])
        for x in G.phi[t]:
            if x == t:
                continue
            H = tuple(sorted((t, x)))
            acc ^= W.xpart(E[H]) if H == qhostD6[t] else W.xpart(needer[(H, t)])
        need[t] = acc
        qb = G.blocks[G.comp[G.blk[t]]]
        assert acc & ~qb == 0, ("need outside Q block", t)
    ranks = {}
    for bi in range(len(G.blocks)):
        cb = G.comp[bi]
        ranks[bi] = rank_of([need[u] for u in range(V) if G.blk[u] == cb])
    if min(ranks.values()) < 12:
        return ("rank", ranks)
    # ---- totals
    cent = decoder_basis()
    dbasis = []
    for r in dead:
        v = W.xpart(r)
        for pb, bv in dbasis:
            if v >> pb & 1:
                v ^= bv
        if v:
            dbasis.append((v.bit_length() - 1, v))
            dbasis.sort(key=lambda z: -z[0])
    miss = []
    for T in cent:
        v = T
        for pb, bv in dbasis:
            if v >> pb & 1:
                v ^= bv
        if v:
            span_add(miss, v)
    if verbose:
        print("dead registers", len(dead), "dead span", len(dbasis), "decoder deficiency", len(miss))
    if miss:
        return ("deficient", len(miss))
    used = set()
    for T in cent:
        pool = [r for r in dead if r not in used] + sorted(used)
        bas = []
        for r in pool:
            vv = W.xpart(r)
            combo = {r}
            for pb, bv, bc in bas:
                if vv >> pb & 1:
                    vv ^= bv
                    combo ^= bc
            if vv:
                bas.append((vv.bit_length() - 1, vv, combo))
                bas.sort(key=lambda z: -z[0])
        v = T
        combo = set()
        for pb, bv, bc in bas:
            if v >> pb & 1:
                v ^= bv
                combo ^= bc
        assert v == 0
        if fresh_totals:
            host = W.helper("total")
            W.gate(e8.FULL, host, sorted(combo))
            W.ret.append(host)
            continue
        cands = sorted((r for r in combo if r not in used and r >= 2 * V), reverse=(host_order == "last"))
        host = cands[0]
        others = [r for r in sorted(combo) if r != host]
        if others:
            W.gate(e8.FULL, host, others)
        else:
            W.climb(host, e8.FULL)
        used.add(host)
        W.ret.append(host)
        assert W.xpart(host) == T
    rows = decoder_rows([W.xpart(q) for q in W.ret])
    # ---- phase B
    W.phase = "B"
    for t in range(V):
        C = dcellof[t]
        W.gate(G.cmask[C], V + t, [keeper[C]])
    qdel = {}
    for bi in range(len(G.blocks)):
        cb = G.comp[bi]
        us = [t for t in range(V) if G.blk[t] == cb]
        wires = [keeper[c] for c in G.cells if c in dualcells and G.cblk[c] == bi]
        inputs = [W.content[w] for w in wires]
        assert all(x & (x - 1) == 0 for x in inputs)
        pos = {x.bit_length() - 1: k for k, x in enumerate(inputs)}
        N = []
        for u in us:
            row = 0
            for l in e8.bits(need[u]):
                row |= 1 << pos[l]
            N.append(row)
        _, ops, perm = realise(N, random.Random(bi * 7 + (node_seed or 0)), tries=NODEOPT[0])
        for a, b in ops:
            W.gate(G.blocks[bi], wires[a], [wires[b]])
        for k, u in enumerate(us):
            qdel[u] = wires[perm[k]]
            assert W.xpart(qdel[u]) == need[u]
    for t in range(V):
        H = qhostD6[t]
        W.gate(G.D6[H], qdel[t], [E[H]])
        needer[(H, t)] = qdel[t]
    for t in range(V):
        srcs = [needer[(tuple(sorted((t, x))), t)] for x in G.phi[t] if x != t]
        W.gate(e8.HYP[t], V + t, srcs)
    word = W.build(rows)
    return W, word


def search(G, sol, seed=0, fresh=False, host_order="last", tries=400, node_seed=None):
    rng = random.Random(seed)
    pt = plan_thirds(G, sol, rng)
    if pt[0] == "failed":
        return ("rank", pt[1]), 0
    freeline, assign = pt
    zzleft = {}
    res = build(G, sol, zzleft=zzleft, freeline=freeline, thirdperm=assign, fresh_totals=fresh, host_order=host_order,
                verbose=True, node_seed=node_seed)
    k = 0
    while res[0] == "deficient" and k < tries:
        k += 1
        zzleft = {H: rng.randrange(2) for H in G.cells}
        res = build(G, sol, zzleft=zzleft, freeline=freeline, thirdperm=assign, fresh_totals=fresh,
                    host_order=host_order, verbose=(k % 50 == 0), node_seed=node_seed)
    return res, k


if __name__ == "__main__":
    G = Geom()
    sol = load_plan(sys.argv[1])
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    fresh = len(sys.argv) > 4 and sys.argv[4] == "fresh"
    host_order = sys.argv[5] if len(sys.argv) > 5 else "last"
    res, k = search(G, sol, seed=seed, fresh=fresh, host_order=host_order)
    print("tries", k)
    if res[0] in ("rank", "deficient"):
        print("FAILED", res)
        sys.exit(1)
    W, word = res
    print("R", word["R"], "gates D/A/B/C", len(word["D"]), len(word["A"]), len(word["B"]), len(word["C"]))
    save(word, sys.argv[2])
