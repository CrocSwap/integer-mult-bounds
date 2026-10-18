#!/usr/bin/env python3
"""Exact bounded census of centre source ownership in the selected schedule."""

from __future__ import annotations

import gzip
import hashlib
import json
import tarfile
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_REL = Path("research/community-frontier1094-audit/selected-replay.tar.gz")
SELECTED_REL = Path("certificates/selected-result.json")
BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
MANIFEST_REL = Path("research/community-frontier1094-audit/SELECTED-SOURCE.json")
MANIFEST_SHA256 = "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b"
ASSEMBLY_REL = Path("research/community-frontier1094-audit/ASSEMBLY.json")
ASSEMBLY_SHA256 = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
REVIEW_REL = Path("docs/research/community-batch1099-review.md")
REVIEW_SHA256 = "7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb"
INTEGRATION_REL = Path("docs/research/community-batch1099-integration.json")
INTEGRATION_SHA256 = "684c50d1ac69863e1fcc0a34bf76c54bac576f6bbde79b3c67d8432a495c8c1c"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBERS = {
    "global": (
        "candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz",
        "2acf02b418078e37090495c601fe550448751d4f35912757b13a1f778efc7760",
    ),
    "programs": (
        "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz",
        "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    ),
    "checks": (
        "candidate/strict/global/base/providers/gauge44/LOCAL-CHECKS.json",
        "2b8b1891a736598010232bfb26abc31973b265a53a2009a3fcfd9138b5ecadb4",
    ),
    "word": (
        "candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz",
        "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    ),
}
SOURCE_REGISTERS = (92, 57, 81, 224, 11, 240, 9, 256)
PREDECESSOR_HEADS = {
    "PR1708": "4d163c04c0980c5b0e9092fbd5864c7cfadc125d",
    "PR1748": "ea14f191752c9901bf6684763534d2d248fb2ad2",
    "PR1791": "00d05a64898571cf57a14310fbcd3507ca99c5ec",
}


def need(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return sha256(payload)


def read_pins() -> dict[str, object]:
    selected = ROOT / SELECTED_REL
    selected_bytes = selected.read_bytes()
    need(sha256(selected_bytes) == SELECTED_SHA256, "selected-result pin changed")
    selected_record = json.loads(selected_bytes)
    manifest_bytes = (ROOT / MANIFEST_REL).read_bytes()
    assembly_bytes = (ROOT / ASSEMBLY_REL).read_bytes()
    review_bytes = (ROOT / REVIEW_REL).read_bytes()
    integration_bytes = (ROOT / INTEGRATION_REL).read_bytes()
    need(sha256(manifest_bytes) == MANIFEST_SHA256, "selected source-manifest pin changed")
    need(sha256(assembly_bytes) == ASSEMBLY_SHA256, "selected assembly-certificate pin changed")
    need(sha256(review_bytes) == REVIEW_SHA256, "selected review pin changed")
    need(sha256(integration_bytes) == INTEGRATION_SHA256, "selected integration-receipt pin changed")
    need(selected_record["source_manifest"] == str(MANIFEST_REL),
         "selected record no longer names the pinned source manifest")
    need(selected_record["certificate"] == str(ASSEMBLY_REL),
         "selected record no longer names the pinned assembly certificate")
    need(selected_record["certificate_sha256"] == ASSEMBLY_SHA256,
         "selected record's assembly hash no longer matches the certificate")
    need(selected_record["proof"] == str(REVIEW_REL)
         and selected_record["review"] == str(REVIEW_REL),
         "selected record no longer names the pinned review")
    need(selected_record["validation"] == str(INTEGRATION_REL),
         "selected record no longer names the pinned integration receipt")
    need(selected_record["reproduce"] == "make frontier1094-verify",
         "selected reproduction command changed")
    assembly = json.loads(assembly_bytes)
    need(assembly["kappa"] == selected_record["kappa"],
         "selected record and assembly conditional value differ")

    archive_path = ROOT / ARCHIVE_REL
    archive_bytes = archive_path.read_bytes()
    need(sha256(archive_bytes) == ARCHIVE_SHA256, "selected replay archive pin changed")

    data: dict[str, object] = {}
    global_payload_sha256 = None
    with tarfile.open(archive_path, "r:gz") as archive:
        for key, (member_name, expected_hash) in MEMBERS.items():
            member = archive.extractfile(member_name)
            need(member is not None, f"missing source member: {member_name}")
            raw = member.read()
            need(sha256(raw) == expected_hash, f"source member changed: {member_name}")
            payload = gzip.decompress(raw) if member_name.endswith(".gz") else raw
            data[key] = json.loads(payload)
            if key == "global":
                global_payload_sha256 = sha256(payload)
    data["selected"] = selected_record
    data["assembly"] = assembly
    data["global_payload_sha256"] = global_payload_sha256
    return data


def scalar_clear(event: list, register: list, role: int) -> bool:
    return (
        len(event) == 3
        and event[0] == "scalar"
        and event[1] == ["clear", register]
        and event[2] == role
    )


def read_forward(program: list, word: dict) -> list[dict]:
    ops = program
    centers: list[dict] = []
    for k, source in enumerate(SOURCE_REGISTERS):
        hits = [i for i, event in enumerate(ops) if event and event[0] == "center" and event[1] == k]
        need(len(hits) == 1, f"forward centre {k}: expected one event")
        i = hits[0]
        need(i >= 2, f"forward centre {k}: missing clear/copy prefix")
        role = 415 + k
        need(ops[i] == ["center", k, role, 0, 8], f"forward centre {k}: centre event changed")
        need(scalar_clear(ops[i - 2], ["C", k], role),
             f"forward centre {k}: dirty centre register was not cleared")
        copy = ops[i - 1]
        need(
            copy[0] == "scalar"
            and copy[1][0] == "copy"
            and copy[1][1] == ["C", k]
            and copy[1][2] == ["L", source]
            and copy[2] == role,
            f"forward centre {k}: source carrier changed",
        )
        need(word["center_frames"][k] == role, f"forward centre {k}: frame map changed")

        targets: list[int] = []
        coefficients: list[Fraction] = []
        j = i + 1
        while j < len(ops) and not scalar_clear(ops[j], ["C", k], 0):
            event = ops[j]
            need(
                len(event) == 3
                and event[0] == "scalar"
                and event[1][0] == "add"
                and event[1][1][0] == "L"
                and event[1][2] == ["C", k]
                and event[2] == 0,
                f"forward centre {k}: scatter block changed at event {j}",
            )
            op = event[1]
            need(type(op[3]) is int and type(op[4]) is int and op[4] != 0,
                 f"forward centre {k}: invalid rational coefficient")
            targets.append(op[1][1])
            coefficients.append(Fraction(op[3], op[4]))
            j += 1
        need(j < len(ops), f"forward centre {k}: missing final clear")
        need(scalar_clear(ops[j], ["C", k], 0), f"forward centre {k}: final clear changed")
        need(len(targets) == 22 and len(set(targets)) == 22,
             f"forward centre {k}: expected 22 distinct scatter targets")
        need(all(112 <= target < 224 for target in targets),
             f"forward centre {k}: scatter target outside the selected panel")
        expected = [
            (entry[1], Fraction(entry[3], entry[4]))
            for entry in word["cut"]
            if entry[2] == source
        ]
        need(list(zip(targets, coefficients)) == expected and len(expected) == 22,
             f"forward centre {k}: scatter differs from CANONICAL-WORD.cut")
        centers.append({"source": source, "targets": tuple(targets)})
    need(len(centers) == 8, "forward program does not contain eight centre blocks")
    return centers


def read_backward(program: list, word: dict) -> list[dict]:
    ops = program
    need(word["centers"] == list(SOURCE_REGISTERS), "canonical source inventory changed")
    need(word["center_frames"] == list(range(415, 423)), "canonical centre frame inventory changed")
    start = ops.index(["phase", "centers"])
    end = ops.index(["phase", "B"])
    block = ops[start + 1 : end]
    need(len(block) == 208, "backward centre block is not 208 macros")

    centers: list[dict] = []
    for k, source in enumerate(SOURCE_REGISTERS):
        part = block[26 * k : 26 * (k + 1)]
        role = 415 + k
        need(part[0] == ["scalar", ["clear", ["C", k]], 0],
             f"backward centre {k}: initial clear changed")
        targets: list[int] = []
        coefficients: list[Fraction] = []
        for event in part[1:23]:
            need(
                len(event) == 3
                and event[0] == "scalar"
                and event[1][0] == "add"
                and event[1][1] == ["C", k]
                and event[1][2][0] == "L"
                and event[2] == 0,
                f"backward centre {k}: gather block changed",
            )
            op = event[1]
            need(type(op[3]) is int and type(op[4]) is int and op[4] != 0,
                 f"backward centre {k}: invalid rational coefficient")
            targets.append(op[2][1])
            coefficients.append(Fraction(op[3], op[4]))
        need(part[23] == ["center", k, 0, role, 8],
             f"backward centre {k}: centre event changed")
        need(part[24] == ["scalar", ["add", ["L", source], ["C", k], -1, 1], role],
             f"backward centre {k}: source restoration changed")
        need(part[25] == ["scalar", ["clear", ["C", k]], role],
             f"backward centre {k}: final clear changed")
        expected = [
            (entry[1], Fraction(entry[3], entry[4]))
            for entry in word["cut"]
            if entry[2] == source
        ]
        need(list(zip(targets, coefficients)) == expected and len(expected) == 22,
             f"backward centre {k}: gather differs from CANONICAL-WORD.cut")
        need(len(set(targets)) == 22 and all(112 <= target < 224 for target in targets),
             f"backward centre {k}: invalid full-panel target roles")
        centers.append({"source": source, "targets": tuple(targets)})
    return centers


def source_signature(call: dict, centers: list[dict]) -> tuple[tuple[int, tuple[int, ...]], ...]:
    owners = call["owners"]
    need(len(owners) == 704, "call owner map does not contain all 704 local roles")
    signature = []
    for center in centers:
        owner_id, chart = owners[center["source"]]
        need(type(owner_id) is int, "source owner ID is not an integer")
        need(isinstance(chart, list) and len(chart) == 3 and all(type(x) is int for x in chart),
             "source chart is not a three-integer tuple")
        signature.append((owner_id, tuple(chart)))
    return tuple(signature)


def target_panel(call: dict) -> frozenset[int]:
    owners = call["owners"]
    panel = owners[112:224]
    need(len(panel) == 112, "call does not map the complete 112-row panel")
    ids = []
    for owner_id, chart in panel:
        need(type(owner_id) is int, "target owner ID is not an integer")
        need(isinstance(chart, list) and len(chart) == 3 and all(type(x) is int for x in chart),
             "target chart is not a three-integer tuple")
        ids.append(owner_id)
    need(len(set(ids)) == 112, "a call aliases rows inside its 112-row target panel")
    return frozenset(ids)


def directly_eligible(
    orientation_a: str,
    sources_a: tuple[tuple[int, tuple[int, ...]], ...],
    targets_a: frozenset[int],
    orientation_b: str,
    sources_b: tuple[tuple[int, tuple[int, ...]], ...],
    targets_b: frozenset[int],
) -> bool:
    return (
        orientation_a == orientation_b
        and sources_a == sources_b
        and targets_a.isdisjoint(targets_b)
    )


def check_controls() -> dict[str, bool]:
    base_sources = tuple((1000 + k, (1, 2, k)) for k in range(8))
    left_targets = frozenset(range(112, 224))
    right_targets = frozenset(range(224, 336))
    positive = directly_eligible(
        "forward", base_sources, left_targets,
        "forward", base_sources, right_targets,
    )
    changed_owner = list(base_sources)
    changed_owner[3] = (9003, changed_owner[3][1])
    owner_control = not directly_eligible(
        "forward", base_sources, left_targets,
        "forward", tuple(changed_owner), right_targets,
    )
    changed_chart = list(base_sources)
    changed_chart[5] = (changed_chart[5][0], (1, 9, 5))
    chart_control = not directly_eligible(
        "forward", base_sources, left_targets,
        "forward", tuple(changed_chart), right_targets,
    )
    equal_chart_distinct_owner = tuple(
        (2000 + k, source[1]) for k, source in enumerate(base_sources)
    )
    chart_alias_control = not directly_eligible(
        "forward", base_sources, left_targets,
        "forward", equal_chart_distinct_owner, right_targets,
    )
    mixed_orientation_control = not directly_eligible(
        "forward", base_sources, left_targets,
        "backward", base_sources, right_targets,
    )
    overlap_control = not directly_eligible(
        "forward", base_sources, left_targets,
        "forward", base_sources, frozenset(range(200, 312)),
    )
    controls = {
        "positive_identical_sources_disjoint_panels": positive,
        "negative_changed_owner": owner_control,
        "negative_changed_chart": chart_control,
        "negative_equal_charts_distinct_owners": chart_alias_control,
        "negative_mixed_orientation": mixed_orientation_control,
        "negative_overlapping_panels": overlap_control,
    }
    need(all(controls.values()), "a synthetic admission control failed")
    return controls


def census(data: dict[str, object]) -> dict[str, object]:
    global_template = data["global"]
    programs = data["programs"]
    checks = data["checks"]
    word = data["word"]
    assembly = data["assembly"]
    need(assembly["template_sha256"] == data["global_payload_sha256"],
         "selected assembly does not bind the archived global template payload")
    need(word["centers"] == list(SOURCE_REGISTERS), "selected centre sources changed")
    need(word["center_frames"] == list(range(415, 423)), "selected centre frames changed")
    need(len(word["cut"]) == 176, "selected cut does not contain 176 edges")

    for orientation in ("forward", "backward"):
        digest = canonical_digest(programs[orientation])
        need(digest == checks[orientation]["sha256"],
             f"{orientation} local program differs from LOCAL-CHECKS")
    forward = read_forward(programs["forward"], word)
    backward = read_backward(programs["backward"], word)
    need(
        tuple(c["targets"] for c in forward) == tuple(c["targets"] for c in backward),
        "forward scatter and backward gather do not use the same target panel rows",
    )
    role_map = {"forward": forward, "backward": backward}

    calls = sorted(global_template["calls"], key=lambda row: row["time"])
    need(len(calls) == 144, "selected schedule does not contain 144 calls")
    need([call["time"] for call in calls] == list(range(144)),
         "selected call times are not exactly 0 through 143")
    sweeps = [
        event
        for event in global_template["execution_schedule"]
        if event.get("kind") == "local_cover_sweep"
    ]
    need(len(sweeps) == 144, "selected execution schedule does not contain 144 local sweeps")
    sweep_by_time = {event["time"]: event for event in sweeps}
    need(len(sweep_by_time) == 144, "local sweep times are not unique")

    call_data = []
    for call in calls:
        time = call["time"]
        event = sweep_by_time.get(time)
        need(event is not None, f"call {time}: no local sweep event")
        for key in ("provider_id", "replica", "stage", "time"):
            need(call[key] == event[key], f"call {time}: local sweep {key} mismatch")
        need(event["replicas"] == [event["replica"]],
             f"call {time}: sweep does not name a single replica")
        need(call["provider_id"] == "gauge44", f"call {time}: provider changed")
        expected_orientation = "forward" if call["stage"] % 2 == 0 else "backward"
        need(call["orientation"] == expected_orientation,
             f"call {time}: orientation disagrees with selected stage")
        need(
            call["local_program_sha256"] == checks[call["orientation"]]["sha256"],
            f"call {time}: local program digest does not match its orientation",
        )
        signature = source_signature(call, role_map[call["orientation"]])
        panel = target_panel(call)
        active = {
            call["owners"][target][0]
            for center in role_map[call["orientation"]]
            for target in center["targets"]
        }
        need(active <= panel, f"call {time}: a centre scatter target lies outside the full panel")
        call_data.append(
            {
                "orientation": call["orientation"],
                "signature": signature,
                "source_owner_ids": frozenset(owner for owner, _ in signature),
                "target_panel": panel,
                "active_target_owner_count": len(active),
            }
        )

    same_orientation = 0
    mixed_orientation = 0
    target_disjoint = 0
    full_chart_equal = 0
    full_source_equal = 0
    any_source_owner_overlap = 0
    max_source_owner_intersection = 0
    max_equal_owner_slots = 0
    admitted = 0
    for i in range(143):
        a, b = call_data[i], call_data[i + 1]
        if a["orientation"] != b["orientation"]:
            mixed_orientation += 1
            need(
                not directly_eligible(
                    a["orientation"], a["signature"], a["target_panel"],
                    b["orientation"], b["signature"], b["target_panel"],
                ),
                f"mixed-orientation pair {i}/{i + 1} was admitted",
            )
            continue
        same_orientation += 1
        overlap = len(a["source_owner_ids"] & b["source_owner_ids"])
        max_source_owner_intersection = max(max_source_owner_intersection, overlap)
        any_source_owner_overlap += overlap > 0
        equal_owner_slots = sum(
            left[0] == right[0]
            for left, right in zip(a["signature"], b["signature"])
        )
        max_equal_owner_slots = max(max_equal_owner_slots, equal_owner_slots)
        full_chart_equal += all(
            left[1] == right[1]
            for left, right in zip(a["signature"], b["signature"])
        )
        full_source_equal += a["signature"] == b["signature"]
        panel_disjoint = a["target_panel"].isdisjoint(b["target_panel"])
        target_disjoint += panel_disjoint
        admitted += directly_eligible(
            a["orientation"], a["signature"], a["target_panel"],
            b["orientation"], b["signature"], b["target_panel"],
        )

    need((same_orientation, mixed_orientation) == (81, 62),
         "adjacent orientation partition changed")
    need(target_disjoint == 81, "not every same-orientation pair has disjoint full panels")
    need(any_source_owner_overlap == 0, "an adjacent same-orientation pair shares a source owner")
    need(max_source_owner_intersection == 0 and max_equal_owner_slots == 0,
         "an adjacent same-orientation pair shares a source owner slot")
    need(full_chart_equal == 9, "full chart-equality count changed")
    need(full_source_equal == 0, "an adjacent pair has an identical eight-row owner/chart boundary")
    need(admitted == 0, "a direct-owner pair unexpectedly passed the admission predicate")

    return {
        "status": "PASS_SELECTED_ADJACENT_OWNER_CENSUS",
        "pins": {
            "base_commit": BASE_COMMIT,
            "selected_result_sha256": SELECTED_SHA256,
            "source_manifest_sha256": MANIFEST_SHA256,
            "assembly_certificate_sha256": ASSEMBLY_SHA256,
            "review_sha256": REVIEW_SHA256,
            "integration_receipt_sha256": INTEGRATION_SHA256,
            "selected_reproduction_command": "make frontier1094-verify",
            "selected_replay_archive_sha256": ARCHIVE_SHA256,
            "archive_member_sha256": {key: MEMBERS[key][1] for key in MEMBERS},
            "predecessor_heads": PREDECESSOR_HEADS,
        },
        "counts": {
            "scheduled_calls": len(calls),
            "adjacent_pairs": 143,
            "same_orientation_pairs": same_orientation,
            "mixed_orientation_pairs": mixed_orientation,
            "same_orientation_pairs_with_disjoint_full_112_row_panels": target_disjoint,
            "same_orientation_pairs_with_any_common_centre_source_owner": any_source_owner_overlap,
            "maximum_common_centre_source_owners_in_a_pair": max_source_owner_intersection,
            "maximum_equal_source_owner_slots_in_a_pair": max_equal_owner_slots,
            "pairs_with_all_eight_chart_tuples_equal": full_chart_equal,
            "pairs_with_all_eight_owner_chart_pairs_equal": full_source_equal,
            "directly_eligible_pairs": admitted,
            "unique_active_centre_targets_per_call": sorted(
                {row["active_target_owner_count"] for row in call_data}
            ),
        },
        "controls": check_controls(),
        "scope": (
            "Only the 143 adjacent pairs in this fixed selected schedule; "
            "direct identical owner/chart rows, no owner transport."
        ),
    }


def main() -> None:
    result = census(read_pins())
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
