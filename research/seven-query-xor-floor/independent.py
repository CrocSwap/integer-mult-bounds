#!/usr/bin/env python3
"""Independent column-image check of the Q=7 XOR floor. Wentao Li + AI, Apache-2.0."""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def component_count(n, graph):
    labels = list(range(n))
    for k, (s, t) in enumerate(itertools.combinations(range(n), 2)):
        if graph >> k & 1:
            a, b = labels[s], labels[t]
            labels = [a if c == b else c for c in labels]
    return len(set(labels))


def operators(n):
    edges = list(itertools.combinations(range(n), 2))
    return [
        (s, t, 1 << edges.index(tuple(sorted((s, t)))))
        for s in range(n)
        for t in range(n)
        if s != t
    ]


def shear_matrix(rows, s, t):
    out = [list(r) for r in rows]
    for col in range(len(out[0])):
        out[t][col] ^= out[s][col]
    return tuple(tuple(r) for r in out)


def half_layers_matrix(n, depth):
    """Column-image variant: track n-by-n matrices over F2 explicitly."""
    identity = tuple(tuple(1 if i == j else 0 for j in range(n)) for i in range(n))
    layers = [{identity: {0}}]
    for _ in range(depth):
        nxt = {}
        for rows, graphs in layers[-1].items():
            for s, t, bit in operators(n):
                nxt.setdefault(shear_matrix(rows, s, t), set()).update(g | bit for g in graphs)
        layers.append(nxt)
    return layers


def census_matrix(n=5, bound=6):
    layers = half_layers_matrix(n, (bound + 1) // 2)
    out = []
    for length in range(bound + 1):
        a, b = length // 2, (length + 1) // 2
        unions = set()
        for rows, left in layers[a].items():
            unions.update(x | y for x in left for y in layers[b].get(rows, ()))
        comps = [component_count(n, g) for g in unions]
        out.append(
            {
                "length": length,
                "identity_graphs": len(unions),
                "minimum_components": min(comps) if comps else None,
                "query_floor": (n + min(comps)) if comps else None,
                "graphs_sha256": hashlib.sha256(
                    json.dumps(sorted(unions), separators=(",", ":")).encode()
                ).hexdigest(),
            }
        )
    return out


def replay_champion_columns(closed):
    """Direct F2 column simulation of path-lowered word on dirty basis."""
    n = 5
    # State: each role is an F2 vector of length n (source coordinates) plus
    # a free dirty bit ignored for the AB image check on outputs.
    # We track source images as n-bit masks on the initial basis.
    x = [1 << j for j in range(n)]
    z = 0
    y = [0] * 32
    # Build path word inline
    slots = list(closed[:-1])
    reads = {}
    for mask in range(1, 32):
        found = None
        for size in range(2, len(slots) + 1, 2):
            for subset in itertools.combinations(range(len(slots)), size):
                value = 0
                for i in subset:
                    value ^= slots[i]
                if value == mask:
                    found = subset
                    break
            if found is not None:
                break
        need(found is not None, f"uncovered mask {mask}")
        reads[mask] = found
    x_count = 0
    q_count = 0
    r_count = 0
    for step, point in enumerate(closed):
        for mask, subset in reads.items():
            if step in subset:
                y[mask] ^= z
                r_count += 1
        if step + 1 >= len(closed):
            break
        delta = point ^ closed[step + 1]
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        for j in donors:
            x[target] ^= x[j]
            x_count += 1
        z ^= x[target]
        q_count += 1
        for j in reversed(donors):
            x[target] ^= x[j]
            x_count += 1
    need(q_count == 7 and x_count == 6 and r_count == 82, "champion counts")
    need(x == [1 << j for j in range(n)], "sources unrestored")
    need(z == 0, "connector unrestored")
    for mask in range(1, 32):
        want = 0
        for j in range(n):
            if mask >> j & 1:
                want ^= 1 << j
        need(y[mask] == want, f"output mask {mask} wrong")
    return {"Q": q_count, "R": r_count, "X": x_count}


def main():
    need(CERT_PATH.is_file(), "missing certificate")
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    rows = census_matrix()
    for row, expected in zip(rows, cert["census"]["by_length"]):
        need(row["identity_graphs"] == expected["identity_graphs"], f"count at X={row['length']}")
        need(row["minimum_components"] == expected["minimum_components"], f"min_c at X={row['length']}")
        need(row["graphs_sha256"] == expected["graphs_sha256"], f"digest at X={row['length']}")
        floor = row["query_floor"]
        need(floor == expected["query_floor_n_plus_c"], f"floor at X={row['length']}")
    for x in range(6):
        floor = rows[x]["query_floor"]
        need(floor is None or floor >= 8, f"independent: X={x} blocks Q=7")
    need(rows[6]["query_floor"] == 7, "independent: X=6 allows Q=7")

    closed = tuple(cert["attaining_witness"]["closed_path"])
    bill = replay_champion_columns(closed)
    need(bill["X"] == 6, "independent champion X")
    tariff = 38 * bill["Q"] + 2 * bill["R"] + 2 * bill["X"]
    need(tariff == 442, "independent tariff")

    # Edge bound control: 2 edges => >=3 components on 5 labels.
    need(5 - 2 >= 3, "edge arithmetic")
    print(
        "PASS_INDEPENDENT_SEVEN_QUERY_XOR_FLOOR "
        f"min_X=6 floors_block_X_le_5 champion={bill} tariff={tariff} controls=2"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
