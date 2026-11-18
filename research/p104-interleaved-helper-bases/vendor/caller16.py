"""Exact signed caller replay, adapted from Ali Romman's #7663 caller.py.

See SOURCE-PINS.json for Rohan Arun's literal #7113-derived caller and
the attributed reference engines. Apache-2.0.
"""

from collections import Counter
from fractions import Fraction
from functools import cache


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_div(numerator, denominator):
    quotient, remainder = divmod(numerator, denominator)
    require(remainder == 0, "inexact caller pre-product")
    return quotient


def literal_layout(caller, word):
    stages = caller["stages"]
    require(stages == 16 and caller["ambient_rank"] == 9 + 8 * stages == 137,
            "literal 16-call, 137-axis layout")
    require(len(caller["events"]) == 4192, "literal caller event count")
    types = caller["types"]
    require(set(types) == {"A", "B"}, "literal type partition")
    require(all(spec["roles"] == 34 for spec in types.values()), "literal 34+34 roles")
    require(types["A"]["ports"] == word["hosted"]["Dports"], "hosted port assignment")
    require((len(types["A"]["ports"]), len(types["B"]["ports"])) == (96, 8),
            "literal 96+8 ports")
    require(sorted(types["A"]["ports"] + types["B"]["ports"]) == list(range(104)),
            "disjoint complete 104-port assignment")
    role_sets = {
        kind: set(range(spec["offset"], spec["offset"] + spec["roles"]))
        for kind, spec in types.items()
    }
    require(role_sets["A"].isdisjoint(role_sets["B"])
            and role_sets["A"] | role_sets["B"] == set(range(caller["roles"])),
            "disjoint complete root role ranges")
    h = word["hosted"]
    coefficients = tuple(Fraction(h[k]) for k in ("alpha", "beta", "alpha2", "beta2"))
    require(coefficients == (-1, Fraction(1, 2), -1, 0), "joint normalized source coefficients")
    require(Fraction(types["A"]["alpha2"]) == coefficients[2], "A second-plane coefficient")
    return stages, types, role_sets


def signed_caller(caller, word, odd_scale, dyadic_height):
    stages, types, role_sets = literal_layout(caller, word)
    unit = odd_scale << dyadic_height
    zero = (0,) * stages
    rows = [{(r, 0, zero): (unit, 0)} for r in range(caller["roles"])]
    paid = Counter()
    targets = Counter()
    uses = Counter()
    calls = []
    checks = 0
    peak = unit
    peak_at = (-1, "entrance")
    clock = -1

    def observe(row, site):
        nonlocal peak, peak_at
        mass = sum(abs(real) + abs(imag) for real, imag in row.values())
        if mass > peak:
            peak, peak_at = mass, (clock, site)

    @cache
    def shifted(exponents, shift):
        result = list(exponents)
        for stage in shift:
            result[stage - 1] += 1
        return tuple(result)

    def term(row, ar=1, ai=0, denominator=1, phase=0, shift=()):
        nonlocal checks
        out = {}
        for (role, q, powers), (x, y) in row.items():
            real, imag = ar * x - ai * y, ar * y + ai * x
            if denominator != 1:
                real, imag = exact_div(real, denominator), exact_div(imag, denominator)
                checks += 1
            if real or imag:
                key = (role, (q + phase) % 4, shifted(powers, shift) if shift else powers)
                out[key] = (real, imag)
        observe(out, "scaled separate term")
        return out

    def add(a, b):
        out = a.copy()
        for key, (u, v) in b.items():
            x, y = out.get(key, (0, 0))
            if x + u or y + v:
                out[key] = (x + u, y + v)
            else:
                out.pop(key, None)
        observe(out, "stored sum")
        return out

    for clock, event in enumerate(caller["events"]):
        kind = event[0]
        if kind == "J":
            _, stage, (x, y, u, v), (a, b, alpha, beta) = event
            require(stage == len(calls) + 1, "chronological joint occurrences")
            require(Fraction(alpha) == -1 and Fraction(beta) == Fraction(1, 2),
                    "literal joint coefficients")
            require(len({x, y, u, v}) == 4 and {x, y, u, v} <= role_sets["A"]
                    and a != b and {a, b} <= role_sets["B"], "joint owner alias")
            calls.append(stage)
            rows[y] = add(rows[y], term(rows[x], phase=-1))
            rows[u] = add(rows[u], term(rows[v], -1, phase=1))
            first, second = rows[a], rows[b]
            rows[a] = add(first, term(second, -1, phase=1))
            rows[b] = add(term(second, denominator=2),
                          term(first, denominator=2, phase=-1))
            for role in (x, y, u, v, a, b):
                rows[role] = term(rows[role], shift=(stage,))
            continue

        _, op, role, *args = event
        require(kind in role_sets and role in role_sets[kind], "caller target owner")
        replicas = len(types[kind]["ports"])
        uses[op] += replicas
        if op in {"ADD", "SWAP", "QUERY"}:
            require(args[0] in role_sets[kind] and args[0] != role, "caller donor owner")
        if op == "SWAP":
            other, = args
            rows[role], rows[other] = rows[other], rows[role]
        elif op == "QUERY":
            donor, sign = args
            require(sign in (-1, 1), "caller query orientation")
            rows[role] = add(rows[role], term(rows[donor], phase=sign))
            paid[1] += replicas
        elif op in {"ADD", "SCALE"}:
            factor = Fraction(args[-1])
            donor = args[0] if op == "ADD" else role
            contribution = term(rows[donor], factor.numerator, denominator=factor.denominator)
            rows[role] = add(rows[role], contribution) if op == "ADD" else contribution
        elif op == "LAMBDA":
            sign, = args
            require(sign in (-1, 1), "caller LAMBDA sign")
            old = rows[role]
            rows[role] = add(term(old, 1, sign, 2), term(old, 1, -sign, 2, phase=2))
        else:
            require(op in {"IDLE_ONE", "IDLE_ODD"}, "known caller operation")
            block = tuple(args[0])
            require(block and len(block) == len(set(block))
                    and all(1 <= k <= stages for k in block), "whole idle stage subset")
            if op == "IDLE_ODD":
                require(len(args) == 2 and len(block) == 1 and args[1] == -1,
                        "literal signed rank-nine child")
            else:
                require(len(args) == 1, "literal unit idle")
            phase = args[1] if op == "IDLE_ODD" else 0
            rows[role] = term(rows[role], phase=phase, shift=block)
            paid[8 * len(block) + phase % 2] += replicas

    require(calls == list(range(1, stages + 1)), "all 16 native invocations")
    for spec in types.values():
        require(len(spec["diagonal"]) == spec["roles"], "complete diagonal")
        for off, (phase, coefficient_phase, *powers) in enumerate(spec["diagonal"]):
            role = spec["offset"] + off
            require(phase in (-1, 0, 1) and coefficient_phase == 0 and len(powers) == stages
                    and set(powers) <= {0, 1} and any(powers), "positive whole root target")
            require(rows[role] == {(role, phase % 4, tuple(powers)): (unit, 0)},
                    "exact signed root endpoint")
            targets[8 * sum(powers) + phase % 2] += len(spec["ports"])
    return {
        "fixed_caller_paid": dict(paid),
        "fixed_root_targets": dict(targets),
        "uses": dict(uses),
        "calls": stages,
        "roles": len(rows),
        "root_owners": sum(targets.values()),
        "dyadic_height": dyadic_height,
        "odd_scale": odd_scale,
        "peak_scaled_mass": str(Fraction(peak, 1 << dyadic_height)),
        "peak_witness": peak_at,
        "exact_preproduct_divisions": checks,
    }
