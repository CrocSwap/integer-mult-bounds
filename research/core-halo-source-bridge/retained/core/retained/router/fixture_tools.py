"""External finite encoders and observers, excluded from online machine claims."""
from itertools import product
from hashlib import sha256


def need(ok, message):
    if not ok:
        raise ValueError(message)


def body(tape):
    from session import borrowed_tape
    from words import BLANK
    raw = bytes(borrowed_tape(tape).cells)
    end = raw.find(bytes((BLANK,)), 1)
    if end < 0:
        end = len(raw)
    need(all(x == BLANK for x in raw[end:]), 'empty observer backing suffix')
    return raw[1:end]


def snapshot(tapes):
    from session import borrowed_tape
    return tuple((bytes(borrowed_tape(t).cells), borrowed_tape(t).head) for t in tapes)


def emit(tape, data):
    for value in data:
        tape.append(value)
    tape.rewind()


def count(n):
    need(n >= 0, 'nonnegative fixture count')
    return bytes(map(int, reversed(bin(n)[2:]))) + bytes((3,))


def big(n, bits):
    need(0 <= n < 1 << bits, 'fixture big-endian field')
    return bytes((n >> k) & 1 for k in reversed(range(bits)))


def word(n, bits):
    need(-(1 << (bits-1)) <= n < 1 << (bits-1), 'fixture signed word')
    return bytes((n >> k) & 1 for k in range(bits))


def integer(data):
    return sum(v << i for i, v in enumerate(data)) - (data[-1] << len(data))


def frame(context, values, width):
    return bytes(context) + bytes((5,)) + b''.join(word(x, width) for pair in values for x in pair)


def bank(context, boundaries, masks, blocks, width, h, page_bodies=None):
    out = bytearray(context); out.append(5)
    for axis, (exposed, mask, block) in enumerate(zip(boundaries, masks, blocks)):
        a, n = len(exposed), sum(mask)
        out.append(6); out.extend(count(a)); out.extend(count(n)); out.extend(count(block))
        out.extend(b''.join(big(x, h) for x in exposed)); out.append(5)
        out.extend(mask); out.append(5)
        for i, length in enumerate((a, a, a, a, n, n, n, n)):
            rows = (length + block - 1) // block
            expected = max(0, rows - (i % 2)) * block * block * width
            data = bytes(expected) if page_bodies is None else page_bodies[axis][i]
            need(len(data) == expected, 'exact finite catalogue page extent')
            out.extend(data); out.append(5)
        out.append(7)
    return bytes(out)


def nonlinear_oracle(side, boundaries, values, reverse=False, stale=False, drop=None):
    points = list(product(range(side), repeat=len(boundaries)))
    state = dict(zip(points, values)); initial = state.copy()
    order = reversed(range(len(boundaries))) if reverse else range(len(boundaries))
    changed_inputs = 0
    for axis in order:
        exposed = boundaries[axis]
        if not exposed or axis == drop:
            continue
        before = initial if stale else state.copy()
        for spectators in product(range(side), repeat=len(boundaries)-1):
            line = [spectators[:axis] + (x,) + spectators[axis:] for x in exposed]
            changed_inputs += any(before[x] != initial[x] for x in line)
            x, z = line[0], line[-1]
            pair = before[x]
            digit = 1 - ((pair[0] & 1) & (before[z][0] & 1))
            state[x] = ((pair[0] & ~1) | digit, pair[1])
    return [state[x] for x in points], changed_inputs


def digest(value):
    import json
    return sha256(json.dumps(value, separators=(',', ':'), sort_keys=True).encode()).hexdigest()
