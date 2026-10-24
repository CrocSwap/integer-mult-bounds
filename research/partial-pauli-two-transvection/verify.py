"""Independent literal word census for the new low-length criterion."""

import hashlib
import itertools
import json
from pathlib import Path

from algebra import low_length, solve_pairings


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def pairing(v: int, w: int, n: int) -> int:
    result = 0
    for bit in range(n):
        result ^= ((v >> bit) & 1) * ((w >> (n + bit)) & 1)
        result ^= ((w >> bit) & 1) * ((v >> (n + bit)) & 1)
    return result


def action(matrix: tuple[int, ...], v: int) -> int:
    answer = 0
    for bit, column in enumerate(matrix):
        if (v >> bit) & 1:
            answer ^= column
    return answer


def literal_groups(n: int) -> tuple[dict[tuple[int, ...], int], int]:
    check(0 <= n <= 2, "literal census capacity")
    identity = tuple(1 << bit for bit in range(2 * n))
    distance = {identity: 0}
    frontier = [identity]
    for depth in range(1, 7):
        next_frontier = []
        for matrix in frontier:
            for axis in range(1, 1 << (2 * n)):
                moved = tuple(v ^ (axis if pairing(v, axis, n) else 0) for v in matrix)
                if moved not in distance:
                    distance[moved] = depth
                    next_frontier.append(moved)
        frontier = next_frontier
    check(not frontier, "Cayley search bound exhausted")
    literal = set()
    for columns in itertools.product(range(1 << (2 * n)), repeat=2 * n):
        if all(pairing(columns[i], columns[j], n) == pairing(identity[i], identity[j], n)
               for i in range(2 * n) for j in range(2 * n)):
            literal.add(columns)
    check(set(distance) == literal, "Cayley corpus differs from literal symplectic matrices")
    return distance, len(literal)


def subspace_bases(n: int) -> list[tuple[int, ...]]:
    spaces: dict[frozenset[int], tuple[int, ...]] = {frozenset({0}): ()}
    for dimension in range(2 * n):
        old_spaces = tuple(spaces.items())
        for space, basis in old_spaces:
            if len(basis) != dimension:
                continue
            for v in range(1, 1 << (2 * n)):
                if v not in space:
                    enlarged = frozenset(space | {x ^ v for x in space})
                    if enlarged not in spaces:
                        spaces[enlarged] = basis + (v,)
    return list(spaces.values())


def signed_image(phase: int, v: int, axes: tuple[int, ...], n: int) -> tuple[int, int]:
    """Conjugate i^phase X^x Z^z using the literal (I-i H_axis)/(1-i)."""
    mask = (1 << n) - 1
    for axis in axes:
        if pairing(v, axis, n):
            exponent = ((axis & mask) & (axis >> n)).bit_count()
            exponent += 2 * ((axis >> n) & (v & mask)).bit_count()
            phase = (phase + exponent - 1) % 4
            v ^= axis
    return phase, v


