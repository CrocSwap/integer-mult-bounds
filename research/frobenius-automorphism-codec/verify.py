"""Exact finite corroboration of the new inverse codecs. Apache-2.0."""

import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))

from codec import Codec
from linear import Field, gl_order, gl_rank, gl_unrank, require
from oracle import determinant, inspect


def rejects(operation):
    try:
        operation()
    except ValueError:
        return 1
    raise RuntimeError("negative control was accepted")


def fields():
    checked = 0
    for q in (2, 3, 4, 5, 7, 8, 9):
        field = Field(q)
        for a in range(q):
            require(field.add(a, field.neg(a)) == 0, "additive inverse")
            if a:
                require(field.mul(a, field.inv(a)) == 1, "multiplicative inverse")
            for b in range(q):
                require(field.mul(a, b) == field.mul(b, a), "commutative product")
                for c in range(q):
                    require(field.mul(a, field.add(b, c)) ==
                            field.add(field.mul(a, b), field.mul(a, c)), "distributivity")
                    require(field.mul(a, field.mul(b, c)) ==
                            field.mul(field.mul(a, b), c), "associative product")
                    checked += 1
    return checked


def general_linear():
    checked = 0
    for q, n in ((2, 0), (2, 1), (2, 2), (2, 3), (3, 2), (4, 2)):
        field = Field(q)
        seen = set()
        for index in range(gl_order(q, n)):
            columns = gl_unrank(field, n, index)
            require(gl_rank(field, columns) == index, "GL inverse failed")
            require(determinant(field, columns) != 0, "GL determinant zero")
            require(columns not in seen, "duplicate GL encoding")
            seen.add(columns)
            checked += 1
    return checked


def exhaustive_codecs():
    contexts, maps, products = [], 0, 0
    for q, heights in ((2, ()), (2, (1,)), (2, (1, 1)), (2, (1, 2)),
                       (3, (1,)), (4, (1, 1)), (8, (1,)), (9, (1,))):
        codec = Codec(q, heights)
        seen = set()
        for index in range(codec.order):
            images = codec.unrank(index)
            require(codec.rank(images) == index, "local codec inverse failed")
            require(images not in seen, "duplicate generator images")
            seen.add(images)
            products += inspect(codec, images, index in (0, codec.order // 2, codec.order - 1))
            maps += 1
        contexts.append({"q": q, "heights": heights, "indices": codec.order})
    return contexts, maps, products


def larger_codecs():
    checked = 0
    contexts = []
    for q, heights in ((2, (2, 2)), (2, (1, 1, 1)), (2, (2, 1)),
                       (3, (1, 1)), (4, (1, 2)), (5, (1,))):
        codec = Codec(q, heights)
        indices = sorted({0, 1, codec.order // 3, codec.order // 2, codec.order - 1})
        for index in indices:
            images = codec.unrank(index)
            require(codec.rank(images) == index, "larger codec inverse failed")
            # Large nonbinary cases check the actual defining relations and products.
            inspect(codec, images, all_products=codec.field.q != 2)
            checked += 1
        contexts.append({"q": q, "heights": heights, "order": str(codec.order),
                         "tested_indices": [str(i) for i in indices]})
    return contexts, checked


def controls():
    codec = Codec(2, (1, 2))
    good = codec.unrank(codec.order - 1)
    constant = [list(v) for v in good]
    constant[0][0] = 1
    high = [list(v) for v in good]
    high[0][codec.units[1]] = 1
    singular = [list(v) for v in good]
    singular[0][codec.units[0]] = 0
    malformed = [list(v) for v in good]
    malformed[0][1] = 2
    requests = [lambda: codec.unrank(-1), lambda: codec.unrank(codec.order),
                lambda: codec.unrank(True), lambda: codec.rank(good[:-1]),
                lambda: codec.rank(tuple(tuple(v) for v in constant)),
                lambda: codec.rank(tuple(tuple(v) for v in high)),
                lambda: codec.rank(tuple(tuple(v) for v in singular)),
                lambda: codec.rank(tuple(tuple(v) for v in malformed)),
                lambda: Codec(6, (1,)), lambda: Codec(2, (0,)),
                lambda: Codec(2, (4, 4)), lambda: gl_rank(Field(2), ((1, 0), (1, 0))),
                lambda: gl_unrank(Field(2), 2, gl_order(2, 2)),
                lambda: inspect(codec, tuple(tuple(v) for v in constant)),
                lambda: inspect(codec, tuple(tuple(v) for v in high)),
                lambda: inspect(codec, tuple(tuple(v) for v in singular))]
    return sum(rejects(request) for request in requests)


def receipt():
    files = sorted(PACKAGE.iterdir())
    require(len(files) <= 16, "package file capacity")
    hashes = {}
    for path in files:
        if path.is_file():
            require(path.stat().st_size <= 128 * 1024, "package file size")
            hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def main():
    field_identities = fields()
    gl_indices = general_linear()
    exhaustive, indices, products = exhaustive_codecs()
    larger, larger_indices = larger_codecs()
    failures = controls()
    report = {"status": "PASS_FROBENIUS_AUTOMORPHISM_CODEC",
              "field_identities": field_identities, "gl_indices": gl_indices,
              "exhaustive_contexts": exhaustive, "exhaustive_indices": indices,
              "basis_products_in_exhaustive_contexts": products,
              "larger_contexts": larger, "larger_indices": larger_indices,
              "rejecting_controls": failures, "sha256": receipt()}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
