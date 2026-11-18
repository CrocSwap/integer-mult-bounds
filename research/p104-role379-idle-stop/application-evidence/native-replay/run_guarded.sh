#!/usr/bin/env bash
set -euo pipefail

out=$1
wall=$2
cpus=$3
run_id=$4
shift 4
here=$(dirname -- "${BASH_SOURCE[0]}")
test ! -e "$out" && test ! -e "$out.stdout" && test ! -e "$out.launch.json"
test "$wall" -gt 0 && test "$wall" -le 1200

rc=0
/usr/bin/time -v -o "$out.time" timeout -k 10s "${wall}s" \
    prlimit --as=2684354560 --cpu="$wall" taskset -c "$cpus" \
    python3.12 -B "$here/check_native.py" "$@" --out "$out" \
    > "$out.stdout" 2> "$out.stderr" || rc=$?

python3.12 -B - "$out" "$rc" "$run_id" "$0" "$here" "$wall" "$cpus" <<'PY'
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

out, rc, run_id, launcher, here, wall, cpus = sys.argv[1:]
out, launcher, here = Path(out), Path(launcher), Path(here)

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None

start, result = out / "START.json", out / "RESULT.json"
record = {
    "stage": "native", "run_id": run_id, "exit": int(rc), "ended_at": datetime.now(timezone.utc).isoformat(),
    "wall_seconds_limit": int(wall), "max_address_space_bytes_per_process": 2684354560,
    "affinity": [int(c) for c in cpus.split(",")],
    "adapter_sha256": digest(here / "check_native.py"),
    "physical_sha256": digest(here / "physical.py"),
    "launcher_sha256": digest(launcher),
    "start_sha256": digest(start), "native_result_sha256": digest(result),
    "stdout_sha256": digest(out.with_suffix(out.suffix + ".stdout")),
    "stderr_sha256": digest(out.with_suffix(out.suffix + ".stderr")),
    "time_sha256": digest(out.with_suffix(out.suffix + ".time")),
}
if start.is_file():
    a = json.loads(start.read_bytes())
    record["candidate_raw_sha256"] = a["candidate_raw"]
    record["started_at"] = a["started_at"]
    if a["scripts"] != {"check_native.py": record["adapter_sha256"], "physical.py": record["physical_sha256"]}:
        raise ValueError("adapter or physical code changed during run")
if record["exit"] == 0:
    r = json.loads(result.read_bytes())
    if r["status"] != "PASS_STRICT_379_NATIVE_FINITE" or r["candidate"]["raw_sha256"] != record["candidate_raw_sha256"]:
        raise ValueError("native completion receipt detached")
    record["candidate_canonical_sha256"] = r["candidate"]["canonical_sha256"]
with out.with_suffix(out.suffix + ".launch.json").open("x") as f:
    json.dump(record, f, indent=2, sort_keys=True)
    f.write("\n")
PY
exit "$rc"
