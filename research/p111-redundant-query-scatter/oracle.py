"""Exhaust readout supports using exact rational ranks.

This checker does not use the row-frequency optimization in verify.py.
Produced by Nick Petalas. Apache-2.0.
"""


def rank(rows):
    """Fraction-free elimination with at most ten rows of length eight."""
    if len(rows) > 10 or any(len(row) != 8 for row in rows):
        raise ValueError("rank domain is at most 10 by 8")
    work = [list(row) for row in rows]
    used = 0
    for col in range(8):
        pivot = next((i for i in range(used, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[used], work[pivot] = work[pivot], work[used]
        for i in range(used + 1, len(work)):
            multiplier = work[i][col]
            if multiplier:
                value = work[used][col]
                work[i] = [value * a - multiplier * b
                           for a, b in zip(work[i], work[used], strict=True)]
        used += 1
    return used


def support_oracle(rows, query_slots):
    """Return each row's unrestricted and genuinely-query-using minima."""
    if len(rows) != 112 or len(query_slots) != 4:
        raise ValueError("oracle requires 112 rows and four query slots")
    vectors = [tuple(int(i == j) for i in range(8)) for j in range(8)]
    vectors.append(tuple(int(i in query_slots) for i in range(8)))
    supports = []
    for mask in range(512):
        old = [vectors[i] for i in range(8) if mask >> i & 1]
        full = old + ([vectors[8]] if mask >> 8 & 1 else [])
        supports.append((mask.bit_count(), old, full, rank(old), rank(full)))
    answers = []
    for row in rows:
        best, active = 10, 10
        for mask, (cost, old, full, old_rank, full_rank) in enumerate(supports):
            if rank(full + [row]) != full_rank:
                continue
            best = min(best, cost)
            if mask >> 8 & 1:
                # Dependent q admits any coefficient. Otherwise it is forced.
                if full_rank == old_rank or rank(old + [row]) > old_rank:
                    active = min(active, cost)
        if best == 10 or active == 10:
            raise AssertionError("dictionary must span every row")
        answers.append((best, active))
    return answers, 112 * 512
