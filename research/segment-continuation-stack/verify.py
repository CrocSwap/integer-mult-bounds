"""Exact endpoints, action census, failure controls and retained source exercises."""
import ast
import itertools
import json
import sys
import weakref
from hashlib import sha256
from pathlib import Path
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
kernel = ModuleType('stack')
sys.modules[kernel.__name__] = kernel
exec(compile((HERE / 'stack.py').read_bytes(), str(HERE / 'stack.py'), 'exec'), kernel.__dict__)


def need(value, message):
    if not value:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    sources = {}
    for row in manifest['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(sha256(raw).hexdigest() == row['sha256'], 'source hash: ' + row['path'])
            sources[row['path']] = raw
    return sources


def word(length, seed=0):
    return ''.join(str((i * i + i // 3 + seed) % 2) for i in range(length))


def fixture(parent, heads, descriptor, prefix=0, occupied=None, module=kernel):
    meter = module.Meter()
    payload = [module.Tape(meter, word(prefix, i), row, h)
               for i, (row, h) in enumerate(zip(parent, heads))]
    control = module.Tape(meter, '[u;01:]' * (prefix // 7))
    desc = module.Tape(meter, word(prefix, 1), descriptor)
    reverse = module.Tape(meter, word(prefix, 0))
    mask = (1 << 16) - 1 if occupied is None else occupied
    machine = module.Controller(payload, control, desc, reverse, mask)
    return meter, machine


def snapshot(machine):
    return (tuple(t.snapshot() for t in machine.payload), machine.control.snapshot(),
            machine.descriptor.snapshot(), machine.reverse.snapshot(), machine.occupied)


def install(tape, data, head=0, module=kernel):
    for symbol in data:
        module.emit(tape, symbol)
    module.rewind(tape)
    for _ in range(head):
        tape.move(1)


def exact_actions(d, H, child, child_heads, child_desc, desc_head):
    # Derived from the loops in the written proof, independently of the meter.
    push = 8 * d + 5 * H + 9 * 16 + 13
    cleanup = sum(2 * h + 5 * len(row) + 7 for row, h in zip(child, child_heads))
    cleanup += 2 * desc_head + 5 * len(child_desc) + 7
    pop = 14 * d + 5 * H + 9 * 16 + 16 + cleanup
    return push, pop


def run_case(parent, heads, descriptor, child, child_heads, child_desc='', desc_head=0,
             prefix=0, occupied=None, module=kernel):
    meter, machine = fixture(parent, heads, descriptor, prefix, occupied, module)
    before = snapshot(machine)
    d, H = len(descriptor), sum(len(row) - h for row, h in zip(parent, heads))
    start = meter.total
    machine.push()
    pushed = meter.total - start
    begin = before[1][0]
    frame = ''.join(machine.control._cells[i] for i in range(begin, machine.control._head))
    need(frame == '[' + descriptor + ':' + ''.join(
        str((before[-1] >> i) & 1) + 'u' * (len(row) - h) + ';'
        for i, (row, h) in enumerate(zip(parent, heads))) + ']', 'literal frame grammar')
    need(len(frame) == d + H + 35, 'frame size')
    for tape, row, h in zip(machine.payload, child, child_heads):
        install(tape, row, h, module)
    install(machine.descriptor, child_desc, desc_head, module)
    start = meter.total
    machine.pop()
    popped = meter.total - start
    need(snapshot(machine) == before, 'complete restoration')
    need((pushed, popped) == exact_actions(d, H, child, child_heads, child_desc, desc_head),
         'exact action invoice')
    child_volume = sum(map(len, child)) + len(child_desc)
    bound = module.action_bound(d, H, child_volume)
    need(pushed + popped <= bound, 'complete linear bound')
    for tape in machine.payload + (machine.descriptor, machine.reverse):
        need(min(tape._visited) >= prefix, 'no dirty ancestor traversal')
    need(min(machine.control._visited) >= begin, 'no prior control-frame traversal')
    return {'push': pushed, 'pop': popped, 'bound': bound, 'frame_symbols': len(frame)}


def finite_cases():
    count, largest = 0, 0
    descriptors = [''.join(bits) for n in range(4) for bits in itertools.product('01', repeat=n)]
    for n in range(5):
        for bits in itertools.product('01', repeat=n):
            for h in range(n + 1):
                for desc in descriptors:
                    slot = count % 16
                    parent, heads = [''] * 16, [0] * 16
                    parent[slot], heads[slot] = ''.join(bits), h
                    child = [word((i + count) % 4, i) for i in range(16)]
                    child_heads = [(i + count) % (len(row) + 1) for i, row in enumerate(child)]
                    result = run_case(parent, heads, desc, child, child_heads,
                                      child_desc='100', desc_head=count % 4,
                                      occupied=1 << slot, prefix=count % 4)
                    largest = max(largest, result['push'] + result['pop'])
                    count += 1
    masks = [0, (1 << 16) - 1, 0x5555, 0xAAAA] + [1 << i for i in range(16)]
    for mask in masks:
        run_case([''] * 16, [0] * 16, '', [''] * 16, [0] * 16, occupied=mask)
    return {'complete_single_role_cases': count, 'empty_mask_cases': len(masks),
            'largest_boundary_action_count': largest}


def nested_case(prefix, depth):
    parent = [word(i % 7 + 1, i) for i in range(16)]
    heads = [i % (len(row) + 1) for i, row in enumerate(parent)]
    meter, machine = fixture(parent, heads, word(17, 2), prefix)
    expected = []  # Test oracle only; Controller never receives this list.
    totals = []
    for level in range(depth):
        expected.append(snapshot(machine))
        start = meter.total
        machine.push()
        pushed = meter.total - start
        for i, tape in enumerate(machine.payload):
            row = word((level + i) % 9, i)
            install(tape, row, (i + level) % (len(row) + 1))
        machine.occupied = 0xFFFF
        install(machine.descriptor, word(43 if level % 2 == 0 else 17, level))
        totals.append([pushed, 0])
    for level in reversed(range(depth)):
        start = meter.total
        machine.pop()
        totals[level][1] = meter.total - start
        need(snapshot(machine) == expected[level], 'nested full state restoration')
    return totals


class SourceView:
    """Observer/size facade for unchanged PR2250 source, outside Controller."""
    def __init__(self, role):
        self.role = role
    def __len__(self):
        return self.role.size
    def __bytes__(self):
        r = self.role
        start = r.tape._head - r.head
        return bytes(int(r.tape._cells[start + i]) for i in range(r.size))


class SourceRole:
    """Calibration facade: source integer sizes/handles are not compiled here."""
    def __init__(self, arena, slot, meter):
        self.arena, self.slot, self.meter = arena, slot, meter
        self.tape = arena.machine.payload[slot]
        self.size = self.head = 0
    @property
    def data(self):
        return SourceView(self)
    def read(self, size):
        need(self.arena.active and 0 <= size <= self.size - self.head, 'source read boundary')
        result = bytearray()
        for _ in range(size):
            symbol = self.tape.read()
            need(symbol in kernel.BITS, 'source read bit')
            result.append(int(symbol))
            self.tape.move(1)
        self.head += size
        return result
    def write(self, data):
        need(self.arena.active and self.head == self.size, 'source append boundary')
        for bit in data:
            need(bit in (0, 1), 'source binary payload')
            kernel.emit(self.tape, str(bit))
            self.size += 1
            self.head += 1
    def rewind(self):
        need(self.arena.active, 'source arena active')
        kernel.rewind(self.tape)
        self.head = 0
    def finish(self):
        need(self.head == self.size, 'source complete consumption')
    def erase(self):
        need(self.arena.active, 'source arena active')
        kernel.clear(self.tape)
        self.head = self.size = 0


class SourceArena:
    def __init__(self, machine):
        self.machine, self.active = machine, True
        self.live = [None] * 16
        self.peak = 0
    def release(self, slot):
        if self.active:
            self.machine.occupied &= ~(1 << slot)
    def tape(self, meter, data=b''):
        need(self.active, 'source allocator active')
        slot = next((i for i in range(16) if not (self.machine.occupied >> i) & 1), None)
        need(slot is not None, 'source fixed role inventory')
        need(self.machine.payload[slot].read() == kernel.BLANK, 'source empty allocation')
        self.machine.payload[slot].move(-1)
        need(self.machine.payload[slot].read() == kernel.LEFT, 'source retired role origin')
        self.machine.payload[slot].move(1)
        self.machine.occupied |= 1 << slot
        role = SourceRole(self, slot, meter)
        self.live[slot] = weakref.ref(role, lambda _, i=slot: self.release(i))
        self.peak = max(self.peak, self.machine.occupied.bit_count())
        role.write(data)
        role.rewind()
        return role


def source_cases(sources):
    source = ROOT / 'research/complex-segment-boundary/source'
    for name in ('streams', 'compact', 'monomial'):
        module = ModuleType(name)
        sys.modules[name] = module
        raw = sources['research/complex-segment-boundary/source/' + name + '.py']
        exec(compile(raw, str(source / (name + '.py')), 'exec'), module.__dict__)
    streams, compact, monomial = (sys.modules[name] for name in ('streams', 'compact', 'monomial'))
    boundary = json.loads(sources['research/complex-segment-boundary/BOUNDARY.json'])
    need(boundary['actual_event']['event_index'] == 8814 and
         boundary['actual_event']['family'] == 65689, 'source event binding')
    recipe = json.loads(sources['research/complex-segment-boundary/RIGHT-RECIPE.json'])
    need(recipe['offset'] == 426 and recipe['phase'] == 1, 'source recipe binding')
    results = []
    for late in (False, True):
        for prefix in (16, 257, 4096):
            parent = [word(i + 1, i) for i in range(16)]
            heads = [i // 2 for i in range(16)]
            meter, machine = fixture(parent, heads, word(17), prefix)
            initial = snapshot(machine)
            machine.push()
            first = SourceArena(machine)
            for m in (streams, compact, monomial):
                m.Tape = first.tape
            fields = (('u', 1), ('t', 1)) + ((('y', 2), ('x', 2)) if late else
                                            (('x', 2), ('y', 2))) + (('b', 1),)
            layout = compact.Layout(fields, 8)
            op = compact.Compact(1, 1, 1, 0, 'x', 'y', late)
            raw = bytes(b for i in range(layout.records) for b in streams.bit_key(i, 8))
            expected = bytearray(len(raw))
            for i in range(layout.records):
                j = layout.encode(op.ideal(layout.decode(i), True))
                expected[j*8:(j+1)*8] = raw[i*8:(i+1)*8]
            smeter = streams.Meter()
            current = first.tape(smeter, raw)
            outer = compact.execute(current, layout, op)
            need(bytes(outer.data) == bytes(expected), 'outer retained compact endpoint')
            outer.read(7)
            install(machine.descriptor, word(43, 1))
            saved = snapshot(machine)
            first.active = False
            start = meter.total
            machine.push()
            boundary_actions = meter.total - start
            second = SourceArena(machine)
            for m in (streams, compact, monomial):
                m.Tape = second.tape
            inner = compact.execute(second.tape(smeter, raw), layout, op)
            need(bytes(inner.data) == bytes(expected), 'inner retained compact endpoint')
            second.active = False
            start = meter.total
            machine.pop()
            boundary_actions += meter.total - start
            need(snapshot(machine) == saved, 'source outer roles restored after inner work')
            first.active = True
            need(bytes(outer.data) == bytes(expected) and outer.head == 7, 'source handle calibration')
            first.active = False
            machine.pop()
            need(snapshot(machine) == initial, 'all sixteen parent roles restored')
            results.append({'late': late, 'prefix': prefix, 'records': layout.records,
                            'inner_boundary_actions': boundary_actions,
                            'peak_source_roles': max(first.peak, second.peak)})
    for late in (False, True):
        counts = {r['inner_boundary_actions'] for r in results if r['late'] == late}
        need(len(counts) == 1, 'source boundary independent of dirty prefix length')
    return results


def rejected(action, label):
    try:
        action()
    except ValueError:
        return label
    raise ValueError('control was accepted: ' + label)


def controls():
    outcomes = []
    for label, old, new in [('top', ']', ':'), ('row', ';', ':'), ('descriptor', ':', ';')]:
        _, m = fixture(['1'] * 16, [0] * 16, '100')
        m.push()
        index = max(i for i, c in m.control._cells.items() if c == old)
        m.control._cells[index] = new
        outcomes.append(rejected(m.pop, 'malformed_' + label))
    _, m = fixture([''] * 16, [0] * 16, '100')
    m.push()
    m.control._cells[m.control._head - 3] = 'u'
    outcomes.append(rejected(m.pop, 'excess_return_distance'))
    _, m = fixture(['1'] * 16, [0] * 16, '100', occupied=0)
    outcomes.append(rejected(m.push, 'absent_nonempty_parent'))
    _, m = fixture([''] * 16, [0] * 16, '')
    m.descriptor._cells[m.descriptor._head] = 'u'
    outcomes.append(rejected(m.push, 'nonbinary_descriptor'))
    raw = (HERE / 'stack.py').read_text(encoding='utf-8')
    mutations = [
        ('omitted_head_return', '                tape.move(-1)\n', '                pass\n'),
        ('wrong_descriptor_bit', 'emit(self.descriptor, symbol)',
         "emit(self.descriptor, '1' if symbol == '0' else '0')"),
        ('unpaid_moves', 'self._meter.moves += 1', 'self._meter.moves += 0'),
    ]
    for label, old, new in mutations:
        need(raw.count(old) == 1, 'unique mutation site')
        module = ModuleType('stack_control_' + label)
        sys.modules[module.__name__] = module
        exec(compile(raw.replace(old, new), '<controlled mutation>', 'exec'), module.__dict__)
        outcomes.append(rejected(lambda: run_case(['101'] * 16, [1] * 16, '100',
                                                  ['10'] * 16, [1] * 16,
                                                  child_desc='01', module=module), label))
    return outcomes


def finite_control_surface():
    tree = ast.parse((HERE / 'stack.py').read_text(encoding='utf-8'))
    controller = next(x for x in tree.body if isinstance(x, ast.ClassDef) and x.name == 'Controller')
    for node in ast.walk(controller):
        if isinstance(node, ast.Attribute):
            need(not node.attr.startswith('_'), 'controller cannot inspect simulator state')
        need(not isinstance(node, (ast.ListComp, ast.DictComp)), 'no dynamic frame comprehension')
    need(not any(isinstance(n, ast.Attribute) and n.attr in ('append', 'pop', 'snapshot')
                 for n in ast.walk(controller)), 'no frame list or snapshot oracle')


def main():
    sources = authenticate()
    finite_control_surface()
    finite = finite_cases()
    nested = {str(prefix): nested_case(prefix, 7) for prefix in (16, 257, 4096)}
    need(nested['16'] == nested['257'] == nested['4096'], 'all-depth calibration locality')
    descriptor = ''.join(str((byte >> bit) & 1) for name in ('BOUNDARY.json', 'RIGHT-RECIPE.json')
                         for byte in sources['research/complex-segment-boundary/' + name] for bit in range(8))
    actual_descriptor = run_case(['101'] * 16, [1] * 16, descriptor,
                                 ['10'] * 16, [1] * 16, child_desc=word(43), prefix=257)
    actual_descriptor['descriptor_bits'] = len(descriptor)
    result = {'status': 'PASS_DELIMITED_CONTINUATION_PRIMITIVE', 'source_pins': len(sources),
              'finite': finite, 'seven_level_boundary_counts': nested['16'],
              'retained_descriptor_round_trip': actual_descriptor,
              'actual_compact_calibrations': source_cases(sources), 'rejecting_controls': controls(),
              'physical_tapes': 19, 'alphabet_symbols': 9,
              'scope': 'Primitive theorem and exact finite corroboration; source handles/sizes remain '
                       'a calibration facade; no recursive C, child-output delivery or supplier admission.'}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
