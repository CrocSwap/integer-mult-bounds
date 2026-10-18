"""Behavioral space, serialization and source-integrity controls."""
import importlib.util
import os
from pathlib import Path
import shutil
import py_compile
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("continuation_check", PACKAGE / "verify.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class ContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = check.load_source()

    def test_literal_bound_values_and_domains(self):
        self.assertEqual(check.bound(2, 20, 3), (144, 340))
        self.assertEqual(check.bound(6, 38, 128), (1703, 3670))
        for bad in ((True, 8, 8), (-1, 8, 8), (1, 0, 8), (1, 8, False), (1_000_001, 8, 8)):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                check.bound(*bad)

    def test_binary_underbudget_and_retained_extent(self):
        result = check.run_case(self.modules, "BB", 4)
        self.assertEqual((result["peak"], result["bound"]), (110, 110))
        self.assertGreater(result["peak"], result["bound"] - 1)
        self.assertGreater(result["backing"], result["peak"] + 4)
        with self.assertRaisesRegex(ValueError, "underbudget"):
            check.need(result["peak"] <= result["bound"] - 1, "underbudget")

    def test_returned_words_order_and_cleanup(self):
        words, records, _controller = self.modules
        indices, residues = words.Arena(8, 16), words.Arena(8, 16)
        stack = records.Stack(indices, residues)
        first, second = indices.literal(17), indices.literal(93)
        with check.Census(records, (stack,), direct=True) as census:
            stack.push(records.VALUE, first, second)
            tag, returned = stack.pop()
            self.assertEqual((tag, *(value.inspect() for value in returned)), (records.VALUE, 17, 93))
            self.assertEqual(census.peak, 20)
            self.assertEqual(census.live, 0)
            self.assertTrue(all(tape.head == 1 for tape in census.tapes))
        indices.free_many(first, second, *returned)
        self.assertFalse(indices.live)

    def test_malformed_pop_delimiter_and_tag(self):
        words, records, _controller = self.modules
        for symbol, message in ((records.VALUE, "top delimiter"), (records.RECORD_END, "continuation kind")):
            indices, residues = words.Arena(8, 16), words.Arena(8, 16)
            stack = records.Stack(indices, residues)
            value = residues.literal(3)
            stack.push(records.RETURN, value)
            if symbol == records.VALUE:
                stack.tape.cells[-1] = symbol
            else:
                stack.tape.cells[1] = symbol
            with self.subTest(symbol=symbol), self.assertRaisesRegex(ValueError, message):
                stack.pop()

    def test_source_corruption_rejects_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "package"
            shutil.copytree(PACKAGE, target)
            source = target / "vendor" / "records.py"
            source.write_bytes(source.read_bytes() + b"\n# changed\n")
            result = subprocess.run([sys.executable, "-I", "-B", str(target / "verify.py"),
                                     "--sources-only"], capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("source SHA256", result.stderr)

    def test_preloaded_module_rejects(self):
        snippet = ("import importlib.util,sys,types;"
                   f"s=importlib.util.spec_from_file_location('check',{str(PACKAGE / 'verify.py')!r});"
                   "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                   "sys.modules['words']=types.ModuleType('words');m.load_source()")
        result = subprocess.run([sys.executable, "-I", "-B", "-c", snippet],
                                capture_output=True, text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no preloaded source modules", result.stderr)

    def test_cached_bytecode_cannot_replace_authenticated_source(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "package"
            shutil.copytree(PACKAGE, target)
            source = target / "vendor" / "words.py"
            raw, timestamp = source.read_bytes(), source.stat().st_mtime_ns
            replacement = b"raise RuntimeError('cached bytecode executed')\n"
            source.write_bytes(replacement + b"#" * (len(raw) - len(replacement)))
            os.utime(source, ns=(timestamp, timestamp))
            py_compile.compile(str(source), doraise=True)
            source.write_bytes(raw)
            os.utime(source, ns=(timestamp, timestamp))
            snippet = ("import importlib.util;"
                       f"s=importlib.util.spec_from_file_location('check',{str(target / 'verify.py')!r});"
                       "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                       "w,r,c=m.load_source();print(w.Arena(8).bits)")
            result = subprocess.run([sys.executable, "-I", "-B", "-c", snippet],
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "8")

    def test_receipt_numeric_types_are_distinct(self):
        check.check_receipt({"depth": 1}, {"depth": 1})
        with self.assertRaisesRegex(ValueError, "typed result receipt"):
            check.check_receipt({"depth": 1}, {"depth": True})


if __name__ == "__main__":
    unittest.main()
