"""Direct packed Word RAM FFT multiplier. Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
Python integers emulate bounded signed word magnitudes; overflow is rejected.
The independent big-integer product occurs only in check(), never multiply().
"""
import json
import random
from pathlib import Path


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_seed():
    path = Path(__file__).with_name('root_seed.py')
    scope = {'__name__': 'native_root_seed', '__file__': str(path)}
    exec(compile(path.read_bytes(), str(path), 'exec'), scope)
    return scope['root_seed']


class Words:
    def __init__(self, width):
        self.width = width
        self.limit = 1 << width
        self.ops = 0
        self.peak = 0

    def v(self, x, cost=1):
        need(abs(x) < self.limit, 'word overflow')
        self.peak = max(self.peak, abs(x).bit_length())
        self.ops += cost
        return x


def multiply(a, b, n, seed=None):
    need(n >= 1, 'positive input bit budget required')
    ell = (n + 2).bit_length()
    bits = max(1, ell // 8)
    beta = 1 << bits
    length = (n + bits - 1) // bits
    need(len(a) == len(b) == length, 'packed ABI length')
    need(all(0 <= x < beta for x in a + b), 'packed digit range')
    need(a[-1] < (1 << (n - bits * (length - 1))) and
         b[-1] < (1 << (n - bits * (length - 1))), 'nonzero input padding')
    size = 1
    while size < 2 * length:
        size <<= 1
    precision = 24 * ell + 64
    scale = 1 << precision
    width = 16 * (precision + 16) + 20
    words = Words(width)
    seed_fn = seed or load_seed()
    root = seed_fn(size, precision, width)
    words.ops += root['charged_word_operations']
    words.peak = max(words.peak, root['largest_intermediate_bits'])

    def cmul(x, y):
        ac = words.v(x[0] * y[0])
        bd = words.v(x[1] * y[1])
        ad = words.v(x[0] * y[1])
        bc = words.v(x[1] * y[0])
        return (words.v(words.v(ac - bd) // scale),
                words.v(words.v(ad + bc) // scale))

    roots = [(scale, 0)]
    z = root['real'], root['imag']
    for _ in range(1, size // 2):
        roots.append(cmul(roots[-1], z))
        words.ops += 3

    def fft(data, inverse=False):
        data = list(data)
        j = 0
        for i in range(1, size):
            mask = size >> 1
            while j & mask:
                j ^= mask
                mask >>= 1
                words.ops += 4
            j ^= mask
            if i < j:
                data[i], data[j] = data[j], data[i]
            words.ops += 9
        step = 2
        while step <= size:
            half = step >> 1
            stride = size // step
            for start in range(0, size, step):
                for k in range(half):
                    tw = roots[k * stride]
                    if not inverse:
                        tw = tw[0], -tw[1]
                    u = data[start + k]
                    v = cmul(data[start + k + half], tw)
                    data[start + k] = (words.v(u[0] + v[0]), words.v(u[1] + v[1]))
                    data[start + k + half] = (words.v(u[0] - v[0]), words.v(u[1] - v[1]))
                    words.ops += 18
            step <<= 1
            words.ops += 3
        return data

    def pad(digits):
        return [(words.v(x * scale), 0) for x in digits] + [(0, 0)] * (size - length)

    aa, bb = fft(pad(a)), fft(pad(b))
    cc = fft([cmul(x, y) for x, y in zip(aa, bb)], inverse=True)
    coefficients = []
    for real, imag in cc:
        real = words.v(real // size)
        imag = words.v(imag // size)
        digit = words.v(words.v(real + scale // 2) // scale)
        need(abs(real - digit * scale) < scale // 4, 'coefficient rounding separation')
        need(abs(imag) < scale // 4, 'imaginary recovery separation')
        coefficients.append(digit)
        words.ops += 14
    need(all(x == 0 for x in coefficients[2 * length - 1:]), 'padding convolution')
    coefficients = coefficients[:2 * length - 1]
    need(all(0 <= x <= length * (beta - 1) ** 2 for x in coefficients), 'coefficient range')
    carry = 0
    result = []
    for x in coefficients + [0]:
        total = words.v(x + carry)
        result.append(words.v(total % beta))
        carry = words.v(total // beta)
        words.ops += 5
    need(carry == 0, 'final carry')
    output_length = (2 * n + bits - 1) // bits
    need(all(x == 0 for x in result[output_length:]), 'output padding')
    result = result[:output_length]
    need(result[-1] < (1 << (2 * n - bits * (output_length - 1))), 'output high padding')
    return dict(digits=result, digit_bits=bits, size=size, precision=precision,
                word_width=width, largest_intermediate_bits=words.peak,
                charged_word_operations=words.ops)


def check():
    rng = random.Random(20261022)
    count = 0
    peak = 0
    total_ops = 0
    for n in (1, 2, 3, 7, 15, 31, 63, 127, 255, 511, 1023, 2049, 65535):
        bits = max(1, (n + 2).bit_length() // 8)
        mask = (1 << bits) - 1
        length = (n + bits - 1) // bits
        pairs = [(0, 0), ((1 << n) - 1, (1 << n) - 1),
                 (rng.getrandbits(n), rng.getrandbits(n))]
        for x, y in (pairs if n < 65535 else pairs[1:2]):
            a = [(x >> (bits * i)) & mask for i in range(length)]
            b = [(y >> (bits * i)) & mask for i in range(length)]
            out = multiply(a, b, n)
            actual = sum(d << (bits * i) for i, d in enumerate(out['digits']))
            need(actual == x * y, 'independent integer multiplication reference')
            need(out['largest_intermediate_bits'] < out['word_width'], 'native word bound')
            count += 1
            peak = max(peak, out['largest_intermediate_bits'])
            total_ops += out['charged_word_operations']
    return dict(status='PASS', complete_product_cases=count,
                maximum_intermediate_bits=peak, charged_operations=total_ops,
                TM_calls=0, whole_input_MUL_calls=0, formalized=False)


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
