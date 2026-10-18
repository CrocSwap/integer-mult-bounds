#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Positive, exhaustive small-domain and failure controls for the census."""
import copy
from collections import Counter
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("relocation_census", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = v
spec.loader.exec_module(v)


def toy_model():
    geo = dict(rank={0: 8, 1: 8, 2: 8}, place={0: (0, 0), 1: (0, 0), 2: (1, 0)},
               stage_pair={0: 1, 1: 1, 2: 0})
    windows = {(0, 0): (2, 10), (0, 1): (0, 14), (0, 2): (0, 14)}
    positions = {(0, 0): 6, (1, 0): 8, (2, 0): 9}
    roles = []
    for time, helper, child, port, width in [(0, 0, 0, 0, 3), (1, 0, 1, 0, 4),
                                            (0, 1, 0, 1, 2), (2, 0, 2, 0, 5),
                                            (2, 1, 0, 0, 1)]:
        roles.append(dict(time=time, stage=time, replica=0, helper=helper,
                          owner_replica=0, child=child, port=port, width=width, offset=0,
                          family=2 * geo["place"][child][0] * 112 + port, copy=port))
    used = Counter()
    for role in roles:
        key = v.bin_key(role)
        role["offset"] = used[key]
        used[key] += role["width"]
    return v.Model(roles, geo, windows, positions)


class CensusControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = v.build()

    def test_comparison_against_integer_radical_oracle(self):
        # At a=1/2, squaring the sums leaves S+2*sqrt(product).
        # The integer product comparison is independent of the gap predicate.
        cases = 0
        for x in range(13):
            for y in range(1, 17):
                for width in range(1, y + 1):
                    old_product, new_product = x * y, (x + width) * (y - width)
                    sign = (new_product > old_product) - (new_product < old_product)
                    self.assertEqual(v.compare(x, y, width), sign)
                    cases += 1
        self.assertEqual(cases, 1768)
        for bad in [(-1, 7, 4), (0, 3, 4), (1, 3, 0), (1.0, 7, 4), (True, 7, 4)]:
            with self.assertRaises(ValueError):
                v.compare(*bad)

    def test_grouped_census_against_every_toy_pair(self):
        model, counts, gains = toy_model(), Counter(), set()
        for index, role in enumerate(model.roles):
            source = v.bin_key(role)
            x, width = model.bins[source].remainder, role["width"]
            for destination, b in model.bins.items():
                y = b.remainder
                if destination == source or y < width:
                    continue
                before, after = x * y, (x + width) * (y - width)
                name = "strictly_improving" if after < before else (
                    "neutral" if after == before else "strictly_worsening")
                counts[name] += 1
                if after < before:
                    gains.add((index, destination))
        result = v.census(model)
        self.assertEqual(dict(counts), result["pair_classification"])
        self.assertEqual(gains, {(c["role_index"], tuple(c["destination"]))
                                 for c in result["improving_candidates"]})
        self.assertEqual(sum(counts.values()), result["capacity_feasible_distinct_bin_pairs"])
        self.assertGreater(len(gains), 0)
        self.assertGreater(counts["strictly_worsening"], 0)

    def test_strict_windows_and_family_rules(self):
        model = toy_model()
        role, destination = model.roles[0], (0, 1, 2)
        for boundary in (0, 14):
            model.positions[0, 0] = boundary
            self.assertEqual(model.rejection(role, destination), "outside_strict_source_event_window")
        model.positions[0, 0] = 6
        self.assertIsNone(model.rejection(role, destination))
        self.assertEqual(model.rejection(role, (0, 1, 1)), "same_call_family_collision")
        self.assertEqual(model.rejection(role, (0, 2, 2)), "active_data_pair")
        # Reusing the moving role's own family on another child is allowed.
        self.assertIsNone(model.rejection(role, (0, 1, 0)))

    def test_real_positive_and_all_window_obstructions(self):
        result = self.result
        c = result["census"]
        self.assertEqual(c["pair_classification"], dict(strictly_improving=19, neutral=32872,
                                                       strictly_worsening=336423971))
        self.assertEqual(c["legal_strict_improvements"], 0)
        for candidate in c["improving_candidates"]:
            lo, hi = candidate["destination_window"]
            self.assertFalse(lo < candidate["call_source_event_position"] < hi)
        positive = result["positive_control"]
        self.assertIsNone(positive["inverse"]["rejection"])
        self.assertEqual(positive["inverse"]["old_remainders"], [39, 9])
        self.assertEqual(positive["inverse"]["new_remainders"], [48, 0])
        self.assertGreater(positive["legal_improvements_detected"], 0)

    def test_missing_or_false_certificate_evidence(self):
        original = self.result
        mutants = []
        x = copy.deepcopy(original)
        x["census"]["improving_candidates"].pop()
        mutants.append(x)
        x = copy.deepcopy(original)
        x["census"]["improving_candidates"][0]["destination_window"][1] = 1000
        mutants.append(x)
        x = copy.deepcopy(original)
        x["census"]["moment_classes"][0]["moment_sign"] *= -1
        mutants.append(x)
        x = copy.deepcopy(original)
        x["positive_control"]["inverse"]["rejection"] = "outside_strict_source_event_window"
        mutants.append(x)
        for mutant in mutants:
            with self.assertRaisesRegex(ValueError, "certificate differs"):
                v.check_certificate(original, v.canonical(mutant))

    def test_source_drift_and_read_only_optimized_relocation(self):
        # Minimal offline tree: only package files and explicit live inputs.
        manifest = json.loads((HERE / "SOURCES.json").read_bytes())
        with tempfile.TemporaryDirectory(prefix="relocation census ") as temp:
            root = Path(temp)
            package = root / "research" / HERE.name
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            for item in manifest["files"]:
                if item["usage"] == "input":
                    path = root / item["path"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(v.ROOT / item["path"], path)
            command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py")]
            files = [p for p in root.rglob("*") if p.is_file()]
            for path in files:
                path.chmod(0o444)
            run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PASS_PR1094_SINGLE_RELOCATION_OBSTRUCTION", run.stdout)
            source = root / (v.SOURCE_PACKAGE + "data/OWNERS.json.gz")
            source.chmod(0o644)
            original = source.read_bytes()
            source.write_bytes(original + b"drift")
            run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("source drift:", run.stderr)
            source.write_bytes(original)
            certificate = package / "CERTIFICATE.json"
            certificate.chmod(0o644)
            receipt = json.loads(certificate.read_bytes())
            receipt["census"]["improving_candidates"].pop()
            certificate.write_bytes(v.canonical(receipt))
            run = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=60)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("certificate differs", run.stderr)
            # An explicit regeneration cannot silently overwrite prior evidence.
            certificate.write_bytes(v.canonical(self.result))
            run = subprocess.run(command + ["--write", str(certificate)], cwd=root,
                                 capture_output=True, text=True, timeout=60)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(certificate.read_bytes(), v.canonical(self.result))
            for path in files:
                path.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
