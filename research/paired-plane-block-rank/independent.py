"""Separate all-span mask and exact finite-field rank oracle; stdlib only."""


def mask(labels, pairs):
    planes = {}
    for a, b in pairs:
        span = {0, labels[a], labels[b], labels[a] ^ labels[b]}
        for port in (a, b):
            planes[port] = span
    return [[i != j and all(sum(((x >> k) & 1) * ((y >> k) & 1) for k in range(9)) % 2 == 0
                            for x in planes[i] for y in planes[j]) for j in range(112)] for i in range(112)]


def rank(matrix, prime):
    a = [[x % prime for x in row] for row in matrix]
    r = 0
    for column in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        inv = pow(a[r][column], -1, prime)
        a[r] = [x*inv % prime for x in a[r]]
        for i in range(r+1, len(a)):
            if a[i][column]:
                factor = a[i][column]
                a[i] = [(x-factor*y) % prime for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def block_mask(matrix, width, allowed):
    # Check columns as direct basis actions, independently of model.fit loops.
    for source in range(len(matrix)):
        j, b = divmod(source, width)
        for target, row in enumerate(matrix):
            i, a = divmod(target, width)
            if i == j or not allowed[i][j]:
                if row[source] != int(i == j and a == b):
                    raise ValueError('independent basis endpoint')


def direct_query_action(blocks, charts, values):
    # Each support carries one vector. Encode with inverse source chart,
    # then decode with target chart; no dense matrix or shared multiply helper.
    out = [None]*112
    for support in blocks:
        x = y = 0
        for i in support:
            ((a, b), (c, d)), (u, v) = charts[i], values[i]
            x += d*u-b*v
            y += a*v-c*u
        for i in support:
            ((a, b), (c, d)) = charts[i]
            out[i] = [a*x+b*y, c*x+d*y]
    return [v for pair in out for v in pair]
