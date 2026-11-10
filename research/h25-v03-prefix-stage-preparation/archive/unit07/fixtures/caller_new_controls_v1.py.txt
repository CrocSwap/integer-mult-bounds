"""Unit07 NEW-only caller controls. Author worker alone executes this file.

Only the accepted NEW T0 support prefix and explicitly named NEW caller helpers
are compiled. Original source_packet/RootProxy/main and all project modules stay
inert. Original supervisor bytes are used only as hash-checked fixture DATA.
Owned temporary stages and fake dispatch/short-I/O services grant no capability.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest

UNIT=Path(__file__).resolve().parents[1]
F=UNIT.parent
CALLER=UNIT/'implementation/run_queue4_prefix_v2.py'
RAW=CALLER.read_bytes()
MARKER=b'# UNIT06_T0_SUPPORT_END\n'
PREFIX=RAW[:RAW.index(MARKER)+len(MARKER)]
BLOCKED={'parent_domain_v1','parent_closure_v1','parent_completion_v1',
         'h25_parent_supervisor','epoch_schema_v5','epoch_copy_v5',
         'v03_prefix_supervisor_v1','v03_prefix_derivation_v1',
         'v03_integrated_constructor_v2','predecessor_entry'}
NEW_FUNCTIONS={'_caller_simple','_caller_pin','_caller_inventory','_caller_stage',
               '_caller_case','_caller_source_packet'}
CONSTANTS={'CALLER_QUEUE_SHA','CALLER_RUNNER_SHA','CALLER_SUPERVISOR_SHA',
           'CALLER_STAGE_KEYS','CALLER_FALSE_FIELDS'}


def sha(raw):return hashlib.sha256(raw).hexdigest()


def module():
    if BLOCKED & set(sys.modules):raise RuntimeError('original runtime module present')
    if len(PREFIX)!=9878 or sha(PREFIX)!='48bc4009acb7569fb4a2ac529bec928a3aafdedc017a0ebaae97f72b7c97eabe':
        raise RuntimeError('accepted new support prefix differs')
    m=types.ModuleType('unit07_new_caller_fixture')
    m.__file__=str(CALLER)
    exec(compile(PREFIX,'<accepted-new-T0-support-only>','exec'),m.__dict__)
    tree=ast.parse(RAW)
    functions=[node for node in tree.body if type(node) is ast.FunctionDef and node.name in NEW_FUNCTIONS]
    if {node.name for node in functions}!=NEW_FUNCTIONS:raise RuntimeError('new helper extraction incomplete')
    exec(compile(ast.Module(body=functions,type_ignores=[]),'<new-caller-functions-only>','exec'),m.__dict__)
    for node in tree.body:
        if type(node) is ast.Assign and len(node.targets)==1 and type(node.targets[0]) is ast.Name and node.targets[0].id in CONSTANTS:
            m.__dict__[node.targets[0].id]=ast.literal_eval(node.value)
    return m


def file(path,raw,mode=0o444):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw);path.chmod(mode)
    return path


def pin(m,path,raw):
    # Fixture's expected contents are independently literal; observed metadata is
    # only this owned fixture's installed identity, never a runtime admission.
    return {'path':str(path),'sha256':sha(raw),'bytes':len(raw),
            'identity':m.identity(path.stat(follow_symlinks=False))}


def io_shim(read=None,write=None,close=None):
    names=('stat','fstat','open','fchmod','fsync','O_RDONLY','O_NOFOLLOW',
           'O_NONBLOCK','O_CLOEXEC','O_WRONLY','O_CREAT','O_EXCL')
    data={name:getattr(os,name) for name in names}
    data.update(read=os.read if read is None else read,
                write=os.write if write is None else write,
                close=os.close if close is None else close)
    return types.SimpleNamespace(**data)


class CallerNewControls(unittest.TestCase):
    def tearDown(self):
        self.assertFalse(BLOCKED & set(sys.modules))

    def test_exact_prefix_only_delta_and_old_unit_unchanged(self):
        old=(F/'unit06/implementation/run_queue4_prefix_v1.py').read_bytes()
        entry=(F/'unit06/implementation/predecessor_entry.py').read_bytes()
        self.assertEqual(sha(old),'90a7ed4a45b94e16fa313623e56f6f3efcd85f3ea40355a43b289d8c49a75825')
        self.assertEqual(sha(entry),'b783c6812a6295069456cfb4187d4e09bb7acbcb20fffd76e0c10267f90c1201')
        self.assertEqual(len(RAW),34716)
        self.assertEqual(sha(RAW),'25138c2c998762649c6a61cb8a6ae8aacd81bd533591b082ab6f58def712fca2')
        self.assertEqual(RAW[9878:],old[9574:])
        self.assertEqual(PREFIX,entry[:9878])

    def test_read_at_8192_short_returns_can_complete(self):
        m=module();calls=[]
        def reading(fd,count):calls.append(count);return os.read(fd,min(1,count))
        m.os=io_shim(read=reading)
        with tempfile.TemporaryDirectory(prefix='u7-caller-') as directory:
            raw=b'x'*8192;p=file(Path(directory)/'input',raw);owner=m.Owner()
            actual,retained=m.retained_read(str(p),sha(raw),len(raw),owner)
            self.assertEqual(retained,raw)
            self.assertEqual((len(calls),owner.read_calls,owner.captures[-1]['read_calls']),(8192,8192,8192))
            self.assertFalse(owner.quarantined)
            self.assertEqual(owner.fd_slots,[None])

    def test_8193rd_short_read_is_prevented_and_close_secondary_retained(self):
        m=module();calls=[];closed=[];secondary=RuntimeError('NEW fixture close B')
        def reading(fd,count):calls.append(count);return os.read(fd,min(1,count))
        def closing(fd):closed.append(fd);os.close(fd);raise secondary
        m.os=io_shim(read=reading,close=closing)
        with tempfile.TemporaryDirectory(prefix='u7-caller-') as directory:
            raw=b'x'*8193;p=file(Path(directory)/'input',raw);owner=m.Owner()
            with self.assertRaises(m.Stop) as caught:m.retained_read(str(p),sha(raw),len(raw),owner)
            self.assertEqual(str(caught.exception),'read call bound')
            self.assertIs(owner.primary,caught.exception)
            self.assertIs(owner.secondary[0],secondary)
            self.assertEqual((len(calls),owner.read_calls,len(closed)),(8192,8192,1))
            self.assertEqual(owner.total_bytes,8192)
            self.assertEqual(owner.fd_slots,[None])
            self.assertTrue(owner.quarantined)

    def test_record_4097th_short_write_is_prevented(self):
        m=module();calls=[]
        def writing(fd,raw):calls.append(len(raw));return os.write(fd,raw[:1])
        m.os=io_shim(write=writing)
        with tempfile.TemporaryDirectory(prefix='u7-caller-') as directory:
            p=Path(directory)/'partial-record';owner=m.Owner()
            with self.assertRaises(m.Stop) as caught:m.write_exclusive(str(p),b'x'*4097,0o444,owner)
            self.assertEqual(str(caught.exception),'write call bound')
            self.assertIs(owner.primary,caught.exception)
            self.assertEqual((len(calls),owner.write_calls,p.stat().st_size),(4096,4096,4096))
            self.assertEqual(owner.fd_slots,[None])

    def test_large_file_8193rd_short_write_is_prevented(self):
        m=module();calls=[]
        def writing(fd,raw):calls.append(len(raw));return os.write(fd,raw[:1])
        m.os=io_shim(write=writing)
        with tempfile.TemporaryDirectory(prefix='u7-caller-') as directory:
            p=Path(directory)/'partial-file';owner=m.Owner()
            with self.assertRaises(m.Stop) as caught:m.write_exclusive(str(p),b'x'*(m.RECORD_CAP+1),0o444,owner)
            self.assertEqual(str(caught.exception),'write call bound')
            self.assertIs(owner.primary,caught.exception)
            self.assertEqual((len(calls),owner.write_calls,p.stat().st_size),(8192,8192,8192))
            self.assertEqual(owner.fd_slots,[None])

    def test_prior_digest_refuses_changed_bytes_and_retains_actual_raw(self):
        m=module()
        with tempfile.TemporaryDirectory(prefix='u7-caller-') as directory:
            expected=b'{"independent":"expected"}\n';actual=b'{"changed":"actual"}\n'
            p=file(Path(directory)/'selection',actual);owner=m.Owner()
            with self.assertRaises(m.Stop):m.retained_read(str(p),sha(expected),m.RECORD_CAP,owner)
            self.assertEqual(owner.captures[0]['raw'],actual)
            self.assertTrue(owner.quarantined)

    def test_real_owned_inventory_and_negative_file_changes(self):
        for fault in ('none','extra','missing','mode','symlink','nested'):
            with self.subTest(fault=fault),tempfile.TemporaryDirectory(prefix='u7-caller-') as directory:
                m=module();stage=Path(directory)/'stage';stage.mkdir()
                raw=b'NEW owned inert input\n';p=file(stage/'input.txt',raw)
                file(stage/'STAGE.json',b'NEW outer manifest bytes\n')
                declared={'files':{'input.txt':{'sha256':sha(raw),'mode':0o444}}}
                if fault=='extra':file(stage/'extra.txt',b'NEW extra\n')
                if fault=='missing':p.unlink()
                if fault=='mode':p.chmod(0o400)
                if fault=='symlink':(stage/'alias').symlink_to(p)
                if fault=='nested':file(stage/'nested/STAGE.json',b'NEW excluded without priorpin\n')
                owner=m.Owner();state={'directory_scans':[],'inventory_observations':[]}
                if fault=='none':self.assertEqual(m._caller_inventory(stage,declared,[],owner,state),declared['files'])
                else:
                    with self.assertRaises(m.Stop):m._caller_inventory(stage,declared,[],owner,state)
                self.assertTrue(all(row['handle'] is None and row['closed'] for row in state['directory_scans']))

    def test_nested_excluded_manifest_requires_exact_prior_blob(self):
        for changed in (False,True):
            with self.subTest(changed=changed),tempfile.TemporaryDirectory(prefix='u7-caller-') as directory:
                m=module();stage=Path(directory)/'stage';stage.mkdir()
                raw=b'NEW input';file(stage/'input',raw);file(stage/'STAGE.json',b'outer')
                nested_raw=b'NEW excluded bytes';nested=file(stage/'nested/STAGE.json',nested_raw)
                expected=pin(m,nested,nested_raw)
                if changed:expected['sha256']='0'*64
                state={'directory_scans':[],'inventory_observations':[]};owner=m.Owner()
                declared={'files':{'input':{'sha256':sha(raw),'mode':0o444}}}
                if changed:
                    with self.assertRaises(m.Stop):m._caller_inventory(stage,declared,[expected],owner,state)
                else:self.assertEqual(m._caller_inventory(stage,declared,[expected],owner,state),declared['files'])

    def test_case_requires_actual_job_stage_and_all_five_false_fields(self):
        m=module();digest='a'*64
        stages={'stage':{'selection':{'manifest':{'sha256':digest}},'jobs':{'job':{'entry':'integration/predecessor_entry.py','lanes':'1','optimized':False,'finite_only':True}}}}
        case={'stage':'stage','stage_sha256':digest,'job':'job','label':'owned-fixture','science_status':'PREFIX_OBSERVATION_DATA','science_fields':{name:False for name in m.CALLER_FALSE_FIELDS}}
        m._caller_case(case,stages)
        for field in m.CALLER_FALSE_FIELDS:
            for missing in (False,True):
                with self.subTest(field=field,missing=missing):
                    changed=dict(case);changed['science_fields']=dict(case['science_fields'])
                    if missing:del changed['science_fields'][field]
                    else:changed['science_fields'][field]=True
                    with self.assertRaises(m.Stop):m._caller_case(changed,stages)
        for key,value in (('science_status','PASS'),('stage_sha256','b'*64),('job','missing')):
            changed=dict(case);changed[key]=value
            with self.assertRaises(m.Stop):m._caller_case(changed,stages)

    def test_new_packet_basename_and_original_supervisor_data_only(self):
        supervisor=(F/'unit06/prerequisites/h25_parent_supervisor.py.txt').read_bytes()
        self.assertEqual(sha(supervisor),'cfb09a18dd10b597cc6d5a8139ee769bef679bc44ae029329755e3d97b055075')
        for old_name_only in (False,True):
            with self.subTest(old_name_only=old_name_only),tempfile.TemporaryDirectory(prefix='u7-caller-') as directory:
                m=module();packet=Path(directory);own=b'# NEW inert fixture caller, never executed\n'
                actual_name='run_queue4_prefix_v2.py';selected_name='run_queue4_prefix_v1.py' if old_name_only else actual_name
                file(packet/actual_name,own);file(packet/'supervisor.py',supervisor)
                manifest={'files':{selected_name:{'sha256':sha(own),'bytes':len(own)},'supervisor.py':{'sha256':sha(supervisor),'bytes':len(supervisor)}}}
                raw=(json.dumps(manifest,sort_keys=True)+'\n').encode();path=file(packet/'SOURCE-READINESS.json',raw)
                m.__file__=str(packet/actual_name);selection={'source_packet':pin(m,path,raw)};owner=m.Owner()
                if old_name_only:
                    with self.assertRaises(m.Stop):m._caller_source_packet(selection,owner)
                    self.assertEqual(len(owner.captures),1)
                else:self.assertEqual(m._caller_source_packet(selection,owner),manifest)

    def test_new_dispatch_recheck_precedes_fake_base_and_failure_suppresses_it(self):
        cls=[node for node in ast.parse(RAW).body if type(node) is ast.ClassDef and node.name=='PriorAdmittedRootProxy']
        self.assertEqual(len(cls),1)
        for fail in (False,True):
            with self.subTest(fail=fail):
                m=module();events=[];error=RuntimeError('NEW fixture recheck A')
                class FakeBase:
                    def __init__(self):self.next=0;self.cases=[{'NEW':'fixture'}]
                    def run(self,command,**kwargs):events.append('fake-base');return 'NEW-FAKE-NOT-RUNTIME'
                def recheck(state,case):
                    events.append('new-recheck')
                    if fail:raise error
                m.RootProxy=FakeBase;m._caller_recheck=recheck;m._CALLER_ADMISSION=object()
                exec(compile(ast.Module(body=cls,type_ignores=[]),'<NEW-dispatch-with-fake-base>','exec'),m.__dict__)
                proxy=m.PriorAdmittedRootProxy()
                if fail:
                    with self.assertRaises(RuntimeError) as caught:proxy.run(['NEW-FAKE-NO-EXEC'])
                    self.assertIs(caught.exception,error)
                    self.assertEqual(events,['new-recheck'])
                else:
                    self.assertEqual(proxy.run(['NEW-FAKE-NO-EXEC']),'NEW-FAKE-NOT-RUNTIME')
                    self.assertEqual(events,['new-recheck','fake-base'])


if __name__=='__main__':unittest.main(verbosity=2)
