"""Verify the new unranking endpoint sets, not predecessor executables.

Produced by Nick Petalas. Apache-2.0. Default execution writes only stdout.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from linear import Field, add_vectors, basis, combine, need, standard
from unrank import Contract, gaussian, injection, injections, subspace


def span(rows, n, field):
    return frozenset(combine(v, rows, n, field)
                     for v in itertools.product(range(field.q), repeat=len(rows)))


def all_subspaces(n, field):
    """Independent vector-set closure, only used for n<=2."""
    need(n <= 2, "literal subspace limit")
    zero = (0,) * n
    spaces = {frozenset((zero,))}
    vectors = tuple(itertools.product(range(field.q), repeat=n))
    for _ in range(n):
        next_spaces = set(spaces)
        for old in spaces:
            for v in vectors:
                extended = frozenset(add_vectors(w, combine((t,), (v,), n, field), field)
                                     for w in old for t in range(field.q))
                next_spaces.add(extended)
        spaces = next_spaces
    return tuple(sorted(spaces, key=lambda x: (len(x), sorted(x))))


def literal_gl(n, field):
    need(n <= 3 and field.q ** (n * n) <= 200000, "literal matrix limit")
    vectors = tuple(itertools.product(range(field.q), repeat=n))
    return tuple(columns for columns in itertools.product(vectors, repeat=n)
                 if len(span(columns, n, field)) == field.q ** n)


def admissible(matrix, spaces, n, field):
    a, b, c, d = spaces
    return (all(combine(v, matrix, n, field) in c for v in a)
            and all(combine(v, matrix, n, field) in d for v in b))


def compare_contract(n, field, spaces, ambient):
    inputs = tuple(basis(tuple(s), n, field) for s in spaces)
    contract = Contract(n, field.q, *inputs)
    expected = frozenset(m for m in ambient if admissible(m, spaces, n, field))
    actual = tuple(contract.decode(i) for i in range(contract.total))
    need(len(actual) == len(set(actual)), "unranking collision")
    need(frozenset(actual) == expected, "decoded endpoint set")
    return len(actual)


def small_census():
    records = []
    for n, q in ((0, 2), (1, 2), (1, 3), (1, 4), (2, 2)):
        field = Field(q)
        spaces, ambient = all_subspaces(n, field), literal_gl(n, field)
        contracts = endpoints = positive = 0
        for quadruple in itertools.product(spaces, repeat=4):
            count = compare_contract(n, field, quadruple, ambient)
            contracts += 1
            endpoints += count
            positive += int(count > 0)
        records.append(dict(n=n, q=q, contracts=contracts,
                            endpoints=endpoints, nonempty=positive))
    return records


def selected_census():
    records = []
    for n, q in ((2, 3), (2, 4), (2, 5), (3, 2)):
        field = Field(q)
        ambient = literal_gl(n, field)
        e = standard(n)
        line = (add_vectors(e[0], e[1], field),)
        candidates = ((), (e[0],), (e[1],), line, e[:2], e)
        fixtures = []
        for i in range(12):
            quadruple = tuple(candidates[(i * (2 * j + 1) + j) % len(candidates)]
                              for j in range(4))
            fixtures.append(tuple(span(x, n, field) for x in quadruple))
        fixtures.extend(tuple(span(x, n, field) for x in quad) for quad in (
            (e[:1], e[:1], e[:2], e[:2]),
            (e[:1], e[1:2], e[:2], e[:2]),
            (e[:1], e[1:2], e[:1], e[1:2]),
            (e[:2], e[:2], e[:1], e[:2]),
            ((), (), (), ()),
        ))
        if n == 3:
            fixtures.append(tuple(span(x, n, field) for x in
                                  (e[:1], e[1:2], e[:2], e[1:])))
        counts = [compare_contract(n, field, quad, ambient) for quad in fixtures]
        records.append(dict(n=n, q=q, contracts=len(fixtures), endpoints=sum(counts),
                            nonempty=sum(x > 0 for x in counts)))
    return records


def component_census():
    grassmann = ordered = 0
    for q in (2, 3, 4):
        f = Field(q)
        for m in range(4):
            for k in range(m + 1):
                rows = tuple(subspace(m, k, i, f) for i in range(gaussian(m, k, q)))
                need(len(set(rows)) == len(rows), "Grassmann collision")
                need(all(basis(r, m, f) == r for r in rows), "Grassmann RREF")
                grassmann += len(rows)
                images = tuple(injection(m, k, i, f)
                               for i in range(injections(m, k, q)))
                need(len(set(images)) == len(images), "injection collision")
                need(all(len(basis(r, m, f)) == k for r in images), "injection rank")
                ordered += len(images)
    return dict(grassmann_endpoints=grassmann, injection_endpoints=ordered)


def large_examples():
    records = []
    for n, q in ((8, 2), (10, 3), (12, 4), (12, 31)):
        f, e = Field(q), standard(n)
        contract = Contract(n, q, e[:n // 2], e[n // 3:2 * n // 3],
                            e[:n - 1], e[1:])
        need(contract.total > 0, "large nonempty contract")
        indices = tuple(sorted({0, 1, contract.total // 2, contract.total - 1}))
        spaces = (contract.a, contract.b, contract.c, contract.d)
        for index in indices:
            matrix = contract.decode(index)
            need(len(basis(matrix, n, f)) == n, "large invertibility")
            for source, target in ((spaces[0], spaces[2]), (spaces[1], spaces[3])):
                for v in source:
                    image = combine(v, matrix, n, f)
                    need(len(basis(target + (image,), n, f)) == len(target),
                         "large capacity endpoint")
        records.append(dict(n=n, q=q, selected_indices=len(indices),
                            cardinality_bits=contract.total.bit_length()))
    return records


def rejections():
    tests = (
        lambda: Contract(13, 2, (), (), (), ()),
        lambda: Contract(-1, 2, (), (), (), ()),
        lambda: Contract(2, 6, (), (), (), ()),
        lambda: Contract(2, 32, (), (), (), ()),
        lambda: Contract(True, 2, (), (), (), ()),
        lambda: Contract(2, 2, ((2, 0),), (), (), ()),
        lambda: Contract(2, 2, ((0,),), (), (), ()),
        lambda: Contract(1, 2, ((0,), (1,)), (), (), ()),
        lambda: Contract(1, 2, (), (), (), ()).decode(-1),
        lambda: Contract(1, 2, (), (), (), ()).decode(1),
        lambda: Contract(1, 2, (), (), (), ()).decode(True),
        lambda: Contract(1, 2, ((1,),), (), (), ()).decode(0),
        lambda: Contract(1, 2, ((1,),), (), (), ()).sample(()),
        lambda: Contract(1, 2, (), (), (), ()).sample((1,)),
        lambda: Contract(1, 2, (), (), (), ()).sample((0,) * 65),
    )
    for operation in tests:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError("invalid input accepted")
    return len(tests)


def sampling_law():
    contract = Contract(2, 2, (), (), (), ())
    need(contract.total == 6, "literal GL2 contract")
    counts, failures = {}, 0
    for blocks in itertools.product(range(8), repeat=2):
        matrix, used = contract.sample(blocks)
        need(used in (3, 6), "charged entropy width")
        if matrix is None:
            failures += 1
        else:
            counts[matrix] = counts.get(matrix, 0) + 1
    need(len(counts) == 6 and set(counts.values()) == {10} and failures == 4,
         "exact finite entropy distribution")
    singleton = Contract(0, 2, (), (), (), ())
    need(singleton.sample((0,)) == ((), 0), "zero-bit singleton")
    need(contract.sample(()) == (None, 0), "zero-attempt exhaustion")
    return dict(two_block_inputs=64, occurrences_per_matrix=10, exhausted=4)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    report = dict(status="PASS_TWO_CAPACITY_DIRECT_UNRANKING",
                  source_sha256=source_bindings(),
                  complete=small_census(), selected=selected_census(),
                  components=component_census(), large=large_examples(),
                  sampling=sampling_law(),
                  invalid_inputs_rejected=rejections())
    report["package_sha256"] = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(ROOT.iterdir()) if p.is_file()}
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        need(not args.receipt.resolve().is_relative_to(ROOT.parent.parent),
             "receipt must be outside checkout")
        args.receipt.write_text(text)
    print(text, end="")


def source_bindings():
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    checked = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = ROOT.parent.parent / row["path"]
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            need(digest == row["sha256"], "predecessor input bytes")
            checked[row["path"]] = digest
    return checked


if __name__ == "__main__":
    main()
