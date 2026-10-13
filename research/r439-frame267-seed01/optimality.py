"""Independent breadth-first proof of the fixed integer-transfer minimum.

Uses flat integer matrices, breadth-first layers and no search.py imports.
The graph contains every possible last positive ADD, including repeated writes.
Ross Richardson, substantial OpenAI Codex assistance; Apache-2.0.
"""


def check_minimum(matrix, claimed):
    if type(claimed) is not int or not 0 <= claimed <= 21:
        raise ValueError('invalid claimed distance')
    if len(matrix) != 6 or any(len(row) != 6 for row in matrix):
        raise ValueError('matrix shape')
    if any(type(x) is not int or not 0 <= x <= 255 for row in matrix for x in row):
        raise ValueError('matrix entries')
    target = bytes(x for row in matrix for x in row)
    identity = bytes(int(i == j) for i in range(6) for j in range(6))
    frontier, seen, layers = {target}, {target}, [1]
    edges = 0
    for depth in range(claimed + 1):
        if identity in frontier:
            if depth != claimed:
                raise ValueError('claimed minimum exceeds independent distance')
            return {'minimum': depth, 'layers': layers, 'visited_states': len(seen),
                    'edges_from_completed_layers': edges,
                    'completed_expansion_depths': list(range(depth))}
        if depth == claimed:
            raise ValueError('claimed minimum is below independent distance')
        following = set()
        for state in frontier:
            # Candidate last gate d += s; removing it must leave >= I entrywise.
            for destination in range(0, 36, 6):
                for source in range(0, 36, 6):
                    if destination == source:
                        continue
                    reduced = []
                    for col in range(6):
                        entry = state[destination + col] - state[source + col]
                        if entry < int(col == destination // 6):
                            break
                        reduced.append(entry)
                    if len(reduced) != 6:
                        continue
                    edges += 1
                    previous = state[:destination] + bytes(reduced) + state[destination + 6:]
                    if previous not in seen:
                        seen.add(previous)
                        following.add(previous)
        frontier = following
        layers.append(len(frontier))
        if len(seen) > 1_000_000:
            raise ValueError('independent state budget exceeded')
    raise ValueError('unreachable')
