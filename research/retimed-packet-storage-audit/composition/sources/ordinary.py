"""Exchange two complete binary fields, using the funded ternary stages when admitted."""

from functools import partial

from bound import H, entered, entrance_logs
from module_atoms import stage_layout, total_width
from streaming_routes import cold_swap_tape, copy_bytes, work_tapes, write_zeros


def least_power(base, value):
    """Return the least d with base^d at least value."""
    lo, hi = 0, value.bit_length()
    while lo < hi:
        j = (lo + hi) // 2
        if base**j < value:
            lo = j + 1
        else:
            hi = j
    return lo


def rectangle(src, dst, small, big, prefix, gap, suffix, *, restrict=False):
    for _ in range(prefix):
        for _ in range(small):
            for _ in range(gap):
                copy_bytes(src, dst, small * suffix)
                if restrict:
                    copy_bytes(src, None, (big - small) * suffix)
                else:
                    write_zeros(dst, (big - small) * suffix)
        extra = (big - small) * gap * big * suffix
        if restrict:
            copy_bytes(src, None, extra)
        else:
            write_zeros(dst, extra)


def ordinary_swap(source, target, binary_width, prefix, gap, suffix_bytes):
    exchange_binary(source, target, binary_width, prefix, gap, suffix_bytes, H, 6)


def exchange_binary(source, target, bits, prefix, gap, suffix, rank_log, stage):
    if bits < 0 or min(prefix, gap, suffix) < 1:
        raise ValueError("Use nonnegative bit width and positive rectangle extents")
    if bits == 0:
        copy_bytes(source, target, prefix * gap * suffix)
        return
    small = 1 << bits
    e = least_power(3, small)
    if not entered(e, 1, rank_log):
        from compact_crt import binary_swap

        binary_swap(source, target, bits, prefix, gap, suffix)
        return
    big = 3**e
    with work_tapes(2) as (expanded, received):
        rectangle(source, expanded, small, big, prefix, gap, suffix)
        expanded.seek(0)
        ternary(expanded, received, e, prefix, gap, suffix, rank_log, stage)
        received.seek(0)
        rectangle(received, target, small, big, prefix, gap, suffix, restrict=True)


def ternary(source, target, e, prefix, gap, suffix, rank_log, stage):
    while stage and not entered(e, stage, rank_log):
        stage -= 1
    if stage == 0:
        cold_swap_tape(source, target, e, prefix, gap, suffix)
        return
    from growing_binary import Weighted

    rank = 1 << rank_log
    previous = None if stage == 1 else 1 << entrance_logs(rank_log)[stage - 2]
    layout = stage_layout(e, previous)
    call = partial(ternary, rank_log=rank_log, stage=stage - 1)
    core = Weighted(rank, layout, call)
    root_shell(source, target, e, prefix, gap, suffix, core)


def root_shell(source, target, e, prefix, gap, suffix, core):
    """Pad one full stock slab, return both body calls, then exchange the parked digits."""
    w = total_width(core.layout)
    d = (e + w - 1) // w
    D = 2 + least_power(core.n, d)
    stock = core.stock**D
    k = least_power(3, stock)
    if 2 * k >= e:
        raise ArithmeticError("An admitted stage exceeded its physical stock budget")
    c, r = divmod(e - k, w)
    Q = 3**k
    padded = ((Q + stock - 1) // stock) * stock
    high_block = 3 ** (e - k) * gap * 3**e * suffix
    with work_tapes(5) as (expanded, body, genuine, high, low):
        for _ in range(prefix):
            copy_bytes(source, expanded, Q * high_block)
            write_zeros(expanded, (padded - Q) * high_block)
        expanded.seek(0)
        core.body_ordinary(expanded, body, c, prefix * padded, 1, 3**r * gap * Q, 3**r * suffix)
        body.seek(0)
        for _ in range(prefix):
            copy_bytes(body, genuine, Q * high_block)
            copy_bytes(body, None, (padded - Q) * high_block)
        current = genuine
        if k:
            current.seek(0)
            cold_swap_tape(current, high, k, prefix, 3 ** (e - k) * gap, 3 ** (e - k) * suffix)
            current = high
        if r:
            current.seek(0)
            cold_swap_tape(current, low, r, prefix * 3 ** (e - r), gap * 3 ** (e - r), suffix)
            current = low
        current.seek(0)
        copy_bytes(current, target, prefix * 3 ** (2 * e) * gap * suffix)
