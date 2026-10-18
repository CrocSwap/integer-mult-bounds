"""Two-tape, four-symbol half-source ADD. Apache-2.0; ywz65/Codex.

The controller sees only its finite state and the two scanned symbols.
Integer encoding, addresses, trace checks and bounds belong to the test harness.
"""
from itertools import product

ALPHABET = ("_", "#", "0", "1")
BITS = ("0", "1")


def initial(negative=False):
    if type(negative) is not bool:
        raise ValueError("orientation must be Boolean")
    return ("start", int(negative), int(negative), 0)


def transition(state, scanned):
    mode, negative, carry, previous = state
    x, y = scanned
    halt = ("reject", negative, 0, 0)
    # None means leave the scanned symbol unchanged, including arbitrary dirt.
    if mode == "start" and x == "0" and y in BITS:
        return ("add", negative, carry, 0), (None, None), (1, 0)
    if mode == "add" and y in BITS:
        if x in BITS:
            source = int(x)
            total = (source ^ negative) + int(y) + carry
            return ("add", negative, total // 2, source), (None, str(total % 2)), (1, 1)
        if x == "#":
            # Arithmetic extension of the source sign at the final target bit.
            total = (previous ^ negative) + int(y) + carry
            return ("end", negative, 0, 0), (None, str(total % 2)), (0, 1)
    if mode == "end" and x == y == "#":
        return ("rewind", negative, 0, 0), (None, None), (-1, -1)
    if mode == "rewind":
        if x in BITS and y in BITS:
            return state, (None, None), (-1, -1)
        if x == y == "#":
            return ("done", negative, 0, 0), (None, None), (1, 1)
    return halt, (None, None), (0, 0)


def compile_table():
    """Finite full table, independent of width, addresses and tape contents."""
    states = [initial(bool(n)) for n in (0, 1)]
    states += [("add", n, c, p) for n, c, p in product((0, 1), repeat=3)]
    states += [(mode, n, 0, 0) for mode in ("end", "rewind") for n in (0, 1)]
    return {(s, (a, b)): transition(s, (a, b))
            for s, a, b in product(states, ALPHABET, ALPHABET)}


TABLE = compile_table()


def simulate(tapes, origins=(0, 0), negative=False, max_steps=1000000, table=None):
    """Generic table interpreter: one read/write and unit movement per tape."""
    table = TABLE if table is None else table
    heads = list(origins)
    state = initial(negative)
    trace = []
    while state[0] not in ("done", "reject"):
        if len(trace) >= max_steps:
            raise ValueError("simulation limit reached")
        read = tuple(t.get(h, "_") for t, h in zip(tapes, heads))
        nxt, writes, moves = table[(state, read)]
        if any(m not in (-1, 0, 1) for m in moves):
            raise ValueError("nonphysical head move")
        trace.append((state, tuple(heads), read, writes, moves))
        for i, (write, move) in enumerate(zip(writes, moves)):
            if write is not None:
                if write not in ALPHABET:
                    raise ValueError("nonfinite alphabet")
                tapes[i][heads[i]] = write
            heads[i] += move
        state = nxt
    return state[0], tuple(heads), trace
