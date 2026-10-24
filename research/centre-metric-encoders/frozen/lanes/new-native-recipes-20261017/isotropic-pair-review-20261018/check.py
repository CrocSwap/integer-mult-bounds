#!/usr/bin/env python3
"""Check the common port gauge with exact sparse Gaussian columns."""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / 'coherent-port/isotropic-pair-gauge-20261018'
H6 = LANES / 'oblique-native-20261017/radical-centre-carry'
PINS = {
    'GAUGE.md': '17f7fcb6d67499f2d0280d1c49b0c0d01076ec839b620d0a82b8ce6de3e3395b',
    'check_isotropic_gauge.py': 'fdab75d06215e6dc1215d8aaf6737443be0c5b4fe3ad8088ff95c5d9221c730d',
    'GAUGE-PROGRAMS.json': '20f14f021623761160b0ef461904b38f82efdc7dd0c4008271620415bf747701',
    'CHECKS.json': '4ef0a622416d46a2ccab39d6f87a2e67be82fdbbe0e6d7cc0e0e0bac5e0ad0c3',
}
INPUTS = {}


def need(value, label):
    if not value:
        raise ValueError(label)


def read(path, expected=None, compressed=False):
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    content = gzip.decompress(raw) if compressed else raw
    need(expected is None or sha256(content).hexdigest() == expected, 'Input pin: '+str(path))
    INPUTS[str(path.relative_to(LANES))] = {'sha256': digest}
    if compressed:
        INPUTS[str(path.relative_to(LANES))]['decompressed_sha256'] = sha256(content).hexdigest()
    return content


def frozen(path, pin):
    record = json.loads(read(path/'FREEZE.json', pin))
    for name, digest in record['files'].items():
        read(path/name, digest)
    return record


def rotate(r, i, power):
    return ((r, i), (-i, r), (-r, -i), (i, -r))[power % 4]


def phase_at(rows, linear, x):
    exponent = sum(value for j, value in enumerate(linear) if x & (1 << j))
    for j, row in enumerate(rows):
        if x & (1 << j):
            exponent += 2*((row & x) >> (j+1)).bit_count()
    return exponent % 4


def compile_circuit(circuit, n=9):
    """Combine adjacent address and phase tables, without a Clifford tableau."""
    size = 1 << n
    mapping, phases = list(range(size)), [0]*size
    output = []

    def flush():
        nonlocal mapping, phases
        if mapping != list(range(size)) or any(phases):
            output.append(('M', tuple(mapping), tuple(phases)))
        mapping, phases = list(range(size)), [0]*size

    for event in circuit:
        kind = event[0]
        if kind == 'C':
            flush()
            need(0 <= event[1] < size and event[2] in (-1, 1), 'Literal C gate')
            output.append(tuple(event))
            continue
        if kind == 'P':
            rows = event[1]
            need(len(rows) == n and all(0 <= r < size for r in rows), 'Address matrix')
            image = [sum(((r & x).bit_count() % 2) << j for j, r in enumerate(rows))
                     for x in range(size)]
            need(sorted(image) == list(range(size)), 'Address matrix is a permutation')
            mapping = [image[x] for x in mapping]
        elif kind == 'X':
            mapping = [x ^ event[1] for x in mapping]
        elif kind in ('D', 'phase'):
            powers = ([event[1] % 4]*size if kind == 'phase' else
                      [phase_at(event[1], event[2], x) for x in range(size)])
            phases = [(p+powers[x]) % 4 for p, x in zip(phases, mapping)]
        else:
            raise ValueError(event)
    flush()
    return output


def inverse(compiled):
    result = []
    for event in reversed(compiled):
        if event[0] == 'C':
            result.append(('C', event[1], -event[2]))
        else:
            image, phase = event[1:]
            back, powers = [0]*len(image), [0]*len(image)
            for x, y in enumerate(image):
                back[y], powers[y] = x, -phase[x] % 4
            result.append(('M', tuple(back), tuple(powers)))
    return result


