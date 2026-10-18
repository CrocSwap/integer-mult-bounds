# SPDX-License-Identifier: Apache-2.0
"""Explicit subsets of F2^9, not a Gaussian-elimination basis implementation.

Independently implements the finite frame contract stated by PR2979 and its
PR2917/PR2894 lineage. No predecessor module is imported or executed.
"""

from collections import Counter
from functools import lru_cache


class Invalid(ValueError):
    """The literal word violates the scoped frame or cleanup contract."""


def require(condition, label):
    if not condition:
        raise Invalid(str(label))


@lru_cache(maxsize=4096)
def span(vectors):
    require(len(vectors) <= 9, "at most nine frame generators")
    points = {0}
    for vector in vectors:
        require(type(vector) is int and 0 < vector < 512, "nine-bit generator")
        points |= {point ^ vector for point in points}
    require(len(points) == 1 << len(vectors), "independent frame generators")
    return frozenset(points)


def dimension(space):
    return len(space).bit_length() - 1


ZERO = span(())
FULL = span(tuple(1 << bit for bit in range(9)))


def roles(gate):
    require(gate[0] in ("add", "scale"), "scalar gate kind")
    expected = 6 if gate[0] == "add" else 5
    require(len(gate) == expected, "scalar gate shape")
    result = gate[1:3] if gate[0] == "add" else gate[1:2]
    require(all(type(r) is int and 0 <= r < 704 for r in result), "register range")
    return result


def boundaries(word):
    require(
        (word["report"]["v"], word["report"]["h"], word["report"]["R"])
        == (112, 9, 480),
        "fixed geometry",
    )
    ports = word["ports"]
    require(len(ports) == len(set(ports)) == 112, "112 unique ports")
    starts = [span((p,)) for p in ports] + [ZERO] * 592
    ends = (
        [FULL] * 112
        + [
            frozenset(x for x in range(512) if (x & p).bit_count() % 2 == 0)
            for p in ports
        ]
        + [FULL] * 480
    )
    for field, frames in (("start_extra", starts), ("helper_final", ends)):
        require(len(word[field]) <= 480, "bounded helper boundary")
        for role, vectors in word[field].items():
            require(224 <= int(role) < 704, "helper boundary register")
            frames[int(role)] = span(tuple(vectors))
    live = set(range(704)) - set(word["removed"])
    require(len(live) == 632 and set(range(224)) <= live, "live geometry")
    widths = Counter()
    for role in sorted(live - set(range(224))):
        require(starts[role] <= ends[role], "entrance inside terminal frame")
        widths[dimension(ends[role]) - dimension(starts[role])] += 1
    return starts, ends, live, dict(sorted(widths.items()))


def climb(current, paid, events, location, role, destination):
    source = current[role]
    require(source <= destination, ("nonmonotone", location, role))
    rank = dimension(destination) - dimension(source)
    if rank:
        paid[rank] += 1
        events.append(
            [*location, role, dimension(source), dimension(destination), rank]
        )
    current[role] = destination


def linear_image(columns, point):
    result = 0
    for bit in range(9):
        if point & (1 << bit):
            result ^= columns[bit]
    return result


def warp(current, role, columns, old, new, inverse=False):
    require(
        len(columns) == 9 and all(type(x) is int and 0 <= x < 512 for x in columns),
        "warp columns",
    )
    old, new = span(tuple(old)), span(tuple(new))
    require(
        len({linear_image(columns, x) for x in range(512)}) == 512, "invertible warp"
    )
    require(frozenset(linear_image(columns, x) for x in old) == new, "warp image")
    source, target = (new, old) if inverse else (old, new)
    require(current[role] == source, "warp entrance frame")
    current[role] = target


def scalar_step(word, current, paid, events, section, index, gate):
    if gate[0] == "warp":
        require(len(gate) == 5, "A warp shape")
        role, operator, old, new = gate[1:]
        require(0 < abs(operator) <= len(word["warps"]), "A warp operator")
        columns = word["warps"][abs(operator) - 1][2]
        # The A gate declares its chronological source/target, even for G^-1.
        if operator < 0:
            warp(current, role, columns, new, old, inverse=True)
        else:
            warp(current, role, columns, old, new)
        return
    destination = span(tuple(gate[-1]))
    for role in roles(gate):
        climb(current, paid, events, (section, index), role, destination)


