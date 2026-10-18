#!/usr/bin/env python3
"""Separate finite-premise replay using explicit nine-bit labels. Apache-2.0.

Does not import verify.py. Reuses the pinned PR845 geometry as an oracle, while
the primary implementation reconstructs roots and pairings independently.
Arham Tahir, with substantial OpenAI Codex assistance; no human review claim.
"""
from collections import Counter
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(value, message):
    if not value:
        raise ValueError(message)


def basis(vectors):
    """Reduce from the lowest bit, unlike the primary highest-bit algorithm."""
    pivots = {}
    chosen = []
    for original in vectors:
        v = original
        while v:
            bit = v & -v
            if bit in pivots:
                v ^= pivots[bit]
            else:
                pivots[bit] = v
                chosen.append(original)
                break
    return chosen


def parity(value):
    return value.bit_count() % 2


def prepare():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    expected = {"research/p112-single-lift/geometry.py",
                "research/complex-frame-pair-decoders/PROOF.md"}
    live_pins = [r for r in pins["files"] if r["usage"] == "input"]
    require(len(live_pins) == 2 and {r["path"] for r in live_pins} == expected,
            "source inventory")
    for row in live_pins:
        require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
                == row["sha256"], "source digest")
    spec = importlib.util.spec_from_file_location("source_geometry", ROOT /
                                      "research/p112-single-lift/geometry.py")
    geom = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(geom)
    old = geom.build()
    lookup = {max(tuple(r), tuple(-v for v in r)): i
              for i, r in enumerate(old["roots"])}
    roots = sorted(lookup)
    order = [lookup[r] for r in roots]
    labels = [old["labels"][i] for i in order]
    duals = [old["duals"][i] for i in order]
    x = [old["X"][i] for i in order]  # Signs do not change any support.
    require(len(roots) == 112 and len(basis(labels)) == 9, "live ambient space")

    def paired(left, right):
        rb = basis(labels[i] for i in right)
        lb = basis(duals[i] for i in left)
        return len(basis(sum(parity(u & v) << j for j, v in enumerate(rb))
                         for u in lb))

    stars, slices = [], []
    hist = Counter()
    for k in range(8):
        star = [i for i in range(112) if x[i][k]]
        require(len(star) == 56 and len(basis(labels[i] for i in star)) == 8
                and paired(star, star) == 8, "coordinate star premises")
        stars.append(star)
        subsets = [[i for i in star if parity(duals[i] & labels[j])]
                   for j in range(112)]
        for subset in subsets:
            require(len(basis(labels[i] for i in subset)) == 7, "slice span seven")
        slices.append(subsets)
        # Reuse only the explicitly constructed immutable label bases.
        left_bases = [basis(duals[i] for i in s) for s in subsets]
        right_bases = [basis(labels[i] for i in s) for s in subsets]
        for left in left_bases:
            for right in right_bases:
                rank = len(basis(sum(parity(u & v) << j for j, v in enumerate(right))
                                 for u in left))
                require(rank >= 6, "cross-pair bound six")
                hist[str(rank)] += 1
    return pins, roots, labels, duals, stars, slices, dict(sorted(hist.items())), paired


def validate(receipt, data):
    pins, roots, labels, duals, stars, slices, hist, paired = data
    require(receipt["sources"] == pins, "receipt source binding")
    require(receipt["roots"] == [list(r) for r in roots], "complete canonical root order")
    require(len(receipt["coordinate_stars"]) == 8, "all coordinate stars")
    for row, star in zip(receipt["coordinate_stars"], stars):
        require(row == {"support": hex(sum(1 << i for i in star)),
                        "span": 8, "pairing": 8}, "star receipt")
    rows = receipt["slices"]
    require(len(rows) == 896, "all 896 slice receipts")
    require({(row["coordinate"], row["root"]) for row in rows}
            == {(k, j) for k in range(8) for j in range(112)}, "unique full coverage")
    for row in rows:
        subset = slices[row["coordinate"]][row["root"]]
        require(row["mask"] == hex(sum(1 << i for i in subset))
                and row["size"] == len(subset) and row["rank"] == 7,
                "exact slice support and dimension")
        witness = row["basis"]
        require(len(witness) == 7 and set(witness) <= set(subset)
                and len(basis(labels[i] for i in witness)) == 7,
                "seven distinct independent original-row witnesses")
    require(receipt["cross_pair_count"] == 100352 and sum(hist.values()) == 100352
            and receipt["cross_pair_histogram"] == hist, "all ordered cross pairs")
    e = receipt["rank_six_example"]
    k, j, h = e["coordinate"], e["left_root"], e["right_root"]
    require(0 <= k < 8 and 0 <= j < 112 and 0 <= h < 112
            and paired(slices[k][j], slices[k][h]) == 6, "actual rank-six witness")
    i, j = receipt["rank_nine_odd_singleton"]
    require(0 <= i < 112 and 0 <= j < 112 and i != j
            and parity(duals[i] & labels[j]) == 0, "off-mask singleton")


def main():
    receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
    data = prepare()
    validate(receipt, data)
    controls = []
    mutations = [
        ("omit slice", lambda p: p["slices"].pop()),
        ("duplicate slice", lambda p: p["slices"].__setitem__(0, p["slices"][1])),
        ("false slice dimension", lambda p: p["slices"][0].__setitem__("rank", 8)),
        ("duplicate basis witness", lambda p: p["slices"][0]["basis"].__setitem__(
            0, p["slices"][0]["basis"][1])),
        ("erase rank-six cases", lambda p: p["cross_pair_histogram"].pop("6")),
        ("change odd singleton to diagonal", lambda p:
            p.__setitem__("rank_nine_odd_singleton", [0, 0])),
    ]
    for name, mutation in mutations:
        bad = copy.deepcopy(receipt)
        mutation(bad)
        try:
            validate(bad, data)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("accepted mutation: " + name)
    print("PASS_P112_FREE_RECTANGLE_INDEPENDENT slices=896 cross_pairs=100352 "
          "basis_rows=6272 controls=" + str(len(controls)))


if __name__ == "__main__":
    main()
