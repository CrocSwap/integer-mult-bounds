"""NEW-body-only pure discriminators. Every service and PID/FD below is fake.

No state/token returned here is an actual capability; no original function,
Popen, native call, kernel census, namespace or target process is executed.
"""
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import unittest

BASE=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453/outputs/c05-v03-completion-20261102T055710Z/unit05')
IMPL=BASE/'implementation'


class FixtureStop(RuntimeError):pass


def need(value,message):
    if value is not True:raise FixtureStop(message)


def extract(name,scope):
    tree=ast.parse((IMPL/'v03_prefix_supervisor_v1.py').read_bytes(),feature_version=(3,12))
    functions=[n for n in tree.body if type(n) is ast.FunctionDef and n.name==name]
    if len(functions)!=1:raise ValueError('unique NEW function required')
    if name not in ('_supervise','_source_snapshot','_capture'):raise ValueError('not a newly authored test target')
    if any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(functions[0])):raise ValueError('unexpected function import')
    data=dict(scope)
    exec(compile(ast.Module(body=functions,type_ignores=[]),'<new-supervisor-body-fixture>','exec'),data)
    return data[name]


def owner():return {'primary':[None],'pending':[False],'iterator_uncertain':[False],'quarantine':[False]}


class SuperviseTests(unittest.TestCase):
    def fixture(self,fail=None,cleanup=None,close=None):
        counts={'popen':0,'finish':0,'close_logs':0,'opens':0,'terminal':0,'adopt':0,'observe':0}
        own=owner()
        case={'output':'/FAKE/output','root_seconds':40,'address_space_bytes':1024,'rss_bytes':1024,
              'id':'FAKE','generation':'FAKE','launch_nonce':'0'*64,'stage_directory':'/FAKE/stage',
              'command':['FAKE-NO-EXEC'],'expectation':{'outcome':'FIXTURE-ONLY'}}
        state={'unknown_owner':own,'plan':{'case':case,'session_directory':'/FAKE/session','mode':'normal'},
               'phase':'READY','run':None,'errors':object(),'initial_sources':('FAKE-SNAPSHOT',),'pid':10,'shared_deadline':1000}
        A=RuntimeError('A fake first');B=RuntimeError('B fake cleanup')
        def stat(path,**kw):
            if path==case['output']:raise FileNotFoundError('fake absent')
            return NS(st_size=0)
        def opening(*args):
            counts['opens']+=1
            if fail=='open2' and counts['opens']==2:raise A
            return 100+counts['opens']
        def popen(*args,**kw):
            counts['popen']+=1
            if fail=='popen':raise A
            return object()
        def adopt(*args):
            counts['adopt']+=1
            if fail=='adopt':raise A
            return (11,10,11,11,123,'Z',0)
        def observe(*args):
            counts['observe']+=1
            if fail=='observe':raise A
            return (),()
        def finish(*args):
            counts['finish']+=1
            if cleanup:raise B
        def close_logs(run,primary):
            counts['close_logs']+=1
            for n,fd in enumerate(run['log_fds']):
                if fd is None or run['log_close_attempted'][n]:continue
                run['log_close_attempted'][n]=True
                if close:raise B
                run['log_close_confirmed'][n]=True
        def terminal(*args):counts['terminal']+=1;return {'FAKE-NOT-OWNERSHIP':True}
        parent=NS(_STAT=stat,_GETRLIMIT=lambda x:(100,100),_OPEN=opening,_SETRLIMIT=lambda *x:None,
          _GETTIMER=lambda *x:(0.0,0.0),_GETSIGNAL=lambda *x:None,_SIGNAL=lambda *x:None,
          _SETTIMER=lambda *x:None,_alarm=lambda *x:None,_POPEN=popen,_SLEEP=lambda *x:None,_close_logs=close_logs)
        domain=NS(CLEANUP_SECONDS=2,create_domain=lambda x:object(),adopt_popen=adopt,
                  observe=observe,poll_owned=lambda *x:0,finish_domain=finish)
        scope={'schema':NS(need=need,EpochStop=FixtureStop,LOG_BYTES=2097152),'parent':parent,'domain':domain,
          '_guard':lambda x:None,'_source_snapshot':lambda x:('FAKE-SNAPSHOT',),'_CLOCK':lambda:1,
          'copying':NS(write_once=lambda *a,**k:{'FAKE-FILE-PIN':True}),'_record_bytes':lambda x:b'FAKE',
          'resource':NS(RLIMIT_FSIZE=1,RLIMIT_AS=9),'signal':NS(ITIMER_REAL=0,SIGALRM=14),
          '_clean':lambda x:None,'os':NS(O_WRONLY=1,O_CREAT=2,O_EXCL=4,O_CLOEXEC=8,O_NOFOLLOW=16),
          'subprocess':NS(DEVNULL=-3),'ENV':{'FAKE':'NOT-A-NATIVE-ENV'},'_terminal':terminal}
        return extract('_supervise',scope),state,counts,A,B

    def test_popen_primary_survives_cleanup_secondary(self):
        fn,s,c,A,B=self.fixture('popen',True)
        with self.assertRaises(RuntimeError) as caught:fn(s)
        self.assertIs(caught.exception,A)
        self.assertIs(s['unknown_owner']['primary'][0],A)
        self.assertIs(s['run']['errors'][3],B)
        self.assertEqual((c['popen'],c['finish'],c['close_logs'],c['terminal']),(1,1,1,0))

    def test_adoption_and_observe_primary_survive_cleanup(self):
        for phase in ('adopt','observe'):
            with self.subTest(phase=phase):
                fn,s,c,A,B=self.fixture(phase,True)
                with self.assertRaises(RuntimeError) as caught:fn(s)
                self.assertIs(caught.exception,A)
                self.assertIs(s['run']['errors'][3],B)
                self.assertEqual(c['finish'],1)
                self.assertEqual(c['terminal'],0)

    def test_uncertain_raw_open_stops_later_acquisitions(self):
        fn,s,c,A,B=self.fixture('open2')
        with self.assertRaises(RuntimeError) as caught:fn(s)
        self.assertIs(caught.exception,A)
        self.assertTrue(s['unknown_owner']['pending'][0])
        self.assertTrue(s['unknown_owner']['quarantine'][0])
        self.assertEqual((c['opens'],c['popen'],c['finish'],c['close_logs']),(2,0,1,1))
        self.assertEqual(s['run']['log_close_attempted'],[True,False])
        self.assertEqual(c['terminal'],0)

    def test_failed_raw_close_is_not_retried_or_terminal(self):
        fn,s,c,A,B=self.fixture(close=True)
        with self.assertRaises(RuntimeError) as caught:fn(s)
        self.assertIs(caught.exception,B)
        self.assertEqual(c['close_logs'],1)
        self.assertTrue(s['unknown_owner']['quarantine'][0])
        self.assertEqual(s['run']['log_close_attempted'],[True,False])
        self.assertEqual(c['terminal'],0)

    def test_consumed_control_does_not_spawn_again(self):
        fn,s,c,A,B=self.fixture()
        fn(s)
        with self.assertRaises(FixtureStop):fn(s)
        self.assertEqual(c['popen'],1)


