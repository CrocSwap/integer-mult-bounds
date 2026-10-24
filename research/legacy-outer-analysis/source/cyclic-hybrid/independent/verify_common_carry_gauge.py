#!/usr/bin/env python3
"""Check the weighted carry identity and the finite reciprocal spill."""

from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import os
import platform
import resource
import time


class Field:
    def __init__(self, q, a=1):
        self.q, self.a = q, a
        self.zero = (F(),)*(q-1)
        self.one = (F(1),)+(F(),)*(q-2)

    def root(self, k):
        position = self.a*k % self.q
        if position == self.q-1:
            return (F(-1),)*(self.q-1)
        result = [F()]*(self.q-1)
        result[position] = F(1)
        return tuple(result)

    def add(self, x, y):
        return tuple(a+b for a, b in zip(x, y))

    def scale(self, x, y):
        return tuple(a*y for a in x)

    def multiply(self, x, y):
        result = [F()]*self.q
        for i, a in enumerate(x):
            for j, b in enumerate(y):
                result[(i+j) % self.q] += a*b
        return tuple(a-result[-1] for a in result[:-1])

    def inverse_factor(self, j):
        result = self.zero
        for k in range(self.q):
            result = self.add(result, self.scale(self.root(j*k), F(self.q-1-k, self.q)))
        assert self.multiply(self.add(self.one, self.scale(self.root(j), -1)), result) == self.one
        return result


