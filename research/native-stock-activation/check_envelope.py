"""Check the public binary segment, rectangular padding and borrowed ternary fields."""

from io import BytesIO

from check_module_atoms import expected_packet, payload


def guarded(exchange, data):
    source = BytesIO(b"pre" + data + b"tail")
    source.seek(3)
    target = BytesIO(b"output" + bytes(len(data)) + b"end")
    target.seek(6)
    exchange(source, target)
    assert source.tell() == 3 + len(data) and source.read() == b"tail"
    assert target.tell() == 6 + len(data)
    result = target.getvalue()
    assert result[:6] == b"output" and result[-3:] == b"end"
    return result[6:-3]


def check():
    from source_inputs import activate

    activate()
    from module_atoms import balanced_widths, ordinary_shell, weighted_pair
    from ordinary import ordinary_swap, rectangle, root_shell
    from streaming_routes import cold_swap_tape

    for bits in range(7):
        side = 1 << bits
        dims = (2, side, 3, side)
        data = payload(6 * side**2)
        got = guarded(lambda s, t: ordinary_swap(s, t, bits, 2, 3, 4), data)
        assert got == expected_packet(data, dims, lambda p, x, g, y: (p, y, g, x))
    print("public segment widths", list(range(7)))

    for small, big in ((1, 3), (4, 9), (8, 9)):
        data = payload(6 * small**2)
        padded, recovered = BytesIO(), BytesIO()
        rectangle(BytesIO(data), padded, small, big, 2, 3, 4)
        expected = bytearray()
        for p in range(2):
            for x in range(big):
                for g in range(3):
                    for y in range(big):
                        if x < small and y < small:
                            j = ((p * small + x) * 3 + g) * small + y
                            expected.extend(data[4 * j : 4 * j + 4])
                        else:
                            expected.extend(bytes(4))
        assert padded.getvalue() == expected
        padded.seek(0)
        rectangle(padded, recovered, small, big, 2, 3, 4, restrict=True)
        assert recovered.getvalue() == data

    class OneAtomProbe:
        # The small stock tests padding. The complete growing-receiver test uses the real stock.
        n = 3
        stock = 2
        layout = balanced_widths(2)

        def body_ordinary(self, source, target, atoms, available, older, gap, suffix):
            assert (atoms, available, older, gap, suffix) == (1, 32, 1, 54, 12)

            def reverse(s, t):
                weighted_pair(
                    s,
                    t,
                    self.layout,
                    available * older,
                    gap,
                    suffix,
                    lambda p: 1,
                    cold_swap_tape,
                )

            ordinary_shell(
                source,
                target,
                self.layout,
                atoms,
                available * older,
                gap,
                suffix,
                reverse,
            )

    side = 3**5
    dims = (2, side, 2, side)
    data = payload(4 * side**2)
    got = guarded(lambda s, t: root_shell(s, t, 5, 2, 2, 4, OneAtomProbe()), data)
    assert got == expected_packet(data, dims, lambda p, x, g, y: (p, y, g, x))
    print("root e=5,w=2,k=2,r=1, Q9->16:", len(data) // 4, "distinct records")


if __name__ == "__main__":
    check()
