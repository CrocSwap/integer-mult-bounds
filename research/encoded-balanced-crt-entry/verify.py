"""Actual producer executions; all host decoding below is observer-only."""
from contextlib import contextmanager
from hashlib import sha1, sha256
from pathlib import Path
from types import ModuleType
import json
import math
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def source_check():
    pins = json.loads((P/'SOURCES.json').read_text())['files']
    count = 0
    for pin in pins:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT/pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'source SHA256 '+pin['path'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['git_blob'],
             'source Git blob '+pin['path'])
        count += 1
    return count


def load(name, path):
    m = ModuleType(name)
    m.__file__ = str(path)
    sys.modules[name] = m
    exec(compile(path.read_bytes(), str(path), 'exec'), m.__dict__)
    return m


def modules():
    w = load('words', ROOT/'research/r437-preparation-composition/predecessor4025/source/words.py')
    r = load('records', ROOT/'research/r437-preparation-composition/predecessor4025/source/records.py')
    e = load('entry', ROOT/'research/encoded-crt-entry-lifecycle/entry.py')
    n = load('numeric', ROOT/'research/encoded-current-crt/producer.py')
    o = load('owner', ROOT/'research/crt-persistent-numerical-owner/owner.py')
    c = load('canonical', ROOT/'research/crt-mixed-row-entry/bridge.py')
    return w, r, e, n, o, c


def fixture(w, r, e, moduli, widths, values):
    source = e.Port(w)
    for s, h, x in zip(moduli, widths, values, strict=True):
        source.append(r.ROOT)
        for _ in range(h):
            source.append(w.ONE)
        source.append(r.WORD_END)
        for value, delimiter in ((s, r.WORD_END), (x, r.RECORD_END)):
            for j in range(h):
                source.append((value >> j) & 1)
            source.append(delimiter)
    source.append(w.RIGHT)
    source.rewind()
    return source


def unword(cells, index, delimiter):
    value, bit = 0, 0
    while cells[index] != delimiter:
        need(cells[index] in (0, 1), 'observer binary word')
        value += cells[index] << bit
        bit += 1
        index += 1
    return value, index+1


def records(port, w, r):
    result, at = [], 1
    while port.cells[at] != w.RIGHT:
        need(port.cells[at] == r.ROOT, 'observer record tag')
        first, at = unword(port.cells, at+1, r.WORD_END)
        second, at = unword(port.cells, at, r.WORD_END)
        need(port.cells[at] == r.RECORD_END, 'observer record end')
        at += 1
        result.append([first, second])
    return result


def numeric_oracle(moduli, values, start, half):
    """Independent exhaustive congruence solution, no predecessor arithmetic."""
    left = moduli[start:start+half]
    left_values = values[start:start+half]
    product = math.prod(left)
    if all(x < s for x, s in zip(left_values, left)):
        residues, prefix = [], 1
        for s, x in zip(left, left_values):
            residues.append((x*prefix) % s)
            prefix *= s
        lower = next(k for k in range(product)
                     if all(k % s == residue for s, residue in zip(left, residues)))
    else:
        lower = 0
    result, prefix = [], product
    for s, x in zip(moduli[start+half:start+2*half], values[start+half:start+2*half]):
        offset = next(o for o in range(s) if (o*prefix-lower) % s == 0)
        result.append([offset, (x+offset) % s if x < s else x])
        prefix *= s
    return lower, product, result


def poison(module):
    def denied(*a, **k):
        raise ValueError('forbidden host geometry/decode')
    for name in ('int', 'float', 'len', 'range', 'sum', 'min', 'max', 'enumerate', 'pow', 'sorted'):
        module.__dict__[name] = denied
    return denied


@contextmanager
def sealed(w, e):
    old = e.Port.__init__, w.Word.__init__, w.Arena.__init__, w.Word.inspect
    def denied(*a, **k):
        raise ValueError('forbidden runtime constructor/decode')
    e.Port.__init__ = w.Word.__init__ = w.Arena.__init__ = w.Word.inspect = denied
    try:
        yield
    finally:
        e.Port.__init__, w.Word.__init__, w.Arena.__init__, w.Word.inspect = old


def actions(ports):
    return sum(p.meter.reads+p.meter.writes+p.meter.moves for p in ports)


