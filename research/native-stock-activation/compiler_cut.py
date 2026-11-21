"""Execute the base plan of the archived binary compiler on true cover rows."""

from math import prod
from functools import cache, cached_property

from factored_frames import Frame, inverse_word
from module_atoms import chart_width, ordinary_shell, rank_one_packet, total_width
from periodic import Job, make_planner, run
from streaming_routes import (
    cold_swap_tape,
    copy_bytes,
    erase,
    regular,
    right_route,
    type_route,
    work_tapes,
)
from tagged_sources import BIT_CALLER, BIT_PIN, PINS, binary_ports, packed, pinned
from ternary_frames import frame_at_three, projector, transpose
from vendor.cover import row_program


def odometer(radix, places):
    """Count in physical lexicographic order without a table of radix values."""
    values = [0] * places
    while True:
        yield tuple(values)
        position = places - 1
        while position >= 0 and values[position] + 1 == radix:
            values[position] = 0
            position -= 1
        if position < 0:
            return
        values[position] += 1


def chart(low, high, dimension):
    values = [a + 3 * x for a, x in zip(low, high, strict=True)]
    return [values[k : k + dimension] for k in range(0, len(values), dimension)]


def low_size(n):
    return prod(3**n - 3**j for j in range(n))


@cache
def source_graph():
    path = "data/binary.json.gz"
    return packed(pinned(path, PINS[path]))


class SourceRule:
    """Generate the true rank tables only when a non-base planner needs them."""

    def __init__(self):
        self.word = binary_ports(source_graph(), packed(pinned(BIT_CALLER, BIT_PIN)))
        self.ambient = self.word.ambient**self.word.power

    @cached_property
    def paid(self):
        return tuple(block.rank for block in self.word.paid_paths())

    @cached_property
    def targets(self):
        return tuple(port.rank for port, keep in self.word.target_paths() if keep)


@cache
def source_rule():
    return SourceRule()


@cache
def source_planner():
    return make_planner(source_rule())


def move_frame(site):
    """Recover the actual nested projection at a MOVE of the archived raw word."""
    graph = source_graph()
    row = graph["program"][site]
    if row[0] != "MOVE":
        raise ValueError("The native site must be a MOVE")
    _, _, old, new = row
    a, b = (graph["frames"][str(i)] for i in (old, new))
    if a["dim"] > b["dim"]:
        a, b = b, a
    small, big = (projector(transpose(f["B"] + f["A"]), f["dim"]) for f in (a, b))
    delta = [
        [y - x for x, y in zip(left, right, strict=True)]
        for left, right in zip(small, big, strict=True)
    ]
    change, rank = frame_at_three(delta)
    return Frame(len(delta), tuple(row_program(change, 3)), tuple(range(rank)))


def base_plan(rank):
    rule = source_rule()
    if rank < 1 or rank // 4 >= rule.ambient:
        raise ValueError("The archived compiler needs its non-base native schedule at this rank")
    return source_planner()


def covered_cut(
    source,
    target,
    layout,
    frame,
    columns,
    groups,
    older,
    gap,
    suffix_bytes,
    ancestor_weights,
    previous_swap,
    stopped_limit,
):
    """Consume [group][regular low][complete high][older][head][gap][tail][suffix]."""
    n = frame.size
    exponent = chart_width(layout)
    high_radix = 3 ** (exponent - 1)
    highs = high_radix ** (n * n)
    lows = low_size(n)
    body = 3 ** (2 * total_width(layout) * n * columns) * gap * suffix_bytes
    suffix = older * body
    canonical = Frame(n, (), (0,))
    matcher = frame.matcher_to(canonical)
    with work_tapes(3) as (routed, split, result):
        right_route(
            source, routed, n, exponent, groups, suffix, matcher, previous_swap=previous_swap
        )
        routed.seek(0)
        type_route(routed, split, groups, lows, highs * suffix)
        erase(routed)
        split.seek(0)
        for low in odometer(3, n * n):
            if regular(low, n):
                for group in range(groups):
                    for high in odometer(high_radix, n * n):
                        u, v = canonical.covered_line(chart(low, high, n), exponent)
                        for old in range(older):

                            def weight(j, i):
                                return ancestor_weights(group, old, j, i)

                            rank_one_packet(
                                split,
                                result,
                                layout,
                                u,
                                v,
                                columns,
                                weight,
                                suffix_bytes,
                                previous_swap,
                                gap=gap,
                                stopped_limit=stopped_limit,
                            )
        erase(split)
        result.seek(0)
        type_route(result, routed, groups, lows, highs * suffix, inverse=True)
        routed.seek(0)
        right_route(
            routed,
            target,
            n,
            exponent,
            groups,
            suffix,
            tuple(inverse_word(matcher)),
            previous_swap=previous_swap,
        )


