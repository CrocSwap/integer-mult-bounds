"""Independent integer oracles and physical lifecycle checks for the new join.

Observer integers, enumeration and byte snapshots never enter runtime control.
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
from itertools import product
from pathlib import Path
from types import ModuleType
import json
import math
import sys

P = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, relative):
    path = P/relative
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def source_check():
    pins = json.loads((P/'INPUT-PINS.json').read_text())
    for pin in pins:
        raw = (P/'source'/pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == pin['git_blob'], 'source Git blob')
    return len(pins)


def modules():
    root = 'source/research/'
    w = load('words', root+'r437-preparation-composition/predecessor4025/source/words.py')
    r = load('endpoint_records', root+'r437-preparation-composition/predecessor4025/source/records.py')
    e = load('endpoint_entry', root+'encoded-crt-entry-lifecycle/entry.py')
    n = load('endpoint_numeric', root+'encoded-current-crt/producer.py')
    o = load('endpoint_owner', root+'crt-persistent-numerical-owner/owner.py')
    c = load('endpoint_canonical', root+'crt-mixed-row-entry/bridge.py')
    f = load('endpoint_frontend', root+'encoded-balanced-crt-entry/frontend.py')
    return w, r, e, n, o, c, f


def fixture(m, moduli, widths, values, tail=0):
    w, r, e, *_ = m
    source = e.Port(w)
    fields = []
    for s, h, x in zip(moduli, widths, values, strict=True):
        source.append(r.ROOT)
        for _ in range(h):
            source.append(w.ONE)
        source.append(r.WORD_END)
        for value, delimiter in ((s, r.WORD_END), (x, r.RECORD_END)):
            begin = source.head
            for j in range(h):
                source.append((value >> j) & 1)
            if delimiter == r.RECORD_END:
                fields.append(tuple(range(begin, source.head)))
            source.append(delimiter)
    source.append(w.RIGHT)
    source.rewind()
    # Observer-supplied old backing is intentionally not all blank. Runtime
    # stops at RIGHT and must preserve these inaccessible historical cells.
    source.cells.extend((w.ONE, w.ZERO, w.BLANK)[j % 3] for j in range(tail))
    return source, fields


def coordinates(source, fields):
    return tuple(sum(source.cells[at] << j for j, at in enumerate(field))
                 for field in fields)


def node_oracle(moduli, values, start, half):
    """Exhaust defining CRT congruences, independent of the encoded recurrence."""
    left = moduli[start:start+half]
    xs = values[start:start+half]
    total = math.prod(left)
    residues, prefix = [], 1
    for s, x in zip(left, xs):
        residues.append(x*prefix % s)
        prefix *= s
    if all(x < s for x, s in zip(xs, left)):
        lower = next(k for k in range(total)
                     if all(k % s == y for s, y in zip(left, residues)))
    else:
        lower = 0
    answer = list(values)
    prefix = total
    for i in range(start+half, start+2*half):
        s, x = moduli[i], values[i]
        shift = next(c for c in range(s) if (c*prefix-lower) % s == 0)
        answer[i] = (x+shift) % s if x < s else x
        prefix *= s
    return tuple(answer)


def global_oracle(moduli, original):
    """One mixed-radix integer; no tree, reconstruction, or node update."""
    integer, prefix = 0, 1
    for s, x in zip(moduli, original):
        integer += x*prefix
        prefix *= s
    answer, prefix = [], 1
    for s in moduli:
        answer.append(integer*pow(prefix, -1, s) % s)
        prefix *= s
    return tuple(answer)


def poison(module):
    def denied(*_args, **_kwargs):
        raise ValueError('forbidden runtime host geometry/decode')
    for name in ('int', 'float', 'len', 'range', 'sum', 'min', 'max',
                 'enumerate', 'pow', 'sorted', 'zip'):
        module.__dict__[name] = denied


@contextmanager
def sealed(m):
    w, _, e, *_ = m
    old = e.Port.__init__, w.Word.__init__, w.Arena.__init__, w.Word.inspect
    def denied(*_args, **_kwargs):
        raise ValueError('forbidden runtime allocation/decode')
    e.Port.__init__ = w.Word.__init__ = w.Arena.__init__ = w.Word.inspect = denied
    try:
        yield
    finally:
        e.Port.__init__, w.Word.__init__, w.Arena.__init__, w.Word.inspect = old


def actions(ports):
    return sum(p.meter.reads+p.meter.writes+p.meter.moves for p in ports)


def run_case(module, m, moduli, widths, original, tail=0):
    w, r, e, n, o, c, f = m
    source, fields = fixture(m, moduli, widths, original, tail)
    before, source_id = bytes(source.cells), id(source.cells)
    active_cells = set().union(*map(set, fields))
    initial_source_actions = actions([source])
    endpoint = module.Endpoint(f, w, r, e, n, o, c, source)
    it = endpoint.iterator
    ports = (*it.bank.ports, *it.guards, *it.counters.values(), endpoint.staging)
    need(len(ports) == 79 and len({id(p.cells) for p in ports}) == 79, '79 owned roles')
    identities = tuple(id(p.cells) for p in ports)
    expected, meters, trace = tuple(original), [], []
    stage = endpoint.stage
    def observed_stage(lease):
        snapshot = bytes(source.cells), source.head
        stage(lease)
        need((bytes(source.cells), source.head) == snapshot, 'live lease leaves source unchanged')
        need(lease.actual.guide.head == 1 and lease.actual.result['stream'].head == 1,
             'consumed numerical streams restore heads')
        need(it.counters['axis'].head == 1 and it.counters['half'].head == 1,
             'borrowed topology heads restored')
        need(it.counters['width'].head == 1 and
             all(x == w.BLANK for x in it.counters['width'].cells[1:]),
             'reused width counter body blank')
        meters.append(lease.actual.context.arena.meter)
    endpoint.stage = observed_stage
    with sealed(m):
        for level in range(1, len(moduli).bit_length()):
            half = 1 << (level-1)
            for start in range(0, len(moduli), 2*half):
                expected = node_oracle(moduli, expected, start, half)
                need(endpoint.step(), 'every aligned node executes')
                need(coordinates(source, fields) == expected, 'independent node endpoint')
                need(source.head == 1 and id(source.cells) == source_id, 'actual source backing and head')
                need(len(source.cells) == len(before), 'source historical extent unchanged')
                need(all(v == source.cells[i] for i, v in enumerate(before)
                         if i not in active_cells), 'metadata and source tail unchanged')
                need(tuple(id(p.cells) for p in ports) == identities, 'stable owned histories')
                need(not it.live and not it.bank.busy and not endpoint.pending, 'node retirement boundary')
                need(all(p.head == 1 and all(x == w.BLANK for x in p.cells)
                         for p in (*it.bank.ports, *it.guards)), 'numerical bank and guards retired')
                need(all(x == w.BLANK for x in endpoint.staging.cells)
                     and endpoint.staging.head == 1, 'staging fully retired')
                trace.append((level, start, 1+sum(widths[start:start+2*half])))
        need(not endpoint.step() and it.closed, 'exact termination')
    if all(x < s for x, s in zip(original, moduli)):
        need(expected == global_oracle(moduli, original), 'independent global mixed-radix endpoint')
    need(all(p.head == 1 and all(x == w.BLANK for x in p.cells) for p in ports), 'all historical backing blank')
    total = actions([source, *ports])-initial_source_actions
    total += sum(x.reads+x.writes+x.moves for x in meters)
    a, d = sum(widths), len(widths)
    logical = 2+3*a+4*d
    bound = 2**18*(logical+2)**2+4096
    bound += sum(2**20*(precision+2)**4+2**16*(precision+2)**2+4096
                 for _, _, precision in trace)
    need(total <= bound, 'raw source-action envelope')
    pstar = a+1
    inherited = (pstar+1)+2*(2*a+2*d+2)+57*(pstar+2)+3*(d*(pstar+2)+2)
    space = len(before)+inherited+8*(pstar+2)+6*(d+2)+(a+2)+logical
    retained = len(source.cells)+sum(len(p.cells) for p in ports)
    need(retained <= space, 'rolewise historical capacity envelope')
    return {'moduli': list(moduli), 'widths': list(widths), 'input': list(original),
            'output': list(expected), 'nodes': len(trace), 'actions': total,
            'raw_bound': bound, 'retained': retained, 'retained_bound': space,
            'source_tail': tail}


def mutant(text, old, new):
    need(text.count(old) == 1, 'unique mutation site')
    module = ModuleType('endpoint_mutant')
    exec(compile(text.replace(old, new), 'endpoint-mutant', 'exec'), module.__dict__)
    poison(module)
    return module


def controls(module, m):
    w, r, e, n, o, c, f = m
    labels = []
    def rejects(label, operation, message):
        try:
            operation()
        except ValueError as error:
            need(message in str(error), 'specific negative control: '+label)
            labels.append(label)
        else:
            raise ValueError('undetected negative control: '+label)
    source, _ = fixture(m, (3,5), (2,3), (1,1), 29)
    endpoint = module.Endpoint(f, w, r, e, n, o, c, source)
    snapshot = bytes(source.cells), source.head
    lease = endpoint.iterator.next()
    endpoint.stage(lease)
    rejects('write_before_numerical_retirement', endpoint.commit, 'follows numerical retirement')
    need((bytes(source.cells), source.head) == snapshot, 'premature update touches no source')
    rejects('advance_with_uncommitted_staging', endpoint.step, 'must commit')
    lease.close()
    endpoint.commit()
    rejects('recommit_retired_staging', endpoint.commit, 'follows numerical retirement')
    text = (P/'endpoint.py').read_text()
    wrong = mutant(text, 'self.staging.append(new)', 'self.staging.append(old)')
    rejects('stale_original_coordinate', lambda: run_case(wrong, m, (2,3,5,7),
             (2,2,3,3), (1,1,1,1)), 'independent node endpoint')
    dirty = mutant(text, 'self.source.rewind()\n        self.staging.retire()\n        self.pending = False',
                   'self.source.rewind()\n        self.staging.rewind()\n        self.pending = False')
    rejects('retained_staging', lambda: run_case(dirty, m, (3,5), (2,3), (1,1)),
            'staging fully retired')
    late = mutant(text, 'lease.close()\n        self.commit()', 'self.commit()\n        lease.close()')
    rejects('actual_order_mutation', lambda: run_case(late, m, (3,5), (2,3), (1,1)),
            'follows numerical retirement')
    shifted = mutant(text, 'for selected in (False, True):', 'for selected in (True, False):')
    rejects('wrong_half_projection', lambda: run_case(shifted, m, (5,7), (3,3), (1,1)),
            'independent node endpoint')
    source, _ = fixture(m, (3,5), (2,3), (1,1))
    original_source = bytes(source.cells)
    endpoint = module.Endpoint(f, w, r, e, n, o, c, source)
    lease = endpoint.iterator.next()
    # Corrupt the first bit above the destination's h=3 low bits in the
    # P=6 updated field. This tests failure detection, not error rollback.
    lease.actual.result['stream'].cells[6+3+3] = w.ONE
    rejects('nonzero_discarded_high_bit', lambda: endpoint.stage(lease),
            'fits declared width')
    need(bytes(source.cells) == original_source, 'failed projection leaves source bytes')
    return labels


def main():
    authenticated = source_check()
    m = modules()
    module = load('endpoint_join', 'endpoint.py')
    poison(module)
    poison(m[-1])
    cases = [run_case(module, m, (3,5), (2,3), values, tail=17)
             for values in product(range(4), range(8))]
    for values in ((0,0,0,0), (1,2,4,6), (1,1,1,1), (3,2,4,6),
                   (1,3,4,6), (1,2,7,6), (1,2,4,7), (3,3,7,7),
                   (0,2,1,5), (1,0,3,2), (0,0,7,7), (1,1,0,0)):
        cases.append(run_case(module, m, (2,3,5,7), (2,2,3,3), values, tail=31))
    cases.append(run_case(module, m, (3,5,7,11,13,17,19,23),
                 (4,4,4,4,4,5,5,5), (2,4,6,10,12,16,18,22), tail=97))
    result = {'status': 'PASS_ENCODED_BALANCED_CRT_ENDPOINT', 'source_count': authenticated,
              'cases': cases, 'cases_count': len(cases), 'nodes': sum(c['nodes'] for c in cases),
              'owned_roles': 79, 'controls': controls(module, m),
              'runtime_geometry_poisoned': True, 'runtime_constructors_sealed': True,
              'scope': 'source-model forward address-state endpoint; no payload routing',
              'new_kappa': None}
    rendered = json.dumps(result, sort_keys=True, indent=2)+'\n'
    if '--write-result' in sys.argv:
        (P/'RESULT.json').write_text(rendered)
    else:
        need(rendered == (P/'RESULT.json').read_text(), 'frozen exact result')
    print(result['status'], 'cases='+str(len(cases)), 'nodes='+str(result['nodes']),
          'owned_roles=79', 'controls='+str(len(result['controls'])))


if __name__ == '__main__':
    main()
