"""Complete finite source-family certificate, with independently checked phase.

The new physical claim is the multi-axis leaf interface, not this census.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from argparse import ArgumentParser
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json

from all_leaf_sources import HERE, need
from clifford_certificate import certify, generators, lowered_circuit, zero_column
from source_catalog import bind_paid, catalog, chart


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def controls():
    word, entries, _pairs, _report = catalog()
    event = next(triple[1] for triple in entries.values() if triple[1].rank == 2)
    raw = word["program"][event.token[1]]
    original, record = chart(raw[2], raw[3])
    original_generators, original_zero = generators(original.circuit), zero_column(original.circuit)
    wrong_phase = deepcopy(record)
    wrong_phase["right"]["phase"] = (wrong_phase["right"]["phase"]+1) % 4
    need(generators(lowered_circuit(wrong_phase)) == original_generators
         and zero_column(lowered_circuit(wrong_phase)) != original_zero,
         "generator-only check misses absolute phase")
    wrong_input_z = deepcopy(record)
    coefficients = list(wrong_input_z["right"]["linear_Z4"])
    coefficients[0] = (coefficients[0]+2) % 4
    wrong_input_z["right"]["linear_Z4"] = coefficients
    need(zero_column(lowered_circuit(wrong_input_z)) == original_zero
         and generators(lowered_circuit(wrong_input_z)) != original_generators,
         "single-column-only check misses an input Z")
    wrong_rank = deepcopy(record); wrong_rank["rank"] = 1
    for modified in (wrong_phase, wrong_input_z, wrong_rank):
        try:
            certify(original, modified)
        except ValueError:
            pass
        else:
            raise ValueError("incorrect source factorization accepted")
    rank_one = next(triple[1] for triple in entries.values() if triple[1].rank == 1)
    int_boolean_record = tuple(int(x) if type(x) is bool else x for x in event.token[2])
    variants = (
        replace(event, rank=True), replace(event, rank=1),
        replace(rank_one, rank=True),
        replace(event, token=("local", event.token[1], int_boolean_record)),
        replace(event, fields=(event.fields[0]+1,)),
        replace(event, token=("caller-local", 0, 0, event.token)),
        replace(event, token=("local", True, event.token[2])),
        replace(event, op="SERVICE"))
    for wrong in variants:
        try:
            bind_paid(wrong)
        except ValueError:
            pass
        else:
            raise ValueError("wrong typed source child accepted")
    return dict(source_factorization_mutants=3, typed_source_rejections=len(variants),
                boolean_integer_alias_rejections=2,
                generator_only_insufficient=True, single_column_only_insufficient=True)


def check(progress=None):
    word, entries, pairs, report = catalog()
    certificates = []
    ranks = Counter()
    for count, (start, stop) in enumerate(pairs, 1):
        original, record = chart(start, stop)
        paulis, column = certify(original, record)
        ranks[record["rank"]] += 1
        certificates.append([start, stop, record["rank"], digest(record), digest(paulis), digest(column)])
        if progress is not None and (count % 128 == 0 or count == len(pairs)):
            progress.write_text(json.dumps(dict(complete=count, total=len(pairs),
                                               unverified_remaining=len(pairs)-count))+"\n")
    # Every raw occurrence was checked against its authentic neighbouring
    # services by catalog(); these are all distinct directed source charts.
    expected = {1:1840, 2:379, 3:494, 4:99, 5:57, 6:10, 7:6, 8:1}
    need(dict(ranks) == expected and sum(ranks.values()) == 2886, "complete selected chart/rank coverage")
    return dict(schema_version=1, source=report, chart_rank_counts=dict(sorted(ranks.items())),
                exact_pauli_images=18*len(pairs), exact_column_positions=512*len(pairs),
                source_certificates=certificates, controls=controls(),
                dense_512_by_512_replays_claim=False,
                certificate_theorem="equal unitary Pauli conjugations plus one equal nonzero column imply identical operator",
                no_new_kappa=True)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--progress", type=Path)
    args = parser.parse_args()
    result = check(args.progress)
    target = HERE/"CATALOG-RESULT.json"
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    if args.emit:
        target.write_text(json.dumps(result, sort_keys=True, indent=2)+"\n")
    else:
        need(canonical == json.dumps(json.loads(target.read_text()), sort_keys=True, separators=(",", ":")),
             "exact complete source-family certificate receipt")
    print("PASS_CURRENT_CODED_ALL_SOURCE_CLIFFORD", json.dumps(dict(
        moves=result["source"]["raw_moves"], charts=len(result["source_certificates"]),
        pauli_images=result["exact_pauli_images"], absolute_phase=True), sort_keys=True))
