#!/usr/bin/env python3
"""One-shot E4 18-call ingredient gate, only after review and GO.

Requires an already provisioned isolated cgroup v2. Sequential retained
physical subprocesses are allowed, with no retries. An external controller
must authenticate the freeze, enforce total wall and group CPU limits, kill
the entire group on timeout, record resources and verify the group empty.
"""
import argparse, hashlib, json, os, resource, signal, sys, time, traceback
from pathlib import Path
HERE=Path(__file__).resolve().parent
CAP_MEMORY=2*1024**3
CAP_CPU=3600
CAP_WALL=4200

def need(ok,message):
    if not ok:raise ValueError(message)
def digest(data):return hashlib.sha256(data).hexdigest()
def exact_new(path,data):
    with path.open('xb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())
def encoded(obj):return (json.dumps(obj,sort_keys=True,indent=2)+'\n').encode()
def cgroup_guard():
    entries=Path('/proc/self/cgroup').read_text().splitlines()
    unified=[x.split(':',2)[2] for x in entries if x.startswith('0::')]
    need(len(unified)==1,'cgroup v2 required')
    cg=(Path('/sys/fs/cgroup')/unified[0].lstrip('/')).resolve()
    need(cg.is_relative_to(Path('/sys/fs/cgroup')),'cgroup path')
    def read(name):return (cg/name).read_text().strip()
    memory=int(read('memory.max'));swap=int(read('memory.swap.max'));pids=int(read('pids.max'))
    quota,period=read('cpu.max').split();need(quota!='max','CPU quota missing')
    need(0<memory<=CAP_MEMORY and swap==0 and 0<pids<=16 and 0<int(quota)<=int(period),'cgroup resource limits')
    need([int(x) for x in read('cgroup.procs').split()]==[os.getpid()],'cgroup must initially contain only this process')
    return {'memory_max':memory,'swap_max':swap,'pids_max':pids,'cpu_max':[int(quota),int(period)]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-once',action='store_true');parser.add_argument('--freeze-sha256',required=True)
    args=parser.parse_args();need(args.run_once,'explicit reviewed GO flag required')
    freeze_raw=(HERE/'FREEZE.json').read_bytes();need(digest(freeze_raw)==args.freeze_sha256,'reviewed freeze mismatch')
    freeze=json.loads(freeze_raw);need(freeze['schema']=='e4-native-scoped-freeze/v1','freeze schema')
    for name,expected in freeze['files'].items():
        path=HERE/name;need(path.is_file() and not path.is_symlink() and digest(path.read_bytes())==expected,'freeze file mismatch '+name)
    guard=cgroup_guard()
    need(not any((HERE/n).exists() for n in ('SCOPED-STARTED.json','SCOPED-RESULT.json','SCOPED-TERMINAL.json','PHYSICAL-SOURCE','PHYSICAL-CANDIDATE')),'one-run marker or physical output exists')
    resource.setrlimit(resource.RLIMIT_AS,(CAP_MEMORY,CAP_MEMORY))
    resource.setrlimit(resource.RLIMIT_CPU,(CAP_CPU,CAP_CPU+1))
    signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('wall limit')))
    signal.alarm(CAP_WALL)
    start=time.monotonic(); run_id=digest(os.urandom(32))
    exact_new(HERE/'SCOPED-STARTED.json',encoded({'run_id':run_id,'freeze_sha256':args.freeze_sha256,'guard':guard,'pid':os.getpid(),'wall_seconds':CAP_WALL,'cpu_seconds':CAP_CPU,'address_space_bytes':CAP_MEMORY,'status':'STARTED'}))
    terminal={'run_id':run_id,'freeze_sha256':args.freeze_sha256,'status':'FAILED','scope':'18-call ingredient native only; external controller must verify total resources and group empty'}
    try:
        import native_core
        result=native_core.run();result['run_id']=run_id;result['freeze_sha256']=args.freeze_sha256
        raw=encoded(result);exact_new(HERE/'SCOPED-RESULT.json',raw)
        terminal.update(status='SCOPED_GATE_RETURNED',result_sha256=digest(raw),result_status=result['status'])
    except BaseException as exc:
        terminal.update(error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc())
    finally:
        signal.alarm(0)
        usage=resource.getrusage(resource.RUSAGE_SELF);children=resource.getrusage(resource.RUSAGE_CHILDREN)
        terminal.update(wall_seconds=time.monotonic()-start,cpu_user_seconds=usage.ru_utime,cpu_system_seconds=usage.ru_stime,peak_rss_kib=usage.ru_maxrss,
                        waited_children_cpu_user_seconds=children.ru_utime,waited_children_cpu_system_seconds=children.ru_stime,waited_children_max_rss_kib=children.ru_maxrss)
        exact_new(HERE/'SCOPED-TERMINAL.json',encoded(terminal))
    return 0 if terminal['status']=='SCOPED_GATE_RETURNED' else 1

if __name__=='__main__':sys.exit(main())
