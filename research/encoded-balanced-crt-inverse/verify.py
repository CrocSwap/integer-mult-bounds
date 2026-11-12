"""Source-pinned two-sided inverse tests and independent current-state oracle.

All host integers, lists, decoding and snapshots here are observers. They
never supply a production coordinate, arithmetic result or runtime geometry.
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import contextmanager
from hashlib import sha1, sha256
from itertools import product
from math import prod
from pathlib import Path
from types import ModuleType, SimpleNamespace
import json
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, relative):
    path = HERE/relative
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def authenticate():
    pins = json.loads((HERE/'INPUT-PINS.json').read_text())
    for pin in pins:
        raw = (HERE/pin['export_path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'source SHA256')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == pin['git_blob'], 'source Git blob')
    seam = json.loads((HERE/'SEAMS.json').read_text())['producer']
    base = (HERE/seam['source']).read_bytes()
    before, after = seam['before'].encode(), seam['after'].encode()
    need(base.count(before) == 1, 'unique subtractive producer seam')
    expected = seam['prefix'].encode()+base.replace(before,after)
    need((HERE/'inverse_producer.py').read_bytes() == expected, 'exact one-line specialization')
    return len(pins)


def modules():
    root = 'source/research/'
    w = load('words', root+'r437-preparation-composition/predecessor4025/source/words.py')
    r = load('inverse_records', root+'r437-preparation-composition/predecessor4025/source/records.py')
    e = load('inverse_entry', root+'encoded-crt-entry-lifecycle/entry.py')
    n = load('forward_numeric', root+'encoded-current-crt/producer.py')
    o = load('inverse_owner', root+'crt-persistent-numerical-owner/owner.py')
    c = load('inverse_canonical', root+'crt-mixed-row-entry/bridge.py')
    f = load('base_frontend', root+'encoded-balanced-crt-entry/frontend.py')
    writer = load('unchanged_writer', root+'encoded-balanced-crt-endpoint/endpoint.py')
    inverse = load('inverse_frontend', 'inverse_frontend.py')
    subtractive = load('subtractive_numeric', 'inverse_producer.py')
    oracle = load('pinned_balanced_oracle', root+'unconditional-batched-crt/check_batched_crt.py')
    return SimpleNamespace(w=w, r=r, e=e, n=n, o=o, c=c, f=f, writer=writer,
                           inverse=inverse, subtractive=subtractive, oracle=oracle)


def fixture(m, moduli, widths, values, tail=0):
    source, fields = m.e.Port(m.w), []
    for s, h, x in zip(moduli, widths, values, strict=True):
        source.append(m.r.ROOT)
        for _ in range(h):
            source.append(m.w.ONE)
        source.append(m.r.WORD_END)
        for value, delimiter in ((s,m.r.WORD_END), (x,m.r.RECORD_END)):
            begin = source.head
            for bit in range(h):
                source.append((value >> bit) & 1)
            if delimiter == m.r.RECORD_END:
                fields.append(tuple(range(begin, source.head)))
            source.append(delimiter)
    source.append(m.w.RIGHT)
    source.rewind()
    source.cells.extend((m.w.ONE,m.w.ZERO,m.w.BLANK)[j % 3] for j in range(tail))
    return source, fields


def values(source, fields):
    return tuple(sum(source.cells[at] << j for j, at in enumerate(field))
                 for field in fields)


def node_oracle(moduli, current, start, half, reverse):
    left = moduli[start:start+half]
    xs = current[start:start+half]
    residues, prefix = [], 1
    for s, x in zip(left, xs):
        residues.append(x*prefix % s)
        prefix *= s
    lower = 0
    if all(x < s for x, s in zip(xs, left)):
        lower = next(k for k in range(prod(left))
                     if all(k % s == y for s, y in zip(left, residues)))
    result = list(current)
    for i in range(start+half, start+2*half):
        s, x = moduli[i], current[i]
        offset = next(c for c in range(s) if (prefix*c-lower) % s == 0)
        result[i] = (x-offset if reverse else x+offset) % s if x < s else x
        prefix *= s
    return tuple(result)


def poison(module):
    def denied(*_args, **_kwargs):
        raise ValueError('forbidden host geometry/decode')
    for name in ('int','float','len','range','sum','min','max','enumerate','pow','sorted','zip'):
        module.__dict__[name] = denied


@contextmanager
def sealed(m):
    old = m.e.Port.__init__, m.w.Word.__init__, m.w.Arena.__init__, m.w.Word.inspect
    def denied(*_args, **_kwargs):
        raise ValueError('forbidden new physical role or host decode')
    m.e.Port.__init__ = m.w.Word.__init__ = m.w.Arena.__init__ = m.w.Word.inspect = denied
    try:
        yield
    finally:
        m.e.Port.__init__, m.w.Word.__init__, m.w.Arena.__init__, m.w.Word.inspect = old


def blank(m, ports):
    return all(p.head == 1 and all(x == m.w.BLANK for x in p.cells) for p in ports)


def actions(ports):
    return sum(p.meter.reads+p.meter.writes+p.meter.moves for p in ports)


def owned(endpoint):
    it = endpoint.iterator
    return (*it.bank.ports, *it.guards, *it.counters.values(), endpoint.staging)


def handoff(m, endpoint, lease, precision, half):
    it, w = endpoint.iterator, m.w
    guide = lease.actual.guide
    need(guide.cells[1:precision+1] == bytearray([w.ONE])*precision,
         'exact current precision tokens')
    need(len(guide.cells) == precision+1 or guide.cells[precision+1] == w.BLANK,
         'current precision terminator')
    for port in it.guards:
        need(port.cells[:precision+2] == bytearray([w.LEFT]+[w.ZERO]*precision+[w.RIGHT]),
             'exact current protected width')
        need(all(x == w.BLANK for x in port.cells[precision+2:]), 'blank old protected tail')
    counter = it.counters['half']
    need(counter.cells[:half+2] == bytearray([w.LEFT]+[w.ONE]*half+[w.RIGHT]),
         'actual encoded node half size')
    need(all(x == w.BLANK for x in counter.cells[half+2:]), 'blank old half-size tail')


def bounds(widths, trace, source_capacity, reverse):
    a, d = sum(widths), len(widths)
    length, pstar = 2+3*a+4*d, a+1
    numerical = (pstar+1)+2*(2*a+2*d+2)+57*(pstar+2)+3*(d*(pstar+2)+2)
    space = numerical+8*(pstar+2)+6*(d+2)+(a+2)+length
    cost = 2**19*(length+2)**2+4096
    coefficient = 2**21 if reverse else 2**20
    cost += sum(coefficient*(p+2)**4+2**16*(p+2)**2+4096 for p in trace)
    return cost, source_capacity+space


def run_direction(m, source, fields, moduli, widths, reverse,
                  frontend=None, numeric=None):
    initial = values(source, fields)
    snapshot, source_id = bytes(source.cells), id(source.cells)
    changed = set().union(*map(set, fields))
    before = actions([source])
    front = frontend or (m.inverse.bind(m.f) if reverse else m.f)
    producer = numeric or (m.subtractive if reverse else m.n)
    endpoint = m.writer.Endpoint(front,m.w,m.r,m.e,producer,m.o,m.c,source)
    ports = owned(endpoint)
    identities = tuple(id(p.cells) for p in ports)
    need(len(ports) == 79 and len(set(identities)) == 79, '79 fixed owned roles')
    stage, meters, precisions = endpoint.stage, [], []
    historical_lengths = [len(p.cells) for p in ports]
    expected_precision = expected_half = None
    def observed_stage(lease):
        handoff(m,endpoint,lease,expected_precision,expected_half)
        before_stage = bytes(source.cells), source.head
        stage(lease)
        need((bytes(source.cells),source.head) == before_stage, 'read-only numerical lease')
        need(lease.actual.guide.head == 1 and lease.actual.result['stream'].head == 1,
             'consumed result heads returned')
        need(endpoint.iterator.counters['axis'].head == 1 and
             endpoint.iterator.counters['half'].head == 1, 'topology heads returned')
        for i, port in enumerate(ports):
            historical_lengths[i] = max(historical_lengths[i],len(port.cells))
        meters.append(lease.actual.context.arena.meter)
    endpoint.stage = observed_stage
    levels = tuple(range(1,len(moduli).bit_length()))
    current = initial
    with sealed(m):
        for level in reversed(levels) if reverse else levels:
            expected_half = 1 << (level-1)
            for start in range(0,len(moduli),2*expected_half):
                expected_precision = 1+sum(widths[start:start+2*expected_half])
                current = node_oracle(moduli,current,start,expected_half,reverse)
                need(endpoint.step(), 'every current node executes')
                need(values(source,fields) == current, 'independent current-node endpoint')
                need(source.head == 1 and id(source.cells) == source_id,
                     'actual source and head restored')
                need(len(source.cells) == len(snapshot) and
                     all(source.cells[i] == x for i,x in enumerate(snapshot) if i not in changed),
                     'metadata and old source tail preserved')
                need(tuple(id(p.cells) for p in ports) == identities, 'stable complete history')
                need(all(len(p.cells) >= size for p,size in zip(ports,historical_lengths)),
                     'retained histories never shortened')
                it = endpoint.iterator
                need(blank(m,(*it.bank.ports,*it.guards,endpoint.staging)),
                     'all current numerical/staging histories retired')
                precisions.append(expected_precision)
        need(not endpoint.step() and endpoint.iterator.closed, 'exact inverse termination')
    need(current == m.oracle.balanced(initial,moduli,reverse=reverse), 'pinned full endpoint')
    need(blank(m,ports), 'all 79 role histories blank')
    work = actions([source,*ports])-before+sum(x.reads+x.writes+x.moves for x in meters)
    time_bound, space_bound = bounds(widths,precisions,len(snapshot),reverse)
    retained = len(source.cells)+sum(len(p.cells) for p in ports)
    need(work <= time_bound and retained <= space_bound, 'complete source envelopes')
    return endpoint, {'reverse':reverse, 'precisions':precisions,'actions':work,
                      'raw_bound':time_bound,'retained':retained,'retained_bound':space_bound}


def round_trip(m, moduli, widths, original, tail):
    result = []
    for first_reverse in (False,True):
        source, fields = fixture(m,moduli,widths,original,tail)
        snapshot = bytes(source.cells), source.head
        first, one = run_direction(m,source,fields,moduli,widths,first_reverse)
        second, two = run_direction(m,source,fields,moduli,widths,not first_reverse)
        histories = (*owned(first),*owned(second))
        need(len(histories) == 158 and len({id(p.cells) for p in histories}) == 158,
             'two fresh invocations retain all 158 distinct histories')
        need(blank(m,histories) and (bytes(source.cells),source.head) == snapshot,
             'two-sided exact full-source restoration')
        joint = len(source.cells)+sum(len(p.cells) for p in histories)
        bound = one['retained_bound']+two['retained_bound']-len(source.cells)
        need(joint <= bound, 'both retained inventories charged')
        result.append({'first_reverse':first_reverse,'calls':[one,two],
                       'joint_retained':joint,'joint_bound':bound,'owned_roles':158})
    return {'moduli':list(moduli),'widths':list(widths),'input':list(original),
            'source_tail':tail,'round_trips':result}


def inverse_case(m, original=(0,1,2,1), frontend=None, numeric=None):
    moduli, widths = (2,3,5,7), (2,2,3,3)
    source, fields = fixture(m,moduli,widths,original,29)
    answer = run_direction(m,source,fields,moduli,widths,True,frontend,numeric)
    return source, fields, answer


def stale_provider(m):
    """Bounded fault: third call rereads the old right-child left value 2.

    The real caller has restored that value to zero at the root. Only the
    lower descriptor bit is temporarily altered; actual encoded arithmetic
    then runs and the borrowed descriptor is restored. No production hook
    or numerical replacement oracle is introduced.
    """
    calls = 0
    def produce(arena, left, right, words, records):
        nonlocal calls
        calls += 1
        if calls != 3:
            return m.subtractive.produce(arena,left,right,words,records)
        for _ in range(10):
            left.step(1)
        old = left.read()
        need(old == words.ZERO, 'fixture actual current-left bit is zero')
        left.write(words.ONE)
        left.rewind()
        result = m.subtractive.produce(arena,left,right,words,records)
        for _ in range(10):
            left.step(1)
        left.write(old)
        left.rewind()
        return result
    return SimpleNamespace(produce=produce)


def bad_guards(m, dirty_tail):
    base = m.inverse.bind(m.f).Iterator
    class Iterator(base):
        count = 0
        def _prepare_guards(self, guide):
            super()._prepare_guards(guide)
            self.count += 1
            if self.count != 2:
                return
            port = self.guards[0]
            if dirty_tail:
                for _ in range(11):
                    port.step(1)
                port.write(self.w.ONE)
            else:
                for _ in range(5):
                    port.step(1)
                for _ in range(6):
                    port.write(self.w.ZERO)
                    port.step(1)
                port.write(self.w.RIGHT)
            port.rewind()
    return SimpleNamespace(Iterator=Iterator)


def controls(m):
    labels = []
    def rejects(label, operation, message):
        try:
            operation()
        except ValueError as error:
            need(message in str(error), 'specific rejection for '+label+': '+str(error))
            labels.append(label)
        else:
            raise ValueError('undetected negative control: '+label)
    rejects('forward_level_order_with_subtraction',
            lambda: inverse_case(m,frontend=m.f), 'exact current precision tokens')
    rejects('addition_in_inverse_nodes', lambda: inverse_case(m,numeric=m.n),
            'independent current-node endpoint')
    rejects('stale_current_left_from_before_root',
            lambda: inverse_case(m,numeric=stale_provider(m)), 'independent current-node endpoint')
    rejects('old_root_precision_reused_at_smaller_child',
            lambda: inverse_case(m,frontend=bad_guards(m,False)), 'exact current protected width')
    rejects('nonblank_old_tail_past_shorter_current_guard',
            lambda: inverse_case(m,frontend=bad_guards(m,True)), 'blank old protected tail')
    base = m.inverse.bind(m.f).Iterator
    class FreshRole(base):
        def _double_half(self):
            self.e.Port(self.w)
            super()._double_half()
    rejects('hidden_new_role_at_reverse_level_transition',
            lambda: inverse_case(m,frontend=SimpleNamespace(Iterator=FreshRole)),
            'forbidden new physical role')
    class Doubled(base):
        def _double_half(self):
            m.f.Iterator._double_half(self)
    rejects('doubling_instead_of_reverse_halving',
            lambda: inverse_case(m,frontend=SimpleNamespace(Iterator=Doubled)),
            'complete selected node')
    class Shortened(base):
        def _double_half(self):
            super()._double_half()
            self.counters['half'].cells.pop()
    rejects('silently_shortened_historical_backing',
            lambda: inverse_case(m,frontend=SimpleNamespace(Iterator=Shortened)),
            'retained histories never shortened')
    wrong = SimpleNamespace(produce=lambda a,l,r,w,rec:
             m.subtractive.produce(a,l,r,w,rec,fault='treat_current_as_original'))
    rejects('current_child_misread_as_original_digits',
            lambda: inverse_case(m,(1,1,1,1),numeric=wrong), 'independent current-node endpoint')
    source, fields, _ = inverse_case(m,(1,3,1,1))
    need(values(source,fields) == (1,3,1,5), 'actual globally invalid inverse witness')
    rejects('global_invalid_identity_shortcut',
            lambda: need(values(source,fields) == (1,3,1,1),'invalid rectangle is not pointwise fixed'),
            'not pointwise fixed')
    source, fields = fixture(m,(2,3,5,7),(2,2,3,3),(0,1,2,1))
    endpoint = m.writer.Endpoint(m.inverse.bind(m.f),m.w,m.r,m.e,m.subtractive,m.o,m.c,source)
    before = bytes(source.cells), source.head
    lease = endpoint.iterator.next()
    endpoint.stage(lease)
    rejects('source_write_before_inverse_result_retirement',endpoint.commit,
            'follows numerical retirement')
    need((bytes(source.cells),source.head) == before, 'rejected write preserves source')
    lease.close()
    endpoint.commit()
    endpoint.iterator.close()
    need(blank(m,owned(endpoint)), 'paid early-close cleanup')
    return labels


def complete_run_driver(m):
    source, fields = fixture(m,(2,3,5,7),(2,2,3,3),(0,1,2,1),47)
    calls = 0
    def observed_produce(*args):
        nonlocal calls
        calls += 1
        return m.subtractive.produce(*args)
    endpoint = m.writer.Endpoint(m.inverse.bind(m.f),m.w,m.r,m.e,
               SimpleNamespace(produce=observed_produce),m.o,m.c,source)
    with sealed(m):
        endpoint.run()  # No verifier-supplied iteration count or schedule.
    need(calls == 3 and values(source,fields) == (0,1,0,0), 'complete encoded run driver')
    need(source.head == 1 and blank(m,owned(endpoint)), 'complete run ownership')
    return {'actual_numerical_nodes':calls,'owned_roles':79,
            'verifier_schedule_supplied':False,'output':list(values(source,fields))}


def main():
    count = authenticate()
    m = modules()
    for module in (m.f,m.writer,m.inverse):
        poison(module)
    cases = [round_trip(m,(3,5),(2,3),x,17) for x in product(range(4),range(8))]
    four = ((0,0,0,0),(1,2,4,6),(1,1,1,1),(3,2,4,6),(1,3,4,6),
            (1,2,7,6),(1,2,4,7),(3,3,7,7),(0,2,1,5),(1,0,3,2),
            (0,0,7,7),(1,1,0,0),(0,1,0,0),(0,1,2,1),(1,3,1,1))
    cases += [round_trip(m,(2,3,5,7),(2,2,3,3),x,31) for x in four]
    cases += [round_trip(m,(4,9),(3,4),x,23)
              for x in ((3,8),(7,15),(4,1),(1,9))]
    for x in ((2,4,6,10,12,16,18,22),(7,4,6,10,12,16,18,31)):
        cases.append(round_trip(m,(3,5,7,11,13,17,19,23),
                                (4,4,4,4,4,5,5,5),x,97))
    result = {'status':'PASS_ENCODED_BALANCED_CRT_INVERSE','source_count':count,
              'cases':cases,'cases_count':len(cases),'owned_roles_per_invocation':79,
              'owned_roles_per_fresh_round_trip':158,
              'actual_numerical_nodes':sum(len(call['precisions']) for case in cases
                 for trip in case['round_trips'] for call in trip['calls']),
              'controls':controls(m),'complete_run_driver':complete_run_driver(m),'new_kappa':None,
              'scope':'one balanced address-state inverse; no payload or raw compact inverse'}
    rendered = json.dumps(result,sort_keys=True,indent=2)+'\n'
    if '--write-result' in sys.argv:
        (HERE/'RESULT.json').write_text(rendered)
    else:
        need(rendered == (HERE/'RESULT.json').read_text(), 'frozen exact receipt')
    print(result['status'],'cases='+str(len(cases)),
          'nodes='+str(result['actual_numerical_nodes']),
          'roles=79/158','controls='+str(len(result['controls'])))


if __name__ == '__main__':
    main()
