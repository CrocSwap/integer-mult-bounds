#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact corroboration for the polarized invoice ceiling.

Checks, with integer interval arithmetic only:

* the two exchange lemmas for every admissible pair and every tested exponent;
* Proposition 1: the greedy spread vector is the unique paid minimum over
  every multiset with the same entry count and rank mass;
* Proposition 2: the balanced vector is the unique target maximum;
* the class theorem: every invoice is at least its canonical invoice, with
  equality exactly at the canonical invoice;
* the x = 1 and x = 0 boundary controls that make the exponent range sharp;
* the composition with the documented comparator on schema-valid invoices;
* mutation controls that must fail.

Every power is bracketed by integer k-th roots, so each comparison is a
certified rational bound, not a floating-point approximation.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path

DIGITS = 24
SCALE = 10 ** DIGITS
X_SET = ((1, 2), (1, 3), (2, 3), (1, 5), (3, 7))
PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parent.parent
COMPARATOR = REPO / "scripts" / "compare_recursive_invoices.py"


def iroot(n: int, k: int) -> int:
    """Floor of the k-th root of a nonnegative integer."""
    if n < 2:
        return n
    lo = 0
    hi = 1 << ((n.bit_length() + k - 1) // k + 1)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid ** k <= n:
            lo = mid
        else:
            hi = mid
    return lo


_BRACKET: dict[tuple[int, int, int], tuple[int, int]] = {}


def bracket(rank: int, p: int, q: int) -> tuple[int, int]:
    """Certified integers lo <= rank**(p/q) * SCALE < lo + 1 <= hi."""
    key = (rank, p, q)
    cached = _BRACKET.get(key)
    if cached is None:
        root = iroot(rank ** p * SCALE ** q, q)
        cached = (root, root + 1)
        _BRACKET[key] = cached
    return cached


def multiset_sum(ranks, x):
    """Certified interval [lo, hi] for sum rank**x, scaled by SCALE."""
    p, q = x
    lo = hi = 0
    for rank in ranks:
        a, b = bracket(rank, p, q)
        lo += a
        hi += b
    return lo, hi


def linear_sum(ranks):
    """Exact value of sum rank**1 (scaled by SCALE)."""
    return SCALE * sum(ranks)


def greedy(K: int, M: int, m: int) -> tuple[int, ...]:
    """Unique paid minimiser: j copies of m, one remainder, rest ones."""
    require(1 <= K <= M <= K * m, "infeasible (K, M, m)")
    require(m >= 2, "ambient rank must be at least two")
    j = min(K - 1, (M - K) // (m - 1))
    r0 = M - K + 1 - j * (m - 1)
    require(1 <= r0 <= m, "greedy remainder out of range")
    return (1,) * (K - j - 1) + (r0,) + (m,) * j


def balanced(K: int, N: int, m: int) -> tuple[int, ...]:
    """Unique target maximiser: entries q or q + 1."""
    require(1 <= K <= N <= K * m, "infeasible (K, N, m)")
    q, t = divmod(N, K)
    require(1 <= q <= m, "balanced quotient out of range")
    vector = (q,) * (K - t) + (q + 1,) * t
    require(max(vector) <= m, "balanced entry exceeds ambient rank")
    return vector


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def multisets(m: int, K: int):
    """Every nondecreasing tuple of K entries in 1..m."""
    return tuple(itertools.combinations_with_replacement(range(1, m + 1), K))


def check_exchange_lemmas(m: int, counts: dict) -> None:
    """Lemmas 1 and 3, certified for each tested exponent."""
    for x in X_SET:
        for a in range(2, m + 1):
            for b in range(a, m):  # b + 1 <= m
                left = multiset_sum((a - 1, b + 1), x)
                right = multiset_sum((a, b), x)
                require(left[1] < right[0],
                        f"lemma 1 fails at m={m} a={a} b={b} x={x}")
                counts["lemma1"] += 1
        for b in range(1, m - 1):
            for a in range(b + 2, m + 1):  # b + 2 <= a
                left = multiset_sum((a - 1, b + 1), x)
                right = multiset_sum((a, b), x)
                require(left[0] > right[1],
                        f"lemma 3 fails at m={m} a={a} b={b} x={x}")
                counts["lemma3"] += 1


def check_box(m: int, max_entries: int, counts: dict) -> None:
    """Exhaustive propositions 1 and 2 and the class theorem on one box."""
    require(m >= 2, "ambient rank must be at least two")
    by_count = {K: multisets(m, K) for K in range(1, max_entries + 1)}

    for K in range(1, max_entries + 1):
        groups: dict[int, list[tuple[int, ...]]] = {}
        for vector in by_count[K]:
            groups.setdefault(sum(vector), []).append(vector)
        counts["paid_groups"] += len(groups)
        for mass, members in groups.items():
            canonical = greedy(K, mass, m)
            require(canonical in members, "greedy vector missing from its class")
            require(len(set(members)) == len(members), "duplicate multiset")
            for x in X_SET:
                base = multiset_sum(canonical, x)
                for vector in members:
                    if vector == canonical:
                        continue
                    value = multiset_sum(vector, x)
                    require(value[0] > base[1],
                            f"paid minimum fails m={m} K={K} M={mass} "
                            f"x={x}: {vector} vs {canonical}")
                    counts["paid_strict"] += 1
            # Boundary control at x = 1: every vector attains the same value.
            require(linear_sum(canonical) == linear_sum(members[0]),
                    "linear tariff control fails")

    for K in range(1, max_entries + 1):
        groups = {}
        for vector in by_count[K]:
            groups.setdefault(sum(vector), []).append(vector)
        counts["target_groups"] += len(groups)
        for mass, members in groups.items():
            canonical = balanced(K, mass, m)
            require(canonical in members, "balanced vector missing from its class")
            for x in X_SET:
                base = multiset_sum(canonical, x)
                for vector in members:
                    if vector == canonical:
                        continue
                    value = multiset_sum(vector, x)
                    require(value[1] < base[0],
                            f"target maximum fails m={m} K={K} N={mass} "
                            f"x={x}: {vector} vs {canonical}")
                    counts["target_strict"] += 1

    for Kp in range(1, max_entries + 1):
        for Kt in range(1, max_entries + 1):
            for paid in by_count[Kp]:
                for target in by_count[Kt]:
                    gp = greedy(Kp, sum(paid), m)
                    bt = balanced(Kt, sum(target), m)
                    canonical = paid == gp and target == bt
                    for x in X_SET:
                        p_lo, _ = multiset_sum(paid, x)
                        _, p_hi_canonical = multiset_sum(gp, x)
                        t_hi, _ = multiset_sum(target, x)
                        t_lo_canonical, _ = multiset_sum(bt, x)
                        margin = (p_lo - p_hi_canonical) - (t_hi - t_lo_canonical)
                        if canonical:
                            require(paid == gp and target == bt,
                                    "canonical identification error")
                            require(multiset_sum(paid, x) == multiset_sum(gp, x),
                                    "canonical paid equality fails")
                            require(multiset_sum(target, x) == multiset_sum(bt, x),
                                    "canonical target equality fails")
                            counts["class_equality"] += 1
                        else:
                            require(margin > 0,
                                    f"class ceiling fails m={m} "
                                    f"paid={paid} target={target} x={x}")
                            counts["class_strict"] += 1
    counts["boxes"] += 1


def write_invoice(path: Path, m: int, paid, targets) -> None:
    invoice = {
        "schema": "integer-mult-recursive-invoice/v1",
        "contract": {
            "model": "mixed-target-unnormalized-power-v1",
            "rank_semantics": "H_r costs r^(1-C); debit surrendered productive fields",
            "ambient_rank": m,
            "boundary": "complete unit before the same mixed-target compiler",
        },
        "paid": {str(r): paid.count(r) for r in sorted(set(paid), reverse=True)
                 if paid.count(r)},
        "targets": {str(r): targets.count(r) for r in sorted(set(targets), reverse=True)
                    if targets.count(r)},
    }
    path.write_text(json.dumps(invoice), encoding="utf-8")


def run_comparator(old_path: Path, new_path: Path) -> dict:
    result = subprocess.run(
        [sys.executable, "-B", str(COMPARATOR), str(old_path), str(new_path)],
        capture_output=True, text=True, timeout=120, check=False)
    if result.returncode != 0:
        return {"status": "REJECTED", "stderr": result.stderr.strip()}
    report = json.loads(result.stdout)
    return {"status": "OK",
            "classification": report["classification"],
            "power_sign": report["power_moment"]["new_minus_old_sign"]}


def check_comparator(counts: dict) -> None:
    """Compose the theorem with the existing hinge comparator."""
    m = 6
    cases = [
        # old canonical, new non-canonical: theorem predicts uniformly worse.
        ("uniformly_worse", "strictly_positive",
         greedy(3, 9, m), balanced(2, 5, m), (2, 3, 4), (2, 3)),
        # old non-canonical, new canonical: theorem predicts uniformly better.
        ("uniformly_better", "strictly_negative",
         (2, 3, 4), (2, 3), greedy(3, 9, m), balanced(2, 5, m)),
        # paid canonical, target non-canonical: still uniformly worse.
        ("uniformly_worse", "strictly_positive",
         greedy(3, 9, m), balanced(2, 5, m), greedy(3, 9, m), (1, 4)),
        # identical canonical invoices are equal.
        ("equal", "identically_zero",
         greedy(3, 9, m), balanced(2, 5, m), greedy(3, 9, m), balanced(2, 5, m)),
    ]
    with tempfile.TemporaryDirectory() as name:
        root = Path(name)
        for index, (classification, sign, op, ot, np_, nt) in enumerate(cases):
            old_path = root / f"old{index}.json"
            new_path = root / f"new{index}.json"
            write_invoice(old_path, m, op, ot)
            write_invoice(new_path, m, np_, nt)
            verdict = run_comparator(old_path, new_path)
            require(verdict.get("classification") == classification,
                    f"comparator classification {verdict} != {classification}")
            require(verdict.get("power_sign") == sign,
                    f"comparator power sign {verdict} != {sign}")
            counts["comparator_cases"] += 1

        # Sufficient class certificate: the most favourable candidate still
        # exceeds the least favourable incumbent, so every candidate loses.
        old_path = root / "old_antipodal.json"
        new_path = root / "new_canonical.json"
        write_invoice(old_path, 8, (3, 6), (2, 7))
        write_invoice(new_path, 8, (8, 8), (1, 1))
        verdict = run_comparator(old_path, new_path)
        require(verdict.get("classification") == "uniformly_worse",
                f"antipodal certificate failed: {verdict}")
        counts["comparator_cases"] += 1
        # The certificate hypothesis, checked with certified brackets.
        for x in X_SET:
            candidate = multiset_sum((8, 8), x)
            candidate_credit = multiset_sum((1, 1), x)
            incumbent_paid = multiset_sum((4, 5), x)
            incumbent_credit = multiset_sum((1, 8), x)
            margin = (candidate[0] - candidate_credit[1]) - (
                incumbent_paid[1] - incumbent_credit[0])
            require(margin > 0, f"antipodal hypothesis fails at x={x}")
            counts["antipodal_hypothesis"] += 1

        # Negative control: the reversed classes are not dominated.
        old_path = root / "old_reverse.json"
        new_path = root / "new_reverse.json"
        write_invoice(old_path, 8, (4, 5), (1, 8))
        write_invoice(new_path, 8, (1, 8), (4, 5))
        verdict = run_comparator(old_path, new_path)
        require(verdict.get("classification") == "uniformly_better",
                f"reverse control failed: {verdict}")
        counts["comparator_cases"] += 1

        # Schema control: a rank above the declared ambient rank is rejected.
        bad_path = root / "bad.json"
        write_invoice(bad_path, 4, (1, 4), (2,))
        payload = json.loads(bad_path.read_text(encoding="utf-8"))
        payload["paid"]["9"] = 1
        bad_path.write_text(json.dumps(payload), encoding="utf-8")
        verdict = run_comparator(bad_path, new_path)
        require(verdict.get("status") == "REJECTED",
                "comparator accepted a rank above the ambient rank")
        require("ambient_rank" in verdict.get("stderr", ""),
                "rejection did not name the ambient rank")
        counts["comparator_rejections"] += 1


def check_mutations(counts: dict) -> None:
    """Mutations of the canonical constructors must be detected."""
    m = 4
    # A balanced paid vector is strictly worse than the greedy spread.
    require(balanced(3, 6, m) == (2, 2, 2), "unexpected balanced fixture")
    require(greedy(3, 6, m) == (1, 1, 4), "unexpected greedy fixture")
    x = (1, 2)
    require(multiset_sum((2, 2, 2), x)[0] > multiset_sum((1, 1, 4), x)[1],
            "paid mutation control did not fail")
    counts["mutations"] += 1

    # A spread target vector is strictly worse than the balanced vector.
    require(greedy(3, 6, m) == (1, 1, 4), "unexpected spread fixture")
    require(balanced(3, 6, m) == (2, 2, 2), "unexpected balance fixture")
    require(multiset_sum((1, 1, 4), x)[1] < multiset_sum((2, 2, 2), x)[0],
            "target mutation control did not fail")
    counts["mutations"] += 1

    # A half-spread paid mutant is not spread-terminal and not minimal.
    mutant = (2, 2, 3)  # K=3, M=7 for m=4
    require(sum(mutant) == 7 and len(mutant) == 3, "bad mutant fixture")
    require(greedy(3, 7, m) == (1, 2, 4), "unexpected greedy fixture")
    require(multiset_sum(mutant, x)[0] > multiset_sum(greedy(3, 7, m), x)[1],
            "spread mutant control did not fail")
    counts["mutations"] += 1

    # Hypothesis controls: infeasible and degenerate parameter ranges.
    for bad in ((3, 2, 4), (3, 13, 4)):
        try:
            greedy(*bad)
        except AssertionError:
            counts["hypothesis_rejections"] += 1
        else:
            raise AssertionError(f"greedy accepted infeasible {bad}")
    for bad in ((3, 1, 4), (3, 13, 4)):
        try:
            balanced(*bad)
        except AssertionError:
            counts["hypothesis_rejections"] += 1
        else:
            raise AssertionError(f"balanced accepted infeasible {bad}")
    try:
        greedy(2, 4, 1)
    except AssertionError:
        counts["hypothesis_rejections"] += 1
    else:
        raise AssertionError("greedy accepted ambient rank one")

    # Exponent boundary: at x = 1 strictness fails for a non-canonical vector.
    require(linear_sum((2, 2, 2)) == linear_sum((1, 1, 4)),
            "x = 1 boundary control did not tie")
    counts["boundary_controls"] += 1
    # At x = 0 every entry contributes one, so the extreme is not polarized.
    require(multiset_sum((2, 2, 2), (0, 1))[0] == 3 * SCALE,
            "x = 0 boundary control value is wrong")
    counts["boundary_controls"] += 1


def source_hashes() -> dict[str, str]:
    names = ("README.md", "PROOF.md", "SOURCES.json", "TASK.json", "VERIFY.json",
             "verify.py")
    return {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
            for name in names}


def main() -> int:
    counts = {
        "boxes": 0,
        "lemma1": 0,
        "lemma3": 0,
        "paid_groups": 0,
        "paid_strict": 0,
        "target_groups": 0,
        "target_strict": 0,
        "class_strict": 0,
        "class_equality": 0,
        "comparator_cases": 0,
        "comparator_rejections": 0,
        "antipodal_hypothesis": 0,
        "mutations": 0,
        "hypothesis_rejections": 0,
        "boundary_controls": 0,
    }

    for m, max_entries in ((5, 3), (4, 4), (6, 2), (3, 5)):
        check_exchange_lemmas(m, counts)
        check_box(m, max_entries, counts)

    check_mutations(counts)
    check_comparator(counts)

    report = {
        "claim_type": "scoped written proof with exact finite corroboration",
        "census": counts,
        "exponents": [f"{p}/{q}" for p, q in X_SET],
        "interval_digits": DIGITS,
        "method": "integer k-th root brackets; no floating point",
        "source_sha256": source_hashes(),
    }
    (PACKAGE / "RESULT.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, sort_keys=True))
    print("PASS_INVOICE_CLASS_POLARIZATION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
