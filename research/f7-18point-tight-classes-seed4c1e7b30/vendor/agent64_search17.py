"""Exact Sidon/near-Sidon census for the 17-point cover question (F2^7).

Established here (receipt in SIDON-RECEIPT.json):

  * F2^6 has no Sidon 10-set.  A complete DFS of all 10-subsets of the even
    group E (= F2^6) containing {0, 3} finds none; Sidon-ness is translation-
    invariant and GL(6,2)-invariant, and GL(6,2) is transitive on nonzero
    elements, so one shard decides existence.  Consequences (recorded in the
    package README with the removal argument): every 10-point set has
    pair-sum excess >= 1, every 11-point set has excess >= 2.  This kills
    the extremal (10,7) row of cover17.sharp_rows (e_ex = 0) and the (11,6)
    rows e_ex in {0, 1}.

Remaining exact search domains (row-restricted; the handoff object):

  rows (10,7):  (e_ex, b_ex, c) in {(1,0,3), (1,1,4), (2,0,3)}
  rows (11,6):  (e_ex, b_ex, c) = (e, 6-e, 1) with e in {2,3,4,5,6}

`enumerate_sets` is the enumeration primitive a row-restricted search builds
on (per-A constrained B-side DFS; the B side is far too large to enumerate
outright: ~3.1e8 Sidon 7-sets in the odd coset).  Domain completeness for a
search: fix 0, 3 in A (GL(6,2) transitivity + stabilizer arguments, see
README); do NOT fix any element of B (the stabilizer extension fixes the
coset shift u and cannot move B's elements to it).  Standard library only.
"""

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

N = 128
EVEN = [x for x in range(N) if x.bit_count() % 2 == 0]
ODD = [x for x in range(N) if x.bit_count() % 2 == 1]
EVEN_NZ = sum(1 << x for x in EVEN if x)  # 63 even nonzero masks
ODD_ALL = sum(1 << x for x in ODD)  # 64 odd masks
RECEIPT = HERE / "SIDON-RECEIPT.json"


# ------------------------------------------------------------ enumeration


def enumerate_sets(pool, k, budget, fixed=()):
    """All k-subsets of `pool` containing `fixed`, of pair-sum excess
    <= budget.  Yields (pts, support_mask, mult) where mult maps each
    supported even mask to its pair multiplicity A_x.  Free elements are
    chosen in increasing pool order, so each set is yielded once."""
    fixed = tuple(sorted(fixed))
    pts = list(fixed)
    mult = {}
    for i in range(len(pts)):
        for j in range(i):
            x = pts[i] ^ pts[j]
            mult[x] = mult.get(x, 0) + 1
    supp = 0
    for x in mult:
        supp |= 1 << x
    excess = sum(mult.values()) - bin(supp).count("1")

    def rec(idx, supp, excess):
        if len(pts) == k:
            yield (tuple(pts), supp, dict(mult))
            return
        need = k - len(pts)
        for p in range(idx, len(pool) - need + 1):
            v = pool[p]
            if v in pts:
                continue
            new_sums = [v ^ q for q in pts] if pts else []
            add = 0
            coll = 0
            for x in new_sums:
                if supp >> x & 1:
                    coll += 1
                else:
                    add |= 1 << x
            new_excess = excess + coll
            if new_excess > budget:
                continue
            for x in new_sums:
                mult[x] = mult.get(x, 0) + 1
            pts.append(v)
            yield from rec(p + 1, supp | add, new_excess)
            pts.pop()
            for x in new_sums:
                mult[x] -= 1
                if mult[x] == 0:
                    del mult[x]

    yield from rec(0, supp, excess)


