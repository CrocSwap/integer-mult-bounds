"""Standalone changed-boundary fixtures, not original caller/native admission.

The new production modules and private qualification body execute unchanged.
Context/association/schema/funding ports here are explicitly inert fixtures.
Real owned R -> GNU-time -> waiting-entry generations and a query subtree use
actual pidfds. No original scientific driver, compiler, native view entry or
property observer runs. The terminal child is the installed /usr/bin/false.
"""
import ast
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import tempfile
import time
import types
import unittest
from contextlib import contextmanager

@contextmanager
def retained_directory(*args,**kwargs):
    yield tempfile.mkdtemp(*args,**kwargs)

D=Path(__file__).resolve().parents[1]
SOURCE=D/'implementation/source'
ENV={'PATH':'/usr/bin:/bin','PYTHONHASHSEED':'0','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
FLAGS=['-S','-s','-P','-B']

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
S=module('fixture_subject_supervisor',SOURCE/'fresh_supervisor.py')
B=module('fixture_subject_relay',SOURCE/'bounded_relay.py')

def sha(raw): return hashlib.sha256(raw).hexdigest()
def pin(path):
    raw=Path(path).read_bytes();return {'path':str(path),'bytes':len(raw),'sha256':sha(raw),'mode':0o444}
def frozen(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,sort_keys=True)+'\n');path.chmod(0o444);return pin(path)

def private_function(name,env):
    tree=ast.parse((SOURCE/'fresh_supervisor.py').read_text());owner=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='bind_active_run_root')
    node=next(n for n in owner.body if isinstance(n,ast.FunctionDef) and n.name==name)
    ns=dict(vars(S));ns.update(env);exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(SOURCE/'fresh_supervisor.py'),'exec'),ns);return ns[name]

class Registry:
    def __init__(self,attempt): self.a=attempt;self.errors=[]
    def attempt(self,label): assert label==self.a.label;return self.a
    def capture_error(self,a,error):
        if a.error is None:a.error=error
        self.errors.append(error)
    def mark_uncertain(self,a,message):a.uncertain.append(message)
    def synchronous_writer(self,a,role,path):
        r={'attempt':a,'kind':'writer-permit','role':role,'path':path,'state':'OWNED','primary':None};a.resources.append(r);return r
    def required_writer_closed(self,a,role):assert a.required[role] is False;a.required[role]=True
    def fd_pending(self,a,role):
        r={'attempt':a,'kind':'fd','role':role,'object':None,'state':'PENDING'};a.resources.append(r);return r
    def fd_acquired(self,r,fd):r.update(object=fd,state='OWNED')
    def fd_not_entered(self,r):r['state']='NOT_ENTERED'
    def fd_unknown(self,r,error):r.update(state='UNKNOWN',primary=error);self.errors.append(error)
    def fd_close(self,r):
        fd=r['object'];r.update(object=None,state='CLOSING')
        try:os.close(fd)
        except BaseException as error:r.update(state='UNKNOWN',secondary=error);raise
        r['state']='CLOSED'
    def poll_root(self,p):return p.poll()

class FixtureIO:
    def __init__(self,fail_path=None):self.fail_path=fail_path;self.primary=OSError('deliberate retained readback failure');self.events=[];self.slots=[]
    def call(self,operation,path,*args,**kw):
        self.events.append((operation,str(path) if isinstance(path,Path) else 'fd'))
        if operation=='write':
            raw=(json.dumps(args[0],sort_keys=True,separators=(',',':'))+'\n').encode();fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            try:
                view=memoryview(raw)
                while view:n=os.write(fd,view);view=view[n:]
                os.fsync(fd)
            finally:os.close(fd)
            return {'path':str(path),'bytes':len(raw),'sha256':sha(raw),'identity':S.identity(path.stat())}
        if operation=='acquire':
            slot=[os.open(path,args[0]),'OWNED'];self.slots.append(slot);return slot
        if operation=='close':
            slot=path;fd=slot[0];slot[:]=[None,'CLOSING'];os.close(fd);slot[1]='CLOSED';return
        if operation=='read':
            if path==self.fail_path:raise self.primary
            raw=path.read_bytes();return {'path':str(path),'bytes':len(raw),'sha256':sha(raw),'identity':S.identity(path.stat())},raw
        raise AssertionError(operation)

class Boundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Process-local fixture subreaper only, in the guarded test process.
        libc=ctypes.CDLL(None,use_errno=True)
        if libc.prctl(36,1,0,0,0)!=0:raise OSError(ctypes.get_errno(),'fixture subreaper')
        cls.libc=libc
    def exercise(self,failed_record=None):
        with retained_directory(prefix='connected-',dir=D/'validation/tmp') as temporary:
            root=Path(temporary);os.chmod(root,0o700);stage=root/'stages/fixture';stage.mkdir(parents=True)
            entry=stage/'integration/candidate_entry.py';entry.parent.mkdir();entry.write_bytes((SOURCE/'candidate_entry.py').read_bytes());entry.chmod(0o444)
            cases=root/'cases';cases.mkdir();case=cases/'FixtureN';case.mkdir(mode=0o700)
            supervision=case/'supervision';supervision.mkdir(mode=0o700);(case/'intent').mkdir(mode=0o700)
            layout=types.SimpleNamespace(case_root=case,supervision_root=supervision,runner_root=case/'runner',science_root=case/'runner/artifact/science',intent_path=case/'intent/INTENT.json')
            attempt=types.SimpleNamespace(label='FixtureN',layout=layout,resources=[],required={'intent':False},uncertain=[],error=None)
            reg=Registry(attempt);outer=B.BoundedRelay((supervision/'root.stdout.raw',supervision/'root.stderr.raw'),B.RegistryOwner(reg,attempt),'fixture-root')
            # Only these two stage files form this inert, explicitly non-scientific fixture.
            job={'normal':{'entry':'integration/candidate_entry.py','optimized':False,'lanes':'candidate','finite_only':False}}
            frozen(stage/'JOBS.json',job)
            declared={'runner_sha256':sha((SOURCE/'run_guarded_v3.py').read_bytes()),'files':{str(p.relative_to(stage)):{'sha256':sha(p.read_bytes()),'mode':0o444} for p in (entry,stage/'JOBS.json')}}
            stage_pin=frozen(stage/'STAGE.json',declared);frozen(root/'control/EXECUTION-PHASE.json',{'aggregate_cap_seconds':600});(root/'runtime').mkdir()
            native_source=root/'fixture-native-source.c';native_source.write_text('/* inert fixture, never compiled */\n');native_source.chmod(0o444)
            receiver=root/'full_result_receiver.py';marker=case/'post-release-marker'
            receiver.write_text('from pathlib import Path\ndef job_for(mode): return {"fixture":mode}\ndef command_for(*args):\n    Path('+repr(str(marker))+').write_text("post-release reached")\n    return ["/usr/bin/false"]\n');receiver.chmod(0o444)
            # The host tools are owned by uid65534, which is deliberately outside
            # the production source/image owner contract. Keep that contract;
            # make byte-identical fixture-owned copies rather than weaken it.
            bin_dir=root/'fixture-bin';bin_dir.mkdir()
            for leaf in ('false','time'):
                q=bin_dir/leaf;q.write_bytes((Path('/usr/bin')/leaf).read_bytes());q.chmod(0o755)
            profile={}
            for kind,path in [('entry',bin_dir/'false'),('time',bin_dir/'time')]:
                p=pin(path);profile.update({kind+'_path':p['path'],kind+'_bytes':p['bytes'],kind+'_sha256':p['sha256']})
            profile.update(schema='joined-native-entry-profile-v1',source_sha256=sha(native_source.read_bytes()))
            parent=S.proc(os.getpid());end=time.monotonic_ns()+8_000_000_000
            config={'schema':'h25-waiting-entry-config-v1','case_id':'FixtureN','job':'normal','stage_path':str(stage),'stage_sha256':stage_pin['sha256'],
                    'runner_path':str(SOURCE/'run_guarded_v3.py'),'runner_sha256':declared['runner_sha256'],'entry_sha256':pin(entry)['sha256'],'entry_bytes':entry.stat().st_size,
                    'outer_output':str(layout.science_root),'completed_layout':{'case_container':str(case),'runner_root':str(case/'runner'),'science_root':str(layout.science_root)},
                    'parent':[parent['pid'],parent['start_ticks']],'working_deadline_ns':end-2_000_000_000,'cleanup_deadline_ns':end-1_000_000_000,'native_source_path':str(native_source)}
            io=FixtureIO(supervision/failed_record if failed_record=='RELEASE.json' else layout.intent_path if failed_record else None)
            kernel=types.SimpleNamespace(identity=S.identity,remember=lambda e:reg.capture_error(attempt,e),IO_UNKNOWN=[False])
            write_intent=private_function('write_intent',{'io_call':io.call,'sync_dir':lambda p:None,'C':kernel})
            # The directory fsync is performed by the production sync_dir closure.
            sync_dir=private_function('sync_dir',{'io_call':io.call,'C':kernel});write_intent=private_function('write_intent',{'io_call':io.call,'sync_dir':sync_dir,'C':kernel})
            wait_pin=write_intent(supervision/'WAIT.json',config)
            domain=S.OwnedDomain(reg,attempt);outer.open();out,err=outer.writers();process=None;deadline=S.DeadlineOwner(end)
            state={'owner_pid':os.getpid(),'run_context':None,'waiting':{'FixtureN':(config,wait_pin,None)},'pending_intents':{'FixtureN':{'schema':'fresh-active-nested-runner-intent-v2','label':'FixtureN','parent_pid':parent['pid'],'parent_start_ticks':parent['start_ticks'],'completed_layout':config['completed_layout']}},'deadlines':{'FixtureN':deadline},'protected':None,'phase':'ROOT_LAUNCH'}
            observed={};query_processes=[]
            class Association:
                def observe(self,label):
                    protected=state['protected'];protected.verify();entry_before=S.proc(protected.entry_key[0]);selftest.assertIn(entry_before['state'],('T','t'))
                    qdomain=S.OwnedDomain(reg,attempt,protected=protected)
                    child_ready=case/'query-child.json'
                    program='import subprocess,time,pathlib; p=subprocess.Popen(["/usr/bin/python3.12","-c","import time;time.sleep(2)"]);pathlib.Path('+repr(str(child_ready))+').write_text(str(p.pid));time.sleep(2)'
                    q=subprocess.Popen(['/usr/bin/python3.12',*FLAGS,'-c',program],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,env=ENV)
                    query_processes.append(q);row=S.proc(q.pid);qdomain.root=S.generation(row);qdomain.add(row)
                    until=time.monotonic()+1
                    while not child_ready.exists() and time.monotonic()<until:outer.pump(.01)
                    selftest.assertTrue(child_ready.exists());qdomain.observe();protected_fds=dict(domain.fds)
                    cleanup=qdomain.cleanup(q,time.monotonic()+2)
                    selftest.assertTrue(cleanup['complete']);selftest.assertEqual(cleanup['remaining'],[])
                    protected.verify();selftest.assertEqual(domain.fds,protected_fds)
                    selftest.assertIn(S.proc(protected.entry_key[0])['state'],('T','t'))
                    selftest.assertTrue(all(regrow['state']=='CLOSED' for regrow in qdomain.fd_tokens.values()))
                    # Unexpected adopted reaps remain observations, not a valid original property result.
                    observed['query_cleanup']=cleanup;observed['entry_still_stopped']=True
                    return None
                def bind_launch(self,label):return object()
                def launch_record(self,token):
                    row={'case_id':'FixtureN','parent_pid':os.getpid()};row['association_sha256']=sha((json.dumps(row,sort_keys=True,separators=(',',':'))+'\n').encode());return row
            association=Association();ports={n:(getattr(association,n),getattr(Association,n),getattr(Association,n).__code__) for n in ('observe','bind_launch','launch_record')};selftest=self
            joined=(B,pin(SOURCE/'bounded_relay.py'),profile,None,pin(receiver),association,Association,ports,os.getpid())
            qualify=private_function('qualify_waiting_candidate',{'state':state,'registry':reg,'_JOINED':joined,'_COMMON':(pin(SOURCE/'run_guarded_v3.py'),pin(entry)),
                'STAGE_BASE':root/'stages','C':kernel,'io':io,'write_intent':write_intent,'validate_nested_intent':lambda v:self.assertEqual(v['schema'],'fresh-active-nested-runner-intent-v3')})
            wrapper='import runpy,sys; n=runpy.run_path('+repr(str(SOURCE/'run_guarded_v3.py'))+',run_name="fixture_common");n["main"].__globals__.update(HERE=__import__("pathlib").Path('+repr(str(root))+'),SOURCE_ROOT=__import__("pathlib").Path('+repr(str(cases))+'),TIMEOUT=7);sys.argv=["fixture","fixture","normal","FixtureN","--waiting-config",'+repr(str(supervision/'WAIT.json'))+',"--waiting-sha256",'+repr(wait_pin['sha256'])+'];n["main"]()'
            try:
                deadline.start();process=subprocess.Popen(['/usr/bin/python3.12',*FLAGS,'-c',wrapper],stdin=subprocess.DEVNULL,stdout=out,stderr=err,env=ENV,start_new_session=True,cwd=root)
                outer.close_writers();row=S.proc(process.pid);domain.root=S.generation(row);domain.add(row);state['run_context']={'process':process,'domain':domain,'relay':outer,'rss_bytes':1073741824}
                if failed_record:
                    with self.assertRaises(OSError) as caught:qualify({'stage':'fixture','job':'normal','label':'FixtureN'},domain,process,outer)
                    self.assertIs(caught.exception,io.primary);self.assertTrue(observed['entry_still_stopped']);self.assertFalse(marker.exists())
                    protected=state['protected'];self.assertFalse(protected.release_entered);self.assertIn(S.proc(protected.entry_key[0])['state'],('T','t'))
                else:
                    protected=qualify({'stage':'fixture','job':'normal','label':'FixtureN'},domain,process,outer)
                    self.assertTrue(protected.released);self.assertTrue(protected.release_entered)
                    while process.poll() is None and time.monotonic_ns()<end-500_000_000:outer.pump(.01)
                    self.assertIsNotNone(process.poll());self.assertTrue(marker.exists())
                    self.assertEqual(process.returncode,1) # Original common R STOP from the inert false child.
                    entry_result=json.loads((case/'runner/ENTRY.json').read_text());self.assertEqual(entry_result['inner_exit'],1)
                    self.assertTrue(entry_result['outer_usage_aliases_retired'])
            finally:
                if deadline.started and not deadline.finished:deadline.finish()
                cleanup=domain.cleanup(process,time.monotonic()+2)
                outer.close_writers()
                if outer.primary is None:outer.drain_until(time.monotonic()+.2)
                if not outer.retired:outer.retire()
                for q in query_processes:
                    if q.returncode is None:
                        try:q.wait(timeout=.2)
                        except ChildProcessError:pass
                self.assertTrue(cleanup['complete'])
    def test_release_after_actual_query_subtree_retirement(self):self.exercise()
    def test_intent_readback_failure_never_releases_stopped_entry(self):self.exercise('INTENT.json')
    def test_release_seal_readback_failure_never_releases_stopped_entry(self):self.exercise('RELEASE.json')

