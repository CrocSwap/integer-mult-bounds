"""Price the existing dedicated-bank repetition of the raw factory.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. The schedule and price formulas follow the PR531/PR622 lineage.
This module does not search or change an owner layout.
"""
import copy
from collections import Counter
from fractions import Fraction as Q

from circuit import need
from full import ROOT, read, digest

PARENT = ROOT / "research/direct-delivery504-global/inputs/data-base/split-centres/GLOBAL-TEMPLATE.json.gz"

GEOMETRY = ("adapter_policy", "cover", "cover_final_correction", "loop_order",
            "port_restriction", "route_semantics")


def construct(native, programs, physical_contract):
    parent = read(PARENT)
    v, helpers, stages, replicas, dimension = 112, 492, 9, 8, 73
    data = 2 * 4 * replicas * v
    live = data + stages * helpers
    need(native["R"] == helpers and native["v"] == v
         and all(native["start"][r] == 0 and native["final"][r] == 1
                 for r in range(2 * v, 2 * v + helpers)), "raw helper bank contract")
    calls = []
    for old in parent["calls"]:
        call = copy.deepcopy(old)
        call["owners"] = call["owners"][:2 * v] + [
            [data + call["stage"] * helpers + helper, [2, call["replica"]]]
            for helper in range(helpers)]
        call["local_program_sha256"] = programs[call["orientation"]]["word_sha256"]
        calls.append(call)
    schedule = []
    for old in parent["execution_schedule"]:
        if old["kind"] in ("local_cover_sweep", "bridge"):
            for replica in range(replicas):
                event = copy.deepcopy(old)
                event.pop("replicas", None)
                event["replica"] = replica
                schedule.append(event)
        else:
            event = copy.deepcopy(old)
            if event["kind"] == "bank_padding_cover_sweep":
                event["families"] = [data, live]
            elif event["kind"] == "translate_every_live_family":
                event["families"] = [0, live]
                event["charged_calls_per_cover"] = live
            schedule.append(event)
    banks = [{"family": data + stage * helpers + helper,
              "stage": stage, "helper": helper, "complement_axes": [72]}
             for stage in range(stages) for helper in range(helpers)]
    return {"format": "raw-factory-dedicated-bank-host-v1", "m": dimension,
            "v": v, "helpers": helpers, "live": live, "physical": live + helpers + 10,
            "parent_template_sha256": digest(parent), "recipe": parent["recipe"],
            "geometry": {key: parent[key] for key in GEOMETRY},
            "physical_contract": physical_contract,
            "data_phase_sha256": parent["exact_data_phase_recipe_sha256"],
            "calls": calls, "execution_schedule": schedule, "banks": banks,
            "idle_children": parent["idle_children"],
            "local_programs": programs,
            "private_namespace": {"centers": [live, live + 8],
                                  "reserved_tableau": [live + 8, live + 8 + helpers],
                                  "coefficient": [live + helpers + 8, live + helpers + 10]}}


