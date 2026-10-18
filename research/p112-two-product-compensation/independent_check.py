#!/usr/bin/env python3
"""Independent nine-bit-label replay; imports no package/predecessor code.

Hanson Sun (@bbMisk), substantial OpenAI Codex assistance. Apache-2.0.
Uses PR845's pinned PR717 labels, low-pivot elimination and bilinear images,
instead of the primary checker's Euclidean construction and 112-bit rows.
The shared input and same AI-assisted author limit the independence claim.
"""
from collections import Counter
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/p112-single-lift/reference-geometry.json"
NORMALS = [(1, 0), (0, 1), (1, 1), (1, -1), (1, 2)]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def parity(value):
    return value.bit_count() % 2


def spanning(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value & -value
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return list(pivots.values())


def image_rank(left, right):
    images = []
    for r in right:
        image = 0
        for i, l in enumerate(left):
            image |= parity(l & r) << i
        images.append(image)
    return len(spanning(images))


def canonical_root(row):
    sign = 1 if next(t for t in row if t) > 0 else -1
    return tuple(sign * t for t in row)


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for entry in pins["files"]:
        if entry["usage"] == "input":
            raw = (ROOT / entry["path"]).read_bytes()
            check(sha(raw) == entry["sha256"], "source hash")
            check(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
                  == entry["git_blob"], "source blob")
    raw = (ROOT / SOURCE).read_bytes()
    source = json.loads(raw)
    expected = json.loads((HERE / "CERTIFICATE.json").read_text())
    order = sorted(range(112), key=lambda i: canonical_root(source["roots"][i]))
    x = [source["X"][i] for i in order]
    check(all(sum(row[i] * row[j] for row in x) == 56 * (i == j)
              for i in range(8) for j in range(8)), "coordinate independence")
    labels = [source["labels"][i] for i in order]
    duals = [source["duals"][i] for i in order]
    check(len(set(labels)) == len(set(duals)) == 112 and all(labels) and all(duals), "distinct nonzero labels")
    check(len(spanning(labels)) == len(spanning(duals)) == 9, "ambient dimensions")
    b = [[parity(a & c) for c in labels] for a in duals]
    for i in range(112):
        for j in range(112):
            rr, ss = source["roots"][order[i]], source["roots"][order[j]]
            gram4 = sum(a * c for a, c in zip(rr, ss))
            check(gram4 % 4 == 0 and b[i][j] == (1 + gram4 // 4) % 2, "all-entry Gram/label binding")
            check(b[i][j] == b[j][i], "symmetric pairing")
    b_words = [sum(t << j for j, t in enumerate(row)) for row in b]
    check(sha(raw) == expected["geometry_source_sha256"], "receipt source")
    roots = [canonical_root(source["roots"][i]) for i in order]
    check(sha(encoded(roots)) == expected["root_order_sha256"], "canonical root order")
    supports = [[i for i, row in enumerate(x) if a * row[4] + c * row[6]] for a, c in NORMALS]
    coordinate_ranks = []
    for k in range(8):
        points = [i for i, row in enumerate(x) if row[k]]
        coordinate_ranks.append(image_rank(spanning(duals[i] for i in points), spanning(labels[i] for i in points)))
    check(coordinate_ranks == [8] * 8, "all eight coordinate charges")
    strata, erasure_witnesses = [], []
    for normal, points in zip(NORMALS, supports):
        weights = [sum(parity(t & duals[i]) for i in points) for t in range(1, 512)]
        dimension = len(spanning(duals[i] for i in points))
        distance = min(w for w in weights if w)
        check(dimension >= 8 and distance > 3, "span robustness")
        histogram = dict(sorted(Counter(weights).items()))
        strata.append({"normal": list(normal), "support_size": len(points), "span_dimension": dimension,
                       "erasure_distance": distance, "character_weight_histogram": histogram})
        witness = weights.index(distance) + 1
        survivors = [duals[i] for i in points if not parity(witness & duals[i])]
        check(len(spanning(survivors)) < dimension, "sharp erasure boundary must lose span")
        erasure_witnesses.append({"character": witness, "deleted": distance,
                                  "remaining_dimension": len(spanning(survivors))})
    left_full = [spanning(duals[i] for i in points) for points in supports]
    right_full = [spanning(labels[i] for i in points) for points in supports]
    left_slices = [[spanning(duals[i] for i in points if b[i][j]) for j in range(112)]
                   for points in supports]
    right_slices = [[spanning(labels[i] for i in points if b[i][j]) for j in range(112)]
                    for points in supports]
    free = [(i, j) for i in range(112) for j in range(112) if b[i][j] == 0]
    check(len(free) == 5824, "free-pair coverage")
    pairs, one_trace, two_trace = [], bytearray(), bytearray()
    for a in range(5):
        for c in range(5):
            original = image_rank(left_full[a], right_full[c])
            one = [image_rank(l, right_full[c]) for l in left_slices[a]]
            two = [image_rank(left_slices[a][j], right_slices[c][i]) for i, j in free]
            check(original >= 8 and min(one) >= 7 and min(two) >= 6, "survivor floors")
            check(min(two) == 4 + sum(bool(t) for t in NORMALS[a]) + sum(bool(t) for t in NORMALS[c]),
                  "credited PR1373 refined floor")
            one_trace.extend(one)
            two_trace.extend(two)
            pairs.append({"left": a, "right": c, "original_rank": original,
                          "one_sided_histogram": dict(sorted(Counter(one).items())),
                          "one_sided_minimum": min(one), "one_sided_witness": one.index(min(one)),
                          "two_sided_histogram": dict(sorted(Counter(two).items())),
                          "two_sided_minimum": min(two), "two_sided_witness": list(free[two.index(min(two))])})
    actual = {"coordinate_pair": [4, 6], "ports": 112, "pairing_rank": image_rank(spanning(duals), spanning(labels)),
              "baseline_coordinate_ranks": coordinate_ranks,
              "pairing_sha256": sha(encoded(b_words)), "strata": strata, "character_evaluations": 2555,
              "free_port_pairs": len(free), "one_sided_records": len(one_trace), "one_sided_sha256": sha(one_trace),
              "two_sided_records": len(two_trace), "two_sided_sha256": sha(two_trace), "pairs": pairs}
    check(json.loads(json.dumps(actual)) == expected["finite"], "complete finite-premise receipt mismatch")
    # A missing affine coordinate changes rank nine to rank eight.
    unshifted = [sum((1 - t) << j for j, t in enumerate(row)) for row in b]
    check(len(spanning(unshifted)) == 8, "affine omission boundary")
    print("PASS_P112_COMPENSATION_INDEPENDENT characters=2555 one_sided=2800 "
          "three_product_records=145600 sharp_erasure_controls=5 affine_control=1")


if __name__ == "__main__":
    main()
