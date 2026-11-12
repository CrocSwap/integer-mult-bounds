"""Necessary fixed-axis test on the single R76 pair (1580, 1659)."""
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from math import prod
from time import monotonic
import argparse
import runpy

PAIR = (1580, 1659)
PRICE = "52e05b80069ce01cad3b8e5f3cf9123e930de36987bd398dd43f103953a4674a"
UNIT = "84049bddeed687a28954fa0b8bb993d676900b4eb86ebd6e54ca1f7c60e27887"
ENGINE = "ea1c4e1b1d11f3331bc8a1960779405bffe1839bc5542650f8829c9262244e3d"


def load(path, digest):
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != digest:
        raise ValueError("changed pinned file " + path.name)
    return raw


def transpose(matrix):
    result = {}
    for i, row in matrix.items():
        for j, x in row.items():
            result.setdefault(j, {})[i] = x
    return result


def compare(first, second, rank):
    first_cols, second_cols = transpose(first), transpose(second)
    stack = lambda a, b: dict(enumerate([*a.values(), *b.values()]))
    return {"unit_rank": rank(first), "nonunit_rank": rank(second),
            "joint_row_rank": rank(stack(first, second)),
            "joint_column_rank": rank(stack(first_cols, second_cols))}


def nonunit_emit(engine, event, bodies, q, alpha, even):
    family, op, *args = event
    emitted = engine["emit"](event, q, alpha, even)
    if family == "J":
        d = bodies[op - 1]
        if d != 1:
            emitted.extend(("SCALE", role, role, d) for role in args[0])
    if family == "A" and op in ("IDLE_ODD", "IDLE_ONE"):
        dst, mask, *_ = args
        d = prod(bodies[i - 1] for i in mask)
        if d != 1:
            emitted.append(("SCALE", dst, dst, d))
    return emitted


def probe(engine, caller, q, bodies):
    first, second = PAIR
    events = caller["events"]
    ty = caller["types"]["A"]
    dest, source = events[first][2:4]
    ops = [item for t in range(first, second)
           for item in nonunit_emit(engine, events[t], bodies, q, Q(ty["alpha2"]), t == first)]
    u, v = engine["transported"](ops, ty["roles"], dest, source)
    N = engine["residual"](u, v, dest, source, Q(1, q) - 1)
    return N, [str(v[dest]), str(u[source])]


def first_difference(first, second):
    for i in sorted(first.keys() | second.keys()):
        a, b = first.get(i, {}), second.get(i, {})
        for j in sorted(a.keys() | b.keys()):
            if a.get(j, 0) != b.get(j, 0):
                return [i, j, str(a.get(j, 0)), str(b.get(j, 0))]
    return None


def main(args):
    started = monotonic()
    engine_path = Path(__file__).with_name("transported_product.py")
    load(engine_path, ENGINE)
    engine = runpy.run_path(str(engine_path))
    rank = engine["rank"]
    check = engine["require"]
    check(compare({0: {1: Q(1)}}, {2: {1: Q(2)}}, rank)["joint_column_rank"] == 2,
          "joint column control")
    check(compare({0: {1: Q(1)}}, {0: {3: Q(2)}}, rank)["joint_row_rank"] == 2,
          "joint row control")
    check(compare({0: {1: Q(1)}}, {0: {1: Q(2)}}, rank)["joint_row_rank"] == 1,
          "unchanged span control")
    price = loads(load(args.price, PRICE))
    unit = loads(load(args.unit_receipt, UNIT))
    check(price["formal_case_cap"] == 1 and price["formal_runner_seconds"] == 90 and
          list(PAIR) in unit["rank_at_most_two_square_zero_keys"], "wrong fixed formal stock or cap")
    caller = loads(load(args.caller, engine["CALLER"]))
    check(all(caller["events"][t] == ["A", "QUERY", 0, 1, -1] for t in PAIR), "wrong query pair")
    base, _ = probe(engine, caller, -1, (Q(1),) * 17)
    check(rank(base) == 2 and not engine["product"](base, base), "unit baseline not reproduced")
    verdict = "q_minus_single_body_probes_inconclusive"
    outputs = []
    for j in range(17):
        if monotonic() - started >= 90:
            verdict = "runner_cap"
            break
        bodies = [Q(1)] * 17
        bodies[j] = Q(2)
        plus, _ = probe(engine, caller, 1, bodies)
        check(not plus, "q=+1 did not give identity")
        mutant, cross = probe(engine, caller, -1, bodies)
        square = engine["product"](mutant, mutant)
        summary = compare(base, mutant, rank)
        outputs.append(summary | {"nonunit_variable": j + 1, "value": "2",
                                  "cross_terms": cross,
                                  "first_square_nonzero": engine["first_nonzero"](square),
                                  "first_entry_difference": first_difference(base, mutant)})
        if square:
            verdict = "nonzero_square_excludes_provider"
            break
        if summary["joint_row_rank"] > 2 or summary["joint_column_rank"] > 2:
            verdict = "changing_span_excludes_fixed_axes"
            break
    print(dumps({
        "pair": PAIR, "verdict": verdict, "price_sha256": PRICE, "unit_receipt_sha256": UNIT,
        "caller_sha256": engine["CALLER"], "independent_unit_engine_sha256": ENGINE,
        "probes": outputs, "unselected_provisional_pair": [1516, 1721],
        "scope": "One pair; q=−1 exact single formal body specializations, q=+1 controls. Fixed q-even setup and axes, with no new body-dependent transports."
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for name in ("caller", "price", "unit-receipt"):
        p.add_argument("--" + name, type=Path, required=True)
    main(p.parse_args())