class OuterPlanTests(unittest.TestCase):
    def fixture(self):
        raw=b'{}';pin={'path':'/FAKE/outer-plan','identity':{'device':1,'inode':1}}
        row={'path':'/FAKE/input','identity':{'device':1,'inode':2}}
        state={'plan':{'source_files':[{'path':row['path']}],'case':{},'source_closure_admission_sha256':'0'*64},
               'configuration':{'plan':pin},'errors':object(),'plan_raw':raw,'plan_endpoint_raw':[None]*3,'plan_endpoint_count':0}
        calls=[];read=[raw];rows=[row]
        def verified(pin,bound,**kw):calls.append((pin,bound));return read[0]
        scope={'schema':NS(need=need,RECORD_BYTES=1048576,inode=lambda x:(x['identity']['device'],x['identity']['inode']),sha=lambda b:hashlib.sha256(b).hexdigest()),
               'copying':NS(read_verified=verified),'parent':NS(MAX_SOURCE_FILES=2,_snapshot_sources=lambda *a:rows,_stage=lambda *a:{}),
               '_record_bytes':lambda obj:(json.dumps(obj,sort_keys=True)+'\n').encode()}
        return extract('_source_snapshot',scope),state,calls,read,rows

    def test_three_actual_fixture_reads_retained_and_equal(self):
        fn,s,c,r,rows=self.fixture();a=fn(s);b=fn(s);d=fn(s)
        self.assertEqual(a,b);self.assertEqual(a,d)
        self.assertEqual(len(c),3);self.assertEqual(s['plan_endpoint_raw'],[b'{}']*3)
        self.assertEqual(s['plan_endpoint_count'],3)
        with self.assertRaises(FixtureStop):fn(s)
        self.assertEqual(len(c),3)

    def test_plan_path_cannot_be_an_inner_row(self):
        fn,s,c,r,rows=self.fixture();s['plan']['source_files'][0]['path']=s['configuration']['plan']['path']
        with self.assertRaises(FixtureStop):fn(s)
        self.assertEqual(c,[])

    def test_plan_inode_cannot_alias_an_inner_row(self):
        fn,s,c,r,rows=self.fixture();rows[0]['identity']['inode']=1
        with self.assertRaises(FixtureStop):fn(s)
        self.assertEqual(len(c),1)
        self.assertEqual(s['plan_endpoint_raw'][0],b'{}')

    def test_changed_plan_raw_is_retained_before_rejection(self):
        fn,s,c,r,rows=self.fixture();r[0]=b'CHANGED-FAKE-RAW'
        with self.assertRaises(FixtureStop):fn(s)
        self.assertEqual(s['plan_endpoint_raw'][0],b'CHANGED-FAKE-RAW')

    def test_outer_plan_row_is_counted(self):
        fn,s,c,r,rows=self.fixture();s['plan']['source_files'].append({'path':'/FAKE/extra'})
        with self.assertRaises(FixtureStop):fn(s)
        self.assertEqual(c,[])


