#!/usr/bin/env python3
"""Review complete serial balanced words with exact ordered operators."""
from collections import Counter
from copy import deepcopy
import argparse
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
SOURCE = LANES / 'new-core-transfer-20261017'
INPUTS = {}


def need(test, label):
    if not test:
        raise ValueError(label)


def read_bytes(path, pin=None, zipped=False):
    raw = path.read_bytes()
    value = gzip.decompress(raw) if zipped else raw
    record = {'sha256': hashlib.sha256(raw).hexdigest()}
    if zipped:
        record['decompressed_sha256'] = hashlib.sha256(value).hexdigest()
    INPUTS[str(path.relative_to(ROOT))] = record
    need(pin is None or hashlib.sha256(value).hexdigest() == pin, 'Input pin: ' + str(path))
    return value


def read(path, pin=None, zipped=False):
    return json.loads(read_bytes(path, pin, zipped))


module_path = HERE / 'check_raw_selected.py'
read_bytes(module_path, 'c6ba81bd2e382e021b2c2ea853f75576dc101400a7cce3408003fe365c7e7bef')
spec = importlib.util.spec_from_file_location('independent_scalar_algebra', module_path)
alg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alg)
add, atom, line = alg.acc, alg.atom, alg.op_left


def combine(row, values):
    result = {}
    for p, coefficient in row.items():
        add(result, values[p], coefficient)
    return result


