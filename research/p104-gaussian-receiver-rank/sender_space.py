#!/usr/bin/env python3
"""Source-bound sender-space screen for the 14 deficient Gaussian receivers.

Every quotient-rank lower bound is accompanied by its actual nonzero modular
minor.  The fixed stock, sender-port and linear-demand assumptions are stated
in PROOF.md.  ``--corrupt-minor`` is an expected-failure negative control.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
import numpy as np

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("gaussian_receiver_baseline", HERE / "verify.py")
base = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(base)
P = 65521

# Each pair is (exact rational demand rank, best surviving capacity bound).
EXPECTED = {
    243: (28, 22), 394: (5, 4), 477: (12, 7), 517: (13, 8),
    518: (12, 7), 529: (7, 6), 531: (4, 1), 541: (7, 6),
    543: (6, 5), 591: (5, 1), 595: (7, 6), 1091: (23, 16),
}
UNRESOLVED = {470: (5, 5), 599: (8, 8)}
UNRESTRICTED = {477, 517, 518, 531, 543, 591, 595, 1091}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def select_minor(matrix):
    """Find original independent rows and pivot columns and verify their minor."""
    pivots = {}
    original_rows = []
    for i, row in enumerate(matrix):
        if base.insert(pivots, row, P):
            original_rows.append(i)
    columns = list(pivots)
    rank = len(columns)
    check(rank == base.rank_mod(matrix, P), "independent rank algorithms disagree")
    minor = matrix[np.ix_(original_rows, columns)]
    check(minor.shape == (rank, rank), "quotient minor is not square")
    return original_rows, columns, minor


def checked_determinant(minor):
    determinant = base.determinant_mod(minor, P)
    check(determinant != 0, "nonzero quotient minor is corrupted or singular")
    return determinant


def compute(corrupt_minor=False):
    check(np.__version__ == "1.26.4", "replay requires numpy==1.26.4")
    graph = base.read_graph()
    raw_witness = (HERE / "null-sources.json").read_bytes()
    check(base.sha(raw_witness) == base.WITNESS_SHA, "rational witness hash mismatch")
    witness = json.loads(raw_witness)
    data = base.evaluate(graph, P)
    groups, local_total, deficient = base.local_ranks(data, witness)
    check(data["n"] == 1291 and len(data["moves"]) == 5674 and
          len(data["received"]) == 977 and local_total == 5660 and len(deficient) == 14,
          "baseline receiver census differs")
    entries = {entry["chart"]: entry for entry in witness["charts"]}
    check(set(entries) == set(EXPECTED) | set(UNRESOLVED), "deficient receiver set differs")
    results = []
    control_seen = False
    for receiver in sorted(entries):
        incoming = groups[receiver]["incoming"]
        demand = groups[receiver]["demand"]
        dimension = len(incoming) - 1
        entry = entries[receiver]
        check(entry["rank_Q"] == dimension, "rational local demand rank differs")
        null = {term["node"]: base.rational(term["coeff"]) for term in entry["support"]}
        check(null and set(null) <= set(incoming), "invalid rational null support")
        pivot = next(node for node in incoming if null.get(node, 0))
        pivot_coefficient = null[pivot]
        demand_basis_nodes = [node for node in incoming if node != pivot]
        # Exact null and rank were already checked in base.local_ranks. These
        # vectors span the fixed demand space modulo the free receiver inputs.
        h = []
        for node in demand_basis_nodes:
            ratio = null.get(node, Fraction(0)) / pivot_coefficient
            scale = base.residue(str(ratio), P)
            h.append((data["vectors"][node] - scale * data["vectors"][pivot]) % P)
        free_roles = [i for i, chart in enumerate(graph["initial"]) if chart == receiver]
        free = [data["vectors"][~i] for i in free_roles]
        W = np.stack(h + free)
        check(base.rank_mod(W, P) == len(W), "demand and free-input basis is dependent")
        source_groups = defaultdict(list)
        for node in incoming:
            source_groups[data["moves"][node][0]].append(node)
        upper, quotient, minors = {}, {}, {}
        for source in sorted(source_groups):
            # The elimination map has kernel equal to the entire original stock
            # at source. Baseline evaluation proved every such stock independent.
            projected = W.copy()
            stock = data["basis"][source]
            check(len(stock) == len(data["owners"][source]), "source stock is dependent")
            for column, row in stock.items():
                coefficients = projected[:, column].copy()
                if np.any(coefficients):
                    projected = (projected - coefficients[:, None] * row) % P
            row_indices, columns, minor = select_minor(projected)
            if receiver == 477 and source == 288:
                check(len(minor) > 0, "corruption control has no minor")
                damaged = minor.copy()
                damaged[0, :] = 0
                if corrupt_minor:
                    checked_determinant(damaged)  # deliberately fails closed
                try:
                    checked_determinant(damaged)
                except ValueError:
                    control_seen = True
                else:
                    raise ValueError("corrupted quotient minor was accepted")
            det = checked_determinant(minor)
            rank = len(row_indices)
            quotient[source] = rank
            upper[source] = len(W) - rank
            check(0 <= upper[source] <= len(data["owners"][source]),
                  "intersection dimension bound is invalid")
            minors[str(source)] = {
                "projected_W_row_indices": row_indices,
                "input_coordinate_columns": columns,
                "determinant_mod_p": det,
            }
        best = max(
            sum(min(len(nodes) - (source == removed), upper[source])
                for source, nodes in source_groups.items())
            for removed in source_groups
        )
        excluded = best < dimension
        uncapped = sum(upper.values())
        unrestricted = uncapped < dimension
        check(unrestricted == (receiver in UNRESTRICTED),
              "unrestricted existing-sender capacity summary differs")
        wanted = EXPECTED.get(receiver, UNRESOLVED.get(receiver))
        check((dimension, best) == wanted and excluded == (receiver in EXPECTED),
              "fixed-port capacity summary differs")
        record = {
            "receiver": receiver,
            "demand_rank_Q": dimension,
            "free_input_owners": len(free_roles),
            "free_input_roles": free_roles,
            "arrival_nodes": incoming,
            "demand_nodes": demand,
            "demand_basis_null_pivot_arrival": pivot,
            "demand_basis_other_arrivals": demand_basis_nodes,
            "source_stock_sizes": {str(s): len(data["owners"][s]) for s in sorted(source_groups)},
            "source_port_counts": {str(s): len(source_groups[s]) for s in sorted(source_groups)},
            "intersection_dim_Q_upper": {str(s): upper[s] for s in sorted(source_groups)},
            "quotient_rank_mod_p": {str(s): quotient[s] for s in sorted(source_groups)},
            "quotient_nonzero_minors": minors,
            "best_capacity_upper_after_one_port_removed": best,
            "uncapped_sender_intersection_upper": uncapped,
            "proven_with_unrestricted_original_sender_allocation": unrestricted,
            "proven_excluded": excluded,
        }
        results.append(record)
    check(control_seen, "corrupted-minor control did not run")
    return {
        "schema_version": 1,
        "predecessor_certificate_head": "327e55157afb3a7a13e7ecb2b2cef20097d7feac",
        "graph_sha256": base.WORD_SHA,
        "prime": P,
        "independent_public_inputs": data["n"],
        "certified_receivers": sorted(EXPECTED),
        "unrestricted_original_sender_allocation_receivers": sorted(UNRESTRICTED),
        "unresolved_receivers": sorted(UNRESOLVED),
        "receiver_source_pairs": sum(len(x["source_port_counts"]) for x in results),
        "receivers": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", action="store_true", help="emit the recomputed complete receipt")
    parser.add_argument("--corrupt-minor", action="store_true", help="expected-failure minor corruption control")
    args = parser.parse_args()
    result = compute(corrupt_minor=args.corrupt_minor)
    if args.emit_result:
        print(json.dumps(result, indent=2))
    else:
        expected = json.loads((HERE / "sender-space-result.json").read_bytes())
        check(result == expected, "sender-space receipt or source-bound minors differ")
        print("PASS_CORRUPTED_QUOTIENT_MINOR_REJECTED chart=477 source=288")
        print("PASS_SENDER_SPACE certified=12 unrestricted_allocation=8 unresolved=2 receiver_source_pairs=83")


if __name__ == "__main__":
    main()
