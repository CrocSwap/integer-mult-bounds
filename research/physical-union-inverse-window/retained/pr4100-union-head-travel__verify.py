#!/usr/bin/env python3
"""Literal multitape head travel of #4100's radix-distributed sparse-union schedule.

Standard library only, exact integers. Every step of vendor/UNION-SCHEDULE.md
section 2 runs on explicit tapes whose head moves are counted. The tapes are
the two work tapes, the radix tapes Z/O, the bit tape Tb, the zip tapes
M1/M2, a record and an indicator LIFO, the indicator bits of the forming
scan, and the microbox. The result is compared with the full Kronecker
product. Finite corroboration, not an all-size proof. Independent of the
lineage sched_test.py/sched_review.py. Ryanson Jonathan with Claude Code
(Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/unconditional-batched-crt"
RW = 8  # record width in cells (payload plus o(p) header); bits are one cell


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def ceil_log2(n):
    return max(1, (n - 1).bit_length()) if n > 1 else 0


# --- 0. Source binding -----------------------------------------------------------

PHRASES = [
    "Round r (r = 1,2,...,R, where R = max |F| <= g) applies to every record x of S_r the operator T_{f_r(F(x))}",
    "2. **Stable binary LSD radix distribution by tag.**",
    "4. **Variable-length lockstep transpose of every prefix block**",
    "rewind over the written length |S_r| only; cells beyond are stale and never read",
    "Hence the head travel of round r is O(|S_r| p (log g + log a + 1))",
    "`sum_r |S_r| = sum_x |F(x)| = sum_i |U_i| = sum_i |E_i| L^(g-1) * (spectators) <= g mu V.`",
    "The step \"variable block length\" of the transpose (item 4) and the head accounting (2.3) are the places that most need an independent review.",
]


def check_sources():
    pins = {row["path"]: row["sha256"]
            for row in json.loads((Path(__file__).parent / "SOURCES.json").read_text())["files"]}
    for rel in ("research/unconditional-batched-crt/vendor/UNION-SCHEDULE.md",
                "research/unconditional-batched-crt/evidence/composition-controls.json"):
        need(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == pins[rel], f"pin {rel}")
    text = (SOURCE / "vendor/UNION-SCHEDULE.md").read_text()
    for phrase in PHRASES:
        need(phrase in text, f"source phrase missing: {phrase[:60]}")
    ledger = json.loads((SOURCE / "evidence/composition-controls.json").read_text())
    slack = Fraction(ledger["cost_slacks"]["union"])
    need(Fraction(2, 5) < slack < Fraction(1, 2), "union row slack in #4100's ledger")
    return len(PHRASES), float(slack)


# --- 1. Tapes -------------------------------------------------------------------------

class Tape:
    """Cells hold records (width RW) or bits (width 1). Moves are counted in cells."""

    def __init__(self, width, stale_rewinds=False):
        self.cells, self.pos, self.moves, self.w = [], 0, 0, width
        self.extent = 0
        self.end = 0  # logical end marker of the current contents; cells beyond are stale
        self.stale = stale_rewinds

    def goto(self, i):
        self.moves += abs(i - self.pos) * self.w
        self.pos = i

    def rewind(self):
        if self.stale:  # control: scan to the physical end of everything ever written first
            self.goto(self.extent)
        self.goto(0)

    def peek(self):
        return self.cells[self.pos] if self.pos < self.end else None

    def read(self):
        need(self.pos < self.end, "read past the end marker")
        v = self.cells[self.pos]
        self.pos += 1
        self.moves += self.w
        return v

    def write(self, v):
        if self.pos < len(self.cells):
            self.cells[self.pos] = v
        else:
            self.cells.append(v)
        self.pos += 1
        self.moves += self.w
        self.extent = max(self.extent, self.pos)
        self.end = max(self.end, self.pos)

    def truncate(self):
        """Place the end marker at the head (contents written from 0 end here)."""
        self.end = self.pos


# --- 2. The schedule ------------------------------------------------------------------

def tree_nodes(a):
    """Recursive halving with h = floor(n/2) first; returns {(lo, n): (h, height)} and heights."""
    nodes = {}

    def build(lo, n):
        if n == 1:
            nodes[(lo, n)] = (None, 0)
            return 0
        h = n // 2
        ht = 1 + max(build(lo, h), build(lo + h, n - h))
        nodes[(lo, n)] = (h, ht)
        return ht

    top = build(0, a)
    return nodes, top


def unit_of(k, a, nodes, level):
    """Frontier unit containing ordinal k before merging nodes of height `level`, and its role."""
    lo, n, parent = 0, a, None
    while nodes[(lo, n)][1] >= level:
        parent = (lo, n)
        h = nodes[(lo, n)][0]
        lo, n = (lo, h) if k < lo + h else (lo + h, n - h)
    if parent is not None and nodes[parent][1] == level:
        plo, pn = parent
        return parent, ("A" if lo == plo else "B")
    return (lo, n), "pass"


def run(g, L, esizes, seed, *, drop_round=None, stale=False, wrong_zip=False):
    rnd = random.Random(seed)
    E = [sorted(rnd.sample(range(L), esizes[i])) for i in range(g)]
    rank = [{v: k for k, v in enumerate(e)} for e in E]
    T = [[[rnd.randrange(-2, 3) for _ in e] for _ in e] for e in E]
    pts = list(itertools.product(range(L), repeat=g))
    X = {x: rnd.randrange(-3, 4) for x in pts}
    ref = dict(X)
    for i in range(g):  # full Kronecker product, axis by axis
        new = dict(ref)
        for x in pts:
            if x[i] in rank[i]:
                row = rank[i][x[i]]
                new[x] = sum(T[i][row][c] * ref[x[:i] + (E[i][c],) + x[i + 1:]] for c in range(len(E[i])))
        ref = new
    flags = {x: tuple(i for i in range(g) if x[i] in rank[i]) for x in pts}

    def mk(width):
        return Tape(width, stale_rewinds=stale)

    MB, IND = mk(RW), mk(1)
    W = [mk(RW), mk(RW)]
    Z, O, Tb, M1, M2 = mk(RW), mk(RW), mk(1), mk(RW), mk(RW)
    STR, STB = mk(RW), mk(1)  # LIFO of final records and of keep indicators
    union_tapes = [W[0], W[1], Z, O, Tb, M1, M2, STR, STB]
    for x in pts:
        MB.write((x, X[x]))
    MB.truncate()
    MB.goto(0)
    MB.moves = 0  # the microbox is given; only the scans below are charged
    # Forming scan (dense, group-scan row): U with indicator bits.
    for _ in pts:
        x, v = MB.read()
        IND.write(1 if flags[x] else 0)
        if flags[x]:
            W[0].write((x, v))
    N = W[0].pos
    W[0].truncate(); IND.truncate()
    MB.rewind(); IND.rewind(); W[0].rewind()
    dense = MB.moves + IND.moves
    W[0].moves = 0
    cur, line_moves, rounds, sizes, rest_sizes = 0, 0, 0, [], []
    nb = ceil_log2(g)
    lines_checked = 0
    r = 0
    while N:
        sizes.append(N)
        Wa, Wb = W[cur], W[1 - cur]
        tag = lambda rec: flags[rec[0]][r]
        # Step 2: stable LSD radix distribution by tag, nb passes.
        n0s = []
        Tb.goto(0)
        for k in range(nb):
            n0 = 0
            Z.goto(0); O.goto(0)
            for _ in range(N):
                rec = Wa.read()
                bit = (tag(rec) >> k) & 1
                Tb.write(bit)
                if bit:
                    O.write(rec)
                else:
                    Z.write(rec)
                    n0 += 1
            n0s.append(n0)
            Z.truncate(); O.truncate()
            Wa.rewind(); Z.rewind(); O.rewind()
            for _ in range(n0):
                Wa.write(Z.read())
            for _ in range(N - n0):
                Wa.write(O.read())
            Wa.truncate()
            Z.rewind(); O.rewind(); Wa.rewind()
        Tb.truncate()
        # Steps 3-6 per axis substream (contiguous by tag).
        seg_start = 0
        while seg_start < N:
            Wa.goto(seg_start)
            f = tag(Wa.peek())
            n_seg = 0
            while seg_start + n_seg < N and tag(Wa.cells[seg_start + n_seg]) == f:
                n_seg += 1
            a = len(E[f])
            nodes, top = tree_nodes(a)
            levels = list(range(1, top + 1))

            def key(rec):
                return rec[0][:f], rank[f][rec[0][f]]

            def zip_level(level, merge):
                # Pass 1: split the segment onto M1 (A parts and pass units) and M2 (B parts).
                Wa.goto(seg_start)
                M1.goto(0); M2.goto(0)
                for _ in range(n_seg):
                    rec = Wa.read()
                    pre, k = key(rec)
                    unit, role = unit_of(k, a, nodes, level)
                    if not merge and role != "pass":
                        lo, n = unit
                        h = nodes[unit][0]
                        role = "A" if k < lo + h else "B"
                    (M2 if role == "B" else M1).write(rec)
                M1.truncate(); M2.truncate()
                M1.rewind(); M2.rewind()
                Wa.goto(seg_start)
                # Pass 2: rebuild the segment, unit by unit, from M1/M2 in lockstep. Unit ends are
                # read from headers (prefix field and ordinal range); the row length is never used.
                written = 0
                while written < n_seg:
                    before = written
                    rec = M1.peek()
                    need(rec is not None, "M1 exhausted before the segment was rebuilt")
                    pre, k = key(rec)
                    unit, role = unit_of(k, a, nodes, level)
                    lo, n = unit

                    def within(tape, lo_, hi_, pre=pre):
                        rr = tape.peek()
                        return rr is not None and key(rr)[0] == pre and lo_ <= key(rr)[1] < hi_

                    if role == "pass":
                        while within(M1, lo, lo + n):
                            Wa.write(M1.read()); written += 1
                    else:
                        h_true = nodes[unit][0]
                        h = n - h_true if wrong_zip else h_true  # control: mismatched chunk sizes
                        if merge:  # lockstep: h from A, then n-h from B, until both parts end together
                            while within(M1, lo, lo + h_true):
                                for _ in range(h):
                                    Wa.write(M1.read()); written += 1
                                for _ in range(n - h):
                                    Wa.write(M2.read()); written += 1
                        else:      # unzip: the whole A part, then the whole B part
                            while within(M1, lo, lo + n):
                                Wa.write(M1.read()); written += 1
                            while within(M2, lo, lo + n):
                                Wa.write(M2.read()); written += 1
                    need(written > before, "no progress in a lockstep pass")
                need(written == n_seg, "segment rebuilt exactly")
                M1.rewind(); M2.rewind()
                Wa.goto(seg_start)

            for level in levels:
                zip_level(level, merge=True)
            # Step 5: every consecutive group of a records must be a complete E_f-line.
            Wa.goto(seg_start)
            for _ in range(n_seg // a):
                group = [Wa.read() for _ in range(a)]
                ords = [rank[f][rec[0][f]] for rec in group]
                need(ords == list(range(a)), "group is a complete E_f-line in ordinal order")
                need(len({rec[0][:f] + rec[0][f + 1:] for rec in group}) == 1, "one common z per line")
                vals = [rec[1] for rec in group]
                if drop_round != r:
                    vals = [sum(T[f][row][c] * vals[c] for c in range(a)) for row in range(a)]
                Wa.goto(Wa.pos - a)
                for rec, v in zip(group, vals):
                    Wa.write((rec[0], v))
                lines_checked += 1
            need(n_seg % a == 0, "segment splits into lines")
            for level in reversed(levels):
                zip_level(level, merge=False)
            seg_start += n_seg
        Wa.rewind()
        # Step 6: undo the radix distribution by replaying the passes in reverse.
        for k in reversed(range(nb)):
            n0 = n0s[k]
            Z.goto(0); O.goto(0)
            for i in range(N):
                (Z if i < n0 else O).write(Wa.read())
            Z.truncate(); O.truncate()
            Wa.rewind(); Z.rewind(); O.rewind()
            Tb.goto(k * N)
            for _ in range(N):
                Wa.write(O.read() if Tb.read() else Z.read())
            Z.rewind(); O.rewind(); Wa.rewind()
        Tb.rewind()
        # Step 7: split; final records and the keep indicators go to the LIFO tapes.
        Wb.goto(0)
        rest = 0
        for _ in range(N):
            rec = Wa.read()
            keep = len(flags[rec[0]]) > r + 1
            STB.write(1 if keep else 0)
            if keep:
                Wb.write(rec)
            else:
                STR.write(rec)
                rest += 1
        rest_sizes.append(rest)
        Wb.truncate()
        Wa.rewind()
        N_next = Wb.pos
        Wb.rewind()
        cur, N, r = 1 - cur, N_next, r + 1
    rounds = r
    # Wrap-up: pop the LIFO, interleaving rest_r with S_{r+1} by keep_r, for r = R..1.
    str_end, stb_end = STR.pos, STB.pos
    for rr in reversed(range(rounds)):
        n_r, rest = sizes[rr], rest_sizes[rr]
        STR.goto(str_end - rest)
        STB.goto(stb_end - n_r)
        src, dst = W[cur], W[1 - cur]
        src.goto(0); dst.goto(0)
        for _ in range(n_r):
            dst.write(src.read() if STB.read() else STR.read())
        dst.truncate()
        str_end -= rest
        stb_end -= n_r
        src.rewind(); dst.rewind()
        cur = 1 - cur
    # Final merge into the microbox by the forming scan's indicator bits (dense).
    S1 = W[cur]
    m0, i0 = MB.moves, IND.moves
    result = {}
    for _ in pts:
        x, v = MB.read()
        if IND.read():
            y, w = S1.read()
            need(y == x, "merge order")
            result[x] = w
        else:
            result[x] = v
        MB.goto(MB.pos - 1)
        MB.write((x, result[x]))
    MB.rewind(); IND.rewind(); S1.rewind()
    dense += (MB.moves - m0) + (IND.moves - i0)
    union = sum(t.moves for t in union_tapes)
    sum_f = sum(len(fl) for fl in flags.values())
    U = sum(1 for fl in flags.values() if fl)
    return dict(ok=result == ref, union=union, dense=dense, sumF=sum_f, streamed=sum(sizes), U=U,
                rounds=rounds, sizes=sizes, nb=nb, amax=max(esizes), V=len(pts), lines=lines_checked)


def union_bound(st):
    """Written per-pass accounting (README), per round of N records, in cells:
    radix 7 nb N RW + nb N bits; each zip or unzip level 8 N RW; in-place line sweep and return
    4 N RW; segment navigation N RW; final rewind N RW; radix undo 8 nb N RW + 3 nb N bits;
    split 4 N RW + N bits; LIFO pops and interleave 7 N RW + 3 N bits."""
    nb, lev = st["nb"], ceil_log2(st["amax"])
    per = (15 * nb + 16 * lev + 17) * RW + (4 * nb + 4)
    return sum(st["sizes"]) * per


CASES = [
    (3, 8, [3, 2, 3], 21),
    (4, 6, [2, 2, 3, 2], 11),
    (5, 7, [2, 3, 2, 3, 2], 5),
    (6, 5, [2, 2, 2, 3, 2, 2], 3),
    (4, 5, [4, 4, 3, 4], 7),         # dense flags: most records carry many flags
    (6, 5, [1, 1, 1, 1, 1, 2], 13),  # sparse flags: |F| mostly 1, a few records with |F| = 6
]


def check_schedule():
    rows = []
    for g, L, es, seed in CASES:
        st = run(g, L, es, seed)
        need(st["ok"], f"exact Kronecker product g={g} L={L}")
        need(st["streamed"] == st["sumF"] == sum(e * L ** (g - 1) for e in es), "volume identity")
        need(st["sumF"] <= g * st["U"], "sum|F| <= g|U|")
        bound = union_bound(st)
        need(st["union"] <= bound, f"union head travel within the written bound g={g}: {st['union']} > {bound}")
        # Forming scan 2V RW + 2V; in-place final merge 4V RW + 2V; so <= 6V RW + 4V <= 8V RW.
        need(st["dense"] <= 6 * st["V"] * RW + 4 * st["V"], "forming scan and final merge are O(V)")
        norm = RW * st["sumF"] * (st["nb"] + ceil_log2(st["amax"]) + 1)
        rows.append(dict(g=g, L=L, E=es, V=st["V"], U=st["U"], sumF=st["sumF"], rounds=st["rounds"],
                         union_over_RW_sumF_logs=round(st["union"] / norm, 3),
                         union_over_bound=round(st["union"] / bound, 3),
                         dense_over_V_RW=round(st["dense"] / (st["V"] * RW), 3), lines=st["lines"]))
    return rows


def check_controls():
    out = {}
    st = run(5, 7, [2, 3, 2, 3, 2], 5, drop_round=1)
    need(not st["ok"], "control: skipping the second round's application changes the result")
    out["dropped_round_detected"] = True
    try:
        run(5, 7, [2, 3, 2, 3, 2], 5, wrong_zip=True)
        detected = False
    except (AssertionError, IndexError):
        detected = True
    need(detected, "control: transposing with mismatched chunk sizes breaks the complete-line check")
    out["wrong_zip_detected"] = detected
    # Rewinding over stale cells (the extent of S_1) charges every round for |U|.
    for g, L, es, seed in ((6, 5, [1, 1, 1, 1, 1, 2], 13), (4, 5, [4, 4, 3, 4], 7)):
        good = run(g, L, es, seed)
        bad = run(g, L, es, seed, stale=True)
        need(bad["ok"], "stale rewinds do not change the result")
        out[f"stale_rewind_ratio_g{g}"] = round(bad["union"] / good["union"], 3)
        out[f"stale_rewind_over_bound_g{g}"] = round(bad["union"] / union_bound(bad), 3)
    need(out["stale_rewind_over_bound_g6"] > 1, "control: stale rewinds break the written bound (sparse flags)")
    # The old per-axis scan of U costs g |U| record visits per window, against sum|F|.
    sparse = run(6, 5, [1, 1, 1, 1, 1, 2], 13)
    out["old_axis_scan_over_sumF_sparse"] = round(6 * sparse["U"] / sparse["sumF"], 3)
    return out


def main():
    phrases, slack = check_sources()
    rows = check_schedule()
    controls = check_controls()
    need(controls["stale_rewind_ratio_g4"] > 1.5, "control: stale rewinds cost visibly more on dense flags")
    print(json.dumps({
        "status": "PASS_PR4100_UNION_HEAD_TRAVEL_FINITE",
        "source_phrases": phrases,
        "ledger_union_slack": round(slack, 6),
        "record_width_cells": RW,
        "cases": rows,
        "controls": controls,
        "all_size_theorem_claimed": False,
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
