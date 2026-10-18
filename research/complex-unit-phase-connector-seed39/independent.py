#!/usr/bin/env python3
"""Separate integer-coordinate census, collapse check and dense exact replay.

No imports from verify.py or predecessor executables. Authored in the same
AI-assisted session; implementation independence is not independent human review.
Hanson Sun / OpenAI Codex, Apache-2.0.
"""
from collections import Counter, defaultdict
from fractions import Fraction
import json
from pathlib import Path
import random

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]
TARGET = ((1,1,1), (1,1,-1), (1,-1,0))


def check(condition, message):
    if not condition:
        raise ValueError(message)


def cover(vertices):
    # Coordinates are (2*Re(z), 2*Im(z)/sqrt(3)); requested rows are real.
    groups = defaultdict(set)
    for p in vertices:
        groups[p[1::2]].add(p[::2])
    answer = 0
    for i, row in enumerate(TARGET):
        if any(tuple(v[k]+2*row[k] for k in range(3)) in group
               for group in groups.values() for v in group):
            answer |= 1 << i
    return answer


def count_paths(repeated=None, sign=1):
    steps = [(j, 2*s, 0) for j in range(3) if j != repeated for s in (-1, 1)]
    if repeated is not None:
        steps += [(repeated, 2*sign, 0), (repeated, -sign, sign), (repeated, -sign, -sign)]
    totals = Counter()
    collapse_count = 0

    def visit(unused, path, current):
        nonlocal collapse_count
        if not unused:
            check(current == (0,)*6, 'open source tour')
            mask = cover(path)
            totals[mask] += 1
            if repeated is not None:
                j = repeated
                triangle = {p[2*j:2*j+2] for p in path}
                check(len(triangle) == 3, 'not three triangle vertices')
                edges = [(a,b) for a in triangle for b in triangle
                         if b[0]-a[0] == 2 and b[1] == a[1]]
                check(len(edges) == 1, 'real side is not unique')
                low, high = edges[0]
                # Merge the third vertex into low. Subtract the initial image.
                images = {p: int(p == high) for p in triangle}
                start = images[(0,0)]
                reduced = []
                for p in path:
                    q = list(p)
                    q[2*j] = 2*(images[p[2*j:2*j+2]] - start)
                    q[2*j+1] = 0
                    reduced.append(tuple(q))
                changes = [tuple(b[k]-a[k] for k in range(6))
                           for a,b in zip(reduced, reduced[1:]) if a != b]
                expected = {tuple(2*s if k == 2*j else 0 for k in range(6))
                            for j in range(3) for s in (-1,1)}
                check(len(changes) == 6 and set(changes) == expected, 'collapse is not a signed six-step tour')
                check(mask & ~cover(reduced) == 0, 'collapse lost a required real difference')
                collapse_count += 1
            return
        for k in range(len(steps)):
            if unused & (1 << k):
                j, a, b = steps[k]
                following = list(current)
                following[2*j] += a
                following[2*j+1] += b
                following = tuple(following)
                visit(unused ^ (1 << k), path + [following], following)

    visit((1 << len(steps))-1, [(0,)*6], (0,)*6)
    return {str(k):v for k,v in sorted(totals.items())}, collapse_count


# Independent arithmetic: a+b*sqrt(-3), with exact rational a,b.
def plus(x, y):
    return x[0]+y[0], x[1]+y[1]


def times(x, y):
    return x[0]*y[0]-3*x[1]*y[1], x[0]*y[1]+x[1]*y[0]


def minus(x):
    return -x[0], -x[1]


def conjugate(x):
    return x[0], -x[1]


def matrix_vector(matrix, vector):
    out = []
    for row in matrix:
        acc = (0,0)
        for coefficient, value in zip(row, vector):
            acc = plus(acc, times(coefficient, value))
        out.append(acc)
    return out


