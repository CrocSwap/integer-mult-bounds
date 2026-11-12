"""Certify the target-moment bound for redistributed paired BIT LOCALs."""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path

TARGET = Fraction("0.0040075385047236")
SCALE = 10**22
PINS = {
    "EFREE-CALLER.json.gz": "757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b",
    "EFREE-RESULT.json": "a46b6c6040f75184cab5467656811ad988c216e3bc8e44d595a5015b6e49620b",
    "retained/inputs/independent_interval.py": "9293f567aa4afd9b4e618f1cddd3cf66eea51c5e194e3c578e7a8f4db6e04a57",
}


def read(root, path):
    raw = (root / path).read_bytes()
    if sha256(raw).hexdigest() != PINS[path]:
        raise ValueError(f"SHA-256 mismatch: {path}")
    return raw


def water_fill(caps, minimum, total):
    demand = list(minimum)
    increments = sorted((depth, j) for j, cap in enumerate(caps)
                        for depth in range(demand[j], cap))
    needed = total - sum(demand)
    if not 0 <= needed <= len(increments):
        return None
    for _, j in increments[:needed]:
        demand[j] += 1
    return demand


def packed(demand, body, ports):
    return Counter({r: c*ports for r, c in Counter(
        body * sum(x >= k for x in demand) for k in range(1, max(demand, default=0)+1)
    ).items()})


