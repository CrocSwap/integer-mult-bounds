"""CLI and evidence-integrity controls. Apache-2.0; AI-assisted by OpenAI Codex."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class EvidenceTests(unittest.TestCase):
    def command(self, package, *options):
        interpreter_options = [option for option in options if option == '-O']
        script_options = [option for option in options if option != '-O']
        return subprocess.run([sys.executable, '-I', *interpreter_options, '-B', str(package / 'verify.py'), *script_options],
                              capture_output=True, text=True, timeout=60,
                              env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))

    def test_normal_and_optimized_read_only_replay(self):
        before = {p.name: p.read_bytes() for p in HERE.iterdir() if p.is_file()}
        for options in ((), ('-O',)):
            answer = self.command(HERE, *options)
            self.assertEqual(answer.returncode, 0, answer.stderr)
            self.assertIn('PASS_UT3_RANK_CAP', answer.stdout)
        self.assertEqual(before, {p.name: p.read_bytes() for p in HERE.iterdir() if p.is_file()})

    def test_source_export_and_evidence_corruption(self):
        # No Git, parent scripts, writable package or network required by the verifier.
        scratch = os.environ.get('UT3_TEST_TMPDIR')
        with tempfile.TemporaryDirectory(prefix='ut3-rank-cap-', dir=scratch) as temporary:
            package = Path(temporary)
            if scratch:
                self.assertEqual(package.resolve().parent, Path(scratch).resolve())
            for name in ('verify.py', 'CERTIFICATE.json'):
                (package / name).write_bytes((HERE / name).read_bytes())
            for options in ((), ('-O',)):
                good = self.command(package, *options)
                self.assertEqual(good.returncode, 0, good.stderr)
            fresh = self.command(package, '--emit')
            self.assertEqual(fresh.returncode, 0, fresh.stderr)
            certificate = json.loads((package / 'CERTIFICATE.json').read_text())
            self.assertEqual(json.loads(fresh.stdout), certificate)
            mutants = []
            changed = json.loads(json.dumps(certificate))
            changed['pilot']['invoice']['rank_mass'][1] = 5
            mutants.append(json.dumps(changed))
            changed = json.loads(json.dumps(certificate))
            changed['profiles_sha256'] = '0' * 64
            mutants.append(json.dumps(changed))
            changed = json.loads(json.dumps(certificate))
            changed['scalar_gauged_fixtures'] = True  # bool must not pass as integer one.
            mutants.append(json.dumps(changed))
            mutants.append('{"schema_version":1,' + json.dumps(certificate)[1:])
            for text in mutants:
                (package / 'CERTIFICATE.json').write_text(text)
                for options in ((), ('-O',)):
                    bad = self.command(package, *options)
                    self.assertNotEqual(bad.returncode, 0)
                    self.assertTrue('certificate mismatch' in bad.stderr or 'duplicate JSON key' in bad.stderr,
                                    bad.stderr)


if __name__ == '__main__':
    unittest.main()
