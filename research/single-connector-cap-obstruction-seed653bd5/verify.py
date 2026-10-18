"""Recheck the one-connector frame obstruction from pinned block certificates."""

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERT_PATH = ROOT / "research/complex-block-rank-optimum/CERTIFICATE.json"
CERT_SHA256 = "d3ada9ac84a74f72ce9364dd47ee2ab9f02d1a6513df135e81dad11d0e6c6958"


def basis(values):
    pivots = {}
    for value in values:
        value = int(value)
        if value < 0 or value >= 512:
            raise ValueError("frame vector is outside F2^9")
        while value:
            pivot = value.bit_length()
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def rank(values):
    return len(basis(values))


def contained(subspace, cap):
    return rank(tuple(subspace) + tuple(cap)) == rank(cap)


def valid_cap(cap):
    return rank(cap) == 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_block(block):
    inputs = block["input_frames"]
    caps = block["target_caps"]
    common = block["common_frame"]
    R, Q = block["R"], block["Q"]
    require(len(inputs) == 8 and len(caps) == 4, "unexpected block dimensions")
    require(len(R) == 4 and all(len(row) == 4 for row in R), "bad helper matrix")
    require(len(Q) == 4 and all(len(row) == 8 for row in Q), "bad external matrix")
    require(all(contained(common, frame) for frame in inputs), "input misses common frame")

    for column in range(8):
        support = [row for row in range(4) if Q[row][column] != "0"]
        require(len(support) == 2 and support[0] != support[1],
                "external input does not have two distinct output incidences")

    source_join = basis(vector for frame in inputs for vector in frame)
    source_rank = len(source_join)
    require(8 <= source_rank <= 9, "unexpected external-input join rank")
    for cap in caps:
        require(valid_cap(cap), "target cap does not have rank eight")
        require(rank(source_join + tuple(cap)) == 9,
                "source join is compatible with a retained target cap")
    return source_rank


def main():
    raw = CERT_PATH.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == CERT_SHA256,
            "pinned block certificate hash mismatch")
    cert = json.loads(raw)
    sources = cert["sources"]
    require(len(sources) == 3, "expected selected and two comparison source sets")
    require(sources[0]["file"] == "inputs/selected.json.gz",
            "selected-word source is not first in certificate")

    counts = {8: 0, 9: 0}
    selected_pairs = all_pairs = 0
    blocks_seen = 0
    for source_index, source in enumerate(sources):
        blocks = source["blocks"]
        require(len(blocks) == 12, "expected twelve blocks per pinned source word")
        for block in blocks:
            source_rank = check_block(block)
            counts[source_rank] += 1
            blocks_seen += 1
            all_pairs += 4
            if source_index == 0:
                selected_pairs += 4
    require(blocks_seen == 36 and selected_pairs == 48 and all_pairs == 144,
            "coverage count mismatch")

    # Positive control: a cap that contains the same source join is accepted.
    control_join = basis((1, 2, 4))
    require(contained(control_join, control_join),
            "positive containment control was rejected")

    # Negative control: deleting one independent vector from a real cap must
    # fail the retained rank-eight endpoint check.
    selected_cap = sources[0]["blocks"][0]["target_caps"][0]
    reduced_cap = basis(selected_cap)[:-1]
    require(rank(reduced_cap) == 7, "cap mutation did not reduce the rank")
    try:
        require(valid_cap(reduced_cap), "mutated cap should be rejected")
    except ValueError:
        cap_mutation_rejected = True
    else:
        raise ValueError("rank-seven target-cap mutation was accepted")

    print(
        "PASS_SINGLE_CONNECTOR_CAP_OBSTRUCTION "
        f"selected_blocks=12 selected_pairs={selected_pairs} "
        f"all_blocks={blocks_seen} all_pairs={all_pairs} "
        f"rank8_joins={counts[8]} rank9_joins={counts[9]} "
        "positive_control=1 cap_mutation_rejected=" + str(int(cap_mutation_rejected))
    )


if __name__ == "__main__":
    main()
