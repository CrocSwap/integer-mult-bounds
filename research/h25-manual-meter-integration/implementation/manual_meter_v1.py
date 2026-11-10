"""SOURCE ONLY fixed same-process manual financial producer; no command grant.

Adapted from two_group_meter.py e1084f4c61228c064ffce1e2cd2488fda0128d00661e60da451596b0a4c4cb1d.
Retains predecessor START/BODY schemas, run-entry clock, FD1 identity and sealing
rules, bounded IO slots and no-close-retry discipline. Child-group dispatch is
replaced by actual A4 initializer or distinct-target closer calls under C2 EX.

Body interval starts at run entry, after interpreter/import/argument startup.
It ends after actual child wait, raw validation and owned-descriptor cleanup.
Startup and final record projection/write/fsync/exit lie outside that interval.
The separately named two-second administrative debit is NOT measured duration,
a physical upper bound or proof of the 2400-second physical total. The physical
publication boundary remains open. No historical timing gap is reconstructed.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import stat
import shlex
import sys
import time
import builtins
from types import ModuleType

W = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
ROOT = W / 'outputs/h25-data-handling-20261028'
PACKAGE = ROOT / 'areas/manual-integration-v29'
LOADER_PATH = PACKAGE / 'manual_loader_v1.py'
# Literal complete selected loader pin is inserted at source freeze.
LOADER_PIN = {'bytes':18257,'sha256':'0e81529af2bf0c56863372379da1aafc4c4f762982d79df7282b2b2cd23e0620'}
USED, RETAINED, BODY_ATTEMPTED = [False], [], [False]
ENV = {'PATH':'/usr/bin:/bin','PYTHONHASHSEED':'0','LANG':'C.UTF-8',
       'LC_ALL':'C.UTF-8','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
FLAGS = ('-S','-s','-P','-B')
INITIAL_PATH = ('/usr/lib/python312.zip','/usr/lib/python3.12','/usr/lib/python3.12/lib-dynload')
MEMORY, STREAM_CAP = 1073741824, 2097152
ADMIN_POLICY = 'startup-and-final-publication-two-second-administrative-debit-v1'
ADMIN_POLICY_DEBIT_SECONDS = 2
FIRST, SECONDARY, IO_UNKNOWN = [None], [None] * 32, [False]
SLOTS = [[None, 'FREE', None, False] for unused in range(32)]
START, END, ARMED = [None], [None], [False]
CHILD = [None]  # No child is created by this manual source path.
PEAK_SAMPLED_PARENT_CHILD_RSS = [None]
MARKER_PHASE = ['NOT_ENTERED']

class AdapterStop(RuntimeError):
    pass


def remember(error):
    if FIRST[0] is None:
        FIRST[0] = error
    elif error is not FIRST[0]:
        for index in range(32):
            if SECONDARY[index] is error:
                break
            if SECONDARY[index] is None:
                SECONDARY[index] = error
                break
        else:
            IO_UNKNOWN[0] = True
    return FIRST[0]


def need(value, message):
    if not value:
        raise AdapterStop(message)


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_uid, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def sha_value(value):
    need(type(value) is str and len(value) == 64 and
         all(c in '0123456789abcdef' for c in value), 'exact sha256 required')


def error_data():
    def item(error):
        if error is None:
            return None
        frames, tb = [], error.__traceback__
        while tb is not None and len(frames) < 32:
            frames.append({'file': tb.tb_frame.f_code.co_filename, 'line': tb.tb_lineno,
                           'function': tb.tb_frame.f_code.co_name})
            tb = tb.tb_next
        return {'type': type(error).__name__, 'frames': frames}
    return {'first': item(FIRST[0]), 'secondary': [item(e) for e in SECONDARY if e is not None],
            'IO_unknown': IO_UNKNOWN[0], 'actual_exception_objects_retained_until_exit': True}


def acquire(path, flags=0, directory=False):
    need(not IO_UNKNOWN[0], 'unknown IO blocks new acquisition')
    slot = next(s for s in SLOTS if s[1] in ('FREE','CLOSED'))
    slot[:] = [None, 'PENDING', str(path), directory]
    try:
        slot[0] = os.scandir(path) if directory else os.open(path, flags | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        slot[1] = 'OWNED'
        return slot
    except BaseException as error:
        IO_UNKNOWN[0] = True
        remember(error)
        raise


def close(slot):
    need(slot[1] == 'OWNED', 'known owned close only; no retry')
    slot[1] = 'CLOSING'
    try:
        slot[0].close() if slot[3] else os.close(slot[0])
    except BaseException as error:
        slot[1] = 'CLOSE_UNKNOWN'
        IO_UNKNOWN[0] = True
        remember(error)
        raise
    slot[1] = 'CLOSED'


def names(path, cap):
    slot, values = acquire(path, directory=True), []
    try:
        for item in slot[0]:
            need(len(values) < cap, 'directory member cap')
            values.append(item.name)
    except BaseException as error:
        remember(error)
        raise
    finally:
        try:
            close(slot)
        except BaseException as secondary:
            remember(secondary)
    need(not IO_UNKNOWN[0], 'directory close unknown')
    return values


def read_fd(slot, cap, proc=False):
    before = os.fstat(slot[0])
    if not proc:
        need(stat.S_ISREG(before.st_mode) and before.st_uid in (0,os.getuid()) and
             before.st_nlink == 1 and before.st_size <= cap, 'stable regular owner/link/size')
        need(identity(Path(slot[2]).lstat()) == identity(before), 'descriptor/path differs')
        os.lseek(slot[0], 0, os.SEEK_SET)
    chunks, count = [], 0
    while True:
        block = os.read(slot[0], min(65536,cap + 1 - count))
        if not block:
            break
        chunks.append(block)
        count += len(block)
        need(count <= cap, 'read cap')
    raw = b''.join(chunks)
    if not proc:
        need(count == before.st_size and identity(os.fstat(slot[0])) == identity(before) ==
             identity(Path(slot[2]).lstat()), 'stable descriptor/path changed')
    return raw


def stable_source(path, expected):
    need(path.is_absolute() and path.resolve(strict=True) == path, 'canonical source path')
    before = path.lstat()
    need(stat.S_IMODE(before.st_mode) == 0o444, 'frozen source mode')
    slot = acquire(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        need(identity(before) == identity(os.fstat(slot[0])), 'source opened identity')
        raw = read_fd(slot, expected['bytes'])
        need(len(raw) == expected['bytes'] and hashlib.sha256(raw).hexdigest() == expected['sha256'], 'source pin')
    except BaseException as error:
        remember(error)
        raise
    finally:
        try:
            close(slot)
        except BaseException as secondary:
            remember(secondary)
    need(not IO_UNKNOWN[0], 'source close unknown')
    return raw


def metadata(path, cap=8192):
    slot = acquire(path, os.O_RDONLY | os.O_NONBLOCK)
    try:
        raw = read_fd(slot, cap, proc=True)
    except BaseException as error:
        remember(error)
        raise
    finally:
        try:
            close(slot)
        except BaseException as secondary:
            remember(secondary)
    need(not IO_UNKNOWN[0], 'metadata close unknown')
    return raw


def process(pid):
    raw = metadata('/proc/' + str(pid) + '/stat')
    end = raw.rfind(b') ')
    need(end >= 0 and raw.split(b' ',1)[0] == str(pid).encode('ascii'), 'process stat syntax/pid')
    fields = raw[end + 2:].split()
    return {'pid':pid,'ppid':int(fields[1]),'pgid':int(fields[2]),'sid':int(fields[3]),
            'start_ticks':int(fields[19]),'rss_bytes':int(fields[21])*os.sysconf('SC_PAGE_SIZE')}


def sample_memory(birth=None):
    parent = process(os.getpid())
    total = parent['rss_bytes']
    if birth is not None:
        current = process(CHILD[0].pid)  # Native child is still unreaped; no PID reuse.
        need(all(current[k] == birth[k] for k in ('pid','ppid','pgid','sid','start_ticks')),
             'owned child generation/session changed')
        total += current['rss_bytes']
    PEAK_SAMPLED_PARENT_CHILD_RSS[0] = total if PEAK_SAMPLED_PARENT_CHILD_RSS[0] is None else max(PEAK_SAMPLED_PARENT_CHILD_RSS[0],total)
    need(total <= MEMORY, 'sampled parent plus owned-child RSS cap')


def lower_limit(kind, ceiling):
    soft, hard = resource.getrlimit(kind)
    bound = min(ceiling,hard) if hard != resource.RLIM_INFINITY else ceiling
    if soft != resource.RLIM_INFINITY:
        bound = min(bound,soft)
    resource.setrlimit(kind,(bound,bound))


def strict_json(raw):
    def pairs(rows):
        value = {}
        for key,item in rows:
            need(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    def constant(value):
        raise AdapterStop('nonfinite JSON')
    return json.loads(raw.decode('ascii'),object_pairs_hook=pairs,parse_constant=constant)


def write_owned(slot, raw):
    need(type(raw) is bytes and len(raw) <= 65536, 'retained metadata cap')
    at = 0
    while at < len(raw):
        count = os.write(slot[0],raw[at:])
        need(type(count) is int and 0 < count <= len(raw)-at, 'owned write progress')
        at += count
    os.fsync(slot[0])


def fresh(path):
    need(path.parent.resolve(strict=True) == path.parent, 'canonical fresh parent')
    slot = acquire(path,os.O_RDWR | os.O_CREAT | os.O_EXCL)
    st = os.fstat(slot[0])
    need(stat.S_ISREG(st.st_mode) and st.st_uid == os.getuid() and st.st_nlink == 1 and
         stat.S_IMODE(st.st_mode) == 0o600 and st.st_size == 0, 'fresh exclusive0600 file')
    return slot


def sync_directory(path):
    slot = acquire(path,os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(slot[0])
    except BaseException as error:
        remember(error)
        raise
    finally:
        try:
            close(slot)
        except BaseException as secondary:
            remember(secondary)
    need(not IO_UNKNOWN[0], 'directory sync close unknown')

PLAN_KEYS = ('schema','attempt_id','profile','action','command_pin','reservation_pin',
    'permission_pin','pre_entry_pin','reserved_manifest_pin','predecessor_snapshot',
    'extra_wires','approved_opening','expected_head_pin','pending_path','policy_pins',
    'phase','phase_release_sha256','cleanup_ns','meter_source_pin')


def plan_shape(operation, action, profile):
    need(type(operation) is dict and set(operation)==set(PLAN_KEYS),'exact fixed manual operation DATA')
    need(operation['schema']=='fresh-fixed-manual-operation-v1' and
         type(operation['attempt_id']) is str and 1<=len(operation['attempt_id'])<=80 and
         all(c.isascii() and (c.isalnum() or c in '-_') for c in operation['attempt_id']),
         'one original bounded attempt label')
    need(type(profile) is str and profile in ('normal','optimized') and
         operation['profile']==profile and operation['action']==action and
         action in ('INITIALIZE','REFRESH','CLOSE'),'fixed literal action and exact mode')
    need(type(operation['cleanup_ns']) is int and 0<=operation['cleanup_ns']<=2_000_000_000,
         'fixed nonnegative cleanup allowance')
    need(operation['phase'] in ('INITIAL','FULL') and type(operation['policy_pins']) is list,
         'original phase and policy pins')
    return operation


def shell_command(action, profile, plan_path, meter_source_pin):
    """Pure exact command DATA shared with the fixed parent before PRE_ENTRY."""
    need(type(action) is str and action in ('INITIALIZE','REFRESH','CLOSE') and
         type(profile) is str and profile in ('normal','optimized'),'fixed command action/profile')
    flags = list(FLAGS) + (['-O'] if profile=='optimized' else [])
    args = ['/usr/bin/python3.12',*flags,str(PACKAGE/'manual_meter_v1.py'),action,profile,
            str(plan_path),meter_source_pin['sha256'],str(meter_source_pin['bytes'])]
    name = Path(plan_path).stem
    body = ROOT/'control/prospective-financial-v1/entries'/name/'METER_BODY.json'
    detail = ROOT/'runtime/manual-operations'/(name+'.stderr.json')
    env_args = ['/usr/bin/env','-i']+[key+'='+value for key,value in ENV.items()]
    command = ' '.join(shlex.quote(arg) for arg in env_args+args)
    return 'umask 077\nset -C\nexec '+command+' > '+shlex.quote(str(body))+' 2> '+shlex.quote(str(detail))


def _read_record(path, expected=None, cap=65536):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True)==path,'canonical original record path')
    slot = acquire(path,os.O_RDONLY|os.O_NONBLOCK)
    try:
        need(stat.S_IMODE(os.fstat(slot[0]).st_mode)==0o444,'sealed original record mode')
        raw = read_fd(slot,cap)
        if expected is not None:
            need(expected=={'path':str(path),'bytes':len(raw),
                'sha256':hashlib.sha256(raw).hexdigest(),'mode':0o444},'original full record pin')
    except BaseException as error:
        if FIRST[0] is None:
            FIRST[0] = error
        remember(error)
        raise
    finally:
        if slot[1]=='OWNED':
            try:
                close(slot)
            except BaseException as error:
                remember(error)
    need(not IO_UNKNOWN[0],'record close unknown')
    return raw


def _publish_original(pin, raw):
    need(type(raw) is bytes and pin=={'path':pin['path'],'bytes':len(raw),
         'sha256':hashlib.sha256(raw).hexdigest(),'mode':0o444},'exact new original pin')
    slot = fresh(Path(pin['path']))
    try:
        write_owned(slot,raw)
        need(read_fd(slot,65536)==raw,'full original readback before seal')
        os.fchmod(slot[0],0o444); os.fsync(slot[0])
        need(stat.S_IMODE(os.fstat(slot[0]).st_mode)==0o444 and
             read_fd(slot,65536)==raw,'sealed original full readback')
    except BaseException as error:
        if FIRST[0] is None:
            FIRST[0] = error
        remember(error)
        raise
    finally:
        if slot[1]=='OWNED':
            try:
                close(slot)
            except BaseException as error:
                remember(error)
    need(FIRST[0] is None and not IO_UNKNOWN[0],'original publication cleanup failed')
    sync_directory(Path(pin['path']).parent)


def _load_loader():
    name = 'h25_fixed_manual_loader_v1'
    need(name not in sys.modules,'one fixed loader namespace')
    raw = stable_source(LOADER_PATH,LOADER_PIN)
    module = ModuleType(name)
    module.__dict__.update(__file__=str(LOADER_PATH),__name__=name,__package__=None,
                           __spec__=None,__builtins__=builtins)
    sys.modules[name] = module
    RETAINED.append((module,raw))
    exec(compile(raw,str(LOADER_PATH),'exec',dont_inherit=True),module.__dict__)
    return module


def _binding(F, operation, candidate, start_pin, pending_pin, reservation, command):
    name = operation['attempt_id']
    request = {'schema':'fresh-round-request-v1','round_id':F.ROUND_ID,'label':name,
        'command_sha256':operation['command_pin']['sha256'],
        'body_reservation_ns':reservation['body_reservation_ns'],
        'policy_sha256':reservation['policy_adoption_pin']['sha256'],
        'phase_release_sha256':operation['phase_release_sha256']}
    provenance = {'schema':'fresh-original-preentry-provenance-v1','entry_id':name,
        'command_sha256':request['command_sha256'],
        'body_reservation_ns':request['body_reservation_ns'],
        'registration_pin':operation['reservation_pin'],'original_start_pin':start_pin,
        'pending_manifest_pin':pending_pin}
    return {'schema':'fresh-active-financial-manual-entry-binding-v1',
        'request':request,'provenance':provenance,'financial_opening_pin':candidate['opening_pin'],
        'financial_head_pin':operation['predecessor_snapshot']['head_pin'],
        'closed_state_pin':reservation['before_closed_state_pin'],
        'registration_checks':[{'path':['attempt_id'],'expected':name},
            {'path':['command_pin'],'expected':operation['command_pin']}],
        'start_checks':[{'path':['attempt_id'],'expected':name},
            {'path':['body_begin_ns'],'expected':START[0]}]}


def body_data(name, command_pin, reservation_pin, start_pin, begin, end,
              cleanup_known, io_unknown, peak_rss, first_name, secondary_names):
    """Pure projection; NO_CHILD is actual absence of child dispatch, not a wait."""
    known = type(begin) is int and type(end) is int and 0<=begin<=end
    return {'schema':'fresh-financial-meter-body-v1','attempt_id':name,
        'command_pin':command_pin,'reservation_pin':reservation_pin,'meter_start_pin':start_pin,
        'body':{'state':'KNOWN' if known else 'UNKNOWN','begin_ns':begin,
            'end_ns':end if known else None,'elapsed_ns':end-begin if known else None},
        'owned_cleanup':'KNOWN_CLOSED' if cleanup_known else 'UNKNOWN',
        'owned_wait':'NO_CHILD','child_exit':None,
        'resource_observations':{'peak_sampled_rss_bytes':peak_rss,'limit_bytes':MEMORY,'scope':'SAMPLED_ONLY'},
        'errors':{'first':first_name,'secondary':list(secondary_names),'io_unknown':io_unknown},
        'body_scope':'RUN_ENTRY_THROUGH_OWNED_CLEANUP_V1','physical_boundary':'OPEN_NOT_ZERO'}


def emit_fd1(raw):
    need(BODY_ATTEMPTED[0] is False,'one BODY publication attempt including partial failure')
    BODY_ATTEMPTED[0] = True
    need(type(raw) is bytes and len(raw)<=65536,'single original BODY cap')
    at = 0
    while at<len(raw):
        count = os.write(1,raw[at:])
        need(type(count) is int and 0<count<=len(raw)-at,'BODY write progress')
        at += count
    os.fsync(1)


def _snapshot_receipt(path, value):
    # Complete retained DATA may be larger than an original frame record.
    # This fixed file is outside the financial census and never grants EX.
    raw = canonical(value)
    need(len(raw)<=33_554_432,'bounded complete current snapshot receipt')
    slot = fresh(path)
    try:
        at = 0
        while at<len(raw):
            n = os.write(slot[0],raw[at:at+65536])
            need(type(n) is int and 0<n<=min(65536,len(raw)-at),'snapshot write progress')
            at += n
        os.fsync(slot[0]); need(read_fd(slot,33_554_432)==raw,'complete snapshot receipt readback')
        os.fchmod(slot[0],0o444); os.fsync(slot[0])
        need(read_fd(slot,33_554_432)==raw,'sealed snapshot receipt readback')
    except BaseException as error:
        if FIRST[0] is None:
            FIRST[0] = error
        remember(error)
        raise
    finally:
        if slot[1]=='OWNED':
            try:
                close(slot)
            except BaseException as error:
                remember(error)
    need(FIRST[0] is None and not IO_UNKNOWN[0],'snapshot close returned')
    sync_directory(path.parent)
    return {'path':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'mode':0o444}


def _run(operation, profile, action, role, self_pin=None):
    # This is the first operation at actual run entry, before reading a plan or
    # fallible preparation. Source startup/import costs remain OPEN_NOT_ZERO.
    loader,loaded,ctx,start_pin,reservation,command = None,None,None,None,None,None
    name,cleanup_known,result,status = None,False,None,'STOP'
    snapshot_pin = None
    owner_attempted = False
    try:
        START[0] = time.monotonic_ns()
        need(USED[0] is False,'one manual attempt including failed preparation')
        USED[0] = True
        if type(operation) is str:
            plan_path = Path(operation)
            operation = strict_json(_read_record(plan_path,cap=8_388_608))
            need(plan_path==ROOT/'runtime/manual-operations'/(operation['attempt_id']+'.json'),
                 'fixed parent operation plan outside financial census')
        plan_shape(operation,action,profile)
        name = operation['attempt_id']
        self_pin = operation['meter_source_pin'] if self_pin is None else self_pin
        need(self_pin==operation['meter_source_pin'] and self_pin['path']==str(PACKAGE/'manual_meter_v1.py') and
             self_pin['mode']==0o444,'exact genuine producer source subject')
        stable_source(Path(self_pin['path']),{'bytes':self_pin['bytes'],'sha256':self_pin['sha256']})
        loader = _load_loader()
        loaded = loader.load_fixed_sources(profile)
        RETAINED.extend((loader,loaded))
        F = loaded.F
        # The loader and materialized C2 launch checks completed before any owned
        # alarm. This operation does not introduce a signal-owner change.
        ARMED[0] = True
        lower_limit(resource.RLIMIT_AS,MEMORY); lower_limit(resource.RLIMIT_FSIZE,33_554_432)
        sample_memory()
        need(metadata('/proc/self/task/'+str(os.getpid())+'/children').strip()==b'',
             'manual operation creates no child and inherits no live child')
        docs = {}
        for key,kind in (('permission_pin','PERMISSION'),('command_pin','COMMAND'),
                         ('reservation_pin','RESERVATION'),('pre_entry_pin','PRE_ENTRY'),
                         ('reserved_manifest_pin','ENTRY_MANIFEST')):
            pin = operation[key]; raw = _read_record(pin['path'],pin)
            docs[kind] = F.validate_original_record(kind,F.financial_decode(raw))
            need(operation['extra_wires'].get(pin['path'])==raw.decode('utf-8'),
                 'candidate own original wires match actual original files')
        permission,command,reservation,pre,reserved = (docs[k] for k in
            ('PERMISSION','COMMAND','RESERVATION','PRE_ENTRY','ENTRY_MANIFEST'))
        expected_class = 'METADATA_CLOSER' if role=='CLOSER' else 'METADATA_INITIALIZER'
        need(all(d['attempt_id']==name for d in docs.values()) and
             command['operation_class']==permission['operation_class']==expected_class and
             command['settlement_route']==reservation['settlement_route']=='MANUAL_ONLY' and
             command['permission_pin']==reservation['permission_pin']==pre['permission_pin']==operation['permission_pin'] and
             reservation['command_pin']==pre['command_pin']==reserved['command_pin']==operation['command_pin'] and
             reserved['reservation_pin']==operation['reservation_pin'] and
             reserved['pre_entry_pin']==operation['pre_entry_pin'] and reserved['phase']=='RESERVED',
             'original same-attempt role/command/permission/reservation/pre-entry chain')
        need(permission['allow_one_attempt'] is True and reservation['no_automatic_retry'] is True and
             reservation['body_reservation_ns']==permission['body_reservation_ns'] and
             reservation['admin_policy_ns']==permission['admin_policy_ns']==F.ADMIN_NS,
             'actual original funding and no automatic retry')
        plan_path = ROOT/'runtime/manual-operations'/(name+'.json')
        need(command['exact_shell_command']==shell_command(action,profile,plan_path,self_pin),
             'original exact fixed source/action/profile/plan command')
        folder = F.FIN_ENTRIES/name
        need(operation['reserved_manifest_pin']['path']==str(folder/'ENTRY-000000.json') and
             pre['expected_meter_start_path']==str(folder/'METER_START.json') and
             pre['execution_started'] is False,'planned originals precede dispatch')
        # Canonical BODY is inherited FD1; opening a matching path never grants
        # producer authority. A4 repeats paired native FD/path identity later.
        body_path = folder/'METER_BODY.json'; info = os.fstat(1)
        need(folder.resolve(strict=True)==folder and stat.S_IMODE(folder.lstat().st_mode)==0o700 and
             body_path.resolve(strict=True)==body_path and identity(body_path.lstat())==identity(info) and
             stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode)==0o600 and
             info.st_uid==os.getuid() and info.st_nlink==1 and info.st_size==0,
             'actual inherited FD1 is exact original empty BODY')
        start = {'schema':'fresh-financial-meter-start-v1','attempt_id':name,
            'command_pin':operation['command_pin'],'reservation_pin':operation['reservation_pin'],
            'permission_pin':operation['permission_pin'],'meter_source_pin':self_pin,
            'body_begin_ns':START[0],'body_scope':'RUN_ENTRY_THROUGH_OWNED_CLEANUP_V1'}
        raw = canonical(start)
        planned_start_pin = {'path':str(folder/'METER_START.json'),'bytes':len(raw),
                     'sha256':hashlib.sha256(raw).hexdigest(),'mode':0o444}
        _publish_original(planned_start_pin,raw)
        start_pin = planned_start_pin  # Genuine durable producer START only after full publication.
        MARKER_PHASE[0] = 'DURABLE_START'
        extra = dict(operation['extra_wires']); extra[start_pin['path']] = raw.decode('utf-8')
        extra[str(body_path)] = ''
        built = loaded.candidate.bind_funding(F).build_started(operation['predecessor_snapshot'],
            operation['reserved_manifest_pin'],start_pin,extra,operation['pending_path'])
        candidate = built['candidate']
        for key in ('started_manifest_pin','pending_pin'):
            pin = built[key]
            _publish_original(pin,candidate['wires'][pin['path']].encode('utf-8'))
        MARKER_PHASE[0] = 'DURABLE_STARTED_AND_PENDING'
        need(operation['approved_opening'] is None,
             'fixed candidate-derived opening selection; no stale pre-START opening hash')
        opening_evidence = F.opening_evidence(candidate)
        adoption = {'schema':'fresh-current-opening-adoption-v1',
            'opening_sha256':candidate['opening_pin']['sha256'],
            'state_sha256':opening_evidence['state_sha256'],
            'manual_body_ns':opening_evidence['manual_body_ns'],
            'manual_admin_ns':opening_evidence['manual_admin_ns'],
            'operations':len(opening_evidence['views']),
            'authorization_sha256':F.AUTHORIZATION_SHA256,
            'funding_source_sha256':loader.SELECTED['funding']['sha256'],
            'authority_scope':'OPENING_DATA_SELECTION_ONLY_NOT_OPERATIONAL_GRANT'}
        adoption_raw = canonical(adoption)
        adoption_path = ROOT/'runtime/manual-operations'/(name+'.opening-adoption.json')
        adoption_pin = {'path':str(adoption_path),'bytes':len(adoption_raw),
            'sha256':hashlib.sha256(adoption_raw).hexdigest(),'mode':0o444}
        _publish_original(adoption_pin,adoption_raw)
        approved_opening = {'schema':'fresh-current-opening-binding-v1',
            'opening_pin':candidate['opening_pin'],'adoption_pin':adoption_pin,
            'funding_source_sha256':loader.SELECTED['funding']['sha256']}
        manual = _binding(F,operation,candidate,start_pin,built['pending_pin'],reservation,command)
        owner_attempted = True
        ctx = loader.open_manual_owner(loaded,role,approved_opening=approved_opening,
            expected_head_pin=operation['expected_head_pin'],approved_manual_entry=manual)
        # Literal manual methods only; never C2.actual_context_ports or payload.
        mode = 'CLOSE_ONLY' if role=='CLOSER' else 'INITIALIZE_ONLY'
        loader.manual_call(loaded,ctx,'adopt_financial_candidate',candidate,mode)
        loader.manual_call(loaded,ctx,'check',0,operation['cleanup_ns'])
        if role=='CLOSER':
            # CLOSE_ONLY adoption already performs prepare_metadata_close once.
            result = loader.manual_call(loaded,ctx,'publish_metadata_close')
        elif action=='INITIALIZE':
            raw_registry = F.initial_registry(approved_opening['opening_pin'],
                operation['policy_pins'],operation['phase'],operation['phase_release_sha256'])
            result = loader.manual_call(loaded,ctx,'initialize',raw_registry)
        else:
            result = loader.manual_call(loaded,ctx,'refresh_opening')
        loader.manual_call(loaded,ctx,'check',0,operation['cleanup_ns'])
        # A4 guards actual own EX/currentness on both sides of this exact F4 IO.
        # No private context reflection or payload ownership port is used.
        expected_financial_head = result['financial_head_pin'] if role=='CLOSER' else candidate['head_pin']
        _, head_raw = F._read_frame_pin(loaded.C.IO,expected_financial_head,os.getuid())
        head_data = F.financial_decode(head_raw)
        current_snapshot = F.read_financial_opening(loaded.C.IO,head_data['opening_pin'],os.getuid())
        need(current_snapshot['head_pin']==expected_financial_head,'exact current snapshot under actual own EX')
        loader.manual_call(loaded,ctx,'check',0,operation['cleanup_ns'])
        snapshot_pin = _snapshot_receipt(ROOT/'runtime/manual-operations'/(name+'.snapshot.json'),
            {'schema':'fresh-manual-current-snapshot-receipt-v1','attempt_id':name,
             'action':action,'profile':profile,'meter_start_pin':start_pin,
             'financial_head_pin':expected_financial_head,'snapshot':current_snapshot})
        loader.manual_call(loaded,ctx,'check',0,operation['cleanup_ns'])
        sample_memory()
        status = 'MANUAL_CALL_RETURNED'
    except BaseException as error:
        if FIRST[0] is None:
            FIRST[0] = error  # Before fallible reporting or cleanup bookkeeping.
        USED[0] = True  # Failed first clock also consumes the one local attempt.
        remember(error)
    finally:
        if loaded is not None:
            try:
                loader.release_manual_once(loaded)
            except BaseException as error:
                if FIRST[0] is None:
                    FIRST[0] = error
                remember(error)
        if loader is not None:
            try:
                loader.cleanup_transports_once(loaded)
            except BaseException as error:
                if FIRST[0] is None:
                    FIRST[0] = error
                remember(error)
        for slot in SLOTS:
            if slot[1]=='OWNED':
                try:
                    close(slot)
                except BaseException as error:
                    if FIRST[0] is None:
                        FIRST[0] = error
                    remember(error)
        try:
            disposition = loader.cleanup_disposition(loaded) if loader is not None else None
            cleanup_known = (not IO_UNKNOWN[0] and all(s[1] in ('FREE','CLOSED') for s in SLOTS)
                and disposition is not None and disposition['known_closed'])
            if disposition is not None:
                for error in (disposition['first'],disposition['controller_first']):
                    if error is not None:
                        remember(error)
                IO_UNKNOWN[0] = IO_UNKNOWN[0] or disposition['loader_io_unknown'] or disposition['controller_io_unknown'] or not cleanup_known
        except BaseException as error:
            if FIRST[0] is None:
                FIRST[0] = error
            remember(error); IO_UNKNOWN[0] = True
        try:
            END[0] = time.monotonic_ns()  # All actual release/slot-close attempts precede END.
            need(type(END[0]) is int and END[0]>=START[0]>=0,'real complete manual body endpoints')
            if reservation is not None:
                need(END[0]-START[0]<=reservation['body_reservation_ns'],'whole own body reservation exceeded')
        except BaseException as error:
            if FIRST[0] is None:
                FIRST[0] = error
            remember(error)
    # Exactly one BODY attempt, through inherited FD1, after release and END.
    if start_pin is not None:
        try:
            body = body_data(name,operation['command_pin'],operation['reservation_pin'],start_pin,
                START[0],END[0],cleanup_known,IO_UNKNOWN[0],PEAK_SAMPLED_PARENT_CHILD_RSS[0],
                type(FIRST[0]).__name__ if FIRST[0] is not None else None,
                [type(e).__name__ for e in SECONDARY if e is not None])
            emit_fd1(canonical(body))
        except BaseException as error:
            if FIRST[0] is None:
                FIRST[0] = error
            remember(error)  # No second BODY write or retry after partial output.
    try:
        detail = {'schema':'fresh-fixed-manual-producer-detail-v1','attempt_id':name,
            'action':action,'profile':profile,'literal_role':role,'status':status,
            'meter_start_pin':start_pin,'marker_phase':MARKER_PHASE[0],
            'body_begin_ns':START[0],'body_end_after_cleanup_ns':END[0],
            'cleanup_known':cleanup_known,'owner_attempted':owner_attempted,
            'manual_result':result,'current_snapshot_receipt_pin':snapshot_pin,
            'errors_after_BODY':error_data(),
            'all_costs_settled':False,'execution_permission':False,'physical_boundary':'OPEN_NOT_ZERO'}
        raw = canonical(detail); need(len(raw)<=65536,'manual detail cap')
        at = 0
        while at<len(raw):
            n = os.write(2,raw[at:]); need(type(n) is int and 0<n<=len(raw)-at,'detail write progress'); at+=n
        os.fsync(2)
    except BaseException as error:
        if FIRST[0] is None:
            FIRST[0] = error
        remember(error)
    return 0 if status=='MANUAL_CALL_RETURNED' and FIRST[0] is None and cleanup_known else 78


def run_initializer(operation, profile='normal', action='INITIALIZE', self_pin=None):
    need(action in ('INITIALIZE','REFRESH'),'literal publisher initializer or refresh')
    return _run(operation,profile,action,'PUBLISHER',self_pin)


def run_closer(operation, profile='normal', self_pin=None):
    return _run(operation,profile,'CLOSE','CLOSER',self_pin)


if __name__=='__main__':
    need(len(sys.argv)==6,'exact ACTION PROFILE PLAN_PATH SELF_SHA SELF_BYTES arguments')
    action,profile,plan_path,self_sha,self_bytes = sys.argv[1:]
    pin = {'path':str(PACKAGE/'manual_meter_v1.py'),'bytes':int(self_bytes),
           'sha256':self_sha,'mode':0o444}
    if action=='CLOSE':
        sys.exit(run_closer(plan_path,profile,pin))
    need(action in ('INITIALIZE','REFRESH'),'fixed manual role command')
    sys.exit(run_initializer(plan_path,profile,action,pin))
