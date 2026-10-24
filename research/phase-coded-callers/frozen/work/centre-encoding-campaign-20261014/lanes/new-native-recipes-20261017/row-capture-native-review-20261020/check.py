#!/usr/bin/env python3
"""Check the selected-row code and its complete native service."""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json

HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
INPUTS = {}
P = [0, 27, 36, 111, 20, 7, 57, 46, 1, 3, 6, 8, 17, 18, 24, 23]
RAW = LANES/'new-core-transfer-20261017/low-displacement-20261020'
ALG = LANES/'controller-followthrough-20261017/row-capture-20261020'
NATIVE = RAW/'row-only-capture-20261020'
ACCEPTED = LANES/'new-native-recipes-20261017/low-displacement-review-20261020'


def need(test, message):
    if not test:
        raise ValueError(message)


def read(path, pin=None, compressed=False):
    data = path.read_bytes()
    content = gzip.decompress(data) if compressed else data
    need(pin is None or sha256(content).hexdigest() == pin,
         'Input pin: '+str(path))
    INPUTS[str(path.relative_to(LANES))] = {'sha256': sha256(data).hexdigest()}
    if compressed:
        INPUTS[str(path.relative_to(LANES))]['decompressed_sha256'] = sha256(content).hexdigest()
    return content


def frozen(path, name, pin):
    obj = json.loads(read(path/name, pin))
    for name, digest in obj['files'].items():
        read(path/name, digest)
    return obj


def rows(value):
    return [{int(k): F(v) for k, v in row.items() if F(v)} for row in value]


def unit(n):
    return [{i: F(1)} for i in range(n)]


def add(target, source, coefficient=F(1)):
    for key, value in source.items():
        x = target.get(key, F(0))+coefficient*value
        if x:
            target[key] = x
        else:
            target.pop(key, None)


def mul(a, b):
    out = []
    for row in a:
        result = {}
        for k, v in row.items():
            add(result, b[k], v)
        out.append(result)
    return out


def rank(a):
    pivots = {}
    for original in a:
        row = dict(original)
        while row:
            j = min(row)
            if j not in pivots:
                value = row[j]
                pivots[j] = {k: v/value for k, v in row.items()}
                break
            add(row, pivots[j], -row[j])
    return len(pivots)


def transpose(a, n):
    out = [{} for _ in range(n)]
    for i, row in enumerate(a):
        for j, v in row.items():
            out[j][i] = v
    return out


def price(events):
    total = 0
    for op, _, _, value in events:
        c = F(value)
        n, d = abs(c.numerator), c.denominator
        need(n > 0 and d & (d-1) == 0, 'Nonzero dyadic coefficient')
        if op == 'scale':
            need(n & (n-1) == 0, 'Dyadic unit scale')
            total += 2*(abs(n.bit_length()-d.bit_length())+(c < 0))
        else:
            need(op == 'add', 'Scalar opcode')
            total += 2*(3+n.bit_length()-1+n.bit_count()+d.bit_length()-1)
    return total


def reverse(events, n):
    """Propagate output columns through the scalar word in reverse order."""
    columns = unit(n)
    for op, target, origin, value in reversed(events):
        c = F(value)
        if op == 'scale':
            columns[target] = {k: c*v for k, v in columns[target].items()}
        else:
            need(op == 'add' and target != origin, 'Distinct ADD fields')
            add(columns[origin], columns[target], c)
    return columns


def prefix(events, n):
    """Compute exact prefix rows, separately from the reverse pass."""
    state = unit(n)
    norm, height = F(1), 0
    for op, target, origin, value in events:
        c = F(value)
        if op == 'scale':
            state[target] = {k: c*v for k, v in state[target].items()}
        else:
            add(state[target], state[origin], c)
        norm = max(norm, sum(map(abs, state[target].values()), F(0)))
        for x in state[target].values():
            d = x.denominator
            need(d & (d-1) == 0, 'Dyadic prefix coefficient')
            height = max(height, d.bit_length()-1)
    return state, {'row_one_norm': str(norm), 'binary_height': height}


