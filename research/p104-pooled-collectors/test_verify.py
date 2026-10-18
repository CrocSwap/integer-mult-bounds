#!/usr/bin/env python3
"""Behavioral checks for the local pooled-collector package."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class PooledBehavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sparse = module("sparse_audit", HERE / "verify.py")
        cls.dense = module("dense_audit", HERE / "independent.py")
        cls.word = cls.sparse.load(cls.sparse.NATIVE / "LOWRANK-WITNESS.json")
        fixture = cls.sparse.load(cls.sparse.NATIVE / "P104-FIXTURE.json")["section4_explicit_P104"]
        cls.ports = cls.sparse.root_ports(fixture)
        cls.circuit = cls.sparse.load(HERE / "CIRCUIT.json")

    def command(self, script, *arguments, directory=HERE):
        return subprocess.run([sys.executable, "-I", "-O", "-B", str(directory / script), *map(str, arguments)],
                              capture_output=True, text=True, timeout=60, check=False)

    def test_complete_receipt_and_literal_regeneration(self):
        actual = self.sparse.check(self.circuit)
        self.assertEqual(actual, self.sparse.load(HERE / "RESULT.json"))
        self.assertEqual(actual["helpers"], 91)
        self.assertEqual(actual["endpoint_coefficients"], 137641)
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "generated.json"
            result = self.command("build.py", "--out", out)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(out.read_text()), self.circuit)
            refusal = self.command("build.py", "--out", out)
            self.assertNotEqual(refusal.returncode, 0)
            self.assertEqual(json.loads(out.read_text()), self.circuit)

    def test_equivalent_pooled_frame_bases(self):
        altered = deepcopy(self.circuit)
        registers = set(altered["pooled_groups"]["helpers"])
        for part in altered["insertions"]:
            for event in part["events"]:
                if self.sparse.footprint(event, registers):
                    if event[0] == "transport":
                        event[2], event[3] = event[2][::-1], event[3][::-1]
                    else:
                        event[-1] = event[-1][::-1]
        self.sparse.replay(self.word, altered, self.ports)
        self.assertEqual(self.dense.audit(altered, self.word, self.ports), 137641)

    def test_real_capture_and_frame_faults(self):
        altered = deepcopy(self.circuit)
        event = next(e for p in altered["insertions"] for e in p["events"]
                     if e[0] == "add" and e[1] in altered["pooled_groups"]["helpers"] and e[2].startswith("X"))
        event[3] = "0"
        with self.assertRaisesRegex(ValueError, "endpoint"):
            self.sparse.replay(self.word, altered, self.ports)
        with self.assertRaisesRegex(ValueError, "endpoint"):
            self.dense.audit(altered, self.word, self.ports)
        altered = deepcopy(self.circuit)
        event = next(e for p in altered["insertions"] for e in p["events"] if e[:2] == ["add", "POOL1"])
        event[-1] = []
        with self.assertRaisesRegex(ValueError, "common-chart"):
            self.sparse.replay(self.word, altered, self.ports)
        with self.assertRaisesRegex(ValueError, "common chart"):
            self.dense.audit(altered, self.word, self.ports)

    def test_export_read_only_and_integrity(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "research/p104-pooled-collectors"
            shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
            native = root / "research/p104-native-channel/inputs"
            native.mkdir(parents=True)
            for name in ("LOWRANK-WITNESS.json", "P104-FIXTURE.json"):
                shutil.copyfile(self.sparse.NATIVE / name, native / name)
            files = sorted(p for p in root.rglob("*") if p.is_file())
            before = {p.relative_to(root): p.read_bytes() for p in files}
            for path in files:
                path.chmod(0o444)
            for script, marker in (("verify.py", "PASS_P104_POOLED_COLLECTORS"),
                                   ("independent.py", "PASS_P104_POOLED_INDEPENDENT")):
                result = self.command(script, directory=package)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(marker, result.stdout)
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            self.assertEqual(after, before)
            receipt = package / "RESULT.json"
            receipt.chmod(0o644)
            wrong = json.loads(receipt.read_text())
            wrong["helpers"] = 90
            receipt.write_text(json.dumps(wrong))
            result = self.command("verify.py", directory=package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt equality", result.stderr)
            receipt.unlink()
            result = self.command("verify.py", directory=package)
            self.assertNotEqual(result.returncode, 0)
            receipt.write_bytes(before[receipt.relative_to(root)])
            source = native / "LOWRANK-WITNESS.json"
            source.chmod(0o644)
            source.write_bytes(source.read_bytes() + b" ")
            for script in ("verify.py", "independent.py"):
                result = self.command(script, directory=package)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("source pin", result.stderr)

    def test_output_refusal(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "receipt.json"
            output.write_text("do not replace")
            result = self.command("verify.py", "--out", output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), "do not replace")


if __name__ == "__main__":
    unittest.main()
