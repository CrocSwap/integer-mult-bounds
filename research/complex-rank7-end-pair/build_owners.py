#!/usr/bin/env python3
"""Reproduce and check the frozen rank-seven whole-owner map.

The whole-owner interface and source schedule are inherited from the
#685/#741/#799 lineage. No optimizer runs during this reproduction.
"""
import argparse
from collections import Counter, defaultdict, deque
import copy
import gzip
import hashlib
import json
from pathlib import Path


def raw(path):
    data = Path(path).read_bytes()
    return gzip.decompress(data) if str(path).endswith('.gz') else data


def read(path):
    return json.loads(raw(path))


def schedule_geometry(parent, order, ports):
    capacities = {}
    child_ports = defaultdict(set)
    for row in parent['idle_children']:
        child, port, rank = row['child'], row['port'], row['rank']
        assert row['replicas'] == 8 and 0 <= port < ports
        assert port not in child_ports[child]
        child_ports[child].add(port)
        assert capacities.get(child, rank) == rank
        capacities[child] = rank
    assert all(ps == set(range(ports)) for ps in child_ports.values())
    blocks, source_ids, globals_ = {}, [], []
    stage = None
    for index, event in enumerate(parent['execution_schedule']):
        if event['kind'] in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            globals_.append(index)
            continue
        if event['kind'] == 'local_cover_sweep':
            stage = event['stage']
            assert stage not in blocks
            blocks[stage] = []
        assert stage is not None
        blocks[stage].append((index, event))
        source_ids.append(index)
    assert globals_ == [30, 31] and source_ids == list(range(30))
    stage_pairs = {e['stage']: e['pair'] for e in parent['recipe'] if e['kind'] == 'local'}
    projections = defaultdict(list)
    last, windows, pairs, sides, calls = {}, {}, {}, {}, {}
    position = 0
    for time, (stage, replica) in enumerate(order):
        for index, event in blocks[stage]:
            projections[replica].append(index)
            if event['kind'] == 'local_cover_sweep':
                calls[time] = position
                last[replica, stage_pairs[stage]] = position
            elif event['kind'] == 'bridge':
                last[replica, event['src']] = position
                last[replica, event['dst']] = position
            elif event['kind'] == 'idle_cover_sweep':
                for side, child in enumerate(event['child_indices']):
                    if child not in capacities:
                        continue
                    assert (replica, child) not in windows
                    pair = event['pair']
                    assert pairs.get(child, pair) == pair
                    assert sides.get(child, side) == side
                    pairs[child], sides[child] = pair, side
                    windows[replica, child] = (last.get((replica, pair), -1), position)
            position += 1
    assert set(projections) == set(range(8))
    assert all(indices == source_ids for indices in projections.values())
    assert set(windows) == {(replica, child) for replica in range(8) for child in capacities}
    result = {
        f'{replica},{child}': [capacities[child], [t for t in range(72) if left < calls[t] < right]]
        for (replica, child), (left, right) in windows.items()
    }
    return result, pairs, sides


