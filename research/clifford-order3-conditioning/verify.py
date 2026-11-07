"""New order-three lift, quadratic-form and two-trace LP certificate.

The character table, width-nine multiplicities and even-sector representation
identifications are inherited, authenticated mathematical inputs. No predecessor
executable or decomposition engine is imported or run. All arithmetic is exact.
"""
from fractions import Fraction as F
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
MANIFEST_SHA = '51d69b9daeefb8ac8b9c530605e17dad60e35e426d31652928b1dff29582fd81'
PATHS = {'source/table.json', 'source/width-nine-input.json', 'source/EXTERNAL.json',
         'predecessor/PR6794-PROOF.md', 'predecessor/PR6714-PROOF.md'}
ZERO, ONE, IMAG = (F(0), F(0)), (F(1), F(0)), (F(0), F(1))


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


def rational(value):
    value = F(value)
    return [value.numerator, value.denominator]


def gaussian(value):
    return [*rational(value[0]), *rational(value[1])]


def authenticate():
    raw = (PACKAGE / 'SOURCE-PINS.json').read_bytes()
    require(hashlib.sha256(raw).hexdigest() == MANIFEST_SHA, 'source manifest bytes')
    pins = load(raw)
    require(type(pins['schema_version']) is int and pins['schema_version'] == 1, 'source schema')
    require(len(pins['files']) == 5 and {x['local_path'] for x in pins['files']} == PATHS, 'source inventory')
    bodies, hashes = {}, {}
    for row in pins['files']:
        path = PACKAGE / row['local_path']
        require(path.is_file() and not path.is_symlink(), 'source regular file')
        data = path.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        require((len(data), hashlib.sha256(data).hexdigest(), blob) ==
                (row['bytes'], row['sha256'], row['git_blob']) and row['mode'] == '100644', 'source bytes')
        bodies[row['local_path']], hashes[row['local_path']] = data, row['sha256']
    return {name: load(bodies[name]) for name in PATHS if name.endswith('.json')}, hashes


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def multiply(a, b):
    return a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0]


def conjugate(a):
    return a[0], -a[1]


def matrix_zero(n):
    return [[ZERO for _ in range(n)] for _ in range(n)]


def matrix_identity(n):
    result = matrix_zero(n)
    for i in range(n):
        result[i][i] = ONE
    return result


def matrix_scale(matrix, scalar):
    return [[multiply(scalar, value) for value in row] for row in matrix]


def matrix_adjoint(matrix):
    return [[conjugate(matrix[j][i]) for j in range(len(matrix))] for i in range(len(matrix))]


def matrix_product(left, right):
    n, result = len(left), matrix_zero(len(left))
    for i in range(n):
        for k in range(n):
            if left[i][k] == ZERO:
                continue
            for j in range(n):
                if right[k][j] != ZERO:
                    result[i][j] = add(result[i][j], multiply(left[i][k], right[k][j]))
    return result


def tensor(left, right):
    return [[multiply(a, b) for a in ar for b in br] for ar in left for br in right]


def matrix_trace(matrix):
    total = ZERO
    for i in range(len(matrix)):
        total = add(total, matrix[i][i])
    return total


def matrix_key(matrix):
    return tuple(value for row in matrix for value in row)


def sparse_matrix(matrix):
    return [[i, j, gaussian(value)] for i, row in enumerate(matrix)
            for j, value in enumerate(row) if value != ZERO]


def selected_lift():
    c = F(1, 2), F(1, 2)
    h = matrix_scale([[ONE, ONE], [ONE, (F(-1), F(0))]], c)
    phase = [[ONE, ZERO], [ZERO, IMAG]]
    small = matrix_product(h, phase)
    return small, tensor(small, matrix_identity(4))


