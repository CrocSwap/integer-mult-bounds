"""Conditional Unit06 authenticated entry. No original project imports at load.

T0 is the original trusted first-launcher/OS/interpreter/system-stdlib premise.
Source selection does not create source, native, C05/C07, funding or runtime
admission. Do not call main except in a separately admitted genuine instance.
"""
from __future__ import annotations
import ast
import builtins
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import types

FILE_CAP=64*1024*1024
TOTAL_CAP=256*1024*1024
RECORD_CAP=1024*1024
MAX_ROWS=8192
IDENTITY_KEYS=('device','inode','mode','links','uid','gid','size','mtime_ns','ctime_ns')
ENV={'PATH':'/usr/bin:/bin','PYTHONHASHSEED':'0','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
SYSTEM_PATH=('/usr/lib/python312.zip','/usr/lib/python3.12','/usr/lib/python3.12/lib-dynload')


class Stop(RuntimeError):pass


def need(condition,message):
    if condition is not True:raise Stop(message)


def plain(value):
    nodes=text=0
    def walk(item,depth):
        nonlocal nodes,text
        nodes+=1
        need(depth<=24 and nodes<=65536,'plain structure bound')
        kind=type(item)
        if item is None or kind is bool:return
        if kind is int:need(-(1<<127)<=item<(1<<127),'integer bound');return
        if kind is str:
            text+=len(item);need(len(item)<=8192 and text<=524288,'text bound');return
        need(kind is list or kind is dict,'exact plain value required')
        need(len(item)<=MAX_ROWS,'container bound')
        if kind is list:
            for child in item:walk(child,depth+1)
        else:
            for key,child in item.items():
                need(type(key) is str,'exact string key required');walk(key,depth+1);walk(child,depth+1)
    walk(value,0)


def canonical(value,cap=RECORD_CAP):
    need(type(cap) is int and 0<=cap<=FILE_CAP,'exact record cap')
    plain(value)
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
    need(len(raw)<=cap,'canonical record cap');return raw


def decode(raw,cap=RECORD_CAP):
    need(type(cap) is int and 0<=cap<=FILE_CAP,'exact decode cap')
    need(type(raw) is bytes and len(raw)<=cap,'raw record cap/type')
    def pairs(rows):
        result={}
        for key,value in rows:
            need(key not in result,'duplicate JSON key');result[key]=value
        return result
    def bad(token):raise Stop('non-integer JSON number')
    value=json.loads(raw,object_pairs_hook=pairs,parse_float=bad,parse_constant=bad)
    plain(value);return value


def path_text(value):
    need(type(value) is str and 1<len(value)<=4096 and value.startswith('/') and all(32<=ord(c)<127 for c in value),'absolute bounded printable ASCII path required')
    need(len(value.split('/'))-1<=64,'path component bound')
    need(all(part not in ('','.','..') for part in value.split('/')[1:]),'canonical path spelling required')
    return value


def identity(info):
    return dict(zip(IDENTITY_KEYS,(info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_uid,info.st_gid,info.st_size,info.st_mtime_ns,info.st_ctime_ns)))


def validate_blob(pin,cap=FILE_CAP):
    need(type(cap) is int and 0<=cap<=FILE_CAP,'exact blob cap')
    need(type(pin) is dict and all(type(k) is str for k in pin),'exact blob map')
    need(set(pin)=={'path','sha256','bytes','identity'},'exact blob fields')
    path_text(pin['path'])
    digest=pin['sha256'];need(type(digest) is str and len(digest)==64 and all(c in '0123456789abcdef' for c in digest),'digest shape')
    need(type(pin['bytes']) is int and 0<=pin['bytes']<=cap,'blob byte bound')
    row=pin['identity'];need(type(row) is dict and all(type(k) is str for k in row) and set(row)==set(IDENTITY_KEYS),'identity fields')
    need(all(type(row[k]) is int and 0<=row[k]<(1<<127) for k in IDENTITY_KEYS),'identity integer fields')
    need(row['inode']>0 and row['size']==pin['bytes'] and stat.S_ISREG(row['mode']) and row['links']==1,'regular single-link identity')


class Owner:
    """New T0-side retained failure state, never an original capability."""
    def __init__(self):
        self.primary=None;self.secondary=[];self.pending=False;self.quarantined=False
        self.busy=False;self.burned=False;self.fd_slots=[];self.captures=[];self.total_bytes=0
        self.last_block=None;self.last_raw=None;self.modules={};self.published=[];self.executed=[]
        self.phase='NEW';self.result=None
    def ready(self):
        if self.primary is not None:raise self.primary
        need(not self.quarantined and not self.pending and not self.busy,'owner terminal/uncertain')
    def fail(self,error):
        if self.primary is None:self.primary=error
        elif error is not self.primary:self.secondary.append(error)
        self.quarantined=True
        return self.primary


def _retained_read(path,expected_sha256,cap,owner,expected_pin=None):
    """Actual descriptor-bound read. Returned source bytes are never reopened for exec."""
    need(type(owner) is Owner,'actual local owner required');owner.ready();path_text(path)
    need(type(cap) is int and 0<=cap<=FILE_CAP,'read cap')
    if expected_sha256 is not None:
        need(type(expected_sha256) is str and len(expected_sha256)==64 and all(c in '0123456789abcdef' for c in expected_sha256),'prior digest')
    if expected_pin is not None:validate_blob(expected_pin,cap);need(expected_pin['path']==path and expected_pin['sha256']==expected_sha256,'prior pin path/digest')
    record={'path':path,'chunks':[],'raw':None,'observed':None};owner.captures.append(record)
    owner.fd_slots.append(None);slot=len(owner.fd_slots)-1;primary=None;owner.busy=True
    try:
        before=identity(os.stat(path,follow_symlinks=False))
        need(stat.S_ISREG(before['mode']) and before['links']==1 and before['size']<=cap,'source kind/link/size')
        owner.pending=True
        owner.fd_slots[slot]=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
        owner.pending=False
        opened=identity(os.fstat(owner.fd_slots[slot]));need(before==opened,'source open drift')
        if expected_pin is not None:need(opened==expected_pin['identity'],'source installed identity differs')
        count=0
        while count<opened['size']:
            owner.last_block=os.read(owner.fd_slots[slot],min(65536,opened['size']-count))
            need(type(owner.last_block) is bytes and bool(owner.last_block),'short source read')
            count+=len(owner.last_block);owner.total_bytes+=len(owner.last_block)
            need(count<=cap and owner.total_bytes<=TOTAL_CAP,'retained aggregate byte cap')
            record['chunks'].append(owner.last_block)
        owner.last_raw=b''.join(record['chunks']);record['raw']=owner.last_raw
        after_fd=identity(os.fstat(owner.fd_slots[slot]));after_path=identity(os.stat(path,follow_symlinks=False))
        row={'path':path,'sha256':hashlib.sha256(record['raw']).hexdigest(),'bytes':count,'identity':after_fd}
        record['observed']=row
        need(opened==after_fd==after_path and count==opened['size'],'source read/path drift')
        need(expected_sha256 is None or row['sha256']==expected_sha256,'source prior digest differs')
        if expected_pin is not None:need(row==expected_pin,'source complete installed pin differs')
        return row,record['raw']
    except BaseException as error:
        primary=owner.fail(error);raise primary
    finally:
        fd=owner.fd_slots[slot];owner.fd_slots[slot]=None
        if fd is not None:
            try:os.close(fd)
            except BaseException as error:
                retained=owner.fail(error)
                if primary is None:raise retained
        owner.busy=False


def retained_read(path,expected_sha256,cap,owner,expected_pin=None):
    need(type(expected_sha256) is str and len(expected_sha256)==64 and all(c in '0123456789abcdef' for c in expected_sha256),'prior digest required')
    return _retained_read(path,expected_sha256,cap,owner,expected_pin)


def retain_regular(pin,cap,owner):
    validate_blob(pin,cap)
    return retained_read(pin['path'],pin['sha256'],cap,owner,pin)


def observe_regular(path,cap,owner):
    """Observe installed bytes/identity; this does not approve their source."""
    return _retained_read(path,None,cap,owner)


def write_exclusive(path,raw,mode,owner):
    need(type(owner) is Owner,'actual local owner required');owner.ready();path_text(path)
    need(type(raw) is bytes and len(raw)<=FILE_CAP and type(mode) is int and 0<=mode<=0o7777,'exclusive output bounds')
    owner.fd_slots.append(None);slot=len(owner.fd_slots)-1;primary=None;owner.busy=True
    try:
        owner.pending=True
        owner.fd_slots[slot]=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        owner.pending=False
        offset=0
        while offset<len(raw):
            count=os.write(owner.fd_slots[slot],raw[offset:]);need(type(count) is int and 0<count<=len(raw)-offset,'write progress');offset+=count
        os.fchmod(owner.fd_slots[slot],mode);os.fsync(owner.fd_slots[slot])
    except BaseException as error:
        primary=owner.fail(error);raise primary
    finally:
        fd=owner.fd_slots[slot];owner.fd_slots[slot]=None
        if fd is not None:
            try:os.close(fd)
            except BaseException as error:
                retained=owner.fail(error)
                if primary is None:raise retained
        owner.busy=False
    return observe_regular(path,FILE_CAP,owner)[0]

# UNIT06_T0_SUPPORT_END

# Exact original ea4 wrapper source follows; only main is adapted.
"""Same-process subreaper wrapper around byte-unchanged reviewed queue v4.

The actual consumer is this wrapper plus its explicitly narrow subprocess alias
proxy and supervisor. The queue's calling environment is deliberately extended;
its original bytes and real root status/stdout/stderr remain independently pinned.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

def source_packet(expected):
    here = Path(__file__).resolve().parent
    manifest_path = here / 'SOURCE-READINESS.json'
    if manifest_path.is_symlink() or manifest_path.stat().st_mode & 0o222:
        raise RuntimeError('Concrete source manifest must be readonly')
    with manifest_path.open('rb') as stream:
        raw = stream.read(262145)
    if len(raw) > 262144 or hashlib.sha256(raw).hexdigest() != expected:
        raise RuntimeError('Parent-reviewed source manifest differs')
    manifest = json.loads(raw)
    blobs = {}
    for name, row in manifest['files'].items():
        if Path(name).name != name or name == 'SOURCE-READINESS.json':
            raise RuntimeError('Unsafe source packet member')
        path = here / name
        if path.is_symlink() or path.stat().st_mode & 0o222:
            raise RuntimeError('Parent must freeze the concrete source packet readonly')
        with path.open('rb') as stream:
            data = stream.read(262145)
        if len(data) > 262144 or len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise RuntimeError('Source packet member differs: ' + name)
        blobs[name] = data
    if blobs[Path(__file__).name] != Path(__file__).read_bytes():
        raise RuntimeError('Actual queue entry differs from frozen source packet')
    path = here / 'supervisor.py'
    spec = importlib.util.spec_from_file_location('h25_parent_supervisor', path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(blobs['supervisor.py'], str(path), 'exec'), module.__dict__)
    return module, manifest



class RootProxy:
    def __init__(self, supervisor, root, cases, evidence, policy, deadline):
        self.s, self.root, self.cases = supervisor, root, cases
        self.evidence, self.policy, self.deadline = evidence, policy, deadline
        self.next = 0
        self.records = []

    def run(self, command, **kwargs):
        s = self.s
        s.need(self.next < len(self.cases), 'Unregistered extra queue root command')
        case = self.cases[self.next]
        expected = ['/usr/bin/python3.12', *s.FLAGS, str(self.root / 'run_guarded_v3.py'),
                    case['stage'], case['job'], case['label']]
        s.need(command == expected and set(kwargs) == {'cwd', 'env', 'capture_output', 'timeout'} and
               kwargs['cwd'] == self.root and kwargs['env'] == s.ENV and
               kwargs['capture_output'] is True and kwargs['timeout'] == 190,
               'Queue subprocess alias call exceeded its exact reviewed interface')
        folder = self.evidence / case['label']
        result = s.run_root(self.root, case, folder, self.policy['root_seconds'], self.deadline,
                            self.policy['root_address_space_bytes'], self.policy['root_rss_sum_bytes'])
        original_rc = result['returncode']
        receipt_path = self.root / 'runtime/runs' / case['label'] / 'receipt.json'
        if receipt_path.exists():
            root_receipt, root_pin = s.read_json(receipt_path, 4 * 1024 * 1024)
        else:
            root_receipt, root_pin = {'status': 'ABSENT_UNCLOSED_ROOT'}, None
        failure = result['failure']
        if original_rc == 0 and (result['cleanup']['observed_after_root_exit'] or
                                 result['cleanup']['reaped_adopted']):
            failure = failure or {'type': 'OrphanAfterApparentPass',
                                  'message': 'Original root exit 0 retained; supervisor admission STOP'}
        if not result['cleanup']['complete']:
            failure = failure or {'type': 'CleanupIncomplete', 'message': 'Owned process groups not empty'}
        originals = {'root_returncode': original_rc, 'root_status': root_receipt['status'],
                     'root_receipt_pin': root_pin, 'root_stdout': result['outer_logs']['root.stdout.raw'],
                     'root_stderr': result['outer_logs']['root.stderr.raw']}
        row = {'label': case['label'], 'actual_consumer': 'wrapper+module-alias-proxy+supervisor+queue-v4',
               'original': originals, 'effective_admission': 'STOP' if failure else 'DEFER_TO_QUEUE_V4',
               'supervision_failure': failure, 'original_root_receipt_unchanged': True,
               'cleanup_before_queue_validation': True}
        s.write_new(folder / 'PROXY.json', row)
        self.records.append(row)
        if failure:
            s.stop_supplement(self.root, case['label'], failure)
            raise RuntimeError('Root supervision rejected case; original status retained: ' + case['label'])
        stdout_record, stdout = s.stable_file(folder / 'root.stdout.raw', s.LOG_CAP, True)
        stderr_record, stderr = s.stable_file(folder / 'root.stderr.raw', s.LOG_CAP, True)
        s.need(stdout_record == originals['root_stdout'] and stderr_record == originals['root_stderr'],
               'Original root command streams changed before queue consumption')
        self.next += 1
        return subprocess.CompletedProcess(command, original_rc, stdout, stderr)


# Unit06 caller additions. Expected pins originate in the independently admitted
# --selection bytes/hash, never in observed candidate data. T0 authenticates this
# actual caller before its first body; none of these checks create that premise.
CALLER_QUEUE_SHA='1348a7b4d7cc1f9fef556f5e0abdaf04411a998afdcd574d7812c76ab37dcf68'
CALLER_RUNNER_SHA='bd882e3dadb1b6aeaa63ee824f1a1c58f8ef2546b6840a2bffa46885a184d3eb'
CALLER_SUPERVISOR_SHA='cfb09a18dd10b597cc6d5a8139ee769bef679bc44ae029329755e3d97b055075'
CALLER_KEYS={'schema','root','config','policy','source_packet','entry','stages','queue_sha256','runner_sha256'}
CALLER_STAGE_KEYS={'stage','manifest','entry','bootstrap','jobs','excluded_stage_manifests'}
CALLER_FALSE_FIELDS=('production_completion','full_c05','full_v03','runtime_qualified','enclosing_parent_exit_observed')
_CALLER_ADMISSION=None
_CALLER_FAILURE_OWNER=None


def _caller_simple(value):
    need(type(value) is str and 0<len(value)<=128 and
         all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in value),'simple caller identity')
    return value


def _caller_pin(pin,path,owner,cap=FILE_CAP):
    validate_blob(pin,cap)
    need(pin['path']==path,'prior selected path differs')
    return retain_regular(pin,cap,owner)


def _caller_source_packet(selection,owner):
    here=Path(__file__).resolve().parent
    _,raw=_caller_pin(selection['source_packet'],str(here/'SOURCE-READINESS.json'),owner,262144)
    manifest=decode(raw,262144)
    need(type(manifest) is dict and type(manifest.get('files')) is dict and
         1<=len(manifest['files'])<=128,'source packet shape/count')
    files=manifest['files']
    need(Path(__file__).name in files and 'supervisor.py' in files,'actual caller/supervisor packet members')
    for name,row in files.items():
        need(type(name) is str and name not in ('','SOURCE-READINESS.json') and
             Path(name).name==name and len(name)<=128 and all(32<=ord(c)<127 for c in name),'source member name')
        need(type(row) is dict and type(row.get('bytes')) is int and 0<=row['bytes']<=262144 and
             type(row.get('sha256')) is str,'source member pin shape')
        pin,data=retained_read(str(here/name),row['sha256'],262144,owner)
        need(pin['bytes']==row['bytes'] and not pin['identity']['mode']&0o222,'source member byte/mode differs')
    need(files['supervisor.py']['sha256']==CALLER_SUPERVISOR_SHA,'actual original supervisor differs')
    need(not selection['source_packet']['identity']['mode']&0o222,'source packet must be readonly')
    return manifest


def _caller_inventory(stage,declared,excluded,owner,state):
    need(type(declared) is dict and type(declared.get('files')) is dict and
         1<=len(declared['files'])<=8192,'runner inventory declaration')
    expected=declared['files'];actual={};outer={};stack=[stage];count=0
    for pin in excluded:
        validate_blob(pin,RECORD_CAP)
        need(pin['path'] not in outer and Path(pin['path']).name=='STAGE.json' and
             Path(pin['path']).is_relative_to(stage) and pin['path']!=str(stage/'STAGE.json'),'excluded manifest path')
        outer[pin['path']]=pin
    seen_outer=set()
    while stack:
        directory=stack.pop();before=identity(os.stat(directory,follow_symlinks=False))
        need(stat.S_ISDIR(before['mode']),'stage directory required')
        record={'path':str(directory),'handle':None,'closed':False};state['directory_scans'].append(record)
        primary=None
        try:
            owner.pending=True;record['handle']=os.scandir(directory);owner.pending=False
            for item in record['handle']:
                count+=1;need(count<=16384,'original stage entry bound')
                path=Path(item.path);relative=path.relative_to(stage).as_posix();path_text(str(path))
                need(len(path.relative_to(stage).parts)<=24,'stage inventory depth bound')
                observed=identity(item.stat(follow_symlinks=False))
                need(not stat.S_ISLNK(observed['mode']),'symlink in admitted stage')
                if stat.S_ISDIR(observed['mode']):stack.append(path);continue
                need(stat.S_ISREG(observed['mode']),'nonregular stage entry')
                if item.name=='STAGE.json':
                    if path==stage/'STAGE.json':continue
                    need(str(path) in outer,'unexpected excluded nested STAGE.json')
                    retain_regular(outer[str(path)],RECORD_CAP,owner);seen_outer.add(str(path));continue
                need(relative in expected and type(expected[relative]) is dict and
                     set(expected[relative])=={'sha256','mode'},'unselected stage file/row')
                row=expected[relative]
                need(type(row['mode']) is int and 0<=row['mode']<=0o777,'runner mode field')
                pin,raw=retained_read(str(path),row['sha256'],FILE_CAP,owner)
                need(pin['identity']['mode']&0o777==row['mode'],'runner stage mode differs')
                actual[relative]={'sha256':pin['sha256'],'mode':pin['identity']['mode']&0o777}
            need(before==identity(os.stat(directory,follow_symlinks=False)),'stage directory drift')
        except BaseException as error:
            primary=owner.fail(error);raise primary
        finally:
            handle=record['handle'];record['handle']=None;record['closed']=True
            if handle is not None:
                try:handle.close()
                except BaseException as error:
                    retained=owner.fail(error)
                    if primary is None:raise retained
    need(actual==expected and seen_outer==set(outer),'full runner stage inventory differs')
    state['inventory_observations'].append({'stage':str(stage),'entries':count,'files':len(actual),'excluded_manifests':len(seen_outer)+1})
    return actual


def _caller_stage(row,root,owner,state):
    need(type(row) is dict and set(row)==CALLER_STAGE_KEYS,'exact stage selection')
    name=_caller_simple(row['stage']);stage=root/'stages'/name
    need(type(row['excluded_stage_manifests']) is list and len(row['excluded_stage_manifests'])<=128,'excluded manifest bound')
    _,raw=_caller_pin(row['manifest'],str(stage/'STAGE.json'),owner,RECORD_CAP)
    declared=decode(raw,RECORD_CAP)
    need(declared.get('runner_sha256')==CALLER_RUNNER_SHA,'approved stage runner differs')
    inventory=_caller_inventory(stage,declared,row['excluded_stage_manifests'],owner,state)
    _,entry_raw=_caller_pin(row['entry'],str(stage/'integration/predecessor_entry.py'),owner)
    _,bootstrap_raw=_caller_pin(row['bootstrap'],str(stage/'integration/PREFIX-BOOTSTRAP.json'),owner,RECORD_CAP)
    _,jobs_raw=_caller_pin(row['jobs'],str(stage/'JOBS.json'),owner,RECORD_CAP)
    for key in ('entry','bootstrap','jobs'):
        pin=row[key];relative=Path(pin['path']).relative_to(stage).as_posix()
        need(relative in inventory and inventory[relative]['sha256']==pin['sha256'] and
             inventory[relative]['mode']==pin['identity']['mode']&0o777,'prior B/M/JOBS not inventoried')
    need(row['entry']['sha256']==state['selection']['entry']['sha256'] and
         row['entry']['bytes']==state['selection']['entry']['bytes'],'generic entry prior selection differs')
    # M is authenticated data here; the independently reviewed entry validates its
    # full schema/argv/output/gates. The caller does not invent those approvals.
    jobs=decode(jobs_raw,RECORD_CAP)
    need(type(jobs) is dict and 1<=len(jobs)<=256,'actual JOBS map')
    _,again=_caller_pin(row['manifest'],str(stage/'STAGE.json'),owner,RECORD_CAP)
    need(again==raw,'approved STAGE changed through inventory')
    return {'selection':row,'manifest':declared,'jobs':jobs,'bootstrap_raw':bootstrap_raw,'entry_raw':entry_raw}


def _caller_case(case,stages):
    need(type(case) is dict and type(case.get('stage')) is str and case['stage'] in stages,'selected queue stage')
    selected=stages[case['stage']];row=selected['selection']
    need(case.get('stage_sha256')==row['manifest']['sha256'],'case prior stage digest differs')
    jobname=_caller_simple(case.get('job'));_caller_simple(case.get('label'))
    need(jobname in selected['jobs'],'actual selected JOBS member missing')
    job=selected['jobs'][jobname]
    need(type(job) is dict and job.get('entry')=='integration/predecessor_entry.py' and
         'bootstrap' not in job and type(job.get('lanes')) is str and 0<len(job['lanes'])<=8192 and
         type(job.get('optimized',False)) is bool and type(job.get('finite_only',False)) is bool,'actual runner entry argv selection')
    need(case.get('science_status')=='PREFIX_OBSERVATION_DATA' and
         type(case.get('science_fields')) is dict and
         all(key in case['science_fields'] and case['science_fields'][key] is False for key in CALLER_FALSE_FIELDS),
         'queue must select the explicit nonqualifying DATA receipt')


def _caller_recheck(state,case=None):
    owner=state['owner'];owner.ready();selection=state['selection'];root=Path(selection['root'])
    try:
        _,raw=retained_read(state['selection_path'],state['selection_sha256'],RECORD_CAP,owner,state['selection_pin'])
        need(raw==state['selection_raw'],'prior selection changed')
        for key in ('config','policy','entry'):retain_regular(selection[key],FILE_CAP,owner)
        _caller_source_packet(selection,owner)
        retained_read(str(root/'run_guarded_v3.py'),CALLER_RUNNER_SHA,FILE_CAP,owner)
        retained_read(str(root/'integration/run_reviewed_queue_v4.py'),CALLER_QUEUE_SHA,FILE_CAP,owner)
        wanted=state['stage_rows'] if case is None else [state['stage_rows_by_name'][case['stage']]]
        for row in wanted:
            stage=_caller_stage(row,root,owner,state)
            if case is not None:_caller_case(case,{row['stage']:stage})
        state['rechecks']+=1
    except BaseException as error:raise owner.fail(error)


def _caller_admit(args):
    global _CALLER_ADMISSION,_CALLER_FAILURE_OWNER
    need(_CALLER_ADMISSION is None and _CALLER_FAILURE_OWNER is None,'one caller bootstrap attempt')
    owner=Owner();owner.burned=True;_CALLER_FAILURE_OWNER=owner
    state={'owner':owner,'selection_path':str(args.selection),'selection_sha256':args.selection_sha256,
           'directory_scans':[],'inventory_observations':[],'rechecks':0}
    _CALLER_ADMISSION=state
    try:
        pin,raw=retained_read(str(args.selection),args.selection_sha256,RECORD_CAP,owner)
        state['selection_pin']=pin;state['selection_raw']=raw;selection=decode(raw,RECORD_CAP)
        need(type(selection) is dict and set(selection)==CALLER_KEYS and
             selection['schema']=='unit06-prior-caller-selection-v1','prior caller selection schema')
        state['selection']=selection;path_text(selection['root']);root=Path(selection['root'])
        need(str(args.root)==selection['root'] and root.resolve()==root,'actual canonical original root selection')
        need(selection['queue_sha256']==CALLER_QUEUE_SHA and selection['runner_sha256']==CALLER_RUNNER_SHA,'actual queue/runner prior pins')
        for key,arg in (('config',args.config),('policy',args.policy)):
            need(str(arg)==selection[key]['path'] and Path(str(arg)).is_relative_to(root/'control'),'actual control selection')
        _,config_raw=retain_regular(selection['config'],RECORD_CAP,owner)
        retain_regular(selection['policy'],RECORD_CAP,owner);retain_regular(selection['entry'],FILE_CAP,owner)
        need(args.source_sha256==selection['source_packet']['sha256'],'actual source packet prior digest')
        _caller_source_packet(selection,owner)
        retained_read(str(root/'run_guarded_v3.py'),CALLER_RUNNER_SHA,FILE_CAP,owner)
        retained_read(str(root/'integration/run_reviewed_queue_v4.py'),CALLER_QUEUE_SHA,FILE_CAP,owner)
        rows=selection['stages'];need(type(rows) is list and 1<=len(rows)<=256,'selected stage count')
        state['stage_rows']=rows;state['stage_rows_by_name']={};stages={}
        for row in rows:
            selected=_caller_stage(row,root,owner,state);name=row['stage']
            need(name not in stages,'duplicate selected stage');stages[name]=selected;state['stage_rows_by_name'][name]=row
        config=decode(config_raw,RECORD_CAP)
        need(type(config) is dict and type(config.get('cases')) is list and 1<=len(config['cases'])<=256,'actual selected queue cases')
        need(set(stages)=={case['stage'] for case in config['cases']},'unmatched selected stages')
        labels=set()
        for case in config['cases']:
            _caller_case(case,stages);need(case['label'] not in labels,'duplicate queue label');labels.add(case['label'])
        state['config_raw']=config_raw;state['phase']='PRIOR_SELECTION_CHECKED'
        return state
    except BaseException as error:raise owner.fail(error)


class PriorAdmittedRootProxy(RootProxy):
    """Additional actual prior check before the unchanged RootProxy.run body."""
    def run(self,command,**kwargs):
        need(type(self.next) is int and 0<=self.next<len(self.cases),'selected proxy dispatch')
        _caller_recheck(_CALLER_ADMISSION,self.cases[self.next])
        return super().run(command,**kwargs)


def main():
    began = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--source-sha256', required=True)
    parser.add_argument('--selection', type=Path, required=True)
    parser.add_argument('--selection-sha256', required=True)
    args = parser.parse_args()
    admission = _caller_admit(args)
    s, source_manifest = source_packet(args.source_sha256)
    s.launch_contract()
    root = args.root.resolve()
    config_path, policy_path = args.config.resolve(), args.policy.resolve()
    s.need(config_path.is_relative_to(root / 'control') and policy_path.is_relative_to(root / 'control'),
           'Config and policy must be frozen round controls')
    config, config_pin = s.read_json(config_path)
    policy, policy_pin = s.read_json(policy_path)
    s.need(set(policy) == {'queue', 'shared_seconds', 'root_seconds', 'root_address_space_bytes', 'root_rss_sum_bytes'},
           'Exact supervisor policy shape required')
    name = config['queue']
    s.need(type(name) is str and name.isalnum() and policy['queue'] == name, 'Queue policy identity differs')
    s.need(type(policy['shared_seconds']) in (int, float) and 0 < policy['shared_seconds'] <= 600 and
           type(policy['root_seconds']) in (int, float) and 0 < policy['root_seconds'] <= 190 and
           type(policy['root_address_space_bytes']) is int and 0 < policy['root_address_space_bytes'] <= 1024 ** 3 and
           type(policy['root_rss_sum_bytes']) is int and 0 < policy['root_rss_sum_bytes'] <= 1024 ** 3,
           'Unadmitted generic supervisor limits')
    evidence = root / 'validation/attempts' / (name + '-supervision')
    evidence.mkdir()
    lock = s.parent_lock(root)
    cap, initial = s.budget(root)
    deadline = min(began + policy['shared_seconds'], began + cap - sum(initial.values()))
    failure, proxy, keeper = None, None, None
    old_argv = sys.argv
    try:
        subreaper, keeper = s.install_subreaper(root)
        s.write_new(evidence / 'PARENT-SUBREAPER.json', subreaper)
        path = root / 'integration/run_reviewed_queue_v4.py'
        queue_pin, raw = s.stable_file(path, s.META_CAP, True)
        s.need(queue_pin['sha256'] == s.QUEUE_SHA, 'Original reviewed queue-v4 bytes changed')
        spec = importlib.util.spec_from_file_location('h25_original_queue_v4', path)
        queue = importlib.util.module_from_spec(spec)
        exec(compile(raw, str(path), 'exec'), queue.__dict__)
        s.need(queue.ROOT == root and queue.subprocess is subprocess, 'Unexpected queue module binding')
        proxy = PriorAdmittedRootProxy(s, root, config['cases'], evidence, policy, deadline)
        # Only this authenticated module's alias changes. The stdlib module is intact.
        queue.subprocess = proxy
        sys.argv = [str(path), str(config_path)]
        queue.main()
        s.need(proxy.next == len(config['cases']), 'Queue omitted a registered root call')
        s.need(not s.children_now(), 'Wrapper finished with children still present')
        s.need(s.stable_file(config_path, s.META_CAP)['sha256'] == config_pin['sha256'] and
               s.stable_file(policy_path, s.META_CAP)['sha256'] == policy_pin['sha256'], 'Control policy changed')
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error)[:2048]}
        raise
    finally:
        sys.argv = old_argv
        try:
            _caller_recheck(admission)
            s.packet_unchanged(Path(__file__).resolve().parent, source_manifest)
        except BaseException as error:
            failure = failure or {'type': type(error).__name__, 'message': str(error)[:2048]}
        elapsed = time.monotonic() - began
        current = s.ledger(root, allow_unclosed=True)
        s.need(all(current.get(k) == v for k, v in initial.items()), 'Prior cost records changed')
        nested = sum(v for k, v in current.items() if k not in initial)
        residual = max(0.0, elapsed - nested)
        if time.monotonic() > deadline:
            failure = failure or {'type': 'SupervisorBudget', 'message': 'Full wrapper bound crossed; cleanup remains charged'}
        result = {'schema': 'h25-queue-v4-supervisor-envelope-v1', 'queue': name,
                  'status': 'STOP' if failure else 'SUPERVISED_QUEUE_V4_COMPLETE', 'failure': failure,
                  'actual_consumer': 'wrapper+module-alias-proxy+supervisor+queue-v4',
                  'original_queue_sha256': s.QUEUE_SHA, 'original_root_sha256': s.RUNNER_SHA,
                  'source_manifest_sha256': args.source_sha256, 'config_pin': config_pin, 'policy_pin': policy_pin,
                  'controls': [] if proxy is None else proxy.records,
                  'prior_selection_sha256': args.selection_sha256,
                  'new_caller_retained_read_bytes': admission['owner'].total_bytes,
                  'new_caller_rechecks': admission['rechecks'],
                  'startup_authentication_in_original_began_budget': True,
                  'C05_V03_runtime_admission_added': False,
                  'complete_wrapper_seconds_before_own_receipt': elapsed,
                  'nested_queue_and_root_seconds': nested, 'wrapper_residual_seconds': residual,
                  'outer_GNU_time_final_tail_reconciliation_required': True,
                  'subreaper_is_same_queue_process': True, 'original_root_receipts_preserved': True}
        folder = root / 'runtime/runs' / (name + '-supervisor-overhead')
        folder.mkdir()
        s.write_new(folder / 'START.json', {'kind': 'parent_cost_only'})
        s.write_new(folder / 'receipt.json', dict(result, label=folder.name, kind='parent_cost_only',
                    wall_seconds=residual, runner_wall_seconds=residual))
        s.write_new(evidence / 'WRAPPER.json', result)
        lock.close()
    if failure:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
