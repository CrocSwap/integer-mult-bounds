#!/usr/bin/env python3
"""Exact Q(i) negative control for invalid shared-scratch triple lockstep.

This is a three-core microexample, not a replay of the full PR137 producer.
It tests the physical interference that invalidates the candidate in PR139.
The frame step is the unitary Clifford C with coefficients (1 +/- i)/2.
"""
from fractions import Fraction as F
import json
import sys

if sys.flags.optimize:
    raise RuntimeError("Assertions must remain enabled")

N = 1 << 6
ZERO = (F(0), F(0))

def add(x, y):
    return (x[0] + y[0], x[1] + y[1])

def sub(x, y):
    return (x[0] - y[0], x[1] - y[1])

def mul(x, y):
    return (x[0]*y[0] - x[1]*y[1], x[0]*y[1] + x[1]*y[0])

def conj(x):
    return (x[0], -x[1])

A = (F(1, 2), F(1, 2))
B = (F(1, 2), F(-1, 2))

def gate(values, axis, inverse=False):
    a = conj(A) if inverse else A
    b = conj(B) if inverse else B
    out = list(values)
    for k in range(N):
        if k & (1 << axis):
            continue
        j = k | (1 << axis)
        out[k] = add(mul(a, values[k]), mul(b, values[j]))
        out[j] = add(mul(b, values[k]), mul(a, values[j]))
    return out

def frame(z, core, inverse=False):
    # Each core has a distinct two-bit active address subspace.
    axes = [2*core, 2*core+1]
    if inverse:
        axes.reverse()
    for axis in axes:
        z = gate(z, axis, inverse=inverse)
    return z

def vecadd(x, y):
    return [add(a, b) for a, b in zip(x, y)]

def vecsub(x, y):
    return [sub(a, b) for a, b in zip(x, y)]

SOURCE = [[(F((i+1)*7+j%5), F((i+2)*(j%3))) for j in range(N)]
          for i in range(3)]
TARGET = [[(F(i+j%7), F(i-j%3)) for j in range(N)]
          for i in range(3)]
DIRTY = [(F(j%5-2), F((j*j)%7-3)) for j in range(N)]

def serial():
    y = [list(v) for v in TARGET]
    z = list(DIRTY)
    for i in range(3):
        # Transparent completed core, including a nontrivial Clifford pair.
        y[i] = vecsub(y[i], z)
        z = vecadd(z, SOURCE[i])
        z = frame(z, i)
        z = frame(z, i, inverse=True)
        y[i] = vecadd(y[i], z)
        z = vecsub(z, SOURCE[i])
    return y, z

def invalid_lockstep():
    y = [vecsub(v, DIRTY) for v in TARGET]
    z = list(DIRTY)
    for x in SOURCE:
        z = vecadd(z, x)
    # A joint rank-3r gate can equal the product of separate frame gates.
    for i in range(3):
        z = frame(z, i)
    for i in range(2, -1, -1):
        z = frame(z, i, inverse=True)
    for i in range(3):
        y[i] = vecadd(y[i], z)
    for x in SOURCE:
        z = vecsub(z, x)
    return y, z

def run():
    merged = list(DIRTY)
    opposite_order = list(DIRTY)
    for i in range(3):
        merged = frame(merged, i)
    for i in range(2, -1, -1):
        opposite_order = frame(opposite_order, i)
    assert merged == opposite_order, "Disjoint frame gates must commute"
    unmerged = merged
    for i in range(2, -1, -1):
        unmerged = frame(unmerged, i, inverse=True)
    assert unmerged == DIRTY, "Exact Clifford inverse failed"

    expected = [vecadd(y, x) for y, x in zip(TARGET, SOURCE)]
    y0, z0 = serial()
    y1, z1 = invalid_lockstep()
    assert z0 == z1 == DIRTY, "All scratch must be restored"
    assert y0 == expected, "Sequential schedule must preserve every target"
    errors = [sum(a != b for a, b in zip(y, t)) for y, t in zip(y1, expected)]
    assert errors == [N, N, N], "Lockstep interference regression disappeared"
    all_sources = [ZERO] * N
    for source in SOURCE:
        all_sources = vecadd(all_sources, source)
    assert all(y == vecadd(t, all_sources) for y, t in zip(y1, TARGET)), (
        "Unexpected form of shared-source leakage"
    )
    return {
        "result": "PASS negative control: three-core lockstep schedule must be rejected",
        "arithmetic": "exact Q(i) with Fraction, no floating point",
        "address_bits": 6, "addresses": N,
        "orthogonal_active_blocks": [[0, 1], [2, 3], [4, 5]],
        "merged_frame_algebra_passes": True,
        "sequential_scratch_restored": True,
        "sequential_target_errors": 0,
        "lockstep_scratch_restored": True,
        "lockstep_target_errors_per_core": errors,
        "lockstep_target_errors_total": sum(errors),
        "scope": "Microexample only: disproves naive lockstep, not full PR137"
    }

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
