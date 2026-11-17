#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Authenticate the single completed E4 signed invocation from saved records."""

import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
DRIVER = HERE.parent / "e4-signed-controller/recovered-executable"
CONTROL = DRIVER / "runs/attempt-01"
FREEZE = "f740b666b75457d78e3679a2ab3a8406c2f3186c220ed7ed9cbfb1a8b54c3068"
UNIT = "<REDACTED-UNIT-IDENTIFIER>"
INVOCATION = "668d934ed2d440c89a4f038823b0cabf"
SIGNED = "f6c24629d235470b86c46703ad59fb22"
NATIVE = "c2e263c03ed18855afd4125d42981d71a27151b81d00ed05b133966629394cf4"
ORIGINAL_ERROR = {"stage": "supervisor", "error": "ValueError('final cgroup absent')"}
PINS = {
    "READY.json": "e994c8151e9da935c625d36ddb0daa05679a3c2831782e00eec51017ba941f55",
    "GUARD.json": "cd09f013c32464713d34f25bf17683356a9fdec7a83cef3ac97398fd752f4c85",
    "ALLOW.json": "d26aa86fee7be4cb2b9bad2409e2443ed08d5e80096c8b8a5970370bd6d2edf1",
    "ALLOW-ACK.json": "6408b493bb8cd11bbdc43ef67b9f63bb0280aa7e278328a3dd6abb1839c58266",
    "SIGNED-LAUNCH-INTENT.json": "5584d89759c7814a1da9dd68db72c0854ad7f3b73f9980f1c492803b0e189537",
    "SIGNED-STARTED.json": "606cb4850984bcdbc14b9ab2ed2bce8e2a9d2777fdb73bd96b16ae88a9711ca6",
    "SUPERVISOR-STARTED.json": "c92c2b8b9f02a341b1382e9069ea2910986bc4a7d8e913a16e6f5f60af290651",
    "SERVICE.stderr": "cd4c9b52a34969a82924c42a5869e06db1d5c7f9ea0712fdf35c4eff815a2392",
    "SIGNED-EXECUTION.json": "fd5c10e102f712d853ff5eff118b7f594398ec97b886b6f408341b93f772b641",
    "SIGNED-AUDIT.jsonl": "c487e86b053cd7b168bee107ec1b7722b7f87f3e1830c80a9e878aa77f40d62c",
    "SUPERVISOR-TERMINAL.json": "720b20a1b1f33e322b01736cefd4e9dc01d07ce7e53cad56ee5c357def3ffbd7",
}
JOURNAL_HASH = "897a42bee0afa89b8ea45af12f5ac8393702a74c4c57d1216ed1431c244ca718"
HOST_HASH = "5ec1ca0045497270715f1fab371cf63758e36ea0bf4b25343f293b730408dd83"


