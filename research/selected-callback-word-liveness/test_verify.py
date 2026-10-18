#!/usr/bin/env python3
"""Behavioral budget, preservation and authenticated-export controls."""
from __future__ import annotations

import importlib.util
import json
import py_compile
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("liveness_verifier", PACKAGE / "verify.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class Behavior(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = VERIFY.load_sources()

    def reject_budget(self, modes, residues, indices, page=False):
        case, current = VERIFY.page_fixture(self.modules) if page else (
            VERIFY.fixture(self.modules, modes), None)
        saved = set(case.residues.live), set(case.indices.live)
        contents = tuple({slot: bytes(arena.words[slot].cells) for slot in arena.live}
                         for arena in (case.residues, case.indices))
        source_bytes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
        with self.assertRaisesRegex(ValueError, "word budget exceeded"), VERIFY.Census(
                self.modules, case.residues, case.indices, residues, indices):
            if current:
                request = SimpleNamespace(kind="child", child_kind="pair", field=0, reverse=False,
                                          coordinate=case.coordinate, negative_inverse=False)
                current.evaluate(request)
            else:
                case.callback.weight(case.coordinate)
        # The primitive's exception boundary requires explicit caller rollback.
        for arena, protected in zip((case.residues, case.indices), saved, strict=True):
            arena.rollback(protected)
        for stack in (case.callback.pending, case.callback.values):
            stack.tape.clear()
            stack.reverse.clear()
        case.program.tape.rewind()
        case.fields.tape.rewind()
        VERIFY.preserved(case, contents, source_bytes)
        VERIFY.cleanup(case, current)

    def test_one_fewer_index_word_rejects_good_branch(self):
        self.reject_budget("G", 20490, 9)

    def test_one_fewer_residue_word_rejects_fallback(self):
        self.reject_budget("P", 20489, 10)

    def test_omitted_retained_page_form_rejects(self):
        self.reject_budget("P", 4107, 23, page=True)

    def test_sharp_matrix_inverse_and_one_word_underbudget(self):
        self.assertEqual(VERIFY.inverse_case(self.modules, 2)["extra"], [18, 0])
        words = self.modules.words
        arena, indices = words.Arena(4, 64), words.Arena(8, 8)
        modulus = arena.literal(5)
        ring = words.Ring(modulus)
        matrices = self.modules.matrices.Matrices(ring)
        source = [[arena.literal(2)]]
        protected = set(arena.live)
        with self.assertRaisesRegex(ValueError, "word budget exceeded"), VERIFY.Census(
                self.modules, arena, indices, 11, 0):
            matrices.inverse(source)
        arena.rollback(protected)
        self.assertEqual(source[0][0].inspect(), 2)
        matrices.free(source)
        ring.close()
        arena.free(modulus)
        self.assertFalse(arena.live)

    def test_repeated_page_requests_preserve_inputs(self):
        case, page = VERIFY.page_fixture(self.modules)
        saved = tuple({slot: bytes(arena.words[slot].cells) for slot in arena.live}
                      for arena in (case.residues, case.indices))
        source_bytes = bytes(case.program.tape.cells), bytes(case.fields.tape.cells)
        peaks = []
        for reverse in (False, True):
            request = SimpleNamespace(kind="child", child_kind="pair", field=0, reverse=reverse,
                                      coordinate=case.coordinate, negative_inverse=True)
            with VERIFY.Census(self.modules, case.residues, case.indices, 20491, 13) as census:
                result = page.evaluate(request)
                self.assertEqual(result.inspect(), 1)
                case.residues.free(result)
            VERIFY.preserved(case, saved, source_bytes)
            peaks.append(census.peak)
        self.assertEqual(peaks, [[36882, 26], [36882, 26]])
        VERIFY.cleanup(case, page)

    def test_complete_stored_form_counts(self):
        self.assertEqual(VERIFY.form_case(self.modules, 3, 2),
                         {"dimension": 3, "rank": 2, "good": 17, "fallback": 36})

    def test_typed_receipt_rejects_understatement_and_boolean(self):
        expected = {"peak": [20490, 10]}
        for actual in ({"peak": [20489, 10]}, {"peak": [20490, True]}):
            with self.assertRaisesRegex(ValueError, "fixed typed receipt"):
                VERIFY.check_receipt(actual, expected)

    def test_invalid_entry_scan_leaves_methods_unchanged(self):
        words = self.modules.words
        residues, indices = words.Arena(3, 8), words.Arena(8, 8)
        word = residues.zero()
        word.cells[-1] = words.BLANK
        original_zero, original_inverse = words.Arena.zero, words.Ring.inverse
        with self.assertRaisesRegex(ValueError, "literal numerical cell census"), VERIFY.Census(
                self.modules, residues, indices, 10, 10):
            self.fail("invalid entry must reject")
        self.assertIs(words.Arena.zero, original_zero)
        self.assertIs(words.Ring.inverse, original_inverse)
        word.cells[-1] = words.RIGHT
        residues.free(word)


class Exports(unittest.TestCase):
    def run_export(self, directory, load=False):
        if load:
            script = ("import importlib.util,sys; "
                      "s=importlib.util.spec_from_file_location('v',sys.argv[1]); "
                      "v=importlib.util.module_from_spec(s); s.loader.exec_module(v); "
                      "v.load_sources(); print(v.HEAD)")
            argv = [sys.executable, "-I", "-O", "-B", "-Werror", "-c", script,
                    str(directory / "verify.py")]
        else:
            argv = [sys.executable, "-I", "-O", "-B", "-Werror",
                    str(directory / "verify.py"), "--sources-only"]
        return subprocess.run(argv, capture_output=True, text=True, timeout=30)

    def export(self, directory):
        target = Path(directory) / "package"
        shutil.copytree(PACKAGE, target, ignore=shutil.ignore_patterns("__pycache__"))
        return target

    def test_git_free_export_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self.export(directory)
            before = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
            result = self.run_export(target, load=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), VERIFY.HEAD)
            after = {p.relative_to(target): p.read_bytes() for p in target.rglob("*") if p.is_file()}
            self.assertEqual(before, after)

    def test_source_corruption_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self.export(directory)
            with (target / "vendor/words.py").open("a") as stream:
                stream.write("\nraise RuntimeError('must never execute')\n")
            result = self.run_export(target, load=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)
            self.assertNotIn("RuntimeError: must never execute", result.stderr)

    def test_changed_head_path_blob_and_inventory_reject(self):
        changes = (("head", "0" * 40), ("source_path", "elsewhere/words.py"),
                   ("path", "../words.py"), ("git_blob", "0" * 40), ("inventory", None))
        for field, value in changes:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                target = self.export(directory)
                path = target / "SNAPSHOT.json"
                manifest = json.loads(path.read_text())
                if field == "head":
                    manifest[field] = value
                elif field == "inventory":
                    manifest["files"].pop()
                else:
                    manifest["files"][0][field] = value
                path.write_text(json.dumps(manifest))
                result = self.run_export(target)
                self.assertNotEqual(result.returncode, 0)

    def test_stale_bytecode_cannot_replace_authenticated_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = self.export(directory)
            source = target / "vendor/words.py"
            poison = Path(directory) / "poison.py"
            poison.write_text("raise RuntimeError('stale bytecode executed')\n")
            cache = source.parent / "__pycache__" / ("words." + sys.implementation.cache_tag + ".pyc")
            cache.parent.mkdir()
            py_compile.compile(str(poison), cfile=str(cache), doraise=True)
            raw = bytearray(cache.read_bytes())
            raw[8:16] = struct.pack("<II", int(source.stat().st_mtime), source.stat().st_size)
            cache.write_bytes(raw)
            result = self.run_export(target, load=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