class Deadlines(unittest.TestCase):
    def test_nested_pop_retains_original_absolute_timer(self):
        end=time.monotonic_ns()+2_000_000_000;owner=S.DeadlineOwner(end);owner.start()
        try:
            token=owner.push(time.monotonic_ns()+500_000_000)
            before=signal.getitimer(signal.ITIMER_REAL)[0]
            owner.pop(token);remaining=signal.getitimer(signal.ITIMER_REAL)[0]
            self.assertGreater(remaining,before)
            self.assertLessEqual(remaining,(end-time.monotonic_ns())/1e9+.01)
            owner.checkpoint()
        finally:owner.finish()
        self.assertEqual(signal.getitimer(signal.ITIMER_REAL),(0.0,0.0))
    def test_work_expiry_keeps_only_original_retirement_deadline(self):
        end=time.monotonic_ns()+2_000_000_000;owner=S.DeadlineOwner(end);owner.start()
        try:
            owner.push(time.monotonic_ns()+20_000_000)
            with self.assertRaises(S.ExecutionDeadline):time.sleep(.1)
            self.assertTrue(owner.poisoned)
            self.assertGreater(signal.getitimer(signal.ITIMER_REAL)[0],0)
            self.assertLessEqual(signal.getitimer(signal.ITIMER_REAL)[0],(end-time.monotonic_ns())/1e9+.01)
            with self.assertRaises(Exception):owner.push(time.monotonic_ns()+100_000_000)
        finally:owner.finish()

if __name__=='__main__':unittest.main(verbosity=2)
