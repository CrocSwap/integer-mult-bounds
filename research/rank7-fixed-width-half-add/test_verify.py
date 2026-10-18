# SPDX-License-Identifier: Apache-2.0
"""Behavioral fixtures and semantic/contract failure controls."""

import json
import shutil
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path

import audit
from kernel import Circuit, build, check, coarse_call, execute, invoice, pack, validate
from sources import PACKAGE, authenticate, canonical, inventory, read
from verify import emit, fixtures, verify


def parsed(circuit):
    return audit.parse(
        json.loads(canonical(asdict(circuit) | {"wires": circuit.wires}))
    )


class CallerTests(unittest.TestCase):
    def test_signed_dirty_target_and_inverse(self):
        forward = build(8, 3, 1, "wired")
        backward = build(8, 3, -1, "wired")
        self.assertEqual(audit.observe(parsed(forward), -40, 17), (-40, 12, 0))
        self.assertEqual(audit.observe(parsed(backward), -40, 17), (-40, 22, 0))
        after = check(forward, -40, 17)
        self.assertEqual(after, 216 | (12 << 8))
        self.assertEqual(execute(backward, after), pack(forward, -40, 17))

    def test_three_paid_policies(self):
        expected_cx = {"wired": 36, "source": 162, "scratch": 178}
        for policy in expected_cx:
            circuit = build(8, 3, 1, policy)
            self.assertEqual(check(circuit, -40, 17), 216 | (12 << 8))
            bill = invoice(circuit)
            self.assertEqual((bill["cx"], bill["ccx"]), (expected_cx[policy], 14))
            self.assertEqual(bill["total_bits"], 25 if policy == "scratch" else 17)

    def test_signed_extremes_and_no_target_headroom(self):
        circuit = build(8, 3, 1, "wired")
        self.assertEqual(audit.observe(parsed(circuit), -128, -112), (-128, -128, 0))
        self.assertEqual(audit.observe(parsed(circuit), 120, 112), (120, 127, 0))
        for width in (4, 8, 32, 256):
            for sign in (-1, 1):
                c = build(width, 3, sign, "wired")
                for source, target in fixtures(width, 3, sign):
                    check(c, source, target)
                    audit.check(parsed(c), source, target)

    def test_paid_coarse_guard_allocation_and_retained_output(self):
        c = build(8, 3, 1, "wired")
        after = coarse_call(c, -5, 2)
        self.assertEqual(after, 216 | (11 << 8))
        self.assertEqual(after & 7, 0)  # The three new source bits return.
        self.assertEqual((after >> 8) & 7, 3)  # Target bits are live output.
        bill = invoice(c)
        self.assertEqual(bill["coarse_new_zero_bits"], 7)
        self.assertEqual(bill["coarse_returned_zero_bits"], 4)
        self.assertEqual(bill["coarse_retained_new_target_bits"], 3)
        with self.assertRaisesRegex(ValueError, "coarse source range"):
            coarse_call(c, -17, 2)
        with self.assertRaisesRegex(ValueError, "overflow"):
            coarse_call(c, 15, 15)

    def test_guard_zeros_are_not_rounding(self):
        c = build(8, 1, 1, "wired")
        self.assertEqual(audit.observe(parsed(c), -40, 17), (-40, -3, 0))
        for source in (-39, -1, 1, 39):
            with self.assertRaisesRegex(ValueError, "guard zeros"):
                pack(c, source, 17)
            with self.assertRaisesRegex(ValueError, "source grid"):
                audit.check(parsed(c), source, 17)

    def test_overflow_rejected_not_wrapped(self):
        c = build(8, 1, 1, "wired")
        self.assertEqual(check(c, 2, 126), 2 | (127 << 8))
        for source, target in ((2, 127), (-128, -128)):
            with self.assertRaisesRegex(ValueError, "overflow"):
                check(c, source, target)
            with self.assertRaisesRegex(ValueError, "result range"):
                audit.check(parsed(c), source, target)

    def test_sign_fill_and_clean_return_mutants(self):
        c = build(8, 3, 1, "wired")
        self.assertEqual(audit.observe(parsed(c), -40, 17), (-40, 12, 0))
        for gates in (c.gates[3:], c.gates[:-3], c.gates[1:]):
            mutant = replace(c, gates=gates)
            with self.assertRaises(ValueError):
                check(mutant, -40, 17)
            with self.assertRaises(ValueError):
                audit.check(parsed(mutant), -40, 17)
        wrong_sign = build(8, 3, -1, "wired")
        self.assertEqual(audit.observe(parsed(wrong_sign), -40, 17), (-40, 22, 0))

    def test_omitted_scratch_uncompute(self):
        c = build(8, 1, 1, "scratch")
        self.assertEqual(check(c, -40, 17), 216 | (253 << 8))
        mutant = replace(c, gates=c.gates[:-8])
        with self.assertRaisesRegex(ValueError, "scratch return"):
            check(mutant, -40, 17)
        with self.assertRaises(ValueError):
            audit.check(parsed(mutant), -40, 17)

    def test_clean_carry_is_a_real_precondition(self):
        c = build(4, 1, 1, "wired")
        clean = check(c, 4, 1)
        self.assertEqual(clean, 4 | (3 << 4))
        dirty = execute(c, pack(c, 4, 1) | (1 << 8))
        self.assertEqual(dirty, 4 | (4 << 4) | (1 << 8))

    def test_primary_argument_and_gate_contracts(self):
        self.assertEqual(check(build(4, 1, 1, "wired"), 4, 1), 52)
        for arguments in (
            (3, 1, 1, "wired"),
            (257, 1, 1, "wired"),
            (8, 0, 1, "wired"),
            (8, 4, 1, "wired"),
            (8, 1, 0, "wired"),
            (8, 1, True, "wired"),
            (8, 1, 1, "unknown"),
        ):
            with self.assertRaises(ValueError):
                build(*arguments)
        for gates in (((0, 0),), ((0, 17),), ((0, 1, 2, 3),), ((True, 1),)):
            with self.assertRaises(ValueError):
                validate(Circuit(8, 1, 1, "wired", gates))
        with self.assertRaisesRegex(ValueError, "gate budget"):
            validate(Circuit(8, 1, 1, "wired", ((0, 1),) * 8193))

    def test_independent_parser_boundaries(self):
        c = build(4, 1, 1, "wired")
        doc = json.loads(canonical(asdict(c) | {"wires": c.wires}))
        self.assertEqual(audit.observe(audit.parse(doc), 4, 1), (4, 3, 0))
        for field, bad in (
            ("width", 257),
            ("shift", 4),
            ("sign", True),
            ("policy", "other"),
            ("wires", 8),
            ("gates", [[0, 0]]),
        ):
            with self.assertRaises(ValueError):
                audit.parse(doc | {field: bad})
        with self.assertRaises(ValueError):
            audit.parse(doc | {"unpaid_shift": 1})

    def test_emitted_file_and_lifecycle(self):
        with tempfile.TemporaryDirectory(prefix="half-add-test-") as directory:
            work = Path(directory)
            program, sha256 = emit(build(8, 3, 1, "wired"), work)
            self.assertEqual(audit.observe(program, -40, 17), (-40, 12, 0))
            self.assertEqual(len(sha256), 64)
            with self.assertRaisesRegex(ValueError, "fresh output"):
                verify(work)
            # A gate removal must fail the gate invoice, even before semantics.
            c = build(8, 3, 1, "wired")
            with self.assertRaisesRegex(ValueError, "gate count"):
                invoice(replace(c, gates=c.gates[:-1]))

    def test_source_bindings_and_candidate_inventory(self):
        self.assertEqual(len(authenticate()), 4)
        word = read(PACKAGE / "vendor/WORD-base.json.gz")
        result = inventory(word)
        self.assertEqual(
            result["first_examples"]["-1/2"]["gate"][:5], ["add", 126, 83, -1, 2]
        )
        with tempfile.TemporaryDirectory(prefix="half-add-pins-") as directory:
            clone = Path(directory)
            shutil.copytree(PACKAGE / "vendor", clone / "vendor")
            shutil.copyfile(PACKAGE / "VENDOR.json", clone / "VENDOR.json")
            self.assertEqual(authenticate(clone), authenticate())
            path = clone / "vendor/WORD-base.json.gz"
            path.write_bytes(b"not the frozen word")
            with self.assertRaisesRegex(ValueError, "source bytes"):
                authenticate(clone)


if __name__ == "__main__":
    unittest.main()
