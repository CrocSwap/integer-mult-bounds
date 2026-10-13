#!/usr/bin/env python3
"""Isolated-source replay and adversarial package checks; standard library only.

Run: python3 -I -B research/r439-four-block-composition/test_package.py
Copies only declared execution/native inputs and the local verifier into a
temporary repository. Does not modify sources, compile C++, or use the network.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
import contextlib
import copy
import gzip
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="r439-package-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.here = self.root / HERE.relative_to(ROOT)
        self.here.mkdir(parents=True)
        self.pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
        for name in ("verify.py", "check_blocks.py", "SOURCES.json", "CERTIFICATE.json"):
            shutil.copyfile(HERE / name, self.here / name)
        for name in self.pins["execution_inputs"] + self.pins["native_inputs"]:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.verify = module(self.here / "verify.py", "isolated_composition_verifier")
        self.blocks = module(self.here / "check_blocks.py", "isolated_composition_blocks")

    def write_json(self, path, value):
        path.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def test_declared_inputs_suffice_and_certificate_corruption_is_rejected(self):
        # The temporary root has no Git metadata, context files, search code,
        # predecessor native harness, or predecessor SOURCES manifests.
        output = self.root / "positive"
        output.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            report = self.verify.run(output, False)
        self.assertEqual(report["subset_cover_edges"], 32)
        self.assertEqual(len(report["subsets"]), 16)
        self.assertEqual(report["native_records"]["replacement"]["adds"], 24233)
        certificate = self.here / "CERTIFICATE.json"
        altered = json.loads(certificate.read_text(encoding="utf-8"))
        altered["subsets"][7]["native_records"]["adds"] -= 1
        self.write_json(certificate, altered)
        output = self.root / "bad-certificate"
        output.mkdir()
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(ValueError, "certificate mismatch"):
                self.verify.run(output, False)

    def test_every_consumed_source_is_hash_checked(self):
        self.verify.sources()
        for name in self.pins["execution_inputs"] + self.pins["native_inputs"]:
            with self.subTest(source=name):
                path = self.root / name
                original = path.read_bytes()
                try:
                    path.write_bytes(original + b"\ncorrupted source\n")
                    with self.assertRaisesRegex(ValueError, "source hash mismatch"):
                        self.verify.sources()
                finally:
                    path.write_bytes(original)

    def test_execution_closure_cannot_omit_a_witness(self):
        altered = copy.deepcopy(self.pins)
        altered["execution_inputs"].pop()
        self.write_json(self.here / "SOURCES.json", altered)
        with self.assertRaisesRegex(ValueError, "execution closure changed"):
            self.verify.sources()

    def test_rehashed_gate_corruption_still_fails_mathematics(self):
        word = json.loads(gzip.decompress((self.root / self.verify.WORD).read_bytes()))
        for frame, _, _, _, _, name in self.blocks.SPECS:
            with self.subTest(frame=frame):
                path = self.root / name
                original = path.read_bytes()
                altered = json.loads(original)
                if frame == 507:
                    altered["replacement"][0].reverse()
                else:
                    gates = (altered["gates"] if frame == 508 else
                             altered["factors"][0]["program"] if frame == 519 else
                             altered["candidate_gates"])
                    gate = gates[0]
                    gate[1], gate[2][0] = gate[2][0], gate[1]
                pins = copy.deepcopy(self.pins)
                try:
                    self.write_json(path, altered)
                    pins["files"][name]["sha256"] = self.verify.sha(path.read_bytes())
                    self.write_json(self.here / "SOURCES.json", pins)
                    self.verify.sources()
                    witnesses = self.blocks.load_blocks(self.root)
                    with self.assertRaisesRegex(ValueError, "local integer map differs"):
                        self.blocks.verify_blocks(word, witnesses)
                finally:
                    path.write_bytes(original)
                    self.write_json(self.here / "SOURCES.json", self.pins)

    def test_unscoped_combined_gate_change_is_rejected(self):
        word = json.loads(gzip.decompress((self.root / self.verify.WORD).read_bytes()))
        witnesses = self.blocks.load_blocks(self.root)
        combined = self.verify.build(word, witnesses, 15)
        # Touch an unchanged gate before the earliest replacement slice.
        combined["B"][0][0] += 1
        with self.assertRaisesRegex(ValueError, "candidate B differs from independent composition"):
            self.blocks.verify_blocks(word, witnesses, combined["B"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
