# SPDX-License-Identifier: Apache-2.0
# Ali Romman with substantial OpenAI Codex assistance.
"""Stage whole complex fields on four tapes with explicit clean workspace."""
from fractions import Fraction


def require(ok, message):
    if not ok:
        raise ValueError(message)


def calls(word, dimension, width):
    length = 2 * dimension * width
    result = []
    for index, event in enumerate(word['program']):
        op = event[0]
        if op in ('ADD', 'COPY'):
            result.append((index, 0, 0, op, str(Fraction(event[3])), event[1] * length, event[2] * length))
        elif op == 'SCALE':
            result.append((index, 0, -1, op, str(Fraction(event[2])), event[1] * length, event[1] * length))
        else:
            result.append((index, op))
    result.append((len(word['program']), 'EXIT'))
    return result


def options(head, call, width, dimension):
    if len(call) == 2:
        yield 0, head, None
        return
    length = 2 * dimension * width
    if call[3] == 'SCALE':
        start = call[-2]
        moves = abs(head - start) + 3 * (length - 1)
        moves += 8 * (dimension * width - 1) + 4 * (dimension - 1) * width
        yield start + length - 1, moves, (0, 0)
        return
    addresses = call[-2:]
    for stage_first in (0, 1):
        for return_first in (0, 1):
            end, moves = head, 0
            for bank in (stage_first, 1 - stage_first, return_first, 1 - return_first):
                start = addresses[bank]
                moves += abs(end - start) + length - 1
                end = start + length - 1
            moves += 8 * (length - 1) + 4 * (2 * dimension - 1) * width
            yield end, moves, (stage_first, return_first)


def solve(sequence, width, dimension):
    layers, parents = [{0: 0}], []
    for call in sequence:
        nxt, parent = {}, {}
        for head, value in sorted(layers[-1].items()):
            for end, cost, choice in options(head, call, width, dimension):
                if end not in nxt or value + cost < nxt[end]:
                    nxt[end], parent[end] = value + cost, (head, choice)
        layers.append(nxt)
        parents.append(parent)
    require(set(layers[-1]) == {0}, 'final origin')
    head, choices = 0, []
    for parent in reversed(parents):
        head, choice = parent[head]
        choices.append(choice)
    require(head == 0, 'initial origin')
    return dict(total=layers[-1][0], layers=[sorted(layer.items()) for layer in layers],
                choices=list(reversed(choices)))


def check(sequence, width, dimension, cert):
    require(len(cert['layers']) == len(sequence) + 1 and len(cert['choices']) == len(sequence), 'certificate shape')
    layers = []
    for rows in cert['layers']:
        layer = dict(rows)
        require(len(rows) == len(layer) and all(type(h) is int and h >= 0 and type(v) is int and v >= 0 for h, v in rows), 'potential domain')
        layers.append(layer)
    require(layers[0] == {0: 0} and set(layers[-1]) == {0}, 'potential boundary')
    head, total = 0, 0
    for i, call in enumerate(sequence):
        reachable = set()
        for h, v in layers[i].items():
            for end, cost, _ in options(h, call, width, dimension):
                reachable.add(end)
                require(end in layers[i + 1] and layers[i + 1][end] <= v + cost, 'edge potential')
        require(reachable == set(layers[i + 1]), 'complete potential layer')
        choice = cert['choices'][i]
        choice = tuple(choice) if choice is not None else None
        matches = [(end, cost) for end, cost, c in options(head, call, width, dimension) if c == choice]
        require(len(matches) == 1, 'attaining transition')
        head, cost = matches[0]
        total += cost
    require(head == 0 and total == cert['total'] <= layers[-1][0], 'attaining optimum')
    return total


def seek(tape, address):
    while tape.head != address:
        tape.move(1 if tape.head < address else -1)


def transfer(source, destination, length):
    require(source is not destination, 'distinct transfer tapes')
    for j in range(length):
        bit = source.read()
        destination.write(destination.read() ^ bit)
        source.write(source.read() ^ bit)
        bit ^= destination.read()
        require(bit == 0, 'clean transfer destination')
        if j + 1 < length:
            source.move(1)
            destination.move(1)


def local(route, ribbons, carry, offset):
    """Translate the fixed local route to two record offsets."""
    tapes = [*ribbons, carry]
    require(all(r.head == offset for r in ribbons) and carry.head == 0, 'local record entrance')
    scratch = [0, 0]
    for op, a, b in route:
        if op == 'move':
            tapes[a].move(b)
        elif op == 'xor':
            scratch[a] ^= tapes[b].read()
        elif op == 'flipmask':
            condition = all(scratch[j] for j in (0, 1) if b & (1 << j))
            tapes[a].write(tapes[a].read() ^ int(condition))
        else:
            raise ValueError('local route instruction')
    require(scratch == [0, 0], 'local scratch return')
    require(all(r.head == offset for r in ribbons) and carry.head == 0, 'local record return')


