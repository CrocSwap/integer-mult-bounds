#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact radius-three search for the inverse 3-cycle pair in F2[S3]."""

import hashlib
import itertools
import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def compose(p, q):
    """Permutation product p*q, applying q first."""
    return tuple(p[q[i]] for i in range(3))


GROUP = tuple(itertools.permutations(range(3)))
GID = {g: i for i, g in enumerate(GROUP)}
TABLE = tuple(tuple(GID[compose(a, b)] for b in GROUP) for a in GROUP)
E = GID[(0, 1, 2)]
X = GID[(1, 0, 2)]  # (12)
Y = GID[(0, 2, 1)]  # (23)
XY = TABLE[X][Y]
YX = TABLE[Y][X]


def rank_one_idempotents():
    # N = u v^T; over F2 this parameterization is unique for rank one.
    return tuple(
        (u, v)
        for u in range(1, 4)
        for v in range(1, 4)
        if ((u & v).bit_count() & 1)
    )


IDEMPOTENTS = rank_one_idempotents()
GENERATORS = tuple((g, u, v) for g in (X, Y) for u, v in IDEMPOTENTS)


def permute_mask(g, mask):
    out = 0
    for a in range(len(GROUP)):
        if (mask >> a) & 1:
            out ^= 1 << TABLE[g][a]
    return out


def right_permute_mask(mask, g):
    out = 0
    for a in range(len(GROUP)):
        if (mask >> a) & 1:
            out ^= 1 << TABLE[a][g]
    return out


PERMUTED_RIGHT = tuple(
    tuple(right_permute_mask(mask, g) for mask in range(1 << len(GROUP)))
    for g in (X, Y)
)
LABEL_INDEX = {X: 0, Y: 1}


def unpack(state):
    return tuple((state >> (6 * i)) & 63 for i in range(4))


def pack(cells):
    return sum(cell << (6 * i) for i, cell in enumerate(cells))


def step(state, generator):
    """Right-multiply a 2x2 F2[S3] matrix by one paid factor."""
    g, u, v = generator
    cells = list(unpack(state))
    p = PERMUTED_RIGHT[LABEL_INDEX[g]]
    for row in range(2):
        value = 0
        for middle in range(2):
            if (u >> middle) & 1:
                value ^= cells[2 * row + middle]
        delta = value ^ p[value]  # right-multiply by ([g]+[1])
        for col in range(2):
            if (v >> col) & 1:
                cells[2 * row + col] ^= delta
    return pack(cells)


def convolve(left, right):
    out = 0
    for a in range(6):
        if (left >> a) & 1:
            for b in range(6):
                if (right >> b) & 1:
                    out ^= 1 << TABLE[a][b]
    return out


def formal_product(word):
    """Independent literal 2x2 matrix product with six-bit group coefficients."""
    out = [1 << E, 0, 0, 1 << E]
    for index in word:
        g, u, v = GENERATORS[index]
        factor = [0, 0, 0, 0]
        for row in range(2):
            for col in range(2):
                cell = (1 << E) if row == col else 0
                if ((u >> row) & 1) and ((v >> col) & 1):
                    cell ^= (1 << E) ^ (1 << g)
                factor[2 * row + col] = cell
        next_out = [0, 0, 0, 0]
        for row in range(2):
            for col in range(2):
                value = 0
                for middle in range(2):
                    value ^= convolve(out[2 * row + middle], factor[2 * middle + col])
                next_out[2 * row + col] = value
        out = next_out
    return tuple(out)


IDENTITY = pack((1 << E, 0, 0, 1 << E))
TARGET_CELLS = (1 << XY, 0, 0, 1 << YX)
TARGET = pack(TARGET_CELLS)


def ball(start, depth):
    found = {start: ()}
    frontier = [start]
    layers = [1]
    for _ in range(depth):
        next_frontier = []
        for state in frontier:
            prefix = found[state]
            for i, generator in enumerate(GENERATORS):
                value = step(state, generator)
                if value not in found:
                    found[value] = prefix + (i,)
                    next_frontier.append(value)
        frontier = next_frontier
        layers.append(len(frontier))
    return found, layers


def group_geodesics():
    words = {E: ()}
    frontier = [E]
    while frontier:
        nxt = []
        for value in frontier:
            for label in (X, Y):
                image = TABLE[value][label]
                if image not in words:
                    words[image] = words[value] + (label,)
                    nxt.append(image)
        frontier = nxt
    return words


def direct_word(left, right, geodesics):
    first = tuple(GENERATORS.index((g, 1, 1)) for g in geodesics[left])
    second = tuple(GENERATORS.index((g, 2, 2)) for g in geodesics[right])
    return first + second


