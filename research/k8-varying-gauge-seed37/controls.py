"""Small independent exhaustion and deliberate failures for the new gauge path."""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import runpy

HERE = Path(__file__).resolve().parent
V = runpy.run_path(str(HERE / "verify.py"))
S = V["SEARCH"]
require = V["require"]


def rejects(label, f):
    try:
        f()
    except (ValueError, KeyError, FileNotFoundError):
        return label
    raise ValueError("control accepted: " + label)


def run():
    word, programs, _, lower = V["load"]()
    # 5^5 independent literal-cost schedules exercise both operand signs and
    # the nonconvex unit discount. This is a finite check, not the clamping proof.
    terms = [(0, Q(1, 4), 1), (1, Q(3, 2), -1), (2, Q(-2), 1),
             (3, Q(1, 8), 1), (4, Q(-1), -1)]
    optimum = S["optimize"](terms)
    lo, hi = optimum["domain"]
    minimum, checked = None, 0
    for path in product(range(lo, hi + 1), repeat=len(terms)):
        value, previous = 0, 0
        for (_, q, sign), k in zip(terms, path):
            shifted = q * Q(2) ** (sign * k)
            a = ["add", ["L", 0], ["L", 1], shifted.numerator, shifted.denominator]
            b = ["add", ["L", 0], ["L", 1], q.numerator, q.denominator]
            value += abs(k - previous) + len(lower(a)) - len(lower(b))
            previous = k
        value += abs(previous)
        minimum = value if minimum is None else min(minimum, value)
        checked += 1
    require(minimum == optimum["delta_real"] == V["independent_minimum"](terms, [lo, hi], lower),
            "exhaustive tiny shortest path")
    rejected = []
    for orientation, events in sorted(programs.items()):
        h = 276
        row = S["optimize"](S["incident"](events, h))
        candidate = S["transform"](events, word, h, row["schedule"])
        first = row["schedule"][0][0]
        require(candidate[first][1][0] == "scale", "first inserted scale position")
        bad = candidate[:first] + candidate[first + 1:]
        rejected.append(rejects(orientation + "_missing_first_scale", lambda: V["replay"](bad, orientation)))
        bad = deepcopy(candidate)
        bad[first + 1] = deepcopy(events[first])
        rejected.append(rejects(orientation + "_unconjugated_add", lambda: V["replay"](bad, orientation)))
        bad = deepcopy(candidate)
        bad[first][2] = 1
        rejected.append(rejects(orientation + "_wrong_scale_frame", lambda: V["frame_check"](bad, word, h)))
        schedule = deepcopy(row["schedule"])
        schedule.pop()
        rejected.append(rejects(orientation + "_incomplete_schedule", lambda: S["transform"](events, word, h, schedule)))
    events = programs["forward"]
    schedule = [[i, 1] for i, _, _ in S["incident"](events, 276)]
    candidate = S["transform"](events, word, 276, schedule)
    require(candidate[-2] == ["scalar", ["scale", ["L", 276], 1, 2], 1],
            "nonzero final gauge has a paid exit SCALE")
    V["frame_check"](candidate, word, 276)
    V["replay"](candidate, "forward")
    bad = candidate[:-2] + candidate[-1:]
    rejected.append(rejects("missing_nonzero_gauge_exit", lambda: V["replay"](bad, "forward")))
    def no_clear(g):
        out = lower(g)
        return out[:-1] if g[0] == "add" else out
    rejected.append(rejects("unpaid_coefficient_work_clear", lambda: V["primitive_invoice"](programs["forward"], no_clear)))
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    del manifest["files"][V["LOWER"]]
    rejected.append(rejects("missing_source_pin", lambda: V["load"](manifest=manifest)))
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    manifest["files"][V["LOWER"]] = "0" * 64
    rejected.append(rejects("changed_source_pin", lambda: V["load"](manifest=manifest)))
    return {"tiny_schedules": checked, "tiny_minimum": minimum, "rejected": rejected}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
