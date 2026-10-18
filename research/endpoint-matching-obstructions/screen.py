"""Exact hypotheses for the rank-homogeneous path obstruction.

The theorem is in PROOF.md. A failed hypothesis means unknown, never feasible.
Apache-2.0; substantial OpenAI Codex assistance; see NOTICE.md.
"""
from collections import defaultdict
from itertools import product
from model import Engine, FREE, fourier_rank


def layers(program):
    stages=[[[] for _ in range(3)]]
    for gate in program:
        if gate[0]=='mix3':
            stages.append([[] for _ in range(3)])
        else:
            stages[-1][gate[1]].append(('C',gate[2],0) if gate[0]=='paid' else FREE[gate[2]])
    if len(stages)<2:
        raise ValueError('at least one scalar block is required')
    return stages


def group(ring,operations):
    g=0
    for op in operations:g=ring.transitions(op,g)
    return g


def certificate(program):
    stages=layers(program);ring=Engine()
    ranks=[[fourier_rank(ring.groups[group(ring,u)]) for u in stage] for stage in stages]
    classes=defaultdict(list)
    for path in product(range(3),repeat=len(stages)-2):
        operations=[op for k,r in enumerate(path,1) for op in stages[k][r]]
        tableau=ring.groups[group(ring,operations)]
        cost=sum(ranks[k][r] for k,r in enumerate(path,1))
        classes[tableau].append((path,cost))
    classes=sorted((sorted((list(p),c) for p,c in values) for values in classes.values()),key=lambda x:x[0][0])
    mixed=sum(len({c for p,c in values})>1 for values in classes)
    rank_bill=sum(map(sum,ranks));paid=sum(g[0]=='paid' for g in program)
    if rank_bill>paid:
        raise ValueError('rank subadditivity control failed')
    return {'scalar_blocks':len(stages)-1,'paid_calls':paid,'unary_ranks':ranks,
            'rank_bill':rank_bill,'middle_classes':classes,'heterogeneous_classes':mixed,
            'status':'excluded' if mixed==0 and rank_bill<9 else 'not_excluded_by_this_criterion'}
