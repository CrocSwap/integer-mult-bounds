"""Exact controls for the written two-register, three-mixing-block theorem.

Jose Manuel, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction as F
from itertools import permutations, product
import json


def require(ok, message):
    if not ok:
        raise ValueError(message)


GROUP = tuple(permutations(range(3)))
UNIT = (0, 1, 2)


def mul(a, b):
    return tuple(a[b[i]] for i in range(3))


def determinant(m):
    return m[0]*m[3]-m[1]*m[2]


def middle_census(prime):
    mixers = [m for m in product(range(prime), repeat=4) if determinant(m)%prime]
    cases = eligible = 0
    for a,b,c,d in product(GROUP,repeat=4):
        labels = (mul(c,a),mul(c,b),mul(d,a),mul(d,b))
        for m in mixers:
            classes = {}
            for index,(label,value) in enumerate(zip(labels,m)):
                if value:
                    classes.setdefault(label,[0]*4)[index] = value
            necessary = (len(classes)==1 and determinant(next(iter(classes.values())))%prime!=0)
            if len(classes)==2:
                necessary = all(determinant(row)%prime==0 for row in classes.values())
            if necessary:
                eligible += 1
                require(sum(bool(x) for x in m)==2 or a==b or c==d,"middle classification")
            cases += 1
    return {"field":prime,"invertible_mixers":len(mixers),"cases":cases,"necessary_condition_survivors":eligible}


def scalar(m):
    return [[{UNIT:F(m[2*i+j])} if m[2*i+j] else {} for j in range(2)] for i in range(2)]


def diagonal(a,b):
    return [[{a:F(1)},{}],[{},{b:F(1)}]]


def mm(a,b):
    out = [[{} for _ in range(2)] for _ in range(2)]
    for i,j,k in product(range(2),repeat=3):
        for g,x in a[i][k].items():
            for h,y in b[k][j].items():
                key = mul(g,h)
                out[i][j][key] = out[i][j].get(key,F(0))+x*y
    return [[{g:x for g,x in row.items() if x} for row in line] for line in out]


def chain(*factors):
    value = scalar((1,0,0,1))
    for factor in factors:
        value = mm(value,factor)
    return value


def exact_reductions():
    a,b = (1,0,2),(0,2,1)
    require(mul(a,b)!=mul(b,a),"noncommuting group control")
    m1,m2,m3 = map(scalar,((1,2,3,7),(2,1,1,1),(1,3,2,5)))
    d0,d3 = diagonal(a,b),diagonal(mul(a,b),a)
    common,other = diagonal(a,a),diagonal(b,UNIT)
    before = chain(d3,m3,other,m2,common,m1,d0)
    after = chain(d3,m3,other,mm(m2,m1),mm(common,d0))
    require(before==after,"common right layer reduction")
    before = chain(d3,m3,common,m2,other,m1,d0)
    after = chain(mm(d3,common),mm(m3,m2),other,m1,d0)
    require(before==after,"common left layer reduction")
    swap = scalar((0,1,1,0))
    left,right = diagonal(a,b),diagonal(b,mul(a,b))
    require(chain(left,swap,right)==chain(diagonal(mul(a,mul(a,b)),mul(b,b)),swap),"monomial preserves product order")
    h,d = scalar((1,1,1,-1)),diagonal(UNIT,a)
    loop = chain(h,d,h,d,h,d,scalar((F(1,4),F(1,4),F(1,4),F(-1,4))),d)
    require(loop==diagonal(a,a),"four-block boundary loop")
    for values in ((1,1,1,2),(1,1,1,0)):
        middle = chain(diagonal(UNIT,a),scalar(values),diagonal(UNIT,a))
        classes = {g:[middle[i][j].get(g,F(0)) for i,j in product(range(2),repeat=2)]
                   for g in (UNIT,a)}
        require(any(determinant(row)!=0 for row in classes.values()),"rank-two coefficient obstruction")
    require(chain(h,d,h,d,h,d)!=diagonal(a,a),"three-block boundary rejection")
    return {"noncommuting_reductions":3,"coefficient_rank_controls":2,"four_block_loop":"PASS"}


def rational_rank(rows):
    rows = [list(map(F,row)) for row in rows]
    pivot = 0
    for col in range(len(rows[0])):
        index = next((i for i in range(pivot,len(rows)) if rows[i][col]),None)
        if index is None:
            continue
        rows[pivot],rows[index] = rows[index],rows[pivot]
        scale = rows[pivot][col]
        rows[pivot] = [x/scale for x in rows[pivot]]
        for i in range(pivot+1,len(rows)):
            scale = rows[i][col]
            rows[i] = [x-scale*y for x,y in zip(rows[i],rows[pivot])]
        pivot += 1
        if pivot==len(rows):
            break
    return pivot


def tensor_controls():
    # Five invertible matrices I+t E12. Tensor flattening preserves rank.
    ranks = []
    for power in (1,3,4):
        vectors = []
        for t in range(5):
            v = [F(1)]
            for _ in range(power):
                v = [x*y for x in v for y in (1,t,0,1)]
            vectors.append(v)
        ranks.append(rational_rank(vectors))
    require(ranks==[2,4,5],"tensor separation and below-threshold control")
    return {"distinct_invertible_operators":5,"powers":[1,3,4],"ranks":ranks}


def main():
    print(json.dumps({"status":"PASS_TWO_REGISTER_THREE_MIX",
                      "middle_census":[middle_census(2),middle_census(3),middle_census(5)],
                      "reductions":exact_reductions(),"tensor_controls":tensor_controls(),
                      "scope":"Exact controls; the written proof covers all groups and fields. Four or more mixing blocks remain open."},indent=2))


if __name__ == "__main__":
    main()
