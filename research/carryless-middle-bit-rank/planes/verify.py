"""Exhaust the small cases of the separated convolution digit theorem."""

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
import json
from math import comb


@dataclass(frozen=True)
class Channel:
    span: int
    left_masks: tuple[int, ...]
    right_masks: tuple[int, ...]

    @property
    def width(self):
        return min(len(self.left_masks), len(self.right_masks))


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def subset_masks(positions, size):
    return tuple(
        sum(1 << i for i in elements)
        for elements in combinations(positions, size)
    )


def positions(m, n):
    return range(m + n - 1) if m and n else range(0)


def direct_convolution(left, right, m, n):
    """An integer oracle that does not use shapes, binomials or GF(2)."""
    coefficients = [0] * len(positions(m, n))
    for i in range(m):
        for h in range(n):
            if (left >> i) & (right >> h) & 1:
                coefficients[i + h] += 1
    return coefficients


def digit_plane(coefficients, digit):
    return sum(((count >> digit) & 1) << k for k, count in enumerate(coefficients))


def translation_channels(m, n, size, *, reflect=True):
    shapes = {
        tuple(i - indices[0] for i in indices)
        for indices in combinations(range(min(m, n)), size)
    }
    channels = []
    for shape in sorted(shapes):
        span = shape[-1]
        left_shape = sum(1 << i for i in shape)
        right_shape = sum(1 << (span - i) for i in shape) if reflect else left_shape
        channels.append(Channel(
            span,
            tuple(left_shape << u for u in range(m - span)),
            tuple(right_shape << v for v in range(n - span)),
        ))
    return tuple(channels)


def encode(word, masks):
    return sum((word & mask == mask) << i for i, mask in enumerate(masks))


def carryless_product(left, right):
    result = 0
    while left:
        if left & 1:
            result ^= right
        left >>= 1
        right <<= 1
    return result


def channel_values(word, channels, *, left):
    return tuple(
        encode(word, c.left_masks if left else c.right_masks)
        for c in channels
    )


def decoded_plane(left_values, right_values, shifts):
    result = 0
    for left, right, shift in zip(left_values, right_values, shifts, strict=True):
        result ^= carryless_product(left, right) << shift
    return result


def rank_binary_rows(rows):
    """Row elimination over GF(2), storing rows as packed bits."""
    pivots = {}
    for row in rows:
        while row:
            lead = row.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = row
                break
            row ^= pivots[lead]
    return len(pivots)


def width_deficit(channels):
    """Remove one prescribed cell on a shorter side, or drop a unit channel."""
    first, *remaining = channels
    p = len(first.left_masks)
    q = len(first.right_masks)
    if min(p, q) == 1:
        return tuple(remaining)
    if p <= q:
        reduced = Channel(first.span, first.left_masks[:-1], first.right_masks)
    else:
        reduced = Channel(first.span, first.left_masks, first.right_masks[:-1])
    return (reduced, *remaining)


def antidiagonal(m, n, k):
    return tuple(i for i in range(m) if 0 <= k - i < n)


def weight_witnesses(m, n, size, k):
    indices = antidiagonal(m, n, k)
    return tuple(
        (sum(1 << i for i in subset), sum(1 << (k - i) for i in subset))
        for subset in combinations(indices, size)
    )


def eligible_masks(own_length, opposite_length, size):
    return tuple(sorted(
        sum(1 << i for i in indices)
        for indices in combinations(range(own_length), size)
        if indices[-1] - indices[0] < opposite_length
    ))


def verify_pooled_ranks(tables, num_left, num_right, left_width, right_width, case):
    left_rows = [0] * num_left
    right_rows = [0] * num_right
    for k, matrix in enumerate(tables):
        for a in range(num_left):
            left_rows[a] |= matrix[a] << (k * num_right)
        for b in range(num_right):
            transposed = sum(((row >> b) & 1) << a for a, row in enumerate(matrix))
            right_rows[b] |= transposed << (k * num_left)
    observed = rank_binary_rows(left_rows), rank_binary_rows(right_rows)
    require(observed == (left_width, right_width), ("pooled ranks", case, observed))
    return observed


def verify_width_deficit(channels, m, n, size, target_width, case):
    reduced = width_deficit(channels)
    width = sum(channel.width for channel in reduced)
    require(width == target_width - 1, ("deficit width", case, width))

    k = min(m, n) - 1
    witnesses = weight_witnesses(m, n, size, k)
    shifts = tuple(channel.span for channel in reduced)
    rows = []
    for a, _ in witnesses:
        left_values = channel_values(a, reduced, left=True)
        row = 0
        for col, (_, b) in enumerate(witnesses):
            right_values = channel_values(b, reduced, left=False)
            plane = decoded_plane(left_values, right_values, shifts)
            row |= ((plane >> k) & 1) << col
        rows.append(row)
    rank = rank_binary_rows(rows)
    require(rank <= width, ("deficit rank", case, width, rank))
    return {"width": width, "witness_rank": rank}


