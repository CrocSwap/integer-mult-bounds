"""Recount the finite ordinary-work bills of the paired words in PR 7633.

Mihir Srivastava with substantial OpenAI Codex assistance. Apache-2.0.
The tariff, words and signed caller are credited in README.md and SOURCES.json.
"""

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from hashlib import sha256
from math import gcd, prod
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
ROUTE_UNIT = 1000
ORDINARY_LIMIT = 10**9
NATIVE_GRID = 1125 << 25


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compare(actual, expected, path):
    if isinstance(actual, dict) and isinstance(expected, dict):
        require(actual.keys() == expected.keys(), f"{path} has different fields")
        for key in actual:
            compare(actual[key], expected[key], f"{path}.{key}")
    else:
        require(actual == expected, f"{path}: computed {actual!r}, published {expected!r}")


def read_inputs():
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    result = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        name = Path(row["path"]).name
        raw = (HERE / "data" / name).read_bytes()
        require(sha256(raw).hexdigest() == row["sha256"], f"input digest differs for {name}")
        result[name] = json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    return result


@cache
def coefficient(literal):
    return Fraction(literal)


def scalar_units(op, q):
    numerator = abs(q.numerator)
    bits = numerator.bit_length() + q.denominator.bit_length() + 1
    if op in ("ADD", "COPY"):
        bits += numerator.bit_count()
    return 4 * bits


@dataclass
class NativeCounts:
    events: Counter
    scalar_units: Counter
    odd_divisions: Counter
    common_denominator: int
    products: int


