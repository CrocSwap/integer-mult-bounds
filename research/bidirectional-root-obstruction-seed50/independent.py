"""Separate dense-matrix, path-DFS and integer-array controls. Apache-2.0.
Cinna Davis (1337isnot1337), with substantial OpenAI Codex assistance.
"""
from collections import Counter


def closed_counts(n, coefficients):
    identity = tuple(tuple(int(i == j) for j in range(n)) for i in range(n))
    matrices = {}
    for d in range(n):
        for s in range(n):
            if d != s:
                for a in coefficients:
                    matrices[d, s, a] = tuple(tuple(int(i == j) + (a if (i, j) == (d, s) else 0)
                                                   for j in range(n)) for i in range(n))

    def multiply(a, b):
        return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(n))
                           for j in range(n)) for i in range(n))

    inverse_lookup = {matrices[d, s, -a]: (d, s, a) for d, s, a in matrices}
    counts = {"1": 0, "2": 0, "3": 0}
    for ga, ma in matrices.items():
        if ma == identity:
            counts["1"] += 1
        for gb, mb in matrices.items():
            product = multiply(mb, ma)
            counts["2"] += product == identity
            gc = inverse_lookup.get(product)
            if gc is not None:
                if ga[:2] != gb[:2] or ga[:2] != gc[:2]:
                    raise RuntimeError("mixed three-transfer closure")
                counts["3"] += 1
    return counts


def four_root_counts(coefficients):
    n = 2
    eye = ((1, 0), (0, 1))
    gates = [(d, s, a) for d in range(2) for s in range(2) if d != s for a in coefficients]

    def act(m, g):
        d, s, a = g
        rows = [list(r) for r in m]
        rows[d] = [x + a * y for x, y in zip(rows[d], rows[s])]
        return tuple(tuple(r) for r in rows)

    direct = mixed = 0
    for a in gates:
        for b in gates:
            for c in gates:
                for d in gates:
                    if act(act(act(act(eye, a), b), c), d) == eye:
                        direct += 1
                        mixed += len({a[:2], b[:2], c[:2], d[:2]}) > 1
    pairs = Counter(act(act(eye, a), b) for a in gates for b in gates)
    grouped = 0
    for left, lc in pairs.items():
        for right, rc in pairs.items():
            if tuple(tuple(sum(right[i][k] * left[k][j] for k in range(2))
                           for j in range(2)) for i in range(2)) == eye:
                grouped += lc * rc
    if direct != grouped:
        raise RuntimeError("independent four-letter closure engines disagree")
    return {"coefficient_domain": list(coefficients), "all_closed_words": direct,
            "mixed_direction_closed_words": mixed, "independent_pair_convolution": grouped}


def one_root(target):
    histogram = Counter()

    def walk(used, position, vertices):
        if used == 63:
            covered = 0
            for i, row in enumerate(target):
                if any(all(b[k] - a[k] == row[k] for k in range(3))
                       for a in vertices for b in vertices):
                    covered |= 1 << i
            histogram[covered] += 1
            return
        for letter in range(6):
            if not used >> letter & 1:
                step = list(position)
                step[letter // 2] += 1 if letter % 2 else -1
                point = tuple(step)
                walk(used | 1 << letter, point, vertices + (point,))

    walk(0, (0, 0, 0), ((0, 0, 0),))
    return [histogram[i] for i in range(8)]


def numeric_short(events, heights):
    # Independent three scalar input columns: z dirt, w dirt, source signal.
    z, w, y = [1, 0, 0], [0, 1, 0], [0, 0, 0]
    stage = 0
    for event in events:
        if event[0] == "T":
            delta = heights[stage + 1] - heights[stage]
            z = [a + delta * b for a, b in zip(z, w)]
            stage += 1
        elif event[0] == "B":
            w[2] += event[1]
        else:
            y = [a + event[1] * b for a, b in zip(y, z)]
    return z[2] == w[2] == 0, y[:2] == [0, 0], y[2]


def dense(program, factors, target, dimension):
    # Deliberately singular, noncommuting exact integer factors; arbitrary dirt.
    matrices = [[[((f + 3) * (i + 2) + (j + 1) ** 2) % 5 - 2
                  for j in range(dimension)] for i in range(dimension)] for f in range(27)]

    def mm(a, b):
        return [[sum(a[i][k] * b[k][j] for k in range(dimension))
                 for j in range(dimension)] for i in range(dimension)]

    if dimension == 1:
        raise RuntimeError("noncommuting control needs dimension at least two")
    if mm(matrices[0], matrices[1]) == mm(matrices[1], matrices[0]):
        raise RuntimeError("fixture operators unexpectedly commute")
    if any(row != matrices[2][0] for row in matrices[2][1:]):
        raise RuntimeError("singular fixture operator lost its repeated-row control")
    initial = [[((r + 2) * (k + 5)) % 13 - 6 for k in range(dimension)] for r in range(11)]

    def apply(fs, values):
        for f in fs:
            values = [sum(a * b for a, b in zip(row, values)) for row in matrices[f]]
        return values

    rows = [r[:] for r in initial]
    for kind, f, sign, src, dst in program:
        values = apply((f,), rows[src]) if kind == "F" else rows[src][:]
        rows[dst] = [a + sign * b for a, b in zip(rows[dst], values)]
    expected = [r[:] for r in initial]
    for i in range(3):
        for j in range(3):
            values = apply(factors["B" + str(j)] + factors["A" + str(i)], initial[j][:])
            expected[i + 3] = [a + target[i][j] * b for a, b in zip(expected[i + 3], values)]
    if rows != expected:
        raise RuntimeError("dense noncommuting fixture failed")
    return rows
