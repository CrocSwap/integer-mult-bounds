#!/usr/bin/env python3
"""Directed rational price and interval proof for the joint funding envelope.

This is a research aid, not a compiler, source admission or kappa proposal.
No floating-point operation influences an interval or sign decision.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from collections import Counter
import json

PIN = "86f71ccbc923db5d7a6753aa971c3a9c8a572680534498ed17be072cfa2aae6b"
DEN = 10**50


def need(ok, why):
    if not ok:
        raise ValueError(why)


def down(x):
    return Q((x.numerator * DEN) // x.denominator, DEN)


def up(x):
    return -down(-x)


def log_series(x, terms=64):
    """For 1 <= x <= 2, positive atanh series and a geometric tail bound."""
    need(1 <= x <= 2, "log range reduction")
    z = (x-1)/(x+1)
    z2, power, s = z*z, z, Q(0)
    for j in range(terms):
        s += 2*power/(2*j+1)
        power *= z2
    # Remaining denominators are >=2*terms+1.
    error = 2*power / ((2*terms+1)*(1-z2))
    return down(s), up(s+error)


@lru_cache(None)
def log_interval(r):
    need(isinstance(r, int) and r >= 1, "positive integral rank")
    a = r.bit_length()-1
    lo2, hi2 = log_series(Q(2))
    lo, hi = log_series(Q(r, 1 << a))
    return down(a*lo2+lo), up(a*hi2+hi)


def exponential_minus(x, degree):
    """Finite Taylor polynomial; odd lower and even upper for x>=0."""
    need(x >= 0, "nonnegative exponential argument")
    term = total = Q(1)
    for k in range(1, degree+1):
        term *= -x/k
        total += term
    return total


@lru_cache(None)
def price(r, kappa):
    if r == 0:
        return Q(0), Q(0)
    need(1 <= r <= 137 and 0 <= kappa <= Q(1, 100), "declared pricing domain")
    lo, hi = log_interval(r)
    # exp(-x) decreases. Taylor's signed remainder bounds hold for all x>=0.
    low = r*exponential_minus(kappa*hi, 35)
    high = r*exponential_minus(kappa*lo, 36)
    return down(low), up(high)


def moment(signed, kappa):
    lo = hi = Q(0)
    for r, count in signed.items():
        a, b = price(int(r), kappa)
        lo += count*(a if count >= 0 else b)
        hi += count*(b if count >= 0 else a)
    return lo, hi


def display(interval):
    with localcontext() as ctx:
        ctx.prec = 35
        approximate = [str(Decimal(x.numerator)/Decimal(x.denominator)) for x in interval]
    return {"exact": list(map(str, interval)), "decimal_display_only": approximate}


def derivative(profile):
    """Enclose a profile derivative uniformly on 0<=kappa<=.01."""
    lo = hi = Q(0)
    for r, n in profile.items():
        a, b = log_interval(r)
        low, high = -b*r, -a*price(r, Q(1, 100))[0]
        lo += n*(low if n >= 0 else high)
        hi += n*(high if n >= 0 else low)
    return lo, hi


def reconstruct_invoice(replay, caller_path, invoice_path):
    raw = caller_path.read_bytes()
    need(sha256(raw).hexdigest() ==
         "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc", "exact caller bytes")
    caller = json.loads(raw)
    calls = sum(e[0] == "J" for e in caller["events"])
    need(calls == caller["stages"] == 17, "actual signed seventeen calls")
    target, paid = Counter(), Counter()
    for item in caller["types"].values():
        ports = len(item["ports"])
        for diagonal in item["diagonal"]:
            target[1+8*sum(diagonal[2:])] += ports
    for event in caller["events"]:
        if event[0] == "J":
            continue
        ports = len(caller["types"][event[0]]["ports"])
        if event[1] == "QUERY":
            paid[1] += ports
        elif event[1] in ("IDLE_ONE", "IDLE_ODD"):
            paid[8*len(event[3])+int(event[1] == "IDLE_ODD")] += ports
    for rank in replay["helper_target_ranks"].values():
        target[rank] += calls
    word = replay["word"]
    for event in word["program"]:
        if event[0] == "MOVE":
            paid[abs(len(word["frames"][event[2]])-len(word["frames"][event[3]]))] += calls
    raw = invoice_path.read_bytes()
    need(sha256(raw).hexdigest() == PIN, "exact complete invoice bytes")
    invoice = json.loads(raw)
    payload = sha256(json.dumps(word, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    need(payload == invoice["new_native"], "invoice/native payload binding")
    need(target == Counter({int(r): n for r, n in invoice["after"]["T"].items()}), "reconstructed complete productive invoice")
    need(paid == Counter({int(r): n for r, n in invoice["after"]["P"].items()}), "reconstructed complete paid invoice")
    base = {r: target[r]-paid[r] for r in target.keys() | paid.keys() if target[r] != paid[r]}
    need((sum(target.values()), sum(paid.values()), sum(r*n for r, n in base.items()))
         == (22461, 110519, 1424), "complete invoice counts and rank surplus")
    return base, calls, {"target": dict(sorted(target.items())), "paid": dict(sorted(paid.items())),
                        "native_calls": calls, "rank_surplus": 1424}


_COARSE_DENOMINATOR = 10**12
_COARSE_POWER = _COARSE_DENOMINATOR**1000
_COARSE_CERTIFICATES = {}


@lru_cache(None)
def coarse_price(r, index):
    """Integer-power certificate at kappa=index/1000; Decimal only seeds it."""
    need(1 <= r <= 137 and 10 <= index <= 1000, "coarse fixed-grid price domain")
    if r == 1 or index == 1000:
        return Q(1), Q(1)
    with localcontext() as ctx:
        ctx.prec = 70
        exponent = Decimal(1000-index)/Decimal(1000)
        seed = int(Decimal(r)**exponent * _COARSE_DENOMINATOR)
    a, b = seed-1, seed+1
    exact = r**(1000-index)*_COARSE_POWER
    need(a > 0 and a**1000 <= exact <= b**1000, "exact coarse integer-power bracket")
    _COARSE_CERTIFICATES[r, index] = [a, b]
    return Q(a, _COARSE_DENOMINATOR), Q(b, _COARSE_DENOMINATOR)


def coarse_cover(base, calls, cap):
    # Fixed rational grid: every bracket has exponent denominator1000.
    indices = [10, 11, 13, 17, 25, 33, 41, 56, 71, 102, 133, 257, 505, 1000]
    records = []
    for a, b in zip(indices, indices[1:]):
        upper = Q(calls*cap)
        for r, n in base.items():
            upper += n*(coarse_price(r, a)[1] if n > 0 else coarse_price(r, b)[0])
        need(upper < 0, "every coarse interval excludes a positive moment")
        records.append({"left": str(Q(a, 1000)), "right": str(Q(b, 1000)), "upper": str(upper)})
    need(records[0]["left"] == "1/100" and records[-1]["right"] == "1", "coarse complete endpoints")
    need(all(a["right"] == b["left"] for a, b in zip(records, records[1:])), "coarse cover has no gaps")
    certificate = [[r, k, ab] for (r, k), ab in sorted(_COARSE_CERTIFICATES.items())]
    return {"interval": ["1/100", "1"], "native_cap": cap,
            "partition": records, "integer_power_exponent": 1000,
            "integer_brackets": len(certificate),
            "integer_brackets_sha256": sha256(json.dumps(certificate, separators=(",", ":")).encode()).hexdigest(),
            "worst_upper": display((max(Q(x["upper"]) for x in records),)*2)}


def prove(replay, structure, local, caller_path, invoice_path):
    base, calls, invoice = reconstruct_invoice(replay, caller_path, invoice_path)
    need(local["zero_only_quarter_certificate"]["dependent_subsets_checked"] == 31, "zero-only quarter funding prerequisite")
    need(4**99 > 3**100, "near-linear rank-four analytic comparison")
    ceilings = {(39875, 39884): {5: 1, 1: 1, 6: -1},
                (42500,): {1: 1, 3: 1, 4: -1}, (41646,): {6: 1, 4: -1}}
    certificates = []
    total = Counter()
    components = local["eight_small_components"]+local["six_zero_prefix_profiles"]
    for component in components:
        ceiling = ceilings.get(tuple(component["cache_sites"]), {})
        total.update(ceiling)
        for subset in component["subsets"]:
            for case in subset["cases"]:
                accepted = []
                for ob in case["all_necessary_obligations"]:
                    diff = Counter({int(r): n for r, n in ob["signed_profile"].items()})
                    diff.subtract(ceiling)
                    diff = {r: n for r, n in diff.items() if n}
                    value0 = sum(r*n for r, n in diff.items())
                    slope_upper = derivative(diff)[1]
                    bound = value0+Q(1, 100)*max(Q(0), slope_upper)
                    if bound <= 0:
                        accepted.append({"witness": ob["witness"], "profile": dict(sorted(diff.items())),
                                         "zero_value": value0, "slope_upper": str(slope_upper), "bound": str(bound)})
                need(accepted, "uniform local upper profile on whole fine interval")
                certificates.append({"sites": component["cache_sites"], "mask": case["mask"],
                                     "new": case["newly_granted"], "proof": accepted[0]})
    need(len(certificates) == 473, "89 small plus384 six-zero uniform cases")
    total = {r: n for r, n in total.items() if n}
    need(total == {5: 1, 1: 2, 4: -2, 3: 1}, "telescoped native upper envelope")
    envelope = Counter(base)
    envelope.update({r: calls*n for r, n in total.items()})
    envelope = {r: n for r, n in envelope.items() if n}
    slope = derivative(envelope)
    need(slope[1] < 0, "strictly decreasing fine envelope")
    goal = moment(envelope, Q(19, 5000))
    need(goal[1] < -Q(252581, 10000), "complete0038 fine moment")
    crossing = Q("0.0037347911502843961"), Q("0.0037347911502843965")
    need(moment(envelope, crossing[0])[0] > 0 and moment(envelope, crossing[1])[1] < 0,
         "fine upper-envelope crossing bracket")
    rows = replay["mainfree_moves"]
    need(len(rows) == 468, "complete zero-row set")
    need(all(r["rank"] <= replay["helper_target_ranks"][h] for r in rows for h in r["row"]),
         "all independent zero subsets have support matching")
    zero_rank = structure["receipt"]["zero_move_rank"]
    need(zero_rank == 463, "zero-row nullity prerequisite")
    cap = (len(rows)-zero_rank)*max(r["rank"] for r in rows)+sum(s["target_rank"] for s in replay["sites"].values())
    need(cap == 72 and len(replay["sites"]) == 14, "coarse full native cap")
    return {"status": "PASS_COMPLETE_JOINT_POWER_ENVELOPES",
            "invoice": invoice, "baseline_signed_profile": dict(sorted(base.items())),
            "native_upper_profile": dict(sorted(total.items())),
            "full_upper_profile": dict(sorted(envelope.items())),
            "uniform_local_cases": len(certificates),
            "local_case_proofs_sha256": sha256(json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
            "fine_interval": ["0", "1/100"], "fine_derivative": display(slope),
            "full_at_0038": display(goal), "upper_envelope_crossing": display(crossing),
            "coarse": coarse_cover(base, calls, cap),
            "kappa_status": "No new kappa. This is an upper envelope, not a feasible supplier."}
