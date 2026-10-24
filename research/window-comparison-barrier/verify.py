#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact finite evidence for the comparison-barrier proof; standard library only."""

import argparse
import ast
from fractions import Fraction as F
from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational_matrix(matrix):
    n = len(matrix)
    require(1 <= n <= 8, "matrix dimension must lie in 1..8")
    require(all(len(row) == n for row in matrix), "square matrix required")
    require(all(type(x) in (int, F) for row in matrix for x in row),
            "exact rational matrix required")
    result = tuple(tuple(F(x) for x in row) for row in matrix)
    require(all(max(abs(x.numerator).bit_length(), x.denominator.bit_length())
                <= 128 for row in result for x in row), "input height limit")
    return result


def matvec(matrix, vector):
    return tuple(sum((a * b for a, b in zip(row, vector)), F(0))
                 for row in matrix)


def solve(matrix, rhs):
    """Small rational elimination used only to construct the new barrier."""
    matrix = rational_matrix(matrix)
    n = len(matrix)
    require(len(rhs) == n, "right-hand side dimension")
    rows = [list(row) + [F(rhs[i])] for i, row in enumerate(matrix)]
    for k in range(n):
        pivots = [i for i in range(k, n) if rows[i][k]]
        require(bool(pivots), "singular matrix")
        pivot = pivots[0]
        rows[k], rows[pivot] = rows[pivot], rows[k]
        value = rows[k][k]
        rows[k] = [x / value for x in rows[k]]
        for i in range(n):
            if i != k:
                value = rows[i][k]
                rows[i] = [x - value * y for x, y in zip(rows[i], rows[k])]
    answer = tuple(row[-1] for row in rows)
    require(matvec(matrix, answer) == tuple(map(F, rhs)), "solve residual")
    return answer


def comparison(matrix):
    matrix = rational_matrix(matrix)
    return tuple(tuple(abs(x) if i == j else -abs(x)
                       for j, x in enumerate(row))
                 for i, row in enumerate(matrix))


def certify(matrix, barrier, envelope):
    matrix = rational_matrix(matrix)
    n = len(matrix)
    require(len(barrier) == len(envelope) == n, "certificate dimension")
    require(all(type(x) in (int, F) for x in (*barrier, *envelope)),
            "exact rational certificate required")
    require(all(x > 0 for x in barrier), "positive barrier required")
    require(all(x > 0 for x in envelope), "positive residual envelope required")
    image = matvec(comparison(matrix), barrier)
    require(all(a >= b for a, b in zip(image, envelope)),
            "comparison supersolution required")
    return max(barrier)


def determinant(matrix):
    """Independent Leibniz oracle, bounded to dimension four; no elimination."""
    n = len(matrix)
    require(n <= 4 and all(len(row) == n for row in matrix), "oracle dimension")
    total = F(0)
    for order in permutations(range(n)):
        inversions = sum(order[i] > order[j] for i in range(n) for j in range(i+1, n))
        term = F(-1 if inversions % 2 else 1)
        for i, j in enumerate(order):
            term *= matrix[i][j]
        total += term
    return total


def cofactor_solve(matrix, rhs):
    denominator = determinant(matrix)
    require(denominator != 0, "oracle nonsingularity")
    answer = []
    for j in range(len(matrix)):
        replaced = [[rhs[i] if k == j else x for k, x in enumerate(row)]
                    for i, row in enumerate(matrix)]
        answer.append(determinant(replaced) / denominator)
    return tuple(answer)


def literal_number(node):
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return F(node.value)
    require(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "Fraction" and not node.keywords
            and 1 <= len(node.args) <= 2, "rational fixture literal")
    values = []
    for arg in node.args:
        sign = 1
        if isinstance(arg, ast.UnaryOp) and isinstance(arg.op, ast.USub):
            sign, arg = -1, arg.operand
        require(isinstance(arg, ast.Constant) and type(arg.value) is int,
                "integer Fraction argument")
        values.append(sign * arg.value)
    return F(*values)


def source_fixture(root, package):
    sources = json.loads((package / "SOURCES.json").read_text())
    for entry in sources["files"]:
        if entry["usage"] == "input":
            data = (root / entry["path"]).read_bytes()
            require(len(data) <= 1_048_576, "source size limit")
            require(sha256(data).hexdigest() == entry["sha256"], "source hash mismatch")
    path = root / "research/sliding-window-inverse/inputs/gaussian_check_setup.py"
    tree = ast.parse(path.read_text())
    nodes = tuple(ast.walk(tree))
    require(len(nodes) <= 20_000, "source syntax size limit")
    candidates = []
    for node in nodes:
        if not isinstance(node, ast.Assign):
            continue
        named = any(isinstance(t, ast.Name) and t.id == "source" for t in node.targets)
        if named and isinstance(node.value, ast.List) and len(node.value.elts) == 3:
            rows = node.value.elts
            require(all(isinstance(row, ast.List) and len(row.elts) == 3 for row in rows),
                    "three-by-three source fixture")
            candidates.append(tuple(tuple(literal_number(x) for x in row.elts) for row in rows))
    require(len(candidates) == 1, "unique source fixture")
    return rational_matrix(candidates[0])


