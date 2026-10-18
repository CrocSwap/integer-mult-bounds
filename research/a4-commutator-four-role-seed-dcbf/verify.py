#!/usr/bin/env python3
"""Replay the A4 direct controls on all 48 states and the bounded exact join."""

from __future__ import annotations

import itertools
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ROLES = 4


def compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p[q[i]] for i in range(4))


def inverse(p: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * 4
    for i, image in enumerate(p):
        out[image] = i
    return tuple(out)


def cycle3(x: int, y: int, z: int) -> tuple[int, ...]:
    out = [0, 1, 2, 3]
    out[x - 1], out[y - 1], out[z - 1] = y - 1, z - 1, x - 1
    return tuple(out)


def xor(left: dict[tuple[int, ...], int], right: dict[tuple[int, ...], int]):
    out = left.copy()
    for key, bit in right.items():
        value = out.get(key, 0) ^ bit
        if value:
            out[key] = value
        else:
            out.pop(key, None)
    return out


def algebra_product(left: dict[tuple[int, ...], int], right: dict[tuple[int, ...], int]):
    out: dict[tuple[int, ...], int] = {}
    for g in left:
        for h in right:
            product = compose(g, h)
            value = out.get(product, 0) ^ 1
            if value:
                out[product] = value
            else:
                out.pop(product, None)
    return out


def matrix_identity(one: tuple[int, ...]):
    out = [[{} for _ in range(ROLES)] for _ in range(ROLES)]
    for i in range(ROLES):
        out[i][i] = {one: 1}
    return out


def matrix_product(left, right):
    out = [[{} for _ in range(ROLES)] for _ in range(ROLES)]
    for i in range(ROLES):
        for k in range(ROLES):
            if not left[i][k]:
                continue
            for j in range(ROLES):
                if right[k][j]:
                    out[i][j] = xor(
                        out[i][j], algebra_product(left[i][k], right[k][j])
                    )
    return out


def factor(one: tuple[int, ...], label: tuple[int, ...], role: int):
    """D_N(label) for the rank-one diagonal projector on one role."""
    out = matrix_identity(one)
    # In F2, ([g] + 1)N toggles both coefficients in the selected entry.
    out[role][role] = xor(out[role][role], {label: 1, one: 1})
    return out


def target_matrix(one, targets):
    out = [[{} for _ in range(ROLES)] for _ in range(ROLES)]
    for i, label in enumerate(targets):
        out[i][i] = {label: 1}
    return out


def regular_outputs(matrix, group, one):
    """Return the output state set for each of the 48 regular basis inputs."""
    outputs = {}
    for source in range(ROLES):
        for address in group:
            image = set()
            for destination in range(ROLES):
                for group_element in matrix[source][destination]:
                    image.symmetric_difference_update(
                        {(destination, compose(address, group_element))}
                    )
            outputs[(source, address)] = frozenset(image)
    assert len(outputs) == 48
    return outputs


def verify_direct_controls() -> tuple[int, int, int, int]:
    identity = (0, 1, 2, 3)
    group = []
    for p in itertools.permutations(range(4)):
        inversions = sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4))
        if inversions % 2 == 0:
            group.append(p)
    group = sorted(group)
    assert len(group) == 12
    assert all(compose(g, h) in group for g in group for h in group)

    a = cycle3(1, 2, 3)
    b = cycle3(1, 2, 4)
    c = compose(compose(compose(a, b), inverse(a)), inverse(b))
    d = compose(a, b)
    assert c == compose(compose(compose(a, b), b), a)
    assert len({identity, a, b, c, d}) == 5
    assert all(label != identity for label in (a, b, c, d))
    assert compose(c, c) == identity and compose(d, d) == identity
    assert compose(compose(a, a), a) == identity
    assert compose(compose(b, b), b) == identity

    # The independent direct word is grouped by its four diagonal outputs:
    # a; b; a,b,b,a (=c); a,b (=d).
    word = [(a, 0), (b, 1), (a, 2), (b, 2), (b, 2), (a, 2), (a, 3), (b, 3)]
    identity_matrix_value = matrix_identity(identity)

    def replay(sequence):
        matrix = identity_matrix_value
        for label, role in sequence:
            matrix = matrix_product(matrix, factor(identity, label, role))
        return matrix

    expected = target_matrix(identity, [a, b, c, d])
    actual = replay(word)
    assert actual == expected, "eight-call direct word misses its exact F2[A4] target"

    expected_columns = regular_outputs(expected, group, identity)
    actual_columns = regular_outputs(actual, group, identity)
    assert actual_columns == expected_columns
    assert len(actual_columns) == 48

    # Controls: every deleted paid factor, a missing fourth output, a mutated
    # fourth label, and the uncredited six-call three-output predecessor.
    for omitted in range(len(word)):
        assert replay(word[:omitted] + word[omitted + 1 :]) != expected
    missing_fourth = target_matrix(identity, [a, b, c, identity])
    assert actual != missing_fourth
    mutated = list(word)
    mutated[-1] = (a, 3)
    assert replay(mutated) != expected

    old_three_output = target_matrix(identity, [a, b, c, identity])
    old_word = word[:6]
    assert replay(old_word) == old_three_output
    return len(group), len(actual_columns), len(word), len(word) - len(old_word)


def run_bounded_search() -> str:
    compiler = shutil.which("g++")
    if not compiler:
        raise RuntimeError("g++ is required to replay the exact bounded search")
    source = PACKAGE / "search.cpp"
    with tempfile.TemporaryDirectory(prefix="a4-commutator-") as temp:
        executable = Path(temp) / "a4-search"
        subprocess.run(
            [compiler, "-std=c++17", "-O3", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(executable)],
            cwd=ROOT,
            check=True,
            timeout=120,
        )
        result = subprocess.run(
            [str(executable)], cwd=ROOT, check=True, capture_output=True, text=True, timeout=120
        )
    required = (
        "PASS_A4_DIRECT_CONTROL order=12 roles=4 idempotents=120 factors=240 target_calls=8",
        "quotient_exponents a=1 b=2 c=0 d=0",
        "PASS_PLANTED_SIX_CALL_JOIN_CONTROL",
        "right_raw_by_length=1,240,57600,13824000 right_raw_total=13881841",
        "PASS_A4_NO_WORD_THROUGH_SIX",
        "left_prefixes_checked=1,240,57600,13824000 total=13881841",
        "scope=target_diag_a_b_commutator_ab; no_length7_or_supplier_claim",
    )
    for marker in required:
        if marker not in result.stdout:
            raise AssertionError(f"bounded search receipt missing: {marker}")
    if "PASS_A4_FOUR_ROLE_CONSTRUCTION" in result.stdout:
        raise AssertionError("search output conflicts with the scoped no-six receipt")
    return result.stdout


def main() -> None:
    group_size, columns, direct_calls, old_saving = verify_direct_controls()
    search_output = run_bounded_search()
    print("PASS_A4_INDEPENDENT_DIRECT_REPLAY group_order=12 basis_columns=48")
    print("direct_calls=8 old_three_output_calls=6 predecessor_saving=0")
    print("PASS_A4_COMPLETE_LENGTH_AT_MOST_SIX_JOIN")
    print(search_output, end="")
    assert (group_size, columns, direct_calls, old_saving) == (12, 48, 8, 2)


if __name__ == "__main__":
    main()
