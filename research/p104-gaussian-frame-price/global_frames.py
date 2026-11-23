"""Exact maximum-closure certificate for joint common-line and common-hyperplane frame changes."""

from collections import Counter, deque
from fractions import Fraction as Q
from functools import cache
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from geometry import space_mask
from verify import tariff, UNIT

PROJ_SHA = "dc5f08a2499662a0d228583aa0fd092b1946bea7b2657899a22fbe46bcf4123c"
RANKS = range(1, 10)
PRICE = tuple([(0, 0)] + [tariff(k) for k in RANKS])


def load_input():
    data = gzip.decompress((HERE / "source-projection.json.gz").read_bytes())
    assert sha256(data).hexdigest() == PROJ_SHA
    g = json.loads(data)
    starts, ends = g["initial"], g["final"]
    anchored = {roles[i] for roles in (starts, ends) for i in g["main_roles"]}
    spaces = [space_mask(v) for v in g["frames"]]
    dims = list(map(len, g["frames"]))
    incidence = Counter()
    helpers = set()

    def put(a, b, units):
        if dims[a] > dims[b]:
            a, b = b, a
        assert spaces[a] & spaces[b] == spaces[a] and dims[a] < dims[b]
        incidence[a, b] += units

    fixed_unit = 0
    for _, a, b in g["moves"]:
        put(a, b, -1)
        fixed_unit += a in anchored and b in anchored and abs(dims[a] - dims[b]) == 1
    main = set(g["main_roles"])
    for i, (a, b) in enumerate(zip(starts, ends, strict=True)):
        if i not in main:
            assert dims[a] < dims[b]
            put(a, b, 1)
            helpers.add((a, b))
    # Keep every geometric edge, including one with zero net price coefficient.
    edges = tuple(
        (a, b, dims[b] - dims[a], w, (a, b) in helpers)
        for (a, b), w in sorted(incidence.items())
    )
    vertices = {item for a, b, *_ in edges for item in (a, b)}
    assert (len(anchored), len(vertices - anchored), len(edges), fixed_unit) == (
        210,
        768,
        2958,
        847,
    )
    templates = len(g["moves"]) + len(starts) - len(main)
    assert templates == 6565 and dict(g["fixed_paid"])[1] + 48 * fixed_unit == 41136
    assert (g["native_calls"], g["splits"], g["weights"], g["scales"]) == (
        48,
        1008,
        [5, 451],
        [1, 2],
    )
    return g, anchored, spaces, edges, templates, fixed_unit


def model(changing, anchored, edges, kind, allow_paid_contractions):
    # Each coefficient vector is an exact signed difference of grade multiplicities.
    n = len(changing)
    coeff = [[0] * 10 for _ in range(n)]
    forbidden = set(anchored)
    implications = set()
    active = set()
    for a, b, r, w, helper in edges:
        if changing[a]:
            active.add(a)
        if changing[b]:
            active.add(b)
        if changing[a] and changing[b]:
            must, other = (a, b) if kind == "grow" else (b, a)
            implications.add((must, other))
            coeff[other][r + 1] += w
            coeff[other][r] -= w
            coeff[must][r + 1] -= w
            coeff[must][r] += w
        elif changing[a] or changing[b]:
            who = a if changing[a] else b
            assert (who == a) == (kind == "grow")
            if r == 1 and (helper or not allow_paid_contractions):
                forbidden.add(who)
            else:
                coeff[who][r - 1] += w
                coeff[who][r] -= w
    reverse = {}
    for a, b in implications:
        reverse.setdefault(b, []).append(a)
    stack = list(forbidden)
    while stack:
        for other in reverse.get(stack.pop(), ()):
            if other not in forbidden:
                forbidden.add(other)
                stack.append(other)
    sites = sorted(active - forbidden)
    index = {v: i for i, v in enumerate(sites)}
    arcs = sorted((index[a], index[b]) for a, b in implications if a in index)
    return sites, [tuple(coeff[v]) for v in sites], arcs


@cache
def prices(coeff):
    mid = sum(n * (lo + hi) for n, (lo, hi) in zip(coeff, PRICE))
    upper = sum(max(n * lo, n * hi) for n, (lo, hi) in zip(coeff, PRICE))
    return mid, upper


