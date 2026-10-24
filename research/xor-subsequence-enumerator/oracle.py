"""Independent index-order counting; no bit recurrence is imported.

Produced by Nick Petalas. Apache-2.0.
"""

from itertools import combinations


def sequence(n, mask, limit):
    if type(n) is not int or not 0 <= n <= limit:
        raise ValueError("invalid oracle width")
    if type(mask) is not int or not 0 <= mask < 1 << n:
        raise ValueError("invalid oracle mask")
    return [index ^ mask for index in range(1 << n)]


def by_endpoints(n, mask):
    """Count chains by final index and length in the actual ordered sequence."""
    values = sequence(n, mask, 7)
    rows = []
    total = [1] + [0] * len(values)
    for i, value in enumerate(values):
        row = {1: 1}
        for j in range(i):
            if values[j] > value:
                for length, count in rows[j].items():
                    row[length + 1] = row.get(length + 1, 0) + count
        for length, count in row.items():
            total[length] += count
        rows.append(row)
    last = max(length for length, count in enumerate(total) if count)
    return total[:last + 1]


def by_subsets(n, mask):
    """Enumerate every index subset, including the empty one."""
    values = sequence(n, mask, 4)
    counts = [0] * (len(values) + 1)
    for size in range(len(values) + 1):
        for indices in combinations(range(len(values)), size):
            if all(values[indices[i]] > values[indices[i + 1]] for i in range(size - 1)):
                counts[size] += 1
    last = max(length for length, count in enumerate(counts) if count)
    return counts[:last + 1]


def longest_only(n, mask):
    """Fenwick maximum-length/count DP, querying only strictly larger values."""
    values = sequence(n, mask, 10)
    size = len(values)
    lengths = [0] * (size + 1)
    counts = [0] * (size + 1)
    answer_length = answer_count = 0
    for value in values:
        cursor = size - value - 1
        best = count = 0
        for _ in range(n + 1):
            if cursor == 0:
                break
            if lengths[cursor] > best:
                best, count = lengths[cursor], counts[cursor]
            elif lengths[cursor] == best:
                count += counts[cursor]
            cursor -= cursor & -cursor
        if cursor != 0:
            raise ValueError("query bound exhausted")
        length, count = best + 1, count if best else 1
        if length > answer_length:
            answer_length, answer_count = length, count
        elif length == answer_length:
            answer_count += count
        cursor = size - value
        for _ in range(n + 1):
            if cursor > size:
                break
            if length > lengths[cursor]:
                lengths[cursor], counts[cursor] = length, count
            elif length == lengths[cursor]:
                counts[cursor] += count
            cursor += cursor & -cursor
        if cursor <= size:
            raise ValueError("update bound exhausted")
    return answer_length, answer_count
