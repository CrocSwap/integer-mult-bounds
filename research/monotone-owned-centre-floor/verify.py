#!/usr/bin/env python3
"""Exact monotone owned-centre floor. Standard library only.

Cinna Davis / 1337isnot1337, substantial OpenAI Codex assistance. Apache-2.0.
Scientific word: Cao Yifan's round-three word and its credited predecessors.
All native warp relations and all helper boundary constraints are discarded.
"""
from collections import Counter, defaultdict, deque
from copy import deepcopy
import argparse
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
SOURCE_SHA = '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
PAYLOAD_SHA = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def basis(vectors):
    pivots = {}
    for value in vectors:
        v = value
        while v:
            p = v.bit_length() - 1
            if p in pivots:
                v ^= pivots[p]
            else:
                pivots[p] = v
                break
    return [pivots[p] for p in sorted(pivots)]


def span(vectors):
    out = {0}
    for v in vectors:
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def load_source():
    data = (ROOT / SOURCE).read_bytes()
    need(hashlib.sha256(data).hexdigest() == SOURCE_SHA, 'Frozen source bytes')
    raw = gzip.decompress(data)
    need(hashlib.sha256(raw).hexdigest() == PAYLOAD_SHA, 'Frozen source payload')
    return json.loads(raw)


def graph(payload, direction):
    """Occurrence DAG; scalar indices omit climbs. No edge crosses a warp.

    0..631 are persistent entrances; 632+i is scalar event i; a warp resets
    its field to unconstrained node 632+N+i. All scalar contacts involving
    owned C0 are released too. No helper or final boundary edges are used.
    """
    c = payload['canonical']
    raw = [e for e in payload['programs'][direction] if e[0] != 'climb']
    need(len(c['start']) == len(c['final']) == 632, '632 independent persistent fields')
    spaces = [span(b) for b in c['frames']]
    need(all(len(b) == len(basis(b)) for b in c['frames']), 'Independent frame bases')
    current = list(range(632))
    frames = dict(enumerate(c['start']))
    incoming = defaultdict(list)
    edges = set()
    targets = []
    warps = 0
    for i, event in enumerate(raw):
        if event[0] == 'scalar':
            gate, frame = event[1:]
            refs = gate[1:3] if gate[0] in ('add', 'copy') else gate[1:2]
            roles = [r[1] for r in refs if r[0] == 'L']
            node = 632 + i
            frames[node] = frame
            for r in roles:
                a = current[r]
                need(spaces[frames[a]] <= spaces[frame], 'Source monotone persistent edge')
                edges.add((a, node))
                incoming[node].append(a)
                current[r] = node
            if frame != 0 and roles and any(r[0] == 'C' for r in refs):
                need(len(roles) == 1, 'One persistent source at high owned contact')
                targets.append({'event': i, 'node': node, 'role': roles[0], 'frame': frame})
        elif event[0] == 'warp':
            need(event[1][0] == 'L', 'Native warp has persistent role')
            node = 632 + len(raw) + i
            frames[node] = event[4]
            current[event[1][1]] = node
            warps += 1
    centers = [(i, e) for i, e in enumerate(raw) if e[0] == 'center']
    need(len(targets) == len(centers) == 8, 'All eight owned lifetimes')
    need([x['role'] for x in targets] == [92, 57, 81, 224, 11, 240, 9, 256], 'Actual owned sources')
    for target, (i, center) in zip(targets, centers):
        high = target['frame']
        need(len(c['frames'][high]) == 8, 'Source rank-eight high chart')
        if direction == 'forward':
            need(raw[target['event']][1] == ['copy', ['C', 0], ['L', target['role']]], 'Actual COPY')
            need(target['event'] + 1 == i, 'COPY immediately before descending center')
            need(raw[i - 2] == ['scalar', ['clear', ['C', 0]], high], 'Owned initialization')
            need(center == ['center', 0, high, 0, 8], 'Actual descending center')
        else:
            need(raw[target['event']][1] == ['add', ['L', target['role']], ['C', 0], -1, 1], 'Actual dual output ADD')
            need(i + 1 == target['event'], 'Ascending center immediately before output')
            need(raw[i + 2] == ['scalar', ['clear', ['C', 0]], high], 'Owned final cleanup')
            need(center == ['center', 0, 0, high, 8], 'Actual ascending center')
    paid = Counter(e[5] for e in payload['programs'][direction] if e[0] == 'climb')
    paid.update(e[4] for _, e in centers)
    need(paid == Counter({1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}), 'Complete baseline paid profile')
    helpers = Counter(len(c['frames'][c['final'][r]]) - len(c['frames'][c['start'][r]]) for r in range(224, 632))
    need(helpers == Counter({4: 28, 7: 7, 8: 47, 9: 326}), 'All 408 independent helper targets')
    return {'raw': raw, 'spaces': spaces, 'frames': frames, 'incoming': incoming,
            'edges': edges, 'targets': targets, 'warps': warps}


