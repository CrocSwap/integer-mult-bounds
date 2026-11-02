#!/usr/bin/env python3
"""Compare authenticated complete receipts, keyed by actual helper members.

This runs neither scientific engine and is not a third implementation.
ToikY with substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "RESULT.json": "c28cd4c7d375ea551a294d364f5b4fcf784b9bbf504dc836e46e53a0fee4f8e1",
    "FULL-CENSUS.json": "9d36dbd0889fa72e67ccbb91cd97e5d0fb2548b4f0190358d8148db4d6533718",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "Duplicate receipt key")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("Nonfinite receipt")))


def integer(value):
    require(type(value) is int and value >= 0, "Strict nonnegative integer")
    return value


def vector(value):
    require(type(value) is list and len(value) == 4, "Four rank fields required")
    return tuple(map(integer, value))


def groups(rows, label):
    answer = {}
    for row in rows:
        members = tuple(map(integer, row["members"]))
        require(members and members == tuple(sorted(set(members))), "Canonical actual members")
        key = integer(row[label])
        require(key not in answer, "Unique group identifier")
        answer[key] = members
    require(len(set(answer.values())) == len(answer) == 3, "Three distinct actual groups")
    return answer


def compute():
    payloads = {}
    for name, sha in PINS.items():
        raw = (ROOT / name).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == sha, "Receipt sha256 mismatch: " + name)
        payloads[name] = decode(raw)
    primary, independent = payloads["RESULT.json"], payloads["FULL-CENSUS.json"]
    old_groups = groups(primary["group_members"], "group")
    new_groups = groups(independent["groups"], "index")
    require(set(old_groups.values()) == set(new_groups.values()), "Exact actual-member group equality")
    old, new = Counter(), Counter()
    for row in primary["census"]["categories"]:
        key = (old_groups[row["group"]], vector(row["base_ranks"]),
               vector(row["singleton_ranks"]), vector(row["augmented_ranks"]))
        old[key] += integer(row["cut_edge_contexts"])
    for row in independent["rank_profile_distribution"]:
        profile = row["profile"]
        key = (new_groups[row["group_index"]], vector(profile["base"]),
               vector(profile["singleton"]), vector(profile["augmented"]))
        new[key] += integer(row["weighted_cases"])
    require(old == new, "Complete group-specific rank-category mismatch")
    require(primary["census"]["cuts"] == independent["cut_count"] == 14795, "Inclusive cut coverage")
    require(sum(old.values()) == independent["weighted_domain"] == 386278548, "Full weighted domain")
    positive = {key: n for key, n in old.items() if key[3][2] > max(key[1][2], key[2][2])}
    require(sum(positive.values()) == independent["positive_excess_weighted_cases"] == 24166,
            "Complete excess total")
    require(all(k[2] == (0, 0, 0, 0) and k[3][0] == k[1][0]
                and k[3][1] == k[1][1]+1 and k[3][2] == 1 for k in positive),
            "All positive cases preserve left kernel and add one right direction")
    semantic = [[list(k[0]), list(k[1]), list(k[2]), list(k[3]), n] for k, n in sorted(old.items())]
    return {"schema_version": 1, "status": "PASS_COMPLETE_SEMANTIC_CENSUS_COMPARISON",
            "receipt_sha256": PINS, "cuts": 14795, "weighted_contexts": sum(old.values()),
            "complete_rank_categories": len(old), "positive_rank_categories": len(positive),
            "positive_weighted_contexts": sum(positive.values()),
            "semantic_histogram_sha256": hashlib.sha256(canonical(semantic).encode()).hexdigest(),
            "group_sizes": sorted(map(len, old_groups.values())),
            "scope": "Exact complete rank distributions keyed by actual members; no comparison of algorithm-specific digests or independently unretained edge-class histogram."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    options = parser.parse_args()
    result = compute()
    if options.emit:
        print(canonical(result))
    else:
        require(canonical(decode((ROOT / "COMPARE.json").read_bytes())) == canonical(result), "Comparison receipt mismatch")
        print("PASS complete actual-member census comparison")
