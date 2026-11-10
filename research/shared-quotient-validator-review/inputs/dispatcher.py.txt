"""Shared forward dispatcher for zxv's PR6072 ordered-coin graphs.

Graph specification: PR6072 at 9011bf83e85ecd0443c789cf03259442f750877d.
State sharing and implementation produced by Nick Petalas. Apache-2.0.
"""

DENOMINATOR = 169
PERIOD = 156
PAIR_STATES = 312
PAIR_COUNT = 144
MAX_STATES = PAIR_STATES * PAIR_COUNT + 4
MAX_REFINEMENTS = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def pair_graph(a, b):
    """Reconstruct the published graph definition, without its test suite."""
    require(type(a) is int and type(b) is int, "integer residues required")
    require(1 <= a <= 12 and 1 <= b <= 12, "nonzero residues required")
    weights = ((13 - a) * (13 - b), (13 - a) * b, a * (13 - b), a * b)
    residues = [tuple(w * pow(2, k, DENOMINATOR) % DENOMINATOR
                      for w in weights) for k in range(PERIOD)]
    nodes = [(k, j) for k, row in enumerate(residues)
             for j in range(sum(row) // DENOMINATOR)]
    require(len(nodes) == PAIR_STATES, "unexpected graph size")
    ids = {node: index for index, node in enumerate(nodes)}
    table = []
    for phase, node in nodes:
        leaves = [PAIR_STATES + output for output, residue in
                  enumerate(residues[phase]) if 2 * residue >= DENOMINATOR]
        row = []
        for coin in (0, 1):
            child = 2 * node + coin
            if child < len(leaves):
                row.append(leaves[child])
            else:
                row.append(ids[((phase + 1) % PERIOD, child - len(leaves))])
        table.append(tuple(row))
    return tuple(table)


def disjoint_bank():
    """Give the 144 graphs common terminal labels, in lexicographic pair order."""
    internal = MAX_STATES - 4
    table, roots = [], []
    for a in range(1, 13):
        for b in range(1, 13):
            offset = len(table)
            roots.append(offset)
            table.extend(tuple(offset + t if t < PAIR_STATES else
                               internal + t - PAIR_STATES for t in row)
                         for row in pair_graph(a, b))
    table.extend((internal + i, internal + i) for i in range(4))
    return tuple(table), tuple(roots)


def validate_graph(table):
    require(5 <= len(table) <= MAX_STATES, "graph size out of bounds")
    require(all(len(row) == 2 for row in table), "binary graph required")
    require(all(type(t) is int and 0 <= t < len(table)
                for row in table for t in row), "invalid target")
    internal = len(table) - 4
    require(all(table[internal + i] == (internal + i, internal + i)
                for i in range(4)), "four fixed absorbing output labels required")


def refine(table, colors):
    """One Moore refinement; empty-word observations separate the terminals."""
    internal = len(table) - 4
    ids, refined = {}, []
    for state, (left, right) in enumerate(table):
        observation = 0 if state < internal else 1 + state - internal
        signature = (observation, colors[left], colors[right])
        refined.append(ids.setdefault(signature, len(ids)))
    return tuple(refined)


def minimize(table, roots):
    validate_graph(table)
    require(len(roots) <= PAIR_COUNT and all(type(r) is int and
            0 <= r < len(table) - 4 for r in roots), "invalid entry table")
    colors = (0,) * (len(table) - 4) + (1, 2, 3, 4)
    history = [colors]
    for _ in range(MAX_REFINEMENTS):
        updated = refine(table, colors)
        history.append(updated)
        stable = len(set(updated)) == len(set(colors))
        colors = updated
        if stable:
            break
    else:
        raise ValueError("refinement exceeded its finite bound")
    count = len(set(colors))
    quotient = [None] * count
    for state, row in enumerate(table):
        translated = tuple(colors[t] for t in row)
        prior = quotient[colors[state]]
        require(prior is None or prior == translated, "unstable quotient")
        quotient[colors[state]] = translated
    require(all(row is not None for row in quotient), "unfilled quotient")
    return tuple(quotient), tuple(colors[r] for r in roots), colors, tuple(history)


def pack_codes(codes, width):
    """Pack little-endian fixed-width codes; unused high bits are zero."""
    require(type(width) is int and 1 <= width <= 16, "invalid code width")
    require(len(codes) <= 2 * MAX_STATES, "too many packed codes")
    require(all(type(c) is int and 0 <= c < 1 << width for c in codes),
            "code does not fit width")
    packed = bytearray((len(codes) * width + 7) // 8)
    for index, code in enumerate(codes):
        position = index * width
        for bit in range(width):
            if code & (1 << bit):
                packed[(position + bit) // 8] |= 1 << ((position + bit) % 8)
    return bytes(packed)


def unpack_codes(packed, count, width):
    require(type(count) is int and 0 <= count <= 2 * MAX_STATES,
            "invalid code count")
    require(type(width) is int and 1 <= width <= 16, "invalid code width")
    require(len(packed) == (count * width + 7) // 8, "wrong payload length")
    codes = []
    for index in range(count):
        position = index * width
        code = sum(((packed[(position + bit) // 8] >>
                     ((position + bit) % 8)) & 1) << bit for bit in range(width))
        codes.append(code)
    return tuple(codes)