def check_fixture(f, m, name, moduli, widths, values, source_tail=0):
    w, r, e, n, o, c = m
    source = fixture(w, r, e, moduli, widths, values)
    source.cells.extend([w.BLANK]*source_tail)  # Supplied entry history, outside runtime.
    snapshot = bytes(source.cells), source.head
    before = actions([source])
    it = f.Iterator(w, r, e, n, o, c, source)
    ports = (*it.bank.ports, *it.guards, *it.counters.values())
    need(len(ports) == 78 and len({id(p.cells) for p in ports}) == 78, '78 distinct owned roles')
    identities = tuple(id(p.cells) for p in ports)
    expected = [(level, start, 1 << (level-1))
                for level in range(1, len(widths).bit_length())
                for start in range(0, len(widths), 1 << level)]
    trace, numeral_work, last_lease = [], 0, None
    try:
        with sealed(w, e):
            for level, start, half in expected:
                lease = it.next()
                last_lease = lease
                need(lease is not None, 'every balanced node produced')
                a = lease.actual
                precision = 1+sum(widths[start:start+2*half])
                need(records(a.left, w, r) == [[s, x] for s, x in
                      zip(moduli[start:start+half], values[start:start+half])], 'selected left records')
                need(records(a.right, w, r) == [[s, x] for s, x in
                      zip(moduli[start+half:start+2*half], values[start+half:start+2*half])], 'selected right records')
                need(a.guide.cells[1:precision+1] == bytearray([w.ONE])*precision and
                      (len(a.guide.cells) == precision+1 or a.guide.cells[precision+1] == w.BLANK),
                     'physical current guide extent')
                lower, product, output = numeric_oracle(moduli, values, start, half)
                need(unword(a.result['lower'].cells, 1, w.RIGHT)[0] == lower, 'independent lower congruences')
                need(unword(a.result['product'].cells, 1, w.RIGHT)[0] == product, 'independent left product')
                need(records(a.result['stream'], w, r) == output, 'independent actual numerical output')
                for guard in it.guards:
                    need(guard.cells[:precision+2] == bytearray([w.LEFT]+[w.ZERO]*precision+[w.RIGHT]),
                         'current exact-width protected zeros')
                    need(all(x == w.BLANK for x in guard.cells[precision+2:]), 'blank protected historical tail')
                need((bytes(source.cells), source.head) == snapshot, 'source restored during result handoff')
                lease.close()
                meter = a.context.arena.meter
                numeral_work += meter.reads+meter.writes+meter.moves
                need(tuple(id(p.cells) for p in ports) == identities, 'stable whole-iterator backing')
                need(all(p.head == 1 and all(x == w.BLANK for x in p.cells)
                         for p in (*it.bank.ports, *it.guards)), 'numerical history retired')
                trace.append({'level': level, 'start': start, 'half': half, 'precision': precision,
                              'lower': lower, 'product': product, 'output': output,
                              'retained': [len(p.cells) for p in ports]})
            need(it.next() is None and it.closed, 'exact final rightmost node and termination')
    finally:
        if last_lease is not None and not last_lease.closed:
            last_lease.close()
        if not it.closed and not it.live:
            it.close()
    need((bytes(source.cells), source.head) == snapshot, 'all source bytes and head restored')
    need(all(p.head == 1 and all(x == w.BLANK for x in p.cells) for p in ports), 'all owned history blank')
    total = actions([source, *ports])-before+numeral_work
    length = 2+3*sum(widths)+4*len(widths)
    raw_action_bound = 2**16*(length+2)**2 + sum(2**20*(t['precision']+2)**4 +
             2**16*(t['precision']+2)**2 + 4096 for t in trace) + 4096
    need(total <= raw_action_bound, 'raw local-action envelope calibration')
    return {'name': name, 'moduli': list(moduli), 'widths': list(widths), 'values': list(values),
            'source_length': length, 'source_backing': len(source.cells),
            'trace': trace, 'actions': total, 'raw_action_bound': raw_action_bound,
            'retained_total': len(source.cells)+sum(len(p.cells) for p in ports), 'owned_roles': 78}


