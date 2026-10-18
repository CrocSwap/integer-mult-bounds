#!/usr/bin/env python3
"""Independent slow crosscheck: ordinary Python sets and A2 vector sums.

No imports from verify.py. Does not use bit masks or Gram determinants.
"""
import collections
import itertools
import json
from pathlib import Path


def sign_normalize(v):
    first_nonzero = next(c for c in v if c)
    return tuple(-x for x in v) if first_nonzero < 0 else tuple(v)


def dot(u, v):
    return sum(x*y for x,y in zip(u,v))


def run():
    root_lines = set()
    for pos in itertools.combinations(range(8), 2):
        for signs in itertools.product((2,-2), repeat=2):
            arr = [0]*8
            for coordinate, value in zip(pos, signs):
                arr[coordinate] = value
            root_lines.add(sign_normalize(arr))
    for pattern in range(256):
        if pattern.bit_count() % 2:
            continue
        root_lines.add(sign_normalize([(-1 if (pattern>>i)&1 else 1) for i in range(8)]))
    lines = sorted(root_lines)
    assert len(lines) == 120
    neighbors = [{j for j, w in enumerate(lines) if i != j and abs(dot(v,w)) == 4}
                 for i, v in enumerate(lines)]
    assert all(len(v)==56 for v in neighbors)
    gather = [v|{i} for i,v in enumerate(neighbors)]
    index = {v:i for i,v in enumerate(lines)}
    a2 = set()
    for i in range(120):
        for j in range(i+1,120):
            if j in neighbors[i]:
                if dot(lines[i],lines[j])>0:
                    r = [x-y for x,y in zip(lines[i],lines[j])]
                else:
                    r = [x+y for x,y in zip(lines[i],lines[j])]
                third = index[sign_normalize(r)]
                assert third != i and third != j
                a2.add(tuple(sorted((i,j,third))))
    assert len(a2) == 1120
    result = collections.Counter()
    for i,j,k in itertools.combinations(range(120),3):
        edges = int(j in neighbors[i]) + int(k in neighbors[i]) + int(k in neighbors[j])
        rank = 2 if (i,j,k) in a2 else 3
        common_open = len(neighbors[i].intersection(neighbors[j],neighbors[k]))
        common_closed = len(gather[i].intersection(gather[j],gather[k]))
        united = len(gather[i].union(gather[j],gather[k]))
        key = f'{edges}edges:rank{rank}:open{common_open}:closed{common_closed}:union{united}'
        result[key]+=1
    actual = json.loads(Path(__file__).with_name('RESULT.json').read_text())['triples']
    assert dict(result) == actual, (result,actual)
    print('PASS_E8_A2_INDEPENDENT_SETS: ' + str(sum(result.values())) + ' triples; A2=' + str(len(a2)))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Do not run proof checks under optimized Python')
    run()
