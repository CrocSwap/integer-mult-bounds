#!/usr/bin/env python3
"""Independent column-image and tariff check; imports no primary verifier code."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def push(k, z):
    s = (1, 0, 1, -1, 0, -1)
    r = (1, 0, -1, -1, 0, 1)
    c = Fraction(k, 4)
    dot = sum(Fraction(r[i]) * Fraction(z[i]) for i in range(6))
    return tuple(Fraction(z[i]) + c * Fraction(s[i]) * dot for i in range(6))


def word(k):
    a = Fraction(k, 4)
    return (
        ("affine", 2, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 5, a, ((0, 1 + a), (2, -a), (3, -a))),
        ("child", 0, 5),
        ("affine", 2, Fraction(1), ((0, Fraction(1)),)),
        ("affine", 3, Fraction(1), ((0, Fraction(-1)),)),
        ("affine", 5, -1 / a, ((0, 1 / a - 1), (2, Fraction(1)), (3, Fraction(1)))),
    )


def run(addr, events):
    state = list(map(Fraction, addr))
    for event in events:
        if event[0] == "child":
            i, j = event[1], event[2]
            state[i], state[j] = state[j], state[i]
        else:
            _, t, d, ctr = event
            state[t] = Fraction(d) * state[t] + sum(Fraction(c) * state[i] for i, c in ctr)
    return tuple(state)


def matrix(k):
    cols = [push(k, tuple(1 if i == j else 0 for i in range(6))) for j in range(6)]
    return tuple(tuple(cols[j][i] for j in range(6)) for i in range(6))


def mm(A, B):
    return tuple(
        tuple(sum(A[i][k] * B[k][j] for k in range(6)) for j in range(6))
        for i in range(6)
    )


def main():
    cert = json.loads((ROOT / "CERTIFICATE.json").read_text())
    need(cert["kernel"] == 3, "kernel")
    need(cert["fused_invoice"]["ordinary_children"] == 3, "children")
    need(cert["baseline_invoice"]["ordinary_children"] == 4, "baseline children")
    need(cert["fused_invoice"]["aligned_xor_scans"] == 2, "xor")
    need(cert["baseline_invoice"]["aligned_xor_scans"] == 4, "baseline xor")
    powers = (3, -3, 6, -6, 12, 24, -48)
    for k in powers:
        for col in range(6):
            basis = tuple(1 if i == col else 0 for i in range(6))
            need(run(basis, word(k)) == push(k, basis), f"column k={k} col={col}")
    a = 3
    I = tuple(tuple(Fraction(i == j) for j in range(6)) for i in range(6))
    # Apply M(-a), then M(2a), then M(-a): product M(-a) M(2a) M(-a) = I.
    need(mm(mm(matrix(-a), matrix(2 * a)), matrix(-a)) == I, "query product identity")
    print(
        "PASS_INDEPENDENT_TRIADIC_QUERY_PAIR "
        f"children=4->3 xor=4->2 kernel=3 columns_checked={len(powers)*6} no_new_kappa"
    )


if __name__ == "__main__":
    main()
