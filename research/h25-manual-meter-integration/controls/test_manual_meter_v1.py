"""New pure-source fixture controls. Never load C2/F4/A4 or invoke native owner.

Only the new meter and loader top-level definitions are imported; actual source
loading entry points are not called. These controls confer no original runtime
qualification and no live profile, lease, FD1 identity or financial admission.
"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest

HERE = Path(__file__).resolve().parents[1] / 'implementation'


def new_module(filename, name):
    spec = importlib.util.spec_from_file_location(name,HERE/filename)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


M = new_module('manual_meter_v1.py','fixture_manual_meter')
L = new_module('manual_loader_v1.py','fixture_manual_loader')


class ManualPureControls(unittest.TestCase):
    def setUp(self):
        self.os = M.os
        M.FIRST[0] = None; M.SECONDARY[:] = [None]*32; M.IO_UNKNOWN[0] = False
        M.BODY_ATTEMPTED[0] = False

    def tearDown(self):
        M.os = self.os

    def test_closed_body_projection_has_no_synthetic_wait_or_physical_total(self):
        record = M.body_data('Own',{}, {},{},11,19,True,False,123,None,[])
        self.assertEqual(record['body'],dict(state='KNOWN',begin_ns=11,end_ns=19,elapsed_ns=8))
        self.assertEqual(record['owned_wait'],'NO_CHILD')
        self.assertIsNone(record['child_exit'])
        self.assertEqual(record['owned_cleanup'],'KNOWN_CLOSED')
        self.assertEqual(record['physical_boundary'],'OPEN_NOT_ZERO')

    def test_clock_reversal_or_missing_endpoint_stays_unknown(self):
        for begin,end in ((8,7),(8,None),(None,9)):
            record = M.body_data('Own',{}, {},{},begin,end,False,True,None,'Fault',[])
            self.assertEqual(record['body']['state'],'UNKNOWN')
            self.assertIsNone(record['body']['elapsed_ns'])
            self.assertEqual(record['owned_cleanup'],'UNKNOWN')
            self.assertTrue(record['errors']['io_unknown'])

    def test_exact_profile_and_action_cannot_upgrade(self):
        plan = dict.fromkeys(M.PLAN_KEYS)
        plan.update(schema='fresh-fixed-manual-operation-v1',attempt_id='Own',
            profile='normal',action='INITIALIZE',cleanup_ns=0,phase='INITIAL',policy_pins=[])
        self.assertIs(M.plan_shape(plan,'INITIALIZE','normal'),plan)
        for action,profile in (('CLOSE','normal'),('INITIALIZE','optimized'),('PAYLOAD','normal')):
            with self.assertRaises(M.AdapterStop): M.plan_shape(plan,action,profile)
        plan['cleanup_ns'] = True
        with self.assertRaises(M.AdapterStop): M.plan_shape(plan,'INITIALIZE','normal')

    def test_command_has_fresh_exclusive_original_capture_and_exact_mode(self):
        pin = dict(bytes=123,sha256='a'*64)
        path = M.ROOT/'runtime/manual-operations/Own.json'
        normal = M.shell_command('INITIALIZE','normal',path,pin)
        optimized = M.shell_command('INITIALIZE','optimized',path,pin)
        self.assertTrue(normal.startswith('umask 077\nset -C\nexec /usr/bin/env -i '))
        self.assertIn('PYTHONHASHSEED=0',normal)
        self.assertIn(' -S -s -P -B ',normal)
        self.assertNotIn(' -O ',normal)
        self.assertIn(' -S -s -P -B -O ',optimized)
        self.assertTrue(normal.endswith(' > '+str(M.ROOT/'control/prospective-financial-v1/entries/Own/METER_BODY.json')+
            ' 2> '+str(M.ROOT/'runtime/manual-operations/Own.stderr.json')))
        self.assertNotIn('PLAN_SHA',normal)

    def test_first_exception_identity_survives_close_failure(self):
        first,second = RuntimeError('first'),OSError('close')
        M.remember(first)
        calls = []
        def failed_close(fd):
            calls.append(fd); raise second
        M.os = SimpleNamespace(close=failed_close)
        slot = [77,'OWNED','fixture',False]
        with self.assertRaises(OSError): M.close(slot)
        self.assertIs(M.FIRST[0],first)
        self.assertIs(M.SECONDARY[0],second)
        self.assertEqual(slot[1],'CLOSE_UNKNOWN')
        self.assertTrue(M.IO_UNKNOWN[0])
        with self.assertRaises(M.AdapterStop): M.close(slot)
        self.assertEqual(calls,[77])

    def test_acquisition_uncertainty_quarantines_next_open(self):
        calls = []
        original = OSError('acquire')
        def failed_open(*args):
            calls.append(args); raise original
        M.os = SimpleNamespace(open=failed_open,O_NOFOLLOW=1,O_CLOEXEC=2)
        saved = [slot[:] for slot in M.SLOTS]
        M.SLOTS[:] = [[None,'FREE',None,False] for unused in range(32)]
        try:
            with self.assertRaises(OSError): M.acquire('/fixture')
            self.assertIs(M.FIRST[0],original)
            self.assertEqual(M.SLOTS[0][1],'PENDING')
            with self.assertRaises(M.AdapterStop): M.acquire('/fixture2')
            self.assertEqual(len(calls),1)
        finally:
            M.SLOTS[:] = saved

    def test_partial_body_write_cannot_be_retried(self):
        writes = []
        error = OSError('partial BODY')
        def writer(fd,raw):
            writes.append((fd,raw))
            if len(writes)==1: return 1
            raise error
        M.os = SimpleNamespace(write=writer,fsync=lambda fd: None)
        with self.assertRaises(OSError): M.emit_fd1(b'abc')
        self.assertTrue(M.BODY_ATTEMPTED[0])
        count = len(writes)
        with self.assertRaises(M.AdapterStop): M.emit_fd1(b'abc')
        self.assertEqual(len(writes),count)
        self.assertEqual([fd for fd,raw in writes],[1,1])

    def test_body_fsync_failure_cannot_reissue_body(self):
        writes = []
        error = OSError('fsync')
        def sync(fd): raise error
        M.os = SimpleNamespace(write=lambda fd,raw:(writes.append((fd,raw)) or len(raw)),fsync=sync)
        with self.assertRaises(OSError): M.emit_fd1(b'abc')
        with self.assertRaises(M.AdapterStop): M.emit_fd1(b'abc')
        self.assertEqual(writes,[(1,b'abc')])

    def test_entry_clock_failure_retains_first_and_detail_without_body(self):
        # This failure occurs before source loading or native acquisition. Only
        # the new meter cleanup/projection code runs against ordinary fixtures.
        saved = (M.time,M.os,M.START[0],M.END[0],M.USED[0],M.ARMED[0],
                 M.BODY_ATTEMPTED[0],M.FIRST[0],M.SECONDARY[:],M.IO_UNKNOWN[0],M.SLOTS[:],M.plan_shape)
        original = RuntimeError('first clock failure')
        calls,writes = [],[]
        def clock():
            calls.append(True)
            if len(calls)==1: raise original
            return 42
        def write(fd,raw):
            writes.append((fd,raw)); return len(raw)
        try:
            M.time = SimpleNamespace(monotonic_ns=clock)
            M.os = SimpleNamespace(write=write,fsync=lambda fd: None)
            M.START[0],M.END[0],M.USED[0],M.ARMED[0] = None,None,False,False
            M.BODY_ATTEMPTED[0] = False
            M.FIRST[0],M.IO_UNKNOWN[0] = None,False
            M.SECONDARY[:] = [None]*32
            M.SLOTS[:] = [[None,'FREE',None,False] for unused in range(32)]
            result = M._run({},'normal','INITIALIZE','PUBLISHER')
            self.assertEqual(result,78)
            self.assertIs(M.FIRST[0],original)
            self.assertTrue(M.USED[0])
            self.assertFalse(M.BODY_ATTEMPTED[0])
            self.assertFalse(any(fd==1 for fd,raw in writes))
            detail = M.strict_json(b''.join(raw for fd,raw in writes if fd==2))
            self.assertEqual(detail['status'],'STOP')
            self.assertEqual(detail['errors_after_BODY']['first']['type'],'RuntimeError')
            self.assertFalse(detail['cleanup_known'])
            self.assertFalse(detail['execution_permission'])
            self.assertIsNone(detail['meter_start_pin'])
            self.assertEqual(len(calls),2)
            reached = []
            def forbidden_replay_preparation(*args):
                reached.append(True)
                raise AssertionError('replay reached plan/source preparation')
            M.plan_shape = forbidden_replay_preparation
            replay = M._run({},'normal','INITIALIZE','PUBLISHER')
            self.assertEqual(replay,78)
            self.assertTrue(M.USED[0])
            self.assertIs(M.FIRST[0],original)
            self.assertEqual(reached,[])
            self.assertFalse(M.BODY_ATTEMPTED[0])
            self.assertFalse(any(fd==1 for fd,raw in writes))
        finally:
            (M.time,M.os,M.START[0],M.END[0],M.USED[0],M.ARMED[0],
             M.BODY_ATTEMPTED[0],M.FIRST[0],secondary,M.IO_UNKNOWN[0],slots,M.plan_shape) = saved
            M.SECONDARY[:] = secondary
            M.SLOTS[:] = slots

    def test_loader_rejects_forged_modules_before_any_native_port(self):
        fake = SimpleNamespace(C=object(),F=object(),A=object())
        with self.assertRaises(L.AdapterStop):
            L.open_manual_owner(fake,'PUBLISHER',approved_opening=None,
                expected_head_pin=None,approved_manual_entry=None)

    def test_binding_keeps_old_financial_head_and_new_candidate_opening_separate(self):
        old_head,new_head,new_opening = {'sha256':'old'},{'sha256':'new'},{'sha256':'opening'}
        operation = {'attempt_id':'Own','command_pin':{'sha256':'command'},
            'reservation_pin':{'path':'reservation'},'phase_release_sha256':None,
            'predecessor_snapshot':{'head_pin':old_head}}
        reservation = {'body_reservation_ns':100,'policy_adoption_pin':{'sha256':'policy'},
            'before_closed_state_pin':{'sha256':'old-state'}}
        binding = M._binding(SimpleNamespace(ROUND_ID='round'),operation,
            {'head_pin':new_head,'opening_pin':new_opening},{'path':'start'},
            {'path':'pending'},reservation,{})
        self.assertEqual(binding['financial_head_pin'],old_head)
        self.assertEqual(binding['financial_opening_pin'],new_opening)
        self.assertNotEqual(binding['financial_head_pin'],new_head)

    def test_loader_manual_ports_exclude_payload_and_duplicate_prepare(self):
        source = (HERE/'manual_loader_v1.py').read_text()
        start = source.index('def manual_call(')
        end = source.index('def release_manual_once(',start)
        port = source[start:end]
        self.assertNotIn("'begin'",port)
        self.assertNotIn("'native_lease_for_controller'",port)
        self.assertNotIn("'current_binding'",port)
        meter = (HERE/'manual_meter_v1.py').read_text()
        self.assertNotIn("manual_call(loaded,ctx,'prepare_metadata_close'",meter)
        self.assertNotIn('actual_context_ports(',meter)


if __name__=='__main__': unittest.main()
