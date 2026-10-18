#!/usr/bin/env python3
"""Exact quadratic-reader boundary experiment. @theon199 + OpenAI Codex.

Apache-2.0. The polynomial oracle and numerical interpreter are separate
implementations. Explicit exceptions keep all checks active under python -O.
"""
import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256, sha1
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def moments(alpha, beta):
    require(len(alpha) == len(beta) and len(alpha) > 0, "nonempty paired batch required")
    prefix = F(0)
    first = second = F(0)
    for drift, reader in zip(alpha, beta):
        first += reader * prefix
        second += reader * prefix * prefix
        prefix += drift
    return prefix, first, second


def event(kind, coefficient):
    return (kind, F(coefficient))


def eager(alpha, beta):
    word = []
    for drift, reader in zip(alpha, beta):
        if reader:
            word.append(event("square_a", reader))
        if drift:
            word.extend([event("shift", drift), event("shift", -drift)])
    return word


def deferred(alpha, beta, square_only=False):
    """The final two/three source shifts also perform source restoration."""
    total, first, second = moments(alpha, beta)
    word = []
    for drift, reader in zip(alpha, beta):
        if reader:
            word.append(event("square_a", reader))
        if drift:
            word.append(event("shift", drift))
    if first and square_only:
        u = (second / first + 1) / 2
        v = u - 1
        word.extend([event("shift", u - total), event("square_a", -first),
                     event("shift", -1), event("square_a", first), event("shift", -v)])
    elif first:
        t = second / (2 * first)
        word.extend([event("shift", t - total), event("product", -2 * first),
                     event("shift", -t)])
    else:
        word.append(event("shift", -total))
        if second:
            word.append(event("square_b", -second))
    return [(kind, coefficient) for kind, coefficient in word if coefficient]


def execute(word, values):
    """Literal exact scalar program, with arbitrary incoming y, a, b."""
    y, a, b = map(F, values)
    for kind, coefficient in word:
        if kind == "shift":
            a += coefficient * b
        elif kind == "square_a":
            y += coefficient * a * a
        elif kind == "square_b":
            y += coefficient * b * b
        elif kind == "product":
            y += coefficient * a * b
        else:
            raise ValueError("unknown event: " + kind)
    return y, a, b


def inverse(word):
    return [(kind, -coefficient) for kind, coefficient in reversed(word)]


class AccessStore:
    """Observe every addressed data access of a second scalar interpreter."""
    def __init__(self, values):
        self.values = list(map(F, values))
        self.reads = self.writes = 0

    def __getitem__(self, index):
        self.reads += 1
        return self.values[index]

    def __setitem__(self, index, value):
        self.writes += 1
        self.values[index] = value


def observed_execute(word, values, duplicate_read=False):
    state = AccessStore(values)
    for kind, coefficient in word:
        if duplicate_read:
            _ = state[2]
        if kind == "shift":
            target, donor = state[1], state[2]
            state[1] = target + coefficient * donor
        elif kind == "square_a" or kind == "square_b":
            target, donor = state[0], state[1 if kind == "square_a" else 2]
            state[0] = target + coefficient * donor * donor
        elif kind == "product":
            target, left, right = state[0], state[1], state[2]
            state[0] = target + coefficient * left * right
        else:
            raise ValueError("unknown observed event")
    return tuple(state.values), state.reads, state.writes


# Independent sparse polynomials in original y, a, b, with rational coefficients.
# Their multiplication checks mixed terms, which dirty-state basis probes miss.
def add(left, right, scale=F(1)):
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, F(0)) + scale * coefficient
    return {key: value for key, value in result.items() if value}


def multiply(left, right):
    result = {}
    for x, c in left.items():
        for z, d in right.items():
            key = tuple(i + j for i, j in zip(x, z))
            result[key] = result.get(key, F(0)) + c * d
    return {key: value for key, value in result.items() if value}


def polynomial_replay(word):
    rows = [{(1, 0, 0): F(1)}, {(0, 1, 0): F(1)}, {(0, 0, 1): F(1)}]
    peak = F(1)
    denominator = 1
    for kind, coefficient in word:
        if kind == "shift":
            rows[1] = add(rows[1], rows[2], coefficient)
        elif kind == "square_a":
            rows[0] = add(rows[0], multiply(rows[1], rows[1]), coefficient)
        elif kind == "square_b":
            rows[0] = add(rows[0], multiply(rows[2], rows[2]), coefficient)
        elif kind == "product":
            rows[0] = add(rows[0], multiply(rows[1], rows[2]), coefficient)
        else:
            raise ValueError("unknown polynomial event")
        peak = max(peak, *(sum(abs(c) for c in row.values()) for row in rows))
        denominator = max(denominator, *(c.denominator for row in rows for c in row.values()))
    return rows, peak, denominator


def expected_polynomials(beta):
    return [{(1, 0, 0): F(1), **({(0, 2, 0): F(sum(beta))} if sum(beta) else {})},
            {(0, 1, 0): F(1)}, {(0, 0, 1): F(1)}]


