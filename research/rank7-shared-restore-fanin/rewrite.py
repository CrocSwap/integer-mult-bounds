# SPDX-License-Identifier: Apache-2.0
"""One shared dirty-source covector across two separated restore consumers."""

import copy

LOW = [256, 128, 64, 34, 17, 11, 4]
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
HIGH = [256, 128, 64, 34, 16, 10, 4, 1]
LOCAL = {"1": 2441, "2": 708, "3": 232, "4": 108, "5": 18, "8": 8}
INVENTORY = {"4": 26, "5": 2, "6": 16, "7": 52, "8": 99, "9": 213}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def r1(word, specification, variant):
    """Apply Jeremy Kothe's literal R1, retaining its exact source preimage."""
    edit = specification["edits"][variant][0]
    need(len(specification["edits"][variant]) == 1, "one credited R1 edit")
    need(
        (edit["section"], edit["start"], edit["stop"]) == ("restore", 178, 180),
        "R1 source address",
    )
    need(word["restore"][178:180] == edit["old"], "R1 literal preimage")
    changed = copy.deepcopy(word)
    changed["restore"][178:180] = copy.deepcopy(edit["new"])
    return changed


def r2(word):
    """Aggregate X40-2*X54, use it twice, and restore both dirty sources."""
    old = word["restore"]
    need(len(old) in (203, 204), "bounded parent or R1 restore")
    expected = {
        162: ["add", 18, 40, 1, 1],
        163: ["add", 18, 54, -2, 1],
        175: ["add", 22, 40, 1, 1],
        177: ["add", 22, 54, -2, 1],
    }
    for index, gate in expected.items():
        need(old[index] == gate + [HIGH], "literal R2 preimage at " + str(index))
    need(
        old[176] == ["add", 22, 45, -1, 1, HIGH], "literal commuting consumer preimage"
    )
    # Only these four source contacts may occur after the aggregation point.
    contacts = [
        i for i in range(162, len(old)) if any(r in (40, 54) for r in old[i][1:3])
    ]
    need(contacts == list(expected), "no intervening source observer or writer")
    changed = copy.deepcopy(word)
    gates = [copy.deepcopy(g) for i, g in enumerate(old) if i not in (163, 177)]
    gates.insert(162, ["add", 40, 54, -2, 1, LOW.copy()])
    gates.append(["add", 40, 54, 2, 1, FULL.copy()])
    changed["restore"] = gates
    need(len(gates) == len(old), "R2 preserves scalar gate count")
    return changed


def finish(word, original, frames):
    """Re-derive both paid profiles and the complete inverse cleanup."""
    profile, inventory = frames.frame_report(word)
    need(inventory == INVENTORY, "unchanged helper widths")
    word["report"]["local_profile"] = profile
    word["report"]["width_inventory"] = inventory
    forward = copy.deepcopy(word)
    forward["A"] = forward["A"][forward["prelude_events"] :]
    word["cleanup"] = frames.derive_cleanup(forward, frames.restored_of(original))
    changes = {key for key in original if original[key] != word[key]}
    need(changes <= {"restore", "report", "cleanup"}, "only declared sections change")
    need(len(word["helper_final"]) == 91, "all private buffers retained")
    return word


def stage_spec(original, composed):
    """Encode R1+R2 for PR3015's unchanged declared-edit source builder."""
    # The combined hunk is necessary because R2's second deletion adjoins R1.
    return [
        {
            "id": "R1+R2-shared-consumers",
            "section": "restore",
            "start": 162,
            "stop": 180,
            "old": original["restore"][162:180],
            "new": composed["restore"][162:180],
        },
        {
            "id": "R2-full-source-restoration",
            "section": "restore",
            "start": 203,
            "stop": 203,
            "old": [],
            "new": [composed["restore"][-1]],
        },
    ]
