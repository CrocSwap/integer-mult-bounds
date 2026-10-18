#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent data-only closure audit of the selected PR1042 replay capsule."""
import argparse
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import re
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HEX64 = re.compile(r"[0-9a-f]{64}")
MAX_MEMBERS = 1000
MAX_MEMBER_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 64 * 1024 * 1024
ROOT_MEMBERS = {
    "RESULT.json", "STAGES.json", "BASELINE-BINDING.json",
    "t16/ASSEMBLY.json", "t16/INDEPENDENT-T16.json", "t16/REPLAY.json",
}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def digest(data):
    return sha256(data).hexdigest()

def strict_json(data, label):
    def no_duplicates(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, f"duplicate JSON key in {label}: {key}")
            out[key] = value
        return out
    try:
        return json.loads(data, object_pairs_hook=no_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON in {label}: {exc}") from exc

def safe_name(name):
    require(type(name) is str and name and "\\" not in name and ":" not in name,
            "invalid archive member path")
    p = PurePosixPath(name)
    require(not p.is_absolute() and p.as_posix() == name and
            all(part not in ("", ".", "..") for part in p.parts),
            "unsafe archive member path: " + name)
    return name

def validate_namespace(members):
    require(type(members) is list and len(members) <= MAX_MEMBERS,
            "archive member limit exceeded")
    names, total = [], 0
    for member in members:
        name = safe_name(member.name)
        require(member.isfile(), "archive member is not a regular file: " + name)
        require(type(member.size) is int and 0 <= member.size <= MAX_MEMBER_BYTES,
                "archive member size limit exceeded: " + name)
        require(member.mode & 0o111 == 0, "archive member is executable: " + name)
        names.append(name)
        total += member.size
    require(len(names) == len(set(names)), "duplicate archive member name")
    require(total <= MAX_TOTAL_BYTES, "expanded archive size limit exceeded")
    return names, total

def read_capsule(path):
    raw_roots, member_digests = {}, {}
    with tarfile.open(path, "r:gz") as archive:
        members = archive.getmembers()
        names, total = validate_namespace(members)
        for member in members:
            stream = archive.extractfile(member)
            require(stream is not None, "archive regular file is unreadable: " + member.name)
            payload = stream.read(MAX_MEMBER_BYTES + 1)
            require(len(payload) == member.size, "archive member length differs: " + member.name)
            member_digests[member.name] = digest(payload)
            if member.name in ROOT_MEMBERS:
                raw_roots[member.name] = payload
    require(ROOT_MEMBERS <= set(raw_roots), "required root receipt missing")
    return names, total, member_digests, raw_roots

def validate_result(result, stages, names, member_digests, expected_stages):
    require(type(result) is dict and result.get("status") == "PASS_COMPLETE_PR1042_COMPOSITION",
            "unexpected capsule result status")
    artifacts = result.get("artifacts")
    require(type(artifacts) is dict, "artifact inventory is not an object")
    require(set(artifacts) == set(names) - {"RESULT.json"},
            "RESULT artifact inventory is not exact archive closure")
    for name, expected in artifacts.items():
        require(type(expected) is str and HEX64.fullmatch(expected) is not None,
                "invalid artifact digest: " + name)
        require(member_digests[name] == expected, "artifact digest differs: " + name)
    recorded_stages = result.get("stages")
    require(type(recorded_stages) is list and recorded_stages == stages,
            "STAGES.json differs from RESULT stages")
    require([item.get("name") for item in stages] == expected_stages,
            "stage sequence differs")
    for item in stages:
        name = item.get("name")
        require(type(item.get("exit_code")) is int and item["exit_code"] == 0,
                "recorded stage failed: " + str(name))
        expected = item.get("log_sha256")
        require(type(expected) is str and HEX64.fullmatch(expected) is not None,
                "invalid stage log digest: " + str(name))
        log_name = name + ".log"
        require(log_name in member_digests and member_digests[log_name] == expected,
                "stage log binding differs: " + str(name))
    return len(artifacts)

def repository_file(relative, expected=None):
    require(type(relative) is str, "invalid repository path")
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT.resolve()) and path.is_file(),
            "missing repository file: " + relative)
    data = path.read_bytes()
    if expected is not None:
        require(digest(data) == expected, "repository pin differs: " + relative)
    return data

def package_file(relative, expected):
    require(type(relative) is str, "invalid package path")
    path = (HERE / relative).resolve()
    require(path.is_relative_to(HERE.resolve()) and path.is_file(),
            "missing package file: " + relative)
    data = path.read_bytes()
    require(digest(data) == expected, "package pin differs: " + relative)
    return data

