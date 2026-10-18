"""Independent eligibility/order checks and fail-closed adapter controls."""

from itertools import product
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from adapter import COMPILER, HERE, ROOT, transformed_source, verify_sources
from priority import RankedSlots
from run import run


def frame_from_digits(digits):
    core = sum(1 << i for i, digit in enumerate(digits) if digit == 2)
    union = sum(1 << i for i, digit in enumerate(digits) if digit != 0)
    return core, union


def state(frame):
    core, union = frame
    return (1 if core == union else union.bit_count() - core.bit_count()), frame


def oracle(index, target):
    # Coordinate sets, rather than the index's bitmask intersections.
    points = lambda mask: {i for i in range(mask.bit_length()) if (mask >> i) & 1}
    core, union = map(points, target)
    admitted = []
    for slot in index.members:
        rank, frame = index.state_of(slot)
        old_core, old_union = map(points, frame)
        if core <= old_core and old_union <= union:
            admitted.append((-rank, slot))
    return [slot for _, slot in sorted(admitted)]


class PriorityTests(unittest.TestCase):
    def assert_order(self, index, target):
        self.assertEqual(list(index.ordered(target)), oracle(index, target))
        self.assertEqual(len(index), len(set(index)))

    def test_exhaustive_three_coordinate_frames(self):
        frames = [frame_from_digits(d) for d in product(range(3), repeat=3)]
        states = {slot * 7: state(frame) for slot, frame in enumerate(frames)}
        index = RankedSlots(3, states.__getitem__)
        for slot in reversed(states):
            index.add(slot)
        for target in frames:
            self.assert_order(index, target)
        for slot in states:
            index.remove(slot)
            for target in frames:
                self.assert_order(index, target)

    def test_seed85_state_machine_with_sparse_large_slot_ids(self):
        rng = random.Random(85)
        slots = list(range(96)) + [127, 128, 255, 1024, 30687, 40337]
        states = {slot: state(frame_from_digits(rng.choices(range(3), k=25))) for slot in slots}
        index = RankedSlots(25, states.__getitem__)
        for _ in range(2400):
            slot = rng.choice(slots)
            action = rng.randrange(4)
            if action == 0:
                index.add(slot)
            elif action == 1 and slot in index:
                index.remove(slot)
            else:
                new_state = state(frame_from_digits(rng.choices(range(3), k=25)))
                index.move(slot, *new_state)
                states[slot] = new_state
            targets = [(0, (1 << 25) - 1), states[rng.choice(slots)][1]]
            for target in targets:
                self.assert_order(index, target)

    def test_same_rank_frame_changes_update_eligibility(self):
        states = {7: (1, (1, 3))}
        index = RankedSlots(3, states.__getitem__)
        index.add(7)
        index.move(7, 1, (2, 6))
        states[7] = (1, (2, 6))
        self.assert_order(index, (1, 3))
        self.assert_order(index, (2, 6))

    def test_retired_clearing_anchor_moves_then_slot_is_removed(self):
        states = {3: (1, (1, 3)), 8: (1, (1, 3)), 10: (2, (1, 7))}
        index = RankedSlots(3, states.__getitem__)
        for slot in states:
            index.add(slot)
        iterator = index.ordered((1, 7))
        self.assertEqual(next(iterator), 10)
        # Match acquire's contract: clearing moves both operands, removes the
        # chosen slot and returns without resuming this iterator.
        for slot in (10, 3):
            index.move(slot, 2, (1, 7))
            states[slot] = (2, (1, 7))
        index.remove(10)
        self.assert_order(index, (1, 7))
        self.assertEqual(list(index.ordered((1, 7))), [3, 8])

    def test_duplicate_add_and_missing_remove_keep_set_semantics(self):
        states = {0: (1, (1, 1))}
        index = RankedSlots(3, states.__getitem__)
        index.add(0)
        index.add(0)
        self.assert_order(index, (1, 7))
        index.remove(0)
        with self.assertRaises(KeyError):
            index.remove(0)
        self.assert_order(index, (0, 7))

    def test_stale_move_mutant_is_detected(self):
        states = {5: (1, (1, 3)), 6: (2, (1, 7))}
        index = RankedSlots(3, states.__getitem__)
        for slot in states:
            index.add(slot)
        states[5] = (3, (0, 7))  # deliberately omit the move hook
        self.assertNotEqual(list(index.ordered((1, 7))), oracle(index, (1, 7)))

    def test_core_union_and_rank_mutants_are_detected(self):
        states = {2: (1, (1, 3)), 4: (2, (1, 7)), 8: (1, (2, 3))}
        for mutation in ("core", "union", "rank", "remove"):
            with self.subTest(mutation=mutation):
                index = RankedSlots(3, states.__getitem__)
                for slot in states:
                    index.add(slot)
                if mutation == "core":
                    index.core_masks[0] |= 1 << 8
                elif mutation == "union":
                    index.union_masks[2] &= ~(1 << 4)
                elif mutation == "rank":
                    index.masks[2] &= ~(1 << 4)
                    index.masks[1] |= 1 << 4
                else:
                    index.members.remove(2)  # deliberately leave stale bits
                target = (1, 7) if mutation == "rank" else (1, 3)
                self.assertNotEqual(list(index.ordered(target)), oracle(index, target))


