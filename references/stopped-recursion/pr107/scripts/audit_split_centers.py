#!/usr/bin/env python3
"""Point-split central gates: a small local saving, not a new kappa.

All old invocation boundaries and side frames are retained. The tested frame
family replaces selected first-gather frames by incident-triple hyperplanes
and selected second-scatter frames by their orthogonal complements.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
import json

from audit_joint_frames import (eye, zero, sub, span_projection, paired_invocation,
                                score_graph, rank, product, matrix)
from audit_cancellation import line_projection
from certify import require, verify_sources
from paired_network import circuit
from prepare_layers import serializable

ROOT = Path(__file__).resolve().parents[1]


def normal(h,i):
    require(h >= 6 and h != 9 and 0 <= i < h, 'Invalid incident hyperplane')
    return tuple(h-7 if j == i else 2 for j in range(h))


def complement(h,i):
    return span_projection([normal(h,i)],h)


def split_graph(h=6,A=(0,),C=(1,)):
    """Rebuild every physical edge and scalar operation, including side roles."""
    A,C = set(A),set(C)
    require(A <= set(range(h)) and C <= set(range(h)), 'Invalid point selection')
    old = paired_invocation(h)
    code = circuit(h).compile()
    triples = list(combinations(range(h),3))
    v,R = len(triples),code['roles']
    I,Z = eye(h),zero(h)
    Qs = {i:complement(h,i) for i in A|C}
    groups = ['X']*v+['Y']*v+['side']*R+['center']*h
    frames = {('in',i):old['frames']['in',i] for i in range(len(groups))}
    last = [('in',i) for i in range(len(groups))]
    edges,operations = [],[]

    def gate(name,roles,M,ops):
        frames[name] = M
        for r in sorted(set(roles)):
            edges.append((last[r],name,groups[r]))
            last[r] = name
        operations.extend(ops)

    sources = {t:[] for t in triples}
    outputs = {t:[] for t in triples}
    for t,s in code['sources'].items():
        sources[t].append(2*v+s)
    for (_,t),s in code['outputs'].items():
        outputs[t].append(2*v+s)
    for step,op in enumerate(('L','J','Li','R','V','G','R','L','J','Li','G','V')):
        if op in ('L','Li'):
            gates = code['gates'] if op == 'L' else reversed(code['gates'])
            for node,ins,outs in gates:
                ops = [(2*v+ins[0],2*v+s) for s in ins[1:]]
                ops += [(2*v+s,2*v+ins[0]) for s in outs[1:]]
                if op == 'Li':
                    ops.reverse()
                gate((step,node),[2*v+s for s in set(ins+outs)],old['frames'][step,node],ops)
        elif op in ('V','J'):
            for j,t in enumerate(triples):
                ops = [(s,j) for s in sources[t]] if op == 'V' else [(v+j,s) for s in outputs[t]]
                roles = [j]+sources[t] if op == 'V' else [v+j]+outputs[t]
                gate((step,j),roles,old['frames'][step,j],ops)
        else:
            # First gather visits selected points first; second scatter visits
            # selected points last. Other sweeps retain their original frames.
            points = sorted(range(h),key=lambda i:(i not in A,i)) if step == 5 else (
                sorted(range(h),key=lambda i:(i in C,i)) if step == 6 else range(h))
            for i in points:
                z = 2*v+R+i
                data = [j for j,t in enumerate(triples) if i in t]
                M = I if op == 'G' else Z
                if step == 5 and i in A:
                    M = sub(I,Qs[i])
                if step == 6 and i in C:
                    M = Qs[i]
                ops = [(z,j) for j in data] if op == 'G' else [(v+j,z) for j in data]
                roles = [z]+[j if op == 'G' else v+j for j in data]
                gate((step,'point',i),roles,M,ops)
    for r in range(len(groups)):
        name = ('out',r)
        frames[name] = old['frames'][name]
        edges.append((last[r],name,groups[r]))
    return dict(h=h,v=v,R=R,frames=frames,edges=edges,operations=operations)


def scalar_check(graph):
    n = 2*graph['v']+graph['R']+graph['h']
    original = [1 << i for i in range(n)]
    expected = list(original)
    for i in range(graph['v']):
        expected[graph['v']+i] ^= original[i]
    for backward in (False,True):
        values = list(original)
        ops = reversed(graph['operations']) if backward else graph['operations']
        for target,source in ops:
            values[target] ^= values[source]
        require(values == expected, 'Wrong shear or dirty-scratch restoration')
    return dict(independent_variables=n,forward_and_inverse_exact=True,
                arbitrary_side_and_center_inputs_restored=True)


def excess(h,s,t,u):
    """Exact best-order rank change within the specified hyperplane family."""
    require(h >= 6 and h != 9 and 0 <= s <= h and 0 <= t <= h,
            'Invalid dimensions')
    require(max(0,s+t-h) <= u <= min(s,t), 'Impossible intersection size')
    v,q = comb(h,3),comb(h-1,2)
    def F(k):
        return k*q-v+comb(h-k,3)
    return dict(X=2*F(s),Y=2*F(t),center=-2*(s+t-u),
                total=2*(F(s)+F(t)-s-t+u))


def exact_path_score(h,A,C):
    """Independent rational ranks on full reduced data and central paths."""
    A,C = set(A),set(C)
    I,Z = eye(h),zero(h)
    Qs = {i:complement(h,i) for i in A|C}
    ag = sorted(range(h),key=lambda i:(i not in A,i))
    cs = sorted(range(h),key=lambda i:(i in C,i))
    cost = dict(X=0,Y=0,center=0)
    for T in combinations(range(h),3):
        P = matrix(line_projection(h,T))
        paths = dict(X=[P]+[sub(I,Qs[i]) if i in A else I for i in ag if i in T]+[I],
                     Y=[Z]+[Qs[i] if i in C else Z for i in cs if i in T]+[sub(I,P)])
        for kind,path in paths.items():
            cost[kind] += sum(rank(sub(b,a)) for a,b in zip(path,path[1:]))
    for i in range(h):
        path = [Z,sub(I,Qs[i]) if i in A else I,Qs[i] if i in C else Z,I]
        cost['center'] += sum(rank(sub(b,a)) for a,b in zip(path,path[1:]))
    return cost


def certificate():
    controls = []
    for A,C in (((),()),((0,),()),((),(1,)),((0,),(1,)),
                ((0,),(0,)),((0,1),(2,)),(tuple(range(6)),tuple(range(6)))):
        g = split_graph(6,A,C)
        score = score_graph(g)
        base = score_graph(paired_invocation(6))
        change = excess(6,len(A),len(C),len(set(A)&set(C)))
        require(all(score[k]-base[k] == change[k] for k in ('X','Y','center')),
                'Full physical edge score disagrees with formula')
        require(score['side'] == base['side'], 'Side wires changed')
        paths = exact_path_score(6,A,C)
        require(all(paths[k] == score[k] for k in paths), 'Path/full graph mismatch')
        controls.append(dict(A=A,C=C,score=score,change=change,scalar=scalar_check(g)))
    h10 = []
    for A,C in (((0,),(1,)),((0,1),(2,3)),((0,1),(1,2))):
        scores = exact_path_score(10,A,C)
        baseline = dict(X=comb(10,3)*9,Y=comb(10,3)*9,center=300)
        change = excess(10,len(A),len(C),len(set(A)&set(C)))
        require(all(scores[k]-baseline[k] == change[k] for k in scores),
                'Indefinite-form path control failed')
        h10.append(dict(A=A,C=C,score=scores,change=change))
    h = 50
    # Enumerate the complete cardinality parameter family, with the best
    # possible intersection. The accompanying proof covers every h>=6,h!=9.
    best = min((excess(h,s,t,max(0,s+t-h))['total'],s,t)
               for s in range(h+1) for t in range(h+1))
    require(best == (-4,1,1), 'Point-split optimum changed')
    v = comb(h,3)
    proofs = ['docs/research/early-sharing-and-centers.md','scripts/audit_split_centers.py']
    return dict(status='POINT-SPLIT LOCAL RANK SAVING; NO NEW KAPPA',
                upstream_commit=verify_sources(),physical_controls=controls,
                indefinite_rational_controls=h10,best_h50=dict(rank_change=best[0],
                    selected_gather_points=best[1],selected_scatter_points=best[2],
                    decreasing_loss_before=h*h,decreasing_loss_after=h*h-2),
                hypothetical_global_deficit_multiplier=Q(v-6*h*h+12,v-6*h*h),
                global_tensor_integration_supplied=False,
                source_sha256={p:sha256((ROOT/p).read_bytes()).hexdigest() for p in proofs},
                scope='Exact local active-factor paths and scalar restoration. Family optimum only for the specified hyperplane labels, fixed boundaries, D=0 and B=I; not a lower bound on other point-split matrices or schedules.')


if __name__ == '__main__':
    result = certificate()
    (ROOT/'certificates/split-centers-audit.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS split-center local improvement: rank -4, loss 2500 -> 2498; no new kappa.')
