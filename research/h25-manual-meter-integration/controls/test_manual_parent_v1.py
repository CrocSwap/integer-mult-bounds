"""New pure transition/selector fixtures; SOURCE ONLY until independent GO.

Only new source modules are loaded. No original F4/C2/A4 module, loader entry,
writer IO/custody method, native provider, target or financial runtime runs.
These cases prove necessary DATA gates, never genuine source/native custody.
Inherited writer readback/descriptor faults remain explicitly UNRUN.
"""
import copy
import importlib.util
from pathlib import Path
import shlex
import unittest

W=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
PACKAGE=Path(__file__).resolve().parents[1]


def new_module(name):
    # Both files are newly authored package source. Their top level defines
    # functions/state and performs no original source loading or filesystem IO.
    path=PACKAGE/'implementation'/(name+'.py')
    spec=importlib.util.spec_from_file_location('new_pure_control_'+name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


WRITER=new_module('original_records_v29')
PARENT=new_module('manual_parent_v1')


def literal_pin(name):
    return {'path':str(WRITER.R/'control'/name),'bytes':17,'sha256':'a'*64,'mode':0o444}


def literal_reserved():
    # Literal fixture, not a loaded source capability or claimed genuine record.
    return {'schema':'fresh-financial-entry-manifest-v1','attempt_id':'fixture-only',
            'command_pin':literal_pin('command.json'),
            'reservation_pin':literal_pin('reservation.json'),
            'pre_entry_pin':literal_pin('pre-entry.json'),
            'meter_start_pin':None,'meter_body_pin':None,'native_chain_pin':None,
            'financial_adjudication_pin':None,'settlement_route':'MANUAL_ONLY',
            'formal_start_pin':None,'formal_receipt_pin':None,'phase':'RESERVED'}


class StartedDataControls(unittest.TestCase):
    def setUp(self):
        self.previous=literal_reserved()
        self.start=literal_pin('START.json')
        self.next=copy.deepcopy(self.previous)
        self.next['meter_start_pin']=copy.deepcopy(self.start)
        self.next['phase']='STARTED'

    def check_transition(self,**overrides):
        args=dict(previous=self.previous,observed=self.next,start_pin=self.start,
                  version=1,last_phase='RESERVED',reconciled=False)
        args.update(overrides)
        return WRITER.started_successor_data(**args)

    def test_exact_transition_has_literal_expected_result(self):
        expected=literal_reserved()
        expected['meter_start_pin']=literal_pin('START.json')
        expected['phase']='STARTED'
        self.assertEqual(self.check_transition(),expected)

    def test_does_not_mutate_private_predecessor_or_received_start(self):
        before=copy.deepcopy(self.previous);start=copy.deepcopy(self.start)
        self.check_transition()
        self.assertEqual(self.previous,before)
        self.assertEqual(self.start,start)

    def test_every_other_manifest_field_rebind_rejects(self):
        for key in self.previous:
            if key in ('meter_start_pin','phase'):continue
            with self.subTest(field=key):
                wrong=copy.deepcopy(self.next)
                wrong[key]=None if wrong[key] is not None else literal_pin('replacement.json')
                with self.assertRaises(WRITER.WriterStop):
                    self.check_transition(observed=wrong)

    def test_wrong_start_pin_rejects(self):
        wrong=copy.deepcopy(self.next)
        wrong['meter_start_pin']=literal_pin('another-operation-start.json')
        with self.assertRaises(WRITER.WriterStop):self.check_transition(observed=wrong)

    def test_phase_skip_and_regression_reject(self):
        for phase in ('RESERVED','OBSERVED_AWAIT_REVIEW','CLOSED_KNOWN','OPEN_UNCERTAIN'):
            with self.subTest(phase=phase):
                wrong=copy.deepcopy(self.next);wrong['phase']=phase
                with self.assertRaises(WRITER.WriterStop):self.check_transition(observed=wrong)

    def test_missing_or_extra_manifest_field_reject(self):
        missing=copy.deepcopy(self.next);del missing['pre_entry_pin']
        extra=copy.deepcopy(self.next);extra['approval']=True
        for wrong in (missing,extra):
            with self.assertRaises(WRITER.WriterStop):self.check_transition(observed=wrong)

    def test_stale_future_and_bool_version_reject(self):
        for version in (0,2,127,True):
            with self.subTest(version=version):
                with self.assertRaises(WRITER.WriterStop):self.check_transition(version=version)

    def test_replay_and_wrong_private_phase_reject(self):
        with self.assertRaises(WRITER.WriterStop):self.check_transition(reconciled=True)
        with self.assertRaises(WRITER.WriterStop):self.check_transition(last_phase='STARTED')

    def test_non_reserved_private_predecessor_rejects(self):
        wrong=copy.deepcopy(self.previous);wrong['phase']='STARTED'
        with self.assertRaises(WRITER.WriterStop):self.check_transition(previous=wrong)

    def test_preexisting_start_rejects(self):
        wrong=copy.deepcopy(self.previous);wrong['meter_start_pin']=self.start
        with self.assertRaises(WRITER.WriterStop):self.check_transition(previous=wrong)

    def test_absent_received_start_is_not_an_authority(self):
        with self.assertRaises(WRITER.WriterStop):self.check_transition(start_pin=None)


class FixedCommandControls(unittest.TestCase):
    def test_source_subject_preserves_unchanged_financial_pin_namespace(self):
        self.assertEqual(PARENT.METER,WRITER.R/'areas/manual-integration-v29/manual_meter_v1.py')
        self.assertEqual(PARENT.LOADER,WRITER.R/'areas/manual-integration-v29/manual_loader_v1.py')

    def test_normal_optimized_have_exact_distinct_argv(self):
        common=[str(PARENT.METER),'CLOSE']
        for profile in ('normal','optimized'):
            with self.subTest(profile=profile):
                command=PARENT.exact_manual_command('CLOSE',profile,'fixture-only')
                self.assertEqual(command.splitlines()[:2],['umask 077','set -C'])
                self.assertEqual(len(command.splitlines()),3)
                self.assertTrue(command.splitlines()[2].startswith('exec /usr/bin/env -i '))
                args=shlex.split(command)
                prefix=['/usr/bin/python3.12','-S','-s','-P','-B']
                if profile=='optimized':prefix+=['-O']
                envelope=['umask','077','set','-C','exec','/usr/bin/env','-i',
                          'PATH=/usr/bin:/bin','PYTHONHASHSEED=0','LANG=C.UTF-8',
                          'LC_ALL=C.UTF-8','TZ=UTC','PYTHONDONTWRITEBYTECODE=1']
                body=PARENT.R/'control/prospective-financial-v1/entries/fixture-only/METER_BODY.json'
                detail=PARENT.PLAN_ROOT/'fixture-only.stderr.json'
                expected=envelope+prefix+common+[profile,str(PARENT.PLAN_ROOT/'fixture-only.json'),
                    PARENT.METER_PIN['sha256'],str(PARENT.METER_PIN['bytes']),
                    '>',str(body),'2>',str(detail)]
                self.assertEqual(args,expected)

    def test_role_action_is_literal_and_cannot_reach_payload(self):
        for bad in ('PAYLOAD_PRELUDE','CONTROLLER','PUBLISHER','begin','',None):
            with self.subTest(action=bad):
                with self.assertRaises(PARENT.ParentStop):
                    PARENT.exact_manual_command(bad,'normal','fixture-only')

    def test_invalid_profile_and_path_injection_reject(self):
        for profile in ('-OO','isolated','normal; echo anything',None):
            with self.assertRaises(PARENT.ParentStop):
                PARENT.exact_manual_command('INITIALIZE',profile,'fixture-only')
        for attempt in ('../other','bad;command','x/y','x\nnext',''):
            with self.assertRaises(PARENT.ParentStop):
                PARENT.exact_manual_command('REFRESH','normal',attempt)

    def test_plan_hash_cycle_is_absent(self):
        args=shlex.split(PARENT.exact_manual_command('INITIALIZE','normal','fixture-only'))
        # Path, source SHA and source length are the three terminal arguments;
        # no hash of PLAN containing COMMAND/PRE_ENTRY is required.
        self.assertEqual(args[-7:-4], [str(PARENT.PLAN_ROOT/'fixture-only.json'),
                                      PARENT.METER_PIN['sha256'],str(PARENT.METER_PIN['bytes'])])
        self.assertEqual(args[-4],'>')
        self.assertEqual(args[-2],'2>')


if __name__=='__main__':unittest.main()