def algebra(raw, code):
    model = raw['model']
    e, u, v = (rows(model[name]) for name in ('response', 'correction_U', 'correction_V'))
    uv = mul(u, v)
    expected_e = unit(112)
    for row, correction in zip(expected_e, uv):
        add(row, correction)
    need(e == expected_e, 'Actual response factorization')
    vp = [{j: row[p] for j, p in enumerate(P) if p in row} for row in v]
    # The actual pivot blocks are signed two-coordinate Hadamards and units.
    vp_t = transpose(vp, 16)
    gram = [{i: F(2 if i < 8 else 1)} for i in range(16)]
    need(mul(vp, vp_t) == gram, 'Actual pivot Gram matrix')
    vi = [{j: x/(2 if j < 8 else 1) for j, x in row.items()} for row in vp_t]
    need(mul(vi, vp) == unit(16) and mul(vp, vi) == unit(16), 'Pivot inverse orders')
    w = mul(vi, v)
    c, ci, b = unit(112), unit(112), []
    for i, p in enumerate(P):
        need({j: w[i].get(q, F(0)) for j, q in enumerate(P)} ==
             {j: F(i == j) for j in range(16)}, 'Normalized pivot columns')
        c[p] = dict(w[i])
        correction = dict(w[i])
        add(correction, {p: F(1)}, F(-1))
        b.append(correction)
        add(ci[p], correction, F(-1))
    need(mul(c, ci) == unit(112) and mul(ci, c) == unit(112), 'Shear inverse orders')
    need(rank(b) == 16, 'Exact shear displacement rank')
    lamb = [{i: F(-5 if i < 8 else -7)} for i in range(16)]
    need(mul(w, e) == mul(lamb, w), 'Selected left eigenvectors')
    ce = mul(c, e)
    encoded = mul(ce, ci)
    need(all(set(row)-{i} <= set(P) for i, row in enumerate(encoded)),
         'Encoded response changes only pivot columns')
    for name, value in [('pivot_minor', vp), ('pivot_minor_inverse', vi),
                        ('centre_reader', w), ('code', c), ('code_inverse', ci),
                        ('response', e), ('selected_capture_response', ce),
                        ('encoded_response', encoded)]:
        need(rows(code[name]) == value, 'Independent algebra: '+name)
    need(code['pivots'] == P, 'Exact selected ports')
    for name, matrix in [('scalar_word', c), ('inverse_scalar_word', ci)]:
        events = code[name]
        need(reverse(events, 112) == transpose(matrix, 112), 'Reverse code: '+name)
        need(price(events) == 1760, 'Code scalar price')
        for op, target, origin, _ in events:
            need(target in P and (op == 'scale' or origin not in P), 'Unchanged shear source')
    word = code['scalar_word']+code['inverse_scalar_word']
    need(reverse(word, 112) == unit(112), 'Literal inverse order')
    need(reverse(code['inverse_scalar_word']+code['scalar_word'], 112) == unit(112),
         'Other literal inverse order')
    query = unit(224)
    for p in P:
        add(query[p], {112+j: x for j, x in ce[p].items()})
    need(reverse(code['final_query_word'], 224) == transpose(query, 224),
         'Arbitrary-baseline late query')
    need(price(code['final_query_word']) == 3424, 'Late query scalar price')
    a, pre_bound = prefix(code['scalar_word'], 112)
    need(a == c, 'Separate forward code')
    a, query_bound = prefix(code['final_query_word'], 224)
    need(a == query, 'Separate forward late query')
    return e, c, ce, {
        'code_price': 1760, 'query_price': 3424,
        'code_prefix': pre_bound, 'query_prefix_on_independent_inputs': query_bound,
        'displacement_rank': 16, 'extra_fields': 0, 'odd_scans': 0,
    }


def inherit():
    frozen(ACCEPTED, 'NATIVE-REVIEW-FREEZE.json',
           'cfdc4fa0361aa79c1d53a59ff48bdde1715ea8e3eb6b9efbc109c97bcc44a976')
    frozen(ACCEPTED, 'EXTENSIONS-REVIEW-FREEZE.json',
           'c8fccfbe49ddd8747095a43aa1c1c59b0270bbbf73d94a317a79113191e4e34c')
    phase_path = LANES/'new-native-recipes-20261017/isotropic-pair-review-20261018/check.py'
    read(phase_path, 'e428f575ad93a8ade3a92b641a2b5eef111519f03ba5cceca4cd4957f008ba18')
    spec = importlib.util.spec_from_file_location('independent_spatial_phase', phase_path)
    phase = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(phase)
    return phase


