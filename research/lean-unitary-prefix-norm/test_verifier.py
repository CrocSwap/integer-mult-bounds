#!/usr/bin/env python3
"""Tests of proof-source and axiom guards; these do not replace the Lean build.

Gareth Davidson, with OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify


class GuardTests(unittest.TestCase):
    def test_live_sources(self):
        result = verify.source_check()
        self.assertEqual((result["core_theorems"], result["example_theorems"]), (13, 20))

    def test_nested_comments_and_forbidden_proofs(self):
        text = "/- outer /- axiom hidden : False -/ sorry -/\n-- admit\ntheorem ok : True := by trivial"
        verify.scan(text, "control")
        for token in ("axiom fabricated : False", "theorem bad : False := by sorry",
                      "set_option debug.skipKernelTC true"):
            with self.assertRaises(verify.VerificationError):
                verify.scan(text + "\n" + token, "control")
        with self.assertRaises(verify.VerificationError):
            verify.strip_comments("/- unclosed")

    def test_axiom_whitelist_and_complete_coverage(self):
        valid = "'A' depends on axioms: [propext, Quot.sound]\n'B' does not depend on any axioms\n"
        self.assertEqual(verify.parse_axioms(valid, ["A", "B"]),
                         {"A": ["Quot.sound", "propext"], "B": []})
        for text in (valid.replace("Quot.sound", "sorryAx"), valid.splitlines()[0],
                     valid + "'A' does not depend on any axioms\n"):
            with self.assertRaises(verify.VerificationError):
                verify.parse_axioms(text, ["A", "B"])

    def test_exact_version_with_cold_setup_output(self):
        version = "Lean (version 4.21.0, x86_64-unknown-linux-gnu, commit 6741444a63ee, Release)"
        cold = "info: mathlib: cloning pinned dependency\n" + version + "\n"
        self.assertEqual(verify.parse_lean_version(cold), version)
        for bad in (cold.replace("4.21.0,", "4.21.1,"),
                    cold.replace("4.21.0,", "4.21.0-rc1,"),
                    cold + version + "\n", "info: download started\n"):
            with self.assertRaises(verify.VerificationError):
                verify.parse_lean_version(bad)

    def test_unrecognized_workspace_is_preserved(self):
        with tempfile.TemporaryDirectory() as path:
            root = Path(path)
            important = root / "user-file"
            important.write_text("keep")
            with self.assertRaises(verify.VerificationError):
                verify.prepare(root)
            self.assertEqual(important.read_text(), "keep")

    def test_readonly_relocation_and_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix="norm proof source guard ") as path:
            root = Path(path)
            package = root / "research" / verify.HERE.name
            shutil.copytree(verify.HERE, package, ignore=shutil.ignore_patterns("__pycache__", ".lake"))
            for name in verify.INPUTS:
                dest = root / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(verify.ROOT / name, dest)
            files = [f for f in root.rglob("*") if f.is_file()]
            before = {str(f.relative_to(root)): verify.sha(f.read_bytes()) for f in files}
            try:
                for f in files:
                    f.chmod(0o444)
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py"),
                                         "--source-only"], cwd="/tmp", capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("not_a_Lean_proof_check", result.stdout)
                self.assertEqual(before, {str(f.relative_to(root)): verify.sha(f.read_bytes())
                                          for f in root.rglob("*") if f.is_file()})
            finally:
                for f in files:
                    f.chmod(0o644)
            source = root / verify.SOURCE
            source.write_text(source.read_text() + "\n-- source corruption control\n")
            with self.assertRaisesRegex(verify.VerificationError, "source hash"):
                verify.source_check(root, package)

    def test_missing_axiom_request(self):
        with tempfile.TemporaryDirectory() as path:
            package = Path(path) / "package"
            shutil.copytree(verify.HERE, package, ignore=shutil.ignore_patterns("__pycache__", ".lake"))
            p = package / "PrintAxioms.lean"
            p.write_text("\n".join(p.read_text().splitlines()[:-1]) + "\n")
            with self.assertRaisesRegex(verify.VerificationError, "complete axiom audit requests"):
                verify.source_check(verify.ROOT, package)


if __name__ == "__main__":
    unittest.main()
