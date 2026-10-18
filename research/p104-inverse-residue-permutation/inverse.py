"""Inverse P104 residue coordinates by an involution. Apache-2.0.

Arham Tahir, with substantial OpenAI Codex assistance.
Finite implementation: ranks 0..7, at most 8192 magnitude bits per component.
The written pair/stage proof has no rank or magnitude restriction.
"""

MAX_BITS = 8192


def need(ok, message):
    if not ok:
        raise ValueError(message)


def checked(value, rank):
    need(type(rank) is int and 0 <= rank <= 7, "rank must be in 0..7")
    need(type(value) is list and len(value) == 2 << rank, "real vector shape")
    need(all(type(x) is int and x.bit_length() <= MAX_BITS for x in value),
         "integer component magnitude")
    return value


def permutation(rank):
    """Target/source involution: reverse address bits and exchange Re/Im."""
    need(type(rank) is int and 0 <= rank <= 7, "rank must be in 0..7")
    result = []
    for address in range(1 << rank):
        reverse = sum(((address >> j) & 1) << (rank - 1 - j) for j in range(rank))
        result.extend((2 * reverse + 1, 2 * reverse))
    return result


def turn(value, rank):
    checked(value, rank)
    return [value[j] for j in permutation(rank)]


def turn_inplace(value, rank, scratch):
    """Three scalar swaps per 2-cycle restore arbitrary borrowed scratch.

    Meter counts logical two-cell swaps, with two reads and two writes each.
    No physical tape or recursive-child tariff is inferred from these counts.
    """
    checked(value, rank)
    need(type(scratch) is int and scratch.bit_length() <= MAX_BITS, "scratch integer")
    cycles = 0
    for i, j in enumerate(permutation(rank)):
        if i < j:
            scratch, value[i] = value[i], scratch
            scratch, value[j] = value[j], scratch
            scratch, value[i] = value[i], scratch
            cycles += 1
    swaps = 3 * cycles
    return scratch, dict(cycles=cycles, scalar_swaps=swaps,
                        scalar_reads=2 * swaps, scalar_writes=2 * swaps)


def pair(a, b, inverse=False):
    """Separate literal pair model; components are exact signed integers."""
    d = (a[0] - b[0], a[1] - b[1])
    s = (b[0] + d[0] // 2, b[1] + d[1] // 2)
    rotated = (d[1], -d[0]) if inverse else (-d[1], d[0])
    out_b = (s[0] - rotated[0] // 2, s[1] - rotated[1] // 2)
    return (out_b[0] + rotated[0], out_b[1] + rotated[1]), out_b


def literal(value, rank, inverse=False):
    result = checked(value, rank)[:]
    for bit in reversed(range(rank)) if inverse else range(rank):
        for a in range(1 << rank):
            if not ((a >> bit) & 1):
                b = a ^ (1 << bit)
                x, y = pair(tuple(result[2*a:2*a+2]), tuple(result[2*b:2*b+2]), inverse)
                result[2*a:2*a+2], result[2*b:2*b+2] = x, y
    return result


def ideal_prefix(value, rank, inverse=False):
    """Require every pair difference even; return the exact ideal image.

    Each pair's output difference is +/-i times its input difference, so this
    is also the backward path's parity certificate. All checks survive -O.
    """
    result = checked(value, rank)[:]
    for bit in reversed(range(rank)) if inverse else range(rank):
        for a in range(1 << rank):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            ar, ai = result[2*a:2*a+2]
            br, bi = result[2*b:2*b+2]
            dr, di = ar-br, ai-bi
            need(dr % 2 == di % 2 == 0, "prefix parity")
            sr, si = (ar+br)//2, (ai+bi)//2
            rr, ri = (di, -dr) if inverse else (-di, dr)
            result[2*a:2*a+2] = sr+rr//2, si+ri//2
            result[2*b:2*b+2] = sr-rr//2, si-ri//2
    return result


def inverse_canonical(value, basis, forward_canonical):
    """Canonical inverse box T Box(H), using the unchanged forward reducer."""
    checked(value, 7)
    return turn(forward_canonical(turn(value, 7), basis), 7)


def inverse_split(value, basis, forward_split, scratch=0):
    """T split(T value), with separately metered/restored dirty scratch."""
    result = checked(value, 7)[:]
    scratch, before = turn_inplace(result, 7, scratch)
    result = forward_split(result, basis)
    scratch, after = turn_inplace(result, 7, scratch)
    return result, scratch, {key: before[key] + after[key] for key in before}
