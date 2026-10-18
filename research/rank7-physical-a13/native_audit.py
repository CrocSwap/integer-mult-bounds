# SPDX-License-Identifier: Apache-2.0
"""Separate native elementary-circuit replay on every Gaussian input column."""

import hashlib
import json
from fractions import Fraction

from vendor.clifford_exact import (
    canonical_frame,
    cgate,
    diag,
    inv,
    parity,
    perm,
    transpose,
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def columns(operator):
    need(operator.n == 9 and len(operator.circuit) <= 30, "bounded native circuit")
    result = []
    for x in range(512):
        vector, denominator = operator.zero_state(x)
        need(0 <= denominator <= 6, "native denominator")
        result.append(
            [
                [y, str(Fraction(a, 2**denominator)), str(Fraction(b, 2**denominator))]
                for y, (a, b) in enumerate(vector)
                if a or b
            ]
        )
    return result


def run(g):
    need(len(g) == 9, "native binary map")
    matrix = transpose(tuple(g), 9)
    inverse = inv(matrix, 9)
    inverse_rows = transpose(inverse, 9)
    q = tuple(
        (1 << i) ^ sum(parity(a & b) << j for j, b in enumerate(inverse_rows))
        for i, a in enumerate(inverse_rows)
    )
    k = perm(9, matrix).then(diag(9, q))
    f0, f1 = canonical_frame(9, [382]), canonical_frame(9, [45])
    # Execute entry adapter and physical warp separately, without telescoping.
    entry = cgate(9, 382).adjoint().then(f0)
    warp = f0.adjoint().then(k).then(f1)
    closed = columns(entry.then(warp).then(warp.adjoint()))
    need(closed == columns(entry), "closing physical source warp")
    result = {
        "source": columns(entry.then(warp)),
        "target": columns(f1),
        "closed_source": closed,
    }
    return {
        name: hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        for name, value in result.items()
    }
