#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Hanson Sun, with substantial OpenAI Codex assistance.
"""Direct small-domain enumeration, source/receipt faults and inherited controls."""
from collections import Counter
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v, cross = load("verify"), load("crosscheck")


def brute(bins, roles):
    """Try every role/destination pair; rebuild capacity and collisions each time."""
    initial = [r["bin"] for r in roles]

    def free(locations):
        result = [b["capacity"] for b in bins]
        occupied = set()
        for i, b in enumerate(locations):
            result[b] -= roles[i]["width"]
            key = bins[b]["family"], roles[i]["time"]
            if key in occupied or roles[i]["time"] not in bins[b]["allowed"]:
                return None
            occupied.add(key)
        return result if min(result) >= 0 else None

    def moves(locations):
        before = free(locations)
        for i in range(len(roles)):
            for b in range(len(bins)):
                if b == locations[i]:
                    continue
                after_locations = list(locations)
                after_locations[i] = b
                after = free(after_locations)
                if after is not None:
                    yield i, b, after_locations, after, sum(x*x for x in after) - sum(x*x for x in before)

    if free(initial) is None:
        return None
    first_moves = list(moves(initial))
    if any(gain > 0 for _, _, _, _, gain in first_moves):
        return None
    prefixes, paths = [], []
    for i, b, locations, after, gain in first_moves:
        if sorted(after) != sorted(free(initial)):
            continue
        prefixes.append((i, b))
        for j, end, _, _, gain2 in moves(locations):
            if gain2 > 0:
                paths.append([i, b, j, end])
    return prefixes, sorted(paths)


class CensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.state, cls.baseline, cls.context = v.load_problem()

    def test_receipt_roundtrip_with_multidigit_rank_keys(self):
        computed = {"profile": {1: 2276, 3: 377, 7: 7, 48: 4866}}
        reloaded = json.loads(json.dumps(computed))
        self.assertEqual(v.canonical(computed), v.canonical(reloaded))
        self.assertEqual(cross.encode(computed), cross.encode(reloaded))

    def test_complete_small_domain(self):
        checked = positive = 0
        # Complete product: 3^3 capacities, three family assignments, two call
        # assignments, and all allowed-call masks containing each current role.
        for capacities in itertools.product(range(2, 5), repeat=3):
            for families in ((0, 1, 2), (0, 0, 1), (0, 1, 0)):
                for times in ((0, 1, 2), (0, 0, 1)):
                    options = [[mask for mask in range(8) if mask & (1 << t)] for t in times]
                    for masks in itertools.product(*options):
                        bins = [dict(capacity=capacities[i], family=families[i],
                                     allowed={t for t in range(3) if masks[i] & (1 << t)}) for i in range(3)]
                        roles = [dict(bin=i, width=(1, 2, 1)[i], time=times[i]) for i in range(3)]
                        oracle = brute(bins, roles)
                        if oracle is None:
                            continue
                        prefixes, paths = oracle
                        state = v.State(bins, roles)
                        fast = v.census(state)
                        other, _ = cross.enumerate_all(bins, roles)
                        self.assertEqual(fast["legal_neutral_prefixes"], len(prefixes))
                        self.assertEqual(fast["sequences"], paths)
                        self.assertEqual(v.canonical(fast), v.canonical(other))
                        self.assertEqual(state.location, [0, 1, 2])
                        checked += 1
                        positive += bool(paths)
        self.assertGreater(checked, 1000)
        self.assertGreater(positive, 0)
        print("SMALL_DOMAIN", "admissible_local_optima=" + str(checked),
              "with_two_move_gain=" + str(positive))

    def test_retained_owner_failure_controls(self):
        auditor, geo, widths, local, roles, plan = self.context
        controls = auditor.controls(geo, widths, local, roles, plan,
                                    Counter(self.baseline["idle"]), 16)
        self.assertEqual(len(controls), 11)
        self.assertEqual({x["rejected_by"] for x in controls}, {"R1", "R2", "R3", "R4", "R5", "R6", "R7", "X1"})

    def test_materialization_is_local_and_reversible(self):
        state, _, context = v.load_problem()
        roles = context[4]
        self.assertEqual(v.materialize(state, roles), roles)
        path = v.read(HERE / "RESULT.json")["census"]["profiles"][0]["witness"]
        i, dest, j, end = path
        origin = state.move(i, dest)
        second_origin = state.move(j, end)
        changed = {origin, dest, second_origin, end}
        material = v.materialize(state, roles)
        for k, source in enumerate(roles):
            if state.roles[k]["bin"] not in changed:
                self.assertEqual(material[k], source)
            self.assertEqual({x: material[k][x] for x in ("time", "stage", "replica", "helper", "width")},
                             {x: source[x] for x in ("time", "stage", "replica", "helper", "width")})
        state.move(j, second_origin)
        state.move(i, origin)
        self.assertEqual(v.materialize(state, roles), roles)

    def test_same_family_move_and_window_rejection(self):
        bins = [dict(capacity=3, family=0, allowed={0}),
                dict(capacity=3, family=0, allowed={0}),
                dict(capacity=3, family=1, allowed={1})]
        state = v.State(bins, [dict(bin=0, width=1, time=0)])
        state.move(0, 1)
        self.assertEqual(state.occupied, {(0, 0): 0})
        self.assertFalse(state.legal(0, 2))
        with self.assertRaisesRegex(ValueError, "illegal relocation"):
            state.move(0, 2)
        with self.assertRaisesRegex(ValueError, "family collision"):
            v.State(bins, [dict(bin=0, width=1, time=0), dict(bin=1, width=1, time=0)])

    def test_source_and_receipt_faults_optimized(self):
        with tempfile.TemporaryDirectory(prefix="neutral pair control ") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for item in v.read(HERE / "SOURCES.json")["files"]:
                if item["usage"] == "input":
                    dest = root / item["path"]
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / item["path"], dest)
            receipt = package / "RESULT.json"
            original = receipt.read_bytes()
            positive = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                      capture_output=True, text=True, timeout=120)
            self.assertEqual(positive.returncode, 0, positive.stderr)
            self.assertEqual(receipt.read_bytes(), original)
            bad = json.loads(original)
            bad["census"]["sequences"].pop()
            receipt.write_text(json.dumps(bad))
            for script in ("verify.py", "crosscheck.py"):
                run = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script)],
                                     capture_output=True, text=True, timeout=120)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn("receipt differs" if script == "verify.py" else "census disagrees", run.stderr)
            receipt.write_bytes(original)
            owner = root / v.PACKAGE / "OWNERS.json.gz"
            owner.write_bytes(owner.read_bytes() + b"corrupted")
            run = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                 capture_output=True, text=True, timeout=120)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source drift:", run.stderr)
            self.assertEqual(receipt.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
