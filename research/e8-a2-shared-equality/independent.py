"""Dual three-space enumeration; no imports from the primal enumerator.

Produced by Nick Petalas. Apache-2.0.
"""

from itertools import combinations
import json


def check(condition, message):
    if not condition:
        raise ValueError(message)


def qform(x):
    return sum((x >> (2 * i) & 1) * (x >> (2 * i + 1) & 1)
               for i in range(4)) % 2


def pairing(x, y):
    return sum(((x >> (2 * i) & 1) * (y >> (2 * i + 1) & 1)
                + (y >> (2 * i) & 1) * (x >> (2 * i + 1) & 1))
               for i in range(4)) % 2


def dual_spaces():
    """U=N+<r>, with r nonzero singular, N an anisotropic plane in r-perp."""
    roots = tuple(x for x in range(256) if qform(x))
    planes = {tuple(sorted((x, y, x ^ y)))
              for x, y in combinations(roots, 2) if pairing(x, y)}
    spaces = {}
    for radical in range(1, 256):
        if qform(radical):
            continue
        for plane in planes:
            if all(not pairing(radical, x) for x in plane):
                vectors = tuple(sorted((0, radical, *plane,
                                        *(x ^ radical for x in plane))))
                spaces[vectors] = radical
    check(len(spaces) == 7560, "complete dual three-space inventory")
    return spaces


def complement_planes(vectors, radical):
    candidates = set()
    for x, y in combinations(vectors[1:], 2):
        if pairing(x, y):
            plane = tuple(sorted((x, y, x ^ y)))
            check(radical not in plane and all(qform(z) for z in plane),
                  "four anisotropic complements")
            candidates.add(plane)
    check(len(candidates) == 4, "complement plane count")
    return tuple(sorted(candidates))


def affine_cosets(vectors, radical):
    # Canonical cosets use syndrome values against every member of U.
    cosets = {}
    for x in range(256):
        syndrome = tuple(pairing(x, y) for y in vectors[1:])
        cosets.setdefault(syndrome, []).append(x)
    check(len(cosets) == 8 and all(len(c) == 32 for c in cosets.values()),
          "complete affine five-space cosets")
    selected = tuple(tuple(c) for c in cosets.values() if pairing(c[0], radical))
    check(len(selected) == 4, "nonzero radical character")
    return selected


def incident_fibers(coset, planes):
    a = coset[0]
    entries, zero_points = [], 0
    for plane in planes:
        projection = tuple(p for p in (0, *plane)
                           if all(pairing(a ^ p, x) == 0 for x in plane))
        check(len(projection) == 1, "unique orthogonal projection")
        point = projection[0]
        if point:
            check(point not in coset, "singleton excluded from the equality support")
            entries.append((plane, point))
        else:
            zero_points += 1
    check(len(entries) == 3 and zero_points == 1, "three valid and one zero projection")
    return tuple(sorted(entries))


def independent_incidence():
    incidence = {}
    coset_count = 0
    for vectors, radical in dual_spaces().items():
        planes = complement_planes(vectors, radical)
        for coset in affine_cosets(vectors, radical):
            support = tuple(x for x in coset if qform(x))
            check(len(support) == 16, "balanced sixteen-root support")
            mask = sum(1 << x for x in support)
            check(mask not in incidence, "distinct affine supports")
            incidence[mask] = incident_fibers(coset, planes)
            coset_count += 1
    check(coset_count == 30240, "complete dual support inventory")
    return incidence, {"dual_three_spaces": 7560, "affine_cosets": coset_count,
                       "zero_projection_exclusions": coset_count}


if __name__ == "__main__":
    incidence, counts = independent_incidence()
    print(json.dumps({"supports": len(incidence), "dual_checks": counts}, sort_keys=True))
