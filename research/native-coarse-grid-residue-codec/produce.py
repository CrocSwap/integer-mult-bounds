"""Bind every selected MOVE rank and check one full operator of each rank."""

import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, label):
    if not ok:
        raise ValueError(label)


def binary_inverse(columns):
    n = len(columns)
    rows = [sum(((columns[j] >> i) & 1) << j for j in range(n)) | (1 << (n + i))
            for i in range(n)]
    for col in range(n):
        pivot = next(j for j in range(col, n) if rows[j] >> col & 1)
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for j in range(n):
            if j != col and rows[j] >> col & 1:
                rows[j] ^= rows[col]
    need([v & ((1 << n) - 1) for v in rows] == [1 << j for j in range(n)],
         "independent binary inverse")
    return [sum(((rows[j] >> (n + i)) & 1) << j for j in range(n)) for i in range(n)]


def binary_apply(columns, value):
    out = 0
    while value:
        bit = value & -value
        out ^= columns[bit.bit_length() - 1]
        value ^= bit
    return out


def main():
    need(__debug__, "source assertions must remain enabled")
    for item in json.loads((HERE / "SOURCES.json").read_text())["files"]:
        if item["usage"] == "input":
            need(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() == item["sha256"],
                 "source bytes changed: " + item["path"])
    word = json.loads(gzip.decompress((ROOT / "research/p104-helper470-twin-rung-removal/WORD.json.gz").read_bytes()))
    source = ROOT / "research/staged544-mixed-fourth-entry/native/vendor/native/new/code/borrow"
    sys.path.insert(0, str(source))
    sys.path.insert(0, str(source / "vendor/clifford"))
    import bw_gauss
    from clifford_exact import canonical_frame, lower_child, rank

    charts, edges, edge_columns, representatives, counts = {}, {}, {}, {}, Counter()
    current = dict(enumerate(word["initial"]))
    for j, e in enumerate(word["program"]):
        op, field = e[:2]
        if op == "INIT":
            need(field not in current, "INIT field already live")
            current[field] = e[2]
        elif op == "CLEAR":
            need(current.pop(field) == e[2], "CLEAR frame")
        elif op == "ADD":
            need(current[field] == current[e[2]] == e[4], "ADD frames")
        elif op == "SCALE":
            need(current[field] == e[3], "SCALE frame")
        elif op == "COPY":
            need(current[field] == current[e[2]] == e[4], "COPY frames")
        elif op == "MOVE":
            old, new = e[2:4]
            need(current[field] == old, "MOVE input frame")
            current[field] = new
            for t in (old, new):
                if t not in charts:
                    charts[t] = canonical_frame(9, word["frames"][t])
            key = old, new
            if key not in edges:
                operator = charts[old].adjoint().then(charts[new])
                r = rank([x for x, z, p in operator.tab[9:]])
                edges[key] = r
                edge_columns[key] = [x for x, z, p in operator.tab[9:]]
                if r not in representatives:
                    recipe, compiled = lower_child(operator)
                    need(recipe["rank"] == r, "compiler rank agrees")
                    representatives[r] = (j, e, recipe, compiled)
            counts[edges[key]] += 1
        else:
            raise ValueError("unknown source opcode")
    need(current == dict(enumerate(word["final"])), "all source endpoint frames")
    need(sum(counts.values()) == 3453 and len(word["program"]) == 22803, "selected event inventory")
    # A second pass uses 18-bit matrices and finite spans, without Pauli composition.
    columns = {j: [x | (z << 9) for x, z, p in chart.tab] for j, chart in charts.items()}
    inverses = {j: binary_inverse(cols) for j, cols in columns.items()}
    other_counts = Counter()
    for e in (event for event in word["program"] if event[0] == "MOVE"):
        old, new = e[2:4]
        b = [binary_apply(columns[new], col) & 511 for col in inverses[old][9:]]
        need(b == edge_columns[old, new], "all independently composed B columns")
        span = {0}
        for col in b:
            span |= {x ^ col for x in span}
        other_counts[len(span).bit_length() - 1] += 1
    need(other_counts == counts, "independent complete MOVE rank census")
    arrays, selected = {}, []
    for r, (j, e, recipe, compiled) in sorted(representatives.items()):
        real, imag, exponent = bw_gauss.frame(
            bw_gauss.frame(bw_gauss.eye(9), word["frames"][e[2]], 9, -1),
            word["frames"][e[3]], 9,
        )
        need(exponent <= 18 and np.max(np.abs(real)) <= 1 << 18 and np.max(np.abs(imag)) <= 1 << 18,
             "small exact oracle integer range")
        for col in range(512):
            values, exp = compiled.zero_state(col)
            need(all(a * (1 << exponent) == int(real[row, col]) * (1 << exp) and
                     b * (1 << exponent) == int(imag[row, col]) * (1 << exp)
                     for row, (a, b) in enumerate(values)), "full source columns")
        arrays[f"r{r}_real"], arrays[f"r{r}_imag"] = real, imag
        selected.append({"rank": r, "event_index": j, "event": e, "recipe": recipe,
                         "oracle_exponent": exponent, "oracle_columns": 512})
    out = Path(sys.argv[1])
    np.savez(out / "oracle.npz", **arrays)
    result = {"word_events": len(word["program"]), "move_events": sum(counts.values()),
              "rank_counts": {str(r): count for r, count in sorted(counts.items())},
              "distinct_edges": len(edges), "source_frames": len(charts),
              "independent_binary_census": True,
              "all_endpoint_frames_checked": True, "assertions_enabled": __debug__,
              "width_one_k5_residue_bits_per_move": 5120,
              "width_one_k5_uncompressed_residue_slots": 5120 * sum(counts.values()),
              "width_one_k5_fixed_seed_bits": sum((5 + (r + 1) // 2) * count for r, count in counts.items()),
              "representatives": selected}
    (out / "source.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
