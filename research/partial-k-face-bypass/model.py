"""Exact mixed K/M face geometry and bounded scheduling, Apache-2.0.

Douglas R. Colkitt, with substantial OpenAI Codex assistance. Geometry and
scalar conventions follow icekylinx's #531 and Kothe/AtomScout's #622.
This implementation reads the packet data; it imports no constructor code.
"""
from collections import defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations
import gzip
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


@lru_cache(None)
def basis(vectors):
    pivots = {}
    for value in vectors:
        for bit in sorted(pivots, reverse=True):
            if value >> bit & 1:
                value ^= pivots[bit]
        if value:
            bit = value.bit_length() - 1
            for other in pivots:
                if pivots[other] >> bit & 1:
                    pivots[other] ^= value
            pivots[bit] = value
    return tuple(pivots[bit] for bit in sorted(pivots, reverse=True))


@lru_cache(None)
def join(left, right):
    return basis(left + right)


def contained(frame, labels):
    return all((vector & label).bit_count() % 2 == 0
               for vector in frame for label in labels)


def load_geometry(directory):
    prototype = json.loads((directory / 'PROTOTYPE.json').read_text())
    modules = json.loads(gzip.decompress((directory / 'PACKET-PROGRAMS.json.gz').read_bytes()))
    ports, roots = prototype['binary_ports'], prototype['root_lines']
    blocks = {}
    requests = defaultdict(list)
    own = {}
    for module in modules:
        block = tuple(module['receipt']['block'])
        ids = module['receipt']['source_lines']
        rows = [{source: Q(1)} for source in ids] + [{} for _ in range(16)]
        frames = [(ports[source],) for source in ids] + [()] * 16
        for event, vectors in zip(module['events'][:40], module['event_frames'][:40]):
            target, source, num, den = event
            frame = basis(tuple(vectors))
            for reg in (target, source):
                require(join(frames[reg], frame) == frame, 'packet prefix frame descent')
                frames[reg] = frame
            for key, value in list(rows[source].items()):
                rows[target][key] = rows[target].get(key, Q(0)) + Q(num, den) * value
                if not rows[target][key]:
                    del rows[target][key]
        blocks[block] = dict(module=module, rows=rows, frames=frames, ids=ids)
        p, q = block[:2], block[2:]
        tetrads = [[s for s in ids if sum(roots[s][i] < 0 for i in block) % 2 == parity]
                   for parity in (0, 1)]
        for parity, tetrad in enumerate(tetrads):
            groups = defaultdict(list)
            for target in tetrad:
                groups[roots[target][p[0]] * roots[target][p[1]]].append(target)
            for eps, group in sorted(groups.items()):
                t, u = sorted(group)
                zz = -Q(2 * roots[u][p[0]], roots[t][p[0]])
                for target, sign in ((t, -1), (u, 1)):
                    wanted = {}
                    for source in tetrads[1 - parity]:
                        gt = Q(sum(a*b for a, b in zip(roots[t], roots[source])), 2)
                        gu = Q(sum(a*b for a, b in zip(roots[u], roots[source])), 2)
                        coefficient = -gt/4 - sign*gu/2/zz
                        if coefficient:
                            wanted[source] = coefficient
                    matches = []
                    for reg, row in enumerate(rows):
                        if set(row) != set(wanted):
                            continue
                        first = next(iter(wanted))
                        scale = wanted[first] / row[first]
                        if all(wanted[s] == scale*row[s] for s in wanted):
                            matches.append(reg)
                    require(len(matches) == 1, 'own token not unique')
                    own[target] = (block, matches[0])
                requests[block, p, eps].append(t)
                e2 = roots[t][q[0]] * roots[t][q[1]]
                requests[block, q, e2].append(u)
    return dict(ports=ports, roots=roots, blocks=blocks, requests=requests, own=own)


def face(geometry, block, pair, sign):
    data = geometry['blocks'][block]
    module = data['module']
    keys = [(p, e) for p in combinations(block, 2) for e in (-1, 1)]
    output, alpha = module['outputs'][keys.index((pair, sign))]
    events = [e for e in module['events'][40:] if e[0] == output]
    require(len(events) == 1, 'face not formed by one addition')
    a, b, num, den = events[0]
    require((num, den) == (1, 1), 'unexpected face coefficients')
    return (a, b), join(data['frames'][a], data['frames'][b])


def mixed_pairs(geometry):
    return [pair for pair in combinations(range(8), 2)
            if sum((block, pair, -1) in geometry['requests']
                   for block in geometry['blocks']) == 2]


