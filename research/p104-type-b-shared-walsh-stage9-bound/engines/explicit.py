"""Explicit role-contact graph and integral max-flow dual for the stage-9 Walsh window."""
from collections import Counter, deque
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from math import lcm
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

HERE = Path(__file__).resolve().parent
HEAD = 'aaeec8c0acf01e99a5f331ef363a698d9c084ace'
CALLER = '07a76c5e2738882c0cb322278e56f6cae3c9885d'
PREDECESSOR = 'c44a551b92786725cc2b805d6cf3b2547e66d711'
PINS = {
    'inputs/CALLER.json': '255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc',
    'inputs/R180-LEAD.json': '4c277906e28c6fc95882cc572423f040858ef210872eb8949b7b4a0fe4af792d',
    'inputs/R92-PRICE.json': '05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f',
    'inputs/pricing.py': 'f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182',
}
CLOCK, STAGE, LIMIT = 2866, 9, 60
ROLES = tuple(range(36, 72))
PORTS = (15, 17, 27, 34, 35, 42, 47, 55)
SOURCE, SINK = 0, 1


def unique(pairs):
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError('duplicate JSON key')
    return result


def read(name):
    raw = (HERE/name).read_bytes()
    assert sha256(raw).hexdigest() == PINS[name], name
    return loads(raw, object_pairs_hook=unique) if name.endswith('.json') else raw


def graph(tape):
    nodes = [['source'], ['sink']]
    gaps, equalities, fixed, odd, rewards = [], [], [], [], []
    last = {}
    counts = Counter()
    forced = None

    def node(clock, role):
        assert role in ROLES
        nodes.append([clock, role])
        return len(nodes)-1

    def attach(clock, role):
        vertex = node(clock, role)
        gaps.append([last[role], vertex, role])
        assert nodes[last[role]][0] < clock
        last[role] = vertex
        return vertex

    for role in ROLES:
        last[role] = node(-1, role)
        fixed.append(last[role])
    for clock, event in enumerate(tape):
        kind = event[0]
        if kind == 'A':
            continue
        if kind == 'J':
            _, stage, a_roles, (a, b, alpha, beta) = event
            assert len(set(a_roles)) == 4 and a != b and Q(alpha) and Q(beta)
            u, v = (attach(clock, role) for role in (a, b))
            counts['J'] += 1
            if stage == STAGE:
                fixed.extend((u, v))
            else:
                equalities.append([u, v])
            continue
        assert kind == 'B'
        _, op, dest, *args = event
        counts[op] += 1
        u = attach(clock, dest)
        if op == 'ADD':
            src, scalar = args
            assert src != dest and Q(scalar)
            v = attach(clock, src)
            equalities.append([u, v])
        elif op == 'SWAP':
            src, = args
            assert src != dest
            v = attach(clock, src)
            last[dest], last[src] = v, u
        elif op == 'QUERY':
            src, exponent = args
            assert src != dest and exponent in (-1, 1)
            fixed.extend((u, attach(clock, src)))
        elif op == 'SCALE':
            assert len(args) == 1 and Q(args[0])
        elif op == 'LAMBDA':
            assert args in ([-1], [1])
        else:
            assert op in ('IDLE_ONE', 'IDLE_ODD')
            mask = args[0]
            assert mask and len(set(mask)) == len(mask) and set(mask) <= set(range(1, 18))
            if op == 'IDLE_ONE':
                assert len(args) == 1
                if STAGE in mask:
                    rewards.append([u, clock, dest, 8*len(mask)])
                if clock == CLOCK:
                    assert dest == 36 and mask == [STAGE]
                    forced = u
            else:
                assert len(args) == 2 and args[1] in (-1, 1)
                odd.append([u, clock, dest, mask, args[1]])
                # Deliberately allow either basis with no reward, even at stage 9.
    for role in ROLES:
        fixed.append(attach(len(tape), role))
    assert forced is not None and forced not in fixed
    assert len(gaps) + len(ROLES) + 2 == len(nodes)
    return dict(nodes=nodes, gaps=gaps, equalities=equalities, fixed=fixed,
                odd=odd, rewards=rewards, forced=forced, counts=dict(counts))


