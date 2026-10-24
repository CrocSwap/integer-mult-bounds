#!/usr/bin/env python3
"""Check the packed carry polynomial on exact q-binomial tensor kernels."""

from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path
import hashlib
import json
import os
import platform
import resource
import time

from verify_newton_hybrid import Cyclotomic


def digits(n, radices):
    out = []
    for q in radices:
        out.append(n % q)
        n //= q
    assert n == 0
    return out


def add(x, y):
    return tuple(a+b for a, b in zip(x, y))


def scale(x, a):
    return tuple(v*a for v in x)


def run_case(radices):
    ell, size = len(radices), prod(radices)
    fields = [Cyclotomic(q, 1+(i % 2)) for i, q in enumerate(radices)]
    local = []
    for f in fields:
        table = [f.one]
        for j in range(1, f.q):
            table.append(f.multiply(table[-1], f.inverse_one_minus_root(j)))
        local.append(table)
    basis = list(product(*(range(q-1) for q in radices)))
    zero = (F(),)*len(basis)
    tuples = [digits(n, radices) for n in range(size)]
    kernel = []
    for ds in tuples:
        kernel.append(tuple(prod(local[i][ds[i]][bs[i]] for i in range(ell))
                            for bs in basis))
    beta = [F()]*ell
    following = F()
    for i in range(ell-1, -1, -1):
        following = (1+following)/radices[i]
        beta[i] = following
    weights = [sum((b*d for b, d in zip(beta, ds)), F()) for ds in tuples]
    assert max(weights) == ell-beta[0]
    assert all((size*s).denominator == 1 for s in weights)
    operand = [F((11*n+7) % 13-6) for n in range(size)]
    packed = [[zero for _ in range(ell+1)] for _ in range(size)]
    pair_checks = 0
    for x in range(size):
        for y in range(size):
            r = (x+y) % size
            exponent = weights[x]+weights[y]-weights[r]
            assert exponent.denominator == 1 and 0 <= exponent <= ell
            no_coordinate_overflow = all(a+b < q for a, b, q in
                                         zip(tuples[x], tuples[y], radices))
            assert (exponent == 0) == no_coordinate_overflow
            if exponent == 0:
                assert tuples[r] == [a+b for a, b in zip(tuples[x], tuples[y])]
            packed[r][int(exponent)] = add(packed[r][int(exponent)],
                                           scale(kernel[x], operand[y]))
            pair_checks += 1
    direct = []
    for rd in tuples:
        total = zero
        for y, yd in enumerate(tuples):
            if all(a <= b for a, b in zip(yd, rd)):
                difference = [b-a for a, b in zip(yd, rd)]
                index = 0
                place = 1
                for q, d in zip(radices, difference):
                    index += place*d
                    place *= q
                total = add(total, scale(kernel[index], operand[y]))
        direct.append(total)
    assert [row[0] for row in packed] == direct
    false_wrap_outputs = sum(
        tuple(sum(v[k] for v in row) for k in range(len(basis))) != desired
        for row, desired in zip(packed, direct))
    assert false_wrap_outputs > 0
    # Use an exact root average in Q[z]/(1+...+z^(L-1)) for L=3,
    # and Q[z]/(z^2+1) for L=4. Both give primitive roots.
    length = ell+1
    assert length in (3, 4)
    for row in packed:
        for k in range(len(basis)):
            accum = [F()]*length
            for j in range(length):
                for degree, coeff in enumerate(row):
                    accum[j*degree % length] += coeff[k]
            if length == 3:
                reduced = (accum[0]-accum[2], accum[1]-accum[2])
            else:
                reduced = (accum[0]-accum[2], accum[1]-accum[3])
            assert reduced == (length*row[0][k], F())
    position = 1
    rank = [0]
    for s in range(ell):
        y = size-position
        matching = (-y) % size
        assert matching == position and kernel[matching] != zero
        assert weights[matching]+weights[y] == ell-s
        rank.append(y)
        position *= radices[s]
    return {"radices": radices, "T": size, "tensor_coefficient_basis": len(basis),
            "pair_checks": pair_checks, "coefficient_output_checks": size*len(basis),
            "root_average_length": length, "constant_readout_rank": len(rank),
            "wrong_full_wrap_outputs": false_wrap_outputs,
            "S_max": str(max(weights))}


def main():
    directory = Path(__file__).resolve().parent
    assert os.statvfs(directory).f_bavail*os.statvfs(directory).f_frsize >= 3*1024**3
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    started = time.perf_counter()
    cases = [run_case(radices) for radices in ((3, 5), (3, 3, 3))]
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() != "Darwin":
        rss *= 1024
    assert rss < 512*1024**2
    result = {"status": "PASS", "scope": "Exact formal carry polynomials and primitive-root average on tensor q-binomial kernels; no fast tape supplier",
              "cases": cases, "elapsed_seconds": time.perf_counter()-started,
              "max_rss_bytes": rss,
              "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "kernel_source_sha256": hashlib.sha256((directory/"verify_newton_hybrid.py").read_bytes()).hexdigest()}
    (directory/"Q-KERNEL-CARRY-RECEIPT.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

