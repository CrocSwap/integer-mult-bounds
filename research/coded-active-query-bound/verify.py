"""Actual-source checks for the active local-query obstruction.

Portable verifier; authenticates three retained source files and compares its
finite receipt. Standard library only. Apache-2.0; OpenAI Codex assistance.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import argparse
import types
import json
import sys

PACKAGE = Path(__file__).resolve().parent
DEFAULT_SOURCE = PACKAGE.parent / 'coded-native-caller'
EXPECTED = PACKAGE / 'RESULT.json'
PINS = {
    'CODE.json': '8be7f3f073b7981ec91c6af43edff0ac8a89f4824ef6026ae758c287dd6c03d0',
    'NORMALIZERS.json': 'ae8aad06aa5d1811d725895b3ab5a4f4daa9dcdd88294aa0d5f723e78bb1e0da',
    'clifford_exact.py': '2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank_binary(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def transpose(rows):
    return [sum(((row >> j) & 1) << i for i, row in enumerate(rows))
            for j in range(len(rows))]


def multiply(left, right):
    cols = transpose(right)
    return [sum(((row & col).bit_count() & 1) << j
                for j, col in enumerate(cols)) for row in left]


def central_image(rows):
    return sum((row & 1) << i for i, row in enumerate(rows))


def conjugated_b_rank(left, right):
    # G_left is orthogonal, so inverse equals transpose.
    relative = multiply(transpose(left), right)
    central = central_image(relative)
    block = [((central >> i) & 1) ^ (relative[0] if i == 0 else 0)
             for i in range(len(relative))]
    return rank_binary(block)


def validate_ports(ports):
    need(len(ports) == 112, 'Exact owner count')
    vectors = [port['q'] for port in ports]
    need(len(set(vectors)) == 112, 'All 112 central vectors are distinct')
    for port in ports:
        rows = port['G_rows']
        need(len(rows) == 9, 'Native address dimension')
        need(multiply(transpose(rows), rows) == [1 << i for i in range(9)],
             'Actual normalizer is binary orthogonal')
        need(central_image(rows) == port['q'], 'Actual central vector binding')


def validate_code(code):
    need(len(code) == 112 and all(len(row) == 112 for row in code), 'Code shape')
    need(all(code[i][i] == 0 for i in range(112)), 'Zero source diagonal')
    support = [sum(code[i][j] != 0 for i in range(112)) for j in range(112)]
    need(support == [52] * 112, 'All columns have 52 nonzero off-diagonal entries')
    need(all(code[i][j] == code[j][i] for i in range(112) for j in range(112)),
         'Actual symmetric source code')
    return support


def validate_modes(columns, code):
    need(len(columns) == 8 and all(len(column) == 112 for column in columns),
         'Eight source modes on 112 owners')
    need(all(value in (-1, 0, 1) for column in columns for value in column),
         'Actual signed integral mode entries')
    for a in range(8):
        for b in range(8):
            need(sum(x * y for x, y in zip(columns[a], columns[b])) == 56 * (a == b),
                 'Exact mode Gram matrix M^T M=56I')
    need(all(sum(column[i] != 0 for column in columns) == 4 for i in range(112)),
         'Every source owner has four mode contacts')
    for i in range(112):
        for j in range(112):
            need(sum(column[i] * column[j] for column in columns) == 4 * ((i == j) - code[i][j]),
                 'Actual code factorization A=I-MM^T/4')


def rejection(test, label):
    try:
        test()
    except ValueError:
        return label
    raise ValueError('Mutation was not rejected: ' + label)


def run(source):
    raw = {}
    for name, digest in PINS.items():
        source_path = source / name
        need(source_path.stat().st_size <= 1024 * 1024, 'Source exceeds fixed size bound: ' + name)
        raw[name] = source_path.read_bytes()
        need(sha256(raw[name]).hexdigest() == digest, 'Source hash: ' + name)
    normalizer_receipt = json.loads(raw['NORMALIZERS.json'])
    ports = normalizer_receipt['ports']
    mode_columns = normalizer_receipt['mode_columns']
    code = [[Fraction(x) for x in row] for row in json.loads(raw['CODE.json'])['A']]
    validate_ports(ports)
    support = validate_code(code)
    validate_modes(mode_columns, code)

    # Execute the authenticated bytes directly: no stale .pyc can replace them.
    ce = types.ModuleType('local_query_clifford')
    ce.__file__ = str(source / 'clifford_exact.py')
    sys.modules[ce.__name__] = ce
    exec(compile(raw['clifford_exact.py'], ce.__file__, 'exec'), ce.__dict__)
    q = ce.cgate(9, 1)
    q_inverse = q.adjoint()
    normalizers = []
    for port in ports:
        phase = tuple(2 * ((port['Z_mask'] >> j) & 1) for j in range(9))
        normalizers.append(ce.perm(9, port['G_rows']).then(ce.diag(9, (0,) * 9, phase)))
    inverses = [normalizer.adjoint() for normalizer in normalizers]

    pair_census = Counter()
    supported_census = Counter()
    one_sided_census = Counter()
    for j in range(112):
        for k in range(112):
            formula = conjugated_b_rank(ports[j]['G_rows'], ports[k]['G_rows'])
            # Literal composition is Q^-1 K_j^-1 K_k Q. Op.then is chronological.
            exact = q.then(normalizers[k]).then(inverses[j]).then(q_inverse)
            tableau = ce.rank([x for x, z, phase in exact.tab[9:]])
            expected = 0 if j == k else 2
            need(formula == tableau == expected,
                 'Actual right-coset test for ordered pair %d,%d' % (j, k))
            left_conjugate = q_inverse.then(normalizers[k]).then(inverses[j]).then(q)
            need(ce.rank([x for x, z, phase in left_conjugate.tab[9:]]) == expected,
                 'Actual left-coset test for ordered pair %d,%d' % (j, k))
            one_sided = normalizers[k].then(inverses[j]).then(q)
            one_grade = ce.rank([x for x, z, phase in one_sided.tab[9:]])
            need(one_grade == 1, 'One-sided transport is outside the monomial coset')
            one_sided_census[one_grade] += 1
            pair_census[formula] += 1
            if code[j][k]:
                supported_census[formula] += 1
    need(pair_census == {0: 112, 2: 12432}, 'Complete ordered-pair census')
    need(supported_census == {2: 5824}, 'Actual supported source transports')

    duplicate = json.loads(json.dumps(ports))
    duplicate[1] = duplicate[0]
    missing_column = [row[:] for row in code]
    for row in missing_column:
        row[0] = Fraction(0)
    diagonal = [row[:] for row in code]
    diagonal[0][0] = Fraction(1)
    bad_modes = [column[:] for column in mode_columns]
    bad_modes[0][0] += 1
    controls = [
        rejection(lambda: validate_ports(duplicate), 'duplicate physical direction'),
        rejection(lambda: validate_code(missing_column), 'empty code column'),
        rejection(lambda: validate_code(diagonal), 'nonzero source diagonal'),
        rejection(lambda: validate_modes(bad_modes, code), 'changed source mode factor'),
    ]
    # A duplicated direction is genuinely an exception to the theorem's
    # coset premise; do not merely reject it at the source-shape layer.
    need(conjugated_b_rank(ports[0]['G_rows'], ports[0]['G_rows']) == 0,
         'Coincident-direction monomial positive control')

    return {
        'schema': 'actual-coded-active-local-query-obstruction/1',
        'status': 'PASS_ACTUAL_SOURCE_COSET_SEPARATION',
        'source_sha256': PINS,
        'owner_count': 112,
        'distinct_central_vectors': 112,
        'column_nonzero_support': dict(Counter(support)),
        'all_ordered_pair_fourier_grade': dict(sorted(pair_census.items())),
        'supported_pair_fourier_grade': dict(sorted(supported_census.items())),
        'independent_formula_and_exact_tableau_checks': 12544,
        'left_coset_tableau_checks': 12544,
        'one_sided_transport_fourier_grade': dict(sorted(one_sided_census.items())),
        'mode_factor_entries_checked': 12544,
        'mode_gram_entries_checked': 64,
        'mode_contacts_per_owner': 4,
        'mutation_controls_rejected': controls,
        'theorem_scope': 'Standalone J=Q^-1 C Q, J-I, QP, PQ, canonical Q U_mode and V_mode Q, their free retraction rebases, and homogeneous direct sums; fresh inputs; arbitrary chronological unary same-width paid calls with data-independent linear feedback.',
        'free_alphabet': 'Any fixed finite projective monomial group H; each map is the same one-column h tensor-lifted on all columns. Independent per-column controls are excluded. No finite ambient Clifford-group premise is required.',
        'minimum_paid_unary_same_width_field_calls': 112,
        'one_sided_QP_and_PQ_H1_optimum': 112,
        'canonical_mode_expansion_and_extraction_H1_optimum': 112,
        'conjugated_J_112_call_attainability_claimed': False,
        'complete_controller_lower_bound': False,
        'proof_kernel_checked': False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=DEFAULT_SOURCE)
    parser.add_argument('--write', action='store_true', help='Regenerate the package-local finite receipt.')
    parser.add_argument('--json', action='store_true', help='Print the full finite receipt.')
    args = parser.parse_args()
    result = run(args.source)
    if args.write:
        EXPECTED.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(EXPECTED.stat().st_size <= 65536, 'Receipt size bound')
        need(json.loads(EXPECTED.read_text()) == json.loads(json.dumps(result)),
             'Frozen finite receipt differs')
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print('PASS_CODED_ACTIVE_QUERY_BOUND owners=112 pair_checks=12544 '
              'distinct_grade2=12432 supported=5824 local_unary_floor=112 '
              'one_sided_optimum=112 mutation_controls=4 modes=8')


if __name__ == '__main__':
    main()
