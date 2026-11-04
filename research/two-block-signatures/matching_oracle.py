"""Generic support screens using perfect matchings of determinants and cofactors.

Every integer bit position represents one support pattern. This module uses no
complementary-space incidence tests or constructive witness from the theorem.
"""
from itertools import permutations


def support_bits(variable_count):
    size = 1 << variable_count
    full = (1 << size)-1
    stripes = []
    for k in range(variable_count):
        span = 1 << k
        repeat = full // ((1 << (2*span))-1)
        stripes.append((repeat*((1 << span)-1)) << span)
    return full, stripes


def matching_screen(p, q, chart):
    n = p+q
    variable = {}
    fixed = set()
    for i in range(n):
        for j in range(n):
            if not chart or (i < p) != (j < p):
                variable[i,j] = len(variable)
            elif i == j:
                fixed.add((i,j))
    if len(variable) > 18:
        raise ValueError("explicit bitset census capped at eighteen variables")
    full, stripes = support_bits(len(variable))
    edges = [[full if (i,j) in fixed else stripes[variable[i,j]] if (i,j) in variable else 0
              for j in range(n)] for i in range(n)]
    det = 0
    cofactors = [[0]*n for _ in range(n)]
    for perm in permutations(range(n)):
        prefix = [full]
        for i,j in enumerate(perm):
            prefix.append(prefix[-1] & edges[i][j])
        det |= prefix[-1]
        suffix = full
        for i in reversed(range(n)):
            j = perm[i]
            cofactors[j][i] |= prefix[i] & suffix
            suffix &= edges[i][j]
    return det, edges, cofactors, len(variable)


def union(bits):
    result = 0
    for x in bits:
        result |= x
    return result


def census(p, q, chart=True):
    det, edges, inverse, variables = matching_screen(p, q, chart)
    states = {0: det}
    for j in range(p+q):
        sa = union(row[j] for row in edges[:p])
        sb = union(row[j] for row in edges[p:])
        ra = union(inverse[j][:p])
        rb = union(inverse[j][p:])
        source = (sa & ~sb, sb & ~sa, sa & sb)
        reader = (ra & ~rb, rb & ~ra, ra & rb)
        next_states = {}
        for s, src in enumerate(source, 1):
            for r, rd in enumerate(reader, 1):
                selector = src & rd
                digit = (4*s+r) << (4*j)
                for key, bits in states.items():
                    compatible = bits & selector
                    if compatible:
                        next_states[key+digit] = compatible
        states = next_states
    return dict(variables=variables, patterns=1 << variables, nonsingular=det.bit_count()), {
        key: bits.bit_count() for key,bits in states.items()}
