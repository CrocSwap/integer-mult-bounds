"""Behavioral source and hypothesis controls. Apache-2.0."""

import copy
import json
import os
import tempfile
from pathlib import Path

import verify as v


def rejected(call, fragment):
    try:
        call()
    except ValueError as error:
        v.require(fragment in str(error), "wrong rejecting contract")
    else:
        raise ValueError("control accepted")


def source_controls():
    pins = json.loads(v.read_bytes(v.PACKAGE / "SOURCES.json"))
    v.authenticate()
    mutants = []
    missing = copy.deepcopy(pins)
    missing["files"].pop()
    mutants.append((missing, "row count"))
    extra = copy.deepcopy(pins)
    extra["files"].append(copy.deepcopy(extra["files"][0]))
    mutants.append((extra, "row count"))
    relabeled = copy.deepcopy(pins)
    next(row for row in relabeled["files"] if row["path"] == v.GEOMETRY)["usage"] = (
        "provenance"
    )
    mutants.append((relabeled, "source usage"))
    duplicate = copy.deepcopy(pins)
    duplicate["files"][0] = copy.deepcopy(duplicate["files"][1])
    mutants.append((duplicate, "inventory"))
    malformed = copy.deepcopy(pins)
    malformed["files"][0]["sha256"] = []
    mutants.append((malformed, "source digest"))
    for mutant, message in mutants:
        rejected(lambda mutant=mutant: v.authenticate(manifest=mutant), message)
    with tempfile.TemporaryDirectory(
        prefix="a2-joint20-control-", dir=os.environ.get("IMB_RUN_CACHE")
    ) as temporary:
        root = Path(temporary)
        target = root / v.GEOMETRY
        target.parent.mkdir(parents=True)
        target.write_bytes(v.authenticate() + b"\n# changed input\n")
        rejected(lambda: v.authenticate(root), "geometry hash")
        target.unlink()
        rejected(lambda: v.authenticate(root), "missing or linked")
    return 7


def hypothesis_controls():
    # Same nondegenerate polar form, opposite Gauss sign, twelve in affine4.
    minus = tuple(
        sum(((x >> i) & 1) * ((x >> (i + 1)) & 1) for i in (0, 2, 4)) % 2
        ^ ((x >> 4) & 1)
        ^ ((x >> 5) & 1)
        for x in range(64)
    )
    polar = tuple(
        sum(
            (minus[(1 << i) ^ (1 << j)] ^ minus[1 << i] ^ minus[1 << j] ^ minus[0]) << j
            for j in range(6)
        )
        for i in range(6)
    )
    v.require(len(v.basis(polar)) == 6, "opposite-sign nondegenerate control")
    L = [x for x in range(64) if not (x >> 1 & 1 or x >> 3 & 1)]
    v.require(
        64 - 2 * sum(minus) == -8 and sum(minus[x] for x in L) == 12,
        "positive sign is necessary",
    )
    g = v.geometry()
    _, full, q = v.model(g)
    result = json.loads(v.read_bytes(v.PACKAGE / "RESULT.json"))
    A = tuple(result["canonical_fiber_labels"])
    v.fiber_signature(A, full, q)
    rejected(lambda: v.fiber_signature(A[:-1], full, q), "large fiber input")
    altered = list(q)
    H = [x >> 1 for x in v.span(v.basis(A)) if x & 1]
    altered[H[0]] ^= 1
    rejected(lambda: v.fiber_signature(A, full, altered), "Gauss sum")
    witness = result["attaining_support_labels"]
    v.require(
        len(witness) == 10 and set(witness) <= set(A) and len(v.basis(witness)) == 5,
        "nineteen is false",
    )
    W = v.span(v.basis(witness))
    v.require(
        len(set(full).intersection(W)) + len(set(A).intersection(W)) == 20,
        "literal sharpness",
    )
    rejected(lambda: v.span((1, 1)), "independent basis")
    rejected(lambda: v.basis(tuple(range(513))), "binary input")
    return 6


def main():
    source_count = source_controls()
    hypothesis_count = hypothesis_controls()
    print(
        f"PASS_E8_A2_JOINT20_CONTROLS source={source_count} "
        f"hypothesis={hypothesis_count}"
    )


if __name__ == "__main__":
    main()
