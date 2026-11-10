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
        self.read_calls=0;self.write_calls=0
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
    record={'path':path,'chunks':[],'raw':None,'observed':None,'read_calls':0};owner.captures.append(record)
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
            need(record['read_calls']<8192,'read call bound');record['read_calls']+=1;owner.read_calls+=1
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
        offset=0;calls=0;call_cap=4096 if len(raw)<=RECORD_CAP else 8192
        while offset<len(raw):
            need(calls<call_cap,'write call bound');calls+=1;owner.write_calls+=1
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

PROJECT_ORDER=('epoch_schema_v5','h25_parent_supervisor','v03_integrated_constructor_v2','v03_source_refusal_observer_v1','epoch_copy_v5','group01_original_predicates_v1','parent_domain_v1','v03_prefix_derivation_v1','epoch_stop_v5','original_build_provenance_v5','parent_closure_v1','epoch_parent_v5','group01_evidence_v1','parent_completion_v1','v03_prefix_supervisor_v1')
PROJECT_PINS={
'epoch_schema_v5':('b89a789654be87bde40a47300f4d9702dce2b90e6ab3be9a2025f6d8041b3e9a',30668),
'h25_parent_supervisor':('cfb09a18dd10b597cc6d5a8139ee769bef679bc44ae029329755e3d97b055075',23047),
'v03_integrated_constructor_v2':('a80a60b390bc60e9bc434b79cda5ae6db88e4f0c6c7436de9adfe1f48a2045b1',6111),
'v03_source_refusal_observer_v1':('abf25690d3bee4a9783ee504567c29f7fb47da670e0ec95f57cb5944bf57264f',14205),
'epoch_copy_v5':('4f459d0336d59975df787c24373e18dad4044c3a24137392e890115f811b3211',82957),
'group01_original_predicates_v1':('fb9e6e11b39b76ab8652c546fd76c06d662ea4116376abcc2a6267bb4783dbfd',23224),
'parent_domain_v1':('a51264289803b4b17bb262f2460ddd4ed72500aaa21e5eb80fa2db4583689361',23942),
'v03_prefix_derivation_v1':('1ed813148c10d5fbd3cd6781d51eca650a347eda7a6323f581d740e6ea9cb6e2',3830),
'epoch_stop_v5':('5b10c9d72dd0e646652a73b6ffe9ba870762d6bc2f7432bc6b06571a1b7d2a6f',8205),
'original_build_provenance_v5':('bd5ffd9a1c221e0945527fc8fa8d0ad4eb36b9a8884503451c1b6b12d00007ea',16024),
'parent_closure_v1':('a15424f14baa3d484fe04bfbe7e449c32561c866dbaca2c1b5f646dfb377ed1f',13463),
'epoch_parent_v5':('058059912144863a4b2bfe4fc9ffc5233b4ab20ee5a7355bde66f4d3f6f28712',26833),
'group01_evidence_v1':('05ec6a63c57340ba929aea1fab71b096efc143e099346640f6def41310bd3e25',15610),
'parent_completion_v1':('d4ee1b7ce4a42b73261984ffb1b9ceb5bb0165223e04a253588f83b99f6981a5',54168),
'v03_prefix_supervisor_v1':('f97b07d4a5f461d4134a2bdf4cfcc28da12acc7e7144c18f6cc0a017cdee86f6',36954)}
GATE_NAMES={'v03_prefix_supervisor_v1':('CONFIGURATION','SOURCE_REVIEW','STAGE_APPROVAL','COMMAND_APPROVAL','FUNDING','EXECUTION_APPROVAL'),'epoch_copy_v5':('COPY_CONFIGURATION','COPY_EXECUTION_APPROVAL','COPY_FUNDING')}


def import_edges(buffers):
    need(type(buffers) is dict and all(type(k) is str and type(v) is bytes for k,v in buffers.items()),'exact retained graph')
    graph={name:set() for name in buffers}
    t0={'ctypes','ast','builtins','__future__','copy','dataclasses','fcntl','gc','hashlib','json','marshal','math','os','pathlib','posix','resource','signal','stat','struct','subprocess','sys','time','types'}
    for name,raw in buffers.items():
        tree=ast.parse(raw,feature_version=(3,12))
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                for alias in node.names:
                    need(alias.name in buffers or alias.name.split('.')[0] in t0,'missing selected project import')
                    if alias.name in buffers:graph[name].add(alias.name)
            elif isinstance(node,ast.ImportFrom):
                need(node.level==0 and node.module is not None and (node.module in buffers or node.module.split('.')[0] in t0),'missing selected project from-import')
                if node.module in buffers:graph[name].add(node.module)
    return graph


