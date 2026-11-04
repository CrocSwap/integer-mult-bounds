"""Original parent evidence writer/receiver successor v29; SOURCE ONLY.

Derived from CrocSwap/integer-mult-bounds original_records.py at public commit
ff7df8391c3bb3f5518ce43682ba4c1e41380e3e, SHA256
a6e9cd9cfcfc5300601d668b7a498b1c6cd13714ebea79122bd97faa0c8a7a8e.
Predecessor authors retain credit. Substantial Pro, Codex and Sol Max assistance.
The one new STARTED observation port cannot reconstruct or resume a parent.

External parent manual authority/source-capture authentication is mandatory.
No Tool call, clock, A4/native EX, financial HEAD/STATE or formal CLOSE is created
or inferred here. Fixed F4 pure validators are externally loaded/authenticated.
"""
import hashlib
import json
import os
from pathlib import Path
import stat
from types import ModuleType, FunctionType

W = Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
R = W/'outputs/h25-data-handling-20261028'
FINANCIAL = R/'control/prospective-financial-v1'
ENTRIES = FINANCIAL/'entries'
F4_SOURCE = R/'areas/fresh-round-reusable-record-implementation-v3/funding_current.py'
CAP = 131072
MAX_FILES, MAX_BYTES, MAX_STEPS, MAX_GROUPS = 4096,16777216,64,64
MAX_VALUE = (1 << 63)-1
_TOKEN = object()
RECORDS = {'COMMAND': {'keys': ['schema', 'attempt_id', 'operation_class', 'settlement_route', 'exact_shell_command', 'exact_shell_sha256', 'permission_pin', 'source_packet_pin', 'operating_profile_pin', 'review_contract_pin', 'result_contract_pin', 'declared_inventory_pin', 'declared_result_groups', 'limits', 'metadata_close_intent'], 'schema': 'fresh-financial-command-v1'}, 'ENTRY_MANIFEST': {'keys': ['schema', 'attempt_id', 'command_pin', 'reservation_pin', 'pre_entry_pin', 'meter_start_pin', 'meter_body_pin', 'native_chain_pin', 'financial_adjudication_pin', 'settlement_route', 'formal_start_pin', 'formal_receipt_pin', 'phase'], 'schema': 'fresh-financial-entry-manifest-v1'}, 'FINANCIAL_ADJUDICATION': {'keys': ['schema', 'attempt_id', 'command_pin', 'reservation_pin', 'permission_pin', 'meter_start_pin', 'meter_body_pin', 'native_chain_pin', 'source_packet_pin', 'review_contract_pin', 'detail_review_pin', 'result_groups', 'financial_status', 'body_outcome', 'accepted_body_ns', 'admin_policy_ns', 'known_policy_ns', 'cleanup_status', 'resource_status', 'tail_status', 'scope_flags'], 'schema': 'fresh-independent-financial-adjudication-v1'}, 'METER_BODY': {'keys': ['schema', 'attempt_id', 'command_pin', 'reservation_pin', 'meter_start_pin', 'body', 'owned_cleanup', 'owned_wait', 'child_exit', 'resource_observations', 'errors', 'body_scope', 'physical_boundary'], 'schema': 'fresh-financial-meter-body-v1'}, 'METER_START': {'keys': ['schema', 'attempt_id', 'command_pin', 'reservation_pin', 'permission_pin', 'meter_source_pin', 'body_begin_ns', 'body_scope'], 'schema': 'fresh-financial-meter-start-v1'}, 'NATIVE_CHAIN': {'keys': ['schema', 'attempt_id', 'command_pin', 'reservation_pin', 'calls'], 'schema': 'fresh-financial-native-chain-v1'}, 'PERMISSION': {'keys': ['schema', 'attempt_id', 'round_id', 'operation_class', 'body_reservation_ns', 'admin_policy_ns', 'source_packet_pin', 'operating_profile_pin', 'review_contract_pin', 'round_authorization_pin', 'allow_one_attempt'], 'schema': 'fresh-financial-permission-v1'}, 'PRE_ENTRY': {'keys': ['schema', 'attempt_id', 'command_pin', 'reservation_pin', 'permission_pin', 'expected_meter_start_path', 'expected_native_chain_path', 'execution_started', 'provider_request_pin'], 'schema': 'fresh-financial-pre-entry-v1'}, 'RESERVATION': {'keys': ['schema', 'attempt_id', 'command_pin', 'permission_pin', 'policy_adoption_pin', 'before_closed_state_pin', 'body_reservation_ns', 'admin_policy_ns', 'policy_reserved_before_ns', 'policy_reserved_after_ns', 'settlement_route', 'no_automatic_retry'], 'schema': 'fresh-financial-reservation-v1'}}


class WriterStop(RuntimeError):
    pass


def need(value,message):
    if not value:
        raise WriterStop(message)


def plain(value,depth=0,budget=None):
    if budget is None:
        budget=[0]
    budget[0]+=1
    need(depth<=16 and budget[0]<=200000,'WRITER:TYPE')
    t=type(value)
    if t is dict:
        need(len(value)<=256 and all(type(k) is str and len(k)<=128 for k in value),'WRITER:TYPE')
        for v in value.values():plain(v,depth+1,budget)
    elif t is list:
        need(len(value)<=4096,'WRITER:TYPE')
        for v in value:plain(v,depth+1,budget)
    elif t is str:
        need(len(value)<=CAP,'WRITER:TYPE')
    elif t is int:
        need(-(1<<63)<=value<=MAX_VALUE,'WRITER:TYPE')
    else:
        need(value is None or t is bool,'WRITER:TYPE')


