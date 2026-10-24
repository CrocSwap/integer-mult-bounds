"""Source-bound fixed-projection-height Clifford invoice obstruction.

For an inverse-image Clifford chart L=F^-1(Z), its x-projection height is
k(L)=d(L,Z), where d(L,M)=9-dim(L intersect M) is the Fourier-rank metric.
Fixing each node's source height makes every paid rank at least its original
nested rank. The 358 zero-entrance helpers have fixed residual rank. Each of
the other 50 helpers has a native-free paid wire path whose source rank sum
equals its residual rank. These paths share no paid edge occurrence.

If one path has source ranks r_i, increases delta_i>=0, and R=sum(r_i),
concavity of H(x)=x**t (0<t<=1) gives
  sum(H(r_i+delta_i)-H(r_i)) >= H(R+sum(delta_i))-H(R).
The rank triangle inequality bounds the changed helper residual by
R+sum(delta_i), so its entire additional credit is funded by that path.
Source native costs are zero, and owned-center tariffs remain fixed.
Therefore neither frozen orientation has a cheaper complete invoice, even
with arbitrary quadratic Clifford charts of the fixed projection heights.

This verifies source incidences and the hypotheses of the written proof;
it is not a proof-kernel certificate or a new physical supplier admission.
Only the Python standard library is used. All checks survive python -O.
"""
from pathlib import Path
from collections import Counter
import argparse
import copy
import gzip
import hashlib
import json


SOURCE_SHA256 = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
EXPECTED_PAID = Counter({1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8})
EXPECTED_HELPERS = Counter({4: 28, 7: 7, 8: 47, 9: 326})


