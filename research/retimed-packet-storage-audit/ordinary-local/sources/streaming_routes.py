"""Permute complete ordinary cover packets with a bounded number of sequential spools."""

from contextlib import ExitStack, contextmanager
from fractions import Fraction
from itertools import product
from tempfile import TemporaryFile

from ternary_frames import residue


CHUNK = 65536
ZEROS = bytes(CHUNK)


def read_exact(source, size):
    record = source.read(size)
    if len(record) != size:
        raise EOFError("Incomplete packet on the source tape")
    return record


def copy_bytes(source, target, size):
    while size:
        step = min(CHUNK, size)
        block = read_exact(source, step)
        if target is not None:
            target.write(block)
        size -= step


def write_zeros(target, size):
    while size:
        step = min(CHUNK, size)
        target.write(ZEROS[:step])
        size -= step


def erase(tape):
    size = tape.seek(0, 2)
    tape.seek(0)
    write_zeros(tape, size)
    tape.seek(0)
    tape.truncate()


@contextmanager
def work_tapes(count):
    with ExitStack() as stack:
        tapes = [stack.enter_context(TemporaryFile()) for _ in range(count)]
        try:
            yield tapes
        finally:
            for tape in tapes:
                erase(tape)


def ternary_extent(count):
    digits, extent = 0, 1
    while extent < count:
        digits, extent = digits + 1, extent * 3
    return digits, extent


def join_buckets(buckets, target):
    for tape in buckets:
        size = tape.tell()
        tape.seek(0)
        copy_bytes(tape, target, size)
        erase(tape)


def regular(flat, n):
    """Decide invertibility in the finite ternary residue space."""
    rows = [list(flat[i * n:(i + 1) * n]) for i in range(n)]
    for j in range(n):
        p = next((i for i in range(j, n) if rows[i][j]), None)
        if p is None:
            return False
        rows[j], rows[p] = rows[p], rows[j]
        factor = rows[j][j]
        for i in range(j + 1, n):
            c = rows[i][j] * factor % 3
            if c:
                rows[i][j:] = [(x - c * y) % 3 for x, y in zip(rows[i][j:], rows[j][j:], strict=True)]
    return True


def low_swap(source, target, buckets, axes, left, right, block):
    """Exchange two ternary coordinates through the complete middle range."""
    left, right = sorted((left, right))
    gap, piece = 3 ** (right - left - 1), 3 ** (axes - right - 1) * block
    trit_swap(source, target, buckets, 3**left, gap, piece)


def trit_swap(source, target, buckets, prefixes, gap, piece):
    for _ in range(prefixes):
        for a in range(3):
            for _ in range(gap):
                for b in range(3):
                    copy_bytes(source, buckets[3 * b + a], piece)
        for b in range(3):
            for a in range(3):
                buckets[3 * b + a].seek(0)
            for _ in range(gap):
                for a in range(3):
                    copy_bytes(buckets[3 * b + a], target, piece)
        for tape in buckets:
            erase(tape)


def cold_swap_tape(source, target, digits, prefix, gap, suffix_bytes):
    """The elementary preceding stage. Each corresponding digit pair crosses once."""
    volume = prefix * 3**(2 * digits) * gap * suffix_bytes
    with work_tapes(11) as tapes:
        current, other, *buckets = tapes
        copy_bytes(source, current, volume)
        for j in range(digits):
            current.seek(0)
            trit_swap(current, other, buckets, prefix * 3**j, gap * 3**(digits - 1),
                      suffix_bytes * 3**(digits - 1 - j))
            erase(current)
            current, other = other, current
        current.seek(0)
        copy_bytes(current, target, volume)


def integer_scale(source, target, tapes, prefixes, side, piece, k, inverse):
    """Scale one target by k or k^-1. Output selectors have period k."""
    if k == 1:
        copy_bytes(source, target, prefixes * side * piece)
        return
    selector = -pow(side, -1, k) % k
    runs = tapes[:k]
    for _ in range(prefixes):
        if inverse:
            r = 0
            for _ in range(side):
                copy_bytes(source, runs[r], piece)
                r = (r + selector) % k
            join_buckets(runs, target)
        else:
            old = 0
            for j, tape in enumerate(runs, 1):
                end = (j * side + k - 1) // k
                copy_bytes(source, tape, (end - old) * piece)
                tape.seek(0)
                old = end
            r = 0
            for _ in range(side):
                copy_bytes(runs[r], target, piece)
                r = (r + selector) % k
            for tape in runs:
                erase(tape)


