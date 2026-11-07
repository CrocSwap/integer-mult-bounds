"""New finite fixed-subspace rank certificates and tiny actual-query fixtures.

Only predecessor prose is authenticated. No PR6808 eight-role attaining word,
constructor, checker or source program is loaded or executed. Small matrices
may coincide with values occurring in predecessor examples.
"""
from itertools import product
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
MANIFEST_SHA = 'f6745060beaa1617ef8256b2211feed75554cd652b713d54f40addf2b5f69b29'
PATHS = {'predecessor/PR6808-README.md', 'predecessor/PR6808-PROOF.md',
         'predecessor/PR6800-README.md', 'predecessor/PR6800-PROOF.md'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def no_number(text):
    raise ValueError('noninteger JSON number')


def load(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=no_number, parse_constant=no_number)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate():
    raw = (PACKAGE / 'SOURCE-PINS.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'source manifest bytes')
    pins = load(raw)
    require(type(pins['schema_version']) is int and pins['schema_version'] == 1, 'source schema')
    require(len(pins['files']) == 4 and {x['local_path'] for x in pins['files']} == PATHS, 'source inventory')
    result = {}
    for row in pins['files']:
        path = PACKAGE / row['local_path']
        require(path.is_file() and not path.is_symlink(), 'source regular file')
        data = path.read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        require((len(data), hashlib.sha256(data).hexdigest(), blob) ==
                (row['bytes'], row['sha256'], row['git_blob']) and row['mode'] == '100644', 'source bytes')
        result[row['local_path']] = row['sha256']
    return result


def zero(rows, columns):
    return [[0]*columns for _ in range(rows)]


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def add(left, right, field, sign=1):
    require(len(left) == len(right), 'matrix row shape')
    require(all(len(a) == len(b) for a, b in zip(left, right)), 'matrix column shape')
    return [[(a+sign*b) % field for a, b in zip(ar, br)] for ar, br in zip(left, right)]


def multiply(left, right, field, columns=None):
    require(all(len(row) == len(right) for row in left), 'matrix product shape')
    width = len(right[0]) if right else (0 if columns is None else columns)
    require(all(len(row) == width for row in right), 'rectangular right matrix')
    result = zero(len(left), width)
    for i, row in enumerate(left):
        for k, scalar in enumerate(row):
            if scalar:
                for j, other in enumerate(right[k]):
                    result[i][j] = (result[i][j] + scalar*other) % field
    return result


def rref(matrix, field):
    work = [[x % field for x in row] for row in matrix]
    height, width = len(work), len(work[0]) if work else 0
    pivots = []
    for column in range(width):
        row = len(pivots)
        pivot = next((i for i in range(row, height) if work[i][column]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        scale = pow(work[row][column], field-2, field)
        work[row] = [(x*scale) % field for x in work[row]]
        for i in range(height):
            if i != row and work[i][column]:
                scale = work[i][column]
                work[i] = [(x-scale*y) % field for x, y in zip(work[i], work[row])]
        pivots.append(column)
        if len(pivots) == height:
            break
    return work, pivots


def rank(matrix, field):
    return len(rref(matrix, field)[1])


def nullspace(matrix, field):
    work, pivots = rref(matrix, field)
    width = len(matrix[0]) if matrix else 0
    vectors = []
    for free in range(width):
        if free in pivots:
            continue
        vector = [0]*width
        vector[free] = 1
        for row, column in enumerate(pivots):
            vector[column] = -work[row][free] % field
        vectors.append(vector)
    return [[vector[i] for vector in vectors] for i in range(width)]


def inverse(matrix, field):
    size = len(matrix)
    extended = [row[:] + tail for row, tail in zip(matrix, identity(size))]
    reduced, pivots = rref(extended, field)
    require(pivots[:size] == list(range(size)), 'singular ordinary scalar map')
    result = [row[size:] for row in reduced]
    require(multiply(matrix, result, field) == multiply(result, matrix, field) == identity(size),
            'ordinary scalar inverse')
    return result


def factor(matrix, field):
    _, pivots = rref(matrix, field)
    amount = len(pivots)
    u = [[row[j] for j in pivots] for row in matrix]
    if amount == 0:
        v = []
    elif amount == 1:
        row = next(i for i in range(2) if u[i][0])
        scale = pow(u[row][0], field-2, field)
        v = [[x*scale % field for x in matrix[row]]]
    else:
        v = multiply(inverse(u, field), matrix, field)
    require(multiply(u, v, field, columns=2) == matrix, 'rank factor product')
    require(rank(u, field) == rank(v, field) == amount, 'full rank factors')
    return amount, u, v


def square_zero(matrix, field):
    require(len(matrix) == 2 and all(len(row) == 2 for row in matrix), 'two-role shape')
    require(all(type(x) is int and 0 <= x < field for row in matrix for x in row), 'field entries')
    require(multiply(matrix, matrix, field) == zero(2, 2), 'coupling is not square zero')


def sum_matrices(matrices, field):
    result = zero(2, 2)
    for matrix in matrices:
        result = add(result, matrix, field)
    return result


def lemma(matrices, field, factors=None):
    if factors is None:
        factors = []
        for matrix in matrices:
            square_zero(matrix, field)
            factors.append(factor(matrix, field))
    else:
        require(len(matrices) == len(factors), 'factor inventory')
    total = sum_matrices(matrices, field)
    amounts = [item[0] for item in factors]
    volume, maximum = sum(amounts), max(amounts, default=0)
    u = [sum((item[1][row] for item in factors), []) for row in range(2)]
    v = [row[:] for _, _, block in factors for row in block]
    require(multiply(u, v, field, columns=2) == total, 'global M equals UV')
    e = multiply(v, u, field)
    start = 0
    for amount, local_u, local_v in factors:
        require(multiply(local_v, local_u, field) == zero(amount, amount), 'ViUi not zero')
        require([row[start:start+amount] for row in e[start:start+amount]] == zero(amount, amount),
                'E diagonal block not zero')
        start += amount
    basis = nullspace(add(total, identity(2), field, -1), field)
    dimension = len(basis[0])
    require(rank(basis, field) == dimension and multiply(total, basis, field) == basis, 'full fixed space')
    image = multiply(v, basis, field)
    require(rank(image, field) == dimension, 'V not injective on fixed space')
    require(multiply(e, image, field) == image, 'E does not fix V(P)')
    defect = add(identity(volume), e, field, -1)
    defect_rank = rank(defect, field)
    require(maximum <= defect_rank <= volume-dimension, 'identity-diagonal rank sandwich')
    require(volume >= dimension+maximum, 'fixed-subspace rank lower bound')
    return dict(R=volume, d=dimension, maximum_rank=maximum, rank_I_minus_E=defect_rank,
                fixed_basis=basis, M=total, E=e,
                M_is_projection=multiply(total, total, field) == total)


def square_zero_matrices(field):
    matrices, factors = [], []
    for cells in product(range(field), repeat=4):
        matrix = [list(cells[:2]), list(cells[2:])]
        if multiply(matrix, matrix, field) == zero(2, 2):
            square_zero(matrix, field)
            matrices.append(matrix)
            factors.append(factor(matrix, field))
    require(matrices and zero(2, 2) in matrices, 'zero-padding inventory')
    return matrices, factors


def enumerate_lemma(field, maximum_slots):
    matrices, factors = square_zero_matrices(field)
    histogram, cases, nonprojective_fixed = {}, 0, 0
    certificate_digest = hashlib.sha256()
    for slots in range(maximum_slots+1):
        for indices in product(range(len(matrices)), repeat=slots):
            selected = [matrices[i] for i in indices]
            result = lemma(selected, field, [factors[i] for i in indices])
            paid_count = sum(factors[i][0] > 0 for i in indices)
            key = '/'.join(str(x) for x in (slots, paid_count, result['R'], result['d'], result['maximum_rank']))
            histogram[key] = histogram.get(key, 0)+1
            nonprojective_fixed += int(result['d'] > 0 and not result['M_is_projection'])
            certificate_digest.update(canonical(dict(indices=indices, certificate=result))+b'\n')
            cases += 1
    return dict(field=field, scalar_roles=2, square_zero_matrices=len(matrices), maximum_slots=maximum_slots,
                ordered_tuple_cases=cases, zero_is_padding_not_paid=True,
                histogram_axes=['slots', 'nonzero_paid_summands', 'R', 'fixed_dimension', 'maximum_rank'],
                histogram=histogram, nonprojection_with_nonzero_fixed_space=nonprojective_fixed,
                certificate_sha256=certificate_digest.hexdigest())


def rank_two_block_fixture(field):
    """One four-role classical block fixture, not the six-target attaining word."""
    u1 = [[1, 0], [0, 1], [0, 0], [0, 0]]
    v1 = [[0, 0, 1, 0], [0, 0, 0, 1]]
    u2 = [[0, 0], [0, 0], [1, 0], [0, 1]]
    v2 = [[1, 0, 0, 0], [0, 1, 0, 0]]
    summands = []
    for u, v in ((u1, v1), (u2, v2)):
        n = multiply(u, v, field)
        require(rank(u, field) == rank(v, field) == rank(n, field) == 2,
                'rank-two block full-rank factor')
        require(multiply(v, u, field) == zero(2, 2), 'rank-two block ViUi')
        require(multiply(n, n, field) == zero(4, 4), 'rank-two block square zero')
        summands.append(n)
    u = [left+right for left, right in zip(u1, u2)]
    v = v1+v2
    m = add(summands[0], summands[1], field)
    require(multiply(u, v, field) == m, 'rank-two block M equals UV')
    e = multiply(v, u, field)
    for start in (0, 2):
        require([row[start:start+2] for row in e[start:start+2]] == zero(2, 2),
                'rank-two block E diagonal')
    basis = nullspace(add(m, identity(4), field, -1), field)
    require(len(basis[0]) == rank(basis, field) == 2, 'rank-two block full fixed dimension')
    image = multiply(v, basis, field)
    require(multiply(m, basis, field) == basis and rank(image, field) == 2,
            'rank-two block fixed-space injection')
    require(multiply(e, image, field) == image, 'rank-two block E fixes V(P)')
    defect_rank = rank(add(identity(4), e, field, -1), field)
    volume, dimension = len(e), len(basis[0])
    maximum = max(rank(n, field) for n in summands)
    require(maximum <= defect_rank <= volume-dimension and volume == dimension+maximum,
            'rank-two block sandwich equality')
    require(multiply(m, m, field) != m, 'rank-two block nonprojection')
    return dict(field=field, scalar_roles=4, summand_ranks=[2, 2], R=4, fixed_dimension=2,
                maximum_rank=2, rank_I_minus_E=defect_rank, summands=summands,
                U=u, V=v, E=e, M=m, fixed_basis=basis, M_is_projection=False,
                scope='One classical A tensor I2 / B tensor I2 factorization fixture.')


def ring_product(left, right):
    a, b = left
    c, d = right
    return (add(multiply(a, c, 2), multiply(b, d, 2), 2),
            add(multiply(a, d, 2), multiply(b, c, 2), 2))


def ordinary(matrix):
    return matrix, zero(2, 2)


def actual_paid(matrix):
    square_zero(matrix, 2)
    require(rank(matrix, 2) > 0, 'zero omitted from nonzero paid count')
    return identity(2), matrix


def validate_free(pair):
    constant, query = pair
    require(query == zero(2, 2), 'Q-dependent free gate')
    require(rank(constant, 2) == 2, 'singular ordinary scalar map')


def conjugated(matrix, change):
    return multiply(multiply(inverse(change, 2), matrix, 2), change, 2)


def clean_endpoint(pair, basis):
    constant, query = pair
    require(multiply(constant, basis, 2) == zero(2, len(basis[0]))
            and multiply(query, basis, 2) == basis, 'not a complete clean-column endpoint')


def normalize(instructions):
    actual, c, summands, paid_ranks = ordinary(identity(2)), identity(2), [], []
    step_digest = hashlib.sha256()
    for kind, data in instructions:
        if kind == 'free':
            validate_free(data)
            change = data[0]
            factor_ring = data
        else:
            require(kind == 'paid', 'instruction kind')
            factor_ring = actual_paid(data)
            change = add(identity(2), data, 2)
        actual = ring_product(actual, factor_ring)
        summands = [conjugated(n, change) for n in summands]
        if kind == 'paid':
            summands.append(data)
            paid_ranks.append(rank(data, 2))
        c = multiply(c, change, 2)
        require(rank(c, 2) == 2, 'normalization constant invertibility')
        for n in summands:
            square_zero(n, 2)
        require([rank(n, 2) for n in summands] == paid_ranks, 'conjugation rank preservation')
        m = sum_matrices(summands, 2)
        expected = (multiply(c, add(identity(2), m, 2), 2), multiply(c, m, 2))
        require(actual == expected, 'actual I+QN absorption/normalization')
        require(multiply(inverse(c, 2), actual[1], 2) == m, 'coefficient-derived normalized M')
        step_digest.update(canonical(dict(kind=kind, actual=actual, C=c, M=m))+b'\n')
    certificate = lemma(summands, 2)
    clean = nullspace(actual[0] + add(actual[1], identity(2), 2, -1), 2)
    clean_endpoint(actual, clean)
    require(multiply(c, clean, 2) == clean and multiply(certificate['M'], clean, 2) == clean,
            'clean columns imply C and M fix P')
    require(certificate['R'] >= len(clean[0])+certificate['maximum_rank'], 'actual clean rank bound')
    return actual, c, certificate, clean, step_digest.hexdigest(), paid_ranks


def normalization_fixtures():
    matrices, _ = square_zero_matrices(2)
    nonzero = [n for n in matrices if rank(n, 2)]
    scalars = []
    for cells in product(range(2), repeat=4):
        matrix = [list(cells[:2]), list(cells[2:])]
        if rank(matrix, 2) == 2:
            scalars.append(matrix)
    swap = [[0, 1], [1, 0]]
    rows, steps, paid_calls = [], 0, 0
    for g, first, second in product(scalars, nonzero, nonzero):
        instructions = [('free', ordinary(g)), ('paid', first), ('free', ordinary(swap)),
                        ('paid', second), ('free', ordinary(inverse(g, 2)))]
        actual, c, cert, clean, trace_hash, ranks = normalize(instructions)
        rows.append(dict(word_sha256=digest(instructions), complete_ring_sha256=digest(actual),
                         C=c, M=cert['M'], normalized_ranks=ranks,
                         full_fixed_dimension=cert['d'], actual_clean_dimension=len(clean[0]),
                         step_sha256=trace_hash))
        steps += len(instructions)
        paid_calls += len(ranks)
    return dict(field=2, ring='F2[Q]/(Q^2-1)', scalar_roles=2,
                new_literal_words=len(rows), actual_instruction_steps=steps,
                actual_nonzero_paid_instructions=paid_calls, words=rows,
                scope='New tiny actual-alphabet normalization fixtures; no old six-target attaining word.')


def rejected(name, callback, reason, witness):
    try:
        callback()
    except ValueError as error:
        require(str(error) == reason, 'wrong control rejection: '+name)
        return dict(name=name, outcome='REJECTED_FOR_INTENDED_REASON', reason=reason, witness=witness)
    raise ValueError('control accepted: '+name)


def require_projection(matrix):
    require(multiply(matrix, matrix, 2) == matrix, 'false extra projection assumption')


def controls():
    unit = identity(2)
    fixed = nullspace(add(unit, identity(2), 2, -1), 2)
    first = rejected('non_square_zero_identity', lambda: lemma([unit], 2), 'coupling is not square zero',
                     dict(N=unit, square=multiply(unit, unit, 2), rank=rank(unit, 2),
                          fixed_dimension=len(fixed[0]), false_R=2, false_required=4))
    n3, public = [[1, 1], [1, 1]], [[1], [0]]
    leak_word = [('free', ordinary(add(unit, n3, 2))), ('paid', n3)]
    actual, c, cert, _, _, _ = normalize(leak_word)
    require(actual[0][0][0] == 0 and actual[1][0][0] == 1, 'payload-only Q witness')
    target_pair = ([[0, 0], [0, 1]], [[1, 0], [0, 0]])
    require(add(*actual, 2) == add(*target_pair, 2) == identity(2), 'Q=1 collapse witness')
    second = rejected('payload_only_helper_leak_and_Q1_collapse', lambda: clean_endpoint(actual, public),
                      'not a complete clean-column endpoint',
                      dict(actual=actual, public_column=public, helper_constant=actual[0][1][0],
                           helper_Q=actual[1][1][0], Q1_actual=add(*actual, 2), Q1_target=add(*target_pair, 2)))
    n1 = [[0, 1], [0, 0]]
    swap = [[0, 1], [1, 0]]
    n1 = conjugated(n1, swap)
    word = [('free', ordinary(add(unit, n1, 2))), ('paid', n1),
            ('free', ordinary(add(unit, n3, 2))), ('paid', n3)]
    genuine, c, cert, clean, _, _ = normalize(word)
    clean_endpoint(genuine, public)
    require(c == unit and cert['d'] == 1 and not cert['M_is_projection'], 'genuine clean nonprojection')
    third = rejected('projection_assumption_excludes_legal_clean_case', lambda: require_projection(cert['M']),
                     'false extra projection assumption',
                     dict(M=cert['M'], square=multiply(cert['M'], cert['M'], 2), actual_word=word,
                          public_column=public, clean_dimension=len(clean[0]), rank_certificate=cert))
    fourth = rejected('Q_dependent_free_gate', lambda: normalize([('free', target_pair)]), 'Q-dependent free gate',
                      dict(forbidden_free_pair=target_pair, actual_clean_public_column=public))
    fifth = rejected('zero_paid_counting_convention', lambda: actual_paid(zero(2, 2)), 'zero omitted from nonzero paid count',
                     dict(N=zero(2, 2), scope='Legal identity padding is omitted from the canonical nonzero paid count; not a forbidden source-model gate.'))
    return [first, second, third, fourth, fifth]


def profile_necessity():
    surviving = []
    for ranks in product(range(3), repeat=4):
        volume, maximum = sum(ranks), max(ranks)
        if volume >= 6+maximum:
            surviving.append(list(ranks))
    require(surviving == [[2, 2, 2, 2]], 'six-target at-most-four rank profiles')
    return dict(productive_dimension=6, call_limit=4, rank_cap=2, padded_profiles_checked=3**4,
                necessary_profiles=surviving, necessary_total_rank=8,
                attainment='Cited PR6808 rank8 witness; its word/data/constructor/verifier is not replayed.',
                higher_call_counts='Outside this optimum statement.')


def parser_controls():
    return [rejected('duplicate_JSON', lambda: load('{"x":1,"x":1}'), 'duplicate JSON key', {'input':'duplicate key'}),
            rejected('floating_JSON', lambda: load('{"x":1.0}'), 'noninteger JSON number', {'input':'1.0'}),
            rejected('nonfinite_JSON', lambda: load('{"x":NaN}'), 'noninteger JSON number', {'input':'NaN'})]


def calculate():
    sources = authenticate()
    return dict(status='PASS_CLEAN_FIXED_SUBSPACE_RANK_BOUND', schema_version=1, source_sha256=sources,
                algebraic_rank_cases=[enumerate_lemma(2, 4), enumerate_lemma(3, 4), enumerate_lemma(5, 3)],
                rank_two_block_fixtures=[rank_two_block_fixture(p) for p in (2, 3, 5)],
                actual_F2_normalization=normalization_fixtures(), mathematical_controls=controls(),
                parser_controls=parser_controls(), rank_profile_necessity=profile_necessity(),
                source_programs_executed=False,
                overlap_disclosure='Tiny2x2matrixvalues may coincide with predecessor examples; no old6808eight-roleattainer runs.',
                scope='All-field fixed-subspace lemma corroboration plus F2 actual-query reduction; no higher-call/global classification.')


def main():
    require(sys.argv[1:] in ([], ['--emit']), 'only optional --emit is supported')
    packet = calculate()
    if not sys.argv[1:]:
        require(canonical(load((PACKAGE / 'RESULT.json').read_bytes())) == canonical(packet),
                'retained complete result mismatch')
    print(canonical(packet).decode())


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print('FAIL_CLEAN_FIXED_SUBSPACE_RANK_BOUND: '+str(error), file=sys.stderr)
        raise SystemExit(1)