def execute(owner, ribbons, carry, call, width, dimension, choice, route):
    require(len(ribbons) == 2 and len({id(owner), id(carry), *(id(r) for r in ribbons)}) == 4, 'four distinct tapes')
    require(all(r.head == 0 for r in ribbons) and carry.head == 0, 'clean local origins')
    length = 2 * dimension * width
    if call[3] == 'SCALE':
        require(tuple(choice) == (0, 0), 'SCALE visit order')
        start = call[-2]
        seek(owner, start)
        for j in range(dimension):
            for component in (0, 1):
                seek(owner, start + (2 * j + component) * width)
                seek(ribbons[component], j * width)
                transfer(owner, ribbons[component], width)
        for ribbon in ribbons:
            seek(ribbon, 0)
        for j in range(dimension):
            for ribbon in ribbons:
                seek(ribbon, j * width)
            local(route, ribbons, carry, j * width)
        for ribbon in ribbons:
            seek(ribbon, 0)
        seek(owner, start)
        for j in range(dimension):
            for component in (0, 1):
                seek(owner, start + (2 * j + component) * width)
                seek(ribbons[component], j * width)
                transfer(ribbons[component], owner, width)
        for ribbon in ribbons:
            seek(ribbon, 0)
        return
    require(abs(call[-1] - call[-2]) >= length, 'disjoint whole fields')
    stage_first, return_first = choice
    require(stage_first in (0, 1) and return_first in (0, 1), 'visit order')
    for bank in (stage_first, 1 - stage_first):
        seek(owner, call[-2 + bank])
        transfer(owner, ribbons[bank], length)
        seek(ribbons[bank], 0)
    for record in range(2 * dimension):
        for ribbon in ribbons:
            seek(ribbon, record * width)
        local(route, ribbons, carry, record * width)
    for bank in (return_first, 1 - return_first):
        seek(ribbons[bank], 0)
        seek(owner, call[-2 + bank])
        transfer(ribbons[bank], owner, length)
        seek(ribbons[bank], 0)


def affine_options(field, call_at_one, width):
    """Return exact (D coefficient, constant) costs for every positive D."""
    if len(call_at_one) == 2:
        yield -1, ((field + 1) * 2 * width, -1) if field >= 0 else (0, 0), None
        return
    addresses = [value // (2 * width) for value in call_at_one[-2:]]

    def distance(previous, following):
        if previous == -1:
            return following * 2 * width, 0
        delta = following - previous - 1
        return (delta * 2 * width, 1) if delta >= 0 else (-delta * 2 * width, -1)

    if call_at_one[3] == 'SCALE':
        a, b = distance(field, addresses[0])
        yield addresses[0], (a + 18 * width, b - 11 - 4 * width), (0, 0)
        return
    for first in (0, 1):
        for back in (0, 1):
            end, a, b = field, 32 * width, -12 - 4 * width
            for bank in (first, 1 - first, back, 1 - back):
                da, db = distance(end, addresses[bank])
                a, b, end = a + da, b + db, addresses[bank]
            yield end, (a, b), (first, back)


def affine_certificate(sequence, width, first, second):
    layers = []
    for rows1, rows2 in zip(first['layers'], second['layers']):
        one = {-1 if h == 0 else (h + 1) // (2 * width) - 1: v for h, v in rows1}
        two = {-1 if h == 0 else (h + 1) // (4 * width) - 1: v for h, v in rows2}
        require(set(one) == set(two), 'affine state correspondence')
        layers.append([[field, two[field] - v, 2 * v - two[field]] for field, v in sorted(one.items())])
    return dict(layers=layers, choices=first['choices'],
                total=[second['total'] - first['total'], 2 * first['total'] - second['total']])


def check_affine(sequence, width, cert):
    """Verify coefficient inequalities on the entire integer ray D >= 1."""
    require(len(cert['layers']) == len(sequence) + 1 and len(cert['choices']) == len(sequence), 'affine shape')
    layers = []
    for rows in cert['layers']:
        layer = {field: (a, b) for field, a, b in rows}
        require(len(layer) == len(rows) and all(type(x) is int for row in rows for x in row), 'affine rows')
        layers.append(layer)
    require(layers[0] == {-1: (0, 0)} and set(layers[-1]) == {-1}, 'affine boundary')
    head, a, b = -1, 0, 0
    for i, call in enumerate(sequence):
        reachable = set()
        for field, (pa, pb) in layers[i].items():
            for end, (ca, cb), _ in affine_options(field, call, width):
                reachable.add(end)
                require(end in layers[i + 1], 'affine reachable state')
                na, nb = layers[i + 1][end]
                require(pa + ca - na >= 0 and pa + pb + ca + cb - na - nb >= 0, 'all-D edge potential')
        require(reachable == set(layers[i + 1]), 'affine coverage')
        choice = cert['choices'][i]
        choice = tuple(choice) if choice is not None else None
        selected = [(end, cost) for end, cost, c in affine_options(head, call, width) if c == choice]
        require(len(selected) == 1, 'affine path')
        head, (ca, cb) = selected[0]
        a, b = a + ca, b + cb
    require(head == -1 and (a, b) == tuple(cert['total']) == layers[-1][-1], 'all-D attaining path')
    return a, b
