"""Closed producer-to-consumer ownership, malformed packets and safe reuse."""
from fractions import Fraction as Q
from hashlib import sha256
from unittest.mock import patch
from gaussian_sources import require
from gaussian_check_exponentials import oracle
from gaussian_check_window import lu


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_core import Core
    from gaussian_prepare import Preparation
    from records import Tape
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from session import erase_marker
    from words import BLANK, RIGHT
    preparation, core = Preparation(), Core()
    p, bits, width = 16, 16, 218
    target_data = [(Q(1, 4), Q(-1, 8)), (Q(-1, 8), Q(1, 4)), (Q(3, 8), Q(-1, 4))]
    rounding = lambda x: Q(int(x*(1 << bits)), 1 << bits)
    def coefficient(argument, positive=False, scale=0):
        lower, upper = oracle(argument, positive, scale)
        lo, hi = (lower*(1 << bits)).__floor__(), (upper*(1 << bits)).__floor__()
        require(lo == hi, "independent coefficient floor separated from its boundary")
        return Q(lo, 1 << bits)
    rho, theta = Q(9, 8), Q(1, 8)
    beta = [rho*j-(rho*j+Q(1, 2)).__floor__() for j in range(3)]
    weights = [coefficient((Q(1, 4)-b*b)/theta) for b in beta]
    kernel = coefficient(rho)
    matrix = [[Q(1) if i == j else (weights[i]*kernel/weights[j] if abs(i-j) == 1 else Q(0))
               for j in range(3)] for i in range(3)]
    low, high = lu([[rounding(v) for v in row] for row in matrix])
    diagonal = coefficient(beta[1]*beta[1], True, 2)
    expected = []
    for component in (0, 1):
        y, x = [Q(0)]*3, [Q(0)]*3
        for i in range(3):
            y[i] = rounding(target_data[i][component]-sum((rounding(low[i][j])*y[j] for j in range(i)), Q(0)))
        for i in reversed(range(3)):
            x[i] = rounding(rounding(1/high[i][i])*(y[i]-sum((rounding(high[i][j])*x[j] for j in range(i+1, 3)), Q(0))))
        expected.append(int(diagonal*x[1]*(1 << p)/(1 << 9)))

    def contents(tape):
        tape.rewind()
        result = bytearray()
        while tape.read() != BLANK:
            result.append(tape.read())
            tape.step(1)
        tape.rewind()
        return bytes(result)

    def packet(data):
        result = Tape()
        for value in data:
            result.append(value)
        result.rewind()
        return result

    def count_bytes(value):
        return bytes([(value >> bit) & 1 for bit in range(max(1, value.bit_length()))]+[RIGHT])

    def changed_header(data, field, value):
        start = 0
        for _ in range(field):
            start = data.index(RIGHT, start)+1
        end = data.index(RIGHT, start)+1
        return data[:start]+count_bytes(value)+data[end:]

    source = Tape()
    with owned(Count.literal(p+2)) as (input_width,):
        for pair in target_data:
            for value in pair:
                integer = int(value*(1 << p))
                with owned(Signed(Count.literal(abs(integer)), integer < 0)) as (encoded,):
                    write_signed(encoded, source, input_width)
        source.rewind()
        source_bytes = contents(source)
        with owned(*(Count.literal(v) for v in (8, 9, 1, 1, p, bits, 0, 3, 1, 1))) as params:
            s, t, u, w, target_p, work_p, target_start, target_length, core_start, core_length = params
            arguments = (s, t, u, w, target_p, work_p, Signed(target_start), target_length, Signed(core_start), core_length)
            saved_parameters = [(bytes(value.tape.cells), value.tape.head) for value in params]
            with no_decode():
                page = preparation.run_explicit(*arguments)
            page_bytes = contents(page)
            require(preparation.closed and not preparation.pool.live
                    and all(tape.head == 1 and all(bit == BLANK for bit in tape.cells)
                            for tape in preparation.pool.tapes), "complete preparation discards dense setup and owned scratch")
            try:
                preparation.run_explicit(*arguments)
            except ValueError as error:
                require("consume prior Gaussian prepared page" in str(error), "protected producer page rejection")
            else:
                raise ValueError("missing protected producer-page rejection")
            require(contents(page) == page_bytes, "protected producer output survives rejected reuse")
            with no_decode():
                returned = core.run(page, source)
            with owned(read_signed(returned, input_width), read_signed(returned, input_width)) as (real, imaginary):
                actual = [(-1 if value.negative else 1)*decode(value.magnitude) for value in (real, imaginary)]
            require(actual == expected and returned.read() == BLANK, "closed producer/consumer equals separate Gaussian source oracle")
            returned.clear()
            erase_marker(returned)

            # These mutations affect cloned packets; the produced page remains intact.
            normalization_start = 0
            for _ in range(11+3+3):
                normalization_start = page_bytes.index(RIGHT, normalization_start)+1
            negative = (1 << width)-(1 << (bits-1))
            negative_bits = bytes((negative >> i) & 1 for i in range(width))
            non_disk = bytes(((3 << (p-1)) >> i) & 1 for i in range(p+2))+source_bytes[p+2:]
            variants = (
                ("page_version", changed_header(page_bytes, 0, 2), source_bytes, "page version"),
                ("precision_order", changed_header(page_bytes, 2, p-1), source_bytes, "precision order"),
                ("core_range", changed_header(page_bytes, 6, 3), source_bytes, "core range"),
                ("odd_boundary_band", changed_header(page_bytes, 9, 3), source_bytes, "two-sided"),
                ("selection_volume", changed_header(page_bytes, 5, 2), source_bytes, "selection volume"),
                ("short_page", page_bytes[:-1], source_bytes, "complete"),
                ("extra_page", page_bytes+b"\x00", source_bytes, "page extent"),
                ("short_input", page_bytes, source_bytes[:-1], "complete"),
                ("extra_input", page_bytes, source_bytes+b"\x00", "target halo"),
                ("input_outside_disk", page_bytes, non_disk, "disk-grid"),
                ("negative_normalization", page_bytes[:normalization_start]+negative_bits+page_bytes[normalization_start+width:],
                 source_bytes, "normalized Gaussian diagonal"),
                ("zero_pivot_reciprocal", page_bytes[:-width]+bytes(width), source_bytes, "pivot reciprocal"),
            )
            controls = ["protected_producer_page"]
            for name, bad_page, bad_source, message in variants:
                first, second = packet(bad_page), packet(bad_source)
                try:
                    with no_decode():
                        try:
                            core.run(first, second)
                        except ValueError as error:
                            require(message in str(error), "specific complete-core rejection: " + name)
                        else:
                            raise ValueError("missing complete-core rejection: " + name)
                    require(contents(first) == bad_page and contents(second) == bad_source,
                            "failed core preserves its borrowed malformed ports")
                    core.idle()
                    require(core.closed and not core.pool.live and core.output.read() == BLANK,
                            "failed core closes and clears its owned output")
                    controls.append(name)
                finally:
                    for tape in (first, second):
                        tape.clear()
                        erase_marker(tape)
            def allocate(*args, **kwargs):
                Tape()
            with patch.object(core, "gather", allocate):
                try:
                    core.run(page, source)
                except ValueError as error:
                    require("physical Tape allocation inside" in str(error), "actual complete-core allocation sentry")
                else:
                    raise ValueError("missing complete-core allocation rejection")
            controls.append("dynamic_physical_tape")
            with no_decode():
                returned = core.run(page, source)
            final_bytes = body(returned)
            try:
                core.run(page, source)
            except ValueError as error:
                require("consume prior Gaussian core output" in str(error), "protected core output rejection")
            else:
                raise ValueError("missing protected core output rejection")
            require(body(returned) == final_bytes and contents(page) == page_bytes and contents(source) == source_bytes,
                    "protected result and original source survive reuse controls")
            controls.append("protected_core_output")
            returned.clear()
            erase_marker(returned)
            page.clear()
            erase_marker(page)
            with no_decode():
                page = preparation.run_explicit(*arguments)
            require(contents(page) == page_bytes, "producer reuse regenerates the same global-H page")
            require(saved_parameters == [(bytes(value.tape.cells), value.tape.head) for value in params],
                    "complete producer preserves all borrowed parameters")
            page.clear()
            erase_marker(page)
            core.idle()
    source.clear()
    erase_marker(source)
    return {"core_values": actual, "controls": controls, "producer_calls": preparation.calls,
            "page_sha256": sha256(page_bytes).hexdigest(), "core_sha256": sha256(final_bytes).hexdigest(),
            "producer_pool_peak": preparation.pool.peak, "core_pool_peak": core.pool.peak}
