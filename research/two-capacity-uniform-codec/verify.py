"""Literal conformance checks for the new construction. Apache-2.0."""

import argparse
import hashlib
import json
from itertools import combinations, permutations, product
from pathlib import Path
import time

from codec import Codec, Contract, draw_rank
from linear import apply, require


ROOT = Path(__file__).resolve().parent


def verify_sources():
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    prefix = ("https://github.com/aliromman/integer-mult-bounds/blob/"
              "96c63f994af628f574c71dca0d7ed219cbfc70c2/")
    for row in manifest["external_sources"]:
        require(row["url"].startswith(prefix), "Unexpected predecessor source")
        payload = (ROOT / row["local_path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                "Predecessor source digest mismatch")
        blob = b"blob " + str(len(payload)).encode() + b"\0" + payload
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "Predecessor Git blob mismatch")
    return len(manifest["external_sources"])


def span(rows, n, prime):
    return frozenset(tuple(sum(a * row[j] for a, row in zip(coefficients, rows)) % prime
                           for j in range(n))
                     for coefficients in product(range(prime), repeat=len(rows)))


def determinant(columns, prime):
    n, value = len(columns), 0
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i + 1, n))
        term = (-1)**inversions
        for i in range(n):
            term *= columns[i][order[i]]
        value += term
    return value % prime


def invertibles(n, prime):
    require(n <= 3 and prime**(n * n) <= 1000, "Literal matrix budget exceeded")
    vectors = tuple(product(range(prime), repeat=n))
    return tuple(columns for columns in product(vectors, repeat=n)
                 if determinant(columns, prime))


def subspaces(n, prime):
    """Independent span-set inventory; keep the first basis for each set."""
    require(n <= 2, "Literal subspace budget exceeded")
    vectors = tuple(product(range(prime), repeat=n))
    result = {}
    for size in range(n + 1):
        for rows in combinations(vectors, size):
            elements = span(rows, n, prime)
            if len(elements) == prime**size:
                result.setdefault(elements, rows)
    return tuple(result.values())


def literal_completions(contract, matrices):
    c = contract
    result = []
    for columns in matrices:
        if any(apply(columns, x, c.prime) != y for x, y in c.fixed):
            continue
        if all(all(apply(columns, x, c.prime) in span(target, c.n, c.prime)
                   for x in source) for source, target in c.capacities):
            result.append(columns)
    return result


def check_contract(contract, matrices):
    codec = Codec(contract)
    expected = literal_completions(contract, matrices)
    expected.sort(key=lambda columns: tuple(apply(columns, x, contract.prime)
                                            for x in codec.complement))
    require(codec.total == len(expected), "Wrong construction cardinality")
    for index, columns in enumerate(expected):
        before = codec.count_calls
        require(codec.unrank(index) == columns, "Unrank disagrees with literal ordered set")
        require(codec.count_calls - before <= len(codec.complement) * contract.prime**contract.n,
                "Unrank exceeded the proved conditional-count bound")
        before = codec.count_calls
        require(codec.rank(columns) == index, "Rank disagrees with literal ordered set")
        require(codec.count_calls - before <= len(codec.complement) * contract.prime**contract.n,
                "Rank exceeded the proved conditional-count bound")
    return len(expected)


def full_small_census():
    contracts, endpoints, positive = 0, 0, 0
    for prime, n in ((2, 0), (2, 1), (2, 2), (3, 1)):
        spaces, matrices = subspaces(n, prime), invertibles(n, prime)
        standard = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
        for fixed_rank in range(n + 1):
            fixed = tuple((e, e) for e in standard[:fixed_rank])
            for a, b, c, d in product(spaces, repeat=4):
                contract = Contract(n, prime, fixed, ((a, c), (b, d)))
                size = check_contract(contract, matrices)
                contracts += 1
                endpoints += size
                positive += bool(size)
    return {"contracts": contracts, "positive_contracts": positive,
            "rank_unrank_endpoints": endpoints}


def nonnormalized_and_larger():
    contracts, endpoints = 0, 0
    for prime, n in ((3, 2), (5, 2), (2, 3)):
        standard = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
        e, f = standard[:2]
        diagonal = tuple((x + y) % prime for x, y in zip(e, f))
        configs = [Contract(n, prime, (), (((), ()), ((), ()))),
                   Contract(n, prime, ((diagonal, e),), (((), ()), ((), ()))),
                   Contract(n, prime, (), (((e,), (f,)), ((f,), (e,)))),
                   Contract(n, prime, ((diagonal, diagonal),),
                            (((e,), (e,)), ((f,), (f,))))]
        if n == 3:
            z = standard[2]
            configs.extend([Contract(n, prime, ((e, f),),
                                     (((e, z), (e, f)), ((f, z), (f, z)))),
                            Contract(n, prime, ((e, e), (f, f)),
                                     (((diagonal,), (e,)), ((z,), (z,))))])
        matrices = invertibles(n, prime)
        for contract in configs:
            endpoints += check_contract(contract, matrices)
            contracts += 1
    return {"contracts": contracts, "rank_unrank_endpoints": endpoints}