class Network:
    def __init__(self, n):
        self.adj = [[] for _ in range(n)]
        self.arcs = []

    def arc(self, u, v, capacity, kind):
        assert u != v and capacity > 0
        i, j = len(self.adj[u]), len(self.adj[v])
        self.adj[u].append([v, j, capacity])
        self.adj[v].append([u, i, 0])
        self.arcs.append((u, v, i, capacity, kind))

    def two_way(self, u, v, capacity, kind):
        self.arc(u, v, capacity, kind)
        self.arc(v, u, capacity, kind)

    def path(self):
        parents = {SOURCE: None}
        todo = deque([SOURCE])
        while todo and SINK not in parents:
            u = todo.popleft()
            for i, (v, _, residual) in enumerate(self.adj[u]):
                if residual and v not in parents:
                    parents[v] = (u, i)
                    todo.append(v)
        return parents

    def maximum(self):
        value, augmentations = 0, 0
        while True:
            parents = self.path()
            if SINK not in parents:
                break
            path, v = [], SINK
            while v != SOURCE:
                u, i = parents[v]
                path.append((u, i))
                v = u
            delta = min(self.adj[u][i][2] for u, i in path)
            for u, i in path:
                v, j, _ = self.adj[u][i]
                self.adj[u][i][2] -= delta
                self.adj[v][j][2] += delta
            value += delta
            augmentations += 1
        return value, augmentations, set(parents)

    def certificate(self, value, side):
        balance = [0] * len(self.adj)
        cut, flowed = [], []
        for number, (u, v, index, capacity, kind) in enumerate(self.arcs):
            flux = capacity-self.adj[u][index][2]
            assert 0 <= flux <= capacity
            balance[u] -= flux
            balance[v] += flux
            if flux:
                flowed.append([number, flux])
            if u in side and v not in side:
                cut.append([number, u, v, capacity, kind])
                assert flux == capacity
            if u not in side and v in side:
                assert flux == 0
        assert balance == [-value, value] + [0]*(len(self.adj)-2)
        assert sum(edge[3] for edge in cut) == value
        return cut, flowed


def solve(g, transition, reward):
    scale = lcm(transition.denominator, *(x.denominator for x in reward))
    cap = int(transition*scale)
    pay = [int(x*scale) for x in reward]
    total = sum(pay)
    hard = total+len(g['gaps'])*cap+1
    net = Network(len(g['nodes']))
    for u, v, role in g['gaps']:
        net.two_way(u, v, cap, 'conversion')
    for u, v in g['equalities']:
        net.two_way(u, v, hard, 'same basis')
    for v in g['fixed']:
        net.arc(v, SINK, hard, 'original')
    for (v, _, _, _), amount in zip(g['rewards'], pay, strict=True):
        net.arc(SOURCE, v, amount, 'reward')
    net.arc(SOURCE, g['forced'], hard, 'force Walsh')
    value, augmentations, side = net.maximum()
    cut, flowed = net.certificate(value, side)
    assert not any(row[4] in ('original', 'same basis', 'force Walsh') for row in cut)
    assert g['forced'] in side and not side.intersection(g['fixed'])
    assert all((u in side) == (v in side) for u, v in g['equalities'])
    conversions = [[role, g['nodes'][u], g['nodes'][v]]
                   for u, v, role in g['gaps'] if (u in side) != (v in side)]
    chosen = [row[1:] for row in g['rewards'] if row[0] in side]
    collected = sum(amount for (v, _, _, _), amount in zip(g['rewards'], pay, strict=True) if v in side)
    assert collected-cap*len(conversions) == total-value
    return {'scale': scale, 'conversion_weight': cap, 'reward_weights': pay,
            'hard_capacity': hard, 'network_arcs': len(net.arcs), 'flow_value': value,
            'augmentations': augmentations, 'cut_edges': cut, 'positive_flow_arcs': flowed,
            'walsh_vertices': sorted(side-{SOURCE}), 'conversions': conversions,
            'collected_idle_calls': chosen, 'selected_odd_clocks': [row[1] for row in g['odd'] if row[0] in side],
            'upper_per_port': str(Q(total-value, scale))}


