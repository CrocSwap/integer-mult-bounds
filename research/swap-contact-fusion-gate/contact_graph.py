"""Exact contact-graph gate after PR4971's carried-frame swaps.

Cinna Davis, substantial OpenAI Codex assistance; Apache-2.0.
This module prices abstract nested transports, not physical native programs.
"""
from collections import Counter
from functools import lru_cache

IDENTITY = tuple(1 << i for i in range(9))
FULL = (1 << 512) - 1
EXCEPTIONS = {
    ((1, -1), (2, 3), (3, -3), (4, 1)): "third_difference",
    ((1, 12), (2, -8), (3, -4), (4, 4)): "four_three_two",
    ((1, 12), (2, -9), (3, 1), (4, -3), (5, 3)): "five_four_three_two",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    values = {0}
    for v in vectors:
        values |= {w ^ v for w in tuple(values)}
    return sum(1 << v for v in values)


@lru_cache(None)
def basis(space):
    values, result = 1, []
    for v in range(1, 512):
        if space >> v & 1 and not values >> v & 1:
            result.append(v)
            values |= sum(1 << (w ^ v) for w in range(512) if values >> w & 1)
    require(values == space, "Space is not a binary subspace")
    return tuple(result)


def dimension(space):
    count = space.bit_count()
    require(count > 0 and count & (count - 1) == 0, "Subspace cardinality")
    return count.bit_length() - 1


def apply_vector(v, matrix):
    result = 0
    for j, column in enumerate(matrix):
        if v >> j & 1:
            result ^= column
    return result


@lru_cache(None)
def transform(space, matrix):
    return space if matrix == IDENTITY else span(apply_vector(v, matrix) for v in basis(space))


@lru_cache(None)
def inverse(matrix):
    values = {apply_vector(v, matrix): v for v in range(512)}
    require(len(values) == 512, "Invertible native address map")
    return tuple(values[1 << j] for j in range(9))


def compose(left, right):
    return tuple(apply_vector(v, left) for v in right)


@lru_cache(None)
def join(left, right):
    if left & right == left:
        return right
    if left & right == right:
        return left
    return span(basis(left) + basis(right))


class Graph:
    def __init__(self, canonical, program):
        self.labels, self.fixed, self.origins = [], [], []
        self.edges, self.incoming, self.outgoing = [], [], []
        self.frames = [span(vs) for vs in canonical["frames"]]
        matrices = {w["op"]: tuple(w["G_columns"]) for w in canonical["warps"]}
        matrices.update({-op: inverse(m) for op, m in list(matrices.items())})
        current = [(self.node(f, True, ["start", r]), IDENTITY)
                   for r, f in enumerate(canonical["start"])] + [None]
        live = canonical["start"][:] + [None]
        self.centers = Counter()

        def register(role):
            return role[1] + (632 if role[0] == "C" else 0)

        for position, event in enumerate(program):
            kind = event[0]
            if kind == "climb":
                _, _, r, before, after, rank = event
                require(live[r] == before, "Chronological climb input")
                require(self.frames[before] & self.frames[after] == self.frames[before], "Nested climb")
                require(rank == dimension(self.frames[after]) - dimension(self.frames[before]) > 0, "Climb rank")
                live[r] = after
            elif kind == "weighted_swap":
                _, r, s, _, _, before, after = event
                require([live[r], live[s]] == before, "Swap input charts")
                current[r], current[s] = current[s], current[r]
                live[r], live[s] = live[s], live[r]
                require([live[r], live[s]] == after, "Swap carries charts")
            elif kind == "warp":
                _, role, op, before, after = event
                r = register(role)
                require(live[r] == before, "Chronological warp input")
                require(transform(self.frames[before], matrices[op]) == self.frames[after], "Operator carries warp chart")
                n, matrix = current[r]
                current[r] = n, compose(matrices[op], matrix)
                live[r] = after
            elif kind == "scalar":
                gate, frame = event[1:]
                r = register(gate[1])
                if gate[0] == "clear":
                    require(r == 632, "Owned clear only")
                    current[r] = self.node(frame, True, [position, "clear"]), IDENTITY
                    live[r] = frame
                elif gate[0] == "copy":
                    s = register(gate[2])
                    require(r == 632 and live[s] == frame, "Owned center copy input")
                    n = self.node(frame, True, [position, "copy"])
                    self.edge(*current[s], n)
                    current[r] = current[s] = n, IDENTITY
                    live[r] = frame
                elif gate[0] == "add":
                    s = register(gate[2])
                    require(live[r] == live[s] == frame, "Scalar contact charts")
                    n = self.node(frame, r == 632 or s == 632, [position, "add"])
                    for role in (r, s):
                        self.edge(*current[role], n)
                        current[role] = n, IDENTITY
                else:
                    require(gate[0] == "scale" and live[r] == frame, "Scalar scale chart")
            elif kind == "center":
                _, _, before, after, rank = event
                require(live[632] == before, "Owned center query input")
                require(rank == abs(dimension(self.frames[before]) - dimension(self.frames[after])), "Center query rank")
                self.centers[rank] += 1
                current[632] = self.node(after, True, [position, "center"]), IDENTITY
                live[632] = after
            else:
                require(kind in ("adapter", "phase", "residual_adapter"), "Inherited event")
        require(live[:632] == canonical["final"], "All terminal charts")
        for r, frame in enumerate(canonical["final"]):
            self.edge(*current[r], self.node(frame, True, ["final", r]))
        self.validate()

    def node(self, frame, fixed, origin):
        n = len(self.labels)
        self.labels.append(self.frames[frame])
        self.fixed.append(fixed)
        self.origins.append(origin)
        self.incoming.append([])
        self.outgoing.append([])
        return n

    def edge(self, source, matrix, target):
        e = len(self.edges)
        self.edges.append((source, target, matrix))
        self.outgoing[source].append(e)
        self.incoming[target].append(e)

    def validate(self):
        for source, target, matrix in self.edges:
            image = transform(self.labels[source], matrix)
            require(image & self.labels[target] == image, "Graph edge containment")

    def histogram(self):
        result = self.centers.copy()
        for source, target, _ in self.edges:
            rank = dimension(self.labels[target]) - dimension(self.labels[source])
            if rank:
                result[rank] += 1
        return result

    def regions(self):
        parent = list(range(len(self.labels)))

        def root(n):
            while parent[n] != n:
                parent[n] = parent[parent[n]]
                n = parent[n]
            return n

        for u, v, matrix in self.edges:
            if matrix == IDENTITY and self.labels[u] == self.labels[v]:
                parent[root(u)] = root(v)
        groups = {}
        for n in range(len(parent)):
            groups.setdefault(root(n), []).append(n)
        return groups, [root(n) for n in range(len(parent))]

    def boundary(self, nodes):
        inside = set(nodes)
        incoming = [e for n in nodes for e in self.incoming[n] if self.edges[e][0] not in inside]
        outgoing = [e for n in nodes for e in self.outgoing[n] if self.edges[e][1] not in inside]
        internal = [e for n in nodes for e in self.incoming[n] if self.edges[e][0] in inside]
        lower, upper = 1, FULL
        for e in incoming:
            u, _, matrix = self.edges[e]
            lower = join(lower, transform(self.labels[u], matrix))
        for e in outgoing:
            _, v, matrix = self.edges[e]
            upper &= transform(self.labels[v], inverse(matrix))
        return incoming, outgoing, internal, lower, upper

    def local_ranks(self, incoming, outgoing, frame):
        d = dimension(frame)
        return sorted([d - dimension(self.labels[self.edges[e][0]]) for e in incoming]
                      + [dimension(self.labels[self.edges[e][1]]) - d for e in outgoing], reverse=True)


def dominates(left, right):
    require(len(left) == len(right), "Same priced edges")
    if sum(left) != sum(right):
        return False
    a = b = 0
    for x, y in zip(left, right):
        a += x
        b += y
        if a < b:
            return False
    return True


def certificate(old, new):
    if dominates(old, new):
        return "majorization"
    difference = Counter(new)
    difference.subtract(old)
    key = tuple(sorted((r, n) for r, n in difference.items() if r and n))
    require(key in EXCEPTIONS, "Unproved moment polynomial: " + str(key))
    return EXCEPTIONS[key]


@lru_cache(None)
def interval_spaces(lower, upper):
    if lower & upper != lower:
        return ()
    require(dimension(upper) - dimension(lower) <= 4, "Bounded complete quotient enumeration")
    found, pending = {lower}, [lower]
    vectors = [v for v in range(1, 512) if upper >> v & 1]
    for space in pending:
        for v in vectors:
            if not space >> v & 1:
                larger = join(space, span([v]))
                if larger not in found:
                    found.add(larger)
                    pending.append(larger)
    return tuple(sorted(found))


def study(graph):
    groups, roots = graph.regions()
    free = {r for r, ns in groups.items() if not any(graph.fixed[n] for n in ns)}
    counts, witnesses = Counter(), []
    for root in sorted(free):
        nodes = groups[root]
        inc, out, internal, lower, upper = graph.boundary(nodes)
        require(lower & upper == lower, "Nonempty one-region interval")
        gap = dimension(upper) - dimension(lower)
        require(gap <= 1, "All charts in interval enumerated")
        counts["gap_" + str(gap)] += 1
        old = graph.local_ranks(inc, out, graph.labels[nodes[0]])
        for frame in sorted({lower, upper}):
            if any(transform(frame, graph.edges[e][2]) != frame for e in internal):
                counts["operator_rejected"] += 1
                continue
            new = graph.local_ranks(inc, out, frame)
            kind = certificate(old, new)
            counts[kind] += 1
            witnesses.append([root, list(basis(frame)), old, new, kind])
    pairs = sorted({tuple(sorted((roots[u], roots[v]))) for u, v, m in graph.edges
                    if m == IDENTITY and roots[u] != roots[v] and roots[u] in free and roots[v] in free})
    fusion = []
    for left, right in pairs:
        _, _, _, lower, upper = graph.boundary(groups[left] + groups[right])
        require(lower & upper != lower, "A pair admits constant-chart fusion")
        # A literal vector in L outside U is a short, exact infeasibility witness.
        vector = next(v for v in basis(lower) if not upper >> v & 1)
        fusion.append([left, right, vector])
    adjacent = sorted({tuple(sorted((roots[u], roots[v]))) for u, v, _ in graph.edges
                       if roots[u] != roots[v] and roots[u] in free and roots[v] in free})
    pair_counts, pair_witnesses = Counter(), []
    for left, right in adjacent:
        a, b = set(groups[left]), set(groups[right])
        both = a | b
        touched = sorted({e for n in both for e in graph.incoming[n] + graph.outgoing[n]})

        def options(nodes):
            lower, upper = 1, FULL
            for n in nodes:
                for e in graph.incoming[n]:
                    u, _, matrix = graph.edges[e]
                    if u not in both:
                        lower = join(lower, transform(graph.labels[u], matrix))
                for e in graph.outgoing[n]:
                    _, v, matrix = graph.edges[e]
                    if v not in both:
                        upper &= transform(graph.labels[v], inverse(matrix))
            return interval_spaces(lower, upper)

        aa, bb = options(a), options(b)
        pair_counts["candidate_assignments"] += len(aa) * len(bb)
        old = sorted([dimension(graph.labels[graph.edges[e][1]]) - dimension(graph.labels[graph.edges[e][0]])
                      for e in touched], reverse=True)
        for fa in aa:
            for fb in bb:
                def value(n):
                    return fa if n in a else fb if n in b else graph.labels[n]

                ranks, valid = [], True
                for e in touched:
                    u, v, matrix = graph.edges[e]
                    before, after = value(u), value(v)
                    image = transform(before, matrix)
                    if image & after != image:
                        valid = False
                        break
                    ranks.append(dimension(after) - dimension(before))
                if not valid:
                    continue
                new = sorted(ranks, reverse=True)
                kind = certificate(old, new)
                pair_counts[kind] += 1
                pair_counts["feasible_assignments"] += 1
                pair_witnesses.append([left, right, list(basis(fa)), list(basis(fb)), kind])
    return {
        "nodes": len(graph.labels), "edges": len(graph.edges),
        "regions": len(groups), "free_regions": len(free),
        "paid": dict(sorted(graph.histogram().items())),
        "single_region_counts": dict(sorted(counts.items())),
        "single_region_witnesses": witnesses,
        "infeasible_identity_edge_fusions": fusion,
        "adjacent_region_pairs": len(adjacent),
        "two_region_counts": dict(sorted(pair_counts.items())),
        "two_region_witnesses": pair_witnesses,
    }
