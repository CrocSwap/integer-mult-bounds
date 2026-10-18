"""Paid terminal repair for fixed signed-permutation reader calls.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
Exact integer model; no supplier, tape, or multiplication-exponent claim.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Child:
    row: tuple[int, ...]
    perm: tuple[int, ...]  # new W[j] = sign(perm[j]) * old W[abs(perm[j])-1]

    def __post_init__(self):
        n = len(self.row)
        if not n or any(type(x) is not int for x in self.row):
            raise ValueError("nonempty integer reader required")
        if (len(self.perm) != n or any(type(x) is not int for x in self.perm)
                or sorted(abs(x) for x in self.perm) != list(range(1, n + 1))):
            raise ValueError("signed permutation required")


def identity(n):
    return tuple(range(1, n + 1))


def compose(left, right):
    """Return left(right(W))."""
    return tuple((1 if x > 0 else -1) * right[abs(x) - 1] for x in left)


def inverse(p):
    ans = [0] * len(p)
    for j, x in enumerate(p):
        ans[abs(x) - 1] = (1 if x > 0 else -1) * (j + 1)
    return tuple(ans)


def row_times(row, p):
    ans = [0] * len(row)
    for a, x in zip(row, p):
        ans[abs(x) - 1] += a * (1 if x > 0 else -1)
    return tuple(ans)


def defect(children):
    """P = G_last ... G_first; E = sum B_i (P_previous - I)."""
    if not children:
        raise ValueError("empty segment")
    n = len(children[0].row)
    p, e = identity(n), [0] * n
    for child in children:
        if len(child.row) != n:
            raise ValueError("mixed widths")
        shifted = row_times(child.row, p)
        e = [a + b - c for a, b, c in zip(e, shifted, child.row)]
        p = compose(child.perm, p)
    return p, tuple(e)


# Instructions are ('A', target, source, +/-1) and ('N', target).
# ADD and NEG operate on arbitrary data; no clean temporary is used.
def permutation_word(p, registers):
    if len(p) != len(registers) or len(set(registers)) != len(registers):
        raise ValueError("register/width mismatch")
    if sorted(abs(x) for x in p) != list(range(1, len(p) + 1)):
        raise ValueError("signed permutation required")
    current = list(range(1, len(p) + 1))
    word = []
    for j, wanted in enumerate(p):
        k = current.index(abs(wanted))
        if j != k:
            a, b = registers[j], registers[k]
            # (a,b) -> (a+b,b) -> (a+b,-a) -> (b,-a) -> (b,a).
            word.extend((('A', a, b, 1), ('A', b, a, -1),
                         ('A', a, b, 1), ('N', b)))
            current[j], current[k] = current[k], current[j]
    word.extend(('N', registers[j]) for j, x in enumerate(p) if x < 0)
    return tuple(word)


def add_word(row, registers, output):
    if len(row) != len(registers) or output in registers:
        raise ValueError("reader ports must be disjoint")
    if any(type(a) is not int for a in row):
        raise ValueError("integer coefficients required")
    # Repeated unit ADDs explicitly pay for coefficient magnitude.
    return tuple(('A', output, src, 1 if a > 0 else -1)
                 for a, src in zip(row, registers) for _ in range(abs(a)))


def reverse_word(word):
    return tuple(('A', op[1], op[2], -op[3]) if op[0] == 'A' else op
                 for op in reversed(word))


def counts(word):
    a = sum(op[0] == 'A' for op in word)
    g = sum(op[0] == 'N' for op in word)
    if a + g != len(word):
        raise ValueError("unknown instruction")
    return {'ADD': a, 'NEG': g, 'instructions': a + g,
            'data_reads': 2 * a + g, 'data_writes': a + g,
            'descriptor_fields': 4 * a + 2 * g}


def boundary_word(children, registers, output):
    p, e = defect(children)
    # E is relative to entry W: restore first, then subtract E W_entry.
    return (permutation_word(inverse(p), registers)
            + add_word(tuple(-a for a in e), registers, output))


def plan(children, required_cuts=(), zero_defect_only=False):
    """Minimum unit instruction cost over canonical repaired partitions.

    Fixed child instructions are common to all partitions. This does not
    optimize the correction circuit or permit edits inside child calls.
    Every required cut exposes canonical eager data and entry workspace.
    """
    if not children:
        raise ValueError("empty batch")
    n, k = len(children[0].row), len(children)
    if any(len(c.row) != n for c in children):
        raise ValueError("mixed widths")
    if any(type(c) is not int or not 0 < c < k for c in required_cuts):
        raise ValueError("required cuts must be interior child indices")
    required = set(required_cuts)
    table = {0: (0, ())}
    for end in range(1, k + 1):
        choices = []
        for start in range(end):
            if start not in table or any(start < c < end for c in required):
                continue
            block = children[start:end]
            if zero_defect_only and any(defect(block)[1]):
                continue
            price = len(boundary_word(block, tuple(range(1, n + 1)), 0))
            previous_price, previous_cuts = table[start]
            choices.append((previous_price + price, previous_cuts + (end,)))
        if not choices:
            raise ValueError("no legal partition")
        table[end] = min(choices)
    return table[k]


def batch_word(children, registers, output, cuts=None, child_words=None):
    k = len(children)
    if cuts is None:
        cuts = plan(children)[1]
    if (not cuts or cuts[-1] != k or tuple(sorted(set(cuts))) != tuple(cuts)
            or cuts[0] < 1):
        raise ValueError("cuts must partition the complete batch")
    if child_words is None:
        child_words = [add_word(c.row, registers, output)
                       + permutation_word(c.perm, registers) for c in children]
    if len(child_words) != k:
        raise ValueError("one fixed word per child required")
    result, start = [], 0
    for end in cuts:
        for word in child_words[start:end]:
            result.extend(word)
        result.extend(boundary_word(children[start:end], registers, output))
        start = end
    return tuple(result)


def recursive_word(depth, row, p, signs, mode='repair', echo=False):
    """Concrete recursive tree of fixed readers, with reused dirty scratch.

    A reader returns (D + row*X, p*X); an echo restores X as well.
    signs sum to one, so every interior reader has the same row as its leaves.
    Both passes and every child's literal inverse are emitted and charged.
    """
    if type(depth) is not int or depth < 0 or (echo and depth == 0):
        raise ValueError("invalid depth/echo")
    if mode not in ('repair', 'eager', 'zero'):
        raise ValueError("unknown mode")
    if not signs or any(type(s) is not int or s not in (-1, 1) for s in signs) or sum(signs) != 1:
        raise ValueError("signed branches must sum to one")
    n = len(row)
    Child(tuple(row), tuple(p))

    def emit(level, reader, source, scratch_start, root_echo=False):
        if level == 0:
            return add_word(reader, source, 0) + permutation_word(p, source)
        workspace = tuple(range(scratch_start, scratch_start + n))
        children = tuple(Child(tuple(s * a for a in reader), tuple(p)) for s in signs)
        if mode == 'eager':
            cuts = tuple(range(1, len(children) + 1))
        else:
            cuts = plan(children, zero_defect_only=(mode == 'zero'))[1]
        words = [emit(level - 1, c.row, workspace, scratch_start + n) for c in children]
        batch = batch_word(children, workspace, 0, cuts, words)
        copy = tuple(('A', w, x, 1) for w, x in zip(workspace, source))
        word = copy + batch + reverse_word(copy) + reverse_word(batch)
        return word if root_echo else word + permutation_word(p, source)

    source = tuple(range(1, n + 1))
    return emit(depth, tuple(row), source, n + 1, echo), 1 + (depth + 1) * n
