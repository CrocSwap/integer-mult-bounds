"""Replay a live two-target CRT root through the retained literal mover. Apache-2.0."""

from argparse import ArgumentParser
import ast
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from math import prod
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FIXTURE_SOURCE = 'research/crt-multitarget-row-audit/verify.py'
PREDECESSOR = 'research/encoded-crt-leaf-payload/replay.py'
TAGS = tuple(293 + 131 * i for i in range(16))


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def authenticate():
    for pin in json.loads((HERE / 'SOURCES.json').read_text())['files']:
        if pin['usage'] == 'input':
            content = (ROOT / pin['path']).read_bytes()
            need(sha256(content).hexdigest() == pin['sha256'], f'input drift: {pin["path"]}')


def retained_cases():
    """Read the exact fixture literals without importing the audit's verifier."""
    tree = ast.parse((ROOT / FIXTURE_SOURCE).read_bytes())
    cases, = [statement.value for statement in tree.body if isinstance(statement, ast.Assign)
              and any(isinstance(name, ast.Name) and name.id == 'CASES' for name in statement.targets)]
    result = {}
    for entry in cases.elts:
        need(isinstance(entry, ast.Call) and isinstance(entry.func, ast.Name)
             and entry.func.id == 'dict' and not entry.args, 'literal predecessor fixture')
        case = {item.arg: ast.literal_eval(item.value) for item in entry.keywords}
        result[case['name']] = case
    return result


def source_fixture(m, case):
    """Encode the fixed test input outside the measured call boundary."""
    source, fields = m.e.Port(m.w), []
    for width, modulus, value in zip(case['widths'], case['moduli'], case['state'], strict=True):
        source.append(m.r.ROOT)
        for _ in range(width):
            source.append(m.w.ONE)
        source.append(m.r.WORD_END)
        for bit in range(width):
            source.append((modulus >> bit) & 1)
        source.append(m.r.WORD_END)
        cells = []
        for bit in range(width):
            cells.append(source.head)
            source.append((value >> bit) & 1)
        fields.append(cells)
        source.append(m.r.RECORD_END)
    source.append(m.w.RIGHT)
    source.rewind()
    source.cells.extend([m.w.ONE, m.w.ZERO, m.w.BLANK] * 3)
    return source, fields


def packet(m, width, tags):
    need(len(tags) == 1 << width and len(set(tags)) == len(tags)
         and all(0 < t < 4096 for t in tags), 'all slots have distinct nonzero markers')
    symbols = ['<']
    for position, tag in enumerate(tags):
        symbols.extend((('R', tag), *format(position, f'0{width}b')))
    symbols.append('>')
    return tuple(bit for symbol in symbols for bit in m.binary.bits(symbol))


def oracle(case):
    """Solve the left congruences by enumeration, then rotate each valid axis."""
    moduli, widths, state = case['moduli'], case['widths'], case['state']
    need(len(state) == 4 and all(x < p for x, p in zip(state[:2], moduli[:2])),
         'independent oracle for the retained valid-left four-axis root')
    left, = [z for z in range(prod(moduli[:2])) if all(
        (z - state[i] * prod(moduli[:i])) % moduli[i] == 0 for i in range(2))]
    offsets = []
    for i in (2, 3):
        modulus, prefix = moduli[i], prod(moduli[:i])
        c, = [v for v in range(modulus) if (prefix * v - left) % modulus == 0]
        offsets.append(c)

    def shift(x, i, sign):
        modulus = moduli[i + 2]
        return (x + sign * offsets[i]) % modulus if x < modulus else x

    slow, fast = (1 << width for width in widths[2:])
    maps = [[fast * shift(a, 0, sign) + shift(b, 1, sign)
             for a, b in product(range(slow), range(fast))] for sign in (1, -1)]
    need(all(maps[1][j] == i for i, j in enumerate(maps[0])), 'direct inverse permutation')
    updated = state[:2] + [shift(state[i + 2], i, 1) for i in range(2)]
    return left, offsets, updated, maps


def expected_headers(case, offsets):
    precision = 1 + sum(case['widths'])

    def word(number, suffix='R'):
        return 'L' + format(number, f'0{precision}b')[::-1] + suffix

    return [dict(h=word(width), modulus=word(modulus), selected_layer=word(0),
                 offsets=word(offset, '|R'), width='L' + '1' * width + 'R')
            for width, modulus, offset in zip(case['widths'][2:], case['moduli'][2:], offsets, strict=True)]


def new_headers(m, route):
    headers = tuple({name: m.join.Tape() for name in route.HEADER_NAMES} for _ in range(2))
    return headers, (m.join.Tape(), m.join.Tape()), m.join.Tape()


