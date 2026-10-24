"""Single-gate frame retiming of a bitE8/1 word (our implementation of the idea of PR #389, ai-nanachi).

Every A, B and C gate may move to the join of its registers' previous frames (the lowest legal frame) or to the
root-spanned meet of their next frames (the highest legal frame), whichever lowers the integer step cost
sum over its registers of cost(rank in) + cost(rank out), cost(r) = r ln(M/r) (ecost.py; M = 64 by default, the
width of the compressed nine-stage layout). Sweeps alternate direction until no gate moves. D gates (frame 0), the
targets at frame 0 at the scatter, the retained totals at the full frame, start and final frames are pinned.
Requires the PR #370 producer modules on sys.path with E8COORD=ham (see regen.py).
Prepared by eumemic with Anthropic Claude assistance; Apache-2.0."""
import os
from collections import defaultdict

assert os.environ.get("E8COORD") == "ham", "set E8COORD=ham before importing (see regen.py)"
import frames as Fm  # noqa: E402  (PR #370 producer: exact root-spanned closure over Q)
from ecost import table  # noqa: E402


def _bits(mask):
    out = []
    while mask:
        b = mask & -mask
        out.append(b.bit_length() - 1)
        mask ^= b
    return out


def retime(w, sweeps=6, M=64):
    v = w["v"]
    rc = table(M, M)
    frames = [sum(1 << s for s in f) for f in w["frames"]]
    FULL = (1 << v) - 1
    dcache = {}

    def dim(mask):
        if mask not in dcache:
            dcache[mask] = Fm.closure(mask)[1] if mask else 0
        return dcache[mask]

    nodes = []   # dict(mask, regs, fixed, phase, gate)
    for ph in ("D", "A"):
        for g in w[ph]:
            nodes.append(dict(mask=frames[g[0]], regs=[g[1]] + g[2], fixed=(ph == "D"), phase=ph, gate=g))
    for q in w["ret"]:
        nodes.append(dict(mask=FULL, regs=[q], fixed=True, phase="pin", gate=None))
    for t in range(v):
        nodes.append(dict(mask=0, regs=[v + t], fixed=True, phase="pin", gate=None))
    for ph in ("B", "C"):
        for g in w[ph]:
            nodes.append(dict(mask=frames[g[0]], regs=[g[1]] + g[2], fixed=False, phase=ph, gate=g))
    byreg = defaultdict(list)
    for i, n in enumerate(nodes):
        for r in n["regs"]:
            byreg[r].append(i)
    prev, nxt = {}, {}
    for r, ids in byreg.items():
        for p, i in enumerate(ids):
            prev[i, r] = ids[p - 1] if p else ("start", r)
            nxt[i, r] = ids[p + 1] if p + 1 < len(ids) else ("final", r)

    def frame_of(key):
        if isinstance(key, int):
            return nodes[key]["mask"]
        kind, r = key
        return frames[w[kind][r]]

    def node_cost(i, mask):
        c = 0
        dm = dim(mask)
        for r in nodes[i]["regs"]:
            c += rc[dm - dim(frame_of(prev[i, r]))] + rc[dim(frame_of(nxt[i, r])) - dm]
        return c

    moved_total = 0
    for sweep in range(sweeps):
        moved = 0
        order = [i for i, n in enumerate(nodes) if not n["fixed"]]
        if sweep % 2:
            order.reverse()
        for i in order:
            lo, hi = 0, FULL
            for r in nodes[i]["regs"]:
                lo |= frame_of(prev[i, r])
                hi &= frame_of(nxt[i, r])
            lo = Fm.closure(lo)[0] if lo else 0
            hi = Fm.closure(hi)[0] if hi else 0
            if lo & ~hi:
                continue
            old = nodes[i]["mask"]
            best = min([old, lo, hi], key=lambda m_: node_cost(i, m_))   # ties keep the old frame
            if node_cost(i, best) < node_cost(i, old):
                nodes[i]["mask"] = best
                moved += 1
        moved_total += moved
        if not moved:
            break
    fid = {m: i for i, m in enumerate(frames)}

    def frame_id(mask):
        if mask not in fid:
            fid[mask] = len(frames)
            frames.append(mask)
        return fid[mask]

    out = {ph: [] for ph in "DABC"}
    for n in nodes:
        if n["phase"] == "pin":
            continue
        g = n["gate"]
        out[n["phase"]].append([frame_id(n["mask"]), g[1], list(g[2])])
    cert = dict(w)
    cert.update(frames=[_bits(m) for m in frames], D=out["D"], A=out["A"], B=out["B"], C=out["C"])
    return cert, moved_total
