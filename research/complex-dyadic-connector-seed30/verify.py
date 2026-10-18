#!/usr/bin/env python3
"""Exact paid dyadic connector extension. No predecessor implementation imports.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
The all-length reductions are in README.md; this is a finite certificate replay.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
from itertools import permutations, product
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
BASE = "ef5f39403610d231a0c27e8a6b4f08c10209bcd6"
SEED = 30
MATRIX = ((1, 1, 1), (1, 1, -1), (1, -1, 0))
OPERATORS = ("B0", "B1", "B2", "A0", "A1", "A2")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def read_sources():
    pins = json.loads((PACKAGE / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "wrong source base")
    for item in pins["files"]:
        if item["usage"] == "input":
            data = (ROOT / item["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == item["sha256"],
                    "source drift: " + item["path"])
    return json.loads((ROOT / "research/weighted-signed-connector-seed58/CERTIFICATE.json").read_text())


def inverse(word):
    result = []
    for event in reversed(word):
        if event[0] == "S":
            result.append(["S", event[1], str(1 / Q(event[2]))])
        else:
            result.append([*event[:-1], -event[-1]])
    return result


def scaled_repair(word):
    pairs = [i for i in range(len(word) - 1) if word[i] == word[i + 1]]
    require(len(pairs) == 1, "expected one adjacent identical pair")
    i = pairs[0]
    before, after = ("1/2", "2") if word[i][0] == "B" else ("2", "1/2")
    return word[:i] + [["S", 6, before], word[i], ["S", 6, after]] + word[i + 2:]


def query_map(word):
    """Free coefficients on z0, B0*x0, B1*x1, B2*x2, then on each Ai of these."""
    z = [Q(1), Q(0), Q(0), Q(0)]
    out = [[Q(0)] * 4 for _ in range(3)]
    for kind, index, value in word:
        if kind == "S":
            require(index == 6 and Q(value) in (Q(2), Q(1, 2)), "invalid root dilation")
            z = [Q(value) * entry for entry in z]
        else:
            require(kind in ("A", "B") and index in range(3) and value in (-1, 1),
                    "invalid query")
            if kind == "B":
                z[index + 1] += value
            else:
                out[index] = [a + value * b for a, b in zip(out[index], z)]
    return z, out


def is_query_map(word, matrix, sign=1):
    z, rows = query_map(word)
    return z == [1, 0, 0, 0] and rows == [[0] + [sign * x for x in row] for row in matrix]


def path_census():
    """Enumerate six distinct signed moves, independently of PR944."""
    moves = tuple((j, s) for j in range(3) for s in (-1, 1))
    wanted = set(MATRIX)
    records = []
    hits = Counter()
    for path in permutations(moves):
        q = [0, 0, 0]
        points = [tuple(q)]
        for j, s in path:
            q[j] += s
            points.append(tuple(q))
        require(q == [0, 0, 0], "source path did not close")
        differences = {tuple(b[k] - a[k] for k in range(3)) for a in points for b in points}
        covered = sorted(wanted & differences)
        hits[len(covered)] += 1
        records.append([path, covered])
    require(len(records) == 720 and hits[3] == 0, "twelve-query obstruction failed")
    return {"paths": len(records), "full_hits": hits[3],
            "row_coverage_histogram": {str(k): v for k, v in sorted(hits.items())},
            "ordered_records_sha256": digest(records)}


def transformed(matrix, word, rp, cp, rs, cs):
    # Permutations map old indices to new indices; signs attach to old indices.
    target = [[0] * 3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            target[rp[i]][cp[j]] = rs[i] * cs[j] * matrix[i][j]
    answer = []
    for kind, index, value in word:
        if kind == "S":
            answer.append([kind, index, value])
        elif kind == "B":
            answer.append([kind, cp[index], value * cs[index]])
        else:
            answer.append([kind, rp[index], value * rs[index]])
    return tuple(tuple(r) for r in target), answer


def orbit_replay(words):
    representatives = {}
    for rp, cp in product(permutations(range(3)), repeat=2):
        for rs, cs in product(product((-1, 1), repeat=3), repeat=2):
            target, _ = transformed(MATRIX, [], rp, cp, rs, cs)
            representatives.setdefault(target, (rp, cp, rs, cs))
    require(len(representatives) == 288, "wrong signed/permuted orbit")
    count = 0
    for target, transform in sorted(representatives.items()):
        for word in words.values():
            actual_target, candidate = transformed(MATRIX, word, *transform)
            require(actual_target == target, "orbit relabelling failed")
            require(is_query_map(candidate, target), "forward orbit map failed")
            require(is_query_map(inverse(candidate), target, -1), "inverse orbit map failed")
            count += 2
    return {"matrices": len(representatives), "forward_and_inverse_maps": count,
            "matrices_sha256": digest(sorted(representatives))}


def factors():
    # Seed 30 mod 6 puts the cheapest, two-factor child at B0.
    offset = SEED % 6
    lengths = [2 + (i - offset) % 6 for i in range(6)]
    return {name: [name + "f" + str(i) for i in range(n)] for name, n in zip(OPERATORS, lengths)}


def expand_product(fs, src, dst, scratch=7):
    if len(fs) == 1:
        return [["F", fs[0], src, dst, 1]]
    n = len(fs) // 2
    right = expand_product(fs[:n], src, scratch, scratch + 1)
    left = expand_product(fs[n:], scratch, dst, scratch + 1)
    return right + left + inverse(right) + inverse(left)


def expand(word, fs):
    result = []
    for kind, index, value in word:
        if kind == "S":
            result.append([kind, index, value])
            continue
        src, dst = (index, 6) if kind == "B" else (6, 3 + index)
        child = expand_product(fs[kind + str(index)], src, dst)
        result.extend(child if value == 1 else inverse(child))
    return result


def combine(target, source, coefficient, operator=None):
    answer = target.copy()
    for (ops, initial), value in source.items():
        key = (ops if operator is None else (operator,) + ops, initial)
        answer[key] = answer.get(key, 0) + coefficient * value
        if answer[key] == 0:
            del answer[key]
    return answer


def initial_state():
    return [{((), i): Q(1)} for i in range(10)]


def free_map(word):
    """Literal noncommutative factor replay, with ten independent dirty arrays."""
    state = initial_state()
    for event in word:
        if event[0] == "S":
            _, row, value = event
            state[row] = {key: Q(value) * v for key, v in state[row].items()}
        else:
            _, factor, src, dst, sign = event
            require(src != dst and 0 <= src < 10 and 0 <= dst < 10, "invalid leaf ports")
            state[dst] = combine(state[dst], state[src], sign, factor)
    return state


def expected_free(fs, sign=1):
    answer = initial_state()
    for i in range(3):
        for j in range(3):
            value = sign * MATRIX[i][j]
            if value:
                monomial = tuple(reversed(fs["A" + str(i)])) + tuple(reversed(fs["B" + str(j)]))
                answer[3 + i][(monomial, j)] = Q(value)
    return answer


def apply_matrix(matrix, vector):
    return [sum(Q(c) * x for c, x in zip(row, vector)) for row in matrix]


def dense_replay(words, fs):
    """Independent numeric basis interpreter, using noncommuting 2-by-2 factors."""
    matrices = {}
    for k, f in enumerate(f for group in fs.values() for f in group):
        # Include singular factors; additive queries need no invertibility of F.
        matrices[f] = [[1 + k % 2, (k % 3) - 1], [1, (k % 4) - 1]]
    checks = 0
    for word in words.values():
        for sign, literal in ((1, word), (-1, inverse(word))):
            for column in range(20):
                start = [[Q(0), Q(0)] for _ in range(10)]
                start[column // 2][column % 2] = Q(1)
                expected = [row.copy() for row in start]
                for i in range(3):
                    for j in range(3):
                        v = start[j].copy()
                        for f in fs["B" + str(j)] + fs["A" + str(i)]:
                            v = apply_matrix(matrices[f], v)
                        expected[3 + i] = [a + sign * MATRIX[i][j] * b
                                           for a, b in zip(expected[3 + i], v)]
                actual = [row.copy() for row in start]
                for event in literal:
                    if event[0] == "S":
                        _, row, coefficient = event
                        actual[row] = [Q(coefficient) * x for x in actual[row]]
                    else:
                        _, factor, src, dst, coefficient = event
                        v = apply_matrix(matrices[factor], actual[src])
                        actual[dst] = [a + coefficient * b for a, b in zip(actual[dst], v)]
                require(actual == expected, "dense dirty-basis replay failed")
                checks += 1
    return checks


def price_optimum(prices, up, down):
    values = [Q(v) for v in prices]
    up, down = Q(up), Q(down)
    require(len(values) == 6 and all(x > 0 for x in values) and up > 0 and down > 0,
            "all eight fixed complete prices must be positive")
    m = min(values)
    return 2 * sum(values) + min(2 * m, m + up + down)


def literal_price(word, prices, up, down):
    tariff = dict(zip(OPERATORS, map(Q, prices)))
    result = Q(0)
    for kind, index, value in word:
        result += (Q(up) if Q(value) == 2 else Q(down)) if kind == "S" else tariff[kind + str(index)]
    return result


def dense_invoice(word, fs, length):
    """Literal dense data-tape trace. Every leaf/scaling starts and returns at 0.

    Ten length-L mutable rows precede 27 dense coefficient matrices. A dot
    product reads each coefficient and source entry, then updates its target.
    Loop/dispatch/instruction work is itemized, not called free.
    """
    names = [f for group in fs.values() for f in group]
    counts = Counter({name: 0 for name in (
        "coefficient_reads", "source_reads", "target_reads", "target_writes",
        "general_multiplications", "dyadic_scalings", "additions", "negations",
        "accumulator_resets", "head_moves", "instructions", "dot_terms",
        "row_iterations", "leaf_calls", "scale_passes")})
    for event in word:
        counts["instructions"] += 1
        head = 0
        if event[0] == "S":
            _, row, _ = event
            counts["scale_passes"] += 1
            for i in range(length):
                address = row * length + i
                counts["head_moves"] += abs(address - head)
                head = address
                counts["target_reads"] += 1
                counts["target_writes"] += 1
                counts["dyadic_scalings"] += 1
                counts["row_iterations"] += 1
        else:
            _, factor, src, dst, sign = event
            counts["leaf_calls"] += 1
            start = 10 * length + names.index(factor) * length * length
            for i in range(length):
                counts["row_iterations"] += 1
                counts["accumulator_resets"] += 1
                for j in range(length):
                    coefficient = start + i * length + j
                    source = src * length + j
                    counts["head_moves"] += abs(coefficient - head) + abs(source - coefficient)
                    head = source
                    counts["coefficient_reads"] += 1
                    counts["source_reads"] += 1
                    counts["general_multiplications"] += 1
                    counts["additions"] += 1
                    counts["dot_terms"] += 1
                target = dst * length + i
                counts["head_moves"] += abs(target - head)
                head = target
                counts["target_reads"] += 1
                counts["target_writes"] += 1
                counts["additions"] += 1
                counts["negations"] += int(sign < 0)
        counts["head_moves"] += head
    return dict(counts)


def dense_invoices(old_word, new_word, fs):
    result = []
    for length in range(1, 6):
        old = dense_invoice(old_word, fs, length)
        new = dense_invoice(new_word, fs, length)
        # Independently price the one removed complete B0 child and two root sweeps.
        removed = dense_invoice(expand_product(fs["B0"], 0, 6), fs, length)
        added = dense_invoice([["S", 6, "1/2"], ["S", 6, "2"]], fs, length)
        require(all(new[k] == old[k] - removed[k] + added[k] for k in old),
                "complete dense invoice delta failed")
        require(added["head_moves"] == 28 * length - 4, "root sweep formula failed")
        require(new["general_multiplications"] + new["dyadic_scalings"] < old["general_multiplications"],
                "charged dense arithmetic does not improve")
        require(new["head_moves"] < old["head_moves"], "charged dense travel does not improve")
        result.append({"length": length, "old": old, "new": new,
                       "common_mutable_words": 10 * length,
                       "common_coefficient_words": 27 * length * length,
                       "common_admission_word_reads": 10 * length + 27 * length * length})
    return result


def controls(words, leaves, fs):
    counts = Counter()
    for word in words.values():
        for i in range(len(word)):
            require(not is_query_map(word[:i] + word[i + 1:], MATRIX), "deleted event escaped")
            counts["delete_query_or_scaling"] += 1
            if word[i][0] != "S":
                mutant = [e.copy() for e in word]
                mutant[i][2] *= -1
                require(not is_query_map(mutant, MATRIX), "query sign mutation escaped")
                counts["query_sign"] += 1
        mutant = [[k, i, str(1 / Q(v))] if k == "S" else [k, i, v] for k, i, v in word]
        require(not is_query_map(mutant, MATRIX), "opposite conjugation escaped")
        counts["reverse_scaling_order"] += 1
    for word in leaves.values():
        first = next(i for i, e in enumerate(word) if e[0] == "F")
        require(free_map(word[:first] + word[first + 1:]) != expected_free(fs),
                "missing primitive escaped")
        counts["missing_recursive_leaf"] += 1
        mutant = [e.copy() for e in word]
        mutant[first][1] = "WRONG_NONCOMMUTATIVE_FACTOR"
        require(free_map(mutant) != expected_free(fs), "wrong factor escaped")
        counts["wrong_recursive_factor"] += 1
    for prices, up, down in (([0] * 6, 1, 1), ([1] * 6, 0, 1),
                            ([1] * 6, 1, -1), ([1] * 5, 1, 1)):
        try:
            price_optimum(prices, up, down)
        except ValueError:
            counts["invalid_complete_prices"] += 1
        else:
            raise ValueError("invalid price vector accepted")
    require(price_optimum([1] * 6, 1, 1) == 14, "unpaid scale shortcut escaped")
    counts["unpaid_scale_budget"] += 1
    return dict(sorted(counts.items()))


def build_certificate():
    source = read_sources()
    require(tuple(map(tuple, source["matrix"])) == MATRIX, "predecessor matrix drift")
    old_words = {name: source["witnesses"][name] for name in OPERATORS}
    new_words = {name: scaled_repair(w) for name, w in old_words.items()}
    for name in OPERATORS:
        require(is_query_map(old_words[name], MATRIX), "predecessor witness incorrect")
        require(is_query_map(new_words[name], MATRIX), "new witness incorrect")
        counts = Counter(k + str(i) for k, i, _ in new_words[name] if k != "S")
        require(counts == Counter({n: 3 if n == name else 2 for n in OPERATORS}),
                "incorrect ordinary-query bill")
        require(Counter(v for k, _, v in new_words[name] if k == "S") == {"2": 1, "1/2": 1},
                "incorrect scaling bill")
    fs = factors()
    leaf_words = {name: expand(w, fs) for name, w in new_words.items()}
    old_leaf_words = {name: expand(w, fs) for name, w in old_words.items()}
    for word in [*leaf_words.values(), *old_leaf_words.values()]:
        require(free_map(word) == expected_free(fs), "expanded forward map failed")
        require(free_map(inverse(word)) == expected_free(fs, -1), "expanded inverse map failed")
    prices = [sum(e[0] == "F" for e in expand_product(fs[n], 0, 6)) for n in OPERATORS]
    require(prices == [4, 10, 16, 28, 40, 52], "seed fixture prices drifted")
    price_tests = []
    for cheapest in range(6):
        vector = [Q(3 + j, 2) for j in range(6)]
        vector[cheapest] = Q(1)
        for up, down in ((Q(1, 5), Q(2, 5)), (Q(1, 3), Q(2, 3)), (Q(3, 2), Q(2))):
            candidates = [literal_price(w, vector, up, down) for w in [*old_words.values(), *new_words.values()]]
            optimum = price_optimum(vector, up, down)
            require(min(candidates) == optimum, "literal word misses weighted optimum")
            price_tests.append({"cheapest": OPERATORS[cheapest], "prices": list(map(str, vector)),
                                "double": str(up), "halve": str(down), "optimum": str(optimum)})
    selected = OPERATORS[SEED % 6]
    result = {
        "schema_version": 1, "base_commit": BASE, "assignment_seed": SEED,
        "status": "PASS_COMPLEX_DYADIC_CONNECTOR",
        "scope": "Exact characteristic-zero circuit and fixed-price optimum with paid root doubling/halving; no new kappa or selected supplier admission.",
        "matrix": MATRIX, "words": new_words,
        "twelve_query_reduction_census": path_census(), "orbit": orbit_replay(new_words),
        "factors_in_application_order": fs, "child_leaf_prices": prices,
        "recursive_words": {name: {"factor_calls": sum(e[0] == "F" for e in word),
                                    "root_scalings": sum(e[0] == "S" for e in word),
                                    "literal_sha256": digest(word)} for name, word in leaf_words.items()},
        "selected_fixture": {"operator": selected, "old_factor_calls": len(old_leaf_words[selected]),
                             "new_factor_calls": sum(e[0] == "F" for e in leaf_words[selected]),
                             "root_scalings": 2, "borrowed_dirty_rows": 4,
                             "unit_leaf_and_scaling_tariffs_total": str(price_optimum(prices, 1, 1)),
                             "literal_word": leaf_words[selected]},
        "free_factor_maps_forward_and_inverse": 24,
        "dense_basis_maps": dense_replay(leaf_words, fs),
        "dense_data_tape_invoices": dense_invoices(old_leaf_words[selected], leaf_words[selected], fs),
        "weighted_tariff_fixtures": price_tests,
        "negative_controls": controls(new_words, leaf_words, fs),
    }
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly regenerate the certificate")
    parser.add_argument("--certificate", type=Path, default=PACKAGE / "CERTIFICATE.json")
    args = parser.parse_args()
    require(not args.write or args.certificate == PACKAGE / "CERTIFICATE.json", "write only the package certificate")
    result = build_certificate()
    if args.write:
        args.certificate.write_text(json.dumps(result, indent=2) + "\n")
    require(json.loads(args.certificate.read_text()) == result, "certificate differs from exact replay")
    controls_count = sum(result["negative_controls"].values())
    print("PASS_COMPLEX_DYADIC_CONNECTOR paths=720 orbit=288 query_maps=3456 "
          "leaf_maps=24 dense_maps=240 old_leaves=308 new_leaves=304 scales=2 "
          f"controls={controls_count} no_new_kappa")


if __name__ == "__main__":
    main()
