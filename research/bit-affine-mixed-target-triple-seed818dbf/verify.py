#!/usr/bin/env python3
"""Exhaust the five-call ball for a three-register AGL_2(F2) target."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
GROUP_ORDER = 24
MASK = (1 << GROUP_ORDER) - 1
SLOT_BITS = GROUP_ORDER
NREG = 3
NGEN = 84
IDENTITY = (1 << 0) | (1 << (SLOT_BITS * 4)) | (1 << (SLOT_BITS * 8))


def affine(matrix: tuple[tuple[int, int], tuple[int, int]], shift: tuple[int, int],
           points: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    result = []
    point_index = {point: i for i, point in enumerate(points)}
    for x, y in points:
        image = ((matrix[0][0] * x ^ matrix[0][1] * y) ^ shift[0],
                 (matrix[1][0] * x ^ matrix[1][1] * y) ^ shift[1])
        result.append(point_index[image])
    return tuple(result)


def build_group():
    # Points are encoded by the ordered pairs (x0,x1), with x0 in bit zero.
    points = ((0, 0), (1, 0), (0, 1), (1, 1))
    elements = tuple(itertools.permutations(range(4)))
    ids = {p: i for i, p in enumerate(elements)}
    multiplication = tuple(tuple(ids[tuple(p[q[i]] for i in range(4))]
                                 for q in elements) for p in elements)
    identity = ids[tuple(range(4))]
    a = ids[affine(((1, 1), (0, 1)), (0, 0), points)]
    b = ids[affine(((1, 0), (1, 1)), (0, 0), points)]
    tx = ids[affine(((1, 0), (0, 1)), (1, 0), points)]
    h = multiplication[multiplication[multiplication[a][b]][a]][tx]
    direct_h = ids[affine(((0, 1), (1, 0)), (0, 1), points)]
    assert h == direct_h
    assert len({a, b, tx}) == 3
    assert all(multiplication[g][g] == identity for g in (a, b, tx))
    assert multiplication[a][b] != multiplication[b][a]
    return elements, multiplication, identity, a, b, tx, h


ELEMENTS, GMUL, GID, A, B, TX, H = build_group()


def projectors() -> list[tuple[int, int]]:
    result = []
    for u in range(1, 8):
        for v in range(1, 8):
            if ((u & v).bit_count() & 1) == 1:
                result.append((u, v))
    return result


PROJECTORS = projectors()
GENERATORS = tuple((u, v, g) for u, v in PROJECTORS for g in (A, B, TX))
GENERATOR_ID = {gate: i for i, gate in enumerate(GENERATORS)}
assert len(ELEMENTS) == GROUP_ORDER and len(PROJECTORS) == 28
assert len(GENERATORS) == NGEN and len(GENERATOR_ID) == NGEN


def f2_rank(vectors: tuple[int, ...]) -> int:
    pivots: dict[int, int] = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def displacement_rank(label: int) -> int:
    # From the point action recover [A-I | b], using 0, e0, e1.
    points = ((0, 0), (1, 0), (0, 1), (1, 1))
    image0 = points[ELEMENTS[label][0]]
    image_e0 = points[ELEMENTS[label][1]]
    image_e1 = points[ELEMENTS[label][2]]
    b = image0[0] | (image0[1] << 1)
    col0 = ((image_e0[0] ^ image0[0] ^ 1)
            | ((image_e0[1] ^ image0[1]) << 1))
    col1 = ((image_e1[0] ^ image0[0])
            | ((image_e1[1] ^ image0[1] ^ 1) << 1))
    return f2_rank((col0, col1, b))


RANK_A, RANK_B, RANK_H = (displacement_rank(g) for g in (A, B, H))
assert (RANK_A, RANK_B, RANK_H) == (1, 1, 2)


def get_entry(state: int, row: int, col: int) -> int:
    return (state >> (SLOT_BITS * (NREG * row + col))) & MASK


def translated(mask: int, label: int, side: str) -> int:
    """Multiply each group basis term by [label] on the requested side."""
    result = 0
    while mask:
        low = mask & -mask
        element = low.bit_length() - 1
        product = GMUL[element][label] if side == "right" else GMUL[label][element]
        result |= 1 << product
        mask ^= low
    return result


def multiply_gate_right(state: int, code: int) -> int:
    u, v, label = GENERATORS[code]
    result = state
    for row in range(NREG):
        row_sum = 0
        for k in range(NREG):
            if (u >> k) & 1:
                row_sum ^= get_entry(state, row, k)
        correction = row_sum ^ translated(row_sum, label, "right")
        for col in range(NREG):
            if (v >> col) & 1:
                result ^= correction << (SLOT_BITS * (NREG * row + col))
    return result


def multiply_gate_left(state: int, code: int) -> int:
    u, v, label = GENERATORS[code]
    result = state
    for col in range(NREG):
        col_sum = 0
        for k in range(NREG):
            if (v >> k) & 1:
                col_sum ^= get_entry(state, k, col)
        correction = col_sum ^ translated(col_sum, label, "left")
        for row in range(NREG):
            if (u >> row) & 1:
                result ^= correction << (SLOT_BITS * (NREG * row + col))
    return result


def encode_diagonal(labels: tuple[int, int, int]) -> int:
    value = 0
    for i, label in enumerate(labels):
        value |= (1 << label) << (SLOT_BITS * (NREG * i + i))
    return value


def replay(codes: tuple[int, ...]) -> int:
    value = IDENTITY
    for code in codes:
        value = multiply_gate_right(value, code)
    return value


def decode_path(code: int, length: int) -> tuple[int, ...]:
    result = [0] * length
    for i in range(length - 1, -1, -1):
        result[i] = code & 127
        code >>= 7
    return tuple(result)


def digest_layer(layer: list[int]) -> str:
    digest = hashlib.sha256()
    for state in layer:
        digest.update(state.to_bytes(27, "little"))
    return digest.hexdigest()


def explicit_gate_state(code: int) -> int:
    u, v, label = GENERATORS[code]
    delta = (1 << label) ^ (1 << GID)
    state = IDENTITY
    for row in range(NREG):
        if (u >> row) & 1:
            for col in range(NREG):
                if (v >> col) & 1:
                    state ^= delta << (SLOT_BITS * (NREG * row + col))
    return state


def exact_small_matmul(left: int, right: int) -> int:
    """Independent formal matrix/group-algebra product for control cases."""
    result = 0
    for i in range(NREG):
        for j in range(NREG):
            entry = 0
            for k in range(NREG):
                x = get_entry(left, i, k)
                y = get_entry(right, k, j)
                while x:
                    xb = x & -x
                    gx = xb.bit_length() - 1
                    yy = y
                    while yy:
                        yb = yy & -yy
                        gy = yb.bit_length() - 1
                        entry ^= 1 << GMUL[gx][gy]
                        yy ^= yb
                    x ^= xb
            result |= entry << (SLOT_BITS * (NREG * i + j))
    return result


def join_search(target: int):
    layers = [[IDENTITY]]
    paths = {IDENTITY: (0, 0)}  # matrix -> (shortest depth, packed generator word)
    for depth in range(1, 4):
        next_layer = []
        for state in layers[-1]:
            prev_code = paths[state][1]
            for code in range(NGEN):
                child = multiply_gate_right(state, code)
                if child not in paths:
                    paths[child] = (depth, (prev_code << 7) | code)
                    next_layer.append(child)
        layers.append(next_layer)

    probe_count = 0
    hits: list[tuple[int, tuple[int, ...]]] = []
    for depth in range(3):
        for prefix_state in layers[depth]:
            prefix_code = paths[prefix_state][1]
            prefix = decode_path(prefix_code, depth)
            remainder = target
            # Left multiplication in this order yields prefix^{-1} * target;
            # every paid generator is an involution.
            for code in prefix:
                remainder = multiply_gate_left(remainder, code)
            probe_count += 1
            found = paths.get(remainder)
            if found is not None:
                suffix_depth, suffix_code = found
                suffix = decode_path(suffix_code, suffix_depth)
                candidate = prefix + suffix
                assert replay(candidate) == target
                hits.append((len(candidate), candidate))

    best = min(hits, default=None, key=lambda hit: (hit[0], hit[1]))
    return layers, probe_count, best


def label_name(g: int) -> str:
    return {A: "a", B: "b", TX: "t_x"}[g]


def gate_label(code: int) -> dict[str, object]:
    u, v, g = GENERATORS[code]
    return {"u": u, "v": v, "label": label_name(g)}


def run() -> dict[str, object]:
    direct_codes = tuple(GENERATOR_ID[(1 << i, 1 << i, g)]
                         for i, g in ((0, A), (1, B), (2, A), (2, B), (2, A), (2, TX)))
    target = encode_diagonal((A, B, H))
    direct = replay(direct_codes)
    assert direct == target

    # Check all paid gates' exact matrices and involution property, plus an
    # independent dense product implementation on representative states.
    gate_checks = 0
    for code in range(NGEN):
        gate = explicit_gate_state(code)
        assert multiply_gate_right(IDENTITY, code) == gate
        assert multiply_gate_left(IDENTITY, code) == gate
        assert multiply_gate_right(gate, code) == IDENTITY
        assert multiply_gate_left(gate, code) == IDENTITY
        gate_checks += 1
    independent_product_checks = 0
    for x, y in ((direct_codes[:1], direct_codes[1:2]),
                 (direct_codes[2:4], direct_codes[4:6]),
                 (direct_codes[:3], direct_codes[3:])):
        left, right = replay(x), replay(y)
        assert exact_small_matmul(left, right) == replay(x + y)
        independent_product_checks += 1

    # Each direct-call omission and a wrong affine label must fail the endpoint.
    omission_controls = 0
    for i in range(len(direct_codes)):
        assert replay(direct_codes[:i] + direct_codes[i + 1:]) != target
        omission_controls += 1
    wrong_target = encode_diagonal((A, B, A))
    assert direct != wrong_target
    wrong_label_codes = list(direct_codes)
    wrong_label_codes[-1] = GENERATOR_ID[(1 << 2, 1 << 2, A)]
    assert replay(tuple(wrong_label_codes)) != target

    layers, probes, best = join_search(target)
    if best is None:
        minimum = 6
        assert direct == target
    else:
        minimum = best[0]
        assert minimum <= 5
        assert replay(best[1]) == target

    # The direct six-call word and rank-four relaxation bound are both exact
    # statements about this paid alphabet; the exhaustive join decides whether
    # the former can be improved by register mixing.
    layer_counts = [len(layer) for layer in layers]
    return {
        "schema_version": 1,
        "seed": "818dbf90f2581f79a4e4150cdd77e415",
        "model": "Mat_3(F2[AGL_2(F2)])",
        "group_order": len(ELEMENTS),
        "coordinate_labels": {"a": A, "b": B, "t_x": TX, "h": H},
        "paid_projectors": len(PROJECTORS),
        "paid_generators": NGEN,
        "target": ["a", "b", "h=a*b*a*t_x"],
        "direct_word": [gate_label(c) for c in direct_codes],
        "direct_cost": len(direct_codes),
        "displacement_ranks": {"a": RANK_A, "b": RANK_B, "h": RANK_H},
        "rank_relaxation_lower_bound": RANK_A + RANK_B + RANK_H,
        "radius": 3,
        "layer_counts": layer_counts,
        "layer_sha256_in_bfs_order": [digest_layer(layer) for layer in layers],
        "left_join_probes": probes,
        "shortest_hit_through_five": None if best is None else {
            "cost": best[0], "word": [gate_label(c) for c in best[1]]},
        "minimum_in_paid_alphabet_through_direct_cost": minimum,
        "exact_minimum_claim": ("six in this 84-generator alphabet" if best is None
                                 else "the recorded word length is exact locally"),
        "controls": {
            "all_generator_matrix_and_inverse_checks": gate_checks,
            "independent_dense_product_checks": independent_product_checks,
            "omitted_direct_call_checks": omission_controls,
            "wrong_target_check": True,
            "wrong_label_check": True,
        },
        "scope": "formal all-dirty register identities in the stated paid alphabet; no supplier or kappa claim",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="write EXPECTED.json from the current exact replay")
    args = parser.parse_args()
    result = run()
    expected_path = PACKAGE / "EXPECTED.json"
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.emit:
        expected_path.write_text(rendered, encoding="utf-8", newline="\n")
    else:
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        if expected != result:
            raise SystemExit("FAIL: replay differs from EXPECTED.json")
    print("PASS_BIT_AFFINE_MIXED_TARGET_TRIPLE "
          f"group={len(ELEMENTS)} generators={NGEN} layers="
          f"{','.join(map(str, result['layer_counts']))} probes={result['left_join_probes']} "
          f"minimum={result['minimum_in_paid_alphabet_through_direct_cost']} "
          f"hit={result['shortest_hit_through_five'] is not None}")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError, KeyError) as exc:
        print(f"FAIL_BIT_AFFINE_MIXED_TARGET_TRIPLE {exc}", file=sys.stderr)
        raise
