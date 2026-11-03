"""Exact three-queue bootstrap optimizer. Produced by Nick Petalas."""

import argparse
from array import array
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GRAPH = "research/pg16m-bootstrap-orders/graph16_59.txt"
GRAPH_SHA = "6a12ff61f721449228957ea9ab691536fbaa24f45c30bdf3a8fcbf8655f36a6e"
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
         "verify.py", "independent.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_small(path):
    with path.open("rb") as stream:
        data = stream.read(131073)
    require(len(data) <= 131072, "file size bound")
    return data


def parse_graph(text):
    require(len(text) <= 131072, "graph text bound")
    words = text.split()
    require(len(words) == 8738, "graph token count")
    numbers = [int(word) for word in words]
    require(numbers[:2] == [546, 16], "graph header")
    rows = [tuple(numbers[2 + 16*v:18 + 16*v]) for v in range(546)]
    for v, row in enumerate(rows):
        require(len(set(row)) == 16, "duplicate neighbor")
        require(all(0 <= u < 546 and (u < 273) != (v < 273) for u in row),
                "graph vertex or bipartition")
    require(all(v in rows[u] for v, row in enumerate(rows) for u in row),
            "asymmetric graph")
    return rows


def load_graph():
    data = read_small(HERE.parents[1] / GRAPH)
    require(hashlib.sha256(data).hexdigest() == GRAPH_SHA, "graph source hash")
    return parse_graph(data.decode("ascii"))


def queues(phase):
    require(type(phase) is int and 0 <= phase < 8, "phase domain")
    result = []
    for residue in range(3):
        row = []
        for t in range(91):
            p = 118 * (3*t + residue) % 273
            pair = (p, 273 + (p + 81) % 273)
            row.extend(reversed(pair) if phase >> residue & 1 else pair)
        result.append(tuple(row))
    return tuple(result)


def validate(adj, q, half):
    require(type(half) is int and 0 <= half <= 8, "half-degree domain")
    require(len(q) == 3 and 1 <= len(q[0]) <= 182, "queue count or length")
    length = len(q[0])
    require(all(len(row) == length for row in q), "unequal queue lengths")
    require(len(adj) == 3*length, "vertex count")
    require(sorted(v for row in q for v in row) == list(range(len(adj))),
            "queue partition")
    for v, row in enumerate(adj):
        require(len(row) == len(set(row)) == 2*half, "graph degree")
        require(all(type(u) is int and 0 <= u < len(adj) and u != v for u in row),
                "graph vertex")
    require(all(v in adj[u] for v, row in enumerate(adj) for u in row),
            "graph symmetry")
    return length


def prefixes(adj, q):
    result = []
    for stream in q:
        table = []
        for neighbors in adj:
            row = array("B", [0])
            for v in stream:
                row.append(row[-1] + (v in neighbors))
            table.append(row)
        result.append(table)
    return result


def optimize(adj, q, half):
    """Incoming-edge Bellman recurrence, retaining every state for traceback."""
    length = validate(adj, q, half)
    side = length + 1
    c0, c1, c2 = prefixes(adj, q)
    q0, q1, q2 = q
    f = array("H", [65535]) * side**3
    f[0] = 0
    for i in range(side):
        for j in range(side):
            z = (i*side + j)*side
            if i:
                v = q0[i-1]
                base0, vals0 = half-c0[v][i-1]-c1[v][j], c2[v]
            if j:
                v = q1[j-1]
                base1, vals1 = half-c0[v][i]-c1[v][j-1], c2[v]
            for k in range(side):
                best = f[z+k]
                if i:
                    d = base0-vals0[k]
                    candidate = f[z-side*side+k] + (d if d > 0 else 0)
                    if candidate < best:
                        best = candidate
                if j:
                    d = base1-vals1[k]
                    candidate = f[z-side+k] + (d if d > 0 else 0)
                    if candidate < best:
                        best = candidate
                if k:
                    v = q2[k-1]
                    d = half-c0[v][i]-c1[v][j]-c2[v][k-1]
                    candidate = f[z+k-1] + (d if d > 0 else 0)
                    if candidate < best:
                        best = candidate
                f[z+k] = best
    require(max(f) <= half*len(adj), "finite distance bound")
    return f, (c0, c1, c2)


