"""Replay the signed caller over the Gaussian group ring and price its actual entries."""
from collections import Counter
from fractions import Fraction
from functools import cache
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from network import main_roles, need, rational


def divided(value, denominator):
    quotient, remainder = divmod(value, denominator)
    need(remainder == 0, "caller grid remainder")
    return quotient


def caller_replay(caller, word):
    stages = caller["stages"]
    cs = 2025
    height = 9
    unit = cs << height
    zero = (0,) * stages
    rows = [{(r, 0, zero): (unit, 0)} for r in range(caller["roles"])]
    peak = unit
    checks = 0
    paid = Counter()
    targets = Counter()
    uses = Counter()
    stages_seen = []
    types = caller["types"]
    need(types["A"]["ports"] == word["hosted"]["Dports"] and sorted(types["A"]["ports"] + types["B"]["ports"]) == list(range(len(word["ports"]))), "port allocation")
    need(9 + 8 * stages == caller["ambient_rank"] <= 153, "caller geometry")
    role_sets = {name: set(range(ty["offset"], ty["offset"] + ty["roles"])) for name, ty in types.items()}
    need(role_sets["A"].isdisjoint(role_sets["B"]) and role_sets["A"] | role_sets["B"] == set(range(len(rows))), "type owners")

    @cache
    def shifted(exponents, shift):
        exponents = list(exponents)
        for k in shift:
            exponents[k - 1] += 1
        return tuple(exponents)

    def term(row, ar=1, ai=0, denominator=1, phase=0, shift=()):
        nonlocal peak, checks
        out = {}
        for (r, q, powers), (x, y) in row.items():
            u, v = ar * x - ai * y, ar * y + ai * x
            if denominator != 1:
                u, v = divided(u, denominator), divided(v, denominator)
                checks += 1
            out[r, (q + phase) % 4, shifted(powers, shift) if shift else powers] = (u, v)
        peak = max(peak, sum(abs(x) + abs(y) for x, y in out.values()))
        return out

    def plus(a, b):
        nonlocal peak
        out = a.copy()
        for k, (u, v) in b.items():
            x, y = out.get(k, (0, 0))
            if x + u or y + v:
                out[k] = (x + u, y + v)
            else:
                out.pop(k, None)
        peak = max(peak, sum(abs(x) + abs(y) for x, y in out.values()))
        return out

    for event in caller["events"]:
        ty = event[0]
        if ty == "J":
            _, stage, (x, y, u, v), (a, b, alpha, beta) = event
            need(stage == len(stages_seen) + 1 and alpha == "-1" and beta == "1/2" and types["A"]["alpha2"] == "-1", "joint coefficients")
            need(len({x, y, u, v}) == 4 and {x, y, u, v} <= role_sets["A"] and a != b and {a, b} <= role_sets["B"], "joint owner alias")
            stages_seen.append(stage)
            rows[y] = plus(rows[y], term(rows[x], phase=-1))
            rows[u] = plus(rows[u], term(rows[v], -1, phase=1))
            r, s = rows[a], rows[b]
            rows[a] = plus(r, term(s, -1, phase=1))
            rows[b] = plus(term(s, denominator=2), term(r, denominator=2, phase=-1))
            for role in (x, y, u, v, a, b):
                rows[role] = term(rows[role], shift=(stage,))
            continue
        _, op, r, *args = event
        need(r in role_sets[ty], "local caller owner")
        count = len(types[ty]["ports"])
        uses[op] += count
        if op in ("ADD", "SWAP", "QUERY"):
            need(args[0] in role_sets[ty] and args[0] != r, "caller donor")
        if op == "SWAP":
            s = args[0]
            rows[r], rows[s] = rows[s], rows[r]
        elif op == "QUERY":
            s, q = args
            need(q in (-1, 1), "query sign")
            rows[r] = plus(rows[r], term(rows[s], phase=q))
            paid[1] += count
        elif op in ("SCALE", "ADD"):
            amount = rational(args[-1])
            if op == "SCALE":
                rows[r] = term(rows[r], amount.numerator, denominator=amount.denominator)
            else:
                rows[r] = plus(rows[r], term(rows[args[0]], amount.numerator, denominator=amount.denominator))
        elif op == "LAMBDA":
            sign = args[0]
            need(sign in (-1, 1), "lambda sign")
            original = rows[r]
            rows[r] = plus(term(original, 1, sign, 2), term(original, 1, -sign, 2, phase=2))
        else:
            need(op in ("IDLE_ONE", "IDLE_ODD"), "caller operation")
            block = tuple(args[0])
            need(len(set(block)) == len(block) and all(1 <= k <= stages for k in block), "idle stages")
            phase = args[1] if op == "IDLE_ODD" else 0
            need(op != "IDLE_ODD" or phase in (-1, 1), "idle sign")
            rows[r] = term(rows[r], phase=phase, shift=block)
            paid[8 * len(block) + phase % 2] += count
    need(stages_seen == list(range(1, stages + 1)), "all native calls")
    for ty in types.values():
        for offset, (phase, coefficient_phase, *powers) in enumerate(ty["diagonal"]):
            r = ty["offset"] + offset
            need(coefficient_phase == 0 and len(powers) == stages and set(powers) <= {0, 1}, "positive root boundary")
            need(rows[r] == {(r, phase % 4, tuple(powers)): (unit, 0)}, "complete signed caller endpoint")
            rank = 8 * sum(powers) + phase % 2
            need(rank > 0 and any(powers), "empty root credit")
            targets[rank] += len(ty["ports"])
    return dict(paid=dict(paid), targets=dict(targets), uses=dict(uses), calls=stages,
                dyadic_height=height, odd_scale=cs, peak_scaled_mass=str(Fraction(peak, 2**height)),
                exact_preproduct_divisions=checks, root_owners=sum(targets.values()),
                fresh_helpers=stages * (word["public"] - len(main_roles(word))))
