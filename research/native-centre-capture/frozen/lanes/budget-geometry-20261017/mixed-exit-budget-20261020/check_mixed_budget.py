"""Price one or two changed exits from the frozen rational bounds."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "low-displacement-budget-20261020" / "BUDGET.json"
PIN = "12836f56beffb0c136b075b44ec25377bba88d122924c67bd0a159a5037b84d2"


def need(ok, text):
    if not ok:
        raise ValueError(text)


def interval(value):
    lo, hi = map(Q, value)
    need(lo <= hi, "Ordered interval")
    return lo, hi


def encode(value):
    return [str(x) for x in value]


def main():
    raw_bytes = SOURCE.read_bytes()
    need(sha256(raw_bytes).hexdigest() == PIN, "Frozen source pin")
    source = json.loads(raw_bytes)
    need((source["dimension"], source["productive_width"], source["calls"]) == (25, 224, 3),
         "One-pair schedule")
    rows = {}
    for family in ("rank30", "odd_rank16"):
        raw = source["results"][family]
        coded = source["results"][family + "_W48_I64"]
        a = interval(raw["unfused_terminal_moment"])
        b = interval(coded["with_terminal_comparator_moment"])
        before = interval(raw["moment"])
        units = {}
        for rank in (1, 2):
            n = raw["limits"][str(rank)]["children"]
            accepted = interval(raw["limits"][str(rank)]["accepted"])
            units[rank] = ((accepted[0] - before[1]) / n,
                           (accepted[1] - before[0]) / n)
            need(0 < units[rank][0] <= units[rank][1], "Positive unit interval")
        rows[family] = {}
        for count in (1, 2, 3):
            base = tuple(((3 - count) * a[i] + count * b[i]) / 3 for i in (0, 1))
            need(base[1] < 1, "Positive budget with the terminal comparator")
            profile = Counter({int(r): (3 - count) * n for r, n in raw["local_profile"].items()})
            profile.update({int(r): count * n for r, n in coded["local_profile"].items()})
            profile[1] += 224
            rank_mass = sum(r * n for r, n in profile.items())
            need(rank_mass == 5600 - 96 * count, "Complete rank count")
            result = {"changed_calls": count, "profile": profile, "rank_mass": rank_mass,
                      "moment": encode(base), "limits": {}}
            for rank, unit in units.items():
                n = ((1 - base[1]) / unit[1]).__floor__()
                yes = tuple(base[i] + n * unit[i] for i in (0, 1))
                no = tuple(base[i] + (n + 1) * unit[i] for i in (0, 1))
                need(n >= 0 and yes[1] < 1 < no[0], "Strict limit and next failure")
                result["limits"][str(rank)] = {
                    "children": n, "rank_mass": n * rank,
                    "accepted": encode(yes), "next": encode(no),
                }
            result["H1_saving_from_full_restoration"] = 96 * count - result["limits"]["1"]["children"]
            rows[family][str(count)] = result
        for rank in (1, 2):
            need(rows[family]["3"]["limits"][str(rank)]["children"]
                 == coded["all_other_debt_after_terminal"]["limits"][str(rank)]["children"],
                 "The three-call endpoint agrees with the frozen source")
    receipt = {
        "source_sha256": PIN,
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "selected_b_snapshot": source["selected_b_snapshot"],
        "method": "Rational interval arithmetic and linearity in the native histogram",
        "scope": "Conditional native histogram only. The changed-call placement and the 224 H1 terminal are not admitted.",
        "rows": rows,
    }
    (HERE / "MIXED-BUDGET.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    for family, entries in rows.items():
        print(family, [(k, r["limits"]["1"]["children"], r["limits"]["2"]["children"])
                       for k, r in entries.items()])


if __name__ == "__main__":
    main()
