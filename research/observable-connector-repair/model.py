"""Exact observable-connector model. Hanson Sun, with OpenAI Codex. Apache-2.0."""
import hashlib
import json
import random


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dot(a, b):
    return (a & b).bit_count() % 2


def matvec(rows, x):
    return sum(dot(row, x) << i for i, row in enumerate(rows))


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            j = row.bit_length() - 1
            if j in pivots:
                row ^= pivots[j]
            else:
                pivots[j] = row
                break
    return len(pivots)


def selected():
    rng = random.Random(50)
    # The first full-rank draw is a fixture choice, not an optimization search.
    B = [3, 6, 12, 9]
    draws = 0
    while rank(B) != 4:
        B = [rng.randrange(1, 16) for _ in range(4)]
        draws += 1
        require(draws <= 100, "fixture draw cap exceeded")
    readers = rng.sample(range(1, 16), 8)
    order = list(range(4))
    rng.shuffle(order)
    return {"width": 4, "B": B, "readers": readers, "steps": order + order,
            "seed": 50, "matrix_draws": draws}


def demands(spec):
    d, B, readers, steps = (spec[k] for k in ("width", "B", "readers", "steps"))
    require(type(d) is int and 1 <= d <= 8, "width outside bounded implementation")
    require(len(B) == d and len(readers) == len(steps), "bad shape")
    require(all(type(a) is int and 0 <= a < 1 << d for a in B + readers), "bad binary mask")
    require(all(type(j) is int and 0 <= j < d for j in steps), "bad source step")
    q, out = 0, []
    for a, j in zip(readers, steps):
        q ^= 1 << j
        bq = matvec(B, q)
        out.append({"reader": a, "source_mask": q, "coherent_mask": bq,
                    "demand": dot(a, bq)})
    require(q == 0, "source tour must restore the source")
    return out


def solve(d, conditions, weights, output_prices=None):
    """Bellman recurrence over every connector correction mask; no pruning."""
    require(type(d) is int and 1 <= d <= 8, "bad width")
    require(len(weights) == d and all(type(w) is int and w > 0 for w in weights), "bad weights")
    require(all(type(a) is int and 0 <= a < 1 << d and type(b) is int and b in (0, 1)
                for a, b in conditions), "bad conditions")
    require(output_prices is None or (len(output_prices) == len(conditions)
            and all(type(w) is int and w > 0 for w in output_prices)), "bad output prices")
    size = 1 << d
    distances = [sum(w for j, w in enumerate(weights) if mask >> j & 1) for mask in range(size)]
    best = {0: (0, ())}
    tables = [[0] + [None] * (size - 1)]
    for i, (a, b) in enumerate(conditions):
        nxt = {}
        for k in range(size):
            defect = b ^ dot(a, k)
            if defect and output_prices is None:
                continue
            penalty = defect * output_prices[i] if output_prices is not None else 0
            if best:
                nxt[k] = min((cost + distances[h ^ k] + penalty, path + (k,))
                             for h, (cost, path) in best.items())
        best = nxt
        tables.append([best[k][0] if k in best else None for k in range(size)])
    require(bool(best), "infeasible observable demands")
    cost, path = min((cost + distances[k], path + (0,)) for k, (cost, path) in best.items())
    corrections = [b ^ dot(a, k) for (a, b), k in zip(conditions, path)]
    return {"cost": cost, "path": list(path), "output_corrections": corrections,
            "tables": tables, "weights": list(weights), "output_prices": output_prices}


