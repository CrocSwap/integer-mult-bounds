"""Cancel one existing forcing path and verify the unforced dual without solving."""
from collections import defaultdict, deque
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from sys import argv


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('duplicate JSON key')
    return result


def verify(result):
    g, u = result['graph'], result['unit']
    assert u['scale'] == u['conversion_weight'] == 1
    assert u['reward_weights'] == [1]*len(g['rewards'])
    hard = u['hard_capacity']
    arcs = []
    for a, b, _ in g['gaps']:
        arcs.extend(((a, b, 1), (b, a, 1)))
    for a, b in g['equalities']:
        arcs.extend(((a, b, hard), (b, a, hard)))
    arcs.extend((v, 1, hard) for v in g['fixed'])
    arcs.extend((0, v, 1) for v, *_ in g['rewards'])
    arcs.append((0, g['forced'], hard))
    assert len(arcs) == u['network_arcs']
    flux = dict(u['positive_flow_arcs'])
    assert len(flux) == len(u['positive_flow_arcs'])
    assert all(0 <= i < len(arcs) and x > 0 for i, x in flux.items())
    def check(arc_list, values, amount):
        balance = [0]*len(g['nodes'])
        for i, (a, b, capacity) in enumerate(arc_list):
            x = values.get(i, 0)
            assert 0 <= x <= capacity
            balance[a] -= x
            balance[b] += x
        assert balance == [-amount, amount]+[0]*(len(balance)-2)
    assert u['flow_value'] == len(g['rewards'])+1
    check(arcs, flux, u['flow_value'])
    force_index = len(arcs)-1
    assert flux[force_index] == 1
    flow_adjacency = defaultdict(list)
    for i, x in sorted(flux.items()):
        if x:
            a, b, _ = arcs[i]
            if a != 0:
                flow_adjacency[a].append((i, b))
    parent = {g['forced']: None}
    queue = deque([g['forced']])
    while queue and 1 not in parent:
        v = queue.popleft()
        for i, w in flow_adjacency[v]:
            if w not in parent:
                parent[w] = i
                queue.append(w)
    v, path = 1, []
    while v != g['forced']:
        i = parent[v]
        path.append(i)
        v = arcs[i][0]
    path = [force_index]+path[::-1]
    for i in path:
        assert flux[i] >= 1
        flux[i] -= 1
    assert not flux.pop(force_index)
    check(arcs[:-1], flux, len(g['rewards']))
    assert sum(cap for a, _, cap in arcs[:-1] if a == 0) == len(g['rewards'])
    return {'cancelled_force_arc_path': path, 'flow_value': len(g['rewards']),
            'all_original_cut': len(g['rewards']), 'global_upper_units_per_port': 0,
            'no_second_solve': True, 'positive_unforced_arcs': sorted([i, x] for i, x in flux.items() if x)}


if __name__ == '__main__':
    assert __debug__ and len(argv) == 2
    raw = Path(argv[1]).read_bytes()
    output = verify(loads(raw, object_pairs_hook=unique))
    output['forced_result_sha256'] = sha256(raw).hexdigest()
    print(dumps(output, sort_keys=True, separators=(',', ':')))
