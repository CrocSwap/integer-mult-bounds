"""Route both signed-product shuttles through the two installed binary carriers."""

from contextlib import closing
from functools import partial

from upstream import install

install()
from binary_receiver import Receiver
from installations import COMPACT
from module_atoms import ceil_root
from ordinary import least_power
from staged_carriers import entrance_logs
from fiscal_scans import rectangle_slab, slab_indices, transfer
from streaming_routes import cold_swap_tape, work_tapes, erase
from triangular_ordinary import root_body


def stage_for_width_log(available, maximum, rank_logs):
    """Choose a receiver from the exact scanned width logarithm."""
    if available < 0 or not 0 <= maximum <= len(rank_logs):
        raise ValueError("Use a positive trit width and a supported stage")
    cuts = entrance_logs(rank_logs)
    return next((i for i in range(maximum, 0, -1) if available >= cuts[i-1]), 0)


def ternary(source, target, digits, prefix, gap, suffix, *, maximum, profile):
    if digits < 1:
        raise ValueError("Use a positive trit width and a supported stage")
    stage = stage_for_width_log(digits.bit_length()-1, maximum, profile.rank_logs)
    if stage:
        stage_body(source, target, digits, prefix, gap, suffix, stage, profile)
        return
    with closing(slab_indices(prefix)) as slabs:
        for _ in slabs:
            cold_swap_tape(source, target, digits, 1, gap, suffix)


def stage_body(source, target, digits, prefix, gap, suffix, stage, profile):
    """Run the selected stage on the two full ternary fields."""
    rank_logs = profile.rank_logs
    rank = 1 << rank_logs[stage - 1]
    previous_width = (1 << entrance_logs(rank_logs)[stage - 2]) if stage > 1 else 0
    width = max(previous_width + 1, ceil_root(digits, 250))
    eta = profile.eta
    component_width = ceil_root(digits**eta.numerator, eta.denominator)
    count = (width + component_width - 1) // component_width
    short, longer = divmod(width, count)
    layout = (longer, short + 1, count - longer, short)
    previous = partial(ternary, maximum=stage - 1, profile=profile)
    direct = (digits + width - 1) // width <= rank**8
    backend = Receiver(rank, layout, previous, direct=direct, profile=profile)
    with closing(slab_indices(prefix)) as slabs:
        for _ in slabs:
            root_body(source, target, digits, 1, gap, suffix, backend)


def ordinary_swap(source, target, bits, prefix, gap, suffix, *, profile=COMPACT):
    rank_logs = profile.rank_logs
    if bits < 0 or min(prefix, gap, suffix) < 1:
        raise ValueError("Use a nonnegative width and positive field dimensions")
    if not bits:
        transfer(source, target, prefix * gap * suffix)
        return
    extent = 1 << bits
    digits = least_power(3, extent)
    stages = len(rank_logs)
    if not stage_for_width_log(digits.bit_length()-1, stages, rank_logs):
        from compact_crt import binary_swap

        with closing(slab_indices(prefix)) as slabs:
            for _ in slabs:
                binary_swap(source, target, bits, 1, gap, suffix)
        return
    padded = 3**digits
    with work_tapes(2) as (opened, completed), closing(slab_indices(prefix)) as slabs:
        for _ in slabs:
            rectangle_slab(source, opened, extent, padded, gap, suffix)
            opened.seek(0)
            ternary(opened, completed, digits, 1, gap, suffix, maximum=stages, profile=profile)
            erase(opened)
            completed.seek(0)
            rectangle_slab(completed, target, extent, padded, gap, suffix, restrict=True)
            erase(completed)
