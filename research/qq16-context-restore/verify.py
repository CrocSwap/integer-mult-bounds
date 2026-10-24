#!/usr/bin/env python3
"""Literal retained constructors versus finite records; no full caller replay."""
import argparse
import ast
import hashlib
import io
import itertools
import json
from pathlib import Path
import sys
import tarfile
from types import ModuleType, SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT/'research/qq16-finite-handle-charge'))
from kernel import need
from constructor import Constructor, FIELDS, UNSIGNED, RING, COUNT, CONTEXT, PROGRAM


def authenticate():
    for row in json.loads((HERE/'SOURCES.json').read_bytes())['files']:
        if row['usage'] == 'input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() == row['sha256'],
                 'source pin: '+row['path'])


def source():
    """Exact selected AST definitions; no arithmetic/loader substitution.

    Only restore_context/tape/count from Machine are in scope. Their original
    ASTs and the real Count inheritance chain are unchanged. Uncalled methods
    may refer to imports outside this slice; they are not replayed or claimed.
    """
    blob = (ROOT/'research/physical-gaussian-leaf/inputs/pr3087.tar').read_bytes()
    hashes = {}
    for name in ('inputs/pr3055.tar', 'inputs/pr2899.tar', 'inputs/pr2809.tar'):
        with tarfile.open(fileobj=io.BytesIO(blob)) as archive:
            blob = archive.extractfile(name).read()
        hashes[name] = hashlib.sha256(blob).hexdigest()
    archive = tarfile.open(fileobj=io.BytesIO(blob))
    env = {'__name__': 'retained_context_oracle'}

    def run(path, names=None, exclude_imports=False):
        raw = archive.extractfile(path).read()
        hashes[path] = hashlib.sha256(raw).hexdigest()
        tree = ast.parse(raw, filename=path)
        if names is not None:
            tree.body = [n for n in tree.body if getattr(n, 'name', None) in names]
            need(len(tree.body) == len(names), 'complete selected source definitions')
        if exclude_imports:
            tree.body = [n for n in tree.body if not isinstance(n, (ast.Import, ast.ImportFrom))]
        exec(compile(tree, path, 'exec'), env)

    vendor = 'inputs/pr2753/predecessor/vendor/'
    run(vendor+'words.py')
    run(vendor+'records.py', exclude_imports=True)
    run(vendor+'cardinality.py', {'Natural'})
    run(vendor+'counts.py', {'Count'})
    env['RetainedCount'] = env['Count']
    run('inputs/pr2753/predecessor/cardinal_counts.py', {'Count'})
    run(vendor+'directory.py', {'Context'})
    run('macro_binding.py', {'view'})
    path = 'macro_machine.py'
    raw = archive.extractfile(path).read()
    hashes[path] = hashlib.sha256(raw).hexdigest()
    cls = next(n for n in ast.parse(raw).body if isinstance(n, ast.ClassDef) and n.name == 'Machine')
    cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and
                n.name in {'tape', 'count', 'restore_context'}]
    need(len(cls.body) == 3, 'three complete literal source methods')
    exec(compile(ast.Module(body=[cls], type_ignores=[]), path, 'exec'), env)
    archive.close()
    path = 'research/qq16-caller-install/installer.py'
    raw = (ROOT/path).read_bytes()
    hashes[path] = hashlib.sha256(raw).hexdigest()
    node = next(n for n in ast.parse(raw).body if isinstance(n, ast.FunctionDef) and n.name == 'owned_tapes')
    records = ModuleType('records')
    records.Tape = env['Tape']
    sys.modules['records'] = records
    exec(compile(ast.Module(body=[node], type_ignores=[]), path, 'exec'), env)
    return env, hashes


def fixture(env, bits=16, boundary_aliases=False):
    arena, indices = env['Arena'](bits, 8), env['Arena'](bits, 8)
    residue = [arena.input(v) for v in (11, 1, (1 << (bits-2))+3)]
    index = [indices.input(v) for v in (5, (1 << (bits-3))+1)]
    highs, program = env['Tape'](), env['Tape']()
    for tape, values in ((highs, (1, 0, 1, 3)), (program, (7, 1, 6))):
        for value in values:
            tape.append(value)
        tape.rewind()
    codes = SimpleNamespace(q=5, dimension=8, bits=3)  # fixed boundary fixture
    if boundary_aliases:
        # Fixed pre-input graph with shared roles, a cycle and an omitted field.
        arena.alias = (program, highs, indices)
        indices.alias = arena
        codes.hidden_tape = env['Tape']()
    fixed = [arena, indices, codes, highs, program, *residue, *index]
    runtime = env['Machine'].__new__(env['Machine'])
    runtime.arena, runtime.indices = arena, indices
    runtime.binding = SimpleNamespace(codes=codes)
    runtime.roles = {'highs': highs, 'program': program}
    runtime.context = runtime.program = runtime.size = runtime.depth = None
    machine = Constructor(len(fixed), (1, 2, 3, 4, 5), (6, 7, 8), (9, 10))
    return runtime, fixed, machine


