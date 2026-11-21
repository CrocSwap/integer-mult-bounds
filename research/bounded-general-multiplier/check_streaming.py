"""Check complete low packets and type slabs against direct coordinate arithmetic."""

from io import BytesIO
from itertools import product
from fractions import Fraction
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from factored_frames import apply_row, inverse_word
from low_rank import group_sizes, unrank_matrix
from streaming_routes import cold_swap_tape, regular, right_route, type_route


def records(count):
    return b"".join(i.to_bytes(4, "little") for i in range(count))


def exercise_types():
    cases = count = 0
    for rows, types, suffix in product((1, 2, 5), (1, 2, 3, 4, 7, 9, 10, 16, 48, 144), (1, 3)):
        data = records(rows * types * suffix)
        target = BytesIO()
        source = BytesIO(data + b"tail")
        type_route(source, target, rows, types, 4 * suffix)
        assert source.read() == b"tail"
        actual = target.getvalue()
        want = b"".join(data[(r * types + t) * suffix * 4:(r * types + t + 1) * suffix * 4]
                        for t in range(types) for r in range(rows))
        assert actual == want
        back = BytesIO()
        type_route(BytesIO(actual), back, rows, types, 4 * suffix, inverse=True)
        assert back.getvalue() == data
        changed = bytearray(actual)
        for t in range(types):
            for r in range(rows):
                p = (t * rows + r) * 4 * suffix
                changed[p] ^= (17 * t + 3 * r + 1) % 256
        expected = bytearray(data)
        for r in range(rows):
            for t in range(types):
                expected[(r * types + t) * 4 * suffix] ^= (17 * t + 3 * r + 1) % 256
        returned = BytesIO()
        type_route(BytesIO(changed), returned, rows, types, 4 * suffix, inverse=True)
        assert returned.getvalue() == expected
        cases += 1
        count += rows * types * suffix
    return cases, count


def exercise_rows():
    word = (("swap", 0, 1), ("add", 0, 1, Fraction(3, 5)), ("scale", 1, Fraction(-2, 5)),
            ("add", 1, 0, Fraction(4, 7)))
    cases = count = 0
    for n, w, groups, suffix in ((1, 4, 3, 5), (2, 1, 3, 3), (2, 2, 3, 2), (2, 3, 1, 1), (3, 1, 2, 2)):
        gates = (("scale", 0, Fraction(-2, 5)),) if n == 1 else word
        size, side = group_sizes(n)[-1], 3 ** (w - 1)
        high = side ** (n * n)
        ordered = sorted(unrank_matrix(i, n) for i in range(size))
        assert ordered == [x for x in product(range(3), repeat=n * n) if regular(x, n)]
        lex_index = {x: i for i, x in enumerate(ordered)}
        data = records(groups * size * high * suffix)
        out = BytesIO()
        calls = []
        def old(source, target, digits, prefix, gap, suffix_bytes):
            assert digits == w - 1
            assert prefix * (3**digits) ** 2 * gap * suffix_bytes == high * suffix * 4
            calls.append((digits, prefix, gap, suffix_bytes))
            cold_swap_tape(source, target, digits, prefix, gap, suffix_bytes)
        right_route(BytesIO(data), out, n, w, groups, 4 * suffix, gates, previous_swap=old)
        expected_calls = sum(1 if gate[0] == "swap" else 2 if gate[0] == "add" and gate[2] > gate[1] else 0 for gate in gates)
        assert len(calls) == (groups * size * n * expected_calls if w > 1 else 0)
        actual = memoryview(out.getvalue())
        for low_idx in range(size):
            low = ordered[low_idx]
            low_prime = tuple(y for i in range(n) for y in apply_row(gates, low[i*n:(i+1)*n], 3))
            target_low = lex_index[low_prime]
            for orig, xs in enumerate(product(range(side), repeat=n * n)):
                x = [a + 3 * b for a, b in zip(low, xs, strict=True)]
                y = [v for i in range(n) for v in apply_row(gates, x[i*n:(i+1)*n], 3**w)]
                off = 0
                for d in y:
                    off = side * off + d // 3
                for outer in range(groups):
                    src = ((outer * size + low_idx) * high + orig) * 4 * suffix
                    dst = ((outer * size + target_low) * high + off) * 4 * suffix
                    assert actual[dst:dst+4*suffix] == data[src:src+4*suffix]
        back = BytesIO()
        right_route(BytesIO(actual), back, n, w, groups, 4 * suffix, tuple(inverse_word(gates)), previous_swap=old)
        assert back.getvalue() == data
        assert len(calls) == (2 * groups * size * n * expected_calls if w > 1 else 0)
        cases += 1
        count += groups * size * high * suffix
    return cases, count


if __name__ == "__main__":
    try:
        right_route(BytesIO(), BytesIO(), 2, 2, 1, 1, ())
    except ValueError as error:
        assert "completed preceding" in str(error)
    else:
        raise AssertionError("A warm route silently received a cold swap")
    print("complete type shapes and records", *exercise_types(), flush=True)
    print("complete right shapes and records", *exercise_rows(), flush=True)
    print("PASS_STREAMING_TERNARY_ROUTES")
