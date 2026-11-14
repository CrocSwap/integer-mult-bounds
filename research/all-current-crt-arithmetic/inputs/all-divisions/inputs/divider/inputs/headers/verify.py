"""Bounded exact-source header and joined key-pass verification.

Fixture decoding is observation only, never part of the runtime graph.
Read-only by default; --receipt explicitly writes a result. Apache-2.0.
"""
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
GRAPH = '267752d474d8b1565ceb0415609b34e75797d8c6b735600242ceb410613b0508'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def modules():
    for pin in json.loads((HERE/'SOURCE-PINS.json').read_text())['files']:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'], 'exact retained bytes')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'], 'exact retained blob')
    prior = load(HERE/'inputs/keypass/verify.py', '_B9_retained_B7')
    _, previous, base, m, key_pass, _, _, key_code, _, _, _ = prior.modules()
    headers = load(HERE/'headers.py', '_B9_headers')
    hardware = load(HERE/'hardware.py', '_B9_hardware')
    caller = load(HERE/'join.py', '_B9_join').bind(hardware.NativePort, hardware.BitPort)
    code, labels, metadata = headers.compile_headers()
    need(len(code) == 21513 and headers.digest(code) == GRAPH, 'fixed header graph')
    return prior, previous, base, m, headers, hardware, caller, code, labels, metadata, key_code


def embedding(code, metadata, key_code):
    start = metadata['key_start']
    need(metadata['key_length'] == len(key_code), 'whole exact key child')
    for pc, (op, *args) in enumerate(key_code):
        if op == 'R':
            expected = (op, args[0], {s: start+target for s, target in args[1].items()})
        elif op == 'J':
            expected = (op, start+args[0])
        else:
            expected = (op, *args)
        need(code[start+pc] == expected, 'exact unchanged key instruction '+str(pc))


def static_checks(code, labels, metadata, key_code):
    embedding(code, metadata, key_code)
    need({row[1] for row in code if row[0] in ('R', 'W', 'M')} == set(range(27)), 'fixed role inventory')
    need(not any(row[0] == 'W' and row[1] in range(22, 26) for row in code), 'zero borrowed writes')
    for op, *args in code:
        need(op in ('R', 'W', 'M', 'J', 'H'), 'literal alphabet')
        if op == 'M':
            need(args[1] in (-1, 1), 'unit move only')
        targets = args[1].values() if op == 'R' else (args[0],) if op == 'J' else ()
        need(all(0 <= pc < len(code) for pc in targets), 'fixed internal continuations')
    mutant = list(code)
    pc = metadata['key_start']+next(i for i, row in enumerate(key_code) if row[0] == 'J')
    mutant[pc] = ('J', 0)
    try:
        embedding(mutant, metadata, key_code)
    except ValueError:
        return {'key_instructions_checked': len(key_code), 'mutated_child_relocation_rejected': True,
                'borrowed_write_targets': [], 'roles': 27}
    raise ValueError('relocation mutant escaped')


def bits(value, width):
    return [str((value >> bit) & 1) for bit in range(width)]


def fixture(m, hardware, widths, *, s=None, a=None, history=0, translated=False):
    h, u = widths[-1], widths[-2]
    p, count = u+h+1, len(widths)
    need(count >= 3 and p >= 4, 'declared local header fixture')
    if s is None:
        s = (1 << h)-1
    if a is None:
        a = max(0, s-1)
    source = []
    for index, width in enumerate(widths):
        modulus = s if index == count-1 else (1 << width)-1
        value = (index+1) % (1 << width)
        source += ['ROOT']+['1']*width+['WE']+bits(modulus, width)+['WE']+bits(value, width)+['RE']
    source.append('R')
    native_tokens = [source, ['1']*(count-2)+['STEP', '1', 'R'], ['1']*p,
                     ['ROOT']+bits(a, p)+['WE', 'ROOT', '1', 'RE', 'R'], []]
    native, origins = [], [0]*27
    for offset, tokens in enumerate(native_tokens):
        role = offset+22
        tape = m.e.Port(m.w)
        for symbol in tokens:
            tape.append(hardware.NUMERIC_VALUES[symbol])
        tape.rewind()
        if history:
            tape.cells.extend([m.w.BLANK]*history)
        if translated:
            shift = role-18
            tape.cells[:0] = bytearray([m.r.RETURN]*shift)
            tape.head += shift
            origins[role] = shift
        native.append(tape)
    marker = [m.join.Tape(['_']*(1+history)) for _ in range(21)]
    for role, tape in enumerate(marker):
        if translated:
            shift = role%4+1
            tape.cells[:0] = ['|']*shift
            tape.head += shift
            origins[role] = shift
    payload = m.bit_tape()
    tapes = (*marker, hardware.BitPort(payload), *(hardware.NativePort(t) for t in native))
    iterator = object.__new__(m.f.Iterator)
    iterator.w, iterator.r, iterator.source = m.w, m.r, native[0]
    iterator.counters = {'axis': native[1], 'width': native[4]}
    lease = types.SimpleNamespace(actual=types.SimpleNamespace(guide=native[2], result={'stream': native[3]}))
    output = {'h': marker[14], 'modulus': marker[15], 'offsets': marker[16], 'selected_layer': marker[17]}
    params = {'h': h, 'p': p, 'm': count-2, 'U': sum(widths[:-1]), 'W': max(widths[:-1]),
              's': s, 'a': a, 'widths': list(widths)}
    return tapes, native, origins, iterator, lease, output, marker[19], params


