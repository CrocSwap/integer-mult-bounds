#!/usr/bin/env python3
"""Independent fixtures and failure boundaries for the finite ledger audit.

Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import importlib.util
import gzip
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('projector_ledger', HERE/'verify.py')
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class ProjectorFixtures(unittest.TestCase):
    def test_oblique_line_exact_matrix(self):
        # The line (1,2) has P=[[1,2],[2,4]]/5, not a coordinate mask.
        line = (1, 2, 0, 0, 0, 0, 0, 0)
        matrix = [[0]*8 for _ in range(8)]
        matrix[0][:2] = [1, 2]
        matrix[1][:2] = [2, 4]
        expected = (tuple(map(tuple, matrix)), 5, 1)
        self.assertEqual(audit.projector((line,)), expected)
        self.assertTrue(audit.fixes(expected, line))
        self.assertFalse(audit.fixes(expected, (1, 0, 0, 0, 0, 0, 0, 0)))

    def test_basis_change_does_not_change_subspace(self):
        rows = ((1, 2, 0, 0, 0, 0, 0, 0), (0, 1, 3, 0, 0, 0, 0, 0))
        changed = (tuple(a+7*b for a, b in zip(*rows)), tuple(-3*x for x in rows[1]))
        self.assertEqual(audit.projector(rows), audit.projector(changed))

    def test_same_dimension_is_not_nesting(self):
        x = audit.projector(((1, 0, 0, 0, 0, 0, 0, 0),))
        y = audit.projector(((0, 1, 0, 0, 0, 0, 0, 0),))
        self.assertEqual(x[2], y[2])
        with self.assertRaisesRegex(audit.Reject, 'non-nested'):
            audit.increase(x, y)

    def test_complement_reverses_nesting(self):
        x = audit.projector(((1, 2, 0, 0, 0, 0, 0, 0),))
        xy = audit.projector(((1, 0, 0, 0, 0, 0, 0, 0), (0, 1, 0, 0, 0, 0, 0, 0)))
        self.assertEqual(audit.increase(x, xy), 1)
        self.assertEqual(audit.increase(audit.complement(xy), audit.complement(x)), 1)
        with self.assertRaisesRegex(audit.Reject, 'non-nested'):
            audit.increase(xy, x)

    def test_nonprojector_rejected_despite_integer_trace(self):
        matrix = [[0]*8 for _ in range(8)]
        matrix[0][1] = matrix[1][0] = 1
        with self.assertRaisesRegex(audit.Reject, 'idempotence'):
            audit.validate_projector((tuple(map(tuple, matrix)), 1, 0))

    def test_zero_full_and_redundant_spanning_rows(self):
        zero = audit.projector(())
        rows = tuple(tuple(int(i == j) for i in range(8)) for j in range(8))
        full = audit.projector(rows + rows)
        self.assertEqual(audit.increase(zero, full), 8)
        self.assertEqual(audit.complement(full), zero)


class SourceCompatibility(unittest.TestCase):
    def test_both_literal_exports_and_frame_operators(self):
        # Secondary cross-check only: the main verifier never invokes/imports
        # this predecessor exporter and derives its own charges independently.
        raw = audit.inputs()
        exporter = audit.ROOT/'research/e8-bit-carrier-skeleton/code/bit/export_records.py'
        for relative in ('data/bitE8mut-p111.json.gz', 'tune/bitE8mut-p111-tuned.json.gz'):
            with self.subTest(word=relative), tempfile.TemporaryDirectory(prefix='bit589-export-') as tmp:
                path = audit.ROOT/(audit.BIT+relative)
                word = json.loads(gzip.decompress(raw[audit.BIT+relative]))
                spaces, zero = audit.geometry(word)
                tape = audit.records(word, spaces, zero)
                subprocess.run([sys.executable, '-I', '-B', str(exporter), str(path), tmp],
                               check=True, timeout=60, capture_output=True, text=True)
                expected = b''.join(struct.pack('<6i', *event) for event in tape)
                self.assertEqual((Path(tmp)/'249-records.bin').read_bytes(), expected)
                frames = json.loads((Path(tmp)/'frames.json').read_text())['frames']
                self.assertEqual(len(frames), len(spaces))
                for index, projection in enumerate(spaces):
                    frame = frames[str(index)]
                    self.assertEqual(audit.projector(tuple(map(tuple, frame['B']))), projection)
                    self.assertEqual(audit.projector(tuple(map(tuple, frame['A']))),
                                     audit.complement(projection))


if __name__ == '__main__':
    unittest.main()
