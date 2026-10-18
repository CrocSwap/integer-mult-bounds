#!/usr/bin/env python3
"""Behavioral controls and a literal-address oracle. Apache-2.0."""

import copy
import gzip
import importlib.util
import itertools
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("oriented_sweeps", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def literal_cost(body, directions, sites, return_home=True):
    """No endpoint formula, role parser or travel code from the primary checker."""
    heads, cost = [0, 0], 0
    for event, direction in zip(body, directions):
        fields = [event["field"]] if event["op"] == "clear" else [event["src"], event["dst"]]
        for site in (range(sites) if direction == "0" else reversed(range(sites))):
            for field in fields:
                tape = 0 if field.startswith("Z") else 1
                cell = int(field[1:]) * sites + site
                cost += abs(heads[tape] - cell)
                heads[tape] = cell
    return cost + (sum(heads) if return_home else 0)


def address_frontier(body, sites):
    """Generic shortest paths keyed by physical head addresses, not endpoint bits."""
    frontier = {(0, 0): 0}
    for event in body:
        fields = [event["field"]] if event["op"] == "clear" else [event["src"], event["dst"]]
        following = {}
        for positions, paid in frontier.items():
            for sites_in_order in (range(sites), range(sites - 1, -1, -1)):
                heads, extra = list(positions), 0
                for site in sites_in_order:
                    for field in fields:
                        tape = 0 if field.startswith("Z") else 1
                        cell = int(field[1:]) * sites + site
                        extra += abs(cell - heads[tape])
                        heads[tape] = cell
                key = tuple(heads)
                following[key] = min(following.get(key, paid + extra), paid + extra)
        frontier = following
    return min(paid + sum(heads) for heads, paid in frontier.items())


class SweepTests(unittest.TestCase):
    def test_exhaustive_small_words(self):
        alphabet = [
            {"op": "clear", "field": "Z0"},
            {"op": "clear", "field": "W2"},
            {"op": "add", "src": "Z2", "dst": "W0", "coefficient": "1"},
            {"op": "add", "src": "W1", "dst": "Z0", "coefficient": "-1"},
        ]
        for length in range(1, 5):
            for word in itertools.product(alphabet, repeat=length):
                candidates = list(itertools.product("01", repeat=length))
                for sites in (1, 2, 3):
                    brute = min(literal_cost(word, ds, sites) for ds in candidates)
                    self.assertEqual(V.optimize(word, sites)[0], brute)
                _, schedule, _ = V.optimize(word, 2)
                base = literal_cost(word, schedule, 1)
                at2 = literal_cost(word, schedule, 2)
                self.assertEqual(literal_cost(word, schedule, 7), base + 6 * (at2 - base))
                self.assertEqual(V.optimize(word, 7)[0], literal_cost(word, schedule, 7))

    def test_full_word_address_oracle(self):
        word = V.load_word()
        receipt = json.loads((HERE / "RESULT.json").read_text())
        for a, b, name in V.WINDOWS:
            body, _ = V.bridge(V.extract(word, a, b, name))
            slope, constant = receipt["windows"][name]["optimal_travel"]
            for sites in (1, 2, 3, 7):
                self.assertEqual(address_frontier(body, sites), slope * sites + constant)

    def test_semantic_and_cost_faults(self):
        word = V.load_word()
        for a, b, name in V.WINDOWS:
            original = V.extract(word, a, b, name)
            body, _ = V.bridge(original)
            cost, ds, _ = V.optimize(body)
            self.assertLess(cost, literal_cost(body, "0" * len(body), 2))
            self.assertLess(literal_cost(body, ds, 2, False), cost)
            # Moving site direction only is harmless; mismatching source sites is not.
            truth = V.execute(original, "0" * len(original), 3)
            self.assertEqual(V.execute(body, "1" * len(body), 3), truth)
            self.assertNotEqual(V.execute(body, ds, 3, wrong_site=True), truth)
            if name == "F0_inverse":
                fault = copy.deepcopy(body)
                index = next(i for i, e in enumerate(fault)
                             if e.get("src") == "W8" and e.get("dst") == "Z0")
                fault[index + 2]["coefficient"] = "1"
                self.assertNotEqual(V.execute(fault, ds, 3), truth)
        invalid = [{"op": "add", "src": "W0", "dst": "W1", "coefficient": "1"}]
        with self.assertRaisesRegex(ValueError, "cross-tape"):
            V.optimize(invalid)

    def test_invalid_source_contract(self):
        word = V.load_word()
        for replacement in (
            {"op": "native", "field": "W0"},
            {"op": "clear", "field": "X0"},
            {"op": "clear", "field": "W16"},
            {"op": "add", "src": "Z0", "dst": "Z0", "coefficient": "1"},
        ):
            fault = copy.deepcopy(word)
            fault[634] = replacement
            with self.assertRaises((ValueError, KeyError)):
                V.extract(fault, 633, 1066, "L2")

    def test_artifact_integrity_and_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / "export"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))

            def run():
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                      cwd=tmp, capture_output=True, text=True, timeout=30)

            initial = {p.name: p.read_bytes() for p in package.iterdir() if p.is_file()}
            self.assertEqual(run().returncode, 0)
            self.assertEqual(initial, {p.name: p.read_bytes() for p in package.iterdir() if p.is_file()})
            archive = package / "source-word.json.gz"
            raw = gzip.decompress(archive.read_bytes())
            archive.write_bytes(gzip.compress(raw, compresslevel=1, mtime=123))
            self.assertEqual(run().returncode, 0, "equivalent recompression")
            archive.write_bytes(gzip.compress(raw.replace(b'"Z0"', b'"Z1"', 1)))
            self.assertNotEqual(run().returncode, 0, "changed source rejected")
            archive.write_bytes(initial[archive.name])
            result = package / "RESULT.json"
            receipt = json.loads(result.read_text())
            receipt["total_optimal_travel"][0] = 11741
            result.write_text(json.dumps(receipt))
            self.assertNotEqual(run().returncode, 0, "changed tariff rejected")
            result.write_bytes(initial[result.name])
            receipt = json.loads(result.read_text())
            receipt["schema_version"] = True
            result.write_text(json.dumps(receipt))
            self.assertNotEqual(run().returncode, 0, "type-sensitive receipt")
            result.unlink()
            self.assertNotEqual(run().returncode, 0, "missing receipt rejected")


if __name__ == "__main__":
    unittest.main()
