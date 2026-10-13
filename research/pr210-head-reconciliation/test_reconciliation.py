"""Failure modes for the independent stream and source reconciliation."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from stream_audit import ROW, equivalent, trace


def records(*rows):
    return b"".join(ROW.pack(*row) for row in rows)


class StreamControls(unittest.TestCase):
    # Even frame identifiers and COPY rank are address data, not payload scalars.
    old_rows = [(0, 0, 10, 12, 8, 0), (1, 0, 1, -2, 12, 0),
                (0, 0, 12, 14, 12, 0), (1, 0, 1, 3, 14, 0),
                (2, 2, 20107, 14, 0, 22), (1, 3, 20107, 1, 0, 0),
                (3, 2, 20107, 14, 0, 0)]
    new_rows = [(0, 0, 10, 14, 20, 0), (1, 0, 1, 3, 14, 0),
                (2, 2, 20107, 14, 0, 22), (1, 3, 20107, 1, 0, 0),
                (3, 2, 20107, 14, 0, 0)]

    def compare(self, rows):
        equivalent(trace(records(*self.old_rows), discard_even=True), trace(records(*rows)))

    def test_identity_elision_and_fusion(self):
        self.compare(self.new_rows)

    def test_different_stream_moves_commute(self):
        a = [(0, 0, 10, 12, 8, 0), (0, 1, 20, 22, 4, 0), (1, 0, 1, 1, 12, 0)]
        b = [a[1], a[0], a[2]]
        equivalent(trace(records(*a)), trace(records(*b)))

    def test_wrong_fused_rank(self):
        rows = self.new_rows.copy(); rows[0] = (0, 0, 10, 14, 19, 0)
        with self.assertRaises(ValueError): self.compare(rows)

    def test_odd_gate_omitted(self):
        with self.assertRaises(ValueError): self.compare(self.new_rows[:1] + self.new_rows[2:])

    def test_signed_odd_coefficient_changed(self):
        rows = self.new_rows.copy(); rows[1] = (1, 0, 1, 1, 14, 0)
        with self.assertRaises(ValueError): self.compare(rows)

    def test_address_frame_not_reduced_mod_two(self):
        rows = self.new_rows.copy(); rows[0] = (0, 0, 0, 0, 20, 0)
        with self.assertRaises(ValueError): self.compare(rows)

    def test_even_copy_rank_not_elided(self):
        with self.assertRaises(ValueError): self.compare(self.new_rows[:2] + self.new_rows[3:])

    def test_copy_source_mutation(self):
        rows = self.new_rows.copy(); rows[2] = (2, 1, 20107, 14, 0, 22)
        with self.assertRaises(ValueError): self.compare(rows)

    def test_move_cannot_cross_retained_use(self):
        rows = self.new_rows.copy(); rows[0], rows[1] = rows[1], rows[0]
        with self.assertRaises(ValueError): self.compare(rows)

    def test_disconnected_chain(self):
        rows = self.old_rows.copy(); rows[2] = (0, 0, 13, 14, 12, 0)
        with self.assertRaises(ValueError): trace(records(*rows), discard_even=True)

    def test_truncated_record(self):
        with self.assertRaises(ValueError): trace(records(*self.new_rows)[:-1])

    def test_scalar_domain_boundary(self):
        # The elided gate is an identity over F2, but not over an odd field.
        self.assertEqual((0 + 2 * 1) % 2, 0)
        self.assertNotEqual((0 + 2 * 1) % 3, 0)


class SourceControls(unittest.TestCase):
    def test_missing_modified_and_extra_inputs(self):
        from verify import manifest
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            source = root / "input.txt"
            source.write_bytes(b"pinned source\n")
            receipt = root / "MANIFEST.json"
            receipt.write_text(json.dumps({"files": {"input.txt": hashlib.sha256(source.read_bytes()).hexdigest()}}))
            digest = hashlib.sha256(receipt.read_bytes()).hexdigest()
            self.assertEqual(manifest(root, digest), 1)
            source.write_bytes(b"changed source\n")
            with self.assertRaises(ValueError): manifest(root, digest)
            source.unlink()
            with self.assertRaises(ValueError): manifest(root, digest)
            source.write_bytes(b"pinned source\n")
            (root / "unpinned.txt").write_text("extra")
            with self.assertRaises(ValueError): manifest(root, digest)

    def test_changed_manifest(self):
        from verify import manifest
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "MANIFEST.json").write_text('{"files": {}}')
            with self.assertRaises(ValueError): manifest(root, "0" * 64)


if __name__ == "__main__":
    unittest.main()
