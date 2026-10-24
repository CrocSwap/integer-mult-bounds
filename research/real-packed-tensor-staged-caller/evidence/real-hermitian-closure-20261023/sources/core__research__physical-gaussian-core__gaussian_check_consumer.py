"""Whole consumer conformance on independent supplied-factor fixtures."""
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
from gaussian_sources import active, require
from gaussian_check_window import inverse, lu, schur


def run():
    from cardinal_counts import Count
    from check_support import no_decode
    from gaussian_core import Core
    from gaussian_rationals import write_count
    from records import Tape
    from ring_check_words import body, decode
    from ring_words import Signed, read_signed, write_signed
    from router_metadata import owned
    from session import erase_marker
    from words import BLANK
    spec = importlib.util.spec_from_file_location("gaussian_consumer_reference",
        active().branchfree_package / "code/branchfree.py")
    reference = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reference)
    owner = Core()
    results = []
    for length, bits in ((1, 16), (5, 24)):
        p, band = 16, 2
        target_length = 1 if length == 1 else 6
        selection = [0] if length == 1 else [0, 1, 3, 4, 5]
        inside = [] if length == 1 else [1, 2, 3]
        boundary = [0] if length == 1 else [0, 4]
        width = bits+8*p+8*(p+1).bit_length()+34
        q = Q(1, 16)
        matrix = [[Q(int(i == j)) for j in range(length)] for i in range(length)]
        if inside:
            for i in inside:
                for j in inside:
                    matrix[i][j] = q**((i-j)**2)
            for a, b in ((0, 1), (1, 0), (3, 4), (4, 3)):
                matrix[a][b] = Q(1, 64)
        block = [[matrix[i][j] for j in inside] for i in inside]
        exact_s = schur(matrix, boundary, inside, inverse(block) if inside else [])
        rounding = lambda x: Q(int(x*(1 << bits)), 1 << bits)
        rounded_s = [[rounding(v) for v in row] for row in exact_s]
        exact_low, exact_high = lu(rounded_s)
        low = [[rounding(v) for v in row] for row in exact_low]
        high = [[rounding(v) for v in row] for row in exact_high]
        reciprocal = [rounding(1/exact_high[i][i]) for i in range(len(boundary))]
        factors = reference.prepare(q, [Q(1)]*len(inside), bits) if inside else None
        target = [(Q((3*i+2) % 7-3, 8), Q((5*i+1) % 7-3, 8)) for i in range(target_length)]
        expected_components = []
        for component in (0, 1):
            b = [target[i][component] for i in selection]
            y = reference.apply(factors, [b[i] for i in inside], reference.counter()) if inside else []
            rhs = [rounding(b[i]-sum((rounding(matrix[i][j])*y[k] for k, j in enumerate(inside)), Q(0)))
                   for i in boundary]
            forward, x_b = [Q(0)]*len(boundary), [Q(0)]*len(boundary)
            for i in range(len(boundary)):
                forward[i] = rounding(rhs[i]-sum((low[i][j]*forward[j] for j in range(i)), Q(0)))
            for i in reversed(range(len(boundary))):
                x_b[i] = rounding(reciprocal[i]*(forward[i]-sum((high[i][j]*x_b[j]
                                                                for j in range(i+1, len(boundary))), Q(0))))
            rhs_i = [rounding(b[i]-sum((rounding(matrix[i][j])*x_b[k] for k, j in enumerate(boundary)), Q(0)))
                     for i in inside]
            x_i = reference.apply(factors, rhs_i, reference.counter()) if inside else []
            merged = [Q(0)]*length
            for positions, values in ((boundary, x_b), (inside, x_i)):
                for i, value in zip(positions, values):
                    merged[i] = value
            j_scale = (32*p-1).bit_length()
            expected_components.append([int(value*Q(1, 2)*(1 << p)/(1 << j_scale)) for value in merged])
        page, source = Tape(), Tape()
        with owned(Count.literal(width), Count.literal(p+2)) as (work_width, input_width):
            def put_count(value):
                with owned(Count.literal(value)) as (count,):
                    write_count(count, page)
            def put(value, destination=page, field=work_width, precision=bits):
                integer = int(value*(1 << precision))
                with owned(Signed(Count.literal(abs(integer)), integer < 0)) as (encoded,):
                    write_signed(encoded, destination, field)
            try:
                for value in (1, p, bits, width, length, target_length, 0, length, len(boundary), band, 1):
                    put_count(value)
                for value in selection:
                    put_count(value)
                for value in (length, len(inside), len(boundary)):
                    put_count(value)
                if inside:
                    for name in ("weights", "inva", "f", "invf", "h"):
                        for value in factors[name]:
                            put(value)
                    edges = inside[:1]+inside[-1:]
                    for rows, columns in ((boundary, edges), (edges, boundary)):
                        for i in rows:
                            for j in columns:
                                put(rounding(matrix[i][j]))
                for _ in range(length):
                    put(Q(1, 2))
                for i in range(len(boundary)):
                    for j in range(i-band, i):
                        put(low[i][j] if j >= 0 else Q(0))
                for i in reversed(range(len(boundary))):
                    for j in range(i+1, i+band+1):
                        put(high[i][j] if j < len(boundary) else Q(0))
                    put(reciprocal[i])
                for real, imaginary in target:
                    put(real, source, input_width, p)
                    put(imaginary, source, input_width, p)
                page.rewind()
                source.rewind()
                saved = [(bytes(t.cells), t.head) for t in (page, source)]
                local_calls, boundary_calls = owner.interior.calls, owner.boundary.calls
                with no_decode():
                    output = owner.run(page, source)
                raw = body(output)
                actual = []
                for i in range(length):
                    pair = []
                    for _ in range(2):
                        with owned(read_signed(output, input_width)) as (value,):
                            pair.append((-1 if value.negative else 1)*decode(value.magnitude))
                    actual.append(pair)
                require(actual == [list(pair) for pair in zip(*expected_components)] and output.read() == BLANK,
                        "complete core matches independently staged supplied-factor fixture")
                require(any(value for pair in actual for value in pair), "nonzero normalized core output")
                require(saved == [(bytes(t.cells), t.head) for t in (page, source)], "complete core preserves page and input")
                require(owner.interior.calls-local_calls == (4 if inside else 0)
                        and owner.boundary.calls-boundary_calls == 2, "both interior passes and boundary solve for both components")
                owner.idle()
                require(owner.closed and not owner.pool.live
                        and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in owner.pool.tapes),
                        "complete core restores all owned roles")
                results.append({"source_length": length, "target_length": target_length,
                                "work_precision": bits, "values": actual,
                                "sha256": sha256(raw).hexdigest(), "pool_peak": owner.pool.peak,
                                "interior_calls": owner.interior.calls-local_calls,
                                "boundary_calls": owner.boundary.calls-boundary_calls})
                output.clear()
                erase_marker(output)
            finally:
                for tape in (page, source):
                    tape.clear()
                    erase_marker(tape)
    return {"packets": results,
            "scope": "whole consumer conformance with independent supplied factors; the true global-Gaussian producer join is a separate check"}
