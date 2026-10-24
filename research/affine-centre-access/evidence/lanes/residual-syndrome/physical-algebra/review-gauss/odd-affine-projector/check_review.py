"""Check the odd leaf map directly from its signed average."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'affine-projector-stream'
PINS = {
    'ODD-WIDTH.md': '5971697aea4c7681234f96bec4dd97ee30983e45c594e91b05e9ebd5b480100f',
    'ODD-WIDTH.json': '88e33dd85d8a1be7574db88749325de17fb2ed466e9fce47870965a5799d3c66',
    'check_odd_width.py': '34d4e60c31e1dff3dc2c096cf6d92bf482733d9dc8bfab9cf73dd0b9c1112cca',
    'AMENDMENT.md': '12836faac08e0edc9a7d746eb5b1be7f62f9c72e17ed1f8a02629c5375db6479',
}
ZERO, ONE = (F(0), F(0)), (F(1), F(0))
UNITS = [ONE, (F(0), F(1)), (F(-1), F(0)), (F(0), F(-1))]
ALPHA, BETA = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def mul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def put(row, j, value):
    v = plus(row.get(j, ZERO), value)
    if v != ZERO:
        row[j] = v
    else:
        row.pop(j, None)


def kernel(values, shift, power=1):
    power %= 4
    if power == 0:
        return dict(values)
    if power == 2:
        return {a ^ shift: v for a, v in values.items()}
    diagonal, other = (ALPHA, BETA) if power == 1 else (BETA, ALPHA)
    result = {}
    for a, v in values.items():
        put(result, a, mul(diagonal, v))
        put(result, a ^ shift, mul(other, v))
    return result


def geometry(n, width, chunk, offset, protected):
    f = width // 2
    bit = lambda i, j: (n * width - 1 - i * width - j) * chunk + offset
    pairs = [(bit(i, j), bit(i, f + j)) for i in range(n) for j in range(f)]
    last = [bit(i, width - 1) for i in range(n)]
    moves = pairs + [(last[0], last[i]) for i in range(1, n)]
    removed = [b for _, b in pairs] + last[1:]
    negative = [b for _, b in pairs]
    address_bits = n * width * chunk + protected
    keep = [b for b in range(address_bits) if b not in removed]
    k, size = len(removed), 1 << address_bits
    u = keep.index(last[0])

    def coordinates(a, wrong_last_sign=False):
        for target, source in moves:
            if a & (1 << source):
                a ^= 1 << target
        leaf = sum(((a >> b) & 1) << j for j, b in enumerate(keep))
        sign = (-1) ** sum((a >> b) & 1 for b in negative)
        if wrong_last_sign:
            sign *= (-1) ** ((a >> last[1]) & 1)
        return leaf, sign

    def leaf(values, wrong=False):
        result = {}
        for a, v in values.items():
            j, sign = coordinates(a, wrong)
            put(result, j, mul((F(sign, 1 << k), F(0)), v))
        return result

    def expand(values):
        result = {}
        for a in range(size):
            j, sign = coordinates(a)
            if j in values:
                result[a] = mul((F(sign), F(0)), values[j])
        return result

    def native(values, q, power=1):
        for column in range(width):
            shift = sum(1 << bit(i, column) for i in range(n) if q & (1 << i))
            values = kernel(values, shift, power)
        return values

    def translation(values, delta):
        shift = sum(1 << bit(i, j) for i in range(n) if delta & (1 << i) for j in range(width))
        return {a ^ shift: v for a, v in values.items()}

    line_count, translation_count = 0, 0
    for a in range(size):
        base = {a: ONE}
        projected = expand(leaf(base))
        need(leaf(projected) == leaf(base), 'L J is the leaf identity')
        need(expand(leaf(projected)) == projected, 'J L is an idempotent projector')
        for q in range(1 << n):
            if q.bit_count() % 2:
                expected = {j: mul(UNITS[f % 4], v) for j, v in kernel(leaf(base), 1 << u).items()}
                need(leaf(native(base, q)) == expected, 'Direct odd-line leaf identity')
                line_count += 1
        for delta in range(1 << n):
            parity = delta.bit_count() % 2
            expected = {j ^ (parity << u): mul((F((-1) ** (f * parity)), F(0)), v)
                        for j, v in leaf(base).items()}
            need(leaf(translation(base, delta)) == expected, 'Direct translation leaf identity')
            translation_count += 1
    need(any(leaf(native({a: ONE}, 2), True) !=
             {j: mul(UNITS[f % 4], v) for j, v in kernel(leaf({a: ONE}, True), 1 << u).items()}
             for a in range(size)), 'Wrong last sign is detected')

    physical_columns = 0
    if (n, width, chunk, protected) == (2, 3, 1, 0):
        for a in range(size):
            base = {a: ONE}
            direct = native(base, 1, -1)
            direct = expand(leaf(direct))
            direct = native(native(direct, 1), 2)
            direct = translation(direct, 1)
            direct = {j: mul(UNITS[1], v) for j, v in direct.items()}
            compressed = expand(kernel(leaf(base), 1 << u, 3))
            need(direct == compressed, 'O_target Pi O_source inverse equals J C_u inverse L')
            physical_columns += 1
    return {'n': n, 'width': width, 'chunk': chunk, 'offset': offset,
            'protected_bits': protected, 'line_columns': line_count,
            'translation_columns': translation_count,
            'physical_update_columns': physical_columns, 'codimension': k}


def small_kernels():
    for sign in [-1, 1]:
        for column in range(2):
            x = [F(column == 0), F(column == 1)]
            a, d = (x[0] + sign * x[1]) / 2, (x[0] - sign * x[1]) / 2
            need([a + d, sign * (a - d)] == x, 'Signed local Haar inverse')
    maximum = F(0)
    for phase in range(4):
        for power in range(4):
            columns = []
            for j in range(4):
                value = ONE if j % 2 == 0 else UNITS[1]
                out = {a: mul(UNITS[phase], v) for a, v in kernel({j // 2: value}, 1, power).items()}
                columns.append([out.get(a, ZERO)[part] for a in range(2) for part in range(2)])
            norms = [sum(abs(columns[j][i]) for j in range(4)) for i in range(4)]
            maximum = max(maximum, max(norms))
            need(max(norms) <= 2, 'Real-component leaf kernel norm')
            need(all(v.denominator <= 2 for col in columns for v in col), 'One extra fractional bit')
    need(maximum == 2, 'The leaf norm bound is sharp')


def main():
    for name, pin in PINS.items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, 'Pin: ' + name)
    small_kernels()
    cases = [geometry(*v) for v in [(2, 1, 2, 1, 1), (2, 3, 1, 0, 0), (3, 1, 1, 0, 1)]]
    result = {'status': 'PASS_INDEPENDENT_ODD_LEAF_ACTIONS', 'producer_imported_or_executed': False,
              'source_pins': PINS, 'cases': cases, 'wrong_sign_controls': len(cases),
              'scope': 'Direct signed-average leaf map, exact native and translation phases, and small coefficient guards.'}
    (HERE / 'CHECK.json').write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
    print(result['status'])
    print(json.dumps({'line_columns': sum(v['line_columns'] for v in cases),
                      'translation_columns': sum(v['translation_columns'] for v in cases),
                      'physical_update_columns': sum(v['physical_update_columns'] for v in cases)}))


if __name__ == '__main__':
    main()
