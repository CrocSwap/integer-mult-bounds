#!/usr/bin/env python3
"""Exact fixed-row rank floors for local gauges of one P112 nine-normal decoder."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PREDECESSOR = ROOT / "research/nine-term-decoder-normal-form-seed42"
PINNED = {
    "e8lab.py": "772349edc9dff45fa3cac89fdbbe8bf1bab734e9776a245fcac8e8bd60d94634",
    "verify.py": "248763cf5ff85f073766aa8a85187a1d314fcf3a716b2586ca8fc1197d4c6c4e",
}


def need(ok, message):
    if not ok:
        raise AssertionError(message)


for name, expected in PINNED.items():
    need(hashlib.sha256((PREDECESSOR / name).read_bytes()).hexdigest() == expected,
         "predecessor source drift: " + name)
sys.path.insert(0, str(PREDECESSOR))
import e8lab as E  # noqa: E402
import verify as V  # noqa: E402


def masks_and_cost(rows, normals, live):
    X = [0] * 9
    for i, row in rows.items():
        for k, coefficient in enumerate(row):
            if coefficient:
                X[k] |= 1 << i
    Y = [E.support(b, live) for b in normals]
    ranks = tuple(E.pairing_rank(X[k], Y[k]) for k in range(9))
    return ranks, X, Y


def exact_tetrads(roots):
    remaining = set(roots)
    blocks = []
    while remaining:
        first = min(remaining)
        block = [first]
        for i in sorted(remaining - {first}):
            if all(E.G[i][j] == 0 for j in block):
                block.append(i)
            if len(block) == 8:
                break
        need(len(block) == 8, "greedy orthogonal block did not have size 8")
        blocks.append(block)
        remaining.difference_update(block)
    need(len(blocks) == 14 and sum(map(len, blocks)) == 112, "P112 partition changed")
    need(len(set(i for block in blocks for i in block)) == 112, "blocks are not disjoint")
    need(all(all(E.G[i][j] == 0 for i, j in itertools.combinations(block, 2))
              for block in blocks), "a block is not orthogonal")
    return blocks


def fixed_row_floor(roots, base_rows, normals, live, changed):
    """Cost from exterior rows only; any added row preserves or raises F2 rank."""
    X = [0] * 9
    changed = set(changed)
    for i in roots:
        if i in changed:
            continue
        for k, coefficient in enumerate(base_rows[i]):
            if coefficient:
                X[k] |= 1 << i
    Y = [E.support(b, live) for b in normals]
    ranks = tuple(E.pairing_rank(X[k], Y[k]) for k in range(9))
    return ranks


def run():
    puncture = V.coordinate_frame()
    need(puncture == [0, 13, 90, 99, 108, 113, 118, 119], "P112 puncture changed")
    extra = next(i for i in range(E.N) if i not in puncture and
                 sum(E.G[i][f] != 0 for f in puncture) == 4)
    need(extra == 1, "extra normal changed")
    frame = V.Frame("coordinate frame + root", [E.LINES[f] for f in puncture] + [E.LINES[extra]])
    need(frame.z == [Fraction(-1), Fraction(-1), Fraction(-1), Fraction(-1),
                     Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(2)],
         "nine-normal dependency changed")
    live = E.FULL ^ sum(1 << i for i in puncture)
    roots = list(E.bits(live))
    need(len(roots) == 112, "live set is not P112")
    tetrads = exact_tetrads(roots)
    base = {i: frame.sparsest(i) for i in roots}
    base_ranks, _, _ = masks_and_cost(base, frame.F, live)
    need(sum(base_ranks) == 68, "canonical sparse P112 cost changed")
    exact, pairs = V.exact_on_pairs(base, frame.F, live)
    need(exact and pairs == 112 ** 2, "baseline decoder identity failed")

    one = []
    two = []
    for a, block in enumerate(tetrads):
        ranks = fixed_row_floor(roots, base, frame.F, live, block)
        one.append({"blocks": [a], "fixed_ranks": list(ranks), "floor": sum(ranks)})
    for a, b in itertools.combinations(range(14), 2):
        changed = tetrads[a] + tetrads[b]
        ranks = fixed_row_floor(roots, base, frame.F, live, changed)
        two.append({"blocks": [a, b], "fixed_ranks": list(ranks), "floor": sum(ranks)})
    need(Counter(x["floor"] for x in one) == Counter({67: 2, 68: 12}), "single-block census changed")
    need(Counter(x["floor"] for x in two) == Counter({64: 1, 67: 24, 68: 66}), "pair census changed")
    need([x for x in two if x["floor"] == 64] == [
        {"blocks": [0, 1], "fixed_ranks": [8, 8, 8, 8, 8, 8, 8, 8, 0], "floor": 64}
    ], "unique optimistic equality case changed")

    # Nontrivial rational gauges on the changed rows preserve the exact decoder identity.
    for block_ids in ([0], [0, 1], [12, 13]):
        changed = set().union(*(set(tetrads[j]) for j in block_ids))
        rows = {i: list(row) for i, row in base.items()}
        for i in changed:
            t = Fraction((i % 7) - 3, 5)
            rows[i] = [base[i][k] + t * frame.z[k] for k in range(9)]
        ok, count = V.exact_on_pairs(rows, frame.F, live)
        need(ok and count == 112 ** 2, "dependency gauge failed exact all-pairs identity")

    bad = {i: list(row) for i, row in base.items()}
    bad[roots[0]][0] += 1
    need(V.exact_on_pairs(bad, frame.F, live)[0] is False, "coefficient mutation escaped control")

    result = {
        "schema_version": 1,
        "seed": "8232e87e36b7bc2bd06a84ddf3384413",
        "base_commit": "ecc75c79c22d909fd42aa68437eb77c4c1361835",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "puncture_indices": puncture,
        "extra_root_index": extra,
        "dependency": [int(x) for x in frame.z],
        "live_roots": len(roots),
        "baseline_sparsest_cost": sum(base_ranks),
        "baseline_term_ranks": list(base_ranks),
        "baseline_exact_pairs": pairs,
        "tetrads": tetrads,
        "single_block_floors": one,
        "pair_block_floors": two,
        "single_floor_histogram": {str(k): v for k, v in sorted(Counter(x["floor"] for x in one).items())},
        "pair_floor_histogram": {str(k): v for k, v in sorted(Counter(x["floor"] for x in two).items())},
        "gauge_identity_controls": 3,
        "mutation_rejected": True,
        "scope_limit": "Exterior rows remain at the canonical sparsest gauges; only one or two blocks of this fixed partition may change. No result is claimed for three or more blocks or another frame or puncture.",
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS_COORD_ROOT_P112_LOCAL_TETRAD_GAUGE", json.dumps({
        "baseline_cost": result["baseline_sparsest_cost"],
        "single_floor_histogram": result["single_floor_histogram"],
        "pair_floor_histogram": result["pair_floor_histogram"],
        "exact_pairs": pairs,
        "gauge_controls": 3,
        "mutation_rejected": True,
    }, sort_keys=True))


if __name__ == "__main__":
    run()
