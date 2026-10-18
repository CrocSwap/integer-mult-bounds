"""Separate tensor-by-column and parity-formula oracle. Apache-2.0.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
No predecessor executable or primary arithmetic implementation is imported.
"""


def turn(z, phase):
    a, b = z
    for _ in range(phase % 4):
        a, b = -b, a
    return a, b


def column_table(record):
    table = []
    for x in range(512):
        bits = [(x // (2**j)) % 2 for j in range(9)]
        y = record["offset"]
        for row, mask in enumerate(record["matrix_rows"]):
            bit = sum(bits[j] * ((mask // (2**j)) % 2) for j in range(9)) % 2
            y ^= bit << row
        exponent = record["phase"]
        exponent += sum(bits[j] * record["linear_Z4"][j] for j in range(9))
        exponent += 2 * sum(bits[j] * bits[k] * ((record["quadratic_rows"][j] >> k) & 1)
                            for j in range(9) for k in range(j + 1, 9))
        table.append((y, exponent % 4))
    return table


def monomial(values, record, multiplicity):
    """Apply one 512-entry tensor factor at a time, at strided field bits."""
    table = column_table(record)
    result = list(values)
    for column in range(multiplicity):
        axes = [j * multiplicity + column for j in range(9)]
        deposits = [sum(((x >> j) & 1) << axis for j, axis in enumerate(axes))
                    for x in range(512)]
        mask = sum(1 << axis for axis in axes)
        out = [None] * len(result)
        for start in range(len(result)):
            if start & mask:
                continue
            for x, (y, phase) in enumerate(table):
                out[start | deposits[y]] = turn(result[start | deposits[x]], phase)
        result = out
    return result


def rounded(values, rank):
    """Closed parity formula, independently of the difference/floor lift."""
    result = list(values)
    for axis in range(rank):
        step = 1 << axis
        for block in range(0, len(result), 2 * step):
            for j in range(block, block + step):
                a, b = result[j]
                c, d = result[j + step]
                error = ((b - d) % 2) - ((a - c) % 2)
                result[j] = ((a - b + c + d + error) // 2,
                             (b + a + d - c - error) // 2)
                result[j + step] = ((a + b + c - d + error) // 2,
                                    (b - a + d + c - error) // 2)
    return result


def native(values, recipe, multiplicity):
    result = monomial(values, recipe["right"], multiplicity)
    result = rounded(result, recipe["rank"] * multiplicity)
    return monomial(result, recipe["left"], multiplicity)


def walsh(values, rank):
    result = list(values)
    for axis in range(rank):
        step = 1 << axis
        for block in range(0, len(result), step * 2):
            for j in range(block, block + step):
                a, b = result[j]
                c, d = result[j + step]
                result[j], result[j + step] = (a + c, b + d), (a - c, b - d)
    return result


def ideal_numerator(values, recipe, multiplicity):
    """H diag(i^popcount) H, denominator 2^rank; no rounded pair code."""
    rank = recipe["rank"] * multiplicity
    result = monomial(values, recipe["right"], multiplicity)
    result = walsh(result, rank)
    mask = (1 << rank) - 1
    result = [turn(value, (index & mask).bit_count()) for index, value in enumerate(result)]
    result = walsh(result, rank)
    return monomial(result, recipe["left"], multiplicity)


def collector_query(sources, query, f, beta, recipe, multiplicity):
    total = [(sum(source[j][0] for source in sources), sum(source[j][1] for source in sources))
             for j in range(len(query))]
    maximum = max(abs(v) for pair in total for v in pair)
    r, n = 7 * multiplicity, 9 * multiplicity
    log_rank = 0
    while 2**log_rank < r:
        log_rank += 1
    guard = log_rank + n // 2
    promotion = 0 if maximum == 0 else max(0, beta + 1 + guard - (maximum.bit_length() - 1))
    fine = [(a * 2**promotion, b * 2**promotion) for a, b in total]
    sent = native(fine, recipe, multiplicity)
    updated = [(a * 2**promotion + c, b * 2**promotion + d)
               for (a, b), (c, d) in zip(query, sent, strict=True)]
    return f + promotion, total, fine, sent, updated
