"""Independent fixed-both local/auxiliary/complement transfer controls.
Does not enumerate data-prefix pairs or import a physical producer.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from math import comb
import json

HERE=Path(__file__).resolve().parent


def check_dimension(h):
    triple_count=0
    product_classes=set()
    for T in combinations(range(h),3):
        p=[Q(int(i in T)+3) for i in range(h)]
        xi=[Q(int(i in T),2)-Q(5,3*(h+1)) for i in range(h)]
        assert all(p) and all(xi) and sum(x*y for x,y in zip(p,xi))==1
        product_classes.update(x*y for x,y in zip(p,xi));triple_count+=1
    centers=[]
    for i in range(h):
        # H^-1(e_i-1/3 1), scaled so p_i xi_i=1.
        p=[Q(int(j==i))+Q(2,h-9) for j in range(h)]
        xi=[Q(h-9,12)-Q(h-9,4)*int(j==i) for j in range(h)]
        assert sum(x*y for x,y in zip(p,xi))==1
        # H p=e_i-1/3 1; kernel xi is the original retained total U_i.
        Hp=[x-sum(p)/9 for x in p]
        assert Hp==[Q(int(j==i))-Q(1,3) for j in range(h)]
        Lp=[x+sum(p) for x in p]
        xiL=[x-sum(xi)/Q(h+1) for x in xi]
        expected_p=[Q(int(j==i))+Q(3*h-7,h-9) for j in range(h)]
        expected_xi=[Q(h-9,3*(h+1))-Q(h-9,4)*int(j==i) for j in range(h)]
        assert Lp==expected_p and xiL==expected_xi
        assert all(Lp) and all(xiL) and sum(x*y for x,y in zip(Lp,xiL))==1
        centers.append(dict(center=i,p=[str(x) for x in Lp],xi=[str(x) for x in xiL]))
    return dict(h=h,triple_count=triple_count,product_classes=sorted(map(str,product_classes)),
                centers=centers)


def permutations():
    a,b=23,25;m=a*b;d=a+b-1
    R=list(range(a))+[a-1]+list(range(a));C=list(range(a))+[0]+list(range(a))
    rows=[{} for _ in range(b)]
    for physical,label in list(enumerate(R))+[(m-d+j,c) for j,c in enumerate(C)]:
        alpha,beta=divmod(physical,b)
        assert alpha not in rows[beta] or rows[beta][alpha]==label
        rows[beta][alpha]=label
        assert len(set(rows[beta].values()))==len(rows[beta])
    for mapping in rows:
        free=iter(j for j in range(a) if j not in mapping.values())
        for i in range(a):
            if i not in mapping:mapping[i]=next(free)
        assert sorted(mapping.values())==list(range(a))
    def label(i):alpha,beta=divmod(i,b);return rows[beta][alpha]
    assert [label(i) for i in range(a)]==list(range(a))
    assert [label(m-a+j) for j in range(a)]==list(range(a))
    assert [i%b for i in range(a)]==list(range(a))
    assert [(m-a+j)%b for j in range(a)]==list(range(2,b))
    r=[label(i) for i in range(b)];c=[label(m-b+j) for j in range(b)]
    assert r==list(range(a))+[22,0]
    assert c==[22,0]+list(range(a))
    assert [i%b for i in range(b)]==[(m-b+j)%b for j in range(b)]
    return dict(dimensions=[a,b],row_labels=R,column_labels=C,
        permutations=[[row[i] for i in range(a)] for row in rows],
        local_a_rows=list(range(a)),local_a_columns=list(range(a)),
        local_b_row_scales=r,local_b_column_scales=c)


def run():
    return dict(status='PASS fixed-both local/auxiliary/complement conditions; data prefixes separate',
        dimensions=[check_dimension(h) for h in (23,25)],physical=permutations(),
        proof_boundary='Finite scalar controls and exact contraction labels; full all-pair data-prefix replay remains separate.')

if __name__=='__main__':
    result=run();HERE.joinpath('local-transfer.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
    print('triples',sum(r['triple_count'] for r in result['dimensions']),
          'centers',sum(len(r['centers']) for r in result['dimensions']))
