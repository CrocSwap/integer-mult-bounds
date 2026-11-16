#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Operational controller only: no word, graph, invoice or source algebra.

All scientific code, INCLUDING run_once.py, executes inside the verified
2GiB service cgroup. The controller records actual kernel settings and
partial evidence; it is outside the scientific job just as the MCP client is.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import signal
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parent


def write(path,data):
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")


def record_job_receipt(out, control, record):
    """Record receipt failures as secondary and leave any primary error intact."""
    receipt = None
    try:
        receipt = json.loads((out / "RESOURCE.json").read_text())
        if (not isinstance(receipt, dict) or
            type(receipt.get("differential_case_completed")) is not bool or
            type(receipt.get("source_executed")) is not bool or
            not isinstance(receipt.get("stages"), list)):
            raise ValueError("invalid job receipt shape")
    except BaseException as error:
        receipt = None
        record["receipt_error"] = repr(error)
        record["secondary_cleanup_errors"].append({"step":"job_receipt", "error":repr(error)})
    record["job_receipt_available"] = receipt is not None
    record["differential_case_completed"] = (
        record.get("returncode") == 0 and not record.get("error") and
        not record.get("cleanup_error") and record.get("group_empty") is True and
        record.get("audit_capture_valid") is True and receipt is not None and
        receipt["source_executed"] is True and receipt["differential_case_completed"] is True)
    if receipt is None:
        try:
            write(control / "INCOMPLETE.json", {"coverage":"unknown", "nominee_admissible":False})
        except BaseException as error:
            record["secondary_cleanup_errors"].append({"step":"incomplete_receipt", "error":repr(error)})


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--control",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--freeze-sha",required=True)
    parser.add_argument("--guard-only",action="store_true")
    args=parser.parse_args();control=args.control.resolve()
    if control != ROOT/"control" or args.out.resolve() != ROOT/"run":
        raise ValueError("continuation requires its fixed control and run paths")
    # A hard process deadline bounds even stalled control-plane operations.
    # An abrupt deadline may leave no final receipt: that is never acceptance.
    signal.signal(signal.SIGALRM, lambda *_: os._exit(124))
    signal.setitimer(signal.ITIMER_REAL,1210)
    started=time.monotonic()
    if args.out.resolve().exists():
        raise FileExistsError("refusing existing output")
    control.mkdir()
    unit="kappa-contact-"+uuid.uuid4().hex[:12]+".service"
    cpu=min(os.sched_getaffinity(0));group=None;proc=None;record={"unit":unit,"source_released":False,
        "hard_deadline_seconds":1210,"hard_deadline_behavior":"abrupt_exit_without_cleanup_or_final_receipt",
        "hard_deadline_cleanup_status":"unverified_until_final_group_empty_check",
        "missing_final_result_means":"incomplete_cleanup_and_descendant_empty_unknown"}
    write(control/"CONTROLLER-METADATA.json",{
        "hard_deadline_seconds":1210,
        "hard_deadline_behavior":"abrupt_exit_without_cleanup_or_final_receipt",
        "missing_final_result_means":"incomplete_cleanup_and_descendant_empty_unknown",
        "empty_group_verification":"only_in_final_RESULT_json",
        "status_scope":"differential_case_operational_completion_only"})
    properties={"MemoryMax":"2147483648","MemorySwapMax":"0","TasksMax":"16","CPUAffinity":str(cpu),
        "CPUQuota":"100%","CPUQuotaPeriodSec":"10ms","RuntimeMaxSec":"1200s","TimeoutStopSec":"250ms",
        "KillMode":"control-group","OOMPolicy":"kill","CPUAccounting":"yes","MemoryAccounting":"yes"}
    command=["systemd-run","--user","--wait","--pipe","--collect","--unit="+unit,"--service-type=exec"]
    command += ["--property="+k+"="+v for k,v in properties.items()]
    command += [sys.executable,"-I","-B",str(ROOT/"controlled_entry.py"),"--control",str(control),
                "--out",str(args.out.resolve()),"--freeze-sha",args.freeze_sha,"--unit",unit]
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
            expected={"MemoryMax":"2147483648","MemorySwapMax":"0","TasksMax":"16","CPUAffinity":str(cpu),
                "CPUQuotaPerSecUSec":"1s","CPUQuotaPeriodUSec":"10ms","RuntimeMaxUSec":"20min",
                "TimeoutStopUSec":"250ms","KillMode":"control-group","OOMPolicy":"kill","ActiveState":"active"}
            record["properties"]=actual
            if any(actual.get(k,"").replace(" ","") != v for k,v in expected.items()):
                raise ValueError("actual unit properties differ")
            if ready["cgroup"] != actual["ControlGroup"] or ready["pid"] != int(actual["MainPID"]) or ready["affinity"] != [cpu]:
                raise ValueError("service/cgroup/affinity binding")
            if not ready["cgroup"].endswith("/"+unit):
                raise ValueError("unique unit containment")
            group=Path("/sys/fs/cgroup")/ready["cgroup"].lstrip("/")
            expected_files={"memory.max":"2147483648","memory.swap.max":"0","cpu.max":"10000 10000",
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
                if time.monotonic()-started>1205:
                    raise TimeoutError("conservative controller wall stop")
                try:
                    stat=dict(line.split() for line in (group/"cpu.stat").read_text().splitlines())
                    maximum_cpu=max(maximum_cpu,int(stat["usage_usec"]))
                    maximum_memory=max(maximum_memory,int((group/"memory.peak").read_text()))
                    if maximum_cpu>1199_000_000:
                        raise TimeoutError("conservative controller stop")
                except FileNotFoundError:
                    pass
                time.sleep(.02)
            record.update(returncode=proc.returncode,sampled_cpu_usec=maximum_cpu,sampled_memory_peak_bytes=maximum_memory,
                          samples_are_lower_observations_not_final_accounting=True)
    except BaseException as error:
        record["error"]=repr(error)
    finally:
        record["secondary_cleanup_errors"]=[]
        if proc is not None and (proc.poll() is None or (group is not None and group.exists())):
            try:
                subprocess.run(["systemctl","--user","stop",unit],capture_output=True,timeout=2)
                proc.wait(timeout=1)
            except BaseException as error:
                record["cleanup_error"]=repr(error)
                record["secondary_cleanup_errors"].append({"step":"stop", "error":repr(error)})
                try:
                    subprocess.run(["systemctl","--user","kill","--kill-whom=all","--signal=KILL",unit],capture_output=True,timeout=2)
                except BaseException as kill_error:
                    record["secondary_cleanup_errors"].append({"step":"kill", "error":repr(kill_error)})
        try:
            record["group_empty"]=group is not None and (not group.exists() or "populated 0" in (group/"cgroup.events").read_text().splitlines())
        except FileNotFoundError:
            record["group_empty"]=group is not None and not group.exists()
        except BaseException as error:
            record["group_empty"]=False
            record["secondary_cleanup_errors"].append({"step":"group_empty", "error":repr(error)})
        record["hard_deadline_cleanup_status"]=("group_empty_verified" if record["group_empty"] else "unverified")
        record["elapsed_controller_wall_seconds"]=time.monotonic()-started
        # The service and all descendants must be gone before touching its audit output.
        # Keep scientific/controller failure as primary and record custody errors separately.
        if not args.guard_only and record.get("source_released"):
            audit_started=time.monotonic()
            try:
                if not record["group_empty"]:
                    raise RuntimeError("audit capture requires verified empty cgroup")
                marker=args.out.resolve()/"case/PREDECESSOR-AUDIT-CAPTURE.json"
                if not marker.is_file():
                    raise RuntimeError("predecessor audit capture marker missing")
                freeze_path=ROOT/"FREEZE.json"
                if hashlib.sha256(freeze_path.read_bytes()).hexdigest()!=args.freeze_sha:
                    raise ValueError("audit controller freeze receipt changed")
                frozen=json.loads(freeze_path.read_bytes())["files"]
                helper=ROOT/"audit_custody.py"
                digest=hashlib.sha256(helper.read_bytes()).hexdigest()
                if helper.is_symlink() or not any(Path(row["path"]).resolve()==helper and row["sha256"]==digest for row in frozen):
                    raise ValueError("audit controller helper not frozen")
                import importlib.util
                spec=importlib.util.spec_from_file_location("audit_custody",helper)
                audit_custody=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit_custody)
                prior=json.loads(marker.read_text())
                archived=args.out.resolve()/"case/PREDECESSOR-AUDIT.jsonl"
                expected="ca23807a4b1d9675daf67903608a6d874e37b94c70109a45fa73732ee8123841"
                if prior.get("status")!="ARCHIVED" or prior.get("sha256")!=expected or audit_custody.sha(archived)!=expected:
                    raise ValueError("predecessor audit archive binding")
                package=ROOT.parent/"inputs/pr7624/research/p104-w2-primal-dual-bypass"
                record["audit_capture"]=audit_custody.archive(package,control/"SIGNED-AUDIT.jsonl",allow_absent=True)
                record["audit_capture_valid"]=True
            except BaseException as error:
                record["audit_capture_valid"]=False
                record["audit_cleanup_error"]=repr(error)
                record["secondary_cleanup_errors"].append({"step":"audit_capture", "error":repr(error)})
            finally:
                record["audit_cleanup_wall_seconds"]=time.monotonic()-audit_started
        if not args.guard_only:
            record_job_receipt(args.out.resolve(),control,record)
        write(control/"RESULT.json",record)
        print(json.dumps(record,sort_keys=True),flush=True)
        if record.get("error") or record.get("cleanup_error") or not record.get("group_empty") or (not args.guard_only and not record.get("differential_case_completed")):
            raise SystemExit(1)


if __name__=="__main__":main()