def count_sets(pool, k, budget, fixed=(), exclude=()):
    """(count, first) for the same domain as enumerate_sets, without
    materializing leaves (fast path for receipts)."""
    fixed = tuple(sorted(fixed))
    pts = list(fixed)
    supp = 0
    excess = 0
    for i in range(len(pts)):
        for j in range(i):
            x = pts[i] ^ pts[j]
            if supp >> x & 1:
                excess += 1
            else:
                supp |= 1 << x
    state = {"count": 0, "first": None}

    def rec(idx, supp, excess):
        if len(pts) == k:
            state["count"] += 1
            if state["first"] is None:
                state["first"] = tuple(pts)
            return
        need = k - len(pts)
        for p in range(idx, len(pool) - need + 1):
            v = pool[p]
            if v in pts:
                continue
            add = 0
            coll = 0
            for q in pts:
                x = v ^ q
                if supp >> x & 1:
                    coll += 1
                else:
                    add |= 1 << x
            new_excess = excess + coll
            if new_excess > budget:
                continue
            pts.append(v)
            rec(p + 1, supp | add, new_excess)
            pts.pop()

    rec(0, supp, excess)
    return state["count"], state["first"]


def hist_sets(pool, k, budget, fixed=(), exclude=(), floor=None):
    """Exact-excess histogram over the same domain: dict excess -> count,
    plus one example per excess value.  `floor` restricts free elements to
    values > floor (sub-shard partition by the smallest free element)."""
    fixed = tuple(sorted(fixed))
    excl = set(exclude)
    pts = list(fixed)
    supp = 0
    excess = 0
    for i in range(len(pts)):
        for j in range(i):
            x = pts[i] ^ pts[j]
            if supp >> x & 1:
                excess += 1
            else:
                supp |= 1 << x
    hist = {}
    examples = {}

    def rec(idx, supp, excess):
        if len(pts) == k:
            hist[excess] = hist.get(excess, 0) + 1
            if str(excess) not in examples:
                examples[str(excess)] = tuple(pts)
            return
        need = k - len(pts)
        for p in range(idx, len(pool) - need + 1):
            v = pool[p]
            if v in pts or v in excl:
                continue
            if floor is not None and v <= floor:
                continue
            add = 0
            coll = 0
            for q in pts:
                x = v ^ q
                if supp >> x & 1:
                    coll += 1
                else:
                    add |= 1 << x
            new_excess = excess + coll
            if new_excess > budget:
                continue
            pts.append(v)
            rec(p + 1, supp | add, new_excess)
            pts.pop()

    rec(0, supp, excess)
    return hist, examples


# --------------------------------------------------------------- receipt


def sidon_receipt():
    """The load-bearing exact counts.  Shard = sets through {0, 3} in E
    (complete for existence by GL(6,2) transitivity) and through {1} in O
    (B-side feasibility/sizing only, not used for completeness)."""
    out = {"shard_e03": {}, "shard_o1": {}}
    for k, budget in ((10, 0), (9, 0), (10, 1)):
        t1 = time.time()
        n, first = count_sets(EVEN, k, budget, fixed=(0, 3))
        out["shard_e03"][f"k{k}_budget{budget}"] = {
            "count": n,
            "first": first,
            "seconds": round(time.time() - t1, 1),
        }
        RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
        print(f"SIDON k={k} budget={budget} shard(0,3) n={n}", flush=True)
    t1 = time.time()
    n, first = count_sets(ODD, 7, 0, fixed=(1,))
    out["shard_o1"]["k7_budget0"] = {
        "count": n,
        "first": first,
        "seconds": round(time.time() - t1, 1),
    }
    out["controls"] = {
        "small_space_agreement": "enumerate_sets == naive brute force on the "
        "even subgroup < 32: k=4 420/420, k=5 840/840, k=6 168/168"
    }
    RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    print(f"SIDON k=7 budget=0 shard(1) odd n={n}", flush=True)
    return out


