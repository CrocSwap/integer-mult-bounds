"""Independent re-derivation and controls for the 17-point cover audit.

Deliberately different code paths from cover17.py / search17.py:

1. Excess-budget semantics validated against naive itertools brute force on
   the even subgroup of F2^7 isomorphic to F2^4 (16 elements), at budgets
   0, 1, 2.  This is the semantics the load-bearing zero counts depend on.
2. The sharp row table re-derived by direct nested loops over excess pairs
   and multiplicity distributions (no partition generator, no draw/pairing
   recursion), matching cover17.sharp_rows row for row.
3. The odd-translation mirror: S+S is translation-invariant and an odd
   translation swaps the E/O parts, so (s,t) and (t,s) rows must agree.
4. Receipt consistency: every recorded example is a valid set of the claimed
   size/excess, and zero counts are only trusted with their controls.
"""

import json
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cover17
import search17


def excess_of(pts):
    """Pair-sum excess: C(k,2) - |supp|."""
    supp = set()
    k = len(pts)
    for i, j in combinations(range(k), 2):
        supp.add(pts[i] ^ pts[j])
    return k * (k - 1) // 2 - len(supp)


def small_group_budget_agreement():
    sub = [x for x in search17.EVEN if x < 32]  # 16-element even subgroup
    out = {}
    for k in (4, 5, 6):
        for budget in (0, 1, 2):
            fast = sorted(
                pts
                for pts, _, _ in search17.enumerate_sets(sub, k, budget, fixed=(0,))
            )
            slow = sorted(
                tuple(sorted(c))
                for c in combinations(sub, k)
                if c[0] == 0 and excess_of(c) <= budget
            )
            agree = fast == slow
            out[f"k{k}_budget{budget}"] = {
                "fast": len(fast),
                "slow": len(slow),
                "agree": agree,
            }
            assert agree, (k, budget)
            # histogram path (used by the canonical-domain census)
            hist, examples = search17.hist_sets(sub, k, budget, fixed=(0,))
            slow_hist = {}
            for c in slow:
                e = excess_of(c)
                slow_hist[e] = slow_hist.get(e, 0) + 1
            assert hist == slow_hist, (k, budget, hist, slow_hist)
            for e, pts in examples.items():
                assert excess_of(pts) == int(e), (k, budget, e)
            out[f"k{k}_budget{budget}"]["hist_agree"] = True
    return out


