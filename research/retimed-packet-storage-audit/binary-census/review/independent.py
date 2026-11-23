#!/usr/bin/env python3
"""Independent finite census and exact source-calendar ownership review.

Does not read or import the author's checker. A retained source Plan is used
only as the implementation under test against a separately enumerated calendar.
"""
import ast
from collections import Counter, defaultdict
from contextlib import contextmanager
from dataclasses import dataclass
from hashlib import sha256
import gzip
import inspect
from io import BytesIO
from itertools import product
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parent
AUTHOR = ROOT.parent / 'work-binary-owner-census'
if not AUTHOR.exists():
    AUTHOR = ROOT.parent
SRC = AUTHOR / 'sources'

def need(ok, reason):
    if not ok:
        raise ArithmeticError(reason)

def rejected(fn):
    try:
        fn()
    except (ArithmeticError, ValueError, KeyError, StopIteration):
        return True
    return False

def load_sources():
    bindings = json.loads((AUTHOR / 'SOURCE-BINDINGS.json').read_text())
    for name, spec in bindings['files'].items():
        raw = (SRC / name).read_bytes()
        need(len(raw) == spec['size'] and sha256(raw).hexdigest() == spec['sha256'], name)
    graph = json.loads((SRC / 'graph.json').read_text())
    caller = json.loads((SRC / 'caller.json').read_text())
    need(graph == json.loads(gzip.decompress((SRC / 'strong-bit.json.gz').read_bytes())), 'graph decode')
    need(caller == json.loads(gzip.decompress((SRC / 'binary-caller.gz').read_bytes())), 'caller decode')
    return bindings, graph, caller

def trace_graph(graph, program=None):
    live = set(range(graph['public']))
    peak = cuts_peak = 0
    peak_site = last_cut = None
    counts = Counter()
    for site, row in enumerate(graph['program'] if program is None else program):
        op, dest, *args = row
        counts[op] += 1
        if op == 'INIT':
            need(dest not in live and dest >= graph['public'], 'invalid INIT')
            live.add(dest)
        else:
            need(dest in live, 'dead destination')
            if op in ('ADD', 'SWAP'):
                need(args[0] in live, 'dead source')
            elif op == 'CLEAR':
                need(dest >= graph['public'], 'public CLEAR')
                live.remove(dest)
            elif op == 'MOVE':
                cuts_peak = max(cuts_peak, len(live) - graph['public'])
                last_cut = site
            else:
                raise ArithmeticError('unknown opcode')
        if len(live) - graph['public'] > peak:
            peak, peak_site = len(live) - graph['public'], site
    need(live == set(range(graph['public'])), 'private leak')
    return dict(counts), peak, cuts_peak, peak_site, last_cut

def census(graph, caller):
    counts, peak, cut_peak, peak_site, last_cut = trace_graph(graph)
    root = Counter(row[0] for row in caller['events'])
    ports = caller['ports']
    targets = len(caller['diagonal']) * ports + root['LOCAL'] * (graph['public'] - 2 * ports)
    paid = root['LOCAL'] * counts['MOVE'] + (root['QUERY'] + root['IDLE_ONE']) * ports
    need((targets, paid, peak, cut_peak) == (18906, 104904, 3433, 2803), 'fixed census')
    last_branch = [(i, row) for i, row in enumerate(caller['events']) if row[0] in ('LOCAL','QUERY','IDLE_ONE')][-1]
    need(last_branch[1][0] == 'LOCAL' and peak_site > last_cut, 'closing tail witness')
    bad = [list(row) for row in graph['program']]
    bad.pop(next(i for i, row in enumerate(bad) if row[0] == 'CLEAR'))
    need(rejected(lambda: trace_graph(graph, bad)), 'missing CLEAR control')
    bad = [list(row) for row in graph['program']]
    bad[next(i for i,row in enumerate(bad) if row[0] == 'INIT')][1] = 0
    need(rejected(lambda: trace_graph(graph, bad)), 'public INIT control')
    bad = [list(row) for row in graph['program']]
    bad[next(i for i,row in enumerate(bad) if row[0] == 'ADD')][2] = 10**9
    need(rejected(lambda: trace_graph(graph, bad)), 'dead read control')
    return {'inner_opcodes': counts, 'outer_opcodes': dict(root), 'targets': targets,
            'paid': paid, 'private_peak': peak, 'paid_cut_private_peak': cut_peak,
            'peak_instruction': peak_site, 'last_inner_paid_instruction': last_cut,
            'last_outer_paid_branch': last_branch[0], 'context_coefficient': targets + peak,
            'private_allocation_lifetimes': counts['INIT'] * root['LOCAL'] + ports * root['QUERY'],
            'controls': ['missing CLEAR','public INIT','dead operand','paid-cut-only undercount']}

