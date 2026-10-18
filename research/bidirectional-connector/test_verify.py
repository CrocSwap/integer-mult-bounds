#!/usr/bin/env python3
"""Failure-sensitive package controls; standard library only. Apache-2.0."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import verify as v


class PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cert = json.loads((v.HERE / "CERTIFICATE.json").read_text())
        cls.word = v.check_certificate(cls.cert)

    def test_wrong_transfer_direction_and_source_port(self):
        for kind in ("B", "C", "A"):
            word = copy.deepcopy(self.word)
            index = next(i for i, op in enumerate(word) if op[0] == kind)
            word[index][-1] ^= 1
            with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "output map"):
                v.check_endpoint(word)

    def test_one_readout_only_works_with_clean_connector(self):
        word = [["B", 0, 0], ["A", 1, 0], ["B", 0, 0]]
        dirty = v.initial()
        want = v.initial()
        want["y1"].add(("A1", "B0", "x0"))
        self.assertNotEqual(v.interpret(word, dirty), want)
        clean = v.initial()
        clean["z0"] = set()
        want["z0"] = set()
        self.assertEqual(v.interpret(word, clean), want)

    def test_cancelling_transfers_are_paid(self):
        padded = self.word + [["C", 1], ["C", 1]]
        v.check_endpoint(padded)
        self.assertEqual(v.invoice(padded)["root_calls"], 80)
        self.assertEqual(v.invoice(padded)["transfers"], [3, 5])

    def test_certificate_corruptions(self):
        variants = []
        cert = copy.deepcopy(self.cert)
        cert["invoice"]["dirty_root_rows"] = 1
        variants.append((cert, "unpaid"))
        cert = copy.deepcopy(self.cert)
        cert["invoice"]["root_calls"] -= 1
        variants.append((cert, "unpaid"))
        cert = copy.deepcopy(self.cert)
        cert["boundaries"][1]["dirty"][1] = 0
        variants.append((cert, "boundary evidence"))
        cert = copy.deepcopy(self.cert)
        del cert["readouts"]["31"]
        variants.append((cert, "readout evidence"))
        for cert, reason in variants:
            with self.subTest(reason=reason), self.assertRaisesRegex(ValueError, reason):
                v.check_certificate(cert)

    def test_reject_invalid_ports_and_indices(self):
        for op in (["C", 2], ["C", True], ["B", 5, 0], ["A", 0, 0], ["C", 0, 1], ["RESET", 0]):
            with self.subTest(op=op), self.assertRaises(ValueError):
                v.ports(op)

    def test_relocated_cli_and_actual_file_corruptions(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "package"
            shutil.copytree(v.HERE, target, ignore=shutil.ignore_patterns("__pycache__"))
            def cli():
                return subprocess.run([sys.executable, "-I", "-O", "-B", str(target / "verify.py")],
                                      cwd=temp, capture_output=True, text=True, timeout=20)
            result = cli()
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_BIDIRECTIONAL_CONNECTOR", result.stdout)
            corrupted = copy.deepcopy(self.cert)
            corrupted["invoice"]["root_calls"] = 77
            (target / "CERTIFICATE.json").write_text(json.dumps(corrupted))
            result = cli()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unpaid", result.stderr)
            (target / "CERTIFICATE.json").write_text(json.dumps(self.cert))
            reference = target / "references/PR1615-CERTIFICATE.json"
            reference.write_bytes(reference.read_bytes() + b" ")
            result = cli()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("SHA256 drift", result.stderr)


if __name__ == "__main__":
    unittest.main()
