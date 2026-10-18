"""Behavioral controls for the actual installed lease accounting."""

import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runtime import PACKAGE, authenticate, load, prepare, run
from verify import exhaustion


class ScratchTrafficTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load()

    def test_literal_invoices(self):
        first = run(self.runtime, 5, 2, 1)
        second = run(self.runtime, 5, 2, 3)
        self.assertEqual(
            (first["traffic"], first["acquisitions"], first["peak"]), (1499, 13, 7)
        )
        self.assertEqual(
            (second["traffic"], second["acquisitions"], second["peak"]), (3959, 33, 8)
        )

    def test_one_role_short(self):
        for suffix in (1, 3):
            for inverse in (False, True):
                self.assertEqual(
                    exhaustion(self.runtime, suffix, inverse)["stranded"], 0
                )

    def test_borrowed_pool_source_is_counted_once(self):
        row = run(self.runtime, 9, 2, 3, occupied=3, pooled_source=True)
        self.assertEqual(
            (row["traffic"], row["acquisitions"], row["peak"]), (6615, 49, 11)
        )

    def test_endpoint_preserving_extra_marker_read_is_rejected(self):
        original = self.runtime.pool.ScratchPool.acquire

        def inflated(pool):
            lease = original(pool)
            lease.physical.read()
            return lease

        # run checks the endpoint before its independent invoice gate.
        with (
            patch.object(self.runtime.pool.ScratchPool, "acquire", inflated),
            self.assertRaisesRegex(ValueError, "physical invoice"),
        ):
            run(self.runtime, 5, 2, 3)

    def test_alias_meter_is_excluded(self):
        original = self.runtime.pool.Lease.operation

        def inflated(lease, method, *args):
            original(lease, method, *args)
            lease.meter.reads += 1000000

        with patch.object(self.runtime.pool.Lease, "operation", inflated):
            self.assertEqual(run(self.runtime, 5, 2, 1)["traffic"], 1499)

    def test_stale_cleanup_preserves_reused_role(self):
        pool = self.runtime.pool.ScratchPool(1)
        first = pool.acquire()
        first.append(0)
        first.clear()
        second = pool.acquire()
        second.append(1)
        second.rewind()
        first.clear()
        self.assertEqual(second.read(), 1)
        with self.assertRaisesRegex(ValueError, "live scratch lease"):
            first.read()
        second.clear()
        pool.empty()

    def test_installer_restores_namespace_on_failure(self):
        runtime = self.runtime
        literal = runtime.records.Tape
        original = runtime.records.Tape.__init__
        count_module = sys.modules["cardinality"]
        old_factory = count_module.Tape
        exhaustion(runtime, 3, False)
        self.assertIs(runtime.records.Tape.__init__, original)
        self.assertIs(count_module.Tape, old_factory)
        with (
            runtime.pool.ScratchPool(1).install(),
            self.assertRaisesRegex(ValueError, "physical Tape allocation"),
        ):
            literal()

    def test_source_corruption_is_rejected(self):
        original = Path.read_bytes

        def corrupted(path):
            body = original(path)
            return body + b"\n" if path.name == "scratch_pool.py" else body

        with (
            patch.object(Path, "read_bytes", corrupted),
            self.assertRaisesRegex(ValueError, "source: .*scratch_pool"),
        ):
            authenticate()

    def test_fixture_bounds(self):
        for q, b, s, spare, occupied in (
            (4, 1, 1, 8, 0),
            (3, 9, 1, 8, 0),
            (129, 8, 8, 11, 0),
            (3, 1, 1, 8, 5),
        ):
            with self.assertRaises(ValueError):
                prepare(self.runtime, q, b, s, spare, occupied, False)

    def test_cli_receipt_rejection(self):
        program = (
            "import sys;sys.path.insert(0,sys.argv[1]);import verify;"
            "sys.argv=sys.argv[:1];verify.result=lambda:{'wrong':True};verify.main()"
        )
        result = subprocess.run(
            [sys.executable, "-I", "-O", "-B", "-c", program, str(PACKAGE)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("complete typed receipt mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
