#!/usr/bin/env python3
"""Behavior, source, quota and receipt controls for the scaling audit."""

import ast
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import source
import verify
from observe import Observer
from traffic import allocations, countdown, invoice

PACKAGE = Path(__file__).resolve().parent


@contextmanager
def exported():
    with tempfile.TemporaryDirectory(prefix="scaling-traffic-test-") as directory:
        root = Path(directory)
        package = root / "research/high-scaling-total-traffic"
        shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
        rows = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
        for row in rows:
            if row["usage"] == "input":
                target = root / row["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source.ROOT / row["path"], target)
        yield root, package


def cli(package):
    return subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def wrong_direction(node):
    matches = 0
    for item in ast.walk(node):
        if isinstance(item, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "alternating"
            for target in item.targets
        ):
            item.value = ast.copy_location(
                ast.UnaryOp(op=ast.Not(), operand=item.value), item.value
            )
            matches += 1
    if matches != 1:
        raise ValueError("one alternating direction")
    return ast.fix_missing_locations(node)


def missing_cleanup(node):
    class RemoveClose(ast.NodeTransformer):
        count = 0

        def visit_Expr(self, item):
            if (
                isinstance(item.value, ast.Call)
                and ast.unparse(item.value) == "even.close()"
            ):
                self.count += 1
                return None
            return item

    transform = RemoveClose()
    node = transform.visit(node)
    if transform.count != 1:
        raise ValueError("one even-count cleanup")
    return node


class ScalingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = source.authenticated()

    def test_literal_invoices_and_counter_credit(self):
        self.assertEqual(
            (countdown(0, 8), countdown(1, 1), countdown(2, 2)), (152, 60, 89)
        )
        observer = Observer(self.data)
        for q, b, s, expected in ((3, 1, 1, 718), (5, 2, 1, 1486), (7, 3, 5, 10543)):
            for inverse in (False, True):
                row = observer.run(q, b, s, inverse)
                self.assertEqual(row["traffic"], expected)
                self.assertEqual(sum(invoice(q, b, s).values()), expected)
                self.assertEqual(row["allocations"], allocations(q, b, s))

    def test_analytic_envelopes_include_large_encoded_parameters(self):
        labels = ("validation", "setup_cleanup", "payload", "outer", "rows", "suffix")
        factors = (8, 80, 34, 44, 98, 160)
        for q in (3, 5, 7, 15, 17, 129, 2**1024 - 1, 2**1024 + 1, 2**1024 + 3):
            for b in (1, 2, 2**128):
                for s in (1, 3, 2**256):
                    with self.subTest(
                        q_bits=q.bit_length(),
                        b_bits=b.bit_length(),
                        s_bits=s.bit_length(),
                    ):
                        volume = q * b * s
                        bill = invoice(q, b, s)
                        for label, factor in zip(labels, factors, strict=True):
                            self.assertLessEqual(bill[label], factor * volume)
                        self.assertLessEqual(allocations(q, b, s), 6 * volume)
                        self.assertLess(
                            sum(bill.values()) + allocations(q, b, s), 1024 * volume
                        )

    def test_endpoint_only_does_not_certify_time(self):
        observer = Observer(self.data)
        baseline = observer.run(65, 2, 1)
        inflated = observer.run(65, 2, 1, extra=True)
        self.assertEqual((baseline["traffic"], inflated["traffic"]), (10354, 49874))
        self.assertEqual(
            inflated["traffic"] - baseline["traffic"], 2 * 2 * 65 * countdown(0, 8)
        )
        self.assertNotEqual(inflated["traffic"], sum(invoice(65, 2, 1).values()))

    def test_wrong_direction_fails_complete_origin_map(self):
        observer = Observer(self.data, wrong_direction)
        with self.assertRaisesRegex(ValueError, "complete origin map"):
            observer.run(5, 2, 3)

    def test_omitted_cleanup_fails_actual_erasure(self):
        observer = Observer(self.data, missing_cleanup)
        with self.assertRaisesRegex(ValueError, "private erasure"):
            observer.run(5, 2, 3)

    def test_malformed_streams_reject(self):
        observer = Observer(self.data)
        for defect in ("short", "long", "non-bit"):
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                observer.run(5, 2, 3, malformed=defect)
        with self.assertRaisesRegex(ValueError, "odd high modulus"):
            observer.run(4, 1, 1)

    def test_canonical_width_is_an_actual_ring_premise(self):
        observer = Observer(self.data)
        arena = observer.modules["words"].Arena(4096, capacity=8)
        modulus = arena.input(3)
        with self.assertRaisesRegex(ValueError, "canonical modulus"):
            observer.modules["words"].Ring(modulus)
        self.assertEqual(arena.live, {modulus.slot})
        arena.free(modulus)
        padded = observer.run(3, 1, 1, digits=4096)
        self.assertEqual(padded["traffic"], 74392)
        self.assertGreater(padded["traffic"], 1024 * 3)

    def test_encoding_and_fixture_limits(self):
        for arguments in ((2, 1, 1), (3, 0, 1), (3, True, 1), (3, 1, 1, 1)):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                invoice(*arguments)
        with self.assertRaisesRegex(ValueError, "fixture volume"):
            Observer(self.data).run(129, 100, 100)
        with self.assertRaisesRegex(ValueError, "fixture width"):
            Observer(self.data).run(3, 1, 1, digits=4097)

    def test_shared_sources_match_original_exports(self):
        # These paths are exact exports, not regenerated variants of the runtime.
        exports = json.loads(
            self.data["research/linear-sign-total-traffic/EXPORTS.json"]
        )
        by_name = {Path(row["path"]).stem: row for row in exports["files"]}
        for name in source.CORE:
            body = self.data[source.PREFIX + name + ".py"]
            self.assertEqual(hashlib.sha256(body).hexdigest(), by_name[name]["sha256"])

    def test_missing_dependency_rejects_before_execution(self):
        with exported() as (root, package):
            manifest = json.loads((package / "SOURCES.json").read_text())
            manifest["files"] = [
                row for row in manifest["files"] if row["path"] != source.ROUTES
            ]
            (package / "SOURCES.json").write_text(json.dumps(manifest))
            with (
                patch.object(source, "ROOT", root),
                patch.object(source, "PACKAGE", package),
                self.assertRaisesRegex(ValueError, "complete proof-relevant"),
            ):
                source.authenticated()

    def test_source_corruption_rejects_actual_cli(self):
        with exported() as (root, package):
            path = root / source.KERNELS
            path.write_bytes(path.read_bytes() + b"\n# altered source\n")
            completed = cli(package)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("source digest", completed.stderr)
            self.assertNotIn("PASS_HIGH_SCALING", completed.stdout)

    def test_typed_receipt_corruption_rejects_actual_cli(self):
        with exported() as (_root, package):
            receipt = json.loads((package / "RESULT.json").read_text())
            receipt["scaling"]["cases"] = True
            (package / "RESULT.json").write_text(json.dumps(receipt))
            completed = cli(package)
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("complete typed receipt mismatch", completed.stderr)
            self.assertNotEqual(
                verify.canonical({"x": True}), verify.canonical({"x": 1})
            )

    def test_read_only_export_runs_without_git(self):
        with exported() as (root, package):
            files = [p for p in root.rglob("*") if p.is_file()]
            initial = {p.relative_to(root).as_posix(): p.read_bytes() for p in files}
            for path in files:
                path.chmod(0o444)
            completed = cli(package)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("PASS_HIGH_SCALING_TOTAL_TRAFFIC", completed.stdout)
            final = {
                p.relative_to(root).as_posix(): p.read_bytes()
                for p in root.rglob("*")
                if p.is_file()
            }
            self.assertEqual(final, initial)


if __name__ == "__main__":
    unittest.main()
