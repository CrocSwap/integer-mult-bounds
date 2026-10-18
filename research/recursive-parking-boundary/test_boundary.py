"""Focused semantic tests, independent witnesses, and fail-closed extraction."""
from itertools import product
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as m
import verify as v


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.push, cls.pop, _ = v.load_tables()

    def test_move_arbitrary_bits_and_empty_stream(self):
        for length in range(10):
            for bits in product(m.BIT, repeat=length):
                source, target = m.Tape.marked(bits), m.Tape.marked()
                self.assertEqual(m.run_move(source, target), 2 * length + 2)
                self.assertEqual(source.bits(), ())
                self.assertEqual(target.bits(), bits)
                self.assertGreaterEqual(min(source.visits + target.visits), -1)
        with self.assertRaisesRegex(ValueError, "move interface violation"):
            m.run_move(m.Tape.marked("0"), m.Tape.marked("1"))

    def test_extractor_rejects_unrecognized_or_incomplete_source(self):
        source = (v.SOURCE_DIR / "TapeStackPush.lean").read_text(encoding="utf-8")
        prefix, tail = source.split("def instruction (", 1)
        for changed in (
            tail.replace("| .done => ⟨.done, {}, {}⟩", "| .oops => ⟨.done, {}, {}⟩", 1),
            tail.replace("| .copy => match source with", "| .copy => match address with", 1),
            tail.replace("⟨none, .left⟩", "⟨none, .jump⟩", 1),
            tail.replace("      | .separator => ⟨.done, {}, {}⟩\n", "", 1),
        ):
            with self.assertRaises(ValueError):
                m.parse_instruction_table(prefix + "def instruction (" + changed,
                                          m.PUSH_MODES, ("source",), 2)

    def test_source_mutation_has_a_semantic_consequence(self):
        source = (v.SOURCE_DIR / "TapeStackPush.lean").read_text(encoding="utf-8")
        prefix, tail = source.split("def instruction (", 1)
        changed = prefix + "def instruction (" + tail.replace(
            "⟨some (.bit b), .right⟩", "⟨some .blank, .right⟩", 1)
        table = m.parse_instruction_table(changed, m.PUSH_MODES, ("source",), 2)
        source, parking, temporary = m.Tape.marked("1"), m.Tape.stack(), m.Tape.marked()
        m.run_table(table, "copy", [source, parking], (0,))
        m.run_table(self.pop, "enterDelimiter", [parking, temporary, source], (0, 1, 2))
        self.assertNotEqual(source.bits(), (m.ONE,))

    def test_finite_dispatch_and_multiple_changing_active_roles(self):
        for width in range(2, 9):
            bits = [tuple(m.BIT[(i + j) % 2] for j in range(7)) for i in range(width)]
            work = m.Workspace([m.Tape.marked(x) for x in bits], m.Tape.stack("0|1__10|"))
            initial = work.parking.snapshot()
            expected = list(bits)
            total = 0
            # Every active role twice, different order; dirty inputs restored.
            for active in tuple(range(width)) + tuple(reversed(range(width))):
                program = m.boundary_program(width, active)
                self.assertEqual(len(program), 2 * width + 1)
                self.assertEqual(sum(phase == "child" for phase, _ in program), 1)
                count = m.boundary(work, active, m.flip_child, self.push, self.pop)
                total += count["total"]
                expected[active] = tuple(m.ONE if b == m.ZERO else m.ZERO for b in expected[active])
                self.assertEqual([t.bits() for t in work.roles], expected)
                self.assertEqual(work.parking.snapshot(), initial)
                self.assertEqual(work.io.bits(), ())
                self.assertEqual(work.temporary.bits(), ())
            self.assertEqual(expected, bits)
            self.assertEqual(total, 2 * width * ((5 * width - 1) * 7 + 9 * width - 2))

    def test_same_local_trace_with_different_ancestors(self):
        observed = []
        for ancestor, origin in (("", -5), ("1" * 10000, 0), ("|0_1" * 17, 121)):
            work = m.Workspace([m.Tape.marked(x) for x in ("0101", "1110", "0011")],
                               m.Tape.stack(ancestor, origin))
            count = v.verify_boundary(work, 1, self.push, self.pop)
            observed.append((count, [position - origin for position in work.parking.visits],
                             [position - origin for position in work.parking.writes]))
        self.assertEqual(observed[0], observed[1])
        self.assertEqual(observed[1], observed[2])

    def test_endpoint_preservation_cannot_certify_child_time(self):
        costs = []
        for length in (0, 1, 31, 1000):
            work = m.Workspace([m.Tape.marked(), m.Tape.marked()], m.Tape.stack("1" * length))
            original = work.parking.snapshot()
            cost = v.ancestor_scan_child(work)
            self.assertEqual(work.parking.snapshot(), original)
            self.assertEqual(cost, 2 * length + 5)
            self.assertLess(min(work.parking.visits), -1)
            costs.append(cost)
        self.assertEqual(costs[-1] - costs[0], 2000)


if __name__ == "__main__":
    unittest.main()
