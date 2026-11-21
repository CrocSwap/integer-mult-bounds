"""Check the uniform depth inequalities and reconstruct actual nonzero radix-sort tags."""

from fractions import Fraction
from io import BytesIO

from staged_carriers import COMPLEX_LOG, RANK_LOGS, strong_precision_log


def uniform_bounds(s):
    floor_s = strong_precision_log() + 1
    if s < floor_s:
        raise ValueError("The public precision is below the connected guarantee")
    q = 1 << 18
    counts = tuple((s + h - 1) // h for h in (COMPLEX_LOG,) + RANK_LOGS)
    levels = 34 + counts[0] + sum(3 + count for count in counts[1:])
    assert COMPLEX_LOG == min((COMPLEX_LOG,) + RANK_LOGS)
    assert levels * COMPLEX_LOG <= 60 * COMPLEX_LOG + 7 * s
    assert 512 * 14 * q < COMPLEX_LOG
    assert 512 * (124 * q + 48) < floor_s
    assert (1 << 32) > 64 * 33 + 129
    assert 64 * (s + 128).bit_length() <= s
    overhead = (2 * levels + 4) * q + 48 + 2 * (s + 128).bit_length()
    assert 8 * overhead < s and s // 2 - 2 - overhead > 1024
    # A polynomial of degree at most nine with factors at least 32 grows by less than two.
    assert 33**9 < 2 * 32**9
    private_base = 12 * (128 * (floor_s + 130) * (floor_s + 1) ** 8 + 64)
    crt_base = 1200 * (64 * (128 * floor_s**2 + floor_s) + 2 * floor_s + 128)
    assert max(private_base, crt_base).bit_length() <= floor_s - 2
    return {
        "s": s,
        "height": levels,
        "amplification_log": overhead,
        "stripe_margin": s // 2 - 2 - overhead,
    }


def check_sort(quotient):
    n = 2
    words = (
        (("add", 0, 1, Fraction(1)), ("swap", 0, 1)),
        (("scale", 0, Fraction(2)), ("add", 1, 0, Fraction(-2))),
    )
    width, slots = n * n, quotient.low_count(n)
    visits = comparisons = 0
    for word in words:
        matrix = quotient.right_matrix(n, word, 3)

        def low_tags():
            for low in quotient.low_rows(n):
                result, _ = quotient.canonical_right(low, matrix, 3)
                yield bytes(x for row in result for x in row)

        def reconstruct(digit, position):
            nonlocal comparisons
            for i, tag in enumerate(low_tags()):
                key = tag[digit + 1 :], i
                before = 0
                for j, other in enumerate(low_tags()):
                    before += (other[digit + 1 :], j) < key
                    comparisons += 1
                if before == position:
                    return tag
            raise AssertionError("The stable order has no such slot")

        seen = []

        class ObservedTags(BytesIO):
            def read(self, size):
                item = super().read(size)
                if size == width:
                    assert len(item) == width
                    seen.append(item)
                return item

        tags = tuple(low_tags())
        assert len(set(tags)) == len(tags) == slots and any(any(tag) for tag in tags)
        target = BytesIO()
        quotient.sort_packets(
            BytesIO(bytes(range(slots))),
            ObservedTags(b"".join(tags)),
            target,
            slots,
            1,
            width,
            [BytesIO(), ObservedTags()] + [BytesIO() for _ in range(6)],
        )
        assert len(seen) == slots * width
        for ordinal, actual in enumerate(seen):
            j, k = divmod(ordinal, slots)
            assert actual == reconstruct(width - 1 - j, k)
            visits += 1
        assert target.getvalue() == bytes(sorted(range(slots), key=tags.__getitem__))
    return {
        "nontrivial_words": len(words),
        "actual_tag_reads": visits,
        "rank_comparisons": comparisons,
    }


def check_successive_groups(quotient):
    words = (
        (("add", 0, 1, Fraction(1, 2)), ("swap", 0, 2), ("scale", 1, Fraction(2))),
        (("swap", 1, 2), ("add", 2, 0, Fraction(-5))),
        (("add", 1, 2, Fraction(2)), ("scale", 0, Fraction(-2))),
    )
    lows = list(quotient.low_rows(3))
    assert len(lows) == 416 and lows == sorted(lows)
    reads = []

    class TagTape(BytesIO):
        def read(self, size):
            value = super().read(size)
            if size == 9:
                reads.append(value)
            return value

    source, tags, target = BytesIO(), TagTape(), BytesIO()
    scratch = [BytesIO(), TagTape()] + [BytesIO() for _ in range(6)]
    ties = visits = 0
    for group, word in enumerate(words):
        matrix = quotient.right_matrix(3, word, 3)
        keys = []
        records = []
        for i, low in enumerate(lows):
            image, _ = quotient.canonical_right(low, matrix, 3)
            keys.append(bytes(x for row in image for x in row))
            records.append((group * 1234567 + i * 50003).to_bytes(4, "little"))
        source.write(b"".join(records))
        tags.write(b"".join(keys))
        offset = target.tell()
        quotient.sort_packets(source, tags, target, len(lows), 4, 9, scratch)
        expected = []
        for digit in reversed(range(9)):
            order = sorted(range(len(lows)), key=lambda i: (keys[i][digit + 1 :], i))
            expected.extend(keys[i] for i in order)
            if 0 < digit < 8:
                ties += len(lows) - len({key[digit + 1 :] for key in keys})
        assert reads == expected
        visits += len(reads)
        reads.clear()
        order = sorted(range(len(lows)), key=keys.__getitem__)
        assert target.getvalue()[offset:] == b"".join(records[i] for i in order)
        assert all(tape.getvalue() == b"" and tape.tell() == 0 for tape in [source, tags, *scratch])
    return {"successive_groups": len(words), "tag_reads": visits, "suffix_ties": ties}


if __name__ == "__main__":
    from retained import install

    install()
    import quotient_route

    first = strong_precision_log() + 1
    for s in (first, 2 * first, 1 << 100, 1 << 256):
        print(uniform_bounds(s))
    print(check_sort(quotient_route))
    print(check_successive_groups(quotient_route))