def physical_state(fixed):
    """Test-only oracle; include borrowed word/tape contents, heads and meters."""
    arenas, tapes = fixed[:2], fixed[3:5]
    return ([[(bytes(w.cells), w.head) for w in a.words] for a in arenas],
            [dict(a.meter.record()) for a in arenas],
            [(bytes(t.cells), t.head, dict(t.meter.record())) for t in tapes],
            [tuple(sorted(a.live)) for a in arenas])


def compare(env, runtime, held, fixed, machine):
    """Independent typed graph isomorphism, including identity and field order.

    Host identity is used only here, never as constructor input. Fixed boundary
    identity is retained; numeric leaves use PR5330's opaque-leaf quotient.
    """
    tags = {env['Unsigned']: UNSIGNED, env['Ring']: RING, env['Count']: COUNT,
            env['Context']: CONTEXT, env['Program']: PROGRAM}
    source_to_handle, handle_to_source = {}, {}

    def visit(value, handle):
        for i, boundary in enumerate(fixed, 1):
            if value is boundary:
                need(handle == i, 'exact fixed boundary alias')
                return
        if type(value) not in tags:
            need(value is None or type(value) is int, 'declared numeric leaf type')
            need(handle == 0, 'opaque numerical leaf quotient')
            return
        tag = tags[type(value)]
        need(machine.read(handle, 0) == tag, 'source type preserved')
        need(tuple(vars(value)) == FIELDS[tag], 'literal source attribute order')
        key = id(value)
        if key in source_to_handle:
            need(source_to_handle[key] == handle, 'source alias preserved')
            return
        need(handle not in handle_to_source, 'fresh source identities remain distinct')
        source_to_handle[key] = handle
        handle_to_source[handle] = key
        for i, name in enumerate(FIELDS[tag]):
            visit(getattr(value, name), machine.field(handle, i))

    actual = (runtime.context, runtime.program, runtime.size, runtime.depth,
              *(held if held else (None, None)))
    for i, value in enumerate(actual):
        visit(value, machine.store.read(machine.roots+i))
    live = {x for x in range(machine.fixed+1, machine.limit) if machine.read(x, 0)}
    need(live == set(handle_to_source), 'all and only retained constructor objects')
    # Test-only expansion at the SAME fixed boundary, not a paid inventory
    # emitter. The source function supplies the literal skip/order convention.
    proxies = {}
    def expand(handle):
        if handle == 0:
            return 0
        if handle <= machine.fixed:
            return fixed[handle-1]
        if handle not in proxies:
            proxy = SimpleNamespace()
            proxies[handle] = proxy
            for i, name in enumerate(FIELDS[machine.read(handle, 0)]):
                setattr(proxy, name, expand(machine.field(handle, i)))
        return proxies[handle]
    projected = tuple(expand(machine.store.read(machine.roots+i)) for i in range(6))
    need(env['owned_tapes'](actual) == env['owned_tapes'](projected),
         'literal ordered Tape inventory after boundary gluing')
    return len(live)


def unmetered(function, machine):
    """Oracle reads are excluded from algorithm receipts, not source data."""
    before = machine.meter()
    try:
        return function()
    finally:
        machine.store.accesses = before['accesses']
        machine.store.scalar = before['scalar']