def square_characters(g):
    trace = matrix_trace(g)
    second = matrix_trace(matrix_product(g, g))
    squared = multiply(trace, trace)
    symmetric = multiply((F(1, 2), F(0)), add(squared, second))
    exterior = multiply((F(1, 2), F(0)), add(squared, (-second[0], -second[1])))
    return dict(natural_trace=gaussian(trace), trace_of_square=gaussian(second),
                symmetric_square_trace=gaussian(symmetric), exterior_square_trace=gaussian(exterior),
                scope='Actual natural symmetric/exterior-square characters; no irreducibility assertion.')


def lift_checks(g):
    identity = matrix_identity(8)
    require(matrix_product(g, matrix_adjoint(g)) == identity, 'lift is not unitary')
    cube = matrix_product(matrix_product(g, g), g)
    require(cube == matrix_scale(identity, (F(-1), F(0))), 'lift cube is not minus identity')
    require(matrix_trace(g) == (F(4), F(0)), 'lift trace is not four')
    characters = square_characters(g)
    require(characters['symmetric_square_trace'] == gaussian((F(6), F(0)))
            and characters['exterior_square_trace'] == gaussian((F(10), F(0))), 'square-character witnesses')
    return dict(unitary=True, trace=gaussian(matrix_trace(g)), cube_phase=gaussian(cube[0][0]),
                character_witnesses=characters)


def pauli(label):
    a, b = label & 7, label >> 3
    basic = {(0, 0): matrix_identity(2),
             (1, 0): [[ZERO, ONE], [ONE, ZERO]],
             (0, 1): [[ONE, ZERO], [ZERO, (F(-1), F(0))]],
             (1, 1): [[ZERO, (F(0), F(-1))], [IMAG, ZERO]]}
    result = [[ONE]]
    for bit in range(3):
        result = tensor(result, basic[((a >> bit) & 1, (b >> bit) & 1)])
    return result


class NonPauli(ValueError):
    def __init__(self, label, image):
        super().__init__('conjugated image is not a signed Pauli')
        self.label, self.image = label, image


def pauli_action(g):
    originals = [pauli(label) for label in range(64)]
    lookup = {}
    for label, matrix in enumerate(originals):
        for sign in (1, -1):
            key = matrix_key(matrix_scale(matrix, (F(sign), F(0))))
            require(key not in lookup, 'signed Pauli collision')
            lookup[key] = (label, sign)
    action, adjoint = [], matrix_adjoint(g)
    for label, matrix in enumerate(originals):
        image = matrix_product(matrix_product(g, matrix), adjoint)
        if matrix_key(image) not in lookup:
            raise NonPauli(label, image)
        target, sign = lookup[matrix_key(image)]
        action.append(dict(label=label, target=target, sign=sign))
    require(len({row['target'] for row in action}) == 64, 'Pauli label permutation')
    return action


def expected_label(label):
    a, b = label & 7, label >> 3
    first_a, first_b = a & 1, b & 1
    return ((a & 6) | (first_a ^ first_b)) + 8 * ((b & 6) | first_a)


def quadratic(form, label):
    alpha, beta, a, b = form & 7, form >> 3, label & 7, label >> 3
    return ((a & b).bit_count() + (alpha & a).bit_count() + (beta & b).bit_count()) & 1


def arf(form):
    return ((form & 7) & (form >> 3)).bit_count() & 1


def form_data(action, classifier=arf):
    tables = [tuple(quadratic(form, label) for label in range(64)) for form in range(64)]
    lookup = {values: form for form, values in enumerate(tables)}
    require(len(lookup) == 64, 'distinct quadratic forms')
    sizes, fixed, records = [0, 0], [0, 0], []
    for form in range(64):
        pullback = tuple(quadratic(form, row['target']) for row in action)
        require(pullback in lookup, 'quadratic pullback')
        target, orbit = lookup[pullback], classifier(form)
        require(classifier(target) == orbit, 'Arf preservation')
        sizes[orbit] += 1
        fixed[orbit] += int(target == form)
        records.append(dict(form=form, pullback=target, arf=orbit, fixed=target == form))
    return dict(orbit_sizes=sizes, fixed_by_arf=fixed, records=records,
                distinct_form_vector_pairs=64*64)


