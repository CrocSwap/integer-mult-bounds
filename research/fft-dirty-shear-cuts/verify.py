#!/usr/bin/env python3
"""Exact gate-cut identities over Q(exp(pi*i/4)); standard library only."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def scalar(value):
    return (Q(value), Q(0), Q(0), Q(0))


ZERO, ONE = scalar(0), scalar(1)
ZETA = (Q(0), Q(1), Q(0), Q(0))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def neg(a):
    return tuple(-x for x in a)


def mul(a, b):
    out = [Q(0)] * 4
    for i in range(4):
        for j in range(4):
            if a[i] and b[j]:
                out[(i + j) % 4] += a[i] * b[j] * (1 if i + j < 4 else -1)
    return tuple(out)


def power(a, exponent):
    require(0 <= exponent <= 8, "power domain")
    out = ONE
    for _ in range(exponent):
        out = mul(out, a)
    return out


ROOTS = tuple(power(ZETA, j) for j in range(8))
INV_SQRT2 = tuple(x / 2 for x in add(ROOTS[1], neg(ROOTS[3])))


def conjugate(a):
    out = ZERO
    for j in range(4):
        out = add(out, mul(scalar(a[j]), ROOTS[(-j) % 8]))
    return out


def identity(n):
    return tuple(tuple(ONE if i == j else ZERO for j in range(n)) for i in range(n))


def adjoint(a):
    return tuple(tuple(conjugate(a[j][i]) for j in range(len(a))) for i in range(len(a)))


def multiply(a, b):
    n = len(a)
    out = [[ZERO] * n for _ in range(n)]
    for i in range(n):
        for k in range(n):
            if a[i][k] != ZERO:
                for j in range(n):
                    if b[k][j] != ZERO:
                        out[i][j] = add(out[i][j], mul(a[i][k], b[k][j]))
    return tuple(tuple(row) for row in out)


def matrix_add(a, b):
    return tuple(tuple(add(x, y) for x, y in zip(r, s)) for r, s in zip(a, b))


def matrix_neg(a):
    return tuple(tuple(neg(x) for x in row) for row in a)


def shear(a):
    m = len(a)
    return tuple(tuple(ONE if i == j else a[i-m][j] if i >= m and j < m else ZERO
                       for j in range(2*m)) for i in range(2*m))


def apply_left(a, gate):
    indices, block = gate
    out = [list(row) for row in a]
    for i, target in enumerate(indices):
        for j in range(len(a)):
            value = ZERO
            for k, source in enumerate(indices):
                value = add(value, mul(block[i][k], a[source][j]))
            out[target][j] = value
    return tuple(tuple(row) for row in out)


def layer_matrix(n, gates, mask):
    out = identity(n)
    for j, gate in enumerate(gates):
        if mask >> j & 1:
            out = apply_left(out, gate)
    return out


def fourier(m):
    require(m in (1, 2, 4), "finite checker supports m=1,2,4")
    scale = INV_SQRT2 if m == 2 else scalar(Q(1, m // 2) if m == 4 else 1)
    return tuple(tuple(mul(scale, ROOTS[(-8*i*j//m) % 8]) for j in range(m))
                 for i in range(m))


def fft_layers(m):
    bits = m.bit_length() - 1
    swaps = []
    for i in range(m):
        j = int(f"{i:0{bits}b}"[::-1], 2) if bits else 0
        if i < j:
            for offset in (0, m):
                swaps.append(((offset+i, offset+j), ((ZERO, ONE), (ONE, ZERO))))
    out = [tuple(swaps)] if swaps else []
    for level in range(1, bits+1):
        size = 1 << level
        gates = []
        for offset in (0, m):
            for start in range(0, m, size):
                for j in range(size//2):
                    w = ROOTS[(-8*j//size) % 8]
                    v = mul(INV_SQRT2, w)
                    gates.append(((offset+start+j, offset+start+j+size//2),
                                  ((INV_SQRT2, v), (INV_SQRT2, neg(v)))))
        out.append(tuple(gates))
    return out


def spectral(m, symbol, twisted):
    f = fourier(m)
    d = tuple(ROOTS[(4*j//m) % 8] if twisted else ONE for j in range(m))
    frame = tuple(tuple(mul(f[i][j], d[j]) for j in range(m)) for i in range(m))
    lam = []
    for i in range(m):
        value = ZERO
        for j in range(m):
            value = add(value, mul(mul(ROOTS[(-8*i*j//m) % 8], d[j]), symbol[j]))
        lam.append(value)
    return frame, tuple(lam), d


def masked_component(frame, lam, mask):
    m = len(lam)
    diagonal = tuple(tuple(lam[i] if i == j and mask >> i & 1 else ZERO
                           for j in range(m)) for i in range(m))
    return multiply(multiply(adjoint(frame), diagonal), frame)


def compile_component(m, symbol, twisted):
    frame, lam, d = spectral(m, symbol, twisted)
    layers = []
    if twisted:
        layers.append(("unitary", tuple(((j,), ((d[j % m],),)) for j in range(2*m))))
    fft = fft_layers(m)
    layers.extend(("unitary", gates) for gates in fft)
    layers.append(("shear", tuple(((i, m+i), ((ONE, ZERO), (lam[i], ONE))) for i in range(m))))
    layers.extend(("unitary", tuple((indices, adjoint(block)) for indices, block in gates))
                  for gates in reversed(fft))
    if twisted:
        layers.append(("unitary", tuple(((j,), ((conjugate(d[j % m]),),)) for j in range(2*m))))
    return layers, frame, lam


def toeplitz_from_split(g, h):
    m = len(g)
    return tuple(tuple(add(g[(i-j) % m], h[i-j] if i >= j else neg(h[m+i-j]))
                       for j in range(m)) for i in range(m))


def validate_layer(n, kind, gates):
    used = set()
    require(kind in ("unitary", "shear"), "layer kind")
    for indices, block in gates:
        require(1 <= len(indices) <= 2 and len(block) == len(indices), "gate shape")
        require(all(0 <= i < n and i not in used for i in indices), "gate overlap")
        require(len(set(indices)) == len(indices), "repeated wire")
        used.update(indices)
        require(all(len(row) == len(indices) for row in block), "block shape")
        if kind == "unitary":
            require(multiply(adjoint(block), block) == identity(len(indices)), "nonunitary gate")
        else:
            require(block[0] == (ONE, ZERO) and block[1][1] == ONE, "dirty shear shape")


def gate_cut_case(g, h):
    m = len(g)
    require(m in (1, 2, 4) and len(h) == m, "symbol domain")
    require(g[0] == h[0], "canonical diagonal split")
    a = tuple(tuple(ZERO for _ in range(m)) for _ in range(m))
    p, w = identity(2*m), identity(2*m)
    total = toeplitz_from_split(g, h)
    cuts = 0
    for twisted, symbol in ((False, g), (True, h)):
        layers, frame, lam = compile_component(m, symbol, twisted)
        require(multiply(adjoint(frame), frame) == identity(m), "Fourier frame")
        component = masked_component(frame, lam, (1 << m)-1)
        before = a
        for kind, gates in layers:
            validate_layer(2*m, kind, gates)
            full = (1 << len(gates))-1
            for mask in range(full+1):
                part = layer_matrix(2*m, gates, mask)
                actual = multiply(part, p)
                cut_w = multiply(part, w) if kind == "unitary" else w
                cut_a = a if kind == "unitary" else matrix_add(before, masked_component(frame, lam, mask))
                require(actual == multiply(cut_w, shear(cut_a)), "prefix cut invariant")
                inv = multiply(shear(matrix_neg(cut_a)), adjoint(cut_w))
                suffix = multiply(shear(total), inv)
                rest = matrix_add(total, matrix_neg(cut_a))
                require(suffix == multiply(shear(rest), adjoint(cut_w)), "suffix cut invariant")
                cuts += 1
            p = multiply(layer_matrix(2*m, gates, full), p)
            if kind == "unitary":
                w = multiply(layer_matrix(2*m, gates, full), w)
            else:
                a = matrix_add(before, component)
        require(w == identity(2*m), "component source/target frame restoration")
    require(a == total and p == shear(total), "Toeplitz endpoint")
    return cuts


def reject(call, label):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("control accepted: " + label)


def controls():
    bad = ((0, 1), ((ONE, ONE), (ZERO, ONE)))
    answers = [reject(lambda: validate_layer(2, "unitary", (bad,)), "nonunitary gate"),
               reject(lambda: validate_layer(2, "shear", (bad,)), "wrong shear direction"),
               reject(lambda: validate_layer(2, "unitary", (((0,), ((ONE,),)),)*2), "overlapping gates"),
               reject(lambda: gate_cut_case((ONE,)*3, (ZERO,)*3), "nondyadic checker input")]
    g, h = (ONE, ROOTS[2]), (ONE, ONE)
    t = toeplitz_from_split(g, h)
    f, lam, _ = spectral(2, h, False)
    wrong = matrix_add(masked_component(f, spectral(2, g, False)[1], 3),
                       masked_component(f, lam, 3))
    require(t != wrong, "missing twist must change endpoint")
    answers.append("missing negacyclic twist")
    require(shear(t) != shear(matrix_neg(t)), "wrong final sign must change endpoint")
    answers.append("wrong final shear sign")
    require(mul(INV_SQRT2, INV_SQRT2) == scalar(Q(1, 2)), "exact sqrt2 field")
    require(mul(ROOTS[1], conjugate(ROOTS[1])) == ONE, "unit root")
    # For beta=3/2, the sharp singular norm is exactly 2.
    b = scalar(Q(3, 2))
    s = shear(((b,),))
    gram = multiply(adjoint(s), s)
    v = ((scalar(2), ZERO), (ONE, ZERO))
    require(multiply(gram, v) == tuple(tuple(mul(scalar(4), x) for x in row) for row in v),
            "sharp shear singular value")
    require(multiply(shear(((neg(b),),)), s) == identity(2), "arbitrary dirty inverse")
    answers.append("sharp beta=3/2 gives norm 2")
    return answers


def main():
    fixtures = [((scalar(Q(1, 4)),), (scalar(Q(1, 4)),)),
                ((ONE, scalar(Q(1, 3))), (ONE, ROOTS[2])),
                ((scalar(Q(1, 2)), scalar(Q(1, 4)), ZERO, scalar(Q(-1, 8))),
                 (scalar(Q(1, 2)), ZERO, ROOTS[2], scalar(Q(1, 8))))]
    counts = [gate_cut_case(g, h) for g, h in fixtures]
    proof_controls = controls()
    directory = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    receipt = {"status": "PASS_FFT_DIRTY_SHEAR_CUTS", "field": "Q(zeta_8)",
               "fixture_dimensions": [len(g) for g, _ in fixtures],
               "matching_subset_cuts": counts, "controls": proof_controls,
               "source_sha256": {name: sha256((directory/name).read_bytes()).hexdigest() for name in names}}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
