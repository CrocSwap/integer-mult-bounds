"""Integer-lifting P104 reference. Tekalign/Codex, Apache-2.0.

This is a scalar reference, not an admitted recursively cheap native child.
No predecessor executable is imported here. Unbounded signed integers, no aliasing.
"""


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rot(z, phase):
    a, b = z
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def pair(a, b, inverse=False):
    """Four Gaussian lifts and one quarter turn; floor acts componentwise."""
    d = (a[0] - b[0], a[1] - b[1])
    s = (b[0] + d[0] // 2, b[1] + d[1] // 2)
    d = rot(d, -1 if inverse else 1)
    b = (s[0] - d[0] // 2, s[1] - d[1] // 2)
    return (b[0] + d[0], b[1] + d[1]), b


def plan(record):
    need(set(record) == {'matrix_rows', 'offset', 'linear_Z4',
                         'quadratic_rows', 'phase'}, 'wrapper schema')
    rows, lin, quad = (record[k] for k in
                       ('matrix_rows', 'linear_Z4', 'quadratic_rows'))
    need(len(rows) == len(lin) == len(quad) == 9, 'wrapper dimension')
    need(all(type(x) is int and 0 <= x < 512 for x in rows + quad), 'binary rows')
    need(all(type(x) is int and 0 <= x < 4 for x in lin), 'linear phase')
    need(type(record['offset']) is int and 0 <= record['offset'] < 512, 'offset')
    need(type(record['phase']) is int and 0 <= record['phase'] < 4, 'global phase')
    out = []
    for x in range(512):
        bits = [(x >> j) & 1 for j in range(9)]
        y = record['offset']
        for j, row in enumerate(rows):
            y ^= (sum(bits[k] * ((row >> k) & 1) for k in range(9)) % 2) << j
        phase = record['phase'] + sum(bits[j] * lin[j] for j in range(9))
        phase += 2 * sum(bits[j] * bits[k] * ((quad[j] >> k) & 1)
                         for j in range(9) for k in range(j + 1, 9))
        out.append((y, phase % 4))
    need(sorted(y for y, _ in out) == list(range(512)), 'wrapper bijection')
    return out


def inverse_plan(p):
    out = [None] * len(p)
    for x, (y, phase) in enumerate(p):
        out[y] = (x, -phase % 4)
    return out


def permute(value, p):
    need(len(value) == len(p), 'wrapper width')
    out = [(0, 0)] * len(value)
    for x, (y, phase) in enumerate(p):
        out[y] = rot(value[x], phase)
    return out


def cycles(p):
    """Input-independent schedule, compiled once and retained as recipe data."""
    seen, result = set(), []
    for start in range(len(p)):
        if start in seen:
            continue
        cycle, x = [], start
        while x not in seen:
            seen.add(x)
            cycle.append(x)
            x = p[x][0]
        need(x == start, 'permutation cycle')
        result.append(cycle)
    return result


def permute_inplace(value, p, meter=None):
    """Cycle swaps use one zero Gaussian scratch, restored after each cycle.

    Cycle compilation is input-independent setup, separately charged in README.
    """
    schedule = cycles(p)
    for cycle in schedule:
        start = cycle[0]
        scratch, value[start] = value[start], (0, 0)
        for x in cycle:
            y, phase = p[x]
            scratch = rot(scratch, phase)
            scratch, value[y] = value[y], scratch
        need(scratch == (0, 0), 'wrapper scratch restored')
    if meter is not None:
        meter['wrapper_cycles'] = meter.get('wrapper_cycles', 0) + len(schedule)
        meter['wrapper_swaps'] = meter.get('wrapper_swaps', 0) + len(value) + len(schedule)


def kernel(value, rank, left, right, inverse=False, meter=None):
    n = len(value)
    need(n > 1 and n & (n - 1) == 0 and 1 <= rank < n.bit_length(), 'kernel domain')
    if inverse:
        left, right = inverse_plan(right), inverse_plan(left)
    permute_inplace(value, right, meter)
    for bit in (reversed(range(rank)) if inverse else range(rank)):
        for x in range(n):
            if x >> bit & 1:
                continue
            y = x ^ (1 << bit)
            value[x], value[y] = pair(value[x], value[y], inverse)
            if meter is not None:
                meter['pairs'] += 1
    if meter is not None:
        meter['wrapper_values'] += 2 * n
    permute_inplace(value, left, meter)
    return value


def exact(value, rank, left, right):
    """Exact rational oracle: return Gaussian numerators / 2**rank."""
    value = permute(value, right)
    for bit in range(rank):
        for x in range(len(value)):
            if x >> bit & 1:
                continue
            y = x ^ (1 << bit)
            a, b = value[x]
            c, d = value[y]
            value[x] = (a - b + c + d, b + a + d - c)
            value[y] = (a + b + c - d, b - a + d + c)
    return permute(value, left)


def working_grid(value, f, b):
    need(type(f) is type(b) is int and f >= 0 and b >= 0, 'grid parameters')
    magnitude = max(abs(v) for z in value for v in z)
    if not magnitude:
        return f
    h = magnitude.bit_length() - 1 - f
    return max(f, b + 8 - h)


def shift(value, delta):
    if delta >= 0:
        return [(a << delta, b << delta) for a, b in value]
    divisor = 1 << -delta
    need(all(v % divisor == 0 for z in value for v in z), 'exact downshift')
    return [(a // divisor, b // divisor) for a, b in value]


def norm2(value):
    return sum(a*a + b*b for a, b in value)


def difference(a, b):
    return [(x-u, y-v) for (x, y), (u, v) in zip(a, b)]


def execute_collector(sources, query, f, b, left, right, observer=None):
    """Execution path: mutate query, restore private C; no array snapshots.

    Optional observer is verifier instrumentation, absent in the execution.
    """
    need(len(sources) == 5 and all(len(v) == 512 for v in sources)
         and len(query) == 512, 'collector shape')
    need(all(type(t) is int for v in sources + [query] for z in v for t in z),
         'integer collector entrance')
    meter = dict(pairs=0, wrapper_values=0, field_adds=0)
    c = [(0, 0)] * 512
    for source in sources:
        for j, (x, y) in enumerate(source):
            a, z = c[j]
            c[j] = (a+x, z+y)
        meter['field_adds'] += 1
    if observer:
        observer('entrance', c)
    F = working_grid(c, f, b)
    for j, (a, z) in enumerate(c):
        c[j] = (a << (F-f), z << (F-f))
    kernel(c, 7, left, right, meter=meter)
    if observer:
        observer('sent', c)
    for j, ((a, z), (x, y)) in enumerate(zip(query, c)):
        query[j] = ((a << (F-f))+x, (z << (F-f))+y)
    meter['field_adds'] += 1
    kernel(c, 7, left, right, inverse=True, meter=meter)
    if observer:
        observer('returned', c)
    divisor = 1 << (F-f)
    for j, (a, z) in enumerate(c):
        need(a % divisor == z % divisor == 0, 'exact downshift')
        c[j] = (a // divisor, z // divisor)
    for source in reversed(sources):
        for j, (x, y) in enumerate(source):
            a, z = c[j]
            c[j] = (a-x, z-y)
        meter['field_adds'] += 1
    need(all(a == z == 0 for a, z in c), 'private erasure')
    if observer:
        observer('private', c)
    return F, meter


def collector(sources, query, f, b, left, right):
    """Instrumentation wrapper, deliberately separate from execution storage."""
    snapshots = {}
    q = list(query)
    F, meter = execute_collector(sources, q, f, b, left, right,
                                lambda name, value: snapshots.update({name: list(value)}))
    need(snapshots['returned'] == shift(snapshots['entrance'], F-f), 'exact paired return')
    return dict(query=q, grid=F, meter=meter, **snapshots)


def invoice(n=512, rank=7, wrapper_cycles=0):
    """Logical scalar-reference currency; no physical tape tariff inferred."""
    pairs = rank * n  # outbound plus return
    return dict(pairs=pairs, real_adds=8*pairs+22*n,
                floor_halves=4*pairs, quarter_turns=pairs,
                wrapper_values=4*n, field_adds=11,
                source_component_reads=20*n, query_component_adds=2*n,
                embedding_components=4*n, downshift_components=2*n,
                magnitude_scan_components=2*n, zero_scan_components=2*n,
                entrance_validation_components=12*n,
                private_initialization_components=2*n,
                wrapper_cycles=wrapper_cycles, wrapper_swaps=4*n+wrapper_cycles,
                wrapper_swap_component_reads=4*(4*n+wrapper_cycles),
                wrapper_swap_component_writes=4*(4*n+wrapper_cycles),
                butterfly_component_reads=4*pairs,
                butterfly_component_writes=4*pairs,
                field_add_component_reads=44*n,
                field_add_component_writes=22*n)
