"""Independent checker: no generator or predecessor imports; Python 3.10+."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
NAMES = ("B0", "B1", "B2", "A0", "A1", "A2")
RETAINED = {
    "sources/PR944-README.md": "76e20674799a7b35dfb5908e7df5cab53f17482da2bfd25db576ba0000dade83",
    "sources/PR944-NOTICE.md": "0a99079d85344f195f58472e0aca5002888c636309fb80f20d1df04c700facc3",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def identity(n):
    return [{(r, ()): 1} for r in range(n)]


def execute(leaves, initial=None, rows=10):
    state = identity(rows) if initial is None else [dict(r) for r in initial]
    for factor, source, target, sign in leaves:
        need(isinstance(factor, str) and type(source) is int and type(target) is int
             and 0 <= source < rows and 0 <= target < rows and source != target
             and type(sign) is int and sign in (-1, 1), "invalid leaf/alias/sign")
        for (origin, applied), value in list(state[source].items()):
            key = (origin, applied + (factor,))
            new = state[target].get(key, 0) + sign * value
            if new:
                state[target][key] = new
            else:
                state[target].pop(key, None)
    return state


def inverse(word):
    return [[f, s, t, -sign] for f, s, t, sign in reversed(word)]


def desired(matrix, factors):
    wanted = identity(10)
    for i in range(3):
        for j in range(3):
            if matrix[i][j]:
                wanted[i + 3][(j, tuple(factors[f"B{j}"] + factors[f"A{i}"]))] = matrix[i][j]
    return wanted


def query_coefficients(word):
    # A separate prefix-tally evaluator, without the noncommutative interpreter.
    q = [0, 0, 0]
    dirt = [0, 0, 0]
    result = [[0] * 3 for _ in range(3)]
    counts = Counter()
    for kind, j, sign in word:
        need(kind in ("A", "B") and type(j) is int and 0 <= j < 3
             and type(sign) is int and sign in (-1, 1), "invalid query")
        counts[f"{kind}{j}"] += 1
        if kind == "B":
            q[j] += sign
        else:
            dirt[j] += sign
            for k in range(3):
                result[j][k] += sign * q[k]
    need(q == [0] * 3 and dirt == [0] * 3, "unrestored connector/dirt")
    return tuple(map(tuple, result)), counts


def lower(word, factors):
    # Iterative task stack, separate from the generator's recursive word builder.
    leaves = []
    for kind, j, sign in word:
        s, t = (j, 6) if kind == "B" else (6, j + 3)
        tasks = [(tuple(factors[f"{kind}{j}"]), s, t, 0, sign)]
        while tasks:
            fs, source, target, depth, direction = tasks.pop()
            if len(fs) == 1:
                leaves.append([fs[0], source, target, direction])
                continue
            cut = len(fs) // 2
            connector = 7 + depth
            need(connector < 10, "scratch capacity")
            r = (fs[:cut], source, connector, depth + 1, 1)
            l = (fs[cut:], connector, target, depth + 1, 1)
            sequence = [r, l, (*r[:-1], -1), (*l[:-1], -1)]
            if direction == -1:
                sequence = [(*task[:-1], -task[-1]) for task in reversed(sequence)]
            tasks.extend(reversed(sequence))
    return leaves


def census(counts, rows):
    # Signed-move DFS, not the generator's permutation/sign-product enumeration.
    left = [[n // 2, n // 2] for n in counts]
    vertices = [(0, 0, 0)]
    total = feasible = 0

    def walk():
        nonlocal total, feasible
        if len(vertices) == sum(counts) + 1:
            total += 1
            points = set(vertices)
            if all(any(tuple(u[k] + row[k] for k in range(3)) in points for u in points) for row in rows):
                feasible += 1
            return
        for j in range(3):
            for sign_index, sign in enumerate((-1, 1)):
                if not left[j][sign_index]:
                    continue
                left[j][sign_index] -= 1
                q = list(vertices[-1])
                q[j] += sign
                vertices.append(tuple(q))
                walk()
                vertices.pop()
                left[j][sign_index] += 1
    walk()
    return {"paths": total, "feasible": feasible}


def orbit_checks(words):
    seen = set()
    replays = 0
    for rp, cp in itertools.product(itertools.permutations(range(3)), repeat=2):
        for rs, cs in itertools.product(itertools.product((-1, 1), repeat=3), repeat=2):
            matrix = tuple(tuple(rs[i] * cs[j] * M[rp[i]][cp[j]] for j in range(3)) for i in range(3))
            if matrix in seen:
                continue
            seen.add(matrix)
            for repeated, word in words.items():
                changed = []
                for kind, j, sign in word:
                    permutation, signs = (rp, rs) if kind == "A" else (cp, cs)
                    new_j = permutation.index(j)
                    changed.append([kind, new_j, sign * signs[new_j]])
                actual, counts = query_coefficients(changed)
                need(actual == matrix, "orbit transformation")
                kind, j = repeated[0], int(repeated[1])
                mapped = (rp if kind == "A" else cp).index(j)
                need(counts == Counter({name: 4 if name == f"{kind}{mapped}" else 2 for name in NAMES}), "orbit count")
                replays += 1
    need(len(seen) == 288, "orbit cardinality")
    return len(seen), replays


def select_word(data, prices):
    need(len(prices) == 6, "six complete query prices required")
    costs = [Fraction(p) for p in prices]
    need(all(c > 0 for c in costs), "prices must be strictly positive")
    chosen = min(range(6), key=lambda i: (costs[i], i))
    matrix, counts = query_coefficients(data["witnesses"][NAMES[chosen]])
    need(matrix == M, "selected word identity")
    actual = sum(counts[name] * c for name, c in zip(NAMES, costs))
    optimum = 2 * sum(costs) + 2 * min(costs)
    need(actual == optimum, "selected price differs from exact optimum")
    return {"repeated": NAMES[chosen], "minimum": str(optimum),
            "word": data["witnesses"][NAMES[chosen]]}


def dense_and_invoice(leaves, factors):
    flat = [f for name in NAMES for f in factors[name]]
    checks = 0
    invoices = []
    for length in (1, 2, 3):
        # Exact integer, generally noncommuting dense leaf operators.
        matrices = {f: [[((a + 1) * (b + 3) + 2 * idx + idx * a) % 5 - 2
                         for b in range(length)] for a in range(length)] for idx, f in enumerate(flat)}

        def apply(matrix, vector):
            return [sum(a * b for a, b in zip(row, vector)) for row in matrix]

        cases = []
        for row in range(10):
            for coordinate in range(length):
                state = [[0] * length for _ in range(10)]
                state[row][coordinate] = 1
                cases.append(state)
        cases += [[[((r * 7 + j * 3 + 58) % 11) - 5 for j in range(length)] for r in range(10)]]
        for initial in cases:
            state = [row[:] for row in initial]
            for f, source, target, sign in leaves:
                delta = apply(matrices[f], state[source])
                state[target] = [x + sign * y for x, y in zip(state[target], delta)]
            wanted = [row[:] for row in initial]
            for i in range(3):
                for j in range(3):
                    value = initial[j][:]
                    for f in factors[f"B{j}"] + factors[f"A{i}"]:
                        value = apply(matrices[f], value)
                    wanted[i + 3] = [x + M[i][j] * y for x, y in zip(wanted[i + 3], value)]
            need(state == wanted, "dense noncommuting identity")
            checks += 1
        # Literal word-cell movement on one tape. Coefficients follow ten data
        # rows; each completed primitive starts and ends with head at cell zero.
        travel = 0
        for f, source, target, sign in leaves:
            position = 0
            idx = flat.index(f)
            for i in range(length):
                for j in range(length):
                    for dest in (10 * length + idx * length ** 2 + i * length + j, source * length + j):
                        travel += abs(dest - position)
                        position = dest
                dest = target * length + i
                travel += abs(dest - position)
                position = dest
            travel += position
        n = len(leaves)
        # Independent closed form for the same literal access order.
        formula = 0
        for f, source, target, sign in leaves:
            idx = flat.index(f)
            for i in range(length):
                previous = 0 if i == 0 else target * length + i - 1
                for j in range(length):
                    coefficient = 10 * length + idx * length ** 2 + i * length + j
                    input_cell = source * length + j
                    formula += coefficient - previous + coefficient - input_cell
                    previous = input_cell
                formula += abs(target * length + i - previous)
            formula += target * length + length - 1
        need(travel == formula, "tape trace/formula mismatch")
        invoices.append({"L": length, "leaves": n, "coefficient_reads": n * length ** 2,
                         "source_reads": n * length ** 2, "target_read_write_pairs": n * length,
                         "multiplications": n * length ** 2, "add_subtracts": n * (length ** 2 + length),
                         "scalar_zero_assignments": n * (3 * length ** 2 + 3 * length),
                         "startup_scalar_zero_assignments": 4,
                         "word_cell_head_moves": travel, "mutable_data_words": 10 * length,
                         "readonly_coefficient_words": len(flat) * length ** 2,
                         "clean_scalar_work_registers": 4,
                         "program_bits": 14 * n, "program_bit_reads": 14 * n,
                         "program_bit_head_moves_including_return": 28 * n})
    return checks, invoices


def verify(data, exhaustive=True):
    need(data["format"] == "weighted-signed-connector-v1" and data["seed"] == 58
         and data["base"] == "abdc6a7002abdbcd9e21bfc5e1a795784deacfdf", "metadata")
    need(tuple(map(tuple, data["matrix"])) == M, "matrix")
    need(data["lengths_B_then_A"] == [4, 5, 6, 7, 2, 3] and data["chosen"] == "A1", "fixture")
    factors = data["factors"]
    need(factors == {name: [f"{name}f{k}" for k in range(n)] for name, n in zip(NAMES, [4, 5, 6, 7, 2, 3])}, "factor admission")
    need(set(data["witnesses"]) == set(NAMES) and set(data["leaves"]) == set(NAMES), "witness inventory")
    leaf_counts = {}
    dense_checks = 0
    invoices = {}
    for repeated in NAMES:
        word = data["witnesses"][repeated]
        actual, counts = query_coefficients(word)
        need(len(word) == 14 and actual == M, "query identity")
        need(counts == Counter({name: 4 if name == repeated else 2 for name in NAMES}), "query multiplicities")
        leaves = data["leaves"][repeated]
        need(leaves == lower(word, factors), "literal recursive expansion")
        need(all(leaf[2] not in (0, 1, 2) for leaf in leaves), "immutable source prefix")
        state = execute(leaves)
        need(state == desired(M, factors), "full noncommuting dirty map")
        need(execute(inverse(leaves), state) == identity(10), "literal inverse")
        leaf_counts[repeated] = len(leaves)
        checks, bill = dense_and_invoice(leaves, factors)
        dense_checks += checks
        invoices[repeated] = bill
    need(leaf_counts == {"B0": 332, "B1": 356, "B2": 380, "A0": 404, "A1": 308, "A2": 320}, "leaf prices")
    orbit_size, orbit_replays = orbit_checks(data["witnesses"])
    price_fixtures = []
    for cheapest in range(6):
        costs = [Fraction(100 + i, 3) for i in range(6)]
        costs[cheapest] = Fraction(1, 7)
        result = select_word(data, costs)
        need(result["repeated"] == NAMES[cheapest], "weighted selector coverage")
        price_fixtures.append({"prices": list(map(str, costs)), "repeated": result["repeated"], "minimum": result["minimum"]})
    need(select_word(data, [1] * 6)["minimum"] == "14", "tie price")
    census_receipt = {}
    if exhaustive:
        support = census([2, 2, 2], M)
        need(support == {"paths": 720, "feasible": 0}, "12-query exclusion")
        census_receipt["support"] = support
        for side in ("B", "A"):
            rows = M if side == "B" else tuple(zip(*M))
            for j in range(3):
                counts = [2] * 3
                counts[j] = 4
                result = census(counts, rows)
                need(result == data["census"][f"{side}{j}"] == {"paths": 10080, "feasible": (544, 544, 512)[j]}, "complete repeated-path census")
                census_receipt[f"{side}{j}"] = result
    return {"status": "PASS_WEIGHTED_SIGNED_CONNECTOR", "seed": 58,
            "query_witnesses": 6, "orbit_matrices": orbit_size, "orbit_query_replays": orbit_replays,
            "census": census_receipt, "leaf_counts": leaf_counts, "dense_cases": dense_checks,
            "dirty_arrays": 4, "price_fixtures": price_fixtures,
            "invoices": invoices, "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--prices", nargs=6, metavar="C", help="positive rational costs in B0 B1 B2 A0 A1 A2 order")
    args = parser.parse_args()
    sources = json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8-sig"))
    need(sources["base"] == "abdc6a7002abdbcd9e21bfc5e1a795784deacfdf"
         and sources["retained"] == RETAINED, "source manifest pins/inventory")
    for relative, digest in sources["retained"].items():
        need(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == digest, "retained source binding")
    data = json.loads((ROOT / "CERTIFICATE.json").read_text(encoding="utf-8"))
    receipt = verify(data)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write_receipt:
        (ROOT / "EXPECTED.json").write_text(rendered, encoding="utf-8", newline="\n")
    else:
        need(json.loads((ROOT / "EXPECTED.json").read_text(encoding="utf-8")) == receipt, "receipt differs")
    print("PASS_WEIGHTED_SIGNED_CONNECTOR witnesses=6 orbit=288 paths=61200 leaves=308_vs_332 dense=378 no_new_kappa")
    if args.prices:
        print(json.dumps(select_word(data, args.prices), sort_keys=True))


if __name__ == "__main__":
    main()
