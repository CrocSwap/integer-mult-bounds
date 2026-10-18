#!/usr/bin/env python3
"""Finite-state optimization of all monotone frames on a fixed scalar word.

The solver nominates assignments, not proofs of admission. Every subspace in
the dependency interval is enumerated; scalar operations, entrance frames,
center cuts and output caps remain fixed. Prepared with OpenAI Codex
(GPT-6 Astra) assistance. Apache-2.0. Uses the credited Chains implementation
retained by PR569, descended from icekylinx's frame coalescing work.
"""
import argparse
from collections import Counter
import copy
from functools import lru_cache
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'research/larger-gain/providers'))
from coupled_frames_base import Chains, basis, contained, join, span


@lru_cache(None)
def interval(lower, upper):
    if not contained(lower, upper):
        raise ValueError('Empty frame interval')
    found, pending = {lower}, [lower]
    while pending:
        frame = pending.pop()
        for vector in span(upper) - span(frame):
            next_frame = join(frame, (vector,))
            if next_frame not in found:
                found.add(next_frame)
                pending.append(next_frame)
    return tuple(sorted(found, key=lambda f: (len(f), f)))


def frame_graph(word, unlock_entrances=False):
    graph = Chains(word)
    if unlock_entrances:
        for register in map(int, word.get('start_extra', {})):
            start = graph.regs[register][0]
            graph.upper[start] = graph.upper[graph.next[start, register]]
            graph.locked.remove(start)
    frames = [interval(graph.lower[k], graph.upper[k]) for k in range(len(graph.nodes))]
    edges = Counter((left, right) for chain in graph.regs for left, right in zip(chain, chain[1:]))
    return graph, frames, edges


def model(word, rate, unlock_entrances=False):
    import numpy as np
    from scipy.sparse import coo_matrix
    graph, frames, edges = frame_graph(word, unlock_entrances)
    costs = [0.0 if not r else r * math.expm1(rate * math.log(73 / r)) / rate for r in range(10)]
    objective, rr, cc, vv, rhs = [], [], [], [], []
    node_vars, edge_vars, marginal_rows = [], [], []

    def row(terms, target):
        i = len(rhs)
        for column, coefficient in terms:
            rr.append(i); cc.append(column); vv.append(coefficient)
        rhs.append(target)
        return i

    for states in frames:
        indices = list(range(len(objective), len(objective) + len(states)))
        node_vars.append(indices)
        objective.extend([0.0] * len(states))
        row([(i, 1) for i in indices], 1)
    for (left, right), multiplicity in sorted(edges.items()):
        pairs = {}
        for a, f in enumerate(frames[left]):
            for b, g in enumerate(frames[right]):
                if contained(f, g):
                    pairs[a, b] = len(objective)
                    objective.append(multiplicity * costs[len(g) - len(f)])
        if not pairs:
            raise ValueError('No compatible edge states')
        left_rows, right_rows = [], []
        for a, variable in enumerate(node_vars[left]):
            left_rows.append(row([(variable, -1)] + [(v, 1) for (i, _), v in pairs.items() if i == a], 0))
        for b, variable in enumerate(node_vars[right]):
            right_rows.append(row([(variable, -1)] + [(v, 1) for (_, j), v in pairs.items() if j == b], 0))
        edge_vars.append((left, right, multiplicity, pairs))
        marginal_rows.append((left_rows, right_rows))
    matrix = coo_matrix((vv, (rr, cc)), shape=(len(rhs), len(objective))).tocsc()
    return graph, frames, node_vars, edge_vars, marginal_rows, np.array(objective), matrix, np.array(rhs)


