#!/usr/bin/env python3
"""independent construction-a and intrinsic lattice-parity certificate for r420.

gojo (@6ojo), with substantial openai codex assistance; apache-2.0.
only the standard library is used. no predecessor arithmetic is imported.
"""

import argparse
from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
WORD = "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
SEED = 76


class Reject(ValueError):
    """a failed mathematical obligation or input binding."""


def require(condition, message):
    if not condition:
        raise Reject(message)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def power_of_two(value):
    return value > 0 and value & (value - 1) == 0


def wedge(blade, vector):
    """right exterior product, indexed by increasing-coordinate bit masks.

    moving the appended coordinate j left across coordinates greater than j
    contributes one minus sign per crossing. zero coefficients are omitted.
    """
    result = {}
    for mask, coefficient in blade.items():
        for j, value in enumerate(vector):
            if value and not (mask & (1 << j)):
                sign = -1 if (mask >> (j + 1)).bit_count() % 2 else 1
                key = mask | (1 << j)
                result[key] = result.get(key, 0) + sign * coefficient * value
    return {mask: value for mask, value in result.items() if value}


def canonical_line(row):
    first = next((value for value in row if value), 0)
    require(first != 0, "zero root")
    return tuple(row) if first > 0 else tuple(-value for value in row)


def residue(row):
    return sum((value % 2) << j for j, value in enumerate(row))


def root_certificate(lines):
    require(type(lines) is list and len(lines) == 120, "root count")
    for row in lines:
        require(type(row) is list and len(row) == 8, "root coordinate shape")
        require(all(type(value) is int for value in row), "integer root coordinates")
        require(sum(value * value for value in row) == 4, "root norm")
    roots = {canonical_line(row) for row in lines}
    require(len(roots) == 120, "distinct root lines")

    # every root is a lattice generator. binary closure records how their
    # residues generate the code; no hnf or rational row reduction is used.
    code = {0}
    generators = []
    for i in sorted(range(120), key=lambda i: (i - SEED) % 120):
        word = residue(lines[i])
        if word not in code:
            generators.append(i)
            code |= {value ^ word for value in code}
    require(len(code) == 16, "binary code size")
    require(all(word.bit_count() % 4 == 0 for word in code), "doubly even code")
    dual = {word for word in range(256)
            if all((word & other).bit_count() % 2 == 0 for other in code)}
    require(dual == code, "self-dual code")

    axis_indices = []
    for j in range(8):
        axis = tuple(2 if k == j else 0 for k in range(8))
        require(axis in roots, "missing doubled coordinate axis")
        axis_indices.append(next(i for i, row in enumerate(lines)
                                 if canonical_line(row) == axis))

    # sum of eight integer squares is four only for a doubled coordinate
    # axis or four signed unit coordinates. this enumerates all norm-two
    # vectors of {z in Z^8 : z mod 2 lies in code}, with metric dot/2.
    norm_two = set()
    for j in range(8):
        for sign in (-1, 1):
            norm_two.add(tuple(2 * sign if k == j else 0 for k in range(8)))
    for support in combinations(range(8), 4):
        if sum(1 << j for j in support) not in code:
            continue
        for signs in product((-1, 1), repeat=4):
            row = [0] * 8
            for j, sign in zip(support, signs):
                row[j] = sign
            norm_two.add(tuple(row))
    require({canonical_line(row) for row in norm_two} == roots,
            "complete construction-a root set")
    # index = |F2^8|/|code|; scaling the metric by 1/2 scales the
    # eight-dimensional gram determinant by 2^-8.
    index = 256 // len(code)
    require(index * index == 2 ** 8, "unimodular lattice")
    return {
        "codewords": sorted(code),
        "code_generator_label_indices": generators,
        "code_weight_distribution": dict(sorted(Counter(
            str(word.bit_count()) for word in code).items())),
        "axis_label_indices": axis_indices,
        "construction_a_index_in_Z8": index,
        "lattice_gram_determinant": 1,
        "signed_norm_two_vectors": len(norm_two),
        "root_lines": len(roots),
    }


def exterior_basis(lines, indices):
    blade = {0: 1}
    chosen = []
    for i in sorted(indices, key=lambda i: (i - SEED) % 120):
        candidate = wedge(blade, lines[i])
        if candidate:
            chosen.append(i)
            blade = candidate
    return chosen, blade


def binary_span_with_witnesses(classes, indices):
    span = {0: ()}
    for i in sorted(indices, key=lambda i: (i - SEED) % 120):
        span.update({mask ^ classes[i]: subset + (i,)
                     for mask, subset in list(span.items()) if mask ^ classes[i] not in span})
    require(power_of_two(len(span)), "binary span cardinality")
    return span


