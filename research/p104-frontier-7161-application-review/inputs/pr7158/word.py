# SPDX-License-Identifier: Apache-2.0
"""Sparse scalar witnesses and a separate census of the literal paid word."""

from collections import Counter, defaultdict
from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bump(vector, role, increment):
    value = vector.get(role, 0) + increment
    if value:
        vector[role] = value
    else:
        vector.pop(role, None)


def frame_spaces(word):
    spaces = []
    for basis in word["frames"]:
        span = {0}
        for v in basis:
            require(0 < v < 512 and v not in span, "Independent native axes")
            span |= {v ^ w for w in span}
        spaces.append(span)
    return spaces


def trace(word):
    """Check the literal frames and ownership, and count every MOVE."""
    n = word["public"]
    require(len(word["initial"]) == len(word["final"]) == n, "Complete boundaries")
    spaces = frame_spaces(word)
    active = dict(enumerate(word["initial"]))
    paid, rises = Counter(), Counter()
    labels = set()
    peak = lifetimes = 0
    for e in word["program"]:
        op, r = e[:2]
        if op == "INIT":
            require(n <= r < n + word["owned_fields"] and r not in active, "Fresh owned label")
            active[r] = e[2]
            labels.add(r)
            lifetimes += 1
            peak = max(peak, len(active) - n)
        elif op == "CLEAR":
            require(r >= n and active[r] == e[2], "Clear only a live owned field")
            del active[r]
        elif op == "MOVE":
            a, b, owned = e[2:]
            require(active[r] == a and owned == (r >= n), "Literal MOVE source and ownership")
            upward = spaces[a] < spaces[b]
            require(upward or (owned and spaces[b] < spaces[a]), "Strict nested MOVE")
            rank = abs(len(word["frames"][b]) - len(word["frames"][a]))
            paid[rank] += 1
            if upward and owned:
                rises[rank] += 1
            active[r] = b
        else:
            require(op in ("ADD", "COPY", "SCALE") and active[r] == e[-1], "Literal scalar target")
            if op != "SCALE":
                require(r != e[2] and active[e[2]] == e[-1], "Literal scalar source")
    require(active == dict(enumerate(word["final"])), "All final frames and owned retirement")
    require(len(labels) == word["owned_fields"], "All owned labels charged")

    main = set(word["live"]) | {r + 112 for r in word["live"]}
    main.update(word["hosted"]["X2"])
    main.update(word["hosted"]["Y2"])
    helpers = Counter()
    for r in set(range(n)) - main:
        a, b = word["initial"][r], word["final"][r]
        require(spaces[a] < spaces[b], "Productive helper boundary")
        helpers[len(word["frames"][b]) - len(word["frames"][a])] += 1
    return dict(paid=paid, helpers=helpers, lifetimes=lifetimes, owned_peak=peak,
                labels=len(labels), owned_ascent_mass=sum(k * v for k, v in rises.items()))


def timed_vector(word, witness, *, suffix):
    """Gather covector backwards, or inject one perturbation forwards.

    In these coordinates MOVE changes the frame and preserves the scalar
    vector. The source phase/frame proof supplies that identification.
    """
    cut = witness["cut"]
    events = word["program"]
    field = "injections" if suffix else "gathers"
    schedule = defaultdict(dict)
    for row in witness[field]:
        t, r = row["cut"], row["role"]
        require((cut <= t <= len(events)) if suffix else (0 <= t <= cut), "Causal schedule")
        coefficient = Fraction(row["coefficient"])
        require(row["frame"] == witness["frame"] and r not in schedule[t] and coefficient,
                "Distinct nonzero timed observations in the declared frame")
        schedule[t][r] = coefficient
    state = {}
    if suffix:
        for t in range(cut, len(events) + 1):
            for r, q in schedule[t].items():
                bump(state, r, q)
            if t < len(events):
                step(state, events[t])
        return state
    for t in range(cut, -1, -1):
        if t < cut:
            op, r, *args = events[t]
            if op in ("INIT", "CLEAR"):
                state.pop(r, None)
            elif op == "SCALE":
                bump(state, r, (Fraction(args[0]) - 1) * state.get(r, 0))
            elif op in ("ADD", "COPY"):
                bump(state, args[0], Fraction(args[1]) * state.get(r, 0))
                if op == "COPY":
                    state.pop(r, None)
        for r, q in schedule[t].items():
            bump(state, r, q)
    require(all(r < word["public"] for r in state), "No pre-initialized owned input")
    return state


def step(state, e, *, guard_copy=True):
    op, r = e[:2]
    if op in ("INIT", "CLEAR"):
        state.pop(r, None)
    elif op == "SCALE":
        bump(state, r, (Fraction(e[2]) - 1) * state.get(r, 0))
    elif op in ("ADD", "COPY"):
        if op == "COPY":
            require(not guard_copy or not state.get(r, 0), "Nonzero COPY destination")
            state.pop(r, None)
        bump(state, r, Fraction(e[3]) * state.get(e[2], 0))


