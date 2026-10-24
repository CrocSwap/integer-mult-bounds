#!/usr/bin/env python3
"""Geometric inclusion, chronology and source-corruption controls. Apache-2.0."""
from collections import deque
from fractions import Fraction
import importlib.util
from itertools import combinations_with_replacement, product
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("receiver_floor", HERE / "verify.py")
V = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(V)


def geometric_profiles(starts, ends, spaces):
    """Forward traversal over actual subspaces, not dimension bounds.

    Deliberately separate from the production suffix recursion. This still
    relaxes scalar endpoint equality to temporal ancestry.
    """
    queue = deque([(starts, (1, 2, 4), ())])
    seen = set(queue)
    answers = set()
    while queue:
        frames, origins, prefix = queue.popleft()
        if origins[0] & 4 and origins[1] & 4:
            tail = tuple(len(end).bit_length() - len(frame).bit_length()
                         for frame, end in zip(frames, ends) if frame != end)
            answers.add(tuple(sorted(prefix + tail)))
        for a, b in ((0, 1), (0, 2), (1, 2)):
            for common in spaces:
                if not (frames[a] <= common <= ends[a] and frames[b] <= common <= ends[b]):
                    continue
                updated, reached = list(frames), list(origins)
                updated[a] = updated[b] = common
                reached[a] = reached[b] = origins[a] | origins[b]
                if tuple(updated) == frames and tuple(reached) == origins:
                    continue
                charged = tuple(len(common).bit_length() - len(frames[r]).bit_length()
                                for r in (a, b) if common != frames[r])
                state = (tuple(updated), tuple(reached), tuple(sorted(prefix + charged)))
                if state not in seen:
                    seen.add(state)
                    queue.append(state)
    return answers


class Controls(unittest.TestCase):
    def test_exhaustive_actual_subspaces_f2_squared(self):
        spaces = []
        for mask in range(1 << 4):
            values = frozenset(x for x in range(4) if mask & (1 << x))
            if 0 in values and all(x ^ y in values for x in values for y in values):
                spaces.append(values)
        self.assertEqual(len(spaces), 5)
        comparable = [(a, b) for a in spaces for b in spaces if a <= b]
        self.assertEqual(len(comparable), 12)
        nonempty = 0
        for pairs in product(comparable, repeat=3):
            starts, ends = tuple(p[0] for p in pairs), tuple(p[1] for p in pairs)
            exact = geometric_profiles(starts, ends, spaces)
            abstract, _ = V.relaxed_profiles(starts, ends)
            self.assertTrue(exact <= abstract, (starts, ends, exact - abstract))
            nonempty += bool(exact)
        self.assertGreater(nonempty, 0)
        print("PASS_1728_EXHAUSTIVE_GEOMETRIC_INCLUSIONS nonempty=" + str(nonempty))

    def test_causal_control_and_terminal_charge(self):
        # Actual shape of #4470 window 10557. A connected contact graph can
        # meet a,b at 0 before meeting b,x at 1; x then never reaches a.
        zero, line, plane = V.span([]), V.span([30]), V.span([30, 416])
        starts, ends = (zero, zero, line), (plane, line, line)
        legitimate, _ = V.relaxed_profiles(starts, ends)
        missing_ancestry, _ = V.relaxed_profiles(starts, ends, required=(0, 0, 0))
        self.assertEqual(legitimate, {(1, 1, 1)})
        self.assertIn((1, 2), missing_ancestry)
        self.assertFalse(V.concave_floor((1, 1, 1), (1, 2)))
        self.assertFalse(V.concave_floor((1, 1, 1), (1, 1)))
        self.assertEqual(V.incumbent_profile({"starts": starts, "ends": ends,
                                              "frames": (line, line)}), (1, 1, 1))

    def test_boundaries_and_nontrivial_positive_case(self):
        zero, line, other = V.span([]), V.span([1]), V.span([2])
        profiles, _ = V.relaxed_profiles((zero, zero, line), (other, other, line))
        self.assertFalse(profiles, "equal dimension does not imply compatible frames")
        profiles, _ = V.relaxed_profiles((line, zero, zero), (zero, line, line))
        self.assertFalse(profiles, "shrinking boundary must be excluded")
        profiles, _ = V.relaxed_profiles((zero, zero, zero), (line, line, line))
        self.assertIn((1, 1, 1), profiles, "zero-dimension source must still propagate ancestry")

    def test_discrete_concave_expansion(self):
        # All 220 nonincreasing nine-step slopes chosen from {0,1,2,3}.
        cases = 0
        for ascending in combinations_with_replacement(range(4), 9):
            slopes = tuple(Fraction(x, 3) for x in reversed(ascending))
            f = [sum(slopes[:r]) for r in range(10)]
            for rank in range(10):
                expanded = slopes[-1] * rank + sum(
                    (slopes[k - 1] - slopes[k]) * min(rank, k) for k in range(1, 9))
                self.assertEqual(f[rank], expanded)
            cases += 1
        self.assertEqual(cases, 220)
        self.assertTrue(V.concave_floor((3, 3), (2, 2, 2)))
        self.assertFalse(V.concave_floor((2, 2, 2), (3, 3)))

    def test_next_use_and_warp_exit_extraction(self):
        # Includes an owned clear, a persistent scale, an ignored climb and a
        # warp whose pre-frame differs from its post-frame.
        c = {"frames": [[], [1], [1, 2]], "start": [0, 0, 1], "final": [2, 1, 1]}
        p = [["phase", "B"], ["scalar", ["clear", ["C", 0]], 0],
             ["climb", "unused"], ["scalar", ["add", ["L", 0], ["L", 2], 1, 1], 1],
             ["scalar", ["add", ["L", 1], ["L", 2], -1, 1], 1],
             ["warp", ["L", 0], "symbol", 2, 0],
             ["scalar", ["scale", ["L", 1], 2, 1], 1]]
        windows = V.extract_windows(c, p)
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0]["index"], 2)
        self.assertEqual(windows[0]["starts"], (V.span([]), V.span([]), V.span([1])))
        self.assertEqual(windows[0]["ends"], (V.span([1, 2]), V.span([1]), V.span([1])))

    def test_source_corruption_is_rejected_before_constructor(self):
        with tempfile.TemporaryDirectory(prefix="receiver-floor-corrupt-") as tmp:
            root = Path(tmp)
            first = root / V.INPUTS[0]
            first.parent.mkdir(parents=True)
            first.write_bytes((V.ROOT / V.INPUTS[0]).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "source hash"):
                V.authenticate(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
