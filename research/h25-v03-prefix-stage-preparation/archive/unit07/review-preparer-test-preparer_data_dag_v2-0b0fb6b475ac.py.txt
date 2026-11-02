"""Actual NEW preparation on explicit inert fixture data, never original bodies.

The selected fixture pins below replace only this isolated NEW module's literal
expectations, with mock.patch restoration. They do not impersonate genuine
C05/source/native/funding admissions. This tests actual filesystem/metadata ops.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'implementation'/'prepare_prefix_stage_v2.py'
spec=importlib.util.spec_from_file_location('unit07_preparer_fixture_dag',SOURCE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def rawfile(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);path.chmod(0o444)
    return {'path':str(path),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'identity':m.identity(path.stat())}


def fixture(root):
    for sub in ('R/control','R/stages','R/runtime','inputs'): (root/sub).mkdir(parents=True,exist_ok=True)
    r=root/'R';inputs=root/'inputs';sc=root/'Sc';(sc/'integration').mkdir(parents=True)
    for name in ('parent-queue.lock','science.lock'):rawfile(r/'runtime'/name,b'')
    entry=rawfile(inputs/'predecessor_entry.py',b'# NEW fixture entry DATA only\n')
    caller=rawfile(inputs/'run_queue4_prefix_v2.py',b'# NEW fixture caller DATA only\n')
    supervisor=rawfile(inputs/'supervisor.py',b'# NEW fixture supervisor DATA only\n')
    tcb=rawfile(inputs/'TCB.json',b'{"fixture_only":true}\n')
    runner=rawfile(r/'run_guarded_v3.py',b'# NEW fixture runner DATA only\n')
    original=rawfile(inputs/'variant.py.txt',b'# INERT FIXTURE ONLY\n'+b' '* (41337-len(b'# INERT FIXTURE ONLY\n')))
    receivers={name:rawfile(inputs/(name+'.py.txt'),('# INERT NEW FIXTURE '+name+'\n').encode()) for name in m.PROJECT_PINS}
    childroot=rawfile(sc/'integration/full_driver.py',b'# INERT ROOT FIXTURE\n'+b' '*(38851-len(b'# INERT ROOT FIXTURE\n')))
    provider=rawfile(sc/'integration/probe_binding_v3.py',b'# INERT PROVIDER FIXTURE\n')
    driver=rawfile(sc/'integration/v03_control_driver_v1.py',b'# INERT CONFIGURED DRIVER FIXTURE\n')
    gate=rawfile(sc/'integration/GATE-VALUES.json',b'{"fixture_only":true}\n')
    childfiles=[childroot,provider,driver,gate]
    declared={'files':{pin['path'][len(str(sc))+1:]:{'sha256':pin['sha256'],'mode':pin['identity']['mode']&0o7777} for pin in childfiles},'runner_sha256':runner['sha256']}
    manifest=rawfile(sc/'STAGE.json',m.canonical(declared))
    base=[m.source_row(pin,category) for pin,category in ((childroot,'root'),(provider,'provider'),(driver,'driver'),(gate,'project'),(manifest,'stage'))]
    for category in ('parent','system_headers','compiler_link','oracle'):
        base.append(m.source_row(rawfile(inputs/(category+'.data'),('owned fixture '+category).encode()),category))
    (sc/'integration').chmod(0o555);sc.chmod(0o555)
    admissions={name:{field:'a'*64 for field in fields} for name,fields in m.GATE_FIELDS.items()}
    request={'schema':'unit07-prefix-preparation-v1','canonical_root':str(r),'queue':'fixturequeue','stage':'fixture-stage','job':'fixturejob','label':'fixture-label','mode':'normal','lanes':'fixturelane','finite_only':True,'entry_source':entry,'receiver_sources':receivers,'caller_source':caller,'supervisor_source':supervisor,'native_tcb_source':tcb,'runner_source':runner,'original_variant':original,'child':{'stage_directory':str(sc),'stage_manifest':manifest,'stage_directories':['integration'],'root_source':childroot,'driver_source':driver,'gate_values':gate,'expectation':{'outcome':'PREFIX_RETURN','exception_type':None,'message':None,'terminal_function':None,'v03_discriminator':False,'compiler_launches':0,'candidate_image_loads':0,'complete_raw_and_owned_terminal_required':True},'id':'fixture-case','generation':'fixture-generation','launch_nonce':'b'*64,'root_seconds':10,'address_space_bytes':1024,'rss_bytes':1024},'parent_source_rows':base,'admissions':admissions,'session_seconds':20,'source_closure_admission_sha256':'c'*64,'outer_policy':{'shared_seconds':60,'root_seconds':30,'root_address_space_bytes':2048,'root_rss_sum_bytes':2048}}
    constants={'CALLER_PIN':(caller['sha256'],caller['bytes']),'ENTRY_PIN':(entry['sha256'],entry['bytes']),'SUPERVISOR_PIN':(supervisor['sha256'],supervisor['bytes']),'TCB_PIN':(tcb['sha256'],tcb['bytes']),'RUNNER_PIN':(runner['sha256'],runner['bytes']),'VARIANT_SHA':original['sha256'],'ROOT_SHA':childroot['sha256'],'PROVIDER_SHA':provider['sha256'],'PROJECT_PINS':{name:(pin['sha256'],pin['bytes']) for name,pin in receivers.items()}}
    return request,constants


class DataDag(unittest.TestCase):
    def test_actual_inert_fixture_preparation_acyclic_and_no_runtime_admission(self):
        with tempfile.TemporaryDirectory(prefix='unit07-full-owned-fixture-') as temporary:
            root=Path(temporary);request,constants=fixture(root)
            production_pins=m.PROJECT_PINS
            try:
                with patch.multiple(m,**constants):result=m.prepare_prefix_stage(request)
                self.assertIs(m.PROJECT_PINS,production_pins)
                owner=m.PREPARATIONS[-1];self.assertIsNone(owner.primary);self.assertTrue(owner.cleanup_done)
                self.assertTrue(all(fd is None for fd in owner.fd_slots))
                for field in m.FALSE_FIELDS:self.assertIs(result[field],False)
                self.assertFalse(result['source_admission']);self.assertFalse(result['c07_interval_proved'])
                self.assertFalse(result['funding_admission']);self.assertTrue(result['requires_independent_approval'])
                read=lambda pin:json.loads(Path(pin['path']).read_bytes())
                p=read(result['receiver_policy']);q=read(result['outer_plan']);selection=read(result['selection']);stage=read(result['stage']);bootstrap=read(result['bootstrap']);packet=read(result['source_packet'])
                self.assertEqual(set(p),set(production_pins));self.assertEqual(bootstrap['outer_plan'],result['outer_plan'])
                self.assertEqual(selection['stages'][0]['manifest'],result['stage'])
                self.assertEqual(selection['stages'][0]['bootstrap'],result['bootstrap'])
                self.assertEqual(selection['source_packet'],result['source_packet'])
                self.assertEqual(set(packet['files']),{'run_queue4_prefix_v2.py','supervisor.py'})
                qpaths={row['path'] for row in q['source_files']}
                for excluded in (result['outer_plan'],result['bootstrap'],result['stage']):self.assertNotIn(excluded['path'],qpaths)
                self.assertEqual({row['category'] for row in q['source_files']},m.SOURCE_CATEGORIES)
                self.assertEqual(q['case']['output'],q['session_directory']+'/producer-output')
                self.assertEqual(q['round_root'],result['private_root'])
                self.assertFalse(Path(q['session_directory']).exists())
                self.assertFalse((root/'R/runtime/runs').exists())
                self.assertIn('integration/PREFIX-BOOTSTRAP.json',stage['files'])
                self.assertIn('data/PREFIX-PLAN.json',stage['files']);self.assertNotIn('STAGE.json',stage['files'])
                self.assertEqual(owner.copy_attempts,20)
                privatepairs={(p['identity']['device'],p['identity']['inode']) for p in bootstrap['private_locks']}
                canonicalpairs={(s.st_dev,s.st_ino) for s in ((root/'R/runtime/parent-queue.lock').stat(),(root/'R/runtime/science.lock').stat())}
                self.assertEqual(len(privatepairs),2);self.assertFalse(privatepairs&canonicalpairs)
                self.assertEqual((root/'R/runtime/parent-queue.lock').read_bytes(),b'')
                self.assertEqual((root/'R/runtime/science.lock').read_bytes(),b'')
                self.assertEqual(result['operation_bill']['final_fit'],'OPEN_NOT_ZERO')
                self.assertTrue(result['operation_bill']['cleanup_consumed']);self.assertEqual(result['operation_bill']['remaining_known_fd_slots'],0)
                self.assertEqual(result['operation_bill']['io_attempts']['close'],len(owner.close_records))
                self.assertEqual(result['operation_bill']['final_tail_cost'],'OPEN_NOT_ZERO')
                self.assertGreater(result['operation_bill']['read_calls'],0);self.assertGreater(result['operation_bill']['write_calls'],0)
            finally:
                # Only owned fixture dirs; mode restoration enables TemporaryDirectory cleanup.
                for path in sorted(root.rglob('*'),key=lambda p:len(p.parts),reverse=True):
                    if path.is_dir():path.chmod(0o700)
                root.chmod(0o700)

if __name__=='__main__':unittest.main(verbosity=2)