def run_dense(program, incoming, matrices):
    state = [list(v) for v in incoming]
    for kind, index, scalar in program:
        if kind == 'Z':
            state[6] = [times(scalar, v) for v in state[6]]
            continue
        source, target = (index, 6) if kind == 'B' else (6, 3+index)
        delta = matrix_vector(matrices[kind+str(index)], state[source])
        state[target] = [plus(old, times(scalar, d)) for old,d in zip(state[target], delta)]
    return state


def desired(incoming, matrices):
    out = [list(v) for v in incoming]
    for i in range(3):
        for j in range(3):
            v = matrix_vector(matrices['A'+str(i)], matrix_vector(matrices['B'+str(j)], incoming[j]))
            out[3+i] = [plus(old, times((TARGET[i][j],0), value)) for old,value in zip(out[3+i],v)]
    return out


def dense_checks():
    data = json.loads((REPO/'research/weighted-signed-connector-seed58/CERTIFICATE.json').read_text())
    rng = random.Random(39)
    cases = 0
    noncommuting_banks = 0
    for width in (2,3):
        matrices = {name:[[(rng.randrange(-2,3), rng.randrange(-1,2)) for _ in range(width)]
                           for _ in range(width)] for name in data['witnesses']}
        basis = [[(int(i==j),0) for i in range(width)] for j in range(width)]
        check(any(matrix_vector(matrices['A0'], matrix_vector(matrices['B0'],v)) !=
                  matrix_vector(matrices['B0'], matrix_vector(matrices['A0'],v)) for v in basis),
              'dense controls need noncommuting maps')
        noncommuting_banks += 1
        inputs = []
        for k in range(7*width):
            rows = [[(0,0)]*width for _ in range(7)]
            rows[k//width][k%width] = (1,0)
            inputs.append(rows)
        inputs.append([[(rng.randrange(-3,4),rng.randrange(-3,4)) for _ in range(width)] for _ in range(7)])
        for raw in data['witnesses'].values():
            word = [(k,j,(s,0)) for k,j,s in raw]
            phase = (Fraction(-1,7), Fraction(4,7))
            p = (1,0)
            gauged = []
            for kind,j,c in word:
                p = times(p,phase)
                gauged += [('Z',0,phase), (kind,j,times(c,p if kind=='B' else conjugate(p)))]
            gauged.append(('Z',0,conjugate(p)))
            for program in (word,gauged):
                undo = [(k,j,conjugate(c) if k=='Z' else minus(c)) for k,j,c in reversed(program)]
                for incoming in inputs:
                    out = run_dense(program,incoming,matrices)
                    check(out == desired(incoming,matrices), 'dense arbitrary-dirty endpoint failed')
                    check(run_dense(undo,out,matrices) == incoming, 'dense inverse failed')
                    cases += 1
    return cases,noncommuting_banks


def main():
    receipt = json.loads((PACKAGE/'CERTIFICATE.json').read_text())
    check(receipt['matrix'] == [list(row) for row in TARGET], 'wrong target')
    histogram, _ = count_paths()
    check(histogram == receipt['signed_census']['row_mask_histogram'], 'signed census mismatch')
    check(sum(histogram.values()) == 720 and histogram.get('7',0)==0, 'signed coverage failed')
    collapsed = 0
    for column in range(3):
        for sign in (-1,1):
            histogram,n = count_paths(column,sign)
            check(histogram == receipt['unit_triangle_censuses'][str(column)+':'+str(sign)]['row_mask_histogram'],
                  'unit triangle census mismatch')
            check(sum(histogram.values()) == 5040 and histogram.get('7',0)==0, 'unit triangle coverage failed')
            collapsed += n
    cases,banks = dense_checks()
    check(collapsed==30240, 'incomplete triangle collapse coverage')
    print('PASS_INDEPENDENT_UNIT_PHASE signed_paths=720 triangle_collapses='+str(collapsed)
          +' dense_forward_inverse_pairs='+str(cases)+' noncommuting_banks='+str(banks))


if __name__ == '__main__':
    main()
