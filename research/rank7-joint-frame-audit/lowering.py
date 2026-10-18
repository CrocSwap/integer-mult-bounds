# SPDX-License-Identifier: Apache-2.0
"""Reconstruct only declared frame edits. Scalar/operator data stay untouched."""

from copy import deepcopy

from frames import require, span


def difference(after, before):
    return {
        r: after.get(r, 0) - before.get(r, 0)
        for r in sorted(set(after) | set(before))
        if after.get(r, 0) != before.get(r, 0)
    }


def edit_groups(record):
    require(len(record["groups"]) == 5, "five groups")
    spaces = {name: span(tuple(pair[0])) for name, pair in record["groups"].items()}
    require(all(len(s) == 128 for s in spaces.values()), "rank-seven groups")
    require(len(record["frame_edits"]) == 139, "139 declared gate edits")
    grouped = {name: [] for name in spaces}
    seen = set()
    for edit in record["frame_edits"]:
        key = (edit["section"], edit["index"])
        require(key not in seen, "duplicate gate edit")
        seen.add(key)
        old, new = span(tuple(edit["old_frame"])), span(tuple(edit["new_frame"]))
        require(new < old and len(old) == 2 * len(new), "one-dimensional gate lowering")
        names = [name for name, space in spaces.items() if new <= space]
        require(len(names) == 1, "unambiguous edited-frame group")
        grouped[names[0]].append(edit)
    helpers = [h for _, hs in record["groups"].values() for h in hs]
    require(len(helpers) == len(set(helpers)) == 22, "22 distinct helpers")
    require(
        set(map(str, helpers)) == set(record["helper_final_changes"]),
        "endpoint edit coverage",
    )
    return grouped


def apply_frames(parent, record, names, endpoints=None):
    grouped = edit_groups(record)
    require(set(names) <= set(grouped), "known lowering groups")
    child = deepcopy(parent)
    lowered = set()
    for name in names:
        frame, helpers = record["groups"][name]
        chosen = set(helpers) if endpoints is None else set(endpoints)
        require(chosen <= set(helpers), "subset of group endpoints")
        for helper in sorted(chosen):
            change = record["helper_final_changes"][str(helper)]
            old = parent["helper_final"][str(helper)]
            require(
                old == change["old"] and change["new"] == frame, "endpoint preimage"
            )
            require(
                span(tuple(frame)) < span(tuple(old)) and len(old) == 8,
                "rank-eight to rank-seven endpoint",
            )
            child["helper_final"][str(helper)] = list(frame)
            lowered.add(helper)
        for edit in grouped[name]:
            section, index = edit["section"], edit["index"]
            require(
                section in ("A", "B", "restore") and 0 <= index < len(parent[section]),
                "gate edit address",
            )
            gate = parent[section][index]
            require(
                gate[:-1] == edit["gate"] and gate[-1] == edit["old_frame"],
                "gate edit preimage",
            )
            child[section][index][-1] = list(edit["new_frame"])
    changed = {key for key in parent if parent[key] != child[key]}
    require(
        changed <= {"helper_final", "A", "B", "restore"}, "frame-only changed fields"
    )
    for section in ("A", "B", "restore"):
        for old, new in zip(parent[section], child[section], strict=True):
            require(old[:-1] == new[:-1], "scalar/operator word unchanged")
            touched = new[1:3] if new[0] == "add" else new[1:2]
            for helper in set(touched) & lowered:
                require(
                    span(tuple(new[-1]))
                    <= span(tuple(child["helper_final"][str(helper)])),
                    "lowered helper gate fits endpoint",
                )
    require(child["cleanup"] == parent["cleanup"], "cleanup unchanged")
    return child
