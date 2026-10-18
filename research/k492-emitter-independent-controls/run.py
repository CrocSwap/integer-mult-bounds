#!/usr/bin/env python3
"""Replay the complete eight-site emitter slice and semantic controls offline.

Usage from repository root:
  python3 -B research/k492-emitter-independent-controls/run.py --out /tmp/k492-emitter-review

Only the reviewed primary emitter and its witness loader run as subprocesses.
The independent checker imports no primary module. No solver, network, assembly,
invoice, credential, paid service, or original unavailable scratch fixture is used.
Prepared with substantial OpenAI Codex (GPT-6 Astra) assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import copy
import difflib
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
import zlib

from independent import Reconstruction, Rejected, digest, encoded, read, require


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE_COMMIT = "66849e1475c930fd7732b1a0067ffee7e1e95f60"
PKG = "research/complex-k492-owner-repair"
REPLAY = "research/community-k492-audit/pr626/replay/mixed-global"
PARENT = "research/structural-gain/frontier-composition/global-replay/base/split-centres/GLOBAL-TEMPLATE.json.gz"
FILES = ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "LOCAL-CHECKS.json",
         "INDEPENDENT-LOCAL-REPLAY.json", "RESIDUAL-ADAPTERS.json",
         "CLIFFORD-RECIPES.json", "CLIFFORD-REVIEW.json")

# Each exact source anchor occurs once. No primary assertion is disabled.
REVERTS = [
    ("emit.R_from_providers", "R=pc['R'];assert type(R)", "R=504;assert type(R)", "primary_rejected"),
    ("emit.roles_72R", "assert len(roles)==72*R", "assert len(roles)==72*504", "primary_rejected"),
    ("emit.widths_range", "for h in range(R)]   # HPE:", "for h in range(504)]   # HPE:", "primary_rejected"),
    ("emit.all_helpers_owned", "assert set(bycall[k])==set(range(R))", "assert set(bycall[k])==set(range(504))", "primary_rejected"),
    ("emit.physical", "physical=DATA+C+R+2", "physical=DATA+C+504+2", "independent_rejected"),
    ("emit.reserved_tableau", "'reserved_tableau':[DATA+C,DATA+C+R]", "'reserved_tableau':[DATA+C,DATA+C+504]", "independent_rejected"),
    ("emit.parent_R0", "parent['physical']-parent['live']==C+R0+2", "parent['physical']-parent['live']==C+R+2", "primary_rejected"),
    ("emit.version_label", "version='round20-R%d-asynchronous-whole-owner-v1'%R", "version='round20-R504-asynchronous-whole-owner-v1'", "pass_changed"),
]
PRIMARY_FAILURES = {
    "emit.R_from_providers": (42,"IndexError"),
    "emit.roles_72R": (48,"AssertionError"),
    "emit.widths_range": (42,"IndexError"),
    "emit.all_helpers_owned": (77,"AssertionError"),
    "emit.parent_R0": (93,"AssertionError"),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True)+"\n", encoding="utf-8")


def mappings():
    items = {
        "SPEC.json": f"{PKG}/data/SPEC.json",
        "OWNERS.json.gz": f"{PKG}/data/OWNERS.json.gz",
        "PLAN.json": f"{REPLAY}/PLAN.json",
        "base/split-centres/GLOBAL-TEMPLATE.json.gz": PARENT,
        "base/split-centres/CANONICAL-WORD.json.gz": f"{REPLAY}/base/split-centres/CANONICAL-WORD.json.gz",
        "base/work/complex-nine-native/DATA-PHASES.json": f"{REPLAY}/base/work/complex-nine-native/DATA-PHASES.json",
    }
    for pid in ("ck", "jp8"):
        for name in FILES:
            rel = f"base/providers/{pid}/{name}"
            items[rel] = f"{REPLAY}/{rel}"
    return items


def verify_pins():
    pins = read(HERE/"INPUT-PINS.json")
    expected_paths = set(mappings().values()) | {f"{PKG}/code/emit_allcold.py", f"{PKG}/code/witness.py",
                                                f"{REPLAY}/hosted/HOSTED.json", f"{PKG}/PROOF-NOTE-R.md"}
    require(pins["base_commit"] == BASE_COMMIT and set(pins["files"]) == expected_paths,
            "source.pin_inventory", "exact input set required")
    for path, item in pins["files"].items():
        require(sha(ROOT/path) == item["sha256"], "source.raw_pin", path)
        if path.endswith(".gz"):
            require(hashlib.sha256(gzip.decompress((ROOT/path).read_bytes())).hexdigest() == item["payload_sha256"],
                    "source.payload_pin", path)
    return pins


def stage(out):
    fixture = out/"fixture"
    for target, source in mappings().items():
        path = fixture/target
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/source, path)
    return fixture


def invoke(out, fixture, name, source):
    case = out/name
    scripts = case/"source"
    scripts.mkdir(parents=True)
    (scripts/"emit_allcold.py").write_text(source, encoding="utf-8")
    shutil.copyfile(ROOT/PKG/"code/witness.py", scripts/"witness.py")
    argv = [sys.executable, "-B", str(scripts/"emit_allcold.py"),
            "--base",str(fixture/"base"),"--owners",str(fixture/"OWNERS.json.gz"),
            "--plan",str(fixture/"PLAN.json"),"--out",str(case/"emitted")]
    env = dict(os.environ, WITNESS_SPEC=str(fixture/"SPEC.json"), PYTHONDONTWRITEBYTECODE="1")
    for key in ("PYTHONOPTIMIZE", "WITNESS_DISCOVER", "WITNESS_RECORD"):
        env.pop(key, None)
    started = time.monotonic()
    process = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=120)
    (case/"stdout.txt").write_text(process.stdout, encoding="utf-8")
    (case/"stderr.txt").write_text(process.stderr, encoding="utf-8")
    receipt = dict(argv=argv, cwd=str(Path.cwd()), exit_code=process.returncode,
                   seconds=round(time.monotonic()-started,6),stdout_sha256=sha(case/"stdout.txt"),
                   stderr_sha256=sha(case/"stderr.txt"), emitter_source_sha256=sha(scripts/"emit_allcold.py"),
                   witness_source_sha256=sha(scripts/"witness.py"),
                   environment_overrides={"WITNESS_SPEC":str(fixture/"SPEC.json"), "PYTHONDONTWRITEBYTECODE":"1"},
                   environment_removed=["PYTHONOPTIMIZE","WITNESS_DISCOVER","WITNESS_RECORD"])
    dump(case/"COMMAND.json", receipt)
    return case, process, receipt


def load_emission(case):
    d = case/"emitted"
    return read(d/"GLOBAL-TEMPLATE.json.gz"), read(d/"HOSTED.json"), read(d/"ACTUAL-SIGMAS.json.gz")


def semantic_controls(out, oracle, baseline):
    original, original_summary, sigmas = baseline
    controls = []

    def trial(name, path, value, obligation, claim_summary=None):
        template, summary = copy.deepcopy(original), copy.deepcopy(original_summary)
        current = template
        for token in path[:-1]:
            current = current[token]
        old = current[path[-1]]
        current[path[-1]] = value
        if claim_summary:
            summary.update(claim_summary)
        summary["template_sha256"] = digest(template)
        require(summary["template_sha256"] != original_summary["template_sha256"],
                "control.nonvacuous", name)
        record = dict(name=name,json_replacement=dict(path=path,before=old,after=value),
                      summary_claim_changes=claim_summary or {}, refreshed_template_sha256=summary["template_sha256"],
                      refreshed_summary_sha256=digest(summary),sigmas_semantic_sha256=digest(sigmas),
                      source_pins_unchanged=True,expected_obligation=obligation)
        if isinstance(old,list) and isinstance(value,list) and old[:-1] == value:
            record["json_replacement"] = dict(operation="remove",path=path+[len(old)-1],before=old[-1])
        try:
            result = oracle.verify(template,summary,sigmas)
        except Rejected as error:
            require(obligation == error.obligation,"control.expected_rejection",f"{name}: {error}")
            record.update(outcome="semantic_rejected_after_hash_refresh",obligation=error.obligation,detail=error.detail)
        else:
            require(obligation is None,"control.unexpected_acceptance",name)
            record.update(outcome="pass_changed",result=result)
        controls.append(record)

    trial("R0-in-provider-stock",["physical"],original["physical"]+12,"emit.physical",
          {"physical":original["physical"]+12})
    trial("R0-in-private-tableau",["private_namespace","reserved_tableau",1],7680,"emit.reserved_tableau")
    trial("truncated-helper-domain",["calls",0,"owners"],original["calls"][0]["owners"][:-1],"emit.all_helpers_owned")
    trial("aliased-helper-families",["calls",0,"owners",225],original["calls"][0]["owners"][224],"emit.owner_family_uniqueness")
    trial("private-family-used-as-owner",["calls",0,"owners",224,0],7168,"emit.owner_family_uniqueness")
    trial("provider-R-restored-to-504",["local_providers","ck","R"],504,"emit.provider_semantics")
    trial("provider-width-spoof",["local_providers","ck","widths",0],8,"emit.provider_semantics")
    ci, hi = next((ci,hi) for ci,c in enumerate(original["calls"]) for hi,o in enumerate(c["owners"])
                  if hi>=224 and o[1][0]==4)
    width = original["calls"][ci]["owners"][hi][1][3]
    trial("narrow-helper-width-changed",["calls",ci,"owners",hi,1,3],width-1,"emit.residual_chart")
    spare = original["calls"][ci]["owners"][hi][1][4]
    trial("spectator-axis-changed",["calls",ci,"owners",hi,1,4,0],72 if spare[0]!=72 else 71,"emit.residual_chart")
    trial("one-literal-role-omitted",["hosting","pooled_slots"],original["hosting"]["pooled_slots"][:-1],"emit.role_metadata",
          {"hosted_residuals":72*oracle.R-1})
    trial("remainder-omitted",["idle_children"],original["idle_children"][:-1],"emit.idle_remainders")
    trial("source-event-order-changed",["execution_schedule",0,"source_event"],1,"emit.controller_expansion")
    trial("provider-artifact-link-changed",["local_providers","ck","residual_adapter_sha256"],"0"*64,"emit.provider_artifact_binding")
    trial("retained-recipe-changed",["recipe",2,"coefficient"],-1,"emit.retained_parent_field")
    trial("retained-call-window-changed",["calls",0,"window"],[],"emit.retained_call_fields")
    trial("async-parent-schedule-erased",["async_schedule","source_schedule"],[],"emit.async_source_binding")
    trial("cosmetic-label",["version"],"independent-emitter-cosmetic-control",None)

    for name, changed_sources, obligation in (
            ("source-inventory-erased",{},"links.input_inventory"),
            ("source-artifact-hash-changed",dict(original_summary["source_artifacts"],
                **{"providers/ck/RESIDUAL-ADAPTERS.json":"0"*64}),"links.inputs")):
        summary = dict(original_summary,source_artifacts=changed_sources)
        summary["template_sha256"] = digest(original)
        try:
            oracle.verify(original,summary,sigmas)
        except Rejected as error:
            require(error.obligation == obligation,"control.expected_rejection",f"{name}: {error}")
            controls.append(dict(name=name,outcome="semantic_rejected_after_hash_refresh",obligation=error.obligation,
                                 detail=error.detail,summary_source_artifacts=changed_sources,
                                 refreshed_template_sha256=summary["template_sha256"],refreshed_summary_sha256=digest(summary),
                                 source_pins_unchanged=True))
        else:
            raise Rejected("control.unexpected_acceptance",name)

    # The same uncompressed JSON is accepted after actual gzip header/stream changes.
    raw = encoded(original)
    compressed = gzip.compress(raw,compresslevel=1,mtime=123456789)
    restored = json.loads(gzip.decompress(compressed))
    result = oracle.verify(restored,original_summary,sigmas)
    baseline_gzip = out/"baseline/emitted/GLOBAL-TEMPLATE.json.gz"
    require(hashlib.sha256(compressed).hexdigest() != sha(baseline_gzip),"control.recompression_nonvacuous","container differs")
    controls.append(dict(name="actual-gzip-recompression",outcome="pass_identical_semantics",
                         original_raw_sha256=sha(baseline_gzip),changed_raw_sha256=hashlib.sha256(compressed).hexdigest(),
                         unchanged_payload_sha256=hashlib.sha256(raw).hexdigest(),result=result))
    dump(out/"SEMANTIC-CONTROLS.json",controls)
    return controls


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",type=Path,required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    require(not out.exists(),"output.fresh_directory",str(out))
    pins = verify_pins()
    out.mkdir(parents=True)
    dump(out/"INPUT-PINS.json",pins)
    dump(out/"ENVIRONMENT.json",dict(python=sys.version,executable=sys.executable,platform=platform.platform(),
                                    zlib_compile=zlib.ZLIB_VERSION,zlib_runtime=zlib.ZLIB_RUNTIME_VERSION,
                                    base_commit=BASE_COMMIT,checker_sha256=sha(HERE/"independent.py"),
                                    harness_sha256=sha(HERE/"run.py"),assertions_enabled=__debug__))
    fixture = stage(out)
    source = (ROOT/PKG/"code/emit_allcold.py").read_text()
    case, process, command = invoke(out,fixture,"baseline",source)
    require(process.returncode == 0,"baseline.primary",process.stderr)
    oracle = Reconstruction(fixture)
    baseline = load_emission(case)
    result = oracle.verify(*baseline)
    retained = read(ROOT/REPLAY/"hosted/HOSTED.json")
    require(baseline[1] == retained,"baseline.retained_HOSTED","fresh output must match retained receipt exactly")
    dump(out/"BASELINE.json",result)
    print("PASS baseline: R=492, R0=504, 35,424 roles, 7,670 physical rows",flush=True)
    reverts = []
    for name, before, after, expected in REVERTS:
        require(source.count(before) == 1,"revert.unique_anchor",name)
        changed = source.replace(before,after)
        case, process, command = invoke(out,fixture,name,changed)
        patch = "".join(difflib.unified_diff(source.splitlines(True),changed.splitlines(True),
                                            fromfile="original/emit_allcold.py",tofile=name+"/emit_allcold.py"))
        (case/"source.patch").write_text(patch,encoding="utf-8")
        record = dict(site=name,expected=expected,command=command,patch_sha256=sha(case/"source.patch"))
        if process.returncode:
            require(expected == "primary_rejected","revert.unexpected_process_failure",name+": "+process.stderr)
            # Require an actual assertion or indexing failure at the mutated emitter,
            # not a missing input/import/environment accident.
            frames = re.findall(r'File "[^"\n]*emit_allcold\.py", line (\d+)',process.stderr)
            last_error = process.stderr.rstrip().splitlines()[-1]
            expected_line, expected_exception = PRIMARY_FAILURES[name]
            require(frames and int(frames[-1]) == expected_line and last_error.split(":")[0] == expected_exception,
                    "revert.failure_kind",name)
            record.update(outcome="primary_rejected",last_error=last_error,failing_emitter_line=expected_line,
                          failing_source_statement=changed.splitlines()[expected_line-1])
        else:
            emission = load_emission(case)
            try:
                check = oracle.verify(*emission)
            except Rejected as error:
                require(expected == "independent_rejected" and error.obligation == name,
                        "revert.expected_semantic_failure",f"{name}: {error}")
                record.update(outcome="independent_rejected",obligation=error.obligation,detail=error.detail,
                              refreshed_template_sha256=emission[1]["template_sha256"])
            else:
                require(expected == "pass_changed","revert.unexpected_acceptance",name)
                template = copy.deepcopy(emission[0]);template["version"] = baseline[0]["version"]
                summary = copy.deepcopy(emission[1]);summary["template_sha256"] = baseline[1]["template_sha256"]
                require(template == baseline[0] and summary == baseline[1] and emission[2] == baseline[2],
                        "revert.cosmetic_only","only version and its directly derived template hash may differ")
                record.update(outcome="pass_changed",changed_fields=["GLOBAL-TEMPLATE.version","HOSTED.template_sha256"],result=check)
        reverts.append(record)
        print(f"PASS {name}: {record['outcome']}",flush=True)
    dump(out/"SOURCE-REVERTS.json",reverts)
    semantic = semantic_controls(out,oracle,baseline)
    final = dict(status="PASS_COMPLETE_EIGHT_EMITTER_SITE_SLICE",base_commit=BASE_COMMIT,
                 baseline=result,source_reverts=dict(total=len(reverts),primary_rejected=5,independent_rejected=2,pass_changed=1),
                 semantic_controls=dict(total=len(semantic),
                     rejected=sum(c["outcome"] == "semantic_rejected_after_hash_refresh" for c in semantic),
                     positive=sum(c["outcome"].startswith("pass_") for c in semantic)),
                 scope="R492 emitter structural contract only, with retained native inputs and hash-matched parent",
                 unresolved=["Unavailable original scratch suite and original R504 fixture are not reproduced",
                             "Other 24 source sites are not claimed by this contribution",
                             "No local scalar/Clifford/phase reconstruction, invoice, assembly, or all-size theorem proof"])
    dump(out/"RESULT.json",final)
    print(final["status"],flush=True)


if __name__ == "__main__":
    main()
