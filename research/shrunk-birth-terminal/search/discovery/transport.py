"""Integer maximum-reward capacitated bipartite transport for discovery.

This optimizes only the supplied finite integer surrogate. Every selected
physical merge and the final complete moment need separate certification.
"""
import heapq


def transport(left_capacity, right_capacity, edges):
    nl, nr = len(left_capacity), len(right_capacity)
    source, sink = nl+nr, nl+nr+1
    graph = [[] for _ in range(sink+1)]

    def add(u, v, capacity, cost):
        f = [v, len(graph[v]), capacity, cost]
        b = [u, len(graph[u]), 0, -cost]
        graph[u].append(f)
        graph[v].append(b)
        return f

    for i, c in enumerate(left_capacity):
        assert c >= 0
        add(source, i, c, 0)
    for j, c in enumerate(right_capacity):
        assert c >= 0
        add(nl+j, sink, c, 0)
    tracked = []
    potential = [0]*(sink+1)
    for i, j, reward in edges:
        assert reward > 0 and 0 <= i < nl and 0 <= j < nr
        c = min(left_capacity[i], right_capacity[j])
        edge = add(i, nl+j, c, -reward)
        tracked.append((i, j, c, reward, edge))
        potential[nl+j] = min(potential[nl+j], -reward)
    potential[sink] = min(potential[nl:nl+nr], default=0)
    sent, gain, iterations = 0, 0, 0
    while True:
        dist = [None]*(sink+1)
        previous = [None]*(sink+1)
        dist[source] = 0
        queue = [(0, source)]
        while queue:
            du, u = heapq.heappop(queue)
            if dist[u] != du:
                continue
            for idx, (v, back, capacity, cost) in enumerate(graph[u]):
                if not capacity:
                    continue
                reduced = cost + potential[u]-potential[v]
                assert reduced >= 0, ('negative reduced cost', u, v, reduced)
                nd = du+reduced
                if dist[v] is None or nd < dist[v]:
                    dist[v] = nd
                    previous[v] = u, idx
                    heapq.heappush(queue, (nd, v))
        if dist[sink] is None:
            break
        path_cost = dist[sink]+potential[sink]-potential[source]
        if path_cost >= 0:
            break
        for u, d in enumerate(dist):
            if d is not None:
                potential[u] += d
        amount = sum(left_capacity)
        v = sink
        while v != source:
            u, idx = previous[v]
            amount = min(amount, graph[u][idx][2])
            v = u
        assert amount > 0
        v = sink
        while v != source:
            u, idx = previous[v]
            e = graph[u][idx]
            e[2] -= amount
            graph[v][e[1]][2] += amount
            v = u
        sent += amount
        gain -= amount*path_cost
        iterations += 1
    flows = [(i,j,c-edge[2]) for i,j,c,reward,edge in tracked if c-edge[2]]
    assert sum(n for i,j,n in flows) == sent
    assert sum((c-edge[2])*reward for i,j,c,reward,edge in tracked) == gain
    assert all(sum(n for k,j,n in flows if k == i) <= c for i,c in enumerate(left_capacity))
    assert all(sum(n for i,k,n in flows if k == j) <= c for j,c in enumerate(right_capacity))
    return flows, dict(flow=sent, integer_surrogate_gain=gain, augmentations=iterations,
                      classes=[nl,nr], eligible_class_edges=len(edges))


if __name__ == '__main__':
    from random import Random
    rng = Random(20261009)
    cases = 0
    for nl in range(1,5):
        for nr in range(1,5):
            for trial in range(15):
                cap = [rng.randrange(1,3) for _ in range(nr)]
                edges = [(i,j,rng.randrange(1,50)) for i in range(nl) for j in range(nr) if rng.randrange(3)]
                rewards = {(i,j):w for i,j,w in edges}
                def brute(i, remaining):
                    if i == nl:
                        return 0
                    result = brute(i+1,remaining)
                    for j in range(nr):
                        if remaining[j] and (i,j) in rewards:
                            new = remaining[:]
                            new[j] -= 1
                            result = max(result, rewards[i,j]+brute(i+1,new))
                    return result
                flows, receipt = transport([1]*nl,cap,edges)
                assert receipt['integer_surrogate_gain'] == brute(0,cap)
                cases += 1
    print('PASS',cases,'independent exhaustive small transport comparisons')