def check_paths(word, witness, paths):
    events = word["program"]
    f = witness["frame"]
    spaces = frame_spaces(word)
    paid = witness["path"]
    covered = set()
    for path in [*paths, paid]:
        r, lo, hi = path["role"], path["lo"], path["hi"]
        require(0 <= lo < hi <= len(events) and path["frame"] == f, "Path interval")
        contacts = [i for i in range(lo, hi) if events[i][1] == r
                    or (events[i][0] in ("ADD", "COPY") and events[i][2] == r)]
        require(contacts == path["moves"] and not covered.intersection(contacts), "Complete contact-free paths")
        covered.update(contacts)
        moves = [events[i] for i in contacts]
        require(moves and all(e[0] == "MOVE" for e in moves), "Retimed operations are MOVEs")
        frames = [moves[0][2], *(e[3] for e in moves)]
        require(frames[:-1] == [e[2] for e in moves], "Continuous source path")
        if path is paid:
            a, b = frames[0], frames[-1]
            require((a, b) == (paid["old"], paid["new"]) and spaces[a] < spaces[f] < spaces[b],
                    "Strictly nested paid midpoint")
            require((len(spaces[f]).bit_length() - len(spaces[a]).bit_length(),
                     len(spaces[b]).bit_length() - len(spaces[f]).bit_length()) == (3, 5),
                    "Paid replacement ranks")
        else:
            require(frames == path["frames"] and f in frames, "Retained neutral path")
    for row in witness["gathers"] + witness["injections"]:
        path = paths[row["path"]] if "path" in row else paid
        require(row["role"] == path["role"] and path["lo"] <= row["cut"] <= path["hi"],
                "Observation belongs to the retimed path")


def pulse(word, skip=None):
    state = {word["public"] - 1: Fraction(1)}
    for i, e in enumerate(word["program"]):
        if i != skip:
            step(state, e)
    return state


def chart_checks(parent, word, witness, paths):
    check_paths(parent, witness, paths)
    c = timed_vector(parent, witness, suffix=False)
    d = timed_vector(parent, witness, suffix=True)
    vectors = [{int(r): Fraction(q) for r, q in witness[k].items()} for k in ("c", "d")]
    require([c, d] == vectors and sum(q * d.get(r, 0) for r, q in c.items()) == 1,
            "Complete c and d, including all collateral coordinates, and unit pairing")
    pivot, frame = witness["pivot"], witness["frame"]
    a, b = parent["initial"][pivot], parent["final"][pivot]
    main = set(parent["live"]) | {r+112 for r in parent["live"]}
    main.update(parent["hosted"]["X2"] + parent["hosted"]["Y2"])
    group = set(c) | set(d) | {pivot}
    require(not group.intersection(main) and all((parent["initial"][r], parent["final"][r]) == (a, b) for r in group),
            "One helper boundary group")
    spaces = frame_spaces(parent)
    ranks = [len(parent["frames"][j])-len(parent["frames"][i]) for i, j in ((a, frame), (frame, b))]
    require(spaces[a] < spaces[frame] < spaces[b] and witness["ranks"] == ranks == [4, 5],
            "Strict productive midpoint")
    mut = 37799
    require(word["program"][mut] == ["ADD", 781, 1558, "1/2", 306], "Literal injection under test")
    z = word["public"] - 1
    full, omitted = pulse(word), pulse(word, skip=mut)
    require(full == {z: 1}, "New arbitrary helper pulse returns without collateral")
    collateral = {r: q for r, q in omitted.items() if r != z}
    require(omitted.get(z) == 1 and len(collateral) == 24 and max(collateral) < word["public"],
            "Omitted injection leaves 24 wrong public outputs with the helper still correct")

    toy = [["INIT", 1, 0], ["ADD", 1, 0, "1", 0], ["COPY", 1, 0, "1", 0], ["CLEAR", 1, 0]]
    unguarded, guarded = {0: 1}, {0: 1}
    for e in toy:
        step(unguarded, e, guard_copy=False)
    require(unguarded == {0: 1}, "Dirty COPY control is invisible at the endpoint")
    try:
        for e in toy:
            step(guarded, e)
    except ValueError as error:
        require(str(error) == "Nonzero COPY destination", "Expected interior COPY failure")
    else:
        raise ValueError("Dirty COPY accepted")
    return dict(c=c, d=d, gather_count=len(witness["gathers"]), injection_count=len(witness["injections"]),
                pulse=z, omitted_injection=mut, collateral=sorted(collateral), erased_dirty_copy_rejected=True)
