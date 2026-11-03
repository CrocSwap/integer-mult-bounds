# SPDX-License-Identifier: Apache-2.0
# Ali Romman with substantial OpenAI Codex assistance.
"""Compile a two-bit control cache with exact local tape costs."""

from itertools import combinations, permutations


def require(ok, message):
    if not ok:
        raise ValueError(message)


def location(width, wire):
    require(type(wire) is int and 0 <= wire <= 2 * width, "wire domain")
    return divmod(wire, width)


def visit(width, heads, wire):
    bank, offset = location(width, wire)
    new = list(heads)
    cost = abs(new[bank] - offset)
    new[bank] = offset
    return tuple(new), cost


def edges(width, state, gate):
    """Enumerate the declared no-prefetch cache policy."""
    old, heads = state
    required = set(gate[:-1])
    target = gate[-1]
    require(len(gate) in (2, 3) and len(set(gate)) == len(gate), "gate domain")
    for wire in gate:
        location(width, wire)
    must_keep = set(old) & required
    optional = sorted(set(old) - required - {target})
    for size in range(min(len(optional), 2 - len(required)) + 1):
        for subset in combinations(optional, size):
            keep = must_keep | set(subset)
            actions = tuple((0, w) for w in sorted(set(old) - keep))
            actions += tuple((1, w) for w in sorted(required - keep))
            for order in permutations(actions):
                held = set(old)
                end = heads
                cost = 0
                for load, wire in order:
                    if load:
                        if len(held) == 2:
                            break
                        held.add(wire)
                    else:
                        held.remove(wire)
                    end, movement = visit(width, end, wire)
                    cost += movement + 1
                else:
                    require(required <= held and target not in held, "valid cache at write")
                    end, movement = visit(width, end, target)
                    yield (tuple(sorted(held)), end), cost + movement + 2, order


def terminals(width, state):
    held, heads = state
    for order in permutations(held):
        end, cost = heads, 0
        for wire in order:
            end, movement = visit(width, end, wire)
            cost += movement + 1
        yield cost + sum(end), order


START = ((), (0, 0, 0))


def optimize(width, gates):
    """Return all layer potentials and one attaining path."""
    layers = [{START: 0}]
    parents = []
    for gate in gates:
        nxt, parent = {}, {}
        for state, value in sorted(layers[-1].items()):
            for end, cost, order in edges(width, state, gate):
                total = value + cost
                if end not in nxt or total < nxt[end]:
                    nxt[end] = total
                    parent[end] = (state, order)
        require(bool(nxt) and len(nxt) <= 100000, "exact state budget; no truncation")
        layers.append(nxt)
        parents.append(parent)
    total, state, finish = min((value + cost, state, order)
                              for state, value in layers[-1].items()
                              for cost, order in terminals(width, state))
    path = []
    for parent in reversed(parents):
        state, order = parent[state]
        path.append(order)
    require(state == START, "path entrance")
    return {"total": total, "layers": [[[list(s[0]), list(s[1]), d]
                                         for s, d in sorted(layer.items())] for layer in layers],
            "actions": list(reversed(path)), "finish": finish}


def check_certificate(width, gates, certificate):
    """Check a feasible potential lower bound and an attaining route."""
    layers = []
    for rows in certificate["layers"]:
        layer = {}
        for cache, heads, value in rows:
            state = (tuple(cache), tuple(heads))
            require(state not in layer and type(value) is int and value >= 0, "potential rows")
            layer[state] = value
        layers.append(layer)
    require(len(layers) == len(gates) + 1 and layers[0] == {START: 0}, "potential entrance")
    for i, gate in enumerate(gates):
        reachable = set()
        for state, value in layers[i].items():
            for end, cost, _ in edges(width, state, gate):
                reachable.add(end)
                require(end in layers[i + 1] and layers[i + 1][end] <= value + cost,
                        "edge potential inequality")
        require(reachable == set(layers[i + 1]), "complete reachable layer")
    total = certificate["total"]
    require(type(total) is int and total >= 0, "total domain")
    for state, value in layers[-1].items():
        for cost, _ in terminals(width, state):
            require(total <= value + cost, "terminal potential inequality")
    require(len(certificate["actions"]) == len(gates), "path length")
    state, cost = START, 0
    for gate, actions in zip(gates, certificate["actions"]):
        actions = tuple(map(tuple, actions))
        matches = [(end, charge) for end, charge, order in edges(width, state, gate) if order == actions]
        require(len(matches) == 1, "legal path transition")
        state, charge = matches[0]
        cost += charge
    finish = tuple(certificate["finish"])
    matches = [charge for charge, order in terminals(width, state) if order == finish]
    require(len(matches) == 1 and cost + matches[0] == total, "attaining terminal")
    return total


def compile_route(width, gates, certificate):
    """Emit unit moves, XOR reads and local conditional writes."""
    check_certificate(width, gates, certificate)
    heads = [0, 0, 0]
    slots = [None, None]
    route = []

    def go(wire):
        bank, offset = location(width, wire)
        while heads[bank] != offset:
            direction = 1 if heads[bank] < offset else -1
            route.append(("move", bank, direction))
            heads[bank] += direction
        return bank

    def action(load, wire):
        slot = slots.index(None) if load else slots.index(wire)
        route.append(("xor", slot, go(wire)))
        slots[slot] = wire if load else None

    for gate, actions in zip(gates, certificate["actions"]):
        for load, wire in actions:
            action(load, wire)
        require(gate[-1] not in slots, "no cached target at write")
        mask = sum(1 << slots.index(wire) for wire in gate[:-1])
        route.append(("flipmask", go(gate[-1]), mask))
    for wire in certificate["finish"]:
        action(0, wire)
    require(slots == [None, None], "empty exit cache")
    for bank in range(3):
        while heads[bank]:
            route.append(("move", bank, -1))
            heads[bank] -= 1
    require(sum(counts(route).values()) == certificate["total"], "literal route bill")
    return route


def counts(route):
    result = dict(moves=0, reads=0, writes=0)
    for op, first, second in route:
        if op == "move":
            require(first in (0, 1, 2) and second in (-1, 1), "move domain")
            result["moves"] += 1
        elif op == "xor":
            require(first in (0, 1) and second in (0, 1, 2), "read domain")
            result["reads"] += 1
        elif op == "flipmask":
            require(first in (0, 1, 2) and second in (1, 2, 3), "write domain")
            result["reads"] += 1
            result["writes"] += 1
        else:
            raise ValueError("unknown instruction")
    return result


def run(route, tapes):
    """Use only the predecessor's metered Tape methods for payload access."""
    require(len(tapes) == 3 and len({id(t) for t in tapes}) == 3, "distinct tapes")
    require(all(t.head == 0 for t in tapes), "origin entrance")
    scratch = [0, 0]
    before = {name: sum(t.counts[name] for t in tapes) for name in ("moves", "reads", "writes")}
    counts(route)
    for op, first, second in route:
        if op == "move":
            tapes[first].move(second)
        elif op == "xor":
            scratch[first] ^= tapes[second].read()
        else:
            condition = all(scratch[j] for j in range(2) if second & (1 << j))
            tapes[first].write(tapes[first].read() ^ int(condition))
    require(scratch == [0, 0], "scratch return")
    require(all(t.head == 0 for t in tapes), "head return")
    observed = {name: sum(t.counts[name] for t in tapes) - value for name, value in before.items()}
    require(observed == counts(route), "metered bill")
    return observed
