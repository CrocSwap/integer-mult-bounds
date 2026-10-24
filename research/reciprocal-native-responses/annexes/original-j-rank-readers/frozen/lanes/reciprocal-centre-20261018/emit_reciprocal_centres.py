#!/usr/bin/env python3
"""Emit and check the two reciprocal centre extensions.

Use a new output directory. Keep odd division separate from scalar gates.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import shutil
import time


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
PINS = {
    'new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz':
        ('gzip', 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'),
    'new-native-recipes-20261017/base/CLIFFORD-RECIPES.json':
        ('plain', '580dee1ca6d0a2971bc1dbe93558b8331bfa61662ce1736b24d944a55127b4f0'),
    'new-native-recipes-20261017/extra/CLIFFORD-RECIPES.json':
        ('plain', 'f3c678f44ac8c116376d707b088516b0c17744a8508f2863843b912738d2024e'),
    'interface-proof/verify_native_lift.py':
        ('plain', '087ad4cc683e5caf1f2a8cd62d5f65c9b4dde2636593b417f8f5099a29875c8b'),
    'independent-review-20261017/NEW-CORE-NATIVE-REVIEW.json':
        ('plain', '924b898621dd25ea9d3330563fdf7acf6c3b63dc99526e15faaee682f4bdd94d'),
    'bridge-review-20261017/odd-grid-a8-review-20261017/FREEZE.json':
        ('plain', '81ebbea971c0902a80479f9af4c82e72c660093c9f712b537690293aaaf21d60'),
}


def require(condition, label):
    if not condition:
        raise ValueError(label)


def digest(raw):
    return sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()


def load_inputs():
    values, pins = {}, {}
    for name, (mode, pin) in PINS.items():
        disk = (LANES / name).read_bytes()
        raw = gzip.decompress(disk) if mode == 'gzip' else disk
        require(digest(raw) == pin, 'Input pin: ' + name)
        pins[name] = {'content_sha256': pin, 'file_sha256': digest(disk), 'mode': mode}
        if name.endswith(('.json', '.json.gz')):
            values[name] = json.loads(raw)
    return values, pins


def scalar_cost(op):
    if op[0] in ('clear', 'copy'):
        return 2
    q = Q(*op[-2:])
    a, b = abs(q.numerator), q.denominator
    require(a and b & (b - 1) == 0, 'Nonzero dyadic scalar')
    if op[0] == 'scale':
        require(a & (a - 1) == 0, 'Power-of-two SCALE')
        return 2 * (abs(a.bit_length() - b.bit_length()) + int(q < 0))
    require(op[0] == 'add', 'Scalar opcode')
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def native(event):
    return event[0] in ('climb', 'warp', 'adapter', 'residual_adapter', 'center')


def add_scalar(events, target, source, coefficient, frame=0):
    q = Q(coefficient)
    require(q, 'Nonzero ADD')
    events.append(['scalar', ['add', target, source, q.numerator, q.denominator], frame])


def weighted_prefix(R, H, mapping, selected, backward):
    events = [['phase', 'weighted_centre_helper_correction']]
    C = ['C', 0]
    for j in range(8):
        events.append(['scalar', ['clear', C], 0])
        query = R[j] if backward else H[j]
        for field, value in sorted(query.items()):
            source = ['L', 112 + field if backward else mapping[field]]
            add_scalar(events, C, source, value / 4 if backward else value)
        if j in selected:
            events.append(['divide_odd', C, 13, 0])
        scatter = H[j] if backward else R[j]
        for field, value in sorted(scatter.items()):
            target = ['L', mapping[field] if backward else 112 + field]
            add_scalar(events, target, C, -value if backward else value / 4)
        events.append(['scalar', ['clear', C], 0])
    return events


def selected_blocks(source, selected, backward):
    require(len(source) == 208, 'Eight source centre blocks')
    result, bindings = [], []
    for j in range(8):
        block = deepcopy(source[26*j:26*(j+1)])
        calls = [e for e in block if e[0] == 'center']
        require(len(calls) == 1 and calls[0][1] == j and calls[0][4] == 8,
                'Source centre block shape')
        if j not in selected:
            continue
        require(block[0][0:2] == ['scalar', ['clear', ['C', j]]], 'Centre starts with CLEAR')
        require(block[-1][0:2] == ['scalar', ['clear', ['C', j]]], 'Centre ends with CLEAR')
        old_call = deepcopy(calls[0])
        start = len(result)
        for e in block:
            if e[0] == 'center':
                if backward:
                    result.append(['divide_odd', ['C', 0], 13, 0])
                e[1] = 0
                bindings.append({'centre': j, 'local_position': len(result),
                                 'source_event': old_call, 'event': deepcopy(e)})
                result.append(e)
                if not backward:
                    result.append(['divide_odd', ['C', 0], 13, 0])
                continue
            require(e[0] == 'scalar', 'Centre scalar event')
            op = e[1]
            for k, value in enumerate(op):
                if isinstance(value, list) and value[0] == 'C':
                    require(value == ['C', j], 'One owned field in each source block')
                    op[k] = ['C', 0]
            if op[0] == 'add' and e[2] == 0:
                require(Q(*op[-2:]) in (Q(1, 4), Q(-1, 4)), 'Source quarter coefficient')
                q = 12 * Q(*op[-2:])
                op[-2:] = [q.numerator, q.denominator]
            result.append(e)
        if backward:
            require(result[-1][1] == ['clear', ['C', 0]], 'Final owned CLEAR')
            result[-1][2] = 0
        require(len(result) - start == 27, 'One added division per retained block')
    return result, bindings


def make_word(provider, R, H, selected, backward):
    c = provider['canonical']
    mapping = {old: i for i, old in enumerate(list(range(224)) + c['helper_origin'])}
    require(len(mapping) == 632, 'Compact field namespace')
    require(all(c['start'][mapping[h]] == 0 and c['final'][mapping[h]] == 1
                for row in H for h in row), 'Helper correction has I input and FULL output')
    orientation = 'backward' if backward else 'forward'
    clean = provider['programs'][orientation]
    first = clean.index(['phase', 'zero_frame_precondition'])
    require(first == 832, 'Clean correction boundary')
    core = deepcopy(clean[first:])
    cut = core.index(['phase', 'centers']) + 1
    require(core[cut] == ['phase', 'B'], 'Empty centre cut')
    prefix = weighted_prefix(R, H, mapping, selected, backward)
    blocks, bindings = selected_blocks(provider['removed_centre_blocks'][orientation], selected, backward)
    program = prefix + core[:cut] + blocks + core[cut:]
    for binding in bindings:
        binding['position'] = len(prefix) + cut + binding.pop('local_position')
        require(program[binding['position']] == binding['event'], 'Exact centre occurrence binding')
    require([e for e in program if native(e) and e[0] != 'center'] ==
            [e for e in clean if native(e)], 'All non-centre native records are unchanged')
    return {'selected_centres': sorted(selected), 'program': program,
            'centre_bindings': bindings, 'weighted_prefix_events': len(prefix),
            'centre_block_events': len(blocks)}


def acc(target, source, coefficient):
    for key, value in source.items():
        new = target.get(key, 0) + coefficient * value
        if new:
            target[key] = new
        else:
            target.pop(key, None)


def height(row):
    result = 0
    for value in row.values():
        denominator, h = value.denominator, 0
        while denominator % 13 == 0:
            denominator //= 13
            h += 1
        require(denominator & (denominator - 1) == 0, 'Only dyadic and 13 denominators')
        result = max(result, h)
    return result


def unit(field):
    return {(field, ()): Q(1)}


def replay(word, c, R, backward):
    fields = [('L', i) for i in range(632)] + [('C', i) for i in range(8)]
    rows = {f: unit(f) for f in fields}
    frames = {('L', i): f for i, f in enumerate(c['start'])}
    frames.update({('C', i): 0 for i in range(8)})
    live_zero, allocated_zero = set(), set()
    divisions, child_heights, peak = [], Counter(), 0
    selected = set(word['selected_centres'])
    warp_classes = set(map(tuple, c['warp_edges']))

    def access(field):
        require(field in rows and (field[0] != 'Z' or field in live_zero),
                ('Live field access', field))

    for position, event in enumerate(word['program']):
        tag, changed = event[0], None
        if tag == 'scalar':
            op, frame = event[1:]
            f = tuple(op[1])
            access(f)
            changed = f
            if op[0] == 'clear':
                require(f[0] == 'C', ('Only owned fields can be cleared', position))
                rows[f], frames[f] = {}, frame
            elif op[0] in ('copy', 'add'):
                source = tuple(op[2])
                access(source)
                require(frames[f] == frames[source] == frame, ('Scalar frame', position))
                require(f != source, ('Distinct scalar fields', position))
                if op[0] == 'copy':
                    require(f[0] == 'C', ('Only owned fields can be copied over', position))
                    rows[f] = dict(rows[source])
                else:
                    acc(rows[f], rows[source], Q(op[3], op[4]))
            elif op[0] == 'scale':
                require(frames[f] == frame, ('SCALE frame', position))
                rows[f] = {k: Q(*op[2:]) * v for k, v in rows[f].items()}
            else:
                raise ValueError(('Scalar opcode', op))
            scalar_cost(op)
        elif tag == 'divide_odd':
            f, divisor, frame = tuple(event[1]), event[2], event[3]
            access(f)
            require(f == ('C', 0) and divisor == 13 and frames[f] == frame == 0,
                    ('Odd-division contract', position))
            before = height(rows[f])
            rows[f] = {k: v / divisor for k, v in rows[f].items()}
            divisions.append({'position': position, 'input_13_height': before,
                              'output_13_height': height(rows[f])})
            changed = f
        elif tag in ('climb', 'center'):
            if tag == 'climb':
                f, old, new, rank = ('L', event[2]), *event[3:]
            else:
                f, old, new, rank = ('C', event[1]), *event[2:]
                require(f == ('C', 0) and rank == 8, 'Serial rank-eight centre call')
            require(frames[f] == old, ('Native input frame', position, f))
            require(abs(len(c['frames'][new]) - len(c['frames'][old])) == rank,
                    ('Native rank', position))
            frames[f] = new
            child_heights[height(rows[f])] += 1
        elif tag == 'warp':
            f, symbol, old, new = tuple(event[1]), *event[2:]
            access(f)
            require(frames[f] == old, ('Warp input frame', position))
            require((1 if symbol > 0 else -1, abs(symbol), old, new) in warp_classes,
                    ('Signed warp class', position))
            frames[f] = new
            if backward:
                symbol = (abs(symbol) + 1000) * (1 if symbol > 0 else -1)
            rows[f] = {(source, word[1:] if word and word[0] == -symbol else (symbol,) + word): value
                       for (source, word), value in rows[f].items()}
            changed = f
        elif tag == 'zero_buffer':
            f = ('Z', event[2])
            if event[1] == 'alloc':
                require(f not in allocated_zero, 'Private field is allocated once')
                allocated_zero.add(f)
                live_zero.add(f)
                rows[f], frames[f] = {}, 1
            else:
                require(event[1] == 'free' and f in live_zero and not rows[f],
                        ('Private field is returned to zero', position))
                require(frames[f] == 1, ('Private field is returned at FULL', position))
                live_zero.remove(f)
        elif tag == 'adapter':
            _, side, field, frame = event
            require(side in ('old_to_new', 'new_to_old'), 'Adapter orientation')
            endpoint = c['start'] if side == 'old_to_new' else c['final']
            require(endpoint[field] == frame, 'Adapter endpoint')
        elif tag == 'residual_adapter':
            _, side, field, entry, *tail = event
            require(side in ('pre', 'post') and entry == c['start'][field]
                    and (tail[0] if tail else 1) == c['final'][field], 'Helper wrapper endpoints')
        else:
            require(tag == 'phase', ('Event grammar', tag))
        if changed is not None:
            peak = max(peak, height(rows[changed]))
    require(not live_zero and len(allocated_zero) == 91, 'All 91 private fields are released')
    for f in fields:
        kind, p = f
        expected = unit(f)
        if kind == 'C' and p == 0:
            expected = {}
        elif kind == 'L' and (p < 112 if backward else 112 <= p < 224):
            port = p if backward else p - 112
            base = 112 if backward else 0
            sign = -1 if backward else 1
            acc(expected, unit(('L', base + port)), sign)
            for j, row in enumerate(R):
                coefficient = -Q(1, 52) if j in selected else -Q(1, 4)
                for source, value in row.items():
                    acc(expected, unit(('L', base + source)),
                        sign * coefficient * row.get(port, 0) * value)
        require(rows[f] == expected, ('Complete response', backward, sorted(selected), f))
    require([frames['L', i] for i in range(632)] == c['final'], 'Every live output frame')
    require(all(frames['C', i] == 0 for i in range(8)), 'Every owned output frame is I')
    require(len(divisions) == 8 and all(d['input_13_height'] == 0 for d in divisions),
            'Eight divisions use complete queries with no new factor 13')
    require(peak == 1, 'All local prefixes have at most one new factor 13')
    return {'arbitrary_live_columns': 632, 'arbitrary_helper_columns': 408,
            'arbitrary_owned_columns': 8, 'C0_exit': 'zero at I',
            'C1_to_C7_exit': 'exact input value at I', 'private_fields_zero_at_release': 91,
            'all_live_endpoint_frames_checked': True,
            'max_prefix_13_height': peak, 'division_events': divisions,
            'child_input_13_height_counts': dict(sorted(child_heights.items()))}


def response(R, selected):
    return [[Q(i == j) - sum((Q(1, 52) if k in selected else Q(1, 4)) *
                             row.get(i, 0) * row.get(j, 0) for k, row in enumerate(R))
             for j in range(112)] for i in range(112)]


def multiply(a, b):
    columns = list(zip(*b))
    return [[sum(x*y for x, y in zip(row, column)) for column in columns] for row in a]


def check_reciprocal(R):
    gram = [[sum(R[i].get(p, 0) * R[j].get(p, 0) for p in range(112)) / 4
             for j in range(8)] for i in range(8)]
    require(gram == [[Q(14 * (i == j)) for j in range(8)] for i in range(8)], 'RK=14I')
    e, g = response(R, set(range(4))), response(R, set(range(4, 8)))
    identity = [[Q(i == j) for j in range(112)] for i in range(112)]
    require(multiply(e, g) == identity and multiply(g, e) == identity, 'Both full inverse orders')
    require(e == list(map(list, zip(*e))) and g == list(map(list, zip(*g))), 'Coordinate responses are symmetric')
    return {'dimension': 112, 'RK': '14 I_8', 'E_G': 'I_112', 'G_E': 'I_112',
            'symmetric_coordinate_responses': True}


def phase_checks(values, payload):
    path = LANES / 'interface-proof/verify_native_lift.py'
    spec = importlib.util.spec_from_file_location('reciprocal_native_phase', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {}
    for name, provider in payload['providers'].items():
        c = provider['canonical']
        recipes = values['new-native-recipes-20261017/' + name + '/CLIFFORD-RECIPES.json']['children']
        lookup = {(r['old'], r['new']): r for r in recipes}
        selected = []
        for f in c['center_frames']:
            for old, new in ((f, 0), (0, f)):
                r = lookup[old, new]
                require(r['rank'] == 8, 'Retained centre rank')
                circuit = module.adjoint(module.frame(c['frames'][old], 9)) + module.frame(c['frames'][new], 9)
                module.equal(module.recipe(r), circuit, name + ' centre ' + str((old, new)))
                selected.append(r)
        provider['centre_recipes'] = selected
        for word in provider['words'].values():
            for binding in word['centre_bindings']:
                _, target, old, new, rank = binding['event']
                require(target == 0 and rank == 8 and (old, new) in lookup,
                        'C0 centre occurrence has exact recipe')
                binding['recipe_key'] = [old, new]
                binding['recipe_sha256'] = digest(encode(lookup[old, new]))
        result[name] = {'centre_recipes_checked': 16, 'Paulis_per_recipe': 18,
                        'Gaussian_state_dimension_per_recipe': 512,
                        'global_phase_checked': True, 'bound_centre_occurrences': 16}
        changed = deepcopy(selected[0])
        changed['left']['phase'] = (changed['left']['phase'] + 1) % 4
        try:
            module.equal(module.recipe(changed), module.recipe(selected[0]), 'Changed global phase')
        except ValueError as error:
            require('global phase' in str(error), 'Phase mutation fails the exact state check')
            result[name]['global_phase_mutation_rejected'] = True
        else:
            raise ValueError('Global phase mutation was accepted')
    return result


def negative_controls(payload, R):
    provider = payload['providers']['base']
    original = provider['words']['E_forward']
    controls = {}
    for label in ('omit_helper_division', 'change_centre_scatter_sign', 'change_centre_frame'):
        changed = deepcopy(original)
        events = changed['program']
        if label == 'omit_helper_division':
            position = next(i for i, e in enumerate(events) if e[0] == 'divide_odd')
            events.pop(position)
        elif label == 'change_centre_scatter_sign':
            position = changed['centre_bindings'][0]['position'] + 2
            require(events[position][0] == 'scalar' and events[position][1][0] == 'add',
                    'Mutation addresses the first centre scatter')
            events[position][1][3] *= -1
        else:
            position = changed['centre_bindings'][0]['position']
            events[position][2] = 0
        try:
            replay(changed, provider['canonical'], R, False)
        except ValueError as error:
            controls[label] = str(error)
        else:
            raise ValueError('Mutation was accepted: ' + label)
    e = response(R, set(range(4)))
    require(multiply(e, e) != [[Q(i == j) for j in range(112)] for i in range(112)],
            'Using the same centre projection twice must fail')
    controls['same_projection_for_both_responses'] = 'E E is not I'
    return controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Output directory must be new')
    require(shutil.disk_usage(HERE).free >= 3 * 1024**3, 'At least 3 GiB free disk')
    start = time.monotonic()
    values, pins = load_inputs()
    source = values['new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz']
    R = [{int(k): Q(v) for k, v in row.items()} for row in source['R']]
    H = [{int(k): Q(v) for k, v in row.items()} for row in source['H']]
    payload = {'schema': 'reciprocal-centre-native-v1', 'R': source['R'], 'H': source['H'],
               'providers': {}, 'source_pins': pins,
               'odd_division_opcode': ['divide_odd', ['C', 0], 13, 0]}
    receipt = {'status': 'PASS_RECIPROCAL_CENTRE_NATIVE_PRODUCER', 'providers': {},
               'reciprocity': check_reciprocal(R)}
    for name, provider in source['providers'].items():
        payload['providers'][name] = {'canonical': provider['canonical'], 'words': {}}
        checks = {}
        for response_name, selected in (('E', set(range(4))), ('G', set(range(4, 8)))):
            for orientation in ('forward', 'backward'):
                backward = orientation == 'backward'
                key = response_name + '_' + orientation
                word = make_word(provider, R, H, selected, backward)
                check = replay(word, provider['canonical'], R, backward)
                profile = Counter(e[5] for e in word['program'] if e[0] == 'climb')
                profile.update(e[4] for e in word['program'] if e[0] == 'center')
                require(profile == {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 4}, 'Native profile')
                scalar_bill = sum(scalar_cost(e[1]) for e in word['program'] if e[0] == 'scalar')
                require(scalar_bill == (165618 if backward else 165594), 'Complete dyadic scalar invoice')
                check.update(events=len(word['program']), native_profile=dict(sorted(profile.items())),
                             native_children=sum(profile.values()), native_mass=sum(k*v for k, v in profile.items()),
                             dyadic_real_primitives=scalar_bill, complex_divisions_by_13=8,
                             real_division_scans=16, division_head_steps_bound='64 (w_g + 1)',
                             all_owned_zero_exit_extra_dyadic_primitives=14,
                             ordinary_native_records_unchanged=True)
                payload['providers'][name]['words'][key] = word
                checks[key] = check
                print(name, key, scalar_bill, 3511, 5105, 'PASS', flush=True)
        receipt['providers'][name] = checks
    receipt['centre_phase_checks'] = phase_checks(values, payload)
    receipt['negative_controls'] = negative_controls(payload, R)
    receipt['source_pins'] = pins
    receipt['scope'] = ('Literal local rational couplers on all 640 input columns. E and G are not completed '
                        'dyadic recursive providers. All ordinary native records retain the pinned phase proof. '
                        'All 32 centre recipes receive fresh exact Pauli and Gaussian-state checks. No global '
                        'controller, child hosting, full binary precision guard, or complete kappa claim.')
    raw = encode(payload)
    disk = gzip.compress(raw, mtime=0)
    receipt.update(payload_sha256=digest(raw), payload_file_sha256=digest(disk),
                   emitter_sha256=digest(Path(__file__).read_bytes()),
                   elapsed_seconds=round(time.monotonic() - start, 3))
    args.out.mkdir(parents=True)
    (args.out / 'RECIPROCAL-CENTRE-PROGRAMS.json.gz').write_bytes(disk)
    (args.out / 'RECIPROCAL-CENTRE-RECEIPT.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(receipt['status'], receipt['payload_sha256'], flush=True)


if __name__ == '__main__':
    main()