def boundary(tapes, native, origins, params, before, *, retired=False):
    h, p, s, a = (params[x] for x in ('h', 'p', 's', 'a'))
    expected = {14: ['L']+bits(h, p)+['R'], 15: ['L']+bits(s, p)+['R'],
                16: ['L']+bits(a, p)+['|', 'R'], 17: ['L']+['0']*p+['R'],
                19: ['L']+['1']*h+['R']}
    for role in range(21):
        tape, origin = tapes[role], origins[role]
        need(tape.head == origin, 'every marker head returns')
        need(tape.cells[:origin] == before[role][0][:origin], 'opaque marker exterior preserved')
        if role in expected and not retired:
            wanted = expected[role]
            need(tape.cells[origin:origin+len(wanted)] == wanted, 'exact arithmetic header role'+str(role))
            need(all(x == '_' for x in tape.cells[origin+len(wanted):]), 'retained marker tail stays blank')
        else:
            need(all(x == '_' for x in tape.cells[origin:]), 'owned body and marker fully retired')
    for role in range(22, 26):
        need((bytes(tapes[role].cells), tapes[role].head) == before[role], 'borrowed bytes and first-body head')
    scratch, origin = native[4], origins[26]
    need(scratch.head == origin+1 and scratch.cells[origin] == 2, 'scratch guard and first-body return')
    need(scratch.cells[:origin] == before[26][0][:origin], 'opaque native exterior preserved')
    need(all(x == 4 for x in scratch.cells[origin+1:]), 'complete width scratch blank')
    need(all(len(t.cells) >= len(before[i][0]) for i, t in enumerate(tapes) if i != 21),
         'historical backing never truncated')


def snapshots(tapes):
    return [(dict(t.cells), t.head) if i == 21 else
            (bytes(t.cells), t.head) if i >= 22 else (list(t.cells), t.head)
            for i, t in enumerate(tapes)]


def expected_build(params):
    h, p, m, u = (params[x] for x in ('h', 'p', 'm', 'U'))
    return 6*p*h+53*p+41*u+57*m+42*h+199-h.bit_count()


def expected_native(params):
    h, p, m, u = (params[x] for x in ('h', 'p', 'm', 'U'))
    return 30*u+47*m+12*h+20*p+113


def header_case(m, hardware, code, labels, metadata, widths, **kwargs):
    case = fixture(m, hardware, widths, **kwargs)
    tapes, native, origins, iterator, lease, output, width, params = case
    before = snapshots(tapes)
    program = hardware.Program(code, labels, metadata)
    result = program.run(tapes, 'BUILD')
    need(result['status'] == 'HEADERS', 'typed current headers accept')
    need(result['instructions'] == expected_build(params), 'universal exact construction bill')
    need(result['native_actions'] == expected_native(params), 'universal exact source overlap')
    boundary(tapes, native, origins, params, before)
    q = 3*params['U']+4*params['m']+3*params['h']+9
    lengths = (q, params['m']+1, params['p']+1, params['p']+3, params['W']+2)
    for role, length in zip(range(22, 27), lengths):
        need(result['history'][role] == [origins[role], origins[role]+length], 'exact native visited interval')
    old = fixture(m, hardware, widths, **kwargs)
    m.route.emit_headers(m.join, old[3], old[4], old[5], old[6])
    for role in (14, 15, 16, 17, 19):
        need(tapes[role].cells == old[0][role].cells and tapes[role].head == old[0][role].head,
             'exact original emit_headers output')
    retired = program.run(tapes, 'RETIRE')
    need(retired['status'] == 'RETIRED' and retired['instructions'] == 28*params['p']+7*params['h']+53,
         'universal exact retirement bill')
    need(retired['native_actions'] == 0, 'retirement needs no closed native owner access')
    boundary(tapes, native, origins, params, before, retired=True)
    return {**params, 'history': kwargs.get('history', 0), 'translated': kwargs.get('translated', False),
            'build_instructions': result['instructions'], 'retire_instructions': retired['instructions'],
            'native_actions': result['native_actions'], 'source_length': q,
            'scratch_interval_cells': params['W']+3, 'exact_source_helper_match': True}


