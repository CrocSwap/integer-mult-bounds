# SPDX-License-Identifier: Apache-2.0
"""Source and process custody for a fresh signed application."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ENTRY = ("import pathlib,runpy,sys\n"
         "path=pathlib.Path(sys.argv[1]);sys.argv=sys.argv[1:]\n"
         "sys.path.insert(0,str(path.parent));runpy.run_path(str(path),run_name='__main__')")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read(path, expected=None):
    data = path.read_bytes()
    if expected is not None:
        require(digest(data) == expected, f"Input hash {path}")
    return data


def write(path, value):
    with path.open("x") as out:
        json.dump(value, out, indent=2, sort_keys=True)
        out.write("\n")


def utc():
    return datetime.now(timezone.utc).isoformat()


def authenticate_inputs(spec):
    return {name: read(Path(ref["path"]), ref["sha256"]) for name, ref in spec["inputs"].items()}


def verify_receipt(spec, doc, result, result_sha):
    contract = spec["native_launch"]
    checks = {
        "stage": "native",
        "exit": 0,
        "run_id": contract["run_id"],
        "candidate_canonical_sha256": spec["candidate_canonical_sha256"],
        "native_result_sha256": result_sha,
        "adapter_sha256": contract["adapter_sha256"],
        "launcher_sha256": contract["launcher_sha256"],
    }
    for name, value in checks.items():
        require(doc.get(name) == value, f"Native launch receipt {name}")
    require(result["status"] == contract["status"], "Native scientific success marker")
    word = result.get("word_canonical_sha256")
    if word is None:
        word = result["candidate"]["canonical_sha256"]
    require(word == spec["candidate_canonical_sha256"], "Native scientific word")
    for name in ("adapter", "launcher"):
        require(spec["inputs"]["native_" + name]["sha256"] == checks[name + "_sha256"],
                f"External native source closure {name}")
    for name in ("physical", "start", "stdout", "stderr", "time"):
        require(doc[name + "_sha256"] == spec["inputs"]["native_" + name]["sha256"],
                f"Native external custody {name}")
    return checks


def binding_controls(spec, launch, native, pin):
    accepted = verify_receipt(spec, launch, native, pin)
    for field in accepted:
        altered = dict(launch, **{field: object()})
        try:
            verify_receipt(spec, altered, native, pin)
        except ValueError as failure:
            require(str(failure) == f"Native launch receipt {field}", "Native control rejected at wrong guard")
        else:
            raise ValueError(f"Mutated native receipt accepted: {field}")
    for field, message in (("status", "Native scientific success marker"),
                           ("word_canonical_sha256", "Native scientific word")):
        try:
            verify_receipt(spec, launch, native | {field: "stale"}, pin)
        except ValueError as failure:
            require(str(failure) == message, "Stale result rejected at wrong guard")
        else:
            raise ValueError(f"Stale native result accepted: {field}")
    return list(accepted) + ["native_status", "native_word"]


def patch(path, changes, records):
    source = path.read_text()
    updated = source
    for old, new in changes:
        require(updated.count(old) == 1, f"Exact one-occurrence source anchor {path.name}")
        updated = updated.replace(old, new, 1)
    compile(updated, str(path), "exec")
    path.write_text(updated)
    records[path.name] = {"source_sha256": digest(source.encode()),
                          "adapted_sha256": digest(path.read_bytes()), "changes": changes}


def group_members(group):
    members = []
    for entry in Path("/proc").iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            stat = (entry / "stat").read_text().rsplit(")", 1)[1].split()
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if int(stat[2]) == group:
            members.append(int(entry.name))
    return members


def launch(work, name, script, deadline, args=(), log_dir=None):
    log_dir = log_dir or work
    out_path, err_path = (log_dir / (name + suffix) for suffix in (".log", ".stderr"))
    started, tick = utc(), time.monotonic()
    deadline = min(tick + 300, deadline)
    require(tick < deadline, "Signed application wall limit")
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
    env.update({k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                                  "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS")})
    command = [sys.executable, "-I", "-B", "-c", ENTRY, str(script), *map(str, args)]
    stop = None
    with out_path.open("x") as out, err_path.open("x") as err:
        proc = subprocess.Popen(command, cwd=script.parent, env=env, stdout=out, stderr=err,
                                start_new_session=True)
        try:
            while not os.waitid(os.P_PID, proc.pid, os.WEXITED | os.WNOHANG | os.WNOWAIT):
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"{name}: process or signed wall limit")
                time.sleep(0.1)
        except BaseException as failure:
            stop = failure
        finally:
            # Keep the leader unreaped until its process group has been signaled.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            _, status, usage = os.wait4(proc.pid, 0)
            proc.returncode = os.waitstatus_to_exitcode(status)
    for _ in range(20):
        residual = group_members(proc.pid)
        if not residual:
            break
        time.sleep(0.1)
    write(work / (name + ".receipt.json"),
          {"started": started, "ended": utc(), "wall_seconds": time.monotonic() - tick,
           "exit": proc.returncode, "stdout_sha256": digest(out_path.read_bytes()),
           "stderr_sha256": digest(err_path.read_bytes()), "command": command, "pid": proc.pid,
           "group_residual": residual, "stop": str(stop) if stop else None,
           "cpu_seconds": usage.ru_utime + usage.ru_stime, "peak_rss_kib": usage.ru_maxrss,
           "major_faults": usage.ru_majflt, "swaps": usage.ru_nswap})
    if stop:
        raise stop
    require(not residual and proc.returncode == 0 and usage.ru_nswap == 0, f"Signed child {name} failed")
