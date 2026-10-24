# SPDX-License-Identifier: Apache-2.0
"""Compile one actual eight-entry low-row functional into local tape instructions.

q and weights are compiler parameters. Runtime instructions contain no arithmetic,
lookup or input-dependent address. This is the low decoder, not payload routing.
"""


def compile_decoder(q, weights, positions=None, cells=None):
    if type(q) is not int or q < 3 or q % 2 == 0 or any(q % d == 0 for d in range(3, q, 2)):
        raise ValueError('odd prime compiler parameter')
    if len(weights) != 8 or any(type(x) is not int for x in weights):
        raise ValueError('eight integer quarter-scaled source coefficients')
    if sum(abs(x) for x in weights) > 16:
        raise ValueError('actual source column coefficient envelope')
    positions = tuple(range(8)) if positions is None else tuple(positions)
    cells = 8 if cells is None else cells
    if len(positions) != 8 or tuple(sorted(set(positions))) != positions or positions[0] < 0 or positions[-1] >= cells:
        raise ValueError('eight ordered fixed cache cell positions')
    bits = (q - 1).bit_length()
    code = [('reject',)]

    def emit(row):
        code.append(row)
        return len(code) - 1

    def chain(rows, destination):
        for row in reversed(rows):
            destination = emit(tuple(row) + (destination,))
        return destination

    layers = [{(0, 0)}]
    for position in range(8 * bits):
        following = set()
        for total, partial in layers[-1]:
            for symbol in (0, 1):
                digit = partial + (symbol << (position % bits))
                if position % bits == bits - 1:
                    if digit < q:
                        following.add((total + weights[position // bits] * digit, 0))
                else:
                    following.add((total, digit))
        layers.append(following)
    entries = {}
    for total, partial in sorted(layers[-1]):
        low = total * pow(4, -1, q) % q
        carry = (total - 4 * low) // q
        if not -7 <= carry <= 12:
            raise ValueError('source quarter-carry envelope')
        rows = [('move', 0, -1)] * (cells * bits)
        for tape, value, width in ((1, low, bits), (2, carry + 8, 5)):
            for bit in range(width):
                rows.extend([('write', tape, (value >> bit) & 1), ('move', tape, 1)])
            rows.extend([('move', tape, -1)] * width)
        finish = chain(rows, emit(('halt',)))
        entries[8 * bits, total, partial] = emit(('branch', 0, ((2, finish),), 0))
    for position in reversed(range(8 * bits)):
        for total, partial in sorted(layers[position]):
            targets = []
            for symbol in (0, 1):
                digit = partial + (symbol << (position % bits))
                next_total, next_partial = total, digit
                if position % bits == bits - 1:
                    if digit >= q:
                        targets.append(0)
                        continue
                    next_total += weights[position // bits] * digit
                    next_partial = 0
                target = entries[position + 1, next_total, next_partial]
                current = positions[position // bits] * bits + position % bits
                following = cells * bits if position + 1 == 8 * bits else positions[(position + 1) // bits] * bits + (position + 1) % bits
                targets.append(chain([('move', 0, 1)] * (following - current), target))
            entries[position, total, partial] = emit(('branch', 0, ((0, targets[0]), (1, targets[1])), 0))
    start = chain([('move', 0, 1)] * (positions[0] * bits), entries[0, 0, 0])
    return {'code': code, 'start': start, 'bits': bits, 'q': q, 'weights': list(weights), 'positions': list(positions), 'cells': cells}


def execute(program, values, corrupt=None):
    """Literal local simulator; integer decoding below is only an endpoint observer."""
    bits = program['bits']
    tapes = [{i * bits + j: (v >> j) & 1 for i, v in enumerate(values) for j in range(bits)}, {}, {}]
    tapes[0][len(values) * bits] = 2
    if corrupt is not None:
        tapes[0][corrupt] = 7
    stats = run_tapes(program, tapes)
    low = sum(tapes[1][j] << j for j in range(bits))
    carry = sum(tapes[2][j] << j for j in range(5)) - 8
    return low, carry, stats


def run_tapes(program, tapes):
    original = dict(tapes[0])
    heads = [0] * len(tapes)
    visited = [{0} for _ in tapes]
    pc, steps = program['start'], 0
    while True:
        row = program['code'][pc]
        steps += 1
        op = row[0]
        if op == 'halt':
            break
        if op == 'reject':
            raise ValueError('invalid encoded low row')
        if op == 'goto':
            pc = row[1]
        elif op == 'branch':
            symbol = tapes[row[1]].get(heads[row[1]])
            pc = dict(row[2]).get(symbol, row[3])
        elif op == 'move':
            heads[row[1]] += row[2]
            visited[row[1]].add(heads[row[1]])
            pc = row[3]
        elif op == 'write':
            tapes[row[1]][heads[row[1]]] = row[2]
            pc = row[3]
        else:
            raise ValueError('nonlocal or arithmetic instruction')
    if tapes[0] != original or heads != [0] * len(tapes):
        raise ValueError('source or head restoration')
    return {'steps': steps, 'visited': sum(map(len, visited)), 'instructions': len(program['code'])}


def compile_frontend(q, weights, positions=None, cells=None):
    """Link the cache decoder to all fixed quarter descriptors with paid dispatch."""
    from offset import compile_offset
    decoder = compile_decoder(q, weights, positions, cells)
    code = []

    def emit(row):
        code.append(row)
        return len(code) - 1

    def chain(rows, destination):
        for row in reversed(rows):
            destination = emit(tuple(row) + (destination,))
        return destination

    finished = emit(('halt',))
    rows = []
    for _ in range(5):
        rows.extend([('write', 2, None), ('move', 2, 1)])
    rows.extend([('move', 2, -1)] * 5)
    cleared = chain(rows, finished)

    def link(program, mapping, continuation):
        base = len(code)
        for row in program['code']:
            if row[0] == 'branch':
                code.append(('branch', mapping[row[1]], tuple((s, dest + base) for s, dest in row[2]), row[3] + base))
            elif row[0] in ('write', 'move'):
                code.append((row[0], mapping[row[1]], row[2], row[3] + base))
            elif row[0] == 'halt':
                code.append(('goto', continuation))
            else:
                code.append(row)
        return program['start'] + base

    targets = {k + 8: link(compile_offset(k), (3, 4), cleared) for k in range(-7, 13)}
    rejected = emit(('reject',))

    def dispatch(position, value):
        if position == 5:
            return chain([('move', 2, -1)] * 5, targets.get(value, rejected))
        branches = tuple((symbol, chain([('move', 2, 1)], dispatch(position + 1, value + (symbol << position)))) for symbol in (0, 1))
        return emit(('branch', 2, branches, rejected))

    start = link(decoder, (0, 1, 2), dispatch(0, 0))
    return {**decoder, 'code': code, 'start': start}
