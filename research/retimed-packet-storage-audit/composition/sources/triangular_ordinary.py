"""Exchange two complete binary fields through the six native stages."""

from functools import partial

from module_atoms import ceil_root, total_width
from ordinary import least_power, rectangle
from receiver import Receiver
from staged_carriers import RANK_LOGS, admitted_stage, entrance_logs, stage_layout
from streaming_routes import cold_swap_tape, copy_bytes, work_tapes, write_zeros


def root_body(source, target, e, prefix, gap, suffix, core):
    width = total_width(core.layout)
    atoms = (e + width - 1) // width
    height = least_power(core.n, atoms)
    # The rightmost fresh charts are used first. Every level still needs independent owners.
    chart_levels = max(0, height - 8)
    rows = core.owners ** (2 + height) * (core.low * core.high) ** chart_levels
    k = least_power(3, rows)
    if 2 * k >= e:
        raise ArithmeticError("The admitted native stock exceeds half its operand")
    c, r = divmod(e - k, width)
    if c < core.n:
        raise ArithmeticError("The admitted ordinary call did not reach its native supplier")
    extent = 3**k
    padded = ((extent + rows - 1) // rows) * rows
    piece = 3 ** (2 * e - k) * gap * suffix
    with work_tapes(5) as (expanded, body, genuine, high, trailing):
        for _ in range(prefix):
            copy_bytes(source, expanded, extent * piece)
            write_zeros(expanded, (padded - extent) * piece)
        expanded.seek(0)
        core.body_ordinary(
            expanded, body, c, prefix * padded, 1, 3**r * gap * extent, 3**r * suffix
        )
        body.seek(0)
        for _ in range(prefix):
            copy_bytes(body, genuine, extent * piece)
            copy_bytes(body, None, (padded - extent) * piece)
        current = genuine
        if k:
            current.seek(0)
            cold_swap_tape(current, high, k, prefix, 3 ** (e - k) * gap, 3 ** (e - k) * suffix)
            current = high
        if r:
            current.seek(0)
            cold_swap_tape(current, trailing, r, prefix * 3 ** (e - r), gap * 3 ** (e - r), suffix)
            current = trailing
        current.seek(0)
        copy_bytes(current, target, prefix * extent * piece)


def ternary(source, target, e, prefix, gap, suffix, *, maximum, rank_logs=RANK_LOGS):
    stage = admitted_stage(e, maximum, rank_logs)
    if not stage:
        cold_swap_tape(source, target, e, prefix, gap, suffix)
        return
    rank = 1 << rank_logs[stage - 1]
    previous_width = 0 if stage == 1 else 1 << entrance_logs(rank_logs)[stage - 2]
    layout = stage_layout(e, previous_width, ceil_root)
    width = total_width(layout)
    direct = (e + width - 1) // width <= rank**8
    previous = partial(ternary, maximum=stage - 1, rank_logs=rank_logs)
    core = Receiver(rank, layout, previous, direct=direct)
    root_body(source, target, e, prefix, gap, suffix, core)


def ordinary_swap(source, target, bits, prefix, gap, suffix):
    if bits < 0 or min(prefix, gap, suffix) < 1:
        raise ValueError("Use positive rectangular fields and a nonnegative width")
    if not bits:
        copy_bytes(source, target, prefix * gap * suffix)
        return
    extent = 1 << bits
    e = least_power(3, extent)
    if not admitted_stage(e):
        from compact_crt import binary_swap

        binary_swap(source, target, bits, prefix, gap, suffix)
        return
    padded = 3**e
    with work_tapes(2) as (opened, completed):
        rectangle(source, opened, extent, padded, prefix, gap, suffix)
        opened.seek(0)
        ternary(opened, completed, e, prefix, gap, suffix, maximum=6)
        completed.seek(0)
        rectangle(completed, target, extent, padded, prefix, gap, suffix, restrict=True)
