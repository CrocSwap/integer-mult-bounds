"""Stage-local necessary support and sound elimination for up to four fusions."""
from collections import defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from itertools import combinations, permutations
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "plan/PRICE.json": "8940a6b5e49e838fb6dba06b73500ee6c906f6dcc8422a04ac6d5eb7b7ecf397",
    "inputs/7113-CALLER.json.gz": "7e8038559cd158f6e32ef6d1a3bf15ab6a8ecc2239af32ab1699511ac28e26d9",
    "inputs/direct_impulse.py": "d04426aed9528aedc6400d384d7fd13c6531e5e3e6592a7eea4faee46c61e004",
    "inputs/r123_pair_derivative.py": "ce9477aadf31c0b21fefea1ae55059793c2a28fd070c7dcc501ca9b3b7151734",
}
FILTERS = [(65521, 11), (65537, 17), (65537, 29)]


def unique(items):
    doc = dict(items)
    if len(doc) != len(items):
        raise ValueError("duplicate JSON key")
    return doc


def checked(rel):
    data = (ROOT / rel).read_bytes()
    if sha256(data).hexdigest() != PINS[rel]:
        raise ValueError(f"changed dependency {rel}")
    return data


def signatures(projectors):
    result = {}
    for clock, matrix in projectors.items():
        result[clock] = tuple(
            sum(q.numerator * pow(q.denominator, -1, p) * pow(36*i+j+1, exponent, p)
                for (i, j), q in matrix.items()) % p
            for p, exponent in FILTERS
        )
    return result


def sum_signature(group, signature):
    return tuple(sum(signature[c][i] for c in group) % p for i, (p, _) in enumerate(FILTERS))


def exact_sum(group, values):
    out = defaultdict(Fraction)
    for clock in group:
        for key, value in values[clock].items():
            out[key] += value
    return {k: v for k, v in out.items() if v}


def perfect(left, right, allowed):
    return any(all((o, e) in allowed for o, e in zip(left, perm, strict=True))
               for perm in permutations(right))


def find_local(stage, sigs, projectors, allowed, deadline):
    result = {"stage": stage["stage"], "cardinalities": [], "matches": []}
    for size in range(1, 5):
        odds = list(combinations(stage["odd"], size))
        odds_by_signature = defaultdict(list)
        for group in odds:
            odds_by_signature[sum_signature(group, sigs)].append(group)
        even_count = 0
        collisions = 0
        exact = 0
        for evens in combinations(stage["even"], size):
            if monotonic() >= deadline:
                raise TimeoutError("stage subset cap")
            even_count += 1
            for odd in odds_by_signature.get(sum_signature(evens, sigs), []):
                collisions += 1
                if exact_sum(odd, projectors) != exact_sum(evens, projectors):
                    continue
                exact += 1
                if perfect(odd, evens, allowed):
                    result["matches"].append({"odd": odd, "even": evens})
        result["cardinalities"].append({
            "k": size, "odd_subsets": len(odds), "even_subsets": even_count,
            "comparisons": len(odds) * even_count, "modular_collisions": collisions, "exact_sums": exact,
        })
    return result


def prune(stages, even_masks):
    active = set(even_masks)
    steps = []
    while active:
        coverage = defaultdict(set)
        for entry in stages:
            for match in entry["matches"]:
                if set(match["even"]) <= active:
                    for clock in match["even"]:
                        coverage[clock].add(entry["stage"])
        removed = {e: min(set(even_masks[e]) - coverage[e]) for e in sorted(active)
                   if set(even_masks[e]) - coverage[e]}
        if not removed:
            break
        active -= removed.keys()
        steps.append(removed)
    return sorted(active), steps


def controls():
    values = {1: {(0, 0): Fraction(1, 2)}, 2: {(0, 0): Fraction(-1, 3)},
              3: {(0, 0): Fraction(1, 6)}, 4: {}}
    assert exact_sum([1, 2], values) == exact_sum([3, 4], values)
    assert sum_signature([1, 2], signatures(values)) == sum_signature([3, 4], signatures(values))
    assert perfect([1, 2], [3, 4], {(1, 4), (2, 3)}) and not perfect([1, 2], [3, 4], {(1, 3), (2, 3)})
    stages = [{"stage": 1, "matches": [{"even": [3, 4]}]}, {"stage": 2, "matches": []}]
    assert prune(stages, {3: [1, 2], 4: [1]}) == ([], [{3: 2}, {4: 1}])
    return ["signed equal rational sum", "distinct odd/even matching", "cascading missing-stage elimination"]


def stop(*_):
    raise TimeoutError("hard 25-second cap")


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(25)
    deadline = monotonic() + 23
    price = loads(checked("plan/PRICE.json"), object_pairs_hook=unique)
    results, events, reason = [], None, None
    active, steps = sorted(map(int, price["even_masks"])), []
    try:
        payload = decompress(checked("inputs/7113-CALLER.json.gz"))
        assert sha256(payload).hexdigest() == price["caller_sha256"]
        caller = loads(payload, object_pairs_hook=unique)
        checked("inputs/direct_impulse.py")
        engine = run_path(str(ROOT / "inputs/direct_impulse.py"))
        checked("inputs/r123_pair_derivative.py")
        walker = run_path(str(ROOT / "inputs/r123_pair_derivative.py"))
        odd, even = engine["literal_stock"](caller["events"], 36)
        assert {str(t): v[1] for t, v in odd.items()} == price["odd_masks"]
        assert {str(t): v[1] for t, v in even.items()} == price["even_masks"]
        allowed = {(o, e) for o, (_, a) in odd.items() for e, (_, b) in even.items() if set(a).isdisjoint(b)}
        assert len(allowed) == 180
        values, events = walker["walk"](caller, engine, [], deadline)
        sigs = signatures(values)
        for stage in price["stages"]:
            results.append(find_local(stage, sigs, values, allowed, deadline))
        assert len(results) == 17
        active, steps = prune(results, {t: v[1] for t, v in even.items()})
    except TimeoutError as error:
        reason = str(error)
    finally:
        alarm(0)
    print(dumps({
        "head": price["head"], "caller": price["caller"], "pins": PINS, "controls": controls(),
        "q": 1, "body": "unit", "literal_events": events, "filters": FILTERS,
        "stages": results, "comparisons": sum(c["comparisons"] for row in results for c in row["cardinalities"]),
        "exact_match_count": sum(len(row["matches"]) for row in results),
        "eliminations": steps, "remaining_even_sites": active,
        "unvisited_stages": [r["stage"] for r in price["stages"][len(results):]], "timeout": reason,
    }, sort_keys=True, indent=2))
    return 124 if reason else 0


if __name__ == "__main__":
    raise SystemExit(main())
