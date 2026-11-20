"""Verify the actual binary operators, cover fibres, weighted leaves and price."""

from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import product
from math import lcm
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from charts import packed, encode
from cover import cold_swap, low_action, high_stream, require, residue
from projectors import binary_native, multiply, placed_port
from leaf import run_columns


def root_column(caller, j, dual, skip=None):
    def shift(terms, stages=(), head=0):
        return {(q ^ head, tuple(sorted(body + tuple(stages)))) for q, body in terms}

    v = [set() for _ in caller["diagonal"]]
    v[j].add((0, ()))
    order = range(len(caller["events"]))
    for k in reversed(order) if dual else order:
        if k == skip:
            continue
        op, *a = caller["events"][k]
        if op == "LOCAL":
            s, x, y = a
            if dual:
                x, y = y, x
            old = v[x]
            v[x] = shift(old, (s,))
            v[y] = shift(v[y] ^ shift(old, head=1), (s,))
        elif op == "IDLE_ONE":
            x, ss = a
            v[x] = shift(v[x], ss)
        else:
            x, y = reversed(a) if dual else a
            if op == "SWAP":
                v[x], v[y] = v[y], v[x]
            else:
                require(op in ("ADD", "QUERY"), "caller gate")
                v[x] ^= shift(v[y], head=int(op == "QUERY"))
    return v


def caller_price(caller, raw_paid, helpers, baseline):
    paid, targets = Counter(), Counter()
    roles = caller["roles"]
    query = next(t for t, e in enumerate(caller["events"]) if e[0] == "QUERY")
    failures = []
    for dual in (False, True):
        count = 0
        for j, d in enumerate(caller["diagonal"]):
            cols = [set() for _ in range(roles)]
            cols[j] = {(d["q"], tuple(sorted(d["stages"])))}
            require(root_column(caller, j, dual) == cols, "root operator polynomial")
            count += sum(
                x != y
                for x, y in zip(root_column(caller, j, dual, query), cols, strict=True)
            )
        failures.append(count)
    stages = {}
    for op, *a in caller["events"]:
        if op == "LOCAL":
            s, x, y = a
            cohort = stages.setdefault(s, set())
            require(x != y and cohort.isdisjoint((x, y)), "disjoint paired slots")
            cohort.update((x, y))
            paid.update(raw_paid)
            targets.update(helpers)
        elif op == "QUERY":
            paid[1] += 111
        elif op == "IDLE_ONE":
            paid[7 * len(a[1])] += 111
    for d in caller["diagonal"]:
        targets[1 + 7 * len(d["stages"])] += 111
    require(
        sorted(stages) == list(range(1, 19))
        and all(len(v) == 4 for v in stages.values()),
        "36 native sites",
    )
    for counts, k in ((paid, "paid"), (targets, "targets")):
        require(
            dict(counts) == {int(g): v for g, v in baseline[k].items()},
            "full priced BIT profile",
        )
    return dict(
        paid=sum(paid.values()),
        outputs=sum(targets.values()),
        root_coefficients_each_way=roles**2,
        omitted_query_failures=failures,
    )


def placement_columns(word, ports):
    """Check the native head, both body directions and the complete exterior."""
    cases = moved = columns = 0
    for i, port in enumerate(ports):
        raw = word["frames"]
        lines = raw[str(word["start"][i])]["B"] + raw[str(word["final"][111 + i])]["B"]
        basis = [list(map(Fraction, row)) for row in lines]
        for stage in range(18):
            first = 8 + 7 * stage
            exterior = [0] * 8 + [k + 1 for k in range(8, 134)]
            exterior[first : first + 7] = [0] * 7
            require(
                placed_port(port, stage, exterior) == exterior, "complete port exterior"
            )
            for j, direction in enumerate(basis):
                native = exterior.copy()
                native[:8] = direction
                if j == 0:
                    require(
                        placed_port(port, stage, native) == native,
                        "fixed physical port head",
                    )
                else:
                    body = exterior.copy()
                    body[first + j - 1] = 1
                    require(
                        placed_port(port, stage, native) == body,
                        "native complement to fresh stage",
                    )
                    require(
                        placed_port(port, stage, body) == native,
                        "fresh stage to native complement",
                    )
                    moved += 2
            cases += 1
            columns += 15
    return dict(
        stages=cases,
        active_basis_columns=columns,
        exterior_cases=cases,
        directions_changed_by_identity=moved,
    )


