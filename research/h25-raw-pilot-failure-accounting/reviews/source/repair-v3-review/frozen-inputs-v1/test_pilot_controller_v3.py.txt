"""Independent synthetic controls SOURCE ONLY; no import/test run authorized yet.

After separate source approval these import only the NEW controller, use literal
oracles/owned temporary files, and replace every Popen path with an inert fake.
No installed binary, original module, /proc process, shell or compiler is run.
"""
from pathlib import Path
from types import SimpleNamespace
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest
from unittest.mock import patch

MODULE_PATH = Path(__file__).with_name('pilot_controller_v3.py')
spec = importlib.util.spec_from_file_location('new_pilot_only', MODULE_PATH)
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class MemoryLedger:
    def __init__(self):
        self.rows = []

    def add(self, kind, **values):
        self.rows.append((kind, values))


class FakeStream:
    def __init__(self, number):
        self.number = number

    def fileno(self):
        return self.number

    def close(self):
        pass


class FakeProcess:
    pid = 999999
    returncode = 0

    def __init__(self):
        self.stdout = FakeStream(900001)
        self.stderr = FakeStream(900002)

    def poll(self):
        return 0

    def wait(self, timeout=None):
        return 0


class FakeSelector:
    def __init__(self):
        self.entries = {}

    def register(self, stream, events, name):
        self.entries[stream] = SimpleNamespace(fileobj=stream, data=name)

    def unregister(self, stream):
        del self.entries[stream]

    def get_map(self):
        return self.entries

    def select(self, timeout=None):
        return [(entry, None) for entry in list(self.entries.values())]

    def close(self):
        self.entries.clear()


def synthetic_admission():
    # Deliberately NOT real identity/context/authority. Pure shape fixture only.
    p = pilot.EXPECTED_P
    pin_gcc = {'role': 'gcc', 'path': '/usr/bin/x86_64-linux-gnu-gcc-13',
               'realpath': '/usr/bin/x86_64-linux-gnu-gcc-13', 'bytes': 1023032,
               'sha256': '1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26',
               'mode': 493}
    pin_sh = {'role': 'shell', 'path': '/bin/sh', 'realpath': '/toy/shell',
              'bytes': 1, 'sha256': '1' * 64, 'mode': 365}
    contexts = {path: [{'synthetic': True}] for path in
                ['/usr/bin/x86_64-linux-gnu-gcc-13', '/bin/sh', '/toy/controller',
                 str(Path(p).parent), p, str(Path(p).parent / 'cwd'), p + '/B-prefix',
                 p + '/probe.c', p + '/overlay.specs', p + '/B-prefix/cc1', p + '/B-prefix/collect2']}
    return {'schema': 'h25-raw-unqualified-pilot-admission-v3',
            'status': 'RAW_UNQUALIFIED_DATA_ONLY', 'authority_ref': 'SYNTHETIC-NOT-AUTHORITY',
            'queue_id': 'synthetic-only', 'queue_token_sha256': '2' * 64,
            'controller_sha256': '3' * 64, 'pilot_sha256': '4' * 64,
            'probe_root': p, 'controller_cwd': '/toy/controller', 'child_cwd': str(Path(p).parent / 'cwd'),
            'child_env': {'PATH': '/usr/bin:/bin', 'PYTHONHASHSEED': '0', 'LANG': 'C.UTF-8',
                          'LC_ALL': 'C.UTF-8', 'TZ': 'UTC', 'PYTHONDONTWRITEBYTECODE': '1'},
            'file_pins': [pin_gcc, pin_sh], 'context_pins': contexts,
            'fixtures': {'probe.c': {'bytes': 42, 'sha256': 'unused', 'mode': 292}},
            'jobs': ['C00', 'C01', 'T1', 'T2', 'T3', 'B5', 'T4', 'T5'],
            'limits': {'whole_seconds': 150, 'gcc_seconds': 10, 'calibration_seconds': 5,
                       'stream_bytes': 1048576, 'child_fsize_bytes': 16777216,
                       'sampled_memory_bytes': 1073741824, 'parallel_jobs': 1},
            'funding_ledger_ref': 'synthetic-funding', 'source_review_ref': 'synthetic-source',
            'command_review_ref': 'synthetic-command', 'context_review_ref': 'synthetic-context',
            'expires_utc': '2999-01-01T00:00:00+00:00', 'full_C05': False, 'full_V03': False}


