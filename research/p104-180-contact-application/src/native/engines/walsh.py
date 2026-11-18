"""Independent exact Gaussian columns for the ordered #7660 frames."""

from functools import cache


WIDTH = 9
SIZE = 1 << WIDTH


def times_i(real, imag, exponent):
    return ((real, imag), (-imag, real), (-real, -imag), (imag, -real))[exponent & 3]


def butterflies(values, block):
    """Unnormalized Walsh transform on the low axes of each coset."""
    stride = 1
    while stride < block:
        for start in range(0, SIZE, 2 * stride):
            for left in range(start, start + stride):
                right = left + stride
                a, b = values[left], values[right]
                values[left], values[right] = a + b, a - b
        stride *= 2


@cache
def chart(basis):
    rank = len(basis)
    if rank in (0, WIDTH):
        return 1 << rank, tuple(range(SIZE)), (0,) * SIZE

    # Enumerate the coordinate map by subset XORs, with the specified
    # ordered basis first and the first independent unit vectors after it.
    elements = [0]
    included = {0}
    for vector in (*basis, *(1 << i for i in range(WIDTH))):
        if vector in included:
            continue
        shifted = [x ^ vector for x in elements]
        included.update(shifted)
        elements.extend(shifted)
    if len(elements) != SIZE:
        raise ValueError("ordered frame completion does not fill the address space")

    inverse = {address: coordinates for coordinates, address in enumerate(elements)}
    inverse_columns = [inverse[1 << i] for i in range(WIDTH)]
    quadratic = []
    for address in range(SIZE):
        active = [inverse_columns[i] for i in range(WIDTH) if address >> i & 1]
        phase = sum(1 - (column.bit_count() & 1) for column in active)
        phase += 2 * sum((a & b).bit_count() & 1 for i, a in enumerate(active) for b in active[i + 1:])
        quadratic.append(phase & 3)
    return 1 << rank, tuple(elements), tuple(quadratic)


def apply_chart(basis, input_real, input_imag, sign):
    block, elements, quadratic = chart(basis)
    if block == 1:
        return input_real, input_imag, 0

    real, imag = zip(*(times_i(input_real[p], input_imag[p], -quadratic[p]) for p in elements))
    real, imag = list(real), list(imag)
    butterflies(real, block)
    butterflies(imag, block)
    for i in range(SIZE):
        exponent = sign * (i & (block - 1)).bit_count()
        real[i], imag[i] = times_i(real[i], imag[i], exponent)
    butterflies(real, block)
    butterflies(imag, block)

    output_real, output_imag = [0] * SIZE, [0] * SIZE
    for i, p in enumerate(elements):
        output_real[p], output_imag[p] = times_i(real[i], imag[i], quadratic[p])
    return output_real, output_imag, block.bit_length() - 1


def transition(before, after, unit_address):
    real, imag = [0] * SIZE, [0] * SIZE
    real[unit_address] = 1
    real, imag, before_den = apply_chart(before, real, imag, -1)
    real, imag, after_den = apply_chart(after, real, imag, 1)
    return {i: (a, b) for i, (a, b) in enumerate(zip(real, imag)) if a or b}, before_den + after_den


def equal_gaussian_columns(left, right):
    left_values, left_den = left
    right_values, right_den = right
    if left_values.keys() != right_values.keys():
        return False
    den = max(left_den, right_den)
    return all(
        a << (den - left_den) == c << (den - right_den)
        and b << (den - left_den) == d << (den - right_den)
        for i, (a, b) in left_values.items()
        for c, d in (right_values[i],)
    )
