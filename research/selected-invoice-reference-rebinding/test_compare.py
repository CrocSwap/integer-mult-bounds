#!/usr/bin/env python3
"""Focused semantic controls; normal and optimized execution must agree.

Adam Gall, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import contextlib
import gzip
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compare_invoice as engine
import verify


class InvoiceComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        corpus = verify.load_corpus()
        cls.source = {name: corpus[name] for name in engine.FILES}
        cls.portable = verify.rebound(cls.source, verify.dump(
            json.loads(cls.source[engine.INVOICE]), sort_keys=True))

    def test_valid_portability_and_stale_edges(self):
        self.assertTrue(engine.compare(self.source, self.portable)["equivalent"])
        for name in engine.CONSUMERS:
            stale = dict(self.portable)
            stale[name] = self.source[name]
            with self.assertRaisesRegex(engine.InvalidGraph, "fresh_invoice"):
                engine.compare(self.source, stale)
            # The reference is validated too; equal bad inputs never shortcut.
            with self.assertRaisesRegex(engine.InvalidGraph, "fresh_invoice"):
                engine.compare(stale, stale)

    def test_synchronized_semantic_change_and_unknown_digest(self):
        invoice = json.loads(self.source[engine.INVOICE])
        invoice["providers"]["gauge44"]["local"]["forward"]["all_dirty_helper_columns_restored"] = False
        changed = verify.rebound(self.source, verify.dump(invoice))
        report = engine.compare(self.source, changed)
        self.assertFalse(report["equivalent"])
        self.assertEqual(set(report["different_files"]), set(engine.FILES))
        # No blanket treatment of other digest-looking fields.
        value = json.loads(self.source["ASSEMBLY.json"])
        value["input_sha256"]["owner_audit"] = "0" * 64
        changed = dict(self.source)
        changed["ASSEMBLY.json"] = verify.dump(value)
        self.assertFalse(engine.compare(self.source, changed)["equivalent"])

    def test_typed_json_duplicate_and_number_domain(self):
        self.assertNotEqual(engine.canonical(engine.parse(b'{"x":true}')),
                            engine.canonical(engine.parse(b'{"x":1}')))
        self.assertEqual(engine.canonical(engine.parse(b'{"x":"P"}')),
                         engine.canonical(engine.parse(b'{"x":"\\u0050"}')))
        for raw in (b'{"x":1,"x":1}', b'{"x":NaN}', b'{"x":Infinity}',
                    b'{"x":-Infinity}', b'{"x":1.0}', b'{"x":1e0}',
                    b'{"x":0.10000000000000000000000000001}', b'\xff'):
            with self.subTest(raw=raw):
                with self.assertRaises(engine.InvalidGraph):
                    engine.parse(raw)

    def test_complete_shape_and_list_order(self):
        for extra in (False, True):
            malformed = dict(self.source)
            if extra:
                malformed["unexpected.json"] = b'{}'
            else:
                del malformed[engine.INVOICE]
            with self.assertRaises(engine.InvalidGraph):
                engine.normalized(malformed)
        changed = dict(self.source)
        changed["ADMISSION-CONTROLS.json"] = b'[]'
        with self.assertRaisesRegex(engine.InvalidGraph, "JSON object"):
            engine.normalized(changed)
        value = json.loads(self.source["ADMISSION-CONTROLS.json"])
        value["rejected_controls"].reverse()
        changed["ADMISSION-CONTROLS.json"] = verify.dump(value)
        self.assertFalse(engine.compare(self.source, changed)["equivalent"])

    def test_independent_oracle_retains_types_and_empty_containers(self):
        for a, b in ((True, 1), ({"empty": []}, {}), ({"empty": {}}, {}),
                     ([1, 2], [2, 1]), ("1", 1)):
            self.assertNotEqual(verify.typed(a), verify.typed(b))
        self.assertEqual(verify.oracle(self.source), verify.oracle(self.portable))
        faulty = dict(engine.normalized(self.source))
        value = json.loads(faulty[engine.INVOICE])
        del value["provider_phase_semantic_sha256"]
        faulty[engine.INVOICE] = engine.canonical(value)
        self.assertNotEqual(verify.typed(json.loads(faulty[engine.INVOICE])),
                            verify.typed(json.loads(self.source[engine.INVOICE])))

    def test_cli_equivalent_different_and_invalid(self):
        with tempfile.TemporaryDirectory(prefix="invoice-cli-") as tmp:
            base = Path(tmp)
            reference, candidate = base / "reference", base / "candidate"
            for directory, files in ((reference, self.source), (candidate, self.portable)):
                for name, raw in files.items():
                    target = directory / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(raw)
            argv = [sys.executable, "-I", "-O", "-B", str(HERE / "compare_invoice.py"),
                    str(reference), str(candidate)]
            good = subprocess.run(argv, capture_output=True, text=True, check=False, timeout=10)
            self.assertEqual(good.returncode, 0, good.stderr + good.stdout)
            self.assertTrue(json.loads(good.stdout)["equivalent"])
            value = json.loads((candidate / "ASSEMBLY.json").read_bytes())
            value["kappa"] = "0"
            (candidate / "ASSEMBLY.json").write_bytes(verify.dump(value))
            changed = subprocess.run(argv, capture_output=True, text=True, check=False, timeout=10)
            self.assertEqual(changed.returncode, 1, changed.stderr + changed.stdout)
            self.assertFalse(json.loads(changed.stdout)["equivalent"])
            (candidate / "ASSEMBLY.json").write_bytes(self.source["ASSEMBLY.json"])
            invalid = subprocess.run(argv, capture_output=True, text=True, check=False, timeout=10)
            self.assertEqual(invalid.returncode, 2, invalid.stderr + invalid.stdout)
            self.assertFalse(json.loads(invalid.stdout)["valid_graph"])

    def test_immutable_archive_header_drift_rejected(self):
        manifest = json.loads((HERE / "SOURCES.json").read_bytes())
        with tempfile.TemporaryDirectory(prefix="invoice-pin-") as tmp:
            exported = Path(tmp)
            for row in manifest["files"]:
                if row["usage"] != "input":
                    continue
                target = exported / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((verify.ROOT / row["path"]).read_bytes())
            archive = exported / verify.ARCHIVE
            original = archive.read_bytes()
            modified = bytearray(original)
            modified[4] ^= 1  # MTIME only: does not change the decompressed tar.
            self.assertEqual(gzip.decompress(original), gzip.decompress(modified))
            archive.write_bytes(modified)
            with self.assertRaisesRegex(RuntimeError, "immutable source hash mismatch"):
                verify.check_sources(exported)

    def test_missing_cli_file_is_not_equivalent(self):
        with tempfile.TemporaryDirectory(prefix="invoice-missing-") as tmp:
            with contextlib.redirect_stdout(io.StringIO()) as output:
                code = engine.main([tmp, tmp])
            self.assertEqual(code, 2)
            self.assertFalse(json.loads(output.getvalue())["valid_graph"])


if __name__ == "__main__":
    unittest.main()
