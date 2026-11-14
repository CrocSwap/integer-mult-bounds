"""Independent sparse review of C7's new arithmetic/contact seams.

Read-only default; no author interpreter, fixture or arithmetic oracle is used.
The unchanged large native positive replay is intentionally not repeated.
Apache-2.0; prepared for @CubeJerry with OpenAI assistance.
"""
from collections import deque
from hashlib import sha1, sha256
from pathlib import Path
import argparse
import gzip
import json
import sys
import types

GAP_SHA = '2062fe2f032732a19f7548c0e966ab05149b98f720eb93cd8b15f67841c6d3d5'
GRAPH_SHA = 'dbe04f2f719bf7c48ce02477871944a6c8ee1a6e1e73c331dc6c06d2de84ace7'
OLD_GRAPH = 'fec60dd4653c6c06846850b2d318d9eec0b7d9856af6b65bae2d336d5c5f99a0'
PROOF_SHA = '1c485c934204b26c30ae551e2cc7a8ebc144d4fd712a506ca501e677c244f6b7'
ALPHABET = set('_01^|$')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def fingerprint(rule):
    return rule.tests, rule.writes, rule.moves, rule.target


def same_primitive(actual, entry, returned, primitive, pentry):
    """Independent rooted graph isomorphism with the required +2 port map."""
    mapping, inverse = {'HALT': returned}, {returned: 'HALT'}
    todo = deque([(pentry, entry)])
    while todo:
        old, new = todo.popleft()
        if old in mapping:
            need(mapping[old] == new, 'ADD target map inconsistency')
            continue
        need(new not in inverse, 'ADD state map is not injective')
        mapping[old], inverse[new] = new, old
        left, right = primitive.rules[old], actual.rules[new]
        need(len(left) == len(right), 'ADD rule count')
        for a, b in zip(left, right):
            for x, y in ((a.tests, b.tests), (a.writes, b.writes), (a.moves, b.moves)):
                need(tuple((t+2, v) for t, v in x) == y, 'ADD exact port/op map')
            todo.append((a.target, b.target))
    return len(mapping)-1


def sources(directory):
    need(sha256((directory/'gap.py').read_bytes()).hexdigest() == GAP_SHA, 'gap.py drift')
    need(sha256((directory/'PROOF.md').read_bytes()).hexdigest() == PROOF_SHA, 'proof drift')
    pins = json.loads((directory/'SOURCE-PINS.json').read_text())
    for pin in pins['files']:
        raw = (directory/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'], 'source size')
        need(sha256(raw).hexdigest() == pin['sha256'], 'source SHA')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['blob'], 'Git blob')
    gap = load(directory/'gap.py', '_independent_C7_source')
    graph, meta = gap.compile_gap()
    old, ometa = gap.predecessor().compile_join()
    need(gap.digest(graph) == GRAPH_SHA and gap.digest(old) == OLD_GRAPH, 'graph hashes')
    need(set(old.rules) <= set(graph.rules), 'old state omission')
    changed = [s for s in old.rules if list(map(fingerprint, old.rules[s])) !=
               list(map(fingerprint, graph.rules[s]))]
    need(set(changed) == {ometa['returns'][28037], ometa['returns'][28039]}, 'old edits')
    for e, nxt in ((28037,28038),(28038,28039),(28039,28040),(28040,28041)):
        r, = graph.rules[meta['returns'][e]]
        need(not r.tests and not r.writes and not r.moves and
             r.target == meta['entries'][nxt], 'chronological return')
    need(graph.start == meta['entries'][28037], 'full prefix start')
    final, = graph.rules[meta['returns'][28041]]
    need(final.target == 'HALT', 'final return')
    new = set(graph.rules)-set(old.rules)
    new_ports = set()
    for s, rows in graph.rules.items():
        for index, rule in enumerate(rows):
            need(rule.target in graph.rules or rule.target == 'HALT', 'undefined target')
            for pairs in (rule.tests, rule.writes, rule.moves):
                need(len(pairs) == len(dict(pairs)), 'duplicate port in operation')
                need(all(0 <= t < 45 for t, _ in pairs), 'out-of-range port')
                if s in new:
                    new_ports.update(t for t, _ in pairs)
            need(all(v in ALPHABET for _, v in rule.tests+rule.writes), 'alphabet')
            need(all(v in (-1,0,1) for _, v in rule.moves), 'non-unit move')
            a = dict(rule.tests)
            for other in rows[:index]:
                b = dict(other.tests)
                need(any(a[t] != b[t] for t in a.keys() & b.keys()), 'overlapping patterns')
    need(new_ports == {3,4,5,6,7,44}, 'new physical footprint')
    _, add, _ = gap.predecessor().lifetime().inputs()
    primitive = add.D.Graph()
    pentry = add.primitive(primitive, 'ADD', 2, 'HALT')
    add_states = []
    for event in (28038,28040):
        stage = meta['new_stages'][event]
        add_states.append(same_primitive(graph, stage['scalar']['entry'], stage['scatter'],
                                         primitive, pentry))
    return gap, graph, meta, {
        'gap_sha256':GAP_SHA, 'graph_sha256':GRAPH_SHA, 'states':len(graph.rules),
        'old_states':len(old.rules), 'new_states':len(new), 'changed_old_states':sorted(changed),
        'new_ports':sorted(new_ports), 'exact_ADD_primitive_states':add_states,
        'retained_source_files_checked':len(pins['files'])}


