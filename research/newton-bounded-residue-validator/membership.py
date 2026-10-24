"""Validate Gaussian Newton membership with bounded residues.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
The lattice and Boolean Newton criterion are Clear1nsight's PR3382.
"""


def obstruction(values):
    """Return None, or (mask, real_residue, imag_residue, modulus_bits).

    Input is a nonempty power-of-two list of Gaussian integer pairs.
    A returned mask identifies a Newton coefficient not divisible by pi^|mask|.
    """
    if type(values) is not list or not values or len(values) & (len(values) - 1):
        raise ValueError("nonempty binary array required")
    if any(type(z) is not tuple or len(z) != 2 or
           any(type(x) is not int for x in z) for z in values):
        raise ValueError("Gaussian integer pairs required")
    r = len(values).bit_length() - 1
    bits = (r + 1) // 2
    modulus_mask = (1 << bits) - 1
    real = [a & modulus_mask for a, _ in values]
    imag = [b & modulus_mask for _, b in values]
    for bit in range(r):
        step = 1 << bit
        for start in range(0, len(values), 2 * step):
            for i in range(start, start + step):
                j = i + step
                real[j] = (real[j] - real[i]) & modulus_mask
                imag[j] = (imag[j] - imag[i]) & modulus_mask
    for mask, (a, b) in enumerate(zip(real, imag)):
        weight = mask.bit_count()
        half = weight // 2
        if ((a | b) & ((1 << half) - 1) or
                (weight & 1 and ((a >> half) ^ (b >> half)) & 1)):
            return mask, a, b, bits
    return None


def member(values):
    return obstruction(values) is None
