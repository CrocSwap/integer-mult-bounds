"""Independent reverse-word inventory and edge-capacitated flow for R219."""
from collections import deque
from fractions import Fraction as Q
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    'reverse_inventory.py': 'ac01889cd8e917b5c3f93dcefaa19c159efc18bcdd6973b94b481f08185d0127',
    'inputs/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
    'inputs/7334-WORD.json.gz': '4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a',
}
WORD_PAYLOAD = '9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac'
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
SCALE = 10**49
LOWER = Q('0.00364665195644044790699554028334161')
UPPER = Q('0.00364665195644044790699554028334162')


def exact_inventory(word, trace, space):
    frames, fixed, adj, _, transport = trace(word)
    # Include untouched segments as singleton components, as well as cocharted
    # connected components from literal ADD/COPY. Reverse trace dates each
    # segment by its ending clock, independently of a forward union-find.
    component = {}
    charts = []
    allowed = set()
    main = set(word['live']) | {r + 112 for r in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    public = word['public']
    assert len(main) == 400 and public == 1501
    for root in sorted(frames):
        if root in component:
            continue
        g = len(charts)
        pending = [root]
        component[root] = g
        pure = True
        while pending:
            node = pending.pop()
            role, _ = node
            assert frames[node] == frames[root]
            pure = pure and role < public and role not in main and node not in fixed
            for peer in sorted(adj.get(node, ())):
                if peer not in component:
                    component[peer] = g
                    pending.append(peer)
                assert component[peer] == g
        charts.append(frames[root])
        if pure:
            allowed.add(g)
    points = [space(basis) for basis in word['frames']]
    ranks = list(map(len, word['frames']))
    pairs = {}
    for node, entries in transport.items():
        for clock, other_chart, side in entries:
            pair = pairs.setdefault(clock, {})
            assert side not in pair
            pair[side] = (component[node], frames[node], other_chart)
    edges = []
    for clock, pair in sorted(pairs.items()):
        lower, lc, a = pair['source']
        upper, uc, b = pair['target']
        assert a == uc and b == lc and lower != upper
        if lower not in allowed and upper not in allowed:
            continue
        assert points[lc] < points[uc]
        assert word['program'][clock][0] == 'MOVE' and word['program'][clock][-1] is False
        edges.append((lower, upper, ranks[uc]-ranks[lc]))
    spaces = [points[c] for c in charts]
    return spaces, allowed, edges


def arc(graph, u, v, capacity):
    assert u != v and capacity > 0
    graph[u][v] = graph[u].get(v, 0) + capacity
    graph[v].setdefault(u, 0)


def push_until_cut(graph, s, t, offered):
    """Shortest augmenting paths, using the explicit bidirectional residual."""
    flow, augmentations = 0, 0
    while flow < offered:
        parent = {s: None}
        queue = deque([s])
        while queue and t not in parent:
            u = queue.popleft()
            for v, capacity in graph[u].items():
                if capacity and v not in parent:
                    parent[v] = u
                    queue.append(v)
        if t not in parent:
            return flow, augmentations, set(parent)
        v = t
        send = offered - flow
        while v != s:
            u = parent[v]
            send = min(send, graph[u][v])
            v = u
        v = t
        while v != s:
            u = parent[v]
            graph[u][v] -= send
            graph[v][u] += send
            v = u
        flow += send
        augmentations += 1
    return flow, augmentations, {s}


def reduce_edges(v, spaces, allowed, edges, increment):
    active = [g for g in sorted(allowed) if v not in spaces[g]]
    index = {g: i for i, g in enumerate(active)}
    source, sink = len(active), len(active) + 1
    graph = [{} for _ in range(len(active) + 2)]
    total = 0
    hard = set()
    finite_count = 0
    for lower, upper, d in edges:
        x, y = index.get(lower), index.get(upper)
        if x is None and y is None:
            continue
        if v in spaces[upper]:
            assert x is not None and y is None
            reward = increment[d][1]
            arc(graph, source, x, reward)
            total += reward
            finite_count += 1
            continue
        # Changed lower frame requires changed upper frame in this case.
        if x is not None:
            hard.add((x, y if y is not None else sink))
        # A cut pays for changing U alone, including a fixed lower frame.
        if y is not None:
            penalty = increment[d + 1][0]
            arc(graph, y, x if x is not None else sink, penalty)
            finite_count += 1
    for x, y in sorted(hard):
        arc(graph, x, y, total + 1)
    flow, augmentations, cut = push_until_cut(graph, source, sink, total)
    assert all(x not in cut or y in cut for x, y in hard)
    return {'vector': v, 'variables': len(active), 'implications': len(hard),
            'finite_arc_occurrences': finite_count, 'source_benefit_scaled': total,
            'flow_scaled': flow, 'upper_scaled': total - flow,
            'augmenting_paths': augmentations}


def control():
    # Adding the lower frame gives 5, requires adding its upper neighbor,
    # and thus incurs 3. A fixed upper frame changes the optimum back to zero.
    graph = [{} for _ in range(4)]
    for u, v, c in ((2, 0, 5), (0, 1, 6), (1, 3, 3)):
        arc(graph, u, v, c)
    f, _, cut = push_until_cut(graph, 2, 3, 5)
    assert f == 3 and cut == {0, 1, 2}
    graph = [{} for _ in range(4)]
    for u, v, c in ((2, 0, 5), (0, 1, 6), (1, 3, 6)):
        arc(graph, u, v, c)
    f, _, cut = push_until_cut(graph, 2, 3, 5)
    assert f == 5 and cut == {2}


def stop(*_):
    raise TimeoutError('60-second binary-vector flow cap')


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(60)
    for path, digest in PINS.items():
        assert sha256((ROOT / path).read_bytes()).hexdigest() == digest
    data = decompress((ROOT / 'inputs' / '7334-WORD.json.gz').read_bytes())
    assert sha256(data).hexdigest() == WORD_PAYLOAD
    word = loads(data)
    assert len(word['program']) == 76466
    inv = run_path(str(ROOT / 'reverse_inventory.py'))
    spaces, allowed, edges = exact_inventory(word, inv['reverse_trace'], inv['frame_space'])
    assert len(allowed) == 482 and len(edges) == 2292
    tariff = run_path(str(ROOT / 'inputs' / 'pricing.py'))['power_bounds']
    bounds = [(Q(0), Q(0))] + [(tariff(r, UPPER)[0], tariff(r, LOWER)[1]) for r in range(1, 10)]
    increment = {}
    for r in range(1, 10):
        lo, hi = (bounds[r][0] - bounds[r-1][1]) * SCALE, (bounds[r][1] - bounds[r-1][0]) * SCALE
        assert lo.denominator == hi.denominator == 1 and 0 < lo <= hi
        increment[r] = (int(lo), int(hi))
    control()
    outcomes = []
    try:
        for v in range(1, 512):
            outcomes.append(reduce_edges(v, spaces, allowed, edges, increment))
    except TimeoutError:
        print(dumps(dict(capped=True, results=outcomes), sort_keys=True, indent=2))
        raise SystemExit(2)
    finally:
        alarm(0)
    print(dumps(dict(head=HEAD, caller=CALLER, pins=PINS, groups=len(spaces),
                     eligible_groups=len(allowed), incident_edges=len(edges), scale=SCALE,
                     runner_cap_seconds=60, vector_cap=511, capped=False,
                     increments=increment, results=outcomes), sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
