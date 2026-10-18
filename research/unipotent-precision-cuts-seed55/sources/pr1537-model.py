"""Paid infinite-order return, Sagar Thakrar / OpenAI Codex, Apache-2.0.

ADD instructions have coefficient +/-1. SCALE instructions double or halve.
Readers are fixed black-box children including their final workspace shear.
"""


def inverse(word):
    return [(op, d, s, -a, b) if op == "ADD" else (op, d, s, b, a)
            for op, d, s, a, b in reversed(word)]


def power(pairs, exponent, compressed=True):
    """Implement (u,v) -> (u + exponent*v,v), restoring every source v."""
    if type(exponent) is not int:
        raise ValueError("integer exponent required")
    if any(u == v for u, v in pairs):
        raise ValueError("distinct shear coordinates required")
    magnitude = abs(exponent)
    sign = 1 if exponent >= 0 else -1
    word = []
    for u, v in pairs:
        if not compressed:
            word.extend([("ADD", u, v, sign, 1)] * magnitude)
            continue
        for bit in range(magnitude.bit_length()):
            if bit:
                word.append(("SCALE", v, v, 2, 1))
            if (magnitude >> bit) & 1:
                word.append(("ADD", u, v, sign, 1))
        word.extend([("SCALE", v, v, 1, 2)] * max(0, magnitude.bit_length() - 1))
    return word


def power_bill(exponent):
    magnitude = abs(exponent)
    return magnitude.bit_count(), 2 * max(0, magnitude.bit_length() - 1)


def boundary_bill(k, m, mode):
    if type(k) is not int or k < 1 or type(m) is not int or m < 1:
        raise ValueError("positive integer child and workspace counts required")
    if mode == "eager":
        return k * m, 0
    if mode != "carry":
        raise ValueError("mode must be eager or carry")
    a, s = power_bill(k)
    b, t = power_bill(k - 1)
    return k - 1 + m * a + b, m * s + t


def pairs_at(base, m):
    return [(base + 2 * j, base + 2 * j + 1) for j in range(m)]


def fixture(k=53, m=5, seed=53):
    """R_i has blocks a*I+b*J, hence R_i P=Q R_i, J^2=0."""
    readers = []
    for i in range(k):
        top, bottom = [], []
        for j in range(m):
            a = 1 if (seed + i * m + j).bit_count() % 2 else -1
            b = (seed + 2 * i + j) % 3 - 1
            top.extend([a, b])
            bottom.extend([0, a])
        readers.append({"reader": [top, bottom]})
    return readers


def emit_node(tree, source, work, m, mode):
    if isinstance(tree, dict):
        word = []
        for d, row in enumerate(tree["reader"]):
            for j, coefficient in enumerate(row):
                word.extend([("ADD", d, source + j, 1 if coefficient > 0 else -1, 1)]
                            * abs(coefficient))
    else:
        word = emit_echo(tree, source, work, m, mode)
    return word + power(pairs_at(source, m), 1)


def emit_group(children, work, m, mode):
    if not children:
        raise ValueError("nonempty child list required")
    boundary_bill(len(children), m, mode)
    word = []
    for i, child in enumerate(children):
        if mode == "carry" and i:
            word += power([(0, 1)], 1)
        word += emit_node(child, work, work + 2 * m, m, mode)
        if mode == "eager":
            word += power(pairs_at(work, m), -1)
    if mode == "carry":
        word += power(pairs_at(work, m), -len(children))
        word += power([(0, 1)], 1 - len(children))
    return word


def emit_echo(children, source, work, m, mode):
    group = emit_group(children, work, m, mode)
    copy = [("ADD", work + j, source + j, 1, 1) for j in range(2 * m)]
    return copy + group + inverse(copy) + inverse(group)


def total_reader(tree):
    if isinstance(tree, dict):
        return tree["reader"]
    matrices = [total_reader(child) for child in tree]
    return [[sum(mat[i][j] for mat in matrices) for j in range(len(matrices[0][0]))]
            for i in range(2)]


def height(tree):
    return 0 if isinstance(tree, dict) else 1 + max(map(height, tree))


def invoice(tree, m, mode, root=False):
    """Counts include all descendants; the root echo omits source drift."""
    if isinstance(tree, dict):
        if root:
            raise ValueError("root must be an echo")
        return sum(abs(x) for row in tree["reader"] for x in row) + m, 0
    child = [invoice(t, m, mode) for t in tree]
    a, s = boundary_bill(len(tree), m, mode)
    return (2 * sum(c[0] for c in child) + 4 * m + 2 * a + (0 if root else m),
            2 * sum(c[1] for c in child) + 2 * s)


def execute(word, state):
    """Literal scalar execution, independent of the row-matrix verifier."""
    from fractions import Fraction
    state = list(state)
    for op, dst, src, num, den in word:
        if op == "ADD":
            state[dst] += num * state[src]
        elif op == "SCALE":
            state[dst] *= Fraction(num, den)
        else:
            raise ValueError("unknown instruction")
    return state
