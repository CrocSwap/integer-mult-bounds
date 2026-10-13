#!/usr/bin/env python3
"""Reproduce the appendix using ordinary (not Boolean-quotient) polynomials.

Packed coefficient rows are a producer implementation separate from the
checker's tuple-set polynomial representation. Only standard library used.
"""
from collections import deque
from itertools import combinations_with_replacement
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASELINE = HERE.parents[1]/'turyn-profile-cnf'


def require(value, message):
    if not value:
        raise ValueError(message)


def encode():
    sources = json.loads((HERE/'SOURCES.json').read_text())
    for name, digest in sources['baseline_files'].items():
        require(hashlib.sha256((BASELINE/name).read_bytes()).hexdigest() == digest,
                'Pinned baseline mismatch: '+name)
    witness = json.loads((BASELINE/'WITNESS.json').read_text())
    coordinates = witness['coordinates']
    names = []
    labels = []
    for vertex in range(7, 24):
        row = [[] for _ in range(8)]
        for k in range(7):
            adjacent = all(sum(coordinates[vertex][8*b+i]*coordinates[k][8*b+i]
                               for i in range(8)) for b in range(3))
            if not adjacent:
                row[k] = [(len(names),)]
                names.append([vertex-7, k])
        row[7] = [()] + [m for polynomial in row[:7] for m in polynomial]
        labels.append(row)
    monomials = [m for degree in range(4)
                 for m in combinations_with_replacement(range(len(names)), degree)]
    column = {m: i for i, m in enumerate(monomials)}
    equations = []
    for a, b in witness['core_variable_edges']:
        packed = 0
        for k in range(8):
            for x in labels[a][k]:
                for y in labels[b][k]:
                    packed ^= 1 << column[tuple(sorted(x+y))]
        equations.append(packed)
    return witness, names, monomials, column, equations


def quadratic_minor(monomials, equations):
    support = sorted({m for row in equations for i, m in enumerate(monomials)
                      if len(m) == 2 and row >> i & 1})
    columns = {m: i for i, m in enumerate(monomials)}
    # Eliminate the transpose to select independent original columns.
    basis = {}
    selected = []
    for monomial in support:
        row = sum(((equation >> columns[monomial]) & 1) << i for i, equation in enumerate(equations))
        while row:
            pivot = row.bit_length()-1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                selected.append(list(monomial))
                break
    require(len(basis) == 57, 'Independent homogeneous quadratic parts')
    return {'status': 'INDEPENDENT_QUADRATIC_PARTS', 'rows': 57,
            'all_quadratic_monomials': len(support), 'pivot_monomials': selected,
            'rank': 57,
            'scope': 'No nonzero affine polynomial lies in the constant-linear-combination span of the 57 normalized edge equations.'}


def refutation(witness, names, monomials, column, equations):
    threshold = sum(len(m) <= 2 for m in monomials)
    basis = {}
    nodes = []
    queue = deque()

    def node(kind, **kwargs):
        nodes.append({'kind': kind, **kwargs})
        return len(nodes)-1

    def insert(row, source):
        used = [source]
        while row:
            pivot = row.bit_length()-1
            if pivot not in basis:
                if len(used) > 1:
                    source = node('xor', inputs=used)
                basis[pivot] = row, source
                if pivot < threshold:
                    queue.append((row, source))
                return source if row == 1 else None
            other, index = basis[pivot]
            row ^= other
            used.append(index)
        return None

    def certificate(final):
        used = set()
        pending = [final]
        while pending:
            i = pending.pop()
            if i in used:
                continue
            used.add(i)
            rule = nodes[i]
            if rule['kind'] == 'xor':
                pending.extend(rule['inputs'])
            if rule['kind'] == 'multiply':
                pending.append(rule['input'])
        keep = sorted(used)
        mapping = {old: new for new, old in enumerate(keep)}
        proof = []
        for old in keep:
            rule = nodes[old].copy()
            if rule['kind'] == 'xor':
                rule['inputs'] = [mapping[x] for x in rule['inputs']]
            if rule['kind'] == 'multiply':
                rule['input'] = mapping[rule['input']]
            proof.append(rule)
        return {'status': 'ORDINARY_CHAR2_PC_REFUTATION', 'degree_bound': 3,
                'variables': names, 'core_variable_edges': witness['core_variable_edges'],
                'steps': proof, 'final': mapping[final], 'full_matrix_rank': len(basis)}

    for i, equation in enumerate(equations):
        final = insert(equation, node('axiom', edge=i))
        if final is not None:
            return certificate(final)
    while queue:
        row, index = queue.popleft()
        terms = []
        remaining = row
        while remaining:
            bit = remaining & -remaining
            remaining -= bit
            terms.append(monomials[bit.bit_length()-1])
        for variable in range(len(names)):
            multiplied = 0
            for monomial in terms:
                multiplied ^= 1 << column[tuple(sorted(monomial+(variable,)))]
            final = insert(multiplied, node('multiply', input=index, variable=variable))
            if final is not None:
                return certificate(final)
    raise ValueError('Expected ordinary degree-three refutation was not found')


def build():
    witness, names, monomials, columns, equations = encode()
    return {'ORDINARY-PC-PROOF.json': refutation(witness, names, monomials, columns, equations),
            'QUADRATIC-RANK.json': quadratic_minor(monomials, equations)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in build().items():
        (args.output/name).write_text(json.dumps(data, indent=2)+'\n')
        print(name)


if __name__ == '__main__':
    main()
