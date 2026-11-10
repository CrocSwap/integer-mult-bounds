"""Finite pure-driver controls; no original C2/F4/A4 module is imported.

The literals below are classifier/postcondition inputs, not claimed F4 snapshots
or native EX observations. Only the new driver definitions are loaded. Native
profile, nofollow/EX/birth/FD facts and cleanup require actual later evidence.
"""
import copy
import errno
import importlib.util
from pathlib import Path
import unittest


ROUND = Path(__file__).resolve().parents[2]
SOURCE = ROUND / 'implementation/manual_provider_driver_v1.py'
spec = importlib.util.spec_from_file_location('new_bootstrap_driver_control_subject', SOURCE)
D = importlib.util.module_from_spec(spec)
spec.loader.exec_module(D)
W = '/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453'
H = W + '/outputs/h25-data-handling-20261028'
FIN = H + '/control/prospective-financial-v1'


def head_pin(letter='a'):
    return dict(path=FIN + '/HEAD.json', bytes=211, sha256=letter * 64, mode=0o600)


def presence(value='PRESENT', **changes):
    result = dict(presence=value, canonical_ancestors=True,
                  paired_namespace=True, real_ex_verified=True)
    result.update(changes)
    return result


def snapshot_literals():
    # Deliberately no fabricated source/Tool/OS proof. The actual native path must
    # run original F4 validation before these new postconditions may be used.
    pin = head_pin()
    snapshot = dict(schema='fresh-financial-snapshot-v1', head_pin=copy.deepcopy(pin))
    evidence = dict(head_pin=copy.deepcopy(pin), pending=[], unknown=[], blockers=[],
                    entries={}, encumbered_policy_ns=6_980_533_479,
                    closed_policy_ns=6_980_533_479)
    return snapshot, evidence, pin


class HeadClassificationControls(unittest.TestCase):
    def test_literal_present_requires_all_three_native_fact_postconditions(self):
        self.assertEqual(D.classify_head_fact(presence()), 'PRESENT')
        for field in ('canonical_ancestors', 'paired_namespace', 'real_ex_verified'):
            with self.subTest(field=field):
                self.assertEqual(D.classify_head_fact(presence(**{field:False})), 'STOP_UNCERTAIN')

    def test_clean_exact_absence_is_negative_not_positive_or_genesis_grant(self):
        self.assertEqual(D.classify_head_fact(presence('ENOENT')), 'HEAD_ABSENT')

    def test_absence_without_canonical_paired_lease_facts_stops(self):
        for field in ('canonical_ancestors', 'paired_namespace', 'real_ex_verified'):
            with self.subTest(field=field):
                self.assertEqual(D.classify_head_fact(presence('ENOENT', **{field:False})), 'STOP_UNCERTAIN')

    def test_permission_link_nondirectory_and_other_error_are_not_absence(self):
        for error in (errno.EACCES, errno.EPERM, errno.ELOOP, errno.ENOTDIR, errno.EIO):
            with self.subTest(error=error):
                self.assertEqual(D.errno_presence(error), 'ERROR')
                self.assertEqual(D.classify_head_fact(presence(D.errno_presence(error))), 'STOP_UNCERTAIN')
        self.assertEqual(D.errno_presence(errno.ENOENT), 'ENOENT')

    def test_errno_lookalikes_cannot_create_clean_absence(self):
        for value in (True, False, str(errno.ENOENT), float(errno.ENOENT), None):
            with self.subTest(value=value):self.assertEqual(D.errno_presence(value), 'ERROR')

    def test_unknown_presence_and_lookalike_boolean_do_not_pass(self):
        with self.assertRaises(D.DriverStop):D.classify_head_fact(presence('MISSING'))
        for field in ('canonical_ancestors', 'paired_namespace', 'real_ex_verified'):
            with self.subTest(field=field):
                with self.assertRaises(D.DriverStop):D.classify_head_fact(presence(**{field:1}))

    def test_extra_authority_or_resume_fields_are_rejected(self):
        bad=presence();bad['approved']=True
        with self.assertRaises(D.DriverStop):D.classify_head_fact(bad)


class SnapshotPostconditionControls(unittest.TestCase):
    def test_literal_current_closed_predecessor_postcondition(self):
        snapshot,evidence,pin=snapshot_literals()
        self.assertEqual(D.validate_snapshot_data(snapshot,evidence,pin), 'VALID_CLOSED_PREDECESSOR')

    def test_stale_snapshot_head_does_not_match_the_original_read(self):
        snapshot,evidence,pin=snapshot_literals();snapshot['head_pin']=head_pin('b')
        with self.assertRaises(D.DriverStop):D.validate_snapshot_data(snapshot,evidence,pin)

    def test_evidence_head_must_match_the_same_current_snapshot(self):
        snapshot,evidence,pin=snapshot_literals();evidence['head_pin']=head_pin('b')
        with self.assertRaises(D.DriverStop):D.validate_snapshot_data(snapshot,evidence,pin)

    def test_history_view_is_not_current_even_if_expected_pin_appears(self):
        snapshot,evidence,pin=snapshot_literals()
        historical=dict(schema='fresh-financial-history-view-v1',head_pin=pin,complete_snapshot=snapshot)
        with self.assertRaises(D.DriverStop):D.validate_snapshot_data(historical,evidence,pin)

    def test_malformed_or_incomplete_snapshot_postcondition_stops(self):
        snapshot,evidence,pin=snapshot_literals()
        for bad in (None, {}, {'schema':'invented','head_pin':pin},
                    {'schema':'fresh-financial-snapshot-v1'}):
            with self.subTest(snapshot=bad):
                with self.assertRaises(D.DriverStop):D.validate_snapshot_data(bad,evidence,pin)

    def test_pending_unknown_and_blockers_each_stop_without_filtering(self):
        for key in ('pending','unknown','blockers'):
            snapshot,evidence,pin=snapshot_literals();evidence[key]=['retained-own-debt']
            before=copy.deepcopy(evidence)
            with self.subTest(key=key):
                with self.assertRaises(D.DriverStop):D.validate_snapshot_data(snapshot,evidence,pin)
                self.assertEqual(evidence,before)


