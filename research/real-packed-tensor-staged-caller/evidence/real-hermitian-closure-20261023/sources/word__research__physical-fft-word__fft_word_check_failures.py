"""Boundary, ownership and corrupted coefficient-return controls."""
from unittest.mock import patch
from fft_word_sources import require


def rejected_return(raw, width, message, short_output=False):
    from cardinal_counts import Count
    from check_support import no_decode
    from fft_word_codec import unpack
    from fft_word_plan import WordPlan
    from records import Tape
    from ring_check_words import body, tape
    from scratch_pool import ScratchPool
    from session import OuterScope, erase_marker, sealed_constructors
    source, output = tape(raw), Tape()
    n = Count.literal(width)
    plan = WordPlan(n)
    pool = ScratchPool(128)
    scope = OuterScope(pool)
    try:
        with sealed_constructors(), scope.installed():
            try:
                plan.compile()
                if short_output:
                    plan.output_bits.close()
                    plan.fields["output_bits"] = Count.literal(1)
                try:
                    with no_decode():
                        unpack(source, output, plan)
                except ValueError as error:
                    require(message in str(error), "intended coefficient-return rejection: " + str(error))
                else:
                    raise ValueError("missing coefficient-return rejection")
            finally:
                plan.close()
                pool.empty()
        require(body(source) == raw, "rejected coefficient return remains borrowed")
    finally:
        output.clear()
        erase_marker(output)
        n.close()
        for value in pool.tapes:
            erase_marker(value)


def run():
    from cardinal_counts import Count
    from check_composed import encode
    from check_support import no_decode
    from fft_word_check_codec import fixtures
    from fft_word_check_fft import packet
    from fft_word_engine import FftWord
    from records import Tape
    from ring_check_words import body
    from session import erase_marker
    from words import BLANK
    owner = FftWord()
    controls = []
    for name, a, b, width, message in (
        ("zero_width", 0, 0, 0, "positive cardinality"),
        ("left_magnitude_too_wide", 8, 1, 3, "fits declared word width"),
        ("right_magnitude_too_wide", 1, 8, 3, "fits declared word width"),
    ):
        values = tuple(Count.literal(v) for v in (a, b, width))
        saved = tuple((bytes(v.tape.cells), v.tape.head) for v in values)
        try:
            try:
                with no_decode():
                    owner.run(*values)
            except ValueError as error:
                require(message in str(error), "intended word admission failure")
                controls.append(name)
            else:
                raise ValueError("missing word admission rejection")
            require(saved == tuple((bytes(v.tape.cells), v.tape.head) for v in values),
                    "rejected word call preserves inputs")
            require(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
                    "rejected word call restores its owner")
            owner.idle()
        finally:
            for value in values:
                value.close()
    packet(owner, 3, 5, 4, consume=False)
    retained = body(owner.output)
    values = tuple(Count.literal(v) for v in (1, 1, 2))
    try:
        try:
            owner.run(*values)
        except ValueError as error:
            require("consume prior FFT-word output" in str(error) and body(owner.output) == retained,
                    "protected word return stays intact")
            controls.append("protected_output")
        else:
            raise ValueError("missing protected word rejection")
    finally:
        for value in values:
            value.close()
        owner.output.clear()
        erase_marker(owner.output)
    values = tuple(Count.literal(v) for v in (1, 1, 17))
    try:
        with patch("fft_word_engine.pack", lambda *_: Tape()):
            try:
                owner.run(*values)
            except ValueError as error:
                require("physical Tape allocation inside" in str(error), "fixed tape inventory guard")
                controls.append("dynamic_physical_tape")
            else:
                raise ValueError("missing dynamic tape rejection")
        owner.idle()
        require(owner.closed and not owner.pool.live and owner.output.read() == BLANK,
                "allocation rejection restores the word owner")
    finally:
        for value in values:
            value.close()
    _, raw, (_, _, _, r, p) = fixtures(31, 29, 5)
    component = p+2
    for name, position, message in (
        ("nonzero_imaginary", component, "nonnegative real"),
        ("negative_coefficient", component-1, "nonnegative real"),
        ("coefficient_headroom", p-1, "coefficient headroom"),
        ("nonzero_dummy_record", 2*r*component, "zero second product record"),
    ):
        changed = bytearray(raw)
        changed[position] = 1
        rejected_return(bytes(changed), 5, message)
        controls.append(name)
    rejected_return(raw[:-1], 5, "zero second product record")
    controls.append("short_return")
    rejected_return(raw+b"\x00", 5, "complete normalized word-product packet")
    controls.append("extra_return")
    rejected_return(raw, 5, "zero high product padding", short_output=True)
    controls.append("shortened_output_extent")
    coefficients = [(0, 0)]*(2*r)
    coefficients[r-1] = (64, 0)
    rejected_return(encode(coefficients, component), 5, "zero final carry")
    controls.append("nonzero_final_carry")
    return {"controls": controls, "positive_after_rejections": packet(owner, 127, 125, 7)}
