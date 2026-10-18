"""Exact byte, real unittest and end-to-end benchmark failure controls.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from contextlib import redirect_stdout
import copy
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import adapter
from comparison import POLICY, comparison_key, elapsed_span
from verify import collision_evidence, trailer


class ByteComparisonTest(unittest.TestCase):
    def test_exact_predecessor_collisions(self):
        self.assertEqual(set(collision_evidence()),
                         {"diagnostic_elapsed_shape", "replacement_decoding"})

    def test_final_elapsed_only_positive_formats(self):
        for nl in (b"\n", b"\r\n"):
            for count, noun in ((b"0", b"tests"), (b"1", b"test"), (b"23", b"tests")):
                for status in (b"OK", b"OK (skipped=2)", b"OK (expected failures=1)",
                               b"FAILED (failures=1, errors=2, unexpected successes=1)"):
                    a = b"opaque diagnostic \xff" + nl + trailer(b"0.001", count, noun, status, nl)
                    b = b"opaque diagnostic \xff" + nl + trailer(b"1234.567", count, noun, status, nl)
                    with self.subTest(nl=nl, count=count, status=status):
                        self.assertIsNotNone(elapsed_span(a))
                        self.assertEqual(comparison_key(a), comparison_key(b))

    def test_each_nontiming_byte_is_retained(self):
        data = b"\x00\xff arbitrary marker summary\x00 in 1.000s\n" + trailer()
        start, end = elapsed_span(data)
        key = comparison_key(data)
        for index in range(len(data)):
            if start <= index < end:
                continue
            changed = data[:index] + bytes([data[index] ^ 1]) + data[index+1:]
            with self.subTest(index=index):
                self.assertNotEqual(key, comparison_key(changed))

    def test_all_256_diagnostic_byte_values_stay_distinct(self):
        keys = {comparison_key(bytes([value]) + b"\n" + trailer()) for value in range(256)}
        self.assertEqual(len(keys), 256)

    def test_earlier_fake_summary_is_not_erased(self):
        a = trailer(b"1.000") + b"more diagnostics\n" + trailer(b"3.000")
        b = trailer(b"2.000") + b"more diagnostics\n" + trailer(b"4.000")
        self.assertNotEqual(comparison_key(a), comparison_key(b))

    def test_count_status_and_line_endings_stay_distinct(self):
        baseline = comparison_key(trailer())
        for changed in (trailer(count=b"2", noun=b"tests"),
                        trailer(status=b"FAILED (failures=1)"),
                        trailer(status=b"OK (skipped=1)"), trailer(nl=b"\r\n")):
            self.assertNotEqual(baseline, comparison_key(changed))

    def test_unrecognized_trailers_compare_raw(self):
        for data in (b"", b"diagnostic in 1.000s\n", trailer() + b"trailing bytes",
                     trailer(count=b"1", noun=b"tests"), trailer(count=b"2", noun=b"test"),
                     trailer(elapsed=b"0.01"), trailer(elapsed=b"0.0000"),
                     trailer().replace(b"OK\n", b"CUSTOM\n"),
                     trailer().replace(b"-" * 70, b"-" * 69),
                     trailer().replace(b"Ran 1", b"Ran 01")):
            with self.subTest(data=data):
                self.assertIsNone(elapsed_span(data))
                self.assertEqual(comparison_key(data), b"raw\0" + data)

    def test_normalized_key_cannot_collide_with_literal_marker(self):
        data = trailer()
        key = comparison_key(data)
        self.assertIsNone(elapsed_span(key))
        self.assertNotEqual(key, comparison_key(key))
        literal = trailer(elapsed=b"<elapsed>")
        self.assertIsNone(elapsed_span(literal))
        self.assertNotEqual(key, comparison_key(literal))

    def test_summary_requires_start_of_line(self):
        data = b"not a line boundary " + trailer()
        self.assertIsNone(elapsed_span(data))
        self.assertEqual(comparison_key(data), b"raw\0" + data)

    def test_strict_bytes_api(self):
        for value in ("text", bytearray(b"x"), None):
            with self.assertRaises(TypeError):
                comparison_key(value)


class RealCaptureTest(unittest.TestCase):
    def capture_pair(self, body, left, right):
        with tempfile.TemporaryDirectory(prefix="unittest-byte-capture-") as temp:
            root = Path(temp)
            (root / "test_capture.py").write_text(
                "import os, unittest\nclass T(unittest.TestCase):\n    def test_capture(self):\n        " + body + "\n",
                encoding="utf-8")
            captures = []
            for value in (left, right):
                env = dict(os.environ, CAPTURE_VALUE=value)
                captures.append(subprocess.run(
                    [sys.executable, "-I", "-B", "-m", "unittest", "discover", "-s", str(root), "-v"],
                    capture_output=True, env=env, timeout=30))
            return captures

    def assert_real_collision(self, left, right, code):
        legacy = adapter.load_benchmark(strict=False)
        self.assertEqual((left.returncode, right.returncode), (code, code))
        self.assertEqual(left.stdout, right.stdout)
        self.assertNotEqual(left.stderr, right.stderr)
        self.assertIsNotNone(elapsed_span(left.stderr))
        self.assertIsNotNone(elapsed_span(right.stderr))
        self.assertEqual(legacy.normalize(left.stderr), legacy.normalize(right.stderr))
        self.assertNotEqual(comparison_key(left.stderr), comparison_key(right.stderr))

    def test_real_failure_diagnostics_with_elapsed_shape(self):
        left, right = self.capture_pair('self.fail(os.environ["CAPTURE_VALUE"])',
                                        "invoice in 1.000s", "invoice in 2.000s")
        self.assert_real_collision(left, right, 1)

    def test_real_passing_stderr_with_invalid_encoding(self):
        left, right = self.capture_pair('os.write(2, bytes.fromhex(os.environ["CAPTURE_VALUE"]) + b"\\n")',
                                        "ff", "fe")
        self.assert_real_collision(left, right, 0)

    def test_real_passing_timing_difference_is_accepted(self):
        left, right = self.capture_pair('__import__("time").sleep(float(os.environ["CAPTURE_VALUE"]))',
                                        "0.001", "0.020")
        self.assertEqual((left.returncode, right.returncode), (0, 0))
        self.assertEqual(left.stdout, right.stdout)
        self.assertIsNotNone(elapsed_span(left.stderr))
        self.assertEqual(comparison_key(left.stderr), comparison_key(right.stderr))


class BenchmarkIntegrationTest(unittest.TestCase):
    def run_fixture(self, strict, transform=None):
        benchmark = adapter.load_benchmark(strict=strict)
        with tempfile.TemporaryDirectory(prefix="unittest-benchmark-control-") as temp:
            root = Path(temp)
            (root / "scripts").mkdir()
            (root / "tests").mkdir()
            shutil.copyfile(adapter.ROOT / "scripts/run_isolated_tests.py", root / "scripts/run_isolated_tests.py")
            fixture = ('import os, unittest\nclass T(unittest.TestCase):\n'
                       '    def test_pass(self):\n'
                       '        os.write(2, b"diagnostic in 1.000s\\nbyte: \\xff\\n")\n'
                       '        print("fixture stdout")\n')
            for name in ("test_a.py", "test_b.py"):
                (root / "tests" / name).write_text(fixture, encoding="utf-8")
            # A bounded isolated fixture, not a rerun or a speed measurement of
            # the repository suite. Inject faults only after real captures.
            benchmark.ROOT = root
            runner = benchmark.load_runner()
            original_run = runner.run_modules
            if transform is not None:
                def faulty(*args, **kwargs):
                    return [transform(row) for row in original_run(*args, **kwargs)]
                runner.run_modules = faulty
            benchmark.load_runner = lambda: runner
            output = root / "fresh.json"
            argv = ["benchmark", "--workers", "2", "--output", str(output)]
            stream = io.StringIO()
            # Keep fixture children deterministic without altering production
            # adapter behavior or inheriting optimized assertion semantics.
            with patch.object(sys, "argv", argv), redirect_stdout(stream), patch.dict(os.environ):
                os.environ.pop("PYTHONOPTIMIZE", None)
                os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
                try:
                    benchmark.main()
                except SystemExit as error:
                    code = error.code
                else:
                    code = 0
            return code, json.loads(output.read_bytes()), stream.getvalue()

    @staticmethod
    def edit_stderr(old, new):
        return lambda row: (row[0], row[1], row[2], row[3].replace(old, new))

    def test_unchanged_fixture_and_policy_are_accepted(self):
        code, result, _ = self.run_fixture(True)
        self.assertEqual(code, 0)
        self.assertEqual(result["normalized_equal_modules"], 2)
        self.assertEqual(result["receipt_mismatches"], [])
        self.assertEqual(result["sequential_failing"], result["concurrent_failing"])
        self.assertTrue(all(r["stderr_comparison_policy"] == POLICY
                            for r in result["per_module_concurrent"].values()))

    def test_predecessor_accepts_changed_diagnostic_but_adapter_rejects(self):
        change = self.edit_stderr(b"in 1.000s", b"in 2.000s")
        old_code, old, _ = self.run_fixture(False, change)
        code, result, _ = self.run_fixture(True, change)
        self.assertEqual(old_code, 0)
        self.assertEqual(old["normalized_equal_modules"], 2)
        self.assertNotEqual(code, 0)
        self.assertEqual(result["receipt_mismatches"], ["test_a.py", "test_b.py"])
        self.assertEqual(result["scheduling_driven_mismatches"], result["receipt_mismatches"])
        self.assertEqual(result["code_mismatches"], [])

    def test_predecessor_accepts_changed_invalid_byte_but_adapter_rejects(self):
        change = self.edit_stderr(b"\xff", b"\xfe")
        old_code, _, _ = self.run_fixture(False, change)
        code, result, _ = self.run_fixture(True, change)
        self.assertEqual(old_code, 0)
        self.assertNotEqual(code, 0)
        self.assertEqual(result["normalized_equal_modules"], 0)

    def test_stdout_exit_status_count_and_result_controls(self):
        changes = {
            "stdout": lambda r: (r[0], r[1], r[2] + b"changed", r[3]),
            "exit_code": lambda r: (r[0], 1, r[2], r[3]),
            "test_count": self.edit_stderr(b"Ran 1 test", b"Ran 2 tests"),
            "status": self.edit_stderr(b"OK", b"FAILED (failures=1)"),
        }
        for name, change in changes.items():
            with self.subTest(control=name):
                code, result, _ = self.run_fixture(True, change)
                self.assertNotEqual(code, 0)
                field = "code_mismatches" if name == "exit_code" else "receipt_mismatches"
                self.assertEqual(result[field], ["test_a.py", "test_b.py"])

    def test_timing_only_fault_is_accepted(self):
        def change(row):
            start, end = elapsed_span(row[3])
            return row[:3] + (row[3][:start] + b"12345.678" + row[3][end:],)
        code, result, _ = self.run_fixture(True, change)
        self.assertEqual(code, 0)
        self.assertEqual(result["normalized_equal_modules"], 2)


class SourceBindingTest(unittest.TestCase):
    def test_each_changed_input_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="unittest-source-control-") as temp:
            root = Path(temp)
            for name in adapter.INPUTS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(adapter.ROOT / name, target)
            adapter.check_sources(root)
            for name in sorted(adapter.INPUTS):
                target = root / name
                original = target.read_bytes()
                target.write_bytes(original + b"\nchanged")
                with self.subTest(source=name), self.assertRaises(ValueError):
                    adapter.load_benchmark(root)
                target.write_bytes(original)

    def test_omitted_input_pin_is_rejected(self):
        manifest = json.loads((adapter.HERE / "SOURCES.json").read_bytes())
        changed = copy.deepcopy(manifest)
        changed["files"] = [r for r in changed["files"] if r["path"] != adapter.PREDECESSOR]
        with patch.object(adapter.json, "loads", return_value=changed), self.assertRaises(ValueError):
            adapter.check_sources()


if __name__ == "__main__":
    unittest.main()
