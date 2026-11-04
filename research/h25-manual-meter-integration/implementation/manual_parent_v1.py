"""Fixed architecture-C original parent/caller and receipt reconciliation.

SOURCE ONLY. The admitted external parent/native-provider/source-custody premise
of original_records remains mandatory. Request records returned here are exact
reviewed request DATA, never a Tool invocation or an execution permission. The
same private parent remains alive across the actual provider request/results;
there is no constructor from saved JSON or receipt and no automatic retry.

Predecessor: original_records.py at ff7df8391c3bb3f5518ce43682ba4c1e41380e3e,
a6e9cd9cfcfc5300601d668b7a498b1c6cd13714ebea79122bd97faa0c8a7a8e;
bootstrap transport follows its retained fixed-loader donor. Original authors
retain credit. Substantial Pro, Codex and Sol Max assistance.
"""
import builtins
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import sys
from types import ModuleType

W=Path('/home/d3lerium/.codex/.chatgpt-projects/g-p-6ad5817fd84881918865926b6fd51453')
R=W/'outputs/h25-data-handling-20261028'
# Fixed prospective installation subject, inside unchanged F4 pin namespace.
# Authored package bytes remain in this round; installation is a separate gate.
PACKAGE=R/'areas/manual-integration-v29'
LOADER=PACKAGE/'manual_loader_v1.py'
METER=PACKAGE/'manual_meter_v1.py'
# Exact final source selection. These pins do not grant installation/execution.
LOADER_PIN={'bytes':18257,'sha256':'0e81529af2bf0c56863372379da1aafc4c4f762982d79df7282b2b2cd23e0620','mode':0o444,'path':str(LOADER)}
METER_PIN={'bytes':33958,'sha256':'d20004e289ca930d0d09acbcab200758b9df8e20df1152510171a37448d99b03','mode':0o444,'path':str(METER)}
PLAN_ROOT=R/'runtime/manual-operations'
ENV={'PATH':'/usr/bin:/bin','PYTHONHASHSEED':'0','LANG':'C.UTF-8',
     'LC_ALL':'C.UTF-8','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1'}
USED=[False]
RETAINED=[]
_TOKEN=object()


class ParentStop(RuntimeError):
    pass


def need(condition,message):
    if not condition:raise ParentStop(message)


def _canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,
                       allow_nan=False)+'\n').encode('ascii')


def exact_manual_command(action,profile,attempt_id):
    """Pure fixed command selector, shared source contract with manual meter."""
    need(type(action) is str and action in ('INITIALIZE','REFRESH','CLOSE'),
         'PARENT:ACTION')
    need(type(profile) is str and profile in ('normal','optimized'),'PARENT:PROFILE')
    need(type(attempt_id) is str and 1<=len(attempt_id)<=64 and
         all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in attempt_id),
         'PARENT:ID')
    args=['/usr/bin/python3.12','-S','-s','-P','-B']
    if profile=='optimized':args.append('-O')
    args.extend((str(METER),action,profile,str(PLAN_ROOT/(attempt_id+'.json')),
                 METER_PIN['sha256'],str(METER_PIN['bytes'])))
    # No PLAN hash in the command: PLAN contains genuine COMMAND/PRE_ENTRY pins.
    # Binding its hash here would create a cryptographic reference cycle.
    body=R/'control/prospective-financial-v1/entries'/attempt_id/'METER_BODY.json'
    detail=PLAN_ROOT/(attempt_id+'.stderr.json')
    env_args=['/usr/bin/env','-i']+[key+'='+value for key,value in ENV.items()]
    command=' '.join(shlex.quote(item) for item in env_args+args)
    return 'umask 077\nset -C\nexec '+command+' > '+shlex.quote(str(body))+' 2> '+shlex.quote(str(detail))


def _source_identity(st):
    return (st.st_dev,st.st_ino,st.st_mode,st.st_uid,st.st_nlink,st.st_size,
            st.st_mtime_ns,st.st_ctime_ns)


