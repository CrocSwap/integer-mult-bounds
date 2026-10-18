# Prepared by eumemic with substantial Anthropic Claude assistance; Apache-2.0.
"""Punctured L3 bit word: PR #543's R420 skeleton (L3) with the punctured-star unit of PR #545 (DreamingOfClouds):
nine E8 lines P are neither sources nor targets (v = 111), and the nine retained decoder totals are pseudo-targets of
frame rank 7 (decoder constant 63).

L3 forms the Q-deliveries in phase B (block nodes run after the targets' d-single reads), but a retained total must be
complete at the scatter, i.e. at the end of phase A.  The pseudo-target total tau_p of a punctured line p therefore
gets the Q-part a target would take from the block node (lines of the complementary block B) from B's free keepers,
rewritten in phase A by a mini-node at the block frame D4(B) before they become the third registers of p's (z,z) D6s:
  tau_p : 0 -> line l_p (reads the source of p's d-single line l_p, before its cell gate)
            -> D6[p, qhost(p)] (reads that D6's o1; qhost(p) still reads o1 in phase B)
            -> p^perp (reads p's needers at its two (z,z) D6s, one of which carries the rewritten free keeper)
Eligible p: both (z,z) cells of p's 4-frame contain p, and qhost(p) != l_p.  Lines a mini-node needs that no free
keeper or freed source of B holds are brought by extra carriers (a helper reading the source at its line frame in
phase A).  A freed source is the source sitting in the d-single cell of a punctured target (no reader in phase B).
Block nodes whose outputs outnumber their live inputs get junk wires (extra carriers of that block when available).
usage: python -I gen_p3.py data/plan-l3.json data/punct.json OUT.json.gz   (PLAN: the L3 plan of PR #543; PARAMS: the
punctured set, the plan_thirds seed, the receiver choices and the block-node search effort)"""
import itertools
import json
import os
import random
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "e8-bit-carrier-skeleton", "code", "skeleton"))   # PR #493 on main
sys.path.insert(0, HERE)
import e8  # noqa: E402
from geom import Geom  # noqa: E402
from gen import span_add  # noqa: E402
from planio import load_plan  # noqa: E402
from wordkit import save, solve_transform_lu  # noqa: E402
from nodeopt import realise  # noqa: E402
from pwordl import PWordL  # noqa: E402

V = e8.V
NODEOPT = [int(os.environ.get("NODEOPT", "2000"))]
GI = e8.GI


def rank_of(vecs):
    b = []
    for v in vecs:
        span_add(b, v)
    return len(b)


# ---- the L3 plan helpers (as in PR #543's gen_l3.py)
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
    zz = [H for H in G.cells if H not in hosted]
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


def decoder_rows(cvals, live):
    """for every live t: the subset of the totals whose XOR is (1 + B(t,.)) restricted to the live lines."""
    rows = {}
    for t in e8.bits(live):
        want = (((1 << V) - 1) ^ sum((int(GI[t, b]) & 1) << b for b in range(V))) & live
        found = None
        for k in range(len(cvals) + 1):
            for C in itertools.combinations(range(len(cvals)), k):
                m = 0
                for c in C:
                    m ^= cvals[c]
                if m == want:
                    found = list(C)
                    break
            if found is not None:
                break
        assert found is not None, ("decoder row not in the span of the totals", t)
        rows[t] = found
    return rows


def eligible(G, sol, dcellof, keepline, qhostD6, zz, p):
    f = G.phi[p]
    zzf = [H for H in zz if G.phi[H[0]] == f]
    Hp = qhostD6[p]
    lp = keepline[dcellof[p]]
    return len(zzf) == 2 and all(p in H for H in zzf) and lp not in Hp, zzf


def express(target, wires, content):
    """combination (list of wires) of the current contents whose XOR is target, or (None, residual)."""
    basis = []
    for w in wires:
        v, combo = content[w], {w}
        for pb, bv, bc in basis:
            if v >> pb & 1:
                v ^= bv
                combo ^= bc
        if v:
            basis.append((v.bit_length() - 1, v, combo))
            basis.sort(key=lambda z: -z[0])
    v, combo = target, set()
    for pb, bv, bc in basis:
        if v >> pb & 1:
            v ^= bv
            combo ^= bc
    return (sorted(combo), 0) if v == 0 else (None, v)