def select_raw(raw_word, selected):
    indices, removed = [], []
    for i, event in enumerate(raw_word['events']):
        need(event[0] in ('native', 'scalar'), 'Raw event grammar')
        target = event[1] if event[0] == 'native' else event[1][1]
        (removed if target in selected else indices).append(i)
    for i in indices:
        event = raw_word['events'][i]
        if event[0] == 'scalar' and event[1][0] == 'add':
            need(event[1][2] not in selected, 'Retained read of removed target')
    return indices, removed


def check_word(word, old, code, e, c, ce):
    need(word['frames'] == old['frames'] and word['start'] == old['start'],
         'Unchanged exact input geometry')
    selected = {112+p for p in P}
    indices, removed = select_raw(old, selected)
    need(word['retained_original_event_indices'] == indices, 'Exact removal indices')
    kept = [old['events'][i] for i in indices]
    cut = [old['events'][i] for i in removed]
    need(Counter(x[0] for x in cut) == {'native': 128, 'scalar': 122},
         'Complete removed inventory')
    need(Counter(x[4] for x in cut if x[0] == 'native') == {1: 128},
         'Only the selected rank-one children are removed')
    need(price([x[1] for x in cut if x[0] == 'scalar']) == 928, 'Removed scalar price')
    pre = [['scalar', [op, 112+t, None if s is None else 112+s, v], 0]
           for op, t, s, v in code['scalar_word']]
    progress = [['native', 112+p, 0, 1, 9, 'capture-full'] for p in P]
    late = [['scalar', [op, 112+t, None if s is None else s-112, v], 1]
            for op, t, s, v in code['final_query_word']]
    need(word['events'] == pre+kept+progress+late, 'Exact complete operation order')
    stages = [('precode', pre), ('retained_core', kept),
              ('selected_full_progress', progress), ('late_query', late)]
    cursor, expected_ranges = 0, {}
    for name, events in stages:
        expected_ranges[name] = [cursor, cursor+len(events)]
        cursor += len(events)
    need(word['stage_ranges'] == expected_ranges, 'Exact stage boundaries')
    need(cursor == 2886, 'Complete event count')
    final = list(old['final'])
    for field in selected:
        final[field] = 1
    need(word['final'] == final, 'Exact changed output frames')
    need(old['frames'][0] == [] and len(old['frames'][1]) == 9, 'I and FULL declarations')
    current = list(word['start'])
    count, used = Counter(), set()
    for i, event in enumerate(word['events']):
        if i == expected_ranges['late_query'][0]:
            need(all(current[p] == 1 for p in range(112)) and
                 all(current[p] == 1 for p in selected), 'Late common-FULL cut')
        if event[0] == 'native':
            _, field, before, after, r, key = event
            need(0 <= field < 224 and current[field] == before, 'Native field and old frame')
            need(word['native_recipes'][key]['rank'] == r, 'Native rank binding')
            if key == 'capture-full':
                need(field in selected and (before, after, r) == (0, 1, 9),
                     'Only selected complete FULL replacements')
            else:
                need(word['native_recipes'][key] == old['native_recipes'][key],
                     'Exact inherited phase record')
                need(key == str(before)+':'+str(after), 'Ordered inherited frame pair')
            current[field] = after
            count[r] += 1
            used.add(key)
        else:
            _, scalar, frame = event
            op, target, origin, _ = scalar
            need(0 <= target < 224 and current[target] == frame, 'Scalar target frame')
            if op == 'add':
                need(0 <= origin < 224 and current[origin] == frame, 'Scalar source frame')
            else:
                need(op == 'scale' and origin is None, 'Scale grammar')
    need(current == final, 'Complete final frame ledger')
    need(used == set(word['native_recipes']), 'Every stored recipe is used')
    need(count == {1: 1392, 2: 64, 3: 48, 9: 16}, 'Complete native profile')
    scalars = [event[1] for event in word['events'] if event[0] == 'scalar']
    expected = unit(640)
    for p in range(112):
        target = 112+p
        expected[target] = {112+j: v for j, v in c[p].items()}
        add(expected[target], ce[p] if p in P else e[p])
    need(reverse(scalars, 640) == transpose(expected, 640), 'All640 reverse input columns')
    actual, growth = prefix(scalars, 640)
    need(actual == expected and actual[224:] == unit(640)[224:], 'Separate forward row check')
    need(growth == {'row_one_norm': '132', 'binary_height': 1},
         'Complete operation-boundary content bounds')
    need(price(scalars) == 11640, 'Complete scalar invoice')
    stage_prices = {name: price([e[1] for e in events if e[0] == 'scalar'])
                    for name, events in stages}
    need(stage_prices == {'precode': 1760, 'retained_core': 6456,
                          'selected_full_progress': 0, 'late_query': 3424},
         'All four scalar stage bills')
    input_views = [r for r in old['endpoint_adapters'] if r['role'] == 'source']
    need(word['input_views'] == input_views, 'All112 exact input phase adapters')
    outputs = word['output_views']
    need(len(outputs) == 96 and {r['port'] for r in outputs} == set(range(112))-set(P),
         'Exactly the96 ordinary output adapters')
    for r in outputs:
        need(r['frame'] == final[112+r['port']] and r['recipe']['rank'] == 0 and
             r['recipe']['right'] is None, 'One output monomial in the actual ordinary frame')
    full = [['C', 1 << j, 1] for j in range(9)]
    need(word['new_full_recipe_circuit'] == full, 'Declared complete positive FULL kernel')
    need(reverse([x[1] for x in kept+progress+late if x[0] == 'scalar'], 640) !=
         transpose(expected, 640), 'Missing precode control')
    need(reverse([x[1] for x in pre+kept+progress if x[0] == 'scalar'], 640) !=
         transpose(expected, 640), 'Missing late query control')
    try:
        select_raw(old, selected-{112+27})
    except ValueError:
        pass
    else:
        raise ValueError('Incomplete selected-pair control')
    return {
        'input_columns': 640, 'unchanged_arbitrary_roles': 416, 'events': cursor,
        'removed_events': len(removed), 'removed_scalar_price': 928,
        'native_profile': dict(sorted(count.items())),
        'native_children': sum(count.values()), 'native_mass': sum(r*n for r, n in count.items()),
        'real_scalar_primitives': price(scalars), 'scalar_stage_prices': stage_prices,
        'input_views': 112, 'output_views': 96,
        'native_side_maps_upper_bound': 2*sum(count.values()),
        'inherited_distinct_native_recipes': len(used)-1,
        'new_distinct_native_recipes': 1, 'growth': growth,
        'private_fields': 0, 'new_fields': 0, 'odd_scans': 0,
    }


