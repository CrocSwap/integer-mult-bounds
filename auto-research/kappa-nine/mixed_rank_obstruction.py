"""Exact minimal-exception exclusion, independent of the NRA solver runs.

The mathematical input is the complementary-block lemma explained in
MIXED-RANK-TEST.md; finite checks verify every support/color hypothesis.
"""
from itertools import combinations
from pathlib import Path
import argparse
import json
from local_support_elimination import ADJ,CLIQUE,INDEX,TRIPLES,classes,initial_supports
from local_rank_test import line_graph
from noncovariant_search import inverse,multiply
from covariant_block_test import rank


def local_control():
    # Columns: T0_x,T0_y,T1_x,T1_y,T2_x,T2_y.
    # Rows: exceptional two-plane, then two regular two-planes.
    a=[[2,0,0,0,0,1],[0,2,0,1,0,0],
       [1,0,0,0,0,1],[0,0,1,0,0,0],
       [0,1,0,1,0,0],[0,0,0,0,1,0]]
    b=inverse(a)
    assert multiply(a,b)==[[int(i==j) for j in range(6)] for i in range(6)]
    assert rank([row[2:] for row in a[2:]])==4
    assert rank([row[2:] for row in b[2:]])==4
    assert rank([row[:2] for row in a[:2]])==rank([row[:2] for row in b[:2]])==2
    for label in range(3):
        for block in (1,2):
            aa=[row[2*label:2*label+2] for row in a[2*block:2*block+2]]
            bb=[row[2*block:2*block+2] for row in b[2*label:2*label+2]]
            assert rank(aa)==rank(bb)==1
    return {'A':a,'B':[[str(x) for x in row] for row in b],
            'complement_ranks':[4,4],'exceptional_distinguished_ranks':[2,2]}


def forcing_witness(point,outside,exceptions):
    star=[k for k,c in enumerate(CLIQUE) if point in c]
    bad=[k for k in star if k in exceptions]
    assert len(bad)==1
    k=bad[0];pair=set(CLIQUE[k])-{point}
    vertex=INDEX[tuple(sorted(pair|{outside}))]
    clique=[i for i in classes()[point][1] if outside in TRIPLES[i]]
    assert vertex in clique and len(clique)==3
    regular=[r for r in star if r!=k]
    # Each regular block has one singleton-color member. It is one of
    # the two nondistinguished labels; the distinguished label lies in
    # the other color with the remaining label.
    singled=[]
    for r in regular:
        colors=line_graph(r)['colors']
        single=[i for i in clique if sum(colors[str(i)]==colors[str(j)] for j in clique)==1]
        assert len(single)==1 and single[0]!=vertex
        singled+=single
    assert set(singled)==set(clique)-{vertex}
    return {'point':point,'outside':outside,'vertex':vertex,'triple':list(TRIPLES[vertex]),
            'clique':clique,'exception_block':k,'regular_blocks':regular,
            'regular_singletons':singled}


def check_conflict(witness):
    exceptions=set(witness['exception_blocks']);left=witness['left'];right=witness['right']
    for w in (left,right):
        assert w==forcing_witness(w['point'],w['outside'],exceptions)
    i=left['vertex'];j=right['vertex'];k=left['exception_block']
    assert k==right['exception_block'] and ADJ[i]>>j&1
    support,_=initial_supports((3,)*7)
    assert support[i]&support[j]==1<<k
    return True


def audit():
    stars=[{k for k,c in enumerate(CLIQUE) if point in c} for point in range(7)]
    conflicts=[];old=[];survivors=[]
    for mask in range(128):
        exceptions={k for k in range(7) if mask>>k&1}
        if not all(exceptions&star for star in stars):
            old.append(sorted(exceptions));continue
        conflict=None
        for k in sorted(exceptions):
            degree_one=[j for j in CLIQUE[k] if len(exceptions&stars[j])==1]
            if len(degree_one)>=2:
                left=forcing_witness(degree_one[0],7,exceptions)
                right=forcing_witness(degree_one[1],8,exceptions)
                conflict={'exception_blocks':sorted(exceptions),'left':left,'right':right}
                assert check_conflict(conflict);break
        if conflict:conflicts.append(conflict)
        else:survivors.append(sorted(exceptions))
    assert len(conflicts)==7 and all(len(w['exception_blocks'])==3 for w in conflicts)
    assert min(map(len,survivors))==4
    return {'status':'EXACT SCOPED EXCLUSION; NO NEW KAPPA',
            'scope':'Uniform mode 3: at least four anchored blocks must have some Y restriction of rank zero or two.',
            'previous_rank_one_exclusions':old,'new_complementary_block_exclusions':conflicts,
            'surviving_exception_sets':survivors,'minimum_exceptions_remaining':4,
            'local_exact_control':local_control(),
            'full_branch_status':'OPEN; no additional one of the 103 complete branch representatives is excluded.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status']);print('Seven minimal patterns excluded; at least four exceptional blocks required.')