def negate_field(source, target, temporary, prefixes, side, piece):
    """Keep zero fixed and reverse the other opaque blocks, preserving each block."""
    for _ in range(prefixes):
        copy_bytes(source, target, piece)
        copy_bytes(source, temporary, (side - 1) * piece)
        temporary.seek(-piece, 1)
        for remaining in reversed(range(side - 1)):
            copy_bytes(temporary, target, piece)
            if remaining:
                temporary.seek(-2 * piece, 1)
        erase(temporary)


def shift_field(source, target, temporary, prefixes, side, gap, piece, factor, offset):
    """Rotate the target. The controlling source is the earlier radix-side field."""
    for _ in range(prefixes):
        amount = offset
        for _ in range(side if factor is not None else 1):
            for _ in range(gap):
                first = (side - amount) * piece
                copy_bytes(source, temporary, first)
                copy_bytes(source, target, amount * piece)
                temporary.seek(0)
                copy_bytes(temporary, target, first)
                erase(temporary)
            if factor is not None:
                amount = (amount + factor) % side


def high_route(source, target, low, digits, suffix_bytes, word, previous_swap):
    """Run all high coefficients and full carries on one genuine matrix fibre."""
    side = 3**(digits - 1)
    n, axes = len(low), len(low)**2
    volume = side**axes * suffix_bytes
    low = [list(row) for row in low]
    with work_tapes(22) as tapes:
        current, other, *small = tapes
        copy_bytes(source, current, volume)

        def step(operation, *args):
            nonlocal current, other
            current.seek(0)
            operation(current, other, *args)
            erase(current)
            current, other = other, current

        def exchange(i, j):
            left, right = sorted((i, j))
            step(previous_swap, digits - 1, side**left, side**(right - left - 1),
                 side**(axes - right - 1) * suffix_bytes)

        for op, t, *args in word:
            for i, row in enumerate(low):
                dest = i * n + t
                if op == "swap":
                    s = args[0]
                    row[s], row[t] = row[t], row[s]
                    exchange(dest, i * n + s)
                    continue
                if op == "scale":
                    coeff = Fraction(args[0])
                    value = row[t] * coeff
                else:
                    s, coeff = args
                    value = row[t] + row[s] * coeff
                row[t] = residue(value, 3)
                offset = residue((Fraction(value) - row[t]) / 3, side)
                if op == "scale":
                    numerator, denominator = coeff.numerator, coeff.denominator
                    if max(abs(numerator), denominator) > len(small):
                        raise ValueError("Scaling exceeds the proved raw factor alphabet")
                    prefixes = side**dest
                    piece = side**(axes - dest - 1) * suffix_bytes
                    if abs(numerator) > 1:
                        step(integer_scale, small, prefixes, side, piece, abs(numerator), False)
                    if numerator < 0:
                        step(negate_field, small[0], prefixes, side, piece)
                    if denominator > 1:
                        step(integer_scale, small, prefixes, side, piece, denominator, True)
                    if offset:
                        step(shift_field, small[0], prefixes, side, 1, piece, None, offset)
                else:
                    src = i * n + s
                    backwards = src > dest
                    if backwards:
                        exchange(src, dest)
                        src, dest = dest, src
                    step(shift_field, small[0], side**src, side, side**(dest - src - 1),
                         side**(axes - dest - 1) * suffix_bytes, residue(coeff, side), offset)
                    if backwards:
                        exchange(src, dest)
        current.seek(0)
        copy_bytes(current, target, volume)


def low_target(source, target, buckets, axes, t, s, coefficient, block):
    """Permute three target blocks. Source s, when present, is earlier than t."""
    piece = 3 ** (axes - t - 1) * block
    if s is None:
        groups, radix, gap = 3**t, 1, 1
    else:
        groups, radix, gap = 3**s, 3, 3 ** (t - s - 1)
    for _ in range(groups):
        for src_value in range(radix):
            for _ in range(gap):
                for d in range(3):
                    dest = coefficient * d if s is None else d + coefficient * src_value
                    copy_bytes(source, buckets[dest % 3], piece)
                join_buckets(buckets[:3], target)


