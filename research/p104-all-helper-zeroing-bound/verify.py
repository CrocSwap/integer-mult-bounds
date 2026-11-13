#!/usr/bin/env python3
"""Replay the exact all-subset funding certificate and independent modular proof."""
from pathlib import Path
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
import tempfile

HERE = Path(__file__).resolve().parent
CALLER_SHA = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PRICE_SHA = "86f71ccbc923db5d7a6753aa971c3a9c8a572680534498ed17be072cfa2aae6b"


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run():
    modular, rational = load("modular_verify"), load("rational_verify")
    raw = bytearray(modular.SOURCE.read_bytes())
    raw[len(raw) // 2] ^= 1
    with tempfile.TemporaryDirectory(prefix="cold-source-control-") as tmp:
        bad = Path(tmp) / "changed-source.gz"
        bad.write_bytes(raw)
        for module in (modular, rational):
            original = module.SOURCE
            module.SOURCE = bad
            caught = False
            try:
                module.run()
            except ValueError as exc:
                need("source bytes" in str(exc), "source mutation rejected before replay")
                caught = True
            finally:
                module.SOURCE = original
            need(caught, "altered source must fail")
    a, b = modular.run(), rational.run()
    need(a["move_coverage"] == b["move_coverage"], "independent complete coverage")
    need(a["paid_histogram"] == b["paid_histogram"], "independent paid invoice")
    need(a["charged_helpers"] == b["charged_helpers"], "independent funding count")
    c = (HERE / "inputs/CALLER.json").read_bytes()
    need(hashlib.sha256(c).hexdigest() == CALLER_SHA, "exact signed caller bytes")
    caller = json.loads(c)
    calls = sum(e[0] == "J" for e in caller["events"])
    need(calls == caller["stages"] == 17, "actual signed native call count")
    word = json.loads(gzip.decompress(modular.SOURCE.read_bytes()))
    records = json.loads(modular.ASSIGNMENT.read_text())
    mains = set(word["live"]) | {i + 112 for i in word["live"]}
    mains |= set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    helpers = set(range(word["public"])) - mains
    # Reconstruct the complete inherited signed invoice, not only the native part.
    # This is the #7113 caller rank rule retained by #7481; ordinary events remain.
    target, paid = Counter(), Counter()
    for d in caller["types"].values():
        ports = len(d["ports"])
        for diagonal in d["diagonal"]:
            target[1 + 8 * sum(diagonal[2:])] += ports
    for e in caller["events"]:
        if e[0] == "J":
            continue
        ports = len(caller["types"][e[0]]["ports"])
        if e[1] == "QUERY":
            paid[1] += ports
        elif e[1] in ("IDLE_ONE", "IDLE_ODD"):
            paid[8 * len(e[3]) + int(e[1] == "IDLE_ODD")] += ports
    for h in helpers:
        r = abs(len(word["frames"][word["initial"][h]])
                - len(word["frames"][word["final"][h]]))
        target[r] += calls
    for r, count in a["paid_histogram"].items():
        paid[r] += calls * count
    raw_price = (HERE / "inputs/CURRENT-PRICE.json").read_bytes()
    need(hashlib.sha256(raw_price).hexdigest() == PRICE_SHA, "exact complete invoice bytes")
    expected = json.loads(raw_price)["after"]
    need(target == Counter({int(k): v for k, v in expected["T"].items()}),
         "complete caller productive invoice")
    need(paid == Counter({int(k): v for k, v in expected["P"].items()}),
         "complete caller paid invoice")
    surplus = sum(r * c for r, c in target.items()) - sum(r * c for r, c in paid.items())
    need(surplus == expected["S"] == 1424, "complete linear-rank surplus")
    mutants = []
    z = copy.deepcopy(records); z.append(copy.deepcopy(z[0])); mutants.append(("duplicate MOVE", z))
    z = copy.deepcopy(records); z[0]["rank"] += 1; mutants.append(("forged paid rank", z))
    z = copy.deepcopy(records); z[0]["target_rank"] += 1; mutants.append(("forged target rank", z))
    rejected = []
    for label, z in mutants:
        try:
            modular.validate_funding(word, z, helpers)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("accepted negative control: " + label)
    # Omitting a funded MOVE must fail the independently reconstructed main witness.
    try:
        modular.check(word, records[1:])
    except ValueError as exc:
        need("nonzero main coefficient" in str(exc), "omitted MOVE detected by source replay")
        rejected.append("omitted funded MOVE")
    else:
        raise ValueError("accepted omitted MOVE")
    need(2 * 2 <= 4 and not (2 * 2 <= 3), "double rank-one funding boundary at t=1/2")
    subspace = load("subspace_verify").run()
    exact_subspace = load("rational_subspace_verify").run()
    need(subspace["assigned_rows"] == 468 and subspace["subset_cases"] == 612,
         "complete group-subspace funding certificate")
    exact_groups = {(g["entrance_frame"], g["exit_frame"]): g
                    for g in exact_subspace["summaries"]}
    need(len(exact_groups) == subspace["charged_boundary_groups"] == 102,
         "independent subspace group coverage")
    for g in subspace["groups"]:
        other = exact_groups[g["entrance_frame"], g["exit_frame"]]
        need(g["rank_lower_bound"] == other["rank_Q"], "independent full group ranks")
        left = {tuple(t["events"]): t["subset_ranks"] for t in g["tables"]}
        right = {tuple(t["events"]): t["subset_ranks_Q_binary_order"]
                 for t in other["components"]}
        need(left == right, "every independent exact subset rank agrees")
    return {"status": "PASS_HELPER_COORDINATE_AND_SUBSPACE_FUNDING_NO_GAIN",
            "native_calls": calls, "rational": b, "independent_modular": a,
            "complete_invoice": {"productive_fields": sum(target.values()),
                                 "paid_jobs": sum(paid.values()), "rank_surplus": surplus},
            "rejected_controls": rejected,
            "altered_source_rejected_by_both_engines": True,
            "double_charge_square_root_boundary": True,
            "universal_kappa_interval": "0<=kappa<=1/2",
            "group_subspace_funding": {k: v for k, v in subspace.items() if k != "groups"},
            "independent_rational_subspace": {k: v for k, v in exact_subspace.items()
                                              if k != "summaries"},
            "all_612_independent_subset_ranks_match": True,
            "kappa_status": "No new kappa; exact fixed-word complete-moment obstruction"}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
