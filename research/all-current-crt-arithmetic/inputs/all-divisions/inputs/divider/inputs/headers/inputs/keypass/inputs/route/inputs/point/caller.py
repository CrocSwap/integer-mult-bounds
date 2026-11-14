"""Paid encoded leaf traversal with a literal direct-query/consume service.

Outer tape-control methods retain #7388's symbol-action model. The point
service and radix mover have separate literal instruction bills.
Apache-2.0; substantial OpenAI assistance.
"""


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def zero_counter(tape, *, offset=False):
    tape.step(1)
    while tape.read() in ('0', '1'):
        tape.write('0')
        tape.step(1)
    need(tape.read() == ('|' if offset else 'R'), 'counter frame terminator')
    if offset:
        tape.step(1)
        need(tape.read() == 'R', 'offset frame endpoint')
    tape.rewind()


def decrement(tape):
    tape.step(1)
    borrow = True
    while tape.read() != 'R':
        bit = tape.read()
        need(bit in ('0', '1'), 'encoded row digit')
        if borrow:
            tape.write('1' if bit == '0' else '0')
            borrow = bit == '0'
        tape.step(1)
    tape.rewind()
    return borrow


def route_address(leaf, point, headers, width, address, private, reverse, extra=()):
    """The current physical address is reread at every literal query."""
    layer = headers['selected_layer']
    zero_counter(layer)
    if reverse:
        width.step(1)
        need(width.read() == '1', 'positive encoded height')
        width.step(1)
        while width.read() == '1':
            need(not leaf.increment(layer), 'reverse layer construction fits')
            need(not leaf.increment(layer), 'reverse layer construction fits')
            width.step(1)
        need(width.read() == 'R', 'complete reverse target sequence')
        width.rewind()
    width.step(1)
    ascending = True
    ports = (*private, headers['h'], headers['modulus'], headers['offsets'],
             layer, address, width, *extra)
    while True:
        need(point.run(ports)['status'] == 'DONE', 'literal current query accepts')
        width.step(1 if ascending else -1)
        if ascending and width.read() == 'R':
            width.step(-1)
            width.step(-1)
            ascending = False
        if width.read() == 'L':
            break
        need(width.read() == '1', 'next encoded target cell')
        need(not (decrement(layer) if reverse else leaf.increment(layer)),
             'current row update fits encoded field')
    zero_counter(layer)


def prepare_keys(leaf, point, headers, record, width, index, address, private,
                 reverse, *, stale_wire=False):
    need(record.matches('<'), 'physical payload frame origin')
    record.move_word(1)
    index.emit('L')
    width.step(1)
    while width.read() == '1':
        index.emit('0')
        width.step(1)
    need(width.read() == 'R', 'actual encoded payload width')
    width.rewind()
    leaf.end_word(index)
    while True:
        record.pass_payload()
        leaf.copy_bits(index, address)
        route_address(leaf, point, headers, width, address, private, reverse,
                      (index,) if stale_wire else ())
        record.rekey(address)
        address.erase()
        if leaf.increment(index):
            break
    need(record.matches('>'), 'complete padded payload rectangle')
    while not record.matches('<'):
        record.move_word(-1)
    index.erase()