class SourceOnlySyntheticControls(unittest.TestCase):
    def test_duplicate_json_fields_refused(self):
        with self.assertRaises(pilot.Refusal):
            pilot.json_bytes(b'{"authority_ref":"x","authority_ref":"y"}')

    def test_missing_authority_digest_refused(self):
        with self.assertRaises(pilot.Refusal):
            pilot.validate_authority({}, b'{}', b'q' * 32, None, '0' * 64, 'x')

    def test_wrong_admission_hash_refused(self):
        token = b'q' * 32
        with self.assertRaises(pilot.Refusal):
            pilot.validate_authority({'authority_ref': 'x'}, b'{}', token,
                                     '0' * 64, hashlib.sha256(token).hexdigest(), 'x')

    def test_wrong_queue_token_refused(self):
        raw = b'{}'
        with self.assertRaises(pilot.Refusal):
            pilot.validate_authority({}, raw, b'q' * 32, hashlib.sha256(raw).hexdigest(),
                                     '0' * 64, 'x')

    def test_wrong_authority_ref_refused(self):
        token, raw = b'q' * 32, b'{}'
        td = hashlib.sha256(token).hexdigest()
        with self.assertRaises(pilot.Refusal):
            pilot.validate_authority({'authority_ref': 'wrong', 'queue_token_sha256': td},
                                     raw, token, hashlib.sha256(raw).hexdigest(), td, 'x')

    def test_valid_authority_relation_is_not_a_grant(self):
        token = b'q' * 32
        td = hashlib.sha256(token).hexdigest()
        a = {'authority_ref': 'synthetic', 'queue_token_sha256': td}
        raw = json.dumps(a).encode()
        pilot.validate_authority(a, raw, token, hashlib.sha256(raw).hexdigest(), td, 'synthetic')
        # No call of main/preflight/Popen; relation alone is never qualification.

    def test_job_order_and_withheld_original_jobs(self):
        queue = pilot.jobs('/owned/probe')
        self.assertEqual([j[0] for j in queue], ['C00', 'C01', 'T1', 'T2', 'T3', 'B5', 'T4', 'T5'])
        self.assertEqual([j[2] for j in queue], [5, 5, 10, 10, 10, 10, 10, 10])
        self.assertEqual(queue[5][1], ['/usr/bin/x86_64-linux-gnu-gcc-13', '-dumpspecs'])
        self.assertEqual(queue[6][1], ['/usr/bin/x86_64-linux-gnu-gcc-13',
                                     '-specs=/owned/probe/overlay.specs', '-dumpspecs'])
        self.assertFalse(any('field-negative-variants' in arg for _, args, _ in queue for arg in args))
        self.assertFalse(any(x[0] in ('B1', 'B2', 'B3', 'B4') for x in queue))

    def test_only_complete_named_nonzero_calibration_outcomes_allowed(self):
        pilot.expected_outcome('C00', 97, b'H25_UNEXPECTED_CC1_EXECUTION_71\n', b'')
        pilot.expected_outcome('C01', 98, b'H25_UNEXPECTED_COLLECT2_EXECUTION_71\n', b'')
        for args in [('C00', 0, b'', b''), ('C00', 97, b'', b''),
                     ('C01', 98, b'H25_UNEXPECTED_COLLECT2_EXECUTION_71\n', b'error'),
                     ('T1', 97, b'', b''), ('B5', -9, b'', b'')]:
            with self.subTest(args=args), self.assertRaises(pilot.Refusal):
                pilot.expected_outcome(*args)

    def test_execution_or_compile_markers_stop_noncalibration(self):
        for marker in [b'H25_UNEXPECTED_CC1_EXECUTION_71\n',
                       b'H25_UNEXPECTED_COLLECT2_EXECUTION_71\n',
                       b'H25_REPORTER_PROBE_MUST_NOT_COMPILE_71']:
            with self.subTest(marker=marker), self.assertRaises(pilot.Refusal):
                pilot.expected_outcome('T2', 0, marker, b'')

    def test_t2_missing_names_are_observations_not_admission(self):
        r = pilot.raw_hypotheses('T2', b'', b'', Path('/owned/probe'), None)
        self.assertIs(r['chosen_cc1_path_observed'], False)
        self.assertIs(r['chosen_collect2_path_observed'], False)
        self.assertIs(r['names_are_unqualified_hypotheses'], True)

    def test_equal_empty_builtin_observations_do_not_prove_emission(self):
        r = pilot.raw_hypotheses('T4', b'', b'', Path('/owned/probe'), b'')
        self.assertIs(r['observed_stdout_equal_B5'], True)
        self.assertIs(r['empty_outputs_can_compare_equal'], True)
        self.assertEqual(r['interpretation'], 'RAW_UNQUALIFIED_OBSERVED_RELATIONS_ONLY')

    def test_fixture_hashes_are_literal_independent_oracles(self):
        manifest = pilot.fixture_manifest()
        self.assertEqual(manifest['probe.c']['sha256'],
                         'b345d84d8da60983a6e43c71902a36e64f509a280bcd52b5988be8be07ce6cd6')
        self.assertEqual(manifest['overlay.specs']['sha256'],
                         '0163aae6bfb1930ef16557472d18856cadf71456f25fa0c3cbfaa55bf8ff99fd')
        self.assertEqual(manifest['B-prefix/cc1']['sha256'],
                         'cafc8280ff7900c85b616ff74c243631b2ab018c438f1dbb99c4d12a9e07c511')
        self.assertEqual(manifest['B-prefix/collect2']['sha256'],
                         'cdbde756b30c3a0f4e05b21b820c840ea4b5f333fa1e483f10a829f45f06dafd')

    def test_shape_refuses_placeholders_and_wrong_context(self):
        a = synthetic_admission()
        a['fixtures'] = pilot.fixture_manifest()
        pilot.validate_shape(a)  # Pure shape only, never actual pin validation.
        for change in [{'authority_ref': None}, {'probe_root': '/unowned/probe'},
                       {'child_cwd': '/original/stage'}, {'child_env': {}},
                       {'controller_sha256': None}, {'jobs': ['B1']},
                       {'limits': {}}, {'file_pins': []}, {'full_C05': True}]:
            b = copy.deepcopy(a); b.update(change)
            with self.subTest(change=change), self.assertRaises(pilot.Refusal):
                pilot.validate_shape(b)

    def test_bounded_reads_and_symlink_refusal_owned_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'input'
            p.write_bytes(b'abc')
            self.assertEqual(pilot.read_bounded(str(p), 3), b'abc')
            with self.assertRaises(pilot.Refusal):
                pilot.read_bounded(str(p), 2)
            q = Path(tmp) / 'alias'; q.symlink_to(p)
            with self.assertRaises(OSError):
                pilot.read_bounded(str(q), 3)

    def test_exclusive_file_rejects_reuse_and_ledger_is_append_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'ledger'
            led = pilot.Ledger(p)
            led.add('A', launched=False); led.add('B', launched=False); led.close()
            rows = p.read_bytes().splitlines(keepends=True)
            self.assertEqual(len(rows), 2)
            second = json.loads(rows[1])
            self.assertEqual(second['previous_sha256'], hashlib.sha256(rows[0]).hexdigest())
            with self.assertRaises(FileExistsError):
                pilot.Ledger(p)
            self.assertEqual(p.read_bytes(), b''.join(rows))

    def test_cap_plus_one_is_retained_and_failure_ledgered_no_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); (p / 'raw').mkdir()
            led = MemoryLedger()
            blocks = {900001: [b'x' * 65536] * 16 + [b'x'], 900002: [b'']}
            def fake_read(fd, limit):
                value = blocks[fd].pop(0)
                self.assertLessEqual(len(value), limit)
                return value
            with patch.object(pilot.subprocess, 'Popen', return_value=FakeProcess()) as spawn, \
                 patch.object(pilot.selectors, 'DefaultSelector', FakeSelector), \
                 patch.object(pilot.os, 'set_blocking'), patch.object(pilot.os, 'read', fake_read), \
                 patch.object(pilot, 'sampled_rss', return_value=0), \
                 patch.object(pilot, 'cleanup', return_value={'direct_child_reaped': True, 'residual_group': False}):
                with self.assertRaises(pilot.Refusal):
                    pilot.capture_job('T1', ['owned-fixture'], 10, p,
                                      {'child_cwd': str(p), 'child_env': pilot.ENV6},
                                      led, pilot.time.monotonic() + 20)
                self.assertEqual(spawn.call_count, 1)  # Mock only, no process.
            self.assertEqual((p / 'raw/T1.stdout.raw').stat().st_size, 1048577)
            self.assertEqual([r[0] for r in led.rows],
                             ['SPAWN_ENTERED', 'SPAWN_RETURNED', 'JOB_CAPTURE_TERMINAL'])
            self.assertIs(led.rows[-1][1]['intended_complete_emission'], False)
            self.assertIsNotNone(led.rows[-1][1]['capture_error'])

    def test_main_wrong_admission_refuses_before_popen(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); (p / 'admission').write_bytes(b'{}'); (p / 'token').write_bytes(b'q' * 32)
            with patch.object(pilot.subprocess, 'Popen', side_effect=AssertionError('NO NATIVE')) as spawn:
                code = pilot.main(['--admission', str(p / 'admission'), '--admission-sha256', '0' * 64,
                                   '--queue-token-file', str(p / 'token'), '--queue-token-sha256', '1' * 64,
                                   '--authority-ref', 'synthetic-no-grant', '--pilot', str(p / 'absent')])
                self.assertEqual(code, 2); spawn.assert_not_called()


