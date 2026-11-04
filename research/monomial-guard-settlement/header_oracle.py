"""Shortest elementary words on whole invertible matrices; literal guard tests."""
from collections import Counter, deque
from hashlib import sha256
from itertools import permutations, product as choices
from math import prod
from pathlib import Path
import json, sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from literal import complement, product, reduce_matrix
from monomial import flat_rows
from settlement import Field


def matrix_distances(f, m):
    start = set()
    for perm in permutations(range(m)):
        for weights in choices(range(1, f.q), repeat=m):
            start.add(tuple(weights[i] if j == perm[i] else 0 for i in range(m) for j in range(m)))
    dist = dict.fromkeys(start, 0)
    queue = deque(start)
    while queue:
        g = queue.popleft()
        cost = dist[g] + 1
        for i in range(m):
            off = i*m
            old = g[off:off+m]
            for j in range(m):
                if i == j:
                    continue
                src = g[j*m:(j+1)*m]
                for a in range(1, f.q):
                    row = tuple(f.add[x][f.mul[a][y]] for x,y in zip(old,src))
                    nxt = g[:off] + row + g[off+m:]
                    if nxt not in dist:
                        dist[nxt] = cost
                        queue.append(nxt)
    if len(dist) != prod(f.q**m - f.q**i for i in range(m)):
        raise ValueError("whole GL size")
    return dist


def passes(f, g, inv, mats):
    for mat in mats:
        transformed = product(f, product(f, g, mat), inv)
        for n in range(1, len(g)):
            if reduce_matrix(f, [row[:n] for row in transformed[:n]])[0] == 0:
                return False
    return True


def examples(f, m):
    if f.q == 2:
        u = (1,)*m
        coordinate = [tuple(int(i==j) for i in range(m)) for j in range(m)]
        return [("exclusive coordinate guards", u, coordinate),
                ("three equal weighted charges", (1,1,1,0), flat_rows(f,(1,1,1,0),[(0,0,0,1)])),
                ("already one axis", (0,0,0,1), [(1,0,0,1),(0,1,0,1)])]
    a = f.neg[1]
    return [("anchored cancelling pair",(1,1,1),flat_rows(f,(0,0,1),[(1,a,0)])),
            ("separated carrier",(1,0,1),flat_rows(f,(0,0,1),[(0,1,0)])),
            ("normalized coordinate rows",(1,1,1),[(1,0,0),(0,1,0),(0,0,1)])]


def scan(q, m):
    f = Field(q)
    cases = examples(f, m)
    families = [[complement(f, u, row) for row in rows] for _,u,rows in cases]
    dist = matrix_distances(f, m)
    cells = [Counter() for _ in cases]
    digest = sha256()
    for word in sorted(dist):
        g = tuple(word[i:i+m] for i in range(0,m*m,m))
        det, inv = reduce_matrix(f, g, inverse=True)
        if not det:
            raise ValueError("singular matrix in Cayley graph")
        mask = 0
        for j, mats in enumerate(families):
            if passes(f, g, inv, mats):
                cells[j][dist[word]] += 1
                mask |= 1 << j
        digest.update(bytes((*word, dist[word], mask)))
    return dict(q=q,m=m,headers=len(dist),matrix_costs=dict(sorted(Counter(dist.values()).items())),
                cases=[dict(name=name,minimum=min(c),passing_by_cost=dict(sorted(c.items())))
                       for (name,_,_),c in zip(cases,cells)], matrix_cost_mask_sha256=digest.hexdigest())


def collect():
    return [scan(2,4), scan(3,3)]


if __name__ == "__main__":
    extended = sys.argv[1:] == ["--extended"]
    if sys.argv[1:] not in ([], ["--extended"]):
        raise ValueError("unknown mode")
    data = scan(4,3) if extended else collect()
    name = "GL3-F4.json" if extended else "MATRIX-DISTANCES.json"
    if json.loads(json.dumps(data)) != json.loads((HERE/name).read_text(encoding="utf8")):
        raise ValueError("frozen whole-header distances")
    print(json.dumps(dict(status="PASS_SETTLEMENT_WHOLE_HEADERS",fixture=name,
                          headers=data["headers"] if extended else sum(x["headers"] for x in data))))
