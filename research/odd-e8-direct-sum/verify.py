"""Check an odd direct-sum E8 fitting family and its decoder tariff.

The finite checks certify the base data and stated tensor identities.
The price screen omits a native producer. It does not certify kappa.
Prepared for Ali Romman with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import json
from decimal import Decimal, localcontext
import argparse

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / 'research/coded-native-caller/NORMALIZERS.json'
SOURCE_HASH = 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da'


def need(value, message):
    if not value:
        raise ValueError(message)


def basis(rows):
    pivots = {}
    for value in rows:
        while value:
            key = value.bit_length() - 1
            if key in pivots:
                value ^= pivots[key]
            else:
                pivots[key] = value
                break
    return list(pivots.values())


def dot(x, y):
    return (x & y).bit_count() % 2


def gram_rank(left, right):
    return len(basis(sum(dot(x, y) << j for j, y in enumerate(right))
                     for x in left))


def cartesian_span(parts):
    first = sum(part[0] << (9 * i) for i, part in enumerate(parts))
    return basis([first] + [(x ^ part[0]) << (9 * i)
                            for i, part in enumerate(parts) for x in part[1:]])


def solve(matrix, values):
    rows = [[F(x) for x in row] + [F(value)]
            for row, value in zip(matrix, values)]
    n = len(rows)
    for j in range(n):
        pivot = next(i for i in range(j, n) if rows[i][j])
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [x / scale for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[j])]
    return [row[-1] for row in rows]


def coefficients(k):
    first = (k + 1) // 2
    # For e equal coordinates, all k-e other coordinates must use C.
    # Every odd e<k must vanish. The e=k value must be one.
    equations = [[comb(e, j - (k-e)) if 0 <= j-(k-e) <= e else 0
                  for j in range(first, k+1)] for e in range(1, k+1, 2)]
    values = [0] * (len(equations)-1) + [1]
    result = dict(zip(range(first, k+1), solve(equations, values)))
    closed = {j: F((-1)**(j-first)*comb(j-1, first-1), 2**(j-1))
              for j in range(first, k+1)}
    need(result == closed, 'The majority coefficient formula failed')
    need(all(x.denominator & (x.denominator-1) == 0 for x in result.values()),
         'The scalar coefficients must be dyadic')
    return result


def geometry(data):
    labels = [p['q'] for p in data['ports']]
    columns = data['mode_columns']
    n, rank = len(labels), len(columns)
    need((n, rank) == (112, 8), 'The base shape changed')
    need(len(set(labels)) == n and all(dot(q, q) == 1 for q in labels),
         'The base labels must be distinct odd vectors')
    need(len(basis(labels)) == 9, 'The base label span must have dimension nine')
    need(len(basis(q ^ labels[0] for q in labels)) == 8,
         'The base affine span must have dimension eight')
    gram = [[sum(columns[a][i] * columns[a][j] for a in range(rank))
             for j in range(n)] for i in range(n)]
    need(all(gram[i][i] == 4 for i in range(n)), 'The root norms changed')
    need(all(sum(columns[a][i] * columns[b][i] for i in range(n)) == 56*(a == b)
             for a in range(rank) for b in range(rank)), 'The tight-frame identity failed')
    need(all(not gram[i][j] for i in range(n) for j in range(n)
             if i != j and dot(labels[i], labels[j])), 'The base fitting mask failed')
    supports = [[labels[i] for i in range(n) if column[i]] for column in columns]
    profiles = []
    for support in supports:
        full = basis(support)
        even = basis(x ^ support[0] for x in support)
        need((len(full), gram_rank(full, full), len(even), gram_rank(even, even)) == (8, 8, 7, 6),
             'The feature support contract failed')
        radicals = [x for x in range(1, 512)
                    if not any(dot(x, y) for y in even) and len(basis(full + [x])) == 8]
        need(len(radicals) == 1 and dot(radicals[0], support[0]) == 1,
             'The feature even-space radical contract failed')
        profiles.append({'support_size': len(support), 'radical': radicals[0]})
    # Verify the product-support formula directly on every feature pair,
    # every inactive fixed label, and every feature triple.
    pair_profiles = Counter()
    for a, b, q in product(range(8), range(8), labels):
        span = cartesian_span([supports[a], supports[b], [q]])
        pair_profiles[(len(span), gram_rank(span, span))] += 1
    triple_profiles = Counter()
    for a, b, c in product(range(8), repeat=3):
        span = cartesian_span([supports[a], supports[b], supports[c]])
        triple_profiles[(len(span), gram_rank(span, span))] += 1
    need(pair_profiles == {(15, 14): 7168}, 'The two-feature tariff changed')
    need(triple_profiles == {(22, 20): 512}, 'The three-feature tariff changed')
    full_product = cartesian_span([labels]*3)
    need((len(full_product), gram_rank(full_product, full_product)) == (25, 25),
         'The full odd product is not nondegenerate')
    return {'base_entries': n*n, 'feature_supports': profiles,
            'pair_support_checks': dict((str(k), v) for k, v in pair_profiles.items()),
            'triple_support_checks': dict((str(k), v) for k, v in triple_profiles.items()),
            'triple_ambient_rank': 25}


def check_mask(k, coeff):
    equal_values = {}
    for e in range(k+1):
        value = sum(a * comb(e, j-(k-e)) for j, a in coeff.items()
                    if 0 <= j-(k-e) <= e)
        equal_values[e] = value
        if e % 2:
            need(value == int(e == k), 'An odd overlap violates the fitting mask')
    return equal_values


def family(k):
    coeff = coefficients(k)
    equal_values = check_mask(k, coeff)
    eigenvalues = {}
    rank = 0
    for active in range(k+1):
        value = sum(a * comb(active, j) * 14**j
                    for j, a in coeff.items() if j <= active)
        eigenvalues[active] = value
        if value:
            rank += comb(k, active) * 8**active * 104**(k-active)
    terms = {j: comb(k, j)*8**j*112**(k-j) for j, a in coeff.items() if a}
    tariff = {6*j+2: count for j, count in terms.items()}
    source_widths = {7*j+1: count for j, count in terms.items()}
    mass = sum(r*n for r, n in tariff.items())
    return {'factors': k, 'ports': 112**k, 'ambient_rank': 8*k+1,
            'scalar_coefficients': {j: str(a) for j, a in coeff.items()},
            'equal_coordinate_values': {e: str(a) for e, a in equal_values.items()},
            'eigenvalues': {e: str(a) for e, a in eigenvalues.items()},
            'fitting_rank': rank, 'factor_terms': sum(terms.values()),
            'pairing_tariff': tariff, 'source_widths': source_widths,
            'pairing_mass': mass, 'pairing_mass_per_port': str(F(mass, 112**k))}


def core(data):
    labels = [p['q'] for p in data['ports']]
    roots = list(zip(*data['mode_columns']))
    cubes = {}
    for index, root in enumerate(roots):
        support = tuple(i for i, x in enumerate(root) if x)
        cubes.setdefault(support, []).append(index)
    need(len(cubes) == 14, 'The cube count changed')
    records = []
    for support, indices in cubes.items():
        need(len(indices) == 8, 'A cube must have eight ports')
        parity, codes = [], []
        for i in indices:
            orientation = roots[i][support[0]]
            code = sum((roots[i][j]*orientation < 0) << b
                       for b, j in enumerate(support[1:]))
            codes.append(code)
            parity.append(code.bit_count() % 2)
        need(set(codes) == set(range(8)), 'The cube sign patterns changed')
        for a, i in enumerate(indices):
            for b, j in enumerate(indices):
                need(dot(labels[i], labels[j]) == int(parity[a] == parity[b]),
                     'The literal parity pairing failed')
                gram = sum(x*y for x,y in zip(roots[i], roots[j]))
                sign = roots[i][support[0]]*roots[j][support[0]]
                need(gram == sign*(4-2*(codes[a]^codes[b]).bit_count()),
                     'The literal cube Gram matrix failed')
        parts = [[labels[i] for i,p in zip(indices,parity) if p == b] for b in (0,1)]
        need(all(len(basis(part)) == 3 for part in parts), 'A parity span must have dimension three')
        need(all(len(basis(x^part[0] for x in part)) == 2 for part in parts),
             'A parity affine span must have dimension two')
        records.append(parts)
    # K0 is stored after multiplication by two.
    K0 = [[0 if i == j else (i^j).bit_count()-2 for j in range(8)] for i in range(8)]
    need(all(sum(K0[i][t]*K0[t][j] for t in range(8)) == 4*(i == j)
             for i in range(8) for j in range(8)), 'The cube core is not an involution')
    polynomial = {1:F(1,2), 2:F(1,2), 4:F(1,2), 7:F(-1,2)}
    square = Counter()
    for a,x in polynomial.items():
        for b,y in polynomial.items():
            square[a^b] += x*y
    need({m:v for m,v in square.items() if v} == {0:F(1)}, 'The triple core is not an involution')
    # Check all 2,744 product cubes without a dense 512-square matrix.
    checked = 0
    for blocks in product(records, repeat=3):
        spaces = []
        for wanted in (0,1):
            generators = []
            for bits in product((0,1), repeat=3):
                if sum(bits)%2 == wanted:
                    generators += cartesian_span([blocks[i][bits[i]] for i in range(3)])
            spaces.append(basis(generators))
        need([len(x) for x in spaces] == [9,9], 'A product parity span has the wrong dimension')
        need(gram_rank(spaces[0], spaces[1]) == 0, 'Opposite product parities must be orthogonal')
        checked += 1
    return {'base_cubes':14, 'product_cubes':checked, 'ports_per_product_cube':512,
            'opposite_parity_span_dimensions':[9,9], 'opposite_pairing_rank':0,
            'core_polynomial':{m:str(v) for m,v in polynomial.items()},
            'proposed_source_children':[8,15,1],
            'proposed_target_children':[15]+[1]*9,
            'physical_program_emitted':False}


def power_interval(rank):
    """Enclose rank^(1-31/10000) with an integer power check."""
    if rank == 1:
        return F(1), F(1)
    unit = 10**24
    with localcontext() as ctx:
        ctx.prec = 70
        lower = int((Decimal(rank).ln()*Decimal(31)/10000).exp()*unit)
    need(lower**10000 <= rank**31*unit**10000 < (lower+1)**10000,
         'The exact integer power bracket failed')
    return F(rank*unit,lower+1), F(rank*unit,lower)


def budget(full_source_copy=False):
    # The complete omitted lifecycle is an unknown signed-moment charge.
    v = 112**3
    if full_source_copy:
        paid = {1:30*v, 8:3*v, 15:6*v+3*21504, 22:3*512}
        coarse = (F(1,4), F(3,10))
    else:
        paid = {1:30*v, 8:3*v, 15:6*v, 14:3*21504, 20:3*512}
        coarse = (F(3,10), F(1,3))
    targets = {73:2*v}
    powers = {r:power_interval(r) for r in set(paid)|set(targets)}
    lower = sum(n*powers[r][0] for r,n in targets.items()) - sum(n*powers[r][1] for r,n in paid.items())
    upper = sum(n*powers[r][1] for r,n in targets.items()) - sum(n*powers[r][0] for r,n in paid.items())
    need(coarse[0] < lower/v < upper/v < coarse[1], 'The declared remaining budget failed')
    return {'test_exponent':'31/10000', 'stages':3, 'ambient_rank':73,
            'granted_paid':paid, 'granted_targets':targets,
            'remaining_margin_per_port':[str(lower/v),str(upper/v)],
            'remaining_margin_per_port_per_local_call':[str(lower/(3*v)),str(upper/(3*v))],
            'copy_tariff_kind':'source_dimension' if full_source_copy else 'pairing_rank',
            'proved_coarse_interval_per_port':[str(x) for x in coarse],
            'unknown_obligations':['physical COPY at the source-dimension tariff' if full_source_copy
                                   else 'physical COPY at the pairing tariff',
                                   'cross-cube producer and all helper lifetimes',
                                   'old-value compensation and source restoration',
                                   'caller, compiler, precision and outer admission'],
            'complete_kappa_claim':False}


def controls(data):
    failures = []
    bad = json.loads(json.dumps(data))
    bad['mode_columns'][0][0] += 1
    try:
        geometry(bad)
    except ValueError:
        failures.append('changed_root_coefficient')
    else:
        raise ValueError('The altered root coefficient was accepted')
    bad = json.loads(json.dumps(data))
    bad['ports'][0]['q'] ^= 1
    try:
        geometry(bad)
    except ValueError:
        failures.append('changed_binary_label')
    else:
        raise ValueError('The altered binary label was accepted')
    for name, coeff in [('reversed_cubic_sign',{2:F(1,2),3:F(1,2)}),
                        ('omitted_degree_two_layer',{3:F(-1,2)})]:
        try:
            check_mask(3,coeff)
        except ValueError:
            failures.append(name)
        else:
            raise ValueError('An invalid fitting coefficient was accepted: '+name)
    return failures


def run():
    raw = SOURCE.read_bytes()
    need(sha256(raw).hexdigest() == SOURCE_HASH, 'The pinned normalizer bytes changed')
    data = json.loads(raw)
    result = {'status':'PASS_ODD_E8_DIRECT_SUM_COMPONENT',
              'source_sha256':SOURCE_HASH,
              'base':geometry(data), 'core':core(data),
              'families':[family(k) for k in range(1,16,2)],
              'budget':budget(), 'full_source_copy_budget':budget(True),
              'controls':controls(data)}
    triple = result['families'][1]
    need((triple['ports'],triple['fitting_rank'],triple['factor_terms'],triple['pairing_mass'])
         == (1404928,20480,22016,311296), 'The triple certificate changed')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    receipt = HERE/'RESULT.json'
    if args.write:
        receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    else:
        need(result == json.loads(receipt.read_text()), 'The regenerated result differs')
    print(result['status'], 'ports=1404928 dimension=25 rank=20480 pairing_mass=311296')
