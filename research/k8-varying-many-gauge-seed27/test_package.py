"""Independent optimum, no-op and restoration controls for the L253 package."""
import difflib
import importlib.util
import json
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    verify = load("l253_verify", HERE / "verify.py")
    independent = load("l253_independent", HERE / "independent.py")
    parent, varying = verify.modules()
    result, candidates = verify.compute()
    _, static_candidates = parent.compute()
    lib = parent.engine()
    word, originals, _, _ = lib.load()
    helper = result["selection"]["helper"]
    controls = 0

    # A tiny exhaustive fixture checks the separate recurrence against every
    # schedule in its complete finite interval.
    toy = [(0, Q(1, 4), 1), (1, Q(3, 2), -1), (2, Q(5, 8), 1)]
    toy_value, (low, high) = independent.exact_minimum(toy)
    brute = min(independent.schedule_delta(toy, [[i, k] for i, k in enumerate(row)])
                for row in product(range(low, high + 1), repeat=len(toy)))
    need(toy_value == brute, "three-use exhaustive schedule control")
    controls += 1

    for orientation in ("forward", "backward"):
        static = static_candidates[orientation]
        terms = varying.incident(static, helper)
        row = result["orientations"][orientation]
        min_delta, domain = independent.exact_minimum(terms)
        need(domain == row["exponent_domain"], orientation + " independent domain")
        need(row["domain_size"] == 7 and row["dp_transition_evaluations"] == 4662,
             orientation + " complete DP state coverage")
        need(min_delta == row["incremental_delta_real"] == -91,
             orientation + " independent all-integer optimum")
        need(independent.schedule_delta(terms, row["schedule"]) == min_delta,
             orientation + " exact chosen schedule price")
        controls += 1

        # The all-zero schedule is a no-op and must earn no saving.
        zero = [[index, 0] for index, _, _ in terms]
        no_op = varying.transform(static, word, helper, zero)
        need(lib.replay(no_op, orientation) == lib.replay(static, orientation)
             and lib.invoice(no_op, "copy-init") == lib.invoice(static, "copy-init"),
             orientation + " zero schedule control")
        controls += 1

        # Removing one newly inserted transition scale breaks the formal map.
        candidate = candidates[orientation]
        matcher = difflib.SequenceMatcher(a=[json.dumps(e, sort_keys=True) for e in static],
                                          b=[json.dumps(e, sort_keys=True) for e in candidate],
                                          autojunk=False)
        inserted = []
        for tag, _, _, j1, j2 in matcher.get_opcodes():
            if tag == "insert":
                inserted.extend(range(j1, j2))
        scale_index = next((i for i in inserted if candidate[i][0] == "scalar"
                            and candidate[i][1][0] == "scale"
                            and candidate[i][1][1] == ["L", helper]), None)
        need(scale_index is not None, orientation + " inserted L253 transition exists")
        broken = candidate[:scale_index] + candidate[scale_index + 1:]
        try:
            lib.replay(broken, orientation)
        except ValueError:
            controls += 1
        else:
            raise ValueError(orientation + " omitted-scale control was accepted")

    print("PASS_L253_PACKAGE_CONTROLS controls=" + str(controls)
          + " orientations=2 seed=27 helper=253")


if __name__ == "__main__":
    main()
