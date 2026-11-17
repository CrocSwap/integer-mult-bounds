#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""One-run systemd cgroup supervisor; no service starts without explicit GO.

Based on signed-completion/controller/launch.py. Keeps the transient unit alive
through final accounting and reports missing counters as incomplete. Scientific
entry is exactly the pinned driver; no wrapper executes in the service.
"""
import argparse,hashlib,json,os,subprocess,sys,time,uuid
from pathlib import Path
from supervisor_finalizer import finalize,physical_custody
HERE=Path(__file__).resolve().parent
DRIVER_FREEZE='3328d0b08145bf8a6fa08e0a075d0dc77a24b3c7d6ae31d5eb298fe91db0be0f'
CPU_CAP=3_600_000_000;WALL_CAP=4200;MEM_CAP=2147483648

def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def raw(path):
    need(path.is_file() and not path.is_symlink(),'missing or symlink '+str(path));return path.read_bytes()
def write_exclusive(path,value):
    data=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
    with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def authenticate():
    data=raw(HERE/'FREEZE.json');need(sha(data)==DRIVER_FREEZE,'driver freeze mismatch')
    freeze=json.loads(data)
    for name,digest in freeze['files'].items():need(sha(raw(HERE/name))==digest,'driver closure '+name)
    return True

def systemctl(*args,check=True,timeout=3):
    return subprocess.run(['systemctl','--user',*args],capture_output=True,text=True,check=check,timeout=timeout)
def show(unit):
    names='ControlGroup,MemoryMax,MemorySwapMax,TasksMax,CPUAffinity,CPUQuotaPerSecUSec,CPUQuotaPeriodUSec,RuntimeMaxUSec,TimeoutStopUSec,KillMode,OOMPolicy,MainPID,ActiveState,SubState,ExecMainCode,ExecMainStatus,ExecStart,CPUUsageNSec,MemoryPeak'
    output=systemctl('show',unit,'--no-pager','--property='+names).stdout
    return dict(line.split('=',1) for line in output.splitlines() if '=' in line)
def kernel_limits(group):
    expected={'memory.max':'2147483648','memory.swap.max':'0','cpu.max':'10000 10000','cpu.max.burst':'0','memory.oom.group':'1','pids.max':'16'}
    got={k:(group/k).read_text().strip() for k in expected};need(got==expected,'kernel cgroup controls mismatch');return got
def cpu_sample(group):
    stats=dict(line.split() for line in (group/'cpu.stat').read_text().splitlines());return int(stats['usage_usec'])
def maybe_bytes(path):
    try:return raw(path)
    except (OSError,ValueError):return None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-once',action='store_true');ap.add_argument('--supervisor-freeze-sha256',required=True);args=ap.parse_args()
    need(args.run_once,'independent GO is required')
    sfraw=raw(HERE/'SUPERVISOR-FREEZE.json');need(sha(sfraw)==args.supervisor_freeze_sha256,'supervisor freeze mismatch')
    sf=json.loads(sfraw);need(sf['driver_freeze_sha256']==DRIVER_FREEZE,'driver freeze binding')
    for name,digest in sf['files'].items():need(sha(raw(HERE/name))==digest,'supervisor closure '+name)
    authenticate()
    names=('SUPERVISOR-STARTED.json','SUPERVISOR-GUARD.json','SUPERVISOR-TERMINAL.json','SUPERVISOR-STDOUT.log','SUPERVISOR-STDERR.log','SCOPED-STARTED.json','SCOPED-TERMINAL.json','SCOPED-RESULT.json','PHYSICAL-SOURCE','PHYSICAL-CANDIDATE')
    need(not any((HERE/n).exists() for n in names),'existing one-run artifact')
    unit='e4-native-'+uuid.uuid4().hex+'.service';cpu=min(os.sched_getaffinity(0));started=time.monotonic()
    props={'MemoryMax':str(MEM_CAP),'MemorySwapMax':'0','TasksMax':'16','CPUAffinity':str(cpu),'CPUQuota':'100%','CPUQuotaPeriodSec':'10ms','RuntimeMaxSec':'4200s','TimeoutStopSec':'250ms','KillMode':'control-group','OOMPolicy':'kill','CPUAccounting':'yes','MemoryAccounting':'yes'}
    driver=[sys.executable,'-B',str(HERE/'driver.py'),'--run-once','--freeze-sha256',DRIVER_FREEZE]
    cmd=['systemd-run','--user','--wait','--pipe','--remain-after-exit','--unit='+unit,'--service-type=exec']
    cmd += ['--property='+k+'='+v for k,v in props.items()];cmd+=driver
    record={'unit':unit,'driver_argv':driver,'supervisor_freeze_sha256':args.supervisor_freeze_sha256,'wall_killed':False,'cpu_killed':False,'secondary_errors':[],'exit_code':None,'verified_before_completion':False}
    write_exclusive(HERE/'SUPERVISOR-STARTED.json',record)
    group=None;proc=None;guard=None;post_limits_ok=False;final_cpu=None;final_memory=None;counter_provenance='unavailable';sample_cpu=0;sample_memory=0
    try:
        with (HERE/'SUPERVISOR-STDOUT.log').open('xb') as out,(HERE/'SUPERVISOR-STDERR.log').open('xb') as err:
            proc=subprocess.Popen(cmd,stdout=out,stderr=err)
            # The driver's own cgroup guard runs before scientific work. The
            # external readback independently binds its service and limits.
            while guard is None:
                need(time.monotonic()-started<15,'unit readback timeout')
                if proc.poll() is not None:raise RuntimeError('systemd-run exited before guard')
                try:
                    v=show(unit)
                    if v.get('ActiveState')!='active' or not v.get('ControlGroup') or not v.get('MainPID') or v['MainPID']=='0':
                        time.sleep(.05);continue
                    expected={'MemoryMax':str(MEM_CAP),'MemorySwapMax':'0','TasksMax':'16','CPUAffinity':str(cpu),'CPUQuotaPerSecUSec':'1s','CPUQuotaPeriodUSec':'10ms','RuntimeMaxUSec':'1h10min','TimeoutStopUSec':'250ms','KillMode':'control-group','OOMPolicy':'kill'}
                    need(all(v.get(k,'').replace(' ','')==x for k,x in expected.items()),'systemd property mismatch')
                    need(v['ControlGroup'].endswith('/'+unit),'unit cgroup binding')
                    # systemd renders argv in ExecStart; exact ordered string is required.
                    need(' '.join(driver) in v.get('ExecStart',''),'ExecStart driver binding')
                    group=Path('/sys/fs/cgroup')/v['ControlGroup'].lstrip('/')
                    need(group.resolve().is_relative_to(Path('/sys/fs/cgroup')),'cgroup path')
                    kernel=kernel_limits(group)
                    need(int(v['MainPID']) in [int(x) for x in (group/'cgroup.procs').read_text().split()],'driver PID outside cgroup')
                    guard={'systemd_properties':v,'kernel_limits':kernel,'verified_while_active':True,'cpu_affinity':cpu}
                except (FileNotFoundError,subprocess.CalledProcessError):time.sleep(.05)
            record['guard']=guard;record['verified_before_completion']=True
            write_exclusive(HERE/'SUPERVISOR-GUARD.json',guard)
            next_status=0.0
            while True:
                elapsed=time.monotonic()-started
                if elapsed>=WALL_CAP:
                    record['wall_killed']=True;raise TimeoutError('aggregate wall deadline')
                try:
                    sample_cpu=max(sample_cpu,cpu_sample(group));sample_memory=max(sample_memory,int((group/'memory.peak').read_text()))
                    # Ten seconds of one-CPU headroom covers bounded status,
                    # stop and fallback kill calls under normal scheduling.
                    if sample_cpu>=CPU_CAP-10_000_000:
                        record['cpu_killed']=True;raise TimeoutError('aggregate CPU deadline')
                except FileNotFoundError:pass
                if time.monotonic()<next_status:
                    time.sleep(.1);continue
                next_status=time.monotonic()+1
                v=show(unit)
                if v.get('SubState')=='exited' and v.get('ActiveState')=='active':
                    need(all(v.get(k,'').replace(' ','')==x for k,x in expected.items()),'post systemd property mismatch')
                    need(' '.join(driver) in v.get('ExecStart',''),'post ExecStart binding')
                    post_limits_ok=True
                    need(v.get('ExecMainCode') in ('exited','1'),'unexpected main exit code type')
                    record['exit_code']=int(v['ExecMainStatus']);record['post_systemd']=v;record['execution_wall_seconds']=time.monotonic()-started
                    # Cached unit totals must be available before stopping the
                    # retained service; sampled values are only lower bounds.
                    try:
                        nsec=int(v['CPUUsageNSec']);final_cpu=(nsec+999)//1000
                        final_memory=int(v['MemoryPeak'])
                        need(0<final_cpu<=CPU_CAP and 0<final_memory<=MEM_CAP,'unavailable systemd totals')
                        counter_provenance='systemd CPUUsageNSec and MemoryPeak from retained exited unit'
                    except (ValueError,KeyError):
                        # Kernel totals are final only after all descendants
                        # have exited; if the cgroup vanished, fail closed.
                        need('populated 0' in (group/'cgroup.events').read_text().splitlines(),'kernel accounting requires empty group')
                        final_cpu=cpu_sample(group);final_memory=int((group/'memory.peak').read_text())
                        counter_provenance='kernel cpu.stat and memory.peak from verified empty retained cgroup'
                    need(final_cpu>=sample_cpu and final_memory>=sample_memory,'inconsistent final counters')
                    break
                if v.get('ActiveState') in ('failed','inactive') or proc.poll() is not None:
                    record['exit_code']=int(v.get('ExecMainStatus','1'));raise RuntimeError('service did not reach successful exited state')
                time.sleep(.1)
    except BaseException as e:
        record['error']=repr(e)
    finally:
        if proc is not None:
            try:
                systemctl('stop',unit,check=True,timeout=4)
                record['systemd_run_exit_code']=proc.wait(timeout=3)
                need(record['systemd_run_exit_code']==0,'systemd-run failed')
            except BaseException as e:
                record['secondary_errors'].append('stop: '+repr(e))
                try:systemctl('kill','--kill-whom=all','--signal=KILL',unit,check=False,timeout=3)
                except BaseException as kill_error:record['secondary_errors'].append('kill: '+repr(kill_error))
        empty=False
        try:
            # A previously observed unique cgroup disappearing after service
            # stop is empty; cgroup.events checks descendants as well.
            for _ in range(40):
                empty=group is not None and (not group.exists() or 'populated 0' in (group/'cgroup.events').read_text().splitlines())
                if empty:break
                time.sleep(.05)
        except FileNotFoundError:empty=group is not None and not group.exists()
        except BaseException as e:record['secondary_errors'].append('group empty: '+repr(e))
        try:
            post_auth=authenticate() and sha(raw(HERE/'SUPERVISOR-FREEZE.json'))==args.supervisor_freeze_sha256 and all(sha(raw(HERE/n))==h for n,h in sf['files'].items())
            need(empty,'output custody requires empty cgroup')
            post_auth=post_auth and physical_custody(raw(HERE/'SCOPED-RESULT.json'),lambda name:raw(HERE/name))
            record['stdout_sha256']=sha(raw(HERE/'SUPERVISOR-STDOUT.log'));record['stderr_sha256']=sha(raw(HERE/'SUPERVISOR-STDERR.log'))
        except BaseException as e:post_auth=False;record['secondary_errors'].append('post authentication: '+repr(e))
        record.update(wall_seconds=time.monotonic()-started,sampled_cpu_usec=sample_cpu,sampled_memory_peak_bytes=sample_memory,samples_are_lower_bounds=True,aggregate_resource_provenance=counter_provenance)
        receipt=finalize(record,maybe_bytes(HERE/'SCOPED-STARTED.json'),maybe_bytes(HERE/'SCOPED-TERMINAL.json'),maybe_bytes(HERE/'SCOPED-RESULT.json'),DRIVER_FREEZE,post_auth,empty,guard is not None and post_limits_ok,final_cpu,final_memory)
        write_exclusive(HERE/'SUPERVISOR-TERMINAL.json',receipt)
    print(json.dumps(receipt,sort_keys=True),flush=True)
    return 0 if receipt['status']=='PASS_SUPERVISED_INGREDIENT_NATIVE' else 1

if __name__=='__main__':sys.exit(main())
