"""Behavioral controls, including optimized authentication failures."""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import independent_check
import verify


class Controls(unittest.TestCase):
    def test_binary_rank_boundary(self):
        self.assertEqual(len(verify.basis([1, 2, 3, 4])), 3)
        self.assertEqual(independent_check.binary_rank([1, 2, 3, 4]), 3)
        with self.assertRaises(ValueError):
            verify.basis([512])
        with self.assertRaises(ValueError):
            independent_check.binary_rank([-1])

    def test_live_axis_contract(self):
        with self.assertRaises(ValueError):
            verify.rank6_capacity(tuple(range(29)))
        with self.assertRaises(ValueError):
            verify.rank6_capacity((1,) * 29)

    def test_threshold_budget(self):
        self.assertGreater(2 * (78 - 38), 22 + 22 + 32)
        self.assertEqual(82 - 38, 12 + 12 + 20)
        self.assertLess(82 - 39, 12 + 12 + 20)
        self.assertGreater(20, 18)

    def test_unpunctured_control(self):
        g = verify.geometry()
        roots, _, _, coordinates = g.root_data()
        full_labels = [
            1 | sum((int(x) & 1) << (i + 1) for i, x in enumerate(c))
            for c in coordinates
        ]
        a, b = (0, 0, 0, 0, 0, 2, -2, 0), (0, 2, -2, 0, 0, 0, 0, 0)
        values = [
            v
            for r, v in zip(roots, full_labels, strict=True)
            if g.dot(a, r) and not g.dot(b, r)
        ]
        self.assertEqual(len(independent_check.maximal_axis_subsets(values)), 16)

    def source_fixture(self, temporary):
        root = Path(temporary)
        package = root / "research/p112-mixed-support38"
        package.mkdir(parents=True)
        shutil.copyfile(verify.PACKAGE / "SOURCES.json", package / "SOURCES.json")
        for path in verify.INPUTS:
            destination = root / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(verify.ROOT / path, destination)
        for path in verify.RETAINED:
            destination = package / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(verify.PACKAGE / path, destination)
        return root, package

    def test_corrupt_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, package = self.source_fixture(temporary)
            verify.authenticate(package, root)
            (root / verify.GEOMETRY).write_text("altered")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                verify.authenticate(package, root)

    def test_inventory_rejections(self):
        for mutation in ("missing", "duplicate", "escape", "extra"):
            with (
                self.subTest(mutation=mutation),
                tempfile.TemporaryDirectory() as temporary,
            ):
                root, package = self.source_fixture(temporary)
                path = package / "SOURCES.json"
                sources = json.loads(path.read_text())
                if mutation == "missing":
                    sources["retained_files"].pop()
                elif mutation == "duplicate":
                    sources["retained_files"][1] = sources["retained_files"][0]
                elif mutation == "escape":
                    sources["files"][-1]["path"] = "../../outside"
                else:
                    sources["unexpected"] = []
                path.write_text(json.dumps(sources))
                with self.assertRaises(ValueError):
                    verify.authenticate(package, root)

    def test_link_and_size_rejections(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "large"
            path.write_bytes(b"x" * 100)
            with self.assertRaisesRegex(ValueError, "size limit"):
                verify.read_bytes(path, limit=10)
            linked = Path(temporary) / "linked"
            linked.symlink_to(path)
            with self.assertRaisesRegex(ValueError, "linked"):
                verify.read_bytes(linked)


if __name__ == "__main__":
    unittest.main(verbosity=2)