class RawRetentionTests(unittest.TestCase):
    def test_partial_copy_failure_retains_already_captured_sources(self):
        class CopyFailure(RuntimeError):pass
        B=CopyFailure('FAKE copy failure');own=owner();run={'retained':{}}
        state={'unknown_owner':own,'errors':object(),'plan':{'session_directory':'/FAKE/session','case':{'output':'/FAKE/out','expectation':{}}}}
        count=[0]
        def inspect(path,bound,**kw):count[0]+=1;return {'path':path,'pair':(1,count[0])}
        def copy(source,target,occupied,**kw):
            if source['path'].endswith('stderr.raw'):raise B
            return {'path':target,'pair':(2,1)}
        scope={'schema':NS(LOG_BYTES=2097152,RECORD_BYTES=1048576,inode=lambda x:x['pair'],need=need),
               '_expected_files':lambda e:(), '_guard':lambda s:None,
               'copying':NS(inspect=inspect,copy_once=copy,read_verified=lambda *a,**k:b'')}
        fn=extract('_capture',scope)
        with self.assertRaises(CopyFailure) as caught:fn(state,run)
        self.assertIs(caught.exception,B)
        self.assertIn('copy',run['retained']['stdout.raw'])
        self.assertIn('source',run['retained']['stderr.raw'])
        self.assertNotIn('copy',run['retained']['stderr.raw'])


if __name__=='__main__':unittest.main(verbosity=2)