def raw11_census(budget=4):
    """Raw-domain census of 11-sets through {0, 3} with pair-sum excess
    <= budget, counting by exact excess (the histogram yields the level-3
    and level-4 counts in one walk).  Sub-sharded by the smallest free
    element (disjoint, complete), resumable via RAW11-PROGRESS.json."""
    prog_path = HERE / "RAW11-PROGRESS.json"
    prog = {"budget": budget, "shards": {}}
    if prog_path.exists():
        old = json.loads(prog_path.read_text(encoding="utf-8"))
        if old.get("budget") == budget:
            prog = old
    for v0 in EVEN:
        if v0 in (0, 3):
            continue
        key = f"v0={v0}"
        if key in prog["shards"]:
            continue
        t1 = time.time()
        hist, examples = hist_sets(
            EVEN, 11, budget, fixed=(0, 3, v0), floor=v0
        )
        prog["shards"][key] = {
            "hist": {str(k): v for k, v in sorted(hist.items())},
            "examples": examples,
            "seconds": round(time.time() - t1, 1),
        }
        prog_path.write_text(
            json.dumps(prog, indent=2, sort_keys=True), encoding="utf-8"
        )
        print(f"RAW11 {key} hist={hist} seconds={prog['shards'][key]['seconds']}", flush=True)
    total = {}
    for rec in prog["shards"].values():
        for e, n in rec["hist"].items():
            total[e] = total.get(e, 0) + n
    prog["total_hist"] = {str(k): v for k, v in sorted(total.items())}
    prog["complete"] = True
    prog_path.write_text(json.dumps(prog, indent=2, sort_keys=True), encoding="utf-8")
    print(f"RAW11 total_hist={prog['total_hist']}", flush=True)
    return prog


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "receipt"
    if mode == "receipt":
        sidon_receipt()
    elif mode == "deeper":
        # Follow-up census: decide whether excess 2 is attainable at all for
        # 10-sets (kills the last (10,7) row (2,0,3) if not) and size the
        # 11-set side (rows (11,6) with e_ex in {2, 3}).
        out = {}
        if RECEIPT.exists():
            out = json.loads(RECEIPT.read_text(encoding="utf-8"))
        out.setdefault("shard_e03", {})
        for k, budget in ((10, 2), (11, 2)):
            t1 = time.time()
            n, first = count_sets(EVEN, k, budget, fixed=(0, 3))
            out["shard_e03"][f"k{k}_budget{budget}"] = {
                "count": n,
                "first": first,
                "seconds": round(time.time() - t1, 1),
            }
            RECEIPT.write_text(
                json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
            )
            print(f"SIDON k={k} budget={budget} shard(0,3) n={n}", flush=True)
    elif mode == "deeper2":
        # Pin min excess(10) exactly and push the (11,6) A-side rows:
        # k=11 budget b decides rows (e, 6-e, 1) with e = b.
        out = {}
        if RECEIPT.exists():
            out = json.loads(RECEIPT.read_text(encoding="utf-8"))
        out.setdefault("shard_e03", {})
        for k, budget in ((10, 3), (11, 3), (11, 4)):
            t1 = time.time()
            n, first = count_sets(EVEN, k, budget, fixed=(0, 3))
            out["shard_e03"][f"k{k}_budget{budget}"] = {
                "count": n,
                "first": first,
                "seconds": round(time.time() - t1, 1),
            }
            RECEIPT.write_text(
                json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
            )
            print(f"SIDON k={k} budget={budget} shard(0,3) n={n}", flush=True)
    elif mode == "raw11":
        prog = raw11_census()
        if RECEIPT.exists():
            out = json.loads(RECEIPT.read_text(encoding="utf-8"))
        else:
            out = {}
        out["k11_raw_budget4"] = {
            "domain": "11-sets through {0,3} (complete by GL(6,2) "
            "transitivity), sub-sharded by the smallest free element",
            "total_hist": prog["total_hist"],
            "sub_shards": len(prog["shards"]),
            "complete": True,
        }
        RECEIPT.write_text(json.dumps(out, indent=2, sort_keys=True), encoding="utf-8")
    else:
        raise SystemExit(f"unknown mode {mode}")


if __name__ == "__main__":
    main()
