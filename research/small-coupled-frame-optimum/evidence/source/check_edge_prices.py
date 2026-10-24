#!/usr/bin/env python3
"""No-change audit of the mapped-DAG objective; no candidate optimization."""
from collections import Counter
import json
from inspect_graph import HERE, FROZEN, load, need


def main():
    data, construct, frame = load()
    published = json.loads((FROZEN / "research/carried-warp-frame-intervals/RESULT.json").read_text())
    result = {"status": "PASS_MAPPED_EDGE_PRICE_BINDING", "directions": {},
              "candidate_optimization_executed": False, "physical_phase_admission": False}
    for direction, source_program in data["programs"].items():
        program, _, _ = construct(source_program)
        schedule = frame.NativeSchedule(data["canonical"], program)
        graph = schedule.graph
        lower, upper = graph.bounds()
        centers = Counter(e[-1] for e in program if e[0] == "center")
        need(centers == Counter({8: 8}), "Owned centre invoice")
        duplicated_operand_contacts = []
        for event in program:
            if event[0] == "scalar" and event[1][0] in ("add", "copy"):
                if event[1][1] == event[1][2]:
                    duplicated_operand_contacts.append(event)
        need(not duplicated_operand_contacts, "Repeated operand needs special edge-price treatment")
        records = {}
        for name, values in [("original_contacts", schedule.original_values), ("least", lower), ("greatest", upper)]:
            profile = centers.copy()
            zero_edges = 0
            for b, parents in enumerate(graph.parents):
                for a, columns in parents:
                    image = frame.image(columns, values[a])
                    need(image & values[b] == image, "Mapped containment")
                    rank = frame.dimension(values[b])-frame.dimension(values[a])
                    need(rank >= 0, "Ascending edge rank")
                    if rank:
                        profile[rank] += 1
                    else:
                        zero_edges += 1
            expected = Counter({int(k):v for k,v in published["directions"][direction]["schedules"][name]["paid"].items()})
            need(profile == expected, "Mapped-edge price differs from literal published price: " + name)
            records[name] = {"paid":dict(sorted(profile.items())), "rank_mass":sum(r*n for r,n in profile.items()),
                             "zero_rank_edges":zero_edges, "counted_multiedges":sum(map(len,graph.parents))}
        result["directions"][direction] = {"source_owned_centres":dict(centers),
            "duplicate_operand_contacts":len(duplicated_operand_contacts), "profiles":records}
    (HERE / "EDGE-PRICE-CHECK.json").write_text(json.dumps(result,indent=2)+"\n")
    print(result["status"])


if __name__ == "__main__":
    main()
