"""Exact subspace bounds for carried frames; Apache-2.0, Codex assistance.

The recurrence is a general lattice argument, applied here to the source-bound
native word of Dugongue / PR4971 and Cao Yifan's round-three predecessor.
"""
from copy import deepcopy
from functools import lru_cache


def need(condition, message):
    if not condition:
        raise ValueError(message)


def space(vectors):
    points = {0}
    for vector in vectors:
        points |= {x ^ vector for x in tuple(points)}
    return sum(1 << x for x in points)


@lru_cache(None)
def basis(subspace):
    result, generated = [], 1
    for vector in range(1, subspace.bit_length()):
        if subspace >> vector & 1 and not generated >> vector & 1:
            result.append(vector)
            generated = space(result)
    need(generated == subspace, "Not a binary subspace")
    return tuple(result)


def dimension(subspace):
    return subspace.bit_count().bit_length() - 1


@lru_cache(None)
def join(left, right):
    if left & right == left:
        return right
    if left & right == right:
        return left
    return space(basis(left) + basis(right))


def linear(columns, vector):
    result = 0
    for bit, column in enumerate(columns):
        if vector >> bit & 1:
            result ^= column
    return result


@lru_cache(None)
def compose(left, right):
    return tuple(linear(left, column) for column in right)


@lru_cache(None)
def inverse(columns):
    size = 1 << len(columns)
    need(all(type(x) is int and 0 <= x < size for x in columns), "Binary map range")
    values = [linear(columns, x) for x in range(size)]
    need(len(set(values)) == size, "Singular binary map")
    back = [0] * size
    for source, target in enumerate(values):
        back[target] = source
    return tuple(back[1 << bit] for bit in range(len(columns)))


@lru_cache(None)
def image(columns, subspace):
    return space(tuple(linear(columns, vector) for vector in basis(subspace)))


class FrameDAG:
    """Edges (a,b,G) impose G(U_a) <= U_b, with a < b and G invertible."""

    def __init__(self, h):
        need(type(h) is int and 1 <= h <= 9, "Ambient dimension between one and nine")
        self.h = h
        self.identity = tuple(1 << bit for bit in range(h))
        self.full = (1 << (1 << h)) - 1
        self.fixed = []
        self.parents = []
        self.children = []

    def node(self, fixed=None):
        if fixed is not None:
            basis(fixed)
            need(fixed & self.full == fixed, "Frame outside ambient space")
        index = len(self.fixed)
        self.fixed.append(fixed)
        self.parents.append([])
        self.children.append([])
        return index

    def edge(self, source, target, columns=None):
        columns = self.identity if columns is None else tuple(columns)
        need(0 <= source < target < len(self.fixed), "Edges require topological order")
        need(len(columns) == self.h, "Map dimension")
        inverse(columns)
        self.parents[target].append((source, columns))
        self.children[source].append((target, columns))

    def bounds(self, extra=None):
        fixed = self.fixed[:]
        for node, subspace in (extra or {}).items():
            need(type(node) is int and 0 <= node < len(fixed), "Unknown pinned node")
            basis(subspace)
            need(subspace & self.full == subspace, "Pinned frame outside ambient space")
            need(fixed[node] is None or fixed[node] == subspace, "Changed fixed node")
            fixed[node] = subspace
        lower = []
        for node, value in enumerate(fixed):
            bound = 1
            for parent, columns in self.parents[node]:
                bound = join(bound, image(columns, lower[parent]))
            if value is not None:
                need(bound & value == bound, "Infeasible lower bound")
                bound = value
            lower.append(bound)
        upper = [None] * len(fixed)
        for node in reversed(range(len(fixed))):
            bound = self.full
            for child, columns in self.children[node]:
                bound &= image(inverse(columns), upper[child])
            if fixed[node] is not None:
                need(fixed[node] & bound == fixed[node], "Infeasible upper bound")
                bound = fixed[node]
            need(lower[node] & bound == lower[node], "Empty frame interval")
            upper[node] = bound
        self.check(lower, fixed)
        self.check(upper, fixed)
        return lower, upper

    def check(self, values, fixed=None):
        fixed = self.fixed if fixed is None else fixed
        need(len(values) == len(fixed), "Node inventory")
        for node, value in enumerate(values):
            basis(value)
            need(value & self.full == value, "Node outside ambient space")
            need(fixed[node] is None or fixed[node] == value, "Fixed node mismatch")
            for parent, columns in self.parents[node]:
                moved = image(columns, values[parent])
                need(moved & value == moved, "Mapped containment failed")

    def extend(self, node, subspace):
        return self.bounds({node: subspace})[0]