def low_passes(word, n):
    """Expand each row operation into complete, fixed-alphabet physical passes."""
    for op, t, *args in word:
        for row in range(n):
            target = row * n + t
            if op == "swap":
                yield "swap", target, row * n + args[0], 0
            elif op == "scale":
                coefficient = residue(args[0], 3)
                if coefficient != 1:
                    yield "target", target, None, coefficient
            else:
                s, value = args
                source = row * n + s
                coefficient = residue(value, 3)
                if coefficient:
                    if source < target:
                        yield "target", target, source, coefficient
                    else:
                        yield "swap", target, source, 0
                        yield "target", source, target, coefficient
                        yield "swap", target, source, 0


def right_route(source, target, n, digits, groups, suffix_bytes, word, *, previous_swap=None):
    """Route [group][lex-regular low][whole high matrix][opaque suffix].

    Padding, all elementary low gates, and removal each access tapes in order.
    The per-low high router uses the full original low and every high carry.
    """
    if n < 1 or digits < 1 or groups < 0 or suffix_bytes < 0:
        raise ValueError("Invalid right-route shape")
    if digits > 1 and previous_swap is None:
        raise ValueError("A high route needs its completed preceding ordinary stage")
    if not groups or not suffix_bytes:
        return
    axes = n * n
    high = 3 ** (axes * (digits - 1))
    block = high * suffix_bytes
    with work_tapes(11) as tapes:
        current, other, *buckets = tapes
        for _ in range(groups):
            for flat in product(range(3), repeat=axes):
                if not regular(flat, n):
                    write_zeros(current, block)
                elif digits == 1:
                    copy_bytes(source, current, block)
                else:
                    low = [flat[i * n:(i + 1) * n] for i in range(n)]
                    high_route(source, current, low, digits, suffix_bytes, word, previous_swap)
            for op, t, s, coefficient in low_passes(word, n):
                current.seek(0)
                if op == "swap":
                    low_swap(current, other, buckets, axes, t, s, block)
                else:
                    low_target(current, other, buckets, axes, t, s, coefficient, block)
                erase(current)
                current, other = other, current
            current.seek(0)
            for flat in product(range(3), repeat=axes):
                copy_bytes(current, target if regular(flat, n) else None, block)
            erase(current)


def type_route(source, target, rows, types, suffix_bytes, *, inverse=False):
    """Transpose complete [rows][types] slabs or return them in the opposite order."""
    if rows < 0 or types < 1 or suffix_bytes < 0:
        raise ValueError("Invalid type-splitter shape")
    if not rows or not suffix_bytes:
        return
    digits, extent = ternary_extent(types)
    if not digits:
        copy_bytes(source, target, rows * suffix_bytes)
        return
    pad = (extent - types) * suffix_bytes
    with work_tapes(5) as tapes:
        current, other, *buckets = tapes
        if inverse:
            copy_bytes(source, current, types * rows * suffix_bytes)
            write_zeros(current, rows * pad)
        else:
            for _ in range(rows):
                copy_bytes(source, current, types * suffix_bytes)
                write_zeros(current, pad)
        steps = reversed(range(digits)) if inverse else range(digits)
        for i in steps:
            current.seek(0)
            rest = (3 ** (digits - i - 1)) * suffix_bytes
            for _ in range(3**i):
                if inverse:
                    for tape in buckets:
                        copy_bytes(current, tape, rows * rest)
                        tape.seek(0)
                    for _ in range(rows):
                        for tape in buckets:
                            copy_bytes(tape, other, rest)
                    for tape in buckets:
                        erase(tape)
                else:
                    for _ in range(rows):
                        for tape in buckets:
                            copy_bytes(current, tape, rest)
                    join_buckets(buckets, other)
            erase(current)
            current, other = other, current
        current.seek(0)
        if inverse:
            for _ in range(rows):
                copy_bytes(current, target, types * suffix_bytes)
                copy_bytes(current, None, pad)
        else:
            copy_bytes(current, target, rows * types * suffix_bytes)
            copy_bytes(current, None, rows * pad)
