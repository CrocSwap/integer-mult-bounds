"""Literal exact S3/sign-character boundary words. Apache-2.0.

Prepared for Arham Tahir with substantial OpenAI Codex assistance.
No predecessor executable is imported.
"""
from itertools import permutations

GROUP = tuple(permutations(range(3)))
IDENTITY = (0, 1, 2)
A = (1, 0, 2)
B = (0, 2, 1)
CHILDREN = (A, B) * 3


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compose(g, h):
    return tuple(g[h[i]] for i in range(3))


def inverse(g):
    return tuple(g.index(i) for i in range(3))


def character(g):
    return (-1) ** sum(g[i] > g[j] for i in range(3) for j in range(i + 1, 3))


def pull(g):
    """(P_g W)_h = W_(g^-1 h); indices follow lexicographic S3 order."""
    return tuple(GROUP.index(compose(inverse(g), h)) for h in GROUP)


READER = tuple(character(h) for h in GROUP)


def signed_swap(i, j):
    return [('ADD', i, j, 1), ('ADD', j, i, -1), ('ADD', i, j, 1)]


def permutation_word(g, offset, width):
    require(g in GROUP and type(width) is int and width > 0, 'invalid group/width')
    p = pull(g)
    seen = set()
    word = []
    for start in range(6):
        if start in seen:
            continue
        cycle = []
        at = start
        while at not in seen:
            seen.add(at)
            cycle.append(at)
            at = p[at]
        require(at == start and len(cycle) in (1, 2, 3), 'invalid regular-action cycle')
        for t in range(width):
            ports = [offset + width * i + t for i in cycle]
            if len(ports) == 2:
                word.extend(signed_swap(*ports))
                word.append(('NEG', ports[1]))
            elif len(ports) == 3:
                word.extend(signed_swap(ports[0], ports[1]))
                word.extend(signed_swap(ports[1], ports[2]))
    return word


def negate_output(width):
    return [('NEG', 12 * width + t) for t in range(width)]


def reader_word(width, reader=READER):
    require(len(reader) == 6 and all(type(c) is int and c in (-1, 0, 1) for c in reader), 'invalid reader')
    return [('ADD', 12 * width + t, 6 * width + j * width + t, c)
            for t in range(width) for j, c in enumerate(reader) if c]


def invert_word(word):
    return [(op[0], op[1], op[2], -op[3]) if op[0] == 'ADD' else op
            for op in reversed(word)]


def batch(width=1, corrections=None, children=CHILDREN, reader=READER):
    """Return literal word and instruction offsets of completed child boundaries."""
    require(type(width) is int and width > 0 and all(g in GROUP for g in children), 'invalid batch')
    # A fixed-child caller must admit the reader before transporting any frame.
    reader_word(width, reader)
    for g in children:
        transformed = [0] * 6
        for i, j in enumerate(pull(g)):
            transformed[j] = reader[i]
        require(tuple(transformed) == tuple(character(g) * c for c in reader), 'reader fails equivariance admission')
    if corrections is None:
        corrections = (IDENTITY,) * (len(children) + 1)
    require(len(corrections) == len(children) + 1 and all(h in GROUP for h in corrections), 'invalid corrections')
    word = permutation_word(corrections[0], 6 * width, width)
    if character(corrections[0]) == -1:
        word.extend(negate_output(width))
    cuts = []
    for g, h in zip(children, corrections[1:]):
        word.extend(reader_word(width, reader))
        word.extend(permutation_word(g, 6 * width, width))
        word.extend(permutation_word(h, 6 * width, width))
        # After an odd child, an even correction requires an output sign flip.
        if character(g) * character(h) == -1:
            word.extend(negate_output(width))
        cuts.append(len(word))
    return word, cuts


def source_word(width, matrix=None):
    n = 6 * width
    if matrix is None:
        matrix = [[int(i == j) for j in range(n)] for i in range(n)]
    require(len(matrix) == n and all(len(row) == n for row in matrix), 'invalid source matrix')
    require(all(type(c) is int and c in (-1, 0, 1) for row in matrix for c in row), 'unsupported source coefficient')
    return [('ADD', n + i, j, c) for i, row in enumerate(matrix) for j, c in enumerate(row) if c]


