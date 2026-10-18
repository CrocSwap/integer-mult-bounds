#!/usr/bin/env python3
"""Exact scalar identity fit for the selected paired-plane endpoint."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
ARCHIVE_PATH = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PORTS = 112
DIMENSION = 9


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_input_pins() -> dict:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    need(sources["base_commit"] == "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
         "source-manifest base commit")
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        path = ROOT / row["path"]
        need(path.is_file(), "missing pinned input: " + row["path"])
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        need(digest == row["sha256"], "live input hash mismatch: " + row["path"])
    return sources


def load_selected_labels() -> list[int]:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    archive_path = ROOT / ARCHIVE_PATH
    archive_bytes = archive_path.read_bytes()
    archive_hash = hashlib.sha256(archive_bytes).hexdigest()
    with tarfile.open(archive_path, "r:gz") as tf:
        member = tf.extractfile(ARCHIVE_MEMBER)
        need(member is not None, "selected DATA-PHASES entry missing")
        payload = member.read()
    payload_hash = hashlib.sha256(payload).hexdigest()
    cert_path = ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json"
    cert = json.loads(cert_path.read_text(encoding="utf-8"))
    need(archive_hash == cert["selected_archive_sha256"], "selected archive/certificate mismatch")
    need(payload_hash == cert["selected_payload_sha256"], "selected payload/certificate mismatch")
    need(cert["port_count"] == PORTS and cert["label_space_dimension"] == DIMENSION,
         "selected certificate dimensions")
    data = json.loads(payload)
    need(data["ports"] == PORTS, "selected recipe port count")
    recipes = sorted(data["recipes"], key=lambda row: row["port"])
    need(len(recipes) == PORTS, "selected recipe count")
    need([row["port"] for row in recipes] == list(range(PORTS)), "selected port order")
    labels = [row["q"] for row in recipes]
    need(len(set(labels)) == PORTS, "selected labels are not distinct")
    need(all(isinstance(q, int) and 0 < q < (1 << DIMENSION) for q in labels),
         "selected label is not a nonzero 9-bit vector")
    need({q.bit_count() for q in labels} == {3, 7}, "selected label weights")
    return labels


def dot(a: int, b: int) -> int:
    return (a & b).bit_count() & 1


def validate_matching(labels: list[int], pairs: list[list[int]]) -> None:
    used: list[int] = []
    for pair in pairs:
        need(isinstance(pair, list) and len(pair) == 2, "matching edge shape")
        i, j = pair
        need(0 <= i < PORTS and 0 <= j < PORTS and i != j, "matching port range/distinctness")
        need(dot(labels[i], labels[j]) == 0, "matching edge is not zero-dot")
        used.extend((i, j))
    need(len(pairs) == PORTS // 2, "matching edge count")
    need(sorted(used) == list(range(PORTS)), "matching is not a perfect cover")


def plane_orthogonal(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return all(dot(a, b) == 0 for a in left for b in right)


def rank_f2(matrix: list[list[int]]) -> int:
    rows = [sum((value & 1) << j for j, value in enumerate(row)) for row in matrix]
    rank = 0
    width = len(matrix[0]) if matrix else 0
    for col in range(width):
        pivot = next((r for r in range(rank, len(rows)) if (rows[r] >> col) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for r in range(len(rows)):
            if r != rank and ((rows[r] >> col) & 1):
                rows[r] ^= rows[rank]
        rank += 1
    return rank


def build_identity_fit(pairs: list[list[int]]) -> list[list[int]]:
    matrix = [[0] * PORTS for _ in range(PORTS)]
    for i, j in pairs:
        # The two columns of each plane term are e_i and e_j on both sides.
        matrix[i][i] += 1
        matrix[j][j] += 1
    return matrix


def validate_scalar_fit(matrix: list[list[int]], labels: list[int], pairs: list[list[int]]) -> int:
    need(len(matrix) == PORTS and all(len(row) == PORTS for row in matrix),
         "scalar matrix shape")
    plane_for_port: list[tuple[int, int] | None] = [None] * PORTS
    for i, j in pairs:
        plane = (labels[i], labels[j])
        plane_for_port[i] = plane
        plane_for_port[j] = plane
    need(all(plane is not None for plane in plane_for_port), "unassigned plane port")
    forbidden = 0
    for i in range(PORTS):
        need(matrix[i][i] == 1, "scalar decoder diagonal is not one")
        for j in range(PORTS):
            if i == j:
                continue
            if not plane_orthogonal(plane_for_port[i], plane_for_port[j]):
                forbidden += 1
                need(matrix[i][j] == 0, "nonzero scalar entry across nonorthogonal planes")
    return forbidden


def apply_c(state: dict[int, tuple[int, int]], mask: int) -> dict[int, tuple[int, int]]:
    """Apply C_mask=((1+i)I+(1-i)X_mask)/2 with an exact common denominator."""
    out: dict[int, tuple[int, int]] = {}

    def add(index: int, real: int, imag: int) -> None:
        old_real, old_imag = out.get(index, (0, 0))
        out[index] = (old_real + real, old_imag + imag)

    for index, (real, imag) in state.items():
        add(index, real - imag, real + imag)
        add(index ^ mask, real + imag, imag - real)
    return {index: value for index, value in out.items() if value != (0, 0)}


def plane_translation(labels: list[int], pair: list[int], start: int,
                      omit_last: bool = False) -> dict[int, tuple[int, int]]:
    i, j = pair
    q, r = labels[i], labels[j]
    state = {start: (1, 0)}
    word = (q, r, q, r)
    if omit_last:
        word = word[:-1]
    for mask in word:
        state = apply_c(state, mask)
    return state


def clean_state(state: dict[int, tuple[int, int]]) -> dict[int, tuple[int, int]]:
    return {index: value for index, value in state.items() if value != (0, 0)}


def apply_scalar_endpoint(matrix: list[list[int]], source: list[int],
                          dirty_target: list[int]) -> list[int]:
    need(len(source) == PORTS and len(dirty_target) == PORTS, "dirty endpoint vector shape")
    return [dirty_target[i] + sum(matrix[i][j] * source[j] for j in range(PORTS))
            for i in range(PORTS)]


def literal_assignments(path: Path) -> dict[str, object]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result: dict[str, object] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        value = ast.literal_eval(node.value)
        for target in node.targets:
            if isinstance(target, ast.Name):
                result[target.id] = value
            elif isinstance(target, ast.Tuple) and isinstance(value, tuple):
                for name, item in zip(target.elts, value):
                    if isinstance(name, ast.Name):
                        result[name.id] = item
    return result


def load_ceiling_module(path: Path):
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    need(spec is not None and spec.loader is not None, "pinned ceiling loader")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rejects(callback) -> bool:
    try:
        callback()
    except (ValueError, IndexError):
        return True
    return False


def main() -> None:
    sources = check_input_pins()
    labels = load_selected_labels()
    cert = json.loads((ROOT / "research/paired-plane-port-matching-seed6c563a/CERTIFICATE.json")
                      .read_text(encoding="utf-8"))
    pairs = cert["matching"]
    validate_matching(labels, pairs)
    need(len({tuple(sorted((labels[i], labels[j]))) for i, j in pairs}) == PORTS // 2,
         "duplicate selected plane")

    # Each local term has source and target columns e_i,e_j and matrix I_2.
    fit = build_identity_fit(pairs)
    need(all(fit[i][j] == int(i == j) for i in range(PORTS) for j in range(PORTS)),
         "sum of plane terms is not I_112")
    forbidden_count = validate_scalar_fit(fit, labels, pairs)
    need(forbidden_count == 11560, "selected nonorthogonal-plane mask census")

    dirty = [2 * i + 1 for i in range(PORTS)]
    dirty_columns_checked = 0
    for source_index in range(PORTS):
        source = [int(j == source_index) for j in range(PORTS)]
        expected = [dirty[i] + int(i == source_index) for i in range(PORTS)]
        need(apply_scalar_endpoint(fit, source, dirty) == expected,
             "source basis changed a dirty scalar target")
        dirty_columns_checked += 1
    zero_source = [0] * PORTS
    for target_index in range(PORTS):
        target = [int(i == target_index) for i in range(PORTS)]
        need(apply_scalar_endpoint(fit, zero_source, target) == target,
             "zero-source scalar endpoint changed a dirty target")
        dirty_columns_checked += 1
    need(dirty_columns_checked == 224, "dirty scalar endpoint coverage")

    charge_histogram: dict[int, int] = {}
    copy_charge = 0
    for i, j in pairs:
        block = [[dot(labels[a], labels[b]) for b in (i, j)] for a in (i, j)]
        need(block == [[1, 0], [0, 1]], "matched-plane pairing block is not I_2")
        charge = rank_f2(block)
        charge_histogram[charge] = charge_histogram.get(charge, 0) + 1
        copy_charge += charge
    need(charge_histogram == {2: 56} and copy_charge == 112, "B14 support-pairing invoice")

    # Check the exact local plane correction on every computational basis state.
    endpoint_checks = 0
    for pair in pairs:
        i, j = pair
        q, r = labels[i], labels[j]
        need(q != r and (q ^ r) != 0, "degenerate matched plane")
        for start in range(1 << DIMENSION):
            actual = plane_translation(labels, pair, start)
            expected = {start ^ q ^ r: (16, 0)}
            need(clean_state(actual) == expected, "C_E^2 is not X_(q_i+q_j)")
            endpoint_checks += 1

    # Recompute the changed-word packing screen from the pinned levers and ceiling.
    lever_path = ROOT / "research/complex-local-word-ceiling/levers.py"
    vals = literal_assignments(lever_path)
    base_profile = vals.get("WORD")
    need(base_profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
         "pinned selected local profile")
    need((vals.get("M"), vals.get("FAM"), vals.get("ST")) == (73, 896, 9),
         "pinned selected ceiling parameters")
    candidate_profile = dict(base_profile)
    removed = candidate_profile.pop(8)
    need(removed == 8, "expected eight rank-8 centre terms")
    candidate_profile[2] += len(pairs)
    need(sum(rank * count for rank, count in candidate_profile.items()) == 5634,
         "candidate local rank mass")

    ceiling_path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    ceiling = load_ceiling_module(ceiling_path)
    grid = Fraction(1, 10**12)
    lo, hi = ceiling.ceiling(candidate_profile, 73, 896, 9, 112,
                             grid=grid, unpaid=2)
    published_profile = dict(base_profile)
    published_profile.pop(8)
    published_profile.update({7: 9, 9: 7})
    old_lo, old_hi = ceiling.ceiling(published_profile, 73, 896, 9, 126,
                                     grid=grid, unpaid=2)
    need(hi == Fraction(4078546959, 10**12), "identity-fit exact ceiling")
    need(old_hi == Fraction(3447203501, 10**12), "published plane-profile control")
    need(lo < hi and old_lo < old_hi and hi > old_hi, "ceiling brackets/order")
    model = ceiling.model(candidate_profile, 73, 896, 9, 112, unpaid=2)
    need(model["local_mass"] == 5634 and model["idle_mass"] == Fraction(13918, 9),
         "candidate changed-word budget")

    # Negative controls: incomplete matching, omitted pair, forbidden cross-entry,
    # and a missing final plane-correction operation must each be detected.
    bad_matching = [list(pair) for pair in pairs]
    bad_matching[0] = [bad_matching[0][0], bad_matching[0][0]]
    need(rejects(lambda: validate_matching(labels, bad_matching)),
         "duplicate/nonedge matching control was accepted")
    omitted = build_identity_fit(pairs[:-1])
    need(rejects(lambda: need(all(omitted[i][j] == int(i == j)
                                  for i in range(PORTS) for j in range(PORTS)),
                             "omitted plane must fail")),
         "omitted plane control was accepted")
    wrong_cross = [row[:] for row in fit]
    cross = next((i, j) for i in range(PORTS) for j in range(PORTS)
                 if i != j and not plane_orthogonal(
                     next((labels[a], labels[b]) for a, b in pairs if i in (a, b)),
                     next((labels[a], labels[b]) for a, b in pairs if j in (a, b))))
    wrong_cross[cross[0]][cross[1]] = 1
    need(rejects(lambda: validate_scalar_fit(wrong_cross, labels, pairs)),
         "forbidden cross-entry control was accepted")
    sample_pair = pairs[0]
    target = {0 ^ labels[sample_pair[0]] ^ labels[sample_pair[1]]: (16, 0)}
    need(clean_state(plane_translation(labels, sample_pair, 0, omit_last=True)) != target,
         "missing endpoint-operation control was accepted")

    print("PASS_PAIRED_PLANE_IDENTITY_SCALAR_FIT")
    print("ports=112 planes=56 scalar_entries=12544 nonorthogonal_mask_entries=11560")
    print("copy_charge=112 support_rank_histogram={2:56} local_mass=5634")
    print("a_lo=", lo, "a_hi=", hi, "kappa_cap=", hi / (1 + hi))
    print("dirty_scalar_columns=", dirty_columns_checked,
          "endpoint_basis_checks=", endpoint_checks,
          "negative_controls=4; routing, hosting, restoration and precision remain unpriced")


if __name__ == "__main__":
    main()