def audit(host, native):
    """Check each literal role and each bank's complete coordinate partition."""
    parent = read(PARENT)
    data, v, helpers, dimension = 7168, 112, 492, 73
    old_native = read(PARENT.parent / "CANONICAL-WORD.json.gz")
    need(native["v"] == 112 and native["h"] == 9 and native["R"] == 492
         and native["ports"] == old_native["ports"], "changed hosted data ports")
    for endpoint in ("start", "final"):
        need(all(native["frames"][native[endpoint][r]] ==
                 old_native["frames"][old_native[endpoint][r]] for r in range(224)),
             "changed hosted data frame")
    need(all(native["start"][r] == 0 and native["final"][r] == 1 for r in range(224, 716))
         and len(native["frames"][1]) == 9, "changed hosted helper boundary")
    need(host["physical_contract"]["native_word_sha256"] == digest(native),
         "unbound native physical contract")
    need(host["parent_template_sha256"] == digest(parent)
         and host["recipe"] == parent["recipe"]
         and host["idle_children"] == parent["idle_children"], "changed parent recipe")
    need(host["data_phase_sha256"] == parent["exact_data_phase_recipe_sha256"],
         "changed data phase source")
    need(host["geometry"] == {key: parent[key] for key in GEOMETRY}, "changed host geometry")
    need(len(host["calls"]) == 72 and len(host["banks"]) == 4428, "missing hosted work")
    covered, addresses, used = set(), {}, {}
    for call, old in zip(host["calls"], parent["calls"]):
        stage, replica = call["stage"], call["replica"]
        need(type(stage) is int and type(replica) is int and 0 <= stage < 9 and 0 <= replica < 8,
             "invalid call address")
        need((stage, replica) not in covered, "duplicate complete call")
        covered.add((stage, replica))
        need(stage == old["stage"] and replica == old["replica"], "changed call address")
        need(call["orientation"] == old["orientation"]
             and call["owners"][:224] == old["owners"][:224]
             and call["window"] == old["window"] and call["pair"] == old["pair"],
             "changed data call")
        need(call["local_program_sha256"] == host["local_programs"][call["orientation"]]["word_sha256"],
             "unbound local program")
        need(len(call["owners"]) == 716
             and len({family for family, _ in call["owners"]}) == 716,
             "aliased complete-invocation owner")
        for helper, (family, route) in enumerate(call["owners"][224:]):
            need(family == data + stage * helpers + helper and route == [2, replica],
                 "wrong helper bank or chart")
            axes = set(range(9 * replica, 9 * replica + 9))
            need(not used.get(family, set()).intersection(axes), "overlapping bank footprint")
            used.setdefault(family, set()).update(axes)
            addresses[family] = (stage, helper)
    need(covered == {(s, r) for s in range(9) for r in range(8)}, "missing call address")
    need({b["family"] for b in host["banks"]} == set(used), "bank complement inventory")
    for bank in host["banks"]:
        family = bank["family"]
        need(addresses[family] == (bank["stage"], bank["helper"])
             and bank["complement_axes"] == [72], "wrong bank complement")
        need(used[family].isdisjoint(bank["complement_axes"])
             and used[family] | set(bank["complement_axes"]) == set(range(dimension)),
             "incomplete bank restoration")
    sweeps = [e for e in host["execution_schedule"] if e["kind"] == "local_cover_sweep"]
    need([(e["stage"], e["replica"]) for e in sweeps] ==
         [(c["stage"], c["replica"]) for c in host["calls"]], "wrong execution chronology")
    need(sum(e["kind"] == "bridge" for e in host["execution_schedule"]) == 72,
         "bridge repetition")
    need(host["live"] == 11596 and host["physical"] == 12098, "physical family bill")
    padding = [e for e in host["execution_schedule"] if e["kind"] == "bank_padding_cover_sweep"]
    final = [e for e in host["execution_schedule"] if e["kind"] == "translate_every_live_family"]
    need(len(padding) == len(final) == 1 and padding[0]["families"] == [data, host["live"]]
         and padding[0]["axis"] == 72 and padding[0]["rank"] == 1, "stale bank sweep")
    need(final[0]["families"] == [0, host["live"]]
         and final[0]["charged_calls_per_cover"] == host["live"], "unpaid final translation")
    # Check every retained schedule field, including bridge signs and adapters.
    index = 0
    for old in parent["execution_schedule"]:
        repeated = old["kind"] in ("local_cover_sweep", "bridge")
        count = 8 if repeated else 1
        group = host["execution_schedule"][index:index + count]
        need(len(group) == count, "incomplete schedule")
        for replica, event in enumerate(group):
            restored = copy.deepcopy(event)
            if repeated:
                need(restored.pop("replica") == replica, "changed schedule replica")
                if "replicas" in old:
                    restored["replicas"] = old["replicas"]
            elif old["kind"] == "bank_padding_cover_sweep":
                restored["families"] = old["families"]
            elif old["kind"] == "translate_every_live_family":
                restored["families"] = old["families"]
                restored["charged_calls_per_cover"] = old["charged_calls_per_cover"]
            need(restored == old, "changed schedule operation")
        index += count
    need(index == len(host["execution_schedule"]), "extra schedule operation")
    need(host["private_namespace"] == {
        "centers": [11596, 11604], "reserved_tableau": [11604, 12096],
        "coefficient": [12096, 12098]}, "private namespace overlap")
    profile = Counter({1: len(host["banks"])})
    for call in host["calls"]:
        profile.update({int(k): value for k, value in native["local_profile"].items()})
    for child in host["idle_children"]:
        profile[child["rank"]] += child["replicas"]
    mass = sum(rank * count for rank, count in profile.items())
    need(73 * host["live"] - mass == 2560, "banked rank-mass identity")
    return {"calls": 72, "helper_roles": 35424, "banks": len(host["banks"]),
            "bank_complement_rank": 1, "profile": dict(sorted(profile.items())),
            "rank_mass": mass, "rank_deficit": 2560,
            "orientation_counts": dict(Counter(c["orientation"] for c in host["calls"]))}