def spill(q, a):
    f = Field(q, a)
    h = [f.one]
    for j in range(1, q):
        h.append(f.multiply(h[-1], f.inverse_factor(j)))
    g = [f.scale(f.multiply(f.root(j*(j-1)//2), h[j]), (-1)**j) for j in range(q)]
    coefficients = [f.zero for _ in range(2*q-1)]
    for i in range(q):
        for j in range(q):
            coefficients[i+j] = f.add(coefficients[i+j], f.multiply(h[i], g[j]))
    assert coefficients[0] == f.one
    assert all(value == f.zero for value in coefficients[1:q])
    assert coefficients[q] == f.scale(f.one, F(-(q-1), 2*q))
    assert coefficients[-1] == f.scale(f.root(1), F(1, q*q))
    assert coefficients[-1] != f.zero
    if q == 3:
        assert coefficients[3] == f.scale(f.one, F(-1, 3))
        assert coefficients[4] == f.scale(f.root(1), F(1, 9))
    return {"q": q, "a": a,
            "coefficients": [[str(part) for part in value] for value in coefficients],
            "nonzero_spill_degrees": [j for j in range(q, 2*q-1) if coefficients[j] != f.zero]}


def weights(radices):
    beta = [F()]*len(radices)
    following = F()
    for i in range(len(radices)-1, -1, -1):
        following = (1+following)/radices[i]
        beta[i] = following
    return beta


def digits(n, radices):
    result = []
    for q in radices:
        result.append(n % q)
        n //= q
    assert n == 0
    return result


def polynomial(radices, beta, kernel, operand):
    size, ell = len(kernel), len(radices)
    out = [[F()]*(ell+1) for _ in range(size)]
    for n, x in enumerate(kernel):
        if x:
            nd = digits(n, radices)
            sn = sum((b*d for b, d in zip(beta, nd)), F())
            for m, y in enumerate(operand):
                if y:
                    r = (n+m) % size
                    md, rd = digits(m, radices), digits(r, radices)
                    sm = sum((b*d for b, d in zip(beta, md)), F())
                    sr = sum((b*d for b, d in zip(beta, rd)), F())
                    degree = sn+sm-sr
                    assert degree.denominator == 1 and 0 <= degree <= ell
                    carry, count = 0, 0
                    for a, b, q in zip(nd, md, radices):
                        carry = (a+b+carry)//q
                        count += carry
                    assert degree == count
                    out[r][int(degree)] += x*y
    return out


def desired(radices, local, operand):
    size = len(operand)
    result = [F()]*size
    for r in range(size):
        rd = digits(r, radices)
        for m, value in enumerate(operand):
            md = digits(m, radices)
            if all(a <= b for a, b in zip(md, rd)):
                coefficient = F(1)
                for table, a, b in zip(local, md, rd):
                    coefficient *= table[b-a]
                result[r] += coefficient*value
    return result


def evaluate(coefficients, point):
    result = F()
    for value in reversed(coefficients):
        result = result*point+value
    return result


def gauge_case(radices):
    ell, size = len(radices), 1
    for q in radices:
        size *= q
    beta = weights(radices)
    assert sum((b*(q-1) for b, q in zip(beta, radices)), F()) == ell-beta[0]
    assert all(b.denominator <= size and size % b.denominator == 0 for b in beta)
    local = [[F(1, j+1) for j in range(q)] for q in radices]
    kernel = []
    for n in range(size):
        value = F(1)
        for table, digit in zip(local, digits(n, radices)):
            value *= table[digit]
        kernel.append(value)
    operand = [F(((7*n+3) % 9-4) or 1) for n in range(size)]
    result = polynomial(radices, beta, kernel, operand)
    assert [row[0] for row in result] == desired(radices, local, operand)
    position = 1
    rank_positions = []
    for s in range(ell):
        column = size-position
        basis = [F()]*size
        basis[column] = F(1)
        row = polynomial(radices, beta, kernel, basis)[0]
        expected = [F()]*(ell+1)
        expected[ell-s] = kernel[position]
        assert row == expected
        rank_positions.append(column)
        position *= radices[s]
    sample_counterexamples = 0
    for count in range(1, ell+1):
        samples = [F(1, j+2) for j in range(count)]
        coefficients = [F(1)]
        for point in samples:
            new = [F()]*(len(coefficients)+1)
            for k, value in enumerate(coefficients):
                new[k] -= point*value
                new[k+1] += value
            coefficients = new
        coefficients += [F()]*(ell+1-len(coefficients))
        witness = [F()]*size
        witness[0] = coefficients[0]
        position = 1
        for s in range(ell):
            witness[size-position] = coefficients[ell-s]/kernel[position]
            position *= radices[s]
        actual = polynomial(radices, beta, kernel, witness)[0]
        assert actual == coefficients and actual[0] != 0
        assert all(evaluate(actual, point) == 0 for point in samples)
        sample_counterexamples += 1
    root_length = 1
    while root_length <= ell:
        root_length *= 2
    ring = root_length//2
    for row in result:
        average = [F()]*ring
        for j in range(root_length):
            for k, value in enumerate(row):
                exponent = j*k % root_length
                average[exponent % ring] += value*(1 if exponent < ring else -1)
        assert average == [root_length*row[0]]+[F()]*(ring-1)
    return {"radices": radices, "T": size, "ell": ell,
            "beta": [str(b) for b in beta], "S_max": str(ell-beta[0]),
            "pair_checks": size*size, "root_average_length": root_length,
            "rank_columns": [0]+rank_positions,
            "nonzero_sample_counterexamples": sample_counterexamples}


def main():
    directory = Path(__file__).resolve().parent
    stat = os.statvfs(directory)
    assert stat.f_bavail*stat.f_frsize >= 3*1024**3
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    started = time.perf_counter()
    spill_rows = [spill(q, a) for q in (3, 5, 7) for a in (1, 2)]
    gauge_rows = [gauge_case(qs) for qs in ((3,), (3, 5), (3, 5, 7))]
    raw_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss = raw_rss if platform.system() == "Darwin" else raw_rss*1024
    assert rss < 512*1024**2
    result = {"status": "pass", "scope": "Exact carry and spill algebra; no tape compiler",
              "spills": spill_rows, "gauge_cases": gauge_rows,
              "elapsed_seconds": time.perf_counter()-started, "peak_rss_bytes": rss,
              "free_after_bytes": os.statvfs(directory).f_bavail*os.statvfs(directory).f_frsize,
              "verifier_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (directory/'common-carry-gauge-receipt.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ("status", "elapsed_seconds", "peak_rss_bytes")}, indent=2))


if __name__ == '__main__':
    main()