def witness_paths(payload, g, target):
    """Shortest ancestor paths, greedily selecting independent entrance vectors."""
    dest = target['node']
    following = {dest: None}
    queue = deque([dest])
    reached = []
    while queue:
        node = queue.popleft()
        if node < 224:
            for v in payload['canonical']['frames'][g['frames'][node]]:
                reached.append((node, v))
        for a in sorted(g['incoming'][node]):
            if a not in following:
                following[a] = node
                queue.append(a)
    witnesses, vectors = [], []
    for root, v in reached:
        if len(basis(vectors + [v])) == len(vectors):
            continue
        path = [root]
        while path[-1] != dest:
            path.append(following[path[-1]])
        witnesses.append({'entrance_role': root, 'vector': v, 'path': path})
        vectors.append(v)
    need(len(vectors) == 8, 'Eight independent main entrance ancestors')
    return {**target, 'lower_dimension': 8, 'witnesses': witnesses}


def check_witnesses(payload, g, rows):
    need(len(rows) == len(g['targets']), 'Complete target list')
    links = 0
    for row, target in zip(rows, g['targets']):
        need(all(row[k] == v for k, v in target.items()), 'Actual target binding')
        vectors = []
        need(len(row['witnesses']) == row['lower_dimension'] == 8, 'Eight witness vectors')
        for w in row['witnesses']:
            root, v, path = w['entrance_role'], w['vector'], w['path']
            need(0 <= root < 224, 'Seed is a fixed main entrance')
            need(v != 0 and v in g['spaces'][payload['canonical']['start'][root]], 'Actual fixed entrance vector')
            need(path[0] == root and path[-1] == target['node'], 'Path endpoints')
            need(len(path) == len(set(path)), 'Acyclic witness path')
            for a, b in zip(path, path[1:]):
                need((a, b) in g['edges'], 'Actual monotone chronological edge')
                links += 1
            need(v in g['spaces'][target['frame']], 'Source attains witness containment')
            vectors.append(v)
        need(len(basis(vectors)) == 8, 'Independent witness vectors')
        need(span(vectors) == g['spaces'][target['frame']], 'Sharp original high frame')
    return links


def rejection_controls(payload, g, rows):
    def rejects(mutant):
        try:
            check_witnesses(payload, g, mutant)
        except ValueError:
            return
        raise ValueError('Corruption control accepted')
    bad = deepcopy(rows); bad.pop(); rejects(bad)
    bad = deepcopy(rows); bad[0]['role'] ^= 1; rejects(bad)
    bad = deepcopy(rows); bad[0]['witnesses'][1] = deepcopy(bad[0]['witnesses'][0]); rejects(bad)
    bad = deepcopy(rows); bad[0]['witnesses'][0]['entrance_role'] = 224; rejects(bad)
    bad = deepcopy(rows); bad[0]['witnesses'][0]['vector'] = 0; rejects(bad)
    bad = deepcopy(rows); bad[0]['witnesses'][0]['path'][-1] -= 1; rejects(bad)
    bad = deepcopy(rows)
    path = bad[0]['witnesses'][0]['path']
    need(len(path) > 2, 'Nontrivial path control')
    bad[0]['witnesses'][0]['path'] = [path[0], path[-1]]; rejects(bad)
    for row in rows:
        vectors = [w['vector'] for w in row['witnesses']]
        for omitted in range(8):
            smaller = span(vectors[:omitted] + vectors[omitted + 1:])
            need(len(smaller) == 128 and not all(v in smaller for v in vectors), 'Rank-seven hyperplane control')
    for i, e in enumerate(g['raw']):
        if e[0] == 'warp':
            out = 632 + len(g['raw']) + i
            need(not g['incoming'][out], 'Every warp relation cut')
    return 7 + 8 * len(rows) + 1


def produce(payload):
    out = {'source_sha256': SOURCE_SHA, 'payload_sha256': PAYLOAD_SHA,
           'scope': 'FIXED_SCALAR_WORD_MONOTONE_CONTACT_FLOOR_ONLY', 'directions': {}}
    for direction in ('forward', 'backward'):
        g = graph(payload, direction)
        rows = [witness_paths(payload, g, t) for t in g['targets']]
        links = check_witnesses(payload, g, rows)
        out['directions'][direction] = {'cut_native_events': g['warps'],
            'monotone_edges': len(g['edges']), 'targets': rows, 'path_links': links}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='Regenerate deterministic witnesses')
    args = ap.parse_args()
    payload = load_source()
    result = produce(payload)
    path = HERE / 'WITNESSES.json'
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    saved = json.loads(path.read_text())
    need(saved == result, 'Deterministic source-bound witness artifact')
    controls = 0
    for direction in ('forward', 'backward'):
        g = graph(payload, direction)
        rows = saved['directions'][direction]['targets']
        check_witnesses(payload, g, rows)
        controls += rejection_controls(payload, g, rows)
    print(json.dumps({'status': 'PASS_MONOTONE_OWNED_CENTRE_FLOOR', 'directions': 2,
        'centers_per_direction': 8, 'minimum_each_high_dimension': 8,
        'minimum_center_rank_mass_with_opposite_zero': 64,
        'path_links': {d: result['directions'][d]['path_links'] for d in result['directions']},
        'controls': controls, 'new_kappa': False}, sort_keys=True))


if __name__ == '__main__':
    main()
