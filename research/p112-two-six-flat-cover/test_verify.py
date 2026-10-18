"""Behavioral and mathematical failure controls for the fifteen-line theorem."""

import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import verify
from cover import exact_pair_cap, rank, set_bits
from independent import check_witness
from vendor.geometry import root_data


class CoverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = verify.bind_sources()
        cls.roots, cls.points, cls.labels, _ = root_data()
        cls.result = json.loads(verify.read_file(verify.PACKAGE / "RESULT.json"))

    def test_all_literal_attaining_covers(self):
        rows = self.result["root_covers"]
        self.assertEqual([tuple(r["normal"]) for r in rows], list(self.roots))
        self.assertEqual(
            sorted(r["minimum_extra"] for r in rows), [15] * 112 + [18] * 8
        )
        self.assertTrue(
            all(check_witness(self.points, self.labels, row) for row in rows)
        )

    def test_pair_pruning_against_all_small_inventory_unions(self):
        universe = (0, 1, 2, 3, 5, 8, 10, 12)
        for choice in range(1, 256):
            family = tuple(x for i, x in enumerate(universe) if choice >> i & 1)
            cap = max(x.bit_count() for x in family)
            target = max((a | b).bit_count() for a in family for b in family)
            witness, _, _ = exact_pair_cap(family, cap, target)
            self.assertEqual((witness[0] | witness[1]).bit_count(), target)
            if target:
                with self.assertRaises(ValueError):
                    exact_pair_cap(family, cap, target - 1)

    def test_a_thirty_nine_coordinate_pair_is_rejected(self):
        family = ((1 << 20) - 1, ((1 << 20) - 1) << 19)
        with self.assertRaisesRegex(ValueError, "exceeds bound"):
            exact_pair_cap(family)

    def test_a_thirty_eight_coordinate_pair_attains(self):
        family = ((1 << 20) - 1, ((1 << 20) - 1) << 18)
        witness, _, _ = exact_pair_cap(family)
        self.assertEqual((witness[0] | witness[1]).bit_count(), 38)

    def test_false_single_flat_cap_and_false_sharpness(self):
        with self.assertRaisesRegex(ValueError, "single-flat cap"):
            exact_pair_cap(((1 << 21) - 1,))
        with self.assertRaisesRegex(ValueError, "not sharp"):
            exact_pair_cap(((1 << 20) - 1,))

    def test_bounds_and_capacity(self):
        for family, cap, target in (
            ((), 20, 38),
            ((-1,), 20, 38),
            ((1 << 112,), 20, 38),
            ((0,), -1, 0),
            ((0,), 20, 41),
        ):
            with self.assertRaises(ValueError):
                exact_pair_cap(family, cap, target)
        with self.assertRaisesRegex(ValueError, "inventory capacity"):
            exact_pair_cap((0,) * 776807)
        with self.assertRaises(ValueError):
            set_bits(1 << 112)
        with self.assertRaises(ValueError):
            rank((512,))

    def test_literal_witness_tampering(self):
        original = self.result["root_covers"][0]
        for key in ("flat_lines", "extra_lines"):
            row = copy.deepcopy(original)
            if key == "flat_lines":
                row[key][0] = row[key][0][1:]
            else:
                row[key] = row[key][1:]
            with self.assertRaises(ValueError):
                check_witness(self.points, self.labels, row)

    def test_live_bytes_and_semantic_label_and_root_changes(self):
        raw = verify.read_file(verify.ROOT / verify.DATA)
        self.assertEqual(
            verify.bind_data(raw, self.points, self.labels, self.sources),
            self.result["input_sha256"],
        )
        with self.assertRaisesRegex(ValueError, "source bytes"):
            verify.bind_data(raw + b"\n", self.points, self.labels, self.sources)
        lines = raw.decode().splitlines()
        for index in (0, 2):
            changed = lines.copy()
            values = changed[index].split()
            values[0] = str(int(values[0]) + 1)
            changed[index] = " ".join(values)
            mutant = ("\n".join(changed) + "\n").encode()
            pins = copy.deepcopy(self.sources)
            next(r for r in pins["files"] if r["usage"] == "input")["sha256"] = (
                hashlib.sha256(mutant).hexdigest()
            )
            with self.assertRaises(ValueError):
                verify.bind_data(mutant, self.points, self.labels, pins)

    def test_retained_source_bytes_and_symlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            shutil.copytree(verify.PACKAGE / "vendor", package / "vendor")
            shutil.copyfile(verify.PACKAGE / "SOURCES.json", package / "SOURCES.json")
            geometry = package / "vendor/geometry.py"
            geometry.chmod(0o644)  # This temporary copy belongs to the test.
            geometry.write_bytes(geometry.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "source bytes"):
                verify.bind_sources(package)
            geometry.unlink()
            geometry.symlink_to(verify.PACKAGE / "vendor/geometry.py")
            with self.assertRaisesRegex(ValueError, "linked"):
                verify.bind_sources(package)

    def test_committed_receipt_tampering(self):
        mutant = copy.deepcopy(self.result)
        mutant["minimum_extra_lines"] = 14
        with self.assertRaisesRegex(ValueError, "receipt differs"):
            verify.check_receipt(mutant, self.result)

    def test_output_is_external_and_never_overwrites(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            verify.write_result({}, verify.PACKAGE / "unexpected.json")
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            verify.write_result({"control": 1}, target)
            self.assertEqual(json.loads(target.read_text()), {"control": 1})
            with self.assertRaises(FileExistsError):
                verify.write_result({"control": 2}, target)
            self.assertEqual(json.loads(target.read_text()), {"control": 1})

    def test_the_actual_preferred_basis_implication(self):
        row = verify.application()
        self.assertEqual(row["basis_support_cap"], 54)
        self.assertEqual(row["minimum_five_piece_support_cap"], 54)
        self.assertEqual(row["extra_cap"], 14)
        self.assertLess(row["extra_cap"], self.result["minimum_extra_lines"])
        self.assertEqual(row["remaining_weights"], (6,) * 6)


if __name__ == "__main__":
    unittest.main()