def build(G, sol, P, freeline, thirdperm, extras=None, node_seed=0, verbose=True, rcvsel=None):
    extras = extras or {}           # block -> sorted list of lines brought by extra carriers
    rcvsel = rcvsel or {}           # p -> 1, 2 or 3: which of p's two (z,z) D6s (bit 0: first, bit 1: second) have rcv p
    Pset = set(P)
    live = ((1 << V) - 1) & ~sum(1 << s for s in Pset)
    isl = lambda s: s not in Pset   # noqa: E731
    W = PWordL(live)
    dcellof, keepline, home, qhostD6, zz = derive(G, sol, freeline)
    dualcells = set(home.values())
    for p in P:
        ok, _ = eligible(G, sol, dcellof, keepline, qhostD6, zz, p)
        assert ok, ("not eligible", p)
    Ex = {H: (ex_part(G, sol, G.d6quads[H][0], H) ^ ex_part(G, sol, G.d6quads[H][1], H)) & live for H in G.cells}
    tauB = defaultdict(list)                       # block B -> punctured p whose Q-part comes from B
    for p in sorted(P):
        tauB[G.comp[G.blk[p]]].append(p)
    stats = dict(extra_carriers=0, junk_wires=0, rcv_flips=0)
    # ---- phase A: carriers, extra carriers, tau line reads (all at line frames, before any cell gate)
    branch = {}
    for s in range(V):
        for c in G.cells_of[s]:
            if c == home[s]:
                branch[(s, c)] = s if isl(s) else None
            else:
                k = W.helper("carrier" if isl(s) else "junk-carrier")
                if isl(s):
                    W.gate(1 << s, k, [s])
                branch[(s, c)] = k
    xcar = {}
    for B in sorted(extras):
        for s in extras[B]:
            k = W.helper("extra-carrier")
            W.gate(1 << s, k, [s])
            xcar[s] = k
            stats["extra_carriers"] += 1
    tau = {}
    for p in sorted(P):
        lp = keepline[dcellof[p]]
        tau[p] = W.helper("total")
        W.gate(1 << lp, tau[p], [lp])
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
        bl, bl2 = branch[(l, c)], branch[(l2, c)]
        assert bl2 is not None, ("delivery branch missing", c)
        if bl is not None and isl(l):
            W.gate(F, bl2, [bl])
        W.gate(F, e, [bl2])
        delivery[(c, qa)] = bl2
        delivery[(c, qb)] = e
        keeper[c] = bl                      # None: the punctured source of a home cell; else a register (maybe 0)
    # ---- quads
    qout = {}
    for q in range(len(G.quads)):
        U = G.quads[q]
        cs = G.qcells[q]
        wires = [delivery[(c, q)] for c in cs]
        inputs = [W.xpart(w) for w in wires]
        outs = [ex_part(G, sol, q, H) & live for H in G.qowners[q]]
        ops, assign = solve_transform_lu(inputs, outs)
        for a, b in ops:
            W.gate(U, wires[a], [wires[b]])
        for k, H in enumerate(G.qowners[q]):
            qout[(q, H)] = wires[assign[k]]
            assert W.xpart(qout[(q, H)]) == outs[k]
    # ---- D6 nodes: o1 = o1 + o2 (o2 dead)
    E = {}
    for H in G.cells:
        q1, q2 = G.d6quads[H]
        o1, o2 = qout[(q1, H)], qout[(q2, H)]
        W.gate(G.D6[H], o1, [o2])
        E[H] = o1
        assert W.xpart(o1) == Ex[H]
    # ---- receivers of the (z,z) D6s: every tau gets at least one rewritten free keeper
    rcv = dict(sol["rcv"])
    zzp = {}
    for p in sorted(P):
        f = G.phi[p]
        zzp[p] = sorted(H for H in zz if G.phi[H[0]] == f)
        if p in rcvsel:
            for i, H in enumerate(zzp[p]):
                want = p if (rcvsel[p] >> i) & 1 else (H[0] if H[1] == p else H[1])
                if rcv[H] != want:
                    rcv[H] = want
                    stats["rcv_flips"] += 1
        if not any(rcv[H] == p for H in zzp[p]):
            rcv[zzp[p][0]] = p
            stats["rcv_flips"] += 1
    # ---- free keepers (third registers of the (z,z) D6s) per complementary block
    fk_of = {}                          # zz D6 -> keeper register (free keeper of the complementary block)
    for bi in range(len(G.blocks)):
        cb = G.comp[bi]
        for H in sorted(H for H in zz if G.cblk[H] == cb):
            fk_of[H] = keeper[thirdperm[H]]
            assert fk_of[H] is not None
    # ---- phase-A mini-nodes at D4(B): rewrite one free keeper per tau to carry the tau's Q-part
    missing = {}
    for B in sorted(tauB):
        Bm = G.blocks[B]
        fks = sorted({fk_of[H] for H in zz if G.cblk[H] == G.comp[B]})
        freed = []
        for q in P:
            if G.blk[q] == B:
                s = keepline[dcellof[q]]
                if isl(s):
                    freed.append(s)                 # the source in q's d-single cell: no reader in phase B
        wires = fks + [xcar[s] for s in extras.get(B, [])] + freed
        plan_writes = []
        for p in tauB[B]:
            Hp = qhostD6[p]
            lp = keepline[dcellof[p]]
            Np = (e8.HYP[p] & live) ^ (1 << lp) ^ Ex[Hp]
            for H in zzp[p]:
                Np ^= Ex[H]
            mine = [H for H in zzp[p] if rcv[H] == p]
            des = fk_of[mine[0]]
            for H in mine[1:]:
                Np ^= W.xpart(fk_of[H])             # p's other received free keepers keep their own line
            plan_writes.append((p, des, Np))
        cont = {w: W.xpart(w) for w in wires}
        for p, des, Np in plan_writes:
            assert des in cont, ("designated keeper not among the block's free keepers", p)
            need_ = Np ^ cont[des]
            combo, res = express(need_, [w for w in wires if w != des], cont)
            if combo is None:
                missing.setdefault(B, set()).update(e8.bits(res))
                continue
            if combo:
                W.gate(Bm, des, combo)
                cont[des] ^= need_
            assert W.xpart(des) == Np or B in missing
    if missing:
        return ("missing", {B: sorted(v) for B, v in missing.items()})
    # ---- (z,z) thirds and needers (phase A)
    needer = {}
    for H in sorted(zz):
        k = fk_of[H]
        W.gate(G.D6[H], k, [E[H]])
        r = rcv[H]
        other = H[0] if r == H[1] else H[1]
        needer[(H, r)] = k
        needer[(H, other)] = E[H]
    for t in range(V):
        H = qhostD6[t]
        x = H[0] if H[1] == t else H[1]
        needer[(H, x)] = E[H]
    # ---- pseudo-target totals: D6[p, qhost(p)] then p^perp
    for p in sorted(P):
        Hp = qhostD6[p]
        W.gate(G.D6[Hp], tau[p], [E[Hp]])
        W.gate(e8.HYP[p], tau[p], [needer[(H, p)] for H in zzp[p]])
        assert W.xpart(tau[p]) == e8.HYP[p] & live, ("total", p)
        W.ret.append(tau[p])
    cvals = [W.xpart(q) for q in W.ret]
    rows = decoder_rows(cvals, live)
    # ---- Q needs of the live targets
    need = {}
    for t in e8.bits(live):
        C = dcellof[t]
        kp = keeper[C]
        acc = e8.HYP[t] & live
        if kp is not None and isl(keepline[C]):
            acc ^= W.xpart(kp)
        for x in G.phi[t]:
            if x == t:
                continue
            H = tuple(sorted((t, x)))
            acc ^= W.xpart(E[H]) if H == qhostD6[t] else W.xpart(needer[(H, t)])
        need[t] = acc
        assert acc & ~(G.blocks[G.comp[G.blk[t]]] & live) == 0, ("need outside the Q block", t)
    # ---- phase B: d-single reads
    W.phase = "B"
    for t in e8.bits(live):
        C = dcellof[t]
        kp = keeper[C]
        if kp is not None and isl(keepline[C]):
            W.gate(G.cmask[C], V + t, [kp])
    # ---- block nodes (phase B)
    qdel = {}
    for bi in range(len(G.blocks)):
        cb = G.comp[bi]
        us = [t for t in e8.bits(live) if G.blk[t] == cb]
        srcw = [keeper[c] for c in G.cells if c in dualcells and G.cblk[c] == bi and keeper[c] is not None
                and isl(keepline[c])]
        assert all(W.xpart(w) & (W.xpart(w) - 1) == 0 for w in srcw)
        pos = {W.xpart(w).bit_length() - 1: k for k, w in enumerate(srcw)}
        rowsN = []
        for u in us:
            r = 0
            for l in e8.bits(need[u]):
                r |= 1 << pos[l]
            rowsN.append(r)
        n0 = len(srcw)
        junk = []
        # junk directions: extra carriers of this block (x-part = a source line: wire + that source has x-part 0)
        avail = [xcar[s] for s in extras.get(bi, []) if s in [W.xpart(w).bit_length() - 1 for w in srcw]]
        bs = []
        allrows = []
        for r in rowsN:
            rr = r
            if not span_add(bs, rr):
                j = len(junk)
                if j < len(avail):
                    junk.append(avail[j])
                else:
                    junk.append(W.helper("junk-wire"))
                    stats["junk_wires"] += 1
                idx = n0 + j
                rr = r | (1 << idx)
                if junk[-1] in xcar.values():
                    s = W.xpart(junk[-1]).bit_length() - 1
                    rr ^= 1 << pos[s]                 # junk direction = extra carrier + its source: x-part 0
                assert span_add(bs, rr)
            allrows.append(rr)
        n = n0 + len(junk)
        for i in range(n):
            if len(allrows) == n:
                break
            if span_add(bs, 1 << i):
                allrows.append(1 << i)
        assert len(allrows) == n
        wires = srcw + junk
        _, ops, perm = realise(allrows, random.Random(bi * 7 + node_seed), tries=NODEOPT[0])
        for a, b in ops:
            W.gate(G.blocks[bi], wires[a], [wires[b]])
        for k, u in enumerate(us):
            qdel[u] = wires[perm[k]]
            assert W.xpart(qdel[u]) == need[u], ("qdel", bi, u)
    for t in e8.bits(live):
        H = qhostD6[t]
        W.gate(G.D6[H], qdel[t], [E[H]])
        needer[(H, t)] = qdel[t]
    for t in e8.bits(live):
        srcs = [needer[(tuple(sorted((t, x))), t)] for x in G.phi[t] if x != t]
        W.gate(e8.HYP[t], V + t, srcs)
    word = W.build(rows)
    word["stats"] = stats
    if verbose:
        print("R", word["R"], "v", word["v"], "gates D/A/B/C", len(word["D"]), len(word["A"]), len(word["B"]),
              len(word["C"]), stats)
    return W, word


