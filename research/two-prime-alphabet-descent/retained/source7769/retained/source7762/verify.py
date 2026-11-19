"""Check the mixed-cycle column obstruction with exact integer arithmetic.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
from itertools import combinations, combinations_with_replacement, product
import json
from math import comb, isqrt
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ArithmeticError(message)


def third_sum(exponents):
    counts = [0, 0, 0]
    for exponent in exponents:
        counts[exponent % 3] += 1
    return counts[0] - counts[2], counts[1] - counts[2]


def edge_word(n, edge):
    a, b = edge
    return tuple(1 if i == a else 2 if i == b else 0 for i in range(n))


def compatible(a, b):
    return a[0] == b[0] or a[1] == b[1] or a == b[::-1]


def gram_determinant(n, q, phase):
    twice_real = 2 if phase % 3 == 0 else -1
    return n ** 3 - 3 * n * q ** 2 + q ** 3 * twice_real


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def multiply(a, b):
    x, y = a
    u, v = b
    return x * u - y * v, x * v + y * u - y * v


def conjugate(a):
    return a[0] - a[1], -a[1]


def matrix_gram(matrix, use_conjugate=True):
    return [[sum_pair(multiply(a, conjugate(b) if use_conjugate else b)
                      for a, b in zip(left, right)) for right in matrix]
            for left in matrix]


def sum_pair(values):
    result = (0, 0)
    for value in values:
        result = add(result, value)
    return result


def check_spectral_identity():
    qmatrix = [[1, 2, 3], [2, 1, 4], [3, 4, 1]]
    square = [[sum(qmatrix[i][k] * qmatrix[k][j] for k in range(3))
               for j in range(3)] for i in range(3)]
    expected = [[(square[i][j] - 3 * qmatrix[i][j] + 3 * (i == j), 0)
                 for j in range(3)] for i in range(3)]
    for phase in ((0, 1), (-1, -1)):
        shift = add(phase, (-1, 0))
        matrix = [[add((qmatrix[i][j], 0), shift if i == j else (0, 0))
                   for j in range(3)] for i in range(3)]
        require(matrix_gram(matrix) == expected, 'Hermitian spectral identity')
        require(matrix_gram(matrix, False) != expected, 'conjugation fault')
        wrong = [[add((qmatrix[i][j], 0), phase if i == j else (0, 0))
                  for j in range(3)] for i in range(3)]
        require(matrix_gram(wrong) != expected, 'diagonal shift fault')
    wrong_coefficient = [[(square[i][j] - qmatrix[i][j] + 3 * (i == j), 0)
                          for j in range(3)] for i in range(3)]
    require(expected != wrong_coefficient, 'linear coefficient fault')
    return {'orientations': 2, 'entries_per_orientation': 9,
            'faults': ['conjugation', 'diagonal shift', 'linear coefficient']}


def maximal_cliques(adjacency):
    result = []

    def visit(chosen, possible, excluded):
        if not possible and not excluded:
            result.append(tuple(chosen))
            return
        union = possible | excluded
        pivot = max(union, key=lambda i: len(possible & adjacency[i]))
        for vertex in sorted(possible - adjacency[pivot]):
            visit(chosen + [vertex], possible & adjacency[vertex],
                  excluded & adjacency[vertex])
            possible.remove(vertex)
            excluded.add(vertex)

    visit([], set(range(len(adjacency))), set())
    return sorted(tuple(sorted(row)) for row in result)


def check_edges():
    n = 8
    words = {word for word in product(range(3), repeat=n)
             if third_sum(word) == (5, 0)}
    edges = list((a, b) for a in range(n) for b in range(n) if a != b)
    require(words == {edge_word(n, edge) for edge in edges}, 'word inventory')
    adjacency = [set() for _ in edges]
    pair_checks = 0
    for i, j in combinations(range(len(edges)), 2):
        left, right = edge_word(n, edges[i]), edge_word(n, edges[j])
        actual = third_sum(b - a for a, b in zip(left, right)) == (5, 0)
        require(actual == compatible(edges[i], edges[j]), 'edge compatibility')
        if actual:
            adjacency[i].add(j)
            adjacency[j].add(i)
        pair_checks += 1
    cliques = maximal_cliques(adjacency)
    stars = {tuple(i for i, edge in enumerate(edges) if edge[axis] == centre)
             for axis in range(2) for centre in range(n)}
    reverse = {tuple(sorted((edges.index((a, b)), edges.index((b, a)))))
               for a, b in combinations(range(n), 2)}
    require(set(cliques) == stars | reverse, 'maximal clique classification')
    six = {sub for star in stars for sub in combinations(star, 6)}
    direct_six = set()

    def enumerate_six(chosen, possible):
        if len(chosen) == 6:
            direct_six.add(tuple(chosen))
            return
        while possible:
            vertex = min(possible)
            possible.remove(vertex)
            enumerate_six(chosen + [vertex], possible & adjacency[vertex])

    enumerate_six([], set(range(len(edges))))
    require(six == direct_six and len(six) == 112, 'six-edge coverage')
    records = []
    for clique in sorted(six):
        columns = [(0,) * n] + [edge_word(n, edges[i]) for i in clique]
        unused = [r for r in range(n) if all(col[r] == 0 for col in columns)]
        require(len(unused) == 1, 'unique unused row')
        reference = unused[0]
        residues = []
        for r in range(n):
            residue = (1, 0) if r == reference else tuple(
                -x % 5 for x in third_sum(col[r] for col in columns))
            roots = [tuple(x % 5 for x in third_sum([e])) for e in range(3)]
            negatives = [tuple(-x % 5 for x in root) for root in roots]
            require(residue in roots and residue not in negatives, 'completion sign')
            residues.append(roots.index(residue))
        records.append({'edges': [list(edges[i]) for i in clique], 'reference': reference,
                        'completion_mod_five': residues})
    return {'ternary_words_examined': 3 ** n, 'edge_words': len(edges),
            'pair_checks': pair_checks, 'maximal_cliques': len(cliques),
            'stars': len(stars), 'reverse_pairs': len(reverse),
            'partial_configurations': records}


def check_root_sums():
    # Phi_15(X) = X^8-X^7+X^5-X^4+X^3-X+1.
    phi = (1, -1, 0, 1, -1, 1, 0, -1)
    powers = []
    current = [1] + [0] * 7
    for _ in range(15):
        powers.append(tuple(current))
        leading = current[-1]
        current = [0] + current[:-1]
        current = [a - leading * b for a, b in zip(current, phi)]
    require(current == [1] + [0] * 7, 'fifteenth power')
    expected = {tuple(sorted(tuple((a + 5 * i) % 15 for i in range(3))
                             + tuple((b + 3 * j) % 15 for j in range(5))))
                for a in range(5) for b in range(3)}
    actual = set()
    examined = 0
    for terms in combinations_with_replacement(range(15), 8):
        examined += 1
        total = tuple(sum(powers[e][i] for e in terms) for i in range(8))
        if total == (0,) * 8:
            actual.add(terms)
    require(actual == expected, 'complete eight-term vanishing sums')
    require(examined == comb(22, 8), 'multiset coverage')
    for terms in actual:
        projected = third_sum(terms)
        require(projected in ((5, 0), (0, 5), (-5, -5)), 'projected mixed sum')
    return {'multisets_examined': examined, 'vanishing_multisets': [list(row) for row in sorted(actual)]}


def check_general_steps():
    primes = [q for q in range(5, 102) if all(q % d for d in range(2, isqrt(q) + 1))]
    phase_records = []
    sign_rows = 0
    for q in primes:
        n = q + 3
        solutions = [(r, s) for r in range(n // 3 + 1) for s in range(n // q + 1)
                     if 3 * r + q * s == n]
        require(solutions == [(1, 1)], 'mixed cycle count')
        balanced = 0
        for a, b, c in product(range(3), repeat=3):
            phase = (a + c - b) % 3
            determinant = gram_determinant(n, q, phase)
            require((determinant >= 0) == (phase == 0), 'Gram phase rigidity')
            balanced += phase == 0
        require(balanced == 9, 'balanced triangle count')
        roots = [tuple(x % q for x in third_sum([e])) for e in range(3)]
        require(not set(roots) & {tuple(-x % q for x in root) for root in roots},
                'sign cosets')
        for orientation in (1, 2):
            columns = [(0,) * n] + [tuple(orientation if r == 0 else
                        -orientation % 3 if r == j else 0 for r in range(n))
                        for j in range(1, n - 1)]
            for r in range(n - 1):
                residue = tuple(-x % q for x in third_sum(col[r] for col in columns))
                require(residue in roots, 'general completion residue')
                sign_rows += 1
        discriminant = 9 + 4 * q
        require(discriminant % 8 == 5 and isqrt(discriminant) ** 2 != discriminant,
                'spectral irrationality')
        for multiplicity in range(n + 1):
            require((2 * multiplicity - n) ** 2 * discriminant != n ** 2,
                    'trace multiplicity contradiction')
        phase_records.append({'q': q, 'rows': n, 'balanced_determinant':
                              gram_determinant(n, q, 0), 'unbalanced_determinant':
                              gram_determinant(n, q, 1), 'discriminant': discriminant})
    # A reverse pair passes pair compatibility but cannot form a three-edge star.
    require(compatible((0, 1), (1, 0)), 'reverse-pair positive control')
    require(not any(compatible((0, 1), edge) and compatible((1, 0), edge)
                    for edge in product(range(8), repeat=2)
                    if edge[0] != edge[1] and edge not in ((0, 1), (1, 0))),
            'reverse-pair extension control')
    require(gram_determinant(8, 5, 1) == -213, 'unbalanced phase control')
    require(third_sum([0] * 6 + [1, 2]) == (5, 0), 'projection is not orthogonal')
    require((1, 0) != tuple(-x % 5 for x in (1, 0)), 'negative sign control')
    require(gram_determinant(6, 3, 1) > 0, 'excluded q=3 phase boundary')
    return {'primes': phase_records, 'triangle_cases': 27 * len(primes),
            'sign_rows': sign_rows,
            'controls': ['reverse pair', 'nontrivial triangle phase',
                         'nonorthogonal projection', 'opposite completion sign',
                         'excluded q=3 boundary'],
            'spectral_identity': check_spectral_identity()}


def sources():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        data = (ROOT / pin['retained']).read_bytes()
        require(sha256(data).hexdigest() == pin['sha256'], 'retained SHA256')
        require(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == pin['git_blob'], 'retained Git blob')
    command = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
               '-B', str(ROOT / 'retained/two-prime/verify.py')]
    replay = subprocess.run(command, check=True, text=True, capture_output=True, timeout=30)
    require('PASS_TWO_PRIME_COLUMN_COMPLETION' in replay.stdout, 'source replay')
    return len(pins)


def collect():
    return {'source_files': sources(), 'root_sums': check_root_sums(),
            'eight_row_projection': check_edges(), 'general_steps': check_general_steps()}


def main():
    actual = collect()
    expected = json.loads((ROOT / 'RESULT.json').read_text())
    require(actual == expected, 'saved certificate mismatch')
    print('PASS_MIXED_CYCLE_COLUMN_OBSTRUCTION')
    print('319770 root multisets; 15 vanishing sums; 6561 ternary words; 1540 edge pairs')
    print('44 maximal cliques; all 112 six-edge configurations; exact sign and trace controls')
    print('No (q+3)-by-(q+2) input over roots of order 3q^b, q prime >=5: written proof')


if __name__ == '__main__':
    main()