def audit(flow, owners, plan, word, parent, word_hash):
    ports, helpers = word['report']['v'], word['report']['R']
    assert (ports, helpers) == (112, 504)
    order = [tuple(call) for call in plan['order']]
    assert len(order) == 72 and set(order) == {(stage, replica) for stage in range(9) for replica in range(8)}
    geometry = {key: plan[key] for key in ('order', 'windows', 'pairs', 'sides')}
    assert digest(geometry) == flow['geometry_sha256']
    if parent is None:
        windows = plan['windows']
        pairs = {int(child): pair for child, pair in plan['pairs'].items()}
        sides = {int(child): side for child, side in plan['sides'].items()}
    else:
        windows, pairs, sides = schedule_geometry(parent, order, ports)
        assert plan['windows'] == windows
        assert plan['pairs'] == {str(child): pair for child, pair in pairs.items()}
        assert plan['sides'] == {str(child): side for child, side in sides.items()}
    widths = [
        len(word['helper_final'].get(str(2 * ports + h), range(9)))
        - len(word['start_extra'].get(str(2 * ports + h), []))
        for h in range(helpers)
    ]
    assert flow['input_word_sha256'] == word_hash
    assert flow['helper_widths'] == widths and all(1 <= w <= 9 for w in widths)
    active_data = {
        (call['stage'], call['replica']): {family for family, route in call['owners'][:2 * ports]}
        for call in parent['calls']
    } if parent is not None else None
    seen, families, bins = set(), defaultdict(set), defaultdict(list)
    assert len(owners) == 72 * helpers
    fields = {'child', 'copy', 'family', 'helper', 'offset', 'owner_replica', 'port', 'replica', 'stage', 'time', 'width'}
    for row in owners:
        assert set(row) == fields and all(type(value) is int for value in row.values())
        stage, replica, helper = row['stage'], row['replica'], row['helper']
        role, time = (stage, replica, helper), row['time']
        assert 0 <= helper < helpers and 0 <= time < 72 and order[time] == (stage, replica)
        assert role not in seen
        seen.add(role)
        owner, child, port = row['owner_replica'], row['child'], row['port']
        assert 0 <= owner < 8 and 0 <= port < ports
        cap, times = windows[f'{owner},{child}']
        assert time in times and row['copy'] == owner * ports + port
        family = owner * 8 * ports + (2 * pairs[child] + sides[child]) * ports + port
        assert row['family'] == family and family not in families[time]
        if active_data is not None:
            assert family not in active_data[stage, replica]
        families[time].add(family)
        width, offset = row['width'], row['offset']
        assert width == widths[helper] and 0 <= offset and offset + width <= cap
        bins[owner, child, port].append((offset, time, width))
    assert seen == {(stage, replica, h) for stage, replica in order for h in range(helpers)}
    slots, idle = {}, Counter()
    for key, (cap, times) in windows.items():
        owner, child = map(int, key.split(','))
        for port in range(ports):
            key3, offset = (owner, child, port), 0
            slot = []
            for actual_offset, time, width in sorted(bins[key3]):
                assert actual_offset == offset
                offset += width
                slot.append((time, width))
            assert offset <= cap
            slots[key3] = sorted(slot)
            if cap > offset:
                idle[cap - offset] += 1
    assert flow['fixed_partial_bins'] == []
    assert len(flow['windows']) == len(windows)
    assert {window['key'] for window in flow['windows']} == set(windows)
    pattern_count = 0
    for window in flow['windows']:
        owner, child = map(int, window['key'].split(','))
        cap, times = windows[window['key']]
        used = 0
        for pattern in window['patterns']:
            count = pattern['count']
            assert type(count) is int and 0 < count <= ports - used
            expected_widths = Counter(pattern['widths'])
            assert all(type(w) is int and 1 <= w <= 9 for w in pattern['widths'])
            assert sum(pattern['widths']) <= cap
            declared = {}
            for time, width, amount in pattern['flows']:
                assert all(type(value) is int for value in (time, width, amount))
                assert time in times and width in expected_widths and 0 < amount <= count
                assert (time, width) not in declared
                declared[time, width] = amount
            actual = Counter()
            for port in range(used, used + count):
                slot = slots[owner, child, port]
                assert Counter(width for time, width in slot) == expected_widths
                assert len({time for time, width in slot}) == len(slot)
                actual.update(slot)
            assert actual == Counter(declared)
            assert all(sum(n for (t, w), n in declared.items() if t == time) <= count for time in times)
            used += count
            pattern_count += 1
        assert used == ports
    profile = Counter({int(rank): 72 * count for rank, count in word['report']['local_profile'].items()})
    profile.update(idle)
    mass = sum(rank * count for rank, count in profile.items())
    assert mass == 520704 and 73 * 7168 - mass == 2560
    assert idle == Counter({48: 2400})
    assert dict(profile) == {int(rank): count for rank, count in flow['global_profile'].items()}
    return {
        'status': 'PASS_LITERAL_PATTERN_FLOW_AND_ALL_36288_OWNERS',
        'source_windows_reconstructed': parent is not None,
        'roles': len(owners), 'physical_bins': len(slots), 'window_count': len(windows),
        'patterns': pattern_count, 'rank_mass': mass, 'deficit': 2560,
        'helper_width_inventory': dict(sorted(Counter(widths).items())),
        'idle_profile': dict(sorted(idle.items())), 'global_profile': dict(sorted(profile.items())),
    }


