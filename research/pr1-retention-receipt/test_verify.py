"""Failure controls for the PR1 retention receipt.

One real-evidence positive case and twelve mutation controls: every control
mutates exactly one retained input or evidence record and must be rejected.

Aaron Wang, with help from opencode. Apache-2.0.
"""

import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verify

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))

ROOT_FILES = [
    "CITATION.cff",
    "Makefile",
    "NOTICE",
    "README.md",
    "docs/reproducibility.md",
    "CONTRIBUTORS.md",
    "docs/research/pr-ledger.json",
    "research/overnight-pr-review-20261009/source-inventory.json",
    "research/overnight-pr-review-20261009/dispositions.json",
]


def build_copy(tmp):
    root = os.path.join(tmp, "root")
    package = os.path.join(root, "research", "pr1-retention-receipt")
    for rel in ROOT_FILES:
        dst = os.path.join(root, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(ROOT, rel.replace("/", os.sep)), dst)
    shutil.copytree(HERE, package,
                    ignore=shutil.ignore_patterns("__pycache__"))
    return root, package


def mutate(path, old, new):
    with open(path, "rb") as fh:
        data = fh.read()
    need = old in data
    if not need:
        raise AssertionError("mutation anchor not found in " + path)
    with open(path, "wb") as fh:
        fh.write(data.replace(old, new, 1))


class ReceiptControls(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pr1-receipt-")
        self.root, self.package = build_copy(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def assert_rejected(self):
        with self.assertRaises(verify.ReceiptError):
            verify.verify(self.root, self.package)

    def test_00_positive(self):
        result = verify.verify(self.root, self.package)
        self.assertEqual(result["totals"]["paths"], 11)
        self.assertEqual(result["totals"]["substantive_surviving_lines"], 0)

    def test_01_vendored_byte_tamper(self):
        mutate(os.path.join(self.package, "inputs", "PR1-HEAD", "CITATION.cff"),
               b"family-names", b"family-namez")
        self.assert_rejected()

    def test_02_rest_blob_sha_tamper(self):
        p = os.path.join(self.package, "inputs", "pr1-files-api.json")
        mutate(p, b"afddca08c8fa9b48eb4fbfa9e2b60d2a13aa0d9b", b"bfddca08c8fa9b48eb4fbfa9e2b60d2a13aa0d9b")
        self.assert_rejected()

    def test_03_rest_additions_tamper(self):
        p = os.path.join(self.package, "inputs", "pr1-files-api.json")
        mutate(p, b'"additions":5', b'"additions":6')
        self.assert_rejected()

    def test_04_patch_line_removed(self):
        p = os.path.join(self.package, "inputs", "pr1-files-api.json")
        mutate(p, b"+  - family-names: Prosz", b"+  - family-namez: Prosz")
        self.assert_rejected()

    def test_05_base_notice_line_dropped(self):
        mutate(os.path.join(self.root, "NOTICE"),
               b"Aurel Prosz", b"Aurel Prosz X")
        self.assert_rejected()

    def test_06_citation_convention_line_removed(self):
        mutate(os.path.join(self.root, "CITATION.cff"),
               b"Project-level authorship identifies the maintainer",
               b"Project-level authors hip identifies the maintainer")
        self.assert_rejected()

    def test_07_contributors_row_removed(self):
        mutate(os.path.join(self.root, "CONTRIBUTORS.md"),
               b"| Aurel Prosz (Paureel) |", b"| Xurel Prosz (Paureel) |")
        self.assert_rejected()

    def test_08_forged_tree_copy(self):
        forged = ("100644 blob 3de09ae19388dda084afa0b6064ff368b9d09ae5\t"
                  "research/forged/paired-tuned-parameters.json\n")
        p = os.path.join(self.package, "inputs", "head-tree.txt")
        with open(p, "ab") as fh:
            fh.write(forged.encode())
        self.assert_rejected()

    def test_09_credit_enumeration_shrunk(self):
        p = os.path.join(self.package, "inputs", "credit-mentions.txt")
        with open(p, "rb") as fh:
            lines = fh.read().splitlines()
        with open(p, "wb") as fh:
            fh.write(b"\n".join(lines[:10]) + b"\n")
        self.assert_rejected()

    def test_10_dispositions_head_tamper(self):
        p = os.path.join(self.root, "research",
                         "overnight-pr-review-20261009", "dispositions.json")
        with open(p, encoding="utf-8") as fh:
            data = json.load(fh)
        for rec in data:
            if rec.get("number") == 1:
                rec["head"] = "cfb168a5611c9eb219d04cf7d551edf1517ecd78"
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh)
        self.assert_rejected()

    def test_11_inventory_paths_tamper(self):
        p = os.path.join(self.root, "research",
                         "overnight-pr-review-20261009", "source-inventory.json")
        with open(p, encoding="utf-8") as fh:
            data = json.load(fh)
        for rec in data:
            if rec.get("number") == 1:
                rec["changed_paths"][0] = "CITATION.cffX"
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh)
        self.assert_rejected()

    def test_12_expected_result_tamper(self):
        p = os.path.join(self.package, "RESULT.json")
        with open(p, encoding="utf-8") as fh:
            data = json.load(fh)
        data["totals"]["added_lines"] += 1
        with open(p, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")
        self.assert_rejected()


if __name__ == "__main__":
    unittest.main()
