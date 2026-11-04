"""The fixed-alphabet DP and closed scalar cases of the separation theorem."""
from collections import Counter
from itertools import product


def frequency_blocks(f, values):
    counts = Counter(values)
    symbols = sorted(counts)
    if not symbols:
        return 0
    full = tuple(counts[s] for s in symbols)
    zero = (0,)*len(symbols[0])
    sums = {}
    best = {}
    for state in product(*(range(n + 1) for n in full)):
        parents = []
        for i, n in enumerate(state):
            if n:
                prior = list(state)
                prior[i] -= 1
                parents.append((tuple(prior), i))
        if not parents:
            best[state], sums[state] = 0, zero
            continue
        parent, i = parents[0]
        sums[state] = tuple(f.add[x][y] for x,y in zip(sums[parent], symbols[i]))
        best[state] = max(best[p] for p,_ in parents) + int(sums[state] == zero)
    if sums[full] != zero:
        raise ValueError("frequency partition total")
    return best[full]


def scalar_small_field(f, values):
    """Number of zero-sum blocks for F2/F3/F4/F5; remove zero charges first."""
    counts = Counter(a for a in values if a)
    n = sum(counts.values())
    total = 0
    for a in values:
        total = f.add[total][a]
    if total:
        raise ValueError("small-field partition total")
    if f.q in (2, 4):
        return n//2
    if f.q == 3:
        a, b = counts[1], counts[2]
        return min(a,b) + abs(a-b)//3
    if f.q != 5:
        raise ValueError("closed scalar formula requires q in 2,3,4,5")
    pairs = 0
    for x in (1, 2):
        y = f.neg[x]
        c = min(counts[x], counts[y])
        pairs += c
        counts[x] -= c
        counts[y] -= c
    remaining = [x for x in counts if counts[x]]
    if len(remaining) <= 1:
        return pairs + sum(counts.values())//5
    x,y = remaining
    if f.mul[2][x] != y:
        x,y = y,x
    if f.mul[2][x] != y:
        raise ValueError("unexpected five-element normal form")
    a,b = counts[x],counts[y]
    return pairs + min((a+2*b)//5,(3*a+b)//5)
