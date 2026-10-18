#!/usr/bin/env python3
"""Exact price DP and dirty-column replay. Ross Richardson / Codex, Apache-2.0."""
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out
    def invalid(value):
        raise ValueError("non-finite JSON: " + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs,
                      parse_constant=invalid)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def check_sources(root=ROOT):
    rows = load_json(HERE / "SOURCES.json")["files"]
    inputs = [row for row in rows if row["usage"] == "input"]
    require(len(inputs) == 3, "source inventory changed")
    for row in inputs:
        path = root / row["path"]
        require(path.is_file(), "missing source: " + row["path"])
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "source drift")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source blob drift")


def prices(values, size):
    require(len(values) == size, "price vector length")
    for x in values:
        require(type(x) is int or type(x) is Fraction, "exact rational prices only")
        require(x > 0, "positive prices required")
    return tuple(Fraction(x) for x in values)


def optimum(b, d, a):
    """Exact query price and lexicographically first optimal p_1..p_k."""
    k = len(b)
    require(k >= 1, "at least one request")
    b, d, a = prices(b, k), prices(d, k - 1), prices(a, k)
    frontier = {0: (Fraction(0), ())}
    for i in range(k):
        following = {}
        for end in ((0,) if i == k - 1 else (0, 1)):
            choices = []
            for start, (cost, history) in frontier.items():
                bill = b[i] * (2 - (start ^ end))
                if i < k - 1:
                    bill += d[i] * end
                choices.append((cost + bill, history + (end,)))
            following[end] = min(choices)
        frontier = following
    value, path = frontier[0]
    return value + 2 * sum(a), path


def uniform_matching(b, d, a):
    """Uniform source tariff: maximum-weight matching on adjacent requests."""
    k = len(a)
    prices([b], 1)
    d, a = prices(d, k - 1), prices(a, k)
    before, best = Fraction(0), Fraction(0)
    for charge in d:
        before, best = best, max(best, before + 2 * b - charge)
    return 2 * sum(a) + 2 * k * b - best


def construct(path):
    """A/B queries, delivery Y, mandatory source mutation M, optional adapter D."""
    require(path and path[-1] == 0, "terminal connector must close")
    require(all(type(x) is int and x in (0, 1) for x in path), "invalid boundary type")
    word, start = [], 0
    for i, end in enumerate(path):
        word.extend([["A", i], ["B", i], ["A", i]])
        if start == end:
            word.append(["B", i])
        word.append(["Y", i])
        if i < len(path) - 1:
            word.append(["M", i])
            if end:
                word.append(["D", i])
        start = end
    return word


def replay(word, k):
    """Identity-map specialization on all independent source/dirt columns.

    The written linear-map proof establishes the arbitrary-map construction.
    Epoch transitions admit no writes to a future or delivered output.
    """
    x, z = 1, 1 << k
    originals = [1 << (k + 1 + i) for i in range(k)]
    outputs, delivered, epoch = originals[:], 0, 0
    stage, mutations = "request", 0
    for item in word:
        require(isinstance(item, (list, tuple)) and len(item) == 2, "query shape")
        op, i = item
        require(type(i) is int and 0 <= i < k, "query index")
        if stage == "mutated" and op in ("A", "B"):
            require(i == epoch + 1, "next source epoch")
            epoch += 1
            stage = "request"
        if op == "A":
            require(stage == "request" and i == epoch == delivered,
                    "output write outside request")
            outputs[i] ^= z
        elif op == "B":
            require(stage == "request" and i == epoch, "B outside source epoch")
            z ^= x
        elif op == "Y":
            require(stage == "request" and i == epoch == delivered, "delivery order")
            require(outputs[i] == originals[i] ^ ((1 << (i + 1)) - 1),
                    "incorrect delivered output")
            delivered += 1
            stage = "delivered"
        elif op == "M":
            require(stage == "delivered" and i == epoch < k - 1, "mutation outside cut")
            x ^= 1 << (i + 1)
            mutations += 1
            stage = "mutated"
        elif op == "D":
            require(stage == "mutated" and i == epoch < k - 1, "adapter outside cut")
            z ^= 1 << (i + 1)
        else:
            raise ValueError("unknown query")
    require(delivered == k and mutations == k - 1, "incomplete chain")
    require(z == 1 << k and x == (1 << k) - 1, "source/connector endpoint")
    return 2 * k + 1


