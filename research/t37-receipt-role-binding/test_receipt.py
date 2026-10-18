#!/usr/bin/env python3
"""Failure controls for portable T37 receipt comparison. Apache-2.0."""
from copy import deepcopy
import json
from pathlib import Path, PurePosixPath
import runpy
import subprocess
import sys
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))
R = V["R"]


class ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest, cls.original, cls.expected = V["fixtures"](V["ROOT"])
        cls.paths = R["historical_paths"]()
        cls.legacy = staticmethod(runpy.run_path(str(V["ROOT"] / V["PREDECESSOR"] / "common.py"))["normalize"])

    def test_role_transpositions_are_not_portable_equivalence(self):
        roles = sorted(self.paths)
        for i, a in enumerate(roles):
            for b in roles[i + 1:]:
                changed = deepcopy(self.original)
                x, y = self.paths[a], self.paths[b]
                changed["input_sha256"][x], changed["input_sha256"][y] = changed["input_sha256"][y], changed["input_sha256"][x]
                self.assertEqual(self.legacy(changed, self.manifest), self.expected)
                with self.assertRaisesRegex(ValueError, "input digest for role"):
                    R["compare"](changed, self.paths, self.expected)

    def test_role_bindings_and_other_fields(self):
        result = V["controls"](self.original, self.expected)
        self.assertEqual(len(result["rejected"]), 11)
        self.assertEqual(len(result["accepted"]), 6)

    def test_strict_json_reader(self):
        with tempfile.TemporaryDirectory(prefix="t37-json-controls-") as tmp:
            path = Path(tmp) / "receipt.json"
            for bad in (b'{"input_sha256": {}, "input_sha256": {}}',
                        b'{"nested": {"proof": true, "proof": false}}',
                        b'{"value": NaN}', b'{"value": Infinity}'):
                path.write_bytes(bad)
                with self.assertRaises(ValueError):
                    R["read_json"](path)
            path.write_bytes(b'{"roles": 167832, "label": "valid"}')
            self.assertEqual(R["read_json"](path), {"roles": 167832, "label": "valid"})

    def test_nonfinite_or_relative_input(self):
        changed = deepcopy(self.original)
        changed["new_field"] = float("inf")
        with self.assertRaises(ValueError):
            R["compare"](changed, self.paths, self.expected)
        with self.assertRaisesRegex(ValueError, "absolute invocation roots"):
            R["runtime_paths"](PurePosixPath("relative"), PurePosixPath("/inputs"))

    def test_source_pin_before_import(self):
        # The first live input is corrupted in an otherwise empty root: the
        # expected source-pin error must occur before any predecessor import.
        rows = R["read_json"](HERE / "SOURCES.json")["files"]
        row = next(item for item in rows if item["usage"] == "input")
        with tempfile.TemporaryDirectory(prefix="t37-source-control-") as tmp:
            root = Path(tmp)
            path = root / row["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"changed source")
            with self.assertRaisesRegex(ValueError, "source pin"):
                V["check_sources"](root)

    def test_result_tampering_rejected(self):
        # The verifier must recompute the census, rather than trust RESULT.json.
        with tempfile.TemporaryDirectory(prefix="t37-result-control-") as tmp:
            package = Path(tmp)
            for name in ("verify.py", "receipt.py", "SOURCES.json", "RESULT.json"):
                (package / name).write_bytes((HERE / name).read_bytes())
            result = R["read_json"](package / "RESULT.json")
            result["permutation_audit"]["strict_equal"] = 2
            (package / "RESULT.json").write_text(json.dumps(result), encoding="utf-8")
            run = subprocess.run([sys.executable, "-I", "-B", str(package / "verify.py"),
                                  "--source-root", str(V["ROOT"]), "--audit-only"],
                                 capture_output=True, text=True, timeout=60)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("complete audit result changed", run.stderr)


if __name__ == "__main__":
    unittest.main()
