"""Source-authenticated checks of the changing-node whole-tree composition.

Observer decoding and snapshots never feed coordinates or branches to runtime.
Finite corroboration is separate from the quantified proof in PROOF.md.
Prepared for Jerry Chen / CubeJerry with substantial OpenAI assistance.
"""
from hashlib import sha256
from pathlib import Path
from types import ModuleType
import itertools
import json
import math
import sys

P = Path(__file__).resolve().parent
ROOT = P.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    module = ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def source_check():
    manifest = json.loads((P / 'SOURCES.json').read_text())
    for pin in manifest['files']:
        if pin['usage'] != 'input':
            continue
        raw = (ROOT / pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'source bytes: ' + pin['path'])
        from hashlib import sha1
        blob = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        need(blob == pin['git_blob'], 'source Git blob: ' + pin['path'])
    seam = json.loads((P / 'SEAMS.json').read_text())
    text = (ROOT / seam['source']).read_text()
    for old, new in seam['replacements'].items():
        need(text.count(old) == 1, 'unique declared geometry seam')
        text = text.replace(old, new)
    need(text == (P / 'workspace.py').read_text(), 'workspace exact declared source seam')
    return sum(pin['usage'] == 'input' for pin in manifest['files'])


def retired(machine):
    w, pool = machine.w, machine.workspace
    need(not pool.live and not machine.guards.live, 'all per-row owners retired')
    for role, cells in pool.backing.items():
        blank = w.BLANK if role.startswith('numeric.') else '_'
        need(all(x == blank for x in cells), 'whole historical role blank: ' + role)
        if role in pool.ports:
            need(pool.ports[role].head == 1, 'numerical retirement head')
    for port in machine.guards.ports:
        need(all(x == w.BLANK for x in port.cells), 'whole protected-zero history blank')
        need(port.head == (1 if machine.guards.started else 0), 'protected-zero head')
    need(all(x == '_' for x in machine.staging.cells) and machine.staging.head == 0,
         'whole staging history blank at origin')


def endpoint(values, moduli):
    """Independent defining CRT formula, only for globally valid input."""
    prefix, integer, prefixes = 1, 0, []
    for value, modulus in zip(values, moduli):
        need(0 <= value < modulus, 'valid defining-formula fixture')
        prefixes.append(prefix)
        integer += prefix * value
        prefix *= modulus
    return tuple(integer * pow(pre, -1, modulus) % modulus
                 for pre, modulus in zip(prefixes, moduli))


