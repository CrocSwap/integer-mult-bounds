"""All complete pencils in selected small fields, raw-state shortest paths."""
from collections import Counter, deque
from functools import lru_cache
from hashlib import sha256
from itertools import permutations
from pathlib import Path
import json,sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from literal import identity_pass
from monomial import flat_rows
from settlement import Field, partition, ternary_extra
from state_oracle import neighbors


def distances_to_passing_pencils(f, m):
    vectors = list(f.vectors(m))
    orders = list(permutations(range(m)))
    states, seeds = set(), set()
    for u in vectors:
        if not any(u):
            continue
        normals = [b for b in vectors if f.dot(b,u) == 1]
        slopes = [w for w in vectors if any(w) and f.dot(w,u) == 0]
        for b in normals:
            for w in slopes:
                s = u+b+w
                states.add(s)
                if identity_pass(f,u,flat_rows(f,b,[w])):
                    for order in orders:
                        seeds.add(tuple(s[t*m+i] for t in range(3) for i in order))
    dist = dict.fromkeys(seeds,0)
    queue = deque(seeds)
    while queue:
        s = queue.popleft()
        for nxt in neighbors(f,s,m,2):
            if nxt not in dist:
                dist[nxt] = dist[s]+1
                queue.append(nxt)
    if states != dist.keys():
        raise ValueError("complete pencil state orbit")
    return states,dist


def census(q, m):
    f = Field(q)
    states,dist = distances_to_passing_pencils(f,m)
    @lru_cache(None)
    def separation(key):
        return len(key)-len(partition(f,[(x,) for x in key]))

    counts = Counter()
    hist = Counter()
    digest = sha256()
    largest_gap = 0
    first_gap = None
    for s in sorted(states):
        u,b,w = s[:m],s[m:2*m],s[2*m:]
        x = [f.mul[i][j] for i,j in zip(u,b)]
        y = [f.mul[i][j] for i,j in zip(u,w)]
        lower = separation(tuple(sorted(i for i in y if i)))
        true = dist[s]
        if lower > true:
            raise ValueError("separation lower bound")
        if len([i for i in b if i]) == 1 and all(not bi or not wi for bi,wi in zip(b,w)):
            counts["anchored"] += 1
            if lower != true:
                raise ValueError("anchored complete pencil")
        if q == 3:
            scalar = ternary_extra(x)
            if not any(y):
                counts["separated"] += 1
                if true != scalar:
                    raise ValueError("separated ternary price")
            gap = true-max(lower,scalar)
            if gap < 0:
                raise ValueError("ternary scalar lower bound")
            if gap > largest_gap:
                largest_gap = gap
                first_gap = dict(u=u,b=b,w=w,separation=lower,scalar=scalar,full=true)
        hist[true] += 1
        digest.update(bytes((*s,true)))
    return dict(q=q,m=m,states=len(states),distances=dict(sorted(hist.items())),
                compared=dict(counts),ternary_max_gap=largest_gap if q==3 else None,
                ternary_gap_example=first_gap,state_distance_sha256=digest.hexdigest())


def collect():
    return [census(q,m) for q,m in [(2,4),(3,3),(3,4),(4,3),(5,3)]]


if __name__=="__main__":
    result=collect()
    if json.loads(json.dumps(result)) != json.loads((HERE/"FULL-PENCILS.json").read_text(encoding="utf8")):
        raise ValueError("frozen unrestricted pencil oracle")
    print(json.dumps(dict(status="PASS_COMPLETE_PENCIL_DISTANCES",states=sum(x["states"] for x in result),
                          anchored=sum(x["compared"]["anchored"] for x in result))))
