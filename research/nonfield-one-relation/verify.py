#!/usr/bin/env python3
"""Exact nonfield specialization checks. Standard library; no predecessor replay."""

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


MODULI = (4, 6, 8, 9, 10, 12)
PRIMES = (2, 3, 5)
ZERO = (0, 0, 0, 0)
IDENTITY = (1, 0, 0, 1)
PACKAGE_FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
                 "VERIFY.json", "verify.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def mmul(a, b, modulus):
    return ((a[0]*b[0]+a[1]*b[2]) % modulus,
            (a[0]*b[1]+a[1]*b[3]) % modulus,
            (a[2]*b[0]+a[3]*b[2]) % modulus,
            (a[2]*b[1]+a[3]*b[3]) % modulus)


def reduced(a, modulus):
    return tuple(value % modulus for value in a)


def residue_primes(modulus):
    require(modulus in MODULI, "modulus outside the fixed composite corpus")
    return tuple(p for p in PRIMES if modulus % p == 0)


def check_projector(a, modulus):
    require(len(a) == 4, "matrix must be two by two")
    require(mmul(a, a, modulus) == a, "matrix is not idempotent")
    require((a[0]*a[3]-a[1]*a[2]) % modulus == 0,
            "matrix has a rank-two residue fiber")


def local_projector_count(modulus, prime):
    power = 1
    for exponent in range(1, 5):
        power *= prime
        if modulus % (power*prime) != 0:
            return prime**(2*(exponent-1))*prime*(prime+1)
    raise ValueError("prime-power exponent exceeds the fixed corpus")


def projector_census(modulus):
    primes = residue_primes(modulus)
    matrices = []
    histogram = Counter()
    for a in product(range(modulus), repeat=4):
        if mmul(a, a, modulus) != a:
            continue
        if (a[0]*a[3]-a[1]*a[2]) % modulus:
            continue
        check_projector(a, modulus)
        pattern = tuple(int(reduced(a, p) != ZERO) for p in primes)
        histogram[pattern] += 1
        matrices.append(a)
    expected = {}
    for pattern in product((0, 1), repeat=len(primes)):
        count = 1
        for active, prime in zip(pattern, primes):
            if active:
                count *= local_projector_count(modulus, prime)
        expected[pattern] = count
    require(dict(histogram) == expected, "CRT/projector count mismatch")
    return tuple(matrices), {"".join(map(str, key)): histogram[key]
                             for key in sorted(histogram)}


def accumulate(polynomial, exponent, matrix, modulus):
    old = polynomial.get(exponent, ZERO)
    value = tuple((x+y) % modulus for x, y in zip(old, matrix))
    if value == ZERO:
        polynomial.pop(exponent, None)
    else:
        polynomial[exponent] = value


def formal_word(frames, projectors, modulus):
    require(len(frames) == len(projectors) <= 3, "word length exceeds three")
    polynomial = {(0, 0): IDENTITY}
    for frame, projector in zip(frames, projectors):
        require(len(frame) == 2, "frame exponent dimension must be two")
        check_projector(projector, modulus)
        complement = tuple((x-y) % modulus
                           for x, y in zip(IDENTITY, projector))
        following = {}
        for exponent, matrix in polynomial.items():
            accumulate(following, exponent, mmul(matrix, complement, modulus),
                       modulus)
            shifted = (exponent[0]+frame[0], exponent[1]+frame[1])
            accumulate(following, shifted, mmul(matrix, projector, modulus),
                       modulus)
        require(len(following) <= 8, "formal support capacity exceeded")
        polynomial = following
    return polynomial


def reduce_polynomial(polynomial, modulus, prime):
    require(prime in PRIMES and modulus % prime == 0,
            "not a unital residue-field quotient of this ring")
    result = {}
    for exponent, matrix in polynomial.items():
        value = reduced(matrix, prime)
        if value != ZERO:
            result[exponent] = value
    return result


def diagonal_endpoint(polynomial):
    if any(matrix[1] or matrix[2] for matrix in polynomial.values()):
        return None
    endpoint = []
    for diagonal in (0, 3):
        terms = [(key, matrix[diagonal]) for key, matrix in polynomial.items()
                 if matrix[diagonal]]
        if len(terms) != 1 or terms[0][1] != 1:
            return None
        endpoint.append(terms[0][0])
    return tuple(endpoint)


def assignments(frames):
    require(len(frames) <= 3, "assignment capacity exceeded")
    endpoints = set()
    for owners in product(range(3), repeat=len(frames)):
        rows = [[0, 0], [0, 0]]
        for owner, frame in zip(owners, frames):
            if owner < 2:
                rows[owner][0] += frame[0]
                rows[owner][1] += frame[1]
        endpoints.add(tuple(tuple(row) for row in rows))
    return endpoints


def eligible(frames):
    """For this fixture, A=diag(1,0) and B=diag(0,1)."""
    require(all(frame in ((1, 0), (0, 1)) for frame in frames),
            "frame outside the two-axis fixture")
    require(len(frames)-len(set(frames)) <= 1,
            "active frame list has more than one rational relation")


