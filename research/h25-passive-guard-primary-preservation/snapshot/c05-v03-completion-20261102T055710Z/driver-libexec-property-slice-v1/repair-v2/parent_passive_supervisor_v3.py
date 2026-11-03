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
HELPER = HERE / 'passive_image_candidates_v2.py'
HELPER_SHA = '56b44235f55685d61e5c8b8099d825b4ec5a53987910f506dffad309c12ffb53'
TARGET = '/usr/bin/x86_64-linux-gnu-gcc-13'
TARGET_SHA = '1b99826121ae6682a634e5efe09bd3e3df58ce58e0b28f849114ab5b89139c26'
TOOLS = {
 '/usr/bin/python3.12': (8020928, 'e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'),
 '/usr/bin/x86_64-linux-gnu-readelf': (789280, '64c58e15274bbbb5153f31078e455e9e77ee5f51489e709bba5bb788ce9df2b0'),
 '/usr/bin/x86_64-linux-gnu-objdump': (390848, '325c4205a4c658a9d1e1ebc469ae55975a2b897a3d3c1e79d9b158612d37f745')}
RAW_CAP, TOTAL_CAP, RESERVE = 786432, 1048576, 262144
MEM_CAP = 1073741824

class Stop(RuntimeError):
    pass

def need(ok, reason):
    if not ok:
        raise Stop(reason)

def digest(b):
    return hashlib.sha256(b).hexdigest()

def read_pin(path, count, expected):
    fd = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
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
        return fd, bytes(data), {k:getattr(after,k) for k in fields}
    except BaseException:
        os.close(fd)
        raise

def proc_identity(pid):
    try:
        text=Path('/proc/'+str(pid)+'/stat').read_text()
    except FileNotFoundError:
        return None
    need(len(text)<=4096,'proc stat bound')
    parts=text.rsplit(')',1)[1].split()
    return (int(parts[19]),int(parts[1]),int(parts[2]),int(parts[3]))

