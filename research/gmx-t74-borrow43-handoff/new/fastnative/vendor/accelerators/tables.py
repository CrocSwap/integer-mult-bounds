"""Exact Gaussian-dyadic state evaluation with bounded, state-free gate tables.

Charles Bethin, with substantial OpenAI Codex assistance. Apache-2.0.
The gate semantics and normalization follow the pinned clifford_exact.py.
"""
from functools import lru_cache


@lru_cache(maxsize=64)
def permutation_table(n, rows):
    """Compute Gx from G(x xor lowbit(x)) xor G(lowbit(x))."""
    columns = [sum(((row >> j) & 1) << i for i, row in enumerate(rows))
               for j in range(n)]
    table = [0] * (1 << n)
    for x in range(1, len(table)):
        bit = x & -x
        table[x] = table[x ^ bit] ^ columns[bit.bit_length() - 1]
    return tuple(table)


@lru_cache(maxsize=64)
def phase_table(n, rows, linear):
    """Remove the lowest bit; all remaining quadratic partners have larger indices."""
    table = [0] * (1 << n)
    for x in range(1, len(table)):
        bit = x & -x
        i, rest = bit.bit_length() - 1, x ^ bit
        table[x] = (table[rest] + linear[i] +
                    2 * ((rows[i] & rest).bit_count() & 1)) % 4
    return tuple(table)


def clear_caches():
    permutation_table.cache_clear()
    phase_table.cache_clear()


def zero_state(self, basis=0):
    """Drop-in evaluator for valid pinned Op circuits; return the full exact state."""
    size = 1 << self.n
    vec = [(0, 0)] * size
    vec[basis] = (1, 0)
    den = 0
    for gate in self.circuit:
        kind = gate[0]
        if kind == 'P':
            mapping = permutation_table(self.n, tuple(gate[1]))
            out = [(0, 0)] * size
            for x, value in enumerate(vec):
                out[mapping[x]] = value
            vec = out
        elif kind == 'X':
            vec = [vec[x ^ gate[1]] for x in range(size)]
        elif kind in ('D', 'phase'):
            phases = (phase_table(self.n, tuple(gate[1]), tuple(gate[2]))
                      if kind == 'D' else [gate[1] % 4] * size)
            out = []
            for (a, b), phase in zip(vec, phases):
                if phase == 0:
                    out.append((a, b))
                elif phase == 1:
                    out.append((-b, a))
                elif phase == 2:
                    out.append((-a, -b))
                else:
                    out.append((b, -a))
            vec = out
        elif kind == 'C':
            q, sign = gate[1:]
            out = []
            for x, (a, b) in enumerate(vec):
                c, d = vec[x ^ q]
                out.append((a - sign*b + c + sign*d,
                            b + sign*a + d - sign*c))
            vec = out
            den += 1
        else:
            raise AssertionError(gate)
        while den and all((a & 1) == (b & 1) == 0 for a, b in vec):
            vec = [(a // 2, b // 2) for a, b in vec]
            den -= 1
    return vec, den
