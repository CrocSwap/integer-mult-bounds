"""Independent truth-table census; imports no primary search code. Apache-2.0.

Sagar Thakrar, with substantial OpenAI Codex assistance.
"""
from collections import Counter, deque
from itertools import combinations, permutations, product


def census(rows, pool):
    # State is the entire bijection on the eight possible three-bit row values.
    identity = tuple(range(8))
    distances = {identity: 0}
    queue = deque([identity])
    generators = tuple(permutations(range(3), 2))
    while queue:
        state = queue.popleft()
        for a, b in generators:
            child = tuple(value ^ (((value >> a) & 1) << b) for value in state)
            if child not in distances:
                distances[child] = distances[state] + 1
                queue.append(child)
    # Enumerate all 512 binary matrices separately, using literal dot products.
    tables = {}
    for bits in product((0, 1), repeat=9):
        matrix = tuple(tuple(bits[3*i+j] for j in range(3)) for i in range(3))
        table = tuple(sum((sum(((x >> i) & 1) * matrix[i][j] for i in range(3)) % 2) << j
                          for j in range(3)) for x in range(8))
        if len(set(table)) == 8:
            key = tuple(sum(matrix[i][j] << i for i in range(3)) for j in range(3))
            tables[key] = table
    if len(tables) != 168 or set(tables.values()) != set(distances):
        raise ValueError("independent GL3 truth tables")
    patterns = Counter()
    by_pattern = {}
    for triple in combinations(pool, 3):
        counts = [0] * 8
        for row in rows:
            counts[sum(1 << i for i, h in enumerate(triple) if h in row)] += 1
        key = tuple(counts)
        patterns[key] += 1
        by_pattern.setdefault(key, []).append(triple)
    histogram, positive = Counter(), []
    for counts, multiplicity in patterns.items():
        old = sum(count * bin(i).count("1") for i, count in enumerate(counts))
        for state, table in sorted(tables.items()):
            reads = sum(count * bin(table[i]).count("1") for i, count in enumerate(counts))
            length = distances[table]
            gain = old - reads - 2 * length
            histogram[gain] += multiplicity
            if gain > 0:
                positive.extend({"helpers": list(triple), "state": list(state), "gain": gain,
                                 "shortest_length": length} for triple in by_pattern[counts])
    positive.sort(key=lambda x: (x["helpers"], x["state"]))
    return {"histogram": dict(sorted(histogram.items())), "positive": positive,
            "cases": sum(histogram.values())}
