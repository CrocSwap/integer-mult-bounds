#!/usr/bin/env python3
"""Sharp carried-frame intervals and exact native endpoints; no new kappa.

Apache-2.0. Prepared by 1337isnot1337 with substantial OpenAI Codex assistance.
Source and predecessor credit are in README.md and the retained source notices.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from frame_dag import FrameDAG, NativeSchedule, basis, dimension, image, inverse, join, need, space
from replay import replay


def rejected(action, reason):
    try:
        action()
    except ValueError as error:
        need(reason in str(error), "Unexpected rejection reason: " + str(error))
        return str(error)
    raise ValueError("A rejection control was accepted: " + reason)


def source():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for row in pins["files"]:
        if row["usage"] == "input":
            need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                 "Changed source: " + row["path"])
    code = ("import contextlib,io,json,sys;sys.path.insert(0,sys.argv[1]);"
            "capture=io.StringIO();"
            "exec('with contextlib.redirect_stdout(capture):\\n import verify as S');"
            "p={d:S.construct(w)[0] for d,w in S.a['programs'].items()};"
            "print(json.dumps({'canonical':S.c,'programs':p}))")
    with tempfile.TemporaryDirectory(prefix="carried-source-cache-") as cache:
        run = subprocess.run([sys.executable, "-I", "-B", "-X", "pycache_prefix=" + cache,
                              "-c", code, str(ROOT / "research/native-frame-carrying-swaps")],
                             check=True, capture_output=True, text=True, timeout=120)
    return json.loads(run.stdout)


def toy():
    graph = FrameDAG(3)
    initial, left, right, terminal = (graph.node(space([1])), graph.node(),
                                      graph.node(), graph.node(space([1, 2, 4])))
    rotation = (2, 4, 1)
    graph.edge(initial, left)
    graph.edge(left, right)
    graph.edge(left, right, rotation)
    graph.edge(right, terminal)
    lower, upper = graph.bounds()
    all_spaces = {1}
    for vector in range(1, 8):
        all_spaces |= {join(value, space([vector])) for value in tuple(all_spaces)}
    need(len(all_spaces) == 16, "All subspaces of F2^3")
    solutions = []
    for a in all_spaces:
        for b in all_spaces:
            if space([1]) & a == space([1]) and a & b == a and image(rotation, a) & b == image(rotation, a):
                values = [space([1]), a, b, space([1, 2, 4])]
                graph.check(values)
                solutions.append(values)
    need(len(solutions) == 6, "Exhaustive toy schedule count")
    pins = 0
    for node in (left, right):
        actual = {values[node] for values in solutions}
        interval = {value for value in all_spaces if value & lower[node] == lower[node] and value & upper[node] == value}
        need(actual == interval, "Complete marginal interval, including intermediate subspaces")
        for value in interval:
            extension = graph.extend(node, value)
            graph.check(extension)
            need(extension[node] == value, "Pinned extension")
            pins += 1
    wrong = lower[:]
    wrong[right] = join(wrong[left], image(inverse(rotation), wrong[left]))
    controls = {
        "wrong_map_direction": rejected(lambda: graph.check(wrong), "Mapped containment failed"),
        "coupled_marginal_choices": rejected(
            lambda: graph.check([lower[initial], upper[left], lower[right], lower[terminal]]),
            "Mapped containment failed"),
        "pin_below_lower": rejected(lambda: graph.extend(right, space([1])), "Infeasible lower bound"),
        "changed_fixed_node": rejected(lambda: graph.extend(terminal, space([1, 2])), "Changed fixed node"),
        "singular_map": rejected(lambda: inverse((1, 1, 4)), "Singular binary map"),
    }
    return {"subspaces": 16, "assignments_checked": 256, "solutions": len(solutions),
            "marginal_pins_extended": pins, "controls": controls}


def profile_record(profile):
    return {str(rank): count for rank, count in sorted(profile.items())}


def cut_differences(candidate, baseline):
    return [sum(count * min(rank, cut) for rank, count in candidate.items()) -
            sum(count * min(rank, cut) for rank, count in baseline.items())
            for cut in range(1, 10)]


def run():
    retained = source()
    canonical = retained["canonical"]
    result = {"status": "PASS_CARRIED_WARP_FRAME_INTERVALS", "toy": toy(), "directions": {},
              "new_kappa_claimed": False,
              "scope": "Sharp marginal intervals for the binary frame contract; exact normalized endpoints; no new physical phase or supplier admission"}
    for direction, original in retained["programs"].items():
        backward = direction == "backward"
        baseline = replay(canonical, original, backward)
        need(baseline == Counter({1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}), "Source paid profile")
        schedule = NativeSchedule(canonical, original)
        graph = schedule.graph
        lower, upper = graph.bounds()
        bounds_census = Counter(f"{dimension(a)}-{dimension(b)}" for a, b, fixed in
                               zip(lower, upper, graph.fixed) if fixed is None)
        records = {}
        generated = {}
        for name, values in (("original_contacts", schedule.original_values), ("least", lower), ("greatest", upper)):
            changed, program = schedule.realize(values)
            paid = replay(changed, program, backward)
            cuts = cut_differences(paid, baseline)
            need(sum(rank * count for rank, count in paid.items()) == 5327, "Fixed total paid rank")
            if name == "original_contacts":
                need(paid == baseline, "Original contact reconstruction")
            else:
                need(all(value >= 0 for value in cuts) and any(value > 0 for value in cuts),
                     "Extremal schedule dominated for every strictly concave rank price")
            records[name] = {"paid": profile_record(paid), "rank_mass": 5327,
                             "min_rank_cut_difference": cuts,
                             "warp_events": sum(e[0] == "warp" for e in program),
                             "swaps": sum(e[0] == "weighted_swap" for e in program),
                             "frame_count": len(changed["frames"])}
            generated[name] = changed, program
        contact = next(node for node in schedule.contacts.values()
                       if dimension(upper[node]) - dimension(lower[node]) >= 2)
        vector = next(vector for vector in basis(upper[contact]) if not lower[contact] >> vector & 1)
        intermediate = join(lower[contact], space([vector]))
        need(lower[contact] != intermediate != upper[contact], "Strict intermediate source frame")
        extension = graph.extend(contact, intermediate)
        changed, program = schedule.realize(extension)
        pinned_paid = replay(changed, program, backward)
        records["intermediate_pin"] = {"node": contact, "lower_dimension": dimension(lower[contact]),
                                       "pinned_dimension": dimension(intermediate),
                                       "upper_dimension": dimension(upper[contact]),
                                       "paid": profile_record(pinned_paid)}
        changed, program = generated["least"]
        bad = deepcopy(program)
        next(event for event in bad if event[0] == "climb")[-1] += 1
        controls = {"wrong_paid_rank": rejected(lambda: replay(changed, bad, backward), "Paid rank mismatch")}
        bad_warp = deepcopy(original)
        need(bad_warp[3] == ["warp", ["L", 273], -59, 0, 0] and
             bad_warp[4] == ["warp", ["L", 273], 59, 0, 0], "Pinned warp counterexample")
        bad_warp[3][4], bad_warp[4][3] = 1, 1
        controls["false_warp_frame"] = rejected(lambda: replay(canonical, bad_warp, backward), "Warp map/frame mismatch")
        bad_swap = deepcopy(original)
        event = next(event for event in bad_swap if event[0] == "weighted_swap" and event[5][0] != event[5][1])
        event[6] = event[5][:]
        controls["missing_swap_frame_carry"] = rejected(lambda: replay(canonical, bad_swap, backward), "Swap carries frames")
        bad_sign = deepcopy(original)
        event = next(event for event in bad_sign if event[0] == "weighted_swap")
        event[3] = str(-Fraction(event[3]))
        controls["wrong_swap_sign"] = rejected(
            lambda: replay(canonical, bad_sign, backward), "Normalized independent-input endpoint")
        result["directions"][direction] = {"graph_nodes": len(graph.fixed),
                                             "graph_edges": sum(map(len, graph.parents)),
                                             "contact_nodes": len(schedule.contacts),
                                             "variable_interval_dimensions": dict(sorted(bounds_census.items())),
                                             "schedules": records, "controls": controls}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = json.loads(json.dumps(run()))
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        (HERE / "RESULT.json").write_text(serialized)
    need(result == json.loads((HERE / "RESULT.json").read_text()), "Deterministic frame interval receipt")
    print(serialized, end="")


if __name__ == "__main__":
    main()
