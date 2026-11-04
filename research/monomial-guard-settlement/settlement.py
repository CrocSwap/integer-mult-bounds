"""Exact zero-sum block certificates and legal row-addition witnesses."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/"source"))
from finite import Field  # exact arithmetic retained from PR6710


def subset_sums(field, values):
    width = len(values[0]) if values else 0
    sums = [(0,)*width]
    for v in values:
        sums += [tuple(field.add[a][b] for a, b in zip(s, v)) for s in sums]
    return sums


def partition(field, values):
    """Maximum zero boundaries along a permutation and an attaining partition."""
    if not values:
        return []
    sums = subset_sums(field, values)
    if any(sums[-1]):
        raise ValueError("nonzero partition total")
    score = [0]*len(sums)
    last = [0]*len(sums)
    for mask in range(1, len(sums)):
        bits = mask
        best = -1
        while bits:
            bit = bits & -bits
            prior = score[mask ^ bit]
            if prior > best:
                best, last[mask] = prior, bit
            bits ^= bit
        score[mask] = best + int(not any(sums[mask]))
    mask = len(sums) - 1
    end = mask
    blocks = []
    while mask:
        mask ^= last[mask]
        if not any(sums[mask]):
            block = end ^ mask
            blocks.append([i for i in range(len(values)) if block & (1 << i)])
            end = mask
    if len(blocks) != score[-1]:
        raise ValueError("partition backtracking")
    return blocks


def charges(field, u, rows):
    return [tuple(field.mul[weight][row[i]] for row in rows) for i, weight in enumerate(u)]


def add_row(field, u, rows, target, source, a):
    """Left transvection on u and inverse right transvection on every row."""
    if target == source or not a:
        raise ValueError("illegal paid row addition")
    u = list(u)
    u[target] = field.add[u[target]][field.mul[a][u[source]]]
    out = []
    for initial in rows:
        row = list(initial)
        row[source] = field.add[row[source]][field.mul[field.neg[a]][row[target]]]
        out.append(tuple(row))
    return tuple(u), tuple(out)


def witness(field, u, rows, target_value=None):
    """Settle to zero, or consolidate to one location using a dummy charge."""
    active = [(i, z) for i, z in enumerate(charges(field, u, rows)) if any(z)]
    values = [z for _, z in active]
    dummy = len(active)
    if target_value is not None:
        if not any(target_value):
            raise ValueError("dummy target must be nonzero")
        values.append(tuple(field.neg[z] for z in target_value))
    blocks = partition(field, values)
    gates = []
    for block in blocks:
        real = [active[i][0] for i in block if i < dummy]
        root = real[-1]
        for i in real[:-1]:
            a = field.mul[field.neg[u[i]]][field.inv[u[root]]]
            gates.append((i, root, a))
            u, rows = add_row(field, u, rows, i, root, a)
    remaining = [v for v in charges(field, u, rows) if any(v)]
    expected = [] if target_value is None else [tuple(target_value)]
    if remaining != expected or len(gates) != len(active) - len(blocks):
        raise ValueError("settlement witness")
    indexed = [[active[i][0] if i < dummy else "target" for i in block] for block in blocks]
    return dict(active=len(active), blocks=indexed, distance=len(gates), gates=gates)


def ternary_extra(values):
    """Paid cost to make a separated full flat pass, for F3."""
    imbalance = values.count(1) - values.count(2)
    if imbalance % 3 != 1:
        raise ValueError("ternary total is not one")
    return min(abs(imbalance - 1), abs(imbalance + 2))//3
