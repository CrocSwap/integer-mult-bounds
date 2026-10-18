#!/usr/bin/env python3
"""Independent closed-form checks for general odd-kernel query pairs. Apache-2.0."""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHECKS = 0


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def load():
    spec = importlib.util.spec_from_file_location("okqp", ROOT / "program.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def push(k):
    s = (1, 0, 1, -1, 0, -1)
    r = (1, 0, -1, -1, 0, 1)
    c = Fraction(k, 4)
    return tuple(
        tuple((Fraction(1) if i == j else Fraction(0)) + c * s[i] * r[j] for j in range(6))
        for i in range(6)
    )


def mm(A, B):
    return tuple(
        tuple(sum(A[i][k] * B[k][j] for k in range(6)) for j in range(6))
        for i in range(6)
    )


def run_word(basis, word):
    state = list(map(Fraction, basis))
    for event in word:
        if event[0] == "child":
            _, first, last = event
            state[first], state[last] = state[last], state[first]
        else:
            _, target, diagonal, controls = event
            state[target] = diagonal * state[target] + sum(c * state[i] for i, c in controls)
    return tuple(state)


def main():
    prog = load()
    cert = json.loads((ROOT / "CERTIFICATE.json").read_text())
    need(cert["no_new_kappa"] is True, "no new kappa")
    need(cert["typed_cost_improvement_over_dyadic"] is False, "no typed gain")

    I = tuple(tuple(Fraction(i == j) for j in range(6)) for i in range(6))
    kernels = (1, 3, 5, 7, 9, 15)
    columns = 0
    for kernel in kernels:
        row = cert["per_kernel"][str(kernel)]
        need(row["fused_invoice"]["ordinary_children"] == 3, "children")
        need(row["baseline_invoice"]["ordinary_children"] == 4, "baseline children")
        need(row["fused_invoice"]["aligned_xor_scans"] == 2, "xor")
        need(row["baseline_invoice"]["aligned_xor_scans"] == 4, "baseline xor")
        a = kernel
        need(mm(mm(push(-a), push(2 * a)), push(-a)) == I, "product identity")
        for k in (kernel, -kernel, 2 * kernel, -4 * kernel, 8 * kernel):
            word = prog.address_word(k)
            for col in range(6):
                basis = tuple(1 if i == col else 0 for i in range(6))
                need(run_word(basis, word) == tuple(push(k)[i][col] for i in range(6)), "col")
                columns += 1
            # Pattern: odd m coprime to kernel.
            for m in (5, 7, 9, 15, 21, 25, 35):
                expect = m % 2 == 1 and gcd(m, kernel) == 1
                need(prog.modulus_admits(k, m) is expect, f"pattern k={k} m={m}")
                need(prog.modulus_admits_kernel(kernel, m) is expect, f"closed m={m}")

    print(
        "PASS_INDEPENDENT_ODD_KERNEL_QUERY_PAIR "
        f"kernels={list(kernels)} columns_checked={columns} "
        f"controls={CHECKS} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
