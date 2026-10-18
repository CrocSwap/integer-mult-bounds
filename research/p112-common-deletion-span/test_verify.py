"""Behavioral controls and separate finite oracles for the common-set theorem."""

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from itertools import combinations
from math import gcd
from pathlib import Path
from unittest.mock import patch

import geometry as g
import verify as v


def integer_rank(rows: list[tuple]) -> int:
    """Fraction-free row elimination, independent of geometry.echelon."""
    matrix = [list(row) for row in rows]
    rank = 0
    for column in range(8):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        for i in range(rank + 1, len(matrix)):
            a, b = matrix[rank][column], matrix[i][column]
            matrix[i] = [a * matrix[i][j] - b * matrix[rank][j] for j in range(8)]
            divisor = gcd(*matrix[i])
            if divisor:
                matrix[i] = [x // divisor for x in matrix[i]]
        rank += 1
    return rank


def vector_orbit(seed: tuple) -> set[tuple]:
    """Reflect primitive normals, without using root-mask permutations."""
    seen = {seed}
    queue = [seed]
    for cursor in range(1201):
        if cursor == len(queue):
            return seen
        for alpha in g.SIMPLE:
            row = queue[cursor]
            pairing = g.dot(row, alpha)
            reflected = g.canonical(
                tuple(4 * row[j] - pairing * alpha[j] for j in range(8))
            )
            if reflected not in seen:
                if len(queue) >= 1200:
                    raise ValueError("normal orbit exceeded capacity")
                seen.add(reflected)
                queue.append(reflected)
    raise ValueError("normal orbit did not close")


class CommonDeletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = v.read_json(v.PACKAGE / "FIXTURE.json")
        cls.lines, cls.labels, cls.live, cls.covered = v.fixture_geometry(cls.fixture)
        cls.qualified, cls.geometry = v.qualified_directions(
            cls.lines, cls.labels, cls.live, cls.covered
        )
        cls.characters = v.character_masks(cls.labels, cls.live)

    def test_literal_sharp_values(self) -> None:
        result = v.prove(self.fixture)
        self.assertEqual(result, v.read_json(v.PACKAGE / "RESULT.json"))
        self.assertEqual(result["maximum_common_deletion_span"], 3)
        self.assertEqual(result["separate_deletion_span"], 5)
        self.assertEqual(result["all_real_direction_count"], 10)

    def test_root_and_simple_basis_ranks(self) -> None:
        self.assertEqual(integer_rank(list(g.SIMPLE)), 8)
        self.assertEqual(integer_rank(list(self.lines)), 8)
        self.assertEqual(len(set(self.labels)), 120)
        self.assertEqual(v.binary_rank(self.labels), 9)
        self.assertTrue(all(g.dot(row, row) == 8 for row in self.lines))

    def test_independent_normal_orbits(self) -> None:
        all_masks = set()
        for zero_set, expected in ((127, 120), (254, 1080)):
            seed_mask = sum(
                1 << i
                for i, row in enumerate(self.lines)
                if all(
                    c == 0 or zero_set >> j & 1
                    for j, c in enumerate(g.coordinates(row))
                )
            )
            normals = vector_orbit(g.normal(self.lines, seed_mask))
            self.assertEqual(len(normals), expected)
            all_masks |= {
                sum(1 << i for i, root in enumerate(self.lines) if g.dot(root, h) == 0)
                for h in normals
            }
        candidates, _ = g.orthogonality_systems(self.lines, self.live)
        self.assertEqual(
            set(candidates), {m for m in all_masks if (m & self.live).bit_count() >= 40}
        )
        self.assertEqual(len(candidates), 248)

    def test_character_oracle_and_all_residual_ranks(self) -> None:
        # Enumerate the binary evaluation code by XOR of its nine generators.
        code = [0]
        for bit in range(9):
            generator = (
                sum(1 << i for i, x in enumerate(self.labels) if x >> bit & 1)
                & self.live
            )
            code += [x ^ generator for x in code]
        self.assertEqual(code, self.characters)
        systems, _ = g.orthogonality_systems(self.lines, self.live)
        for system in systems:
            residual = self.live & ~(system | self.covered)
            code_size = len({word & residual for word in code})
            rows = [x for i, x in enumerate(self.labels) if residual >> i & 1]
            self.assertEqual(1 << v.binary_rank(rows), code_size)

    def test_cuts_against_literal_label_span(self) -> None:
        for row in self.qualified:
            residual = [
                x
                for i, x in enumerate(self.labels)
                if self.live >> i & 1
                and g.dot(self.lines[i], row["vector"])
                and not self.covered >> i & 1
            ]
            self.assertEqual(len(v.binary_span(residual)), 256)
            for cut in row["cuts"]:
                removed = {x for i, x in enumerate(self.labels) if cut >> i & 1}
                self.assertLessEqual(len(removed), 4)
                self.assertEqual(
                    len(v.binary_span([x for x in residual if x not in removed])), 128
                )

    def test_rank_nine_requires_two_independent_characters(self) -> None:
        # Nine independent singleton columns need two deletions, not one.
        labels = [1 << j for j in range(9)] + [0] * 111
        characters = v.character_masks(labels, (1 << 9) - 1)
        cuts = v.deletion_cuts((1 << 9) - 1, 9, characters)
        self.assertEqual(
            set(cuts), {(1 << a) | (1 << b) for a, b in combinations(range(9), 2)}
        )
        self.assertEqual(
            v.deletion_cuts(255, 8, characters), [1 << j for j in range(8)]
        )
        self.assertEqual(v.deletion_cuts(127, 7, characters), [0])

    def test_shared_set_oracle_and_integer_ranks(self) -> None:
        # Here every direction has one minimal cut. Exhaust all 2^10 selections.
        cuts = [row["cuts"][0] for row in self.qualified]
        unions = {0}
        for cut in cuts:
            unions |= {state | cut for state in tuple(unions)}
        allowed = {state for state in unions if state.bit_count() <= 4}
        self.assertEqual(allowed, set(v.common_states(self.qualified)))
        maximum = 0
        for state in allowed:
            vectors = [
                row["vector"] for row in self.qualified if row["cuts"][0] & ~state == 0
            ]
            maximum = max(maximum, integer_rank(vectors))
        self.assertEqual(maximum, 3)
        self.assertEqual(integer_rank([row["vector"] for row in self.qualified]), 5)

    def test_every_small_subset_of_the_relevant_twelve_lines(self) -> None:
        relevant = 0
        residuals = []
        for row in self.qualified:
            relevant |= row["cuts"][0]
            residuals.append(
                self.live
                & ~self.covered
                & sum(
                    1 << i
                    for i, root in enumerate(self.lines)
                    if g.dot(root, row["vector"])
                )
            )
        indices = [i for i in range(120) if relevant >> i & 1]
        self.assertEqual(len(indices), 12)
        checked, maximum = 0, 0
        for size in range(5):
            for selected in combinations(indices, size):
                deleted = sum(1 << i for i in selected)
                vectors = [
                    row["vector"]
                    for row, residual in zip(self.qualified, residuals, strict=True)
                    if len({word & residual & ~deleted for word in self.characters})
                    <= 128
                ]
                maximum = max(maximum, integer_rank(vectors))
                checked += 1
        self.assertEqual((checked, maximum), (794, 3))

    def test_dropping_reflections_rejects(self) -> None:
        with (
            patch.object(
                g, "reflection_permutations", return_value=[list(range(120))] * 8
            ),
            self.assertRaisesRegex(ValueError, "classification changed"),
        ):
            v.prove(self.fixture)

    def test_accepting_every_direction_rejects(self) -> None:
        with (
            patch.object(v, "deletion_cuts", return_value=[0]),
            self.assertRaisesRegex(ValueError, "inventory exceeded"),
        ):
            v.prove(self.fixture)

    def test_missing_direction_rejects(self) -> None:
        original = v.qualified_directions

        def shortened(*args: object) -> tuple:
            rows, report = original(*args)
            return rows[:-1], report

        with (
            patch.object(v, "qualified_directions", side_effect=shortened),
            self.assertRaisesRegex(ValueError, "classification changed"),
        ):
            v.prove(self.fixture)

    def test_invalid_frames_and_bases_reject(self) -> None:
        bad = copy.deepcopy(self.fixture)
        bad["omitted_frame"][0] = bad["omitted_frame"][1]
        with self.assertRaisesRegex(ValueError, "invalid frame"):
            v.fixture_geometry(bad)
        for value in (0, True, 512, "6"):
            bad = copy.deepcopy(self.fixture)
            bad["V1_basis"][0] = value
            with self.assertRaisesRegex(ValueError, "invalid basis"):
                v.fixture_geometry(bad)
        bad = copy.deepcopy(self.fixture)
        bad["V2_basis"][0] = bad["V2_basis"][1]
        with self.assertRaisesRegex(ValueError, "independent"):
            v.fixture_geometry(bad)

    def test_git_free_cli_and_corruption_rejection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            exported = Path(directory)
            for name in (
                "geometry.py",
                "verify.py",
                "FIXTURE.json",
                "RESULT.json",
                "SOURCES.json",
            ):
                shutil.copyfile(v.PACKAGE / name, exported / name)
            command = [sys.executable, "-O", "-B", str(exported / "verify.py")]
            options = {
                "text": True,
                "capture_output": True,
                "timeout": 30,
                "check": False,
                "cwd": exported,
            }
            result = subprocess.run(command, **options)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("common_span=3", result.stdout)
            receipt = v.read_json(exported / "RESULT.json")
            receipt["maximum_common_deletion_span"] = 4
            (exported / "RESULT.json").write_text(json.dumps(receipt), encoding="utf-8")
            result = subprocess.run(command, **options)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("differs from the committed receipt", result.stderr)
            (exported / "FIXTURE.json").write_text("{}", encoding="utf-8")
            result = subprocess.run(command, **options)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fixture pin mismatch", result.stderr)

    def test_orbit_capacity_rejects_instead_of_truncating(self) -> None:
        with self.assertRaisesRegex(ValueError, "Weyl orbit exceeded capacity"):
            g.orbit(7, g.reflection_permutations(self.lines))

    def test_json_boundary_limits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            for text, message in (
                ("[]", "object"),
                (" " * (1024 * 1024 + 1), "one MiB"),
            ):
                path.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    v.read_json(path)


if __name__ == "__main__":
    unittest.main()
