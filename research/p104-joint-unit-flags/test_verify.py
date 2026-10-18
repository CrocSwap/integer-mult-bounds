# SPDX-License-Identifier: Apache-2.0
"""Behavior and rejecting controls for the actual static-flag checkers."""

import copy
import importlib.util
import json
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(package, script="verify.py", *arguments):
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-O",
            "-Werror",
            "-B",
            str(package / script),
            *arguments,
        ],
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )


def export(root):
    package = root / "research/p104-joint-unit-flags"
    package.mkdir(parents=True)
    for source in PACKAGE.iterdir():
        if source.suffix in {".py", ".json", ".md", ".tsv"}:
            shutil.copyfile(source, package / source.name)
    for row in json.loads((PACKAGE / "SOURCES.json").read_bytes())["files"]:
        if row["usage"] == "input":
            target = root / row["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row["path"], target)
    return package


class Behavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary = load("verify")
        cls.oracle = load("independent")
        cls.original = cls.oracle.residuals(*cls.oracle.sources())
        cls.certificate = cls.oracle.read_json(PACKAGE / "CERTIFICATE.json")

    def test_real_cli_and_emission(self):
        for script, marker in [
            ("verify.py", "PASS_P104_JOINT_UNIT_FLAGS helpers=208"),
            ("independent.py", "PASS_P104_JOINT_UNIT_FLAGS_INDEPENDENT"),
        ]:
            result = run(PACKAGE, script)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(marker, result.stdout)
        result = run(PACKAGE, "verify.py", "--emit")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), self.certificate)

    def test_semantic_oracle_accepts_another_valid_basis(self):
        changed = copy.deepcopy(self.certificate)
        basis = changed["helpers"][0]["basis"]
        basis[2], basis[3] = basis[3], basis[2]
        self.assertNotEqual(changed, self.certificate)
        self.oracle.check(changed, self.original)

    def test_flag_and_bijection_faults(self):
        for fault in range(5):
            changed = copy.deepcopy(self.certificate)
            row = changed["helpers"][0]
            if fault == 0:
                changed["helpers"][1] = copy.deepcopy(row)
            elif fault == 1:
                row["basis"][0] = row["basis"][1]
            elif fault == 2:
                row["basis"][3] = row["basis"][2]
            elif fault == 3:
                row["basis"][6], row["basis"][7] = row["basis"][7], row["basis"][6]
            else:
                row["arrival_choice"] = True
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                self.oracle.check(changed, self.original)

    def test_cover_and_graph_faults(self):
        for fault in range(3):
            changed = copy.deepcopy(self.certificate)
            if fault == 0:
                pair = changed["forms"]["arrival"][0]
                pair[1] = pair[0]
            elif fault == 1:
                changed["forms"]["departure"][0][0] = True
            else:
                changed["graph"]["edges"] -= 1
            with self.subTest(fault=fault), self.assertRaises(ValueError):
                self.oracle.check(changed, self.original)

    def test_augmenting_and_hall_failure(self):
        self.assertEqual(self.primary.matching([[0, 1], [0]]), [1, 0])
        for graph in ([[0], [0]], [[], [0, 1]], [[2]], [[True]], [[]] * 209):
            with self.subTest(graph=graph[:2]), self.assertRaises(ValueError):
                self.primary.matching(graph)

    def test_git_free_read_only_export(self):
        with tempfile.TemporaryDirectory() as directory:
            package = export(Path(directory))
            files = [p for p in Path(directory).rglob("*") if p.is_file()]
            for path in files:
                path.chmod(0o444)
            try:
                for script in ("verify.py", "independent.py"):
                    result = run(package, script)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("PASS_P104_JOINT_UNIT_FLAGS", result.stdout)
            finally:
                for path in files:
                    path.chmod(0o644)

    def test_source_before_execution_and_poisoned_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            package = export(root)
            geometry = root / self.primary.GEOMETRY
            raw = geometry.read_bytes()
            geometry.write_text("raise RuntimeError('UNAUTHENTICATED_EXECUTION')\n")
            result = run(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("input SHA256", result.stderr)
            self.assertNotIn("UNAUTHENTICATED_EXECUTION", result.stderr)
            geometry.write_bytes(raw)
            poison = root / "poison.py"
            poison.write_text("raise RuntimeError('POISONED_CACHE')\n")
            # Registered replay gives this process a private cache prefix;
            # the isolated child ignores that prefix and uses this standard path.
            cache = (
                geometry.parent
                / "__pycache__"
                / (f"geometry.{sys.implementation.cache_tag}.opt-1.pyc")
            )
            cache.parent.mkdir()
            compiled = py_compile.compile(
                str(poison),
                cfile=str(cache),
                doraise=True,
                invalidation_mode=py_compile.PycInvalidationMode.UNCHECKED_HASH,
            )
            self.assertEqual(Path(compiled), cache)
            ordinary = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-O",
                    "-Werror",
                    "-B",
                    "-c",
                    "import importlib.util,sys; "
                    's=importlib.util.spec_from_file_location("ordinary",sys.argv[1]); '
                    "s.loader.exec_module(importlib.util.module_from_spec(s))",
                    str(geometry),
                ],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            self.assertNotEqual(ordinary.returncode, 0)
            self.assertIn("POISONED_CACHE", ordinary.stderr)
            result = run(package)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_P104_JOINT_UNIT_FLAGS", result.stdout)

    def test_serialized_faults(self):
        with tempfile.TemporaryDirectory() as directory:
            package = export(Path(directory))
            path = package / "CERTIFICATE.json"
            raw = path.read_text()
            path.write_text(
                raw.replace('"schema_version": 1', '"schema_version": true')
            )
            for script in ("verify.py", "independent.py"):
                result = run(package, script)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("FAIL_P104_JOINT_UNIT_FLAGS", result.stderr)
            path.write_text('{"schema_version":1,' + raw[1:])
            result = run(package)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate JSON key", result.stderr)


if __name__ == "__main__":
    unittest.main()
