#!/usr/bin/env python3
"""Exact interval oracles, source corruption and invoice controls (stdlib only).

Ross Richardson, substantial OpenAI Codex assistance, Apache-2.0.
"""
import base64
from copy import deepcopy
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("checker", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def exact_log_interval(n, d, terms=120):
    """Fraction oracle; no rounding of powers or summands."""
    # Reduce by powers of four, then use a direct atanh series with y <= 3/5.
    k = 0
    while n > 4 * d:
        d *= 4
        k += 1

    def part(a, b):
        y = Q(a - b, a + b)
        total = sum((2 * y ** (2 * j + 1) / (2 * j + 1) for j in range(terms)), Q(0))
        tail = 2 * y ** (2 * terms + 1) / ((2 * terms + 1) * (1 - y * y))
        return total, total + tail
    lo, hi = part(n, d)
    l4, h4 = part(4, 1)
    return lo + k * l4, hi + k * h4


def exact_exp_interval(x, terms=48):
    term = Q(1)
    total = term
    for k in range(1, terms + 1):
        term = term * x / k
        total += term
    tail = term * x / (terms + 1) / (1 - x / (terms + 2))
    return total, total + tail


class Reconciliation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(gzip.decompress((HERE / "sources.json.gz").read_bytes()))
        cls.expected = json.loads((HERE / "EXPECTED.json").read_text())

    def capsule(self):
        return v.GitCapsule(deepcopy(self.data))

    def test_complete_offline_receipt(self):
        self.assertEqual(v.run(self.capsule()), self.expected)

    def test_every_pinned_object_rejects_one_byte_corruption(self):
        for oid in self.data["objects"]:
            data = deepcopy(self.data)
            record = data["objects"][oid]
            raw = bytearray(base64.b64decode(record["data"]))
            raw[-1] ^= 1
            record["data"] = base64.b64encode(raw).decode()
            with self.subTest(oid=oid), self.assertRaisesRegex(ValueError, "Git object digest"):
                v.GitCapsule(data)

    def test_every_pinned_object_is_required(self):
        for oid in self.data["objects"]:
            data = deepcopy(self.data)
            del data["objects"][oid]
            with self.subTest(oid=oid), self.assertRaisesRegex(ValueError, "missing Git object"):
                v.run(v.GitCapsule(data))

    def test_rehashed_supplier_cannot_be_rebound_to_old_commit(self):
        data = deepcopy(self.data)
        capsule = self.capsule()
        _, oid = capsule.resolve(v.NEW, v.PACKAGE + "/references/pr194-certificate.json")
        record = data["objects"].pop(oid)
        raw = base64.b64decode(record["data"]) + b" "
        replacement = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        record["data"] = base64.b64encode(raw).decode()
        data["objects"][replacement] = record
        with self.assertRaisesRegex(ValueError, "missing Git object"):
            v.run(v.GitCapsule(data))

    def test_extra_valid_object_is_rejected(self):
        data = deepcopy(self.data)
        raw = b"unrelated"
        oid = hashlib.sha1(b"blob 9\0" + raw).hexdigest()
        data["objects"][oid] = {"type": "blob", "data": base64.b64encode(raw).decode()}
        with self.assertRaisesRegex(ValueError, "unconsumed capsule objects"):
            v.run(v.GitCapsule(data))

    def test_every_log_ratio_against_fraction_oracle(self):
        cap = self.capsule()
        ratios = set()
        for name in v.NAMES:
            c = cap.json(v.NEW, v.PACKAGE + "/certificates/network-children-" + name + ".json")
            ratios.update((c["m"], r) for r in v.histogram(c))
        for n, d in sorted(ratios | {(1, 1), (2, 1), (4, 1), (8, 1), (110, 1)}):
            low, high = v.log_interval(n, d)
            ol, oh = exact_log_interval(n, d, terms=170)
            with self.subTest(ratio=(n, d)):
                self.assertLessEqual(Q(low, v.SCALE), ol)
                self.assertGreaterEqual(Q(high, v.SCALE), oh)

    def test_exp_interval_against_fraction_oracle(self):
        rng = random.Random(97)
        values = [0, 1, v.SCALE // 16]
        values += [rng.randrange(v.SCALE // 16) for _ in range(24)]
        for x in values:
            low, high = v.exp_interval(x, x)
            ol, oh = exact_exp_interval(Q(x, v.SCALE))
            with self.subTest(x=x):
                self.assertLessEqual(Q(low, v.SCALE), ol)
                self.assertGreaterEqual(Q(high, v.SCALE), oh)

    def test_exact_zero_exponent_has_rank_moment(self):
        for m in (66, 72, 110):
            hist = {1: 3, m - 1: 7}
            low, high = v.moment_interval(m, hist, Q(0))
            exact = Q(3 + 7 * (m - 1), m)
            self.assertLessEqual(Q(low, v.SCALE), exact)
            self.assertGreaterEqual(Q(high, v.SCALE), exact)

    def test_invalid_domains_are_rejected(self):
        calls = [lambda: v.log_interval(0, 1), lambda: v.log_interval(1, 0),
                 lambda: v.log_interval(1, 2), lambda: v.exp_interval(-1, 0),
                 lambda: v.exp_interval(0, v.SCALE // 16 + 1),
                 lambda: v.exp_interval(2, 1), lambda: v.moment_interval(66, {}, Q(0)),
                 lambda: v.moment_interval(66, {66: 1}, Q(0)),
                 lambda: v.moment_interval(66, {2: -1}, Q(0)),
                 lambda: v.moment_interval(66, {2: True}, Q(0)),
                 lambda: v.moment_interval(66, {2: 1}, Q(-1))]
        for i, call in enumerate(calls):
            with self.subTest(control=i), self.assertRaises(ValueError):
                call()

    def source_profile(self):
        c = self.capsule()
        source = c.json(v.NEW, v.PACKAGE + "/SOURCE.json")["suppliers"]["pr194"]
        return c.json(source["commit"], source["path"])["complex_profile"]

    def test_fractional_invocation_is_rejected(self):
        p = self.source_profile()
        p["child_histogram"]["1"] += 1
        with self.assertRaisesRegex(ValueError, "nonintegral"):
            v.five_stage(p)

    def test_negative_invocation_is_rejected(self):
        p = self.source_profile()
        p["child_histogram"]["2"] = 2637
        with self.assertRaisesRegex(ValueError, "nonintegral"):
            v.five_stage(p)

    def test_wrong_geometry_is_rejected(self):
        for field in ("m", "W_per_vertex"):
            p = self.source_profile()
            p[field] += 1
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "source geometry"):
                v.five_stage(p)

    def test_omitted_bridge_fails_source_derived_invoice(self):
        p = v.five_stage(self.source_profile())
        c = self.capsule().json(v.NEW, v.PACKAGE + "/certificates/network-children-pr194-five.json")
        for r in (4, 21, 42, 46):
            altered = deepcopy(c)
            altered["child_histogram"][str(r)] -= 2640
            with self.subTest(bridge=r), self.assertRaisesRegex(ValueError, "derived histogram"):
                v.check_profile(p, altered)

    def test_rank_preserving_substitution_is_detected(self):
        p = v.five_stage(self.source_profile())
        c = self.capsule().json(v.NEW, v.PACKAGE + "/certificates/network-children-pr194-five.json")
        modified = deepcopy(c)
        # Two rank-2 children become one rank-1 and one rank-3 child.
        for r, delta in ((1, 1), (2, -2), (3, 1)):
            modified["child_histogram"][str(r)] += delta
        original, altered = v.histogram(c), v.histogram(modified)
        self.assertEqual(sum(original.values()), sum(altered.values()))
        self.assertEqual(sum(r*n for r,n in original.items()), sum(r*n for r,n in altered.items()))
        lo, hi = v.moment_interval(110, original, Q(7474, 10**7))
        alo, ahi = v.moment_interval(110, altered, Q(7474, 10**7))
        self.assertTrue(ahi < lo or hi < alo)
        with self.assertRaisesRegex(ValueError, "derived histogram"):
            v.check_profile(p, modified)

    def test_next_point_cannot_replace_an_accepted_endpoint(self):
        endpoints = tuple(a + Q(1, 10**7) for a in v.ENDPOINTS)
        with patch.object(v, "ENDPOINTS", endpoints), self.assertRaisesRegex(ValueError, "exponent binding"):
            v.run(self.capsule())

    def test_falsified_interval_engines_are_rejected(self):
        engines = [lambda *a: (0, 0), lambda *a: (10**9 * v.SCALE, 10**9 * v.SCALE)]
        for engine in engines:
            with self.subTest(engine=engine), patch.object(v, "moment_interval", engine), self.assertRaises(ValueError):
                v.run(self.capsule())

    def test_original_margin_and_strict_flags_are_checked(self):
        corruptions = [("moment_upper_bound", "0/10^30"), ("margin_lower_bound", "0/10^30"),
                       ("passed", 1), ("next_grid_point_rejected", 1)]
        for field, value in corruptions:
            cap = self.capsule()
            original = cap.json

            def corrupted(commit, path):
                record = original(commit, path)
                if commit == v.NEW and path.endswith("/moment-pr144.json"):
                    record[field] = value
                return record
            with self.subTest(field=field), patch.object(cap, "json", corrupted), self.assertRaises(ValueError):
                v.run(cap)

    def test_relocation_and_disk_corruptions(self):
        with tempfile.TemporaryDirectory(prefix="pr225-independent-") as directory:
            root = Path(directory)
            names = ("verify.py", "sources.json.gz", "EXPECTED.json")
            for name in names:
                shutil.copyfile(HERE / name, root / name)
            command = [sys.executable, "-I", "-O", "-B", str(root / "verify.py")]
            env = dict(os.environ, PATH="", PYTHONPATH="")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_PR225_FIVE_STAGE_RECONCILIATION", result.stdout)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})
            controls = []
            for name in v.NAMES:
                bad = deepcopy(self.expected)
                bad["profiles"][name]["rank"] += 1
                controls.append(("EXPECTED.json", json.dumps(bad).encode()))
            bad = deepcopy(self.expected)
            bad["current_head"] = v.OLD
            controls.append(("EXPECTED.json", json.dumps(bad).encode()))
            controls.append(("sources.json.gz", b"not gzip"))
            for name, content in controls:
                (root / name).write_bytes(content)
                result = subprocess.run(command, cwd=root, env=env, capture_output=True, timeout=30)
                self.assertNotEqual(result.returncode, 0)
                (root / name).write_bytes(before[name])


if __name__ == "__main__":
    unittest.main(verbosity=2)