def make(plan, P, seed=0, node_seed=0, rcvsel=None):
    G = Geom()
    sol = load_plan(plan)
    pt = plan_thirds(G, sol, random.Random(seed))
    assert pt[0] != "failed"
    freeline, assign = pt
    extras = {}
    for _ in range(20):
        res = build(G, sol, P, freeline, assign, extras=extras, node_seed=node_seed, verbose=False, rcvsel=rcvsel)
        if res[0] == "missing":
            for B, ls in res[1].items():
                extras[B] = sorted(set(extras.get(B, [])) | set(ls))
            continue
        break
    return build(G, sol, P, freeline, assign, extras=extras, node_seed=node_seed, rcvsel=rcvsel), extras


if __name__ == "__main__":
    # usage: gen_p3.py PLAN PARAMS.json OUT.json.gz ; PARAMS: punctured set P, plan_thirds seed, receiver choices, NODEOPT
    prm = json.load(open(sys.argv[2]))
    NODEOPT[0] = prm["nodeopt"]
    sel = {int(k): v for k, v in prm["receivers"].items()}
    (W, word), extras = make(sys.argv[1], sorted(prm["punctured"]), seed=prm["thirds_seed"], rcvsel=sel)
    print("extra carriers per block", {B: len(v) for B, v in sorted(extras.items())})
    save(word, sys.argv[3])