def count_word(word, grid=NATIVE_GRID):
    # Each sparse row acts on the independent public input coordinates.
    public = word["public"]
    rows = {i: {i: grid} for i in range(public)}
    events, charges, odd = Counter(), Counter(), Counter()
    common = grid
    products = 0
    for clock, event in enumerate(word["program"]):
        op, dest = event[:2]
        events[op] += 1
        if op == "INIT":
            require(public <= dest < public + word["owned_fields"] and dest not in rows,
                    f"bad private allocation at {clock}")
            rows[dest] = {}
        elif op == "CLEAR":
            require(dest >= public and dest in rows, f"bad private return at {clock}")
            del rows[dest]
        elif op == "MOVE":
            require(dest in rows and event[2] != event[3], f"empty MOVE at {clock}")
            # A chart change preserves the normalized scalar row.
        else:
            require(op in ("ADD", "COPY", "SCALE"), f"unknown native operation {op}")
            source = dest if op == "SCALE" else event[2]
            require(op == "SCALE" or source != dest, f"aliased scalar at {clock}")
            require(dest in rows and source in rows, f"inactive scalar role at {clock}")
            q = coefficient(event[-2])
            charges[op] += scalar_units(op, q)
            denominator = q.denominator
            if denominator & (denominator - 1):
                odd[op] += 1
            # Check each product before cancellation. SCALE and COPY replace a row.
            out = rows[dest] if op == "ADD" else {}
            for column, value in rows[source].items():
                term, remainder = divmod(value * q.numerator, denominator)
                if remainder:
                    raise ValueError(f"nonintegral product at event {clock}, input {column}")
                if common > 1:
                    common = gcd(common, term)
                updated = out.get(column, 0) + term
                if updated:
                    out[column] = updated
                else:
                    out.pop(column, None)
            products += len(rows[source])
            rows[dest] = out
    require(rows.keys() == set(range(public)), "unreturned private label")
    return NativeCounts(events, charges, odd, grid // common, products)


def body_axes(stages):
    # Axis zero carries the sign. The eight axes of stage j start at 1 + 8*j.
    return {1 + 8 * stage + offset for stage in stages for offset in range(8)}


def swaps_to_prefix(axes):
    return sum(axis >= len(axes) for axis in axes)


def count_caller(caller):
    stages = [e[1] for e in caller["events"] if e[0] == "J"]
    require(stages == list(range(1, caller["stages"] + 1)), "joint stage sequence")
    items = {}
    lambda_uses = surcharge = 0
    for name, group in caller["types"].items():
        ports = len(group["ports"])
        roles = len(group["diagonal"])
        require(roles == group["roles"], "caller role count")
        events = [e for e in caller["events"] if e[0] == name]
        per_port = Counter(e[1] for e in events)
        idle_swaps = query_steps = output_steps = 0
        for _, op, _, *args in events:
            if op == "IDLE_ONE":
                idle_swaps += swaps_to_prefix(body_axes(args[0]))
            elif op == "QUERY":
                query_steps += 2 + int(args[1] == -1)
            elif op in ("ADD", "SCALE"):
                surcharge += ports * scalar_units(op, coefficient(args[-1]))
            else:
                require(op in ("IDLE_ODD", "LAMBDA", "SWAP"), f"unknown caller operation {op}")
        for phase, reserved, *mask in group["diagonal"]:
            require(reserved == 0 and len(mask) == len(stages), "output route description")
            axes = body_axes(stage for stage, used in zip(stages, mask) if used)
            if phase:
                axes.add(0)
            output_steps += 2 * swaps_to_prefix(axes) + 2 * int(phase != 0) + int(phase == -1)
        lambda_uses += ports * per_port["LAMBDA"]
        items[name] = {
            "envelope": 32 * roles * ports * (len(stages) + len(events)),
            "field_boundary": 26 * roles * ports,
            "thin": 16 * ports * per_port["QUERY"],
            "output_routes": ROUTE_UNIT * ports * output_steps,
            "idle_routes": ROUTE_UNIT * ports * 2 * idle_swaps,
            "query_routes": ROUTE_UNIT * ports * query_steps,
            "fused_routes": 36_500 * ports * per_port["IDLE_ODD"],
        }
    return items, lambda_uses, surcharge


def caller_conversions(caller, grid):
    # The signed caller uses a separate tariff for scaling all raw owners in and out.
    scale = prod(p**k for p, k in zip(grid["prime_order"], grid["grid_exponents"], strict=True)
                 if p != 2)
    require(scale == int(grid["caller_odd_scale"]), "caller odd scale disagrees with exponents")
    owners = sum(t["roles"] * len(t["ports"]) for t in caller["types"].values())
    return 2 * owners * 4 * (scale.bit_length() + 1 + scale.bit_count())


def price_word(word, native, caller, items, lambda_uses):
    calls = caller["stages"]
    public = word["public"]
    hosted = word["hosted"]
    live = word["live"]
    ports = len(live)
    second = len(hosted["Dports"])
    require(len(word["ports"]) == ports and len(word["initial"]) == public, "native dimensions")
    require(caller["types"]["A"]["ports"] == hosted["Dports"] and
            sorted(hosted["Dports"] + caller["types"]["B"]["ports"]) == list(range(ports)),
            "caller and native port inventories differ")
    main = live + [x + 112 for x in live] + hosted["X2"] + hosted["Y2"]
    require(len(hosted["X2"]) == len(hosted["Y2"]) == second and
            len(set(main)) == len(main) and set(main) <= set(range(public)), "main role inventory")
    route_items = {
        "moves": native.events["MOVE"],
        "helper_boundary": 2 * (public - len(main)),
        "first_main_boundary": 2 * ports,
        "second_main_boundary": 2 * second,
        "first_main_adapter": 4 * ports,
        "second_main_adapter": 4 * second,
        "owned_lifetime": 4 * native.events["INIT"],
    }
    routing = ROUTE_UNIT * sum(route_items.values())
    scalar = native.scalar_units.total()
    caller_total = sum(sum(group.values()) for group in items.values())
    raw = calls * (routing + scalar) + caller_total
    denominator = native.common_denominator
    odd_scale = denominator // (denominator & -denominator)
    conversion_pair = sum(scalar_units("SCALE", q) for q in (Fraction(odd_scale), Fraction(1, odd_scale)))
    conversions = calls * public * conversion_pair
    second_charge = ROUTE_UNIT * lambda_uses
    subtotal = raw + conversions + second_charge
    return {
        "route_items": route_items,
        "routing": routing,
        "scalar_upper": scalar,
        "odd_divisions": dict(native.odd_divisions),
        "init_clear_allowance": 2 * (native.events["INIT"] + native.events["CLEAR"]),
        "caller_items": items,
        "caller_total": caller_total,
        "raw_upper": raw,
        "per_input_conversion": conversions,
        "lambda_second_charge": second_charge,
        "lambda_paid_rank1_would_reduce_S_by": lambda_uses,
        "conservative_total": subtotal,
        "margin_to_billion": ORDINARY_LIMIT - subtotal,
    }


def lifetime_budget(total, lifetimes, tariff):
    fixed = total - tariff * lifetimes
    maximum = (ORDINARY_LIMIT - 1 - fixed) // lifetimes
    at_max = fixed + lifetimes * maximum
    return {"fixed": fixed, "lifetimes": lifetimes, "max_integer_tariff": maximum,
            "total_at_max": at_max, "total_at_next": at_max + lifetimes}


def controls(word, caller, published):
    # An undersized grid must fail on a literal product, even if a later ADD cancels it.
    try:
        count_word(word, NATIVE_GRID // 3)
    except ValueError as error:
        require("nonintegral product at event" in str(error), str(error))
        grid_failure = str(error)
    else:
        raise ValueError("undersized odd grid accepted")

    # Changing just the orientation of one A query saves one route per port.
    mutant = deepcopy(caller)
    query = next(e for e in mutant["events"] if e[:2] == ["A", "QUERY"] and e[4] == -1)
    query[4] = 1
    changed, _, _ = count_caller(mutant)
    baseline = published["candidate"]["caller_items"]
    loss = baseline["A"]["query_routes"] - changed["A"]["query_routes"]
    require(loss == ROUTE_UNIT * len(caller["types"]["A"]["ports"]), "query sign control")

    # Keep the total and the route sum identical while misclassifying a full lifetime.
    changed = deepcopy(published["candidate"])
    changed["route_items"]["owned_lifetime"] -= 4
    changed["route_items"]["moves"] += 4
    try:
        compare(changed, published["candidate"], "candidate")
    except ValueError as error:
        require("candidate.route_items." in str(error), str(error))
    else:
        raise ValueError("compensating ledger errors accepted")
    return {"short_grid_rejection": grid_failure, "query_sign_units": loss,
            "same_total_misclassification": "rejected"}


def main():
    inputs = read_inputs()
    caller = inputs["7113-caller.json"]
    grid = inputs["7113-grid.json"]
    application = inputs["7633-application.json"]
    contract = inputs["7633-common-u.json"]
    caller_digest = sha256((HERE / "data/7113-caller.json").read_bytes()).hexdigest()
    require(caller_digest == grid["caller_sha256"] == application["caller_sha256"]
            == contract["caller_sha256"], "caller binding")
    reference = inputs["7633-matched-ordinary.json"]
    items, lambda_uses, surcharge = count_caller(caller)
    conversions = caller_conversions(caller, grid)
    compare(surcharge, reference["caller_scalar_surcharge"], "caller_scalar_surcharge")
    compare(conversions, reference["caller_odd_conversions"], "caller_odd_conversions")
    evidence = {}
    for side, name in (("source", "7631-word.json.gz"), ("candidate", "7633-word.json.gz")):
        word = inputs[name]
        canonical = json.dumps(word, separators=(",", ":"), sort_keys=True).encode()
        digest = sha256(canonical).hexdigest()
        require(digest == contract[side + "_canonical_sha256"], f"{side} U word binding")
        tally = count_word(word)
        bill = price_word(word, tally, caller, items, lambda_uses)
        compare(bill, reference[side], side)
        lifetimes = tally.events["INIT"]
        tariff = contract["ordinary_units_per_lifetime_pair"]
        compare(lifetimes, contract[side + "_lifetimes"], side + " U lifetimes")
        compare(ROUTE_UNIT * bill["route_items"]["owned_lifetime"], tariff * lifetimes,
                side + " U ordinary charge")
        total = bill["conservative_total"] + surcharge + conversions
        compare(total, reference[side + "_total"], side + "_total")
        require(total < ORDINARY_LIMIT, f"{side} exceeds ordinary budget")
        if side == "candidate":
            require(digest == application["native_canonical_sha256"], "application word binding")
            complete = dict(bill, all_caller_scalar_surcharge=surcharge,
                            charged_caller_odd_conversions=conversions,
                            conservative_total=total, margin_to_billion=ORDINARY_LIMIT - total)
            compare(complete, application["source_unit_ordinary"], "application.source_unit_ordinary")
        evidence[side] = {
            "events": dict(tally.events), "scalar_units_per_call": dict(tally.scalar_units),
            "grid_products": tally.products, "least_grid_denominator": tally.common_denominator,
            "ordinary_units": total, "margin": ORDINARY_LIMIT - total,
            "tariff_test": lifetime_budget(total, lifetimes * caller["stages"], tariff),
        }

    evidence["controls"] = controls(inputs["7633-word.json.gz"], caller, reference)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    print("PASS paired ordinary bills under the declared tariffs")


if __name__ == "__main__":
    main()
