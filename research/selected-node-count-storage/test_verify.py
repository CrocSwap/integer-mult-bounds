"""Behavior and failure controls for the count-storage replay."""
from copy import deepcopy
import gzip
import importlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

import verify


def decode(value):
    cells = value.tape.cells[1:]
    stop = cells.index(3)
    return sum(bit << position for position, bit in enumerate(cells[:stop]))


class CountBehavior(unittest.TestCase):
    def test_padding_counts_real_constructor_interval(self):
        with verify.sources():
            result = verify.padding_fixture(8)
        self.assertEqual(result, {"digits": 8, "peak_symbols": 29, "peak_tapes": 3,
                                  "peak_single": 10, "count_writes": 78})

    def test_product_preserves_operands_and_erases_temporaries(self):
        with verify.sources():
            Count = importlib.import_module("cardinal_counts").Count
            census = verify.Census()
            with census.install():
                left, right = Count.literal(1023), Count.literal(17)
                product = Count.product(left, right)
                self.assertEqual((decode(left), decode(right), decode(product)), (1023, 17, 17391))
                self.assertEqual(len(census.live), 3)
                for value in (left, right, product):
                    value.close()
                self.assertEqual((census.symbols, len(census.live)), (0, 0))

    def test_countdowns_with_padding_and_boundary_carries(self):
        with verify.sources():
            Count = importlib.import_module("cardinal_counts").Count
            Counter = importlib.import_module("stream").Counter
            census = verify.Census()
            with census.install():
                for initial in (0, 1, 2, 127, 128, 1025):
                    source = Count.literal(initial)
                    padded = source.marginal()
                    countdown = Counter(padded)
                    for expected in range(initial, 0, -1):
                        self.assertFalse(countdown.finished)
                        self.assertEqual(decode(countdown), expected)
                        countdown.decrement()
                    self.assertTrue(countdown.finished)
                    self.assertEqual(decode(countdown), 0)
                    self.assertEqual(decode(source), initial)
                    for value in (countdown, padded, source):
                        value.close()
                self.assertEqual(census.symbols, 0)

    def test_underbudget_and_observer_bypass_reject(self):
        with verify.sources():
            self.assertEqual(verify.controls(), ["literal-constructor-temporary-budget",
                                                  "direct-cell-observer-bypass"])

    def test_observed_inventory_exhaustion_rejects(self):
        with verify.sources():
            Count = importlib.import_module("cardinal_counts").Count
            with self.assertRaisesRegex(ValueError, "bounded observed count inventory"):
                with verify.Census().install():
                    retained = [Count.literal(1) for _ in range(100)]
                    self.fail("constructor inventory accepted: " + str(len(retained)))
            with self.assertRaisesRegex(ValueError, "bounded observed count inventory"):
                with verify.Census().install():
                    Count.literal(1 << 2048)

    def test_tape_substitutions_restore_after_failure(self):
        with verify.sources():
            modules = [importlib.import_module(name) for name in ("cardinality", "counts", "stream")]
            originals = [module.Tape for module in modules]
            with self.assertRaisesRegex(RuntimeError, "fixture interruption"):
                with verify.Census().install():
                    raise RuntimeError("fixture interruption")
            self.assertEqual([module.Tape for module in modules], originals)


class SnapshotBehavior(unittest.TestCase):
    def test_preloaded_source_module_rejects(self):
        with patch.dict(sys.modules, {"cardinality": ModuleType("cardinality")}):
            with self.assertRaisesRegex(ValueError, "source module collision"):
                with verify.sources():
                    self.fail("foreign module accepted")

    def test_recompression_preserves_the_same_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "recompressed.gz"
            payload = gzip.decompress((verify.HERE / "SOURCE.tar.gz").read_bytes())
            archive.write_bytes(gzip.compress(payload, compresslevel=1, mtime=123456))
            destination = root / "export"
            verify.unpack(destination, archive=archive)
            self.assertEqual(len(list(destination.rglob("*.py"))), 43)

    def test_changed_digest_and_duplicate_manifest_reject(self):
        manifest = json.loads((verify.HERE / "SNAPSHOT.json").read_text())
        bad = deepcopy(manifest)
        bad["files"][0]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(ValueError, "snapshot source digest"):
                verify.unpack(Path(temporary), manifest=bad)
            bad = deepcopy(manifest)
            bad["files"][0] = bad["files"][1]
            with self.assertRaisesRegex(ValueError, "unique snapshot paths"):
                verify.unpack(Path(temporary), manifest=bad)

    def test_archive_path_escape_rejects_before_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "bad.gz"
            with tarfile.open(archive, "w:gz") as output:
                member = tarfile.TarInfo("../escape")
                member.size = 1
                output.addfile(member, io.BytesIO(b"x"))
            with self.assertRaisesRegex(ValueError, "regular declared snapshot path"):
                verify.unpack(root / "export", archive=archive)
            self.assertFalse((root / "escape").exists())

    def test_wrong_typed_receipt_rejects_in_optimized_export(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("verify.py", "ROOTS.json", "SNAPSHOT.json", "SOURCE.tar.gz", "RESULT.json"):
                (root / name).write_bytes((verify.HERE / name).read_bytes())
            result = json.loads((root / "RESULT.json").read_text())
            result["padding"][0]["digits"] = True
            (root / "RESULT.json").write_text(json.dumps(result))
            run = subprocess.run([sys.executable, "-I", "-O", "-Werror", "-B", str(root / "verify.py"),
                                  "--quick"], capture_output=True, text=True, timeout=30, cwd=root)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("exact typed count-storage receipt", run.stderr)


if __name__ == "__main__":
    unittest.main()
