"""Small exact controls for the independent temporal-gauge DP."""

from fractions import Fraction
import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("seed25_independent_test", HERE / "independent.py")
independent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(independent)


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    terms = [
        (0, Fraction(3, 2), 1),
        (1, Fraction(5, 4), -1),
        (2, Fraction(7, 8), 1),
    ]
    optimum = independent.optimize(terms)
    need(optimum["delta_real"] == independent.exhaustive(
        terms, optimum["domain"][0], optimum["domain"][1]), "DP equals 27-vector exhaustive search")
    need(independent.objective(terms, optimum["schedule"]) == optimum["delta_real"],
         "schedule recomputes exact objective")

    events = [
        ["scalar", ["add", ["L", 4], ["L", 5], 3, 2], 0],
        ["scalar", ["add", ["L", 6], ["L", 4], 1, 2], 0],
        ["phase", "done"],
    ]
    zero, pulses = independent.transform(events, 4, [[0, 0], [1, 0]])
    need(zero == events and pulses == [], "zero schedule identity")
    changed, pulses = independent.transform(events, 4, [[0, -1], [1, 1]])
    need(len(pulses) == 3 and changed != events, "entry, transition, and exit pulses")
    try:
        independent.transform(events, 4, [[0, -1]])
    except ValueError:
        pass
    else:
        raise AssertionError("incomplete schedule was accepted")
    print("PASS_TEMPORAL_DP_CONTROLS exhaustive=27 zero_identity=1 incomplete_schedule_rejected=1")


if __name__ == "__main__":
    main()
