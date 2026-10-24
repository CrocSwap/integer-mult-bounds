#!/usr/bin/env python3
"""Exact finite ingredients of the affine A5 minimum proof (Apache-2.0).

Krzysztof Wojt, with substantial OpenAI Codex assistance.
The completeness argument is in README.md; a finite rank test alone is not it.
All matrices use binary column encoding and act on the left.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def identity(n: int) -> tuple[int, ...]:
    return tuple(1 << i for i in range(n))


def act(matrix: tuple[int, ...], vector: int) -> int:
    out = 0
    while vector:
        bit = vector & -vector
        out ^= matrix[bit.bit_length() - 1]
        vector ^= bit
    return out


def compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(act(left, column) for column in right)


def power(matrix: tuple[int, ...], exponent: int) -> tuple[int, ...]:
    out = identity(len(matrix))
    for _ in range(exponent):
        out = compose(matrix, out)
    return out


def f4_multiply(a: int, b: int) -> int:
    polynomial = (a if b & 1 else 0) ^ (a << 1 if b & 2 else 0)
    return polynomial ^ (7 if polynomial & 4 else 0)


def binary_natural(matrix: tuple[int, ...]) -> tuple[int, ...]:
    out = []
    for v in (1, 2, 4, 8):
        lo = f4_multiply(matrix[0], v & 3) ^ f4_multiply(matrix[1], v >> 2)
        hi = f4_multiply(matrix[2], v & 3) ^ f4_multiply(matrix[3], v >> 2)
        out.append(lo | (hi << 2))
    return tuple(out)


def perm_compose(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[i]] for i in range(5))


def parity_action(permutation: tuple[int, ...]) -> tuple[int, ...]:
    # Coordinates v0,...,v3 represent (v0,...,v3,sum(vi)) in F2^5.
    return tuple(((1 << permutation[i]) ^ (1 << permutation[4])) & 15
                 for i in range(4))


def group_model() -> tuple[list[tuple[int, ...]], list[tuple[int, ...]],
                           dict[str, tuple[tuple[int, ...], tuple[int, ...]]]]:
    x, y = (1, 0, 3, 2, 4), (2, 1, 4, 3, 0)
    permutations = [tuple(range(5))]
    words: list[tuple[int, ...]] = [()]
    lookup = {permutations[0]: 0}
    for p, word in zip(permutations, words):
        for k, generator in enumerate((x, y)):
            q = perm_compose(generator, p)
            if q not in lookup:
                lookup[q] = len(permutations)
                permutations.append(q)
                words.append(word + (k,))
    require(len(permutations) == 60, "A5 order")
    modules = {
        "natural": (binary_natural((1, 1, 0, 1)), binary_natural((0, 2, 3, 1))),
        "augmentation": (parity_action(x), parity_action(y)),
    }
    return permutations, words, modules


def evaluate_word(generators: tuple[tuple[int, ...], tuple[int, ...]],
                  word: tuple[int, ...]) -> tuple[int, ...]:
    out = identity(len(generators[0]))
    for letter in word:
        out = compose(generators[letter], out)
    return out


def check_representation(permutations: list[tuple[int, ...]],
                         words: list[tuple[int, ...]],
                         generators: tuple[tuple[int, ...], tuple[int, ...]]) -> list[tuple[int, ...]]:
    images = [evaluate_word(generators, w) for w in words]
    lookup = {p: i for i, p in enumerate(permutations)}
    for i, p in enumerate(permutations):
        for j, q in enumerate(permutations):
            require(compose(images[i], images[j]) == images[lookup[perm_compose(p, q)]],
                    "representation multiplication")
    require(len(set(images)) == 60, "group faithfulness")
    return images


def independent_basis(vectors: list[int]) -> list[int]:
    pivots: dict[int, int] = {}
    for value in vectors:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return list(pivots.values())


def permutation_kernel(images: list[tuple[int, ...]]) -> tuple[int, list[int]]:
    size = 1 << len(images[0])
    pivots: dict[int, tuple[int, int]] = {}
    kernel = []
    for i, matrix in enumerate(images):
        column = sum(1 << (v * size + act(matrix, v)) for v in range(size))
        combination = 1 << i
        while column:
            pivot = column.bit_length() - 1
            if pivot in pivots:
                old_column, old_combination = pivots[pivot]
                column ^= old_column
                combination ^= old_combination
            else:
                pivots[pivot] = (column, combination)
                break
        if not column:
            require(combination != 0, "nonzero dependence")
            kernel.append(combination)
    require(len(independent_basis(kernel)) == len(kernel), "independent kernel witnesses")
    require(len(pivots) + len(kernel) == 60, "rank-nullity")
    return len(pivots), kernel


def check_annihilator(images: list[tuple[int, ...]], mask: int) -> None:
    require(0 < mask < (1 << len(images)), "nonzero valid group-algebra witness")
    selected = [matrix for i, matrix in enumerate(images) if mask >> i & 1]
    # Independent of the flattened-matrix rank calculation: cancel actual output
    # basis vectors, for every input basis vector of the permutation module.
    for v in range(1 << len(images[0])):
        outputs: set[int] = set()
        for matrix in selected:
            w = act(matrix, v)
            if w in outputs:
                outputs.remove(w)
            else:
                outputs.add(w)
        require(not outputs, "annihilator acts nontrivially")


def extension(rx: tuple[int, ...], ry: tuple[int, ...],
              rows: tuple[int, ...], columns: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    a, b = len(rows), len(columns)
    n = a + 4 + b
    unit = identity(n)
    x, y = list(unit), list(unit)
    for j in range(4):
        x[a + j] = (rx[j] << a) | sum(((r >> j) & 1) << i for i, r in enumerate(rows))
        y[a + j] = ry[j] << a
    for j, column in enumerate(columns):
        x[a + 4 + j] ^= column << a
    defect = power(compose(tuple(x), tuple(y)), 5)
    require(all(defect[j] == unit[j] for j in range(a + 4)), "fifth-power defect outside corner")
    for j in range(b):
        delta = defect[a + 4 + j] ^ unit[a + 4 + j]
        require(delta < (1 << a), "fifth-power defect outside corner")
        x[a + 4 + j] ^= delta
    result = tuple(x), tuple(y)
    d = compose(rx, ry)
    d3 = power(d, 3)
    corner_map = compose(ry, tuple(u ^ v for u, v in zip(d, d3)))
    for j, column in enumerate(columns):
        middle = act(corner_map, column)
        formula = sum(((r & middle).bit_count() % 2) << i for i, r in enumerate(rows))
        require(result[0][a + 4 + j] & ((1 << a) - 1) == formula,
                "explicit corner C=A Ry(D+D^3)B")
    require(power(result[0], 2) == unit, "extension x-square")
    require(power(result[1], 3) == unit, "extension y-cube")
    require(power(compose(*result), 5) == unit, "extension xy-fifth")
    return result


def orbit_sizes(images: list[tuple[int, ...]]) -> list[int]:
    unseen = set(range(1 << len(images[0])))
    sizes = []
    while unseen:
        orbit = {act(g, min(unseen)) for g in images}
        require(orbit <= unseen, "disjoint complete orbits")
        sizes.append(len(orbit))
        unseen -= orbit
    return sorted(sizes)


def rejected(call, label: str) -> str:
    try:
        call()
    except ValueError:
        return label
    raise ValueError("negative control accepted: " + label)


def check_subquotient(core: tuple[tuple[int, ...], tuple[int, ...]],
                     target: tuple[tuple[int, ...], tuple[int, ...]],
                     p: tuple[int, ...], q: tuple[int, ...]) -> int:
    # P is row-encoded, Q column-encoded. Take an actual section of Q,
    # rather than treating a bottom vector-space complement as fixed.
    section = {}
    for v in range(4):
        section.setdefault(act(q, v), v)

    def map_point(v: int) -> int:
        t, m, z = v & 3, v >> 2 & 15, v >> 6
        pt = sum(((r & t).bit_count() % 2) << i for i, r in enumerate(p))
        return pt | (m << 2) | (section[z] << 6)

    domain = [v for v in range(256) if v >> 6 in section]
    image = {map_point(v) for v in domain}
    p_image = {sum(((r & t).bit_count() % 2) << i for i, r in enumerate(p)) for t in range(4)}
    require(len(image) == len(p_image) * 16 * len(section), "subquotient core size")
    for v in domain:
        for g, h in zip(core, target):
            require(map_point(act(g, v)) == act(h, map_point(v)), "subquotient equivariance")
        if map_point(v) == 0:
            require(v < 4 and all((r & v).bit_count() % 2 == 0 for r in p),
                    "subquotient kernel outside top ker(P)")
    return len(domain)


def core_checks() -> dict:
    permutations, words, modules = group_model()
    results = {}
    controls = []
    for name, (rx, ry) in modules.items():
        check_representation(permutations, words, (rx, ry))
        delta = tuple(c ^ (1 << j) for j, c in enumerate(rx))
        require(len(independent_basis(list(delta))) == 2, "rank(x-I)=2")
        ker = [v for v in range(16) if act(rx, v) == v]
        coker = [r for r in range(16) if all((r & c).bit_count() % 2 == (r >> j & 1)
                                            for j, c in enumerate(rx))]
        rows, columns = tuple(independent_basis(coker)), tuple(independent_basis(ker))
        require(len(rows) == len(columns) == 2, "two-dimensional extension spaces")
        require(all((r & c).bit_count() % 2 == 0 for r in rows for c in columns), "AB=0")
        xy = compose(rx, ry)
        require(power(xy, 5) == identity(4), "order-five simple action")
        require(all(act(xy, v) != v for v in range(1, 16)), "no xy-fixed vector")
        core = extension(rx, ry, rows, columns)
        images = check_representation(permutations, words, core)
        rank, kernel = permutation_kernel(images)
        require(rank < 60, "universal extension must have a nonzero algebra kernel")
        for mask in kernel:
            check_annihilator(images, mask)
        controls.append(rejected(lambda: check_annihilator(images, 1), name + ":identity-is-not-zero"))
        missing_term = kernel[0] ^ (kernel[0] & -kernel[0])
        controls.append(rejected(lambda: check_annihilator(images, missing_term), name + ":missing-witness-term"))
        controls.append(rejected(lambda: check_annihilator(images, 0), name + ":zero-witness"))
        wrong_corner = list(core[0])
        wrong_corner[6] ^= 1
        controls.append(rejected(
            lambda: check_representation(permutations, words, (tuple(wrong_corner), core[1])),
            name + ":wrong-extension-corner"))
        controls.append(rejected(
            lambda: require(act(core[0], 64) == 64, "bottom complement is not fixed"),
            name + ":bottom-complement-is-not-a-fixed-summand"))

        # Check C(P A0,B0 Q) = P C0 Q for every binary 2x2 P,Q.
        # This finite bilinearity check corroborates the all-size block proof.
        corner_checks = 0
        subquotient_points = 0
        for p, q in product(product(range(4), repeat=2), repeat=2):
            new_rows = tuple(act(rows, r) for r in p)
            new_columns = tuple(act(columns, c) for c in q)
            built_x, built_y = extension(rx, ry, new_rows, new_columns)
            for j in range(2):
                old_corner = act(tuple(core[0][6 + k] & 3 for k in range(2)), q[j])
                predicted = sum(((r & old_corner).bit_count() % 2) << i for i, r in enumerate(p))
                require(built_x[6 + j] & 3 == predicted, "corner bilinearity")
            subquotient_points += check_subquotient(core, (built_x, built_y), p, q)
            corner_checks += 1
        results[name] = {
            "simple_x_columns": list(rx), "simple_y_columns": list(ry),
            "fixed_columns_basis": list(columns), "fixed_rows_basis": list(rows),
            "universal_x_columns": list(core[0]), "universal_y_columns": list(core[1]),
            "permutation_algebra_rank": rank,
            "kernel_basis_hex": [f"{m:015x}" for m in kernel],
            "orbit_size_histogram": dict(sorted(Counter(orbit_sizes(images)).items())),
            "bilinear_corner_cases": corner_checks,
            "subquotient_domain_points_checked": subquotient_points,
            "first_witness_permutations": [list(p) for i, p in enumerate(permutations) if kernel[0] >> i & 1],
        }
    # The predecessor's upper bound needs only one regular orbit, not a rerun of
    # its CNOT/data programs or predecessor endpoint searches.
    nx, ny = modules["natural"]
    doubled = tuple(tuple(g) + tuple(c << 4 for c in g) for g in (nx, ny))
    images = check_representation(permutations, words, doubled)
    regular_seed = 1 | (4 << 4)
    require(len({act(g, regular_seed) for g in images}) == 60, "eight-bit regular orbit")
    controls.append(rejected(lambda: check_annihilator(images, (1 << 60) - 1), "eight-bit-norm-does-not-vanish"))
    return {"schema": "a5-affine-address-minimum/v1", "minimum_affine_bits": 8,
            "group_order": 60, "group_basis_permutations": [list(p) for p in permutations],
            "universal_extensions": results, "upper_regular_seed": regular_seed,
            "controls": controls}


def calculate() -> dict:
    # -I deliberately removes the script directory; load only this explicitly
    # selected sibling source, with no third-party or predecessor imports.
    import runpy
    algebra = runpy.run_path(str(HERE / "check_algebra.py"))["run_checks"]()
    result = core_checks()
    for name, x_key, y_key, algebra_name in (
        ("natural", "X_as_F2_matrix", "Y_as_F2_matrix", "natural"),
        ("augmentation", "X_matrix", "Y_matrix", "augmentation_subspace"),
    ):
        for key, letter in ((x_key, "x"), (y_key, "y")):
            columns = result["universal_extensions"][name][f"simple_{letter}_columns"]
            rows = [[column >> i & 1 for column in columns] for i in range(4)]
            # The independent checker orders the natural basis as
            # (1,0),(0,1),(w,0),(0,w); this file groups each F4 coordinate.
            order = (0, 2, 1, 3) if name == "natural" else (0, 1, 2, 3)
            rows = [[rows[i][j] for j in order] for i in order]
            require(rows == algebra["modules"][algebra_name][key], "independent simple-module binding")
    result["simple_module_coordinate_binding"] = {"natural": [0, 2, 1, 3], "augmentation": [0, 1, 2, 3]}
    result["simple_quotient"] = algebra
    root = HERE.parent.parent
    source_rows = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["files"]
    bound_inputs = {}
    for row in source_rows:
        if row["usage"] == "input":
            digest = hashlib.sha256((root / row["path"]).read_bytes()).hexdigest()
            require(digest == row["sha256"], "source hash: " + row["path"])
            bound_inputs[row["path"]] = digest
    require(len(bound_inputs) == 2, "both predecessor inputs bound")
    predecessor = json.loads((root / "research/a5-eight-bit-carrier/RESULT.json").read_text(encoding="utf-8"))
    require(predecessor["result"]["group_order"] == 60, "predecessor group order")
    require(predecessor["result"]["faithful_formal_basis_columns"] == 60, "predecessor upper-bound scope")
    result["source_sha256"] = bound_inputs
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true", help="explicitly regenerate RESULT.json")
    args = parser.parse_args()
    result = calculate()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_result:
        (HERE / "RESULT.json").write_text(encoded, encoding="utf-8")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(json.loads(encoded) == expected, "committed result mismatch")
    print("PASS_A5_AFFINE_ADDRESS_MINIMUM bits=8 result_sha256=" + hashlib.sha256(encoded.encode()).hexdigest())


if __name__ == "__main__":
    main()
