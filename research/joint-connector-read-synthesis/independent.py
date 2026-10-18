"""Separate physical-row layered frontier; no synthesis imports. Apache-2.0."""
from hashlib import sha256
import json


def read_bill(pool, targets):
    reached = {0}
    wave = {0}
    bills = {0: 0}
    k = 0
    while wave:
        k += 1
        wave = {a ^ b for a in wave for b in pool} - reached
        reached.update(wave)
        bills.update((a, k) for a in wave)
    return [bills.get(t) for t in targets]


def frontier(source, colors, targets, optimum, cap=250000):
    n = len(colors)
    # Physical formal rows: bits 0,1 encode old root dirt; bit j+2 is B_j x_j.
    root = [1, 2]
    pool = set(root + [root[0] ^ root[1]])
    for j in source:
        for k in range(2):
            if colors[j] & (1 << k):
                root[k] ^= 1 << (j+2)
        pool.update((root[0], root[1], root[0] ^ root[1]))
    desired = [m << 2 for m in targets]
    minimum = read_bill(pool, desired)
    # Each level closes every free source transition, then takes exactly one paid shear.
    pending = {(0, 1, 2, frozenset((1,)))}
    earlier = set()
    canonical = []
    layers = []
    vectors = sorted(((v & 3) << n) | (v >> 2) for v in pool)
    index = {v: i for i, v in enumerate(vectors)}
    terminal_checks = 0
    for cost in range(optimum+1):
        layer = pending - earlier
        todo = list(layer)
        while todo:
            cut, a, b, seen = todo.pop()
            if cut == len(source):
                continue
            c = colors[source[cut]]
            if (a & c).bit_count() % 2 != 1 or (b & c).bit_count() % 2 != 0:
                continue
            aa = a ^ (1 << (source[cut]+2))
            state = (cut+1, aa, b, seen | {aa})
            if state not in earlier and state not in layer:
                layer.add(state)
                todo.append(state)
            if len(earlier) + len(layer) > cap:
                raise ValueError("independent frontier state cap exceeded")
        hits = 0
        for cut, a, b, seen in layer:
            if cut == len(source) and (a, b) == (1, 2):
                terminal_checks += 1
                if read_bill(seen, desired) == minimum:
                    hits += 1
            if cost < optimum:
                mask = sum(1 << index[((v & 3) << n) | (v >> 2)] for v in seen)
                canonical.append((cost, cut, a & 3, b & 3, mask))
        if (cost < optimum and hits) or (cost == optimum and not hits):
            raise ValueError("claimed transfer optimum disagrees with complete independent frontier")
        layers.append(len(layer))
        earlier.update(layer)
        pending = set()
        for cut, a, b, seen in layer:
            pending.add((cut, a ^ b, b, seen | {a ^ b}))
            pending.add((cut, a, a ^ b, seen))
    digest = sha256(json.dumps(sorted(canonical), separators=(",", ":")).encode()).hexdigest()
    return {"lower_frontier_counts": layers[:-1], "lower_frontier_sha256": digest,
            "optimum_layer_states": layers[-1], "terminal_checks": terminal_checks,
            "minimum_reads": dict(zip(map(str, targets), minimum))}


def dense(program, n, targets, matrices):
    """All dirty basis columns, with separately supplied 2x2 binary linear maps."""
    labels = ["x"+str(j) for j in range(n)] + ["z0", "z1"] + ["y"+str(t) for t in targets]
    rows = {s: [1 << (2*i), 1 << (2*i+1)] for i, s in enumerate(labels)}
    initial = {s: v[:] for s, v in rows.items()}

    def apply(matrix, values):
        return [(values[0] if r & 1 else 0) ^ (values[1] if r & 2 else 0) for r in matrix]

    want = {s: v[:] for s, v in rows.items()}
    for t in targets:
        source = [0, 0]
        for j in range(n):
            if t >> j & 1:
                val = apply(matrices["B"][j], initial["x"+str(j)])
                source = [a ^ b for a, b in zip(source, val)]
        val = apply(matrices["A"][t], source)
        want["y"+str(t)] = [a ^ b for a, b in zip(want["y"+str(t)], val)]

    def run(word):
        for op in word:
            if op[0] == "C":
                dst, src = "z"+str(op[1]), "z"+str(1-op[1])
                val = rows[src]
            elif op[0] == "B":
                dst = "z"+str(op[2])
                val = apply(matrices["B"][op[1]], rows["x"+str(op[1])])
            else:
                dst = "y"+str(op[1])
                val = apply(matrices["A"][op[1]], rows["z"+str(op[2])])
            rows[dst] = [a ^ b for a, b in zip(rows[dst], val)]

    run(program)
    if rows != want:
        raise ValueError("dirty dense endpoint mismatch")
    run(reversed(program))
    if rows != initial:
        raise ValueError("dirty dense inverse mismatch")
    return 2*len(labels)
