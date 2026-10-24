#!/usr/bin/env python3
"""Exact permutation census and Gaussian-integer controls; standard library only."""
from __future__ import annotations

import hashlib
import itertools
import json
import math
from pathlib import Path
import platform

Perm = tuple[int, ...]
Gaussian = tuple[int, int]
Matrix = tuple[tuple[Gaussian, ...], ...]


class VerificationError(Exception):
    """A mathematical certificate or a rejection control failed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def inverse(p: Perm) -> Perm:
    result = [0] * len(p)
    for x, image in enumerate(p):
        result[image] = x
    return tuple(result)


def translated_conjugate(p: Perm, pinv: Perm, v: int) -> Perm:
    return tuple(p[pinv[x] ^ v] for x in range(len(p)))


def obstruction(p: Perm) -> tuple[int, int, int] | None:
    """Return (v,w,x) witnessing [P X_v P^-1, X_w] != 1, or None."""
    n = len(p)
    pinv = inverse(p)
    for v in range(1, n):
        q = translated_conjugate(p, pinv, v)
        if all(q[x] == (x ^ q[0]) for x in range(n)):
            continue
        for bit in range(n.bit_length() - 1):
            w = 1 << bit
            for x in range(n):
                if q[x ^ w] != (q[x] ^ w):
                    return v, w, x
        raise VerificationError("nontranslation commuted with all basis shifts")
    return None


def affine_maps(m: int) -> set[Perm]:
    """Independently construct all maps x -> b + Mx by column enumeration."""
    require(1 <= m <= 3, "bounded census dimension")
    n = 1 << m
    result: set[Perm] = set()
    for columns in itertools.permutations(range(1, n), m):
        linear = []
        for x in range(n):
            image = 0
            for bit in range(m):
                if x & (1 << bit):
                    image ^= columns[bit]
            linear.append(image)
        if len(set(linear)) == n:
            for b in range(n):
                result.add(tuple(image ^ b for image in linear))
    return result


def census(m: int) -> dict[str, int]:
    n = 1 << m
    affines = affine_maps(m)
    formula = n * math.prod(n - (1 << j) for j in range(m))
    require(len(affines) == formula, "affine construction count")
    normalizers = 0
    nonlinear = 0
    for p in itertools.permutations(range(n)):
        witness = obstruction(p)
        require((witness is None) == (p in affines), "classification mismatch")
        if witness is None:
            normalizers += 1
        else:
            v, w, x = witness
            q = translated_conjugate(p, inverse(p), v)
            require(q[x ^ w] != (q[x] ^ w), "invalid noncommutation witness")
            nonlinear += 1
    require(normalizers == formula, "normalizer formula")
    require(normalizers + nonlinear == math.factorial(n), "census coverage")
    return {"m": m, "permutations": math.factorial(n),
            "normalizers": normalizers, "nonlinear_witnesses": nonlinear}


def multiply(a: Matrix, b: Matrix) -> Matrix:
    """Multiply eight-by-eight matrices over Z[i], with no float arithmetic."""
    rows = []
    for r in range(8):
        row = []
        for c in range(8):
            real = imag = 0
            for k in range(8):
                ar, ai = a[r][k]
                br, bi = b[k][c]
                real += ar * br - ai * bi
                imag += ar * bi + ai * br
            row.append((real, imag))
        rows.append(tuple(row))
    return tuple(rows)


def root(v: int) -> Matrix:
    """The exact Gaussian-integer matrix 2 C_v, for three-bit addresses."""
    return tuple(tuple((int(r == c) + int(r == (c ^ v)),
                        int(r == c) - int(r == (c ^ v)))
                       for c in range(8)) for r in range(8))


def toffoli_fixture() -> dict[str, object]:
    p = tuple(x ^ (4 if (x & 3) == 3 else 0) for x in range(8))
    pinv = inverse(p)
    require(pinv == p, "Toffoli must be an involution")
    q = translated_conjugate(p, pinv, 1)
    expected = tuple((x ^ 1) ^ (4 if x & 2 else 0) for x in range(8))
    require(q == expected, "Toffoli conjugation formula")
    commutator = tuple(q[q[x ^ 2] ^ 2] for x in range(8))
    require(commutator == tuple(x ^ 4 for x in range(8)), "commutator X_4")
    require(obstruction(p) is not None, "nonlinear fixture admitted")
    for v in range(1, 8):
        square = multiply(root(v), root(v))
        expected_square = tuple(tuple((4 * int(r == (c ^ v)), 0)
                                     for c in range(8)) for r in range(8))
        require(square == expected_square, "C_v squared is not X_v")
    conjugated = tuple(tuple(root(1)[pinv[r]][pinv[c]]
                             for c in range(8)) for r in range(8))
    require(multiply(conjugated, root(2)) != multiply(root(2), conjugated),
            "literal conjugated call roots commute")
    return {"permutation": p, "conjugated_shift_1": q,
            "commutator_with_shift_2": commutator,
            "literal_call_roots_noncommute": True}


def rejection_controls(counts: list[dict[str, int]], fixture: dict[str, object]) -> int:
    """Reject distinct false mathematical claims, also under optimized Python."""
    rejected = 0
    for control in range(4):
        try:
            if control == 0:
                require(counts[2]["normalizers"] == 1345, "forged census")
            elif control == 1:
                p = fixture["permutation"]
                require(isinstance(p, tuple) and p in affine_maps(3),
                        "Toffoli falsely declared affine")
            elif control == 2:
                require(fixture["commutator_with_shift_2"] == tuple(range(8)),
                        "nontrivial commutator erased")
            else:
                require(multiply(root(1), root(1)) == root(1),
                        "root falsely declared idempotent")
        except VerificationError:
            rejected += 1
        else:
            raise VerificationError("a false claim passed a rejection control")
    require(rejected == 4, "control coverage")
    return rejected


def main() -> None:
    counts = [census(m) for m in range(1, 4)]
    fixture = toffoli_fixture()
    rejected = rejection_controls(counts, fixture)
    package = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    print(json.dumps({"result": "PASS_NO_PHASE_NONLINEAR_BOUNDARY",
                      "census": counts, "toffoli": fixture,
                      "rejected_controls": rejected,
                      "python": platform.python_version(), "sha256": hashes},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