def invoice(word, b, d, a, mutation):
    tables = {"B": b, "D": d, "A": a, "M": mutation}
    return sum(tables[op][i] for op, i in word if op in tables)


def matrix_gates(matrix, sources, targets):
    require(len(matrix) == len(targets), "matrix rows")
    require(set(sources).isdisjoint(targets), "matrix alias")
    gates = []
    for row, dst in zip(matrix, targets):
        require(type(row) is int and 0 <= row < (1 << len(sources)), "matrix entry")
        gates.extend([src, dst] for j, src in enumerate(sources) if row >> j & 1)
    return gates


def pilot(path):
    """PR1439's B=(3,6,7), C=(1,0,0), with independent one-bit updates."""
    k = len(path)
    x, u = [0, 1, 2], list(range(3, 3 + k - 1))
    z = list(range(k + 2, k + 5))
    ys = [list(range(k + 5 + 3 * i, k + 8 + 3 * i)) for i in range(k)]
    matrices = [(2, 4, 1) if i % 2 == 0 else (3, 2, 4) for i in range(k)]
    word, gates, cuts = construct(path), [], []
    for op, i in word:
        if op == "B":
            gates.extend(matrix_gates((3, 6, 7), x, z))
        elif op == "A":
            gates.extend(matrix_gates(matrices[i], z, ys[i]))
        elif op == "M":
            gates.append([u[i], x[0]])
        elif op == "D":
            gates.extend([[u[i], z[0]], [u[i], z[2]]])
        elif op == "Y":
            cuts.append([i, len(gates)])
    return {"k": k, "bits": 4 * k + 5, "x": x, "u": u, "z": z, "y": ys,
            "A": matrices, "B": [3, 6, 7], "C": [1, 0, 0],
            "word": word, "gates": gates, "deliveries": cuts}


def check_pilot(p):
    rows = [1 << i for i in range(p["bits"])]
    original = rows[:]
    snapshots = {cut: i for i, cut in p["deliveries"]}
    expected_source = [original[i] for i in p["x"]]
    expected = []
    for i in range(p["k"]):
        bx = [0, 0, 0]
        for j, mask in enumerate(p["B"]):
            for t in range(3):
                if mask >> t & 1:
                    bx[j] ^= expected_source[t]
        values = []
        for j, mask in enumerate(p["A"][i]):
            value = original[p["y"][i][j]]
            for t in range(3):
                if mask >> t & 1:
                    value ^= bx[t]
            values.append(value)
        expected.append(values)
        if i < p["k"] - 1:
            expected_source[0] ^= original[p["u"][i]]
    delivered = 0
    for n, (src, dst) in enumerate(p["gates"], 1):
        require(type(src) is int and type(dst) is int and src != dst, "bad scalar XOR")
        require(0 <= src < p["bits"] and 0 <= dst < p["bits"], "scalar address")
        for j, out in enumerate(p["y"]):
            if dst in out:
                require(j == delivered, "scalar write outside request")
        rows[dst] ^= rows[src]
        if n in snapshots:
            i = snapshots[n]
            require(i == delivered, "scalar delivery sequence")
            require([rows[j] for j in p["y"][i]] == expected[i], "scalar delivery map")
            delivered += 1
    require(delivered == p["k"], "scalar missing delivery")
    require([rows[i] for i in p["x"]] == expected_source, "scalar source endpoint")
    require(all(rows[i] == original[i] for i in p["z"] + p["u"]), "scalar dirty restoration")
    require(all([rows[j] for j in p["y"][i]] == expected[i] for i in range(p["k"])),
            "scalar output endpoint")
    return rows