def invoice(host, admission, checks):
    """Retain every generic adapter, router, tape and precision allowance."""
    m, v, helpers, centers, replicas, stages = 73, 112, 492, 8, 8, 9
    local = host["local_programs"]
    macro_slots = max(c["scalar_macros"] for c in checks.values())
    children = sum(admission["profile"].values())
    local_children = sum(local["forward"]["paid_profile"].values())
    compiler = 64 * (m + 1) ** 3
    adapters = 16 * (macro_slots + local_children + 716 + centers) + 64 * m
    # The block retains all original scalar interfaces and frame transitions.
    # Its added unary scales commute with coordinate adapters. See PROOF.md.
    local_bound = max(p["real_primitives"] for p in local.values()) + adapters * compiler
    scalar = sum(local[c["orientation"]]["real_primitives"] for c in host["calls"])
    bridges = 72
    bridge_additions, shifts, moves = 2 * v * bridges, 4 * v * replicas, 8 * v * replicas
    live, physical = host["live"], host["physical"]
    nonlocal_items = (4 * v * replicas * stages + 2 * v * replicas * stages
                      + 2 * 72 * helpers + sum(x["replicas"] for x in host["idle_children"])
                      + len(host["banks"]) + bridge_additions + shifts + moves
                      + live + physical)
    outside = 8 * nonlocal_items + 64 * m
    per_vertex = (scalar + bridge_additions + shifts + moves + live
                  + (72 * adapters + outside) * compiler + 64 * physical)
    group = 2 ** (36 * 36)
    for i in range(1, 37):
        group *= 2 ** (2 * i) - 1
    stock, streamed_mass = group * physical, group * admission["rank_mass"]
    logical = group * per_vertex + 64
    router = compiler * (logical + 1) * (stock + 1) ** 2
    total_mass = streamed_mass + 2 ** 100000
    literal = 2 * 2 ** 30000 * stock ** 2 + 8 * streamed_mass + 4 * stock + 4 + 32 * m
    payload = 512
    row = 2 * stock.bit_length() + 9909 + 252 + 2 * payload
    maximum_child = max(admission["profile"])
    local_bits = max(Q(p["positive_peak"]).numerator.bit_length()
                     - Q(p["positive_peak"]).denominator.bit_length() + 1
                     for p in local.values())
    required_prefix = local_bits + 37 + 72 + bridges + 4
    strict = {"local": local_bound < 2 ** 48, "logical": logical < 2 ** 6050,
              "router": router < 2 ** 30000, "literal": literal < 2 ** 100000,
              "mass": total_mass < 2 ** 100001, "precision": 32 * m * total_mass ** 2 < 2 ** 210000,
              "tape": 2 * total_mass + 18 < 2 ** 210000, "row": row < 20161,
              "halving": m * m > 2 * maximum_child ** 2, "prefix": required_prefix < payload}
    need(all(strict.values()), "complete paid finite charge")
    return {"local_macro_slots_retained": macro_slots, "local_children": local_children,
            "all_paid_children": children, "compiler": compiler, "local_adapters": adapters,
            "factory_new_frame_conversions": 0,
            "factory_adapter_reserve_per_block_retained": 16 * 32,
            "local_primitive_bound": local_bound, "hosted_scalar_primitives": scalar,
            "hosted_operand_reads": sum(local[c["orientation"]]["operand_reads"] for c in host["calls"]),
            "outside_adapter_reserve": outside, "wrapper_factors": 0,
            "per_cover_vertex_bound": per_vertex, "bridge_sweeps": bridges,
            "global_prefix_bits": required_prefix, "charged_payload_bits": payload,
            "physical_stock_bits": stock.bit_length(), "router_bits": router.bit_length(),
            "literal_bits": literal.bit_length(), "physical_row_coefficient": row,
            "strict_checks": strict}
