#!/usr/bin/env python3
"""Check the quadratic description and the optimal affine product cover."""

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def require(value, label):
    if not value:
        raise ValueError(label)


def dot(a,b):
    return (a & b).bit_count()%2


def span(vectors):
    result = {0}
    for vector in vectors:
        result |= {x^vector for x in result}
    return frozenset(result)


def dimension(space):
    return len(space).bit_length()-1


def quadratic(a,w):
    require(w.bit_count()%2==0,"even quadratic domain")
    return (w.bit_count()//2+dot(a,w))%2


def self_orthogonal_spaces(width):
    levels = [{frozenset((0,))}]
    even = [x for x in range(1 << width) if x.bit_count()%2==0]
    for _ in range(width//2):
        following = set()
        for old in levels[-1]:
            for x in even:
                if x not in old and all(dot(x,y)==0 for y in old):
                    following.add(frozenset(old | {y^x for y in old}))
        levels.append(following)
    return set().union(*levels)


def product(values):
    out = 1
    for value in values:
        out *= value
    return out


def lagrangians(g):
    require(g>=0,"nonnegative symplectic dimension")
    return product((1 << j)+1 for j in range(1,g+1))


def split_count(g):
    require(g>=0,"nonnegative split dimension")
    return 1 if g==0 else 2*lagrangians(g-1)


def nonsplit_count(g):
    require(g>=1,"nonempty nonsplit dimension")
    return product((1 << j)+1 for j in range(2,g+1))


def preferred(width,residue):
    f = width//2
    return residue in ({f%4} if width%2==0 else {f%4,(f+1)%4})


def maximum_dimension(width,residue):
    return width//2-int(not preferred(width,residue))


def predicted_extensions(width,a,old):
    f,r = width//2,dimension(old)
    residue = a.bit_count()%4
    omega = (1 << width)-1
    if width%2:
        return split_count(f-r) if preferred(width,residue) else nonsplit_count(f-r)
    if quadratic(a,omega):
        return lagrangians(f-1-r)
    rp = dimension(span(list(old)+[omega]))
    return split_count(f-rp) if preferred(width,residue) else nonsplit_count(f-rp)


def check_extensions(width):
    spaces = self_orthogonal_spaces(width)
    records = {}
    prescribed = 0
    sums = 0
    omega = (1 << width)-1
    even = [x for x in range(1 << width) if x.bit_count()%2==0]
    for a in range(1 << width):
        singular = [w for w in spaces if all(quadratic(a,x)==0 for x in w)]
        largest = max(map(dimension,singular))
        require(largest==maximum_dimension(width,a.bit_count()%4),"sharp Witt index")
        maxima = [w for w in singular if dimension(w)==largest]
        for old in singular:
            count = sum(old<=w for w in maxima)
            require(count>0,"prescribed extension exists")
            require(count==predicted_extensions(width,a,old),"exact extension multiplicity")
            prescribed += 1
        total = sum((-1)**quadratic(a,w) for w in even)
        # Multiply Gaussian integers directly; do not use the predicted sign.
        re,im = 1,0
        for i in range(width):
            sign = -1 if (a >> i)&1 else 1
            re,im = re-sign*im,im+sign*re
        require(total==re,"complete quadratic Gauss sum")
        if width%2:
            require(total==((-1)**int(not preferred(width,a.bit_count()%4)))*(1 << (width//2)),
                    "odd quadratic type")
        elif quadratic(a,omega):
            require(total==0,"anisotropic radical sum")
        else:
            require(total==((-1)**int(not preferred(width,a.bit_count()%4)))*(1 << (width//2)),
                    "even quotient type")
        sums += 1
        records[a] = maxima
    return {"width":width,"self_orthogonal_spaces":len(spaces),
            "prescribed_extensions_checked":prescribed,"Gauss_sums":sums},records


def phase_sector(rows):
    n = len(rows)
    phases = set()
    for q in range(1,1 << n):
        if q.bit_count()%2:
            value = 0
            for i,x in enumerate(rows):
                if (q >> i)&1:
                    value ^= x
            phases.add(value.bit_count()%4)
    return len(phases)==1


def check_points(n,width,maxima):
    accepted = 0
    tuples = 0
    for rows in itertools.product(range(1 << width),repeat=n):
        a = rows[0]
        old = span(x^a for x in rows[1:])
        criterion = all(w.bit_count()%2==0 for w in old)
        if criterion:
            criterion = all(quadratic(a,w)==0 for w in old)
        require(criterion==phase_sector(rows),"complete odd-sum criterion")
        if criterion:
            extensions = [w for w in maxima[a] if old<=w]
            require(extensions,"point has an optimal product piece")
            require(len(extensions)==predicted_extensions(width,a,old),"point multiplicity")
            for w in extensions:
                require(all(x^a in w for x in rows),"product contains every row")
            accepted += 1
        tuples += 1
    return {"n":n,"width":width,"all_row_tuples":tuples,"sector_points":accepted}


def main():
    extensions,by_width = [],{}
    for width in range(1,7):
        record,maxima = check_extensions(width)
        extensions.append(record)
        by_width[width] = maxima
    points = [check_points(n,width,by_width[width])
              for n in (1,2,3) for width in range(1,5)]
    dependency = HERE.parent/"review-gauss/maximal-affine-sectors/RIGIDITY.md"
    result = {"status":"PASS_QUADRATIC_AFFINE_SECTOR_COVER",
              "proof_sha256":hashlib.sha256((HERE/"COVERAGE.md").read_bytes()).hexdigest(),
              "rigidity_sha256":hashlib.sha256(dependency.read_bytes()).hexdigest(),
              "extension_cases":extensions,"point_cases":points,
              "scope":"Exact quadratic criterion, prescribed optimal product extensions, Gauss types, and extension multiplicities. No physical adaptive-code access or supplier claim."}
    (HERE/"COVERAGE.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"])


if __name__=="__main__":
    main()
