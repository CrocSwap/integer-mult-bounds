"""Physical-memory budgets must also apply on native Windows."""
import contextlib
import ctypes
import os
from pathlib import Path
import struct
import sys
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import run_parallel
import verify_parallel


class PhysicalMemoryChecks(unittest.TestCase):
    @contextlib.contextmanager
    def windows_memory(self, total, available=1 << 30, succeeds=True):
        def query(buffer):
            # Independent SDK layout: two DWORDs followed by seven DWORDLONGs.
            self.assertEqual(ctypes.cast(buffer, ctypes.POINTER(ctypes.c_uint32))[0], 64)
            payload = struct.pack('<II7Q', 64, 75, total, available,
                                  2 * total, available, 1 << 47, 1 << 46, 0)
            ctypes.memmove(buffer, payload, len(payload))
            return 7 if succeeds else 0

        kernel = Mock()
        kernel.GlobalMemoryStatusEx.side_effect = query
        with patch.object(sys, 'platform', 'win32'), patch.object(
                ctypes, 'WinDLL', return_value=kernel, create=True), patch.object(
                os, 'sysconf', side_effect=AttributeError('not on Windows'), create=True):
            yield kernel.GlobalMemoryStatusEx

    def test_windows_memory_preserves_high_bits_and_uses_total_physical_bytes(self):
        with self.windows_memory((33 << 30) + (1 << 29)) as query:
            self.assertEqual(run_parallel.memory_gib(), 33.5)
            query.assert_called_once()

    def test_windows_worker_budget_is_memory_limited(self):
        with self.windows_memory(8 << 30), patch.dict(os.environ, {}, clear=True), patch.object(
                run_parallel, 'available_cpus', return_value=32):
            self.assertEqual(run_parallel.jobs(), 2)

    def test_windows_small_memory_also_limits_isolated_groups(self):
        with self.windows_memory(3 << 30), patch.dict(os.environ, {}, clear=True), patch.object(
                verify_parallel, 'available_cpus', return_value=32):
            self.assertEqual(verify_parallel.default_jobs(), 1)

    def test_memory_budget_keeps_one_worker_and_respects_cpu_limit(self):
        for total, cpus, expected in ((1 << 29, 32, 1), (64 << 30, 2, 2)):
            with self.subTest(total=total, cpus=cpus), self.windows_memory(total), patch.dict(
                    os.environ, {}, clear=True), patch.object(
                    run_parallel, 'available_cpus', return_value=cpus):
                self.assertEqual(run_parallel.jobs(), expected)

    def test_windows_failed_or_zero_memory_query_is_unknown(self):
        for total, succeeds in ((16 << 30, False), (0, True)):
            with self.subTest(total=total, succeeds=succeeds), self.windows_memory(
                    total, succeeds=succeeds):
                self.assertIsNone(run_parallel.memory_gib())

    def test_unavailable_windows_api_is_unknown(self):
        for error in (OSError('API unavailable'), AttributeError('API absent')):
            with self.subTest(error=type(error).__name__), patch.object(
                    sys, 'platform', 'win32'), patch.object(
                    ctypes, 'WinDLL', side_effect=error, create=True), patch.object(
                    os, 'sysconf', side_effect=AttributeError, create=True):
                self.assertIsNone(run_parallel.memory_gib())

    def test_unknown_memory_retains_cpu_fallback(self):
        with self.windows_memory(16 << 30, succeeds=False), patch.dict(
                os.environ, {}, clear=True), patch.object(
                run_parallel, 'available_cpus', return_value=4):
            self.assertEqual(run_parallel.jobs(), 4)

    def test_explicit_jobs_does_not_query_memory(self):
        with patch.dict(os.environ, {'JOBS': '7'}), patch.object(
                run_parallel, 'memory_gib', side_effect=AssertionError('must not query')), patch.object(
                verify_parallel, 'memory_gib', side_effect=AssertionError('must not query')):
            self.assertEqual(run_parallel.jobs(), 7)
            self.assertEqual(verify_parallel.default_jobs(), 7)

    def test_posix_memory_uses_pages_without_loading_windows_api(self):
        with patch.object(sys, 'platform', 'linux'), patch.object(
                os, 'sysconf', side_effect={'SC_PAGE_SIZE': 4096,
                                           'SC_PHYS_PAGES': 3 * 2**20}.__getitem__, create=True), patch.object(
                ctypes, 'WinDLL', side_effect=AssertionError('Windows API on POSIX'), create=True):
            self.assertEqual(run_parallel.memory_gib(), 12)

    def test_posix_unavailable_memory_is_unknown(self):
        for error in (AttributeError(), OSError(), ValueError()):
            with self.subTest(error=type(error).__name__), patch.object(
                    sys, 'platform', 'linux'), patch.object(
                    os, 'sysconf', side_effect=error, create=True):
                self.assertIsNone(run_parallel.memory_gib())

    @unittest.skipUnless(sys.platform == 'win32', 'native Windows API smoke test')
    def test_native_windows_reports_physical_memory(self):
        memory = run_parallel.memory_gib()
        self.assertIsNotNone(memory)
        self.assertGreater(memory, 0)


if __name__ == '__main__':
    unittest.main()
