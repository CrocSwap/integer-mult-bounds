#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for haoyan with substantial OpenAI Codex assistance.
"""Independent source-event, owner, chart, and finite-reserve audit.

This derivative fixes the R480 seven-slot k8 word and 37 replicas. It charges
1024 complex prefix bits and checks disjoint pending children on each family.
The source is Hao Yan's variable-replica checker at the pinned repository base.
SOURCES.json and INDEPENDENT-DERIVATION.patch identify that source and all edits.

Inputs are read-only. No owner constructor or controller auditor is imported.
--word is the canonical local supplier JSON.gz, with a hash-bound native
INDEPENDENT-LOCAL-REPLAY.json beside it (override with --local-replay).
--baseline-parent is the original eight-replica GLOBAL-TEMPLATE.json.gz.
Its sibling CANONICAL-WORD.json.gz supplies the ports and centre frames.
DATA-PHASES.json defaults to ../work/complex-nine-native/DATA-PHASES.json
(override with --phases). The checker recounts local widths and paid ranks.
--out names a JSON receipt. Checks remain enabled under python -O.
"""
import argparse
import copy
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path

V, H, M, T, R = 112, 9, 73, 37, 480
EXPECTED_IDLE = None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def basis(vectors):
    pivots = {}
    for x in vectors:
        require(type(x) is int and 0 <= x < 1 << H, 'invalid local frame vector')
        while x:
            bit = x.bit_length() - 1
            if bit in pivots:
                x ^= pivots[bit]
            else:
                pivots[bit] = x
                break
    for bit in sorted(pivots):
        for upper in pivots:
            if upper > bit and pivots[upper] >> bit & 1:
                pivots[upper] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


def local_inventory(word, replay):
    require((word['v'], word['h'], word['R']) == (V, H, R), 'local supplier dimensions')
    frames = [basis(frame) for frame in word['frames']]
    n = 2 * V + R
    require(len(word['start']) == len(word['final']) == n, 'local frame vector lengths')
    current = [frames[f] for f in word['start']]
    paid = Counter()

    def climb(register, frame):
        require(basis(current[register] + frame) == frame, 'nonmonotone local frame')
        jump = len(frame) - len(current[register])
        if jump:
            paid[jump] += 1
        current[register] = frame

    require(not word['target_levels'], 'this audit requires the current zero-level centre interface')
    for section in ('A', 'B', 'tail'):
        if section == 'B':
            require(all(current[t] == () for t in range(V, 2 * V)), 'target centre level')
            for q, frame_id in zip(word['centers'], word['center_frames']):
                require(current[q] == frames[frame_id], 'centre carrier frame')
                paid[len(frames[frame_id])] += 1
        for gate in word[section]:
            registers = gate[1:3] if gate[0] == 'add' else gate[1:2]
            require(gate[0] in ('add', 'scale'), 'unknown scalar gate')
            for register in registers:
                climb(register, frames[gate[-1]])
    for register, frame_id in enumerate(word['final']):
        climb(register, frames[frame_id])
    require(dict(paid) == {int(r): count for r, count in word['local_profile'].items()}, 'local paid-profile recount')
    for orientation in ('forward', 'backward'):
        require(dict(paid) == {int(r): count for r, count in replay['paid_profiles'][orientation].items()}, 'local replay profile binding')
    widths = [len(frames[word['final'][q]]) - len(frames[word['start'][q]]) for q in range(2 * V, n)]
    require(Counter(widths) == {4: 56, 5: 32, 7: 30, 8: 122, 9: 240}, 'current supplier width inventory')
    return widths, paid


