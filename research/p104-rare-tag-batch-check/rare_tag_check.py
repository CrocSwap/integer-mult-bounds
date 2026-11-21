#!/usr/bin/env python3
"""Independent finite review of the #7846 current-value rare-tag schedule.

The 5 x 5 x 5 case is deliberately unlike the author's four-wire Beneš
test.  Everything here is exact integer arithmetic, and the program compares
all 125 basis inputs with a simple sequential whole-axis implementation.
"""

from collections import defaultdict
from itertools import product
import json


L = 5
M = 3
E = ((0, 2), (1, 3, 4), (0, 1))
# Invertible matrices on the selected coordinates. Their complements are fixed.
MAT = (((1, 2), (3, 7)),
       ((1, 1, 0), (0, 1, 1), (1, 1, 2)),
       ((2, -1), (1, 0)))
P = tuple(product(range(L), repeat=M))
INDEX = {p: j for j, p in enumerate(P)}
B = 4  # a fixed square block width between the minimum class and its size


def demand(ok, reason):
    if not ok:
        raise ValueError(reason)


def at_axis(other, axis, x):
    out = list(other)
    out.insert(axis, x)
    return tuple(out)


def direct_axis(state, axis, cross_support=False):
    """Independent oracle: the complete source-axis matrix, line by line."""
    result = state.copy()
    selected = E[axis]
    for other in product(range(L), repeat=M-1):
        line = [state[INDEX[at_axis(other, axis, x)]] for x in range(L)]
        for out, x in enumerate(selected):
            val = sum(MAT[axis][out][col] * line[y]
                      for col, y in enumerate(selected))
            # A deliberately illegal extra matrix entry for the control below.
            if cross_support and axis == 0 and out == 0:
                val += line[1]  # coordinate 1 lies outside E[0]
            result[INDEX[at_axis(other, axis, x)]] = val
    return result


def direct_word(state, cross_support=False):
    for axis in range(M):
        state = direct_axis(state, axis, cross_support=cross_support)
    return state


def flag_set(pos):
    return tuple(j for j in range(M) if pos[j] in E[j])


def schedule_groups():
    # Groups retain the full mask, not just the visit number or axis. Each
    # group contains complete, pairwise-disjoint lines in one Cartesian class.
    groups = defaultdict(list)
    for axis in range(M):
        for other in product(range(L), repeat=M-1):
            point = at_axis(other, axis, E[axis][0])
            flags = flag_set(point)
            groups[(flags.index(axis), axis, flags)].append(other)
    return groups


def batch(lines, b=B):
    demand(len(lines) >= b, "underfilled flag-class batch")
    count, rem = divmod(len(lines), b)
    out = [lines[i*b:(i+1)*b] for i in range(count)]
    if rem:
        out[-1].extend(lines[count*b:])
    demand(all(b <= len(x) < 2*b for x in out), "bad batch size")
    demand(sum(map(len, out)) == len(lines), "lost or duplicated line")
    return out


GROUPS = schedule_groups()


def scheduled_word(state, *, stale=False):
    state = state.copy()
    initial = state.copy()
    # Within each pass all groups are disjoint. Every line is read immediately
    # before writing its result; changing to the initial snapshot is a control.
    for visit in range(M):
        for (j, axis, flags), lines in sorted(GROUPS.items()):
            if j != visit:
                continue
            for rows in batch(lines):
                for other in rows:
                    source = initial if stale else state
                    inputs = [source[INDEX[at_axis(other, axis, x)]]
                              for x in E[axis]]
                    for out, x in enumerate(E[axis]):
                        state[INDEX[at_axis(other, axis, x)]] = sum(
                            MAT[axis][out][col] * y for col, y in enumerate(inputs))
    return state