def case(geometry, pair, sign):
    blocks, requests, own = (geometry[k] for k in ('blocks', 'requests', 'own'))
    incident = sorted(b for b in blocks if set(pair) <= set(b))
    selected = [b for b in incident if (b, pair, sign) in requests]
    require(len(incident) == 3 and len(selected) == 2, 'not a mixed pair')
    ordinary = next(b for b in incident if b not in selected)
    targets = sorted(t for b in selected for t in requests[b, pair, sign])
    leavers = [(b, r) for b in selected for r in face(geometry, b, pair, sign)[0]]
    frames = [blocks[b]['frames'][r] for b, r in leavers]
    ordinary_targets = [t for t in blocks[ordinary]['ids']
                        if geometry['roots'][t][pair[0]] * geometry['roots'][t][pair[1]] == sign]
    mlabels = [geometry['ports'][t] for t in ordinary_targets]
    labels = [geometry['ports'][t] for t in targets]
    packet = face(geometry, ordinary, pair, sign)[1]
    operations, pre_packet = [], []
    for index, target in enumerate(targets):
        own_index = leavers.index(own[target])
        operations.append((index, 4 + own_index, 'own'))
        other = next(b for b in selected if b != own[target][0])
        foreign = [j for j, (b, _) in enumerate(leavers) if b == other]
        operations.extend((index, 4 + j, 'raw') for j in foreign)
        pre_packet.append(basis(frames[own_index] + tuple(x for j in foreign for x in frames[j])))
    operations.extend((i, -1, 'packet') for i in range(4))
    require(all(contained(f, mlabels) for f in frames), 'raw leaver outside ordinary caps')
    obstruction = next((x, t-8, geometry['ports'][t]) for x in packet for t in ordinary_targets
                       if (x & geometry['ports'][t]).bit_count() % 2)
    complete = [join(f, packet) for f in pre_packet]
    cross = [[contained(f, [label]) for label in labels] for f in complete]
    require(cross == [[i == j for j in range(4)] for i in range(4)], 'packet sharing remains possible')
    witnesses = [[i, j, next(x for x in complete[i] if (x & labels[j]).bit_count() % 2)]
                 for i in range(4) for j in range(4) if i != j]
    return dict(pair=list(pair), sign=sign, selected_blocks=selected, ordinary_block=ordinary,
                targets=[t-8 for t in targets], ordinary_targets=[t-8 for t in ordinary_targets],
                target_labels=labels, ordinary_labels=mlabels, leavers=leavers,
                leaver_frames=frames, packet_frame=packet, pre_packet_frames=pre_packet,
                complete_frames=complete, packet_outside_ordinary_caps=obstruction,
                cross_cap_matrix=cross, cross_cap_witnesses=witnesses,
                operations=operations, packet_carrier_lower_bound=4)


def search(data, copies, ordinary_guard=True, state_limit=2_000_000):
    """Complete memoized state search, or explicitly stop at state_limit.

Target reads change both operand frames to their join. Each required read is
executed once; every packet read chooses a carrier. Equal adjacent packet
states are interchangeable, so skip only that exact symmetry.
    """
    ops, labels = data['operations'], data['target_labels']
    initial = ((),)*4 + tuple(data['leaver_frames']) + (tuple(data['packet_frame']),)*copies
    visited = 0

    @lru_cache(None)
    def dfs(done, state):
        nonlocal visited
        visited += 1
        if visited > state_limit:
            raise RuntimeError('state limit exceeded; no exhaustion claim')
        if done == (1 << len(ops)) - 1:
            return ()
        for i, (a, source, _) in enumerate(ops):
            if done >> i & 1:
                continue
            for b in ([source] if source >= 0 else range(8, 8 + copies)):
                if source < 0 and b > 8 and state[b] == state[b-1]:
                    continue
                frame = join(state[a], state[b])
                if not contained(frame, [labels[a]]):
                    continue
                if ordinary_guard and b < 8 and not contained(frame, data['ordinary_labels']):
                    continue
                if any(ob == b and j != i and not(done >> j & 1) and
                       not contained(frame, [labels[oa]]) for j, (oa, ob, _) in enumerate(ops)):
                    continue
                updated = list(state)
                updated[a] = updated[b] = frame
                if any(not(done >> j & 1) and j != i and ob < 0 and
                       not any(contained(updated[k], [labels[oa]]) for k in range(8, 8+copies))
                       for j, (oa, ob, _) in enumerate(ops)):
                    continue
                suffix = dfs(done | 1 << i, tuple(updated))
                if suffix is not None:
                    return ((i, b),) + suffix
        return None

    schedule = dfs(0, initial)
    return dict(copies=copies, ordinary_guard=ordinary_guard, states=visited,
                status='EXHAUSTED' if schedule is None else 'FOUND',
                schedule=schedule, state_limit=state_limit)


def recipe(data, schedule):
    reads = []
    for event, source in schedule:
        target = data['targets'][data['operations'][event][0]]
        if source >= 8:
            reads.append([target, 'packet', source-8])
        else:
            block, local = data['leavers'][source-4]
            reads.append([target, 'leaver', list(block), local])
    return dict(pair=data['pair'], sign=data['sign'], blocks=data['selected_blocks'],
                targets=data['targets'], ops=reads)
