"""Execute unchanged PR2250 primitives through segment-relative tape roles."""
import json
import sys
from dataclasses import asdict
from pathlib import Path
from hashlib import sha256

HERE = Path(__file__).resolve().parent
manifest = json.loads((HERE / 'SOURCES.json').read_text())
for item in [row for row in manifest['files'] if 'retained' in row] + manifest['supplied_artifacts']:
    if sha256((HERE / item['retained']).read_bytes()).hexdigest() != item['sha256']:
        raise ValueError('retained source hash')
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'source'))
import streams
import compact
import monomial
from segment import Arena, need


def bind(arena):
    for module in (streams, compact, monomial):
        module.Tape = arena.tape


def direct(raw, layout, word):
    out = bytearray(len(raw))
    for i in range(layout.records):
        j = layout.encode(word.ideal(layout.decode(i), True))
        r = layout.record_bits
        out[j*r:(j+1)*r] = raw[i*r:(i+1)*r]
    return bytes(out)


def exercise(ancestor_length, late):
    meter = streams.Meter()
    ancestors = [bytes((i + j) % 2 for j in range(ancestor_length)) for i in range(Arena.slots)]
    arena = Arena(meter, ancestors)
    bind(arena)
    fields = (('u', 1), ('t', 1)) + ((('y', 2), ('x', 2)) if late else (('x', 2), ('y', 2))) + (('b', 1),)
    layout = compact.Layout(fields, 8)
    word = compact.Compact(1, 1, 1, 0, 'x', 'y', late)
    raw = bytes(b for i in range(layout.records) for b in streams.bit_key(i, 8))
    current = arena.tape(meter, raw)
    current.read(7)
    sibling = arena.tape(meter, bytes((1,0,1,1)))
    sibling.read(2)
    before = [(bytes(t.data), t.head, t.origin) for t in (current, sibling)]
    descriptor = bytes(bit for byte in (HERE / 'BOUNDARY.json').read_bytes() for bit in streams.bit_key(byte, 8))
    with arena.child(descriptor):
        try:
            current.rewind()
        except ValueError as error:
            need(str(error) == 'active local segment', 'suspended parent cannot rewind')
        else:
            raise ValueError('suspended parent was accessible')
        child = arena.tape(meter, raw)
        child.read(11)
        child_before = (bytes(child.data), child.head, child.origin)
        with arena.child(descriptor):
            data = arena.tape(meter, raw)
            result = compact.execute(data, layout, word)
            need(bytes(result.data) == direct(raw, layout, word), 'nested real compact endpoint')
            need(result.head == 0, 'nested compact return head')
            result.erase()
        need((bytes(child.data), child.head, child.origin) == child_before, 'nested parent restored')
        result = compact.execute(child, layout, word)
        need(bytes(result.data) == direct(raw, layout, word), 'real compact endpoint')
        result.erase()
    need([(bytes(t.data), t.head, t.origin) for t in (current, sibling)] == before, 'complete suspended current roles restored')
    for i, prefix in enumerate(ancestors):
        need(bytes(arena.backings[i][:len(prefix)]) == prefix, 'arbitrary dirty ancestor preserved')
    # A source-incompatible global rewind reads ancestor bytes instead of current payload.
    original = ORIGINAL_TAPE(streams.Meter(), ancestors[0] + raw)
    original.head = len(ancestors[0]) + 7
    original.rewind()
    need(original.head != len(ancestors[0]), 'old rewind fails the segment origin contract')
    old_rewind_moves = original.meter.moves
    original.erase()
    need(not original.data and ancestors[0], 'old erase destroys dirty ancestor')
    try:
        current.read(len(raw) + 1)
    except ValueError as error:
        need(str(error) == 'sequential read boundary', 'read rejected at segment boundary')
    else:
        raise ValueError('out-of-segment read admitted')
    need(arena.peak <= Arena.slots, 'fixed role budget')
    return {'ancestor_length': ancestor_length, 'late': late, 'peak_roles': arena.peak,
            'meter': asdict(meter), 'payload_boundary_steps': arena.payload_boundary_steps, 'descriptor_transport_model_steps': arena.descriptor_transport_model_steps, 'old_global_rewind_moves': old_rewind_moves}


def phase_fibre():
    recipe = json.loads((HERE / 'RIGHT-RECIPE.json').read_text())
    meter = streams.Meter()
    arena = Arena(meter, [b'10101'] * Arena.slots)
    bind(arena)
    # Phase preserves every address, so restriction to a declared fibre commutes.
    # The second column is independently enumerated over two values; the first
    # covers all nine-bit values. This is not a complete affine rectangle.
    class Fibre:
        records = 1024
        record_bits = 8
        def decode(self, index):
            x, y = index // 2, index % 2
            return {'v' + str(i): ((x >> i) & 1) | (((y >> i) & 1) << 1) for i in range(9)}
    layout = Fibre()
    raw = bytes(b for i in range(layout.records) for b in streams.bit_key((i * 37 + 19) % 256, 8))
    source = arena.tape(meter, raw)
    output = monomial.phase_pass(source, layout, recipe, 2, 1, 0, 4)
    expected = bytearray()
    for index in range(layout.records):
        x, y = index // 2, index % 2
        phase = 2 * recipe['phase']
        for value in (x, y):
            for i in range(9):
                if value >> i & 1:
                    phase += recipe['linear_Z4'][i]
                    for j in range(i + 1, 9):
                        phase += 2 * ((recipe['quadratic_rows'][i] >> j) & 1) * ((value >> j) & 1)
        real = sum(raw[index*8+i] << i for i in range(4))
        imag = sum(raw[index*8+4+i] << i for i in range(4))
        for _ in range(phase % 4):
            real, imag = -imag, real
        expected.extend(streams.bit_key(real % 16, 4))
        expected.extend(streams.bit_key(imag % 16, 4))
    need(bytes(output.data) == bytes(expected), 'actual source recipe phase on invariant fibre')
    restored = monomial.phase_pass(output, layout, recipe, 2, 1, 0, 4, True)
    need(bytes(restored.data) == raw, 'inverse phase exact restoration')
    for backing in arena.backings:
        need(backing[:5] == b'10101', 'phase dirty ancestor preserved')
    return {'records': 1024, 'f': 2, 'peak_roles': arena.peak, 'meter': asdict(meter),
            'scope': 'Actual event8814 right recipe; phase-invariant address restriction only; K=1 coordinate calibration, no actual packing assertion.'}


def main():
    cases = [exercise(n, late) for late in (False, True) for n in (16, 257, 4096)]
    for start in (0, 3):
        need(all(c['meter'] == cases[start]['meter'] for c in cases[start:start+3]), 'all costs independent of ancestor extent')
        need(all(c['payload_boundary_steps'] == cases[start]['payload_boundary_steps'] for c in cases[start:start+3]), 'payload origin and return costs independent of ancestor extent')
        need(all(c['descriptor_transport_model_steps'] == cases[start]['descriptor_transport_model_steps'] for c in cases[start:start+3]), 'conditional descriptor model independent of ancestor extent')
    result = {'status': 'PASS_SEGMENT_REFINEMENT_CALIBRATION', 'cases': cases, 'actual_phase_fibre': phase_fibre(),
              'scope': 'Unchanged real compact implementation on complete reduced f=2 rectangles; two nested source invocations using a Python control-stack oracle; descriptor charges model known boundaries/lengths, not physical frame implementation; no production rectangle or recursive child implementation.'}
    print(json.dumps(result, indent=2))


ORIGINAL_TAPE = streams.Tape
if __name__ == '__main__':
    main()