def journal_accounting(common, start, guard, child, terminal):
    journal = HERE / "ORIGINAL-UNIT-JOURNAL.jsonl"
    host = HERE / "HOST-RETIREMENT.json"
    common.need(common.sha(journal) == JOURNAL_HASH and common.sha(host) == HOST_HASH,
                "preserved exact journal and retired-host bytes")
    records = [json.loads(line) for line in journal.read_bytes().splitlines()]
    query = common.read(HERE / "JOURNAL-QUERY.json")
    ids = ["7d4958e842da4a758f6c1cdc7b36dcc5", "39f53479d3a045ac8e11786248231fbf",
           "9d1aaa27d60140bd96365438aad20286", "ae8f7b866b0347b9af31fe1c80b127c0"]
    common.need([row["MESSAGE_ID"] for row in records] == ids and len({r["__CURSOR"] for r in records}) == 4
                and query["unit"] == UNIT and query["raw_journal_sha256"] == JOURNAL_HASH
                and query["window_readback_equal_after_json_key_sort"] is True
                and query["all_retained_unit_events"] == 4 and query["structured_resource_events"] == 1
                and query["all_retained_invocations"] == [INVOCATION], "exact retained journal query")
    observation = common.read(host)
    common.need(all(row["USER_UNIT"] == UNIT and row["USER_INVOCATION_ID"] == INVOCATION
                    and row["_UID"] == row["_SYSTEMD_OWNER_UID"] == "1000"
                    and row["_PID"] == query["all_retained_manager_pids"][0]
                    and row["_EXE"] == "/usr/lib/systemd/systemd" and row["_COMM"] == "systemd"
                    and row["_TRANSPORT"] == "journal" and row["_SYSTEMD_UNIT"] == "user@1000.service"
                    and row["_BOOT_ID"] == observation["boot_id"] == query["all_retained_boots"][0]
                    for row in records), "same boot, trusted systemd manager, unit and invocation")
    opening, running, stopping, final = records
    command = start["systemd"]["ExecStart"].split("argv[]=", 1)[1].split(" ;", 1)[0]
    common.need(all(command in row["MESSAGE"] for row in records[:3])
                and opening["JOB_TYPE"] == running["JOB_TYPE"] == "start"
                and running["JOB_RESULT"] == stopping["JOB_RESULT"] == "done"
                and stopping["JOB_TYPE"] == "stop" and final["CODE_FUNC"] == "unit_log_resources",
                "journal command and lifecycle")
    stderr = (CONTROL / "SERVICE.stderr").read_text()
    common.need(f"Running as unit: {UNIT}; invocation ID: {INVOCATION}" in stderr
                and "Finished with result: success" in stderr
                and "Main processes terminated with: code=exited/status=0" in stderr,
                "independent systemd-run unit, invocation and exit")
    times = [1000 * int(row["__MONOTONIC_TIMESTAMP"]) for row in records]
    common.need(times[0] < times[1] <= start["ready"]["ready_monotonic_ns"]
                < guard["started_monotonic_ns"] < times[2] <= times[3] < observation["checked_monotonic_ns"],
                "journal windows enclose actual signed child")
    wall = (times[2] - times[0]) / 1_000_000_000
    child_end = (times[2] - guard["started_monotonic_ns"]) / 1_000_000_000
    cpu, memory, swap = (int(final[k]) for k in ("CPU_USAGE_NSEC", "MEMORY_PEAK", "MEMORY_SWAP_PEAK"))
    common.need(0 < child["wall_seconds"] < child_end < wall <= 1200
                and child["stage_cap_seconds"] == 900 and child["wall_seconds"] < 900
                and 1000 * terminal["sampled_cpu_usec"] <= cpu <= 1_200_000_000_000
                and terminal["sampled_memory_peak_bytes"] <= memory <= 2**31 and swap == 0
                and child["waited_children_cpu_seconds"] <= cpu / 1_000_000_000,
                "exact final accounting and original bounds")
    props = dict(line.split("=", 1) for line in observation["show_stdout"].splitlines())
    common.need(observation["unit"] == props["Id"] == UNIT and observation["show_exit_code"] == 0
                and observation["show_stderr"] == "" and props["MainPID"] == "0"
                and (props["LoadState"], props["ActiveState"], props["SubState"]) == ("not-found", "inactive", "dead")
                and observation["cgroup_path"] == "/sys/fs/cgroup" + start["ready"]["cgroup"]
                and observation["cgroup_lstat_errno"] == 2, "retired exact service and missing cgroup")
    return wall, (cpu + 999) // 1000, memory, swap


