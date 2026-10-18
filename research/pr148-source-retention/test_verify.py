#!/usr/bin/env python3
"""Positive source proof and deliberate false-retention controls. Apache-2.0."""
import base64
import copy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as v


class RetentionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proof = json.loads(v.read_file(v.HERE, "TREE-PROOF.json"))
        cls.coverage = json.loads(v.read_file(v.HERE, "COVERAGE.json"))
        manifest = json.loads(v.read_file(v.HERE, "VERIFY.json"))
        cls.repo = {p: v.read_file(v.ROOT, p) for p in manifest["inputs"]}
        names = {r["storage"]["path"] for r in cls.coverage["rows"] if r["storage"]["kind"] == "recovered"}
        cls.package = {p: v.read_file(v.HERE, p) for p in names | {"original/LICENSE", "original/NOTICE", "VERIFY.json"}}
        cls.result = json.loads(v.read_file(v.HERE, "RESULT.json"))

    def check(self, proof=None, coverage=None, repo=None, package=None):
        return v.verify_data(self.proof if proof is None else proof,
                             self.coverage if coverage is None else coverage,
                             (self.repo if repo is None else repo).__getitem__,
                             (self.package if package is None else package).__getitem__)

    def test_positive_complete_receipt(self):
        self.assertEqual(self.check(), self.result)

    def test_omitted_duplicate_and_foreign_paths(self):
        for mutation in ("omit", "duplicate", "foreign"):
            with self.subTest(mutation=mutation):
                coverage = copy.deepcopy(self.coverage)
                if mutation == "omit":
                    coverage["rows"].pop()
                elif mutation == "duplicate":
                    coverage["rows"][-1] = copy.deepcopy(coverage["rows"][0])
                else:
                    coverage["rows"][-1]["path"] = "not-in-the-pr.txt"
                with self.assertRaisesRegex(ValueError, "coverage"):
                    self.check(coverage=coverage)

    def test_false_blob_mode_and_author_delta(self):
        for key, value in (("blob", "0" * 40), ("mode", "100755"), ("direct_change", True)):
            with self.subTest(field=key):
                coverage = copy.deepcopy(self.coverage)
                coverage["rows"][0][key] = value
                with self.assertRaisesRegex(ValueError, "source entry|author-delta"):
                    self.check(coverage=coverage)

    def test_wrong_endpoints(self):
        for field in ("head_commit", "main_commit", "comparison_base", "direct_base"):
            with self.subTest(field=field):
                coverage = copy.deepcopy(self.coverage)
                coverage[field] = "0" * 40
                with self.assertRaisesRegex(ValueError, "pinned endpoint"):
                    self.check(coverage=coverage)

    def test_missing_and_damaged_authenticated_objects(self):
        for mutation in ("missing-head", "damaged-commit", "missing-tree"):
            with self.subTest(mutation=mutation):
                proof = copy.deepcopy(self.proof)
                if mutation == "missing-head":
                    del proof["objects"][v.HEAD]
                elif mutation == "damaged-commit":
                    entry = proof["objects"][v.HEAD]
                    entry["base64"] = base64.b64encode(base64.b64decode(entry["base64"]) + b"x").decode()
                else:
                    del proof["objects"][v.Proof(proof).commit(v.HEAD)[0]]
                with self.assertRaisesRegex(ValueError, "Git object"):
                    self.check(proof=proof)

    def test_false_locations_and_path_escape(self):
        mutations = (("main-file", "path", "../README.md"),
                     ("main-file", "path", "LICENSE"),
                     ("pr181-archive", "member", "README.md"),
                     ("recovered", "path", "original/NOTICE"))
        for kind, key, value in mutations:
            with self.subTest(kind=kind, value=value):
                coverage = copy.deepcopy(self.coverage)
                row = next(r for r in coverage["rows"] if r["storage"]["kind"] == kind)
                row["storage"][key] = value
                with self.assertRaises(ValueError):
                    self.check(coverage=coverage)

    def test_changed_live_and_recovered_bytes(self):
        row = next(r for r in self.coverage["rows"] if r["storage"]["kind"] == "main-file")
        main_name = row["storage"]["path"]
        mutations = (("repo", main_name), ("repo", v.ARCHIVE + "/baseline-pr181.part01"),
                     ("repo", v.HISTORY), ("package", "original/README.md"),
                     ("package", "original/LICENSE"), ("package", "original/NOTICE"))
        for where, name in mutations:
            with self.subTest(where=where, name=name):
                data = dict(self.repo if where == "repo" else self.package)
                data[name] += b"changed"
                with self.assertRaises(ValueError):
                    self.check(**{where: data})

    def test_missing_recovered_original(self):
        package = dict(self.package)
        del package["original/README.md"]
        with self.assertRaises(KeyError):
            self.check(package=package)

    def test_incomplete_replay_invalidation(self):
        package = dict(self.package)
        manifest = json.loads(package["VERIFY.json"])
        manifest["inputs"].pop()
        package["VERIFY.json"] = json.dumps(manifest).encode()
        with self.assertRaisesRegex(ValueError, "CI invalidation"):
            self.check(package=package)


if __name__ == "__main__":
    unittest.main(verbosity=2)
