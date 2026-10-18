#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Adversarial input and authentication tests for the independent replay.

These tests use the frozen table, never the producer or sparse interpreter.
Prepared for David Arias with substantial OpenAI Codex assistance.
"""
import copy
import hashlib
import importlib.util
import json
import marshal
from pathlib import Path
import struct
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import independent_check as checked


class IndependentBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.table = json.loads((checked.HERE / "TABLE.json").read_text())

    def fixture(self):
        return checked.fixtures((1, 3, 1, 1), checked.pattern(9, 17))

    def require_reject(self, bank):
        for name in ("forward", "inverse"):
            with self.subTest(direction=name):
                with self.assertRaisesRegex(checked.CheckFailure, "^table rejected:"):
                    checked.execute(self.table[name], bank, 100000)

    def test_zero_empty_and_noncanonical_descriptors_reject(self):
        for tape in (4, 5, 6, 7):
            for malformed in ([checked.ZERO], [], [checked.ONE, checked.ZERO]):
                with self.subTest(tape=tape, malformed=malformed):
                    bank = self.fixture()
                    bank[tape] = checked.marked(malformed, 0)
                    self.require_reject(bank)

    def test_short_and_long_payloads_reject(self):
        for size in (8, 10):
            bank = self.fixture()
            bank[0] = checked.marked([checked.ZERO] * size, 0)
            self.require_reject(bank)

    def test_nonboolean_payload_rejects(self):
        bank = self.fixture()
        bank[0][0][4] = checked.UNIT
        self.require_reject(bank)

    def test_occupied_work_origins_reject(self):
        # Global blank work is a precondition. This is the locally checked
        # origin violation, not a claim that every distant dirty cell is read.
        for tape in (1,) + checked.WORK:
            with self.subTest(tape=tape):
                bank = self.fixture()
                bank[tape] = ({0: checked.ONE}, 0)
                self.require_reject(bank)

    def test_nonlocal_schema_and_duplicate_symbol_branches_reject(self):
        for replacement in (["move", 0, 2], ["write", True, checked.ZERO],
                            ["branch", 0, [[checked.ZERO, 0], [checked.ZERO, 1]], 0]):
            with self.subTest(replacement=replacement):
                program = copy.deepcopy(self.table["forward"])
                program["instructions"][0] = replacement
                with self.assertRaises(checked.CheckFailure):
                    checked.validate_program(program)

    def test_both_source_hashes_are_checked(self):
        raw = b"source identity\n"
        record = {"sha256": hashlib.sha256(raw).hexdigest(), "git_blob": "0" * 40}
        with self.assertRaisesRegex(checked.CheckFailure, "Git blob"):
            checked.authenticate(raw, record)

    def test_authenticated_source_ignores_stale_timestamp_bytecode(self):
        original_here = checked.HERE
        raw = (original_here.parents[1] / checked.SOURCE_PATH).read_bytes()
        manifest = json.loads((original_here / "SOURCES.json").read_text())
        record = next(row for row in manifest["files"] if row["path"] == checked.SOURCE_PATH)
        with tempfile.TemporaryDirectory(prefix="ordered-shear-auth-") as temporary:
            root = Path(temporary)
            package = root / "research/fixed-tape-ordered-shear"
            package.mkdir(parents=True)
            source = root / checked.SOURCE_PATH
            source.parent.mkdir(parents=True)
            source.write_bytes(raw)
            manifest_path = package / "SOURCES.json"
            manifest_path.write_text(json.dumps({"files": [record]}))
            cached = Path(importlib.util.cache_from_source(str(source)))
            cached.parent.mkdir(parents=True)
            malicious = compile("raise RuntimeError('STALE_PYC_EXECUTED')", str(source), "exec")
            header = importlib.util.MAGIC_NUMBER + struct.pack("<III", 0, int(source.stat().st_mtime), len(raw))
            cached.write_bytes(header + marshal.dumps(malicious))
            try:
                checked.HERE = package
                loaded, authenticated, _ = checked.predecessor(manifest_path)
                self.assertEqual(authenticated, raw)
                self.assertTrue(callable(loaded.add_high))
                # Tampering must fail before any source statement executes.
                source.write_bytes(b"raise RuntimeError('TAMPERED_SOURCE_EXECUTED')\n")
                with self.assertRaisesRegex(checked.CheckFailure, "SHA256 mismatch"):
                    checked.predecessor(manifest_path)
            finally:
                checked.HERE = original_here


if __name__ == "__main__":
    unittest.main()