def controls(f, m):
    w, r, e, n, o, c = m
    rejected = []
    def rejects(label, fn, message=None):
        try:
            fn()
        except ValueError as error:
            need(message is None or message in str(error), 'specific rejection: '+label)
            rejected.append(label)
        else:
            raise ValueError('undetected negative control: '+label)
    source = fixture(w, r, e, (5,7,3,2), (3,3,2,2), (3,2,1,1))
    snapshot = bytes(source.cells), source.head
    it = f.Iterator(w, r, e, n, o, c, source)
    ports = (*it.bank.ports, *it.guards, *it.counters.values())
    rejects('host_geometry_argument', lambda: it._entry(w, r, None, n, source, it.guards,
             (3,3,2,2), 3, 1, 0, 0), 'no host geometry')
    with sealed(w, e):
        lease = it.next()
        before = actions([source, *ports])
        rejects('live_next', it.next, 'previous node result')
        rejects('live_iterator_close', it.close, 'retired iterator')
        need(actions([source, *ports]) == before, 'live rejection has no tape traffic')
        lease.close()
        # No later next has occurred: this is a current-phase violation,
        # not a claim of physical validation of historical object identities.
        rejects('double_lease_close', lease.close, 'node lease closes once')
        it.close()  # Early close at a retired boundary is paid and complete.
    need((bytes(source.cells), source.head) == snapshot, 'early-close source restoration')
    need(all(p.head == 1 and all(x == w.BLANK for x in p.cells) for p in ports), 'early-close history')
    ports[0].cells[-1] = w.ONE
    rejects('stale_retired_history', lambda: need(all(x == w.BLANK for x in ports[0].cells), 'stale tail'))
    ports[0].cells[-1] = w.BLANK

    malformed = fixture(w, r, e, (2,3,5), (2,2,3), (1,2,4))
    bad_snapshot = bytes(malformed.cells), malformed.head
    captured = []
    original_init = e.Port.__init__
    def capture(port, *args, **kwargs):
        original_init(port, *args, **kwargs)
        captured.append(port)
    before = actions([malformed])
    e.Port.__init__ = capture
    try:
        rejects('nondyadic_shape_with_cleanup', lambda: f.Iterator(w, r, e, n, o, c, malformed),
                'dyadic source axis count')
    finally:
        e.Port.__init__ = original_init
    need(len(captured) == 78, 'rejected preparation fixed inventory')
    need(all(p.head == 1 and all(x == w.BLANK for x in p.cells) for p in captured), 'rejected preparation retires')
    need((bytes(malformed.cells), malformed.head) == bad_snapshot, 'rejected preparation source restoration')
    rejection_actions = actions([malformed, *captured])-before
    need(rejection_actions <= 2**16*(len(malformed.cells)+2)**2, 'rejected preparation allowance')

    mutant = load('wrong_half_frontend', P/'frontend.py')
    poison(mutant)
    mutant.Iterator._double_half = lambda self: None
    rejects('omitted_half_size_doubling', lambda: check_fixture(mutant, m, 'mutant',
             (5,7,3,2), (3,3,2,2), (3,2,1,1)), 'selected left records')
    rejects('typed_receipt_boolean_integer', lambda: need(canonical({'x': True}) == canonical({'x': 1}),
                                                         'typed receipt'))
    return {'rejections': rejected, 'rejected_shape_actions': rejection_actions,
            'early_close_restores': True}


def main():
    source_count = source_check()
    m = modules()
    f = load('encoded_frontend', P/'frontend.py')
    poison(f)
    cases = [check_fixture(f, m, 'changing_half_and_nonzero_start', (5,7,3,2), (3,3,2,2), (3,2,1,1)),
             check_fixture(f, m, 'invalid_left_and_padded_right', (7,3), (3,2), (7,3)),
             check_fixture(f, m, 'wide_declared_axes', (7,5,3,2), (4,4,3,3), (6,4,2,1)),
             check_fixture(f, m, 'eight_axis_tree', (3,5,7,11,13,17,19,23),
                           (4,4,4,4,4,5,5,5), (2,4,6,10,12,16,18,22), source_tail=97)]
    result = {'status': 'PASS_ENCODED_BALANCED_CRT_ENTRY', 'cases': cases,
              'host_geometry_poisoned': True, 'runtime_constructors_sealed': True,
              'cost_scope': 'raw_action_envelope; complete_source_constant_unspecified',
              'lease_scope': 'linear_use_current_lease; historical_host_handles_excluded',
              'full_crt_permutation': False, 'new_kappa': None,
              'source_count': source_count, 'controls': controls(f, m)}
    if '--write-result' in sys.argv:
        (P/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
    else:
        need(canonical(result) == canonical(json.loads((P/'RESULT.json').read_text())), 'frozen typed receipt')
    print(result['status'], 'nodes='+str(sum(len(c['trace']) for c in cases)), 'owned_roles=78',
          'controls='+str(len(result['controls']['rejections'])))


if __name__ == '__main__':
    main()
