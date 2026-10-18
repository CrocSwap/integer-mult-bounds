#!/usr/bin/env python3
"""Exact q=6 trajectory obstruction for four mixed affine targets over F2."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


R = 4
D = 3
N = R * D
I2 = ((1, 0), (0, 1))
ZERO = (0, 0)


def mul(f, g):
    a, b = f
    c, d = g
    return (
        tuple(tuple(sum(a[i][k] * c[k][j] for k in range(2)) % 2 for j in range(2)) for i in range(2)),
        tuple((sum(a[i][k] * d[k] for k in range(2)) + b[i]) % 2 for i in range(2)),
    )


def prod(*fs):
    z = (I2, ZERO)
    for f in fs:
        z = mul(z, f)
    return z


def xor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def mat_rank(rows):
    rows = list(rows)
    r = 0
    for col in range(N):
        p = next((i for i in range(r, N) if (rows[i] >> col) & 1), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        for i in range(N):
            if i != r and ((rows[i] >> col) & 1):
                rows[i] ^= rows[r]
        r += 1
    return r


def gmat(f):
    a, b = f
    return tuple(sum(a[i][j] << j for j in range(2)) | (b[i] << 2) for i in range(2)) + (4,)


def outer_uv(matrix):
    for u in range(1, 1 << D):
        for v in range(1, 1 << D):
            candidate = tuple(
                sum((((u >> i) & 1) * ((v >> j) & 1)) << j for j in range(D))
                for i in range(D)
            )
            if candidate == matrix:
                return u, v
    raise AssertionError("generator displacement did not factor as rank one")


def pack_register_vector(register_mask, vector):
    return sum(
        1 << (r * D + d)
        for r in range(R)
        if (register_mask >> r) & 1
        for d in range(D)
        if (vector >> d) & 1
    )


def mv(rows, vector):
    return sum(((row & vector).bit_count() & 1) << i for i, row in enumerate(rows))


def right_step(matrix, factor):
    _label, _x, _y, v, w = factor
    mvect = mv(matrix, v)
    return tuple(row ^ (w if (mvect >> i) & 1 else 0) for i, row in enumerate(matrix))


def make_data():
    a = (((1, 1), (0, 1)), ZERO)
    b = (((1, 0), (1, 1)), ZERO)
    tx = (I2, (1, 0))
    ty = (I2, (0, 1))
    labels = [a, b, tx, ty]
    assert all(prod(g, g) == (I2, ZERO) for g in labels)
    i3 = (1, 2, 4)
    uv = [outer_uv(xor(gmat(g), i3)) for g in labels]

    projectors = [(x, y) for x in range(1, 16) for y in range(1, 16) if (x & y).bit_count() & 1]
    assert len(projectors) == 120
    factors = []
    for label, (u, v) in enumerate(uv):
        for x, y in projectors:
            factors.append((label, x, y, pack_register_vector(x, u), pack_register_vector(y, v)))
    assert len(factors) == 480

    h = prod(a, b, a, tx)
    h_inv = prod(tx, a, b, a)
    blocks = [gmat(g) for g in (h, h_inv, tx, ty)]
    target_rows = []
    for r in range(R):
        for d in range(D):
            row = 0
            for e in range(D):
                if (blocks[r][d] >> e) & 1:
                    row |= 1 << (r * D + e)
            target_rows.append(row)
    target = tuple(target_rows)
    identity = tuple(1 << i for i in range(N))
    return projectors, factors, target, identity


def state_digest(states):
    payload = b"".join(
        b"".join(row.to_bytes(2, "little") for row in state)
        for state in sorted(states)
    )
    return hashlib.sha256(payload).hexdigest()


def q6_frontiers(factors, target, identity):
    layers = {target}
    result = []
    for depth in range(1, 7):
        edges = 0
        nxt = set()
        for state in layers:
            rank = mat_rank(xor(state, identity))
            assert rank == 7 - depth
            for factor in factors:
                candidate = right_step(state, factor)
                if mat_rank(xor(candidate, identity)) == rank - 1:
                    edges += 1
                    nxt.add(candidate)
        result.append({
            "depth": depth,
            "incoming_states": len(layers),
            "strict_drop_edges": edges,
            "unique_states": len(nxt),
            "states_sha256": state_digest(nxt),
        })
        layers = nxt
        if not layers:
            break
    assert not layers, "unexpected q=6 endpoint frontier"
    assert result[-1]["unique_states"] == 0
    return result


def direct_controls(factors, target, identity):
    factor_map = {(f[0], f[1], f[2]): f for f in factors}
    word = []
    for register, labels in enumerate(([0, 1, 0, 2], [2, 0, 1, 0], [2], [3])):
        e = 1 << register
        word.extend(factor_map[(label, e, e)] for label in labels)
    assert len(word) == 10
    direct = identity
    for factor in word:
        direct = right_step(direct, factor)
    assert direct == target

    deleted = identity
    for i, factor in enumerate(word):
        if i != 5:
            deleted = right_step(deleted, factor)
    assert deleted != target

    wrong = identity
    wrong_word = list(word)
    wrong_word[-1] = factor_map[(2, 1 << 3, 1 << 3)]
    for factor in wrong_word:
        wrong = right_step(wrong, factor)
    assert wrong != target

    for factor in factors:
        assert right_step(right_step(identity, factor), factor) == identity
    return {
        "direct_word_calls": len(word),
        "direct_word_endpoint": "target",
        "drop_call_control": "rejected",
        "wrong_label_control": "rejected",
        "all_480_factors_involutive": True,
    }


def q7_evidence():
    root = Path(__file__).parent
    program = root / "q7_trajectory_search.py"
    output = root / "Q7-OUTPUT.txt"
    lines = output.read_text().splitlines()
    rows = []
    for line in lines:
        match = re.fullmatch(
            r"depth (\d+) states (\d+) neutral0 (\d+) neutral1 (\d+) goal (True|False)",
            line,
        )
        if match:
            depth, states, neutral0, neutral1 = map(int, match.groups()[:4])
            rows.append({
                "depth": depth,
                "states": states,
                "neutral0": neutral0,
                "neutral1": neutral1,
                "goal": match.group(5) == "True",
            })
    assert [row["depth"] for row in rows] == list(range(1, 7))
    assert not any(row["goal"] for row in rows)
    assert rows[-1] == {
        "depth": 6,
        "states": 0,
        "neutral0": 0,
        "neutral1": 0,
        "goal": False,
    }
    return {
        "program": program.name,
        "program_sha256": hashlib.sha256(program.read_bytes()).hexdigest(),
        "output": output.name,
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "frontiers": rows,
        "endpoint_found": False,
    }


def compute_certificate():
    projectors, factors, target, identity = make_data()
    target_rank = mat_rank(xor(target, identity))
    assert target_rank == 6
    return {
        "schema_version": 1,
        "field": "F2",
        "target": "diag(h,h^-1,tx,ty) in the homogeneous affine 3x3 representation",
        "registers": 4,
        "target_displacement_rank": target_rank,
        "paid_labels": ["a", "b", "tx", "ty"],
        "rank_one_idempotents": len(projectors),
        "factors": len(factors),
        "q6_frontiers": q6_frontiers(factors, target, identity),
        "q6_endpoint_found": False,
        "controls": direct_controls(factors, target, identity),
        "q7_trajectory": q7_evidence(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    cert_path = Path(__file__).with_name("CERTIFICATE.json")
    actual = compute_certificate()
    if args.write_certificate:
        cert_path.write_text(json.dumps(actual, indent=2) + "\n")
    expected = json.loads(cert_path.read_text())
    assert actual == expected, "certificate differs from exact recomputation"
    digest = hashlib.sha256(cert_path.read_bytes()).hexdigest()
    print("PASS_AFFINE_MIXED_Q6_OBSTRUCTION")
    print(json.dumps({"certificate_sha256": digest, "frontiers": actual["q6_frontiers"], "controls": actual["controls"]}, sort_keys=True))


if __name__ == "__main__":
    main()