def main():
    sys.path.insert(0, str(DRIVER))
    import common

    f, cfg = common.authenticate(DRIVER / "EXECUTION-FREEZE.json", FREEZE)
    common.need((cfg["run_id"], cfg["native_run_id"]) == (SIGNED, NATIVE), "exact distinct original runs")
    for name, expected in PINS.items():
        common.need(common.sha(CONTROL / name) == expected, "exact original evidence: " + name)
    t = common.read(CONTROL / "SUPERVISOR-TERMINAL.json")
    common.need(t["status"] == "INCOMPLETE_OR_FAILED" and t["error"] == ORIGINAL_ERROR and not t["secondary_errors"]
                and t["exit_code"] is None and t["readback_limits_pass"] is False
                and t["aggregate_cpu_usec"] is None and t["peak_memory_bytes"] is None
                and t["systemd_run_exit_code"] == 0 and t["post_authentication_pass"] is True
                and t["process_group_empty"] is True and t["audit_capture_status"] == "ARCHIVED"
                and t["cpu_killed"] is False and t["wall_killed"] is False
                and all(t[k] is True for k in ("allow_published", "allow_acknowledged", "verified_before_release", "source_released"))
                and t["unit"] == UNIT and not (CONTROL / "SIGNED-STAGE-RECEIPT.json").exists(),
                "original failed finalization remains unchanged")
    ready, guard, allow, ack, intent, marker, child = (common.read(CONTROL / name) for name in (
        "READY.json", "GUARD.json", "ALLOW.json", "ALLOW-ACK.json", "SIGNED-LAUNCH-INTENT.json",
        "SIGNED-STARTED.json", "SIGNED-EXECUTION.json"))
    ns = ack["accepted_monotonic_ns"]
    common.need(ready == guard["ready"] and guard["systemd"] == t["live_properties"]
                and guard["kernel"] == t["kernel_limits"] and guard["verified_before_release"] is True
                and ack["unit"] == UNIT, "exact pre-release guard and acknowledgement")
    common.check_ready(ready, guard["systemd"], guard["kernel"], UNIT, 0, f, cfg, FREEZE, ns)
    common.check_grant(allow, UNIT, FREEZE, f, cfg, ns >= ready["allow_deadline_ns"])
    argv_sha = hashlib.sha256(json.dumps(child["argv"], separators=(",", ":")).encode()).hexdigest()
    intent_sha = PINS["SIGNED-LAUNCH-INTENT.json"]
    common.check_start(intent, marker, ack, f, cfg, FREEZE, intent_sha, argv_sha)
    common.check_child(child, f, cfg, FREEZE)
    common.need(child["child_pid"] == marker["child_pid"] == t["signed_child_pid"]
                and child["launch_intent_sha256"] == t["launch_intent_sha256"] == intent_sha,
                "same executed child and immutable intent")
    wall, cpu, memory, swap = journal_accounting(common, guard, marker, child, t)

    out = common.WORK / "producer54/validation_signed"
    rows = {}
    for path in out.rglob("*"):
        common.need(common.contract.no_link(path, out), "no signed output links")
        if path.is_file():
            rows[path.relative_to(out).as_posix()] = common.sha(path)
    science = common.read(out / "RESULT.json")
    common.need(len(rows) == 52 and common.contract.REQUIRED <= rows.keys()
                and rows["RESULT.json"] == child["result_sha256"] == "6fe1f74fb37f6882108702429ec9783e79af7e5737d60530d50b7ad02e29f534"
                and science["status"] == "PASS_E4_COMPLETE_SIGNED_APPLICATION", "complete held signed outputs")
    candidate = science["candidate_check_sha256"]
    source = science["source_resource"]["check_sha256"]
    common.need(set(candidate) == set(common.contract.NAMES) | {"ODD-8X9-APPLICATION-CHECKS.json"}
                and set(source) == set(common.contract.NAMES)
                and all(rows["candidate-checks/" + name] == value for name, value in candidate.items())
                and all(rows["source-checks/" + name] == value for name, value in source.items()),
                "both retained check inventories")
    audit = common.contract.audit_custody.validate_log(CONTROL / "SIGNED-AUDIT.jsonl")
    common.need(audit["sha256"] == PINS["SIGNED-AUDIT.jsonl"] and audit["rows"] == 3 and audit["bytes"] == 849,
                "existing original shim audit")
    report = {
        "schema": "e4-signed-stage-recovery/v1", "status": "PASS_RECOVERED_SIGNED_STAGE",
        "run_id": SIGNED, "native_run_id": NATIVE, "candidate_canonical_sha256": common.contract.CAND,
        "signed_result_sha256": rows["RESULT.json"], "signed_binding_sha256": f["binding_sha256"],
        "producer_sha256": common.contract.PRODUCER, "native_result_sha256": cfg["native_sha256"],
        "native_supervisor_sha256": cfg["native_supervisor_sha256"],
        "certificate_result_sha256": cfg["certificates_sha256"],
        "certificate_terminal_sha256": cfg["certificate_receipt_sha256"], "common_u_sha256": cfg["common_u_sha256"],
        "signed_terminal_sha256": PINS["SUPERVISOR-TERMINAL.json"],
        "signed_execution_sha256": PINS["SIGNED-EXECUTION.json"], "signed_journal_sha256": JOURNAL_HASH,
        "signed_retirement_sha256": HOST_HASH, "signed_audit_sha256": audit["sha256"],
        "journal_query_sha256": common.sha(HERE / "JOURNAL-QUERY.json"), "journal_invocation_id": INVOCATION,
        "original_error": ORIGINAL_ERROR, "original_readback_limits_pass": False, "exit_code": child["exit_code"],
        "initial_limits_pass": True, "post_authentication_pass": True, "process_group_empty": True,
        "audit_capture_valid": True, "execution_wall_seconds": wall, "aggregate_cpu_usec": cpu,
        "peak_memory_bytes": memory, "peak_swap_bytes": swap, "raw_hashes": rows,
        "control_sha256": PINS, "execution_freeze_sha256": FREEZE, "recovery_script_sha256": common.sha(Path(__file__)),
        "scope": "Final realized limits from the original unit's structured journal and exit from the signed child. Original final unit setting readback unavailable.",
    }
    common.exclusive(HERE / "RECOVERED-SIGNED-RECEIPT.json", report)
    print(json.dumps({k: report[k] for k in ("status", "run_id", "aggregate_cpu_usec", "peak_memory_bytes", "execution_wall_seconds")}))


if __name__ == "__main__":
    main()
