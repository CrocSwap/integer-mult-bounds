#!/usr/bin/env python3
"""Replay finite source-bound witnesses for PROOF.md (not its all-size proof)."""

from __future__ import annotations

import hashlib
import argparse
import json
from fractions import Fraction
from pathlib import Path
import sys
from types import ModuleType


ROOT = Path(__file__).resolve().parent
KERNEL_PATH = ROOT / "kernel.py"
RESULT_PATH = ROOT / "RESULT.json"
EXPECTED_GIT_BLOB = "b00bbbc7655121232a46101962c48e71cee98a39"
EXPECTED_SHA256 = "fc3e2bf828fa547bee5710f9d5502b7c8c4dcb4cab7536ff73e3dbff54960f1b"


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise RuntimeError(explanation)


def git_blob_id(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(prefix + data).hexdigest()


def load_kernel() -> tuple[ModuleType, bytes]:
    data = KERNEL_PATH.read_bytes()
    require(hashlib.sha256(data).hexdigest() == EXPECTED_SHA256,
            "kernel.py SHA-256 differs from the pinned #6509 source")
    require(git_blob_id(data) == EXPECTED_GIT_BLOB,
            "kernel.py Git blob differs from the pinned #6509 source")
    module = ModuleType("retained_6509_kernel")
    exec(compile(data, str(KERNEL_PATH), "exec"), module.__dict__)
    return module, data


def add(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return a[0] + b[0], a[1] + b[1]


def sub(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return a[0] - b[0], a[1] - b[1]


def ideal_pair(pair: tuple[tuple[int, int], tuple[int, int]], sigma: int):
    x, y = pair
    s = add(x, y)
    d = sub(x, y)
    rotated = (-sigma * d[1], sigma * d[0])
    numerators = (add(s, rotated), sub(s, rotated))
    require(all((coordinate % 2) == 0 for out in numerators for coordinate in out),
            "the ideal image used in an integer identity was not integral")
    return tuple((out[0] // 2, out[1] // 2) for out in numerators)


def expected_ray_input(t: int):
    return ((1 - t, -t), (t, t))


def expected_ray_output(t: int):
    return ((1 + t, -t), (-t, t))


def width_for(t: int) -> int:
    # The #6509 proof bounds every pair intermediate by 4M+1; here M<=2t.
    return max(3, (8 * t + 2).bit_length() + 1)


def source_mutation_control(source: bytes) -> None:
    text = source.decode("utf-8")
    needle = "return (1 if real > 0 else -1), 0"
    require(text.count(needle) == 1, "could not locate the pinned odd-center branch")
    mutant_text = text.replace(needle, "return 0, 0", 1)
    mutant = ModuleType("illegal_center_mutant")
    exec(compile(mutant_text, "<mutated #6509 kernel>", "exec"), mutant.__dict__)
    try:
        mutant.pair((1, 0), (0, 0), width=8, sign=1)
    except ValueError as error:
        require("Exact pair halves" in str(error),
                "illegal-center mutant failed for an unexpected reason")
    else:
        raise RuntimeError("illegal odd-sum center was accepted by the source mutant")


def global_period_control(kernel: ModuleType) -> None:
    # The translation (-1,-1) is fixed by C_sigma, but the sign-based source
    # center changes from c(1)=1 to c(-1)=-1.
    start = ((1, 0), (0, 0))
    shift = ((-1, 0), (-1, 0))
    translated = ((0, 0), (-1, 0))
    require(kernel.center(1, 0) == (1, 0), "unexpected source center at sum 1")
    require(kernel.center(-1, 0) == (-1, 0), "unexpected source center at sum -1")
    out0 = kernel.pair(start[0], start[1], width=8, sign=1)
    out1 = kernel.pair(translated[0], translated[1], width=8, sign=1)
    difference = (sub(out1[0], out0[0]), sub(out1[1], out0[1]))
    require(difference != shift,
            "a sign-dependent center unexpectedly obeyed this global period candidate")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true",
                        help="write the verified receipt to RESULT.json")
    args = parser.parse_args()
    kernel, source = load_kernel()

    # The factor 2 in lambda=2 C_sigma^* e is essential: C_sigma^* e
    # itself has half-integral coordinates for the c=1 witness.
    half_adjoint_error = (
        (Fraction(-1, 2), Fraction(-1, 2)),
        (Fraction(1, 2), Fraction(1, 2)),
    )
    require(any(value.denominator != 1 for row in half_adjoint_error for value in row),
            "the one-step adjoint error should not be a lattice vector")
    integral_lambda = tuple(tuple(2 * value for value in row) for row in half_adjoint_error)
    require(integral_lambda == ((-1, -1), (1, 1)),
            "doubled adjoint error does not match the predicted integral ray")
    twice_error = ((1, -1), (-1, 1))
    require(ideal_pair(integral_lambda, 1) == twice_error,
            "C_sigma lambda != 2e on the retained c=1 ray")

    t_values = set(range(9))
    t_values.update(1 << exponent for exponent in (16, 32, 64, 128, 256))
    t_values.update(1 << (p - 1) for p in range(1, 65))
    ordered_t_values = sorted(t_values)
    for t in ordered_t_values:
        width = width_for(t)
        incoming = expected_ray_input(t)
        expected = expected_ray_output(t)
        output = kernel.pair(incoming[0], incoming[1], width=width, sign=1)
        require(output == expected, f"forward exact ray mismatch at t={t}")
        returned = kernel.pair(output[0], output[1], width=width, sign=-1)
        require(returned == incoming, f"literal inverse mismatch at t={t}")

    dyadic_cases = []
    for p in range(1, 65):
        t = 1 << (p - 1)
        h = Fraction(1, 1 << p)
        input_norm2 = h * h * (4 * t * t - 2 * t + 1)
        output_norm2 = h * h * (4 * t * t + 2 * t + 1)
        require(input_norm2 == 1 - h + h * h,
                f"dyadic input norm identity failed at p={p}")
        require(output_norm2 == 1 + h + h * h,
                f"dyadic output norm identity failed at p={p}")
        require(input_norm2 < 1 and output_norm2 > 1,
                f"dyadic unit-ball crossing failed at p={p}")
        dyadic_cases.append({
            "p": p,
            "input_norm_squared": str(input_norm2),
            "output_norm_squared": str(output_norm2),
        })

    source_mutation_control(source)
    global_period_control(kernel)

    result = {
        "status": "PASS",
        "scope": "finite exact execution of #6509 source ray and negative controls; all-size proof is PROOF.md",
        "kernel_git_blob": EXPECTED_GIT_BLOB,
        "kernel_sha256": EXPECTED_SHA256,
        "ray_case_count": len(ordered_t_values),
        "ray_t_values": [str(t) for t in ordered_t_values],
        "max_ray_t_bits": max(ordered_t_values).bit_length(),
        "dyadic_p_range": [1, 64],
        "dyadic_case_count": len(dyadic_cases),
        "dyadic_endpoint_examples": [dyadic_cases[0], dyadic_cases[-1]],
        "controls": {
            "illegal_center_mutation_rejected": True,
            "one_step_adjoint_error_not_integral": True,
            "candidate_global_equal_coordinate_period_rejected": True,
        },
        "dependencies": "Python standard library only",
        "python_version": sys.version.split()[0],
    }
    if args.write_result:
        RESULT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                               encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
