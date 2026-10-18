#!/usr/bin/env python3
"""Behavioral controls for the weighted finite certificate. Apache-2.0."""
import copy
import importlib.util
import itertools
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


producer = load("producer", HERE / "verify.py")
separate = load("separate", HERE / "independent.py")


def packed(formal):
    group = producer.permutations()
    result = 0
    for permutation, coefficient in formal.items():
        for slot, bit in enumerate(coefficient):
            if bit:
                result ^= 1 << (24 * slot + group.index(permutation))
    return result


def unpacked(state):
    return {p: tuple((state >> (24 * slot + g)) & 1 for slot in range(4))
            for g, p in enumerate(producer.permutations())
            if any((state >> (24 * slot + g)) & 1 for slot in range(4))}


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="s4-tests-")
        cls.executable = producer.compile_engine(cls.temp.name)
        cls.setup = separate.setup()
        cls.small, _ = separate.weighted_ball(cls.setup[4], cls.setup[3], 4)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_complete_small_ball_and_all_transitions(self):
        actual = producer.run_engine(self.executable, "--dump-small")
        primary = {a | (b << 24) | (c << 48) | (d << 72): cost
                   for a, b, c, d, cost in actual["small_states"]}
        self.assertEqual(actual["layers"], [1, 6, 19, 134, 542])
        self.assertEqual(primary, self.small)
        _, _, labels, tables, calls = self.setup
        for state in self.small:
            for call in calls:
                g, u, v, _ = call
                projector = tuple(((u >> i) & 1) * ((v >> j) & 1)
                                  for i in range(2) for j in range(2))
                oracle = producer.formal_product(unpacked(state),
                                                producer.paid(labels.index(g), projector))
                self.assertEqual(separate.right_call(state, call, tables), packed(oracle))

    def test_brute_words_without_ball_deduplication(self):
        _, _, _, tables, calls = self.setup
        brute = {}
        for length in range(5):
            for word in itertools.product(calls, repeat=length):
                cost = sum(call[3] for call in word)
                if cost > 4:
                    continue
                state = 1 | (1 << 72)
                for call in word:
                    state = separate.right_call(state, call, tables)
                brute[state] = min(cost, brute.get(state, 100))
        self.assertEqual(brute, self.small)
        self.assertEqual(len(brute), 702)

    def test_dirty_order_and_projection_kernel(self):
        e0, e1 = (1, 0, 0, 0), (0, 0, 0, 1)
        correct = producer.replay([(0, e0), (1, e0)])
        self.assertEqual(correct, {(2, 0, 1, 3): (1, 0, 0, 0),
                                   (0, 1, 2, 3): (0, 0, 0, 1)})
        self.assertNotEqual(producer.replay([(1, e0), (0, e0)]), correct)
        self.assertNotEqual(producer.replay([(0, e0), (1, e0), (1, e1)]), correct)
        # Sum of S4 elements has zero natural and ordered-pair images over F2.
        group = producer.permutations()
        for points in [[(i,) for i in range(4)], list(itertools.permutations(range(4), 2))]:
            for point in points:
                outputs = {}
                for p in group:
                    image = tuple(p[i] for i in point)
                    outputs[image] = outputs.get(image, 0) ^ 1
                self.assertEqual(set(outputs.values()), {0})
        leak = {p: (0, 1, 0, 0) for p in group}
        for p, c in correct.items():
            old = leak.get(p, (0, 0, 0, 0))
            leak[p] = tuple(x ^ y for x, y in zip(old, c))
        self.assertNotEqual(leak, correct)
        for invalid in [(0, 1, 0, 0), (1, 0, 0, 1)]:
            with self.assertRaisesRegex(ValueError, "rank-one idempotent"):
                producer.paid(0, invalid)

    def test_scientific_receipt_corruption(self):
        _, distances = producer.direct_words()
        good = producer.read_json(HERE / "EXPECTED.json")["census"]
        producer.validate_census(good, distances)
        faults = []
        for field, value in [("radius", 8), ("states", 1)]:
            bad = copy.deepcopy(good)
            bad[field] = value
            faults.append(bad)
        bad = copy.deepcopy(good)
        bad["queries"].pop()
        faults.append(bad)
        for column in (2, 3, 4, 5):
            bad = copy.deepcopy(good)
            bad["queries"][0][column] = 0
            faults.append(bad)
        for bad in faults:
            with self.assertRaises(ValueError):
                producer.validate_census(bad, distances)

    def test_capacity_and_cli_fail_closed(self):
        for arg in ("9garbage", "0", "10"):
            run = subprocess.run([str(self.executable), arg], capture_output=True,
                                 text=True, timeout=10)
            self.assertEqual(run.returncode, 1)
            self.assertIn("radius must be 1..9", run.stderr)
        with tempfile.TemporaryDirectory(prefix="s4-capacity-") as directory:
            source = Path(directory) / "engine.cpp"
            text = (HERE / "engine.cpp").read_text()
            self.assertEqual(text.count("CAP = 2000000"), 1)
            source.write_text(text.replace("CAP = 2000000", "CAP = 10"))
            exe = producer.compile_engine(directory, source)
            run = subprocess.run([str(exe), "4"], capture_output=True, text=True, timeout=10)
            self.assertEqual(run.returncode, 1)
            self.assertIn("no exclusion certified", run.stderr)
            self.assertEqual(run.stdout, "")

    def test_hash_collisions_do_not_decide_equality(self):
        with tempfile.TemporaryDirectory(prefix="s4-hash-") as directory:
            source = Path(directory) / "engine.cpp"
            text = (HERE / "engine.cpp").read_text()
            self.assertEqual(text.count("static_cast<std::size_t>(h)"), 1)
            source.write_text(text.replace("static_cast<std::size_t>(h)",
                                           "static_cast<std::size_t>(h & 1U)"))
            exe = producer.compile_engine(directory, source)
            result = producer.run_engine(exe, "--dump-small")
            states = {a | (b << 24) | (c << 48) | (d << 72): cost
                      for a, b, c, d, cost in result["small_states"]}
            self.assertEqual(states, self.small)

    def test_optimized_git_free_read_only_replay_and_source_drift(self):
        with tempfile.TemporaryDirectory(prefix="s4-export-") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            inputs = producer.read_json(HERE / "SOURCES.json")["files"]
            for item in inputs:
                if item["usage"] == "input":
                    destination = root / item["path"]
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(producer.ROOT / item["path"], destination)
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            directories = [root] + [p for p in root.rglob("*") if p.is_dir()]
            for p in directories:
                p.chmod(0o555)
            try:
                run = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                     capture_output=True, text=True, timeout=120, cwd=root)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn("PASS_S4_TWO_PREMIUM_REGISTERS ordered_pairs=576", run.stdout)
                after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
                self.assertEqual(after, before)
            finally:
                for p in directories:
                    p.chmod(0o755)
            source = root / next(x["path"] for x in inputs if x["usage"] == "input")
            source.write_text(source.read_text() + "\nchanged source\n")
            run = subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py")],
                                 capture_output=True, text=True, timeout=120, cwd=root)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source drift:", run.stderr)


if __name__ == "__main__":
    unittest.main()
