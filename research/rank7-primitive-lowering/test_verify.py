# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls and independent integer-arithmetic checks."""

import copy
from fractions import Fraction as Q
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from fixtures import BLOCKS, check_blocks, instructions, produce
from literal import check_macro
from lower import POLICIES, certify, exclude_short_blocks, execute, lower
from replay import PACKAGE, ROOT, authenticate, read
from verify import (
    audit,
    check_expansion,
    coefficient_certificate,
    compare_variants,
    materialize,
    source_obligations,
)


def integer_census():
    """A separate fixed-denominator engine; three halvings fit denominator 8."""
    states = {(8, 0, 0, 8, 0, 0)}
    counts = [1]
    for _depth in range(3):
        following = set(states)
        for state in states:
            for target in range(3):
                for mode in range(4):
                    rows = list(state)
                    for column in range(2):
                        i = 2 * target + column
                        if mode == 0:
                            rows[i] = 0
                        elif mode == 1:
                            rows[i] = -rows[i]
                        elif mode == 2:
                            rows[i] *= 2
                        else:
                            if rows[i] % 2:
                                raise ValueError("insufficient exact denominator")
                            rows[i] //= 2
                    following.add(tuple(rows))
                for source in range(3):
                    if source == target:
                        continue
                    for sign in (0, -1, 1):
                        rows = list(state)
                        for column in range(2):
                            i, j = 2 * target + column, 2 * source + column
                            rows[i] = rows[j] if sign == 0 else rows[i] + sign * rows[j]
                        following.add(tuple(rows))
        states = following
        counts.append(len(states))
    return counts, states


