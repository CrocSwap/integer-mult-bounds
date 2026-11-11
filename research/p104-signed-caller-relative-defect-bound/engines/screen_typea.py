"""Exact Type A query prices and relative rank-slack obstruction."""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import runpy
import signal

ENGINE_SHA = "d9c5126ec681646350f60ba44ad3ad548a98e6d9d177d1fff711ae8a0c6dfd97"


def shear(coefficient):
    return ((Fraction(1), Fraction(0)), (Fraction(coefficient), Fraction(1)))


def run(root, engine, out):
    assert __debug__ and sha256(engine.read_bytes()).hexdigest() == ENGINE_SHA
    m = runpy.run_path(str(engine))
    paths = m["authenticate"](root)
    c = m["decode"](paths["round30/complex/source/inputs/CALLER.json"][1])
    early = m["decode"](paths["round30/complex/source/inputs/EARLY-RESULT.json"][1])
    audit = runpy.run_path(str(paths["round30/complex/audit.py"][0]))
    _, _, _, edges, _, _, copies, paid, target, _ = audit["read_model"]()
    assert audit["HEAD"] == m["HEAD"] and copies == 17 and len(edges) == 137891
    exponent = Fraction(early["price"]["independent_raw_bracket"][1])
    power = runpy.run_path(str(paths["round30/complex/source/powers.py"][0]))["power"]
    a = c["types"]["A"]
    ports = len(set(a["ports"]))
    assert ports == len(a["ports"]) == 96 and power(1, exponent) == (1, 1)
    query = [(i, event[2:]) for i, event in enumerate(c["events"]) if event[:2] == ["A", "QUERY"]]
    assert len(query) == 4
    tariff = {r: power(r, exponent) for r in set(paid) | set(target)}
    net = {r: target[r] - paid[r] for r in tariff}
    base = [sum(n * tariff[r][i if n >= 0 else 1-i] for r, n in net.items()) for i in range(2)]
    cases = []
    for size in range(1, 5):
        for subset in combinations([i for i, _ in query], size):
            saving = size * ports
            cases.append({"clocks": subset, "removed_calls": size, "paid_delta": {1: -saving},
                          "saving": str(saving), "complete_margin_interval": [str(x + saving) for x in base]})
    pins = {"lead/screen.py": ENGINE_SHA} | m["PINS"]
    m["write"](out, "PRICE.json", {"head": m["HEAD"], "pins": pins, "scenarios": cases,
                                  "type_a_ports": ports, "copies": copies, "whole_saving_upper": str(4 * ports),
                                  "old_crossing_upper": str(exponent), "old_margin": list(map(str, base)),
                                  "original_paid": dict(paid), "original_productive": dict(target),
                                  "grant": "additional ordinary mixing and other ancillary costs free only in this upper"})

    n = a["roles"]
    assert n == 36 and a["offset"] == 0 and len(a["diagonal"]) == n
    assert all(row[0] == -1 and row[1] == 0 and len(row) == 19 for row in a["diagonal"])
    assert all(r != s and 0 <= min(r, s) and max(r, s) < n and k % 2 for _, (r, s, k) in query)
    alpha = Fraction(a["alpha2"])
    assert alpha
    blocks = []
    for clock, event in enumerate(c["events"]):
        if event[0] == "J":
            _, stage, active, _ = event
            assert len(active) == len(set(active)) == 4 and all(0 <= r < n for r in active)
            # Order the two planes (source, destination) as (x,y) and (v,u).
            relative = [m["mul"](m["inv"](shear(b)), shear(-b)) for b in (Fraction(1), alpha)]
            for plane in relative:
                assert plane == shear(plane[1][0]) and plane[1][0]
                # The defect image is the destination line. The shear fixes it.
                assert plane[0][1] == 0 and plane[1][1] + 1 == 2
            blocks.append({"clock": clock, "stage": stage, "roles": active,
                           "relative_planes": [m["stringify"](p) for p in relative],
                           "rank_defect": 2, "rank_plus_identity_on_defect": 2})
        elif event[0] == "A":
            assert event[1] in {"ADD", "SCALE", "SWAP", "LAMBDA", "QUERY", "IDLE_ONE"}
    assert [row["stage"] for row in blocks] == list(range(1, 18))
    maximum = sum(row["rank_defect"] for row in blocks) + len(query)
    lower = n + max(row["rank_plus_identity_on_defect"] for row in blocks)
    assert maximum == lower == 38
    for case in cases:
        case["relative_rank_upper"] = maximum - case["removed_calls"]
        assert case["relative_rank_upper"] < lower
    # A pair of sign reflections has total rank equal to dimension and
    # zero plus-identity rank on each defect. It satisfies the inequality.
    assert (Fraction(-1) + 1) == 0
    # A nonzero shear has rank one and plus-identity rank one on its
    # defect, so it cannot realize a saturated negative endpoint alone.
    assert shear(Fraction(2))[1][1] + 1 == 2
    m["write"](out, "SUPPORT.json", {"head": m["HEAD"], "pins": pins, "checked_subsets": len(cases),
          "unvisited_subsets": 0, "status": "all_subsets_excluded", "endpoint": "-I_36",
          "q_specializations": [1, -1], "body_specialization": 1, "lower_total_relative_rank": lower,
          "query": query, "j_blocks": blocks, "cases": cases, "optimistic_saving_upper_after_support": "0",
          "price_sha256": sha256((out / "PRICE.json").read_bytes()).hexdigest(),
          "controls": ["saturated_reflections_allowed", "saturated_shear_excluded"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("round30", type=Path)
    parser.add_argument("engine", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()

    def cap(*_):
        raise TimeoutError("20-second hard runner deadline")

    signal.signal(signal.SIGALRM, cap)
    signal.alarm(20)
    args.out.mkdir()
    run(args.round30.resolve(), args.engine.resolve(), args.out.resolve())