def label(value):
    need(type(value) is str and 1<=len(value)<=64 and
         all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in value),'WRITER:ID')
    return value


def basename(value):
    need(type(value) is str and 1<=len(value)<=128 and value not in ('.','..') and
         all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.' for c in value),'WRITER:PATH')
    return value


def pin_data(value,cap=CAP):
    plain(value)
    need(type(value) is dict and set(value)=={'path','bytes','sha256','mode'},'WRITER:PIN')
    p=value['path'];n=value['bytes'];h=value['sha256'];mode=value['mode']
    need(type(p) is str and p.startswith(str(R)+'/') and len(p)<=4096 and
         all(x not in ('','.','..') for x in p.split('/')[1:]) and '\x00' not in p and '\\' not in p,'WRITER:PIN')
    need(type(n) is int and 0<=n<=cap and type(h) is str and len(h)==64 and
         all(c in '0123456789abcdef' for c in h) and type(mode) is int and mode in (0o444,0o600,0o400),'WRITER:PIN')
    return value


def canonical(value):
    plain(value)
    raw=(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
    need(len(raw)<=CAP,'WRITER:WIRE_LIMIT')
    return raw


def identity(st):
    return (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_nlink,st.st_size,st.st_mtime_ns,st.st_ctime_ns)


def bind_parent_writer(actual_F4,source_pin):
    """Trusted source-private parent supplies actual fixed F4, never JSON owner.

    Consistency is NOT authentication of a fabricated module. A4 actual IO/EX
    and formal/financial publication are separate, never provided by this API.
    """
    pin_data(source_pin,2097152)
    need(source_pin['path']==str(F4_SOURCE) and source_pin['mode']==0o444,'WRITER:SOURCE')
    need(type(actual_F4) is ModuleType,'WRITER:SOURCE')
    namespace=ModuleType.__getattribute__(actual_F4,'__dict__')
    need(type(namespace.get('__file__')) is str and namespace['__file__']==str(F4_SOURCE),'WRITER:SOURCE')
    functions={}
    for name in ('validate_original_record','metadata_decode','_manifest_successor'):
        fn=namespace.get(name)
        need(type(fn) is FunctionType and fn.__globals__ is namespace and
             fn.__code__.co_filename==str(F4_SOURCE),'WRITER:SOURCE')
        functions[name]=(fn,fn.__code__)
    def call(name,*args):
        need(ModuleType.__getattribute__(actual_F4,'__dict__') is namespace and
             all(namespace.get(k) is f and f.__code__ is code for k,(f,code) in functions.items()),'WRITER:SOURCE_CHANGED')
        return functions[name][0](*args)
    def create(attempt_id):
        # No instance exists yet: validate the label before construction or any
        # attribute/Path work. Pre-object errors propagate unchanged to parent.
        checked_id=label(attempt_id)
        return _ParentEvidence(_TOKEN,checked_id,call)
    return create


def started_successor_data(previous,observed,start_pin,version,last_phase,reconciled):
    """New pure necessary transition gate; DATA never authenticates a source.

    Custody/source/original-parent checks remain in receive_started_manifest.
    This helper is used there and is the bounded new-code control surface.
    """
    need(type(version) is int and version==1 and type(last_phase) is str and
         last_phase=='RESERVED' and
         reconciled is False,'WRITER:STARTED_ONE_STEP')
    plain(previous);plain(observed);plain(start_pin)
    need(type(previous) is dict and type(observed) is dict and
         set(previous)==set(RECORDS['ENTRY_MANIFEST']['keys']) and
         previous['schema']==RECORDS['ENTRY_MANIFEST']['schema'] and
         previous['phase']=='RESERVED' and previous['meter_start_pin'] is None,
         'WRITER:PRIVATE_PREDECESSOR')
    pin_data(start_pin)
    expected=dict(previous,meter_start_pin=dict(start_pin),phase='STARTED')
    need(observed==expected,'WRITER:STARTED_EXACT')
    return expected


def _entry_operation(fn):
    # Fixed source methods only; caller never supplies a callback/IO/native owner.
    def guarded(self,*args,**kwargs):
        need(self.first is None and not self.unknown and self.last_phase not in ('CLOSED_KNOWN','OPEN_UNCERTAIN'),'WRITER:BLOCKED')
        try:return fn(self,*args,**kwargs)
        except BaseException as error:
            self.phase='FAILED_UNCERTAIN'
            raise self._remember(error)
    return guarded


class _ParentEvidence:
    """One fresh persistent parent-owned entry, no A4/native ownership claim.

    An externally admitted serialized parent keeps this object/capture originals
    alive. Existing/partial entry cannot be resumed/retried through this class.
    """
    def __init__(self,token,attempt_id,call):
        need(token is _TOKEN,'WRITER:PRIVATE_FACTORY')
        self.attempt_id=attempt_id;self.root=ENTRIES/attempt_id;self._call=call
        self.phase='PRIVATE_BEFORE_CREATE';self.first=None;self.secondary=[];self.unknown=False
        self.slots=[[None,'FREE',False] for unused in range(8)]
        self.pins={};self.values={};self.calls=[];self.pending=None;self.session=None
        self.unresolved=[];self.origins=[];self.version=0;self.last_manifest=None
        self.terminal=False;self.created=False;self.last_phase=None;self.last_manifest_obj=None;self.observation_errors=[]
        # Retained private bytes belong to this actual instance, never JSON restore.
        self._reserved_manifest_raw=None;self._reserved_manifest_pin=None
        self._received_start_original=None;self._started_reconciled=False

    def _remember(self,error):
        if self.first is None:self.first=error
        elif error is not self.first and all(error is not e for e in self.secondary):
            if len(self.secondary)<32:self.secondary.append(error)
            else:self.unknown=True
        return self.first

    def _acquire(self,path,flags=0,directory=False):
        need(type(path) is type(W) and type(flags) is int and type(directory) is bool,'WRITER:PATH')
        if directory:
            need(path in (FINANCIAL,ENTRIES) or path.parent==ENTRIES,'WRITER:PATH')
        elif flags==os.O_RDONLY|os.O_DIRECTORY:
            need(path in (ENTRIES,self.root),'WRITER:PATH')
        else:
            need(path.parent==self.root and flags in (os.O_RDONLY|os.O_NONBLOCK,os.O_WRONLY|os.O_CREAT|os.O_EXCL),'WRITER:PATH')
        need(not self.unknown,'WRITER:IO_UNKNOWN')
        slot=next(s for s in self.slots if s[1] in ('FREE','CLOSED'))
        slot[:]=[None,'PENDING',directory]
        try:
            slot[0]=os.scandir(path) if directory else os.open(path,flags|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            slot[1]='OWNED';return slot
        except BaseException as e:
            self.unknown=True;self._remember(e);raise

    def _close(self,slot):
        need(slot[1]=='OWNED','WRITER:ONE_CLOSE')
        slot[1]='CLOSE_ENTERED'
        try:
            slot[0].close() if slot[2] else os.close(slot[0])
            slot[1]='CLOSED'
        except BaseException as e:
            slot[1]='CLOSE_UNKNOWN';self.unknown=True;self._remember(e);raise

    def _names(self,path,cap):
        slot=None;primary=None;out=[]
        before=self._directory(path)
        try:
            slot=self._acquire(path,directory=True)
            for item in slot[0]:
                need(len(out)<cap,'WRITER:CENSUS_LIMIT');out.append(item.name)
        except BaseException as e:primary=self._remember(e)
        finally:
            if slot is not None and slot[1]=='OWNED':
                try:self._close(slot)
                except BaseException as e:primary=self._remember(e)
        if primary is not None:raise primary
        need(self._directory(path)==before,'WRITER:DIRECTORY_CHANGED')
        return out

    def _directory(self,path):
        st=path.lstat()
        need(path.resolve(strict=True)==path and stat.S_ISDIR(st.st_mode) and
             st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o700,'WRITER:DIRECTORY')
        return identity(st)

    def _sync(self,path):
        slot=None;primary=None;before=self._directory(path)
        try:
            slot=self._acquire(path,os.O_RDONLY|os.O_DIRECTORY)
            need(identity(os.fstat(slot[0]))==before==self._directory(path),'WRITER:DIRECTORY_CHANGED')
            os.fsync(slot[0])
            need(identity(os.fstat(slot[0]))==before==self._directory(path),'WRITER:DIRECTORY_CHANGED')
        except BaseException as e:primary=self._remember(e)
        finally:
            if slot is not None and slot[1]=='OWNED':
                try:self._close(slot)
                except BaseException as e:primary=self._remember(e)
        if primary is not None:raise primary

    def _census(self,extra_files=0,extra_bytes=0):
        # Read-only necessary global suffix bounds, NOT financial/current HEAD authority.
        self._directory(FINANCIAL);self._directory(ENTRIES)
        count,total=0,0;inventory=[]
        root_names=self._names(FINANCIAL,MAX_FILES+1)
        need('entries' in root_names,'WRITER:CENSUS')
        dirs=self._names(ENTRIES,30);need(len(dirs)<=29,'WRITER:OPERATION_LIMIT')
        paths=[]
        for name in root_names:
            if name=='entries':continue
            basename(name)
            need(name=='HEAD.json' or any(name.startswith(p) and name.endswith('.json') and
                 len(name)==len(p)+11 and name[len(p):-5].isdigit() for p in ('HEAD-','STATE-','OPENING-')),'WRITER:ROOT_MEMBER')
            paths.append(FINANCIAL/name)
        for entry in dirs:
            label(entry);folder=ENTRIES/entry;self._directory(folder)
            for name in self._names(folder,MAX_FILES+1):
                need(len(paths)<MAX_FILES,'WRITER:GLOBAL_LIMIT');paths.append(folder/basename(name))
        for path in paths:
            st=path.lstat()
            need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_uid==os.getuid() and
                 stat.S_IMODE(st.st_mode) in (0o444,0o600) and st.st_size<=CAP,'WRITER:CENSUS')
            count+=1;total+=st.st_size;inventory.append((str(path),identity(st)))
            need(count+extra_files<=MAX_FILES and total+extra_bytes<=MAX_BYTES,'WRITER:GLOBAL_LIMIT')
        need(count+extra_files<=MAX_FILES and total+extra_bytes<=MAX_BYTES,'WRITER:GLOBAL_LIMIT')
        return count,total,tuple(sorted(inventory))

    def _namespace(self):
        # Canonical selected ancestors and own parent directory, paired around
        # every sealed-original observation. This is not native EX/currentness.
        return tuple(self._directory(p) for p in (FINANCIAL,ENTRIES,self.root))

    def _publication_before(self,extra_files=0,extra_bytes=0):
        before=self._namespace()
        census=self._census(extra_files,extra_bytes)
        need(self._namespace()==before,'WRITER:DIRECTORY_CHANGED')
        return before,census

    def _sealed_original(self,path,raw,boundary,appended):
        # Both copied and planned originals pass this exact consistency path.
        # Directory fsync does not prove producer exit/file fsync/parent sealing.
        need(type(appended) is bool,'WRITER:TYPE')
        before,prior=boundary;anchor=self._namespace()
        need(anchor[:2]==before[:2] and
             (anchor[2][:5]==before[2][:5] if appended else anchor[2]==before[2]),
             'WRITER:DIRECTORY_CHANGED')
        selected_before=identity(path.lstat())
        observed=self._readback(path,raw)
        need(identity(path.lstat())==selected_before,'WRITER:READBACK')
        need(self._namespace()==anchor,'WRITER:DIRECTORY_CHANGED')
        self._sync(self.root)
        current=self._census()
        need(self._namespace()==anchor,'WRITER:DIRECTORY_CHANGED')
        old_files=dict(prior[2]);new_files=dict(current[2]);selected=str(path)
        need(selected in new_files and new_files[selected]==selected_before==identity(path.lstat()),
             'WRITER:READBACK')
        need((selected not in old_files if appended else selected in old_files) and
             set(new_files)==(set(old_files)|{selected}) and
             all(new_files[p]==info for p,info in old_files.items()) and
             current[0]==prior[0]+(1 if appended else 0) and
             current[1]==prior[1]+(len(raw) if appended else 0),'WRITER:CENSUS_CHANGED')
        return observed

    @_entry_operation
    def create(self):
        need(self.phase=='PRIVATE_BEFORE_CREATE','WRITER:NO_RETRY')
        self.phase='CREATE_ENTERED'
        try:
            self._census();need(len(self._names(ENTRIES,30))<29,'WRITER:OPERATION_LIMIT')
            os.mkdir(self.root,0o700);self.created=True;self._directory(self.root);self._sync(ENTRIES)
            self.phase='CREATED'
        except BaseException as e:
            self.phase='FAILED_UNCERTAIN';raise self._remember(e)

    def _readback(self,path,raw):
        before=path.lstat();slot=None;primary=None;data=None
        try:
            need(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode)==0o444 and
                 before.st_uid==os.getuid() and before.st_nlink==1 and before.st_size==len(raw),'WRITER:READBACK')
            slot=self._acquire(path,os.O_RDONLY|os.O_NONBLOCK)
            need(identity(os.fstat(slot[0]))==identity(before),'WRITER:READBACK')
            chunks=[];count=0
            while True:
                block=os.read(slot[0],min(65536,CAP+1-count))
                if not block:break
                chunks.append(block);count+=len(block);need(count<=CAP,'WRITER:READBACK')
            data=b''.join(chunks)
            need(data==raw and identity(os.fstat(slot[0]))==identity(before)==identity(path.lstat()),'WRITER:READBACK')
        except BaseException as e:primary=self._remember(e)
        finally:
            if slot is not None and slot[1]=='OWNED':
                try:self._close(slot)
                except BaseException as e:primary=self._remember(e)
        if primary is not None:raise primary
        return {'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'mode':0o444}

    def _publish_bytes(self,name,raw):
        basename(name)
        standard=name.endswith('.json') and name[:-5] in RECORDS and name!='ENTRY_MANIFEST.json'
        native=any(name.startswith(p) and len(name)==len(p)+8 and name[-8:-5].isascii() and name[-8:-5].isdigit() and name.endswith('.json') for p in ('NATIVE-REQUEST-','NATIVE-RESULT-'))
        manifest=name=='ENTRY-%06d.json'%self.version
        need(standard or native or manifest,'WRITER:FIXED_NAME')
        need(type(raw) is bytes and len(raw)<=CAP,'WRITER:RAW_TYPE_LIMIT')
        need(self.created and self.phase=='CREATED' and self.first is None and not self.unknown,'WRITER:BLOCKED')
        boundary=self._publication_before(1,len(raw));path=self.root/name
        slot=None;primary=None
        try:
            slot=self._acquire(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL)
            st=os.fstat(slot[0]);need(stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode)==0o600 and
                 st.st_uid==os.getuid() and st.st_nlink==1 and st.st_size==0 and identity(st)==identity(path.lstat()),'WRITER:FRESH')
            offset=0
            while offset<len(raw):
                n=os.write(slot[0],raw[offset:offset+65536]);need(type(n) is int and 0<n<=min(65536,len(raw)-offset),'WRITER:WRITE')
                offset+=n
            os.fsync(slot[0]);os.fchmod(slot[0],0o444);os.fsync(slot[0])
        except BaseException as e:primary=self._remember(e)
        finally:
            if slot is not None and slot[1]=='OWNED':
                try:self._close(slot)
                except BaseException as e:primary=self._remember(e)
        if primary is not None:
            self.phase='FAILED_UNCERTAIN';raise primary
        try:
            return self._sealed_original(path,raw,boundary,True)
        except BaseException as e:
            self.phase='FAILED_UNCERTAIN';raise self._remember(e)

    def _record(self,kind,obj):
        need(self.created and self.phase=='CREATED' and not self.unknown and self.first is None,'WRITER:BLOCKED')
        need(type(kind) is str and kind in RECORDS,'WRITER:KIND');plain(obj)
        need(type(obj) is dict and obj.get('schema')==RECORDS[kind]['schema'] and
             set(obj)==set(RECORDS[kind]['keys']) and obj.get('attempt_id')==self.attempt_id,'WRITER:SCHEMA')
        self._call('validate_original_record',kind,obj)
        for field,prior in (('command_pin','COMMAND'),('reservation_pin','RESERVATION'),
                            ('permission_pin','PERMISSION'),('meter_start_pin','METER_START'),
                            ('meter_body_pin','METER_BODY'),('native_chain_pin','NATIVE_CHAIN')):
            if field in obj:
                need(prior in self.pins and obj[field]==self.pins[prior],'WRITER:CORRELATION')
        if kind=='COMMAND':
            need('PERMISSION' in self.values,'WRITER:ORDER')
            q=self.values['PERMISSION']
            need(obj['operation_class']==q['operation_class'] and all(obj[k]==q[k] for k in ('source_packet_pin','operating_profile_pin','review_contract_pin')),'WRITER:CORRELATION')
        elif kind=='RESERVATION':
            need(obj['settlement_route']==self.values['COMMAND']['settlement_route'] and all(obj[k]==self.values['PERMISSION'][k] for k in ('body_reservation_ns','admin_policy_ns')),'WRITER:CORRELATION')
        elif kind=='PRE_ENTRY':
            need(len(self.calls)==1 and self.pending==0 and obj['provider_request_pin']==self.calls[0]['request_pin'] and
                 obj['execution_started'] is False and obj['expected_meter_start_path']==str(self.root/'METER_START.json') and
                 obj['expected_native_chain_path']==str(self.root/'NATIVE_CHAIN.json'),'WRITER:PRE_ENTRY')
        elif kind=='METER_START':
            need('PRE_ENTRY' in self.pins,'WRITER:ORDER')
        elif kind=='METER_BODY':
            need(obj['body']['begin_ns']==self.values['METER_START']['body_begin_ns'],'WRITER:CORRELATION')
        elif kind=='FINANCIAL_ADJUDICATION':
            need(obj['source_packet_pin']==self.values['COMMAND']['source_packet_pin'] and obj['review_contract_pin']==self.values['COMMAND']['review_contract_pin'],'WRITER:CORRELATION')
        return obj

    @_entry_operation
    def emit(self,kind,fields):
        need(type(kind) is str and kind in RECORDS and kind in ('PERMISSION','COMMAND','RESERVATION','PRE_ENTRY'),'WRITER:ORIGINAL_REVIEW_ONLY')
        plain(fields);need(type(fields) is dict and set(fields)==set(RECORDS[kind]['keys'])-{'schema','attempt_id'},'WRITER:SCHEMA')
        obj=dict(fields,schema=RECORDS[kind]['schema'],attempt_id=self.attempt_id)
        self._record(kind,obj);raw=canonical(obj);p=self._publish_bytes(kind+'.json',raw)
        self.pins[kind]=dict(p);self.values[kind]=json.loads(canonical(obj));return dict(p)

    @_entry_operation
    def receive(self,kind,raw,origin_pin):
        need(type(kind) is str and kind in RECORDS and kind not in ('ENTRY_MANIFEST','NATIVE_CHAIN'),'WRITER:KIND')
        need(type(raw) is bytes,'WRITER:RAW_TYPE');pin_data(origin_pin,MAX_VALUE)
        if len(raw)>CAP or origin_pin['bytes']!=len(raw):
            self._unresolved({'kind':kind,'origin_pin':origin_pin,'reason':'EXTERNAL_OVERSIZE_OR_LENGTH_UNKNOWN','hash_verified':False})
            return {'retained_external':origin_pin,'published_pin':None,'execution_permission':False}
        need(hashlib.sha256(raw).hexdigest()==origin_pin['sha256'],'WRITER:ORIGIN_HASH')
        try:
            obj=self._call('metadata_decode',raw);self._record(kind,obj)
        except BaseException as error:
            self._unresolved({'kind':kind,'origin_pin':origin_pin,'reason':'EXTERNAL_UNSUPPORTED_OR_CORRELATION','hash_verified':True},error)
            return {'retained_external':origin_pin,'published_pin':None,'execution_permission':False}
        path=self.root/(kind+'.json')
        if origin_pin['path']==str(path):
            # Explicit observation of independently produced original at its PLANNED path.
            # Never fallback from an exclusive-create failure or accept old entry reuse.
            need(self.created and kind not in self.pins,'WRITER:NO_RETRY')
            boundary=self._publication_before()
            p=self._sealed_original(path,raw,boundary,False)
            need(p==origin_pin,'WRITER:ORIGIN_METADATA')
        else:p=self._publish_bytes(kind+'.json',raw)
        need(len(self.origins)<128,'WRITER:ORIGIN_LIMIT')
        self.origins.append(dict(origin_pin));self.pins[kind]=dict(p);self.values[kind]=json.loads(canonical(obj))
        if kind=='METER_START' and origin_pin['path']==str(self.root/'METER_START.json'):
            self._received_start_original=(bytes(raw),dict(origin_pin))
        return {'retained_external':origin_pin,'published_pin':p,'execution_permission':False}

    @_entry_operation
    def receive_started_manifest(self,raw,origin_pin):
        """Observe exactly the sealed meter-produced ENTRY-000001 once.

        A source-private persistent parent must already have emitted RESERVED
        and received the genuine planned START. All predecessor custody, exact
        metadata and source-bound F4 successor checks precede private advancement.
        No manifest/pin supplied here creates a native owner or approval.
        """
        need(self.created and self.phase=='CREATED' and self.version==1 and
             self.last_phase=='RESERVED' and not self._started_reconciled and
             self._reserved_manifest_raw is not None and
             self._reserved_manifest_pin is not None and
             self._received_start_original is not None and not self.unresolved,
             'WRITER:STARTED_ONE_STEP')
        need(type(raw) is bytes and len(raw)<=CAP,'WRITER:RAW_TYPE_LIMIT')
        pin_data(origin_pin)
        need(origin_pin['path']==str(self.root/'ENTRY-000001.json') and
             origin_pin['mode']==0o444 and origin_pin['bytes']==len(raw) and
             origin_pin['sha256']==hashlib.sha256(raw).hexdigest(),
             'WRITER:STARTED_ORIGINAL')
        before=self._call('metadata_decode',self._reserved_manifest_raw)
        need(canonical(before)==self._reserved_manifest_raw and
             before==self.last_manifest_obj and
             self.last_manifest==self._reserved_manifest_pin and
             before['phase']=='RESERVED' and before['meter_start_pin'] is None,
             'WRITER:PRIVATE_PREDECESSOR')
        start_raw,start_origin=self._received_start_original
        need(start_origin==self.pins.get('METER_START') and
             start_origin['path']==str(self.root/'METER_START.json') and
             self._call('metadata_decode',start_raw)==self.values['METER_START'],
             'WRITER:STARTED_START')
        observed=self._call('metadata_decode',raw)
        expected=started_successor_data(before,observed,start_origin,self.version,
                                        self.last_phase,self._started_reconciled)
        need(observed==expected and canonical(observed)==raw,
             'WRITER:STARTED_EXACT')
        self._call('validate_original_record','ENTRY_MANIFEST',observed)
        self._call('_manifest_successor',before,observed)
        # Recheck genuine predecessor and START originals as well as ENTRY1.
        boundary=self._publication_before()
        previous_path=Path(self._reserved_manifest_pin['path'])
        need(self._readback(previous_path,self._reserved_manifest_raw)==
             self._reserved_manifest_pin,'WRITER:PRIVATE_PREDECESSOR')
        need(self._readback(self.root/'METER_START.json',start_raw)==start_origin,
             'WRITER:STARTED_START')
        sealed=self._sealed_original(self.root/'ENTRY-000001.json',raw,boundary,False)
        need(sealed==origin_pin,'WRITER:ORIGIN_METADATA')
        need(len(self.origins)<128,'WRITER:ORIGIN_LIMIT')
        self.origins.append(dict(origin_pin))
        self.last_manifest=dict(sealed);self.last_manifest_obj=json.loads(raw)
        self.last_phase='STARTED';self.version=2;self._started_reconciled=True
        return {'retained_external':dict(origin_pin),'published_pin':dict(sealed),
                'execution_permission':False}

    def _unresolved(self,observation,error=None):
        need(len(self.unresolved)<128,'WRITER:UNRESOLVED_LIMIT')
        self.unresolved.append(json.loads(canonical(observation)))
        if error is not None:self.observation_errors.append(error)

    def _decode_original(self,raw,origin_pin):
        need(type(raw) is bytes,'WRITER:RAW_TYPE');pin_data(origin_pin,MAX_VALUE)
        if len(raw)>CAP or origin_pin['bytes']!=len(raw):
            self._unresolved({'kind':'NATIVE','origin_pin':origin_pin,'reason':'EXTERNAL_OVERSIZE_OR_LENGTH_UNKNOWN','hash_verified':False});return None
        need(hashlib.sha256(raw).hexdigest()==origin_pin['sha256'],'WRITER:ORIGIN_HASH')
        try:
            obj=self._call('metadata_decode',raw);plain(obj)
            return obj
        except BaseException as error:
            self._unresolved({'kind':'NATIVE','origin_pin':origin_pin,'reason':'EXTERNAL_MALFORMED','hash_verified':True},error);return None

    def _request(self,tool,obj):
        need(type(obj) is dict,'WRITER:NATIVE_REQUEST')
        if tool=='exec_command':
            allowed={'cmd','workdir','login','shell','tty','yield_time_ms','max_output_tokens','sandbox_permissions','justification','prefix_rule'}
            need(not self.calls and {'cmd','workdir'}<=set(obj)<=allowed,'WRITER:NATIVE_REQUEST')
            need(obj['cmd']==self.values['COMMAND']['exact_shell_command'] and obj['workdir']==str(W),'WRITER:NATIVE_COMMAND')
            for k,v in obj.items():
                if k in ('login','tty'):need(type(v) is bool,'WRITER:NATIVE_REQUEST')
                elif k in ('yield_time_ms','max_output_tokens'):need(type(v) is int and 0<=v<=MAX_VALUE,'WRITER:NATIVE_REQUEST')
                elif k=='prefix_rule':need(type(v) is list and len(v)<=32 and all(type(x) is str and len(x)<=4096 for x in v),'WRITER:NATIVE_REQUEST')
                else:need(type(v) is str and len(v)<=CAP,'WRITER:NATIVE_REQUEST')
        else:
            need(self.calls and not self.terminal and self.session is not None and 'session_id' in obj and
                 set(obj)<={'session_id','chars','yield_time_ms','max_output_tokens'},'WRITER:NATIVE_REQUEST')
            need(type(obj['session_id']) is int and obj['session_id']==self.session,'WRITER:SESSION')
            for k,v in obj.items():
                if k=='chars':need(type(v) is str and len(v)<=CAP,'WRITER:NATIVE_REQUEST')
                else:need(type(v) is int and 0<=v<=MAX_VALUE,'WRITER:NATIVE_REQUEST')

    def _result(self,obj):
        need(type(obj) is dict and {'output','wall_time_seconds'}<=set(obj)<=
             {'output','wall_time_seconds','session_id','exit_code','chunk_id','original_token_count'},'WRITER:NATIVE_RESULT')
        need(type(obj['output']) is str and len(obj['output'])<=CAP,'WRITER:NATIVE_RESULT')
        wall=obj['wall_time_seconds']
        # Lexical diagnostic only. No conversion to elapsed/charged nanoseconds.
        need((type(wall) is int and 0<=wall<=MAX_VALUE) or
             (type(wall) is str and 1<=len(wall)<=128 and wall.count('.')<=1 and
              all(c in '0123456789.' for c in wall) and any(c in '0123456789' for c in wall)),'WRITER:WALL_DIAGNOSTIC')
        if 'chunk_id' in obj:need(type(obj['chunk_id']) is str and len(obj['chunk_id'])<=128,'WRITER:NATIVE_RESULT')
        if 'original_token_count' in obj:need(type(obj['original_token_count']) is int and 0<=obj['original_token_count']<=MAX_VALUE,'WRITER:NATIVE_RESULT')
        session=obj.get('session_id');code=obj.get('exit_code')
        if code is None:
            need(type(session) is int and 0<=session<=MAX_VALUE and (self.session is None or session==self.session),'WRITER:SESSION')
            return session,False
        need(type(code) is int and -(1<<63)<=code<=MAX_VALUE,'WRITER:NATIVE_EXIT')
        need(session is None or (type(session) is int and session==self.session),'WRITER:SESSION')
        return self.session,True

    @_entry_operation
    def native_request(self,tool,raw,origin_pin):
        need(type(tool) is str and tool in ('exec_command','write_stdin') and self.pending is None and len(self.calls)<MAX_STEPS and not self.terminal and not self.unresolved and 'NATIVE_CHAIN' not in self.pins,'WRITER:NATIVE_PLAN')
        need('RESERVATION' in self.pins,'WRITER:ORDER')
        obj=self._decode_original(raw,origin_pin)
        if obj is None:return None
        try:self._request(tool,obj)
        except BaseException as error:
            self._unresolved({'kind':'NATIVE_REQUEST','origin_pin':origin_pin,'reason':'EXTERNAL_UNSUPPORTED_REQUEST','hash_verified':True},error);return None
        ordinal=len(self.calls);p=self._publish_bytes('NATIVE-REQUEST-%03d.json'%ordinal,raw)
        self.calls.append({'ordinal':ordinal,'tool':tool,'request_pin':dict(p),'original_tool_result_pin':None})
        self.pending=ordinal;return p

    @_entry_operation
    def native_result(self,raw,origin_pin):
        need(self.pending is not None and 'PRE_ENTRY' in self.pins and not self.unresolved,'WRITER:NATIVE_ORDER')
        obj=self._decode_original(raw,origin_pin)
        if obj is None:return None
        try:session,terminal=self._result(obj)
        except BaseException as error:
            self._unresolved({'kind':'NATIVE_RESULT','origin_pin':origin_pin,'reason':'EXTERNAL_UNSUPPORTED_RESULT','hash_verified':True},error);return None
        p=self._publish_bytes('NATIVE-RESULT-%03d.json'%self.pending,raw)
        self.calls[self.pending]['original_tool_result_pin']=dict(p);self.pending=None
        self.session=session;self.terminal=terminal;return p

    @_entry_operation
    def native_chain(self):
        need(self.calls and self.pending is None and not self.unresolved,'WRITER:NATIVE_INCOMPLETE')
        obj={'schema':RECORDS['NATIVE_CHAIN']['schema'],'attempt_id':self.attempt_id,
             'command_pin':self.pins['COMMAND'],'reservation_pin':self.pins['RESERVATION'],'calls':self.calls}
        self._record('NATIVE_CHAIN',obj);p=self._publish_bytes('NATIVE_CHAIN.json',canonical(obj))
        self.pins['NATIVE_CHAIN']=dict(p);self.values['NATIVE_CHAIN']=json.loads(canonical(obj))
        if not self.terminal:self._unresolved({'kind':'NATIVE_CHAIN','reason':'NO_SUPPORTED_TERMINAL','hash_verified':False})
        return dict(p)

    @_entry_operation
    def manifest(self,phase,formal_start_pin=None,formal_receipt_pin=None):
        need(type(phase) is str and phase in ('RESERVED','STARTED','OBSERVED_AWAIT_REVIEW','CLOSED_KNOWN','OPEN_UNCERTAIN','FORMAL_AWAIT_CLOSE'),'WRITER:PHASE')
        if self.unresolved:need(phase=='OPEN_UNCERTAIN','WRITER:UNRESOLVED')
        need(self.version<128 and self.last_phase not in ('CLOSED_KNOWN','OPEN_UNCERTAIN'),'WRITER:MANIFEST_TERMINAL')
        rank={'RESERVED':0,'STARTED':1,'OBSERVED_AWAIT_REVIEW':2,'FORMAL_AWAIT_CLOSE':3,'CLOSED_KNOWN':4,'OPEN_UNCERTAIN':4}
        if self.last_phase is not None:need(rank[phase]>=rank[self.last_phase],'WRITER:MANIFEST_REGRESSION')
        need('COMMAND' in self.pins and 'RESERVATION' in self.pins,'WRITER:ORDER')
        if phase=='CLOSED_KNOWN':
            need(self.values['COMMAND']['settlement_route']=='MANUAL_ONLY' and self.terminal and
                 'FINANCIAL_ADJUDICATION' in self.values and self.values['FINANCIAL_ADJUDICATION']['financial_status']=='CLOSED_KNOWN','WRITER:INDEPENDENT_CLOSURE')
        if phase=='FORMAL_AWAIT_CLOSE':need(self.values['COMMAND']['settlement_route']=='FORMAL_OUTER','WRITER:FORMAL_ROUTE')
        if phase in ('OBSERVED_AWAIT_REVIEW','CLOSED_KNOWN','FORMAL_AWAIT_CLOSE'):
            need(all(k in self.pins for k in ('PRE_ENTRY','METER_START','METER_BODY','NATIVE_CHAIN')),'WRITER:OBSERVATION_INCOMPLETE')
        if phase in ('CLOSED_KNOWN','FORMAL_AWAIT_CLOSE'):
            need(self.terminal and 'FINANCIAL_ADJUDICATION' in self.values and self.values['FINANCIAL_ADJUDICATION']['financial_status']=='CLOSED_KNOWN','WRITER:INDEPENDENT_CLOSURE')
            b=self.values['METER_BODY'];a=self.values['FINANCIAL_ADJUDICATION']
            need(b['body']['state']=='KNOWN' and a['accepted_body_ns']==b['body']['elapsed_ns'] and
                 a['admin_policy_ns']==self.values['PERMISSION']['admin_policy_ns'] and
                 a['known_policy_ns']==a['accepted_body_ns']+a['admin_policy_ns'] and
                 b['owned_cleanup']=='KNOWN_CLOSED' and b['errors']['io_unknown'] is False and
                 a['cleanup_status']=='KNOWN_CLOSED' and a['tail_status']=='ADMIN_ONLY_OPEN','WRITER:KNOWN_FACTS')
        # An independent adjudicator must inspect complete group observation/raw
        # lineage. Neither Tool exit nor last-started-child scalar zero is PASS.
        # This is an ENTRY observation, never financial HEAD/STATE or formal CLOSE.
        if phase in ('RESERVED','STARTED'):need('PRE_ENTRY' in self.pins,'WRITER:ORDER')
        if phase=='STARTED':need('METER_START' in self.pins,'WRITER:ORDER')
        if formal_start_pin is not None:pin_data(formal_start_pin)
        if formal_receipt_pin is not None:pin_data(formal_receipt_pin)
        obj={'schema':RECORDS['ENTRY_MANIFEST']['schema'],'attempt_id':self.attempt_id,
             'command_pin':self.pins.get('COMMAND'),'reservation_pin':self.pins.get('RESERVATION'),
             'pre_entry_pin':self.pins.get('PRE_ENTRY'),'meter_start_pin':self.pins.get('METER_START'),
             'meter_body_pin':self.pins.get('METER_BODY'),'native_chain_pin':self.pins.get('NATIVE_CHAIN'),
             'financial_adjudication_pin':self.pins.get('FINANCIAL_ADJUDICATION'),
             'settlement_route':self.values['COMMAND']['settlement_route'],
             'formal_start_pin':formal_start_pin,'formal_receipt_pin':formal_receipt_pin,'phase':phase}
        if self.last_manifest_obj is not None:
            for k,v in self.last_manifest_obj.items():
                if k.endswith('_pin') and v is not None:need(obj[k]==v,'WRITER:MANIFEST_REBIND')
        self._call('validate_original_record','ENTRY_MANIFEST',obj)
        if self.last_manifest_obj is not None:
            self._call('_manifest_successor',self.last_manifest_obj,obj)
        name='ENTRY-%06d.json'%self.version;p=self._publish_bytes(name,canonical(obj))
        self.last_manifest=dict(p);self.last_manifest_obj=json.loads(canonical(obj));self.last_phase=phase;self.version+=1
        if self.version==1 and phase=='RESERVED':
            self._reserved_manifest_raw=canonical(obj);self._reserved_manifest_pin=dict(p)
        return dict(p)


if __name__=='__main__':
    raise SystemExit(78)  # No actual parent-role input transport/grant is configured.
