#!/usr/bin/env python3
"""Corruption, coverage and accounting controls on the real pinned evidence.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import base64
from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class RetentionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = v.loads((v.HERE / "SOURCE-PROOF.json").read_bytes())
        cls.archive, cls.reviews = v.external_inputs()
        proof = v.Proof(cls.document)
        cls.data = {role: v.loads(proof.blob(role)) for role in v.BLOBS if role != "original_notice"}

    def check(self, document=None, archive=None, reviews=None):
        return v.verify(self.document if document is None else document,
                        self.archive if archive is None else archive,
                        self.reviews if reviews is None else reviews)

    def test_complete_positive_case(self):
        self.assertEqual(self.check(), v.loads((v.HERE / "RESULT.json").read_bytes()))

    def test_omitted_package_file(self):
        doc = deepcopy(self.document)
        del doc["files"]["experiments/round7-review/saturated-Z.json.gz"]
        with self.assertRaisesRegex(ValueError, "inventory"):
            self.check(document=doc)

    def test_same_count_file_substitution(self):
        doc = deepcopy(self.document)
        row = doc["files"].pop("NOTICE")
        doc["files"]["unrelated-NOTICE"] = row
        with self.assertRaisesRegex(ValueError, "inventory"):
            self.check(document=doc)

    def test_mode_substitution(self):
        doc = deepcopy(self.document)
        doc["files"]["README.md"]["mode"] = "100755"
        with self.assertRaisesRegex(ValueError, "inventory"):
            self.check(document=doc)

    def test_commit_byte_corruption(self):
        doc = deepcopy(self.document)
        obj = doc["objects"][v.PR99]
        obj["base64"] = base64.b64encode(base64.b64decode(obj["base64"]) + b"\n").decode()
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.check(document=doc)

    def test_missing_comparison_parent(self):
        doc = deepcopy(self.document)
        del doc["objects"][v.PARENT]
        with self.assertRaisesRegex(ValueError, "missing Git object"):
            self.check(document=doc)

    def test_missing_descendant_tree(self):
        doc = deepcopy(self.document)
        proof = v.Proof(doc)
        _, oid = proof.resolve(v.PR99, v.ORIGINAL + "/experiments/round7-review/vendor/lean")
        del doc["objects"][oid]
        with self.assertRaisesRegex(ValueError, "missing Git object"):
            self.check(document=doc)

    def test_accounting_blob_corruption(self):
        doc = deepcopy(self.document)
        proof = v.Proof(doc)
        _, oid = proof.resolve(*v.BLOBS["bit_ledger"])
        doc["objects"][oid]["base64"] = base64.b64encode(b"{}").decode()
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.check(document=doc)

    def test_archive_omits_retaining_parent(self):
        archive = deepcopy(self.archive)
        archive["parents"].remove(v.PR103)
        with self.assertRaisesRegex(ValueError, "archive receipt"):
            self.check(archive=archive)

    def test_review_head_substitution(self):
        reviews = deepcopy(self.reviews)
        reviews["103"]["head"] = v.PR99
        with self.assertRaisesRegex(ValueError, "different head"):
            self.check(reviews=reviews)

    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            v.loads('{"files":{},"files":{"NOTICE":{}}}')

    def test_duplicate_histogram_rank(self):
        data = deepcopy(self.data)
        hist = data["candidate"]["Z"]["histogram"]["hist"]
        hist.append(hist[0])
        with self.assertRaisesRegex(ValueError, "duplicate histogram rank"):
            v.check_accounting(**data)

    def test_duplicate_changed_slot(self):
        data = deepcopy(self.data)
        changes = data["candidate"]["Z"]["changes"]
        changes[1]["slot"] = changes[0]["slot"]
        with self.assertRaisesRegex(ValueError, "duplicate changed slot"):
            v.check_accounting(**data)

    def test_omitted_double_extension(self):
        data = deepcopy(self.data)
        changes = data["candidate"]["Z"]["changes"]
        next(c for c in changes if c["new_dim"] - c["old_dim"] == 2)["new_dim"] -= 1
        with self.assertRaisesRegex(ValueError, "dimension increase"):
            v.check_accounting(**data)

    def test_changed_width(self):
        data = deepcopy(self.data)
        data["candidate"]["Z"]["histogram"]["W"] += 1
        with self.assertRaisesRegex(ValueError, "common parameter"):
            v.check_accounting(**data)

    def test_mass_preserving_wrong_profile(self):
        data = deepcopy(self.data)
        hist = data["candidate"]["Z"]["histogram"]["hist"]
        # -3 H1 + H3 preserves total rank, but is not the retained profile.
        for entry in hist:
            if entry[0] == 1:
                entry[1] -= 3
            if entry[0] == 3:
                entry[1] += 1
        with self.assertRaisesRegex(ValueError, "22 recorded mergers"):
            v.check_accounting(**data)

    def test_component_charge_omission(self):
        data = deepcopy(self.data)
        data["prior_review"]["independently_recomputed_component_deltas"]["slot_chains"] = {}
        with self.assertRaisesRegex(ValueError, "component accounting"):
            v.check_accounting(**data)

    def test_pr103_histogram_substitution(self):
        data = deepcopy(self.data)
        data["bit_ledger"]["histogram"] = {str(k): n for k, n in data["baseline"]["histogram"]["hist"]}
        with self.assertRaisesRegex(ValueError, "exact candidate histogram"):
            v.check_accounting(**data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
