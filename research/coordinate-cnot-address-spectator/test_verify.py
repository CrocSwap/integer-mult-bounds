"""Mathematical and fail-closed checks for the scoped certificate.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
Apache-2.0.
"""
import contextlib
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
spec = importlib.util.spec_from_file_location("spectator_verify", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
I = V.load_independent()


@contextlib.contextmanager
def exported_package():
    with tempfile.TemporaryDirectory(prefix="address-spectator-test-") as directory:
        root = Path(directory)
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
            if item["usage"] == "input":
                dest = root / item["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / item["path"], dest)
        try:
            yield root, package
        finally:
            # Restore only the temporary files this fixture created.
            for path in root.rglob("*"):
                path.chmod(0o755 if path.is_dir() else 0o644)
            root.chmod(0o755)


def execute(package, root):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                          cwd=root, text=True, capture_output=True, timeout=120)


class CertificateChecks(unittest.TestCase):
    def test_algebra_natural_map_and_dense_updates(self):
        """Check the matrix-image implication on the complete two-call alphabet."""
        for r in (2, 3):
            n = 3 * r
            gates = V.generators(r)
            eye = V.identity(n)
            images = [V.step(eye, gate, n) for gate in gates]
            # Dense input catches bit-packing mistakes hidden by the identity.
            dense = sum(1 << (row * n + col) for row in range(n) for col in range(n)
                        if (row * 7 + col * 11 + row * col) % 5 < 3)
            for gate, image in zip(gates, images):
                self.assertEqual(V.step(dense, gate, n), V.matrix_product(image, dense, n))
                self.assertEqual(V.natural_image(V.formal_evaluate([gate], r), r), image)
            for first, first_image in zip(gates, images):
                formal = V.formal_evaluate([first], r)
                for second in gates:
                    self.assertEqual(V.natural_image(V.formal_step(formal, second, r), r),
                                     V.step(first_image, second, n))

    def test_algebra_free_scalar_conjugation_closure(self):
        for r in (2, 3):
            mask = (1 << r) - 1
            invertibles = [code for code in range(1 << (r * r))
                           if I.rank([(code >> (k * r)) & mask for k in range(r)]) == r]
            projectors = {p for _, _, p in V.projectors(r)}
            for basis in invertibles:
                inverse = next(q for q in invertibles
                               if V.matrix_product(basis, q, r) == V.identity(r))
                for p in projectors:
                    transformed = V.matrix_product(V.matrix_product(basis, p, r), inverse, r)
                    self.assertIn(transformed, projectors)
            self.assertEqual(len(invertibles), {2: 6, 3: 168}[r])

    def test_independent_projectors_and_address_group(self):
        # Independently enumerate all 512 possible binary address matrices.
        address_group = {code for code in range(512)
                         if I.rank([(code >> (3 * row)) & 7 for row in range(3)]) == 3}
        self.assertEqual(len(address_group), 168)
        address_gates = [V.identity(3) ^ (1 << (i * 3 + j))
                         for i in range(3) for j in range(3) if i != j]
        reached = {V.identity(3)}
        while True:
            new = {V.matrix_product(a, b, 3) for a in reached for b in address_gates}
            if new <= reached:
                break
            reached |= new
        self.assertEqual(reached, address_group)
        for r in (2, 3):
            other = {sum(row << (k * r) for k, row in enumerate(rows))
                     for rows in I.all_projectors(r)}
            self.assertEqual(other, {p for _, _, p in V.projectors(r)})

    def test_receipt_mutations(self):
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        mutants = []
        for key, value in (("edge_intersection", 1), ("generators", 167),
                           ("address_dimension", 2), ("registers", 4),
                           ("minimum_paid_calls", 5), ("edge_attempts_per_engine", 0),
                           ("ball_2_sha256", "0" * 64)):
            mutant = copy.deepcopy(expected)
            mutant["cases"][1][key] = value
            mutants.append(mutant)
        mutant = copy.deepcopy(expected)
        mutant["cases"].pop()
        mutants.append(mutant)
        for mutant in mutants:
            with self.assertRaisesRegex(ValueError, "receipt mismatch"):
                V.check_receipt(expected, mutant)

    def test_real_receipt_corruption_rejected(self):
        with exported_package() as (root, package):
            path = package / "EXPECTED.json"
            bad = json.loads(path.read_text())
            bad["cases"][1]["edge_intersection"] = 1
            path.write_text(json.dumps(bad))
            result = execute(package, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("receipt mismatch", result.stderr)

    def test_real_source_corruption_rejected(self):
        with exported_package() as (root, package):
            item = next(x for x in json.loads((package / "SOURCES.json").read_text())["files"]
                        if x["usage"] == "input")
            path = root / item["path"]
            path.write_bytes(path.read_bytes() + b"\nsource mutation\n")
            result = execute(package, root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source pin mismatch", result.stderr)

    def test_read_only_relocated_optimized_replay(self):
        with exported_package() as (root, package):
            for path in root.rglob("*"):
                path.chmod(0o555 if path.is_dir() else 0o444)
            root.chmod(0o555)
            result = execute(package, root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_COORDINATE_CNOT_ADDRESS_SPECTATOR", result.stdout)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
