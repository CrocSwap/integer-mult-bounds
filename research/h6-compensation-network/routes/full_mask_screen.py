#!/usr/bin/env python3
"""Exact full-size obstruction for the explicit target-mask chain architecture."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import fiber
from artifact import write_receipt


def main():
    roots, _, shell, profiles = fiber.e.construct_shell()
    P = shell[(profiles & 4) == 0, :16].astype(np.int64)
    _, packed, _ = fiber.e.binary_labels(roots, P)
    labels, counts = np.unique(packed, return_counts=True)
    require = fiber.require
    require(len(labels) == 14670 and sum(counts) == 30960, 'complete label domain')
    parity = np.array([word.bit_count() & 1 for word in range(1<<17)], dtype=np.uint8)
    degree = []
    witnesses = []
    weighted_edge_count = 0
    for target_index, target_label in enumerate(labels):
        neighbor_indices = np.flatnonzero(parity[np.bitwise_and(labels, target_label)] == 0)
        degree.append(int(len(neighbor_indices)))
        active, selected = {}, []
        for neighbor in neighbor_indices:
            word = int(labels[neighbor])
            for pivot in sorted(active, reverse=True):
                if word>>pivot&1:word ^= active[pivot]
            if word:
                active[word.bit_length()-1] = word
                selected.append(int(neighbor))
                if len(active) == 16:break
        require(len(active) == 16, 'every target incident-label span equals its full cap')
        frame = fiber.basis(int(labels[i]) for i in selected)
        cap = fiber.perp(int(target_label))
        require(frame == cap, 'exact cap witness')
        witnesses.append(selected)
        weighted_edge_count += int(counts[target_index]) * int(counts[neighbor_indices].sum())
    helper_count = sum(int(count)*n for count,n in zip(counts,degree))
    require(weighted_edge_count == 480337920, 'independent full support agreement')
    require(helper_count > 1_000_000, 'restricted architecture exceeds H6-scale helper budget')
    result = dict(status='PASS_FULL_MASK_CHAIN_ARCHITECTURE_OBSTRUCTION',
        unique_source_and_target_labels=14670,source_ports=30960,
        full_support_edge_helpers=weighted_edge_count,
        required_distinct_ordinary_helper_lanes=helper_count,
        per_source_label_neighbor_count_histogram=dict(Counter(degree)),
        source_label_multiplicity_histogram=dict(Counter(counts.tolist())),
        every_target_mask_span_dimension=16,helper_path=[1,15,1],
        helper_rank_transition_mass=17*helper_count,
        labels=labels.tolist(),label_multiplicities=counts.tolist(),
        neighbor_label_counts=degree,cap_span_witness_label_indices=witnesses,
        source_sha256=hashlib.sha256(fiber.SOURCE.read_bytes()).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        proof='In this architecture each target mask frame contains every selected incident source label. At full size these labels span the target rank16 cap, witnessed for every distinct label. Distinct caps are distinct16-dimensional subspaces of F2^17 and therefore form an antichain. An ordinary monotone helper cannot visit two distinct caps. Every scalar source channel consequently requires a different lane for every incident target-label bucket; summing source fiber multiplicity times distinct-neighbor count gives the exact lane count.',
        limitation='The lower bound applies only to the emitted per-source, complete-target-mask chain architecture with ordinary helpers. It does not lower-bound circuits using coordinate/K mixing, sparse corrections, cross-channel cancellation, private copies, alternative flags, or other hierarchical factorizations.',
        composition_caveat='Neither these mask paths nor the small-k routes can be freely appended to the unchanged K macro; target starting frames and all center-copy descents must be priced.')
    destination=Path(__file__).with_name('FULL-MASK-SCREEN.json')
    write_receipt(destination, result, fields=['labels', 'label_multiplicities',
        'neighbor_label_counts', 'cap_span_witness_label_indices'])
    print(json.dumps({key:result[key] for key in ('status','required_distinct_ordinary_helper_lanes','helper_rank_transition_mass','per_source_label_neighbor_count_histogram')},sort_keys=True))


if __name__=='__main__':main()
