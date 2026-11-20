"""Test an expanded word on formal independent input arrays and all their addresses."""

from collections import Counter
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from schedule import Word, complete_order, expand


def need(value, label):
    if not value:
        raise ValueError(label)


def exchanged(items, left, right):
    out = list(items)
    out[left], out[right] = out[right], out[left]
    return tuple(out)


class Arrays:
    # A term is one independent input at a permutation of the full address.
    def __init__(self, width, ambient, lift, fault=None):
        self.n = ambient
        self.lift = lift
        self.axes = 2 * ambient * lift + 2
        self.identity = tuple(range(self.axes))
        self.fields = {i: {(i, self.identity): 1} for i in range(width)}
        self.next_field = width
        self.fault = fault
        self.leaves = 0
        self.calls = 0
        self.max_live = 0
        self.width = width

    def permute(self, owner, permutation):
        self.fields[owner] = {
            (source, tuple(permutation[i] for i in address)): value
            for (source, address), value in self.fields[owner].items()}

    def move(self, owner, order, inverse):
        if order == tuple(range(self.n)):
            return
        p = list(self.identity)
        for i, old in enumerate(order):
            for offset in range(2 * self.lift):
                a, b = 2 * self.lift * i + offset, 2 * self.lift * old + offset
                if inverse:
                    p[a] = b
                else:
                    p[b] = a
        self.permute(owner, p)

    def leaf(self, owner, axis):
        self.leaves += 1
        if self.fault == "lost_leaf" and self.leaves == 1:
            return
        p = self.identity
        for pair in range(self.lift):
            a = 2 * (axis * self.lift + pair)
            p = exchanged(p, a, a + 1)
        self.permute(owner, p)

    def add(self, dest, src, factor):
        row = Counter(self.fields[dest])
        for key, value in self.fields[src].items():
            row[key] += factor * value
        self.fields[dest] = {k: v for k, v in row.items() if v}

    def native(self, owners, f):
        # Two rank-four outputs. One paid field is an owned copy of arbitrary data.
        # The five groups of columns include a genuine spectator group.
        x, y = owners
        tmp = self.next_field
        self.next_field += 1
        self.fields[tmp] = {}
        self.add(tmp, y, 1)
        self.add(x, tmp, 1)
        self.max_live = max(self.max_live, len(self.fields) - self.width)
        self.calls += 1
        def group(slot):
            return tuple(range(slot * f, (slot + 1) * f))

        # A three-cycle makes a reversed matcher observably different from its inverse.
        order = complete_order(group(4) + group(0) + group(2) + group(3) + group(1), self.n)
        for owner in (x, tmp):
            self.move(owner, order, False)
        for owner, slots in ((x, (1, 4)), (x, (2, 3)), (tmp, (1,)),
                             (tmp, (2,)), (tmp, (3, 4))):
            yield owner, tuple(i for s in slots for i in group(s))
        for owner in (x, tmp):
            self.move(owner, order, self.fault != "wrong_matcher")
        self.add(x, tmp, -1)
        self.fields[y], self.fields[tmp] = self.fields[tmp], self.fields[y]
        if self.fault != "dirty_bank":
            del self.fields[tmp]  # The machine retires this owned, nonzero field.

    def check(self):
        expected = list(self.identity)
        for a in range(0, self.axes - 2, 2):
            expected[a], expected[a + 1] = expected[a + 1], expected[a]
        target = {i: {(i, tuple(expected)): 1} for i in range(self.width)}
        need(self.fields == target, "whole arbitrary-input endpoint or owned retirement")


def run(n, f, fault=None):
    word = Word(5, 4, 2, (2, 2, 1, 1, 2))
    width = word.root_width(n)
    m = Arrays(width, n, f, fault)
    expand(word, n, list(range(width)), m)
    m.check()
    need(m.leaves == width * word.leaves_per_array(n), "complete leaf bill")
    return m.calls, m.leaves, m.max_live


def reject(fn):
    try:
        fn()
    except ValueError:
        return
    raise ValueError("negative control survived")


def main():
    cases = [run(n, f) for n in (1, 3, 4, 5, 7, 9, 12, 15, 16, 21, 25, 33)
             for f in (1, 2, 3)]
    for fault in ("wrong_matcher", "dirty_bank", "lost_leaf"):
        reject(lambda: run(12, 2, fault))
    word = Word(5, 4, 2, (2, 2, 1, 1, 2))
    width = word.root_width(12)
    reject(lambda: expand(word, 12, [0] * width, None))
    reject(lambda: expand(word, 12, list(range(width - 1)), None))
    reject(lambda: complete_order((1, 1), 4))
    reject(lambda: Word(5, 4, 2, (4,)))
    # A free native oracle checks the empty-paid edge in the arithmetic interface.
    free = Word(8, 4, 1, ())
    need(free.leaves_per_array(16) == 0 and free.leaves_per_array(17) == 1,
         "zero paid positions and a nonempty tail")
    need(free.leaves_per_array(1 << 70) == 0, "integer tile length")
    print("PASS_FULL_ARRAY_SCHEDULE", json.dumps(dict(cases=len(cases),
          native_calls=sum(a for a, _, _ in cases), paid_leaves=sum(b for _, b, _ in cases),
          peak_owned=max(c for _, _, c in cases), negative_controls=7), sort_keys=True))


if __name__ == "__main__":
    main()
