# SPDX-License-Identifier: Apache-2.0
"""Small independent recurrence control and registered-result checks."""
import importlib.util
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("joint_temporal_verify", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def exhaustive_cost(events, helpers, lo, hi):
    terms = []
    for event in events:
        gate = event[1]
        signs = [int(gate[1] == ["L", h]) - int(gate[2] == ["L", h]) for h in helpers]
        terms.append((verify.Fraction(gate[3], gate[4]), signs))
    best = None
    states = list(itertools.product(range(lo, hi + 1), repeat=2))
    for path in itertools.product(states, repeat=len(terms)):
        previous = (0, 0)
        cost = 0
        for (q, signs), current in zip(terms, path):
            cost += verify.price(q * verify.pow2(signs[0] * current[0] + signs[1] * current[1]))
            cost -= verify.price(q)
            cost += abs(current[0] - previous[0]) + abs(current[1] - previous[1])
            previous = current
        cost += abs(previous[0]) + abs(previous[1])
        best = cost if best is None else min(best, cost)
    return best


def main():
    tiny = [
        ["scalar", ["add", ["L", 253], ["L", 254], 3, 8], 1],
        ["scalar", ["add", ["L", 254], ["L", 17], 1, 4], 1],
        ["scalar", ["add", ["L", 253], ["L", 19], 3, 2], 1],
    ]
    exact = verify.joint_optimize(tiny, (253, 254), -1, 1)
    brute = exhaustive_cost(tiny, (253, 254), -1, 1)
    if exact["delta_real"] != brute:
        raise ValueError("tiny exact DP differs from direct exhaustive enumeration")
    result = json.loads((HERE / "RESULT.json").read_bytes())
    if result["status"] != "PASS_L253_L254_JOINT_BOX":
        raise ValueError("registered result status")
    for orientation in ("forward", "backward"):
        row = result["orientations"][orientation]
        if row["complex_saving"] != 364 or row["formal_columns"] != 712:
            raise ValueError(orientation + " result receipt")
        if row["negative_controls"] != ["shared_ADD_coefficient", "omitted_transition_scale"]:
            raise ValueError(orientation + " negative controls")
    print("PASS_L253_L254_JOINT_TESTS tiny_dp=exhaustive orientations=2 controls=4")


if __name__ == "__main__":
    main()
