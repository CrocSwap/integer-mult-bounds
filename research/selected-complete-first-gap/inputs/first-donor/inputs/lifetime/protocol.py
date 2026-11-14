"""Eight literal contacts for the selected owned1526 lifetime.

All Python graph construction is offline. Runtime transitions inspect symbols,
write individual cells and move each affected head at most one cell.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""
from dataclasses import dataclass
from functools import cache
from hashlib import sha1, sha256
from pathlib import Path
import json
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
TAPES = 44
OLD, CONTEXT, OWNED, SOURCE_WORK, TARGET_WORK, EXTERNAL = 0, 1, 2, 3, 4, 43
EXTERNAL_OWNERS = (1349, 728, 729, 730, 1515)
EVENTS = (28037, 28041, 28129, 28135, 28139, 28141, 28159, 37618)
SYMBOL = {'0': 0, '1': 1, '^': 2, '|': 3, '$': 4, '_': 6}
CHARACTER = {value: key for key, value in SYMBOL.items()}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def authenticate():
    pins = json.loads((HERE/'SOURCE-PINS.json').read_text())['files']
    for pin in pins:
        raw = (HERE/pin['local']).read_bytes()
        need(len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'],
             'retained source drift: '+pin['local'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == pin['blob'],
             'retained Git blob drift: '+pin['local'])
    return pins


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


@cache
def inputs():
    authenticate()
    saved = sys.dont_write_bytecode, sys.pycache_prefix
    try:
        with tempfile.TemporaryDirectory(prefix='lifetime-source-') as temp:
            sys.dont_write_bytecode = True
            sys.pycache_prefix = str(Path(temp)/'must-remain-absent')
            zero = load(HERE/'inputs/zero/zero.py', '_owned_lifetime_zero')
            add = load(HERE/'inputs/add/add.py', '_owned_lifetime_add')
            move = load(HERE/'inputs/move/adapter.py', '_owned_lifetime_move')
            # Build while all nested retained loaders have source-only cache policy.
            move.core()
            need(not Path(temp, 'must-remain-absent').exists(), 'cache policy drift')
    finally:
        sys.dont_write_bytecode, sys.pycache_prefix = saved
    return zero, add, move


class Relocate:
    """Fixed +2 port relabeling of supplied B1 primitive graphs."""
    def __init__(self, graph):
        self.graph = graph
        self.rules = graph.rules

    def state(self, stem):
        return self.graph.state(stem)

    def add(self, state, target, tests=(), writes=(), moves=()):
        def mapped(pairs):
            return tuple((t+2, value) for t, value in pairs)
        self.graph.add(state, target, mapped(tests), mapped(writes), mapped(moves))

    def jump(self, target, moves=()):
        return self.graph.jump(target, tuple((t+2, delta) for t, delta in moves))

    def rewind(self, tape, target, erase=False):
        return self.graph.rewind(tape+2, target, erase=erase)


def home_transfer(g, work, gather, after):
    """Copy the single complete owned HOME; successful scatter retires work."""
    cleanup = g.rewind(OWNED, g.rewind(work, after, erase=not gather))
    end = g.state('owned-dollar')
    g.add(end, cleanup, tests=((OWNED, '$'),), moves=((OWNED, -1),))
    loop = g.state('owned-gather' if gather else 'owned-scatter')
    boundary = ((OWNED, '|'),) if gather else ((OWNED, '|'), (work, '|'))
    g.add(loop, end, tests=boundary, writes=((work, '|'),) if gather else (),
          moves=((OWNED, 1),))
    for bit in '01':
        if gather:
            g.add(loop, loop, tests=((OWNED, bit),), writes=((work, bit),),
                  moves=((OWNED, 1), (work, 1)))
        else:
            for output in '01':
                g.add(loop, loop, tests=((OWNED, bit), (work, output)),
                      writes=((OWNED, output),), moves=((OWNED, 1), (work, 1)))
    return g.jump(loop, ((OWNED, 1), (work, 1)))


def bank_transfer(g, selected, work, gather, after):
    """Scan every field of the fixed five-owner bank, then return its head."""
    need(type(selected) is int and 0 <= selected < 5, 'fixed external home slot')
    cleanup = g.rewind(EXTERNAL, g.rewind(work, after, erase=not gather))
    tail = g.state('external-dollar')
    g.add(tail, cleanup, tests=((EXTERNAL, '$'),))
    next_state = tail
    for index in range(4, -1, -1):
        active = index == selected
        loop = g.state('bank-gather' if gather else 'bank-scatter')
        boundary = ((EXTERNAL, '|'),)
        if active and not gather:
            boundary += ((work, '|'),)
        g.add(loop, next_state, tests=boundary,
              writes=((work, '|'),) if active and gather else (),
              moves=((EXTERNAL, 1),))
        for bit in '01':
            if not active:
                g.add(loop, loop, tests=((EXTERNAL, bit),), moves=((EXTERNAL, 1),))
            elif gather:
                g.add(loop, loop, tests=((EXTERNAL, bit),), writes=((work, bit),),
                      moves=((EXTERNAL, 1), (work, 1)))
            else:
                for output in '01':
                    g.add(loop, loop, tests=((EXTERNAL, bit), (work, output)),
                          writes=((EXTERNAL, output),), moves=((EXTERNAL, 1), (work, 1)))
        next_state = loop
    return g.jump(next_state, ((EXTERNAL, 1), (work, 1)))


def shifted_heads(g, direction, after):
    for tape in range(42, 2, -1):
        after = g.jump(after, ((tape, direction),))
    return after


def clear_work(g, tape, after):
    """Physically traverse and erase a complete work field from its origin."""
    home = g.rewind(tape, after)
    loop = g.state('erase-read-only-work-copy')
    for bit in '01':
        g.add(loop, loop, tests=((tape, bit),), writes=((tape, '_'),),
              moves=((tape, 1),))
    g.add(loop, home, tests=((tape, '|'),), writes=((tape, '_'),))
    return g.jump(loop, ((tape, 1),))


def embed_zero(g, module, live_return, retired_return):
    original, labels = module.compile_zero()
    code = module.hardware_code(original)
    names = [g.state('OLD23-zero') for _ in code]
    reject = g.state('zero-reject')
    g.rules[reject] = []
    for pc, instruction in enumerate(code):
        state = names[pc]
        g.rules.setdefault(state, [])
        op, *args = instruction
        nxt = names[pc+1] if pc+1 < len(code) else reject
        if op == 'R':
            for symbol, destination in args[1].items():
                g.add(state, names[destination], tests=((args[0], CHARACTER[symbol]),))
        elif op == 'W':
            g.add(state, nxt, writes=((args[0], CHARACTER[args[1]]),))
        elif op == 'M':
            g.add(state, nxt, moves=((args[0], args[1]),))
        elif op == 'J':
            g.add(state, names[args[0]])
        elif op == 'H':
            destination = {'LIVE_HOME': live_return, 'RETIRED_HOME': retired_return,
                           'REJECT': reject}[args[0]]
            g.add(state, destination)
        else:
            raise ValueError('nonliteral frozen zero instruction')
    return names[labels['ENTER']], names[labels['CLEAR']], len(code)


def compile_protocol(*, mutation=None):
    """One immutable table with eight named entry/return interfaces.

    A mutation is verifier-only and never accepted by the default constructor.
    """
    zero, add, move = inputs()
    g = add.D.Graph()
    returned = {}
    for event in EVENTS:
        name = g.state('RETURN-'+str(event))
        g.add(name, 'HALT')
        returned[event] = name
    init_done = shifted_heads(g, -1, returned[28037])
    clear_done = shifted_heads(g, 1, returned[37618])
    init, clear, zero_size = embed_zero(g, zero, init_done, clear_done)
    entries = {28037: init, 37618: clear}
    stages = {}
    proxy = Relocate(g)
    for event, external_slot in ((28041, 0), (28129, 1), (28135, 2), (28139, 3)):
        cleanup = clear_work(g, SOURCE_WORK, returned[event])
        scatter = home_transfer(g, TARGET_WORK, False, cleanup)
        markers = {}
        action = 'ADD' if mutation == 'wrong-first-sign' and event == 28041 else 'SUB'
        invoke = add.primitive(proxy, action, 2, scatter, markers)
        gather_owned = home_transfer(g, TARGET_WORK, True, invoke)
        entries[event] = bank_transfer(g, external_slot, SOURCE_WORK, True, gather_owned)
        stages[event] = markers | {'scatter': scatter}
    event = 28141
    scatter = home_transfer(g, SOURCE_WORK, False, returned[event])
    markers = {}
    move_mutation = mutation if mutation in ('wrong_phase', 'omit_second_C', 'weak_cutoff') else None
    invoke = move.primitive(proxy, 'MOVE28141', 1, scatter,
                            mutation=move_mutation, stages=markers)
    entries[event] = home_transfer(g, SOURCE_WORK, True, invoke)
    stages[event] = markers | {'scatter': scatter}
    event = 28159
    cleanup = clear_work(g, SOURCE_WORK, returned[event])
    scatter = bank_transfer(g, 4, TARGET_WORK, False, cleanup)
    markers = {}
    invoke = add.primitive(proxy, 'ADD', 2, scatter, markers)
    gather_target = bank_transfer(g, 4, TARGET_WORK, True, invoke)
    entries[event] = home_transfer(g, SOURCE_WORK, True, gather_target)
    stages[event] = markers | {'scatter': scatter}
    g.start = entries[28037]
    g.execution_start = g.start
    g.validate()
    all_ports = {t for rules in g.rules.values() for rule in rules
                 for pairs in (rule.tests, rule.writes, rule.moves) for t, _ in pairs}
    need(all_ports == set(range(TAPES)), 'fixed44-port inventory')
    return g, {'entries': entries, 'returns': returned, 'stages': stages,
               'zero_locations': zero_size, 'fixed_tapes': TAPES}


def digest(graph):
    value = [(name, [(r.tests, r.writes, r.moves, r.target) for r in rules])
             for name, rules in graph.rules.items()]
    return sha256(json.dumps(value, separators=(',', ':')).encode()).hexdigest()


class Rejected(ValueError):
    pass


@dataclass
class State:
    tapes: list
    heads: list
    origins: list
    lows: list
    highs: list
    writes: list
    steps: int = 0

    def clone(self):
        return State([bytearray(t) for t in self.tapes], self.heads.copy(),
                     self.origins.copy(), self.lows.copy(), self.highs.copy(),
                     self.writes.copy(), self.steps)


class Program:
    """Literal CPU; all bounds/oracles are external read-only observations.

    Fast cases preserve the exact one-Graph-transition semantics. General
    finite rules are matched against all pre-transition scanned symbols.
    """
    def __init__(self, graph):
        names = list(graph.rules)
        self.labels = {name: i for i, name in enumerate(names)}
        self.labels['HALT'] = -1
        self.start = self.labels[graph.start]
        self.rows = []
        for name in names:
            rules = [(tuple((t, SYMBOL[s]) for t, s in r.tests),
                      tuple((t, SYMBOL[s]) for t, s in r.writes), r.moves,
                      self.labels[r.target]) for r in graph.rules[name]]
            if rules and all(len(r[0]) == 1 and not r[1] and not r[2] for r in rules) and len({r[0][0][0] for r in rules}) == 1:
                branch = [-2]*7
                for rule in rules:
                    branch[rule[0][0][1]] = rule[3]
                self.rows.append((0, rules[0][0][0][0], branch))
            elif len(rules) == 1 and not rules[0][0]:
                _, writes, moves, nxt = rules[0]
                if len(writes) == 1 and not moves:
                    self.rows.append((1, writes[0][0], (writes[0][1], nxt)))
                elif len(moves) == 1 and not writes:
                    self.rows.append((2, moves[0][0], (moves[0][1], nxt)))
                elif not moves and not writes:
                    self.rows.append((3, nxt, None))
                else:
                    self.rows.append((4, rules, None))
            else:
                self.rows.append((4, rules, None))

    def run(self, state, *, start=None, stop=None, budget=150_000_000):
        need(len(state.tapes) == TAPES and len({id(t) for t in state.tapes}) == TAPES,
             'all physical tape owners must be distinct')
        pc = self.start if start is None else self.labels[start]
        stop_pc = None if stop is None else self.labels[stop]
        rows, tapes, heads = self.rows, state.tapes, state.heads
        lows, highs, writes = state.lows, state.highs, state.writes
        limit = state.steps+budget
        while pc != -1 and pc != stop_pc:
            op, tape, arg = rows[pc]
            if op == 0:
                pc = arg[tapes[tape][heads[tape]]]
                if pc == -2:
                    raise Rejected('literal scanned-symbol rejection')
            elif op == 1:
                value, pc = arg
                need(heads[tape] != state.origins[tape] or value == 2,
                     'permanent origin overwrite')
                tapes[tape][heads[tape]] = value
                writes[tape] += 1
            elif op == 2:
                delta, pc = arg
                need(delta in (-1, 1), 'nonunit emitted move')
                heads[tape] += delta
                need(0 <= heads[tape] < len(tapes[tape]), 'finite verifier capacity')
                lows[tape] = min(lows[tape], heads[tape])
                highs[tape] = max(highs[tape], heads[tape])
            elif op == 3:
                pc = tape
            else:
                found = None
                for rule in tape:
                    if all(tapes[t][heads[t]] == symbol for t, symbol in rule[0]):
                        need(found is None, 'nondeterministic literal rules')
                        found = rule
                if found is None:
                    raise Rejected('literal scanned-symbol rejection')
                for t, value in found[1]:
                    need(heads[t] != state.origins[t] or value == 2,
                         'permanent origin overwrite')
                    tapes[t][heads[t]] = value
                    writes[t] += 1
                for t, delta in found[2]:
                    need(delta in (-1, 1), 'nonunit emitted move')
                    heads[t] += delta
                    need(0 <= heads[t] < len(tapes[t]), 'finite verifier capacity')
                    lows[t] = min(lows[t], heads[t])
                    highs[t] = max(highs[t], heads[t])
                pc = found[3]
            state.steps += 1
            need(state.steps <= limit, 'finite execution budget')
        return state
