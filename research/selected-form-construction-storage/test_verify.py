"""Behavioral and rejection checks for the literal constructor census."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))


class ConstructorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import verify

        cls.verify = verify

    def test_sharp_small_bounds(self):
        from census import run_case

        with self.verify.loaded() as modules:
            good = run_case(modules, "good", 3, 2, 3, 3)
            fallback = run_case(modules, "fallback", 3, 1, 3, 3)
        self.assertEqual((good["peak_extra"], good["stored"]), (84, 17))
        self.assertEqual((fallback["peak_extra"], fallback["stored"]), (71, 36))

    def test_one_word_underbudget_rejects_both(self):
        from census import run_case

        with self.verify.loaded() as modules:
            for kind, rank, budget in (("good", 2, 83), ("fallback", 1, 70)):
                with self.subTest(kind=kind), self.assertRaisesRegex(ValueError, "word budget exceeded"):
                    run_case(modules, kind, 3, rank, 3, 3, budget=budget)

    def test_omitted_input_matrix_rejects(self):
        from census import run_case

        with self.verify.loaded() as modules, self.assertRaisesRegex(ValueError, "word budget exceeded"):
            run_case(modules, "good", 3, 2, 3, 3, budget=84 - 9)

    def test_evaluator_allowance_does_not_cover_construction(self):
        from census import run_case

        with self.verify.loaded() as modules, self.assertRaisesRegex(ValueError, "word budget exceeded"):
            # Allow 36,879 total Words above unrelated borrowed residents.
            # Input projector plus modulus/one already consume 4,098 Words.
            run_case(modules, "good", 64, 42, 3, 3, budget=36879 - 4098)

    def test_borrowed_words_shift_total_peak(self):
        from census import run_case

        with self.verify.loaded() as modules:
            a = run_case(modules, "good", 3, 2, 3, 3)
            b = run_case(modules, "good", 3, 2, 3, 7)
        self.assertEqual(b["entry"] - a["entry"], 4)
        self.assertEqual((a["peak_extra"], b["peak_extra"]), (84, 84))

    def test_restored_entry_head_precondition(self):
        from census import Census, fixture

        with self.verify.loaded() as modules:
            arena, _mod, _ring, _residents, projector, _values = fixture(modules, "good", 3, 2, 3, 3)
            try:
                projector[0][0].head = 2
                with self.assertRaisesRegex(ValueError, "restored entry heads"), Census(modules, arena, 84):
                    self.fail("unrestored input was admitted")
            finally:
                arena.rollback(set())

    def test_algebra_and_preservation_guards(self):
        from algebra import check_form
        from census import check_preserved, fixture

        with self.verify.loaded() as modules:
            arena, _mod, ring, _residents, projector, values = fixture(modules, "good", 3, 2, 3, 3)
            saved = {slot: bytes(arena.words[slot].cells) for slot in arena.live}
            try:
                form = modules.forms.good_form(projector, 2, ring)
                arena.free(form.cross[0][0])
                form.cross[0][0] = arena.zero()
                with self.assertRaisesRegex(ValueError, "good cross endpoint"):
                    check_form(form, "good", values, 2, 3)
                projector[0][0].cells[1] ^= 1
                with self.assertRaisesRegex(ValueError, "borrowed numerical"):
                    check_preserved(arena, saved)
            finally:
                arena.rollback(set())
            self.assertFalse(arena.live)

    def test_source_rejections_need_explicit_rollback(self):
        with self.verify.loaded() as modules:
            cases = (("good", 3, [[0, 0], [0, 1]], "complete good class"),
                     ("good", 3, [[1, 0], [0, 1]], "northeast diagonal endpoint"),
                     ("fallback", 7, [[2, 0], [0, 0]], "terminal determinant sign"),
                     ("fallback", 6, [[3, 1], [0, 4]], "fallback unit pivot"))
            for kind, modulus, values, error in cases:
                with self.subTest(kind=kind, modulus=modulus):
                    arena = modules.words.Arena(modulus.bit_length() + 1, 256)
                    mod = arena.literal(modulus)
                    ring = modules.words.Ring(mod)
                    matrix = [[arena.literal(x) for x in row] for row in values]
                    saved = {slot: bytes(arena.words[slot].cells) for slot in arena.live}
                    with self.assertRaisesRegex(ValueError, error):
                        if kind == "good":
                            modules.forms.good_form(matrix, 1, ring)
                        else:
                            modules.forms.fallback_form(matrix, ring)
                    self.assertGreater(len(arena.live), len(saved))
                    arena.rollback(set(saved))
                    self.assertEqual({slot: bytes(arena.words[slot].cells) for slot in arena.live}, saved)
                    arena.rollback(set())

    def test_repeated_constructor_erases_scratch(self):
        from census import Census, check_preserved, fixture

        with self.verify.loaded() as modules:
            arena, _mod, ring, _residents, matrix, _values = fixture(modules, "fallback", 3, 1, 3, 3)
            saved = {slot: bytes(arena.words[slot].cells) for slot in arena.live}
            try:
                for _ in range(3):
                    with Census(modules, arena, 71) as census:
                        form = modules.forms.fallback_form(matrix, ring)
                    self.assertEqual(census.peak - census.entry, 71)
                    form.close(ring)
                    self.assertEqual(arena.live, set(saved))
                    check_preserved(arena, saved)
            finally:
                arena.rollback(set())

    def test_typed_receipt(self):
        expected = {"good": 33574, "fallback": 32645}
        for key, value in (("good", 33574.0), ("fallback", True), ("good", 33573)):
            actual = {**expected, key: value}
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "typed receipt"):
                self.verify.check_receipt(actual, expected)

    def test_source_and_manifest_corruption(self):
        mutations = (("head", "wrong"), ("path", "vendor/../words.py"),
                     ("git_blob", "0" * 40), ("source_path", "other/words.py"))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(PACKAGE / "vendor", root / "vendor")
            manifest = json.loads((PACKAGE / "SNAPSHOT.json").read_text())
            for key, value in mutations:
                changed = copy.deepcopy(manifest)
                (changed if key == "head" else changed["files"][0])[key] = value
                (root / "SNAPSHOT.json").write_text(json.dumps(changed))
                with self.subTest(key=key), self.assertRaises(ValueError):
                    self.verify.sources(root)
            (root / "SNAPSHOT.json").write_text(json.dumps(manifest))
            with (root / "vendor" / "words.py").open("ab") as handle:
                handle.write(b"\n# corrupt source\n")
            with self.assertRaisesRegex(ValueError, "source SHA256"):
                self.verify.sources(root)

    def test_authenticated_bytes_bypass_stale_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            shutil.copytree(PACKAGE / "vendor", root / "vendor")
            shutil.copy(PACKAGE / "SNAPSHOT.json", root / "SNAPSHOT.json")
            path = root / "vendor" / "words.py"
            original = path.read_bytes()
            stamp = path.stat().st_mtime_ns
            trap = b'raise RuntimeError("stale bytecode executed")\n'
            path.write_bytes(trap + b" " * (len(original) - len(trap)))
            os.utime(path, ns=(stamp, stamp))
            cache = importlib.util.cache_from_source(str(path), optimization="")
            py_compile.compile(str(path), cfile=cache, doraise=True,
                               invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
            path.write_bytes(original)
            os.utime(path, ns=(stamp, stamp))
            code = f"import sys; sys.path.insert(0, {str(root / 'vendor')!r}); import words"
            result = subprocess.run([sys.executable, "-I", "-B", "-c", code],
                                    capture_output=True, text=True, timeout=10, check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stale bytecode executed", result.stderr)
            with self.verify.loaded(root) as modules:
                arena = modules.words.Arena(3, 1)
                word = arena.literal(2)
                self.assertEqual(word.inspect(), 2)
                arena.free(word)


if __name__ == "__main__":
    unittest.main()
