"""Fixed pre-entry acquisition witness v30; no prepare or meter dispatch.

Uses exact published PR6709 parent startup and private loader handles. Original
C2 GlobalLease/OwnedIO and actual F4 readers remain unchanged. The fixed read
closure is preflighted before F4 is allowed to follow it; no IO proxy or forged
owner is used. This one-shot process has no resume, inbox or Tool bridge.

Predecessor authors retain credit. Substantial ChatGPT Pro, Codex and Sol Max
implementation/review assistance. Source review is not native qualification.
"""
import builtins
import errno
import hashlib
import json
import os
import resource
from pathlib import Path
import stat
import sys
import time
from types import ModuleType

W=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
R=W/'outputs/h25-data-handling-20261028'
Q=W/'outputs/f4-a4-runtime-qualification-20261104T0459Z'
DRIVER=Q/'implementation/manual_provider_driver_v1.py'
INSTALLED=R/'areas/manual-integration-v29'
PARENT_PATH=INSTALLED/'manual_parent_v1.py'
PARENT_PIN={'bytes':33415,'sha256':'6cc5a91e141517df7c66740ac321571f140d4b23e36a52342a00e008ab052a3d'}
FIN_ROOT=R/'control/prospective-financial-v1'
FIN_HEAD=FIN_ROOT/'HEAD.json'
FORMAL_CONTROL=R/'control/fresh-metered-round-v1'
FORMAL_DOMAIN=R/'runtime/fresh-metered-round-v1/attempts'
LEGACY=R/'areas/fresh-round-provenance-bridge-v1/OPENING.json'
LEGACY_CORPUS=LEGACY.parent/'corpus'
ENV={'PATH':'/usr/bin:/bin','PYTHONHASHSEED':'0','LANG':'C.UTF-8',
     'LC_ALL':'C.UTF-8','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
CAP,MAX_FILES,MAX_BYTES,RECEIPT_CAP=131072,4096,16777216,67108864
RETAINED=[]
_GATE=None


class DriverStop(RuntimeError):
    pass


def need(value,message):
    if value is not True:raise DriverStop(message)


def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,
                       allow_nan=False)+'\n').encode('ascii')


def errno_presence(errno_value):
    return 'ENOENT' if type(errno_value) is int and errno_value==errno.ENOENT else 'ERROR'


def classify_head_fact(fact):
    need(type(fact) is dict and set(fact)=={'presence','canonical_ancestors',
         'paired_namespace','real_ex_verified'},'DRIVER:HEAD_FACT')
    need(type(fact['presence']) is str and fact['presence'] in ('PRESENT','ENOENT','ERROR') and
         all(type(fact[k]) is bool for k in ('canonical_ancestors','paired_namespace',
                                             'real_ex_verified')),'DRIVER:HEAD_FACT')
    if not all(fact[k] for k in ('canonical_ancestors','paired_namespace','real_ex_verified')):
        return 'STOP_UNCERTAIN'
    if fact['presence']=='ENOENT':return 'HEAD_ABSENT'
    return 'PRESENT' if fact['presence']=='PRESENT' else 'STOP_UNCERTAIN'


def read_policy(path):
    """Pure lexical necessary gate; canonical native checks follow separately."""
    if type(path) is not str or not path.startswith('/') or '\x00' in path or '\\' in path:
        return False
    p=Path(path)
    if str(p)!=path or any(part in ('.','..') for part in path.split('/')[1:]):return False
    return (p==LEGACY or p==LEGACY_CORPUS or p.parent==LEGACY_CORPUS or
            any(p==root or p.is_relative_to(root) for root in
                (FIN_ROOT,FORMAL_CONTROL,FORMAL_DOMAIN)))


class ReadBudget:
    def __init__(self):self.files={};self.total=0
    def add(self,path,raw_bytes):
        need(type(path) is str and type(raw_bytes) is bytes,'DRIVER:READ_BUDGET_TYPE')
        need(len(raw_bytes)<=CAP,'DRIVER:READ_RECORD_CAP')
        if path in self.files:
            need(self.files[path]==raw_bytes,'DRIVER:READ_CHANGED');return
        need(len(self.files)<MAX_FILES and self.total+len(raw_bytes)<=MAX_BYTES,
             'DRIVER:READ_CLOSURE_CAP')
        self.files[path]=raw_bytes;self.total+=len(raw_bytes)


