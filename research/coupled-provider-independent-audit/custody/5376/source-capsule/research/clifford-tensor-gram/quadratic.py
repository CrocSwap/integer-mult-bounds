"""Exact sums of native Clifford paths, with no state vector.

The proof and cost bounds are in ADVANCES.md. Binary affine forms use bit
zero for the constant and bit j+1 for variable j. All phases are retained.
Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import combinations
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "vendor"))
from fields import Gaussian as G


def need(ok, message):
    if not ok:
        raise ValueError(message)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length()-1
        mask ^= low


def parity_sum(values):
    out = 0
    for value in values:
        out ^= value
    return out


class Phase:
    """A constant plus linear terms and even quadratic terms modulo four."""

    def __init__(self, variables):
        self.constant = 0
        self.linear = [0]*variables
        self.cross = set()

    def toggle(self, i, j):
        if i == j:
            self.linear[i] = (self.linear[i]+2) % 4
        else:
            term = tuple(sorted((i, j)))
            self.cross.symmetric_difference_update((term,))

    def add_parity(self, mask, coefficient):
        constant = mask & 1
        variables = list(bits(mask >> 1))
        self.constant = (self.constant+coefficient*constant) % 4
        for i in variables:
            self.linear[i] = (self.linear[i]+coefficient*(1-2*constant)) % 4
        if coefficient % 2:
            self.cross.symmetric_difference_update(combinations(variables, 2))

    def add_product(self, left, right):
        """Add twice the product of two binary affine forms."""
        if left & 1:
            self.add_parity(right, 2)
        if right & 1:
            self.add_parity(left ^ (left & 1), 2)
        for i in bits(left >> 1):
            for j in bits(right >> 1):
                self.toggle(i, j)

    def substitute(self, mapping, variables):
        out = Phase(variables)
        out.constant = self.constant
        for i, coefficient in enumerate(self.linear):
            out.add_parity(mapping[i], coefficient)
        for i, j in self.cross:
            out.add_product(mapping[i], mapping[j])
        return out

    def restrict(self, equations):
        pivots = {}
        for equation in equations:
            while equation > 1:
                pivot = equation.bit_length()-1
                if pivot not in pivots:
                    pivots[pivot] = equation
                    break
                equation ^= pivots[pivot]
            if equation == 1:
                return None
        mapping, free = [], 0
        for j in range(1, len(self.linear)+1):
            if j in pivots:
                equation = pivots[j] ^ (1 << j)
                value = (equation & 1) ^ parity_sum(mapping[k] for k in bits(equation >> 1))
            else:
                free += 1
                value = 1 << free
            mapping.append(value)
        return self.substitute(mapping, free)

    def drop(self, j):
        mapping = [0 if k == j else 1 << (k+1-(k > j)) for k in range(len(self.linear))]
        return self.substitute(mapping, len(mapping)-1), mapping


def gauss_sum(phase, equations=()):
    """Sum i**phase over all solutions of the binary equations."""
    phase = phase.restrict(equations)
    if phase is None:
        return G(0)
    factor = G(1)
    units = (G(1), G("i"), G(-1), G("-i"))
    while phase.linear:
        j = next((j for j, a in enumerate(phase.linear) if a % 2), None)
        if j is not None:
            a = phase.linear[j]
            neighbors = [u if v == j else v for u, v in phase.cross if j in (u, v)]
            phase, mapping = phase.drop(j)
            phase.add_parity(parity_sum(mapping[k] for k in neighbors), -a)
            factor = factor*(1+units[a])
        elif phase.cross:
            j = min(phase.cross)[0]
            constant = phase.linear[j]//2
            neighbors = [u if v == j else v for u, v in phase.cross if j in (u, v)]
            phase, mapping = phase.drop(j)
            equation = constant ^ parity_sum(mapping[k] for k in neighbors)
            phase = phase.restrict((equation,))
            if phase is None:
                return G(0)
            factor = factor*2
        else:
            if any(phase.linear):
                return G(0)
            factor = factor*(1 << len(phase.linear))
            phase.linear = []
    return factor*units[phase.constant]


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            j = row.bit_length()-1
            if j not in pivots:
                pivots[j] = row
                break
            row ^= pivots[j]
    return len(pivots)


class Paths:
    """Build a quadratic path sum from the frozen native gate grammar."""

    def __init__(self, n, circuit):
        need(type(n) is int and n >= 0, "Nonnegative axis count")
        self.n = n
        self.phase = Phase(n)
        self.inputs = [1 << (j+1) for j in range(n)]
        self.outputs = self.inputs.copy()
        self.factor = G(1)
        limit = 1 << n

        def mask(x):
            return type(x) is int and 0 <= x < limit

        for gate in circuit:
            need(type(gate) in (tuple, list) and bool(gate), "Native gate")
            kind = gate[0]
            if kind == "P":
                need(len(gate) == 2 and len(gate[1]) == n and all(mask(x) for x in gate[1])
                     and rank(gate[1]) == n, "Invertible native permutation")
                self.outputs = [parity_sum(self.outputs[j] for j in bits(row)) for row in gate[1]]
            elif kind == "X":
                need(len(gate) == 2 and mask(gate[1]), "Native translation")
                self.outputs = [x ^ ((gate[1] >> j) & 1) for j, x in enumerate(self.outputs)]
            elif kind == "D":
                need(len(gate) == 3 and len(gate[1]) == len(gate[2]) == n, "Native diagonal shape")
                rows, alpha = gate[1:]
                need(all(mask(x) for x in rows) and all(type(a) is int and 0 <= a < 4 for a in alpha),
                     "Native diagonal entries")
                need(all((rows[i] >> j) & 1 == (rows[j] >> i) & 1 for i in range(n) for j in range(n))
                     and all(alpha[j] % 2 == (rows[j] >> j) & 1 for j in range(n)), "Native diagonal parity")
                for j, a in enumerate(alpha):
                    self.phase.add_parity(self.outputs[j], a)
                for i, row in enumerate(rows):
                    for j in bits(row >> (i+1)):
                        self.phase.add_product(self.outputs[i], self.outputs[j+i+1])
            elif kind == "C":
                need(len(gate) == 3 and mask(gate[1]) and type(gate[2]) is int and gate[2] in (-1, 1),
                     "Native C gate")
                q, sign = gate[1:]
                self.phase.linear.append((-sign) % 4)
                variable = 1 << len(self.phase.linear)
                self.outputs = [x ^ (variable if q >> j & 1 else 0) for j, x in enumerate(self.outputs)]
                self.factor = self.factor*G.pair(1, sign)/2
            elif kind == "phase":
                need(len(gate) == 2 and type(gate[1]) is int, "Native global phase")
                self.phase.constant = (self.phase.constant+gate[1]) % 4
            else:
                raise ValueError("Unknown native gate")

    def entry(self, output, input_index):
        need(type(output) is int and type(input_index) is int and
             0 <= output < 1 << self.n and 0 <= input_index < 1 << self.n, "Base coordinate")
        equations = [x ^ ((input_index >> j) & 1) for j, x in enumerate(self.inputs)]
        equations += [x ^ ((output >> j) & 1) for j, x in enumerate(self.outputs)]
        return self.factor*gauss_sum(self.phase, equations)

    def trace(self):
        return self.factor*gauss_sum(self.phase, [x ^ y for x, y in zip(self.inputs, self.outputs)])


def partial_inner(left, right, output_prefix=(), input_prefix=()):
    """Sum conjugate(left[x,y])*right[x,y] over the unspecified bits."""
    need(left.n == right.n, "Common axis count")
    n = left.n
    need(len(output_prefix) <= n and len(input_prefix) <= n and
         all(type(b) is int and b in (0, 1) for b in (*output_prefix, *input_prefix)), "Coordinate prefix")
    a, b = len(left.phase.linear), len(right.phase.linear)
    phase = Phase(a+b)
    phase.constant = (-left.phase.constant+right.phase.constant) % 4
    phase.linear = [(-x) % 4 for x in left.phase.linear]+right.phase.linear
    phase.cross = left.phase.cross | {(i+a, j+a) for i, j in right.phase.cross}

    def shift(mask):
        return (mask & 1) | ((mask >> 1) << (a+1))

    equations = [x ^ shift(y) for x, y in zip(left.inputs, right.inputs)]
    equations += [x ^ shift(y) for x, y in zip(left.outputs, right.outputs)]
    equations += [left.outputs[j] ^ x for j, x in enumerate(output_prefix)]
    equations += [left.inputs[j] ^ x for j, x in enumerate(input_prefix)]
    factor = G.pair(left.factor.real, -left.factor.imag)*right.factor
    return factor*gauss_sum(phase, equations)


def inverse_circuit(n, circuit):
    """Invert a circuit after Paths has checked its gate data."""
    out = []
    for gate in reversed(circuit):
        kind = gate[0]
        if kind == "P":
            rows = [x | (1 << (n+j)) for j, x in enumerate(gate[1])]
            for j in range(n):
                k = next(k for k in range(j, n) if rows[k] >> j & 1)
                rows[j], rows[k] = rows[k], rows[j]
                for k in range(n):
                    if k != j and rows[k] >> j & 1:
                        rows[k] ^= rows[j]
            out.append((kind, tuple(x >> n for x in rows)))
        elif kind == "D":
            out.append((kind, gate[1], tuple((-a) % 4 for a in gate[2])))
        elif kind == "C":
            out.append((kind, gate[1], -gate[2]))
        elif kind == "phase":
            out.append((kind, -gate[1]))
        else:
            out.append(gate)
    return out
