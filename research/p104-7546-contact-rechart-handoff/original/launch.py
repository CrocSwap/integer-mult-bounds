#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Operational controller only: no word, graph, invoice or source algebra.

All scientific code, INCLUDING run_once.py, executes inside the verified
1GiB service cgroup. The controller records actual kernel settings and
partial evidence; it is outside the scientific job just as the MCP client is.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parent


def write(path,data):
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--control",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--freeze-sha",required=True)
    parser.add_argument("--guard-only",action="store_true")
    args=parser.parse_args();control=args.control.resolve();control.mkdir()
    unit="kappa-contact-"+uuid.uuid4().hex[:12]+".service"
    cpu=min(os.sched_getaffinity(0));group=None;proc=None;record={"unit":unit,"source_released":False}
    properties={"MemoryMax":"1073741824","MemorySwapMax":"0","TasksMax":"16","CPUAffinity":str(cpu),
        "CPUQuota":"100%","CPUQuotaPeriodSec":"10ms","RuntimeMaxSec":"100s","TimeoutStopSec":"250ms",
        "KillMode":"control-group","OOMPolicy":"kill","CPUAccounting":"yes","MemoryAccounting":"yes"}
    command=["systemd-run","--user","--wait","--pipe","--collect","--unit="+unit,"--service-type=exec"]
    command += ["--property="+k+"="+v for k,v in properties.items()]
    command += [sys.executable,"-I","-B",str(ROOT/"controlled_entry.py"),"--control",str(control),
                "--out",str(args.out.resolve()),"--freeze-sha",args.freeze_sha,"--unit",unit]
    started=time.monotonic()
    try:
        with (control/"SERVICE-STDOUT.txt").open("x") as out,(control/"SERVICE-STDERR.txt").open("x") as err:
            proc=subprocess.Popen(command,stdout=out,stderr=err)
            deadline=time.monotonic()+5
            while not (control/"READY.json").exists() and proc.poll() is None and time.monotonic()<deadline:
                time.sleep(.01)
            ready=json.loads((control/"READY.json").read_text())
            names=["ControlGroup","MemoryMax","MemorySwapMax","TasksMax","CPUAffinity","CPUQuotaPerSecUSec",
                   "CPUQuotaPeriodUSec","RuntimeMaxUSec","TimeoutStopUSec","KillMode","OOMPolicy","MainPID","ActiveState"]
            shown=subprocess.run(["systemctl","--user","show",unit,"--no-pager","--property="+",".join(names)],
                                 capture_output=True,text=True,check=True,timeout=2)
            actual=dict(line.split("=",1) for line in shown.stdout.splitlines() if "=" in line)
            expected={"MemoryMax":"1073741824","MemorySwapMax":"0","TasksMax":"16","CPUAffinity":str(cpu),
                "CPUQuotaPerSecUSec":"1s","CPUQuotaPeriodUSec":"10ms","RuntimeMaxUSec":"1min40s",
                "TimeoutStopUSec":"250ms","KillMode":"control-group","OOMPolicy":"kill","ActiveState":"active"}
            record["properties"]=actual
            if any(actual.get(k,"").replace(" ","") != v for k,v in expected.items()):
                raise ValueError("actual unit properties differ")
            if ready["cgroup"] != actual["ControlGroup"] or ready["pid"] != int(actual["MainPID"]) or ready["affinity"] != [cpu]:
                raise ValueError("service/cgroup/affinity binding")
            if not ready["cgroup"].endswith("/"+unit):
                raise ValueError("unique unit containment")
            group=Path("/sys/fs/cgroup")/ready["cgroup"].lstrip("/")
            expected_files={"memory.max":"1073741824","memory.swap.max":"0","cpu.max":"10000 10000",
                            "cpu.max.burst":"0","memory.oom.group":"1","pids.max":"16"}
            observed={name:(group/name).read_text().strip() for name in expected_files}
            if observed != expected_files:
                raise ValueError("kernel aggregate controls differ")
            if ready["pid"] not in map(int,(group/"cgroup.procs").read_text().split()):
                raise ValueError("entry outside verified cgroup")
            record.update(kernel_controls=observed,verified_before_release=True,guard_only=args.guard_only)
            write(control/"GUARD-VERIFIED.json",record)
            with (control/"ALLOW.pending").open("x") as allow:
                json.dump({"unit":unit,"freeze_sha256":args.freeze_sha,"guard_only":args.guard_only},allow)
            (control/"ALLOW.pending").rename(control/"ALLOW.json")
            record["source_released"]=not args.guard_only
            maximum_cpu,maximum_memory=0,0
            while proc.poll() is None:
                try:
                    stat=dict(line.split() for line in (group/"cpu.stat").read_text().splitlines())
                    maximum_cpu=max(maximum_cpu,int(stat["usage_usec"]))
                    maximum_memory=max(maximum_memory,int((group/"memory.peak").read_text()))
                    if maximum_cpu>105_000_000 or time.monotonic()-started>112:
                        raise TimeoutError("conservative controller stop")
                except FileNotFoundError:
                    pass
                time.sleep(.02)
            record.update(returncode=proc.returncode,sampled_cpu_usec=maximum_cpu,sampled_memory_peak_bytes=maximum_memory,
                          samples_are_lower_observations_not_final_accounting=True)
    except BaseException as error:
        record["error"]=repr(error)
    finally:
        if proc is not None and (proc.poll() is None or (group is not None and group.exists())):
            try:
                subprocess.run(["systemctl","--user","stop",unit],capture_output=True,timeout=2)
                proc.wait(timeout=1)
            except BaseException as error:
                record["cleanup_error"]=repr(error)
                subprocess.run(["systemctl","--user","kill","--kill-whom=all","--signal=KILL",unit],capture_output=True,timeout=2)
        try:
            record["group_empty"]=group is None or not group.exists() or not (group/"cgroup.procs").read_text().strip()
        except FileNotFoundError:
            record["group_empty"]=True
        record["elapsed_controller_wall_seconds"]=time.monotonic()-started
        record["nominee_admissible_for_next_gate"]=False
        if not args.guard_only:
            p=args.out.resolve()/"RESOURCE.json"
            receipt=json.loads(p.read_text()) if p.exists() else None
            record["job_receipt_available"]=receipt is not None
            record["nominee_admissible_for_next_gate"]=(record.get("returncode")==0 and not record.get("error") and
                not record.get("cleanup_error") and record["group_empty"] and receipt is not None and
                receipt.get("nominee_available_for_assessment",False))
            if receipt is None:
                write(control/"INCOMPLETE.json",{"coverage":"unknown","nominee_admissible":False})
        write(control/"RESULT.json",record)
        print(json.dumps(record,sort_keys=True),flush=True)


if __name__=="__main__":main()
