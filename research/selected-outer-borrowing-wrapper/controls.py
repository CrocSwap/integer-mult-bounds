"""Semantic mutants of the actual wrapper, with named failure observations."""

from unittest.mock import patch

import checks
import outer
from cardinal_counts import Count
from predecessor import require


def identity(source):
    # Checker-only finite fixture scan. Return a valid fresh output, not an alias.
    output = type(source)()
    for _ in range(len(source.cells) - 1):
        output.append(source.read())
        source.step(1)
    source.rewind()
    output.rewind()
    return output


def rejected(action, expected):
    try:
        action()
    except ValueError as error:
        require(str(error) == expected, f"named control failed elsewhere: {error}")
    else:
        raise ValueError("semantic mutant was accepted")


def weighted_callee(source, rows, **kwargs):
    """Actual F_A with A=(2,1) over F3; involutive but not unweighted F_I."""
    current = model_unweighted(source, rows, **kwargs)
    pre, m, gap, suffix = (
        kwargs["p"] * checks.decode(rows),
        3,
        kwargs["gap"],
        kwargs["suffix"],
    )
    for before, tail in ((pre, m**3 * gap * suffix), (pre * m**3 * gap, suffix)):
        counts = [Count.literal(value) for value in (before, tail)]
        extents = [count.marginal() for count in counts]
        for count in counts:
            count.close()
        try:
            following = outer.sign_address(current, kwargs["ring"], 3, *extents)
            current = outer.replace(current, following, source)
        finally:
            for extent in extents:
                extent.close()
    return current


model_unweighted = checks.model_callee


def check_exchange_omission(remainder):
    selected = []
    original_interchange, original_swap = outer.interchange, outer.swap_chunks

    def capture(*args):
        selected[:] = [args[-1] if remainder else args[3]]
        return original_interchange(*args)

    def omit_swap(source, ring, *args):
        if selected and ring is selected[0]:
            return identity(source)
        return original_swap(source, ring, *args)

    with (
        patch.object(outer, "interchange", capture),
        patch.object(outer, "swap_chunks", omit_swap),
    ):
        rejected(
            lambda: checks.case(q=2, w=2, n=1, ell=1, k=2, stock_value=3),
            "complete Boolean-column full-chunk interchange",
        )


def run_controls():
    names = []
    original_pass = outer.body_pass
    endpoint = "complete Boolean-column full-chunk interchange"
    # Removing a pass must preserve ownership so only mathematics detects it.
    for flag in ("negative", "sign"):

        def omit(source, *args, _flag=flag, **kwargs):
            if kwargs.get(_flag, False):
                return identity(source)
            return original_pass(source, *args, **kwargs)

        with patch.object(outer, "body_pass", omit):
            rejected(lambda: checks.case(n=1), endpoint)
        names.append("omitted_" + flag)

    def changed_sign(source, *args, **kwargs):
        if kwargs.get("negative", False):
            kwargs["negative"] = False
        return original_pass(source, *args, **kwargs)

    with patch.object(outer, "body_pass", changed_sign):
        rejected(lambda: checks.case(n=1), endpoint)
    names.append("wrong_initial_sign")

    # Ring identities, not decoded runtime values, select each mutated boundary.
    for remainder in (False, True):
        check_exchange_omission(remainder)
        names.append("omitted_remainder" if remainder else "omitted_high_exchange")

    def wrong_f(source, row_count, **kwargs):
        del row_count, kwargs
        return identity(source)

    with patch.object(checks, "model_callee", wrong_f):
        rejected(
            lambda: checks.case(n=1),
            "each completed F has its full row-pointwise endpoint",
        )
    names.append("wrong_F_endpoint")
    # Let the weaker weighted-F per-call check pass; the full endpoint must fail.
    original_destination = checks.destination

    def weighted_destination(address, n, m, _weights, gap, suffix):
        return original_destination(address, n, m, (2, 1), gap, suffix)

    with (
        patch.object(checks, "model_callee", weighted_callee),
        patch.object(checks, "destination", weighted_destination),
    ):
        rejected(checks.case, endpoint)
    names.append("weighted_involution_is_not_F_I")
    for position in (1, 2):
        result = checks.case(n=1, fail_at=position)
        require(result["failed_at"] == position, "callee failure is propagated")
        names.append(f"callee_failure_{position}_cleanup")
    return names
