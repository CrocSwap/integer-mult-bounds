"""Small explicit finite fields and exact row operations used by finite replays."""
from itertools import product


class Field:
    """Polynomial-basis digit encoding; field order and characteristic differ."""
    def __init__(self, q):
        extensions = {4: (2, (1, 1)), 8: (2, (1, 1, 0)), 9: (3, (1, 0))}
        if q in extensions:
            p, modulus = extensions[q]
        elif q in (2, 3, 5, 7):
            p, modulus = q, (0,)
        else:
            raise ValueError("unimplemented arithmetic field")
        self.q = q
        degree = len(modulus)
        coeff = [tuple((a // p**i) % p for i in range(degree)) for a in range(q)]

        def encode(values):
            return sum((value % p)*p**i for i, value in enumerate(values))

        def multiply(a, b):
            word = [0] * (2*degree - 1)
            for i in range(degree):
                for j in range(degree):
                    word[i + j] += coeff[a][i] * coeff[b][j]
            for i in range(len(word) - 1, degree - 1, -1):
                for j, value in enumerate(modulus):
                    word[i - degree + j] -= word[i]*value
            return encode(word[:degree])

        self.add = [[encode([x + y for x, y in zip(coeff[a], coeff[b])])
                     for b in range(q)] for a in range(q)]
        self.mul = [[multiply(a, b) for b in range(q)] for a in range(q)]
        self.neg = [self.add[a].index(0) for a in range(q)]
        self.inv = [0] + [self.mul[a].index(1) for a in range(1, q)]

    def dot(self, a, b):
        value = 0
        for x, y in zip(a, b):
            value = self.add[value][self.mul[x][y]]
        return value

    def vectors(self, width):
        return product(range(self.q), repeat=width)

    def axpy(self, a, x, b):
        return tuple(self.add[u][self.mul[x][v]] for u, v in zip(a, b))

    def basis(self, rows):
        """Canonical nonzero RREF rows, valid for the zero-dimensional quotient."""
        a = [list(row) for row in rows if any(row)]
        if not a:
            return ()
        i = 0
        for j in range(len(a[0])):
            pivot = next((k for k in range(i, len(a)) if a[k][j]), None)
            if pivot is None:
                continue
            a[i], a[pivot] = a[pivot], a[i]
            a[i] = [self.mul[self.inv[a[i][j]]][v] for v in a[i]]
            for k in range(len(a)):
                if k != i and a[k][j]:
                    a[k] = list(self.axpy(a[k], self.neg[a[k][j]], a[i]))
            i += 1
            if i == len(a):
                break
        return tuple(tuple(row) for row in a[:i])