def header_cases(m, hardware, code, labels, metadata):
    cases = []
    for h in range(1, 5):
        for s in range(1, 1 << h):
            for a in sorted({0, s-1}):
                cases.append(header_case(m, hardware, code, labels, metadata, (1, 2, 2, h), s=s, a=a))
    for h in (7, 8, 15, 16, 31, 32, 129):
        cases.append(header_case(m, hardware, code, labels, metadata, (1, 1, 3, h),
                                 history=37, translated=True))
    for widths in ((4097, 1, 2, 2), (*([1]*126), 2, 3), (3, 3, 257, 2), (1, 2, 1)):
        cases.append(header_case(m, hardware, code, labels, metadata, widths,
                                 history=83, translated=True))
    for a in (0, 16):
        cases.append(header_case(m, hardware, code, labels, metadata, (3, 3, 2, 5), s=17, a=a))
    return {'cases': cases, 'count': len(cases),
            'completed_domain': 'All h=1..4, s=1..2^h-1, a in {0,s-1}, fixed prefix/left widths; plus listed stress packets.',
            'untouched_region': 'Other finite packets are not exhaustively enumerated; the proof supplies the all-width statement.',
            'seed': None, 'stopping_rule': 'Exactly this deterministic list, no adaptive search.',
            'instructions': sum(x['build_instructions']+x['retire_instructions'] for x in cases)}


def domain_controls(m, hardware, code, labels, metadata):
    controls = []
    for name in ('wrong_native_entry', 'wrong_root', 'empty_prefix_width', 'short_prefix_field',
                 'early_right_end', 'root_axis', 'short_guide', 'short_result',
                 'dirty_output_origin', 'dirty_output_body', 'dirty_mode', 'alias'):
        tapes, native, origins, iterator, lease, output, width, params = fixture(m, hardware, (3, 3, 2, 3))
        if name == 'wrong_native_entry': native[0].head += 1
        elif name == 'wrong_root': native[0].cells[1] = m.r.VALUE
        elif name == 'empty_prefix_width': native[0].cells[2] = m.r.WORD_END
        elif name == 'short_prefix_field': native[0].cells[6] = m.r.WORD_END
        elif name == 'early_right_end': native[0].cells[-2] = m.w.RIGHT
        elif name == 'root_axis': native[1].cells[1] = m.r.STEP
        elif name == 'short_guide': native[2].cells[2] = m.w.BLANK
        elif name == 'short_result': native[3].cells[3] = m.r.WORD_END
        elif name == 'dirty_output_origin': tapes[14].cells[0] = '1'
        elif name == 'dirty_output_body': tapes[14].cells.extend(['1'])
        elif name == 'dirty_mode': tapes[0].cells[0] = '1'
        elif name == 'alias': tapes = (*tapes[:25], hardware.NativePort(native[2]), tapes[26])
        program = hardware.Program(code, labels, metadata)
        if name == 'alias':
            try:
                program.run(tapes, 'BUILD')
            except ValueError as error:
                need(str(error) == 'fixed distinct physical owners', 'alias guard reason')
                controls.append({'name': name, 'rejected_by': 'physical binder', 'instructions': 0})
                continue
            raise ValueError('alias accepted')
        result = program.run(tapes, 'BUILD')
        need(result['status'] == 'MALFORMED', 'encoded invalid control rejects '+name)
        need(not any(result['writes'][22:26]), 'rejection does not write borrowed fields')
        controls.append({'name': name, 'status': result['status'], 'instructions': result['instructions'],
                         'failure_cleanup_claimed': False})
    return controls


