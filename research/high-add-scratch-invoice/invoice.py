"""Independent integer invoices; no retained implementation is imported."""


def require(ok, message):
    if not ok:
        raise ValueError(message)


def counter(n, width):
    """Fully drained pooled Counter, with width encoded digits on entry."""
    require(type(n) is int and n >= 0, "nonnegative count")
    require(type(width) is int and width >= max(1, n.bit_length()), "count width")
    return 15 * n + 14 * width - 5 * n.bit_count() + 37 + 4 * (n == 0)


def suffix_probe(suffix):
    return 4 if suffix % 2 == 0 else 15 if suffix % 4 == 1 else 12


def allocations(q, before, middle, suffix):
    return (8 + 2 * before + 2 * before * q + 4 * before * middle * q
            + 2 * before * middle * q * q * (suffix > 1))


def shell(q, before, middle, suffix, *, zero_correction=True):
    """All physical I/O outside the explicitly classified arithmetic calls."""
    require(type(q) is int and q >= 3 and q % 2, "odd high modulus")
    require(all(type(n) is int and n > 0 for n in (before, middle, suffix)),
            "positive canonical extents")
    b = q.bit_length() + 1
    lengths = [n.bit_length() for n in (before, middle, suffix)]
    volume = before * middle * q * q * suffix
    # Unit coefficients permute offsets 0,...,q-1. One split is empty.
    split = counter(0, b) + counter(q, b)
    split += 2 * sum(counter(n, b) for n in range(1, q))
    if not zero_correction:
        split -= 4
    result = sum(27 * length + 63 for length in lengths) + 23 * volume + 32
    result += 2 * counter(before, lengths[0] + 1)
    result += 2 * before * counter(q, b)
    result += 2 * before * q * counter(middle, lengths[1] + 1)
    result += 2 * before * middle * (split + 2 * q * suffix_probe(suffix))
    if suffix > 1:
        result += 2 * before * middle * q * q * counter(suffix, lengths[2] + 1)
    return result


def limits(q, before, middle, suffix):
    volume = before * middle * q * q * suffix
    b = q.bit_length() + 1
    return dict(volume=volume, scratch=10 + (suffix > 1), numerical_extra=6,
                shell=640 * volume, arithmetic=832 * before * q * b * b,
                total=4096 * volume, disposed=4102 * volume)