def traceback(q, half, f, tables):
    side = len(q[0]) + 1
    position = [side-1]*3
    backwards = []
    for _ in range(3*(side-1)):
        target = f[(position[0]*side + position[1])*side + position[2]]
        for stream in range(3):
            if position[stream] == 0:
                continue
            before = position.copy()
            before[stream] -= 1
            v = q[stream][before[stream]]
            seen = sum(tables[a][v][before[a]] for a in range(3))
            previous = f[(before[0]*side + before[1])*side + before[2]]
            if previous + max(0, half-seen) == target:
                backwards.append(v)
                position = before
                break
        else:
            raise ValueError("missing tight predecessor")
    require(position == [0, 0, 0], "traceback origin")
    return tuple(reversed(backwards))


def literal_cost(adj, order, q, half):
    require(sorted(order) == list(range(len(adj))), "order permutation")
    owner = {v: a for a, row in enumerate(q) for v in row}
    position = [0, 0, 0]
    seen, cost, cut, peak = set(), 0, 0, 0
    histogram = [0]*(2*half + 1)
    for v in order:
        a = owner[v]
        require(q[a][position[a]] == v, "order violates queue")
        position[a] += 1
        earlier = sum(u in seen for u in adj[v])
        histogram[earlier] += 1
        cost += max(0, half-earlier)
        cut += 2*half - 2*earlier
        peak = max(peak, cut)
        seen.add(v)
    require(cut == 0 and sum(histogram) == len(adj), "literal ledger")
    return cost, peak, histogram


def brute(adj, q, half):
    """Every distinct queue-label shuffle on the small control domains."""
    length = len(q[0])
    require(length <= 2, "brute-force domain")
    best, count = 65535, 0
    for first in itertools.combinations(range(3*length), length):
        remaining = [t for t in range(3*length) if t not in first]
        for second in itertools.combinations(remaining, length):
            word, positions = [], [0, 0, 0]
            for t in range(3*length):
                a = 0 if t in first else 1 if t in second else 2
                word.append(q[a][positions[a]])
                positions[a] += 1
            value = literal_cost(adj, word, q, half)[0]
            best, count = min(best, value), count+1
    return best, count


def controls(adj):
    cases, shuffles = 0, 0
    for length in (1, 2):
        size = 3*length
        for half in range((size-1)//2 + 1):
            small = [tuple((v+d) % size for d in range(1, size)
                           if min(d, size-d) <= half) for v in range(size)]
            for phase in range(8):
                q = tuple(tuple(reversed(range(a*length, (a+1)*length)))
                          if phase >> a & 1 else tuple(range(a*length, (a+1)*length))
                          for a in range(3))
                f, tables = optimize(small, q, half)
                expected, count = brute(small, q, half)
                require(f[-1] == expected, "literal shuffle oracle")
                order = traceback(q, half, f, tables)
                require(literal_cost(small, order, q, half)[0] == expected,
                        "small attaining order")
                cases, shuffles = cases+1, shuffles+count
    bad = [((adj, (queues(0)[0],)*3, 8), "queue partition"),
           ((adj, queues(0), 7), "graph degree"),
           ((adj, queues(0)[:2], 8), "queue count or length")]
    for args, reason in bad:
        try:
            optimize(*args)
        except ValueError as exc:
            require(str(exc) == reason, "unexpected rejection reason")
            continue
        raise ValueError("accepted invalid " + reason)
    return {"tiny_domains": cases, "literal_shuffles": shuffles,
            "rejected_optimizer_inputs": len(bad)}


def receipt(result):
    hashes = {}
    for name in FILES:
        hashes[name] = hashlib.sha256(read_small(HERE / name)).hexdigest()
    return {"status": "PASS_PG16_THREE_COSET_BOOTSTRAP", "result": result,
            "graph_sha256": GRAPH_SHA, "package_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--orders", action="store_true", help="include all eight attaining orders")
    args = parser.parse_args()
    adj = load_graph()
    small = controls(adj)
    results = []
    for phase in range(8):
        q = queues(phase)
        f, tables = optimize(adj, q, 8)
        require(f[-1] == 784, "changed declared family minimum")
        order = traceback(q, 8, f, tables)
        value, peak, histogram = literal_cost(adj, order, q, 8)
        require(value == f[-1], "attainment")
        record = {"phase": phase, "minimum": value, "peak_cut": peak,
                  "earlier_neighbor_histogram": histogram,
                  "order_sha256": hashlib.sha256(str(order).encode("ascii")).hexdigest()}
        if args.orders:
            record["order"] = order
        results.append(record)
        del f, tables
    print(json.dumps(receipt({"families": results, "states_per_family": 183**3,
                              "arcs_per_family": 3*182*183**2,
                              "controls": small}), sort_keys=True))


if __name__ == "__main__":
    main()
