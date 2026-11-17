"""Exact finite corroboration of the six-point sojourn exclusion.

Produced by Nick Petalas. Apache-2.0.
No predecessor executable, Git object, network or optional dependency is used.
"""

import hashlib
import itertools
import json
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sumset(left, right):
    return {x ^ y for x in left for y in right}


def translated_masks(points):
    return tuple(sum(1 << (x ^ shift) for x in points) for shift in range(16))


def complete_census():
    """Every six-set and every three-set in the four-dimensional group."""
    triples = tuple(itertools.combinations(range(16), 3))
    histogram = [0] * 17
    six_sets = 0
    for six in itertools.combinations(range(16), 6):
        shifts = translated_masks(six)
        for a, b, c in triples:
            cardinality = (shifts[a] | shifts[b] | shifts[c]).bit_count()
            require(cardinality < 16, "three translates covered the group")
            histogram[cardinality] += 1
        six_sets += 1
    require(six_sets == 8008, "incomplete six-set domain")
    require(len(triples) == 560, "incomplete triple domain")
    require(sum(histogram) == 4484480, "incomplete paired domain")
    return six_sets, len(triples), histogram


def independent_normalized_census():
    """Literal sets, independently of the bit-mask union implementation."""
    histogram = [0] * 17
    for six in itertools.combinations(range(16), 6):
        union = sumset((0, 1, 2), six)
        require(len(union) < 16, "normalized triple covered the group")
        # The three-point set spans H={0,1,2,3}; inspect its four cosets.
        for representative in (0, 4, 8, 12):
            coset = {representative ^ h for h in range(4)}
            if len(set(six) & coset) <= 1:
                require(len(union & coset) <= 3, "coset argument failed")
        histogram[len(union)] += 1
    require(sum(histogram) == 8008, "incomplete normalized domain")
    return histogram


def fiber_fixture():
    six = (0, 1, 2, 3, 4, 8)
    four = (0, 4, 8, 12)
    require(sumset(four, six) == set(range(16)), "sharp fiber fixture failed")
    q0 = {v | (w << 4) for v in four for w in range(8)}
    q1 = set(six)
    require(len(q0) == 32 and len(q1) == 6, "bad layer cardinalities")
    require(sumset(q0, q1) == set(range(128)), "cross-layer fixture failed")
    # Cross-layer sharpness alone must not be called a universal prefix set.
    require(sumset(q0, q0) | sumset(q1, q1) != set(range(128)),
            "fixture unexpectedly satisfies the same-layer condition")
    return q0, q1


def boundary_controls(q0, q1):
    # Four translates can cover with six points, so 'three' is essential.
    require(len(sumset((0, 4, 8, 12), q1)) == 16,
            "four-translate counterexample lost")
    # In an odd cyclic group the affine-plane argument does not apply.
    cyclic = {(a + b) % 5 for a in (0, 1, 2) for b in (0, 3)}
    require(cyclic == set(range(5)), "odd-group counterexample lost")
    # Half the group is a sharp threshold for the three-translate lemma.
    half = (0, 1, 4, 5, 8, 9, 12, 13)
    require(sumset((0, 1, 2), half) == set(range(16)),
            "half-group boundary fixture lost")
    # Omitting an entire quotient fiber destroys the cross-layer cover.
    omitted = {x for x in q0 if x >> 4 != 7}
    require(len(omitted) == 28 and len(sumset(omitted, q1)) == 112,
            "missing-fiber control failed")
    return 4


def main():
    six_sets, triples, histogram = complete_census()
    independent = independent_normalized_census()
    require(histogram == [560 * count for count in independent],
            "affine-normalized and full censuses disagree")
    q0, q1 = fiber_fixture()
    controls = boundary_controls(q0, q1)
    require(len(q0) + len(q1) == 38, "sharp cross-layer total changed")
    package = Path(__file__).resolve().parent
    files = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "verify.py")
    receipt = {
        "status": "PASS_RANK4_SIX_POINT_SOJOURN",
        "claim_type": "scoped proof with exact finite corroboration",
        "six_sets": six_sets,
        "triples": triples,
        "paired_sumsets": sum(histogram),
        "full_histogram": histogram,
        "normalized_histogram": independent,
        "complementary_layer_floor": 32,
        "cross_layer_total_floor": 38,
        "sharp_cross_layer_sizes": [len(q0), len(q1)],
        "boundary_controls": controls,
        "python": platform.python_version(),
        "sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                   for name in files},
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