def need(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {x ^ vector for x in tuple(result)}
    return frozenset(result)


def dimension(space):
    need(len(space) > 0 and not len(space) & (len(space)-1), 'subspace cardinality')
    return len(space).bit_length()-1


def map_vector(columns, vector):
    result = 0
    for bit, column in enumerate(columns):
        if vector >> bit & 1:
            result ^= column
    return result


def inverse(columns):
    values = {map_vector(columns, x): x for x in range(512)}
    need(len(values) == 512, 'invertible native map')
    return tuple(values[1 << i] for i in range(9))


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def source_graph(payload, direction='forward'):
    """Reconstruct chronological contacts and every persistent wire incidence."""
    need(direction in ('forward', 'backward'), 'known program orientation')
    program = payload['programs'][direction]
    canonical = payload['canonical']
    frames = list(map(span, canonical['frames']))
    need(canonical['h'] == 9 and len(canonical['start']) == len(canonical['final']) == 632,
         'source dimensions')
    need(all(dimension(s) == len(b) for s, b in zip(frames, canonical['frames'])),
         'independent canonical frame bases')
    maps = {w['op']: tuple(w['G_columns']) for w in canonical['warps']}
    maps.update({-op: inverse(g) for op, g in list(maps.items())})
    nodes, edges, adapter_roles = [], [], []
    paths = [[] for _ in range(632)]

    def node(label):
        index = len(nodes)
        nodes.append(label)
        return index

    def edge(kind, start, end, role, rank, event):
        index = len(edges)
        edges.append({'kind': kind, 'a': start, 'b': end, 'role': role,
                      'rank': rank, 'event': event})
        paths[role].append(index)

    current = [node(label) for label in canonical['start']]
    entrances = current[:]
    for event_index, event in enumerate(program):
        kind = event[0]
        if kind == 'scalar':
            gate, label = event[1:]
            refs = gate[1:3] if gate[0] in ('add', 'copy') else gate[1:2]
            contact = node(label)
            for role_kind, role in refs:
                if role_kind != 'L':
                    continue
                old = nodes[current[role]]
                need(frames[old] <= frames[label], 'every source paid edge nested')
                edge('paid', current[role], contact, role,
                     dimension(frames[label])-dimension(frames[old]), event_index)
                current[role] = contact
        elif kind == 'warp':
            _, role_ref, op, source, target = event
            need(role_ref[0] == 'L', 'persistent native occurrence')
            role = role_ref[1]
            left, right = node(source), node(target)
            old = nodes[current[role]]
            need(frames[old] <= frames[source], 'source paid pre-warp nesting')
            edge('paid', current[role], left, role,
                 dimension(frames[source])-dimension(frames[old]), event_index)
            need(frozenset(map_vector(maps[op], v) for v in frames[source]) == frames[target],
                 'source native rank zero')
            edge('native', left, right, role, 0, event_index)
            current[role] = right
        elif kind == 'adapter':
            need(len(event) == 4 and event[1] in ('old_to_new', 'new_to_old')
                 and type(event[2]) is int and 0 <= event[2] < 224,
                 'source adapters touch only main roles')
            adapter_roles.append(event[2])
        else:
            need(kind in ('climb', 'center', 'phase'), 'known source event')

    exits = []
    for role, label in enumerate(canonical['final']):
        final = node(label)
        exits.append(final)
        old = nodes[current[role]]
        need(frames[old] <= frames[label], 'source final nesting')
        edge('paid', current[role], final, role,
             dimension(frames[label])-dimension(frames[old]), len(program))

    paid = Counter(e['rank'] for e in edges if e['kind'] == 'paid' and e['rank'])
    emitted = Counter(e[5] for e in program if e[0] == 'climb')
    need(paid == emitted, 'all positive source paid occurrences reconstructed')
    centers = Counter(e[4] for e in program if e[0] == 'center')
    need(centers == Counter({8: 8}) and paid+centers == EXPECTED_PAID,
         'complete source invoice')
    need(Counter(adapter_roles) == Counter({role: 2 for role in range(224)}),
         'both source main adapter boundaries')

    nonzero_entrances, zero_entrances = [], []
    helper_dimensions, helper_ranks = Counter(), Counter()
    for role in range(224, 632):
        start = frames[canonical['start'][role]]
        finish = frames[canonical['final'][role]]
        k, l = dimension(start), dimension(finish)
        need(start < finish, 'source helper strictly nested and productive')
        helper_dimensions[k, l] += 1
        helper_ranks[l-k] += 1
        (nonzero_entrances if k else zero_entrances).append(role)
    need(len(nonzero_entrances) == 50 and len(zero_entrances) == 358,
         'complete helper entrance partition')
    need(helper_ranks == EXPECTED_HELPERS, 'source helper rank census')
    return {'nodes': nodes, 'edges': edges, 'frames': frames,
            'paths': {role: paths[role] for role in nonzero_entrances},
            'entrances': entrances, 'exits': exits, 'centers': centers,
            'paid': paid, 'helper_dimensions': helper_dimensions,
            'helper_ranks': helper_ranks, 'nonzero_entrances': nonzero_entrances,
            'zero_entrances': zero_entrances, 'adapter_roles': adapter_roles}


def check_paths(graph, paths):
    """Check every nonzero-entrance helper's complete actual paid wire path."""
    need(sorted(paths) == graph['nonzero_entrances'],
         'every nonzero-entrance helper path covered')
    all_ids = [index for ids in paths.values() for index in ids]
    need(len(all_ids) == len(set(all_ids)), 'path paid edge occurrences disjoint')
    result = []
    for role, ids in paths.items():
        need(ids, 'nonempty helper path')
        current = graph['entrances'][role]
        ranks, positive = [], []
        for index in ids:
            need(type(index) is int and 0 <= index < len(graph['edges']), 'path edge range')
            edge = graph['edges'][index]
            need(edge['kind'] == 'paid', 'path has no native operation')
            need(edge['role'] == role and edge['a'] == current,
                 'continuous actual helper-wire path')
            current = edge['b']
            ranks.append(edge['rank'])
            if edge['rank']:
                positive.append({'edge': index, 'event': edge['event'],
                                 'rank': edge['rank'], 'a': edge['a'], 'b': edge['b']})
        need(current == graph['exits'][role], 'complete helper entry to exit path')
        start = graph['frames'][graph['nodes'][graph['entrances'][role]]]
        finish = graph['frames'][graph['nodes'][graph['exits'][role]]]
        k, l = dimension(start), dimension(finish)
        need(0 < k < l <= 9 and start < finish, 'source helper endpoint heights')
        need(sum(ranks) == l-k, 'source helper path geodesic')
        result.append({'role': role, 'entrance_node': graph['entrances'][role],
                       'exit_node': graph['exits'][role], 'entrance_height': k,
                       'exit_height': l, 'source_helper_rank': l-k,
                       'edge_occurrences': ids, 'positive_source_edges': positive,
                       'path_rank_mass': sum(ranks)})
    need(len(all_ids) == 1016, 'complete selected paid path occurrence census')
    return result


def verify(payload):
    need(canonical_hash(payload) == SOURCE_SHA256, 'source payload hash')
    directions = {}
    for direction in ('forward', 'backward'):
        graph = source_graph(payload, direction)
        paths = check_paths(graph, graph['paths'])
        directions[direction] = {
            'program_sha256': canonical_hash(payload['programs'][direction]),
            'nodes': len(graph['nodes']),
            'paid_edge_occurrences': sum(e['kind'] == 'paid' for e in graph['edges']),
            'native_edge_occurrences': sum(e['kind'] == 'native' for e in graph['edges']),
            'source_native_ranks_all_zero': True,
            'source_main_adapter_occurrences': len(graph['adapter_roles']),
            'source_adapters_touch_no_helper': True,
            'helper_dimension_census': {str(k)+'->'+str(l): v for (k, l), v
                                        in sorted(graph['helper_dimensions'].items())},
            'zero_entrance_helpers': graph['zero_entrances'],
            'rigid_zero_entrance_helper_count': len(graph['zero_entrances']),
            'paid_only_nonzero_entrance_helper_count': len(paths),
            'selected_paid_edge_occurrences': sum(len(p['edge_occurrences']) for p in paths),
            'paths_edge_occurrence_disjoint': True,
            'source_geodesic_rank_census': dict(sorted(Counter(p['source_helper_rank'] for p in paths).items())),
            'paths': paths,
            'owned_center_profile_fixed': dict(sorted(graph['centers'].items())),
            'baseline_paid_profile': dict(sorted((graph['paid']+graph['centers']).items())),
            'baseline_helper_profile': dict(sorted(graph['helper_ranks'].items()))}
    return {
        'status': 'PASS_FIXED_PROJECTION_HEIGHT_CLIFFORD_OBSTRUCTION',
        'source_sha256': SOURCE_SHA256,
        'directions': directions,
        'rank_metric': 'd(L,M)=9-dim(L intersect M), L(F)=F^-1(Z)',
        'fixed_height': 'k(L)=dim(proj_x L)=d(L,Z)',
        'path_debt_inequality': 'sum(H(r_i+delta_i)-H(r_i)) >= H(sum(r_i)+sum(delta_i))-H(sum(r_i))',
        'proof_domain': 'H(x)=x^t, H(0)=0, 0<t<=1; equivalently 0<=C<1 with t=1-C',
        'scope': 'In each frozen scalar/contact word, arbitrary Clifford inverse-image charts preserving every node x-projection dimension cannot lower the complete invoice with the retained helper contracts and fixed owned-center tariffs. Compatible shared native maps may vary, and the two orientations may choose charts independently. Contact-height changes, different scalar graphs, changed helper contracts and changed owned-center tariffs remain outside the theorem. No new physical supplier, phase replay, compiler admission or improved kappa is asserted.'}


def controls(payload):
    result = {}
    for direction in ('forward', 'backward'):
        graph = source_graph(payload, direction)
        found = []

        def reject(name, action, expected):
            try:
                action()
            except ValueError as error:
                need(expected in str(error), 'unexpected rejection: '+str(error))
                found.append(name)
            else:
                raise ValueError('accepted corruption: '+name)

        bad = copy.deepcopy(payload)
        next(e for e in bad['programs'][direction]
             if e[0] == 'scalar' and e[1][0] == 'add')[1][3] += 1
        reject('changed source coefficient', lambda: verify(bad), 'source payload hash')
        paths = copy.deepcopy(graph['paths'])
        position = next(j for j, i in enumerate(paths[525][:-1])
                        if graph['edges'][i]['rank'] == 0)
        paths[525].pop(position)
        reject('omitted old-zero path edge', lambda: check_paths(graph, paths),
               'continuous actual helper-wire path')
        paths = copy.deepcopy(graph['paths'])
        paths[537] = paths[525]
        reject('double-counted shared paid debt', lambda: check_paths(graph, paths),
               'path paid edge occurrences disjoint')
        paths = copy.deepcopy(graph['paths'])
        paths[525][0] = next(i for i, e in enumerate(graph['edges']) if e['kind'] == 'native')
        reject('inserted native operation in path', lambda: check_paths(graph, paths),
               'path has no native operation')
        result[direction] = found
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    raw = args.word.read_bytes()
    payload = json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)
    result = verify(payload)
    if args.self_test:
        result['negative_controls'] = controls(payload)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    summary = copy.deepcopy(result)
    for evidence in summary['directions'].values():
        evidence.pop('paths')
        evidence.pop('zero_entrance_helpers')
    print(json.dumps(summary, indent=2))
