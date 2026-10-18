#!/usr/bin/env python3
"""Corruption, coverage, provenance and accounting controls on the real pinned evidence.

steph4n (@steph4n-gh), with substantial Google Gemini assistance. Apache-2.0.
"""
import base64
from copy import deepcopy
import gzip
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class RetentionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = v.loads((v.HERE / "SOURCE-PROOF.json").read_bytes())
        cls.archive, cls.reviews, cls.r9_ledger, cls.r9_log, cls.contributors = v.external_inputs()
        proof = v.Proof(cls.document)
        _, c205_oid = proof.resolve(v.PR205, v.PACKED_DIR + "/certificate.json", "100644")
        _, c211_oid = proof.resolve(v.PR211, v.CASCADE_DIR + "/certificate.json", "100644")
        _, src_oid = proof.resolve(v.PR211, v.CASCADE_DIR + "/SOURCE.json", "100644")
        _, b64_oid = proof.resolve(v.PR217, v.PR217_FRAMES_B64_PATH, "100644")
        cls.c205 = v.loads(proof.raw(c205_oid, "blob"))
        cls.c211 = v.loads(proof.raw(c211_oid, "blob"))
        cls.source_meta = v.loads(proof.raw(src_oid, "blob"))
        frames_raw = gzip.decompress(base64.b64decode(proof.raw(b64_oid, "blob").rstrip(b"\n"), validate=True))
        cls.bases = v.loads(frames_raw)

    def check(self, document=None, archive=None, reviews=None, r9_ledger=None, r9_log=None, contributors=None):
        return v.verify(
            self.document if document is None else document,
            self.archive if archive is None else archive,
            self.reviews if reviews is None else reviews,
            self.r9_ledger if r9_ledger is None else r9_ledger,
            self.r9_log if r9_log is None else r9_log,
            self.contributors if contributors is None else contributors,
        )

    def test_complete_positive_case(self):
        self.assertEqual(self.check(), v.loads((v.HERE / "RESULT.json").read_bytes()))

    def test_omitted_direct_file(self):
        doc = deepcopy(self.document)
        del doc["direct_files"][v.CASCADE_DIR + "/opframe-bases.json"]
        with self.assertRaisesRegex(ValueError, "direct PR211 inventory"):
            self.check(document=doc)

    def test_same_count_direct_file_substitution(self):
        doc = deepcopy(self.document)
        row = doc["direct_files"].pop(v.CASCADE_DIR + "/NOTICE")
        doc["direct_files"][v.CASCADE_DIR + "/UNRELATED-NOTICE"] = row
        with self.assertRaisesRegex(ValueError, "direct PR211 inventory"):
            self.check(document=doc)

    def test_inherited_file_omission(self):
        doc = deepcopy(self.document)
        del doc["inherited_files"][v.PACKED_DIR + "/certificate.json"]
        with self.assertRaisesRegex(ValueError, "inherited PR205 inventory"):
            self.check(document=doc)

    def test_mode_substitution(self):
        doc = deepcopy(self.document)
        doc["direct_files"][v.CASCADE_DIR + "/README.md"]["mode"] = "100755"
        with self.assertRaisesRegex(ValueError, "direct PR211 inventory"):
            self.check(document=doc)

    def test_commit_byte_corruption(self):
        doc = deepcopy(self.document)
        obj = doc["objects"][v.PR211]
        obj["base64"] = base64.b64encode(base64.b64decode(obj["base64"]) + b"\n").decode()
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.check(document=doc)

    def test_missing_parent_commit(self):
        doc = deepcopy(self.document)
        del doc["objects"][v.PR205]
        with self.assertRaisesRegex(ValueError, "missing Git object"):
            self.check(document=doc)

    def test_missing_retained_tree(self):
        doc = deepcopy(self.document)
        proof = v.Proof(doc)
        _, oid = proof.resolve(v.PR210, "research/coordinated-crossover-pr200/search")
        del doc["objects"][oid]
        with self.assertRaisesRegex(ValueError, "missing Git object"):
            self.check(document=doc)

    def test_certificate_blob_corruption(self):
        doc = deepcopy(self.document)
        proof = v.Proof(doc)
        _, oid = proof.resolve(v.PR211, v.CASCADE_DIR + "/certificate.json")
        doc["objects"][oid]["base64"] = base64.b64encode(b"{}").decode()
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.check(document=doc)

    def test_archive_omits_retaining_parent(self):
        archive = deepcopy(self.archive)
        archive["parents"].remove(v.PR210)
        with self.assertRaisesRegex(ValueError, "archive receipt"):
            self.check(archive=archive)

    def test_next100_review_head_substitution(self):
        reviews = deepcopy(self.reviews)
        reviews["217"]["head"] = v.PR211
        with self.assertRaisesRegex(ValueError, "different head"):
            self.check(reviews=reviews)

    def test_round9_ledger_source_file_omission(self):
        ledger = deepcopy(self.r9_ledger)
        prs = ledger["prs"]
        row = next(r for r in (prs.values() if isinstance(prs, dict) else prs) if r.get("number") == 211)
        row["source_files"].pop()
        with self.assertRaisesRegex(ValueError, "source_files mismatch"):
            self.check(r9_ledger=ledger)

    def test_round9_log_section_mismatch(self):
        log = deepcopy(self.r9_log)
        log["fresh"]["physical"]["W"] += 1
        with self.assertRaisesRegex(ValueError, "Round-9 replay log differs"):
            self.check(r9_log=log)

    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            v.loads('{"direct_files":{},"direct_files":{}}')

    def test_duplicate_frame_operation_index(self):
        bases = [list(self.bases[0]), list(self.bases[0])] + self.bases[2:]
        with self.assertRaisesRegex(ValueError, "duplicate operation index"):
            v.check_accounting(self.c205, self.c211, self.r9_log, bases, self.source_meta)

    def test_terminal_sink_delta_tampering(self):
        c211 = deepcopy(self.c211)
        r9_log = deepcopy(self.r9_log)
        c211["admitted"]["terminal_child_delta"]["3"] = -99
        r9_log["fresh"]["admitted"]["terminal_child_delta"]["3"] = -99
        with self.assertRaisesRegex(ValueError, "terminal sink child-histogram delta"):
            v.check_accounting(self.c205, c211, r9_log, self.bases, self.source_meta)

    def test_mass_preserving_wrong_unpacked_profile(self):
        c211 = deepcopy(self.c211)
        r9_log = deepcopy(self.r9_log)
        # -6*H1 + 3*H2 preserves rank mass and divisibility by 3, but changes physical internal decomposition.
        for target in (c211, r9_log["fresh"]):
            target["admitted"]["profile"]["child_histogram"]["1"] -= 6
            target["admitted"]["profile"]["child_histogram"]["2"] += 3
            target["arithmetic"]["unpacked_profile"]["child_multiplicities"]["1"] -= 6
            target["arithmetic"]["unpacked_profile"]["child_multiplicities"]["2"] += 3
        with self.assertRaisesRegex(ValueError, "physical internal/target decomposition"):
            v.check_accounting(self.c205, c211, r9_log, self.bases, self.source_meta)

    def test_banked_delta_desynchronization(self):
        c211 = deepcopy(self.c211)
        r9_log = deepcopy(self.r9_log)
        for target in (c211, r9_log["fresh"]):
            target["physical"]["child_histogram"]["1"] -= 6
            target["physical"]["child_histogram"]["2"] += 3
        with self.assertRaisesRegex(ValueError, "3-copy bank histogram projection"):
            v.check_accounting(self.c205, c211, r9_log, self.bases, self.source_meta)

    def test_missing_contributors_attribution(self):
        with self.assertRaisesRegex(ValueError, "CONTRIBUTORS.md missing PR211 attribution"):
            self.check(contributors="No PR211 attribution present")


if __name__ == "__main__":
    unittest.main(verbosity=2)
