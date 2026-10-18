"""Behavioral controls, including a modular singleton that is not a rational one."""

import itertools
import json
import os
import runpy
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))


def regular_copy(source, destination):
    paths = sorted(source.rglob("*"))
    if len(paths) > 35:
        raise ValueError("private copy inventory bound")
    destination.mkdir()
    for path in paths:
        mode = path.lstat().st_mode
        target = destination / path.relative_to(source)
        if stat.S_ISDIR(mode):
            target.mkdir()
        elif stat.S_ISREG(mode):
            data = path.read_bytes()
            if len(data) > 100_000:
                raise ValueError("private copy size bound")
            with target.open("xb") as output:
                if output.write(data) != len(data):
                    raise ValueError("private copy short write")
        else:
            raise ValueError("private copy link or special file")


class Controls(unittest.TestCase):
    def test_cocircuit_completeness(self):
        identity = [tuple(int(i == j) for j in range(8)) for i in range(8)]
        extra = [
            (101, 1, 0, 0, 0, 0, 0, 0),
            (1, 1, 0, 0, 0, 0, 0, 0),
            (0, 0, 1, 2, 3, 4, 5, 6),
        ]
        for subset in ((), (0,), (1,), (0, 1), (0, 2), (0, 1, 2)):
            points = identity + [extra[i] for i in subset]
            ids = list(range(len(points)))
            basis, dependencies = V["modular_dependencies"](points, ids, 101)
            cuts = set(V["small_cuts"](ids, basis, dependencies, 101))
            for size in (1, 2):
                for cut in itertools.combinations(ids, size):
                    kernel = V["exact_nullspace"](
                        [p for i, p in enumerate(points) if i not in cut]
                    )
                    if kernel:
                        self.assertIn(cut, cuts)
        # H_0 reduces to zero mod101, but over Q only deleting BOTH0,1 gives a kernel.
        points = identity + [extra[0]]
        self.assertEqual(
            V["exact_nullspace"]([p for i, p in enumerate(points) if i != 0]), []
        )
        self.assertEqual(len(V["exact_nullspace"](points[2:])), 1)

    def test_fail_closed_rank(self):
        with self.assertRaisesRegex(ValueError, "full modular rank"):
            V["modular_dependencies"]([(1,) * 8] * 8, list(range(8)), 101)

    def test_canonical_json_types(self):
        self.assertNotEqual(
            V["canonical_json"]({"schema_version": True}),
            V["canonical_json"]({"schema_version": 1}),
        )

    def test_actual_source_and_inventory_rejection(self):
        with tempfile.TemporaryDirectory(prefix="alpha74-controls-") as directory:
            root = Path(directory)
            package = root / "research" / HERE.name
            package.parent.mkdir()
            regular_copy(HERE, package)
            geometry = root / V["GEOMETRY"]
            geometry.parent.mkdir()
            geometry.write_bytes((V["ROOT"] / V["GEOMETRY"]).read_bytes())
            for script in ("verify.py", "independent.py"):
                geometry.write_bytes(geometry.read_bytes() + b"\n# corrupt\n")
                self.reject(root, package, script, "canonical geometry bytes")
                geometry.write_bytes((V["ROOT"] / V["GEOMETRY"]).read_bytes())
            source = package / "SOURCES.json"
            original = source.read_bytes()
            for field, value in (("schema_version", True), ("files", [])):
                data = json.loads(original)
                data[field] = value
                source.write_text(json.dumps(data))
                self.reject(root, package, "verify.py", "source")
            source.write_bytes(original)
            vendor = package / "vendor/PR3307-WITNESS.json"
            vendor.write_bytes(vendor.read_bytes() + b" ")
            self.reject(root, package, "verify.py", "predecessor bytes")

    def reject(self, root, package, script, message):
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(
            [sys.executable, "-O", "-B", str(package / script)],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(message, result.stderr)


if __name__ == "__main__":
    unittest.main()