class LoweringTests(unittest.TestCase):
    def test_literal_unit_blocks(self):
        counts = check_blocks()
        self.assertEqual(counts["parent"]["inverse=False,dual=False"], 4)
        self.assertEqual(counts["three_add"]["inverse=False,dual=False"], 4)
        self.assertEqual(counts["tariff"]["inverse=False,dual=False"], 4)
        self.assertEqual(
            instructions(BLOCKS["three_add"]),
            [("add", 1, 0, 1), ("add", 0, 1, -1), ("add", 1, 0, 1), ("add", 1, 0, 1)],
        )

    def test_complete_small_word_exclusion(self):
        counts, states = integer_census()
        self.assertEqual(counts, [1, 19, 208, 1769])
        self.assertEqual(exclude_short_blocks()["cumulative_states"], counts)
        self.assertNotIn((0, -8, 8, -8, 0, 0), states)
        self.assertNotIn((-8, 8, -8, 0, 0, 0), states)
        self.assertNotIn((-8, -8, 8, 0, 0, 0), states)
        self.assertNotIn((0, 8, -8, -8, 0, 0), states)
        self.assertIn((8, 8, 0, 8, 0, 0), states)

    def test_entire_bounded_coefficient_domain(self):
        checked = 0
        for numerator in range(-255, 256):
            for exponent in range(13):
                for policy in POLICIES:
                    recipe = certify("add", numerator, 1 << exponent, policy=policy)
                    self.assertEqual(
                        execute(recipe, ((1, 0), (0, 1), (0, 0))),
                        ((1, Q(numerator, 1 << exponent)), (0, 1), (0, 0)),
                    )
                checked += 1
        self.assertEqual(checked, 6643)
        for exponent in range(-12, 8):
            for sign in (-1, 1):
                q = sign * Q(2) ** exponent
                self.assertEqual(
                    execute(
                        certify("scale", q.numerator, q.denominator),
                        ((1, 0), (0, 1), (0, 0)),
                    ),
                    ((q, 0), (0, 1), (0, 0)),
                )

    def test_arbitrary_signed_fractional_inputs(self):
        result = execute(lower("add", -3, 8), ((Q(11, 7), 0), (Q(-5, 13), 0), (0, 0)))
        self.assertEqual(result, ((Q(1249, 728), 0), (Q(-5, 13), 0), (0, 0)))
        self.assertEqual(lower("add", 2, 1), [("add", 0, 1, 1), ("add", 0, 1, 1)])
        self.assertEqual(lower("scale", 1, 1), [])
        self.assertEqual(lower("add", 0, 1), [])

    def test_mutable_source_is_restored_and_cheaper(self):
        self.assertEqual(
            lower("add", 1, 2, policy="source_walk"),
            [("half", 1), ("add", 0, 1, 1), ("double", 1)],
        )
        self.assertEqual(
            execute(
                lower("add", 1, 2, policy="source_walk")[:1], ((1, 0), (0, 1), (0, 0))
            )[1],
            (0, Q(1, 2)),
        )
        with self.assertRaisesRegex(ValueError, "source preservation"):
            certify(
                "add",
                1,
                2,
                [("half", 1), ("add", 0, 1, 1), ("half", 1)],
                policy="source_walk",
            )
        events = [
            ["scalar", ["add", ["L", 2], ["L", 3], 1, 2], 7],
            ["scalar", ["add", ["L", 3], ["L", 2], -3, 2], 7],
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            before = materialize(events, path / "read.json.gz")
            after = materialize(events, path / "write.json.gz", policy="source_walk")
            target = materialize(events, path / "target.json.gz", policy="target_walk")
            self.assertEqual(before["real_instructions"], 20)
            self.assertEqual(after["real_instructions"], 14)
            self.assertEqual(target["real_instructions"], 14)
            self.assertEqual(
                lower("add", 1, 2, policy="target_walk"),
                [("double", 0), ("add", 0, 1, 1), ("half", 0)],
            )
            self.assertEqual(
                check_expansion(
                    events, read(path / "write.json.gz"), policy="source_walk"
                ),
                4,
            )

    def test_exact_width_and_source_access_ledger(self):
        events = [
            ["scalar", ["add", ["L", 2], ["L", 3], 1, 2], 7],
            ["scalar", ["add", ["L", 3], ["L", 2], -3, 2], 7],
        ]
        ledger = source_obligations(events)
        self.assertEqual(ledger["changed_scalar_macros"], 2)
        self.assertEqual(ledger["real_instructions_saved"], 6)
        self.assertEqual(
            ledger["writable_source_extra_fractional_bits"],
            [[["L", 2], 1], [["L", 3], 1]],
        )
        source = coefficient_certificate(events, policy="source_walk")["add:1/2"]
        target = coefficient_certificate(events, policy="target_walk")["add:1/2"]
        self.assertEqual(
            (source["source_extra_fractional_bits"], source["target_add_peak_factor"]),
            (1, "1"),
        )
        self.assertEqual(
            (target["source_extra_fractional_bits"], target["target_add_peak_factor"]),
            (0, "2"),
        )

    def test_comparison_rejects_false_cost_or_non_scalar_claim(self):
        rows = read(PACKAGE / "evidence/RESULT.json")["providers"]["base"]
        compare_variants(rows)
        for field, value in (("real_instructions", 1), ("non_scalar_sha256", "wrong")):
            changed = copy.deepcopy(rows)
            changed["tariff"]["forward"]["lowerings"]["source_walk"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                compare_variants(changed)

    def test_invalid_coefficients_and_instructions(self):
        cases = [
            ("add", 1, 3),
            ("add", 256, 1),
            ("add", 1, 8192),
            ("scale", 3, 1),
            ("scale", 0, 1),
            ("unknown", 1, 1),
        ]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                lower(*case)
        for operation in (
            ("add", 0, 0, 1),
            ("add", 0, 1, 2),
            ("half", 3),
            ("unknown", 0),
        ):
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                execute([operation], ((1, 0), (0, 1), (0, 0)))

    def test_local_semantic_mutants(self):
        recipe = lower("add", 1, 4)
        for mutated in (
            recipe[:-1],
            [*recipe[:1], ("double", 2), *recipe[2:]],
            [*recipe[:-2], ("add", 0, 2, -1), recipe[-1]],
        ):
            with self.subTest(recipe=mutated), self.assertRaises(ValueError):
                certify("add", 1, 4, mutated)

    def test_serialized_output_and_real_register_mutants(self):
        events = [
            ["phase", "test"],
            ["scalar", ["add", ["L", 22], ["Z", 230], 1, 4], 17],
            ["scalar", ["scale", ["L", 22], -1, 1], 17],
            ["phase", "done"],
        ]
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "expanded.json.gz"
            row = materialize(events, output)
            expanded = read(output)
            self.assertEqual(row["real_instructions"], 12)
            self.assertEqual(check_expansion(events, expanded), 4)
            mutants = []
            wrong = copy.deepcopy(expanded)
            wrong[1][1][2] = ["L", 22, 0]
            mutants.append(wrong)
            wrong = copy.deepcopy(expanded)
            wrong[1][2] = 18
            mutants.append(wrong)
            wrong = copy.deepcopy(expanded)
            wrong[5][1] = ["neg", ["K", 0, 0]]
            mutants.append(wrong)
            wrong = copy.deepcopy(expanded)
            wrong[-1] = ["phase", "wrong"]
            mutants.append(wrong)
            mutants.extend((expanded[:-1], [*expanded, ["phase", "extra"]]))
            for mutant in mutants:
                with self.subTest(mutant=mutant), self.assertRaises(ValueError):
                    check_expansion(events, mutant)

    def test_literal_checker_detects_uncleared_or_borrowed_state(self):
        events = [
            ["primitive", ["copy", ["K", 0, 0], ["L", 3, 0]], 1],
            ["primitive", ["half", ["K", 0, 0]], 1],
            ["primitive", ["add", ["L", 2, 0], ["K", 0, 0], 1], 1],
            ["primitive", ["clear", ["K", 0, 0]], 1],
        ]
        check_macro(events, "add", Q(1, 2), ["L", 2], ["L", 3], 0, 1)
        with self.assertRaisesRegex(ValueError, "scratch cleanup"):
            check_macro(events[:-1], "add", Q(1, 2), ["L", 2], ["L", 3], 0, 1)
        self.assertEqual(
            execute(lower("add", 1, 2), ((1, 0), (0, 1), (7, 0)))[2], (0, 0)
        )

    def test_word_preimages_and_no_unrelated_edits(self):
        parent = read(PACKAGE / "vendor/WORD-base.json.gz")
        child = produce(parent, "tariff")
        self.assertEqual(
            {k for k in parent if parent[k] != child[k]}, {"restore", "cleanup"}
        )
        self.assertEqual(
            child["restore"][177], ["scale", 22, -1, 1, [256, 128, 64, 38, 20, 10, 1]]
        )
        for section, index in (("restore", 175), ("cleanup", 33)):
            mutant = copy.deepcopy(parent)
            mutant[section][index][3] = 19
            with (
                self.subTest(section=section),
                self.assertRaisesRegex(ValueError, "preimage"),
            ):
                produce(mutant, "tariff")

    def test_source_inventory_and_hash_controls(self):
        self.assertEqual(authenticate(), 6)
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory) / "package"
            shutil.copytree(PACKAGE / "vendor", package / "vendor")
            for name in ("VENDOR.json", "SOURCES.json"):
                shutil.copyfile(PACKAGE / name, package / name)
            self.assertEqual(authenticate(package, ROOT), 6)
            word = package / "vendor/WORD-base.json.gz"
            word.write_bytes(word.read_bytes() + b"mutant")
            with self.assertRaisesRegex(ValueError, "source hash"):
                authenticate(package, ROOT)
            data = json.loads((package / "VENDOR.json").read_text())
            data["files"].pop()
            (package / "VENDOR.json").write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "complete frozen inventory"):
                authenticate(package, ROOT)

    def test_existing_workspace_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            sentinel = path / "keep.txt"
            sentinel.write_text("preserved", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                audit(path)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserved")


if __name__ == "__main__":
    unittest.main()
