"""Exact source checks, literal point tests and actual current-CRT payload joins.

Test serializers/oracles are outside every measured boundary. Default is
read-only; --receipt explicitly writes a complete JSON receipt.
Apache-2.0; substantial OpenAI assistance.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def authenticate():
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())['files']
    for pin in pins:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
             'retained source bytes: '+pin['local'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
             'retained Git blob: '+pin['local'])
    return len(pins)


def modules():
    authenticate()
    adapter = load('new_literal_adapter', HERE/'adapter.py')
    hardware = load('new_literal_hardware', HERE/'hardware.py')
    caller = load('new_paid_caller', HERE/'caller.py')
    base = load('credited_leaf_replay', HERE/'inputs/predecessor/research/encoded-crt-leaf-payload/replay.py')
    m = base.modules()
    oracle = load('canonical_benes_source', HERE/'inputs/switch/check_batched_crt.py')
    code, labels = adapter.compile_adapter()
    need(len(code) == 2500 and adapter.digest(code)
         == '2257055b689e0f88dca29532548639323dc3fa27a6e5150ea6652ed5636e07a2',
         'frozen literal table drift')
    need({instruction[1] for instruction in code if instruction[0] in ('R', 'W', 'M')}
         == set(range(20)), 'fixed twenty-role inventory')
    need(all(instruction[2] in (-1, 1) for instruction in code if instruction[0] == 'M'),
         'every emitted move is one cell')
    return adapter, hardware, caller, base, m, oracle, code, labels


def word(m, value, width, suffix='R', tail=''):
    return m.join.Tape(list('L'+''.join(str((value >> bit) & 1) for bit in range(width))+suffix+tail))


def point_fixture(m, h, p, s, a, j, x, *, header_h=None, target=None, history=0):
    target = min(j, 2*h-2-j) if target is None else target
    sources = [word(m, h if header_h is None else header_h, p, tail='_10R'),
               word(m, s, p, tail='_01L'), word(m, a, p, '|R', tail='_10|'),
               word(m, j, p, tail='_001'), word(m, x, h, tail='_10R'),
               m.join.Tape(list('L'+'1'*h+'R_10L'))]
    sources[-1].head = target+1  # Serialized verifier entry capability only.
    private = [m.join.Tape(['_']*(history+1)) for _ in range(14)]
    return private+sources


def observe_value(tape, bits):
    return sum((symbol == '1') << bit for bit, symbol in enumerate(tape.cells[1:bits+1]))


def point_case(m, hardware, code, labels, args, expected, *, precision=None, history=0):
    h, s, a, j, x = args
    p = h+3 if precision is None else precision
    target = min(j, 2*h-2-j)
    tapes = point_fixture(m, h, p, s, a, j, x, history=history)
    snapshots = [(list(t.cells), t.head) for t in tapes]
    machine = hardware.Program(code, labels)
    result = machine.run(tapes)
    need(result['status'] == 'DONE', 'point accepts')
    need(observe_value(tapes[18], h) == (x ^ (expected << target)), 'independent point/consume oracle')
    for index, tape in enumerate(tapes):
        if index < 14:
            need(tape.head == 0 and all(symbol == '_' for symbol in tape.cells), 'full private retirement')
        elif index == 18:
            changed = list(snapshots[index][0])
            changed[target+1] = str(int(changed[target+1]) ^ expected)
            need((tape.cells, tape.head) == (changed, 0), 'one physical target and intact exterior')
        else:
            need((tape.cells, tape.head) == snapshots[index], 'borrowed field/head restoration')
    ell, k = h.bit_length(), target+1
    extra = 30*p+74*h+6*ell+10*k+261
    need(result['instructions']-result['core_instructions'] == extra, 'exact adapter instruction count')
    need(result['instructions'] <= 1024*(h+3)**2+128*(p+h+3), 'proved complete point envelope')
    need(result['writes'][14:18] == [0]*4 and result['writes'][18:] == [1, 2],
         'only owned address bit and restored target marker are written')
    retained = sum(len(t.cells) for t in tapes[:14])
    need(retained <= 14*(history+1)+p+16*(h+4), 'private history envelope')
    return {'args': list(args), 'precision': p, 'instructions': result['instructions'],
            'core_instructions': result['core_instructions'], 'adapter_instructions': extra,
            'retained_private_cells': retained}


def point_tests(m, hardware, code, labels, oracle):
    networks, points, steps = 0, 0, 0
    for h in (1, 2, 3):
        for s in range(1, (1 << h)+1):
            for a in range(s):
                rows = oracle.benes(oracle.rotation(1 << h, s, a))
                networks += 1
                for j, (_, row) in enumerate(rows):
                    for x, expected in enumerate(row):
                        result = point_case(m, hardware, code, labels, (h, s, a, j, x), expected)
                        points += 1
                        steps += result['instructions']
    focused = []
    for a in range(17):
        row = oracle.benes(oracle.rotation(32, 17, a))[6][1]
        for x, expected in enumerate(row):
            focused.append(point_case(m, hardware, code, labels, (5, 17, a, 6, x), expected))
    args = (5, 17, 9, 6, 23)
    expected = oracle.benes(oracle.rotation(32, 17, 9))[6][1][23]
    wide = point_case(m, hardware, code, labels, args, expected, precision=2049, history=79)
    return {'canonical_networks': networks, 'all_entries_through_h3': points,
            'instructions_through_h3': steps, 'h5_s17_j6_points': len(focused),
            'focused_instruction_sum': sum(row['instructions'] for row in focused),
            'large_precision_with_retained_history': wide}


def point_controls(m, hardware, code, labels):
    observed = []
    for name, h_value, s, a, j in (
        ('zero_modulus', 2, 0, 0, 0), ('large_modulus', 2, 5, 0, 0),
        ('offset_equals_modulus', 2, 3, 3, 0), ('large_layer', 2, 3, 1, 3),
        ('height_width_disagreement', 3, 3, 1, 0)):
        tapes = point_fixture(m, 2, 5, s, a, j, 0, header_h=h_value, target=0)
        before = [(list(t.cells), t.head) for t in tapes[14:]]
        result = hardware.Program(code, labels).run(tapes)
        need(result['status'] == 'REJECT', 'semantic rejection '+name)
        need([(t.cells, t.head) for t in tapes[14:]] == before, 'semantic rejection borrows '+name)
        need(all(t.head == 0 and all(x == '_' for x in t.cells) for t in tapes[:14]),
             'semantic rejection cleanup '+name)
        observed.append(name)
    for name, mutate in (
        ('dirty_private_origin', lambda t: t[8].cells.__setitem__(0, '1')),
        ('wrong_borrowed_head', lambda t: setattr(t[15], 'head', 1)),
        ('target_on_endpoint', lambda t: setattr(t[19], 'head', 3))):
        tapes = point_fixture(m, 2, 5, 2, 1, 0, 0)
        mutate(tapes)
        need(hardware.Program(code, labels).run(tapes)['status'] == 'MALFORMED', name)
        observed.append(name)
    tapes = point_fixture(m, 2, 5, 2, 1, 0, 0)
    tapes[15] = tapes[14]
    try:
        hardware.Program(code, labels).run(tapes)
    except ValueError as error:
        need('distinct physical' in str(error), 'specific alias binding failure')
    else:
        raise ValueError('alias accepted')
    observed.append('aliased_owner_binding')
    mutant = list(code)
    row = mutant[labels['CORE_DONE']]
    branches = dict(row[2]); branches['1'] = branches['0']
    mutant[labels['CORE_DONE']] = row[0], row[1], branches
    try:
        point_case(m, hardware, tuple(mutant), labels, (2, 2, 1, 2, 0), 1)
    except ValueError as error:
        need(str(error) == 'independent point/consume oracle', 'specific Boolean mutation failure')
    else:
        raise ValueError('suppressed consumed Boolean escaped oracle')
    observed.append('suppressed_boolean_consumption')
    return observed


def fixture_case(m, base, moduli, values):
    m.fixture = dict(m.fixture, moduli=list(moduli), initial=list(values))
    return base.initial_fixture(m)


def direct_leaf(moduli, values, tags):
    left, right = moduli[2:]
    lower = values[2] if values[2] < left else 0
    choices = [offset for offset in range(right) if (left*offset-lower) % right == 0]
    need(len(choices) == 1, 'unique direct CRT offset')
    offset, = choices
    destinations = [(x+offset) % right if x < right else x for x in range(len(tags))]
    expected_values = list(values)
    if values[3] < right:
        expected_values[3] = (values[3]+offset) % right
    return offset, destinations, sorted(zip(destinations, tags)), expected_values


def actual_case(m, base, caller, hardware, code, labels, name, moduli, values):
    source, payload, fields = fixture_case(m, base, moduli, values)
    original = bytes(source.cells), source.head, dict(payload.cells), payload.head
    identities = id(source.cells), id(payload.cells)
    offset, destinations, expected_payload, expected_values = direct_leaf(moduli, values, base.TAGS)
    point = hardware.Program(code, labels)
    forward, first = caller.run_leg(m, base, point, source, payload, False)
    need(base.observe_payload(payload, 2) == expected_payload, 'actual forward payload oracle')
    need(base.coordinates(source, fields) == expected_values, 'actual current source oracle')
    inverse, second = caller.run_leg(m, base, point, source, payload, True)
    need((bytes(source.cells), source.head, dict(payload.cells), payload.head) == original,
         'same physical source/payload/key two-sided restoration')
    need((id(source.cells), id(payload.cells)) == identities, 'no replacement source or payload')
    histories = (*first[0], *second[0])
    need(len(histories) == 200 and len({id(cells) for cells in histories}) == 200,
         'both fresh invocations retain all 200 actual symbol owners')
    need(all(all(symbol in ('_', m.w.BLANK) for symbol in cells) for cells in histories),
         'all earlier symbol histories remain retired')
    need(forward['literal_query_calls'] == inverse['literal_query_calls'] == 12,
         'four positions times three actual rows')
    for receipt in (forward, inverse):
        need(receipt['literal_query_instructions']-receipt['literal_core_instructions'] == 7012,
             'exact all-query adapter overhead')
    return {'name': name, 'moduli': list(moduli), 'input': list(values), 'offset': offset,
            'forward_destinations': destinations, 'forward_payload': expected_payload,
            'forward_source': expected_values, 'directions': [forward, inverse],
            'both_retained_symbol_roles': 200,
            'both_retained_symbol_cells': sum(map(len, histories)),
            'source_retained_cells': len(source.cells), 'payload_retained_extent': payload.extent}


def stale_wire_table(code, labels):
    mutant = list(code)
    for pc in range(labels['COPY_X_START'], labels['COPY_X_END']):
        row = mutant[pc]
        if row[0] in ('R', 'W', 'M') and row[1] == 18:
            mutant[pc] = (row[0], 20, *row[2:])
    return tuple(mutant)


def caller_controls(m, base, caller, hardware, code, labels):
    results = []
    moduli, values = (5, 7, 2, 3), (3, 2, 1, 1)
    _, _, correct, _ = direct_leaf(moduli, values, base.TAGS)
    for fault in ('stale_offset', 'stale_wire'):
        source, payload, fields = fixture_case(m, base, moduli, values)
        actual_code = stale_wire_table(code, labels) if fault == 'stale_wire' else code
        point = hardware.Program(actual_code, labels)
        receipt, owners = caller.run_leg(m, base, point, source, payload, False, fault=fault)
        wrong = base.observe_payload(payload, 2)
        need(wrong != correct, 'source/current-wire mutation detected: '+fault)
        results.append({'fault': fault, 'returned_payload': wrong,
                        'detected_by': 'direct CRT forward placement',
                        'queries': receipt['literal_query_calls']})
    source, payload, fields = fixture_case(m, base, moduli, values)
    before = dict(payload.cells)
    point = hardware.Program(code, labels)
    caller.run_leg(m, base, point, source, payload, False)
    caller.run_leg(m, base, point, source, payload, True, fault='forward_rows_in_inverse')
    need(dict(payload.cells) != before and base.coordinates(source, fields) == list(values),
         'inverse layer order distinguished despite restored source coordinates')
    results.append({'fault': 'forward_rows_in_inverse',
                    'detected_by': 'full payload inverse, with source coordinates restored'})
    source, payload, fields = fixture_case(m, base, (5, 7, 3, 1), (3, 2, 1, 0))
    try:
        caller.run_leg(m, base, hardware.Program(code, labels), source, payload, False)
    except ValueError as error:
        need(str(error) == 'CRT modulus exceeds one', 'exact retained modulus admission')
    else:
        raise ValueError('unit modulus unexpectedly admitted by retained source')
    results.append({'fault': 'unit_modulus_source_input',
                    'detected_by': 'retained numerical source rejects: CRT modulus exceeds one',
                    'scope': 'Standalone point theorem permits s=1; this caller excludes it.'})
    return results


def baseline_check(base):
    original = base.modules()
    source, payload, fields = base.initial_fixture(original)
    snapshot = bytes(source.cells), source.head, dict(payload.cells), payload.head
    rows = []
    for reverse in (False, True):
        receipt, owners = base.run_leg(original, source, payload, reverse)
        rows.append(receipt)
    expected = json.loads((HERE/'inputs/predecessor/research/encoded-crt-leaf-payload/RESULT.json').read_text())
    need(rows == expected['forward_and_inverse'], 'exact same-workload old receipt')
    need((bytes(source.cells), source.head, dict(payload.cells), payload.head) == snapshot,
         'old baseline full restoration')
    return {'source_commit': 'd6f4a69202ad0bba4a915f4d4f3eaba1fe431c86',
            'exact_same_workload_receipts': True, 'directions': rows}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    adapter, hardware, caller, base, m, oracle, code, labels = modules()
    cases = (
        ('exact_7388', (5, 7, 3, 2), (3, 2, 1, 1)),
        ('current_wire_sensitive', (5, 7, 2, 3), (3, 2, 1, 1)),
        ('zero_offset', (5, 7, 3, 2), (3, 2, 0, 1)),
        ('invalid_left', (5, 7, 3, 2), (3, 2, 3, 1)),
        ('padded_right', (5, 7, 3, 2), (3, 2, 1, 3)),
    )
    result = {'status': 'PASS', 'graph_locations': len(code), 'physical_point_tapes': 20,
              'graph_sha256': adapter.digest(code),
              'uniform_point_evidence': point_tests(m, hardware, code, labels, oracle),
              'point_controls': point_controls(m, hardware, code, labels),
              'actual_caller_cases': [actual_case(m, base, caller, hardware, code, labels, *case)
                                      for case in cases],
              'caller_controls': caller_controls(m, base, caller, hardware, code, labels),
              'executed_original_baseline': baseline_check(base),
              'new_kappa': None,
              'scope': 'Uniform literal point-consumption adapter plus bounded actual encoded CRT leaf/payload join; mixed outer tariffs retained.'}
    encoded = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.receipt:
        args.receipt.write_text(encoded)
    print(json.dumps({'status': result['status'], 'graph_locations': len(code),
                      'point_queries': 1566+544+1, 'actual_roundtrips': len(cases),
                      'controls': len(result['point_controls'])+len(result['caller_controls'])}, sort_keys=True))


if __name__ == '__main__':
    main()