class _Startup:
    """Fixed loader-only transport; ownership exists before each native open."""
    def __init__(self):
        self.fd=None;self.phase='NEW';self.first=None;self.secondary=[]
        self.unknown=False;self.module=None

    def remember(self,error):
        if self.first is None:self.first=error
        elif error is not self.first and all(error is not e for e in self.secondary):
            if len(self.secondary)<32:self.secondary.append(error)
            else:self.unknown=True
        return self.first

    def load(self):
        need(self.phase=='NEW','PARENT:STARTUP_ONE_USE')
        self.phase='ACQUIRE_PENDING'
        try:
            need(LOADER_PIN['bytes']>0 and LOADER_PIN['mode']==0o444,
                 'PARENT:FINAL_SOURCE_SELECTION')
            before=LOADER.lstat()
            need(LOADER.resolve(strict=True)==LOADER and stat.S_ISREG(before.st_mode) and
                 stat.S_IMODE(before.st_mode)==0o444 and before.st_uid==os.getuid() and
                 before.st_nlink==1 and before.st_size==LOADER_PIN['bytes'],
                 'PARENT:LOADER_SOURCE')
            self.fd=os.open(LOADER,os.O_RDONLY|os.O_NONBLOCK|os.O_NOFOLLOW|os.O_CLOEXEC)
            self.phase='OWNED'
            need(_source_identity(os.fstat(self.fd))==_source_identity(before),
                 'PARENT:LOADER_SOURCE')
            pieces=[];count=0
            while True:
                block=os.read(self.fd,min(65536,2097153-count))
                if not block:break
                pieces.append(block);count+=len(block)
                need(count<=2097152,'PARENT:LOADER_CAP')
            raw=b''.join(pieces)
            need(count==LOADER_PIN['bytes'] and hashlib.sha256(raw).hexdigest()==
                 LOADER_PIN['sha256'] and _source_identity(os.fstat(self.fd))==
                 _source_identity(before)==_source_identity(LOADER.lstat()),
                 'PARENT:LOADER_SOURCE')
        except BaseException as error:
            if self.phase=='ACQUIRE_PENDING':self.unknown=True
            self.remember(error)
        finally:
            if self.phase=='OWNED':
                self.phase='CLOSE_ENTERED'
                try:os.close(self.fd);self.phase='CLOSED'
                except BaseException as error:
                    self.phase='CLOSE_UNKNOWN';self.unknown=True;self.remember(error)
        if self.first is not None:raise self.first
        need(not self.unknown and self.phase=='CLOSED','PARENT:STARTUP_UNKNOWN')
        name='h25_fixed_manual_parent_loader_v29'
        need(name not in sys.modules,'PARENT:PRIVATE_MODULE_REUSE')
        self.module=ModuleType(name)
        self.module.__dict__.update(__name__=name,__file__=str(LOADER),__package__=None,
                                    __spec__=None,__builtins__=builtins)
        sys.modules[name]=self.module
        RETAINED.append((self,raw,self.module))
        exec(compile(raw,str(LOADER),'exec',dont_inherit=True),self.module.__dict__)
        return self.module


def _parent_operation(method):
    def run(self,*args,**kwargs):
        need(self.first is None and not self.unknown and self.phase not in
             ('SETTLED','FAILED_UNCERTAIN'),'PARENT:BLOCKED')
        try:return method(self,*args,**kwargs)
        except BaseException as error:
            self.phase='FAILED_UNCERTAIN'
            raise self.remember(error)
    return run


