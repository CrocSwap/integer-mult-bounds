# SPDX-License-Identifier: Apache-2.0
"""Behavior checks for the explicit-subspace oracle and its published command."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

import frames
import verify


class FrameTests(unittest.TestCase):
    def test_explicit_span_and_dependence(self):
        self.assertEqual(frames.span((1, 2, 4)), frozenset(range(8)))
        with self.assertRaisesRegex(frames.Invalid, "independent frame"):
            frames.span((1, 2, 3))
        with self.assertRaisesRegex(frames.Invalid, "at most nine"):
            frames.span(tuple(range(1, 11)))

    def test_charged_climb_and_non_nested_failure(self):
        current, paid, events = [frames.span((1,))], Counter(), []
        frames.climb(current, paid, events, ("test", 0), 0, frames.span((1, 2, 4)))
        self.assertEqual(dict(paid), {2: 1})
        self.assertEqual(events, [["test", 0, 0, 1, 3, 2]])
        with self.assertRaisesRegex(frames.Invalid, "nonmonotone"):
            frames.climb(current, paid, events, ("test", 1), 0, frames.span((2, 4)))
        self.assertEqual(dict(paid), {2: 1})

    def test_warp_image_and_inverse(self):
        columns = [2, 1, 4, 8, 16, 32, 64, 128, 256]
        current = [frames.span((1,))]
        frames.warp(current, 0, columns, [1], [2])
        self.assertEqual(current, [frozenset({0, 2})])
        frames.warp(current, 0, columns, [1], [2], inverse=True)
        self.assertEqual(current, [frozenset({0, 1})])
        with self.assertRaisesRegex(frames.Invalid, "warp image"):
            frames.warp(current, 0, columns, [1], [4])
        cycle = [2, 4, 1, 8, 16, 32, 64, 128, 256]
        current = [frames.span((2,))]
        word = {"warps": [[0, 0, cycle, [1], [2]]]}
        frames.scalar_step(
            word, current, Counter(), [], "A", 0, ["warp", 0, -1, [2], [1]]
        )
        self.assertEqual(current, [frozenset({0, 1})])

    def test_cli_exact_result_and_optimized_equality(self):
        with tempfile.TemporaryDirectory() as temporary:
            env = {**os.environ, "PYTHONPYCACHEPREFIX": temporary}
            command = [sys.executable, "-B", str(verify.PACKAGE / "verify.py")]
            normal = subprocess.run(
                command, check=True, capture_output=True, text=True, timeout=60, env=env
            )
            optimized = subprocess.run(
                command[:1] + ["-O"] + command[1:],
                check=True,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )
        self.assertEqual(normal.stdout, optimized.stdout)
        report = json.loads(normal.stdout)
        self.assertEqual(report["status"], "PASS_INDEPENDENT_RANK7_JOINT_FRAME_AUDIT")
        for tag in ("base", "extra"):
            provider = report["providers"][tag]
            self.assertEqual(
                provider["groups"]["V45"]["profile_delta"],
                {"1": -2, "2": 10, "3": 6, "4": -10},
            )
            self.assertEqual(
                [
                    s["surrogate_margin"]
                    for s in provider["V45_subsets"]
                    if len(s["helpers"]) in (0, 1, 4)
                ],
                [-78512, -53141, -53141, -53141, -53141, 22972],
            )
            self.assertEqual(len(provider["controls"]), 9)
        self.assertEqual(
            report["invoice_boundary"]["conditional_idle_remainder"],
            {"1": 17310, "3": 4956, "5": 1728, "48": 28190},
        )

    def test_git_free_export_and_corrupted_source_rejection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / "research" / verify.PACKAGE.name
            package.mkdir(parents=True)
            for name in ("frames.py", "lowering.py", "verify.py", "SOURCES.json"):
                shutil.copyfile(verify.PACKAGE / name, package / name)
            records = json.loads((package / "SOURCES.json").read_text())["files"]
            for record in records:
                if record["usage"] == "input":
                    target = root / record["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(verify.ROOT / record["path"], target)
            env = {**os.environ, "PYTHONPYCACHEPREFIX": str(root / "bytecode")}
            command = [sys.executable, "-O", "-B", str(package / "verify.py")]
            good = subprocess.run(
                command, check=True, capture_output=True, text=True, timeout=60, env=env
            )
            self.assertEqual(
                json.loads(good.stdout)["providers"]["base"]["final"]["widths"],
                {"4": 26, "5": 2, "6": 16, "7": 52, "8": 99, "9": 213},
            )
            source = root / verify.SOURCE / "data/STAGE1-FRAME-EDITS.json"
            source.write_bytes(source.read_bytes() + b" ")
            bad = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=60,
                env=env,
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(bad.stdout, "")
            self.assertIn("input SHA256:", bad.stderr)


if __name__ == "__main__":
    unittest.main()
