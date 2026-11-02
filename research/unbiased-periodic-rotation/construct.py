#!/usr/bin/env python3
"""Construct five exact periodic lattice rotation tables. Apache-2.0."""
import json


def coset(point):
    """Class in Z^2 / [[3,-4],[4,3]] Z^2."""
    x, y = point
    return ((3 * x + 4 * y) % 25, (-4 * x + 3 * y) % 25)


def weighted_edges():
    """Return a five-regular bipartite multigraph and its literal outputs."""
    keys = sorted({coset((x, y)) for x in range(25) for y in range(25)})
    if len(keys) != 25:
        raise ValueError("incorrect quotient size")
    weights = [[0] * 25 for _ in range(25)]
    outputs = [[None] * 25 for _ in range(25)]
    for i in range(25):
        x, y = divmod(i, 5)
        u, a = divmod(3 * x - 4 * y, 5)
        v, b = divmod(4 * x + 3 * y, 5)
        both = min(a, b) if a in (1, 4) else max(0, a + b - 5)
        counts = ((0, 0, 5 - a - b + both), (1, 0, a - both),
                  (0, 1, b - both), (1, 1, both))
        for dx, dy, count in counts:
            if count > 0:
                point = (u + dx, v + dy)
                j = keys.index(coset(point))
                if outputs[i][j] is not None:
                    raise ValueError("two outputs alias in one row")
                weights[i][j] = count
                outputs[i][j] = point
    if any(sum(row) != 5 for row in weights):
        raise ValueError("incorrect input degree")
    if any(sum(weights[i][j] for i in range(25)) != 5 for j in range(25)):
        raise ValueError("incorrect output degree")
    return weights, outputs


def matching(weights):
    """Find one perfect matching by at most 25 bounded augmentations."""
    owners = [-1] * 25
    assigned = [-1] * 25
    for root in range(25):
        queue = [root]
        seen = {root}
        parent = [-1] * 25
        free = -1
        for step in range(25):
            if step == len(queue) or free >= 0:
                break
            row = queue[step]
            for col in range(25):
                if weights[row][col] == 0 or parent[col] >= 0:
                    continue
                parent[col] = row
                if owners[col] < 0:
                    free = col
                    break
                other = owners[col]
                if other not in seen:
                    seen.add(other)
                    queue.append(other)
        if free < 0:
            raise ValueError("regular graph has no augmenting path")
        for _ in range(25):
            row = parent[free]
            previous = assigned[row]
            assigned[row], owners[free] = free, row
            if previous < 0:
                break
            free = previous
        else:
            raise ValueError("augmentation exceeds row count")
    if sorted(assigned) != list(range(25)):
        raise ValueError("matching is not a permutation")
    return assigned


def construct():
    weights, outputs = weighted_edges()
    tables = []
    for _ in range(5):
        permutation = matching(weights)
        table = []
        for i, j in enumerate(permutation):
            if weights[i][j] <= 0 or outputs[i][j] is None:
                raise ValueError("matching selected an absent edge")
            weights[i][j] -= 1
            table.append(list(outputs[i][j]))
        tables.append(table)
    if any(value != 0 for row in weights for value in row):
        raise ValueError("decomposition left an edge")
    return {"schema_version": 1, "tables": tables}


if __name__ == "__main__":
    print(json.dumps(construct(), indent=2))