def controls(flow, owners, plan, word, parent, word_hash):
    def wrong_flow(candidate):
        pattern = next(p for w in candidate[0]['windows'] for p in w['patterns'] if p['flows'])
        pattern['flows'][0][2] += 1

    def wrong_count(candidate):
        next(p for w in candidate[0]['windows'] for p in w['patterns'])['count'] += 1

    def outside_window(candidate):
        row = candidate[1][0]
        times = candidate[2]['windows'][f"{row['owner_replica']},{row['child']}"][1]
        time = next(t for t in range(72) if t not in times)
        row['time'] = time
        row['stage'], row['replica'] = candidate[2]['order'][time]

    mutations = {
        'call outside owner window': outside_window,
        'duplicate helper role': lambda c: c[1].__setitem__(-1, copy.deepcopy(c[1][0])),
        'wrong native residual width': lambda c: c[1][0].__setitem__('width', c[1][0]['width'] + 1),
        'noncompact prefix': lambda c: c[1][0].__setitem__('offset', c[1][0]['offset'] + 1),
        'wrong physical family': lambda c: c[1][0].__setitem__('family', c[1][0]['family'] + 1),
        'wrong source window capacity': lambda c: next(iter(c[2]['windows'].values())).__setitem__(0, 49),
        'wrong flow multiplicity': wrong_flow,
        'wrong pattern multiplicity': wrong_count,
    }
    rejected = []
    for name, mutate in mutations.items():
        candidate = [copy.deepcopy(flow), copy.deepcopy(owners), copy.deepcopy(plan)]
        mutate(candidate)
        try:
            audit(*candidate, word, parent, word_hash)
        except (AssertionError, KeyError):
            rejected.append(name)
        else:
            raise AssertionError(f'accepted negative control: {name}')
    return rejected



