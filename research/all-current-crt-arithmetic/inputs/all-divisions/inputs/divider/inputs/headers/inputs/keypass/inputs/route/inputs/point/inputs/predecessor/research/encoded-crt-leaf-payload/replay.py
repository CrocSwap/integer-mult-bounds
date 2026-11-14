"""Source-bound finite replay of one encoded CRT payload fiber. Apache-2.0."""

from argparse import ArgumentParser
from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path
from types import ModuleType, SimpleNamespace
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = json.loads((HERE / 'INPUT-PINS.json').read_text())
TAGS = (0x125, 0x2DA, 0x389, 0xE61)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate(path, pin):
    data = path.read_bytes()
    need(len(data) == pin['bytes'] and sha256(data).hexdigest() == pin['sha256'],
         f'source bytes changed: {pin["path"]}')
    git_blob = b'blob ' + str(len(data)).encode() + b'\0' + data
    need(sha1(git_blob).hexdigest() == pin['git_blob'], 'source Git blob changed')


def load(name, path):
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def modules():
    for pin in PINS['canonical']:
        authenticate(ROOT / pin['path'], pin)
    for pin in PINS['retained']:
        authenticate(HERE / 'frozen' / pin['file'], pin)
    canonical = {Path(p['path']).name: ROOT / p['path'] for p in PINS['canonical']}
    w = load('words', canonical['words.py'])  # The retained records module imports this name.
    r = load('payload_records', canonical['records.py'])
    e = load('payload_entry', canonical['entry.py'])
    numeric = load('payload_numeric', canonical['producer.py'])
    owner = load('payload_owner', canonical['owner.py'])
    bridge = load('payload_bridge', canonical['bridge.py'])
    f = load('payload_forward_frontend', HERE / 'frozen/frontend.py')
    reverse = load('payload_reverse_frontend', HERE / 'frozen/inverse_frontend.py').bind(f)
    writer = load('payload_writer', HERE / 'frozen/endpoint.py')
    subtractive = load('payload_subtractive', HERE / 'frozen/inverse_producer.py')
    join = load('payload_query', canonical['join.py'])
    rom = load('payload_benes', canonical['microcode.py'])
    binary = load('payload_binary', canonical['binary.py'])
    radix = load('payload_radix', canonical['radix.py'])
    builder = load('payload_radix_builder', canonical['machine.py'])
    program, _, registers = binary.compile_program(radix.assemble(builder), lifecycle=True)
    route = load('payload_route', HERE / 'route.py')
    fixture = next(case for case in json.loads(canonical['RESULT.json'].read_text())['cases']
                   if case['name'] == 'nonroot_roundtrip')

    class MeasuredBitTape(binary.BitTape):
        def __init__(self, initial=()):
            super().__init__(initial)
            self.extent = max(1, len(initial))

        def move(self, direction):
            super().move(direction)
            self.extent = max(self.extent, self.head + 1)

    return SimpleNamespace(w=w, r=r, e=e, numeric=numeric, owner=owner, bridge=bridge,
                           f=f, reverse=reverse, writer=writer, subtractive=subtractive,
                           join=join, rom=rom, binary=binary, program=program,
                           registers=registers, rom_program=rom.producer_program(),
                           route=route, fixture=fixture, bit_tape=MeasuredBitTape)


@contextmanager
def seal_numerical_roles(m):
    def deny(*_args, **_kwargs):
        raise ValueError('new numerical role or host word inspection during execution')

    owners = ((m.e.Port, '__init__'), (m.w.Word, '__init__'), (m.w.Arena, '__init__'),
              (m.w.Word, 'inspect'))
    originals = [getattr(kind, method) for kind, method in owners]
    for kind, method in owners:
        setattr(kind, method, deny)
    try:
        yield
    finally:
        for (kind, method), original in zip(owners, originals, strict=True):
            setattr(kind, method, original)


def bit_actions(tapes):
    return sum(sum(tape.actions.values()) for tape in tapes)


def meter_actions(meter):
    return meter.reads + meter.writes + meter.moves


