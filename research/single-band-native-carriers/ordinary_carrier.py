"""Route both signed-product shuttles through the two installed binary carriers."""

from functools import partial

from upstream import install

install()
from binary_receiver import Receiver
from calibration import COMPACT
from module_atoms import ceil_root
from ordinary import least_power, rectangle
from staged_carriers import admitted_stage, entrance_logs
from streaming_routes import cold_swap_tape, copy_bytes, work_tapes, erase
from triangular_ordinary import root_body


def ternary(source, target, digits, prefix, gap, suffix, *, maximum, profile):
    stage = admitted_stage(digits, maximum, profile.rank_logs)
    if not stage:
        cold_swap_tape(source, target, digits, prefix, gap, suffix)
        return
    stage_body(source, target, digits, prefix, gap, suffix, stage, profile)


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
    root_body(source, target, digits, prefix, gap, suffix, backend)


def ordinary_swap(source, target, bits, prefix, gap, suffix, *, profile=COMPACT):
    rank_logs = profile.rank_logs
    if bits < 0 or min(prefix, gap, suffix) < 1:
        raise ValueError("Use a nonnegative width and positive field dimensions")
    if not bits:
        copy_bytes(source, target, prefix * gap * suffix)
        return
    extent = 1 << bits
    digits = least_power(3, extent)
    stages = len(rank_logs)
    if not admitted_stage(digits, stages, rank_logs):
        from compact_crt import binary_swap

        binary_swap(source, target, bits, prefix, gap, suffix)
        return
    padded = 3**digits
    with work_tapes(2) as (opened, completed):
        rectangle(source, opened, extent, padded, prefix, gap, suffix)
        opened.seek(0)
        ternary(opened, completed, digits, prefix, gap, suffix, maximum=stages, profile=profile)
        erase(opened)
        completed.seek(0)
        rectangle(completed, target, extent, padded, prefix, gap, suffix, restrict=True)
