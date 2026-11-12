"""Exact Gaussian-rational probes for the selected R76 rank-two correction."""
from dataclasses import dataclass
from fractions import Fraction as Q
from json import dumps, loads
from pathlib import Path
import argparse
import runpy
from math import prod
from time import monotonic


@dataclass(frozen=True, eq=False)
class G:
    re: Q = Q(0)
    im: Q = Q(0)

    def __bool__(self):
        return bool(self.re or self.im)

    def __eq__(self, other):
        other = lift(other)
        return self.re == other.re and self.im == other.im

    def __str__(self):
        return f"{self.re}+({self.im})i" if self.im else str(self.re)

    def __add__(self, other):
        other = lift(other)
        return G(self.re + other.re, self.im + other.im)

    __radd__ = __add__

    def __neg__(self):
        return G(-self.re, -self.im)

    def __sub__(self, other):
        return self + -lift(other)

    def __rsub__(self, other):
        return lift(other) + -self

    def __mul__(self, other):
        other = lift(other)
        return G(self.re * other.re - self.im * other.im, self.re * other.im + self.im * other.re)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = lift(other)
        d = other.re * other.re + other.im * other.im
        return self * G(other.re / d, -other.im / d)

    def __rtruediv__(self, other):
        return lift(other) / self


def lift(value):
    return value if isinstance(value, G) else G(Q(value))


def qpow(q, power):
    return (G(Q(1)), q, G(Q(-1)), -q)[power % 4]


def gaussian_ops(event, q, alpha, bodies, even):
    family, op, *args = event
    if family == "B":
        return []
    if family == "J":
        u, v, x, y = args[0]
        scalar = bodies[op - 1]
        return [("ADD", v, u, 1 / q), ("ADD", x, y, alpha * q)] + (
            [("SCALE", r, r, scalar) for r in (u, v, x, y)] if scalar != 1 else [])
    if family != "A":
        raise ValueError("unknown caller family")
    dst, *tail = args
    if op == "ADD":
        return [(op, dst, tail[0], Q(tail[1]))]
    if op == "SCALE":
        return [(op, dst, dst, Q(tail[0]))]
    if op == "SWAP":
        return [(op, dst, tail[0], Q(1))]
    if op == "LAMBDA":
        # (1+i sign)/2 + (1-i sign)q²/2 at q=±i.
        return [("SCALE", dst, dst, G(Q(0), Q(tail[0])))]
    if op == "QUERY":
        return [("ADD", dst, tail[0], Q(1) if even else qpow(q, tail[1]))]
    if op in ("IDLE_ODD", "IDLE_ONE"):
        c = prod(bodies[s - 1] for s in tail[0])
        if op == "IDLE_ODD":
            c *= qpow(q, tail[1])
        return [("SCALE", dst, dst, c)] if c != 1 else []
    raise ValueError("unknown Type A operation")


def probe(engine, caller, pair, q, bodies):
    first, second = pair
    events = caller["events"]
    ty = caller["types"]["A"]
    d, s = events[first][2:4]
    tape = [op for t in range(first, second)
            for op in gaussian_ops(events[t], q, Q(ty["alpha2"]), bodies, t == first)]
    u, v = engine["transported"](tape, ty["roles"], d, s)
    N = engine["residual"](u, v, d, s, qpow(q, -1) - 1)
    return N, [str(v[d]), str(u[s])]


def main(args):
    start = monotonic()
    root = Path(__file__).resolve().parent
    formal = runpy.run_path(str(root / "formal_necessity.py"))
    pinned, pair = formal["load"], formal["PAIR"]
    engine_path = root / "transported_product.py"
    pinned(engine_path, formal["ENGINE"])
    engine = runpy.run_path(str(engine_path))
    rank, check = engine["rank"], engine["require"]
    price = loads(pinned(args.price, formal["PRICE"]))
    unit = loads(pinned(args.unit_receipt, formal["UNIT"]))
    check(price["formal_case_cap"] == 1 and price["formal_runner_seconds"] == 90 and
          list(pair) in unit["rank_at_most_two_square_zero_keys"], "wrong fixed pair")
    caller = loads(pinned(args.caller, engine["CALLER"]))
    i = G(Q(0), Q(1))
    check(i * i == -1 and 1 / i == -i and (Q(1, 3) + i) / (Q(1, 3) + i) == 1, "Gaussian field control")
    check(gaussian_ops(["A", "LAMBDA", 1, -1], i, Q(-1), (Q(1),) * 17, False)[0][-1] == -i,
          "Gaussian LAMBDA control")
    verdict = "gaussian_necessary_probes_inconclusive"
    receipts = []
    baseline = {}
    for stage in (0, *range(1, 18)):
        if monotonic() - start >= 90:
            verdict = "runner_cap"
            break
        bodies = [Q(1)] * 17
        if stage:
            bodies[stage - 1] = Q(2)
        matrices, details = {}, {}
        for name, q in (("i", i), ("minus_i", -i)):
            N, cross = probe(engine, caller, pair, q, bodies)
            matrices[name] = N
            sq = engine["product"](N, N)
            details[name] = {"rank": rank(N), "square_rank": rank(sq),
                             "first_square_nonzero": engine["first_nonzero"](sq), "cross_terms": cross}
            if stage:
                details[name]["vs_unit"] = formal["compare"](baseline[name], N, rank)
                details[name]["first_entry_difference_vs_unit"] = formal["first_difference"](baseline[name], N)
        comparison = formal["compare"](matrices["i"], matrices["minus_i"], rank)
        receipts.append({"nonunit_variable": stage or None, "characters": details, "q_even_shape": comparison})
        if any(v["square_rank"] for v in details.values()):
            verdict = "nonzero_square_excludes_provider"
            break
        if any(v["rank"] > 2 for v in details.values()):
            verdict = "rank_excludes_provider"
            break
        if comparison["joint_row_rank"] > 2 or comparison["joint_column_rank"] > 2:
            verdict = "changing_span_at_same_q_squared_excludes_fixed_q_even_axes"
            break
        if stage and any(
            v["vs_unit"]["joint_row_rank"] > 2 or v["vs_unit"]["joint_column_rank"] > 2 for v in details.values()
        ):
            verdict = "changing_body_span_excludes_fixed_axes"
            break
        if not stage:
            baseline = matrices
    print(dumps({
        "pair": pair, "verdict": verdict, "probes": receipts, "price_sha256": formal["PRICE"],
        "caller_sha256": engine["CALLER"], "unit_receipt_sha256": formal["UNIT"],
        "controls": ["exact Gaussian rational arithmetic", "q²=−1 signed LAMBDA"],
        "unselected_provisional_pair": [1516, 1721],
        "scope": "One selected pair, q=±i with exact rational Gaussian characters. Same q-even axes at the two characters."
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    for name in ("caller", "price", "unit-receipt"):
        p.add_argument("--" + name, type=Path, required=True)
    main(p.parse_args())
