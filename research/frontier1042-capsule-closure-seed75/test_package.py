#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
import copy
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify

class FakeMember:
    def __init__(self, name, size=0, mode=0o644, regular=True):
        self.name, self.size, self.mode, self._regular = name, size, mode, regular
    def isfile(self): return self._regular

class NamespaceControls(unittest.TestCase):
    def test_C1_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "unsafe archive"):
            verify.validate_namespace([FakeMember("../escape")])
    def test_C2_duplicate_member(self):
        with self.assertRaisesRegex(ValueError, "duplicate archive"):
            verify.validate_namespace([FakeMember("a"), FakeMember("a")])

class ClosureControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pins = verify.strict_json((verify.HERE / "PINS.json").read_bytes(), "PINS.json")
        a = verify.ROOT / cls.pins["archive"]["path"]
        cls.names, _, cls.digests, cls.roots = verify.read_capsule(a)
        cls.result = verify.strict_json(cls.roots["RESULT.json"], "RESULT.json")
        cls.stages = verify.strict_json(cls.roots["STAGES.json"], "STAGES.json")
    def validate(self, result=None, stages=None, names=None, digests=None):
        return verify.validate_result(result or self.result, stages or self.stages,
                                      names or self.names, digests or self.digests,
                                      self.pins["stages"])
    def test_C3_nondeclared_member(self):
        result = copy.deepcopy(self.result); result["artifacts"].pop(next(iter(result["artifacts"])))
        with self.assertRaisesRegex(ValueError, "not exact archive closure"): self.validate(result=result)
    def test_C4_mutated_artifact_digest(self):
        digests = dict(self.digests); name = next(iter(self.result["artifacts"])); digests[name] = "0" * 64
        with self.assertRaisesRegex(ValueError, "artifact digest differs"): self.validate(digests=digests)
    def test_C5_nonzero_stage(self):
        stages = copy.deepcopy(self.stages); stages[0]["exit_code"] = 1
        result = copy.deepcopy(self.result); result["stages"] = stages
        with self.assertRaisesRegex(ValueError, "recorded stage failed"): self.validate(result=result, stages=stages)
    def test_C6_promoted_receipt_mismatch(self):
        original = verify.repository_file
        def mismatched_receipt(relative, expected=None):
            data = original(relative, expected)
            return data + b"x" if relative == "research/community-frontier1042-audit/ASSEMBLY.json" else data
        with patch.object(verify, "repository_file", side_effect=mismatched_receipt):
            with self.assertRaisesRegex(ValueError, "promoted receipt differs from capsule"):
                verify.check(self.pins)

class HistoricalSelectedControls(unittest.TestCase):
    def setUp(self):
        self.pins = verify.strict_json((verify.HERE / "PINS.json").read_bytes(), "PINS.json")
        self.expected = verify.strict_json((verify.HERE / "RESULT.json").read_bytes(), "RESULT.json")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.package = self.root / "research" / verify.HERE.name
        self.package.mkdir(parents=True)
        shutil.copyfile(verify.HERE / self.pins["selected_record"]["path"],
                        self.package / self.pins["selected_record"]["path"])
        paths = [self.pins["archive"]["path"], self.pins["integration_record"]["path"]]
        paths.extend("research/community-frontier1042-audit/" + name
                     for name in self.pins["promoted_receipts"])
        selected = verify.strict_json(verify.package_file(self.pins["selected_record"]["path"],
                                                         self.pins["selected_record"]["sha256"]), "selected")
        paths.append(selected["source_manifest"])
        for relative in paths:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(verify.ROOT / relative, target)
        for name, value in (("ROOT", self.root), ("HERE", self.package)):
            patcher = patch.object(verify, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_missing_live_selected_pointer_does_not_affect_history(self):
        self.assertFalse((self.root / "certificates/selected-result.json").exists())
        self.assertEqual(verify.check(self.pins), self.expected)

    def test_advanced_live_selected_pointer_does_not_affect_history(self):
        live = self.root / "certificates/selected-result.json"
        live.parent.mkdir(parents=True)
        live.write_text('{"kappa": "1672660197076918/1000000000000000000"}\n', encoding="utf-8")
        self.assertEqual(verify.check(self.pins), self.expected)

    def test_mutated_frozen_selected_record_is_rejected(self):
        frozen = self.package / self.pins["selected_record"]["path"]
        frozen.write_bytes(frozen.read_bytes() + b"x")
        with self.assertRaisesRegex(ValueError, "package pin differs: SELECTED-RESULT.json"):
            verify.check(self.pins)

if __name__ == "__main__": unittest.main(verbosity=2)
