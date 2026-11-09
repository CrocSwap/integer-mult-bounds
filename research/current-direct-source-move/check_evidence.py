"""Validate manual evidence and boundary bytes without replaying long calls.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from copy import deepcopy
from hashlib import sha256
import json
from direct_sources import HERE, need
from check_move import fixture, encode_header


def first_attempt(item, raw_log):
    need(item["status"] == "timeout" and item["exit_code"] == 124
         and item["cap_seconds"] == 580 and item["elapsed_seconds"] >= 580,
         "preserved initial bounded timeout")
    need(item["complete_raw_MOVE_executed"] is False
         and item["exit_or_commit_receipt"] is False
         and item["byte_validated_saved_boundaries"] is False
         and item["returned_factor_telemetry_only"] is True,
         "initial telemetry is not a completed or byte-validated witness")
    need(sha256(raw_log).hexdigest() == item["log_sha256"]
         and b"COMPLETE_DIRECT_MOVE" not in raw_log, "complete preserved first log")
    rows = [json.loads(line.split(" ",1)[1]) for line in raw_log.decode().splitlines()
            if line.startswith("RETURNED_FACTOR ")]
    need(rows == item["returned_factors"]
         and [row["factor"] for row in rows] == ["entrance", "positive_child"],
         "only the two observed original returned factors")
    need([row["physical_actions"] for row in rows] == [2720267547,316154275],
         "preserved original partial action telemetry")
    for name, expected in item["production_source_sha256"].items():
        need(sha256((HERE/name).read_bytes()).hexdigest() == expected,
             "unchanged production source across the observational harness refinement")
    return dict(status="timeout", returned_factors=2, complete_MOVE=False,
                byte_validated_boundaries=False, cap_seconds=580)


def boundary(name, record, stage, parent, wanted, initial, expected, header, cumulative):
    need(stage == bytes(wanted) and parent == bytes(header), "complete independent boundary stage/header bytes")
    need(record["factor"] == name and record["stage_sha256"] == sha256(stage).hexdigest()
         and record["parent_sha256"] == sha256(parent).hexdigest(), "recorded exact complete boundary hashes")
    public = expected if name == "commit" else initial
    need(record["public_sha256"] == sha256(bytes(public)).hexdigest(), "original public body protected until complete commit")
    need(record["cumulative_run_actions"] == cumulative
         and record["byte_validated_complete_boundary"] is True
         and record["prior_cohorts_retained_in_space"] is True
         and record["all_heads_at_origins"] is True
         and record["other_private_bodies_blank"] is True
         and record["logging_is_read_only_harness"] is True,
         "actual returned boundary observation and literal cumulative bill")
    extents = record["private_materialized_extents"]
    need(len(extents) == 4235 and all(type(n) is int and n >= 1 for n in extents)
         and not record.get("materialized_is_exact_visited", False), "complete rolewise materialized backing, not visited claim")
    regions = sum(3+j % 5+1 for j in range(4235))+(9+1)+(11+1)+len(initial)+len(header)
    need(record["conservative_all_visited_cells"] == regions+cumulative,
         "conservative supplied-regions plus literal-action visited bound")
    return extents


def final_attempt(folder):
    execution = json.loads((folder/"EXECUTION.json").read_text())
    need(execution["cap_seconds"] == 1100 and execution["source_commit"] ==
         "fc2c8585d8eb20687aa124c64853b0aeecc4dbde", "one final authorized committed source attempt")
    checkpoint = json.loads((HERE/"CHECKPOINT.json").read_text())
    for name, expected_hash in checkpoint["source_sha256"].items():
        need(sha256((HERE/name).read_bytes()).hexdigest() == expected_hash,
             "exact critical source bytes from the executed checkpoint")
    raw_log = (folder/"execution.log").read_text()
    returned = [json.loads(line.split(" ",1)[1]) for line in raw_log.splitlines()
                if line.startswith("RETURNED_FACTOR ")]
    completions = [json.loads(line.split(" ",1)[1]) for line in raw_log.splitlines()
                   if line.startswith("COMPLETE_DIRECT_MOVE ")]
    names = ["entrance", "positive_child", "exit", "commit"]
    need([row["factor"] for row in returned] == names[:len(returned)]
         and len(returned) <= 4, "actual ordered returned-factor prefix")
    triple, values, initial, expected, targets = fixture(True)
    header = encode_header(values); V = len(initial); cumulative = 8*V+14
    extents = None; checked = []
    for row in returned:
        name = row["factor"]; cumulative += row["physical_actions"]
        record = json.loads((folder/(name+"-boundary.json")).read_text())
        stage = (folder/(name+"-stage.bits")).read_bytes()
        parent = (folder/(name+"-parent.bits")).read_bytes()
        current = boundary(name,record,stage,parent,targets[name],initial,expected,header,cumulative)
        need(extents is None or all(a <= b for a,b in zip(extents,current)),
             "every already-materialized cohort stays allocated")
        extents = current
        checked.append(dict(factor=name, cumulative_run_actions=cumulative,
                            materialized_private_body=sum(extents), stage_sha256=record["stage_sha256"]))
    complete = execution["exit_code"] == 0
    if complete:
        need(0 < execution["elapsed_seconds"] < execution["cap_seconds"],
             "completed within the allocated manual process cap")
        need(len(completions) == 1 and len(returned) == 4, "complete returned run and all four byte-validated boundaries")
        result = completions[0]; bills = {row["factor"]:row["physical_actions"] for row in returned}
        need(result["complete_raw_MOVE_executed"] is True
             and result["source_event"] == triple[1].token[1]
             and result["source_owner"] == triple[1].fields[0]
             and result["physical_bits"] == V and result["records"] == 4096
             and result["columns"] == result["rank"] == 1
             and result["private_ports"] == 4235 and result["ordinary_runtime_entries"] == 0
             and result["factor_actions"] == bills, "complete actual selected direct source witness")
        need(result["physical_actions"] == cumulative+5*V+7
             == bills["entrance"]+bills["positive_child"]+bills["exit"]+22*V+35
             and bills["commit"] == 9*V+14 and result["protected_admin_actions"] == 22*V+35,
             "all executed factors and complete protected-stage actions")
        need(result["endpoint_sha256"] == sha256(bytes(expected)).hexdigest()
             and result["exact_prefix_admission"] is True
             and result["stronger_input_divisibility_envelope"] is False
             and result["long_record_absorption_regime"] is False
             and result["enclosing_selected_caller_claim"] is False,
             "exact endpoint and bounded witness scope")
        final_extents = result["private_materialized_extents"]
        need(len(final_extents) == 4235 and all(a <= b for a,b in zip(extents,final_extents)),
             "all retired historical cohorts remain charged at final return")
        compact_records = [{key:json.loads((folder/(name+"-boundary.json")).read_text())[key]
                            for key in ("factor", "stage_sha256", "parent_sha256", "public_sha256",
                                        "cumulative_run_actions", "conservative_all_visited_cells")}
                           for name in names]
        need(result["byte_validated_boundaries"] == compact_records,
             "final receipt repeats exactly the four actual saved boundaries")
    else:
        need(execution["exit_code"] == 124 and not completions,
             "timeout cannot be called a complete whole MOVE witness")
        result = None
    mutants = 0
    if returned:
        first = returned[0]; name = first["factor"]
        record = json.loads((folder/(name+"-boundary.json")).read_text())
        stage = (folder/(name+"-stage.bits")).read_bytes(); parent=(folder/(name+"-parent.bits")).read_bytes()
        bad_stage = bytearray(stage); bad_stage[0] ^= 1
        variants = [(record,bytes(bad_stage)), (dict(record,public_sha256="0"*64),stage),
                    (dict(record,materialized_is_exact_visited=True),stage)]
        for altered, altered_stage in variants:
            try:
                boundary(name,altered,altered_stage,parent,targets[name],initial,expected,header,8*V+14+first["physical_actions"])
            except ValueError:
                mutants += 1
            else:
                raise ValueError("incorrect saved boundary evidence accepted")
    return dict(complete_raw_MOVE=complete, returned_boundaries=checked,
                boundary_mutants_rejected=mutants, cap_seconds=1100,
                total_physical_actions=None if result is None else result["physical_actions"],
                check_is_saved_evidence_not_numeric_reexecution=True)


def check():
    root = HERE/"evidence"
    item = json.loads((root/"ATTEMPT-580.json").read_text()); raw_log=(root/"attempt-580.log").read_bytes()
    first = first_attempt(item,raw_log)
    wrong = deepcopy(item); wrong["complete_raw_MOVE_executed"] = True
    try:
        first_attempt(wrong,raw_log)
    except ValueError:
        pass
    else:
        raise ValueError("first timeout promoted to a complete witness")
    folder = root/"final-1100"
    final = final_attempt(folder) if (folder/"EXECUTION.json").exists() else None
    return dict(first=first, first_completion_mutant_rejected=True, final=final,
                final_attempt_unrecorded=final is None, no_new_kappa=True)


if __name__ == "__main__":
    result = check()
    need(result == json.loads((HERE/"EVIDENCE-RESULT.json").read_text()),
         "exact expected saved-evidence result")
    print("PASS_CURRENT_DIRECT_MOVE_EVIDENCE", json.dumps(dict(
        first_timeout_preserved=True,
        final_complete=False if result["final"] is None else result["final"]["complete_raw_MOVE"],
        validated_final_boundaries=0 if result["final"] is None else len(result["final"]["returned_boundaries"]),
        numeric_reexecution=False),sort_keys=True))