def invoice(word):
    """Literal scalar-expression price; constants are never free scalings."""
    counts = Counter(add=0, square_mul=0, cross_mul=0, constant_mul=0,
                     data_reads=0, data_writes=0, descriptor_fields=0, events=0)
    for kind, coefficient in word:
        require(coefficient != 0, "zero event should be removed")
        counts["add"] += 1
        counts["events"] += 1
        counts["data_writes"] += 1
        counts["constant_mul"] += int(abs(coefficient) != 1)
        counts["data_reads"] += 3 if kind == "product" else 2
        counts["descriptor_fields"] += 5 if kind == "product" else 4
        if kind.startswith("square"):
            counts["square_mul"] += 1
        elif kind == "product":
            counts["cross_mul"] += 1
        else:
            require(kind == "shift", "unknown invoice event")
    counts["scalar_operations"] = sum(counts[key] for key in
                                      ("add", "square_mul", "cross_mul", "constant_mul"))
    return dict(sorted(counts.items()))


def check_batch(alpha, beta, probes=False):
    target = expected_polynomials(beta)
    words = [eager(alpha, beta), deferred(alpha, beta), deferred(alpha, beta, True)]
    for word in words:
        require(polynomial_replay(word)[0] == target, "wrong full polynomial endpoint")
        require(polynomial_replay(word + inverse(word))[0] == expected_polynomials([0]),
                "inverse failed on full polynomial state")
    if probes:
        for values in product((-1, 0, 1), repeat=3):
            y, a, b = map(F, values)
            wanted = (y + sum(beta) * a * a, a, b)
            for word in words:
                require(execute(word, values) == wanted, "scalar/polynomial disagreement")
                require(execute(inverse(word), wanted) == tuple(map(F, values)),
                        "literal scalar inverse failed")


