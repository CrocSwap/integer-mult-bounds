"""NUL-bearing PAX paths must not pass offline export validation.

Builds on Tekalign's exporter and roger-sato's path/topology controls.
Prepared for josecarlosgonzalezroque-design with substantial OpenAI Codex
assistance. Apache-2.0.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import export_research_package as exporter
sys.path.pop(0)


class ExportNulPathTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.package = 'research/fixture'

    def bundle(self, names):
        # Construct the archive independently of the exporter. PAX preserves a
        # NUL in a path even though the ordinary tar name field terminates there.
        payloads = {name: b'\x00\xffproof payload\r\n' for name in names}
        payloads[self.package + '/VERIFY.json'] = json.dumps({'inputs': names}).encode('utf-8')
        receipt = {'format': exporter.FORMAT, 'commit': 'a' * 40,
                   'package': self.package, 'files': [
                       {'path': name, 'mode': 0o644, 'size': len(data),
                        'sha256': hashlib.sha256(data).hexdigest()}
                       for name, data in payloads.items()]}
        archive = self.root / 'bundle.tar'
        with tarfile.open(archive, 'w', format=tarfile.PAX_FORMAT) as out:
            rows = [*payloads.items(), (exporter.RECEIPT, json.dumps(receipt).encode('utf-8'))]
            for name, data in rows:
                info = tarfile.TarInfo(name)
                info.size, info.mode = len(data), 0o644
                info.pax_headers = {'path': name}
                out.addfile(info, io.BytesIO(data))
        return archive, receipt, payloads

    def cli(self, archive, check_inputs):
        flags = ['-O'] if sys.flags.optimize else []
        return subprocess.run(
            [sys.executable, *flags, '-B', str(ROOT / 'scripts/export_research_package.py'),
             'check', str(archive), *(['--check-inputs'] if check_inputs else [])],
            env={**os.environ, 'PATH': ''}, capture_output=True, timeout=30)

    def test_nul_pax_members_cannot_receive_a_success_receipt(self):
        names = ('inputs/\x00evidence.json', 'inputs/evidence\x00hidden.json',
                 'inputs\x00hidden/evidence.json', 'inputs/evidence.json\x00')
        for name in names:
            archive, _, _ = self.bundle([name])
            original = archive.read_bytes()
            with tarfile.open(archive) as source:
                self.assertEqual(source.getmember(name).name, name)
                # The former validator accepted these complete, consistent
                # receipts, but the advertised files cannot be materialized.
                with self.assertRaisesRegex(ValueError, 'embedded null'):
                    source.extractall(self.root / 'extracted', filter='data')
            for check_inputs in (False, True):
                with self.subTest(name=name, check_inputs=check_inputs):
                    result = self.cli(archive, check_inputs)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertIn(b'NUL', result.stderr)
                    self.assertNotIn(b'PASS_RESEARCH_EXPORT', result.stdout)
                    self.assertEqual(archive.read_bytes(), original)

    def test_valid_pax_paths_and_nul_payloads_remain_byte_exact(self):
        names = ['inputs/evidencehidden.json', 'inputs/雪.bin',
                 'inputs/carriage\rreturn', 'inputs/line\nfeed', 'inputs/crlf\r\nname']
        archive, receipt, payloads = self.bundle(names)
        self.assertEqual(exporter.check_bundle(archive), receipt)
        checked = exporter.check_bundle(archive, check_inputs=True)
        self.assertEqual(checked, {**receipt, 'declared_inputs_checked': len(names)})
        result = self.cli(archive, True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(b'PASS_RESEARCH_EXPORT', result.stdout)
        with tarfile.open(archive) as source:
            for name, data in payloads.items():
                self.assertEqual(source.extractfile(name).read(), data)

    def test_committed_nul_declaration_rejects_before_tree_lookup(self):
        raw = json.dumps({'inputs': ['inputs/evidence\x00hidden.json']}).encode('utf-8')
        rows = (row for row in [('b' * 40, raw)])
        with patch.object(exporter, 'git', side_effect=[b'a' * 40, b'']) as git, \
             patch.object(exporter, 'git_blobs', return_value=rows):
            with self.assertRaisesRegex(ValueError, 'NUL'):
                exporter.inventory(self.root, self.package, 'HEAD')
        self.assertEqual(git.call_count, 1)


if __name__ == '__main__':
    unittest.main()
