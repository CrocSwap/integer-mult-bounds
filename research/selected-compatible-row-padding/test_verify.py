"""Behavioral and provenance controls for the public wrapper and replay CLI."""

import importlib
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source import PACKAGE, authenticate, installed


def content(tape):
    return bytes(tape.cells[1:]).rstrip(b"\x04")


class WrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scope = installed()
        cls.scope.__enter__()
        cls.counts = importlib.import_module("cardinal_counts")
        cls.records = importlib.import_module("records")
        cls.padding = importlib.import_module("padding")

    @classmethod
    def tearDownClass(cls):
        cls.scope.__exit__(None, None, None)

    def test_literal_two_prefix_endpoint(self):
        source = self.records.Tape()
        data = bytes((1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0))
        for bit in data:
            source.append(bit)
        source.rewind()
        counts = tuple(self.counts.Count.literal(v) for v in (2, 3, 2, 2))

        def callee(padded, rows):
            self.assertEqual(
                content(padded), bytes((1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0))
            )
            self.assertEqual(content(rows.tape), bytes((0, 0, 1, 3)))
            out = self.records.Tape()
            values = content(padded)
            for start in range(0, 16, 2):
                for bit in values[start : start + 2][::-1]:
                    out.append(bit)
            out.rewind()
            return out

        try:
            out = self.padding.complete(source, *counts, callee)
            self.assertEqual(content(out), bytes((0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1)))
            self.assertEqual(content(source), data)
            self.assertEqual(source.head, 1)
            out.clear()
        finally:
            source.clear()
            for count in counts:
                count.close()

    def test_rejected_output_erases_owned_buffers(self):
        tapes = []

        class Observed(self.records.Tape):
            def __init__(self):
                super().__init__()
                tapes.append(self)

        previous = self.padding.Tape
        self.padding.Tape = Observed
        source = Observed()
        for bit in (1, 0, 1, 0, 1):
            source.append(bit)
        source.rewind()
        counts = tuple(self.counts.Count.literal(v) for v in (1, 5, 3, 1))

        def callee(padded, rows):
            out = Observed()
            for _ in range(6):
                out.append(1)
            out.rewind()
            return out

        try:
            with self.assertRaisesRegex(ValueError, "added rows zero"):
                self.padding.complete(source, *counts, callee)
            self.assertEqual(content(source), bytes((1, 0, 1, 0, 1)))
            for tape in tapes[1:]:
                self.assertEqual(content(tape), b"")
                self.assertEqual(tape.head, 1)
            self.assertEqual(len(tapes), 4)
        finally:
            for tape in tapes:
                tape.clear()
            for count in counts:
                count.close()
            self.padding.Tape = previous

    def test_capacity_rejects_before_payload(self):
        rows, stock = (self.counts.Count.literal(v) for v in (3, 4))
        try:
            with self.assertRaisesRegex(ValueError, "capacity"):
                self.padding.plan_rows(rows, stock)
            self.assertEqual(content(rows.tape), bytes((1, 1, 3)))
            self.assertEqual(content(stock.tape), bytes((0, 0, 1, 3)))
        finally:
            rows.close()
            stock.close()

    def test_large_binary_plan(self):
        rows, stock = (self.counts.Count.literal(v) for v in (1000, 128))
        padded = added = None
        try:
            padded, added = self.padding.plan_rows(rows, stock)
            self.assertEqual(content(padded.tape), bytes([0] * 10 + [1, 3]))
            self.assertEqual(content(added.tape), bytes((0, 0, 0, 1, 1, 3)))
        finally:
            for count in (rows, stock, padded, added):
                if count is not None:
                    count.close()


class IntegrityTests(unittest.TestCase):
    def command(self, package, *arguments):
        return subprocess.run(
            [sys.executable, "-O", "-B", str(package / "verify.py"), *arguments],
            capture_output=True,
            text=True,
            timeout=120,
        )

    def test_symlinked_temporary_root(self):
        with TemporaryDirectory() as temporary:
            real = Path(temporary) / "real"
            real.mkdir()
            alias = Path(temporary) / "alias"
            try:
                alias.symlink_to(real, target_is_directory=True)
            except OSError as error:
                self.skipTest("symlink fixture unavailable: " + str(error))
            code = (
                "import sys,tempfile;sys.path.insert(0,sys.argv[1]);"
                "tempfile.tempdir=sys.argv[2];from source import installed,require\n"
                "with installed() as (_,root):\n"
                " import bootstrap\n"
                " require(root==root.resolve()==bootstrap.ROOT,\n"
                "         'resolved source root')\n"
                "print('PASS_SYMLINK_EXPORT_ROOT')\n"
            )
            run = subprocess.run(
                [sys.executable, "-B", "-c", code, str(PACKAGE), str(alias)],
                capture_output=True,
                text=True,
                timeout=15,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(run.stdout.strip(), "PASS_SYMLINK_EXPORT_ROOT")

    def test_missing_source_member(self):
        with TemporaryDirectory() as temporary:
            copied = Path(temporary) / "package"
            shutil.copytree(PACKAGE, copied)
            manifest = json.loads((copied / "PREDECESSOR.json").read_text())
            manifest["files"].pop()
            (copied / "PREDECESSOR.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "84-file"):
                authenticate(copied)

    def test_git_blob_corruption(self):
        with TemporaryDirectory() as temporary:
            copied = Path(temporary) / "package"
            shutil.copytree(PACKAGE, copied)
            manifest = json.loads((copied / "PREDECESSOR.json").read_text())
            manifest["files"][0]["git_blob"] = "0" * 40
            (copied / "PREDECESSOR.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "Git blob pin"):
                authenticate(copied)

    def test_source_corruption(self):
        with TemporaryDirectory() as temporary:
            copied = Path(temporary) / "package"
            shutil.copytree(PACKAGE, copied)
            archive = copied / "predecessor.tar.gz"
            data = bytearray(archive.read_bytes())
            data[-12] ^= 1
            archive.write_bytes(data)
            run = self.command(copied)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("archive SHA256", run.stderr)

    def test_typed_receipt_and_git_free_optimized_replay(self):
        with TemporaryDirectory() as temporary:
            copied = Path(temporary) / "package"
            shutil.copytree(PACKAGE, copied)
            good = self.command(copied)
            self.assertEqual(good.returncode, 0, good.stderr)
            receipt = json.loads((copied / "CORE.json").read_text())
            receipt["controls"]["semantic_endpoint_control"] = True
            (copied / "CORE.json").write_text(json.dumps(receipt))
            bad = self.command(copied)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("typed receipt", bad.stderr)

    def test_preloaded_source_module_rejects(self):
        code = (
            "import runpy,sys,types;sys.modules['records']=types.ModuleType('records');"
            "target=sys.argv.pop();runpy.run_path(target,run_name='__main__')"
        )
        run = subprocess.run(
            [sys.executable, "-B", "-c", code, str(PACKAGE / "verify.py")],
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("preloaded predecessor", run.stderr)


if __name__ == "__main__":
    unittest.main()
