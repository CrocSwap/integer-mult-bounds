"""Independent exact rational derivative screen for all one- to four-union stage sets."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from itertools import combinations, permutations
from json import dumps, loads
from math import comb
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
PRICE = "plan/PRICE.json"
ARCHIVE = "inputs/7113-CALLER.json.gz"
ENGINE = "independent/r123_tangent.py"
PINS = {
    PRICE: "8940a6b5e49e838fb6dba06b73500ee6c906f6dcc8422a04ac6d5eb7b7ecf397",
    ARCHIVE: "7e8038559cd158f6e32ef6d1a3bf15ab6a8ecc2239af32ab1699511ac28e26d9",
    ENGINE: "8ad672bd808b6b8c30306fa2b125b19be5e8c19215425b79dc592e552a96b169",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
PAYLOAD = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
LIMIT, SECONDS = 26075, 25


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("duplicate metadata key")
    return result


def pinned(root, relative):
    raw = (root / relative).read_bytes()
    if sha256(raw).hexdigest() != PINS[relative]:
        raise ValueError(f"changed dependency {relative}")
    return raw


def weight(i, j):
    return (-1) ** (i + j) * (i + 1) ** 41 * (j + 2) ** 37


def project(matrix):
    return sum((value * weight(i, j) for (i, j), value in matrix.items()), Q(0))


def signed_matrix(terms, odd, even):
    result = defaultdict(Q)
    for sign, clocks in [(1, odd), (-1, even)]:
        for clock in clocks:
            for index, value in terms[clock].items():
                result[index] += sign * value
    return {index: value for index, value in result.items() if value}


def match(left, right, allowed):
    return next((list(zip(left, permutation, strict=True))
                 for permutation in permutations(right)
                 if all((o, e) in allowed for o, e in zip(left, permutation, strict=True))), None)


def controls(engine):
    same = {(0, 0): Q(1, 2)}
    unequal = {(0, 1): project(same) / weight(0, 1)}
    assert project(same) == project(unequal)
    terms = {1: same, 2: unequal, 3: same, 4: unequal}
    assert signed_matrix(terms, (1,), (2,))
    assert not signed_matrix(terms, (1, 2), (3, 4))
    assert match((1, 2), (3, 4), {(1, 4), (2, 3)}) == [(1, 4), (2, 3)]
    assert match((1, 2), (3, 4), {(1, 3), (2, 3)}) is None
    return engine["controls"]() + [
        "equal rational fingerprint and unequal exact matrices",
        "equal full matrix sum with nonzero summands",
        "distinct compatible bijection and reused donor rejection",
    ]


def check_stage(stage, odd, even, terms, signatures, allowed, state, deadline):
    row = dict(stage=stage, odd=odd, even=even, cardinalities=[], matches=[])
    for size in range(1, 5):
        left = [(group, sum(signatures[o] for o in group)) for group in combinations(odd, size)]
        right = [(group, sum(signatures[e] for e in group)) for group in combinations(even, size)]
        counts = dict(k=size, odd_subsets=len(left), even_subsets=len(right), comparisons=0,
                      compatible=0, rational_scalar_equal=0, exact_sums=0)
        for odd_clocks, a in left:
            for even_clocks, b in right:
                if state["comparisons"] >= LIMIT or monotonic() >= deadline:
                    raise TimeoutError("stage comparison cap")
                state["comparisons"] += 1
                counts["comparisons"] += 1
                pairing = match(odd_clocks, even_clocks, allowed)
                counts["compatible"] += pairing is not None
                if a != b:
                    continue
                counts["rational_scalar_equal"] += 1
                if signed_matrix(terms, odd_clocks, even_clocks):
                    continue
                counts["exact_sums"] += 1
                if pairing is not None:
                    row["matches"].append(dict(odd=odd_clocks, even=even_clocks))
        assert counts["comparisons"] == len(left) * len(right)
        row["cardinalities"].append(counts)
    return row


def eliminate(stages, masks):
    active = set(masks)
    receipts = []
    while active:
        admitted = defaultdict(set)
        for row in stages:
            for item in row["matches"]:
                if set(item["even"]).issubset(active):
                    for e in item["even"]:
                        admitted[e].add(row["stage"])
        gone = {e: min(set(masks[e]) - admitted[e]) for e in sorted(active)
                if not set(masks[e]).issubset(admitted[e])}
        if not gone:
            break
        receipts.append(gone)
        active.difference_update(gone)
    return receipts, sorted(active)


def literal(root, price, engine, state, deadline):
    raw = decompress(pinned(root, ARCHIVE))
    if sha256(raw).hexdigest() != PAYLOAD:
        raise ValueError("changed caller payload")
    caller = loads(raw, object_pairs_hook=unique)
    b = caller["types"]["B"]
    n, offset = b["roles"], b["offset"]
    assert (caller["stages"], n, offset, len(b["ports"])) == (17, 36, 36, 8)
    steps, odd, even = engine["unit_ops"](caller["events"], n, offset)
    state["literal_events"] = len(steps)
    assert {str(t): list(m) for t, (_, m) in odd.items()} == price["odd_masks"]
    assert {str(t): list(m) for t, (_, m) in even.items()} == price["even_masks"]
    allowed = {(o, e) for o, (_, left) in odd.items() for e, (_, right) in even.items()
               if set(left).isdisjoint(right)}
    assert len(allowed) == 180
    roles = {t: row[0] for t, row in (odd | even).items()}
    terms = engine["impulses"](steps, roles, n, deadline)
    signatures = {t: project(matrix) for t, matrix in terms.items()}
    state["projector_fingerprints"] = {t: str(v) for t, v in signatures.items()}

    # Compare the exact full direct derivative to the independent impulses at
    # two largest matching-witness stages before relying on fingerprints.
    samples = []
    for stage in (2, 9):
        pairs = [(o, e) for o, e in price["matching_witness"] if stage in even[e][1]]
        inject = {t: (roles[t], sign) for o, e in pairs for t, sign in [(o, 1), (e, -1)]}
        assert len(pairs) == 2 and len(inject) == 4
        endpoint, full = engine["tangent"](steps, inject, n)
        odd_sites, even_sites = zip(*pairs, strict=True)
        delta = signed_matrix(terms, odd_sites, even_sites)
        assert endpoint == engine["identity"](n) and full == delta
        assert project(delta) == sum(signatures[o] - signatures[e] for o, e in pairs)
        i, j = min(delta)
        samples.append(dict(stage=stage, fusions=pairs, witness=[i + offset, j + offset, str(delta[i, j])]))
    state["full_tangent_controls"] = samples
    for stage in range(1, 18):
        left = sorted(o for o, (_, mask) in odd.items() if stage not in mask)
        right = sorted(e for e, (_, mask) in even.items() if stage in mask)
        previous = price["stages"][stage - 1]
        assert (stage, left, right) == (previous["stage"], previous["odd"], previous["even"])
        assert sum(comb(len(odd), k) * comb(len(right), k) for k in range(1, 5)) == previous["relaxed_comparisons"]
        state["stages"].append(check_stage(stage, left, right, terms, signatures, allowed, state, deadline))
    state["eliminations"], state["remaining_even_sites"] = eliminate(
        state["stages"], {t: mask for t, (_, mask) in even.items()})
    state["compatible_comparisons"] = sum(c["compatible"] for row in state["stages"] for c in row["cardinalities"])
    state["exact_match_count"] = sum(len(row["matches"]) for row in state["stages"])


def main():
    parser = ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--controls-only", action="store_true")
    args = parser.parse_args()
    assert __debug__
    price = loads(pinned(args.root, PRICE), object_pairs_hook=unique)
    assert (price["head"], price["caller"], price["caller_sha256"]) == (HEAD, CALLER, PAYLOAD)
    assert price["limits"]["relaxed_comparisons"] == LIMIT and price["limits"]["seconds"] == SECONDS
    pinned(args.root, ENGINE)
    engine = run_path(str(args.root / ENGINE))
    tests = controls(engine)
    if args.controls_only:
        print(dumps(dict(controls=tests), indent=2, sort_keys=True))
        return 0

    def stop(*_):
        raise TimeoutError("hard 25-second cap")

    state = dict(head=HEAD, caller=CALLER, caller_sha256=PAYLOAD, q=1, body="unit",
                 cap_cases=LIMIT, cap_seconds=SECONDS, pins=PINS, comparisons=0,
                 stages=[], timeout=None, controls=tests)
    signal(SIGALRM, stop)
    alarm(SECONDS)
    deadline = monotonic() + 23
    try:
        literal(args.root, price, engine, state, deadline)
    except TimeoutError as problem:
        state["timeout"] = str(problem)
    finally:
        alarm(0)
    state["unvisited_stages"] = list(range(len(state["stages"]) + 1, 18))
    print(dumps(state, indent=2, sort_keys=True))
    return 124 if state["timeout"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
