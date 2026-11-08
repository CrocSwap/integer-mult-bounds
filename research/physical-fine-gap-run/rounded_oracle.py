"""External integer oracle for the *rounded* schedule, without physical code.

Prepared for @CubeJerry with OpenAI Codex assistance. Apache-2.0.
This tests tape execution, not the source inverse theorem. The separate
original_matrix_oracle.py checks the original rational Reference instead.
"""


def truncate(value, bits):
    return (-1 if value < 0 else 1) * (abs(value) >> bits)


def action(words, pages, reverse_f=False):
    p, streams = pages.plan, pages.streams

    def diagonal(values, coefficients):
        if len(values) != len(coefficients):
            raise ValueError("oracle diagonal shape")
        return [truncate(x * y, p.f) for x, y in zip(values, coefficients)]

    def residual(values, page):
        offset, result = 0, []
        for start, block, begin, size in p.blocks():
            gauges_in = page[offset:offset + size]; offset += size
            kernel = page[offset:offset + size]; offset += size
            gauges_out = page[offset:offset + block]; offset += block
            data = diagonal(values[begin:start + block], gauges_in)
            convolution = [truncate(sum(data[j] * kernel[i-j] for j in range(i+1)), p.f)
                           for i in range(size)]
            result.extend(diagonal(convolution[start-begin:], gauges_out))
        if offset != len(page) or len(result) != p.n:
            raise ValueError("oracle residual extent")
        return result

    def recurrence(values, coefficients):
        previous, result = 0, []
        for value, mu in zip(values, coefficients):
            previous = truncate((value << p.f) - mu * previous, p.f)
            result.append(previous)
        return result

    values = diagonal(words, streams["Finv"])
    values = residual(values, streams["residual_minus"])
    values = recurrence(values, streams["mu_minus"])
    factors = streams["F"][::-1] if reverse_f else streams["F"]
    values = diagonal(values, factors)
    values.reverse()
    values = residual(values, streams["residual_plus"])
    values = recurrence(values, streams["mu_plus"])
    values.reverse()
    return tuple(diagonal(values, streams["Finv"]))
