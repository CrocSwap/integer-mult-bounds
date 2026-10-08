#!/usr/bin/env python3
"""Independent exact-Q control for saturated source and dual continuations."""
from collections import defaultdict
import argparse
import json
from types import SimpleNamespace
from ternary_stream_saturated_scratch import (
    DirectProducer, frame_cut, matching, saturated_candidates, rational_basis,
    audit_coefficients, audit_frames, audit_wrapper)


def bilateral_candidates(c, labels, source, depth=4):
    edges, order = saturated_candidates(c, labels, source, depth)
    edges = {b: set(uses) for b, uses in edges.items()}
    descendants = {n: 0 for n in c.active}
    for output, target in c.side:
        descendants[c.outputs[output]] |= 1 << target
    for n in sorted(c.active, reverse=True):
        for a in c.args[n] or ():
            descendants[a] |= descendants[n]
    masks = [sum(1 << j for j in t) for t in c.inputs]
    core, union, bound, sat = {}, {}, {}, {}
    for n in c.active-source:
        family = [mask for j, mask in enumerate(masks) if descendants[n] >> j & 1]
        core[n], union[n] = (1 << c.h)-1, 0
        for mask in family:
            core[n] &= mask
            union[n] |= mask
        bound[n] = (union[n].bit_count()-core[n].bit_count()) or 1
        sat[n] = c.h-len(labels[n]) == bound[n]
    key = lambda n: (-bound[n], -sat[n], -descendants[n].bit_count(), n)
    consumers = defaultdict(list)
    for n in sorted(c.active-source):
        for side, a in enumerate(c.args[n] or ()):
            consumers[a].append(2*n+side)
    for uses in consumers.values():
        for before in uses:
            b = before//2
            if not sat[b]:
                continue
            for delivery in uses:
                target = delivery//2
                if (key(b) < key(target) and not union[target] & ~union[b]
                        and not core[b] & ~core[target]):
                    edges.setdefault(b, set()).add(delivery)
    for b, uses in edges.items():
        for r in uses:
            assert rational_basis(labels[b]+labels[r//2]) == labels[r//2]
    return ({b: sorted(uses) for b, uses in edges.items()},
            [n for n in order if n in source]+sorted(c.active-source, key=key))


def compile_saturated_stream(c, labels, source, chosen, order):
    outgoing = defaultdict(list)
    for node in c.active:
        for side, parent in enumerate(c.args[node] or ()):
            outgoing[parent].append(('gate', 2*node+side))
    for output, node in c.outputs.items():
        outgoing[node].append(('output', output))
    continuation, predecessor = {}, {}
    for node, following in chosen.items():
        target, side = divmod(following, 2)
        value = c.args[target][side]
        previous = 2*node+c.args[node].index(value)
        assert previous not in continuation and following not in predecessor
        assert node in source or target not in source
        assert rational_basis(labels[node]+labels[target]) == labels[target]
        continuation[previous] = following
        predecessor[following] = previous
    deliveries, sources, outputs = {}, {}, {}
    gates, frames = [], []
    for node in order:
        if c.args[node]:
            ins = [deliveries[2*node+side] for side in (0, 1)]
            assert len(set(ins)) == 2
            final = [side for side in (0, 1) if 2*node+side not in continuation]
            assert final
            pivot = final[0]
            reuse = ins[pivot]
        else:
            reuse = len(frames)
            frames.append(())
            ins, pivot = [reuse], 0
            sources[c.inputs[node-1]] = reuse
        starts = sorted(use for use in outgoing[node]
                        if use[0] == 'output' or use[1] not in predecessor)
        assert starts
        outs = [reuse]
        for _ in starts[1:]:
            outs.append(len(frames))
            frames.append(())
        for slot, (kind, target) in zip(outs, starts):
            if kind == 'output':
                outputs[target] = slot
            else:
                while True:
                    assert target not in deliveries
                    deliveries[target] = slot
                    if target not in continuation:
                        break
                    target = continuation[target]
        for slot in set(ins+outs):
            assert rational_basis(frames[slot]+labels[node]) == labels[node]
            frames[slot] = labels[node]
        block = dict(group=node, nodes=[node], label=labels[node],
                     matrix=[[1]*len(ins) for _ in outs],
                     independent=[0], pivots=[pivot], inverse=[[1]],
                     coefficients=[[1] for _ in outs])
        gates.append(dict(block=block, ins=ins, outs=outs, fresh=outs[1:]))
    assert len(frames) == c.roles-len(chosen)
    return dict(roles=len(frames), sources=sources, outputs=outputs, gates=gates)


def audit(h=10, depth=4):
    c = DirectProducer(h)
    c.verify_map()
    labels, source = frame_cut(c)
    edges, order = bilateral_candidates(c, labels, source, depth)
    chosen = matching(edges)
    code = compile_saturated_stream(c, labels, source, chosen, order)
    return dict(h=h, original_roles=c.roles, new_roles=code['roles'],
                candidate_links=sum(map(len, edges.values())), matched_links=len(chosen),
                dual_frame_links=sum(n not in source for n in chosen),
                coefficients=audit_coefficients(c, code), frames=audit_frames(c, code),
                dirty_wrapper=audit_wrapper(c, code))


def strict_dual_control():
    """Actual source/dual cut with a strict dual-frame continuation."""
    inputs = [(0, 1, 7, 8, 9), (1, 2, 10, 11, 12), (0, 2, 13, 14, 15)]
    inputs += [(0, 1, 2)+pair for pair in ((3, 4), (3, 5), (4, 5), (5, 6), (3, 6))]
    c = SimpleNamespace(
        h=28, inputs=inputs, variables={t: i+1 for i, t in enumerate(inputs)},
        args=[None]*9+[(1, 2), (1, 3)],
        support=[0]+[1 << i for i in range(8)]+[3, 5],
        active={1, 2, 3, 9, 10}, outputs={0: 9, 1: 9, 2: 9, 3: 9, 4: 10},
        side=[(i, 3+i) for i in range(5)], totals=[], roles=7)
    labels, source = frame_cut(c)
    edges, order = bilateral_candidates(c, labels, source, 4)
    chosen = matching(edges)
    code = compile_saturated_stream(c, labels, source, chosen, order)
    assert source == {1, 2, 3} and edges == {9: [20]}
    assert (len(labels[9]), len(labels[10])) == (24, 27)
    assert code['roles'] == 6
    return dict(h=28, original_roles=c.roles, new_roles=code['roles'],
                source_nodes=sorted(source), dual_nodes=sorted(c.active-source),
                dual_frame_dimensions=[len(labels[9]), len(labels[10])],
                candidate_links=sum(map(len, edges.values())), matched_links=len(chosen),
                dual_frame_links=sum(n not in source for n in chosen),
                coefficients=audit_coefficients(c, code), frames=audit_frames(c, code),
                dirty_wrapper=audit_wrapper(c, code, require_identity=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, default=10)
    parser.add_argument('--depth', type=int, default=4)
    args = parser.parse_args()
    print(json.dumps(audit(args.h, args.depth), indent=2, sort_keys=True))
