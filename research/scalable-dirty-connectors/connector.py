"""Literal universal dirty-row connectors. Apache-2.0; AI assistance disclosed.

An operation (kind, label, port) is B_label into port, A_label from port,
or, for kind X, row[label] ^= row[port]. No observation or frame change is free.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Program:
    sources: int
    roots: int
    operations: tuple[tuple[str, int, int], ...]


def _source_count(n):
    if type(n) is not int or n < 4:
        raise ValueError("source count must be an integer >= 4")


def star(n):
    """Use n-3 dirty roots and exactly two calls to every B and A.

    The emitted program has exponential size because it has 2**n-1 outputs.
    """
    _source_count(n)
    dimensions = n - 4
    gray = tuple(i ^ (i >> 1) for i in range(1 << dimensions))
    operations = []
    frame = 0

    def move(destination):
        nonlocal frame
        changed = frame ^ destination
        for bit in range(dimensions):
            if changed & (1 << bit):
                operations.append(("X", 0, bit + 1))
                frame ^= 1 << bit

    def tour(reverse, phase, point):
        for g in reversed(gray) if reverse else gray:
            move(g)
            extra = frame
            for other in range(4):
                first, second = (point, other) if phase == 0 else (other, point)
                mask = first | (second << 2) | (extra << 4)
                if mask:
                    operations.append(("A", mask, 0))

    for t, point in enumerate((0, 1, 3, 2)):
        tour(bool(t % 2), 0, point)
        operations.append(("B", (0, 1, 0, 1)[t], 0))
    for j in range(4, n):
        operations.append(("B", j, j - 3))
    for t, point in enumerate((0, 1, 3, 2)):
        tour(bool(t % 2), 1, point)
        operations.append(("B", (2, 3, 2, 3)[t], 0))
    for j in range(4, n):
        operations.append(("B", j, j - 3))
    return Program(n, n - 3, tuple(operations))


def gray_baseline(n):
    """PR1185's two closed Gray cycles, with explicitly scheduled readouts."""
    _source_count(n)
    split = n // 2
    sizes = (split, n - split)
    operations = []
    for phase, size in enumerate(sizes):
        gray = tuple(i ^ (i >> 1) for i in range(1 << size))
        for t, point in enumerate(gray):
            for other in range(1 << sizes[1 - phase]):
                first, second = (point, other) if phase == 0 else (other, point)
                mask = first | (second << split)
                if mask:
                    operations.append(("A", mask, 0))
            changed = point ^ gray[(t + 1) % len(gray)]
            label = changed.bit_length() - 1 + (split if phase else 0)
            operations.append(("B", label, 0))
    return Program(n, 1, tuple(operations))


def extra_readout_baseline(n):
    """One root, two B calls per source, minimum even readouts on this word.

    PR943/1185 permit extra readouts instead of extra B calls. The interleave
    word was supplied by the subsequent independent review. No global word
    optimality is assumed here. A 0/1 subset DP minimizes readout cardinality
    for each target on this fixed word, including cancellation of dirty roots.
    """
    _source_count(n)
    word = [0, 1] + [j for i in range(2, n) for j in (i, i - 2)] + [n - 2, n - 1]
    points = [0]
    for j in word:
        points.append(points[-1] ^ (1 << j))
    # State index is (source mask << 1) | readout-count parity. Each boundary
    # can be selected once: selecting it twice cancels and cannot be minimal.
    unreachable = len(points) + 1
    cost = [unreachable] * (1 << (n + 1))
    selected = [0] * len(cost)
    cost[0] = 0
    for boundary, point in enumerate(points):
        old_cost, old_selected = cost, selected
        cost, selected = old_cost[:], old_selected[:]
        offset = (point << 1) | 1
        for state, count in enumerate(old_cost):
            destination = state ^ offset
            if count + 1 < cost[destination]:
                cost[destination] = count + 1
                selected[destination] = old_selected[state] | (1 << boundary)
    reads = [[] for _ in points]
    for mask in range(1, 1 << n):
        if cost[mask << 1] == unreachable:
            raise ValueError("source-prefix span does not cover target")
        for boundary in range(len(points)):
            if selected[mask << 1] & (1 << boundary):
                reads[boundary].append(("A", mask, 0))
    operations = []
    for boundary, calls in enumerate(reads):
        operations.extend(calls)
        if boundary < len(word):
            operations.append(("B", word[boundary], 0))
    return Program(n, 1, tuple(operations))


def fixed_port_five():
    """Eight paid transfers; every B and A uses physical row zero."""
    skeleton = (
        ("X", 1, 0), ("B", 0, 0), ("X", 1, 0), ("X", 0, 1),
        ("B", 1, 0), ("X", 0, 1), ("B", 2, 0), ("B", 3, 0),
        ("X", 1, 0), ("B", 0, 0), ("X", 1, 0), ("X", 0, 1),
        ("B", 4, 0), ("X", 0, 1), ("B", 3, 0), ("B", 1, 0),
        ("B", 4, 0), ("B", 2, 0),
    )
    # Literal boundary pairs from physical replay; they are not computed using
    # the verifier and can be checked independently by its row interpreter.
    pairs = (
        (0, 2), (2, 6), (0, 6), (0, 17), (2, 17), (2, 7), (0, 7),
        (7, 8), (7, 10), (10, 17), (8, 17), (5, 12), (6, 10),
        (0, 10), (0, 8), (10, 14), (7, 15), (15, 17), (7, 16),
        (0, 16), (2, 16), (0, 15), (2, 15), (10, 15), (7, 14),
        (10, 16), (8, 16), (5, 13), (6, 14), (0, 14), (2, 14),
    )
    readouts = [[] for _ in range(len(skeleton) + 1)]
    for mask, pair in enumerate(pairs, 1):
        for boundary in pair:
            readouts[boundary].append(("A", mask, 0))
    operations = []
    for boundary, calls in enumerate(readouts):
        operations.extend(calls)
        if boundary < len(skeleton):
            operations.append(skeleton[boundary])
    return Program(5, 2, tuple(operations))
