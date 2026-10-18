"""Explicit integration replay; not part of the short registered gate check.

Reuses Aaron Wang's byte-pinned PR2301 post-emit runner and final predicates.
Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binding as b
import verify


def predecessor_runner():
    verify.predecessor()
    spec = importlib.util.spec_from_file_location("credited_pr2301", HERE / "vendor/PR2301-verify.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # The exact vendored module's original relative paths point to its own old
    # package location. Only these environment paths are rebound; no function
    # source or stage arguments are edited.
    module.ROOT = b.ROOT
    module.STAGE = b.ROOT / b.STAGE
    module.MC = b.ROOT / "research/complex-k492-owner-repair/vendor/multicold"
    module.ARCHIVE = b.ROOT / verify.ARCHIVE
    module.RUNPORT = module.MC / "code/run_portable.py"
    module.RETAINED_INVOICE = module.MC / "vendor/pr558/vendor/pr552/complex-global/vendor531/evidence/audit/PREFIX-AND-INVOICE.json"
    b.need(b.sha(module.RUNPORT.read_bytes()) == module.RUNPORT_SHA, "post-emit wrapper pin")
    return module


def execute(work):
    b.need(not sys.flags.optimize, "full integration harness requires assertions for credited predecessor")
    source_pins = b.pins()
    work = work.resolve()
    b.need(not work.exists() and not work.is_relative_to(b.ROOT), "fresh external full-check work")
    work.mkdir(parents=True)
    local = work / "local1042"
    local.mkdir()
    with tarfile.open(b.ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz") as archive:
        seen = set()
        for member in archive.getmembers():
            if not member.name.startswith("slots/local/"):
                continue
            rel = Path(member.name[len("slots/local/"):])
            b.need(member.isfile() and not rel.is_absolute() and ".." not in rel.parts
                   and str(rel) not in seen, "safe distinct local member")
            seen.add(str(rel))
            path = local / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(archive.extractfile(member).read())
    b.need(len(seen) == 10, "complete archived local input")
    positive = work / "positive"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONOPTIMIZE="2")
    # Deliberately hostile inherited optimization setting. The new wrapper runs
    # under -O and must still launch the original stages with assertions active.
    command = [sys.executable, "-I", "-O", "-B", str(HERE / "run_bound.py"),
               "--local", str(local), "--work", str(positive)]
    with (work / "positive.log").open("x") as log:
        result = subprocess.run(command, cwd=b.ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    b.need(result.returncode == 0, "successor positive failed; see positive.log")
    complete = b.decode((positive / "BOUND-REPLAY.json").read_bytes())
    b.need(complete["status"] == "PASS_SELECTED_OWNER_BOUND_REPLAY" and complete["strict_replay_executed"], "bound successor receipt")
    b.need(len(complete["strict_stages"]) == 11 and complete["owner_binding"]["roles"] == 69120, "positive coverage")
    credited = predecessor_runner()
    source = positive / "legacy/source"
    pristine = positive / "legacy/strict"
    b.need(b.sha((source / "verify_t16.py").read_bytes()) == credited.VERIFY_T16_SHA, "unchanged strict driver")
    b.need(b.sha((source / "code/audit_allcold.py").read_bytes()) == credited.AUDIT_SHA, "unchanged audit")
    owners = (b.ROOT / b.OWNER).read_bytes()
    mutants = []
    for name in ("PR2301_time_swap", "PR2301_digest"):
        case = work / name
        case.mkdir()
        strict = case / "strict"
        shutil.copytree(pristine, strict)
        hosted = strict / "global/hosted"
        template = credited.load_template(hosted)
        if name.endswith("time_swap"):
            pair = credited.time_swap(template)
            b.need(pair[:2] == (0, 480), "exact predecessor witness")
        else:
            template["hosting"]["owner_map_sha256"] = "0" * 64
        credited.reemit(hosted, template)
        ledger, fresh = credited.run_stages(case, source, strict, name)
        b.need(len(ledger) == 6 and all(x["exit_code"] == 0 for x in ledger), "old post-emit chain did not accept mutant")
        old_final = credited.final_binding(fresh, strict, source, pristine)
        b.need(old_final["passed"] == old_final["total"] == 20, "old final predicates did not accept mutant")
        try:
            b.check((hosted / "GLOBAL-TEMPLATE.json.gz").read_bytes(), owners, source_pins[str(b.OWNER)])
        except ValueError as exc:
            message = str(exc)
            b.need(("pooled slots differ" if name.endswith("time_swap") else "digest link") in message,
                   "mutant rejected for unrelated reason")
        else:
            raise ValueError("new gate accepted old counterexample")
        mutants.append({"fixture": name, "old_stages": ledger, "old_final": old_final,
                        "new_gate_rejected": True, "rejection": message})
        print("PASS_OLD_ACCEPT_NEW_REJECT", name, flush=True)
    b.need(b.pins() == source_pins, "sources changed during full replay")
    receipt = {"schema": "selected-owner-bound-integration/1", "strict_replay_executed": True,
               "python": sys.version, "optimized_wrapper": True, "inherited_pythonoptimize": "2",
               "source_pins": source_pins, "positive": complete, "mutants": mutants,
               "predecessor_head": verify.predecessor()["head"],
               "method": "Unchanged full 11-stage positive; two credited six-stage accepted mutants with all 20 final predicates, rejected by new gate. No cold ancestry."}
    with (work / "INTEGRATION.json").open("x") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    result = execute(parser.parse_args().work)
    print("PASS_SELECTED_OWNER_BOUND_INTEGRATION", "positive_stages=11", "accepted_then_rejected_mutants=2")
