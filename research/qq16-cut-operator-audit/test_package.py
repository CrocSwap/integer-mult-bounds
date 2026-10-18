"""Focused source-integrity and operator-law controls, standard library only."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_cut_reviewer", PACKAGE / "verify.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class PackageChecks(unittest.TestCase):
    def test_every_live_source_corruption_rejected(self):
        raw = audit.source_bytes()
        original = Path.read_bytes
        for name in raw:
            with self.subTest(path=name):
                target = audit.ROOT / name

                def read(path, target=target):
                    value = original(path)
                    return value + b"corruption" if path == target else value

                with patch.object(Path, "read_bytes", read):
                    with self.assertRaisesRegex(ValueError, "source hash"):
                        audit.source_bytes()

    def test_affine_composition_at_nonidentity_owner(self):
        # Independent evaluation of the two reads at one arbitrary owner.
        columns = list(audit.E)
        columns[0], columns[1] = columns[1], columns[0]
        left = audit.intern(columns, 1)
        right = audit.intern(audit.E, 2)
        owner = tuple(columns)
        point = 7
        g, a = audit.MAPS[left]
        h, b = audit.MAPS[right]
        owner_after_left = tuple(audit.act(owner, v) for v in g)
        expected_owner = tuple(audit.act(owner_after_left, v) for v in h)
        expected_point = point ^ audit.act(owner, a) ^ audit.act(owner_after_left, b)
        composed_g, composed_a = audit.MAPS[audit.compose(left, right)]
        self.assertEqual(tuple(audit.act(owner, v) for v in composed_g), expected_owner)
        self.assertEqual(point ^ audit.act(owner, composed_a), expected_point)
        self.assertNotEqual(a ^ b, composed_a)

    def test_inverse_requires_transported_shift(self):
        columns = list(audit.E)
        columns[0], columns[1] = columns[1], columns[0]
        mapping = audit.intern(columns, 1)
        inverse = audit.undo(mapping)
        self.assertEqual(audit.MAPS[inverse][1], 2)
        wrong = audit.intern(columns, 1)
        self.assertNotEqual(audit.compose(mapping, wrong), 0)

    def test_singular_unread_minor_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "singular minor"):
            audit.inverse([[1, 1], [1, 1]])


if __name__ == "__main__":
    unittest.main()
