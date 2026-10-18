# SPDX-License-Identifier: Apache-2.0
"""Behavioral and rejection controls for the physical four-ADD boundary."""

import copy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import bit_audit
import fanout
import verify
from operators import UNITS, N, Q, closed_source, group, monomial, real_rows


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix="a13-tests-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.work = Path(cls.directory.name)
        verify.authenticate()
        cls.canonical = verify.transport("base", cls.work)
        cls.preparation, cls.g, cls.target, cls.source = group(cls.canonical)
        cls.rows = real_rows(cls.preparation[126], cls.target, cls.source)

    def test_actual_preparation(self):
        preparation = group(self.canonical)[0]
        self.assertEqual(tuple(preparation), (126, 153, 164, 218))
        self.assertEqual(
            preparation[126],
            {126: Q(1, 2), 127: Q(-1, 2), 164: Q(1, 2), 165: Q(-1, 2)},
        )
        self.assertEqual(
            {sum(map(abs, row.values())) for row in preparation.values()}, {Q(2)}
        )

    def test_physical_quarter_is_retained(self):
        state = verify.inputs(3, "quarter", self.rows)
        targets, sources = verify.operands(
            state, self.preparation, self.target, self.source
        )
        self.assertEqual(targets[0][0][0] - sources[0][0] / 2, Q(1, 4))
        self.assertNotEqual((2 * targets[0][0][0]).denominator, 1)
        circuit = fanout.build(8, True)
        final = fanout.check(circuit, 0, tuple(int(4 * t[0][0]) for t in targets))
        self.assertEqual(fanout.observe(circuit, final)[0][1] & 3, 1)

    def test_one_less_width_fails_on_actual_norm_witness(self):
        state = verify.inputs(5, "norm", self.rows)
        targets, sources = verify.operands(
            state, self.preparation, self.target, self.source
        )
        source = int(4 * sources[0][0])
        before = tuple(int(4 * t[0][0]) for t in targets)
        self.assertEqual(before[0] - source // 2, 270)
        with self.assertRaisesRegex(ValueError, "overflow"):
            fanout.pack(fanout.build(9, True), source, before)
        fanout.check(fanout.build(10, True), source, before)

    def test_omitting_paid_climb_is_not_the_physical_boundary(self):
        identity = tuple({x: UNITS[0]} for x in range(N))
        with self.assertRaisesRegex(ValueError, "quarter terms"):
            real_rows(self.preparation[126], identity, self.source)

    def test_source_phase_and_inverse_are_decisive(self):
        wrong = copy.deepcopy(self.source)
        j, (a, b) = next(iter(wrong[0].items()))
        wrong[0][j] = -a, -b
        with self.assertRaisesRegex(ValueError, "closing warp"):
            closed_source(self.g, self.target, wrong)

    def test_emitted_paid_group_chronology(self):
        events = verify.read(self.work / "base/LOCAL-PROGRAMS.json.gz")["forward"]
        verify.check_emitted(events, self.canonical)
        index = events.index(["climb", "A", 126, 0, 136, 1])
        del events[index]
        with self.assertRaisesRegex(ValueError, "paid group chronology"):
            verify.check_emitted(events, self.canonical)

    def test_actual_word_mutants_rejected(self):
        bad = copy.deepcopy(self.canonical)
        bad["A"][14][3] = 1
        with self.assertRaisesRegex(ValueError, "four-ADD"):
            group(bad)
        bad = copy.deepcopy(self.canonical)
        bad["frames"][136] = [46]
        with self.assertRaisesRegex(ValueError, "frames"):
            group(bad)

    def test_shared_and_separate_literal_signed_calls(self):
        circuits = [fanout.build(4, shared) for shared in (False, True)]
        checked = 0
        for source in range(-8, 8, 2):
            for a in range(-8, 8):
                for b in range(-8, 8):
                    targets = (a, b, -a - 1, -b - 1)
                    if not all(-8 <= t - source // 2 < 8 for t in targets):
                        continue
                    states = [fanout.check(c, source, targets) for c in circuits]
                    self.assertEqual(states[0], states[1])
                    bit_audit.check((4, circuits[1].gates), source, targets)
                    checked += 1
        self.assertEqual(checked, 1200)

    def test_complete_invoice_and_maximum_width(self):
        for width in (4, 8, 10, 69, 256):
            shared, separate = [fanout.build(width, flag) for flag in (True, False)]
            small, big = fanout.invoice(shared), fanout.invoice(separate)
            self.assertEqual(big["cx"] - small["cx"], 6)
            self.assertEqual(big["ccx"], small["ccx"])
            self.assertEqual(big["wires"], small["wires"])
            low, high = -(1 << (width - 1)), 1 << (width - 1)
            fanout.check(shared, -4, (0, low, high - 3, -1))

    def test_guard_cleanup_and_initialization_are_required(self):
        good = fanout.build(8, True)
        for gates in (good.gates[:-1], good.gates[1:]):
            bad = fanout.Circuit(8, True, gates)
            with self.assertRaisesRegex(ValueError, "fanout identity"):
                fanout.check(bad, -4, (0, 0, 0, 0))
        with self.assertRaisesRegex(ValueError, "guard"):
            fanout.check(good, -3, (0, 0, 0, 0))
        dirty = fanout.pack(good, -4, (0, 0, 0, 0)) | (1 << (5 * good.width))
        self.assertNotEqual(fanout.observe(good, fanout.execute(good, dirty))[1], 0)

    def test_serialized_program_and_wire_alias_rejected(self):
        doc = {"width": 8, "shared": True, "wires": 41, "gates": [[0, 0]]}
        with self.assertRaisesRegex(ValueError, "alias"):
            bit_audit.parse(doc)
        doc["gates"] = [[0, 41]]
        with self.assertRaisesRegex(ValueError, "range"):
            bit_audit.parse(doc)
        with self.assertRaisesRegex(ValueError, "width"):
            fanout.build(257, True)
        with self.assertRaisesRegex(ValueError, "invertible"):
            monomial([1] * 9)

    def test_source_corruption_is_rejected(self):
        package = self.work / "corrupt"
        package.mkdir()
        shutil.copytree(verify.HERE / "vendor", package / "vendor")
        shutil.copyfile(verify.HERE / "VENDOR.json", package / "VENDOR.json")
        path = package / "vendor/WORD-base.json.gz"
        with path.open("ab") as stream:
            self.assertEqual(stream.write(b"x"), 1)
        with self.assertRaisesRegex(ValueError, "source hash"):
            verify.authenticate(package)

    def test_occupied_output_is_preserved(self):
        occupied = self.work / "occupied"
        occupied.mkdir()
        marker = occupied / "keep"
        self.assertEqual(marker.write_bytes(b"prior diagnostic"), 16)
        result = subprocess.run(
            [
                sys.executable,
                "-B",
                str(verify.HERE / "verify.py"),
                "--work",
                str(occupied),
            ],
            capture_output=True,
            check=False,
            timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"fresh work directory", result.stderr)
        self.assertEqual(marker.read_bytes(), b"prior diagnostic")


if __name__ == "__main__":
    unittest.main()
