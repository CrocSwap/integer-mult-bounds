"""Independent boundary controls using exact integers and physical digit code."""
from pathlib import Path
import tempfile
from unittest.mock import patch

import bindings
from frontend import Layout, compile_route, need


def rejects(action, text):
    try:
        action()
    except ValueError as error:
        need(text in str(error), "expected rejection boundary: "+text)
        return str(error)
    raise ValueError("negative control was accepted: "+text)


def source_and_compiler(compiler):
    with tempfile.TemporaryDirectory(prefix="compiler-t74-source-control-") as directory:
        root = Path(directory)
        source = root/bindings.COMPILER
        source.parent.mkdir(parents=True)
        source.write_bytes((bindings.ROOT/bindings.COMPILER).read_bytes()+b"\n# altered control\n")
        with patch.object(bindings, "ROOT", root):
            rejected_source = rejects(bindings.authenticate, "source bytes changed")
    layout = Layout((2, 1), 1)
    malformed = [[[0, 0], [0, 1]] for _ in layout.labels]
    rejected_permutation = rejects(lambda: compile_route(compiler, layout, malformed),
                                   "complete original local permutation")
    truncated = [[[0, 1]] for _ in layout.labels]
    rejected_axis = rejects(lambda: compile_route(compiler, layout, truncated),
                           "one source circuit per actual axis")
    return dict(altered_source=rejected_source, duplicate_wire=rejected_permutation,
                omitted_axis=rejected_axis)


def physical_macros(owner):
    from bridge import GlobalBoundary
    from cardinal_counts import Count
    from check_support import bits, no_decode
    from session import borrowed_tape, erase_marker, sealed_constructors
    from words import BLANK

    boundary = GlobalBoundary(owner)
    boundary.rearm()
    signed_cases = division_cases = exact_rejections = range_rejections = 0
    with no_decode(), sealed_constructors(), boundary.scope.installed():
        # A host exact-integer oracle supplies expected bits. The tested routine
        # processes only digits and a one-bit carry, including signed overflow.
        for width in range(2, 7):
            count = Count.literal(width)
            try:
                for value in range(-(1 << (width-1)), 1 << (width-1)):
                    for negate in (False, True):
                        source, target = boundary.pool.acquire(), boundary.pool.acquire()
                        try:
                            for bit in range(width):
                                source.append((value >> bit) & 1)
                            source.rewind()
                            if negate and value == -(1 << (width-1)):
                                rejects(lambda: boundary.signed_component(source, target, count, True),
                                        "signed phase headroom")
                                range_rejections += 1
                            else:
                                boundary.signed_component(source, target, count, negate)
                                expected = -value if negate else value
                                need(bits(borrowed_tape(target)) == bytes((expected >> bit) & 1 for bit in range(width)),
                                     "independent signed-component integer oracle")
                                signed_cases += 1
                        finally:
                            source.clear()
                            target.clear()
            finally:
                count.close()

        # Exact quotient guards must distinguish divisibility from mere
        # toward-zero rounding, and reject a quotient outside signed headroom.
        for pair, low, output_width, expected_error in (
                ((24, -24), 2, 4, None), ((0, -4), 2, 2, None),
                ((25, -24), 2, 4, "exact compiled switch divisibility"),
                ((24, -25), 2, 4, "exact compiled switch divisibility"),
                ((32, 0), 2, 4, "truncated root signed headroom")):
            width = 8
            counts = tuple(Count.literal(x) for x in (width, low, output_width, 1))
            boundary.current = boundary.pool.acquire()
            try:
                for value in pair:
                    for bit in range(width):
                        boundary.current.append((value >> bit) & 1)
                boundary.current.rewind()
                if expected_error:
                    rejects(lambda: boundary.exact_divide(*counts), expected_error)
                    exact_rejections += 1
                else:
                    boundary.exact_divide(*counts)
                    expected = bytes((value//(1 << low) >> bit) & 1
                                     for value in pair for bit in range(output_width))
                    need(bits(borrowed_tape(boundary.current)) == expected, "independent exact quotient oracle")
                    division_cases += 1
            finally:
                boundary.current.clear()
                boundary.current = None
                for count in counts:
                    count.close()
        boundary.pool.empty()
    boundary.idle()
    for tape in (*boundary.pool.tapes, boundary.output):
        erase_marker(tape)
    boundary.closed = True
    need(all(t.head == 1 and all(x == BLANK for x in t.cells) for t in boundary.pool.tapes),
         "physical macro controls erase owned bodies and markers")
    return dict(signed_cases=signed_cases, signed_overflow_rejections=range_rejections,
                exact_quotients=division_cases, division_or_headroom_rejections=exact_rejections)


def floor_controls(context, certify):
    import active_plan
    from cardinal_counts import Count
    from check_support import inspect_count
    calls = []

    def original_boundary(value, numerator, denominator):
        # Sentinel at the unchanged-helper boundary. It proves fallback
        # delegation without spending a replay on another enormous power.
        calls.append([inspect_count(value), numerator, denominator])
        raise ValueError("unfolded original metadata boundary")

    with patch.object(active_plan, "floor_power", original_boundary):
        with context() as (table, uses, misses):
            wrong = dict(table)
            wrong[(997, 1000, 6)] += 1
            corruption = rejects(lambda: certify(wrong), "finite floor-power certificate")
            value = Count.literal(33)
            try:
                fallback = rejects(lambda: active_plan.floor_power(value, 997, 1000),
                                   "unfolded original metadata boundary")
            finally:
                value.close()
            need(not uses and misses == [[997, 1000]] and calls == [[33, 997, 1000]],
                 "out-of-domain metadata reaches unchanged-helper boundary")
    return dict(incorrect_entry=corruption, out_of_domain=fallback,
                delegated_parameters=calls, exact_table_entries=len(table))
