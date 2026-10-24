"""Check the scalar contract and rejection controls with explicit paths."""

import argparse
import ast
from collections import defaultdict
from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def require(condition, message):
    if not condition:
        raise ValueError(message)


def function_namespace(path):
    source = ast.parse(path.read_text())
    functions = [item for item in source.body if isinstance(item, ast.FunctionDef)]
    namespace = {}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec", optimize=0), namespace)
    return namespace


def matrix(value):
    a, b = value % 3, value // 3
    return [[a, -b % 3], [b, a]]


def product(left, right):
    columns = list(zip(*right))
    return [[sum(a * b for a, b in zip(row, column)) % 3 for column in columns]
            for row in left]


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def lift(rows):
    result = []
    for row in rows:
        blocks = [matrix(value) for value in row]
        result.extend([[entry for block in blocks for entry in block[i]] for i in range(2)])
    return result


def field_sum(a, b):
    return (a % 3 + b % 3) % 3 + 3 * ((a // 3 + b // 3) % 3)


def run(command, env, prefix, out):
    result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=180)
    (out / (prefix + "-stdout.txt")).write_text(result.stdout)
    (out / (prefix + "-stderr.txt")).write_text(result.stderr)
    return result


def main(args):
    package = args.package.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    first = function_namespace(package / "independent_dirty.py")
    second = function_namespace(package / "completion.py")
    require(all((x * x + 1) % 3 for x in range(3)), "The quadratic is irreducible over F3")
    for a in range(9):
        for b in range(9):
            total = [[(x + y) % 3 for x, y in zip(r, s)] for r, s in zip(matrix(a), matrix(b))]
            require(matrix(first["add"](a, b)) == matrix(second["add"](a, b)) == total, "Both addition tables")
            require(matrix(first["mul"](a, b)) == matrix(second["product"](a, b)) == product(matrix(a), matrix(b)), "Both multiplication tables")
        if a:
            inverse = first["inv"](a)
            require(inverse == second["inverse_element"](a), "Both inverse tables")
            require(product(matrix(a), matrix(inverse)) == identity(2), "Independent inverse check")

    word = json.loads((package / "dirty-word.json").read_text())
    factors = json.loads((package / "PG29-FACTORS.json").read_text())
    inputs, outputs = defaultdict(list), defaultdict(list)
    for i, (_, edge) in enumerate(word["inputs"][157:], 157):
        inputs[edge].append(i)
    for i, (_, edge) in enumerate(word["outputs"][157:], 157):
        outputs[edge].append(i)
    require(len(inputs) == len(outputs) == 9, "Nine pairs at each boundary")
    require(all(len(v) == 2 for v in list(inputs.values()) + list(outputs.values())), "Each pair has two stubs")
    quotient = [row[:157] + [field_sum(row[a], row[b]) for a, b in inputs.values()]
                for row in word["transfer"]]
    require(quotient[:157] == [row + [0] * 9 for row in identity(157)], "Matched inputs preserve messages")
    require(all(quotient[a] == quotient[b] for a, b in outputs.values()), "Matched outputs agree")
    junk = [quotient[a] for a, b in outputs.values()]
    inverse = lift(factors["inverse_D9"])
    require(product(inverse, lift(factors["D9"])) == identity(18), "Inverse over F3")
    require(product(lift(factors["D9"]), inverse) == identity(18), "Other inverse order over F3")
    normalized = product(inverse, lift(junk))
    correction = lift(factors["correction"])
    restored = [[(entry - error) % 3 for entry, error in zip(row, corr + [0] * 18)]
                for row, corr in zip(normalized, correction)]
    require(restored == [[0] * 314 + row for row in identity(18)], "All 332 F3 columns are restored")
    require(any(row[:314] != [0] * 314 for row in normalized), "Omitting the message correction fails")
    require(lift(factors["D9"]) != identity(18), "Omitting D normalization fails")
    witness = next((i, j, row[j]) for i, row in enumerate(word["transfer"][:157])
                   for j in range(157, 175) if row[j])
    pair = next(pair for pair in inputs.values() if witness[1] in pair)
    require(all(field_sum(row[pair[0]], row[pair[1]]) == 0 for row in word["transfer"][:157]), "The matched partner cancels contamination")

    env = dict(os.environ, PYTHONOPTIMIZE="1")
    result = run([sys.executable, "-O", "-B", str(package / "verify.py")], env, "optimized-environment", out)
    require(result.returncode == 0 and "PASS_PG29_DIRTY_PACKAGE" in result.stdout, "Wrapper works in the optimized environment")
    with tempfile.TemporaryDirectory(prefix="pg29-review-control-") as temp:
        copied = Path(temp) / "package"
        shutil.copytree(package, copied)
        corrupted = json.loads((copied / "PG29-FACTORS.json").read_text())
        corrupted["correction"][0][0] = (corrupted["correction"][0][0] + 1) % 9
        (copied / "PG29-FACTORS.json").write_text(json.dumps(corrupted))
        hashes = json.loads((copied / "SOURCE-HASHES.json").read_text())
        hashes["PG29-FACTORS.json"] = sha256((copied / "PG29-FACTORS.json").read_bytes()).hexdigest()
        (copied / "SOURCE-HASHES.json").write_text(json.dumps(hashes))
        result = run([sys.executable, "-O", "-B", str(copied / "verify.py")], env, "wrong-factor-control", out)
        require(result.returncode != 0 and "factors == independent_factors" in result.stderr,
                "The semantic factor check remains active with PYTHONOPTIMIZE")
        bad_word = json.loads((copied / "dirty-word.json").read_text())
        bad_word["local_words"][0]["matrix"][0] = [0] * 5
        (copied / "dirty-word.json").write_text(json.dumps(bad_word))
        result = run([sys.executable, "-I", "-B", str(copied / "independent_dirty.py")], env, "singular-local-control", out)
        require(result.returncode != 0 and "rank(local['matrix'])==5" in result.stderr, "Singular local map is rejected")

    provenance = None
    if args.primary_dir:
        source = args.primary_dir.resolve()
        pins = {"upstream_verify.py": "3be25d94a25e8ea8b484a1fb614a697e0a24e4519b647febc64b2d314f44d758",
                "182-vertex-code.json": "f47b7f8af378fe7f86c7da32f04533b419711e468997c30ddef30a3a791dba01"}
        for name, digest in pins.items():
            require(sha256((source / name).read_bytes()).hexdigest() == digest, "Primary source pin")
        with tempfile.TemporaryDirectory(prefix="pg29-review-provenance-") as temp:
            temporary = Path(temp)
            for name in ["upstream_verify.py", "182-vertex-code.json", "dirty_completion.py"]:
                shutil.copy2(source / name, temporary / name)
            result = run([sys.executable, "-B", str(temporary / "upstream_verify.py"), str(temporary / "182-vertex-code.json")], {}, "primary-verifier", out)
            require(result.returncode == 0, "Primary verifier passes")
            result = run([sys.executable, "-B", str(temporary / "dirty_completion.py")], {}, "transcript-regeneration", out)
            require(result.returncode == 0, "Historical transcript generator passes")
            require((temporary / "dirty-word.json").read_bytes() == (package / "dirty-word.json").read_bytes(), "Exact transcript regeneration")
        provenance = {"primary_pins": pins, "generator_sha256": sha256((source / "dirty_completion.py").read_bytes()).hexdigest(),
                      "original_verifier_passed": True, "transcript_regenerated_byte_exactly": True,
                      "note": "The geometry generator uses primary-source utilities. This is a provenance replay, not an independent geometry implementation. No primary code is copied into this review output."}
    report = {"status": "PASS_PG29_INDEPENDENT_REVIEW_CHECKS", "field_table_pairs_checked": 81,
              "two_field_implementations_match_F3_matrix_representation": True,
              "matched_GF9_columns": 166, "independent_lifted_F3_columns": 332,
              "unmatched_input_contamination_witness": {"message_output_row": witness[0], "boundary_input_column": witness[1], "GF9_coefficient": witness[2]},
              "missing_correction_fails": True, "missing_normalization_fails": True,
              "wrong_factor_rejected_under_PYTHONOPTIMIZE": True, "singular_local_map_rejected": True,
              "provenance": provenance, "new_kappa": False}
    (out / "REVIEW-CHECKS.json").write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--primary-dir", type=Path)
    main(parser.parse_args())
