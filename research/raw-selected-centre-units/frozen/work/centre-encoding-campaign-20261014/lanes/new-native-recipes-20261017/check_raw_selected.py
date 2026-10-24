#!/usr/bin/env python3
"""Review the raw selected local maps with a separate exact interpreter."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import importlib.util
import json
import shutil
import time

HERE = Path(__file__).resolve().parent
LANES = HERE.parent
ROOT = LANES.parents[2]
SOURCE = LANES / 'native-escape-20261017'
A = (0, 7, 20, 27, 36, 46, 57, 111)
U = tuple(p for p in range(112) if p not in A)
CORE_PIN = 'fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877'
WORD_PIN = '16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219'
INTERFACE_PIN = '5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3'
KERNEL_PACKET_PIN = '17122a343fb8a3dd804b2d7042d523aa209d0684447cdba63d84cc5561b6144f'
PACKET_PINS = {
    'RAW-SELECTED-BACKWARD': '0d3280c6ad7ce79fba15bc6ff53e32fff1de75d8c17113c6174799e544e6103f',
    'RAW-SELECTED-FORWARD': '92d66da6d103963f8727b5e2ecb85f5cb48a220f870d36c433b6b3c6803b7cc9',
    'ZERO-LINE-BACKWARD': 'b02395d076f2ab3956f35de863109fbabe0ab7dc1c5e8199024045679a1a1727',
}
INPUTS = {}


def need(condition, label):
    if not condition:
        raise ValueError(label)


def hashed(path, pin=None, zipped=False):
    raw = path.read_bytes()
    content = gzip.decompress(raw) if zipped else raw
    key = str(path.relative_to(ROOT))
    record = {'sha256': hashlib.sha256(raw).hexdigest()}
    if zipped:
        record['decompressed_sha256'] = hashlib.sha256(content).hexdigest()
    need(pin is None or hashlib.sha256(content).hexdigest() == pin, 'Input pin: ' + key)
    INPUTS[key] = record
    return content


def load(path, pin=None, zipped=False):
    return json.loads(hashed(path, pin, zipped))


def acc(target, source, coefficient=Q(1)):
    for key, value in source.items():
        result = target.get(key, 0) + coefficient * value
        if result:
            target[key] = result
        else:
            target.pop(key, None)


def rank(vectors):
    basis = {}
    for x in vectors:
        while x:
            lead = x.bit_length() - 1
            if lead not in basis:
                basis[lead] = x
                break
            x ^= basis[lead]
    return len(basis)


def register(wire):
    kind, index = wire
    need(kind in ('L', 'C'), 'Core register namespace')
    need(0 <= index < (704 if kind == 'L' else 8), 'Core register range')
    return index + (704 if kind == 'C' else 0)


def price(kind, coefficient=None):
    if kind in ('clear', 'copy'):
        return 2
    coefficient = Q(coefficient)
    numerator = abs(coefficient.numerator)
    denominator = coefficient.denominator
    need(numerator > 0 and denominator & (denominator - 1) == 0, 'Nonzero dyadic scalar')
    if kind == 'scale':
        need(numerator & (numerator - 1) == 0, 'Power-of-two scale')
        return 2 * (abs(numerator.bit_length() - denominator.bit_length()) + (coefficient < 0))
    need(kind == 'add', 'Scalar opcode')
    return 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count() + denominator.bit_length() - 1)


def core_matrix(events, word, orientation, J):
    """Pull all output covectors through the circuit in reverse order."""
    columns = [{i: Q(1)} for i in range(712)]
    for event in reversed(events):
        if event[0] != 'scalar':
            continue
        gate = event[1]
        op, target = gate[0], register(gate[1])
        if op == 'clear':
            need(target >= 704, 'Only owned core arrays are cleared')
            columns[target] = {}
        elif op == 'scale':
            c = Q(*gate[2:])
            columns[target] = {i: c * value for i, value in columns[target].items()}
        else:
            need(op == 'add', 'Core ADD grammar')
            source = register(gate[2])
            need(source != target, 'Distinct ADD wires')
            acc(columns[source], columns[target], Q(*gate[3:]))
    for source, actual in enumerate(columns):
        expected = {source: Q(1)} if source < 704 else {}
        if orientation == 'forward' and source < 112:
            acc(expected, {112 + p: J[p][source] for p in range(112) if J[p][source]})
        if orientation == 'backward' and 112 <= source < 224:
            acc(expected, {p: -J[p][source - 112] for p in range(112) if J[p][source - 112]})
        need(actual == expected, orientation + ' reverse transpose column ' + str(source))

    frames = word['start'][:] + [None] * 8
    profile = Counter()
    scalar_cost = 0
    scalar_count = 0
    for event in events:
        tag = event[0]
        if tag == 'scalar':
            gate, declared = event[1:]
            op, target = gate[0], register(gate[1])
            scalar_count += 1
            if op == 'clear':
                need(target >= 704, 'Owned clear at actual frame')
                frames[target] = declared
                scalar_cost += price(op)
            else:
                need(frames[target] == declared, 'Declared scalar target frame')
                if op == 'add':
                    need(frames[register(gate[2])] == declared, 'Declared scalar source frame')
                scalar_cost += price(op, Q(*(gate[3:] if op == 'add' else gate[2:])))
        elif tag == 'climb':
            _, _, wire, old, new, paid = event
            need(frames[wire] == old, 'Declared native input frame')
            a, b = word['frames'][old], word['frames'][new]
            need(rank(a + b) == len(b), 'Nested native subspaces')
            need(paid == len(b) - len(a) > 0, 'Declared native rank')
            frames[wire] = new
            profile[paid] += 1
        elif tag == 'adapter':
            _, direction, wire, frame = event
            endpoint = word['start'] if direction == 'old_to_new' else word['final']
            need(direction in ('old_to_new', 'new_to_old') and endpoint[wire] == frame, 'Ordinary adapter endpoint')
        elif tag == 'residual_adapter':
            _, side, wire, entry, *tail = event
            need(side in ('pre', 'post'), 'Residual adapter side')
            need(entry == word['start'][wire] and (tail[0] if tail else 1) == word['final'][wire], 'Residual adapter endpoints')
        else:
            need(tag == 'phase', 'Core event grammar')
    need(frames == word['final'] + [0] * 8, 'Complete core frame ledger')
    need(scalar_cost == 202138 and sum(k * v for k, v in profile.items()) == 5522, 'Core invoice')
    return columns, {'exact_input_columns': 712, 'scalar_events': scalar_count, 'scalar_cost': scalar_cost, 'profile': dict(sorted(profile.items())), 'native_mass': 5522}


def atom(source):
    return {((), source): Q(1)}


def op_left(poly, port, sign):
    letter = sign * (port + 1)
    out = {}
    for (word, source), coefficient in poly.items():
        reduced = word[1:] if word and word[0] == -letter else (letter,) + word
        acc(out, {(reduced, source): coefficient})
    return out


def boundary(events, data):
    data = [dict(poly) for poly in data]
    for event in events:
        tag, target = event['kind'], event['target']
        need(target < 224 or target == 704, 'Boundary touches only data or C0')
        if tag == 'clear':
            need(target == 704, 'Boundary clear is owned C0')
            data[target] = {}
        elif tag == 'copy':
            source = event['source']
            need(target == 704 and not data[target] and source < 224, 'Owned physical copy')
            data[target] = dict(data[source])
        elif tag == 'line':
            need(target == 704 and event['port'] in A and event['power'] in (-1, 1), 'Selected signed line on C0')
            data[target] = op_left(data[target], event['port'], event['power'])
        elif tag == 'scale':
            c = Q(event['coefficient'])
            data[target] = {key: c * value for key, value in data[target].items() if c * value}
        else:
            need(tag == 'add' and (event['source'] < 224 or event['source'] == 704), 'Physical common-address ADD')
            need(target != event['source'], 'Distinct physical ADD arrays')
            acc(data[target], data[event['source']], Q(event['coefficient']))
    return data


def apply_matrix(columns, data):
    output = [{} for _ in range(712)]
    for source, column in enumerate(columns):
        for target, coefficient in column.items():
            acc(output[target], data[source], coefficient)
    return output


def evaluate(columns, before, after):
    data = [atom(i) for i in range(712)]
    for p in range(112):
        data[p] = op_left(data[p], p, 1)
    data = boundary(before, data)
    for p in range(112):
        data[p] = op_left(data[p], p, -1)
    data = apply_matrix(columns, data)
    for p in range(112):
        data[112 + p] = op_left(data[112 + p], p, -1)
    physical_without_F = boundary(after, data)
    output = [dict(poly) for poly in physical_without_F]
    for p in range(112):
        output[112 + p] = op_left(output[112 + p], p, 1)
    return output, physical_without_F


def linear_combination(coefficients, data):
    result = {}
    for key, coefficient in coefficients.items():
        acc(result, data[key], coefficient)
    return result


def expected_map(kind, B, D):
    output = [atom(i) if i < 704 else {} for i in range(712)]
    r = {a: op_left(atom(112 + a), a, -1) for a in A}
    qa = {a: op_left(atom(a), a, 1) for a in A}
    if kind.startswith('B'):
        for a in A:
            output[a] = linear_combination({112 + p: c for p, c in B[a].items()}, output)
            acc(output[a], r[a], 1 if kind == 'B0' else -12)
            output[112 + a] = qa[a]
        for p in U:
            acc(output[p], atom(112 + p), -1)
            if kind != 'B16':
                acc(output[p], linear_combination(D[p], qa))
            if kind == 'B0':
                acc(output[p], linear_combination(D[p], r), -1)
            else:
                acc(output[112 + p], linear_combination(D[p], r), -1)
    else:
        queries = {a: linear_combination(B[a], output) for a in A}
        for a in A:
            acc(output[a], op_left(queries[a], a, -1), -1)
        for p in U:
            acc(output[112 + p], atom(p))
            acc(output[112 + p], linear_combination(D[p], queries), -1)
            if kind == 'F0':
                acc(output[112 + p], linear_combination(D[p], r), -1)
    return output


def check_inverse(kind, out, B, D):
    recovered = [{} for _ in range(224)]
    if kind.startswith('B'):
        r = {}
        for a in A:
            r[a] = dict(out[a])
            acc(r[a], linear_combination({112 + p: c for p, c in B[a].items()}, out), -1)
            recovered[112 + a] = op_left(r[a], a, 1)
            recovered[a] = op_left(out[112 + a], a, -1)
        for p in U:
            v = dict(out[112 + p])
            if kind != 'B0':
                acc(v, linear_combination(D[p], r))
            recovered[112 + p] = v
            recovered[p] = dict(out[p])
            acc(recovered[p], v)
            if kind != 'B16':
                acc(recovered[p], linear_combination({112 + a: c for a, c in D[p].items()}, out), -1)
            if kind == 'B0':
                acc(recovered[p], linear_combination(D[p], r))
    else:
        query = {a: linear_combination(B[a], out) for a in A}
        r = {a: op_left(out[112 + a], a, -1) for a in A}
        for a in A:
            recovered[a] = dict(out[a])
            acc(recovered[a], op_left(query[a], a, -1))
            recovered[112 + a] = dict(out[112 + a])
        for p in U:
            recovered[p] = dict(out[p])
            recovered[112 + p] = dict(out[112 + p])
            acc(recovered[112 + p], out[p], -1)
            acc(recovered[112 + p], linear_combination(D[p], query))
            if kind == 'F0':
                acc(recovered[112 + p], linear_combination(D[p], r))
    need(recovered == [atom(i) for i in range(224)], kind + ' data inverse')


def rotate(pair, phase):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def mono(record, x, value):
    rows, quadratic, alpha = record['matrix_rows'], record['quadratic_rows'], record['linear_Z4']
    need(len(rows) == len(quadratic) == len(alpha) == 9 and rank(rows) == 9, 'Monomial matrix dimensions')
    target = sum(((row & x).bit_count() % 2) << j for j, row in enumerate(rows)) ^ record['offset']
    exponent = record['phase']
    exponent += sum(alpha[j] for j in range(9) if (x >> j) & 1)
    exponent += 2 * sum((quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count() for j in range(9) if (x >> j) & 1)
    return target, rotate(value, exponent)


def kernel_column(record, x):
    target, value = mono(record['right'], x, (1, 0))
    a, b = value
    result = {}
    for y, coefficient in ((target, (a - b, a + b)), (target ^ 1, (a + b, b - a))):
        output, coefficient = mono(record['left'], y, coefficient)
        need(output not in result, 'Two distinct kernel addresses')
        result[output] = coefficient
    return result


def kernel_checks(records, ports):
    decoder_path = LANES / 'interface-proof/verify_native_lift.py'
    hashed(decoder_path, '087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b')
    spec = importlib.util.spec_from_file_location('independent_native_decoder', decoder_path)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    need({(record['port'], record['inverse']) for record in records} == {(a, inv) for a in A for inv in (False, True)}, 'Exact signed line class set')
    count = 0
    for item in records:
        p, inverse, recipe = item['port'], item['inverse'], item['recipe']
        need(recipe['rank'] == 1, 'Each added child has rank one')
        sign = -1 if inverse else 1
        direct = (('C', ports[p], sign),)
        decoder.equal(decoder.recipe(recipe), direct, 'Independent signed line ' + str((p, sign)))
        decoder.equal(direct + decoder.fourier(9), decoder.fourier(9) + direct, 'Line commutes with common F')
        for x in range(512):
            expected = {x: (1, sign), x ^ ports[p]: (1, -sign)}
            need(kernel_column(recipe, x) == expected, 'Exact signed line Gaussian column')
            count += 1
    bad = deepcopy(records[0]['recipe'])
    bad['left']['phase'] = (bad['left']['phase'] + 1) % 4
    need(kernel_column(bad, 0) != kernel_column(records[0]['recipe'], 0), 'Wrong line global phase is rejected')
    return {'signed_recipes': len(records), 'all_basis_columns': count, 'independent_Pauli_and_zero_state_checks': len(records), 'F_commutation_checks': len(records)}


def main():
    started = time.monotonic()
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, 'At least 3 GiB free')
    for prefix in PACKET_PINS:
        freeze = load(SOURCE / (prefix + '-FREEZE.json'))
        entries = freeze.get('files', freeze)
        for name, pin in entries.items():
            zipped = name.endswith(' decompressed')
            path = SOURCE / name.removesuffix(' decompressed')
            hashed(path, pin, zipped)
    packets = {prefix: load(SOURCE / (prefix + '-PROGRAM.json.gz'), pin, True) for prefix, pin in PACKET_PINS.items()}
    b = packets['RAW-SELECTED-BACKWARD']
    f = packets['RAW-SELECTED-FORWARD']
    b0 = packets['ZERO-LINE-BACKWARD']
    core = load(LANES / 'circuit-interface/CENTRE-FREE-PROGRAMS.json.gz', CORE_PIN, True)
    word_path = ROOT / 'work/five-pr-sprint-20261013/lanes/centre-sharing/CANONICAL-WORD.json.gz'
    raw_word = hashed(word_path, WORD_PIN)
    word = json.loads(gzip.decompress(raw_word))
    for p, direction in enumerate(word['ports']):
        start_x = word['frames'][word['start'][p]]
        start_y = word['frames'][word['start'][112 + p]]
        final_x = word['frames'][word['final'][p]]
        final_y = word['frames'][word['final'][112 + p]]
        need(len(start_x) == rank(start_x + [direction]) == 1, 'Source endpoint line subspace')
        need(start_y == [] and len(final_x) == 9, 'Input Y and output X endpoint frames')
        need(len(final_y) == 8 and all((v & direction).bit_count() % 2 == 0 for v in final_y), 'Output Y endpoint hole subspace')
    interface = load(LANES / 'circuit-interface/INTERFACE.json', INTERFACE_PIN)
    native_review = load(LANES / 'interface-proof/NATIVE-LIFT-REVIEW.json', '61b3990c983b96b8bff01feab8c83a612ea41612b948b1059186ce9ffa9692ea')
    need(native_review['changed_payload_sha256'] == CORE_PIN and native_review['status'] == 'PASS_INDEPENDENT_NATIVE_FRAME_LIFT_AND_FINITE_LOCAL_BILL', 'Inherited native review binding')
    signed = load(LANES / 'paired-package-review/upstream-followthrough-20261015/current-query-encoder/UNIFORM-SIGNED-PROGRAMS.json.gz', KERNEL_PACKET_PIN, True)
    need(b['retained_core'] == b0['retained_core'] == core['backward'] and f['retained_core'] == core['forward'], 'Byte-exact inherited core event arrays')
    need(b['line_recipes'] == f['line_recipes'] == signed['line_recipes'], 'Signed line recipe binding')
    need(b0['physical_exchange'] == b['physical_exchange'] and b0['post_lower_shear'] == b['post_lower_shear'] and b0['added_native_lines'] == 0, 'Zero-line B subword binding')
    need(f['input_physical_exchange'] == f['output_physical_exchange'] == b['physical_exchange'], 'All physical swap tapes')

    R = [[Q(row.get(str(p), '0')) for p in range(112)] for row in interface['R']]
    J = [[Q(p == q) - sum(row[p] * row[q] for row in R) / 4 for q in range(112)] for p in range(112)]
    B = {a: {p: -J[a][p] for p in U if J[a][p]} for a in A}
    D = {p: {a: -J[p][a] for a in A if J[p][a]} for p in U}
    need(all(J[a][c] == 0 for a in A for c in A), 'Selected block of J is zero')
    need(all(sum(B[a].get(p, 0) * D[p].get(c, 0) for p in U) == 13 * (a == c) for a in A for c in A), 'BD equals 13I')
    need(all(J[p][q] == Q(p == q) - sum(D[p].get(a, 0) * B[a].get(q, 0) for a in A) for p in U for q in U), 'Ordinary block is I-DB')
    matrices, core_checks = {}, {}
    for orientation in ('forward', 'backward'):
        matrices[orientation], core_checks[orientation] = core_matrix(core[orientation], word, orientation, J)
        print('PASS reverse transpose core', orientation, flush=True)

    variants = {
        'B0': ('backward', b0['physical_exchange'], b0['post_lower_shear'], 206506, 5522),
        'B8': ('backward', b['prefix'] + b['physical_exchange'], b['post_lower_shear'], 210714, 5530),
        'B16': ('backward', b['prefix'] + b['physical_exchange'], b['post_lower_shear'] + b['optional_ordinary_correction'], 214922, 5538),
        'F0': ('forward', f['input_physical_exchange'], f['output_physical_exchange'], 202554, 5522),
        'F8': ('forward', f['optional_input_code'] + f['input_physical_exchange'], f['output_physical_exchange'], 206762, 5530),
    }
    reports = {}
    for kind, (orientation, before, after, scalar, mass) in variants.items():
        actual, physical = evaluate(matrices[orientation], before, after)
        expected = expected_map(kind, B, D)
        need(actual == expected, kind + ' exact free-operator matrix')
        need(actual[224:704] == [atom(i) for i in range(224, 704)] and actual[704:] == [{}] * 8, kind + ' borrowed and private outputs')
        if kind.startswith('B'):
            need(all(physical[112 + a] == atom(a) for a in A), kind + ' physical selected Y is F times original selected X')
        check_inverse(kind, actual, B, D)
        extra_scalar = sum(price(e['kind'], e.get('coefficient')) for e in before + after if e['kind'] != 'line')
        lines = sum(e['kind'] == 'line' for e in before + after)
        need(scalar == 202138 + extra_scalar and mass == 5522 + lines, kind + ' exact invoice')
        reports[kind] = {'all_input_columns': 712, 'data_inverse_columns': 224, 'helpers_restored': 480, 'owned_private_zero': 8, 'scalar_cost': scalar, 'native_mass': mass, 'new_rank_one_children': lines}
        print('PASS local free-operator map', kind, flush=True)

    controls = {}
    expected = expected_map('B8', B, D)
    controls['omit_B8_input_code'] = evaluate(matrices['backward'], b['physical_exchange'], b['post_lower_shear'])[0] != expected
    controls['omit_B_output_lower_shear'] = evaluate(matrices['backward'], b['prefix'] + b['physical_exchange'], [])[0] != expected
    controls['omit_B_input_swap'] = evaluate(matrices['backward'], b['prefix'], b['post_lower_shear'])[0] != expected
    wrong = deepcopy(b['prefix'])
    for event in wrong:
        if event['kind'] == 'line':
            event['power'] *= -1
    controls['wrong_inverse_line_sign'] = evaluate(matrices['backward'], wrong + b['physical_exchange'], b['post_lower_shear'])[0] != expected
    controls['omit_F_output_swap'] = evaluate(matrices['forward'], f['optional_input_code'] + f['input_physical_exchange'], [])[0] != expected_map('F8', B, D)
    logical_swap = [atom(i) for i in range(712)]
    for a in A:
        logical_swap[a], logical_swap[112 + a] = logical_swap[112 + a], logical_swap[a]
    logical_swap = boundary(b0['post_lower_shear'], apply_matrix(matrices['backward'], logical_swap))
    controls['replace_physical_swap_by_logical_swap'] = logical_swap != expected_map('B0', B, D)
    moved = expected_map('F8', B, D)
    a = A[0]
    moved[a] = atom(a)
    for p, coefficient in B[a].items():
        acc(moved[a], op_left(atom(p), p, -1), -coefficient)
    controls['move_Q_through_dense_B'] = moved != expected_map('F8', B, D)
    witness_port = next(p for p in B[a] if word['ports'][p] != word['ports'][a])
    actual_selected_column = {0: (1, -1), word['ports'][a]: (1, 1)}
    actual_ordinary_column = {0: (1, -1), word['ports'][witness_port]: (1, 1)}
    controls['actual_native_Q_through_B_counterexample'] = actual_selected_column != actual_ordinary_column
    need(all(controls.values()), 'Every operator mutation is rejected')
    lines = kernel_checks(signed['line_recipes'], word['ports'])
    result = {
        'status': 'PASS_INDEPENDENT_RAW_SELECTED_LOCAL_REVIEW',
        'method': 'Reverse transpose accumulation of the retained scalar core, followed by matrix composition over a free group algebra of the Q operators. No producer code is imported.',
        'core': core_checks,
        'variants': reports,
        'signed_line_checks': lines,
        'data_endpoint_frame_checks': 448,
        'negative_controls': controls,
        'actual_Q_B_noncommutation_witness': {'selected_port': a, 'ordinary_port': witness_port, 'B_entry': str(B[a][witness_port]), 'selected_direction': word['ports'][a], 'ordinary_direction': word['ports'][witness_port], 'basis_input': 0, 'Gaussian_denominator': 2},
        'boundary_access': 'Boundary ADDs are actual common-address operations on physical data arrays. They do not identify unequal logical frames. The coded endpoint formulas keep those operators explicitly.',
        'inherited_native_review_sha256': '61b3990c983b96b8bff01feab8c83a612ea41612b948b1059186ce9ffa9692ea',
        'not_repeated': ['Full old-core Clifford recipe sweep', 'Full 712-array physical Gaussian operator replay'],
        'not_claimed': ['Actual inter-call controller or decoder', 'New child hosting', 'Complete recursive scalar, storage, and precision invoice', 'New kappa'],
        'seconds': time.monotonic() - started,
        'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (HERE / 'RAW-REVIEW-INPUTS.json').write_text(json.dumps(INPUTS, indent=2, sort_keys=True) + '\n')
    result['input_manifest_sha256'] = hashlib.sha256((HERE / 'RAW-REVIEW-INPUTS.json').read_bytes()).hexdigest()
    (HERE / 'RAW-REVIEW.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
