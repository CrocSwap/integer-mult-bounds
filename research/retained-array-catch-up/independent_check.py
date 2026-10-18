#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent second method for the retained-array catch-up package.

Shares no code with verify.py and does not import ceiling.py.

 A. Frames as explicit coordinate sets.  The base (non-replica) template schedule, read from a
    byte-identical copy (same sha256) of the base member in the PR2346-pinned #1042 archive, is
    replayed with each pair's applied coordinates stored as a Python set: a local call applies its
    stage's eight coordinates; an idle sweep applies rank/8 stage blocks taken from the idle child
    RANKS (its from/to level fields are only cross-checked, not used).  A record snapshots its
    family's set; catch-up = |consumer set - record set| x rows (the PR1664 nested-frame distance).
    Recomputes PR2540, INIT64, d_A, the all-initial variant at three consumer timings (end, the
    earliest timing the observed Y_(k,U) fields allow under final-value reads, and P_early: each bank
    right after its last local call), the zero-advance window and the lagging-record example.  Theorem B floors are recomputed by explicit
    enumeration of the per-bank splits of the 62 rows (own-bank premise), by nearest-consumer
    delivery (count only) and by a direct cut loop (one consumer level).
 B. Hosted heights per family, in all 16 replicas.  The selected #1094 hosted template is replayed
    family by family (local call +8, idle child +remaining rank, pooled slot +width at its own
    time), under both tie conventions for slots and events at equal times.  Every capture, consumer
    and read instant used by the routes must see one uniform height 8 x (level + 1) on all 224
    families of its pair, in every replica; the zero-advance window is reported per replica.
 C. Moment arithmetic with decimal.Decimal at 80 digits (ln/exp from the decimal module):
    the no-saving threshold, the #1166 break-evens 573 / 71 against PR2474, and the route verdicts.
 D. Exact frame model by a different algorithm: Dijkstra over per-level reduced echelon bases
    (membership by Gaussian elimination, not span enumeration), with the meeting-level formula
    computed from ranks by elimination, on the complete GF(2)^2 / 4-level record-partner domain.