def check_forms(data):
    require(data['orbit_sizes'] == [36, 28], 'quadratic orbit sizes')
    require(data['fixed_by_arf'] == [6, 10], 'order3 fixed-form counts')
    for row in data['records']:
        expected = bool((row['form'] & 1) and ((row['form'] >> 3) & 1))
        require(row['fixed'] == expected, 'fixed-form coordinate condition')


def extract_points(table, width, tcols=(31, 32, 33), zcols=(9, 10)):
    chars = table['characters']
    require(len(chars) == 67 and all(len(row) == 67 for row in chars), '67 by 67 table')
    require(all(type(x) is int for row in chars for x in row), 'integer table')
    rows, multiplicities = width['quotient_source_rows'], width['odd_tensor_multiplicities']['9']
    require(len(rows) == len(multiplicities) == 30 and rows == sorted(set(rows)), 'thirty quotient rows')
    result = []
    for source_row, multiplicity in zip(rows, multiplicities):
        require(type(source_row) is int and 1 <= source_row <= 67, 'source row index')
        require(type(multiplicity) is int and multiplicity >= 0, 'width-nine multiplicity')
        source = chars[source_row-1]
        require(source[0] > 0, 'positive degree')
        require(len({source[j-1] for j in tcols}) == len({source[j-1] for j in zcols}) == 1,
                'selected published columns agree')
        result.append(dict(row=source_row, d=source[0], t=source[tcols[0]-1],
                           z=source[zcols[0]-1], m=multiplicity))
    return result


def bind_classes(points, width):
    require(width['quotient_source_classes'][13] == [31, 32, 33], 'transvection columns')
    require(width['quotient_source_classes'][4] == [9, 10], 'order3 columns')
    require(width['quotient_class_sizes'][4] == 672 and width['fixed_dimensions'][4] == 4,
            'cited order3 class identification')
    check_column_anchors(points)


def check_column_anchors(points):
    expected = {1: (1, 1, 1, 269), 2: (7, -5, 4, 0), 9: (56, -24, 11, 28)}
    actual = {row['row']: (row['d'], row['t'], row['z'], row['m']) for row in points if row['row'] in expected}
    require(actual == expected, 'selected column anchors')


def bounds_for(orbit_size, forms):
    index = forms['orbit_sizes'].index(orbit_size)
    fixed = forms['fixed_by_arf'][index]
    return (F(-16, orbit_size), F(16, orbit_size),
            F(-fixed, 2*orbit_size), F(fixed, orbit_size))


def determinant(rows):
    a, b, c = rows
    return (a[0]*(b[1]*c[2]-b[2]*c[1]) - a[1]*(b[0]*c[2]-b[2]*c[0])
            + a[2]*(b[0]*c[1]-b[1]*c[0]))


def solve3(rows, rhs):
    det = determinant(rows)
    if not det:
        return None
    result = []
    for column in range(3):
        altered = [list(row) for row in rows]
        for i in range(3):
            altered[i][column] = rhs[i]
        result.append(F(determinant(altered), det))
    return result


def metrics(points, weights):
    total, t, z, objective = F(0), F(0), F(0), F(0)
    for index, weight in weights:
        row = points[index]
        total += weight
        t += weight * F(row['t'], row['d'])
        z += weight * F(row['z'], row['d'])
        objective += weight * F(row['m'], row['d'])
    return total, t, z, objective


def feasibility(points, weights, bounds):
    if not weights or any(weight <= 0 for _, weight in weights):
        return 'positive support weights', None
    total, t, z, objective = metrics(points, weights)
    if total != 1:
        return 'simplex normalization', None
    if not bounds[0] <= t <= bounds[1]:
        return 'transvection trace slab', None
    if not bounds[2] <= z <= bounds[3]:
        return 'order3 trace slab', None
    return None, (t, z, objective)


