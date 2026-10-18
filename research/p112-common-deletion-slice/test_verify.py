#!/usr/bin/env python3
"""Behavioral, arithmetic, quantifier and failure controls for the C5 slice."""

import copy
import subprocess
import tempfile
import unittest
from pathlib import Path

import geometry
import verify


class SliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="p112-slice-tests-")
        cls.directory = Path(cls.temporary.name)
        cls.fixture = verify.read_json(verify.PACKAGE / "FIXTURE.json")
        cls.result = verify.read_json(verify.PACKAGE / "RESULT.json")
        cls.model, cls.geometry_report = verify.build_model(cls.fixture)
        cls.executable = verify.compile_scanner(cls.directory)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_literal_sharpness_boundary(self):
        checked = verify.check_case(self.fixture, self.result["scan"]["witness"])
        self.assertEqual(checked, {"residual_ranks": [7, 7, 7, 7], "rational_span": 4})

    def test_common_cut_is_required(self):
        witness = copy.deepcopy(self.result["scan"]["witness"])
        witness["deleted_labels"] = []
        with self.assertRaisesRegex(ValueError, "residual rank"):
            verify.check_case(self.fixture, witness)

    def test_dependent_direction_is_rejected(self):
        witness = copy.deepcopy(self.result["scan"]["witness"])
        witness["directions"][1] = witness["directions"][0]
        with self.assertRaisesRegex(ValueError, "false rational rank"):
            verify.check_case(self.fixture, witness)

    def test_wrong_declared_rank_is_rejected(self):
        witness = copy.deepcopy(self.result["scan"]["witness"])
        witness["rank"] = 3
        with self.assertRaisesRegex(ValueError, "false rational rank"):
            verify.check_case(self.fixture, witness)

    def test_bad_common_sets_are_rejected(self):
        for deleted in ([299] * 4, [0], [299, 363, 361, 297, 1]):
            with self.subTest(deleted=deleted):
                witness = copy.deepcopy(self.result["scan"]["witness"])
                witness["deleted_labels"] = deleted
                with self.assertRaises(ValueError):
                    verify.check_case(self.fixture, witness)

        witness = copy.deepcopy(self.result["scan"]["witness"])
        witness["V2_annihilator"] = [8, 8, 160]
        with self.assertRaisesRegex(ValueError, "dependent annihilator"):
            verify.check_case(self.fixture, witness)

    def test_invalid_fixture_boundaries(self):
        for key, value in (
            ("schema", "wrong"),
            ("V1_basis", [1] * 6),
            ("V1_basis", [True, 6, 66, 138, 2, 57]),
            ("omitted_frame", [[0] * 8] * 8),
        ):
            with self.subTest(key=key, value=value):
                fixture = copy.deepcopy(self.fixture)
                fixture[key] = value
                with self.assertRaises(ValueError):
                    verify.fixture_geometry(fixture)

    def test_coverage_includes_normal_planes(self):
        self.assertEqual(
            self.geometry_report["normal_dimensions"], {"1": 4560, "2": 1120}
        )
        self.assertEqual(
            [row["orbit_size"] for row in self.geometry_report["parabolic_orbits"]],
            [1120, 120, 3360, 1080],
        )
        self.assertEqual(
            self.geometry_report["model_sha256"], self.result["model_sha256"]
        )

    def test_independent_root_and_label_invariants(self):
        roots = geometry.roots()
        self.assertEqual(len(roots), 120)
        self.assertEqual({sum(x * x for x in row) for row in roots}, {8})
        self.assertEqual(len({geometry.label(row) for row in roots}), 120)
        for row in roots:
            coordinates = geometry.coordinates(row)
            reconstructed = tuple(
                sum(coordinates[i] * geometry.SIMPLE[i][j] for i in range(8))
                for j in range(8)
            )
            self.assertEqual(reconstructed, row)

    def test_binary_rank_against_complete_xor_spans(self):
        # Exhaust every subset of a nine-vector dependent fixture.
        values = [1, 2, 4, 8, 16, 3, 5, 9, 17]
        for mask in range(512):
            rows = [value for i, value in enumerate(values) if mask >> i & 1]
            self.assertEqual(
                1 << verify.binary_rank(rows), len(verify.binary_span(rows))
            )

    def test_scanner_positive_and_quantifier_controls(self):
        process = subprocess.run(
            [str(self.executable), "--self-test"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
        self.assertEqual(process.stdout, "PASS_SCAN_CONTROLS\n")

    def test_scanner_rejects_malformed_streams(self):
        lines = self.model.splitlines()
        duplicate = lines[0].split()
        duplicate[1] = duplicate[0]
        wrong_count = lines.copy()
        wrong_count[2] = "5679"
        for model in (
            "",
            " ".join(duplicate) + "\n",
            "\n".join(wrong_count),
            self.model + "unexpected trailing bytes\n",
        ):
            with self.subTest(prefix=model[:30]):
                process = subprocess.run(
                    [str(self.executable)],
                    input=model,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                self.assertEqual(process.returncode, 2)
                self.assertIn("FAIL:", process.stderr)
                self.assertEqual(process.stdout, "")

    def test_semantic_mutants_fail_controls(self):
        source = (verify.PACKAGE / "scan.cpp").read_text()
        mutants = (
            ("if (rank == 8) return small;", "if (rank == 8) return {0};"),
            (
                'require(rank == 9, "invalid residual rank");',
                'require(rank == 9, "invalid residual rank"); return small;',
            ),
            ("if (weight(next) > 4) continue;", "if (weight(next) > 6) continue;"),
        )
        for index, (old, new) in enumerate(mutants):
            with self.subTest(mutant=index):
                self.assertEqual(source.count(old), 1)
                path = self.directory / f"mutant-{index}.cpp"
                path.write_text(source.replace(old, new))
                mutant = verify.compile_scanner(self.directory, path)
                process = subprocess.run(
                    [str(mutant), "--self-test"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                self.assertEqual(process.returncode, 2)
                self.assertIn("FAIL:", process.stderr)
        # Later tests must not accidentally reuse the last mutant.
        self.executable = verify.compile_scanner(self.directory)

    def test_json_capacity_and_shape(self):
        path = self.directory / "bad.json"
        for data in ("[]", "{bad", " " * (2 * 1024 * 1024 + 1)):
            path.write_text(data)
            with self.assertRaises(ValueError):
                verify.read_json(path)

    def test_cli_rejects_bad_fixture_and_receipt(self):
        bad = self.directory / "bad.json"
        bad.write_text("[]")
        for option in ("--fixture", "--expected"):
            process = subprocess.run(
                ["python3", "-B", str(verify.PACKAGE / "verify.py"), option, str(bad)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(process.returncode, 2)
            self.assertIn("JSON must be an object", process.stderr)
            self.assertNotIn("PASS_", process.stdout)

    def test_rank_trace_rejects_false_or_missing_cases(self):
        case = copy.deepcopy(self.result["scan"]["witness"])
        checked = verify.check_rank_trace(
            self.fixture, {"rank_checks": [case], "exact_rank_checks": 1}
        )
        self.assertEqual(checked["cases"], 1)
        with self.assertRaisesRegex(ValueError, "incomplete"):
            verify.check_rank_trace(
                self.fixture, {"rank_checks": [case], "exact_rank_checks": 2}
            )
        case["rank"] = 3
        with self.assertRaisesRegex(ValueError, "false rational rank"):
            verify.check_rank_trace(
                self.fixture, {"rank_checks": [case], "exact_rank_checks": 1}
            )


if __name__ == "__main__":
    unittest.main()
