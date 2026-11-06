"""Exact binary paired-rank compression, @CubeJerry/AI, Apache-2.0."""


def need(ok, message):
    if not ok:
        raise ValueError(message)


def parity(x):
    return x.bit_count() & 1


def column_basis(columns):
    """Return original basis indices and coordinates of every input column."""
    pivots, selected = {}, []
    for index, original in enumerate(columns):
        value, coefficients = original, 1 << len(selected)
        while value:
            top = value.bit_length()-1
            if top not in pivots:
                pivots[top] = value, coefficients
                selected.append(index)
                break
            vector, coords = pivots[top]
            value ^= vector
            coefficients ^= coords
    coordinates = []
    for original in columns:
        value, coefficients = original, 0
        while value:
            top = value.bit_length()-1
            need(top in pivots, 'Column belongs to selected span')
            vector, coords = pivots[top]
            value ^= vector
            coefficients ^= coords
        coordinates.append(coefficients)
    return selected, coordinates


def factor_helpers(left, right):
    """U/V columns are nonnegative bit masks; return compressed columns."""
    need(len(left) == len(right), 'Matching helper column counts')
    need(all(type(v) is int and v >= 0 for v in left+right), 'Binary helper vectors')
    gram = [sum(parity(y & x) << i for i, y in enumerate(right)) for x in left]
    selected, compressed_left = column_basis(gram)
    compressed_right = [sum(((gram[j] >> i) & 1) << p for p, j in enumerate(selected))
                        for i in range(len(right))]
    return compressed_left, compressed_right, len(selected)


def compress_calls(calls, data, registers):
    """Preserve frames and data parts; endpoint validity is a separate check.

    Calls are (exponent, x_mask, y_mask). The surplus bound applies only
    when the theorem's full endpoint hypothesis has been established.
    """
    need(type(data) is int and type(registers) is int and 0 <= data <= registers,
         'Data and register dimensions')
    need(all(type(x) is int and type(y) is int and 0 <= x < 1 << registers
             and 0 <= y < 1 << registers and parity(x & y) == 1
             for _, x, y in calls), 'Binary rank-one idempotent projector')
    left, right = [x >> data for _, x, _ in calls], [y >> data for _, _, y in calls]
    new_left, new_right, width = factor_helpers(left, right)
    mask = (1 << data)-1
    result = [(a, (x & mask) | (u << data), (y & mask) | (v << data))
              for (a, x, y), u, v in zip(calls, new_left, new_right)]
    return result, width