def primal_record(points, weights, values):
    return dict(weights=[[points[i]['row'], rational(w)] for i, w in weights],
                transvection=rational(values[0]), order3=rational(values[1]), objective=rational(values[2]))


def record_vertex(state, points, weights, bounds):
    reason, values = feasibility(points, weights, bounds)
    if reason:
        return
    key = tuple((i, w.numerator, w.denominator) for i, w in weights)
    if key in state['seen']:
        return
    state['seen'].add(key)
    size = len(weights)
    state['counts'][size] = state['counts'].get(size, 0) + 1
    state['digest'].update(canonical(primal_record(points, weights, values)))
    for kind in ('minimum', 'maximum'):
        old = state[kind]
        if old is None or (values[2] < old[0] if kind == 'minimum' else values[2] > old[0]):
            state[kind] = (values[2], tuple(weights), values)


def vertices(points, bounds):
    state = dict(seen=set(), counts={}, digest=hashlib.sha256(), minimum=None, maximum=None)
    for i in range(30):
        record_vertex(state, points, [(i, F(1))], bounds)
    for i, j in combinations(range(30), 2):
        for coordinate, bound in ((0, bounds[0]), (0, bounds[1]), (1, bounds[2]), (1, bounds[3])):
            key = 't' if coordinate == 0 else 'z'
            left, right = F(points[i][key], points[i]['d']), F(points[j][key], points[j]['d'])
            if left != right:
                weight = (bound-right)/(left-right)
                record_vertex(state, points, [(i, weight), (j, 1-weight)], bounds)
    for indices in combinations(range(30), 3):
        rows = [[points[i][key] for i in indices] for key in ('d', 't', 'z')]
        for t, z in product(bounds[:2], bounds[2:]):
            raw = solve3(rows, (F(1), t, z))
            if raw is not None:
                weights = [(i, raw[j]*points[i]['d']) for j, i in enumerate(indices)]
                record_vertex(state, points, weights, bounds)
    require(state['seen'], 'empty two-trace feasible polytope')
    return state


def dual_value(coefficients, bounds, kind):
    constant, t, z = coefficients
    chosen = []
    for coefficient, low, high in ((t, bounds[0], bounds[1]), (z, bounds[2], bounds[3])):
        if coefficient == 0:
            chosen.append(None)
        elif kind == 'minimum':
            chosen.append(low if coefficient > 0 else high)
        else:
            chosen.append(high if coefficient > 0 else low)
    value = constant + sum((c*b for c, b in zip((t, z), chosen) if b is not None), F(0))
    return value, chosen


def dual_certificate(points, bounds, kind, primal):
    objective, support, values = primal
    required = [((points[i]['d'], points[i]['t'], points[i]['z']), F(points[i]['m'])) for i, _ in support]
    extras = [((row['d'], row['t'], row['z']), F(row['m'])) for row in points]
    extras += [((0, 1, 0), F(0)), ((0, 0, 1), F(0))]
    for completion in combinations(extras, 3-len(required)):
        equations = required + list(completion)
        coefficients = solve3([row for row, _ in equations], [rhs for _, rhs in equations])
        if coefficients is None:
            continue
        residuals = []
        for row in points:
            plane = sum((a*row[k] for a, k in zip(coefficients, ('d', 't', 'z'))), F(0))
            residuals.append(F(row['m'])-plane if kind == 'minimum' else plane-F(row['m']))
        value, chosen = dual_value(coefficients, bounds, kind)
        if min(residuals) < 0 or value != objective:
            continue
        for coordinate, bound in zip(values[:2], chosen):
            require(bound is None or coordinate == bound, 'primal/dual active-bound mismatch')
        return dict(affine_coefficients=[rational(x) for x in coefficients],
                    signed_active_bounds=[rational(x) if x is not None else None for x in chosen],
                    scaled_residuals=[[row['row'], rational(x)] for row, x in zip(points, residuals)],
                    objective=rational(value), primal=primal_record(points, support, values))
    raise ValueError('no exact supporting-plane dual for primal optimum')


