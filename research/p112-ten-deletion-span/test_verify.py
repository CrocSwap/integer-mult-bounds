"""Bounded behavioral controls; no full flat/orbit census is run here."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import beta
import geometry
import verify

WITNESS_8 = (
    9234633784970952704,
    4403416531266,
    356241767927876,
    123248381691908,
    3,
    121,
    582125436746596352,
    8796095643648,
    177,
    576495938286125056,
    9895671762944,
    229,
    5629500607954944,
    1099581362176,
)
WITNESS_10 = (
    881632412340060325,
    35734196326400,
    4611687410016717824,
    140891033437121,
    4,
    68,
    36591750462046208,
    6597078286336,
    125,
    126734110411456512,
    4398055030784,
    128,
    252834898098782208,
    2199040049152,
    175,
    72127965198024704,
    7696598188032,
)


def complete_transcript():
    """A small synthetic parser input with every required orbit index."""
    rows = ["flats 776805 reps 159 budget 10"]
    rows.extend(
        f"rep {i} flat {100 + i} lines 20 maxspan 4 active 10 "
        "maxdirs 10 positive_pairs 1"
        for i in range(159)
    )
    rows.append("TOTAL maxdirs 10 maxspan 4 positive_pairs 159 oracle_calls 159")
    return "\n".join(rows) + "\n"


class GeometryTests(unittest.TestCase):
    def test_catalogue_covers_chambers_and_retains_small_supports(self):
        directions, coverage = geometry.direction_catalogue()
        self.assertEqual(
            coverage["chamber_zero_counts"], (42, 28, 22, 14, 16, 23, 37, 63)
        )
        self.assertEqual(
            (coverage["weyl_directions"], coverage["d7"], coverage["e7"]),
            (1200, 1080, 120),
        )
        self.assertEqual(len(directions), 248)
        points = tuple(
            p for p in geometry.root_lines() if p not in geometry.frame_lines()
        )
        supports = [
            sum(bool(sum(a * b for a, b in zip(h, p, strict=True))) for p in points)
            for h in directions
        ]
        self.assertEqual(sorted(supports), [53] * 112 + [56] * 8 + [70] * 128)

    def test_signed_gram_rejects_a_nonorthogonal_permutation(self):
        points = tuple(
            p for p in geometry.root_lines() if p not in geometry.frame_lines()
        )
        permutation = list(range(112))
        self.assertEqual(geometry.signed_gram(points, permutation), 0)
        permutation[0], permutation[1] = permutation[1], permutation[0]
        with self.assertRaisesRegex(ValueError, "absolute Gram matrix"):
            geometry.signed_gram(points, permutation)

    def test_python_rank_is_rational_and_detects_dependence(self):
        rows = [
            (1, 1, 0, 0, 0, 0, 0, 0),
            (1, 0, 1, 0, 0, 0, 0, 0),
            (0, 1, 1, 0, 0, 0, 0, 0),
        ]
        # The leading 3x3 determinant is -2, while its binary rank is two.
        self.assertEqual(verify.matrix_rank(rows), 3)
        self.assertEqual(len(verify.binary_span([3, 5, 6])), 4)
        rows[2] = (2, 1, 1, 0, 0, 0, 0, 0)
        self.assertEqual(verify.matrix_rank(rows), 2)
        self.assertEqual(verify.matrix_rank([rows[0], rows[0]]), 1)
        with self.assertRaisesRegex(ValueError, "rational matrix capacity"):
            verify.matrix_rank([rows[0]] * 249)


class NativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory(
            prefix="p112-tests-", dir=os.environ.get("TMPDIR")
        )
        cls.addClassCleanup(temporary.cleanup)
        cls.work = Path(temporary.name)
        cls.binary = verify.build(cls.work)
        data = verify.ROOT / "research/one-sided-six-multisets/data"
        text, _ = geometry.fixture(data / "data.txt", data / "gens.txt")
        cls.lines = text.splitlines()
        if len(cls.lines) != 509:
            raise ValueError("test fixture capacity")
        cls.fixture = cls.work / "fixture.txt"
        cls.fixture.write_text(text)

    def native(self, *arguments, fixture=None):
        return subprocess.run(
            [str(self.binary), str(fixture or self.fixture), *map(str, arguments)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def assert_rejected(self, result, message):
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn(message, result.stderr)

    def test_native_rank_over_q_and_duplicate_indices(self):
        rows = list(self.lines)
        rows[1:4] = ["1 1 0 0 0 0 0 0", "1 0 1 0 0 0 0 0", "0 1 1 0 0 0 0 0"]
        path = self.work / "rank-fixture.txt"
        path.write_text("\n".join(rows) + "\n")
        result = self.native("--rank", 0, 1, 2, fixture=path)
        self.assertEqual((result.returncode, result.stdout), (0, "RANK 3\n"))
        rows[3] = "2 1 1 0 0 0 0 0"
        path.write_text("\n".join(rows) + "\n")
        result = self.native("--rank", 0, 1, 2, fixture=path)
        self.assertEqual((result.returncode, result.stdout), (0, "RANK 2\n"))
        result = self.native("--rank", 0, 0, 0, fixture=path)
        self.assertEqual((result.returncode, result.stdout), (0, "RANK 1\n"))

    def test_native_rejects_invalid_cli_bounds(self):
        cases = (
            ((9,), "budget must be 8 or 10"),
            (("10junk",), "invalid integer"),
            ((10, 0), "invalid orbit limit"),
            ((10, 160), "invalid orbit limit"),
            (("--rank", -1), "direction index"),
            (("--rank", 248), "direction index"),
            (("--rank", *range(9)), "usage:"),
        )
        for arguments, message in cases:
            with self.subTest(arguments=arguments):
                self.assert_rejected(self.native(*arguments), message)

    def test_native_rejects_malformed_fixture_fields(self):
        cases = (
            (0, "0 " + " ".join(self.lines[0].split()[1:]), "invalid label"),
            (1, "4 0 0 0 0 0 0 0", "invalid coordinate"),
            (1, "0 0 0 0 0 0 0 0", "invalid direction norm"),
            (1, "3 3 0 0 0 0 0 0", "invalid direction norm"),
            (249, "1 0", "invalid support"),
            (249, f"0 {1 << 48}", "invalid support"),
            (497, " ".join(["0"] * 112), "invalid permutation"),
        )
        for index, replacement, message in cases:
            rows = list(self.lines)
            rows[index] = replacement
            path = self.work / "bad-fixture.txt"
            path.write_text("\n".join(rows) + "\n")
            with self.subTest(index=index, replacement=replacement):
                self.assert_rejected(self.native("--rank", 0, fixture=path), message)

    def test_native_rejects_truncated_and_trailing_fixture_data(self):
        cases = (
            ("", "invalid label"),
            ("\n".join(self.lines) + "\nextra\n", "trailing fixture input"),
        )
        for text, message in cases:
            path = self.work / "bad-fixture.txt"
            path.write_text(text)
            with self.subTest(message=message):
                self.assert_rejected(self.native("--rank", 0, fixture=path), message)


class ReceiptTests(unittest.TestCase):
    def test_twelve_separate_deletions_allow_span_five(self):
        result = verify.witness_check(verify.WITNESS_12, 12)
        self.assertEqual((result["rank"], result["common_union_size"]), (5, 39))

    def test_parser_accepts_complete_rows_and_refuses_incomplete_slice(self):
        text = complete_transcript()
        actual = verify.parse_census(text, 10)
        self.assertEqual(
            actual["total"],
            {
                "max_directions": 10,
                "max_span": 4,
                "positive_pairs": 159,
                "oracle_calls": 159,
            },
        )
        self.assertEqual(actual["pairs"], 123511995)
        rows = text.splitlines()
        del rows[47]
        with self.assertRaisesRegex(ValueError, "incomplete orbit slice"):
            verify.parse_census("\n".join(rows) + "\n", 10)

    def test_parser_rejects_changed_totals_and_invalid_rows(self):
        text = complete_transcript()
        with self.assertRaisesRegex(ValueError, "inconsistent census total"):
            verify.parse_census(
                text.replace("positive_pairs 159", "positive_pairs 160"), 10
            )
        with self.assertRaisesRegex(ValueError, "census row range"):
            verify.parse_census(text.replace("lines 20", "lines 21", 1), 10)
        with self.assertRaisesRegex(ValueError, "duplicate flat representative"):
            verify.parse_census(text.replace("flat 101", "flat 100", 1), 10)
        with self.assertRaisesRegex(ValueError, "flat/orbit coverage"):
            verify.parse_census(text, 8)

    def test_positive_witnesses_check_rational_span_and_cuts(self):
        self.assertEqual(verify.witness_check(WITNESS_8, 8)["rank"], 3)
        self.assertEqual(verify.witness_check(WITNESS_10, 10)["rank"], 4)
        incorrect = list(WITNESS_10)
        incorrect[6] = (1 << 64) - 1
        with self.assertRaisesRegex(ValueError, "witness deletion budget"):
            verify.witness_check(incorrect, 10)
        dependent = list(WITNESS_10)
        dependent[-3:] = dependent[5:8]
        with self.assertRaisesRegex(ValueError, "dependent sharp-span witness"):
            verify.witness_check(dependent, 10)

    def test_bound_sources_rejects_changed_input_bytes(self):
        actual = verify.bound_sources()
        target = verify.ROOT / "research/one-sided-six-multisets/data/data.txt"
        self.assertEqual(len(actual), 2)
        self.assertEqual(
            actual[str(target.relative_to(verify.ROOT))],
            "ac4a48851b922f2a433684b60c74768ae3bb4fc5e8990ffe63e3942bb3c2ea34",
        )
        original = Path.read_bytes

        def corrupted(path):
            raw = original(path)
            return raw + b"\nchanged\n" if path == target else raw

        with (
            patch.object(Path, "read_bytes", corrupted),
            self.assertRaisesRegex(ValueError, "changed source:.*data.txt"),
        ):
            verify.bound_sources()

    def test_output_export_does_not_overwrite_existing_file(self):
        with tempfile.TemporaryDirectory(
            prefix="p112-export-", dir=os.environ.get("TMPDIR")
        ) as temporary:
            output = Path(temporary) / "receipt.json"
            output.write_text('{"keep": true}\n')
            result = subprocess.run(
                [
                    sys.executable,
                    str(verify.PACKAGE / "verify.py"),
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("output already exists", result.stderr)
            self.assertEqual(json.loads(output.read_text()), {"keep": True})


class BetaTests(unittest.TestCase):
    def test_new_shape_needs_ten_deletions_and_leaves_two_shapes(self):
        shape = (2, 4, 5, 6, 6, 6, 6, 6, 6)
        self.assertIsNone(beta.certificate(shape, 8, 3))
        self.assertIsNone(beta.certificate(shape, 8, 4))
        certificate = beta.certificate(shape, 10, 4)
        self.assertEqual(certificate["quotient_basis"], (2, 4, 5, 6))
        self.assertEqual(
            (
                certificate["support_cap"],
                certificate["deleted_lines"],
                certificate["direction_bound"],
            ),
            (42, 10, 4),
        )
        result = beta.reduction()
        self.assertEqual(
            [row["weights"] for row in result["new_p10_exclusions"]], [shape]
        )
        self.assertEqual(
            result["remaining"],
            [(2, 5, 5, 5, 6, 6, 6, 6, 6), (3, 4, 4, 6, 6, 6, 6, 6, 6)],
        )
        self.assertEqual(result["minimum_cover_budgets"], [10, 14, 12])
        self.assertEqual(
            (result["examined"], len(result["earlier_p8_exclusions"])), (4795, 12)
        )

    def test_cover_rejects_invalid_boundary_inputs(self):
        cases = (
            ((2, 4, 5, 6), 10, 4),
            ((4, 2, 5, 6, 6), 10, 4),
            ((2, 4, 5, 6, 6), -1, 4),
            ((2, 4, 5, 6, 6), 10, 9),
        )
        for weights, budget, span in cases:
            with (
                self.subTest(weights=weights, budget=budget, span=span),
                self.assertRaises(ValueError),
            ):
                beta.certificate(weights, budget, span)


if __name__ == "__main__":
    unittest.main()
