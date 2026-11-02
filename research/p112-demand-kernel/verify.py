"""Generate and check the fixed P112 demand kernel. Nick Petalas, Apache-2.0."""

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from kernel import (accepts, all_cliques, alphabet, check_witnesses, domination,
                    hit_signature, quotient, reduce_rows, require, tuple_cliques)

ROOT = HERE.parent.parent
FILE_LIMIT = 1_048_576


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def read_json(path):
    raw = bounded_read(path)
    return json.loads(raw)


def bounded_read(path):
    with path.open("rb") as stream:
        raw = stream.read(FILE_LIMIT + 1)
    require(len(raw) <= FILE_LIMIT, "JSON input exceeds one MiB")
    return raw


def load_inputs():
    sources = read_json(HERE / "SOURCES.json")
    loaded = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        require(path.is_file() and not path.is_symlink(), "regular input file")
        raw = bounded_read(path)
        require(hashlib.sha256(raw).hexdigest() == row["sha256"], "input SHA256 mismatch")
        loaded[path.name] = json.loads(raw)
    require(set(loaded) == {"GEOMETRY.json", "CANDIDATES.json"}, "exact live inputs")
    return loaded["GEOMETRY.json"], loaded["CANDIDATES.json"]


def digest_stream(rows):
    digest = hashlib.sha256()
    for row in rows:
        digest.update((canonical(row) + "\n").encode())
    return digest.hexdigest()


def must_reject(call, message):
    try:
        call()
    except ValueError:
        return
    raise ValueError("control accepted: " + message)


def general_controls():
    checked = 0
    masks = list(range(1, 8))
    for ranks in product((1, 2), repeat=7):
        rows = {mask: (rank, 0) for mask, rank in zip(masks, ranks, strict=True)}
        kept = reduce_rows(rows)
        domination(rows, kept)
        for weights in product(range(3), repeat=3):
            require(accepts(rows, weights) == accepts(kept, weights), "toy equivalence")
            checked += 1
    # Smaller vertex sets need not give stronger rank-demand inequalities.
    require(not accepts({2: (1, 0)}, (1, 0)), "inclusion is not dominance")
    require(accepts({3: (1, 0)}, (1, 0)), "different hit sets matter")
    # A row dominated by no single row may still follow from a sum of rows.
    require(len(reduce_rows({1: (1, 0), 2: (1, 0), 3: (2, 0)})) == 3,
            "pairwise reduction does not assert LP irredundancy")
    return checked


def behavioral_controls(rows, kept, factors, cliques, coordinates, examples, model):
    width = len(factors)
    checked = 0
    for mask in range(1 << width):
        weights = tuple(mask >> k & 1 for k in range(width))
        require(accepts(rows, weights) == accepts(kept, weights), "binary multiplicity")
        checked += 1
    for seed in range(256):
        weights = tuple(((seed + 1) * (k + 3) + (seed >> (k % 8))) % 5
                        for k in range(width))
        require(accepts(rows, weights) == accepts(kept, weights), "integer multiplicity")
        checked += 1
    weights = tuple(coordinates.count(k) for k in range(width))
    require(accepts(kept, weights), "coordinate support control")
    for k in coordinates:
        damaged = list(weights)
        damaged[k] -= 1
        require(not accepts(kept, damaged), "missing coordinate support rejected")
    # The source caps identify fixtures, without repricing or auditing their claims.
    for example in examples:
        one_factors, _ = alphabet(model, [example, example])
        weights = tuple(int(pair in one_factors[:9]) for pair in factors)
        require(not accepts(kept, weights), "saved deficient layout rejected")
    altered = dict(kept)
    mask = next(iter(altered))
    rank, witness = altered[mask]
    altered[mask] = (rank + 1, witness)
    must_reject(lambda: check_witnesses(altered, factors, cliques), "false demand")
    must_reject(lambda: check_witnesses({mask: (rank, 0)}, factors, cliques), "false witness")
    must_reject(lambda: domination(rows, {}), "empty alleged kernel")
    must_reject(lambda: accepts(kept, (-1,) * width), "negative multiplicities")
    must_reject(lambda: accepts(kept, (True,) * width), "Boolean multiplicities")
    must_reject(lambda: accepts(kept, (1,)), "wrong multiplicity dimension")
    return checked


def compute():
    model, examples = load_inputs()
    factors, coordinates = alphabet(model, examples)
    cliques = all_cliques(model)
    require(set(cliques) == tuple_cliques(model), "separate complete-domain enumeration")
    rows = quotient(cliques, factors)
    kept = reduce_rows(rows)
    mapping = domination(rows, kept)
    check_witnesses(kept, factors, cliques)
    # Inspect every original row, including every nonmaximal clique.
    for clique in cliques:
        mask = hit_signature(clique, factors)
        other = mapping[mask]
        require(other & mask == other and kept[other][0] >= clique.bit_count(),
                "original row not dominated")
    binary_checks = behavioral_controls(rows, kept, factors, cliques,
                                        coordinates, examples, model)
    toy_checks = general_controls()
    return {
        "status": "PASS_P112_DEMAND_KERNEL",
        "claim_type": "finite certificate and scoped equivalence proof",
        "alphabet": [[hex(left), hex(right)] for left, right in factors],
        "coordinate_indices": coordinates,
        "complete_demands": len(cliques), "signature_rows": len(rows),
        "kernel_rows": len(kept),
        "kernel_by_demand": dict(sorted(Counter(rank for rank, _ in kept.values()).items())),
        "kernel": [[hex(mask), rank, hex(witness)]
                   for mask, (rank, witness) in kept.items()],
        "cliques_sha256": digest_stream(hex(q) for q in cliques),
        "quotient_sha256": digest_stream([hex(mask), rank, hex(witness)]
                                        for mask, (rank, witness) in sorted(rows.items())),
        "domination_sha256": digest_stream([hex(a), hex(b)] for a, b in sorted(mapping.items())),
        "multiplicity_checks": binary_checks, "toy_equivalence_checks": toy_checks,
        "new_kappa": None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print generated certificate only")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
        return
    require(canonical(read_json(HERE / "RESULT.json")) == canonical(result), "saved result differs")
    names = ("kernel.py", "verify.py", "README.md", "PROOF.md", "TASK.json",
             "SOURCES.json", "VERIFY.json", "RESULT.json")
    hashes = {}
    for name in names:
        raw = bounded_read(HERE / name)
        hashes[name] = hashlib.sha256(raw).hexdigest()
    print(canonical({"status": result["status"], "complete_demands": result["complete_demands"],
                     "signature_rows": result["signature_rows"], "kernel_rows": result["kernel_rows"],
                     "multiplicity_checks": result["multiplicity_checks"],
                     "toy_equivalence_checks": result["toy_equivalence_checks"],
                     "source_sha256": hashes}))


if __name__ == "__main__":
    main()
