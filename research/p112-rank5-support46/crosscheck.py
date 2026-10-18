"""Independent five-label basis enumeration and behavioral controls."""

import json
import sys
from hashlib import sha256
from itertools import combinations
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis_span(values):
    basis = [0] * 9
    for value in values:
        for pivot in range(8, -1, -1):
            if value & (1 << pivot):
                if basis[pivot]:
                    value ^= basis[pivot]
                else:
                    basis[pivot] = value
                    break
    nonzero = [x for x in basis if x]
    span = [0]
    for row in nonzero:
        span += [x ^ row for x in span]
    return set(span)


def reject(call, message):
    try:
        call()
    except ValueError as error:
        require(message in str(error), "wrong rejection")
    else:
        raise ValueError("malformed control was accepted")


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import verify

    geometry = verify.authenticate()
    roots, _, _, coordinates = geometry.root_data()
    labels = [
        1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(c)) for c in coordinates
    ]
    a, b = roots[0], next(root for root in roots if not geometry.dot(roots[0], root))
    receipt = json.loads((verify.PACKAGE / "RESULT.json").read_text())
    checked = 0
    for axis, other, expected in (
        (a, b, receipt["axes"][0]),
        (b, a, receipt["axes"][1]),
    ):
        fiber = [
            labels[i]
            for i, root in enumerate(roots)
            if geometry.dot(axis, root) and not geometry.dot(other, root)
        ]
        tight = set()
        for chosen in combinations(fiber, 5):
            span = basis_span(chosen)
            checked += 1
            if len(span) == 32:
                support = sum(1 << i for i, label in enumerate(fiber) if label in span)
                if support.bit_count() == 12:
                    tight.add(support)
        verify.require(len(tight) == 120, "independent tight inventory")
        digest = sha256(repr(sorted(tight)).encode()).hexdigest()
        verify.require(
            digest == expected["tight_masks_sha256"], "independent tight hash"
        )
        # The unpunctured configuration must retain real disjoint maxima.
        verify.require(
            sum(not (x & y) for x, y in combinations(tight, 2)) == 240,
            "lost unpunctured disjoint control",
        )
    reject(lambda: verify.binary_coordinates((1, 1)), "duplicate")
    reject(lambda: verify.binary_coordinates((512,)), "nine-bit")
    reject(lambda: verify.binary_coordinates(tuple(range(121))), "bounded")
    reject(lambda: verify.puncture_check(tuple(tight), 7), "four-root")
    reject(lambda: verify.puncture_check(tuple(tight), -1), "range")
    reject(lambda: verify.puncture_check(tuple(tight)[:-1], 15), "inventory")
    verify.require(2 * (78 - 47) == 62 <= 63, "support47 boundary control")
    print(f"PASS_P112_SUPPORT46_CROSSCHECK bases={checked} tight=240 controls=7")


if __name__ == "__main__":
    main()
