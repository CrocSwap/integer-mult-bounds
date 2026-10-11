"""Helper-slot reuse by elimination of dead registers (bitE8/1 words).

A helper is dead after its last phase-A/B gate. It still holds a leftover x-content (an F2 combination of source
lines) at its death frame. Before the birth gate of a later helper whose first frame is fb, look among the dead slots
whose current frame lies inside fb for a linear relation of their x-contents over F2:
    content(r0) = XOR_{q in S} content(q).
Emit the gate  r0 += S  at G = the join of the current frames of r0 and S (G lies inside fb). Afterwards r0 holds no
x-content (only helper dirt, which the rebuilt compensation D and cleanup C account for), so r0 hosts the new helper.
The eliminators S move to G and stay dead there. The relation is chosen by Gaussian elimination over F2 on the
candidates sorted by frame dimension, then replaced by the cheapest relation with |S| <= 3 under the integer step costs
of ecost.py (extra climbing of r0 and of the eliminators), when one exists.
The 9 retained totals (born at the full frame) also take dead slots: the leftover x-lines of the chosen slot are read
from the sources at the full frame, which zeroes its x-content.
D (dirt compensation at frame 0) and C (cleanup at the full frame) are rebuilt exactly as PR #370's fullword.py does.
Same idea as PR #376's helper-lifetime reuse (applecrusher), generalised from aliasing to linear relations.
Requires the PR #370 producer modules on sys.path with E8COORD=ham (see regen.py).
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import os

assert os.environ.get("E8COORD") == "ham", "set E8COORD=ham before importing (see regen.py)"
import e8lib as E  # noqa: E402  (PR #370 producer, unchanged)
import frames as Fm  # noqa: E402  (PR #370 producer: exact root-spanned closure over Q)
from ecost import table  # noqa: E402

RC = table(40, 8)          # step cost r ln(40/r) of the five-stage ledger, as integers
MAXS_PAIRS = 60            # pair/triple relations are searched when at most this many dead slots fit


def _step(a, b):
    return RC[b - a] if b > a else 0


def _dim(mask):
    return Fm.closure(mask)[1] if mask else 0


def _bits(mask):
    out = []
    while mask:
        b = mask & -mask
        out.append(b.bit_length() - 1)
        mask ^= b
    return out


def sparse_relation(cands, dead, fb):
    """cheapest (r0, S) with content(r0) = XOR content(S), |S| <= 3, scored by the extra climbing of the
    eliminators (death frame -> G -> full instead of death frame -> full) and of r0 (death frame -> G -> birth
    frame instead of 0 -> birth frame and death frame -> full); None if no such relation fits inside fb"""
    best = None
    single = {}
    for q in cands:
        single.setdefault(dead[q][0], []).append(q)
    pairs = {}
    if len(cands) <= MAXS_PAIRS:
        for i, a in enumerate(cands):
            for b in cands[i + 1:]:
                pairs.setdefault(dead[a][0] ^ dead[b][0], []).append((a, b))
    dfb = _dim(fb)

    def score(r0, S):
        G = dead[r0][1]
        for q in S:
            G |= dead[q][1]
        G, dg = Fm.closure(G) if G else (0, 0)
        if G & ~fb:
            return None
        d0 = _dim(dead[r0][1])
        c = _step(d0, dg) + _step(dg, dfb) - _step(d0, 8) - _step(0, dfb)
        for q in S:
            if dead[q][1] != G:
                dq = _dim(dead[q][1])
                c += _step(dq, dg) + _step(dg, 8) - _step(dq, 8)
        return c

    for r0 in cands:
        x = dead[r0][0]
        opts = []
        if x == 0:
            opts.append([])
        for q in single.get(x, []):
            if q != r0:
                opts.append([q])
        for a, b in pairs.get(x, []):
            if r0 not in (a, b):
                opts.append([a, b])
        if len(cands) <= MAXS_PAIRS:
            for a in cands:
                if a == r0:
                    continue
                for b, c_ in pairs.get(x ^ dead[a][0], []):
                    if r0 not in (b, c_) and a not in (b, c_):
                        opts.append([a, b, c_])
                        break
        for S in opts:
            sc = score(r0, S)
            if sc is not None and (best is None or sc < best[0]):
                best = (sc, r0, S)
    return None if best is None else (best[1], best[2])


def reuse(w, maxr=10 ** 9):
    """returns (new word, dict(helpers=..., totals=...) reuse counts); w is a bitE8/1 word from PR #370's fullword.build (helpers start at
    frame 0 and end at the full frame)"""
    v, R = w["v"], w["R"]
    assert w["format"] == "bitE8/1" and w["coords"] == "ham" and w["lines"] == [list(r) for r in E.LINES]
    assert all(not w["frames"][w["start"][r]] for r in range(2 * v, 2 * v + R))
    frames = [sum(1 << s for s in f) for f in w["frames"]]
    fid = {m: i for i, m in enumerate(frames)}
    XM = (1 << v) - 1

    def frame_id(mask):
        if mask not in fid:
            fid[mask] = len(frames)
            frames.append(mask)
        return fid[mask]

    nA = len(w["A"])
    gates = [list(g) for g in w["A"]] + [list(g) for g in w["B"]]
    first, last = {}, {}
    for k, (f, d, srcs) in enumerate(gates):
        for r in [d] + srcs:
            if r >= 2 * v:
                first.setdefault(r, k)
                last[r] = k
    ret = set(w["ret"])
    val = [1 << s for s in range(v)] + [0] * (v + R)    # x-content only (helpers never read targets)
    cont_at = {}
    for k, (f, d, srcs) in enumerate(gates):
        for s in srcs:
            val[d] ^= val[s]
        for r in [d] + srcs:
            if r >= 2 * v and last.get(r) == k:
                cont_at[r] = (val[r] & XM, frames[f])
    births = sorted((first[r], r) for r in range(2 * v, 2 * v + R) if r in first and r not in ret)
    deaths = sorted((last[r], r) for r in cont_at if r not in ret)
    dead = {}          # physical slot -> [x-content, current frame mask, death gate index]
    rename = {}        # logical register born later -> physical slot it reuses
    insert_before = {}
    di = 0
    nre = 0

    def bury(upto):
        nonlocal di
        while di < len(deaths) and deaths[di][0] < upto:
            k, r = deaths[di]
            di += 1
            x, f = cont_at[r]
            dead[rename.get(r, r)] = [x, f, k]

    for kb, rb in births:
        bury(kb)
        if nre >= maxr:
            continue
        fb = frames[gates[kb][0]]
        cands = sorted((_dim(fm), p) for p, (x, fm, k) in dead.items() if (fm & ~fb) == 0)
        if not cands:
            continue
        basis = []     # (vector, set of slots) with distinct leading bits
        found = None
        for dm, p in cands:
            y, comb = dead[p][0], {p}
            for bv, bs in basis:
                if y >> (bv.bit_length() - 1) & 1:
                    y ^= bv
                    comb ^= bs
            if y == 0:
                found = (p, sorted(q for q in comb if q != p))
                break
            basis.append((y, comb))
            basis.sort(key=lambda z: -z[0])
        if found is None:
            continue
        found = sparse_relation([p for _, p in cands], dead, fb) or found
        r0, S = found
        G = dead[r0][1]
        for q in S:
            G |= dead[q][1]
        G = Fm.closure(G)[0] if G else 0
        assert G & ~fb == 0
        x = dead[r0][0]
        for q in S:
            x ^= dead[q][0]
        assert x == 0, "not a relation"
        if S:
            insert_before.setdefault(kb, []).append([frame_id(G), r0, list(S), "helper"])
        for q in S:
            dead[q][1] = G
        assert dead[r0][2] < kb
        del dead[r0]
        rename[rb] = r0
        nre += 1
    # retained totals (born at the full frame) reuse dead slots: undo by reading the slot's x-lines at the full frame
    FULLM = (1 << v) - 1
    ntot = 0
    for q in w["ret"]:
        kq = first[q]
        bury(kq)
        free = [p for p in dead if dead[p][2] < kq]      # only slots already dead at the total's birth
        if not free:
            continue
        r0 = min(free, key=lambda p: (bin(dead[p][0]).count("1"), p))
        xs = _bits(dead[r0][0])
        if xs:
            insert_before.setdefault(kq, []).append([frame_id(FULLM), r0, xs, "total"])
        del dead[r0]
        rename[q] = r0
        ntot += 1
    out, kinds = [], []
    for k, g in enumerate(gates):
        for f, d, srcs, kind in insert_before.get(k, []):
            out.append([f, d, srcs])
            kinds.append(kind)
        f, d, srcs = g
        out.append([f, rename.get(d, d), [rename.get(s, s) for s in srcs]])
        kinds.append(None)
    nA2 = nA + sum(len(insert_before.get(k, [])) for k in range(nA))
    A2, B2 = out[:nA2], out[nA2:]
    # ledger of the inserted elimination gates: (phase, index in that phase, kind); retime.py keeps gate positions
    ledger = [["A", i, kd] if i < nA2 else ["B", i - nA2, kd] for i, kd in enumerate(kinds) if kd]
    alive = sorted(set(range(2 * v, 2 * v + R)) - set(rename))
    newid = {r: 2 * v + i for i, r in enumerate(alive)}
    for i in range(2 * v):
        newid[i] = i
    R2 = len(alive)

    def ren(gl):
        return [[f, newid[d], [newid[s] for s in srcs]] for f, d, srcs in gl]

    A2, B2 = ren(A2), ren(B2)
    ret2 = [newid[rename.get(q, q)] for q in w["ret"]]
    # dirt compensation and cleanup, rebuilt as in PR #370's fullword.build
    nreg = 2 * v + R2
    dv = [0] * nreg
    for r in range(2 * v, nreg):
        dv[r] = 1 << (r - 2 * v)
    for f, d, srcs in A2:
        for s in srcs:
            dv[d] ^= dv[s]
    cdirt = [dv[q] for q in ret2]
    for t in range(v):
        for k in w["scatter"][t]:
            dv[v + t] ^= cdirt[k]
    for f, d, srcs in B2:
        for s in srcs:
            dv[d] ^= dv[s]
    zero, full = frame_id(0), frame_id(FULLM)
    D = []
    for t in range(v):
        srcs = [2 * v + b for b in _bits(dv[v + t])]
        if srcs:
            D.append([zero, v + t, srcs])
    Cl = [[full, d, srcs] for f, d, srcs in reversed(A2 + B2) if d >= 2 * v]
    start = w["start"][:2 * v] + [w["start"][2 * v]] * R2
    final = w["final"][:2 * v] + [w["final"][2 * v]] * R2
    cert = dict(w)
    cert.update(R=R2, frames=[_bits(m) for m in frames], start=start, final=final, ret=ret2, D=D, A=A2, B=B2, C=Cl)
    return cert, dict(helpers=nre, totals=ntot, eliminations=ledger)
