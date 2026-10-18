#!/usr/bin/env python3
"""Exact collision checks for the unchanged PR3250 program. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIM = 512
PAIRS = DIM // 2


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(raw, expected_sha):
    need(len(raw) <= 32768, "reference source capacity")
    need(hashlib.sha256(raw).hexdigest() == expected_sha, "reference source hash")


def authenticated_reference():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    rows = pins["retained_predecessor"]["files"]
    need(len(rows) == 2, "two retained predecessor files")
    need({r["retained_path"] for r in rows} ==
         {"reference.py", "vendor/pr3250/PROOF.md"}, "fixed predecessor paths")
    for row in rows:
        with (HERE / row["retained_path"]).open("rb") as stream:
            raw = stream.read(32769)
        authenticate(raw, row["sha256"])
    # One static, source-authenticated local module. No arbitrary plugin loading.
    import reference

    return reference


def digest(value):
    return hashlib.sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def pullback(core, mapping, ref):
    """Invert the signed right monomial, retaining its actual global phase."""
    return [ref.rotate(*core[dest], (-phase) % 4) for dest, phase in mapping]


def entry(choices, precision, recipe, ref):
    need(len(choices) == PAIRS and all(c in (-1, 0, 1) for c in choices), "ternary word")
    need(2 <= precision <= 2046, "fixture precision capacity")
    large = 1 << (precision + 1)
    # PR3250's integer quantum is q/4. Here q=1, so multiply entries by four.
    core = [(4 * large, 0) if i % 2 == 0 else (4 * choices[i // 2], 0)
            for i in range(DIM)]
    return pullback(core, ref.table(recipe["right"]), ref)


def execute(choices, precision, recipe, ref):
    source = entry(choices, precision, recipe, ref)
    original = list(source)
    destination = [(0, 0)] * DIM
    source, destination, counts = ref.run(source, destination, recipe, precision,
                                        precision + 2)
    return original, source, destination, counts


def expected(precision, recipe, ref):
    large = 1 << (precision + 1)
    core = [(2 * large, 2 * large if i % 2 == 0 else -2 * large)
            for i in range(DIM)]
    target = [(0, 0)] * DIM
    ref.monomial(core, target, ref.table(recipe["left"]), Counter())
    return target, [(-a // 2, -b // 2) for a, b in target]


def fixture(precision, recipe, ref):
    want_source, want_destination = expected(precision, recipe, ref)
    words = [[0] * PAIRS, [-1] * PAIRS, [1] * PAIRS,
             [(-1, 0, 1)[i % 3] for i in range(PAIRS)],
             [-1 if i % 2 else 1 for i in range(PAIRS)]]
    endpoints, summaries = [], []
    for choices in words:
        original, source, destination, counts = execute(choices, precision, recipe, ref)
        need(source == want_source and destination == want_destination, "common endpoint")
        need(counts["native_nonzero_rounds"] == 2 * sum(c != 0 for c in choices),
             "actual native rounding sites")
        need(counts["halfadd_nonzero_rounds"] == 0, "exact half-ADD on witness")
        exact, _ = ref.exact(original, [(0, 0)] * DIM, recipe)
        need(ref.error2(source, exact) == 16 * sum(c * c for c in choices),
             "unitary exact-output separation in q/4 units")
        endpoints.append(digest([source, destination]))
        summaries.append(counts)
    need(summaries[1] == summaries[2] == summaries[4], "same sign-family summary")
    return {"precision": precision, "endpoint_sha256": endpoints[0],
            "sign_family_summary": summaries[1], "checked_words": len(words)}


def small_tensor_product(ref):
    """Exhaust all 3^4 combinations, including mixed zero/sign rounding sites."""
    outputs = set()
    for choices in itertools.product((-1, 0, 1), repeat=4):
        values = []
        for small in choices:
            large = 1 << 6  # p=5
            sr = ref.nearest(large + small, 5)
            dr = ref.nearest(large - small, 5)
            values.extend((sr // 2, dr // 2, sr // 2, -dr // 2))
        outputs.add(tuple(values))
    need(len(outputs) == 1, "all 81 four-pair inputs collide")
    return 81


def audit():
    ref = authenticated_reference()
    events, recipes = ref.load()
    need(events[11795] == ["climb", "A", 470, 0, 5, 1], "actual child event")
    need(events[11796][1][-2:] == [-1, 2], "actual half coefficient")
    recipe = recipes[0]
    rows = [fixture(p, recipe, ref) for p in (2, 3, 5, 11, 53, 104, 256, 2046)]
    cardinality = 3 ** PAIRS
    return {"status": "PASS_QQ16_ROUNDED_CHILD_INVERSION",
            "event_indices": [11795, 11796], "pairs": PAIRS,
            "endpoint_family_cardinality": str(cardinality),
            "endpoint_only_retained_bits": (cardinality - 1).bit_length(),
            "fixed_summary_family_cardinality": str(2 ** PAIRS),
            "fixed_summary_retained_bits": PAIRS,
            "small_product_inputs": small_tensor_product(ref), "fixtures": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        expected_result = json.loads((HERE / "RESULT.json").read_text())
        need(result == expected_result, "committed receipt equality")
    print(result["status"], "endpoint_bits=406 fixed_summary_bits=256")


if __name__ == "__main__":
    main()