def run():
    need(len(GROUP) == 6 and len(set(GROUP)) == 6, "S3 group inventory")
    need(all(TABLE[TABLE[a][b]][c] == TABLE[a][TABLE[b][c]]
             for a, b, c in itertools.product(range(6), repeat=3)), "associativity")
    need(TABLE[X][X] == E and TABLE[Y][Y] == E, "transposition involutions")
    need(XY != YX and TABLE[XY][XY] == YX and TABLE[XY][YX] == E,
         "inverse 3-cycle target")
    need(len(IDEMPOTENTS) == 6 and len(set(IDEMPOTENTS)) == 6,
         "complete rank-one idempotents")
    need(len(GENERATORS) == 12 and len(set(GENERATORS)) == 12,
         "complete paid alphabet")

    found, layers = ball(IDENTITY, 5)
    geodesics = group_geodesics()
    need(set(geodesics) == set(range(6)), "transposition alphabet does not generate S3")

    # Compare the packed transition with literal products for every ordered
    # word through length three, and replay every canonical path in the full
    # radius-five ball using literal group-algebra matrix multiplication.
    checked = 0
    for length in range(4):
        for word in itertools.product(range(len(GENERATORS)), repeat=length):
            packed_state = IDENTITY
            for index in word:
                packed_state = step(packed_state, GENERATORS[index])
            literal = formal_product(word)
            need(unpack(packed_state) == literal, "packed/literal product disagreement")
            checked += 1

    path_replays = 0
    for state, word in found.items():
        need(pack(formal_product(word)) == state, "radius-five path formal replay")
        path_replays += 1

    pair_rows = []
    omission_controls = 0
    direct_histogram = {}
    exact_histogram = {}
    for left, right in itertools.product(range(6), repeat=2):
        cells = (1 << left, 0, 0, 1 << right)
        target = pack(cells)
        direct = direct_word(left, right, geodesics)
        direct_cost = len(direct)
        # The direct construction costs at most six. If a target is absent
        # from the complete radius-five ball, its exact minimum is therefore 6.
        exact_cost = len(found[target]) if target in found else 6
        need(exact_cost == direct_cost, "two targets share a paid call")
        need(formal_product(direct) == cells, "direct target-pair construction")
        if target in found:
            need(pack(formal_product(found[target])) == target,
                 "shortest target-pair witness replay")
            need(len(found[target]) == direct_cost,
                 "shortest paid word does not match direct bill")
        else:
            need(direct_cost == 6, "radius-five absence with a shorter direct bill")
        for i in range(direct_cost):
            need(formal_product(direct[:i] + direct[i + 1:]) != cells,
                 "omitted direct factor still reaches target")
            omission_controls += 1
        direct_histogram[str(direct_cost)] = direct_histogram.get(str(direct_cost), 0) + 1
        exact_histogram[str(exact_cost)] = exact_histogram.get(str(exact_cost), 0) + 1
        pair_rows.append({
            "left_group_element": left,
            "right_group_element": right,
            "direct_calls": direct_cost,
            "minimum_calls": exact_cost,
            "target_in_radius_five": target in found,
            "direct_generator_indices": list(direct),
        })

    state_digest = hashlib.sha256(
        b"".join(state.to_bytes(4, "little") for state in sorted(found))
    ).hexdigest()
    xyx = TABLE[TABLE[X][Y]][X]
    inverse_pair = next(p for p in pair_rows
                        if p["left_group_element"] == XY and p["right_group_element"] == YX)

    certificate = {
        "status": "PASS_S3_TWO_TARGET_NO_SHARING",
        "group": "S3",
        "group_elements": [list(p) for p in GROUP],
        "transpositions": {"x": X, "y": Y},
        "target_group_elements": {"xy": XY, "yx": YX, "xyx_yxy": xyx},
        "registers": 2,
        "generators": [[g, u, v] for g, u, v in GENERATORS],
        "rank_one_idempotents": [[u, v] for u, v in IDEMPOTENTS],
        "identity_radius_five_layers": layers,
        "identity_radius_five_state_count": len(found),
        "identity_radius_five_state_sha256": state_digest,
        "ordered_words_independently_checked_through_length_three": checked,
        "radius_five_canonical_paths_formally_replayed": path_replays,
        "target_pair_count": len(pair_rows),
        "direct_call_histogram": dict(sorted(direct_histogram.items())),
        "minimum_call_histogram": dict(sorted(exact_histogram.items())),
        "all_two_target_minima_equal_separate_geodesic_bills": True,
        "target_pairs": pair_rows,
        "inverse_three_cycle_pair_minimum": inverse_pair["minimum_calls"],
        "longest_element_pair_minimum": next(
            p["minimum_calls"] for p in pair_rows
            if p["left_group_element"] == xyx and p["right_group_element"] == xyx
        ),
        "direct_omission_controls": omission_controls,
        "packed_transition_independently_replayed": True,
        "free_scalar_mixing": "captured by all rank-one idempotents after augmentation normalization",
        "new_kappa_claimed": False,
    }
    return certificate


def main():
    result = run()
    path = HERE / "CERTIFICATE.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(path.is_file(), "missing CERTIFICATE.json")
        expected = json.loads(path.read_text())
        need(result == expected, "certificate mismatch")
    digest = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(result["status"], "layers=" + str(result["identity_radius_five_layers"]),
          "pairs=" + str(result["target_pair_count"]), "minima=" + str(result["minimum_call_histogram"]),
          "sha256=" + digest)


if __name__ == "__main__":
    main()
