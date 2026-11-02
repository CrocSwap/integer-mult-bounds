#!/usr/bin/env python3
"""Finite conformance and a generated source-bound receipt. Nick Petalas."""

import hashlib
import json
from pathlib import Path
from types import ModuleType


HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_fast():
    path = HERE / "fast.py"
    module = ModuleType("p112_fast")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def small_subspaces(fast, source):
    spaces = {frozenset({0})}
    for _ in range(4):
        expanded = set(spaces)
        for space in spaces:
            for vector in range(16):
                expanded.add(space | frozenset(x ^ vector for x in space))
        spaces = expanded
        need(len(spaces) <= 67, "four-dimensional subspace capacity")
    need(len(spaces) == 67, "complete four-dimensional subspace census")
    checks = 0
    for space in spaces:
        basis = source.basis(sorted(space))
        for mask in range(16):
            count = sum(not vector & mask for vector in space)
            dimension = fast.kernel_dimension(basis, mask)
            need(1 << dimension == count, "restriction kernel versus literal vector set")
            checks += 1
    return checks


def wide_cases(fast):
    checks = 0
    for dimension in range(10):
        basis = [((1 << i) | (1 << (i + 50))) for i in range(dimension)]
        for pattern in range(32):
            mask = sum(((pattern >> (i % 5)) & 1) << i for i in range(112))
            count = 0
            for coefficients in range(1 << dimension):
                value = 0
                for i in range(dimension):
                    if coefficients >> i & 1:
                        value ^= basis[i]
                count += not value & mask
            need(1 << fast.kernel_dimension(basis, mask) == count, "112-bit kernel fixture")
            checks += 1
    return checks


def scientific_replay(fast, source):
    counts = {"queries": 0, "masked_basis_rows": 0}
    original = fast.kernel_dimension

    def counted(basis, mask):
        counts["queries"] += 1
        counts["masked_basis_rows"] += len(basis)
        return original(basis, mask)

    fast.kernel_dimension = counted
    try:
        result = fast.run(source)
    finally:
        fast.kernel_dimension = original
    expected = json.loads((fast.SOURCE.parent / "CERTIFICATE.json").read_text())
    need(source.canonical(result) == source.canonical(expected), "complete scientific receipt")
    need(counts == {"queries": 97920, "masked_basis_rows": 816510}, "full kernel work count")
    baseline_rows = 32385 * (256 + 256 + 512) + 765 * 512
    need(baseline_rows == 33553920, "literal predecessor mask count")
    return result, {**counts, "predecessor_masked_vectors": baseline_rows}


def controls(fast):
    need(fast.kernel_dimension([], (1 << 112) - 1) == 0, "zero space")
    need(fast.kernel_dimension([1, 2, 4], 0) == 3, "zero restriction")
    need(fast.kernel_dimension([1, 2, 4], 7) == 0, "injective restriction")
    need(fast.kernel_dimension([3, 5], 1) == 1, "restriction-dependent basis images")
    need(fast.kernel_dimension([1 << 111], 1 << 111) == 0, "highest permitted bit")
    return 5


def main():
    fast = load_fast()
    source = fast.load_source()
    small = small_subspaces(fast, source)
    wide = wide_cases(fast)
    control_count = controls(fast)
    result, work = scientific_replay(fast, source)
    names = ["README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "fast.py", "verify.py", "benchmark.py"]
    hashes = {name: hashlib.sha256((HERE / name).read_bytes()).hexdigest() for name in names}
    receipt = {"status": "PASS_P112_COMPATIBILITY_KERNELS", "small_cases": small,
               "wide_cases": wide, "controls": control_count, "work": work,
               "scientific_sha256": source.digest(result), "package_sha256": hashes}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
