"""Independent unrestricted-query scalar oracle. No primary-model imports.

Adam Gall with OpenAI Codex assistance; Apache-2.0.
"""
from fractions import Fraction
from heapq import heappop, heappush


def cheapest(updates, dimension, sources, readers, corrections):
    """Dijkstra on literal current z/output coefficients, with delivery cuts.

Sources x0,u0,... and z0 are independent. The source current value is
reconstructed from the imposed updates, not from a connector syndrome.
Arbitrary numbers and orders of A/B calls are admitted at every request.
"""
    k = len(sources)
    dirty = 1 << (dimension + 1)
    xvalues = [1]
    for vector in updates:
        xvalues.append(xvalues[-1] ^ (vector << 1))
    # node=(request index, mode 0=request/1=post-mutation-cut, z, current output).
    start = (0, 0, dirty, 0)
    distances = {start: Fraction(0)}
    heap = [(Fraction(0), start)]
    settled = 0
    while heap:
        cost, node = heappop(heap)
        if distances[node] != cost:
            continue
        settled += 1
        i, mode, z, out = node
        if i == k:
            if z == dirty:
                return cost, settled
            continue
        edges = []
        if mode == 0:
            edges.append(((i, 0, z ^ xvalues[i], out), Fraction(sources[i])))
            edges.append(((i, 0, z, out ^ z), Fraction(readers[i])))
            if out == xvalues[i]:
                edges.append(((i + 1, 1 if i + 1 < k else 0, z, 0), Fraction(0)))
        else:
            edges.append(((i, 1, z ^ (updates[i - 1] << 1), 0), Fraction(corrections[i - 1])))
            edges.append(((i, 0, z, 0), Fraction(0)))
        for target, price in edges:
            candidate = cost + price
            if target not in distances or candidate < distances[target]:
                distances[target] = candidate
                heappush(heap, (candidate, target))
    raise ValueError("closed eager program should always be reachable")


def exhaustive_parities(updates, dimension, sources, readers, corrections):
    """Separate finite reference: enumerate every query/correction parity word."""
    k = len(sources)
    source = [1]
    for vector in updates:
        source.append(source[-1] ^ (vector << 1))
    best = None
    legal = 0
    for query_bits in range(1 << k):
        for repair_bits in range(1 << (k - 1)):
            residue = 0
            price = 2 * sum(map(Fraction, readers))
            for i in range(k):
                odd = query_bits >> i & 1
                residue ^= source[i] if odd else 0
                price += Fraction(sources[i]) * (2 - odd)
            for j in range(k - 1):
                used = repair_bits >> j & 1
                residue ^= (updates[j] << 1) if used else 0
                price += Fraction(corrections[j]) * used
            if residue == 0:
                legal += 1
                best = price if best is None else min(best, price)
    return best, legal
