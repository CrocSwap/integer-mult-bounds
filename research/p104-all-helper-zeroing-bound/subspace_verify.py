#!/usr/bin/env python3
"""Independent prime-field lower ranks and exact subspace funding certificate.

Only nonzero modular minors are lifted to characteristic zero. No modular zero
or modular dependence is asserted to hold over Q.
"""
from collections import Counter, defaultdict
from pathlib import Path
import importlib.util
import json

HERE = Path(__file__).resolve().parent
P = 65521


def need(ok, why):
    if not ok:
        raise ValueError(why)


def rank(rows):
    echelon = {}
    for original in rows:
        v = {i: x % P for i, x in original.items() if x % P}
        while v:
            pivot = min(v)
            if pivot not in echelon:
                inv = pow(v[pivot], -1, P)
                echelon[pivot] = {i: x * inv % P for i, x in v.items()}
                break
            c = v[pivot]
            for i, x in echelon[pivot].items():
                z = (v.get(i, 0) - c * x) % P
                if z:
                    v[i] = z
                else:
                    v.pop(i, None)
    return len(echelon)


def check_group(rows, components, target_rank):
    need(1 <= target_rank <= 9, "positive bounded group target rank")
    listed = [e for block in components for e in block]
    need(len(listed) == len(set(listed)) and set(listed) == set(rows),
         "component partition covers every assigned event exactly once")
    total_rank = rank([x["row"] for x in rows.values()])
    component_ranks = [rank([rows[e]["row"] for e in block]) for block in components]
    need(sum(component_ranks) == total_rank, "modular component spans form a direct sum")
    cases = 0
    tables = []
    worst = None
    for block in components:
        need(1 <= len(block) <= 6, "bounded complete component domain")
        table = [0]
        for mask in range(1, 1 << len(block)):
            chosen = [e for j, e in enumerate(block) if mask >> j & 1]
            lower_rank = rank([rows[e]["row"] for e in chosen])
            table.append(lower_rank)
            numerator = sum(min(1000 * target_rank, 1023 * rows[e]["rank"])
                            for e in chosen)
            margin = 1000 * target_rank * lower_rank - numerator
            need(margin >= 0, "exact normalized rank-price envelope funds every subset")
            worst = margin if worst is None else min(worst, margin)
            cases += 1
        tables.append({"events": block, "subset_ranks": table})
    return {"rank_lower_bound": total_rank, "components": len(components),
            "subset_cases": cases, "minimum_integer_margin": worst, "tables": tables}


def controls():
    # A dependent pair cannot be split into independent accounting blocks.
    pair = {1: {"row": {0: 1}, "rank": 1},
            2: {"row": {0: 2}, "rank": 1}}
    caught = False
    try:
        check_group(pair, [[1], [2]], 4)
    except ValueError as exc:
        need("direct sum" in str(exc), "partition control fails at rank check")
        caught = True
    need(caught, "false partition is rejected")
    # The same dependent pair cannot be funded at unit target rank.
    caught = False
    try:
        check_group(pair, [[1, 2]], 1)
    except ValueError as exc:
        need("envelope" in str(exc), "cost control fails at funding check")
        caught = True
    need(caught, "overpriced dependent pair is rejected")
    need(check_group(pair, [[1, 2]], 4)["rank_lower_bound"] == 1,
         "correctly funded dependent pair passes")
    independent = {1: {"row": {0: 1}, "rank": 1},
                   2: {"row": {1: 1}, "rank": 1}}
    need(check_group(independent, [[1], [2]], 1)["rank_lower_bound"] == 2,
         "full-price independent directions pass")
    return {"false_direct_sum_rejected": True, "overpriced_dependence_rejected": True,
            "funded_dependent_pair_passes": True, "independent_full_prices_pass": True}


def run():
    need(9 * 1000 ** 100 < 1023 ** 100, "uniform rational envelope for kappa<=1/100")
    spec = importlib.util.spec_from_file_location("subspace_source_modular", HERE / "modular_verify.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    projected = {}
    source_receipt = m.run(projected)
    need(len(projected) == 468, "complete assigned projection census")
    groups = defaultdict(dict)
    for event, row in projected.items():
        groups[row["group"]][event] = row
    declarations = json.loads((HERE / "GROUP-COMPONENTS.json").read_text())
    partitions = {}
    for record in declarations:
        key = (record["entrance_frame"], record["exit_frame"])
        need(key not in partitions and key in groups, "unique source-bound group certificate")
        partitions[key] = record["components"]
    receipts, sizes = [], Counter()
    for group, rows in sorted(groups.items()):
        components = partitions.get(group, [[e] for e in rows])
        targets = {r["target_rank"] for r in rows.values()}
        need(len(targets) == 1, "uniform target rank within a boundary group")
        target = next(iter(targets))
        need(all(1 <= r["rank"] <= target for r in rows.values()), "paid rank dominated by target")
        out = check_group(rows, components, target)
        out.update(entrance_frame=group[0], exit_frame=group[1], target_rank=target)
        receipts.append(out)
        sizes.update(map(len, components))
    tested = controls()
    return {"status": "PASS_INDEPENDENT_GROUP_SUBSPACE_FUNDING",
            "source_sha256": source_receipt["source_sha256"], "prime": P,
            "assigned_rows": len(projected), "charged_boundary_groups": len(groups),
            "component_size_histogram": dict(sorted(sizes.items())),
            "subset_cases": sum(x["subset_cases"] for x in receipts),
            "groups": receipts, "controls": tested,
            "kappa_interval": "0<=kappa<=1/100",
            "lifting": "Nonzero modular minors lower-bound actual characteristic-zero ranks; no modular zero is lifted.",
            "scope": "Independent scalar input subspaces in literal identical entrance/exit helper groups; fixed source operations and paid positions; no new kappa."}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
