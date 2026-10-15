"""Phase-placement/normalized-interval checker; no predecessor code imports.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
This separate model is AI-written, not independent human review.
"""
from itertools import combinations_with_replacement, permutations, product


TRANSFERS = ((0, 1, 1), (0, 1, -1), (1, 0, 1), (1, 0, -1))


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def census():
    """Enumerate source orders, phase assignments, and closing port choices.

    First source signs are +1; the caller tests every target column-sign choice.
    Unlike the chronological checker, root source coefficients are reconstructed
    as G times open normalized injection intervals, not propagated by gates.
    """
    states = [((1, 0), (0, 1))]
    for destination, source, coefficient in TRANSFERS:
        shear = [[1, 0], [0, 1]]
        shear[destination][source] = coefficient
        states.append(multiply(shear, states[-1]))
    directions = [((g[1][1], -g[1][0]), (-g[0][1], g[0][0])) for g in states]
    orders = sorted(set(permutations((0, 0, 1, 1, 2, 2))))
    phases = list(combinations_with_replacement(range(5), 6))
    records = {}
    skeletons = 0
    for order in orders:
        first = [order.index(j) for j in range(3)]
        last = [5 - order[::-1].index(j) for j in range(3)]
        for stages in phases:
            skeletons += 1
            choices = []
            for j in range(3):
                options = []
                for start_port, end_port, end_sign in product(range(2), range(2), (-1, 1)):
                    start = directions[stages[first[j]]][start_port]
                    end = directions[stages[last[j]]][end_port]
                    if all(start[k] + end_sign * end[k] == 0 for k in range(2)):
                        options.append((start_port, end_port, end_sign, start))
                choices.append(options)
            for selected in product(*choices):
                word = []
                for phase in range(5):
                    for position, j in enumerate(order):
                        if stages[position] != phase:
                            continue
                        start_port, end_port, end_sign, _ = selected[j]
                        is_first = position == first[j]
                        word.append(("B", j, 1 if is_first else end_sign,
                                     start_port if is_first else end_port))
                    if phase < 4:
                        word.append(("T", *TRANSFERS[phase]))
                phase = 0
                opened = [False] * 3
                observations = set()
                for event in [None, *word]:
                    if event is not None:
                        if event[0] == "T":
                            phase += 1
                        else:
                            opened[event[1]] = not opened[event[1]]
                    for row in states[phase]:
                        signal = tuple(sum(row[k] * selected[j][3][k] for k in range(2))
                                       if opened[j] else 0 for j in range(3))
                        observation = row + signal
                        observations.add(observation)
                        observations.add(tuple(-x for x in observation))
                # Two signed observations must sum to (zero dirt, desired row).
                available = 0
                for code, row in enumerate(product((-1, 0, 1), repeat=3)):
                    if any((-value[0], -value[1], *(row[j] - value[j + 2] for j in range(3)))
                           in observations for value in observations):
                        available |= 1 << code
                key = tuple(word)
                if key in records:
                    raise RuntimeError("independent enumeration duplicated a source trace")
                records[key] = available
    return records, {"source_orders": len(orders), "phase_assignments": len(phases),
                     "order_phase_skeletons": skeletons}
