# SPDX-License-Identifier: Apache-2.0
"""Build the P111 decoder and its paid frame schedule."""
from fractions import Fraction as Q
from itertools import combinations, product

N = 9
FULL = tuple(1 << j for j in range(N))
ZERO = ()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def basis(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    for bit in sorted(pivots):
        for other in pivots:
            if other > bit and (pivots[other] >> bit) & 1:
                pivots[other] ^= pivots[bit]
    return tuple(pivots[bit] for bit in sorted(pivots))


def span(rows):
    values = {0}
    for row in rows:
        values |= {x ^ row for x in values}
    return values


def contained(left, right):
    return len(basis(left + right)) == len(basis(right))


def distance(left, right):
    return 2 * len(basis(left + right)) - len(left) - len(right)


def parity(value):
    return value.bit_count() & 1


def perp(vector):
    return basis([x for x in range(1, 1 << N) if parity(x & vector) == 0])


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def roots():
    values = []
    for a, b in combinations(range(8), 2):
        for sign in (1, -1):
            row = [0] * 8
            row[a], row[b] = 2, 2 * sign
            values.append(tuple(row))
    for signs in product((1, -1), repeat=7):
        row = (1,) + signs
        if row.count(-1) % 2 == 0:
            values.append(row)
    require(len(values) == 120, "E8 line count")
    return values


def labels_from_pairing(gram):
    """Construct an orthonormal chart for the binary label form."""
    rows = [sum(((value + 1) & 1) << j for j, value in enumerate(row)) for row in gram]
    anchors = []
    for index, row in enumerate(rows):
        if len(basis([rows[j] for j in anchors] + [row])) > len(anchors):
            anchors.append(index)
    require(len(anchors) == N, "binary label rank")
    form = [sum(((gram[a][b] + 1) & 1) << j for j, b in enumerate(anchors)) for a in anchors]

    def pairing(x, y):
        return parity(sum(parity(row & y) << i for i, row in enumerate(form)) & x)

    chart = []
    for _ in range(N):
        candidates = [x for x in range(1, 1 << N)
                      if all(pairing(x, y) == 0 for y in chart) and pairing(x, x)]
        chosen = None
        for x in candidates:
            trial = chart + [x]
            if len(trial) == N or any(
                pairing(y, y) and all(pairing(y, z) == 0 for z in trial)
                for y in range(1, 1 << N)
            ):
                chosen = x
                break
        require(chosen is not None, "orthonormal chart exists")
        chart.append(chosen)
    labels = []
    for row in gram:
        evaluations = sum(((row[a] + 1) & 1) << i for i, a in enumerate(anchors))
        labels.append(sum(parity(evaluations & x) << i for i, x in enumerate(chart)))
    require(all(parity(labels[i] & labels[j]) == ((gram[i][j] + 1) & 1)
                for i in range(120) for j in range(120)), "label pairing identity")
    return labels


def geometry():
    lines = roots()
    gram = [[dot(a, b) // 4 for b in lines] for a in lines]
    require(all(dot(a, b) % 4 == 0 for a in lines for b in lines), "integral E8 products")
    frame = []
    for a in range(0, 8, 2):
        for sign in (1, -1):
            row = tuple(2 if j == a else 2 * sign if j == a + 1 else 0 for j in range(8))
            frame.append(lines.index(row))
    extra = next(j for j in range(120) if j not in frame)
    pivot = next(k for k, a in enumerate(frame) if gram[extra][a])
    live = [i for i in range(120) if i not in frame and i != extra]
    labels = labels_from_pairing(gram)
    return dict(lines=lines, gram=gram, frame=frame, extra=extra, pivot=pivot,
                live=live, labels=labels, ports=[labels[i] for i in live])


def decoder(geo, replaced):
    live, frame, gram = geo['live'], geo['frame'], geo['gram']
    gather = [[gram[i][a] for i in live] for a in frame]
    scatter = [[Q(gram[i][a], 4) for a in frame] for i in live]
    normals = list(frame)
    endpoints = [ZERO for _ in frame]
    if replaced:
        k, beta = geo['pivot'], geo['extra']
        coefficients = [Q(gram[beta][a], 2) for a in frame]
        require(coefficients[k] != 0, "replacement pivot")
        gather[k] = [gram[beta][i] for i in live]
        normals[k] = beta
        endpoints[k] = (geo['labels'][frame[k]],)
        for row in scatter:
            old = row[k]
            for j in range(8):
                row[j] = old / coefficients[k] if j == k else row[j] - old * coefficients[j] / coefficients[k]
    query_frames = [perp(geo['labels'][a]) for a in normals]
    for k, row in enumerate(gather):
        support = [geo['ports'][i] for i, value in enumerate(row) if value]
        require(basis(support) == query_frames[k], "source query span")
        require(contained(endpoints[k], query_frames[k]), "copy endpoint inside source span")
    expected = [[Q(gram[t][i], 2) for i in live] for t in live]
    require(all(sum(scatter[t][k] * gather[k][i] for k in range(8)) == expected[t][i]
                for t in range(111) for i in range(111)), "exact decoder identity")
    return dict(gather=gather, scatter=scatter, frames=query_frames,
                endpoints=endpoints, expected=expected, normals=normals)


def build(replaced=True):
    geo = geometry()
    data = decoder(geo, replaced)
    v = len(geo['live'])
    # Both words use the same stock. The candidate pays the three unused tails.
    direct = decoder(geo, False)
    stock = sum(bool(q) for row in direct['gather'] for q in row) + 8
    n = 2 * v + stock
    centers = list(range(2 * v, 2 * v + 8))
    uses = []
    for k, row in enumerate(data['gather']):
        for i, q in enumerate(row):
            if q:
                uses.append(dict(center=k, source=i, q=q, role=2 * v + 8 + len(uses)))
    require(2 * v + 8 + len(uses) <= n, "matched helper stock")
    frames = [(p,) for p in geo['ports']] + [ZERO] * (n - v)
    initial = list(frames)
    events = []

    def move(role, frame):
        frame = basis(frame)
        if frames[role] != frame:
            require(contained(frames[role], frame), "constructor frame descent")
            events.append(dict(op='move', role=role, before=list(frames[role]), after=list(frame)))
            frames[role] = frame

    def add(target, source, q, frame, phase):
        require(frames[target] == frames[source] == basis(frame), "constructor common frame")
        events.append(dict(op='add', target=target, source=source, q=str(q), frame=list(frame), phase=phase))

    # Compute and remove the complete response to arbitrary helper input.
    for use in uses:
        add(centers[use['center']], use['role'], 1, ZERO, 'old_gather')
    for t, row in enumerate(data['scatter']):
        for k, q in enumerate(row):
            if q:
                add(v + t, centers[k], -q, ZERO, 'compensate')
    for use in reversed(uses):
        add(centers[use['center']], use['role'], -1, ZERO, 'old_ungather')
    # Read every source at its initial line. No source copy is free.
    for use in uses:
        i, h = use['source'], use['role']
        move(h, (geo['ports'][i],))
        add(h, i, use['q'], (geo['ports'][i],), 'source_read')
    for k, center in enumerate(centers):
        frame = data['frames'][k]
        move(center, frame)
        for use in uses:
            if use['center'] == k:
                move(use['role'], frame)
                add(center, use['role'], 1, frame, 'new_gather')
    order = [k for k in range(8) if not data['endpoints'][k]] + [k for k in range(8) if data['endpoints'][k]]
    for k in order:
        endpoint = data['endpoints'][k]
        events.append(dict(op='copy_begin', source=centers[k], before=list(data['frames'][k]), after=list(endpoint), term=k))
        for t, row in enumerate(data['scatter']):
            if row[k]:
                move(v + t, endpoint)
                events.append(dict(op='copy_add', target=v + t, q=str(row[k]), frame=list(endpoint), term=k))
        events.append(dict(op='copy_end', term=k))
    # The retained centers and all source-use helpers are restored at FULL.
    for role in list(range(v)) + list(range(2 * v, n)):
        move(role, FULL)
    for use in reversed(uses):
        add(centers[use['center']], use['role'], -1, FULL, 'restore_gather')
    for use in reversed(uses):
        add(use['role'], use['source'], -use['q'], FULL, 'restore_source')
    for t, port in enumerate(geo['ports']):
        move(v + t, perp(port))
    return dict(version=1, name='one_replacement' if replaced else 'coordinate',
                n=n, v=v, helper_stock=stock, active_helpers=8 + len(uses),
                initial_frames=[list(x) for x in initial], final_frames=[list(x) for x in frames],
                events=events, centers=centers, unused=list(range(2 * v + 8 + len(uses), n)),
                geometry=geo, decoder=data)


def serializable(word):
    return {key: value for key, value in word.items() if key not in ('geometry', 'decoder')}
