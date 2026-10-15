#!/usr/bin/env python3
"""Check the reviewed QQ16 witness consequence and the extra-query profile envelope."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from fractions import Fraction as Q
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
WITNESS_SHA256 = "e35e5868a1322e406191079c0675975b139692ba50b1e2e5fb8a40b6480519f4"
WITNESS_PROOF_SHA256 = "52f2ee565320f05282c637aa79eee100606c24240b1b5866f0c8d62e7913c9fc"
OBSERVATION_REVIEW_SHA256 = "9a06ff40830ef80d3566fce77c78639cb64d519d487a0a7f57d543c3146e2c49"
QQ16_INVOICE_SHA256 = "b91eb8599c403db55c889bb225a1cd93f46fdb83eb339f101d18843d52b1c920"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_pinned_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    require(digest(path) == CEILING_SHA256, "pinned selected ceiling implementation changed")
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    require(spec is not None and spec.loader is not None, "cannot load pinned ceiling")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    selected_path = ROOT / "certificates/selected-result.json"
    witness_path = ROOT / "research/joint-query/evidence/QQ16-SELECTED-WITNESS.json"
    proof_path = ROOT / "research/joint-query/evidence/QQ16-SELECTED-WITNESS.md"
    review_path = ROOT / "research/joint-query/evidence/QQ16-RATIONAL-OBSERVATION-REVIEW.md"
    invoice_path = ROOT / "research/joint-query/evidence/CONSERVED-QQ16.json"
    require(digest(selected_path) == SELECTED_SHA256, "selected record hash changed")
    require(digest(witness_path) == WITNESS_SHA256, "pinned witness receipt changed")
    require(digest(proof_path) == WITNESS_PROOF_SHA256, "pinned witness proof changed")
    require(digest(review_path) == OBSERVATION_REVIEW_SHA256, "pinned observation review changed")
    require(digest(invoice_path) == QQ16_INVOICE_SHA256, "pinned QQ16 invoice changed")

    witness = json.loads(witness_path.read_text())
    require(witness["ordinary_gram"] == 48, "witness Gram scalar changed")
    require(witness["identity_coefficients"] == ["2112"] * 8,
            "reviewed B2 response is not eight independent 2112 coordinates")
    require(witness["relative_routes_checked"] == 96,
            "pinned witness route count changed")

    # Apply the reviewed exact identities B1 B1* = B2 B2* = 48 I and
    # [B2 B1* B1 B2*]_identity = 192 I to each of the eight basis directions.
    gram = 48
    cross_identity_coefficient = 192
    query_diagonal = gram * gram - cross_identity_coefficient
    require(query_diagonal == 2112, "B2 h coefficient arithmetic changed")
    query_outputs = []
    old_query_outputs = []
    for k in range(8):
        e = tuple(int(i == k) for i in range(8))
        query_outputs.append(tuple(query_diagonal * x for x in e))
        # The old B1 response vanishes because B1 B1* = 48 I.
        old_query_outputs.append(tuple(0 for _ in e))
    require(query_outputs == [tuple(2112 * int(i == k) for i in range(8)) for k in range(8)],
            "extra B2 observation failed to separate a witness direction")
    require(len(set(query_outputs)) == 8 and all(old == (0,) * 8 for old in old_query_outputs),
            "old/new query separation control failed")
    require(gram * gram - (cross_identity_coefficient + 1) == 2111,
            "cross-coefficient mutation control failed")
    rotated_outputs = [output[1:] + output[:1] for output in query_outputs]
    require(rotated_outputs != query_outputs,
            "output-coordinate permutation control failed")
    require(len(set(rotated_outputs)) == 8,
            "output-coordinate permutation unexpectedly merged witnesses")

    ceiling = import_pinned_ceiling()
    selected = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
    selected_lo, selected_hi = ceiling.ceiling(selected, 73, 896, 9, 64, grid=Q(1, 10**12))
    require(selected_lo == Q(1690054109, 10**12)
            and selected_hi == Q(169005411, 10**11), "selected ceiling bracket changed")

    invoice = json.loads(invoice_path.read_text())
    b_profile = {int(k): int(v) for k, v in invoice["invoices"]["B"]["native_profile"].items()}
    require(b_profile == {1: 2436, 2: 418, 3: 432, 4: 142, 5: 82},
            "merged QQ16 B profile changed")
    require(sum(r * n for r, n in b_profile.items()) == 5546,
            "merged QQ16 B rank mass changed")

    rank8 = b_profile.copy()
    rank8[8] = rank8.get(8, 0) + 1
    rank8_one_extra = rank8.copy()
    rank8_one_extra[1] += 1
    rank8_two_extra = rank8.copy()
    rank8_two_extra[1] += 2
    rank8_three_extra = rank8.copy()
    rank8_three_extra[1] += 3
    eight_rank1 = b_profile.copy()
    eight_rank1[1] += 8

    profiles = {"B": b_profile, "B+rank8": rank8, "B+rank8+1rank1": rank8_one_extra,
                "B+rank8+2rank1": rank8_two_extra, "B+rank8+3rank1": rank8_three_extra,
                "B+8rank1": eight_rank1}
    brackets = {name: ceiling.ceiling(p, 73, 896, 9, 64, grid=Q(1, 10**12))
                for name, p in profiles.items()}
    require(brackets["B+rank8"] == (Q(16907931, 10**10), Q(1690793101, 10**12)),
            "rank-8 output bracket changed")
    require(brackets["B+8rank1"][1] == Q(422363351, 250000000000),
            "eight rank-one output bracket changed")
    require(brackets["B+rank8+2rank1"][0] == Q(1690160547, 10**12),
            "two-unit overhead bracket changed")
    require(brackets["B+rank8+3rank1"][1] == Q(1689844449, 10**12),
            "three-unit overhead bracket changed")
    require(brackets["B+rank8"][0] > selected_hi,
            "ideal rank-8 output envelope no longer clears selected ceiling")
    require(brackets["B+rank8+2rank1"][0] > selected_hi,
            "two-unit residual budget no longer clears selected ceiling")
    require(brackets["B+rank8+3rank1"][1] < selected_lo,
            "three-unit overhead did not fall below selected ceiling")
    require(brackets["B+8rank1"][1] < selected_lo,
            "eight separate output tariffs did not fail the selected ceiling")

    print("PASS_QQ16_EXTRA_B2_OBSERVATION_SCREEN")
    print("witness_directions=8 old_B1_response=0 new_B2_identity_coefficient=2112")
    print("query_shape=96_ordinary_inputs_to_8_independent_outputs source_mutation=0")
    print(f"selected_ceiling=[{selected_lo},{selected_hi}]")
    for name in profiles:
        lo, hi = brackets[name]
        mass = ceiling.model(profiles[name], 73, 896, 9, 64)["local_mass"]
        gain = float((hi / selected_hi - 1) * 100)
        print(f"{name} mass={mass} ceiling=[{lo},{hi}] upper_gain_pct={gain:.9f}")
    print("scope=reviewed_witness_subspace_only; native_wrapper_and_full_controller=not_established")


if __name__ == "__main__":
    main()
