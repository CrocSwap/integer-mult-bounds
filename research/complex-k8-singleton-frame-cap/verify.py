#!/usr/bin/env python3
"""Exhaust a singleton 4D-to-6D B-frame extension class for selected PR1094."""

from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import itertools
import json
import tarfile
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/FULL-WORD.json.gz"
MEMBER_SHA256 = "49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289"
WORD_SHA256 = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
ASSEMBLY_SHA256 = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
PLAN_SHA256 = "7bd786ba8e66408f02aa9ef446eaf20c1bfe981ea2e4dd1e5a929f0aa7767bc0"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
SOURCE_MANIFEST_SHA256 = "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def assert_pin(data: bytes, expected: str, label: str):
    assert sha256(data) == expected, label


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def span(vectors):
    pivots = {}
    for value in vectors:
        value = int(value)
        for pivot in sorted(pivots, reverse=True):
            if value >> pivot & 1:
                value ^= pivots[pivot]
        if value:
            pivot = value.bit_length() - 1
            for other in list(pivots):
                if pivots[other] >> pivot & 1:
                    pivots[other] ^= value
            pivots[pivot] = value
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


@lru_cache(maxsize=None)
def vectors(frame):
    out = {0}
    for basis_vector in frame:
        out |= {x ^ basis_vector for x in tuple(out)}
    return frozenset(out)


def registers(event):
    return [event[1]] + ([event[2]] if event[0] == "add" else [])


def terminal_frame(word, role):
    v, h, helpers = word["report"]["v"], word["report"]["h"], word["report"]["R"]
    if v <= role < 2 * v:
        port = word["ports"][role - v]
        return span(x for x in range(1, 1 << h) if (x & port).bit_count() % 2 == 0)
    helper_final = {int(r): f for r, f in word.get("helper_final", {}).items()}
    return span(helper_final.get(role, [1 << i for i in range(h)]))


def local_profile(word):
    """Independent literal climb counter: A, B, early cleanup, then endpoints."""
    v, h, helpers = word["report"]["v"], word["report"]["h"], word["report"]["R"]
    n = 2 * v + helpers
    current = [()] * n
    for role, port in enumerate(word["ports"]):
        current[role] = span([port])
    for role, frame in word.get("start_extra", {}).items():
        current[int(role)] = span(frame)
    profile = collections.Counter()

    def climb(role, frame):
        old = current[role]
        frame = span(frame)
        assert span(old + frame) == frame, ("nonmonotone", role)
        if len(frame) > len(old):
            profile[len(frame) - len(old)] += 1
        current[role] = frame

    for section in ("A", "B"):
        for event in word[section]:
            for role in registers(event):
                climb(role, event[-1])
    for cleanup_index, frame in word.get("early_cleanup", []):
        for role in registers(word["cleanup"][cleanup_index]):
            climb(role, frame)
    for role in range(n):
        climb(role, terminal_frame(word, role))
    # Centre calls are carried as their own eight rank-eight children by the
    # selected word. B gates do not touch the centre roles, so these fees are
    # invariant under the census and can be read from the pinned centre ledger.
    for rank in word["report"]["centre_ranks"]:
        profile[rank] += 1
    return profile


def all_6d_extensions(old):
    """Return all 6D superspaces of a 4D subspace in F_2^9 (Gaussian count 155)."""
    old = span(old)
    assert len(old) == 4
    enlarged = list(old)
    complement = []
    for vector in range(1, 1 << 9):
        trial = span(enlarged + [vector])
        if len(trial) > len(enlarged):
            enlarged = list(trial)
            complement.append(vector)
            if len(enlarged) == 9:
                break
    assert len(complement) == 5
    out = set()
    # Every 2-space in the five-dimensional quotient is represented by its
    # three nonzero vectors, so each unordered independent pair is one space.
    for left, right in itertools.combinations(range(1, 1 << 5), 2):
        lifts = []
        for mask in (left, right):
            value = 0
            for bit, vector in enumerate(complement):
                if mask >> bit & 1:
                    value ^= vector
            lifts.append(value)
        frame = span(old + tuple(lifts))
        if len(frame) == 6:
            out.add(frame)
    assert len(out) == 155, len(out)
    return tuple(sorted(out))


