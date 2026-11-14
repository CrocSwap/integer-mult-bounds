"""Literal fixed-tape scan graphs; no indexed payload access in execution.

Alphabet is fixed. K, all homes and all service choices are frozen in states.
F is never stored in a runtime counter. New material: Apache-2.0.
"""
from dataclasses import dataclass

ALPHABET = '_01^|$'


class Tape:
    def __init__(self, text='^'):
        self.cells = list(text)
        self.head = 0
        self.peak = len(self.cells)
        self.visited = {0}

    def read(self):
        self.visited.add(self.head)
        self.peak = max(self.peak,self.head+1)
        return self.cells[self.head] if self.head < len(self.cells) else '_'

    def write(self, value):
        self.visited.add(self.head)
        if self.head >= len(self.cells):
            self.cells.extend('_' for _ in range(self.head+1-len(self.cells)))
        self.cells[self.head] = value
        self.peak = max(self.peak, len(self.cells))

    def move(self, delta):
        if delta not in (-1,0,1):
            raise ValueError('one physical transition moves at most one cell')
        if self.head+delta < 0:
            raise ValueError('head crossed permanent origin')
        self.head += delta
        self.visited.add(self.head)
        self.peak = max(self.peak,self.head+1)

    def contents(self):
        return ''.join(self.cells)


@dataclass(frozen=True)
class Rule:
    tests: tuple
    writes: tuple
    moves: tuple
    target: str


class Graph:
    def __init__(self):
        self.rules = {}
        self.serial = 0
        self.start = None
        self.execution_start = None
        self.checkpoints = {}

    def state(self, stem):
        result = f'{stem}.{self.serial}'
        self.serial += 1
        return result

    def add(self, state, target, tests=(), writes=(), moves=()):
        self.rules.setdefault(state, []).append(Rule(tuple(tests), tuple(writes),
                                                    tuple(moves), target))

    def jump(self, target, moves=()):
        state = self.state('jump')
        self.add(state, target, moves=moves)
        return state

    def rewind(self, tape, target, erase=False):
        state = self.state('erase' if erase else 'rewind')
        self.add(state, target, tests=((tape, '^'),))
        for symbol in ALPHABET.replace('^', ''):
            self.add(state, state, tests=((tape, symbol),),
                     writes=((tape, '_'),) if erase else (), moves=((tape, -1),))
        return state

    def validate(self):
        # Exact symbolic determinism: two patterns overlap iff every shared
        # tested tape has the same symbol. No wildcard expansion is needed.
        for state, rules in self.rules.items():
            for i, a in enumerate(rules):
                if a.target not in self.rules and a.target != 'HALT':
                    raise ValueError('undefined graph continuation')
                for b in rules[:i]:
                    left, right = dict(a.tests), dict(b.tests)
                    if all(left[t] == right[t] for t in left.keys() & right.keys()):
                        raise ValueError('nondeterministic graph state '+state)

    def run(self, tapes, limit=10000000, checkpoint=None, start=None):
        state, steps = self.start if start is None else start, 0
        while state != 'HALT':
            if checkpoint and state in self.checkpoints:
                checkpoint(self.checkpoints[state], tapes)
            if steps >= limit:
                raise ValueError('literal graph execution capacity')
            matches = [r for r in self.rules[state]
                       if all(tapes[t].read() == value for t, value in r.tests)]
            if len(matches) != 1:
                raise ValueError('malformed tape or nondeterministic transition '+state)
            rule, = matches
            for tape, value in rule.writes:
                tapes[tape].write(value)
            for tape, delta in rule.moves:
                tapes[tape].move(delta)
            state, steps = rule.target, steps+1
        if checkpoint and 'HALT' in self.checkpoints:
            checkpoint(self.checkpoints['HALT'], tapes)
        return steps


