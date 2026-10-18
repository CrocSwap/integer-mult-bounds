# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the fixed-flag coefficient-support obstruction."""

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def module(name):
    path = PACKAGE / (name + ".py")
    spec = importlib.util.spec_from_file_location("flow_test_" + name, path)
    result = importlib.util.module_from_spec(spec)
    # Execute source directly so imported test modules cannot use a stale cache.
    exec(compile(path.read_bytes(), str(path), "exec"), result.__dict__)
    return result


V, I = module("verify"), module("independent")


def run(path, *args):
    return subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(path), *args],
                          capture_output=True, text=True, timeout=30)


def export(root):
    target = root / "research" / PACKAGE.name
    shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns("__pycache__"))
    for name in V.INPUTS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(V.ROOT / name, path)
    return target


class FlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.word, cls.fixture, cls.flags = V.inputs()
        cls.receipt = V.read_json(PACKAGE / "RESULT.json")

    def test_actual_clis_and_emission(self):
        for name in ("verify", "independent"):
            result = run(PACKAGE / (name + ".py"))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_P104_FLAG_FLOW", result.stdout)
        result = run(PACKAGE / "verify.py", "--emit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), self.receipt)

    def test_positive_relays_and_all_small_edge_subsets(self):
        a, b, c, d = [V.span(row) for row in ([1], [2], [1, 2], [1, 2, 4])]
        paths = {f"{kind}{i}": [] for kind in "XY" for i in range(104)}
        paths.update(X0=[a], X1=[b], X2=[d], Y0=[c], Y1=[d], Y2=[b])
        edges = [(a, c), (b, c), (c, d), (a, d), (b, d)]
        for count in range(6):
            for subset in combinations(edges, count):
                _, outputs = V.propagate(paths, set(subset))
                adjacency = {}
                for before, after in subset:
                    adjacency.setdefault(before, set()).add(after)
                for target in range(3):
                    expected = sum(1 << s for s in range(3)
                                   if I.bfs(adjacency, paths[f"X{s}"]) & set(paths[f"Y{target}"]))
                    self.assertEqual(outputs[target], expected)
        self.assertTrue(V.propagate(paths, {(a, c), (c, d)})[1][1] & 1)
        self.assertFalse(V.propagate(paths, {(a, c)})[1][1] & 1)
        # A contained frame, or another frame of equal dimension, is not an ADD contact.
        self.assertFalse(V.propagate(paths, set())[1][0] & 1)
        self.assertFalse(V.propagate(paths, set())[1][2] & 1)
        with self.assertRaisesRegex(ValueError, "forward nested"):
            V.propagate(paths, {(d, c)})

    def test_same_flags_with_different_basis_spelling(self):
        flags = copy.deepcopy(self.flags)
        for helper in flags["helpers"]:
            helper["basis"][5] ^= helper["basis"][4]
        actual = V.compute(self.word, self.fixture, flags)
        self.assertTrue(V.typed_equal(actual, self.receipt))
        I.compare_receipt(self.word, self.fixture, flags, self.receipt)

    def test_missing_coefficient_and_closed_cut(self):
        paths = V.data_paths(self.word)
        edges = V.helper_graph(self.flags, paths)
        reach, outputs = V.propagate(paths, edges)
        self.assertFalse(outputs[0] >> 4 & 1)
        ports = V.ordered_roots(self.fixture)
        witness = V.cut_witness(4, 0, paths, edges, reach, ports)
        self.assertEqual(witness["correction_numerator_over_8"], -4)
        # Forging a source-to-target edge crosses the certified cut.
        fake_edges = edges | {(paths["X4"][0], paths["Y0"][-1])}
        with self.assertRaisesRegex(ValueError, "forward-closed"):
            V.cut_witness(4, 0, paths, fake_edges, reach, ports)
        reverse = {(v, u) for u, v in edges}
        adjacency = {}
        for u, v in reverse:
            adjacency.setdefault(u, set()).add(v)
        self.assertTrue(I.bfs(adjacency, paths["X4"]) & set(paths["Y0"]))

    def test_semantic_and_typed_receipt_faults(self):
        for key, value in (("reachable_required_pairs", 4992), ("helpers", True)):
            altered = copy.deepcopy(self.receipt)
            altered[key] = value
            self.assertFalse(V.typed_equal(altered, self.receipt))
            with self.assertRaisesRegex(ValueError, "full receipt"):
                I.compare_receipt(self.word, self.fixture, self.flags, altered)
        altered = copy.deepcopy(self.flags)
        altered["helpers"][0]["basis"][1] = altered["helpers"][0]["basis"][0]
        with self.assertRaisesRegex(ValueError, "independence"):
            V.compute(self.word, self.fixture, altered)
        with self.assertRaisesRegex(ValueError, "dependent"):
            I.compare_receipt(self.word, self.fixture, altered, self.receipt)
        for reader in (V.unique, I.no_duplicates):
            with self.assertRaisesRegex(ValueError, "duplicate"):
                json.loads('{"x":1,"x":2}', object_pairs_hook=reader)

    def test_git_free_read_only_export(self):
        with tempfile.TemporaryDirectory(prefix="p104-flow-export-") as temp:
            root = Path(temp)
            package = export(root)
            files = [p for p in root.rglob("*") if p.is_file()]
            try:
                for path in files:
                    path.chmod(0o444)
                for name in ("verify", "independent"):
                    result = run(package / (name + ".py"))
                    self.assertEqual(result.returncode, 0, result.stderr)
            finally:
                for path in files:
                    path.chmod(0o644)
            self.assertFalse((root / ".git").exists())
            self.assertFalse(list(root.rglob("*.pyc")))

    def test_cli_source_and_receipt_corruption(self):
        with tempfile.TemporaryDirectory(prefix="p104-flow-fault-") as temp:
            root = Path(temp)
            package = export(root)
            source = root / V.FLAGS
            original = source.read_bytes()
            source.write_bytes(original + b"\n")
            for name in ("verify", "independent"):
                result = run(package / (name + ".py"))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("input SHA256", result.stderr)
            source.write_bytes(original)
            receipt = json.loads((package / "RESULT.json").read_text())
            receipt["missing_source_masks_hex"][0] = "0x0"
            (package / "RESULT.json").write_text(json.dumps(receipt))
            for name in ("verify", "independent"):
                result = run(package / (name + ".py"))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("receipt equality", result.stderr)


if __name__ == "__main__":
    unittest.main()
