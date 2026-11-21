"""Propagate sparse nonconstant data through every original paid position and every chart."""

import argparse
from functools import cache
from pathlib import Path
from random import Random
import sys


@cache
def residue(a, modulus):
    return a.numerator * pow(a.denominator, -1, modulus) % modulus


def column_action(vector, operations, inverse, modulus):
    # These instructions name a right matrix. Its action on a column uses the transpose indices.
    v = list(vector)
    for op, i, *args in operations if inverse else reversed(operations):
        if op == "swap":
            j = args[0]
            v[i], v[j] = v[j], v[i]
        elif op == "scale":
            a = residue(args[0], modulus)
            v[i] = v[i] * (pow(a, -1, modulus) if inverse else a) % modulus
        else:
            j, a = args
            t = residue(a, modulus)
            v[j] = (v[j] + (-t if inverse else t) * v[i]) % modulus
    return bytes(v)


@cache
def right_columns(columns, word, modulus):
    cols = list(columns)
    for op, i, *args in word:
        if op == "swap":
            j = args[0]
            cols[i], cols[j] = cols[j], cols[i]
        elif op == "scale":
            factor = residue(args[0], modulus)
            cols[i] = bytes((factor * x) % modulus for x in cols[i])
        else:
            j, a = args
            factor = residue(a, modulus)
            cols[i] = bytes(
                (x + factor * y) % modulus for x, y in zip(cols[i], cols[j], strict=True)
            )
    return tuple(cols)


class Sparse:
    dimension = 134

    def __init__(self, identity, modulus):
        self.modulus = modulus
        self.words = {identity: ()}
        self.values = {}
        self.count = 0
        self.active_paid = 0
        self.active_routes = 0
        self.moved = 0

    def zero(self):
        i = self.count
        self.count += 1
        self.values[i] = set()
        return i

    def clone(self, source):
        i = self.zero()
        self.values[i] = self.values[source].copy()
        return i

    def retire(self, owner, *, require_zero=False):
        assert not require_zero or not self.values[owner]
        del self.values[owner]

    def xor(self, dest, source):
        self.values[dest] ^= self.values[source]

    def swap(self, a, b):
        self.values[a], self.values[b] = self.values[b], self.values[a]

    def route(self, owner, word):
        if not self.values[owner]:
            return
        self.active_routes += 1
        got = set()
        for label, g, h, t in self.values[owner]:
            new = right_columns(g, word, self.modulus)
            if new not in self.words:
                self.words[new] = self.words[g] + word
            got.add((label, new, h, t))
        self.values[owner] = got

    def pay(self, job):
        from raw_binary import job_frame

        if not self.values[job.owner]:
            return
        self.active_paid += 1
        frame = job_frame(job, self.dimension)
        modulus = self.modulus
        out = set()
        for label, g, h, t in self.values[job.owner]:
            word = self.words[g] + frame.word
            delta = bytes((y - x) % modulus for x, y in zip(h, t, strict=True))
            local = column_action(delta, word, True, modulus)
            masked = bytearray(self.dimension)
            for i in frame.mask:
                masked[i] = local[i]
            v = column_action(masked, word, False, modulus)
            self.moved += any(v)
            out.add(
                (
                    label,
                    g,
                    bytes((x + z) % modulus for x, z in zip(h, v, strict=True)),
                    bytes((y - z) % modulus for y, z in zip(t, v, strict=True)),
                )
            )
        self.values[job.owner] = out


def check(predecessor, modulus):
    sys.path.insert(0, str(predecessor.resolve()))
    from raw_binary import BinarySource
    from compiler_cut import source_rule
    from periodic import Job

    n = 134
    ident = tuple(bytes(int(i == j) for i in range(n)) for j in range(n))
    ops = (("add", 7, 113, 4), ("swap", 0, 126), ("add", 0, 32, 2), ("add", 7, 0, 1))
    g = right_columns(ident, ops, modulus)
    m = Sparse(ident, modulus)
    m.words[g] = ops
    src = source_rule().word
    raw = BinarySource(m)
    rng = Random(7868)
    entries = []
    expected = {}
    seeds = {0, 111, 114, 4218, 4372}
    for i, port in enumerate(src.targets):
        owner = m.zero()
        assert owner == i
        entries.append((port.tag, Job(owner, tuple(range(port.rank)))))
        if i in seeds:
            h = bytes(rng.randrange(modulus) for _ in range(n))
            t = bytes(rng.randrange(modulus) for _ in range(n))
            m.values[i].add((i, g, h, t))
            # Independent direct multiplication of the two sparse dense matrices.
            inv = (("add", 7, 0, -1), ("add", 0, 32, -2), ("swap", 0, 126), ("add", 7, 113, -4))
            gi = right_columns(ident, inv, modulus)
            delta = [(y - x) % modulus for x, y in zip(h, t, strict=True)]
            local = [
                sum(row[k] * z for row, z in zip(gi, delta, strict=True)) % modulus
                for k in range(port.rank)
            ]
            v = [sum(g[j][k] * z for j, z in enumerate(local)) % modulus for k in range(n)]
            expected[owner] = {
                (
                    i,
                    g,
                    bytes((x + z) % modulus for x, z in zip(h, v, strict=True)),
                    bytes((y - z) % modulus for y, z in zip(t, v, strict=True)),
                )
            }
    for (tag, job), paid in zip(raw.raw(entries, 1), src.paid, strict=True):
        assert tag == paid.tag and len(job.axes) == paid.rank
        m.pay(job)
    assert len(m.values) == len(entries)
    wrong = [i for i, x in m.values.items() if x != expected.get(i, set())]
    assert not wrong, (wrong[:3], len(wrong))
    assert m.active_paid and m.active_routes and m.moved
    print(
        "modulus",
        modulus,
        "sparse root and helper inputs",
        len(seeds),
        "nonempty paid cuts",
        m.active_paid,
        "nonempty routes",
        m.active_routes,
        "moved terms",
        m.moved,
        "distinct full GL134 charts",
        len(m.words),
        flush=True,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("predecessor", type=Path)
    predecessor = p.parse_args().predecessor
    for modulus in (3, 9):
        check(predecessor, modulus)
