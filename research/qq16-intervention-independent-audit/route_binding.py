#!/usr/bin/env python3
"""Bind QQ16 chart routes to the actual emitted stage/port map occurrences.

Standard-library independent source-binding audit; imports no predecessor code.
This checks owner matrices for the alignment blocks of all 37 F/B cases,
not scalar bodies, native phases, translations, or the full emitted operators.
Payload-constant witness fields make translations irrelevant to this audit.
Substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def expected_routes(phases):
    """Swap two orthonormal eight-frames using their projections directly."""
    m = phases["m"]
    recipes = phases["recipes"]
    require(m == 73 and len(recipes) == 112, "phase dimensions")
    routes = {}
    for p, recipe in enumerate(recipes):
        axes = recipe["idle_children"][0]["orthogonal_axes"][:8]
        frame = [recipe["q"], *axes]
        require(len(frame) == 9 and all(type(v) is int and 0 < v < 512 for v in frame),
                "local chart dimensions")
        require(all(((u & v).bit_count() % 2) == (i == j)
                    for i, u in enumerate(frame) for j, v in enumerate(frame)),
                "local chart orthonormality")
        routes[0, p] = tuple(1 << j for j in range(m))
        for s in range(1, 9):
            columns = []
            for j in range(m):
                v = 1 << j
                swapped = v
                for i, b in enumerate(axes):
                    e = 1 << (9 + 8 * (s - 1) + i)
                    # Remove the b/e components and reinsert them exchanged.
                    if ((v & b).bit_count() % 2) != bool(v & e):
                        swapped ^= b ^ e
                columns.append(swapped)
            routes[s, p] = tuple(columns)
    return routes


def check_bindings(packet, phases):
    routes = expected_routes(phases)
    maps, programs, params = (packet[k] for k in ("map_registry", "programs", "case_parameters"))
    T = packet["T_ports"]
    require(T == [21, 37, 47, 76, 81, 87, 92, 110], "selected T binding")
    expected_cases = {f"F_{s}" for s in range(9)} | {
        f"B_{s}_{t}" for s in range(1, 8) for t in range(s + 1, 9)}
    require(set(programs) == set(params) == expected_cases, "complete case domain")
    bindings = []

    def block(case, start, fields, stage, description):
        events = programs[case]
        require(start >= 0 and start + len(fields) <= len(events), "alignment bounds")
        for offset, field in enumerate(fields):
            index = start + offset
            event = events[index]
            require(len(event) == 5 and event[:2] == ["cover_map", ["L", field]],
                    f"{case}:{index}: {description} field/order")
            reference = event[2]
            require(reference in maps, f"{case}:{index}: missing map")
            columns = maps[reference]["owner_right_matrix_columns"]
            require(len(columns) == 73 and all(type(c) is int for c in columns),
                    f"{case}:{index}: matrix schema")
            port = field % 112
            require(tuple(columns) == routes[stage, port],
                    f"{case}:{index}: {description} stage/port owner matrix")
            bindings.append([case, index, field, stage, reference])

    f_names = ["X_A_fused_query", "X_T_query_subtract", "X_A_restore_selected",
               "X_T_sign", "X_U_query_subtract"]
    b_names = ["future_E_t", "Y_U_from_X_T", "eight_unsigned_swaps", "Y_T_query_subtract"]
    for case in sorted(expected_cases):
        events, param = programs[case], params[case]
        parts = case.split("_")
        stage = int(parts[1])
        kind = parts[0]
        require(param["stage"] == stage and param["orientation"] == kind,
                f"{case}: parameter binding")
        sweeps = [(i, e[1]) for i, e in enumerate(events) if e[0] == "cover_sweep"]
        cores = [e[:3] for e in events if e[0] == "retained_core"]
        require(cores == [["retained_core", "forward" if kind == "F" else "backward", stage]],
                f"{case}: retained core binding")
        if kind == "F":
            require([name for _, name in sweeps] == f_names, f"{case}: forward sweep order")
            first, last = sweeps[0][0], sweeps[-1][0]
            require(last - first == 4 and events[0][:3] == ["retained_core", "forward", stage],
                    f"{case}: forward block order")
            if stage == 0:
                require(first == 1, "F0 has identity alignment")
            else:
                require(first == 113, f"{case}: forward entry alignment")
                block(case, 1, list(range(112)), stage, "forward entry")
                block(case, last + 1, list(range(112)), stage, "forward exit")
        else:
            future = int(parts[2])
            require(param["future"] == future, f"{case}: future binding")
            require([name for _, name in sweeps] == b_names, f"{case}: backward sweep order")
            future_index, current_first, current_last = sweeps[0][0], sweeps[1][0], sweeps[-1][0]
            require(current_last - current_first == 2 and current_first == future_index + 233,
                    f"{case}: backward block order")
            ys = list(range(112, 224))
            block(case, future_index - 112, ys, future, "future entry")
            block(case, future_index + 1, ys, future, "future exit")
            block(case, current_first - 120, ys + T, stage, "current entry")
            block(case, current_last + 1, ys + T, stage, "current exit")

    require(len(bindings) == 14784, "complete alignment reference count")
    retained = {"F_0", "B_1_2", "F_2", "B_3_4", "F_4", "B_5_6", "F_6", "B_7_8", "F_8"}
    retained_bindings = sum(row[0] in retained for row in bindings)
    require(retained_bindings == 2752, "retained schedule alignment count")
    encoded = json.dumps(bindings, separators=(",", ":")).encode()
    return {
        "cases": 37,
        "phase_derived_stage_port_matrices": 1008,
        "positive_stage_alignment_references": len(bindings),
        "retained_nine_case_alignment_references": retained_bindings,
        "bindings_sha256": hashlib.sha256(encoded).hexdigest(),
        "scope": "Actual emitted alignment owner matrices; not native phases, scalar bodies or translations",
    }


def run_controls(packet, phases):
    """Change references only, preserving every registry matrix and key."""
    controls = []
    program = packet["programs"]["F_2"]
    e2, e8 = program[3], program[9]
    original2, original8 = e2[2], e8[2]

    def rejected(label, edit, undo):
        edit()
        try:
            try:
                check_bindings(packet, phases)
            except ValueError as exc:
                require("stage/port owner matrix" in str(exc), "control rejected for unexpected reason")
                controls.append(label)
            else:
                raise ValueError("control accepted: " + label)
        finally:
            undo()

    def swap():
        e2[2], e8[2] = original8, original2

    def restore():
        e2[2], e8[2] = original2, original8

    rejected("swap F2 port 2 and 8 map references within unchanged registry", swap, restore)
    wrong_stage = packet["programs"]["F_4"][3][2]
    rejected("use F4 port 2 map reference at F2 port 2", lambda: e2.__setitem__(2, wrong_stage), restore)
    # Positive representation control: map IDs are labels, not mathematics.
    alias = "audit_identical_matrix_alias"
    require(alias not in packet["map_registry"], "temporary alias collision")
    packet["map_registry"][alias] = packet["map_registry"][original2]
    e2[2] = alias
    try:
        check_bindings(packet, phases)
    finally:
        restore()
        del packet["map_registry"][alias]
    return {"rejecting_controls": controls, "positive_control": "identical map under a new registry ID"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument("phases", type=Path)
    args = parser.parse_args()
    packet = json.loads(gzip.decompress(args.packet.read_bytes()))
    phases = json.loads(args.phases.read_bytes())
    result = check_bindings(packet, phases)
    result.update(run_controls(packet, phases))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