class NativeSchedule:
    """Remove paid climbs; carry each demand pointer through swaps and warps.

    Owned-cell contacts retain their supplied frames. All main/helper entrances
    and exits remain fixed. Scalar coefficients and normalized words stay fixed.
    """

    def __init__(self, canonical, program):
        self.canonical = canonical
        need(canonical["h"] == 9, "Retained nine-bit caller")
        self.spaces = list(map(space, canonical["frames"]))
        self.maps = {}
        for warp in canonical["warps"]:
            op, columns = warp["op"], tuple(warp["G_columns"])
            need(type(op) is int and op > 0 and op not in self.maps, "Warp IDs")
            self.maps[op], self.maps[-op] = columns, inverse(columns)
        self.program = [deepcopy(event) for event in program if event[0] != "climb"]
        graph = self.graph = FrameDAG(9)
        self.contacts = {}
        values = []

        def node(label=None):
            value = None if label is None else self.spaces[label]
            result = graph.node(value)
            values.append(value)
            return result

        current = [(node(label), graph.identity) for label in canonical["start"]]
        for index, event in enumerate(self.program):
            if event[0] == "weighted_swap":
                left, right = event[1:3]
                current[left], current[right] = current[right], current[left]
            elif event[0] == "warp":
                _, role, op, _, _ = event
                need(role[0] == "L" and op in self.maps, "Known live warp")
                parent, columns = current[role[1]]
                current[role[1]] = parent, compose(self.maps[op], columns)
            elif event[0] == "scalar":
                gate, label = event[1:]
                roles = gate[1:3] if gate[0] in ("add", "copy") else gate[1:2]
                live = [role[1] for role in roles if role[0] == "L"]
                if not live or gate[0] == "scale":
                    continue
                contact = node(label if len(live) < len(roles) else None)
                values[contact] = self.spaces[label]
                for role in live:
                    parent, columns = current[role]
                    graph.edge(parent, contact, columns)
                    current[role] = contact, graph.identity
                self.contacts[index] = contact
        for role, label in enumerate(canonical["final"]):
            final = node(label)
            parent, columns = current[role]
            graph.edge(parent, final, columns)
        graph.check(values)
        self.original_values = values

    def realize(self, values):
        self.graph.check(values)
        canonical = deepcopy(self.canonical)
        frames = list(self.spaces)
        labels = {subspace: label for label, subspace in enumerate(frames)}
        current = [frames[label] for label in canonical["start"]]
        result = []

        def label(subspace):
            if subspace not in labels:
                labels[subspace] = len(frames)
                frames.append(subspace)
                canonical["frames"].append(list(basis(subspace)))
            return labels[subspace]

        def climb(role, target):
            old = current[role]
            if old != target:
                need(old & target == old, "Non-nested realized climb")
                result.append(["climb", "carried", role, label(old), label(target),
                               dimension(target) - dimension(old)])
                current[role] = target

        for index, original in enumerate(self.program):
            event = deepcopy(original)
            if event[0] == "weighted_swap":
                left, right = event[1:3]
                event[5] = [label(current[left]), label(current[right])]
                current[left], current[right] = current[right], current[left]
                event[6] = [label(current[left]), label(current[right])]
            elif event[0] == "warp":
                role, op = event[1][1], event[2]
                old = current[role]
                current[role] = image(self.maps[op], old)
                event[3:] = [label(old), label(current[role])]
            elif event[0] == "scalar":
                gate = event[1]
                roles = gate[1:3] if gate[0] in ("add", "copy") else gate[1:2]
                live = [role[1] for role in roles if role[0] == "L"]
                if live:
                    target = current[live[0]] if gate[0] == "scale" else values[self.contacts[index]]
                    for role in live:
                        climb(role, target)
                    event[2] = label(target)
            result.append(event)
        for role, final in enumerate(canonical["final"]):
            climb(role, frames[final])
        return canonical, result
