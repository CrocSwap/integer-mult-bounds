"""Defect-sensitive controls for lifetime composition, source and semantics."""
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import runtime as source_runtime
import verify


class Controls(unittest.TestCase):
    def test_fallback_zero_half_is_owned(self):
        with source_runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "child entry budget"):
                verify.caller_case(m, good=False, child_limit=18)

    def test_good_child_undercharge(self):
        with source_runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "child entry budget"):
                verify.caller_case(m, child_limit=17)

    def test_restored_extra_stream_scratch_is_not_free(self):
        with source_runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "exact callback entry"):
                verify.caller_case(m, good=False, extra_scratch=True)

    def test_wrong_parent_return(self):
        with source_runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "same completed child returns"):
                verify.caller_case(m, good=False, wrong_parent=True)

    def test_callee_restoration_is_required(self):
        with source_runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "exact callback entry"):
                verify.caller_case(m, good=False, leak_callback=True)

    def test_twenty_two_callee_indices_compose(self):
        # This is a model callback attaining its allowance, not the actual
        # PR2796 coefficient evaluator or a whole-caller sharpness witness.
        with source_runtime.runtime() as m:
            row = verify.caller_case(m, good=False, callee_indices=22)
            self.assertEqual(row["peaks_with_abstract_coefficient"][1], 41)

    def test_non_add_one_word_undercharge(self):
        for kind in ("swap", "sign"):
            with self.subTest(kind=kind), source_runtime.runtime() as m:
                with self.assertRaisesRegex(ValueError, "numerical budget"):
                    verify.primitive_case(m, kind, 3, 1, budget=5)

    def test_omitted_translation_changes_sign_map(self):
        with source_runtime.runtime() as m:
            with self.assertRaisesRegex(ValueError, "complete Boolean permutation"):
                verify.primitive_case(m, "sign", 5, 2, omit_translation=True)

    def test_every_runtime_source_pin(self):
        snapshot = source_runtime.read_json(source_runtime.ROOT / "evidence/PR2801-SNAPSHOT.json")
        with tempfile.TemporaryDirectory(prefix="child-lifetime-control-") as directory:
            root = Path(directory)
            shutil.copytree(source_runtime.ROOT / "vendor", root / "vendor")
            (root / "vendor").chmod(0o755)
            (root / "evidence").mkdir()
            shutil.copyfile(source_runtime.ROOT / "evidence/PR2801-SNAPSHOT.json",
                            root / "evidence/PR2801-SNAPSHOT.json")
            with patch.object(source_runtime, "ROOT", root):
                for row in snapshot["files"]:
                    path = root / row["path"]
                    original = path.read_bytes()
                    path.chmod(0o644)
                    path.write_bytes(original + b"\n# mutation\n")
                    with self.subTest(path=row["path"]):
                        with self.assertRaisesRegex(ValueError, "source SHA256"):
                            source_runtime.authenticate()
                    path.write_bytes(original)
                path = root / "evidence/PR2801-SNAPSHOT.json"
                path.chmod(0o644)
                path.write_text("{}")
                with self.assertRaisesRegex(ValueError, "snapshot pin"):
                    source_runtime.authenticate()

    def test_authenticated_bytes_ignore_effective_stale_pyc(self):
        # The normal source loader would honor this timestamp-valid .pyc.
        # Our loader must execute authenticated source bytes instead.
        import py_compile
        with tempfile.TemporaryDirectory(prefix="child-lifetime-bytecode-") as directory:
            root = Path(directory)
            shutil.copytree(source_runtime.ROOT / "vendor", root / "vendor")
            (root / "vendor").chmod(0o755)
            (root / "evidence").mkdir()
            shutil.copyfile(source_runtime.ROOT / "evidence/PR2801-SNAPSHOT.json",
                            root / "evidence/PR2801-SNAPSHOT.json")
            target = root / "vendor/words.py"
            original = target.read_bytes()
            metadata = target.stat()
            malicious = b'raise RuntimeError("stale bytecode executed")\n'
            target.chmod(0o644)
            target.write_bytes(malicious + b" "*(len(original)-len(malicious)))
            import os
            os.utime(target, (metadata.st_atime, metadata.st_mtime))
            cache = importlib.util.cache_from_source(str(target))
            py_compile.compile(str(target), cfile=cache, doraise=True)
            target.write_bytes(original)
            os.utime(target, (metadata.st_atime, metadata.st_mtime))
            loader = importlib.machinery.SourceFileLoader("normal_words", str(target))
            spec = importlib.util.spec_from_loader("normal_words", loader)
            module = importlib.util.module_from_spec(spec)
            with self.assertRaisesRegex(RuntimeError, "stale bytecode executed"):
                loader.exec_module(module)
            with patch.object(source_runtime, "ROOT", root):
                with source_runtime.runtime() as m:
                    self.assertEqual(m.words.Arena(3).literal(2).inspect(), 2)

    def test_inherited_proof_pins(self):
        with tempfile.TemporaryDirectory(prefix="child-lifetime-dependencies-") as directory:
            root = Path(directory)
            shutil.copytree(source_runtime.ROOT / "evidence", root / "evidence")
            rows = source_runtime.read_json(root / "evidence/DEPENDENCIES.json")
            with patch.object(source_runtime, "ROOT", root):
                source_runtime.authenticate_dependencies()
                for row in rows:
                    path = root / row["export"]
                    original = path.read_bytes()
                    path.chmod(0o644)
                    path.write_bytes(original + b"\nchanged bound\n")
                    with self.subTest(path=row["export"]):
                        with self.assertRaisesRegex(ValueError, "dependency source SHA256"):
                            source_runtime.authenticate_dependencies()
                    path.write_bytes(original)

    def test_typed_receipt(self):
        row = source_runtime.read_json(source_runtime.ROOT / "RESULT.json")
        verify.compare_receipt(row, row)
        for defect in ("boolean", "missing", "undercharged"):
            altered = json.loads(json.dumps(row))
            if defect == "boolean":
                altered["no_new_kappa"] = 1
            elif defect == "missing":
                del altered["primitives"]
            else:
                altered["child_entry_indices"]["fallback"] = 18
            with self.subTest(defect=defect), self.assertRaisesRegex(ValueError, "typed receipt equality"):
                verify.compare_receipt(row, altered)


if __name__ == "__main__":
    unittest.main()
