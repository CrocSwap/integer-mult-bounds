"""Verify the source-bound native join with exact Gaussian arithmetic."""

import argparse
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N = 512


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate(data, expected):
    require(hashlib.sha256(data).hexdigest() == expected, "source mismatch")


def equal(a, b):
    exponent = max(a[2], b[2])
    return all(np.array_equal(x * (1 << (exponent - a[2])), y * (1 << (exponent - b[2])))
               for x, y in zip(a[:2], b[:2]))


def add(a, b, numerator, exponent=1):
    scale = max(a[2], b[2] + exponent)
    return tuple(a[i] * (1 << (scale - a[2])) + numerator * b[i] * (1 << (scale - b[2] - exponent))
                 for i in range(2)) + (scale,)


def unit(real, imag, phase):
    return [(real, imag), (-imag, real), (-real, -imag), (imag, -real)][phase % 4]


def monomial(z, record, inverse=False):
    real, imag, exponent = z
    out_real, out_imag = np.empty_like(real), np.empty_like(imag)
    seen = set()
    for x in range(N):
        bits = [i for i in range(9) if x & (1 << i)]
        y = record["offset"] ^ sum(((row & x).bit_count() % 2) << i
                                   for i, row in enumerate(record["matrix_rows"]))
        phase = record["phase"] + sum(record["linear_Z4"][i] for i in bits)
        phase += 2 * sum((record["quadratic_rows"][i] >> j) & 1 for i in bits for j in bits if i < j)
        require(y not in seen and 0 <= y < N, "recipe is not a permutation")
        seen.add(y)
        src, dst, sign = (y, x, -1) if inverse else (x, y, 1)
        out_real[dst], out_imag[dst] = unit(real[src], imag[src], sign * phase)
    return out_real, out_imag, exponent


def coordinate(z, rank, inverse=False):
    real, imag, exponent = z
    real, imag = real.copy(), imag.copy()
    sign = -1 if inverse else 1
    # The two coefficients are (1 + sign*i)/2 and (1 - sign*i)/2.
    for axis in range(rank):
        low = np.array([x for x in range(N) if not x & (1 << axis)])
        high = low ^ (1 << axis)
        ar, ai, br, bi = real[low].copy(), imag[low].copy(), real[high].copy(), imag[high].copy()
        real[low], imag[low] = ar - sign * ai + br + sign * bi, sign * ar + ai - sign * br + bi
        real[high], imag[high] = ar + sign * ai + br - sign * bi, -sign * ar + ai + sign * br + bi
        exponent += 1
    return real, imag, exponent


def recipe(z, record, inverse=False):
    first, last = (record["left"], record["right"]) if inverse else (record["right"], record["left"])
    if first is not None:
        z = monomial(z, first, inverse)
    z = coordinate(z, record["rank"], inverse)
    if last is not None:
        z = monomial(z, last, inverse)
    return z


def join(source, target, native, mutant=None, inverse=False):
    warp, child = native["warp"], native["child"]
    if inverse:
        target = add(target, source, 1)
        return recipe(source, warp, True), recipe(target, child, True)
    if mutant != "omit_warp":
        source = recipe(source, warp)
    if mutant == "add_before_child":
        target = add(target, source, -1)
    if mutant != "omit_child":
        target = recipe(target, child, mutant == "reverse_child")
    if mutant != "add_before_child":
        target = add(target, source, 1 if mutant == "wrong_add_sign" else -1)
    return source, target


def concatenate(a, b):
    exponent = max(a[2], b[2])
    return tuple(np.concatenate((a[i] * (1 << (exponent - a[2])), b[i] * (1 << (exponent - b[2]))), axis=1)
                 for i in range(2)) + (exponent,)


def combine(z, real, imag):
    return z[0] @ real - z[1] @ imag, z[0] @ imag + z[1] @ real, z[2]


