"""Reverse-order, rolling-slice oracle. Produced by Nick Petalas.

This file imports no primary optimizer and stores no full Bellman table.
"""

from array import array
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRAPH = HERE.parents[1] / "research/pg16m-bootstrap-orders/graph16_59.txt"


def insist(condition, message):
    if not condition:
        raise ValueError(message)


def read_small(path):
    with path.open("rb") as stream:
        raw = stream.read(131073)
    insist(len(raw) <= 131072, "file size bound")
    return raw


def graph():
    raw = read_small(GRAPH)
    insist(len(raw) < 131072 and hashlib.sha256(raw).hexdigest() ==
           "6a12ff61f721449228957ea9ab691536fbaa24f45c30bdf3a8fcbf8655f36a6e",
           "source graph bytes")
    lines = raw.decode("ascii").splitlines()
    insist(lines[0] == "546 16" and len(lines) == 547, "source graph shape")
    adj = [frozenset(map(int, line.split())) for line in lines[1:]]
    insist(all(len(row) == 16 for row in adj), "source degrees")
    insist(all(0 <= u < 546 and v in adj[u] and (v < 273) != (u < 273)
               for v, row in enumerate(adj) for u in row), "source incidence")
    return adj


def reversed_streams(mask):
    insist(type(mask) is int and 0 <= mask < 8, "phase")
    streams = [[], [], []]
    for index in range(273):
        a = index % 3
        point = 118*index % 273
        line = 273 + (point+81) % 273
        streams[a].extend((line, point) if mask & (1 << a) else (point, line))
    result = tuple(tuple(row[::-1]) for row in streams)
    insist(all(len(row) == 182 for row in result), "stream lengths")
    insist(len(set(v for row in result for v in row)) == 546, "partition")
    return result


def neighbor_positions(adj, streams):
    positions = [{v: t for t, v in enumerate(row)} for row in streams]
    result = []
    for a in range(3):
        rows = []
        for neighbors in adj:
            marked = array("B", [0])*183
            for v in neighbors:
                if v in positions[a]:
                    marked[positions[a][v]+1] = 1
            for t in range(1, 183):
                marked[t] += marked[t-1]
            rows.append(marked)
        result.append(rows)
    return result


def reverse_minimum(adj, streams):
    """Reversal preserves cost on this 16-regular graph; keep two i-slices."""
    c0, c1, c2 = neighbor_positions(adj, streams)
    a, b, c = streams
    previous = array("H", [65535])*(183*183)
    for i in range(183):
        current = array("H", [65535])*(183*183)
        if i == 0:
            current[0] = 0
        for j in range(183):
            offset = j*183
            if i:
                v = a[i-1]
                first_base, first_tail = 8-c0[v][i-1]-c1[v][j], c2[v]
            if j:
                v = b[j-1]
                second_base, second_tail = 8-c0[v][i]-c1[v][j-1], c2[v]
            for k in range(183):
                best = current[offset+k]
                if i:
                    deficit = first_base-first_tail[k]
                    candidate = previous[offset+k] + (deficit if deficit > 0 else 0)
                    if candidate < best:
                        best = candidate
                if j:
                    deficit = second_base-second_tail[k]
                    candidate = current[offset-183+k] + (deficit if deficit > 0 else 0)
                    if candidate < best:
                        best = candidate
                if k:
                    v = c[k-1]
                    deficit = 8-c0[v][i]-c1[v][j]-c2[v][k-1]
                    candidate = current[offset+k-1] + (deficit if deficit > 0 else 0)
                    if candidate < best:
                        best = candidate
                current[offset+k] = best
        previous = current
    insist(previous[-1] < 65535, "reachable terminal")
    return previous[-1]


def reversal_controls(adj):
    orders = [tuple(range(546)), tuple(range(545, -1, -1)),
              tuple(v for p in range(273) for v in (p, p+273))]
    for order in orders:
        rank = {v: t for t, v in enumerate(order)}
        degrees = [sum(rank[u] < rank[v] for u in adj[v]) for v in order]
        forward = sum(max(0, 8-j) for j in degrees)
        backward = sum(max(0, j-8) for j in degrees)
        insist(forward == backward and sum(degrees) == 4368, "reversal ledger")
    return len(orders)


def main():
    adj = graph()
    values = [reverse_minimum(adj, reversed_streams(mask)) for mask in range(8)]
    insist(values == [784]*8, "reverse family values")
    hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "verify.py", "independent.py"):
        hashes[name] = hashlib.sha256(read_small(HERE / name)).hexdigest()
    print(json.dumps({"status": "PASS_PG16_THREE_COSET_REVERSE_ORACLE",
                      "minima": values, "states": 8*183**3,
                      "reversal_controls": reversal_controls(adj),
                      "package_sha256": hashes}, sort_keys=True))


if __name__ == "__main__":
    main()
