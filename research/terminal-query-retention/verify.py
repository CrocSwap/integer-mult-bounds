#!/usr/bin/env python3
"""Portable exact local identities + moment. Not a universal compiler check."""
import argparse,hashlib,json
from fractions import Fraction as F
from pathlib import Path
import moment
from verify_query_retention import mat,eye,mm,inverse,rank

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--flow',type=Path)
    args=parser.parse_args();here=Path(__file__).resolve().parent
    selected=json.loads((here/'terminal-inputs.json').read_text())
    full=None
    if args.flow:
        raw=args.flow.read_bytes();assert hashlib.sha256(raw).hexdigest()==selected['flow_sha256']
        full=json.loads(raw)
    total=0
    assert len(selected['centers'])==22
    for item in selected['centers']:
        c,n=item['witness'],item['node'];i=c['node'];N=n['n'];p=c['pivot']
        assert N==n['d']==n['retired']==9 and n['t']==n['r']==n['new_dirty']==0
        assert not n['source_controls'] and len(n['reads'])==1
        assert n['reads'][0]['kind']=='center' and n['frame'][0]==1 and len(n['frame'][1])==20
        assert not any(pair[0]==i or pair[2]==i for pair in selected['kernel_pairs'])
        if full:
            assert n==full['nodes'][i]
            assert item['inputs']==[full['vectors'][v] for v in n['inputs']]
            assert item['query']==full['vectors'][n['reads'][0]['value']]
        rows=[dict((j,F(a)) for j,a in r) for r in item['inputs']]
        cols=sorted(set().union(*(set(r) for r in rows)))
        assert rank([[r.get(j,0) for j in cols] for r in rows])==9
        ell=[F(c['coefficients'].get(str(j),'0')) for j in range(N)]
        assert ell==[F(1)]*9
        actual={j:sum(ell[k]*rows[k].get(j,0) for k in range(N)) for j in cols}
        actual={j:v for j,v in actual.items() if v}
        assert actual==dict((j,F(a)) for j,a in item['query'])
        T=eye(N);T[p]=ell;literal=eye(N)
        for op,t,s,a in c['literal_forward_steps']:
            assert op=='add';literal[t]=[x+F(a)*y for x,y in zip(literal[t],literal[s])]
        assert literal==T and mm(inverse(T),T)==eye(N)
        assert T!=eye(N) and ell!=eye(N)[p] # stale/early cleanup controls
        total+=N
    profile=json.loads((here/'profile.json').read_text())
    H={int(r):n for r,n in profile['histogram'].items()}
    assert sum(H.values())==358975 and sum(r*n for r,n in H.items())==1613040
    a=F(754736418878859,10**18)
    low,high=moment.moment(H,110,14692,a)
    nextlow,_=moment.moment(H,110,14692,a+F(1,10**18))
    assert high<1<nextlow
    print(json.dumps(dict(status='PASS_EXACT_LOCAL_WITNESSES_AND_MOMENT',dirty_columns=total,
       flow_provenance_checked=bool(full),saving=str(a),
       moment_gap_lower=str(1-high),next_grid_rejected=True,
       scope='Construction uses the written compositional proof and inherited interfaces; no new Lean or global transcript replay.'),indent=2))
if __name__=='__main__':main()
