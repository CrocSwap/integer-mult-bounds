"""Controls for prefix demand, numerical-neutrality, source pins and semantics."""
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
verify = ModuleType("caller_capacity_verify")
verify.__file__ = str(ROOT / "verify.py")
exec(compile((ROOT / "verify.py").read_bytes(), verify.__file__, "exec"), verify.__dict__)


class Controls(unittest.TestCase):
    def test_request_counted_before_success(self):
        with verify.frozen_probe() as (probe, runtime), runtime.runtime() as m:
            arena = m.words.Arena(3, 20)
            Census, _ = verify.instrument(probe, (1,), (0,))
            census = Census(m, (arena,), (0,))
            with self.assertRaisesRegex(ValueError, "pending allocation budget"):
                census.allocate(arena)
            self.assertEqual(census.pending, [1])
            self.assertEqual(arena.live, set())
            self.assertEqual(arena.words, [])
            self.assertEqual(arena.meter.allocations, 0)

    def test_canonical_warm_backing_is_an_entry_term(self):
        with verify.frozen_probe() as (probe, runtime), runtime.runtime() as m:
            arena = m.words.Arena(3, 20)
            resident = arena.literal(2)
            Census, _ = verify.instrument(probe, (2,), (6,))
            census = Census(m, (arena,), (2,))
            self.assertEqual(census.entry, (1,))
            self.assertEqual(census.backing, (7,))
            self.assertEqual(census.capacities, (7,))
            for _ in range(9):
                w = census.allocate(arena)
                arena.free(w)
            census.restored()
            self.assertEqual(resident.inspect(), 2)
            self.assertEqual(len(arena.words), 7)

    def test_numerically_neutral_stream_premise(self):
        with verify.frozen_probe() as (probe, runtime), runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "exact callback entry"):
                probe.caller_case(m, extra_scratch=True)

    def test_callback_restoration_premise(self):
        with verify.frozen_probe() as (probe, runtime), runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "exact callback entry"):
                probe.caller_case(m, leak_callback=True)

    def test_sign_translation_is_semantic(self):
        with verify.frozen_probe() as (probe, runtime), runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "complete Boolean permutation"):
                probe.primitive_case(m, "sign", 5, 2, omit_translation=True)

    def test_frozen_input_integrity_and_inventory(self):
        with tempfile.TemporaryDirectory(prefix="caller-capacity-integrity-") as d:
            root = Path(d)
            for name in ("predecessor", "evidence"):
                shutil.copytree(ROOT / name, root / name)
            shutil.copyfile(ROOT / "SNAPSHOTS.json", root / "SNAPSHOTS.json")
            with patch.object(verify, "ROOT", root):
                verify.authenticate()
                for row in verify.read_json(root / "SNAPSHOTS.json")["files"]:
                    f = root / row["path"]
                    original = f.read_bytes()
                    f.chmod(0o644)
                    f.write_bytes(original + b"\nchanged resource premise\n")
                    with self.subTest(path=row["path"]), self.assertRaisesRegex(ValueError, "frozen source SHA256"):
                        verify.authenticate()
                    f.write_bytes(original)
                f = root / "predecessor/vendor/words.py"
                f.parent.chmod(0o755)
                f.unlink()
                with self.assertRaisesRegex(ValueError, "closed frozen input inventory"):
                    verify.authenticate()
                f = root / "SNAPSHOTS.json"
                f.chmod(0o644); f.write_text("{}")
                with self.assertRaisesRegex(ValueError, "snapshot manifest pin"):
                    verify.authenticate()

    def test_effective_bytecode_cannot_replace_frozen_harness(self):
        with tempfile.TemporaryDirectory(prefix="caller-capacity-bytecode-") as d:
            root = Path(d)
            for name in ("predecessor", "evidence"):
                shutil.copytree(ROOT / name, root / name)
            shutil.copyfile(ROOT / "SNAPSHOTS.json", root / "SNAPSHOTS.json")
            f = root / "predecessor/verify.py"
            original, metadata = f.read_bytes(), f.stat()
            evil = b'raise RuntimeError("stale fixture bytecode")\n'
            f.chmod(0o644)
            f.parent.chmod(0o755)
            f.write_bytes(evil + b" "*(len(original)-len(evil)))
            os.utime(f, (metadata.st_atime, metadata.st_mtime))
            py_compile.compile(str(f), doraise=True)
            f.write_bytes(original)
            os.utime(f, (metadata.st_atime, metadata.st_mtime))
            loader = importlib.machinery.SourceFileLoader("stale_probe", str(f))
            spec = importlib.util.spec_from_loader("stale_probe", loader)
            module = importlib.util.module_from_spec(spec)
            with self.assertRaisesRegex(RuntimeError, "stale fixture bytecode"):
                loader.exec_module(module)
            with patch.object(verify, "ROOT", root), verify.frozen_probe() as (probe, runtime):
                self.assertTrue(callable(probe.caller_case))
                with runtime.runtime() as m:
                    self.assertEqual(m.words.Arena(3).literal(2).inspect(), 2)

    def test_typed_receipt(self):
        expected = verify.read_json(ROOT / "RESULT.json")
        verify.compare_receipt(expected, expected)
        for defect in ("boolean", "demand", "missing"):
            changed = json.loads(json.dumps(expected))
            if defect == "boolean":
                changed["no_new_kappa"] = 1
            elif defect == "demand":
                changed["actual_underquota_failures"][0]["pending_peaks"][0] -= 1
            else:
                del changed["closed_coefficient_bodies"]
            with self.subTest(defect=defect), self.assertRaisesRegex(ValueError, "typed receipt equality"):
                verify.compare_receipt(changed, expected)


if __name__ == "__main__":
    unittest.main()
