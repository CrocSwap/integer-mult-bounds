"""Check recorded compatible slice receipts; do not re-execute their traces.

The long physical executions have their own explicitly bounded commands.
This checker authenticates their saved bytes and independently checks the
source/interface joins, completed-prefix action invoice and retained
materialized space. The uncompleted exit has no successful receipt.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
from copy import deepcopy
from hashlib import sha256
import json

from atomic_move import AtomicMove, source_boundary
from check_move import header_bits, ordinary_factory
from check_slices import corpus
from move_sources import HERE, need


def typed_natural(value):
    return type(value) is int and value >= 0


def aggregate(receipts):
    header, packets, matrix, _ = corpus()
    bad_header, bad_packets, bad_matrix, bad_index = corpus(True)
    need(header == bad_header and matrix == bad_matrix, "same source and descriptor for the late reject")
    hashes = [sha256(bytes(packet)).hexdigest() for packet in packets]
    bad_hashes = [sha256(bytes(packet)).hexdigest() for packet in bad_packets]
    header_hash = sha256(bytes(header_bits(header))).hexdigest()
    volume, header_size = len(packets[0]), len(header_bits(header))
    engine = AtomicMove(source_boundary()[0], ordinary_factory)
    counts = [1, engine.entry.port_count, engine.leaf.port_count, engine.exit.port_count]
    need(counts == [1, 1878, 349, 1878], "source-derived complete private inventory")
    limits = [0]
    for count in counts:
        limits.append(limits[-1]+count)
    ports = limits[-1]
    need(set(receipts) == {"entry", "leaf", "reject"}, "completed entrance, positive leaf and late reject only")
    for name, receipt in receipts.items():
        need(receipt["slice"] == name and receipt["records"] == 4096
             and receipt["physical_bits"] == volume
             and receipt["fixed_private_ports"] == ports, "whole admitted packet and private inventory")
        need(receipt["matrix"] == matrix and receipt["header_sha256"] == header_hash,
             "original source matrix and complete unchanged descriptor")
        need(receipt["exact_byte_boundary_checked"] is True
             and receipt["uninterrupted_run_claim"] is False, "literal slice evidence scope")
        extents = receipt["private_role_extents"]
        need(len(extents) == ports and all(typed_natural(x) and x >= 1 for x in extents)
             and extents[0] >= volume, "complete materialized stage and fixed role extents")
        family = {"entry": 1, "leaf": 2, "exit": 3, "reject": 2}[name]
        need(all(extent == 1 for i, extent in enumerate(extents)
                 if i != 0 and not limits[family] <= i < limits[family+1]),
             "each slice accesses only its own disjoint numerical cohort")
        for field in ("factor_actions", "prefix_actions", "postfix_actions", "total_actions"):
            need(typed_natural(receipt[field]), "literal action counts are natural numbers")
        need(receipt["factor_actions"] > 0 and receipt["total_actions"] ==
             receipt["factor_actions"]+receipt["prefix_actions"]+receipt["postfix_actions"],
             "complete additive action invoice")
        if name == "reject":
            need(receipt["corpus_sha256"] == bad_hashes
                 and receipt["input_packet_sha256"] == bad_hashes[1]
                 and receipt["returned_packet_sha256"] == bad_hashes[1]
                 and receipt["bad_initial_index"] == bad_index
                 and receipt["rejection"] == "inexact Gaussian halving",
                 "late leaf rejection on exact reachable postentrance bytes")
            need(receipt["prefix_actions"] == 0 and receipt["postfix_actions"] == 5*volume+7,
                 "reject slice includes actual stage retirement only")
        else:
            j = {"entry": 0, "leaf": 1, "exit": 2}[name]
            need(receipt["corpus_sha256"] == hashes
                 and receipt["input_packet_sha256"] == hashes[j]
                 and receipt["returned_packet_sha256"] == hashes[j+1]
                 and receipt["rejection"] is None and receipt["bad_initial_index"] is None,
                 "complete original-source byte-boundary chain")
            need(receipt["prefix_actions"] == (8*volume+14 if name == "entry" else 0)
                 and receipt["postfix_actions"] == (14*volume+21 if name == "exit" else 0),
                 "literal transfer/commit/retire occurrence invoice")
    success = [receipts[name] for name in ("entry", "leaf")]
    maxima = [max(receipt["private_role_extents"][i] for receipt in success) for i in range(ports)]
    factor_actions = sum(receipt["factor_actions"] for receipt in success)
    actions = sum(receipt["total_actions"] for receipt in success)
    need(actions == factor_actions+8*volume+14, "completed entrance/leaf prefix and transfer action invoice")
    origins = sum(3+i % 5 for i in range(ports))
    cohort_materialized = {name: sum(maxima[limits[j]:limits[j+1]])
                           for j, name in enumerate(("stage", "entrance", "leaf", "exit"))}
    largest_slice = max(sum(receipt["private_role_extents"]) for receipt in success)
    need(sum(maxima) > largest_slice, "retained older cohorts are not replaced by maximum active space")
    initial_regions = origins+ports + 9+volume+1 + 11+header_size+1
    result = dict(
        schema_version=1, evidence="partial returned-boundary sliced execution: entrance and leaf only",
        records=4096, physical_bits=volume, header_bits=header_size,
        source_matrix=matrix, packet_sha256=hashes, header_sha256=header_hash,
        completed_positive_factors=["entry", "leaf"], missing_positive_factors=["exit"],
        factor_actions={name: receipts[name]["factor_actions"] for name in ("entry", "leaf")},
        executed_administrative_actions=8*volume+14, total_completed_prefix_actions=actions,
        complete_three_factor_sliced_witness=False,
        fixed_private_ports=ports, cohort_materialized_body_cells=cohort_materialized,
        partial_prefix_materialized_private_body_cells=sum(maxima),
        maximum_materialized_private_body_cells_in_one_slice=largest_slice,
        private_origin_and_ancestor_cells=origins,
        partial_prefix_materialized_private_cells_including_origins=sum(maxima)+origins,
        partial_prefix_materialized_all_cells_including_origins=sum(maxima)+origins+9+volume+11+header_size,
        conservative_prefix_all_visited_cells_upper_bound=initial_regions+actions,
        visited_bound_derivation="initial private/public/header regions plus one cell per literal action; moves into implicit blanks are included",
        materialized_extents_are_not_measured_visited_highwater=True,
        rolewise_materialized_body_maxima=maxima,
        late_leaf_rejection=dict(factor_actions=receipts["reject"]["factor_actions"],
                                 retirement_actions=receipts["reject"]["postfix_actions"],
                                 total_actions=receipts["reject"]["total_actions"],
                                 materialized_private_cells_including_origins=
                                     sum(receipts["reject"]["private_role_extents"])+origins,
                                 conservative_all_visited_cells_upper_bound=
                                     initial_regions+volume-1+receipts["reject"]["total_actions"],
                                 original_bad_index=bad_index,
                                 reachable_packet_sha256=bad_hashes[1],
                                 full_failed_move_execution_claim=False),
        complete_uninterrupted_process_claim=False,
        physical_traces_reexecuted_by_this_checker=False, no_new_kappa=True)
    return result


def load():
    manifest = json.loads((HERE/"receipts/MANIFEST.json").read_text())
    rows = {}
    for name in ("entry", "leaf", "reject"):
        path = HERE/"receipts"/(name+".json")
        data = path.read_bytes()
        need(sha256(data).hexdigest() == manifest["sha256"][name+".json"], "saved physical receipt byte integrity")
        rows[name] = json.loads(data)
    return rows


def controls(receipts):
    cases = []
    for name, mutate in (
        ("changed_boundary", lambda x: x["leaf"].__setitem__("input_packet_sha256", "0"*64)),
        ("changed_header", lambda x: x["leaf"].__setitem__("header_sha256", "0"*64)),
        ("dropped_action", lambda x: x["entry"].__setitem__("total_actions", x["entry"]["total_actions"]-1)),
        ("missing_stage", lambda x: x["leaf"]["private_role_extents"].__setitem__(0, 1)),
        ("discarded_return_scope", lambda x: x["leaf"].__setitem__("uninterrupted_run_claim", True)),
    ):
        altered = deepcopy(receipts)
        mutate(altered)
        try:
            aggregate(altered)
        except ValueError:
            cases.append(name)
        else:
            raise ValueError("altered slice receipt accepted: "+name)
    return cases


def main():
    parser = ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    receipts = load()
    result = aggregate(receipts)
    result["rejected_receipt_mutations"] = controls(receipts)
    target = HERE/"SLICED-RESULT.json"
    if args.emit:
        target.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    else:
        need(result == json.loads(target.read_text()), "complete recorded-slice consistency receipt")
    print("PASS_CURRENT_CODED_ATOMIC_MOVE_RECORDED_SLICES", json.dumps(dict(
        records=result["records"], completed_prefix_actions=result["total_completed_prefix_actions"],
        fixed_private_ports=result["fixed_private_ports"],
        physical_traces_reexecuted=False), sort_keys=True))


if __name__ == "__main__":
    main()