def literal_radix(m, record, width, buckets):
    for bucket in buckets:
        origin = m.route.RecordTape(m.binary, bucket)
        origin.emit('<')
        origin.move_word(-1)

    tapes = dict(zip(('bad', 'b0', 'b1'), (record.tape, *buckets)))
    before = bit_actions(tapes.values())
    machines = []
    width.step(1)
    while width.read() == '1':
        machine = m.binary.Machine(m.program, len(m.registers), tapes)
        need(machine.run() == 'accept', 'retained binary consumer accepts')
        machines.append(machine)
        width.step(1)
    need(width.read() == 'R', 'encoded radix pass limit')
    width.rewind()
    low_level_radix = bit_actions(tapes.values()) - before
    for bucket in buckets:
        origin = m.route.RecordTape(m.binary, bucket)
        for _ in origin.codes['<']:
            bucket.write(0)
            bucket.move(1)
        origin.move_word(-1)
    return machines, low_level_radix


def run_leg(m, source, payload, reverse):
    """Execute one actual selected leaf. Geometry and destination keys come from tapes."""
    source_before = meter_actions(source.meter)
    borrowed_source = bytes(source.cells), source.head
    payload_before = bit_actions((payload,))
    front = m.reverse if reverse else m.f
    numeric = m.subtractive if reverse else m.numeric
    endpoint = m.writer.Endpoint(front, m.w, m.r, m.e, numeric, m.owner, m.bridge, source)
    it = endpoint.iterator
    numeric_ports = (*it.bank.ports, *it.guards, *it.counters.values(), endpoint.staging)

    headers = {name: m.join.Tape() for name in ('h', 'modulus', 'selected_layer', 'offsets')}
    width, index, address, countdown, row = (m.join.Tape() for _ in range(5))
    service = {name: ['_'] for name in (*m.rom.REGS, 'arena', 'spool', 'layers', 'rom')}
    service.update({name: port.cells for name, port in headers.items()})
    layers, rom = m.join.Tape(service['layers']), m.join.Tape(service['rom'])
    adapter_ports = (*headers.values(), width, index, address, countdown, row, layers, rom)
    record = m.route.RecordTape(m.binary, payload)
    buckets = (m.bit_tape(), m.bit_tape())
    arena_meters = []

    with seal_numerical_roles(m):
        lease = it.next()
        while lease is not None:
            arena_meters.append(lease.actual.context.arena.meter)
            if m.route.selected_leaf(it, lease):
                break
            lease.close()
            lease = it.next()
        need(lease is not None, 'selected physical nonroot leaf')
        borrowed_result = lease.actual.result['stream']
        result_before = bytes(borrowed_result.cells), borrowed_result.head
        m.route.emit_headers(m.join, it, lease, headers, width)
        observed_headers = {name: ''.join(tape.cells) for name, tape in headers.items()}
        observed_headers['width'] = ''.join(width.cells)
        produced = m.rom.execute(m.rom_program, service)
        need(produced['status'] == 'accept' and all(h == 0 for h in produced['heads'].values()),
             'actual encoded ROM production and head return')
        m.route.prepare_keys(m.join, record, layers, width, index, address, countdown, row, reverse)
        machines, radix_tape_actions = literal_radix(m, record, width, buckets)
        need((bytes(source.cells), source.head) == borrowed_source and
             (bytes(borrowed_result.cells), borrowed_result.head) == result_before and
             lease.actual.guide.head == 1 and it.counters['axis'].head == 1 and
             it.counters['half'].head == 1,
             'live source, result and borrowed heads preserved before staging')
        endpoint.stage(lease)
        lease.close()
        endpoint.commit()
        if not it.closed:
            it.close()

    width.erase()
    layers.erase()
    rom.erase()
    for tape in headers.values():
        tape.erase()
    need(all(p.head == 1 and all(c == m.w.BLANK for c in p.cells) for p in numeric_ports),
         'all acquired encoded CRT ports retired')
    need(all(p.head == 0 and all(c == '_' for c in p.cells) for p in adapter_ports)
         and all(all(c == '_' for c in cells) for cells in service.values()),
         'all encoded metadata and ROM histories retired')
    need(all(t.head == 0 and not t.cells for t in buckets) and
         all(machine.status == 'accept' and not any(machine.registers) for machine in machines),
         'all literal bucket and finite control histories retired')
    need(source.head == 1 and payload.head == 0, 'both physical boundary heads returned')

    symbol_cells = [p.cells for p in numeric_ports]
    symbol_cells += [width.cells, index.cells, address.cells, countdown.cells, row.cells]
    symbol_cells += list(service.values())
    need(len({id(cells) for cells in symbol_cells}) == len(symbol_cells),
         'disjoint retained symbol roles')
    receipt = dict(
        direction='inverse' if reverse else 'forward',
        selected_nodes=1,
        skipped_nodes=len(arena_meters) - 1,
        observed_headers=observed_headers,
        encoded_source_symbol_actions=sum(meter_actions(p.meter) for p in (source, *numeric_ports))
        - source_before + sum(meter_actions(meter) for meter in arena_meters),
        adapter_symbol_actions=sum(p.actions for p in adapter_ports),
        benes_instructions=produced['steps'],
        radix_bit_control_instructions=sum(sum(machine.census.values()) for machine in machines),
        radix_passes=len(machines),
        payload_adapter_bit_actions=bit_actions((payload, *buckets)) - payload_before - radix_tape_actions,
        retained_symbol_roles=len(symbol_cells),
        retained_symbol_cells=sum(map(len, symbol_cells)),
        retained_bucket_bits=sum(t.extent for t in buckets),
        retained_radix_register_bits=sum(len(machine.registers) for machine in machines),
        retained_benes_registers=len(produced['registers']),
    )
    return receipt, (symbol_cells, buckets, machines, produced)