def run_case(modules, pred, tree, workspace, query_module, name, moduli, widths, values, ell):
    helper, base, rom, original, adapter, program = modules
    w, records, entry, numeric, caller_module, crt, row_module = base
    source = helper.axis_stream(w, records, entry, moduli, widths, values)
    initial = bytes(source.cells), source.head
    source_identity = id(source), id(source.cells)
    machine = tree.WholeTree(modules, workspace, query_module, source, widths, ell)
    oracle = caller_module.Caller(moduli, widths, ell, crt)
    expected = tuple(values)
    ids, high, trace = {}, {}, []
    write = source.write
    def guarded_write(value):
        need(not machine.workspace.live, 'source mutation before query retirement')
        write(value)
    source.write = guarded_write
    all_commands = machine.schedule + tuple(reversed(machine.schedule))
    forward = None
    for position, command in enumerate(all_commands):
        level, start, row = command
        stop, middle = start + (1 << level), start + (1 << (level - 1))
        specs = [s for s in oracle.row(expected, level, row) if middle <= s[0] < stop]
        expected = oracle.apply(expected, specs)
        pool = machine.workspace
        before = helper.traffic([source, *machine.guards.ports, *pool.ports.values()])
        setup_before, stage_before = pool.setup_actions, machine.staging.actions
        result = machine.step(command)
        retired(machine)
        need((id(source), id(source.cells)) == source_identity, 'one source backing across all nodes')
        need(pred.decode(source, widths, w, records) == expected, 'physical current-state row')
        need(source.head == 1 and len(source.cells) == len(initial[0]), 'source shape and head')
        for role, cells in pool.backing.items():
            need(role not in ids or ids[role] == id(cells), 'stable whole-tree role identity')
            ids[role] = id(cells)
            high[role] = max(high.get(role, 0), len(cells))
            need(len(cells) == high[role], 'historical backing never shrinks')
        traffic = helper.traffic([source, *machine.guards.ports, *pool.ports.values()]) - before
        traffic += pool.setup_actions - setup_before + machine.staging.actions - stage_before
        producer_calls, producer_steps = 0, 0
        if result is not None:
            producer_calls, producer_steps = result.invocations, result.producer_steps
            traffic += sum(t.actions for t in result.ports) + producer_steps
            meter = result.entry.context.arena.meter
            traffic += meter.reads + meter.writes + meter.moves
            # Independently compare to the predecessor's published complete row formula.
            inherited, _ = pred.bounds(widths, ell, level, start, row)
            precision = 1 + sum(widths[start:stop])
            need(tree.row_bound(widths, ell, command)
                 == inherited + 4 * 63 + 118 + 2**12 * (precision + 2),
                 'only declared paid additions to predecessor row invoice')
        else:
            need(traffic == 0, 'literal idle has zero tape traffic')
        allowance = tree.row_bound(widths, ell, command)
        need(traffic <= allowance, 'measured source operations below complete written allowance')
        trace.append({'command': list(command), 'state': list(expected),
                      'precision': 1 + sum(widths[start:stop]), 'actions': traffic,
                      'allowance': allowance, 'producer_calls': producer_calls,
                      'producer_instructions': producer_steps,
                      'retained_workspace_cells': sum(len(c) for c in pool.backing.values()),
                      'guard_cells': [len(p.cells) for p in machine.guards.ports]})
        if position + 1 == len(machine.schedule):
            forward = expected
            need(forward == oracle.run(values), 'published whole-tree forward order')
            if all(v < m for v, m in zip(values, moduli)):
                need(forward == endpoint(values, moduli), 'independent defining CRT endpoint')
    need((bytes(source.cells), source.head) == initial, 'entire physical source roundtrip')
    retained = (len(source.cells) + len(machine.staging.cells)
                + sum(len(p.cells) for p in machine.guards.ports)
                + sum(high.values()))
    need(len(pool.backing) == 118, 'unchanged actual row inventory')
    need(retained <= tree.retained_bound(widths, ell), 'complete rolewise storage envelope')
    return machine, {'name': name, 'moduli': list(moduli), 'widths': list(widths),
                     'initial': list(values), 'forward': list(forward), 'trace': trace,
                     'row_events': len(trace), 'active_rows': sum(t['producer_calls'] > 0 for t in trace),
                     'producer_calls': sum(t['producer_calls'] for t in trace),
                     'retained_total': retained, 'retained_bound': tree.retained_bound(widths, ell),
                     'high_water': high, 'source_initializations': 1}


