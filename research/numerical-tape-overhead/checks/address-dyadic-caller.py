#!/usr/bin/env python3
"""Exact fixed-point DIF/DIT caller on raw equal-length binary words; no trigonometric oracle."""
import argparse
from itertools import islice
from math import isqrt
from random import Random


class DyadicGrid:
    def __init__(self, k):
        self.k = k
        self.bits = 128 * (k+1)
        self.one = 1 << self.bits
        self.h = isqrt(self.one*self.one // 2)
        self.root_n = isqrt((1 << k) * self.one*self.one)
        self.twiddles = self.prepare()

    def nearest(self, value):
        return (value + (self.one >> 1)) >> self.bits

    def times(self, x, y):
        return (self.nearest(x[0]*y[0]-x[1]*y[1]), self.nearest(x[0]*y[1]+x[1]*y[0]))

    def scalar(self, x, y):
        return (self.nearest(x[0]*y), self.nearest(x[1]*y))

    def prepare(self):
        q = self.one
        root = (0, q)
        tables = {}
        for level in range(1, self.k+1):
            if level == 1:
                generator = (-q, 0)
            elif level == 2:
                generator = root
            else:
                c, s = root
                nc = isqrt(q*(q+c)//2)
                ns = (q*s)//(2*nc)
                root = generator = (nc, ns)
            power = (q, 0)
            row = []
            for _ in range(1 << (level-1)):
                row.append(power)
                power = self.times(power, generator)
            tables[level] = tuple(row)
        return tables

    def butterfly(self, left, right, twiddle, reverse):
        if reverse:
            right = self.times(right, (twiddle[0], -twiddle[1]))
        plus = self.scalar((left[0]+right[0], left[1]+right[1]), self.h)
        minus = self.scalar((left[0]-right[0], left[1]-right[1]), self.h)
        return plus, minus if reverse else self.times(minus, twiddle)

    def transform(self, word, reverse=False):
        levels = range(1, self.k+1) if reverse else range(self.k, 0, -1)
        for level in levels:
            row = self.twiddles[level]
            stream = iter(word)
            result = []
            for _ in range(1 << (self.k-level)):
                left = tuple(islice(stream, len(row)))
                parked = []
                for x, tw in zip(left, row):
                    plus, minus = self.butterfly(x, next(stream), tw, reverse)
                    result.append(plus)
                    parked.append(minus)
                result.extend(parked)
            assert len(result) == 1 << self.k and next(stream, None) is None
            word = result
        return word


def multiply_raw(raw, certify=False):
    left, right = raw.split('|')
    n = len(left)
    assert n == len(right) and set(left+right) <= {'0','1'}
    b = (n-1).bit_length()
    h = (n+b-1)//b
    k = (4*h-1).bit_length()
    length, beta = 1 << k, 1 << b
    grid = DyadicGrid(k)

    def digits(source):
        least_first = source[::-1]
        return [int(least_first[j:j+b][::-1], 2) for j in range(0,n,b)]

    ds, es = digits(left), digits(right)
    def spectrum(coeffs):
        bank = [(q*grid.one, 0) for q in coeffs] + [(0,0)]*(length-len(coeffs))
        return grid.transform(bank)
    a, bspec = spectrum(ds), spectrum(es)
    back = grid.transform([grid.times(x,y) for x,y in zip(a,bspec)], reverse=True)
    answer = []
    carry = 0
    maximum_numerator = 0
    for j, point in enumerate(back):
        re, im = grid.scalar(point, grid.root_n)
        coefficient = grid.nearest(re)
        if certify:
            wanted = sum(ds[i]*es[j-i] for i in range(max(0,j-h+1),min(j+1,h)))
            assert coefficient == wanted
            maximum_numerator = max(maximum_numerator, abs(re-wanted*grid.one), abs(im))
        carry, lo = divmod(coefficient+carry, beta)
        answer.extend((lo >> bit) & 1 for bit in range(b))
    assert carry == 0 and not any(answer[2*n:])
    external = ''.join(str(v) for v in reversed(answer[:2*n]))
    assert len(external) == 2*n
    return external, k, maximum_numerator.bit_length()-grid.bits


def check(extended):
    random = Random(120830)
    widths = [7, 8, 9, 15, 17, 31, 33, 65, 127, 129, 255, 257, 512]
    if extended:
        widths.extend([1023, 1024, 2048, 4097])
    observed = set()
    worst = -10**6
    count = 0
    for n in widths:
        cases = [(0,0), ((1<<n)-1,(1<<n)-1), (random.getrandbits(n),random.getrandbits(n))]
        for x, y in cases:
            out, k, exponent = multiply_raw(f'{x:0{n}b}|{y:0{n}b}', certify=True)
            assert out == f'{x*y:0{2*n}b}'
            worst = max(worst, exponent)
            observed.add(k)
            count += 1
    print('exact final words and all circular coefficients:', count, 'products, input lengths',
          widths[0], 'through', widths[-1], 'and k values', sorted(observed))
    print('largest component reconstruction error was below 2^'+str(worst))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--extended', action='store_true')
    args = parser.parse_args()
    check(args.extended)
