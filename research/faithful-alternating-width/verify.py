#!/usr/bin/env python3
"""Construct faithful binary dot embeddings; replay the declared finite domain."""

import hashlib
import itertools
import json
from pathlib import Path


MAX_DIMENSION = 32
PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(form):
    require(type(form) is tuple, "form must be a tuple")
    n = len(form)
    require(n <= MAX_DIMENSION, "dimension exceeds 32")
    require(all(type(row) is int and 0 <= row < (1 << n) for row in form),
            "rows must be bounded binary integers")
    for i in range(n):
        require(not (form[i] >> i) & 1, "form is not alternating")
        for j in range(i):
            require(((form[i] >> j) & 1) == ((form[j] >> i) & 1),
                    "form is not symmetric")


def pairing(form, x, y):
    return sum(((x >> i) & 1) * (form[i] & y).bit_count()
               for i in range(len(form))) & 1


def adapted_basis(form):
    """Return hyperbolic pairs followed by a basis of the radical."""
    remaining = [1 << i for i in range(len(form))]
    pairs = []
    for _ in range(len(form) // 2):
        hits = [(i, j) for i in range(len(remaining))
                for j in range(i + 1, len(remaining))
                if pairing(form, remaining[i], remaining[j])]
        if not hits:
            break
        i, j = hits[0]
        u, v = remaining[i], remaining[j]
        pairs.extend((u, v))
        remaining = [z ^ (u if pairing(form, z, v) else 0)
                     ^ (v if pairing(form, z, u) else 0)
                     for h, z in enumerate(remaining) if h not in (i, j)]
    return tuple(pairs + remaining), len(pairs)


def canonical_images(rank, nullity):
    """Explicit H^(rank/2) plus zero(nullity) in a minimum dot space."""
    images = []
    for i in range(rank // 2):
        images.append((1 << (2 * i)) | (1 << (2 * i + 1)))
        images.append(((1 << (rank + 1)) - 1) ^ ((1 << (2 * i + 1)) - 1))
    if nullity:
        images.append((1 << (rank + 2)) - 1)
        images.extend(3 << (rank + 2 * j) for j in range(1, nullity))
        return rank + 2 * nullity, tuple(images)
    return rank + int(rank > 0), tuple(images)


def transport(basis, images):
    """Transport the canonical images back to the original input basis."""
    n = len(basis)
    pivots = [None] * n
    for vector, image in zip(basis, images, strict=True):
        for bit in range(n - 1, -1, -1):
            if not (vector >> bit) & 1:
                continue
            if pivots[bit] is None:
                pivots[bit] = (vector, image)
                break
            old_vector, old_image = pivots[bit]
            vector ^= old_vector
            image ^= old_image
        else:
            raise ValueError("adapted basis is dependent")
    result = []
    for i in range(n):
        vector, image = 1 << i, 0
        for bit in range(n - 1, -1, -1):
            if (vector >> bit) & 1:
                require(pivots[bit] is not None, "adapted basis is incomplete")
                old_vector, old_image = pivots[bit]
                vector ^= old_vector
                image ^= old_image
        require(vector == 0, "basis transport failed")
        result.append(image)
    return tuple(result)


def embed(form):
    """Return (minimum_width, images_of_original_basis, binary_rank)."""
    validate(form)
    basis, rank = adapted_basis(form)
    width, images = canonical_images(rank, len(form) - rank)
    return width, transport(basis, images), rank


def binary_rank(vectors):
    pivots = {}
    for vector in vectors:
        for bit in range(2 * MAX_DIMENSION - 1, -1, -1):
            if not (vector >> bit) & 1:
                continue
            if bit not in pivots:
                pivots[bit] = vector
                break
            vector ^= pivots[bit]
    return len(pivots)


def gram(images):
    return tuple(sum(((x & y).bit_count() & 1) << j
                     for j, y in enumerate(images)) for x in images)


def check_embedding(form, result, exhaustive):
    width, images, rank = result
    n = len(form)
    require(not exhaustive or n <= 6, "literal-vector check exceeds dimension six")
    require(len(images) == n and all(0 <= v < (1 << width) for v in images),
            "embedding has wrong dimensions")
    require(gram(images) == form, "Gram identity failed")
    require(binary_rank(images) == n, "embedding is not injective")
    require(binary_rank(form) == rank, "rank mismatch")
    if exhaustive:
        span = {0}
        for vector in images:
            span |= {x ^ vector for x in tuple(span)}
        kernel = sum(all((row & v).bit_count() % 2 == 0 for row in form)
                     for v in range(1 << n))
        require(len(span) == 1 << n, "literal images collide")
        require(kernel == 1 << (n - rank), "literal nullity mismatch")
    expected = n + (n - rank) if rank < n else n + int(n > 0)
    require(width == expected, "width theorem mismatch")


def alternating_forms(n):
    require(0 <= n <= 6, "form census dimension exceeds six")
    edges = tuple(itertools.combinations(range(n), 2))
    for mask in range(1 << len(edges)):
        rows = [0] * n
        for bit, (i, j) in enumerate(edges):
            if (mask >> bit) & 1:
                rows[i] |= 1 << j
                rows[j] |= 1 << i
        yield tuple(rows)


def form_census():
    counts = {}
    digest = hashlib.sha256()
    for n in range(7):
        by_width = {}
        for form in alternating_forms(n):
            result = embed(form)
            check_embedding(form, result, exhaustive=True)
            width = result[0]
            by_width[str(width)] = by_width.get(str(width), 0) + 1
            digest.update(json.dumps((form, result), separators=(",", ":")).encode())
            digest.update(b"\n")
        counts[str(n)] = by_width
    return {"by_dimension_and_width": counts, "construction_sha256": digest.hexdigest(),
            "forms": sum(sum(row.values()) for row in counts.values())}


def exhaustive_minima():
    """Independent literal search, without the constructor or lower bound."""
    first = {}
    candidates = 0
    injective = 0
    for width in range(7):
        even = tuple(v for v in range(1, 1 << width) if v.bit_count() % 2 == 0)
        for n in range(4):
            for images in itertools.product(even, repeat=n):
                candidates += 1
                span = {0}
                for vector in images:
                    span |= {x ^ vector for x in tuple(span)}
                if len(span) != 1 << n:
                    continue
                injective += 1
                first.setdefault(gram(images), width)
    minima = []
    for n in range(4):
        for form in alternating_forms(n):
            require(form in first, "literal search found no embedding")
            require(first[form] == embed(form)[0], "literal minimum disagrees")
            minima.append({"form": form, "width": first[form]})
    return {"candidate_tuples": candidates, "injective_tuples": injective,
            "forms": len(minima), "minima": minima}


def large_fixtures():
    count = 0
    for n in range(7, MAX_DIMENSION + 1):
        for rank in range(0, n + 1, 2):
            form = tuple((1 << (i ^ 1)) if i < rank else 0 for i in range(n))
            basis = [1 << i for i in range(n)]
            for step in range(4 * n):
                i = step % n
                j = (i + 1 + (step // n)) % n
                if i != j:
                    basis[i] ^= basis[j]
            changed = tuple(sum(pairing(form, x, y) << j
                                for j, y in enumerate(basis)) for x in basis)
            check_embedding(changed, embed(changed), exhaustive=False)
            count += 1
    return count


def expect_rejection(form, result=None, message=None):
    try:
        if result is None:
            embed(form)
        else:
            check_embedding(form, result, exhaustive=True)
    except ValueError as error:
        require(str(error) == message, "rejection reason changed")
        return 1
    raise ValueError("negative control was accepted")


def controls():
    count = 0
    for form, message in [([0], "form must be a tuple"),
                          ((0,) * 33, "dimension exceeds 32"),
                          ((True,), "rows must be bounded binary integers"),
                          ((2,), "rows must be bounded binary integers"),
                          ((-1,), "rows must be bounded binary integers"),
                          ((1,), "form is not alternating"),
                          ((2, 0), "form is not symmetric")]:
        count += expect_rejection(form, message=message)
    count += expect_rejection((2, 1, 0), (3, (3, 6, 0), 2),
                              "embedding is not injective")
    count += expect_rejection((2, 1), (2, (1, 2), 2), "Gram identity failed")
    count += expect_rejection((2, 1), (4, (3, 6), 2), "width theorem mismatch")
    return count


def receipt():
    census = form_census()
    minima = exhaustive_minima()
    larger = large_fixtures()
    rejected = controls()
    examples = {}
    for name, form in {"hyperbolic_with_radical": (2, 1, 0),
                       "singular_f4_dimension_two_rank_one": (2, 1, 0, 0)}.items():
        result = embed(form)
        check_embedding(form, result, exhaustive=True)
        examples[name] = {"form": form, "width": result[0], "images": result[1]}
    hashes = {name: hashlib.sha256((PACKAGE / name).read_bytes()).hexdigest()
              for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                           "VERIFY.json", "verify.py")}
    return {"status": "PASS_FAITHFUL_ALTERNATING_WIDTH", "claim_type": "scoped proof",
            "form_census": census, "literal_minima": minima, "large_fixtures": larger,
            "rejected_controls": rejected, "examples": examples, "source_sha256": hashes}


if __name__ == "__main__":
    print(json.dumps(receipt(), indent=2, sort_keys=True))
