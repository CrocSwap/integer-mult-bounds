"""Two low-word circuits on the same read-only input ports and carry."""

from collections import Counter
from itertools import product
import random


class Circuit:
    def __init__(self, width):
        self.width = width
        self.inputs = 5 * width
        self.gates = []
        self.cache = {}

    def input(self, index):
        return list(range(1 + index * self.width, 1 + (index + 1) * self.width))

    def gate(self, op, u, v):
        if u == 0 or v == 0:
            return max(u, v) if op == 'xor' else 0
        if u == v:
            return 0 if op == 'xor' else u
        key = (op, min(u, v), max(u, v))
        if key not in self.cache:
            self.gates.append(key)
            self.cache[key] = self.inputs + len(self.gates)
        return self.cache[key]

    def add(self, first, second):
        carry = 0
        result = []
        for i, (u, v) in enumerate(zip(first, second, strict=True)):
            prop = self.gate('xor', u, v)
            result.append(self.gate('xor', prop, carry))
            if i + 1 < len(first):
                gen = self.gate('and', u, v)
                carry = self.gate('xor', gen, self.gate('and', prop, carry))
        return result

    def low_product(self, first, second):
        width = len(first)
        acc = [0] * width
        for i, v in enumerate(second):
            row = [self.gate('and', u, v) for u in first[:width-i]]
            acc = self.add(acc, [0] * i + row)
        return acc

    def invoice(self):
        count = Counter(op for op, _, _ in self.gates)
        return {'and': count['and'], 'xor': count['xor'],
                'clean_scratch_bits': len(self.gates),
                'clean_cnot': 4 * count['xor'] + self.width,
                'clean_toffoli': 2 * count['and']}

    def evaluate_planes(self, planes, outputs):
        values = [0, *planes]
        for op, u, v in self.gates:
            values.append((values[u] & values[v]) if op == 'and' else (values[u] ^ values[v]))
        return [values[i] for i in outputs]


def build(m, a, b, fused):
    circuit = Circuit(m)
    x, u, y, v, carry = (circuit.input(i) for i in range(5))
    if fused:
        if a+b != m:
            raise ValueError('this circuit implements the one-bit correction')
        left = circuit.add(x, u)[1:]
        right = circuit.add(y, v)[1:]
        result = [0] + circuit.low_product(left, right)
        left_parity = circuit.gate('xor', x[a], u[a])
        right_parity = circuit.gate('xor', y[b], v[b])
        toggle = circuit.gate('and', left_parity, right_parity)
        result[-1] = circuit.gate('xor', result[-1], toggle)
    else:
        result = circuit.add(circuit.low_product(x, y), circuit.low_product(u, v))
    return circuit, circuit.add(result, carry)


def test_batch(circuits, cases, m):
    planes = [0] * (5*m)
    oracle = [0] * m
    for k, words in enumerate(cases):
        x, u, y, v, c = words
        expected = x*y + u*v + c
        for i in range(m):
            oracle[i] |= ((expected >> i) & 1) << k
            for j, word in enumerate(words):
                planes[j*m+i] |= ((word >> i) & 1) << k
    for circ, out in circuits:
        if circ.evaluate_planes(planes, out) != oracle:
            raise ValueError('circuit disagrees with the integer sum')


def check():
    rows = []
    rng = random.Random(8016)
    for m in (4, 8):
        a = b = m // 2
        circuits = [build(m, a, b, flag) for flag in (False, True)]
        size = 1 << m
        if m == 4:
            sides = [(x, u) for x, u in product(range(size), repeat=2) if (x-u) % (1 << a) == 0]
            cases = ((x, u, y, v, c) for (x, u), (y, v), c in product(sides, sides, range(size)))
        else:
            def sample():
                x, y, c = (rng.randrange(size) for _ in range(3))
                return x, x ^ (rng.getrandbits(m-a) << a), y, y ^ (rng.getrandbits(m-b) << b), c
            cases = (sample() for _ in range(4096))
        from itertools import islice
        total = 0
        while batch := list(islice(cases, 128)):
            test_batch(circuits, batch, m)
            total += len(batch)
        rows.append({'m': m, 'a': a, 'b': b, 'cases': total,
                     'two_products': circuits[0][0].invoice(), 'shared_carry': circuits[1][0].invoice()})
    return rows