def source_transport():
    module = types.ModuleType('review_transport')
    sys.modules[module.__name__] = module
    exec(compile((SRC / 'transport.py').read_text(), str(SRC / 'transport.py'), 'exec'), module.__dict__)
    return module

@dataclass(frozen=True)
class Job:
    owner: int
    axes: tuple
    def select(self, indices):
        return Job(self.owner, tuple(self.axes[i] for i in indices))

def fixture(mod, q, base, ticks):
    p = mod.Plan.__new__(mod.Plan)
    p.n, p.targets, p.paid = 24, (1, 1), (1,) * q
    p.bands, p.count = range(10,16,2), {10:1,12:2,14:1}
    p.delay = {10:1,12:base,14:base**2}
    p.ticks, p.rounds, p.width = ticks, 8, max(32,1 << (2*ticks-1).bit_length())
    p.source_width = ticks * 2
    p.send, p.receive, p.sources = defaultdict(list), defaultdict(list), defaultdict(list)
    for parent, child in ((14,12),(12,10)):
        p.send[parent,q-1] = [mod.Link(0,1,child,0,0)]
        p.receive[child,0] = [mod.Link(0,1,parent,q-1,0)]
    p.sources[14,1] = [mod.Source(0,1,0,4)]
    return p

def oracle_calendar(p):
    q, span, maximum = len(p.paid), len(p.bands), max(p.count.values())
    contexts = {}
    slots = []
    for birth in range(p.ticks):
        for e in p.bands:
            for rep in range(p.count[e]):
                ident = (birth * span + (e-10)//2) * maximum + rep
                contexts[ident] = (birth, birth + q*p.delay[e], e, rep)
                slots.append((birth+q*p.delay[e], 0, e, 0, rep, ident))
                for j in range(q):
                    slots.append((birth+j*p.delay[e], 1, -e, j, rep, ident))
    slots.sort()
    rows, timed, serial, loans = [], [], 0, {}
    for tick, phase, ordered_e, j, rep, ident in slots:
        if phase == 0:
            row = (2,ident)
            rows.append(row); timed.append((tick,row)); continue
        e = -ordered_e
        if j == 0:
            row = [0,ident,e-8]
            for port in range(2):
                key = tick,e,rep,port
                if key in loans:
                    row += [1,loans.pop(key)]
                elif e == 14 and port == 1 and rep == 0:
                    row += [2,tick*2,e-8,4]
                else:
                    row += [0,e-8]
            row = tuple(row); rows.append(row); timed.append((tick,row))
        selected = 0
        if tick < p.ticks and j == q-1 and e in (12,14) and rep == 0:
            child = e-2
            selected = child-8
            key = tick,child,0,0
            need(key not in loans, 'oracle duplicate loan')
            loans[key] = serial
        row = (1,ident,serial,e-8,selected)
        serial += 1
        rows.append(row); timed.append((tick,row))
    need(not loans, 'oracle uncollected loan')
    return rows, timed, contexts

class CensusMachine:
    def __init__(self, p, timed, contexts, forwarding):
        self.p, self.timed, self.contexts, self.forwarding = p, timed, contexts, forwarding
        self.live = {i:None for i in range(p.width)}
        self.next_owner, self.capacity = p.width, p.width
        self.vacant, self.holders = [], defaultdict(set)
        self.tick, self.ident, self.op = 0, None, None
        self.peak, self.observations = p.width, 0
        self.open_transients = self.close_transients = self.aliases = 0
        self.registered_only_failures = 0
        self.max_inclusive = 0
        self.max_holders = 0
        self.k = len(p.targets) + 5
        self.bound = p.width + self.k * sum(p.count[e]*(len(p.paid)*p.delay[e]+1) for e in p.bands)

    def observe(self):
        self.observations += 1
        charges = Counter(v for v in self.live.values() if v is not None)
        inclusive = {i for i,(birth,end,e,rep) in self.contexts.items() if birth <= self.tick <= end}
        self.max_inclusive = max(self.max_inclusive, len(inclusive))
        need(set(charges) <= inclusive, 'owner beyond origin lifetime')
        need(all(v <= self.k for v in charges.values()), 'per-context charge')
        need(len(self.live) <= self.p.width + self.k*len(inclusive) <= self.bound, 'inclusive bound')
        need(self.capacity <= self.bound, 'capacity bound')
        frame = inspect.currentframe().f_back
        while frame and frame.f_code.co_name != 'decode':
            frame = frame.f_back
        if frame:
            registered = frame.f_locals['live']
            pending = frame.f_locals['pending']
            need(all(job.owner in self.live for job in pending.values()), 'pending dead owner')
            if self.ident not in registered and charges.get(self.ident,0):
                if self.op == 0: self.open_transients += 1
                if self.op == 2: self.close_transients += 1
            if len(self.live) > self.p.width + self.k*len(registered):
                self.registered_only_failures += 1

    def allocate(self):
        if self.vacant:
            owner = self.vacant.pop()
        else:
            owner = self.next_owner
            self.next_owner += 1
            self.capacity += 1
        need(owner not in self.live, 'double allocation')
        self.live[owner] = self.ident
        self.peak = max(self.peak, len(self.live))
        self.observe()
        return owner

    def retire(self, owner):
        need(owner in self.live, 'double retire')
        need(not self.holders[owner] - {self.ident}, 'retired outstanding loan')
        del self.live[owner]
        self.vacant.append(owner)
        self.observe()

    def zero(self, exemplar):
        return Job(self.allocate(), exemplar.axes)

    def retire_zero(self, job):
        need(self.live[job.owner] == self.ident, 'retired borrowed input')
        self.retire(job.owner)

    def leaf(self, job):
        need(job.owner in self.live and len(job.axes) == 1, 'bad leaf')

    def native(self, ports, columns):
        ident = self.ident
        for job in ports:
            need(job.owner in self.live, 'dead native input')
            self.holders[job.owner].add(ident)
            self.max_holders = max(self.max_holders, len(self.holders[job.owner]))
            self.aliases += int(self.live[job.owner] not in (None,ident))
        def run():
            own = [self.allocate(), self.allocate()]
            for j in range(len(self.p.paid)):
                if j == len(self.p.paid)-1:
                    own.append(self.allocate())
                job = ports[0] if self.forwarding else Job(own[0], tuple(range(columns)))
                need(len(job.axes) == columns, 'toy native extent')
                yield job
            own += [self.allocate(), self.allocate()]
            for owner in reversed(own):
                self.retire(owner)
            for job in ports:
                self.holders[job.owner].remove(ident)
        return run()

    def records(self):
        for tick,row in self.timed:
            self.tick, self.op, self.ident = tick,row[0],row[1]
            yield row
            self.observe()

def calendars(mod):
    cases, totals = [], Counter()
    for q in (2,3,4):
        for base in (q,q+1):
            for ticks in (1,5,100):
                for forwarding in (False,True):
                    p = fixture(mod,q,base,ticks)
                    expected,timed,contexts = oracle_calendar(p)
                    need(list(p.events()) == expected, 'calendar differs from independent ordered slots')
                    machine = CensusMachine(p,timed,contexts,forwarding)
                    rows = [Job(i,tuple(range(p.n))) for i in range(p.width)]
                    p.decode(rows,0,0,machine,machine.records())
                    need(machine.live == {i:None for i in range(p.width)}, 'decoder retained owner')
                    need(machine.capacity == machine.peak, 'free-first capacity')
                    need(machine.open_transients and machine.close_transients, 'microstep controls not reached')
                    need(machine.registered_only_failures, 'dictionary-only undercount control not reached')
                    cases.append({'q':q,'base':base,'ticks':ticks,'forwarding':forwarding,
                                  'contexts':len(contexts),'records':len(expected),'capacity':machine.capacity,
                                  'inclusive_peak':machine.max_inclusive,'aliases':machine.aliases,
                                  'maximum_simultaneous_holders':machine.max_holders})
                    totals.update(contexts=len(contexts),records=len(expected),observations=machine.observations,
                                  open_transients=machine.open_transients,close_transients=machine.close_transients,
                                  registered_only_failures=machine.registered_only_failures,aliases=machine.aliases)
    p = fixture(mod,3,2,10)
    expected,timed,contexts = oracle_calendar(p)
    machine = CensusMachine(p,timed,contexts,False)
    need(rejected(lambda:p.decode([Job(i,tuple(range(p.n))) for i in range(p.width)],0,0,machine,machine.records())),
         'short-delay return violation not rejected')
    need(any(case['forwarding'] and case['maximum_simultaneous_holders'] >= 3 for case in cases),
         'three-generation forwarded custody not exercised')
    p = fixture(mod,2,2,10)
    expected,timed,contexts = oracle_calendar(p)
    by_tick = defaultdict(list)
    for tick,row in timed: by_tick[tick].append(row)
    reversed_closes = []
    for tick,rows in sorted(by_tick.items()):
        closes = [row for row in rows if row[0] == 2]
        reversed_closes.extend((tick,row) for row in reversed(closes))
        reversed_closes.extend((tick,row) for row in rows if row[0] != 2)
    machine = CensusMachine(p,reversed_closes,contexts,False)
    need(rejected(lambda:p.decode([Job(i,tuple(range(p.n))) for i in range(p.width)],0,0,machine,machine.records())),
         'reversed same-tick close order not rejected')
    return {'fixtures':len(cases),'totals':dict(totals),'cases':cases,
            'controls':['registered-dictionary undercount','short delay breaks loan custody',
                        'reversed same-tick closing order','three-generation forwarded ancestor aliases']}

def allocator():
    tree = ast.parse((SRC / 'raw_binary.py').read_text())
    bank = next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name == 'Banks')
    names = {'start','zero','read','install','retire','clone'}
    methods = [node for node in bank.body if isinstance(node,ast.FunctionDef) and node.name in names]
    need({x.name for x in methods} == names, 'allocator methods')
    derived = ast.parse((SRC / 'receiver.py').read_text())
    derived = next(node for node in derived.body if isinstance(node,ast.ClassDef) and node.name == 'OwnerBanks')
    need(len(derived.bases) == 1 and isinstance(derived.bases[0],ast.Name) and derived.bases[0].id == 'Banks', 'owner inheritance')
    need(not ({node.name for node in derived.body if isinstance(node,ast.FunctionDef)} & names), 'allocator override')
    @contextmanager
    def tapes(n):
        yield tuple(BytesIO() for _ in range(n))
    def read(tape,n):
        data = tape.read(n)
        need(len(data) == n, 'short test tape')
        return data
    env = {'write_zeros':lambda tape,n:tape.write(bytes(n)), 'read_exact':read,
           'copy_bytes':lambda a,b,n:b.write(read(a,n)), 'work_tapes':tapes,'CHUNK':2}
    extracted = ast.Module(body=[ast.ClassDef(name='ExtractedBanks',bases=[],keywords=[],body=methods,decorator_list=[])],type_ignores=[])
    exec(compile(ast.fix_missing_locations(extracted),'source-extracted allocator','exec'),env)
    def fresh():
        obj = env['ExtractedBanks']()
        obj.capacity, obj.vacant, obj.live = 0, [], set()
        obj.tape, obj.volume = BytesIO(), 3
        return obj
    histories = steps = 0
    for word in product('AR',repeat=10):
        obj, peak, valid = fresh(), 0, True
        for symbol in word:
            if symbol == 'A':
                obj.zero()
            elif obj.live:
                obj.retire(min(obj.live),require_zero=True)
            else:
                valid = False
                break
            steps += 1
            peak = max(peak,len(obj.live))
            need(obj.capacity == peak, 'source allocator high-water')
            need(set(obj.vacant).isdisjoint(obj.live) and set(obj.vacant)|obj.live == set(range(obj.capacity)), 'completed-call partition')
            need(len(set(obj.vacant)) == len(obj.vacant), 'duplicate vacant index')
        histories += valid
    obj = fresh()
    first = obj.zero()
    obj.tape.seek(0); obj.tape.write(b'ABC')
    clone = obj.clone(first)
    obj.start(clone)
    need(obj.tape.read(3) == b'ABC' and first != clone, 'actual clone owner/data')
    obj.retire(clone); obj.retire(first)
    need(obj.zero() == first and obj.capacity == 2, 'free-first reuse')
    obj = fresh()
    for _ in range(10): obj.zero()
    for owner in sorted(obj.live): obj.retire(owner)
    obj.zero()
    need(obj.capacity == 10 and len(obj.live) == 1, 'warm history control')
    stale_read_rejected = rejected(lambda:obj.start(0 if 0 not in obj.live else 1))
    need(stale_read_rejected, 'retired owner read control')
    return {'complete_length10_histories':histories,'executed_calls':steps,
            'clone_bytes':3,'warm_capacity':10,'warm_live':1,
            'controls':['warm history cannot be reset','retired owner cannot be read']}

