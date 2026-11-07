"""Exact new Bell-congruence/orbit corroboration for two actual even blocks.

The five retained source objects are inert premises. No predecessor engine,
group enumeration, width-nine decomposition, order-three or LP replay is run.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
SOURCE_SHA = '51d69b9daeefb8ac8b9c530605e17dad60e35e426d31652928b1dff29582fd81'
SOURCE_PATHS = {'predecessor/PR6714-PROOF.md', 'predecessor/PR6794-PROOF.md',
                'source/table.json', 'source/width-nine-input.json', 'source/EXTERNAL.json'}
UNITS = ((1, 0), (0, 1), (-1, 0), (0, -1))
ZERO = (0, 0)
ONE = (1, 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'duplicate JSON key')
        result[key] = value
    return result


def no_number(text):
    raise ValueError('noninteger JSON number')


def load(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=no_number, parse_constant=no_number)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def authenticate():
    raw = (P / 'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA, 'source manifest bytes')
    manifest = load(raw)
    need(type(manifest['schema_version']) is int and manifest['schema_version'] == 1,
         'source manifest schema')
    files = manifest['files']
    need(len(files) == 5 and {r['local_path'] for r in files} == SOURCE_PATHS,
         'source inventory')
    result = {}
    for row in files:
        path = P / row['local_path']
        need(path.is_file() and not path.is_symlink(), 'source regular file')
        data = path.read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need((len(data), hashlib.sha256(data).hexdigest(), blob, row['mode']) ==
             (row['bytes'], row['sha256'], row['git_blob'], '100644'), 'source bytes')
        result[row['local_path']] = row['sha256']
    return result


def cadd(left, right):
    return left[0]+right[0], left[1]+right[1]


def cmul(left, right):
    return left[0]*right[0]-left[1]*right[1], left[0]*right[1]+left[1]*right[0]


def conjugate(value):
    return value[0], -value[1]


def blank():
    return [[ZERO for _ in range(8)] for _ in range(8)]


def identity():
    result = blank()
    for i in range(8):
        result[i][i] = ONE
    return result


def frozen(matrix):
    return tuple(tuple(row) for row in matrix)


def scale(matrix, scalar):
    return [[cmul(value, scalar) for value in row] for row in matrix]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def bar(matrix):
    return [[conjugate(value) for value in row] for row in matrix]


def adjoint(matrix):
    return transpose(bar(matrix))


def multiply(left, right):
    result = blank()
    for i in range(8):
        for k, value in enumerate(left[i]):
            if value != ZERO:
                for j, other in enumerate(right[k]):
                    if other != ZERO:
                        result[i][j] = cadd(result[i][j], cmul(value, other))
    return result


def difference(left, right):
    for i in range(8):
        for j in range(8):
            if left[i][j] != right[i][j]:
                return dict(row=i, column=j, left=left[i][j], right=right[i][j])
    return None


def parity(value):
    return value.bit_count() % 2


def omega(left, right):
    return parity((left & 7) & (right >> 3)) ^ parity((left >> 3) & (right & 7))


def quadratic(form, vector):
    return parity((vector & 7) & (vector >> 3)) ^ omega(vector, form)


def arf(form):
    return parity((form & 7) & (form >> 3))


def pauli(label, phase_override=None):
    a, b = label & 7, label >> 3
    phase = parity(a & b) if phase_override is None else phase_override
    result = blank()
    for x in range(8):
        result[x ^ a][x] = UNITS[(phase+2*parity(b & x)) % 4]
    return result


def generators():
    result = []
    for j in range(3):
        x, z = pauli(1 << j), pauli(8 << j)
        s = blank()
        rx = scale(identity(), (1, 1))
        for column in range(8):
            s[column][column] = UNITS[(column >> j) & 1]
            rx[column ^ (1 << j)][column] = (1, -1)
        result.extend([(f'X{j}', x, 1), (f'Z{j}', z, 1),
                       (f'S{j}', s, 1), (f'Rx{j}', rx, 2)])
    for control in range(3):
        for target in range(3):
            if control != target:
                matrix = blank()
                for column in range(8):
                    row = column ^ ((1 << target) if (column >> control) & 1 else 0)
                    matrix[row][column] = ONE
                result.append((f'CNOT{control}{target}', matrix, 1))
    result.append(('central_i', scale(identity(), (0, 1)), 1))
    need(len(result) == 19 and len({name for name, _, _ in result}) == 19,
         'generator inventory')
    for name, matrix, denominator in result:
        target = scale(identity(), (denominator*denominator, 0))
        need(multiply(matrix, adjoint(matrix)) == target == multiply(adjoint(matrix), matrix),
             'actual Gaussian-dyadic unitarity: '+name)
    return result


def transpose_guard(matrix, assigned_arf):
    need(transpose(matrix) == scale(matrix, UNITS[2*assigned_arf]),
         'transpose/Arf assignment')


def basis_checks(bells):
    characters, gram_digest, weight_digest = [], hashlib.sha256(), hashlib.sha256()
    for w, basis in enumerate(bells):
        transpose_guard(basis, arf(w))
        need(adjoint(basis) == basis and multiply(basis, basis) == identity(), 'Hermitian Bell basis')
        character = [quadratic(w, v) for v in range(64)]
        characters.append(character)
        for v, other in enumerate(bells):
            value = ZERO
            for i in range(8):
                for j in range(8):
                    value = cadd(value, cmul(conjugate(basis[i][j]), other[i][j]))
            need(value == ((8, 0) if v == w else ZERO), 'complete Bell orthogonality')
            gram_digest.update(canonical([w, v, value])+b'\n')
            actual = multiply(multiply(other, basis), transpose(other))
            need(actual == scale(basis, UNITS[2*character[v]]), 'actual Pauli weight line')
            weight_digest.update(canonical([w, v, character[v], actual])+b'\n')
    need(len({tuple(c) for c in characters}) == 64, 'distinct quadratic weight characters')
    orbits = [[w for w in range(64) if arf(w) == a] for a in (0, 1)]
    need([len(o) for o in orbits] == [36, 28], 'transpose orbit dimensions')
    return orbits, dict(distinct_form_vector_pairs=4096, literal_weight_line_cases=4096,
                        distinct_Bell_inner_products=4096, orthogonality_sha256=gram_digest.hexdigest(),
                        weight_line_sha256=weight_digest.hexdigest())


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length()-1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def matrix_trace(matrix):
    result = ZERO
    for i in range(8):
        result = cadd(result, matrix[i][i])
    return result


def square_traces(matrix, denominator, permutation, phases):
    natural_trace = matrix_trace(matrix)
    squared_trace = matrix_trace(multiply(matrix, matrix))
    tensor_trace = cmul(natural_trace, natural_trace)
    divisor = 2*denominator*denominator
    result = []
    for assigned_arf in (0, 1):
        sign = 1 if assigned_arf == 0 else -1
        numerator = cadd(tensor_trace, (sign*squared_trace[0], sign*squared_trace[1]))
        need(all(x % divisor == 0 for x in numerator), 'exact square-character denominator')
        expected = numerator[0]//divisor, numerator[1]//divisor
        actual = ZERO
        for w, target in enumerate(permutation):
            if target == w and arf(w) == assigned_arf:
                actual = cadd(actual, UNITS[phases[w]])
        need(actual == expected, 'literal Sym2/Lambda2 character identity')
        result.append(actual)
    return result


def signed_action(matrix, denominator, bells, lookup):
    labels, signs = [], []
    for basis in bells:
        actual = multiply(multiply(matrix, basis), adjoint(matrix))
        need(all(x % (denominator*denominator) == 0 for row in actual for pair in row for x in pair),
             'signed Pauli exact denominator')
        normalized = [[(a//(denominator*denominator), b//(denominator*denominator))
                       for a, b in row] for row in actual]
        need(frozen(normalized) in lookup, 'actual Pauli normalization')
        label, phase = lookup[frozen(normalized)]
        need(phase in (0, 2), 'Hermitian Pauli sign')
        labels.append(label)
        signs.append(1 if phase == 0 else -1)
    need(sorted(labels) == list(range(64)) and labels[0] == 0, 'Pauli label permutation')
    for u in range(64):
        for v in range(64):
            need(labels[u ^ v] == (labels[u] ^ labels[v]), 'symplectic map linearity')
            need(omega(labels[u], labels[v]) == omega(u, v), 'symplectic map pairing')
    return labels, signs


def congruence_action(matrix, denominator, bells, lookup):
    labels, phases = [], []
    for w, basis in enumerate(bells):
        actual = multiply(multiply(matrix, basis), transpose(matrix))
        divisor = denominator*denominator
        need(all(x % divisor == 0 for row in actual for pair in row for x in pair),
             'Bell congruence exact denominator')
        normalized = [[(a//divisor, b//divisor) for a, b in row] for row in actual]
        need(frozen(normalized) in lookup, 'Gaussian-unit Bell congruence')
        target, phase = lookup[frozen(normalized)]
        need(arf(w) == arf(target), 'congruence transpose orbit')
        labels.append(target)
        phases.append(phase)
    need(sorted(labels) == list(range(64)), 'Bell congruence permutation')
    return labels, phases


def generator_actions(items, bells):
    lookup = {}
    for label, basis in enumerate(bells):
        for phase, unit in enumerate(UNITS):
            key = frozen(scale(basis, unit))
            need(key not in lookup, 'distinct phased Bell basis')
            lookup[key] = label, phase
    result, intertwiner_digest = [], hashlib.sha256()
    for name, matrix, denominator in items:
        tau, signs = signed_action(matrix, denominator, bells, lookup)
        perm, phases = congruence_action(matrix, denominator, bells, lookup)
        traces = square_traces(matrix, denominator, perm, phases)
        for w, target in enumerate(perm):
            for v in range(64):
                need(quadratic(target, tau[v]) == quadratic(w, v), 'quadratic pullback permutation')
            left = scale(multiply(bar(matrix), adjoint(bells[w])), UNITS[phases[w]])
            right = multiply(adjoint(bells[target]), matrix)
            need(left == right, 'whole Vbar/Bell intertwiner')
            intertwiner_digest.update(canonical([name, w, target, phases[w], left])+b'\n')
        result.append(dict(name=name, denominator=denominator, numerator_sha256=digest(matrix),
                           Pauli_labels=tau, Pauli_signs=signs, Bell_labels=perm,
                           Bell_phase_exponents=phases, Sym2_Lambda2_traces=traces))
    return result, dict(generators=19, signed_Pauli_conjugations=19*64,
                        Bell_congruences=19*64, whole_matrix_intertwiners=19*64,
                        quadratic_transport_cases=19*64*64,
                        symplectic_linearity_pairs=19*64*64, symplectic_pairing_pairs=19*64*64,
                        distinct_square_character_checks=19*2,
                        intertwiner_sha256=intertwiner_digest.hexdigest())


def ordered_pair_orbits(orbits, actions):
    result = []
    for labels in orbits:
        seen, queue = {(labels[0], labels[1])}, [(labels[0], labels[1])]
        cursor = 0
        while cursor < len(queue):
            left, right = queue[cursor]
            cursor += 1
            for action in actions:
                perm = action['Bell_labels']
                pair = perm[left], perm[right]
                if pair not in seen:
                    seen.add(pair)
                    queue.append(pair)
        complete = {(left, right) for left in labels for right in labels if left != right}
        need(seen == complete, 'ordered-pair two-transitivity')
        result.append(dict(Arf=arf(labels[0]), dimension=len(labels),
                           ordered_distinct_pairs_reached=len(seen),
                           directed_generator_edges_checked=19*len(seen),
                           sorted_pair_sha256=digest(sorted(seen))))
    return result


def transvection_data(actions, orbits):
    action = next(a for a in actions if a['name'] == 'S0')
    tau, perm = action['Pauli_labels'], action['Bell_labels']
    need(all(tau[tau[v]] == v for v in range(64)), 'S0 quotient involution')
    need(sum(tau[v] == v for v in range(64)) == 32, 'S0 fixed-vector count')
    need(binary_rank([tau[1 << j] ^ (1 << j) for j in range(6)]) == 1,
         'S0 quotient transvection rank')
    fixed = [[w for w in orbit if perm[w] == w] for orbit in orbits]
    need([len(row) for row in fixed] == [16, 16], 'S0 fixed quadratic forms')
    return dict(generator='S0', fixed_Pauli_labels=32, quotient_rank_difference=1,
                fixed_forms_by_Arf=fixed, fixed_form_counts=[16, 16],
                actual_Sym2_Lambda2_traces=action['Sym2_Lambda2_traces'],
                nontrivial_permutation_character_values=[15, 15])


def row_guard(table, published_row, degree, transvection_value):
    row = table[published_row-1]
    need(row[0] == degree and all(row[c-1] == transvection_value for c in (31, 32, 33)),
         'source constituent degree/transvection identification')


def source_blocks(transvection):
    table = load((P / 'source/table.json').read_bytes())
    data = load((P / 'source/width-nine-input.json').read_bytes())
    external = load((P / 'source/EXTERNAL.json').read_bytes())
    chars, rows = table['characters'], data['quotient_source_rows']
    need(len(chars) == 67 and all(len(row) == 67 for row in chars), 'published table shape')
    need(all(type(v) is int for row in chars for v in row), 'published table integer entries')
    need(len(rows) == len(set(rows)) == 30 and all(type(r) is int and 1 <= r <= 67 for r in rows),
         'source quotient row labels')
    multiplicities = data['odd_tensor_multiplicities']['9']
    need(len(multiplicities) == 30 and all(type(m) is int and m >= 0 for m in multiplicities),
         'inherited width-nine multiplicity shape')
    need(data['quotient_source_classes'][13] == [31, 32, 33]
         and data['transvection_column_one_based'] == 14
         and data['quotient_class_sizes'][13] == 63 and data['fixed_dimensions'][13] == 5,
         'inherited transvection class binding')
    need(table['order'] == data['projective_order'] == 92897280, 'projective Gram order')
    need(external['table_sha256'] == hashlib.sha256((P/'source/table.json').read_bytes()).hexdigest(),
         'external table byte association')
    for r in rows:
        need(chars[r-1][30] == chars[r-1][31] == chars[r-1][32], 'quotient transvection fibre')
    inherited = dict(zip(rows, multiplicities))
    trivial = [r for r in rows if chars[r-1][0] == 1]
    need(trivial == [1] and inherited[1] == 269, 'inherited trivial width-nine row')
    blocks = []
    for dimension, value in zip((36, 28), transvection['nontrivial_permutation_character_values']):
        candidates = [r for r in rows if chars[r-1][0] == dimension-1 and chars[r-1][30] == value]
        need(len(candidates) == 1, 'unique source constituent row')
        r = candidates[0]
        row_guard(chars, r, dimension-1, value)
        multiplicity = inherited[1]+inherited[r]
        gram = Fraction(92897280*multiplicity, (8**10)*dimension)
        blocks.append(dict(actual_even_dimension=dimension, published_constituent_row=r,
                           quotient_constituent_degree=dimension-1, transvection_character=value,
                           inherited_m9_trivial=inherited[1], inherited_m9_constituent=inherited[r],
                           m_mu_at_width10=multiplicity, Gram_eigenvalue=[gram.numerator, gram.denominator],
                           regular_matrix_block_dimension=dimension*dimension))
    need([r['published_constituent_row'] for r in blocks] == [7, 6], 'published row convention')
    return blocks, chars, inherited


def rejected(name, callback, reason, witness):
    try:
        callback()
    except ValueError as error:
        need(str(error) == reason, 'wrong rejection reason: '+name)
        return dict(name=name, outcome='REJECTED_FOR_INTENDED_REASON', reason=reason, witness=witness)
    raise ValueError('control accepted: '+name)


def matrix_guard(left, right, reason):
    need(left == right, reason)


def convention_guard(label, matrix):
    need(matrix == pauli(label), 'wrong binary-dot Bell phase')


def controls(items, bells, actions, chars, inherited):
    central = next(a for a in actions if a['name'] == 'central_i')
    g = next(g for name, g, _ in items if name == 'central_i')
    phase = central['Bell_phase_exponents'][0]
    need(phase == 2 and central['Bell_labels'][0] == 0, 'actual central congruence phase')
    wrong = scale(multiply(g, adjoint(bells[0])), UNITS[phase])
    right = multiply(adjoint(bells[0]), g)
    result = [rejected('V_in_place_of_Vbar',
                       lambda: matrix_guard(wrong, right, 'Vbar conjugation is necessary'),
                       'Vbar conjugation is necessary', dict(generator='central_i', theta=UNITS[phase],
                       mismatch=difference(wrong, right)))]
    s = next(g for name, g, _ in items if name == 'S0')
    action = next(a for a in actions if a['name'] == 'S0')
    correct = multiply(multiply(s, bells[0]), transpose(s))
    wrong = multiply(multiply(s, bells[0]), adjoint(s))
    need(wrong == bells[0] and action['Bell_labels'][0] == 8, 'actual S0 congruence witness')
    result.append(rejected('conjugation_in_place_of_congruence',
                           lambda: matrix_guard(wrong, correct, 'Bell action requires congruence'),
                           'Bell action requires congruence', dict(generator='S0', input_form=0,
                           correct_form=8, wrong_form=0, mismatch=difference(wrong, correct))))
    result.append(rejected('degree_alone_selects_wrong_35', lambda: row_guard(chars, 8, 35, 15),
                           'source constituent degree/transvection identification',
                           dict(wrong_published_row=8, degree=chars[7][0], actual_Tt=chars[7][30],
                                required_Tt=15, inherited_m9=inherited[8], correct_row=7,
                                correct_m9=inherited[7])))
    result.append(rejected('Y_assigned_to_symmetric_Arf0', lambda: transpose_guard(bells[9], 0),
                           'transpose/Arf assignment', dict(form=9, actual_Arf=arf(9),
                           mismatch=difference(transpose(bells[9]), bells[9]))))
    alternate = pauli(27, ((27 & 7) & (27 >> 3)).bit_count() % 4)
    need(alternate != bells[27], 'multiple-Y convention witness')
    result.append(rejected('tensor_Y_gauge_mislabeled_as_binary_dot',
                           lambda: convention_guard(27, alternate), 'wrong binary-dot Bell phase',
                           dict(form=27, canonical_phase=0, tensor_Y_phase=2,
                           mismatch=difference(alternate, bells[27]),
                           scope='Serialization/basis-gauge guard; the alternate phased matrix is not an illegal group element.')))
    return result


def parser_controls():
    return [rejected('duplicate_JSON', lambda: load('{"x":1,"x":1}'), 'duplicate JSON key', {}),
            rejected('floating_JSON', lambda: load('{"x":1.0}'), 'noninteger JSON number', {}),
            rejected('nonfinite_JSON', lambda: load('{"x":NaN}'), 'noninteger JSON number', {})]


def calculate():
    sources = authenticate()
    bells = [pauli(w) for w in range(64)]
    items = generators()
    orbits, basis = basis_checks(bells)
    actions, action_counts = generator_actions(items, bells)
    pairs = ordered_pair_orbits(orbits, actions)
    transvection = transvection_data(actions, orbits)
    blocks, chars, inherited = source_blocks(transvection)
    return dict(status='PASS_CLIFFORD_QUADRATIC_ORBIT_BLOCKS', schema_version=1,
                source_sha256=sources, source_manifest_sha256=SOURCE_SHA,
                conventions=dict(base_ring='Z[i,1/2]', natural_dimension=8, center_order=4,
                                 label='a+8*b', Bell_phase='i^parity(a&b)',
                                 Q_w='parity(a_v&b_v)+omega(v,w) mod2',
                                 generator_alphabet='Xj,Zj,Sj,Rxj; six directed CNOT; central iI',
                                 intertwiner='theta*bar(g_num)*B_w^dagger=B_target^dagger*g_num'),
                basis_checks=basis, generator_action_counts=action_counts, generators=actions,
                transpose_orbits=[dict(Arf=a, dimension=len(o), labels=o) for a, o in enumerate(orbits)],
                ordered_pair_orbits=pairs, transvection=transvection, actual_width10_blocks=blocks,
                witnessed_controls=controls(items, bells, actions, chars, inherited),
                parser_controls=parser_controls(), predecessor_programs_executed=False,
                scope='New actual-generator/Bell and ordered-pair evidence for two blocks; inherited table/group/m9/reciprocity/Gram premises; no full spectrum or endpoint claim.')


def main():
    need(sys.argv[1:] in ([], ['--emit']), 'only optional --emit is supported')
    packet = calculate()
    if not sys.argv[1:]:
        need(canonical(load((P/'RESULT.json').read_bytes())) == canonical(packet),
             'retained complete result mismatch')
    print(canonical(packet).decode())


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print('FAIL_CLIFFORD_QUADRATIC_ORBIT_BLOCKS: '+str(error), file=sys.stderr)
        raise SystemExit(1)