def lp_certificate(points, bounds, orbit_size):
    state = vertices(points, bounds)
    extrema = {kind: dual_certificate(points, bounds, kind, state[kind]) for kind in ('minimum', 'maximum')}
    return dict(orbit_size=orbit_size, slabs=[rational(x) for x in bounds],
                distinct_vertices=len(state['seen']), support_histogram=state['counts'],
                vertex_digest=state['digest'].hexdigest(), **extrema)


def rejected(name, callback, reason, witness):
    try:
        callback()
    except ValueError as error:
        require(str(error) == reason, 'wrong control rejection: '+name)
        return dict(name=name, outcome='REJECTED_FOR_INTENDED_REASON', reason=reason, witness=witness)
    raise ValueError('control accepted: '+name)


def lifted_controls(g, action, forms):
    shifted = matrix_scale(g, IMAG)
    cube = matrix_product(matrix_product(shifted, shifted), shifted)
    require(cube == matrix_scale(matrix_identity(8), IMAG), 'wrong-phase actual cube')
    require(pauli_action(shifted) == action, 'global-phase control changed Pauli action')
    characters = square_characters(shifted)
    require(characters['symmetric_square_trace'] == gaussian((F(-6), F(0)))
            and characters['exterior_square_trace'] == gaussian((F(-10), F(0))), 'wrong-phase actual characters')
    first = rejected('wrong_global_phase_i_g', lambda: lift_checks(shifted), 'lift cube is not minus identity',
                     dict(trace=gaussian(matrix_trace(shifted)), cube_phase=gaussian(cube[0][0]),
                          same_signed_Pauli_action=True, character_witnesses=characters))
    permutation = matrix_identity(8)
    permutation[6], permutation[7] = permutation[7], permutation[6]
    try:
        pauli_action(permutation)
    except NonPauli as error:
        second = dict(name='non_Pauli_Toffoli_permutation', outcome='DETECTED_NON_PAULI_IMAGE',
                      witness=dict(input_label=error.label, image=sparse_matrix(error.image)))
    else:
        raise ValueError('non-Pauli control was accepted')
    bad_counts = form_data(action, classifier=lambda f: (((f & 7) & (f >> 3)) & 6).bit_count() & 1)
    require(forms['records'][9]['fixed'] and forms['records'][9]['arf'] != bad_counts['records'][9]['arf'],
            'wrong-Arf actual fixed-form witness')
    third = rejected('omit_first_pair_from_Arf', lambda: check_forms(bad_counts), 'quadratic orbit sizes',
                     dict(actual_orbits=forms['orbit_sizes'], mutated_orbits=bad_counts['orbit_sizes'],
                          actual_fixed=forms['fixed_by_arf'], mutated_fixed=bad_counts['fixed_by_arf'],
                          actual_form9=forms['records'][9], mutated_form9=bad_counts['records'][9]))
    return [first, second, third]