class Guard:
    def __init__(self, out, started, already_retained):
        self.out, self.raw, self.total = out, 0, already_retained
        self.started = started
        self.deadline = self.started + 55  # final five seconds reserved for cleanup/receipt
        self.child = None
        self.known = {}
        self.pidfds = {}
        self.steps, self.secondary = [], []
        self.peak_sampled_rss = 0
        self.launches = 0
    def write(self, name, data, raw=False):
        need('/' not in name and len(name)<100, 'output name')
        if raw:
            need(self.raw+len(data)<=RAW_CAP and self.total+len(data)<=TOTAL_CAP-RESERVE,
                 'shared raw/retention cap')
        need(self.total+len(data)<=TOTAL_CAP, 'all new output cap')
        fd = os.open(self.out/name, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC,0o600)
        try:
            view=memoryview(data)
            while view:
                n=os.write(fd,view)
                need(n>0,'short output write')
                self.total += n
                if raw: self.raw += n
                view=view[n:]
        finally: os.close(fd)
    def register(self,pid,identity):
        fd=os.pidfd_open(pid,0)
        again=proc_identity(pid)
        if again is None or again[0]!=identity:
            os.close(fd); return
        self.known[pid]=identity; self.pidfds[pid]=fd
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
        if p is None: return
        # The only process group signalled is a child started with start_new_session.
        for sig,wait in ((signal.SIGTERM,.25),(signal.SIGKILL,.75)):
            members=[]
            for pid,born in self.known.items():
                info=proc_identity(pid)
                if info is not None and info[0]==born and info[2:]==(p.pid,p.pid): members.append(pid)
            if members:
                try: os.killpg(p.pid,sig)
                except ProcessLookupError: pass
            # pidfds bind exact known processes, including a detected child that
            # changed its group; no process-name or broad parent-group kill.
            for fd in self.pidfds.values():
                try: signal.pidfd_send_signal(fd,sig)
                except ProcessLookupError: pass
            try: p.wait(timeout=wait)
            except subprocess.TimeoutExpired: pass
            # Always send the second group signal; leader exit alone is not
            # evidence that every group child has exited.
        if p.poll() is None: self.secondary.append('known leader did not reap within cleanup budget')
        poller=selectors.DefaultSelector()
        for fd in self.pidfds.values(): poller.register(fd,selectors.EVENT_READ)
        until=time.monotonic()+.5
        while poller.get_map() and time.monotonic()<until:
            for key,event in poller.select(.025): poller.unregister(key.fd)
        if poller.get_map(): self.secondary.append('live known pidfd survivors after cleanup')
        poller.close()
        for stream in (p.stdout,p.stderr):
            try: stream.close()
            except Exception as exc: self.secondary.append('pipe close: '+str(exc)[:200])
        self.child=None
        for fd in self.pidfds.values(): os.close(fd)
        self.pidfds.clear(); self.known.clear()
    def run(self, name, argv, seconds, caps, passfds=()):
        self.sample()
        need(self.launches<10,'launch count cap')
        tool=argv[0]
        began=time.monotonic()
        toolfd,toolbytes,toolstat=read_pin(tool,*TOOLS[tool])
        del toolbytes
        rec={'name':name,'argv':argv,'caps':caps,'seconds_limit':seconds,'tool_sha256':TOOLS[tool][1],
             'tool_stat':toolstat,'status':'STARTED','raw_retained_bytes':[0,0]}
        self.steps.append(rec)
        buffers=[bytearray(),bytearray()]
        failure=None
        sel=selectors.DefaultSelector()
        try:
            self.child=subprocess.Popen(argv,executable='/proc/self/fd/'+str(toolfd),
                stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                pass_fds=tuple(set(passfds+(toolfd,))),start_new_session=True,
                cwd=str(HERE),env={'LANG':'C','LC_ALL':'C','PATH':'/usr/bin:/bin',
                'DEBUGINFOD_URLS':'','PYTHONDONTWRITEBYTECODE':'1','TZ':'UTC'})
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
        except BaseException as exc:
            rec['status']='STOP'; rec['error']=type(exc).__name__+': '+str(exc)[:400]
            failure=exc
        finally:
            active=self.child
            try:
                self.cleanup()
                if self.secondary:
                    raise Stop("cleanup side failures; no subsequent step permitted")
            except BaseException as exc:
                self.secondary.append('step cleanup: '+type(exc).__name__+': '+str(exc)[:300])
                if failure is None: failure=exc
            try: sel.close(); os.close(toolfd)
            except BaseException as exc:
                self.secondary.append('step fd close: '+type(exc).__name__+': '+str(exc)[:300])
                if failure is None: failure=exc
            if active is not None: rec['returncode']=active.returncode
            rec['wall_seconds']=time.monotonic()-began
            for index,buf in enumerate(buffers):
                # Bytes beyond an individual cap are counted against terminal reserve.
                over=len(buf)>caps[index]
                try:
                    self.write(name+('.stdout' if index==0 else '.stderr'),bytes(buf),raw=not over)
                    rec['raw_retained_bytes'][index]=len(buf)
                except BaseException as exc:
                    self.secondary.append('raw retention: '+type(exc).__name__+': '+str(exc)[:300])
                    if failure is None: failure=exc
                rec.setdefault('sha256',[]).append(digest(buf))
            rec['capture_complete']=failure is None
        if failure is not None:
            rec['status']='STOP'
            rec.setdefault('error',type(failure).__name__+': '+str(failure)[:400])
            raise failure
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
    started=time.monotonic()
    active_guard=[None]
    def alarm(signum,frame):
        # Linux ITIMER_REAL deadline; no claim about an unavailable kernel/CPU.
        if time.monotonic()-started>=59.9:
            g=active_guard[0]
            if g is not None and g.child is not None:
                for fd in g.pidfds.values():
                    try: signal.pidfd_send_signal(fd,signal.SIGKILL)
                    except ProcessLookupError: pass
                for pid,born in g.known.items():
                    info=proc_identity(pid)
                    if info is not None and info[0]==born and info[2:]==(g.child.pid,g.child.pid):
                        try: os.killpg(g.child.pid,signal.SIGKILL)
                        except ProcessLookupError: pass
                        break
            try: os.write(2,b'STOP: hard60s deadline; terminal may be incomplete\n')
            finally: os._exit(124)
        signal.setitimer(signal.ITIMER_REAL,max(.001,60-(time.monotonic()-started)))
        raise Stop('wall/signal stop '+str(signum))
    signal.signal(signal.SIGALRM,alarm)
    signal.signal(signal.SIGTERM,alarm); signal.signal(signal.SIGINT,alarm)
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
    af,raw,ast=read_pin(admission_path,admission_size,args.admission_sha256); os.close(af)
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
    # Parent must supply the fixed round deadline; deadline cannot be reset by invocation.
    need(a.get('round_hard_stop_epoch')==1793664771.401519,'fixed round hardstop')
    need(time.time()+60<=a['round_hard_stop_epoch'],'insufficient fixed round time')
    lockfd=os.open(HERE/'private-one-pass.lock',os.O_CREAT|os.O_RDWR|os.O_CLOEXEC|os.O_NOFOLLOW,0o600)
    ls=os.fstat(lockfd)
    need(stat.S_ISREG(ls.st_mode) and ls.st_uid==os.getuid() and ls.st_mode&0o077==0,'private lock ownership/mode')
    fcntl.flock(lockfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
    # Exclusive permanent marker prevents retries even after a failed pass.
    marker=os.open(HERE/'ONE-PASS-STARTED',os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_CLOEXEC,0o600)
    os.write(marker,args.token.encode()); os.close(marker)
    out=HERE/('run-'+args.token); out.mkdir(mode=0o700)
    g=Guard(out,started,baseline+len(args.token)); active_guard[0]=g
    fds=[]; status='STOP'; first=None; metadata=None; hs=None
    try:
        fd,B,metadata=read_pin(TARGET,1023032,TARGET_SHA); fds.append(fd)
        hf,hb,hs=read_pin(HELPER,11809,HELPER_SHA); fds.append(hf); del hb
        need(time.monotonic()-started<=10,'setup identity capture allocation')
        helper=g.run('helper',['/usr/bin/python3.12','-B','-S','/proc/self/fd/'+str(hf)],5,(65536,16384),(hf,))
        r=json.loads(helper)
        need(r.get('status')=='PARTIAL_LOCALISATION_DATA_ONLY' and r.get('candidate_overflow') is False,
             'structured helper STOP/overflow')
        need(r.get('image_sha256')==TARGET_SHA and r.get('image_bytes')==len(B),'helper B binding')
        need(r.get('certificate_feasible') is False and r.get('full_C05') is False and r.get('full_V03') is False,'helper scope')
        refs=r['references']; need(len(refs)<=8,'candidate count')
        for c in refs:
            off=c['file_offset']; n=c['span_bytes']
            need(0<=off<=len(B) and 0<n<=10 and off+n<=len(B) and B[off:off+n].hex()==c['raw_hex'],'candidate B raw binding')
        g.run('readelf',['/usr/bin/x86_64-linux-gnu-readelf','--wide','--file-header','--program-headers',
              '--section-headers','--dynamic','--relocs','--symbols','--','/proc/self/fd/'+str(fd)],5,(196608,32768),(fd,))
        for index,c in enumerate(refs):
            # Only code candidates get windows; raw data slots remain data-only.
            if c['kind']=='RAW_LE64_LITERAL_ADDRESS': continue
            off=c['file_offset']; n=c['span_bytes']
            rows=[x for x in r['loads'] if x['flags']&1 and x['offset']<=off and off+n<=x['offset']+x['filesz']]
            need(len(rows)==1,'window executable file map')
            load=rows[0]; start=load['vaddr']+off-load['offset']
            end=start+min(256,load['offset']+load['filesz']-off)
            need(start==c['link_pc_or_slot'] and end-start>=n,'window VA binding')
            need(not any(x is not load and max(start,x['vaddr'])<min(end,x['vaddr']+x['memsz']) for x in r['loads']),
                 'window competing VA map')
            text=g.run('objdump-'+str(index),['/usr/bin/x86_64-linux-gnu-objdump','--disassemble-all','--wide',
                '--show-raw-insn','--start-address='+hex(start),'--stop-address='+hex(end),'--','/proc/self/fd/'+str(fd)],
                3,(16384,4096),(fd,))
            bind_window(text,B,load,start,end,c)
        g.sample(); status='PARTIAL_LOCALISATION_DATA_ONLY'
    except BaseException as exc:
        first=type(exc).__name__+': '+str(exc)[:1000]
    finally:
        # Alarm remains active through cleanup. The parent retains its external deadline.
        try: g.cleanup()
        except BaseException as exc: g.secondary.append('cleanup: '+type(exc).__name__+': '+str(exc)[:300])
        for fd in fds:
            try: os.close(fd)
            except OSError as exc: g.secondary.append('fd close: '+str(exc)[:200])
        try: os.close(lockfd)
        except OSError as exc: g.secondary.append('lock close: '+str(exc)[:200])
        if g.secondary:
            status='STOP'
            if first is None: first=g.secondary[0]
        receipt={'status':status,'first_error':first,'secondary_errors':g.secondary,'steps':g.steps,
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
        signal.setitimer(signal.ITIMER_REAL,0)
    return 0 if status=='PARTIAL_LOCALISATION_DATA_ONLY' else 2

if __name__=='__main__':
    try: raise SystemExit(main())
    except (Stop,OSError,ValueError) as exc:
        sys.stderr.write('STOP supervisor: '+type(exc).__name__+': '+str(exc)[:1000]+'\n')
        raise SystemExit(2)
