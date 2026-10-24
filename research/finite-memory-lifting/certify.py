"""Reachable-row certificate producer for positive tensor widths.

The algorithm is classical weighted-automata equivalence, used here on
concrete physical column entries. Apache-2.0; OpenAI Codex assistance.
"""
import argparse
import json
from exact import G, encode, fingerprint, load, need, parse, rowmul


class Basis:
    def __init__(self, width):
        self.width = width
        self.rows, self.echelon, self.pivots, self.transforms = [], [], [], []

    def reduce(self, v):
        w = list(v)
        coordinates = [G() for _ in self.rows]
        for e, pivot, transform in zip(self.echelon, self.pivots, self.transforms):
            gain = w[pivot]
            if gain:
                w = [x-gain*y for x, y in zip(w, e)]
                coordinates = [x+gain*y for x, y in zip(coordinates, transform)]
        return w, coordinates

    def add(self, v):
        w, coordinates = self.reduce(v)
        pivot = next((i for i, x in enumerate(w) if x), None)
        if pivot is None:
            return False
        gain = w[pivot]
        for transform in self.transforms:
            transform.append(G())
        self.rows.append(list(v))
        self.echelon.append([x/gain for x in w])
        self.pivots.append(pivot)
        self.transforms.append([-x/gain for x in coordinates] + [G(1)/gain])
        return True

    def coordinates(self, v):
        remainder, coordinates = self.reduce(v)
        need(not any(remainder), 'closure not reached')
        return coordinates


def certify(data, max_states=256):
    _, n, p, q, left, right, transitions = parse(data, max_states)
    symbols = sorted(transitions, key=lambda t: tuple(map(int, t.split(','))))
    basis = Basis(n)
    labels = []
    first_bad = None

    def visit(v, output, word):
        nonlocal first_bad
        values = rowmul(v, right)
        for j, z in enumerate(values):
            if z and first_bad is None:
                first_bad = {'kind': 'counterexample', 'problem_sha256': fingerprint(data),
                             'word': word, 'output': output, 'input': j,
                             'value': z.json(), 'width_bound': n}
        if basis.add(v):
            labels.append((output, word))

    for symbol in symbols:
        for i in range(p):
            visit(rowmul(left[i], transitions[symbol]), i, [symbol])
    seed_rank = len(basis.rows)
    if first_bad:
        return first_bad
    cursor = 0
    while cursor < len(basis.rows):
        v = basis.rows[cursor]
        output, word = labels[cursor]
        for symbol in symbols:
            visit(rowmul(v, transitions[symbol]), output, word + [symbol])
            if first_bad:
                need(len(first_bad['word']) <= n-seed_rank+1, 'short-witness bound')
                return first_bad
        cursor += 1
    r = len(basis.rows)
    return {'kind': 'all_positive_widths', 'problem_sha256': fingerprint(data),
            'rank': r, 'positive_seed_rank': seed_rank,
            'basis': encode(basis.rows),
            'seeds': {s: encode([basis.coordinates(rowmul(v, transitions[s])) for v in left])
                      for s in symbols},
            'closure': {s: encode([basis.coordinates(rowmul(v, transitions[s]))
                                  for v in basis.rows]) for s in symbols},
            'width_bound': n}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem')
    parser.add_argument('--max-states', type=int, default=256)
    args = parser.parse_args()
    print(json.dumps(certify(load(args.problem), args.max_states), indent=2))


if __name__ == '__main__':
    main()
