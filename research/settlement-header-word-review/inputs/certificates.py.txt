"""Zero-block, raw-order and closed-form finite certificates."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, combinations_with_replacement
from math import factorial

from algorithms import frequency_blocks, scalar_small_field
from literal import identity_pass, literal_orders
from monomial import flat_rows, passing_permutations, separated_ternary_probability
from settlement import Field, partition, ternary_extra, witness


def need(condition, name):
    if not condition:
        raise ValueError(name)


def block_oracle(f, values):
    """List admissible blocks directly; then cover by disjoint zero blocks."""
    values = tuple(values)
    zero_masks = []
    for k in range(1,len(values)+1):
        for indices in combinations(range(len(values)),k):
            total = [0]*len(values[0])
            for i in indices:
                total = [f.add[a][b] for a,b in zip(total,values[i])]
            if not any(total):
                zero_masks.append(sum(1 << i for i in indices))
    @lru_cache(None)
    def best(mask):
        if not mask:
            return 0
        pivot = mask & -mask
        return 1+max(best(mask ^ block) for block in zero_masks
                     if pivot & block and mask & block == block)
    return best((1 << len(values))-1)


def partitions_report():
    result = []
    for q in (2,3,4,5,7,8,9):
        f = Field(q)
        cases = 0
        closed = 0
        edges = Counter()
        for h in range(1,8):
            for items in combinations_with_replacement(range(1,q),h):
                total = 0
                for x in items:
                    total=f.add[total][x]
                if total:
                    continue
                values=[(x,) for x in items]
                a=partition(f,values)
                expected=block_oracle(f,values)
                need(len(a)==expected==frequency_blocks(f,values),"labeled/frequency/disjoint partitions")
                if q <= 5:
                    need(expected==scalar_small_field(f,items),"small-field exact block count")
                    closed+=1
                cases+=1
                edges[h-expected]+=1
        result.append(dict(q=q,scalar_cases=cases,small_field_cases=closed,
                           optimal_cost_histogram=dict(sorted(edges.items()))))
    return result


def permutation_reports():
    result=[]
    for q in (2,3,4,5,7,8,9):
        f=Field(q)
        u=(1,1); b=(1,0); w=(f.neg[1],1)
        u2=(0,1); b2=(1,1); w2=(f.neg[1],0)
        for label,image,base,slope in [("exclusive",u,b,w),("identical",u2,b2,w2)]:
            rows=flat_rows(f,base,[slope])
            nums=[]
            for mask in range(1 << q):
                fixed=[row for i,row in enumerate(rows) if mask & (1 << i)]
                a=passing_permutations(f,image,fixed)
                # In dimension two the sole determinant is its literal diagonal entry.
                literal=sum(all(1 != f.mul[image[j]][v[j]] for v in fixed) for j in range(2))
                need(a==literal,"two-coordinate named order counts")
                nums.append(a)
            expected=0 if label=="exclusive" else 1
            need(nums[-1]==expected,"monomial orbit contrast")
            result.append(dict(q=q,model=label,named_subsets=len(nums),
                               joint_numerator=nums[-1],single_numerators=[nums[1<<i] for i in range(q)],
                               histogram=dict(sorted(Counter(nums).items()))))
    return result


def ternary_cases():
    f=Field(3); report=[]
    for m in range(2,9):
        tested=0
        for values in combinations_with_replacement(range(3),m):
            if sum(values)%3!=1:
                continue
            expected=separated_ternary_probability(values)
            counted=passing_permutations(f,(1,)*m,[values])
            need(Fraction(counted,factorial(m))==expected,"ternary labeled-order formula")
            if m<=5:
                need(counted==literal_orders(f,(1,)*m,[values]),"ternary literal order count")
            d=values.count(1)-values.count(2)
            need((expected>0)==(ternary_extra(values)==0) and d%3==1,"ternary zero-cost criterion")
            tested+=1
        report.append(dict(m=m,tested=tested))
    return report


def constructions():
    f=Field(5)
    anchor=[]
    for w in [(1,4,2,3,0),(1,1,1,2,0),(1,1,1,2,4,4,4,3,0)]:
        p=witness(f,(1,)*len(w),[w])
        anchor.append(dict(field=5,w=w,certificate=p))
    binary=[]
    f=Field(2)
    for n in range(6):
        h=2*n+1
        u=(1,)*h+(0,); b=u; w=(0,)*h+(1,)
        pencil=flat_rows(f,b,[w])
        cert=witness(f,u,pencil,target_value=(1,1))
        need(cert["distance"]==n and witness(f,u,[w])["distance"]==0,"binary unbounded gap")
        binary.append(dict(n=n,certificate=cert))
    return dict(anchored=anchor,binary=binary)


def controls():
    f=Field(5)
    need(witness(f,(1,)*5,[(1,4,2,3,0)])["distance"]==2,"cancelling pairs anchor")
    need(witness(f,(1,)*5,[(1,1,1,2,0)])["distance"]==3,"indivisible block anchor")
    f2=Field(2)
    rows=[(1,0),(0,1)]
    need(witness(f2,(1,1),rows,target_value=(1,1))["distance"]==1,"binary dummy anchor")
    need(passing_permutations(f2,(1,1),rows)==0 and passing_permutations(f2,(0,1),[(1,1),(0,1)])==1,
         "monomial order anchor")
    vals=(1,1,1,2)
    need(frequency_blocks(f,[(x,) for x in vals])==scalar_small_field(f,vals)==1,"small field anchor")
    need(ternary_extra((1,1,1,1,0))==1 and separated_ternary_probability((2,2,0))==Fraction(2,3),
         "ternary scalar anchor")
    need(identity_pass(f2,(0,1),[(1,1)]) and not identity_pass(f2,(1,0),[(1,1)]),"literal minor anchor")
