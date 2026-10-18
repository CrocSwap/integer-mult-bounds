#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Weyl-root / row-coordinate dual replay; imports no primary engine."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def indices(mask):
    return [i for i in range(120) if (mask >> i) & 1]


def check_weyl_roots(lines):
    simple = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(6):
        row = [0]*8
        row[i], row[i+1] = -2, 2
        simple.append(tuple(row))
    seen, pending = {simple[0]}, [simple[0]]
    while pending:
        root = pending.pop()
        for normal in simple:
            product = sum(a*b for a, b in zip(root, normal))
            require(product % 4 == 0, "nonintegral reflection")
            reflected = tuple(a-(product//4)*b for a, b in zip(root, normal))
            if reflected not in seen:
                seen.add(reflected)
                pending.append(reflected)
    advertised = {tuple(r) for r in lines} | {tuple(-x for x in r) for r in lines}
    require(len(seen) == 240 and advertised == seen, "Weyl root model disagreement")


def row_coordinates(rows):
    """Choose raw row generators and solve coordinates in that seven-space."""
    pivots, dimension = {}, 0
    for value in rows:
        coefficients = 0
        while value:
            pivot = value.bit_length()-1
            if pivot in pivots:
                value ^= pivots[pivot][0]
                coefficients ^= pivots[pivot][1]
            else:
                pivots[pivot] = (value, coefficients ^ (1 << dimension))
                dimension += 1
                break
    coordinates = []
    for value in rows:
        coefficients = 0
        while value:
            pivot = value.bit_length()-1
            require(pivot in pivots, "row not in chosen span")
            value ^= pivots[pivot][0]
            coefficients ^= pivots[pivot][1]
        coordinates.append(coefficients)
    return dimension, coordinates


def main():
    try:
        sources = json.loads((HERE / "SOURCES.json").read_text())
        for source in sources["archives"]:
            file = HERE / source["local_path"]
            require(hashlib.sha256(file.read_bytes()).hexdigest() == source["sha256"], "source hash disagreement")
        data = json.loads((HERE / "generated/MODEL.json").read_text())
        lines, live = data["lines"], data["live"]
        check_weyl_roots(lines)
        require(len(live) == 112 and set(live) == set(range(120))-set(data["punctured_frame"]), "wrong live model")
        frame_roots = []
        for k in range(4):
            for sign in (1, -1):
                root = [0]*8
                root[2*k], root[2*k+1] = 2, 2*sign
                frame_roots.append(root)
        require([lines[i] for i in data["punctured_frame"]] == frame_roots, "wrong punctured frame")
        ip = [[sum(x*y for x, y in zip(a, b))//4 for b in lines] for a in lines]
        n = [sum(((value+1) % 2) << j for j, value in enumerate(row)) for row in ip]
        support = []
        for alpha in range(120):
            c = sum(1 << i for i in live if ip[alpha][i] != 0)
            support.extend((c, c & ~(1 << alpha)))
        histogram, table = Counter(), []
        for a, left in enumerate(support):
            ids = indices(left)
            for b, right in enumerate(support):
                rows = [n[i] & right for i in ids]
                rank, coordinates = row_coordinates(rows)
                histogram[str(rank)] += 1
                if rank != 7:
                    continue
                codes = [sum((((c & dual).bit_count() % 2) << i) for i, c in zip(ids, coordinates))
                         for dual in range(1, 128)]
                require(len(set(codes)) == 127 and 0 not in codes, "dual code incomplete")
                weights = dict(zip(ids, (row.bit_count() for row in rows)))
                values = [(cut.bit_count(), sum(weights[i] for i in indices(cut)), cut) for cut in codes]
                d, w = min(v[0] for v in values), min(v[1] for v in values)
                dm = min((v for v in values if v[0] == d), key=lambda v: (v[1], v[2]))[2]
                wm = min((v for v in values if v[1] == w), key=lambda v: (v[0], v[2]))[2]
                digest = hashlib.sha256("".join(format(v, "x")+"\n" for v in sorted(codes)).encode()).hexdigest()
                for cut in (dm, wm):
                    after, _ = row_coordinates([row for i, row in zip(ids, rows) if not (cut >> i) & 1])
                    require(after == 6, "dual erasure witness not rank six")
                table.append([a, b, d, w, format(dm, "x"), format(wm, "x"),
                              sum(v[0] == d for v in values), sum(v[1] == w for v in values), digest])
        expected = [json.loads(line) for line in (HERE / "generated/THRESHOLDS.jsonl").read_text().splitlines()]
        require(table == expected, "independent complete table disagreement")
        certificate = json.loads((HERE / "generated/CERTIFICATE.json").read_text())
        require(dict(histogram) == certificate["parent_pair_rank_histogram"], "independent parent ranks disagree")
        lookup = {(r[0], r[1]): r for r in table}
        joint = Counter(min(r[2], lookup[r[1], r[0]][2]) for r in table)
        weighted = Counter(min(r[3], lookup[r[1], r[0]][3]) for r in table)
        require({str(k): v for k, v in joint.items()} == certificate["joint_first_drop_histogram"], "joint thresholds disagree")
        require({str(k): v for k, v in weighted.items()} == certificate["joint_even_position_loss_histogram"], "weighted thresholds disagree")
        witness = certificate["witness"]
        f = witness["frame"]
        require(len(f) == 8 and all(i in live for i in f), "invalid frame witness")
        require(all(ip[i][j] == 0 for i in f for j in f if i != j), "frame not orthogonal")
        a, b = witness["left_tag"], witness["right_tag"]
        fmask = sum(1 << i for i in f)
        require(indices(support[a] & fmask) == witness["frame_change_deleted_rows"], "frame cut mismatch")
        cut = sum(1 << i for i in witness["frame_change_deleted_rows"])
        require(cut.bit_count() == 4 and not ((support[a] & ~cut) & fmask), "frame not removed by four cuts")
        require(bool(support[b] & fmask), "frame was not originally met")
        rank, _ = row_coordinates([n[i] & support[b] for i in indices(support[a] & ~cut)])
        require(rank == 7, "frame cut unexpectedly changes copy price")
        print("PASS_INDEPENDENT_P112_STAR_TRIMS atoms=7616 codewords=967232 copy_drop=20 frame_change=4 even_loss=560")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("REJECT_INDEPENDENT_P112_STAR_TRIMS: "+str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