def archived_move(
    source,
    target,
    layout,
    site,
    columns,
    groups,
    older,
    gap,
    suffix_bytes,
    ancestor_weights,
    stopped_limit,
    previous_swap=cold_swap_tape,
):
    """Run a genuine rank-one MOVE at its original eight-axis ambient."""
    frame = move_frame(site)
    if len(frame.mask) != 1:
        raise ValueError("A higher-rank MOVE requires its completed positive split")
    covered_cut(
        source,
        target,
        layout,
        frame,
        columns,
        groups,
        older,
        gap,
        suffix_bytes,
        ancestor_weights,
        previous_swap,
        stopped_limit,
    )


def base_reversed(
    source,
    target,
    layout,
    dimension,
    columns=1,
    *,
    groups=1,
    older=1,
    gap=1,
    suffix_bytes=1,
    stopped_limit,
    previous_swap=cold_swap_tape,
    ancestor_weights=None,
):
    """Return the real width-rank base plan on arbitrary data with its fresh and older rows."""
    if not 1 <= columns < stopped_limit:
        raise ValueError("The emitted packets must fit the paid stopped base")
    planner = base_plan(dimension)
    if ancestor_weights is None:

        def ancestor_weights(group, old, column, axis):
            return 1

    volume = (
        groups
        * low_size(dimension)
        * 3 ** ((chart_width(layout) - 1) * dimension**2)
        * older
        * 3 ** (2 * total_width(layout) * dimension * columns)
        * gap
        * suffix_bytes
    )
    with work_tapes(2) as (current, other):
        copy_bytes(source, current, volume)

        class TapeBase:
            def leaf(self, job):
                nonlocal current, other
                frame = Frame(dimension, (), job.axes)
                current.seek(0)
                covered_cut(
                    current,
                    other,
                    layout,
                    frame,
                    columns,
                    groups,
                    older,
                    gap,
                    suffix_bytes,
                    ancestor_weights,
                    previous_swap,
                    stopped_limit,
                )
                erase(current)
                current, other = other, current

        # The genuine archived base asks only for one leaf per selected ordered axis.
        # No native grammar is needed at this clause. The paid leaf has a concrete tape body.
        run(
            source_rule(), dimension, [Job(0, tuple(range(dimension)))], TapeBase(), planner=planner
        )
        current.seek(0)
        copy_bytes(current, target, volume)


def base_ordinary(
    source,
    target,
    layout,
    dimension,
    columns=1,
    *,
    groups=1,
    older=1,
    gap=1,
    suffix_bytes=1,
    stopped_limit,
    previous_swap=cold_swap_tape,
):
    """Run the compiled reversed receiver twice, with its actual ordinary shell."""
    rows = groups * low_size(dimension) * 3 ** ((chart_width(layout) - 1) * dimension**2) * older

    def reverse(s, t):
        base_reversed(
            s,
            t,
            layout,
            dimension,
            columns,
            groups=groups,
            older=older,
            gap=gap,
            suffix_bytes=suffix_bytes,
            stopped_limit=stopped_limit,
            previous_swap=previous_swap,
        )

    ordinary_shell(source, target, layout, dimension * columns, rows, gap, suffix_bytes, reverse)
