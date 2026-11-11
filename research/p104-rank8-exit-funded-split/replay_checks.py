# SPDX-License-Identifier: Apache-2.0
"""Independent literal interval controls and fixed-profile packing relaxation."""

from collections import Counter
from fractions import Fraction as Q


def require(condition, message):
    if not condition:
        raise ValueError(message)


def touches(event, role):
    return event[1] == role or (event[0] in ("ADD", "COPY") and event[2] == role)


def stationary(word, role, frame, lo, hi):
    events = word["program"]
    require(0 <= lo <= hi <= len(events), "Well-ordered original cuts")
    require(lo == 0 or (events[lo-1][0] != "MOVE" and touches(events[lo-1], role)),
            "Stationary interval starts at a literal contact boundary")
    require(hi == len(events) or (events[hi][0] != "MOVE" and touches(events[hi], role)),
            "Stationary interval ends at a literal contact boundary")
    current = word["initial"][role] if role < word["public"] else None
    for e in events[:lo]:
        if e[1] != role:
            continue
        if e[0] == "INIT":
            current = e[2]
        elif e[0] == "CLEAR":
            current = None
        elif e[0] == "MOVE":
            current = e[3]
    require(current is not None and current == frame, "Live literal stationary chart")
    require(not any(touches(e, role) for e in events[lo:hi]),
            "Whole contact interval has no MOVE or intervening contact")


def rejected(check):
    try:
        check()
    except ValueError:
        return True
    raise ValueError("Malformed stationary access accepted")


def check_stationary(word, hit):
    retained = []
    for name, endpoint in (("gathers", 0), ("injections", 1)):
        for x in hit[name]:
            if "stationary_interval" not in x:
                continue
            lo, hi = x["stationary_interval"]
            require("path" not in x and "paid_path" not in x and x["cut"] == (lo, hi)[endpoint],
                    "Literal stationary access without retiming")
            require(Q(x["coefficient"]) and x["frame"] == hit["frame"], "Nonzero cocharted access")
            stationary(word, x["role"], x["frame"], lo, hi)
            retained.append(dict(kind=name, role=x["role"], cut=x["cut"], interval=[lo, hi]))
    require(retained, "At least one genuine stationary coefficient")
    a = retained[0]
    toy = dict(public=1, initial=[0], program=[
        ["INIT", 1, 0], ["MOVE", 1, 0, 1, True],
        ["ADD", 1, 0, "1", 1], ["CLEAR", 1, 1],
    ])
    return dict(accesses=retained,
                wrong_chart=rejected(lambda: stationary(word, a["role"], -1, *a["interval"])),
                inside_moving_epoch=rejected(lambda: stationary(toy, 1, 0, 1, 2)),
                after_clear=rejected(lambda: stationary(toy, 1, 1, 4, 4)))


def packing(invoice, native, g, claim):
    """Fixed T, 17 fixed native words, and fixed ambient-145 remainder mass."""
    cap = 145
    paid = Counter(invoice["P"])
    local = Counter({r: 17*count for r, count in native["paid"].items()})
    paid.subtract(local)
    require(all(n >= 0 and r <= cap for r, n in paid.items()), "Exact nonnegative paid remainder")
    mass = sum(r*n for r, n in paid.items())
    relaxed = Counter(invoice["T"])
    relaxed.subtract(local)
    relaxed[cap] -= Q(mass, cap)

    # r^(1-x) log(r) is positive. Bound each signed derivative term
    # across the entire recipe range using its monotone power factor.
    end = Q(1, 32)
    derivative = (0, 0)
    for r, count in relaxed.items():
        term = g.mul(g.power(r, end if count >= 0 else 0), g.log(r))
        derivative = g.add(derivative, g.smul(term, -count))
    require(derivative[1] < 0 and g.moment(relaxed, 0)[0] > 0 > g.moment(relaxed, end)[1],
            "Directed relaxed crossing and uniform decrease")
    lo, hi = Q(0), end
    for _ in range(36):
        mid = (lo+hi)/2
        a, b = g.moment(relaxed, mid)
        if a > 0:
            lo = mid
        elif b < 0:
            hi = mid
        else:
            raise ValueError("Ambiguous packing ceiling bisection")
    require(0 < claim < lo < hi, "Candidate within fixed-profile packing ceiling")
    return dict(ambient_cap=cap, remainder_rank_mass=mass, raw_ceiling=[str(lo), str(hi)],
                claimed_fraction=[str(claim/hi), str(claim/lo)])


def extend_exit(word, hit):
    from copy import deepcopy

    e = hit["extension"]
    role, old, new, cut = (e[k] for k in ("role", "old", "new", "cut"))
    main = set(word["live"]) | {r+112 for r in word["live"]} | set(word["hosted"]["X2"]) | set(word["hosted"]["Y2"])
    require(0 <= role < word["public"] and role not in main and word["initial"][role] == 3
            and word["final"][role] == old and new == 127 and cut == len(word["program"]),
            "Literal rank-eight arbitrary helper exit")
    require(str(role) in hit["c"] or str(role) in hit["d"], "The extended coordinate participates")
    old_basis, new_basis = word["frames"][old], word["frames"][new]
    space = {0}
    for v in new_basis:
        space |= {v ^ x for x in space}
    require(len(old_basis) == 8 and len(new_basis) == 9 and set(old_basis) <= space,
            "One strictly nested paid exit rank")
    out = deepcopy(word)
    out["program"].append(["MOVE", role, old, new, False])
    out["final"][role] = new
    return out


def check_exit(word, hit, paths):
    from copy import deepcopy
    from temporal_construct import construct

    e = hit["extension"]
    extend_exit(word, hit)
    omitted = rejected(lambda: construct(word, hit, paths))
    bad = deepcopy(hit)
    bad["extension"]["old"] = bad["extension"]["new"]
    wrong_source = rejected(lambda: extend_exit(word, bad))
    return dict(move=["MOVE", e["role"], e["old"], e["new"], False], original_cut=e["cut"],
                omitted_extension_rejected=omitted, wrong_source_rejected=wrong_source)
