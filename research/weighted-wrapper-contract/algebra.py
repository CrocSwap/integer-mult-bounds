"""Exact independent finite-map oracle. Apache-2.0; @CubeJerry + Codex.

Universal claims are proved in README.md, not inferred from these censuses.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from math import gcd, prod


def need(condition, message):
    if not condition:
        raise ValueError(message)


def group(modulus, dimension):
    vectors = tuple(product(range(modulus), repeat=dimension))
    index = {v: i for i, v in enumerate(vectors)}
    add = tuple(tuple(index[tuple((a+b) % modulus for a, b in zip(x, y))]
                      for y in vectors) for x in vectors)
    sub = tuple(tuple(index[tuple((a-b) % modulus for a, b in zip(x, y))]
                      for y in vectors) for x in vectors)
    return vectors, index, add, sub


def inverse(mapping):
    need(sorted(mapping) == list(range(len(mapping))), "bijection required")
    result = [0] * len(mapping)
    for x, y in enumerate(mapping):
        result[y] = x
    return tuple(result)


def linear_maps(modulus, dimension, vectors, index):
    maps = []
    for entries in product(range(modulus), repeat=dimension**2):
        rows = [entries[i*dimension:(i+1)*dimension] for i in range(dimension)]
        mapping = tuple(index[tuple(sum(a*b for a, b in zip(row, x)) % modulus
                                    for row in rows)] for x in vectors)
        if len(set(mapping)) == len(vectors):
            maps.append(mapping)
    need(len(set(maps)) == len(maps), "distinct matrices give distinct maps")
    return maps


def word(h, d, p, pinv, q, qinv, add, sub):
    """Literal D-=H; F_P; D+=H; F_Q; D=-D; D+=H."""
    d = sub[d][h]
    h, d = p[d], pinv[h]
    d = add[d][h]
    h, d = q[d], qinv[h]
    d = sub[0][d]
    return h, add[d][h]


def automorphism_census(modulus, dimension):
    vectors, index, add, sub = group(modulus, dimension)
    maps = linear_maps(modulus, dimension, vectors, index)
    inverses = [inverse(p) for p in maps]
    size = len(vectors)
    digest, images, compatible, evaluations = sha256(), Counter(), 0, 0
    optimum = Counter()
    for p, pinv in zip(maps, inverses):
        defect = tuple(sub[p[p[x]]][x] for x in range(size))
        floor, predicted_best = len(set(defect)), size * defect.count(0)
        best, minimum_image = 0, size**2
        for q, qinv in zip(maps, inverses):
            image, agrees, output = set(), 0, bytearray()
            for h in range(size):
                for d in range(size):
                    oh, od = word(h, d, p, pinv, q, qinv, add, sub)
                    output.extend((oh, od))
                    image.add((sub[oh][d], sub[od][h]))
                    agrees += (oh, od) == (d, h)
            evaluations += size**2
            digest.update(output)
            images[len(image)] += 1
            expected = q == p and floor == 1
            need((agrees == size**2) == expected, "two-callee iff criterion")
            need(len(image) >= floor, "first-bank error image lower bound")
            need(agrees * len(image) == size**2, "kernel-image count")
            if q == p:
                need(len(image) == floor and agrees == predicted_best,
                     "same map attains optimum")
            compatible += expected
            best, minimum_image = max(best, agrees), min(minimum_image, len(image))
        need(best == predicted_best and minimum_image == floor, "optimal second callee")
        optimum[best] += 1
    return dict(modulus=modulus, dimension=dimension, automorphisms=len(maps),
                ordered_callee_pairs=len(maps)**2, address_pairs=evaluations,
                compatible_pairs=compatible,
                error_image_sizes={str(k): v for k, v in sorted(images.items())},
                optimal_agreements={str(k): v for k, v in sorted(optimum.items())},
                complete_endpoint_sha256=digest.hexdigest())


def weighted_map(weights, modulus, vectors, index):
    need(all(gcd(a, modulus) == 1 for a in weights), "unit weights required")
    return tuple(index[tuple(a*x % modulus for a, x in zip(weights, reversed(v)))]
                 for v in vectors)


def weighted_census(modulus, dimension):
    vectors, index, add, sub = group(modulus, dimension)
    units = [a for a in range(modulus) if gcd(a, modulus) == 1]
    size, compatible, evaluations = len(vectors), 0, 0
    digest, histogram = sha256(), Counter()
    for weights in product(units, repeat=dimension):
        p = weighted_map(weights, modulus, vectors, index)
        pinv = inverse(p)
        defect = [(a*b-1) % modulus for a, b in zip(weights, reversed(weights))]
        expected_count = size * prod(gcd(modulus, x) for x in defect)
        count, output = 0, bytearray()
        for h in range(size):
            for d in range(size):
                actual = word(h, d, p, pinv, p, pinv, add, sub)
                delta = sub[d][h]
                error = sub[p[p[delta]]][delta]
                need(actual == (add[d][error], add[h][error]), "equal-callee error identity")
                count += actual == (d, h)
                output.extend(actual)
        need(count == expected_count, "composite gcd count")
        need((count == size**2) == all(x == 0 for x in defect), "reciprocal weights")
        compatible += count == size**2
        histogram[count] += 1
        evaluations += size**2
        digest.update(output)
    return dict(modulus=modulus, dimension=dimension, weight_tuples=len(units)**dimension,
                address_pairs=evaluations, compatible_tuples=compatible,
                agreement_histogram={str(k): v for k, v in sorted(histogram.items())},
                complete_endpoint_sha256=digest.hexdigest())


def controls():
    vectors, index, add, sub = group(9, 2)
    p = weighted_map((4, 1), 9, vectors, index)
    pinv = inverse(p)
    h, d = index[(0, 0)], index[(1, 0)]
    oh, od = word(h, d, p, pinv, p, pinv, add, sub)
    need((vectors[oh], vectors[od]) == ((4, 0), (3, 0)), "lift-only failure witness")
    need(sub[oh][od] == sub[d][h], "difference-only check misses error")
    for x in range(len(vectors)):
        for y in range(len(vectors)):
            a, b = p[y], pinv[x]
            need((p[b], pinv[a]) == (x, y), "each weighted F is involutive")
    need(word(h, d, p, pinv, pinv, p, add, sub) != (d, h), "inverse second fails")
    good = weighted_map((4, 7), 9, vectors, index)
    need(all(good[good[x]] == x for x in range(len(vectors))), "nontrivial positive")
    need(3*3 % 8 == 1 and 3 not in (1, 7), "two-adic middle-weight boundary")
    try:
        weighted_map((3, 1), 9, vectors, index)
    except ValueError as error:
        need(str(error) == "unit weights required", "intended nonunit rejection")
    else:
        raise ValueError("nonunit admitted")
    return dict(lift_witness=dict(modulus=9, weights=[4, 1], h=[0, 0], d=[1, 0],
                                  actual_h=list(vectors[oh]), actual_d=list(vectors[od])),
                controls=["involutive_F_insufficient", "inverse_second_fails",
                          "difference_only_check_misses_error", "reciprocal_weights_pass",
                          "two_adic_middle_units", "nonunits_rejected"])


def run():
    return dict(automorphism_censuses=[automorphism_census(m, n) for m, n in
                                     ((2, 2), (3, 2), (2, 3), (4, 2))],
                weighted_censuses=[weighted_census(m, n) for m, n in
                                  ((2, 1), (3, 1), (4, 1), (8, 1), (9, 1),
                                   (3, 2), (4, 2), (8, 2), (9, 2))],
                controls=controls())
