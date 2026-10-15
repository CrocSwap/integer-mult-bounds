#!/usr/bin/env python3
"""All-positive-price five-source connector theorem: exact finite evidence.

Prepared for adamgall with substantial OpenAI Codex assistance. Apache-2.0.
The arbitrary-length reduction is proved in README.md; no predecessor code import.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ELIGIBLE_MASKS = tuple(m for m in range(1, 32) if m.bit_count() in (3, 5))
BASE = (2,) * 36


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def authenticate():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        payload = (ROOT / item["path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == item["sha256"],
                "source SHA256 mismatch: " + item["path"])
        obj = b"blob " + str(len(payload)).encode() + b"\0" + payload
        require(hashlib.sha1(obj).hexdigest() == item["git_blob"],
                "source Git blob mismatch: " + item["path"])
    selection = json.loads((HERE / "SELECTION.json").read_text())
    require(selection["seed"] == "9c083f6b391fc18192cb0990085ca4ed",
            "independent selection seed")
    require(selection["base_commit"] == manifest["base_commit"], "selection base")
    return manifest


def source_words():
    """Restricted-growth words: exactly two events per label, labels by first use."""
    def visit(word, counts):
        if len(word) == 10:
            yield tuple(word)
            return
        for j, count in enumerate(counts):
            if count == 1:
                counts[j] = 2
                word.append(j)
                yield from visit(word, counts)
                word.pop()
                counts[j] = 1
        if len(counts) < 5:
            word.append(len(counts))
            counts.append(1)
            yield from visit(word, counts)
            counts.pop()
            word.pop()
    yield from visit([], [])


def prefixes(word):
    values = [0]
    for j in word:
        values.append(values[-1] ^ (1 << j))
    return values


def minimum_readouts(word):
    """Shortest paths on (connector-dirt parity, source coefficient mask)."""
    available = sorted(set(prefixes(word)))
    distances = [None] * 64
    distances[0] = 0
    queue = deque([0])
    while queue:
        state = queue.popleft()
        for value in available:
            other = state ^ (32 | value)
            if distances[other] is None:
                distances[other] = distances[state] + 1
                queue.append(other)
    require(all(value is not None for value in distances), "readout span incomplete")
    return tuple(distances[m] for m in range(1, 32))


def independent_census():
    """Pair endpoints, derive active intervals, then enumerate readout subsets.

    Does not call source_words, prefixes, or the shortest-path engine. Repeating
    a prefix value twice cancels, so subset enumeration is an exact oracle.
    """
    def match(remaining, pairs):
        if not remaining:
            yield tuple(pairs)
            return
        first, *rest = remaining
        for second in rest:
            yield from match(tuple(x for x in rest if x != second),
                             pairs + [(first, second)])

    rows = {}
    for pairs in match(tuple(range(10)), []):
        ordered = sorted(pairs)
        word = [None] * 10
        for label, (left, right) in enumerate(ordered):
            word[left] = word[right] = label
        boundary_values = sorted({sum(1 << label for label, (left, right)
                                      in enumerate(ordered) if left < cut <= right)
                                  for cut in range(11)})
        costs = [100] * 32
        subset_xor = [0] * (1 << len(boundary_values))
        for subset in range(1 << len(boundary_values)):
            if subset:
                low = subset & -subset
                subset_xor[subset] = (subset_xor[subset ^ low]
                                      ^ boundary_values[low.bit_length() - 1])
            count = subset.bit_count()
            if count % 2 == 0:
                mask = subset_xor[subset]
                costs[mask] = min(costs[mask], count)
        require(max(costs) < 100, "independent readout span incomplete")
        require(tuple(word) not in rows, "duplicate independent pairing")
        rows[tuple(word)] = tuple(costs[1:])
    return rows


def readout_slots(word, mask):
    values = prefixes(word)
    for count in range(2, len(values) + 1, 2):
        for slots in itertools.combinations(range(len(values)), count):
            result = 0
            for slot in slots:
                result ^= values[slot]
            if result == mask:
                return list(slots)
    raise ValueError("no readout representation")


def plan(word):
    slots = [readout_slots(word, mask) for mask in range(1, 32)]
    events = []
    for boundary in range(len(word) + 1):
        for mask, locations in enumerate(slots, 1):
            if boundary in locations:
                events.append(["A", mask])
        if boundary < len(word):
            events.append(["B", word[boundary]])
    return {"source_word": list(word), "readout_slots": slots, "events": events}


def profile(events):
    counts = [0] * 36
    for kind, index in events:
        require(kind in ("A", "B"), "unknown complete call")
        require((kind == "B" and 0 <= index < 5)
                or (kind == "A" and 1 <= index <= 31), "invalid call port")
        counts[index if kind == "B" else index + 4] += 1
    return tuple(counts)


def symbolic_endpoint(events):
    """Formal source products and dirt; no cleanliness assumptions."""
    z = 1 << 5
    outputs = [1 << (6 + i) for i in range(31)]
    profile(events)
    for kind, index in events:
        if kind == "B":
            z ^= 1 << index
        else:
            outputs[index - 1] ^= z
    require(z == 1 << 5, "connector not restored")
    require(outputs == [(1 << (5 + mask)) | mask for mask in range(1, 32)],
            "dirty output endpoint mismatch")


def all_witnesses(rows, source_fixture):
    witnesses = []
    for target in range(5):
        rename = list(range(5))
        rename[2], rename[target] = rename[target], rename[2]
        word = tuple(rename[j] for j in source_fixture)
        witnesses.append({"extra": ["B", target], **plan(word)})
    singletons = {}
    for word, costs in sorted(rows.items()):
        missing = [m for m, cost in enumerate(costs, 1) if cost > 2]
        if len(missing) == 1 and costs[missing[0] - 1] == 4:
            singletons.setdefault(missing[0].bit_count(), (word, missing[0]))
    require(set(singletons) == {3, 5}, "both missing-mask weight orbits needed")
    for target in ELIGIBLE_MASKS:
        word, missing = singletons[target.bit_count()]
        old_in = [j for j in range(5) if missing >> j & 1]
        old_out = [j for j in range(5) if not (missing >> j & 1)]
        new_in = [j for j in range(5) if target >> j & 1]
        new_out = [j for j in range(5) if not (target >> j & 1)]
        rename = dict(zip(old_in + old_out, new_in + new_out))
        witnesses.append({"extra": ["A", target],
                          **plan(tuple(rename[j] for j in word))})
    for witness in witnesses:
        expected = list(BASE)
        kind, index = witness["extra"]
        expected[index if kind == "B" else index + 4] += 2
        require(profile(witness["events"]) == tuple(expected), "witness call profile")
        symbolic_endpoint(witness["events"])
    return witnesses


def optimum(prices):
    """Exact complete-map tariff; all 36 prices must be positive exact numbers."""
    require(len(prices) == 36, "36 prices required")
    require(all(isinstance(p, (int, Fraction)) and not isinstance(p, bool) and p > 0
                for p in prices), "positive exact prices required")
    eligible = tuple(range(5)) + tuple(m + 4 for m in ELIGIBLE_MASKS)
    best = min(eligible, key=lambda index: (prices[index], index))
    return 2 * sum(prices) + 2 * prices[best], best


def dense_map(matrix, vector):
    return sum(((row & vector).bit_count() & 1) << i
               for i, row in enumerate(matrix))


def dense_replay(events, state, a_maps, b_maps):
    result = list(state)
    for kind, index in events:
        if kind == "B":
            result[5] ^= dense_map(b_maps[index], result[index])
        else:
            result[5 + index] ^= dense_map(a_maps[index - 1], result[5])
    return result


def dense_checks(witnesses):
    checks = 0
    noncommuting = False
    singular = False
    for width in (1, 2, 3):
        full = (1 << width) - 1
        maps = [tuple(((11 * k + 7 * i + (k >> (i % 3))) ^ (k * (i + 1))) & full
                      for i in range(width)) for k in range(36)]
        # Fix explicit singular/noncommuting matrices at width 2 and 3.
        if width > 1:
            maps[0] = tuple([3, 2] + ([4] if width == 3 else []))
            maps[1] = tuple([1, 3] + ([4] if width == 3 else []))
            maps[2] = (0,) * width
            noncommuting |= any(dense_map(maps[0], dense_map(maps[1], x))
                                != dense_map(maps[1], dense_map(maps[0], x))
                                for x in range(1 << width))
            singular |= maps[2] == (0,) * width
        b_maps, a_maps = maps[:5], maps[5:]
        for witness in witnesses:
            events = witness["events"]
            for column in range(37 * width):
                state = [0] * 37
                state[column // width] = 1 << (column % width)
                expected = list(state)
                for mask in range(1, 32):
                    payload = 0
                    for j in range(5):
                        if mask >> j & 1:
                            payload ^= dense_map(b_maps[j], state[j])
                    expected[5 + mask] ^= dense_map(a_maps[mask - 1], payload)
                actual = dense_replay(events, state, a_maps, b_maps)
                require(actual == expected, "dense dirty basis endpoint")
                require(dense_replay(list(reversed(events)), actual, a_maps, b_maps)
                        == state, "dense literal inverse")
                checks += 1
    require(noncommuting and singular, "dense fixture coverage")
    return checks


def semantic_controls(witnesses, rows):
    rejected = []

    def reject(name, callback):
        try:
            callback()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError("control accepted: " + name)

    base = witnesses[5]["events"]
    omit_b = next(i for i, event in enumerate(base) if event[0] == "B")
    reject("omitted source restoration", lambda: symbolic_endpoint(base[:omit_b] + base[omit_b + 1:]))
    extra_mask = witnesses[5]["extra"][1]
    positions = [i for i, event in enumerate(base) if event == ["A", extra_mask]]
    reject("four readouts truncated to two", lambda: symbolic_endpoint(
        [event for i, event in enumerate(base) if i not in positions[:2]]))
    moved = [list(event) for event in base]
    moved[positions[0]][1] = extra_mask ^ 1
    reject("wrong readout destination", lambda: symbolic_endpoint(moved))
    require(any(6 in costs for costs in rows.values()), "six-readout control absent")
    reject("readout oracle capped at four", lambda: require(
        all(max(costs) <= 4 for costs in rows.values()), "six readouts required"))
    prices = [10] * 36
    prices[4 + 3] = 1  # A_3 is even-weight and cannot absorb the surcharge alone.
    value, _ = optimum(prices)
    reject("all outputs eligible for cheapest surcharge", lambda: require(
        value == 2 * sum(prices) + 2 * min(prices), "cheap even mask cannot repair"))
    prices = [10] * 36
    prices[4 + 31] = 1
    value, _ = optimum(prices)
    reject("weight-five mask omitted", lambda: require(
        value == 2 * sum(prices) + 2 * min(prices[i] for i in
        (*range(5), *(m + 4 for m in ELIGIBLE_MASKS if m != 31))), "full mask can repair"))
    reject("unpaid repeat pair", lambda: require(sum(profile(base)) == 72, "complete bill is74"))
    reject("zero-price outside positive domain", lambda: optimum([0] + [1] * 35))
    # A readout at the initial prefix looks harmless only with a clean connector.
    dirty_bad = [["A", 1]] + base
    reject("clean-only readout false positive", lambda: symbolic_endpoint(dirty_bad))
    return rejected


def compute():
    authenticate()
    rows = {word: minimum_readouts(word) for word in source_words()}
    require(len(rows) == 945, "complete canonical pairing count")
    require(rows == independent_census(), "independent full readout costs disagree")
    heavy_missing_hist = Counter()
    readout_hist = Counter()
    for word, costs in rows.items():
        require(all(cost >= 2 and cost % 2 == 0 for cost in costs), "readout parity")
        missing = [m for m in ELIGIBLE_MASKS if costs[m - 1] > 2]
        require(missing, "odd-mask obstruction failed")
        heavy_missing_hist[len(missing)] += 1
        readout_hist.update(costs)
    source_certificate = json.loads((ROOT / "research/universal-connector-boundary/CERTIFICATE.json").read_text())
    source_fixture = source_certificate["schedules"]["five_extra_source"]["source_word"]
    witnesses = all_witnesses(rows, source_fixture)
    require(len(witnesses) == 16, "full Pareto frontier")
    # Expose every frontier vector by a strictly positive independent price.
    for winner, witness in enumerate(witnesses):
        kind, index = witness["extra"]
        low = index if kind == "B" else index + 4
        prices = [Fraction(7, 3)] * 36
        prices[low] = Fraction(1, 5)
        formula, chosen = optimum(prices)
        bills = [sum(c * p for c, p in zip(profile(w["events"]), prices)) for w in witnesses]
        require(chosen == low and bills[winner] == formula
                and all(cost > formula for i, cost in enumerate(bills) if i != winner),
                "frontier vector not independently exposed")
    regression_prices = [1, 4, 10, 16, 28] + [1] * 31
    require(optimum(regression_prices)[0] == 182, "PR1770 tariff regression")
    dirty_checks = dense_checks(witnesses)
    controls = semantic_controls(witnesses, rows)
    census_payload = [[list(word), list(costs)] for word, costs in sorted(rows.items())]
    return {"schema_version": 1, "status": "PASS_CONNECTOR_ALL_TARIFF_OPTIMUM",
            "pairings": len(rows), "labeled_source_words_by_symmetry": len(rows) * 120,
            "readout_cost_histogram": {str(k): v for k, v in sorted(readout_hist.items())},
            "heavy_odd_missing_histogram": {str(k): v for k, v in sorted(heavy_missing_hist.items())},
            "complete_cost_rows_sha256": hashlib.sha256(canonical(census_payload)).hexdigest(),
            "eligible_extra_source_indices": list(range(5)),
            "eligible_extra_readout_masks": list(ELIGIBLE_MASKS),
            "pareto_profiles": [list(profile(w["events"])) for w in witnesses],
            "witnesses": witnesses, "dirty_basis_forward_and_inverse_cases": dirty_checks,
            "controls_rejected": controls, "regression_PR1770_bill": 182,
            "claim": "For every positive36price vector, optimum=2sum(prices)+2min(B_j,A_m for weight(m)=3or5); exactly16 componentwise minimal call profiles over all schedule lengths.",
            "scope": "Generic immutable-source one-dirty-connector additive F2 alphabet; no selected supplier or new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path, help="create a new receipt exclusively")
    args = parser.parse_args()
    result = compute()
    if args.write_result:
        with args.write_result.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        require(json.loads((HERE / "RESULT.json").read_text()) == result, "committed receipt mismatch")
    print("PASS_CONNECTOR_ALL_TARIFF_OPTIMUM pairings=945 pareto_profiles=16 "
          "all_positive_prices=36 dirty_basis_cases=3552 controls=9 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as exc:
        print("FAIL_CONNECTOR_ALL_TARIFF_OPTIMUM:", exc, file=sys.stderr)
        raise SystemExit(1)
