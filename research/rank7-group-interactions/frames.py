# SPDX-License-Identifier: Apache-2.0
"""Finite frame accounting through orthogonal characters, not row reduction.

A frame is represented by the 512-bit indicator of its annihilator in F2^9.
No construction, producer, frame solver, or earlier auditor is imported.
"""

from collections import Counter
from functools import lru_cache


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(str(message))


ALL = (1 << 512) - 1
EVEN = tuple(
    sum(1 << n for n in range(512) if (n & v).bit_count() % 2 == 0)
    for v in range(512)
)


@lru_cache(maxsize=4096)
def annihilator(rows):
    result = ALL
    for row in rows:
        require(type(row) is int and 0 < row < 512, "nine-bit nonzero generator")
        result &= EVEN[row]
    return result


def frame(rows):
    return annihilator(tuple(rows))


def dimension(ann):
    size = ann.bit_count()
    require(size > 0 and size & (size - 1) == 0, "annihilator cardinality")
    return 9 - (size.bit_length() - 1)


def contained(small, big):
    return big & ~small == 0


def normalized(counter):
    return {str(r): n for r, n in sorted(counter.items()) if n}


def difference(left, right):
    result = Counter({int(r): n for r, n in left.items()})
    result.subtract({int(r): n for r, n in right.items()})
    return normalized(result)


def vertex(rows, flag=0, alternative=None):
    old = frame(rows)
    new = old if alternative is None else frame(alternative)
    return (old, new, flag if old != new else 0)


def selected(v, mask):
    return v[1] if v[2] & mask else v[0]


def charge(before, after, label):
    require(contained(before, after), ("nonmonotone", label))
    rank = dimension(after) - dimension(before)
    return Counter({rank: 1}) if rank else Counter()


def event_plan(word, record):
    """Bind the record to literal vertices, each depending on at most one group."""
    names = list(record["groups"])
    require(names == ["V45", "A", "B", "C", "D"], "five named groups")
    spaces = {n: frame(record["groups"][n][0]) for n in names}
    require(all(dimension(a) == 7 for a in spaces.values()), "rank-seven spaces")
    flags = {n: 1 << i for i, n in enumerate(names)}
    ends, edits = {}, {}
    for name, (_, helpers) in record["groups"].items():
        for helper in helpers:
            key = str(helper)
            require(key not in ends, "unique endpoint owner")
            change = record["helper_final_changes"][key]
            require(word["helper_final"][key] == change["old"], "endpoint preimage")
            old, new = frame(change["old"]), frame(change["new"])
            require(new == spaces[name] and contained(new, old), "endpoint subspace")
            require(dimension(old) == dimension(new) + 1, "endpoint codimension")
            ends[key] = vertex(change["old"], flags[name], change["new"])
    require(set(ends) == set(record["helper_final_changes"]), "all endpoint edits")
    for edit in record["frame_edits"]:
        section, index = edit["section"], edit["index"]
        key = (section, index)
        require(section in ("A", "B", "restore") and key not in edits, "unique gate edit")
        require(type(index) is int and 0 <= index < len(word[section]), "gate index")
        gate = word[section][index]
        require(gate[:-1] == edit["gate"] and gate[-1] == edit["old_frame"], "gate preimage")
        old, new = frame(edit["old_frame"]), frame(edit["new_frame"])
        owners = [n for n in names if contained(new, spaces[n])]
        require(len(owners) == 1, "unique gate-edit group")
        require(contained(new, old) and dimension(old) == dimension(new) + 1, "gate codimension")
        edits[key] = vertex(edit["old_frame"], flags[owners[0]], edit["new_frame"])
    require(len(ends) == 22 and len(edits) == 139, "complete stage-one edit counts")
    return names, ends, edits


def build_edges(word, record):
    """Construct every charged register edge, including fixed centre COPY costs."""
    names, replacements, edits = event_plan(word, record)
    require(len(word["ports"]) == 112, "112 source ports")
    starts = [vertex([p]) for p in word["ports"]] + [vertex([])] * 592
    ends = [vertex([1 << j for j in range(9)])] * 112
    ends += [(1 | (1 << p), 1 | (1 << p), 0) for p in word["ports"]]
    ends += [vertex([1 << j for j in range(9)])] * 480
    for key, rows in word["start_extra"].items():
        starts[int(key)] = vertex(rows)
    for key, rows in word["helper_final"].items():
        ends[int(key)] = replacements.get(key, vertex(rows))
    current = list(starts)
    edges, guards = [], []

    def climb(register, target, label):
        require(type(register) is int and 0 <= register < 704, "register domain")
        edges.append((label, register, current[register], target))
        current[register] = target

    def warp(register, before, after, label):
        expected = frame(before)
        guards.append((label, current[register], expected))
        current[register] = vertex(after)

    def section_step(section, index, gate):
        label = f"{section}:{index}"
        if gate[0] == "warp":
            warp(gate[1], gate[3], gate[4], label)
            return
        require(gate[0] in ("add", "scale"), "known scalar operation")
        target = edits.get((section, index), vertex(gate[-1]))
        registers = gate[1:3] if gate[0] == "add" else gate[1:2]
        for register in registers:
            climb(register, target, label)

    for index, gate in enumerate(word["A"]):
        section_step("A", index, gate)
    for register, rows in zip(word["centers"], word["center_frames"], strict=True):
        guards.append((f"center:{register}", current[register], frame(rows)))
        previous = vertex(rows)
        levels = {
            frame(word["target_levels"].get(str(gate[1] - 112), []))
            for gate in word["cut"] if gate[2] == register
        }
        for target in sorted(levels, key=lambda a: (-dimension(a), a)):
            # COPY goes down the nested chain; its positive child rank is the
            # reverse containment difference. The register itself stays put.
            new = (target, target, 0)
            edges.append((f"copy:{register}", register, new, previous))
            previous = new
    by_position = {}
    for item in word["warps"]:
        by_position.setdefault(item[0], []).append(item)
    require(all(0 <= p <= len(word["B"]) for p in by_position), "B warp position")
    for position in range(len(word["B"]) + 1):
        for item in by_position.get(position, []):
            warp(item[1], item[3], item[4], f"B-warp:{position}")
        if position < len(word["B"]):
            section_step("B", position, word["B"][position])
    for index, gate in enumerate(word["restore"]):
        section_step("restore", index, gate)
    live = sorted(set(range(704)) - set(word["removed"]))
    for register in live:
        climb(register, ends[register], "end")
    widths = [(r, starts[r], ends[r]) for r in live if r >= 224]
    return names, edges, guards, widths


def evaluate(edges, guards, widths, mask):
    paid, inventory = Counter(), Counter()
    for label, current, expected in guards:
        require(selected(current, mask) == expected, ("warp/center entrance", label))
    for label, register, before, after in edges:
        paid.update(charge(selected(before, mask), selected(after, mask), (label, register)))
    for register, start, end in widths:
        a, b = selected(start, mask), selected(end, mask)
        require(contained(a, b), ("entrance-relative width", register))
        inventory[dimension(b) - dimension(a)] += 1
    return normalized(paid), normalized(inventory)