def observe_headers(headers, widths):
    return [dict({name: ''.join(tape.cells) for name, tape in header.items()},
                 width=''.join(width.cells)) for header, width in zip(headers, widths, strict=True)]


def borrowed_ports(it, lease):
    actual = lease.actual
    return (it.source, actual.result['stream'], actual.guide, actual.left, actual.right,
            it.counters['axis'], it.counters['half'])


def state_of(ports):
    return [(id(t.cells), bytes(t.cells), t.head, t.meter.writes) for t in ports]


def make_endpoint(m, source, reverse):
    return m.writer.Endpoint(m.reverse if reverse else m.f, m.w, m.r, m.e,
                             m.subtractive if reverse else m.numeric, m.owner, m.bridge, source)


def run_leg(previous, m, route, source, payload, *, reverse=False, staged=False):
    source_before = previous.meter_actions(source.meter)
    payload_before = previous.bit_actions((payload,))
    endpoint = make_endpoint(m, source, reverse)
    it = endpoint.iterator
    numeric_ports = (*it.bank.ports, *it.guards, *it.counters.values(), endpoint.staging)
    headers, widths, combined = new_headers(m, route)
    indices = tuple(m.join.Tape() for _ in range(2))
    scratch = tuple(m.join.Tape() for _ in range(3))
    header_ports = tuple(t for header in headers for t in header.values())
    bank = {name: ['_'] for name in (*m.rom.REGS, 'arena', 'spool', 'layers', 'rom')}
    bank_ids = tuple(map(id, bank.values()))
    layers, rom = m.join.Tape(bank['layers']), m.join.Tape(bank['rom'])
    adapter = (*header_ports, *widths, combined, *indices, *scratch, layers, rom)
    record = m.route.RecordTape(m.binary, payload)
    buckets = m.bit_tape(), m.bit_tape()
    runs, machines, bank_history, pass_counts = [], [], [], []
    radix_tape_actions = 0
    select_row_bit = m.join.select_row_bit
    row_queries = 0

    def count_query(row, countdown):
        nonlocal row_queries
        row_queries += 1
        return select_row_bit(row, countdown)

    with previous.seal_numerical_roles(m), patch.object(m.join, 'select_row_bit', count_query):
        lease, arena_meters = route.open_root(it)
        borrowed = borrowed_ports(it, lease)
        need(all(port.head == 1 for port in borrowed), 'actual root borrow entry heads')
        before = state_of(borrowed)
        route.emit_root_headers(m, it, lease, headers, widths, combined)
        header_receipt = observe_headers(headers, widths)
        for target, header in enumerate(headers):
            need(tuple(map(id, bank.values())) == bank_ids
                 and all(all(c == '_' for c in cells) for cells in bank.values()),
                 'same blank ROM bank including old tails')
            active = {name: tape.cells for name, tape in header.items()}
            service = bank | active
            run = m.rom.execute(m.rom_program, service)
            need(run['status'] == 'accept' and all(h == 0 for h in run['heads'].values()),
                 'live encoded producer accepts and returns every head')
            need(tuple(map(id, bank.values())) == bank_ids
                 and all(service[name] is cells for name, cells in bank.items()),
                 'producer retained the same backing identities')
            need(all(''.join(cells).rstrip('_') == header_receipt[target][name]
                     for name, cells in active.items()), 'actual producer preserves each active header')
            runs.append(run)
            bank_history.append(sum(map(len, bank.values())))
            route.rekey_axis(m, record, layers, widths, indices, scratch, target, reverse)
            layers.erase()
            rom.erase()
            for tape in header.values():
                tape.erase()
            if staged or target == len(headers) - 1:
                current_machines, tape_actions = previous.literal_radix(m, record, combined, buckets)
                machines.extend(current_machines)
                radix_tape_actions += tape_actions
                pass_counts.extend(sum(machine.census.values()) for machine in current_machines)
        need(state_of(borrowed) == before, 'actual borrows preserved before staging')
        endpoint.stage(lease)
        need(state_of(borrowed) == before, 'borrowed source still unchanged while staging')
        lease.close()
        endpoint.commit()
        if not it.closed:
            it.close()

    combined.erase()
    for width in widths:
        width.erase()
    need(all(p.head == 1 and all(c == m.w.BLANK for c in p.cells) for p in numeric_ports),
         'all owned encoded CRT tapes retired')
    need(all(p.head == 0 and all(c == '_' for c in p.cells) for p in adapter)
         and all(all(c == '_' for c in cells) for cells in bank.values()),
         'all header, routing and shared ROM tapes retired')
    need(all(t.head == 0 and not t.cells for t in buckets)
         and all(machine.status == 'accept' and not any(machine.registers) for machine in machines),
         'all literal bucket and control histories retired')
    need(source.head == 1 and payload.head == 0, 'both physical entry heads returned')

    symbol_cells = [p.cells for p in numeric_ports]
    symbol_cells += [p.cells for p in adapter if p is not layers and p is not rom]
    symbol_cells += list(bank.values())
    need(len({id(cells) for cells in symbol_cells}) == len(symbol_cells), 'no duplicate symbol backing')
    receipt = dict(
        mode='staged_forward' if staged else 'fused_inverse' if reverse else 'fused_forward',
        headers=header_receipt, producer_calls=len(runs), row_queries=row_queries,
        skipped_leases=len(arena_meters) - 1,
        encoded_source_symbol_actions=sum(previous.meter_actions(p.meter) for p in (source, *numeric_ports))
        - source_before + sum(previous.meter_actions(meter) for meter in arena_meters),
        adapter_symbol_actions=sum(p.actions for p in adapter),
        benes_instructions=sum(run['steps'] for run in runs),
        radix_bit_control_instructions=sum(pass_counts), radix_instructions_by_pass=pass_counts,
        payload_adapter_bit_actions=previous.bit_actions((payload, *buckets))
        - payload_before - radix_tape_actions,
        retained_symbol_roles=len(symbol_cells), retained_symbol_cells=sum(map(len, symbol_cells)),
        retained_rom_bank_cells_after_each_target=bank_history,
        retained_benes_registers=sum(len(run['registers']) for run in runs),
        retained_radix_register_bits=sum(len(machine.registers) for machine in machines),
        retained_bucket_bits=sum(tape.extent for tape in buckets), payload_visited_bits=payload.extent,
    )
    return receipt, (symbol_cells, buckets, machines, runs)


