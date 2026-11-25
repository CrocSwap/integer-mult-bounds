#!/usr/bin/env python3
"""Independent helper-lifetime regression cases; run with python -B test_verify.py."""

import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SPEC = importlib.util.spec_from_file_location("helper_lifetime_verify", HERE / "verify.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


def small_word():
    """One cold helper ends at a two-dimensional subspace of GF(2)^3."""
    return {
        "h": 3,
        "v": 1,
        "R": 1,
        "frames": [[], [4, 2, 1], [4, 2], [4], [1]],
        "start": [0, 0, 0],
        "final": [1, 1, 2],
        "precondition": [],
        "compensation": [],
        "A": [],
        "B": [],
        "cut": [],
        "tail": [["scale", 2, 1, 1, 2]],
        "cleanup": [],
        "centers": [],
        "center_frames": [],
    }


def frozen_word(provider):
    path = (
        ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers"
        / provider / "CANONICAL-WORD.json.gz"
    )
    return json.loads(gzip.decompress(path.read_bytes()))


class HelperLifetimeTests(unittest.TestCase):
    def reject(self, word):
        with self.assertRaises(ValueError):
            VERIFY.check_word(word)

    def test_valid_cold_helper(self):
        self.assertIsInstance(VERIFY.check_word(small_word()), dict)

    def test_valid_monotone_multigate_lifetime(self):
        word = small_word()
        word["A"] = [["scale", 2, 1, 1, 3]]
        word["B"] = [["scale", 2, 1, 1, 2]]
        VERIFY.check_word(word)

    def test_semantically_equivalent_bases(self):
        word = small_word()
        word["frames"].append([6, 2])
        word["A"] = [["scale", 2, 1, 1, 5]]
        VERIFY.check_word(word)

    def test_earlier_full_tail_frame_then_proper_terminal(self):
        word = small_word()
        word["tail"].insert(0, ["scale", 2, 1, 1, 1])
        self.reject(word)

    def test_equal_rank_incomparable_frames(self):
        word = small_word()
        word["A"] = [["scale", 2, 1, 1, 3]]
        word["B"] = [["scale", 2, 1, 1, 4]]
        self.reject(word)

    def test_final_climb_cannot_descend(self):
        word = small_word()
        word["tail"] = [["scale", 2, 1, 1, 1]]
        self.reject(word)

    def test_negative_register_is_not_python_index(self):
        word = small_word()
        word["tail"][0][1] = -1
        self.reject(word)

    def test_out_of_range_register(self):
        word = small_word()
        word["tail"][0][1] = len(word["start"])
        self.reject(word)

    def test_invalid_earlier_frame_not_hidden_by_last_touch(self):
        for frame in (-1, 999):
            with self.subTest(frame=frame):
                word = small_word()
                word["tail"].insert(0, ["scale", 2, 1, 1, frame])
                self.reject(word)

    def test_zero_denominator(self):
        word = small_word()
        word["tail"][0][3] = 0
        self.reject(word)

    def test_malformed_gate(self):
        word = small_word()
        word["tail"] = [["add", 2, 0, 2]]
        self.reject(word)

    def test_pre_wrapper_touch_of_cold_or_entering_helper(self):
        for section in ("precondition", "compensation"):
            for entrance in (0, 3):
                with self.subTest(section=section, entrance=entrance):
                    word = small_word()
                    word["start"][2] = entrance
                    word[section] = [["scale", 2, 1, 1, 0]]
                    self.reject(word)

    def test_cleanup_add_cannot_read_early_ended_helper(self):
        word = small_word()
        word["cleanup"] = [["add", 0, 2, 1, 1, 1]]
        self.reject(word)

    def test_cleanup_add_cannot_write_early_ended_helper(self):
        word = small_word()
        word["cleanup"] = [["add", 2, 0, 1, 1, 1]]
        self.reject(word)

    def test_cleanup_scale_cannot_touch_early_ended_helper(self):
        word = small_word()
        word["cleanup"] = [["scale", 2, 1, 1, 1]]
        self.reject(word)

    def test_frozen_pr626_providers(self):
        for provider in ("ck", "jp8"):
            with self.subTest(provider=provider):
                VERIFY.check_word(frozen_word(provider))

    def test_frozen_ck_frame_mutation_preserves_scalar_program(self):
        original = frozen_word("ck")
        self.assertEqual(original["tail"][34], ["add", 234, 0, -1, 2, 52])
        word = copy.deepcopy(original)
        word["tail"][34][-1] = 1
        self.assertEqual(
            [gate[:-1] for gate in original["tail"]],
            [gate[:-1] for gate in word["tail"]],
        )
        self.reject(word)


if __name__ == "__main__":
    unittest.main(verbosity=2)
