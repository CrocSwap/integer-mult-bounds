"""Check complete physical compact macros, radix swaps and balanced CRT payloads."""

from io import BytesIO
from itertools import product

from source_inputs import activate

activate()

from compact_crt import CompactSwitch, binary_swap
from crt_tree import CRTTree


def check(benes, arithmetic):
    switches = lambda y: (((y >> 3) ^ (y >> 4)) & 1,)
    macro = CompactSwitch(2, 6, 2, 6, (0,), switches)
    source = b"".join(i.to_bytes(2, "little") for i in range(4096))
    result = BytesIO()
    macro.apply(BytesIO(source), result, 2, binary_swap)
    result = result.getvalue()
    for address in range(4096):
        y = (address >> 2) & 63
        dest = address ^ (switches(y)[0] << 2)
        assert int.from_bytes(result[2 * dest : 2 * dest + 2], "little") == address
    assert macro.stats["whole_field_swaps"] == 12
    assert 0 < macro.stats["repaired_records"] < 4096
    count = 0
    for sides in ((3, 5), (5, 3), (5, 7, 3, 11)):
        widths = tuple(s.bit_length() for s in sides)
        L = sum(widths)
        tree = CRTTree(sides, widths, 96, benes, binary_swap)
        source = b"".join(i.to_bytes(2, "little") for i in range(1 << L))
        forward, back = BytesIO(), BytesIO()
        tree.apply(BytesIO(source), forward, 2)
        forward.seek(0)
        tree.apply(forward, back, 2, reverse=True)
        assert back.getvalue() == source
        # Check a separate arithmetic CRT implementation on all padded positions.
        forward = forward.getvalue()
        for coords in product(*(range(1 << w) for w in widths)):

            def ordinal(c):
                return sum(value << sum(widths[:j]) for j, value in enumerate(c))

            dest = ordinal(arithmetic(coords, sides))
            assert int.from_bytes(forward[2 * dest : 2 * dest + 2], "little") == ordinal(coords)
            count += 1
    print("PASS_CRT_TAPES", count, "dirty CRT addresses;", dict(macro.stats))


if __name__ == "__main__":
    from source_inputs import activate

    _, base = activate()
    import importlib.util

    path = base / "research/unconditional-batched-crt/check_batched_crt.py"
    spec = importlib.util.spec_from_file_location("source_crt", path)
    src = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(src)
    check(src.benes, src.balanced)