def check_frame(m, previous, payload, expected, width):
    need(previous.observe_payload(payload, width) == list(enumerate(expected))
         and payload.cells == m.bit_tape(packet(m, width, expected)).cells,
         'direct CRT forward frame mismatch')


def header_probe(previous, m, route, case):
    source, _ = source_fixture(m, case)
    it = make_endpoint(m, source, False).iterator
    headers, widths, combined = new_headers(m, route)
    with previous.seal_numerical_roles(m):
        lease, _ = route.open_root(it)
        ports = borrowed_ports(it, lease)
        before = state_of(ports)
        route.emit_root_headers(m, it, lease, headers, widths, combined)
        need(state_of(ports) == before, 'control preserves live headers and source')
        lease.close()
        if not it.closed:
            it.close()
    observed = observe_headers(headers, widths)
    for header, width in zip(headers, widths, strict=True):
        for tape in (*header.values(), width):
            tape.erase()
    combined.erase()
    return observed


def check_header_alignment(previous, m, route, case):
    _, offsets, _, _ = oracle(case)
    expected = expected_headers(case, offsets)
    need(case['widths'][2] != case['widths'][3] and len(set(offsets)) == 2,
         'control distinguishes both ordered widths and offsets')
    observed = header_probe(previous, m, route, case)
    need(observed == expected, 'distinct live header alignment')
    copy = m.join.copy_numeric_field
    first = None

    def stale_offset(source, target, guide, words, delimiter, suffix):
        nonlocal first
        copy(source, target, guide, words, delimiter, suffix)
        if first is None:
            first = target
            return
        first.step(1)
        target.step(1)
        while first.read() in m.route.BITS:
            target.write(first.read())
            first.step(1)
            target.step(1)
        need(first.read() == target.read() == '|', 'stale control preserves field shape')
        first.rewind()
        target.rewind()

    with patch.object(m.join, 'copy_numeric_field', stale_offset):
        mutated = header_probe(previous, m, route, case)
    need(mutated[0] == expected[0] and mutated[1] == (expected[1] | {'offsets': expected[0]['offsets']})
         and mutated != expected, 'stale offset must fail ordered header oracle')
    return dict(case=case['name'], headers=observed, stale_second_offset_rejected=True)