def make_context(parent, phases, ports, word, replay, roles):
    widths, paid = local_inventory(word, replay)
    require(len(parent['calls']) == 72 and {(c['stage'], c['replica']) for c in parent['calls']} == {(s, r) for s in range(9) for r in range(8)}, 'original eight-replica baseline calls')
    require(len(roles) == 9 * T * R, 'complete helper role count')
    address = {}
    for role in roles:
        key = (role['stage'], role['replica'])
        time = role['time']
        require(time not in address or address[time] == key, 'inconsistent invocation time address')
        address[time] = key
    require(set(address) == set(range(9 * T)), 'contiguous invocation times')
    order = [address[t] for t in range(9 * T)]
    require(set(order) == {(s, r) for s in range(9) for r in range(T)}, 'stage/replica inventory')
    # Arbitrary interleaving: the exact per-replica projection is checked below.
    rank = {child['child']: child['rank'] for child in parent['idle_children']}
    source = parent['execution_schedule']
    blocks, stage = {}, None
    for index, event in enumerate(source):
        if event['kind'] in ('bank_padding_cover_sweep', 'translate_every_live_family'):
            continue
        if event['kind'] == 'local_cover_sweep':
            stage = event['stage']
            blocks[stage] = []
        require(stage is not None, 'source event before first invocation')
        blocks[stage].append((index, event))
    require(set(blocks) == set(range(9)), 'source stage inventory')
    events = [(index, event, replica, time) for time, (stage, replica) in enumerate(order) for index, event in blocks[stage]]
    projections = defaultdict(list)
    for index, event, replica, time in events:
        projections[replica].append(index)
    require(set(projections) == set(range(T)) and all(p == list(range(30)) for p in projections.values()), 'per-replica source-event projection')
    stage_pair = {e['stage']: e['pair'] for e in parent['recipe'] if e['kind'] == 'local'}
    last, windows, callpos, child_pair, side = {}, {}, {}, {}, {}
    bridges = 0
    for position, (_, event, replica, _) in enumerate(events):
        kind = event['kind']
        if kind == 'local_cover_sweep':
            stage = event['stage']
            callpos[stage, replica] = position
            last[replica, stage_pair[stage]] = position
        elif kind == 'bridge':
            last[replica, event['src']] = last[replica, event['dst']] = position
            bridges += 1
        elif kind == 'idle_cover_sweep':
            for sd, child in enumerate(event['child_indices']):
                if child in rank:
                    windows[replica, child] = (last.get((replica, event['pair']), -1), position)
                    child_pair[child], side[child] = event['pair'], sd
    require(len(windows) == T * len(rank), 'actual window inventory')
    require(len(ports) == V, 'port count')
    bases = []
    for q in ports:
        zero = next(i for i in range(H) if not (q >> i & 1))
        correction = q ^ (1 << zero)
        axes = list(range(H))
        axes[0], axes[zero] = axes[zero], axes[0]
        frame = [(1 << i) ^ (correction if correction >> i & 1 else 0) for i in axes] + [1 << i for i in range(H, M)]
        require(all((x & y).bit_count() % 2 == int(i == j) for i, x in enumerate(frame) for j, y in enumerate(frame)), 'nonorthogonal owner basis')
        bases.append(frame)
    return dict(widths=widths, paid=paid, order=order, at={key:t for t,key in enumerate(order)}, rank=rank,
                windows=windows, callpos=callpos, child_pair=child_pair, side=side, stage_pair=stage_pair,
                bases=bases, phases=phases, bridges=bridges, event_count=len(events), replay=replay)


def check_pending_axes(context):
    checked = 0
    for port, frame in enumerate(context['bases']):
        used = defaultdict(set)
        for child, rank in context['rank'].items():
            axes = list(map(int, context['phases']['recipes'][port]['idle_children'][child]['orthogonal_axes']))
            require(len(axes) == rank and len(set(axes)) == rank and set(axes) <= set(frame),
                    'pending child orthogonal basis')
            family = context['child_pair'][child], context['side'][child]
            require(not used[family] & set(axes), 'overlapping pending children on one family')
            used[family].update(axes)
            checked += 1
    return checked


