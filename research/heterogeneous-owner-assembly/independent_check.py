#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Ali Romman with substantial OpenAI Codex assistance.
"""Check the shared-pool dual in integer form. Do not import verify.py."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
Q = Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run():
    catalogue = load(HERE / "CATALOGUE.json")
    pins = load(HERE / "DEPENDENCIES.json")
    require(hashlib.sha256((HERE / "CATALOGUE.json").read_bytes()).hexdigest() == pins["catalogue_sha256"],
            "frozen catalogue hash mismatch")
    for path, digest in {**catalogue["sources"], **pins["sha256"]}.items():
        require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                "source drift: " + path)
    sources = [ROOT / relative for relative in sorted(catalogue["sources"])]
    provider_records = {(record["source"], record["provider"]): record["interface"]
                        for record in catalogue["records"]}
    require(len(provider_records) == len(catalogue["records"]), "duplicate source record")
    interfaces = {row["id"]: row for row in catalogue["interfaces"]}
    require(len(interfaces) == len(catalogue["interfaces"]), "duplicate interface")
    actual = {}
    for path in sources:
        relative = path.relative_to(ROOT).as_posix()
        for name, provider in load(path)["providers"].items():
            key = (relative, name)
            require(key in provider_records, "missing source provider")
            row = interfaces[provider_records[key]]
            require(row["profile"] == provider["expected_profile"] and
                    row["inventory"] == provider["inventory"], "source cost mismatch")
            actual[key] = row
    require(set(actual) == set(provider_records), "extra source record")
    require({row["id"] for row in actual.values()} == set(interfaces), "unbound interface")
    baseline = actual["research/complex-t21-owners/data/SPEC.json", "gauge44"]
    claim = load(ROOT / pins["roles"]["selected_claim"])
    left = Q(claim["complex_lower"])
    right = left + Q(1, 10**24)
    engine_path = ROOT / pins["roles"]["atanh"]
    spec = importlib.util.spec_from_file_location("owner_independent_interval", engine_path)
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    values, derivatives = {}, {}
    for r in range(1, 49):
        a, b = engine.log_bounds(Q(73, r))
        values[r] = (r * engine.exp_bounds(left * a)[0],
                     r * engine.exp_bounds(right * b)[1])
        derivatives[r] = (r * a, r * b * engine.exp_bounds(b / 500)[1])

    def lower_bound(terms, table):
        return sum((coefficient * table[r][coefficient < 0]
                    for r, coefficient in terms.items() if coefficient), Q(0))

    # The recurrence uses exact filled width as its state.
    prices = {4: -1, 5: -20, 7: -8, 8: -2, 9: 4}
    best = [None] * 49
    best[0] = 0
    for used in range(49):
        if best[used] is None:
            continue
        for width, price in prices.items():
            if used + width <= 48:
                proposal = best[used] + price
                if best[used + width] is None or proposal > best[used + width]:
                    best[used + width] = proposal
    bin_rows = []
    for capacity, bonus in ((8, 2), (16, 4), (32, 8), (48, -13)):
        for used in range(capacity + 1):
            if best[used] is None:
                continue
            r, price = capacity - used, bonus + best[used]
            terms = Counter({r: 925}) if r else Counter()
            terms[1] -= 13 * r + 48 * price
            terms[48] -= 19 * r - price
            exact_zero = all(n == 0 for n in terms.values())
            require(sum(r * n for r, n in terms.items()) == 0, "bin value at zero differs")
            bound = lower_bound(terms, values)
            derivative = lower_bound(terms, derivatives)
            require(exact_zero or bound > 0, "integer bin dual fails")
            require(exact_zero or derivative > 0, "uniform integer bin derivative fails")
            bin_rows.append(dict(capacity=capacity, residual=r, lower_925=str(bound),
                                 uniform_derivative_lower_925=str(derivative), exact_zero=exact_zero))
    require(lower_bound({1: 48, 48: -1}, values) > 0, "signed-price multiplier is not positive")
    require(lower_bound({1: 48, 48: -1}, derivatives) > 0, "signed-price derivative is not positive")

    def features(row):
        mass = sum(int(w) * n for w, n in row["inventory"].items())
        weight = sum(prices[int(w)] * n for w, n in row["inventory"].items())
        profile_mass = sum(int(r) * n for r, n in row["profile"].items())
        require(profile_mass - mass == 1856, "local rank contract fails")
        return mass, weight

    base_mass, base_weight = features(baseline)
    penalties = {}
    for row in interfaces.values():
        mass, weight = features(row)
        dm, dp = mass - base_mass, weight - base_weight
        terms = Counter({int(r): 925 * n for r, n in row["profile"].items()})
        for r, n in baseline["profile"].items():
            terms[int(r)] -= 925 * n
        terms[1] += 48 * dp - 13 * dm
        terms[48] -= dp + 19 * dm
        require(sum(r * n for r, n in terms.items()) == 0, "provider value at zero differs")
        bound = lower_bound(terms, values)
        derivative = lower_bound(terms, derivatives)
        require(all(n == 0 for n in terms.values()) if row["id"] == baseline["id"] else bound > 0,
                "integer provider dual fails: " + row["id"])
        if row["id"] != baseline["id"]:
            require(bound > 925 * Q(27, 4000), "uniform provider penalty floor fails")
            require(derivative > 925 * Q(19, 10), "uniform provider derivative floor fails")
            if row["inventory"] != baseline["inventory"]:
                require(bound > 925 * Q(113, 200), "changed-inventory penalty floor fails")
                require(derivative > 925 * 336, "changed-inventory derivative floor fails")
        penalties[row["id"]] = dict(root_lower=str(bound / 925),
                                    uniform_derivative_lower=str(derivative / 925))

    # Count the reference directly, without the affine forms in verify.py.
    capacities = {8: 672, 16: 448, 32: 448, 48: 448}
    bonuses = {8: 2, 16: 4, 32: 8, 48: -13}
    idle_mass = sum(c * n for c, n in capacities.items()) - 9 * base_mass
    idle_weight = sum(bonuses[c] * n for c, n in capacities.items()) + 9 * base_weight
    rank_one = Q(13 * idle_mass + 48 * idle_weight, 925)
    rank_48 = Q(19 * idle_mass - idle_weight, 925)
    require((rank_one, rank_48) == (Q(6, 37), Q(11086, 37)), "reference coefficient mismatch")
    expected = Counter({int(r): 333 * n for r, n in baseline["profile"].items()})
    expected.update({1: 6, 48: 11086})
    require(expected == {int(r): n for r, n in claim["profile"].items()}, "reference profile mismatch")
    signs = {}
    for name, endpoint in (("left", left), ("right", right)):
        bounds = engine.moment(73, 33152, list(expected.items()), endpoint)
        require(bounds[1] < 1 if name == "left" else bounds[0] > 1, "reference root sign fails")
        signs[name] = list(map(str, bounds))
    return dict(status="PASS_INDEPENDENT_INTEGER_MIXTURE_DUAL", records=len(actual),
                interfaces=len(interfaces), interval=[str(left), str(right)],
                uniform_derivative_interval=["0", "1/500"],
                bin_cases=bin_rows, provider_penalty_lower=penalties,
                reference_idle={1: str(rank_one), 48: str(rank_48)}, root_signs=signs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "output exists; choose a new file")
    result = run()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], "records=" + str(result["records"]),
          "interfaces=" + str(result["interfaces"]))


if __name__ == "__main__":
    main()
