"""Canonical coefficients for any repeated site coordinate, via the five Lagrangian distances."""
import argparse
from collections import Counter
from fractions import Fraction
from functools import cache
from pathlib import Path
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from adjoint import HERE, IDENTITY, Q, conjugate, table
from bell_reads import transvection
from compile_row import apply, span

ORDER = 47377612800
COUNTS = (1,30,280,960,1024)


def point_set(point):
    return sum(1 << v for v in span(point))


def distance(left,right):
    return 5-(left & right).bit_count().bit_length()


@cache
def quotient():
    # Close the diagonal Lagrangian under a fixed list of symplectic transvections.
    base = (1,2,4,8)
    initial = point_set(base)
    queue = [base]
    seen = {initial}
    axes = (1,2,4,8,16,32,64,128,3,6,12)
    for point in queue:
        for axis in axes:
            image = tuple(transvection(axis,v) for v in point)
            key = point_set(image)
            if key not in seen:
                seen.add(key)
                queue.append(image)
    points = [point_set(point) for point in queue]
    rings = [distance(initial,X) for X in points]
    Q.need(tuple(rings.count(j) for j in range(5))==COUNTS,"2,295 Lagrangians with correct sphere census")
    return queue,points,rings


@cache
def radial_matrix():
    bases,points,rings = quotient()
    classes = json.loads((HERE/'source/CLASS-ALGEBRA.json').read_text())['classes']
    mass = [0]*5
    for c in classes:
        counts = []
        for s in c['representatives']:
            action = [apply(s,v) for v in range(256)]
            moved = [point_set(tuple(action[v] for v in X)) for X in bases]
            counts.append(Counter(distance(a,b) for a,b in zip(moved,points,strict=True)))
        Q.need(all(h==counts[0] for h in counts),"Rational packet has dissimilar displacements")
        for j in range(5):
            mass[j] += c['size']*(-64)**c['fixed']*counts[0][j]
    kernel = [Fraction(v,len(points)*cnt*16**12) for v,cnt in zip(mass,COUNTS,strict=True)]
    reps = [points[rings.index(j)] for j in range(5)]
    return tuple(tuple(sum(kernel[distance(Y,X)] for X,r in zip(points,rings,strict=True) if r==k)
                       for k in range(5)) for Y in reps)


def solve(matrix,rhs):
    augmented = [list(row)+[v] for row,v in zip(matrix,rhs,strict=True)]
    for j in range(5):
        pivot = next(i for i in range(j,5) if augmented[i][j])
        augmented[j],augmented[pivot] = augmented[pivot],augmented[j]
        augmented[j]=[v/augmented[j][j] for v in augmented[j]]
        for i in range(5):
            if i!=j:
                a=augmented[i][j]
                augmented[i]=[v-a*w for v,w in zip(augmented[i],augmented[j],strict=True)]
    return tuple(row[-1] for row in augmented)


@cache
def profile():
    # Stored values multiply conjugate(V[r,c]); factor 1/16 of extraction is absorbed.
    rhs = tuple(Fraction(1,4**13)*Fraction(-1,64)**j for j in range(5))
    return solve(radial_matrix(),rhs)


@cache
def unitary(target):
    # table divides the literal unitary by 4 for Choi normalization.
    matrix, shift = table(target)
    return matrix,shift-2


def transition(target,p,r,c,left_basis=IDENTITY,right_basis=IDENTITY):
    """Literal <a|W_p U_S|b> for a,b supplied as normalized stabilizer columns."""
    Q.need(all(type(v) is int and 0 <= v < m for v,m in ((p,256),(r,16),(c,16))),"site/Pauli labels")
    x,z = divmod(p,16)
    mid,e = unitary(tuple(target))
    left,u = unitary(tuple(left_basis))
    right,v = unitary(tuple(right_basis))
    result = (0,0)
    for j in range(16):
        l = conjugate(left[(j ^ x) | (r << 4)])
        if (z & j).bit_count()%2:
            l = (-l[0],-l[1])
        if l == (0,0):
            continue
        for k in range(16):
            term = Q.multiply(l,Q.multiply(mid[j | (k << 4)],right[k | (c << 4)]))
            result = result[0]+term[0],result[1]+term[1]
    return tuple(Fraction(value,1 << (e+u+v)) for value in result)


def coefficient(target,p,r,c,left_basis=IDENTITY,right_basis=IDENTITY):
    val = conjugate(transition(target,p,r,c,left_basis,right_basis))
    j = distance(point_set(tuple(left_basis[:4])),point_set(tuple(apply(target,b) for b in right_basis[:4])))
    weight = profile()[j]
    return val[0]*weight,val[1]*weight


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    rec=json.loads(parser.parse_args().input.read_text())
    print(json.dumps([[str(v) for v in coefficient(tuple(t),p,rec['row'],rec['column'],
                         tuple(rec.get('left_basis',IDENTITY)),tuple(rec.get('right_basis',IDENTITY)))]
                      for t,p in rec['queries']]))
