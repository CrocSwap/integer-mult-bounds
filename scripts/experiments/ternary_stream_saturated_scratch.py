#!/usr/bin/env python3
"""Independent exact-Q controls for saturated-source delivery continuations."""
from collections import defaultdict
import argparse
import json
from ternary_stream_scratch import (
    DirectProducer, frame_cut, candidate_links, matching, rational_basis,
    audit_coefficients, audit_frames, audit_wrapper)


def saturated_candidates(c, labels, source, depth=4):
    core, union = {}, {}
    for n in sorted(c.active):
        if c.args[n]:
            a, b = c.args[n]
            core[n] = core[a] & core[b]
            union[n] = union[a] | union[b]
        else:
            core[n] = union[n] = sum(1 << j for j in c.inputs[n-1])
    bound = {n: (union[n].bit_count()-core[n].bit_count()) or 1 for n in source}
    saturated = {n: len(labels[n]) == bound[n] for n in source}
    key = lambda n: (bound[n], saturated[n], c.support[n].bit_count(), n)
    order = sorted(source, key=key)+sorted(c.active-source)
    edges = candidate_links(c, source, depth, mixed=True)
    edges = {b: set(r for r in uses if r//2 not in source or key(b) < key(r//2))
             for b, uses in edges.items()}
    consumers = defaultdict(list)
    for n in sorted(source):
        for side, a in enumerate(c.args[n] or ()):
            consumers[a].append(2*n+side)
    for uses in consumers.values():
        for r in uses:
            target = r//2
            if not saturated[target] or not core[target]:
                continue
            for other in uses:
                previous = other//2
                if (key(previous) < key(target) and not union[previous] & ~union[target]
                        and not core[target] & ~core[previous]):
                    edges.setdefault(previous, set()).add(r)
    for b, uses in edges.items():
        for r in uses:
            assert rational_basis(labels[b]+labels[r//2]) == labels[r//2]
    return {b: sorted(uses) for b, uses in edges.items() if uses}, order


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
        assert node in source
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


def audit(h=8, depth=4):
    c = DirectProducer(h)
    c.verify_map()
    labels, source = frame_cut(c)
    edges, order = saturated_candidates(c, labels, source, depth)
    chosen = matching(edges)
    code = compile_saturated_stream(c, labels, source, chosen, order)
    return dict(h=h, original_roles=c.roles, new_roles=code['roles'],
                candidate_links=sum(map(len, edges.values())), matched_links=len(chosen),
                coefficients=audit_coefficients(c, code), frames=audit_frames(c, code),
                dirty_wrapper=audit_wrapper(c, code))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, default=8)
    parser.add_argument('--depth', type=int, default=4)
    args = parser.parse_args()
    print(json.dumps(audit(args.h, args.depth), indent=2, sort_keys=True))