def load_selected_word():
    archive_bytes = ARCHIVE.read_bytes()
    assert sha256(archive_bytes) == ARCHIVE_SHA256, "selected replay archive pin"
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        member = archive.extractfile(MEMBER)
        assert member is not None, "selected local word member missing"
        compressed = member.read()
    assert sha256(compressed) == MEMBER_SHA256, "selected local word member pin"
    raw = gzip.decompress(compressed)
    assert sha256(raw) == WORD_SHA256, "selected local word content pin"
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    selected_path = ROOT / "certificates/selected-result.json"
    source_manifest_path = ROOT / "research/community-frontier1094-audit/SELECTED-SOURCE.json"
    assembly_path = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
    plan_path = ROOT / "research/complex-t16-rare-pattern-exchanges/data/PLAN.json"
    source_manifest = read_json(PACKAGE / "SOURCES.json")
    assert source_manifest["base_commit"] == BASE, "source manifest base"
    for row in source_manifest["inputs"]:
        source_bytes = (ROOT / row["path"]).read_bytes()
        assert sha256(source_bytes) == row["sha256"], "source manifest pin " + row["path"]
    selected_bytes = selected_path.read_bytes()
    source_manifest_bytes = source_manifest_path.read_bytes()
    assembly_bytes = assembly_path.read_bytes()
    plan_bytes = plan_path.read_bytes()
    assert sha256(selected_bytes) == SELECTED_SHA256, "selected record pin"
    if SOURCE_MANIFEST_SHA256:
        assert sha256(source_manifest_bytes) == SOURCE_MANIFEST_SHA256, "selected source manifest pin"
    assert sha256(assembly_bytes) == ASSEMBLY_SHA256, "selected assembly pin"
    assert sha256(plan_bytes) == PLAN_SHA256, "selected T16 plan pin"
    selected, assembly, plan = map(json.loads, (selected_bytes, assembly_bytes, plan_bytes))
    assert selected["source_manifest"] == "research/community-frontier1094-audit/SELECTED-SOURCE.json"
    assert selected["proof"] == "docs/research/community-batch1099-review.md"
    assert selected["audited_source_head"] == "0fc329d0bec93ca7cd288eaea1295172e8789810"
    assert assembly["kappa"] == selected["kappa"] and assembly["binding"] == "complex"
    assert plan["profile"] == {str(k): int(v) for k, v in assembly["complex_profile"].items()}
    assert len(plan["provider_calls"]) == 144
    assert all(call["provider"] == "gauge44" for call in plan["provider_calls"])

    word = load_selected_word()
    sample_old = span([1, 2, 4, 8])
    sample_extensions = all_6d_extensions(sample_old)
    assert len(sample_extensions) == 155
    assert all(len(frame) == 6 and vectors(sample_old) <= vectors(frame) for frame in sample_extensions)
    try:
        assert_pin(b"selected-record-mutation", SELECTED_SHA256, "selected record mutation control")
    except AssertionError:
        pin_mutation_rejected = True
    else:
        raise AssertionError("selected record mutation was accepted")
    complement = []
    enlarged = list(sample_old)
    for value in range(1, 1 << 9):
        candidate = span(enlarged + [value])
        if len(candidate) > len(enlarged):
            enlarged = list(candidate)
            if len(enlarged) == 9:
                break
    # Three independent quotient directions plus three old basis vectors
    # make a 6D frame that omits one old direction.
    complement = [value for value in enlarged if value not in sample_old]
    incompatible = span(sample_old[1:] + tuple(complement[:3]))
    assert len(incompatible) == 6 and not (vectors(sample_old) <= vectors(incompatible))
    centres = set(word["centers"])
    assert len(centres) == len(word["center_frames"]) == 8
    assert all(len(span(frame)) == 8 for frame in word["center_frames"])
    assert all(not centres.intersection(registers(event)) for event in word["B"]), "B gate touches a centre role"
    base_profile = local_profile(word)
    reported = {int(k): int(v) for k, v in word["report"]["local_profile"].items()}
    assert dict(base_profile) == reported
    registry_profile = {int(k): int(v) for k, v in plan["provider_registry"]["gauge44"]["actual_paid_profile"].items()}
    assert registry_profile == reported
    registry_widths = collections.Counter(map(int, plan["provider_registry"]["gauge44"]["widths"]))
    reported_widths = {int(k): int(v) for k, v in word["report"]["width_inventory"].items()}
    assert dict(registry_widths) == reported_widths

    # Global profile is exactly 144 local provider profiles plus unchanged
    # owner/centre/idle events. A frame-only change leaves widths and call count fixed.
    global_profile = {int(k): int(v) for k, v in plan["profile"].items()}
    extra = collections.Counter(global_profile)
    for rank, count in reported.items():
        extra[rank] -= 144 * count
    assert min(extra.values()) >= 0, "selected global profile is not 144 local copies plus extras"

    v, h, helpers = word["report"]["v"], word["report"]["h"], word["report"]["R"]
    n = 2 * v + helpers
    running = {role: set(vectors(terminal_frame(word, role))) for role in range(n)}
    for cleanup_index, frame in word.get("early_cleanup", []):
        for role in registers(word["cleanup"][cleanup_index]):
            running[role].intersection_update(vectors(span(frame)))

    total_gates = 0
    domain_count = 0
    feasible_count = 0
    superspaces_enumerated = 0
    cap_dimensions = collections.Counter()
    gate_caps = []
    feasible = []
    for index in range(len(word["B"]) - 1, -1, -1):
        event = word["B"][index]
        old = span(event[-1])
        roles = registers(event)
        if len(old) == 4:
            total_gates += 1
            domain_count += 155
            common = set.intersection(*(running[role] for role in roles))
            cap = span(common)
            assert vectors(old) <= common, ("base frame exceeds suffix cap", index)
            cap_dimensions[len(cap)] += 1
            gate_caps.append({
                "B_index": index,
                "roles": roles,
                "old_frame": list(old),
                "common_suffix_cap": list(cap),
                "cap_dimension": len(cap),
                "superspaces_ruled_out_by_cap": 155 if len(cap) < 6 else 0,
            })
            if len(cap) >= 6:
                for candidate in all_6d_extensions(old):
                    superspaces_enumerated += 1
                    if vectors(candidate) <= common:
                        feasible_count += 1
                        altered = json.loads(json.dumps(word))
                        altered["B"][index][-1] = list(candidate)
                        profile = local_profile(altered)
                        feasible.append({
                            "B_index": index,
                            "frame": list(candidate),
                            "local_profile": dict(sorted(profile.items())),
                        })
        frame_vectors = vectors(old)
        for role in roles:
            running[role].intersection_update(frame_vectors)

    assert sum(cap_dimensions.values()) == total_gates
    assert max(cap_dimensions, default=0) < 6, "a 6D common suffix cap requires a separate exact repricing"
    assert superspaces_enumerated == 0 and feasible_count == 0, "a feasible singleton requires separate exact repricing"

    result = {
        "status": "PASS_NO_ADDITIONAL_4_TO_6_SINGLETON_B_FRAME",
        "base_commit": BASE,
        "selected_kappa": selected["kappa"],
        "selected_complex_endpoint": assembly["complex_lower"],
        "source": {
            "selected_record_sha256": SELECTED_SHA256,
            "assembly_sha256": ASSEMBLY_SHA256,
            "plan_sha256": PLAN_SHA256,
            "selected_replay_tar_sha256": ARCHIVE_SHA256,
            "selected_local_word_member": MEMBER,
            "member_sha256": MEMBER_SHA256,
            "uncompressed_word_sha256": WORD_SHA256,
        },
        "domain": {
            "local_B_gates": len(word["B"]),
            "centre_roles": len(centres),
            "B_gate_centre_accesses": 0,
            "unchanged_4d_B_gates": total_gates,
            "superspaces_per_gate": 155,
            "candidate_space_size": domain_count,
            "superspaces_enumerated_after_cap_screen": superspaces_enumerated,
            "superspaces_ruled_out_by_exact_cap_dimension": domain_count - superspaces_enumerated,
            "maximum_common_suffix_cap_dimension": max(cap_dimensions, default=0),
            "suffix_cap_dimension_by_gate": dict(sorted(cap_dimensions.items())),
            "chronologically_feasible_singletons": feasible_count,
        },
        "controls": {
            "gaussian_superspace_positive_control": {"dimension": 4, "extensions": len(sample_extensions), "expected": 155},
            "incompatible_6d_frame_rejected": True,
            "incompatible_6d_frame": list(incompatible),
            "selected_source_hash_mutation_rejected": pin_mutation_rejected,
        },
        "per_gate_suffix_caps": gate_caps,
        "base": {
            "local_profile": dict(sorted(reported.items())),
            "global_profile": dict(sorted(global_profile.items())),
            "unchanged_global_extras_after_144_calls": dict(sorted((k, v) for k, v in extra.items() if v)),
            "width_inventory": word["report"]["width_inventory"],
            "selected_owner_width_inventory": dict(sorted(registry_widths.items())),
            "provider_calls": len(plan["provider_calls"]),
        },
        "feasible_candidates": feasible,
        "candidate_argument": "For a B event at index i, any legal replacement frame must contain the current 4D frame and lie in the intersection of every later frame on both affected register chains, including early cleanups and terminal frames. That intersection is recorded as common_suffix_cap. Every one of the 155 6D superspaces per eligible gate is excluded because all recorded cap dimensions are below 6.",
        "optimistic_cost": "A legal one-gate change would add no scalar operation, source access, copy, helper, restoration, width or owner event; it would only alter the local paid histogram and, repeated over 144 calls, the global moment. No candidate passes frame feasibility, so the selected profile and complex moment are unchanged for this scope.",
        "scope": "Only one additional B-gate frame is changed, from a 4D span to a 6D superspace in F2^9. Scalar operations, entrances, terminal frames, endpoints, widths, owner map, centre charges and 144-call schedule are fixed. No multi-gate schedule optimality, other frame dimensions or new kappa claim.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS_NO_ADDITIONAL_4_TO_6_SINGLETON_B_FRAME",
        f"gates={total_gates}",
        f"candidate_space={domain_count}",
        f"max_cap_dimension={max(cap_dimensions, default=0)}",
        f"chronologically_feasible={feasible_count}",
    )


if __name__ == "__main__":
    main()