def slots_from_flow(pattern):
    count, widths = pattern['count'], pattern['widths']
    sockets = len(widths)
    if not sockets:
        assert not pattern['flows']
        return [[] for _ in range(count)]
    flows = {(time, width): n for time, width, n in pattern['flows']}
    assert len(flows) == len(pattern['flows'])
    times = sorted({time for time, width in flows})
    assert len(times) >= sockets
    assert all(sum(n for (t, w), n in flows.items() if t == time) <= count for time in times)
    size = len(times)
    time_index = {time: index for index, time in enumerate(times)}
    edges = [[0] * size for _ in range(size)]
    for width in sorted(set(widths)):
        available = deque((time, n) for (time, w), n in sorted(flows.items()) if w == width)
        for socket, socket_width in enumerate(widths):
            if socket_width != width:
                continue
            left = count
            while left:
                time, n = available.popleft()
                amount = min(left, n)
                edges[socket][time_index[time]] += amount
                left -= amount
                if n > amount:
                    available.appendleft((time, n - amount))
        assert not available

    # Equal degrees allow one perfect matching for each physical bin.
    deficits = deque()
    for time in range(size):
        missing = count - sum(edges[socket][time] for socket in range(sockets))
        if missing:
            deficits.append((time, missing))
    for socket in range(sockets, size):
        left = count
        while left:
            time, n = deficits.popleft()
            amount = min(left, n)
            edges[socket][time] += amount
            left -= amount
            if n > amount:
                deficits.appendleft((time, n - amount))
    assert not deficits
    assert all(sum(row) == count for row in edges)
    assert all(sum(edges[i][j] for i in range(size)) == count for j in range(size))
    slots = []
    for _ in range(count):
        matched = [-1] * size

        def augment(socket, seen):
            for time, multiplicity in enumerate(edges[socket]):
                if not multiplicity or time in seen:
                    continue
                seen.add(time)
                if matched[time] < 0 or augment(matched[time], seen):
                    matched[time] = socket
                    return True
            return False

        complete = all(augment(socket, set()) for socket in range(size))
        assert complete, 'regular bipartite graph has no perfect matching'
        slot = []
        for time, socket in enumerate(matched):
            assert socket >= 0 and edges[socket][time] > 0
            edges[socket][time] -= 1
            if socket < sockets:
                slot.append([times[time], widths[socket]])
        slot.sort()
        assert len(slot) == sockets and len({time for time, width in slot}) == sockets
        slots.append(slot)
    assert not any(any(row) for row in edges)
    actual = Counter((time, width) for slot in slots for time, width in slot)
    assert actual == Counter(flows)
    return slots

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def expand(flow, plan):
    widths = flow['helper_widths']
    pools = defaultdict(deque)
    for time in range(72):
        for helper, width in enumerate(widths):
            pools[time, width].append(helper)
    assert flow['fixed_partial_bins'] == []
    owners = []

    def emit(owner, child, port, slot):
        family = owner * 896 + (2 * plan['pairs'][str(child)] + plan['sides'][str(child)]) * 112 + port
        offset = 0
        for time, width in sorted(slot):
            helper = pools[time, width].popleft()
            stage, replica = plan['order'][time]
            owners.append(dict(child=child, copy=owner * 112 + port, family=family,
                helper=helper, offset=offset, owner_replica=owner, port=port,
                replica=replica, stage=stage, time=time, width=width))
            offset += width

    for window in flow['windows']:
        owner, child = map(int, window['key'].split(','))
        ports = deque(range(112))
        for pattern in window['patterns']:
            for slot in slots_from_flow(pattern):
                emit(owner, child, ports.popleft(), slot)
        assert not ports
    assert not any(pools.values())
    return sorted(owners, key=lambda row: (row['time'], row['helper']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-template', type=Path)
    args = parser.parse_args()
    flow_path = Path(__file__).resolve().parent / 'data' / 'OWNER-FLOW.json.gz'
    flow, word, plan = map(read, (flow_path, args.word, args.plan))
    parent = read(args.source_template) if args.source_template else None
    word_hash = hashlib.sha256(raw(args.word)).hexdigest()
    assert word_hash == '096ed4abee4bb02c0d6f03bb8191510e57f6b1fcd34e8644f4fd336254e46411'
    assert flow['schema'] == 'frozen-rank7-owner-flow/1'
    owners = expand(flow, plan)
    report = audit(flow, owners, plan, word, parent, word_hash)
    payload = canonical(owners)
    owner_hash = hashlib.sha256(payload).hexdigest()
    assert owner_hash == '02bde66a90b8ae9b0c4d8d563ca2218ad1de851fa6dec3d1abb5d3a30ca3dd2a'
    assert owner_hash == flow['owner_content_sha256']
    report['rejected_controls'] = controls(flow, owners, plan, word, parent, word_hash)
    report['input_content_sha256'] = {
        'flow': hashlib.sha256(raw(flow_path)).hexdigest(),
        'word': word_hash, 'plan': hashlib.sha256(raw(args.plan)).hexdigest(),
    }
    if args.source_template:
        report['input_content_sha256']['source_template'] = hashlib.sha256(raw(args.source_template)).hexdigest()
    report['owner_content_sha256'] = owner_hash
    report['geometry_sha256'] = flow['geometry_sha256']
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / 'OWNERS.json.gz').open('wb') as stream:
        with gzip.GzipFile(filename='', mode='wb', fileobj=stream, mtime=0) as archive:
            archive.write(payload)
    (args.out / 'OWNER-CERTIFICATE.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
