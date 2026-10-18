#!/usr/bin/env python3
"""Behavioral and artifact controls for the zero-retention error certificate.

Nick Petalas. Apache-2.0.
"""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("defects", HERE / "verify.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)
TOY = [
    ["clear", "Z0", "current"],
    ["add", "Z0", "X0", "1"],
    ["line", "Z0", 0, -1],
    ["map", "Z0", 1, 0, False],
    ["clear", "W0", "current"],
    ["add", "W0", "Z0", "-1/4"],
]


def literal_pair(word, tolerances):
    """Execute a small signed two-dimensional model, with noncommuting isometries."""
    state = {name: (Q(1), Q(0)) for name in CHECK.INPUTS}
    cuts = []
    for event in word:  # Six events in the toy fixture.
        op, dest = event[:2]
        if op == "clear":
            value = (Q(0), Q(0))
        elif op == "add":
            c = Q(event[3])
            value = tuple(
                a + c * b for a, b in zip(state[dest], state[event[2]], strict=True)
            )
        elif op == "line":
            a, b = state[dest]
            value = (b, -a)
        else:  # Reflection does not commute with the preceding rotation.
            a, b = state[dest]
            value = (b, a)
        fault = tolerances.get(op, Q(0))
        state[dest] = (value[0] + fault, value[1])
        cuts.append(state[dest])
    return state, cuts


class MathematicalControls(unittest.TestCase):
    """Exercise the certificate on literal expected behaviors, not its constants."""

    def test_fractional_adjoint_and_all_channels(self):
        cuts, loads, _ = CHECK.forward(TOY)
        expected = (Q(1, 4), Q(1), Q(9, 4), Q(5, 4), Q(1, 4), Q(1, 4))
        self.assertEqual(cuts[-1][2], expected)
        self.assertEqual(CHECK.reverse_cut(TOY, loads, 5, "W0"), expected)
        exact, exact_cuts = literal_pair(TOY, {})
        noisy, noisy_cuts = literal_pair(TOY, {"add": Q(2), "line": Q(3), "map": Q(5)})
        self.assertEqual(exact["W0"], (Q(1, 4), Q(0)))
        self.assertEqual(noisy["W0"], (Q(3, 2), Q(-3, 4)))
        for (_, _, row), ideal, approximate in zip(
            cuts, exact_cuts, noisy_cuts, strict=True
        ):
            bound = row[3] * 2 + row[4] * 3 + row[5] * 5
            error_squared = sum(
                (a - b) ** 2 for a, b in zip(ideal, approximate, strict=True)
            )
            self.assertLessEqual(error_squared, bound**2)
        self.assertEqual(noisy["X0"], (Q(1), Q(0)))

    def test_clear_hides_a_real_transient_not_an_all_cut_error(self):
        word = [*TOY[:3], ["clear", "Z0", "identity"]]
        cuts, _, _ = CHECK.forward(word)
        _, actual = literal_pair(word, {"line": Q(1)})
        _, ideal = literal_pair(word, {})
        self.assertEqual(actual[2], (Q(1), Q(-1)))
        self.assertEqual(ideal[2], (Q(0), Q(-1)))
        self.assertEqual(cuts[2][2][4], Q(1))
        self.assertEqual(cuts[-1][2], (Q(0),) * 6)
        self.assertEqual(actual[-1], (Q(0), Q(0)))

    def test_dirty_reads_borrowed_writes_and_uncleared_scratch_reject(self):
        bad_words = [
            [["add", "Z0", "X0", "1"]],
            [["clear", "X0", "current"]],
            [["clear", "Z0", "current"], ["add", "Z0", "F0", "1"]],
            [
                ["begin", "private", 8],
                ["clear", "F0", "wide"],
                ["add", "F0", "X0", "1"],
                ["end", "private", 8],
            ],
            [["map"]],
            [["begin", "private", 8], ["end", "private", 16]],
            [["begin", "private", 8], ["end", "private", 8.0]],
            [
                ["begin", "private", 8],
                *[["clear", f"F{i}", "wide"] for i in range(8)],
                ["clear", "G0", "wide"],
            ],
            [*TOY[:2], ["line", "Z0", 0, True]],
            [*TOY[:2], ["map", "Z0", 1, 0, 1]],
            [TOY[0], ["add", "Z0", "X0", "1/3"]],
        ]
        for word in bad_words:
            with self.subTest(word=word), self.assertRaises(ValueError):
                CHECK.forward(word)
        valid = [
            ["begin", "private", 8],
            ["clear", "F0", "wide"],
            ["add", "F0", "X0", "1"],
            ["clear", "F0", "identity"],
            ["end", "private", 8],
        ]
        self.assertEqual(CHECK.forward(valid)[0][-1][2], (Q(0),) * 6)

    def test_capacity_is_enforced_before_iteration(self):
        with self.assertRaisesRegex(ValueError, "event capacity"):
            CHECK.forward([TOY[0]] * 3824)

    def test_wrong_reverse_load_cannot_corroborate_forward(self):
        _, loads, _ = CHECK.forward(TOY)
        loads[2] = (Q(0), Q(0))
        self.assertEqual(CHECK.reverse_cut(TOY, loads, 5, "W0")[1:3], (Q(3, 4), Q(2)))
        self.assertNotEqual(
            CHECK.reverse_cut(TOY, loads, 5, "W0"), CHECK.forward(TOY)[0][-1][2]
        )

    def test_guard_and_feedback_boundary(self):
        # Independent exact endpoint arithmetic for the inequality in PROOF.md.
        for b in (0, 1, 8, 64, 1024):
            u = Q(1, 2 ** (b + 22))
            error = u * 2919388 / (1 - u * 199144)
            self.assertLess(error, Q(1, 2**b))
        u = Q(1, 2**21)
        self.assertGreater(u * 2919388 / (1 - u * 199144), Q(1))
        self.assertEqual(Q(1, 199144) * 199144, Q(1))


class ArtifactControls(unittest.TestCase):
    """Invoke the actual optimized CLI from a Git-free copied package."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.copy = Path(self.temporary.name) / "package"
        shutil.copytree(HERE, self.copy, ignore=shutil.ignore_patterns("__pycache__"))

    def run_cli(self, *args):
        return subprocess.run(
            [
                sys.executable,
                "-Werror",
                "-I",
                "-O",
                "-B",
                str(self.copy / "verify.py"),
                *args,
            ],
            cwd=self.temporary.name,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )

    def test_read_only_relocated_replay(self):
        before = {
            p.relative_to(self.copy): p.read_bytes()
            for p in self.copy.rglob("*")
            if p.is_file()
        }
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "PASS_QQ16_ZERO_RETENTION_DEFECTS cuts=3816 "
            "P=32368 J=2919388 K=199144 guard=22 borrowed_writes=0 no_new_kappa\n",
        )
        after = {
            p.relative_to(self.copy): p.read_bytes()
            for p in self.copy.rglob("*")
            if p.is_file()
        }
        self.assertEqual(after, before)

    def test_word_and_inventory_drift_reject(self):
        path = self.copy / "source" / "WORD.json"
        original = path.read_bytes()
        path.write_bytes(original + b" ")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("source size drift", result.stderr)
        path.write_bytes(original)
        inventory = self.copy / "PREDECESSOR.json"
        inventory.write_bytes(inventory.read_bytes() + b" ")
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inventory drift", result.stderr)

    def test_typed_receipt_corruption_rejects(self):
        path = self.copy / "RESULT.json"
        original = path.read_text()
        receipt = json.loads(original)
        receipt["schema_version"] = True  # Python's True == 1 must not authenticate it.
        path.write_text(json.dumps(receipt))
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("result certificate drift", result.stderr)
        path.write_text('{"schema_version":0,' + original.lstrip()[1:])
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate JSON key", result.stderr)
        receipt = json.loads(original)
        receipt["cut_certificate"][3800][3] = "0"
        path.write_text(json.dumps(receipt))
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("result certificate drift", result.stderr)

    def test_existing_write_target_is_unchanged(self):
        path = self.copy / "RESULT.json"
        before = path.read_bytes()
        result = self.run_cli("--write", str(path))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertEqual(path.read_bytes(), before)

    def test_oversized_receipt_rejects(self):
        path = self.copy / "RESULT.json"
        path.write_bytes(b" " * 2_000_001)
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("oversized input", result.stderr)


if __name__ == "__main__":
    unittest.main()