class FailureState:
    def __init__(self):
        self.first=None;self.secondary=[];self.unknown=False;self.close_failed=False
    def remember(self,error):
        if self.first is None:self.first=error
        elif error is not self.first and all(error is not e for e in self.secondary):
            if len(self.secondary)<32:self.secondary.append(error)
            else:self.unknown=True
        return self.first
    def close_failure(self,error):
        self.close_failed=True;self.unknown=True;return self.remember(error)


class BootstrapGate:
    def __init__(self):self.used=False
    def enter(self,verb='BOOTSTRAP'):
        need(self.used is False,'DRIVER:ONE_USE_NO_RESUME')
        self.used=True
        need(type(verb) is str and verb=='BOOTSTRAP','DRIVER:DISPATCH_DISABLED')


def validate_snapshot_data(snapshot,evidence,expected_head_pin):
    """Necessary DATA postcondition; actual native/source facts are separate."""
    need(type(snapshot) is dict and snapshot.get('schema')=='fresh-financial-snapshot-v1',
         'DRIVER:CURRENT_COMPLETE_SNAPSHOT_REQUIRED')
    need(snapshot.get('head_pin')==expected_head_pin,'DRIVER:STALE_HEAD')
    need(type(evidence) is dict and type(evidence.get('pending')) is list and
         type(evidence.get('unknown')) is list,'DRIVER:EVIDENCE')
    need(not evidence['pending'] and not evidence['unknown'] and not evidence.get('blockers',[]),
         'DRIVER:PENDING_OR_UNKNOWN')
    if 'head_pin' in evidence:need(evidence['head_pin']==expected_head_pin,'DRIVER:STALE_HEAD')
    return 'VALID_CLOSED_PREDECESSOR'


def identity(st):
    return (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_nlink,st.st_size,
            st.st_mtime_ns,st.st_ctime_ns)


def _source(path,pin,failure):
    """Fixed source transport only; known close once, retained raw/module later."""
    fd=None;phase='PENDING';raw=None
    try:
        before=path.lstat()
        need(path.resolve(strict=True)==path and stat.S_ISREG(before.st_mode) and
             stat.S_IMODE(before.st_mode)==0o444 and before.st_uid in (0,os.getuid()) and
             before.st_nlink==1 and before.st_size==pin['bytes'],'DRIVER:SOURCE')
        fd=os.open(path,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC);phase='OWNED'
        need(identity(os.fstat(fd))==identity(before),'DRIVER:SOURCE')
        chunks=[];count=0
        while True:
            part=os.read(fd,min(65536,pin['bytes']+1-count))
            if not part:break
            count+=len(part);need(count<=pin['bytes'],'DRIVER:SOURCE_CAP');chunks.append(part)
        raw=b''.join(chunks)
        need(count==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256'] and
             identity(os.fstat(fd))==identity(before)==identity(path.lstat()),'DRIVER:SOURCE')
    except BaseException as error:
        if phase=='PENDING':failure.unknown=True
        failure.remember(error)
    finally:
        if phase=='OWNED':
            phase='CLOSE_ENTERED'
            try:os.close(fd);phase='CLOSED'
            except BaseException as error:failure.close_failure(error)
    if failure.first is not None:raise failure.first
    return raw


def _load_parent(failure):
    raw=_source(PARENT_PATH,PARENT_PIN,failure)
    name='h25_runtime_acquisition_private_parent_v30'
    need(name not in sys.modules,'DRIVER:MODULE_REPLAY')
    module=ModuleType(name)
    module.__dict__.update(__name__=name,__file__=str(PARENT_PATH),__package__=None,
                           __spec__=None,__builtins__=builtins)
    sys.modules[name]=module;RETAINED.append((module,raw))
    exec(compile(raw,str(PARENT_PATH),'exec',dont_inherit=True),module.__dict__)
    return module