def signed_corrections(n: int, source: tuple[int, ...], target: tuple[int, ...],
                       axes: tuple[int, ...]) -> int:
    mask = (1 << n) - 1
    errors = []
    for v, w in zip(source, target):
        phase, image = signed_image(((v & mask) & (v >> n)).bit_count() % 4, v, axes, n)
        desired = ((w & mask) & (w >> n)).bit_count() % 4
        check(image == w and (phase - desired) % 2 == 0, "non-Hermitian image")
        errors.append(((phase - desired) // 2) & 1)
    count = 0
    for signs in itertools.product((0, 1), repeat=len(source)):
        wanted = tuple(sign ^ error for sign, error in zip(signs, errors))
        candidates = [a for a in range(1 << (2 * n))
                      if all(pairing(a, w, n) == bit for w, bit in zip(target, wanted))]
        check(len(candidates) == 1 << (2 * n - len(source)), "wrong sign-correction fiber")
        correction = solve_pairings(n, target, wanted)
        check(correction in candidates, "invalid Pauli correction")
        count += 1
    return count


def census(n: int) -> dict[str, object]:
    group, group_size = literal_groups(n)
    bases = subspace_bases(n)
    histogram = [0] * 7
    known = [0] * 4
    unknown = 0
    signed = 0
    digest = hashlib.sha256()
    for source in bases:
        restrictions: dict[tuple[int, ...], int] = {}
        for matrix, cost in group.items():
            target = tuple(action(matrix, v) for v in source)
            restrictions[target] = min(cost, restrictions.get(target, 7))
        for target, actual in sorted(restrictions.items()):
            result = low_length(n, source, target)
            histogram[actual] += 1
            check((result.minimum is not None and result.minimum <= 2) == (actual <= 2),
                  "incorrect zero/one/two-transvection decision")
            check(result.lower_bound <= actual, "false lower bound")
            if result.minimum is None:
                unknown += 1
            else:
                check(result.minimum == actual, "incorrect sharp length")
                known[result.minimum] += 1
                check(result.axes is not None, "missing attaining word")
                for v, w in zip(source, target):
                    for axis in result.axes:
                        v ^= axis if pairing(v, axis, n) else 0
                    check(v == w, "literal witness failure")
                signed += signed_corrections(n, source, target, result.axes)
            digest.update(json.dumps([source, target, actual, result.axes]).encode())
    return {"n": n, "group": group_size, "source_subspaces": len(bases),
            "contracts": sum(histogram), "length_histogram": histogram,
            "sharp_lengths_supplied": known, "lower_bound_only": unknown,
            "signed_basis_contracts": signed, "digest": digest.hexdigest()}


def controls() -> dict[str, int]:
    bad = [(-1, (), ()), (True, (), ()), (10, (), ()), (1, [], ()),
           (1, (1,), ()), (1, (0,), (1,)), (1, (True,), (1,)),
           (1, (4,), (1,)), (2, (1, 1), (1, 2)),
           (2, (1, 2), (1, 1)), (2, (1, 2), (1, 4))]
    for args in bad:
        try:
            low_length(*args)
        except ValueError:
            continue
        raise RuntimeError("malformed contract accepted")
    first = low_length(2, (1,), (3,))
    check(first.minimum == 2 and first.residual_form == ((0,),), "singular rank-one control")
    singular = low_length(2, (1, 2), (2, 3))
    check(singular.minimum is None and singular.lower_bound == 3
          and singular.residual_form == ((0, 0), (0, 0)), "singular rank-two control")
    source = (1, 2, 4, 8)
    target = (1, 2, 6, 9)
    third = low_length(2, source, target)
    check(third.minimum == 3 and third.residual_form == ((0, 1), (1, 0)),
          "alternating rank-two control")
    try:
        solve_pairings(1, (1, 1), (0, 1))
    except ValueError:
        return {"invalid_contracts": len(bad), "boundary_controls": 3,
                "inconsistent_systems": 1}
    raise RuntimeError("inconsistent pairing system accepted")


def large_examples() -> dict[str, int]:
    cases = 0
    for n in range(2, 10):
        e, f = 1, 2
        source = tuple(1 << bit for bit in range(2 * n))
        axes = (e, f, e ^ f)
        target = tuple(signed_image(0, v, axes, n)[1] for v in source)
        result = low_length(n, source, target)
        check(result.minimum == 3, "all-width alternating example")
        one = low_length(n, (1,), (3,))
        check(one.minimum == 2, "all-width singular rank-one example")
        cases += 2
    return {"fixed_examples_n2_through_n9": cases}


def main() -> None:
    output = {"censuses": [census(n) for n in range(3)],
              "controls": controls(), "higher_dimensions": large_examples()}
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "algebra.py", "verify.py")
    hashes = {}
    for name in names:
        data = (package / name).read_bytes()
        check(len(data) <= 1 << 20, "package file capacity")
        hashes[name] = hashlib.sha256(data).hexdigest()
    output["source_sha256"] = hashes
    print(json.dumps(output, sort_keys=True, indent=2))
    print("PASS_PARTIAL_PAULI_TWO_TRANSVECTION no_new_kappa")


if __name__ == "__main__":
    main()