class AdmissionTests(unittest.TestCase):
    def test_pinned_sources_and_three_exact_edit_sites(self):
        verify_sources()
        source = (ROOT / COMPILER).read_text()
        transformed = transformed_source(source)
        self.assertIn("if not contains(blocks[frames[s]]['frame'],blocks[g]['frame']):continue", transformed)
        self.assertIn("for dual in (False,True):", transformed)
        self.assertIn("assert not slots[s]", transformed)
        with self.assertRaisesRegex(ValueError, "source shape changed"):
            transformed_source(source + source)

    def test_tampered_compiler_and_archive_are_rejected_before_import(self):
        read_bytes = Path.read_bytes
        for target in (ROOT / COMPILER, HERE / "reference-pr175.py"):
            with self.subTest(target=target):
                def altered(path):
                    data = read_bytes(path)
                    return data + b"\n# control" if path == target else data
                with patch.object(Path, "read_bytes", altered):
                    with self.assertRaisesRegex(ValueError, "Changed pinned source"):
                        verify_sources()

    def test_reused_output_is_rejected_before_compilation(self):
        with self.assertRaisesRegex(ValueError, "fresh directory"):
            run("indexed", 23, HERE)

    def test_disabled_assertions_are_rejected_without_outputs(self):
        # Keep generated fixtures available for inspection, including failures.
        directory = Path(tempfile.mkdtemp(prefix="reclamation-admission-"))
        for flag in ("-O", "-OO"):
            output = directory / flag.lstrip("-")
            result = subprocess.run([sys.executable, flag, "-B", str(HERE / "run.py"),
                                     "--mode", "indexed", "--h", "23", "--out", str(output)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Assertions must remain enabled", result.stderr)
            self.assertFalse(output.exists())

    def test_missing_frame_update_hook_fails_real_compilation(self):
        directory = Path(tempfile.mkdtemp(prefix="reclamation-stale-hook-"))
        code = f"""
import sys
from pathlib import Path
sys.path.insert(0, {str(HERE)!r})
import adapter
from priority import RankedSlots
from run import run
class StaleSlots(RankedSlots):
    def move(self, slot, new_rank, new_frame):
        pass
adapter.RankedSlots = StaleSlots
run('indexed', 23, Path({str(directory / 'run')!r}))
"""
        result = subprocess.run([sys.executable, "-B", "-c", code],
                                capture_output=True, text=True, timeout=120)
        (directory / "stderr.txt").write_text(result.stderr)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("PASS_RECLAMATION_AXIS", result.stdout)
        self.assertTrue("AssertionError" in result.stderr or "receipt differs" in result.stderr,
                        result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
