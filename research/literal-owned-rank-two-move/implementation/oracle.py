"""Original-frame forward Gaussian kernel, independent of emitted factor order."""
from functools import cache
import rank2 as C


def gamma(n):
    if type(n) is not int or n <= 0:
        raise ValueError('positive Gamma field')
    b = bin(n)[2:]
    return '0' * (len(b) - 1) + b


def header(shape):
    return ''.join(gamma(n) for n in shape)


def encode(values, width):
    result = []
    for pair in values:
        for value in pair:
            if not -(1 << (width - 1)) <= value < (1 << (width - 1)):
                raise ValueError('signed oracle overflow')
            result.append(format(value % (1 << width), '0' + str(width) + 'b'))
    return ''.join(result)


def reverse9(x):
    return int(format(x, '09b')[::-1], 2)


@cache
def columns():
    engine = C.load('rank2_forward_source_engine', 'source/native_verify.py')
    # The source order is T470 T601*, derived from exact frame lists.
    circuit = engine.adjoint(engine.frame((137,), 9)) + engine.frame((75, 137, 265), 9)
    result = []
    for source in range(512):
        value, denominator = engine.state(circuit, reverse9(source))
        result.append((tuple((reverse9(target), a, b) for target, (a, b) in value.items()),
                       1 << denominator))
    return tuple(result)


def image_f1(values, shape):
    f, r, p, s, width, _ = shape
    if f != 1 or len(values) != p * 512 * s * r:
        raise ValueError('full actual nine-slot f=1 oracle domain')
    result = [(0, 0) for _ in values]
    # Rank-two entries have Gaussian component denominator two. Keep the
    # source engine's normalized denominator, rather than assume it silently.
    if any(denominator != 2 for _, denominator in columns()):
        raise ValueError('unexpected exact source denominator')
    tail = s * r
    for source, (entries, _) in enumerate(columns()):
        for target, a, b in entries:
            for outer in range(p):
                for suffix in range(tail):
                    x, y = values[(outer * 512 + source) * tail + suffix]
                    index = (outer * 512 + target) * tail + suffix
                    u, v = result[index]
                    result[index] = (u + a * x - b * y, v + b * x + a * y)
    if any(a % 2 or b % 2 for a, b in result):
        raise ValueError('nonintegral complete source image')
    return [(a // 2, b // 2) for a, b in result]


def expected_f1(values, shape):
    return encode(image_f1(values, shape), shape[4])
