"""Small exact Q(i) arithmetic and strict transfer-table parsing.

Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction
import hashlib
import json
import re


def need(value, message):
    if not value:
        raise ValueError(message)


class G:
    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        if isinstance(a, G):
            self.a, self.b = a.a, a.b
        else:
            self.a, self.b = Fraction(a), Fraction(b)

    def __add__(self, other):
        z = G(other)
        return G(self.a + z.a, self.b + z.b)

    __radd__ = __add__

    def __neg__(self):
        return G(-self.a, -self.b)

    def __sub__(self, other):
        return self + -G(other)

    def __mul__(self, other):
        z = G(other)
        return G(self.a*z.a - self.b*z.b, self.a*z.b + self.b*z.a)

    __rmul__ = __mul__

    def __truediv__(self, other):
        z = G(other)
        den = z.a*z.a + z.b*z.b
        need(bool(den), 'zero divisor in coefficient field')
        return G((self.a*z.a + self.b*z.b)/den,
                 (self.b*z.a - self.a*z.b)/den)

    def __bool__(self):
        return bool(self.a or self.b)

    def __eq__(self, other):
        if not isinstance(other, (G, int, Fraction)):
            return False
        z = G(other)
        return self.a == z.a and self.b == z.b

    def json(self):
        return str(self.a) if not self.b else [str(self.a), str(self.b)]


def scalar(x):
    def part(t):
        need(type(t) is int or (isinstance(t, str) and
             re.fullmatch(r'[+-]?\d+(?:/[+-]?\d+)?', t, flags=re.ASCII)),
             'explicit integer/fraction coefficient required')
        return Fraction(t)
    if isinstance(x, list):
        need(len(x) == 2, 'Gaussian pair required')
        return G(part(x[0]), part(x[1]))
    return G(part(x))


def zeros(rows, cols):
    return [[G() for _ in range(cols)] for _ in range(rows)]


def mm(a, b):
    need(bool(a) and bool(b) and len(a[0]) == len(b), 'matrix product shape')
    c = zeros(len(a), len(b[0]))
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        c[i][j] = c[i][j] + x*y
    return c


def rowmul(v, a):
    return mm([v], a)[0]


def encode(a):
    return [[G(x).json() for x in row] for row in a]


def matrix(a, rows, cols):
    need(isinstance(a, list) and len(a) == rows, 'matrix row count')
    need(all(isinstance(row, list) and len(row) == cols for row in a), 'matrix column count')
    return [[scalar(x) for x in row] for row in a]


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=True).encode()).hexdigest()


def parse(data, max_states=256):
    need(isinstance(data, dict), 'problem object required')
    need(set(data) == {'local_dimension', 'states', 'outputs', 'inputs',
                       'left', 'right', 'transitions'}, 'exact problem fields required')
    d, n, p, q = (data[k] for k in ('local_dimension', 'states', 'outputs', 'inputs'))
    need(all(type(x) is int and x > 0 for x in (d, n, p, q)), 'positive dimensions required')
    need(n <= max_states, 'state budget exceeded: no decision')
    left, right = matrix(data['left'], p, n), matrix(data['right'], n, q)
    need(isinstance(data['transitions'], dict), 'transition object required')
    trans = {}
    for symbol, a in data['transitions'].items():
        need(isinstance(symbol, str) and re.fullmatch(r'\d+,\d+', symbol, flags=re.ASCII),
             'symbol must be output,input indices')
        y, x = map(int, symbol.split(','))
        need(0 <= y < d and 0 <= x < d and symbol == f'{y},{x}', 'noncanonical symbol')
        trans[symbol] = matrix(a, n, n)
    # Every omitted local matrix entry has the zero transition. This is an
    # explicit sparse-table contract, not a promise about unexamined entries.
    return d, n, p, q, left, right, trans


def load(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            need(k not in result, 'duplicate JSON key')
            result[k] = v
        return result
    with open(path, encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=unique)
