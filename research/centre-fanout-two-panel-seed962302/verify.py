#!/usr/bin/env python3
"""Exact two-panel fanout for the selected 480-helper centre phase.

This replays the pinned event contract and tests its linear identity over Q.
The centre child itself is represented by an arbitrary exact rank-8 linear map;
the equality proof depends only on invoking the same map once on the same source.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import io
import json
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
RECORD_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
ASSEMBLY_SHA256 = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
PROVIDER = "candidate/strict/global/base/providers/gauge44/"
DIM = 8
EXPECTED_SOURCES = [92, 57, 81, 224, 11, 240, 9, 256]
EXPECTED_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json_tar(tar: tarfile.TarFile, path: str):
    member = tar.extractfile(path)
    need(member is not None, f"missing archive member {path}")
    raw = member.read()
    if path.endswith(".gz"):
        raw = gzip.decompress(raw)
    return json.loads(raw)


def scalar_clear(op, register: list) -> bool:
    return bool(
        op
        and op[0] == "scalar"
        and len(op) >= 2
        and op[1][0] == "clear"
        and op[1][1] == register
    )


def read_centres(program, word, local_checks):
    ops = program["forward"]
    centres = []
    for index, event in enumerate(ops):
        if not event or event[0] != "center":
            continue
        k, role, destination, rank = event[1:]
        need(k == len(centres), "centre events are not in canonical order")
        need(index >= 2, "centre event lacks its clear/copy prefix")
        before_clear, before_copy = ops[index - 2 : index]
        need(scalar_clear(before_clear, ["C", k]), f"centre {k}: missing dirty clear")
        need(before_clear[2] == role, f"centre {k}: clear role differs")
        need(
            before_copy[0] == "scalar"
            and before_copy[1][0] == "copy"
            and before_copy[1][1] == ["C", k]
            and before_copy[1][2][0] == "L",
            f"centre {k}: missing carrier copy",
        )
        source = before_copy[1][2][1]
        need(source == EXPECTED_SOURCES[k], f"centre {k}: source carrier changed")
        need((role, destination, rank) == (415 + k, 0, 8), f"centre {k}: event changed")
        need(word["center_frames"][k] == role, f"centre {k}: frame role changed")

        updates = []
        j = index + 1
        while j < len(ops) and not scalar_clear(ops[j], ["C", k]):
            current = ops[j]
            need(
                current[0] == "scalar"
                and current[1][0] == "add"
                and current[1][1][0] == "L"
                and current[1][2] == ["C", k],
                f"centre {k}: unexpected instruction in scatter block at {j}",
            )
            target = current[1][1][1]
            coefficient = Q(current[1][3], current[1][4])
            updates.append((target, coefficient))
            j += 1
        need(j < len(ops), f"centre {k}: missing final clear")
        need(ops[j][2] == 0, f"centre {k}: final clear has a nonzero frame")
        need(len(updates) == 22, f"centre {k}: expected 22 target updates")
        need(len({target for target, _ in updates}) == 22, f"centre {k}: repeated target")
        need(all(coefficient != 0 for _, coefficient in updates), f"centre {k}: zero scatter")
        centres.append(
            {"k": k, "role": role, "source": source, "updates": updates, "start": index - 2, "end": j}
        )

    need(len(centres) == 8, "selected word must have eight centre events")
    need(word["R"] == 480, "archive is not the selected 480-helper word")
    profile = {int(r): n for r, n in local_checks["forward"]["paid_profile"].items()}
    need(profile == EXPECTED_PROFILE, "selected per-call paid profile changed")
    need(sum(len(c["updates"]) for c in centres) == 176, "selected scatter edge count changed")
    return centres, profile


def matvec(matrix, vector):
    return [sum((a * b for a, b in zip(row, vector)), Q(0)) for row in matrix]


def transforms():
    """Nontrivial exact invertible maps; the fanout identity is valid for every map."""
    out = []
    for k in range(8):
        matrix = []
        for i in range(DIM):
            row = []
            for j in range(DIM):
                if i == j:
                    row.append(Q(1))
                elif i < j:
                    row.append(Q(((k + 3 * i + 5 * j) % 7) - 3, 28))
                else:
                    row.append(Q(0))
            matrix.append(row)
        out.append(matrix)
    return out


def zero_vector():
    return [Q(0) for _ in range(DIM)]


def empty_targets(ids):
    return {target: zero_vector() for target in ids}


def add_scaled(target, source, coefficient):
    return [x + coefficient * y for x, y in zip(target, source)]


def run_separate(centres, matrices, source_a, source_b, targets_a, targets_b, dirt_a, dirt_b):
    final_a, final_b = {}, {}
    for panel, sources, targets, dirt, final in (
        (0, source_a, targets_a, dirt_a, final_a),
        (1, source_b, targets_b, dirt_b, final_b),
    ):
        for centre in centres:
            k = centre["k"]
            private = list(dirt[k])
            private = zero_vector()  # selected pre-clear removes arbitrary dirty state
            private = [x + y for x, y in zip(private, sources[centre["source"]])]
            private = matvec(matrices[k], private)
            for target, coefficient in centre["updates"]:
                targets[target] = add_scaled(targets[target], private, coefficient)
            private = zero_vector()  # selected post-clear restores private state
            final[k] = private
    return targets_a, targets_b, final_a, final_b


def run_fused(
    centres,
    matrices,
    source_a,
    source_b,
    targets_a,
    targets_b,
    dirt,
    *,
    skip_update=None,
    restore=True,
):
    final = {}
    for centre in centres:
        k = centre["k"]
        private = list(dirt[k])
        private = zero_vector()  # one pre-clear for the shared private centre
        private = [x + y for x, y in zip(private, source_a[centre["source"]])]
        private = matvec(matrices[k], private)
        for panel, targets in ((0, targets_a), (1, targets_b)):
            for index, (target, coefficient) in enumerate(centre["updates"]):
                if skip_update == (panel, k, index):
                    continue
                targets[target] = add_scaled(targets[target], private, coefficient)
        final[k] = zero_vector() if restore else private
    return targets_a, targets_b, final


def test_basis(centres, matrices):
    target_ids = sorted({target for c in centres for target, _ in c["updates"]})
    source_ids = [c["source"] for c in centres]
    need(not (set(target_ids) & set(source_ids)), "source and target roles overlap")
    cases = 0
    zero_sources = {source: zero_vector() for source in source_ids}
    zero_dirt = {k: zero_vector() for k in range(8)}

    def compare(sa, sb, ta, tb, da, db, ds):
        nonlocal cases
        original_a = {r: list(v) for r, v in sa.items()}
        original_b = {r: list(v) for r, v in sb.items()}
        sep = run_separate(
            centres, matrices, sa, sb, {k: list(v) for k, v in ta.items()},
            {k: list(v) for k, v in tb.items()}, da, db
        )
        fused = run_fused(
            centres, matrices, sa, sb, {k: list(v) for k, v in ta.items()},
            {k: list(v) for k, v in tb.items()}, ds
        )
        need(sep[0] == fused[0] and sep[1] == fused[1], "fused panel map differs from separate calls")
        need(all(v == zero_vector() for v in sep[2].values()), "separate private centre not restored")
        need(all(v == zero_vector() for v in sep[3].values()), "second private centre not restored")
        need(all(v == zero_vector() for v in fused[2].values()), "shared private centre not restored")
        need(sa == original_a and sb == original_b, "shared source row was modified")
        cases += 1

    # Basis for every source coordinate.
    for source in source_ids:
        for coordinate in range(DIM):
            sa = {r: list(v) for r, v in zero_sources.items()}
            sa[source][coordinate] = Q(1)
            sb = {r: list(v) for r, v in sa.items()}
            compare(sa, sb, empty_targets(target_ids), empty_targets(target_ids), zero_dirt, zero_dirt, zero_dirt)

    # Basis for every arbitrary dirty coordinate in both target panels.
    for panel in (0, 1):
        for target in target_ids:
            for coordinate in range(DIM):
                ta, tb = empty_targets(target_ids), empty_targets(target_ids)
                (ta if panel == 0 else tb)[target][coordinate] = Q(1)
                compare(zero_sources, zero_sources, ta, tb, zero_dirt, zero_dirt, zero_dirt)

    # Independent dirty values in each private centre of each separate call.
    for k in range(8):
        for coordinate in range(DIM):
            da, db, ds = ({r: list(v) for r, v in zero_dirt.items()} for _ in range(3))
            da[k][coordinate] = Q(1)
            compare(zero_sources, zero_sources, empty_targets(target_ids), empty_targets(target_ids), da, zero_dirt, ds)
            da, db, ds = ({r: list(v) for r, v in zero_dirt.items()} for _ in range(3))
            db[k][coordinate] = Q(1)
            ds[k][coordinate] = Q(3, 7)
            compare(zero_sources, zero_sources, empty_targets(target_ids), empty_targets(target_ids), zero_dirt, db, ds)

    # A dense rational fixture checks simultaneous arbitrary dirt and all panels.
    sa = {r: [Q((r + 2 * i) % 9 - 4, 7) for i in range(DIM)] for r in source_ids}
    sb = {r: list(v) for r, v in sa.items()}
    ta = {r: [Q((r + i) % 11 - 5, 13) for i in range(DIM)] for r in target_ids}
    tb = {r: [Q((2 * r + i) % 13 - 6, 17) for i in range(DIM)] for r in target_ids}
    da = {k: [Q(k - i, 5) for i in range(DIM)] for k in range(8)}
    db = {k: [Q(i - k, 9) for i in range(DIM)] for k in range(8)}
    ds = {k: [Q(2 * i + k, 11) for i in range(DIM)] for k in range(8)}
    compare(sa, sb, ta, tb, da, db, ds)
    return cases, target_ids


def controls(centres, matrices, target_ids):
    source_ids = [c["source"] for c in centres]
    zero_sources = {source: zero_vector() for source in source_ids}
    targets_a, targets_b = empty_targets(target_ids), empty_targets(target_ids)
    dirt = {k: zero_vector() for k in range(8)}

    # A changed second source cannot be replaced by the shared source value.
    source_b = {r: list(v) for r, v in zero_sources.items()}
    source_b[source_ids[0]][0] = Q(1)
    separate = run_separate(
        centres, matrices, zero_sources, source_b, empty_targets(target_ids), empty_targets(target_ids), dirt, dirt
    )
    fused = run_fused(
        centres, matrices, zero_sources, source_b, empty_targets(target_ids), empty_targets(target_ids), dirt
    )
    need(separate[1] != fused[1], "changed-source negative control was not detected")

    # Omitting one of the two target-panel updates corrupts that output.
    nonzero = {r: zero_vector() for r in source_ids}
    nonzero[source_ids[0]][0] = Q(1)
    separate = run_separate(
        centres, matrices, nonzero, nonzero, empty_targets(target_ids), empty_targets(target_ids), dirt, dirt
    )
    fused = run_fused(
        centres, matrices, nonzero, nonzero, empty_targets(target_ids), empty_targets(target_ids), dirt,
        skip_update=(1, 0, 0),
    )
    need(separate[1] != fused[1], "missing-target negative control was not detected")

    # A missing final clear leaves private data after a nonzero source.
    _, _, final = run_fused(
        centres, matrices, nonzero, nonzero, empty_targets(target_ids), empty_targets(target_ids), dirt, restore=False
    )
    need(any(v != zero_vector() for v in final.values()), "missing-clear negative control was not detected")
    return 3


def main():
    task = json.loads((PKG / "TASK.json").read_text())
    selected_path = ROOT / "certificates/selected-result.json"
    selected_bytes = selected_path.read_bytes()
    selected = json.loads(selected_bytes)
    need(sha256(selected_bytes) == RECORD_SHA256 == task["selected_record_sha256"], "selected record pin changed")
    need(selected["kappa"] == "836330098538459/500000000000000000", "selected kappa changed")
    need(selected["source_manifest"] == "research/community-frontier1094-audit/SELECTED-SOURCE.json", "manifest link changed")
    need(selected["certificate"] == "research/community-frontier1094-audit/ASSEMBLY.json", "certificate link changed")
    need(selected["certificate_sha256"] == ASSEMBLY_SHA256, "selected certificate digest link changed")
    need(selected["reproduce"] == "make frontier1094-verify", "selected reproduction instruction changed")
    need(sha256((ROOT / selected["certificate"]).read_bytes()) == ASSEMBLY_SHA256, "selected certificate bytes changed")

    archive_bytes = ARCHIVE.read_bytes()
    need(sha256(archive_bytes) == ARCHIVE_SHA256, "selected replay archive pin changed")
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as archive:
        word = load_json_tar(archive, PROVIDER + "CANONICAL-WORD.json.gz")
        programs = load_json_tar(archive, PROVIDER + "LOCAL-PROGRAMS.json.gz")
        local_checks = load_json_tar(archive, PROVIDER + "LOCAL-CHECKS.json")
    centres, profile = read_centres(programs, word, local_checks)
    matrices = transforms()
    basis_cases, target_ids = test_basis(centres, matrices)
    control_count = controls(centres, matrices, target_ids)

    # Exact full local phase invoice for the two-call boundary.
    target_updates_per_panel = sum(len(c["updates"]) for c in centres)
    separate = {
        "clear": 4 * len(centres),
        "source_copy": 2 * len(centres),
        "rank8_center": 2 * len(centres),
        "target_update": 2 * target_updates_per_panel,
    }
    fused = {
        "clear": 2 * len(centres),
        "source_copy": len(centres),
        "rank8_center": len(centres),
        "target_update": 2 * target_updates_per_panel,
    }
    need(sum(separate.values()) == 416 and sum(fused.values()) == 384, "phase invoice changed")
    need(separate["target_update"] == fused["target_update"] == 352, "target updates were undercharged")
    need(separate["rank8_center"] - fused["rank8_center"] == 8, "rank-8 saving changed")

    # Recompute the favorable envelope, then compare it to the unchanged bit side.
    ceiling_path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("selected_ceiling", ceiling_path)
    ceiling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling)
    shared_profile = dict(profile)
    shared_profile[8] //= 2
    bit_a = Q(json.loads((ROOT / selected["certificate"]).read_text())["bit_lower"])
    lo, hi = ceiling.ceiling(shared_profile, 73, 896, 9, 32, grid=Q(1, 10**12))
    bit_moment = ceiling.relax(shared_profile, 73, 896, 9, 32, bit_a)
    need(lo < hi and bit_moment[1] < 1, "half-centre screen does not beat the current bit threshold")
    whole_kappa_cap = bit_a / (1 + bit_a)
    current_kappa = Q(selected["kappa"])
    gain_percent = (whole_kappa_cap / current_kappa - 1) * 100

    print(
        "PASS_CENTRE_TWO_PANEL_FANOUT "
        f"R={word['R']} centres={len(centres)} targets_per_centre=22 "
        f"updates_per_panel={target_updates_per_panel} basis_cases={basis_cases} controls={control_count} "
        f"actions={sum(separate.values())}->{sum(fused.values())} "
        f"rank8={separate['rank8_center']}->{fused['rank8_center']} "
        f"profile8={profile[8]}->{shared_profile[8]} "
        f"a_cap={float(hi):.12f} bit_a={float(bit_a):.12f} "
        f"whole_kappa_cap={float(whole_kappa_cap):.15f} max_gain_pct={float(gain_percent):.4f}"
    )


if __name__ == "__main__":
    main()
