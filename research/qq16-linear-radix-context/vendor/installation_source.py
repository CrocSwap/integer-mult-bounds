#!/usr/bin/env python3
"""Source-bound numerical constructor and physical count-installation audit.

Mihir Srivastava, substantial OpenAI Codex assistance. Apache-2.0.
All executed source algorithms come from the authenticated retained archive.
"""
import ast
from contextlib import contextmanager
import hashlib
import io
import itertools
import json
from pathlib import Path
import sys
import tarfile
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = 'research/physical-gaussian-leaf/inputs/pr3087.tar'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def authenticate():
    for row in json.loads((HERE / 'SOURCES.json').read_bytes())['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
                 == row['sha256'], 'source pin: ' + row['path'])


def load_source():
    data = (ROOT / ARCHIVE).read_bytes()
    for path in ('inputs/pr3055.tar', 'inputs/pr2899.tar', 'inputs/pr2809.tar'):
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            data = archive.extractfile(path).read()
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        sources = {member.name: archive.extractfile(member).read()
                   for member in archive.getmembers() if member.isfile() and member.name.endswith('.py')}
    vendor = 'inputs/pr2753/predecessor/vendor/'
    modules = {}
    def module(name, path):
        obj = types.ModuleType(name)
        obj.__file__ = path
        sys.modules[name] = obj
        exec(compile(sources[path], path, 'exec'), obj.__dict__)
        modules[name] = obj
        return obj
    for name in ('words', 'records', 'stream', 'cardinality', 'counts'):
        module(name, vendor + name + '.py')
    module('cardinal_counts', 'inputs/pr2753/predecessor/cardinal_counts.py')
    module('directory', vendor + 'directory.py')
    w, r = modules['words'], modules['records']
    namespace = dict(Tape=r.Tape, Arena=w.Arena, Meter=w.Meter, BLANK=w.BLANK,
                     LEFT=w.LEFT, need=w.need, contextmanager=contextmanager,
                     sys=sys, FunctionType=types.FunctionType)
    def definitions(path, names, target):
        tree = ast.parse(sources[path])
        nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names]
        need({n.name for n in nodes} == set(names), 'complete source definition slice')
        exec(compile(ast.Module(body=nodes, type_ignores=[]), path, 'exec'), target)
    definitions('scratch_pool.py', {'Lease', 'ScratchPool'}, namespace)
    definitions('macro_binding.py', {'view'}, namespace)
    namespace.update(Count=modules['cardinal_counts'].Count,
                     Context=modules['directory'].Context, Ring=w.Ring,
                     Unsigned=w.Unsigned, Program=r.Program,
                     append_tape=modules['directory'].append_tape)
    tree = ast.parse(sources['macro_machine.py'])
    machine = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Machine')
    names = {'tape', 'count', 'commit', 'save_count', 'new_context'}
    methods = [n for n in machine.body if isinstance(n, ast.FunctionDef) and n.name in names]
    need({n.name for n in methods} == names, 'complete constructor method slice')
    cls = ast.ClassDef(name='Machine', bases=[], keywords=[], body=methods, decorator_list=[])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])),
                 'macro_machine.py:constructor-slice', 'exec'), namespace)
    # Bind the caller's actual precondition: streams park before new_context.
    call = next(n for n in machine.body if isinstance(n, ast.FunctionDef) and n.name == 'call')
    calls = [ast.unparse(n.value.func) for n in call.body
             if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)]
    need(calls.index('self.streams.park') < calls.index('self.new_context'), 'source CALL parks before replacement')
    load = next(n for n in machine.body if isinstance(n, ast.FunctionDef) and n.name == 'load_root')
    need(any(isinstance(n, ast.Call) and ast.unparse(n.func) == 'self.new_context'
             for n in ast.walk(load)), 'source root constructor call')
    return modules, namespace, sources


@contextmanager
def allocated_from(modules, pool, Tape):
    """Specialize only the loaded allocation sites, as source install does.

    This does not execute the complete install hook or selected loader. Each
    source module retains a separate globals namespace, including both Counts.
    """
    changed = []
    for module in modules.values():
        for name, value in tuple(vars(module).items()):
            if value is Tape:
                changed.append((module, name, value))
                setattr(module, name, pool.acquire)
    original_init = Tape.__init__
    def forbidden(*_args, **_kwargs):
        raise ValueError('unexpected physical Tape allocation')
    Tape.__init__ = forbidden
    try:
        yield
    finally:
        Tape.__init__ = original_init
        for module, name, value in reversed(changed):
            setattr(module, name, value)


def counts(tapes):
    return tuple(sum(getattr(t.meter, field) for t in tapes)
                 for field in ('reads', 'writes', 'moves'))


def body(tape, blank):
    return bytes(tape.cells[1:]).rstrip(bytes([blank]))


def expected_install(n, dirty):
    # n includes the RIGHT delimiter; dirty is the previous dense body length.
    return 7*n + 2*dirty + 10, 2*n + dirty, 6*n + 2*dirty + 14