def source_surface():
    def calls(file, cls, method):
        tree = ast.parse((SRC/file).read_text())
        node = next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name == cls)
        node = next(n for n in node.body if isinstance(n,ast.FunctionDef) and n.name == method)
        return sorted(n.func.attr for n in ast.walk(node) if isinstance(n,ast.Call)
                      and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Attribute)
                      and isinstance(n.func.value.value,ast.Name) and n.func.value.value.id == 'self'
                      and n.func.value.attr == 'banks')
    inner = calls('raw_binary.py','BinarySource','inner')
    outer = calls('strong_binary.py','StrongBinarySource','raw')
    need(inner == ['retire','swap','xor','zero'], 'inner bank call surface changed')
    need(outer == ['clone','retire','route','route','route','route','swap','xor','xor'], 'outer bank call surface changed')
    return {'inner_bank_calls':inner,'outer_bank_calls':outer}

def main():
    bindings,graph,caller = load_sources()
    result = {'status':'PASS_INDEPENDENT_BINARY_OWNER_CENSUS',
              'source_commit':bindings['commit'], 'source_files':len(bindings['files']),
              'proof_sha256':sha256((AUTHOR/'PROOF.md').read_bytes()).hexdigest(),
              'finite_census':census(graph,caller), 'source_surface':source_surface(),
              'allocator':allocator(),'calendar':calendars(source_transport()),
              'scope':'Exact fixed source census plus bounded independent calendar/decoder/allocator checks; all-size interval proof reviewed separately; mass and delay asymptotics excluded.'}
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__ == '__main__':
    main()
