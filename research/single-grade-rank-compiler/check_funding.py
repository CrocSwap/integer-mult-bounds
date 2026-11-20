"""Bind the five exact types, dimension witnesses, cover and ordinary prices."""

import gzip
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from itertools import product
from math import comb, isqrt
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from funding import _mode, certificate


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.name.endswith(".gz") else data)


def sources():
    for row in read(HERE / "ORIGINS.json"):
        path = ROOT / row["local"]
        raw = path.read_bytes()
        if path.name.endswith(".gz") and not row["source"].endswith(".gz"):
            raw = gzip.decompress(raw)
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need((blob, sha256(raw).hexdigest()) == (row["blob"], row["sha256"]), row["local"])


def ordinary(word, pending):
    uniform = word["uniform"] if pending else word["finite_admission"]["uniform_compiler"]
    covered = Q(word["covered"] if pending else word["covered_saving"])
    loss = Q(uniform["uniform_saving"]) - covered
    need(loss == Q(1, 10**10) and Q(64, 2**45) < loss / 4, "fund the bad cover rows")
    rho = Q(1, 250)
    levels = word["ordinary_bootstrap"]
    price = Q(levels[0]["previous"])
    cold_gap = (1 - rho) * covered - price
    need(min(cold_gap, rho - price, 1 - rho - price) > 0,
         "the elementary ordinary service must fund the first complete backend")
    for row in levels:
        need(Q(row["previous"]) == price, "older ordinary service")
        next_price = Q(row["claim"] if pending else row["admitted"])
        gap = (1 - rho) * covered + rho * price - next_price
        need(min(gap, rho - next_price, 1 - rho - next_price) > 0, "all wrapper costs")
        price = next_price
    need(price == Q(word["ordinary_admitted"]), "ordinary root price")
    return {"covered": str(covered), "ordinary": str(price), "cold_start_gap": str(cold_gap),
            "levels_from_elementary": 1 + len(levels)}


def applications():
    s = read(ROOT / "research/shared-wire-split-composition/FULL-RESULT.json")
    b = read(ROOT / "research/paired-query-only-bit/EFREE-RESULT.json")
    p = read(HERE / "retained/pending-application.json.gz")
    n = read(HERE / "retained/pending-bit.json.gz")
    h = read(ROOT / "research/higher-moment-strictification/RESULT.json")
    selected = s["gate"]
    pending = p["application"]["compiler"]
    cases = {
        "selected_complex": (s["invoice"]["T"], s["invoice"]["P"], selected["tested"],
                             Q(selected["tested"]) - Q(selected["compiler_gap"]), 153),
        "selected_BIT": (b["targets"], b["paid"], b["raw_tested"],
                         b["finite_admission"]["uniform_compiler"]["uniform_saving"], 134),
        "pending_complex": (p["application"]["invoice"]["targets"], p["application"]["invoice"]["paid"],
                            pending["tested"], Q(pending["tested"]) - Q(pending["compiler_gap"]),
                            p["caller_census"]["finite_binding"]["ambient"]),
        "pending_BIT": (n["targets"], n["paid"], n["tested_saving"], n["uniform"]["uniform_saving"], 134),
        "historical_p7": (h["invoice_oracle"]["targets"], h["invoice_oracle"]["paid"],
                          h["strictification"]["tested_saving"], h["uniform_rank"]["uniform_saving"], 121),
    }
    rows = {}
    for name, args in cases.items():
        raw_targets, raw_paid, _, _, ambient = args
        row = certificate(*args, cap="3/1000" if name == "historical_p7" else "1/250")
        b0, q0 = sum(raw_targets.values()), sum(raw_paid.values())
        need(row["batch_width_degree_upper"] <= 16 and row["all_recursive_visits_degree_per_root_owner"] <= 27,
             "unrolled row and visit bounds")
        need(ambient >= 64 and b0 + q0 + ambient*q0 + 2 < 2**27, "local syntax degree")
        if name.endswith("BIT"):
            row.update(ordinary(n, True) if name == "pending_BIT" else ordinary(b, False))
        else:
            need(Q(row["uniform_saving"]) > Q(pending["claim"] if name == "pending_complex" else
                                              selected["claim"] if name == "selected_complex" else "0.00268647"),
                 "outer strict service")
        rows[name] = row
    need(Q(rows["selected_BIT"]["ordinary"]) == Q(n["ordinary_bootstrap"][0]["previous"]),
         "join the two established ordinary series")
    return rows


def controls():
    def quarter(histogram, power):
        total = 0
        for rank, count in histogram.items():
            root = isqrt(isqrt(rank))
            need(root**4 == rank, "test requires an integer fourth root")
            total += count * root**power
        return total

    targets, paid = {1: 70, 256: 1}, {16: 18}
    need(all(quarter(targets, s) > quarter(paid, s) for s in (2, 4))
         and quarter(targets, 3)**2 < quarter(paid, 2) * quarter(paid, 4), "interior chord")
    paid = {1: 1, 256: 1}
    targets = {1: 2, 256: 1}
    need(quarter(paid, 2) * quarter(paid, 4) - quarter(targets, 3)**2 == 13,
         "favorable raw moments but adverse chord")
    width = comb(12, 6) * 25**6
    need(41**41 * 256**8 < 128**41 and 8 * 8**24 < width**2, "interior constructive type")
    cases = [({1: 1}, {1: 1}, "1/300", "1/400", 8),
             ({16: 2}, {8: 1}, "1/300", "1/250", 32),
             ({32: 1}, {8: 1}, "1/300", "1/400", 31)]
    for args in cases:
        try:
            certificate(*args)
        except ValueError:
            continue
        raise ValueError("invalid input admitted")

    # Independently enumerate integer type terms for 1,375 small three-grade cases.
    for a, b, c in product(range(1, 6), repeat=3):
        for v in range(1, 12):
            def mass(i, j):
                return comb(v, i) * comb(v - i, j) * a**i * b**j * c**(v-i-j)
            mode = _mode({1: a, 4: b, 16: c}, v)
            optimum = max(mass(i, j) for i in range(v + 1) for j in range(v - i + 1))
            need(mass(mode[1], mode[4]) == optimum, "incorrect integer type")


def main():
    sources()
    controls()
    result = applications()
    if sys.argv[1:] == ["--write"]:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    elif len(sys.argv) != 1:
        raise ValueError("use no argument or --write")
    need(result == read(HERE / "RESULT.json"), "recorded dimension or useful type changed")
    print("PASS_SINGLE_GRADE_FUNDING profiles=5 max_width_degree=16 max_visit_degree=27")


if __name__ == "__main__":
    main()