def echo(width=1, eager=False, matrix=None, corrections=None):
    if eager:
        require(corrections is None, 'eager corrections are fixed')
        corrections = (IDENTITY,) + tuple(inverse(g) for g in CHILDREN)
    if corrections is not None:
        require(len(corrections) == 7 and all(h in GROUP for h in corrections), 'invalid corrections')
        state = corrections[0]
        for g, h in zip(CHILDREN, corrections[1:]):
            state = compose(h, compose(g, state))
        require(state == IDENTITY, 'root batch does not restore workspace')
    e, _ = batch(width, corrections)
    f = source_word(width, matrix)
    return invert_word(e) + f + e + invert_word(f)


def validate_word(word, dimension):
    require(type(dimension) is int and dimension > 0, 'invalid dimension')
    for op in word:
        require(isinstance(op, (list, tuple)) and len(op) in (2, 4), 'malformed instruction')
        require(op[0] in ('ADD', 'NEG'), 'unknown instruction')
        require(len(op) == (4 if op[0] == 'ADD' else 2), 'wrong arity')
        require(type(op[1]) is int and 0 <= op[1] < dimension, 'invalid target')
        if op[0] == 'ADD':
            require(type(op[2]) is int and 0 <= op[2] < dimension and op[2] != op[1], 'invalid/aliased source')
            require(type(op[3]) is int and op[3] in (-1, 1), 'invalid sign')


def replay(word, dimension):
    """Full integer map, signed peak row norm and cancellation-free majorant."""
    validate_word(word, dimension)
    rows = [[int(i == j) for j in range(dimension)] for i in range(dimension)]
    majorant = [1] * dimension
    signed_peak = positive_peak = 1
    for op in word:
        t = op[1]
        if op[0] == 'ADD':
            s, c = op[2:]
            rows[t] = [x + c * y for x, y in zip(rows[t], rows[s])]
            majorant[t] += majorant[s]
        else:
            rows[t] = [-x for x in rows[t]]
        signed_peak = max(signed_peak, sum(abs(x) for x in rows[t]))
        positive_peak = max(positive_peak, majorant[t])
    return rows, signed_peak, positive_peak


def invoice(word):
    additions = sum(op[0] == 'ADD' for op in word)
    negations = len(word) - additions
    # Concrete word-address backend: one complete origin-return trip per scalar op.
    moves = sum(2 * (1 + max(op[1], op[2])) if op[0] == 'ADD' else 2 * (1 + op[1]) for op in word)
    return {'ADD': additions, 'NEG': negations, 'instructions': len(word),
            'data_reads': 2 * additions + negations, 'data_writes': additions + negations,
            'data_accesses': 3 * additions + 2 * negations,
            'descriptor_records': len(word), 'origin_return_word_moves': moves}


def group_price(g, add_price=1, neg_price=1):
    require(add_price > 0 and neg_price > 0, 'prices must be positive')
    v = invoice(permutation_word(g, 0, 1))
    return v['ADD'] * add_price + v['NEG'] * neg_price


def plan(output_cuts=(), workspace_cuts=(), add_price=1, neg_price=1):
    """Six-state exact boundary planner; entrance and terminal correction included."""
    require(all(type(i) is int and 1 <= i <= 6 for i in (*output_cuts, *workspace_cuts)), 'invalid checkpoint')
    states = {h: (group_price(h, add_price, neg_price) + (character(h) == -1) * neg_price, (h,)) for h in GROUP}
    for i, g in enumerate(CHILDREN, 1):
        following = {}
        for p, (cost, path) in states.items():
            for h in GROUP:
                s = compose(h, compose(g, p))
                if i in output_cuts and character(s) != 1:
                    continue
                if (i in workspace_cuts or i == 6) and s != IDENTITY:
                    continue
                new = (cost + group_price(h, add_price, neg_price) + (character(h) == 1) * neg_price, path + (h,))
                if s not in following or new < following[s]:
                    following[s] = new
        states = following
    require(IDENTITY in states, 'no valid boundary path')
    return states[IDENTITY]
