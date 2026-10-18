"""Independent executable boundary controls; no Lean theorem is inferred here."""
import itertools

STATES = (0, 1, 2)


def need(ok, why):
    if not ok:
        raise ValueError(why)


def symbols(q, states=STATES):
    op, *args = q
    if op == 'push':
        k, f, rest = args
        return {(k, f(v)) for v in states} | symbols(rest, states)
    if op in ('peek', 'pop'):
        return symbols(args[2], states)
    if op == 'load':
        return symbols(args[1], states)
    if op == 'branch':
        return symbols(args[1], states) | symbols(args[2], states)
    return set()


def depth(q):
    op, *args = q
    if op in ('push', 'peek', 'pop'):
        return 1 + depth(args[2])
    if op == 'load':
        return 1 + depth(args[1])
    if op == 'branch':
        return 1 + max(depth(args[1]), depth(args[2]))
    return 1


def execute(q, state, stacks, allowed):
    """Literal one-label interpreter, checking every primitive prefix."""
    work = 0
    while True:
        work += 1
        op, *args = q
        if op == 'push':
            k, f, q = args
            stacks[k].insert(0, f(state))
        elif op in ('peek', 'pop'):
            k, f, q = args
            head = stacks[k][0] if stacks[k] else None
            state = f(state, head)
            if op == 'pop' and stacks[k]:
                stacks[k].pop(0)
        elif op == 'load':
            f, q = args
            state = f(state)
        elif op == 'branch':
            f, left, right = args
            q = left if f(state) else right
        elif op == 'goto':
            return args[0](state), state, work
        elif op == 'halt':
            return None, state, work
        else:
            raise ValueError('unknown instruction')
        need(state in STATES, 'state left declared finite control')
        need(all((k, x) in allowed for k, xs in stacks.items() for x in xs),
             'primitive prefix leaves the admitted alphabet')


def fixture():
    # Noninput symbols are natural numbers, not a declared finite alphabet.
    scan = ('peek', 'input', lambda v, x: 2 if x is None else int(x),
            ('branch', lambda v: v == 2, ('goto', lambda v: 'drain'),
             ('push', 'work', lambda v: 1000 + v,
              ('pop', 'input', lambda v, x: v, ('goto', lambda v: 'scan')))))
    drain = ('pop', 'work', lambda v, x: 2 if x is None else x - 1000,
             ('branch', lambda v: v == 2, ('halt',),
              ('load', lambda v: v, ('push', 'output', lambda v: bool(v),
                                    ('goto', lambda v: 'drain')))))
    return {'scan': scan, 'drain': drain}


def run_checks():
    program = fixture()
    initial = {('input', False), ('input', True)}
    allowed = initial | set().union(*(symbols(q) for q in program.values()))
    bound = max(depth(q) for q in program.values())
    cases = prefixes = moves = 0
    for length in range(9):
        for word in itertools.product((False, True), repeat=length):
            for entry_state in STATES:
                state, label = entry_state, 'scan'
                stacks = {'input': list(word), 'work': [], 'output': []}
                steps = total = 0
                while label is not None:
                    q = program[label]
                    label, state, count = execute(q, state, stacks, allowed)
                    need(count <= depth(q) <= bound, 'fixed primitive-step bound')
                    steps += 1
                    total += count
                    need(steps <= 2 * len(word) + 3, 'fixture termination')
                need(stacks == {'input': [], 'work': [], 'output': list(word)},
                     'complete output and scratch endpoint')
                need(total <= bound * steps, 'run resource composition')
                cases += 1
                prefixes += steps
                moves += total
    rejected = []

    def reject(name, thunk):
        try:
            thunk()
        except ValueError:
            rejected.append(name)
        else:
            raise ValueError('control accepted: ' + name)

    def one(q, state, stacks, alphabet):
        return execute(q, state, stacks, alphabet)

    reject('omit-state-range', lambda: one(('push', 'work', lambda v: 1000+v, ('halt',)),
           1, {'input': [], 'work': [], 'output': []}, {('work', 1000)}))
    reject('omit-label', lambda: one(program['drain'], 0,
           {'input': [], 'work': [1000], 'output': []}, initial | symbols(program['scan'])))
    reject('omit-false-branch', lambda: one(('branch', lambda v: False, ('halt',),
           ('push', 'work', lambda v: 9999, ('halt',))), 0,
           {'input': [], 'work': [], 'output': []}, allowed))
    reject('unadmitted-dirty-initial-stack', lambda: one(('load', lambda v:v, ('halt',)), 0,
           {'input': [], 'work': [9999], 'output': []}, allowed))
    reject('drop-finite-control', lambda: one(('load', lambda v:v+1, ('goto', lambda v:'scan')),
           2, {'input': [], 'work': [], 'output': []}, allowed))
    # Finite labels alone do not bound callback ranges when state is unbounded.
    unbounded = {1000+n for n in range(1001)}
    need(len(unbounded) == 1001 and 2000 not in {1000,1001,1002}, 'unbounded-state countermodel')
    # Counting macro steps as one primitive loses even a fixed straight-line cost.
    q = ('halt',)
    for _ in range(31):
        q = ('load', lambda v:v, q)
    _, _, actual = execute(q, 0, {'input': [], 'work': [], 'output': []}, allowed)
    reject('unit-macro-cost', lambda: need(actual <= 1, '32 primitive actions in one macro step'))
    return dict(status='PASS_FINITE_MODELS_NOT_KERNEL', input_cases=cases,
                macro_prefixes=prefixes, primitive_actions=moves,
                alphabet_size=len(allowed), fixed_primitive_bound=bound,
                negative_controls=rejected, infinite_control_distinct_symbols=len(unbounded))


if __name__ == '__main__':
    import json
    print(json.dumps(run_checks(), sort_keys=True))
