"""Exact directed contraction compiler; no third-party implementation copied.

Tekalign, substantial OpenAI Codex assistance. Apache-2.0.
Uses the classical Chu-Liu/Edmonds minimum-arborescence method. The emitted
cut/word certificate is checked without importing this implementation.
"""
from fractions import Fraction


def require(ok, message):
    if not ok:
        raise ValueError(message)


def prices(mu, add):
    q = len(mu)
    require(q >= 1 and len(add) == q and all(len(row) == q for row in add), 'tariff shape')
    def exact(x):
        require(type(x) in (int, Fraction) and x > 0, 'positive exact tariff')
        return Fraction(x)
    roots = [exact(x) for x in mu]
    edges = [[None if i == j else exact(add[i][j]) for j in range(q)] for i in range(q)]
    require(all(add[i][i] is None for i in range(q)), 'no self ADD tariff')
    return roots, edges


def compile_word(parents):
    q = len(parents)
    children = [[] for _ in parents]
    roots = []
    for i, j in enumerate(parents):
        (roots if j is None else children[j]).append(i)
    # Iterative postorder; the graph root is not a physical row.
    prep = []
    todo = [(i, False) for i in reversed(roots)]
    while todo:
        i, returned = todo.pop()
        if returned:
            if parents[i] is not None:
                prep.append(['ADD', i, parents[i]])
        else:
            todo.append((i, True))
            todo.extend((j, False) for j in reversed(children[i]))
    require(len(prep)+len(roots) == q, 'spanning forest')
    return prep+[['P', i] for i in roots]+list(reversed(prep))


def synthesize(mu, add):
    mu, add = prices(mu, add)
    q = len(mu)
    # Vertices are disjoint bit masks; 0 is a graph-only root.
    nodes = [0]+[1 << i for i in range(q)]
    # Edges: source cluster, destination cluster, residual cost, original key.
    edges = [(0, 1 << i, mu[i], (None, i)) for i in range(q)]
    edges += [(1 << j, 1 << i, 2*add[i][j], (j, i))
              for i in range(q) for j in range(q) if i != j]
    dual, stages = {}, []
    while True:
        incoming = {}
        for edge in edges:
            u, v, weight, key = edge
            tie = (weight, -1 if key[0] is None else key[0], key[1])
            if v not in incoming or tie < incoming[v][0]:
                incoming[v] = (tie, edge)
        require(all(v in incoming for v in nodes if v), 'root reachability')
        chosen = {v:incoming[v][1] for v in nodes if v}
        for v, edge in chosen.items():
            dual[v] = dual.get(v, Fraction(0))+edge[2]
        reduced = [(u,v,w-chosen[v][2],key) for u,v,w,key in edges]
        # Follow chosen parents to find one cycle, deterministically.
        cycle = None
        done = {0}
        for start in nodes:
            path, index, v = [], {}, start
            while v not in done and v not in index:
                index[v] = len(path)
                path.append(v)
                v = chosen[v][0]
            if v in index:
                cycle = set(path[index[v]:])
                break
            done.update(path)
        if cycle is None:
            selected = [edge[3] for edge in chosen.values()]
            break
        merged = 0
        for v in cycle:
            merged |= v
        stages.append((cycle, merged, chosen))
        nodes = [v for v in nodes if v not in cycle]+[merged]
        edges = []
        for u,v,w,key in reduced:
            u = merged if u in cycle else u
            v = merged if v in cycle else v
            if u != v:
                edges.append((u,v,w,key))
    for cycle, merged, chosen in reversed(stages):
        # Exactly one selected original arc enters the contracted cluster.
        entering = [(j,i) for j,i in selected
                    if merged & (1 << i) and (j is None or not merged & (1 << j))]
        require(len(entering) == 1, 'unique contracted entry')
        destination = entering[0][1]
        for v in cycle:
            if not v & (1 << destination):
                selected.append(chosen[v][3])
    require(len(selected) == q, 'one parent per row')
    parents = [None]*q
    for j,i in selected:
        parents[i] = j
    cost = sum(mu[i] if j is None else 2*add[i][j] for i,j in enumerate(parents))
    cuts = [{'rows':[i for i in range(q) if mask & (1 << i)], 'price':str(value)}
            for mask,value in sorted(dual.items()) if value]
    return dict(schema_version=1, q=q, parents=parents, cuts=cuts, cost=str(cost),
                word=compile_word(parents))


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tariffs', type=Path)
    args = parser.parse_args()
    def unique(pairs):
        result = {}
        for k,v in pairs:
            require(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    data = json.loads(args.tariffs.read_bytes(), object_pairs_hook=unique)
    require(set(data) == {'mu','add'}, 'tariff fields')
    def parse(v):
        require(type(v) in (int,str), 'exact JSON tariff')
        return Fraction(v)
    mu = [parse(v) for v in data['mu']]
    add = [[None if v is None else parse(v) for v in row] for row in data['add']]
    print(json.dumps(synthesize(mu,add), sort_keys=True, indent=2))