def _canonical_nofollow(path):
    need(type(path) is type(W) and path.is_absolute(),'DRIVER:CANONICAL_PATH')
    current=Path('/')
    for index,part in enumerate(path.parts[1:]):
        current=current/part;st=current.lstat()
        need(not stat.S_ISLNK(st.st_mode),'DRIVER:SYMLINK_COMPONENT')
        if index<len(path.parts)-2:need(stat.S_ISDIR(st.st_mode),'DRIVER:ANCESTOR_TYPE')
    return st


def _directory(path):
    st=_canonical_nofollow(path)
    need(stat.S_ISDIR(st.st_mode) and
         not stat.S_IMODE(st.st_mode)&0o002,'DRIVER:CANONICAL_ANCESTOR')
    return identity(st)


def _paired_presence(lease):
    """Non-acquiring lstat only; failed C2 IO never becomes clean absence."""
    chain=[];missing=None
    for path in (R,R/'control',FIN_ROOT):
        try:chain.append((path,_directory(path)))
        except OSError as error:
            if errno_presence(error.errno)!='ENOENT':raise
            missing=path;break
    if missing is not None:
        need(chain!=[],'DRIVER:AMBIGUOUS_MISSING_ANCESTOR')
        need(all(_directory(p)==old for p,old in chain),'DRIVER:ANCESTOR_CHANGED')
        try:missing.lstat()
        except OSError as error:need(errno_presence(error.errno)=='ENOENT','DRIVER:ABSENCE_CHANGED')
        else:raise DriverStop('DRIVER:ABSENCE_CHANGED')
        lease.verify()
        return {'presence':'ENOENT','canonical_ancestors':True,'paired_namespace':True,
                'real_ex_verified':True},None,str(missing)
    before=None
    try:before=FIN_HEAD.lstat()
    except OSError as error:
        if errno_presence(error.errno)!='ENOENT':raise
    need(all(_directory(p)==old for p,old in chain),'DRIVER:ANCESTOR_CHANGED')
    if before is None:
        try:FIN_HEAD.lstat()
        except OSError as error:need(errno_presence(error.errno)=='ENOENT','DRIVER:ABSENCE_CHANGED')
        else:raise DriverStop('DRIVER:ABSENCE_CHANGED')
        lease.verify()
        return {'presence':'ENOENT','canonical_ancestors':True,'paired_namespace':True,
                'real_ex_verified':True},None,str(FIN_HEAD)
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.getuid() and
         stat.S_IMODE(before.st_mode)==0o600 and 0<before.st_size<=CAP and
         FIN_HEAD.resolve(strict=True)==FIN_HEAD and identity(FIN_HEAD.lstat())==identity(before),
         'DRIVER:HEAD_ALIAS_OR_TYPE')
    lease.verify()
    return {'presence':'PRESENT','canonical_ancestors':True,'paired_namespace':True,
            'real_ex_verified':True},identity(before),None


def _targets(F,obj):
    """Exact consequential edge selector from selected F4 read_financial_opening."""
    if type(obj) is not dict:return []
    schema=obj.get('schema');records=F.FRAME_RECORDS
    if schema==records['ENTRY_MANIFEST']['schema']:
        return [obj[k] for k in ('command_pin','reservation_pin','pre_entry_pin','meter_start_pin',
            'meter_body_pin','native_chain_pin','financial_adjudication_pin','formal_start_pin',
            'formal_receipt_pin') if obj[k] is not None]
    if schema==records['COMMAND']['schema']:
        return [obj['permission_pin']]+([] if obj['metadata_close_intent'] is None else
                                      [obj['metadata_close_intent']['receipt_pin']])
    if schema==records['PRE_ENTRY']['schema']:return [obj['provider_request_pin']]
    if schema==records['STATE']['schema']:
        return [e[k] for e in obj['metadata_close_events'] for k in
                ('intent_pin','formal_head_pin','financial_state_pin','receipt_pin') if e[k] is not None]
    if schema=='fresh-active-head-v1':return [obj['registry_pin']]
    if schema==records['NATIVE_CHAIN']['schema']:
        return [c[k] for c in obj['calls'] for k in ('request_pin','original_tool_result_pin')
                if c[k] is not None and c[k]['bytes']<=CAP]
    return []


