"""Build the cyclic correction and bordered triangular coefficient pages."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import chain

from fine_ring import tz


@dataclass(frozen=True)
class Words:
    width: int
    data: bytes

    @classmethod
    def encode(cls, coefficients, bits):
        numbers=[]
        for v in coefficients:
            x=Fraction(v)
            numbers.append(tz(x.numerator << bits,x.denominator))
        width=max((1+abs(z).bit_length()//8 for z in numbers),default=1)
        return cls(width,b"".join(z.to_bytes(width,"little",signed=True) for z in numbers))

    def __iter__(self):
        view=memoryview(self.data)
        for i in range(0,len(view),self.width):
            yield int.from_bytes(view[i:i+self.width],"little",signed=True)


@dataclass
class ProductPage:
    size: int
    offsets: range
    bits: int
    coefficients: Words


@dataclass
class SolvePage:
    size: int
    width: int
    bits: int
    forward: Words
    backward: Words


class CyclicBand:
    def __init__(self, rows, width):
        """Use input rows of (column, coefficient) pairs or dictionaries."""
        self.rows = []
        for pairs in rows:
            if isinstance(pairs, dict):
                pairs = pairs.items()
            row = {}
            for j, v in pairs:
                if j in row:
                    raise ValueError("Duplicate stored column")
                if v:
                    row[j] = Fraction(v)
            self.rows.append(row)
        n = len(self.rows)
        if n < 1 or width < 0:
            raise ValueError("Invalid cyclic matrix dimensions")
        self.size = n
        self.width = min(width, n // 2)
        for i, row in enumerate(self.rows):
            for j in row:
                if not 0 <= j < n or min((j-i) % n, (i-j) % n) > self.width:
                    raise ValueError("Source coupling exceeds paid cyclic band")

    @classmethod
    def from_rows(cls, rows, width):
        return cls(rows, width)

    def apply_page(self, bits):
        n, w = self.size, self.width
        # For even n one antipodal offset occurs twice at radius n/2.
        # Retain it exactly once, at the negative representative.
        offs = range(-w, w + (2*w != n))
        coefficients = (row.get((i+h) % n, 0) for i, row in enumerate(self.rows) for h in offs)
        return ProductPage(n, offs, bits, Words.encode(coefficients,bits))

    def factor(self, bits):
        """Build the bordered LU in setup; every later read is sequential."""
        n, w = self.size, self.width
        m = n-w
        U = [dict(row) for row in self.rows]
        L = [{} for _ in self.rows]
        for k in range(n):
            pivot = U[k].get(k, 0)
            if not pivot:
                raise ValueError("Zero source pivot")
            if k < m:
                downstream = chain(range(k+1, min(m, k+w+1)), range(m, n))
            else:
                downstream = range(k+1, n)
            for i in downstream:
                left = U[i].pop(k, 0)
                if not left:
                    continue
                multiplier = left / pivot
                L[i][k] = multiplier
                for j, val in U[k].items():
                    if j <= k:
                        continue
                    new = U[i].get(j, 0) - multiplier * val
                    if new:
                        U[i][j] = new
                    else:
                        U[i].pop(j, None)
        def forward():
            for i in range(m):
                yield from (L[i].get(j, 0) for j in range(max(0, i-w), i))
                yield from (L[j].get(i, 0) for j in range(m, n))
            for i in range(m, n):
                yield from (L[i].get(j, 0) for j in range(m, i))
        def backward():
            for i in reversed(range(m, n)):
                yield from (U[i].get(j, 0) for j in range(i+1,n))
                yield 1 / U[i][i]
            for i in reversed(range(m)):
                yield from (U[i].get(j, 0) for j in range(i+1, min(m, i+w+1)))
                yield from (U[i].get(j, 0) for j in range(m, n))
                yield 1 / U[i][i]
        return SolvePage(n,w,bits,Words.encode(forward(),bits),Words.encode(backward(),bits))
