# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Primary column-code census. E8 model adapted from PR1226/PR968."""
from collections import Counter
import hashlib
import itertools
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def model():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si in (1, -1):
            for sj in (1, -1):
                row = [0] * 8
                row[i], row[j] = 2 * si, 2 * sj
                roots.append(tuple(row))
    for row in itertools.product((1, -1), repeat=8):
        if row.count(-1) % 2 == 0:
            roots.append(row)
    lines, seen = [], set()
    for root in roots:
        key = max(root, tuple(-x for x in root))
        if key not in seen:
            seen.add(key)
            lines.append(root)
    frame = []
    for a in range(4):
        for sign in (1, -1):
            root = [0] * 8
            root[2*a], root[2*a+1] = 2, 2*sign
            frame.append(lines.index(tuple(root)))
    return {"lines": [list(r) for r in lines], "punctured_frame": frame,
            "live": [i for i in range(120) if i not in frame]}


def pairing(data):
    lines = data["lines"]
    ip = []
    for a in lines:
        row = []
        for b in lines:
            value = sum(x*y for x, y in zip(a, b))
            need(value % 4 == 0, "nonintegral root inner product")
            row.append(value // 4)
        ip.append(row)
    nrows = [sum(((ip[i][j]+1) % 2) << j for j in range(120)) for i in range(120)]
    return ip, nrows


def supports(data, ip):
    live = data["live"]
    result = []
    for alpha in range(120):
        mask = sum(1 << i for i in live if ip[i][alpha] != 0)
        result.extend((mask, mask & ~(1 << alpha)))
    return result


def basis(vectors):
    pivots = {}
    for value in vectors:
        while value:
            pivot = value.bit_length()-1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return tuple(pivots.values())


def cost(nrows, left, right):
    return len(basis(nrows[i] & right for i in bits(left)))


def analyze_code(code, left, right, nrows):
    weights = {i: (nrows[i] & right).bit_count() for i in bits(left)}
    values = [(v.bit_count(), sum(weights[i] for i in bits(v)), v) for v in code]
    d = min(x[0] for x in values)
    w = min(x[1] for x in values)
    dm = min((x for x in values if x[0] == d), key=lambda x: (x[1], x[2]))[2]
    wm = min((x for x in values if x[1] == w), key=lambda x: (x[0], x[2]))[2]
    digest = hashlib.sha256("".join(format(v, "x")+"\n" for v in sorted(code)).encode()).hexdigest()
    return [d, w, format(dm, "x"), format(wm, "x"),
            sum(x[0] == d for x in values), sum(x[1] == w for x in values), digest]


def census(data):
    ip, nrows = pairing(data)
    sup = supports(data, ip)
    histogram, table = Counter(), []
    for a, left in enumerate(sup):
        for b, right in enumerate(sup):
            rank = cost(nrows, left, right)
            histogram[str(rank)] += 1
            if rank != 7:
                continue
            columns = basis(nrows[j] & left for j in bits(right))
            need(len(columns) == 7, "row/column rank disagreement")
            code = [0]
            for column in columns:
                code += [v ^ column for v in code]
            code.remove(0)
            need(len(code) == len(set(code)) == 127, "incomplete rank-seven code")
            record = [a, b, *analyze_code(code, left, right, nrows)]
            for index in (4, 5):
                cut = int(record[index], 16)
                need(cost(nrows, left & ~cut, right) == 6, "minimum cut does not attain rank six")
            table.append(record)
    return dict(sorted(histogram.items())), table


def frames(data, ip):
    live_mask = sum(1 << i for i in data["live"])
    adjacent = [sum(1 << j for j in data["live"] if j != i and ip[i][j] == 0) for i in range(120)]
    result = []
    def extend(chosen, candidates):
        if len(chosen) == 8:
            result.append(tuple(chosen))
            return
        while candidates:
            if candidates.bit_count() < 8-len(chosen):
                break
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length()-1
            extend(chosen+[vertex], candidates & adjacent[vertex])
    extend([], live_mask)
    return result


def table_bytes(table):
    return ("".join(json.dumps(row, separators=(",", ":"))+"\n" for row in table)).encode()


def summarize(data, histogram, table):
    lookup = {(r[0], r[1]): r for r in table}
    ip, nrows = pairing(data)
    sup = supports(data, ip)
    row_d = Counter(r[2] for r in table)
    joint_d = Counter(min(r[2], lookup[r[1], r[0]][2]) for r in table)
    joint_w = Counter(min(r[3], lookup[r[1], r[0]][3]) for r in table)
    fs = frames(data, ip)
    need(len(fs) == 1260, "live frame census changed")
    counts = Counter(i for frame in fs for i in frame)
    need(set(counts) == set(data["live"]) and set(counts.values()) == {90}, "frame incidence changed")
    used = set(r[i] for r in table for i in (0, 1))
    frame_masks = [sum(1 << i for i in frame) for frame in fs]
    hits = {}
    for a in used:
        need(a % 2 == 1 or a//2 in data["punctured_frame"], "cost-seven untrimmed live normal")
        intersections = [(sup[a] & frame).bit_count() for frame in frame_masks]
        need(all(size in (0, 4) for size in intersections),
             "cheap star/frame intersection not zero or four")
        hits[a] = sum(1 << i for i, size in enumerate(intersections) if size)
        need(hits[a].bit_count() >= 1170, "cheap factor misses more than ninety frames")
    need(all((hits[r[0]] & hits[r[1]]).bit_count() >= 1080 for r in table),
         "a rank-seven parent lacks the required frame witness")
    order = lambda row: ((row[0]-46) % 240, (row[1]-46) % 240)
    selected = min((r for r in table if r[2] == 20 and r[3] == 560), key=order)
    a, b = selected[:2]
    left, right = sup[a], sup[b]
    cut = int(selected[4], 16)
    wcut = int(selected[5], 16)
    met = [f for f in fs if left & sum(1 << i for i in f) and right & sum(1 << i for i in f)]
    frame = met[0]
    fmask = sum(1 << i for i in frame)
    geometry_cut = left & fmask
    need(geometry_cut.bit_count() == 4 and cost(nrows, left & ~geometry_cut, right) == 7,
         "frame-change witness also changes copied rank")
    after_hit = sum(bool((left & ~geometry_cut) & sum(1 << i for i in f)) and
                    bool(right & sum(1 << i for i in f)) for f in fs)
    need(after_hit < len(met), "four-deletion frame witness loses no frame")
    return {
        "status": "PASS_P112_STAR_FIRST_COST_DROP",
        "assignment_seed": 46, "lines": 120, "live_lines": 112, "tagged_supports": 240,
        "distinct_supports": len(set(sup)), "ordered_parent_pairs": 57600,
        "parent_pair_rank_histogram": histogram, "rank7_tagged_pairs": len(table),
        "rank7_distinct_support_pairs": len({(sup[r[0]], sup[r[1]]) for r in table}),
        "nonzero_column_codewords_per_orientation": 127, "completed_codewords": 127*len(table),
        "row_first_drop_histogram": dict(sorted(row_d.items())),
        "joint_first_drop_histogram": dict(sorted(joint_d.items())),
        "joint_even_position_loss_histogram": dict(sorted(joint_w.items())),
        "global_first_copy_drop": min(joint_d), "global_even_position_loss_floor": min(joint_w),
        "table_sha256": hashlib.sha256(table_bytes(table)).hexdigest(),
        "live_frames": len(fs), "frames_per_line": 90, "first_frame_hit_change": 4,
        "witness": {"left_tag": a, "right_tag": b, "left_normal": a//2, "right_normal": b//2,
                    "deleted_rows": list(bits(cut)), "row_rank_after": cost(nrows, left & ~cut, right),
                    "even_positions_removed": sum((nrows[i] & right).bit_count() for i in bits(cut)),
                    "minimum_even_loss_deleted_rows": list(bits(wcut)),
                    "frame": list(frame), "frame_change_deleted_rows": list(bits(geometry_cut)),
                    "frame_change_rank": 7, "frames_met_before": len(met), "frames_met_after": after_hit},
        "scope": "Arbitrary row and/or column support deletions within original rank-seven C/N atoms on fixed P112. Constrained-position loss is support coverage, not a count of added repair terms or paid operations. No decoder assembly, physical admission or new kappa.",
    }
