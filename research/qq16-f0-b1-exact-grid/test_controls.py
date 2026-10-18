"""Behavioral and boundary controls for the uniform component proof."""

import copy
import itertools
import json
import unittest
from fractions import Fraction as Q
from unittest.mock import patch

import sources
import verify


class Controls(unittest.TestCase):
    def test_all_small_gaussian_pairs(self):
        # Direct complex arithmetic, independent of the envelope recurrence.
        # A Gaussian line is ((s+i*d)/2, (d+i*s)/2), s=a+b, d=a-b.
        for values in itertools.product(range(-2, 3), repeat=4):
            ar, ai, br, bi = map(Q, values)
            sr, si, dr, di = ar + br, ai + bi, ar - br, ai - bi
            numerators = (sr - di, si + dr, dr - si, di + sr)
            for numerator in numerators:
                self.assertLessEqual(abs(numerator), 8)
                self.assertLessEqual(abs(numerator / 2), 4)
                self.assertEqual((numerator / 2 * 2).denominator, 1)
        # A half-integer output demonstrates why omitting the division fails.
        self.assertEqual(Q(1, 2).denominator, 2)

    def test_actual_carried_state_is_not_a_reset(self):
        packet, recipes, residuals = sources.load()
        children = {(r["old"], r["new"]): r for r in recipes["children"]}
        adapters = {(r["role"], r["port"]): r for r in recipes["endpoint_adapters"]}
        state = [verify.ref.UNIT] * 704 + [verify.ref.ZERO] * 8
        ledger = verify.ref.Envelope()
        row = verify.run_stage(
            sources.expand(packet, "B_1_2"),
            state,
            ledger,
            packet,
            children,
            adapters,
            residuals,
            26099,
        )
        result = json.loads((sources.HERE / "RESULT.json").read_text())
        self.assertNotEqual(
            row["final_bounds_sha256"], result["stages"]["B_1_2"]["final_bounds_sha256"]
        )
        self.assertLess(ledger.max_grid, result["grid_guard"])

    def test_noninvertible_owner_map_rejected(self):
        packet, _, _ = sources.load()
        bad = copy.deepcopy(packet)
        bad["map_registry"]["m4"]["owner_right_matrix_columns"][0] = 0
        with self.assertRaisesRegex(ValueError, "invertible owner map"):
            verify.check_cover_maps(bad)

    def test_truncated_payload_translation_rejected(self):
        packet, _, _ = sources.load()
        bad = copy.deepcopy(packet)
        bad["map_registry"]["m4"]["payload_translation_at_identity_owner"] = 1 << 73
        with self.assertRaisesRegex(ValueError, "73-axis translation"):
            verify.check_cover_maps(bad)
        self.assertGreater(
            packet["map_registry"]["m4"]["payload_translation_at_identity_owner"], 511
        )

    def test_one_owner_substitution_rejected(self):
        packet, _, _ = sources.load()
        bad = copy.deepcopy(packet)
        bad["map_registry"]["m4"]["action"] = "out(z)=in(z XOR delta)"
        with self.assertRaisesRegex(ValueError, "full-cover action"):
            verify.check_cover_maps(bad)

    def test_private_clear_and_event_inventory(self):
        state = [verify.ref.UNIT] * 712
        with self.assertRaisesRegex(ValueError, "owned clear"):
            verify.scalar(verify.ref.Envelope(), state, ["clear", ["L", 0]])
        packet, _, _ = sources.load()
        bad = copy.deepcopy(packet)
        bad["programs"]["B_1_2"].pop()
        with self.assertRaisesRegex(ValueError, "event inventory"):
            sources.expand(bad, "B_1_2")
        # Reclassifying a live source as documentary must not bypass its hash.
        manifest_path = sources.HERE / "SOURCES.json"
        inventory = json.loads(manifest_path.read_text())
        original_read = sources.read
        for index in (2, 3):
            bad = copy.deepcopy(inventory)
            self.assertEqual(bad["files"][index]["usage"], "input")
            bad["files"][index]["usage"] = "provenance"
            with (
                patch.object(
                    sources,
                    "read",
                    side_effect=lambda path, cap, bad=bad: (
                        json.dumps(bad).encode()
                        if path == manifest_path
                        else original_read(path, cap)
                    ),
                ),
                self.assertRaisesRegex(ValueError, "fixed source inventory"),
            ):
                sources.authenticate()

    def test_grid_width_and_declared_scope(self):
        result = json.loads((sources.HERE / "RESULT.json").read_text())
        maximum = Q(result["max_range_exact"])
        self.assertGreater(maximum, 1 << 142)
        self.assertLess(maximum, 1 << 143)
        self.assertEqual(result["signed_width_P_plus"], 143 + 71 + 1)
        self.assertEqual(
            result["payload_dimension"], "N=2^73, exactly one tensor layer"
        )
        self.assertFalse(result["physical_routing_priced"])


if __name__ == "__main__":
    unittest.main()
