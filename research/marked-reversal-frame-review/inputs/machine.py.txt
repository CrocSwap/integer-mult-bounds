"""Finite two-tape rules for a fixed sampler, with one owned delimiter cell.

The interpreter's position and step counters are observations, never rule inputs.
New construction produced by Nick Petalas. Apache-2.0.
"""
from dataclasses import dataclass

PERIOD = 156
ENTRY = ('entry', 0, 0)
PREPARE = ('prepare', 0, 0)
HALT = ('halt', 0, 0)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def add_rule(rules, key, value):
    require(key not in rules, 'duplicate rule key')
    rules[key] = value


def forward_rules(table, phases, rules):
    """One right-moving step, including output XOR on a leaf edge."""
    for state, phase in enumerate(phases):
        for bit in (0, 1):
            target = table[state][bit]
            next_phase = (phase + 1) % PERIOD
            mode = 'back' if target >= 312 else 'forward'
            for accumulator in range(4):
                out = accumulator ^ (target - 312) if target >= 312 else accumulator
                key = (('forward', phase, state), bit, accumulator)
                add_rule(rules, key, ((mode, next_phase, target), bit, out, 1))


def reverse_rules(table, phases, rules):
    """Move left, then apply the predecessor's phase-and-coin inverse."""
    targets = set()
    for state, phase in enumerate(phases):
        for bit in (0, 1):
            target = table[state][bit]
            next_phase = (phase + 1) % PERIOD
            targets.add((next_phase, target))
            for accumulator in range(4):
                key = (('read', next_phase, target), bit, accumulator)
                value = (('back', phase, state), bit, accumulator, 0)
                add_rule(rules, key, value)
    require((0, 0) in targets, 'root must be a recurrent internal target')
    for phase, state in sorted(targets):
        for bit in (0, 1):
            for accumulator in range(4):
                key = (('back', phase, state), bit, accumulator)
                add_rule(rules, key, (('read', phase, state), bit, accumulator, -1))
    return len(targets)


def build_rules(table, counts):
    require(len(table) == 312 and len(counts) == PERIOD, 'fixed graph dimensions')
    phases = tuple(p for p, count in enumerate(counts) for _ in range(count))
    require(len(phases) == 312, 'phase layout')
    rules = {}
    forward_rules(table, phases, rules)
    targets = reverse_rules(table, phases, rules)
    for accumulator in range(4):
        for bit in (0, 1):
            add_rule(rules, (ENTRY, bit, accumulator), (PREPARE, bit, accumulator, -1))
        add_rule(rules, (PREPARE, '_', accumulator),
                 (('forward', 0, 0), '#', accumulator, 1))
        add_rule(rules, (('read', 0, 0), '#', accumulator),
                 (HALT, '_', accumulator, 1))
    return rules, targets


@dataclass(frozen=True)
class Trace:
    output: int
    steps: int
    head_moves: int
    marker_writes: int
    max_excursion: int
    root_revisits: int


def execute(rules, bits, accumulator=0, start=3, max_steps=4000):
    """Bounded observer for local rules. No position or time enters a rule key."""
    require(1 <= len(bits) <= 1024 and all(type(x) is int and x in (0, 1) for x in bits),
            'observer binary fixture length 1..1024')
    require(type(accumulator) is int and 0 <= accumulator < 4, 'two-bit output cell')
    require(type(start) is int and 1 <= start <= 64, 'observer start 1..64')
    require(type(max_steps) is int and 1 <= max_steps <= 10000, 'observer step bound')
    tape = ['dirty'] * (start - 1) + ['_'] + list(bits)
    initial = tuple(tape)
    state, head, output = ENTRY, start, accumulator
    moves = writes = excursion = revisits = 0
    for step in range(1, max_steps + 1):
        require(0 <= head < len(tape), 'observer fixture exhausted')
        key = (state, tape[head], output)
        require(key in rules, 'undefined machine transition')
        state, symbol, output, move = rules[key]
        writes += symbol != tape[head]
        tape[head] = symbol
        head += move
        moves += abs(move)
        excursion = max(excursion, head - start)
        revisits += state == ('back', 0, 0) and head != start
        if state == HALT:
            require(head == start and tuple(tape) == initial, 'head or tape not restored')
            return Trace(output, step, moves, writes, excursion, revisits)
    raise ValueError('observer step bound exhausted')
