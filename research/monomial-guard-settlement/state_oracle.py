"""Multi-source shortest paths on raw vectors, independent of the settlement rule."""
from collections import Counter, deque
from functools import lru_cache
from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json,sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from literal import identity_pass
from settlement import Field, partition


def tuples(f, m, k, binary):
    vectors = list(f.vectors(m))
    for u in vectors:
        if not any(u):
            continue
        eligible = [row for row in vectors if f.dot(u, row) == int(binary)]
        for rows in product(eligible, repeat=k):
            if not binary and len(f.basis(rows)) != k:
                continue
            yield u + sum(rows, ())


def neighbors(f, state, m, k):
    for i in range(m):
        for j in range(m):
            if i == j:
                continue
            for a in range(1, f.q):
                v = list(state)
                v[i] = f.add[state[i]][f.mul[a][state[j]]]
                for t in range(1, k + 1):
                    pos = m*t
                    v[pos+j] = f.add[state[pos+j]][f.mul[f.neg[a]][state[pos+i]]]
                yield tuple(v)


def charge_key(f, state, m, k):
    weighted = [tuple(f.mul[state[i]][state[m*j+i]] for j in range(1, k + 1))
                for i in range(m)]
    return tuple(sorted(v for v in weighted if any(v)))


def seeds(f, states, m, k, binary):
    if not binary:
        return {s for s in states if all(not s[i] or all(not s[j*m+i] for j in range(1,k+1))
                                         for i in range(m))}
    initial = set()
    orders = list(permutations(range(m)))
    for s in states:
        rows = [s[j*m:(j+1)*m] for j in range(1,k+1)]
        if identity_pass(f, s[:m], rows):
            for pi in orders:
                initial.add(tuple(s[j*m+i] for j in range(k+1) for i in pi))
    return initial


def census(q, m, k, binary):
    f = Field(q)
    states = set(tuples(f, m, k, binary))
    initial = seeds(f, states, m, k, binary)
    distance = dict.fromkeys(initial, 0)
    queue = deque(initial)
    while queue:
        s = queue.popleft()
        level = distance[s] + 1
        for nxt in neighbors(f, s, m, k):
            if nxt not in distance:
                distance[nxt] = level
                queue.append(nxt)
    if distance.keys() != states:
        raise ValueError("raw state-space coverage")

    @lru_cache(None)
    def predicted(key):
        values = list(key) + ([(1,)*k] if binary else [])
        return len(key) - len(partition(f, values))

    digest = sha256()
    for s in sorted(states):
        if predicted(charge_key(f, s, m, k)) != distance[s]:
            raise ValueError("raw BFS distance vs partition")
        digest.update(bytes((*s, distance[s])))
    return dict(q=q, m=m, rows=k, goal="guard" if binary else "separation",
                states=len(states), shortest_distance_histogram=dict(sorted(Counter(distance.values()).items())),
                state_distance_sha256=digest.hexdigest())


def collect():
    separation = [(2,4,1),(2,6,1),(3,4,1),(3,5,1),(4,4,1),(5,3,1),
                  (2,4,2),(3,3,2),(4,3,2)]
    binary = [(3,1),(3,3),(4,2),(4,3),(4,4)]
    return ([census(q,m,k,False) for q,m,k in separation] +
            [census(2,m,k,True) for m,k in binary])


if __name__ == "__main__":
    actual = collect()
    if json.loads(json.dumps(actual)) != json.loads((HERE/"RAW-STATES.json").read_text(encoding="utf8")):
        raise ValueError("frozen raw state census")
    print(json.dumps(dict(status="PASS_GUARD_RAW_DISTANCES", cases=len(actual),
                          states=sum(x["states"] for x in actual))))