def run_case(modules, ns, q, width, dimension, dirty=0, capacity=2,
             early_close=False, wrong_view=False):
    w, r = modules['words'], modules['records']
    modulus_value = q**width
    arena = w.Arena(modulus_value.bit_length()+1, 32)
    indices = w.Arena(8, 8)
    modulus = arena.input(modulus_value)
    size, depth = indices.input(2*dimension), indices.input(1)
    highs, program, spectator = r.Tape(), r.Tape(), r.Tape()
    for i in range(dirty):
        highs.append((i+1) & 1)
    highs.rewind()
    for tape in (program, spectator):
        for bit in (1, 0, 1, 1, 0):
            tape.append(bit)
        tape.rewind()
    protected = [(t, bytes(t.cells), t.head) for t in (program, spectator)]
    pool = ns['ScratchPool'](capacity)
    runtime = object.__new__(ns['Machine'])
    runtime.arena, runtime.indices = arena, indices
    runtime.binding = types.SimpleNamespace(codes=types.SimpleNamespace(q=q, dimension=dimension, bits=7))
    runtime.roles = {'highs': highs, 'program': program, 'spectator': spectator}
    observation = {}
    def observed_save(self, value, label):
        need(isinstance(value.tape, ns['Lease']), 'source count uses a scratch lease')
        source = value.tape.physical
        observation['lease'] = value.tape
        observation['n'] = len(body(source, w.BLANK))
        observation['source_value'] = sum(bit << i for i, bit in enumerate(body(source, w.BLANK)[:-1]))
        if early_close:
            value.close()
        before = counts((source, highs))
        ns['Machine'].save_count(self, value, label)
        observation['install'] = tuple(b-a for a, b in zip(before, counts((source, highs))))
    runtime.save_count = types.MethodType(observed_save, runtime)
    with allocated_from(modules, pool, r.Tape):
        runtime.new_context(modulus, size, depth)
    if wrong_view:
        runtime.context.highs.tape = program
    expected = q**((width-1)*dimension*dimension)
    encoding = bytes((expected >> i) & 1 for i in range(expected.bit_length())) + bytes([w.RIGHT])
    need(body(highs, w.BLANK) == encoding and observation['source_value'] == expected,
         'exact high count and canonical encoding')
    need(runtime.context.highs.tape is highs and runtime.program.tape is program,
         'installed fixed Tape views')
    need(runtime.context.cap.inspect() == q**(width-1), 'exact high-field radix')
    need(runtime.context.raw is runtime.context.ring.raw and runtime.context.ring.modulus is modulus,
         'retained numerical aliases')
    need(observation['install'] == expected_install(len(encoding), dirty), 'exact installation operation counts')
    need(pool.peak == 2 and pool.allocations == 2, 'exact two-lease constructor')
    pool.empty()
    need(highs.head == program.head == spectator.head == 1 and
         all(arena.words[i].head == 1 for i in arena.live) and
         all(indices.words[i].head == 1 for i in indices.live), 'canonical constructor heads')
    need(arena.live == {modulus.slot, runtime.context.ring.one.slot, runtime.context.cap.slot},
         'no temporary numerical words after constructor')
    need(all(bytes(t.cells) == data and t.head == head for t, data, head in protected),
         'dirty program and spectator preservation')
    # The ended result lease uses slot one; force reuse of that exact slot.
    first, second = pool.acquire(), pool.acquire()
    need(second.physical is observation['lease'].physical, 'same physical scratch role reused')
    second.append(1); second.append(w.RIGHT); second.rewind()
    saved = bytes(second.physical.cells), second.physical.head
    observation['lease'].clear()
    need((bytes(second.physical.cells), second.physical.head) == saved and second.active,
         'ended lease cannot erase later borrower')
    first.clear(); second.clear(); pool.empty()
    runtime.context.close()
    runtime.context.ring.close()
    arena.free(modulus); indices.free_many(size, depth)
    need(not arena.live and not indices.live and not body(highs, w.BLANK), 'owned constructor cleanup')
    return {'q': q, 'w': width, 'd': dimension, 'dirty': dirty, 'value': str(expected),
            'n': len(encoding), 'install': observation['install'], 'peak': 2}


def reject(action, message):
    try:
        action()
    except ValueError as error:
        need(message in str(error), 'specific rejection: ' + str(error))
        return
    raise ValueError('negative control accepted: ' + message)


def main():
    authenticate()
    modules, ns, sources = load_source()
    cases = [run_case(modules, ns, q, width, dimension, dirty)
             for q, width, dimension, dirty in itertools.product((2, 3, 5), (1, 2, 3), (1, 2, 4), (0, 1, 7))]
    cases.append(run_case(modules, ns, 3, 3, 8, 31))
    reject(lambda: run_case(modules, ns, 3, 2, 2, capacity=1), 'fixed scratch role inventory exhausted')
    reject(lambda: run_case(modules, ns, 3, 2, 2, early_close=True), 'live scratch lease')
    reject(lambda: run_case(modules, ns, 3, 2, 2, wrong_view=True), 'installed fixed Tape views')
    witness = next(c for c in cases if (c['q'],c['w'],c['d'],c['dirty']) == (3,2,2,0))
    need(witness['value'] == '81' and witness['n'] == 8, 'dimension-square positive discriminator')
    need(int(witness['value']) != 3**2, 'dimension-linear exponent rejected')
    need(witness['install'] != (expected_install(8,0)[0]-1, 16, 62), 'one-read undercharge rejected')
    need(expected_install(8,7) != expected_install(8,0), 'dirty overwrite cannot use empty tariff')
    result = {'status': 'PASS_QQ16_HIGH_COUNT_INSTALLATION', 'cases': len(cases),
              'executed_rejection_controls': 3, 'arithmetic_discriminators': 3, 'witness': witness,
              'largest_count_bits': max(c['n']-1 for c in cases),
              'source_members_sha256': {path: hashlib.sha256(sources[path]).hexdigest()
                  for path in ('macro_machine.py','scratch_pool.py','macro_binding.py',
                    'inputs/pr2753/predecessor/vendor/counts.py',
                    'inputs/pr2753/predecessor/vendor/directory.py')}}
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