def _preflight(C,F,head_raw):
    """Full finite read-closure verification, using only actual unchanged C.IO.

    Every next file path is policy-checked before its resolve/lstat/open/read.
    Whole closure and identities are rechecked before original F4 repeats reads.
    """
    budget=ReadBudget();rows={};docs={};dirs={}
    def grab(path,expected=None,mode=None,decode=True):
        p=str(path);need(read_policy(p),'DRIVER:BLOCKED_READ_DOMAIN')
        if p in docs:
            if expected is not None:
                need(rows[p]['bytes']==expected['bytes'] and rows[p]['sha256']==expected['sha256'] and
                     rows[p]['mode']==expected['mode'],'DRIVER:REFERENCE_CHANGED')
            return docs[p]
        _canonical_nofollow(Path(p))
        row,raw=C.IO.read(Path(p),CAP,mode,expected,True)
        budget.add(p,raw);rows[p]=row;docs[p]=F.financial_decode(raw) if raw and decode else None
        return docs[p]
    def directory(path):
        need(read_policy(str(path)),'DRIVER:BLOCKED_READ_DOMAIN')
        before=_directory(path);names=C.IO.names(path,MAX_FILES+1)
        need(len(names)<=MAX_FILES and all(type(n) is str and n not in ('.','..') and
             '/' not in n and '\\' not in n for n in names),'DRIVER:CENSUS')
        need(_directory(path)==before,'DRIVER:DIRECTORY_CHANGED')
        dirs[str(path)]=(before,tuple(sorted(names)));return sorted(names)
    for name in directory(FIN_ROOT):
        if name!='entries':
            need(name.endswith('.json'),'DRIVER:CENSUS')
            grab(FIN_ROOT/name,mode=0o600 if name=='HEAD.json' or name.startswith('HEAD-') else 0o444)
    for name in directory(FIN_ROOT/'entries'):
        F.flabel(name)
        for member in directory(FIN_ROOT/'entries'/name):
            need(member.endswith('.json'),'DRIVER:CENSUS')
            grab(FIN_ROOT/'entries'/name/member,mode=0o444 if member.startswith('ENTRY-') else None)
    need(budget.files.get(str(FIN_HEAD))==head_raw,'DRIVER:STALE_HEAD')
    head=docs[str(FIN_HEAD)];F.fx(head,('schema','generation','state_pin','opening_pin','previous_head_sha256'))
    need(head['schema']=='fresh-financial-head-v1','DRIVER:HEAD_SCHEMA')
    opening=grab(head['opening_pin']['path'],head['opening_pin'])
    F.validate_original_record('OPENING',opening)
    grab(opening['frame_contract_pin']['path'],opening['frame_contract_pin'])
    scanned=set()
    while set(docs)-scanned:
        path=next(iter(set(docs)-scanned));scanned.add(path)
        for target in _targets(F,docs[path]):
            F.fp(target,True);need(read_policy(target['path']),'DRIVER:BLOCKED_READ_DOMAIN')
            grab(target['path'],target)
    need(F.LEGACY_BASE_PIN['path']==str(LEGACY),'DRIVER:LEGACY_SUBJECT')
    grab(LEGACY,F.LEGACY_BASE_PIN,decode=False)
    legacy=F.decode(budget.files[str(LEGACY)])
    names=directory(LEGACY_CORPUS)
    need(type(legacy) is dict and type(legacy.get('files')) is dict and
         set(names)==set(legacy['files']),'DRIVER:LEGACY_CORPUS')
    for name in names:
        item=legacy['files'][name]
        grab(LEGACY_CORPUS/name,{'path':str(LEGACY_CORPUS/name),'bytes':item['bytes'],
                               'sha256':item['sha256'],'mode':0o444},decode=False)
    # No unpermitted reader capability is supplied. The original function will
    # receive exactly C.IO after this closure has been paired under real EX.
    for path,row in rows.items():
        after,again=C.IO.read(Path(path),CAP,row['mode'],
                             {'bytes':row['bytes'],'sha256':row['sha256']},True)
        need(after==row and again==budget.files[path],'DRIVER:READ_CLOSURE_CHANGED')
    for path,(old,names) in dirs.items():
        need(_directory(Path(path))==old and tuple(sorted(C.IO.names(Path(path),MAX_FILES+1)))==names,
             'DRIVER:READ_CLOSURE_CHANGED')
    return head,{'paths':sorted(rows),'file_count':len(rows),'bytes':budget.total,
                 'directories':sorted(dirs),'complete_preflight':True}