def optimize(profits, implications, hard_floor=1):
    n = len(profits)
    s = n
    t = n + 1
    funds = sum(v for v in profits if v > 0)
    hard = 2 * (funds + hard_floor)
    graph = [[] for _ in range(n + 2)]
    dest = []
    res = []
    edges = []

    def edge(u, v, c):
        if not c:
            return
        j = len(res)
        graph[u].append(j)
        graph[v].append(j + 1)
        dest.extend([v, u])
        res.extend([c, 0])
        edges.append((u, v, c))

    for j, v in enumerate(profits):
        if v > 0:
            edge(s, j, v)
        elif v < 0:
            edge(j, t, -v)
    for u, v in implications:
        edge(u, v, hard)
    flow = 0
    while True:
        levels = [-1] * (n + 2)
        levels[s] = 0
        queue = deque([s])
        while queue:
            u = queue.popleft()
            for j in graph[u]:
                v = dest[j]
                if res[j] and levels[v] < 0:
                    levels[v] = levels[u] + 1
                    queue.append(v)
        if levels[t] < 0:
            break
        pointers = [0] * (n + 2)

        def push(u, budget):
            if u == t:
                return budget
            while pointers[u] < len(graph[u]):
                j = graph[u][pointers[u]]
                v = dest[j]
                if res[j] and levels[u] + 1 == levels[v]:
                    sent = push(v, min(res[j], budget))
                    if sent:
                        res[j] -= sent
                        res[j ^ 1] += sent
                        return sent
                pointers[u] += 1
            return 0

        while True:
            added = push(s, hard)
            if not added:
                break
            flow += added
    # Validate the primal and dual certificate independently of augmentation order.
    balance = [0] * (n + 2)
    out = [[] for _ in range(n + 2)]
    back = [[] for _ in range(n + 2)]
    min_positive = None
    for j, (u, v, c) in enumerate(edges):
        forward = res[2 * j]
        reverse = res[2 * j + 1]
        assert forward >= 0 and reverse >= 0 and forward + reverse == c
        balance[u] -= reverse
        balance[v] += reverse
        for first, last, qty in [(u, v, forward), (v, u, reverse)]:
            if qty:
                out[first].append(last)
                back[last].append(first)
                min_positive = qty if min_positive is None else min(min_positive, qty)
    assert balance == [0] * n + [-flow, flow]
    cut = {i for i, depth in enumerate(levels[:n]) if depth >= 0}
    assert all(u not in cut or v in cut for u, v in implications)
    value = sum(profits[v] for v in cut)
    assert value == funds - flow
    return value, cut, out, back, min_positive


def components(graph, reverse, which):
    # Kosaraju on the induced free residual graph.
    finished = []
    seen = set()
    for root in which:
        if root in seen:
            continue
        seen.add(root)
        stack = [(root, 0)]
        while stack:
            u, p = stack[-1]
            if p == len(graph[u]):
                finished.append(u)
                stack.pop()
            else:
                v = graph[u][p]
                stack[-1] = (u, p + 1)
                if v in which and v not in seen:
                    seen.add(v)
                    stack.append((v, 0))
    seen.clear()
    for root in reversed(finished):
        if root in seen:
            continue
        comp = []
        seen.add(root)
        stack = [root]
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in reverse[u]:
                if v in which and v not in seen:
                    seen.add(v)
                    stack.append(v)
        yield comp


def reach(graph, root):
    seen = {root}
    stack = [root]
    while stack:
        for v in graph[stack.pop()]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return seen


def hist(coeff, chosen):
    return tuple(sum(coeff[i][j] for i in chosen) for j in range(10))


def check_one(g, fixed, spaces, edges, kind, v, err):
    active = (
        [not bool(p & (1 << v)) for p in spaces]
        if kind == "grow"
        else [any((a & v).bit_count() % 2 for a in basis) for basis in g["frames"]]
    )
    sites, coeff, arcs = model(active, fixed, edges, kind, True)
    p = [prices(h) for h in coeff]
    upper, upper_choice, *_ = optimize([b for a, b in p], arcs)
    assert upper == 0 and not upper_choice
    top, cut, out, back, gap = optimize([a for a, b in p], arcs, hard_floor=2 * UNIT)
    assert top == 0 and not cut
    s = len(sites)
    t = s + 1
    forced = reach(out, s) - {s}
    nonfree = reach(back, t)
    assert not forced and s not in nonfree
    free = set(range(s)) - nonfree
    zero = 0
    for comp in components(out, back, free):
        assert not any(hist(coeff, comp)), (kind, v, comp, hist(coeff, comp))
        zero += 1
    assert gap is None or gap > err
    return dict(sites=s, gap=gap, neutral_components=zero, free=len(free))