def load_authenticated_modules(policy,expected,order,owner):
    """Concrete retained-byte construction; expected is independently fixed DATA.

    Runtime entry passes only fixed PROJECT_PINS/ORDER. NEW literal fixtures may
    exercise this mechanism with separate explicit expected fixture byte pins.
    """
    need(type(owner) is Owner,'actual bootstrap owner required');owner.ready()
    need(not owner.burned,'one bootstrap construction attempt');owner.burned=True
    try:
        need(type(policy) is dict and type(expected) is dict and type(order) is tuple,'exact module inputs')
        need(all(type(k) is str for k in policy) and all(type(k) is str for k in expected),'exact module names')
        need(all(type(name) is str for name in order),'exact order names')
        need(set(policy)==set(expected)==set(order) and len(order)==len(set(order)) and 1<=len(order)<=48,'module set/order bound')
        need(not any(name in sys.modules for name in order),'selected project name already ambient')
        buffers={};filenames={}
        for name in order:
            pin=policy[name];validate_blob(pin)
            pair=expected[name];need(type(pair) is tuple and len(pair)==2,'exact expected source row')
            digest,size=pair
            need(type(digest) is str and type(size) is int and pin['sha256']==digest and pin['bytes']==size,'selected project prior pin differs')
            observed,raw=retain_regular(pin,FILE_CAP,owner)
            buffers[name]=raw;filenames[name]=observed['path']
        owner.phase='ALL_PROJECT_BYTES_AUTHENTICATED'
        graph=import_edges(buffers);positions={name:index for index,name in enumerate(order)}
        need(all(positions[dependency]<positions[name] for name,deps in graph.items() for dependency in deps),'project dependency/init order differs')
        for name in order:
            module=types.ModuleType(name)
            module.__dict__['__file__']=filenames[name]
            module.__dict__['__builtins__']=builtins.__dict__
            owner.modules[name]=module
        for name in order:
            need(name not in sys.modules,'selected name became ambient')
            module=owner.modules[name]
            code=compile(buffers[name],filenames[name],'exec',dont_inherit=True,optimize=sys.flags.optimize)
            sys.modules[name]=module;owner.published.append(name);owner.phase='INITIALIZING:'+name
            exec(code,module.__dict__)
            owner.executed.append(name)
            need(sys.modules.get(name) is module and module.__dict__.get('__builtins__') is builtins.__dict__,'constructed module identity drift')
            need(len(module.__dict__)<=512,'actual namespace bound')
            for dependency in graph[name]:need(sys.modules.get(dependency) is owner.modules[dependency],'project import identity differs')
        owner.phase='PROJECT_GRAPH_READY'
        return dict(owner.modules)
    except BaseException as error:
        raise owner.fail(error)


def validate_startup(executable,flags,environment,search_path,argv,manifest):
    plain(manifest)
    need(type(manifest.get('mode')) is str and manifest['mode'] in ('normal','optimized'),'exact selected mode')
    need(executable=='/usr/bin/python3.12','pinned interpreter')
    need(type(flags) is dict and flags=={'no_site':1,'no_user_site':1,'dont_write_bytecode':1,'safe_path':True,'ignore_environment':0,'isolated':0,'hash_randomization':0,'optimize':1 if manifest['mode']=='optimized' else 0},'original startup flags')
    need(type(environment) is dict and environment==ENV and tuple(search_path)==SYSTEM_PATH,'exact native environment/search path')
    expected=['--output',manifest['session_directory'],'--lanes',manifest['lanes']]
    need(type(manifest['finite_only']) is bool,'exact finite-only selection')
    if manifest['finite_only']:expected.append('--finite-only')
    need(type(argv) is list and all(type(x) is str for x in argv) and argv==expected,'fixed runner entry tail differs')


def install_gate_data(modules,gates):
    plain(gates)
    need(type(gates) is dict and set(gates)==set(GATE_NAMES),'exact gate module set')
    for name,keys in GATE_NAMES.items():
        need(type(gates[name]) is dict and set(gates[name])==set(keys),'exact admitted gate names')
        need(all(gates[name][key] is not None for key in keys),'runtime gate data remains unconfigured')
    for name,keys in GATE_NAMES.items():
        for key in keys:modules[name].__dict__[key]=gates[name][key]


