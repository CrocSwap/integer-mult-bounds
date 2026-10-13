"""Exact inventory equivalence and failures for the pinned split-ZIP reader."""
from copy import deepcopy
from hashlib import sha1, sha256
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('archive_checker', ROOT / 'scripts/verify_pr_reconciliation.py')
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def buffered_inventory(package, manifest):
    """Independent whole-buffer oracle: the original Git blob calculation."""
    data = b''.join((package / p['file']).read_bytes() for p in manifest['parts'])
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        result = {}
        for name in z.namelist():
            body = z.read(name)
            result[name] = sha1(b'blob ' + str(len(body)).encode() + b'\0' + body).hexdigest()
    return result


def pin(package, data, count):
    # Split inside the local header and payload, not merely on member boundaries.
    cuts = [0, 17, len(data) // 2, len(data)]
    parts = []
    for i, (start, end) in enumerate(zip(cuts, cuts[1:])):
        body = data[start:end]
        name = f'part{i}'
        (package / name).write_bytes(body)
        parts.append(dict(file=name, bytes=len(body), sha256=sha256(body).hexdigest()))
    return dict(parts=parts, files=count, archive_sha256=sha256(data).hexdigest())


class ArchiveInventory(unittest.TestCase):
    def test_real_pinned_archive_matches_original_all_1700_blobs(self):
        package = ROOT / 'research/coordinated-frames-and-entrance-banks'
        manifest = json.loads((package / 'BASELINE.json').read_text())
        self.assertEqual(checker.archive_inventory(package, manifest),
                         buffered_inventory(package, manifest))

    def test_chunk_boundaries_empty_binary_compression_and_duplicate_names(self):
        payload = bytes(range(256)) * 8193  # Crosses two 1 MiB chunk boundaries.
        for compression in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED,
                            zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA):
            with self.subTest(compression=compression), tempfile.TemporaryDirectory() as td:
                package = Path(td)
                stream = io.BytesIO()
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    with zipfile.ZipFile(stream, 'w', compression=compression) as z:
                        z.writestr('empty/', b'')
                        z.writestr('binary', payload)
                        z.writestr('duplicate', b'old')
                        z.writestr('duplicate', b'new')
                manifest = pin(package, stream.getvalue(), 3)
                self.assertEqual(checker.archive_inventory(package, manifest),
                                 buffered_inventory(package, manifest))

    def test_all_manifest_guards_and_changed_part(self):
        with tempfile.TemporaryDirectory() as td:
            package = Path(td)
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as z:
                z.writestr('data', b'proof-relevant data')
            manifest = pin(package, stream.getvalue(), 1)
            for field, message in [('bytes', 'Archive part size'),
                                   ('sha256', 'Archive part digest'),
                                   ('archive_sha256', 'Archive digest'),
                                   ('files', 'Archive file count')]:
                bad = deepcopy(manifest)
                if field in ('bytes', 'sha256'):
                    bad['parts'][0][field] = 0 if field == 'bytes' else '0' * 64
                else:
                    bad[field] = 0 if field == 'files' else '0' * 64
                with self.subTest(field=field), self.assertRaisesRegex(ValueError, message):
                    checker.archive_inventory(package, bad)
            (package / 'part2').write_bytes(b'x' * manifest['parts'][2]['bytes'])
            with self.assertRaisesRegex(ValueError, 'Archive part digest'):
                checker.archive_inventory(package, manifest)

    def test_inflated_member_size_is_rejected_and_spool_closed(self):
        with tempfile.TemporaryDirectory() as td:
            package = Path(td)
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w') as z:
                z.writestr('data', b'proof-relevant data')
            data = bytearray(stream.getvalue())
            offset = data.index(b'PK\x01\x02') + 24  # Central uncompressed size.
            size = int.from_bytes(data[offset:offset + 4], 'little')
            data[offset:offset + 4] = (size + 1).to_bytes(4, 'little')
            manifest = pin(package, bytes(data), 1)
            # Original whole-buffer reader tolerates this metadata inconsistency.
            self.assertEqual(len(buffered_inventory(package, manifest)), 1)
            spool = tempfile.TemporaryFile()
            self.addCleanup(spool.close)
            with patch.object(checker.tempfile, 'TemporaryFile', return_value=spool):
                with self.assertRaisesRegex(ValueError, 'Archive member size'):
                    checker.archive_inventory(package, manifest)
            self.assertTrue(spool.closed)

    def test_repinning_cannot_hide_crc_corruption_or_truncation(self):
        with tempfile.TemporaryDirectory() as td:
            package = Path(td)
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w', compression=zipfile.ZIP_STORED) as z:
                z.writestr('data', b'proof-relevant data')
            original = stream.getvalue()
            damaged = bytearray(original)
            damaged[30 + len('data')] ^= 1  # Stored payload, CRC deliberately unchanged.
            for data in (bytes(damaged), original[:-22]):
                manifest = pin(package, data, 1)
                with self.subTest(length=len(data)), self.assertRaises(zipfile.BadZipFile):
                    checker.archive_inventory(package, manifest)
                with self.assertRaises(zipfile.BadZipFile):
                    buffered_inventory(package, manifest)


if __name__ == '__main__':
    unittest.main()
