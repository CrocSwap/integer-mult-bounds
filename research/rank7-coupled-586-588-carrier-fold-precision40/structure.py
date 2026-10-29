# SPDX-License-Identifier: Apache-2.0
"""Exact two-sided subspace certificate, independent of the word producer."""
from collections import defaultdict
from fractions import Fraction as Q

def check(parent,transform,aud):
    h=transform['helper'];live=sorted(set(range(704))-set(parent['removed'])-set(range(112,224)))
    S={r:{r:Q(1)} for r in live};T={r:{r:Q(1)} for r in live}
    for g in transform['before']:aud.apply(g,S)
    for g in transform['after']:aud.apply(g,T)
    v={r:row[h] for r,row in S.items() if h in row};alpha=T[h]
    J={r:{r:Q(1)} for r in live}
    for g in reversed(transform['after']):aud.apply(aud.invert(g),J)
    y={r:row[h] for r,row in J.items() if h in row}
    M={r:{(r,()):Q(1)} for r in live};program=list(parent['A'][parent['prelude_events']:]);bypos=defaultdict(list)
    for op,rec in enumerate(parent['warps'],1):bypos[rec[0]].append(['warp',rec[1],op])
    for p in range(len(parent['B'])+1):
        program+=bypos[p]
        if p<len(parent['B']):program.append(parent['B'][p])
    program+=parent['restore']
    for g in program:
        if g[0]=='warp' or not 112<=g[1]<224:aud.walg_apply(g,M,False,10**6)
    u=defaultdict(Q)
    for r,a in alpha.items():
        for key,c in M[r].items():u[key]+=a*c
    u={key:c for key,c in u.items() if c}
    protected=set(map(int,parent['helper_final']))|set(map(int,parent['start_extra']))|{c['source'] for c in parent['initial_corrections']}
    H={r for r in live if r>=224 and r not in protected}
    assert set(v)<=H and all(r in H and not ops for r,ops in u)
    u={r:c for (r,ops),c in u.items()}
    for r,row in M.items():
        mv=defaultdict(Q)
        for (c,ops),a in row.items():mv[ops]+=a*v.get(c,Q(0))
        assert {ops:a for ops,a in mv.items() if a}==({():y[r]} if r in y else {})
    assert sum(alpha.get(r,Q(0))*c for r,c in y.items())==1
    us=defaultdict(Q)
    for r,a in u.items():
        for c,b in S[r].items():us[c]+=a*b
    assert {r:c for r,c in us.items() if c}=={h:Q(1)}
    assert all(sum(row.get(c,Q(0))*a for c,a in y.items())==(1 if r==h else 0) for r,row in T.items())
    return {'status':'PASS_EXACT_TWO_SIDED_SUBSPACE_CERTIFICATE','helper':h,'v':{str(r):str(c) for r,c in v.items()},'u':{str(r):str(c) for r,c in u.items()},'alpha':{str(r):str(c) for r,c in alpha.items()},'y':{str(r):str(c) for r,c in y.items()},'identities':['S e_h = v','u S = e_h^T','M v = y','alpha M = u','alpha y = 1','T y = e_h','e_h^T T = alpha'],'scope':'Exact free-operator identities before target writes; full target correctness checked separately.'}
