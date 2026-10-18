# SPDX-License-Identifier: Apache-2.0
"""Independent direct-event inventory for PR2979 helper249/private953."""
import json

HELPER = 249
PRIVATE = 953
W = [256, 128, 64, 35, 16, 11, 5]
FULL = [256, 128, 64, 32, 16, 8, 4, 2, 1]
PHASES = ["zero_frame_precondition", "entry_adapters", "A", "centers", "B",
          "cleanup_tail", "final", "exit_adapters", "full_frame_cleanup", "done"]


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def same(a, b):
    return json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def frame(frames, index):
    require(type(index) is int and 0 <= index < len(frames), "frame ID contract")
    return frames[index]


def operands(gate):
    require(gate[0] in ("add", "scale", "warp"), "source gate kind")
    return gate[1:3] if gate[0] == "add" else gate[1:2]


def source_boundary(word, canonical):
    require(all(len(word[s]) <= 10_000 for s in
                ("A", "B", "restore", "cleanup", "precondition", "compensation", "cut")),
            "source section capacity")
    require(len(word["initial_corrections"]) <= 704 and len(word["warps"]) <= 512,
            "source auxiliary capacity")
    require(word["report"]["v"] == 112 and word["report"]["R"] == 480,
            "source domain")
    kept = [r for r in range(704) if r not in word["removed"]]
    require(len(kept) == 632 and same(canonical["helper_origin"], kept[224:]),
            "literal compact register mapping")
    require(canonical["v"] == 112 and canonical["R"] == 408, "canonical domain")
    require(same(word["helper_final"][str(HELPER)], W), "source endpoint")
    require(str(HELPER) not in word["start_extra"], "cold entrance")
    require(HELPER not in word["centers"], "helper is not a center")
    require(all(w[1] != HELPER for w in word["warps"]), "helper is not a lender")
    for section in ("precondition", "compensation", "cut"):
        require(all(HELPER not in operands(g) and PRIVATE not in operands(g)
                    for g in word[section]), "uncovered source section")
    require(all(HELPER not in (c["source"], c["target"]) and
                PRIVATE not in (c["source"], c["target"])
                for c in word["initial_corrections"]), "uncovered correction")
    r = kept.index(HELPER)
    frames = canonical["frames"]
    require(len(frames) <= 4096 and same(frames[0], []) and same(frames[1], FULL),
            "canonical frame conventions")
    terminal = canonical["final"][r]
    require(type(canonical["start"][r]) is int and canonical["start"][r] == 0
            and same(frame(frames, terminal), W),
            "canonical residual pair")
    require(r in canonical["zero_buffers"], "declared private buffer")
    return kept, r, terminal


def expected(word):
    """Source frame/gate inventory with scalar clocks, independent of frame IDs."""
    rows = [["entry_adapters", 0, ["wrapper", "pre", [], W]]]
    current = []
    for section, phase in (("A", "A"), ("B", "B"),
                           ("restore", "cleanup_tail"), ("cleanup", "full_frame_cleanup")):
        require(len(word[section]) <= 10_000, "source gate capacity")
        clock = 0
        if section == "cleanup":
            rows.append([phase, 0, ["buffer", "alloc"]])
        for gate in word[section]:
            regs = operands(gate)
            if HELPER in regs or PRIVATE in regs:
                require(gate[0] != "warp", "no direct warp in covered source")
                require((section == "cleanup") == (PRIVATE in regs), "private scope")
                if HELPER in regs and not same(current, gate[-1]):
                    rows.append([phase, clock, ["climb", current, gate[-1],
                                               len(gate[-1]) - len(current)]])
                    current = gate[-1]
                rows.append([phase, clock, ["scalar", gate[:-1], gate[-1]]])
            if gate[0] != "warp":
                clock += 1
        if section == "cleanup":
            rows += [[phase, clock, ["buffer", "free"]],
                     [phase, clock, ["wrapper", "post", [], W]]]
    require(same(current, W), "source reaches endpoint without final climb")
    return rows


def scalar(operation, kept, backward):
    sizes = {"clear": 2, "copy": 3, "scale": 4, "add": 5}
    require(operation[0] in sizes and len(operation) == sizes[operation[0]],
            "scalar schema")
    count = 2 if operation[0] in ("add", "copy") else 1
    regs = []
    for tag, r in operation[1:1 + count]:
        require(type(r) is int and 0 <= r < len(kept), "compact role range")
        require(tag in ("L", "Z", "C"), "role namespace")
        regs.append(kept[r] + (704 if tag == "Z" else 0) if tag != "C" else -1)
    result = [operation[0], *regs, *operation[1 + count:]]
    if result[0] in ("add", "scale"):
        a, b = result[-2:]
        require(type(a) is int and type(b) is int and a != 0 and b != 0,
                "scalar rational contract")
    if backward and result[0] == "add":
        result[1], result[2] = result[2], result[1]
        result[3] = -result[3]
    elif backward and result[0] == "scale":
        result[2], result[3] = result[3], result[2]
    return result


def direct(event, frames, kept, r, backward):
    """Normalize a covered event; reject unsupported direct operations."""
    tag = event[0]
    if tag == "scalar":
        require(len(event) == 3, "scalar event schema")
        op = scalar(event[1], kept, backward)
        count = 2 if op[0] in ("add", "copy") else 1
        if any(x in (HELPER, PRIVATE) for x in op[1:1 + count]):
            return ["scalar", op, frame(frames, event[2])]
    elif tag == "climb" and event[2] == r:
        require(len(event) == 6, "climb schema")
        require(all(type(x) is int for x in event[2:]), "climb integer fields")
        return ["climb", frame(frames, event[3]), frame(frames, event[4]), event[5]]
    elif tag == "residual_adapter" and event[2] == r:
        require(len(event) == 5, "cold wrapper must name terminal")
        require(type(event[3]) is int and type(event[4]) is int, "wrapper frame types")
        return ["wrapper", event[1], frame(frames, event[3]), frame(frames, event[4])]
    elif tag == "zero_buffer" and event[2] == r:
        require(len(event) == 3, "buffer schema")
        return ["buffer", event[1]]
    elif tag == "warp":
        require(event[1] not in (["L", r], ["Z", r]), "unexpected direct warp")
    elif tag == "adapter":
        require(event[2] != r, "ordinary adapter substituted for cold wrapper")
    return None


def check(word, canonical, stream, backward):
    kept, r, terminal = source_boundary(word, canonical)
    require(len(stream) <= 100_000, "event capacity")
    frames = canonical["frames"]
    rows, indices, phases, clock = [], [], [], 0
    for index, event in enumerate(stream):
        require(type(event) is list and event, "event schema")
        tag = event[0]
        require(tag in ("phase", "scalar", "climb", "residual_adapter", "zero_buffer",
                        "warp", "adapter", "center"), "unknown event tag")
        if tag == "phase":
            phases.append(event[1])
            require(phases == PHASES[:len(phases)], "phase chronology")
            clock = 0
            continue
        require(phases, "event before first phase")
        row = direct(event, frames, kept, r, backward)
        if row is not None:
            require(tag != "climb" or event[1] == phases[-1], "climb phase tag")
            # The entry pre-wrapper has no scalar predecessor in its phase.
            rows.append([phases[-1], clock, row])
            indices.append(index)
        if tag == "scalar":
            clock += 1
    require(phases == PHASES, "complete phase trace")
    require(same(rows, expected(word)), "direct event inventory/chronology mismatch")
    return {"compact_helper": r, "recipe_key": f"0:{terminal}",
            "events": len(stream), "covered_events": len(rows),
            "event_indices": indices, "inventory": rows}
