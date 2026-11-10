"""Literal inverse and mask reading for the finite witnesses. No residue or signature classification."""
from fractions import Fraction


class Field:
    def __init__(self, label):
        self.label = label
        self.modulus = {"Q":0, "F2":2, "F3":3, "F4":4}[label]

    def value(self, a):
        return Fraction(a) if self.label == "Q" else a % self.modulus

    def minus(self, a, b):
        if self.label == "F4":
            return a ^ b
        return (a-b) % self.modulus if self.modulus else a-b

    def times(self, a, b):
        if self.label == "F4":
            # F2[z]/(z^2+z+1), coefficient bits in ascending degree.
            raw = (a if b&1 else 0) ^ (a << 1 if b&2 else 0)
            return raw ^ 7 if raw & 4 else raw
        return (a*b) % self.modulus if self.modulus else a*b

    def reciprocal(self, a):
        if self.label == "F4":
            return (None,1,3,2)[a]
        return pow(a, -1, self.modulus) if self.modulus else 1/a


def inverse(matrix, field):
    n = len(matrix)
    f = Field(field)
    rows = [[f.value(a) for a in row] + [int(i == j) for j in range(n)] for i,row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j,n) if rows[i][j]), None)
        if pivot is None:
            return None
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = f.reciprocal(rows[j][j])
        rows[j] = [f.times(scale,x) for x in rows[j]]
        for i in range(n):
            if i != j and rows[i][j]:
                c = rows[i][j]
                rows[i] = [f.minus(x,f.times(c,y)) for x,y in zip(rows[i],rows[j],strict=True)]
    return tuple(tuple(row[n:]) for row in rows)


def masks(matrix, inv, p):
    symbols = []
    for j in range(len(matrix)):
        sources = int(any(row[j] for row in matrix[:p])) + 2*int(any(row[j] for row in matrix[p:]))
        readers = int(any(inv[j][:p])) + 2*int(any(inv[j][p:]))
        symbols.append(4*sources + readers)
    return tuple(symbols)


def inverse_is_two_sided(matrix, inv, field):
    f = Field(field)
    n = len(matrix)
    for first, second in ((matrix,inv), (inv,matrix)):
        for i in range(n):
            for j in range(n):
                # Subtract the entire dot product from the desired entry.
                delta = int(i == j)
                for k in range(n):
                    delta = f.minus(delta, f.times(first[i][k], second[k][j]))
                if delta:
                    return False
    return True
