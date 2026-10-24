#!/usr/bin/env python3
"""Exact full-matrix audit of the 423 declared PR4470 physical lowerings.

Apache-2.0. Prepared for Chris / Clear1nsight with substantial OpenAI assistance.
No predecessor evaluator or compiler is imported. NumPy stores integer matrices;
there is no floating-point arithmetic in the scientific comparison.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import platform
import random
import sys
import time
import numpy as np

HERE = Path(__file__).resolve().parent
SOURCE_HEAD = "b9a13c1673e0e9697de410de16e8bbf3207a7363"
PINS = {
    "CANONICAL.json.gz": "4a8c4ed26e53a72362d571c972e65aff546be784",
    "PR4447-PATCH.json": "f96d295d40014d4dd503f58eb3cdabcbb4b8e101",
    "PR4470-PATCH.json": "51304a6601061ed4e698f910b09135ef109555e3",
    "PR4470-NATIVE.json.gz": "0910f74138decf498e7fc445cc2daff4390169d6",
}

def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def read_source(name: str) -> object:
    raw = (HERE / "vendor" / name).read_bytes()
    require(blob_id(raw) == PINS[name], "Source binding failed: " + name)
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)


def space(basis: list[int], n: int) -> frozenset[int]:
    values = {0}
    for vector in basis:
        require(type(vector) is int and 0 < vector < 1 << n, "Invalid basis vector")
        require(vector not in values, "Dependent basis")
        values.update(tuple(x ^ vector for x in values))
    return frozenset(values)


def transpose(rows: list[int], n: int) -> list[int]:
    return [sum(((rows[j] >> i) & 1) << j for j in range(n)) for i in range(n)]


def linear_map(rows: list[int], n: int) -> np.ndarray:
    require(len(rows) == n and all(type(r) is int and 0 <= r < 1 << n for r in rows),
            "Invalid binary matrix")
    result = np.array([sum(((r & x).bit_count() % 2) << i for i, r in enumerate(rows))
                       for x in range(1 << n)], dtype=np.int64)
    require(len(set(map(int, result))) == 1 << n, "Singular binary matrix")
    return result


def inverse_rows(rows: list[int], n: int) -> list[int]:
    # Invert the finite bijection, independently of binary elimination.
    p = list(map(int, linear_map(rows, n)))
    inverse = [0] * len(p)
    for x, y in enumerate(p):
        inverse[y] = x
    return transpose([inverse[1 << i] for i in range(n)], n)


def extend(basis: list[int], n: int) -> list[int]:
    out = list(basis)
    values = set(space(out, n))
    for i in range(n):
        vector = 1 << i
        if vector not in values:
            values.update(tuple(x ^ vector for x in values))
            out.append(vector)
    require(len(out) == n, "Incomplete basis")
    return out


def adjoint(circuit: list[tuple], n: int) -> list[tuple]:
    result = []
    for gate in reversed(circuit):
        kind = gate[0]
        if kind == "P":
            result.append(("P", inverse_rows(gate[1], n)))
        elif kind == "D":
            result.append(("D", gate[1], [(-a) % 4 for a in gate[2]]))
        elif kind == "C":
            result.append(("C", gate[1], -gate[2]))
        elif kind == "phase":
            result.append(("phase", (-gate[1]) % 4))
        elif kind == "X":
            result.append(gate)
        else:
            raise ValueError("Unknown primitive")
    return result


def frame(basis: list[int], n: int) -> list[tuple]:
    # Source-specified reference frame, not an imported lowering algorithm.
    rank = len(basis)
    space(basis, n)
    core = [("C", 1 << i, 1) for i in range(rank)]
    if rank in (0, n):
        return core
    rows = transpose(extend(basis, n), n)
    inverse_columns = transpose(inverse_rows(rows, n), n)
    quadratic = [(1 << i) ^ sum(((x & y).bit_count() % 2) << j
                 for j, y in enumerate(inverse_columns))
                 for i, x in enumerate(inverse_columns)]
    alpha = [(quadratic[i] >> i) & 1 for i in range(n)]
    wrapper = [("P", rows), ("D", quadratic, alpha)]
    return adjoint(wrapper, n) + core + wrapper


def monomial(record: dict, n: int) -> list[tuple]:
    required = {"matrix_rows", "offset", "quadratic_rows", "linear_Z4", "phase"}
    require(set(record) == required, "Unsupported monomial schema")
    rows = list(record["matrix_rows"])
    linear_map(rows, n)
    q = list(record["quadratic_rows"])
    a = list(record["linear_Z4"])
    require(len(q) == len(a) == n and transpose(q, n) == q, "Invalid quadratic form")
    require(all(type(x) is int and 0 <= x < 1 << n for x in q), "Invalid quadratic row")
    require(all(type(x) is int and 0 <= x < 4 for x in a), "Invalid linear phase")
    require(all((a[i] % 2) == ((q[i] >> i) & 1) for i in range(n)), "Phase parity")
    require(type(record["offset"]) is int and 0 <= record["offset"] < 1 << n,
            "Invalid offset")
    require(type(record["phase"]) is int and 0 <= record["phase"] < 4, "Invalid phase")
    return [("D", q, a), ("P", rows), ("X", record["offset"]), ("phase", record["phase"])]


def recipe(record: dict, n: int) -> list[tuple]:
    require(set(record) == {"rank", "left", "right"}, "Unsupported recipe schema")
    rank = record["rank"]
    require(type(rank) is int and 0 <= rank <= n, "Invalid child rank")
    if rank == 0:
        require(record["right"] is None, "Unexpected rank-zero right factor")
        return monomial(record["left"], n)
    return (monomial(record["right"], n) + [("C", 1 << i, 1) for i in range(rank)]
            + monomial(record["left"], n))


def matrix(circuit: list[tuple], n: int) -> tuple[np.ndarray, np.ndarray, int]:
    """Return Gaussian integer numerators and a common denominator 2**d."""
    require(1 <= n <= 9, "Audit dimension out of range")
    # Each C doubles the denominator; unitary prefixes bound each numerator by 2**d.
    # The stricter 28 bound also keeps squared magnitudes and cross-scaled equality safe.
    require(sum(e[0] == "C" for e in circuit) <= 28, "Integer safety cap exceeded")
    size = 1 << n
    real = np.eye(size, dtype=np.int64)
    imag = np.zeros((size, size), dtype=np.int64)
    denominator = 0
    for gate in circuit:
        kind = gate[0]
        if kind in ("P", "X"):
            p = linear_map(gate[1], n) if kind == "P" else np.arange(size) ^ gate[1]
            require(len(set(map(int, p))) == size, "Invalid address permutation")
            rr = np.empty_like(real); ii = np.empty_like(imag)
            rr[p, :] = real; ii[p, :] = imag
            real, imag = rr, ii
        elif kind in ("D", "phase"):
            if kind == "phase":
                phases = np.full(size, gate[1] % 4, dtype=np.int64)
            else:
                q, a = gate[1:]
                phases = np.array([(sum(a[i] for i in range(n) if x >> i & 1)
                    + 2 * sum(((q[i] & x) >> (i + 1)).bit_count()
                              for i in range(n) if x >> i & 1)) % 4
                    for x in range(size)], dtype=np.int64)
            cos = np.array([1, 0, -1, 0], dtype=np.int64)[phases, None]
            sin = np.array([0, 1, 0, -1], dtype=np.int64)[phases, None]
            real, imag = cos * real - sin * imag, sin * real + cos * imag
        elif kind == "C":
            q, sign = gate[1:]
            require(0 < q < size and sign in (-1, 1), "Invalid Gaussian gate")
            shifted_r = real[np.arange(size) ^ q, :]
            shifted_i = imag[np.arange(size) ^ q, :]
            real, imag = (real - sign * imag + shifted_r + sign * shifted_i,
                          imag + sign * real + shifted_i - sign * shifted_r)
            denominator += 1
        else:
            raise ValueError("Unknown primitive " + str(kind))
    return real, imag, denominator


def equal(a: tuple, b: tuple) -> bool:
    d = max(a[2], b[2])
    require(d <= 28, "Comparison safety cap")
    return all(np.array_equal(a[i] * (1 << (d-a[2])), b[i] * (1 << (d-b[2])))
               for i in (0, 1))


def check_rank(value: tuple, rank: int) -> None:
    real, imag, d = value
    require(0 <= rank <= 9 and 2*d >= rank, "Invalid magnitude exponent")
    occupied = (real != 0) | (imag != 0)
    require(bool(np.all(np.count_nonzero(occupied, axis=0) == 1 << rank)), "Column support rank")
    require(bool(np.all(np.count_nonzero(occupied, axis=1) == 1 << rank)), "Row support rank")
    square = real*real + imag*imag
    require(bool(np.all(square[occupied] == 1 << (2*d-rank))), "Exact entry magnitude")


def self_tests() -> dict:
    checks = 0
    rng = random.Random(4470)
    for n in range(1, 5):
        identity = matrix([], n)
        for trial in range(12):
            basis = []
            for x in rng.sample(range(1, 1 << n), (1 << n)-1):
                if x not in space(basis, n):
                    basis.append(x)
                if len(basis) == n:
                    break
            for rank in range(n+1):
                circuit = frame(basis[:rank], n)
                require(equal(matrix(circuit + adjoint(circuit, n), n), identity), "Frame inverse control")
                checks += 1
        for q in range(1, 1 << n):
            # Independent entry-law oracle for a single Gaussian gate.
            r, i, d = matrix([("C", q, 1)], n)
            e = np.eye(1 << n, dtype=np.int64)
            x = e[np.arange(1 << n) ^ q]
            require(d == 1 and np.array_equal(r, e+x) and np.array_equal(i, e-x), "Gaussian entry law")
            checks += 1
    # An absolute phase must fail even though support and all magnitudes survive.
    good = matrix([("C", 1, 1)], 2)
    shifted = matrix([("C", 1, 1), ("phase", 1)], 2)
    check_rank(good, 1); check_rank(shifted, 1)
    require(not equal(good, shifted), "Absolute-phase mutation escaped")
    require(not equal(good, matrix([("C", 1, -1)], 2)), "Conjugation mutation escaped")
    rejected = 0
    for test in (lambda: check_rank(good, 2), lambda: linear_map([1, 1], 2),
                 lambda: space([1, 1], 2), lambda: matrix([("C", 1, 1)]*29, 2)):
        try:
            test()
        except ValueError:
            rejected += 1
    require(rejected == 4, "Structural mutation escaped")
    require(blob_id(b"source") != blob_id(b"sourcf"), "Source-byte control")
    # Explicit two-column tensor identity with summed, not unscaled, phase.
    r, i, d = matrix([("C", 1, 1), ("phase", 1)], 1)
    rr = np.kron(r, r) - np.kron(i, i)
    ii = np.kron(r, i) + np.kron(i, r)
    require(equal((rr, ii, 2*d), matrix([("C", 1, 1), ("C", 2, 1), ("phase", 2)], 2)),
            "Tensor phase lift")
    return {"positive_checks": checks+2, "rejected_controls": 7, "tensor_phase_test": True}


def catalogue() -> tuple[list[list[int]], dict]:
    base = read_source("CANONICAL.json.gz")
    predecessor = read_source("PR4447-PATCH.json")
    patch = read_source("PR4470-PATCH.json")
    require(patch["source_head"] == "322e0ec764aa7ef7801383feb1f656e460dd8bed", "Patch predecessor")
    frames = deepcopy(base["frames"])
    require(len(frames) == 1159, "Base frame census")
    require(space(frames[predecessor["old_frame"]], 9) == space(predecessor["old_basis"], 9),
            "Predecessor contact binding")
    frames.append(predecessor["new_basis"])
    labels = {space(b, 9): index for index, b in enumerate(frames)}
    changed = Counter()
    keys = set()
    for move in patch["changes"]:
        key = (move["phase"], move["ordinal"])
        require(key not in keys, "Repeated changed contact")
        keys.add(key); changed[move["phase"]] += 1
        old = space(move["old"], 9); new = space(move["new"], 9)
        require(old != new, "Unchanged patch entry")
        if new not in labels:
            labels[new] = len(frames)
            frames.append(move["new"])
    require(dict(changed) == {"entrance": 38, "exit": 47, "A": 21, "B": 238, "cleanup_tail": 155},
            "Changed-frame census")
    return frames, dict(sorted(changed.items()))


def audit() -> dict:
    controls = self_tests()
    frames, changes = catalogue()
    receipt = read_source("PR4470-NATIVE.json.gz")
    records = receipt["new_physical_edges_and_boundaries"]
    require(len(records) == 423, "Physical pair census")
    seen = set(); histogram = Counter(); digest = hashlib.sha256()
    largest_c = 0
    for index, record in enumerate(records):
        a, b, rank = record["old"], record["new"], record["rank"]
        require((a, b) not in seen, "Repeated physical pair")
        seen.add((a, b))
        require(0 <= a < len(frames) and 0 <= b < len(frames), "Unknown frame")
        require(space(frames[a], 9) < space(frames[b], 9), "Nonnested physical pair")
        require(rank == len(frames[b])-len(frames[a]), "Declared dimension gap")
        circuit = adjoint(frame(frames[a], 9), 9) + frame(frames[b], 9)
        largest_c = max(largest_c, sum(e[0] == "C" for e in circuit))
        wanted = matrix(circuit, 9)
        for direction in ("forward", "backward"):
            lowered = record["recipes"][direction]
            require(lowered["rank"] == rank, "Lowered rank disagrees")
            actual = matrix(recipe(lowered, 9), 9)
            expected = wanted if direction == "forward" else (wanted[0], -wanted[1], wanted[2])
            require(equal(actual, expected), f"Exact matrix mismatch at pair {a},{b}, {direction}")
            check_rank(actual, rank)
            digest.update(json.dumps([a, b, rank, direction], separators=(",", ":")).encode())
            histogram[rank] += 1
        if index == 0:
            bad = deepcopy(record["recipes"]["forward"])
            bad["left"]["phase"] = (bad["left"]["phase"] + 1) % 4
            mutated = matrix(recipe(bad, 9), 9)
            check_rank(mutated, rank)
            require(not equal(mutated, wanted), "Real-source absolute-phase control escaped")
        if (index+1) % 50 == 0:
            print(f"CHECKED_PHYSICAL_PAIRS {index+1}/423", flush=True)
    return {"schema": "pr4470-exact-transport-audit/v1", "status": "PASS_EXACT_TRANSPORT_MATRICES",
            "source_head": SOURCE_HEAD, "physical_pairs": len(seen), "orientations": 2,
            "source_files": {name: {"git_blob": pin, "sha256": hashlib.sha256((HERE / "vendor" / name).read_bytes()).hexdigest()} for name, pin in sorted(PINS.items())},
            "matrix_dimension": 512, "basis_columns_compared": 423*2*512,
            "complex_matrix_entries_compared": 423*2*512*512,
            "rank_histogram_both_orientations": dict(sorted(histogram.items())),
            "frame_catalogue_count": len(frames), "patch_changes": changes,
            "maximum_target_gaussian_gates": largest_c, "self_tests": controls,
            "actual_source_phase_mutation_rejected": True,
            "coverage_index_sha256": digest.hexdigest(), "new_kappa": False,
            "not_covered": ["completeness of the declared 423-pair list", "chronological native endpoint replay",
                "p16 controller", "physical tape costs", "precision and storage", "outer theorem"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    started = time.monotonic()
    result = self_tests() if args.self_test else audit()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        require(not args.out.exists(), "Refusing to overwrite an existing receipt")
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    print(json.dumps({"python": platform.python_version(), "numpy": np.__version__,
                      "elapsed_seconds": round(time.monotonic()-started, 3)}, sort_keys=True))

if __name__ == "__main__":
    main()
