# SPDX-License-Identifier: Apache-2.0
"""Two guarded timed helper retirements at literal source cuts."""

from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inverse(program):
    return [[e[0], *e[1:-2], str(1 / Fraction(e[-2]) if e[0] == "SCALE" else -Fraction(e[-2])), e[-1]]
            for e in reversed(program)]


def construct(word, witness):
    n, owned = word["public"], word["owned_fields"]
    events = word["program"]
    cuts = (witness["cut1"], witness["cut2"])
    frames, pivots, donors = witness["frames"], witness["pivots"], witness["donors"]
    require(witness["mode"] == "literal" and 0 <= cuts[0] < cuts[1] < len(events), "Two literal ordered cuts")
    require(len(set(pivots)) == len(set(donors)) == 2 and pivots[1] in donors, "Distinct retirement roles and two paid exits")
    require(all(word["initial"][r] == 3 and word["final"][r] == 245 for r in donors), "Exact rank-eight exit inventory")
    require(word["initial"][pivots[0]] == 3 and word["final"][pivots[0]] == 127, "First helper in rank-nine group")
    require([len(word["frames"][f]) for f in frames] == [4, 8], "Exact two split ranks")
    boundary = witness["basis"]
    require(all(e[0] in ("ADD", "SCALE") and e[-1] == 3 for e in boundary), "Input-chart boundary basis")

    out = deepcopy(word)
    out["public"] = n + 2
    out["owned_fields"] = owned + 4
    out["initial"].extend(frames)
    for r in donors:
        out["final"][r] = 127
    for p, f in zip(pivots, frames, strict=True):
        out["final"][p] = f
    out["final"].extend([127, 127])
    charts = word["initial"] + [None] * owned
    gather, inject, first, last, retirement = (defaultdict(list) for _ in range(5))
    for k, cut in enumerate(cuts):
        records = witness["gathers"][k], witness["injections"][k]
        require(all(records), "Both timed direction schedules are nonempty")
        first[min(x["cut"] for x in records[0])].append(k)
        last[max(x["cut"] for x in records[1])].append(k)
        retirement[cut].append(k)
        for target, points, early in ((gather, records[0], True), (inject, records[1], False)):
            for point in points:
                time = point["cut"]
                require(point["frame"] == frames[k] and 0 <= time <= len(events) and
                        (time <= cut if early else time >= cut), "Coframed causal schedule")
                target[time].append((k, point))

    def mapped(role, time, at_retirement=True):
        for k, pivot in enumerate(pivots):
            if role == pivot and (time > cuts[k] or at_retirement and time == cuts[k]):
                return n + k
        return role + 2 if role >= n else role

    def emit_original(e, time):
        e = e.copy()
        for j in (1, 2) if e[0] in ("ADD", "COPY") else (1,):
            e[j] = mapped(e[j], time)
        program.append(e)

    def read_original(e):
        op, r = e[:2]
        if op == "MOVE":
            require(charts[r] == e[2], "Source MOVE frame")
            charts[r] = e[3]
        elif op == "INIT":
            require(charts[r] is None, "Source owned initialization")
            charts[r] = e[2]
        elif op == "CLEAR":
            require(charts[r] == e[2], "Source owned clear")
            charts[r] = None
        else:
            require(charts[r] == e[-1], "Source scalar destination")
            if op in ("ADD", "COPY"):
                require(charts[e[2]] == e[-1], "Source scalar donor")

    def buffers(k):
        a = n + 2 + owned + 2 * k
        return a, a + 1

    program = inverse(boundary)
    for i in range(len(events) + 1):
        for k in first[i]:
            a, _ = buffers(k)
            program.append(["INIT", a, frames[k]])
        for k, point in gather[i]:
            r, f = point["role"], frames[k]
            require(charts[r] == f, "Gather in actual literal chart")
            a, _ = buffers(k)
            program.append(["ADD", a, mapped(r, i, False), point["coefficient"], f])
        for k in retirement[i]:
            p, f, z = pivots[k], frames[k], n + k
            require(charts[p] == f, "Resident pivot at its exact cut")
            a, b = buffers(k)
            program.extend([["INIT", b, f], ["ADD", b, z, "1", f], ["ADD", b, a, "-1", f],
                            ["ADD", z, p, "1", f], ["ADD", z, a, "-1", f], ["ADD", z, b, "-1", f],
                            ["ADD", p, a, "1", f], ["ADD", p, z, "-1", f], ["CLEAR", a, f]])
        for k, point in inject[i]:
            r, f = point["role"], frames[k]
            require(charts[r] == f, "Injection in actual literal chart")
            _, b = buffers(k)
            program.append(["ADD", mapped(r, i), b, point["coefficient"], f])
        for k in last[i]:
            _, b = buffers(k)
            program.append(["CLEAR", b, frames[k]])
        if i < len(events):
            event = events[i]
            read_original(event)
            emit_original(event, i)
    require(charts == word["final"] + [None] * owned, "Source complete final chart boundary")
    for r in donors:
        emit_original(["MOVE", r, 245, 127, False], len(events))
    for e in boundary:
        emit_original([*e[:-1], 127], len(events))
    out["program"] = program
    return out


def profiles(word):
    n = word["public"]
    main = set(word["live"]) | {r + 112 for r in word["live"]} | set(word["hosted"]["X2"] + word["hosted"]["Y2"])
    ranks = tuple(map(len, word["frames"]))
    paid = Counter(abs(ranks[e[3]] - ranks[e[2]]) for e in word["program"] if e[0] == "MOVE")
    targets = Counter(ranks[b] - ranks[a] for r, (a, b) in enumerate(zip(word["initial"], word["final"], strict=True)) if r not in main)
    live = peak = lifetimes = 0
    for e in word["program"]:
        if e[0] == "INIT":
            lifetimes += 1
            live += 1
            peak = max(peak, live)
        elif e[0] == "CLEAR":
            live -= 1
    require(live == 0, "Owned lifetimes close")
    return dict(paid=dict(paid), targets=dict(targets), events=len(word["program"]), public=n,
                owned=word["owned_fields"], lifetimes=lifetimes, peak=peak)