def _launch(profile):
    need(type(profile) is str and profile in ('normal','optimized'),'DRIVER:PROFILE')
    need(sys.executable=='/usr/bin/python3.12' and sys.implementation.name=='cpython' and
         sys.version_info[:2]==(3,12) and sys.flags.optimize==(1 if profile=='optimized' else 0) and
         dict(os.environ)==ENV and os.getcwd()==str(W),'DRIVER:LAUNCH')
    for limit,expected in ((resource.RLIMIT_AS,1073741824),(resource.RLIMIT_CPU,20),
                           (resource.RLIMIT_FSIZE,67108864),(resource.RLIMIT_NOFILE,256)):
        need(resource.getrlimit(limit)==(expected,expected),'DRIVER:RESOURCE_ENVELOPE')
    for fd in (1,2):
        st=os.fstat(fd)
        need(stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode)==0o600 and
             st.st_uid==os.getuid() and st.st_nlink==1,'DRIVER:CAPTURE')


def run_bootstrap(profile):
    global _GATE
    failure=FailureState();RETAINED.append(failure)
    need(_GATE is None,'DRIVER:ONE_USE_NO_RESUME');_GATE=BootstrapGate();_GATE.enter()
    parent=loader=loaded=lease=None;close_entered=False;acquire_entered=False
    classification='STOP_UNCERTAIN';fact=None;missing_component=None;snapshot=None
    expected_head=None;evidence=None;read_domain=None;lease_observations=[];cleanup=None
    begin=end=None;stage='BEFORE_BOOTSTRAP'
    try:
        begin=time.monotonic_ns();_launch(profile)
        parent=_load_parent(failure);RETAINED.append(parent)
        startup=parent._Startup();RETAINED.append(startup)
        loader=startup.load();RETAINED.append(loader)
        loaded=loader.load_fixed_sources(profile);RETAINED.append(loaded)
        loader._actual(loaded);C,F=loaded.C,loaded.F
        need(F.FIN_HEAD==FIN_HEAD and F.FIN_ROOT==FIN_ROOT and F.CONTROL==FORMAL_CONTROL and
             F.DOMAIN==FORMAL_DOMAIN,'DRIVER:FIXED_READ_DOMAIN')
        lease=C.GlobalLease();RETAINED.append(lease)
        stage='ACQUIRE_ENTERED';acquire_entered=True
        lease.acquire();lease_observations.append(lease.verify());stage='EX_VERIFIED'
        fact,head_identity,missing_component=_paired_presence(lease)
        classification=classify_head_fact(fact)
        if classification=='PRESENT':
            stage='READ_PRESENT_HEAD'
            row,head_raw=C.IO.read(FIN_HEAD,CAP,0o600,None,True)
            need(tuple(row['identity'])==head_identity,'DRIVER:STALE_HEAD')
            expected_head={'path':str(FIN_HEAD),'bytes':row['bytes'],'sha256':row['sha256'],'mode':0o600}
            head,read_domain=_preflight(C,F,head_raw)
            loader._actual(loaded);lease.verify();stage='READ_COMPLETE_PREDECESSOR'
            snapshot=F.read_financial_opening(C.IO,head['opening_pin'],os.getuid())
            evidence=F.financial_evidence(snapshot)
            classification=validate_snapshot_data(snapshot,evidence,expected_head)
            # Immutable read domain checked again against the actual returned
            # view. A historical view or changed head never supplies currentness.
            need(all(read_policy(path) for path in snapshot['wires']),
                 'DRIVER:BLOCKED_READ_DOMAIN')
            RETAINED.extend((head_raw,snapshot,evidence))
        lease_observations.append(lease.verify());loader._actual(loaded)
        stage='OBSERVATION_COMPLETE'
    except BaseException as error:
        failure.remember(error);classification='STOP_UNCERTAIN'
        if lease is not None and acquire_entered and lease.fd is None:failure.unknown=True
    finally:
        if lease is not None and type(lease.fd) is int and lease.phase not in ('CLOSE_ENTERED','CLOSE_UNKNOWN','CLOSE_RETURNED'):
            close_entered=True
            try:lease.close()
            except BaseException as error:failure.close_failure(error)
        elif lease is not None and acquire_entered and lease.fd is None:
            failure.unknown=True
        if loader is not None:
            try:
                loader.cleanup_transports_once(loaded)
                cleanup=loader.cleanup_disposition(loaded)
                if not cleanup['known_closed']:failure.unknown=True
            except BaseException as error:failure.close_failure(error)
        try:end=time.monotonic_ns()
        except BaseException as error:failure.remember(error)
    known_cleanup=(not failure.unknown and close_entered and
                   lease is not None and lease.phase=='CLOSE_RETURNED' and
                   cleanup is not None and cleanup.get('known_closed') is True)
    if failure.first is not None or not known_cleanup:classification='STOP_UNCERTAIN'
    receipt={'schema':'acquisition-observation-v30','profile':profile,'pid':os.getpid(),
        'uid':os.getuid(),'classification':classification,'last_stage':stage,
        'head_fact':fact,'missing_component':missing_component,
        'head_absence_is_not_orphan_or_debt_absence':True,'expected_head_pin':expected_head,
        'snapshot':snapshot if classification=='VALID_CLOSED_PREDECESSOR' else None,
        'read_domain':read_domain,'actual_selected_EX_observations':lease_observations,
        'acquire_entered':acquire_entered,'close_entered_once':close_entered,
        'lease_terminal_phase':None if lease is None else lease.phase,
        'cleanup_known':known_cleanup,'io_unknown':failure.unknown,
        'error':None if failure.first is None else type(failure.first).__name__,
        'secondary_errors':[type(e).__name__ for e in failure.secondary],
        'error_errno':failure.first.errno if isinstance(failure.first,OSError) and
            type(failure.first.errno) is int else None,
        'error_code':failure.first.args[0] if failure.first is not None and
            type(failure.first.args) is tuple and failure.first.args and
            type(failure.first.args[0]) is str and len(failure.first.args[0])<=256 else None,
        'original_exception_objects_retained':True,'begin_ns':begin,'end_ns':end,
        'prepare_enabled':False,'dispatch_enabled':False,'financial_records_created':0,
        'snapshot_is_not_continuing_lease':True,'positive_owner_qualification':
            classification=='VALID_CLOSED_PREDECESSOR' and known_cleanup,
        'normal_negative_is_not_optimized_permission':True,'physical_boundary':'OPEN_NOT_ZERO',
        'execution_permission':False,'original_S0603_complete':False,'all_costs_settled':False}
    raw=canonical(receipt);need(len(raw)<=RECEIPT_CAP,'DRIVER:RECEIPT_CAP')
    at=0
    while at<len(raw):
        n=os.write(1,raw[at:at+65536]);need(type(n) is int and 0<n<=min(65536,len(raw)-at),
                                       'DRIVER:RECEIPT_WRITE');at+=n
    os.fsync(1)
    return 0 if classification=='VALID_CLOSED_PREDECESSOR' and known_cleanup else 78


if __name__=='__main__':
    need(len(sys.argv)==5 and sys.argv[1]=='BOOTSTRAP','DRIVER:BOOTSTRAP_ONLY')
    profile,self_sha,self_bytes=sys.argv[2:]
    failure=FailureState();RETAINED.append(failure)
    need(Path(__file__)==DRIVER,'DRIVER:FIXED_SOURCE_SUBJECT')
    _source(DRIVER,{'bytes':int(self_bytes),'sha256':self_sha},failure)
    sys.exit(run_bootstrap(profile))
