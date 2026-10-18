# SPDX-License-Identifier: Apache-2.0
"""Check selected frame distances and persistent live-stream ownership."""
from collections import Counter
from geometry import rank, require

LOCAL = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
GLOBAL = {1: 349604, 2: 60192, 3: 62585, 4: 20448,
          5: 11808, 7: 7, 8: 1152, 48: 4866}


def distance(first, second):
    return 2 * rank(first + second) - rank(first) - rank(second)


def check_local(word, programs):
    require((word['v'], word['h'], word['R']) == (112, 9, 480), 'local dimensions')
    frames = word['frames']
    require(all(all(0 < x < 512 for x in frame) and rank(frame) == len(frame)
                for frame in frames), 'independent frame bases')
    require(len(word['start']) == len(word['final']) == 704, 'live local role count')
    require(len(word['center_frames']) == len(word['centers']) == 8, 'eight centres')
    require(all(len(frames[f]) == 8 for f in word['center_frames']), 'centre frame ranks')
    require({int(k): v for k, v in word['local_profile'].items()} == LOCAL, 'local profile')
    report = {}
    for orientation, events in programs.items():
        paid, centres = Counter(), []
        for event in events:
            if event[0] == 'climb':
                _, _, role, old, new, charge = event
                require(0 <= role < 704, 'native child live role')
            elif event[0] == 'center':
                _, centre, old, new, charge = event
                require(0 <= centre < 8, 'private centre index')
                require({old, new} == {0, word['center_frames'][centre]}, 'centre endpoints')
                centres.append(centre)
            else:
                continue
            require(charge == distance(frames[old], frames[new]), 'minimum Fourier rank')
            require(charge > 0, 'positive paid rank')
            paid[charge] += 1
        require(sorted(centres) == list(range(8)), 'all private centre transitions')
        require(dict(paid) == LOCAL, 'literal paid local histogram')
        report[orientation] = {'native_edges': sum(paid.values()), 'centre_edges': 8,
                               'rank_mass': sum(k * v for k, v in paid.items())}
    require(set(report) == {'forward', 'backward'}, 'both orientations')
    return report


def check_global(word, programs, template, idle_frames, phases):
    require((template['m'], template['live'], template['physical']) == (73, 14336, 14826),
            'selected global dimensions')
    require(template['private_namespace'] == {
        'centers': [14336, 14344], 'reserved_tableau': [14344, 14824],
        'coefficient': [14824, 14826]}, 'private/live namespace separation')
    require(set(template['local_providers']) == {'gauge44'}, 'selected provider')
    provider = template['local_providers']['gauge44']
    require(provider['local_programs'] == programs, 'hosted programs equal selected programs')
    require(provider['ports'] == word['ports'], 'hosted port binding')
    calls = template['calls']
    require(len(calls) == 144, 'call count')
    require({(c['stage'], c['replica']) for c in calls}
            == {(s, r) for s in range(9) for r in range(16)}, 'all controller calls')
    for index, call in enumerate(calls):
        owners = [x[0] for x in call['owners']]
        require(len(owners) == len(set(owners)) == 704, 'injective whole-call owners')
        require(all(0 <= x < 14336 for x in owners), 'all helper roles on live paths')
        require(call['time'] == index, 'serialized call order')
        require(call['orientation'] in programs, 'call orientation')
    schedule = template['execution_schedule']
    per_replica = {r: [] for r in range(16)}
    local_order, block = [], -1
    for event in schedule[:-2]:
        require('replica' in event, 'per-replica event')
        replica = event['replica']
        per_replica[replica].append(event['source_event'])
        if event['kind'] == 'local_cover_sweep':
            block += 1
            local_order.append((event['stage'], replica))
        require(event['time'] == block, 'complete call before owner reassignment')
    require(local_order == [(c['stage'], c['replica']) for c in calls], 'local schedule order')
    require(all(order == list(range(30)) for order in per_replica.values()), 'complete replica paths')
    require(schedule[-1]['families'] == [0, 14336]
            and schedule[-1]['charged_calls_per_cover'] == 14336, 'all final live paths')
    require(schedule[-2]['families'] == [14336, 14336], 'no bank replaces a live path')
    require(len(idle_frames) == len(template['idle_children']) == 7526, 'idle child count')
    paid = Counter()
    for frame, child in zip(idle_frames, template['idle_children']):
        require({k: v for k, v in frame.items() if k != 'orthogonal_axes'} == child,
                'idle frame/controller binding')
        axes = frame['orthogonal_axes']
        inherited = phases['recipes'][frame['port']]['idle_children'][frame['child']]['orthogonal_axes']
        require(axes == inherited[frame['pending_offset']:], 'literal pending frame tail')
        require(len(axes) == frame['rank'] and rank(axes) == len(axes), 'idle minimum rank')
        require(all(0 < x < (1 << 73) for x in axes), 'idle axis width')
        require(all((x & y).bit_count() % 2 == int(i == j)
                    for i, x in enumerate(axes) for j, y in enumerate(axes)), 'orthogonal idle axes')
        paid[frame['rank']] += frame['replicas']
    idle_histogram = dict(sorted(paid.items()))
    for call in calls:
        paid.update(LOCAL)
    require(dict(paid) == GLOBAL, 'complete global histogram')
    return {'live_paths': 14336, 'complete_calls': 144, 'whole_call_owner_roles': 144 * 704,
            'idle_children': len(idle_frames), 'idle_histogram': idle_histogram,
            'paid_histogram': dict(sorted(paid.items())),
            'rank_mass': sum(k * v for k, v in paid.items()),
            'scope': 'Frame ranks, selected program binding, and persistent ownership; no scalar-map or cold compiler replay.'}