def initial_fixture(m):
    # External fixture encoding happens before the measured input boundary.
    case = m.fixture
    source, coordinates = m.e.Port(m.w), []
    for width, modulus, value in zip(case['widths'], case['moduli'], case['initial'], strict=True):
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
        coordinates.append(tuple(cells))
        source.append(m.r.RECORD_END)
    source.append(m.w.RIGHT)
    source.rewind()
    source.cells.extend([m.w.ONE, m.w.ZERO, m.w.BLANK] * 3)

    width = case['widths'][-1]
    need(len(TAGS) == 1 << width and len(set(TAGS)) == len(TAGS) and all(TAGS), 'marked fixture')
    symbols = ['<']
    for position, tag in enumerate(TAGS):
        symbols.extend((('R', tag), *format(position, f'0{width}b')))
    symbols.append('>')
    packet = tuple(bit for symbol in symbols for bit in m.binary.bits(symbol))
    return source, m.bit_tape(packet), coordinates


def coordinates(source, fields):
    return [sum(source.cells[cell] << bit for bit, cell in enumerate(field)) for field in fields]


def observe_payload(tape, width):
    # The observer sees sparse physical bit backing. The runtime above never decodes a key.
    def codeword(position):
        return sum(tape.cells.get(13 * position + bit, 0) << bit for bit in range(13))
    need(codeword(0) == 5, 'observed payload origin')
    observed = []
    at = 1
    while codeword(at) != 6:
        payload = codeword(at)
        need(4096 <= payload < 8192, 'observed opaque code')
        key = 0
        at += 1
        for _ in range(width):
            symbol = codeword(at)
            need(symbol in (2, 3), 'observed key bit')
            key = 2 * key + symbol - 2
            at += 1
        observed.append((key, payload - 4096))
    return observed


def direct_oracle(case):
    start = case['start']
    left, right = case['moduli'][start:start + 2]
    lower = case['initial'][start]
    need(case['level'] == 1 and lower < left, 'oracle for a valid two-axis leaf')
    offset, = [i for i in range(right) if (left * i - lower) % right == 0]
    dest = [(x + offset) % right if x < right else x for x in range(len(TAGS))]
    need(len(set(dest)) == len(TAGS), 'direct CRT permutation')
    return dest, sorted(zip(dest, TAGS, strict=True))


def reverse_order_control(m):
    # Two noncommuting involutions make the control sensitive to row order,
    # since the fixture's modulus-two rotation alone cannot distinguish it.
    def observed(reverse):
        out = []
        for initial in range(4):
            address = m.join.Tape(list('L' + format(initial, '02b')[::-1] + 'R'))
            layers = m.join.Tape(list('L1100|0101|0000|R'))
            width = m.join.Tape(list('L11R'))
            m.route.route_address(m.join, layers, width, address, m.join.Tape(), m.join.Tape(), reverse)
            out.append(sum(int(bit) << i for i, bit in enumerate(address.cells[1:3])))
        return out
    need(observed(False) == [3, 0, 2, 1] and observed(True) == [1, 3, 2, 0],
         'reversed noncommuting row control')
    return 'noncommuting rows distinguish traversal order'


