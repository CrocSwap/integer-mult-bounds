"""Exact rational scalar checker; dictionary method credited to #7834.

Semantic checking is not a literal tape machine or funded-word existence.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from math import lcm

ZERO, ONE = (F(0), F(0)), (F(1), F(0))
ARITY = {"add": 2, "sub": 2, "half": 1, "clear": 1, "neg": 1,
         "i": 1, "unit": 1, "x": 2, "s": 2, "cz": 3,
         "cx": 3, "paid": 2, "scale": 4}
NAMES = tuple(ARITY)
NATIVE = {"unit", "x", "s", "cz", "cx", "paid"}


def plus(x, y):
    return x[0] + y[0], x[1] + y[1]


def times(x, y):
    return x[0]*y[0] - x[1]*y[1], x[0]*y[1] + x[1]*y[0]


def turn(x, k=1):
    a, b = x
    return ((a, b), (-b, a), (-a, -b), (b, -a))[k % 4]


def identity(n):
    return tuple(tuple(ONE if i == j else ZERO for j in range(1 << n))
                 for i in range(1 << n))


def matrix_product(a, b):
    def entry(i, j):
        z = ZERO
        for k in range(len(a)):
            z = plus(z, times(a[i][k], b[k][j]))
        return z
    return tuple(tuple(entry(i, j) for j in range(len(a))) for i in range(len(a)))


def column_matrix(n, op, axes=()):
    """One-column operator, retaining its absolute complex phase."""
    out = [[ZERO for _ in range(1 << n)] for _ in range(1 << n)]
    for j in range(1 << n):
        if op == "paid":
            out[j][j] = F(1, 2), F(1, 2)
            out[j ^ (1 << axes[0])][j] = F(1, 2), F(-1, 2)
        elif op in ("x", "cx"):
            dest = j ^ (1 << axes[0]) if op == "x" else j ^ (((j >> axes[0]) & 1) << axes[1])
            out[dest][j] = ONE
        else:
            exponent = (1 if op == "unit" else (j >> axes[0]) & 1
                        if op == "s" else 2*((j >> axes[0]) & 1)*((j >> axes[1]) & 1))
            out[j][j] = turn(ONE, exponent)
    return tuple(tuple(row) for row in out)


@dataclass(frozen=True)
class Word:
    dimension: int
    productive: int
    owned: int
    ops: tuple

    def valid_syntax(self):
        if any(type(v) is not int for v in (self.dimension, self.productive, self.owned)):
            return False
        if self.dimension < 2 or self.productive < 2 or self.owned < 0:
            return False
        for instruction in self.ops:
            if not instruction:
                return False
            op, *args = instruction
            if op not in ARITY or len(args) != ARITY[op] or any(type(v) is not int for v in args):
                return False
            if not 0 <= args[0] < self.productive + self.owned:
                return False
            if op in ("add", "sub") and not 0 <= args[1] < self.productive + self.owned:
                return False
            if op == "scale" and args[3] <= 0:
                return False
            if op in NATIVE and any(not 0 <= v < self.dimension for v in args[1:]):
                return False
            if op in ("cz", "cx") and args[1] == args[2]:
                return False
        return True

    def funded(self, saving=F(1, 500)):
        if not self.valid_syntax() or not 0 < saving < 1:
            return False
        p = sum(op[0] == "paid" for op in self.ops)
        a, b = saving.numerator, saving.denominator
        return p**b < self.productive**b * self.dimension**(b-a)

    def constants(self):
        """Odd denominator LCM and strict numerator/denominator height."""
        d, m = 1, 2
        for op, *args in self.ops:
            if op == "scale":
                _, a, b, q = args
                m = max(m, (abs(a)+abs(b)).bit_length(), q.bit_length())
                while q % 2 == 0:
                    q //= 2
                d = lcm(d, q)
        return d, m

    def all_columns(self):
        if not self.valid_syntax():
            return False
        eye = identity(self.dimension)
        rows = [{(i, eye): ONE} for i in range(self.productive)]
        rows += [{} for _ in range(self.owned)]
        for op, reg, *args in self.ops:
            old = rows[reg]
            if op == "clear":
                new = {}
            elif op in ("add", "sub"):
                new = dict(old)
                for key, value in rows[args[0]].items():
                    value = value if op == "add" else turn(value, 2)
                    new[key] = plus(new.get(key, ZERO), value)
            elif op in NATIVE:
                left, new = column_matrix(self.dimension, op, args), {}
                for (owner, mat), value in old.items():
                    key = owner, matrix_product(left, mat)
                    new[key] = plus(new.get(key, ZERO), value)
            else:
                scalar = ((F(args[0], args[2]), F(args[1], args[2])) if op == "scale"
                          else (F(1, 2), F(0)) if op == "half"
                          else (-F(1), F(0)) if op == "neg" else (F(0), F(1)))
                new = {key: times(value, scalar) for key, value in old.items()}
            rows[reg] = {key: value for key, value in new.items() if value != ZERO}
        target = eye
        for axis in range(self.dimension):
            target = matrix_product(column_matrix(self.dimension, "paid", (axis,)), target)
        return (all(rows[i] == {(i, target): ONE} for i in range(self.productive))
                and all(not rows[i] for i in range(self.productive, len(rows))))


def encode(word):
    """Unary fields, with signed numerators mapped by 2a or -2a-1."""
    if not word.valid_syntax():
        raise ValueError("invalid word")
    fields = [word.dimension, word.productive, word.owned]
    for op, *args in word.ops:
        fields.append(NAMES.index(op))
        for j, arg in enumerate(args):
            if op == "scale" and j in (1, 2):
                arg = 2*arg if arg >= 0 else -2*arg-1
            fields.append(arg)
    return "".join("1"*v + "0" for v in fields)


def parse(code):
    if not code or not code.endswith("0") or any(c not in "01" for c in code):
        return None
    fields = iter(map(len, code[:-1].split("0")))
    try:
        n, w, z = next(fields), next(fields), next(fields)
        ops = []
        for tag in fields:
            op = NAMES[tag]
            args = []
            for j in range(ARITY[op]):
                value = next(fields)
                if op == "scale" and j in (1, 2):
                    value = value//2 if value % 2 == 0 else -(value//2)-1
                args.append(value)
            ops.append((op, *args))
    except (StopIteration, IndexError):
        return None
    word = Word(n, w, z, tuple(ops))
    return word if word.valid_syntax() else None
