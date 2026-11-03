# SPDX-License-Identifier: Apache-2.0
# Ali Romman with substantial OpenAI Codex assistance.
"""Move selected scalar operands between an owner tape and two clean ribbons."""
from fractions import Fraction


def require(ok, message):
    if not ok:
        raise ValueError(message)


def address(field, coordinate, component, dimension, width):
    require(type(dimension) is int and dimension > 0 and 0 <= coordinate < dimension, 'coordinate domain')
    require(component in (0, 1) and field >= 0 and width > 0, 'record domain')
    return ((field * dimension + coordinate) * 2 + component) * width


def plan(word, dimension, width):
    alive = set(range(word['public']))
    owners = word['public'] + word['owned_fields']
    result = []
    for index, event in enumerate(word['program']):
        op = event[0]
        if op == 'INIT':
            require(event[1] not in alive and word['public'] <= event[1] < owners, 'fresh owner')
            alive.add(event[1])
        elif op == 'CLEAR':
            require(event[1] in alive and event[1] >= word['public'], 'owned clear')
            alive.remove(event[1])
        elif op in ('ADD', 'COPY'):
            target, source = event[1:3]
            require(target in alive and source in alive and target != source, 'live distinct operands')
            for j in range(dimension):
                for component in (0, 1):
                    result.append((index, j, component, op, str(Fraction(event[3])),
                                   address(target, j, component, dimension, width),
                                   address(source, j, component, dimension, width)))
            continue
        elif op == 'SCALE':
            require(event[1] in alive, 'live target')
            for j in range(dimension):
                result.append((index, j, -1, op, str(Fraction(event[2])),
                               address(event[1], j, 0, dimension, width),
                               address(event[1], j, 1, dimension, width)))
            continue
        elif op == 'MOVE':
            require(event[1] in alive, 'live native field')
        else:
            raise ValueError('source event domain')
        result.append((index, op))
    require(alive == set(range(word['public'])), 'owned lifetime return')
    result.append((len(word['program']), 'EXIT'))
    return result


def options(head, call, width):
    if len(call) == 2:
        yield 0, head, None
        return
    addresses = call[-2:]
    for stage_first in (0, 1):
        for return_first in (0, 1):
            end, moves = head, 0
            for bank in (stage_first, 1 - stage_first, return_first, 1 - return_first):
                start = addresses[bank]
                moves += abs(end - start) + width - 1
                end = start + width - 1
            moves += 8 * (width - 1)
            yield end, moves, (stage_first, return_first)


def solve(calls, width):
    layers = [{0: 0}]
    parents = []
    for call in calls:
        nxt, parent = {}, {}
        for head, value in sorted(layers[-1].items()):
            for end, cost, choice in options(head, call, width):
                if end not in nxt or value + cost < nxt[end]:
                    nxt[end] = value + cost
                    parent[end] = (head, choice)
        layers.append(nxt)
        parents.append(parent)
    require(set(layers[-1]) == {0}, 'final origin')
    head, choices = 0, []
    for parent in reversed(parents):
        head, choice = parent[head]
        choices.append(choice)
    require(head == 0, 'initial origin')
    return dict(total=layers[-1][0], layers=[sorted(d.items()) for d in layers],
                choices=list(reversed(choices)))


def check(calls, width, certificate):
    layers = []
    for rows in certificate['layers']:
        layer = dict(rows)
        require(len(layer) == len(rows) and all(type(h) is int and h >= 0 and type(v) is int and v >= 0
                                               for h, v in rows), 'potential domain')
        layers.append(layer)
    require(len(layers) == len(calls) + 1 and layers[0] == {0: 0}, 'potential entrance')
    for i, call in enumerate(calls):
        reachable = set()
        for head, value in layers[i].items():
            for end, cost, _ in options(head, call, width):
                reachable.add(end)
                require(end in layers[i + 1] and layers[i + 1][end] <= value + cost, 'edge potential')
        require(reachable == set(layers[i + 1]), 'complete state layer')
    require(set(layers[-1]) == {0} and certificate['total'] <= layers[-1][0], 'terminal potential')
    require(len(certificate['choices']) == len(calls), 'path length')
    head, total = 0, 0
    for call, choice in zip(calls, certificate['choices']):
        choice = tuple(choice) if choice is not None else None
        matches = [(end, cost) for end, cost, c in options(head, call, width) if c == choice]
        require(len(matches) == 1, 'path transition')
        head, cost = matches[0]
        total += cost
    require(head == 0 and total == certificate['total'], 'attaining path')
    return total


def fixed_bill(calls, width, return_each):
    head, total = 0, 0
    for call in calls:
        choice = None if len(call) == 2 else (0, 1)
        head, cost, _ = next(row for row in options(head, call, width) if row[2] == choice)
        total += cost
        if return_each:
            total += head
            head = 0
    require(head == 0, 'baseline return')
    return total


def seek(tape, destination):
    while tape.head != destination:
        tape.move(1 if tape.head < destination else -1)


def transfer(source, destination, width):
    """Move one record into a clean record and return the control bit to zero."""
    require(source is not destination, 'distinct transfer tapes')
    for j in range(width):
        control = source.read()
        destination.write(destination.read() ^ control)
        source.write(source.read() ^ control)
        control ^= destination.read()
        require(control == 0, 'clean transfer destination')
        if j + 1 < width:
            source.move(1)
            destination.move(1)


def execute(owner, ribbons, carry, call, width, choice, local_route, local_engine):
    """Execute all transfers and the local circuit with unit head moves."""
    require(len(call) != 2 and len(ribbons) == 2, 'scalar call')
    require(len({id(owner), id(carry), *(id(t) for t in ribbons)}) == 4, 'four distinct tapes')
    require(all(t.head == 0 for t in [*ribbons, carry]), 'local origin entrance')
    addresses = call[-2:]
    require(abs(addresses[0] - addresses[1]) >= width, 'disjoint owner records')
    stage_first, return_first = choice
    require(stage_first in (0, 1) and return_first in (0, 1), 'visit order')
    for bank in (stage_first, 1 - stage_first):
        seek(owner, addresses[bank])
        transfer(owner, ribbons[bank], width)
        seek(ribbons[bank], 0)
    local_engine.run(local_route, [*ribbons, carry])
    for bank in (return_first, 1 - return_first):
        seek(owner, addresses[bank])
        transfer(ribbons[bank], owner, width)
        seek(ribbons[bank], 0)
