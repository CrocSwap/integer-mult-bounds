"""Finite rounded Gaussian native reference kernel. Arham Tahir/Codex, Apache-2.0.

Primitive and wrapper schema: PR2725 and its credited native ancestry.
No predecessor executable is imported. Values are Gaussian integer numerators
with a shared power-of-two denominator.
"""


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rotate(value, phase):
    a, b = value
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def wrapper_plan(record):
    need(set(record) == {'matrix_rows', 'offset', 'linear_Z4', 'quadratic_rows', 'phase'}, 'wrapper schema')
    rows, linear, quadratic = (record[k] for k in ('matrix_rows', 'linear_Z4', 'quadratic_rows'))
    need(len(rows) == len(linear) == len(quadratic) == 9, 'wrapper dimension')
    need(all(type(v) is int and 0 <= v < 512 for v in rows + quadratic), 'wrapper binary rows')
    need(all(type(v) is int and 0 <= v < 4 for v in linear), 'wrapper phases')
    need(type(record['offset']) is int and 0 <= record['offset'] < 512, 'wrapper offset')
    need(type(record['phase']) is int and 0 <= record['phase'] < 4, 'global phase')
    out = []
    for x in range(512):
        y = record['offset'] ^ sum(((x & row).bit_count() % 2) << j for j, row in enumerate(rows))
        phase = record['phase']
        for j in range(9):
            if x >> j & 1:
                phase += linear[j] + 2 * (quadratic[j] & x & ~((1 << (j + 1)) - 1)).bit_count()
        out.append((y, phase % 4))
    need(sorted(y for y, _ in out) == list(range(512)), 'wrapper bijection')
    return out


def permute(vector, plan):
    out = [(0, 0)] * len(vector)
    for x, (y, phase) in enumerate(plan):
        out[y] = rotate(vector[x], phase)
    return out


def nearest_half(value):
    """Round value/2 to the nearest integer, with signed ties to even."""
    q, rem = divmod(value, 2)
    return q + (rem != 0 and q % 2 != 0)


def rounded_stage(vector, bit):
    """In-place C pairs; return squared local defect times four."""
    defect4 = 0
    for x in range(len(vector)):
        if x >> bit & 1:
            continue
        y = x ^ (1 << bit)
        a, b = vector[x]
        c, d = vector[y]
        nums = (a - b + c + d, b + a + d - c, a + b + c - d, b - a + d + c)
        values = [nearest_half(v) for v in nums]
        defect4 += sum((2 * q - v) ** 2 for q, v in zip(values, nums))
        vector[x], vector[y] = tuple(values[:2]), tuple(values[2:])
    return defect4


def working_precision(vector, f, b, stages):
    need(type(f) is type(b) is int and f >= 0 and b >= 0, 'precision parameters')
    n = len(vector).bit_length() - 1
    need(len(vector) == 1 << n and 0 < stages <= n, 'stage domain')
    need(all(len(z) == 2 and all(type(v) is int for v in z) for z in vector), 'integer entrance')
    magnitude = max(abs(v) for z in vector for v in z)
    if not magnitude:
        return f
    h = magnitude.bit_length() - 1 - f
    guard = (stages - 1).bit_length() + n // 2
    return max(f, b + guard - h)


def execute(vector, f, b, recipe, plans=None, forced_precision=None):
    """Return output numerators at F and local defects; retain output grid F.

    forced_precision is a falsification hook, outside the proved policy.
    """
    need(len(vector) == 512, 'finite native dimension')
    rank = recipe['rank']
    need(type(rank) is int and 1 <= rank <= 8, 'native rank')
    F = working_precision(vector, f, b, rank)
    if forced_precision is not None:
        need(type(forced_precision) is int and forced_precision >= f, 'forced precision')
        F = forced_precision
    if plans is None:
        plans = wrapper_plan(recipe['left']), wrapper_plan(recipe['right'])
    left, right = plans
    value = [(a << (F - f), c << (F - f)) for a, c in vector]
    value = permute(value, right)
    defects = [rounded_stage(value, bit) for bit in range(rank)]
    return permute(value, left), F, defects
