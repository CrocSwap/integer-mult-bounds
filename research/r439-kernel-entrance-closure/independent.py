#!/usr/bin/env python3
"""Independent exact Gram-projector and row-matrix check; Apache-2.0.

No imports from verify.py or the predecessor implementation. Same researcher
with AI assistance; algorithmic independence does not imply human review.
"""
from fractions import Fraction as F
from itertools import combinations
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def dot(x, y):
    return sum(a*b for a,b in zip(x,y))


def basis(rows):
    out = []
    for raw in rows:
        v = tuple(map(F, raw))
        rem = tuple(v[i]-project(v, out)[i] for i in range(8)) if out else v
        if any(rem):
            out.append(v)
            check(len(out) <= 2, 'independent rank exceeds two')
    check(out, 'zero first-contact frame')
    return tuple(out)


def project(v, b):
    if len(b) == 1:
        c = dot(v,b[0])/dot(b[0],b[0])
        return tuple(c*x for x in b[0])
    x,y = b
    a,c,d = dot(x,x),dot(x,y),dot(y,y)
    denominator = a*d-c*c
    check(denominator > 0, 'positive Gram determinant')
    s,t = dot(v,x),dot(v,y)
    u,z = (d*s-c*t)/denominator,(a*t-c*s)/denominator
    return tuple(u*x[i]+z*y[i] for i in range(8))


def key(b):
    return tuple(project(tuple(F(i == j) for i in range(8)), b) for j in range(8))


def meet(a, b):
    """Intersect distinct planes by a 2-column residual dependence, no elimination."""
    check(len(a) == len(b) == 2, 'plane pair')
    ra = tuple(x-y for x,y in zip(a[0], project(a[0],b)))
    rb = tuple(x-y for x,y in zip(a[1], project(a[1],b)))
    coordinate = next((j for j in range(8) if ra[j] or rb[j]), None)
    check(coordinate is not None, 'distinct planes')
    s,t = rb[coordinate],-ra[coordinate]
    if any(s*ra[j]+t*rb[j] for j in range(8)):
        return None
    v = tuple(s*a[0][j]+t*a[1][j] for j in range(8))
    check(any(v) and project(v,a) == project(v,b) == v, 'intersection vector')
    return (v,)


def nullrows(rows, n):
    """F2 elimination on target rows, opposite orientation to main checker."""
    matrix = [list(row) for row in rows]
    pivots = []
    k = 0
    for col in range(n):
        selected = next((j for j in range(k,len(matrix)) if matrix[j][col]), None)
        if selected is None:
            continue
        matrix[k],matrix[selected] = matrix[selected],matrix[k]
        for j in range(len(matrix)):
            if j != k and matrix[j][col]:
                matrix[j] = [x^y for x,y in zip(matrix[j],matrix[k])]
        pivots.append(col)
        k += 1
    vectors = []
    for j in range(n):
        if j not in pivots:
            v = [int(i == j) for i in range(n)]
            for pivot,equation in zip(pivots,matrix):
                v[pivot] = equation[j]
            vectors.append(v)
    return k,vectors


def run():
    pins = json.loads((HERE/'SOURCES.json').read_text())
    inputs = [r for r in pins['files'] if r['usage'] == 'input']
    check(len(inputs) == 1, 'one pinned word input')
    data = (ROOT/inputs[0]['path']).read_bytes()
    check(hashlib.sha256(data).hexdigest() == inputs[0]['sha256'], 'independent source hash')
    word = json.loads(gzip.decompress(data))
    check((word['v'],word['R']) == (111,439), 'dimensions')
    contacts = {}
    for section in ['A','B']:
        for frame,destination,sources in word[section]:
            for helper in [destination,*sources]:
                if helper >= 222 and helper not in contacts:
                    contacts[helper] = frame
    check(sorted(contacts) == list(range(222,661)), 'complete helper contacts')
    original = {f:basis([word['lines'][i] for i in word['frames'][f]]) for f in set(contacts.values())}
    all_spaces = {key(b):b for b in original.values()}
    planes = [b for b in all_spaces.values() if len(b)==2]
    for a,b in combinations(planes,2):
        intersection = meet(a,b)
        if intersection:
            all_spaces[key(intersection)] = intersection
    check(len(all_spaces)==366, 'complete independent closure')
    response = [[0]*439 for _ in range(111)]
    for frame,target,sources in word['D']:
        check(frame==0 and 111<=target<222,'independent D shape')
        for source in sources:
            check(222<=source<661,'independent source role')
            response[target-111][source-222] ^= 1
    receipt = json.loads((HERE/'CERTIFICATE.json').read_text())
    classes = receipt['classification']['classes']
    recorded = {}
    for row in classes:
        b = basis(row['frame'])
        k = key(b)
        check(k not in recorded,'duplicate certificate frame')
        recorded[k] = row
    check(set(recorded)==set(all_spaces),'exact closure equals certificate')
    live = []
    for k,b in all_spaces.items():
        row = recorded[k]
        eligible_frames = {f for f,v in original.items() if all(project(x,v)==x for x in b)}
        helpers = sorted(h for h in contacts if contacts[h] in eligible_frames)
        check(helpers == row['eligible_helpers'],'independent eligibility')
        matrix = [[r[h-222] for h in helpers] for r in response]
        rank,vectors = nullrows(matrix,len(helpers))
        check(rank==row['response_rank'] and len(vectors)==row['nullity'],'independent nullity')
        supports = [[h for h,value in zip(helpers,v) if value] for v in vectors]
        # Only the zero space or a one-dimensional nullspace occurs in this input.
        check(supports==row['kernel_basis'],'independent kernel basis')
        if supports:
            live.extend(supports)
    check(live==[[444,470]],'unique independent nonzero direction')
    fixture = [[int((c>>r)&1) for c in [1,2,4,8,16,31]] for r in range(5)]
    check(nullrows(fixture,6)==(5,[[1]*6]),'independent long-support control')
    print('PASS_R439_KERNEL_ENTRANCE_INDEPENDENT projectors=366 all_response_matrices=366 unique_kernel=444+470 no_new_kappa')


if __name__ == '__main__':
    run()