def replay(previous, m, route, cases):
    case = cases['two_short_first']
    left, offsets, forward_state, maps = oracle(case)
    width = sum(case['widths'][2:])
    initial_packet = packet(m, width, TAGS)
    forward_tags = [tag for _, tag in sorted(zip(maps[0], TAGS, strict=True))]
    expected = expected_headers(case, offsets)
    source, fields = source_fixture(m, case)
    payload = m.bit_tape(initial_packet)
    source_initial, payload_initial = bytes(source.cells), dict(payload.cells)
    source_id, payload_id = id(source.cells), id(payload.cells)
    target_source = bytearray(source_initial)
    for field, value in zip(fields, forward_state, strict=True):
        for bit, cell in enumerate(field):
            target_source[cell] = (value >> bit) & 1

    forward, forward_keep = run_leg(previous, m, route, source, payload)
    check_frame(m, previous, payload, forward_tags, width)
    need(bytes(source.cells) == target_source and id(source.cells) == source_id
         and id(payload.cells) == payload_id, 'exact forward source and same backing')
    inverse, inverse_keep = run_leg(previous, m, route, source, payload, reverse=True)
    need(bytes(source.cells) == source_initial and payload.cells == payload_initial
         and id(source.cells) == source_id and id(payload.cells) == payload_id,
         'exact inverse source, payload and backing')
    need({id(c) for c in forward_keep[0]}.isdisjoint(id(c) for c in inverse_keep[0]),
         'only actual boundary tapes are shared across legs')

    staged_source, _ = source_fixture(m, case)
    staged_payload = m.bit_tape(initial_packet)
    staged, _staged_keep = run_leg(previous, m, route, staged_source, staged_payload, staged=True)
    check_frame(m, previous, staged_payload, forward_tags, width)
    need(bytes(staged_source.cells) == target_source, 'staged forward same source')
    need(all(leg['headers'] == expected and leg['producer_calls'] == 2 for leg in (forward, inverse, staged)),
         'both independently checked live headers on every leg')
    need(forward['row_queries'] == inverse['row_queries'] == staged['row_queries'] == 96,
         'all physical row queries executed')
    same_forward = ('benes_instructions', 'encoded_source_symbol_actions',
                    'retained_rom_bank_cells_after_each_target', 'retained_symbol_cells',
                    'retained_bucket_bits', 'payload_visited_bits')
    need(all(forward[key] == staged[key] for key in same_forward), 'matched source and routing work')
    need(all(forward[key] <= staged[key] for key in ('adapter_symbol_actions',
             'payload_adapter_bit_actions', 'retained_radix_register_bits')), 'no measured adapter tradeoff')
    need([len(leg['radix_instructions_by_pass']) for leg in (forward, inverse, staged)] == [4, 4, 8],
         'literal fused and staged pass counts')
    need(forward['skipped_leases'] == staged['skipped_leases'] == 2 and inverse['skipped_leases'] == 0,
         'actual encoded forward and reverse root lease schedules')
    need(staged['radix_bit_control_instructions'] > forward['radix_bit_control_instructions'],
         'strictly lower measured radix instruction count')

    drop_source, _ = source_fixture(m, case)
    drop_payload = m.bit_tape(initial_packet)
    rekey = route.rekey_axis

    def omit_fast(m, record, layers, widths, indices, scratch, target, reverse):
        if target == 0:
            rekey(m, record, layers, widths, indices, scratch, target, reverse)

    with patch.object(route, 'rekey_axis', omit_fast):
        drop, _drop_keep = run_leg(previous, m, route, drop_source, drop_payload)
    dropped_tags = [tag for _, tag in previous.observe_payload(drop_payload, width)]
    dropped_slot = dropped_tags.index(TAGS[0])
    need(dropped_slot == 4 and maps[0][0] == 5
         and dropped_tags != forward_tags and bytes(drop_source.cells) == target_source
         and drop['headers'] == expected and drop['row_queries'] == 48,
         'missing fast target fails physical placement despite correct source update')
    previous.reverse_order_control(m)
    previous.truncated_layers_control(m)
    alignment = check_header_alignment(previous, m, route, cases['growing_bank'])

    return dict(status='PASS_ENCODED_CRT_TWO_TARGET_PAYLOAD', fixture=case['name'],
                moduli=case['moduli'], widths=case['widths'], reconstructed_left=left,
                input_source=case['state'], forward_source=forward_state,
                input_tags=list(TAGS), forward_tags=forward_tags,
                forward_destinations=maps[0], inverse_destinations=maps[1],
                restored_source_and_payload=True, source_retained_cells=len(source.cells),
                executions=[forward, inverse, staged],
                forward_radix_instructions_saved=staged['radix_bit_control_instructions']
                - forward['radix_bit_control_instructions'],
                controls=dict(dropped_fast_first_tag_actual_slot=dropped_slot,
                              dropped_fast_first_tag_required_slot=maps[0][0],
                              noncommuting_row_order=True, truncated_layers_rejected=True,
                              ordered_header_alignment=alignment))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    authenticate()
    previous = load('leaf_replay', ROOT / PREDECESSOR)
    route = load('two_target_route', HERE / 'route.py')
    result = replay(previous, previous.modules(), route, retained_cases())
    result_file = HERE / 'RESULT.json'
    serialized = json.dumps(result, sort_keys=True, indent=2) + '\n'
    if args.write_result:
        result_file.write_text(serialized)
    else:
        need(result_file.read_text() == serialized, 'committed exact result differs')
    print(f'{result["status"]} records=16 radix_passes=4/8 '
          f'radix_instructions_saved={result["forward_radix_instructions_saved"]} controls=4')


if __name__ == '__main__':
    main()