def arithmetic_checks(tree):
    cases = 0
    worst = (0, 1)
    def moments(widths, ell, p):
        d = len(widths)
        sums = [0, 0, 0, 0]
        for level in range(1, d.bit_length()):
            n = 1 << level
            for start in range(0, d, n):
                precision = 1 + sum(widths[start:start+n])
                values = ((precision+2)**4, (precision+2)**2,
                          precision**2 * (n//2), (n+1)*(precision+2))
                sums = [a+b for a, b in zip(sums, values)]
        a, b, c, f = sums
        need(7*a < 8*(ell+3)**4*d**4 and a <= 715*p**4, 'quartic tree moment')
        need(b < 2*(ell+2)**2*d**2 and b <= 32*p**2, 'quadratic tree moment')
        need(3*c < 2*(ell+1)**2*d**3 and c <= 6*p**3, 'ROM tree moment')
        need(f < 3*(ell+3)*d**2 and f <= 15*p**2, 'stream tree moment')
        return sums
    for ell in range(2, 9):
        for d in (2, 4, 8):
            masks = range(1 << d) if d <= 4 else (0, 1, 85, 170, 254, 255)
            for mask in masks:
                widths = tuple(ell - 1 + ((mask >> i) & 1) for i in range(d))
                p = max(14, sum(widths))
                moments(widths, ell, p)
                exact = tree.whole_bound(widths, ell)
                ample = 2**34 * 2**(3 * ell) * (p + 2)**8
                envelope = 2**(4 * ell) * (p + 2)**16
                need(exact <= ample <= envelope, 'whole-tree geometric envelope calibration')
                if exact * worst[1] > worst[0] * envelope:
                    worst = (exact, envelope)
                cases += 1
    challenge = moments((20,)*16, 20, 320)
    return {'cases': cases, 'worst_ratio_numerator': worst[0], 'worst_ratio_denominator': worst[1],
            'independent_moment_challenge': {'ell': 20, 'd': 16, 'moments': challenge}}


def controls(machine, modules, pred, tree, workspace, query_module):
    failures = []
    def reject(label, fn):
        try:
            fn()
        except ValueError:
            failures.append(label)
        else:
            raise ValueError('negative control survived: ' + label)
    pool, w = machine.workspace, machine.w
    geometry = pool.geometry
    pool.begin(geometry, machine.source, machine.guards.ports)
    reject('live_query_reentry', lambda: pool.begin(geometry, machine.source, machine.guards.ports))
    reject('source_write_before_close', lambda: machine.source.write(machine.source.read()))
    pool.live = False
    changed = ((2,) * len(machine.widths), 2, 1, 0)
    reject('changed_global_shape', lambda: pool.begin(changed, machine.source, machine.guards.ports))
    role = 'numeric.canonical_right'
    port = pool.ports[role]
    port.cells[-1] = w.ONE
    reject('stale_historical_tail', lambda: retired(machine))
    port.cells[-1] = w.BLANK
    machine.guards.prepare(5)
    reject('unretired_guard_resize', lambda: machine.guards.prepare(7))
    machine.guards.retire()
    old = load('old_fixed_node_workspace', ROOT / 'research/crt-stable-row-workspace/workspace.py').Workspace()
    old.begin((machine.widths, machine.ell, 1, 0), machine.source, machine.guards.ports)
    old.live = False
    reject('predecessor_rejects_next_node',
           lambda: old.begin((machine.widths, machine.ell, 1, 2), machine.source, machine.guards.ports))
    reject('non_dyadic_shape', lambda: tree.commands((3, 3, 2), 3))
    reject('invalid_declared_width', lambda: tree.commands((4, 2), 3))
    # Direct defining endpoint detects omission of the first nontrivial subtree.
    values, moduli = (3, 2, 1, 1), (5, 7, 3, 2)
    helper, base, *_ = modules
    caller_module, crt = base[4], base[5]
    oracle = caller_module.Caller(moduli, (3, 3, 2, 2), 3, crt)
    state = values
    for level, start, row in tree.commands((3, 3, 2, 2), 3):
        if level == 1 and start == 0:
            continue
        middle, stop = start + (1 << (level - 1)), start + (1 << level)
        state = oracle.apply(state, [s for s in oracle.row(state, level, row) if middle <= s[0] < stop])
    reject('omitted_subtree_endpoint', lambda: need(state == endpoint(values, moduli), 'incomplete tree'))
    # This arithmetic fault is independent of the symbolic physical-row interpreter.
    reject('max_of_totals_storage', lambda: need(max(9 + 1, 1 + 9) == max(9, 1) + max(1, 9),
                                               'crossed historical peaks'))
    quadratic = sum((16//(1<<j))*(20*(1<<j)+3)**2 for j in range(1, 5))
    need(quadratic == 199815, 'independent review counterexample')
    reject('quadratic_geometric_ratio',
           lambda: need(3*quadratic < 4*23**2*16**2, 'rejected quadratic coefficient'))
    retired(machine)
    return failures


def main():
    source_count = source_check()
    pred = load('paid_row_reentry', ROOT / 'research/crt-paid-row-reentry/verify.py')
    modules = pred.modules()
    tree = load('whole_tree', P / 'tree.py')
    workspace = load('whole_tree_workspace', P / 'workspace.py')
    query_module = load('stable_row_query', ROOT / 'research/crt-stable-row-workspace/query.py')
    machine, actual = run_case(modules, pred, tree, workspace, query_module,
                              'four_axis_changing_precision', (5, 7, 3, 2),
                              (3, 3, 2, 2), (3, 2, 1, 1), 3)
    _, invalid = run_case(modules, pred, tree, workspace, query_module,
                          'invalid_left_padding', (7, 3), (3, 2), (7, 3), 3)
    result = {'status': 'PASS_CRT_WHOLE_TREE_STATE', 'source_count': source_count,
              'fixtures': [actual, invalid], 'geometric_budget': arithmetic_checks(tree),
              'negative_controls': controls(machine, modules, pred, tree, workspace, query_module),
              'fixed_owned_roles': 127, 'source_relative': True, 'kappa_change': None}
    if '--write-result' in sys.argv:
        (P / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        need(result == json.loads((P / 'RESULT.json').read_text()), 'frozen typed receipt')
    print(result['status'], 'four_axis_rows=' + str(actual['row_events']),
          'producer_calls=' + str(actual['producer_calls']),
          'retained=' + str(actual['retained_total']),
          'controls=' + str(len(result['negative_controls'])))


if __name__ == '__main__':
    main()