def tree_events(depth, n, batch_word, level=0, start=0):
    """Binary tree: children first; each level has its own two dirty streams."""
    if depth == 0:
        return []
    require(n % 2 == 0, "binary node must split evenly")
    result = []
    for offset in (0, n // 2):
        result.extend(tree_events(depth - 1, n // 2, batch_word, level + 1, start + offset))
    for gate in batch_word:
        for position in range(start, start + n):
            result.append((level, position, gate))
    return result


def execute_tree(events, y, a, b):
    y, a, b = list(map(F, y)), [list(map(F, row)) for row in a], [list(map(F, row)) for row in b]
    for level, position, gate in events:
        yy, aa, bb = execute([gate], (y[position], a[level][position], b[level][position]))
        y[position], a[level][position], b[level][position] = yy, aa, bb
    return y, a, b


def failure_controls():
    alpha = beta = (1,) * 8
    good = deferred(alpha, beta)
    values = (F(7, 3), F(2, 5), F(-3, 7))
    wanted = execute(eager(alpha, beta), values)
    mutants = {
        "omitted_nonlinear_repair": [g for g in good if g[0] != "product"],
        "wrong_repair_sign": [(k, -c if k == "product" else c) for k, c in good],
        "missing_source_restoration": good[:-1],
        "wrong_repair_frame": good[:-3] + [event("shift", -8), good[-2], good[-1]],
    }
    for name, word in mutants.items():
        require(execute(word, values) != wanted, "mutation escaped: " + name)
    require(execute(good[:4], values)[0] != execute(eager(alpha[:2], beta[:2]), values)[0],
            "unsafe intermediate observation escaped")
    # Signed readers can hide a pure mixed defect from all coordinate basis tests.
    raw = [("square_a", F(1)), ("shift", F(1)), ("square_a", F(1)),
           ("shift", F(-2)), ("square_a", F(-1)), ("shift", F(1))]
    plain = eager((1, -2, 1), (1, 1, -1))
    for value in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        require(execute(raw, value) == execute(plain, value), "basis-blind fixture changed")
    require(execute(raw, (0, 1, 1))[0] - execute(plain, (0, 1, 1))[0] == 4,
            "mixed-term negative control failed")
    free = invoice(good)
    require(free["constant_mul"] == 3 and free["scalar_operations"] == 31,
            "nonunit scalings were not fully priced")
    extra, reads, writes = observed_execute(good, values, duplicate_read=True)
    require(extra == wanted and (reads, writes) != (free["data_reads"], free["data_writes"]),
            "uncharged repeated-read control escaped")
    # A source-basis repair without the product does restore a, but leaves a false y.
    return {"rejected_word_mutations": sorted(mutants), "unsafe_prefix": True,
            "basis_only_false_acceptance": {"basis_probes": 3, "mixed_defect_at_1_1": 4},
            "nonunit_price": {"multiplications": 3, "unpaid_false_total": 28},
            "uncharged_repeated_read": {"wrong_reads": reads, "correct_reads": free["data_reads"]}}


def source_checks():
    data = json.loads((HERE / "CONTEXT.json").read_text())
    require(data["base_commit"] == "ef5f39403610d231a0c27e8a6b4f08c10209bcd6", "base pin changed")
    require(data["predecessor_heads"] == {
        "PR1205": "e2008d7ffcad464da7ec21c69e8d8a8c91de4930",
        "PR1246": "5ed1ce17a9df4c853a93f9758ba903d2620c3443"}, "predecessor head changed")
    for row in data["files"]:
        contents = (HERE / row["path"]).read_bytes()
        require(sha256(contents).hexdigest() == row["sha256"], "source content mismatch")
        blob = sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()
        require(blob == row["git_blob"], "source blob mismatch")
    return data


def certificate():
    sources = source_checks()
    census = Counter()
    for length in range(1, 6):
        for choices in product(tuple(product((-1, 1), repeat=2)), repeat=length):
            alpha, beta = zip(*choices)
            check_batch(alpha, beta, probes=True)
            _, first, second = moments(alpha, beta)
            rank = 2 if first else int(second != 0)
            census["batches"] += 1
            census["repair_rank_" + str(rank)] += 1
    cases = []
    for length in range(2, 17):
        alpha = beta = (1,) * length
        check_batch(alpha, beta, probes=True)
        records = {label: invoice(word) for label, word in (
            ("eager", eager(alpha, beta)), ("bilinear", deferred(alpha, beta)),
            ("square_only", deferred(alpha, beta, True)))}
        for label, word in (("eager", eager(alpha, beta)), ("bilinear", deferred(alpha, beta)),
                            ("square_only", deferred(alpha, beta, True))):
            endpoint, reads, writes = observed_execute(word, (F(7, 3), F(2, 5), F(-3, 7)))
            require(endpoint == execute(word, (F(7, 3), F(2, 5), F(-3, 7))), "access oracle endpoint failed")
            require((reads, writes) == (records[label]["data_reads"], records[label]["data_writes"]),
                    "literal addressed-access invoice failed")
        require(records["eager"]["scalar_operations"] == 4 * length, "eager cost formula failed")
        require(records["bilinear"]["scalar_operations"] == 3 * length + 7, "fused cost formula failed")
        cases.append({"arity": length, "costs": records})
    # Truly rational source drift and reader weights, outside the signed census.
    rational = ((F(2, 3), F(-5, 7), F(3, 2)), (F(4, 5), F(-2, 3), F(7, 4)))
    check_batch(*rational, probes=True)
    trees = []
    eager_word, fused_word = eager((1,) * 8, (1,) * 8), deferred((1,) * 8, (1,) * 8)
    for depth in range(4):
        n = 2 ** depth
        y = [F(i - 2, 3) for i in range(n)]
        a = [[F(2 * level + i - 1, 5) for i in range(n)] for level in range(depth)]
        b = [[F(i - level + 2, 7) for i in range(n)] for level in range(depth)]
        expected_y = [y[i] + 8 * sum(a[level][i] ** 2 for level in range(depth)) for i in range(n)]
        summaries = {}
        for label, word in (("eager", eager_word), ("bilinear", fused_word)):
            events = tree_events(depth, n, word)
            actual = execute_tree(events, y, a, b)
            require(actual == (expected_y, a, b), "recursive dirty-state endpoint failed")
            reversed_events = [(lev, pos, (k, -c)) for lev, pos, (k, c) in reversed(events)]
            require(execute_tree(reversed_events, *actual) == (y, a, b), "recursive inverse failed")
            bill = invoice([gate for _, _, gate in events])
            require(bill["scalar_operations"] == invoice(word)["scalar_operations"] * n * depth,
                    "complete recursive recurrence failed")
            summaries[label] = bill
        trees.append({"depth": depth, "n": n, "dirty_data_scalars": (2 * depth + 1) * n,
                      "internal_nodes": 2 ** depth - 1, "costs": summaries})
    _, peak, denominator = polynomial_replay(fused_word)
    return {"schema_version": 1, "status": "scoped nonlinear boundary; no new kappa",
            "sources": sources, "assignment_seed": 55,
            "census": {**dict(sorted(census.items())), "numeric_assignments": census["batches"] * 27,
                       "lengths": [1, 2, 3, 4, 5], "alphabet": "alpha,beta in {-1,+1}"},
            "pilot": {"arity": 8, "moments": [str(v) for v in moments((1,) * 8, (1,) * 8)],
                      "bilinear_word": [[k, str(c)] for k, c in fused_word],
                      "peak_polynomial_coefficient_l1": str(peak),
                      "largest_stored_coefficient_denominator": denominator},
            "cost_cases": cases, "recursive_cases": trees, "rational_fixture": True,
            "controls": failure_controls()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print a freshly computed certificate; no file writes")
    args = parser.parse_args()
    try:
        result = certificate()
        if args.emit:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            require(result == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate mismatch")
            print("PASS_QUADRATIC_READER batches=1364 pilot=32->31 square_repair_rank=2 controls=8 kappa=unchanged")
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_QUADRATIC_READER: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
