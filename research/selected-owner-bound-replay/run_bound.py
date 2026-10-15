"""Opt-in successor: unchanged selected strict replay AND owner postcondition.

This does not replace the selected command or rebuild the local provider's
ancestry. Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import binding as b


STAGES = ["restore-parent", "bind8", "lift16", "bind", "emit", "audit", "invoice",
          "assembly", "admission-controls", "bit-supplier-controls", "independent-t16"]


def run(local, work):
    source_pins = b.pins()
    local, work = local.resolve(), work.resolve()
    b.need(local.is_dir(), "local provider directory missing")
    b.need(not work.exists() and not work.is_relative_to(b.ROOT), "use fresh output outside repository")
    work.mkdir(parents=True)
    legacy = work / "legacy"
    command = [sys.executable, "-B", str(b.ROOT / b.STAGE / "verify.py"),
               "--main", str(b.ROOT), "--local", str(local), "--work", str(legacy)]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for key in ("PYTHONOPTIMIZE", "WITNESS_SPEC", "WITNESS_DISCOVER", "WITNESS_RECORD"):
        env.pop(key, None)
    log = work / "legacy.log"
    with log.open("x") as output:
        result = subprocess.run(command, cwd=b.ROOT, env=env, stdout=output, stderr=subprocess.STDOUT)
    b.need(result.returncode == 0, "unchanged strict replay failed; see " + str(log))
    strict = legacy / "strict"
    replay_raw = (strict / "REPLAY.json").read_bytes()
    replay = b.decode(replay_raw)
    b.need(replay["status"] == "PASS_GAUGE44_T16_STRICT_GLOBAL_REPLAY", "strict status")
    stages_raw = (strict / "STAGES.json").read_bytes()
    stages = b.decode(stages_raw)
    b.need(stages == replay["stages"] and [x["name"] for x in stages] == STAGES
           and all(x["exit_code"] == 0 for x in stages), "strict stage coverage")
    for row in stages:
        b.need(b.sha((strict / (row["name"] + ".log")).read_bytes()) == row["log_sha256"], "stage log binding")
    owner_raw = (b.ROOT / b.OWNER).read_bytes()
    b.need((legacy / "source/data/OWNERS.json.gz").read_bytes() == owner_raw, "executed owner source differs")
    condition = b.check((strict / "global/hosted/GLOBAL-TEMPLATE.json.gz").read_bytes(),
                        owner_raw, source_pins[str(b.OWNER)])
    # Bind the map just checked to the same template named by the actual fresh
    # assembly/invoice/owner receipts, not merely to a sibling template file.
    for name in ("ASSEMBLY.json", "global/audit/OWNERS-AND-PROFILE.json",
                 "global/audit/PREFIX-AND-INVOICE.json", "global/hosted/HOSTED.json"):
        receipt = b.decode((strict / name).read_bytes())
        b.need(receipt["template_sha256"] == condition["template_payload_sha256"], "fresh template receipt binding")
    b.need(b.pins() == source_pins, "source drift during replay")
    receipt = {"schema": "selected-owner-bound-replay/1", "status": "PASS_SELECTED_OWNER_BOUND_REPLAY",
               "strict_replay_executed": True, "strict_stages": STAGES,
               "strict_replay_sha256": b.sha(replay_raw), "strict_stage_ledger_sha256": b.sha(stages_raw),
               "strict_log_sha256": b.sha(log.read_bytes()), "owner_binding": condition,
               "kappa": replay["kappa"], "source_pins": source_pins,
               "scope": "Unchanged selected final strict replay plus exact owner-map postcondition; local provider supplied; no cold ancestry or all-size proof."}
    with (work / "BOUND-REPLAY.json").open("x") as handle:
        json.dump(receipt, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    receipt = run(args.local, args.work)
    print(receipt["status"], "roles=" + str(receipt["owner_binding"]["roles"]), flush=True)


if __name__ == "__main__":
    main()
