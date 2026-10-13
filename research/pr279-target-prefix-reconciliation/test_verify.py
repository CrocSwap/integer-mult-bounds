"""Source and evidence confusion controls for the exact PR279 reconstruction."""
from copy import deepcopy
from array import array
from pathlib import Path
import importlib.util
import gzip
import io
import json
import tarfile
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pr279_reconciliation', HERE / 'verify.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


class SourceControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source, cls.files = check.collect_candidate()

    def test_exact_candidate_and_schedule(self):
        check.validate_candidate(self.source, self.files)
        result = check.check_selection(self.files)
        self.assertEqual(result['targets'], 880)
        self.assertEqual(result['setup_restore_additions'], 1320)
        self.assertEqual(result['five_stage_paid_call_delta'], -1100)

    def test_missing_new_transform_is_rejected(self):
        files = dict(self.files)
        del files['target_transform.py']
        with self.assertRaisesRegex(ValueError, 'Missing or additional'):
            check.validate_candidate(self.source, files)

    def test_old_transform_receipt_cannot_replace_current_source(self):
        files = dict(self.files)
        files['verify.py'] = (check.ROOT / check.HISTORICAL / 'verify.py').read_bytes()
        with self.assertRaisesRegex(ValueError, 'Changed candidate file: verify.py'):
            check.validate_candidate(self.source, files)

    def test_changed_selection_and_extra_files_are_rejected(self):
        files = dict(self.files)
        files['target-selection.json'] += b' '
        with self.assertRaisesRegex(ValueError, 'Changed candidate file'):
            check.validate_candidate(self.source, files)
        files = dict(self.files)
        files['unreviewed.py'] = b'print("PASS")\n'
        with self.assertRaisesRegex(ValueError, 'Missing or additional'):
            check.validate_candidate(self.source, files)

    def test_source_head_cannot_be_relabelled(self):
        source = deepcopy(self.source)
        source['candidate_head'] = check.REVIEWED
        with self.assertRaisesRegex(ValueError, 'Unexpected source commit'):
            check.validate_candidate(source, self.files)

    def test_omitted_restore_charge_is_rejected(self):
        files = dict(self.files)
        selection = json.loads(files['target-selection.json'])
        selection['groups'][0]['extra_setup_restore_additions'] = 3
        files['target-selection.json'] = json.dumps(selection).encode()
        with self.assertRaisesRegex(ValueError, 'Unpaid setup/restore'):
            check.check_selection(files)

    def test_reconstruction_preserves_every_byte_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / 'source'
            check.reconstruct(self.files, destination)
            self.assertEqual({p.relative_to(destination).as_posix(): p.read_bytes()
                              for p in destination.rglob('*') if p.is_file()}, self.files)
            with self.assertRaises(FileExistsError):
                check.reconstruct(self.files, destination)


class ArchiveControls(unittest.TestCase):
    @staticmethod
    def archive(names, symlink=False):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w:gz') as archive:
            for name in names:
                info = tarfile.TarInfo(name)
                if symlink:
                    info.type = tarfile.SYMTYPE
                    info.linkname = 'target_transform.py'
                else:
                    info.size = 1
                archive.addfile(info, io.BytesIO(b'x'))
        return buffer.getvalue()

    def test_duplicate_member_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate archive member'):
            check.archive_files(self.archive(['a.py', 'a.py']))

    def test_paths_and_symlinks_are_rejected(self):
        for name in ('../a.py', '/a.py', 'C:/a.py', 'a\\b.py', 'a/../b.py'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'Invalid archive member'):
                check.archive_files(self.archive([name]))
        with self.assertRaisesRegex(ValueError, 'Invalid archive member'):
            check.archive_files(self.archive(['a.py'], symlink=True))

    def test_word_digest_ignores_container_time_but_binds_frames(self):
        word = array('i', [1, 4, 7, -1, 21, 3]).tobytes()
        canonical = check.canonical_records(gzip.compress(word, mtime=0))
        self.assertEqual(canonical, check.canonical_records(gzip.compress(word, mtime=100)))
        wrong_frame = array('i', [1, 4, 7, -1, 20, 3]).tobytes()
        self.assertNotEqual(canonical, check.canonical_records(gzip.compress(wrong_frame, mtime=0)))


class EvidenceControls(unittest.TestCase):
    def setUp(self):
        source = check.read_json(HERE / 'SOURCE.json')
        self.manifest = source['candidate_manifest_sha256']
        self.report = dict(
            status='PASS_IMMUTABLE_PARITY_FUSED_GEN4_FIVE_STAGE_BANKED_CONSTRUCTION',
            manifest_sha256=self.manifest, files=114, inputs_unchanged=True,
            kappa=check.KAPPA, fresh_stages=sorted(check.STAGES),
            negative_controls=['omitted ' + stage + ' stage' for stage in sorted(check.STAGES)])

    def test_historical_replay_is_not_current_evidence(self):
        historical = check.read_json(check.ROOT / 'research/community-pr279-audit/verification.json')
        with self.assertRaisesRegex(ValueError, 'Replay source mismatch'):
            check.check_replay(historical, self.manifest)

    def test_each_missing_stage_is_rejected(self):
        for stage in check.STAGES:
            report = deepcopy(self.report)
            report['fresh_stages'].remove(stage)
            with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, 'Incomplete fresh-stage'):
                check.check_replay(report, self.manifest)

    def test_missing_negative_control_and_failed_run_are_rejected(self):
        report = deepcopy(self.report)
        report['negative_controls'].pop()
        with self.assertRaisesRegex(ValueError, 'Missing stage-omission'):
            check.check_replay(report, self.manifest)
        self.report['status'] = 'FAIL'
        with self.assertRaisesRegex(ValueError, 'Replay did not complete'):
            check.check_replay(self.report, self.manifest)


if __name__ == '__main__':
    unittest.main()
