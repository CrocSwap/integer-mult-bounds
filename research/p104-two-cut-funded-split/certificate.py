# SPDX-License-Identifier: Apache-2.0
"""Exact endpoint, COPY and cross-cut checks for the two timed directions."""

from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q

from source import need
from support import L


def vectors(word, witness):
    n = word["public"]
    m = n + word["owned_fields"]
    events = word["program"]
    requests = [defaultdict(set), defaultdict(set)]
    snapshots = [{}, {}]
    for side, key in enumerate(("gathers", "injections")):
        for points in witness[key]:
            for p in points:
                requests[side][p["cut"]].add(p["role"])

    def save(side, t, values):
        for r in requests[side].get(t, ()):
            snapshots[side][t, r] = values[r].copy()

    rows = [{r: Q(1)} if r < n else {} for r in range(m)]
    save(0, 0, rows)
    for t, e in enumerate(events):
        op, r = e[:2]
        if op in ("INIT", "CLEAR"):
            rows[r] = {}
        elif op == "SCALE":
            rows[r] = {j: Q(e[-2]) * q for j, q in rows[r].items()}
        elif op in ("ADD", "COPY"):
            if op == "COPY":
                need(not rows[r], "Source COPY destination zero for all inputs")
            L.add(rows[r], rows[e[2]], Q(e[-2]))
        save(0, t + 1, rows)

    cols = [{r: Q(1)} for r in range(m)]
    save(1, len(events), cols)
    for t in reversed(range(len(events))):
        e = events[t]
        op, r = e[:2]
        if op in ("INIT", "CLEAR"):
            cols[r] = {}
        elif op == "SCALE":
            cols[r] = {j: Q(e[-2]) * q for j, q in cols[r].items()}
        elif op in ("ADD", "COPY"):
            L.add(cols[e[2]], cols[r], Q(e[-2]))
            if op == "COPY":
                cols[r] = {m + t: Q(1)}
        save(1, t, cols)
    return snapshots


def dot(c, d):
    return sum(q * d.get(r, 0) for r, q in c.items())


def check(word, witness, snapshots):
    n = word["public"]
    main = set(word["live"]) | {r + 112 for r in word["live"]} | set(word["hosted"]["X2"] + word["hosted"]["Y2"])
    group = ({r for r, (a, b) in enumerate(zip(word["initial"], word["final"], strict=True))
              if (a, b) == (3, 127)} - main) | set(witness["donors"])
    need(len(group) == 618 and len(set(witness["pivots"])) == 2, "Exact extended helper group and distinct pivots")
    need(set(witness["pivots"]) <= group, "Both pivots are helpers")
    cuts = witness["cut1"], witness["cut2"]
    matrix = []
    for side, key, label in ((0, "gathers", "c"), (1, "injections", "d")):
        directions = []
        for k, points in enumerate(witness[key]):
            accum = {}
            for p in points:
                t = p["cut"]
                need(p["frame"] == witness["frames"][k] and (t <= cuts[k] if not side else t >= cuts[k]), "Literal causal schedule")
                key2 = t, p["role"]
                need(key2 in snapshots[side], "Pinned observation")
                L.add(accum, snapshots[side][key2], Q(p["coefficient"]))
            want = {int(r): Q(q) for r, q in witness[label][k].items()}
            need(accum == want and set(accum) <= group, "All endpoint, outside and COPY guard coordinates")
            directions.append(accum)
        matrix.append(directions)
    c, d = matrix
    need([[dot(a, b) for b in d] for a in c] == [[1, 0], [0, 1]], "Full two-sided pairing")

    perturbations = defaultdict(dict)
    for p in witness["injections"][0]:
        if p["cut"] < cuts[1]:
            L.add(perturbations[p["cut"]], {p["role"]: Q(p["coefficient"])}, Q(1))
    state = {}
    for t in range(min(perturbations, default=cuts[1]), cuts[1]):
        L.add(state, perturbations.get(t, {}), Q(1))
        op, r, *a = word["program"][t]
        if op in ("INIT", "CLEAR"):
            state.pop(r, None)
        elif op == "SCALE" and r in state:
            state[r] *= Q(a[0])
        elif op in ("ADD", "COPY"):
            if op == "COPY":
                need(not state.get(r), "First perturbation preserves the actual COPY guard")
            L.add(state, {r: state.get(a[0], Q(0))}, Q(a[1]))
    need(all(p["cut"] == cuts[1] for p in witness["gathers"][1]), "Second gathers share their literal cut")
    coupling = sum(Q(p["coefficient"]) * state.get(p["role"], 0) for p in witness["gathers"][1])
    need(coupling == 0, "First injections have zero response in the second gather")
    donors = [str(state.get(r, 0)) for r in witness["donors"]]
    need(donors == witness["first_late_donor_response"] == ["8", "8"], "Exact late donor responses")
    return dict(status="PASS_LITERAL_TWO_CUT_CERTIFICATE", cuts=list(cuts), pivots=witness["pivots"],
                frames=witness["frames"], cross_response=donors, pairing=[[1, 0], [0, 1]])


def controls(word, witness, snapshots):
    def reject(bad):
        try:
            check(word, bad, snapshots)
        except ValueError:
            return True
        raise ValueError("Timed certificate corruption accepted")

    result = {}
    for k in range(2):
        for side in ("gathers", "injections"):
            bad = deepcopy(witness)
            bad[side][k].pop()
            result[f"omitted_{side}_{k}"] = reject(bad)
    bad = deepcopy(witness)
    bad["pivots"][1] = bad["pivots"][0]
    result["reused_retirement_pivot"] = reject(bad)
    bad = deepcopy(witness)
    bad["first_late_donor_response"][1] = "7"
    result["altered_cross_cut_response"] = reject(bad)
    return result