class CleanupFaultCombinations(unittest.TestCase):
    def run_capture(self, tmp, ledger, process, fake_read, fsync=None, close=None):
        from contextlib import ExitStack
        p = Path(tmp); (p / 'raw').mkdir()
        with ExitStack() as stack:
            stack.enter_context(patch.object(pilot.subprocess, 'Popen', return_value=process))
            stack.enter_context(patch.object(pilot.selectors, 'DefaultSelector', FakeSelector))
            stack.enter_context(patch.object(pilot.os, 'set_blocking'))
            stack.enter_context(patch.object(pilot.os, 'read', fake_read))
            stack.enter_context(patch.object(pilot, 'sampled_rss', return_value=0))
            stack.enter_context(patch.object(pilot, 'cleanup', return_value={
                'direct_child_reaped': True, 'residual_group': False}))
            fallback = stack.enter_context(patch.object(pilot, 'parent_fallback'))
            if fsync is not None:
                stack.enter_context(patch.object(pilot.os, 'fsync', fsync))
            if close is not None:
                stack.enter_context(patch.object(pilot.os, 'close', close))
            with self.assertRaises(pilot.OperationStop) as caught:
                pilot.capture_job('T1', ['owned-fake-only'], 10, p,
                    {'child_cwd': str(p), 'child_env': pilot.ENV6}, ledger,
                    pilot.time.monotonic() + 20)
            return caught.exception.record, fallback.call_count

    def test_cap_plus_fsync_failures_keep_cap_primary_and_terminal(self):
        blocks = {900001: [b'x' * 65536] * 16 + [b'x'], 900002: [b'']}
        def read(fd, limit):
            return blocks[fd].pop(0)
        def sync(fd):
            raise OSError('injected-fsync')
        with tempfile.TemporaryDirectory() as tmp:
            ledger = MemoryLedger()
            record, fallback = self.run_capture(tmp, ledger, FakeProcess(), read, fsync=sync)
            self.assertIn('stream exceeds cap', record['primary_error']['error'])
            stages = [x['stage'] for x in record['secondary_errors']]
            self.assertIn('stdout.raw.fsync', stages)
            self.assertIn('stderr.raw.fsync', stages)
            self.assertEqual(ledger.rows[-1][0], 'JOB_CAPTURE_TERMINAL')
            self.assertEqual((Path(tmp) / 'raw/T1.stdout.raw').stat().st_size, 1048577)
            self.assertEqual(fallback, 1)

    def test_multiple_close_failures_do_not_skip_remaining_owners(self):
        stream_closes, fd_closes = [], []
        class BadStream(FakeStream):
            def close(self):
                stream_closes.append(self.number)
                raise OSError('injected-pipe-close')
        proc = FakeProcess(); proc.stdout = BadStream(900001); proc.stderr = BadStream(900002)
        original_close = os.close
        def close(fd):
            fd_closes.append(fd)
            original_close(fd)
            raise OSError('injected-raw-close-after-real-close')
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(FakeSelector, 'close', side_effect=OSError('injected-selector-close')):
            record, _ = self.run_capture(tmp, MemoryLedger(), proc, lambda fd,n: b'', close=close)
            self.assertEqual(record['primary_error']['stage'], 'selector.close')
            self.assertEqual(stream_closes, [900001, 900002])
            self.assertEqual(len(fd_closes), 2)
            self.assertIn('stdout.raw.close', [x['stage'] for x in record['secondary_errors']])
            self.assertIn('stderr.raw.close', [x['stage'] for x in record['secondary_errors']])

    def test_terminal_ledger_add_failure_is_stop_and_fallback(self):
        class BadTerminalLedger(MemoryLedger):
            def add(self, kind, **values):
                if kind == 'JOB_CAPTURE_TERMINAL':
                    raise OSError('terminal-ledger-add')
                super().add(kind, **values)
        with tempfile.TemporaryDirectory() as tmp:
            record, fallback = self.run_capture(tmp, BadTerminalLedger(), FakeProcess(), lambda fd,n: b'')
            self.assertEqual(record['primary_error']['stage'], 'JOB_CAPTURE_TERMINAL.ledger_add')
            self.assertEqual(fallback, 1)
            self.assertIs(record['reporter_qualified'], False)

    def test_spawn_returned_ledger_failure_still_closes_both_acquired_pipes(self):
        closed = []
        class TrackedStream(FakeStream):
            def close(self):
                closed.append(self.number)
        class BadSpawnLedger(MemoryLedger):
            def add(self, kind, **values):
                if kind == 'SPAWN_RETURNED':
                    raise OSError('spawn-returned-ledger')
                super().add(kind, **values)
        proc = FakeProcess(); proc.stdout = TrackedStream(900001); proc.stderr = TrackedStream(900002)
        with tempfile.TemporaryDirectory() as tmp:
            record, _ = self.run_capture(tmp, BadSpawnLedger(), proc, lambda fd,n: b'')
            self.assertIn('spawn-returned-ledger', record['primary_error']['error'])
            self.assertEqual(closed, [900001, 900002])
            self.assertEqual(record['primary_error']['stage'], 'capture')

    def test_ledger_close_after_primary_retains_primary_and_secondary(self):
        class BadClose(MemoryLedger):
            def close(self):
                raise OSError('ledger-close-after-primary')
        failures = pilot.Failures(); failures.add('earlier-capture', ValueError('first'))
        self.assertIs(pilot.close_accounting(BadClose(), failures, pilot.time.monotonic()+10), False)
        self.assertEqual(failures.view()['primary_error']['stage'], 'earlier-capture')
        self.assertEqual(failures.view()['secondary_errors'][0]['stage'], 'ledger.close')

    def test_ledger_close_after_apparent_success_prevents_success(self):
        class BadClose(MemoryLedger):
            def close(self):
                raise OSError('ledger-close-after-data')
        failures = pilot.Failures()
        self.assertIs(pilot.close_accounting(BadClose(), failures, pilot.time.monotonic()+10), False)
        self.assertEqual(failures.view()['primary_error']['stage'], 'ledger.close')
        self.assertIn('ledger-close-after-data', failures.view()['primary_error']['error'])

    def test_ledger_fsync_failure_does_not_skip_fd_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = pilot.Ledger(Path(tmp) / 'ledger')
            closed, original_close = [], os.close
            def close(fd):
                closed.append(fd); original_close(fd)
            with patch.object(pilot.os, 'fsync', side_effect=OSError('ledger-fsync')), \
                 patch.object(pilot.os, 'close', close):
                with self.assertRaises(pilot.OperationStop) as caught:
                    ledger.close()
            self.assertEqual(len(closed), 1)
            self.assertEqual(caught.exception.record['primary_error']['stage'], 'ledger.fsync')


if __name__ == '__main__':
    unittest.main()
