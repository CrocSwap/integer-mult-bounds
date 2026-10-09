#!/usr/bin/env python3
"""Incremental reconstruction of the selected PR97 shared-core bit profile.

Copyright 2026 icekylinx. Apache-2.0. Construction with GPT-6 Astra;
integration with OpenAI Codex. The inherited PR97 ledger is by Zhihao Chen,
and its frozen scalar/frame witness is Swapnil Jain's construction. Their
original credits, licenses and disclosures remain in the pinned snapshot.
No complete-basis replay or inherited rational-frame audit is repeated.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

from partial_gauge_bit import ROOT, require, encoded, frozen_sources

INPUT = ROOT / 'certificates/paired-cube-bit-input.json'


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
    require(len(chosen) == len(selected) == 9543 and len(skipped) == len(omitted) == 2022,
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
        selected_profile_equal=True, full_upstream_audits_repeated=False)
    result['changed_transition_histogram'] = [dict(old_rank=a,new_rank=b,count=n)
                                             for (a,b),n in sorted(changed.items())]
    result['zero_prelude_receipt'] = dict(omitted_slots=len(omitted),
        positive_support_reads=dirty_reads,odd_F2_reads=odd_dirty_reads,
        source_frame=['0'],target_frame=['0'],scalar_coefficients='exact inherited adjoint',
        placement='before every positive-rank local operation')
    result['provenance'] = dict(pr97=provenance['pr97'], underlying=provenance['underlying'])
    result['scope'] = ('Incremental selected-gauge rank and zero-prelude check; actual nested '
                       'subspaces and unchanged complete scalar word remain inherited. '
                       'Strict rational supplier moments are checked by paired_cube_network.py.')
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