def check(pins):
    require(pins.get("schema") == "integer-mult-frontier1042-capsule-closure-v1",
            "unsupported pins schema")
    archive_pin = pins["archive"]
    archive_raw = repository_file(archive_pin["path"], archive_pin["sha256"])
    names, expanded, member_digests, roots = read_capsule(ROOT / archive_pin["path"])
    require(len(names) == archive_pin["members"] and expanded == archive_pin["expanded_bytes"],
            "archive count or expanded size differs")
    result = strict_json(roots["RESULT.json"], "RESULT.json")
    stages = strict_json(roots["STAGES.json"], "STAGES.json")
    artifact_count = validate_result(result, stages, names, member_digests, pins["stages"])
    require(artifact_count == archive_pin["declared_artifacts"], "artifact count differs")
    require(result.get("kappa") == pins["kappa"] and result.get("decimal") == pins["decimal"],
            "capsule selected value differs")
    promoted_hashes = {}
    for outer, inner in pins["promoted_receipts"].items():
        outer_data = repository_file("research/community-frontier1042-audit/" + outer)
        require(outer_data == roots[inner], "promoted receipt differs from capsule: " + outer)
        promoted_hashes[outer] = digest(outer_data)
    selected_pin = pins["selected_record"]
    selected = strict_json(package_file(selected_pin["path"], selected_pin["sha256"]), selected_pin["path"])
    require(selected.get("audited_source_head") == pins["audited_source_head"], "audited source head differs")
    require(selected.get("kappa") == pins["kappa"] and selected.get("decimal") == pins["decimal"],
            "published selected value differs")
    require(selected.get("certificate") == "research/community-frontier1042-audit/ASSEMBLY.json",
            "selected certificate path differs")
    require(selected.get("certificate_sha256") == promoted_hashes["ASSEMBLY.json"],
            "selected certificate digest differs")
    integration_pin = pins["integration_record"]
    integration = strict_json(repository_file(integration_pin["path"], integration_pin["sha256"]), integration_pin["path"])
    receipts = integration.get("receipts")
    require(type(receipts) is dict, "integration receipt map missing")
    require(receipts.get(archive_pin["path"]) == digest(archive_raw), "integration archive digest differs")
    for outer, expected in promoted_hashes.items():
        relative = "research/community-frontier1042-audit/" + outer
        require(receipts.get(relative) == expected, "integration promoted digest differs: " + outer)
    source_path = selected.get("source_manifest")
    source_data = repository_file(source_path)
    require(receipts.get(source_path) == digest(source_data), "integration source manifest digest differs")
    require(result.get("baseline_binding_sha256") == promoted_hashes["BASELINE-BINDING.json"],
            "capsule baseline binding differs")
    require(result.get("selected_assembly_sha256") == promoted_hashes["ASSEMBLY.json"],
            "capsule selected assembly binding differs")
    return {
        "status": "PASS_FRONTIER1042_CAPSULE_CLOSURE",
        "assignment_seed": pins["assignment_seed"], "base_commit": pins["base_commit"],
        "audited_source_head": pins["audited_source_head"], "kappa": pins["kappa"],
        "archive_sha256": digest(archive_raw), "members": len(names),
        "declared_artifacts": artifact_count, "expanded_bytes": expanded,
        "stages": len(stages), "promoted_receipts": len(promoted_hashes),
        "controls": ["C1_path_traversal", "C2_duplicate_member", "C3_nondeclared_member",
                     "C4_mutated_artifact_digest", "C5_nonzero_stage", "C6_promoted_receipt_mismatch"],
        "scope": "Independent standard-library, data-only finite closure audit of the frozen PR1042 selected replay capsule. Authenticates paths, complete bytes, receipt edges and publication pins; does not authenticate execution, replay construction code, all-size interfaces, analytic transfer or the multiplication theorem."
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path)
    ap.add_argument("--check", action="store_true",
                    help="require byte equality with the committed RESULT.json")
    args = ap.parse_args()
    pins = strict_json((HERE / "PINS.json").read_bytes(), "PINS.json")
    receipt = check(pins)
    raw = (json.dumps(receipt, indent=2) + "\n").encode()
    if args.check:
        require(raw == (HERE / "RESULT.json").read_bytes(), "committed receipt differs")
    if args.out:
        args.out.write_bytes(raw)
    print(raw.decode(), end="")
    print(receipt["status"])

if __name__ == "__main__":
    try:
        main()
    except (KeyError, OSError, ValueError, tarfile.TarError) as exc:
        raise SystemExit("FAIL: " + str(exc)) from exc
