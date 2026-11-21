"""Replay nonconstant support through all positions of the archived binary native word."""

from argparse import ArgumentParser
from fractions import Fraction
from functools import cache
from pathlib import Path
from random import Random
import sys


def main():
    parser = ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("predecessor", type=Path)
    args = parser.parse_args()
    sys.path.extend((str(args.source.resolve()), str(args.predecessor.resolve())))
    from check_raw_delta import Sparse, right_columns
    from compiler_cut import source_rule
    from direct_body import direct_actions, direct_factors
    from factored_frames import Frame, inverse_word
    from periodic import Job
    from raw_binary import Axis, BinarySource, job_frame
    from ternary_frames import residue

    n = 134
    source = source_rule().word
    seeds = {0, 111, 114, 4218, 4372}
    ident = tuple(bytes(int(x == y) for x in range(n)) for y in range(n))
    for modulus in (3, 9):
        rng = Random(7914)
        units = [x for x in range(modulus) if x % 3]
        A = [rng.choice(units) for _ in range(n)]
        Ai = [pow(a, -1, modulus) for a in A]

        @cache
        def scaled_word(word):
            out = []
            for op, tail, i, j, coeff in direct_actions(word, 1):
                a = residue(coeff, modulus)
                if not tail and op == "swap":
                    a = A[i] * Ai[j] % modulus
                elif not tail and op == "add":
                    a = a * A[j] * Ai[i] % modulus
                out.append((op, tail, i, j, a))
            return tuple(out)

        @cache
        def factors(word, axis):
            u, v = direct_factors(Frame(n, word, (axis,)), modulus)
            return bytes(u), bytes(v)

        class DirectSparse(Sparse):
            def route(self, owner, word):
                if not self.values[owner]:
                    return
                self.active_routes += 1
                out = set()
                for label, h, t in self.values[owner]:
                    pair = list(h), list(t)
                    for op, tail, i, j, a in scaled_word(word):
                        bank = pair[tail]
                        if op == "swap":
                            bank[i], bank[j] = (
                                a * bank[j] % modulus,
                                pow(a, -1, modulus) * bank[i] % modulus,
                            )
                        elif op == "scale":
                            bank[i] = a * bank[i] % modulus
                        else:
                            bank[j] = (bank[j] + a * bank[i]) % modulus
                    out.add((label, bytes(pair[0]), bytes(pair[1])))
                self.values[owner] = out

            def pay(self, job):
                if not self.values[job.owner]:
                    return
                self.active_paid += 1
                frame = job_frame(job, n)
                out = set()
                for label, h, t in self.values[job.owner]:
                    d = [(y - ai * x) % modulus for x, ai, y in zip(h, Ai, t, strict=True)]
                    change = [0] * n
                    for axis in frame.mask:
                        u, v = factors(frame.word, axis)
                        coeff = sum(x * y for x, y in zip(v, d, strict=True)) % modulus
                        if coeff:
                            change = [
                                (x + coeff * y) % modulus for x, y in zip(change, u, strict=True)
                            ]
                    self.moved += any(change)
                    out.add(
                        (
                            label,
                            bytes(
                                (x + a * v) % modulus for x, a, v in zip(h, A, change, strict=True)
                            ),
                            bytes((y - v) % modulus for y, v in zip(t, change, strict=True)),
                        )
                    )
                self.values[job.owner] = out

        banks = DirectSparse(None, modulus)
        entries, expected = [], {}
        for i, port in enumerate(source.targets):
            owner = banks.zero()
            if i in seeds:
                g = (
                    ("add", 7, 113, Fraction(4, 5)),
                    ("swap", 0, 126),
                    ("scale", 4, Fraction(-2)),
                    ("add", 0, 32, 2),
                    ("add", 7, 0, i % 4 + 1),
                )
                axes = tuple(Axis(g, j) for j in range(port.rank))
                h, t = (bytes(rng.randrange(modulus) for _ in range(n)) for _ in range(2))
                banks.values[i].add((i, h, t))
                # Use full dense image and dual columns only in this endpoint check.
                data = right_columns(ident, g, modulus)
                inv = right_columns(ident, tuple(inverse_word(g)), modulus)
                diff = [(y - ai * x) % modulus for x, ai, y in zip(h, Ai, t, strict=True)]
                local = [
                    sum(col[j] * x for col, x in zip(inv, diff, strict=True)) % modulus
                    for j in range(port.rank)
                ]
                change = [
                    sum(data[j][k] * entry for j, entry in enumerate(local)) % modulus
                    for k in range(n)
                ]
                expected[i] = {
                    (
                        i,
                        bytes((x + a * v) % modulus for x, a, v in zip(h, A, change, strict=True)),
                        bytes((y - v) % modulus for y, v in zip(t, change, strict=True)),
                    )
                }
            else:
                axes = tuple(range(port.rank))
            entries.append((port.tag, Job(owner, axes)))
        count = 0
        for (tag, job), paid in zip(BinarySource(banks).raw(entries, 1), source.paid, strict=True):
            assert tag == paid.tag and len(job.axes) == paid.rank
            banks.pay(job)
            count += 1
        assert count == 107460 and len(banks.values) == len(entries) == 20706
        wrong = [k for k, v in banks.values.items() if v != expected.get(k, set())]
        assert not wrong, wrong[:3]
        print(
            "modulus",
            modulus,
            "raw paid",
            count,
            "outputs",
            len(entries),
            "seeds",
            len(seeds),
            "nonempty routes",
            banks.active_routes,
            "nonempty paid",
            banks.active_paid,
            "moved support",
            banks.moved,
            flush=True,
        )


if __name__ == "__main__":
    main()