def run(root):
    caller = json.loads(gzip.decompress(read(root, "EFREE-CALLER.json.gz")))
    receipt = json.loads(read(root, "EFREE-RESULT.json"))
    relative = "retained/inputs/independent_interval.py"
    read(root, relative)
    spec = spec_from_file_location("retained_interval", root / relative)
    price = module_from_spec(spec)
    spec.loader.exec_module(price)

    def fixed(text):
        value = Fraction(text)*SCALE
        assert value.denominator == 1
        return value.numerator

    def show(value):
        sign = "-" if value < 0 else ""
        whole, tail = divmod(abs(value), SCALE)
        return f"{sign}{whole}.{tail:022d}"

    powers = {}

    def moment(hist, side):
        total = 0
        for rank, count in hist.items():
            rank = int(rank)
            if rank not in powers:
                b = price.bounds_text(price.power(rank, 1-TARGET))
                powers[rank] = fixed(b["lower"]), fixed(b["upper"])
            total += powers[rank][side]*count
        return total

    roles, body, ports = (caller[k] for k in ("roles", "body_rank", "ports"))
    assert (roles, body, ports) == (38, 7, 111)
    stages = range(1, 19)
    arms = (range(1, 10), range(10, 19))
    target = {s: {i for i, row in enumerate(caller["diagonal"]) if s in row["stages"]} for s in stages}
    assert all(row["q"] == 1 for row in caller["diagonal"])
    assert all(target[s] & target[t] == {0,19} for s in arms[0] for t in arms[1])
    caps = [sorted(len(target[s])//2 for s in arm) for arm in arms]
    assert caps[0] == caps[1] == list(range(2,11))
    assert all(len(target[s]) % 2 == 0 for s in stages)
    events = caller["events"]
    assert Counter(e[1] for e in events if e[0] == "LOCAL") == {s:2 for s in stages}
    assert sum(e[0] == "QUERY" for e in events) == 4
    idle = Counter(body*len(e[2]) for e in events if e[0] == "IDLE_ONE")
    root_idle = Counter({r:c*ports for r,c in idle.items()})
    native_p = Counter({int(r):c for r,c in receipt["native_paid"].items()})
    native_t = Counter({int(r):c for r,c in receipt["native_helpers"].items()})
    root_t = Counter(1+body*len(row["stages"]) for row in caller["diagonal"])
    root_t = Counter({r:c*ports for r,c in root_t.items()})
    full_p = Counter({r:36*c for r,c in native_p.items()}) + root_idle + Counter({1:4*ports})
    full_t = Counter({r:36*c for r,c in native_t.items()}) + root_t
    assert full_p == Counter({int(r):c for r,c in receipt["paid"].items()})
    assert full_t == Counter({int(r):c for r,c in receipt["targets"].items()})

    native_debit = moment(native_p,0)-moment(native_t,1)
    native_debit_upper = moment(native_p,1)-moment(native_t,0)
    root_credit = moment(root_t,1)
    cross_credit = 18*(moment({7:2*ports},1)-moment({14:ports},0))

    def upper(n, q, idle_debit, cross):
        return root_credit - n*native_debit - q*ports*SCALE - idle_debit + cross

    def rebate(incidences):
        doubled = moment({7:2*ports},1)-moment({14:ports},0)
        return (incidences*doubled+1)//2

    baseline = upper(36,4,moment(root_idle,0),0)
    arm_step = moment({63:ports},0)-moment({56:ports},1)
    penalty = ports*SCALE + 2*arm_step - native_debit_upper
    assert penalty > rebate(1) > 0
    original_degrees = [len(target[s])-4 for s in stages]
    assert packed(original_degrees[:9],body,ports)+packed(original_degrees[9:],body,ports) == root_idle
    increased = [x+2 for x in original_degrees]
    assert packed(increased[:9],body,ports)+packed(increased[9:],body,ports) == (
        root_idle + Counter({63:4*ports})
    )
    lower_multiplicity = {
        "minimum_queries_with_two_local_stage": baseline+rebate(27),
        "at_least_one_extra_query": baseline+rebate(36)-ports*SCALE,
        "no_two_local_stage": (
            baseline+18*native_debit_upper+rebate(36)
            -17*ports*SCALE-moment({63:4*ports},0)
        ),
    }
    assert max(lower_multiplicity.values()) < 0

    toy_caps, toy_min = (1,3,4,4), (0,0,2,1)
    toy = list(product(*(range(lo,hi+1) for lo,hi in zip(toy_min,toy_caps,strict=True))))
    for total in range(sum(toy_min),sum(toy_caps)+1):
        best = water_fill(toy_caps,toy_min,total)
        for level in range(1,max(toy_caps)+1):
            assert sum(min(level,d) for d in best) == max(
                sum(min(level,d) for d in candidate) for candidate in toy if sum(candidate)==total
            )

    def arm_table(cap):
        table = {}
        for biggest in range(max(cap)+1):
            minimum = [max(0,c-biggest) for c in cap]
            for n in range(biggest,sum(cap)+1):
                demand = water_fill(cap,minimum,sum(cap)-n)
                if demand is not None:
                    table[biggest,n] = moment(packed([2*x for x in demand],body,ports),0)
        return table

    left, right = map(arm_table, caps)
    by_total = {}
    checked = 0
    for (a,n), v in left.items():
        for (b,m), w in right.items():
            if max(a,b) < 3:
                continue
            checked += 1
            q = max(0,39-n-m,38-n-m+max(a,b,a+b-2))
            row = (upper(n+m,q,v+w,cross_credit),a,b,n,m,q)
            if n+m not in by_total or row > by_total[n+m]:
                by_total[n+m] = row
    assert checked <= 160000 and max(by_total.values())[0] < 0

    # Non-saturation: one additional stage incidence, with every mask
    # allowed to occupy all 18 stages and arbitrary individual degrees.
    total_cap = sum(map(sum,caps))
    unsaturated = []
    for n in range(total_cap+1):
        count = 2*(total_cap-n)+1
        full, rem = divmod(count,18)
        hist = Counter({126:ports*full})
        if rem:
            hist[7*rem] = ports
        unsaturated.append((upper(n,max(0,39-n),moment(hist,0),0),n))
    assert max(unsaturated)[0] < 0
    excess_native_count_upper = upper(total_cap+1,0,0,0)
    assert native_debit > 0 and excess_native_count_upper < 0

    # Recount all one-slot reallocations. For two slots the whole-family
    # bound above already covers all changed multiplicities.
    d = original_degrees
    cases = []
    for src in range(18):
        for dst in range(18):
            if src == dst or d[dst] < 2:
                continue
            moved = d[:]
            moved[src] += 2
            moved[dst] -= 2
            tariff = moment(packed(moved[:9],body,ports)+packed(moved[9:],body,ports),0)
            cases.append((upper(36,5,tariff,cross_credit),src+1,dst+1))
    assert max(cases)[0] < 0
    return dict(target=str(TARGET), dependencies=PINS, opposite_stage_pairs=81,
                native_counts_considered=total_cap+1, per_arm_tables=[len(left),len(right)],
                saturated_higher_multiplicity_price_cells=checked,
                saturated_higher_multiplicity_maximum=show(max(by_total.values())[0]),
                saturated_maximizing_cell=list(max(by_total.values())[1:]),
                max_for_36=show(by_total[36][0]),
                unsaturated_maximum=show(max(unsaturated)[0]),
                unsaturated_maximizing_locals=max(unsaturated)[1],
                ordered_one_slot_transfers=len(cases),
                one_slot_upper=show(max(cases)[0]),
                best_one_slot=list(max(cases)[1:]),
                water_fill_toy_controls=len(toy),
                above_saturated_native_cap_maximum=show(excess_native_count_upper),
                lower_multiplicity_saturated={name:show(value)
                                              for name,value in lower_multiplicity.items()})


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Use CPython 3.12 with assertions enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", nargs="?", type=Path, default=Path(__file__).resolve().parent.parent / "paired-query-only-bit")
    receipt = json.dumps(run(parser.parse_args().package), indent=2, sort_keys=True) + "\n"
    expected = Path(__file__).resolve().with_name("RECEIPT.json").read_bytes()
    if receipt.encode() != expected:
        raise ValueError("exact paid-moment receipt mismatch")
    print("PASS_BIT_PAIRED_SCHEDULE_BOUND")
