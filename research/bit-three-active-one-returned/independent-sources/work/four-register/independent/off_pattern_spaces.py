"""List scalar idempotents in binary off-diagonal spaces of rank at most three."""
from itertools import permutations
from pathlib import Path
import json
from time import time

ROOT = Path(__file__).parent
OFF = sum(1 << (4*i+j) for i in range(4) for j in range(4) if i != j)

def outer(x,y):
    return sum(((x>>i)&1)*((y>>j)&1) << (4*i+j) for i in range(4) for j in range(4))

projectors = [(x,y,outer(x,y)) for x in range(1,16) for y in range(1,16) if (x&y).bit_count()%2]
patterns = sorted(set(m&OFF for x,y,m in projectors)-{0})

def strong(space):
    edges = 0
    for m in space:
        edges |= m
    for i in range(4):
        seen = 1 << i
        while True:
            nxt = seen
            for j in range(4):
                if seen >> j & 1:
                    nxt |= (edges >> (4*j)) & 15
            if nxt == seen:break
            seen = nxt
        if seen != 15:return False
    return True

def canonical(space):
    return min(tuple(sorted(sum(((m>>(4*i+j))&1) << (4*p[i]+p[j]) for i in range(4) for j in range(4)) for m in space)) for p in permutations(range(4)))

start = time()
spaces = {(0,)}
levels = []
for dimension in range(1,4):
    nxt = set()
    for space in spaces:
        for v in patterns:
            if v not in space:
                nxt.add(tuple(sorted(space + tuple(x^v for x in space))))
    spaces = nxt
    irreducible = [s for s in spaces if strong(s)]
    representatives = sorted(set(canonical(s) for s in irreducible))
    record = dict(dimension=dimension, spaces=len(spaces), irreducible_spaces=len(irreducible), representatives=[dict(space=s, projectors=[(x,y) for x,y,m in projectors if m&OFF in s]) for s in representatives])
    levels.append(record)
    print(json.dumps(dict(dimension=dimension, spaces=len(spaces), irreducible=len(irreducible), classes=len(representatives), seconds=time()-start)),flush=True)
(ROOT/'off-pattern-spaces.json').write_text(json.dumps(dict(projectors=len(projectors), off_patterns=len(patterns), levels=levels),indent=2)+'\n')