def centre_copies(word, current, paid, events):
    require(len(word["centers"]) == len(word["center_frames"]) == 8, "eight centres")
    for index, (role, frame) in enumerate(
        zip(word["centers"], word["center_frames"], strict=True)
    ):
        source = span(tuple(frame))
        require(current[role] == source, "centre entrance")
        readers = {
            span(tuple(word["target_levels"].get(str(g[1] - 112), [])))
            for g in word["cut"]
            if g[2] == role
        }
        for target in sorted(readers, key=lambda s: (-len(s), tuple(sorted(s)))):
            require(target <= source, "nested centre copy levels")
            rank = dimension(source) - dimension(target)
            if rank:
                paid[rank] += 1
                events.append(
                    ["centre", index, role, dimension(source), dimension(target), rank]
                )
            source = target
        # These are copied readout paths. The main carrier frame is unchanged.


def ledger(word, check_report=True):
    for section in ("A", "B", "restore", "cut", "cleanup"):
        require(len(word[section]) <= 10000, "bounded section")
    require(len(word["warps"]) <= 480, "bounded warps")
    current, ends, live, widths = boundaries(word)
    paid, events = Counter(), []
    for index, gate in enumerate(word["A"]):
        scalar_step(word, current, paid, events, "A", index, gate)
    for target in range(112):
        require(
            current[112 + target]
            == span(tuple(word["target_levels"].get(str(target), []))),
            "target level",
        )
    centre_copies(word, current, paid, events)
    by_position = {}
    for position, role, columns, old, new in word["warps"]:
        require(0 <= position <= len(word["B"]), "B warp position")
        by_position.setdefault(position, []).append((role, columns, old, new))
    for index in range(len(word["B"]) + 1):
        for role, columns, old, new in by_position.get(index, []):
            warp(current, role, columns, old, new)
        if index < len(word["B"]):
            scalar_step(word, current, paid, events, "B", index, word["B"][index])
    for index, gate in enumerate(word["restore"]):
        scalar_step(word, current, paid, events, "restore", index, gate)
    for role in sorted(live):
        climb(current, paid, events, ("end", role), role, ends[role])
    profile = dict(sorted(paid.items()))
    if check_report:
        require(
            profile == {int(r): n for r, n in word["report"]["local_profile"].items()},
            "paid report mismatch",
        )
        require(
            widths == {int(r): n for r, n in word["report"]["width_inventory"].items()},
            "width report mismatch",
        )
    return {"profile": profile, "widths": widths, "events": events}


def cleanup_namespace(word):
    """Check the literal reverse/inverse syntax and names, not zero-return semantics."""
    require(0 <= word["prelude_events"] <= len(word["A"]), "prelude length")
    restored = {int(h) for h in word["helper_final"]}
    by_position = {}
    for operator, record in enumerate(word["warps"], 1):
        by_position.setdefault(record[0], []).append(["warp", record[1], operator])
    forward = list(word["A"][word["prelude_events"] :])
    for index in range(len(word["B"]) + 1):
        forward.extend(by_position.get(index, []))
        if index < len(word["B"]):
            forward.append(word["B"][index])
    forward.extend(word["restore"])
    inverse = []
    for gate in reversed(forward):
        if 112 <= gate[1] < 224:
            continue
        kind, role = gate[:2]
        target = role + 704 if role in restored else role
        if kind == "warp":
            inverse.append(["warp", target, -gate[2]])
        elif kind == "add":
            source = gate[2] + 704 if gate[2] in restored else gate[2]
            inverse.append(["add", target, source, -gate[3], gate[4]])
        else:
            require(kind == "scale", "inverse gate kind")
            inverse.append(["scale", target, gate[3], gate[2]])
    require(len(inverse) == len(word["cleanup"]), "cleanup length")
    require(inverse == [g[:-1] for g in word["cleanup"]], "inverse cleanup syntax")
    require(
        all(span(tuple(g[-1])) == FULL for g in word["cleanup"]), "full cleanup frame"
    )
    private = {
        r
        for g in word["cleanup"]
        for r in (g[1:3] if g[0] == "add" else g[1:2])
        if r >= 704
    }
    require(private == {704 + h for h in restored}, "cleanup endpoint/buffer bijection")
    return {"private_buffers": len(private), "cleanup_gates": len(inverse)}
