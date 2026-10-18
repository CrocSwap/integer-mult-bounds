"""Independent natural-image census using columns and right multiplication.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0. Imports no implementation from the primary checker.
"""


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            top = row.bit_length() - 1
            if top in pivots:
                row ^= pivots[top]
            else:
                pivots[top] = row
                break
    return len(pivots)


def scalar_product(left, right, r):
    return tuple(sum(((sum(((left[i] >> k) & 1) * ((right[k] >> j) & 1)
                           for k in range(r))) % 2) << j for j in range(r))
                 for i in range(r))


def all_projectors(r):
    # Enumerate ALL 2^(r*r) matrices; do not inherit the u,v parametrization.
    mask = (1 << r) - 1
    return [rows for code in range(1 << (r * r))
            if rank(rows := tuple((code >> (i * r)) & mask for i in range(r))) == 1
            and scalar_product(rows, rows, r) == rows]


def to_rows_integer(columns):
    n = len(columns)
    return sum(((columns[j] >> i) & 1) << (i * n + j) for i in range(n) for j in range(n))


def column_generators(r):
    n = 3 * r
    records = []
    for p in all_projectors(r):
        for a in range(3):
            for b in range(3):
                if a == b:
                    continue
                columns = []
                for col in range(n):
                    out = 1 << col
                    if col % 3 == b:
                        for row in range(r):
                            if p[row] >> (col // 3) & 1:
                                out ^= 1 << (3 * row + a)
                    columns.append(out)
                changes = [(j, column ^ (1 << j)) for j, column in enumerate(columns)
                           if column != 1 << j]
                vectors = {delta for _, delta in changes}
                if len(vectors) != 1:
                    raise ValueError("generator difference is not rank one")
                vector = vectors.pop()
                sources = tuple(k for k in range(n) if vector >> k & 1)
                destinations = tuple(j for j, _ in changes)
                records.append((tuple(columns), sources, destinations))
    return records


def right_step(columns, record):
    # Column operations compute M G, unlike the primary row updates G M.
    row = 0
    for k in record[1]:
        row ^= columns[k]
    output = list(columns)
    for k in record[2]:
        output[k] ^= row
    return tuple(output)


def right_target(columns):
    result = list(columns)
    result[0], result[1] = result[1], result[0]
    result[3], result[4] = result[4], result[3]
    return tuple(result)


def census(r):
    records = column_generators(r)
    ball = {tuple(1 << k for k in range(3 * r))}
    front = set(ball)
    layers = [1]
    for _ in range(2):
        nxt = {right_step(state, record) for state in front for record in records} - ball
        layers.append(len(nxt))
        ball.update(nxt)
        front = nxt
    shifted = {right_target(state) for state in ball}
    base_hits = len(ball & shifted)
    edge_hits = 0
    for state in ball:
        for record in records:
            if right_step(state, record) in shifted:
                edge_hits += 1
    return ({to_rows_integer(state) for state in ball}, layers,
            {to_rows_integer(record[0]) for record in records}, (base_hits, edge_hits))
