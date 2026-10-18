#!/usr/bin/env python3
"""Source-bound scalar endpoint obstruction; standard library, exact arithmetic.

Independent audit with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor executable is imported; no network access or artifact writes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/work/complex-nine-native/DATA-PHASES.json"
PAYLOAD_SHA = "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa"
FIXTURE_SHA = "4fd648f7b5178bff5441bf364d58234b7bc1a43b924bc6da03013c948f1473b1"
FIXTURE_BLOB = "7ca668d7d50c7276e89b0f6f9575e1b9f1ad9ef6"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() & 1


def load_inputs():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
                 == row["sha256"], "input hash: " + row["path"])
    fixture = (HERE / "PR1825-CERTIFICATE.json").read_bytes()
    need(hashlib.sha256(fixture).hexdigest() == FIXTURE_SHA, "PR1825 fixture hash")
    fixture_source = sources["remote_sources"][0]
    need(fixture_source["sha256"] == FIXTURE_SHA
         and fixture_source["git_blob"] == FIXTURE_BLOB
         and fixture_source["commit"] == "d16fb8936795ff101e4d2f63cfdc6a25066ebabf",
         "PR1825 fixture provenance")
    git_object = b"blob " + str(len(fixture)).encode("ascii") + b"\0" + fixture
    need(hashlib.sha1(git_object).hexdigest() == FIXTURE_BLOB, "PR1825 Git blob")
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        stream = archive.extractfile(MEMBER)
        need(stream is not None, "missing selected phase payload")
        payload = stream.read()
    need(hashlib.sha256(payload).hexdigest() == PAYLOAD_SHA, "phase payload hash")
    data = json.loads(payload)
    recipes = sorted(data["recipes"], key=lambda row: row["port"])
    need([row["port"] for row in recipes] == list(range(112)), "port indexing")
    q = [row["q"] for row in recipes]
    need(len(set(q)) == 112 and all(0 < v < 512 and dot(v, v) for v in q),
         "selected odd distinct labels")
    need(all(row["terminal_Y_translation"] == row["q"] for row in recipes),
         "selected unpaid-line terminal correction")
    return q, json.loads(fixture)


def plane_frames(q, pairs):
    need(sorted(i for pair in pairs for i in pair) == list(range(len(q))),
         "matching coverage")
    frames = [None] * len(q)
    for i, j in pairs:
        need(i != j and dot(q[i], q[j]) == 0, "nonorthogonal matched labels")
        frames[i] = (q[i], q[j])
        frames[j] = (q[j], q[i])
    return frames


def columns_from_certificate(q, pairs, matrices):
    """Expand the published rank-one/rank-two choices, over F2 only here."""
    need(len(pairs) == len(matrices), "matrix inventory")
    columns = []
    for (i, j), m in zip(pairs, matrices):
        need(0 <= m < 16, "two-by-two matrix encoding")
        if not m:
            continue
        a, b, c, d = [(m >> k) & 1 for k in range(4)]
        if (a * d - b * c) & 1:
            columns.extend(((q[i], (q[i] if a else 0) ^ (q[j] if b else 0)),
                            (q[j], (q[i] if c else 0) ^ (q[j] if d else 0))))
        else:
            # A nonzero column x determines the unique binary row y.
            x = (a | (c << 1)) or (b | (d << 1))
            pivot = 0 if x & 1 else 1
            y = ((a | (b << 1)) if pivot == 0 else (c | (d << 1)))
            need(all(((x >> r) & 1) * ((y >> s) & 1)
                     == ((m >> (2 * r + s)) & 1)
                     for r in range(2) for s in range(2)), "rank-one factor")
            columns.append(((q[i] if x & 1 else 0) ^ (q[j] if x & 2 else 0),
                            (q[i] if y & 1 else 0) ^ (q[j] if y & 2 else 0)))
    return columns


def check_binary_identity(q, columns):
    need(all(sum(((a >> r) & 1) * ((b >> s) & 1) for a, b in columns) % 2
             == int(r == s) for r in range(9) for s in range(9)),
         "binary nine-dimensional identity")
    need(all(sum(dot(qi, a) * dot(qj, b) for a, b in columns) % 2 == dot(qi, qj)
             for qi in q for qj in q), "binary full port identity")


def masked(left, right):
    """True means a cross coefficient must vanish, not that it may be used."""
    return any(dot(a, b) for a in left for b in right)


def cross_failures(matrix, frames):
    return [(i, j, value) for i, row in enumerate(matrix) for j, value in enumerate(row)
            if i != j and masked(frames[i], frames[j]) and value != 0]


def require_cross_mask(matrix, frames):
    need(not cross_failures(matrix, frames), "forbidden scalar cross-entry")


def apply_scalar_columns(x, y, left, right):
    out = list(y)
    for d, t in zip(left, right):
        query = sum(value * coefficient for value, coefficient in zip(x, t))
        for i, coefficient in enumerate(d):
            out[i] += coefficient * query
    return out


def run():
    q, fixture = load_inputs()
    pairs = fixture["matching"]
    frames = plane_frames(q, pairs)
    columns = columns_from_certificate(q, pairs, fixture["plane_matrices_2bit_rows"])
    need(len(pairs) == 56 and len(columns) == 23, "published query expansion")
    check_binary_identity(q, columns)
    left = [[dot(v, a) for v in q] for a, _ in columns]
    right = [[dot(v, b) for v in q] for _, b in columns]
    integer_matrix = [[sum(d[i] * t[j] for d, t in zip(left, right))
                       for j in range(112)] for i in range(112)]
    binary_matrix = [[value % 2 for value in row] for row in integer_matrix]
    bad = cross_failures(integer_matrix, frames)
    parity_bad = cross_failures(binary_matrix, frames)
    mask_count = sum(i != j and masked(frames[i], frames[j])
                     for i in range(112) for j in range(112))
    need((mask_count, len(bad), len(parity_bad)) == (11560, 11559, 6608),
         "complete off-diagonal mask census")
    need(all(dot(q[i], q[j]) for i, j, _ in parity_bad), "parity obstruction support")
    need(q[0] == 11 and q[7] == 21 and frames[0] == (11, 19)
         and frames[7] == (21, 446), "minimal robust witness binding")
    need([[integer_matrix[i][j] for j in (0, 7)] for i in (0, 7)]
         == [[7, 5], [5, 7]], "two-role scalar matrix")
    need(dot(q[0], q[1]) == 0 and masked(frames[0], frames[1])
         and integer_matrix[0][1] == 4, "line-free is not plane-free witness")

    # Replay the literal scalar interpretation on every formal dirty column.
    for j in range(112):
        basis = [int(i == j) for i in range(112)]
        need(apply_scalar_columns(basis, [0] * 112, left, right)
             == [integer_matrix[i][j] for i in range(112)], "source column replay")
        need(apply_scalar_columns([0] * 112, basis, left, right) == basis,
             "arbitrary dirty target preservation")
    x = [int(i == 7) for i in range(112)]
    y = [11 if i == 0 else (-3 if i == 7 else 0) for i in range(112)]
    dirty = apply_scalar_columns(x, y, left, right)
    need(dirty[0] == 16 and y[0] == 11, "dirty cross-port counterexample")

    # Positive fixture: arbitrary entries on orthogonal-plane pairs are allowed.
    fitting = [[int(i == j) if masked(frames[i], frames[j]) else 17
                for j in range(112)] for i in range(112)]
    require_cross_mask(fitting, frames)
    need(all(fitting[i][i] == 1 for i in range(112)), "positive endpoint diagonal")
    controls = []

    def reject(name, callback):
        try:
            callback()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("control accepted: " + name)

    reject("integer literal scalar lift", lambda: require_cross_mask(integer_matrix, frames))
    reject("binary pairing as scalar endpoint", lambda: require_cross_mask(binary_matrix, frames))
    reject("omitted binary factor", lambda: check_binary_identity(q, columns[:-1]))
    altered = list(fixture["plane_matrices_2bit_rows"])
    altered[0] ^= 1
    reject("mutated plane matrix", lambda: check_binary_identity(
        q, columns_from_certificate(q, pairs, altered)))
    altered_pairs = [list(pair) for pair in pairs]
    altered_pairs[0][1] = 7
    reject("invalid matching", lambda: plane_frames(q, altered_pairs))
    changed = [list(row) for row in fitting]
    changed[0][1] = 4
    reject("old-line mask substituted for plane mask", lambda: require_cross_mask(changed, frames))
    return {"status": "PASS_PAIRED_PLANE_SCALAR_MASK_OBSTRUCTION",
            "ports": 112, "planes": 56, "binary_columns": 23,
            "binary_identity_entries": 12544, "masked_offdiagonal_entries": mask_count,
            "integer_mask_failures": len(bad), "parity_forced_failures": len(parity_bad),
            "witness_ports": [0, 7], "witness_labels": [q[0], q[7]],
            "witness_scalar_matrix": [[7, 5], [5, 7]],
            "dirty_target_actual": dirty[0], "dirty_target_required": y[0],
            "dirty_basis_columns": 224, "negative_controls": controls,
            "scope": "Fixed binary factors and parity-preserving integral lifts; zero-copy endpoint corrections only. No universal plane-port obstruction or new kappa."}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
