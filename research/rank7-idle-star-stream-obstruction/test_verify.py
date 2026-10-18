"""Behavioral controls for literal source binding and physical-stream equality."""

import copy
import json
import unittest
from unittest.mock import patch

import source
import verify
from algebra import (
    apply_overlay,
    data_event,
    host_projection,
    identity,
    intertwines,
    intervening_events,
    phase,
    replay,
    shear,
)
from source import BASE_ROWS, PACKAGE, decode, journal_edits, load_context, read_bytes


class StreamControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = load_context()
        _, cls.original = host_projection(cls.context)
        cls.changed = apply_overlay(
            cls.context["recipe"], cls.original, cls.context["moves"]
        )

    def test_current_overlay_leaks_from_y0_to_y1(self):
        before = replay(self.context, self.original, 16)
        after = replay(self.context, self.changed, 16)
        self.assertEqual(before[3][1], (0, 0))
        self.assertEqual(after[3][1], (-1, -1))

    def test_inactive_characters_preserve_the_operator(self):
        for character in (0, 1, 2, 4, 8):
            self.assertEqual(
                replay(self.context, self.original, character),
                replay(self.context, self.changed, character),
            )

    def test_first_move_alone_has_the_same_active_failure(self):
        single = apply_overlay(
            self.context["recipe"], self.original, self.context["moves"][:1]
        )
        self.assertEqual(
            replay(self.context, single, 16), replay(self.context, self.changed, 16)
        )

    def test_undo_restores_the_actual_operator(self):
        restored = copy.deepcopy(self.changed)
        for _, _, donor, receiver, axes in reversed(self.context["moves"]):
            for axis in axes:
                restored[receiver].remove(axis)
                restored[donor].append(axis)
        self.assertEqual(
            replay(self.context, restored, 16), replay(self.context, self.original, 16)
        )

    def test_identity_does_not_transport_phases_between_streams(self):
        self.assertFalse(intertwines(identity(), 7, 0))
        self.assertTrue(intertwines(identity(), 0, 0))
        self.assertTrue(intertwines(identity(), 7, 0, exponent=0))

    def test_real_stream_exchange_transports_the_projector(self):
        matrix = identity()
        matrix[0], matrix[7] = matrix[7], matrix[0]
        self.assertTrue(intertwines(matrix, 7, 0))
        self.assertFalse(intertwines(matrix, 7, 1))

    def test_shear_does_not_transport_the_projector(self):
        matrix = identity()
        shear(matrix, 0, 7, 1)
        self.assertFalse(intertwines(matrix, 7, 0))

    def test_actual_interval_fails_the_guard(self):
        matrix = identity()
        for event in intervening_events(self.context["template"]):
            data_event(matrix, event, self.context, self.original, 16)
        self.assertFalse(intertwines(matrix, 7, 0))
        for exponent in range(4):
            varied = [list(row) for row in matrix]
            phase(varied, 0, exponent)
            self.assertFalse(intertwines(varied, 7, 0))

    def test_intervening_bridge_on_x0_invalidates_the_short_proof(self):
        template = copy.deepcopy(self.context["template"])
        event = next(e for e in intervening_events(template) if e["kind"] == "bridge")
        event["dst"] = 0
        with self.assertRaisesRegex(ValueError, "X0 mixed"):
            intervening_events(template)

    def test_intervening_local_on_x0_invalidates_the_short_proof(self):
        template = copy.deepcopy(self.context["template"])
        event = next(e for e in template["recipe"] if e.get("stage") == 6)
        event["pair"] = 0
        with self.assertRaisesRegex(ValueError, "X0 mixed"):
            intervening_events(template)

    def test_foreign_axis_is_rejected(self):
        moves = copy.deepcopy(self.context["moves"])
        moves[0][4][0] = 1 << 80
        with self.assertRaisesRegex(ValueError, "axis ownership"):
            apply_overlay(self.context["recipe"], self.original, moves)

    def test_duplicate_axis_is_rejected(self):
        moves = copy.deepcopy(self.context["moves"])
        moves[1][4] = list(moves[0][4])
        with self.assertRaisesRegex(ValueError, "axis ownership"):
            apply_overlay(self.context["recipe"], self.original, moves)

    def test_noncommuting_axis_is_rejected(self):
        moves = copy.deepcopy(self.context["moves"])
        moves[0][4][0] = next(
            v
            for v in self.original[10]
            if any((v & w).bit_count() % 2 for w in self.original[12])
        )
        with self.assertRaisesRegex(ValueError, "commuting rule"):
            apply_overlay(self.context["recipe"], self.original, moves)

    def test_duplicate_hosted_slice_is_rejected(self):
        context = dict(
            self.context, rows=self.context["rows"] + self.context["rows"][:1]
        )
        with self.assertRaisesRegex(ValueError, "hosted slice overlap"):
            host_projection(context)

    def test_hosted_prefix_hole_is_rejected(self):
        rows = copy.deepcopy(self.context["rows"])
        # Remove the first slice of a bin while retaining a later slice.
        first = next(
            i
            for i, row in enumerate(rows)
            if row[5] == 0 and any(r[3] == row[3] and r[5] > 0 for r in rows)
        )
        del rows[first]
        with self.assertRaisesRegex(ValueError, "compact hosted prefix"):
            host_projection(dict(self.context, rows=rows))

    def test_journal_preimage_and_duplicate_edits_are_rejected(self):
        base = decode(read_bytes(PACKAGE / "vendor/BASE-FILL.json.gz"))["rows"]
        journal = decode(read_bytes(PACKAGE / "vendor/EXCHANGE.json"))
        bad = copy.deepcopy(journal)
        bad["edits"][0][1][2] += 1
        with self.assertRaisesRegex(ValueError, "journal preimage"):
            journal_edits(base, bad)
        bad = copy.deepcopy(journal)
        bad["edits"][-1] = bad["edits"][0]
        with self.assertRaisesRegex(ValueError, "duplicate journal edit"):
            journal_edits(base, bad)
        self.assertEqual(len(base), BASE_ROWS)

    def test_invalid_character_and_stream_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "Fourier character"):
            replay(self.context, self.original, 1 << 73)
        with self.assertRaisesRegex(ValueError, "physical stream index"):
            intertwines(identity(), 8, 0)

    def test_changed_live_and_vendor_bytes_fail_before_replay(self):
        metadata = decode(read_bytes(PACKAGE / "SOURCES.json"))
        files = [
            source.ROOT / row["path"]
            for row in metadata["files"]
            if row["usage"] == "input"
        ]
        files += [PACKAGE / row["local_path"] for row in metadata["retained_files"]]
        original = source.read_bytes
        for changed in files:
            with self.subTest(changed=changed):

                def read_changed(path, changed=changed):
                    raw = original(path)
                    return raw + b"\n" if path == changed else raw

                with (
                    patch("source.read_bytes", side_effect=read_changed),
                    self.assertRaisesRegex(ValueError, "source pin"),
                ):
                    source.authenticate()

    def test_corrupted_receipt_is_rejected(self):
        result = json.loads(read_bytes(PACKAGE / "RESULT.json"))
        result["overlay"][3][1] = [0, 0]
        with (
            patch("verify.read_bytes", return_value=json.dumps(result).encode()),
            patch("verify.load_context", return_value=self.context),
            patch("sys.argv", ["verify.py"]),
            self.assertRaisesRegex(ValueError, "stored receipt differs"),
        ):
            verify.main()


if __name__ == "__main__":
    unittest.main()