def stop(*_):
    raise TimeoutError('60-second exact cut cap')


def main():
    assert __debug__
    signal(SIGALRM, stop)
    alarm(LIMIT)
    c, old, r180 = (read(name) for name in ('inputs/CALLER.json', 'inputs/R92-PRICE.json', 'inputs/R180-LEAD.json'))
    read('inputs/pricing.py')
    assert (old['head'], old['caller_head']) == (HEAD, CALLER)
    assert (r180['head'], r180['caller'], r180['clock']) == (HEAD, CALLER, CLOCK)
    assert r180['ports'] == list(PORTS) and r180['pins']['inputs/CALLER.json'] == PINS['inputs/CALLER.json']
    tape, b = c['events'], c['types']['B']
    assert len(tape) == 4783 and tape[CLOCK] == ['B', 'IDLE_ONE', 36, [STAGE]]
    assert b['offset'] == 36 and b['roles'] == len(ROLES) and b['ports'] == list(PORTS)
    assert [event[1] for event in tape if event[0] == 'J'] == list(range(1, 18))
    g = graph(tape)
    assert len(g['rewards']) == 16 and len(g['odd']) == 4
    assert g['counts'] == {'ADD': 3476, 'SWAP': 44, 'SCALE': 210, 'LAMBDA': 66,
                           'IDLE_ONE': 60, 'IDLE_ODD': 4, 'J': 17}
    # At all-original every equality/fixed endpoint passes, and neither reward nor conversion occurs.
    original = [False]*len(g['nodes'])
    assert not any(original[i] for i in g['fixed'])
    assert not any(original[u] != original[v] for u, v in g['equalities'])
    assert not any(original[u] != original[v] for u, v, _ in g['gaps'])
    assert not any(original[v] for v, *_ in g['rewards'])
    unit = solve(g, Q(1), [Q(1)]*len(g['rewards']))
    power = run_path(str(HERE/'inputs/pricing.py'))['cost']
    k = Q(old['old_crossing_upper'])
    lo8, hi8 = power(Counter({8: 1}), k)
    upper = Q(unit['upper_per_port'])
    weighted = None
    if upper > 0:
        weights = []
        for _, _, _, rank in g['rewards']:
            delta = Counter({rank: 1})
            if rank > 8:
                delta[rank-8] -= 1
            weights.append(min(hi8, power(delta, k)[1]))
        weighted = solve(g, lo8, weights)
        raw_upper = len(PORTS)*min(upper*hi8, Q(weighted['upper_per_port']))
    else:
        raw_upper = len(PORTS)*upper*lo8
    alarm(0)
    print(dumps({'benchmark': HEAD, 'caller': CALLER, 'pr7411': PREDECESSOR, 'pins': PINS,
                 'forced_clock': CLOCK, 'stage': STAGE, 'event_cap': 4783, 'roles': ROLES,
                 'ports': PORTS, 'runner_cap_seconds': LIMIT, 'graph': g, 'unit': unit,
                 'weighted_if_needed': weighted, 'incumbent_kappa_upper': str(k),
                 'rank8_cost_interval': [str(lo8), str(hi8)], 'raw_upper_at_crossing': str(raw_upper),
                 'original_basis_control_gross': '0', 'build_admitted_by_price': raw_upper > 0},
                sort_keys=True, separators=(',', ':')))


if __name__ == '__main__':
    main()
