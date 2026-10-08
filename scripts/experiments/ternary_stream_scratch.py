#!/usr/bin/env python3
"""Exact small physical controls for nested-frame delivery-wire reuse."""
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
from ternary_target_circuit import DirectProducer, nonsingular, perp
from ternary_reuse_plateaus import rational_basis, audit_coefficients, audit_frames, audit_wrapper


def frame_cut(c):
    original, core = {}, {}
    descendants = {n: 0 for n in c.active}
    for output, target in c.side:
        descendants[c.outputs[output]] |= 1 << target
    for node in sorted(c.active, reverse=True):
        for parent in c.args[node] or ():
            descendants[parent] |= descendants[node]
    lines = [tuple(Fraction(int(j in t)) for j in range(c.h)) for t in c.inputs]
    for node in sorted(c.active):
        if c.args[node]:
            a, b = c.args[node]
            original[node] = rational_basis(original[a]+original[b])
            core[node] = core[a] & core[b]
        else:
            original[node] = (lines[node-1],)
            core[node] = frozenset(c.inputs[node-1])
    source = {n for n in c.active if len(core[n]) >= 2}
    dual = {}
    for node in sorted(c.active-source):
        targets = tuple(lines[j] for j in range(len(lines)) if descendants[node] >> j & 1)
        assert targets
        dual[node] = perp(rational_basis(targets), c.h)
    delayed = [n for n in dual if not nonsingular(dual[n])]
    stack = list(delayed)
    while stack:
        node = stack.pop()
        if node not in source:
            source.add(node)
            stack.extend(c.args[node] or ())
    labels = {n: original[n] if n in source else dual[n] for n in c.active}
    for n in c.active:
        assert nonsingular(labels[n])
        for a in c.args[n] or ():
            assert rational_basis(labels[a]+labels[n]) == labels[n]
    return labels, source


def candidate_links(c, source, depth, mixed=False):
    lookup = {tuple(sorted(c.args[n])): n for n in source if c.args[n]}
    edges = defaultdict(set)
    for node in sorted(c.active if mixed else source):
        if not c.args[node]:
            continue
        for side, a in enumerate(c.args[node]):
            other = c.args[node][1-side]
            stack = [(other, 0)]
            while stack:
                at, level = stack.pop()
                if level == depth:
                    continue
                for x in c.args[at] or ():
                    previous = lookup.get(tuple(sorted((a, x))))
                    if previous is not None:
                        assert c.support[previous] & c.support[node] == c.support[previous]
                        edges[previous].add(2*node+side)
                    stack.append((x, level+1))
    return {n: sorted(uses) for n, uses in edges.items()}


def matching(edges):
    """Independent augmenting-path maximum matching for small controls."""
    right = {}
    def augment(n, seen):
        for r in edges[n]:
            if r in seen:
                continue
            seen.add(r)
            if r not in right or augment(right[r], seen):
                right[r] = n
                return True
        return False
    for n in sorted(edges):
        augment(n, set())
    return {n: r for r, n in right.items()}


def compile_stream(c, labels, source, chosen):
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
    order = sorted(source, key=lambda n: (c.support[n].bit_count(), n))
    order += sorted(c.active-source)
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


def audit(h=8, depth=1, mixed=False):
    c = DirectProducer(h)
    c.verify_map()
    labels, source = frame_cut(c)
    edges = candidate_links(c, source, depth, mixed)
    chosen = matching(edges)
    code = compile_stream(c, labels, source, chosen)
    return dict(h=h, ancestor_depth=depth, source_to_dual=mixed, original_roles=c.roles,
                candidate_links=sum(map(len, edges.values())), matched_links=len(chosen),
                new_roles=code['roles'], source_nodes=len(source),
                coefficients=audit_coefficients(c, code), frames=audit_frames(c, code),
                dirty_wrapper=audit_wrapper(c, code))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, default=8)
    parser.add_argument('--depth', type=int, default=1)
    parser.add_argument('--mixed', action='store_true')
    args = parser.parse_args()
    print(json.dumps(audit(args.h, args.depth, args.mixed), indent=2, sort_keys=True))