def slab_controls(points, bounds):
    by_row = {row['row']: i for i, row in enumerate(points)}
    # Credited PR6794's fixed upper primal mixture; not its optimizer or verifier.
    weights = [(by_row[1], F(3, 4)), (by_row[2], F(1, 4))]
    reason, values = feasibility(points, weights, bounds)
    require(reason == 'order3 trace slab', 'credited old mixture must fail new slab')
    old_only = (bounds[0], bounds[1], F(-1), F(1))
    old_reason, old_values = feasibility(points, weights, old_only)
    require(old_reason is None, 'old one-trace mixture witness')
    other = [(by_row[2], F(1, 2)), (by_row[9], F(1, 2))]
    correct_reason, _ = feasibility(points, other, bounds)
    wrong_bounds = (bounds[0], bounds[1], F(-8, 28), F(16, 28))
    wrong_reason, wrong_values = feasibility(points, other, wrong_bounds)
    require(correct_reason == 'order3 trace slab' and wrong_reason is None, 'wrong16-fixed orbit-bound witness')
    return [dict(name='omit_order3_constraint', outcome='OLD_PRIMAL_ADMITTED_ONLY_AFTER_OMISSION',
                 witness=primal_record(points, weights, old_values), rejected_by=reason),
            dict(name='reuse_transvection_fixed16_for_order3', outcome='LOOSE_BOUND_ADMITS_FORBIDDEN_PRIMAL',
                 witness=primal_record(points, other, wrong_values), rejected_by=correct_reason,
                 correct_bounds=[rational(x) for x in bounds[2:]],
                 wrong_bounds=[rational(x) for x in wrong_bounds[2:]])]


def column_controls(table, width):
    wrong = extract_points(table, width, zcols=(31, 32))
    row = next(x for x in wrong if x['row'] == 2)
    return [rejected('transvection_column_used_as_order3', lambda: check_column_anchors(wrong),
                     'selected column anchors', dict(source_row=2, actual_wrong_T3=row['z'], expected_T3=4))]


def calculate():
    sources, identities = authenticate()
    small, g = selected_lift()
    lift = lift_checks(g)
    action = pauli_action(g)
    require(all(row['target'] == expected_label(row['label']) for row in action), 'selected symplectic action')
    fixed_vectors = sum(row['target'] == row['label'] for row in action)
    require(fixed_vectors == 16, 'six-bit fixed-space count')
    require(all(action[action[action[i]['target']]['target']]['target'] == i for i in range(64)),
            'order-three quotient action')
    forms = form_data(action)
    check_forms(forms)
    table, width = sources['source/table.json'], sources['source/width-nine-input.json']
    require(sources['source/EXTERNAL.json']['table_sha256'] == identities['source/table.json'], 'external table pin')
    points = extract_points(table, width)
    bind_classes(points, width)
    certificates = [lp_certificate(points, bounds_for(size, forms), size) for size in (28, 36)]
    lower = min(F(*cert['minimum']['objective']) for cert in certificates)
    upper = max(F(*cert['maximum']['objective']) for cert in certificates)
    require(lower > 0 and upper >= lower, 'positive spectral interval')
    scale = F(92897280, 8**10)
    condition = upper/lower
    faults = lifted_controls(g, action, forms) + slab_controls(points, bounds_for(28, forms))
    faults += column_controls(table, width)
    symplectic = [[(action[1 << j]['target'] >> i) & 1 for j in range(6)] for i in range(6)]
    return dict(status='PASS_CLIFFORD_ORDER3_CONDITIONING', schema_version=1, source_sha256=identities,
                source_programs_executed=False, selected_lift=dict(lift, g2=sparse_matrix(small),
                    quotient_matrix=symplectic, fixed_quotient_vectors=fixed_vectors),
                Pauli_action=action, quadratic_forms=forms,
                source_points=points, LP=certificates,
                multiplicity_ratio_interval=[rational(lower), rational(upper)],
                Gram_scale=rational(scale), Gram_interval=[rational(scale*lower), rational(scale*upper)],
                sufficient_condition_bound=rational(condition), credited_one_trace_bound=807,
                improves_credited_bound=condition < 807, controls=faults, control_count=len(faults),
                inherited_premises=['published quotient-character identification', 'width-nine multiplicities',
                    'even-sector decomposition/reciprocity', 'transvection bound16/N',
                    'order3 class5 identification', 'Pauli orbit/central phase rules', 'Schur propagation'],
                scope='Two-trace30-point relaxation; primal optima are not asserted actual irreducibles or spectrum.')


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
        print('FAIL_CLIFFORD_ORDER3_CONDITIONING: '+str(error), file=sys.stderr)
        raise SystemExit(1)
