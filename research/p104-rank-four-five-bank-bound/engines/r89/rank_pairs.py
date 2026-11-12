"""Rank, without excluding, the banks that dropped on both sides."""
from collections import defaultdict
from gzip import decompress
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path
import sys
from time import monotonic

SUFFIX_RESULT = "340d1beb37477198e4690a56153d1a225c8ad70e00cf470c07a5bc080c0255ad"
SUFFIX_ENGINE = "751d5d0c4c665c8768ff69bcf939700d3be2f989c59f09af3a4aa14d3c1ebbc4"


def checked(path, want):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != want:
        raise ValueError(f"changed dependency: {path.name}")
    return raw


def exterior_kernel(roles, vectors, cohort, prime, plus):
    basis, kernel = [], []
    for role in roles:
        row, weights = vectors[role].copy(), {role: 1}
        for pivot, old_row, old_weights in basis:
            amount = -row.get(pivot, 0)
            plus(row, old_row, amount)
            plus(weights, old_weights, amount)
        exterior = row.keys() - cohort
        if not exterior:
            kernel.append((weights, row))
            continue
        pivot = min(exterior)
        inverse = pow(row[pivot], -1, prime)
        basis.append((pivot, {k: v * inverse % prime for k, v in row.items()},
                      {k: v * inverse % prime for k, v in weights.items()}))
    return kernel


def dot(a, b, prime):
    return sum(v * b.get(k, 0) for k, v in a.items()) % prime


def independent(b, d, prime):
    pivot = next((i for i, value in enumerate(d) if value), None)
    if pivot is None:
        return any(b)
    return any((value * d[pivot] - other * b[pivot]) % prime
               for value, other in zip(b, d, strict=True))


def pair_class(prefix, suffix, prime, plus):
    b_rows = [[dot(c, d, prime) for _, d in suffix] for _, c in prefix]
    d_rows = [[(dot(a, b, prime) - value) % prime
               for (b, _), value in zip(suffix, row, strict=True)]
              for (a, _), row in zip(prefix, b_rows, strict=True)]
    direct = [sum(map(len, (a, b, c, d))) for i, (a, c) in enumerate(prefix)
              for j, (b, d) in enumerate(suffix) if b_rows[i][j] and not d_rows[i][j]]
    if direct:
        return 0, min(direct)
    # A nonzero wedge is witnessed by a basis vector or a sum of two.
    for i, (br, dr) in enumerate(zip(b_rows, d_rows, strict=True)):
        if independent(br, dr, prime):
            return 1, 0
        for j in range(i):
            bs = [(x + y) % prime for x, y in zip(br, b_rows[j], strict=True)]
            ds = [(x + y) % prime for x, y in zip(dr, d_rows[j], strict=True)]
            if independent(bs, ds, prime):
                return 1, 0
    width = len(suffix)
    joint = {i: {j: v for j, v in enumerate(d_rows[i] + b_rows[i]) if v}
             for i in range(len(prefix))}
    # In the proportional case, only xD=0 and xB nonzero can work.
    kernel = exterior_kernel(list(joint), joint, set(range(width, 2 * width)), prime, plus)
    return (1, 0) if any(image for _, image in kernel) else (2, 0)


def forward_event(event, rows, scalar, plus, prime):
    op, dst, *args = event
    if op == "INIT":
        rows[dst] = {}
    elif op == "CLEAR":
        rows[dst] = None
    elif op == "SCALE":
        factor = scalar(args[0])
        rows[dst] = {k: factor * v % prime for k, v in rows[dst].items() if factor * v % prime}
    elif op in ("COPY", "ADD"):
        if op == "COPY":
            assert not rows[dst]
        plus(rows[dst], rows[args[0]], scalar(args[1]))
    else:
        assert op == "MOVE"


def main():
    assert __debug__
    deadline = monotonic() + 30
    root = Path(sys.argv[1])
    checked(root / "lead/suffix_sweep.py", SUFFIX_ENGINE)
    reverse = run_path(str(root / "lead/suffix_sweep.py"))
    raw = reverse["authenticated"](root)
    engine = run_path(str(root / "inputs/exterior_minor.py"))
    unique, scalar, plus, prime = (engine[k] for k in ("unique", "scalar", "plus", "P"))
    word = json.loads(decompress(raw["inputs/7334-WORD.json.gz"]), object_pairs_hook=unique)
    price = json.loads(raw["inputs/PRICE.json"], object_pairs_hook=unique)
    suffix_receipt = json.loads(checked(root / "lead/RESULT.json", SUFFIX_RESULT), object_pairs_hook=unique)
    assert suffix_receipt["status"] == "EXHAUSTED" and not suffix_receipt["unvisited"]
    assert suffix_receipt["head"] == price["head"] == reverse["HEAD"]
    banks = [row for row in suffix_receipt["results"] if row["disposition"] == "rank drop"]
    assert len(banks) == 1465
    assert pair_class([({0: 1}, {3: 1})], [({0: 1}, {3: 1})], prime, plus) == (0, 4)
    assert pair_class([({0: 1}, {3: 1})], [({0: 2}, {3: 1})], prime, plus) == (2, 0)
    cohort = set(price["endpoint_cohort"])
    public = word["public"]
    tape = word["program"]
    requests = defaultdict(list)
    for row in banks:
        requests[row["key"][0]].append(row)
    rows = [{i: 1} for i in range(public)] + [None] * word["owned_fields"]
    prefixes, results = {}, {}
    for cut in range(len(tape) + 1):
        if (cut % 128 == 0 or cut in requests) and monotonic() >= deadline:
            break
        for row in requests.get(cut, ()):
            key = tuple(row["key"])
            prefix = exterior_kernel(row["public"], rows, cohort, prime, plus)
            assert len(prefix) == len(row["public"]) - row["prefix_rank_mod_65521"]
            prefixes[key] = prefix
        if cut < len(tape):
            forward_event(tape[cut], rows, scalar, plus, prime)
    active = word["final"] + [None] * word["owned_fields"]
    columns = [{i: 1} for i in range(public)] + [None] * word["owned_fields"]
    for cut in range(len(tape), -1, -1):
        if (cut % 128 == 0 or cut in requests) and monotonic() >= deadline:
            break
        for row in requests.get(cut, ()):
            key = tuple(row["key"])
            if key not in prefixes:
                continue
            suffix = exterior_kernel(row["public"], columns, cohort, prime, plus)
            assert len(suffix) == len(row["public"]) - row["suffix_rank_mod_65521"]
            kind, terms = pair_class(prefixes[key], suffix, prime, plus)
            results[key] = {**row, "pair_class": kind, "direct_terms": terms}
        if cut:
            reverse["reverse_event"](tape[cut - 1], active, columns, public, scalar, plus, prime)
    records = [results[tuple(row["key"])] for row in banks if tuple(row["key"]) in results]
    print(json.dumps({"head": price["head"], "prime": prime, "cases_cap": 1465, "seconds_cap": 30,
                      "controls": ["planted unit pair", "wrong local pairing"],
                      "cases": len(records), "modular_pairs": sum(r["pair_class"] < 2 for r in records),
                      "unvisited": [row["key"] for row in banks if tuple(row["key"]) not in results],
                      "results": records, "input_sha256": {"suffix_result": SUFFIX_RESULT, "suffix_engine": SUFFIX_ENGINE}},
                     separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
