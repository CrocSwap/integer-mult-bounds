#!/usr/bin/env python3
"""Read the channel schedule behind the published 208-flag matching.

Sources are the X registers and targets are the Y registers in the pinned
geometry. This scan does not rebuild the matching and does not import that
module.
"""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = (
    "PASS_P104_FLAG_CHANNEL_SCHEDULE flags=208 joint_events=0 "
    "targets_before_sources no_new_kappa"
)


def fail(message):
    raise SystemExit("FAIL_P104_FLAG_CHANNEL_SCHEDULE " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    expected = {
        "research/p104-joint-unit-flags/CERTIFICATE.json",
        "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
        "research/p104-endpoint-geometric-budget/geometry.py",
    }
    require(set(pinned) == expected, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def register(item):
    if isinstance(item, str) and len(item) > 1 and item[0] in "XY" and item[1:].isdigit():
        return item
    return None


def schedule(program):
    first, last = {}, {}
    joint = 0
    for index, event in enumerate(program):
        names = [name for item in event if (name := register(item))]
        kinds = {name[0] for name in names}
        if "X" in kinds and "Y" in kinds:
            joint += 1
        for name in names:
            first.setdefault(name, index)
            last[name] = index
    return first, last, joint


def coefficients(program, name):
    found = []
    for event in program:
        if event[0] == "add" and name in (register(event[1]), register(event[2])):
            found.append(str(event[3]))
    return sorted(set(found), key=lambda item: (item[0] == "-", item))


def evaluate():
    authenticate()
    geometry = (ROOT / "research/p104-endpoint-geometric-budget/geometry.py").read_text(encoding="utf-8")
    require("sources = [paths[f'X{s}'] for s in range(104)]" in geometry, "source naming left the geometry")
    require("targets = [paths[f'Y{t}'] for t in range(104)]" in geometry, "target naming left the geometry")
    certificate = json.loads((ROOT / "research/p104-joint-unit-flags/CERTIFICATE.json").read_text(encoding="utf-8"))
    witness = json.loads((ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json").read_text(encoding="utf-8"))
    helpers = certificate["helpers"]
    program = witness["program"]
    require(len(helpers) == 208 and len(program) == 4058, "the published sizes changed")
    flag = helpers[0]
    require(flag["source"] == 0 and flag["target"] == 34 and flag["basis"][0] == 232, "flag 0 changed")
    first, last, joint = schedule(program)
    sources = [f"X{i}" for i in range(104)]
    targets = [f"Y{i}" for i in range(104)]
    require(set(sources) <= set(first) and set(targets) <= set(first), "a register never appears")
    source_first = min(first[name] for name in sources)
    target_last_first = max(first[name] for name in targets)
    require(target_last_first < source_first, "some source appears before every target")
    require(joint == 0, "an event names both a source and a target")
    matched_joint = sum(1 for row in helpers if first[f"X{row['source']}"] == first[f"Y{row['target']}"])
    require(all(first[f"Y{row['target']}"] < first[f"X{row['source']}"] for row in helpers), "a matched target waits for its source")
    source, target = "X0", "Y34"
    require(witness["initial_frames"][source] == [232], "X0 does not start at the flag head")
    require(witness["initial_frames"][source] != witness["final_frames"][source], "X0 is restored")
    require(witness["initial_frames"][target] != witness["final_frames"][target], "Y34 is restored")
    require(232 in witness["final_frames"][target], "Y34 does not end with the flag head")
    return {
        "flags": 208,
        "program_events": 4058,
        "joint_source_target_events": joint,
        "matched_pairs_with_target_first": 208,
        "earliest_source_event": source_first,
        "latest_target_first_event": target_last_first,
        "flag0": {
            "source": 0,
            "target": 34,
            "basis_head": 232,
            "source_events": [first[source], last[source]],
            "target_events": [first[target], last[target]],
            "source_coefficients": coefficients(program, source),
            "target_coefficients": coefficients(program, target),
            "source_initial": witness["initial_frames"][source],
            "source_final": witness["final_frames"][source],
            "target_final_contains_basis_head": True,
            "restored": False,
        },
        "matched_same_first_event": matched_joint,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution: " + json.dumps(observed, sort_keys=True))
    print(MARKER)


if __name__ == "__main__":
    main()
