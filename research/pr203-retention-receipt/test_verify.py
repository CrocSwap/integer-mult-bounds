#!/usr/bin/env python3
"""Corruption, coverage, provenance and mathematical screen controls on the real pinned evidence.

steph4n (@steph4n-gh), with substantial Google Gemini assistance. Apache-2.0.
"""
import base64
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class RetentionControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = v.loads((v.HERE / "SOURCE-PROOF.json").read_bytes())
        (
            cls.archive_92,
            cls.reviews_92,
            cls.archive_next100,
            cls.reviews_next100,
            cls.r9_ledger,
            cls.r9_cases,
            cls.live_fc,
            cls.contributors,
        ) = v.external_inputs()
        proof = v.Proof(cls.document)
        cls.payloads = {
            path: proof.raw(row["blob"], "blob")
            for path, row in cls.document["files"].items()
        }
        _, b187 = proof.resolve(v.PR187, v.PR187_PHYSICAL_PATH, "100644")
        _, b193 = proof.resolve(v.PR193, v.PR193_CERT_PATH, "100644")
        _, bf193 = proof.resolve(v.PR193, v.PR193_BALANCED_FANO_PATH, "100644")
        _, fc193 = proof.resolve(v.PR193, v.FANO_COMPLETION_PATH, "100644")
        cls.raw_187 = proof.raw(b187, "blob")
        cls.raw_193 = proof.raw(b193, "blob")
        cls.raw_bf193 = proof.raw(bf193, "blob")
        cls.raw_fc193 = proof.raw(fc193, "blob")

    def check(self, document=None, archive_92=None, reviews_92=None,
              archive_next100=None, reviews_next100=None, r9_ledger=None,
              r9_cases=None, live_fc=None, contributors=None):
        return v.verify(
            self.document if document is None else document,
            self.archive_92 if archive_92 is None else archive_92,
            self.reviews_92 if reviews_92 is None else reviews_92,
            self.archive_next100 if archive_next100 is None else archive_next100,
            self.reviews_next100 if reviews_next100 is None else reviews_next100,
            self.r9_ledger if r9_ledger is None else r9_ledger,
            self.r9_cases if r9_cases is None else r9_cases,
            self.live_fc if live_fc is None else live_fc,
            self.contributors if contributors is None else contributors,
        )

    def mutate_payload(self, rel_path, new_obj):
        payloads = dict(self.payloads)
        raw = json.dumps(new_obj, sort_keys=True, indent=2).encode("utf-8") + b"\n"
        payloads[v.PKG_DIR + "/" + rel_path] = raw
        src = v.loads(payloads[v.PKG_DIR + "/SOURCE.json"])
        src["files"][rel_path] = hashlib.sha256(raw).hexdigest()
        payloads[v.PKG_DIR + "/SOURCE.json"] = json.dumps(src, sort_keys=True, indent=2).encode("utf-8") + b"\n"
        return payloads

    def test_complete_positive_case(self):
        self.assertEqual(self.check(), v.loads((v.HERE / "RESULT.json").read_bytes()))

    def test_omitted_package_file(self):
        doc = deepcopy(self.document)
        del doc["files"][v.PKG_DIR + "/ceiling-certificate.json"]
        with self.assertRaisesRegex(ValueError, "29-file inventory"):
            self.check(document=doc)

    def test_same_count_file_substitution(self):
        doc = deepcopy(self.document)
        row = doc["files"].pop(v.PKG_DIR + "/NOTICE")
        doc["files"][v.PKG_DIR + "/UNRELATED-NOTICE"] = row
        with self.assertRaisesRegex(ValueError, "29-file inventory"):
            self.check(document=doc)

    def test_mode_substitution(self):
        doc = deepcopy(self.document)
        doc["files"][v.PKG_DIR + "/README.md"]["mode"] = "100755"
        with self.assertRaisesRegex(ValueError, "29-file inventory"):
            self.check(document=doc)

    def test_commit_byte_corruption(self):
        doc = deepcopy(self.document)
        obj = doc["objects"][v.PR203]
        obj["base64"] = base64.b64encode(base64.b64decode(obj["base64"]) + b"\n").decode()
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.check(document=doc)

    def test_missing_merge_base_commit(self):
        doc = deepcopy(self.document)
        del doc["objects"][v.MERGE_BASE]
        with self.assertRaisesRegex(ValueError, "missing Git object"):
            self.check(document=doc)

    def test_missing_upstream_pr187_tree(self):
        doc = deepcopy(self.document)
        proof = v.Proof(doc)
        _, oid = proof.resolve(v.PR187, "research/source-assisted-bit-bootstrap")
        del doc["objects"][oid]
        with self.assertRaisesRegex(ValueError, "missing Git object"):
            self.check(document=doc)

    def test_certificate_blob_corruption(self):
        doc = deepcopy(self.document)
        proof = v.Proof(doc)
        _, oid = proof.resolve(v.PR203, v.PKG_DIR + "/ceiling-certificate.json")
        doc["objects"][oid]["base64"] = base64.b64encode(b"{}").decode()
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            self.check(document=doc)

    def test_reconciliation92_archive_omits_pr187(self):
        archive_92 = deepcopy(self.archive_92)
        archive_92["parents"].remove(v.PR187)
        with self.assertRaisesRegex(ValueError, "reconciliation92 archive receipt"):
            self.check(archive_92=archive_92)

    def test_next100_archive_omits_pr193(self):
        archive_next100 = deepcopy(self.archive_next100)
        archive_next100["parents"].remove(v.PR193)
        with self.assertRaisesRegex(ValueError, "next100 archive receipt"):
            self.check(archive_next100=archive_next100)

    def test_next100_review_head_substitution(self):
        reviews = deepcopy(self.reviews_next100)
        reviews["204"]["head"] = v.PR203
        with self.assertRaisesRegex(ValueError, "different head"):
            self.check(reviews_next100=reviews)

    def test_round9_ledger_source_file_omission(self):
        ledger = deepcopy(self.r9_ledger)
        prs = ledger["prs"]
        row = next(r for r in (prs.values() if isinstance(prs, dict) else prs) if r.get("number") == 203)
        row["source_files"].pop()
        with self.assertRaisesRegex(ValueError, "source_files mismatch"):
            self.check(r9_ledger=ledger)

    def test_round9_log_case_mismatch(self):
        cases = list(self.r9_cases)
        cases[-1] = (cases[-1][0], cases[-1][1] + 1)
        with self.assertRaisesRegex(ValueError, "Round-9 replay log 16 Fano cases"):
            self.check(r9_cases=cases)

    def test_duplicate_json_key(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON key"):
            v.loads('{"files":{},"files":{}}')

    def test_source_manifest_digest_tampering(self):
        payloads = dict(self.payloads)
        src = v.loads(payloads[v.PKG_DIR + "/SOURCE.json"])
        src["files"]["audit.py"] = "0" * 64
        payloads[v.PKG_DIR + "/SOURCE.json"] = json.dumps(src).encode("utf-8")
        with self.assertRaisesRegex(ValueError, "27-file SHA256 manifest mismatch"):
            v.check_accounting(payloads, self.raw_187, self.raw_193,
                               self.raw_bf193, self.raw_fc193, self.live_fc, self.r9_cases)

    def test_upstream_pr187_profile_tampering(self):
        in_187 = v.loads(self.payloads[v.PKG_DIR + "/inputs/bit-pr187.json"])
        in_187["profile"]["loss"] -= 1
        payloads = self.mutate_payload("inputs/bit-pr187.json", in_187)
        with self.assertRaisesRegex(ValueError, "bit-pr187 paired-cube loss mismatch"):
            v.check_accounting(payloads, self.raw_187, self.raw_193,
                               self.raw_bf193, self.raw_fc193, self.live_fc, self.r9_cases)

    def test_ceiling_certificate_tampering(self):
        cert = v.loads(self.payloads[v.PKG_DIR + "/ceiling-certificate.json"])
        cert["odd_cube_extension"]["strict_global_a_ceiling"] = "5165/1000000"
        payloads = self.mutate_payload("ceiling-certificate.json", cert)
        with self.assertRaisesRegex(ValueError, "recomputed ceiling-certificate.json differs"):
            v.check_accounting(payloads, self.raw_187, self.raw_193,
                               self.raw_bf193, self.raw_fc193, self.live_fc, self.r9_cases)

    def test_center_basis_certificate_tampering(self):
        cert = v.loads(self.payloads[v.PKG_DIR + "/center-basis-certificate.json"])
        cert["finite_sweep"]["nonzero_vectors_checked"] -= 1
        payloads = self.mutate_payload("center-basis-certificate.json", cert)
        with self.assertRaisesRegex(ValueError, "recomputed center-basis-certificate.json differs"):
            v.check_accounting(payloads, self.raw_187, self.raw_193,
                               self.raw_bf193, self.raw_fc193, self.live_fc, self.r9_cases)

    def test_fano_reuse_certificate_tampering(self):
        cert = v.loads(self.payloads[v.PKG_DIR + "/fano-reuse-certificate.json"])
        cert["cases"][0]["scalar_exhaustion"]["exists"] = True
        payloads = self.mutate_payload("fano-reuse-certificate.json", cert)
        with self.assertRaisesRegex(ValueError, "scalar_exhaustion negative status mismatch"):
            v.check_accounting(payloads, self.raw_187, self.raw_193,
                               self.raw_bf193, self.raw_fc193, self.live_fc, self.r9_cases)

    def test_vector_receipt_status_tampering(self):
        rows = v.loads(self.payloads[v.PKG_DIR + "/discovery/receipts/vector-k3.json"])
        for r in rows:
            r["status"] = "unsat"
        payloads = self.mutate_payload("discovery/receipts/vector-k3.json", rows)
        with self.assertRaisesRegex(ValueError, "vector receipt unsat/unknown counts mismatch"):
            v.check_accounting(payloads, self.raw_187, self.raw_193,
                               self.raw_bf193, self.raw_fc193, self.live_fc, self.r9_cases)

    def test_missing_contributors_attribution(self):
        with self.assertRaisesRegex(ValueError, "CONTRIBUTORS.md missing PR203 attribution"):
            self.check(contributors="No PR203 attribution present")


if __name__ == "__main__":
    unittest.main(verbosity=2)