def normalized(state, denominator):
    state = {x: value for x, value in state.items() if value != (0, 0)}
    if not state:
        return {}, 0
    bits = 0
    for real, imag in state.values():
        bits |= abs(real) | abs(imag)
    shift = min(denominator, (bits & -bits).bit_length()-1)
    return ({x: (real >> shift, imag >> shift) for x, (real, imag) in state.items()},
            denominator-shift)


def run(compiled, column):
    state, denominator = {column: (1, 0)}, 0
    for event in compiled:
        if event[0] == 'M':
            image, phases = event[1:]
            state = {image[x]: rotate(real, imag, phases[x])
                     for x, (real, imag) in state.items()}
        else:
            _, v, sign = event
            moved = {}
            for x, (real, imag) in state.items():
                for y, value in ((x, (real-sign*imag, imag+sign*real)),
                                 (x ^ v, (real+sign*imag, imag-sign*real))):
                    old = moved.get(y, (0, 0))
                    moved[y] = (old[0]+value[0], old[1]+value[1])
            state = {x: value for x, value in moved.items() if value != (0, 0)}
            denominator += 1
    return normalized(state, denominator)


def monomial(record):
    need(set(record) == {'matrix_rows', 'quadratic_rows', 'linear_Z4', 'offset', 'phase'},
         'Complete monomial record')
    return [['D', record['quadratic_rows'], record['linear_Z4']],
            ['P', record['matrix_rows']], ['X', record['offset']], ['phase', record['phase']]]


def recipe(record):
    rank = record['rank']
    need(0 <= rank <= 9, 'Native rank')
    before = [] if record['right'] is None else monomial(record['right'])
    return compile_circuit(before + [['C', 1 << j, 1] for j in range(rank)]
                           + monomial(record['left']))


def compare(left, right, label, support=None):
    digest = sha256()
    coefficients = 0
    for x in range(512):
        actual, expected = run(left, x), run(right, x)
        need(actual == expected, label+' column '+str(x))
        if support is not None:
            need(len(actual[0]) == support, label+' support')
        coefficients += len(actual[0])
        digest.update(json.dumps([x, actual[1], sorted(actual[0].items())], separators=(',', ':')).encode())
    return {'spatial_columns': 512, 'nonzero_coefficients': coefficients, 'digest': digest.hexdigest()}


def gauge(n, a, b):
    size = 1 << n
    phase = ('M', tuple(range(size)), tuple((b & x).bit_count() % 2 for x in range(size)))
    return [phase, ('C', a, 1), phase]


def span(vectors):
    values = {0}
    for vector in vectors:
        values |= {x ^ vector for x in values}
    return values


def canonical(vectors, n=9):
    """Build the declared chart from a truth-table inverse of its address map."""
    rank, size = len(vectors), 1 << n
    need(len(span(vectors)) == 1 << rank, 'Independent declared frame basis')
    if rank == n:
        return [('C', 1 << j, 1) for j in range(n)]
    if not rank:
        return []
    columns = list(vectors)
    for vector in (1 << j for j in range(n)):
        if vector not in span(columns):
            columns.append(vector)
    need(len(columns) == n, 'Complete chart basis')
    image = []
    for x in range(size):
        y = 0
        for j, column in enumerate(columns):
            if x & (1 << j):
                y ^= column
        image.append(y)
    back = [0]*size
    for x, y in enumerate(image):
        back[y] = x
    inverse_columns = [back[1 << j] for j in range(n)]
    quadratic = [(1 << j) ^ sum(((v & w).bit_count() % 2) << k
                                for k, w in enumerate(inverse_columns))
                 for j, v in enumerate(inverse_columns)]
    linear = [(row >> j) & 1 for j, row in enumerate(quadratic)]
    K = [('M', tuple(image), tuple(phase_at(quadratic, linear, y) for y in image))]
    return inverse(K)+[('C', 1 << j, 1) for j in range(rank)]+K


