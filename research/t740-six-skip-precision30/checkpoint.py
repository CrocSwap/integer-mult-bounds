#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Resume nomination after the diagnosed coarse-selector failure.

Only completed nomination geometry is reused. The final original strict
supplier/outer release runs in full. Exact authenticated producer statements
generate all receipts; no success receipt is hand-written here.
Substantial OpenAI Codex assistance; retained producers keep their credit.
"""

import argparse
import ast
import contextlib
import os
import shutil
import sys
import textwrap
import time

import verify as v


def execute(nodes, namespace, filename):
    tree = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(tree, str(filename), "exec"), namespace)  # authenticated source only


def called(node, name):
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Call)
        and isinstance(node.value.func, ast.Name)
        and node.value.func.id == name
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-work", type=v.Path, required=True)
    parser.add_argument("--work", type=v.Path, required=True)
    a = parser.parse_args()
    baseline, work = a.baseline_work.resolve(), a.work.resolve()
    candidate = work / "candidate"
    v.need(os.name == "posix" and not sys.flags.optimize, "POSIX, assertions required")
    v.need(not work.is_relative_to(v.P), "external checkpoint required")
    v.authenticate()
    parent = v.ROOT / "research/rank7-t740-carrier-skips"
    sys.path.insert(0, str(parent))
    original = v.load(parent / "reproduce.py", "checkpoint_complete_baseline")
    r = v.read(baseline / "RESULT.json")
    stages = v.read(baseline / "STAGES.json")
    for stage in stages:
        v.need(
            stage["exit_code"] == 0
            and v.sha(baseline / (stage["stage"] + ".log")) == stage["log_sha256"],
            "complete baseline stage/log",
        )
    v.need(
        original.check_release(baseline, baseline / "pr3042", r["fill_sha256"], stages)
        == r,
        "mandatory full baseline, not discovery",
    )
    adapter = work / "admit_precision30.py"
    old_body = adapter.read_text()
    edits = v.read(v.P / "PRECISION-EDITS.json")
    v.need(
        len(edits) == 6 and old_body.count(edits[-1]["old"]) == 1,
        "only diagnosed selector correction",
    )
    new_body = old_body.replace(edits[-1]["old"], edits[-1]["new"])
    reference_hash, candidate_hash = v.expected_adapter_hashes()
    v.need(
        v.hashlib.sha256(new_body.encode()).hexdigest() == candidate_hash,
        "exact authenticated corrected producer",
    )
    saved = work / "failed-coarse-selector"
    v.need(not saved.exists(), "preserve each failed attempt once")
    saved.mkdir()
    for source in (
        adapter,
        work / "DERIVATION.json",
        work / "complete-admission.log",
        candidate / "RESULT.json",
        candidate / "STAGES.json",
        candidate / "RUNTIME-PATCHES.json",
    ):
        shutil.copyfile(source, saved / (source.parent.name + "-" + source.name))
    prepared = v.read(candidate / "RESULT.json")
    v.need(
        prepared["status"] == "PREPARED_REPLICA_SAME_WORD_DERIVATIVE_NOT_ADMITTED",
        "prepared failed nomination, never an admitted receipt",
    )
    old_stages = v.read(candidate / "STAGES.json")
    v.need(
        [s["name"] for s in old_stages]
        == ["owners", "parent-lift", "rebind", "discovery"],
        "exact failed checkpoint stage inventory",
    )
    for stage in old_stages[:3]:
        v.need(
            stage["exit_code"] == 0
            and v.sha(candidate / (stage["name"] + ".log")) == stage["log_sha256"]
            and v.sha(v.Path(stage["command"][2])) == stage["script_sha256"],
            "actual completed preparation",
        )
    adapter.write_bytes(new_body.encode())
    (work / "DERIVATION.json").write_bytes(
        (
            v.json.dumps(
                dict(
                    reference_sha256=reference_hash,
                    candidate_sha256=candidate_hash,
                    replacements=edits,
                ),
                indent=2,
                sort_keys=True,
            )
            + "\n"
        ).encode()
    )
    module = v.load(adapter, "authenticated_corrected_admission")
    body = next(
        n
        for n in ast.parse(new_body).body
        if isinstance(n, ast.FunctionDef) and n.name == "main"
    ).body
    command = v.expected_command("complete-admission", baseline, sys.executable)
    command[command.index("--work") + 1] = str(candidate)
    sys.argv = [str(adapter), *command[3:]]
    ns = module.__dict__
    prefix = []
    for node in body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and isinstance(node.value.func.value, ast.Name)
            and node.value.func.value.id == "work"
            and node.value.func.attr == "mkdir"
        ):
            break
        if (
            called(node, "need")
            and len(node.value.args) > 1
            and isinstance(node.value.args[1], ast.Constant)
            and node.value.args[1].value == "fresh external work required"
        ):
            continue  # replaced by the authenticated prepared-checkpoint checks above
        prefix.append(node)
    execute(prefix, ns, adapter)
    v.need(
        ns["external_hashes"] == prepared["external_input_sha256"],
        "unchanged literal inputs",
    )
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONINTMAXSTRDIGITS="0",
        OPENBLAS_NUM_THREADS="1",
        OMP_NUM_THREADS="1",
    )
    for key in (
        "PYTHONOPTIMIZE",
        "PYTHONPATH",
        "WITNESS_SPEC",
        "WITNESS_RECORD",
        "WITNESS_DISCOVER",
    ):
        env.pop(key, None)
    runtime = candidate / "layout/packing74"
    ns.update(
        package=candidate / "package",
        runtime=runtime,
        data=runtime / "candidate",
        result=prepared,
        patches=prepared["patches"],
        stages=old_stages[:3],
        env=env,
    )
    execute(
        [
            next(n for n in body if isinstance(n, ast.FunctionDef) and n.name == name)
            for name in ("patch", "run")
        ],
        ns,
        adapter,
    )
    insertion = ast.parse(textwrap.dedent(edits[-1]["new"])).body[0]
    execute([insertion], ns, adapter)
    ns["write"](candidate / "RUNTIME-PATCHES.json", ns["patches"])
    shutil.copyfile(ns["package"] / "code/assemble.py", runtime / "code/assemble.py")
    replay_path = runtime / "replay.py"
    expected_replay = (ns["source"] / "replay.py").read_text()
    for node in body:
        if (
            called(node, "patch")
            and isinstance(node.value.args[0], ast.Constant)
            and node.value.args[0].value == "replay.py"
        ):
            pairs = eval(
                compile(ast.Expression(node.value.args[1]), str(adapter), "eval"), ns
            )
            for before, after in pairs:
                v.need(
                    expected_replay.count(before) == 1, "exact replay producer preimage"
                )
                expected_replay = expected_replay.replace(before, after)
    v.need(
        replay_path.read_bytes() == expected_replay.encode(),
        "source-authenticated replay continuation",
    )
    replay = ast.parse(replay_path.read_bytes()).body
    rn = dict(__file__=str(replay_path), __name__="authenticated_checkpoint_discovery")
    initial = []
    for node in replay:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "ap" for t in node.targets
        ):
            break
        initial.append(node)
    execute(initial, rn, replay_path)
    discovery = candidate / "discovery"
    ds = v.read(discovery / "STAGES.json")
    v.need(
        [s["name"] for s in ds] == ["bind", "emit", "audit", "invoice", "assembly"],
        "exact failed discovery",
    )
    for stage in ds[:4]:
        v.need(
            stage["exit_code"] == 0
            and v.sha(discovery / (stage["name"] + ".log")) == stage["log_sha256"],
            "actual successful nomination geometry; not a skipped strict release",
        )
    for filename in ("STAGES.json", "assembly.log", "WITNESS-RECORD.jsonl"):
        shutil.copyfile(discovery / filename, saved / ("discovery-" + filename))
    up = rn["ROOT"] / "research/complex-k492-owner-repair/vendor/multicold"
    denv = dict(
        env,
        PYTHONUTF8="1",
        MULTICOLD_SOURCE=str(up),
        GAIN_PR564_SOURCE=str(up),
        WITNESS_SPEC=str(discovery / "runtime/data/SPEC.json"),
        WITNESS_DISCOVER="1",
        WITNESS_RECORD=str(discovery / "WITNESS-RECORD.jsonl"),
    )
    rn.update(
        a=argparse.Namespace(discover=True),
        data=ns["data"],
        work=discovery,
        local=ns["natives"]["base"] / "local",
        code=runtime / "code",
        upstream=up,
        spec=discovery / "runtime/data/SPEC.json",
        env=denv,
        stages=ds[:4],
        g=discovery / "global",
    )
    execute(
        [next(n for n in replay if isinstance(n, ast.FunctionDef) and n.name == "run")],
        rn,
        replay_path,
    )
    start = next(
        i
        for i, n in enumerate(replay)
        if called(n, "run")
        and isinstance(n.value.args[0], ast.Constant)
        and n.value.args[0].value == "assembly"
    )
    started = time.monotonic()
    with (
        (candidate / "discovery-checkpoint.log").open("w") as transcript,
        contextlib.redirect_stdout(transcript),
    ):
        execute(replay[start:], rn, replay_path)
    resume_record = dict(
        name="discovery-checkpoint",
        exit_code=0,
        seconds=time.monotonic() - started,
        script_sha256=v.sha(v.Path(__file__)),
        command=[sys.executable, "-B", str(v.Path(__file__))],
        scope="Nomination geometry prefix reused; corrected assembly/freeze/independent executed. Final strict release is fresh.",
    )
    resume_record["log_sha256"] = v.sha(candidate / "discovery-checkpoint.log")
    ns["stages"].append(resume_record)
    ns["result"]["checkpoint_scope"] = resume_record["scope"]
    tail = next(
        i
        for i, n in enumerate(body)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "supplier" for t in n.targets)
    )
    execute(
        body[tail:], ns, adapter
    )  # includes the original COMPLETE strict supplier and outer release
    outer_path = v.P / "reproduce.py"
    outer = ast.parse(outer_path.read_bytes()).body
    finish = next(
        i
        for i, n in enumerate(outer)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "a" for t in n.targets)
        and isinstance(n.value, ast.Call)
        and isinstance(n.value.func, ast.Name)
        and n.value.func.id == "read"
    )
    ns.update(WORK=work, BASELINE=baseline, nom=v.calculate(), r=r, save=ns["write"])
    execute(outer[finish:], ns, outer_path)


if __name__ == "__main__":
    main()
