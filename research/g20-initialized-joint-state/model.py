"""Finite initialized joint-state construction for one fixed G20 column."""
from array import array

COEFFICIENTS = (-1, -4, -4, -4)
ACTIVE = (0, 2, 4, 7)
INACTIVE = (1, 3, 5, 6)
THRESHOLDS = tuple(range(-12, 1))
MAX_STATES = 1 << 15


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def transition(state: tuple, letter: int) -> tuple:
    values, comparison = state
    mask, bit = divmod(letter, 2)
    digit = sum(a * ((mask >> i) & 1) for i, a in enumerate(COEFFICIENTS))
    changed = mask if bit == 0 else mask ^ 15
    return (tuple((v + digit - j * bit) // 2
                  for v, j in zip(values, THRESHOLDS)),
            (comparison & ~changed) | (mask & changed))


class Tables:
    def __init__(self, states: list, edges: array, parents: list, incoming: list,
                 ranks: array, inverse: list, maxima: list):
        self.states = states
        self.edges = edges
        self.parents = parents
        self.incoming = incoming
        self.ranks = ranks
        self.inverse = inverse
        self.maxima = maxima


def construct() -> Tables:
    states = [((0,) * 13, 15)]
    index = {states[0]: 0}
    parents, incoming, edges = [-1], [-1], array('H')
    for source in range(MAX_STATES):
        if source == len(states):
            break
        for letter in range(32):
            target = transition(states[source], letter)
            if target not in index:
                need(len(states) < MAX_STATES, '15-bit state capacity exhausted')
                index[target] = len(states)
                states.append(target)
                parents.append(source)
                incoming.append(letter)
            edges.append(index[target])
    need(len(edges) == 32 * len(states), 'complete closure')
    ranks = array('B', [0]) * len(edges)
    inverse, maxima = [], []
    for letter in range(32):
        fibers = {}
        for source in range(len(states)):
            target = edges[32 * source + letter]
            fiber = fibers.setdefault(target, [])
            need(len(fiber) < 256, '8-bit active history capacity exhausted')
            ranks[32 * source + letter] = len(fiber)
            fiber.append(source)
        inverse.append({target: tuple(fiber) for target, fiber in fibers.items()})
        maxima.append(max(map(len, fibers.values())))
    return Tables(states, edges, parents, incoming, ranks, inverse, maxima)


def check_rows(rows: tuple) -> None:
    need(type(rows) is tuple and len(rows) <= 4097, 'bounded tuple of rows')
    for row in rows:
        need(type(row) is tuple and len(row) == 9, 'nine row channels')
        need(all(type(b) is int and b in (0, 1) for b in row), 'binary row')


def split_row(row: tuple) -> tuple:
    active = sum(row[j] << i for i, j in enumerate(ACTIVE))
    inactive = sum(row[j] << i for i, j in enumerate(INACTIVE))
    return 2 * active + row[8], inactive, row[8]


def forward(tables: Tables, rows: tuple) -> tuple:
    state, inactive, residue, radix_high, history = 0, 15, 0, 0, 0
    for position, row in enumerate(rows):
        letter, mask, bit = split_row(row)
        changed = mask if bit == 0 else mask ^ 15
        saved, width = 0, 0
        for i in range(4):
            if (changed >> i) & 1:
                saved |= ((inactive >> i) & 1) << width
                width += 1
        maximum = tables.maxima[letter]
        record = tables.ranks[32 * state + letter] + maximum * saved
        history = history * (maximum << width) + record
        state = tables.edges[32 * state + letter]
        inactive = (inactive & ~changed) | (mask & changed)
        if position < 2:
            digit = sum(a * row[j] for a, j in zip(COEFFICIENTS, ACTIVE))
            residue = (residue + (digit << position)) % 4
            if position == 1:
                radix_high ^= bit
    return state, inactive, residue, radix_high, history


def copy_output(tables: Tables, rows: tuple, work: tuple, dirty: int) -> int:
    state, inactive, residue, radix_high, _ = work
    values, comparison = tables.states[state]
    valid = bool(rows) and rows[0][8] == rows[-1][8] == 1
    valid = valid and comparison == inactive == 0
    quotient = -13 + sum(v >= 0 for v in values)
    carry = quotient - (quotient - residue * (1 + 2 * radix_high)) % 4
    return dirty ^ (((carry + 16) & 31) | (int(valid) << 5))


def reverse(tables: Tables, rows: tuple, work: tuple) -> tuple:
    state, inactive, residue, radix_high, history = work
    for position in range(len(rows) - 1, -1, -1):
        row = rows[position]
        letter, mask, bit = split_row(row)
        changed = mask if bit == 0 else mask ^ 15
        maximum = tables.maxima[letter]
        history, record = divmod(history, maximum << changed.bit_count())
        saved, rank = divmod(record, maximum)
        fiber = tables.inverse[letter].get(state, ())
        need(rank < len(fiber), 'history outside target fiber')
        state = fiber[rank]
        for i in range(4):
            if (changed >> i) & 1:
                need(((inactive >> i) & 1) == ((mask >> i) & 1),
                     'inactive comparison outside transition image')
                inactive = (inactive & ~(1 << i)) | ((saved & 1) << i)
                saved >>= 1
        if position < 2:
            digit = sum(a * row[j] for a, j in zip(COEFFICIENTS, ACTIVE))
            residue = (residue - (digit << position)) % 4
            if position == 1:
                radix_high ^= bit
    need((state, inactive, residue, radix_high, history) == (0, 15, 0, 0, 0),
         'prepared work and history must return exactly')
    return state, inactive ^ 15, residue, radix_high, history


def produce(tables: Tables, rows: tuple, dirty: int = 0) -> tuple:
    check_rows(rows)
    need(type(dirty) is int and 0 <= dirty < 64, 'six-bit dirty target')
    work = forward(tables, rows)
    result = copy_output(tables, rows, work, dirty)
    final = reverse(tables, rows, work)
    need(final == (0, 0, 0, 0, 0), 'all work clears')
    return result, work[-1].bit_length()