def formula(n, a, b, q, x):
    t, u = (b & q).bit_count() % 2, (b & x).bit_count() % 2
    q0 = q ^ (a if t else 0)
    return {x ^ (q0 if u else 0): rotate(1, 0, (2*t-1)*u)}, 0


def general_checks():
    counts = {}
    for n in range(1, 5):
        total = 0
        for a in range(1, 1 << n):
            for b in range(1, 1 << n):
                if (a & b).bit_count() % 2 != 1:
                    continue
                w = gauge(n, a, b)
                for q in range(1 << n):
                    circuit = inverse(w)+[('C', q ^ a, -1), ('C', q, 1)]+w
                    for x in range(1 << n):
                        need(run(circuit, x) == formula(n, a, b, q, x), 'General pair formula')
                        total += 1
        counts[n] = total
    w = gauge(9, 45, 1)
    for q in range(512):
        circuit = inverse(w)+[('C', q ^ 45, -1), ('C', q, 1)]+w
        for x in range(512):
            need(run(circuit, x) == formula(9, 45, 1, q, x), 'Every local direction')
    for x in range(512):
        need(run(w+w, x) == ({x: (0, 1)}, 0), 'Exact square phase')
    for v in range(512):
        need((run(w+[('C', v, 1)], 0) == run([('C', v, 1)]+w, 0)) == (v & 1 == 0),
             'Exact pure-C continuation criterion')
    # This shear is not orthogonal. Covectors use the inverse transpose.
    chart = compile_circuit([['P', [3, 2]]], 2)
    transported = inverse(chart)+gauge(2, 1, 1)+chart
    dual_action = gauge(2, 1, 3)
    for x in range(4):
        need(run(transported, x) == run(dual_action, x), 'General chart dual action')
    need(any(run(transported, x) != run(gauge(2, 1, 1), x) for x in range(4)),
         'Naive covector action rejects for a non-orthogonal chart')
    # Two two-bit columns check the tensor phase separately.
    for q in range(4):
        tensor = []
        wg = []
        for shift in (0, 2):
            local = gauge(4, 3 << shift, 1 << shift)
            tensor += inverse(local)+[('C', (q ^ 3) << shift, -1), ('C', q << shift, 1)]+local
            wg += local
        for x in range(16):
            y, phase = 0, 0
            for shift in (0, 2):
                value = (x >> shift) & 3
                t, u = q & 1, value & 1
                y |= (value ^ ((q ^ (3 if t else 0)) if u else 0)) << shift
                phase += (2*t-1)*u
            need(run(tensor, x) == ({y: rotate(1, 0, phase)}, 0), 'Tensor pair phase')
            need(run(wg+wg, x) == ({x: (-1, 0)}, 0), 'Tensor square phase i squared')
    print('general formula and tensor phases PASS', flush=True)
    return {'all_parameters_dimensions_1_to_4': counts, 'all_nine_bit_q_columns': 512*512,
            'tensor_width_two_columns': 64, 'pure_C_continuation_directions': 512,
            'nonorthogonal_chart_columns': 4}


def transition_checks():
    counts = {}
    for n in range(1, 5):
        parameters = [(a, b) for a in range(1, 1 << n) for b in range(1, 1 << n)
                      if (a & b).bit_count() % 2]
        gauges = {(a, b): gauge(n, a, b) for a, b in parameters}
        total = 0
        for a1, b1 in parameters:
            for a2, b2 in parameters:
                op = inverse(gauges[a1, b1])+gauges[a2, b2]
                for x in (range(1 << n) if n <= 3 else (0,)):
                    u1, u2 = (b1 & x).bit_count() % 2, (b2 & x).bit_count() % 2
                    if a1 == a2:
                        delta = u1 ^ u2
                        expected = ({x ^ (a1 if delta else 0): ((-1)**(u1*delta), 0)}, 0)
                    else:
                        cross = (b2 & a1).bit_count() % 2
                        expected = ({x: ((-1)**(u1+u2), 0),
                                     x ^ a2: ((-1)**u1, 0),
                                     x ^ a1: ((-1)**(u2+cross), 0),
                                     x ^ a1 ^ a2: (1, 0)}, 1)
                    need(run(op, x) == expected, 'Exact transition formula and global phase')
                    need(len(expected[0]) == (1 if a1 == a2 else 4), 'Transition support criterion')
                    total += 1
        counts[n] = total
    print('general transition formula and rank obstruction PASS', flush=True)
    return {'dimensions_1_to_3_all_columns_and_dimension_4_zero_column': counts,
            'same_radical_rank': 0, 'distinct_radicals_rank': 2}


