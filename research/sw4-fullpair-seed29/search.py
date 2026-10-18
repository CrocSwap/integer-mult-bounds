#!/usr/bin/env python3
"""Simultaneous FULL entering-copy read exchanges on the pinned P6k4 word.

Track: complex supplier (assignment seed 29). Object: all unordered pairs and
triples of the legal full single-pair read-set exchanges, applied at once on
bare P6k4 (input 0390ec65...). BRoute's notes leave cross-pair combinations
open; PR #775 enumerates partial-involving combinations and explicitly excludes
all-full combinations. This closes the all-full class for arity 2 and 3.

Rewrite/frame semantics follow the credited SW4 construction
(research/complex-sw4-frame8/construction/sw4/build_sw4.py): a moved or
inserted B gate takes the join of its current operand frames; every untouched
B gate keeps its original frame as a floor and joins current operand frames;
early-cleanup tails keep their original floors; caps, tails and ends are
checked exactly; helper identities and start/end frames are fixed.

Candidate order is shuffled with random.Random(29) (assignment seed); every
per-candidate outcome is recorded under an order-independent key, so the
evidence does not depend on the shuffle.

Usage (from the repository root):
  python3 research/sw4-fullpair-seed29/search.py --out <dir>
writes CANDIDATES.json, EVIDENCE.json, SEARCH.json to <dir> (created).
Standard library only.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import random
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RECIPE = REPO / "research/complex-sw4-frame8/construction/sw4/SW4-RECIPE-P6k4.json"
WORD = HERE / "inputs/P6K4-WORD.json.gz"

V = 112
HH = 9
PR = 2147483629
SEED = 29
# Floating nomination aid only (credited: PR #775 / PR #699 complex endpoint).
COST_EXPONENT = 0.0016634287545402057


@lru_cache(maxsize=None)
def basis(vectors):
    # Reduced row-echelon over F2 with fixed bit order (same canonical form as
    # research/complex-sw4-frame8/construction/sw4/build_sw4.py): the pivot
    # set is a span invariant and equal spans give equal tuples.
    piv = {}
    for x in vectors:
        while x:
            k = x.bit_length() - 1
            if k in piv:
                x ^= piv[k]
            else:
                piv[k] = x
                break
    for k in sorted(piv):
        for j in piv:
            if j > k and piv[j] >> k & 1:
                piv[j] ^= piv[k]
    return tuple(piv[k] for k in sorted(piv, reverse=True))


@lru_cache(maxsize=None)
def join(a, b):
    return basis(a + b)


@lru_cache(maxsize=None)
def cap_ok(frame, port):
    return all((x & port).bit_count() % 2 == 0 for x in frame)


@lru_cache(maxsize=None)
def hyper(port):
    return basis(tuple(x for x in range(1, 1 << HH) if (x & port).bit_count() % 2 == 0))


FULL = basis(tuple(1 << i for i in range(HH)))


def regs(e):
    return e[1:3] if e[0] == "add" else e[1:2]


def encode(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode()


def floating_cost(profile):
    return sum(v * (int(k) ** (1.0 - COST_EXPONENT)) for k, v in profile.items())


class Evaluator:
    """One-pass exact frame refit with paid-profile accounting."""

    def __init__(self, word):
        self.w = word
        n = 2 * V + word["report"]["R"]
        start = [(p,) for p in word["ports"]] + [()] * (n - V)
        for q, f in word["start_extra"].items():
            start[int(q)] = basis(tuple(f))
        end = [FULL] * V + [hyper(p) for p in word["ports"]] + [FULL] * (n - 2 * V)
        for q, f in word["helper_final"].items():
            end[int(q)] = basis(tuple(f))
        cur = list(start)
        paid = [0] * 10
        for e in word["A"]:
            f = basis(tuple(e[-1]))
            for q in regs(e):
                if join(cur[q], f) != f:
                    raise ValueError(("A-containment", q))
                d = len(f) - len(cur[q])
                if d:
                    paid[d] += 1
                cur[q] = f
        levels = {int(t): basis(tuple(f)) for t, f in word.get("target_levels", {}).items()}
        for q, f in zip(word["centers"], word["center_frames"]):
            f = basis(tuple(f))
            served = {levels.get(e[1] - V, ()) for e in word["cut"] if e[2] == q}
            for t in sorted(served, key=lambda x: -len(x)):
                if t != f:
                    paid[len(f) - len(t)] += 1
                f = t
        self.start_cur = cur
        self.start_paid = paid
        self.end = end
        self.gates = [
            (list(e[1:3]) if e[0] == "add" else list(e[1:2]), basis(tuple(e[-1])))
            for e in word["B"]
        ]
        self.tails = [
            (list(regs(word["cleanup"][i])), basis(tuple(f)))
            for i, f in word.get("early_cleanup", [])
        ]

    def run(self, moves):
        """Apply original-index moves in one pass.

        Returns (profile, None) on success or (None, failure) where failure is
        a (reason, ...) tuple. Move order is canonicalized by the caller.
        """
        edits = {}
        delete = set()
        insert = {}
        for m in moves:
            i = m["read_index"]
            if i in edits:
                return None, ("conflicting_read", i)
            edits[i] = (m["target"], m["r"] if m["kind"] == "h2r" else m["h"])
            if m["kind"] == "h2r":
                if m["delete_preread_index"] in delete:
                    return None, ("conflicting_delete", m["delete_preread_index"])
                delete.add(m["delete_preread_index"])
            else:
                insert.setdefault(m["insert_preread_before"], []).append(
                    (m["target"], m["h"])
                )
        if delete & set(edits):
            return None, ("edit_delete_overlap",)
        cur = self.start_cur[:]
        paid = self.start_paid[:]
        for i, (rs, floor) in enumerate(self.gates):
            for irs in insert.get(i, ()):
                bad = self._gate(cur, paid, irs, (), ("insert", i))
                if bad:
                    return None, bad
            if i in delete:
                continue
            if i in edits:
                bad = self._gate(cur, paid, list(edits[i]), (), i)
            else:
                bad = self._gate(cur, paid, rs, floor, i)
            if bad:
                return None, bad
        for i, (rs, floor) in enumerate(self.tails):
            f = floor
            for q in rs:
                f = join(f, cur[q])
            for q in rs:
                if join(cur[q], f) != f or join(f, self.end[q]) != self.end[q]:
                    return None, ("tail", i, q)
            for q in rs:
                d = len(f) - len(cur[q])
                if d:
                    paid[d] += 1
                cur[q] = f
        for q, f in enumerate(self.end):
            if join(cur[q], f) != f:
                return None, ("end", q)
            d = len(f) - len(cur[q])
            if d:
                paid[d] += 1
        return {str(k): v for k, v in enumerate(paid) if k and v}, None

    def _gate(self, cur, paid, rs, floor, origin):
        f = floor
        for q in rs:
            f = join(f, cur[q])
        for q in rs:
            if V <= q < 2 * V and not cap_ok(f, self.w["ports"][q - V]):
                return ("cap", origin if isinstance(origin, int) else origin[0], q)
        for q in rs:
            d = len(f) - len(cur[q])
            if d:
                paid[d] += 1
            cur[q] = f
        return None


def find_pairs(w):
    """Eligible entering-copy pairs and their movable reads (BRoute rule)."""
    gates = w["B"]
    found = []
    for h in sorted(map(int, w["start_extra"])):
        touched = [i for i, e in enumerate(gates) if h in regs(e)]
        writes = [i for i in touched if gates[i][1] == h]
        if not writes:
            continue
        ci = writes[0]
        e = gates[ci]
        if e[0] != "add" or e[3:5] != [1, 1] or V <= e[2] < 2 * V:
            continue
        r = e[2]
        before = [i for i in touched if i < ci]
        if any(
            not (gates[i][0] == "add" and V <= gates[i][1] < 2 * V and gates[i][2] == h)
            for i in before
        ):
            continue
        stop = next(
            (i for i in range(ci + 1, len(gates)) if gates[i][1] in (h, r)),
            len(gates),
        )
        insertion = before[-1] + 1 if before else ci
        moves = []
        for i in range(ci + 1, stop):
            g = gates[i]
            if g[0] != "add" or not V <= g[1] < 2 * V or g[2] not in (h, r):
                continue
            t, a, b = g[1], g[3], g[4]
            m = {"h": h, "r": r, "read_index": i, "target": t, "coef": [a, b]}
            if g[2] == h:
                pre = [j for j in before if gates[j][:5] == ["add", t, h, -a, b]]
                if len(pre) != 1:
                    continue
                m.update(kind="h2r", delete_preread_index=pre[0])
            else:
                m.update(
                    kind="r2h",
                    insert_preread_before=insertion,
                    preread=["add", t, h, -a, b],
                )
            moves.append(m)
        if moves:
            found.append(
                {"h": h, "r": r, "copy_index": ci, "stop_index": stop, "moves": moves}
            )
    return found


def canon(moves):
    return sorted(moves, key=lambda m: (m["read_index"], m["kind"], m["h"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--arity", type=int, nargs="+", default=[2, 3])
    a = ap.parse_args()
    out = a.out
    out.mkdir(parents=True, exist_ok=True)
    t_start = time.monotonic()

    raw = gzip.decompress(WORD.read_bytes())
    word = json.loads(raw)
    sha = hashlib.sha256(raw).hexdigest()
    rec = json.loads(RECIPE.read_text())
    assert sha == rec["input_sha256"], "pinned promoted-input hash mismatch"

    ev = Evaluator(word)
    base, bad = ev.run([])
    assert not bad and base == rec["profile_in"], ("input profile", base, bad)
    sw, bad = ev.run(canon(rec["moves"]))
    assert not bad and sw == rec["profile_out"], ("SW4 profile", sw, bad)
    print("BASELINE_OK", sha, flush=True)

    pairs = find_pairs(word)
    n_single_subsets = sum((1 << len(p["moves"])) - 1 for p in pairs)
    print(
        "PAIRS",
        len(pairs),
        "single_subsets",
        n_single_subsets,
        "move_histogram",
        dict(Counter(len(p["moves"]) for p in pairs)),
        flush=True,
    )
    # NOTE: newline="\n" keeps committed bytes platform-stable (sha-pinned).
    (out / "CANDIDATES.json").write_text(
        json.dumps({"input_sha256": sha, "pairs": pairs}, indent=2) + "\n",
        newline="\n",
    )

    # Single-pair revalidation: recover the 38 legal full exchanges.
    counts = Counter()
    full_of = {}
    for p in pairs:
        ms = p["moves"]
        for mask in range(1, 1 << len(ms)):
            moves = [m for j, m in enumerate(ms) if mask >> j & 1]
            profile, fail = ev.run(canon(moves))
            counts["single_total"] += 1
            if profile is None:
                counts["single_" + fail[0]] += 1
            else:
                counts["single_legal"] += 1
                if mask == (1 << len(ms)) - 1:
                    full_of[p["h"]] = (profile, moves)
    legal_full_h = sorted(full_of)
    print("SINGLES", dict(counts), "legal_full", legal_full_h, flush=True)

    recipe_h = sorted(int(h) for h in rec["pairs"])
    assert all(h in full_of for h in recipe_h), "recipe pairs must be legal fulls"
    # The recipe moves must match the derived full move sets exactly.
    by_h = {}
    for m in rec["moves"]:
        by_h.setdefault(m["h"], []).append(m)
    for h in recipe_h:
        mine = [
            (m["kind"], m["read_index"], m["target"], tuple(m["coef"])) for m in full_of[h][1]
        ]
        theirs = [
            (m["kind"], m["read_index"], m["target"], tuple(m["coef"])) for m in by_h[h]
        ]
        assert sorted(mine) == sorted(theirs), ("recipe moves differ", h)

    fulls = {h: full_of[h][1] for h in legal_full_h}
    cost_sw = floating_cost(sw)
    cost_in = floating_cost(base)
    evidence = {
        "input_sha256": sha,
        "comparison_sha256": rec["output_sha256"],
        "seed": SEED,
        "legal_full_h": legal_full_h,
        "counts": dict(counts),
    }

    rng = random.Random(SEED)
    for arity in a.arity:
        groups = list(itertools.combinations(legal_full_h, arity))
        rng.shuffle(groups)
        key = "groups_%d" % arity
        evidence[key] = []
        n_legal = 0
        examined = 0
        for g in groups:
            moves = canon([m for h in g for m in fulls[h]])
            profile, fail = ev.run(moves)
            examined += 1
            if profile is None:
                evidence[key].append({"group": list(g), "ok": False, "fail": list(fail)})
                counts["g%d_%s" % (arity, fail[0])] += 1
            else:
                n_legal += 1
                c = floating_cost(profile)
                evidence[key].append(
                    {
                        "group": list(g),
                        "ok": True,
                        "profile": profile,
                        "cost": c,
                        "cost_delta_vs_sw4": c - cost_sw,
                        "cost_delta_vs_input": c - cost_in,
                    }
                )
                counts["g%d_legal" % arity] += 1
        print(
            "ARITY",
            arity,
            "groups",
            examined,
            "legal",
            n_legal,
            "seconds",
            round(time.monotonic() - t_start, 1),
            flush=True,
        )

    evidence["counts"] = dict(counts)
    evidence["cost_sw4"] = cost_sw
    evidence["cost_input"] = cost_in
    evidence["profile_sw4"] = sw
    evidence["profile_input"] = base
    evidence["seconds"] = round(time.monotonic() - t_start, 3)
    (out / "EVIDENCE.json").write_text(
        json.dumps(evidence, indent=1) + "\n", newline="\n"
    )

    # Headline: best legal full combination vs SW4 by floating cost.
    best = None
    for arity in a.arity:
        for e in evidence["groups_%d" % arity]:
            if e["ok"] and (best is None or e["cost"] < best["cost"]):
                best = e
    report = {
        "status": "COMPLETE",
        "input_sha256": sha,
        "seed": SEED,
        "arity": a.arity,
        "counts": dict(counts),
        "cost_sw4": cost_sw,
        "cost_input": cost_in,
        "best": best,
        "seconds": evidence["seconds"],
    }
    (out / "SEARCH.json").write_text(
        json.dumps(report, indent=1) + "\n", newline="\n"
    )
    print("DONE", json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
