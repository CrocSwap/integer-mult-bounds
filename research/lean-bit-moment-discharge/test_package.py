"""Failure controls for source binding and the two explicitly distinct replay modes.

No Lean execution is inferred from these standard-library tests.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import copy
from fractions import Fraction as Q
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import certificate
import finite
import verify


def writable_copy(root):
    """Fault controls mutate their temporary copy, including from read-only exports."""
    shutil.copytree(HERE, root, copy_function=shutil.copyfile)
    root.chmod(0o755)
    for path in root.rglob("*"):
        if path.is_dir():
            path.chmod(0o755)


class Controls(unittest.TestCase):
    def test_each_pinned_source(self):
        pins = verify.check_sources()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            writable_copy(root)
            for name in pins["files"]:
                with self.subTest(source=name):
                    path = root / name
                    old = path.read_bytes()
                    path.write_bytes(old + b"\n")
                    with self.assertRaisesRegex(ValueError, "source bytes changed"):
                        verify.check_sources(root)
                    path.write_bytes(old)
            verify.check_sources(root)

    def test_proof_escape_even_with_rebound_hash(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            writable_copy(root)
            path = root / "lean/StoppedRecurrence.lean"
            old = path.read_text()
            pins = verify.read(root / "PROOF-SOURCES.json")
            for escape in ("axiom injected : False", "example : False := by sorry",
                           "example : False := by admit"):
                with self.subTest(escape=escape):
                    path.write_text(old + "\n" + escape + "\n")
                    pins["files"]["lean/StoppedRecurrence.lean"] = hashlib.sha256(path.read_bytes()).hexdigest()
                    (root / "PROOF-SOURCES.json").write_text(json.dumps(pins))
                    with self.assertRaisesRegex(ValueError, "unapproved proof escape"):
                        verify.check_sources(root)

    def test_axiom_report_coverage_and_trust(self):
        targets = verify.check_sources()["axiom_targets"]
        lines = ["'" + name + "' depends on axioms: [propext, Classical.choice, Quot.sound]"
                 for name in targets]
        good = "\n".join(lines)
        self.assertEqual(set(verify.parse_axioms(good, targets)), set(targets))
        for bad in ("\n".join(lines[:-1]), good + "\n" + lines[0],
                    good.replace("Quot.sound", "sorryAx", 1),
                    good.replace("Quot.sound", "untrustedAxiom", 1),
                    good + "\n'extra' depends on axioms: []"):
            with self.subTest(report=bad[-100:]):
                with self.assertRaises(ValueError):
                    verify.parse_axioms(bad, targets)

    def test_strict_receipt_types(self):
        self.assertNotEqual(verify.encoded({"n": 1}), verify.encoded({"n": True}))
        self.assertNotEqual(verify.encoded({"n": 1}), verify.encoded({"n": 1.0}))
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.json"
            for raw in ('{"n": 1, "n": 1}', '{"n": NaN}', '{"n": Infinity}'):
                path.write_text(raw)
                with self.assertRaises(ValueError):
                    verify.read(path)

    def test_corrupt_dyadic_certificates(self):
        original = verify.read(HERE / "DYADIC.json")
        counts = certificate.profile()
        mutations = {
            "small_square": lambda d: d["rows"][0]["upper_numerators"].__setitem__(0, 124999999999),
            "negative_square": lambda d: d["rows"][0]["upper_numerators"].__setitem__(0, -125000000000),
            "short_chain": lambda d: d["rows"][0]["upper_numerators"].pop(),
            "reversed_chain": lambda d: d["rows"][0]["upper_numerators"].reverse(),
            "omitted_rank": lambda d: d["rows"].pop(),
            "wrong_count": lambda d: d["rows"][0].__setitem__("count", 381025),
            "upward_exponent": lambda d: d.__setitem__("numerator", 130850),
            "float_grid": lambda d: d.__setitem__("grid", float(10**12)),
            "boolean_bound": lambda d: d["rows"][0]["upper_numerators"].__setitem__(0, True),
            "boolean_rank": lambda d: d["rows"][0].__setitem__("rank", True),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                data = copy.deepcopy(original)
                mutate(data)
                with self.assertRaises(ValueError):
                    certificate.check(data, counts)

    def test_proposal_domain_and_unit_endpoint(self):
        for x, p, k, d in [(Q(0), 1, 3, 100), (Q(2), 1, 3, 100),
                           (Q(1, 2), 8, 3, 100), (Q(1, 2), -1, 3, 100),
                           (Q(1, 2), 1, 0, 100), (Q(1, 2), 1, 3, 0)]:
            with self.subTest(parameters=(x,p,k,d)):
                with self.assertRaises(ValueError):
                    certificate.propose_chain(x,p,k,d)
        self.assertEqual(certificate.propose_chain(Q(1, 2), 0, 3, 100), [100]*3)

    def test_generated_lean_binding_and_fallback(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            writable_copy(root)
            path = root / "lean/SelectedMoment.lean"
            old = path.read_text()
            path.write_text(old.replace("15735950448", "15735950449"))
            with self.assertRaisesRegex(ValueError, "Lean/certificate semantic binding"):
                finite.replay(root)
            path.write_text(old)
            path = root / "lean/Selected.lean"
            path.write_text(path.read_text().replace("118606528512 /", "0 /"))
            with self.assertRaisesRegex(ValueError, "formal scalar binding"):
                finite.replay(root)

    def test_lean_profile_semantic_binding(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            writable_copy(root)
            path = root / "lean/Selected.lean"
            path.write_text(path.read_text().replace("381024, 400416", "381025, 400416"))
            with self.assertRaisesRegex(ValueError, "formal profile binding"):
                finite.replay(root)

    def test_receipt_drift_is_rejected_end_to_end(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            writable_copy(root)
            path = root / "FINITE.json"
            value = verify.read(path)
            value["calibration"]["cases"] -= 1
            path.write_text(json.dumps(value))
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(root / "verify.py")],
                                    cwd=temporary, capture_output=True, text=True, timeout=90)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("finite receipt differs", result.stderr)

    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "keep.json"
            out.write_bytes(b"preserve existing evidence\n")
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                     "--out", str(out)], cwd=temporary, capture_output=True,
                                    text=True, timeout=15)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("output already exists", result.stderr)
            self.assertEqual(out.read_bytes(), b"preserve existing evidence\n")

    def test_kernel_mode_requires_explicit_environment(self):
        for arguments in (["--lake", "/missing/lake"], ["--fetch-cache"],
                          ["--lake", "/missing/lake", "--work-dir", "/missing/work"]):
            with self.subTest(arguments=arguments):
                result = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                         *arguments], capture_output=True, text=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("PASS_", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
