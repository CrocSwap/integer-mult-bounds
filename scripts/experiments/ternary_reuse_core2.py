#!/usr/bin/env python3
"""Full h28 count for unique-common-pair plateau fusion in the PR7 producer.

Uses exact modular row spaces with a deterministic determinant bound, not
probabilistic fingerprints. Imports the frozen PR7 PairedTriple producer.
"""
from collections import defaultdict
from math import comb
from pathlib import Path
import argparse
import json
import sys
from hashlib import sha256

ROOT = Path(__file__).resolve().parents[2]
PRIME = (1 << 61)-1


def span_mod(rows, dimension):
    basis = {}
    for original in rows:
        row = list(original)
        for pivot in sorted(basis):
            factor = row[pivot]
            if factor:
                leading = basis[pivot]
                row = [(x-factor*y) % PRIME for x, y in zip(row, leading)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is None:
            continue
        factor = pow(row[pivot], -1, PRIME)
        row = [(x*factor) % PRIME for x in row]
        for old in basis:
            factor = basis[old][pivot]
            if factor:
                basis[old] = [(x-factor*y) % PRIME for x, y in zip(basis[old], row)]
        basis[pivot] = row
        if len(basis) == dimension:
            break
    return tuple(tuple(basis[pivot]) for pivot in sorted(basis))


def add3(a, b):
    a1, a2 = a
    b1, b2 = b
    aa, bb = a1 | a2, b1 | b2
    return ((b1 & ~aa) | (a1 & ~bb) | (a2 & b2),
            (b2 & ~aa) | (a2 & ~bb) | (a1 & b1))


def rank3(masks):
    pivots = {}
    for mask in masks:
        row = (mask, 0)
        while row[0] | row[1]:
            pivot = (row[0] | row[1]).bit_length()-1
            leading = 1 if row[0] >> pivot & 1 else 2
            if pivot not in pivots:
                pivots[pivot] = row if leading == 1 else (row[1], row[0])
                break
            other = pivots[pivot]
            row = add3(row, (other[1], other[0]) if leading == 1 else other)
    return len(pivots)


def local_count(n, producer):
    c = producer(n)
    coefficient_check = c.verify()
    total = c.triple(list(range(n)), c.variables)[()]
    assert c.support[total] == (1 << len(c.inputs))-1
    stack = [total]
    while stack:
        node = stack.pop()
        if node in c.active:
            continue
        c.active.add(node)
        stack.extend(c.args[node] or ())
    outputs = list(c.outputs.items())+[((), total)]
    cores = {}
    for node in sorted(c.active):
        if c.args[node]:
            a, b = c.args[node]
            assert not c.support[a] & c.support[b]
            assert c.support[node] == c.support[a] | c.support[b]
            cores[node] = cores[a] & cores[b]
        else:
            cores[node] = sum(1 << i for i in c.inputs[node-1])
    eligible = {node for node in c.active if cores[node] == 0}
    required = {node: [] for node in eligible}
    for excluded, node in outputs:
        if node in eligible and excluded:
            required[node].append(tuple(int(i in excluded) for i in range(n)))
    # All requirement rows are actual triple indicators. Every square minor
    # has |det|<=3^(n/2). RREF numerators and denominators obey that bound.
    # p>2B^2 proves both exact rational rank and collision-free equality.
    bound = 3 ** ((n+1)//2)
    assert PRIME > 2*bound*bound
    for node in sorted(eligible, reverse=True):
        required[node] = span_mod(required[node], n)
        for parent in c.args[node] or ():
            if parent in eligible:
                required[parent].extend(required[node])
    buckets = defaultdict(list)
    for node in sorted(c.active):
        key = ('enlarged', required[node]) if node in eligible else ('fixed', node)
        buckets[key].append(node)
    groups = {nodes[0]: nodes for nodes in buckets.values()}
    home = {node: group for group, nodes in groups.items() for node in nodes}
    incoming = {group: set() for group in groups}
    outgoing = {group: set() for group in groups}
    old_port_count = 0
    for node in c.active:
        for parent in c.args[node] or ():
            old_port_count += 1
            if home[parent] != home[node]:
                incoming[home[node]].add(parent)
                outgoing[home[parent]].add((parent, ('gate', home[node])))
    for i, (_, node) in enumerate(outputs):
        old_port_count += 1
        outgoing[home[node]].add((node, ('output', i)))
    original_roles = old_port_count-len(c.active)+len(c.inputs)
    additions = sum(c.args[node] is not None for node in c.active)
    assert original_roles == additions+len(outputs)
    new_roles = len(c.inputs)
    digest = sha256()
    combined = []
    for group, nodes in groups.items():
        ports = sorted(outgoing[group])
        if len(nodes) == 1:
            rank = 1
        else:
            inputs = sorted(incoming[group])
            local = {node: 1 << j for j, node in enumerate(inputs)}
            for node in nodes:
                a, b = c.args[node]
                assert not local[a] & local[b], 'A boundary input is counted twice'
                local[node] = local[a] | local[b]
            rank = rank3([local[node] for node, _ in ports])
            combined.append(dict(nodes=len(nodes), inputs=len(inputs), outputs=len(ports), rank=rank))
        new_roles += len(ports)-rank
        digest.update(json.dumps((nodes, sorted(incoming[group]), ports, rank),
                                 separators=(',', ':')).encode()+b'\n')
    return dict(local_ground_size=n, global_h=n+2,
                local_inputs=len(c.inputs), retained_additions=additions,
                output_uses=len(outputs), eligible_common_pair_nodes=len(eligible),
                enlarged_span_classes=len({required[node] for node in eligible}),
                merged_classes=len(combined), largest_merged_class=max((row['nodes'] for row in combined), default=1),
                original_local_roles=original_roles, new_local_roles=new_roles,
                saved_roles_per_common_pair=original_roles-new_roles,
                boundary_plan_sha256=digest.hexdigest(),
                deterministic_exactness=dict(prime=PRIME, minor_bound=bound,
                    prime_exceeds_twice_minor_bound_squared=True,
                    rational_row_space_equality_exact=True, boundary_ranks_over='F3'),
                all_original_coefficients_verified=coefficient_check['all_disjoint_output_coefficients_exact'],
                retained_total_exact=True)


def certificate(producer=None):
    sys.path.insert(0, str(ROOT/'scripts'))
    if producer is None:
        from paired_triple_circuit import PairedTriple
        producer = PairedTriple
    result = local_count(26, producer)
    assert result['retained_additions'] == 41439
    assert result['original_local_roles'] == 44040
    assert result['saved_roles_per_common_pair'] == 174
    old = 11840940
    saved = comb(28, 2)*result['saved_roles_per_common_pair']
    from experiments.ternary_reuse_plateaus import local_context_control
    control = local_context_control(10, producer)
    assert control['saved_roles'] == 9
    assert not control['dirty_wrapper']['intended_map_is_identity']
    result['positive_small_context'] = control
    result['status'] = 'CONDITIONAL COMPILER REFINEMENT; ASSEMBLY CERTIFIED SEPARATELY'
    result['pr7_commit'] = '6725c6a17b17871a35353fd29157f4ed851bc114'
    result['global_h28'] = dict(pr7_roles=old, common_pair_contexts=comb(28, 2),
                               saved_roles=saved, new_role_upper_bound=old-saved,
                               center_loss_unchanged=comb(28, 2)*26)
    result['scope'] = ('Only unique-common-pair nodes are replaced. Existing four-star '
                       'resynthesis, source/support coefficients, designated outputs, '
                       'central losses, tensor stages and endpoint frames are retained. '
                       'Exact checks supplement the written general compiler proof.')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pr7-scripts', type=Path, default=ROOT/'scripts')
    parser.add_argument('--n', type=int, default=26)
    parser.add_argument('--output', type=Path, default=ROOT/'certificates/ternary-reuse-core2.json')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT/'scripts'))
    sys.path.insert(0, str(args.pr7_scripts))
    from paired_triple_circuit import PairedTriple
    result = certificate(PairedTriple) if args.n == 26 else local_count(args.n, PairedTriple)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, indent=2, sort_keys=True))
