"""Exact increasing q_j embedding and target-grid augmentation."""
from itertools import product
from fractions import Fraction as Q
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent
def qmap(j,s,t):return (2*t*j+s)//(2*s)
def ceildiv(a,b):return -((-a)//b)
def image_inverse(k,s,t):
    j=max(0,ceildiv(s*(2*k-1),2*t))
    return j if j<s and 2*t*j<s*(2*k+1) else None
def main():
    cases=[]
    for sizes in [((13,16),(11,16)),((17,32),(23,32)),((5,8),(7,8),(6,8))]:
        maps=[[qmap(j,s,t) for j in range(s)] for s,t in sizes]
        assert all(len(set(a))==len(a) and a==sorted(a) for a in maps)
        for (s,t),a in zip(sizes,maps):
            assert [k for k in range(t) if image_inverse(k,s,t) is not None]==a
            assert [image_inverse(k,s,t) for k in a]==list(range(s))
        original=list(product(*(range(s) for s,t in sizes)))
        it=iter(enumerate(original,1));embedded=[]
        for x in product(*(range(t) for s,t in sizes)):
            source=tuple(image_inverse(k,s,t) for k,(s,t) in zip(x,sizes))
            if None not in source:
                value=next(it);assert source==value[1];embedded.append((x,value))
        assert next(it,None) is None
        cropped=[v for x,v in embedded];assert cropped==list(enumerate(original,1))
        cases.append(dict(sizes=sizes,source_records=len(original),target_records=__import__('math').prod(t for s,t in sizes),
                          monotone_product_embedding=True,selection_restores_source_order=True))
    from check_union import eye,inverse,mm
    s,t=5,8;q=[qmap(j,s,t) for j in range(s)]
    H=eye(s)
    for j in range(s-1):H[j][j+1]=H[j+1][j]=Q(1,16)
    aug=eye(t);wanted=eye(t);Hi=inverse(H)
    for i in range(s):
        for j in range(s):aug[q[i]][q[j]]=H[i][j];wanted[q[i]][q[j]]=Hi[i][j]
    assert inverse(aug)==wanted
    assert max(abs(i-j) for i in range(t) for j in range(t) if aug[i][j])<=2
    out=dict(status='PASS_EXACT_PRODUCT_Q_EMBEDDING_AND_SELECTION',cases=cases,
        square_target_grid_augmentation=dict(s=s,t=t,q=q,all_inverse_entries_checked=True,
            holes_identity=True,physical_bandwidth_at_most_two=True),
        membership_formula='j=max(0,ceil(s(2k−1)/(2t))); retain iff j<s and 2tj<s(2k+1)')
    (HERE/'Q-EMBEDDING-CONTROLS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
