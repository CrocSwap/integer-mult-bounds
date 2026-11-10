"""Check saved completed child evidence without pretending to replay rank eight.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from copy import deepcopy
from hashlib import sha256
import json
from all_leaf_sources import HERE, need
from check_child import fixture
from check_view import encode
from source_catalog import catalog


def validate(item):
    rank, mode = item["rank"], item["mode"]
    need(type(rank) is int and rank in (2, 8)
         and mode in ("success", "cutoff", "parity"), "documented complete child receipt")
    header, initial, expected = fixture(mode, rank)
    pc = next(pc for pc, triple in catalog()[1].items() if triple[1].rank == rank)
    event = catalog()[1][pc][1]
    need(item["source_event"] == pc and item["owner"] == event.fields[0]
         and item["parent_f"] == 1 and item["child_f"] == rank
         and item["original_cutoff"] == header["cutoff"], "actual source and scaled leaf width")
    need(item["records"] == 4096 and item["physical_bits"] == len(initial) == 73728
         and item["header_bits"] == len(encode(header)), "complete source-compatible geometry")
    endpoint = expected if mode == "success" else initial
    need(item["endpoint_sha256"] == sha256(bytes(endpoint)).hexdigest(), "independent complete endpoint hash")
    need(item["rejection"] == {"success":None, "cutoff":"elementary PAID branch f <= cutoff",
                                "parity":"inexact Gaussian halving"}[mode], "exact named result")
    extents = item["private_materialized_extents"]
    need(item["private_ports"] == len(extents) == 388 and
         all(type(n) is int and n >= 1 for n in extents), "complete rolewise materialized receipt")
    need(item["ordinary_invocations"] == 0 and not item["complete_selected_move_claim"]
         and not item.get("visited_extent_measured", False), "correct evidence and space scope")
    actions = item["physical_actions"]
    need(type(actions) is int and actions > 0, "literal positive physical action receipt")
    # Initial charged regions include all private origin/frontier prefixes,
    # field/header prefixes and the two complete input bodies/frontiers.
    initial_regions = sum((3+j % 5)+1 for j in range(388)) + (9+1)+(11+1)
    initial_regions += len(initial)+len(encode(header))
    conservative_visited = initial_regions+actions
    need(sum(extents)+len(initial)+len(encode(header)) <= conservative_visited,
         "materialized body lies below the conservative visited ceiling")
    return dict(rank=rank, mode=mode, actions=actions,
                private_materialized_body=sum(extents),
                conservative_all_visited_cells=conservative_visited,
                rank8_reexecuted_by_this_check=False)


def check():
    cases = []
    for name in ("rank2-success", "rank2-cutoff", "rank2-parity", "rank8-success"):
        value = json.loads((HERE/"receipts"/(name+".json")).read_text())
        cases.append(validate(value))
    wrong = json.loads((HERE/"receipts/rank8-success.json").read_text())
    variants = []
    for key, replacement in (("endpoint_sha256", "0"*64), ("child_f", 1),
                             ("ordinary_invocations", 1), ("visited_extent_measured", True)):
        variant = deepcopy(wrong); variant[key] = replacement; variants.append(variant)
    for variant in variants:
        try:
            validate(variant)
        except ValueError:
            pass
        else:
            raise ValueError("mutated child evidence accepted")
    return dict(cases=cases, receipt_mutants_rejected=len(variants),
                evidence_kind="saved completed child receipts; rank-eight is not rerun by this checker")
