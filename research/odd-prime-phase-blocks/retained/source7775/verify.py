"""Check exact controls for two-prime alphabet descent.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from functools import cache
from hashlib import sha1, sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def divide(poly, divisor):
    work = list(poly)
    quotient = [0]*(len(work)-len(divisor)+1)
    for i in range(len(quotient)-1, -1, -1):
        factor = work[i+len(divisor)-1]
        quotient[i] = factor
        for j, value in enumerate(divisor):
            work[i+j] -= factor*value
    require(not any(work), 'exact cyclotomic division')
    return tuple(quotient)


@cache
def cyclotomic(order):
    poly = (-1,)+(0,)*(order-1)+(1,)
    for d in range(1, order):
        if order % d == 0:
            poly = divide(poly, cyclotomic(d))
    return poly


def roots(order):
    poly = cyclotomic(order)
    degree = len(poly)-1
    values = []
    row = (1,)+(0,)*(degree-1)
    for _ in range(order):
        values.append(row)
        shifted = (0,)+row
        row = tuple(shifted[i]-shifted[-1]*poly[i] for i in range(degree))
    require(row == values[0] and len(set(values)) == order, 'primitive root orbit')
    return values


def root_sum(exponents, basis):
    return tuple(sum(basis[e % len(basis)][i] for e in exponents) for i in range(len(basis[0])))


def legal_pattern(values, q):
    counts = sorted(Counter(values).values())
    return len(counts) == 1 or counts == [3, q]


def collision_checks():
    canonical = 0
    for q in (5, 7, 11, 13):
        for modulus in (3, 5, 9, 15, 25):
            for intersection in range(3):
                left = {0, 1, 2}
                right = set(range(intersection)) | set(range(3, 6-intersection))
                require(len(right) == 3 and len(left & right) == intersection, 'intersection representative')
                for t in range(1, modulus):
                    for u in range(1, modulus):
                        values = [(t*(i in left)-u*(i in right)) % modulus for i in range(q+3)]
                        require(not legal_pattern(values, q), 'distinct three-subsets accepted')
                        canonical += 1
    full = 0
    for q, modulus in ((5, 3), (5, 5), (7, 3), (7, 5)):
        subsets = list(combinations(range(q+3), 3))
        for left, right in combinations(subsets, 2):
            left, right = set(left), set(right)
            for t in range(1, modulus):
                for u in range(1, modulus):
                    values = [(t*(i in left)-u*(i in right)) % modulus for i in range(q+3)]
                    require(not legal_pattern(values, q), 'full subset-pair collision')
                    full += 1
    # Without the prime-size condition, disjoint triples can give counts 3 and 6.
    control = [(int(i < 3)+int(3 <= i < 6)) % 5 for i in range(9)]
    require(legal_pattern(control, 6), 'composite-size scope control')
    return {'canonical_intersection_cases': canonical, 'all_subset_pair_cases': full,
            'composite_q6_pattern_control': sorted(Counter(control).values())}


def check_gram(matrix, basis):
    n, m = len(matrix), len(matrix[0])
    for i in range(m):
        for j in range(m):
            actual = root_sum([row[j]-row[i] for row in matrix], basis)
            require(actual == ((n,)+(0,)*(len(basis[0])-1) if i == j else (0,)*len(basis[0])),
                    'exact cyclotomic Gram')
    return m*m


def dephase(matrix, modulus):
    return [[(v-row[0]-matrix[0][j]+matrix[0][0]) % modulus for j, v in enumerate(row)]
            for row in matrix]


def alphabet_case(q, a, b, attaining):
    modulus, base = 3**a*q**b, 3*q
    quotient = modulus//base
    basis = roots(modulus)
    lookup = {row: i for i, row in enumerate(basis)}
    normalized_triples = []
    for i, row in enumerate(basis):
        target = tuple(-x-y for x, y in zip(basis[0], row, strict=True))
        if target in lookup:
            normalized_triples.append((0, i, lookup[target]))
    expected = [(0, modulus//3, 2*modulus//3), (0, 2*modulus//3, modulus//3)]
    require(normalized_triples == expected, 'complete normalized three-root sums')
    line_pairs = 0
    for left in normalized_triples:
        for right in normalized_triples:
            value = root_sum([y-x for x, y in zip(left, right, strict=True)], basis)
            require(value == ((3,)+(0,)*(len(basis[0])-1) if left == right else (0,)*len(basis[0])),
                    'parallel or orthogonal Fourier lines')
            line_pairs += 1
    cycles3 = [tuple((shift+k*(modulus//3)) % modulus for k in range(3)) for shift in range(modulus//3)]
    cyclesq = [tuple((shift+k*(modulus//q)) % modulus for k in range(q)) for shift in range(modulus//q)]
    for cycle in cycles3+cyclesq:
        require(not any(root_sum(cycle, basis)), 'exact prime cycle')
    constant = mixed = 0
    for first in cycles3:
        for second in cyclesq:
            combined = first+second
            require(max(Counter(combined).values()) <= 2, 'cycle root multiplicity exceeds two')
            histogram = sorted(Counter(e % quotient for e in combined).values())
            require(histogram in ([q+3], [3, q]), 'higher-phase coset counts')
            constant += histogram == [q+3]
            mixed += histogram == [3, q]
    require(constant == modulus and constant+mixed == modulus*quotient, 'complete cycle-pair count')
    triple = [[(r*j*(modulus//3)+j) % modulus for j in range(3)] for r in range(3)]
    triple += [[r*j*(modulus//q) % modulus for j in range(3)] for r in range(q)]
    checks = check_gram(triple, basis)
    ratio = (triple[0][1]-triple[0][0]-triple[3][1]+triple[3][0]) % modulus
    require(ratio == 1, 'essential higher-phase cross ratio')
    if quotient > 1:
        require(any(e % quotient for row in dephase(triple, modulus) for e in row),
                'three-column nondescending example lost')
    lifted = None
    if q == 5:
        lifted = [[quotient*v for v in row] for row in attaining]
        checks += check_gram(lifted, basis)
        changed = [[(v+(r+1)**2+3*j*j+1) % modulus for j, v in enumerate(row)]
                   for r, row in enumerate(lifted)]
        checks += check_gram(changed, basis)
        require(dephase(changed, modulus) == lifted, 'exact row/column phase recovery')
        if quotient > 1:
            require(any((row[0]-changed[0][0]) % quotient for row in changed),
                    'column-only gauge control')
    return {'q': q, 'a': a, 'b': b, 'modulus': modulus, 'quotient_order': quotient,
            'cyclotomic_degree': len(basis[0]), 'prime_cycles': len(cycles3)+len(cyclesq),
            'cycle_pairs': constant+mixed, 'constant_coset_pairs': constant, 'mixed_coset_pairs': mixed,
            'normalized_three_root_sums': normalized_triples, 'Fourier_line_pairs': line_pairs,
            'sharp_three_column_example': triple, 'cross_ratio_exponent': ratio,
            'cannot_descend': quotient > 1, 'four_column_attainment': lifted,
            'exact_Gram_entries': checks}


def collect():
    pins = json.loads((ROOT/'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        raw = (ROOT/pin['retained']).read_bytes()
        require(sha256(raw).hexdigest() == pin['sha256'] and
                sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'source pin')
    source = ROOT/'retained/source7769'
    run = subprocess.run([sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
                          '-B', str(source/'verify.py')], capture_output=True, text=True, check=True, timeout=60)
    require('PASS_FIFTEENTH_ROOT_COLUMN_CAPACITY' in run.stdout, 'unchanged full base capacity')
    result = json.loads((source/'RESULT.json').read_text())
    require(result['exact_capacity'] == 4, 'source exact capacity')
    attaining = result['extension_graph']['attaining_matrix_rows']
    require(cyclotomic(15) == (1, -1, 0, 1, -1, 1, 0, -1, 1), 'source Phi15 convention')
    cases = [alphabet_case(q, a, b, attaining) for q in (5, 7) for a, b in ((1, 1), (2, 1), (1, 2), (2, 2))]
    return {'source_files': len(pins), 'quotient_collision_checks': collision_checks(),
            'alphabet_cases': cases, 'cycle_pairs_checked': sum(c['cycle_pairs'] for c in cases),
            'exact_Gram_entries': sum(c['exact_Gram_entries'] for c in cases),
            'universal_statement': 'q>=5 prime; a,b>=1; q+3 rows; at least four orthogonal columns descend to mu_(3q)',
            'eight_row_capacity': 'exactly four for every mu_(3^a*5^b), a,b>=1',
            'sharp_column_threshold': 'three-column examples do not descend when 3^a*q^b>3q'}


def main():
    actual = collect()
    require(json.loads(json.dumps(actual)) == json.loads((ROOT/'RESULT.json').read_text()), 'saved result mismatch')
    print('PASS_TWO_PRIME_ALPHABET_DESCENT')
    print('At least four orthogonal columns with q+3 rows descend from mu_(3^a*q^b) to mu_(3q)')
    print('Exact eight-row capacity four for all a,b>=1; three-column boundary is sharp')
    print('Exact quotient-pattern, prime-cycle, Fourier-line, cross-ratio and lifted-attainment checks pass')
    print('Unchanged complete fifteenth-root capacity and nested source checks pass')


if __name__ == '__main__':
    main()