def source_binding(packet, h6, signed, core, geometry):
    labels = next(iter(core['providers'].values()))['canonical']['ports']
    need(all(p['canonical']['ports'] == labels for p in core['providers'].values()), 'Provider labels')
    large = signed['large_ports']
    need(sorted(row['port'] for row in packet['monomials']) == sorted(large), 'All actual centre ports')
    need([p for p, q in enumerate(labels) if (q & 45).bit_count() % 2 == 0] == sorted(large),
         'Exactly the actual radical-perpendicular ports')
    need(sorted(tuple(row['ports']) for row in packet['left_coded_pair_plane_tails']) ==
         sorted(tuple(row['ports']) for row in geometry['pair_edges']), 'Actual pair planes')
    source_rows = packet['left_coded_source_tails']
    target_rows = {row['port']: row for row in packet['left_coded_tails']}
    routes = {}
    for provider, record in h6['providers'].items():
        for direction, word in record.items():
            need(word['frames'][word['carry_frame']] == [45], 'Actual canonical carry frame')
            need(len(word['centre_frames']) == 8, 'Eight source frames')
            for j, frame in enumerate(word['centre_frames']):
                need(span(word['frames'][frame]) == span(source_rows[j]['frame_basis']),
                     'Actual centre subspace binding')
            flags = [False]*640
            changed = Counter()
            endpoint = {(r['role'], r['port']): r for r in word['endpoint_adapters']}
            checks = []
            for event in word['events']:
                if event[0] == 'native':
                    _, field, before, after, rank, key = event
                    need(not flags[field], 'No later native call on a coded source')
                    if field in large and after == 1:
                        j = word['centre_frames'].index(before)
                        need(rank == 2, 'Old source exit rank')
                        flags[field] = True
                        changed['source_2_to_1'] += 1
                    elif 112 <= field < 224 and field-112 in large and before == word['carry_frame']:
                        p = field-112
                        need(after == endpoint['target', p]['frame'] and rank == 7,
                             'Old target exit and endpoint adapter')
                        flags[field] = True
                        changed['target_7_to_6'] += 1
                        checks.append((p, word['native_recipes'][key], endpoint['target', p]))
                elif event[0] == 'scalar':
                    op = event[1]
                    if op[0] in ('add', 'copy'):
                        need(flags[op[1]] == flags[op[2]], 'Common W commutes with remaining scalar graph')
                    elif op[0] == 'clear':
                        need(not flags[op[1]], 'No coded field is cleared')
                    else:
                        need(op[0] == 'scale', 'Known scalar operation')
                elif event[0] == 'set_empty_frame':
                    need(not flags[event[1]], 'No coded frame reset')
                else:
                    raise ValueError(event)
            need(changed == {'source_2_to_1': 48, 'target_7_to_6': 48}, 'All changed exits')
            need({i for i, flag in enumerate(flags) if flag} == set(large) | {112+p for p in large},
                 'Exactly two coded centre banks, with helpers unchanged')
            routes[provider+'/'+direction] = {'changed_exits': dict(changed), 'coded_fields': 96,
                                              'coded_borrowed_fields': 0,
                                              'literal_source_basis_equal': [word['frames'][f] == source_rows[j]['frame_basis']
                                                                             for j, f in enumerate(word['centre_frames'])]}
            if provider == 'base' and direction == 'forward':
                routes['_target_checks'] = checks
                routes['_carry_recipe'] = word['native_recipes']['0:'+str(word['carry_frame'])]
                routes['_source_old'] = [word['native_recipes'][str(frame)+':1']
                                         for frame in word['centre_frames']]
    return labels, routes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    for name, pin in PINS.items():
        read(SOURCE/name, pin)
    read(SOURCE/'FREEZE.json', '3c1669513029238abf181d4137b7a25efd4113c951ac78301a9da2c7e9df6ec1')
    packet = json.loads(read(SOURCE/'GAUGE-PROGRAMS.json', PINS['GAUGE-PROGRAMS.json']))
    receipt = json.loads(read(SOURCE/'CHECKS.json', PINS['CHECKS.json']))
    need(receipt['program_sha256'] == PINS['GAUGE-PROGRAMS.json'], 'Receipt packet binding')
    dependencies = {}
    for name, (kind, pin) in packet['pins'].items():
        raw = read(LANES/name, pin, kind == 'gzip')
        if name.endswith(('.json', '.gz')):
            dependencies[name] = json.loads(raw)
    frozen(H6, 'a1b0ec7bbead298e1484199b15896e2b5b688d53b3f2f5d9e0d73c29bea04a80')
    h6 = json.loads(read(H6/'RADICAL-CENTRE-PROGRAM.json.gz',
                        '25ddd47640a98e61b5edf5f36e2aad9867eab00e072545322bb36e4d63c561ea', True))
    h6_binding_pins = {
        'H6-SOURCE-PROGRAMS.json': '4eb739a9191aaba6b8c15a2c10868ceba80c4596000eca50c8f68f29c527e569',
        'bind_h6_sources.py': '150453ca6e3bd75bdfab1805def824c44c34e83037b6996ff355d493de26686b',
        'H6-SOURCE-CHECKS.json': 'cb5a9d3b4f83b4718ec70bdd5473d55cc25d3c3078d696f6f6504862c6443e7e',
        'H6-SOURCE-BINDING.md': '7a3a9313f6c8b01dc5a2dc2aa156abb109ad624d25cf92f9aa0dc0b57d11d783',
    }
    for name, pin in h6_binding_pins.items():
        read(SOURCE/name, pin)
    actual_sources = json.loads(read(SOURCE/'H6-SOURCE-PROGRAMS.json', h6_binding_pins['H6-SOURCE-PROGRAMS.json']))
    read(SOURCE/'H6-SOURCE-FREEZE.json', 'cf436b1016f7d9c5b933eb818098ff0339436fec20d0ed497045fc992e6ee0b5')
    matching_freeze = json.loads(read(SOURCE/'MATCHING-EXITS-FREEZE.json',
                                      '9d5e63259b861bf69ac5e00b2ec9ad3158aec3edac4ce54e08fcf33249f137be'))
    for name, pin in matching_freeze['pins'].items():
        read(SOURCE/name, pin)
    matching = json.loads(read(SOURCE/'MATCHING-EXITS-PROGRAMS.json',
                               '89ce6c4b426498e2fb9e7dfce9a4a192e3183644fef457c5b357baf63b9c6276'))
    signed = dependencies['controller-followthrough-20261017/bipartite-eight-20261018/BIPARTITE-EIGHT-PROGRAM.json.gz']
    core = dependencies['new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz']
    geometry = dependencies['controller-followthrough-20261017/partial-orthogonal/SYMMETRIC-FAMILY.json']
    labels, routes = source_binding(packet, h6, signed, core, geometry)
    results = {'general': general_checks(), 'transitions': transition_checks()}
    W, Z = compile_circuit(packet['W']['circuit']), compile_circuit(packet['canonical_Z'])
    need(Z == canonical([45]), 'Independent construction of the exact canonical Z')
    FULL = [('C', 1 << j, 1) for j in range(9)]
    need(packet['n'] == 9 and packet['a'] == 45 and packet['b'] == 1, 'Actual gauge parameters')
    results['W'] = compare(W, gauge(9, 45, 1), 'Literal W', 2)
    need(packet['W']['native_recipe']['rank'] == 1, 'Native W rank')
    results['W_recipe'] = compare(recipe(packet['W']['native_recipe']), W, 'W native recipe', 2)
    results['canonical_carry_binding'] = compare(recipe(routes.pop('_carry_recipe')), Z, 'Actual canonical Z', 2)
    results['alignments'] = {}
    for name, intended in [('W_Z_inverse', inverse(Z)+W), ('Z_inverse_W', W+inverse(Z))]:
        row = packet['alignments'][name]
        actual = compile_circuit(monomial(row['record']))
        need(actual == compile_circuit(row['circuit']), 'Serialized alignment circuit')
        results['alignments'][name] = compare(actual, intended, name, 1)
    results['pairs'] = []
    for row in packet['monomials']:
        p, q = row['port'], row['q']
        need(q == labels[p] and row['q_partner'] == q ^ 45, 'Actual pair labels')
        t, q0 = q & 1, q ^ (45 if q & 1 else 0)
        need(row['q0'] == q0 and row['phase_coefficient'] == 2*t-1, 'Formula fields')
        need(row['matrix_rows'] == [(1 << j) ^ (1 if q0 >> j & 1 else 0) for j in range(9)],
             'Formula address matrix')
        canonical_pair = inverse(Z)+[('C', q ^ 45, -1), ('C', q, 1)]+Z
        results['pairs'].append({'port': p, **compare(compile_circuit(monomial(row['canonical_record'])),
                                                    canonical_pair, 'Canonical pair '+str(p), 1)})
    print('canonical gauge and all actual pairs PASS', flush=True)
    results['target_tails'] = []
    old_targets = {p: (old, adapter) for p, old, adapter in routes.pop('_target_checks')}
    for row in packet['left_coded_tails']:
        p, q = row['port'], row['q']
        need(q == labels[p] and row['recipe']['rank'] == row['left_coded_rank'] == 6 and
             row['right_coded_rank'] == 8, 'Target rank declarations')
        expected = inverse(Z)+[('C', q, -1)]+FULL+W
        actual = recipe(row['recipe'])
        need(actual == compile_circuit(row['circuit']), 'Native target serialization')
        entry = {'port': p, **compare(actual, expected, 'Left target '+str(p), 64)}
        right = inverse(Z)+W+[('C', q, -1)]+FULL
        for x in range(512):
            need(len(run(right, x)[0]) == 256, 'Right-coded rank eight on every column')
        old, adapter = old_targets[p]
        intended_old = inverse(Z)+[('C', q, -1)]+FULL
        entry['old_endpoint_binding'] = compare(recipe(old)+inverse(recipe(adapter)), intended_old,
                                                'Actual old target exit '+str(p), 128)
        need(run(actual, 0) != run(right, 0), 'Wrong W order rejects')
        need(run(actual+[('M', tuple(range(512)), (2,)*512)], 0) != run(expected, 0),
             'Wrong global sign rejects')
        results['target_tails'].append(entry)
        if len(results['target_tails']) % 8 == 0:
            print('target tails', len(results['target_tails']), 'PASS', flush=True)
    results['source_tails'] = []
    old_sources = routes.pop('_source_old')
    for row, old in zip(packet['left_coded_source_tails'], old_sources):
        source = compile_circuit(row['source_frame'])
        need(source == canonical(row['frame_basis']), 'Source frame and exact ordered basis')
        need(row['recipe']['rank'] == row['new_rank'] == 1 and row['old_rank'] == 2,
             'Source rank declarations')
        need(recipe(row['recipe']) == compile_circuit(row['circuit']), 'Native source serialization')
        entry = {'vertex': row['vertex'], **compare(recipe(row['recipe']), inverse(source)+FULL+W,
                                                   'Source tail '+str(row['vertex']), 2)}
        actual_old, claimed_old = recipe(old), inverse(source)+FULL
        mismatches = []
        for x in range(512):
            if run(actual_old, x) != run(claimed_old, x):
                mismatches.append(x)
            need(len(run(actual_old+W, x)[0]) == 2, 'Actual coded H6 source rank one')
        entry['h6_operator_binding'] = {'equal_columns': 512-len(mismatches),
                                       'first_mismatch': next(iter(mismatches), None),
                                       'actual_W_completed_support': 2}
        results['source_tails'].append(entry)
    results['pair_plane_tails'] = []
    for row in packet['left_coded_pair_plane_tails']:
        p, r = row['ports']
        need(labels[p] ^ labels[r] == 45 and row['recipe']['rank'] == row['new_rank'] == 6 and
             row['old_rank'] == 7, 'Actual pair plane and ranks')
        source = compile_circuit(row['source_frame'])
        need(source == canonical(row['frame_basis']), 'Pair plane and exact ordered basis')
        need(recipe(row['recipe']) == compile_circuit(row['circuit']), 'Native plane serialization')
        entry = {'ports': [p, r], **compare(recipe(row['recipe']), inverse(source)+FULL+W,
                                          'Pair plane '+str(p), 64)}
        for x in range(512):
            need(len(run(inverse(source)+FULL, x)[0]) == 128, 'Old pair-plane rank seven')
        results['pair_plane_tails'].append(entry)
    print('source tails and pair planes PASS', flush=True)
    results['actual_h6_sources'] = []
    need(len(actual_sources['recipes']) == 16, 'Both actual providers and eight source vertices')
    seen = set()
    for row in actual_sources['recipes']:
        provider, j = row['provider'], row['vertex']
        need((provider, j) not in seen, 'Unique actual source recipe')
        seen.add((provider, j))
        word = h6['providers'][provider]['forward']
        frame = word['centre_frames'][j]
        need(row['frame_id'] == frame and row['frame_basis'] == word['frames'][frame],
             'Exact actual H6 frame')
        need(compile_circuit(row['frame_circuit']) == canonical(row['frame_basis']),
             'Independent actual source canonical frame')
        need(row['recipe']['rank'] == 1 and recipe(row['recipe']) == compile_circuit(row['circuit']),
             'Actual one-child source recipe')
        for direction in ('forward', 'backward'):
            other = h6['providers'][provider][direction]
            need(other['frames'][other['centre_frames'][j]] == row['frame_basis'] and
                 other['native_recipes'][str(frame)+':1'] == word['native_recipes'][str(frame)+':1'],
                 'Both orientation source records are identical')
        old = recipe(word['native_recipes'][str(frame)+':1'])
        results['actual_h6_sources'].append({'provider': provider, 'vertex': j,
                                             **compare(recipe(row['recipe']), old+W, 'Actual source binding', 2)})
    print('actual H6 source binding PASS', flush=True)
    need(matching['gauge_freeze_sha256'] == '3c1669513029238abf181d4137b7a25efd4113c951ac78301a9da2c7e9df6ec1',
         'Matching gauge dependency')
    need(matching['source_pins'] == packet['pins'], 'Same matching source pins')
    results['matching_targets'] = []
    need(len(matching['target_exits']) == 48, 'All matching target exits')
    for row in matching['target_exits']:
        p, pair = row['port'], row['pair']
        need(p in pair and tuple(pair) in {tuple(e['ports']) for e in geometry['pair_edges']},
             'Actual matching pair and target')
        perpendicular = {x for x in range(512) if all((x & labels[z]).bit_count() % 2 == 0 for z in pair)}
        need(span(row['input_frame_basis']) == perpendicular and len(row['input_frame_basis']) == 7,
             'Exact pair-perpendicular subspace')
        source = compile_circuit(row['input_frame'])
        need(source == canonical(row['input_frame_basis']), 'Literal matching input frame')
        expected = inverse(source)+[('C', labels[p], -1)]+FULL+W
        actual = compile_circuit(monomial(row['record']))
        need(actual == compile_circuit(row['circuit']) and row['new_rank'] == 0 and row['old_rank'] == 1,
             'Matching monomial record')
        results['matching_targets'].append({'port': p, **compare(actual, expected, 'Matching target', 1)})
        need(len(run(expected+inverse(W), 0)[0]) == 2, 'Old matching target rank one')
    orders = [[] for _ in range(8)]
    for edge in geometry['pair_edges']:
        for vertex, port in zip(edge['vertices'], edge['ports']):
            orders[vertex].append(port)
    need(all(len(order) == 6 for order in orders), 'Actual six-carrier cyclic orders')
    results['cyclic_sources'] = []
    need(len(matching['cyclic_source_exits']) == 48, 'All cyclic source exits')
    for row in matching['cyclic_source_exits']:
        vertex, p = row['vertex'], row['carrier']
        order = orders[vertex]
        index = order.index(p)
        five = [order[(index+j) % 6] for j in range(5)]
        need(row['cyclic_order'] == order and row['five_ports'] == five, 'Exact cyclic source order')
        need(span(row['input_frame_basis']) == span([45]+[labels[q] for q in five]) and
             len(row['input_frame_basis']) == 6, 'Actual cyclic source subspace')
        source = compile_circuit(row['input_frame'])
        need(source == canonical(row['input_frame_basis']), 'Literal cyclic input frame')
        actual = recipe(row['recipe'])
        need(actual == compile_circuit(row['circuit']) and row['new_rank'] == row['recipe']['rank'] == 2 and
             row['old_rank'] == 3, 'Cyclic native record')
        results['cyclic_sources'].append({'vertex': vertex, 'carrier': p,
                                         **compare(actual, inverse(source)+FULL+W, 'Cyclic source', 4)})
        need(len(run(inverse(source)+FULL, 0)[0]) == 8, 'Old cyclic source rank three')
    print('matching and cyclic exit phases PASS', flush=True)
    control = receipt['width_two_control']
    q, chars = control['q'], control['characters']
    need(len(chars) == 2 and all((45 & x).bit_count() % 2 == 1 for x in chars), 'Width-two characters')
    exponent = sum(((q & x).bit_count() % 2)-(((q ^ 45) & x).bit_count() % 2) for x in chars) % 4
    need(exponent == 2 and sum((45 & x).bit_count() % 2 for x in chars) % 2 == 0,
         'Simultaneous translation shortcut rejects')
    old_profile = Counter()
    for event in h6['providers']['base']['forward']['events']:
        if event[0] == 'native':
            old_profile[event[4]] += 1
    new_profile = old_profile.copy()
    new_profile[2] -= 48; new_profile[1] += 48
    new_profile[7] -= 48; new_profile[6] += 48
    results.update(status='PASS', routes=routes, source_pins=PINS,
                   h6_route_delta={'old_profile': dict(sorted(old_profile.items())),
                                   'new_profile': {k:v for k,v in sorted(new_profile.items()) if v},
                                   'old_mass': sum(k*v for k,v in old_profile.items()),
                                   'new_mass': sum(k*v for k,v in new_profile.items()),
                                   'children': sum(new_profile.values()), 'scalar_graph_delta': 0,
                                   'scope': 'The target replacement and corrected source recipes are bound to H6. Replace each selected target native exit together with its inverse endpoint adapter. The structural replacement gives W on 96 centre-bank outputs. Native side-map execution and complete supplier costs remain open.'},
                   negative_controls={'wrong_W_order':48, 'wrong_global_sign':48,
                                      'tensor_simultaneous_translation':1},
                   phase_method='Sparse exact Gaussian columns; no producer or Clifford compiler import.')
    for name, value in [('REVIEW.json', results), ('INPUTS.json', INPUTS)]:
        (args.output/name).write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')
    print('PASS_ISOTROPIC_PAIR_INDEPENDENT_REVIEW', flush=True)


if __name__ == '__main__':
    main()