def returning_controls(m, hardware, code, labels, metadata):
    controls = []
    outer = metadata['key_start']
    offset_one = next(pc for pc, row in enumerate(code[:outer]) if row == ('W', 16, '1'))
    modulus_zero = next(pc for pc, row in enumerate(code[:outer]) if row == ('W', 15, '0'))
    scratch_clear = next(pc for pc in range(labels['LEFT_RECORD'], labels['RIGHT_HEADERS'])
                         if code[pc] == ('W', 26, '_'))
    native_return = max(pc for pc in range(labels['HEADERS_READY']) if code[pc] == ('M', 25, 1))
    retire_clear = next(pc for pc in range(labels['RETIRE'], outer) if code[pc] == ('W', 16, '_'))
    mutations = {'omitted_height_increment': (labels['HEIGHT_INCREMENT'], ('J', labels['HEIGHT_COUNTED'])),
                 'stale_zero_offset': (offset_one, ('W', 16, '0')),
                 'wrong_current_modulus_bit': (modulus_zero, ('W', 15, '1')),
                 'missing_scratch_erase': (scratch_clear, ('J', scratch_clear+1)),
                 'missing_result_head_return': (native_return, ('J', native_return+1)),
                 'missing_offset_retirement': (retire_clear, ('J', retire_clear+1))}
    for name, (pc, replacement) in mutations.items():
        mutant = list(code)
        mutant[pc] = replacement
        case = fixture(m, hardware, (3, 3, 2, 2), s=2 if name == 'wrong_current_modulus_bit' else 3,
                       a=1 if name == 'wrong_current_modulus_bit' else 2)
        tapes, native, origins, _, _, _, _, params = case
        before = snapshots(tapes)
        program = hardware.Program(mutant, labels, metadata)
        result = program.run(tapes, 'BUILD')
        need(result['status'] == 'HEADERS', 'returning construction mutant actually returns')
        retired = name == 'missing_offset_retirement'
        if retired:
            result = program.run(tapes, 'RETIRE')
            need(result['status'] == 'RETIRED', 'returning cleanup mutant actually returns')
        try:
            boundary(tapes, native, origins, params, before, retired=retired)
        except ValueError as error:
            controls.append({'name': name, 'pc': pc, 'returned': result['status'], 'detected_by': str(error)})
        else:
            raise ValueError('returning semantic mutant escaped '+name)
    return controls, {'stale_offset_pc': offset_one, 'wrong_modulus_pc': modulus_zero}


def actual_case(previous, m, base, caller, hardware, code, labels, metadata, name, moduli, values):
    source, payload, fields = previous.fixture_case(m, base, moduli, values)
    original = bytes(source.cells), source.head, dict(payload.cells), payload.head
    offset, destinations, expected_payload, expected_values = previous.direct_leaf(moduli, values, base.TAGS)
    old = next(x for x in json.loads((HERE/'inputs/keypass/RESULT.json').read_text())['actual_caller_cases']
               if x['name'] == name)
    machine = hardware.Program(code, labels, metadata)
    directions, ownership = [], []
    counters = ('native_actions', 'header_instructions', 'retire_instructions', 'key_instructions',
                'route_instructions', 'point_instructions', 'payload_bit_actions', 'routes')
    for reverse in (False, True):
        before = {key: getattr(machine, key) for key in counters}
        receipt, owned = caller.run_leg(m, base, machine, source, payload, reverse)
        delta = {key: getattr(machine, key)-before[key] for key in counters}
        raw_source = receipt.pop('encoded_source_symbol_actions')
        raw_payload = receipt.pop('payload_adapter_bit_actions')
        total = receipt.pop('literal_query_instructions')
        receipt.update(remaining_source_symbol_actions=raw_source-delta['native_actions'],
                       native_actions_included_in_literal_bill=delta['native_actions'],
                       remaining_payload_adapter_bit_actions=raw_payload-delta['payload_bit_actions'],
                       payload_bit_actions_included_in_literal_bill=delta['payload_bit_actions'],
                       literal_header_key_retirement_instructions=total,
                       literal_header_instructions=delta['header_instructions'],
                       literal_retirement_instructions=delta['retire_instructions'],
                       literal_key_instructions=delta['key_instructions'],
                       literal_route_instructions=delta['route_instructions'],
                       literal_point_instructions=delta['point_instructions'])
        prior = old['directions'][int(reverse)]
        need(receipt['remaining_source_symbol_actions'] == prior['encoded_source_symbol_actions']-592,
             'true old header/native overlap removed exactly once')
        need(delta['header_instructions'] == 1051 and delta['retire_instructions'] == 207
             and delta['native_actions'] == 571, 'exact current physical header bill')
        need(delta['key_instructions'] == prior['literal_key_pass_instructions'], 'identical B7 workload')
        need(delta['routes'] == 4 and receipt['literal_query_calls'] == 12, 'actual four current wires')
        need(receipt['outer_adapter_symbol_actions'] == 14
             and receipt['remaining_payload_adapter_bit_actions'] == 156, 'complete residual action meters')
        for key in ('radix_bit_control_instructions', 'radix_passes', 'retained_symbol_roles',
                    'retained_symbol_cells', 'retained_bucket_bits', 'retained_radix_register_bits'):
            need(receipt[key] == prior[key], 'unchanged retained provider '+key)
        directions.append(receipt)
        ownership.append(owned)
        if not reverse:
            need(base.observe_payload(payload, 2) == expected_payload, 'direct current CRT tag oracle')
            need(base.coordinates(source, fields) == expected_values, 'direct current source coordinate oracle')
    need((bytes(source.cells), source.head, dict(payload.cells), payload.head) == original,
         'complete source/payload/identity-key sorted roundtrip')
    histories = (*ownership[0][0], *ownership[1][0])
    need(len(histories) == len({id(x) for x in histories}) == 200, 'unchanged actual owner union')
    return {'name': name, 'moduli': list(moduli), 'input': list(values), 'offset': offset,
            'forward_destinations': destinations, 'directions': directions,
            'retained_owners_both_directions': 200, 'retained_symbol_cells_both': sum(map(len, histories)),
            'complete_physical_roundtrip': True}


