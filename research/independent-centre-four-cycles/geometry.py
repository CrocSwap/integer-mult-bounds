#!/usr/bin/env python3
"""Exact prefix minimization for one induced four-cycle.

The distance is the classical paired Lagrangian neighbour distance: 0 on a
repeated label, 1 on a transvection pair, and 2 across pairs. This file prices
the four cycle corrections by the equality pattern of those pairs. Apache-2.0.
"""
from itertools import product

INF = 10 ** 18


def need(condition, message):
    if not condition:
        raise ValueError(message)


def label_distance(left, right):
    if left == right:
        return 0
    return 1 if left // 2 == right // 2 else 2


def topk(values, k):
    best = []
    for index, value in enumerate(values):
        item = (value, index)
        if len(best) < k:
            best.append(item)
            best.sort()
        elif item < best[-1]:
            best[-1] = item
            best.sort()
    return tuple(best)


def invoice(costs, labels, prefix):
    value = sum(costs[i][labels[i]] for i in range(4))
    for left, right in ((0, 1), (1, 2), (2, 3), (3, 0)):
        value += min(label_distance(labels[left], labels[right]), prefix) - 2
    return value


def _rows(costs):
    width = len(costs[0])
    pairs = width // 2
    rows = []
    marginal = []
    tag_of = []
    for row in costs:
        pair_rows = []
        pair_min = []
        pair_tag = []
        for pair in range(pairs):
            left, right = row[2 * pair], row[2 * pair + 1]
            pair_rows.append((left, right))
            if left <= right:
                pair_min.append(left)
                pair_tag.append(0)
            else:
                pair_min.append(right)
                pair_tag.append(1)
        rows.append(pair_rows)
        marginal.append(pair_min)
        tag_of.append(pair_tag)
    return rows, marginal, tag_of


def _joint(rows, vertices, edges, pair):
    best_value = INF
    best_tags = None
    for tags in product((0, 1), repeat=len(vertices)):
        total = sum(rows[vertices[i]][pair][tags[i]] for i in range(len(vertices)))
        total += sum(-2 if tags[a] == tags[b] else -1 for a, b in edges)
        if total < best_value:
            best_value = total
            best_tags = tags
    return best_value, best_tags


def cycle_minimum(costs, prefix):
    """Minimum of four unaries plus the four cycle corrections.

    ``costs[v][label]`` is the capped-rank unary of cycle vertex ``v``. The
    returned labels are one minimizing 4-tuple. Their invoice equals the value.
    """
    need(len(costs) == 4, "four cycle costs")
    width = len(costs[0])
    need(width % 2 == 0 and width >= 2 and all(len(row) == width and all(type(x) is int for x in row)
                                               for row in costs), "paired integer costs")
    need(1 <= prefix <= 9, "prefix")
    pairs = width // 2
    rows, marginal, tag_of = _rows(costs)
    baseline = min(2, prefix) - 2
    best_value = INF
    best_labels = None

    def consider(value, labels):
        nonlocal best_value, best_labels
        if value < best_value:
            best_value = value
            best_labels = labels

    def place(labels, vertex, pair, tag):
        labels[vertex] = 2 * pair + tag

    def place_best(labels, vertex, pair):
        place(labels, vertex, pair, tag_of[vertex][pair])

    # One common pair. All four edges couple the tags.
    for pair in range(pairs):
        value, tags = _joint(rows, (0, 1, 2, 3), ((0, 1), (1, 2), (2, 3), (3, 0)), pair)
        consider(value, tuple(2 * pair + tag for tag in tags))

    # A path of three vertices on one pair, and the remaining vertex on another.
    # The two edges leaving the outsider cross pairs, so each contributes baseline.
    if pairs >= 2:
        for path in ((0, 1, 2, 3), (1, 2, 3, 0), (2, 3, 0, 1), (3, 0, 1, 2)):
            a, b, c, outsider = path
            for pair in range(pairs):
                value, tags = _joint(rows, (a, b, c), ((0, 1), (1, 2)), pair)
                alt = None
                for other in range(pairs):
                    if other == pair:
                        continue
                    item = (marginal[outsider][other], other)
                    if alt is None or item < alt:
                        alt = item
                labels = [None] * 4
                place(labels, a, pair, tags[0])
                place(labels, b, pair, tags[1])
                place(labels, c, pair, tags[2])
                place_best(labels, outsider, alt[1])
                consider(value + alt[0] + 2 * baseline, tuple(labels))

        # Two opposite edges lie inside two distinct pairs.
        for left, right in (((0, 1), (2, 3)), ((1, 2), (3, 0))):
            left_joint = [_joint(rows, left, ((0, 1),), pair) for pair in range(pairs)]
            right_joint = [_joint(rows, right, ((0, 1),), pair) for pair in range(pairs)]
            left_order = sorted((left_joint[pair][0], pair) for pair in range(pairs))
            for pair in range(pairs):
                other = left_order[0][1] if left_order[0][1] != pair else left_order[1][1]
                labels = [None] * 4
                for vertex, tag in zip(left, left_joint[other][1]):
                    place(labels, vertex, other, tag)
                for vertex, tag in zip(right, right_joint[pair][1]):
                    place(labels, vertex, pair, tag)
                consider(left_joint[other][0] + right_joint[pair][0] + 2 * baseline, tuple(labels))

        # The two diagonals occupy two distinct pairs. No cycle edge is internal
        # to a pair, so every correction is baseline and the tags separate.
        group_a = [marginal[0][pair] + marginal[2][pair] for pair in range(pairs)]
        group_b = [marginal[1][pair] + marginal[3][pair] for pair in range(pairs)]
        order_b = sorted((group_b[pair], pair) for pair in range(pairs))
        for pair in range(pairs):
            other = order_b[0][1] if order_b[0][1] != pair else order_b[1][1]
            labels = [None] * 4
            place_best(labels, 0, pair)
            place_best(labels, 2, pair)
            place_best(labels, 1, other)
            place_best(labels, 3, other)
            consider(group_a[pair] + group_b[other] + 4 * baseline, tuple(labels))

    # One cycle edge lies in a pair. Its two free vertices use two further pairs.
    if pairs >= 3:
        pools = [tuple(pair for _value, pair in topk(marginal[vertex], 4)) for vertex in range(4)]
        for edge, free_a, free_b in (((0, 1), 2, 3), ((1, 2), 3, 0), ((2, 3), 0, 1), ((3, 0), 1, 2)):
            joints = [_joint(rows, edge, ((0, 1),), pair) for pair in range(pairs)]
            for pair in range(pairs):
                add = None
                chosen = None
                for left in pools[free_a]:
                    if left == pair:
                        continue
                    for right in pools[free_b]:
                        if right == pair or right == left:
                            continue
                        total = marginal[free_a][left] + marginal[free_b][right]
                        if add is None or total < add:
                            add = total
                            chosen = (left, right)
                need(chosen is not None, "room for two free pairs")
                labels = [None] * 4
                for vertex, tag in zip(edge, joints[pair][1]):
                    place(labels, vertex, pair, tag)
                place_best(labels, free_a, chosen[0])
                place_best(labels, free_b, chosen[1])
                consider(joints[pair][0] + add + 3 * baseline, tuple(labels))

        # One diagonal pair matches, and the other two vertices use new pairs.
        for matched, free_a, free_b in (((0, 2), 1, 3), ((1, 3), 0, 2)):
            for pair in range(pairs):
                add = None
                chosen = None
                for left in pools[free_a]:
                    if left == pair:
                        continue
                    for right in pools[free_b]:
                        if right == pair or right == left:
                            continue
                        total = marginal[free_a][left] + marginal[free_b][right]
                        if add is None or total < add:
                            add = total
                            chosen = (left, right)
                need(chosen is not None, "room for a diagonal complement")
                labels = [None] * 4
                place_best(labels, matched[0], pair)
                place_best(labels, matched[1], pair)
                place_best(labels, free_a, chosen[0])
                place_best(labels, free_b, chosen[1])
                consider(marginal[matched[0]][pair] + marginal[matched[1]][pair] + add + 4 * baseline,
                         tuple(labels))

    # Four distinct pairs. Tags separate, and every correction is baseline.
    if pairs >= 4:
        pools = [tuple(pair for _value, pair in topk(marginal[vertex], 4)) for vertex in range(4)]
        for choice in product(*pools):
            if len(set(choice)) < 4:
                continue
            labels = [None] * 4
            total = 4 * baseline
            for vertex, pair in enumerate(choice):
                place_best(labels, vertex, pair)
                total += marginal[vertex][pair]
            consider(total, tuple(labels))

    need(best_labels is not None and all(type(label) is int for label in best_labels),
         "cycle minimum exists")
    need(invoice(costs, best_labels, prefix) == best_value, "minimizer invoice")
    return best_value, best_labels


