"""Independent endpoint-sort oracle: no bit masks or per-coordinate sets.

Brian / JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter, defaultdict


def span_count(intervals, capacity):
    """Return occupied cardinality and prefix status, rejecting bounds/overlap."""
    spans = []
    for offset, width in intervals:
        if not 0 <= offset <= offset + width <= capacity:
            raise ValueError('window and footprint')
        # range preserves the original integer-index contract without enumeration.
        cells = range(offset, offset + width)
        if cells:
            spans.append((cells.start, cells.stop))
    end = count = 0
    for start, stop in sorted(spans):
        if start < end:
            raise ValueError('disjoint footprints')
        count += stop - start
        end = stop
    return count, count == end


def recount(roles, windows):
    groups = defaultdict(list)
    for role in roles:
        key = role['owner_replica'], role['child'], role['port']
        groups[key].append((role['offset'], role['width']))
    counts = {}
    idle = Counter()
    for owner, (capacity, _) in windows.items():
        rep, child = map(int, owner.split(','))
        for port in range(112):
            key = rep, child, port
            count, compact = span_count(groups.pop(key, []), capacity)
            if not compact:
                raise ValueError('compacted prefix')
            counts[key] = count
            if count < capacity:
                idle[capacity - count] += 1
    if groups:
        raise ValueError('Unknown owner bins')
    return counts, idle
