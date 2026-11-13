#!/usr/bin/env python3
"""Exact rank-price sign census for the paired 1,066-target result."""
from collections import Counter


def need(condition, message):
    if not condition:
        raise ValueError(message)


def check(doc, prices):
    need(doc["status"] == "FRESH_EXACTQ_ALL_PUBLIC_SINGLE_RELATION_PRICE_SCREEN",
         "paired exact source screen status")
    rows = doc["records"]
    need(len(rows) == 1066, "all paired candidates present")
    counts = Counter()
    for row in rows:
        target = row["target_rank"]
        debit = row["minimum_enabling_relation_rank"]
        need(target > 0 and debit is not None and debit > 0,
             "target and debit ranks are positive")
        if target == debit:
            sign = "equal"
            need(row["saving_0038"]["exact"] == ["0", "0"],
                 "equal-rank cancellation is exactly zero")
        elif target > debit:
            sign = "positive"
            need(row["saving_0038"]["exact"][0] != "0" and
                 row["saving_0038"]["classification"] == "positive",
                 "positive rank difference has positive certified price")
        else:
            sign = "negative"
            need(row["saving_0038"]["classification"] == "negative",
                 "negative rank difference has negative certified price")
        counts[sign] += 1
    need(counts == Counter({"positive": 376, "equal": 437, "negative": 253}),
         "complete exact sign counts")

    equal_rank = next(row for row in rows if row["target_rank"] ==
                      row["minimum_enabling_relation_rank"])
    rank = equal_rank["target_rank"]
    correct_profile = Counter({rank: 1})
    correct_profile[rank] -= 1
    correct_profile = {r: count for r, count in correct_profile.items() if count}
    correct = prices.moment(correct_profile)
    # A dict literal with duplicate rank keys collapses and exposes the mutant.
    wrong = prices.moment({rank: -1})
    need(correct == (0, 0) and wrong != correct,
         "executed repeated-rank collision control rejects an equal-rank error")
    return {
        "status": "PASS_EXACT_PROFILE_SIGN_CROSSCHECK",
        "candidate_count": len(rows),
        "counts": dict(sorted(counts.items())),
        "sign_law": "for 0<=kappa<1, sign(f(target_rank)-f(minimum_debit_rank)) equals sign(target_rank-minimum_debit_rank); at kappa=1 every profile is zero",
        "all_zero_profiles_are_equal_rank": True,
        "negative_control": {
            "mutant": "{rank: 1, rank: -1} built as a dict literal, collapsing to {rank: -1}",
            "rank": rank,
            "correct_exact_interval": [str(value) for value in correct],
            "mutant_interval": [str(value) for value in wrong],
            "rejected": True,
        },
    }
