#!/usr/bin/env python3
"""Check that only the derivative's input interface changed."""
import ast
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
NAMES = (
    "parity", "rank", "extend_basis", "rows_from_columns", "inverse_rows",
    "linear", "quadratic_phase", "mul_gaussian", "times_i",
    "canonical_source_kernel", "apply_monomial", "factorized_kernel",
    "same_kernel",
)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def functions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {node.name: ast.dump(node, include_attributes=False)
            for node in tree.body if isinstance(node, ast.FunctionDef)}


def main():
    original = functions(HERE / "original/kernel_check.py")
    derivative = functions(HERE / "kernel_check.py")
    result = {}
    for name in NAMES:
        require(name in original and name in derivative, "missing function " + name)
        a, b = original[name], derivative[name]
        require(a == b, "mathematical AST changed: " + name)
        result[name] = hashlib.sha256(a.encode()).hexdigest()
    print(json.dumps({"schema": "source-kernel-derivative-ast/1",
                      "functions_identical": list(NAMES),
                      "function_ast_sha256": result}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
