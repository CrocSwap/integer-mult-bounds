#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact favorable ceiling screen for rank-two shared-line block fusion."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import tarfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBERS = {
    "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz":
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz":
        "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
}
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
BASE_CEILING = (
    Fraction(52814190909, 31250000000000),
    Fraction(1690054109089, 10**15),
)
FULL_CEILING = (
    Fraction(1768394682583, 10**15),
    Fraction(221049335323, 125000000000000),
)


def need(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_member(archive: tarfile.TarFile, name: str) -> bytes:
    raw = archive.extractfile(name).read()
    need(sha256(raw) == MEMBERS[name], f"archive member digest: {name}")
    return gzip.decompress(raw)


def fused(profile: dict[int, int], groups: int) -> dict[int, int]:
    need(isinstance(groups, int) and 0 <= groups <= profile[2] // 2,
         "fusion count must be in 0..floor(n2/2)")
    out = dict(profile)
    out[2] -= 2 * groups
    out[3] += groups
    return out


def main() -> None:
    need(sha256(ARCHIVE.read_bytes()) == ARCHIVE_SHA256, "selected replay archive digest")
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        word = json.loads(load_member(
            archive,
            "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz",
        ))
        programs = json.loads(load_member(
            archive,
            "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz",
        ))

    profile = {int(rank): int(count) for rank, count in word["local_profile"].items()}
    need(profile == BASE_PROFILE, "pinned canonical local profile")
    for direction in ("forward", "backward"):
        recounted: dict[int, int] = {}
        for event in programs[direction]:
            if event[0] == "climb":
                rank = int(event[5])
            elif event[0] == "center":
                rank = 8
            else:
                continue
            recounted[rank] = recounted.get(rank, 0) + 1
        need(recounted == BASE_PROFILE, f"{direction} source-event rank census")

    model_path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_ceiling", model_path)
    need(spec is not None and spec.loader is not None, "ceiling module load")
    ceiling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling)

    kwargs = dict(m=73, families=896, stages=9, centre=64)
    base_model = ceiling.model(profile, **kwargs)
    need(base_model["R"] == 51, "selected outer rank cap")
    need(base_model["total_mass"] == 7232, "coverage mass")
    need(base_model["local_mass"] == 5586 and base_model["idle_mass"] == 1646,
         "selected mass split")

    baseline = ceiling.ceiling(profile, **kwargs)
    need(baseline == BASE_CEILING, "exact selected ceiling bracket")
    no_fusion = fused(profile, 0)
    need(no_fusion == profile, "zero-fusion control")
    maximum_groups = profile[2] // 2
    need(maximum_groups == 209, "maximum pair count")
    best = fused(profile, maximum_groups)
    need(best == {1: 2412, 2: 0, 3: 641, 4: 142, 5: 82, 8: 8},
         "all-pairs profile")
    best_model = ceiling.model(best, **kwargs)
    need(best_model["local_mass"] == 5377 and best_model["idle_mass"] == 1855,
         "all-pairs mass split")
    best_bracket = ceiling.ceiling(best, **kwargs)
    need(best_bracket == FULL_CEILING, "exact all-pairs ceiling bracket")

    target = baseline[1] * Fraction(105, 100)
    ratio = best_bracket[1] / baseline[1]
    need(best_bracket[1] < target, "5% target must remain out of reach")
    need(ratio == Fraction(43131577624, 41220831929), "exact endpoint ratio")
    need(ratio < Fraction(21, 20), "strict 5% ratio control")

    # Negative controls: no 210th pair exists, an overfull source profile is rejected,
    # and rank 52 violates the pinned outer halving guard.
    try:
        fused(profile, 210)
    except AssertionError:
        pass
    else:
        raise AssertionError("impossible 210th fusion accepted")
    try:
        ceiling.model({**profile, 1: profile[1] + 10000}, **kwargs)
    except ValueError:
        pass
    else:
        raise AssertionError("overfull local mass accepted")
    try:
        ceiling.model(profile, **kwargs, R=52)
    except ValueError:
        pass
    else:
        raise AssertionError("rank-52 cap accepted")

    print(
        "PASS_SHARED_LINE_RANK2_SCREEN",
        f"profile={profile}",
        f"groups={maximum_groups}",
        f"baseline_hi={float(baseline[1]):.15f}",
        f"best_hi={float(best_bracket[1]):.15f}",
        f"ratio={float(ratio):.10f}",
        "target=1.05",
        "physical_interface=not_established",
    )


if __name__ == "__main__":
    main()
