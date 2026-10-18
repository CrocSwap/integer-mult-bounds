#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Recount the composed T740 witness and certify its complete moment."""

import argparse
import json
from fractions import Fraction

import materialize as m


def physical_bound(replicas=740, buffers=91, payload=2048):
    m.need(type(replicas) is int and replicas == 740, "T740 physical contract")
    m.need(type(buffers) is int and buffers == 91, "all 91 private buffers")
    physical = 896 * replicas + 408 + 8 + buffers + 2
    group = 2 ** 1296
    for j in range(1, 37):
        group *= 2 ** (2 * j) - 1
    stock_bits = (group * physical).bit_length()
    stock_l2_bits = (stock_bits + 1) // 2
    reserve = 128 + 37 + 18 + stock_l2_bits + 1 + 4
    m.need(physical <= 2 ** 20 and stock_l2_bits <= 1330, "retained full-stock bound")
    m.need(type(payload) is int and reserve <= payload, "paid prefix payload")
    return {"live": 896 * replicas, "physical": physical, "buffers": buffers,
                "group_order_times_physical_bit_length": stock_bits,
                "stock_l2_bits": stock_l2_bits, "reserve": reserve, "payload": payload,
                "namespaces": {"centers": [663040, 663048],
                            "tableau": [663048, 663456],
                            "zero_buffers": [663456, 663547],
                            "coefficients": [663547, 663549]}}


def owners(rows, order, dispatch, providers, claimed=m.PROFILE):
    path = m.MAIN / "allocation/vendor/independent_owners.py"
    module = m.load_path(path, "authenticated_owner740")
    normalized = {name: {**value, "actual_paid_profile": {
        int(k): v for k, v in value["actual_paid_profile"].items()}}
        for name, value in providers.items()}
    fill = {"columns": ["time", "helper", "owner_replica", "child", "port", "offset"],
            "rows": rows, "dispatch_overrides": []}
    result, _, _ = module.check(740, order, fill, dispatch, claimed,
        m.read(m.MAIN / "allocation/vendor/PLAN.json.gz"),
        m.read(m.MAIN / "allocation/vendor/TEMPLATE.json.gz"), normalized)
    m.need(result["roles"] == 2717280 and result["rank_mass"] == 48165120,
           "complete T740 roles and paid mass")
    # The retained diagnostic uses 72 buffers; charge the actual 91.
    m.need(result["physical"] == result["live"] + 490, "known retained diagnostic")
    result["physical"] = result["live"] + 509
    return result


def moment(profile):
    path = m.MAIN / "tools/root.py"
    root = m.load_path(path, "authenticated_root740")
    lower, upper = root.kappa_from_profile(profile, 740)
    old = m.read(m.PACKAGE / "vendor/PR3021-RESULT.json")
    previous = Fraction(old["kappa"])
    m.need(lower > previous, "strict improvement over PR3021 released kappa")
    baseline = m.read(m.PACKAGE / "vendor/pr3021-FINITE.json")
    previous_upper = Fraction(baseline["new_root"][1])
    m.need(lower > previous_upper, "strict complete moment improvement")
    cap = m.load("vendor/pr3024/cap_proof.py", "retained_cap_r1")
    providers = m.read(m.PACKAGE / "vendor/pr3015/allocation/PROVIDERS.json")
    local = {int(r): n for r, n in providers["gauge44"]["actual_paid_profile"].items()}
    m.need(local == {int(r): n for r, n in providers["extra"]["actual_paid_profile"].items()},
           "common actual R1 local profile")
    certificate = m.read(m.MAIN / "certificates/RELAX-CAP.json")
    cap.LOCAL = local
    certificate.update(local_per_call={str(r): n for r, n in local.items()},
                       cap_lower=str(lower), cap_upper=str(upper))
    recertified = cap.verify_cap(certificate, root)
    m.need(all(Fraction(profile.get(int(r), 0)) ==
        9 * 740 * local.get(int(r), 0) + 740 * Fraction(n)
        for r, n in recertified["idle_per_replica"].items()), "attained R1 cap idle counts")
    return {"root": [str(lower), str(upper)], "r1_cap": recertified,
                "exchange_sign": cap.prove_exchange_sign(),
                "previous_released_kappa": str(previous),
                "gain_over_previous_root": [str(lower - previous_upper),
                    str(upper - Fraction(baseline["new_root"][0]))]}


def run():
    rows, order, dispatch, providers = m.witness()
    result = owners(rows, order, dispatch, providers)
    stock = physical_bound()
    m.need(result["physical"] == stock["physical"] == 663549, "full physical stock")
    m.need(result["idle"] == {1: 173160, 3: 49617, 5: 17205, 48: 281903},
           "exact cap-attaining idle bill")
    return dict(status="PASS_T740_R1_FINITE", **result, stock=stock,
                moment=moment(m.PROFILE),
                scope="Finite composed allocation and moment; fresh release is separate.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    result = json.loads(json.dumps(run(), sort_keys=True))
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        m.need(result == m.read(m.PACKAGE / "evidence/FINITE.json"), "published finite receipt")
    print(result["status"], "roles=2717280", "physical=663549", flush=True)


if __name__ == "__main__":
    main()