def main():
    import numpy as np
    import scipy
    from scipy.optimize import linprog, milp, Bounds, LinearConstraint
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--rate', type=float, default=.0016026318137744147)
    parser.add_argument('--integer', action='store_true')
    parser.add_argument('--seconds', type=int, default=120)
    args = parser.parse_args()
    if args.out.exists():
        raise ValueError('Use a fresh output directory')
    args.out.mkdir(parents=True)
    raw = args.word.read_bytes()
    word = json.loads(gzip.decompress(raw))
    graph, frames, nv, ev, mr, c, matrix, rhs = model(word, args.rate)
    original = graph.profile()
    print(json.dumps(dict(nodes=len(frames), variables=len(c), constraints=len(rhs),
                          variable_nodes=sum(len(s) > 1 for s in frames),
                          maximum_states=max(map(len, frames)))), flush=True)
    lp = linprog(c, A_eq=matrix, b_eq=rhs, bounds=(0, None), method='highs')
    if not lp.success:
        raise ValueError(lp.message)
    answer = lp
    if args.integer:
        integrality = np.zeros(len(c))
        for choices in nv:
            integrality[choices] = 1
        answer = milp(c, integrality=integrality, bounds=Bounds(0, np.inf),
                      constraints=LinearConstraint(matrix, rhs, rhs),
                      options=dict(time_limit=args.seconds, mip_rel_gap=1e-10))
        if answer.x is None:
            raise ValueError(answer.message)
    selected = [int(np.argmax(answer.x[choices])) for choices in nv]
    fractional = sum(int(abs(answer.x[v] - round(answer.x[v])) > 1e-7) for choices in nv for v in choices)
    cost = lambda p: sum(n * (r * math.expm1(args.rate * math.log(73 / r)) / args.rate) for r,n in p.items())
    center_cost = cost(graph.center_profile)
    record = dict(status='NUMERICAL_RELAXATION_ONLY' if fractional else 'FRAME_ASSIGNMENT_REQUIRES_NATIVE_REPLAY',
                  word_path=str(args.word.resolve()), word_sha256=hashlib.sha256(raw).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  rate=args.rate, solver_version=scipy.__version__, nodes=len(frames),
                  variables=len(c), constraints=len(rhs), fractional_node_states=fractional,
                  original_cost=cost(original), relaxed_cost=lp.fun + center_cost,
                  incumbent_cost=answer.fun + center_cost, profile_before=dict(sorted(original.items())),
                  scope='All monotone frame states between exact fixed-boundary dependency bounds. '
                        'Scalar word, entrances, cuts and output caps fixed. Floating solver values '
                        'are nominations only; this is not an exact upper bound or global admission.')
    if not fractional:
        candidate = copy.deepcopy(word)
        trace = []
        for k, (node, state) in enumerate(zip(graph.nodes, selected)):
            frame = frames[k][state]
            if frame != node['F']:
                if k in graph.locked:
                    raise ValueError('Locked frame changed')
                trace.append(dict(section=node['section'], index=node['index'], old=node['F'], new=frame))
                candidate[node['section']][node['index']][-1] = list(frame)
                node['F'] = frame
        new_profile = graph.profile()
        if sum(r*n for r,n in original.items()) != sum(r*n for r,n in new_profile.items()):
            raise ValueError('Rank mass changed')
        for section in ('A','B'):
            if [e[:-1] for e in word[section]] != [e[:-1] for e in candidate[section]]:
                raise ValueError('Scalar operation changed')
        candidate['report']['local_profile'] = dict(sorted(new_profile.items()))
        record.update(profile_after=dict(sorted(new_profile.items())), trace=trace,
                      changed_gates=len(trace), assigned_cost=cost(new_profile))
        payload = gzip.compress(json.dumps(candidate,sort_keys=True,separators=(',',':')).encode(),mtime=0)
        (args.out/'FULL-WORD.json.gz').write_bytes(payload)
        record['output_sha256'] = hashlib.sha256(payload).hexdigest()
    messages = [[list(map(float, lp.eqlin.marginals[left])), list(map(float, lp.eqlin.marginals[right]))]
                for left,right in mr]
    (args.out/'DUAL-MESSAGES.json.gz').write_bytes(gzip.compress(json.dumps(messages,separators=(',',':')).encode(),mtime=0))
    (args.out/'RESULT.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k != 'trace'}),flush=True)


if __name__ == '__main__':
    main()