def source_prefix(directory):
    raw = (directory/'inputs/selected-native.json.gz').read_bytes()
    need(len(raw) == 350722 and sha256(raw).hexdigest() ==
         '2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883', 'source archive')
    source = json.loads(gzip.decompress(raw))
    canonical = sha256(json.dumps(source,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    need(canonical == '91429a6b96729292a8764836e00c87a6f7cd3b76f05159033f4867f69a98d097',
         'canonical source hash')
    expected = [['INIT',1526,601],['ADD',212,449,'1/2',3],['MOVE',1349,3,601,False],
                ['ADD',124,212,'1',3],['ADD',1526,1349,'-1',601]]
    need(source['program'][28037:28042] == expected, 'exact source event range')
    need(source['frames'][3] == [] and source['frames'][601] == [137], 'source frames')
    frame = dict(enumerate(source['initial']))
    for index, event in enumerate(source['program'][:28042]):
        if index == 28037:
            need(1526 not in frame and all(frame[x] == 3 for x in (124,212,449,1349)),
                 'live prefix inputs and inactive owner')
        op, *args = event
        if op == 'ADD':
            target, origin, coefficient, wanted = args
            need(frame.get(target) == wanted and frame.get(origin) == wanted, 'ADD source typing')
        elif op == 'SCALE':
            owner, coefficient, wanted = args
            need(frame.get(owner) == wanted, 'SCALE source typing')
        elif op == 'MOVE':
            owner, previous, wanted, flag = args
            need(frame.get(owner) == previous, 'MOVE source typing')
            frame[owner] = wanted
        elif op == 'INIT':
            owner, wanted = args
            need(owner not in frame, 'INIT live-owner alias')
            frame[owner] = wanted
        else:
            raise ValueError('unreviewed prefix opcode '+op)
    final = {str(x):frame[x] for x in (124,212,449,1349,1526)}
    need(final == {'124':3,'212':3,'449':3,'1349':601,'1526':601}, 'final source frames')
    return {'typed_events':28042,'canonical_sha256':canonical,'final_frames':final,
            'earlier_numerical_execution_claimed':False}


def gamma(n):
    need(type(n) is int and n > 0, 'positive Gamma input')
    bits = bin(n)[2:]
    return '0'*(len(bits)-1)+bits


def packet(values, width, cutoff=1):
    need(len(values) == 1024, 'complete f=r=P=S=1 packet')
    lo, hi = -(1 << (width-1)), (1 << (width-1))-1
    need(all(lo <= x <= hi for x in values), 'signed packet range')
    header = gamma(1)*4+gamma(width)+gamma(cutoff)
    return header+''.join(format(x % (1 << width), '0'+str(width)+'b') for x in values)


class Sparse:
    """Separate sparse simultaneous-transition interpreter with retained history."""
    def __init__(self, fields, width, cutoff=1, donor=None):
        self.origins = [17+t%7 for t in range(45)]
        self.heads = self.origins.copy()
        self.cells = {}
        self.written = set()
        self.steps = 0
        self.low = self.origins.copy()
        self.high = self.origins.copy()
        self.width, self.cutoff = width, cutoff
        self.F = len(fields[0])
        need(len(fields) == 3 and all(len(x) == self.F for x in fields), 'bank geometry')
        for t, origin in enumerate(self.origins):
            self.put(t, origin, '^')
            self.put(t, origin-3, '1')
            self.put(t, origin-2, '|')
        for t in (0,1):
            self.install(t, '0101|$')
            self.heads[t] += 1
        zero = packet([0]*1024, width, cutoff)
        self.install(2, zero+'|$')
        self.install(43, '|'.join([zero if donor is None else donor]+[zero]*4)+'|$')
        self.install(44, '|'.join(fields)+'|$')
        # Previously visited, erased private tails remain charged.
        for t in range(45):
            occupied = [a for (owner,a) in self.cells if owner == t]
            self.low[t], self.high[t] = min(occupied), max(occupied)
        for t in (5,6,7):
            self.low[t] -= 13+t
            self.high[t] += 3+t
        self.entry_low, self.entry_high = self.low.copy(), self.high.copy()
        self.initial_heads, self.initial_cells = self.heads.copy(), self.cells.copy()

    def put(self, tape, address, value):
        if value == '_':
            self.cells.pop((tape,address), None)
        else:
            self.cells[tape,address] = value

    def install(self, tape, text):
        for offset, value in enumerate(text, 1):
            self.put(tape, self.origins[tape]+offset, value)

    def read(self, tape):
        return self.cells.get((tape,self.heads[tape]), '_')

    def touch(self, tape):
        self.low[tape] = min(self.low[tape], self.heads[tape])
        self.high[tape] = max(self.high[tape], self.heads[tape])

    def execute(self, graph, start, stop='HALT', limit=3000000):
        state, before = start, self.steps
        while state != stop:
            need(self.steps-before < limit, 'independent execution limit: '+state)
            rows = []
            for rule in graph.rules.get(state, ()):
                if all(self.read(t) == symbol for t, symbol in rule.tests):
                    rows.append(rule)
            if not rows:
                return {'status':'reject', 'state':state, 'steps':self.steps-before}
            need(len(rows) == 1, 'multiple matching instructions')
            rule, = rows
            for t, _ in rule.tests:
                self.touch(t)
            for t, symbol in rule.writes:
                self.touch(t)
                self.put(t, self.heads[t], symbol)
                self.written.add(t)
            for t, delta in rule.moves:
                self.touch(t)
                self.heads[t] += delta
                self.touch(t)
            self.steps += 1
            state = rule.target
        return {'status':'return', 'state':state, 'steps':self.steps-before}

    def field(self, slot, bank=44):
        start = self.origins[bank]+1+slot*(self.F+1)
        return ''.join(self.cells.get((bank,start+i),'_') for i in range(self.F))

    def new_history(self):
        return sum(b-a-c+d for a,b,c,d in zip(self.low,self.high,self.entry_high,self.entry_low))

    def restored(self, expected_fields):
        need(self.heads == self.initial_heads, 'successful head restoration')
        expected = self.initial_cells.copy()
        for slot, value in enumerate(expected_fields):
            for offset, symbol in enumerate(value):
                expected[44,self.origins[44]+1+slot*(self.F+1)+offset] = symbol
        need(self.cells == expected, 'all public/private/exterior bytes')
        need(self.written <= {3,4,5,6,7,44}, 'new-contact write ownership')


def work_field(cpu, tape):
    return ''.join(cpu.cells.get((tape,cpu.origins[tape]+i),'_') for i in range(1,cpu.F+1))


def contact(cpu, graph, meta, event):
    """Pause/read/resume only; never write any machine state between boundaries."""
    stage = meta['new_stages'][event]
    first = stage['half'].get('entry', stage['scalar']['entry'])
    gather = cpu.execute(graph, meta['entries'][event], first)
    need(gather['status'] == 'return' and gather['steps'] == 14*cpu.F+24, 'two paid gathers')
    half = None
    if event == 28038:
        before = cpu.cells.copy()
        target = work_field(cpu, 4)
        half = cpu.execute(graph, first, stage['scalar']['entry'])
        if half['status'] != 'return':
            return {'status':'reject','part':'half','detail':half}
        need(work_field(cpu,4) == target, 'half changed its target')
        need(all(cpu.cells.get(key,'_') == value for key,value in before.items() if key[0] != 3),
             'half changed another owner or surviving guide')
        need(all(key[0] == 3 or key in before for key in cpu.cells), 'half left a guide')
        need(cpu.heads == cpu.initial_heads, 'half head return')
        need(half['steps'] <= 4096*(cpu.F+1), 'half time envelope')
    scalar = cpu.execute(graph, stage['scalar']['entry'], stage['scatter'])
    if scalar['status'] != 'return':
        return {'status':'reject','part':'ADD','detail':scalar}
    need(scalar['steps'] <= 4096*(cpu.F+1), 'ADD time envelope')
    stop = meta['entries'][28039 if event == 28038 else 28041]
    scatter = cpu.execute(graph, stage['scatter'], stop)
    need(scatter['status'] == 'return' and scatter['steps'] == 9*cpu.F+17,
         'scatter, erase and return tariff')
    return {'status':'return', 'gather_steps':gather['steps'],
            'half_steps':0 if half is None else half['steps'],
            'ADD_steps':scalar['steps'], 'scatter_erase_return_steps':scatter['steps']}


def arithmetic_cases(graph, meta):
    receipts = []
    for width, cutoff in ((2,1),(3,1),(5,1),(9,1),(17,1),(3,1 << 2048)):
        if width == 2:
            A = [0]*1024
            B = [-2 if i%3 == 0 else 0 for i in range(1024)]
            C = [1]*1024
        else:
            A = [1 if i%2 else -1 for i in range(1024)]
            choices = (-(1 << (width-1)), (1 << (width-1))-2, -2, 0, 2)
            B = [choices[i%len(choices)] for i in range(1024)]
            C = [-x for x in A]
        newA = [a+b//2 for a,b in zip(A,B)]
        newC = [c+a for c,a in zip(C,newA)]
        fields = [packet(x,width,cutoff) for x in (C,A,B)]
        cpu = Sparse(fields,width,cutoff)
        first = contact(cpu,graph,meta,28038)
        need(first['status'] == 'return', 'first contact failed')
        cpu.restored([fields[0],packet(newA,width,cutoff),fields[2]])
        # Explicit independent arithmetic seam: the unchanged native MOVE is skipped.
        second = contact(cpu,graph,meta,28040)
        need(second['status'] == 'return', 'second contact failed')
        cpu.restored([packet(newC,width,cutoff),packet(newA,width,cutoff),fields[2]])
        need(cpu.steps <= 12334*cpu.F+12370, 'complete new overhead envelope')
        need(0 <= cpu.new_history() <= 128*(cpu.F+2), 'new-contact historical growth')
        receipts.append({'width':width,'cutoff_bit_length':cutoff.bit_length(),'components':1024,
                         'field_bits':cpu.F,'first':first,'second':second,
                         'total_new_steps':cpu.steps,'history_growth':cpu.new_history()})
    return receipts


def with_rule(graph, state, target):
    replacement = types.SimpleNamespace(rules=graph.rules.copy())
    kind = type(next(r for rows in graph.rules.values() for r in rows))
    replacement.rules[state] = [kind((),(),(),target)]
    return replacement


def controls(gap, graph, meta):
    checks = []
    width = 4
    A, B, C = [2]*1024, [2]*1024, [-1]*1024
    fields = [packet(x,width) for x in (C,A,B)]
    skipped = with_rule(graph,meta['entries'][28038],meta['entries'][28039])
    cpu = Sparse(fields,width)
    need(cpu.execute(skipped,meta['entries'][28038],meta['entries'][28039])['status'] == 'return',
         'skip returning control')
    need(contact(cpu,skipped,meta,28040)['status'] == 'return', 'skip second contact')
    cpu.restored([packet([1]*1024,width),fields[1],fields[2]])
    need(cpu.field(0) != packet([2]*1024,width), 'skipped ADD escaped public oracle')
    checks.append({'control':'returning_skipped_28038','owned_unchanged':True,'public_wrong':True})

    # This literal wrong-source contact consumes unchanged449 (= original212).
    # It returns cleanly while missing the required fresh212 value.
    _, add, _ = gap.predecessor().lifetime().inputs()
    wrong = add.D.Graph()
    wrong_entry, _, _ = gap.new_add(wrong,28040,0,2,'HALT')
    cpu = Sparse(fields,width)
    need(contact(cpu,graph,meta,28038)['status'] == 'return', 'fresh212 preparation')
    result = cpu.execute(wrong,wrong_entry)
    need(result['status'] == 'return', 'stale-value control did not return')
    cpu.restored([packet([1]*1024,width),packet([3]*1024,width),fields[2]])
    need(cpu.field(0) != packet([2]*1024,width), 'stale212 escaped public oracle')
    checks.append({'control':'returning_wrong_source_equal_to_old212','owned_unchanged':True,
                   'public_wrong':True,'steps':result['steps']})

    zero = [0]*1024
    fields = [packet(x,4) for x in (zero,zero,[-2]*1024)]
    mutant = add.D.Graph()
    mentry, _, _ = gap.new_add(mutant,28038,1,2,'HALT',half=True,mutation='zero-fill')
    cpu = Sparse(fields,4)
    result = cpu.execute(mutant,mentry)
    need(result['status'] == 'return', 'zero-fill did not return')
    cpu.restored([fields[0],packet([7]*1024,4),fields[2]])
    need(cpu.field(1) != packet([-1]*1024,4), 'zero-fill escaped exact signed oracle')
    checks.append({'control':'returning_logical_instead_of_arithmetic_shift','steps':result['steps']})

    for name, A, B, C, event in (
        ('last_component_odd',zero,zero[:-1]+[1],zero,28038),
        ('first_ADD_overflow',[7]*1024,[2]*1024,zero,28038),
        ('second_ADD_overflow',[6]*1024,[2]*1024,[1]*1024,28040)):
        fields = [packet(x,4) for x in (C,A,B)]
        cpu = Sparse(fields,4)
        if event == 28040:
            need(contact(cpu,graph,meta,28038)['status'] == 'return', 'prior ADD failed')
        before = [cpu.field(i) for i in range(3)]
        result = cpu.execute(graph,meta['entries'][event],
                             meta['entries'][28039 if event == 28038 else 28041])
        need(result['status'] == 'reject', 'invalid input accepted: '+name)
        need([cpu.field(i) for i in range(3)] == before, 'failed contact changed public bank')
        if event == 28040:
            need(cpu.field(1) == packet([7]*1024,4), 'prior committed ADD was rolled back')
        checks.append({'control':name,'steps':result['steps'],'reject_state':result['state'],
                       'contact_public_unchanged':True})

    fields = [packet(zero,4,3),packet(zero,4,3),packet(zero,4,2)]
    for name, bad_fields in (('unequal_same_length_cutoff_headers',fields),
                             ('short_DATA_hole',[fields[0],fields[1],fields[2][:-1]+'_'])):
        cpu = Sparse(bad_fields,4,3)
        result = cpu.execute(graph,meta['entries'][28038],meta['entries'][28039])
        need(result['status'] == 'reject', 'malformed control accepted')
        need([cpu.field(i) for i in range(3)] == bad_fields, 'malformed public change')
        checks.append({'control':name,'steps':result['steps'],'reject_state':result['state']})
    return checks


def later_move_failure(graph, meta):
    # The exact source endpoint can fit although first D cannot negate MIN.
    width = 6
    A, B, C = [2]*1024,[2]*1024,[-1]*1024
    X = [0]*1024
    native = 129
    packed = int(format(native,'09b')[::-1],2)
    need(packed == 258, 'independent physical axis reversal')
    X[2*packed] = -32
    direct = [0]*1024
    for x in range(512):
        target = int(format(x,'09b')[::-1],2)
        other = int(format(x ^ 137,'09b')[::-1],2)
        sign = -1 if (x & 9).bit_count()%2 else 1
        a,b = X[2*target:2*target+2]
        c,d = (sign*v for v in X[2*other:2*other+2])
        numerators = a-b+c+d, a+b+d-c
        need(all(v%2 == 0 for v in numerators), 'direct source formula exactness')
        direct[2*target:2*target+2] = [v//2 for v in numerators]
    need(max(map(abs,direct)) == 16, 'fitting complete source endpoint')
    need(((native >> 7)&1)*(((native >> 0) ^ (native >> 3))&1) == 1,
         'actual first phase flips native129')
    fields = [packet(x,width) for x in (C,A,B)]
    cpu = Sparse(fields,width,donor=packet(X,width))
    result = cpu.execute(graph,meta['entries'][28038],limit=1500000)
    need(result['status'] == 'reject', 'later MOVE unexpectedly succeeded')
    need(cpu.field(1) == packet([3]*1024,width), 'earlier212 commitment lost')
    need(cpu.field(0) == fields[0] and cpu.field(2) == fields[2], 'unreached ADD changed public')
    need(cpu.field(0,43) == packet(X,width), 'failed MOVE scattered donor')
    need(all(value == cpu.initial_cells[key] for key,value in cpu.cells.items() if key[0] == 2),
         'unreached SUB changed owned result')
    return {'status':'reject_as_required','start':'post-INIT arithmetic entry28038',
            'steps':result['steps'],'reject_state':result['state'],
            'native_nonzero_index':native,'packed_nonzero_index':packed,
            'independent_complete_endpoint_maximum':16,'first_phase_requires':32,
            'public212_committed':True,'full_prefix_rollback_not_claimed':True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package',type=Path)
    parser.add_argument('--write',type=Path,help='optional explicit receipt output')
    args = parser.parse_args()
    gap, graph, meta, static = sources(args.package.resolve())
    result = {'status':'PASS','scope':'new arithmetic seams, static full composition, bounded failure join',
              'static':static,'source_prefix':source_prefix(args.package.resolve()),
              'arithmetic_cases':arithmetic_cases(graph,meta),
              'controls':controls(gap,graph,meta),
              'later_MOVE_failure':later_move_failure(graph,meta),
              'independence':'separate sparse interpreter, Gamma encoder and integer oracle; no author CPU/verifier',
              'not_replayed':'unchanged complete positive native MOVE; preceding INIT; global source caller'}
    text = json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:
        args.write.write_text(text)
    print(text,end='')


if __name__ == '__main__':
    main()
