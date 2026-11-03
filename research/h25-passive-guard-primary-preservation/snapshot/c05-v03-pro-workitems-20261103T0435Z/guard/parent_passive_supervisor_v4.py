# Modified 2026-11-03 for Clear1nsight with substantial OpenAI Codex assistance.
# Publication-only notice/pin adapter of the independently reviewed local source.
# Retains unpaidmoon/Cursor Grok PR6339 and Clear1nsight PR6346/6347/6351 credit.
"""SOURCE ONLY until separately admitted by parent. One offline discovery pass.
Linux 7.0.0-42-generic / Python3.12 POSIX subprocess/process-group semantics.
This is sampled accounting and bounded capture, not a universal OS proof.
Never executes GCC. No imports of prior controllers or the helper in-process.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
HELPER = HERE / 'passive_image_candidates_v3.py'
HELPER_SHA = '8ba6eaaa43916cb38002c50231c6309afd0e1b5e58dc72658be10f4ab6c4626d'
HELPER_SIZE = 12983
OPERATION_ADMITTED = False
TARGET = '/usr/bin/x86_64-linux-gnu-gcc-13'
TARGET_SHA = '1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26'
TOOLS = {
 '/usr/bin/python3.12': (8020928, 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'),
 '/usr/bin/x86_64-linux-gnu-readelf': (789280, '64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0'),
 '/usr/bin/x86_64-linux-gnu-objdump': (390848, '325c4205a4c658a9d1e1ebc469ae55975a2b897a3d3c1e79d9b158612d37f745')}
RAW_CAP, TOTAL_CAP, RESERVE = 786432, 1048576, 262144
MEM_CAP = 1073741824
KNOWN_CAP = 128
RAW_ERROR_CAP = 4096

class Stop(RuntimeError):
    pass

def need(ok, reason):
    if not ok:
        raise Stop(reason)

def digest(b):
    return hashlib.sha256(b).hexdigest()

class RawErrors:
    """C10 delivered-error cells, conditional on private state/adequate unwind.

    No universal allocation, async, pre-handler or inherited-helper claim.
    The first traceback cell is never replaced by a later rethrow traceback.
    With at most128 known pidfds, one failed step and no next launch,4096
    secondary cells exceed the finite independent cleanup attempt sites.
    Capacity exhaustion itself remains quarantine/INCOMPLETE, never success.
    """
    def __init__(self):
        self.first = [None, None]
        self.errors = [None] * RAW_ERROR_CAP
        self.tracebacks = [None] * RAW_ERROR_CAP
        self.count = 0
        self.overflow = [None, None]
        self.quarantined = False
    def capture(self, error):
        if self.first[0] is None:
            self.first[0] = error
            self.first[1] = error.__traceback__
        elif error is not self.first[0]:
            index = self.count
            if index >= RAW_ERROR_CAP:
                self.quarantined = True
                if self.overflow[0] is None:
                    self.overflow[0] = error
                    self.overflow[1] = error.__traceback__
                return
            self.errors[index] = error
            self.tracebacks[index] = error.__traceback__
            self.count = index + 1
    def deliver(self):
        if self.first[0] is not None:
            raise BaseException.with_traceback(self.first[0], self.first[1])
    def ready(self):
        self.deliver()
        need(not self.quarantined, 'uncertain acquisition/close; no further operation')

def acquire(slot, errors, operation, *args, allow_primary=False, **kwargs):
    """Slot exists before native return; pending remains pending on ambiguity."""
    if allow_primary:
        need(not errors.quarantined, 'uncertainty forbids even failure-capture acquisition')
    else:
        errors.ready()
    need(slot[0] is None, 'owner slot already used')
    slot[0] = 'PENDING'
    try:
        slot[1] = operation(*args, **kwargs)
        slot[0] = 'KNOWN'
        return slot[1]
    except BaseException as error:
        errors.capture(error)
        errors.quarantined = True
        errors.deliver()

def close_slot(slot, errors, object_close=False):
    """Retire ownership before one close; no blind numeric retry after error."""
    if slot[0] == 'PENDING':
        errors.quarantined = True
        return False
    if slot[0] != 'KNOWN':
        return True
    value = slot[1]
    slot[1] = None
    slot[0] = 'RETIRED'
    try:
        if object_close:
            value.close()
        else:
            os.close(value)
        return True
    except BaseException as error:
        errors.capture(error)
        errors.quarantined = True
        return False

def read_pin(path, count, expected, errors=None, owner=None):
    if errors is None: errors = RawErrors()
    errors.ready()
    if owner is None: owner = [None, None]
    failed = False
    result = None
    try:
        fd = acquire(owner, errors, os.open, path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
        before = os.fstat(fd)
        need(stat.S_ISREG(before.st_mode) and before.st_size == count, 'pin size/type: '+str(path))
        data = bytearray()
        while len(data) <= count:
            chunk = os.read(fd, min(65536, count+1-len(data)))
            if not chunk:
                break
            data.extend(chunk)
        after = os.fstat(fd)
        fields = ('st_dev','st_ino','st_mode','st_size','st_mtime_ns','st_ctime_ns')
        need(all(getattr(before,k)==getattr(after,k) for k in fields), 'pin changed: '+str(path))
        need(len(data)==count and digest(data)==expected, 'pin mismatch: '+str(path))
        os.lseek(fd,0,0)
        result = fd, bytes(data), {k:getattr(after,k) for k in fields}
    except BaseException as error:
        errors.capture(error)
        failed = True
    if failed:
        close_slot(owner, errors)
        errors.deliver()
    return result

def proc_identity(pid):
    try:
        text=Path('/proc/'+str(pid)+'/stat').read_text()
    except FileNotFoundError:
        return None
    need(len(text)<=4096,'proc stat bound')
    parts=text.rsplit(')',1)[1].split()
    return (int(parts[19]),int(parts[1]),int(parts[2]),int(parts[3]))

class Guard:
    def __init__(self, out, started, already_retained, errors=None):
        self.errors = RawErrors() if errors is None else errors
        self.pidfd_owners = [[None, None] for unused in range(KNOWN_CAP)]
        self.pipe_owners = [[None, None], [None, None]]
        self.process_owner = [None, None]
        self.poller_owner = [None, None]
        self.write_owner = [None, None]
        self.out, self.raw, self.total = out, 0, already_retained
        self.started = started
        self.deadline = self.started + 55  # final five seconds reserved for cleanup/receipt
        self.child = None
        self.known = {}
        self.pidfds = {}
        self.steps = []
        self.peak_sampled_rss = 0
        self.launches = 0
    def write(self, name, data, raw=False, failure_capture=False):
        owner = self.write_owner
        failed = False
        try:
            if failure_capture:
                need(not self.errors.quarantined,'uncertainty forbids failure capture')
            else:
                self.errors.ready()
            need(owner[0] in (None,'RETIRED'),'write owner not reusable')
            owner[0]=None
            owner[1]=None
            need('/' not in name and len(name)<100, 'output name')
            if raw:
                need(self.raw+len(data)<=RAW_CAP and self.total+len(data)<=TOTAL_CAP-RESERVE,
                     'shared raw/retention cap')
            need(self.total+len(data)<=TOTAL_CAP, 'all new output cap')
            fd = acquire(owner, self.errors, os.open, self.out/name,
                         os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600,
                         allow_primary=failure_capture)
            view=memoryview(data)
            while view:
                n=os.write(fd,view)
                need(n>0,'short output write')
                self.total += n
                if raw: self.raw += n
                view=view[n:]
        except BaseException as error:
            self.errors.capture(error)
            failed = True
        closed = close_slot(owner, self.errors)
        if failed or not closed:
            self.errors.deliver()
    def register(self,pid,identity):
        self.errors.ready()
        owner = None
        for slot in self.pidfd_owners:
            if slot[0] is None:
                owner = slot
                break
        try:
            need(owner is not None, 'known process ownership capacity')
            fd=acquire(owner,self.errors,os.pidfd_open,pid,0)
            again=proc_identity(pid)
            need(again is not None and again[0]==identity, 'pidfd adoption identity uncertain')
            self.known[pid]=identity
            self.pidfds[pid]=fd
        except BaseException as error:
            self.errors.capture(error)
            self.errors.quarantined = True
            if owner is not None: close_slot(owner,self.errors)
            self.errors.deliver()
    def sample(self):
        need(time.monotonic()<self.deadline,'whole-operation working deadline')
        # Only this root and PIDs reached from its explicitly launched child.
        todo=list(self.known)
        unexpected=False
        while todo:
            pid=todo.pop()
            info=proc_identity(pid)
            if info is None or info[0]!=self.known[pid]:
                self.known.pop(pid,None); continue
            try:
                children=Path('/proc/'+str(pid)+'/task/'+str(pid)+'/children').read_text().split()
            except FileNotFoundError: continue
            for text in children:
                child=int(text); ci=proc_identity(child)
                if ci is not None and ci[1]==pid and child not in self.known:
                    self.register(child,ci[0])
                    if child in self.known: todo.append(child); unexpected=True
        rss=0
        domain={os.getpid():proc_identity(os.getpid())[0],**self.known}
        for pid,born in domain.items():
            info=proc_identity(pid)
            if info is None or info[0]!=born: continue
            try:
                value=int(Path('/proc/'+str(pid)+'/statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')
                again=proc_identity(pid)
                if again is not None and again[0]==born: rss+=value
            except FileNotFoundError: pass
        self.peak_sampled_rss=max(rss,self.peak_sampled_rss)
        need(not unexpected,'unexpected descendant; only direct reviewed payload children permitted')
        need(rss<=MEM_CAP,'sampled root/known-child RSS cap')
    def cleanup(self):
        p=self.child
        try:
            if p is not None:
                # Group signalling remains restricted to this launched session.
                for sig,wait in ((signal.SIGTERM,.25),(signal.SIGKILL,.75)):
                    member=False
                    for pid,born in self.known.items():
                        if self.errors.quarantined:
                            continue  # No new proc/path I/O after uncertain acquisition.
                        try:
                            info=proc_identity(pid)
                            if info is not None and info[0]==born and info[2:]==(p.pid,p.pid):
                                member=True
                        except BaseException as error:
                            self.errors.capture(error)
                            self.errors.quarantined=True
                    if member:
                        try: os.killpg(p.pid,sig)
                        except ProcessLookupError: pass
                        except BaseException as error:
                            self.errors.capture(error)
                            self.errors.quarantined=True
                    for slot in self.pidfd_owners:
                        if slot[0]=='KNOWN':
                            try: signal.pidfd_send_signal(slot[1],sig)
                            except ProcessLookupError: pass
                            except BaseException as error:
                                self.errors.capture(error)
                                self.errors.quarantined=True
                    try: p.wait(timeout=wait)
                    except subprocess.TimeoutExpired: pass
                    except BaseException as error:
                        self.errors.capture(error)
                        self.errors.quarantined=True
                try:
                    need(p.poll() is not None,'known leader did not reap within cleanup budget')
                except BaseException as error:
                    self.errors.capture(error)
                    self.errors.quarantined=True
                # No new selector acquisition after a delivered failure/uncertainty.
                if self.errors.first[0] is None and not self.errors.quarantined:
                    try:
                        poller=acquire(self.poller_owner,self.errors,selectors.DefaultSelector)
                        for slot in self.pidfd_owners:
                            if slot[0]=='KNOWN': poller.register(slot[1],selectors.EVENT_READ)
                        until=time.monotonic()+.5
                        while poller.get_map() and time.monotonic()<until:
                            for key,event in poller.select(.025): poller.unregister(key.fd)
                        need(not poller.get_map(),'live known pidfd survivors after cleanup')
                    except BaseException as error:
                        self.errors.capture(error)
                        self.errors.quarantined=True
        except BaseException as error:
            self.errors.capture(error)
            self.errors.quarantined=True
        finally:
            # Independent release is reached even after persistent observation denial.
            close_slot(self.poller_owner,self.errors,True)
            # Retire every numeric lookup before the first ambiguous close.
            self.child=None
            if self.process_owner[0]=='KNOWN':
                self.process_owner[0]='RETIRED'
                self.process_owner[1]=None
            self.pidfds.clear()
            self.known.clear()
            for slot in self.pipe_owners:
                close_slot(slot,self.errors,True)
            for slot in self.pidfd_owners:
                close_slot(slot,self.errors)
        self.errors.deliver()
    def run(self, name, argv, seconds, caps, passfds=()):
        self.errors.ready()
        # All owners and capture containers precede this step's first acquisition.
        tool_owner=[None,None]
        selector_owner=[None,None]
        buffers=[bytearray(),bytearray()]
        rec=None
        began=time.monotonic()
        try:
            self.errors.ready()
            self.sample()
            need(self.launches<10,'launch count cap')
            tool=argv[0]
            toolfd,toolbytes,toolstat=read_pin(tool,*TOOLS[tool],self.errors,tool_owner)
            del toolbytes
            rec={'name':name,'argv':argv,'caps':caps,'seconds_limit':seconds,'tool_sha256':TOOLS[tool][1],
                 'tool_stat':toolstat,'status':'STARTED','raw_retained_bytes':[0,0]}
            self.steps.append(rec)
            sel=acquire(selector_owner,self.errors,selectors.DefaultSelector)
            self.process_owner[0]=None
            self.child=acquire(self.process_owner,self.errors,subprocess.Popen,argv,
                executable='/proc/self/fd/'+str(toolfd),
                stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                pass_fds=tuple(set(passfds+(toolfd,))),start_new_session=True,
                cwd=str(HERE),env={'LANG':'C','LC_ALL':'C','PATH':'/usr/bin:/bin',
                'DEBUGINFOD_URLS':'','PYTHONDONTWRITEBYTECODE':'1','TZ':'UTC'})
            # Popen-returned object is already rooted. Internal pre-return pipe
            # and child uncertainty remains an external-teardown/C11 obligation.
            self.pipe_owners[0][1]=self.child.stdout
            self.pipe_owners[0][0]='KNOWN'
            self.pipe_owners[1][1]=self.child.stderr
            self.pipe_owners[1][0]='KNOWN'
            self.poller_owner[0]=None
            self.launches+=1
            info=proc_identity(self.child.pid)
            if info is not None: self.register(self.child.pid,info[0])
            need(self.child.pid in self.known,'launched child identity unavailable; cleanup domain uncertain')
            rec['pid']=self.child.pid; rec['process_group']=self.child.pid
            for index,stream in enumerate((self.child.stdout,self.child.stderr)):
                os.set_blocking(stream.fileno(),False); sel.register(stream,selectors.EVENT_READ,index)
            while sel.get_map() or self.child.poll() is None:
                self.sample()
                need(time.monotonic()-began<seconds,'step timeout: '+name)
                for key,event in sel.select(.025):
                    index=key.data
                    # cap+1 is retained failure evidence, never a truncated success.
                    remaining=caps[index]+1-len(buffers[index])
                    need(remaining>0,'stream cap+1: '+name)
                    block=os.read(key.fileobj.fileno(),min(8192,remaining))
                    if not block:
                        sel.unregister(key.fileobj); continue
                    buffers[index].extend(block)
                    need(len(buffers[index])<=caps[index],'stream cap+1: '+name)
                    need(self.raw+sum(map(len,buffers))<=RAW_CAP,'combined raw cap')
            rec['returncode']=self.child.wait(timeout=.1)
            rec['status']='EXITED'
            need(rec['returncode']==0,'nonzero exit: '+name)
        except BaseException as error:
            self.errors.capture(error)
        finally:
            active=self.child
            try:
                self.cleanup()
            except BaseException as error:
                self.errors.capture(error)
            # These are independent attempts, never a shared short-circuit statement.
            close_slot(selector_owner,self.errors,True)
            close_slot(tool_owner,self.errors)
            try:
                if rec is not None:
                    rec['status']='STOP' if self.errors.first[0] is not None else rec['status']
                    if active is not None: rec['returncode']=active.returncode
                    rec['wall_seconds']=time.monotonic()-began
                    rec['capture_complete']=False
                    # A failed/unqualified capture remains incomplete. Do not
                    # open raw or receipt files after any delivered uncertainty.
                    if not self.errors.quarantined:
                        for index,buf in enumerate(buffers):
                            over=len(buf)>caps[index]
                            self.write(name+('.stdout' if index==0 else '.stderr'),bytes(buf),raw=not over,
                                       failure_capture=self.errors.first[0] is not None)
                            rec['raw_retained_bytes'][index]=len(buf)
                        rec['sha256']=[digest(buf) for buf in buffers]
                        rec['capture_complete']=self.errors.first[0] is None
            except BaseException as error:
                self.errors.capture(error)
                if rec is not None:
                    rec['capture_complete']=False
        self.errors.deliver()
        need(not self.errors.quarantined,'step cleanup uncertain; no next launch')
        return bytes(buffers[0])

def bind_window(text, B, load, start, stop, candidate):
    covered=set()
    for line in text.decode('ascii','strict').splitlines():
        m=re.match(r'^\s*([0-9a-fA-F]+):\s+(.*)$',line)
        if not m: continue
        addr=int(m.group(1),16)
        raw=re.match(r'^((?:[0-9a-fA-F]{2}(?:\s+|$))+)',m.group(2))
        need(raw is not None,'decoder address row without raw bytes')
        b=bytes.fromhex(raw.group(1))
        need(start<=addr and addr+len(b)<=stop,'decoder raw outside nominated window')
        off=load['offset']+addr-load['vaddr']
        need(B[off:off+len(b)]==b,'decoder raw differs from authoritative B')
        covered.update(range(off,off+len(b)))
    off=candidate['file_offset']
    need(set(range(off,off+candidate['span_bytes']))<=covered,'candidate raw not present in decoder rows')

def main():
    """Actual local callable. No formatted replacement or renewed admission.

    C10 claims exclude signal interference, hard os._exit, inherited helpers,
    pre-return uncertainty and genuine enclosing process/namespace authority.
    """
    errors=RawErrors()
    owners=[[None,None] for unused in range(6)]
    started=time.monotonic()
    active_guard=[None]
    g=None
    status='STOP'
    metadata=hs=None
    baseline=0
    args=None
    def alarm(signum,frame):
        # Retained deadline path, explicitly OUTSIDE the no-async C10 claim.
        if time.monotonic()-started>=59.9:
            current=active_guard[0]
            if current is not None and current.child is not None:
                for descriptor in current.pidfds.values():
                    try: signal.pidfd_send_signal(descriptor,signal.SIGKILL)
                    except ProcessLookupError: pass
                for pid,born in current.known.items():
                    info=proc_identity(pid)
                    if info is not None and info[0]==born and info[2:]==(current.child.pid,current.child.pid):
                        try: os.killpg(current.child.pid,signal.SIGKILL)
                        except ProcessLookupError: pass
                        break
            try: os.write(2,b'STOP: hard60s deadline; terminal may be incomplete\n')
            finally: os._exit(124)
        signal.setitimer(signal.ITIMER_REAL,max(.001,60-(time.monotonic()-started)))
        raise Stop('wall/signal stop '+str(signum))
    try:
        # This successor is source-only. A fake namespace may replace this
        # literal for isolated controls; no genuine operation is admitted here.
        need(OPERATION_ADMITTED is True,'source-only successor; actual operation withheld')
        signal.signal(signal.SIGALRM,alarm)
        signal.signal(signal.SIGTERM,alarm)
        signal.signal(signal.SIGINT,alarm)
        signal.setitimer(signal.ITIMER_REAL,55)
        ap=argparse.ArgumentParser()
        ap.add_argument('--admission',required=True)
        ap.add_argument('--admission-sha256',required=True)
        ap.add_argument('--token',required=True)
        args=ap.parse_args()
        need(re.fullmatch(r'[A-Za-z0-9_-]{8,64}',args.token),'fresh token format')
        admission_path=Path(args.admission)
        need(admission_path.is_absolute(),'absolute admission path')
        admission_size=admission_path.stat().st_size
        need(0<admission_size<=16384,'admission bound')
        af,raw,ast=read_pin(admission_path,admission_size,args.admission_sha256,errors,owners[0])
        close_slot(owners[0],errors)
        errors.ready()
        a=json.loads(raw)
        need(a.get('scope')=='ONE_PASS_RAW_UNQUALIFIED' and a.get('token')==args.token,'scope/token')
        for key in ('independent_source_accepted','synthetic_controls_accepted','parent_serial_queue_owned',
                    'current_linux_context_accepted','reviewed_source_tool_identity_context_accepted','retention_funding_accepted'):
            need(a.get(key) is True,'missing parent admission: '+key)
        need(a.get('remaining_initial_seconds',0)>=60 and a.get('remaining_total_seconds',0)>=60,'remaining budgets')
        need(a.get('supervisor_sha256')==digest(Path(__file__).read_bytes()),'supervisor source pin')
        need(a.get('helper_sha256')==HELPER_SHA,'helper source pin')
        baseline=a.get('already_retained_new_bytes')
        need(type(baseline) is int and 0<=baseline<=262144,'existing new output reservation')
        # The original closed round epoch is retained, never renewed.
        need(a.get('round_hard_stop_epoch')==1793664771.401519,'fixed round hardstop')
        need(time.time()+60<=a['round_hard_stop_epoch'],'insufficient fixed round time')
        lockfd=acquire(owners[1],errors,os.open,HERE/'private-one-pass.lock',
                      os.O_CREAT|os.O_RDWR|os.O_CLOEXEC|os.O_NOFOLLOW,0o600)
        ls=os.fstat(lockfd)
        need(stat.S_ISREG(ls.st_mode) and ls.st_uid==os.getuid() and ls.st_mode&0o077==0,'private lock ownership/mode')
        fcntl.flock(lockfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        marker=acquire(owners[2],errors,os.open,HERE/'ONE-PASS-STARTED',
                       os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_CLOEXEC,0o600)
        need(os.write(marker,args.token.encode())==len(args.token),'short permanent marker write')
        close_slot(owners[2],errors)
        errors.ready()
        out=HERE/('run-'+args.token)
        out.mkdir(mode=0o700)
        g=Guard(out,started,baseline+len(args.token),errors)
        active_guard[0]=g
        fd,B,metadata=read_pin(TARGET,1023032,TARGET_SHA,errors,owners[3])
        hf,hb,hs=read_pin(HELPER,HELPER_SIZE,HELPER_SHA,errors,owners[4])
        del hb
        need(time.monotonic()-started<=10,'setup identity capture allocation')
        helper=g.run('helper',['/usr/bin/python3.12','-B','-S','/proc/self/fd/'+str(hf)],5,(65536,16384),(hf,))
        r=json.loads(helper)
        need(r.get('status')=='PARTIAL_LOCALISATION_DATA_ONLY' and r.get('candidate_overflow') is False,
             'structured helper STOP/overflow')
        need(r.get('image_sha256')==TARGET_SHA and r.get('image_bytes')==len(B),'helper B binding')
        need(r.get('certificate_feasible') is False and r.get('full_C05') is False and r.get('full_V03') is False,'helper scope')
        refs=r['references']
        need(len(refs)<=8,'candidate count')
        for candidate in refs:
            off=candidate['file_offset']
            n=candidate['span_bytes']
            need(0<=off<=len(B) and 0<n<=10 and off+n<=len(B) and B[off:off+n].hex()==candidate['raw_hex'],
                 'candidate B raw binding')
        g.run('readelf',['/usr/bin/x86_64-linux-gnu-readelf','--wide','--file-header','--program-headers',
              '--section-headers','--dynamic','--relocs','--symbols','--','/proc/self/fd/'+str(fd)],5,(196608,32768),(fd,))
        for index,candidate in enumerate(refs):
            if candidate['kind']=='RAW_LE64_LITERAL_ADDRESS': continue
            off=candidate['file_offset']
            n=candidate['span_bytes']
            rows=[row for row in r['loads'] if row['flags']&1 and row['offset']<=off and off+n<=row['offset']+row['filesz']]
            need(len(rows)==1,'window executable file map')
            load=rows[0]
            start=load['vaddr']+off-load['offset']
            end=start+min(256,load['offset']+load['filesz']-off)
            need(start==candidate['link_pc_or_slot'] and end-start>=n,'window VA binding')
            need(not any(row is not load and max(start,row['vaddr'])<min(end,row['vaddr']+row['memsz']) for row in r['loads']),
                 'window competing VA map')
            text=g.run('objdump-'+str(index),['/usr/bin/x86_64-linux-gnu-objdump','--disassemble-all','--wide',
                '--show-raw-insn','--start-address='+hex(start),'--stop-address='+hex(end),'--','/proc/self/fd/'+str(fd)],
                3,(16384,4096),(fd,))
            bind_window(text,B,load,start,end,candidate)
        g.sample()
        status='PARTIAL_LOCALISATION_DATA_ONLY'
    except BaseException as error:
        # Raw root precedes cleanup, formatting, receipt building and diagnostics.
        errors.capture(error)
    finally:
        if g is not None:
            try: g.cleanup()
            except BaseException as error: errors.capture(error)
        for owner in reversed(owners):
            close_slot(owner,errors)
        # This is supplementary unqualified data, never an authority record.
        # Failure/uncertainty permits no new terminal publication or formatting.
        if g is not None and errors.first[0] is None and not errors.quarantined:
            try:
                receipt={'status':status,'first_error':None,'secondary_errors':[], 'steps':g.steps,
                  'wall_seconds':time.monotonic()-g.started,'raw_bytes':g.raw,'bytes_before_terminal':g.total,
                  'already_retained_new_bytes':baseline,'marker_bytes':len(args.token),
                  'image_sha256':TARGET_SHA,'image_bytes':1023032,'image_descriptor_metadata':metadata,
                  'helper_sha256':HELPER_SHA,'helper_descriptor_metadata':hs,
                  'outer_stderr_reservation_bytes':2048,
                  'peak_sampled_root_known_child_rss':g.peak_sampled_rss,'memory_sample_not_hard_bound':True,
                  'fixed_working_limit_seconds':55,'reserved_cleanup_seconds':5,'launches':g.launches,
                  'target_executed':False,'readelf_semantics_validated':False,'instruction_boundaries_validated':False,
                  'relocation_effects_audited':False,'source_role_qualified':False,'D_applicability_qualified':False,
                  'certificate_feasible':False,'full_C05':False,'full_V03':False,'original_credit':0}
                final=json.dumps(receipt,sort_keys=True).encode()+b'\n'
                need(len(final)<=65536,'terminal receipt reserve')
                g.write('TERMINAL.json',final)
                need(g.total+2048<=TOTAL_CAP,'external failure capture reservation')
            except BaseException as error:
                errors.capture(error)
        try: signal.setitimer(signal.ITIMER_REAL,0)
        except BaseException as error: errors.capture(error)
    errors.deliver()
    need(not errors.quarantined,'outer ownership uncertain; no success')
    return 0

if __name__=='__main__':
    # Default interpreter rendering is outside the admitted raw callable path.
    # No formatted record, Stop wrapper or SystemExit replaces a delivered error.
    raise SystemExit(main())
