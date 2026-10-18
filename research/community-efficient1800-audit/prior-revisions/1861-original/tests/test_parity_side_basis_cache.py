"""Focused controls for the parity-side basis/contains tooling package."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research/parity-side-basis-cache"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import binary_phase_frames as bpf  # noqa: E402


def load_baseline():
    spec = importlib.util.spec_from_file_location("parity_bpf_baseline", PACKAGE / "baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ParitySideBasisCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_baseline()

    def test_baseline_bytes_match_base_commit(self):
        original = subprocess.check_output(
            ["git", "show", "0b1cccf86e2f5132ed286a26ef0a681a495740ea:scripts/binary_phase_frames.py"],
            cwd=ROOT,
        )
        self.assertEqual((PACKAGE / "baseline.py").read_bytes(), original)
        self.assertEqual(
            sha256(original).hexdigest(),
            "4148cfa313cf050ed25296e8db36d35871520b8318fd086c7d1facf0c6af67d7",
        )

    def test_basis_contains_classify_agree(self):
        rows = (0b1011, 0b1100, 0b0010, 0)
        self.assertEqual(self.baseline.basis(rows), bpf.basis(rows))
        for v in range(16):
            self.assertEqual(self.baseline.contains(rows, v), bpf.contains(rows, v))
        self.assertEqual(self.baseline.classify(rows), bpf.classify(rows))

    def test_contains_rejects_negative(self):
        with self.assertRaises(AssertionError):
            bpf.contains((1,), -1)

    def test_certificate_pins_only_binary_phase_frames(self):
        for rel in (
            "certificates/parity-side.json",
            "certificates/disjoint-tensor-compression.json",
            "certificates/dyadic-central-factor.json",
        ):
            base = json.loads(
                subprocess.check_output(
                    ["git", "show", f"0b1cccf86e2f5132ed286a26ef0a681a495740ea:{rel}"],
                    cwd=ROOT,
                )
            )
            live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
            live["source_sha256"]["scripts/binary_phase_frames.py"] = base["source_sha256"][
                "scripts/binary_phase_frames.py"
            ]
            self.assertEqual(live, base)

    def test_package_verify_entrypoint(self):
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(PACKAGE / "verify.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("PASS_PARITY_SIDE_BASIS_CACHE", proc.stdout)


if __name__ == "__main__":
    unittest.main()
