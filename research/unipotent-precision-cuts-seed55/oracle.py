"""Separate scalar-column oracle, Hanson Sun / OpenAI Codex, Apache-2.0.

No imports from planner or the predecessor. Fraction arithmetic deliberately
does not assume that halving preserves the integer grid.
"""
from fractions import Fraction


def inspect(word, dimension):
    norms = [[0] * dimension for _ in range(len(word)+1)]
    columns, integral = [], True
    for col in range(dimension):
        values = [Fraction(int(row == col)) for row in range(dimension)]
        for row, value in enumerate(values):
            norms[0][row] += abs(value)
        for step, instruction in enumerate(word, 1):
            kind, target, source, numerator, denominator = instruction
            if kind == "ADD":
                values[target] += numerator * values[source]
            elif kind == "SCALE":
                values[target] *= Fraction(numerator, denominator)
            else:
                raise ValueError("unknown instruction")
            integral = integral and values[target].denominator == 1
            for row, value in enumerate(values):
                norms[step][row] += abs(value)
        columns.append(values)
    matrix = [list(row) for row in zip(*columns)]
    peak = max(map(max, norms))
    return matrix, int(peak), integral


def invert(word):
    out = []
    for kind, target, source, numerator, denominator in word[::-1]:
        if kind == "ADD":
            out.append((kind, target, source, -numerator, denominator))
        else:
            out.append((kind, target, source, denominator, numerator))
    return out


def primitive_state(word, state):
    values = [Fraction(x) for x in state]
    for kind, dst, src, num, den in word:
        if kind == "ADD":
            values[dst] += num * values[src]
        else:
            values[dst] *= Fraction(num, den)
    return values


def endpoint(children, m):
    """Direct source-only map, with no workspace drifting in this oracle."""
    dim = 2+4*m
    matrix = [[int(i == j) for j in range(dim)] for i in range(dim)]
    for child in children:
        for dst in range(2):
            for j, coefficient in enumerate(child["reader"][dst]):
                matrix[dst][2+j] += coefficient
    return matrix


def all_partitions(k):
    for mask in range(1 << (k-1)):
        yield [i+1 for i in range(k-1) if (mask >> i) & 1] + [k]


def independent_cost(length, blocks, fused=False):
    """Repeated division, independent of the predecessor's bit-count formula."""
    def power(n):
        additions, scales = 0, 0
        while n:
            additions += n % 2
            n //= 2
            if n:
                scales += 2
        return additions, scales
    first, last = power(length), power(length-1)
    if fused:
        last = (0,0)
    return length-1+blocks*first[0]+last[0], blocks*first[1]+last[1]


def uniform_forward_states(children, m):
    """Derive canonical cuts using eager black-box maps, no frame formula."""
    n = 2+4*m
    zero = [[int(i == j) for j in range(n)] for i in range(n)]

    def add_map(state, child, sign):
        out = [row[:] for row in state]
        for dst in range(2):
            for j, coefficient in enumerate(child["reader"][dst]):
                for col in range(n):
                    out[dst][col] += sign * coefficient * state[2+2*m+j][col]
        return out

    def copy(state, sign):
        out = [row[:] for row in state]
        for j in range(2*m):
            out[2+2*m+j] = [u+sign*x for u,x in zip(out[2+2*m+j],out[2+j])]
        return out

    records = {}
    state = copy(zero, 1)
    records["forward_group"] = [[row[:] for row in state]]
    for child in children:
        state = add_map(state, child, 1)
        records["forward_group"].append(state)
    state = copy(state, -1)
    values = [state]
    for child in children[::-1]:
        state = add_map(state, child, -1)
        values.append(state)
    records["forward_undo"] = values[::-1]
    state = zero
    records["inverse_group"] = [state]
    for child in children:
        state = add_map(state, child, 1)
        records["inverse_group"].append(state)
    state = copy(state, 1)
    values = [state]
    for child in children[::-1]:
        state = add_map(state, child, -1)
        values.append(state)
    records["inverse_undo"] = values[::-1]
    return records
