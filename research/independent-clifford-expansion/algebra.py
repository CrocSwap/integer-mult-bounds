"""Exact inverse-chart geometry for independently changed Clifford gauges.

Apache-2.0. Cinna Davis, with substantial OpenAI Codex assistance.
The chronological graph and source word are credited to PR4610 and
research/general-gaussian-contact-search; see SOURCES.json and README.md.
"""
from collections import Counter
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def predecessor():
    path = ROOT / 'research/general-gaussian-contact-search/model.py'
    spec = importlib.util.spec_from_file_location('independent_chart_source', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def canonical(rows):
    pivots = {}
    for row in rows:
        for pivot in sorted(pivots, reverse=True):
            if row >> pivot & 1:
                row ^= pivots[pivot]
        if row:
            pivot = row.bit_length() - 1
            for other in list(pivots):
                if pivots[other] >> pivot & 1:
                    pivots[other] ^= row
            pivots[pivot] = row
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def pairing(a, b, n):
    low = (1 << n) - 1
    return (((a & low) & (b >> n)).bit_count() +
            ((a >> n) & (b & low)).bit_count()) % 2


def distance(a, b, n):
    return len(canonical((*a, *b))) - n


def turn(space, axis, n):
    return canonical(v ^ (axis if pairing(v, axis, n) else 0) for v in space)


def linear(columns, value):
    result = 0
    while value:
        bit = value & -value
        result ^= columns[bit.bit_length() - 1]
        value ^= bit
    return result


def neighbors(space, n):
    """All 2*(2**n-1) distinct Lagrangians at distance one.

    Select one dual representative for each nonzero functional on space.
    Adding a vector on which that functional is one gives the other neighbor.
    Each returned axis is an actual Pauli transvection taking space there.
    """
    dual = [None] * n
    images = {}
    for bit in range(2*n):
        value = sum(pairing(v, 1 << bit, n) << j for j, v in enumerate(space))
        axis = 1 << bit
        for pivot in sorted(images, reverse=True):
            if value >> pivot & 1:
                old, lift = images[pivot]
                value ^= old
                axis ^= lift
        if value:
            images[value.bit_length()-1] = value, axis
    need(len(images) == n, 'Lagrangian pairing map is surjective')
    for j in range(n):
        value, axis = 1 << j, 0
        for pivot in sorted(images, reverse=True):
            if value >> pivot & 1:
                old, lift = images[pivot]
                value ^= old
                axis ^= lift
        need(value == 0, 'exact dual solution')
        dual[j] = axis
    for functional in range(1, 1 << n):
        axis = linear(dual, functional)
        pivot = (functional & -functional).bit_length()-1
        for candidate in (axis, axis ^ space[pivot]):
            yield candidate, turn(space, candidate, n)


def build(collapse_zero=True):
    source = predecessor()
    payload = source.load(ROOT / 'research/general-gaussian-contact-search/inputs/round3-word.json.gz')
    nodes, edges, fixed, _ = source.graph(payload, 'free')
    parent = list(range(len(nodes)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    if collapse_zero:
        for kind, a, b, rank, _ in edges:
            if kind == 'paid' and rank == 0:
                need(nodes[a] == nodes[b], 'zero-edge canonical frames agree')
                parent[find(b)] = find(a)
    roots = sorted({find(i) for i in range(2, len(nodes))})
    index = {r: i for i, r in enumerate(roots)}
    group = {i: index[find(i)] for i in range(2, len(nodes))}
    frames = payload['canonical']['frames']
    charts = [canonical(source.lagrangian(frames[nodes[r]], 9)) for r in roots]
    frozen = sorted({group[i] for i in fixed})
    maps = {w['op']: w['G_columns'] for w in payload['canonical']['warps']}
    maps.update({-op: source.inv(g) for op, g in list(maps.items())})
    operators = {}
    for op, g in maps.items():
        inverse = source.inv(g)
        inverse_t = [sum(((inverse[j] >> i) & 1) << j for j in range(9)) for i in range(9)]
        def image(v):
            x, z = v & 511, v >> 9
            gx = source.mv(g, x)
            return gx | ((source.mv(inverse_t, x ^ z) ^ gx) << 9)
        operators[op] = tuple(image(1 << bit) for bit in range(18))
    warp_ops = iter(e[2] for e in payload['programs']['forward'] if e[0] == 'warp')
    contacts = []
    for kind, a, b, rank, _ in edges:
        op = next(warp_ops) if kind == 'warp' else 0
        ga, gb = group[a], group[b]
        if ga == gb and op == 0:
            continue
        contacts.append((ga, gb, op, 1))
    for role in range(224, 632):
        a, b = 2 + role, len(nodes) - 632 + role
        contacts.append((group[a], group[b], 0, -1))
    centers = Counter(e[4] for e in payload['programs']['forward'] if e[0] == 'center')
    model = dict(width=9, charts=charts, frozen=frozen, operators=operators,
                 contacts=contacts, groups=[group[i] for i in range(2, len(nodes))],
                 centers=dict(centers), original_nodes=len(nodes)-2,
                 collapse_zero=collapse_zero)
    paid, helper = invoice(model, charts)
    expected = Counter(e[5] for e in payload['programs']['forward'] if e[0] == 'climb') + centers
    need(paid == expected, 'entire original paid invoice, including centers')
    need(helper == Counter({4: 28, 7: 7, 8: 47, 9: 326}), 'all 408 arbitrary helpers')
    return model


def invoice(model, charts):
    n = model['width']
    need(len(charts) == len(model['charts']), 'complete chart assignment')
    for i in model['frozen']:
        need(tuple(charts[i]) == tuple(model['charts'][i]), 'frozen main/owned/adapter chart')
    for chart in charts:
        need(len(canonical(chart)) == n and all(0 < x < (1 << (2*n)) for x in chart), 'full chart dimension')
        need(all(pairing(a, b, n) == 0 for a in chart for b in chart), 'isotropic chart')
    paid, helpers = Counter(model['centers']), Counter()
    for a, b, op, sign in model['contacts']:
        left = tuple(linear(model['operators'][op], v) for v in charts[a]) if op else charts[a]
        rank = distance(left, charts[b], n)
        if sign == -1:
            need(rank > 0, 'each helper remains strictly productive')
            helpers[rank] += 1
        elif rank:
            paid[rank] += 1
    return paid, helpers