def entry_operation(manifest,owner):
    """Actual operation source, conditional on T0/custody/admissions; NOT fixture-run."""
    plain(manifest)
    need(manifest.get('schema')=='unit06-bootstrap-manifest-v1','bootstrap manifest schema')
    validate_blob(manifest['receiver_policy'],RECORD_CAP);validate_blob(manifest['outer_plan'],RECORD_CAP)
    policy_raw=retain_regular(manifest['receiver_policy'],RECORD_CAP,owner)[1];policy=decode(policy_raw)
    plan_raw=retain_regular(manifest['outer_plan'],RECORD_CAP,owner)[1];plan=decode(plan_raw)
    need(type(manifest.get('mode')) is str and manifest['mode'] in ('normal','optimized') and plan['mode']==manifest['mode'],'outer plan/bootstrap mode differs')
    need(plan['session_directory']==manifest['session_directory'],'runner output/plan session differs')
    path_text(manifest['canonical_root']);path_text(plan['round_root'])
    need(plan['round_root']!=manifest['canonical_root'],'private control root must differ')
    pairs=set()
    for lock_name in ('parent-queue.lock','science.lock'):
        canonical_lock=observe_regular(manifest['canonical_root']+'/runtime/'+lock_name,RECORD_CAP,owner)[0]
        pairs.add((canonical_lock['identity']['device'],canonical_lock['identity']['inode']))
    need(type(manifest['private_locks']) is list and len(manifest['private_locks'])==2,'two actual private lock pins')
    for index,pin in enumerate(manifest['private_locks']):
        need(type(pin) is dict and pin.get('path')==plan['round_root']+'/runtime/'+('parent-queue.lock','science.lock')[index],'actual private constructor lock path differs')
        row=retain_regular(pin,RECORD_CAP,owner)[0];pair=(row['identity']['device'],row['identity']['inode'])
        need(pair not in pairs,'private/canonical locks share actual inode');pairs.add(pair)
    gates=manifest['gates'];plain(gates)
    need(gates['v03_prefix_supervisor_v1']['CONFIGURATION']['plan']==manifest['outer_plan'] and gates['v03_prefix_supervisor_v1']['CONFIGURATION']['receiver_policy']==manifest['receiver_policy'],'actual selected plan/policy gate binding')
    modules=load_authenticated_modules(policy,PROJECT_PINS,PROJECT_ORDER,owner)
    install_gate_data(modules,gates)
    need(all(sys.modules.get(name) is modules[name] for name in PROJECT_ORDER),'actual module census before owner')
    owner.phase='ORIGINAL_OWNER_CONSTRUCTION'
    token=modules['v03_prefix_supervisor_v1'].make_prefix_owner(modules)
    owner.phase='ORIGINAL_PREFIX_OPERATION'
    result_pin=modules['v03_prefix_supervisor_v1'].run_prefix(token)
    owner.result=result_pin
    observed,raw=retain_regular(result_pin,RECORD_CAP,owner);result=decode(raw)
    need(result['schema']=='h25-owned-v03-prefix-observation-v1' and result['production_completion'] is False and result['full_c05'] is False and result['full_v03'] is False and result['runtime_qualified'] is False,'prefix DATA result scope')
    data={'schema':'unit06-prefix-science-data-v1','status':'PREFIX_OBSERVATION_DATA','observation':observed,
          'production_completion':False,'full_c05':False,'full_v03':False,'runtime_qualified':False,'enclosing_parent_exit_observed':False}
    pin=write_exclusive(manifest['session_directory']+'/receipt.json',canonical(data),0o600,owner)
    owner.phase='DATA_RECEIPT_WRITTEN';return pin


def main():
    owner=Owner()
    try:
        stage=Path(__file__).parent.parent
        stage_pin,stage_raw=observe_regular(str(stage/'STAGE.json'),RECORD_CAP,owner)
        declared=decode(stage_raw)
        relative='integration/PREFIX-BOOTSTRAP.json'
        expected=declared['files'][relative]
        pin,raw=retained_read(str(stage/relative),expected['sha256'],RECORD_CAP,owner)
        need(pin['identity']['mode']&0o777==expected['mode'],'manifest stage mode differs')
        manifest=decode(raw)
        flags={name:getattr(sys.flags,name) for name in ('no_site','no_user_site','dont_write_bytecode','safe_path','ignore_environment','isolated','hash_randomization','optimize')}
        validate_startup(sys.executable,flags,dict(os.environ),sys.path,sys.argv[1:],manifest)
        owner.phase='ENTRY_INPUTS_BOUND'
        return entry_operation(manifest,owner)
    except BaseException as error:
        raise owner.fail(error)


if __name__=='__main__':main()
