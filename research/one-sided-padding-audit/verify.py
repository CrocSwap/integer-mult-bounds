#!/usr/bin/env python3
"""Exact audit of PR3074's one-sided padding implication.

CubeJerry, with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor Python module is imported or executed. Standard library only.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
DATA = "research/one-sided-decoders-all-m/data/data.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def binary_basis(rows):
    pivots = {}
    for row in rows:
        while row:
            lead = row.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = row
                break
            row ^= pivots[lead]
    return tuple(pivots[i] for i in sorted(pivots, reverse=True))


def rank2(rows):
    return len(binary_basis(rows))


def contains(rows, vector):
    return rank2([*rows, vector]) == rank2(rows)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def parity(x):
    return x.bit_count() % 2


def determinant(matrix):
    """Bareiss integer elimination; no tolerance or modular rank inference."""
    n = len(matrix)
    require(all(len(row) == n for row in matrix), "square minor required")
    require(all(type(x) is int for row in matrix for x in row), "integer minor required")
    if not n:
        return 1
    a = [row[:] for row in matrix]
    sign, previous = 1, 1
    for k in range(n - 1):
        pivot = next((i for i in range(k, n) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[k][k] * a[i][j] - a[i][k] * a[k][j]
                require(numerator % previous == 0, "nonexact Bareiss division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = a[k][k]
    return sign * a[-1][-1]


def check_sources(root=ROOT):
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    checked = []
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        payload = (root / row["path"]).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == row["sha256"],
                "source hash: " + row["path"])
        blob = b"blob " + str(len(payload)).encode() + b"\0" + payload
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"],
                "source Git blob: " + row["path"])
        checked.append(row["path"])
    require(DATA in checked, "geometry must be pinned")
    return checked


def geometry(path=ROOT / DATA):
    # JSON half-integers are read as rationals, never binary floats.
    data = json.loads(path.read_text(), parse_float=Fraction)
    roots = [tuple(Fraction(x) for x in row) for row in data["L"]]
    frame = [tuple(Fraction(x) for x in row) for row in data["F0"]]
    require(len(roots) == 112 and len(frame) == 8, "geometry sizes")
    require(all(len(row) == 8 for row in roots + frame), "root dimension")
    # Independent D8+ construction, not the predecessor's root generator.
    full = set()
    for i, j in combinations(range(8), 2):
        for u, v in product((-1, 1), repeat=2):
            row = [Fraction(0)] * 8
            row[i], row[j] = Fraction(u), Fraction(v)
            full.add(tuple(row))
    for signs in product((-1, 1), repeat=8):
        if sum(s < 0 for s in signs) % 2 == 0:
            full.add(tuple(Fraction(s, 2) for s in signs))

    def canon(row):
        return row if next(x for x in row if x) > 0 else tuple(-x for x in row)

    expected = {canon(row) for row in full}
    require(len(full) == 240 and len(expected) == 120, "D8+ generation")
    require({canon(row) for row in roots + frame} == expected, "complete E8 lines")
    require(len(set(map(canon, roots + frame))) == 120, "duplicate root line")
    require({canon(tuple(map(Fraction, row))) for row in data["E8"]} == expected,
            "source E8 enumeration")
    require(all(dot(a, b) == 2 * (i == j)
                for i, a in enumerate(frame) for j, b in enumerate(frame)),
            "orthogonal frame")
    all_roots = roots + frame
    coordinates = [[dot(row, f) for f in frame] for row in all_roots]
    require(all(x.denominator == 1 for row in coordinates for x in row),
            "integral frame coordinates")
    coordinates = [[int(x) for x in row] for row in coordinates]
    require(coordinates[:112] == data["FC"], "source frame coordinates")
    labels = data["LAB"] + data["Z"]
    require(len(labels) == 120 and all(type(x) is int and 0 < x < 512 for x in labels),
            "nine-bit labels")
    require(len(set(labels)) == 120 and rank2(labels[:112]) == 9, "label rank")
    # Authenticate the label chart directly against all dense-pairing entries.
    # This does not reuse the source's floating determinant basis selection.
    pairing = []
    for row in all_roots:
        values = [1 + dot(row, other) for other in all_roots]
        require(all(x.denominator == 1 for x in values), "integral pairings")
        pairing.append(sum((int(x) % 2) << j for j, x in enumerate(values)))
    require(rank2(pairing) == 9, "dense pairing rank")
    mapping = {}
    for label, image in zip(labels, pairing):
        x, y = label, image
        while x:
            k = x.bit_length() - 1
            if k not in mapping:
                mapping[k] = (x, y)
                break
            x ^= mapping[k][0]
            y ^= mapping[k][1]
        require(x != 0 or y == 0, "label-to-pairing linear consistency")
    require(len(mapping) == 9, "label map domain")
    require(rank2([y for _, y in mapping.values()]) == 9, "label map injective")
    return {"C": coordinates, "labels": labels, "B": pairing}


def minor_check(row, available, matrix, rank):
    rows, columns = row["rows"], row["columns"]
    require(type(row["determinant"]) is int, "typed determinant")
    require(len(rows) == len(columns) == rank, "minor dimensions")
    require(all(type(i) is int for i in rows + columns), "typed minor indices")
    require(len(set(rows)) == rank and len(set(columns)) == rank, "duplicate minor index")
    require(set(rows) <= set(available) and set(columns) <= set(range(8)),
            "minor outside complement")
    value = determinant([[matrix[i][j] for j in columns] for i in rows])
    require(value != 0 and value == row["determinant"], "minor determinant")
    magnitude = abs(value)
    require(magnitude & (magnitude - 1) == 0, "minor must be a power of two")
    return value


def check_certificate(certificate, g):
    require(certificate["schema"] == "one-sided-padding-annihilators/v1", "certificate schema")
    records = certificate["characters"]
    require(all(type(r["character"]) is int for r in records)
            and [r["character"] for r in records] == list(range(1, 512)),
            "all 511 characters exactly once")
    counts, exceptional, determinants = Counter(), [], set()
    for record in records:
        h = record["character"]
        complement = [t for t, label in enumerate(g["labels"]) if parity(h & label)]
        old = [t for t in complement if t < 112]
        rank = record["rank112"]
        require(type(rank) is int and rank in (7, 8), "declared rank")
        determinants.add(abs(minor_check(record["minor112"], old, g["C"], rank)))
        if rank == 7:
            axis = record["kernel_axis"]
            require(type(axis) is int and axis in range(8), "kernel axis")
            require(all(g["C"][t][axis] == 0 for t in old), "null direction")
            require(len(old) == 56, "exceptional complement size")
            off = [t for t in range(112) if g["C"][t][axis]]
            require(set(off) == set(range(112)) - set(old), "exceptional support")
            require(rank2([g["labels"][t] for t in off]) == 8, "support hyperplane")
            require(all(parity(h & g["labels"][t]) == ((g["B"][t] >> (112 + axis)) & 1)
                        for t in range(120)), "exception equals frame pairing")
            exceptional.append({"character": h, "axis": axis})
        else:
            require(record["kernel_axis"] is None, "full-rank kernel")
        determinants.add(abs(minor_check(record["minor120"], complement, g["C"], 8)))
        counts[rank] += 1
    require(counts == {7: 8, 8: 503}, "rank distribution")
    require(sorted(e["axis"] for e in exceptional) == list(range(8)), "eight distinct axes")
    return {"characters": 511, "rank112_histogram": {str(k): v for k, v in sorted(counts.items())},
            "rank120_histogram": {"8": 511}, "absolute_minor_determinants": sorted(determinants),
            "scalar_fields": "every field of characteristic different from two", "exceptional": exceptional}


def support(column):
    return [i for i, x in enumerate(column) if x]


def term_cost(column, y, g):
    n = len(column)
    columns = [s for s in range(n) if dot(g["C"][s], y)]
    mask = sum(1 << s for s in columns)
    return rank2([g["B"][t] & mask for t in support(column)])


def cost(terms, g):
    return sum(term_cost(p, y, g) for p, y in terms)


def exact(terms, n, g):
    require(all(len(p) == n and len(y) == 8 for p, y in terms), "decoder shape")
    require(all(sum(p[t] * y[j] for p, y in terms) == g["C"][t][j]
                for t in range(n) for j in range(8)), "decoder endpoint")


def corrected(column, y, g):
    nz = support(y)
    if len(nz) != 1 or not any(column):
        return None
    axis = nz[0]
    labels = [g["labels"][t] for t in support(column)]
    return axis if contains(labels, g["labels"][112 + axis]) else None


def unit(i, value=1):
    return [Fraction(value) * (i == j) for j in range(8)]


def merge(terms, g):
    """Merge groups originally corrected, then reclassify their sums."""
    groups, other = {}, []
    for p, y in terms:
        if not any(p) or not any(y):
            continue
        axis = corrected(p, y, g)
        if axis is None:
            other.append((p[:], y[:]))
        else:
            if axis not in groups:
                groups[axis] = [Fraction(0)] * 112
            groups[axis] = [a + y[axis] * b for a, b in zip(groups[axis], p)]
    return other + [(p, unit(i)) for i, p in sorted(groups.items()) if any(p)]


def pad(terms, g, normalize=True):
    exact(terms, 112, g)
    normalized = merge(terms, g) if normalize else deepcopy(terms)
    exact(normalized, 112, g)
    result, used = [], set()
    for p, y in normalized:
        q = p[:] + [Fraction(0)] * 8
        axis = corrected(p, y, g)
        # An unnormalized negative control still gets an exact endpoint:
        # only one term gets the new row, but every duplicate loses relief.
        if axis is not None and axis not in used:
            q[112 + axis] = Fraction(2) / y[axis]
            used.add(axis)
        result.append((q, y[:]))
    for i in range(8):
        if i not in used:
            p = [Fraction(0)] * 120
            p[112 + i] = Fraction(1)
            result.append((p, unit(i, 2)))
    exact(result, 120, g)
    return normalized, result, sorted(used)


def coordinate_terms(g):
    return [([Fraction(row[j]) for row in g["C"][:112]], unit(j)) for j in range(8)]


def root_swap(g, axis=0):
    r = next(i for i, row in enumerate(g["C"][:112]) if row[axis])
    h = g["C"][r]
    terms = []
    for j in range(8):
        if j != axis:
            y = unit(j)
            y[axis] = -Fraction(h[j], h[axis])
            terms.append(([Fraction(row[j]) for row in g["C"][:112]], y))
    p = [Fraction(dot(row, h), h[axis]) for row in g["C"][:112]]
    diagonal = p[r]
    p[r] = Fraction(0)
    terms.append((p, unit(axis)))
    terms.append(([Fraction(i == r) for i in range(112)], unit(axis, diagonal)))
    exact(terms, 112, g)
    return terms


def fixtures(g):
    coordinate = coordinate_terms(g)
    swap = root_swap(g)
    split = swap[:-2] + [([x / 2 for x in swap[-2][0]], swap[-2][1]) for _ in range(2)] + swap[-1:]
    cancellation = coordinate[1:] + [([x + 2 for x in coordinate[0][0]], unit(0)),
                                    ([Fraction(-2)] * 112, unit(0))]
    disappearing = coordinate + [([Fraction(1)] * 112, unit(0)),
                                  ([Fraction(-1)] * 112, unit(0))]
    return {"coordinate": coordinate, "root_swap": swap, "split_swap": split,
            "correction_lost": cancellation, "zero_sum": disappearing}


def check_decoders(g):
    results = {}
    for name, terms in fixtures(g).items():
        normalized, padded, corrected_axes = pad(terms, g)
        before, after, final = cost(terms, g), cost(normalized, g), cost(padded, g)
        require(after <= before, "merge cost rose")
        require(final == after + 8 and final <= before + 8, "padding cost")
        results[name] = {"raw": before, "normalized": after, "padded": final,
                         "corrected_after_merge": corrected_axes}
    require(results["correction_lost"] == {"raw": 72, "normalized": 64, "padded": 72,
                                          "corrected_after_merge": []}, "cancellation witness")
    require(results["split_swap"]["raw"] == 71, "split-swap witness")
    _, unmerged, _ = pad(fixtures(g)["correction_lost"], g, normalize=False)
    require(cost(unmerged, g) == 81, "unmerged extra-charge witness")
    return {"decoders": results, "unnormalized_exact_cost": 81}


def check_lift_controls(g):
    # Finite calibration; PROOF.md supplies the arbitrary-S spanning argument.
    for mask in range(256):
        live = list(range(112)) + [112 + i for i in range(8) if mask >> i & 1]
        weights = [rank2([g["labels"][t] for t in live if g["C"][t][j]]) for j in range(8)]
        require(sum(weights) == 64 + mask.bit_count(), "lift coordinate weights")
        for t in range(120):
            for j in range(8):
                extended = g["C"][t][j] if t in live else 0
                correction = 2 if t == 112 + j and t not in live else 0
                require(extended + correction == g["C"][t][j], "lift extension endpoint")
        require(sum(weights) + 8 - mask.bit_count() == 72, "lift upper budget")
    return {"frame_subsets": 256, "coordinate_extension_cost": 72}


def odd_field_control(g):
    """Exhaust all nonzero F3^8 directions; the all-field proof uses minors."""
    old_counts, new_counts = Counter(), Counter()
    for y in product(range(3), repeat=8):
        if not any(y):
            continue
        off = [t for t, row in enumerate(g["C"]) if dot(row, y) % 3]
        old = [t for t in off if t < 112]
        old_rank = rank2([g["labels"][t] for t in old])
        new_rank = rank2([g["labels"][t] for t in off])
        require(old_rank == (8 if len(support(y)) == 1 else 9), "F3 support classification")
        require(new_rank == 9, "F3 full support classification")
        old_counts[old_rank] += 1
        new_counts[new_rank] += 1
    # Characteristic two is excluded for a reason: the all-ones direction
    # is nonzero but C*y=0, so even the nonzero-codeword premise changes.
    require(all(sum(row) % 2 == 0 for row in g["C"]), "characteristic-two witness")
    return {"F3_nonzero_directions": 6560,
            "F3_rank112_histogram": {str(k): v for k, v in sorted(old_counts.items())},
            "F3_rank120_histogram": {str(k): v for k, v in sorted(new_counts.items())},
            "F2_nonzero_kernel_witness": [1] * 8}


def expect_rejection(call, fragment):
    try:
        call()
    except ValueError as error:
        require(fragment in str(error), "wrong rejection: " + str(error))
        return
    raise ValueError("negative control accepted: " + fragment)


def negative_controls(certificate, g):
    names = []

    def broken(name, edit, fragment):
        changed = deepcopy(certificate)
        edit(changed)
        expect_rejection(lambda: check_certificate(changed, g), fragment)
        names.append(name)

    broken("omitted_character", lambda c: c["characters"].pop(), "all 511")
    broken("duplicate_character", lambda c: c["characters"][1].update(character=1), "all 511")
    broken("zero_minor", lambda c: c["characters"][0]["minor112"].update(determinant=0), "minor determinant")
    broken("wrong_minor_sign", lambda c: c["characters"][0]["minor112"].update(
        determinant=-c["characters"][0]["minor112"]["determinant"]), "minor determinant")
    broken("duplicate_minor_row", lambda c: c["characters"][0]["minor112"]["rows"].__setitem__(
        0, c["characters"][0]["minor112"]["rows"][1]), "duplicate minor index")
    exceptional = next(i for i, r in enumerate(certificate["characters"]) if r["rank112"] == 7)
    broken("wrong_null_axis", lambda c: c["characters"][exceptional].update(
        kernel_axis=(c["characters"][exceptional]["kernel_axis"] + 1) % 8), "null direction")
    broken("missing_full_extension_minor", lambda c: c["characters"][exceptional]["minor120"].update(
        rows=c["characters"][exceptional]["minor112"]["rows"]), "minor dimensions")
    for name in ("coordinate", "root_swap"):
        _, padded, _ = pad(fixtures(g)[name], g)
        first = next(p for p, _ in padded if any(p[112:]))
        index = next(i for i in range(112, 120) if first[i])
        first[index] = 0
        expect_rejection(lambda: exact(padded, 120, g), "decoder endpoint")
        names.append("missing_frame_value_" + name)
    raw = fixtures(g)["correction_lost"]
    _, padded, _ = pad(raw, g, normalize=False)
    expect_rejection(lambda: require(cost(padded, g) <= cost(raw, g) + 8, "raw budget"), "raw budget")
    names.append("unmerged_corrections_exceed_raw_plus8")
    # The frame rows force y=e_0/2, nonzero on 56 old rows: delta is not C_E y.
    delta = [Fraction(t == 112) for t in range(120)]
    forced_y = [x / 2 for x in delta[112:]]
    expect_rejection(lambda: require(all(dot(row, forced_y) == delta[t]
        for t, row in enumerate(g["C"])), "one-sided factor"), "one-sided factor")
    names.append("delta_factor_not_in_root_code")
    return names


def run(certificate_path):
    pins = check_sources()
    g = geometry()
    certificate = json.loads(certificate_path.read_text())
    return {"status": "PASS_ONE_SIDED_PADDING_AUDIT", "sources_checked": len(pins),
            "support_classification": check_certificate(certificate, g),
            **check_decoders(g), **check_lift_controls(g), **odd_field_control(g),
            "negative_controls": negative_controls(certificate, g),
            "scope": "Exact finite rank premise and written padding/merge proof in characteristic not two; L120 remains open. No new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=PACKAGE / "CERTIFICATE.json")
    parser.add_argument("--output", type=Path, help="Write result to a new external file; otherwise compare EXPECTED.json")
    args = parser.parse_args()
    result = run(args.certificate)
    if args.output:
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        require(result == json.loads((PACKAGE / "EXPECTED.json").read_text()), "stored result mismatch")
    print("PASS_ONE_SIDED_PADDING_AUDIT characters=511 ranks112=503x8+8x7 ranks120=511x8 "
          "lift_masks=256 F3=6560 cancellation=72->64->72 controls=11 no_new_kappa")


if __name__ == "__main__":
    main()
