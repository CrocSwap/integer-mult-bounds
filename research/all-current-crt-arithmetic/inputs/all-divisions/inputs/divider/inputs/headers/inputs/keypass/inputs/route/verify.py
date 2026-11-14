"""Bounded literal routes, exact source seam and actual payload roundtrips.

Default is read-only. --receipt explicitly saves the computed evidence.
Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
GRAPH = 'f8f0bd615531c914efc110d8a9d5ce2fafa2b00c8a568bdbfb86bf24868a0ef7'


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def modules():
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())['files']
    for pin in pins:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'], 'exact source bytes')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'exact Git blob')
    previous = load(HERE/'inputs/point/verify.py', '_retained_B5_verify')
    point, old_hardware, caller, base, m, oracle, point_code, point_labels = previous.modules()
    controller = load(HERE/'controller.py', '_literal_full_row')
    hardware = load(HERE/'hardware.py', '_literal_full_row_hardware')
    join = load(HERE/'join.py', '_literal_full_row_join').bind()
    code, labels, metadata = controller.compile_controller()
    need(len(code) == 10123 and controller.digest(code) == GRAPH, 'fixed complete graph')
    return previous, point, base, m, oracle, controller, hardware, join, code, labels, metadata


def check_embedding(code, metadata, point_code):
    for mode, placement in metadata['point_copies'].items():
        start, after = placement['start'], placement['after']
        need(placement['length'] == len(point_code), 'complete point copy extent')
        for pc, instruction in enumerate(point_code):
            op, *args = instruction
            if op == 'R':
                expected = (op, args[0], {symbol: start+target for symbol, target in args[1].items()})
            elif op == 'J':
                expected = (op, start+args[0])
            elif op == 'H' and args[0] == 'DONE':
                expected = ('J', after)
            else:
                expected = instruction
            need(code[start+pc] == expected, 'exact point copy including every return edge: '+mode)


def static_checks(point, code, labels, metadata, join):
    point_code, _ = point.compile_adapter()
    check_embedding(code, metadata, point_code)
    touched = {row[1] for row in code if row[0] in ('R', 'W', 'M')}
    need(touched == set(range(20)), 'same fixed twenty-owner inventory')
    for row in code:
        need(row[0] in ('R', 'W', 'M', 'J', 'H'), 'literal opcode alphabet')
        if row[0] == 'M':
            need(row[2] in (-1, 1), 'unit physical move')
        targets = row[2].values() if row[0] == 'R' else (row[1],) if row[0] == 'J' else ()
        need(all(0 <= pc < len(code) for pc in targets), 'total fixed PC map')
    altered = list(code)
    success = next(i for i, row in enumerate(point_code) if row == ('H', 'DONE'))
    altered[metadata['point_copies']['FORWARD_ASC']['start']+success] = ('H', 'DONE')
    try:
        check_embedding(altered, metadata, point_code)
    except ValueError:
        pass
    else:
        raise ValueError('omitted point-to-controller return was accepted')
    need(set(metadata['entries']) == {'FORWARD', 'INVERSE'}, 'two fixed entry ports')
    return {'instructions': len(code), 'literal_controller_instructions': 123,
            'point_instruction_copies_checked': 10000, 'tapes': 20, 'graph_sha256': GRAPH,
            'omitted_return_detected': True, 'exact_caller_seam': join.exact_seam}


def fixture(previous, m, h, p, s, a, x, *, history=0, translated=False):
    tapes = previous.point_fixture(m, h, p, s, a, 0, x, history=history)
    tapes[19].head = 0
    tapes[17].cells[1:p+1] = [('1' if bit % 3 else '0') for bit in range(p)]
    origins = [0]*20
    if translated:
        for i, tape in enumerate(tapes):
            prefix = list('10L0'*(1+i % 3))
            origins[i] = len(prefix)
            if i < 14:
                tape.cells[:] = prefix+['_']*(p+h+16)+list('R10|L')
            else:
                tape.cells[:] = prefix+tape.cells
            tape.head += len(prefix)
    return tapes, origins


def value(cells, origin, width):
    return sum((cells[origin+1+i] == '1') << i for i in range(width))


def retirement(tapes, before, origins, h, p, expected):
    for i, tape in enumerate(tapes):
        old, old_head = before[i]
        need(tape.head == old_head == origins[i], 'every physical head returned')
        if i < 14:
            need(tape.cells[:len(old)] == old and all(s == '_' for s in tape.cells[len(old):]),
                 'complete prior private history/exterior preserved and new work blank')
        elif i in (17, 18):
            changed = list(old)
            width, output = (p, 0) if i == 17 else (h, expected)
            changed[origins[i]+1:origins[i]+1+width] = [str((output >> bit) & 1) for bit in range(width)]
            need(tape.cells == changed, 'only owned row/address bodies change')
        else:
            need(tape.cells == old, 'borrowed complete contents and opaque exterior preserved')


def trace_check(result, origins, h, p, s, a, x, direction, rows):
    q = 2*h-1
    need(result['point_calls'] == len(result['visits']) == q, 'exact complete row count')
    current = x
    for r, visit in enumerate(result['visits']):
        j = r if direction == 'FORWARD' else q-1-r
        target = min(j, q-1-j)
        need(value(visit['row'], origins[17], p) == j, 'encoded current row invariant')
        need(value(visit['address'], origins[18], h) == current, 'actual current wire invariant')
        need(visit['target_head'] == origins[19]+target+1, 'row and physical target agree')
        phase = 'ASC' if r < h else 'DESC'
        need(visit['mode'] == direction+'_'+phase, 'fixed finite cursor mode')
        need(visit['private_heads'] == origins[:14], 'same returned point origins at every call')
        axis, switches = rows[j]
        need(axis == target, 'independent canonical target ordering')
        current ^= switches[current] << target
    if q > 1:
        extent = result['visits'][1]['private_extents']
        need(all(v['private_extents'] == extent for v in result['visits'][1:]),
             'no private history growth after the first complete point call')
    expected = ((x+(a if direction == 'FORWARD' else -a)) % s) if x < s else x
    need(current == expected, 'canonical full network equals padded rotation')
    return expected


def route_case(previous, m, oracle, hardware, code, labels, metadata, args, direction,
               *, precision=None, history=0, translated=False):
    h, s, a, x = args
    p = h+3 if precision is None else precision
    tapes, origins = fixture(previous, m, h, p, s, a, x, history=history, translated=translated)
    before = [(list(t.cells), t.head) for t in tapes]
    machine = hardware.Program(code, labels, metadata)
    result = machine.run(tapes, direction)
    need(result['status'] == 'DONE', 'complete route accepts')
    rows = oracle.benes(oracle.rotation(1 << h, s, a))
    expected = trace_check(result, origins, h, p, s, a, x, direction, rows)
    retirement(tapes, before, origins, h, p, expected)
    pop = (2*h-2).bit_count()
    driver = 14*p+36*h-12-7*pop if direction == 'FORWARD' else 14*p+72*h-38-14*pop
    need(result['controller_instructions'] == driver, 'exact all-height controller bill')
    need(result['instructions'] <= (2*h-1)*(1024*(h+3)**2+128*(p+h+3))+14*p+72*h,
         'complete source-derived point plus controller envelope')
    private = sum(len(t.cells)-len(old[0]) for t, old in zip(tapes[:14], before[:14]))
    need(private <= p+11*h+h.bit_length()+48, 'fixed per-role history union')
    need(result['writes'][14:17] == [0, 0, 0] and result['writes'][18] == 2*h-1
         and result['writes'][19] == 2*(2*h-1), 'actual current-address and width ownership effects')
    return {'args': list(args), 'direction': direction, 'precision': p,
            'instructions': result['instructions'], 'point_calls': result['point_calls'],
            'controller_instructions': driver, 'new_private_cells': private,
            'translated_origins': translated}


def complete_routes(previous, m, oracle, hardware, code, labels, metadata):
    cases = calls = instructions = 0
    checksum = sha256()
    for h in (1, 2, 3):
        for s in range(1, (1 << h)+1):
            for a in range(s):
                for x in range(1 << h):
                    for direction in ('FORWARD', 'INVERSE'):
                        row = route_case(previous, m, oracle, hardware, code, labels, metadata,
                                         (h, s, a, x), direction)
                        cases += 1
                        calls += row['point_calls']
                        instructions += row['instructions']
                        checksum.update(json.dumps(row, sort_keys=True).encode())
    focused_cases = focused_calls = focused_steps = 0
    for a in range(17):
        for x in range(32):
            for direction in ('FORWARD', 'INVERSE'):
                row = route_case(previous, m, oracle, hardware, code, labels, metadata,
                                 (5, 17, a, x), direction)
                focused_cases += 1
                focused_calls += row['point_calls']
                focused_steps += row['instructions']
                checksum.update(json.dumps(row, sort_keys=True).encode())
    boundary = []
    for args, p, translated in (((1, 2, 1, 0), 2, True),
                                ((5, 17, 9, 23), 2049, False),
                                ((7, 127, 65, 126), 10, True),
                                ((9, 257, 129, 256), 12, False)):
        for direction in ('FORWARD', 'INVERSE'):
            boundary.append(route_case(previous, m, oracle, hardware, code, labels, metadata,
                                       args, direction, precision=p, history=79, translated=translated))
    return {'complete_routes_through_h3': cases, 'point_calls_through_h3': calls,
            'instructions_through_h3': instructions, 'h5_s17_complete_routes': focused_cases,
            'h5_s17_point_calls': focused_calls, 'h5_s17_instructions': focused_steps,
            'finite_domain_checksum': checksum.hexdigest(), 'boundary_routes': boundary}


def actual_case(previous, m, base, caller, hardware, code, labels, metadata, name, moduli, values):
    source, payload, fields = previous.fixture_case(m, base, moduli, values)
    original = bytes(source.cells), source.head, dict(payload.cells), payload.head
    identities = id(source.cells), id(payload.cells)
    offset, destinations, expected_payload, expected_values = previous.direct_leaf(moduli, values, base.TAGS)
    machine = hardware.Program(code, labels, metadata)
    receipts, ownership = [], []
    for reverse in (False, True):
        old_routes, old_points = machine.routes, machine.point_instructions
        old_total = machine.instructions
        receipt, owned = caller.run_leg(m, base, machine, source, payload, reverse)
        total = receipt.pop('literal_query_instructions')
        point_steps = machine.point_instructions-old_points
        receipt.update(literal_route_instructions=total, literal_point_instructions=point_steps,
                       literal_controller_instructions=total-point_steps,
                       complete_wire_routes=machine.routes-old_routes)
        need(machine.instructions-old_total == total, 'whole literal bill has no observer addition')
        need(receipt['complete_wire_routes'] == 4 and receipt['literal_query_calls'] == 12,
             'one literal controller entry per actual wire')
        need(total-point_steps == 4*(162 if reverse else 123), 'actual complete driver bill')
        receipts.append(receipt)
        ownership.append(owned)
        if not reverse:
            need(base.observe_payload(payload, 2) == expected_payload, 'actual forward payload oracle')
            need(base.coordinates(source, fields) == expected_values, 'actual source coordinate oracle')
    need((bytes(source.cells), source.head, dict(payload.cells), payload.head) == original,
         'complete physical source/payload/key inverse')
    need((id(source.cells), id(payload.cells)) == identities, 'source and payload owners unchanged')
    histories = (*ownership[0][0], *ownership[1][0])
    need(len(histories) == len({id(cells) for cells in histories}) == 200,
         'all actual acquired symbol owners remain counted')
    old_result = json.loads((HERE/'inputs/point/RESULT.json').read_text())
    old = next(case for case in old_result['actual_caller_cases'] if case['name'] == name)
    compared = ('encoded_source_symbol_actions', 'radix_bit_control_instructions', 'radix_passes',
                'payload_adapter_bit_actions', 'retained_symbol_roles', 'retained_symbol_cells',
                'retained_bucket_bits', 'retained_radix_register_bits')
    for new, prior in zip(receipts, old['directions']):
        need(all(new[key] == prior[key] for key in compared), 'unchanged source/payload/storage provider bills')
        need(new['literal_point_instructions'] == prior['literal_query_instructions'],
             'same complete point-query workload')
    return {'name': name, 'moduli': list(moduli), 'input': list(values), 'offset': offset,
            'forward_destinations': destinations, 'forward_payload': expected_payload,
            'forward_source': expected_values, 'directions': receipts,
            'both_retained_symbol_roles': 200, 'both_retained_symbol_cells': sum(map(len, histories)),
            'source_retained_cells': len(source.cells), 'payload_retained_extent': payload.extent,
            'same_workload_comparison': 'Exact retained B5 receipt; source/radix providers executed unchanged here.'}


def semantic_mutants(previous, m, hardware, code, labels, metadata):
    variants = []
    skipped = list(code)
    for start, end in (('FORWARD_ASC_UPDATE', 'FORWARD_DESC_UPDATE'),
                       ('FORWARD_DESC_UPDATE', 'FORWARD_DESC_AFTER')):
        hits = [pc for pc in range(labels[start], labels[end]) if skipped[pc] == ('W', 17, '1')]
        need(len(hits) == 1, 'one static carry completion per forward update')
        skipped[hits[0]] = ('W', 17, '0')
    variants.append(('lost_current_row_increment', skipped, metadata, 'FORWARD', 0))
    wrong_inverse = list(code)
    wrong_inverse[labels['INVERSE']] = ('J', labels['FORWARD'])
    variants.append(('forward_rows_in_inverse_graph', wrong_inverse, metadata, 'INVERSE', 2))
    wrong_cursor = list(code)
    wrong_cursor[labels['FORWARD_ASC_AFTER']] = ('J', labels['FORWARD_DESC_AFTER'])
    variants.append(('premature_cursor_reversal', wrong_cursor, metadata, 'FORWARD', 0))
    stale = list(code)
    inner = metadata['point_labels']
    for block in metadata['point_copies'].values():
        for pc in range(block['start']+inner['COPY_X_START'], block['start']+inner['COPY_X_END']):
            row = stale[pc]
            if row[0] in ('R', 'W', 'M') and row[1] == 18:
                stale[pc] = (row[0], 20, *row[2:])
    variants.append(('stale_current_wire_extra_test_owner', stale, dict(metadata, tapes=21), 'FORWARD', 0))
    receipts = []
    for name, mutant, meta, direction, x in variants:
        tapes, origins = fixture(previous, m, 2, 5, 3, 2, x)
        if meta['tapes'] == 21:
            tapes.append(m.join.Tape(list(tapes[18].cells)))
            origins.append(0)
        before = [(list(t.cells), t.head) for t in tapes]
        result = hardware.Program(mutant, labels, meta).run(tapes, direction)
        need(result['status'] == 'DONE', 'semantic mutation must actually return: '+name)
        output = value(tapes[18].cells, 0, 2)
        expected = (x+(2 if direction == 'FORWARD' else -2)) % 3
        need(output != expected, 'complete rotation oracle detects returning mutation: '+name)
        retirement(tapes, before, origins, 2, 5, output)
        receipts.append({'fault': name, 'output': output, 'expected': expected,
                         'point_calls': result['point_calls'], 'all_heads_and_private_history_restored': True})
    dirty = list(code)
    hits = [pc for pc in range(labels['FINISH'], labels['ADAPTER_FAIL']) if dirty[pc] == ('W', 17, '0')]
    need(len(hits) == 1, 'one complete final row clear write')
    dirty[hits[0]] = ('W', 17, '1')
    tapes, origins = fixture(previous, m, 2, 5, 3, 2, 0)
    result = hardware.Program(dirty, labels, metadata).run(tapes)
    need(result['status'] == 'DONE' and value(tapes[17].cells, 0, 5) != 0,
         'returned row retirement violation detected')
    receipts.append({'fault': 'omitted_row_zeroing', 'detected_by': 'complete owned-row retirement'})
    return receipts


def domain_controls(previous, m, hardware, code, labels, metadata):
    controls = []
    for name, s, a in (('zero_modulus', 0, 0), ('large_modulus', 5, 0), ('offset_equals_modulus', 3, 3)):
        tapes, _ = fixture(previous, m, 2, 5, s, a, 0)
        result = hardware.Program(code, labels, metadata).run(tapes)
        need(result['status'] == 'REJECT', 'inherited semantic rejection '+name)
        controls.append({'fault': name, 'status': 'REJECT', 'failure_rollback_claimed': False})
    for name, mutate in (
        ('dirty_private_origin', lambda t: t[8].cells.__setitem__(0, '1')),
        ('wrong_header_head', lambda t: setattr(t[15], 'head', 1)),
        ('empty_unary_width', lambda t: t[19].cells.__setitem__(1, 'R')),
        ('nonbit_row_body', lambda t: t[17].cells.__setitem__(2, '|'))):
        tapes, _ = fixture(previous, m, 2, 5, 3, 2, 0)
        mutate(tapes)
        need(hardware.Program(code, labels, metadata).run(tapes)['status'] == 'MALFORMED', name)
        controls.append({'fault': name, 'status': 'MALFORMED', 'failure_rollback_claimed': False})
    tapes, _ = fixture(previous, m, 2, 5, 3, 2, 0)
    tapes[15] = tapes[14]
    try:
        hardware.Program(code, labels, metadata).run(tapes)
    except ValueError as error:
        need(str(error) == 'fixed distinct physical owners', 'alias binding reason')
    else:
        raise ValueError('aliased borrowed owners accepted')
    controls.append({'fault': 'aliased_owners', 'detected_by': 'physical owner binder'})
    return controls


def actual_controls(previous, m, base, caller, hardware, code, labels, metadata):
    moduli, values = (5, 7, 2, 3), (3, 2, 1, 1)
    _, _, correct, _ = previous.direct_leaf(moduli, values, base.TAGS)
    source, payload, fields = previous.fixture_case(m, base, moduli, values)
    machine = hardware.Program(code, labels, metadata)
    caller.run_leg(m, base, machine, source, payload, False, fault='stale_offset')
    need(base.observe_payload(payload, 2) != correct, 'actual stale numerical offset detected')
    source, payload, fields = previous.fixture_case(m, base, moduli, values)
    before = dict(payload.cells)
    machine = hardware.Program(code, labels, metadata)
    caller.run_leg(m, base, machine, source, payload, False)
    caller.run_leg(m, base, machine, source, payload, True, fault='forward_rows_in_inverse')
    need(dict(payload.cells) != before and base.coordinates(source, fields) == list(values),
         'actual payload detects wrong direction despite restored source coordinates')
    source, payload, fields = previous.fixture_case(m, base, (5, 7, 3, 1), (3, 2, 1, 0))
    try:
        caller.run_leg(m, base, hardware.Program(code, labels, metadata), source, payload, False)
    except ValueError as error:
        need(str(error) == 'CRT modulus exceeds one', 'retained source admission boundary')
    else:
        raise ValueError('unit modulus entered actual retained caller')
    return [{'fault': 'stale_actual_offset', 'detected_by': 'direct CRT payload oracle'},
            {'fault': 'wrong_actual_inverse_entry', 'detected_by': 'complete payload inverse'},
            {'fault': 'unit_modulus_source_input', 'detected_by': 'retained numerical admission'}]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    previous, point, base, m, oracle, controller, hardware, caller, code, labels, metadata = modules()
    result = {'status': 'PASS', 'static': static_checks(point, code, labels, metadata, caller),
              'uniform_routes': complete_routes(previous, m, oracle, hardware, code, labels, metadata),
              'returning_controls': semantic_mutants(previous, m, hardware, code, labels, metadata),
              'domain_controls': domain_controls(previous, m, hardware, code, labels, metadata)}
    cases = (('exact_7388', (5, 7, 3, 2), (3, 2, 1, 1)),
             ('current_wire_sensitive', (5, 7, 2, 3), (3, 2, 1, 1)))
    result['actual_caller_cases'] = [actual_case(previous, m, base, caller, hardware, code, labels,
                                               metadata, *case) for case in cases]
    result['actual_controls'] = actual_controls(previous, m, base, caller, hardware, code, labels, metadata)
    result['source_hashes'] = {name: sha256((HERE/name).read_bytes()).hexdigest()
                               for name in ('controller.py', 'hardware.py', 'join.py', 'verify.py',
                                            'PROOF.md', 'SOURCE-PINS.json')}
    result['new_kappa'] = None
    result['scope'] = 'Uniform literal complete per-wire controller and bounded actual join to retained source/radix providers; external acquisition and outer control remain explicit.'
    rendered = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.receipt:
        args.receipt.write_text(rendered)
    print(json.dumps({'status': 'PASS', 'instructions': len(code), 'physical_tapes': 20,
                      'complete_routes': result['uniform_routes']['complete_routes_through_h3']
                          + result['uniform_routes']['h5_s17_complete_routes']+8,
                      'actual_roundtrips': len(cases), 'controls': 17}, sort_keys=True))


if __name__ == '__main__':
    main()