def service(graph, name, arity, target):
    """Four small supplied primitive graphs used ONLY by finite fixtures.

    Real scientific scalar/route/leaf graphs are still premises of the theorem.
    Tapes 1,2 are operands; tape 3 is retained private primitive scratch.
    """
    if name == 'REV':
        if arity != 1:
            raise ValueError('unary reversal')
        cleanup = graph.rewind(3, target, erase=True)
        back_operand = graph.rewind(1, cleanup)
        copy = graph.state('reverse-install')
        graph.add(copy, back_operand, tests=((3, '|'),), writes=((1, '|'),))
        for bit in '01':
            graph.add(copy, copy, tests=((3, bit),), writes=((1, bit),),
                      moves=((1, 1), (3, 1)))
        install = graph.jump(copy, ((1, 1), (3, 1)))
        rewind_scratch = graph.rewind(3, install)
        reverse = graph.state('reverse-copy')
        graph.add(reverse, rewind_scratch, tests=((1, '^'),), writes=((3, '|'),))
        for bit in '01':
            graph.add(reverse, reverse, tests=((1, bit),), writes=((3, bit),),
                      moves=((1, -1), (3, 1)))
        begin_reverse = graph.jump(reverse, ((1, -1), (3, 1)))
        seek = graph.state('reverse-seek')
        graph.add(seek, begin_reverse, tests=((1, '|'),))
        for bit in '01':
            graph.add(seek, seek, tests=((1, bit),), moves=((1, 1),))
        return graph.jump(seek, ((1, 1),))
    if name == 'FIRST':
        if arity != 1:
            raise ValueError('unary leaf fixture')
        at = graph.state('first-bit')
        for bit in '01':
            graph.add(at, target, tests=((1, bit),), writes=((1, str(1-int(bit))),),
                      moves=((1, -1),))
        return graph.jump(at, ((1, 1),))
    if name not in ('ZERO', 'NOT', 'XOR') or arity != (2 if name == 'XOR' else 1):
        raise ValueError('missing supplied primitive graph')
    cleanup = target
    for tape in range(arity, 0, -1):
        cleanup = graph.rewind(tape, cleanup)
    loop = graph.state('primitive-'+name)
    graph.add(loop, cleanup, tests=tuple((t, '|') for t in range(1, arity+1)))
    if name == 'XOR':
        for a in '01':
            for b in '01':
                graph.add(loop, loop, tests=((1, a), (2, b)),
                          writes=((2, str(int(a)^int(b))),), moves=((1, 1), (2, 1)))
    else:
        for bit in '01':
            graph.add(loop, loop, tests=((1, bit),),
                      writes=((1, '0' if name == 'ZERO' else str(1-int(bit))),),
                      moves=((1, 1),))
    return graph.jump(loop, tuple((t, 1) for t in range(1, arity+1)))


def scan(graph, homes, selected, gather, target):
    """Unroll finite home order; scan arbitrary F only by field delimiters."""
    next_state = graph.rewind(0, target)
    for home in range(homes-1, -1, -1):
        work = selected.get(home)
        after = next_state
        loop = graph.state('gather' if gather else 'return')
        if work:
            graph.add(loop, after, tests=((0, '|'),) if gather else ((0, '|'), (work, '|')),
                      writes=((work, '|'),) if gather else (), moves=((0, 1),))
        else:
            graph.add(loop, after, tests=((0, '|'),), moves=((0, 1),))
        for bit in '01':
            if not work:
                graph.add(loop, loop, tests=((0, bit),), moves=((0, 1),))
            elif gather:
                graph.add(loop, loop, tests=((0, bit),), writes=((work, bit),),
                          moves=((0, 1), (work, 1)))
            else:
                for output in '01':
                    graph.add(loop, loop, tests=((0, bit), (work, output)),
                              writes=((0, output),), moves=((0, 1), (work, 1)))
        next_state = graph.jump(loop, ((work, 1),)) if work else loop
    return graph.jump(next_state, ((0, 1),))


