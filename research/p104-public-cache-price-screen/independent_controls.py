#!/usr/bin/env python3
"""Small exact direct-span controls for the paired image/kernel invariant."""
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent


def need(value, label):
    if not value:
        raise ValueError(label)


def dense_rank(rows, columns=4):
    matrix = [[Q(row.get(j, 0)) for j in range(columns)] for row in rows]
    rank = 0
    for column in range(columns):
        pivot = next((r for r in range(rank, len(matrix)) if matrix[r][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        divisor = matrix[rank][column]
        matrix[rank] = [v/divisor for v in matrix[rank]]
        for r in range(len(matrix)):
            if r != rank:
                factor = matrix[r][column]
                matrix[r] = [x-factor*y for x,y in zip(matrix[r],matrix[rank])]
        rank += 1
    return rank


def in_span(target, rows):
    return dense_rank(rows+[target]) == dense_rank(rows)


def reject(value, label):
    need(not value, 'negative control: '+label)
    return label


def main():
    path = HERE/'verifier/paired_prices.py'
    spec = importlib.util.spec_from_file_location('reviewed_paired_module',path)
    paired = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(paired)
    mains, helpers = {0,3}, {1,2}
    tariffs = {1:1,2:8}
    observations = [{0:Q(1),2:Q(1)}, {1:Q(1)}]
    state = paired.make_state()
    for row in observations:
        paired.insert_observation(state,row,mains,helpers)
    target = {0:Q(1),2:Q(2)}
    projected, g = paired.target_residual(state,target,mains,helpers)
    need(not projected and g == {2:Q(1)}, 'fresh direction has no cheap coordinate')
    need(state['kernel_support'] == {1}, 'cheap coordinate occurs only in prior kernel')
    support = state['kernel_support'] | set(g)
    need(min(tariffs[j] for j in support) == 1, 'whole E support gives the attainable cheap debit')
    relation = {1:Q(1),2:Q(1)}
    need(in_span(target,observations+[relation]), 'independent dense span verifies enabling relation')
    reject(in_span(relation,observations), 'enabling relation cannot already lie in P')
    need(dense_rank(observations) == len(state['image'])+len(state['kernel']) == 2,
         'image plus kernel dimensions equal independent full rank')
    controls = []
    controls.append(reject(min(tariffs[j] for j in g) == 1,
                           'discarding K misses the cheapest attainable coordinate'))
    controls.append(reject(in_span(target,observations+[{1:Q(1)}]),
                           'a cheap relation in K alone does not enable the target'))
    controls.append(reject(in_span(target,observations), 'target is outside strict history'))
    later = paired.make_state()
    for row in observations+[target]:
        paired.insert_observation(later,row,mains,helpers)
    main_residual, residual = paired.target_residual(later,target,mains,helpers)
    need(not main_residual and not paired.reduce_row(residual,later['kernel']),
         'self arrival creates an apparent hit and therefore must be excluded')
    controls.append('self-arrival history poisoning detected')
    outside = {3:Q(1),2:Q(1)}
    projected, _ = paired.target_residual(state,outside,mains,helpers)
    need(projected == {3:Q(1)}, 'independent main direction remains missing')
    controls.append(reject(in_span(outside,observations+[{1:Q(1)},{2:Q(1)}]),
                           'even all helper relations cannot repair a main miss'))
    paired.insert_observation(state,{0:Q(2),2:Q(2)},mains,helpers)
    paired.insert_observation(state,{1:Q(-3)},mains,helpers)
    need(len(state['image'])+len(state['kernel']) == 2 and state['kernel_support'] == {1},
         'dependent observation insertion leaves the represented subspaces unchanged')
    print(json.dumps({'status':'PASS_INDEPENDENT_DENSE_SPAN_PRICE_CONTROLS',
                      'method':'Separate exact dense elimination versus paired sparse state',
                      'executed_failure_controls':controls,
                      'positive_checks':['cheapest coordinate only in K','explicit g+k enabling relation',
                                         'image/kernel rank','self arrival recognition','dependent repeats'],
                      'scope':'Synthetic invariant controls; not additional source-census coverage or a universal theorem by finite examples.'},
                     indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
