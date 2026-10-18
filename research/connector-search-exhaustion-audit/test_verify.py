#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-boundary controls independent of the native branch fixtures."""

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


class SourceBoundary(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="search-input-control-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        inventory = json.loads((verify.HERE / "SOURCES.json").read_bytes())
        self.inventory = self.root / "SOURCES.json"
        self.inventory.write_text(json.dumps(inventory))
        for row in inventory["files"]:
            if row["usage"] == "input":
                target = self.root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / row["path"], target)

    def test_identical_source_export(self):
        self.assertEqual(
            verify.authenticated_source(self.root, self.inventory),
            (verify.ROOT / verify.SOURCE).read_text(),
        )

    def test_changed_native_source_rejected(self):
        source = self.root / verify.SOURCE
        source.write_bytes(source.read_bytes() + b"\n")
        with self.assertRaises(ValueError):
            verify.authenticated_source(self.root, self.inventory)

    def test_missing_declared_input_rejected(self):
        (self.root / "research/connector-covering-code/README.md").unlink()
        with self.assertRaises(ValueError):
            verify.authenticated_source(self.root, self.inventory)

    def test_symlinked_source_rejected(self):
        source = self.root / verify.SOURCE
        target = source.with_name("copied-source.cpp")
        source.rename(target)
        source.symlink_to(target.name)
        with self.assertRaises(ValueError):
            verify.authenticated_source(self.root, self.inventory)

    def test_truncated_inventory_rejected(self):
        record = json.loads(self.inventory.read_bytes())
        record["files"].pop()
        self.inventory.write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            verify.authenticated_source(self.root, self.inventory)

    def test_duplicate_inventory_rejected(self):
        record = json.loads(self.inventory.read_bytes())
        record["files"][-1] = record["files"][-2]
        self.inventory.write_text(json.dumps(record))
        with self.assertRaises(ValueError):
            verify.authenticated_source(self.root, self.inventory)


if __name__ == "__main__":
    unittest.main()
