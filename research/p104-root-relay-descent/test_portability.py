"""Regenerated-output portability controls; immutable inputs stay exact.

Maintainer repair by Douglas Colkitt with OpenAI Codex assistance.
Construction and verifier: DreamingOfClouds; retained predecessors in README.
Apache-2.0.
"""
from copy import deepcopy
import gzip
import io
import json
from pathlib import Path
import sys
import unittest
import zlib

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from construct import matches_shipped, payload
from sources import authenticate


class WordPortabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shipped = (HERE / 'WORD.json.gz').read_bytes()
        cls.word = json.loads(gzip.decompress(cls.shipped))

    def test_original_word(self):
        self.assertTrue(matches_shipped(self.word, self.shipped))

    def test_os_header_variants(self):
        # Byte 9 is gzip's OS field. Neither the payload nor CRC changes.
        for code in (0, 3, 19, 255):
            changed = bytearray(self.shipped)
            changed[9] = code
            with self.subTest(os_code=code):
                self.assertTrue(matches_shipped(self.word, bytes(changed)))

    def test_compression_timestamp_and_filename(self):
        for level in (1, 6, 9):
            with self.subTest(level=level):
                buffer = io.BytesIO()
                with gzip.GzipFile(filename='different-name.json', mode='wb',
                                   compresslevel=level, mtime=1700000000,
                                   fileobj=buffer) as stream:
                    stream.write(payload(self.word))
                self.assertNotEqual(buffer.getvalue(), self.shipped)
                self.assertTrue(matches_shipped(self.word, buffer.getvalue()))

    def test_changed_event_and_unknown_field_rejected(self):
        changed = deepcopy(self.word)
        changed['program'].pop()
        self.assertFalse(matches_shipped(changed, self.shipped))
        changed = deepcopy(self.word)
        changed['unexpected_proof_field'] = 1
        self.assertFalse(matches_shipped(changed, self.shipped))

    def test_boolean_is_not_an_integer(self):
        changed = deepcopy(self.word)
        move = next(event for event in changed['program'] if event[0] == 'MOVE')
        self.assertIs(type(move[4]), bool)
        move[4] = int(move[4])
        # Python object equality alone would silently accept this mutation.
        self.assertEqual(changed, self.word)
        self.assertFalse(matches_shipped(changed, self.shipped))

    def test_extra_payload_and_corrupt_container_rejected(self):
        self.assertFalse(matches_shipped(self.word, gzip.compress(payload(self.word) + b' ')))
        self.assertFalse(matches_shipped(self.word, self.shipped + gzip.compress(b'not a word')))
        for bad in (self.shipped[:20], self.shipped[:-8] + b'\0' * 8):
            with self.subTest(size=len(bad)):
                with self.assertRaises((gzip.BadGzipFile, EOFError, zlib.error)):
                    matches_shipped(self.word, bad)

    def test_immutable_source_still_uses_exact_bytes(self):
        pin = json.loads((HERE / 'SOURCES.json').read_bytes())['base_word']
        raw = (HERE / pin['local_path']).read_bytes()
        authenticate(raw, pin)
        changed = bytearray(raw)
        changed[9] = 3 if raw[9] != 3 else 19
        self.assertEqual(gzip.decompress(raw), gzip.decompress(changed))
        with self.assertRaises(ValueError):
            authenticate(bytes(changed), pin)


if __name__ == '__main__':
    unittest.main(verbosity=2)
