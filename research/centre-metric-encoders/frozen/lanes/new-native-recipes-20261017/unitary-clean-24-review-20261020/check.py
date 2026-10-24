#!/usr/bin/env python3
"""Check complete complex blocks and their native field types."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import importlib.util
import json

HERE = Path(__file__).resolve().parent
HELPER = HERE.parent/'row-capture-native-review-20261020/check.py'
PIN = '5b8f2839db4fd4b0e4b24d5b8f8938c74a15497ae0e58f324896cf431d3ecb84'
if sha256(HELPER.read_bytes()).hexdigest() != PIN:
    raise ValueError('Independent helper pin')
spec = importlib.util.spec_from_file_location('independent_real_arithmetic', HELPER)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
q.read(HELPER, PIN)
need = q.need
SOURCE = q.RAW/'unitary-clean-24-20261020'
CODE = q.RAW/'metric-completion-20261020'


def realify(matrix, size):
    result = [{} for _ in range(2*size)]
    need(len(matrix) == size, 'Square complex matrix')
    for p, row in enumerate(matrix):
        for raw_j, (raw_a, raw_b) in row.items():
            j, a, b = int(raw_j), F(raw_a), F(raw_b)
            need(0 <= j < size, 'Complex matrix column')
            for t, s, value in ((2*p, 2*j, a), (2*p, 2*j+1, -b),
                                 (2*p+1, 2*j, b), (2*p+1, 2*j+1, a)):
                if value:
                    result[t][s] = value
    return result


def component_real(gate):
    op, target, source, value = gate
    return [[op, 2*target+c, None if source is None else 2*source+c, value]
            for c in (0, 1)]


def component_dual(gates, permutation):
    def p(k):
        return 2*permutation[k//2]+k % 2
    result = []
    for op, target, source, value in gates:
        value = F(value)
        if op == 'add':
            result.append(['add', p(source), p(target), str(-value)])
        else:
            need(op == 'scale' and source is None and value, 'Invertible component scale')
            result.append(['scale', p(target), None, str(1/value)])
    return result


def flatten(events):
    result = []
    for event in events:
        if event[0] == 'native':
            continue
        if event[0] == 'scalar':
            result += component_real(event[1])
        elif event[0] == 'gaussian_add':
            result += event[5]
        else:
            need(event[0] == 'component_code', 'Complete event grammar')
            result += event[2]
    return result


def endpoint(code, selected):
    c = realify(code, 112)
    result = q.unit(1280)
    for p in range(112):
        for b in (0, 1):
            x, y = 2*p+b, 224+2*p+b
            result[x] = {y: F(-1)} if p in selected else dict(c[x])
            result[y] = dict(c[x])
            if p not in selected:
                q.add(result[y], {y: F(1)})
    return result


def inverse_endpoint(code, selected):
    c = realify(code, 112)
    z = [{224+j if j//2 in selected else j: F(1)} for j in range(224)]
    x = q.mul(q.transpose(c, 224), z)
    result = q.unit(1280)
    result[:224] = x
    for p in range(112):
        for b in (0, 1):
            j = 2*p+b
            result[224+j] = {j: F(-1)} if p in selected else {224+j: F(1), j: F(-1)}
    return result


def conjugate(matrix, permutation):
    cp = [2*permutation[j//2]+j % 2 for j in range(1280)]
    return [{cp[j]: value for j, value in matrix[cp[i]].items()} for i in range(1280)]


def swap_formula(code, selected):
    c = realify(code, 112)
    source = [224+j if j//2 in selected else j for j in range(224)]
    result = q.unit(1280)
    for p in range(112):
        for b in (0, 1):
            j = 2*p+b
            result[j] = {source[k]: value for k, value in c[j].items()}
            if p in selected:
                result[224+j] = {j: F(-1)}
            else:
                q.add(result[j], {224+j: F(-1)})
    return result


def local_block(fields, gates, expected):
    need(len(fields) == len(set(fields)), 'Distinct fields in a complete block')
    index = {p: i for i, p in enumerate(fields)}
    local = []
    for op, t, s, value in gates:
        need(t//2 in index and (s is None or s//2 in index), 'No field outside its block')
        need(op in ('add', 'scale') and (op != 'add' or t != s), 'Component opcode')
        local.append([op, 2*index[t//2]+t % 2,
                      None if s is None else 2*index[s//2]+s % 2, value])
    need(q.reverse(local, 2*len(fields)) == q.transpose(expected, 2*len(fields)),
         'Complete block real matrix, including complex linearity')
    rows, bound = q.prefix(local, 2*len(fields))
    need(rows == expected, 'Separate block forward replay')
    return bound


def trace(word, selected, entry, expected, block_cache):
    current = list(word['start'])
    profile, used = Counter(), set()
    maximum_local, maximum_height = F(1), 0
    for event in word['events']:
        kind = event[0]
        if kind == 'native':
            _, field, before, after, rank, key = event
            need(0 <= field < 224 and current[field] == before, 'Actual native input field and frame')
            need(word['native_recipes'][key]['rank'] == rank, 'Actual native child rank')
            current[field] = after
            profile[rank] += 1
            used.add(key)
            continue
        if kind == 'scalar':
            _, gate, frame = event
            op, target, origin, _ = gate
            need(0 <= target < 224 and current[target] == frame, 'Complex-real scalar target')
            if op == 'add':
                need(0 <= origin < 224 and origin != target and current[origin] == frame,
                     'Complex-real scalar source')
            else:
                need(op == 'scale' and origin is None, 'Complex-real scale grammar')
            continue
        if kind == 'gaussian_add':
            _, target, origin, value, frame, gates = event
            need(target != origin, 'Gaussian ADD needs distinct fields')
            fields = [target, origin]
            a, b = map(F, value)
            need(a or b, 'A nonzero Gaussian transfer')
            matrix = [{0: F(1)}, {1: F(1)}, {2: F(1)}, {3: F(1)}]
            q.add(matrix[0], {2: a, 3: -b})
            q.add(matrix[1], {2: b, 3: a})
            matrix = [{j: v for j, v in row.items() if v} for row in matrix]
        else:
            need(kind == 'component_code', 'Only complete component blocks are admitted')
            _, fields, gates, matrix_raw, frame = event
            matrix = realify(matrix_raw, len(fields))
        need(all(0 <= field < 224 and current[field] == frame for field in fields),
             'One common complex frame at both block boundaries')
        key = json.dumps([fields, gates, matrix], sort_keys=True, default=str)
        if key not in block_cache:
            block_cache[key] = local_block(fields, gates, matrix)
        bound = block_cache[key]
        maximum_local = max(maximum_local, F(bound['row_one_norm']))
        maximum_height = max(maximum_height, bound['binary_height'])
    need(current == word['final'] and len(current) == 640, 'All640 final frames')
    need(used == set(word['native_recipes']), 'Every stored recipe has an occurrence')
    rank = 9 if entry == 'I' else 8
    need(profile == {1: 1328, 2: 64, 3: 48, rank: 24}, 'Complete native profile')
    need(current[224:] == word['start'][224:], 'Unchanged helper frames')
    gates = flatten(word['events'])
    columns = q.reverse(gates, 1280)
    need(columns == q.transpose(expected, 1280), 'All1280 independent reverse input columns')
    need(all(t < 448 and (s is None or s < 448) for _, t, s, _ in gates),
         'No component instruction touches an arbitrary helper')
    costs = {}
    cursor = 0
    for name, (start, end) in sorted(word['stage_ranges'].items(), key=lambda item: item[1][0]):
        need(start == cursor and start <= end, 'Complete ordered stage cuts')
        cursor = end
        cost = q.price(flatten(word['events'][start:end]))
        need(cost % 2 == 0, 'Integral real-component cost')
        costs[name] = cost//2
    need(cursor == len(word['events']), 'Stage ledger covers the complete word')
    need(costs['source_unitary_code'] == 8052 and costs['signed_selected_exchanges'] == 576,
         'Paid code and all24 rotations')
    total = q.price(gates)//2
    need(total == sum(costs.values()), 'Complete scalar invoice')
    need(costs == {'retained_retuned_core': 7392, 'selected_progress': 0,
                   'source_unitary_code': 8052, 'signed_selected_exchanges': 576}
         and total == 16020, 'All exact stage invoices')
    state = q.unit(1280)
    endpoint_norm, endpoint_height = F(1), 0
    for event in word['events']:
        changed = set()
        for op, target, origin, value in flatten([event]):
            value = F(value)
            if op == 'scale':
                state[target] = {j: value*x for j, x in state[target].items()}
            else:
                q.add(state[target], state[origin], value)
            changed.add(target)
        for target in changed:
            endpoint_norm = max(endpoint_norm, sum(map(abs, state[target].values()), F(0)))
            for value in state[target].values():
                denominator = value.denominator
                need(denominator & (denominator-1) == 0, 'Dyadic macro endpoint')
                endpoint_height = max(endpoint_height, denominator.bit_length()-1)
    need(state == expected and state[448:] == q.unit(1280)[448:],
         'Separate forward trace and all416 arbitrary complex helper outputs')
    return {
        'real_input_columns': 1280, 'complex_input_columns': 640,
        'unchanged_arbitrary_complex_fields': 416,
        'native_profile': dict(sorted(profile.items())),
        'native_children': sum(profile.values()),
        'native_mass': sum(k*v for k, v in profile.items()),
        'native_side_maps_upper_bound': 2*(sum(profile.values())-(24 if entry == 'I' else 0)),
        'input_views': len(word['input_views']), 'output_views': len(word['output_views']),
        'scalar_stage_prices': costs, 'real_scalar_primitives': total,
        'component_instructions': len(gates), 'new_fields': 0, 'private_fields': 0,
        'odd_divisions': 0, 'maximum_local_block_component_row_norm': str(maximum_local),
        'maximum_local_block_binary_height': maximum_height,
        'maximum_macro_endpoint_content_component_norm': str(endpoint_norm),
        'maximum_macro_endpoint_content_binary_height': endpoint_height,
        'bound_scope': 'Each complete block has a complex frame. Its internal component bound uses its physical input components.',
    }


def forward_source(word, old, model, formation, code, cyclic, selected, entry):
    need(word['frames'] == old['frames'], 'Unchanged literal frame table')
    selected_fields = {112+p for p in selected}
    kept_indices, removed = q.select_raw(old, selected_fields)
    need(word['retained_original_event_indices'] == kept_indices, 'Exact removal index ledger')
    need(len(removed) == 380 and
         Counter(old['events'][i][4] for i in removed if old['events'][i][0] == 'native') == {1: 192},
         'Exact380-event and192-H1 removal census')
    need(all(not (e[0] == 'native' and e[1] in selected_fields) and
                 not (e[0] == 'scalar' and (e[1][1] in selected_fields or
                      e[1][0] == 'add' and e[1][2] in selected_fields))
             for e in [old['events'][i] for i in kept_indices]),
         'No retained access to a removed selected target')
    records = {r['event']: r for r in old['transfer_records']}
    need(len(records) == len(old['transfer_records']), 'Unique original transfer sites')
    params = {r['id']: r for r in cyclic['parameters']}
    mode = code['mode_code']
    start, end = word['stage_ranges']['retained_retuned_core']
    need(start == 0, 'The core is first')
    core = word['events'][start:end]
    cursor, retunings = 0, []
    for i in kept_indices:
        old_event = old['events'][i]
        if i not in records:
            need(core[cursor] == old_event, 'Every nontransfer core event is byte-equal')
            cursor += 1
            continue
        record = records[i]
        if record['part'] == 'large48':
            par = params[record['parameter']]
            ports = cyclic['cyclic_carriers'][par['vertex']]
            p, j = ports[par['row']], ports[par['column']]
            old_coefficient = F(model['mode_response'][p][str(j)])
        else:
            need(record['part'] == 'small64', 'Transfer source part')
            p, j = record['target_port'], record['source_port']
            old_coefficient = F(model['response'][p][str(j)])
        op, target, origin, old_value = old_event[1]
        need(op == 'add' and target == 112+p and origin == j and p not in selected,
             'Actual ordinary transfer fields')
        need(F(record['coefficient']) == F(old_value), 'Accepted scalar transfer coefficient')
        a, b = map(F, mode[p].get(str(j), ['0', '0']))
        ratio = F(old_value)/old_coefficient
        a, b = ratio*a, ratio*b
        retunings.append({'original_event': i, 'mode_target': p, 'mode_source': j,
                          'coefficient': [str(a), str(b)]})
        if not (a or b):
            continue
        expected = ['gaussian_add', target, origin, [str(a), str(b)], old_event[2]]
        need(core[cursor][:5] == expected, 'Actual retuned transfer and common frame')
        cursor += 1
    need(cursor == len(core) and word['transfer_retunings'] == retunings,
         'Complete retuned transfer census')
    input_views = [{**v, 'field': v['port']} for v in formation['input_views']]
    source_views = {v['port']: v for v in formation['input_views']}
    before = list(old['start'])
    progress = []
    for p in sorted(selected):
        if entry == 'I':
            key, old_frame, rank = 'direct-full', 0, 9
            need(word['native_recipes'][key] == formation['native_recipes']['capture-full'],
                 'Exact accepted direct F9 recipe')
        else:
            key, old_frame, rank = 'unitary-line:'+str(p), old['start'][p], 8
            before[112+p] = old_frame
            input_views.append({**source_views[p], 'field': 112+p,
                                'role': 'selected_target', 'source_entry_port': p})
        progress.append(['native', 112+p, old_frame, 1, rank, key])
    after = list(old['final'])
    for p in selected:
        after[112+p] = 1
    need(word['start'] == before and word['final'] == after, 'All actual endpoint frame declarations')
    need(word['input_views'] == sorted(input_views, key=lambda v: v['field']),
         'Every input adapter is bound to its actual complex field')
    need(word['output_views'] == [v for v in formation['output_views'] if v['port'] not in selected],
         'Every ordinary inverse target adapter is inherited')
    code_block = [['component_code', list(range(112)), code['component_words']['code'], code['code'], 1]]
    rotations = []
    for p in sorted(selected):
        rotations += [['scalar', ['add', 112+p, p, '1'], 1],
                      ['scalar', ['add', p, 112+p, '-1'], 1],
                      ['scalar', ['add', 112+p, p, '1'], 1]]
    need(word['events'] == core+progress+code_block+rotations, 'Complete forward chronology')
    stages = [('retained_retuned_core', core), ('selected_progress', progress),
              ('source_unitary_code', code_block), ('signed_selected_exchanges', rotations)]
    expected_ranges, at = {}, 0
    for name, events in stages:
        expected_ranges[name] = [at, at+len(events)]
        at += len(events)
    need(word['stage_ranges'] == expected_ranges, 'Exact complete stage boundaries')
    for event in core:
        if event[0] == 'native':
            need(word['native_recipes'][event[5]] == old['native_recipes'][event[5]],
                 'Byte-equal retained exact-phase recipe')
    return {'removed_events': len(removed), 'removed_H1_children': 192,
            'retained_transfer_slots': len(retunings),
            'nonzero_gaussian_transfers': sum(e[0] == 'gaussian_add' for e in core)}


def dual_source(word, original, permutation):
    need(word['stage_ranges'] == original['stage_ranges'], 'Dual preserves macro chronology')
    need(word['wire_permutation'] == {str(p): t for p, t in enumerate(permutation) if p != t},
         'Exact field permutation')
    for key in ('frames', 'start', 'final', 'native_recipes', 'output_views'):
        need(word[key] == original[key], 'Exact dual physical record: '+key)
    need(all(original[key][p] == original[key][permutation[p]]
             for key in ('start', 'final') for p in range(640)), 'Selected endpoint symmetry')
    expected_views = deepcopy(original['input_views'])
    for view in expected_views:
        view['field'] = permutation[view['field']]
    need(word['input_views'] == sorted(expected_views, key=lambda v: v['field']),
         'Every dual input adapter is explicitly rebound')
    original_views = {v['field']: v for v in original['input_views']}
    for view in word['input_views']:
        need(all(view[k] == original_views[view['field']][k]
                 for k in ('port', 'frame', 'rank', 'left', 'right')),
             'Same-port Q/Q phase identity at each input field')
    need(len(word['events']) == len(original['events']), 'No hidden runtime exchanges')
    for event, old in zip(word['events'], original['events']):
        kind = old[0]
        if kind == 'native':
            expected = deepcopy(old)
            expected[1] = permutation[old[1]]
        elif kind == 'scalar':
            op, target, source, value = old[1]
            value = F(value)
            gate = (['add', permutation[source], permutation[target], str(-value)] if op == 'add'
                    else ['scale', permutation[target], None, str(1/value)])
            expected = ['scalar', gate, old[2]]
        elif kind == 'gaussian_add':
            _, target, source, value, frame, components = old
            a, b = map(F, value)
            expected = ['gaussian_add', permutation[source], permutation[target],
                        [str(-a), str(b)], frame, component_dual(components, permutation)]
        else:
            need(kind == 'component_code', 'Dual block grammar')
            _, fields, components, matrix, frame = old
            expected = ['component_code', [permutation[p] for p in fields],
                        component_dual(components, permutation), matrix, frame]
        need(event == expected, 'Literal chronological real inverse-transpose and field rebind')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-freeze', required=True)
    parser.add_argument('--payload-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    q.frozen(SOURCE, 'FREEZE.json', args.source_freeze)
    q.frozen(CODE, 'TWENTY-FOUR-FREEZE.json',
             '3fda436c0390fb8ef2ee72b4d9fe6ccbfc0ea994208f4d962bb9f43960af7a82')
    q.frozen(q.LANES/'independent-review-20261017/unitary-footprint-review-20261020', 'FREEZE.json',
             'c537f75e6b76397e8fa390cd03a01e8021b7e0e55ff6c8932c3cc439613d0a61')
    q.frozen(HERE.parent/'row-capture-native-review-20261020', 'FREEZE.json',
             '488dc693d6e7d48e8024455c9c3f2f899f94a8e9058aef28ad38f7c46c7d8532')
    q.frozen(HERE.parent/'line-entry-reuse-review-20261020', 'FREEZE.json',
             'cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c')
    phase = q.inherit()
    payload = json.loads(q.read(SOURCE/'run-v2-normal/UNITARY-CLEAN.json.gz', args.payload_sha256, True))
    code = json.loads(q.read(CODE/'twenty-four-v2-normal/UNITARY-24.json.gz',
                             '9be7deb70acfc20d98408c84d59a24dbd6e2eddaea408958ec64b6003eb75f8c', True))
    raw = json.loads(q.read(q.RAW/'odd16-normal-v2/EXTENSION-PROGRAM.json.gz',
                            'd466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4', True))
    formation = json.loads(q.read(q.NATIVE/'direct-normal/DIRECT-FULL-CAPTURE.json.gz',
                                  'fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c', True))
    reuse = json.loads(q.read(q.NATIVE/'reuse-normal/LINE-ENTRY-REUSE.json.gz',
                              'efe67a962752f2c36513d84094d215fd0909a5360707938ff99d62743dc72110', True))
    cyclic = json.loads(q.read(q.LANES/'independent-review-20261017/cyclic-pair-flags-20261018/CYCLIC-FLAGS.json',
                               '3034e1df3670f64e5b79a51a435d7903f3be7cef10d6b486a8bd4d420c989585'))
    selected = set(code['selected_full_ports'])
    need(len(selected) == 24 and payload['selected_ports'] == sorted(selected), 'Actual24 selected ports')
    need(payload['ports'] == raw['model']['ports'] and payload['code'] == code['code'] and
         payload['inverse_and_adjoint_code'] == code['inverse_and_adjoint'], 'Exact matrix and port sources')
    c = realify(code['code'], 112)
    need(q.mul(c, q.transpose(c, 224)) == q.unit(224) and
         q.mul(q.transpose(c, 224), c) == q.unit(224), 'Both real unitary orders')
    f, fi = endpoint(code['code'], selected), inverse_endpoint(code['code'], selected)
    identity = list(range(640))
    swap = [112+p if p in selected else p-112 if p-112 in selected else p for p in range(640)]
    d, di = q.transpose(fi, 1280), q.transpose(f, 1280)
    b, bi = conjugate(d, swap), conjugate(di, swap)
    need(b == swap_formula(code['code'], selected), 'Separate unitary Bswap block formula')
    maps = {'forward_I': f, 'forward_Q': f, 'inverse_adjoint_Q': d, 'selected_conjugate_Q': b}
    inverses = {'forward_I': fi, 'forward_Q': fi, 'inverse_adjoint_Q': di, 'selected_conjugate_Q': bi}
    for name in maps:
        need(realify(payload['content_maps'][name], 224) == maps[name][:448],
             'Exact serialized content map: '+name)
        need(realify(payload['inverse_content_maps'][name], 224) == inverses[name][:448],
             'Exact serialized inverse map: '+name)
        need(q.mul(maps[name][:448], inverses[name][:448]) == q.unit(448) and
             q.mul(inverses[name][:448], maps[name][:448]) == q.unit(448), 'Both complete inverse orders')
    need(set(payload['providers']) == {'base', 'extra'}, 'Both actual providers')
    reports, phase_reports, cache = {}, {}, {}
    phase_seen = {}
    for provider, words in payload['providers'].items():
        need(set(words) == set(maps), 'All four complete local variants')
        reports[provider] = {}
        for name, word in words.items():
            entry = 'I' if name == 'forward_I' else 'Q'
            if name.startswith('forward'):
                source_report = forward_source(word, raw['providers'][provider]['forward'],
                                               raw['model'], formation['providers'][provider],
                                               code, cyclic, selected, entry)
            else:
                dual_source(word, words['forward_Q'], identity if name == 'inverse_adjoint_Q' else swap)
                source_report = {'chronological_inverse_adjoint': True, 'runtime_boundary_swaps': 0}
            reports[provider][name] = {**trace(word, selected, entry, maps[name], cache), **source_report}
        line_word = words['forward_Q']
        for p in sorted(selected):
            before = line_word['start'][112+p]
            record = line_word['native_recipes']['unitary-line:'+str(p)]
            if p in q.P:
                accepted = reuse['providers'][provider]
                need(record == accepted['native_recipes']['capture-line:'+str(p)] and
                     line_word['frames'][before] == accepted['frames'][accepted['start'][112+p]],
                     'Exact accepted line-to-FULL phase and ordered input basis')
                phase_reports[provider+':'+str(p)] = {'inherited_review': 'cc5ed3b0ecc6eb5cec48f8baead43ec813042c3e83cd68104b7745366c13c55c'}
                continue
            signature = json.dumps([line_word['frames'][before], record], sort_keys=True)
            if signature not in phase_seen:
                native = phase.recipe(record)
                full = [('C', 1 << j, 1) for j in range(9)]
                phase_seen[signature] = phase.compare(phase.canonical(line_word['frames'][before])+native,
                                                      full, 'Actual selected line '+str(p), 512)
            phase_reports[provider+':'+str(p)] = phase_seen[signature]
    # The controls use executed component instructions and exact physical phase.
    gates = flatten(payload['providers']['base']['forward_Q']['events'])
    first_complex = next(e for e in payload['providers']['base']['forward_Q']['events']
                         if e[0] == 'gaussian_add' and F(e[3][1]))
    bad_macro = deepcopy(first_complex[5])
    bad_macro[0][3] = str(-F(bad_macro[0][3]))
    need(q.reverse(bad_macro, 1280) != q.reverse(first_complex[5], 1280), 'Wrong complex sign control')
    need(q.reverse(list(reversed(gates)), 1280) != q.transpose(f, 1280),
         'Wrong chronological order control')
    record = payload['providers']['base']['forward_Q']['native_recipes']['unitary-line:'+str(min(selected))]
    bad = phase.recipe(record)+phase.compile_circuit([['phase', 1]])
    need(phase.run(bad, 0) != phase.run(phase.recipe(record), 0), 'Wrong global phase control')
    result = {
        'status': 'PASS_INDEPENDENT_UNITARY_24_CLEAN_NATIVE',
        'producer_freeze_sha256': args.source_freeze, 'payload_decompressed_sha256': args.payload_sha256,
        'words': reports, 'selected_line_full_phase_checks': phase_reports,
        'distinct_selected_line_recipes_checked': len(phase_seen),
        'complex_block_cache_entries': len(cache), 'both_content_inverse_orders': True,
        'negative_controls': ['wrong Gaussian component sign', 'wrong scalar chronology', 'wrong native global phase'],
        'scope': 'Eight complete local physical words on640 arbitrary complex fields. Every real component block closes before any native or map event. No routed caller, recursive hosting, rounding bound or complete supplier cost is claimed.',
    }
    args.out.mkdir(parents=True, exist_ok=False)
    for name, obj in [('REVIEW.json', result), ('INPUTS.json', q.INPUTS)]:
        (args.out/name).write_text(json.dumps(obj, sort_keys=True, indent=2)+'\n')
    print(result['status'], flush=True)


if __name__ == '__main__':
    main()