class ReadDomainAndCapControls(unittest.TestCase):
    def test_source_fixed_current_metadata_and_legacy_descriptor_paths(self):
        for path in (FIN+'/HEAD.json', FIN+'/STATE-000000.json',
                     H+'/control/fresh-metered-round-v1/ACTIVE-HEAD.json',
                     H+'/areas/fresh-round-provenance-bridge-v1/OPENING.json'):
            with self.subTest(path=path):self.assertTrue(D.read_policy(path))

    def test_protected_and_unrelated_paths_are_refused(self):
        for path in (W+'/outputs/h25-bookkeeping-swarm-20261028/runtime/runs/run.json',
                     '/etc/passwd', H+'/runtime/runs/unrelated.json', '/tmp/predecessor.json',
                     FIN+'/../../runtime/runs/escape.json', 'HEAD.json'):
            with self.subTest(path=path):self.assertFalse(D.read_policy(path))

    def test_foreign_path_object_is_not_stringified(self):
        calls=[]
        class Hostile:
            def __str__(self):calls.append(True);raise AssertionError('foreign hook')
        self.assertFalse(D.read_policy(Hostile()))
        self.assertEqual(calls,[])

    def test_duplicate_same_bytes_does_not_consume_new_file_budget(self):
        budget=D.ReadBudget()
        for unused in range(4100):budget.add(FIN+'/HEAD.json',b'{}\n')
        with self.assertRaises(D.DriverStop):budget.add(FIN+'/HEAD.json',b'{"changed":1}\n')

    def test_per_record_cap_is_literal_131072_bytes(self):
        budget=D.ReadBudget();budget.add(FIN+'/record.json',b'x'*131072)
        with self.assertRaises(D.DriverStop):budget.add(FIN+'/oversize.json',b'x'*131073)

    def test_cumulative_byte_cap_is_literal_16_mib(self):
        budget=D.ReadBudget();block=b'x'*131072
        for ordinal in range(128):budget.add(FIN+'/f%04d.json'%ordinal,block)
        with self.assertRaises(D.DriverStop):budget.add(FIN+'/over-total.json',b'x')

    def test_file_cap_is_literal_4096_distinct_records(self):
        budget=D.ReadBudget()
        for ordinal in range(4096):budget.add(FIN+'/f%04d.json'%ordinal,b'x')
        with self.assertRaises(D.DriverStop):budget.add(FIN+'/file-4097.json',b'x')


class OneUseAndFailureControls(unittest.TestCase):
    def test_bootstrap_gate_is_one_use(self):
        gate=D.BootstrapGate();gate.enter('BOOTSTRAP')
        with self.assertRaises(D.DriverStop):gate.enter('BOOTSTRAP')

    def test_prepare_and_all_manual_dispatch_verbs_are_blocked(self):
        for verb in ('PREPARE','prepare','INITIALIZE','REFRESH','CLOSE','DISPATCH','dispatch'):
            with self.subTest(verb=verb):
                gate=D.BootstrapGate()
                with self.assertRaises(D.DriverStop):gate.enter(verb)
                with self.assertRaises(D.DriverStop):gate.enter('BOOTSTRAP')

    def test_saved_json_cannot_restore_a_gate_or_resume_a_lost_driver(self):
        with self.assertRaises(TypeError):D.BootstrapGate({'phase':'BOOTSTRAP','ordinal':1})
        gate=D.BootstrapGate()
        with self.assertRaises(D.DriverStop):gate.enter('RESUME')
        with self.assertRaises(D.DriverStop):gate.enter('BOOTSTRAP')

    def test_first_read_error_survives_distinct_close_failure(self):
        state=D.FailureState();first=OSError(errno.EIO,'read');cleanup=OSError(errno.EBADF,'close')
        self.assertIs(state.remember(first),first)
        state.close_failure(cleanup)
        self.assertIs(state.first,first)
        self.assertEqual(state.secondary,[cleanup])
        self.assertTrue(state.unknown)
        self.assertTrue(state.close_failed)

    def test_close_failure_alone_is_first_and_uncertain(self):
        state=D.FailureState();error=OSError(errno.EBADF,'close')
        state.close_failure(error)
        self.assertIs(state.first,error)
        self.assertTrue(state.unknown)
        self.assertTrue(state.close_failed)

    def test_duplicate_error_object_does_not_repeat_secondary(self):
        state=D.FailureState();first=RuntimeError('first');other=RuntimeError('other')
        state.remember(first);state.remember(first);state.remember(other);state.remember(other)
        self.assertEqual(state.secondary,[other])


if __name__=='__main__':
    unittest.main()
