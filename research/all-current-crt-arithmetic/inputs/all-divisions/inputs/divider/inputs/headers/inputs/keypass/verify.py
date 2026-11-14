"""Bounded full key passes and exact current-source/radix joins.

Default is read-only; --receipt explicitly saves computed evidence.
Apache-2.0. Prepared for @CubeJerry with substantial OpenAI assistance.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
GRAPH = '8f5ae62b89de8308eb021920185269d884f07f625a5b3ee10b39f27aee5a393b'


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
    for pin in json.loads((HERE/'SOURCE-PINS.json').read_text())['files']:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'], 'exact source bytes')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'exact Git blob')
    retained = load(HERE/'inputs/route/verify.py', '_retained_B6_verify')
    previous, point, base, m, oracle, route, old_hw, old_join, old_code, _, _ = retained.modules()
    key_pass = load(HERE/'key_pass.py', '_literal_key_pass')
    hardware = load(HERE/'hardware.py', '_literal_key_hardware')
    caller = load(HERE/'join.py', '_literal_key_join').bind(hardware.BitPort)
    code, labels, metadata = key_pass.compile_pass()
    need(len(code) == 21135 and key_pass.digest(code) == GRAPH, 'fixed complete key graph')
    return retained, previous, base, m, key_pass, hardware, caller, code, labels, metadata, old_code


def embedding(code, metadata, old_code):
    for name, block in metadata['route_copies'].items():
        start = block['start']
        need(block['length'] == len(old_code), 'complete route extent')
        for pc, instruction in enumerate(old_code):
            op, *args = instruction
            if op == 'R':
                expected = (op, args[0], {symbol: start+target for symbol, target in args[1].items()})
            elif op == 'J':
                expected = (op, start+args[0])
            elif instruction == ('H', 'DONE'):
                expected = ('J', block['return'])
            else:
                expected = instruction
            need(code[start+pc] == expected, 'exact route instruction relocation '+name)


def static_checks(code, labels, metadata, old_code, caller):
    embedding(code, metadata, old_code)
    need({row[1] for row in code if row[0] in ('R', 'W', 'M')} == set(range(22)), 'fixed 22 roles')
    for row in code:
        need(row[0] in ('R', 'W', 'M', 'J', 'H'), 'literal opcode')
        if row[0] == 'M':
            need(row[2] in (-1, 1), 'unit physical movement')
        if row[0] == 'W' and row[1] == 21:
            need(row[2] in ('0', '1'), 'binary payload write')
        targets = row[2].values() if row[0] == 'R' else (row[1],) if row[0] == 'J' else ()
        need(all(0 <= pc < len(code) for pc in targets), 'total finite branch map')
    mutant = list(code)
    halt = old_code.index(('H', 'DONE'))
    mutant[metadata['route_copies']['FORWARD']['start']+halt] = ('H', 'DONE')
    try:
        embedding(mutant, metadata, old_code)
    except ValueError:
        pass
    else:
        raise ValueError('route-to-key-pass return omission was not detected')
    return {'instructions': len(code), 'outer_graph_locations': 889, 'physical_tapes': 22,
            'exact_relocated_instructions': 2*len(old_code), 'graph_sha256': GRAPH,
            'entry_ports': metadata['entries'], 'missing_return_detected': True,
            'exact_caller_seam': caller.exact_seam}


def fixture(retained, previous, m, hardware, h, p, s, a, *, history=0, translated=False):
    tapes, origins = retained.fixture(previous, m, h, p, s, a, 0, history=history, translated=translated)
    for role in (18, 20):
        prefix = list('10L01') if translated else []
        body = ['_']*max(history+1, h+2)
        tape = m.join.Tape(prefix+body+(list('R10|L') if translated else []))
        tape.head = len(prefix)
        if role == 18:
            tapes[role], origins[role] = tape, len(prefix)
        else:
            tapes.append(tape)
            origins.append(len(prefix))
    payloads = [0 if i % 3 == 0 else 4095 if i % 3 == 1 else (137*i+53) % 4096 for i in range(1 << h)]
    keys = [((1 << h)-1-i) for i in range(1 << h)]
    symbols = ['<']
    for value, key in zip(payloads, keys):
        symbols.extend([('R', value), *format(key, '0'+str(h)+'b')])
    symbols.append('>')
    body = [bit for symbol in symbols for bit in m.binary.bits(symbol)]
    prefix, suffix = ([1, 0, 1, 1, 0, 1, 0], [1, 0, 1, 1]) if translated else ([], [])
    payload = m.bit_tape(prefix+body+suffix)
    payload.head = len(prefix)
    payload.write_positions = []
    raw_write = payload.write
    def record_write(bit):
        payload.write_positions.append(payload.head)
        raw_write(bit)
    payload.write = record_write
    tapes.append(hardware.BitPort(payload))
    origins.append(len(prefix))
    return tapes, origins, payload, payloads


def integer(word, origin, width):
    return sum((word[origin+1+bit] == '1') << bit for bit in range(width))


def decode_keys(payload, origin, h):
    out = []
    for index in range(1 << h):
        at = origin+13*(2+index*(h+1))
        value = 0
        for digit in range(h):
            code = sum(payload.cells.get(at+13*digit+bit, 0) << bit for bit in range(13))
            need(code in (2, 3), 'result remains the original allocated key code')
            value = 2*value+(code & 1)
        out.append(value)
    return out


def check_retirement(tapes, before, origins, payload_before, payload, h, p, expected):
    for role, tape in enumerate(tapes[:-1]):
        old, head = before[role]
        need(tape.head == head == origins[role], 'all marker heads return')
        if role == 17:
            changed = list(old)
            changed[head+1:head+p+1] = ['0']*p
            need(tape.cells == changed, 'owned row zeroing and exterior preservation')
        else:
            need(tape.cells[:len(old)] == old and all(v == '_' for v in tape.cells[len(old):]),
                 'complete private/index/address retirement or borrowed restoration')
    need(payload.head == origins[21], 'paid physical payload-head return')
    correct = dict(payload_before)
    allowed = []
    for index, value in enumerate(expected):
        at = origins[21]+13*(2+index*(h+1))
        for digit in range(h):
            code = 2+((value >> (h-1-digit)) & 1)
            for bit in range(13):
                where = at+13*digit+bit
                allowed.append(where)
                if (code >> bit) & 1:
                    correct[where] = 1
                else:
                    correct.pop(where, None)
    need(payload.cells == correct, 'exact full payload/key/exterior contents')
    need(payload.write_positions == allowed, 'every key cell written once; no payload/marker/exterior write')


def pass_case(retained, previous, m, hardware, code, labels, metadata, args, direction,
              *, precision=None, history=0, translated=False):
    h, s, a = args
    p, n = h+3 if precision is None else precision, 1 << h
    tapes, origins, payload, values = fixture(retained, previous, m, hardware, h, p, s, a,
                                               history=history, translated=translated)
    before = [(list(t.cells), t.head) for t in tapes[:-1]]
    payload_before = dict(payload.cells)
    machine = hardware.Program(code, labels, metadata)
    result = machine.run(tapes, direction)
    need(result['status'] == 'DONE', 'complete key pass accepts')
    expected = [((i+(a if direction == 'FORWARD' else -a)) % s) if i < s else i for i in range(n)]
    need(decode_keys(payload, origins[21], h) == expected, 'independent padded-rotation key oracle')
    check_retirement(tapes, before, origins, payload_before, payload, h, p, expected)
    need(result['routes'] == len(result['visits']) == n and result['point_calls'] == n*(2*h-1),
         'encoded carry executes exactly all physical wires and rows')
    for index, visit in enumerate(result['visits']):
        need(integer(visit['index'], origins[20], h) == integer(visit['address'], origins[18], h) == index,
             'current physical index is copied at every route call')
        need(integer(visit['destination'], origins[18], h) == expected[index], 'route destination before write')
        need(visit['payload_head'] == origins[21]+13*(2+index*(h+1)), 'same record allocated key pointer')
        need(visit['heads'][:21] == origins[:21], 'all marker heads return between whole-route calls')
    need(result['pass_controller_instructions'] == n*(156*h+126)+18*h+203, 'exact full outer bill')
    need(result['payload_bit_actions'] == n*(117*h+66)+156, 'exact literal payload action partition')
    pop = (2*h-2).bit_count()
    driver = 14*p+36*h-12-7*pop if direction == 'FORWARD' else 14*p+72*h-38-14*pop
    need(result['route_instructions']-result['point_instructions'] == n*driver, 'full N-times route bill')
    need(result['writes'][21] == 13*n*h, 'no key write omitted from cost')
    need(payload.extent <= max(len(payload_before) and max(payload_before)+1, origins[21]+13*(2+n*(h+1))+1),
         'paid payload frontier and prior history retained')
    growth = sum(len(t.cells)-len(old[0]) for t, old in zip(tapes[:14], before[:14]))
    need(growth <= p+11*h+h.bit_length()+48, 'fixed per-role union across every wire and row')
    return {'args': list(args), 'direction': direction, 'precision': p, 'instructions': result['instructions'],
            'route_instructions': result['route_instructions'], 'point_calls': result['point_calls'],
            'pass_controller_instructions': result['pass_controller_instructions'], 'routes': n,
            'payload_bit_actions': result['payload_bit_actions'], 'new_private_cells': growth,
            'translated_origins': translated, 'opaque_payload_bits': 12}


def bounded_passes(retained, previous, m, hardware, code, labels, metadata):
    rows = []
    for h in (1, 2, 3):
        for s in range(1, (1 << h)+1):
            for a in range(s):
                for direction in ('FORWARD', 'INVERSE'):
                    rows.append(pass_case(retained, previous, m, hardware, code, labels, metadata,
                                          (h, s, a), direction))
    small = len(rows)
    for a in (0, 1, 8, 9, 16):
        for direction in ('FORWARD', 'INVERSE'):
            rows.append(pass_case(retained, previous, m, hardware, code, labels, metadata,
                                  (5, 17, a), direction))
    for args, precision in (((1, 2, 1), 2), ((3, 5, 3), 97)):
        for direction in ('FORWARD', 'INVERSE'):
            rows.append(pass_case(retained, previous, m, hardware, code, labels, metadata,
                                  args, direction, precision=precision, history=79, translated=True))
    return {'complete_passes_through_h3': small, 'focused_h5_s17_passes': 10,
            'translated_prior_history_passes': 4, 'complete_passes': len(rows),
            'wire_routes': sum(row['routes'] for row in rows),
            'point_queries': sum(row['point_calls'] for row in rows),
            'literal_instructions': sum(row['instructions'] for row in rows),
            'domain_checksum': sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
            'boundary_receipts': rows[-4:]}


def actual_case(previous, m, base, caller, hardware, code, labels, metadata, name, moduli, values):
    source, payload, fields = previous.fixture_case(m, base, moduli, values)
    original = bytes(source.cells), source.head, dict(payload.cells), payload.head
    identities = id(source.cells), id(payload.cells)
    offset, destinations, expected_payload, expected_values = previous.direct_leaf(moduli, values, base.TAGS)
    machine = hardware.Program(code, labels, metadata)
    receipts, ownership = [], []
    for reverse in (False, True):
        before = machine.routes, machine.route_instructions, machine.point_instructions, machine.payload_bit_actions
        receipt, owned = caller.run_leg(m, base, machine, source, payload, reverse)
        total = receipt.pop('literal_query_instructions')
        routes, route_steps, point_steps, payload_steps = (now-old for now, old in zip(
            (machine.routes, machine.route_instructions, machine.point_instructions, machine.payload_bit_actions), before))
        raw_payload = receipt.pop('payload_adapter_bit_actions')
        receipt.update(literal_key_pass_instructions=total, literal_route_instructions=route_steps,
                       literal_point_instructions=point_steps, literal_pass_controller_instructions=total-route_steps,
                       literal_row_controller_instructions=route_steps-point_steps, complete_wire_routes=routes,
                       payload_bit_actions_included_in_literal_bill=payload_steps,
                       remaining_payload_adapter_bit_actions=raw_payload-payload_steps)
        need(routes == 4 and receipt['literal_query_calls'] == 12, 'one complete pass over actual four tags')
        need(total-route_steps == 1991 and route_steps-point_steps == 4*(162 if reverse else 123),
             'actual full key and row driver costs')
        need(receipt['remaining_payload_adapter_bit_actions'] >= 0, 'no payload cost counted twice')
        receipts.append(receipt)
        ownership.append(owned)
        if not reverse:
            need(base.observe_payload(payload, 2) == expected_payload, 'actual direct CRT payload oracle')
            need(base.coordinates(source, fields) == expected_values, 'actual source coordinate oracle')
    need((bytes(source.cells), source.head, dict(payload.cells), payload.head) == original,
         'physical source/payload/identity-key sorted roundtrip')
    need((id(source.cells), id(payload.cells)) == identities, 'same source and payload owners')
    histories = (*ownership[0][0], *ownership[1][0])
    need(len(histories) == len({id(cells) for cells in histories}) == 200, 'retained actual owner inventory')
    old = next(case for case in json.loads((HERE/'inputs/route/RESULT.json').read_text())['actual_caller_cases']
               if case['name'] == name)
    for new, prior in zip(receipts, old['directions']):
        for key in ('encoded_source_symbol_actions', 'radix_bit_control_instructions', 'radix_passes',
                    'retained_symbol_roles', 'retained_symbol_cells', 'retained_bucket_bits',
                    'retained_radix_register_bits', 'literal_point_instructions'):
            need(new[key] == prior[key], 'unchanged source/radix/storage and exact complete query workload')
        need(new['literal_route_instructions'] == prior['literal_route_instructions'], 'unchanged complete B6 workload')
    return {'name': name, 'moduli': list(moduli), 'input': list(values), 'offset': offset,
            'forward_destinations': destinations, 'forward_payload': expected_payload,
            'forward_source': expected_values, 'directions': receipts, 'retained_symbol_roles_both': 200,
            'retained_symbol_cells_both': sum(map(len, histories)), 'payload_retained_extent': payload.extent,
            'original_physical_position_keys_verified': True,
            'same_workload_comparison': 'Exact executed B6 point/route work and unchanged source/radix providers.'}


def semantic_controls(retained, previous, m, hardware, code, labels, metadata):
    mutants = []
    complemented = list(code)
    for name in ('FORWARD', 'INVERSE'):
        lo, hi = labels[name+'_ROUTE_RETURN'], labels[name+'_INDEX_INCREMENT']
        writes = [pc for pc in range(lo, hi) if code[pc][0:2] == ('W', 21)]
        need(len(writes) == 26, 'two complete key code emission blocks')
        for pc in (writes[0], writes[13]):
            complemented[pc] = ('W', 21, str(1-int(code[pc][2])))
    mutants.append(('complemented_output_key_digits', complemented, 'FORWARD'))
    stale = list(code)
    lo, hi = labels['FORWARD_COPY_INDEX'], labels['FORWARD_ROUTE_RETURN']
    hit = [pc for pc in range(lo, hi) if code[pc] == ('W', 18, '1')]
    need(len(hit) == 1, 'one copy-one instruction')
    stale[hit[0]] = ('W', 18, '0')
    mutants.append(('stale_zero_address_copy', stale, 'FORWARD'))
    inverse = list(code)
    inverse[labels['INVERSE']] = ('J', labels['FORWARD'])
    mutants.append(('forward_entry_in_inverse_pass', inverse, 'INVERSE'))
    out = []
    for name, mutant, direction in mutants:
        tapes, origins, payload, values = fixture(retained, previous, m, hardware, 2, 5, 3, 2)
        before = [(list(t.cells), t.head) for t in tapes[:-1]]
        old = dict(payload.cells)
        result = hardware.Program(mutant, labels, metadata).run(tapes, direction)
        need(result['status'] == 'DONE', 'semantic mutant genuinely returns: '+name)
        actual = decode_keys(payload, 0, 2)
        correct = [(i+(2 if direction == 'FORWARD' else -2)) % 3 if i < 3 else i for i in range(4)]
        need(actual != correct, 'direct complete-key oracle detects returning mutant: '+name)
        check_retirement(tapes, before, origins, old, payload, 2, 5, actual)
        out.append({'fault': name, 'keys': actual, 'expected': correct, 'returned_clean': True})
    dirty = list(code)
    hits = [pc for pc in range(labels['FORWARD_INDEX_RETIRE'], labels['INVERSE']) if code[pc] == ('W', 20, '_')]
    dirty[hits[-1]] = ('W', 20, '1')
    tapes, _, payload, _ = fixture(retained, previous, m, hardware, 2, 5, 3, 2)
    result = hardware.Program(dirty, labels, metadata).run(tapes)
    need(result['status'] == 'DONE' and tapes[20].cells[0] == '1', 'index retirement mutation detected')
    out.append({'fault': 'missing_index_origin_clear', 'detected_by': 'complete retained history'})
    no_return = list(code)
    no_return[labels['FORWARD_PAYLOAD_REWIND']] = ('J', labels['FORWARD_INDEX_RETIRE'])
    tapes, _, payload, _ = fixture(retained, previous, m, hardware, 2, 5, 3, 2)
    result = hardware.Program(no_return, labels, metadata).run(tapes)
    need(result['status'] == 'DONE' and payload.head != 0, 'omitted physical head-return detected')
    out.append({'fault': 'omitted_paid_payload_return', 'detected_by': 'actual payload head'})
    return out


def domain_controls(retained, previous, m, hardware, code, labels, metadata):
    controls = []
    changes = (
        ('wrong_payload_origin_code', 'bit', 0, 0),
        ('missing_payload_tag', 'bit', 25, 0),
        ('invalid_allocated_key_tag', 'bit', 27, 0),
        ('invalid_allocated_key_high_bit', 'bit', 30, 1),
        ('short_payload_frame', 'bit', 64, 0),
        ('long_payload_frame', 'bit', 169, 1),
        ('dirty_index_origin', 'marker', 20, '1'),
        ('dirty_address_origin', 'marker', 18, '1'),
    )
    for name, kind, where, value in changes:
        tapes, _, payload, _ = fixture(retained, previous, m, hardware, 2, 5, 3, 2)
        if kind == 'bit':
            if value:
                payload.cells[where] = value
            else:
                payload.cells.pop(where, None)
        else:
            tapes[where].cells[0] = value
        result = hardware.Program(code, labels, metadata).run(tapes)
        need(result['status'] == 'MALFORMED', 'structural malformed control: '+name)
        controls.append({'fault': name, 'status': result['status'], 'failure_rollback_claimed': False})
    tapes, _, payload, _ = fixture(retained, previous, m, hardware, 2, 5, 3, 2)
    tapes[14].cells[1] = '1'
    result = hardware.Program(code, labels, metadata).run(tapes)
    need(result['status'] == 'REJECT', 'height/header consistency remains checked by point service')
    controls.append({'fault': 'height_width_disagreement', 'status': 'REJECT'})
    tapes, _, payload, _ = fixture(retained, previous, m, hardware, 2, 5, 3, 2)
    tapes[20] = tapes[18]
    try:
        hardware.Program(code, labels, metadata).run(tapes)
    except ValueError as error:
        need(str(error) == 'fixed distinct physical owners', 'alias rejection reason')
    else:
        raise ValueError('index/address alias accepted')
    controls.append({'fault': 'index_address_alias', 'detected_by': 'physical owner binder'})
    return controls


def overwrite_boundary(retained, previous, m, base, hardware, code, labels, metadata):
    tapes, _, payload, values = fixture(retained, previous, m, hardware, 2, 5, 3, 2)
    old = dict(payload.cells)
    old_keys = decode_keys(payload, 0, 2)
    machine = hardware.Program(code, labels, metadata)
    for direction in ('FORWARD', 'INVERSE'):
        need(machine.run(tapes, direction)['status'] == 'DONE', 'full sorted overwrite boundary pass')
        buckets = (m.bit_tape(), m.bit_tape())
        base.literal_radix(m, m.route.RecordTape(m.binary, payload), tapes[19], buckets)
    need(decode_keys(payload, 0, 2) == list(range(4)) and payload.cells != old,
         'arbitrary overwritten keys are not inverted by inverse routing')
    need([value for key, value in base.observe_payload(payload, 2)] == values, 'opaque payload roundtrip still holds')
    return {'initial_keys': old_keys, 'final_keys': decode_keys(payload, 0, 2),
            'payload_restored': True, 'arbitrary_key_overwrite_invertibility_claimed': False}


def actual_controls(previous, m, base, caller, hardware, code, labels, metadata):
    moduli, values = (5, 7, 2, 3), (3, 2, 1, 1)
    _, _, expected, _ = previous.direct_leaf(moduli, values, base.TAGS)
    source, payload, fields = previous.fixture_case(m, base, moduli, values)
    caller.run_leg(m, base, hardware.Program(code, labels, metadata), source, payload, False, fault='stale_offset')
    need(base.observe_payload(payload, 2) != expected, 'stale actual numerical offset detected')
    source, payload, fields = previous.fixture_case(m, base, moduli, values)
    old = dict(payload.cells)
    machine = hardware.Program(code, labels, metadata)
    caller.run_leg(m, base, machine, source, payload, False)
    caller.run_leg(m, base, machine, source, payload, True, fault='forward_rows_in_inverse')
    need(payload.cells != old and base.coordinates(source, fields) == list(values),
         'wrong inverse key route detected even with source coordinates restored')
    return [{'fault': 'stale_actual_offset', 'detected_by': 'actual direct CRT payload oracle'},
            {'fault': 'wrong_actual_inverse_route', 'detected_by': 'whole physical payload roundtrip'}]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    retained, previous, base, m, key_pass, hardware, caller, code, labels, metadata, old_code = modules()
    result = {'status': 'PASS', 'static': static_checks(code, labels, metadata, old_code, caller),
              'uniform_passes': bounded_passes(retained, previous, m, hardware, code, labels, metadata),
              'returning_controls': semantic_controls(retained, previous, m, hardware, code, labels, metadata),
              'domain_controls': domain_controls(retained, previous, m, hardware, code, labels, metadata),
              'inverse_overwrite_boundary': overwrite_boundary(retained, previous, m, base, hardware, code, labels, metadata)}
    cases = (('exact_7388', (5, 7, 3, 2), (3, 2, 1, 1)),
             ('current_wire_sensitive', (5, 7, 2, 3), (3, 2, 1, 1)))
    result['actual_caller_cases'] = [actual_case(previous, m, base, caller, hardware, code, labels, metadata, *case)
                                     for case in cases]
    result['actual_controls'] = actual_controls(previous, m, base, caller, hardware, code, labels, metadata)
    result['source_hashes'] = {name: sha256((HERE/name).read_bytes()).hexdigest()
                              for name in ('key_pass.py', 'hardware.py', 'join.py', 'verify.py',
                                           'PROOF.md', 'SOURCE-PINS.json')}
    result['new_kappa'] = None
    result['scope'] = 'Uniform complete key pass for exactly the fixed 13-bit codeword / 12-bit opaque payload ABI; bounded actual source/radix join; mixed model and external acquisition retained.'
    rendered = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if args.receipt:
        args.receipt.write_text(rendered)
    print(json.dumps({'status': 'PASS', 'instructions': len(code), 'physical_tapes': 22,
                      'complete_key_passes': result['uniform_passes']['complete_passes'],
                      'actual_roundtrips': len(cases), 'controls': 19}, sort_keys=True))


if __name__ == '__main__':
    main()