class _ManualParent:
    """Live original evidence object plus fixed source-role dispatch selection."""
    def __init__(self,token,loaded,action,profile,attempt_id):
        need(token is _TOKEN,'PARENT:PRIVATE_FACTORY')
        self.loaded=loaded;self.action=action;self.profile=profile
        self.phase='NEW';self.first=None;self.secondary=[];self.unknown=False
        self.plan_slot=[None,'FREE'];self.plan_pin=None;self.prepared_request=None
        self.started=False;self.receipts=False;self.reviewed=False
        self.settlement_entered=False;self.settlement=None;self.settlement_result=None
        self._current_snapshot_raw=None;self.current_snapshot_receipt_pin=None
        self.detail_pin=None
        self.evidence=loaded.writer.bind_parent_writer(loaded.F,
            {'path':str(loaded.writer.F4_SOURCE),'bytes':151228,
             'sha256':'a0c2ab55aaf47350bb51fa98e07bc7b520c388742f2da06820d2d10f7d8f506d',
             'mode':0o444})(attempt_id)
        self.attempt_id=self.evidence.attempt_id
        self.plan_path=PLAN_ROOT/(self.attempt_id+'.json')
        self.command=exact_manual_command(action,profile,self.attempt_id)
        self.contexts=[]

    def remember(self,error):
        if self.first is None:self.first=error
        elif error is not self.first and all(error is not e for e in self.secondary):
            if len(self.secondary)<32:self.secondary.append(error)
            else:self.unknown=True
        return self.first

    def _plan_directory(self):
        # Fixed external non-financial staging directory must already exist;
        # creation/custody and command authorization belong to the parent TCB.
        for path in (R,R/'runtime',PLAN_ROOT):
            st=path.lstat()
            need(path.resolve(strict=True)==path and stat.S_ISDIR(st.st_mode) and
                 st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==0o700,
                 'PARENT:PLAN_DIRECTORY')

    def _publish_plan(self,plan):
        self.loaded.F.financial_plain(plan)
        raw=_canonical(plan)
        need(len(raw)<=8_388_608,'PARENT:PLAN_CAP')
        self._plan_directory();self.plan_slot[:]=[None,'PENDING']
        primary=None
        try:
            self.plan_slot[0]=os.open(self.plan_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|
                                     os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
            self.plan_slot[1]='OWNED'
            before=os.fstat(self.plan_slot[0])
            need(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode)==0o600 and
                 before.st_uid==os.getuid() and before.st_nlink==1 and before.st_size==0 and
                 _source_identity(before)==_source_identity(self.plan_path.lstat()),
                 'PARENT:PLAN_FRESH')
            offset=0
            while offset<len(raw):
                n=os.write(self.plan_slot[0],raw[offset:offset+65536])
                need(type(n) is int and 0<n<=min(65536,len(raw)-offset),'PARENT:PLAN_WRITE')
                offset+=n
            os.fsync(self.plan_slot[0]);os.fchmod(self.plan_slot[0],0o444)
            os.fsync(self.plan_slot[0])
        except BaseException as error:
            if self.plan_slot[1]=='PENDING':self.unknown=True
            primary=self.remember(error)
        finally:
            if self.plan_slot[1]=='OWNED':
                self.plan_slot[1]='CLOSE_ENTERED'
                try:os.close(self.plan_slot[0]);self.plan_slot[1]='CLOSED'
                except BaseException as error:
                    self.plan_slot[1]='CLOSE_UNKNOWN';self.unknown=True
                    primary=self.remember(error)
        if primary is not None:raise primary
        # Readback owns a distinct single-close descriptor; no write retry.
        self.plan_slot[:]=[None,'PENDING']
        try:
            self.plan_slot[0]=os.open(self.plan_path,os.O_RDONLY|os.O_NONBLOCK|
                                     os.O_NOFOLLOW|os.O_CLOEXEC)
            self.plan_slot[1]='OWNED';before=os.fstat(self.plan_slot[0])
            need(stat.S_IMODE(before.st_mode)==0o444 and before.st_size==len(raw) and
                 _source_identity(before)==_source_identity(self.plan_path.lstat()),
                 'PARENT:PLAN_READBACK')
            actual=b''
            while len(actual)<=len(raw):
                block=os.read(self.plan_slot[0],min(65536,len(raw)+1-len(actual)))
                if not block:break
                actual+=block
            need(actual==raw and _source_identity(os.fstat(self.plan_slot[0]))==
                 _source_identity(before)==_source_identity(self.plan_path.lstat()),
                 'PARENT:PLAN_READBACK')
        except BaseException as error:
            if self.plan_slot[1]=='PENDING':self.unknown=True
            primary=self.remember(error)
        finally:
            if self.plan_slot[1]=='OWNED':
                self.plan_slot[1]='CLOSE_ENTERED'
                try:os.close(self.plan_slot[0]);self.plan_slot[1]='CLOSED'
                except BaseException as error:
                    self.plan_slot[1]='CLOSE_UNKNOWN';self.unknown=True
                    primary=self.remember(error)
        if primary is not None:raise primary
        self.plan_slot[:]=[None,'PENDING']
        try:
            self.plan_slot[0]=os.open(PLAN_ROOT,os.O_RDONLY|os.O_DIRECTORY|
                                     os.O_NOFOLLOW|os.O_CLOEXEC)
            self.plan_slot[1]='OWNED';os.fsync(self.plan_slot[0]);self._plan_directory()
        except BaseException as error:
            if self.plan_slot[1]=='PENDING':self.unknown=True
            primary=self.remember(error)
        finally:
            if self.plan_slot[1]=='OWNED':
                self.plan_slot[1]='CLOSE_ENTERED'
                try:os.close(self.plan_slot[0]);self.plan_slot[1]='CLOSED'
                except BaseException as error:
                    self.plan_slot[1]='CLOSE_UNKNOWN';self.unknown=True
                    primary=self.remember(error)
        if primary is not None:raise primary
        return {'path':str(self.plan_path),'bytes':len(raw),
                'sha256':hashlib.sha256(raw).hexdigest(),'mode':0o444}

    @_parent_operation
    def prepare(self,permission_fields,command_fields,reservation_fields,
                original_native_request,original_native_request_pin,operation_fields):
        """Emit original predispatch records from already admitted review inputs.

        The native request is the externally retained original direct request;
        no request/result is fabricated here. External source custody must bind
        it to the exact Tool call, whose request remains returned DATA until the
        genuinely authorized provider performs it.
        """
        need(self.phase=='NEW','PARENT:NO_RETRY')
        e=self.evidence;F=self.loaded.F
        e.create();e.emit('PERMISSION',permission_fields)
        expected_class='METADATA_CLOSER' if self.action=='CLOSE' else 'METADATA_INITIALIZER'
        need(command_fields['operation_class']==expected_class and
             command_fields['settlement_route']=='MANUAL_ONLY' and
             command_fields['exact_shell_command']==self.command,
             'PARENT:FIXED_COMMAND_ROLE')
        e.emit('COMMAND',command_fields);e.emit('RESERVATION',reservation_fields)
        request=F.metadata_decode(original_native_request)
        need(type(request) is dict and request.get('cmd')==self.command and
             request.get('workdir')==str(W) and request.get('shell')=='/bin/bash' and
             request.get('login') is False and request.get('tty',False) is False,
             'PARENT:ORIGINAL_DIRECT_REQUEST')
        request_pin=e.native_request('exec_command',original_native_request,
                                     original_native_request_pin)
        need(request_pin is not None and not e.unresolved,'PARENT:ORIGINAL_DIRECT_REQUEST')
        e.emit('PRE_ENTRY',{'command_pin':e.pins['COMMAND'],
            'reservation_pin':e.pins['RESERVATION'],'permission_pin':e.pins['PERMISSION'],
            'expected_meter_start_path':str(e.root/'METER_START.json'),
            'expected_native_chain_path':str(e.root/'NATIVE_CHAIN.json'),
            'execution_started':False,'provider_request_pin':request_pin})
        reserved=e.manifest('RESERVED')
        F.financial_plain(operation_fields)
        allowed={'predecessor_snapshot','extra_wires','approved_opening','expected_head_pin',
                 'pending_path','policy_pins','phase','phase_release_sha256','cleanup_ns'}
        need(type(operation_fields) is dict and set(operation_fields)==allowed,
             'PARENT:OPERATION_FIELDS')
        plan=dict(operation_fields,schema='fresh-fixed-manual-operation-v1',
            attempt_id=self.attempt_id,action=self.action,profile=self.profile,
            command_pin=e.pins['COMMAND'],reservation_pin=e.pins['RESERVATION'],
            permission_pin=e.pins['PERMISSION'],pre_entry_pin=e.pins['PRE_ENTRY'],
            reserved_manifest_pin=reserved,meter_source_pin=dict(METER_PIN))
        # Exact source-produced originals become wires by actual sealed readback,
        # never through caller-provided substituted COMMAND/START/BODY records.
        extra=dict(operation_fields['extra_wires'])
        for kind in ('PERMISSION','COMMAND','RESERVATION','PRE_ENTRY'):
            p=e.pins[kind]
            # All four were just emitted by this very live evidence object.
            wire=e.values[kind];raw=self.loaded.writer.canonical(wire)
            need(e._readback(Path(p['path']),raw)==p,'PARENT:ORIGINAL_READBACK')
            need(p['path'] not in extra or extra[p['path']]==raw.decode('ascii'),
                 'PARENT:EXTRA_ORIGINAL_REBIND')
            extra[p['path']]=raw.decode('ascii')
        raw=bytes(e._reserved_manifest_raw)
        need(e._readback(Path(reserved['path']),raw)==reserved,'PARENT:ORIGINAL_READBACK')
        need(reserved['path'] not in extra or extra[reserved['path']]==raw.decode('ascii'),
             'PARENT:EXTRA_ORIGINAL_REBIND')
        extra[reserved['path']]=raw.decode('ascii')
        need(request_pin['path'] not in extra or extra[request_pin['path']]==
             original_native_request.decode('utf-8'),'PARENT:EXTRA_ORIGINAL_REBIND')
        extra[request_pin['path']]=original_native_request.decode('utf-8')
        plan['extra_wires']=extra
        self.plan_pin=self._publish_plan(plan)
        self.prepared_request=json.loads(original_native_request)
        self.phase='DISPATCH_READY'
        return {'tool':'exec_command','request':json.loads(original_native_request),
                'plan_pin':dict(self.plan_pin),'reserved_manifest_pin':dict(reserved),
                'execution_permission':False}

    @_parent_operation
    def receive_native_result(self,raw,origin_pin):
        need(self.phase in ('DISPATCH_READY','NATIVE_RUNNING'),'PARENT:NATIVE_ORDER')
        pin=self.evidence.native_result(raw,origin_pin)
        need(pin is not None and not self.evidence.unresolved,'PARENT:NATIVE_UNKNOWN')
        self.phase='NATIVE_TERMINAL' if self.evidence.terminal else 'NATIVE_RUNNING'
        return pin

    @_parent_operation
    def retain_poll_request(self,raw,origin_pin):
        need(self.phase=='NATIVE_RUNNING','PARENT:NATIVE_ORDER')
        pin=self.evidence.native_request('write_stdin',raw,origin_pin)
        need(pin is not None,'PARENT:NATIVE_REQUEST_UNKNOWN')
        return {'tool':'write_stdin','request':json.loads(raw),'request_pin':pin,
                'execution_permission':False}

    @_parent_operation
    def seal_terminal_body(self):
        """Seal/read the actual planned stdout only after genuine terminal exit.

        This records existing producer bytes. It cannot create, transcode or
        repair a missing/partial BODY, and native terminal authenticity remains
        the original external source-capture premise.
        """
        need(self.phase=='NATIVE_TERMINAL','PARENT:TERMINAL_BEFORE_SEAL')
        e=self.evidence;path=e.root/'METER_BODY.json';slot=None;primary=None;raw=None
        boundary=e._publication_before()
        try:
            before=path.lstat()
            need(stat.S_ISREG(before.st_mode) and stat.S_IMODE(before.st_mode)==0o600 and
                 before.st_uid==os.getuid() and before.st_nlink==1 and
                 0<before.st_size<=131072,'PARENT:BODY_ORIGINAL')
            slot=e._acquire(path,os.O_RDONLY|os.O_NONBLOCK)
            need(_source_identity(os.fstat(slot[0]))==_source_identity(before),
                 'PARENT:BODY_ORIGINAL')
            chunks=[];count=0
            while True:
                block=os.read(slot[0],min(65536,131073-count))
                if not block:break
                chunks.append(block);count+=len(block)
                need(count<=131072,'PARENT:BODY_CAP')
            raw=b''.join(chunks)
            need(count==before.st_size and _source_identity(os.fstat(slot[0]))==
                 _source_identity(before)==_source_identity(path.lstat()),
                 'PARENT:BODY_ORIGINAL')
            self.loaded.F.validate_original_record('METER_BODY',
                                                   self.loaded.F.metadata_decode(raw))
            os.fchmod(slot[0],0o444);os.fsync(slot[0])
        except BaseException as error:primary=self.remember(error)
        finally:
            if slot is not None and slot[1]=='OWNED':
                try:e._close(slot)
                except BaseException as error:
                    self.unknown=True;primary=self.remember(error)
        if primary is not None:raise primary
        # Expected sealing changes only this selected member's mode/ctime. The
        # writer's following sealed-original observation rechecks stable census.
        e._sync(e.root)
        pin=e._readback(path,raw)
        after=e._census();old=dict(boundary[1][2]);new=dict(after[2])
        need(set(old)==set(new) and all(new[p]==st for p,st in old.items()
             if p!=str(path)),'PARENT:BODY_SEAL_CENSUS')
        return {'raw':raw,'pin':pin,'execution_permission':False}

    @_parent_operation
    def reconcile_terminal(self,start_raw,start_pin,started_raw,started_pin,body_raw,body_pin):
        need(self.phase=='NATIVE_TERMINAL' and not self.receipts,'PARENT:TERMINAL_ONCE')
        e=self.evidence;F=self.loaded.F
        start=F.metadata_decode(start_raw)
        need(start['meter_source_pin']==METER_PIN,'PARENT:FIXED_METER_SOURCE')
        need(start_pin['path']==str(e.root/'METER_START.json') and
             body_pin['path']==str(e.root/'METER_BODY.json'),'PARENT:PLANNED_ORIGINALS')
        accepted=e.receive('METER_START',start_raw,start_pin)
        need(accepted['published_pin']==start_pin,'PARENT:START_UNRESOLVED')
        e.receive_started_manifest(started_raw,started_pin)
        accepted=e.receive('METER_BODY',body_raw,body_pin)
        need(accepted['published_pin']==body_pin,'PARENT:BODY_UNRESOLVED')
        chain=e.native_chain()
        observed=e.manifest('OBSERVED_AWAIT_REVIEW')
        self.receipts=True;self.phase='AWAIT_INDEPENDENT_REVIEW'
        return {'native_chain_pin':chain,'manifest_pin':observed,'execution_permission':False,
                'own_reservation_retained':True,'all_costs_settled':False}

    def _read_terminal_file(self,path,cap,expected=None,seal=False):
        need(path in (PLAN_ROOT/(self.attempt_id+'.stderr.json'),
                      PLAN_ROOT/(self.attempt_id+'.snapshot.json')),
             'PARENT:FIXED_RECEIPT_PATH')
        need(self.plan_slot[1] in ('FREE','CLOSED'),'PARENT:RECEIPT_SLOT')
        self._plan_directory();self.plan_slot[:]=[None,'PENDING'];primary=None;raw=None
        try:
            before=path.lstat()
            need(path.resolve(strict=True)==path and stat.S_ISREG(before.st_mode) and
                 before.st_uid==os.getuid() and before.st_nlink==1 and
                 stat.S_IMODE(before.st_mode)==(0o600 if seal else 0o444) and
                 0<before.st_size<=cap,'PARENT:RECEIPT_ORIGINAL')
            self.plan_slot[0]=os.open(path,os.O_RDONLY|os.O_NONBLOCK|
                                     os.O_NOFOLLOW|os.O_CLOEXEC)
            self.plan_slot[1]='OWNED'
            need(_source_identity(os.fstat(self.plan_slot[0]))==_source_identity(before),
                 'PARENT:RECEIPT_ORIGINAL')
            chunks=[];count=0
            while True:
                block=os.read(self.plan_slot[0],min(65536,cap+1-count))
                if not block:break
                chunks.append(block);count+=len(block);need(count<=cap,'PARENT:RECEIPT_CAP')
            raw=b''.join(chunks)
            need(count==before.st_size and _source_identity(os.fstat(self.plan_slot[0]))==
                 _source_identity(before)==_source_identity(path.lstat()),
                 'PARENT:RECEIPT_ORIGINAL')
            if seal:os.fchmod(self.plan_slot[0],0o444);os.fsync(self.plan_slot[0])
            sealed=os.fstat(self.plan_slot[0])
            need(stat.S_IMODE(sealed.st_mode)==0o444 and
                 sealed.st_size==len(raw) and
                 _source_identity(sealed)==_source_identity(path.lstat()),
                 'PARENT:RECEIPT_READBACK')
            pin={'path':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
                 'mode':0o444}
            if expected is not None:need(pin==expected,'PARENT:RECEIPT_PIN')
            self._plan_directory()
        except BaseException as error:
            if self.plan_slot[1]=='PENDING':self.unknown=True
            primary=self.remember(error)
        finally:
            if self.plan_slot[1]=='OWNED':
                self.plan_slot[1]='CLOSE_ENTERED'
                try:os.close(self.plan_slot[0]);self.plan_slot[1]='CLOSED'
                except BaseException as error:
                    self.plan_slot[1]='CLOSE_UNKNOWN';self.unknown=True
                    primary=self.remember(error)
        if primary is not None:raise primary
        return raw,pin

    @_parent_operation
    def retain_current_snapshot_receipt(self):
        """Read the actual producer stderr and its sealed current-subject receipt.

        Receipt DATA does not approve import. The fresh settlement owner repeats
        full current-HEAD/census/candidate verification under genuine EX.
        """
        need(self.phase=='AWAIT_INDEPENDENT_REVIEW' and self.receipts and
             self._current_snapshot_raw is None,'PARENT:CURRENT_RECEIPT_ONCE')
        detail_raw,detail_pin=self._read_terminal_file(
            PLAN_ROOT/(self.attempt_id+'.stderr.json'),65536,seal=True)
        detail=self.loaded.F.metadata_decode(detail_raw)
        need(detail.get('schema')=='fresh-fixed-manual-producer-detail-v1' and
             detail.get('attempt_id')==self.attempt_id and detail.get('action')==self.action and
             detail.get('profile')==self.profile and
             detail.get('meter_start_pin')==self.evidence.pins['METER_START'],
             'PARENT:PRODUCER_DETAIL')
        pin=detail['current_snapshot_receipt_pin']
        raw,observed=self._read_terminal_file(
            PLAN_ROOT/(self.attempt_id+'.snapshot.json'),33_554_432,expected=pin)
        def unique_pairs(items):
            result={}
            for key,value in items:
                need(key not in result,'PARENT:RECEIPT_DUPLICATE');result[key]=value
            return result
        def no_number(unused):raise ParentStop('PARENT:RECEIPT_NUMBER')
        receipt=json.loads(raw.decode('ascii'),object_pairs_hook=unique_pairs,
                           parse_float=no_number,parse_constant=no_number)
        self.loaded.F.financial_plain(receipt)
        need(type(receipt) is dict and set(receipt)=={'schema','attempt_id','action','profile',
             'meter_start_pin','financial_head_pin','snapshot'} and
             receipt['schema']=='fresh-manual-current-snapshot-receipt-v1' and
             receipt['attempt_id']==self.attempt_id and receipt['action']==self.action and
             receipt['profile']==self.profile and
             receipt['meter_start_pin']==self.evidence.pins['METER_START'] and
             receipt['snapshot']['head_pin']==receipt['financial_head_pin'] and
             _canonical(receipt)==raw,'PARENT:CURRENT_SUBJECT_RECEIPT')
        self.loaded.F.financial_evidence(receipt['snapshot'])
        self._current_snapshot_raw=_canonical(receipt['snapshot'])
        self.current_snapshot_receipt_pin=observed;self.detail_pin=detail_pin
        return {'receipt_pin':dict(observed),'financial_head_pin':receipt['financial_head_pin'],
                'execution_permission':False,'own_reservation_retained':True}

    @_parent_operation
    def receive_independent_adjudication(self,raw,origin_pin):
        need(self.phase=='AWAIT_INDEPENDENT_REVIEW' and not self.reviewed,
             'PARENT:INDEPENDENT_REVIEW_ONCE')
        # This consumes a genuinely independent original under the original
        # source/custody premise. It never writes or infers a favorable review.
        accepted=self.evidence.receive('FINANCIAL_ADJUDICATION',raw,origin_pin)
        need(accepted['published_pin'] is not None,'PARENT:REVIEW_UNRESOLVED')
        a=self.evidence.values['FINANCIAL_ADJUDICATION']
        phase='CLOSED_KNOWN' if a['financial_status']=='CLOSED_KNOWN' else 'OPEN_UNCERTAIN'
        terminal=self.evidence.manifest(phase)
        self.reviewed=True;self.phase='REVIEWED_KNOWN' if phase=='CLOSED_KNOWN' else 'OPEN_UNCERTAIN'
        return {'manifest_pin':terminal,'execution_permission':False,
                'own_reservation_retained':True,'all_costs_settled':False}

    def _collect_current_own_wires(self):
        """Read every actual sealed own member; never reconstruct native originals."""
        e=self.evidence;before=e._publication_before();wires={}
        for name in e._names(e.root,4097):
            self.loaded.writer.basename(name);path=e.root/name;slot=None;primary=None;raw=None
            try:
                st=path.lstat()
                need(stat.S_ISREG(st.st_mode) and stat.S_IMODE(st.st_mode)==0o444 and
                     st.st_uid==os.getuid() and st.st_nlink==1 and st.st_size<=131072,
                     'PARENT:OWN_ORIGINALS')
                slot=e._acquire(path,os.O_RDONLY|os.O_NONBLOCK)
                need(_source_identity(os.fstat(slot[0]))==_source_identity(st),
                     'PARENT:OWN_ORIGINALS')
                chunks=[];count=0
                while True:
                    block=os.read(slot[0],min(65536,131073-count))
                    if not block:break
                    chunks.append(block);count+=len(block)
                    need(count<=131072,'PARENT:OWN_ORIGINAL_CAP')
                raw=b''.join(chunks)
                need(count==st.st_size and _source_identity(os.fstat(slot[0]))==
                     _source_identity(st)==_source_identity(path.lstat()),
                     'PARENT:OWN_ORIGINALS')
            except BaseException as error:primary=self.remember(error)
            finally:
                if slot is not None and slot[1]=='OWNED':
                    try:e._close(slot)
                    except BaseException as error:
                        self.unknown=True;primary=self.remember(error)
            if primary is not None:raise primary
            e._readback(path,raw)  # Exact sealed-original custody, no conversion.
            wires[str(path)]=raw.decode('utf-8')
        need(e._namespace()==before[0] and e._census()==before[1],
             'PARENT:OWN_ORIGINAL_CENSUS')
        return wires

    @_parent_operation
    def settle_own(self):
        need(self.phase=='REVIEWED_KNOWN' and not self.settlement_entered and
             self._current_snapshot_raw is not None,
             'PARENT:OWN_SETTLEMENT_ONCE')
        self.settlement_entered=True  # Before fallible native factory/acquire.
        extra_wires=self._collect_current_own_wires()
        # Direct source-bound own MANUAL_ONLY importer, never target close.
        factory=self.loaded.settlement.bind_manual_settlement(
            self.loaded.C,self.loaded.F,self.loaded.candidate)
        self.contexts.append(factory)
        context=factory();self.contexts.append(context);self.settlement=context
        primary=None;result=None
        try:
            current_snapshot=json.loads(self._current_snapshot_raw)
            result=context.settle(current_snapshot,self.attempt_id,
                                  self.evidence.last_manifest,extra_wires)
            self.settlement_result=result
        except BaseException as error:primary=self.remember(error)
        finally:
            # Actual returned context remains strongly held; exactly one release.
            # A failed factory is not guessed-closed by this parent.
            try:context.release()
            except BaseException as error:
                self.unknown=True;primary=self.remember(error)
        if primary is not None:raise primary
        disposition=context.disposition()
        need(disposition['cleanup_known'] is True and
             disposition['import_readback_complete'] is True and
             disposition['reservation_retained'] is False and disposition['unknown'] is False,
             'PARENT:SETTLEMENT_READBACK_OR_CLEANUP_UNKNOWN')
        self.phase='SETTLED'
        return {'settlement':result,'owner_disposition':disposition,
                'execution_permission':False,'all_costs_settled':False}


def _open(action,profile,attempt_id):
    exact_manual_command(action,profile,attempt_id)  # Validate before startup IO.
    need(USED[0] is False,'PARENT:ONE_ORIGINAL_PARENT')
    USED[0]=True
    startup=_Startup();RETAINED.append(startup)
    loader=startup.load()
    loaded=loader.load_fixed_sources(profile)
    # The fixed loader retains authentic modules and validates its private handle.
    # No caller supplies/replaces C/F/A, writer, candidate or settlement modules.
    RETAINED.extend((loader,loaded))
    parent=_ManualParent(_TOKEN,loaded,action,profile,attempt_id)
    RETAINED.append(parent)
    return parent


def open_initializer_parent(attempt_id,profile='normal'):
    return _open('INITIALIZE',profile,attempt_id)


def open_refresh_parent(attempt_id,profile='normal'):
    return _open('REFRESH',profile,attempt_id)


def open_closer_parent(attempt_id,profile='normal'):
    return _open('CLOSE',profile,attempt_id)


if __name__=='__main__':
    raise SystemExit(78)  # No external native authority/provider/session is issued.