def truncated_layers_control(m):
    try:
        m.route.route_address(m.join, m.join.Tape(list('L1100|R')), m.join.Tape(list('L11R')),
                              m.join.Tape(list('L00R')), m.join.Tape(), m.join.Tape(), False)
    except ValueError as exc:
        need(str(exc) == 'missing descending ROM layers', 'specific truncated-layer rejection')
        return 'truncated width-two layer stream rejected'
    raise ValueError('truncated layer stream accepted')


def replay(m):
    source, payload, fields = initial_fixture(m)
    source_cells, payload_cells = id(source.cells), id(payload.cells)
    source_initial = bytes(source.cells), source.head
    payload_initial = dict(payload.cells), payload.head
    oracle_dest, oracle_forward = direct_oracle(m.fixture)
    forward, first = run_leg(m, source, payload, False)
    observed = observe_payload(payload, m.fixture['widths'][-1])
    need(observed == oracle_forward and oracle_dest != list(range(len(TAGS))),
         'independent nonidentity forward payload placement')
    need(coordinates(source, fields) == m.fixture['forward'], 'retained independent source endpoint')
    coordinate_cells = set().union(*fields)
    need(len(source.cells) == len(source_initial[0]) and
         all(source.cells[i] == bit for i, bit in enumerate(source_initial[0])
             if i not in coordinate_cells), 'source metadata and inaccessible tail unchanged')
    inverse, second = run_leg(m, source, payload, True)
    need((bytes(source.cells), source.head) == source_initial and id(source.cells) == source_cells,
         'actual full source and head restored')
    need((payload.cells, payload.head) == payload_initial and id(payload.cells) == payload_cells,
         'actual full payload frame, keys and head restored')
    all_symbol_cells = [*first[0], *second[0]]
    need(len({id(c) for c in all_symbol_cells}) == len(all_symbol_cells),
         'both directions retain distinct symbol histories')

    expected_headers = {'h': 'L01000R', 'modulus': 'L01000R', 'selected_layer': 'L00000R',
                        'offsets': 'L10000|R', 'width': 'L11R'}
    need(forward['observed_headers'] == inverse['observed_headers'] == expected_headers,
         'same live encoded offset and width in both directions')
    controls = [reverse_order_control(m), truncated_layers_control(m)]
    prior_query = m.join.select_row_bit
    def suppress(*args):
        prior_query(*args)
        return '0'
    try:
        m.join.select_row_bit = suppress
        bad_source, bad_payload, _ = initial_fixture(m)
        run_leg(m, bad_source, bad_payload, False)
        need(observe_payload(bad_payload, m.fixture['widths'][-1]) == list(enumerate(TAGS))
             and list(enumerate(TAGS)) != oracle_forward,
             'no-switch control must fail the forward oracle')
    finally:
        m.join.select_row_bit = prior_query
    controls.append('suppressed switches fail the forward oracle')
    return {
        'status': 'PASS_ENCODED_CRT_LEAF_PAYLOAD',
        'fixture': m.fixture['name'],
        'moduli': m.fixture['moduli'],
        'widths': m.fixture['widths'],
        'input_tags': TAGS,
        'forward_destinations': oracle_dest,
        'forward_tags': [value for _, value in observed],
        'forward_source': m.fixture['forward'],
        'restored_source_and_payload': True,
        'source_cells_retained': len(source.cells),
        'payload_bits_visited': payload.extent,
        'forward_and_inverse': [forward, inverse],
        'control_cases': controls,
        'benes_program_instructions': len(m.rom_program),
        'radix_program_instructions': len(m.program),
    }


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = replay(modules())
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write_result:
        with args.write_result.open('x') as stream:
            stream.write(text)
    else:
        need(text == (HERE / 'RESULT.json').read_text(), 'exact committed payload receipt')
    print(result['status'], 'markers=4 padded=2 forward_and_inverse=2 controls=3')
