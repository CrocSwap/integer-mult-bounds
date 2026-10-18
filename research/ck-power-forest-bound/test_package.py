#!/usr/bin/env python3
"""Source admission and weighted-forest identity controls. Apache-2.0."""
import copy
from fractions import Fraction as Q
import gzip
import itertools
import json
from pathlib import Path
import runpy
import shutil
import tempfile
import unittest

C = runpy.run_path(str(Path(__file__).resolve().with_name("common.py")))


def weighted_program(rows, parents):
    depth = {}
    def visit(t, visiting):
        if t in depth:
            return depth[t]
        if t in visiting:
            raise ValueError("cycle")
        depth[t] = 0 if t not in parents else 1 + visit(parents[t][0], visiting | {t})
        return depth[t]
    for t in range(3):
        visit(t, set())
    order = sorted(range(3), key=lambda t: (-depth[t], t))
    preparation = [(t, parents[t][0], -parents[t][1]) for t in order if t in parents]
    middle = []
    for t in range(3):
        residual = rows[t] if t not in parents else [a - parents[t][1] * b for a, b in zip(rows[t], rows[parents[t][0]])]
        middle.extend((t, 3 + j, q) for j, q in enumerate(residual) if q)
    return preparation + middle + [(t, s, -q) for t, s, q in preparation[::-1]]


def operator(program, dual=False):
    rows = [[Q(int(i == j)) for j in range(5)] for i in range(5)]
    for t, s, q in program:
        if dual:
            t, s, q = s, t, -q
        rows[t] = [a + q * b for a, b in zip(rows[t], rows[s])]
    return rows


class PackageTests(unittest.TestCase):
    def test_all_three_target_weighted_forests(self):
        rows = [[Q(1, 2), Q(3, 4)], [Q(1, 4), Q(-1)], [Q(3, 4), Q(1, 2)]]
        original = [(t, 3 + j, q) for t, row in enumerate(rows) for j, q in enumerate(row)]
        total, cycles = 0, 0
        choices = [[None, *[p for p in range(3) if p != t]] for t in range(3)]
        for topology in itertools.product(*choices):
            targets = [i for i, p in enumerate(topology) if p is not None]
            try:
                weighted_program(rows, {t: (topology[t], Q(1)) for t in targets})
            except ValueError:
                cycles += 1
                continue
            for weights in itertools.product([Q(-2), Q(-1, 2), Q(1, 2), Q(2)], repeat=len(targets)):
                parents = {t: (topology[t], q) for t, q in zip(targets, weights)}
                program = weighted_program(rows, parents)
                for dual in (False, True):
                    self.assertEqual(operator(program, dual), operator(original, dual))
                total += 1
        self.assertEqual((total, cycles), (169, 11))

    def test_missing_preparation_corrupts_arbitrary_targets(self):
        rows = [[Q(1, 2), Q(0)], [Q(1, 4), Q(0)], [Q(0), Q(0)]]
        original = [(t, 3 + j, q) for t, row in enumerate(rows) for j, q in enumerate(row) if q]
        program = weighted_program(rows, {0: (1, Q(2)), 1: (2, Q(-1, 2))})
        bad = operator(program[2:])
        good = operator(original)
        self.assertEqual([r[3:] for r in bad], [r[3:] for r in good])
        self.assertNotEqual(bad, good)

    def test_source_recompression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            m = C["load"](C["HERE"] / "SOURCES.json")
            for name, pin in m["files"].items():
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                data = (C["ROOT"] / name).read_bytes()
                if pin["encoding"] == "gzip-payload":
                    data = gzip.compress(gzip.decompress(data), compresslevel=1, mtime=12345)
                target.write_bytes(data)
            C["inputs"](root)

    def test_source_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            m = C["load"](C["HERE"] / "SOURCES.json")
            for name in m["files"]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(C["ROOT"] / name, target)
            word = C["load"](root / C["WORD"])
            word["compensation"][0][3] *= -1
            (root / C["WORD"]).write_bytes(gzip.compress(C["canonical"](word)))
            with self.assertRaisesRegex(ValueError, "source pin"):
                C["inputs"](root)

    def test_duplicate_json_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"floor":16364,"floor":16363}')
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                C["load"](path)

    def test_typed_receipt(self):
        with self.assertRaisesRegex(ValueError, "changed"):
            C["same"]({"count": 1}, {"count": True}, "changed")

    def test_output_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text("keep original")
            with self.assertRaises(FileExistsError):
                C["write"](path, {"floor": 16364})
            self.assertEqual(path.read_text(), "keep original")


if __name__ == "__main__":
    unittest.main()
