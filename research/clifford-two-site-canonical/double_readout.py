"""Canonical four-qubit Clifford coordinates for eleven repeated sites and an arbitrary pair."""
import argparse
from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path

from predecessor import pointed as P
from compile_row import apply


def binary_transform(table):
    """Walsh coefficients in the low four output and high four input bits."""
    for bit in range(8):
        step = 1 << bit
        for k in range(0, 256, 2 * step):
            for i in range(k, k + step):
                left, right = table[i], table[i + step]
                table[i], table[i + step] = left + right, left - right


def prepare(target, row, column, joint, weights, left_basis=P.IDENTITY, right_basis=P.IDENTITY):
    """Return a shared-block readout for Pauli translates of a supplied symplectic map.

    joint contains (i,k,m,n,(real,imag)) in the indicated bases. Duplicate terms add.
    weights(L,u,X,w) is the inverse-transformed marked radial input for the two flags.
    """
    target, left, right = tuple(target), tuple(left_basis), tuple(right_basis)
    relative = P.transformed_inputs(target, left, right)
    P.require(all(type(k) is int and 0 <= k < 16 for k in (row, column)),
              "expected four-bit repeated coordinates")
    space = P.point_set(relative[:4])
    images = [apply(relative, v) for v in range(256)]
    blocks = defaultdict(list)
    for i, k, m, n, (real, imag) in joint:
        P.require(all(type(v) is int and 0 <= v < 16 for v in (i, k, m, n)),
                  "expected four-bit joint coordinates")
        blocks[row ^ i, column ^ k].append((m, n, Fraction(real), Fraction(imag)))

    lanes = {}
    for (x, y), terms in blocks.items():
        table = [weights(P.BASE, (x << 4) | z, space, images[(y << 4) | t])
                 for t in range(16) for z in range(16)]
        binary_transform(table)
        for m, n, real, imag in terms:
            h = table[(row ^ m) | ((column ^ n) << 4)] * Fraction(1,16)
            address = x ^ m, y ^ n
            a, b = lanes.get(address, (0, 0))
            lanes[address] = a + h * real, b + h * imag
    active = [(m, n, scalar) for (m, n), scalar in lanes.items() if scalar != (0, 0)]

    def read(p):
        P.require(type(p) is int and 0 <= p < 256, "expected an eight-bit Pauli label")
        real = imag = Fraction(0)
        for m, n, scalar in active:
            val = P.conjugate(P.transition(target, p, m, n, left, right))
            a, b = P.Q.multiply(scalar, val)
            real += a
            imag += b
        return real, imag
    return read


def main():
    from flag_weights import weight
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    req = json.loads(parser.parse_args().request.read_text())
    left, right = req.get('left_basis', P.IDENTITY), req.get('right_basis', P.IDENTITY)
    readouts = {}
    results = []
    for S, p in req['queries']:
        S = tuple(S)
        if S not in readouts:
            readouts[S] = prepare(S, req['row'], req['column'], req['joint'], weight, left, right)
        results.append([str(x) for x in readouts[S](p)])
    print(json.dumps(results))


if __name__ == '__main__':
    main()