def emit(spec, strategy, solution=None):
    """Emit every scalar XOR, including source and connector restoration."""
    d, readers = spec["width"], spec["readers"]
    ds = demands(spec)
    u, z0, y0 = d, d + 1, 2 * d + 1
    count = y0 + len(readers) + 1  # last row is an arbitrary dirty spectator
    gates, cuts = [], []

    def gate(target, source, kind):
        require(target != source, "aliasing XOR")
        gates.append([target, source, kind])

    def b_call():
        for j, row in enumerate(spec["B"]):
            for h in range(d):
                if row >> h & 1:
                    gate(z0 + j, h, "B")

    def read(i):
        for j in range(d):
            if readers[i] >> j & 1:
                gate(y0 + i, z0 + j, "reader")

    def repair(delta):
        for j in range(d):
            if delta >> j & 1:
                gate(z0 + j, u, "connector_repair")

    if strategy == "direct":
        # Deliberately outside the fixed-query alphabet: open/fuse A_i B.
        for i, j in enumerate(spec["steps"]):
            gate(j, u, "source")
            row = 0
            for h, brow in enumerate(spec["B"]):
                if readers[i] >> h & 1:
                    row ^= brow
            for h in range(d):
                if row >> h & 1:
                    gate(y0 + i, h, "direct_product")
            cuts.append(len(gates))
    elif strategy == "eager":
        for i, j in enumerate(spec["steps"]):
            gate(j, u, "source")
            read(i)
            b_call()
            read(i)
            b_call()
            cuts.append(len(gates))
    else:
        if strategy == "coherent":
            path = [x["coherent_mask"] for x in ds] + [0]
            outputs = [0] * len(readers)
        elif strategy == "output_only":
            path = [0] * (len(readers) + 1)
            outputs = [x["demand"] for x in ds]
        else:
            require(strategy == "planned" and solution is not None, "unknown strategy")
            path, outputs = solution["path"], solution["output_corrections"]
            require(len(path) == len(readers) + 1 and path[-1] == 0, "unrestored plan")
            require(len(outputs) == len(readers), "bad output correction shape")
            require(all(type(k) is int and 0 <= k < 1 << d for k in path), "bad plan mask")
            require(all(type(p) is int and p in (0, 1) for p in outputs), "bad output correction")
            require(all(dot(x["reader"], k) ^ p == x["demand"]
                        for x, k, p in zip(ds, path, outputs)), "unobservable plan")
        # Early prewrites are explicit; future output ports are reserved.
        for i in range(len(readers)):
            read(i)
        b_call()
        old = 0
        for i, j in enumerate(spec["steps"]):
            gate(j, u, "source")
            repair(old ^ path[i])
            old = path[i]
            read(i)
            if outputs[i]:
                gate(y0 + i, u, "output_repair")
            cuts.append(len(gates))
        repair(old)
        b_call()
    return {"registers": count, "gates": gates, "cuts": cuts}


def expected_rows(spec, cut=None):
    d, m = spec["width"], len(spec["readers"])
    rows = [1 << j for j in range(2 * d + m + 2)]
    upto = m if cut is None else cut + 1
    q = 0
    for i, step in enumerate(spec["steps"][:upto]):
        q ^= 1 << step
        a = spec["readers"][i]
        linear = 0
        for j, brow in enumerate(spec["B"]):
            if a >> j & 1:
                linear ^= brow
        rows[2 * d + 1 + i] ^= linear
        rows[2 * d + 1 + i] ^= dot(linear, q) << d
    for j in range(d):
        rows[j] ^= ((q >> j) & 1) << d
    return rows


def check_word(spec, word):
    rows = [1 << j for j in range(word["registers"])]
    by_cut = {n: i for i, n in enumerate(word["cuts"])}
    checked = 0
    for pos, (t, s, _) in enumerate(word["gates"], 1):
        rows[t] ^= rows[s]
        if pos in by_cut:
            i = by_cut[pos]
            expected = expected_rows(spec, i)
            d = spec["width"]
            visible = list(range(d + 1)) + list(range(2 * d + 1, 2 * d + 2 + i)) + [len(rows) - 1]
            require(all(rows[j] == expected[j] for j in visible), "incorrect observable cut")
            checked += 1
    require(rows == expected_rows(spec), "incorrect final dirty-state map")
    return {"basis_columns": len(rows), "observation_cuts": checked, "final_rows": rows}


def invoice(word):
    histogram = {}
    for _, _, kind in word["gates"]:
        histogram[kind] = histogram.get(kind, 0) + 1
    g = len(word["gates"])
    maximum_sum = sum(max(t, s) for t, s, _ in word["gates"])
    # Row-major L-bit blocks, 1-based cells, return to origin after every XOR.
    quadratic = 2 * maximum_sum + g
    return {"scalar_xors": g, "by_kind": histogram,
            "head_steps_L1": 2 * (maximum_sum + g),
            "head_steps_polynomial": {"L2": quadratic, "L": g},
            "data_reads_per_L": 2 * g, "data_writes_per_L": g,
            "xor_instructions_per_L": g, "dispatches_per_L": g,
            "online_tariff_polynomial": {"L2": quadratic, "L": 6 * g},
            "data_cells_per_L": word["registers"],
            "instruction_records_per_L": g,
            "word_sha256": hashlib.sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
