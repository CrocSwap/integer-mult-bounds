#!/usr/bin/env python3
"""Restriction-kernel evaluator, produced by Nick Petalas.

The complete census and scientific contract are Philipp / mightyOil's PR1325.
The pinned predecessor stays unchanged. Apache-2.0.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from types import ModuleType


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/sparse-redundant-decoder/verify.py"
MARKER = ("PASS_SPARSE_REDUNDANT_DECODER planes=32385 single_vectors=765 "
          "minimum=64 all_active=65 equality_shifts=4 controls=6 no_new_kappa")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read_bytes(path):
    with path.open("rb") as handle:
        payload = handle.read(1048577)
    need(len(payload) <= 1048576, "one MiB source capacity")
    return payload


def load_source():
    pins = json.loads(read_bytes(HERE / "SOURCES.json"))
    source_bytes = None
    for item in pins["files"]:
        if item["usage"] == "input":
            path = ROOT / item["path"]
            payload = read_bytes(path)
            need(hashlib.sha256(payload).hexdigest() == item["sha256"],
                 "source hash: " + item["path"])
            if path == SOURCE:
                source_bytes = payload
    need(source_bytes is not None, "missing source pin")
    source = ModuleType("p112_pinned_source")
    source.__file__ = str(SOURCE)
    # Compile the authenticated bytes directly; do not consult a bytecode cache.
    exec(compile(source_bytes, str(SOURCE), "exec"), source.__dict__)
    return source


def kernel_dimension(generators, mask):
    """Dimension of vectors in span(generators) vanishing on mask.

    Callers supply an independent binary basis, at most nine 112-bit rows.
    Restriction is linear; its nullity is d minus the restricted row rank.
    """
    pivots = {}
    for row in generators:
        value = row & mask
        for _ in range(9):
            if not value:
                break
            pivot = value.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
        else:
            raise ValueError("basis capacity exceeded")
    return len(generators) - len(pivots)


def plane_census(source, spaces, bases, conflict):
    planes = []
    stream = hashlib.sha256()
    for anchor in range(3):
        others = [k for k in range(4) if k != anchor]
        census = Counter()
        space = spaces[anchor]
        for i, x in enumerate(space[1:], 1):
            for y in space[i + 1:]:
                if y >= x ^ y:
                    continue
                union = x | y
                dims = [kernel_dimension(bases[k], union & conflict[anchor][k])
                        for k in others]
                need(dims == [0, 0, 1], "plane compatibility dimensions")
                census[tuple(dims)] += 1
                stream.update(source.canonical([anchor, x, y, dims]).encode() + b"\n")
        need(sum(census.values()) == 10795, "complete plane count")
        planes.append({"anchor": anchor, "partner_order": others,
                       "counts": {",".join(map(str, k)): v
                                  for k, v in sorted(census.items())}})
    return planes, stream.hexdigest()


def single_census(spaces, bases, conflict):
    single = []
    for anchor in range(3):
        census = Counter()
        for z in spaces[anchor][1:]:
            dim = kernel_dimension(bases[3], z & conflict[anchor][3])
            need(dim <= 2, "nonzero coordinate deficiency forces extra deficiency <=2")
            census[dim] += 1
        need(census == {1: 1, 2: 254}, "complete single-vector census")
        single.append({"anchor": anchor,
                       "dimensions": {str(k): v for k, v in sorted(census.items())}})
    return single


def decoder_witnesses(source, roots, rows, supports):
    witnesses = []
    shifts_list = [("zero", [0] * 112)]
    shifts_list += [(f"coordinate_{j}", [r[j] for r in roots]) for j in range(3)]
    for name, shifts in shifts_list:
        info, _, _ = source.decode(roots, shifts, rows, supports)
        need(info["total"] == 64 and info["active_terms"] == 8, "all equality witnesses")
        witnesses.append({"name": name, **info})
    shifts = [0] * 112
    shifts[40] = 2
    info, d, t = source.decode(roots, shifts, rows, supports)
    need(info["costs"] == [8] * 8 + [1] and info["active_terms"] == 9,
         "sharp all-active witness")
    witnesses.append({"name": "all_active_single_row", "row": 40, "shift": 2, **info})
    costs = []
    for s in range(12):
        shifts = [((i * 17 + s * 13 + 40) % 7) - 3 for i in range(112)]
        item, _, _ = source.decode(roots, shifts, rows, supports)
        need(item["total"] >= 64, "finite shift check")
        costs.append(item["total"])
    return witnesses, costs, d, t


def source_controls(source, roots, rows, spaces, d, t):
    controls = []

    def reject(name, operation):
        try:
            operation()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("control not rejected: " + name)

    damaged = [list(x) for x in d]
    damaged[40][0] += 2
    reject("missing_shift_subtraction", lambda: source.check_identity(roots, damaged, t))
    damaged_t = [list(x) for x in t]
    for i, row in enumerate(roots):
        damaged_t[i][8] = row[0] + row[1]
    reject("missing_third_normal_coordinate",
           lambda: source.check_identity(roots, d, damaged_t))
    wrong = [row ^ ((1 << 112) - 1) for row in rows]
    reject("missing_pairing_affine_one",
           lambda: need(len(source.basis(wrong)) == 9, "binary pairing dimension"))
    reject("unpunctured_unit", lambda: need(
        [source.dimension(s) for s in source.setup(source.geometry(True))[3]]
        == [8] * 8 + [9], "puncture contract"))
    reject("omitted_ratio_conflict",
           lambda: need(source.dimension(spaces[1]) == 0, "plane lemma missing conflicts"))
    reject("incomplete_plane_inventory",
           lambda: need(10794 == (255 * 254) // 6, "complete planes"))
    return controls


def run(source):
    sources = source.check_sources()
    roots = source.geometry()
    need(len(roots) == 112, "P112 frame puncture")
    need(all(sum(r[j] * r[k] for r in roots) == (56 if j == k else 0)
             for j in range(8) for k in range(8)), "real root span via R-transpose-R=56I")
    _, rows, supports, allspaces = source.setup(roots)
    need([source.dimension(s) for s in allspaces] == [8] * 8 + [9],
         "column-code dimensions")
    need(all(any(rows[i] >> j & 1 for j in y)
             for y in supports for i in range(112)), "zero term cost iff row support empty")
    spaces = [allspaces[k] for k in (0, 1, 2, 8)]
    bases = [source.basis(space) for space in spaces]
    need([len(b) for b in bases] == [8, 8, 8, 9], "restriction basis dimensions")
    vals = [r[:3] + (0,) for r in roots]
    conflict = [[sum((v[j] != v[k]) << i for i, v in enumerate(vals))
                 for k in range(4)] for j in range(4)]
    planes, plane_digest = plane_census(source, spaces, bases, conflict)
    single = single_census(spaces, bases, conflict)
    witnesses, costs, d, t = decoder_witnesses(source, roots, rows, supports)
    controls = source_controls(source, roots, rows, spaces, d, t)
    need(witnesses[-1]["total"] == 65 and witnesses[0]["total"] == 64,
         "active/zero distinction")
    return {"schema_version": 1, "scope": "fixed coordinate frame plus e0+e1+e2 on P112",
            "base_commit": source.BASE, "roots": 112, "root_digest": source.digest(roots),
            "pairing_digest": source.digest(rows), "column_support_sizes": list(map(len, supports)),
            "column_code_dimensions": [source.dimension(s) for s in allspaces],
            "planes": planes, "plane_count": 32385, "plane_stream_sha256": plane_digest,
            "single_vector_census": single, "single_vectors": 765, "witnesses": witnesses,
            "equality_shifts": ["0", "r0", "r1", "r2"], "all_active_minimum": 65,
            "minimum": 64, "finite_example_costs": costs,
            "identity_entries_checked": 17 * 112 * 112, "controls": controls,
            "source_inputs": sources, "new_kappa": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    source = load_source()
    result = run(source)
    if args.write:
        with args.write.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((SOURCE.parent / "CERTIFICATE.json").read_text())
        need(source.canonical(result) == source.canonical(expected), "certificate exact replay")
    print(MARKER)


if __name__ == "__main__":
    main()
