"""Two-tape parking controller. Apache-2.0; ywz65 with OpenAI Codex.

Only (finite state, two scanned symbols) selects a transition. Coordinates,
step limits and counters belong to the simulator, not the controller.
"""
from itertools import product

ALPHABET = tuple('_01^$FR')
STATES = ('begin', 'end', 'end_check', 'push', 'push_copy', 'push_rewind',
          'pop', 'pop_measure', 'pop_return', 'pop_copy')
HALTS = ('done', 'reject')

def transition_table():
    table = {(s, a, b): ('reject', (None, None), (0, 0))
             for s, a, b in product(STATES, ALPHABET, ALPHABET)}
    def put(s, a, b, nxt, writes=(None, None), moves=(0, 0)):
        table[s, a, b] = nxt, writes, moves
    for b in ALPHABET:
        put('begin', '_', b, 'done', ('F', None), (1, 0))
        put('end', '_', b, 'end_check', moves=(-1, 0))
        for a in ALPHABET:
            put('end_check', a, b, 'reject', moves=(1, 0))
        put('end_check', 'F', b, 'done', ('_', None))
    for b in '01$':
        put('push', '_', b, 'push_copy', ('R', None), (1, 0))
    for b in '01':
        put('push_copy', '_', b, 'push_copy', (b, '_'), (1, 1))
    put('push_copy', '_', '$', 'push_rewind', (None, '_'), (0, -1))
    put('push_rewind', '_', '_', 'push_rewind', moves=(0, -1))
    put('push_rewind', '_', '^', 'done', moves=(0, 1))
    put('pop', '_', '_', 'pop_measure', moves=(-1, 0))
    for a in '01':
        put('pop_measure', a, '_', 'pop_measure', moves=(-1, 1))
        put('pop_return', a, '_', 'pop_return', moves=(1, 0))
        put('pop_copy', a, '_', 'pop_copy', ('_', a), (-1, -1))
    put('pop_measure', 'R', '_', 'pop_return', moves=(1, 0))
    put('pop_measure', 'F', '_', 'reject', moves=(1, 0))
    put('pop_return', '_', '_', 'pop_copy', (None, '$'), (-1, -1))
    put('pop_copy', 'R', '^', 'done', ('_', None), (0, 1))
    return table

TABLE = transition_table()

def need(ok, message):
    if not ok:
        raise ValueError(message)

def certify(table):
    need(set(table) == set(product(STATES, ALPHABET, ALPHABET)), 'complete finite table')
    for key, (nxt, writes, moves) in table.items():
        need(nxt in STATES + HALTS, 'finite next state')
        need(len(writes) == len(moves) == 2, 'exactly two tapes')
        need(all(x is None or x in ALPHABET for x in writes), 'finite writes')
        need(all(type(x) is int and x in (-1, 0, 1) for x in moves), 'unit head moves')
    return len(table)

class Machine:
    def __init__(self, parking=None, packet=None, heads=(0, 0), table=None):
        self.tapes = [dict(parking or {}), dict(packet or {})]
        self.heads = list(heads)
        self.table = TABLE if table is None else table
        self.state = 'done'
        self.counts = dict(steps=0, reads=0, writes=0, moves=0)
        self.visited = [set(), set()]
        self.transitions = set()

    def step(self):
        pair = tuple(t.get(h, '_') for t, h in zip(self.tapes, self.heads))
        key = (self.state, *pair)
        nxt, writes, moves = self.table[key]
        self.transitions.add(key)
        self.counts['steps'] += 1
        self.counts['reads'] += 2
        for k in (0, 1):
            h = self.heads[k]
            self.visited[k].add(h)
            if writes[k] is not None:
                self.counts['writes'] += 1
                if writes[k] == '_':
                    self.tapes[k].pop(h, None)
                else:
                    self.tapes[k][h] = writes[k]
            self.heads[k] += moves[k]
            self.counts['moves'] += abs(moves[k])
        self.state = nxt

    def run(self, entry, limit=1000000):
        need(entry in ('begin', 'end', 'push', 'pop'), 'public entry')
        before = dict(self.counts)
        self.state = entry
        for _ in range(limit):
            self.step()
            if self.state in HALTS:
                return {k: self.counts[k] - before[k] for k in before}
        raise ValueError('test execution budget; not a controller counter')

def tariff(operation, n=0):
    if operation == 'begin':
        steps, writes, moves = 1, 1, 1
    elif operation == 'end':
        steps, writes, moves = 2, 1, 1
    elif operation == 'push':
        steps, writes, moves = 2*n+3, 2*n+2, 3*n+3
    elif operation == 'pop':
        steps, writes, moves = 3*n+4, 2*n+2, 5*n+5
    else:
        raise ValueError(operation)
    return dict(steps=steps, reads=2*steps, writes=writes, moves=moves)