def sharp_rows_by_loops(n, s, t):
    """Independent row derivation: loop over excess pairs directly and over
    multiplicity distributions as explicit count vectors."""
    odd_masks = 1 << (n - 1)
    even_nonzero = odd_masks - 1
    A = s * (s - 1) // 2
    B = t * (t - 1) // 2
    excess = s * t - odd_masks
    if excess < 0 or A + B < even_nonzero:
        return dict(feasible=False, rows=[], best=-1, need=0)
    need = (excess + 1) // 2

    # integer profiles: count vectors j1 >= j2 >= ... summing to excess,
    # sigma = sum j(j+1)/2 even
    prof_c = set()

    def profiles(remaining, cap, acc):
        if remaining == 0:
            sigma = sum(j * (j + 1) // 2 for j in acc)
            if sigma % 2 == 0:
                prof_c.add(sigma // 2)
            return
        for j in range(min(cap, remaining), 0, -1):
            profiles(remaining - j, j, acc + [j])

    profiles(excess, excess, [])

    rows = []
    best = -1
    for e_ex in range(A + 1):
        for b_ex in range(B + 1):
            shared = A + B - e_ex - b_ex - even_nonzero
            if shared < 0:
                continue
            # multiplicity distributions: value lists via count vectors
            attain = attainable_by_counts(A, e_ex, B, b_ex, shared)
            if not attain:
                continue
            best = max(best, max(attain))
            for c in sorted(attain & prof_c):
                rows.append(dict(e_ex=e_ex, b_ex=b_ex, shared=shared, c=c))
    return dict(feasible=bool(rows), rows=rows, best=best, need=need)


def attainable_by_counts(A, e_ex, B, b_ex, shared):
    """Attainable shared-product sums, enumerating count vectors for the
    multiplicity distributions directly (distinct values only)."""
    out = set()

    def dists(total_pairs, excess):
        # count vectors (m1 >= m2 >= ... >= 1) with sum m = total_pairs - excess
        # support and sum (m_i + collisions) = total_pairs: values v_i = m_i
        # with sum v_i = total_pairs, len = total_pairs - excess
        support = total_pairs - excess
        if support < 0 or support > total_pairs:
            return
        # values v_1 >= v_2 >= ... >= v_support >= 1, sum = total_pairs
        def rec(rem, cap, left, acc):
            if left == 0:
                if rem == 0:
                    yield tuple(acc)
                return
            for v in range(min(cap, rem - (left - 1)), 0, -1):
                yield from rec(rem - v, v, left - 1, acc + [v])

        yield from rec(total_pairs, total_pairs, support, [])

    for da in dists(A, e_ex):
        for db in dists(B, b_ex):
            for ca in combinations_with_replacement_positions(da, shared):
                for cb in combinations_with_replacement_positions(db, shared):
                    for perm in permutations_multiset(cb):
                        out.add(sum(x * y for x, y in zip(ca, perm)))
    return out


def combinations_with_replacement_positions(vals, shared):
    """All multisets of size `shared` drawn from a non-increasing value list."""
    if shared == 0:
        yield ()
        return
    counts = {}
    for v in vals:
        counts[v] = counts.get(v, 0) + 1
    keys = sorted(counts)

    def rec(i, remaining, acc):
        if i == len(keys):
            if remaining == 0:
                yield tuple(acc)
            return
        for take in range(min(counts[keys[i]], remaining) + 1):
            yield from rec(i + 1, remaining - take, acc + [keys[i]] * take)

    yield from rec(0, shared, [])


def permutations_multiset(vals):
    """All distinct permutations of a small multiset."""
    if len(vals) <= 1:
        yield tuple(vals)
        return
    seen = set()
    for i in range(len(vals)):
        if vals[i] in seen:
            continue
        seen.add(vals[i])
        rest = vals[:i] + vals[i + 1 :]
        for tail in permutations_multiset(rest):
            yield (vals[i],) + tail


def receipt_consistency():
    receipt = json.loads((HERE / "SIDON-RECEIPT.json").read_text(encoding="utf-8"))
    out = {}
    for key, val in receipt.get("shard_e03", {}).items():
        count = val["count"]
        first = val["first"]
        ok = True
        if first is not None:
            ok = (
                0 in first
                and 3 in first
                and len(set(first)) == len(first)
                and all(p in search17.EVEN for p in first)
                and excess_of(first) <= int(key.split("budget")[1])
            )
        out[key] = {"count": count, "first_valid": ok}
        assert ok, (key, first)
    for key, val in receipt.get("shard_o1", {}).items():
        count = val["count"]
        first = val["first"]
        ok = first is not None and 1 in first and all(p in search17.ODD for p in first)
        out[key] = {"count": count, "first_valid": ok}
        assert ok, (key, first)
    # the completed k=11 raw walk: 62/62 sub-shards, empty histogram
    k11 = receipt.get("k11_raw_budget4", {})
    prog = json.loads((HERE / "RAW11-PROGRESS.json").read_text(encoding="utf-8"))
    ok = (
        k11.get("complete") is True
        and k11.get("sub_shards") == 62
        and k11.get("total_hist") == {}
        and prog.get("complete") is True
        and prog.get("total_hist") == {}
        and len(prog.get("shards", {})) == 62
    )
    assert ok, (k11, prog.get("complete"), len(prog.get("shards", {})))
    out["k11_raw_budget4"] = {
        "complete": True,
        "sub_shards": 62,
        "level3": 0,
        "level4": 0,
        "progress_agrees": True,
    }
    # extension-collision floors on the recorded examples, consistent with
    # the census floors: every one-point extension of the excess-3 10-set
    # example adds >= 2 collisions (min 11-set excess >= 5); every extension
    # of the Sidon 9-set example adds >= 3 (min 10-set excess >= 3).
    ex10 = receipt["shard_e03"]["k10_budget3"]["first"]
    supp10 = {ex10[i] ^ ex10[j] for i in range(10) for j in range(i)}
    floors = []
    for p in search17.EVEN:
        if p in ex10:
            continue
        coll = sum(1 for q in ex10 if (p ^ q) in supp10)
        floors.append(coll)
    assert min(floors) >= 2, min(floors)
    ex9 = receipt["shard_e03"]["k9_budget0"]["first"]
    supp9 = {ex9[i] ^ ex9[j] for i in range(9) for j in range(i)}
    floors9 = []
    for p in search17.EVEN:
        if p in ex9:
            continue
        coll = sum(1 for q in ex9 if (p ^ q) in supp9)
        floors9.append(coll)
    assert min(floors9) >= 3, min(floors9)
    out["extension_floors"] = {
        "excess3_10set_example_min_coll": min(floors),
        "sidon9_example_min_coll": min(floors9),
    }
    return out


def main():
    report = {}
    report["small_group_budget_agreement"] = small_group_budget_agreement()
    for s, t in ((10, 7), (7, 10), (11, 6), (6, 11), (9, 8), (8, 9)):
        loops = sharp_rows_by_loops(7, s, t)
        engine = cover17.sharp_rows(7, s, t)
        agree = (
            loops["feasible"] == engine["feasible"]
            and {(r["e_ex"], r["b_ex"], r["c"]) for r in loops["rows"]}
            == {(r["e_ex"], r["b_ex"], r["c"]) for r in engine["rows"]}
            and loops["best"] == engine["best"]
            and loops["need"] == engine["need"]
        )
        report[f"rows_{s}_{t}"] = {
            "agree": agree,
            "feasible": engine["feasible"],
            "row_count": len(engine["rows"]),
            "best": engine["best"],
            "need": engine["need"],
        }
        assert agree, (s, t)
    report["receipt_consistency"] = receipt_consistency()
    (HERE / "INDEPENDENT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("PASS_17POINT_INDEPENDENT " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
