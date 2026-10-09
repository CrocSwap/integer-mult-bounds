#!/usr/bin/env python3
"""Incremental reconstruction of the selected PR97 shared-core bit profile.

Copyright 2026 icekylinx. Apache-2.0. Construction with GPT-6 Astra;
integration with OpenAI Codex. The inherited PR97 ledger is by Zhihao Chen,
and its frozen scalar/frame witness is Swapnil Jain's construction. Their
original credits, licenses and disclosures remain in the pinned snapshot.
Global-optimal bit gauge subset via exact telescoping interval-min-cut:
Prepared by Thomas Marchand with Google Antigravity assistance.
No complete-basis replay or inherited rational-frame audit is repeated.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

import argparse
from collections import Counter, defaultdict, deque
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

from partial_gauge_bit import ROOT, require, encoded, frozen_sources
from three_stage_cover_network import log_upper, exp_upper

INPUT = ROOT / 'certificates/paired-cube-bit-input.json'
COARSE_OPT = Q(461877426979, 10**15)
BAD_OPT = Q(1, 10**16)


def histogram(value):
    return Counter({int(r): n for r, n in value.items() if n})


def target_histogram(schedule, adjoint, readouts):
    """Delete certified frames in inherited order, with positive Z support.

    Positive support is deliberately retained even when a coefficient is
    even: those extra F2 zero reads are harmless, and keep the certified
    conservative target-frame convention used by the supplied profile.
    Nesting of the actual subspaces is inherited; ranks alone do not prove it.
    """
    current = [0] * schedule.v
    result = Counter()
    for slot in readouts:
        rank = schedule.f[slot]
        for target, coefficient in adjoint[slot].items():
            require(coefficient > 0, 'Nonpositive inherited target coefficient')
            increment = rank-current[target]
            require(increment >= 0, 'Selected target chain retreats')
            if increment:
                result[increment] += 1
            current[target] = rank
    for rank in current:
        require(0 <= rank <= schedule.h-1, 'Target exceeds output frame')
        if rank < schedule.h-1:
            result[schedule.h-1-rank] += 1
    require(sum(r*n for r,n in result.items()) == schedule.v*(schedule.h-1),
            'Target chain rank mass differs')
    return result


def child_histogram(h, v, aux, source, target, gauges):
    children = Counter()
    for local in (aux, source, target, Counter({h-1: h})):
        children.update({r: 3*n for r,n in local.items() if r and n})
    children.update({3*r: n for r,n in gauges.items() if r and n})
    children[2] += 2*v
    return children


def verify_global_mincut(schedule, adjoint, old_aux, source, chosen, children):
    """Certify global optimality over all 2^11565 readout subsets via exact integer min-cut."""
    h, v, R = schedule.h, schedule.v, schedule.R
    m, W = 3 * h, 2 * v + R
    fallback = 32 * m * m
    scale = W * m * (10**16) * (1 << 120)
    logs = {r: log_upper(Q(m, r)) for r in range(1, m)}
    exp_m = exp_upper(COARSE_OPT * log_upper(Q(m)))
    w_int = {0: 0}
    for r in range(1, m):
        val = (Q(r, W * m) * exp_upper(COARSE_OPT * logs[r])
               + BAD_OPT * Q(fallback, W * m) * exp_m) * scale
        require(val.denominator == 1, 'Non-integer scaled moment weight')
        w_int[r] = int(val.numerator)
    slot_ben = {}
    pos_slots = []
    chosen_rank22 = []
    target_ranks = defaultdict(set)
    for s in schedule.readout:
        first = schedule.dim(schedule.start_key(s))
        g = schedule.f[s]
        ben = 3 * w_int[first] - (w_int[3 * g] + 3 * w_int[first - g])
        slot_ben[s] = ben
        if ben > 0:
            if g == h - 1:
                chosen_rank22.append(s)
            else:
                pos_slots.append(s)
                for t in adjoint[s]:
                    target_ranks[t].add(g)
    S, T = 0, 1
    idx = 2
    s_idx = {s: idx + i for i, s in enumerate(pos_slots)}
    idx += len(pos_slots)
    u_node = {}
    for t in sorted(target_ranks):
        k = len(target_ranks[t])
        for p in range(1, k + 1):
            for q in range(p, k + 1):
                u_node[(t, p, q)] = idx
                idx += 1
    graph = [[] for _ in range(idx)]
    orig_edges = []
    def add_edge(u, v_node, cap):
        orig_edges.append((u, v_node, cap))
        graph[u].append([v_node, cap, len(graph[v_node])])
        graph[v_node].append([u, 0, len(graph[u]) - 1])
    inf = sum(slot_ben[s] for s in pos_slots) + 1
    for s in pos_slots:
        add_edge(S, s_idx[s], slot_ben[s])
    for t in sorted(target_ranks):
        cand = sorted(target_ranks[t])
        d_full = [0] + cand + [h - 1]
        k = len(cand)
        for p in range(1, k + 1):
            c_pp = 3 * (w_int[d_full[p] - d_full[p - 1]]
                        + w_int[d_full[p + 1] - d_full[p]]
                        - w_int[d_full[p + 1] - d_full[p - 1]])
            require(c_pp > 0, 'Nonpositive diagonal target cut capacity')
            add_edge(u_node[(t, p, p)], T, c_pp)
            for q in range(p + 1, k + 1):
                c_pq = 3 * (w_int[d_full[q + 1] - d_full[p]]
                            + w_int[d_full[q] - d_full[p - 1]]
                            - w_int[d_full[q + 1] - d_full[p - 1]]
                            - w_int[d_full[q] - d_full[p]])
                require(c_pq > 0, 'Nonpositive telescoping interval capacity')
                add_edge(u_node[(t, p, q)], T, c_pq)
                add_edge(u_node[(t, p, q - 1)], u_node[(t, p, q)], inf)
                add_edge(u_node[(t, p + 1, q)], u_node[(t, p, q)], inf)
    for s in pos_slots:
        g = schedule.f[s]
        for t in adjoint[s]:
            p = sorted(target_ranks[t]).index(g) + 1
            add_edge(s_idx[s], u_node[(t, p, p)], inf)
    flow = 0
    while True:
        level = [-1] * idx
        q = deque([S])
        level[S] = 0
        while q:
            u = q.popleft()
            for v_node, cap, _ in graph[u]:
                if cap > 0 and level[v_node] < 0:
                    level[v_node] = level[u] + 1
                    q.append(v_node)
        if level[T] < 0:
            break
        ptr = [0] * idx
        def dfs(u, pushed):
            if u == T or pushed == 0:
                return pushed
            for i in range(ptr[u], len(graph[u])):
                ptr[u] = i
                v_node, cap, rev = graph[u][i]
                if level[v_node] == level[u] + 1 and cap > 0:
                    tr = dfs(v_node, pushed if pushed < cap else cap)
                    if tr > 0:
                        graph[u][i][1] -= tr
                        graph[v_node][rev][1] += tr
                        return tr
            return 0
        while True:
            pushed = dfs(S, inf)
            if pushed == 0:
                break
            flow += pushed
    vis = [False] * idx
    q = deque([S])
    vis[S] = True
    while q:
        u = q.popleft()
        for v_node, cap, _ in graph[u]:
            if cap > 0 and not vis[v_node]:
                vis[v_node] = True
                q.append(v_node)
    cut_cap = sum(cap for u, v_node, cap in orig_edges if vis[u] and not vis[v_node])
    require(cut_cap == flow, 'Max-flow min-cut duality mismatch')
    mincut_chosen = set(chosen_rank22) | {s for s in pos_slots if vis[s_idx[s]]}
    require(mincut_chosen == chosen, 'Selected subset differs from exact global min-cut optimum')
    empty_aux = Counter(old_aux)
    for s in schedule.readout:
        first = schedule.dim(schedule.start_key(s))
        g = schedule.f[s]
        if first - g:
            empty_aux[first - g] -= 1
        empty_aux[first] += 1
    empty_children = child_histogram(h, v, empty_aux, source, Counter({h - 1: v}), Counter())
    empty_moment = sum(n * w_int[r] for r, n in empty_children.items())
    opt_moment = sum(n * w_int[r] for r, n in children.items())
    total_pos_ben = sum(slot_ben[s] for s in chosen_rank22) + sum(slot_ben[s] for s in pos_slots)
    require(empty_moment - (total_pos_ben - flow) == opt_moment and opt_moment < scale,
            'Exact telescoping min-cut moment identity failed')
    return dict(network_nodes=idx, positive_benefit_slots=len(pos_slots) + len(chosen_rank22),
                max_flow_equals_min_cut=True, exact_moment_identity=True)


def reconstruct(input_path=INPUT):
    record = json.loads(Path(input_path).read_text())
    folder, provenance = frozen_sources(record)
    selection_path = ROOT / record['selection_file']
    require(sha256(selection_path.read_bytes()).hexdigest() == record['selection_sha256'],
            'Selected finite slot list changed')
    selection = json.loads(selection_path.read_text())
    spec = importlib.util.spec_from_file_location('paired_cube_pinned_deferred', folder/'deferred.py')
    deferred = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(deferred)
    with gzip.open(folder/'witness_23.json.gz', 'rt') as stream:
        witness = json.load(stream)
    with gzip.open(folder/'deferred_23.json.gz', 'rt') as stream:
        data = json.load(stream)
    schedule = deferred.Schedule(witness, data)
    ledger = json.loads((folder/'bit-ledger-result.json').read_text())
    for flag in ('complete_forward_F2', 'complete_reflected_F2',
                 'reflected_frame_continuity', 'all_scalar_gates_equal_frame_keys',
                 'histogram_matches_external'):
        require(ledger[flag] is True, 'Inherited physical ledger lacks '+flag)
    selected = selection['retained_readout_order']
    omitted = selection['omitted_readout_order']
    chosen, skipped = set(selected), set(omitted)
    require(len(chosen) == len(selected) == 9730 and len(skipped) == len(omitted) == 1835,
            'Selected gauge counts differ')
    require(chosen.isdisjoint(skipped) and chosen | skipped == schedule.sel,
            'Selection does not partition the inherited gauges')
    require(len(schedule.sel) == 11565, 'Inherited gauge count differs')
    for slots, subset in ((selected, chosen), (omitted, skipped)):
        require(slots == [s for s in schedule.readout if s in subset],
                'Gauge order is not the inherited subsequence')
    h, v, R = schedule.h, schedule.v, schedule.R
    require((h,v,R) == (23,1771,28866), 'Inherited dimensions differ')
    old_aux = deferred.chain_ranks(schedule)
    require(encoded(old_aux) == ledger['rank_histograms']['aux'],
            'Inherited auxiliary chain receipt differs')
    source = Counter(r for path in schedule.xdata() for r in path if r)
    require(sum(r*n for r,n in source.items()) == v*(h-1), 'Source chain mass differs')
    adjoint = schedule.adjoint()  # exact scalar coefficients, not producer bitset unions
    old_target = target_histogram(schedule, adjoint, schedule.readout)
    target = target_histogram(schedule, adjoint, selected)
    aux = Counter(old_aux)
    changed = Counter()
    dirty_reads = odd_dirty_reads = 0
    for slot in omitted:
        first = schedule.dim(schedule.start_key(slot))
        gauge = schedule.f[slot]
        require(0 < gauge <= first, 'Omitted gauge does not fit first-use frame')
        if first-gauge:
            aux[first-gauge] -= 1
        aux[first] += 1
        changed[(first-gauge, first)] += 1
        # The exact same old-value coefficient is emitted in the initial
        # prelude, before any slot or target frame grows from zero. Thus its
        # source/target frame keys are both ('0',), for arbitrary dirty inputs.
        dirty_reads += len(adjoint[slot])
        odd_dirty_reads += sum(c & 1 for c in adjoint[slot].values())
    schedule.sel = chosen
    require(encoded(deferred.chain_ranks(schedule)) == encoded(aux),
            'Direct modified frame chains differ from transition deltas')
    require(all(n >= 0 for n in aux.values()), 'Negative changed auxiliary count')
    gauges = Counter(schedule.f[s] for s in selected)
    children = child_histogram(h,v,aux,source,target,gauges)
    mincut_receipt = verify_global_mincut(schedule, adjoint, old_aux, source, chosen, children)
    values = dict(h=h,v=v,R=R,m=3*h,W_per_vertex=2*v+R,loss=h*(h-1),
                  deficit_per_vertex=2*v-3*h*(h-1),selected_roles=len(selected),
                  omitted_roles=len(omitted),rank_per_vertex=sum(r*n for r,n in children.items()))
    for key, value in values.items():
        require(record[key] == value, 'Selected profile differs: '+key)
    for key, value in (('auxiliary_histogram', aux), ('source_data_histogram', source),
                       ('target_data_histogram', target), ('selected_rank_histogram', gauges),
                       ('copied_center_histogram', Counter({h-1:h})), ('child_histogram', children)):
        require(histogram(record[key]) == +value, 'Selected profile differs: '+key)
    require(values['W_per_vertex']*values['m']-values['rank_per_vertex'] == 2024,
            'Shared-core rank deficit differs')
    require(all(0 < r < 3*h and n > 0 for r,n in children.items()), 'Invalid child')
    result = dict(record)
    result['checks'] = dict(source_hashes_equal=True, selected_slot_partition_equal=True,
        target_chains_inherited_subsequences=True, positive_integer_support=True,
        omitted_dirty_reads_at_zero=True, changed_chain_histograms_equal=True,
        selected_profile_equal=True, global_mincut_optimum_verified=True,
        full_upstream_audits_repeated=False)
    result['global_mincut_receipt'] = mincut_receipt
    result['changed_transition_histogram'] = [dict(old_rank=a,new_rank=b,count=n)
                                             for (a,b),n in sorted(changed.items())]
    result['zero_prelude_receipt'] = dict(omitted_slots=len(omitted),
        positive_support_reads=dirty_reads,odd_F2_reads=odd_dirty_reads,
        source_frame=['0'],target_frame=['0'],scalar_coefficients='exact inherited adjoint',
        placement='before every positive-rank local operation')
    result['provenance'] = dict(pr97=provenance['pr97'], underlying=provenance['underlying'])
    result['scope'] = ('Incremental selected-gauge rank, zero-prelude and exact global min-cut '
                       'optimality check; actual nested subspaces and unchanged complete scalar '
                       'word remain inherited. Strict rational supplier moments are checked by '
                       'paired_cube_network.py.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=INPUT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = json.dumps(reconstruct(args.input), indent=2, sort_keys=True)+'\n'
    if args.output:
        args.output.write_text(result)
    else:
        print(result, end='')


if __name__ == '__main__':
    main()