def price_cases():
    for k in range(1, 5):
        a = tuple(1 + (i % 2) for i in range(k))
        for b in itertools.product((1, 3), repeat=k):
            for d in itertools.product((1, 2, 5), repeat=k - 1):
                yield b, d, a


def run():
    check_sources()
    records = []
    for b, d, a in price_cases():
        value, path = optimum(b, d, a)
        word = construct(path)
        replay(word, len(b))
        require(invoice(word, b, d, a, [0] * (len(b) - 1)) == value, "attaining invoice")
        records.append([list(b), list(d), list(a), str(value)])
    matching_cases = 0
    for k in range(1, 9):
        for d in itertools.product((1, 6, 9), repeat=k - 1):
            a = [1] * k
            require(optimum([3] * k, d, a)[0] == uniform_matching(3, d, a),
                    "uniform weighted matching")
            matching_cases += 1
    examples = []
    for k in range(1, 9):
        a = [3 + (i % 2) for i in range(k)]
        value, path = optimum([7] * k, [2] * (k - 1), a)
        require(value == 2 * sum(a) + 14 * k - 12 * (k // 2), "uniform corollary")
        candidate, baseline = pilot(path), pilot((0,) * k)
        require(check_pilot(candidate) == check_pilot(baseline), "pilot endpoints differ")
        require(len(candidate["gates"]) == value + k - 1, "pilot full price")
        examples.append({"k": k, "baseline_xors": len(baseline["gates"]),
                         "candidate_xors": len(candidate["gates"]), "path": path,
                         "bits": candidate["bits"],
                         "baseline_head_steps": sum(2 * max(s, t) for s, t in baseline["gates"]),
                         "candidate_head_steps": sum(2 * max(s, t) for s, t in candidate["gates"])})
    b, d, a = (10, 1, 10), (2, 2), (1, 1, 1)
    value, path = optimum(b, d, a)
    require((value, path) == (32, (1, 1, 0)), "nonadjacent open run")
    rational, _ = optimum([Fraction(x, 3) for x in b],
                          [Fraction(x, 3) for x in d], [Fraction(x, 3) for x in a])
    require(rational == Fraction(32, 3), "exact rational tariff")
    _, pilot_path = optimum([7] * 3, [2] * 2, [3, 4, 3])
    p = pilot(pilot_path)
    controls, word = [], p["word"]
    bad = {
        "omit-required-adapter": [x for x in word if x[0] != "D"],
        "write-future-output": [["A", 1]] + word,
        "write-delivered-output": word + [["A", 0]],
        "omit-source-update": [x for x in word if x != ["M", 0]],
        "late-adapter": [x for x in word if x[0] != "D"] + [["D", 0]],
        "omit-last-B": word[:],
    }
    del bad["omit-last-B"][max(i for i, item in enumerate(word) if item[0] == "B")]
    for name, mutation in bad.items():
        try:
            replay(mutation, 3)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("negative control accepted: " + name)
    return {"status": "PASS_MUTABLE_CONNECTOR_DELIVERY_OPTIMUM", "no_new_kappa": True,
            "tariff_cases": len(records),
            "tariff_digest": hashlib.sha256(canonical(records).encode()).hexdigest(),
            "uniform_matching_cases": matching_cases,
            "pilots": examples, "three_output_pilot": p,
            "heterogeneous_price_example": {"B": b, "D": d, "A": a,
                "query_cost": int(value), "closed_query_cost": 48, "path": path},
            "controls": controls}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.write_receipt:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(canonical(load_json(HERE / "RESULT.json")) == canonical(result), "receipt drift")
    print(result["status"], "tariffs=" + str(result["tariff_cases"]),
          "pilot=64->52", "controls=" + str(len(result["controls"])), "no_new_kappa")


if __name__ == "__main__":
    main()