def check():
    demand(len(P) == L ** M, "wrong complete-field size")
    for axis in range(M):
        demand(len(set(E[axis])) == len(E[axis]), "duplicate selected coordinate")
        demand(min(len(E[axis]), L-len(E[axis])) >= 2, "side too small")
        demand(len(MAT[axis]) == len(E[axis]), "wrong row count")
        demand(all(len(row) == len(E[axis]) for row in MAT[axis]), "wrong column count")

    # Check the exact product formula and exhaustive coverage without relying
    # on the grouping algorithm for the expected counts.
    for (visit, axis, flags), lines in GROUPS.items():
        demand(flags[visit] == axis, "wrong flag visit")
        expected = 1
        for k in range(M):
            if k != axis:
                expected *= len(E[k]) if k in flags else L-len(E[k])
        demand(len(lines) == expected and len(set(lines)) == expected, "incorrect class size")
        demand(all(flag_set(at_axis(other, axis, x)) == flags
                   for other in lines for x in E[axis]), "line crosses a flag class")
        demand(len(lines) >= 2 ** (M-1) >= B, "full batch not guaranteed")

    all_visits = sum(len(lines)*len(E[axis])
                     for (_, axis, _), lines in GROUPS.items())
    demand(all_visits == sum(len(e)*L**(M-1) for e in E) == 175, "cell visit count")
    demand(sum(len(x) for x in GROUPS.values()) == M*L**(M-1) == 75, "line visit count")

    # The complete matrix comparison is enough for arbitrary rational and
    # complex inputs by linearity, for this fixed numerical example.
    compared = 0
    for j in range(len(P)):
        basis = [int(i == j) for i in range(len(P))]
        want, got = direct_word(basis), scheduled_word(basis)
        if got != want:
            raise ValueError((j, next(i for i in range(len(P)) if got[i] != want[i])))
        compared += len(P)

    dirty = [i + 1 for i in range(len(P))]
    want = direct_word(dirty)
    stale = scheduled_word(dirty, stale=True)
    crossed = direct_word(dirty, cross_support=True)
    stale_mismatches = sum(x != y for x, y in zip(want, stale))
    cross_mismatches = sum(x != y for x, y in zip(want, crossed))
    demand(stale_mismatches > 0 and cross_mismatches > 0, "fault control undetected")
    cross_source, cross_output = (1, 0, 0), (0, 0, 0)
    pulse = [int(pos == cross_source) for pos in P]
    legal_pulse = direct_axis(pulse, 0)
    illegal_pulse = direct_axis(pulse, 0, cross_support=True)
    demand(flag_set(cross_source) != flag_set(cross_output), "same flag witness")
    demand(legal_pulse[INDEX[cross_output]] == 0
           and illegal_pulse[INDEX[cross_output]] == 1, "cross-class pulse witness")

    # m=2 is a control against reading an eventual bound as an all-m bound:
    # with both E and its complement of size 2, a flag class has only 2 lines,
    # less than a desired block of 4, despite satisfying W=2.
    small_selected = ({0, 1}, {0, 1})
    short_lines = {(y,) for x, y in product(range(4), repeat=2)
                   if x in small_selected[0] and y in small_selected[1]}
    short_class = len(short_lines)
    demand(short_class == 2 and short_class < B, "two-axis control missing")
    underfilled_rejected = False
    try:
        batch(sorted(short_lines))
    except ValueError:
        underfilled_rejected = True
    demand(underfilled_rejected, "underfilled batch control accepted")
    out = {
        "status": "PASS_SCOPED_EXACT_RARE_TAG",
        "core_shape": [L]*M,
        "selected_sizes": list(map(len, E)),
        "minimum_side": 2,
        "block_width": B,
        "flag_axis_classes": len(GROUPS),
        "minimum_class_lines": min(map(len, GROUPS.values())),
        "maximum_class_lines": max(map(len, GROUPS.values())),
        "distinct_line_visits": sum(map(len, GROUPS.values())),
        "selected_cell_visits": all_visits,
        "bases": len(P),
        "matrix_coefficients_compared": compared,
        "stale_read_control_mismatches": stale_mismatches,
        "cross_support_control_mismatches": cross_mismatches,
        "two_axis_control_lines": short_class,
        "two_axis_desired_block": B,
        "two_axis_underfilled_rejected": underfilled_rejected,
        "cross_class_pulse": [list(cross_source), list(cross_output)],
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    check()
