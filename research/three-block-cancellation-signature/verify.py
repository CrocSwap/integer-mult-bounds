#!/usr/bin/env python3
"""Verify the new cancellation witness and generic obstruction.

Nick Petalas. Apache-2.0. No predecessor scientific verifier is imported.
"""

import hashlib
import importlib.util
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("signature_model", PACKAGE / "model.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load local model")
model = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(model)


def check_witness():
    p, b = model.witness()
    model.require(model.multiply(p, b) == model.identity(6), "P B is not identity")
    model.require(model.multiply(b, p) == model.identity(6), "B P is not identity")
    model.require(model.inverse(p) == b and model.inverse(b) == p, "inverse mismatch")
    signature = ((7,) * 6, (6, 6, 5, 5, 3, 3))
    model.require(model.masks(p, b, (2, 2, 2)) == signature, "wrong integer signature")
    for prime in (2, 3, 5, 7, 11):
        pm = tuple(tuple(x % prime for x in row) for row in p)
        bm = tuple(tuple(x % prime for x in row) for row in b)
        result = tuple(tuple(x % prime for x in row) for row in model.multiply(pm, bm))
        model.require(result == model.identity(6), "finite-field endpoint failed")
        model.require(model.masks(pm, bm, (2, 2, 2)) == signature, "field signature changed")
    mutations = 0
    for i in range(6):
        for j in range(6):
            if p[i][j]:
                bad = tuple(tuple(0 if (u, v) == (i, j) else p[u][v]
                                  for v in range(6)) for u in range(6))
                model.require(model.multiply(bad, b) != model.identity(6), "omission survived")
                mutations += 1
    return {"P": p, "inverse": b, "source_masks": signature[0],
            "reader_masks": signature[1], "finite_fields": [2, 3, 5, 7, 11],
            "nonzero_entry_omissions_rejected": mutations}


def check_generic(sizes):
    n, full = sum(sizes), (1 << len(sizes)) - 1
    terms, cofactors = model.matching_terms(n)
    tested = nonsingular = 0
    histogram = {}
    for support in model.full_source_supports(sizes):
        tested += 1
        inverse, match = model.generic_inverse(support, n, terms, cofactors)
        if inverse is None:
            continue
        nonsingular += 1
        model.require(inverse == model.reach_inverse(support, n, match), "path/cofactor mismatch")
        source, reader = model.masks(model.support_matrix(support, n), inverse, sizes)
        model.require(source == (full,) * n, "wrong enumeration domain")
        count = reader.count(full)
        model.require(count >= len(sizes), "generic full-reader floor failed")
        histogram[count] = histogram.get(count, 0) + 1
    model.require(sum(histogram.values()) == nonsingular, "lost generic support")
    return {"block_sizes": sizes, "tested": tested, "generic_nonsingular": nonsingular,
            "full_reader_histogram": histogram}


def check_six_port_patterns():
    terms, cofactors = model.matching_terms(6)
    p, _ = model.witness()
    actual = sum(1 << (i * 6 + j) for i in range(6) for j in range(6) if p[i][j])
    inverse, match = model.generic_inverse(actual, 6, terms, cofactors)
    model.require(inverse is not None, "witness support is structurally singular")
    model.require(inverse == model.reach_inverse(actual, 6, match), "witness path mismatch")
    _, reader = model.masks(model.support_matrix(actual, 6), inverse, (2, 2, 2))
    model.require(reader.count(7) >= 3, "own support evades generic theorem")
    representatives = (0, 2, 4)
    sharp = sum(1 << (i * 6 + j) for i in range(6) for j in range(6)
                if i in representatives or i == j)
    inv_sharp, match = model.generic_inverse(sharp, 6, terms, cofactors)
    model.require(inv_sharp is not None, "sharp support is singular")
    model.require(inv_sharp == model.reach_inverse(sharp, 6, match), "sharp path mismatch")
    source, readers = model.masks(model.support_matrix(sharp, 6), inv_sharp, (2, 2, 2))
    model.require(source == (7,) * 6 and readers.count(7) == 3, "floor is not sharp")
    return {"actual_support_generic_reader_masks": reader,
            "sharp_generic_reader_masks": readers}


def check_invalid():
    cases = ((model.identity, (0,)), (model.inverse, (((0,),),)),
             (model.matching_terms, (7,)), (model.support_matrix, (-1, 3)),
             (model.full_source_supports, ((3, 1),)))
    rejected = 0
    for function, args in cases:
        try:
            result = function(*args)
            if function is model.full_source_supports:
                tuple(result)
        except ValueError:
            rejected += 1
    model.require(rejected == len(cases), "invalid input accepted")
    return rejected


def main():
    receipt = {"claim_type": "scoped proof with exact finite corroboration",
               "witness": check_witness(),
               "generic_support_domains": [check_generic(sizes) for sizes in
                                           ((1, 1, 1), (2, 1, 1), (2, 2, 1))],
               "six_port_patterns": check_six_port_patterns(),
               "invalid_inputs_rejected": check_invalid()}
    paths = sorted(path for path in PACKAGE.iterdir() if path.is_file())
    model.require(len(paths) <= 16, "unexpected package inventory")
    receipt["package_sha256"] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in paths}
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_THREE_BLOCK_CANCELLATION_SIGNATURE")


if __name__ == "__main__":
    main()