def principal(matrix, labels):
    return tuple(tuple(matrix[i][j] for j in labels) for i in labels)


def window_checks(matrix, barrier):
    """Every ordered principal window, every residual-box vertex, every sign."""
    n = len(matrix)
    sites = tuple((i, j) for i in range(n) for j in range(n) if i != j and matrix[i][j])
    require(len(sites) <= 6, "finite sign enumeration limit")
    windows = tuple(labels for width in range(1, n+1)
                    for labels in permutations(range(n), width))
    cases = 0
    digest = sha256()
    for signs in product((-1, 1), repeat=len(sites)):
        variant = [list(row) for row in matrix]
        for (i, j), sign in zip(sites, signs):
            variant[i][j] = sign * abs(matrix[i][j])
        for labels in windows:
            block = principal(variant, labels)
            bound = tuple(barrier[i] for i in labels)
            certify(block, bound, (F(1),) * len(labels))
            for rhs in product((-1, 1), repeat=len(labels)):
                actual = cofactor_solve(block, rhs)
                require(all(abs(x) <= h for x, h in zip(actual, bound)), "window bound")
                digest.update((str((signs, labels, rhs, actual)) + "\n").encode())
                cases += 1
    return len(windows), 2 ** len(sites), cases, digest.hexdigest()


def recovery_checks(matrix, barrier):
    cases = 0
    residual = F(7, 5)
    require(residual * max(barrier) == F(581, 1170) < F(1, 2), "new recovery margin")
    require(residual * F(4, 11) == F(28, 55) > F(1, 2), "old certificate inconclusive")
    for width in range(1, len(matrix)+1):
        for labels in permutations(range(len(matrix)), width):
            block = principal(matrix, labels)
            exact = tuple(F(2*i-3) for i in labels)
            for signs in product((-1, 1), repeat=width):
                rhs = tuple(residual * sign for sign in signs)
                error = cofactor_solve(block, rhs)
                approximate = tuple(a+b for a, b in zip(exact, error))
                recovered = tuple((x+F(1, 2)).numerator // (x+F(1, 2)).denominator
                                  for x in approximate)
                require(recovered == exact, "literal known-integer recovery")
                require(matvec(block, error) == rhs, "physical residual identity")
                cases += 1
    return cases


def rejection_checks(matrix, barrier):
    rejected = 0
    controls = [([], (), ()), ([[1, 2]], (1,), (1,)),
                ([[1.0]], (1,), (1,)), ([[1]], (0,), (1,)),
                ([[1]], (1,), (0,)), ([[1]], (1,), (1.0,)),
                ([[1]], (F(1, 2),), (1,)), ([[1, 2], [2, 1]], (1, 1), (1, 1)),
                (matrix, (F(1, 4), F(1, 5), F(1, 3)), (1, 1, 1))]
    for k in range(len(barrier)):
        lowered = tuple(x-F(i == k, 1000) for i, x in enumerate(barrier))
        controls.append((matrix, lowered, (1, 1, 1)))
    for args in controls:
        try:
            certify(*args)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("negative certificate accepted")
    return rejected


def evidence(root, package):
    matrix = source_fixture(root, package)
    ones = (F(1),) * len(matrix)
    comp = comparison(matrix)
    barrier = solve(comp, ones)
    require(barrier == (F(49, 156), F(10, 39), F(83, 234)), "new barrier value")
    bound = certify(matrix, barrier, ones)
    require(bound == F(83, 234), "improved constant")
    old_gap = min(matvec(comp, ones))
    require(old_gap == F(11, 4) and 1/old_gap-bound == F(23, 2574), "exact gain")
    require(cofactor_solve(comp, ones) == barrier, "independent sharpness witness")
    threshold = F(1, 2)/bound
    error = cofactor_solve(comp, (threshold,) * len(matrix))
    require(max(error) == F(1, 2), "strict threshold boundary")
    windows, signs, vertices, digest = window_checks(matrix, barrier)
    recovered = recovery_checks(matrix, barrier)
    rejected = rejection_checks(matrix, barrier)
    return {"claim_type": "scoped proof with finite corroboration",
            "barrier": list(map(str, barrier)), "bound": str(bound),
            "old_bound": str(1/old_gap), "gain": str(1/old_gap-bound),
            "recovery_threshold": str(threshold), "ordered_windows": windows,
            "sign_variants": signs, "residual_vertices": vertices,
            "known_integer_recoveries": recovered, "rejected_controls": rejected,
            "case_sha256": digest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write a new receipt outside the checkout")
    args = parser.parse_args()
    package = Path(__file__).resolve().parent
    root = package.parent.parent
    result = evidence(root, package)
    print(json.dumps(result, sort_keys=True))
    if args.receipt is not None:
        output = args.receipt.expanduser().resolve()
        require(not output.is_relative_to(root), "receipt must be outside checkout")
        hashes = {p.name: sha256(p.read_bytes()).hexdigest()
                  for p in sorted(package.iterdir()) if p.is_file()}
        receipt = {"result": result, "package_sha256": hashes}
        with output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("PASS_WINDOW_COMPARISON_BARRIER")


if __name__ == "__main__":
    main()