def run():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    source_controls = 0
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        data = (ROOT / item["path"]).read_bytes()
        authenticate(data, item["sha256"])
        try:
            authenticate(data + b"changed", item["sha256"])
        except ValueError:
            source_controls += 1
        else:
            raise ValueError("source mutation accepted")
    with tempfile.TemporaryDirectory(prefix="native-boundary-join-") as folder:
        directory = Path(folder)
        # The source guard is preserved. Only the new checker runs in both modes.
        subprocess.run([sys.executable, "-I", "-B", str(HERE / "produce.py"), folder],
                       check=True, capture_output=True, text=True, timeout=180)
        native = json.loads((directory / "native.json").read_text())
        require(native["predecessor_assertions_enabled"], "source assertions disabled")
        with np.load(directory / "oracle.npz", allow_pickle=False) as archive:
            def read(name):
                return (archive[name + "_real"].astype(object), archive[name + "_imag"].astype(object),
                        int(archive[name + "_exp"]))
            initial_source, final_source, final_target = [read(n) for n in ("initial_source", "final_source", "final_target")]
    zero = (np.zeros((N, N), dtype=object), np.zeros((N, N), dtype=object), 0)
    identity = (np.eye(N, dtype=object), np.zeros((N, N), dtype=object), 0)
    initial = concatenate(initial_source, zero), concatenate(zero, identity)
    expected = concatenate(final_source, zero), concatenate(add(zero, final_source, -1), final_target)
    actual = join(*initial, native)
    require(all(equal(a, b) for a, b in zip(actual, expected)), "all-column endpoint failed")
    restored = join(*actual, native, inverse=True)
    require(all(equal(a, b) for a, b in zip(restored, initial)), "all-column inverse failed")
    controls = []
    for mutant in ("omit_warp", "omit_child", "reverse_child", "add_before_child", "wrong_add_sign"):
        changed = join(*initial, native, mutant=mutant)
        require(not all(equal(a, b) for a, b in zip(changed, expected)), "accepted " + mutant)
        controls.append(mutant)
    for location in ("warp.left", "child.left", "child.right"):
        changed_native = copy.deepcopy(native)
        outer, inner = location.split(".")
        changed_native[outer][inner]["phase"] = (changed_native[outer][inner]["phase"] + 1) % 4
        changed = join(*initial, changed_native)
        require(not all(equal(a, b) for a, b in zip(changed, expected)), "absolute phase ignored")
        controls.append("constant_phase_" + location)

    # Nonzero complex dirty data include integers wider than machine words.
    dirty_count = 4
    real = np.array([[(x * (j + 3) % 31 - 15) * (1 << (67 + 13 * j)) + x
                     for j in range(dirty_count)] for x in range(2 * N)], dtype=object)
    imag = np.array([[(x * (j + 7) % 29 - 14) * (1 << (71 + 11 * j)) - j
                     for j in range(dirty_count)] for x in range(2 * N)], dtype=object)
    dirty_initial = [combine(z, real, imag) for z in initial]
    dirty_expected = [combine(z, real, imag) for z in expected]
    dirty_actual = join(*dirty_initial, native)
    require(all(equal(a, b) for a, b in zip(dirty_actual, dirty_expected)), "dirty endpoint failed")
    require(all(equal(a, b) for a, b in zip(join(*dirty_actual, native, inverse=True), dirty_initial)),
            "dirty inverse failed")
    return {
        "schema_version": 1, "status": "PASS_EMITTED_NATIVE_BOUNDARY_JOIN",
        "base_commit": manifest["base_commit"], "native": native,
        "all_columns": 1024, "dirty_complex_pairs": dirty_count,
        "endpoint_and_literal_inverse": True, "mutation_controls": controls,
        "source_mutation_controls": source_controls,
        "forward_bill": {"serialized_monomials": 3, "rank_one_child": 1,
                         "complex_scaled_add": 1, "real_scaled_adds": 1024, "C0_butterflies": 256},
        "all_width_statement": "local tensor identity only; scalar -1/2 stays fixed",
        "selected_frontier_changed": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    if args.output is None:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "receipt mismatch")
    else:
        with args.output.open("x") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    print("PASS_EMITTED_NATIVE_BOUNDARY_JOIN 1024 columns; 4 wide dirty pairs; 8 boundary mutations")


if __name__ == "__main__":
    main()
