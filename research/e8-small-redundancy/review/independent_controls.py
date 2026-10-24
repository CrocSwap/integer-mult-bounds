"""Check proof premises and rejection controls without package imports."""

import gzip
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parents[1] / "early-remainder-audit/packages/e8-small-redundancy"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows, field=None):
    basis = {}
    for values in rows:
        row = [Fraction(x) for x in values] if field is None else [x % field for x in values]
        for pivot, other in sorted(basis.items()):
            value = row[pivot]
            row = [x - value * y for x, y in zip(row, other)]
            if field is not None:
                row = [x % field for x in row]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is not None:
            scale = 1 / row[pivot] if field is None else pow(row[pivot], -1, field)
            row = [x * scale for x in row]
            if field is not None:
                row = [x % field for x in row]
            basis[pivot] = row
    return len(basis)


def bit_basis(words):
    pivots = {}
    for word in words:
        for pivot, row in sorted(pivots.items(), reverse=True):
            if (word >> pivot) & 1:
                word ^= row
        if word:
            pivots[word.bit_length() - 1] = word
    return list(pivots.values())


def coordinates(simple, vector):
    matrix = [[Fraction(simple[j][i]) for j in range(8)] + [Fraction(vector[i])]
              for i in range(8)]
    for col in range(8):
        pivot = next(i for i in range(col, 8) if matrix[i][col])
        matrix[col], matrix[pivot] = matrix[pivot], matrix[col]
        scale = matrix[col][col]
        matrix[col] = [x / scale for x in matrix[col]]
        for row in range(8):
            if row != col:
                scale = matrix[row][col]
                matrix[row] = [x - scale * y for x, y in zip(matrix[row], matrix[col])]
    return [row[-1] for row in matrix]


roots = json.loads(gzip.decompress((PACKAGE / "inputs/bit-word.json.gz").read_bytes()))["lines"]
simple = json.loads((PACKAGE / "binary/parabolic-results.json").read_text())["simple_roots"]
signed_roots = roots + [[-x for x in row] for row in roots]
require(rank(simple) == 8, "Simple roots must be independent")
for root in signed_roots:
    values = coordinates(simple, root)
    require(all(x.denominator == 1 for x in values), "Root coordinates must be integral")
    require(all(x >= 0 for x in values) or all(x <= 0 for x in values),
            "Root coordinates must have one sign")

kernel = [sum((1 + sum(x * y for x, y in zip(q, r)) // 2) % 2 << j
              for j, r in enumerate(roots)) for q in roots]
basis = bit_basis(kernel)
require(len(basis) == 9, "The binary corrector must have rank nine")
code = [0]
for row in basis:
    code += [word ^ row for word in code]
require(len(set(code)) == 512, "The code enumeration must be complete")

coset = [word ^ 1 for word in code]
require(1 not in code, "The coordinate unit must lie outside the code")
histogram = Counter()
for word in coset:
    support = [roots[j] for j in range(120) if (word >> j) & 1]
    # A modular full-rank witness proves rational full rank.
    value = 8 if rank(support, 101) == 8 else rank(support)
    histogram[value] += 1
require(histogram == {1: 1, 7: 1, 8: 510}, "The unit coset must attain defect eight")
require(rank([roots[j] for j in range(120) if ((kernel[0] ^ 1) >> j) & 1]) == 7,
        "A root-row support loses full rank when its own root is removed")
linear_kernel = [sum((sum(x * y for x, y in zip(q, r)) // 2) % 2 << j
                     for j, r in enumerate(roots)) for q in roots]
require(len(bit_basis(linear_kernel)) == 8, "The affine constant changes the matrix rank")

controls = []
with tempfile.TemporaryDirectory(prefix="e8-independent-controls-") as temporary:
    copy = Path(temporary) / "package"
    shutil.copytree(PACKAGE, copy, ignore=shutil.ignore_patterns("__pycache__"))

    def rejected(name, command, expected, extra_env=None):
        completed = subprocess.run(command, capture_output=True, text=True, timeout=300,
                                   env={**os.environ, **(extra_env or {})})
        require(completed.returncode != 0 and expected in completed.stderr,
                "Control did not fail at the required check: " + name)
        controls.append({"name": name, "command": command, "exit_code": completed.returncode,
                         "environment_additions": extra_env or {},
                         "expected_stderr": expected, "actual_stderr": completed.stderr})

    path = copy / "inputs/bit-word.json.gz"
    original = path.read_bytes()
    path.write_bytes(original[:-1] + bytes([original[-1] ^ 1]))
    rejected("input_hash_corruption", [sys.executable, "-B", str(copy / "verify.py")],
             "Source hash mismatch: inputs/bit-word.json.gz")
    path.write_bytes(original)

    bit_word = json.loads(gzip.decompress(original))
    bit_word["lines"] = bit_word["lines"][:-1]
    path.write_bytes(gzip.compress(json.dumps(bit_word).encode(), mtime=0))
    rejected("one_root_omitted", [sys.executable, "-B", str(copy / "binary/parabolic_check.py")],
             "AssertionError")
    path.write_bytes(original)

    bit_word = json.loads(gzip.decompress(original))
    bit_word["lines"][0][0] += 5
    path.write_bytes(gzip.compress(json.dumps(bit_word).encode(), mtime=0))
    manifest_path = copy / "SOURCE-HASHES.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["inputs/bit-word.json.gz"] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    rejected("assertions_active_with_inherited_optimization",
             [sys.executable, "-I", "-O", "-B", str(copy / "verify.py")],
             "assert all(sum(x*x for x in q) == 4 for q in all_roots)",
             {"PYTHONOPTIMIZE": "1"})
    path.write_bytes(original)
    manifest["inputs/bit-word.json.gz"] = hashlib.sha256(original).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    path = copy / "inputs/complex-word.json.gz"
    original = path.read_bytes()
    complex_word = json.loads(gzip.decompress(original))
    complex_word["ports"][0], complex_word["ports"][1] = complex_word["ports"][1], complex_word["ports"][0]
    path.write_bytes(gzip.compress(json.dumps(complex_word).encode(), mtime=0))
    rejected("certificate_port_order_changed",
             [sys.executable, "-B", str(copy / "coordinate/coordinate_totals_rigidity.py"), str(path)],
             "AssertionError")
    path.write_bytes(original)

    name = "coordinate/coordinate_totals_rigidity.json"
    path = copy / name
    receipt = json.loads(path.read_text())
    receipt["results"][0]["rational_rank"] = 62
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    manifest_path = copy / "SOURCE-HASHES.json"
    manifest = json.loads(manifest_path.read_text())
    manifest[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    rejected("wrong_receipt_with_updated_manifest", [sys.executable, "-B", str(copy / "verify.py")],
             "Coordinate receipt mismatch")

result = {"status": "PASS", "package": str(PACKAGE), "independent_imports": [],
          "signed_root_expansions": 240, "simple_basis_rank": 8,
          "root_coordinates_integral_and_one_sign": True, "binary_kernel_rank": len(basis),
          "linear_kernel_without_affine_constant_rank": len(bit_basis(linear_kernel)),
          "unit_coset_support_rank_histogram": dict(sorted(histogram.items())),
          "unit_coset_total_defect": sum((8 - k) * v for k, v in histogram.items()),
          "root_row_with_own_root_removed_rank": 7, "rejection_controls": controls,
          "scope": "Independent finite premises and boundary controls. Not a formal proof of every factorization."}
(HERE / "independent-controls.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS_E8_INDEPENDENT_CONTROLS root_expansions=240 coset_words=512 rejected=5")