def run_session(env, bits, boundary_aliases=False):
    runtime, fixed, machine = fixture(env, bits, boundary_aliases)
    before = physical_state(fixed)
    held = None
    states, peak_retained, reuse = 0, 0, False
    previous_handles = set()
    # Every 3^3 * 2^2 slot tuple, including aliases. This exhaustive structural
    # domain is not a claim that every tuple is a valid numerical parent frame.
    labels = list(itertools.product(range(3), range(3), range(3), range(2), range(2)))
    for i, row in enumerate(labels * 2):
        if i == 1:
            held = (runtime.context, runtime.program)
            machine.hold()
        if i == 109:
            held = None
            machine.release()
        runtime.restore_context(row)
        machine.restore(row)
        count = unmetered(lambda: compare(env, runtime, held, fixed, machine), machine)
        peak_retained = max(peak_retained, count)
        current = {machine.store.cells[machine.roots], machine.store.cells[machine.roots+1]}
        reuse = reuse or bool(current & previous_handles)
        previous_handles.update(current)
        states += 1
    need(physical_state(fixed) == before, 'all borrowed physical state untouched')
    need(reuse and machine.peak == 15 and peak_retained == 10,
         'retention discriminator and safe address reuse')
    machine.dispose()
    need(not any(machine.store.cells), 'complete owned metadata disposal')
    receipt, tariff = machine.meter(), machine.tariff()
    need(receipt['accesses'] <= tariff['accesses'] and receipt['scalar'] <= tariff['scalar'],
         'session constructive tariff')
    return dict(restorations=states, slot_tuples=len(labels), peak_dynamic=machine.peak,
                peak_retained=peak_retained, safe_address_reuse=reuse,
                collections=machine.collections, receipt=receipt, tariff=tariff)


def reject(function, reason):
    try:
        function()
    except ValueError as error:
        need(reason in str(error), 'intended failure control: '+str(error))
        return
    raise ValueError('accepted mutation: '+reason)


def controls(env):
    names = []

    def mutant(name, change, reason):
        runtime, fixed, machine = fixture(env)
        runtime.restore_context((0, 1, 2, 0, 1))
        machine.restore((0, 1, 2, 0, 1))
        held = (runtime.context, runtime.program)
        machine.hold()
        runtime.restore_context((2, 0, 1, 1, 0))
        machine.restore((2, 0, 1, 1, 0))
        change(machine)
        reject(lambda: compare(env, runtime, held, fixed, machine), reason)
        names.append(name)

    root = lambda m, i=0: m.store.read(m.roots+i)
    mutant('wrong_highs_tape',
           lambda m: m.put(m.field(root(m), 7), 0, 5), 'exact fixed boundary alias')
    mutant('wrong_program_tape', lambda m: m.put(root(m, 1), 3, 4), 'exact fixed boundary alias')
    mutant('split_raw_alias',
           lambda m: m.put(root(m), 2, m.field(root(m, 4), 2)), 'source alias preserved')
    mutant('overwrite_borrowed_old_cap',
           lambda m: m.put(root(m, 4), 6, 6), 'exact fixed boundary alias')
    mutant('premature_old_context_reclamation',
           lambda m: m.write(root(m, 4), 0, 0), 'source type preserved')
    mutant('wrong_size_word', lambda m: m.store.write(m.roots+2, 9), 'exact fixed boundary alias')
    runtime, fixed, machine = fixture(env)
    machine.restore((0, 1, 2, 0, 1))
    machine.hold()
    reject(machine.hold, 'one borrowed prior pair')
    reject(machine.dispose, 'release borrowed pair before disposal')
    reject(lambda: machine.restore((3, 0, 0, 0, 0)), 'declared word slot')
    names += ['second_borrowed_pair', 'disposal_while_borrowed', 'out_of_range_slot']
    machine.release()
    for _ in range(10):
        machine.fresh(UNSIGNED)
    reject(lambda: machine.restore((0, 1, 2, 0, 1)), 'five fresh records')
    names.append('uncollected_history_exhaustion')
    return names


def compute():
    authenticate()
    env, hashes = source()
    small = run_session(env, 16)
    large = run_session(env, 4096)
    need(small == large, 'metadata independent of borrowed numerical bit lengths')
    aliased = run_session(env, 16, True)
    aliased_large = run_session(env, 4096, True)
    need(aliased == small == aliased_large, 'unchanged fixed-boundary sharing and cycles')
    return dict(status='PASS_QQ16_CONTEXT_RESTORE', source_members=hashes,
                each_session=small, sessions=4, total_restorations=4*small['restorations'],
                controls=controls(env),
                scope='Literal restoration metadata only; fixed boundary and at most one held pair; no numerical restoration, whole frontend, supplier or kappa claim.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = compute()
    path = HERE/'RESULT.json'
    if args.write:
        path.write_bytes((json.dumps(result, indent=2, sort_keys=True)+'\n').encode('utf-8'))
    else:
        need(result == json.loads(path.read_bytes()), 'complete deterministic receipt')
    print(result['status'])


if __name__ == '__main__':
    main()
