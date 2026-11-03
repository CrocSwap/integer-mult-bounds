# SPDX-License-Identifier: Apache-2.0
# Ali Romman with substantial OpenAI Codex assistance.
"""An exclusive two-field cache with exact affine physical costs."""
from itertools import permutations

START = ((-1, -1), -1)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def distance(previous, following, width):
    if previous == -1:
        return following * 2 * width, 0
    delta = following - previous - 1
    return (delta * 2 * width, 1) if delta >= 0 else (-delta * 2 * width, -1)


def transfer_cost(head, field, width):
    a, b = distance(head, field, width)
    return a + 18 * width, b - 3


def action_orders(slots, required):
    """Keep required resident fields; acquire only the missing current fields."""
    for assignment in permutations(required):
        if any(old in required and old != new for old, new in zip(slots, assignment)):
            continue
        actions = []
        for bank, (old, new) in enumerate(zip(slots, assignment)):
            if old == new:
                continue
            if old >= 0:
                actions.append((0, bank, old))
            actions.append((1, bank, new))
        for order in permutations(actions):
            held = list(slots)
            for load, bank, field in order:
                if load:
                    if held[bank] != -1 or field in held:
                        break
                    held[bank] = field
                else:
                    if held[bank] != field:
                        break
                    held[bank] = -1
            else:
                require(tuple(held) == assignment, 'cache assignment')
                yield tuple(held), order


def edges(state, event, width, local_cost, batched):
    slots, head = state
    op = event[0]
    if op in ('ADD', 'COPY'):
        required = tuple(event[1:3])
        require(len(set(required)) == 2, 'distinct field operands')
        orders = action_orders(slots, required)
    else:
        actions = tuple((0, bank, field) for bank, field in enumerate(slots) if field >= 0)
        orders = (((-1, -1), order) for order in permutations(actions))
    for held, order in orders:
        end, a, b = head, 0, 0
        for _, _, field in order:
            ca, cb = transfer_cost(end, field, width)
            a, b, end = a + ca, b + cb, field
        if op in ('ADD', 'COPY'):
            a += 8 * width + 2 * local_cost[(op, str(event[3]))]
            b -= 4 * width
        elif op == 'SCALE':
            call = (0, 0, -1, op, str(event[2]), event[1] * 2 * width, event[1] * 2 * width)
            [(end, (ca, cb), _)] = list(batched.affine_options(end, call, width))
            a += ca + 24 * width + local_cost[(op, str(event[2]))]
            b += cb
        else:
            require(op in ('MOVE', 'INIT', 'CLEAR', 'EXIT'), 'event domain')
            if end >= 0:
                a += (end + 1) * 2 * width
                b -= 1
            end = -1
        yield (held, end), (a, b), order


def solve(events, width, dimension, local_cost, batched):
    layers, parents = [{START: 0}], []
    for event in events:
        nxt, parent = {}, {}
        for state, value in sorted(layers[-1].items()):
            for end, (a, b), order in edges(state, event, width, local_cost, batched):
                total = value + a * dimension + b
                if end not in nxt or total < nxt[end]:
                    nxt[end], parent[end] = total, (state, order)
        require(bool(nxt) and len(nxt) <= 64, 'complete cache state budget')
        layers.append(nxt)
        parents.append(parent)
    require(set(layers[-1]) == {START}, 'final owner return')
    state, actions = START, []
    for parent in reversed(parents):
        state, order = parent[state]
        actions.append(order)
    require(state == START, 'initial owner state')
    return dict(total=layers[-1][START], layers=layers, actions=list(reversed(actions)))


def affine_certificate(first, second):
    layers = []
    for one, two in zip(first['layers'], second['layers']):
        require(set(one) == set(two), 'affine states')
        layers.append([[list(state[0]), state[1], two[state] - value, 2 * value - two[state]]
                       for state, value in sorted(one.items())])
    return dict(layers=layers, actions=first['actions'], total=[second['total'] - first['total'], 2 * first['total'] - second['total']])


def check(events, width, local_cost, batched, cert):
    require(len(cert['layers']) == len(events) + 1 and len(cert['actions']) == len(events), 'certificate shape')
    layers = []
    for rows in cert['layers']:
        layer = {(tuple(slots), head): (a, b) for slots, head, a, b in rows}
        require(len(rows) == len(layer), 'unique state rows')
        require(all(type(x) is int for slots, head, a, b in rows for x in [*slots, head, a, b]), 'integer potential')
        layers.append(layer)
    require(layers[0] == {START: (0, 0)} and set(layers[-1]) == {START}, 'potential boundary')
    state, a, b = START, 0, 0
    for i, event in enumerate(events):
        reachable = set()
        for before, (pa, pb) in layers[i].items():
            for end, (ca, cb), _ in edges(before, event, width, local_cost, batched):
                reachable.add(end)
                require(end in layers[i + 1], 'reachable cache state')
                na, nb = layers[i + 1][end]
                require(pa + ca - na >= 0 and pa + pb + ca + cb - na - nb >= 0, 'all-D edge inequality')
        require(reachable == set(layers[i + 1]), 'complete cache state layer')
        order = tuple(map(tuple, cert['actions'][i]))
        matches = [(end, cost) for end, cost, actions in edges(state, event, width, local_cost, batched) if actions == order]
        require(len(matches) == 1, 'attaining cache transition')
        state, (ca, cb) = matches[0]
        a, b = a + ca, b + cb
    require(state == START and (a, b) == tuple(cert['total']) == layers[-1][START], 'attaining all-D total')
    return a, b


def execute(owner, ribbons, carry, slots, event, width, dimension, actions, routes, batched):
    """Run the compiled field transfers and local circuits on metered tapes."""
    require(len({id(owner), id(carry), *(id(r) for r in ribbons)}) == 4, 'four distinct tapes')
    require(len(slots) == 2 and len({f for f in slots if f >= 0}) == sum(f >= 0 for f in slots), 'exclusive cache slots')
    require(all(r.head == 0 for r in [*ribbons, carry]), 'local origin entrance')
    held = list(slots)
    length = 2 * dimension * width
    for load, bank, field in actions:
        require(load in (0, 1) and bank in (0, 1), 'transfer action')
        if load:
            require(held[bank] == -1 and field not in held, 'load into clean exclusive slot')
        else:
            require(held[bank] == field, 'evict live cache owner')
        batched.seek(owner, field * length)
        source, destination = (owner, ribbons[bank]) if load else (ribbons[bank], owner)
        batched.transfer(source, destination, length)
        batched.seek(ribbons[bank], 0)
        held[bank] = field if load else -1
    op = event[0]
    if op in ('ADD', 'COPY'):
        target, source = event[1:3]
        require(target in held and source in held and target != source, 'resident scalar operands')
        ordered = [ribbons[held.index(target)], ribbons[held.index(source)]]
        for record in range(2 * dimension):
            for ribbon in ordered:
                batched.seek(ribbon, record * width)
            batched.local(routes[(op, str(event[3]))], ordered, carry, record * width)
        for ribbon in ordered:
            batched.seek(ribbon, 0)
    else:
        require(held == [-1, -1], 'complete boundary flush')
        if op == 'SCALE':
            call = (0, 0, -1, op, str(event[2]), event[1] * length, event[1] * length)
            batched.execute(owner, ribbons, carry, call, width, dimension, (0, 0), routes[(op, str(event[2]))])
        else:
            require(op in ('MOVE', 'INIT', 'CLEAR', 'EXIT'), 'boundary domain')
            batched.seek(owner, 0)
    return tuple(held)
