"""Mutation and portability controls for the immutable input loader."""
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fetch_inputs
import source_data as sd


class SourceDataTests(unittest.TestCase):
    def test_all_input_pins(self):
        self.assertEqual(sd.verify_all(), 11)

    def test_altered_input_rejected(self):
        name = 'expected/kernel-pins.json'
        with self.assertRaisesRegex(ValueError, 'Pinned input bytes changed'):
            sd.verify_bytes(name, sd.read_bytes(name) + b' ')

    def test_unpinned_path_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unpinned input'):
            sd.read_bytes('../untrusted.json')

    def test_source_location_is_explicit(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, 'CORETIME_SOURCE_DIR'):
                sd.source_root()

    def test_fetch_url_and_exact_bytes(self):
        name = 'expected/kernel-pins.json'
        raw = sd.read_bytes(name)
        manifest = dict(sd.MANIFEST, files={name: sd.MANIFEST['files'][name]})
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(fetch_inputs, 'MANIFEST', manifest):
                with patch('urllib.request.urlopen', return_value=io.BytesIO(raw)) as request:
                    fetch_inputs.fetch(directory)
                url = request.call_args.args[0]
                self.assertIn('/' + sd.HEAD + '/', url)
                self.assertTrue(url.endswith('/' + name))
                self.assertEqual((Path(directory) / name).read_bytes(), raw)
                with patch('urllib.request.urlopen') as request:
                    fetch_inputs.fetch(directory)
                    request.assert_not_called()

    def test_fetch_rejects_corrupted_download(self):
        name = 'expected/kernel-pins.json'
        manifest = dict(sd.MANIFEST, files={name: sd.MANIFEST['files'][name]})
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(fetch_inputs, 'MANIFEST', manifest):
                with patch('urllib.request.urlopen', return_value=io.BytesIO(b'{}')):
                    with self.assertRaisesRegex(ValueError, 'Pinned input bytes changed'):
                        fetch_inputs.fetch(directory)
            self.assertFalse((Path(directory) / name).exists())


if __name__ == '__main__':
    unittest.main()
