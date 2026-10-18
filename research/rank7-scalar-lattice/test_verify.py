# SPDX-License-Identifier: Apache-2.0
"""Behavioral controls for the exact source-bound reference envelopes."""

import copy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from audit import execute
from lattice import MAX_EVENTS, analyze
from verify import HERE, authenticate, compile_provider, read_json


def add(numerator, denominator=1):
    return ["scalar", ["add", ["L", 1], ["L", 0], numerator, denominator], 0]


class ReferenceControls(unittest.TestCase):
    def test_dyadic_dirty_target_and_inverse(self):
        result = analyze([add(1, 8), add(-1, 8)], inputs=2)
        self.assertEqual(result["fraction_bits"], 3)
        self.assertEqual(result["source_guard_bits"], 3)
        self.assertEqual(result["max_l1"], "9/8")
        self.assertEqual(execute([add(1, 8), add(-1, 8)], 3, False, 2), "9/8")
        with self.assertRaisesRegex(ValueError, "nonintegral encoded coefficient"):
            execute([add(1, 8), add(-1, 8)], 2, False, 2)

    def test_warp_words_must_not_collapse(self):
        events = [
            ["warp", ["L", 0], 7, 0, 0],
            add(1),
            ["warp", ["L", 0], -7, 0, 0],
            add(-1),
        ]
        with self.assertRaisesRegex(ValueError, "ordinary endpoint"):
            analyze(events, inputs=2)
        events[2], events[3] = events[3], events[2]
        self.assertEqual(analyze(events, inputs=2)["max_l1"], "2")
        self.assertEqual(execute(events, 0, False, 2), 2)

    def test_omitted_inverse_and_private_clear(self):
        with self.assertRaisesRegex(ValueError, "ordinary endpoint"):
            analyze([add(1)], inputs=2)
        events = [["scalar", ["copy", ["C", 0], ["L", 0]], 0]]
        with self.assertRaisesRegex(ValueError, "private endpoint"):
            analyze(events, inputs=2)
        events.append(["scalar", ["clear", ["C", 0]], 0])
        self.assertTrue(analyze(events, inputs=2)["complete_endpoint_checked"])

    def test_zero_source_needs_no_fraction_bits(self):
        events = [
            ["scalar", ["clear", ["C", 0]], 0],
            ["scalar", ["add", ["L", 1], ["C", 0], 1, 8], 0],
        ]
        result = analyze(events, inputs=2)
        self.assertEqual(result["fraction_bits"], 0)
        self.assertEqual(result["source_guard_bits"], 0)
        self.assertEqual(execute(events, 0, False, 2), 1)

    def test_nondyadic_and_zero_scale(self):
        with self.assertRaisesRegex(ValueError, "dyadic coefficient"):
            analyze([add(1, 3), add(-1, 3)], inputs=2)
        with self.assertRaisesRegex(ValueError, "nonzero scale"):
            analyze([["scalar", ["scale", ["L", 0], 0, 1], 0]], inputs=2)

    def test_limits_and_unsupported_event(self):
        with self.assertRaisesRegex(ValueError, "event count"):
            analyze([["phase", "x"]] * (MAX_EVENTS + 1), inputs=2)
        with self.assertRaisesRegex(ValueError, "role index"):
            analyze([["scalar", ["clear", ["L", 768]], 0]], inputs=2)
        with self.assertRaisesRegex(ValueError, "non-scalar kind"):
            analyze([["unpriced_new_operator", 0]], inputs=2)

    def test_dirty_and_duplicate_buffer(self):
        events = [
            ["zero_buffer", "alloc", 0],
            ["scalar", ["copy", ["Z", 0], ["L", 0]], 0],
            ["zero_buffer", "free", 0],
        ]
        with self.assertRaisesRegex(ValueError, "clean buffer return"):
            analyze(events, inputs=2)
        with self.assertRaisesRegex(ValueError, "unique buffer allocation"):
            analyze([["zero_buffer", "alloc", 0]] * 2, inputs=2)

    def test_source_bytes_are_checked(self):
        self.assertEqual(authenticate(), 8)
        with tempfile.TemporaryDirectory(prefix="rank7-lattice-source-control-") as raw:
            root = Path(raw)
            shutil.copytree(HERE / "vendor", root / "vendor")
            shutil.copyfile(HERE / "VENDOR.json", root / "VENDOR.json")
            source = root / "vendor/native/bw_emit.py"
            source.write_bytes(source.read_bytes() + b"\n# changed\n")
            with self.assertRaisesRegex(ValueError, "source hash"):
                authenticate(root)

    def test_occupied_output_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix="rank7-lattice-output-control-") as raw:
            path = Path(raw)
            sentinel = path / "keep"
            sentinel.write_text("keep", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(HERE / "verify.py"), "--work", str(path)],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("fresh work directory", result.stderr)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")


class CompleteWordControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory(prefix="rank7-lattice-native-control-")
        cls.addClassCleanup(cls.work.cleanup)
        cls.programs = compile_provider("base", Path(cls.work.name))

    def test_literal_word_and_insufficient_precision(self):
        for name, bits, mass in (("forward", 4, 302), ("backward", 5, 169)):
            with self.subTest(orientation=name):
                events = self.programs[name]
                self.assertEqual(execute(events, bits, name == "backward"), mass)
                with self.assertRaisesRegex(
                    ValueError, "nonintegral encoded coefficient"
                ):
                    execute(events, bits - 1, name == "backward")

    def test_real_word_semantic_mutation(self):
        events = copy.deepcopy(self.programs["forward"])
        index = next(
            i for i, e in enumerate(events) if e[0] == "scalar" and e[1][0] == "add"
        )
        events[index][1][3] *= -1
        with self.assertRaisesRegex(ValueError, "endpoint|clean buffer"):
            analyze(events)

    def test_one_less_magnitude_bit_can_overflow(self):
        # A norm-attaining free-word input with every magnitude equal to 7.
        # P=4 and one less bit than P+13 gives a signed 16-bit output.
        self.assertEqual(302 * 7 * 16, 33824)
        self.assertEqual(169 * 7 * 32, 37856)
        self.assertGreater(33824, (1 << 15) - 1)
        self.assertGreater(37856, (1 << 15) - 1)
        self.assertLess(37856, (1 << 16) - 1)

    def test_receipt_contains_no_admission_claim(self):
        result = read_json(HERE / "RESULT.json")
        self.assertEqual(
            result["status"],
            "PASS_RANK7_SCALAR_REFERENCE_LATTICE_NOT_PHYSICAL_ADMISSION",
        )
        forward = result["providers"]["base"]["forward"]
        backward = result["providers"]["base"]["backward"]
        self.assertEqual((forward["fraction_bits"], backward["fraction_bits"]), (4, 5))
        self.assertEqual((forward["max_l1"], backward["max_l1"]), ("302", "169"))


if __name__ == "__main__":
    unittest.main()