def check_word(frames, projectors, modulus, possible_endpoints):
    ring_word = formal_word(frames, projectors, modulus)
    endpoint = diagonal_endpoint(ring_word)
    for prime in residue_primes(modulus):
        images = tuple(reduced(n, prime) for n in projectors)
        specialized = formal_word(frames, images, prime)
        require(reduce_polynomial(ring_word, modulus, prime) == specialized,
                "specialization does not preserve the full formal word")
        if endpoint is not None:
            active = tuple(frame for frame, n in zip(frames, images) if n != ZERO)
            eligible(active)
            require(endpoint in assignments(active), "disjoint assignment failed")
            rank_sum = sum(int(value != 0) for row in endpoint for value in row)
            require(rank_sum <= len(active), "active-fiber paid-rank floor failed")
    if endpoint is not None:
        require(endpoint in possible_endpoints, "global assignment failed")
    return endpoint is not None


def word_census(projectors):
    counts = {}
    independent_frames = ((1, 0), (0, 1))
    possible = assignments(independent_frames)
    for modulus in (4, 6, 8, 9):
        diagonal = 0
        matrices = projectors[modulus]
        for word in product(matrices, repeat=2):
            diagonal += check_word(independent_frames, word, modulus, possible)
        counts[str(modulus)+"_independent"] = {
            "words": len(matrices)**2, "diagonal_endpoints": diagonal}
    related_frames = ((1, 0), (0, 1), (1, 0))
    possible = assignments(related_frames)
    diagonal = 0
    for word in product(projectors[4], repeat=3):
        diagonal += check_word(related_frames, word, 4, possible)
    counts["4_one_relation"] = {
        "words": len(projectors[4])**3, "diagonal_endpoints": diagonal}
    return counts


def fixtures():
    partial = (3, 0, 0, 0)
    complement = (4, 0, 0, 0)
    a = (1, 0)
    require(diagonal_endpoint(formal_word((a,), (partial,), 6)) is None,
            "a component-dependent monomial was accepted globally")
    glued = formal_word((a, a), (partial, complement), 6)
    require(diagonal_endpoint(glued) == (a, (0, 0)), "CRT gluing failed")
    for prime in (2, 3):
        require(sum(reduced(n, prime) != ZERO for n in (partial, complement)) == 1,
                "partial-projector active count failed")
    sharp = formal_word(((1, 0), (0, 1)), ((1, 0, 0, 0),)*2, 4)
    require(diagonal_endpoint(sharp) == ((1, 1), (0, 0)),
            "sharp rank-two target or dirty restoration failed")
    return {"partial_projector_modulus": 6, "glued_paid_factors": 2,
            "active_factors_in_each_residue": 1, "sharp_rank_sum": 2,
            "sharp_paid_factors": 2}


def controls():
    rejected = 0
    cases = (("modulus", 1), ("quotient", 5), ("idempotent", (0, 1, 0, 0)),
             ("rank", IDENTITY), ("relations", ((1, 0),)*3))
    for kind, value in cases:
        try:
            if kind == "modulus":
                residue_primes(value)
            elif kind == "quotient":
                reduce_polynomial({(0, 0): IDENTITY}, 6, value)
            elif kind in ("idempotent", "rank"):
                check_projector(value, 4)
            else:
                eligible(value)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("a negative control was accepted")
    require(diagonal_endpoint({(0, 0): (2, 0, 0, 1)}) is None,
            "nonunit endpoint coefficient accepted")
    require(diagonal_endpoint({(0, 0): (1, 1, 0, 1)}) is None,
            "off-diagonal endpoint accepted")
    require(diagonal_endpoint({(0, 0): IDENTITY, (1, 0): (1, 0, 0, 0)}) is None,
            "two-term diagonal accepted as a monomial")
    twice = formal_word(((1, 0),)*2, ((1, 0, 0, 0),)*2, 2)
    require(diagonal_endpoint(twice) == ((2, 0), (0, 0)),
            "rational address labels were reduced modulo the characteristic")
    return rejected+4


def report():
    projectors = {}
    histograms = {}
    for modulus in MODULI:
        projectors[modulus], histograms[str(modulus)] = projector_census(modulus)
    return {"schema": "nonfield-one-relation-checks/1",
            "claim_type": "scoped proof using PR6044 as a cited premise",
            "projector_histograms": histograms,
            "word_censuses": word_census(projectors),
            "fixtures": fixtures(), "rejection_controls": controls()}


def read_limited(path):
    with path.open("rb") as handle:
        data = handle.read(1_048_577)
    require(len(data) <= 1_048_576, "file exceeds one MiB")
    return data


def bound_receipt(result):
    root = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        data = read_limited(root/name)
        hashes[name] = sha256(data).hexdigest()
    return {"result": result, "source_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-to", type=Path)
    parser.add_argument("--check-receipt", type=Path)
    options = parser.parse_args()
    result = report()
    receipt = bound_receipt(result)
    encoded = json.dumps(receipt, sort_keys=True, indent=2)+"\n"
    if options.check_receipt is not None:
        data = read_limited(options.check_receipt)
        # Canonical bytes also reject JSON true substituted for integer one.
        require(data.decode("utf-8") == encoded, "receipt or source hashes differ")
    if options.emit_to is not None:
        root = Path(__file__).resolve().parent
        require(not options.emit_to.resolve().is_relative_to(root),
                "receipt must be outside the package")
        with options.emit_to.open("x", encoding="utf-8") as handle:
            require(handle.write(encoded) == len(encoded), "short receipt write")
    print(json.dumps(result, sort_keys=True))
    print("PASS_NONFIELD_ONE_RELATION")


if __name__ == "__main__":
    main()
