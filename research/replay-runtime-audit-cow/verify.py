#!/usr/bin/env python3
"""Compare the pinned T16 async audit with copy-on-write mutation controls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SOURCES = json.loads((PACKAGE / "SOURCES.json").read_text())
UPSTREAM_PACKAGE = ROOT / SOURCES["upstream_package"]
SELECTED_ARCHIVE = ROOT / SOURCES["selected_input_archive"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha(path):
    return sha_bytes(Path(path).read_bytes())


def tree_inventory(path):
    root = Path(path)
    result = {}
    for item in sorted(root.rglob("*")):
        require(not item.is_symlink(), "Symlink in pinned tree: " + str(item))
        if item.is_file():
            result[item.relative_to(root).as_posix()] = sha(item)
    return result


def tree_digest(path):
    data = json.dumps(tree_inventory(path), sort_keys=True, separators=(",", ":")).encode()
    return sha_bytes(data)


def checked_extract(archive, destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True)
    with tarfile.open(archive, "r:gz") as source:
        members = source.getmembers()
        require(all(member.isfile() and
                    (destination / member.name).resolve().is_relative_to(destination)
                    for member in members),
                "Archive has a non-file or escaping path: " + str(archive))
        source.extractall(destination, filter="data")


def replace_once(source, old, new):
    count = source.count(old)
    require(count == 1, "Pinned audit patch anchor count is " + str(count) + ": " + old[:100])
    return source.replace(old, new, 1)


def build_fast_audit(original):
    expected = SOURCES["upstream_audit_sha256"]
    require(sha_bytes(original) == expected, "Pinned upstream audit source changed")
    source = original.decode("utf-8")
    source = replace_once(
        source,
        "def reject(name,mut):\n"
        " if '--mutation-controls' not in sys.argv[4:]:return\n"
        " q=copy.deepcopy(ct);mut(q)",
        "def cow(root,path):\n"
        " if not path:return copy.copy(root)\n"
        " head,*tail=path\n"
        " q=copy.copy(root);q[head]=cow(root[head],tail);return q\n"
        "def reject(name,mut,path=None):\n"
        " if '--mutation-controls' not in sys.argv[4:]:return\n"
        " q=copy.deepcopy(ct) if path is None else cow(ct,path);mut(q)")

    controls = {
        "reject('alias two whole owners',lambda q:q['calls'][0]['owners'].__setitem__((2*V+1),q['calls'][0]['owners'][(2*V)]))": "('calls',0,'owners')",
        "reject('helper on active data family',lambda q:q['calls'][0]['owners'][(2*V)].__setitem__(0,q['calls'][0]['owners'][0][0]))": "('calls',0,'owners',2*V)",
        "reject('owner in private namespace',lambda q:q['calls'][0]['owners'][(2*V)].__setitem__(0,DATA))": "('calls',0,'owners',2*V)",
        "reject('wrong residual width',lambda q:enter(q)[1].__setitem__(3,enter(q)[1][3]-1))": "('calls',enter_call,'owners',enter_owner,1)",
        "reject('wrong spectator coordinate',lambda q:enter(q)[1][4].__setitem__(0,72))": "('calls',enter_call,'owners',enter_owner,1,4)",
        "reject('omit idle remainder',lambda q:q['idle_children'].pop())": "('idle_children',)",
        "reject('understate physical reserve',lambda q:q.__setitem__('physical',PHYSICAL-1))": "()",
        "reject(P+': wrong provider at its invocation',lambda q:at_p(q).__setitem__('provider_id','__unregistered__'))": "('calls',ci)",
        "reject(P+': stale per-call local program hash',lambda q:at_p(q).__setitem__('local_program_sha256','0'*64))": "('calls',ci)",
        "reject(P+': stale serialized provider program',lambda q:q['local_providers'][P]['local_programs']['forward'].pop())": "('local_providers',P,'local_programs','forward')",
        "reject(P+': unbound residual adapter hash',lambda q:q['local_providers'][P].__setitem__('residual_adapter_sha256','0'*64))": "('local_providers',P)",
        "reject(P+': wrong provider width registry',lambda q:q['local_providers'][P]['widths'].__setitem__(narrow,providers[P]['widths'][narrow]-1))": "('local_providers',P,'widths')",
        "reject(P+': wrong per-call residual width',lambda q:at_p(q)['owners'][2*V+narrow][1].__setitem__(3,at_p(q)['owners'][2*V+narrow][1][3]-1))": "('calls',ci,'owners',2*V+narrow,1)",
        "reject(P+': wrong sweep provider',lambda q:next(e for e in q['execution_schedule']if e['kind']=='local_cover_sweep').__setitem__('provider_id','__unregistered__'))": "('execution_schedule',si)",
        "reject(P+': entering helper width silently restored to nine',lambda q:q['local_providers'][P]['widths'].__setitem__(narrow,9))": "('local_providers',P,'widths')",
    }
    for original_call, path in controls.items():
        source = replace_once(source, original_call, original_call[:-1] + "," + path + ")")

    source = replace_once(
        source,
        " P=provider_ids[0]",
        " P=provider_ids[0];ci=next(i for i,c in enumerate(ct['calls'])if c['provider_id']==P);"
        "si=next(i for i,e in enumerate(ct['execution_schedule'])if e['kind']=='local_cover_sweep'"
        "and DISPATCH[e['stage'],e['replica']]==P)")
    source = replace_once(
        source,
        "enter=lambda q:next(o for c in q['calls']for o in c['owners'][(2*V):]if o[1][0]==4)",
        "enter=lambda q:next(o for c in q['calls']for o in c['owners'][(2*V):]if o[1][0]==4);"
        "enter_call,enter_owner=next((ci,2*V+hi)for ci,c in enumerate(ct['calls'])"
        "for hi,o in enumerate(c['owners'][(2*V):])if o[1][0]==4)")
    source = replace_once(
        source,
        "controls=[]",
        "controls=[]\ncontrol_snapshot=json.dumps(ct,sort_keys=True,separators=(',',':')).encode()")
    source = replace_once(
        source,
        "report=dict(status='PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS'",
        "assert json.dumps(ct,sort_keys=True,separators=(',',':')).encode()==control_snapshot,"
        "'mutation control leaked into source template'\n"
        "report=dict(status='PASS_INDEPENDENT_ASYNC_WHOLE_OWNER_CONTROLLER_PHASES_AND_SPECTATORS'")
    encoded = source.encode("utf-8")
    compile(encoded, "audit_allcold_fast.py", "exec")
    generated_digest = sha_bytes(encoded)
    require(generated_digest == SOURCES["generated_candidate_sha256"],
            "Generated candidate differs from its pinned patch: " + generated_digest)
    return encoded


def check_input_bindings():
    for row in SOURCES["files"]:
        if row["usage"] == "input":
            require(sha(ROOT / row["path"]) == row["sha256"],
                    "Live input changed: " + row["path"])
    record_path = ROOT / SOURCES["selected_record"]
    require(sha(record_path) == SOURCES["selected_record_sha256"], "Selected record changed")
    record = json.loads(record_path.read_text())
    require(record["review"] == SOURCES["selected_review"] and
            record["reproduce"] == SOURCES["selected_reproduce"],
            "Selected review or reproduction pointer changed")
    require(sha(SELECTED_ARCHIVE) == SOURCES["selected_input_archive_sha256"],
            "Selected replay archive changed")
    replay_path = ROOT / SOURCES["selected_replay_metadata"]
    require(sha(replay_path) == SOURCES["selected_replay_metadata_sha256"],
            "Selected replay metadata changed")
    replay = json.loads(replay_path.read_text())
    audit = next((stage for stage in replay["stages"] if stage["name"] == "audit"), None)
    require(audit is not None and audit["exit_code"] == 0 and
            audit["seconds"] == SOURCES["recorded_selected_audit_stage_seconds"],
            "Recorded selected audit stage changed")

    package_manifest_path = UPSTREAM_PACKAGE / "MANIFEST.json"
    require(sha(package_manifest_path) == SOURCES["package_manifest_sha256"],
            "T16 package manifest changed")
    inventory = json.loads(package_manifest_path.read_text())
    actual = {name: digest for name, digest in tree_inventory(UPSTREAM_PACKAGE).items()
              if name != "MANIFEST.json"}
    require(actual == inventory, "T16 package inventory differs")

    source_meta = json.loads((UPSTREAM_PACKAGE / "SOURCE.json").read_text())
    require(source_meta["head"] == SOURCES["upstream_head"] and
            source_meta["files"]["code/audit_allcold.py"] == SOURCES["upstream_audit_sha256"],
            "PR1087 audit source pointer changed")
    source_archive = UPSTREAM_PACKAGE / "upstream1087.tar.gz"
    require(sha(source_archive) == SOURCES["upstream_archive_sha256"],
            "PR1087 source archive changed")
    return record, source_meta, source_archive


def execute_variant(label, script, fixture, scratch, env, expected_outputs, expected_mutations):
    run = scratch / label
    run.mkdir(parents=True)
    base = run / "base"
    hosted = run / "hosted"
    shutil.copytree(fixture / "base", base)
    shutil.copytree(fixture / "hosted", hosted)
    report = run / "audit/ASYNC-AUDIT.json"
    log = run / "stage.log"
    start = time.monotonic()
    with log.open("wb") as stream:
        completed = subprocess.run(
            [sys.executable, "-B", str(script), str(base), str(hosted), str(report),
             "--mutation-controls"],
            cwd=ROOT, env=env, stdout=stream, stderr=subprocess.STDOUT)
    elapsed = time.monotonic() - start
    require(completed.returncode == 0,
            label + " failed; inspect " + str(log) + "\n" + log.read_text()[-4000:])
    actual = {}
    for relative, expected in expected_outputs.items():
        path = run / relative
        actual[relative] = sha(path)
        require(actual[relative] == expected, label + " output changed: " + relative)
    result = json.loads(report.read_text())
    require(result["mutation_controls_run"] is True and
            result["mutations_rejected"] == expected_mutations,
            label + " did not retain the exact mutation controls")
    return dict(variant=label, wall_seconds=elapsed, output_sha256=actual,
                rejected_mutations=result["mutations_rejected"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=3,
                        help="alternating original/candidate pairs (1 through 5; default 3)")
    args = parser.parse_args()
    require(1 <= args.pairs <= 5, "pairs must be in 1..5")
    require(sys.version_info >= (3, 12), "Use Python 3.12 or later")
    record, source_meta, source_archive = check_input_bindings()
    with tempfile.TemporaryDirectory(prefix="replay-runtime-audit-cow-") as temporary:
        scratch = Path(temporary)
        source_root = scratch / "source"
        selected_root = scratch / "selected"
        checked_extract(source_archive, source_root)
        checked_extract(SELECTED_ARCHIVE, selected_root)
        require(sha(source_root / "MANIFEST.json") == source_meta["manifest_sha256"],
                "Extracted PR1087 manifest changed")
        upstream_inventory = {name: digest for name, digest in tree_inventory(source_root).items()
                              if name != "MANIFEST.json"}
        require(upstream_inventory == source_meta["files"],
                "Extracted PR1087 files differ from the pinned inventory")

        source_dir = source_root / "code"
        original_script = source_dir / "audit_allcold.py"
        original = original_script.read_bytes()
        require(sha_bytes(original) == SOURCES["upstream_audit_sha256"],
                "Extracted audit source changed")
        fast_script = source_dir / "audit_allcold_fast.py"
        fast_bytes = build_fast_audit(original)
        fast_script.write_bytes(fast_bytes)

        # A one-byte source successor must invalidate the generated fast path.
        try:
            build_fast_audit(original + b"\n")
        except ValueError as error:
            require("source changed" in str(error), "Wrong source invalidation failure")
            source_mutation_rejected = True
        else:
            raise ValueError("Changed source unexpectedly admitted by the fast-path builder")

        for name in ("OWNERS.json.gz", "PLAN.json", "SPEC.json"):
            shutil.copyfile(UPSTREAM_PACKAGE / "data" / name, source_root / "data" / name)
        global_root = selected_root / "candidate/strict/global"
        fixture = scratch / "fixture"
        fixture.mkdir()
        for name in ("base", "hosted"):
            shutil.copytree(global_root / name, fixture / name)
        for name, expected in SOURCES["input_fixture_trees"].items():
            part = fixture / name.removeprefix("candidate/strict/global/")
            require(len(tree_inventory(part)) == expected["files"] and
                    tree_digest(part) == expected["tree_sha256"],
                    "Selected audit fixture changed: " + name)

        expected_outputs = SOURCES["expected_outputs"]
        reference_report = json.loads(
            (global_root / "audit/ASYNC-AUDIT.json").read_text())
        expected_mutations = reference_report["mutations_rejected"]
        require(len(expected_mutations) == 15, "Selected archive mutation count changed")

        env = os.environ.copy()
        for name in ("PYTHONOPTIMIZE", "WITNESS_DISCOVER", "WITNESS_RECORD", "WITNESS_SPEC"):
            env.pop(name, None)
        env.update(PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
                   PYTHONINTMAXSTRDIGITS="0",
                   MULTICOLD_SOURCE=str(source_root),
                   GAIN_PR564_SOURCE=str(source_root),
                   WITNESS_SPEC=str(source_root / "data/SPEC.json"))

        runs = []
        for pair in range(args.pairs):
            order = (("original", original_script), ("candidate", fast_script))
            if pair % 2:
                order = tuple(reversed(order))
            for offset, (label, script) in enumerate(order):
                unique = "{}-{}".format(pair, label)
                runs.append(execute_variant(unique, script, fixture,
                                            scratch / "runs" / unique, env,
                                            expected_outputs, expected_mutations))

        original_times = [r["wall_seconds"] for r in runs if r["variant"].endswith("original")]
        candidate_times = [r["wall_seconds"] for r in runs if r["variant"].endswith("candidate")]
        original_median = statistics.median(original_times)
        candidate_median = statistics.median(candidate_times)
        result = {
            "status": "PASS_REPLAY_RUNTIME_AUDIT_COW",
            "base_commit": SOURCES["base_commit"],
            "priority_revision": SOURCES["priority_revision"],
            "selected_record_sha256": sha(ROOT / SOURCES["selected_record"]),
            "upstream_audit_sha256": sha_bytes(original),
            "candidate_sha256": sha_bytes(fast_bytes),
            "selected_input_archive_sha256": sha(SELECTED_ARCHIVE),
            "pairs": args.pairs,
            "runs": runs,
            "original_median_seconds": original_median,
            "candidate_median_seconds": candidate_median,
            "speedup": original_median / candidate_median,
            "seconds_saved_per_audit_stage": original_median - candidate_median,
            "expected_output_sha256": expected_outputs,
            "rejected_mutation_count_per_run": len(expected_mutations),
            "source_mutation_rejected": source_mutation_rejected,
            "candidate_template_mutation_leak_check": "PASS",
            "scope": "One exact T16 asynchronous audit stage. No complete cold PR1094 replay, mathematical change, new kappa or selected-frontier change.",
            "environment": {
                "python": sys.version.split()[0],
                "platform": sys.platform,
                "cpu_processes": 1
            }
        }
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
