#!/usr/bin/env python3
"""Independent AI reviewer controls for the explicit packet backing contract.

Uses the primary source instrumentation for defect injection; these controls
are not an independently implemented all-parameter proof or a heap census.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("packet_envelope_under_test", ROOT / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verify)


class EnvelopeControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rt = verify.runtime.load_runtime()

    def test_actual_positive_contract(self):
        # Both sides of the F/Q comparison, with scratch and hidden source backing.
        for fibre, prefix in ((1, 4), (3, 3), (7, 2)):
            result = verify.fixture(self.rt, 2, fibre, prefix, 5, 2, 11)
            self.assertEqual(result["caller_peak"], result["bill"]["caller"])
            self.assertEqual(result["composed_peak"], result["bill"]["composed"])

    def test_prefix_only_bound_rejected_by_actual_copy(self):
        original = verify.envelope

        def prefix_only(*args, **kwargs):
            bill = original(*args, **kwargs)
            bill["caller"] = bill["prefix"]
            return bill

        with mock.patch.object(verify, "envelope", prefix_only):
            with self.assertRaisesRegex(ValueError, "caller envelope"):
                verify.fixture(self.rt, 2, 7, 2, 0, 2)

    def test_copy_only_bound_rejected_by_actual_prefix_read(self):
        original = verify.envelope

        def copy_only(*args, **kwargs):
            bill = original(*args, **kwargs)
            bill["caller"] = bill["copy"]
            return bill

        with mock.patch.object(verify, "envelope", copy_only):
            with self.assertRaisesRegex(ValueError, "caller envelope"):
                verify.fixture(self.rt, 2, 1, 7, 0, 2)

    def test_omitted_preflight_rejected(self):
        original = verify.envelope

        def omit_preflight(N, F, K, D, Q, A=None):
            bill = original(N, F, K, D, Q, A)
            bill["caller"] -= Q
            return bill

        with mock.patch.object(verify, "envelope", omit_preflight):
            with self.assertRaisesRegex(ValueError, "caller envelope"):
                verify.fixture(self.rt, 2, 3, 3, 0, 2)

    def test_unpriced_private_scratch_rejected(self):
        original = verify.envelope

        def ignore_scratch(N, F, K, D, Q, A=None):
            bill = original(N, F, K, D, Q, A)
            if A is not None:
                bill["composed"] = bill["caller"]
            return bill

        with mock.patch.object(verify, "envelope", ignore_scratch):
            with self.assertRaisesRegex(ValueError, "composed action envelope"):
                verify.fixture(self.rt, 2, 3, 3, 0, 2, 23)

    def test_domain_and_boolean_rejection(self):
        good = [2, 3, 7, 5, 3]
        for position, invalid in ((0, 0), (1, 0), (2, 6), (3, 4), (4, 1)):
            row = good.copy()
            row[position] = invalid
            with self.assertRaises(ValueError):
                verify.envelope(*row)
        for position in range(5):
            row = good.copy()
            row[position] = True
            with self.assertRaisesRegex(ValueError, "integer domain"):
                verify.envelope(*row)
        for allowance in (True, 3, -1):
            with self.assertRaisesRegex(ValueError, "action includes"):
                verify.envelope(*good, allowance)

    def test_typed_receipt_rejection(self):
        check = verify.runtime.check_receipt
        check({"count": 1, "complete": True}, {"complete": True, "count": 1})
        for changed in ({"count": True, "complete": True},
                        {"count": 1.0, "complete": True},
                        {"count": 1, "complete": 1}):
            with self.assertRaisesRegex(ValueError, "typed deterministic"):
                check({"count": 1, "complete": True}, changed)

    def test_authenticated_sources_and_preload_rejection(self):
        self.assertGreater(len(verify.runtime.authenticate()), 10)
        with self.assertRaisesRegex(ValueError, "source module already loaded"):
            verify.runtime.load_runtime()

    def test_manifest_and_source_corruption(self):
        with tempfile.TemporaryDirectory(prefix="packet-envelope-defect-") as temporary:
            copy = Path(temporary) / "package"
            shutil.copytree(ROOT, copy)
            manifest_path = copy / "SNAPSHOTS.json"
            manifest_path.chmod(manifest_path.stat().st_mode | 0o200)
            original = manifest_path.read_bytes()
            manifest_path.write_bytes(original + b" ")
            with self.assertRaisesRegex(ValueError, "manifest digest"):
                verify.runtime.authenticate(copy)
            manifest_path.write_bytes(original)
            manifest = json.loads(original)
            source = copy / next(item["path"] for item in manifest["files"]
                                 if item["path"].endswith("packet_engine.py"))
            source.chmod(source.stat().st_mode | 0o200)
            source.write_bytes(source.read_bytes() + b"\n# injected corruption\n")
            with self.assertRaisesRegex(ValueError, "source digest"):
                verify.runtime.authenticate(copy)

    def test_endpoint_only_local_restoration_is_insufficient(self):
        # This deliberately violates the interior backing-length contract,
        # restores the borrowed local before return, and still completes the
        # literal engine. It is an interface counterexample, not a native bug.
        import packet_engine
        rt = self.rt
        Tape = rt.records.Tape
        source, directory, first = Tape(), Tape(), Tape()
        source.cells.extend(b"\x00\x01")
        directory.cells.extend(bytes([rt.records.RECORD_END]) * 2)
        first.cells.extend(bytes([rt.words.BLANK]))
        n, f, q = 2, 1, 2
        bound = verify.envelope(n, f, len(source.cells), len(directory.cells), q, f + 1)
        observed = []
        prefix_count, field_count = rt.counts.Count.literal(n), rt.counts.Count.literal(1)

        def enlarged_local(local, event, layout, coefficient, factory):
            out = factory()
            out.append(local.cells[1])
            out.rewind()
            old_length = len(local.cells)
            local.cells.extend(b"\x00" * 100)
            run = sys._getframe(1)
            owners = [source, directory, first, out]
            owners += [run.f_locals[name] for name in
                       ("current", "output", "local", "changed", "fields")
                       if isinstance(run.f_locals.get(name), Tape)]
            observed.append(verify.unique_size(owners))
            del local.cells[old_length:]
            self.assertEqual(len(local.cells), f + 1)
            return out

        layout = SimpleNamespace(fibre=lambda: rt.counts.Count.literal(f))
        events = (SimpleNamespace(kind="sign") for _ in range(2))
        try:
            with mock.patch.object(packet_engine, "action", enlarged_local):
                output = packet_engine.run(source, events, layout, directory,
                                           prefix_count, field_count, lambda _: None)
            self.assertEqual(bytes(output.cells[1:]), b"\x00\x01")
            self.assertEqual(bytes(source.cells[1:]), b"\x00\x01")
            self.assertGreater(min(observed), bound["composed"])
        finally:
            prefix_count.close()
            field_count.close()


if __name__ == "__main__":
    unittest.main()
