"""Behavior and source-boundary controls, including optimized CLI rejection."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import GEOMETRY, PACKAGE, ROOT, basis, require, root_data, span
from verify import model


def private_export(destination):
    paths = tuple(PACKAGE.rglob("*"))
    require(len(paths) < 50, "package inventory bound")
    target = destination / "research" / PACKAGE.name
    for source in paths:
        require(not source.is_symlink(), "no linked package source")
        if source.is_file():
            output = target / source.relative_to(PACKAGE)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(source.read_bytes())
    source = destination / GEOMETRY
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_bytes((ROOT / GEOMETRY).read_bytes())
    return target


def run(target, script="verify.py"):
    process = subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(target / script)],
        capture_output=True,
        text=True,
        timeout=45,
    )
    return process.returncode, process.stdout + process.stderr


class Controls(unittest.TestCase):
    def test_sharpness_and_rank_boundary(self):
        g, roots, labels = root_data()
        pair, axis, bulk = model(g, roots, labels)
        result = json.loads((PACKAGE / "RESULT.json").read_bytes())
        ambient = result["witness"]["ambient_basis"]
        closure = {i for i, x in enumerate(labels) if x in span(ambient)}
        self.assertEqual(len(closure & set(axis)), 13)
        self.assertTrue(closure - set(axis))
        self.assertEqual(len(basis(tuple(labels[i] for i in closure & set(axis)))), 6)
        enlarged = next(
            span((*ambient, labels[i])) for i in bulk if labels[i] not in span(ambient)
        )
        self.assertEqual(len(enlarged), 128)
        self.assertGreaterEqual(sum(labels[i] in enlarged for i in axis), 14)
        self.assertTrue(any(labels[i] in enlarged for i in closure - set(axis)))
        self.assertEqual(pair, (0, 1))

    def test_corruptions_and_private_export(self):
        mutations = (
            "source",
            "schema",
            "usage",
            "inventory",
            "predecessor",
            "threshold",
            "missing",
        )
        for mutation in mutations:
            with (
                self.subTest(mutation=mutation),
                tempfile.TemporaryDirectory() as directory,
            ):
                target = private_export(Path(directory))
                if mutation == "source":
                    with (Path(directory) / GEOMETRY).open("ab") as handle:
                        handle.write(b"\n# changed\n")
                elif mutation in ("schema", "usage", "inventory"):
                    path = target / "SOURCES.json"
                    value = json.loads(path.read_bytes())
                    if mutation == "schema":
                        value["schema_version"] = True
                    elif mutation == "usage":
                        value["files"] = [
                            {**row, "usage": "provenance"} for row in value["files"]
                        ]
                    else:
                        value["files"].append(value["files"][0])
                    path.write_text(json.dumps(value))
                elif mutation == "predecessor":
                    path = target / "PREDECESSORS.json"
                    value = json.loads(path.read_bytes())
                    value["schema_version"] = True
                    path.write_text(json.dumps(value))
                elif mutation == "threshold":
                    path = target / "RESULT.json"
                    value = json.loads(path.read_bytes())
                    value["concentration_threshold"] = 13
                    path.write_text(json.dumps(value))
                else:
                    (target / "vendor/pr3295-PROOF.md").unlink()
                code, output = run(target)
                self.assertNotEqual(code, 0, output)
                self.assertNotIn("PASS_D6_AXIS_CONCENTRATION", output)

    def test_optimized_export_and_formatting(self):
        with tempfile.TemporaryDirectory() as directory:
            target = private_export(Path(directory))
            path = target / "RESULT.json"
            path.write_text(
                json.dumps(json.loads(path.read_bytes()), separators=(",", ":"))
            )
            for script in ("verify.py", "independent.py"):
                code, output = run(target, script)
                self.assertEqual(code, 0, output)
                self.assertIn("PASS_D6_AXIS", output)


if __name__ == "__main__":
    unittest.main()