def toy_oracle():
    """Compare every subset against literal point sets, then verify optimum by enumeration."""
    # Include an anchored lower/upper endpoint, a zero-net helper pair, mixed weights,
    # and rank-one paid-only pairs admitting equality in the relaxation.
    frames = [
        {0},
        {0, 1},
        {0, 1, 2, 3},
        set(range(8)),
        {0, 2},
        {0, 2, 4, 6},
        {0, 4},
        {0, 1, 4, 5},
    ]
    edges = [
        (0, 1, 1, -2, False),
        (1, 2, 1, 3, True),
        (2, 3, 1, -1, False),
        (4, 2, 1, 1, True),
        (4, 5, 1, -1, False),
        (5, 3, 1, 2, True),
        (0, 2, 2, 2, True),
        (0, 5, 2, -3, False),
        (6, 5, 1, 0, True),
        (6, 7, 1, -1, False),
        (7, 3, 1, 2, True),
    ]
    anchors = {0, 3}
    tested = legal = contracted = positive = 0
    for kind in ("grow", "shrink"):
        for v in range(1, 8):
            trial = [
                (
                    f | {p ^ v for p in f}
                    if kind == "grow"
                    else {p for p in f if (p & v).bit_count() % 2 == 0}
                )
                for f in frames
            ]
            changing = [f != t for f, t in zip(frames, trial)]
            possible = [i for i, c in enumerate(changing) if c and i not in anchors]
            for relaxed in (False, True):
                sites, coeff, arcs = model(changing, anchors, edges, kind, relaxed)
                site_set = set(sites)
                true_profits = []
                upper_profits = []
                for size in range(len(possible) + 1):
                    for subset in combinations(possible, size):
                        tested += 1
                        chosen = set(subset)
                        actual = [
                            trial[i] if i in chosen else f for i, f in enumerate(frames)
                        ]
                        fits = all(
                            (
                                actual[a] < actual[b]
                                if helper or not relaxed
                                else actual[a] <= actual[b]
                            )
                            for a, b, _, _, helper in edges
                        )
                        ids = {i for i, x in enumerate(sites) if x in chosen}
                        permitted = chosen <= site_set and all(
                            a not in ids or b in ids for a, b in arcs
                        )
                        assert fits == permitted
                        if not fits:
                            continue
                        legal += 1
                        contracted += any(actual[a] == actual[b] for a, b, *_ in edges)
                        literal = [0] * 10
                        for a, b, r, w, _ in edges:
                            grade = (
                                len(actual[b]).bit_length()
                                - len(actual[a]).bit_length()
                            )
                            literal[grade] += w
                            literal[r] -= w
                        assert tuple(literal) == hist(coeff, ids)
                        nominal, direct_upper = prices(tuple(literal))
                        vertex_upper = sum(prices(coeff[j])[1] for j in ids)
                        assert nominal <= 2 * direct_upper <= 2 * vertex_upper
                        true_profits.append(nominal)
                        upper_profits.append(vertex_upper)
                expected = max(true_profits)
                actual, *_ = optimize([prices(h)[0] for h in coeff], arcs)
                assert actual == expected
                upper_optimum, *_ = optimize([prices(h)[1] for h in coeff], arcs)
                assert upper_optimum == max(upper_profits)
                positive += expected > 0
    assert 0 < contracted < legal < tested and 0 < positive < 28
    # A four-vertex independent closure control exercises a nonempty optimum.
    value, selected, *_ = optimize([6, -2, 2, -8], [(0, 1), (2, 3)])
    assert (value, selected) == (4, {0, 1})
    return dict(
        families=28,
        selections=tested,
        legal=legal,
        legal_with_contraction=contracted,
        positive_optima=positive,
        hand_closure_value=value,
    )


def run():
    g, fixed, spaces, edges, count, unit_moves = load_input()
    width = max(b - a for a, b in PRICE)
    err = 2 * count * width
    assert Q(err, 2 * UNIT) == Q(141523958955377375, UNIT)
    result = {
        "target": "39/10000",
        "projection_sha256": PROJ_SHA,
        "anchored_main_charts": len(fixed),
        "mutable_active_charts": 768,
        "incidence_pairs": len(edges),
        "signed_terms_per_native": count,
        "anchored_unit_paid_moves_per_native": unit_moves,
        "guaranteed_paid_unit_roles_in_48_call_invoice": dict(g["fixed_paid"])[1]
        + 48 * unit_moves,
        "split_count": g["splits"],
        "tariff_scale": str(UNIT),
        "rounding_budget_doubled_grid": str(err),
        "midpoint_only_upper_gain_per_native": str(Q(err, 2 * UNIT)),
        "true_maximum_gain_per_native": "0",
        "toy": toy_oracle(),
    }
    for kind in ("grow", "shrink"):
        vals = [check_one(g, fixed, spaces, edges, kind, v, err) for v in range(1, 512)]
        result[kind] = {
            "cases": len(vals),
            "zero_midpoint_maxima": len(vals),
            "zero_directed_upper_maxima": len(vals),
            "min_positive_residual_doubled_grid": str(
                min(x["gap"] for x in vals if x["gap"] is not None)
            ),
            "free_components": sum(x["neutral_components"] for x in vals),
            "max_free_sites": max(x["free"] for x in vals),
            "max_active_sites": max(x["sites"] for x in vals),
        }
    return result


if __name__ == "__main__":
    observed = run()
    expected = json.loads((HERE / "GLOBAL-FRAMES.json").read_text())
    assert expected == observed, "joint frame result differs from the recorded receipt"
    print(
        "PASS_GLOBAL_FRAME_CLOSURE: 1022 exact zero upper profits, 1022 midpoint duals, "
        "288 neutral residual components and 736 literal toy selections"
    )