def run_leg(m, base, point, source, payload, reverse, *, fault=None):
    """One actual selected nonroot leaf; no runtime fixture geometry lookup."""
    need(fault in (None, 'stale_offset', 'stale_wire', 'forward_rows_in_inverse'),
         'only explicit verifier fault configurations')
    source_before = base.meter_actions(source.meter)
    source_snapshot = bytes(source.cells), source.head
    payload_before = base.bit_actions((payload,))
    front = m.reverse if reverse else m.f
    numeric = m.subtractive if reverse else m.numeric
    endpoint = m.writer.Endpoint(front, m.w, m.r, m.e, numeric, m.owner, m.bridge, source)
    iterator = endpoint.iterator
    numerical = (*iterator.bank.ports, *iterator.guards,
                 *iterator.counters.values(), endpoint.staging)
    headers = {name: m.join.Tape() for name in ('h', 'modulus', 'selected_layer', 'offsets')}
    width, index, address = (m.join.Tape() for _ in range(3))
    private = tuple(m.join.Tape() for _ in range(14))
    adapter_ports = (*headers.values(), width, index, address, *private)
    record = m.route.RecordTape(m.binary, payload)
    buckets = (m.bit_tape(), m.bit_tape())
    arena_meters = []
    point_before = point.instructions, point.core_instructions, point.calls, point.symbol_actions
    with base.seal_numerical_roles(m):
        lease = iterator.next()
        while lease is not None:
            arena_meters.append(lease.actual.context.arena.meter)
            if m.route.selected_leaf(iterator, lease):
                break
            lease.close()
            lease = iterator.next()
        need(lease is not None, 'actual selected nonroot leaf')
        result = lease.actual.result['stream']
        result_snapshot = bytes(result.cells), result.head
        m.route.emit_headers(m.join, iterator, lease, headers, width)
        observed = {name: ''.join(tape.cells) for name, tape in headers.items()}
        observed['width'] = ''.join(width.cells)
        if fault == 'stale_offset':
            zero_counter(headers['offsets'], offset=True)
        prepare_keys(m.route, point, headers, record, width, index, address, private,
                     False if fault == 'forward_rows_in_inverse' else reverse,
                     stale_wire=fault == 'stale_wire')
        machines, radix_tape_actions = base.literal_radix(m, record, width, buckets)
        need((bytes(source.cells), source.head) == source_snapshot and
             (bytes(result.cells), result.head) == result_snapshot and
             lease.actual.guide.head == 1 and iterator.counters['axis'].head == 1 and
             iterator.counters['half'].head == 1,
             'source/result bytes and borrowed heads before staging')
        endpoint.stage(lease)
        lease.close()
        endpoint.commit()
        if not iterator.closed:
            iterator.close()
    width.erase()
    for header in headers.values():
        header.erase()
    need(all(t.head == 0 and all(symbol == '_' for symbol in t.cells)
             for t in adapter_ports), 'all acquired query/controller histories retired')
    need(all(t.head == 1 and all(symbol == m.w.BLANK for symbol in t.cells)
             for t in numerical), 'all acquired numerical histories retired')
    need(all(t.head == 0 and not t.cells for t in buckets) and
         all(machine.status == 'accept' and not any(machine.registers) for machine in machines),
         'literal radix bucket and register retirement')
    need(source.head == 1 and payload.head == 0, 'actual source/payload heads return')
    histories = tuple(t.cells for t in (*numerical, *adapter_ports))
    need(len({id(cells) for cells in histories}) == len(histories), 'distinct retained symbol roles')
    receipt = {
        'direction': 'inverse' if reverse else 'forward',
        'selected_nodes': 1, 'skipped_nodes': len(arena_meters)-1,
        'observed_headers': observed,
        'encoded_source_symbol_actions': sum(base.meter_actions(t.meter) for t in (source, *numerical))
            - source_before + sum(base.meter_actions(meter) for meter in arena_meters),
        'outer_adapter_symbol_actions': sum(t.actions for t in adapter_ports)
            - (point.symbol_actions-point_before[3]),
        'query_symbol_actions_included_in_literal_bill': point.symbol_actions-point_before[3],
        'literal_query_instructions': point.instructions-point_before[0],
        'literal_core_instructions': point.core_instructions-point_before[1],
        'literal_query_calls': point.calls-point_before[2],
        'radix_bit_control_instructions': sum(sum(machine.census.values()) for machine in machines),
        'radix_passes': len(machines),
        'payload_adapter_bit_actions': base.bit_actions((payload, *buckets))-payload_before-radix_tape_actions,
        'retained_symbol_roles': len(histories), 'retained_symbol_cells': sum(map(len, histories)),
        'retained_bucket_bits': sum(t.extent for t in buckets),
        'retained_radix_register_bits': sum(len(machine.registers) for machine in machines),
    }
    return receipt, (histories, buckets, machines)
