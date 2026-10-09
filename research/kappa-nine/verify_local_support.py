"""Replay local linear certificates without invoking an equation solver."""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import json
from local_support_elimination import ADJ, CAPACITY, all_cliques, initial_supports


def clique_equation(a,b,group,slot):
    assert group and len(set(group))==len(group)
    assert all(0<=i<84 for i in group)
    assert all(ADJ[i]>>j&1 for i,j in combinations(group,2)), 'not a clique'
    ua=0;ub=0
    for i in group:ua|=a[i];ub|=b[i]
    assert ((CAPACITY[ua]==2*len(group) and ua>>slot&1) or
            (CAPACITY[ub]==2*len(group) and ub>>slot&1)), 'not saturated on this block'
    return {84*slot+i:Q(1) for i in group if a[i]&b[i]&(1<<slot)}


def verify_rejection(branch,result):
    a,b=initial_supports(branch);total={};rhs=Q(0)
    for item in result['certificate']:
        coefficient=Q(item['coefficient']);rhs+=coefficient
        if item.get('type')=='trace':
            i=item['vertex'];assert 0<=i<84
            row={84*slot+i:Q(1) for slot in range(8) if a[i]&b[i]&(1<<slot)}
        else:
            slot=item.get('slot',result.get('slot'));assert 0<=slot<7
            row=clique_equation(a,b,item['clique'],slot)
        for i,x in row.items():total[i]=total.get(i,Q(0))+coefficient*x
    assert all(x==0 for x in total.values()), 'nonzero variable coefficient'
    assert rhs==Q(result['contradiction_rhs']) and rhs!=0, 'no contradiction'
    return True


def verify_linear_witness(branch,result,cliques):
    a,b=initial_supports(branch)
    values={int(i):Q(x) for i,x in result['linear_witness'].items()}
    assert all(0<=i<672 and a[i%84]&b[i%84]&(1<<(i//84)) for i in values)
    for i in range(84):
        assert sum(values.get(84*slot+i,0) for slot in range(8))==1, 'trace equation'
    for group,_ in cliques:
        ua=0;ub=0
        for i in group:ua|=a[i];ub|=b[i]
        saturated=0
        if CAPACITY[ua]==2*len(group):saturated|=ua
        if CAPACITY[ub]==2*len(group):saturated|=ub
        for slot in range(7):
            if saturated>>slot&1:
                assert sum(values.get(84*slot+i,0) for i in group)==1, 'clique diagonal equation'
    return True


def replay(path):
    result=json.loads(path.read_text());cliques=all_cliques();rejected=survived=0
    for branch in result['branches']:
        test=branch['diagonal_test']
        if test['status'].startswith('EXCLUDED'):
            verify_rejection(branch['branch'],test);rejected+=1
        else:
            verify_linear_witness(branch['branch'],test,cliques);survived+=1
    return {'replayed_rejections':rejected,'replayed_linear_witnesses':survived,
            'caution':'A linear witness does not satisfy or certify the nonlinear projector conditions.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('certificate',type=Path);args=parser.parse_args()
    print(json.dumps(replay(args.certificate),indent=2))
