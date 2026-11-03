"""Exact hypercube preparation for the observable connector contract.

Produced by Nick Petalas. Apache-2.0. The Bellman model is Hanson Sun's
PR1523; hypercube distance transforms and path ranking are classical.
"""

MAX_WIDTH = 8
MAX_STAGES = 256
MAX_PRICE_BITS = 256


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(d, conditions, weights, output_prices):
    require(type(d) is int and 1 <= d <= MAX_WIDTH, "bad width")
    require(len(conditions) <= MAX_STAGES, "stage limit exceeded")
    require(len(weights) == d and all(type(w) is int and w > 0 for w in weights),
            "bad weights")
    require(all(type(a) is int and 0 <= a < 1 << d
                and type(b) is int and b in (0, 1) for a, b in conditions),
            "bad conditions")
    require(output_prices is None or (len(output_prices) == len(conditions)
            and all(type(w) is int and w > 0 for w in output_prices)),
            "bad output prices")
    prices = list(weights) + ([] if output_prices is None else list(output_prices))
    require(all(w.bit_length() <= MAX_PRICE_BITS for w in prices), "price limit exceeded")


def distance_transform(costs, ranks, weights):
    """Return (cost, predecessor path rank, predecessor state) at every mask."""
    size = len(costs)
    require(size == 1 << len(weights) and len(ranks) == size, "bad transform shape")
    labels = [None if c is None else (c, ranks[k], k) for k, c in enumerate(costs)]
    for j, weight in enumerate(weights):
        bit = 1 << j
        for block in range(0, size, 2 * bit):
            for lo in range(block, block + bit):
                hi = lo + bit
                left, right = labels[lo], labels[hi]
                if right is not None:
                    candidate = (right[0] + weight, right[1], right[2])
                    if left is None or candidate < left:
                        labels[lo] = candidate
                if left is not None:
                    candidate = (left[0] + weight, left[1], left[2])
                    if right is None or candidate < right:
                        labels[hi] = candidate
    return labels


def advance(labels, reader, demand, output_price):
    """Impose the read boundary and rank the retained complete path prefixes."""
    size = len(labels)
    costs, ranks, parents = [None] * size, [None] * size, [None] * size
    for k, label in enumerate(labels):
        defect = demand ^ ((reader & k).bit_count() & 1)
        if label is not None and (not defect or output_price is not None):
            penalty = 0 if output_price is None else defect * output_price
            costs[k] = label[0] + penalty
            parents[k] = label[2]
    ordered = sorted((labels[k][1], k) for k in range(size) if costs[k] is not None)
    for rank, (_, k) in enumerate(ordered):
        ranks[k] = rank
    return costs, ranks, parents


def reconstruct(parents, terminal):
    path = [terminal]
    for row in reversed(parents):
        predecessor = row[path[-1]]
        require(predecessor is not None, "broken predecessor chain")
        path.append(predecessor)
    require(path[-1] == 0, "unrestored starting state")
    return list(reversed(path[:-1])) + [0]


def solve(d, conditions, weights, output_prices=None):
    """Preserve PR1523's full returned value on the declared bounded domain."""
    validate(d, conditions, weights, output_prices)
    size = 1 << d
    costs, ranks = [None] * size, [None] * size
    costs[0], ranks[0] = 0, 0
    tables, parents = [list(costs)], []
    for i, (reader, demand) in enumerate(conditions):
        labels = distance_transform(costs, ranks, weights)
        price = None if output_prices is None else output_prices[i]
        costs, ranks, row = advance(labels, reader, demand, price)
        tables.append(list(costs))
        parents.append(row)
    distances = [sum(w for j, w in enumerate(weights) if k >> j & 1)
                 for k in range(size)]
    endings = [(c + distances[k], ranks[k], k)
               for k, c in enumerate(costs) if c is not None]
    require(bool(endings), "infeasible observable demands")
    cost, _, terminal = min(endings)
    path = reconstruct(parents, terminal)
    corrections = [b ^ ((a & k).bit_count() & 1)
                   for (a, b), k in zip(conditions, path)]
    return {"cost": cost, "path": path, "output_corrections": corrections,
            "tables": tables, "weights": list(weights), "output_prices": output_prices}
