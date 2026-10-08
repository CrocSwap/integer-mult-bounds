"""Exact finite screen of unequal outer/middle bit factors.

The same outer dimension permits stage-one/stage-three auxiliary sharing.
This is a bounded experiment, not an all-network or all-size optimality claim.
"""
from fractions import Fraction as Q
from math import comb

from explore import log_integer_bounds
from paired_exclusion_circuit import PairedExclusionCircuit
from shared_point_circuit import SharedPointCircuit
from search_network import log_ratio_bounds


def certificate():
    local = {}
    for h in range(30,71,2):
        c = SharedPointCircuit(h,PairedExclusionCircuit(h-1))
        local[h] = dict(v=comb(h,3),additions=c.additions,
                        partial_outputs=len(c.outputs),
                        side_roles=c.additions+len(c.outputs))
    cases = []
    for outer,a in local.items():
        for middle,b in local.items():
            v,u = a['v'],b['v']
            N,m = v*v*u,outer*outer*middle
            L = 2*v*u*outer*outer+v*v*middle*middle
            D = N-2*L
            if D <= 0:
                continue
            W = 2*N+v*u*(a['side_roles']+outer)+v*v*(b['side_roles']+middle)
            eta = Q(D,W*m)
            nlo,nhi = log_ratio_bounds(1/(1-eta),terms=3)
            dlo,dhi = log_integer_bounds(m)
            cases.append(dict(outer=outer,middle=middle,N=N,m=m,W=W,L=L,
                              eta=eta,saving_lower=nlo/dhi,saving_upper=nhi/dlo))
    winner = max(cases,key=lambda row:row['saving_lower'])
    assert all(winner['saving_lower']>row['saving_upper'] for row in cases if row is not winner)
    assert winner['outer']==winner['middle']
    h=winner['outer']
    c=SharedPointCircuit(h,PairedExclusionCircuit(h-1))
    checked=dict(local=c.local.verify(),global_circuit=c.verify(),frames=c.verify_frames())
    return dict(status='BOUNDED SCREEN; NO NEW BIT SAVING OR GLOBAL OPTIMALITY CLAIM',
                outer_sizes=list(local),middle_sizes=list(local),
                pairs_examined=len(local)**2,positive_deficit_cases=len(cases),
                winner=winner,winner_audits=checked,
                circuit_counts={str(h):row for h,row in local.items()},
                scope='Paired common-point circuits, equal first and third factors, distinct middle factor; 30 through 70 by twos only.')


if __name__=='__main__':
    import json
    from explore import serializable
    from pathlib import Path
    result=certificate()
    Path(__file__).with_name('bit-screen.json').write_text(
        json.dumps(serializable(result),indent=2,sort_keys=True)+'\n')
    print('PASS finite bit screen:',result['winner']['outer'],result['winner']['middle'],result['winner']['outer'])