def pairing(a, b, gram_masks):
    return sum((b & row).bit_count() for i, row in enumerate(gram_masks)
               if a & (1 << i)) % 2


def quotient_certificate(lines):
    indices, blade = exterior_basis(lines, range(120))
    require(len(indices) == 8 and set(blade) == {255}, "ambient lattice rank")
    determinant = blade[255]
    require(abs(determinant) == 16, "root basis has index sixteen")
    basis = [lines[i] for i in indices]
    cofactors = []
    for omitted in range(8):
        minor = {0: 1}
        for i, row in enumerate(basis):
            if i != omitted:
                minor = wedge(minor, row)
        cofactors.append([(-1) ** (omitted + j) * minor.get(255 ^ (1 << j), 0)
                          for j in range(8)])
    coordinates = []
    for row in lines:
        numerators = [sum(a * b for a, b in zip(row, cofactor)) for cofactor in cofactors]
        require(all(value % determinant == 0 for value in numerators), "integral lattice coordinates")
        coordinates.append([value // determinant for value in numerators])
    gram = [[sum(a * b for a, b in zip(left, right)) // 2 for right in basis] for left in basis]
    gram_masks = [residue(row) for row in gram]
    classes = [residue(row) for row in coordinates]
    q_values = []
    for mask in range(256):
        representative = [sum(basis[i][j] for i in range(8) if mask & (1 << i))
                          for j in range(8)]
        norm_squared = sum(value * value for value in representative)
        require(norm_squared % 4 == 0, "even lattice norm")
        q_values.append((norm_squared // 4) % 2)
    certificate = {"basis_label_indices": indices, "basis_determinant": determinant,
                   "gram": gram, "gram_masks": gram_masks,
                   "integral_root_coordinates": coordinates, "root_classes": classes,
                   "quadratic_values": q_values}
    validate_quotient(lines, certificate)
    return certificate


def validate_quotient(lines, certificate):
    basis = [lines[i] for i in certificate["basis_label_indices"]]
    coordinates = certificate["integral_root_coordinates"]
    classes = certificate["root_classes"]
    require(len(coordinates) == len(classes) == 120, "quotient label count")
    for original, row, mask in zip(lines, coordinates, classes):
        require(len(row) == 8 and all(type(x) is int for x in row), "integer coordinate witness")
        require([sum(row[i] * basis[i][j] for i in range(8)) for j in range(8)] == original,
                "root coordinate reconstruction")
        require(mask == residue(row), "intrinsic root residue")
    require(len(set(classes)) == 120 and 0 not in classes, "distinct nonzero root classes")
    gram = [[sum(a * b for a, b in zip(left, right)) // 2 for right in basis] for left in basis]
    require(gram == certificate["gram"], "lattice gram binding")
    masks = [residue(row) for row in gram]
    require(masks == certificate["gram_masks"], "polar form binding")
    require([a for a in range(256) if all(pairing(a, 1 << i, masks) == 0 for i in range(8))] == [0],
            "nondegenerate polar form")
    q = certificate["quadratic_values"]
    require(len(q) == 256 and all(type(x) is int and x in (0, 1) for x in q), "quadratic value table")
    for a in range(256):
        value = sum(gram[i][i] // 2 for i in range(8) if a & (1 << i))
        value += sum(gram[i][j] for i in range(8) for j in range(i + 1, 8)
                     if a & (1 << i) and a & (1 << j))
        require(q[a] == value % 2, "quadratic norm identity")
    require(sum(q) == 120 and set(classes) == {a for a in range(256) if q[a]},
            "root to anisotropic-class bijection")
    for a in range(256):
        for b in range(256):
            require(q[a ^ b] ^ q[a] ^ q[b] == pairing(a, b, masks), "quadratic polarization")
    for i in range(120):
        for j in range(120):
            expected = (sum(a * b for a, b in zip(lines[i], lines[j])) // 2) % 2
            require(pairing(classes[i], classes[j], masks) == expected, "root pairing identity")


def frame_certificate(lines, classes, coordinates, frame, frame_id):
    require(type(frame) is list and all(type(i) is int and 0 <= i < 120 for i in frame),
            "frame label index")
    require(len(frame) == len(set(frame)), "duplicate frame label")
    rational_basis, blade = exterior_basis(lines, frame)
    rational_members = [i for i, row in enumerate(lines) if not wedge(blade, row)]
    require(rational_members == sorted(frame), "rational frame closure")
    span = binary_span_with_witnesses(classes, frame)
    closure = [i for i, mask in enumerate(classes) if mask in span]
    parity_rank = len(span).bit_length() - 1
    require(parity_rank == len(rational_basis), "selected-frame parity rank")
    extras = []
    for i in sorted(set(closure) - set(frame)):
        subset = span[classes[i]]
        difference = [sum(coordinates[k][j] for k in subset) - coordinates[i][j] for j in range(8)]
        require(all(value % 2 == 0 for value in difference), "even lattice lift")
        minor = wedge(blade, lines[i])
        require(minor, "extra root is rationally outside")
        key = min(minor)
        extras.append({"label": i, "subset_labels": list(subset),
                       "half_difference_lattice_coordinates": [value // 2 for value in difference],
                       "nonzero_augmented_minor": [key, minor[key]]})
    if extras:
        perpendicular = [i for i, row in enumerate(lines)
                         if all(sum(a * b for a, b in zip(row, lines[j])) == 0 for j in frame)]
        require(perpendicular == [extra["label"] for extra in extras],
                "extra roots are exactly the orthogonal-complement roots")
    return {"frame": frame_id, "rational_basis_labels": rational_basis,
            "rational_rank": len(rational_basis), "parity_rank": parity_rank,
            "rational_root_count": len(frame), "parity_root_count": len(closure),
            "parity_membership_mask_hex": format(sum(1 << i for i in closure), "030x"),
            "extra_roots": extras}


def validate_extra_witness(lines, coordinates, frame, record, extra):
    label = extra["label"]
    subset = extra["subset_labels"]
    require(label not in frame and set(subset).issubset(frame), "extra witness frame binding")
    require(len(subset) == len(set(subset)), "extra witness subset")
    difference = [sum(coordinates[k][j] for k in subset) - coordinates[label][j] for j in range(8)]
    require(difference == [2 * value for value in extra["half_difference_lattice_coordinates"]],
            "extra witness even lift")
    blade = {0: 1}
    for i in record["rational_basis_labels"] + [label]:
        blade = wedge(blade, lines[i])
    key, value = extra["nonzero_augmented_minor"]
    require(value != 0 and blade.get(key, 0) == value, "extra witness nonzero minor")


def analyze(word):
    require((word.get("format"), word.get("h"), word.get("v"), word.get("R"), word.get("form")) ==
            ("bitE8/1+mut", 8, 120, 420, "<x,y>/2"), "r420 geometry header")
    lines = word.get("lines")
    roots = root_certificate(lines)
    quotient = quotient_certificate(lines)
    require(type(word.get("frames")) is list and len(word["frames"]) == 672, "frame count")
    frames = [frame_certificate(lines, quotient["root_classes"], quotient["integral_root_coordinates"], f, i)
              for i, f in enumerate(word["frames"])]
    census = Counter((f["rational_rank"], f["parity_rank"], f["rational_root_count"], f["parity_root_count"])
                     for f in frames)
    for record in frames:
        for extra in record["extra_roots"]:
            validate_extra_witness(lines, quotient["integral_root_coordinates"],
                                   word["frames"][record["frame"]], record, extra)
    raw = [residue(row) for row in lines]
    return {"format": "r420-intrinsic-lattice-parity-v1", "assignment_seed": SEED,
            "root_lattice": roots, "quotient": quotient,
            "quadratic_census": {"zero": 136, "one": 120},
            "polarization_pairs_checked": 65536, "root_pairings_checked": 14400,
            "raw_coordinate_parity": {"distinct_classes": len(set(raw)),
                                      "zero_labels": [i for i, value in enumerate(raw) if not value]},
            "frame_count": len(frames), "root_memberships_checked": len(frames) * 120,
            "changed_closure_frames": sum(bool(f["extra_roots"]) for f in frames),
            "extra_memberships": sum(len(f["extra_roots"]) for f in frames),
            "changed_closures_add_exactly_perpendicular_roots": True,
            "frame_census": [{"rational_rank": key[0], "parity_rank": key[1],
                              "rational_roots": key[2], "parity_roots": key[3], "frames": count}
                             for key, count in sorted(census.items())], "frames": frames}


def rejection_controls(word, certificate):
    controls = []

    def rejects(name, action, reason):
        try:
            action()
        except Reject as error:
            require(str(error).startswith(reason), "wrong rejection: " + name + ": " + str(error))
            controls.append({"name": name, "rejection": str(error)})
        else:
            raise Reject("mutation accepted: " + name)

    lines = word["lines"]
    quotient = certificate["quotient"]
    changed = deepcopy(quotient)
    changed["root_classes"] = [residue(row) for row in lines]
    rejects("raw_coordinates_are_not_lattice_parity", lambda: validate_quotient(lines, changed),
            "intrinsic root residue")
    changed = deepcopy(quotient)
    changed["integral_root_coordinates"][SEED][0] += 1
    rejects("changed_integral_coordinate", lambda: validate_quotient(lines, changed),
            "root coordinate reconstruction")
    changed = deepcopy(quotient)
    changed["root_classes"][SEED], changed["root_classes"][SEED + 1] = (
        changed["root_classes"][SEED + 1], changed["root_classes"][SEED])
    rejects("swapped_label_classes", lambda: validate_quotient(lines, changed), "intrinsic root residue")
    changed = deepcopy(quotient)
    changed["gram"][0][1] += 1
    rejects("wrong_lattice_gram", lambda: validate_quotient(lines, changed), "lattice gram binding")
    changed = deepcopy(quotient)
    changed["gram_masks"][0] ^= 1
    rejects("wrong_polar_form", lambda: validate_quotient(lines, changed), "polar form binding")
    changed = deepcopy(quotient)
    changed["quadratic_values"] = [mask.bit_count() % 2 for mask in range(256)]
    rejects("omit_quadratic_cross_terms", lambda: validate_quotient(lines, changed), "quadratic norm identity")
    changed = deepcopy(quotient)
    changed["quadratic_values"] = [0] * 256
    rejects("use_norm_instead_of_half_norm", lambda: validate_quotient(lines, changed), "quadratic norm identity")

    record = next(f for f in certificate["frames"] if f["extra_roots"])
    frame = word["frames"][record["frame"]]
    extra = record["extra_roots"][0]
    changed_extra = deepcopy(extra)
    changed_extra["half_difference_lattice_coordinates"][0] += 1
    rejects("wrong_even_lift", lambda: validate_extra_witness(lines, quotient["integral_root_coordinates"],
            frame, record, changed_extra), "extra witness even lift")
    changed_extra = deepcopy(extra)
    changed_extra["nonzero_augmented_minor"][1] = 0
    rejects("zero_outside_minor", lambda: validate_extra_witness(lines, quotient["integral_root_coordinates"],
            frame, record, changed_extra), "extra witness nonzero minor")
    changed_extra = deepcopy(extra)
    changed_extra["subset_labels"] = [extra["label"]]
    rejects("subset_outside_frame", lambda: validate_extra_witness(lines, quotient["integral_root_coordinates"],
            frame, record, changed_extra), "extra witness frame binding")
    changed_lines = deepcopy(lines)
    changed_lines[SEED] = [-x for x in lines[SEED - 1]]
    rejects("antipodal_duplicate", lambda: root_certificate(changed_lines), "distinct root lines")
    return controls


def load_bound_word(root, pins):
    for relative, digest in pins["files_sha256"].items():
        path = root / relative
        require(path.is_file(), "missing pinned source: " + relative)
        require(sha256(path.read_bytes()).hexdigest() == digest, "changed pinned source: " + relative)
    with gzip.open(root / WORD, "rt", encoding="utf-8") as source:
        return json.load(source)


def verify(root, expected_path, write_path=None):
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    word = load_bound_word(root, pins)
    result = analyze(word)
    result["negative_controls"] = rejection_controls(word, result)
    if write_path is None:
        require(result == json.loads(expected_path.read_text(encoding="utf-8")),
                "certificate differs from complete replay")
    else:
        with write_path.open("x", encoding="utf-8", newline="\n") as output:
            summary = {key: value for key, value in result.items() if key != "frames"}
            output.write(json.dumps(summary, indent=2, sort_keys=True)[:-2])
            output.write(',\n  "frames": [\n')
            output.write(",\n".join("    " + json.dumps(row, sort_keys=True, separators=(",", ":"))
                                     for row in result["frames"]))
            output.write("\n  ]\n}\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=HERE.parents[1])
    parser.add_argument("--expected", type=Path, default=HERE / "EXPECTED.json")
    parser.add_argument("--write", type=Path, help="write a fresh certificate; refuses overwrite")
    args = parser.parse_args()
    try:
        result = verify(args.source_root, args.expected, args.write)
    except (Reject, OSError, ValueError, KeyError, TypeError) as error:
        print("fail_r420_lattice_parity: " + str(error), file=sys.stderr)
        return 1
    print("pass_r420_lattice_parity: 120 anisotropic classes; %d frames; %d changed closures; "
          "%d extra memberships; %d rejected controls" % (result["frame_count"],
          result["changed_closure_frames"], result["extra_memberships"], len(result["negative_controls"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
