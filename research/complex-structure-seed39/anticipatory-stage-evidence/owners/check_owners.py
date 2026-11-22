#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent literal owner, event-window, residual-axis and profile checker.

Prepared for Tekalign (@tekuuu) with substantial OpenAI Codex assistance.
Credits: PR2269's frozen controller/owner inputs, PR2339's borrowed providers,
and the predecessor independent_core.py audit by Hao Yan and contributors.
No constructor, optimizer, emitter or inherited audit code is imported.
Native scalar/warp/phase proofs remain bound external obligations.
"""
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
V, H, M, T, R = 112, 9, 73, 74, 400
PARENT_PINS = {
    'new/PLAN.json': 'bf1abd33c8ba946371cae37e021747343ef6603a31297bcc962197cc23f535e2',
    'GLOBAL-TEMPLATE.json.gz': '1d31424c4e27e26a35a9932ca778e43f1f3577589275422cc642aa68b31112db',
}
PHASE_PIN = 'c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)


def span(vectors):
    """Complete F2 span as an integer bitmap, independently of canonical IDs."""
    points = {0}
    for vector in vectors:
        require(type(vector) is int and 0 <= vector < 512, 'local frame vector')
        points |= {point ^ vector for point in tuple(points)}
    return sum(1 << point for point in points), len(points).bit_length()-1


def local(directory):
    wordfile = directory/'CANONICAL-WORD.json.gz'
    word = read(wordfile)
    require((word['v'], word['h'], word['R']) == (V, H, R), '400-helper native interface')
    require(len(word['start']) == len(word['final']) == 2*V+R, 'native endpoints')
    require(len(word['helper_origin']) == R and len(set(word['helper_origin'])) == R,
            'unique original helper registers')
    require(word['helper_origin'] == sorted(set(range(224, 704))-set(word['removed'])),
            'native helper origin complement')
    require(not word['target_levels'], 'zero COPY target levels')
    frames = [span(vectors) for vectors in word['frames']]
    current = [frames[f] for f in word['start']]
    paid = Counter()

    def climb(register, frame):
        require(type(register) is int and 0 <= register < 2*V+R, 'native register range')
        old = current[register]
        require(old[0] & ~frame[0] == 0, 'nonmonotone native frame')
        rank = frame[1]-old[1]
        if rank:
            paid[rank] += 1
        current[register] = frame

    for section in ('A', 'B', 'tail'):
        if section == 'B':
            require(all(f == (1, 0) for f in current[V:2*V]), 'COPY target cut')
            require(len(word['centers']) == len(word['center_frames']) == 8, 'COPY centers')
            for register, frameid in zip(word['centers'], word['center_frames']):
                require(current[register] == frames[frameid], 'COPY source cut')
                paid[frames[frameid][1]] += 1
        for gate in word[section]:
            if gate[0] == 'warp':
                register, operator, before, after = gate[1:]
                require(type(register) is int and 0 <= register < 2*V+R, 'native warp register range')
                require(current[register] == frames[before], 'native warp source frame')
                require(operator != 0 and frames[before][1] == frames[after][1], 'native warp rank zero')
                current[register] = frames[after]
            else:
                require(gate[0] in ('add', 'scale'), 'native paid-stage opcode')
                for register in gate[1:3] if gate[0] == 'add' else gate[1:2]:
                    climb(register, frames[gate[-1]])
    for register, frameid in enumerate(word['final']):
        climb(register, frames[frameid])
    widths = [frames[word['final'][q]][1]-frames[word['start'][q]][1]
              for q in range(2*V, 2*V+R)]
    require(all(0 < w <= H for w in widths), 'proper native helper widths')
    require(paid == Counter({int(r): n for r, n in word['local_profile'].items()}), 'native paid recount')
    require(sum(r*n for r, n in paid.items())-sum(widths) == 1856, 'native interface rank mass')
    replay = read(directory/'INDEPENDENT-LOCAL-REPLAY.json')
    require(replay['status'] == 'PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY', 'native replay status')
    require(replay['canonical_word_sha256'] == sha(wordfile), 'native replay word binding')
    require(replay['local_programs_sha256'] == sha(directory/'LOCAL-PROGRAMS.json.gz'), 'native replay program binding')
    programs = read(directory/'LOCAL-PROGRAMS.json.gz')
    for orientation in ('forward', 'backward'):
        literal = Counter(event[-1] for event in programs[orientation] if event[0] in ('climb', 'center'))
        require(literal == paid == Counter({int(r): n for r, n in replay['paid_profiles'][orientation].items()}),
                'literal native program paid profile')
    return dict(widths=widths, paid=paid, ports=word['ports'], origins=word['helper_origin'],
                inputs={name: sha(directory/name) for name in
                        ('CANONICAL-WORD.json.gz', 'LOCAL-PROGRAMS.json.gz', 'INDEPENDENT-LOCAL-REPLAY.json')})


def geometry(plan, template, phases):
    order = [tuple(x) for x in plan['order']]
    require(len(order) == 9*T and set(order) == {(s, r) for s in range(9) for r in range(T)}, 'call order inventory')
    rank = {}
    children = set()
    for row in template['idle_children']:
        child, port, width = row['child'], row['port'], row['rank']
        require((child, port) not in children and 0 <= port < V, 'source child port inventory')
        children.add((child, port))
        require(child not in rank or rank[child] == width, 'source child ranks agree')
        rank[child] = width
    require(children == {(c, p) for c in rank for p in range(V)}, 'complete source pending inventory')
    source = template['execution_schedule']
    stage_pair = {e['stage']: e['pair'] for e in template['recipe'] if e['kind'] == 'local'}
    require(set(stage_pair) == set(range(9)), 'stage pair inventory')
    starts = [i for i, event in enumerate(source) if event['kind'] == 'local_cover_sweep']
    require(len(starts) == 9 and starts[0] == 0, 'source local boundaries')
    blocks = {}
    for j, start in enumerate(starts):
        end = starts[j+1] if j+1 < len(starts) else 30
        blocks[source[start]['stage']] = list(range(start, end))
    require(source[30]['kind'] == 'bank_padding_cover_sweep' and source[31]['kind'] == 'translate_every_live_family', 'source terminal global events')
    # Expand source-event blocks directly; compare every replica's projection.
    events = [(index, rep, time) for time, (stage, rep) in enumerate(order) for index in blocks[stage]]
    projections = [[] for _ in range(T)]
    touches = [[-1]*4 for _ in range(T)]
    windows, callpos, pair, side = {}, {}, {}, {}
    bridges = 0
    for pos, (index, rep, time) in enumerate(events):
        projections[rep].append(index)
        event = source[index]
        if event['kind'] == 'local_cover_sweep':
            stage = event['stage']
            callpos[stage, rep] = pos
            touches[rep][stage_pair[stage]] = pos
        elif event['kind'] == 'bridge':
            touches[rep][event['src']] = touches[rep][event['dst']] = pos
            bridges += 1
        elif event['kind'] == 'idle_cover_sweep':
            for sd, child in enumerate(event['child_indices']):
                if child in rank:
                    require((rep, child) not in windows, 'unique pending window')
                    windows[rep, child] = (touches[rep][event['pair']], pos)
                    pair[child], side[child] = event['pair'], sd
    require(all(p == list(range(30)) for p in projections), 'per-replica chronological source projection')
    require(len(windows) == T*len(rank) and bridges == 9*T, 'complete windows and bridges')
    require(pair == {int(k):v for k,v in plan['pairs'].items()} and side == {int(k):v for k,v in plan['sides'].items()}, 'source child family matches plan')
    rebuilt = {f'{rep},{child}': [rank[child], [t for t, call in enumerate(order) if lo < callpos[call] < hi]]
               for (rep, child), (lo, hi) in windows.items()}
    require(rebuilt == plan['windows'], 'independently reconstructed plan windows')
    return dict(order=order, at={call:t for t,call in enumerate(order)}, ranks=rank,
                windows=windows, callpos=callpos, pair=pair, side=side, stage_pair=stage_pair,
                source_events=len(events), bridges=bridges)


def axes(geo, ports, phases):
    require(len(ports) == V and len(set(ports)) == V, 'ordered native ports')
    frames, pending = [], {}
    for port, q in enumerate(ports):
        zero = next(i for i in range(H) if not (q >> i & 1))
        correction = q ^ (1 << zero)
        labels = list(range(H))
        labels[0], labels[zero] = labels[zero], labels[0]
        frame = [(1 << i) ^ (correction if correction >> i & 1 else 0) for i in labels]
        frame += [1 << i for i in range(H, M)]
        require(all((a & b).bit_count() % 2 == int(i == j) for i,a in enumerate(frame) for j,b in enumerate(frame)), 'orthogonal owner axes')
        frames.append(frame)
        used = defaultdict(set)
        for child, width in geo['ranks'].items():
            vectors = list(map(int, phases['recipes'][port]['idle_children'][child]['orthogonal_axes']))
            require(len(vectors) == len(set(vectors)) == width and set(vectors) <= set(frame), 'pending axes')
            key = geo['pair'][child], geo['side'][child]
            require(not used[key].intersection(vectors), 'pending children overlap on physical family')
            used[key].update(vectors)
            pending[port, child] = vectors
    return frames, pending


def audit(roles, geo, providers, dispatch, frames, pending):
    require(len(roles) == 9*T*R, 'complete 400-helper role count')
    families = [set() for _ in geo['order']]
    helpers = [0 for _ in geo['order']]
    used = defaultdict(int)
    charts = {}
    chart_ids = {}
    role_charts = []
    cross = 0
    for z in roles:
        stage, replica, helper, time = (z[k] for k in ('stage','replica','helper','time'))
        owner, child, port, offset, width, family = (z[k] for k in ('owner_replica','child','port','offset','width','family'))
        call = stage, replica
        require(all(type(z[k]) is int for k in ('stage','replica','helper','time','owner_replica','child','port','offset','width','family','copy')), 'integral owner coordinates')
        require(call in geo['at'] and time == geo['at'][call], 'owner invocation time')
        require(0 <= helper < R and 0 <= owner < T and 0 <= port < V and child in geo['ranks'], 'owner coordinates')
        provider = providers[dispatch[call]]
        require(width == provider['widths'][helper], 'whole native helper width')
        if 'original_helper_register' in z:
            require(z['original_helper_register'] == provider['origins'][helper], 'original helper register binding')
        require(z['copy'] == V*owner+port, 'owner copy identity')
        wanted_family = owner*(8*V)+(2*geo['pair'][child]+geo['side'][child])*V+port
        require(family == wanted_family and 0 <= family < 8*T*V, 'physical family identity')
        require(family//(2*V) != 4*replica+geo['stage_pair'][stage], 'helper aliases active data family')
        low, high = geo['windows'][owner, child]
        require(low < geo['callpos'][call] < high, 'strict bridge-aware window')
        require(not helpers[time] >> helper & 1, 'duplicate native helper role')
        require(family not in families[time], 'duplicate physical family within call')
        helpers[time] |= 1 << helper
        families[time].add(family)
        require(0 <= offset and offset+width <= geo['ranks'][child], 'slice capacity')
        mask = ((1 << width)-1) << offset
        key = owner, child, port
        require(not used[key] & mask, 'overlapping residual axes in bin')
        used[key] |= mask
        chart_key = port, child, offset, width
        if chart_key not in charts:
            frame = frames[port]
            occupied = [frame.index(v) for v in pending[port,child][offset:offset+width]]
            spectators = [i for i in range(M) if i not in occupied][:H-width]
            permutation = occupied+spectators+[i for i in range(M) if i not in occupied and i not in spectators]
            require(len(set(occupied+spectators)) == H and sorted(permutation) == list(range(M)), 'complete residual spectator chart')
            charts[chart_key] = tuple(frame[i] for i in permutation)
            chart_ids[chart_key] = hashlib.sha256(json.dumps(charts[chart_key], separators=(',',':')).encode()).hexdigest()
        role_charts.append((time, helper, stage, replica, family, chart_ids[chart_key]))
        cross += replica != owner
    require(all(mask == (1 << R)-1 for mask in helpers), 'every native helper exactly once per invocation')
    idle = Counter()
    for owner, child in geo['windows']:
        for port in range(V):
            mask = used[owner,child,port]
            count = mask.bit_count()
            require(mask == (1 << count)-1, 'gap in pending residual prefix')
            remainder = geo['ranks'][child]-count
            if remainder:
                idle[remainder] += 1
    profile = Counter(idle)
    for call in geo['order']:
        profile.update(providers[dispatch[call]]['paid'])
    mass = sum(r*n for r,n in profile.items())
    require(M*(8*T*V)-mass == 23680, 'full profile rank deficit 23680')
    require(M*M > 2*max(profile)**2, 'proper halving child dimension')
    digest = hashlib.sha256()
    for time, helper, stage, replica, family, chart_id in sorted(role_charts):
        digest.update(json.dumps([stage, replica, helper, family, chart_id], separators=(',',':')).encode()+b'\n')
    return dict(status='PASS_INDEPENDENT_400_HELPER_LITERAL_OWNERS_WINDOWS_AXES_AND_PROFILE',
        helpers_per_call=R, roles=len(roles), calls=9*T, live=8*T*V,
        inherited_physical_envelope=8*T*V+8+R+2,
        physical_scope='The 8+R+2 private reserve is inherited, not verified here. In particular private zero-buffer/coefficient label mapping and lifetimes need the separate finite/global invoice.',
        rank_mass=mass, deficit=23680, profile=dict(sorted(profile.items())), idle=dict(sorted(idle.items())),
        local_profiles={pid:dict(sorted(p['paid'].items())) for pid,p in providers.items()},
        width_inventories={pid:dict(sorted(Counter(p['widths']).items())) for pid,p in providers.items()},
        dispatch=dict(Counter(dispatch.values())), cross_replica_roles=cross,
        source_events=geo['source_events'], bridge_events=geo['bridges'], pending_windows=len(geo['windows']),
        pending_bins=len(geo['windows'])*V, unique_residual_spectator_charts=len(set(charts.values())),
        actual_sigma_stream_sha256=digest.hexdigest(), sigma_stream_order='increasing invocation time, then current native helper ID',
        all_whole_owners_distinct_and_active_data_excluded=True, all_pending_residual_axes_disjoint=True,
        scope='Independent finite chronological owner, proper-width, chart and paid-profile replay. Native scalar, warp, local/global phase, emitted-controller equivalence, coefficient invoice and outer bound remain separately required. This is not complete supplier admission.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owners', type=Path, default=HERE/'OWNERS.json.gz')
    parser.add_argument('--parent', type=Path, default=ROOT/'parent')
    parser.add_argument('--base-native', type=Path, default=ROOT/'interface/base')
    parser.add_argument('--extra-native', type=Path, default=ROOT/'interface/extra')
    parser.add_argument('--phases', type=Path, default=HERE/'DATA-PHASES.json')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--controls', action='store_true')
    args = parser.parse_args()
    for name, pin in PARENT_PINS.items():
        require(sha(args.parent/name) == pin, 'parent input pin '+name)
    require(sha(args.phases) == PHASE_PIN, 'inherited phase input pin')
    plan, template, phases = read(args.parent/'new/PLAN.json'), read(args.parent/'GLOBAL-TEMPLATE.json.gz'), read(args.phases)
    require(template['exact_data_phase_recipe_sha256'] == PHASE_PIN, 'parent phase binding')
    providers = {'gauge44':local(args.base_native), 'extra':local(args.extra_native)}
    require(providers['gauge44']['ports'] == providers['extra']['ports'] == plan['provider_registry']['gauge44']['ports'], 'ordered data ports unchanged')
    geo = geometry(plan, template, phases)
    dispatch = {(c['stage'], c['replica']):c['provider'] for c in plan['provider_calls']}
    require(len(plan['provider_calls']) == len(dispatch) == 9*T and set(dispatch) == set(geo['order']), 'complete dispatch')
    require(set(dispatch.values()) == set(providers), 'native provider dispatch registry')
    frames, pending = axes(geo, providers['gauge44']['ports'], phases)
    roles = read(args.owners)
    result = audit(roles, geo, providers, dispatch, frames, pending)
    result.update(parent_head='b479fc5567bc09ab9185bffe89b62594f36d74e5',
                  input_sha256={**{'parent/'+k:v for k,v in PARENT_PINS.items()}, 'owners':sha(args.owners), 'data_phases':sha(args.phases)},
                  native_input_sha256={pid:p['inputs'] for pid,p in providers.items()},
                  checker_sha256=sha(Path(__file__)), controls=[])
    if args.controls:
        mutations = []
        first = roles[0]
        mutations.append(('wrong_width', 0, dict(first, width=first['width']-1), 'whole native helper width'))
        mutations.append(('wrong_family', 0, dict(first, family=8*T*V), 'physical family identity'))
        mutations.append(('wrong_time', 0, dict(first, time=(first['time']+1)%(9*T)), 'owner invocation time'))
        same_call = next(i for i,z in enumerate(roles) if i and z['time'] == first['time'])
        duplicate = dict(roles[same_call], helper=first['helper'], width=first['width'])
        mutations.append(('duplicate_helper', same_call, duplicate, 'duplicate native helper role'))
        alias = dict(first, helper=roles[same_call]['helper'], width=roles[same_call]['width'])
        mutations.append(('duplicate_family', same_call, alias, 'duplicate physical family within call'))
        mutations.append(('slice_overflow', 0, dict(first, offset=geo['ranks'][first['child']]), 'slice capacity'))
        # A complete physical family substitution, so chronology/active-data
        # controls reach their named predicates without failing field binding.
        for label, active, reason in (
                ('active_data_alias', True, 'helper aliases active data family'),
                ('outside_bridge_window', False, 'strict bridge-aware window')):
            replacement = None
            call = first['stage'], first['replica']
            for child, capacity in geo['ranks'].items():
                is_active = geo['pair'][child] == geo['stage_pair'][first['stage']]
                lo, hi = geo['windows'][first['replica'],child]
                if capacity < first['width'] or is_active != active:
                    continue
                if not active and lo < geo['callpos'][call] < hi:
                    continue
                replacement = dict(first, owner_replica=first['replica'], child=child, offset=0,
                                   copy=V*first['replica']+first['port'],
                                   family=first['replica']*8*V+(2*geo['pair'][child]+geo['side'][child])*V+first['port'])
                break
            require(replacement is not None, 'construct '+label+' control')
            mutations.append((label, 0, replacement, reason))
        previous_bins = {}
        overlap = None
        for index, role in enumerate(roles):
            key = role['owner_replica'], role['child'], role['port']
            if key in previous_bins:
                earlier = previous_bins[key]
                if role['time'] != earlier['time'] and earlier['offset']+role['width'] <= geo['ranks'][role['child']]:
                    overlap = index, dict(role, offset=earlier['offset'])
                    break
            previous_bins[key] = role
        require(overlap is not None, 'construct residual-overlap control')
        mutations.append(('overlapping_residual_axes', overlap[0], overlap[1], 'overlapping residual axes in bin'))
        for name, index, bad, reason in mutations:
            # The optional provenance field must follow the intentionally
            # substituted helper to reach the actual tested predicate.
            if 'original_helper_register' in bad:
                pid = dispatch[bad['stage'],bad['replica']]
                bad['original_helper_register'] = providers[pid]['origins'][bad['helper']]
            changed = list(roles)
            changed[index] = bad
            try:
                audit(changed, geo, providers, dispatch, frames, pending)
            except ValueError as error:
                require(str(error) == reason, 'unexpected negative-control reason: '+name+': '+str(error))
            else:
                raise ValueError('accepted negative control: '+name)
            result['controls'].append(name)
    if args.out:
        args.out.write_text(json.dumps(result, indent=2)+'\n')
    print(result['status'])
    print(json.dumps({k:result[k] for k in ('roles','profile','idle','rank_mass','deficit','controls')}, sort_keys=True))


if __name__ == '__main__':
    main()
