# SPDX-License-Identifier: GPL-3.0-or-later
"""Literal traces independently tabulated from the retained GCC C branches."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().with_name("gcc13_prefix_visits_v1.py")
SPEC = importlib.util.spec_from_file_location("new_gcc13_prefix_visits", MODULE)
prefix = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prefix)


def run(rows=(("P/", 0, False),), machine="M/V/", just="M/",
        multi=None, os_multi=None, arch=None, do_multi=False):
    return list(prefix.gcc13_prefix_visits(rows, machine, just, multi, os_multi, arch, do_multi))


class PrefixTests(unittest.TestCase):
    def test_require_zero_one_two_one_pass_literal_trace(self):
        self.assertEqual(run((("A/", 0, False), ("B/", 1, False), ("C/", 2, True)), arch="ARCH"),
                         ["A/M/V/", "A/ARCH/", "A/", "B/M/V/", "C/M/V/", "C/M/"])

    def test_both_multilib_paths_two_passes_and_arch_order(self):
        self.assertEqual(run((("A/", 0, False), ("B/", 0, True), ("C/", 2, True)),
                             multi="32", os_multi="../lib32", arch="ARCH", do_multi=True),
                         ["A/M/V/32/", "A/ARCH/", "A/32/",
                          "B/M/V/32/", "B/ARCH/", "B/../lib32/",
                          "C/M/V/32/", "C/M/32/",
                          "A/M/V/", "A/ARCH/", "A/",
                          "B/M/V/", "B/ARCH/", "B/", "C/M/V/", "C/M/"])

    def test_only_os_multilib_skips_machine_arch_and_non_os_base_second_pass(self):
        self.assertEqual(run((("A/", 0, False), ("B/", 0, True),
                              ("C/", 1, True), ("D/", 2, False)),
                             multi=None, os_multi="OS", arch="ARCH", do_multi=True),
                         ["A/M/V/", "A/ARCH/", "A/", "B/M/V/", "B/ARCH/", "B/OS/",
                          "C/M/V/", "D/M/V/", "D/M/", "B/"])

    def test_only_compiler_multilib_skips_os_base_second_pass(self):
        self.assertEqual(run((("A/", 0, False), ("B/", 0, True)),
                             multi="32", os_multi=None, arch="ARCH", do_multi=True),
                         ["A/M/V/32/", "A/ARCH/", "A/32/", "B/M/V/32/", "B/ARCH/", "B/",
                          "A/M/V/", "A/ARCH/", "A/", "B/M/V/", "B/ARCH/"])

    def test_null_and_empty_compiler_multilib_are_unequal(self):
        self.assertEqual(run(multi=None, do_multi=True), ["P/M/V/", "P/"])
        self.assertEqual(run(multi="", do_multi=True), ["P/M/V//", "P//", "P/M/V/", "P/"])

    def test_null_and_empty_os_multilib_are_unequal(self):
        rows = (("P/", 0, True),)
        self.assertEqual(run(rows, os_multi=None, do_multi=True), ["P/M/V/", "P/"])
        self.assertEqual(run(rows, os_multi="", do_multi=True), ["P/M/V/", "P//", "P/"])

    def test_asymmetric_empty_compiler_and_dot_os(self):
        self.assertEqual(run((("A/", 0, False), ("B/", 0, True)),
                             multi="", os_multi=".", do_multi=True),
                         ["A/M/V//", "A//", "B/M/V//", "B/", "A/M/V/", "A/", "B/M/V/"])

    def test_asymmetric_dot_compiler_and_empty_os(self):
        self.assertEqual(run((("A/", 0, False), ("B/", 0, True)),
                             multi=".", os_multi="", do_multi=True),
                         ["A/M/V/", "A/", "B/M/V/", "B//", "B/"])

    def test_dot_multilib_suppresses_second_pass(self):
        self.assertEqual(run(multi=".", os_multi=".", do_multi=True), ["P/M/V/", "P/"])

    def test_multiarch_null_empty_dot_distinction(self):
        self.assertEqual(run(arch=None), ["P/M/V/", "P/"])
        self.assertEqual(run(arch=""), ["P/M/V/", "P//", "P/"])
        self.assertEqual(run(arch="."), ["P/M/V/", "P/./", "P/"])

    def test_do_multi_false_ignores_multilib_but_keeps_multiarch(self):
        self.assertEqual(run(multi="32", os_multi="OS", arch="ARCH", do_multi=False),
                         ["P/M/V/", "P/ARCH/", "P/"])

    def test_duplicate_prefixes_and_equal_suffix_visits_are_not_deduplicated(self):
        self.assertEqual(run((("P/", 2, False), ("P/", 2, False)), machine="M/", just="M/"),
                         ["P/M/", "P/M/", "P/M/", "P/M/"])

    def test_literal_dotdot_and_repeated_separators_are_not_normalized(self):
        self.assertEqual(run((("/usr/lib/../lib//", 0, False),), multi="../lib32", do_multi=True),
                         ["/usr/lib/../lib//M/V/../lib32/", "/usr/lib/../lib//../lib32/",
                          "/usr/lib/../lib//M/V/", "/usr/lib/../lib//"])

    def test_empty_prefix_and_suffixes_remain_visits(self):
        self.assertEqual(run((("", 0, False),), machine="", just="", arch=""), ["", "/", ""])
        self.assertEqual(run(()), [])

    def test_each_required_policy_in_two_passes(self):
        self.assertEqual(run((("A/", 1, False), ("B/", 2, True)), multi="32", do_multi=True),
                         ["A/M/V/32/", "B/M/V/32/", "B/M/32/", "A/M/V/", "B/M/V/", "B/M/"])

    def test_eager_whole_input_validation_precedes_any_emission(self):
        with self.assertRaisesRegex(prefix.QueryFrontierLimit, "machine-suffix"):
            prefix.gcc13_prefix_visits((("first/", 0, False), ("bad/", 3, False)),
                                       "M/", "M/", None, None, None, False)

    def test_exact_row_scalar_and_tuple_types(self):
        bad_rows = ([('P/', 0, False)], (("P/", True, False),),
                    (("P/", 0, 1),), (("P/", -1, False),), (("P/", 0),),
                    (("nul\0", 0, False),))
        for rows in bad_rows:
            with self.subTest(rows=rows), self.assertRaises(prefix.QueryFrontierLimit):
                run(rows)
        with self.assertRaises(prefix.QueryFrontierLimit):
            run(do_multi=1)
        with self.assertRaises(prefix.QueryFrontierLimit):
            run(machine=None)

    def test_no_str_subclass_callbacks(self):
        class Hostile(str):
            def __len__(self):
                raise RuntimeError("callback")
        with self.assertRaises(prefix.QueryFrontierLimit):
            run(machine=Hostile("M/"))

    def test_expanded_string_and_suffix_slash_bounds(self):
        with self.assertRaisesRegex(prefix.QueryFrontierLimit, "per-string"):
            run((("P", 1, False),), machine="M" * 8192)
        with self.assertRaisesRegex(prefix.QueryFrontierLimit, "per-string"):
            run(multi="M" * 8192, do_multi=True)
        with self.assertRaisesRegex(prefix.QueryFrontierLimit, "per-string"):
            run(arch="A" * 8192)

    def test_input_count_and_aggregate_bounds(self):
        with self.assertRaises(prefix.QueryFrontierLimit):
            run((("", 1, False),) * 1025)
        with self.assertRaisesRegex(prefix.QueryFrontierLimit, "aggregate"):
            run((("P" * 8192, 1, False),) * 65)

    def test_output_count_limit_is_frontier_not_silent_exhaustion(self):
        self.assertEqual(len(run((("", 0, False),) * 512, machine="", just="")), 1024)
        iterator = prefix.gcc13_prefix_visits((("", 0, False),) * 513,
                                             "", "", None, None, None, False)
        self.assertEqual(len([next(iterator) for _ in range(1024)]), 1024)
        with self.assertRaisesRegex(prefix.QueryFrontierLimit, "output bound"):
            next(iterator)

    def test_output_aggregate_limit_before_next_spelling(self):
        self.assertEqual(len(run((("P" * 2048, 0, False),) * 128, machine="", just="")), 256)
        with self.assertRaisesRegex(prefix.QueryFrontierLimit, "output bound"):
            run((("P" * 2048, 0, False),) * 129, machine="", just="")


if __name__ == "__main__":
    unittest.main()