def paired_transform(values, prefix):
    """Witnessed min-plus transform for the paired correction."""
    width = len(values)
    need(width % 2 == 0 and width >= 4 and all(type(x) is int for x in values), "transform domain")
    need(1 <= prefix <= 9, "prefix")
    minima = []
    for pair in range(width // 2):
        left, right = 2 * pair, 2 * pair + 1
        if (values[left], left) <= (values[right], right):
            minima.append((values[left], left))
        else:
            minima.append((values[right], right))
    first, second = sorted(range(len(minima)), key=lambda pair: minima[pair])[:2]
    baseline = min(2, prefix) - 2
    result = []
    for label in range(width):
        outside = minima[second if label // 2 == first else first]
        result.append(min((values[label] - 2, label),
                          (values[label ^ 1] - 1, label ^ 1),
                          (outside[0] + baseline, outside[1])))
    return tuple(result)


def cycle_reference(costs, prefix):
    """Same minimum, by fixing one label and eliminating the path of three.

    The paired transform is the predecessor path step. The closing correction
    stays outside it because that edge meets the fixed label.
    """
    need(len(costs) == 4 and len(costs[0]) >= 4, "reference domain")
    width = len(costs[0])
    baseline = min(2, prefix) - 2
    best_value = INF
    best_labels = None
    first, second, third, fourth = costs
    for start in range(width):
        partner = start ^ 1
        shifted = tuple(second[label] + (-2 if label == start else -1 if label == partner else baseline)
                        for label in range(width))
        left = paired_transform(shifted, prefix)
        middle_cost = tuple(third[label] + left[label][0] for label in range(width))
        middle = paired_transform(middle_cost, prefix)
        for end in range(width):
            extra = -2 if end == start else -1 if end == partner else baseline
            value = first[start] + fourth[end] + extra + middle[end][0]
            if value < best_value:
                third_label = middle[end][1]
                second_label = left[third_label][1]
                best_value = value
                best_labels = (start, second_label, third_label, end)
    need(best_labels is not None, "reference minimum exists")
    need(invoice(costs, best_labels, prefix) == best_value, "reference invoice")
    return best_value, best_labels


def brute(costs, prefix):
    best = (INF, None)
    width = len(costs[0])
    for labels in product(range(width), repeat=4):
        value = invoice(costs, labels, prefix)
        if value < best[0]:
            best = (value, labels)
    return best
