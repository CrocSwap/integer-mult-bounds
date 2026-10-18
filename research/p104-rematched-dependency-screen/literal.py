# SPDX-License-Identifier: Apache-2.0
"""Literal quotient-frame contact oracle, sharing only parsed inputs and tracing."""

from itertools import combinations


def quotient_spaces():
    """Enumerate distinct RREF subspaces of F2^5 as literal point lists."""
    result = []
    for size in range(6):
        spaces = []
        for pivots in combinations(range(5), size):
            free = [
                (i, j)
                for i, p in enumerate(pivots)
                for j in range(p + 1, 5)
                if j not in pivots
            ]
            for entries in range(1 << len(free)):
                rows = [1 << p for p in pivots]
                for index, (i, j) in enumerate(free):
                    if entries >> index & 1:
                        rows[i] |= 1 << j
                points = [0]
                for row in rows:
                    points += [p ^ row for p in points]
                spaces.append(sorted(points))
        if len({tuple(s) for s in spaces}) != len(spaces):
            raise ValueError("duplicate quotient subspace")
        result.append(spaces)
    if list(map(len, result)) != [1, 31, 155, 155, 31, 1]:
        raise ValueError("quotient census")
    return result


def coset_masks(low, high):
    """Construct all 32 literal cosets of A inside B without interval tests."""
    points, basis = [0], []
    for frame, target in ((low, 2), (high, 7)):
        for vector in range(1, 512):
            if len(basis) == target:
                break
            if frame >> vector & 1 and vector not in points:
                basis.append(vector)
                points += [p ^ vector for p in points]
        if len(basis) != target:
            raise ValueError("endpoint basis dimension")
    a_points = [0, basis[0], basis[1], basis[0] ^ basis[1]]
    masks = []
    for q in range(32):
        lift = 0
        for j in range(5):
            if q >> j & 1:
                lift ^= basis[2 + j]
        masks.append(sum(1 << (a ^ lift) for a in a_points))
    if len(set(masks)) != 32:
        raise ValueError("distinct quotient cosets")
    return masks


def allowed_frames(frames, edge, dimension, cosets, quotients):
    lines, departures, arrivals, caps, _ = frames
    a, b = edge
    if dimension == 1:
        return [lines[a // 2]]
    if dimension == 2:
        return [departures[a]]
    if dimension == 7:
        return [arrivals[b]]
    if dimension == 8:
        return [caps[b // 2]]
    if not 3 <= dimension <= 6:
        raise ValueError("literal dimension")
    result = []
    for points in quotients[dimension - 2]:
        mask = 0
        for point in points:
            mask |= cosets[point]
        result.append(mask)
    return result


def literal_layers(frames, edges, paths):
    if not 0 < len(edges) <= 2309:
        raise ValueError("literal helper capacity")
    quotients = quotient_spaces()
    cosets = [coset_masks(frames[1][a], frames[2][b]) for a, b in edges]
    readers, writers = {}, {}
    for index in range(104):
        for frame in paths[f"X{index}"]:
            readers[frame] = readers.get(frame, 0) | 1 << index
        for frame in paths[f"Y{index}"]:
            writers[frame] = writers.get(frame, 0) | 1 << index
    layers = []
    for dimension in range(1, 9):
        hosts, reads, writes = {}, [], []
        for helper, edge in enumerate(edges):
            choices = allowed_frames(frames, edge, dimension, cosets[helper], quotients)
            read_mask, write_mask = 0, 0
            for frame in choices:
                hosts[frame] = hosts.get(frame, 0) | 1 << helper
                read_mask |= readers.get(frame, 0)
                write_mask |= writers.get(frame, 0)
            reads.append(read_mask)
            writes.append(write_mask)
        adjacency = [1 << i for i in range(len(edges))]
        for mask in hosts.values():
            remaining = mask
            for _ in range(len(edges)):
                if not remaining:
                    break
                bit = remaining & -remaining
                adjacency[bit.bit_length() - 1] |= mask
                remaining ^= bit
        layers.append((adjacency, reads, writes))
    return layers
