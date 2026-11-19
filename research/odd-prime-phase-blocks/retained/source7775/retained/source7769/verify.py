"""Check the exact four-column capacity over fifteenth roots.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha1, sha256
from itertools import combinations, combinations_with_replacement, permutations, product
import json
from math import comb
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
SECOND = (0, 5, 10, 0, 3, 6, 9, 12)
PHI = (1, -1, 0, 1, -1, 1, 0, -1, 1)


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def residue(exponents):
    coefficients = [0] * 15
    for exponent in exponents:
        coefficients[exponent % 15] += 1
    for power in range(14, 7, -1):
        leading = coefficients[power]
        for j, value in enumerate(PHI):
            coefficients[power - 8 + j] -= leading * value
    return tuple(coefficients[:8])


def tensor_residue(exponents):
    result = [0] * 8
    for exponent in exponents:
        x, y = 2 * exponent % 3, 2 * exponent % 5
        xs = [(x, 1)] if x < 2 else [(0, -1), (1, -1)]
        ys = [(y, 1)] if y < 4 else [(j, -1) for j in range(4)]
        for (i, a), (j, b) in product(xs, ys):
            result[4 * i + j] += a * b
    return tuple(result)


def multiset_words(counts, prefix=()):
    if not any(counts):
        yield prefix
        return
    for value, count in enumerate(counts):
        if count:
            counts[value] -= 1
            yield from multiset_words(counts, prefix + (value,))
            counts[value] += 1


def source_check():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        data = (ROOT / pin['retained']).read_bytes()
        require(sha256(data).hexdigest() == pin['sha256'], 'source SHA256')
        require(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == pin['git_blob'], 'source Git blob')
    args = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
            '-B', str(ROOT / 'retained/source7762/verify.py')]
    output = subprocess.run(args, check=True, capture_output=True, text=True, timeout=60)
    require('PASS_MIXED_CYCLE_COLUMN_OBSTRUCTION' in output.stdout, 'source replay')
    return len(pins)


def enumerate_columns():
    zero = (0,) * 8
    supports = []
    examined = 0
    for tail in combinations_with_replacement(range(15), 7):
        examined += 1
        row = (0,) + tail
        if residue(row) == zero:
            require(tensor_residue(row) == zero, 'second basis on zero support')
            supports.append(tuple(sorted(row)))
    require(examined == comb(21, 7) == 116280, 'tail multiset coverage')
    first = set()
    for row in supports:
        counts = [row.count(value) for value in range(15)]
        counts[0] -= 1
        first.update((0,) + word for word in multiset_words(counts))
    cycles = {tuple(sorted([(a + 5 * i) % 15 for i in range(3)]
                           + [(b + 3 * j) % 15 for j in range(5)]))
              for a in range(5) for b in range(3)}
    shifted = {tuple(sorted((x + shift) % 15 for x in SECOND)) for shift in range(15)}
    require(cycles == shifted and len(cycles) == 15, 'pair normalization orbit')
    second = set()
    for row in cycles:
        if 0 in row:
            tail = list(row)
            tail.remove(0)
            second.update((0,) + word for word in permutations(tail))
    require(first == second and len(first) == 20160, 'independent candidate enumeration')
    valid = []
    for word in sorted(first):
        differences = [(a - b) % 15 for a, b in zip(word, SECOND, strict=True)]
        direct = residue(differences) == zero
        require(direct == (tensor_residue(differences) == zero), 'two exact pairing bases')
        require(direct == (tuple(sorted(differences)) in cycles), 'cycle pairing check')
        if direct:
            valid.append(word)
    require(len(valid) == 95, 'third-column count')
    return valid, {'tail_multisets_examined': examined, 'zero_supports': supports,
                   'normalized_candidates': len(first), 'pair_normalization_orbit': sorted(shifted)}


def graph_check(vertices):
    zero = (0,) * 8
    adjacency = [set() for _ in vertices]
    edges, wrong_edges = [], []
    for i, j in combinations(range(len(vertices)), 2):
        differences = [a - b for a, b in zip(vertices[i], vertices[j], strict=True)]
        direct = residue(differences) == zero
        require(direct == (tensor_residue(differences) == zero), 'graph independent basis')
        if direct:
            edges.append((i, j))
            adjacency[i].add(j)
            adjacency[j].add(i)
        if residue(a + b for a, b in zip(vertices[i], vertices[j], strict=True)) == zero:
            wrong_edges.append((i, j))
    require(edges != wrong_edges, 'omitted conjugation control')
    require(len(edges) == 12, 'edge count')
    components, remaining = [], set(range(len(vertices)))
    while remaining:
        found, stack = set(), [min(remaining)]
        while stack:
            v = stack.pop()
            if v not in found:
                found.add(v)
                stack.extend(adjacency[v] - found)
        remaining -= found
        components.append(sorted(found))
    sizes = Counter(map(len, components))
    require(sizes == {1: 83, 6: 2}, 'component sizes')
    for component in components:
        if len(component) > 1:
            require(all(len(adjacency[v]) == 2 for v in component), 'six-cycle degrees')
    triangles = [(i, j, k) for i, j, k in combinations(range(len(vertices)), 3)
                 if j in adjacency[i] and k in adjacency[i] and k in adjacency[j]]
    require(not triangles, 'complete triangle enumeration')
    masks = [sum(1 << j for j in neighbors) for neighbors in adjacency]
    require(all(masks[i] & masks[j] == 0 for i, j in edges), 'independent common-neighbor check')
    for word in vertices:
        require(residue(a - a for a in word) == (8,) + (0,) * 7, 'self-column norm')
    columns = [(0,) * 8, SECOND, vertices[edges[0][0]], vertices[edges[0][1]]]
    for i, j in product(range(4), repeat=2):
        difference = [a - b for a, b in zip(columns[i], columns[j], strict=True)]
        require(residue(difference) == ((8,) + (0,) * 7 if i == j else zero), 'attaining Gram')
        require((tensor_residue(difference) == zero) == (i != j), 'attaining tensor Gram')
    mutations = 0
    for column, row, change in product(range(4), range(8), range(1, 15)):
        altered = list(columns[column])
        altered[row] = (altered[row] + change) % 15
        other = columns[(column + 1) % 4]
        require(residue(a - b for a, b in zip(altered, other, strict=True)) != zero,
                'one-entry change escaped Gram check')
        mutations += 1
    return {'vertices': vertices, 'edges': edges, 'components': components,
            'pair_checks': comb(len(vertices), 2), 'triple_checks': comb(len(vertices), 3),
            'maximal_three_column_sets': 83, 'maximal_four_column_sets': 12,
            'attaining_matrix_rows': list(zip(*columns, strict=True)),
            'single_entry_mutations_rejected': mutations,
            'wrong_bilinear_edge_count': len(wrong_edges)}


def collect():
    count = source_check()
    vertices, enumeration = enumerate_columns()
    return {'source_files': count, 'exact_capacity': 4,
            'enumeration': enumeration, 'extension_graph': graph_check(vertices)}


def main():
    actual = collect()
    expected = json.loads((ROOT / 'RESULT.json').read_text())
    require(json.loads(json.dumps(actual)) == expected, 'saved certificate mismatch')
    print('PASS_FIFTEENTH_ROOT_COLUMN_CAPACITY')
    print('Exact maximum: four orthogonal columns in eight rows over fifteenth roots')
    print('116280 tail multisets; two enumerations of 20160 normalized columns; 95 extensions')
    print('4465 pairs; 138415 triples; graph = two six-cycles and 83 isolated vertices')
    print('Twelve normalized four-column sets; exact attaining Gram; 448 changed entries reject')


if __name__ == '__main__':
    main()
