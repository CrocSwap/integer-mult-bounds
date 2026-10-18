"""Scoped PR626 replica-prefix audit; Python 3.10+, standard library only.

The native supplier and physical realization assumptions remain inherited.
Prepared for Brody Arbon with substantial OpenAI Codex assistance; Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_sources(root):
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    sources = {}
    for label, entry in manifest["inputs"].items():
        path = root / entry["path"]
        raw = path.read_bytes()
        data = gzip.decompress(raw) if entry["representation"] == "gzip-payload" else raw
        require(digest(data) == entry["sha256"], "source pin: " + label)
        if entry["path"].endswith((".json", ".json.gz")):
            sources[label] = json.loads(data)
    return manifest, sources


def schedule_audit(parent, plan, invoice, owners):
    """Reconstruct just source-event identities and norm-factor counts."""
    order = plan["order"]
    require(len(order) == 72, "72 calls")
    require(all(isinstance(x, list) and len(x) == 2 and
                all(type(v) is int for v in x) and
                0 <= x[0] < 9 and 0 <= x[1] < 8 for x in order), "call domain")
    require(len(set(map(tuple, order))) == 72, "call uniqueness")
    for replica in range(8):
        require([s for s, r in order if r == replica] == list(range(9)), "replica chronology")
    calls = plan["provider_calls"]
    require(len(calls) == len(invoice["selected_calls"]) == 72, "dispatch size")
    for time, ((stage, replica), call, charged) in enumerate(zip(order, calls, invoice["selected_calls"])):
        require((call["time"], call["stage"], call["replica"]) == (time, stage, replica), "dispatch order")
        require((charged["stage"], charged["replica"]) == (stage, replica), "invoice order")
        require(call["provider"] == charged["provider_id"], "provider binding")
        require(call["orientation"] == charged["orientation"] ==
                ("backward" if stage % 2 else "forward"), "orientation")
        require(call["local_program_sha256"] == charged["program_sha256"], "program binding")

    source = parent["execution_schedule"]
    require(len(source) == 32, "source schedule size")
    require([e["kind"] for e in source[-2:]] ==
            ["bank_padding_cover_sweep", "translate_every_live_family"], "global suffix")
    blocks, stage = {}, None
    kinds = {"local_cover_sweep", "bridge", "idle_cover_sweep", "terminal_Y_translations", "terminal"}
    for position, event in enumerate(source[:-2]):
        require(event["kind"] in kinds, "unknown event")
        if event["kind"] == "local_cover_sweep":
            stage = event["stage"]
            require(stage not in blocks, "duplicate local stage")
            require(event["replicas"] == list(range(8)), "source replicas")
            blocks[stage] = []
        require(stage is not None, "event before first call")
        if event["kind"] == "bridge":
            require(type(event["coefficient"]) is int and abs(event["coefficient"]) == 1,
                    "bridge norm factor")
            require(all(type(event[k]) is int and 0 <= event[k] < 4 for k in ("src", "dst"))
                    and event["src"] != event["dst"], "bridge family domain")
            require("source_replica" not in event and "target_replica" not in event,
                    "cross-replica bridge")
        blocks[stage].append((position, event))
    require(set(blocks) == set(range(9)), "nine local stages")
    require(Counter(e["kind"] for e in source[:-2])["bridge"] == 9, "nine bridges")

    # Explicit disjoint streamed data families in the retained source controller.
    expected_pairs = [0, 0, 0, 1, 1, 2, 2, 3, 3]
    require(len(parent["calls"]) == 72, "parent calls")
    for call in parent["calls"]:
        s, r = call["stage"], call["replica"]
        require(call["pair"] == expected_pairs[s], "source pair")
        require(call["owners"][:224] ==
                [[896 * r + 224 * expected_pairs[s] + j, [1, s, j % 112]] for j in range(224)],
                "active data owners")

    # This checks family ownership, not geometry, windows or residual unitarity.
    roles, cross = set(), 0
    per_call_families = {}
    require(len(owners) == 72 * 492, "helper role count")
    for row in owners:
        s, r, h, f, owner = (row[k] for k in ("stage", "replica", "helper", "family", "owner_replica"))
        require(all(type(x) is int for x in (s, r, h, f, owner)), "integer owner")
        require(0 <= s < 9 and 0 <= r < 8 and 0 <= h < 492 and 0 <= f < 7168,
                "helper domain")
        require(owner == f // 896, "owner replica")
        require((s, r, h) not in roles, "duplicate helper")
        roles.add((s, r, h))
        families = per_call_families.setdefault((s, r), set())
        require(f not in families, "helper family alias")
        require(not (896 * r + 224 * expected_pairs[s] <= f <
                     896 * r + 224 * expected_pairs[s] + 224), "helper on active data")
        families.add(f)
        cross += owner != r

    factors, counters, projection = [0] * 8, Counter(), [[] for _ in range(8)]
    trace, prefix_max = [], 0
    for time, ((s, r), call) in enumerate(zip(order, calls)):
        localbits = invoice["providers"][call["provider"]]["local"][call["orientation"]]["prefix_bits"]
        require(type(localbits) is int and 0 < localbits <= 101, "local prefix bits")
        for position, event in blocks[s]:
            kind = event["kind"]
            projection[r].append(position)
            # A local prefix may read restored/unitarily transformed helpers from
            # any owner replica. Thus use the maximum over ALL owner bounds.
            if kind == "local_cover_sweep":
                prefix_max = max(prefix_max, localbits + max(factors))
            if kind in ("local_cover_sweep", "bridge"):
                factors[r] += 1
                counters[kind] += 1
            prefix_max = max(prefix_max, max(factors))
            trace.append([time, s, r, position, list(factors)])
    require(all(p == list(range(30)) for p in projection), "complete source projection")
    require(factors == [18] * 8, "per-replica growth count")
    require(counters == {"local_cover_sweep": 72, "bridge": 72}, "global growth count")
    require(cross == 28404, "selected cross-replica roles")
    return {
        "calls": 72, "source_events_per_replica": 30, "scheduled_replica_events": len(trace),
        "helper_roles": len(roles), "cross_replica_helper_roles": cross,
        "growth_factors_per_replica": factors, "global_growth_factors": sum(factors),
        "local_and_controller_prefix_bits": prefix_max,
        "trace_sha256": digest(canonical(trace)),
        "endpoint_norm": "maximum of individual streamed-family L2 norms, grouped by owner replica",
    }


def controls(sources):
    failures = []
    def reject(name, which, change):
        copied = {k: deepcopy(sources[k]) for k in ("parent", "plan", "invoice", "owners")}
        change(copied[which])
        try:
            schedule_audit(**copied)
        except ValueError:
            failures.append(name)
        else:
            raise ValueError("control accepted: " + name)
    reject("duplicate_call", "plan", lambda p: p["order"].__setitem__(1, p["order"][0]))
    reject("out_of_order_replica", "plan", lambda p: p["order"].__setitem__(0, [1, 0]))
    reject("changed_provider", "invoice", lambda p: p["selected_calls"][0].__setitem__("provider_id", "jp8"))
    reject("doubled_bridge", "parent", lambda p: p["execution_schedule"][3].__setitem__("coefficient", 2))
    reject("cross_replica_bridge", "parent", lambda p: p["execution_schedule"][3].__setitem__("source_replica", 1))
    reject("missing_bridge", "parent", lambda p: p["execution_schedule"][3].__setitem__("kind", "terminal"))
    reject("unknown_event", "parent", lambda p: p["execution_schedule"][2].__setitem__("kind", "unpriced_map"))
    reject("data_owner_in_other_replica", "parent", lambda p: p["calls"][0]["owners"][0].__setitem__(0, 896))
    reject("wrong_helper_replica", "owners", lambda p: p[0].__setitem__("owner_replica", (p[0]["owner_replica"] + 1) % 8))
    reject("aliased_helper_family", "owners", lambda p: p[1].update(family=p[0]["family"], owner_replica=p[0]["owner_replica"]))
    reject("helper_on_active_data", "owners", lambda p: p[0].update(family=0, owner_replica=0))
    reject("missing_local_allowance", "invoice", lambda p: p["providers"]["ck"]["local"]["forward"].__setitem__("prefix_bits", 0))
    return failures


def run(root):
    manifest, sources = read_sources(root)
    invoice, prefix = sources["invoice"], sources["prefix"]
    require(invoice["status"] == "PASS_INDEPENDENT_MIXED_ASYNC_SCALAR_PREFIX_AND_FINITE_INVOICE", "invoice status")
    require(prefix["status"] == "PASS_MIXED_ASYNC_GLOBAL_PREFIX", "prefix status")
    require(invoice["template_sha256"] == prefix["template_sha256"], "template receipt binding")
    require(invoice["controller_audit_sha256"] == prefix["controller_audit_sha256"], "controller binding")
    require(sources["controller_receipt"]["template_sha256"] == invoice["template_sha256"], "controller template")
    require(sources["controller_receipt"]["one_owner_per_complete_invocation"] is True,
            "whole-invocation receipt")
    for pid in ("ck", "jp8"):
        program = sources[pid + "_program"]
        for orientation in ("forward", "backward"):
            actual = digest(json.dumps(program[orientation], separators=(",", ":")).encode())
            require(actual == invoice["providers"][pid]["program_hashes"][orientation], "native program binding")
            local = invoice["providers"][pid]["local"][orientation]
            prior = sources[pid + "_replay"]["local"][orientation]
            require(local["prefix_l1"] == prior["prefix_l1_upper"] and
                    local["prefix_bits"] == prior["prefix_bits_upper"] and
                    prior["private_work_erased"] is True, "inherited local prefix binding")
            require(local["all_dirty_helper_columns_restored"] is True and
                    local["private_centres_and_coefficient_work_cleared"] is True and
                    local["all_exact_columns"] == 716, "inherited scalar receipt")
            require(Fraction(local["prefix_l1"]) < 2 ** local["prefix_bits"], "local envelope")
    result = schedule_audit(**{k: sources[k] for k in ("parent", "plan", "invoice", "owners")})
    local = max(v["prefix_bits"] for p in invoice["providers"].values() for v in p["local"].values())
    require((local, prefix["stream_input_sup_to_l2_bits"], prefix["primitive_arithmetic_margin_bits"]) == (101, 37, 4), "inherited allowances")
    original = local + 37 + result["global_growth_factors"] + 4
    revised = local + 37 + max(result["growth_factors_per_replica"]) + 4
    scheduled = result["local_and_controller_prefix_bits"] + 37 + 4
    require(original == prefix["global_prefix_bits"] == invoice["global_prefix_bits"] == 286, "old bound")
    require(scheduled <= revised == 160 < prefix["retained_payload_bits"] == 512, "scoped new bound")
    spec = importlib.util.spec_from_file_location("replica_prefix_models", HERE / "model_checks.py")
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return {
        "status": "PASS_REPLICA_PREFIX_AUDIT", "base_commit": manifest["base_commit"],
        "assignment_seed": 72, "schedule": result,
        "prefix_bits": {"inherited_local": local, "inherited_input_conversion": 37,
                        "inherited_arithmetic_margin": 4, "old": original,
                        "replica_bound": revised, "schedule_sensitive_bound": scheduled,
                        "reduction": original - revised, "retained_payload": 512},
        "schedule_controls": controls(sources), "finite_models": model.run_checks(),
        "scope": "Conditional precision-accounting refinement only; no new kappa, cold supplier replay, physical realization proof or production integration.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--record", type=Path, help="write a NEW receipt instead of comparing EXPECTED.json")
    args = parser.parse_args()
    result = run(args.repo.resolve())
    if args.record:
        with args.record.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads((HERE / "EXPECTED.json").read_bytes()), "expected receipt mismatch")
    print("PASS_REPLICA_PREFIX_AUDIT calls=72 owner_roles=35424 prefix_bits=286->160 retained_payload=512 no_new_kappa")


if __name__ == "__main__":
    main()
