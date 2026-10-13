"""Exercise coverage against real replay bytes, including coherently rehashed omissions."""
import ast
from contextlib import contextmanager
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import verify_frontier741_bindings as historical
import verify_frontier_replay as coverage


class ReplayCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.root = Path(cls.tmp.name).resolve()
        cls.ancestor = cls.root / 'ancestor'
        cls.complex = cls.ancestor / 'complex'
        cls.bit = cls.ancestor / 'bit'
        shutil.copytree(ROOT / 'research/community-frontier741-audit/bit', cls.bit)
        archive_path = ROOT / 'research/community-queue-20261013/pr741-fresh-replay.tar.gz'
        prefix = PurePosixPath('pr741-fresh-replay')
        with tarfile.open(archive_path) as archive:
            members = {PurePosixPath(m.name): m for m in archive if m.isfile()}
            cls.pristine = json.loads(archive.extractfile(members[prefix / 'RECEIPT.json']).read())
            required = {'RECEIPT.json', *cls.pristine['artifacts'],
                        *(s['name'] + '.log' for s in cls.pristine['stages'])}
            cls.archive_local = {
                p.relative_to(prefix).as_posix() for p in members
                if p.parent == prefix / 'local'
            }
            # Extract only consumed ordinary files; compiler symlinks are not needed.
            for relative in required:
                target = (cls.complex / relative).resolve()
                if not target.is_relative_to(cls.complex):
                    raise ValueError('Invalid retained replay path')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.extractfile(members[prefix / relative]).read())
        cls.receipt = cls.complex / 'RECEIPT.json'
        cls.stages = cls.complex / 'STAGES.json'

    @contextmanager
    def changed(self, *paths):
        saved = {p: p.read_bytes() if p.exists() else None for p in paths}
        try:
            yield
        finally:
            for path, content in saved.items():
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_bytes(content)

    def write(self, path, value):
        path.write_bytes((json.dumps(value, indent=2) + '\n').encode())

    def write_receipt_and_stages(self, receipt):
        self.write(self.stages, receipt['stages'])
        receipt['artifacts']['STAGES.json'] = sha256(self.stages.read_bytes()).hexdigest()
        self.write(self.receipt, receipt)

    def test_pristine_retained_replay_passes_both_checks(self):
        coverage.check_coverage(self.complex)
        self.assertEqual(coverage.check_ancestry(self.ancestor)['decimal'],
                         '0.001661202643272239')

    def test_contract_matches_frozen_producer_and_retained_local_inventory(self):
        # Parse the producer without importing or executing its expensive pipeline.
        producer = ROOT / 'research/complex-sw4-frame8/verify.py'
        tree = ast.parse(producer.read_text(encoding='utf-8'))
        calls = [n.value for n in tree.body if isinstance(n, ast.Expr)
                 and isinstance(n.value, ast.Call)
                 and isinstance(n.value.func, ast.Name) and n.value.func.id == 'run']
        names = tuple(ast.literal_eval(call.args[0]) for call in calls)
        fixed_lists = [ast.literal_eval(n.value) for n in tree.body
                       if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == 'files' for t in n.targets)]
        self.assertEqual(len(names), 22)
        self.assertEqual(names, coverage.EXPECTED_STAGES)
        self.assertEqual(len(fixed_lists), 1)
        self.assertEqual(len(fixed_lists[0]), 34)
        self.assertEqual(len(self.archive_local), 10)
        self.assertEqual(set(fixed_lists[0]) | self.archive_local, coverage.EXPECTED_ARTIFACTS)
        self.assertEqual(set(self.pristine['artifacts']), coverage.EXPECTED_ARTIFACTS)
        self.assertEqual(len(coverage.EXPECTED_ARTIFACTS), 44)

    def test_replacement_phase_stage_with_matching_index_and_log_is_rejected(self):
        receipt = deepcopy(self.pristine)
        phase = next(s for s in receipt['stages'] if s['name'] == 'all-native-phase-edges')
        old_log = self.complex / (phase['name'] + '.log')
        phase['name'] = 'unrelated-successful-stage'
        new_log = self.complex / (phase['name'] + '.log')
        with self.changed(self.receipt, self.stages, old_log, new_log):
            new_log.write_bytes(old_log.read_bytes())
            old_log.unlink()
            self.write_receipt_and_stages(receipt)
            # This is a real accepted historical input, not a mocked reader.
            historical.check(self.bit, self.complex)
            with self.assertRaisesRegex(ValueError, 'Required replay stages'):
                coverage.check_coverage(self.complex)

    def test_each_artifact_omission_and_file_deletion_is_rejected(self):
        for relative in sorted(self.pristine['artifacts']):
            with self.subTest(artifact=relative):
                path = self.complex / relative
                receipt = deepcopy(self.pristine)
                del receipt['artifacts'][relative]
                with self.changed(self.receipt, path):
                    path.unlink()
                    self.write(self.receipt, receipt)
                    with self.assertRaisesRegex(ValueError, 'Required replay artifact inventory'):
                        coverage.check_coverage(self.complex)

    def test_omitted_phase_evidence_passes_historical_binding_but_fails_new_cli(self):
        relative = 'local/CLIFFORD-REVIEW.json'
        receipt = deepcopy(self.pristine)
        del receipt['artifacts'][relative]
        path = self.complex / relative
        work = self.root / 'must-not-start'
        with self.changed(self.receipt, path):
            path.unlink()
            self.write(self.receipt, receipt)
            historical.check(self.bit, self.complex)
            result = subprocess.run(
                [sys.executable, '-B', str(ROOT / 'scripts/verify_frontier_replay.py'),
                 '--frontier', '799', '--work', str(work), '--ancestor', str(self.ancestor)],
                capture_output=True, text=True, timeout=15,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Required replay artifact inventory', result.stderr)
            self.assertFalse(work.exists(), 'An incomplete ancestor must fail before work begins')

    def test_stage_order_and_failure_cannot_be_hidden_in_matching_index(self):
        for kind in ('reordered', 'failed'):
            with self.subTest(kind=kind), self.changed(self.receipt, self.stages):
                receipt = deepcopy(self.pristine)
                if kind == 'reordered':
                    receipt['stages'][0], receipt['stages'][1] = receipt['stages'][1], receipt['stages'][0]
                else:
                    receipt['stages'][0]['exit_code'] = 1
                self.write_receipt_and_stages(receipt)
                if kind == 'reordered':
                    historical.check(self.bit, self.complex)
                with self.assertRaisesRegex(ValueError, 'Required replay stages'):
                    coverage.check_coverage(self.complex)

    def test_disagreeing_stage_index_is_rejected_even_with_updated_hash(self):
        receipt = deepcopy(self.pristine)
        index = deepcopy(receipt['stages'])
        index[0]['exit_code'] = 1
        with self.changed(self.receipt, self.stages):
            self.write(self.stages, index)
            receipt['artifacts']['STAGES.json'] = sha256(self.stages.read_bytes()).hexdigest()
            self.write(self.receipt, receipt)
            historical.check(self.bit, self.complex)
            with self.assertRaisesRegex(ValueError, 'Receipt stages differ'):
                coverage.check_coverage(self.complex)

    def test_added_hash_bound_artifact_is_not_part_of_frozen_inventory(self):
        receipt = deepcopy(self.pristine)
        extra = self.complex / 'unrelated-evidence.json'
        with self.changed(self.receipt, extra):
            self.write(extra, {'status': 'unrelated'})
            receipt['artifacts'][extra.name] = sha256(extra.read_bytes()).hexdigest()
            self.write(self.receipt, receipt)
            historical.check(self.bit, self.complex)
            with self.assertRaisesRegex(ValueError, 'Required replay artifact inventory'):
                coverage.check_coverage(self.complex)

    def test_public_result_is_written_only_after_generated_evidence_passes(self):
        # Substitute only native generation; validate actual archived files and hashes.
        for omit in (False, True):
            work = self.root / ('generated-incomplete' if omit else 'generated-complete')

            def supplier(command, **kwargs):
                self.assertEqual(Path(command[2]).name, 'verify_frontier741.py')
                replay = Path(command[-1])
                shutil.copytree(self.ancestor, replay)
                self.write(replay / 'RESULT.json', historical.check(replay / 'bit', replay / 'complex'))
                if omit:
                    receipt_path = replay / 'complex/RECEIPT.json'
                    receipt = json.loads(receipt_path.read_bytes())
                    relative = 'local/CLIFFORD-REVIEW.json'
                    del receipt['artifacts'][relative]
                    (replay / 'complex' / relative).unlink()
                    self.write(receipt_path, receipt)
                return subprocess.CompletedProcess(command, 0)

            with self.subTest(omit=omit), patch.object(coverage.subprocess, 'run', side_effect=supplier) as run:
                args = ['--frontier', '741', '--work', str(work)]
                if omit:
                    with self.assertRaisesRegex(ValueError, 'Required replay artifact inventory'):
                        coverage.main(args)
                    self.assertFalse((work / 'RESULT.json').exists())
                else:
                    coverage.main(args)
                    published = json.loads((work / 'RESULT.json').read_bytes())
                    self.assertEqual(published['receipt_coverage'], {'stages': 22, 'artifacts': 44})
                    self.assertEqual(published['decimal'], '0.001661202643272239')
                self.assertTrue((work / 'replay/RESULT.json').exists())
                run.assert_called_once()

    def test_799_fresh_and_reused_ancestry_are_checked_before_publication(self):
        retained_result = ROOT / 'research/community-frontier799-audit/RESULT.json'
        for reuse in (False, True):
            for omit in (False, True):
                work = self.root / f'generated799-{reuse}-{omit}'
                supplied = self.root / f'supplied799-{reuse}-{omit}'
                if reuse:
                    shutil.copytree(self.ancestor, supplied)

                def supplier(command, **kwargs):
                    self.assertEqual(Path(command[2]).name, 'verify_frontier799.py')
                    replay = Path(command[command.index('--work') + 1])
                    replay.mkdir()
                    if reuse:
                        self.assertEqual(command[-2:], ['--ancestor', str(supplied)])
                        ancestor = supplied
                    else:
                        self.assertNotIn('--ancestor', command)
                        ancestor = replay / 'ancestor'
                        shutil.copytree(self.ancestor, ancestor)
                    shutil.copyfile(retained_result, replay / 'RESULT.json')
                    if omit:
                        receipt_path = ancestor / 'complex/RECEIPT.json'
                        receipt = json.loads(receipt_path.read_bytes())
                        del receipt['artifacts']['local/CLIFFORD-REVIEW.json']
                        self.write(receipt_path, receipt)
                    return subprocess.CompletedProcess(command, 0)

                args = ['--frontier', '799', '--work', str(work)]
                if reuse:
                    args += ['--ancestor', str(supplied)]
                with self.subTest(reuse=reuse, omit=omit), patch.object(
                        coverage.subprocess, 'run', side_effect=supplier) as run:
                    if omit:
                        with self.assertRaisesRegex(ValueError, 'Required replay artifact inventory'):
                            coverage.main(args)
                        self.assertFalse((work / 'RESULT.json').exists())
                    else:
                        coverage.main(args)
                        result = json.loads((work / 'RESULT.json').read_bytes())
                        self.assertEqual(result.pop('receipt_coverage'), {'stages': 22, 'artifacts': 44})
                        self.assertEqual(result, json.loads(retained_result.read_bytes()))
                    run.assert_called_once()

    def test_supplier_failure_never_publishes_a_result(self):
        work = self.root / 'failed-supplier'
        with patch.object(coverage.subprocess, 'run',
                          side_effect=subprocess.CalledProcessError(1, ['supplier'])):
            with self.assertRaises(subprocess.CalledProcessError):
                coverage.main(['--frontier', '799', '--work', str(work)])
        self.assertFalse((work / 'RESULT.json').exists())


if __name__ == '__main__':
    unittest.main()
