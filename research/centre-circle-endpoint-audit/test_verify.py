#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the CLI, literal circuits, schedule and source boundary."""

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
SUBJECT_SPEC = importlib.util.spec_from_file_location(
    "endpoint_subject", HERE / "verify.py"
)
if SUBJECT_SPEC is None or SUBJECT_SPEC.loader is None:
    raise RuntimeError("local subject loader unavailable")
verify = importlib.util.module_from_spec(SUBJECT_SPEC)
SUBJECT_SPEC.loader.exec_module(verify)


class EndpointAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inputs = verify.load_inputs()
        cls.cuts, cls.response = verify.local_matrices(
            cls.inputs["programs"]["forward"], "forward"
        )

    def cli(self, script, *arguments, expected=0):
        process = subprocess.run(
            [sys.executable, "-I", "-O", "-Werror", "-B", str(script), *arguments],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
            env=os.environ.copy(),
        )
        self.assertEqual(process.returncode, expected, process.stdout + process.stderr)
        return process.stdout + process.stderr

    def test_actual_optimized_cli_and_exact_emission(self):
        result = json.loads(self.cli(HERE / "verify.py", "--emit"))
        self.assertEqual(result, json.loads((HERE / "RESULT.json").read_text()))
        self.assertIn(
            "joint_rank=16 late_rank=128 late_bridges=48", self.cli(HERE / "verify.py")
        )

    def test_literal_original_target_witness(self):
        backward, _ = verify.local_matrices(
            self.inputs["programs"]["backward"], "backward"
        )
        observed = verify.chronological_cuts(
            self.inputs["template"], {"forward": self.cuts, "backward": backward}
        )
        self.assertEqual([row.get(112, F(0)) for row in observed[0]], [0] * 8)
        self.assertEqual(
            [row.get(112, F(0)) for row in observed[10]], [-1, -1, -1, -1, 0, 0, 0, 0]
        )

    def test_missing_centre_rejected(self):
        program = [
            event
            for event in self.inputs["programs"]["forward"]
            if not (event[0] == "center" and event[1] == 0)
        ]
        with self.assertRaisesRegex(ValueError, "centre order"):
            verify.local_matrices(program, "forward")

    def test_fanout_sign_fault_rejected(self):
        program = copy.deepcopy(self.inputs["programs"]["forward"])
        center = next(i for i, e in enumerate(program) if e[0] == "center")
        event = next(
            e
            for e in program[center + 1 :]
            if e[0] == "scalar" and e[1][0] == "add" and e[1][2][0] == "C"
        )
        event[1][3] *= -1
        with self.assertRaisesRegex(ValueError, "ordinary scalar endpoint"):
            verify.local_matrices(program, "forward")

    def test_all_late_bridges_are_required(self):
        for mode in ("drop", "sign", "order"):
            with self.subTest(mode=mode):
                template = copy.deepcopy(self.inputs["template"])
                schedule = template["execution_schedule"]
                if mode == "drop":
                    del schedule[229]
                elif mode == "sign":
                    schedule[229]["coefficient"] = -1
                else:
                    schedule[229], schedule[230] = schedule[230], schedule[229]
                with self.assertRaisesRegex(ValueError, "late bridge chain"):
                    verify.late_responses(template, self.response)

    def test_owner_role_fault_rejected(self):
        template = copy.deepcopy(self.inputs["template"])
        call = next(
            c for c in template["calls"] if c["stage"] == 8 and c["replica"] == 0
        )
        call["owners"][112], call["owners"][113] = (
            call["owners"][113],
            call["owners"][112],
        )
        with self.assertRaisesRegex(ValueError, "complete late target response"):
            verify.late_responses(template, self.response)

    def test_rank_engine_on_independent_and_dependent_rows(self):
        self.assertEqual(
            verify.minor_receipt([{0: F(2)}, {1: F(3)}], range(2))["determinant"], "6"
        )
        self.assertEqual(len(verify.echelon([{0: F(1)}, {0: F(-7)}])[0]), 1)
        self.assertEqual(verify.determinant([[F(1), F(2)], [F(2), F(4)]]), 0)
        reduced = [dict(row) for row in self.response]
        reduced[0] = {}
        self.assertEqual(verify.minor_receipt(reduced, range(112, 224))["rank"], 7)
        self.assertEqual(
            verify.minor_receipt(self.response, range(112, 224))["rank"], 8
        )

    def test_git_free_read_only_export_and_corruption_controls(self):
        with tempfile.TemporaryDirectory(
            prefix="centre-endpoint-", dir=os.environ.get("TMPDIR")
        ) as work:
            root = Path(work)
            package = root / "research" / HERE.name
            package.mkdir(parents=True)
            for name in ("verify.py", "independent.py", "SOURCES.json", "RESULT.json"):
                shutil.copyfile(HERE / name, package / name)
            archive = root / verify.ARCHIVE
            archive.parent.mkdir(parents=True)
            shutil.copyfile(HERE.parents[1] / verify.ARCHIVE, archive)
            originals = {path: path.read_bytes() for path in package.iterdir()}
            for path in originals:
                path.chmod(0o444)
            archive.chmod(0o444)
            package.chmod(0o555)
            try:
                self.assertIn(
                    "PASS_CENTRE_CIRCLE_ENDPOINT_AUDIT", self.cli(package / "verify.py")
                )
                self.assertIn(
                    "joint_determinant=1024", self.cli(package / "independent.py")
                )
                self.assertEqual(
                    {path: path.read_bytes() for path in package.iterdir()}, originals
                )
            finally:
                package.chmod(0o755)
                for path in originals:
                    path.chmod(0o644)
                archive.chmod(0o644)
            receipt = package / "RESULT.json"
            wrong = json.loads(receipt.read_text())
            wrong["late_stage"]["direct_sum_rank"] = 0
            receipt.write_text(json.dumps(wrong))
            self.assertIn(
                "receipt differs", self.cli(package / "verify.py", expected=1)
            )
            receipt.write_bytes(originals[receipt])
            with archive.open("r+b") as stream:
                stream.write(b"broken archive")
            self.assertIn("archive hash", self.cli(package / "verify.py", expected=1))
            self.assertIn(
                "archive digest", self.cli(package / "independent.py", expected=1)
            )


if __name__ == "__main__":
    unittest.main()