Run from the repository root:  python3 -I -B research/retained-array-catch-up/independent_check.py
Prepared by thakrarsagar with substantial AI assistance from Claude (Anthropic, Claude Opus 5.5).
"""
import gzip
import hashlib
import heapq
import io
import itertools
import json
import sys
import tarfile
from decimal import Decimal as D, getcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ("research/community-frontier1042-audit/selected-replay.tar.gz",
           "22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754")
MEMBER = ("t16/global/base/split-centres/GLOBAL-TEMPLATE.json.gz",
          "a179dad87651aba340a5a8ddbcd86a8e757cad87b8a1f8bad48106fbecd38518")
HOSTED = ("research/community-frontier1094-audit/selected-replay.tar.gz",
          "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
          "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz",
          "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760")
PR2540_PROOF = ("research/qq16-complete-native-decoder/PROOF.md",
                "09d587f1d6bc250e90e29fa8751a40f45be79f1a8a56af0b645c144cefaefa46")


class Fail(Exception):
    pass


def need(ok, message):
    if not ok:
        raise Fail(message)


# ------------------------------------------------------------------ A. coordinate sets
def template():
    raw = (ROOT / ARCHIVE[0]).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == ARCHIVE[1], "archive pin")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
        member = tar.getmember(MEMBER[0])
        data = tar.extractfile(member).read()
    need(hashlib.sha256(data).hexdigest() == MEMBER[1], "template member pin")
    return json.loads(gzip.decompress(data))


def pr2540_frames():
    text = (ROOT / PR2540_PROOF[0]).read_text(encoding="utf-8")
    need(hashlib.sha256(text.encode("utf-8")).hexdigest() == PR2540_PROOF[1], "PR2540 proof pin")
    need("F_L=product_(j=0,...,8)" in text and "U1=<e0,...,e16>" in text, "PR2540 frame statements")
    f_l = set(range(0, 8 + 1))          # axes e0..e8
    f_u1 = set(range(0, 16 + 1))        # axes e0..e16
    need(f_l < f_u1, "nested frames")
    return len(f_u1 - f_l)


def coordinate_replay(t):
    stage_pair = {}
    for e in t["recipe"]:
        if e["kind"] == "local":
            stage_pair[e["stage"]] = e["pair"]
    rank = {c["child"]: c["rank"] for c in t["idle_children"] if c["port"] == 0}
    applied = {p: set() for p in range(4)}           # applied (stage block, axis) coordinates
    next_block = {p: 0 for p in range(4)}            # stage blocks are applied in order 0..8
    snapshots = [("entry", {p: frozenset(s) for p, s in applied.items()})]
    for e in t["execution_schedule"][:30]:
        kind = e["kind"]
        if kind == "local_cover_sweep":
            p = stage_pair[e["stage"]]
            need(next_block[p] == e["stage"], "local call applies the next stage block")
            applied[p] |= {(e["stage"], a) for a in range(8)}
            next_block[p] += 1
        elif kind == "idle_cover_sweep":
            p = e["pair"]
            ranks = [rank.get(c, 0) for c in e["child_indices"]]
            need(ranks[0] == ranks[1] and ranks[0] % 8 == 0, "idle child pair of equal multiple-of-8 rank")
            blocks = ranks[0] // 8
            need(e["from_level"] + 1 == next_block[p] and e["to_level"] == next_block[p] - 1 + blocks,
                 "declared idle levels agree with rank/8 blocks")
            for b in range(next_block[p], next_block[p] + blocks):
                applied[p] |= {(b, a) for a in range(8)}
            next_block[p] += blocks
        snapshots.append((kind, {p: frozenset(s) for p, s in applied.items()}))
    need(all(len(s) == 72 for s in applied.values()), "every pair ends with 72 applied coordinates")
    return snapshots, stage_pair


def law(snapshots, stage_pair, t):
    sched = t["execution_schedule"][:30]
    end = snapshots[-1][1]
    before = lambda i: snapshots[i][1]           # state before schedule entry i
    after = lambda i: snapshots[i + 1][1]
    gap = lambda rec, cons, p: len(cons[p] - rec[p])
    local_idx = {k: [i for i, e in enumerate(sched) if e["kind"] == "local_cover_sweep"
                     and stage_pair[e["stage"]] == k] for k in range(4)}
    out = {"PR2540": 16 * gap(after(0), after(1), 0)}
    out["INIT"] = [16 * gap(before(local_idx[k][0]), end, k) for k in range(4)]
    out["dA"] = [8 * gap(after([i for i in local_idx[k] if sched[i]["stage"] % 2][0]), end, k) for k in range(3)]
    last = {k: after(local_idx[k][-1]) for k in range(4)}
    init_early = [gap(before(local_idx[k][0]), last[k], k) for k in range(4)]
    da_early = [gap(after([i for i in local_idx[k] if sched[i]["stage"] % 2][0]), last[k], k) for k in range(3)]
    out["early"] = 16 * sum(init_early) + 8 * sum(da_early)
    # All-initial variant: bank k reads the initial X_(k+1,U); pair k+1's set may be taken at any
    # snapshot before its first call (no bridge writes X_(k+1,U) before it).
    reads_final, reads_early = [], []
    for k in range(3):
        first = local_idx[k + 1][0]
        need(not any(e["kind"] == "bridge" and e["dst"] == k + 1 for e in sched[:first]), "X_(k+1,U) initial")
        held = [snapshots[i][1][k + 1] for i in range(first + 1)]
        reads_final.append(len(end[k] - before(first)[k + 1]))          # coordinates per row
        reads_early.append(min(len(last[k][k] ^ h) for h in held))
    out["allinit_final"] = 16 * sum(len(end[k] - before(local_idx[k][0])[k]) for k in range(4)) + 8 * sum(reads_final)
    out["allinit_early"] = 16 * sum(init_early) + 8 * sum(reads_early)
    out["allinit_reads"] = (reads_final, reads_early)
    # P_Y: bank k's observed field Y_(k,U) = -final X_(k,U) is final only after the last write of X_(k,U)
    # (local calls on pair k overwrite it; bridges with dst = k add into it).
    last_write = [max(i for i, e in enumerate(sched)
                      if (e["kind"] == "local_cover_sweep" and stage_pair[e["stage"]] == k)
                      or (e["kind"] == "bridge" and e["dst"] == k)) for k in range(4)]
    out["last_write"] = last_write
    ycons = {k: after(last_write[k]) for k in range(4)}
    out["y_levels"] = [len(ycons[k][k]) // 8 - 1 for k in range(4)]
    init_rec = {k: before(local_idx[k][0]) for k in range(4)}
    da_rec = {k: after([i for i in local_idx[k] if sched[i]["stage"] % 2][0]) for k in range(3)}
    out["y_mass"] = (16 * sum(gap(init_rec[k], ycons[k], k) for k in range(4))
                     + 8 * sum(gap(da_rec[k], ycons[k], k) for k in range(3)))
    reads_y = []
    for k in range(3):
        held = [snapshots[i][1][k + 1] for i in range(local_idx[k + 1][0] + 1)]
        reads_y.append(min(len(ycons[k][k] ^ h) for h in held))
    out["allinit_y"] = 16 * sum(gap(init_rec[k], ycons[k], k) for k in range(4)) + 8 * sum(reads_y)
    # Theorem B floors. Rows: (bank, count, list of admissible record coordinate sets of the source pair).
    original = [(k, 16, [init_rec[k][k]]) for k in range(4)] + [(k, 8, [da_rec[k][k]]) for k in range(3)]
    variant = [(k, 16, [init_rec[k][k]]) for k in range(4)] +               [(k, 8, [snapshots[i][1][k + 1] for i in range(local_idx[k + 1][0] + 1)]) for k in range(3)]
    timings = {"final": {k: end[k] for k in range(4)}, "Y": {k: ycons[k][k] for k in range(4)},
               "early": {k: last[k][k] for k in range(4)}}
    out["thmB"] = {(name, label): thm_b(rows, cons) for name, cons in timings.items()
                   for label, rows in (("original", original), ("all_initial", variant))}
    # Lagging example: the last write of X_(0,U) (local calls on pair 0, bridges into pair 0).
    out["x0_last_write"] = max(i for i, e in enumerate(sched)
                               if (e["kind"] == "local_cover_sweep" and stage_pair[e["stage"]] == 0)
                               or (e["kind"] == "bridge" and e["dst"] == 0))
    out["x0_levels_after_13"] = len(end[0] - after(13)[0]) // 8
    touch = min(i for i, e in enumerate(sched) if
                (e["kind"] == "local_cover_sweep" and stage_pair[e["stage"]] == 3) or
                (e["kind"] == "idle_cover_sweep" and e["pair"] == 3 and e["to_level"] > e["from_level"]) or
                (e["kind"] == "bridge" and 3 in (e["src"], e["dst"])))
    out["zero_witness"] = (gap(snapshots[0][1], before(touch), 3),
                           sum(1 for e in sched[:touch] if e["kind"] == "local_cover_sweep"))
    return out


def thm_b(rows, cons, need_rows=62):
    """(own-bank floor, count-only delivery, one-level cut sum or None) from coordinate sets."""
    own_costs = {}
    for bank, n, recs in rows:
        below = [len(cons[bank] - r) for r in recs if r <= cons[bank]]
        need(below, "own-bank capture below its consumer")
        own_costs.setdefault(bank, []).extend([min(below)] * n)
    prefix = {b: [sum(sorted(c)[:i]) for i in range(len(c) + 1)] for b, c in own_costs.items()}
    banks = sorted(prefix)
    own = min(sum(prefix[b][i] for b, i in zip(banks, split))
              for split in itertools.product(*[range(len(prefix[b])) for b in banks]) if sum(split) == need_rows)
    free = sorted(min(len(c ^ r) for c in cons.values() for r in recs) for _, n, recs in rows for _ in range(n))
    count_only = sum(free[:need_rows])
    one_level = None
    if len({frozenset(c) for c in cons.values()}) == 1:
        top = len(next(iter(cons.values())))
        heights = [(n, max(len(r) for r in recs)) for _, n, recs in rows]
        one_level = sum(max(0, need_rows - sum(n for n, h in heights if h >= j)) for j in range(1, top + 1))
    return own, count_only, one_level


# ------------------------------------------------------------------ B. Decimal moments
getcontext().prec = 80
M, W = D(73), D(896) / D(9)
R_IDLE = 51


def child(r, a):
    return (D(r) / M) ** (1 - a) if r else D(0)


def relax(local, extra_rank8, extra_units, a):
    """Per-call moment: QQ16 5F+4B words, extra mass, idle remainder as rank-51 mass."""
    total = 72 * W + extra_units
    mass = sum(D(r) * n for r, n in local.items()) + 8 * extra_rank8
    idle = total - mass
    need(idle >= 0, "coverage law")
    s = sum(n * child(r, a) for r, n in local.items()) + extra_rank8 * child(8, a) + idle / R_IDLE * child(R_IDLE, a)
    return s / W


def qq16_words():
    core = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}
    return {r: (5 * (n + (8 if r == 1 else 0)) + 4 * (n + (24 if r == 1 else 0))) / D(9) for r, n in core.items()}


def gains(units, pricing, kappa):
    a = kappa / (1 - kappa)
    local = qq16_words()
    per_call = D(units) / D(9)
    value = relax(local, per_call / 8 if pricing == "rank8" else D(0), per_call, a)
    return value < 1, abs(value - 1)


def decimal_checks():
    pr2474 = D("0.001703676387993676")
    out = {}
    for pricing, step, expect in (("idle", 1, 573), ("rank8", 8, 71)):
        ok_lo, m_lo = gains(expect * step, pricing, pr2474)
        ok_hi, m_hi = gains((expect + 1) * step, pricing, pr2474)
        need(ok_lo and not ok_hi, "break-even %s = %d" % (pricing, expect))
        need(min(m_lo, m_hi) > D(10) ** -40, "decision margin far above precision")
        out["breakeven_" + pricing] = expect
    # No positive saving, exactly (rationals): at a = 0 every child costs r/m, so the moment is
    # total/(m w) = (72 w + u/9)/(73 w), which is >= 1 iff u >= 9 w = 896 units per replica; and
    # every child cost (r/m)^(1-a) >= r/m for a >= 0, so the moment only grows with a.
    from fractions import Fraction as F
    w = F(896, 9)
    need(all(((72 * w + F(u, 9)) / (73 * w) >= 1) == (u >= 896) for u in range(0, 2000)), "896 threshold")
    local = qq16_words()
    for units in (3648, 3712, 2496, 1344, 960, 3456, 2304, 1152, 1952, 1824, 1216):
        need(relax(local, 0, D(units) / 9, D(0)) > 1, "no saving at %d" % units)
    sel = D("0.001672660197076918")
    a_sel = sel / (1 - sel)
    for units in (800, 608):          # own-bank P_early floors; 608 is also the count-only P_Y original
        need(relax(local, 0, D(units) / 9, D(0)) < 1 and relax(local, 0, D(units) / 9, a_sel) > 1,
             "%d units: positive ceiling, but cannot reach the selected kappa (Decimal)" % units)
    for units in (544, 112, 0):       # count-only deliveries: the count alone does not decide
        need(relax(local, 0, D(units) / 9, a_sel) < 1, "%d units still beat the selected kappa" % units)
    ok, _ = gains(464, "idle", D("0.00221"))
    need(ok, "S-priced 464 array-calls keeps a ceiling above 0.00221 (the price gate's read-invoice value)")
    out["threshold"] = 896
    return out


# ------------------------------------------------------------------ C. echelon Dijkstra
P = 2


def pivot(row):
    return next(i for i, x in enumerate(row) if x)


def reduce(basis, v):
    """Reduce v by a fully reduced GF(2) echelon basis (distinct pivots, zero pivot columns elsewhere)."""
    v = list(v)
    for row in basis:
        if v[pivot(row)]:
            v = [(x + y) % P for x, y in zip(v, row)]
    return tuple(v)


def insert(basis, v):
    r = reduce(basis, v)
    if not any(r):
        return basis
    k = pivot(r)
    rows = [tuple((x + y) % P for x, y in zip(row, r)) if row[k] else row for row in basis]
    return tuple(sorted(rows + [r], key=pivot))


def rank(vectors):
    b = ()
    for v in vectors:
        b = insert(b, v)
    return len(b)


def members(basis):
    out = set()
    for coeffs in itertools.product(range(P), repeat=len(basis)):
        v = tuple(0 for _ in range(2))
        for c, row in zip(coeffs, basis):
            v = tuple((x + c * y) % P for x, y in zip(v, row))
        out.add(v)
    return out


def dijkstra(entry, demand, H):
    start = [()] * (H + 1)
    for v, h in entry:
        start[h] = insert(start[h], v)
    start = tuple(start)
    best = {start: 0}
    heap = [(0, start)]
    while heap:
        d, s = heapq.heappop(heap)
        if d > best[s]:
            continue
        if all(not any(reduce(s[h], v)) for v, h in demand):
            return d
        for h in range(H + 1):
            for v in members(s[h]):
                if not any(v):
                    continue
                for g in (h - 1, h + 1):
                    if 0 <= g <= H and any(reduce(s[g], v)):
                        n = list(s)
                        n[g] = insert(s[g], v)
                        n = tuple(n)
                        if d + 1 < best.get(n, 10 ** 9):
                            best[n] = d + 1
                            heapq.heappush(heap, (d + 1, n))
    need(False, "unreachable")


def frame_checks():
    vecs = [v for v in itertools.product(range(P), repeat=2) if any(v)]
    spaces = [()] + [(v,) for v in vecs] + [tuple(vecs[:2])]
    count = 0
    H = 3
    for R in spaces:
        for Pp in spaces:
            if rank(list(R) + list(Pp)) != len(R) + len(Pp):
                continue
            b = ()
            for v in list(R) + list(Pp):
                b = insert(b, v)
            whole = members(b)
            for O in spaces:
                if not O or not all(v in whole for v in O):
                    continue
                rho_r = rank(list(Pp) + list(O)) - rank(list(Pp))
                rho_p = rank(list(R) + list(O)) - rank(list(R))
                rho_o = rank(list(O))
                for hr, hp, hc in itertools.product(range(H + 1), repeat=3):
                    entry = [(v, hr) for v in R] + [(v, hp) for v in Pp]
                    demand = [(v, hc) for v in O]
                    opt = dijkstra(entry, demand, H)
                    formula = min(rho_r * abs(x - hr) + rho_p * abs(x - hp) + rho_o * abs(x - hc)
                                  for x in range(H + 1))
                    need(opt == formula, "meeting formula = Dijkstra optimum at %s" % ((R, Pp, O, hr, hp, hc),))
                    count += 1
    return count


def hosted_template():
    raw = (ROOT / HOSTED[0]).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == HOSTED[1], "hosted archive pin")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
        data = tar.extractfile(tar.getmember(HOSTED[2])).read()
    need(hashlib.sha256(data).hexdigest() == HOSTED[3], "hosted template pin")
    return json.loads(gzip.decompress(data))


def hosted_heights(h, replica):
    """Per-family height (applied coordinates) of every family of one replica at the route instants."""
    sched = [e for e in h["execution_schedule"] if e.get("replica") == replica]
    need([e["source_event"] for e in sched] == list(range(30)), "replica schedule of 30 events")
    pair_of_stage = {e["stage"]: e["pair"] for e in h["recipe"] if e["kind"] == "local"}
    base = 896 * replica
    by_child = {}
    for c in h["idle_children"]:
        if c["replica"] == replica:
            by_child.setdefault(c["child"], []).append(c)
    steps = {f: [] for f in range(896)}            # (time, event index or None, delta)
    for i, e in enumerate(sched):
        if e["kind"] == "local_cover_sweep":
            p = pair_of_stage[e["stage"]]
            for f in range(224 * p, 224 * p + 224):
                steps[f].append((e["time"], i, 8))
        elif e["kind"] == "idle_cover_sweep":
            for c in e["child_indices"]:
                for row in by_child.get(c, []):
                    steps[row["family"] - base].append((e["time"], i, row["rank"]))
    for slot in h["hosting"]["pooled_slots"]:
        if slot["owner_replica"] == replica:
            steps[slot["family"] - base].append((slot["time"], None, slot["width"]))
    need(all(sum(d for _, _, d in steps[f]) == 72 for f in steps), "every family ends with 72 coordinates")

    def height(f, idx, after, tie):
        """Just before (after=False) or after event idx; tie 0 puts equal-time slots first, tie 1 last."""
        t = sched[idx]["time"]
        total = 0
        for time, i, d in steps[f]:
            if i is not None:
                total += d if (i < idx or (after and i == idx)) else 0
            elif time < t or (time == t and tie == 0):
                total += d
        return total

    def settled(f, t):
        """After every event and slot at times <= t."""
        return sum(d for time, _, d in steps[f] if time <= t)

    def uniform(values):
        vals = set(values)
        need(len(vals) == 1, "one uniform height on the pair at a route instant (replica %d)" % replica)
        return vals.pop()

    fams = lambda p: range(224 * p, 224 * p + 224)
    out = {}
    for tie in (0, 1):
        out["INIT", tie] = [uniform(height(f, i, False, tie) for f in fams(k)) for k, i in enumerate((0, 7, 13, 19))]
        out["dA", tie] = [uniform(height(f, i, True, tie) for f in fams(k)) for k, i in enumerate((1, 7, 13))]
        out["early", tie] = [uniform(height(f, i, True, tie) for f in fams(k)) for k, i in enumerate((4, 10, 16, 20))]
        # P_Y: bank 0 right after event 6; banks 1-3 after bridges 27/26/25, read once their time (the final
        # sweeps' time) has settled, since residual slots at that time belong to the final sweeps.
        out["Y", tie] = [uniform(height(f, 6, True, tie) for f in fams(0))] + \
            [uniform(settled(f, sched[i]["time"]) for f in fams(k)) for k, i in ((1, 27), (2, 26), (3, 25))]
        out["y3_window", tie] = {height(f, 14, False, tie) for f in range(784, 896)}
    times = [sched[i]["time"] for i in (5, 11, 17)]
    out["allinit_read"] = [uniform(settled(f, t) for f in fams(k + 1)) for k, t in enumerate(times)]
    out["allinit_consumer"] = [uniform(settled(f, t) for f in fams(k)) for k, t in enumerate(times)]
    t14 = sched[14]["time"] - sched[0]["time"]
    out["t14"] = t14
    out["x3_early"] = sum(1 for slot in h["hosting"]["pooled_slots"]
                          if slot["owner_replica"] == replica and 672 <= slot["family"] - base < 784
                          and slot["time"] < sched[14]["time"])
    return out


def controls(t):
    """Negative/positive controls for the independent method (each must behave as stated)."""
    rejected = 0
    need(dijkstra([((1, 0), 0)], [((1, 0), 3)], 3) == 3, "positive control: one row climbs three levels")
    need(dijkstra([((1, 0), 0), ((0, 1), 3)], [((1, 1), 3)], 3) == 3, "positive control: record climb to partner")
    need(dijkstra([((1, 0), 0), ((0, 1), 3)], [((1, 1), 0)], 3) == 3, "positive control: partner descent")
    bad = json.loads(json.dumps(t))
    sweep = next(e for e in bad["execution_schedule"][:30] if e["kind"] == "idle_cover_sweep" and 4 in e["child_indices"])
    for e in bad["idle_children"]:
        if e["port"] == 0 and e["child"] in sweep["child_indices"]:
            e["rank"] -= 8                     # drop one stage block from both children of pair 2's first idle sweep
    try:
        coordinate_replay(bad)
    except Fail as exc:
        need(str(exc) == "declared idle levels agree with rank/8 blocks", "control 1 rejected for the stated reason")
        rejected += 1
    # A formula without the output-transport term must disagree with the optimum somewhere.
    wrong = sum(1 for hr, hp, hc in itertools.product(range(4), repeat=3)
                if dijkstra([((1, 0), hr), ((0, 1), hp)], [((1, 1), hc)], 3)
                != min(abs(x - hr) + abs(x - hp) for x in range(4)))
    need(wrong > 0, "negative control: dropping the output term must fail")
    rejected += 1
    return rejected


def main():
    t = template()
    snapshots, stage_pair = coordinate_replay(t)
    v = law(snapshots, stage_pair, t)
    need(pr2540_frames() == 8 and v["PR2540"] == 128, "PR2540: 16 x |F_U1 - F_L| = 16 x 8 = 128")
    need(v["INIT"] == [1152, 768, 512, 256] and v["dA"] == [448, 320, 192], "INIT / d_A climbs")
    total = sum(v["INIT"]) + sum(v["dA"])
    need(total == 3648, "INIT64 + d_A = 3648")
    need(sum(v["dA"]) == 960, "d_A alone 960")
    need(v["last_write"] == [6, 27, 26, 25] and v["y_levels"] == [2, 8, 8, 8] and v["y_mass"] == 2496,
         "X_(k,U) last written at events 6/27/26/25; earliest Y-allowed consumers 2/8/8/8; 2496")
    need(v["early"] == 1344, "P_early 1344")
    need(v["allinit_reads"] == ([48, 32, 16], [0, 0, 0]), "all-initial reads: 8 x 48/32/16 at the end, 0 at P_early")
    need((v["allinit_final"], v["allinit_y"], v["allinit_early"]) == (3456, 2304, 1152), "all-initial variant 3456 / 2304 / 1152")
    tb = v["thmB"]
    need(tb["final", "original"] == (1952, 1952, 1952) and tb["final", "all_initial"] == (1824, 1824, 1824),
         "Theorem B, one consumer level: cut loop = own-bank = count-only = 1952 / 1824")
    need((tb["Y", "original"], tb["Y", "all_initial"], tb["early", "original"], tb["early", "all_initial"])
         == ((1344, 608, None), (1216, 544, None), (800, 112, None), (608, 0, None)),
         "Theorem B own-bank 1344/1216 (Y), 800/608 (early); count-only 608/544 (Y), 112/0 (early)")
    need(v["x0_last_write"] == 6 and v["x0_levels_after_13"] == 6, "X_(0,U) last written at event 6 (lagging example)")
    need(v["zero_witness"] == (0, 6), "zero-advance window: no coordinate applied to pair 3 across six calls")
    dec = decimal_checks()
    n = frame_checks()
    rejected = controls(t)
    need(rejected == 2, "both independent controls rejected")
    h = hosted_template()
    window_ok = []
    for replica in range(16):
        hh = hosted_heights(h, replica)
        for tie in (0, 1):
            need(hh["INIT", tie] == [0, 24, 40, 56] and hh["dA", tie] == [16, 32, 48]
                 and hh["early", tie] == [24, 40, 56, 72] and hh["Y", tie] == [24, 72, 72, 72],
                 "hosted heights at captures and consumers (replica %d, tie convention %d)" % (replica, tie))
        need(hh["allinit_read"] == [24, 40, 56] and hh["allinit_consumer"] == [24, 40, 56],
             "all-initial read and consumer at one level after the sweep time settles (replica %d)" % replica)
        if hh["y3_window", 0] == hh["y3_window", 1] == {0}:
            window_ok.append(replica)
        if replica == 0:
            need((hh["t14"], hh["x3_early"]) == (40, 160), "window ends at time 40; pair-3 X streams host 160 residuals in it")
    need(window_ok == [0, 1, 2, 3, 7, 8, 9, 10, 12, 13, 14, 15],
         "zero-advance window on the pair-3 Y streams holds in 12 replicas (not 4, 5, 6, 11)")
    n_inst = sum(len(hh[key]) for key in (("INIT", 0), ("dA", 0), ("early", 0), ("Y", 0), "allinit_read", "allinit_consumer"))
    need(n_inst == 21, "21 route instants at exact hosted heights")
    print("PASS_RETAINED_ARRAY_CATCH_UP_INDEPENDENT pr2540=128 init64_dA=%d/2496/1344 all_initial=3456/2304/1152 dA_only=960 "
          "thmB_one_level=1952/1824 thmB_own_bank=1344/1216/800/608 thmB_count_only=608/544/112/0 zero_advance_calls=6 "
          "zero_advance_replicas=%d/16 hosted_route_instants=%dx16 breakeven_S=%d breakeven_C=%d no_saving=%d "
          "echelon_dijkstra_instances=%d controls_rejected=%d"
          % (total, len(window_ok), n_inst, dec["breakeven_idle"], dec["breakeven_rank8"], dec["threshold"], n, rejected))


if __name__ == "__main__":
    try:
        main()
    except Fail as exc:
        print("FAIL:", exc)
        sys.exit(1)
