"""Reverse inventory and edge-capacity verification for R222/R223."""
from collections import defaultdict
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from math import ceil, floor
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv

ROOT = Path(__file__).resolve().parent
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PINS = {
    'inputs/7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
    'inputs/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'reverse_inventory.py': 'ac01889cd8e917b5c3f93dcefaa19c159efc18bcdd6973b94b481f08185d0127',
    'cut_flow.py': 'a16c67f11d216d0a7d7f4caf0b994cc0a1dcbc01d667ed0924691f72f0959cdb',
}
PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
SCALE = 10**52


def inventory(word, rev):
    frames, fixed, adjacent, _, transport = rev['reverse_trace'](word)
    main = set(word['live']) | {r+112 for r in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    public = word['public']
    assert public == 1501 and len(main) == 400
    helper = set(range(public)) - main
    component, charts, allowed = {}, [], []
    for root in sorted(frames):
        if root in component:
            continue
        i = len(charts)
        component[root] = i
        pending = [root]
        pure = True
        while pending:
            node = pending.pop()
            assert frames[node] == frames[root]
            pure = pure and node[0] in helper
            for peer in sorted(adjacent.get(node, ())):
                if peer not in component:
                    component[peer] = i
                    pending.append(peer)
                assert component[peer] == i
        charts.append(frames[root])
        if pure:
            allowed.append(i)
    chart_points = list(map(rev['frame_space'], word['frames']))
    points = [chart_points[c] for c in charts]
    ranks = [len(word['frames'][c]) for c in charts]
    allowed_set = set(allowed)
    paid_ends = defaultdict(dict)
    for node, rows in transport.items():
        for t, other, side in rows:
            assert side not in paid_ends[t]
            paid_ends[t][side] = (component[node], other)
    edges = []
    for t, pair in sorted(paid_ends.items()):
        a, upper_chart = pair['source']
        b, lower_chart = pair['target']
        assert charts[a] == lower_chart and charts[b] == upper_chart
        if a not in allowed_set and b not in allowed_set:
            continue
        assert points[a] < points[b] and word['program'][t][-1] is False
        edges.append((a, b, ranks[b]-ranks[a], True))
    ends = defaultdict(list)
    for node in fixed:
        ends[node[0]].append(node)
    for r in sorted(helper):
        end = (r, len(word['program']))
        start, = set(ends[r]) - {end}
        assert end in fixed and frames[start] == word['initial'][r] and frames[end] == word['final'][r]
        a, b = component[start], component[end]
        if a not in allowed_set and b not in allowed_set:
            continue
        assert points[a] < points[b]
        edges.append((a, b, ranks[b]-ranks[a], False))
    return points, allowed, edges


def compile_edges(v, points, allowed, edges):
    active = [g for g in allowed if v not in points[g]]
    index = {g: i for i, g in enumerate(active)}
    s, t = len(active), len(active)+1
    hard, terms = set(), []
    for a, b, d, paid in edges:
        x, y = index.get(a), index.get(b)
        if x is None and y is None:
            continue
        if v in points[b]:
            assert x is not None and y is None
            if paid:
                terms.append((s, x, d, True))
            elif d == 1:
                hard.add((x, t))
            else:
                terms.append((x, t, d, False))
            continue
        if x is not None:
            hard.add((x, y if y is not None else t))
        if paid:
            if y is not None:
                terms.append((y, x if x is not None else t, d+1, False))
        else:
            # Nesting forces x <= y, so a reward c for (y,x)=(1,0)
            # equals c*y - c*x on every allowed cut.
            if y is not None:
                terms.append((s, y, d+1, True))
            if x is not None:
                terms.append((x, t, d+1, True))
    return s, t, sorted(hard), terms


def flow_value(frozen, reward, penalty, push, arc, *, cancel=False):
    s, t, hard, terms = frozen
    graph = [{} for _ in range(t+1)]
    offered = 0
    for u, v, rank, good in terms:
        cap = reward[rank] if good else penalty[rank]
        arc(graph, u, v, cap)
        if u == s:
            offered += cap
    if cancel:
        # A source-to-sink cut crosses exactly one terminal arc at each
        # variable. Subtract their common minimum from all cuts and offered.
        for node in range(s):
            common = min(graph[s].get(node, 0), graph[node].get(t, 0))
            if common:
                graph[s][node] -= common
                graph[node][t] -= common
                offered -= common
    for u, v in hard:
        arc(graph, u, v, offered+1)
    flow, _, cut = push(graph, s, t, offered)
    assert all(u not in cut or v in cut for u, v in hard)
    return offered-flow


def control(push, arc):
    # A target reward adds +5 only if the upper grows alone. One paid
    # charge of 3 for that upper gives +2. Coupling it to an additional
    # finite penalty of 4 makes the upper unprofitable.
    terms = [(2, 1, 1, True), (0, 3, 1, True), (1, 3, 2, False)]
    for cancel in (False, True):
        assert flow_value((2, 3, [(0, 1)], terms),
                          [0, 5, 3], [0, 5, 3], push, arc, cancel=cancel) == 2
        assert flow_value((2, 3, [(0, 1)], terms+[(1, 3, 3, False)]),
                          [0, 5, 3, 4], [0, 5, 3, 4], push, arc, cancel=cancel) == 0


def stop(*_):
    raise TimeoutError('60-second endpoint shared-price cap')


def main():
    assert __debug__
    assert len(argv) in (1, 6)
    if len(argv) == 1:
        first, last, skip, cap, mode = 1, 511, 0, 60, 'cancel'
    else:
        first, last, skip, cap = map(int, argv[1:5])
        mode = argv[5]
    assert 1 <= first <= last <= 511 and 0 <= skip < 18 and 1 <= cap <= 60
    assert mode in ('direct', 'cancel')
    cancel = mode == 'cancel'
    signal(SIGALRM, stop)
    alarm(cap)
    for name, pin in PINS.items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == pin
    raw = decompress((ROOT / 'inputs/7334-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest() == PAYLOAD
    word = loads(raw)
    assert len(word['program']) == 76466
    rev = run_path(str(ROOT / 'reverse_inventory.py'))
    points, allowed, edges = inventory(word, rev)
    targets, paid = sum(not e[-1] for e in edges), sum(e[-1] for e in edges)
    assert (len(points), len(allowed), paid, targets) == (1517, 553, 2573, 193)
    flow = run_path(str(ROOT / 'cut_flow.py'))
    push, arc = flow['push_until_cut'], flow['arc']
    control(push, arc)
    tariff = run_path(str(ROOT / 'inputs/pricing.py'))['power_bounds']
    k0 = Q('0.00364665195644044790699554028334161')
    k1 = Q('0.00364665195644044790699554028334162')
    h = [(Q(0), Q(0))] + [(tariff(r, k1)[0], tariff(r, k0)[1]) for r in range(1, 10)]
    lo = [0] + [floor(SCALE*(h[r][0]-h[r-1][1])) for r in range(1, 10)]
    hi = [0] + [ceil(SCALE*(h[r][1]-h[r-1][0])) for r in range(1, 10)]
    assert all(0 < a <= b for a, b in zip(lo[1:], hi[1:], strict=True))
    midpoint = [a+b for a,b in zip(lo, hi, strict=True)]
    radius = sum(b-a for a,b in zip(lo, hi, strict=True))
    assert 0 < radius < min(midpoint[1:])
    vertices = []
    for rank in range(1, 10):
        for sign in (-1, 1):
            p = midpoint.copy()
            p[rank] += sign*radius
            vertices.append(p)
    rows, rounding, partial = [], [], None
    capped = False
    try:
        for v in range(first, last+1):
            frozen = compile_edges(v, points, allowed, edges)
            if v != first or not skip:
                rounding.append([v, frozen[0], flow_value(frozen, lo, hi, push, arc, cancel=cancel),
                                 flow_value(frozen, hi, lo, push, arc, cancel=cancel)])
            partial = [v, []]
            for price in vertices[skip if v == first else 0:]:
                partial[1].append(flow_value(frozen, price, price, push, arc, cancel=cancel))
            rows.append(partial)
            partial = None
    except TimeoutError:
        capped = True
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, groups=len(points), eligible_groups=len(allowed),
                     paid_edges=paid, target_edges=targets, increment_scale=SCALE, scale=2*SCALE,
                     box=list(zip(lo[1:],hi[1:],strict=True)), center=midpoint[1:], radius=radius,
                     vertices=len(vertices), vectors=len(rows), cap_seconds=cap,
                     first_vector=first, last_vector=last, skip_first_vertices=skip, mode=mode,
                     rounding=rounding, rows=rows, partial_row=partial,
                     max=max((max(values) for _,values in rows),default=None),capped=capped),
                indent=2,sort_keys=True))
    if capped:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