def phases(word, old, phase):
    full = [('C', 1 << j, 1) for j in range(9)]
    record = word['native_recipes']['capture-full']
    result = {'full': phase.compare(phase.recipe(record), full, 'New complete F9', 512)}
    old_target = {r['port']: r for r in old['endpoint_adapters'] if r['role'] == 'target'}
    inverse_checks = []
    for view in word['output_views']:
        p = view['port']
        inherited = phase.recipe(old_target[p])
        new = phase.recipe(view['recipe'])
        left = phase.compare(inherited+new, [], 'Output inverse '+str(p), 1)
        right = phase.compare(new+inherited, [], 'Output inverse other order '+str(p), 1)
        inverse_checks.append({'port': p, 'orders': [left, right]})
    result['output_inverse_monomials'] = inverse_checks
    identity = {'matrix_rows': [1 << j for j in range(9)],
                'quadratic_rows': [0]*9, 'linear_Z4': [0]*9, 'offset': 0, 'phase': 0}
    direct = {'rank': 9, 'left': identity, 'right': identity}
    result['identity_wrapper_corollary'] = phase.compare(
        phase.recipe(direct), full, 'Direct identity-wrapper F9', 512)
    bad = phase.recipe(record)+phase.compile_circuit([['phase', 1]])
    need(phase.run(bad, 0) != phase.run(full, 0), 'Wrong global phase control')
    result['scope'] = 'Exact executed recipes; descriptive compiler circuits are not executed.'
    return result


