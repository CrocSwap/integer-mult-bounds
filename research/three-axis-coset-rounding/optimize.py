"""Minimise all fixed-coset centre errors by a complete radius-six census."""
from collections import Counter
import struct
from kernel import matrix, multiply, reversed_pairs, need


def optimize():
    rows = matrix();columns = list(zip(*rows))
    defects = list(zip(*[[4*(i == j)-rows[i][j] for j in range(16)] for i in range(16)]))
    best = {};x = [0]*16;y = [0]*16;d = [0]*16;count = 0
    def walk(index,room):
        nonlocal count
        if index == 16:
            count += 1
            key = tuple(v % 4 for v in y)
            candidate = (sum(v*v for v in d),6-room,tuple(x))
            if key not in best or candidate < best[key]:
                best[key] = candidate
            return
        for a in range(-2,3):
            if a*a > room:
                continue
            x[index] = a
            for j in range(16):
                y[j] += a*columns[index][j];d[j] += a*defects[index][j]
            walk(index+1,room-a*a)
            for j in range(16):
                y[j] -= a*columns[index][j];d[j] -= a*defects[index][j]
        x[index] = 0
    walk(0,6)
    keys = set(best)
    need(len(keys) == 64, 'All 64 cosets')
    for key in keys:
        for column in columns:
            need(tuple((a+b) % 4 for a,b in zip(key,column)) in keys, 'Coset closure under every generator')
    records = []
    for key,(cost,norm,center) in sorted(best.items()):
        records.append(dict(key=key,center=center,cost16=cost,norm2=norm))
    centers = [r['center'] for r in records]
    images = [multiply(rows,c) for c in centers]
    sums = [(sum(c[::2]),sum(c[1::2])) for c in centers]
    costs = [[sum((4*a-b)**2 for a,b in zip(centers[j],images[i])) for j in range(64)] for i in range(64)]
    edges = [[j for j in range(64) if sums[i] == sums[j] and costs[i][j] <= 64
              and ((i == 0) == (j == 0))] for i in range(64)]
    matched = {}
    def visit(i,seen):
        for j in edges[i]:
            if j in seen: continue
            seen.add(j)
            if j not in matched or visit(matched[j],seen):
                matched[j] = i
                return True
        return False
    for i in range(64):
        need(visit(i,set()),'Perfect sum-preserving coset matching')
    inverse = [matched[j] for j in range(64)]
    permutation = [inverse.index(i) for i in range(64)]
    need(all(permutation[permutation[permutation[permutation[i]]]] == i for i in range(64)),
         'The constructed permutation has fourth power one')
    blob = bytearray()
    for i,r in enumerate(records):
        plus = tuple(4*a-b for a,b in zip(centers[permutation[i]],images[i]))
        minus = tuple(4*a-b for a,b in zip(centers[inverse[i]],reversed_pairs(images[i])))
        need(max(sum(v*v for v in plus),sum(v*v for v in minus)) <= 64,'Both signs meet sharp uniform bound')
        blob.extend(struct.pack('16B32b',*r['key'],*plus,*minus))
    return dict(enumerated_vectors=count,center_costs16=dict(sorted(Counter(v[0] for v in best.values()).items())),
                centers=records,permutation=permutation,inverse=inverse,
                permuted_costs16=dict(sorted(Counter(costs[i][j] for i,j in enumerate(permutation)).items()))),bytes(blob)
