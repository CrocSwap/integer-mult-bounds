"""Exact weighted-path certificates; no numerical solver is used here.

See PROOF.md for the determinant argument and its formal-group-algebra scope.
Apache-2.0; substantial OpenAI Codex assistance; see NOTICE.md.
"""
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import permutations, product

import dense
from model import Engine, FREE, generic_paths


def require(condition, message):
    if not condition:
        raise ValueError(message)


def split_layers(program):
    stages = [[[] for _ in range(3)]]
    for gate in program:
        if gate[0] == 'mix3':
            stages.append([[] for _ in range(3)])
        else:
            op = ('C', gate[2], 0) if gate[0] == 'paid' else FREE[gate[2]]
            stages[-1][gate[1]].append(op)
    require(len(stages) >= 2, 'At least one scalar block is required')
    return stages


@lru_cache(maxsize=4096)
def matrix_signature(matrix):
    """Read the six conjugated Paulis from G P G*, with exact Gaussian ints.

    Unlike model.py, this uses no Clifford tableau transition formulas.
    Unlike dense.signature, it does not search 256 possible Paulis.
    """
    e, re, im = matrix
    adjoint = dense.normalize(e, [re[8*c+r] for r in range(8) for c in range(8)],
                              [-im[8*c+r] for r in range(8) for c in range(8)])
    require(dense.multiply(matrix, adjoint) == dense.identity(), 'Nonunitary path')
    answer = []
    for generator in (1, 2, 4, 8, 16, 32):
        p = dense.multiply(dense.multiply(matrix, dense.pauli(generator)), adjoint)
        exponent, real, imag = p
        require(exponent == 0, 'Conjugate is not an integral Pauli')
        rows = [r for r in range(8) if real[8*r] or imag[8*r]]
        require(len(rows) == 1, 'Conjugate is not monomial')
        x = rows[0]
        phases = ((1, 0), (0, 1), (-1, 0), (0, -1))
        pair = real[8*x], imag[8*x]
        require(pair in phases, 'Invalid Pauli phase')
        phase = phases.index(pair)
        z = 0
        for bit in range(3):
            c = 1 << bit
            entry = real[8*(c ^ x)+c], imag[8*(c ^ x)+c]
            if entry == (-pair[0], -pair[1]):
                z |= c
            else:
                require(entry == pair, 'Invalid Pauli character')
        value = x | (z << 3) | (phase << 6)
        require(dense.pauli(value) == p, 'Full Pauli reconstruction mismatch')
        answer.append(value)
    return tuple(answer)


def direct_records(program):
    """Independently enumerate full paths and group by exact dense matrices."""
    stages = split_layers(program)
    matrices = []
    for stage in stages:
        layer = []
        for operations in stage:
            a = dense.identity()
            for op in operations:
                a = dense.multiply(dense.operator(op), a, True)
            layer.append(a)
        matrices.append(layer)
    groups = defaultdict(list)
    for output, column in product(range(3), repeat=2):
        for path in product(range(3), repeat=len(stages)-2):
            a = matrices[0][column]
            for k, role in enumerate(path, 1):
                a = dense.multiply(matrices[k][role], a, True)
            a = dense.multiply(matrices[-1][output], a, True)
            groups[output, column, a].append(path)
    records = []
    signatures = {}
    for (output, column, matrix), paths in groups.items():
        sig = matrix_signature(matrix)
        # Matrix equality modulo the four central phases must match tableaus.
        if sig in signatures:
            require(signatures[sig] == matrix, 'Projective grouping mismatch')
        signatures[sig] = matrix
        counts = [sum(bool(matrix[1][8*r+c] or matrix[2][8*r+c])
                      for r in range(8)) for c in range(8)]
        require(len(set(counts)) == 1 and counts[0] in (1, 2, 4, 8),
                'Unexpected dense Fourier support')
        records.append({'output': output, 'column': column,
                        'group': sig, 'rank': counts[0].bit_length()-1,
                        'frame': dense.independent_frame(sig),
                        'paths': sorted(paths)})
    return records, len(stages)-1


def symbolic_records(program):
    """Extract paths through the inherited symbolic polynomial engine."""
    ring = Engine()
    rows, blocks = generic_paths(ring, program, 3)
    records = []
    for output, row in enumerate(rows):
        for key, poly in row.items():
            column = key & 3
            frame, rank = ring.frame_info(key >> 2)
            paths = []
            for mask, coefficient in poly.items():
                require(coefficient == 1, 'Unexpected path multiplicity')
                edges = []
                require(mask >> (9*blocks) == 0, 'Out-of-range path bit')
                for k in range(blocks):
                    entries = [i for i in range(9) if mask >> (9*k+i) & 1]
                    require(len(entries) == 1, 'Path must select one entry per block')
                    edges.append(divmod(entries[0], 3))
                require(edges[0][1] == column and edges[-1][0] == output,
                        'Wrong path endpoints')
                require(all(edges[k][0] == edges[k+1][1] for k in range(blocks-1)),
                        'Disconnected path')
                paths.append(tuple(edge[0] for edge in edges[:-1]))
            records.append({'output': output, 'column': column,
                            'group': ring.groups[key >> 2], 'rank': rank,
                            'frame': frame, 'paths': sorted(paths)})
    return records, blocks


def canonical(records):
    return sorted((r['output'], r['column'], r['group'], r['rank'], r['frame'], r['paths'])
                  for r in records)


def targets(records):
    return [sorted({r['frame'] for r in records if r['column'] == j and r['rank'] == 3})
            for j in range(3)]


def allowed(record, frames):
    return record['rank'] == 3 and (frames is None or
                                   record['frame'] == frames[record['column']])


def check(records, blocks, vector, frames=None):
    """Check the sufficient obstruction hypotheses over exact rationals."""
    require(len(vector) == 3*(blocks-1)+6, 'Wrong certificate dimension')
    require(all(type(x) is int or isinstance(x, Fraction) for x in vector),
            'Weights must be exact integers or Fractions')
    require(frames is None or len(frames) == 3, 'Wrong frame dimension')
    nw = 3*(blocks-1)
    weights, output, source = vector[:nw], vector[nw:nw+3], vector[nw+3:]
    gap = sum(output)+sum(source)-sum(weights)
    require(gap > 0, 'Nonpositive determinant valuation gap')
    for record in records:
        degrees = [sum(weights[3*k+role] for k, role in enumerate(path))
                   for path in record['paths']]
        require(degrees, 'Empty coefficient class')
        if allowed(record, frames):
            require(min(degrees) >= output[record['output']]+source[record['column']],
                    'Allowed path lies below endpoint valuation')
        else:
            require(len(set(degrees)) == 1,
                    'Forbidden coefficient has heterogeneous path weights')
    return gap


def structural_obstruction(records, frames):
    """Zero-weight special case: the allowed entry graph has no matching."""
    edges = {(r['output'], r['column']) for r in records if allowed(r, frames)}
    return not any(all((i, p[i]) in edges for i in range(3))
                   for p in permutations(range(3)))