def actual_controls(previous, m, base, caller, hardware, code, labels, metadata, mutation_pcs):
    controls = []
    for name, moduli, pc, replacement in (
            ('returning_stale_current_offset', (5, 7, 2, 3), mutation_pcs['stale_offset_pc'], ('W', 16, '0')),
            ('returning_wrong_current_modulus', (5, 7, 3, 2), mutation_pcs['wrong_modulus_pc'], ('W', 15, '1'))):
        mutant = list(code)
        mutant[pc] = replacement
        source, payload, fields = previous.fixture_case(m, base, moduli, (3, 2, 1, 1))
        _, _, expected, source_values = previous.direct_leaf(moduli, (3, 2, 1, 1), base.TAGS)
        machine = hardware.Program(mutant, labels, metadata)
        receipt, _ = caller.run_leg(m, base, machine, source, payload, False)
        need(base.coordinates(source, fields) == source_values, 'returning mutant leaves numerical source correct')
        need(base.observe_payload(payload, 2) != expected, 'current-value payload oracle detects returning fault')
        need(machine.last['status'] == 'RETIRED' and source.head == 1 and payload.head == 0,
             'fault actually completes all cleanup and head checks')
        controls.append({'name': name, 'pc': pc, 'caller_returned': True, 'source_coordinates_correct': True,
                         'all_caller_retirement_checks_passed': True, 'payload_oracle_detected': True,
                         'instructions': receipt['literal_query_instructions']})
    return controls


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', type=Path)
    args = parser.parse_args()
    prior, previous, base, m, headers, hardware, caller, code, labels, metadata, key_code = modules()
    static = static_checks(code, labels, metadata, key_code)
    uniform = header_cases(m, hardware, code, labels, metadata)
    domain = domain_controls(m, hardware, code, labels, metadata)
    returning, mutation_pcs = returning_controls(m, hardware, code, labels, metadata)
    actual = [actual_case(previous, m, base, caller, hardware, code, labels, metadata, name, moduli, (3, 2, 1, 1))
              for name, moduli in (('exact_7388', (5, 7, 3, 2)), ('current_wire_sensitive', (5, 7, 2, 3)))]
    actual_faults = actual_controls(previous, m, base, caller, hardware, code, labels, metadata, mutation_pcs)
    result = {'status': 'PASS', 'scope': 'Uniform typed actual-source headers and bounded current four-tag join',
              'new_kappa': False, 'graph': GRAPH, 'instructions': len(code), 'roles': 27,
              'static': static, 'uniform_headers': uniform, 'domain_controls': domain,
              'returning_controls': returning, 'actual_caller_cases': actual,
              'actual_returning_controls': actual_faults, 'source_seams': caller.exact_header_seams,
              'source_hashes': {name: sha256((HERE/name).read_bytes()).hexdigest()
                                for name in ('headers.py', 'hardware.py', 'join.py', 'PROOF.md')}}
    text = json.dumps(result, indent=2, sort_keys=True)+'\n'
    if args.receipt:
        args.receipt.write_text(text)
    print(json.dumps({'status': 'PASS', 'uniform_headers': uniform['count'],
                      'uniform_instructions': uniform['instructions'], 'actual_roundtrips': len(actual),
                      'controls': len(domain)+len(returning)+len(actual_faults)+1,
                      'graph': GRAPH, 'new_kappa': False}, sort_keys=True))


if __name__ == '__main__':
    main()
