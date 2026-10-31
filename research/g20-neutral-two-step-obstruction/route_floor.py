"""Exact retained-route closure and path lower bills for G20.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Ali Romman (#5708) supplies the source route/emitter contract. Route closure and
potential lower-bound extension by worker D; independent graph review by worker B.
All calculations are integer. No predecessor executable is imported.
"""
from collections import Counter, defaultdict

def need(condition, message):
    if not condition:
        raise ValueError(message)


def graph(paths):
    edges, successors, indegree = {}, defaultdict(set), Counter()
    for key, route in paths.items():
        need(len(route) == 1 and len(route[0]) == 3, "one-edge retained route")
        a, b, rank = route[0]
        need(all(type(x) is int for x in (a, b, rank)) and a != b and 1 <= rank <= 7,
             "typed positive route rank")
        need(key == f"{a}:{b}", "route key")
        edges[a, b] = rank
        successors[a].add(b)
        indegree[b] += 1
        indegree[a] += 0
    roots = [node for node, degree in indegree.items() if degree == 0]
    need(len(roots) == 1, "unique graph root")
    level, stack = {roots[0]: 0}, roots[:]
    while stack:
        a = stack.pop()
        for b in sorted(successors[a]):
            proposed = level[a] + edges[a, b]
            if b in level:
                need(level[b] == proposed, "exact rank potential")
            else:
                level[b] = proposed
                stack.append(b)
    need(set(level) == set(indegree), "root reaches every frame")
    reachable = {node: set() for node in level}
    for a in sorted(level, key=lambda x: (level[x], x), reverse=True):
        for b in successors[a]:
            need(level[a] < level[b], "strict level increase")
            reachable[a].add(b)
            reachable[a].update(reachable[b])
    # A second graph algorithm, ordinary DFS, checks the complete closure.
    for a in level:
        found, pending = set(), list(successors[a])
        while pending:
            b = pending.pop()
            if b not in found:
                found.add(b)
                pending.extend(successors[b])
        need(found == reachable[a], "independent reachability equality")
    return edges, level, reachable


def collapsed_invoice(records, start, final, owned, level, reachable, edges):
    """Lower bill for every allowed route, retaining exact zero-row semantics."""
    values, frames = [1 << index for index in range(len(start))], list(start)
    paid, requested, paid_new = Counter(), set(), set()

    def demand(role, target):
        source = frames[role]
        if source == target:
            return None
        if source is None:
            need(role in owned and not values[role], "whole-zero owned header")
        elif target not in reachable.get(source, ()):
            return (source, target)
        else:
            requested.add((source, target))
            if values[role]:
                paid[level[target] - level[source]] += 1
                if (source, target) not in edges:
                    paid_new.add((source, target))
        frames[role] = target
        return None

    for event in records:
        op, d = event[:2]
        if op in ("INIT", "ERASE"):
            need(d in owned and (op != "INIT" or not values[d]), "owned event")
            values[d], frames[d] = 0, event[2]
            continue
        need(op == "ADD", "emission alphabet")
        s, frame = event[2:]
        if not values[s]:
            continue
        for role in (d, s):
            missing = demand(role, frame)
            if missing is not None:
                return None, missing, requested, paid_new
        values[d] ^= values[s]
    for role, frame in enumerate(final):
        if role in owned:
            need(not values[role], "owned final return")
        else:
            missing = demand(role, frame)
            if missing is not None:
                return None, missing, requested, paid_new
        frames[role] = frame
    need(frames == list(final), "every final frame included")
    return paid, None, requested, paid_new


def signed_delta(histogram, base):
    return [[r, histogram[r] - base[r]] for r in sorted(histogram.keys() | base.keys())
            if histogram[r] != base[r]]


def sign_certificate(delta):
    if not delta:
        return "zero"
    if all(c > 0 for r, c in delta):
        return "positive_terms"
    negative = [(r, -c) for r, c in delta if c < 0]
    positive = [(r, c) for r, c in delta if c > 0]
    if (len(negative) == 1 and negative[0][1] == 1
            and sum(r * c for r, c in positive) == negative[0][0]
            and sum(c for r, c in positive) >= 2):
        return "strict_subadditivity"
    raise ValueError("unproved sign shape")


def controls():
    """Named graph, row-sensitive routing and sign rejection controls."""
    cases = []
    edges, level, reach = graph({"0:1": [[0, 1, 1]], "1:2": [[1, 2, 2]]})
    need(reach[0] == {1, 2} and level[2] == 3 and (0, 2) not in edges, "transitive route")
    cases.append("new_transitive_route")
    try:
        graph({"0:1": [[0, 1, 1]], "1:2": [[1, 2, 2]], "0:2": [[0, 2, 2]]})
    except ValueError as error:
        need(str(error) == "exact rank potential", "potential rejection reason")
        cases.append("inconsistent_potential_rejected")
    else:
        raise ValueError("inconsistent potential accepted")
    fixtures = [
        ([("ADD", 0, 1, 2)], [0, 0], [2, 2], set(), {3: 2}, None, "both_nonzero_routes_paid"),
        ([("ADD", 0, 1, 2)], [2, 0], [2, 2], set(), {3: 1}, None, "unchanged_chart_free"),
        ([], [2], [0], set(), None, (2, 0), "unreachable_final_return"),
        ([("ERASE", 0, 2), ("ADD", 1, 0, 1)], [0, 0], [2, 0], {0}, {}, None, "zero_source_skips_routes"),
        ([("ERASE", 0, 0), ("ADD", 0, 1, 2), ("ERASE", 0, 2)],
         [0, 0], [2, 2], {0}, {3: 1}, None, "zero_destination_free_source_paid"),
        ([("ADD", 0, 1, 2), ("ERASE", 0, 2)], [None, 0], [2, 2], {0}, None, None, "invalid_live_none_header"),
    ]
    for records, start, final, owned, wanted, absent, name in fixtures:
        if name == "invalid_live_none_header":
            try:
                collapsed_invoice(records, start, final, owned, level, reach, edges)
            except ValueError as error:
                need(str(error) == "whole-zero owned header", "header rejection reason")
            else:
                raise ValueError("live None header accepted")
        else:
            bill, missing, _, _ = collapsed_invoice(records, start, final, owned, level, reach, edges)
            need(bill == wanted and missing == absent, name)
        cases.append(name)
    need(sign_certificate([[1, 1], [3, 1], [4, -1]]) == "strict_subadditivity", "partition sign")
    cases.append("strict_partition_loss")
    try:
        sign_certificate([[1, 1], [2, -2], [3, 1]])
    except ValueError:
        cases.append("profitable_shape_not_certified")
    else:
        raise ValueError("profitable shape accepted")
    return cases