def mixed_cut(word, charts):
    """Route two independent roles through one child that mixes their input fields."""
    group = [g for g in product(range(3), repeat=4) if (g[0] * g[3] - g[1] * g[2]) % 3]
    points = list(product(range(3), repeat=4))
    match = [(1, 1, 0, 1), (1, 0, 1, 1)]
    target = []
    for i in range(2):
        rank, den, matrix = charts[word["start"][i]]
        require(
            rank == 1
            and all(
                matrix[j][k] == den * int(j == k == i)
                for j in range(8)
                for k in range(8)
            ),
            "two source head lines",
        )
        target.append(tuple(matrix[j][k] // den for j in range(2) for k in range(2)))

    def mul(a, b):
        return tuple(
            sum(a[i * 2 + k] * b[k * 2 + j] for k in range(2)) % 3
            for i in range(2)
            for j in range(2)
        )

    def inv(g):
        a, b, c, d = g
        z = pow(a * d - b * c, -1, 3)
        return tuple(x * z % 3 for x in (d, -b, -c, a))

    def conjugate(g, p):
        return mul(mul(g, p), inv(g))

    @cache
    def header(g, s):
        h, _ = low_action([g[:2], g[2:]], [s[:2], s[2:]], 3)
        return tuple(h[0] + h[1])

    @cache
    def addresses(p):
        # The common head weight is (2,1). The tail has opposite atom order.
        perm = []
        for a, b, c, d in points:
            x, y = d - 2 * a, c - b
            u, v = p[0] * x + p[1] * y, p[2] * x + p[3] * y
            aa, bb, cc, dd = [z % 3 for z in (a + 2 * u, b + v, c - v, d - u)]
            perm.append(((3 * aa + bb) * 3 + cc) * 3 + dd)
        require(
            sorted(perm) == list(range(len(points))),
            "permutation on the complete payload",
        )
        return perm

    def job(p, data):
        out = [0] * len(points)
        for dst, value in zip(addresses(p), data, strict=True):
            out[dst] = value
        return out

    parent = {
        (r, g): [
            1 << (len(points) * (len(group) * r + i) + k) for k in range(len(points))
        ]
        for r in range(2)
        for i, g in enumerate(group)
    }
    failures = {}
    for mode in ("correct", "reverse_matcher", "omit_donor", "omit_return"):
        matcher = [inv(s) for s in match] if mode == "reverse_matcher" else match
        child = {(r, header(g, matcher[r])): v for (r, g), v in parent.items()}
        for h in group:
            x, y = child[0, h], child[1, h]
            x, y = (
                job(conjugate(h, target[0]), x),
                job(
                    conjugate(h, target[1]), [a ^ b for a, b in zip(x, y, strict=True)]
                ),
            )
            if mode != "omit_donor":
                # The full interchange after the first projector equals the second projector.
                y = [b ^ a for b, a in zip(y, job((1, 0, 0, 1), x), strict=True)]
            child[0, h], child[1, h] = x, y
        wrong = 0
        for (r, g), v in parent.items():
            h = g if mode == "omit_return" else header(g, matcher[r])
            want = job(conjugate(g, conjugate(match[r], target[r])), v)
            wrong += sum(a != b for a, b in zip(child[r, h], want, strict=True))
        failures[mode] = wrong
    require(
        failures.pop("correct") == 0 and all(failures.values()),
        "routed whole-job cut and return",
    )
    return dict(parent_slots=len(parent) * len(points), mutant_errors=failures)


def cover_probes():
    records = cases = carry_errors = 0
    group = [a for a in product(range(3), repeat=4) if (a[0] * a[3] - a[1] * a[2]) % 3]
    for matrix in (
        [[0, 1], [1, Fraction(-2, 7)]],
        [[Fraction(4, 5), Fraction(2, 5)], [Fraction(1, 5), Fraction(3, 5)]],
        [[7, 3], [9, 4]],
    ):
        for low in group:
            g0 = [low[:2], low[2:]]
            for width in (1, 2, 3) if low == (0, 1, 1, 0) else (1, 2):
                size = 3 ** (width - 1)
                target, c = low_action(g0, matrix, 3)
                result = high_stream(range(size**4), matrix, 3, width, c)
                no_carry = high_stream(
                    range(size**4), matrix, 3, width, [[0, 0], [0, 0]]
                )
                carry_errors += sum(
                    a != b for a, b in zip(result, no_carry, strict=True)
                )
                for i, high in enumerate(product(range(size), repeat=4)):
                    value = [
                        [g0[s][j] + 3 * high[2 * s + j] for j in range(2)]
                        for s in range(2)
                    ]
                    actual = multiply(value, matrix)
                    out = 0
                    for s in range(2):
                        for j in range(2):
                            entry = residue(actual[s][j], 3 * size)
                            require(target[s][j] == entry % 3, "full low class")
                            out = out * size + entry // 3
                    require(result[out] == i, "whole high-fibre permutation")
                records += len(result)
                cases += 1
    require(carry_errors > 0, "dropped fixed-low carry control")
    return dict(cases=cases, high_records=records, omitted_carry_errors=carry_errors)


def seed_rows():
    cases = count = 0
    for q, w in ((2, 1), (2, 3), (3, 1), (3, 3)):
        for prefix, gap, suffix in ((1, 1, 1), (2, 3, 2)):
            side = q**w
            n = prefix * gap * suffix * side**2
            data = cold_swap(range(n), q, w, prefix, gap, suffix)
            for ix, label in enumerate(data):
                a, s = divmod(ix, suffix)
                a, h = divmod(a, side)
                a, middle = divmod(a, gap)
                pre, d = divmod(a, side)
                expected = (((pre * side + h) * gap + middle) * side + d) * suffix + s
                require(label == expected, "ordinary cold service")
            count += n
            cases += 1
    return dict(cases=cases, records=count)


def weighted_probes(charts, word):
    from retained.fallback import conjugate_diagonal, residual
    from random import Random

    prime, width = 5, 2
    m, modulus = 8, 25
    clock, owner, source, destination = 12, 683, 2, 125
    require(
        word["program"][clock] == ["MOVE", owner, source, destination],
        "literal rank-one leaf probe source",
    )
    ru, du, u = charts[source]
    rv, dv, v = charts[destination]
    require(rv - ru == 1, "rank of the probed native leg")
    native = [
        [
            (residue(Fraction(v[i][j], dv) - Fraction(u[i][j], du), modulus))
            for j in range(m)
        ]
        for i in range(m)
    ]
    # Conjugate the actual projector by invertible elementary shears.
    # Use the full ring, including nonzero multiples of the prime.
    examples = {}
    random = Random(7835)
    p = [row.copy() for row in native]
    for _ in range(2000):
        i, j = random.sample(range(m), 2)
        c = random.randrange(1, modulus)
        p[i] = [(x + c * y) % modulus for x, y in zip(p[i], p[j], strict=True)]
        for row in p:
            row[j] = (row[j] - c * row[i]) % modulus
        pivot = p[0][0]
        if pivot:
            examples.setdefault(bool(pivot % prime), [row.copy() for row in p])
        if len(examples) == 2:
            break
    require(len(examples) == 2, "actual good and nonzero nonunit pivots")
    counts = {}
    for good, p in examples.items():
        total = 0
        for f in (1, 2, 5):
            weights = [
                [(1, 2, 6, 7, 8, 9, 11, 12)[(j + 2 * i) % 8] for i in range(m)]
                for j in range(f)
            ]
            matrices = [
                conjugate_diagonal(residual(p, modulus), a + [1] * m, modulus)
                for a in weights
            ]
            for pos in range(2 * m * f):
                fields = [
                    [int(i * f + j == pos) for j in range(f)] for i in range(2 * m)
                ]
                result, actual, calls = run_columns(
                    p, weights, fields[:m], fields[m:], prime, width
                )
                require(
                    actual == good
                    and (calls == [f] if good else len(calls) < 32 * m**2),
                    "paid leaf",
                )
                for j, matrix in enumerate(matrices):

                    def index(i):
                        return j if i < m else f - 1 - j

                    x = [fields[i][index(i)] for i in range(2 * m)]
                    want = [
                        sum(a * b for a, b in zip(row, x, strict=True)) % modulus
                        for row in matrix
                    ]
                    require(
                        want == [z[index(i)] for i, z in enumerate(result)],
                        "weighted original order",
                    )
                total += 1
        counts["good" if good else "bad"] = dict(pivot=p[0][0], basis_positions=total)
    counts["source_move"] = dict(
        clock=clock, owner=owner, source=source, destination=destination
    )
    return counts


def run():
    word = packed(HERE / "retained/data/binary.json.gz")
    caller_path = HERE.parent / "paired-query-only-bit/EFREE-CALLER.json.gz"
    bit = json.loads((HERE / "retained/grade14-bit.json").read_bytes())
    require(
        sha256(encode(word)).hexdigest() == bit["word_sha256"], "priced binary word"
    )
    require(
        sha256(caller_path.read_bytes()).hexdigest() == bit["native"]["caller_sha256"],
        "priced binary caller",
    )
    caller = packed(caller_path)
    charts, ports, paid, helpers = binary_native(word)
    placement = placement_columns(word, ports)
    return dict(
        frames=len(charts),
        port_stages=placement["stages"],
        port_placement=placement,
        native_coefficients_each_way=word["public"] ** 2,
        raw_paid=sum(paid.values()),
        raw_helpers=sum(helpers.values()),
        projector_denominator_lcm=lcm(*(d for _, d, _ in charts.values())),
        caller=caller_price(caller, paid, helpers, bit["native"]),
        weighted=weighted_probes(charts, word),
        cover=cover_probes(),
        mixed_cut=mixed_cut(word, charts),
        cold=seed_rows(),
    )


if __name__ == "__main__":
    result = run()
    if "--emit" not in sys.argv:
        require(
            result == json.loads((HERE / "RESULT.json").read_bytes())["binary"],
            "frozen BIT evidence",
        )
    print(json.dumps(result, sort_keys=True))
    print("PASS_GRADE14_ALL_COLUMN_BIT")
