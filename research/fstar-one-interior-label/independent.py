#!/usr/bin/env python3
"""Reverse-order exact exclusion and direct L8 replay, no producer imports."""

import hashlib
import json
from pathlib import Path

SOURCE = "research/fstar-entry-class-scope-seed63d5f999/data/tied_min.json"
DIGEST = "670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93"


def check(ok, message):
    if not ok:
        raise ValueError(message)


def named(a, b, q):
    support = sum(2**j for j in range(3) if q[j] != 0)
    return b == support or a == b and a in (1, 2, 4)


def even(a, b):
    return sum((a >> j & 1) * (b >> j & 1) for j in range(3)) % 2 == 0


def reverse_exclusion(factors):
    n = len(factors)
    pairs = []
    for _p, q in factors:
        support = sum(2**j for j in range(3) if q[j])
        pairs.append(tuple((a, b) for a in range(1, 8) for b in range(1, 8)
                           if b | support == support and not even(a, b)
                           and named(a, b, q)))
    initial = tuple(tuple(sorted({a for a, _b in line})) for line in pairs)
    frontier = {initial}
    counts = []
    visited = 0
    for _depth in range(n):
        counts.append(len(frontier))
        visited += len(frontier)
        check(visited <= 100_000, "independent state capacity exhausted")
        following = set()
        for state in sorted(frontier):
            for last in range(n):
                if not state[last]:
                    continue
                for b in sorted({b for a, b in pairs[last] if a in state[last]}):
                    candidate = list(state)
                    candidate[last] = ()
                    valid = True
                    for t in range(n):
                        scalar = sum(factors[t][0][j] * factors[last][1][j]
                                     for j in range(3))
                        if candidate[t] and scalar == 0:
                            candidate[t] = tuple(a for a in candidate[t] if even(a, b))
                            if not candidate[t]:
                                valid = False
                                break
                    if valid:
                        following.add(tuple(candidate))
                        check(len(following) <= 100_000,
                              "independent frontier capacity")
        frontier = following
    counts.append(len(frontier))
    check(visited + len(frontier) <= 100_000, "independent state capacity exhausted")
    return ((),) * n not in frontier, counts


def direct_replay(factors, witness, exceptions):
    n = len(factors)
    check(type(witness) is list and len(witness) == n, "independent witness length")
    check(all(type(row) is list and len(row) == 3
              and all(type(x) is int for x in row) for row in witness), "triples")
    check(sorted(row[0] for row in witness) == list(range(n)), "order permutation")
    outside = 0
    for position, (t, a, b) in enumerate(witness):
        p, q = factors[t]
        check(1 <= a <= 7 and 1 <= b <= 7, "nonzero three-bit labels")
        check(all(not (a >> j & 1) or p[j] != 0 for j in range(3)), "row support")
        check(all(not (b >> j & 1) or q[j] != 0 for j in range(3)), "column support")
        check(not even(a, b), "diagonal parity")
        if not named(a, b, q):
            check(a == 7 and b in (1, 2, 4), "exceptional label class")
            outside += 1
        for s, _aa, bb in witness[position + 1:]:
            entry = sum(p[j] * factors[s][1][j] for j in range(3))
            check(entry != 0 or even(a, bb), "ordered zero-arc parity")
    check(outside == exceptions, "exact exceptional-pair count")


def main():
    package = Path(__file__).resolve().parent
    with (package.parents[1] / SOURCE).open("rb") as stream:
        payload = stream.read(4097)
    check(len(payload) <= 4096 and hashlib.sha256(payload).hexdigest() == DIGEST,
          "independent source binding")
    factors = json.loads(payload)
    with (package / "RESULT.json").open("rb") as stream:
        receipt = stream.read(2_000_001)
    check(len(receipt) <= 2_000_000, "receipt capacity")
    records = json.loads(receipt)["records"]
    check(len(records) == 12, "complete restriction count")
    for omitted, record in enumerate(records):
        indices = [t for t in range(12) if t != omitted]
        check(record["indices"] == indices and record["omitted"] == omitted,
              "restriction binding")
        sub = [factors[t] for t in indices]
        impossible, counts = reverse_exclusion(sub)
        check(impossible, "reverse Form-R exclusion failed")
        direct_replay(sub, record["extended"]["witness"], 1)
        ten = record["ten_line"]
        check(len(set(ten["indices"])) == 10
              and all(type(t) is int and 0 <= t < 11 for t in ten["indices"]),
              "ten-line subset")
        direct_replay([sub[t] for t in ten["indices"]], ten["witness"], 0)
        print("reverse", omitted, "layer_counts=" + ",".join(map(str, counts)))
    print("PASS_FSTAR_REVERSE_EXCLUSION records=12 form_r=10 one_exception=11")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit("FAIL_FSTAR_REVERSE: " + str(error)) from error
