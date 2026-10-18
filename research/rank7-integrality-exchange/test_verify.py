# SPDX-License-Identifier: Apache-2.0
"""Observable certificate, source-binding and optimized-execution checks."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

import moment
import verify


class CertificateTests(unittest.TestCase):
    def test_literal_journal_and_preimage(self):
        source = {"rows": [[0, 0, 1, 2, 3, 0]]}
        certificate = {"edits": [[0, [0, 0, 1, 2, 3, 0], [0, 0, 1, 2, 4, 0]]]}
        result = verify.apply(source, certificate)
        self.assertEqual(result["rows"], [[0, 0, 1, 2, 4, 0]])
        self.assertEqual(source["rows"], [[0, 0, 1, 2, 3, 0]])
        with self.assertRaisesRegex(ValueError, "journal preimage"):
            verify.apply(result, certificate)
        wrong_call = {"edits": [[0, source["rows"][0], [1, 0, 1, 2, 4, 0]]]}
        with self.assertRaisesRegex(ValueError, "fixed call/helper"):
            verify.apply(source, wrong_call)

    def test_source_bytes_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            payload = root / "input.json"
            payload.write_text("{}", encoding="utf-8")
            manifest = {
                "files": [
                    {
                        "path": "input.json",
                        "usage": "input",
                        "sha256": hashlib.sha256(b"{}").hexdigest(),
                    }
                ]
            }
            (root / "SOURCES.json").write_text(json.dumps(manifest), encoding="utf-8")
            with (
                patch.object(verify, "ROOT", root),
                patch.object(verify, "PACKAGE", root),
            ):
                self.assertEqual(len(verify.authenticate()), 1)
                payload.write_text('{"changed":true}', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "source digest"):
                    verify.authenticate()

    def test_exact_root_and_sign(self):
        profile = {
            1: 1645680,
            2: 470196,
            3: 159468,
            4: 71928,
            5: 13716,
            8: 5328,
            48: 28190,
        }
        self.assertEqual(
            moment.root(profile),
            (
                Fraction("0.0017290339826465135177175"),
                Fraction("0.0017290339826465135177176"),
            ),
        )
        self.assertEqual(moment.sign_certificate()["derivative_upper"], "-60509/125000")
        self.assertEqual(moment.exponential((0, 0)), (moment.SCALE, moment.SCALE))
        with self.assertRaisesRegex(ValueError, "strict root improvement"):
            verify.strict_gain(profile, profile)

    def test_optimized_cli_preserves_checks(self):
        outputs = []
        for optimize in (False, True):
            with tempfile.TemporaryDirectory() as cache:
                command = [
                    sys.executable,
                    "-X",
                    "pycache_prefix=" + cache,
                    "-B",
                    "-W",
                    "error",
                ]
                if optimize:
                    command.append("-O")
                command.append(str(verify.PACKAGE / "verify.py"))
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=60
                )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stdout.strip(),
                "PASS_RANK7_INTEGRALITY_EXCHANGE roles=271728 moved=44 controls=11",
            )
            outputs.append(result.stdout)
        self.assertEqual(outputs[0], outputs[1])


if __name__ == "__main__":
    unittest.main()