def inverse(matrix):
    n = len(matrix)
    a = [list(row) + [Q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for p in range(n):
        pivot = next((r for r in range(p, n) if a[r][p]), None)
        need(pivot is not None, 'Invertible centre matrix')
        a[p], a[pivot] = a[pivot], a[p]
        scale = a[p][p]
        a[p] = [value / scale for value in a[p]]
        for r in range(n):
            if r != p and a[r][p]:
                scale = a[r][p]
                a[r] = [x - scale * y for x, y in zip(a[r], a[p])]
    result = [row[n:] for row in a]
    need(all(sum(matrix[i][k] * result[k][j] for k in range(n)) == (i == j)
             and sum(result[i][k] * matrix[k][j] for k in range(n)) == (i == j)
             for i in range(n) for j in range(n)), 'Two centre inverse orders')
    return result


def core_operator(events, word, J, direction):
    n = len(word['start'])
    zeros = {z: n + 8 + i for i, z in enumerate(word['zero_buffers'])}
    total = n + 8 + len(zeros)
    need(n == 632 and len(zeros) == 91, 'Current provider dimensions')

    def reg(wire):
        kind, value = wire
        if kind == 'L':
            need(0 <= value < n, 'Live field range')
            return value
        if kind == 'C':
            need(0 <= value < 8, 'Owned field range')
            return n + value
        need(kind == 'Z' and value in zeros, 'Private field range')
        return zeros[value]

    columns = [atom(i) for i in range(total)]
    for event in reversed(events):
        tag = event[0]
        if tag == 'scalar':
            gate = event[1]
            op, target = gate[0], reg(gate[1])
            if op == 'clear':
                need(n <= target < n + 8, 'Only owned fields clear')
                columns[target] = {}
            elif op == 'scale':
                c = Q(*gate[2:])
                columns[target] = {key: c * value for key, value in columns[target].items()}
            else:
                need(op == 'add', 'Core scalar opcode')
                add(columns[reg(gate[2])], columns[target], Q(*gate[3:]))
        elif tag == 'warp':
            target, letter = reg(event[1]), event[2]
            result = {}
            for (word_value, output), coefficient in columns[target].items():
                reduced = word_value[:-1] if word_value and word_value[-1] == -letter else word_value + (letter,)
                add(result, {(reduced, output): coefficient})
            columns[target] = result
        elif tag == 'zero_buffer' and event[1] == 'alloc':
            columns[zeros[event[2]]] = {}
    for source, actual in enumerate(columns):
        expected = atom(source) if source < n or n < source < n + 8 else {}
        if direction == 'forward' and source < 112:
            add(expected, {((), 112 + p): J[p][source] for p in range(112) if J[p][source]})
        if direction == 'backward' and 112 <= source < 224:
            add(expected, {((), p): -J[p][source - 112] for p in range(112) if J[p][source - 112]})
        need(actual == expected, direction + ' reverse free-operator column ' + str(source))
    rational = [{output: c for (_, output), c in column.items()} for column in columns[:n + 8]]

    frames = word['start'][:] + [0] * 8 + [None] * len(zeros)
    active, allocated, freed = set(), set(), set()
    profile, tags = Counter(), Counter()
    scalar = 0
    allowed_warps = set(map(tuple, word['warp_edges']))
    for event in events:
        tag = event[0]
        tags[tag] += 1
        if tag == 'scalar':
            gate, declared = event[1:]
            op, target = gate[0], reg(gate[1])
            if op == 'clear':
                need(n <= target < n + 8, 'Owned frame clear')
                frames[target] = declared
                scalar += alg.price(op)
            else:
                need(frames[target] == declared, 'Core scalar target frame')
                need(target < n + 8 or target in active, 'Core target lifetime')
                if op == 'add':
                    source = reg(gate[2])
                    need(frames[source] == declared, 'Core scalar source frame')
                    need(source < n + 8 or source in active, 'Core source lifetime')
                scalar += alg.price(op, Q(*(gate[3:] if op == 'add' else gate[2:])))
        elif tag == 'climb':
            _, _, wire, old, new, paid = event
            before, after = word['frames'][old], word['frames'][new]
            need(frames[wire] == old, 'Child input frame')
            need(alg.rank(before + after) == len(after), 'Nested child frames')
            need(paid == len(after) - len(before) > 0, 'Paid child rank')
            frames[wire] = new
            profile[paid] += 1
        elif tag == 'warp':
            _, wire, symbol, old, new = event
            target = reg(wire)
            need(frames[target] == old, 'Warp input frame')
            need((1 if symbol > 0 else -1, abs(symbol), old, new) in allowed_warps, 'Canonical signed warp class')
            need(target < n + 8 or target in active, 'Warp private lifetime')
            frames[target] = new
        elif tag == 'zero_buffer':
            target = zeros[event[2]]
            if event[1] == 'alloc':
                need(target not in allocated and target not in active, 'Single zero allocation')
                allocated.add(target)
                active.add(target)
                frames[target] = 1
            else:
                need(event[1] == 'free' and target in active and target not in freed and frames[target] == 1, 'Return zero at FULL')
                active.remove(target)
                freed.add(target)
        elif tag == 'adapter':
            _, side, wire, frame = event
            endpoint = word['start'] if side == 'old_to_new' else word['final']
            need(side in ('old_to_new', 'new_to_old') and endpoint[wire] == frame, 'Ordinary adapter endpoint')
        elif tag == 'residual_adapter':
            _, side, wire, entry, *tail = event
            need(side in ('pre', 'post') and entry == word['start'][wire] and (tail[0] if tail else 1) == word['final'][wire], 'Helper adapter endpoints')
        else:
            need(tag == 'phase', 'Core event grammar')
    need(not active and allocated == freed == set(zeros.values()), 'All zero-buffer lifetimes close')
    need(frames[:n + 8] == word['final'] + [0] * 8, 'Final core frames')
    need(scalar == 164514 and dict(profile) == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20}, 'Core complete invoice')
    need(tags['warp'] == 240, 'All retained warps')
    return rational, {'orientation': direction, 'extended_columns': total, 'arbitrary_columns': n + 8,
                      'private_zero_buffers': len(zeros), 'scalar': scalar, 'events': dict(tags),
                      'native_profile': dict(sorted(profile.items()))}


def boundary(events, data, n):
    result = [dict(row) for row in data]
    for event in events:
        kind, target = event['kind'], event['target']
        need(0 <= target < 224 or n <= target < n + 8, 'Boundary target access')
        if kind == 'clear':
            need(n <= target < n + 8, 'Only owned fields clear')
            result[target] = {}
        elif kind in ('scale', 'divide_odd'):
            if kind == 'divide_odd':
                need(target == n and event['divisor'] == 3, 'Distinct owned /3 opcode')
                coefficient = Q(1, 3)
            else:
                coefficient = Q(event['coefficient'])
                need(coefficient.denominator & (coefficient.denominator - 1) == 0, 'Old SCALE is dyadic')
            result[target] = {key: coefficient * value for key, value in result[target].items()}
        else:
            need(kind == 'add', 'No new native operation')
            source = event['source']
            need(0 <= source < 224 or n <= source < n + 8, 'Boundary source access')
            need(source != target, 'Distinct ADD fields')
            add(result[target], result[source], Q(event['coefficient']))
    return result


def factor_frames(events, bank, frame, n):
    frames = {p: frame for p in range(bank, bank + 112)}
    frames.update({p: 0 for p in range(n, n + 8)})
    for event in events:
        kind, target, declared = event['kind'], event['target'], event['frame']
        need(target in frames, 'Factor target bank')
        if kind == 'clear':
            need(n <= target < n + 8, 'Owned factor preparation')
            frames[target] = declared
        else:
            need(frames[target] == declared == frame, 'Factor target common frame')
            if kind == 'add':
                source = event['source']
                need(source in frames and frames[source] == declared, 'Factor source common frame')
            else:
                need(n <= target < n + 8, 'Scale or divide only an owned query')
    need(all(frames[p] == 0 for p in range(n, n + 8)), 'All factor-owned frames return to I')


def execute(program, matrix, n):
    state = [atom(i) for i in range(n + 8)]
    for p in range(112):
        state[p] = line(state[p], p, 1)
    state = boundary(program['prefix'] + program['input_exchange'], state, n)
    for p in range(112):
        state[p] = line(state[p], p, -1)
    result = [{} for _ in range(n + 8)]
    for source, column in enumerate(matrix):
        for target, coefficient in column.items():
            add(result[target], state[source], coefficient)
    for p in range(112):
        result[112 + p] = line(result[112 + p], p, -1)
    physical_without_F = boundary(program['suffix'] + program['owned_cleanup'], result, n)
    result = deepcopy(physical_without_F)
    for p in range(112):
        result[112 + p] = line(result[112 + p], p, 1)
    return result, physical_without_F


def geometry(r, selected):
    S, U = tuple(selected), tuple(p for p in range(112) if p not in selected)
    gram = [[sum(row[p] * row[q] for row in r) / 4 for q in range(112)] for p in range(112)]
    J = [[Q(p == q) - gram[p][q] for q in range(112)] for p in range(112)]
    T = [[sum(r[i][p] * r[j][p] for p in S) / 4 - 13 * (i == j) for j in range(8)] for i in range(8)]
    ti = inverse(T)
    C = [[sum(r[i][p] * ti[i][j] * r[j][q] for i in range(8) for j in range(8)) / 4
          for q in range(112)] for p in range(112)]
    hi = {p: {q: Q(p == q) + C[p][q] for q in U if Q(p == q) + C[p][q]} for p in U}
    h = {p: {q: J[p][q] for q in U if J[p][q]} for p in U}
    return S, U, J, C, h, hi


def expected_map(name, S, U, J, C, h, hi, n):
    identity = [atom(i) for i in range(n + 8)]
    value = deepcopy(identity)
    qa = {p: line(identity[p], p, 1) for p in S}
    qb = {p: line(identity[112 + p], p, -1) for p in S}
    if name in ('balanced_backward', 'diagonal_backward'):
        for p in S:
            value[p] = dict(qb[p])
            value[112 + p] = dict(qa[p])
            if name == 'balanced_backward':
                add(value[p], combine({q: -J[p][q] for q in S if J[p][q]}, qa))
                add(value[p], combine({112 + q: -J[p][q] for q in U if J[p][q]}, identity))
            else:
                add(value[p], qa[p], -1)
        for p in U:
            value[p] = combine(hi[p], identity) if name == 'balanced_backward' else dict(identity[p])
            add(value[p], identity[112 + p], -1)
            if name == 'balanced_backward':
                for q, c in hi[p].items():
                    add(value[p], combine({s: J[q][s] for s in S if J[q][s]}, qa), -c)
        if name == 'diagonal_backward':
            z = {p: qa[p] if p in S else identity[p] for p in range(112)}
            for p in range(112):
                add(value[p], combine({q: C[p][q] for q in range(112) if C[p][q]}, z))
    else:
        need(name == 'balanced_forward', 'Known local variant')
        for p in S:
            query = combine({q: J[p][q] for q in S if J[p][q]}, qb)
            add(query, combine({q: J[p][q] for q in U if J[p][q]}, identity))
            add(value[p], line(query, p, -1))
        for p in U:
            value[112 + p] = combine(h[p], identity)
            add(value[112 + p], combine({112 + q: c for q, c in h[p].items()}, identity))
            add(value[112 + p], combine({q: J[p][q] for q in S if J[p][q]}, qb))
    value[n:] = [{} for _ in range(8)]
    return value


def check_inverse(name, actual, S, U, J, r, h, hi, n):
    recovered = deepcopy(actual)
    if name in ('balanced_backward', 'diagonal_backward'):
        qa = {p: actual[112 + p] for p in S}
        for p in S:
            recovered[p] = line(qa[p], p, -1)
        for p in U:
            recovered[p] = combine(h[p], actual)
            add(recovered[p], combine({112 + q: c for q, c in h[p].items()}, actual))
            add(recovered[p], combine({q: J[p][q] for q in S if J[p][q]}, qa))
        for p in S:
            query = dict(actual[p])
            if name == 'diagonal_backward':
                row = {q: sum(v[p] * v[q] for v in r) / 4 for q in U}
                add(query, combine(row, actual), -1)
            add(query, combine({q: J[p][q] for q in S if J[p][q]}, qa))
            add(query, combine({112 + q: J[p][q] for q in U if J[p][q]}, actual))
            recovered[112 + p] = line(query, p, 1)
    else:
        qb = {p: line(actual[112 + p], p, -1) for p in S}
        ordinary = {}
        for p in U:
            ordinary[p] = dict(actual[112 + p])
            add(ordinary[p], combine({q: J[p][q] for q in S if J[p][q]}, qb), -1)
        for p in U:
            recovered[112 + p] = combine(hi[p], ordinary)
            add(recovered[112 + p], actual[p], -1)
        for p in S:
            query = combine({q: J[p][q] for q in S if J[p][q]}, qb)
            add(query, combine({q: J[p][q] for q in U if J[p][q]}, actual))
            add(recovered[p], line(query, p, -1), -1)
    need(recovered[:n] == [atom(i) for i in range(n)], 'Ordered content inverse')


def invoice(events):
    scalar, scans = 0, 0
    for event in events:
        if event['kind'] == 'divide_odd':
            need(event['divisor'] == 3, 'Only fixed /3 scans')
            scans += 2
        else:
            scalar += alg.price(event['kind'], event.get('coefficient'))
    return scalar, scans


def factor_binding(events, word, offset, n):
    def field(p):
        if p == n:
            return 112
        need(offset <= p < offset + 112, 'Factor grid-word data bank')
        return p - offset

    actual = []
    for event in events:
        kind, target = event['kind'], field(event['target'])
        if kind == 'clear':
            actual.append([kind, target])
        elif kind == 'divide_odd':
            actual.append([kind, target, event['divisor']])
        elif kind == 'scale':
            actual.append([kind, target, str(Q(event['coefficient']))])
        else:
            actual.append([kind, target, field(event['source']), str(Q(event['coefficient']))])
    reduced = []
    for event in word:
        if event[0] == 'clear' and reduced and reduced[-1] == event:
            continue
        reduced.append(event)
    need(actual == reduced, 'Exact odd-grid factor after seven adjacent zero-clear removals')


def endpoint_commutations(ports):
    path = LANES / 'interface-proof/verify_native_lift.py'
    read_bytes(path, '087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b')
    spec = importlib.util.spec_from_file_location('independent_balanced_endpoint_decoder', path)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    for direction in ports:
        for sign in (-1, 1):
            c = (('C', direction, sign),)
            decoder.equal(c + decoder.fourier(9), decoder.fourier(9) + c, 'Actual signed line commutes with F')
    return 2 * len(ports)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="New receipt path; existing files are not overwritten.")
    out = parser.parse_args().out.resolve()
    manifest = out.with_name(out.stem + "-INPUTS.json")
    need(out.parent.is_dir(), "Output directory exists")
    need(not out.exists() and not manifest.exists(), "Output files must be new")
    started = time.monotonic()
    need(shutil.disk_usage(HERE).free >= 3 * 1024**3, 'At least 3 GiB free')
    freeze = read(SOURCE / 'FREEZE-SERIAL-BALANCED.json', 'fec84012aa803703efe1bf5c733f5c03fe2269f45054496ae55a212f4f96c42f')
    for name, pin in freeze['files'].items():
        read_bytes(SOURCE / name, pin)
    packet = read(SOURCE / 'SERIAL-BALANCED-PROGRAMS.json.gz', 'a0e9cd4f125089844e67090ab0e8e3fc94e449a146e06dbcc36345dd517a6b9e', True)
    core = read(SOURCE / 'CLEAN-J-PROGRAMS.json.gz', 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa', True)
    native = read(LANES / 'independent-review-20261017/NEW-CORE-NATIVE-REVIEW.json', '924b898621dd25ea9d3330563fdf7acf6c3b63dc99526e15faaee682f4bdd94d')
    need(native['status'] == 'PASS_INDEPENDENT_NEW_CORE_NATIVE_RECIPES' and native['clean_payload_sha256'] == packet['source_pins']['core'], 'Both literal native orientations are bound')
    r = [[Q(row.get(str(p), 0)) for p in range(112)] for row in core['R']]
    need(len(r) == 8 and all(sum(r[i][p] * r[j][p] for p in range(112)) == 56 * (i == j) for i in range(8) for j in range(8)), 'Actual full row Gram matrix')
    odd_path = LANES / 'independent-review-20261017/odd-grid-a8-20261017'
    odd_words = read(odd_path / 'A8-ODD-GRID-WORDS.json', '525822746e2d760a81c5a4c8847c25974d0a419a2c5abbaa0472d13bde1c6aa9')
    read_bytes(odd_path / 'A8-ODD-GRID.md', 'e0210105ba6c6246f1f84c8ce2d92cfd07aa6cc8a161ca27d7fcc8e0183cfb01')
    read(odd_path / 'A8-ODD-GRID.json', '0c1dc7cc08de30a14b42c744e73d3963a68acd83bc381f884867b85bfeaee96a')
    commutations = {}
    for provider, item in core['providers'].items():
        commutations[provider] = endpoint_commutations(item['canonical']['ports'])
    cores, core_reports, reports = {}, {}, {}
    counts = {'one_minor': {'balanced_backward': (171474, 16), 'diagonal_backward': (171730, 16), 'balanced_forward': (171650, 0)},
              'five_minors': {'balanced_backward': (170274, 0), 'diagonal_backward': (171554, 0), 'balanced_forward': (171266, 0)}}
    for family_name, family in packet['families'].items():
        S, U, J, C, h, hi = geometry(r, family['selected_S'])
        need(list(U) == family['ordinary_U'] and len(S) in (8, 40), 'Exact selected partition')
        need(all(sum(r[i][p] * r[j][p] for p in U) == 4 * family['lambda'] * (i == j) for i in range(8) for j in range(8)), 'Actual ordinary Gram matrix')
        reports[family_name] = {}
        for provider, item in family['providers'].items():
            word, n = item['canonical'], len(item['canonical']['start'])
            need(word == core['providers'][provider]['canonical'], 'Current canonical source')
            for p, direction in enumerate(word['ports']):
                initial_x = word['frames'][word['start'][p]]
                final_y = word['frames'][word['final'][112 + p]]
                need(len(initial_x) == alg.rank(initial_x + [direction]) == 1, 'Actual X input line')
                need(word['start'][112 + p] == 0 and word['final'][p] == 1, 'Actual common I and FULL boundaries')
                need(len(final_y) == 8 and all((v & direction).bit_count() % 2 == 0 for v in final_y), 'Actual Y output hole')
            reports[family_name][provider] = {}
            for name, program in item['programs'].items():
                direction = program['orientation']
                events = program['retained_core']
                need(direction in ('forward', 'backward') and events == core['providers'][provider]['programs'][direction], 'Exact current native event array')
                key = provider + '/' + direction
                if key not in cores:
                    cores[key], core_reports[key] = core_operator(events, word, J, direction)
                need(program['events'] == program['prefix'] + program['input_exchange'] + events + program['suffix'] + program['owned_cleanup'], 'Literal complete event order')
                factor = program['prefix'] if direction == 'forward' else program['suffix']
                factor_frames(factor, 112 if direction == 'forward' else 0, 0 if direction == 'forward' else 1, n)
                need(sum(e['kind'] == 'clear' for e in factor) == 9, 'Current serial factor uses nine clears')
                if family_name == 'one_minor':
                    factor_name = {'balanced_forward': 'H', 'balanced_backward': 'H_inverse', 'diagonal_backward': 'H_inverse_fused_upper'}[name]
                    factor_binding(factor, odd_words[factor_name], 112 if direction == 'forward' else 0, n)
                actual, physical = execute(program, cores[key], n)
                expected = expected_map(name, S, U, J, C, h, hi, n)
                need(actual == expected, 'Complete ordered map: ' + family_name + '/' + provider + '/' + name)
                need(actual[224:n] == [atom(p) for p in range(224, n)] and actual[n:] == [{}] * 8, 'All current helper and owned columns')
                if direction == 'backward':
                    need(all(physical[112 + p] == atom(p) for p in S), 'Physical selected Y equals F times original X')
                check_inverse(name, actual, S, U, J, r, h, hi, n)
                scalar, scans = invoice(program['prefix'] + program['input_exchange'] + program['suffix'] + program['owned_cleanup'])
                scalar += 164514
                need((scalar, scans) == counts[family_name][name], 'Independently counted current invoice')
                controls = {}
                changed = deepcopy(program)
                changed['prefix' if direction == 'forward' else 'suffix'] = []
                controls['omit_factor'] = execute(changed, cores[key], n)[0] != expected
                changed = deepcopy(program)
                changed['input_exchange'] = []
                controls['omit_input_physical_exchange'] = execute(changed, cores[key], n)[0] != expected
                if scans:
                    changed = deepcopy(program)
                    changed['suffix'] = [e for e in changed['suffix'] if e['kind'] != 'divide_odd']
                    controls['omit_exact_odd_division'] = execute(changed, cores[key], n)[0] != expected
                if name == 'diagonal_backward':
                    changed = deepcopy(program)
                    changed['suffix'] = [e for e in changed['suffix'] if not (e['kind'] == 'add' and e['target'] in S)]
                    controls['omit_selected_upper_scatter'] = execute(changed, cores[key], n)[0] != expected
                need(all(controls.values()), 'Changed words reject')
                reports[family_name][provider][name] = {
                    'scalar_real_primitives': scalar, 'additional_real_divide_by_3_scans': scans,
                    'native_mass': 5073, 'native_children': 3507, 'new_native_children': 0,
                    'all_input_columns': n + 8, 'logical_helpers_under_inherited_wrapper_contract': 408,
                    'owned_output_fields_zero': 8, 'private_zero_buffers': 91,
                    'factor_owned_clears': 9, 'content_inverse_columns': n, 'controls': controls,
                }
                print('PASS serial balanced', family_name, provider, name, scalar, scans, flush=True)
    result = {'status': 'PASS_INDEPENDENT_SERIAL_BALANCED_LOCAL_WORDS', 'core_checks': core_reports, 'families': reports,
              'exact_signed_endpoint_F_commutations': commutations,
              'A8_grid_factor_binding': 'All six A8 factors equal the frozen grid-theorem factors after seven adjacent zero-CLEAR removals and the proved endpoint frame assignment.',
              'odd_division_scope': 'Exact rational local operator, with /3 recorded as a separate opcode. Machine admission requires the separately reviewed common-grid contract.',
              'not_claimed': ['A dyadic-only implementation of the A8 inverse', 'Idle preparation', 'Complete controller, owners, or decoder', 'Complete recursive hosting, cost, precision, or kappa'],
              'native_dependency_sha256': '924b898621dd25ea9d3330563fdf7acf6c3b63dc99526e15faaee682f4bdd94d',
              'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'seconds': time.monotonic() - started}
    manifest.write_text(json.dumps(INPUTS, indent=2, sort_keys=True) + '\n')
    result['input_manifest_sha256'] = hashlib.sha256(manifest.read_bytes()).hexdigest()
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
