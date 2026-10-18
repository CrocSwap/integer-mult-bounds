# SPDX-License-Identifier: Apache-2.0
"""Read-only controls for the explicit-subset frame invoice.

Every semantic negative control changes an actual decoded input, not a stored
success marker. Runtime safety predicates are explicit checks in frames.py.
"""

import copy
import gzip
import importlib.util
import json
from pathlib import Path
import unittest


PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("normal45_independent_frames", PACKAGE / "frames.py")
FRAMES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FRAMES)


class FrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.words = {
            stem: json.loads(gzip.decompress((PACKAGE / "inputs" / f"{stem}.json.gz").read_bytes()))
            for stem in ("WORD-base", "WORD-extra", "PARENT-base", "PARENT-extra")
        }

    def reject(self, word, predicate):
        with self.assertRaises(FRAMES.FrameError) as caught:
            FRAMES.analyze(word)
        self.assertEqual(caught.exception.predicate, predicate)

    def candidate(self):
        return copy.deepcopy(self.words["WORD-base"])

    def test_four_pinned_word_invoices(self):
        for stem, word in self.words.items():
            with self.subTest(stem=stem):
                result = FRAMES.analyze(word)
                final = stem.startswith("WORD")
                self.assertEqual(result["profile"],
                                 {1: 2434, 2: 632, 3: 286, 4: 104, 5: 26, 8: 8} if final else
                                 {1: 2416, 2: 640, 3: 280, 4: 110, 5: 26, 8: 8})
                self.assertEqual(result["width_inventory"],
                                 {4: 26, 5: 2, 7: 62, 8: 100, 9: 218} if final else
                                 {4: 26, 5: 2, 7: 62, 8: 96, 9: 222})
                self.assertEqual(result["helper_count"], 408)
                self.assertEqual(result["endpoint_count"], 632)
                self.assertEqual(result["buffer_count"], 86 if final else 82)
                self.assertEqual(result["warp_checks"], {"A": 24, "B": 72})
                self.assertEqual(result["center_descents"], 8)
                self.assertEqual(result["center_count"], 8)
                self.assertEqual(result["helper_ids"], sorted(result["helper_ids"]))
                self.assertEqual(len(result["widths"]), len(result["helper_ids"]))
                self.assertEqual(sum(result["widths"]), 3310 if final else 3314)
                self.assertEqual(sum(rank * count for rank, count in result["profile"].items()),
                                 5166 if final else 5170)

    def test_only_four_ordered_helper_widths_change(self):
        parent = FRAMES.analyze(self.words["PARENT-base"])
        changed = FRAMES.analyze(self.words["WORD-base"])
        self.assertEqual(parent["helper_ids"], changed["helper_ids"])
        difference = [(helper, before, after) for helper, before, after in zip(
            parent["helper_ids"], parent["widths"], changed["widths"]) if before != after]
        self.assertEqual(difference, [(249, 9, 8), (251, 9, 8), (265, 9, 8), (267, 9, 8)])

    def test_equal_dimension_wrong_scalar_subspace(self):
        word = self.candidate()
        self.assertEqual(word["A"][13][-1], [45])
        word["A"][13][-1] = [46]
        self.assertEqual(FRAMES._dimension(FRAMES._span([45], "test")),
                         FRAMES._dimension(FRAMES._span([46], "test")))
        self.reject(word, "frame_containment")

    def test_omitted_terminal_override_leaves_stale_cleanup(self):
        word = self.candidate()
        del word["helper_final"]["249"]
        self.reject(word, "cleanup_namespace")

    def test_incompatible_terminal_endpoint(self):
        word = self.candidate()
        word["helper_final"]["249"] = []
        self.reject(word, "frame_containment")

    def test_omitted_endpoint_charge_in_actual_report(self):
        word = self.candidate()
        word["report"]["local_profile"]["1"] -= 1
        self.reject(word, "declared_profile")

    def test_missing_cleanup_private_name(self):
        word = self.candidate()
        for gate in word["cleanup"]:
            for position in ([1, 2] if gate[0] == "add" else [1]):
                if gate[position] == 704 + 249:
                    gate[position] = 249
        self.reject(word, "cleanup_namespace")

    def test_missing_cleanup_full_frame(self):
        word = self.candidate()
        word["cleanup"][0][-1] = []
        self.reject(word, "cleanup_frame")

    def test_missing_cleanup_frame_field(self):
        word = self.candidate()
        word["cleanup"][0].pop()
        self.reject(word, "primitive_schema")

    def test_cleanup_inverse_coefficient(self):
        word = self.candidate()
        word["cleanup"][0][3] *= -1
        self.reject(word, "cleanup_inverse_syntax")

    def test_cleanup_inverse_order(self):
        word = self.candidate()
        word["cleanup"][0], word["cleanup"][1] = word["cleanup"][1], word["cleanup"][0]
        self.reject(word, "cleanup_inverse_syntax")

    def test_cleanup_excluded_prelude_boundary(self):
        word = self.candidate()
        word["prelude_events"] -= 1
        self.reject(word, "cleanup_inverse_syntax")

    def test_wrong_warp_subspace(self):
        word = self.candidate()
        word["warps"][0][4] = [320, 192, 45, 31]
        self.assertEqual(FRAMES._dimension(FRAMES._span(word["warps"][0][3], "test")),
                         FRAMES._dimension(FRAMES._span(word["warps"][0][4], "test")))
        self.reject(word, "warp_map")

    def test_noninvertible_warp(self):
        word = self.candidate()
        word["warps"][0][2][0] = word["warps"][0][2][1]
        self.reject(word, "warp_invertibility")

    def test_changed_warp_schedule(self):
        word = self.candidate()
        word["warps"][0][0] = 1000
        self.reject(word, "frame_containment")

    def test_warp_frame_equal_rank_wrong_preimage(self):
        word = self.candidate()
        warp = word["warps"][0]
        warp[3] = [384, 133, 85, 44]
        warp[4] = sorted(FRAMES._linear_image(FRAMES._span(warp[3], "test"), warp[2]))
        self.reject(word, "warp_frame")

    def test_changed_center_frame(self):
        word = self.candidate()
        word["center_frames"][0] = []
        self.reject(word, "center_frame")

    def test_outside_center_descent(self):
        word = self.candidate()
        word["target_levels"]["0"] = list(range(1, 512))
        self.reject(word, "center_descent")

    def test_false_and_nondyadic_scalars_are_rejected(self):
        for value in (False, 3):
            with self.subTest(value=value):
                word = self.candidate()
                word["A"][13][4] = value
                self.reject(word, "primitive_schema")

    def test_forged_width_inventory(self):
        word = self.candidate()
        word["report"]["width_inventory"]["8"] -= 1
        self.reject(word, "declared_width_inventory")

    def test_redundant_generators_preserve_invoice(self):
        word = self.candidate()
        word["A"][13][-1] = [0, 45, 45]
        word["cleanup"][0][-1] = list(reversed(word["cleanup"][0][-1])) + [0]
        self.assertEqual(FRAMES.analyze(word), FRAMES.analyze(self.words["WORD-base"]))

    def test_equivalent_scalar_representation_preserves_invoice(self):
        word = self.candidate()
        word["cleanup"][0][3] *= 2
        word["cleanup"][0][4] *= 2
        self.assertEqual(FRAMES.analyze(word), FRAMES.analyze(self.words["WORD-base"]))

    def test_analyze_does_not_mutate_word(self):
        word = self.candidate()
        before = copy.deepcopy(word)
        FRAMES.analyze(word)
        self.assertEqual(word, before)


if __name__ == "__main__":
    unittest.main()
