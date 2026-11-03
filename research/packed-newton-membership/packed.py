"""Guarded-byte Gaussian Newton membership, ranks zero through nine.

Produced by Nick Petalas. Apache-2.0.
The lattice is Clear1nsight/PR3382; bounded residues are Ali Romman/PR5374.
"""

MAX_RANK = 9
MAX_COMPONENT_BITS = 8192


def _plans():
    """Build public address masks, never coefficient-dependent tables."""
    plans = []
    for rank in range(MAX_RANK + 1):
        size = 1 << rank
        residue_mask = (1 << ((rank + 1) // 2)) - 1
        stages = []
        for bit in range(rank):
            upper = bytes(residue_mask if (i // 2) & (1 << bit) else 0
                          for i in range(2 * size))
            guard = bytes(128 if (i // 2) & (1 << bit) else 0
                          for i in range(2 * size))
            upper = int.from_bytes(upper, "little")
            guard = int.from_bytes(guard, "little")
            shift = 16 * (1 << bit)
            stages.append((upper, upper >> shift, guard, shift))
        plans.append(tuple(stages))
    return tuple(plans)


PLANS = _plans()


def _pack(values, residue_mask):
    data = bytearray(2 * len(values))
    for index, value in enumerate(values):
        if (type(value) is not tuple or len(value) != 2 or
                type(value[0]) is not int or type(value[1]) is not int):
            raise ValueError("Gaussian integer pairs required")
        if max(value[0].bit_length(), value[1].bit_length()) > MAX_COMPONENT_BITS:
            raise ValueError("component exceeds 8192-bit domain")
        data[2 * index] = value[0] & residue_mask
        data[2 * index + 1] = value[1] & residue_mask
    return int.from_bytes(data, "little")


def _transform(word, rank):
    for upper, lower, guard, shift in PLANS[rank]:
        difference = ((word & upper) | guard) - ((word & lower) << shift)
        word = (word & ~upper) | (difference & upper)
    return word.to_bytes(2 * (1 << rank), "little")


def obstruction(values):
    """Return the first failing (mask, real, imaginary, residue_bits), or None.

    Exact contract: a list of 2**rank integer pairs, 0 <= rank <= 9,
    with absolute component bit lengths <= 8192. Input is never mutated.
    """
    if (type(values) is not list or not values or
            len(values) & (len(values) - 1) or len(values) > (1 << MAX_RANK)):
        raise ValueError("binary array of length 1 through 512 required")
    rank = len(values).bit_length() - 1
    bits = (rank + 1) // 2
    word = _pack(values, (1 << bits) - 1)
    data = _transform(word, rank)
    for mask in range(len(values)):
        real, imag = data[2 * mask], data[2 * mask + 1]
        weight = mask.bit_count()
        half = weight // 2
        if ((real | imag) & ((1 << half) - 1) or
                (weight & 1 and ((real >> half) ^ (imag >> half)) & 1)):
            return mask, real, imag, bits
    return None


def member(values):
    return obstruction(values) is None