def entropy_census():
    cases, words, completion_samples = 0, 0, 0
    for total in range(1, 13):
        for budget in range(11):
            frequencies, exhausted = [0] * total, 0
            for bits in product((0, 1), repeat=budget):
                index, used = draw_rank(total, bits)
                require(0 <= used <= budget, "Invalid bit consumption")
                if index is None:
                    exhausted += 1
                else:
                    frequencies[index] += 1
                words += 1
            require(len(set(frequencies)) == 1, "Sampler has unequal output probabilities")
            require(exhausted == 2**budget % total, "Wrong exact exhaustion probability")
            cases += 1
    codec = Codec(Contract(2, 2, (), (((), ()), ((), ()))))
    expected = {codec.unrank(i): 0 for i in range(codec.total)}
    for bits in product((0, 1), repeat=8):
        columns, _ = codec.sample(bits)
        if columns is not None:
            expected[columns] += 1
            completion_samples += 1
    require(set(expected.values()) == {42}, "Completion samples are not exactly uniform")
    return {"cardinality_budget_pairs": cases, "bit_strings": words,
            "successful_completion_samples": completion_samples}


def large_round_trips():
    n, prime = 8, 2
    standard = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
    configs = [Contract(n, prime, (), (((), ()), ((), ()))),
               Contract(n, prime, ((standard[0], standard[-1]),),
                        (((standard[1],), (standard[0], standard[1])),
                         ((standard[2],), (standard[2], standard[3]))))]
    result = []
    for contract in configs:
        codec = Codec(contract)
        indices = sorted({0, 1, codec.total // 3, codec.total // 2, codec.total - 1})
        for index in indices:
            columns = codec.unrank(index)
            require(codec.rank(columns) == index, "Large exact round trip failed")
            codec.check_completion(columns)
        result.append({"dimension": n, "total": codec.total, "tested_ranks": indices,
                       "count_calls": codec.count_calls})
    return result


def controls():
    good = Contract(2, 2, (), (((), ()), ((), ())))
    codec = Codec(good)
    actions = [lambda: codec.unrank(-1), lambda: codec.unrank(codec.total),
               lambda: codec.unrank(True), lambda: codec.rank(((0, 0), (0, 0))),
               lambda: Contract(2, 4, (), (((), ()), ((), ()))),
               lambda: Contract(13, 2, (), (((), ()), ((), ()))),
               lambda: Contract(2, 2, (((1, 0), (0, 0)),), (((), ()), ((), ()))),
               lambda: Contract(2, 2, (), ((((2, 0),), ()), ((), ()))),
               lambda: draw_rank(0, (0,)), lambda: draw_rank(6, (2,)),
               lambda: draw_rank(6, (0,) * 4097)]
    constrained = Codec(Contract(2, 2, (((1, 0), (1, 0)),),
                                 ((((0, 1),), ((0, 1),)), ((), ()))))
    actions.append(lambda: constrained.rank(((0, 1), (1, 0))))
    capacity = Codec(Contract(2, 2, (), ((((1, 0),), ((1, 0),)), ((), ()))))
    actions.append(lambda: capacity.rank(((0, 1), (1, 0))))
    empty = Codec(Contract(2, 2, (), ((((1, 0),), ()), ((), ()))))
    require(empty.total == 0, "Empty fixture is not empty")
    actions.append(lambda: empty.sample((0, 1)))
    for action in actions:
        try:
            action()
        except ValueError:
            continue
        raise ValueError("Invalid input was accepted")
    return len(actions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    result = {"bound_predecessor_files": verify_sources(),
              "small_census": full_small_census(),
              "additional_census": nonnormalized_and_larger(),
              "entropy_census": entropy_census(),
              "large_round_trips": large_round_trips(), "rejection_controls": controls()}
    result["source_sha256"] = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in sorted(ROOT.rglob("*")) if path.is_file()}
    if args.receipt:
        require(not args.receipt.resolve().is_relative_to(ROOT.parent.parent),
                "Write receipts outside the checkout")
        args.receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    print(f"PASS_TWO_CAPACITY_UNIFORM_CODEC seconds={time.monotonic() - started:.3f}")


if __name__ == "__main__":
    main()