def direct_refinement(payload):
    frozen(NATIVE, 'DIRECT-FULL-FREEZE.json',
           'f0d3b0d7c8d93e391089a2d28066dd02b4a9b28e306dea5f4e7cb5fc895b054e')
    direct = json.loads(read(NATIVE/'direct-normal/DIRECT-FULL-CAPTURE.json.gz',
                             'fa3342f8b4ddf286f6f67922f4184486ec0162610e4de6a457de3eed0750504c', True))
    need(direct['refinement_source_decompressed_sha256'] ==
         '7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2',
         'Exact refinement source')
    need(set(direct) == set(payload)|{'refinement_source_decompressed_sha256'},
         'No additional refinement state')
    for key in set(payload)-{'providers', 'schema'}:
        need(direct[key] == payload[key], 'Unchanged refinement metadata: '+key)
    identity = {'matrix_rows': [1 << j for j in range(9)],
                'quadratic_rows': [0]*9, 'linear_Z4': [0]*9, 'offset': 0, 'phase': 0}
    expected = {'rank': 9, 'left': identity, 'right': identity}
    for name, word in payload['providers'].items():
        changed = direct['providers'][name]
        need(set(changed) == set(word), 'Unchanged word schema')
        for key in set(word)-{'native_recipes'}:
            need(changed[key] == word[key], 'Exact unchanged complete word: '+key)
        need(set(changed['native_recipes']) == set(word['native_recipes']),
             'No additional native recipe')
        for key, record in word['native_recipes'].items():
            need(changed['native_recipes'][key] == (expected if key == 'capture-full' else record),
                 'Only the direct FULL recipe changes')
    return {'providers': ['base', 'extra'], 'changed_occurrences_per_word': 16,
            'all_events_and_boundary_views_byte_equal': True,
            'real_scalar_primitives': 11640, 'native_children': 1520, 'native_mass': 1808,
            'native_side_maps_upper_bound': 3008,
            'proof': 'Exact complete-word substitution using the independently checked identity-wrapper kernel.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    frozen(ALG, 'FREEZE.json', '0810ec37cb70d819a1d40f817476a41dd1151535309972af1b5b1db2bcb42baf')
    raw = json.loads(read(RAW/'odd16-normal-v2/EXTENSION-PROGRAM.json.gz',
                          'd466cea24be92fb7f749d686c5efc63f44ea82575c15f78c38e9d6d4c972eba4', True))
    code = json.loads(read(ALG/'run-normal/ROW-CAPTURE.json',
                           '4c98af5d7a1437a03f53e84f0f2cbc7cd2ac47d4c6d4ee1523c16bf469692eb7'))
    e, c, ce, algebra_report = algebra(raw, code)
    frozen(NATIVE, 'FREEZE.json',
           '5321a8ff856042c5ca30ce6b29b90a51ccd4dcf02317820243bfffbb433c84d8')
    frozen(LANES/'bridge-access-20261017/row-capture-access-20261020', 'FREEZE.json',
           '9d4eda12aa32eb11d97f6a9a88c691152a0c9580ea678cceaacae3d9b06c5b11')
    payload = json.loads(read(NATIVE/'run-normal/PRODUCTIVE-CAPTURE.json.gz',
                              '7c3b8343ec04c65f98b7170c7f37c9f80605e28c95df00bcf2a189908461c8b2', True))
    need(payload['schema'] == 'productive-sixteen-full-capture-v1', 'Native schema')
    need(payload['selected_ports'] == P and payload['ports'] == raw['model']['ports'],
         'Exact physical selected ports and line directions')
    need(payload['ordinary_ports'] == sorted(set(range(112))-set(P)) and
         payload['inverse_code'] == code['code_inverse'], 'Complete inverse and ordinary metadata')
    for key, expected in [('response', e), ('code', c), ('captured_response', ce)]:
        need(rows(payload[key]) == expected, 'Native matrix contract: '+key)
    need(set(payload['providers']) == {'base', 'extra'}, 'Both providers')
    need(payload['providers']['base'] == payload['providers']['extra'],
         'Byte-equal provider payloads')
    word_reports = {}
    for provider, word in payload['providers'].items():
        word_reports[provider] = check_word(word, raw['providers'][provider]['forward'], code, e, c, ce)
    phase = inherit()
    phase_report = phases(payload['providers']['base'], raw['providers']['base']['forward'], phase)
    refinement_report = direct_refinement(payload)
    report = {
        'status': 'PASS_INDEPENDENT_ROW_CAPTURE_NATIVE',
        'algebra': algebra_report, 'literal_words': word_reports,
        'phases': phase_report, 'direct_full_refinement': refinement_report,
        'negative_controls': ['missing precode', 'missing late query',
                              'incomplete selected pair', 'wrong global phase'],
        'scope': 'Complete local forward native service with changed output representation. No free later-stage conversion, global decoder, recursive host, or complete supplier claim.',
    }
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'REVIEW.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    (args.out/'INPUTS.json').write_text(json.dumps(INPUTS, indent=2, sort_keys=True)+'\n')
    print(report['status'])


if __name__ == '__main__':
    main()
