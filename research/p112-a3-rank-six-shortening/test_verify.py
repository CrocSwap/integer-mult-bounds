"""Independent finite oracles and semantic failure controls for A3 shortening."""

import copy
import json
import unittest
from collections import Counter
from unittest.mock import patch

import a3_model as model
import verify
from a3_geometry import SIMPLE, root_data


def independent_roots_labels():
    """Generate the root lattice orbit, instead of solving root coordinates."""
    roots = {r: 1 | (1 << (i + 1)) for i, r in enumerate(SIMPLE)}
    queue = list(roots)
    for index in range(240):
        if index >= len(queue):
            break
        r = queue[index]
        for i, normal in enumerate(SIMPLE):
            pairing = sum(x * y for x, y in zip(r, normal, strict=True))
            if pairing % 4:
                raise ValueError("nonintegral reflection")
            scale = pairing // 4
            image = tuple(x - scale * y for x, y in zip(r, normal, strict=True))
            label = roots[r] ^ ((scale & 1) << (i + 1))
            if image in roots:
                if roots[image] != label:
                    raise ValueError("inconsistent independently propagated label")
            else:
                roots[image] = label
                queue.append(image)
        if len(queue) > 240:
            raise ValueError("root orbit capacity")
    if len(queue) != 240:
        raise ValueError("incomplete root orbit")
    return dict(
        sorted((r, label) for r, label in roots.items() if r > tuple(-x for x in r))
    )


def independent_frames(roots):
    """Level-by-level clique extension with explicit neighbor-set intersections."""
    neighbors = [
        {
            j
            for j in range(120)
            if sum(a * b for a, b in zip(r, roots[j], strict=True)) == 0
        }
        for r in roots
    ]
    level = [()]
    for _ in range(8):
        next_level = []
        for prefix in level:
            candidates = set(range(prefix[-1] + 1 if prefix else 0, 120))
            for i in prefix:
                candidates.intersection_update(neighbors[i])
            if len(next_level) + len(candidates) > 200_000:
                raise ValueError("frame level capacity")
            next_level.extend(prefix + (j,) for j in sorted(candidates))
        level = next_level
    return set(level)


def independent_basis(labels):
    basis = [0] * 9
    for value in labels:
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return basis


def member(value, basis):
    for bit in range(8, -1, -1):
        if value >> bit & 1:
            value ^= basis[bit]
    return value == 0


class ShorteningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = independent_roots_labels()
        cls.roots, cls.labels = tuple(fixture), tuple(fixture.values())
        cls.frames = independent_frames(cls.roots)
        cls.values = tuple(
            (0, -2 * (r[0] + r[1]), -2 * (r[0] + r[2]), -2 * (r[0] + r[3]))
            for r in cls.roots
        )
        cls.costs = tuple(
            min(sum(x != shift for x in v) for shift in v) for v in cls.values
        )
        cls.extrema = [f for f in cls.frames if sum(cls.costs[i] for i in f) == 12]

    def test_independent_root_lattice_labels(self):
        roots, _, _, coordinates = root_data()
        labels = tuple(
            1 | sum((int(x) % 2) << (i + 1) for i, x in enumerate(c))
            for c in coordinates
        )
        self.assertEqual((roots, labels), (self.roots, self.labels))
        self.assertEqual(sum(bool(x) for x in independent_basis(labels)), 9)

    def test_full_star_and_spectrum(self):
        _, values, costs, steps = model.star(self.roots)
        self.assertEqual(values, self.values)
        self.assertEqual(costs, self.costs)
        self.assertEqual(Counter(costs), {0: 20, 1: 64, 2: 36})
        self.assertEqual([s["orbit_size"] for s in steps], [240, 56, 27])

    def test_two_complete_frame_enumerations(self):
        frames, _ = model.orthogonal_frames(self.roots)
        self.assertEqual(set(frames), self.frames)
        self.assertEqual(len(frames), len(self.frames))
        self.assertEqual(len(frames), 2025)
        self.assertEqual(
            Counter(sum(self.costs[i] for i in f) for f in frames),
            {8: 1005, 10: 960, 12: 60},
        )

    def test_independent_all_extremal_binary_spans(self):
        self.assertEqual(len(self.extrema), 60)
        for frame in self.extrema:
            live = [i for i in range(120) if i not in frame]
            row = model.extremal_frame(frame, self.values, self.costs, self.labels)
            for endpoint in range(4):
                mandatory = [
                    i
                    for i in live
                    if self.costs[i] == 1
                    and self.values[i].count(self.values[i][endpoint]) == 1
                ]
                basis = independent_basis([self.labels[i] for i in mandatory])
                self.assertEqual((len(mandatory), sum(bool(x) for x in basis)), (16, 6))
                self.assertEqual(
                    [i for i in live if member(self.labels[i], basis)], mandatory
                )
                mask = sum(1 << i for i in mandatory)
                self.assertEqual(
                    int(row["endpoints"][endpoint]["mandatory_mask"], 16), mask
                )
                self.assertEqual(
                    int(row["endpoints"][endpoint]["live_closure_mask"], 16), mask
                )

    def test_support_only_losing_control(self):
        self.assertEqual(sum(self.costs), 136)
        self.assertEqual(136 - 12 - 2 * 21, 82)
        self.assertEqual(136 - 12 - 2 * 22, 80)
        self.assertFalse(136 - 12 - 2 * 22 > 4 * 20)

    def test_actual_historical_profile_and_deletion(self):
        self.assertIn(model.PROFILE, model.original_survivors())
        self.assertEqual(sum(w - 2 for w in model.PROFILE), 35)
        row = model.application()
        self.assertEqual(row["retained_code_dimension_lower"], 3)
        self.assertEqual(row["retained_weights"], (2, 6, 6, 6, 6, 6))
        self.assertEqual(row["small_support_cap"], 22)
        with self.assertRaises(ValueError):
            model.application(code_dimension=5)
        with self.assertRaises(ValueError):
            model.application(deleted=2)
        with self.assertRaises(ValueError):
            model.application(weights=(2,) + (6,) * 4 + (7,) * 4)

    def test_nonextremal_and_incomplete_frame_controls(self):
        ordinary = next(f for f in self.frames if sum(self.costs[i] for i in f) == 8)
        with self.assertRaises(ValueError):
            model.extremal_frame(ordinary, self.values, self.costs, self.labels)
        with self.assertRaises(ValueError):
            model.orthogonal_frames(self.roots[:-1])

    def test_binary_label_semantic_mutants(self):
        frame = self.extrema[0]
        with self.assertRaises(ValueError):
            model.extremal_frame(frame, self.values, self.costs, (1,) * 120)
        labels = list(self.labels)
        live_singleton = next(
            i for i in range(120) if i not in frame and self.costs[i] == 1
        )
        labels[live_singleton] ^= 1
        with self.assertRaises(ValueError):
            model.extremal_frame(frame, self.values, self.costs, labels)

    def test_source_bytes_and_geometry_mutants(self):
        original = verify.read_bytes
        for target in (verify.ROOT / verify.DATA, verify.PACKAGE / "a3_geometry.py"):

            def mutated(path, target=target):
                raw = original(path)
                return raw + b"\n" if path == target else raw

            with (
                patch.object(verify, "read_bytes", side_effect=mutated),
                self.assertRaises(ValueError),
            ):
                verify.bind_sources()
        verify.bind_sources()

    def test_committed_receipt_rejection(self):
        expected = json.loads(verify.read_bytes(verify.PACKAGE / "RESULT.json"))
        actual = copy.deepcopy(expected)
        actual["a3"] = model.frame_receipt(self.roots, self.labels)
        verify.check_receipt(actual, expected)
        actual["a3"]["extremal_frames"][0]["endpoints"][0]["span_size"] = 32
        with self.assertRaises(ValueError):
            verify.check_receipt(actual, expected)

    def test_linear_transport_and_binary_span_boundary(self):
        self.assertEqual(
            model.label_action_receipt(self.roots, self.labels)[
                "root_label_comparisons"
            ],
            960,
        )
        for values in ([], [1], [1, 2], [1, 2, 3], list(range(1, 512))[:120]):
            basis = independent_basis(values)
            self.assertEqual(
                {i for i in range(512) if member(i, basis)}, model.binary_span(values)
            )
        with self.assertRaises(ValueError):
            model.binary_span([512])

    def test_output_safety(self):
        forbidden = verify.PACKAGE / "MUST-NOT-EXIST.json"
        self.assertFalse(forbidden.exists())
        with (
            patch.object(verify, "receipt", return_value={}),
            patch("sys.argv", ["verify.py", "--output", str(forbidden)]),
            self.assertRaises(ValueError),
        ):
            verify.main()
        self.assertFalse(forbidden.exists())


if __name__ == "__main__":
    unittest.main()