def check_roles(context, roles):
    c = context
    live, physical = T * 8 * V, T * 8 * V + 8 + R + 2
    require(len(roles) == 9 * T * R, 'complete helper role count')
    helpers, families, used = defaultdict(set), defaultdict(set), defaultdict(set)
    charts, chart_cache = set(), {}
    for z in roles:
        s, r, helper = z['stage'], z['replica'], z['helper']
        owner, child, port = z['owner_replica'], z['child'], z['port']
        offset, width, family = z['offset'], z['width'], z['family']
        call = (s, r)
        require(call in c['at'] and 0 <= helper < R and 0 <= owner < T and 0 <= port < V, 'role coordinates')
        require(z['time'] == c['at'][call], 'role invocation time')
        require(width == c['widths'][helper], 'whole-helper residual width')
        require(0 <= family < live, 'private-namespace collision')
        require(child in c['rank'], 'unknown idle child')
        require(z['copy'] == V * owner + port and family == owner * 896 + (2 * c['child_pair'][child] + c['side'][child]) * V + port, 'physical family identity')
        lo, hi = c['windows'][owner, child]
        require(lo < c['callpos'][call] < hi, 'strict bridge-aware idle window')
        require(family // 224 != r * 4 + c['stage_pair'][s], 'helper aliases active data pair')
        require(helper not in helpers[call] and family not in families[call], 'duplicate helper or family within whole invocation')
        helpers[call].add(helper)
        families[call].add(family)
        cells = set(range(offset, offset + width))
        bin_key = (owner, child, port)
        require(offset >= 0 and offset + width <= c['rank'][child] and not used[bin_key] & cells, 'overlapping or out-of-capacity slice')
        used[bin_key].update(cells)
        chart_key = (port, child, offset, width)
        if chart_key not in chart_cache:
            frame = c['bases'][port]
            pending = list(map(int, c['phases']['recipes'][port]['idle_children'][child]['orthogonal_axes']))
            require(len(pending) == c['rank'][child], 'phase child rank')
            occupied = [frame.index(x) for x in pending[offset:offset + width]]
            spectators = [i for i in range(M) if i not in occupied][:H - width]
            permutation = occupied + spectators + [i for i in range(M) if i not in occupied and i not in spectators]
            require(len(occupied) == width and len(set(occupied + spectators)) == H and sorted(permutation) == list(range(M)), 'residual/spectator permutation')
            require([frame[i] for i in permutation[:width]] == pending[offset:offset + width], 'pending-axis binding')
            chart_cache[chart_key] = tuple(frame[i] for i in permutation)
        charts.add(chart_cache[chart_key])
    require(set(helpers) == set(c['order']) and all(h == set(range(R)) for h in helpers.values()), 'complete per-call helper inventory')
    idle = Counter()
    for owner, child in c['windows']:
        for port in range(V):
            cells = used[owner, child, port]
            require(cells == set(range(len(cells))), 'gap in pending prefix')
            left = c['rank'][child] - len(cells)
            if left:
                idle[left] += 1
    require(dict(idle) == EXPECTED_IDLE, 'nominated idle profile')
    profile = Counter({rank: 9 * T * count for rank, count in c['paid'].items()})
    profile.update(idle)
    mass = sum(rank * count for rank, count in profile.items())
    require(M * live - mass == 320*T, 'replica-scaled rank deficit')
    require(c['bridges'] == 9*T, 'actual bridge count')
    localbits = max(x['prefix_bits_upper'] for x in c['replay']['local'].values())
    prefix = localbits + (M + 1) // 2 + len(c['order']) + c['bridges'] + 4
    group = 2 ** (36 * 36)
    for i in range(1, 37):
        group *= 2 ** (2 * i) - 1
    stock = group * physical
    row = 2 * stock.bit_length() + 9909 + 252 + 2 * 1024
    require(prefix < 1024, 'prefix reserve')
    require(row < 20161 and M * M > 2 * max(profile) ** 2, 'row or halving reserve')
    return dict(status='PASS_INDEPENDENT_VARIABLE_T_LITERAL_WINDOWS_CHARTS_PREFIX_ROW', roles=len(roles), calls=len(c['order']),
                source_events_per_replica=30, expanded_replica_events=c['event_count'], bridge_events=c['bridges'],
                literal_windows=len(c['windows']), checked_whole_helper_widths=len(roles), checked_busy_family_windows=len(roles),
                orthogonal_port_bases=len(c['bases']), actual_73_axis_charts=len(charts), checked_slice_prefixes=len(c['windows']) * V,
                local_profile=dict(sorted(c['paid'].items())), width_inventory=dict(sorted(Counter(c['widths']).items())),
                idle=dict(sorted(idle.items())), profile=dict(sorted(profile.items())), live=live, physical=physical,
                rank_mass=mass, deficit=320*T, namespace={'data':[0,live], 'centres':[live,live+8], 'tableau':[live+8,live+8+R], 'coefficient':[live+8+R,physical]},
                local_prefix_bits=localbits, local_prefix_from_native_receipt=True, local_profile_recounted=True,
                prefix_formula=dict(local_scalar=localbits, input_l2=(M + 1) // 2, invocations=len(c['order']), bridges=c['bridges'], margin=4),
                prefix_bits=prefix, charged_prefix_bits=1024, physical_stock_bits=stock.bit_length(),
                physical_row_coefficient=row, row_limit=20161,
                scope='Finite role/window/chart and inherited prefix/row obligations. Requires separately admitted local supplier and emitted controller, complete finite invoice, exact moments and outer assembly; no all-size theorem is asserted.')


def controls(context, roles):
    candidates = []
    first = roles[0]
    bad = dict(first, family=896*T)
    candidates.append(('private_namespace_collision', [bad] + roles[1:], 'private-namespace collision'))
    index = next(i for i, z in enumerate(roles) if z['replica'] >= 1)
    bad = dict(roles[index], replica=roles[index]['replica'] - 1)
    candidates.append(('copy_replica_alias', [bad] + roles[:index] + roles[index+1:], 'role invocation time'))
    candidates.append(('missing_whole_helper', roles[1:], 'complete helper role count'))
    split = dict(first, width=first['width'] - 1)
    fragment = dict(first, offset=first['offset'] + first['width'] - 1, width=1)
    candidates.append(('split_whole_helper', [split, fragment] + roles[1:], 'complete helper role count'))
    candidates.append(('truncated_helper_width', [split] + roles[1:], 'whole-helper residual width'))
    # Keep the family and chart valid, but move one complete role past its
    # actual idle event. Freeze the original invocation order for controls.
    crossing = None
    for index, z in enumerate(roles):
        lo, hi = context['windows'][z['owner_replica'], z['child']]
        later = next((key for key in context['order'] if context['callpos'][key] >= hi), None)
        if later is not None:
            crossing = [dict(z, stage=later[0], replica=later[1], time=context['at'][later])] + roles[:index] + roles[index+1:]
            break
    require(crossing is not None, 'no idle-boundary control could be constructed')
    candidates.append(('cross_idle_boundary', crossing, 'strict bridge-aware idle window'))
    rejected = []
    for name, bad, expected in candidates:
        try:
            check_roles(context, bad)
        except ValueError as exc:
            require(str(exc) == expected, 'control rejected at unexpected predicate: ' + name)
            rejected.append(dict(name=name, reason=str(exc)))
        else:
            raise ValueError('accepted negative control: ' + name)
    bad = dict(context, phases=copy.deepcopy(context['phases']))
    pair = next((a, b) for a in context['rank'] for b in context['rank']
                if a < b and (context['child_pair'][a], context['side'][a]) ==
                (context['child_pair'][b], context['side'][b]))
    children = bad['phases']['recipes'][0]['idle_children']
    children[pair[1]]['orthogonal_axes'][0] = children[pair[0]]['orthogonal_axes'][0]
    try:
        check_pending_axes(bad)
    except ValueError as exc:
        require(str(exc) == 'overlapping pending children on one family',
                'pending-axis control rejected at unexpected predicate')
        rejected.append(dict(name='cross_child_pending_axis_alias', reason=str(exc)))
    else:
        raise ValueError('accepted negative control: cross_child_pending_axis_alias')
    return rejected


def main():
    global T, EXPECTED_IDLE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-parent', type=Path, required=True)
    parser.add_argument('--owners', type=Path, required=True)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--phases', type=Path)
    parser.add_argument('--local-replay', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument("--replicas", type=int, required=True)
    parser.add_argument("--expected-idle", required=True)
    args = parser.parse_args()
    T = args.replicas
    require(T == 37, "replica range")
    EXPECTED_IDLE = {int(k): v for k,v in json.loads(args.expected_idle).items()}
    phases_path = args.phases or args.baseline_parent.parent.parent / 'work/complex-nine-native/DATA-PHASES.json'
    canonical_path = args.baseline_parent.parent / 'CANONICAL-WORD.json.gz'
    replay_path = args.local_replay or args.word.parent / 'INDEPENDENT-LOCAL-REPLAY.json'
    parent, phases, canonical, word, replay, roles = map(read, (args.baseline_parent, phases_path, canonical_path, args.word, replay_path, args.owners))
    require(replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'local replay status')
    require(replay['canonical_word_sha256'] == filehash(args.word), 'local word/replay hash binding')
    require(set(replay['local']) == {'forward', 'backward'}, 'both native prefix orientations')
    require(word['ports'] == canonical['ports'], 'local/controller port interface')
    require(len(word['center_frames']) == len(canonical['center_frames']) == 8, 'eight centre interfaces')
    require([basis(word['frames'][f]) for f in word['center_frames']] == [basis(canonical['frames'][f]) for f in canonical['center_frames']], 'ordered centre-frame interface')
    context = make_context(parent, phases, canonical['ports'], word, replay, roles)
    pending = check_pending_axes(context)
    receipt = check_roles(context, roles)
    receipt['disjoint_pending_child_axis_checks'] = pending
    receipt['controls_rejected'] = controls(context, roles)
    receipt['input_sha256'] = {str(path): filehash(path) for path in (args.baseline_parent, phases_path, canonical_path, args.word, replay_path, args.owners)}
    args.out.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(receipt['status'], 'roles=' + str(receipt['roles']), 'controls=' + str(len(receipt['controls_rejected'])))


if __name__ == '__main__':
    main()