def verify_domain(m, n, digit, digest):
    case = (m, n, digit)
    size = 1 << digit
    channels = translation_channels(m, n, size)
    width = sum(channel.width for channel in channels)
    expected_width = comb(min(m, n), size)
    require(width == expected_width, ("shorter width", case, width, expected_width))

    left_masks = tuple(sorted(mask for c in channels for mask in c.left_masks))
    right_masks = tuple(sorted(mask for c in channels for mask in c.right_masks))
    require(left_masks == eligible_masks(m, n, size), ("left slots", case))
    require(right_masks == eligible_masks(n, m, size), ("right slots", case))

    num_left, num_right = 1 << m, 1 << n
    left_bank = tuple(channel_values(a, channels, left=True) for a in range(num_left))
    right_bank = tuple(channel_values(b, channels, left=False) for b in range(num_right))
    shifts = tuple(channel.span for channel in channels)
    indices = positions(m, n)
    tables = [[0] * num_left for _ in indices]
    packed_bytes = max(1, (len(indices) + 7) // 8)
    digest.update(bytes(case))
    for a, left_values in enumerate(left_bank):
        for b, right_values in enumerate(right_bank):
            expected = digit_plane(direct_convolution(a, b, m, n), digit)
            observed = decoded_plane(left_values, right_values, shifts)
            require(observed == expected, ("all positions", case, a, b, expected, observed))
            digest.update(expected.to_bytes(packed_bytes, "little"))
            for k in indices:
                tables[k][a] |= ((expected >> k) & 1) << b

    ranks = []
    for k, matrix in enumerate(tables):
        expected_rank = comb(len(antidiagonal(m, n, k)), size)
        observed_rank = rank_binary_rows(matrix)
        require(observed_rank == expected_rank, ("position rank", case, k, observed_rank))
        ranks.append(observed_rank)
        witnesses = weight_witnesses(m, n, size, k)
        require(len(witnesses) == expected_rank, ("witness count", case, k))
        for row, (a, _) in enumerate(witnesses):
            for col, (_, b) in enumerate(witnesses):
                require(((matrix[a] >> b) & 1) == (row == col),
                        ("identity witness", case, k, a, b))

    left_rank, right_rank = verify_pooled_ranks(
        tables, num_left, num_right, len(left_masks), len(right_masks), case,
    )
    deficit = verify_width_deficit(channels, m, n, size, width, case) if width else None
    return {
        "m": m,
        "n": n,
        "j": digit,
        "r": size,
        "channels": len(channels),
        "input_pairs": num_left * num_right,
        "positions": len(indices),
        "ranks": ranks,
        "shorter_width": width,
        "left_width": left_rank,
        "right_width": right_rank,
        "deficit": deficit,
    }


def verify_hankel_ranks():
    masks_checked = 0
    for p in range(1, 6):
        for q in range(1, 6):
            for coefficients in range(1 << (p + q - 1)):
                rows = [
                    carryless_product(1 << i, 1 << h) & coefficients != 0
                    for i in range(p)
                    for h in range(q)
                ]
                packed = [sum(rows[i * q + h] << h for h in range(q)) for i in range(p)]
                require(rank_binary_rows(packed) <= min(p, q),
                        ("Hankel rank", p, q, coefficients))
                masks_checked += 1
    return masks_checked


def sample_bits(label, channel, value, width):
    entry = f"{label}:{channel}:{value}".encode("ascii")
    return int.from_bytes(sha256(entry).digest(), "little") & ((1 << width) - 1)


def project(left_values, right_values, coefficients):
    return sum(
        (carryless_product(left, right) & mask).bit_count()
        for left, right, mask in zip(left_values, right_values, coefficients, strict=True)
    ) & 1


def xor_tuple(left, right):
    return tuple(a ^ b for a, b in zip(left, right, strict=True))


def verify_affine_centering():
    lengths = ((1, 3), (4, 2), (2, 2), (2, 5))
    total_width = sum(min(p, q) for p, q in lengths)
    left_values = [
        tuple(sample_bits("left", c, a, p) for c, (p, _) in enumerate(lengths))
        for a in range(8)
    ]
    right_values = [
        tuple(sample_bits("right", c, b, q) for c, (_, q) in enumerate(lengths))
        for b in range(16)
    ]
    require(any(left_values[0]) and any(right_values[0]), "nonzero anchor setup")
    count = 0
    for output in range(6):
        masks = tuple(
            sample_bits("decoder", c, output, p + q - 1)
            for c, (p, q) in enumerate(lengths)
        )
        affine_constant = output & 1
        rows = []
        for a in left_values:
            row = 0
            for b_index, b in enumerate(right_values):
                evaluations = (
                    project(a, b, masks) ^ affine_constant,
                    project(a, right_values[0], masks) ^ affine_constant,
                    project(left_values[0], b, masks) ^ affine_constant,
                    project(left_values[0], right_values[0], masks) ^ affine_constant,
                )
                difference = sum(evaluations) & 1
                centered = project(
                    xor_tuple(a, left_values[0]), xor_tuple(b, right_values[0]), masks,
                )
                require(difference == centered, ("affine double difference", output, a, b))
                row |= difference << b_index
                count += 1
            rows.append(row)
        require(rank_binary_rows(rows) <= total_width, ("centered rank", output, rows))

    # A single affine-output channel can have raw rank two at width one.
    # Both local encoders flip their input bit and the readout adds one.
    table = [[(1 ^ a) * (1 ^ b) ^ 1 for b in range(2)] for a in range(2)]
    raw_rank = rank_binary_rows(sum(entry << b for b, entry in enumerate(row)) for row in table)
    anchored = [
        sum((table[a][b] ^ table[a][0] ^ table[0][b] ^ table[0][0]) << b for b in range(2))
        for a in range(2)
    ]
    anchored_rank = rank_binary_rows(anchored)
    require(raw_rank == 2 and anchored == [0, 2] and anchored_rank == 1, "affine rank control")
    return {
        "evaluations": count,
        "lengths": lengths,
        "shorter_width": total_width,
        "width_one_raw_rank": raw_rank,
        "width_one_anchored_rank": anchored_rank,
    }


def verify_negative_controls():
    m, n, digit = 5, 6, 2
    a, b = 0b10111, 0b11101
    unreflected = translation_channels(m, n, 1 << digit, reflect=False)
    oracle = digit_plane(direct_convolution(a, b, m, n), digit)
    mutation = decoded_plane(
        channel_values(a, unreflected, left=True),
        channel_values(b, unreflected, left=False),
        tuple(channel.span for channel in unreflected),
    )
    require(oracle == 1 << 4 and mutation == 0, "unreflected asymmetric shape")

    channels = translation_channels(2, 3, 2)
    oracle = digit_plane(direct_convolution(3, 3, 2, 3), 1)
    mutation = decoded_plane(
        channel_values(3, channels, left=True),
        channel_values(3, channels, left=False),
        (0,),
    )
    require(oracle == 1 << 1 and mutation == 1, "omitted degree shift")

    raw0 = carryless_product(3, 3)
    raw1 = carryless_product(1, 5)
    digits0 = digit_plane(direct_convolution(3, 3, 3, 3), 1)
    digits1 = digit_plane(direct_convolution(1, 5, 3, 3), 1)
    require(raw0 == raw1 == 5 and digits0 == 2 and digits1 == 0, "bare product collision")

    dense0 = direct_convolution(3, 3, 4, 4)
    dense1 = direct_convolution(1, 9, 4, 4)
    expected0 = sum(x << k for k, x in enumerate(dense0))
    expected1 = sum(x << k for k, x in enumerate(dense1))
    require(expected0 == expected1 == 9 and dense0 != dense1, "dense output control")
    return {
        "unreflected_shape_rejected": True,
        "omitted_degree_shift_rejected": True,
        "bare_product_collision": {"pairs": [[3, 3], [1, 5]], "raw": raw0, "planes": [digits0, digits1]},
        "dense_product_collision": {"pairs": [[3, 3], [1, 9]], "integer_product": expected0,
                                    "coefficients": [dense0, dense1]},
    }


def main():
    digest = sha256()
    domains = [
        verify_domain(m, n, digit, digest)
        for m in range(8)
        for n in range(8)
        for digit in range(4)
    ]
    hankel_count = verify_hankel_ranks()
    affine = verify_affine_centering()
    controls = verify_negative_controls()
    result = {
        "status": "PASS_PRE_CARRY_DIGIT_WIDTH",
        "schema_version": 1,
        "domain": {"m": [0, 7], "n": [0, 7], "j": [0, 3], "bounds_inclusive": True},
        "source": {
            "main": "e54523517d0f03e58352e647c403a5af3e525a57",
            "comparison_pr": 7830,
            "comparison_head": "87fbf4f7b35b0f18ab12b5767775a9a424cf0b15",
        },
        "summary": {
            "domains": len(domains),
            "input_pairs_by_digit": sum(d["input_pairs"] for d in domains),
            "digit_comparisons": sum(d["input_pairs"] * d["positions"] for d in domains),
            "position_ranks": sum(d["positions"] for d in domains),
            "pooled_operand_ranks": 2 * len(domains),
            "width_deficit_controls": sum(d["deficit"] is not None for d in domains),
            "zero_width_domains": sum(d["shorter_width"] == 0 for d in domains),
            "hankel_masks": hankel_count,
        },
        "oracle_planes_sha256": digest.hexdigest(),
        "affine_centering": affine,
        "negative_controls": controls,
        "domains": domains,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
