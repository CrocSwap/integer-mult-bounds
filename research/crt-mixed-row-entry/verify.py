"""Check the actual CRT entry and the mixed-width row contract.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import types

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def modules():
    for row in json.loads((P / 'SOURCES.json').read_text())['files']:
        if row['usage'] == 'input':
            raw = (ROOT / row['path']).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256')
    base = ROOT / 'research/r437-preparation-composition/predecessor4025/source'
    return (load('words', base / 'words.py'), load('records', base / 'records.py'),
            load('entry', ROOT / 'research/encoded-crt-entry-lifecycle/entry.py'),
            load('producer', ROOT / 'research/encoded-current-crt/producer.py'),
            load('caller', ROOT / 'research/crt-mixed-width-caller/verify.py'),
            load('crt', ROOT / 'research/unconditional-batched-crt/check_batched_crt.py'),
            load('bridge', P / 'bridge.py'))


def port(w, e, data):
    p = e.Port(w)
    for symbol in data:
        p.append(symbol)
    p.rewind()
    return p


def bits(value, width):
    return [(value >> i) & 1 for i in range(width)]


def axis_stream(w, r, e, moduli, widths, state):
    data = []
    for q, h, x in zip(moduli, widths, state):
        data += [r.ROOT] + [w.ONE] * h + [r.WORD_END]
        data += bits(q, h) + [r.WORD_END] + bits(x, h) + [r.RECORD_END]
    return port(w, e, data + [w.RIGHT])


def snapshot(ports):
    return [(bytes(p.cells), p.head) for p in ports]


def traffic(ports):
    return sum(p.meter.reads + p.meter.writes + p.meter.moves for p in ports)


def read_result(result, width, w, r):
    def word(x):
        return sum(b << i for i, b in enumerate(x.cells[1:-1]))
    raw = result['stream'].cells
    at, rows = 1, []
    while raw[at] != w.RIGHT:
        need(raw[at] == r.ROOT, 'output root')
        at += 1
        fields = []
        for _ in range(2):
            fields.append(sum(raw[at + i] << i for i in range(width)))
            at += width
            need(raw[at] == r.WORD_END, 'output field delimiter')
            at += 1
        need(raw[at] == r.RECORD_END, 'output record delimiter')
        at += 1
        rows.append(fields)
    return word(result['lower']), word(result['product']), rows


def case(mod, moduli, widths, ell, state, level, start, row):
    w, r, e, producer, c, ref, b = mod
    caller = c.Caller(moduli, widths, ell, ref)
    caller.state(state)
    size = 1 << level
    middle, stop = start + size // 2, start + size
    width = 1 + sum(widths[start:stop])
    source = axis_stream(w, r, e, moduli, widths, state)
    dirty = [port(w, e, bits(3 * i + 1, width) + [w.RIGHT]) for i in range(8)]
    for i, p in enumerate(dirty):
        for _ in range(i % 3):
            p.step(1)
    borrowed = [source, *dirty]
    before, initial = snapshot(borrowed), traffic(borrowed)
    actual = b.RowEntry(w, r, e, producer, source, dirty, widths, ell, level, start, row)
    active = [axis for axis in range(middle, stop)
              if c.local_row(widths[axis], ell, row) is not None]
    need(list(actual.active) == active, 'literal active-axis set')
    if not active:
        need(actual.context is None and actual.result is None, 'idle has no numerical call')
        actual.close()
        need(snapshot(borrowed) == before and traffic(borrowed) == initial, 'idle has no tape work')
        return dict(idle=True, level=level, start=start, row=row)
    lower, product, rows = read_result(actual.result, width, w, r)
    valid = all(state[i] < moduli[i] for i in range(start, middle))
    expected_lower = ref.decode_group(state[start:middle], moduli[start:middle]) if valid else 0
    need(lower == expected_lower and product == math.prod(moduli[start:middle]), 'current child reconstruction')
    need(actual.result['left_valid'] == valid, 'left validity')
    offsets = caller.offsets(state, level)
    for axis, (offset, value) in zip(range(middle, stop), rows):
        need(offset == offsets[axis], 'actual Caller.offsets')
        need(value == ((state[axis] + offset) % moduli[axis]
                       if state[axis] < moduli[axis] else state[axis]), 'whole-rotation value')
    given = dict(offsets)
    given.update({axis: entry[0] for axis, entry in zip(range(middle, stop), rows)})
    need(caller.row(state, level, row, given) == caller.row(state, level, row), 'actual row query')
    owned = [*actual.inputs, *actual.context.owned]
    numerical = actual.context.arena.meter
    actual.close()
    need(snapshot(borrowed) == before, 'borrowed bytes and heads')
    need(all(p.head == 1 and all(x == w.BLANK for x in p.cells) for p in owned), 'all owned backing erased')
    length = 2 + sum(3 * h + 4 for h in widths)
    n = size
    bound = 57 * (width + 2) + 3 * (width - 2) * (2 * width + 4) + 6 + 3 * width + 4 * n + 4
    retained = sum(len(p.cells) for p in owned)
    need(retained <= bound, 'complete owned backing grant')
    measured = traffic(borrowed + owned) - initial + numerical.reads + numerical.writes + numerical.moves
    time_bound = 2**20 * (width + 2)**4 + 2**16 * (width + 2)**2 + 128 * (length + width + n + 1)
    need(measured <= time_bound, 'complete source-operation grant')
    return dict(idle=False, state=list(state), level=level, start=start, row=row,
                precision=width, active=active, lower=lower, product=product, values=rows,
                traffic=measured, time_bound=time_bound, owned_backing=retained, backing_bound=bound)


def rejects(fn, name):
    try:
        fn()
    except ValueError:
        return name
    raise ValueError('control accepted: ' + name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write-result', action='store_true')
    args = ap.parse_args()
    mod = modules()
    w, r, e, producer, c, ref, b = mod
    widths, moduli = (3, 3, 4, 4), (5, 7, 11, 13)
    records = []
    caller = c.Caller(moduli, widths, 4, ref)
    def inspect(state, level, row, specs):
        for start in range(0, 4, 1 << level):
            records.append(case(mod, moduli, widths, 4, state, level, start, row))
    endpoint = caller.run((1, 2, 0, 9), inspect=inspect)
    need(endpoint == ref.balanced((1, 2, 0, 9), moduli), 'full actual trace endpoint')
    for state in ((1, 5, 0, 9), (5, 5, 11, 15), (0, 0, 15, 14), (7, 7, 0, 9)):
        records.append(case(mod, moduli, widths, 4, state, 2, 0, 0))
    records.append(case(mod, (3, 5), (3, 3), 3, (7, 5), 1, 0, 0))
    records.append(case(mod, (3, 5), (2, 3), 3, (1, 1), 1, 0, 3))
    discriminator = next(x for x in records if x.get('state') == [1, 5, 0, 9] and x['level'] == 2)
    need(discriminator['lower'] == 11 and discriminator['values'] == [[0, 0], [3, 12]], 'right-prefix discriminator')
    controls = []
    original = producer.produce
    for fault in ('treat_current_as_original', 'omit_right_prefix', 'rotate_padding'):
        producer.produce = lambda *a, f=fault: original(*a, fault=f)
        controls.append(rejects(lambda: case(mod, moduli, widths, 4, (1, 5, 11, 15), 2, 0, 0), fault))
    producer.produce = original
    for fn, name in ((lambda: case(mod, moduli, widths, 4, (1, 5, 0, 9), 2, 1, 0), 'unaligned node'),
                     (lambda: case(mod, moduli, widths, 4, (1, 5, 0, 9), 2, 0, 7), 'row outside schedule')):
        controls.append(rejects(fn, name))
    # The source has a padded intermediate target on a valid whole-level path.
    small = c.Caller((7, 3), (3, 2), 3, ref)
    state, wrong = (1, 1), (1, 1)
    offsets = small.offsets(state, 1)
    for row in range(5):
        state = small.apply(state, small.row(state, 1, row, offsets))
        wrong = small.apply(wrong, small.row(wrong, 1, row, offsets, True))
    need(state == (1, 2) and wrong == (1, 3), 'target-validity gating rejected')
    controls.append('target-validity gate changes actual endpoint')
    result = dict(status='PASS_ACTUAL_CRT_ROW_ENTRY', cases=records, endpoint=list(endpoint), controls=controls,
                  bridge_sha256=hashlib.sha256((P / 'bridge.py').read_bytes()).hexdigest())
    encoded = json.dumps(result, sort_keys=True)
    if args.write_result:
        (P / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(encoded == json.dumps(json.loads((P / 'RESULT.json').read_text()), sort_keys=True), 'typed complete receipt')
    print(json.dumps(dict(status=result['status'], cases=len(records), controls=len(controls), idle=sum(x['idle'] for x in records))))


if __name__ == '__main__':
    main()