def reserve(graph, extra_homes, target):
    """Append full zero homes by copying first-field extent, without F arithmetic."""
    if not extra_homes:
        return target
    return_home = graph.rewind(0, target)
    finish = graph.state('reserve-finish')
    graph.add(finish, return_home, writes=((0, '$'),))
    next_state = graph.rewind(3, finish, erase=True)
    for position in range(extra_homes-1,-1,-1):
        loop = graph.state('reserve-zero-home')
        graph.add(loop, loop, tests=((3, '0'),), writes=((0, '0'),), moves=((0, 1),(3, 1)))
        graph.add(loop, next_state, tests=((3, '|'),), writes=((0, '|'),), moves=((0, 1),))
        begin = graph.jump(loop, ((3, 1),))
        next_state = graph.rewind(3, begin) if position else begin
    seek = graph.state('reserve-seek-end')
    graph.add(seek, next_state, tests=((0, '$'),))
    for symbol in '^01|':
        graph.add(seek, seek, tests=((0, symbol),), moves=((0, 1),))
    rewind_template = graph.rewind(3, seek)
    rewind_home = graph.rewind(0, rewind_template)
    copy = graph.state('reserve-copy-extent')
    for bit in '01':
        graph.add(copy, copy, tests=((0, bit),), writes=((3, '0'),), moves=((0, 1),(3, 1)))
    graph.add(copy, rewind_home, tests=((0, '|'),), writes=((3, '|'),))
    return graph.jump(copy, ((0, 1),(3, 1)))


def compile_graph(events, owners, primitive=service, productive_count=None):
    """Return a real transition graph on four tapes for the fixture family.

    General theorem: replace primitive by supplied finite graphs using m
    scratch tapes; tape count is 1+b+m, independently of Q,K,F.
    """
    graph, next_state = Graph(), 'HALT'
    home_index = {owner: i for i, owner in enumerate(owners)}
    if len(home_index) != len(owners):
        raise ValueError('permanent home owner identities must be distinct')
    for index in range(len(events)-1, -1, -1):
        event = events[index]
        if not event.service:
            continue
        graph.checkpoints[next_state] = index
        if not 1 <= len(event.owners) <= 2 or len(set(event.owners)) != len(event.owners):
            raise ValueError('bounded distinct physical operands')
        selected = {home_index[owner]: i+1 for i, owner in enumerate(event.owners)}
        cleanup = next_state
        for tape in range(len(event.owners), 0, -1):
            cleanup = graph.rewind(tape, cleanup, erase=True)
        scatter = scan(graph, len(owners), selected, False, cleanup)
        invoke = primitive(graph, event.service, len(event.owners), scatter)
        origin = invoke
        for tape in range(len(event.owners), 0, -1):
            origin = graph.rewind(tape, origin)
        next_state = scan(graph, len(owners), selected, True, origin)
    graph.execution_start = next_state
    productive_count = len(owners) if productive_count is None else productive_count
    if not 1 <= productive_count <= len(owners):
        raise ValueError('positive productive count within permanent bank')
    graph.start = reserve(graph,len(owners)-productive_count,next_state)
    graph.validate()
    return graph


def initial_tapes(payloads, home_count, preformatted=False):
    if not payloads or len({len(x) for x in payloads}) != 1 or not payloads[0]:
        raise ValueError('positive common full field format')
    if len(payloads) > home_count or any(set(x)-set('01') for x in payloads):
        raise ValueError('binary productive bank in declared homes')
    # Only productive fields are supplied. New private extents are prepared
    # by the literal reserve graph. Optional preformatting is for fault tests.
    fields = list(payloads)
    if preformatted:
        fields += ['0'*len(payloads[0])]*(home_count-len(payloads))
    return [Tape('^'+'|'.join(fields)+'|$'), Tape(), Tape(), Tape()]


def decoded(tapes, home_count):
    raw = tapes[0].contents()
    if raw[0] != '^' or not raw.endswith('|$'):
        raise ValueError('home boundaries changed')
    fields = tuple(raw[1:-2].split('|'))
    if len(fields) != home_count:
        raise ValueError('permanent home count changed')
    return fields
